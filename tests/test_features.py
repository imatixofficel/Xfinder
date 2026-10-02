import base64, json, os, sys, tempfile, unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
os.environ["XFINDER_ROOT"] = tempfile.mkdtemp()

from src import donations, naming, publisher  # noqa: E402
from src.config import DONATIONS_DIR  # noqa: E402


class Naming(unittest.TestCase):
    def test_uri_and_vmess(self):
        r = naming.rename("vless://u@1.2.3.4:443?security=tls#old", "Xfinder • VLESS • 001")
        self.assertTrue(r.startswith("vless://u@1.2.3.4:443?security=tls#"))
        self.assertEqual(naming.original_name(r), "Xfinder • VLESS • 001")
        vm = "vmess://" + base64.b64encode(json.dumps({"add": "1.1.1.1", "port": "443", "id": "x", "ps": "old"}).encode()).decode()
        r = naming.rename(vm, "new")
        self.assertEqual(naming.original_name(r), "new")
        obj = json.loads(base64.b64decode(r.split("://")[1] + "==")); self.assertEqual(obj["add"], "1.1.1.1")


class Donations(unittest.TestCase):
    def test_parse_expire_cleanup(self):
        body = "### Configs\n\nvless://a@1.1.1.1:443#x\ntrojan://b@2.2.2.2:443\n\n### Ad\n\n<b>سلام</b> کانال من"
        cfgs, ad = donations.parse_issue(body)
        self.assertEqual(len(cfgs), 2); self.assertNotIn("<", ad)
        ok, _ = donations.ingest(body, 7, "alice"); self.assertTrue(ok)
        ok, _ = donations.ingest(body, 8, "alice"); self.assertFalse(ok)       # ضد اسپم
        self.assertEqual(len(donations.load_active()), 1)
        f = next(DONATIONS_DIR.glob("*.json"))
        d = json.loads(f.read_text()); d["expires_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        f.write_text(json.dumps(d))
        self.assertEqual(donations.load_active(), [])
        self.assertEqual(donations.cleanup(), 1); self.assertFalse(list(DONATIONS_DIR.glob("*.json")))


class Top20(unittest.TestCase):
    def test_top20_file(self):
        items = [{"config": f"trojan://p{i}@10.0.0.{i}:443?security=none", "server": f"10.0.0.{i}", "port": 443,
                  "http_ping_ms": 500 - i, "tcp_ping_ms": 50, "protocol": "trojan"} for i in range(1, 31)]
        d = publisher.publish(items, [], [], [], 30, [], 0)
        from src.config import OUTPUT_DIR
        lines = (OUTPUT_DIR / "top20.txt").read_text().split()
        self.assertEqual(len(lines), 20)
        self.assertIn("p30@", lines[0])                                       # کمترین پینگ اول
        self.assertEqual(base64.b64decode((OUTPUT_DIR / "top20-b64.txt").read_text()).decode().split(), lines)
        self.assertEqual(d["stats"]["top"], 20)


if __name__ == "__main__":
    unittest.main()
