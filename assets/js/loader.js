/* لودر Spokes؛ مستقل از شبکه و محدود به چند ثانیه است. */
const loadMessages=["در حال اتصال به منابع...","جمع‌آوری کانفیگ‌ها...","تست پینگ ۴۰۰ همزمانی...","ترکیب با IPهای تمیز...","آماده‌سازی پنل..."];
let loaderDone=false;
function finishLoader(){if(loaderDone)return;loaderDone=true;const l=document.getElementById("loader");if(!l)return;l.classList.add("hide");setTimeout(()=>l.remove(),650)}
function startLoader(){
 const pct=document.getElementById("loadPercent"),msg=document.getElementById("loadMessage"),bar=document.getElementById("loadBar");
 if(!pct||!msg)return;
 let n=0,last=-1;
 const timer=setInterval(()=>{
   n=Math.min(100,n+3);
   pct.textContent=n+"%"; if(bar)bar.style.width=n+"%";
   const idx=Math.min(loadMessages.length-1,Math.floor(n/20));
   if(idx!==last){msg.textContent=loadMessages[idx];last=idx}
   if(n>=100){clearInterval(timer);setTimeout(finishLoader,180)}
 },38);
 setTimeout(()=>{clearInterval(timer);finishLoader()},5000);
}
startLoader();
