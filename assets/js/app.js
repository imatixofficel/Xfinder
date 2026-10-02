async function init(){
 applyLang(currentLang||((navigator.language||"").toLowerCase().startsWith("fa")?"fa":"en"));
 detectLanguage().catch(()=>{});
 loadData().then(()=>renderAll()).catch(()=>renderAll());

 $$(".nav-item").forEach(b=>b.addEventListener("click",()=>{
   $$(".nav-item").forEach(x=>x.classList.remove("active"));b.classList.add("active");
   $$(".section").forEach(x=>x.classList.remove("active"));$("#"+b.dataset.section).classList.add("active");
   $("#sidebar").classList.remove("open");
 }));
 $$(".quick-card").forEach(b=>b.addEventListener("click",()=>document.querySelector(`[data-section="${b.dataset.jump}"]`)?.click()));
 $("#hamburger").onclick=()=>$("#sidebar").classList.toggle("open");
 $("#searchInput").oninput=renderTable;$("#protocolFilter").onchange=renderTable;
 $("#refreshBtn").onclick=async()=>{await loadData();renderAll();toast(currentLang==="fa"?"داده‌ها بروزرسانی شد":"Data refreshed")};

 const setTheme=()=>{document.body.classList.toggle("light");document.documentElement.classList.toggle("prelight",document.body.classList.contains("light"));localStorage.setItem("xfinder_theme",document.body.classList.contains("light")?"light":"dark")};
 if(localStorage.getItem("xfinder_theme")==="light"){document.body.classList.add("light");document.documentElement.classList.add("prelight")}
 $("#themeToggle").onclick=setTheme;$("#themeToggle2").onclick=setTheme;

 const toggleLang=()=>applyLang(currentLang==="fa"?"en":"fa");$("#langToggle").onclick=toggleLang;$("#langToggle2").onclick=toggleLang;
 $("#closeModal").onclick=()=>$("#qrModal").classList.remove("show");
 $("#qrModal").onclick=e=>{if(e.target.id==="qrModal")e.currentTarget.classList.remove("show")};
 $("#copyQrConfig").onclick=async()=>{try{await navigator.clipboard.writeText(activeQRConfig);toast(translations[currentLang].copied)}catch{}};

 const g=$("#globalSearch");if(g)g.addEventListener("input",()=>{const q=g.value.trim();const input=$("#searchInput");if(input){input.value=q;document.querySelector('[data-section="configs"]')?.click();renderTable()}});
}
document.addEventListener("DOMContentLoaded",init);
