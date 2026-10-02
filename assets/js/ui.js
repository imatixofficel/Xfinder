const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
function esc(v){return String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function toast(t){const x=$("#toast");x.textContent=t;x.classList.add("show");setTimeout(()=>x.classList.remove("show"),1800)}
function pingClass(n){n=Number(n||0);return n<80?"good":n<=150?"warn":"bad"}
function renderStats(d){
 $("#statTotal").textContent=d.stats?.total??0;$("#statAlive").textContent=d.stats?.alive??0;$("#statRemixed").textContent=d.stats?.remixed??0;$("#statPing").textContent=d.stats?.avg_ping??0;
 $("#updatedAt").textContent=d.updated_at?new Date(d.updated_at).toLocaleString(currentLang==="fa"?"fa-IR":"en-US"):"—";
 $("#navConfigCount").textContent=(d.configs||[]).length;
}
function renderChart(d){const values=(d.configs||[]).slice(0,20).map(x=>Math.max(18,Math.min(100,160-(Number(x.tcp_ping_ms)||100)/2)));$("#chart").innerHTML=(values.length?values:Array(14).fill(35)).map(v=>`<div class="bar" style="height:${v*2}px"></div>`).join("")}
function renderProtocols(d){const counts={vless:0,vmess:0,trojan:0,ss:0,hysteria2:0};(d.configs||[]).forEach(x=>counts[x.protocol]=(counts[x.protocol]||0)+1);const max=Math.max(1,...Object.values(counts));$("#protocolBars").innerHTML=Object.entries(counts).map(([k,v])=>`<div class="protocol-row"><div class="protocol-label"><span>${k.toUpperCase()}</span><b>${v}</b></div><div class="protocol-track"><div class="protocol-fill ${k}" style="width:${v/max*100}%"></div></div></div>`).join("")}
function filteredConfigs(){const q=$("#searchInput").value.toLowerCase().trim(),p=$("#protocolFilter").value;return(API.data?.configs||[]).filter(x=>(p==="all"||x.protocol===p)&&(!q||`${x.server} ${x.port} ${x.country} ${x.protocol} ${x.config}`.toLowerCase().includes(q)))}
function renderTable(){
 const rows=filteredConfigs();
 $("#configRows").innerHTML=rows.length?rows.map((x,i)=>`<tr><td><span class="proto-badge ${esc(x.protocol)}">${esc((x.protocol||"").toUpperCase())}</span></td><td class="server-cell">${esc(x.server)}:${esc(x.port)}</td><td class="ping ${pingClass(x.tcp_ping_ms)}">${esc(x.tcp_ping_ms??"—")} ms</td><td class="ping ${pingClass(x.http_ping_ms)}">${esc(x.http_ping_ms??"—")} ms</td><td>${esc(x.country_flag||"")} ${esc(x.country||"—")}</td><td class="good">${esc(x.trust_score??"—")}</td><td><div class="action"><button onclick="copyConfig(${i})">کپی</button><button onclick="showQR(${i})">QR</button></div></td></tr>`).join(""):`<tr><td colspan="7" class="empty-state"><strong>${API.error?"فایل داده قابل دسترسی نیست":"هنوز کانفیگ سالمی منتشر نشده است"}</strong><span>${API.error?"data/configs.json را بررسی کنید و Workflow را اجرا کنید.":"پس از اجرای Collector و تأیید کانفیگ‌ها، همه موارد اینجا نمایش داده می‌شوند."}</span></td></tr>`;
 const st=$("#dataStatus");if(st)st.textContent=API.data?.configs?.length?`${API.data.configs.length} کانفیگ`:(API.error?"خطای داده":"در انتظار Collector");
}
window.copyConfig=async i=>{const x=filteredConfigs()[i];if(!x)return;try{await navigator.clipboard.writeText(x.config);toast(translations[currentLang].copied)}catch{toast("Copy failed")}}
let activeQRConfig="";
window.showQR=i=>{
 const x=filteredConfigs()[i];if(!x)return;
 activeQRConfig=x.config||"";
 $("#qrServer").textContent=`${x.server||"—"}:${x.port||""} · ${(x.protocol||"").toUpperCase()}`;
 $("#qrConfig").textContent=activeQRConfig;
 $("#qrImage").src="https://api.qrserver.com/v1/create-qr-code/?size=280x280&margin=10&data="+encodeURIComponent(activeQRConfig);
 $("#qrModal").classList.add("show");
};
function renderSources(){const sources=[["Au1rxx/free-vpn-subscriptions","HTTP test priority",100],["Epodonios/v2ray-configs","5 minute source",85],["MatinGhanbari/v2ray-configs","15 minute source",85],["Delta-Kronecker/V2ray-Config","Xray-oriented source",90],["R3ZARAHIMI/tg-v2ray-configs-every2h","Country separated",80],["FreeList-V2ray-Configs","No-CF source",75]];$("#sourceGrid").innerHTML=sources.map(s=>`<article class="source-card"><div><h4>${esc(s[0])}</h4><p>${esc(s[1])}</p></div><div class="trust">${s[2]}</div></article>`).join("")}
function renderLargeStats(d){$("#statsLarge").innerHTML=[["Total",d.stats?.total??0],["Alive",d.stats?.alive??0],["Remixed",d.stats?.remixed??0],["Average TCP/HTTP",(d.stats?.avg_ping??0)+" ms"],["Active Sources",d.sources?.active??0],["Removed Sources",d.sources?.dead_removed??0]].map(x=>`<div><span>${x[0]}</span><strong>${esc(x[1])}</strong></div>`).join("")}
function renderAll(){const d=API.data||{stats:{},sources:{},configs:[]};renderStats(d);renderChart(d);renderProtocols(d);renderTable();renderSources();renderLargeStats(d)}
