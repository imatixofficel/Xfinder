import base64, json, time
from datetime import datetime, timezone
from .config import DATA_DIR, OUTPUT_DIR, MAX_PUBLISH_BASE, MAX_HTTP_PING_MS, TOP_N, BRAND
from .naming import original_name, rename, tagged_name
from .geo import flag


def _ping(x):
    return x.get("http_ping_ms") or x.get("tcp_ping_ms") or 9999


SLIM_KEYS = ("config", "name", "orig_name", "protocol", "server", "port", "tcp_ping_ms", "http_ping_ms",
             "is_remixed", "source", "trust_score", "rank", "conf", "country", "country_flag",
             "country_code", "download_speed", "speed_rank", "last_tested")


def slim(x):
    """فقط فیلدهای لازم برای سایت (JSON سبک‌تر)."""
    return {k: x[k] for k in SLIM_KEYS if k in x and x[k] is not None}


def clean_items(items):
    """حذف خراب‌ها: بدون تست واقعی، تکراری، و خیلی کند؛ سریع‌ترین‌ها اول."""
    out, seen = [], set()
    for x in sorted(items, key=_ping):      # سریع‌ترین نسخه‌ی هر تکراری می‌ماند
        if not x.get("alive", True) or x.get("xray_alive") is False:
            continue
        ping = x.get("http_ping_ms")
        if ping is not None and ping > MAX_HTTP_PING_MS:
            continue
        key = x["config"].split("#", 1)[0]
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out


def publish(items, remixed, wireguard=(), source_stats=(), raw_total=0, donations=(), clean_ips=0):
    """ترتیب نمایش: اول کانفیگ‌های ترکیب‌شده با IP تمیز، بعد WireGuard، بعد بقیه."""
    items = clean_items(items)[:MAX_PUBLISH_BASE]
    all_items = list(remixed) + list(wireguard) + items
    for i, x in enumerate(all_items, 1):
        x["protocol"] = x.get("protocol") or x["config"].split("://", 1)[0].lower()
        x.setdefault("http_ping_ms", None); x.setdefault("is_remixed", False)
        x.setdefault("country", "Unknown"); x.setdefault("country_code", ""); x.setdefault("country_flag", "🌐")
        x.setdefault("last_tested", int(time.time()))
        if x["protocol"] != "wireguard" or x["config"].lower().startswith("wireguard://"):   # URI قابل نام‌گذاری
            orig = original_name(x["config"])
            x["orig_name"] = orig[:60]
            x["name"] = tagged_name(
                orig, x["protocol"], BRAND, seed=f"{x.get('server')}:{x.get('port')}:{x['config'].split('#', 1)[0]}",
                flag=flag(x.get("country_code")), ping=_ping(x) if _ping(x) != 9999 else None,
                speed=x.get("download_speed"))
            x["config"] = rename(x["config"], x["name"])
        else:
            x["name"] = x.get("name") or "WireGuard"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True); DATA_DIR.mkdir(parents=True, exist_ok=True)
    groups = {p: [] for p in ["vless", "vmess", "trojan", "ss", "hysteria2", "wireguard"]}
    for x in all_items: groups.setdefault(x["protocol"], []).append(x["config"])
    for p, lines in groups.items():
        (OUTPUT_DIR / f"{p}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # all.txt بدون WireGuard: همه‌ی برنامه‌ها wireguard:// را در اشتراک نمی‌فهمند (فایل جدا: wireguard.txt)
    (OUTPUT_DIR / "all.txt").write_text("\n".join(x["config"] for x in all_items if x["protocol"] != "wireguard") + "\n", encoding="utf-8")

    # ۲۰ کانفیگ برتر: همه‌ی کاندیدها قبلاً با Xray + HTTPS واقعی تست شده‌اند؛ کمترین پینگ واقعی اول.
    top, seen = [], set()
    for x in sorted((y for y in all_items if y["protocol"] != "wireguard"), key=_ping):
        key = (x.get("server"), x.get("port"))
        if key in seen:
            continue
        seen.add(key); top.append(x)
        if len(top) >= TOP_N:
            break
    for r, x in enumerate(top, 1):
        x["rank"] = r
    top_text = "\n".join(x["config"] for x in top) + ("\n" if top else "")
    (OUTPUT_DIR / "top20.txt").write_text(top_text, encoding="utf-8")
    (OUTPUT_DIR / "top20-b64.txt").write_text(base64.b64encode(top_text.encode()).decode(), encoding="utf-8")

    # نام/آدرس منابع در خروجی عمومی نمایش داده نمی‌شود (Source 1، Source 2، ...).
    alias = {s["name"]: f"Source {n}" for n, s in enumerate(source_stats, 1)}
    for x in all_items:
        x["source"] = alias.get(x.get("source"), "Source") if x.get("source") else x.get("source")
    source_stats = [dict(s, name=alias[s["name"]]) for s in source_stats]

    # ۲۰ کانفیگ پرسرعت: مرتب بر اساس سرعت دانلود واقعی (فقط کانفیگ‌های اندازه‌گیری‌شده).
    fast, seen = [], set()
    for x in sorted((y for y in all_items if y["protocol"] != "wireguard" and y.get("download_speed")),
                    key=lambda y: -y["download_speed"]):
        key = (x.get("server"), x.get("port"))
        if key in seen:
            continue
        seen.add(key); fast.append(x)
        if len(fast) >= TOP_N:
            break
    for r, x in enumerate(fast, 1):
        x["speed_rank"] = r
    fast_text = "\n".join(x["config"] for x in fast) + ("\n" if fast else "")
    (OUTPUT_DIR / "top20-speed.txt").write_text(fast_text, encoding="utf-8")
    (OUTPUT_DIR / "top20-speed-b64.txt").write_text(base64.b64encode(fast_text.encode()).decode(), encoding="utf-8")

    pings = [x["tcp_ping_ms"] for x in all_items if x.get("tcp_ping_ms")]
    avg = round(sum(pings) / len(pings)) if pings else 0
    ok = [s for s in source_stats if s.get("ok")]
    data = {"updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": {"total": len(all_items), "alive": len(items), "remixed": len(remixed), "wireguard": len(wireguard),
                      "avg_ping": avg, "clean_ips": clean_ips, "top": len(top), "speed_tested": sum(1 for x in all_items if x.get("download_speed")),
                      "countries": len({x["country_code"] for x in all_items if x.get("country_code")})},
            "sources": {"total": len(source_stats), "active": len(ok), "dead_removed": len(source_stats) - len(ok)},
            "source_list": list(source_stats), "donations": list(donations), "configs": [slim(x) for x in all_items]}
    (DATA_DIR / "configs.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (DATA_DIR / "donations.json").write_text(json.dumps({"updated_at": data["updated_at"], "donations": list(donations)},
                                                       ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return data
