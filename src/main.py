"""نقطه شروع اجرای Xfinder."""
import asyncio
from .sources import SOURCES
from .collector import collect
from .validator import validate
from .health import SourceHealth
from .publisher import publish
from .settings import DB_PATH, OUTPUT_DIR

async def run():
    health = SourceHealth(DB_PATH)
    fetched = await collect(SOURCES)
    all_configs = []
    for name, result in fetched.items():
        success = not result["error"]
        health.record(name, result["url"], success, result["error"])
        all_configs.extend(result["configs"])
        print(f"[{'OK' if success else 'FAIL'}] {name}: {len(result['configs'])} config(s)" +
              (f" — {result['error']}" if result["error"] else ""))

    rows = await validate(all_configs)
    source_summary = health.summary()
    stats = publish(rows, source_summary, OUTPUT_DIR)
    print("\nXfinder update complete")
    print(f"Collected unique configs: {stats['total']}")
    print(f"Valid: {stats['valid']} | TCP reachable: {stats['alive']}")
    print(f"Output directory: {OUTPUT_DIR}/")

if __name__ == "__main__":
    asyncio.run(run())
