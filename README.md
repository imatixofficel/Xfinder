# Xfinder — Live Node Panel

پنل Xfinder برای GitHub Pages با رابط تاریک الهام‌گرفته از داشبورد مرجع، فونت Vazirmatn، RTL/LTR، لودر «به نام خدا»، جدول کانفیگ‌ها و Collector پایتون.

## نکته مهم درباره «کانفیگ‌ها نمی‌آیند»

GitHub Pages فقط Frontend است و نمی‌تواند Python را اجرا کند. بنابراین مسیر درست این است:

1. GitHub Actions اجرا شود.
2. منابع جمع‌آوری شوند.
3. کانفیگ‌ها TCP Validate شوند.
4. خروجی `data/configs.json` ساخته شود.
5. GitHub Actions فایل را commit کند.
6. GitHub Pages همان فایل را نمایش دهد.

نسخه جدید لودر را مستقل از شبکه کرده است؛ بنابراین اگر API یا IP detection خطا داشته باشد، لودر دیگر روی «در حال اتصال به منابع...» گیر نمی‌کند.

## نصب

```bash
git clone https://github.com/USERNAME/xfinder.git
cd xfinder
python -m src.main
python -m http.server 8000 --directory .
```

سپس:

```text
http://localhost:8000
```

## فعال‌کردن GitHub Pages

در GitHub:

`Settings → Pages → Deploy from a branch → main → / (root)`

## اجرای اولین جمع‌آوری

بعد از Push، از مسیر زیر Workflow را یک بار دستی اجرا کنید:

`Actions → Xfinder Auto Update → Run workflow`

پس از موفقیت Workflow، فایل `data/configs.json` و فایل‌های `output/*.txt` تغییر می‌کنند و صفحه آنها را نشان می‌دهد.

Workflow زمان‌بندی‌شده نیز هر ۱۰ دقیقه تعریف شده است؛ زمان واقعی شروع Scheduled Actions ممکن است چند دقیقه جابه‌جا شود.

## ساختار

```text
xfinder/
├── index.html
├── assets/
│   ├── css/
│   ├── js/
│   ├── img/logo.svg
│   └── fonts/
├── data/configs.json
├── output/
├── src/
│   ├── config.py
│   ├── trust_scorer.py
│   ├── health_monitor.py
│   ├── finder.py
│   ├── validator.py
│   ├── remixer.py
│   ├── publisher.py
│   └── main.py
└── .github/workflows/collect.yml
```

## ویژگی‌های Frontend

- سایدبار سمت چپ و ظاهر Dark Dashboard
- کارت‌های آماری
- فیلتر پروتکل و جستجوی زنده
- کپی کانفیگ و QR
- RTL/LTR
- تشخیص زبان از localStorage، زبان مرورگر و در نهایت IP
- حالت Dark/Light
- لودر Wandering Eyes با «به نام خدا»
- لودر مستقل از API و دارای timeout قطعی
- نمایش وضعیت داده به‌جای گیرکردن روی Loading

## ویژگی‌های Backend

- جمع‌آوری موازی ۶ منبع
- پشتیبانی از URI مستقیم و Base64 subscription
- استخراج VMess JSON
- تست TCP با `asyncio.Semaphore(400)` و timeout پنج ثانیه
- حذف نودهای مرده
- Remix با IPهای تمیز و حفظ پارامترهای SNI/Host
- تولید فایل‌های پروتکل و `all.txt`
- تولید `data/configs.json`

## وضعیت HTTP Test

برای اینکه عدد HTTP به‌عنوان «تست واقعی» جعل نشود، نسخه فعلی مقدار `http_ping_ms` را فقط زمانی منتشر می‌کند که Collector واقعاً آن را تولید کرده باشد. TCP باز بودن پورت به‌تنهایی HTTP health محسوب نمی‌شود.

## منابع

منابع دقیق در `src/config.py` تعریف شده‌اند. در صورت خراب یا حذف شدن یک منبع، Collector آن منبع را در لاگ Workflow گزارش می‌کند و اجرای سایر منابع را ادامه می‌دهد.

## مجوز و مسئولیت

منابع عمومی ممکن است تغییر کنند یا حذف شوند. قبل از استفاده از هر کانفیگ، قوانین شبکه و ارائه‌دهنده سرویس خود را رعایت کنید.
