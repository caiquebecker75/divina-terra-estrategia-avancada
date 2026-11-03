(function(){
  'use strict';
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const stage=$('#stage'), telas=$$('.tela'), wipe=$('#wipe'), prog=$('#prog i'), cont=$('#cont'), capTxt=$('#capTxt');
  const modoPdf=new URLSearchParams(location.search).has('pdf');
  if(modoPdf)document.documentElement.classList.add('pdf');
  const reduz=matchMedia('(prefers-reduced-motion: reduce)').matches||modoPdf;
  let atual=0,emTransicao=false,pendente=null,autoAtivos=[];
  const total=telas.length, dd=n=>String(n).padStart(2,'0');
  telas.forEach(t=>{const m=document.createElement('div');m.className='miolo';const semCorpo=t.classList.contains('s-cap')||t.classList.contains('s-capa');const c=document.createElement('div');c.className='corpo';
    [...t.childNodes].forEach(n=>{if(n.nodeType===1&&n.classList.contains('sangra'))return;if(semCorpo||(n.nodeType===1&&n.classList.contains('fonte')))m.appendChild(n);else c.appendChild(n);});
    if(!semCorpo){m.insertBefore(c,m.firstChild);const z=+t.dataset.z||1,y=+t.dataset.y||0;c.style.zoom=z;c.style.width=(1488/z)+'px';c.style.left=(56/z)+'px';c.style.top=((78+y)/z)+'px';}t.appendChild(m);});
  function escala(){stage.style.transform='scale('+Math.min(innerWidth/1600,innerHeight/900)+')';}
  addEventListener('resize',escala);escala();
  function contar(el){
    const alvo=parseFloat(el.dataset.conta),casas=+el.dataset.casas||0,t0=performance.now(),dur=1200;
    const fmt=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:casas,maximumFractionDigits:casas});
    if(reduz){el.textContent=fmt.format(alvo);return;}
    (function passo(t){const p=Math.min(1,(t-t0)/dur),v=alvo*(1-Math.pow(1-p,3));el.textContent=fmt.format(v);if(p<1)requestAnimationFrame(passo);})(t0);
  }
  function aplicar(n){
    pararAutos();telas[atual].classList.remove('ativa');atual=n;const t=telas[n];t.classList.add('ativa');
    stage.classList.toggle('capa',n===0);
    capTxt.textContent=(t.dataset.cap||'').replace(/^\((\d+)\) /,'$1 · ');
    prog.style.width=((n+1)/total*100)+'%';cont.textContent=dd(n+1)+' / '+dd(total);
    $('#ant').disabled=n===0;$('#prox').disabled=n===total-1;
    t.querySelectorAll('[data-conta]').forEach(contar);
    $$('#sumLista button').forEach(b=>b.classList.toggle('atual',+b.dataset.i===n));
    history.replaceState(null,'','#'+(n+1));
    mostrarFala();iniciarAutos(t);
  }
  function ir(n){
    n=Math.max(0,Math.min(total-1,n));
    if(emTransicao){pendente=n;return;}
    if(n===atual)return;
    if(reduz||!wipe.animate||document.hidden){aplicar(n);return;}
    const dir=n>atual?1:-1,de=dir>0?'inset(0 0 0 100%)':'inset(0 100% 0 0)',meio='inset(0 0 0 0)',para=dir>0?'inset(0 100% 0 0)':'inset(0 0 0 100%)',ease='cubic-bezier(.7,0,.3,1)';
    emTransicao=true;
    wipe.animate([{clipPath:de},{clipPath:meio}],{duration:300,easing:ease,fill:'forwards'}).onfinish=()=>{aplicar(n);
      wipe.animate([{clipPath:meio},{clipPath:para}],{duration:340,easing:ease,fill:'forwards'}).onfinish=()=>{emTransicao=false;if(pendente!==null){const p=pendente;pendente=null;ir(p);}};};
  }
  addEventListener('hashchange',()=>{const n=parseInt(location.hash.slice(1),10);if(!isNaN(n))ir(n-1);});
  $('#ant').addEventListener('click',e=>{e.stopPropagation();ir(atual-1);});
  $('#prox').addEventListener('click',e=>{e.stopPropagation();ir(atual+1);});
  const indice=v=>/^\d+$/.test(v)?+v-1:telas.findIndex(t=>t.id===v);
  $$('[data-ir]').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();ir(indice(b.dataset.ir));}));
  /* sumário */
  const sum=$('#sumario'),lista=$('#sumLista');let capAnt='';
  telas.forEach((t,i)=>{
    const c=(t.dataset.cap||'').match(/^\((\d+)\) (.*)$/);
    if(c&&c[1]!==capAnt){capAnt=c[1];const h=document.createElement('li');h.className='cap-s';h.textContent=c[1]+' · '+c[2];lista.appendChild(h);}
    if(t.classList.contains('s-cap'))return;
    const li=document.createElement('li'),b=document.createElement('button');
    b.innerHTML='<b>'+dd(i+1)+'</b>'+t.dataset.titulo;b.dataset.cursor='Ir';b.dataset.i=i;
    b.addEventListener('click',e=>{e.stopPropagation();sum.classList.remove('aberto');setTimeout(()=>ir(i),60);});
    li.appendChild(b);lista.appendChild(li);
  });
  $$('[data-sumario]').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();sum.classList.add('aberto');}));
  $('.fechar',sum).addEventListener('click',e=>{e.stopPropagation();sum.classList.remove('aberto');});
  /* roteiro de fala: tecla N, só para quem apresenta */
  const fala=$('#fala');let verFala=false;
  function mostrarFala(){const f=telas[atual].dataset.fala||'';fala.textContent=f;fala.classList.toggle('on',verFala&&!!f);}
  /* teclado, clique e toque */
  addEventListener('keydown',e=>{
    if(e.target.matches('input'))return;
    if(caixa.classList.contains('aberta')){if(e.key==='Escape')caixa.classList.remove('aberta');return;}
    if(sum.classList.contains('aberto')){if(e.key==='Escape')sum.classList.remove('aberto');return;}
    if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();ir(atual+1);}
    else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();ir(atual-1);}
    else if(e.key==='Home')ir(0);else if(e.key==='End')ir(total-1);
    else if(e.key==='m'||e.key==='M')sum.classList.toggle('aberto');
    else if(e.key==='n'||e.key==='N'){verFala=!verFala;mostrarFala();}
  });
  const INTERATIVO='a,button,input,label,.amplia,[data-cursor],#sumario,.comparador,[data-abas]';
  $('#wrap').addEventListener('click',e=>{if(e.target.closest(INTERATIVO)||sum.classList.contains('aberto'))return;ir(e.clientX>innerWidth/2?atual+1:atual-1);});
  let x0=null,y0=null;
  addEventListener('touchstart',e=>{x0=e.touches[0].clientX;y0=e.touches[0].clientY;},{passive:true});
  addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0,dy=e.changedTouches[0].clientY-y0;if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)&&!e.target.closest('.comparador,input'))ir(dx<0?atual+1:atual-1);x0=null;});
  /* lightbox */
  const caixa=$('#caixa');
  $$('[data-amplia]').forEach(el=>el.addEventListener('click',e=>{e.stopPropagation();$('#cxImg').src=el.dataset.amplia;caixa.classList.add('aberta');}));
  caixa.addEventListener('click',()=>caixa.classList.remove('aberta'));
  /* cursor em dois tons */
  const cur=$('#cursor'),anel=$('#anel'),anelTxt=$('#anelTxt');let mx=innerWidth/2,my=innerHeight/2,ax=mx,ay=my;
  addEventListener('mousemove',e=>{document.body.classList.add('tem-mouse');mx=e.clientX;my=e.clientY;cur.style.transform='translate('+mx+'px,'+my+'px)';
    const a=e.target.closest('[data-cursor],a,button,.amplia,label');anel.classList.toggle('sobre',!!a);anelTxt.textContent=a?(a.dataset.cursor||''):'';},{passive:true});
  (function segue(){ax+=(mx-ax)*.2;ay+=(my-ay)*.2;anel.style.transform='translate('+ax+'px,'+ay+'px)';requestAnimationFrame(segue);})();
  addEventListener('touchstart',()=>document.body.classList.remove('tem-mouse'),{passive:true});
  /* abas: [data-abas] com botões .aba[data-k] e painéis .painel[data-k]; data-fn chama função extra */
  const FN={};
  $$('[data-abas]').forEach(g=>{
    const bts=$$('.aba',g),pns=$$('.painel',g);
    g.__abre=k=>{bts.forEach(b=>b.classList.toggle('on',b.dataset.k===k));pns.forEach(p=>p.classList.toggle('on',p.dataset.k===k));if(g.dataset.fn&&FN[g.dataset.fn])FN[g.dataset.fn](k,g);};
    bts.forEach(b=>{b.dataset.cursor=b.dataset.cursor||'Abrir';b.addEventListener('click',e=>{e.stopPropagation();g.__abre(b.dataset.k);});});
  });
  /* temporizador: abre sozinho, um por vez; o primeiro clique de verdade para */
  const leitura=t=>Math.max(4500,Math.min(12000,3000+String(t||'').replace(/\s+/g,' ').trim().length*38));
  function pararAutos(){autoAtivos.forEach(clearTimeout);autoAtivos=[];$$('.relogio-auto').forEach(r=>r.remove());}
  function iniciarAutos(t){
    if(modoPdf)return;
    $$('[data-abas]',t).forEach(g=>{
      if(g.hasAttribute('data-sem-auto'))return;
      const bts=$$('.aba',g),pns=$$('.painel',g);if(bts.length<2)return;
      let i=Math.max(0,bts.findIndex(b=>b.classList.contains('on')));
      const ms=k=>{const p=pns.find(x=>x.dataset.k===bts[k].dataset.k);return leitura(p?p.textContent:bts[k].textContent);};
      function rel(k,d){$$('.relogio-auto',g).forEach(r=>r.remove());const r=document.createElement('i');r.className='relogio-auto';bts[k].appendChild(r);r.style.transitionDuration=d+'ms';void r.offsetWidth;r.classList.add('corre');}
      function passo(){i=(i+1)%bts.length;g.__abre(bts[i].dataset.k);const d=ms(i);rel(i,d);autoAtivos.push(setTimeout(passo,d));}
      const d=ms(i);rel(i,d);autoAtivos.push(setTimeout(passo,d));
    });
  }
  stage.addEventListener('pointerdown',e=>{if(e.isTrusted&&e.target.closest('.tela.ativa'))pararAutos();},true);
  /* PDF: uma página por botão */
  window.__pdfEstados=()=>{const g=$('[data-abas]',telas[atual]);return g&&!g.hasAttribute('data-sem-pdf')?$$('.aba',g).length:0;};
  window.__pdfEstado=k=>{const g=$('[data-abas]',telas[atual]);g.__abre($$('.aba',g)[k].dataset.k);};
  /* comparador antes e depois */
  $$('.comparador').forEach(c=>{const mover=x=>{const r=c.getBoundingClientRect();const p=Math.max(2,Math.min(98,(x-r.left)/r.width*100));c.style.setProperty('--p',p+'%');};
    let on=false;c.addEventListener('pointerdown',e=>{on=true;c.setPointerCapture(e.pointerId);mover(e.clientX);e.stopPropagation();});c.addEventListener('pointermove',e=>{if(on)mover(e.clientX);});c.addEventListener('pointerup',()=>{on=false;});c.addEventListener('click',e=>e.stopPropagation());});
  /* simulador de mix */
  (function(){
    const r=$('#simE');if(!r)return;const g=$('#simG'),i=$('#simI'),B=77.5,a=.0192*B,b=.218*B,sup0=.504,mio0=1-.504-.218-.0192;
    const fmt=(v,c=1)=>v.toLocaleString('pt-BR',{minimumFractionDigits:c,maximumFractionDigits:c});
    function calc(){const E=+r.value/100,G=+g.value/100,I=+i.value/100,N=(B-I*(a+b))/(1-I*(E+G)),res=N*(1-E-G),s=res*sup0/(sup0+mio0),m=res-s;
      $('#simEv').textContent=fmt(E*100,0)+'%';$('#simGv').textContent=fmt(G*100,0)+'%';$('#simIv').textContent=fmt(I*100,0)+'%';
      const seg={s:s/N*100,g:G*100,m:m/N*100,e:E*100};
      for(const k in seg){const el=$('#bar-'+k);el.style.flexGrow=seg[k];el.querySelector('b').textContent=fmt(seg[k],0)+'%';}
      $('#simR').textContent=fmt(N-B);$('#simP').textContent=fmt((N/B-1)*100);$('#simS').textContent=fmt(s-sup0*B);}
    [r,g,i].forEach(x=>{x.addEventListener('input',calc);x.addEventListener('click',e=>e.stopPropagation());});calc();
  })();
  /* checklists marcáveis com contador */
  $$('[data-marca]').forEach(g=>{const it=$$('label',g),o=$('[data-placar]',g.closest('.tela'));
    const up=()=>{if(o)o.textContent=it.filter(l=>l.querySelector('input').checked).length+' de '+it.length;};
    it.forEach(l=>{l.addEventListener('click',e=>e.stopPropagation());l.querySelector('input').addEventListener('change',up);});up();});
  /* auditoria */
  (function(){const box=$('#audit');if(!box)return;const lin=$$('.linha',box),nota=$('#auditNota'),st=$('#auditSt');
    function up(){let ok=0,va=0;lin.forEach(l=>{const v=(l.querySelector('input:checked')||{}).value;if(v==='ok'){ok++;va++;}else if(v==='aj')va++;});const p=va?Math.round(ok/va*100):0;nota.textContent=p+'%';st.textContent=p>=85?'Loja no padrão':p>=70?'Plano de correção em 15 dias':'Visita do consultor em 7 dias';}
    box.addEventListener('change',up);box.addEventListener('click',e=>e.stopPropagation());up();})();
  /* início */
  const h=parseInt(location.hash.slice(1),10),n0=isNaN(h)?0:Math.max(0,Math.min(total-1,h-1));
  telas.forEach(t=>t.classList.remove('ativa'));atual=n0===0?(total>1?1:0):0;aplicar(n0);telas.forEach((t,i)=>{if(i!==n0)t.classList.remove('ativa');});
})();
