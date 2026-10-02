"""جمع‌آوری کانفیگ‌ها از منابع تعریف‌شده و نرمال‌سازی فرمت‌های مختلف."""
import asyncio, base64, json, random, re
from urllib.request import Request, urlopen
from .config import SOURCES, BLACKLIST, MAX_PER_SOURCE
from .discover import discover
from .wg_sources import confs_to_uris

URI_PATTERN = re.compile(r"(?i)(?:vless|vmess|trojan|ss|hysteria2|wireguard)://[^\s\"'<>\\]+")
MAX_BYTES = 40_000_000


def fetch(url, timeout=20):
    req = Request(url, headers={"User-Agent": "Xfinder/2.4 (+GitHub Actions)"})
    with urlopen(req, timeout=timeout) as r:
        return r.read(MAX_BYTES).decode("utf-8", "ignore")


def decode_base64_text(text):
    compact = "".join(text.split())
    if len(compact) < 16:
        return ""
    compact = compact.replace("-", "+").replace("_", "/")
    try:
        return base64.b64decode(compact + "=" * ((4 - len(compact) % 4) % 4), validate=False).decode("utf-8", "ignore")
    except Exception:
        return ""


def vmess_json_to_uri(obj):
    """VMess JSON قدیمی را به vmess:// base64 تبدیل می‌کند."""
    if not isinstance(obj, dict) or not obj.get("add") or not obj.get("port"):
        return None
    headers = obj.get("headers")
    clean = {
        "v": str(obj.get("v", 2)), "ps": str(obj.get("ps", obj.get("remarks", "Xfinder"))),
        "add": str(obj["add"]), "port": str(obj["port"]), "id": str(obj.get("id", obj.get("uuid", ""))),
        "aid": str(obj.get("aid", obj.get("alterId", 0))), "scy": str(obj.get("scy", "auto")),
        "net": str(obj.get("net", obj.get("type", "tcp"))), "type": str(obj.get("type", "none")),
        "host": str(obj.get("host", headers.get("Host", "") if isinstance(headers, dict) else "")),
        "path": str(obj.get("path", "")), "tls": str(obj.get("tls", "")), "sni": str(obj.get("sni", "")),
        "alpn": str(obj.get("alpn", "")), "fp": str(obj.get("fp", "")),
        "allowInsecure": str(obj.get("allowInsecure", obj.get("allow_insecure", ""))),
    }
    raw = json.dumps(clean, separators=(",", ":"), ensure_ascii=False).encode()
    return "vmess://" + base64.b64encode(raw).decode().rstrip("=")


def extract(text):
    """URI مستقیم، Base64 subscription و JSONهای Delta را پشتیبانی می‌کند."""
    bodies = [text]
    decoded = decode_base64_text(text)
    if decoded:
        bodies.append(decoded)
    found = []
    for body in bodies:
        found.extend(URI_PATTERN.findall(body))
        if "[Interface]" in body:
            found.extend(confs_to_uris(body))
        if body.lstrip()[:1] in "[{":
            try:
                parsed = json.loads(body)
                stack = [parsed]
                while stack:
                    x = stack.pop()
                    if isinstance(x, dict):
                        u = vmess_json_to_uri(x)
                        if u:
                            found.append(u)
                        stack.extend(x.values())
                    elif isinstance(x, list):
                        stack.extend(x)
            except Exception:
                pass
    cleaned, seen = [], set()
    for u in found:
        u = u.rstrip(".,;)]}")
        if u not in seen:
            seen.add(u)
            cleaned.append(u)
    return cleaned


SOURCE_STATS = []


async def collect():
    loop = asyncio.get_running_loop()
    out = []
    SOURCE_STATS.clear()

    async def one(src):
        if any(b.lower() in src["name"].lower() for b in BLACKLIST):
            return []
        try:
            text = await loop.run_in_executor(None, fetch, src["url"])
            cfgs = extract(text)
            total = len(cfgs)
            if total > MAX_PER_SOURCE:  # random sample -> different slice every run
                cfgs = random.sample(cfgs, MAX_PER_SOURCE)
            items = [{"config": c, "source": src["name"], "trust_score": src["trust"]} for c in cfgs]
            SOURCE_STATS.append({"name": src["name"], "trust": src["trust"], "count": total, "ok": bool(items)})
            print(f"source ok: {src['name']} total={total} used={len(items)}", flush=True)
            return items
        except Exception as e:
            print("source failed:", src["name"], e, flush=True)
            SOURCE_STATS.append({"name": src["name"], "trust": src["trust"], "count": 0, "ok": False})
            return []

    try:
        extra = await loop.run_in_executor(None, discover, [x["name"] for x in SOURCES])
    except Exception:
        extra = []
    batches = await asyncio.gather(*(one(s) for s in list(SOURCES) + extra))
    seen = set()
    for batch in batches:
        for it in batch:
            if it["config"] not in seen:
                seen.add(it["config"])
                out.append(it)
    return out


if __name__ == "__main__":
    data = asyncio.run(collect())
    json.dump(data, open("data/raw_configs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("collected", len(data))
