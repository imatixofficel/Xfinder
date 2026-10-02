import base64, json, unittest
from src.xray_probe import outbound_from_uri, make_config, _batch_config


def vmess(**kw):
    obj = {'v': '2', 'ps': 't', 'add': 'example.com', 'port': '443', 'id': '00000000-0000-0000-0000-000000000001',
           'aid': '0', 'scy': 'auto', 'net': 'ws', 'tls': 'tls', 'sni': 'example.com', 'host': 'example.com', 'path': '/ws'}
    obj.update(kw)
    return 'vmess://' + base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip('=')


class XrayProbeTests(unittest.TestCase):
    def test_vless_ws_tls(self):
        u = 'vless://00000000-0000-0000-0000-000000000001@example.com:443?security=tls&sni=example.com&type=ws&path=%2Fws&host=example.com#test'
        o = outbound_from_uri(u)
        self.assertEqual(o['protocol'], 'vless')
        self.assertEqual(o['streamSettings']['network'], 'ws')
        self.assertEqual(o['streamSettings']['tlsSettings']['serverName'], 'example.com')
        self.assertNotIn('allowInsecure', o['streamSettings']['tlsSettings'])

    def test_vless_reality(self):
        u = 'vless://uuid@1.2.3.4:443?security=reality&pbk=KEY&sid=ab&sni=x.com&fp=chrome&flow=xtls-rprx-vision&type=tcp'
        o = outbound_from_uri(u)
        self.assertEqual(o['streamSettings']['security'], 'reality')
        self.assertEqual(o['streamSettings']['realitySettings']['publicKey'], 'KEY')
        self.assertEqual(o['settings']['vnext'][0]['users'][0]['flow'], 'xtls-rprx-vision')

    def test_reality_without_key_rejected(self):
        with self.assertRaises(ValueError):
            outbound_from_uri('vless://uuid@1.2.3.4:443?security=reality&sni=x.com')

    def test_trojan_tls(self):
        o = outbound_from_uri('trojan://password@example.com:443?security=tls&sni=example.com#t')
        self.assertEqual(o['protocol'], 'trojan')
        self.assertEqual(o['settings']['servers'][0]['password'], 'password')
        self.assertEqual(o['streamSettings']['security'], 'tls')

    def test_vmess_ws_tls_keeps_tls(self):
        # Regression: vmess "tls" field used to be ignored, so TLS vmess never connected.
        o = outbound_from_uri(vmess())
        self.assertEqual(o['protocol'], 'vmess')
        self.assertEqual(o['streamSettings']['network'], 'ws')
        self.assertEqual(o['streamSettings']['security'], 'tls')
        self.assertEqual(o['streamSettings']['tlsSettings']['serverName'], 'example.com')

    def test_vmess_plain_tcp(self):
        o = outbound_from_uri(vmess(net='tcp', tls=''))
        self.assertEqual(o['streamSettings']['network'], 'tcp')
        self.assertNotIn('security', o['streamSettings'])

    def test_vmess_grpc(self):
        o = outbound_from_uri(vmess(net='grpc', path='svc'))
        self.assertEqual(o['streamSettings']['grpcSettings']['serviceName'], 'svc')

    def test_shadowsocks_b64(self):
        raw = base64.urlsafe_b64encode(b'chacha20-ietf-poly1305:pass@example.com:443').decode().rstrip('=')
        o = outbound_from_uri('ss://' + raw)
        self.assertEqual(o['protocol'], 'shadowsocks')
        self.assertEqual(o['settings']['servers'][0]['method'], 'chacha20-ietf-poly1305')

    def test_shadowsocks_sip002(self):
        ui = base64.urlsafe_b64encode(b'aes-256-gcm:secret').decode().rstrip('=')
        o = outbound_from_uri(f'ss://{ui}@example.com:8388#n')
        self.assertEqual(o['settings']['servers'][0]['password'], 'secret')
        self.assertEqual(o['settings']['servers'][0]['port'], 8388)

    def test_unsupported_rejected_individually(self):
        for u in ('hysteria2://pw@example.com:443', 'vless://u@example.com:443?type=xhttp&security=tls',
                  'vless://u@example.com:443?type=kcp'):
            with self.assertRaises(ValueError):
                outbound_from_uri(u)

    def test_config_shape(self):
        c = make_config('trojan://password@example.com:443?sni=example.com', 20001)
        self.assertEqual(c['inbounds'][0]['port'], 20001)
        self.assertEqual(c['outbounds'][0]['protocol'], 'trojan')

    def test_batch_routing_is_one_to_one(self):
        e = [({}, outbound_from_uri('trojan://a@h1.com:443')), ({}, outbound_from_uri('trojan://b@h2.com:443'))]
        c = _batch_config(e, 21000)
        self.assertEqual([i['port'] for i in c['inbounds']], [21000, 21001])
        self.assertEqual([r['outboundTag'] for r in c['routing']['rules']], ['o0', 'o1'])


if __name__ == '__main__':
    unittest.main()


class RemixTests(unittest.TestCase):
    def test_remix_replaces_host_and_port_once(self):
        from src.remixer import remix_config
        out = remix_config('vless://u@old.example.com:443?security=tls&type=ws#tag', '1.2.3.4', 8443)
        self.assertIn('@1.2.3.4:8443?', out)
        self.assertNotIn(':443', out)
        self.assertIn('sni=old.example.com', out)
        self.assertTrue(out.endswith('#tag'))
        o = outbound_from_uri(out)
        self.assertEqual(o['settings']['vnext'][0]['port'], 8443)
        self.assertEqual(o['settings']['vnext'][0]['address'], '1.2.3.4')

    def test_remix_vmess(self):
        from src.remixer import remix_config
        out = remix_config(vmess(), '1.2.3.4', 2053)
        o = outbound_from_uri(out)
        self.assertEqual(o['settings']['vnext'][0]['address'], '1.2.3.4')
        self.assertEqual(o['settings']['vnext'][0]['port'], 2053)
