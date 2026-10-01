# Xfinder

پنل استاتیک Xfinder با ظاهر داشبورد مدرن، فونت Vazirmatn، RTL/LTR، لودر «به نام خدا»، جستجو، فیلتر، حالت تاریک، Trust Score و نمایش داده از `data/configs.json`.

## نکته مهم

این بسته یک **نسخه امن و قابل انتشار** است: جمع‌آوری خودکار endpointهای پروکسی عمومی، تست عملیاتی آن‌ها و Remix با IPهای شخص ثالث در کد اجرایی فعال نشده‌اند. فایل‌های `finder.py`، `validator.py` و `remixer.py` به‌صورت scaffold محلی هستند و از fixtureهای داخل پروژه استفاده می‌کنند.

## اجرا

```bash
python -m src.main
python -m http.server 8000 --directory .
```

سپس `http://localhost:8000` را باز کنید.

## GitHub Pages

`Settings → Pages → Deploy from branch → main → / (root)`

## زمان‌بندی

Workflow با `*/10 * * * *` اجرا می‌شود. GitHub Actions ممکن است اجرای cron را چند دقیقه جابه‌جا کند.

## امکانات رابط

- طراحی داشبورد تیره/روشن با کارت و سایدبار
- فونت Vazirmatn
- RTL/LTR
- تشخیص زبان از localStorage، مرورگر و در مرحله سوم IP
- لودر «به نام خدا» و Wandering Eyes با CSS خالص
- فیلتر VLESS / VMess / Trojan / SS / Hysteria2
- جستجوی زنده
- Copy و QR placeholder
- Trust Score و منابع
- واکنش‌گرا و منوی موبایل
