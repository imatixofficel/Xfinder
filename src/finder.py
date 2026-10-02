import asyncio, base64, json, re
from urllib.request import Request, urlopen
from .config import SOURCES, BLACKLIST

PATTERN=re.compile(r"(vless://\S+|vmess://\S+|trojan://\S+|ss://\S+|hysteria2://\S+)",re.I)

def fetch(url, timeout=15):
    req=Request(url,headers={"User-Agent":"Xfinder/1.0"})
    with urlopen(req,timeout=timeout) as r: return r.read().decode("utf-8","ignore")

def extract(text):
    text=text.strip()
    # بعضی subscriptionها Base64 هستند.
    candidates=[text]
    compact="".join(text.split())
    if len(compact)>32:
        try:
            candidates.append(base64.b64decode(compact+"===" ).decode("utf-8","ignore"))
        except Exception: pass
    found=[]
    for body in candidates:
        found.extend(PATTERN.findall(body))
    # حذف تکراری و بلک‌لیست بر اساس نام منبع
    return list(dict.fromkeys(found))

async def collect():
    loop=asyncio.get_running_loop()
    out=[]
    for src in SOURCES:
        if any(b.lower() in src["name"].lower() for b in BLACKLIST): continue
        try:
            text=await loop.run_in_executor(None,fetch,src["url"])
            for cfg in extract(text): out.append({"config":cfg,"source":src["name"],"trust_score":src["trust"]})
        except Exception as e:
            print("source failed:",src["name"],e)
    return out

if __name__=="__main__":
    data=asyncio.run(collect())
    json.dump(data,open("data/raw_configs.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print("collected",len(data))
