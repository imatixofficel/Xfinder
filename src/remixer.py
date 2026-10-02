"""ساخت نسخه‌های Remix با IPهای تمیز؛ پارامترهای TLS/SNI/Host حفظ می‌شوند."""
import base64,json,re
from urllib.request import Request,urlopen
from .config import CLEAN_IPS_URL,MAX_REMIX_PING,REMIX_PER_CONFIG

def fetch_clean():
    try:
        req=Request(CLEAN_IPS_URL,headers={"User-Agent":"Xfinder/1.1"})
        raw=urlopen(req,timeout=15).read().decode("utf-8","ignore")
        data=json.loads(raw)
        if isinstance(data,dict):data=data.get("ips") or data.get("data") or data.get("results") or []
        out=[]
        for x in data:
            if isinstance(x,str):out.append({"ip":x,"ping":0})
            elif isinstance(x,dict):out.append({"ip":x.get("ip") or x.get("address"),"ping":x.get("ping",x.get("ping_ms",999))})
        return [x for x in out if x["ip"] and float(x["ping"] or 999)<=MAX_REMIX_PING]
    except Exception as e:
        print("clean ip source failed:",e);return []

def remix_config(cfg,new_ip):
    proto=cfg.split("://",1)[0].lower()
    if proto=="vmess":
        try:
            raw=cfg.split("://",1)[1].split("#",1)[0];raw += "="*((4-len(raw)%4)%4)
            obj=json.loads(base64.b64decode(raw).decode("utf-8","ignore"));obj["add"]=new_ip
            label=cfg.split("#",1)[1] if "#" in cfg else "Xfinder-remix"
            body=base64.b64encode(json.dumps(obj,separators=(",",":"),ensure_ascii=False).encode()).decode().rstrip("=")
            return "vmess://"+body+"#"+label
        except Exception:pass
    return re.sub(r"(?<=@)(?:\[[^\]]+\]|[^:/?#]+)",new_ip,cfg,count=1)

def build(items):
    ips=fetch_clean()
    if not ips:return items,[]
    remixed=[]
    for item in items:
        if item.get("protocol") not in {"vless","vmess","trojan"}:continue
        for clean in ips[:REMIX_PER_CONFIG]:
            r=dict(item);r["config"]=remix_config(item["config"],clean["ip"]);r["server"]=clean["ip"];r["is_remixed"]=True
            r["remix_ping_ms"]=clean["ping"];remixed.append(r)
    return items,remixed

if __name__=="__main__":
    import json
    data=json.load(open("data/validated.json",encoding="utf-8"));_,r=build(data)
    json.dump(r,open("data/remixed.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print("remixed:",len(r))
