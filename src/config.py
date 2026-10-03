import os
from pathlib import Path

ROOT = Path(os.getenv("XFINDER_ROOT") or Path(__file__).resolve().parents[1])
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DB_PATH = ROOT / "sources.db"


def _env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return float(default)


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return int(default)


# --- Time / size budgets (the pipeline must ALWAYS finish and publish) ---
PIPELINE_BUDGET = _env_float("PIPELINE_BUDGET", 520)   # seconds for the whole run
MAX_PER_SOURCE = _env_int("MAX_PER_SOURCE", 2000)      # random sample per source
MAX_TCP_CANDIDATES = _env_int("MAX_TCP_CANDIDATES", 20000)
MAX_XRAY_CANDIDATES = _env_int("MAX_XRAY_CANDIDATES", 1600)
MAX_PER_ENDPOINT = 3                                   # same host:port variants

CONCURRENCY = 800
TCP_TIMEOUT = 3.0
HTTP_TIMEOUT = 8.0
MIN_TRUST = 60
MAX_REMIX_PING = 70
REMIX_PER_CONFIG = 2

SOURCES = [
    {"name":"Au1rxx/free-vpn-subscriptions","url":"https://github.com/Au1rxx/free-vpn-subscriptions/raw/main/output/v2ray-base64.txt","trust":100,"has_http_test":True},
    {"name":"barry-far/V2ray-Config","url":"https://raw.githubusercontent.com/barry-far/V2ray-Config/main/All_Configs_Sub.txt","trust":92,"has_http_test":False},
    {"name":"soroushmirzaei/telegram-configs-collector","url":"https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed","trust":90,"has_http_test":False},
    {"name":"Delta-Kronecker/V2ray-Config","url":"https://github.com/Delta-Kronecker/V2ray-Config/raw/refs/heads/main/config/farg/all_configs.json","trust":90,"has_http_test":False},
    {"name":"mahdibland/V2RayAggregator","url":"https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge_base64.txt","trust":88,"has_http_test":False},
    {"name":"Epodonios/v2ray-configs","url":"https://github.com/Epodonios/v2ray-configs/raw/main/All_Configs_Sub.txt","trust":85,"has_http_test":False},
    {"name":"MatinGhanbari/v2ray-configs","url":"https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/super-sub.txt","trust":85,"has_http_test":False},
    {"name":"ebrasha/free-v2ray-public-list","url":"https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/V2Ray-Config-By-EbraSha.txt","trust":84,"has_http_test":False},
    {"name":"R3ZARAHIMI/tg-v2ray-configs-every2h","url":"https://raw.githubusercontent.com/R3ZARAHIMI/tg-v2ray-configs-every2h/main/all.txt","trust":80,"has_http_test":False},
    # --- منابع اضافه‌شده (هر منبعی که از دسترس خارج شود خودکار نادیده گرفته می‌شود) ---
    {"name":"yebekhe/TelegramV2rayCollector","url":"https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix","trust":82,"has_http_test":False},
    {"name":"Pawdroid/Free-servers","url":"https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub","trust":78,"has_http_test":False},
    {"name":"ermaozi/get_subscribe","url":"https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt","trust":76,"has_http_test":False},
    {"name":"mfuu/v2ray","url":"https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray","trust":75,"has_http_test":False},
    {"name":"Danialsamadi/v2go","url":"https://raw.githubusercontent.com/Danialsamadi/v2go/main/AllConfigsSub.txt","trust":75,"has_http_test":False},
    {"name":"MahsaNetConfigTopic/config","url":"https://raw.githubusercontent.com/MahsaNetConfigTopic/config/main/xray_final.txt","trust":74,"has_http_test":False},
    {"name":"10ium/V2Hub3","url":"https://raw.githubusercontent.com/10ium/V2Hub3/main/merged_base64","trust":72,"has_http_test":False},
    {"name":"Leon406/SubCrawler","url":"https://raw.githubusercontent.com/Leon406/SubCrawler/master/sub/share/v2","trust":70,"has_http_test":False},
    {"name":"Xfinder (self)","url":"https://imatixofficel.github.io/Xfinder/output/all.txt","trust":70,"has_http_test":True},
]
CLEAN_IPS_URL = "https://raw.githubusercontent.com/imatixofficel/Scanner-matix/main/data/clean_ips.json"
BLACKLIST = {"v2ray_configs_pool","nim_vpn_ir","outline_vpn","hope_net","proxystore11","yaney_01","fnet00","ShadowProxy66","zibanabz"}

# --- سرعت و حجم خروجی ---
MAX_PUBLISH_BASE = 1000      # فقط سریع‌ترین کانفیگ‌های اصلی منتشر می‌شوند تا سایت سنگین نشود
REMIX_BASE_LIMIT = 400       # فقط بهترین کانفیگ‌ها با IP تمیز ترکیب می‌شوند
# --- WireGuard (Cloudflare WARP) ---
WG_ACCOUNTS = 3              # تعداد حساب WARP که نگه‌داری می‌شود
WG_ENDPOINTS_PER_ACCOUNT = 6 # هر حساب با چند IP تمیز ساخته می‌شود
WG_PORT = 2408
WARP_ACCOUNTS_FILE = DATA_DIR / "warp_accounts.json"

# --- اهدای کانفیگ / ۲۴ ساعته ---
DONATIONS_DIR = ROOT / "donations"
DONATION_TTL_HOURS = 24
MAX_DONATION_CONFIGS = 3
MAX_DONATION_AD = 200
# --- اشتراک ۲۰ کانفیگ برتر ---
TOP_N = 20
# --- اسکن خودکار GitHub برای پیدا کردن منبع جدید ---
DISCOVER_SOURCES = os.getenv("DISCOVER_SOURCES", "1") != "0"
DISCOVER_MAX_REPOS = _env_int("DISCOVER_MAX_REPOS", 8)
BRAND = "Xfinder"

# --- WireGuard از منابع (تست واقعی با Xray) ---
MAX_WG_CANDIDATES = _env_int("MAX_WG_CANDIDATES", 96)
EXTRA_SOURCES_FILE = ROOT / "sources_extra.txt"   # هر خط: URL  یا  name|URL  (برای افزودن منبع دلخواه)


def _load_extra_sources():
    out = []
    try:
        for ln in EXTRA_SOURCES_FILE.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            name, url = (ln.split("|", 1) + [""])[:2] if "|" in ln else ("", ln)
            if "|" in ln:
                name, url = ln.split("|", 1)
            url = url.strip()
            if url.startswith("https://"):
                parts = url.split("/")
                out.append({"name": name.strip() or (parts[3] + "/" + parts[4] if len(parts) > 4 else url),
                            "url": url, "trust": 65, "has_http_test": False})
    except OSError:
        pass
    return out


# منبع WireGuard (تأییدشده: خروجی خام، فرمت wireguard://کلید@IP:پورت). چند URL با ویرگول از env هم می‌شود.
DEFAULT_WG_SOURCES = "https://raw.githubusercontent.com/wiki/gfpcom/free-proxy-list/lists/wireguard.txt"


def _wg_env_sources():
    out = []
    for url in os.getenv("WG_SOURCE_URLS", DEFAULT_WG_SOURCES).split(","):
        url = url.strip()
        if url.startswith("https://"):
            parts = url.split("/")
            out.append({"name": "WG: " + (parts[4] + "/" + parts[5] if "wiki" in parts and len(parts) > 6 else "/".join(parts[3:5])),
                        "url": url, "trust": 70, "has_http_test": False})
    return out


SOURCES += _load_extra_sources() + _wg_env_sources()
