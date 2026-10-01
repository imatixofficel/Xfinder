const loaderMessages={
  fa:["در حال اتصال به منابع...","جمع‌آوری کانفیگ‌ها...","تست پینگ ۴۰۰ همزمانی...","ترکیب با IPهای تمیز...","آماده‌سازی پنل..."],
  en:["Connecting to sources...","Collecting configurations...","Testing 400 concurrent connections...","Combining with clean IPs...","Preparing dashboard..."]
};
async function runLoader(){
  const screen=document.getElementById("xf-loader"), app=document.getElementById("app"), pct=document.querySelector(".loader-percent"), msg=document.getElementById("loader-message");
  let lang=localStorage.getItem("xfinder_lang");
  if(!lang){
    const nav=(navigator.language||"en").toLowerCase();
    lang=nav.startsWith("fa")?"fa":nav.startsWith("en")?"en":null;
    if(!lang){try{const r=await fetch("https://ipapi.co/json/");const j=await r.json();lang=["IR","AF"].includes(j.country_code)?"fa":"en"}catch{lang="en"}}
  }
  applyLanguage(lang);
  for(let p=0;p<=100;p+=4){
    pct.textContent=p+"%"; msg.textContent=loaderMessages[currentLang][Math.min(4,Math.floor(p/20))];
    await new Promise(r=>setTimeout(r,45));
  }
  await new Promise(r=>setTimeout(r,180));
  screen.classList.add("hidden"); app.classList.remove("hidden");
}
