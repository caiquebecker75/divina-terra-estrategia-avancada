/* Interações da visão estratégica para a diretoria: abas, linha do tempo, blocos que abrem,
   filtro e mês do calendário, simulador do potencial. O PDF fotografa cada aba como uma página. */
(function(){
  'use strict';
  const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
  const para=e=>e.stopPropagation();
  const fmt=(v,c)=>v.toLocaleString('pt-BR',{minimumFractionDigits:c,maximumFractionDigits:c});

  /* abas: regiões e curva de valor */
  $$('[data-abas]').forEach(g=>{
    const bts=$$('.aba',g),pns=$$('.painel',g);
    g.__abre=k=>{bts.forEach(b=>b.classList.toggle('on',b.dataset.k===k));pns.forEach(p=>p.classList.toggle('on',p.dataset.k===k));};
    bts.forEach(b=>{b.addEventListener('click',e=>{para(e);g.__abre(b.dataset.k);});});
  });

  /* detalhe ao clicar ou passar o mouse: linha do tempo e matriz de crescimento */
  $$('[data-det-alvo]').forEach(c=>{
    const alvo=document.getElementById(c.dataset.detAlvo),its=$$('[data-det]',c);
    const mostra=it=>{its.forEach(x=>x.classList.toggle('on',x===it));const dx=it.querySelector('.dx');
      alvo.innerHTML=dx?dx.innerHTML:'<b>'+it.querySelector('b').textContent+':</b> '+it.dataset.det;};
    its.forEach(it=>{it.addEventListener('click',e=>{para(e);mostra(it);});it.addEventListener('mouseenter',()=>mostra(it));});
  });

  /* quem faz o quê: clique numa área destaca a linha dela */
  $$('.d-90 .tb').forEach(tb=>{
    const cel=[...tb.children],ars=$$('.ar',tb);let sel=null;
    ars.forEach(a=>a.addEventListener('click',e=>{para(e);sel=sel===a?null:a;
      let lin=null;cel.forEach(x=>{if(x.classList.contains('ar'))lin=x;if(x.classList.contains('h')||!lin)return;x.classList.toggle('apagado',!!sel&&lin!==sel);});
      ars.forEach(x=>x.classList.toggle('on',x===sel));}));
  });

  /* blocos que abrem o detalhe (mini trade book) */
  $$('[data-abre]').forEach(b=>b.addEventListener('click',e=>{para(e);const ab=!b.classList.contains('aberto');
    $$('[data-abre]',b.parentElement).forEach(x=>x.classList.remove('aberto'));b.classList.toggle('aberto',ab);}));

  /* calendário: filtro por nível e plano do mês */
  $$('.d-cal').forEach(t=>{
    const bts=$$('.filtro button',t),spans=$$('.cal .dt span',t),meses=$$('.cal .mes',t),dms=$$('.detcal .dm',t);
    bts.forEach(b=>b.addEventListener('click',e=>{para(e);bts.forEach(x=>x.classList.toggle('on',x===b));const f=b.dataset.f;
      spans.forEach(s=>s.classList.toggle('apagado',f!=='todas'&&!s.classList.contains(f)));
      meses.forEach(m=>m.classList.toggle('apagado',f!=='todas'&&!m.querySelector('.dt span.'+f)));}));
    const abre=m=>{dms.forEach(d=>d.classList.toggle('on',d.dataset.m===m));meses.forEach(x=>x.classList.toggle('sel',x.dataset.m===m));};
    meses.forEach(m=>m.addEventListener('click',e=>{para(e);abre(m.classList.contains('sel')?'0':m.dataset.m);}));
  });

  /* simulador do potencial: N=(B-I(a+b))/(1-I(E+G)), com a e b de hoje */
  const sE=$('#sE');
  if(sE){
    const sG=$('#sG'),sI=$('#sI'),B=77.5,a=.0653*B,b=.218*B,cen=$$('.d-pot .cen button');
    const calc=()=>{const E=+sE.value/100,G=+sG.value/100,I=+sI.value/100,N=(B-I*(a+b))/(1-I*(E+G));
      $('#vE').textContent=sE.value+'%';$('#vG').textContent=sG.value+'%';$('#vI').textContent=sI.value+'%';
      $('#rR').textContent='+R$ '+fmt(N-B,1)+' mi';$('#rP').textContent='+'+fmt((N/B-1)*100,1)+'%';
      const at=[sE.value,sG.value,sI.value].join(',');cen.forEach(c=>c.classList.toggle('on',c.dataset.c===at));
      const res=N*(1-E-G),sp=.504,mi=1-.504-.218-.0653,su=res*sp/(sp+mi),de=res-su,seg={bS:su/N*100,bG:G*100,bD:de/N*100,bE:E*100},nom={bS:'Suplemento',bG:'Granel',bD:'Despensa e outros',bE:''};
      for(const k in seg){const el=$('#'+k);if(!el)continue;el.style.flex=seg[k]+' 1 0';el.textContent='R$ '+fmt(seg[k],0)+(nom[k]?' '+nom[k]:'');}};
    [sE,sG,sI].forEach(x=>{x.addEventListener('input',calc);x.addEventListener('click',para);x.addEventListener('keydown',para);});
    cen.forEach(c=>c.addEventListener('click',e=>{para(e);const [e1,g1,i1]=c.dataset.c.split(',');sE.value=e1;sG.value=g1;sI.value=i1;calc();}));
    calc();
  }

  /* PDF: uma página por aba da tela ativa */
  window.__pdfEstados=()=>{const t=$('.tela.ativa');const g=t&&$('[data-abas]',t);return g?$$('.aba',g).length:0;};
  window.__pdfEstado=k=>{const g=$('.tela.ativa [data-abas]');const b=$$('.aba',g)[k];if(b)g.__abre(b.dataset.k);};
})();
