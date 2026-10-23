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
MAX_PER_SOURCE = _env_int("MAX_PER_SOURCE", 200000)    # عملاً بدون سقف: همه‌ی کانفیگ‌های هر منبع
MAX_TCP_CANDIDATES = _env_int("MAX_TCP_CANDIDATES", 200000)
MAX_XRAY_CANDIDATES = _env_int("MAX_XRAY_CANDIDATES", 50000)
MAX_PER_ENDPOINT = 3                                   # same host:port variants

CONCURRENCY = 800
TCP_TIMEOUT = 3.0
HTTP_TIMEOUT = 8.0
MIN_TRUST = 60
MAX_REMIX_PING = 70
REMIX_PER_CONFIG = 2
REMIX_ENABLED = False   # ترکیب با IP تمیز (Scanner-matix Remix) غیرفعال است؛ کانفیگ‌ها دست‌نخورده منتشر می‌شوند

# فقط منابع داخل sources_extra.txt استفاده می‌شوند (هیچ منبع پیش‌فرض/قدیمی وجود ندارد).
SOURCES = []
CLEAN_IPS_URL = "https://raw.githubusercontent.com/imatixofficel/Scanner-matix/main/data/clean_ips.json"
BLACKLIST = {"v2ray_configs_pool","nim_vpn_ir","outline_vpn","hope_net","proxystore11","yaney_01","fnet00","ShadowProxy66","zibanabz"}

# --- سرعت و حجم خروجی ---
MAX_HTTP_PING_MS = 2500     # کانفیگ‌های کندتر از این (تست واقعی HTTPS) حذف می‌شوند
MAX_PUBLISH_BASE = 2000      # فقط سریع‌ترین کانفیگ‌های اصلی منتشر می‌شوند تا سایت سنگین نشود
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
DISCOVER_SOURCES = False   # اسکن خودکار GitHub غیرفعال است؛ فقط منابع sources_extra.txt
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
                # نام یکتا (چند منبع از یک ریپو): owner/repo:پوشه/فایل
                auto = (parts[3] + "/" + parts[4] + ":" + "/".join(parts[-2:])) if len(parts) > 6 else url
                out.append({"name": name.strip() or auto,
                            "url": url, "trust": 65, "has_http_test": False})
    except OSError:
        pass
    return out


SOURCES += _load_extra_sources()

# --- تست دانلود واقعی (فقط برای کانفیگ‌هایی که تست HTTP را پاس کرده‌اند) ---
SPEED_TEST_LIMIT = _env_int("SPEED_TEST_LIMIT", 300)   # فقط این تعداد از سریع‌ترین‌ها (کمترین پینگ HTTP)
