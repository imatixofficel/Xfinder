"use strict";
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=v=>String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
const IC={grid:'<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',list:'<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',shield:'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',gear:'<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2-1.2L14 3h-4l-.6 2.7a7 7 0 0 0-2 1.2l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2 1.2L10 21h4l.6-2.7a7 7 0 0 0 2-1.2l2.3 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/>',bolt:'<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',menu:'<path d="M4 7h16M4 12h16M4 17h16"/>',search:'<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',refresh:'<path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7"/>',copy:'<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/>',
github:'<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
telegram:'<path d="M22 2 11 13"/><path d="M22 2l-7 20-4-9-9-4z"/>',
youtube:'<path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/><path d="m10 15 5-3-5-3z"/>',
gift:'<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
download:'<path d="M12 3v12M7 10l5 5 5-5M4 21h16"/>'};
const fillIcons=r=>$$("svg[data-ic]",r).forEach(s=>{s.setAttribute("viewBox","0 0 24 24");s.classList.add("i");s.innerHTML=IC[s.dataset.ic]||""});
const T={fa:{god1:"به نام خدا",hello:"کاربر Xfinder",menu:"منو",system:"سیستم",dashboard:"داشبورد",configs:"کانفیگ‌ها",sources:"منابع",settings:"تنظیمات",promo:"کانفیگ‌ها <b>هر ۱۰ دقیقه</b><br>خودکار تازه می‌شوند",refresh:"بروزرسانی",welcome:"به Xfinder خوش آمدید!",updated:"آخرین بروزرسانی",qs_t:"اشتراک شخصی خودت را بساز",qs_d:"همه کانفیگ‌های سالم در یک لینک؛ در برنامه‌ات وارد کن و تمام.",qs_b:"کپی لینک اشتراک",remixed_l:"ترکیب با IP تمیز",proto_t:"پروتکل‌ها",assets:"کانفیگ‌ها",configs_d:"اول کانفیگ‌های ترکیب‌شده با IP تمیز نمایش داده می‌شوند.",wg_d:"با Cloudflare WARP و IP تمیز. فایل .conf را دانلود کن یا لینک را کپی کن.",wg_gen_t:"ساخت کانفیگ اختصاصی",wg_gen_d:"کلید در مرورگر خودت ساخته می‌شود و فقط برای تو است.",wg_gen_b:"بساز",src_d:"منابع معتبر و امتیاز اعتماد آن‌ها",lang_l:"زبان",sub_l:"لینک‌های اشتراک",copy:"کپی",copied:"کپی شد!",all:"همه",clean:"IP تمیز",server:"سرور",type:"نوع",ping:"پینگ",trust:"اعتماد",more:"نمایش بیشتر",refreshed:"بروزرسانی شد",detail:"جزئیات",download:"دانلود .conf",empty:"هنوز کانفیگی منتشر نشده. اجرای Collector را بررسی کنید.",copyall:"کپی همه",search:"جستجو",sel:"یک کانفیگ را انتخاب کن",nowg:"هنوز WireGuard ساخته نشده.",genfail:"ساخت انجام نشد (اینترنت یا محدودیت Cloudflare). چند لحظه بعد دوباره امتحان کن.",genwait:"در حال ساخت…",
donate:"اهدای کانفیگ",about:"درباره",links:"لینک‌ها",install:"نصب وب‌اپ روی گوشی",top_b:"تست و ۲۰ کانفیگ برتر",top_t:"۲۰ کانفیگ برتر",top_copy:"کپی لینک اشتراک",top_all:"کپی همه کانفیگ‌ها",
top_info:"نتیجه‌ی آخرین تست واقعی (Xray + HTTPS)، مرتب‌شده بر اساس کمترین پینگ. هر ۱۰ دقیقه تازه می‌شود.",top_none:"هنوز نتیجه‌ای نیست.",
don_d:"کانفیگ خودت را اهدا کن؛ بعد از تست واقعی ۲۴ ساعت به همه نمایش داده می‌شود و خودکار حذف می‌شود.",don_t:"ثبت اهدای جدید",don_cfg:"کانفیگ‌ها (حداکثر ۳ تا، هر کدام در یک خط)",don_ad:"متن تبلیغاتی (اختیاری، حداکثر ۲۰۰ کاراکتر)",don_ad_ph:"مثلاً: کانال تلگرام من",
don_note:"ثبت از طریق یک Issue در GitHub انجام می‌شود (نیاز به حساب GitHub). فقط کانفیگ‌هایی که تست واقعی را پاس کنند نمایش داده می‌شوند.",don_send:"ارسال اهدا",don_list:"اهدای‌های فعال",don_empty:"فعلاً اهدای فعالی نیست.",don_nocfg:"هیچ کانفیگ معتبری پیدا نشد.",don_long:"کانفیگ‌ها کپی شد؛ در صفحه‌ی GitHub در بخش Configs جایگذاری کن.",
left:"باقی‌مانده",hours:"ساعت",min:"دقیقه",name:"نام",about_t:"این پروژه توسط <b>متیکس (Matix)</b> توسعه داده شده است.",about_r:"© تمام حقوق این پروژه محفوظ است.",
clean_ok:"IP تمیز Scanner-matix: ",clean_no:"IP تمیز Scanner-matix در دسترس نبود",inst_done:"نصب شد",
ios_help:"در Safari دکمه‌ی Share (اشتراک‌گذاری) را بزن و «Add to Home Screen» را انتخاب کن.",and_help:"از منوی مرورگر (⋮) گزینه‌ی «Install app» یا «Add to Home screen» را انتخاب کن.",genok:"کانفیگ اختصاصی ساخته شد",count:"تعداد",origin:"منبع"},
en:{god1:"In the Name of God",hello:"Xfinder User",menu:"MENU",system:"SYSTEM",dashboard:"Dashboard",configs:"Configs",sources:"Sources",settings:"Settings",promo:"Configs refresh <b>every 10 min</b><br>automatically",refresh:"Refresh",welcome:"Welcome to Xfinder!",updated:"Last update",qs_t:"Build your own subscription",qs_d:"All healthy configs in one link. Import it in your app and you're done.",qs_b:"Copy subscription link",remixed_l:"merged with clean IPs",proto_t:"Protocols",assets:"Configs",configs_d:"Configs merged with clean IPs are shown first.",wg_d:"Cloudflare WARP with clean IPs. Download the .conf or copy the link.",wg_gen_t:"Create your own config",wg_gen_d:"Keys are created in your browser and belong only to you.",wg_gen_b:"Create",src_d:"Reputable sources and their trust score",lang_l:"Language",sub_l:"Subscription links",copy:"Copy",copied:"Copied!",all:"All",clean:"Clean IP",server:"Server",type:"Type",ping:"Ping",trust:"Trust",more:"Show more",refreshed:"Refreshed",detail:"Details",download:"Download .conf",empty:"No configs yet. Check the collector run.",copyall:"Copy all",search:"Search",sel:"Select a config",nowg:"No WireGuard yet.",genfail:"Could not create it (network or Cloudflare limit). Try again in a moment.",genwait:"Creating…",
donate:"Donate configs",about:"About",links:"LINKS",install:"Install web app on phone",top_b:"Test & top 20 configs",top_t:"Top 20 configs",top_copy:"Copy subscription link",top_all:"Copy all configs",
top_info:"Result of the latest real test (Xray + HTTPS), sorted by lowest ping. Refreshed every 10 minutes.",top_none:"No results yet.",
don_d:"Donate your config; after a real test it is shown to everyone for 24 hours and then removed automatically.",don_t:"New donation",don_cfg:"Configs (max 3, one per line)",don_ad:"Promo text (optional, max 200 chars)",don_ad_ph:"e.g. my Telegram channel",
don_note:"Submission goes through a GitHub Issue (GitHub account required). Only configs that pass the real test are shown.",don_send:"Send donation",don_list:"Active donations",don_empty:"No active donations right now.",don_nocfg:"No valid config found.",don_long:"Configs copied; paste them into the Configs field on the GitHub page.",
left:"Left",hours:"h",min:"m",name:"Name",about_t:"This project was developed by <b>Matix</b>.",about_r:"© All rights reserved.",
clean_ok:"Scanner-matix clean IPs: ",clean_no:"Scanner-matix clean IPs unavailable",inst_done:"Installed",
ios_help:"In Safari tap Share, then choose “Add to Home Screen”.",and_help:"Open the browser menu (⋮) and choose “Install app” or “Add to Home screen”.",genok:"Your config is ready",count:"Count",origin:"Source"}};
let lang=localStorage.getItem("xf_lang")||((navigator.language||"").startsWith("fa")?"fa":"en");
const t=k=>T[lang][k]||k;
function applyLang(){document.documentElement.lang=lang;document.documentElement.dir=lang==="fa"?"rtl":"ltr";
 $$("[data-i]").forEach(e=>{const v=t(e.dataset.i);if(e.dataset.i==="promo"||e.dataset.i==="about_t")e.innerHTML=v;else e.textContent=v});
 $$("[data-ip]").forEach(e=>e.placeholder=t(e.dataset.ip));$("#lang span").textContent=lang==="fa"?"FA":"EN";localStorage.setItem("xf_lang",lang);if(D)renderAll()}
const toast=m=>{const e=$("#toast");e.textContent=m;e.classList.add("show");clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove("show"),1600)};
const copy=async s=>{try{await navigator.clipboard.writeText(s)}catch{const a=document.createElement("textarea");a.value=s;document.body.append(a);a.select();document.execCommand("copy");a.remove()}toast(t("copied"))};
// wordmark: هر حرف جدا انیمیت می‌شود
$$("[data-wm]").forEach(e=>{e.setAttribute("aria-label",e.dataset.wm);e.innerHTML=[...e.dataset.wm].map((c,i)=>`<span style="--n:${i}" aria-hidden="true">${c}</span>`).join("")});
fillIcons();
// data
let D=null,view=[],sel=null,filter={p:"all",q:""};
const base=location.href.replace(/[#?].*$/,"").replace(/[^/]*$/,"");
async function load(){try{const r=await fetch("data/configs.json?ts="+Date.now(),{cache:"no-store"});D=await r.json()}catch{D={stats:{},sources:{},configs:[],source_list:[],donations:[]}}D.configs=D.configs||[];return D}
const pc=x=>x.protocol==="wireguard"?"WG":(x.protocol||"").toUpperCase();
const pcls=n=>n&&n<150?"g":"";
function spark(x){let h=0;const s=(x.server||"")+x.port;for(const c of s)h=(h*31+c.charCodeAt(0))>>>0;const b=Number(x.tcp_ping_ms)||200;let p="";for(let i=0;i<8;i++){h=(h*1103515245+12345)>>>0;const y=4+((h>>8)%14)*(Math.min(b,400)/400+.4);p+=(i?"L":"M")+i*12+" "+Math.min(21,y).toFixed(1)}return`<svg class="spark" viewBox="0 0 84 24"><path d="${p}"/></svg>`}
function renderBars(){const top=D.configs.filter(x=>x.tcp_ping_ms).slice(0,7);const mx=Math.max(1,...top.map(x=>x.tcp_ping_ms));
 $("#bars").innerHTML=top.map((x,i)=>`<div class="bar" style="--i:${i}"><b style="height:${Math.max(14,100-x.tcp_ping_ms/mx*70)}%"></b><b style="height:${x.is_remixed?24:12}%"></b></div>`).join("")||"";
 $("#xl").innerHTML=top.map(x=>`<span>${Math.round(x.tcp_ping_ms)}</span>`).join("")}
function renderStats(){const s=D.stats||{},n=D.configs.length;$("#alivePct").innerHTML=(n?100:0)+"<small>%</small>";$("#remixChip").textContent="+"+(s.remixed||0);
 $("#upd").textContent=D.updated_at?new Date(D.updated_at).toLocaleString(lang==="fa"?"fa-IR":"en-US"):"—";$("#navCount").textContent=n;$("#navWg").textContent=s.wireguard||0;$("#cnt1").textContent=n;const ci=s.clean_ips||0;$("#cleanInfo").textContent=ci?t("clean_ok")+ci:t("clean_no")}
let ptab="all";
function renderProtos(){const tabs=[["all",t("all")],["clean",t("clean")]];$("#protoTabs").innerHTML=tabs.map(([k,l])=>`<button class="tab ${ptab===k?"on":""}" data-pt="${k}">${l}</button>`).join("");
 const src=D.configs.filter(x=>ptab==="all"||x.is_remixed),c={};src.forEach(x=>c[x.protocol]=(c[x.protocol]||0)+1);
 const rows=Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,4);
 $("#protoList").innerHTML=rows.map(([k,v])=>`<div class="row"><span class="ic latin" style="font-size:10px;font-weight:700">${k.slice(0,2).toUpperCase()}</span><div><b>${v}</b><small class="latin">${k==="wireguard"?"WireGuard":k.toUpperCase()}</small></div><button class="ghost" data-all="${k}">${t("copyall")}</button></div>`).join("")||`<div class="empty">—</div>`;
 $$("[data-pt]").forEach(b=>b.onclick=()=>{ptab=b.dataset.pt;renderProtos()});
 $$("[data-all]").forEach(b=>b.onclick=()=>copy(src.filter(x=>x.protocol===b.dataset.all).map(x=>x.config).join("\n")))}
const PT=["all","clean","vless","vmess","trojan","ss","wireguard"];
function mountTable(root,pageSize){
 let n=pageSize;const st={p:"all",q:""};
 root.innerHTML=`<div class="tools"><div class="tabs" style="margin:0"></div><label class="search"><svg class="i" data-ic="search"></svg><input data-ip="search" placeholder="${t("search")}"></label></div><div class="tw"><table><thead><tr><th>${t("server")}</th><th>${t("name")}</th><th>${t("type")}</th><th>${t("ping")}</th><th>${t("trust")}</th><th></th><th></th></tr></thead><tbody></tbody></table></div><button class="ghost more">${t("more")}</button>`;
 fillIcons(root);const tb=$("tbody",root),tabs=$(".tabs",root),more=$(".more",root);
 const list=()=>D.configs.filter(x=>(st.p==="all"||(st.p==="clean"?x.is_remixed:x.protocol===st.p))&&(!st.q||(x.server+x.port+x.protocol+x.source+(x.name||"")).toLowerCase().includes(st.q)));
 const draw=()=>{const L=list();view=L;
  tabs.innerHTML=PT.map(k=>`<button class="tab ${st.p===k?"on":""}" data-k="${k}">${k==="all"?t("all"):k==="clean"?t("clean"):k==="wireguard"?"WG":k.toUpperCase()}</button>`).join("");
  tb.innerHTML=L.slice(0,n).map((x,i)=>`<tr data-row="${i}" class="${sel===x?"sel":""}"><td><div class="coin"><i>${pc(x).slice(0,2)}</i>${esc(x.server)}<small>:${esc(x.port)}</small></div></td><td class="latin nm" title="${esc(x.name)}">${esc(x.name||"")}</td><td class="latin">${pc(x)}${x.is_remixed?" ✦":""}</td><td><span class="pp ${pcls(x.tcp_ping_ms)}">${x.tcp_ping_ms?Math.round(x.tcp_ping_ms)+" ms":"—"}</span></td><td class="latin">${esc(x.trust_score??"—")}</td><td>${spark(x)}</td><td><button class="pill sm" data-c="${i}">${t("copy")}</button></td></tr>`).join("")||`<tr><td colspan="7" class="empty">${t("empty")}</td></tr>`;
  more.style.display=L.length>n?"":"none";$$("[data-k]",tabs).forEach(b=>b.onclick=()=>{st.p=b.dataset.k;n=pageSize;draw()})};
 tb.onclick=e=>{const c=e.target.closest("[data-c]"),r=e.target.closest("tr[data-row]");if(c){e.stopPropagation();copy(view[c.dataset.c].config);return}if(r){sel=view[r.dataset.row];renderDetail();$$("tr.sel").forEach(x=>x.classList.remove("sel"));r.classList.add("sel")}};
 more.onclick=()=>{n+=pageSize;draw()};$("input",root).oninput=e=>{st.q=e.target.value.toLowerCase().trim();n=pageSize;draw()};draw()}
function renderDetail(){const x=sel||D.configs[0];const el=$("#detail");if(!x){el.innerHTML=`<div class="empty">${t("sel")}</div>`;return}sel=x;
 el.innerHTML=`<div class="logo latin" style="font-weight:700">${pc(x).slice(0,2)}</div><h3 class="latin">${pc(x)} <span class="sub">${x.is_remixed?"· Clean IP":""}</span></h3><dl><dt>${t("name")}</dt><dd>${esc(x.name||"")}</dd><dt>${t("server")}</dt><dd>${esc(x.server)}</dd><dt>Port</dt><dd>${esc(x.port)}</dd><dt>${t("ping")}</dt><dd>${x.tcp_ping_ms?Math.round(x.tcp_ping_ms)+" ms":"—"}</dd><dt>${t("origin")}</dt><dd>${esc((x.source||"").split("/")[0])}</dd></dl><div class="btns"><button class="gb" id="dq">QR</button><button class="pill" id="dc">${t("copy")}</button></div>`;
 $("#dc").onclick=()=>copy(x.config);$("#dq").onclick=()=>showQR(x.config)}
function showQR(s){$("#qimg").src="https://api.qrserver.com/v1/create-qr-code/?size=280x280&margin=6&data="+encodeURIComponent(s);$("#qtxt").textContent=s;$("#qr").classList.add("show");$("#qcopy").onclick=()=>copy(s)}
function dl(name,text){const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([text],{type:"text/plain"}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000)}
let mine=[];
function renderWg(){const L=[...mine,...D.configs.filter(x=>x.protocol==="wireguard")];
 $("#wgList").innerHTML=L.map((x,i)=>`<div class="card wgc"><div class="coin"><i>WG</i>${esc(x.server)}<small>:${esc(x.port)}</small></div><div class="sub latin">${x.mine?"Personal":"Cloudflare WARP"}</div><div class="btns"><button class="pill sm" data-wc="${i}">${t("copy")}</button><button class="ghost" data-wd="${i}">${t("download")}</button><button class="ghost" data-wq="${i}">QR</button></div></div>`).join("")||`<div class="empty">${t("nowg")}</div>`;
 $$("[data-wc]").forEach(b=>b.onclick=()=>copy(L[b.dataset.wc].config));$$("[data-wd]").forEach(b=>b.onclick=()=>dl("Xfinder-"+b.dataset.wd+".conf",L[b.dataset.wd].conf));$$("[data-wq]").forEach(b=>b.onclick=()=>showQR(L[b.dataset.wq].conf))}
const b64=u8=>btoa(String.fromCharCode(...u8));
// X25519 خالص JS (BigInt) برای مرورگرهایی که WebCrypto آن را پشتیبانی نمی‌کنند؛ با بردارهای RFC 7748 تست شده.
const XP=(1n<<255n)-19n,xm=a=>((a%XP)+XP)%XP,xle=u=>{let n=0n;for(let i=u.length-1;i>=0;i--)n=(n<<8n)|BigInt(u[i]);return n};
function xpow(b,e){let r=1n;b=xm(b);while(e>0n){if(e&1n)r=r*b%XP;b=b*b%XP;e>>=1n}return r}
function x25519(k,u){const kk=Uint8Array.from(k);kk[0]&=248;kk[31]&=127;kk[31]|=64;const kn=xle(kk),x1=xle(u)&((1n<<255n)-1n);let x2=1n,z2=0n,x3=x1,z3=1n,sw=0n;
 for(let t=254n;t>=0n;t--){const bit=(kn>>t)&1n;sw^=bit;if(sw){[x2,x3]=[x3,x2];[z2,z3]=[z3,z2]}sw=bit;
  const a=xm(x2+z2),aa=xm(a*a),b=xm(x2-z2),bb=xm(b*b),e=xm(aa-bb),c=xm(x3+z3),d=xm(x3-z3),da=xm(d*a),cb=xm(c*b);
  x3=xm((da+cb)*(da+cb));z3=xm(x1*xm((da-cb)*(da-cb)));x2=xm(aa*bb);z2=xm(e*(aa+121665n*e))}
 if(sw){[x2,x3]=[x3,x2];[z2,z3]=[z3,z2]}
 let r=xm(x2*xpow(z2,XP-2n)),o=new Uint8Array(32);for(let i=0;i<32;i++){o[i]=Number(r&255n);r>>=8n}return o}
async function wgKeys(){
 try{if(window.crypto&&crypto.subtle){const kp=await crypto.subtle.generateKey({name:"X25519"},true,["deriveBits"]);
  return{priv:new Uint8Array(await crypto.subtle.exportKey("pkcs8",kp.privateKey)).slice(-32),pub:new Uint8Array(await crypto.subtle.exportKey("raw",kp.publicKey))}}}catch{}
 const priv=crypto.getRandomValues(new Uint8Array(32));priv[0]&=248;priv[31]&=127;priv[31]|=64;const base=new Uint8Array(32);base[0]=9;return{priv,pub:x25519(priv,base)}}
const CF_REG="https://api.cloudflareclient.com/v0a2158/reg";
const CF_ROUTES=[u=>u,u=>"https://corsproxy.io/?url="+encodeURIComponent(u),u=>"https://api.codetabs.com/v1/proxy/?quest="+encodeURIComponent(u)];
async function cfRegister(body){let last;for(const route of CF_ROUTES){try{const ctl=new AbortController(),tm=setTimeout(()=>ctl.abort(),12000);
  const r=await fetch(route(CF_REG),{method:"POST",headers:{"Content-Type":"application/json","CF-Client-Version":"a-6.3-1922"},body,signal:ctl.signal});clearTimeout(tm);
  if(!r.ok)throw new Error("HTTP "+r.status);const j=await r.json();if(j&&j.config&&j.config.peers&&j.config.interface)return j.config;throw new Error("bad response")}catch(e){last=e}}throw last||new Error("register failed")}
let wgBusy=false;
async function genWg(){if(wgBusy)return;wgBusy=true;const btn=$("#genWg");btn.disabled=true;toast(t("genwait"));
 try{if(typeof BigInt==="undefined"&&!(window.crypto&&crypto.subtle))throw new Error("no crypto");
  const {priv,pub}=await wgKeys();
  const c=await cfRegister(JSON.stringify({key:b64(pub),install_id:"",fcm_token:"",type:"Android",model:"PC",locale:"en_US",warp_enabled:true,tos:new Date().toISOString()}));
  const ips=D.configs.filter(x=>x.is_remixed&&x.tcp_ping_ms).map(x=>x.server);const host=ips[Math.floor(Math.random()*ips.length)]||"engage.cloudflareclient.com";
  const conf=`[Interface]\nPrivateKey = ${b64(priv)}\nAddress = ${c.interface.addresses.v4}/32, ${c.interface.addresses.v6}/128\nDNS = 1.1.1.1\nMTU = 1280\n\n[Peer]\nPublicKey = ${c.peers[0].public_key}\nAllowedIPs = 0.0.0.0/0, ::/0\nEndpoint = ${host}:2408\nPersistentKeepalive = 25\n`;
  mine.unshift({server:host,port:2408,conf,config:conf,mine:true,protocol:"wireguard"});renderWg();toast(t("genok"))}
 catch(e){console.warn("wg",e);toast(t("genfail"))}finally{wgBusy=false;btn.disabled=false}}
function renderSources(){const L=D.source_list&&D.source_list.length?D.source_list:[];$("#srcList").innerHTML=L.map(s=>`<div class="card"><div><b class="latin">${esc(s.name)}</b><div class="sub">${t("count")}: <span class="num">${s.count}</span></div></div><span class="${s.ok?"chip":"chipg"}">${s.trust}</span></div>`).join("")||`<div class="empty">—</div>`}
const REPO="https://github.com/imatixofficel/Xfinder";
function renderDonate(){const L=(D.donations||[]).filter(d=>new Date(d.expires_at)>Date.now());$("#navDon").textContent=L.length;
 $("#donList").innerHTML=L.map((d,i)=>{const ms=new Date(d.expires_at)-Date.now(),h=Math.max(0,Math.floor(ms/36e5)),m=Math.max(0,Math.floor(ms%36e5/6e4));
  return`<div class="card dcard">${d.ad?`<div class="ad">${esc(d.ad)}</div>`:""}<div class="left">${t("left")}: ${h}${t("hours")} ${m}${t("min")}</div>${d.configs.map((c,j)=>`<div class="dcfg"><b title="${esc(c.name)}">${esc(c.name)}</b><span class="pp ${pcls(c.ping)}">${c.ping?Math.round(c.ping)+" ms":"—"}</span><div class="btns"><button class="pill sm" data-dc="${i}:${j}">${t("copy")}</button><button class="ghost" data-dq="${i}:${j}">QR</button></div></div>`).join("")}</div>`}).join("")||`<div class="empty">${t("don_empty")}</div>`;
 const pick=a=>{const[i,j]=a.split(":");return L[i].configs[j].config};
 $$("[data-dc]").forEach(b=>b.onclick=()=>copy(pick(b.dataset.dc)));$$("[data-dq]").forEach(b=>b.onclick=()=>showQR(pick(b.dataset.dq)))}
$("#donSend").onclick=()=>{const cfgs=($("#donCfg").value.match(/(?:vless|vmess|trojan|ss|hysteria2):\/\/[^\s"'<>]+/gi)||[]).slice(0,3);if(!cfgs.length){toast(t("don_nocfg"));return}
 const ad=$("#donAd").value.replace(/[<>]/g,"").trim().slice(0,200);
 const url=REPO+"/issues/new?"+new URLSearchParams({template:"donate.yml",title:"Donate: "+cfgs.length+" config(s)",configs:cfgs.join("\n"),ad});
 if(url.length>7000){copy(cfgs.join("\n"));window.open(REPO+"/issues/new?template=donate.yml","_blank","noopener");toast(t("don_long"))}else window.open(url,"_blank","noopener")};
const topLink=()=>base+"output/top20.txt";
function openTop(){const L=D.configs.filter(x=>x.rank).sort((a,b)=>a.rank-b.rank);
 $("#topInfo").textContent=L.length?t("top_info"):t("top_none");$("#topLink").textContent=topLink();
 $("#topList").innerHTML=L.map(x=>`<div class="row"><span class="rk">${x.rank}</span><div style="min-width:0"><b class="latin nm">${esc(x.name)}</b><small class="latin">${esc(x.server)}:${esc(x.port)}</small></div><span class="pp ${pcls(x.http_ping_ms||x.tcp_ping_ms)}" style="margin-inline-start:auto">${Math.round(x.http_ping_ms||x.tcp_ping_ms||0)} ms</span></div>`).join("");
 $("#topCopy").onclick=()=>copy(topLink());$("#topAll").onclick=()=>copy(L.map(x=>x.config).join("\n"));$("#topQr").onclick=()=>{$("#topm").classList.remove("show");showQR(topLink())};
 $("#topm").classList.add("show")}
$("#topBtn").onclick=async()=>{await load();renderAll();openTop()};
$("#topx").onclick=()=>$("#topm").classList.remove("show");$("#topm").onclick=e=>{if(e.target.id==="topm")e.target.classList.remove("show")};
// نصب وب‌اپ (PWA)
let dip=null;addEventListener("beforeinstallprompt",e=>{e.preventDefault();dip=e});
addEventListener("appinstalled",()=>{dip=null;toast(t("inst_done"));$("#install").style.display="none"});
if(matchMedia("(display-mode: standalone)").matches||navigator.standalone)$("#install").style.display="none";
$("#install").onclick=async()=>{if(dip){dip.prompt();try{await dip.userChoice}catch{}dip=null;return}
 const ios=/iphone|ipad|ipod/i.test(navigator.userAgent)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1);
 $("#iosTxt").textContent=ios?t("ios_help"):t("and_help");$("#iosm").classList.add("show");document.body.classList.remove("nav-open")};
$("#iosx").onclick=()=>$("#iosm").classList.remove("show");$("#iosm").onclick=e=>{if(e.target.id==="iosm")e.target.classList.remove("show")};
if("serviceWorker" in navigator&&/^https?:$/.test(location.protocol))addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));
function renderAll(){renderStats();renderDonate();renderBars();renderProtos();mountTable($("#t1"),8);mountTable($("#t2"),30);renderDetail();renderWg();renderSources()}
// navigation + hamburger
const mob=matchMedia("(max-width:900px)");
$("#burger").onclick=()=>document.body.classList.toggle(mob.matches?"nav-open":"nav-collapsed");
$("#scrim").onclick=()=>document.body.classList.remove("nav-open");
$$(".nav[data-go]").forEach(b=>b.onclick=()=>{$$(".nav").forEach(x=>x.classList.remove("on"));b.classList.add("on");$$(".sec").forEach(x=>x.classList.remove("on"));$("#"+b.dataset.go).classList.add("on");$("#crumb").textContent=b.querySelector("span").textContent;document.body.classList.remove("nav-open");scrollTo({top:0})});
$("#gs").oninput=e=>{const v=e.target.value;document.querySelector('[data-go="configs"]').click();const i=$("#t2 input");if(i){i.value=v;i.dispatchEvent(new Event("input"))}};
const sw=()=>{lang=lang==="fa"?"en":"fa";applyLang()};$("#lang").onclick=sw;$("#lang2").onclick=sw;
$("#refresh").onclick=async()=>{await load();renderAll();toast(t("refreshed"))};
$("#genWg").onclick=genWg;$("#qx").onclick=()=>$("#qr").classList.remove("show");$("#qr").onclick=e=>{if(e.target.id==="qr")e.target.classList.remove("show")};
const subs=()=>["all","vless","vmess","trojan","ss","hysteria2","wireguard"].map(p=>base+"output/"+p+".txt");
$("#copySub").onclick=()=>copy(base+"output/all.txt");$("#subLinks").onclick=()=>copy(subs().join("\n"));
// loader: سریع، حداکثر ۲.۵ ثانیه
const bar=$("#bar");let p=0;const tick=setInterval(()=>{p=Math.min(90,p+8);bar.style.width=p+"%"},120);
const hide=()=>{clearInterval(tick);bar.style.width="100%";setTimeout(()=>{$("#loader").classList.add("hide");setTimeout(()=>$("#loader").remove(),500)},250)};
const minWait=new Promise(r=>setTimeout(r,1500)),cap=setTimeout(hide,2500);
applyLang();
load().then(()=>{renderAll()}).finally(()=>minWait.then(()=>{clearTimeout(cap);hide()}));
