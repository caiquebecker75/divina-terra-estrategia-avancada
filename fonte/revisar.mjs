// Fotografa cada tela (e estado de botão) e procura texto cortado ou sobreposto.
import { chromium } from '/Volumes/hd caique becker/Mac Caique/Projetos/ariuno-videos/node_modules/playwright/index.mjs';
import { mkdirSync } from 'node:fs';
const BASE=process.argv[2]||'http://localhost:4911/',OUT=process.argv[3],soEstados=process.argv[4]==='estados';
mkdirSync(OUT,{recursive:true});
const b=await chromium.launch({channel:'chrome'});const pg=await b.newPage({viewport:{width:1600,height:900}});
pg.on('pageerror',e=>console.log('ERRO',e.message));
await pg.goto(BASE+'?pdf=1#1',{waitUntil:'networkidle'});await pg.evaluate(()=>document.fonts.ready);
await pg.addStyleTag({content:'.pdf .so-tela{display:inline-flex!important}'});
const total=await pg.evaluate(()=>document.querySelectorAll('.tela').length);
const checa=()=>pg.evaluate(()=>{
  const t=document.querySelector('.tela.ativa'),m=t.querySelector('.miolo');const lim=document.querySelector('#stage').getBoundingClientRect();const out=[];
  const vis=e=>{const s=getComputedStyle(e);return s.visibility!=='hidden'&&s.display!=='none'&&e.offsetParent!==null};
  const fol=[...t.querySelectorAll('h1,h2,h3,h4,p,li,td,th,span,b,button,dd,dt,small,label,.fonte')].filter(e=>vis(e)&&e.children.length===0&&e.textContent.trim());
  const rects=fol.map(e=>{const R=document.createRange();R.selectNodeContents(e);return {e,r:R.getBoundingClientRect(),tx:e.textContent.trim().slice(0,38)}}).filter(x=>x.r.width>0);
  for(const x of rects){ if(x.r.bottom>lim.bottom-34||x.r.right>lim.right-40||x.r.left<lim.left+40||x.r.top<lim.top+50) out.push('FORA: '+x.tx+' b='+Math.round(x.r.bottom)+' r='+Math.round(x.r.right)); }
  // estouro de caixa
  for(const e of t.querySelectorAll('div,td,button,span,li')){ if(!vis(e))continue; if(e.scrollHeight>e.clientHeight+3&&getComputedStyle(e).overflow==='hidden'&&e.clientHeight>0) out.push('CORTE: '+e.className+' '+e.textContent.trim().slice(0,30)); }
  for(let i=0;i<rects.length;i++)for(let j=i+1;j<rects.length;j++){const a=rects[i],c=rects[j];if(a.e.contains(c.e)||c.e.contains(a.e))continue;
    const w=Math.min(a.r.right,c.r.right)-Math.max(a.r.left,c.r.left),h=Math.min(a.r.bottom,c.r.bottom)-Math.max(a.r.top,c.r.top);
    if(w>6&&h>5){out.push('SOBRE: '+a.tx+' x '+c.tx);if(out.length>10)return out;}}
  // alturas de grade: conteúdo interno maior que a caixa
  for(const e of t.querySelectorAll('.col,.cx,.m,.c,.lj,.o,.bloco,.des')){ if(!vis(e))continue; if(e.scrollHeight>e.clientHeight+3) out.push('ESTOURA: '+e.className+' '+e.scrollHeight+'>'+e.clientHeight+' '+e.textContent.trim().slice(0,30)); }
  const f=t.querySelector('.fonte');if(f){const fr=f.getBoundingClientRect();for(const x of rects){if(x.e===f)continue;if(x.r.bottom>fr.top+2&&x.r.top<fr.bottom&&x.r.left<fr.right&&x.r.right>fr.left){out.push('NA FONTE: '+x.tx);break;}}}
  return out;});
for(let n=1;n<=total;n++){
  await pg.evaluate(n=>{location.hash='#'+n},n);
  await pg.waitForFunction(n=>document.querySelector('#cont').textContent.startsWith(String(n).padStart(2,'0')),n);
  await pg.waitForTimeout(150);
  const tit=await pg.evaluate(()=>document.querySelector('.tela.ativa').dataset.titulo);
  const pr=await checa();if(pr.length)console.log(String(n).padStart(2,'0'),tit,JSON.stringify(pr.slice(0,6)));
  await pg.screenshot({path:`${OUT}/${String(n).padStart(2,'0')}.jpg`,type:'jpeg',quality:70});
  const est=await pg.evaluate(()=>window.__pdfEstados?window.__pdfEstados():0);
  if(est&&soEstados){await pg.evaluate(()=>document.documentElement.classList.add('estados'));for(let k=0;k<est;k++){await pg.evaluate(k=>window.__pdfEstado(k),k);await pg.waitForTimeout(120);const q=await checa();if(q.length)console.log(String(n).padStart(2,'0'),'estado',k,JSON.stringify(q.slice(0,5)));await pg.screenshot({path:`${OUT}/${String(n).padStart(2,'0')}-${k}.jpg`,type:'jpeg',quality:70});}await pg.evaluate(()=>document.documentElement.classList.remove('estados'));}
}
await b.close();console.log('fim',total);
