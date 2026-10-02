// Xfinder local Spokes loader — نسخه بدون وابستگی خارجی
export function createSpokesLoader(root){
  const el=document.createElement('div');
  el.className='spokes';
  for(let i=0;i<8;i++) el.appendChild(document.createElement('i'));
  root.appendChild(el);
  return el;
}
