"""Offline end-to-end test of the whole pipeline using a fake xray + local servers.
Proves: bad config in a batch does not poison the batch, dead proxies are dropped,
the deadline is honoured, results are published, and the process cannot hang."""
import asyncio, base64, json, os, socket, stat, subprocess, sys, tempfile, textwrap, time, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def free_listener():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); s.listen(64)
    return s


class E2E(unittest.TestCase):
    def test_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            wrapper = td / "xray"
            wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {REPO}/tests/fake_xray.py \"$@\"\n")
            wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)
            listeners = [free_listener() for _ in range(12)]
            self.addCleanup(lambda: [l.close() for l in listeners])
            ports = [l.getsockname()[1] for l in listeners]
            cfgs = []
            for i, p in enumerate(ports[:8]):           # 8 good (tcp open + proxy works)
                cfgs.append(f"trojan://good{i}@127.0.0.1:{p}?security=none#g{i}")
            for i, p in enumerate(ports[8:11]):         # 3 tcp-open but proxy dead
                cfgs.append(f"trojan://dead{i}@127.0.0.1:{p}?security=none#d{i}")
            cfgs.append("hysteria2://pw@127.0.0.1:%d#hy" % ports[11])            # unsupported -> only itself dropped
            cfgs.append("vless://u@127.0.0.1:%d?type=xhttp#x" % ports[11])        # unsupported transport
            cfgs.append("trojan://nobody@127.0.0.1:1?security=none#closed")       # tcp closed
            (td / "root").mkdir()
            script = textwrap.dedent(f"""
                import sys; sys.path.insert(0, {str(REPO)!r})
                import src.main as m
                CFGS = {cfgs!r}
                async def fake_collect():
                    return [{{"config": c, "source": "t", "trust_score": 90}} for c in CFGS]
                async def fake_clean():
                    return []
                m.collect = fake_collect
                m.fetch_clean_async = fake_clean
                m.main()
            """)
            env = dict(os.environ, XFINDER_ROOT=str(td / "root"), XRAY_BIN=str(wrapper), XRAY_BATCH_SIZE="4",
                       XRAY_PARALLEL="2", XRAY_PROBE_TIMEOUT="3", PIPELINE_BUDGET="60", XRAY_PORT_BASE="31000",
                       XRAY_PROBE_URLS="http://probe.test/trace,http://probe.test/generate_204")
            t = time.time()
            r = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True, timeout=120)
            print(r.stdout, r.stderr)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertLess(time.time() - t, 60)
            data = json.loads((td / "root/data/configs.json").read_text())
            got = sorted(c["config"].split("@")[0].split("//")[1] for c in data["configs"])
            self.assertEqual(got, sorted(f"good{i}" for i in range(8)))
            self.assertTrue((td / "root/output/all.txt").read_text().count("good") == 8)

    def _run(self, td, wrapper_body, cfgs, clean, budget="25"):
        wrapper = td / "xray"
        wrapper.write_text(wrapper_body)
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)
        (td / "root").mkdir()
        script = textwrap.dedent(f"""
            import sys; sys.path.insert(0, {str(REPO)!r})
            import src.main as m
            async def fake_collect():
                return [{{"config": c, "source": "t", "trust_score": 90}} for c in {cfgs!r}]
            async def fake_clean():
                return {clean!r}
            m.collect = fake_collect
            m.fetch_clean_async = fake_clean
            m.main()
        """)
        env = dict(os.environ, XFINDER_ROOT=str(td / "root"), XRAY_BIN=str(wrapper), XRAY_BATCH_SIZE="4",
                   XRAY_PARALLEL="2", XRAY_PROBE_TIMEOUT="3", PIPELINE_BUDGET=budget, XRAY_PORT_BASE="33000",
                   XRAY_PROBE_URLS="http://probe.test/trace,http://probe.test/generate_204")
        t = time.time()
        r = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True, timeout=120)
        return r, time.time() - t

    def test_hung_xray_cannot_hang_job(self):
        # Xray that never answers (the failure mode seen in the CI log): must end fast, non-zero, no publish.
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            l = free_listener(); p = l.getsockname()[1]
            r, dt = self._run(td, "#!/bin/sh\nsleep 1000\n", [f"trojan://good1@127.0.0.1:{p}?security=none"], [], budget="12")
            l.close()
            self.assertLess(dt, 45, r.stdout + r.stderr)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse((td / "root/data/configs.json").exists())

    def test_remix_stage(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            ls = [free_listener() for _ in range(2)]
            p0, p1 = (x.getsockname()[1] for x in ls)
            body = f"#!/bin/sh\nexec {sys.executable} {REPO}/tests/fake_xray.py \"$@\"\n"
            clean = [{"ip": "127.0.0.1", "ping": 5.0, "ports": [p1]}]
            r, dt = self._run(td, body, [f"vless://good1@127.0.0.1:{p0}?security=none&type=tcp#a"], clean)
            for x in ls: x.close()
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            data = json.loads((td / "root/data/configs.json").read_text())
            self.assertEqual(data["stats"]["remixed"], 1)
            self.assertTrue(any(c["is_remixed"] and f":{p1}" in c["config"] for c in data["configs"]))

    def test_fails_loudly_without_xray(self):
        env = dict(os.environ, XFINDER_ROOT=tempfile.mkdtemp(), XRAY_BIN="/nonexistent/xray")
        r = subprocess.run([sys.executable, "-m", "src.main"], cwd=REPO, env=env, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Xray binary not found", r.stderr)


if __name__ == "__main__":
    unittest.main()
