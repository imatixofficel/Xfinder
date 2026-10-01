const translations={
  fa:{god_text:"به نام خدا",dashboard:"داشبورد",configs:"کانفیگ‌ها",sources:"منابع",stats:"آمار",settings:"تنظیمات",total:"تعداد کل",alive:"سالم",remixed:"Remix شده",avg_ping:"میانگین پینگ",protocol:"پروتکل",server:"سرور",ping:"پینگ",country:"کشور",actions:"عملیات",copy:"کپی",copied:"کپی شد!",last_update:"آخرین آپدیت"},
  en:{god_text:"In the Name of God",dashboard:"Dashboard",configs:"Configs",sources:"Sources",stats:"Stats",settings:"Settings",total:"Total",alive:"Alive",remixed:"Remixed",avg_ping:"Avg Ping",protocol:"Protocol",server:"Server",ping:"Ping",country:"Country",actions:"Actions",copy:"Copy",copied:"Copied!",last_update:"Last Update"}
};
let currentLang="fa";
function t(key){return translations[currentLang][key]??key}
function applyLanguage(lang){
  currentLang=lang==="en"?"en":"fa";
  document.documentElement.lang=currentLang;
  document.documentElement.dir=currentLang==="fa"?"rtl":"ltr";
  document.querySelectorAll("[data-i18n]").forEach(el=>el.textContent=t(el.dataset.i18n));
  const b=document.getElementById("lang-toggle"); if(b)b.textContent=currentLang==="fa"?"🇮🇷 فارسی":"🇬🇧 English";
  localStorage.setItem("xfinder_lang",currentLang);
}
