from pathlib import Path

# تنظیمات پایه پروژه Xfinder
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUTPUT = ROOT / 'output'
TRUST_THRESHOLD = 60
CONCURRENCY = 400
TIMEOUT = 5

# این نسخه از بسته، منابع زنده و endpointهای پروکسی را جمع‌آوری یا remix نمی‌کند.
# آدرس‌های واقعی را عمداً در کد اجرایی قرار نداده‌ایم.
