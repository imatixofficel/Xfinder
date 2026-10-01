"""ریمیکس آزمایشی: جایگزینی endpoint با IP عمومی و حفظ اطلاعات TLS/SNI تا حد امکان."""
import ipaddress,json,urllib.parse
import requests
from .config import DATA_DIR, REMIX_PING_MAX

def load_clean_ips():
    url="https://raw.githubusercontent.com/imatixofficel/Scanner-matix/main/data/clean_ips.json"
    try:
        r=requests.get(url,timeout=20);r.raise_for_status();data=r.json()
        if isinstance(data,dict):
            for k in ("ips","data","clean_ips"):
                if isinstance(data.get(k),list): data=data[k];break
        return [str(x) for x in data if isinstance(x,str)][:1000]
    except Exception:
        return []

def remix_uri(uri, new_ip):
    try:
        scheme=uri.split("://",1)[0].lower()
        if scheme=="vmess":
            import base64
            raw=uri[8:];raw+="="*((4-len(raw)%4)%4)
            obj=json.loads(base64.urlsafe_b64decode(raw).decode())
            obj["add"]=new_ip
            enc=base64.urlsafe_b64encode(json.dumps(obj,separators=(",",":")).encode()).decode().rstrip("=")
            return "vmess://"+enc
        u=urllib.parse.urlsplit(uri)
        host=u.hostname
        if not host:return None
        # حفظ query شامل sni/host؛ فقط hostname اصلی را عوض می‌کنیم.
        netloc=new_ip
        if u.port: netloc += f":{u.port}"
        return urllib.parse.urlunsplit((u.scheme,netloc,u.path,u.query,u.fragment))
    except Exception:
        return None

def remix():
    src=DATA_DIR/"validated.json"
    items=json.loads(src.read_text(encoding="utf-8")) if src.exists() else []
    ips=load_clean_ips()
    if not ips:return []
    out=[]
    # سه نسخه برای هر مورد؛ برای جلوگیری از انفجار داده سقف 3000 مورد.
    for item in items:
        if item.get("ping_ms",999999)>REMIX_PING_MAX or item.get("protocol") not in {"vless","vmess","trojan"}:continue
        for idx,ip in enumerate(ips[:3],1):
            try: ipaddress.ip_address(ip)
            except ValueError: continue
            c=remix_uri(item["config"],ip)
            if c: out.append({**item,"config":c,"server":ip,"is_remixed":True,"remix_variant":idx})
        if len(out)>=3000:break
    (DATA_DIR/"remixed.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Remixed candidates: {len(out)}")
    return out

if __name__=="__main__": remix()
