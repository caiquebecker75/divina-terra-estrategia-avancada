(function(){
  'use strict';
  const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
  const stage=$('#stage'),telas=$$('.tela'),prog=$('#prog i'),cont=$('#cont'),fala=$('#fala'),sum=$('#sumario'),caixa=$('#caixa');
  const modoPdf=new URLSearchParams(location.search).has('pdf');
  if(modoPdf)document.documentElement.classList.add('pdf');
  const total=telas.length,dd=n=>String(n).padStart(2,'0');let atual=-1,verFala=false;
  function escala(){stage.style.transform='scale('+Math.min(innerWidth/1600,innerHeight/900)+')';}
  addEventListener('resize',escala);escala();
  function contar(el){const alvo=+el.dataset.conta;if(modoPdf){el.textContent=alvo;return;}const t0=performance.now();(function p(t){const f=Math.min(1,(t-t0)/1100);el.textContent=Math.round(alvo*(1-Math.pow(1-f,3)));if(f<1)requestAnimationFrame(p);})(t0);}
  function ir(n){n=Math.max(0,Math.min(total-1,n));if(n===atual)return;if(atual>=0)telas[atual].classList.remove('ativa');atual=n;const t=telas[n];t.classList.add('ativa');
    stage.classList.toggle('escuro',t.classList.contains('tema-escuro'));stage.classList.toggle('fundo-aveia',t.classList.contains('tema-aveia'));
    prog.style.width=((n+1)/total*100)+'%';cont.textContent=dd(n+1)+' / '+dd(total);$('#ant').disabled=n===0;$('#prox').disabled=n===total-1;
    t.querySelectorAll('[data-conta]').forEach(contar);$$('#sumLista button').forEach(b=>b.classList.toggle('atual',+b.dataset.i===n));
    history.replaceState(null,'','#'+(n+1));mostrarFala();}
  function mostrarFala(){const f=telas[atual].dataset.fala||'';fala.textContent=f;fala.classList.toggle('on',verFala&&!!f);}
  $('#ant').addEventListener('click',e=>{e.stopPropagation();ir(atual-1);});
  $('#prox').addEventListener('click',e=>{e.stopPropagation();ir(atual+1);});
  addEventListener('hashchange',()=>{const n=parseInt(location.hash.slice(1),10);if(!isNaN(n))ir(n-1);});
  const lista=$('#sumLista');
  telas.forEach((t,i)=>{const li=document.createElement('li'),b=document.createElement('button');b.innerHTML='<b>'+dd(i+1)+'</b>'+t.dataset.titulo;b.dataset.i=i;b.addEventListener('click',e=>{e.stopPropagation();sum.classList.remove('aberto');setTimeout(()=>ir(i),60);});li.appendChild(b);lista.appendChild(li);});
  $$('[data-sumario]').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();sum.classList.add('aberto');}));
  $('.fechar',sum).addEventListener('click',e=>{e.stopPropagation();sum.classList.remove('aberto');});
  sum.addEventListener('click',e=>e.stopPropagation());
  $$('[data-amplia]').forEach(i=>i.addEventListener('click',e=>{e.stopPropagation();$('#cxImg').src=i.src;caixa.classList.add('aberta');}));
  caixa.addEventListener('click',e=>{e.stopPropagation();caixa.classList.remove('aberta');});
  addEventListener('keydown',e=>{
    if(caixa.classList.contains('aberta')){if(e.key==='Escape')caixa.classList.remove('aberta');return;}
    if(sum.classList.contains('aberto')){if(e.key==='Escape')sum.classList.remove('aberto');return;}
    if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();ir(atual+1);}
    else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();ir(atual-1);}
    else if(e.key==='Home')ir(0);else if(e.key==='End')ir(total-1);
    else if(e.key==='n'||e.key==='N'){verFala=!verFala;mostrarFala();}
    else if(e.key==='m'||e.key==='M')sum.classList.toggle('aberto');
  });
  /* cursor em dois tons, visível sobre todas as cores */
  if(matchMedia('(pointer:fine)').matches&&!modoPdf){document.body.classList.add('tem-mouse');const c=$('#cursor'),a=$('#anel');let x=0,y=0,ax=0,ay=0;
    addEventListener('mousemove',e=>{x=e.clientX;y=e.clientY;c.style.transform='translate('+x+'px,'+y+'px)';a.classList.toggle('gr',!!e.target.closest('a,button,[data-amplia]'));});
    (function p(){ax+=(x-ax)*.25;ay+=(y-ay)*.25;a.style.transform='translate('+ax+'px,'+ay+'px)';requestAnimationFrame(p);})();}
  /* entrada escalonada */
  telas.forEach(t=>{[...t.children].forEach((el,i)=>{if(!el.matches('.fonte,.ft,img')){el.classList.add('ent');el.style.setProperty('--i',i);}});});
  const n0=parseInt(location.hash.slice(1),10);ir(isNaN(n0)?0:n0-1);
})();
