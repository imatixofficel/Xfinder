import asyncio, socket, time, re
from urllib.parse import urlparse
from .config import CONCURRENCY,TCP_TIMEOUT

def endpoint(cfg):
    # استخراج endpoint عمومی بدون تلاش برای decode کردن credentials.
    m=re.search(r"@([^/?#]+)",cfg)
    hostport=m.group(1) if m else ""
    if not hostport:
        u=urlparse(cfg); hostport=u.netloc
    hostport=hostport.split("?")[0]
    if ":" in hostport and not hostport.startswith("["):
        host,port=hostport.rsplit(":",1)
    else: host,port=hostport,("443")
    try: port=int(port)
    except ValueError: port=443
    return host.strip("[]"),port

async def tcp_probe(item,sem):
    async with sem:
        host,port=endpoint(item["config"])
        start=time.perf_counter()
        try:
            fut=asyncio.open_connection(host,port)
            reader,writer=await asyncio.wait_for(fut,timeout=TCP_TIMEOUT)
            ms=round((time.perf_counter()-start)*1000,1)
            writer.close()
            try: await writer.wait_closed()
            except Exception: pass
            item.update({"server":host,"port":port,"tcp_ping_ms":ms,"alive":True})
        except Exception:
            item.update({"server":host,"port":port,"tcp_ping_ms":None,"alive":False})
        return item

async def validate(items):
    sem=asyncio.Semaphore(CONCURRENCY)
    return await asyncio.gather(*(tcp_probe(x,sem) for x in items))

if __name__=="__main__":
    import json
    raw=json.load(open("data/raw_configs.json",encoding="utf-8"))
    good=[x for x in asyncio.run(validate(raw)) if x["alive"]]
    json.dump(good,open("data/validated.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print("alive:",len(good))
