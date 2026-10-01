"""اعتبارسنجی اولیه URI و تست TCP محدود."""
import asyncio
import socket
import time
from urllib.parse import urlsplit, unquote
from .settings import TCP_CONCURRENCY, TCP_CONCURRENCY_MAX, TCP_TIMEOUT_SECONDS, MAX_CONFIGS_TO_TEST

SUPPORTED = ("vless://", "vmess://", "trojan://", "ss://", "hysteria2://", "hy2://", "tuic://", "wireguard://")

def protocol_of(config):
    return config.split("://", 1)[0].lower() if "://" in config else "unknown"

def endpoint_of(config):
    """استخراج میزبان/پورت از URIهایی که ساختار userinfo@host:port دارند."""
    proto = protocol_of(config)
    if proto == "vmess":
        return None
    try:
        parsed = urlsplit(config)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return None
        return host, port
    except (ValueError, TypeError):
        return None

def basic_validate(config):
    if not config.startswith(SUPPORTED):
        return False
    if len(config) > 20_000:
        return False
    if protocol_of(config) == "vmess":
        # ساختار VMess معمولاً Base64 است؛ فقط وجود payload بررسی می‌شود.
        return len(config) > len("vmess://")
    return endpoint_of(config) is not None

async def tcp_test(config, semaphore):
    endpoint = endpoint_of(config)
    if endpoint is None:
        return {"latency_ms": None, "tcp_alive": None}
    host, port = endpoint
    async with semaphore:
        started = time.perf_counter()
        try:
            loop = asyncio.get_running_loop()
            await asyncio.wait_for(
                loop.getaddrinfo(host, port, type=socket.SOCK_STREAM),
                timeout=TCP_TIMEOUT_SECONDS
            )
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=TCP_TIMEOUT_SECONDS
            )
            latency = round((time.perf_counter() - started) * 1000, 1)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            return {"latency_ms": latency, "tcp_alive": True}
        except Exception:
            return {"latency_ms": None, "tcp_alive": False}

async def validate(configs):
    concurrency = max(1, min(int(TCP_CONCURRENCY), TCP_CONCURRENCY_MAX))
    semaphore = asyncio.Semaphore(concurrency)
    unique = list(dict.fromkeys(configs))
    output = []
    # سقف تعداد تست برای جلوگیری از ایجاد بار زیاد روی شبکه
    for config in unique[:MAX_CONFIGS_TO_TEST]:
        valid = basic_validate(config)
        row = {
            "config": config,
            "protocol": protocol_of(config),
            "host": (endpoint_of(config) or (None, None))[0],
            "port": (endpoint_of(config) or (None, None))[1],
            "valid": valid,
            "latency_ms": None,
            "tcp_alive": None,
        }
        if valid:
            row.update(await tcp_test(config, semaphore))
        output.append(row)
    return output
