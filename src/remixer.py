"""Clean-IP source + lightweight endpoint scanner + config remixing."""
import asyncio, base64, json, re, socket
from urllib.request import Request, urlopen
from .config import CLEAN_IPS_URL, MAX_REMIX_PING, REMIX_PER_CONFIG, REMIX_BASE_LIMIT

SCAN_PORTS = (443, 8443, 2053, 2083, 2087, 2096, 80, 8080)
SCAN_TIMEOUT = 1.5
SCAN_CONCURRENCY = 300
MAX_SOURCE_IPS = 400


def _fetch_source():
    req = Request(CLEAN_IPS_URL, headers={"User-Agent": "Xfinder/2.2 (+GitHub Actions)"})
    raw = urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    data = json.loads(raw)
    if isinstance(data, dict):
        data = data.get("ips") or data.get("data") or data.get("results") or []
    out = []
    for x in data:
        if isinstance(x, str):
            ip = x.strip()
            ping = 0
        elif isinstance(x, dict):
            ip = str(x.get("ip") or x.get("address") or "").strip()
            ping = x.get("ping", x.get("ping_ms", 999))
        else:
            continue
        if not ip:
            continue
        try: ping = float(ping or 999)
        except Exception: ping = 999
        try: socket.inet_pton(socket.AF_INET, ip)
        except OSError:
            continue
        out.append({"ip": ip, "ping": ping})
    # preserve order while deduplicating
    seen, clean = set(), []
    for x in out:
        if x["ip"] not in seen:
            seen.add(x["ip"]); clean.append(x)
    return clean


async def _probe(ip, port, sem):
    async with sem:
        loop = asyncio.get_running_loop()
        start = loop.time()
        try:
            fut = asyncio.open_connection(ip, port, family=socket.AF_INET)
            r, w = await asyncio.wait_for(fut, timeout=SCAN_TIMEOUT)
            ms = round((loop.time() - start) * 1000, 1)
            w.close()
            try: await w.wait_closed()
            except Exception: pass
            return {"ip": ip, "port": port, "ping": ms}
        except Exception:
            return None


async def _scan(ips):
    sem = asyncio.Semaphore(SCAN_CONCURRENCY)
    tasks = []
    for x in ips:
        for p in SCAN_PORTS:
            tasks.append(_probe(x["ip"], p, sem))
    results = await asyncio.gather(*tasks)
    by_ip = {}
    for r in results:
        if r: by_ip.setdefault(r["ip"], []).append(r)
    out = []
    for ip, ports in by_ip.items():
        best = min(ports, key=lambda x: x["ping"])
        out.append({"ip": ip, "ping": best["ping"], "ports": sorted({p["port"] for p in ports})})
    out.sort(key=lambda x: x["ping"])
    return out


async def fetch_clean_async():
    try:
        loop = asyncio.get_running_loop()
        raw = await loop.run_in_executor(None, _fetch_source)
        if not raw: return []
        raw = sorted(raw, key=lambda x: x["ping"])[:MAX_SOURCE_IPS]
        scanned = await _scan(raw)
        return [x for x in scanned if x["ping"] <= MAX_REMIX_PING]
    except Exception as e:
        print("clean IP scanner failed:", e)
        return []


def fetch_clean():
    try:
        return asyncio.run(fetch_clean_async())
    except RuntimeError:
        return []


def remix_config(cfg, new_ip, new_port=None):
    proto = cfg.split("://", 1)[0].lower()
    if proto == "vmess":
        try:
            raw = cfg.split("://", 1)[1].split("#", 1)[0]
            raw += "=" * ((4 - len(raw) % 4) % 4)
            obj = json.loads(base64.b64decode(raw).decode("utf-8", "ignore"))
            old = obj.get("add", "")
            obj["add"] = new_ip
            if new_port: obj["port"] = str(new_port)
            if not obj.get("sni") and obj.get("tls"): obj["sni"] = obj.get("host") or old
            if not obj.get("host"): obj["host"] = old
            label = cfg.split("#", 1)[1] if "#" in cfg else "Xfinder-remix"
            body = base64.b64encode(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()).decode().rstrip("=")
            return "vmess://" + body + "#" + label
        except Exception:
            return cfg
    m = re.search(r"@(\[[^\]]+\]|[^:/?#]+)(?::(\d+))?", cfg)
    if not m: return cfg
    old = m.group(1).strip("[]")
    port = str(new_port or (m.group(2) or ""))
    replacement = new_ip + ((":" + port) if port else "")
    out = cfg[:m.start(1)] + replacement + cfg[m.end():]  # m.end(): also drop the OLD port
    head, _, tag = out.partition("#")
    if "?" in head:
        if "sni=" not in head and "security=none" not in head: head += "&sni=" + old
        if "host=" not in head and "type=ws" in head: head += "&host=" + old
    return head + ("#" + tag if tag else "")


def build(items):
    return build_with(items, fetch_clean())


def build_with(items, ips):
    if not ips: return items, []
    remixed = []
    base = sorted(items, key=lambda x: (-int(x.get("trust_score", 0)), x.get("http_ping_ms") or x.get("tcp_ping_ms") or 9999))[:REMIX_BASE_LIMIT]
    for item in base:
        if item.get("protocol") not in {"vless", "vmess", "trojan"}: continue
        original_port = int(item.get("port") or 443)
        for clean in ips[:REMIX_PER_CONFIG]:
            # Prefer the original port when the scanner confirms it; otherwise use
            # the fastest reachable port on that clean IP.
            ports = clean.get("ports") or []
            port = original_port if original_port in ports else (ports[0] if ports else original_port)
            r = dict(item)
            r["config"] = remix_config(item["config"], clean["ip"], port)
            r["server"] = clean["ip"]; r["port"] = port
            r["is_remixed"] = True; r["remix_ping_ms"] = clean["ping"]
            r["source"] = item.get("source", "") + " + CleanIP Scanner"
            remixed.append(r)
    return items, remixed
