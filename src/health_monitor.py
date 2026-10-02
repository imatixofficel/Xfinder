import sqlite3
from datetime import datetime, timezone
from .config import DB_PATH, SOURCES, BLACKLIST

def init_db():
    con=sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS sources(
      name TEXT PRIMARY KEY,url TEXT,trust REAL DEFAULT 0,last_ok TEXT,
      consecutive_failures INTEGER DEFAULT 0,config_count INTEGER DEFAULT 0,
      success_rate REAL DEFAULT 0,avg_ping REAL DEFAULT 0,disabled INTEGER DEFAULT 0)""")
    for s in SOURCES:
        if s["name"] not in BLACKLIST:
            con.execute("INSERT OR IGNORE INTO sources(name,url) VALUES(?,?)",(s["name"],s["url"]))
    con.commit();con.close()

def active_sources():
    init_db()
    con=sqlite3.connect(DB_PATH); rows=con.execute("SELECT name,url,trust,disabled FROM sources WHERE disabled=0").fetchall();con.close()
    return [{"name":r[0],"url":r[1],"trust":r[2],"disabled":r[3]} for r in rows]

if __name__=="__main__":
    init_db()
    print("health database ready")
