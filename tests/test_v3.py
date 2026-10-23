"""Speed test, GeoIP labels, last_tested, top20-speed output."""
import json, os, stat, subprocess, sys, tempfile, textwrap, time, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "tests"))
os.environ.setdefault("XFINDER_ROOT", tempfile.mkdtemp())

from src import geo, naming, publisher  # noqa: E402
import mmdb_writer  # noqa: E402
from test_pipeline_e2e import free_listener  # noqa: E402


def mmdb(entries):
    return geo.MMDBReader(mmdb_writer.build(entries))


REC_DE = {"country": {"iso_code": "DE", "names": {"en": "Germany"}}}
REC_US = {"country": {"iso_code": "US", "names": {"en": "United States"}}}


class GeoTests(unittest.TestCase):
    def test_reader_lookup(self):
        db = mmdb({"1.2.3.0/24": REC_DE, "8.8.0.0/16": REC_US})
        self.assertEqual(geo.country_from_record(db.get("1.2.3.200")), ("DE", "Germany"))
        self.assertEqual(geo.country_from_record(db.get("8.8.4.4")), ("US", "United States"))
        self.assertEqual(geo.country_from_record(db.get("9.9.9.9")), (None, None))

    def test_flag(self):
        self.assertEqual(geo.flag("de"), "🇩🇪")
        self.assertEqual(geo.flag(""), "")
        self.assertEqual(geo.flag("ZZZ"), "")

    def test_annotate_ip_and_hostname(self):
        db = mmdb({"1.2.3.0/24": REC_DE, "8.8.0.0/16": REC_US})
        items = [{"server": "1.2.3.4"}, {"server": "cdn.example.com"}, {"server": "nowhere.invalid"}, {"server": "9.9.9.9"}]
        n = geo.annotate(items, db=db, resolver=lambda h: {"cdn.example.com": "8.8.8.8"}.get(h))
        self.assertEqual(n, 2)
        self.assertEqual((items[0]["country_code"], items[0]["country"], items[0]["country_flag"]), ("DE", "Germany", "🇩🇪"))
        self.assertEqual(items[1]["country_code"], "US")
        self.assertNotIn("country_code", items[2]); self.assertNotIn("country_code", items[3])

    def test_no_database_is_harmless(self):
        items = [{"server": "1.2.3.4"}]
        old = geo.load_db
        geo.load_db = lambda: None
        try:
            self.assertEqual(geo.annotate(items), 0)
        finally:
            geo.load_db = old
        self.assertNotIn("country_code", items[0])


class NamingV3(unittest.TestCase):
    def test_flag_ping_speed_in_name(self):
        n = naming.tagged_name("Germany 01", "vless", seed="a", flag="🇩🇪", ping=120.4, speed=2457.6)
        self.assertTrue(n.startswith("🇩🇪 Germany 01 | Xfinder "))
        self.assertTrue(n.endswith("| 120ms | 2.4MB/s"))
        self.assertTrue(naming.tagged_name("", "ss", flag="🇩🇪", ping=50).startswith("🇩🇪 Xfinder "))
        self.assertTrue(naming.tagged_name("", "ss", ping=50).endswith("| SS | 50ms"))

    def test_no_double_flag_and_speed_format(self):
        self.assertTrue(naming.tagged_name("🇫🇷 Paris", "ss", flag="🇩🇪").startswith("🇫🇷 Paris |"))
        self.assertEqual(naming.fmt_speed(850), "850KB/s")
        self.assertEqual(naming.fmt_speed(1024), "1.0MB/s")
        self.assertEqual(naming.fmt_speed(None), "")


class PublishV3(unittest.TestCase):
    def test_top20_speed_sorted_and_fields(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            publisher.DATA_DIR, publisher.OUTPUT_DIR = td / "data", td / "out"
            items = []
            for i in range(30):
                items.append({"config": f"trojan://p{i}@10.0.0.{i}:443#n{i}", "server": f"10.0.0.{i}", "port": 443,
                              "protocol": "trojan", "alive": True, "http_ping_ms": 100 + i, "tcp_ping_ms": 50,
                              "download_speed": float(100 + i * 10) if i < 25 else None,
                              "country_code": "DE", "country": "Germany", "country_flag": "🇩🇪"})
            before = int(time.time())
            d = publisher.publish(items, [], [], [], 30, [], 0)
            lines = (td / "out/top20-speed.txt").read_text().split()
            self.assertEqual(len(lines), 20)
            speeds = [int(l.split("@")[0].split("//")[1][1:]) for l in lines]
            self.assertEqual(speeds, sorted(speeds, reverse=True))            # سریع‌ترین اول
            self.assertEqual(speeds[0], 24)
            allt = (td / "out/all.txt").read_text().split()
            self.assertEqual(allt[0].split("@")[0].split("//")[1], "p0")        # all.txt همچنان بر اساس تأخیر HTTP
            c0 = d["configs"][0]
            self.assertGreaterEqual(c0["last_tested"], before)
            self.assertEqual(c0["country_code"], "DE")
            self.assertIn("🇩🇪", c0["name"])
            self.assertTrue(any(c.get("speed_rank") == 1 for c in d["configs"]))
            self.assertTrue((td / "out/top20-speed-b64.txt").exists())

    def test_top20_speed_file_exists_even_without_speed(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            publisher.DATA_DIR, publisher.OUTPUT_DIR = td / "data", td / "out"
            publisher.publish([{"config": "trojan://a@1.1.1.1:443", "server": "1.1.1.1", "port": 443, "protocol": "trojan",
                                "http_ping_ms": 10}], [], [], [], 1, [], 0)
            self.assertEqual((td / "out/top20-speed.txt").read_text(), "")


class Fidelity(unittest.TestCase):
    """کانفیگ باید همان کانفیگ منبع باشد؛ فقط نام (remark) عوض می‌شود."""
    VMESS = '{"v":"2","ps":"old \\"x\\"","add":"1.2.3.4","port":"443","id":"abc","aid":0,"net":"ws","path":"/p?a=1&b=2","tls":"tls","sni":"s.example.com"}'
    URIS = [
        "vless://11111111-2222-3333-4444-555555555555@host.example.com:443?encryption=none&security=reality&sni=a.com&fp=chrome&pbk=AbC_-123&sid=ab&type=tcp&flow=xtls-rprx-vision#orig",
        "trojan://pa%24%24@1.2.3.4:8443?security=tls&sni=x.com&type=ws&path=%2Fa%3Fb%3D1&host=x.com#t",
        "ss://YWVzLTEyOC1nY206cGFzcw==@5.6.7.8:8388#s",
        "ss://YWVzLTEyOC1nY206cGFzcw@5.6.7.8:8388/?plugin=v2ray-plugin%3Btls#s2",
        "hysteria2://pw@9.9.9.9:443?sni=h.com&insecure=1&obfs=salamander#h",
        "wireguard://PRIV%2Bkey%3D@1.1.1.1:2408?address=172.16.0.2%2F32&publickey=PUB&mtu=1280&reserved=1,2,3#w",
        "vless://u@h.com:443?type=tcp",                       # بدون نام
    ]

    def test_only_remark_changes(self):
        for u in self.URIS:
            r = naming.rename(u, "🇩🇪 New | Xfinder ⚡ | 10ms")
            self.assertEqual(r.split("#", 1)[0], u.split("#", 1)[0], u)
            self.assertEqual(naming.original_name(r), "🇩🇪 New | Xfinder ⚡ | 10ms")

    def test_vmess_only_ps_changes(self):
        import base64
        u = "vmess://" + base64.b64encode(self.VMESS.encode()).decode()
        r = naming.rename(u, "🇩🇪 N | Xfinder")
        a = json.loads(self.VMESS)
        b = json.loads(naming._b64d(r.split("://", 1)[1]).decode())
        self.assertEqual({k: v for k, v in a.items() if k != "ps"}, {k: v for k, v in b.items() if k != "ps"})
        self.assertEqual(b["ps"], "🇩🇪 N | Xfinder")
        self.assertEqual(list(a), list(b))                                       # ترتیب کلیدها هم همان
        self.assertEqual(naming._b64d(r.split("://", 1)[1]).decode().replace("🇩🇪 N | Xfinder", "").count('"ps":""'), 1)

    def test_publish_keeps_connection_part(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            publisher.DATA_DIR, publisher.OUTPUT_DIR = td / "data", td / "out"
            items = [{"config": u, "server": "h", "port": i, "protocol": u.split("://")[0], "http_ping_ms": 10 + i,
                      "alive": True, "country_code": "DE"} for i, u in enumerate(self.URIS)]
            publisher.publish(items, [], [], [], 1, [], 0)
            out = json.loads((td / "data/configs.json").read_text())["configs"]
            self.assertEqual(len(out), len(self.URIS))
            for c in out:
                src = next(u for u in self.URIS if u.split("#", 1)[0] == c["config"].split("#", 1)[0])
                self.assertEqual(c["config"].split("#", 1)[0], src.split("#", 1)[0])


class E2ESpeed(unittest.TestCase):
    def test_pipeline_measures_speed_geo_and_last_tested(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            wrapper = td / "xray"
            wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {REPO}/tests/fake_xray.py \"$@\"\n")
            wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)
            ls = [free_listener() for _ in range(5)]
            self.addCleanup(lambda: [l.close() for l in ls])
            cfgs = [f"trojan://good{i}@127.0.0.1:{l.getsockname()[1]}?security=none#g{i}" for i, l in enumerate(ls[:4])]
            cfgs.append(f"trojan://dead@127.0.0.1:{ls[4].getsockname()[1]}?security=none#dead")
            (td / "root").mkdir()
            dbfile = td / "geo.mmdb"
            dbfile.write_bytes(mmdb_writer.build({"127.0.0.0/8": REC_DE}))
            script = textwrap.dedent(f"""
                import sys; sys.path.insert(0, {str(REPO)!r})
                import src.main as m
                async def fake_collect():
                    return [{{"config": c, "source": "t", "trust_score": 90}} for c in {cfgs!r}]
                m.collect = fake_collect
                m.main()
            """)
            env = dict(os.environ, XFINDER_ROOT=str(td / "root"), XRAY_BIN=str(wrapper), XRAY_BATCH_SIZE="4",
                       XRAY_PARALLEL="2", XRAY_PROBE_TIMEOUT="3", PIPELINE_BUDGET="60", XRAY_PORT_BASE="34000",
                       XRAY_PROBE_URLS="http://probe.test/trace,http://probe.test/generate_204",
                       XRAY_SPEED_URL="http://probe.test/speed", XRAY_SPEED_BATCH="2", GEO_DB_PATH=str(dbfile))
            t = time.time()
            r = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            data = json.loads((td / "root/data/configs.json").read_text())
            cs = data["configs"]
            self.assertEqual(len(cs), 4)
            self.assertEqual(sorted(c["config"].split("#")[0] for c in cs), sorted(u.split("#")[0] for u in cfgs[:4]))
            self.assertEqual(sorted(l.split("#")[0] for l in (td / "root/output/all.txt").read_text().split()),
                             sorted(u.split("#")[0] for u in cfgs[:4]))
            for c in cs:
                self.assertGreater(c["download_speed"], 0)
                self.assertEqual(c["country_code"], "DE")
                self.assertTrue(c["name"].startswith("🇩🇪 g"), c["name"])
                self.assertRegex(c["name"], r"\| \d+ms \| [\d.]+(MB|KB)/s$")
                self.assertGreaterEqual(c["last_tested"], int(t) - 1)
            self.assertEqual(len((td / "root/output/top20-speed.txt").read_text().split()), 4)
            self.assertEqual(data["stats"]["speed_tested"], 4)


if __name__ == "__main__":
    unittest.main()
