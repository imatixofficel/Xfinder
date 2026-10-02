const translations = {
  fa:{god_text:"به نام خدا",dashboard:"داشبورد",configs:"کانفیگ‌ها",sources:"منابع",stats:"آمار",settings:"تنظیمات",total:"تعداد کل",alive:"سالم",remixed:"Remix شده",avg_ping:"میانگین پینگ",protocol:"پروتکل",server:"سرور",ping:"پینگ",country:"کشور",actions:"عملیات",copy:"کپی",copied:"کپی شد!",last_update:"آخرین آپدیت"},
  en:{god_text:"In the Name of God",dashboard:"Dashboard",configs:"Configs",sources:"Sources",stats:"Stats",settings:"Settings",total:"Total",alive:"Alive",remixed:"Remixed",avg_ping:"Avg Ping",protocol:"Protocol",server:"Server",ping:"Ping",country:"Country",actions:"Actions",copy:"Copy",copied:"Copied!",last_update:"Last Update"}
};
let currentLang = localStorage.getItem("xfinder_lang") || null;
function applyLang(lang){
  currentLang=lang; localStorage.setItem("xfinder_lang",lang);
  document.documentElement.lang=lang; document.documentElement.dir=lang==="fa"?"rtl":"ltr";
  document.querySelectorAll("[data-i18n]").forEach(el=>{const k=el.dataset.i18n;if(translations[lang][k])el.textContent=translations[lang][k]});
  document.getElementById("langToggle").textContent=lang==="fa"?"🇮🇷 فارسی":"🇬🇧 English";
}
async function detectLanguage(){
  if(currentLang){applyLang(currentLang);return}
  const nav=(navigator.language||"en").toLowerCase();
  if(nav.startsWith("fa")){applyLang("fa");return}
  if(nav.startsWith("en")){applyLang("en");return}
  try{
    const r=await fetch("https://ipapi.co/json/",{signal:AbortSignal.timeout(1800)});
    const d=await r.json(); applyLang(["IR","AF"].includes(d.country_code)?"fa":"en");
  }catch(e){applyLang("en")}
}
