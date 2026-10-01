"""تست TCP همزمان؛ این تست صرفاً دسترسی TCP را اندازه می‌گیرد."""
import asyncio, json, socket, time, urllib.parse
from .config import DATA_DIR, CONCURRENCY, TIMEOUT

def parse_endpoint(uri):
    try:
        scheme=uri.split("://",1)[0].lower()
        if scheme=="vmess":
            import base64
            raw=uri[8:]; raw += "="*((4-len(raw)%4)%4)
            obj=json.loads(base64.urlsafe_b64decode(raw).decode())
            return scheme,obj.get("add"),int(obj.get("port") or 0)
        u=urllib.parse.urlsplit(uri)
        host=u.hostname
        port=u.port
        return scheme,host,port
    except Exception:
        return "",None,None

async def probe(item, sem):
    scheme,host,port=parse_endpoint(item["config"])
    if not host or not port:return None
    async with sem:
        start=time.perf_counter()
        try:
            fut=asyncio.open_connection(host,port)
            reader,writer=await asyncio.wait_for(fut,timeout=TIMEOUT)
            ms=round((time.perf_counter()-start)*1000)
            writer.close()
            try: await writer.wait_closed()
            except Exception: pass
            item.update({"protocol":scheme,"server":host,"port":port,"ping_ms":ms})
            return item
        except Exception:return None

async def run(items):
    sem=asyncio.Semaphore(CONCURRENCY)
    results=await asyncio.gather(*(probe(x,sem) for x in items))
    return [x for x in results if x]

def validate():
    p=DATA_DIR/"collected.json"
    items=json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    alive=asyncio.run(run(items))
    (DATA_DIR/"validated.json").write_text(json.dumps(alive,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Alive TCP endpoints: {len(alive)}")
    return alive

if __name__=="__main__": validate()
