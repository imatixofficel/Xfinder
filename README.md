# Xfinder

پنل استاتیک برای نمایش وضعیت کانفیگ‌های عمومی به همراه pipeline پایتون و GitHub Actions.

> **نکته فنی:** GitHub Pages فقط فایل‌های استاتیک را سرو می‌کند. جمع‌آوری و تست در GitHub Actions اجرا می‌شود و خروجی آن داخل `data/` و `output/` قرار می‌گیرد.

## امکانات

- پنل HTML/CSS/JS بدون فریم‌ورک
- RTL/LTR و فارسی/انگلیسی
- تشخیص زبان از localStorage، زبان مرورگر و در مرحله سوم IP
- لودینگ اختصاصی Xfinder با «به نام خدا»
- جستجوی زنده و فیلتر پروتکل
- کپی کانفیگ و QR
- حالت روشن/تاریک
- جمع‌آوری از URLهای عمومی و صفحات عمومی Telegram
- تست TCP با `asyncio.Semaphore(400)`
- خروجی تفکیک‌شده برای VLESS/VMess/Trojan/SS/Hysteria2
- SQLite برای وضعیت منابع
- اجرای خودکار هر ۱۰ دقیقه

## نصب

```bash
git clone https://github.com/USERNAME/xfinder.git
cd xfinder

python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
python -m src.main

python -m http.server 8000 --directory .
```

سپس `http://localhost:8000` را باز کنید.

## فعال‌سازی GitHub Pages

در GitHub:
`Settings → Pages → Build and deployment → Deploy from a branch → main → / (root)`

بعد از فعال شدن Pages، آدرس سایت مشابه زیر خواهد بود:

`https://USERNAME.github.io/xfinder/`

## زمان‌بندی

Workflow با cron زیر درخواست می‌شود:

```yaml
- cron: "*/10 * * * *"
```

زمان‌بندی GitHub Actions ممکن است در زمان شلوغی چند دقیقه تأخیر داشته باشد.

## ساختار

- `index.html` رابط اصلی
- `assets/` استایل، جاوااسکریپت و لوگو
- `data/configs.json` داده قابل مصرف توسط Pages
- `src/` pipeline پایتون
- `output/` خروجی‌های متنی
- `.github/workflows/collect.yml` زمان‌بندی خودکار

## نکات مهم

1. تست validator فقط handshake TCP را اندازه می‌گیرد و به معنی احراز سلامت کامل پروتکل نیست.
2. جایگزینی IP در remix به تنهایی اتصال را تضمین نمی‌کند؛ SNI، Host، TLS و مسیر شبکه باید با endpoint سازگار باشند.
3. منابع عمومی ممکن است حذف، تغییر، rate-limit یا archive شوند. بنابراین pipeline با خطاهای منبع برخورد می‌کند.
4. GitHub Pages برای فایل‌های بسیار بزرگ مناسب نیست؛ در مقیاس بالا می‌توان از Release Assets یا object storage استفاده کرد.
5. QR از سرویس عمومی QuickChart در زمان کلیک استفاده می‌کند. برای محیط کاملاً مستقل، یک کتابخانه QR محلی اضافه کنید.
6. برای کشور هر IP از `ipapi.co` استفاده می‌شود؛ محدودیت نرخ یا عدم دسترسی می‌تواند کشور را `--` نشان دهد.
7. اجرای همزمان ۴۰۰ اتصال می‌تواند باعث rate-limit یا محدودیت شبکه شود؛ در صورت نیاز مقدار `CONCURRENCY` را کاهش دهید.

## افزودن منبع

منابع URL در `src/config.py` داخل `URL_SOURCES` و کانال‌ها در `TELEGRAM_CHANNELS` قرار دارند.

فرمت ساده:

```python
{"name":"MySource","url":"https://example.com/configs.txt","interval":"hourly"}
```

## تست دستی

```bash
python -m src.finder
python -m src.validator
python -m src.remixer
python -m src.publisher
```

یا کل pipeline:

```bash
python -m src.main
```

## مجوز و مسئولیت

قبل از استفاده از منابع و داده‌های شخص ثالث، شرایط استفاده و مجوز آن‌ها را بررسی کنید. این پروژه صرفاً ابزار جمع‌آوری، اندازه‌گیری و نمایش داده‌های عمومی است.
