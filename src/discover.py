"""اسکن خودکار GitHub برای پیدا کردن منبع‌های تازه‌ی کانفیگ.
منابع پیدا‌شده trust پایین دارند و کانفیگ‌هایشان مثل بقیه با Xray واقعاً تست می‌شود.
هر خطایی (rate-limit، قطعی شبکه) فقط یعنی «منبع جدیدی اضافه نشد»."""
import json, os, re
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from .config import DISCOVER_SOURCES, DISCOVER_MAX_REPOS

API = "https://api.github.com"
NAME_OK = re.compile(r"(?i)(sub|config|v2ray|vless|vmess|trojan|mix|all|merge|proxy|node|xray)")
SKIP = re.compile(r"(?i)\.(md|json|yaml|yml|py|js|png|jpg|zip|html|css)$|readme|license|clash|sing-?box")


def _get(url):
    h = {"User-Agent": "Xfinder/2.5", "Accept": "application/vnd.github+json"}
    tok = os.getenv("GITHUB_TOKEN")
    if tok:
        h["Authorization"] = "Bearer " + tok
    return json.loads(urlopen(Request(url, headers=h), timeout=15).read().decode("utf-8", "ignore"))


def discover(known_names=()):
    if not DISCOVER_SOURCES:
        return []
    out = []
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%d")
        q = f"v2ray config in:name,description,topics pushed:>{since} stars:>10"
        repos = _get(f"{API}/search/repositories?q={q.replace(' ', '+')}&sort=updated&per_page={DISCOVER_MAX_REPOS * 2}")
        known = {n.lower() for n in known_names}
        for r in repos.get("items", [])[:DISCOVER_MAX_REPOS * 2]:
            full = r.get("full_name", "")
            if not full or any(full.lower() == k.split(" ")[0] for k in known) or r.get("fork") or r.get("archived"):
                continue
            try:
                files = _get(f"{API}/repos/{full}/contents/")
            except Exception:
                continue
            picked = 0
            for f in files if isinstance(files, list) else []:
                size = f.get("size") or 0
                if (f.get("type") == "file" and f.get("download_url") and NAME_OK.search(f["name"])
                        and not SKIP.search(f["name"]) and 2000 < size < 6_000_000 and picked < 2):
                    out.append({"name": f"{full}/{f['name']}", "url": f["download_url"], "trust": 60,
                                "has_http_test": False, "discovered": True})
                    picked += 1
            if len({o["name"].split("/")[0] + o["name"].split("/")[1] for o in out}) >= DISCOVER_MAX_REPOS:
                break
    except Exception as e:
        print("source discovery skipped:", e, flush=True)
    print(f"discovered {len(out)} extra source files", flush=True)
    return out
