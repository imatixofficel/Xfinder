import base64, json, unittest
from src.xray_probe import outbound_from_uri, make_config

class XrayProbeTests(unittest.TestCase):
    def test_vless_ws_tls(self):
        u = 'vless://00000000-0000-0000-0000-000000000001@example.com:443?security=tls&sni=example.com&type=ws&path=%2Fws&host=example.com#test'
        o = outbound_from_uri(u)
        self.assertEqual(o['protocol'], 'vless')
        self.assertEqual(o['streamSettings']['network'], 'ws')
        self.assertEqual(o['streamSettings']['tlsSettings']['serverName'], 'example.com')

    def test_trojan_tls(self):
        u = 'trojan://password@example.com:443?sni=example.com#t'
        o = outbound_from_uri(u)
        self.assertEqual(o['protocol'], 'trojan')
        self.assertEqual(o['settings']['servers'][0]['password'], 'password')

    def test_vmess(self):
        obj = {'v': '2', 'ps': 't', 'add': 'example.com', 'port': '443', 'id': '00000000-0000-0000-0000-000000000001', 'aid': '0', 'scy': 'auto', 'net': 'ws', 'tls': 'tls', 'sni': 'example.com', 'host': 'example.com', 'path': '/ws'}
        body = base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip('=')
        o = outbound_from_uri('vmess://' + body)
        self.assertEqual(o['protocol'], 'vmess')
        self.assertEqual(o['streamSettings']['network'], 'ws')

    def test_shadowsocks(self):
        raw = base64.urlsafe_b64encode(b'chacha20-ietf-poly1305:pass@example.com:443').decode().rstrip('=')
        o = outbound_from_uri('ss://' + raw)
        self.assertEqual(o['protocol'], 'shadowsocks')
        self.assertEqual(o['settings']['servers'][0]['method'], 'chacha20-ietf-poly1305')

    def test_config_shape(self):
        c = make_config('trojan://password@example.com:443?sni=example.com', 20001)
        self.assertEqual(c['inbounds'][0]['port'], 20001)
        self.assertEqual(c['outbounds'][0]['protocol'], 'trojan')

if __name__ == '__main__':
    unittest.main()
