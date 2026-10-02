from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DB_PATH = ROOT / "sources.db"

CONCURRENCY = 400
TCP_TIMEOUT = 5.0
HTTP_TIMEOUT = 8.0
MIN_TRUST = 60
MAX_REMIX_PING = 70
REMIX_PER_CONFIG = 3

SOURCES = [
    {"name":"Au1rxx/free-vpn-subscriptions","url":"https://github.com/Au1rxx/free-vpn-subscriptions/raw/main/output/v2ray-base64.txt","trust":100,"has_http_test":True},
    {"name":"Epodonios/v2ray-configs","url":"https://github.com/Epodonios/v2ray-configs/raw/main/All_Configs_Sub.txt","trust":85,"has_http_test":False},
    {"name":"MatinGhanbari/v2ray-configs","url":"https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/super-sub.txt","trust":85,"has_http_test":False},
    {"name":"Delta-Kronecker/V2ray-Config","url":"https://github.com/Delta-Kronecker/V2ray-Config/raw/refs/heads/main/config/farg/all_configs.json","trust":90,"has_http_test":False},
    {"name":"R3ZARAHIMI/tg-v2ray-configs-every2h","url":"https://raw.githubusercontent.com/R3ZARAHIMI/tg-v2ray-configs-every2h/main/all.txt","trust":80,"has_http_test":False},
    {"name":"FreeList-V2ray-Configs","url":"https://raw.githubusercontent.com/FreeList-V2ray-Configs/main/Config_no_cf.txt","trust":75,"has_http_test":False},
]
CLEAN_IPS_URL = "https://raw.githubusercontent.com/imatixofficel/Scanner-matix/main/data/clean_ips.json"
BLACKLIST = {"v2ray_configs_pool","nim_vpn_ir","outline_vpn","hope_net","proxystore11","yaney_01","fnet00","ShadowProxy66","zibanabz"}
