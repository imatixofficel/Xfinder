<div align="center">

<img src="assets/img/logo.png" width="120" alt="Xfinder">
**به نام پروردگار**

# Xfinder

**کانفیگ‌های تست‌شده V2Ray / WireGuard با IP تمیز — به‌روزرسانی خودکار هر ۱۰ دقیقه**

🌐 **آدرس پروژه:** https://imatixofficel.github.io/Xfinder/

[GitHub](https://github.com/imatixofficel) · [Telegram](https://t.me/Imatix7) · [YouTube](https://youtube.com/@i.matix7)

</div>

> این پروژه توسط **متیکس (Matix)** توسعه داده شده است. © تمام حقوق محفوظ است.

---

## Xfinder چیست؟

Xfinder یک Collector خودکار برای کانفیگ‌های **عمومی** VLESS / VMess / Trojan / Shadowsocks / Hysteria2 است. هر ۱۰ دقیقه GitHub Actions منابع را می‌خواند، کانفیگ‌ها را با **Xray واقعی** و یک درخواست **HTTPS واقعی** تست می‌کند، بهترین‌ها را با IP تمیز [Scanner-matix](https://github.com/imatixofficel/Scanner-matix) ترکیب (Remix) و دوباره تست می‌کند و فقط موارد سالم را روی GitHub Pages منتشر می‌کند.

## چطور استفاده کنم؟

۱. وارد **https://imatixofficel.github.io/Xfinder/** شو.
۲. در داشبورد روی **«کپی لینک اشتراک»** بزن و لینک را در برنامه‌ات (v2rayNG، Hiddify، Streisand، NekoBox، …) به‌صورت Subscription اضافه کن.
۳. برای سریع‌ترین‌ها روی **«تست و ۲۰ کانفیگ برتر»** بزن؛ لینک اشتراک ۲۰ کانفیگ با کمترین پینگ واقعی را می‌گیری.
۴. هر کانفیگ یک **نام** دارد (مثل `Xfinder • VLESS • 85ms • 003`؛ `✦` یعنی ترکیب‌شده با IP تمیز) که در برنامه‌ات هم دیده می‌شود.

### لینک‌های اشتراک (Subscription)

| فایل | آدرس |
| --- | --- |
| همه‌ی کانفیگ‌ها | https://imatixofficel.github.io/Xfinder/output/all.txt |
| ۲۰ کانفیگ برتر | https://imatixofficel.github.io/Xfinder/output/top20.txt |
| ۲۰ برتر (Base64) | https://imatixofficel.github.io/Xfinder/output/top20-b64.txt |
| VLESS | https://imatixofficel.github.io/Xfinder/output/vless.txt |
| VMess | https://imatixofficel.github.io/Xfinder/output/vmess.txt |
| Trojan | https://imatixofficel.github.io/Xfinder/output/trojan.txt |
| Shadowsocks | https://imatixofficel.github.io/Xfinder/output/ss.txt |
| Hysteria2 | https://imatixofficel.github.io/Xfinder/output/hysteria2.txt |

> با همین آدرس‌ها می‌شود پروژه را در برنامه‌ها **Mark / Subscription** کرد.

## امکانات

- **منوی همبرگری:** داشبورد، کانفیگ‌ها، WireGuard، منابع، اهدای کانفیگ، درباره، تنظیمات، لینک GitHub / Telegram / YouTube و دکمه‌ی نصب وب‌اپ.
- **نصب روی گوشی (PWA):** از منو «نصب وب‌اپ روی گوشی». در Android/Chrome نصب مستقیم؛ در iPhone از Safari → Share → Add to Home Screen.
- **WireGuard از منابع:** خط‌های `wireguard://` و فایل‌های `.conf` منابع جمع می‌شوند و چون UDP هستند، بدون تست TCP مستقیم با Xray + درخواست HTTPS واقعی تست می‌شوند؛ فقط سالم‌ها در بخش WireGuard (و `output/wireguard.txt`) می‌آیند. منبع دلخواه را در `sources_extra.txt` اضافه کن؛ اسکن خودکار GitHub هم هر اجرا دنبال مخزن‌های WireGuard/WARP می‌گردد. توجه: WireGuard در `all.txt` نیست (همه‌ی برنامه‌ها آن را در اشتراک نمی‌فهمند).
- **WireGuard شخصی (اختیاری):** کلید در مرورگر خودت ساخته می‌شود (WebCrypto، و اگر مرورگر X25519 را نداشت، پیاده‌سازی JS داخلی). کلید خصوصی هیچ‌جا ارسال نمی‌شود؛ فقط کلید عمومی برای ثبت حساب WARP به Cloudflare می‌رود.
- **ترکیب با IP تمیز:** کانفیگ‌های VLESS / VMess / Trojan با IP تمیز Scanner-matix ترکیب و دوباره با Xray تست می‌شوند. وضعیت Scanner-matix بالای داشبورد نمایش داده می‌شود.
- **اسکن خودکار منابع:** علاوه بر منابع ثابت، هر اجرا چند مخزن تازه‌ی GitHub را پیدا می‌کند (`src/discover.py`، با `DISCOVER_SOURCES=0` خاموش می‌شود). منابع کشف‌شده trust پایین دارند و کانفیگ‌هایشان مثل بقیه تست می‌شود.
- **اهدای کانفیگ:** پایین را ببین.

## اهدای کانفیگ (۲۴ ساعته)

1. در منو → **اهدای کانفیگ**، حداکثر ۳ کانفیگ و یک متن تبلیغاتی کوتاه (اختیاری، حداکثر ۲۰۰ کاراکتر) بنویس و «ارسال اهدا» را بزن.
2. **اهدای مستقیم (بدون رفتن به GitHub):** سایت به یک Cloudflare Worker رایگان می‌فرستد که با `repository_dispatch` به workflow `donations.yml` خبر می‌دهد و آن در `donations/` ذخیره می‌کند. راه‌اندازی یک‌بار: `worker/README.md`. تا آدرس Worker در `index.html` (متای `xf-donate-endpoint`) نگذاری، سایت به فرم Issue در GitHub برمی‌گردد.
3. در اجرای بعدی (≤ ۱۰ دقیقه) کانفیگ‌ها با Xray + HTTPS واقعی تست می‌شوند؛ **فقط سالم‌ها** همراه متن تبلیغاتی نمایش داده می‌شوند.
4. بعد از **۲۴ ساعت** فایل اهدا به‌صورت خودکار حذف می‌شود (پاکسازی ساعتی). هر کاربر هم‌زمان یک اهدای فعال می‌تواند داشته باشد.

متن تبلیغاتی فقط به‌صورت متن ساده نمایش داده می‌شود (HTML/لینک فعال نمی‌شود).

## نصب در GitHub

1. محتویات این ZIP را داخل repository قرار بده.
2. در **Settings → Pages → Build and deployment → Source**، گزینه **GitHub Actions** را انتخاب کن.
3. در **Settings → Actions → General → Workflow permissions** گزینه **Read and write permissions** را فعال کن (برای `donations.yml`).
4. از **Actions → Xfinder Auto Update → Run workflow** اولین اجرا را دستی شروع کن؛ بعد از آن هر ۱۰ دقیقه خودکار اجرا می‌شود.

> نکته: GitHub زمان‌بندی `cron` را گاهی چند دقیقه دیر اجرا می‌کند؛ «هر ۱۰ دقیقه» یعنی تقریباً هر ۱۰ دقیقه.

### اگر repository قبلی داری

```bash
git rm -r --cached data output sources.db
git add .gitignore package.json .github src assets index.html manifest.webmanifest sw.js favicon.ico README.md requirements.txt donations tests
git commit -m "chore: Xfinder v2.5"
git push
```

اگر یکی از مسیرها قبلاً وجود نداشت، Git خطای همان مسیر را می‌دهد؛ آن را حذف کن و دوباره اجرا کن.

## ساختار فرایند

```text
Collect (منابع ثابت + اسکن خودکار + Xfinder خودش)
   ↓
TCP pre-check → Real Xray config test → Real HTTPS request through Xray
   ↓
Clean-IP source (Scanner-matix) → TCP scan → Remix → Real Xray + HTTPS دوباره
   ↓
Donations (تست جدا) → نام‌گذاری → top20 → Publish به GitHub Pages
```

## محدودیت‌های فنی (صادقانه)

- **Remix فقط VLESS / VMess / Trojan:** جایگزینی IP تمیز Cloudflare فقط برای کانفیگ‌هایی کار می‌کند که پشت CDN هستند. Shadowsocks ساده و Hysteria2 (UDP/QUIC) از Cloudflare عبور نمی‌کنند، پس ترکیب آن‌ها معنی ندارد. هر Remix قبل از انتشار تست می‌شود و ناموفق‌ها منتشر نمی‌شوند.
- **«تست» دکمه‌ی ۲۰ برتر** نتیجه‌ی آخرین تست واقعی سرور (هر ۱۰ دقیقه) است؛ مرورگر نمی‌تواند خودش یک پروکسی را واقعاً تست کند.
- ساخت WireGuard به API Cloudflare بستگی دارد؛ اگر Cloudflare مرورگر را محدود کند، چند مسیر جایگزین امتحان می‌شود.

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
- `output/top20.txt` و `output/top20-b64.txt` (۲۰ کانفیگ برتر)
- `data/donations.json`
- `data/configs.json`

این فایل‌ها **generated** هستند و نباید دستی در Git تغییر داده شوند.

## نکته درباره کانفیگ‌های عمومی

Xfinder فقط کانفیگ‌های عمومی منابع تعریف‌شده را جمع‌آوری و تست می‌کند. وضعیت سرورهای عمومی دائماً تغییر می‌کند؛ بنابراین «سالم» بودن یعنی در زمان آخرین اجرای Workflow تست واقعی موفق بوده است، نه تضمین دائمی اتصال.

## v2.4 — پایداری و رفع هنگ‌کردن Actions

- پایپ‌لاین بودجهٔ زمانی دارد (`PIPELINE_BUDGET`، پیش‌فرض ۵۲۰ ثانیه تا اجرا در بازه‌ی ۱۰ دقیقه جا شود) و همیشه تمام می‌شود؛ هر مرحله deadline جدا دارد.
- لاگ‌ها بلافاصله چاپ می‌شوند (`PYTHONUNBUFFERED`) تا پیشرفت در Actions دیده شود.
- نمونه‌گیری تصادفی از هر منبع (`MAX_PER_SOURCE`) و سقف کاندیدای Xray (`MAX_XRAY_CANDIDATES`).
- DNS با thread-pool بزرگ؛ پایان فرایند با `os._exit` تا threadهای معلق job را نگه ندارند.
- اگر Xray کانفیگی را رد کند فقط همان کانفیگ حذف می‌شود، نه کل batch.
- باگ‌های رفع‌شده: TLS در vmess نادیده گرفته می‌شد؛ remix پورت قدیمی را کنار پورت جدید نگه می‌داشت؛ `curl -f` باعث بی‌اثر شدن بررسی کد HTTP می‌شد.
- hysteria2 و transportهای پشتیبانی‌نشده (xhttp، kcp، ...) تست نمی‌شوند و منتشر نمی‌شوند.
- اگر هیچ کانفیگی تست Xray را رد نکند job با خطا تمام می‌شود و سایت خالی منتشر نمی‌شود.
- تست: `python -m unittest discover -s tests -v` (بدون نیاز به اینترنت؛ Xray واقعی در CI استفاده می‌شود).
