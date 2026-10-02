/* لودر Xfinder با Wandering Eyes؛ مستقل از شبکه است و هیچ‌وقت بی‌نهایت نمی‌چرخد. */
const loadMessages=["در حال اتصال به منابع...","جمع‌آوری کانفیگ‌ها...","تست پینگ ۴۰۰ همزمانی...","ترکیب با IPهای تمیز...","آماده‌سازی پنل..."];
let loaderDone=false;
function finishLoader(){
  if(loaderDone)return;
  loaderDone=true;
  const l=document.getElementById("loader");
  if(!l)return;
  l.classList.add("hide");
  setTimeout(()=>l.remove(),650);
}
function startLoader(){
  const pct=document.getElementById("loadPercent"),msg=document.getElementById("loadMessage"),bar=document.getElementById("loadBar");
  if(!pct||!msg){return;}
  let n=0,i=0;
  const timer=setInterval(()=>{
    n=Math.min(100,n+4);
    pct.textContent=n+"%";
    if(bar)bar.style.width=n+"%";
    if(n%20===0)msg.textContent=loadMessages[i++%loadMessages.length];
    if(n>=100){clearInterval(timer);setTimeout(finishLoader,180);}
  },42);
  setTimeout(()=>{clearInterval(timer);finishLoader();},3600);
}
startLoader();
