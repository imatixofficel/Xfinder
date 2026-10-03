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
    def setUp(self):
        for f in DONATIONS_DIR.glob("*.json"): f.unlink()

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


class WireGuard(unittest.TestCase):
    PRIV = "yAnz5TF+lXXJte14tji3zlMNq+hd2rYUIgJBgB3fBmk="
    PUB = "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="

    def test_roundtrip_and_outbound(self):
        from src import wg_sources as w
        d = {"private_key": self.PRIV, "public_key": self.PUB, "psk": "", "host": "162.159.192.1", "port": 2408,
             "address": ["172.16.0.2", "fd01::2"], "mtu": 1280, "reserved": [1, 2, 3]}
        uri = w.to_uri(d, "n")
        p = w.parse_uri(uri)
        self.assertEqual((p["private_key"], p["public_key"], p["host"], p["port"], p["reserved"]), (self.PRIV, self.PUB, "162.159.192.1", 2408, [1, 2, 3]))
        o = w.outbound_from_uri(uri)["settings"]
        self.assertEqual(o["address"], ["172.16.0.2", "fd01::2"]); self.assertEqual(o["peers"][0]["endpoint"], "162.159.192.1:2408")
        self.assertIn("PrivateKey = " + self.PRIV, w.conf_from_uri(uri))

    def test_raw_unencoded_keys_and_conf_extract(self):
        from src import wg_sources as w
        from src.finder import extract
        raw = f"wireguard://{self.PRIV}@1.2.3.4:2408?address=172.16.0.2/32&publickey={self.PUB}&mtu=1280#x"
        self.assertEqual(w.parse_uri(raw)["public_key"], self.PUB)
        conf = f"[Interface]\nPrivateKey = {self.PRIV}\nAddress = 172.16.0.2/32\n\n[Peer]\nPublicKey = {self.PUB}\nEndpoint = 5.6.7.8:2408\n"
        got = extract(conf)
        self.assertEqual(len(got), 1); self.assertEqual(w.parse_uri(got[0])["host"], "5.6.7.8")
        self.assertEqual(len(extract(raw)), 1)

    def test_bad_keys_rejected(self):
        from src import wg_sources as w
        with self.assertRaises(ValueError):
            w.parse_uri("wireguard://abc@1.2.3.4:2408?address=1.1.1.1&publickey=zzz")


class DirectDonation(unittest.TestCase):
    def test_ingest_json(self):
        for f in DONATIONS_DIR.glob("*.json"): f.unlink()
        payload = json.dumps({"configs": ["vless://a@1.1.1.1:443#x", "javascript:alert(1)", "trojan://b@2.2.2.2:443"], "ad": "<b>hi</b>", "user": "ab12/../x"})
        ok, _ = donations.ingest_json(payload, 99)
        self.assertTrue(ok)
        d = donations.load_active()[0]
        self.assertEqual(len(d["configs"]), 2); self.assertNotIn("<", d["ad"]); self.assertEqual(d["user"], "web-ab12x")
        self.assertFalse(donations.ingest_json("not json", 1)[0])


class WarpDefaults(unittest.TestCase):
    def test_gfp_style_uri_gets_warp_defaults(self):
        from src import wg_sources as w
        priv = "oApA+WWuzVzPHXI7I82rGrJT2r5ZKoZ1GJbcTsDG6mc="
        d = w.parse_uri(f"wireguard://{priv}@162.159.192.1:2408")
        self.assertEqual((d["public_key"], d["address"]), (w.WARP_PUB, ["172.16.0.2"]))
        full = w.to_uri(d); self.assertEqual(w.parse_uri(full)["private_key"], priv)
        with self.assertRaises(ValueError):                       # endpoint غیر کلودفلر: بدون کلید peer معتبر نیست
            w.parse_uri(f"wireguard://{priv}@103.107.198.228:80")


class DonorName(unittest.TestCase):
    def setUp(self):
        for f in DONATIONS_DIR.glob("*.json"): f.unlink()

    def test_name_roundtrip_issue_and_api(self):
        body = "### Configs\n\nvless://a@1.1.1.1:443#x\n\n### Ad\n\nhi\n\n### Name\n\n@my_channel 🚀 <b>x</b>"
        self.assertEqual(donations.extract_name(body), "@my_channel 🚀 bx/b")
        self.assertNotIn("<", donations.extract_name(body)); self.assertIn("🚀", donations.extract_name(body))
        ok, _ = donations.ingest_json(json.dumps({"configs": ["vless://a@1.1.1.1:443"], "name": "@xf_chan # 🔥", "ad": ""}), 5)
        self.assertTrue(ok); self.assertEqual(donations.load_active()[0]["name"], "@xf_chan 🔥")


class WgRemixHelpers(unittest.TestCase):
    def test_warp_ip_and_conf(self):
        from src import wg_sources as w
        self.assertTrue(w.is_warp_ip("162.159.192.7")); self.assertTrue(w.is_warp_ip("188.114.97.3"))
        self.assertFalse(w.is_warp_ip("104.16.1.1")); self.assertFalse(w.is_warp_ip("example.com"))
        priv = "oApA+WWuzVzPHXI7I82rGrJT2r5ZKoZ1GJbcTsDG6mc="
        d = w.parse_uri(f"wireguard://{priv}@162.159.192.1:2408?reserved=239%2C203%2C185")
        nd = w.with_endpoint(d, "188.114.96.1", 2408)
        conf = w.conf_text(nd)
        self.assertIn("Endpoint = 188.114.96.1:2408", conf); self.assertIn("[Interface]", conf); self.assertIn("Reserved = 239,203,185", conf)
        self.assertEqual(w.parse_uri(w.to_uri(nd))["reserved"], [239, 203, 185])

    def test_argh94_style_uri(self):
        from src import wg_sources as w
        u = ("wireguard://qDyWaZpek1GxtGsvuWI3k4iJwBUfhj1jjCAbUCpoUVM%3D@162.159.195.16:4500?address=172.16.0.2%2F32&reserved=239%2C203%2C185"
             "&publickey=bmXOC%2BF1FxEMF9dyiK2H5%2F1SUtzH0JuVo51h2wPfgyo%3D&mtu=1280&keepalive=5&wnoise=random#%F0%9F%87%A8%F0%9F%87%A6181847")
        d = w.parse_uri(u)
        self.assertEqual((d["host"], d["port"], d["address"], d["reserved"]), ("162.159.195.16", 4500, ["172.16.0.2"], [239, 203, 185]))
