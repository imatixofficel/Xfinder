const API={data:null};
async function loadData(){
  try{
    const r=await fetch("data/configs.json?ts="+Date.now(),{cache:"no-store",signal:AbortSignal.timeout(3500)});
    if(!r.ok)throw new Error("HTTP "+r.status);
    API.data=await r.json(); return API.data;
  }catch(e){
    API.data={updated_at:new Date().toISOString(),stats:{total:0,alive:0,remixed:0,avg_ping:0},sources:{total:0,active:0,dead_removed:0},configs:[]};
    return API.data;
  }
}
