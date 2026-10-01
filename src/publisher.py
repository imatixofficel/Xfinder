"""تولید JSON و فایل‌های متنی و داشبورد."""
import json
from datetime import datetime, timezone
from pathlib import Path

PROTOCOLS = ["vless", "vmess", "trojan", "ss", "hysteria2", "tuic", "wireguard"]

def publish(rows, source_summary, output_dir="output"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    alive = [r for r in rows if r.get("tcp_alive") is True]
    updated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    stats = {
        "updated_at": updated,
        "total": len(rows),
        "valid": sum(1 for r in rows if r["valid"]),
        "alive": len(alive),
        "sources_total": len(source_summary),
        "sources_active": sum(1 for s in source_summary if s["active"]),
        "average_latency_ms": round(sum(r["latency_ms"] for r in alive if r["latency_ms"] is not None) / max(1, sum(1 for r in alive if r["latency_ms"] is not None)), 1) if alive else None,
        "configs": rows,
        "sources": source_summary,
    }
    (out / "configs.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    for proto in PROTOCOLS:
        items = [r["config"] for r in rows if r["protocol"] == proto and r["valid"]]
        (out / f"{proto}.txt").write_text("\n".join(items) + ("\n" if items else ""), encoding="utf-8")
    all_items = [r["config"] for r in rows if r["valid"]]
    (out / "all.txt").write_text("\n".join(all_items) + ("\n" if all_items else ""), encoding="utf-8")
    return stats
