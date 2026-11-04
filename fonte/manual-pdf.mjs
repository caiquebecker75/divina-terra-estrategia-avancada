// Gera o PDF do manual: node fonte/manual-pdf.mjs [endereço] [saída]
import { chromium } from '/Volumes/hd caique becker/Mac Caique/Projetos/ariuno-videos/node_modules/playwright/index.mjs';
const b=await chromium.launch({channel:'chrome'});const p=await b.newPage({viewport:{width:1500,height:1000}});
await p.goto((process.argv[2]||'http://localhost:4911/')+'manual.html',{waitUntil:'load'});
await p.evaluate(async()=>{document.querySelectorAll('details:not(.noprint)').forEach(d=>d.open=true);const im=[...document.images];im.forEach(i=>i.loading='eager');await Promise.race([Promise.all(im.map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r}))),new Promise(r=>setTimeout(r,120000))]);await document.fonts.ready});
await p.pdf({path:process.argv[3]||'manual-divina-terra.pdf',format:'A3',landscape:true,printBackground:true,preferCSSPageSize:true,timeout:0});
await b.close();console.log('manual pdf ok');
