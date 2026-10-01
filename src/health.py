"""ثبت سلامت منبع‌ها با SQLite."""
import sqlite3
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat()

class SourceHealth:
    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS source_health (
                    name TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    failures INTEGER NOT NULL DEFAULT 0,
                    last_attempt TEXT,
                    last_success TEXT,
                    last_error TEXT,
                    active INTEGER NOT NULL DEFAULT 1
                )
            """)

    def record(self, name, url, success, error=""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO source_health(name,url,failures,last_attempt,last_success,last_error,active)
                VALUES(?,?,?, ?,?,?,?)
                ON CONFLICT(name) DO UPDATE SET
                    url=excluded.url,
                    failures=CASE WHEN ? THEN 0 ELSE source_health.failures + 1 END,
                    last_attempt=excluded.last_attempt,
                    last_success=CASE WHEN ? THEN excluded.last_success ELSE source_health.last_success END,
                    last_error=excluded.last_error,
                    active=CASE WHEN ? THEN 1 ELSE source_health.active END
            """, (
                name, url, 0 if success else 1, now_iso(),
                now_iso() if success else None, error[:500], 1 if success else 0,
                1 if success else 0, 1 if success else 0, 1 if success else 0
            ))

    def summary(self):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT name,url,failures,last_attempt,last_success,last_error,active FROM source_health ORDER BY name"
            ).fetchall()
        keys = ["name","url","failures","last_attempt","last_success","last_error","active"]
        return [dict(zip(keys, row)) for row in rows]
