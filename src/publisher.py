import base64, json
from datetime import datetime, timezone
from .config import DATA_DIR, OUTPUT_DIR, MAX_PUBLISH_BASE, TOP_N, BRAND
from .naming import original_name, rename, make_label


def _ping(x):
    return x.get("http_ping_ms") or x.get("tcp_ping_ms") or 9999


def publish(items, remixed, wireguard=(), source_stats=(), raw_total=0, donations=(), clean_ips=0):
    """ترتیب نمایش: اول کانفیگ‌های ترکیب‌شده با IP تمیز، بعد WireGuard، بعد بقیه."""
    items = list(items)[:MAX_PUBLISH_BASE]
    all_items = list(remixed) + list(wireguard) + items
    for i, x in enumerate(all_items, 1):
        x["protocol"] = x.get("protocol") or x["config"].split("://", 1)[0].lower()
        x.setdefault("http_ping_ms", None); x.setdefault("is_remixed", False)
        x.setdefault("country", "UN"); x.setdefault("country_flag", "🌐")
        if x["protocol"] != "wireguard":   # WireGuard یک فایل .conf است، نه URI
            x["orig_name"] = original_name(x["config"])[:60]
            x["name"] = make_label(x["protocol"], _ping(x) if _ping(x) != 9999 else None, i, x["is_remixed"], BRAND)
            x["config"] = rename(x["config"], x["name"])
        else:
            x["name"] = x.get("name") or "WireGuard"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True); DATA_DIR.mkdir(parents=True, exist_ok=True)
    groups = {p: [] for p in ["vless", "vmess", "trojan", "ss", "hysteria2", "wireguard"]}
    for x in all_items: groups.setdefault(x["protocol"], []).append(x["config"])
    for p, lines in groups.items():
        (OUTPUT_DIR / f"{p}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "all.txt").write_text("\n".join(x["config"] for x in all_items) + "\n", encoding="utf-8")

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

    pings = [x["tcp_ping_ms"] for x in all_items if x.get("tcp_ping_ms")]
    avg = round(sum(pings) / len(pings)) if pings else 0
    ok = [s for s in source_stats if s.get("ok")]
    data = {"updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": {"total": len(all_items), "alive": len(items), "remixed": len(remixed), "wireguard": len(wireguard),
                      "avg_ping": avg, "clean_ips": clean_ips, "top": len(top)},
            "sources": {"total": len(source_stats), "active": len(ok), "dead_removed": len(source_stats) - len(ok)},
            "source_list": list(source_stats), "donations": list(donations), "configs": all_items}
    (DATA_DIR / "configs.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (DATA_DIR / "donations.json").write_text(json.dumps({"updated_at": data["updated_at"], "donations": list(donations)},
                                                       ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return data
