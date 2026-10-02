import json
from datetime import datetime, timezone
from .config import ROOT, OUTPUT_DIR, MAX_PUBLISH_BASE

def publish(items, remixed, wireguard=(), source_stats=(), raw_total=0):
    """ترتیب نمایش: اول کانفیگ‌های ترکیب‌شده با IP تمیز، بعد WireGuard، بعد بقیه."""
    items = list(items)[:MAX_PUBLISH_BASE]
    all_items = list(remixed) + list(wireguard) + items
    for x in all_items:
        x["protocol"] = x.get("protocol") or x["config"].split("://", 1)[0].lower()
        x.setdefault("http_ping_ms", None); x.setdefault("is_remixed", False)
        x.setdefault("country", "UN"); x.setdefault("country_flag", "🌐")
    OUTPUT_DIR.mkdir(exist_ok=True)
    groups = {p: [] for p in ["vless", "vmess", "trojan", "ss", "hysteria2", "wireguard"]}
    for x in all_items: groups.setdefault(x["protocol"], []).append(x["config"])
    for p, lines in groups.items():
        (OUTPUT_DIR / f"{p}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "all.txt").write_text("\n".join(x["config"] for x in all_items) + "\n", encoding="utf-8")
    pings = [x["tcp_ping_ms"] for x in all_items if x.get("tcp_ping_ms")]
    avg = round(sum(pings) / len(pings)) if pings else 0
    ok = [s for s in source_stats if s.get("ok")]
    data = {"updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": {"total": len(all_items), "alive": len(items), "remixed": len(remixed), "wireguard": len(wireguard), "avg_ping": avg},
            "sources": {"total": len(source_stats), "active": len(ok), "dead_removed": len(source_stats) - len(ok)},
            "source_list": list(source_stats), "configs": all_items}
    (ROOT / "data/configs.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return data
