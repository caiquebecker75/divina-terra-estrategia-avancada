// Calcula o zoom de cada tela para o conteúdo ocupar a área útil sem estourar (grava fonte/zoom.json).
import { chromium } from '/Volumes/hd caique becker/Mac Caique/Projetos/ariuno-videos/node_modules/playwright/index.mjs';
import { writeFileSync } from 'node:fs';
const b=await chromium.launch({channel:'chrome'});const pg=await b.newPage({viewport:{width:1600,height:900}});
await pg.goto('http://localhost:4911/book.html?pdf=1#1',{waitUntil:'networkidle'});await pg.evaluate(()=>document.fonts.ready);
await pg.addStyleTag({content:'.pdf .so-tela{display:inline-flex!important}'});
const res=await pg.evaluate(async()=>{
  const telas=[...document.querySelectorAll('.tela')],out={};
  const AREA=900-78;
  for(let i=0;i<telas.length;i++){
    const t=telas[i],c=t.querySelector('.corpo');if(!c)continue;
    t.classList.add('ativa');const fonte=t.querySelector('.fonte');
    const topoFonte=fonte?fonte.getBoundingClientRect().top:846;
    const lim=topoFonte-8-78;
    const g=t.querySelector('[data-abas]');const bts=g?[...g.querySelectorAll('.aba')]:[];
    const on=g?(bts.find(x=>x.classList.contains('on'))||{}).dataset?.k:null;
    const mede=()=>{const r0=c.getBoundingClientRect();let h=0,w=0;for(const e of c.querySelectorAll('*')){if(e.closest('svg')&&e.tagName!=='svg')continue;const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden')continue;if(e.offsetParent===null&&s.position!=='fixed')continue;const r=e.getBoundingClientRect();if(!r.width)continue;h=Math.max(h,r.bottom-r0.top);w=Math.max(w,r.right-r0.left);const sc=e.scrollWidth-e.clientWidth;}
      return {h,w};};
    const estados=(g&&!g.hasAttribute('data-sem-pdf'))?bts.map(x=>x.dataset.k):[null];
    const poe=z=>{c.style.zoom=z;c.style.width=(1280/z)+'px';c.style.left=(160/z)+'px';c.style.top=(78/z)+'px';};const cabe=z=>{poe(z);let ok=true,hm=0;for(const k of estados){if(k)g.__abre(k);const m=mede();hm=Math.max(hm,m.h);if(m.h>lim||m.w>1280+2)ok=false;}return {ok,hm};};
    let lo=.66,hi=.87,best=.66;for(let n=0;n<7;n++){const mid=(lo+hi)/2;if(cabe(mid).ok){best=mid;lo=mid;}else hi=mid;}
    best=Math.floor(best*100)/100;const f=cabe(best);const sobra=Math.max(0,lim-f.hm);
    if(on&&g)g.__abre(on);poe(best);
    out[i+1]=[best,Math.round(sobra/2)];t.classList.remove('ativa');
  }
  return out;});
writeFileSync(new URL('zoom.json',import.meta.url),JSON.stringify(res));
const v=Object.values(res).map(x=>x[0]);console.log('zoom min',Math.min(...v),'max',Math.max(...v));console.log(Object.entries(res).map(([k,a])=>k+':'+a[0]+'/'+a[1]).join(' '));
await b.close();
