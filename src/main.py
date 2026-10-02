import asyncio
from .health_monitor import init_db
from .finder import collect
from .validator import validate
from .remixer import build
from .publisher import publish
from pathlib import Path
import json

async def run():
    init_db()
    raw=await collect()
    Path("data/raw_configs.json").write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding="utf-8")
    validated=[x for x in await validate(raw) if x.get("alive")]
    # استخراج پروتکل از URL
    for x in validated:
        x["protocol"]=x["config"].split("://",1)[0].lower()
    Path("data/validated.json").write_text(json.dumps(validated,ensure_ascii=False,indent=2),encoding="utf-8")
    base,remixed=build(validated)
    Path("data/remixed.json").write_text(json.dumps(remixed,ensure_ascii=False,indent=2),encoding="utf-8")
    publish(base,remixed)
    print(f"Xfinder complete: {len(base)} alive, {len(remixed)} remixed")

if __name__=="__main__":
    asyncio.run(run())
