import asyncio, os, sys, time
from collections import Counter
from .config import (MAX_WG_CANDIDATES, DATA_DIR, PIPELINE_BUDGET, MAX_TCP_CANDIDATES, MAX_XRAY_CANDIDATES, MAX_PER_ENDPOINT)
from .health_monitor import init_db
from .finder import collect, SOURCE_STATS
from .validator import validate
from .xray_probe import validate_xray, check_binary
from .remixer import fetch_clean_async, build_with
from .publisher import publish
from .donations import load_active, cleanup
from .naming import original_name, rename
from . import wg_sources
import random
from .config import BRAND


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


async def _validate_wg(items, deadline):
    """WireGuard (UDP): بدون تست TCP؛ مستقیم Xray + HTTPS واقعی."""
    cands = []
    for x in items:
        try:
            d = wg_sources.parse_uri(x["config"])
        except Exception:
            continue
        x.update({"server": d["host"], "port": d["port"], "tcp_ping_ms": None, "config": wg_sources.to_uri(d, "WG")})
        cands.append(x)
    random.shuffle(cands)
    cands = limit_per_endpoint(cands)[:MAX_WG_CANDIDATES]
    if not cands:
        log("wireguard: 0 usable candidates in sources")
        return []
    tested = await validate_xray(cands, xray_binary(), deadline=deadline)
    good = [x for x in tested if x.get("xray_alive")]
    for x in good:
        x["alive"] = True
        x["protocol"] = "wireguard"
        x["conf"] = wg_sources.conf_from_uri(x["config"])
    good.sort(key=lambda x: x.get("http_ping_ms") or 9999)
    log(f"wireguard: {len(cands)} candidates -> {len(good)} passed real Xray probe")
    return good


WARP_FALLBACK = ["162.159.192.1", "162.159.195.1", "188.114.96.1", "188.114.97.1", "188.114.98.1", "188.114.99.1"]


async def _remix_wg(good, clean, deadline):
    """WireGuard + IP تمیز: حساب‌های سالم را روی endpointهای WARP جدید (ترجیحاً از Scanner-matix) امتحان می‌کند.
    فقط IPهای داخل رنج WARP کلودفلر معنی دارند (UDP)؛ هر ترکیب با Xray واقعی تست می‌شود و ناموفق‌ها حذف می‌شوند."""
    ping_of = {c["ip"]: c.get("ping") for c in clean}
    ips = [c["ip"] for c in clean if wg_sources.is_warp_ip(c["ip"])][:8]
    scanner = bool(ips)
    if not ips:
        ips = WARP_FALLBACK
    bases, seen = [], set()
    for x in good:
        try:
            d = wg_sources.parse_uri(x["config"])
        except Exception:
            continue
        if d["private_key"] not in seen:
            seen.add(d["private_key"]); bases.append(d)
        if len(bases) >= 4:
            break
    cands = []
    for d in bases:
        for ip in ips:
            nd = wg_sources.with_endpoint(d, ip, 2408)
            cands.append({"config": wg_sources.to_uri(nd, "WG"), "server": ip, "port": 2408, "is_remixed": True,
                          "source": "Scanner-matix + WireGuard" if scanner else "WARP endpoint swap", "trust_score": 85,
                          "tcp_ping_ms": ping_of.get(ip)})
    if not cands:
        return []
    tested = await validate_xray(cands, xray_binary(), deadline=deadline)
    ok = [x for x in tested if x.get("xray_alive")]
    for x in ok:
        x.update({"alive": True, "protocol": "wireguard", "conf": wg_sources.conf_from_uri(x["config"])})
    ok.sort(key=lambda x: x.get("http_ping_ms") or 9999)
    log(f"wireguard remix ({'Scanner-matix' if scanner else 'builtin WARP endpoints'}): {len(cands)} -> {len(ok)} passed")
    return ok[:12]


async def run():
    t0 = time.monotonic()
    b = PIPELINE_BUDGET
    check_binary(xray_binary())          # fail fast and loudly if Xray is missing
    init_db()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 0) اهدای کانفیگ: فایل‌های منقضی (بیش از ۲۴ ساعت) پاک می‌شوند.
    try:
        cleanup()
    except Exception as e:
        log("donation cleanup skipped:", e)

    # 1) Collect -> TCP pre-filter -> real Xray/HTTPS probe.
    raw = await collect()
    wg_raw = [x for x in raw if x["config"].lower().startswith("wireguard://")]
    raw = [x for x in raw if not x["config"].lower().startswith("wireguard://")]
    log(f"collected {len(raw)} unique configs (+{len(wg_raw)} wireguard) in {time.monotonic() - t0:.0f}s")
    validated = await _real_validate(raw, "base", t0 + 0.25 * b, t0 + 0.70 * b)

    # 1b) WireGuard منابع (UDP) — جدا از بقیه، با بودجه‌ی زمانی کوچک.
    wg_good = []
    try:
        if wg_raw and validated:
            wg_good = await _validate_wg(wg_raw, t0 + 0.78 * b)
    except Exception as e:
        log("wireguard stage skipped:", e)

    # 2) Clean-IP scanner results -> remix -> real Xray probe again.
    remixed, clean = [], []
    if validated and time.monotonic() < t0 + 0.80 * b:
        clean = await fetch_clean_async()
        log(f"clean IPs usable: {len(clean)}" if clean else "clean IPs: Scanner-matix returned nothing usable; remix skipped")
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
    try:
        if wg_good and time.monotonic() < t0 + 0.93 * b:
            wg_new = await _remix_wg(wg_good, clean, t0 + 0.95 * b)
            have = {x["config"] for x in wg_good}
            wg_good = [x for x in wg_new if x["config"] not in have] + wg_good
    except Exception as e:
        log("wireguard remix skipped:", e)

    # 3) کانفیگ‌های اهدایی: جدا و با همان تست واقعی Xray؛ فقط سالم‌ها نمایش داده می‌شوند.
    donations = []
    try:
        active = load_active()
        flat = [{"config": c, "source": f"Donation #{d['id']}", "trust_score": 70}
                for d in active for c in d["configs"]]
        if flat:
            ok = await _real_validate(flat, "donation", time.monotonic() + 40, time.monotonic() + 100)
            good = {x["config"]: x for x in ok}
            for d in active:
                rows = []
                for c in d["configs"]:
                    x = good.get(c)
                    if x:
                        ping = x.get("http_ping_ms") or x.get("tcp_ping_ms")
                        donor = (d.get("name") or "").strip()
                        label = f"{BRAND} | {donor}" if donor else BRAND
                        pn = {"ss": "SS", "hysteria2": "HY2"}.get(x.get("protocol"), (x.get("protocol") or "").upper())
                        nm = f"{label} • {pn}" + (f" • {int(round(ping))}ms" if ping else "")
                        rows.append({"config": rename(c, nm), "name": nm, "protocol": x.get("protocol"), "ping": ping})
                if rows:
                    donations.append({"id": d["id"], "name": d.get("name", ""), "ad": d.get("ad", ""),
                                      "created_at": d["created_at"], "expires_at": d["expires_at"], "configs": rows})
        log(f"donations: {len(active)} active, {len(donations)} verified")
    except Exception as e:
        log("donations skipped:", e)

    publish(validated, remixed, wg_good, list(SOURCE_STATS), len(raw), donations, len(clean))
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
