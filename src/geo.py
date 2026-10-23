"""GeoIP: کشور هر کانفیگ (بدون وابستگی خارجی).

دیتابیس: DB-IP «Country Lite» (فرمت MMDB، رایگان؛ سازگار با GeoLite2). فایل به‌صورت خودکار دانلود و کش می‌شود؛
با GEO_DB_PATH می‌شود فایل MMDB دلخواه (مثلاً GeoLite2-Country.mmdb) داد، با GEO_DB_URL آدرس دانلود را عوض کرد.
اگر دیتابیس در دسترس نباشد، کانفیگ‌ها بدون کشور منتشر می‌شوند (هیچ‌چیز خراب نمی‌شود).
"""
import gzip, ipaddress, os, socket, struct, time
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from .config import ROOT

MARKER = b"\xab\xcd\xefMaxMind.com"


class MMDBReader:
    """خواننده‌ی حداقلی MMDB (درخت جست‌وجو + decoder)."""

    def __init__(self, data):
        self.buf = data
        i = data.rfind(MARKER)
        if i < 0:
            raise ValueError("not an MMDB file")
        self.meta, _ = self._decode(i + len(MARKER), i + len(MARKER))
        self.node_count = self.meta["node_count"]
        self.record_size = self.meta["record_size"]
        self.ip_version = self.meta["ip_version"]
        self.node_bytes = self.record_size * 2 // 8
        self.tree_size = self.node_count * self.node_bytes
        self.data_start = self.tree_size + 16
        self._v4_root = None

    # --- decoder ---
    def _decode(self, off, base):
        buf = self.buf
        ctrl = buf[off]; off += 1
        typ = ctrl >> 5
        if typ == 1:                                   # pointer
            ss = (ctrl >> 3) & 3; vvv = ctrl & 7
            if ss == 0:
                p = (vvv << 8) | buf[off]; off += 1
            elif ss == 1:
                p = ((vvv << 16) | int.from_bytes(buf[off:off + 2], "big")) + 2048; off += 2
            elif ss == 2:
                p = ((vvv << 24) | int.from_bytes(buf[off:off + 3], "big")) + 526336; off += 3
            else:
                p = int.from_bytes(buf[off:off + 4], "big"); off += 4
            val, _ = self._decode(base + p, base)
            return val, off
        if typ == 0:
            typ = 7 + buf[off]; off += 1
        size = ctrl & 31
        if size == 29:
            size = 29 + buf[off]; off += 1
        elif size == 30:
            size = 285 + int.from_bytes(buf[off:off + 2], "big"); off += 2
        elif size == 31:
            size = 65821 + int.from_bytes(buf[off:off + 3], "big"); off += 3
        if typ == 2:
            return buf[off:off + size].decode("utf-8", "replace"), off + size
        if typ == 3:
            return struct.unpack(">d", buf[off:off + 8])[0], off + 8
        if typ == 15:
            return struct.unpack(">f", buf[off:off + 4])[0], off + 4
        if typ in (5, 6, 8, 9, 10):
            v = int.from_bytes(buf[off:off + size], "big")
            if typ == 8 and size == 4 and v >= 2 ** 31:
                v -= 2 ** 32
            return v, off + size
        if typ == 7:
            d = {}
            for _ in range(size):
                k, off = self._decode(off, base)
                v, off = self._decode(off, base)
                d[k] = v
            return d, off
        if typ == 11:
            arr = []
            for _ in range(size):
                v, off = self._decode(off, base)
                arr.append(v)
            return arr, off
        if typ == 14:
            return bool(size), off
        if typ == 4:
            return bytes(buf[off:off + size]), off + size
        return None, off + size

    # --- search tree ---
    def _record(self, node, bit):
        o = node * self.node_bytes
        b = self.buf
        rs = self.record_size
        if rs == 24:
            return int.from_bytes(b[o + 3 * bit:o + 3 * bit + 3], "big")
        if rs == 28:
            if bit == 0:
                return ((b[o + 3] >> 4) << 24) | int.from_bytes(b[o:o + 3], "big")
            return ((b[o + 3] & 0x0F) << 24) | int.from_bytes(b[o + 4:o + 7], "big")
        return int.from_bytes(b[o + 4 * bit:o + 4 * bit + 4], "big")

    def get(self, ip):
        addr = ipaddress.ip_address(ip)
        bits = 32 if addr.version == 4 else 128
        if addr.version == 6 and self.ip_version == 4:
            return None
        node = 0
        if addr.version == 4 and self.ip_version == 6:   # ::/96 (IPv4 در IPv6)
            if self._v4_root is None:
                n = 0
                for _ in range(96):
                    if n >= self.node_count:
                        break
                    n = self._record(n, 0)
                self._v4_root = n
            node = self._v4_root
        num = int(addr)
        for i in range(bits):
            if node >= self.node_count:
                break
            node = self._record(node, (num >> (bits - 1 - i)) & 1)
        if node == self.node_count:
            return None
        if node < self.node_count:
            return None
        off = self.tree_size + node - self.node_count
        val, _ = self._decode(off, self.data_start)
        return val


def flag(code):
    """پرچم ایموجی از کد دو حرفی کشور؛ برای ورودی نامعتبر رشته‌ی خالی."""
    c = (code or "").strip().upper()
    if len(c) != 2 or not c.isalpha() or not c.isascii():
        return ""
    return "".join(chr(0x1F1E6 + ord(ch) - 65) for ch in c)


def country_from_record(rec):
    """(code, name) از رکورد MMDB؛ در نبود داده (None, None)."""
    if not isinstance(rec, dict):
        return None, None
    c = rec.get("country") or rec.get("registered_country") or {}
    code = c.get("iso_code")
    if not code:
        return None, None
    names = c.get("names") or {}
    return code.upper(), names.get("en") or code.upper()


def _log(*a):
    print("geo:", *a, flush=True)


def _download(url, dest):
    req = Request(url, headers={"User-Agent": "Xfinder/3 (+GitHub Actions)"})
    with urlopen(req, timeout=40) as r:
        raw = r.read(60_000_000)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    tmp.write_bytes(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    tmp.replace(dest)


def load_db():
    """MMDBReader یا None (دانلود خودکار DB-IP Country Lite در صورت نبودن فایل)."""
    path = os.getenv("GEO_DB_PATH")
    path = Path(path) if path else ROOT / "geo_cache" / "dbip-country-lite.mmdb"
    try:
        if not path.exists() and os.getenv("GEO_DISABLE") == "1":
            return None
        if not path.exists():
            urls = [os.environ["GEO_DB_URL"]] if os.getenv("GEO_DB_URL") else []
            if not urls:
                now = datetime.now(timezone.utc)
                prev = (now.replace(day=1) - timedelta(days=1))
                urls = [f"https://download.db-ip.com/free/dbip-country-lite-{d:%Y-%m}.mmdb.gz" for d in (now, prev)]
            for u in urls:
                try:
                    _download(u, path)
                    break
                except Exception as e:
                    _log("download failed:", u, e)
        if path.exists():
            return MMDBReader(path.read_bytes())
    except Exception as e:
        _log("database unavailable:", e)
    return None


def _is_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _resolve(host):
    try:
        return socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
    except Exception:
        try:
            return socket.getaddrinfo(host, None)[0][4][0]
        except Exception:
            return None


def annotate(items, db=None, resolver=_resolve, timeout=25):
    """country / country_code / country_flag را روی هر آیتم می‌گذارد. بدون دیتابیس چیزی عوض نمی‌شود."""
    db = db if db is not None else load_db()
    if db is None:
        _log("no GeoIP database; skipping country labels")
        return 0
    hosts = {str(x.get("server") or "").strip("[]") for x in items}
    hosts.discard("")
    ips = {h: h for h in hosts if _is_ip(h)}
    todo = [h for h in hosts if h not in ips]
    if todo:
        ex = ThreadPoolExecutor(max_workers=48)
        futs = {ex.submit(resolver, h): h for h in todo}
        done, _ = wait(futs, timeout=timeout)
        for f in done:
            try:
                ip = f.result()
            except Exception:
                ip = None
            if ip:
                ips[futs[f]] = ip
        ex.shutdown(wait=False, cancel_futures=True)
    cache, n = {}, 0
    for x in items:
        host = str(x.get("server") or "").strip("[]")
        ip = ips.get(host)
        if not ip:
            continue
        if ip not in cache:
            try:
                cache[ip] = country_from_record(db.get(ip))
            except Exception:
                cache[ip] = (None, None)
        code, name = cache[ip]
        if code:
            x.update({"country": name, "country_code": code, "country_flag": flag(code)})
            n += 1
    _log(f"{n}/{len(items)} configs labelled")
    return n
