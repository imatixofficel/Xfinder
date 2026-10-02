"""Real Xray connectivity validation.

Candidates are tested in small batches: one Xray process per batch, one local
SOCKS5 inbound + one outbound per candidate, routed 1:1. HTTPS is then fetched
through that exact outbound with curl. Several batches run in parallel and the
whole stage honours a hard deadline, so a huge public list can never hang CI.

Robustness rules:
  * a config Xray rejects only removes ITSELF (never the whole batch);
  * unsupported protocols/transports are rejected up-front with a clear reason;
  * a missing/broken Xray binary is a loud error, not "everything is dead".
"""
import asyncio, base64, json, os, shutil, tempfile, time
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

PROBE_URLS = [u.strip() for u in os.getenv(
    "XRAY_PROBE_URLS",
    "https://www.cloudflare.com/cdn-cgi/trace,https://www.gstatic.com/generate_204").split(",") if u.strip()]
DEFAULT_TIMEOUT = float(os.getenv("XRAY_PROBE_TIMEOUT", "5"))
BATCH_SIZE = max(1, int(os.getenv("XRAY_BATCH_SIZE", "32")))
PARALLEL = max(1, int(os.getenv("XRAY_PARALLEL", "4")))
PORT_BASE = int(os.getenv("XRAY_PORT_BASE", "20000"))
SUPPORTED_NETWORKS = {"tcp", "ws", "grpc", "http"}
OK_CODES = {"200", "204"}


def _b64decode(s):
    s = s.strip().replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * ((4 - len(s) % 4) % 4))


def _bool(v):
    return str(v).lower() in {"1", "true", "yes", "on"}


def _first(q, *keys, default=""):
    for k in keys:
        v = q.get(k)
        if v and v[0]:
            return v[0]
    return default


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
    sec = _first(q, "security").lower()
    if sec not in {"tls", "reality"}:
        return None
    server_name = _first(q, "sni", "host") or fallback_host
    fp = _first(q, "fp")
    if sec == "reality":
        pk = _first(q, "pbk", "publicKey")
        if not pk:
            raise ValueError("reality public key missing")
        return {"security": "reality", "realitySettings": {
            "show": False, "fingerprint": fp or "chrome", "serverName": server_name,
            "publicKey": pk, "shortId": _first(q, "sid", "shortId"), "spiderX": unquote(_first(q, "spx"))}}
    d = {"serverName": server_name}
    # Only emit allowInsecure when really requested: newer Xray versions deprecate it.
    if _bool(_first(q, "allowInsecure", "allow_insecure", "insecure", default="0")):
        d["allowInsecure"] = True
    if fp:
        d["fingerprint"] = fp
    alpn = _first(q, "alpn")
    if alpn:
        d["alpn"] = [x for x in unquote(alpn).split(",") if x]
    return {"security": "tls", "tlsSettings": d}


def _stream_from_query(q, host):
    net = (_first(q, "type", "network", default="tcp") or "tcp").lower()
    if net == "raw":
        net = "tcp"
    if net == "gun":
        net = "grpc"
    if net == "h2":
        net = "http"
    if net not in SUPPORTED_NETWORKS:
        raise ValueError(f"unsupported transport: {net}")
    s = {"network": net}
    if net == "ws":
        w = {"path": unquote(_first(q, "path", default="/") or "/")}
        h = _first(q, "host")
        if h:
            w["headers"] = {"Host": h}
        s["wsSettings"] = w
    elif net == "grpc":
        s["grpcSettings"] = {"serviceName": unquote(_first(q, "serviceName", "path")),
                             "multiMode": _first(q, "mode") == "multi"}
    elif net == "http":
        h = _first(q, "host")
        s["httpSettings"] = {"path": unquote(_first(q, "path", default="/") or "/")}
        if h:
            s["httpSettings"]["host"] = [x for x in h.split(",") if x]
    else:
        if _first(q, "headerType").lower() == "http":
            s["tcpSettings"] = {"header": {"type": "http", "request": {
                "path": [unquote(_first(q, "path", default="/"))],
                "headers": {"Host": [_first(q, "host", default=host)]}}}}
    tls = _tls(q, host)
    if tls:
        s["security"] = tls["security"]
        s["tlsSettings" if tls["security"] == "tls" else "realitySettings"] = tls[tls["security"] + "Settings"]
    return s


def outbound_from_uri(uri):
    proto = uri.split("://", 1)[0].lower()
    if proto == "vmess":
        body = uri.split("://", 1)[1].split("#", 1)[0]
        o = json.loads(_b64decode(body).decode("utf-8", "replace"))
        host, port = str(o.get("add", "")), int(o.get("port", 443))
        if not host or not o.get("id"):
            raise ValueError("vmess address/id missing")
        user = {"id": o["id"], "alterId": int(o.get("aid", 0) or 0), "security": o.get("scy", "auto") or "auto"}
        net = (o.get("net") or "tcp").lower()
        q = {
            "type": [net],
            "security": [(o.get("tls") or "").lower()],   # <- vmess keeps TLS flag in "tls"
            "sni": [o.get("sni", "")], "host": [o.get("host", "")], "path": [o.get("path", "")],
            "fp": [o.get("fp", "")], "alpn": [o.get("alpn", "")],
            "headerType": [o.get("type", "none") if net == "tcp" else "none"],
            "allowInsecure": [str(o.get("allowInsecure", "") or "0")],
        }
        return {"protocol": "vmess", "settings": {"vnext": [{"address": host, "port": port, "users": [user]}]},
                "streamSettings": _stream_from_query(q, host)}
    if proto in {"vless", "trojan"}:
        u = urlparse(uri)
        host, port = u.hostname or "", u.port or 443
        if not host:
            raise ValueError("address missing")
        if not u.username:
            raise ValueError("credential missing")
        q = parse_qs(u.query)
        if proto == "vless":
            user = {"id": unquote(u.username), "encryption": _first(q, "encryption", default="none")}
            flow = _first(q, "flow")
            if flow:
                user["flow"] = flow
            settings = {"vnext": [{"address": host, "port": port, "users": [user]}]}
        else:
            settings = {"servers": [{"address": host, "port": port, "password": unquote(u.username)}]}
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
            try:
                userinfo = _b64decode(userinfo).decode("utf-8", "replace")
            except Exception:
                pass
        if ":" not in userinfo:
            raise ValueError("invalid shadowsocks credentials")
        method, password = userinfo.split(":", 1)
        host, port = _split_host_port(hp)
        return {"protocol": "shadowsocks", "settings": {"servers": [
            {"address": host, "port": port, "method": method, "password": unquote(password)}]}}
    raise ValueError(f"unsupported protocol: {proto}")


def make_config(uri, socks_port):
    return {"log": {"loglevel": "none"},
            "inbounds": [{"listen": "127.0.0.1", "port": socks_port, "protocol": "socks",
                          "settings": {"auth": "noauth", "udp": False}}],
            "outbounds": [outbound_from_uri(uri)]}


def _batch_config(entries, base_port):
    """entries: list of (item, outbound). Inbound i -> outbound i."""
    cfg = {"log": {"loglevel": "warning"}, "inbounds": [], "outbounds": [],
           "routing": {"domainStrategy": "AsIs", "rules": []}}
    for i, (_, out) in enumerate(entries):
        out = dict(out)
        out["tag"] = f"o{i}"
        cfg["inbounds"].append({"tag": f"i{i}", "listen": "127.0.0.1", "port": base_port + i,
                                "protocol": "socks", "settings": {"auth": "noauth", "udp": False}})
        cfg["outbounds"].append(out)
        cfg["routing"]["rules"].append({"type": "field", "inboundTag": [f"i{i}"], "outboundTag": f"o{i}"})
    return cfg


async def _run_quiet(binary, *args, timeout=10):
    proc = await asyncio.create_subprocess_exec(
        binary, *args, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
    try:
        return await asyncio.wait_for(proc.wait(), timeout=timeout) == 0
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await proc.wait()
        return False


async def _test_config(binary, cfg_path):
    return await _run_quiet(binary, "run", "-test", "-config", str(cfg_path))


async def _curl_probe(port):
    for target in PROBE_URLS:
        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            "curl", "-sS", "--max-time", str(max(2, int(DEFAULT_TIMEOUT))),
            "--proxy", f"socks5h://127.0.0.1:{port}", "-o", "/dev/null", "-w", "%{http_code}", target,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=DEFAULT_TIMEOUT + 1.5)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            await proc.communicate()
            continue
        if proc.returncode == 0 and out.decode(errors="ignore").strip()[:3] in OK_CODES:
            return True, round((time.perf_counter() - start) * 1000, 1)
    return False, None


async def _wait_ports(ports, proc, timeout=8.0):
    """Wait until every port accepts connections (or xray died / timeout)."""
    ready = {}
    end = time.monotonic() + timeout

    async def one(port):
        while time.monotonic() < end and proc.returncode is None:
            try:
                r, w = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", port), 0.3)
                w.close()
                try:
                    await w.wait_closed()
                except Exception:
                    pass
                ready[port] = True
                return
            except Exception:
                await asyncio.sleep(0.05)
        ready[port] = False

    await asyncio.gather(*(one(p) for p in ports))
    return ready


def _fail(item, why):
    item.update({"xray_tested": True, "xray_alive": False, "xray_error": why[:180], "http_ping_ms": None})


async def _probe_batch(items, binary, slot):
    base_port = PORT_BASE + slot * BATCH_SIZE
    entries = []
    for item in items:
        try:
            entries.append((item, outbound_from_uri(item.get("config", ""))))
        except Exception as e:
            _fail(item, str(e))
    if not entries:
        return items

    with tempfile.TemporaryDirectory(prefix="xfinder-xray-") as td:
        td = Path(td)
        full = td / "batch.json"
        full.write_text(json.dumps(_batch_config(entries, base_port)), encoding="utf-8")
        if not await _test_config(binary, full):
            # Isolate the culprit(s): test each config on its own, keep the good ones.
            sem = asyncio.Semaphore(8)

            async def single(idx, entry):
                async with sem:
                    p = td / f"single-{idx}.json"
                    p.write_text(json.dumps(_batch_config([entry], base_port)), encoding="utf-8")
                    return await _test_config(binary, p)

            verdicts = await asyncio.gather(*(single(i, e) for i, e in enumerate(entries)))
            kept = []
            for ok, entry in zip(verdicts, entries):
                if ok:
                    kept.append(entry)
                else:
                    _fail(entry[0], "xray rejected config")
            entries = kept
            if not entries:
                return items
            full.write_text(json.dumps(_batch_config(entries, base_port)), encoding="utf-8")

        err_path = td / "xray.err"
        proc = None
        try:
            with open(err_path, "wb") as errf:
                proc = await asyncio.create_subprocess_exec(
                    binary, "run", "-c", str(full), stdout=asyncio.subprocess.DEVNULL, stderr=errf)
                ports = [base_port + i for i in range(len(entries))]
                ready = await _wait_ports(ports, proc)
                results = await asyncio.gather(*[
                    _curl_probe(p) if ready.get(p) else asyncio.sleep(0, result=(False, None)) for p in ports])
            for (item, _), port, (alive, latency) in zip(entries, ports, results):
                item.update({"xray_tested": True, "xray_alive": alive, "http_ping_ms": latency})
                if not alive:
                    item["xray_error"] = "proxy HTTPS probe failed" if ready.get(port) else "xray inbound not ready"
            if not any(ready.values()):
                tail = err_path.read_text(errors="ignore")[-300:] if err_path.exists() else ""
                print(f"WARNING slot {slot}: xray inbounds never became ready. {tail}", flush=True)
        except Exception as e:
            for item, _ in entries:
                _fail(item, f"{type(e).__name__}: {e}")
        finally:
            if proc is not None and proc.returncode is None:
                try:
                    proc.terminate()
                    await asyncio.wait_for(proc.wait(), 2)
                except Exception:
                    try:
                        proc.kill()
                        await proc.wait()
                    except Exception:
                        pass
    return items


def check_binary(binary):
    path = shutil.which(binary) if os.sep not in binary else (binary if os.access(binary, os.X_OK) else None)
    if not path:
        raise RuntimeError(f"Xray binary not found or not executable: {binary!r} (set XRAY_BIN)")
    if not shutil.which("curl"):
        raise RuntimeError("curl is required for real proxy probing")
    return path


async def validate_xray(items, binary="xray", deadline=None):
    """Return only items that were really tested. `deadline` is time.monotonic()."""
    check_binary(binary)
    unique, seen = [], set()
    for item in items:
        cfg = item.get("config", "")
        if not cfg or cfg in seen:
            continue
        seen.add(cfg)
        unique.append(dict(item))
    batches = [unique[i:i + BATCH_SIZE] for i in range(0, len(unique), BATCH_SIZE)]
    queue = asyncio.Queue()
    for b in batches:
        queue.put_nowait(b)
    done = 0
    tested = []

    async def worker(slot):
        nonlocal done
        while True:
            try:
                batch = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            if deadline is not None and time.monotonic() >= deadline:
                return
            remaining = None if deadline is None else max(1.0, deadline - time.monotonic() + 2)
            try:
                await asyncio.wait_for(_probe_batch(batch, binary, slot), timeout=remaining)
            except asyncio.TimeoutError:
                continue
            tested.extend(x for x in batch if x.get("xray_tested"))
            done += len(batch)
            print(f"Xray validation: {done}/{len(unique)}", flush=True)

    await asyncio.gather(*(worker(s) for s in range(PARALLEL)))
    if done < len(unique):
        print(f"Xray stage stopped at time budget: tested {done}/{len(unique)}", flush=True)
    return tested
