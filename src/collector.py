"""دریافت کانفیگ از فایل‌های متنی عمومی."""
import base64
import httpx
from .settings import FETCH_TIMEOUT_SECONDS, MAX_BYTES_PER_SOURCE

PREFIXES = ("vless://", "vmess://", "trojan://", "ss://", "hysteria2://", "hy2://", "tuic://", "wireguard://")

def decode_subscription(text):
    """اگر متن شبیه subscription تک‌خطی Base64 باشد، تلاش به decode می‌کند."""
    raw = text.strip()
    if not raw or "\n" in raw or raw.startswith(PREFIXES):
        return text
    try:
        padded = raw + "=" * (-len(raw) % 4)
        decoded = base64.b64decode(padded, validate=False).decode("utf-8", errors="ignore")
        if any(decoded.strip().startswith(p) for p in PREFIXES):
            return decoded
    except Exception:
        pass
    return text

async def fetch_source(client, name, url):
    response = await client.get(url, timeout=FETCH_TIMEOUT_SECONDS, follow_redirects=True)
    response.raise_for_status()
    content = response.content
    if len(content) > MAX_BYTES_PER_SOURCE:
        raise ValueError(f"منبع بیش از سقف مجاز {MAX_BYTES_PER_SOURCE} بایت است")
    text = response.text
    text = decode_subscription(text)
    configs = []
    for line in text.splitlines():
        item = line.strip().lstrip("\ufeff")
        if item.startswith(PREFIXES):
            configs.append(item)
    return configs

async def collect(sources):
    headers = {"User-Agent": "Xfinder/1.0 (public-config-list collector)"}
    timeout = httpx.Timeout(FETCH_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        import asyncio
        tasks = [fetch_source(client, name, info["url"]) for name, info in sources.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    by_source = {}
    for (name, info), result in zip(sources.items(), results):
        if isinstance(result, Exception):
            by_source[name] = {"url": info["url"], "configs": [], "error": str(result)}
        else:
            by_source[name] = {"url": info["url"], "configs": result, "error": ""}
    return by_source
