/* لودر Xfinder: مستقل از API است تا در صورت خطای شبکه هرگز گیر نکند. */
const loadMessages=["در حال اتصال به منابع...","جمع‌آوری کانفیگ‌ها...","تست پینگ ۴۰۰ همزمانی...","ترکیب با IPهای تمیز...","آماده‌سازی پنل..."];
let loaderDone=false;
function finishLoader(){
  if(loaderDone)return;
  loaderDone=true;
  const l=document.getElementById("loader");
  if(!l)return;
  l.classList.add("hide");
  setTimeout(()=>{l.remove();},700);
}
function startLoader(){
  const pct=document.getElementById("loadPercent"),msg=document.getElementById("loadMessage");
  if(!pct||!msg)return;
  let n=0,i=0;
  const timer=setInterval(()=>{
    n=Math.min(100,n+5);
    pct.textContent=n+"%";
    msg.textContent=loadMessages[i++%loadMessages.length];
    if(n>=100){clearInterval(timer);setTimeout(finishLoader,180);}
  },80);
  // حتی در صورت خطای JS یا شبکه، لودر باید حداکثر بعد از 4 ثانیه بسته شود.
  setTimeout(finishLoader,4000);
}
startLoader();
