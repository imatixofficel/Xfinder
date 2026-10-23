"""نام‌گذاری یکدست کانفیگ‌ها (Remark) بدون تغییر در مشخصات اتصال."""
import base64, json
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
            obj = json.loads(_b64d(body).decode("utf-8", "ignore"))
            obj["ps"] = label
            raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()
            return "vmess://" + base64.b64encode(raw).decode().rstrip("=")
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


def tagged_name(orig, proto, brand="Xfinder", seed=""):
    """نام اصلی کانفیگ + خط جداکننده + برند و استیکر: «OriginalName | Xfinder ⚡».
    اگر کانفیگ نام نداشت، با پروتکل نام‌گذاری می‌شود."""
    tag = f"{brand} {pick_emoji(seed or orig)}"
    orig = (orig or "").strip()
    if re.search(r"\|\s*" + re.escape(brand) + r"\b", orig) or orig.startswith(brand + " "):
        return orig                        # تگ دوباره اضافه نشود
    if not orig:
        p = {"ss": "SS", "hysteria2": "HY2", "wireguard": "WG"}.get(proto, (proto or "").upper())
        return f"{tag} | {p}" if p else tag
    return f"{orig} | {tag}"
