"""WireGuard از منابع عمومی: پارس wireguard:// و فایل‌های .conf، ساخت outbound واقعی برای Xray.
WireGuard روی UDP است؛ بنابراین تست TCP ندارد و مستقیم با Xray (+ درخواست HTTPS واقعی) تست می‌شود."""
import base64, ipaddress, re
from urllib.parse import quote, unquote, parse_qs


# Cloudflare WARP: کلید عمومی peer ثابت است و آدرس IPv4 تونل برای حساب‌های رایگان 172.16.0.2 است.
# بعضی منابع (مثل gfpcom/free-proxy-list) فقط «کلید خصوصی@endpoint» می‌دهند؛ برای endpointهای WARP کلودفلر
# مقدارهای پیش‌فرض را پر می‌کنیم. اگر درست نبود، تست واقعی Xray همان کانفیگ را حذف می‌کند.
WARP_PUB = "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="
WARP_V4 = "172.16.0.2"
_WARP_NETS = [ipaddress.ip_network(n) for n in ("162.159.192.0/22", "188.114.96.0/22", "2606:4700:d0::/48", "2606:4700:d1::/48")]


def _is_warp_endpoint(host):
    if host.lower() == "engage.cloudflareclient.com":
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(ip in n for n in _WARP_NETS if n.version == ip.version)


def is_warp_ip(host):
    """آیا IP داخل رنج endpointهای WARP کلودفلر (UDP) است؟ فقط این IPها برای WireGuard/WARP کار می‌کنند."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(ip in n for n in _WARP_NETS if n.version == ip.version)


def with_endpoint(d, host, port):
    nd = dict(d)
    nd["host"], nd["port"] = host, int(port)
    return nd


def _key_ok(k):
    try:
        k = (k or "").strip().replace("-", "+").replace("_", "/")
        return len(base64.b64decode(k + "=" * ((4 - len(k) % 4) % 4), validate=True)) == 32
    except Exception:
        return False


def _first(q, *names):
    for n in names:
        if q.get(n):
            return q[n][0]
    return ""


def _split_hp(hp):
    hp = hp.strip()
    if hp.startswith("["):
        e = hp.find("]")
        return hp[1:e], int(hp[e + 2:])
    host, port = hp.rsplit(":", 1)
    return host, int(port)


def _norm(d):
    if not (_key_ok(d["private_key"]) and _key_ok(d["public_key"])):
        raise ValueError("invalid wireguard key")
    if not d["host"] or not (0 < d["port"] < 65536):
        raise ValueError("invalid endpoint")
    if not d["address"]:
        raise ValueError("address missing")
    if d.get("psk") and not _key_ok(d["psk"]):
        d["psk"] = ""
    return d


def parse_uri(uri):
    body = uri.split("://", 1)[1]
    body, _, _frag = body.partition("#")
    auth, _, query = body.partition("?")
    if "@" not in auth:
        raise ValueError("credential missing")
    priv, hp = auth.rsplit("@", 1)
    host, port = _split_hp(hp)
    q = parse_qs(query.replace("+", "%2B"))      # '+' داخل کلید base64 باید حفظ شود
    addrs = [a.strip().split("/")[0] for a in re.split(r"[,\s]+", _first(q, "address", "ip", "ips")) if a.strip()]
    reserved = []
    try:
        reserved = [int(x) for x in re.split(r"[,\s]+", _first(q, "reserved")) if x != ""][:3]
        if len(reserved) != 3 or any(not 0 <= x < 256 for x in reserved):
            reserved = []
    except Exception:
        reserved = []
    try:
        mtu = int(_first(q, "mtu") or 1280)
    except ValueError:
        mtu = 1280
    d = {"private_key": unquote(priv).replace(" ", "+"), "public_key": _first(q, "publickey", "public_key", "peer_public_key", "pbk").replace(" ", "+"),
         "psk": _first(q, "presharedkey", "psk", "pre_shared_key").replace(" ", "+"), "host": host, "port": port,
         "address": addrs, "mtu": min(max(mtu, 576), 1500), "reserved": reserved}
    if _is_warp_endpoint(host):
        d["public_key"] = d["public_key"] or WARP_PUB
        d["address"] = d["address"] or [WARP_V4]
    return _norm(d)


def to_uri(d, name="Xfinder-WG"):
    q = f"address={quote(','.join(a + ('/128' if ':' in a else '/32') for a in d['address']), safe='')}&publickey={quote(d['public_key'], safe='')}&mtu={d['mtu']}"
    if d.get("psk"):
        q += "&presharedkey=" + quote(d["psk"], safe="")
    if d.get("reserved"):
        q += "&reserved=" + ",".join(map(str, d["reserved"]))
    host = f"[{d['host']}]" if ":" in d["host"] else d["host"]
    return f"wireguard://{quote(d['private_key'], safe='')}@{host}:{d['port']}?{q}#{quote(name, safe='')}"


def conf_text(d):
    host = f"[{d['host']}]" if ":" in d["host"] else d["host"]
    s = ("# Xfinder - https://imatixofficel.github.io/Xfinder/\n"
         + (f"# Reserved = {','.join(map(str, d['reserved']))}   (برای کلاینت‌هایی که Reserved پشتیبانی می‌کنند)\n" if d.get("reserved") else "")
         + f"[Interface]\nPrivateKey = {d['private_key']}\nAddress = "
         + ", ".join(a + ("/128" if ":" in a else "/32") for a in d["address"]) + f"\nDNS = 1.1.1.1, 1.0.0.1\nMTU = {d['mtu']}\n\n"
         f"[Peer]\nPublicKey = {d['public_key']}\n")
    if d.get("psk"):
        s += f"PresharedKey = {d['psk']}\n"
    return s + f"AllowedIPs = 0.0.0.0/0, ::/0\nEndpoint = {host}:{d['port']}\nPersistentKeepalive = 25\n"


def conf_from_uri(uri):
    return conf_text(parse_uri(uri))


def outbound_from_uri(uri):
    d = parse_uri(uri)
    host = f"[{d['host']}]" if ":" in d["host"] else d["host"]
    peer = {"publicKey": d["public_key"], "endpoint": f"{host}:{d['port']}", "allowedIPs": ["0.0.0.0/0", "::/0"]}
    if d.get("psk"):
        peer["preSharedKey"] = d["psk"]
    st = {"secretKey": d["private_key"], "address": d["address"], "peers": [peer], "mtu": d["mtu"], "noKernelTun": True}
    if d.get("reserved"):
        st["reserved"] = d["reserved"]
    return {"protocol": "wireguard", "settings": st}


def confs_to_uris(text):
    """فایل(های) .conf استاندارد → wireguard:// (فقط بلوک‌های کامل و معتبر)."""
    out = []
    for block in re.split(r"(?im)^\s*\[Interface\]\s*$", text)[1:]:
        iface, _, peer = block.partition("[Peer]")
        kv = lambda s: {m.group(1).lower(): m.group(2).strip() for m in re.finditer(r"(?m)^\s*([A-Za-z]+)\s*=\s*(.+?)\s*$", s)}
        i, p = kv(iface), kv(peer.split("[Interface]")[0])
        try:
            host, port = _split_hp(p.get("endpoint", ""))
            d = _norm({"private_key": i.get("privatekey", ""), "public_key": p.get("publickey", ""), "psk": p.get("presharedkey", ""),
                       "host": host, "port": port, "mtu": int(i.get("mtu", 1280) or 1280),
                       "address": [a.strip().split("/")[0] for a in i.get("address", "").split(",") if a.strip()], "reserved": []})
            out.append(to_uri(d, "WG"))
        except Exception:
            continue
    return out
