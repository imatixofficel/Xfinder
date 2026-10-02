/* لودر Spokes: مستقل از اینترنت و همیشه با زمان محدود تمام می‌شود. */
const loadMessages=["در حال آماده‌سازی پنل...","در حال خواندن منابع...","آماده‌سازی کانفیگ‌ها...","بررسی وضعیت Collector...","پنل آماده است..."];
let loaderDone=false;
function finishLoader(){if(loaderDone)return;loaderDone=true;const l=document.getElementById('loader');if(!l)return;l.classList.add('hide');setTimeout(()=>l.remove(),550)}
function startLoader(){const pct=document.getElementById('loadPercent'),msg=document.getElementById('loadMessage'),bar=document.getElementById('loadBar');if(!pct||!msg)return;let n=0,last=-1;const timer=setInterval(()=>{n=Math.min(100,n+4);pct.textContent=n+'%';if(bar)bar.style.width=n+'%';const idx=Math.min(loadMessages.length-1,Math.floor(n/20));if(idx!==last){msg.textContent=loadMessages[idx];last=idx}if(n>=100){clearInterval(timer);setTimeout(finishLoader,180)}},35);setTimeout(()=>{clearInterval(timer);finishLoader()},4200)}
startLoader();
