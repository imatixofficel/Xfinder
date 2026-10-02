"""Real Xray connectivity probe for public proxy URIs.

The probe builds a temporary Xray config, starts a local SOCKS5 listener and
uses curl through that listener to perform a real HTTPS request. Nothing is
written to the repository except the final generated data when requested by
the caller.
"""
import asyncio, base64, json, os, re, tempfile, time
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

PROBE_URLS = [
    "https://www.cloudflare.com/cdn-cgi/trace",
    "https://www.gstatic.com/generate_204",
]
DEFAULT_TIMEOUT = float(os.getenv("XRAY_PROBE_TIMEOUT", "8"))
CONCURRENCY = int(os.getenv("XRAY_CONCURRENCY", "16"))


def _b64decode(s):
    s = s.strip().replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * ((4 - len(s) % 4) % 4))


def _bool(v):
    return str(v).lower() in {"1", "true", "yes", "on"}


def _split_host_port(hostport, default=443):
    if hostport.startswith("["):
        end = hostport.find("]")
        host = hostport[1:end]
        rest = hostport[end + 1:]
        return host, int(rest[1:]) if rest.startswith(":") else default
    if hostport.count(":") > 1:
        return hostport, default
    if ":" in hostport:
        h, p = hostport.rsplit(":", 1)
        try: return h, int(p)
        except ValueError: return h, default
    return hostport, default


def _tls(q, fallback_host=""):
    sec = q.get("security", [""])[0].lower()
    if sec not in {"tls", "reality"}:
        return None
    d = {"serverName": q.get("sni", [""])[0] or q.get("host", [""])[0] or fallback_host,
         "allowInsecure": _bool(q.get("allowInsecure", [q.get("allow_insecure", ["0"])[0]])[0])}
    fp = q.get("fp", [""])[0]
    if fp: d["fingerprint"] = fp
    alpn = q.get("alpn", [""])[0]
    if alpn: d["alpn"] = [x for x in alpn.split(",") if x]
    if sec == "reality":
        pk = q.get("pbk", [""])[0] or q.get("publicKey", [""])[0]
        sid = q.get("sid", [""])[0] or q.get("shortId", [""])[0]
        if not pk: raise ValueError("reality public key missing")
        d["realitySettings"] = {"show": False, "publicKey": pk, "shortId": sid}
        d.pop("serverName", None)
    return {"security": "reality" if sec == "reality" else "tls",
            "tlsSettings": d if sec == "tls" else None,
            "realitySettings": d.get("realitySettings") if sec == "reality" else None}


def _stream_from_query(q, host):
    net = (q.get("type", q.get("network", ["tcp"]))[0] or "tcp").lower()
    s = {"network": net}
    if net == "ws":
        w = {"path": unquote(q.get("path", ["/"])[0] or "/")}
        h = q.get("host", [""])[0]
        if h: w["headers"] = {"Host": h}
        s["wsSettings"] = w
    elif net in {"grpc", "gun"}:
        s["network"] = "grpc"
        s["grpcSettings"] = {"serviceName": q.get("serviceName", [q.get("path", [""])[0]])[0],
                              "multiMode": q.get("mode", [""])[0] == "multi"}
    elif net in {"h2", "http"}:
        s["network"] = "http"
        h = q.get("host", [""])[0]
        s["httpSettings"] = {"path": unquote(q.get("path", ["/"])[0] or "/")}
        if h: s["httpSettings"]["host"] = [h]
    else:
        typ = q.get("headerType", q.get("type", ["none"]))[0]
        if typ == "http":
            s["tcpSettings"] = {"header": {"type": "http", "request": {"path": [q.get("path", ["/"])[0]], "headers": {"Host": [q.get("host", [host])[0]]}}}}
    tls = _tls(q, host)
    if tls:
        s["security"] = tls["security"]
        if tls["security"] == "tls": s["tlsSettings"] = tls["tlsSettings"]
        else: s["realitySettings"] = tls["realitySettings"]
    return s


def outbound_from_uri(uri):
    proto = uri.split("://", 1)[0].lower()
    if proto == "vmess":
        body = uri.split("://", 1)[1].split("#", 1)[0]
        o = json.loads(_b64decode(body).decode("utf-8", "replace"))
        host, port = str(o.get("add", "")), int(o.get("port", 443))
        if not host: raise ValueError("vmess address missing")
        v = {"vnext": [{"address": host, "port": port, "users": [{"id": o.get("id", ""), "alterId": int(o.get("aid", 0) or 0), "security": o.get("scy", "auto") or "auto"}]}]}
        q = {"type": [o.get("net", "tcp")], "security": [o.get("tls", "")], "sni": [o.get("sni", "")], "host": [o.get("host", "")], "path": [o.get("path", "/")], "fp": [o.get("fp", "")], "alpn": [o.get("alpn", "")]}
        o2 = {"protocol": "vmess", "settings": v, "streamSettings": _stream_from_query(q, host)}
        return o2
    if proto in {"vless", "trojan"}:
        u = urlparse(uri)
        host, port = u.hostname or "", u.port or 443
        if not host: raise ValueError("address missing")
        q = parse_qs(u.query)
        if proto == "vless":
            user = {"id": unquote(u.username or ""), "encryption": q.get("encryption", ["none"])[0]}
            flow = q.get("flow", [""])[0]
            if flow: user["flow"] = flow
            settings = {"vnext": [{"address": host, "port": port, "users": [user]}]}
        else:
            settings = {"servers": [{"address": host, "port": port, "password": unquote(u.username or "")}]} 
        return {"protocol": proto, "settings": settings, "streamSettings": _stream_from_query(q, host)}
    if proto == "ss":
        rest = uri.split("://", 1)[1].split("#", 1)[0]
        qpart = ""
        if "?" in rest: rest, qpart = rest.split("?", 1)
        # SIP002: base64(method:password@host:port), or base64(method:password)@host:port
        if "@" not in rest:
            dec = _b64decode(rest).decode("utf-8", "replace")
            if "@" not in dec: raise ValueError("invalid shadowsocks URI")
            rest = dec
        userinfo, hp = rest.rsplit("@", 1)
        if ":" not in userinfo: raise ValueError("invalid shadowsocks credentials")
        method, password = userinfo.split(":", 1)
        host, port = _split_host_port(hp)
        return {"protocol": "shadowsocks", "settings": {"servers": [{"address": host, "port": port, "method": method, "password": password}]}}
    if proto == "hysteria2":
        u = urlparse(uri); host, port = u.hostname or "", u.port or 443; q = parse_qs(u.query)
        s = {"address": host, "port": port, "password": unquote(u.username or "")}
        obfs = q.get("obfs", [""])[0]
        if obfs:
            s["obfs"] = {"type": obfs, "password": q.get("obfs-password", [""])[0]}
        tls = {"serverName": q.get("sni", [""])[0] or host, "allowInsecure": _bool(q.get("insecure", ["0"])[0])}
        if q.get("alpn"): tls["alpn"] = q["alpn"][0].split(",")
        s["tls"] = tls
        return {"protocol": "hysteria2", "settings": {"servers": [s]}}
    if proto == "wireguard":
        u = urlparse(uri); host, port = u.hostname or "", u.port or 2408; q = parse_qs(u.query)
        pub = q.get("publickey", [""])[0]
        address = q.get("address", [""])[0]
        if not pub or not address: raise ValueError("wireguard parameters missing")
        return {"protocol": "wireguard", "settings": {"secretKey": unquote(u.username or ""), "address": [x.strip() for x in unquote(address).split(",") if x.strip()], "peers": [{"publicKey": pub, "endpoint": f"{host}:{port}", "keepAlive": 25}], "mtu": int(q.get("mtu", ["1280"])[0])}}
    raise ValueError(f"unsupported protocol: {proto}")


def make_config(uri, socks_port):
    outbound = outbound_from_uri(uri)
    return {"log": {"loglevel": "none"}, "inbounds": [{"listen": "127.0.0.1", "port": socks_port, "protocol": "socks", "settings": {"auth": "noauth", "udp": False}}], "outbounds": [outbound]}


def _xray_test(binary, cfg):
    p = subprocess_run([binary, "run", "-test", "-config", str(cfg)], timeout=5)
    return p[0] == 0


def subprocess_run(cmd, timeout):
    import subprocess
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception:
        return 124, b"", b""


async def probe_one(item, binary, sem, slot):
    async with sem:
        uri = item.get("config", "")
        host = item.get("server", "")
        with tempfile.TemporaryDirectory(prefix="xfinder-xray-") as td:
            cfg_path = Path(td) / "config.json"
            port = 20000 + (slot % 20000)
            try:
                cfg_path.write_text(json.dumps(make_config(uri, port), ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                item.update({"xray_tested": True, "xray_alive": False, "xray_error": str(e)[:180]})
                return item
            loop = asyncio.get_running_loop()
            ok = await loop.run_in_executor(None, _xray_test, binary, cfg_path)
            if not ok:
                item.update({"xray_tested": True, "xray_alive": False, "xray_error": "xray config rejected"})
                return item
            import subprocess
            try:
                proc = await asyncio.create_subprocess_exec(binary, "run", "-c", str(cfg_path), stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                await asyncio.sleep(0.65)
                alive = False; latency = None
                for target in PROBE_URLS:
                    start = time.perf_counter()
                    curl = await asyncio.create_subprocess_exec("curl", "-fsS", "--max-time", str(max(2, int(DEFAULT_TIMEOUT))), "--proxy", f"socks5h://127.0.0.1:{port}", "-o", "/dev/null", "-w", "%{http_code}", target, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
                    try:
                        out, _ = await asyncio.wait_for(curl.communicate(), timeout=DEFAULT_TIMEOUT + 2)
                    except asyncio.TimeoutError:
                        curl.kill(); await curl.communicate(); continue
                    if curl.returncode == 0 and out.decode(errors="ignore").strip()[:3] in {"200", "204", "301", "302", "403"}:
                        alive = True; latency = round((time.perf_counter() - start) * 1000, 1); break
                if proc.returncode is None:
                    proc.terminate()
                    try: await asyncio.wait_for(proc.wait(), 1.5)
                    except asyncio.TimeoutError: proc.kill(); await proc.wait()
                item.update({"xray_tested": True, "xray_alive": alive, "http_ping_ms": latency})
                if not alive: item["xray_error"] = "proxy HTTPS probe failed"
                return item
            except Exception as e:
                try:
                    if proc.returncode is None: proc.kill()
                except Exception: pass
                item.update({"xray_tested": True, "xray_alive": False, "xray_error": str(e)[:180]})
                return item


async def validate_xray(items, binary="xray"):
    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [probe_one(dict(x), binary, sem, i) for i, x in enumerate(items)]
    return await asyncio.gather(*tasks)
