async function init(){
  // اول رابط را بالا می‌آوریم؛ هیچ API نباید باعث گیر کردن صفحه شود.
  applyLang(currentLang||((navigator.language||"").toLowerCase().startsWith("fa")?"fa":"en"));
  detectLanguage().catch(()=>{});
  loadData().then(()=>renderAll()).catch(()=>renderAll());

  $$(".nav-item").forEach(b=>b.addEventListener("click",()=>{
    $$(".nav-item").forEach(x=>x.classList.remove("active"));b.classList.add("active");
    $$(".section").forEach(x=>x.classList.remove("active"));$("#"+b.dataset.section).classList.add("active");
    $("#pageTitle").textContent=b.querySelector("b").textContent;$("#sidebar").classList.remove("open");
  }));
  $("#hamburger").onclick=()=>$("#sidebar").classList.toggle("open");
  $("#searchInput").oninput=renderTable;$("#protocolFilter").onchange=renderTable;
  $("#refreshBtn").onclick=async()=>{await loadData();renderAll();toast(currentLang==="fa"?"داده‌ها به‌روزرسانی شد":"Data refreshed")};
  const toggle=()=>{document.body.classList.toggle("light");localStorage.setItem("xfinder_theme",document.body.classList.contains("light")?"light":"dark")};
  if(localStorage.getItem("xfinder_theme")==="light")document.body.classList.add("light");
  $("#themeToggle").onclick=toggle;$("#themeToggle2").onclick=toggle;
  const lang=()=>applyLang(currentLang==="fa"?"en":"fa");$("#langToggle").onclick=lang;$("#langToggle2").onclick=lang;
  $("#closeModal").onclick=()=>$("#qrModal").classList.remove("show");
  $("#qrModal").onclick=e=>{if(e.target.id==="qrModal")e.currentTarget.classList.remove("show")};
}
document.addEventListener("DOMContentLoaded",init);

document.addEventListener("DOMContentLoaded",()=>{
  const g=document.getElementById("globalSearch");
  if(g)g.addEventListener("input",()=>{
    const q=g.value.trim();
    const input=document.getElementById("searchInput");
    if(input){input.value=q;document.querySelector('[data-section="configs"]')?.click();renderTable();}
  });
});
