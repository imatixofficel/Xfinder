document.addEventListener("DOMContentLoaded",async()=>{
  if(localStorage.getItem("xfinder_theme")==="dark")document.body.classList.add("dark");
  initUI();
  await runLoader();
  await bootData();
});