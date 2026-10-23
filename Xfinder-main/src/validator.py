"""اعتبارسنجی مرحله اول: اتصال TCP به endpoint واقعی هر کانفیگ."""
import asyncio, base64, json, re, socket, time
from urllib.parse import urlparse
from .config import CONCURRENCY, TCP_TIMEOUT


def _b64(s):
    s = s.strip().replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * ((4 - len(s) % 4) % 4))


def vmess_endpoint(cfg):
    try:
        raw = cfg.split("://", 1)[1].split("#", 1)[0]
        obj = json.loads(_b64(raw).decode("utf-8", "ignore"))
        return str(obj.get("add", "")), int(obj.get("port", 443))
    except Exception:
        return "", 443


def ss_endpoint(cfg):
    try:
        rest = cfg.split("://", 1)[1].split("#", 1)[0].split("?", 1)[0]
        if "@" not in rest:
            rest = _b64(rest).decode("utf-8", "ignore")
        hp = rest.rsplit("@", 1)[1]
        if hp.startswith("["):
            end = hp.find("]")
            return hp[1:end], int(hp[end + 2:])
        host, port = hp.rsplit(":", 1)
        return host, int(port)
    except Exception:
        return "", 443


def endpoint(cfg):
    proto = cfg.split("://", 1)[0].lower()
    if proto == "vmess":
        return vmess_endpoint(cfg)
    if proto == "ss":
        return ss_endpoint(cfg)
    try:
        u = urlparse(cfg)
        host = u.hostname or ""
        port = u.port or 443
        if host:
            return host, port
    except Exception:
        pass
    m = re.search(r"@([^/?#]+)", cfg)
    if m:
        hp = m.group(1)
        try:
            host, port = hp.rsplit(":", 1)
            return host.strip("[]"), int(port)
        except Exception:
            return hp.strip("[]"), 443
    return "", 443


def install_big_executor(loop, workers=256):
    """DNS (getaddrinfo) runs in the default executor. The stock executor only has
    ~6 threads, so hundreds of slow DNS lookups serialize and the run appears hung."""
    from concurrent.futures import ThreadPoolExecutor
    loop.set_default_executor(ThreadPoolExecutor(max_workers=workers, thread_name_prefix="xf"))


async def tcp_probe(item, sem):
    async with sem:
        host, port = endpoint(item["config"])
        start = time.perf_counter()
        if not host or not (0 < port < 65536):
            item.update({"server": host, "port": port, "tcp_ping_ms": None, "alive": False})
            return item
        try:
            fut = asyncio.open_connection(host, port, family=socket.AF_UNSPEC)
            reader, writer = await asyncio.wait_for(fut, timeout=TCP_TIMEOUT)
            ms = round((time.perf_counter() - start) * 1000, 1)
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), 1)
            except Exception:
                pass
            item.update({"server": host, "port": port, "tcp_ping_ms": ms, "alive": True})
        except (Exception, asyncio.CancelledError):
            item.update({"server": host, "port": port, "tcp_ping_ms": None, "alive": False})
        return item


async def validate(items, deadline=None):
    """TCP-check all items. Never blocks past `deadline` (monotonic seconds);
    items not finished by then are simply treated as dead."""
    install_big_executor(asyncio.get_running_loop())
    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [asyncio.ensure_future(tcp_probe(x, sem)) for x in items]
    if not tasks:
        return []
    timeout = None if deadline is None else max(0.1, deadline - time.monotonic())
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    for t in pending:
        t.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
        print(f"tcp stage hit its time budget: {len(done)} done, {len(pending)} skipped", flush=True)
    return [x for x in items if x.get("alive")]


if __name__ == "__main__":
    raw = json.load(open("data/raw_configs.json", encoding="utf-8"))
    good = asyncio.run(validate(raw))
    json.dump(good, open("data/validated.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("alive:", len(good))
