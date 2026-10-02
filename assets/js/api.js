/* لایه داده: هیچ درخواست شبکه‌ای نباید رابط کاربری را متوقف کند. */
const API={data:null,error:null,source:""};
const EMPTY_DATA={
  updated_at:null,
  stats:{total:0,alive:0,remixed:0,avg_ping:0},
  sources:{total:6,active:0,dead_removed:0},
  configs:[]
};
async function loadData(){
  const urls=["data/configs.json?ts="+Date.now(),"./data/configs.json?ts="+Date.now()];
  for(const url of urls){
    try{
      const r=await fetch(url,{cache:"no-store"});
      if(!r.ok)throw new Error("HTTP "+r.status);
      const d=await r.json();
      if(!d||!Array.isArray(d.configs))throw new Error("Invalid data");
      API.data=d;API.error=null;API.source=url;return d;
    }catch(e){API.error=e;}
  }
  API.data=structuredClone(EMPTY_DATA);
  return API.data;
}
