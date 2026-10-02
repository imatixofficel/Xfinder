"""Real Xray connectivity validation.

Runs Xray in small batches instead of starting a new Xray process for every
configuration. Each candidate gets its own local SOCKS5 inbound and outbound;
HTTPS is then fetched through that exact outbound. This keeps validation real
while preventing large public lists from timing out the GitHub runner.
"""
import asyncio, base64, json, os, socket, tempfile, time
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

PROBE_URLS = [
    "https://www.cloudflare.com/cdn-cgi/trace",
    "https://www.gstatic.com/generate_204",
]
DEFAULT_TIMEOUT = float(os.getenv("XRAY_PROBE_TIMEOUT", "5"))
CONCURRENCY = max(1, int(os.getenv("XRAY_CONCURRENCY", "32")))
BATCH_SIZE = max(1, int(os.getenv("XRAY_BATCH_SIZE", "32")))


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
        try:
            return h, int(p)
        except ValueError:
            return h, default
    return hostport, default


def _tls(q, fallback_host=""):
    sec = q.get("security", [""])[0].lower()
    if sec not in {"tls", "reality"}:
        return None
    server_name = q.get("sni", [""])[0] or q.get("host", [""])[0] or fallback_host
    d = {"serverName": server_name,
         "allowInsecure": _bool(q.get("allowInsecure", [q.get("allow_insecure", ["0"])[0]])[0])}
    fp = q.get("fp", [""])[0]
    if fp:
        d["fingerprint"] = fp
    alpn = q.get("alpn", [""])[0]
    if alpn:
        d["alpn"] = [x for x in alpn.split(",") if x]
    if sec == "reality":
        pk = q.get("pbk", [""])[0] or q.get("publicKey", [""])[0]
        sid = q.get("sid", [""])[0] or q.get("shortId", [""])[0]
        if not pk:
            raise ValueError("reality public key missing")
        return {"security": "reality", "realitySettings": {"show": False, "fingerprint": fp or "chrome", "serverName": server_name, "publicKey": pk, "shortId": sid}}
    return {"security": "tls", "tlsSettings": d}


def _stream_from_query(q, host):
    net = (q.get("type", q.get("network", ["tcp"]))[0] or "tcp").lower()
    s = {"network": net}
    if net == "ws":
        w = {"path": unquote(q.get("path", ["/"])[0] or "/")}
        h = q.get("host", [""])[0]
        if h:
            w["headers"] = {"Host": h}
        s["wsSettings"] = w
    elif net in {"grpc", "gun"}:
        s["network"] = "grpc"
        s["grpcSettings"] = {"serviceName": q.get("serviceName", [q.get("path", [""])[0]])[0],
                              "multiMode": q.get("mode", [""])[0] == "multi"}
    elif net in {"h2", "http"}:
        s["network"] = "http"
        h = q.get("host", [""])[0]
        s["httpSettings"] = {"path": unquote(q.get("path", ["/"])[0] or "/")}
        if h:
            s["httpSettings"]["host"] = [h]
    else:
        typ = q.get("headerType", q.get("type", ["none"]))[0]
        if typ == "http":
            s["tcpSettings"] = {"header": {"type": "http", "request": {"path": [q.get("path", ["/"])[0]], "headers": {"Host": [q.get("host", [host])[0]]}}}}
    tls = _tls(q, host)
    if tls:
        s["security"] = tls["security"]
        if tls["security"] == "tls":
            s["tlsSettings"] = tls["tlsSettings"]
        else:
            s["realitySettings"] = tls["realitySettings"]
    return s


def outbound_from_uri(uri):
    proto = uri.split("://", 1)[0].lower()
    if proto == "vmess":
        body = uri.split("://", 1)[1].split("#", 1)[0]
        o = json.loads(_b64decode(body).decode("utf-8", "replace"))
        host, port = str(o.get("add", "")), int(o.get("port", 443))
        if not host:
            raise ValueError("vmess address missing")
        user = {"id": o.get("id", ""), "alterId": int(o.get("aid", 0) or 0), "security": o.get("scy", "auto") or "auto"}
        v = {"vnext": [{"address": host, "port": port, "users": [user]}]}
        q = {k: [o.get(k, "")] for k in ("net", "tls", "sni", "host", "path", "fp", "alpn")}
        q["type"] = [o.get("net", "tcp")]
        o2 = {"protocol": "vmess", "settings": v, "streamSettings": _stream_from_query(q, host)}
        return o2
    if proto in {"vless", "trojan"}:
        u = urlparse(uri)
        host, port = u.hostname or "", u.port or 443
        if not host:
            raise ValueError("address missing")
        q = parse_qs(u.query)
        if proto == "vless":
            user = {"id": unquote(u.username or ""), "encryption": q.get("encryption", ["none"])[0]}
            flow = q.get("flow", [""])[0]
            if flow:
                user["flow"] = flow
            settings = {"vnext": [{"address": host, "port": port, "users": [user]}]}
        else:
            settings = {"servers": [{"address": host, "port": port, "password": unquote(u.username or "")}]}
        return {"protocol": proto, "settings": settings, "streamSettings": _stream_from_query(q, host)}
    if proto == "ss":
        rest = uri.split("://", 1)[1].split("#", 1)[0]
        if "?" in rest:
            rest, _ = rest.split("?", 1)
        if "@" not in rest:
            dec = _b64decode(rest).decode("utf-8", "replace")
            if "@" not in dec:
                raise ValueError("invalid shadowsocks URI")
            rest = dec
        userinfo, hp = rest.rsplit("@", 1)
        if ":" not in userinfo:
            raise ValueError("invalid shadowsocks credentials")
        method, password = userinfo.split(":", 1)
        host, port = _split_host_port(hp)
        return {"protocol": "shadowsocks", "settings": {"servers": [{"address": host, "port": port, "method": method, "password": password}]}}
    if proto == "hysteria2":
        u = urlparse(uri)
        host, port = u.hostname or "", u.port or 443
        q = parse_qs(u.query)
        s = {"address": host, "port": port, "password": unquote(u.username or "")}
        obfs = q.get("obfs", [""])[0]
        if obfs:
            s["obfs"] = {"type": obfs, "password": q.get("obfs-password", [""])[0]}
        s["tls"] = {"serverName": q.get("sni", [""])[0] or host, "allowInsecure": _bool(q.get("insecure", ["0"])[0])}
        return {"protocol": "hysteria2", "settings": {"servers": [s]}}
    raise ValueError(f"unsupported protocol: {proto}")


def make_config(uri, socks_port):
    return {"log": {"loglevel": "none"}, "inbounds": [{"listen": "127.0.0.1", "port": socks_port, "protocol": "socks", "settings": {"auth": "noauth", "udp": False}}], "outbounds": [outbound_from_uri(uri)]}


def _test_config(binary, cfg_path):
    import subprocess
    try:
        r = subprocess.run([binary, "run", "-test", "-config", str(cfg_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8)
        return r.returncode == 0
    except Exception:
        return False


async def _curl_probe(port):
    for target in PROBE_URLS:
        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            "curl", "-fsS", "--max-time", str(max(2, int(DEFAULT_TIMEOUT))),
            "--proxy", f"socks5h://127.0.0.1:{port}", "-o", "/dev/null",
            "-w", "%{http_code}", target,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=DEFAULT_TIMEOUT + 1.5)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            continue
        code = out.decode(errors="ignore").strip()[:3]
        if proc.returncode == 0 and code in {"200", "204", "301", "302", "403"}:
            return True, round((time.perf_counter() - start) * 1000, 1)
    return False, None


async def _wait_port(port, timeout=2.0):
    end = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < end:
        try:
            r, w = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", port), timeout=0.25)
            w.close()
            try:
                await w.wait_closed()
            except Exception:
                pass
            return True
        except Exception:
            await asyncio.sleep(0.05)
    return False


async def _probe_batch(items, binary, batch_index):
    base_port = 24000 + ((batch_index * BATCH_SIZE) % 8000)
    prepared = []
    for i, item in enumerate(items):
        try:
            out = outbound_from_uri(item.get("config", ""))
            prepared.append((i, item, out, base_port + i))
        except Exception as e:
            item.update({"xray_tested": True, "xray_alive": False, "xray_error": str(e)[:180]})
    if not prepared:
        return items

    cfg = {
        "log": {"loglevel": "none"},
        "inbounds": [],
        "outbounds": [],
        "routing": {"domainStrategy": "AsIs", "rules": []},
    }
    for i, item, out, port in prepared:
        tag = f"o{i}"
        in_tag = f"i{i}"
        cfg["inbounds"].append({"tag": in_tag, "listen": "127.0.0.1", "port": port, "protocol": "socks", "settings": {"auth": "noauth", "udp": False}})
        out["tag"] = tag
        cfg["outbounds"].append(out)
        cfg["routing"]["rules"].append({"type": "field", "inboundTag": [in_tag], "outboundTag": tag})

    with tempfile.TemporaryDirectory(prefix="xfinder-xray-batch-") as td:
        cfg_path = Path(td) / "config.json"
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        loop = asyncio.get_running_loop()
        ok = await loop.run_in_executor(None, _test_config, binary, cfg_path)
        if not ok:
            # Fall back to per-config syntax tests only for a malformed batch.
            for i, item, out, port in prepared:
                single = Path(td) / f"single-{i}.json"
                single.write_text(json.dumps(make_config(item.get("config", ""), port), ensure_ascii=False), encoding="utf-8")
                syntax = await loop.run_in_executor(None, _test_config, binary, single)
                item.update({"xray_tested": True, "xray_alive": False, "xray_error": "xray config rejected" if not syntax else "batch config rejected"})
            return items
        try:
            proc = await asyncio.create_subprocess_exec(binary, "run", "-c", str(cfg_path), stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
            ports = await asyncio.gather(*[_wait_port(port) for _, _, _, port in prepared])
            results = await asyncio.gather(*[_curl_probe(port) if ready else asyncio.sleep(0, result=(False, None)) for (_, _, _, port), ready in zip(prepared, ports)])
            for (i, item, _, port), (alive, latency) in zip(prepared, results):
                item.update({"xray_tested": True, "xray_alive": alive, "http_ping_ms": latency})
                if not alive:
                    item["xray_error"] = "proxy HTTPS probe failed"
            if proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), 1.5)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
        except Exception as e:
            for _, item, _, _ in prepared:
                item.update({"xray_tested": True, "xray_alive": False, "xray_error": str(e)[:180]})
    return items


async def validate_xray(items, binary="xray"):
    # De-duplicate exact URIs before expensive real validation.
    unique = []
    seen = set()
    for item in items:
        cfg = item.get("config", "")
        if not cfg or cfg in seen:
            continue
        seen.add(cfg)
        unique.append(dict(item))
    results = []
    for start in range(0, len(unique), BATCH_SIZE):
        batch = unique[start:start + BATCH_SIZE]
        results.extend(await _probe_batch(batch, binary, start // BATCH_SIZE))
        print(f"Xray validation: {min(start + BATCH_SIZE, len(unique))}/{len(unique)}")
    return results
