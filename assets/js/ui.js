let allConfigs=[], currentData=null;
function pingClass(p){return p<80?"ping-good":p<=150?"ping-mid":"ping-bad"}
function escapeHtml(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
function renderStats(d){
  document.getElementById("stat-total").textContent=d.stats.total??0;
  document.getElementById("stat-alive").textContent=d.stats.alive??0;
  document.getElementById("stat-remixed").textContent=d.stats.remixed??0;
  document.getElementById("stat-ping").textContent=(d.stats.avg_ping??0)+" ms";
  document.getElementById("updated-at").textContent=formatDate(d.updated_at);
  document.getElementById("stats-json").textContent=JSON.stringify(d.stats,null,2);
  const s=d.sources||{}; document.getElementById("table-summary").textContent=`${s.active??0} / ${s.total??0} ${currentLang==="fa"?"منبع فعال":"active sources"}`;
}
function renderSources(d){
  const box=document.getElementById("sources-box"); box.innerHTML="";
  (d.source_list||[]).forEach(x=>{const el=document.createElement("div");el.className="source-item";el.innerHTML=`<b>${escapeHtml(x.name||x.type||"Source")}</b><br><a href="${escapeHtml(x.url||"#")}" target="_blank" rel="noopener">${escapeHtml(x.url||"")}</a>`;box.appendChild(el)});
  if(!box.children.length)box.innerHTML=`<div class="muted">${currentLang==="fa"?"فهرست منابع در فایل داده ثبت نشده است.":"Source list is not included in the data file."}</div>`;
}
function renderTable(){
  const q=document.getElementById("search").value.trim().toLowerCase(), proto=document.getElementById("protocol-filter").value;
  const rows=allConfigs.filter(x=>(proto==="all"||x.protocol===proto)&&(`${x.server} ${x.country} ${x.protocol}`.toLowerCase().includes(q)));
  const body=document.getElementById("configs-body"), empty=document.getElementById("empty-state"); body.innerHTML="";
  rows.slice(0,500).forEach((x,i)=>{
    const tr=document.createElement("tr"), p=Number(x.ping_ms)||0, c=x.country_flag||x.country||"—";
    tr.innerHTML=`<td><span class="badge ${escapeHtml(x.protocol)}">${escapeHtml(x.protocol).toUpperCase()}</span></td>
      <td>${escapeHtml(x.server)}:${escapeHtml(x.port)}</td><td class="${pingClass(p)}">${p? p+" ms":"—"}</td><td>${escapeHtml(c)}</td>
      <td><button class="action-btn" data-copy="${i}">${t("copy")}</button><button class="action-btn" data-qr="${i}">QR</button></td>`;
    body.appendChild(tr);
  });
  empty.classList.toggle("hidden",rows.length>0);
  document.getElementById("table-summary").textContent=`${rows.length} ${currentLang==="fa"?"مورد":"items"}`;
  body.querySelectorAll("[data-copy]").forEach(b=>b.onclick=()=>copyConfig(rows[+b.dataset.copy]));
  body.querySelectorAll("[data-qr]").forEach(b=>b.onclick=()=>showQr(rows[+b.dataset.qr]));
}
async function copyConfig(x){
  try{await navigator.clipboard.writeText(x.config||"");toast(t("copied"))}catch{toast("Clipboard unavailable")}
}
function showQr(x){
  const value=encodeURIComponent(x.config||"");
  window.open(`https://quickchart.io/qr?text=${value}&size=320`,`_blank`,`noopener`);
}
function toast(s){const e=document.getElementById("toast");e.textContent=s;e.classList.add("show");setTimeout(()=>e.classList.remove("show"),1600)}
function initUI(){
  document.querySelectorAll(".nav-item").forEach(b=>b.onclick=()=>{
    document.querySelectorAll(".nav-item").forEach(x=>x.classList.remove("active"));b.classList.add("active");
    document.querySelectorAll(".page-section").forEach(x=>x.classList.remove("active"));
    document.getElementById("section-"+b.dataset.section).classList.add("active");
    document.getElementById("page-title").textContent=t(b.dataset.section);
    document.getElementById("sidebar").classList.remove("open");
  });
  document.getElementById("search").oninput=renderTable;
  document.getElementById("protocol-filter").onchange=renderTable;
  document.getElementById("menu-toggle").onclick=()=>document.getElementById("sidebar").classList.toggle("open");
  document.getElementById("lang-toggle").onclick=()=>{applyLanguage(currentLang==="fa"?"en":"fa");renderStats(currentData);renderSources(currentData);renderTable()};
  document.getElementById("theme-toggle").onclick=()=>{document.body.classList.toggle("dark");localStorage.setItem("xfinder_theme",document.body.classList.contains("dark")?"dark":"light")};
}
async function bootData(){
  currentData=await loadData();allConfigs=currentData.configs||[];renderStats(currentData);renderSources(currentData);renderTable();
}
