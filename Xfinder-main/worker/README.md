# راه‌اندازی اهدای مستقیم (بدون هدایت به GitHub)

سایت روی GitHub Pages فقط فایل ثابت است و نمی‌تواند خودش در مخزن بنویسد. این Worker رایگان Cloudflare واسطه است:
**سایت → Worker → GitHub (repository_dispatch) → workflow `donations.yml` → پوشه `donations/`**

۱. توکن بساز: GitHub → Settings → Developer settings → **Fine-grained tokens** → فقط روی مخزن `Xfinder`، دسترسی **Contents: Read and write** (برای repository_dispatch کافی است). مدت اعتبار دلخواه.
۲. Cloudflare Dashboard → Workers & Pages → Create Worker → کد `donate-worker.js` را جایگذاری و Deploy کن
   (یا با CLI: `cd worker && npx wrangler deploy`).
۳. در Worker → Settings → Variables → **Secret** با نام `GITHUB_TOKEN` و مقدار توکن را اضافه کن.
   (اختیاری: Secret با نام `SALT` برای هش IP، و KV با نام `RL` برای محدودیت ۳ اهدا در ساعت.)
۴. آدرس Worker (مثل `https://xfinder-donate.<نام>.workers.dev`) را در `index.html` بگذار:
   `<meta name="xf-donate-endpoint" content="https://xfinder-donate.<نام>.workers.dev">`
۵. commit و push کن. تمام.

تا وقتی آدرس را نگذاری، سایت به روش قبلی (باز کردن فرم Issue در GitHub) برمی‌گردد تا چیزی خراب نشود.
