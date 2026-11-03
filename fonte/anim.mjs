// Confere as animações em modo normal: mede opacidade no início e no fim, e fotografa.
import { chromium } from '/Volumes/hd caique becker/Mac Caique/Projetos/ariuno-videos/node_modules/playwright/index.mjs';
const OUT=process.argv[2];const b=await chromium.launch({channel:'chrome'});const pg=await b.newPage({viewport:{width:1600,height:900}});
const erros=[];pg.on('pageerror',e=>erros.push(e.message));pg.on('console',m=>{if(m.type()==='error')erros.push(m.text())});
await pg.goto('http://localhost:4911/#2',{waitUntil:'networkidle'});
const total=await pg.evaluate(()=>document.querySelectorAll('.tela').length);const presos=[];
for(const n of [4,5,11,14,15,21,22,31,50,54,55,59,66]){
  await pg.evaluate(n=>{location.hash='#'+n},n);await pg.waitForTimeout(950);
  const cedo=await pg.evaluate(()=>{const t=document.querySelector('.tela.ativa');return t.getAnimations({subtree:true}).length});
  await pg.screenshot({path:`${OUT}/a${n}-1.jpg`,type:'jpeg',quality:60});
  await pg.waitForTimeout(2600);
  const st=await pg.evaluate(()=>{const t=document.querySelector('.tela.ativa');let z=0;t.querySelectorAll('.corpo *').forEach(e=>{const s=getComputedStyle(e);if(+s.opacity<.05&&e.offsetParent&&!e.closest('svg'))z++;});return z;});
  await pg.screenshot({path:`${OUT}/a${n}-2.jpg`,type:'jpeg',quality:60});
  console.log(n,'animacoes no inicio',cedo,'invisiveis no fim',st);
}
// navegação real por seta e clique
await pg.evaluate(()=>{location.hash='#2'});await pg.waitForTimeout(900);await pg.keyboard.press('ArrowRight');await pg.waitForTimeout(1000);console.log('seta ->',await pg.evaluate(()=>document.querySelector('#cont').textContent));
await pg.click('#trilhaTopo [data-e="4"]');await pg.waitForTimeout(1000);console.log('trilha ->',await pg.evaluate(()=>document.querySelector('.tela.ativa').dataset.titulo));
console.log('total',total,'erros',erros.slice(0,4));await b.close();
