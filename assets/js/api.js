async function loadData(){
  const fallback={updated_at:null,stats:{total:0,alive:0,remixed:0,avg_ping:0},sources:{total:0,active:0,dead_removed:0},configs:[]};
  try{
    const r=await fetch(`data/configs.json?ts=${Date.now()}`,{cache:"no-store"});
    if(!r.ok)throw new Error("HTTP "+r.status);
    return await r.json();
  }catch(e){console.error("خطا در دریافت داده:",e);return fallback}
}
function formatDate(v){
  if(!v)return "—";
  try{return new Intl.DateTimeFormat(currentLang==="fa"?"fa-IR":"en-US",{dateStyle:"medium",timeStyle:"short"}).format(new Date(v))}
  catch{return v}
}
