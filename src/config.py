"""تنظیمات اصلی Xfinder."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DB_PATH = ROOT / "sources.db"

TIMEOUT = 5
CONCURRENCY = 400
MAX_PER_SOURCE = 5000
REMIX_PING_MAX = 70

# منابع عمومی؛ فهرست را می‌توانید با منابع مورد اعتماد خودتان توسعه دهید.
URL_SOURCES = [
    {"name":"SoliSpirit","url":"https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/main/all_configs.txt","interval":"fast"},
    {"name":"Epodonios","url":"https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt","interval":"fast"},
    {"name":"MatinGhanbari","url":"https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt","interval":"fast"},
    {"name":"mohammadaz2","url":"https://raw.githubusercontent.com/mohammadaz2/v2rayConfigsForYou/main/configs.txt","interval":"hourly"},
    {"name":"whitelist-download","url":"https://raw.githubusercontent.com/whitelist-download/v2ray-configs/main/vless.txt","interval":"hourly"},
    {"name":"FreeList-V2ray-Configs","url":"https://raw.githubusercontent.com/FreeList-V2ray-Configs/main/configs.txt","interval":"2h"},
    {"name":"Delta-Kronecker","url":"https://raw.githubusercontent.com/Delta-Kronecker/V2ray-Config/main/all.txt","interval":"2h"},
    {"name":"clean-ips","url":"https://raw.githubusercontent.com/imatixofficel/Scanner-matix/main/data/clean_ips.json","interval":"daily"},
]
TELEGRAM_CHANNELS = [
    "v2ray_configs_pool","nim_vpn_ir","outline_vpn","hope_net","proxystore11",
    "yaney_01","fnet00","ShadowProxy66","zibanabz"
]
