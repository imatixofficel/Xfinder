import asyncio, json
from pathlib import Path
from .health_monitor import init_db
from .finder import collect, SOURCE_STATS
from .validator import validate
from .xray_probe import validate_xray
from .remixer import fetch_clean_async, build_with

from .publisher import publish


def xray_binary():
    # GitHub Actions sets XRAY_BIN; local runs can put xray in PATH.
    import os
    return os.getenv("XRAY_BIN", "xray")


async def _real_validate(items, label):
    tcp_alive = [x for x in await validate(items) if x.get("alive")]
    if not tcp_alive:
        print(f"{label}: 0 passed TCP")
        return []
    tested = await validate_xray(tcp_alive, xray_binary())
    good = [x for x in tested if x.get("xray_alive")]
    for x in good:
        x["alive"] = True
    print(f"{label}: {len(tcp_alive)} passed TCP, {len(good)} passed real Xray probe")
    return good


async def run():
    init_db()
    Path("data").mkdir(exist_ok=True)

    # 1) Collect -> TCP pre-filter -> real Xray/HTTPS probe.
    raw = await collect()
    validated = await _real_validate(raw, "base")
    for x in validated:
        x["protocol"] = x["config"].split("://", 1)[0].lower()
    validated.sort(key=lambda x: x.get("http_ping_ms") or x.get("tcp_ping_ms") or 9999)

    # 2) Clean-IP scanner results -> remix -> real Xray probe again.
    clean = await fetch_clean_async()
    _, remixed_candidates = build_with(validated, clean)
    remixed = await _real_validate(remixed_candidates, "remix")
    for x in remixed:
        x["protocol"] = x["config"].split("://", 1)[0].lower()
        x["is_remixed"] = True
    remixed.sort(key=lambda x: x.get("http_ping_ms") or x.get("tcp_ping_ms") or 9999)

    # Automatic WARP generation is intentionally not published: a generated
    # WireGuard private key is a credential. The browser-side generator remains
    # available in the site for personal configs.
    wg = []

    publish(validated, remixed, wg, list(SOURCE_STATS), len(raw))
    print(f"Xfinder complete: {len(validated)} real-tested, {len(remixed)} real-tested remix, WG auto-publish disabled")


if __name__ == "__main__":
    asyncio.run(run())
