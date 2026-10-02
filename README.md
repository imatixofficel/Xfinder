# Xfinder — نسخه کامل و اصلاح‌شده

Xfinder یک Collector خودکار برای کانفیگ‌های عمومی VLESS / VMess / Trojan / Shadowsocks / Hysteria2 است.
Pipeline هر ۱۰ دقیقه اجرا می‌شود و ترتیب آن این است:

```text
Collect sources
   ↓
TCP pre-check
   ↓
Real Xray config test
   ↓
Real HTTPS request through Xray SOCKS
   ↓
Clean-IP source (Scanner-matix)
   ↓
Independent TCP scan of candidate IPs/ports
   ↓
Remix config + clean IP
   ↓
Real Xray + HTTPS test again
   ↓
Publish only verified proxy configs
   ↓
GitHub Pages
```

## تفاوت مهم این نسخه

- فقط باز بودن TCP کافی نیست؛ کانفیگ باید توسط Xray پذیرفته شود و یک HTTPS request واقعی از تونل عبور کند.
- IPهای Clean-IP از Scanner-matix دریافت می‌شوند، سپس Xfinder خودش IP/Portهای قابل‌دسترسی را دوباره TCP-check می‌کند.
- Remix قبل از انتشار یک بار دیگر با Xray تست می‌شود.
- فایل‌های تولیدی `data/` و `output/` دیگر توسط GitHub Actions به `main` commit نمی‌شوند؛ بنابراین اجرای خودکار نباید Merge Conflict ایجاد کند.
- Artifact نهایی مستقیماً با GitHub Pages Deploy می‌شود.
- کلید خصوصی WARP روی سرور ذخیره/منتشر نمی‌شود؛ بخش ساخت WireGuard اختصاصی در مرورگر باقی می‌ماند.
- `sources.db` و خروجی‌های runtime هم generated هستند و در Git نگه‌داری نمی‌شوند.

## نصب در GitHub

1. محتویات این ZIP را داخل repository قرار بده.
2. در **Settings → Pages → Build and deployment → Source**، گزینه **GitHub Actions** را انتخاب کن.
3. از **Actions → Xfinder Auto Update → Run workflow** اولین اجرا را دستی شروع کن.
4. بعد از موفقیت اولین اجرا، Workflow طبق schedule هر ۱۰ دقیقه اجرا می‌شود.

### اگر repository قبلی داری

چون نسخه‌های قدیمی ممکن است `data/` و `output/` را قبلاً track کرده باشند، فقط یک بار در Git Bash این کار را انجام بده:

```bash
git rm -r --cached data output sources.db

git add .gitignore package.json .github src assets index.html README.md requirements.txt

git commit -m "chore: stop tracking generated Xfinder output"
git push
```

اگر یکی از مسیرها قبلاً وجود نداشت، Git پیام خطای مربوط به همان مسیر را می‌دهد؛ مسیر موجود را حذف کن و دوباره دستور را اجرا کن.

بعد از این commit، اجرای Collector دیگر `data/output` را به `main` push نمی‌کند.

## اجرای محلی

نیازمندی‌ها:

- Python 3.11+
- Xray-core در PATH با نام `xray`
- curl

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.main
```

برای کنترل تست Xray:

```bash
XRAY_CONCURRENCY=16 XRAY_PROBE_TIMEOUT=7 python -m src.main
```

## خروجی سایت

Workflow خروجی را در Artifact مربوط به GitHub Pages قرار می‌دهد:

- `output/all.txt`
- `output/vless.txt`
- `output/vmess.txt`
- `output/trojan.txt`
- `output/ss.txt`
- `output/hysteria2.txt`
- `output/wireguard.txt`
- `data/configs.json`

این فایل‌ها **generated** هستند و نباید دستی در Git تغییر داده شوند.

## نکته درباره کانفیگ‌های عمومی

Xfinder فقط کانفیگ‌های عمومی منابع تعریف‌شده را جمع‌آوری و تست می‌کند. وضعیت سرورهای عمومی دائماً تغییر می‌کند؛ بنابراین «سالم» بودن یعنی در زمان آخرین اجرای Workflow تست واقعی موفق بوده است، نه تضمین دائمی اتصال.
