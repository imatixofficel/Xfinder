"""جمع‌آوری و استخراج URIهای عمومی."""
import base64, json, re, sys
from pathlib import Path
import requests
from .config import URL_SOURCES, TELEGRAM_CHANNELS, DATA_DIR, MAX_PER_SOURCE

URI_RE = re.compile(r"(?:vless|vmess|trojan|ss|hysteria2)://[^\s<>'\"`]+", re.I)
HEADERS = {"User-Agent":"Xfinder/1.0 public-feed-collector"}

def decode_b64(text):
    text=text.strip()
    text += "="*((4-len(text)%4)%4)
    try:return base64.urlsafe_b64decode(text).decode("utf-8","ignore")
    except Exception:return ""

def extract(text):
    out=[]
    for raw in URI_RE.findall(text or ""):
        raw=raw.rstrip("),.;")
        if raw.lower().startswith("vmess://"):
            decoded=decode_b64(raw[8:])
            if decoded:
                try:
                    obj=json.loads(decoded)
                    # تبدیل حداقلی به URI؛ پارسر کامل‌تر در publisher انجام می‌شود.
                    add={"v":"2","ps":obj.get("ps",""),"add":obj.get("add",""),
                         "port":str(obj.get("port","")),"id":obj.get("id",""),
                         "aid":str(obj.get("aid","0")),"net":obj.get("net","tcp"),
                         "type":obj.get("type","none"),"host":obj.get("host",""),
                         "path":obj.get("path",""),"tls":obj.get("tls","")}
                    enc=base64.urlsafe_b64encode(json.dumps(add,separators=(",",":")).encode()).decode().rstrip("=")
                    out.append("vmess://"+enc)
                    continue
                except Exception: pass
        out.append(raw)
    return list(dict.fromkeys(out))[:MAX_PER_SOURCE]

def fetch_url(url):
    r=requests.get(url,headers=HEADERS,timeout=20)
    r.raise_for_status()
    return extract(r.text)

def fetch_telegram(channel):
    url=f"https://t.me/s/{channel}"
    r=requests.get(url,headers=HEADERS,timeout=20)
    r.raise_for_status()
    return extract(r.text)

def collect():
    records=[]
    for s in URL_SOURCES:
        try:
            for c in fetch_url(s["url"]):
                records.append({"config":c,"source":s["name"],"source_url":s["url"]})
        except Exception as e:
            print(f"[WARN] {s['url']}: {e}",file=sys.stderr)
    for ch in TELEGRAM_CHANNELS:
        try:
            for c in fetch_telegram(ch):
                records.append({"config":c,"source":f"telegram:{ch}","source_url":f"https://t.me/s/{ch}"})
        except Exception as e:
            print(f"[WARN] telegram {ch}: {e}",file=sys.stderr)
    dedup={}
    for r in records: dedup[r["config"]]=r
    out=list(dedup.values())
    (DATA_DIR/"collected.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Collected {len(out)} unique configs")
    return out

if __name__=="__main__":
    collect()
