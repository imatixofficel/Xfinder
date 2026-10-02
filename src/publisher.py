import json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
from .config import ROOT,OUTPUT_DIR

def protocol(cfg):
    return cfg.split("://",1)[0].lower()

def country(server):
    # GeoIP خارجی در این مرحله عمداً اختیاری است؛ برای انتشار پایدار، کشور را Unknown می‌گذاریم.
    return "UN","🌐"

def publish(items,remixed):
    all_items=items+remixed
    for x in all_items:
        x["protocol"]=x.get("protocol") or protocol(x["config"])
        x.setdefault("http_ping_ms",None)
        x.setdefault("is_remixed",False)
        x.setdefault("country","UN");x.setdefault("country_flag","🌐")
    OUTPUT_DIR.mkdir(exist_ok=True)
    groups={p:[] for p in ["vless","vmess","trojan","ss","hysteria2"]}
    for x in all_items:
        groups.setdefault(x["protocol"],[]).append(x["config"])
    for p,lines in groups.items():
        (OUTPUT_DIR/f"{p}.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    (OUTPUT_DIR/"all.txt").write_text("\n".join(x["config"] for x in all_items)+"\n",encoding="utf-8")
    avg=round(sum(x["tcp_ping_ms"] for x in items if x.get("tcp_ping_ms") is not None)/max(1,sum(1 for x in items if x.get("tcp_ping_ms") is not None)))
    data={"updated_at":datetime.now(timezone.utc).isoformat(),"stats":{"total":len(all_items),"alive":len(items),"remixed":len(remixed),"avg_ping":avg},"sources":{"total":6,"active":6,"dead_removed":0},"configs":all_items}
    (ROOT/"data/configs.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    return data

if __name__=="__main__":
    good=json.load(open(ROOT/"data/validated.json",encoding="utf-8")) if (ROOT/"data/validated.json").exists() else []
    rem=json.load(open(ROOT/"data/remixed.json",encoding="utf-8")) if (ROOT/"data/remixed.json").exists() else []
    publish(good,rem)
