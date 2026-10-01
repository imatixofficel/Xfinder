"""پایش سلامت منابع در SQLite."""
import os,sqlite3,datetime,json,re,requests
from .config import DB_PATH, URL_SOURCES, TELEGRAM_CHANNELS

SCHEMA="""CREATE TABLE IF NOT EXISTS sources(
id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE,url TEXT,kind TEXT,
last_success TEXT,last_failure TEXT,fail_count INTEGER DEFAULT 0,last_seen TEXT,active INTEGER DEFAULT 1)"""

def db():
    c=sqlite3.connect(DB_PATH);c.execute(SCHEMA);c.commit();return c

def upsert(c,name,url,kind):
    c.execute("INSERT OR IGNORE INTO sources(name,url,kind) VALUES(?,?,?)",(name,url,kind))

def github_archived(url):
    m=re.search(r"github\.com/([^/]+)/([^/]+)",url)
    if not m:return False
    try:
        r=requests.get(f"https://api.github.com/repos/{m.group(1)}/{m.group(2)}",headers={"Accept":"application/vnd.github+json"},timeout=10)
        return bool(r.ok and r.json().get("archived"))
    except Exception:return False

def monitor():
    c=db()
    for s in URL_SOURCES: upsert(c,s["name"],s["url"],"url")
    for ch in TELEGRAM_CHANNELS: upsert(c,f"telegram:{ch}",f"https://t.me/s/{ch}","telegram")
    # پاکسازی بر اساس سیاست زمانی؛ نتیجه فقط منبع را inactive می‌کند.
    now=datetime.datetime.now(datetime.timezone.utc)
    rows=c.execute("SELECT name,url,fail_count,last_success,last_seen,active FROM sources").fetchall()
    for name,url,fails,last_success,last_seen,active in rows:
        remove=False
        if fails>=2: remove=True
        if last_success:
            dt=datetime.datetime.fromisoformat(last_success)
            if (now-dt).days>=30: remove=True
        if last_seen:
            dt=datetime.datetime.fromisoformat(last_seen)
            if (now-dt).days>=548: remove=True
        if github_archived(url): remove=True
        if remove:c.execute("UPDATE sources SET active=0 WHERE name=?",(name,))
    c.commit();c.close()
    return True

if __name__=="__main__": monitor()
