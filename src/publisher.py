"""ساخت JSON و خروجی‌های متنی."""
import json,datetime,urllib.parse,base64
from pathlib import Path
from .config import DATA_DIR,OUTPUT_DIR

def country_guess(host):
    # تشخیص کشور از IP با سرویس عمومی؛ خطا = --
    try:
        import requests
        r=requests.get(f"https://ipapi.co/{host}/json/",timeout=3)
        if r.ok:
            j=r.json(); code=j.get("country_code","--")
            flags={"US":"🇺🇸","DE":"🇩🇪","NL":"🇳🇱","FR":"🇫🇷","GB":"🇬🇧","FI":"🇫🇮","IR":"🇮🇷","TR":"🇹🇷","RU":"🇷🇺"}
            return code,flags.get(code,"🌐")
    except Exception:pass
    return "--","🌐"

def enrich(items):
    out=[]
    for x in items:
        x=dict(x); host=x.get("server","")
        cc,flag=country_guess(host) if host else ("--","🌐")
        x["country"],x["country_flag"]=cc,flag
        x.setdefault("is_remixed",False)
        out.append(x)
    return out

def publish():
    valid=json.loads((DATA_DIR/"validated.json").read_text()) if (DATA_DIR/"validated.json").exists() else []
    rem=json.loads((DATA_DIR/"remixed.json").read_text()) if (DATA_DIR/"remixed.json").exists() else []
    configs=enrich(valid)
    # برای پنل، ریمیکس‌ها نیز در فهرست دیده می‌شوند.
    all_items=configs+enrich(rem)
    OUTPUT_DIR.mkdir(exist_ok=True)
    groups={k:[] for k in ("vless","vmess","trojan","ss","hysteria2")}
    for x in all_items:
        if x.get("protocol") in groups: groups[x["protocol"]].append(x["config"])
    for k,v in groups.items():
        (OUTPUT_DIR/f"{k}.txt").write_text("\n".join(dict.fromkeys(v))+"\n",encoding="utf-8")
    (OUTPUT_DIR/"all.txt").write_text("\n".join(dict.fromkeys(x["config"] for x in all_items))+"\n",encoding="utf-8")
    remdir=OUTPUT_DIR/"remixed";remdir.mkdir(exist_ok=True)
    (remdir/"all.txt").write_text("\n".join(dict.fromkeys(x["config"] for x in rem))+"\n",encoding="utf-8")

    pings=[x["ping_ms"] for x in configs if x.get("ping_ms") is not None]
    data={
      "updated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "stats":{"total":len(all_items),"alive":len(configs),"remixed":len(rem),"avg_ping":round(sum(pings)/len(pings)) if pings else 0},
      "sources":{"total":0,"active":0,"dead_removed":0},
      "source_list":[],
      "configs":all_items
    }
    # وضعیت منابع از SQLite
    try:
        import sqlite3
        from .config import DB_PATH
        c=sqlite3.connect(DB_PATH)
        rows=c.execute("SELECT name,url,active FROM sources").fetchall()
        data["sources"]={"total":len(rows),"active":sum(r[2] for r in rows),"dead_removed":sum(1 for r in rows if not r[2])}
        data["source_list"]=[{"name":r[0],"url":r[1],"active":bool(r[2])} for r in rows]
        c.close()
    except Exception:pass
    (DATA_DIR/"configs.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    return data

if __name__=="__main__": publish()
