"""نام‌گذاری یکدست کانفیگ‌ها (Remark) بدون تغییر در مشخصات اتصال."""
import base64, json, re
from urllib.parse import quote, unquote


def _b64d(s):
    s = s.strip().replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * ((4 - len(s) % 4) % 4))


def original_name(cfg):
    """نام اصلی کانفیگ (remark) یا رشته‌ی خالی."""
    try:
        if cfg.lower().startswith("vmess://"):
            obj = json.loads(_b64d(cfg.split("://", 1)[1].split("#", 1)[0]).decode("utf-8", "ignore"))
            return str(obj.get("ps") or "")
        if "#" in cfg:
            return unquote(cfg.split("#", 1)[1])
    except Exception:
        pass
    return ""


def rename(cfg, label):
    """فقط نام نمایشی را عوض می‌کند؛ اگر ساختار نامعتبر بود کانفیگ دست‌نخورده برمی‌گردد."""
    try:
        if cfg.lower().startswith("vmess://"):
            body = cfg.split("://", 1)[1].split("#", 1)[0]
            text = _b64d(body).decode("utf-8")
            ps = json.dumps(label, ensure_ascii=False)
            # فقط مقدار "ps" جایگزین می‌شود؛ بقیه‌ی JSON بایت‌به‌بایت همان اصلی می‌ماند.
            new, n = re.subn(r'("ps"\s*:\s*)"(?:[^"\\]|\\.)*"', lambda m: m.group(1) + ps, text, count=1)
            ok = False
            if n:
                try:
                    ok = json.loads(new).get("ps") == label
                except Exception:
                    ok = False
            if not ok:
                obj = json.loads(text)
                obj["ps"] = label
                new = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
            return "vmess://" + base64.b64encode(new.encode("utf-8")).decode()
        return cfg.split("#", 1)[0] + "#" + quote(label, safe="")
    except Exception:
        return cfg


def make_label(proto, ping, index, remixed=False, brand="Xfinder"):
    p = {"ss": "SS", "hysteria2": "HY2", "wireguard": "WG"}.get(proto, (proto or "").upper())
    tag = f"{brand} ✦ {p}" if remixed else f"{brand} • {p}"
    ms = f" • {int(round(ping))}ms" if ping else ""
    return f"{tag}{ms} • {index:03d}"


import hashlib, re

# چند استیکر مختلف؛ برای هر کانفیگ ثابت (بر اساس هش) انتخاب می‌شود تا نام بین اجراها عوض نشود.
BRAND_EMOJIS = [
    # اینترنت و شبکه
    "🌐", "🌍", "🌎", "🌏", "📡", "📶", "🛰️", "🔗", "☁️", "🌩️", "📲", "💻", "🖥️", "🔌", "🧭",
    # امنیت و VPN
    "🔒", "🔐", "🔓", "🔑", "🗝️", "🛡️", "🔰", "🧱", "🥷", "🕵️", "👻", "🎭", "🚦",
    # سرعت
    "⚡", "🚀", "🛸", "🏎️", "💨", "🧬", "⚙️",
]


def pick_emoji(seed):
    h = int(hashlib.sha1(str(seed).encode("utf-8", "ignore")).hexdigest(), 16)
    return BRAND_EMOJIS[h % len(BRAND_EMOJIS)]


def fmt_speed(kbps):
    """KB/s -> «2.4MB/s» یا «850KB/s»."""
    if not kbps:
        return ""
    return f"{kbps / 1024:.1f}MB/s" if kbps >= 1024 else f"{int(round(kbps))}KB/s"


def _has_flag(text):
    t = (text or "").lstrip()
    return len(t) >= 2 and all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in t[:2])


def tagged_name(orig, proto, brand="Xfinder", seed="", flag="", ping=None, speed=None):
    """«🇩🇪 نام اصلی | Xfinder 🔐 | 120ms | 2.4MB/s».
    پرچم کشور (اگر داریم) اول می‌آید؛ پینگ و سرعت فقط وقتی اندازه‌گیری شده باشند.
    اگر کانفیگ نام نداشت: «🇩🇪 Xfinder 🔐 | VLESS | 120ms | 2.4MB/s»."""
    orig = (orig or "").strip()
    if re.search(r"\|\s*" + re.escape(brand) + r"\b", orig) or orig.startswith(brand + " "):
        return orig                        # تگ دوباره اضافه نشود
    tag = [f"{brand} {pick_emoji(seed or orig)}"]
    p = {"ss": "SS", "hysteria2": "HY2", "wireguard": "WG"}.get(proto, (proto or "").upper())
    if not orig and p:
        tag.append(p)
    if ping:
        tag.append(f"{int(round(ping))}ms")
    if speed:
        tag.append(fmt_speed(speed))
    prefix = f"{flag} " if flag and not _has_flag(orig) else ""
    tail = " | ".join(tag)
    return f"{prefix}{orig} | {tail}" if orig else f"{prefix}{tail}"
