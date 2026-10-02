import asyncio, os, sys, time
from collections import Counter
from .config import (DATA_DIR, PIPELINE_BUDGET, MAX_TCP_CANDIDATES, MAX_XRAY_CANDIDATES, MAX_PER_ENDPOINT)
from .health_monitor import init_db
from .finder import collect, SOURCE_STATS
from .validator import validate
from .xray_probe import validate_xray, check_binary
from .remixer import fetch_clean_async, build_with
from .publisher import publish


def log(*a):
    print(*a, flush=True)


def xray_binary():
    # GitHub Actions sets XRAY_BIN; local runs can put xray in PATH.
    return os.getenv("XRAY_BIN", "xray")


def limit_per_endpoint(items, n=MAX_PER_ENDPOINT):
    seen, out = Counter(), []
    for x in items:
        key = (x.get("server"), x.get("port"))
        if seen[key] < n:
            seen[key] += 1
            out.append(x)
    return out


async def _real_validate(items, label, tcp_deadline, xray_deadline):
    items = items[:MAX_TCP_CANDIDATES]
    tcp_alive = await validate(items, deadline=tcp_deadline)
    tcp_alive.sort(key=lambda x: x.get("tcp_ping_ms") or 9999)
    tcp_alive = limit_per_endpoint(tcp_alive)[:MAX_XRAY_CANDIDATES]
    if not tcp_alive:
        log(f"{label}: 0 passed TCP")
        return []
    log(f"{label}: {len(items)} candidates -> {len(tcp_alive)} passed TCP, starting real Xray probe")
    tested = await validate_xray(tcp_alive, xray_binary(), deadline=xray_deadline)
    good = [x for x in tested if x.get("xray_alive")]
    for x in good:
        x["alive"] = True
        x["protocol"] = x["config"].split("://", 1)[0].lower()
    good.sort(key=lambda x: x.get("http_ping_ms") or x.get("tcp_ping_ms") or 9999)
    log(f"{label}: {len(tested)} Xray-tested, {len(good)} passed real Xray probe")
    return good


async def run():
    t0 = time.monotonic()
    b = PIPELINE_BUDGET
    check_binary(xray_binary())          # fail fast and loudly if Xray is missing
    init_db()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Collect -> TCP pre-filter -> real Xray/HTTPS probe.
    raw = await collect()
    log(f"collected {len(raw)} unique configs in {time.monotonic() - t0:.0f}s")
    validated = await _real_validate(raw, "base", t0 + 0.25 * b, t0 + 0.70 * b)

    # 2) Clean-IP scanner results -> remix -> real Xray probe again.
    remixed = []
    if validated and time.monotonic() < t0 + 0.80 * b:
        clean = await fetch_clean_async()
        log(f"clean IPs usable: {len(clean)}")
        _, candidates = build_with(validated, clean)
        remixed = await _real_validate(candidates, "remix", t0 + 0.85 * b, t0 + 0.95 * b)
        for x in remixed:
            x["is_remixed"] = True

    if not validated:
        # Do NOT publish an empty site over a good one: fail the job instead.
        raise SystemExit("ERROR: no config passed real Xray validation; nothing published.")

    # Automatic WARP generation is intentionally not published: a generated
    # WireGuard private key is a credential. The browser-side generator remains
    # available in the site for personal configs.
    publish(validated, remixed, [], list(SOURCE_STATS), len(raw))
    log(f"Xfinder complete in {time.monotonic() - t0:.0f}s: {len(validated)} real-tested, "
        f"{len(remixed)} real-tested remix")


def main():
    code = 0
    try:
        asyncio.run(run())
    except SystemExit as e:
        code = 1 if e.code not in (0, None) else 0
        if e.code not in (0, None):
            print(e.code, file=sys.stderr, flush=True)
    except BaseException as e:
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    # Abandoned DNS threads must never keep the process (and the CI job) alive.
    os._exit(code)


if __name__ == "__main__":
    main()
