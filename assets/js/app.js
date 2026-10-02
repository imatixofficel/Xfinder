async function init(){
  await detectLanguage();
  const d=await loadData(); renderAll();
  $$(".nav-item").forEach(b=>b.addEventListener("click",()=>{
    $$(".nav-item").forEach(x=>x.classList.remove("active"));b.classList.add("active");
    $$(".section").forEach(x=>x.classList.remove("active"));$("#"+b.dataset.section).classList.add("active");
    $("#pageTitle").textContent=b.querySelector("b").textContent;$("#sidebar").classList.remove("open");
  }));
  $("#hamburger").onclick=()=>$("#sidebar").classList.toggle("open");
  $("#searchInput").oninput=renderTable;$("#protocolFilter").onchange=renderTable;
  $("#refreshBtn").onclick=async()=>{await loadData();renderAll();toast("بروزرسانی شد")};
  const toggle=()=>{document.body.classList.toggle("light");localStorage.setItem("xfinder_theme",document.body.classList.contains("light")?"light":"dark")};
  if(localStorage.getItem("xfinder_theme")==="light")document.body.classList.add("light");
  $("#themeToggle").onclick=toggle;$("#themeToggle2").onclick=toggle;
  const lang=()=>applyLang(currentLang==="fa"?"en":"fa");$("#langToggle").onclick=lang;$("#langToggle2").onclick=lang;
  $("#closeModal").onclick=()=>$("#qrModal").classList.remove("show");
  $("#qrModal").onclick=e=>{if(e.target.id==="qrModal")e.currentTarget.classList.remove("show")};
  setTimeout(finishLoader,600);
}
document.addEventListener("DOMContentLoaded",init);
