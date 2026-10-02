# Xfinder

پنل زنده Xfinder برای نمایش کانفیگ‌های معتبر در GitHub Pages.

## اجرا

```bash
git clone https://github.com/USERNAME/xfinder.git
cd xfinder
python -m src.main
python -m http.server 8000
```

سپس:
`http://localhost:8000`

## GitHub Pages

در Repository به مسیر Settings → Pages بروید و Branch اصلی و پوشه `/root` را انتخاب کنید.

## بروزرسانی خودکار

Workflow موجود در:

```text
.github/workflows/collect.yml
```

هر ۱۰ دقیقه اجرا می‌شود. توجه کنید GitHub Actions زمان‌بندی cron را ممکن است با تأخیر اجرا کند.

## معماری

- `finder.py`: دریافت منابع و استخراج URLهای VLESS/VMess/Trojan/SS/Hysteria2
- `validator.py`: تست TCP همزمان با Semaphore
- `remixer.py`: خواندن IPهای تمیز و ساخت نسخه‌های remix
- `publisher.py`: ساخت `data/configs.json` و خروجی‌های پروتکل
- `trust_scorer.py`: محاسبه Trust Score
- `health_monitor.py`: پایگاه داده SQLite برای وضعیت منابع
- `main.py`: اجرای کل pipeline

## نکته مهم درباره تست HTTP

تست TCP نشان می‌دهد endpoint از نظر اتصال TCP پاسخ می‌دهد؛ این به‌تنهایی به معنی سالم بودن کامل پروکسی نیست.

برای تست واقعی HTTP از داخل تونل، باید یک core مانند sing-box/Xray نصب و پیکربندی شود و ترافیک آزمایشی از همان تونل عبور کند. این نسخه هسته پروکسی را خودکار دانلود و اجرا نمی‌کند تا اجرای ناخواسته یک binary شبکه‌ای روی GitHub Actions رخ ندهد.

## Remix

جایگزینی IP به‌تنهایی تضمین‌کننده اتصال نیست. SNI، Host، TLS و سایر پارامترهای transport باید با مقصد سازگار باشند.

## منابع

منابع در `src/config.py` محدود به ۶ URL تعریف‌شده هستند. بلک‌لیست نیز همان‌جا اعمال می‌شود.

## فونت

رابط از Vazirmatn استفاده می‌کند. در محیط بدون اینترنت می‌توانید نسخه مجاز WOFF2 فونت را در:

```text
assets/fonts/
```

قرار دهید و در CSS به آن ارجاع دهید.

## مجوز و استفاده

این پروژه برای مانیتورینگ و نمایش داده‌های عمومی طراحی شده است. قبل از استفاده از منابع یا سرویس‌های اشخاص ثالث، شرایط استفاده و قوانین مربوط به آن‌ها را بررسی کنید.
