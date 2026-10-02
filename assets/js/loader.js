const loadMessages=["در حال اتصال به منابع...","جمع‌آوری کانفیگ‌ها...","تست پینگ ۴۰۰ همزمانی...","ترکیب با IPهای تمیز...","آماده‌سازی پنل..."];
let loaderDone=false;
function finishLoader(){
  if(loaderDone)return; loaderDone=true;
  const l=document.getElementById("loader"); if(l)l.classList.add("hide");
}
async function startLoader(){
  const pct=document.getElementById("loadPercent"), msg=document.getElementById("loadMessage");
  let n=0, i=0;
  const timer=setInterval(()=>{n=Math.min(100,n+4);pct.textContent=n+"%";msg.textContent=loadMessages[i%loadMessages.length];i++;if(n>=100){clearInterval(timer);setTimeout(finishLoader,250)}},55);
  setTimeout(finishLoader,5200);
}
window.addEventListener("error",()=>setTimeout(finishLoader,100));
startLoader();
