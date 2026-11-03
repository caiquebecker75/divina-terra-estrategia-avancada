# Desenha os planogramas em HTML. Usado no deck e no manual.
import json,pathlib,html,re
R=pathlib.Path(__file__).resolve().parent.parent
PAL=['#7C381F','#596D49','#CA942A','#AC834C','#461D17','#A9C094','#BCAD99','#E5DDD1']
TXT={'#7C381F':'#fff','#596D49':'#fff','#CA942A':'#2b1209','#AC834C':'#fff','#461D17':'#fff','#A9C094':'#2b1209','#BCAD99':'#2b1209','#E5DDD1':'#2b1209'}
FAM={'Castanhas e nozes':'#7C381F','Sementes':'#596D49','Frutas secas':'#AC834C','Snacks e chocolates':'#CA942A','Mix, cacau e farinhas':'#BCAD99'}
NIV={1:'Alto',2:'Alto',3:'Olhos',4:'Olhos',5:'Mão',6:'Baixo'}
def dados(): return json.loads((R/'analise/planogramas.json').read_text())
def nucleo(r,cat):
    c=r['P']['cats'].get(cat)
    if not c or 'niveis' not in c: return set()
    return {e['sku'] for n in c['niveis'] for m in n['mods'] for e in m}
def cores(c):
    v={}
    for n in c['niveis']:
        for m in n['mods']:
            for e in m: v[e['mc']]=v.get(e['mc'],0)+e['v']
    ord_=sorted(v,key=v.get,reverse=True)
    return {m:(PAL[i] if i<6 else '#E5DDD1') for i,m in enumerate(ord_)},ord_
def br(x): return str(x).replace('.',',').replace(',0','') if isinstance(x,float) else str(x)
def legenda(c,cor,ord_):
    it=''.join(f'<span><i style="background:{cor[m]}"></i>{html.escape(m)}</span>' for m in ord_[:6])
    if len(ord_)>6: it+=f'<span><i style="background:#E5DDD1"></i>Outras {len(ord_)-6} marcas</span>'
    return f'<div class="leg pg-leg"><b>Marca</b>{it}<b>Marcação</b><span><u></u>Núcleo: está em todas as lojas</span><span><u class="ls"></u>Lista: entra por tamanho</span><span><i class="hach"></i>Espaço local</span><span><em>2×</em>Frentes</span></div>'
def paginas(r,T,cat,porp=4):
    c=r[T]['cats'][cat]
    if 'tubos' in c: return 1
    n=max(1,int(c['f']+.999));return (n+porp-1)//porp
def fotos():
    f=R/'assets/produtos/mapa.json'
    return json.loads(f.read_text()) if f.exists() else {}
FORMATO={'pote':'p','caps':'c','garrafa':'g','sache':'s','barra':'b','caixa':'x'}
def formato(d):
    d=d.upper()
    if re.search(r'BARRA|BAR\b|PROTEIN CRISP|WAFER',d): return 'b'
    if re.search(r'SACH|STICK|SHOT',d): return 's'
    if re.search(r'\d\s?(ML|L)\b|AZEITE|VINAGRE|BEBIDA|KOMBUCHA',d): return 'g'
    if re.search(r'CAPS|CPS|TABS|COMP',d): return 'c'
    if re.search(r'CHA\b|CAIXA|\bCX\b|ALFAJOR|BISCOITO|MASSA|ESPAGUETE|PENNE|CHOCOLATE',d): return 'x'
    return 'p'
ALT={'p':1.35,'c':1.9,'g':3.0,'s':1.6,'b':2.6,'x':1.35}
def _r(v): return (f'{v:,.2f}').replace(',','X').replace('.',',').replace('X','.') if v is not None else ''
def face(e,px,alt,cor,tx,fm):
    "Uma frente: a foto real do produto em proporção real, apoiada na prateleira."
    w=e['w']*px
    info=fm.get(str(e['sku']))
    if info:
        h=min(alt-3,w*info['ar'])
        return f'<img class="pgf" src="assets/produtos/{e["sku"]}.webp" loading="lazy" alt="" style="width:{w:.1f}px;height:{h:.1f}px;object-fit:contain;object-position:bottom">'
    k=formato(e['desc']);h=min(alt-3,w*ALT[k])
    return f'<span class="pk pk-{k}" style="width:{w:.1f}px;height:{h:.1f}px;--c:{cor};color:{tx}"><i>{html.escape(e["mc"][:13])}</i></span>'
def item(e,px,alt,cor,fm,nuc):
    "Produto na prateleira: todas as frentes e, embaixo, a régua de preço."
    t=TXT[cor];rail=20
    fotos_=''.join(face(e,px,alt-rail,cor,t,fm) for _ in range(e['f']))
    lo,hi=e.get('pmin'),e.get('pmax')
    rg=f'<span class="pgr"><b>{_r(lo)}</b><b>{_r(hi)}</b></span>' if lo else '<span class="pgr"></span>'
    dat=' '.join(f'data-{k}="{html.escape(str(v),quote=True)}"' for k,v in dict(n=e['desc'],s=e['sku'],m=e['mc'],f=e['f'],c=e['f']*6,a=f'R$ {_r(lo)}' if lo else '',b=f'R$ {_r(hi)}' if hi else '',p=f'R$ {_r(e["pm"])}' if e.get('pm') else '',cl='Núcleo' if e['sku'] in nuc else 'Lista').items())
    return f'<div class="pgi" {dat} style="width:{e["w"]*e["f"]*px:.1f}px" tabindex="0"><div class="pgfs">{fotos_}</div>{rg}</div>'
def relatorio(c,fm,nuc):
    lin=[]
    for n in c['niveis']:
        pos=0
        for mi,m in enumerate(n['mods']):
            for e in m:
                pos+=1;lin.append(dict(mod=mi+1,niv=n['n'],pos=pos,sub=n['rot'],sku=e['sku'],nome=e['desc'],marca=e['mc'],fr=e['f'],cap=e['f']*6,larg=e['w']*e['f'],cl='Núcleo' if e['sku'] in nuc else 'Lista',pmin=e.get('pmin'),pmax=e.get('pmax'),pm=e.get('pm')))
    return lin
def plano(r,T,cat,maxm=None,px=None,ini=0):
    c=r[T]['cats'][cat];nuc=nucleo(r,cat);fm=fotos()
    if 'tubos' in c: return granel(c,T)
    cor,ord_=cores(c);f=c['f'];inteiros=max(1,int(f+.999))
    mostra=min(inteiros,ini+maxm) if maxm else inteiros
    nb=mostra-ini
    px=px or min(4.15,1380/(max(1,(f-ini) if (f-ini)<nb else nb)*90))
    alt=26*px;h='';larg_tot=0
    cols=[]
    for m in range(ini,mostra):
        larg=86 if (m+1<=f) else 43
        cols.append((m,larg))
    h=f'<div class="pg-g" style="--alt:{alt:.1f}px"><div class="pg-esq">'+''.join(f'<div class="pg-e"><b>{n["n"]}</b><span>{NIV[n["n"]]}</span></div>' for n in c['niveis'])+'</div><div class="pg-bays">'
    for m,larg in cols:
        h+=f'<div class="pg-bay" style="width:{(larg+4)*px:.1f}px"><div class="pg-tit">Módulo {m+1} · {"0,90 m" if larg==86 else "0,45 m"}</div>'
        for n in c['niveis']:
            itens=n['mods'][m] if m<len(n['mods']) else []
            soma=sum(e['w']*e['f'] for e in itens)
            cx=''
            for e in itens:
                cx+=item(e,px,alt,cor[e['mc']],fm,nuc)
            sob=larg-soma
            h+=f'<div class="pg-sh{" olho" if n["n"] in(3,4) else ""}" style="height:{alt:.1f}px">{cx}</div>'
        h+='</div>'
    h+='</div></div>'
    rel=''
    if nb<=2:
        lin=relatorio(c,fm,nuc);lin=[x for x in lin if ini<x['mod']<=mostra];vis=sorted(lin,key=lambda x:(x['mod'],x['niv'],x['pos']))
        filas=''.join(f'<tr><td>{x["mod"]}.{x["niv"]}.{x["pos"]}</td><td>{html.escape(x["marca"])}<small>{html.escape(x["nome"].title()[:44])}</small></td><td>{x["fr"]}</td><td class="np">{_r(x["pmin"])} a {_r(x["pmax"])}</td></tr>' for x in vis[:13])
        mais=f'<p class="pg-mais">Mais {len(vis)-13} posições no manual e no kit.</p>' if len(vis)>13 else ''
        rel=f'<div class="pg-rel"><div class="gt">Relatório de posições<small>Módulo.nível.posição, frentes e faixa de preço</small></div><table><thead><tr><th>Pos.</th><th>Produto</th><th>Fr.</th><th>Preço, R$</th></tr></thead><tbody>{filas}</tbody></table>{mais}</div>'
    h=f'<div class="pg-duo">{h}{rel}</div>'
    com=sum(1 for n in c['niveis'] for m in n['mods'] for e in m if str(e['sku']) in fm);tot=sum(1 for n in c['niveis'] for m in n['mods'] for e in m)
    resumo=f'<div class="pg-res"><span><b>{br(float(f))}</b> {"módulo" if f<=1 else "módulos"}</span><span><b>{c["skus"]}</b> produtos</span><span><b>{c["frentes"]}</b> frentes</span><span><b>{round(c["cob"]*100)}%</b> da venda da categoria nesta faixa</span>{f"<span class=mais>Módulos {ini+1} a {mostra} de {inteiros}</span>" if (maxm and inteiros>maxm) else ""}</div>'
    leg='<div class="leg pg-leg"><span><b>Cada foto é uma frente</b></span><span><i class="ol"></i>Faixa dos olhos: níveis 3 e 4</span><span>Nível 1: a loja pode trocar até 20% por regional</span><span><em class="ex">9,90 12,90</em>Régua de preço: mínimo e máximo sugeridos, em reais</span><span>Passe o mouse no produto para ver o nome na base, o SKU e as frentes.</span></div>'
    return resumo+h+leg
def granel(c,T):
    it=''.join(f'<div class="pgi pg-tb" data-n="{html.escape(t["desc"],quote=True)}" data-s="{t["sku"]}" data-m="A granel" data-f="1" data-a="R$ {_r(t.get("pmin"))}/kg" data-b="R$ {_r(t.get("pmax"))}/kg" tabindex="0"><div class="pg-tubo" style="background:{FAM[t["fam"]]};color:{"#2b1209" if FAM[t["fam"]] in("#CA942A","#BCAD99") else "#fff"}"><span>{html.escape(t["nome"])}</span></div><span class="pgr"><b>{_r(t.get("pmin"))}</b><b>{_r(t.get("pmax"))}</b></span></div>' for t in c['tubos'])
    leg=''.join(f'<span><i style="background:{v}"></i>{k} · {sum(1 for t in c["tubos"] if t["fam"]==k)} tubos</span>' for k,v in FAM.items())
    return f'<div class="pg-res"><span><b>{c["f"]}</b> módulos</span><span><b>{c["skus"]}</b> tubos</span><span><b>{round(c["cob"]*100)}%</b> da venda do granel nesta faixa</span></div><div class="pg-tubos" style="--n:{min(10,max(8,len(c["tubos"])//2+1 if len(c["tubos"])<=20 else 10))}">{it}</div><div class="leg pg-leg"><b>Família</b>{leg}</div>'
DICA='''<script>(function(){var d=document.createElement('div');d.className='pg-dica';var z=function(){var s=document.getElementById('stage');return s||document.body};z().appendChild(d);
function mostra(e){var a=e.target.closest&&e.target.closest('.pgi');if(!a){d.style.display='none';return}var v=a.dataset,l=[['SKU',v.s],['Marca',v.m],['Frentes',v.f],['Capacidade',v.c?v.c+' unidades':''],['Preço mínimo',v.a],['Preço máximo',v.b],['Preço médio pago',v.p],['Classe',v.cl]];d.innerHTML='<b>'+v.n+'</b><table>'+l.filter(function(x){return x[1]}).map(function(x){return '<tr><td>'+x[0]+'</td><td>'+x[1]+'</td></tr>'}).join('')+'</table>';d.style.display='block';var r=a.getBoundingClientRect(),w=d.offsetWidth,h=d.offsetHeight,x=Math.min(innerWidth-w-10,Math.max(10,r.left+r.width/2-w/2)),y=r.top-h-8;if(y<8)y=r.bottom+8;var host=d.parentNode;if(host.id==='stage'){var hr=host.getBoundingClientRect(),k=hr.width/1600;d.style.position='absolute';d.style.left=(x-hr.left)/k+'px';d.style.top=(y-hr.top)/k+'px'}else{d.style.left=x+'px';d.style.top=y+'px'}}
document.addEventListener('mouseover',mostra);document.addEventListener('focusin',mostra);document.addEventListener('mouseleave',function(){d.style.display='none'})})();</script>'''
CSS='''
.leg{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;font-size:14px;line-height:1.2;color:var(--cinza)}.leg b{color:var(--terra);font-weight:600}.leg span{display:inline-flex;align-items:center;gap:6px}.leg i{display:inline-block;width:13px;height:13px;border-radius:3px;flex:none}
.pg-res{display:flex;flex-wrap:wrap;gap:6px 22px;font-size:15px;color:var(--cinza);margin:8px 0 8px}.pg-res b{font:400 23px var(--serif);color:var(--choco)}.pg-res .mais{font-weight:600;color:var(--choco)}
.pg-duo{display:flex;gap:12px;justify-content:center;align-items:flex-start}.pg-rel{flex:1;min-width:280px;max-width:560px;font-size:12px}.pg-rel table{width:100%;border-collapse:collapse;margin-top:4px}.pg-rel th{font-size:11px;text-align:left;color:var(--cinza);border-bottom:1.5px solid var(--linho);padding:2px 5px}.pg-rel td{padding:3px 5px;border-bottom:1px solid var(--aveia);line-height:1.12;font-weight:600;font-size:12.5px}.pg-rel td small{display:block;font-weight:400;font-size:11.5px;color:var(--cinza)}.pg-rel td:first-child{white-space:nowrap;font-weight:400;color:var(--cinza)}.pg-mais{margin-top:4px;color:var(--cinza)}
.pg-g{display:flex;flex:none;align-items:flex-start;background:#fff;border:1px solid var(--linho);border-radius:6px;padding:6px 10px 8px 4px;width:max-content;}
.pg-esq{width:46px;flex:none;padding-top:19px}.pg-e{height:var(--alt);display:flex;flex-direction:column;justify-content:flex-end;padding:0 7px 4px 0;text-align:right;font-size:10px;color:var(--cinza);line-height:1.05}.pg-e b{font:400 14px var(--serif);color:var(--terra)}
.pg-bays{display:flex;border-left:2px solid #1d1a18}
.pg-bay{border-right:2px solid #1d1a18;flex:none}.pg-tit{height:19px;font-size:10.5px;line-height:19px;color:var(--cinza);text-align:center;border-bottom:1px solid #1d1a18;border-top:2px solid #1d1a18}
.pg-sh{display:flex;align-items:flex-end;justify-content:space-evenly;gap:0;border-bottom:4px solid #2c2622;box-shadow:inset 0 -5px 7px -6px rgba(0,0,0,.35);overflow:hidden;position:relative}
.pg-sh.olho{background:rgba(202,148,42,.07)}
.pgi{display:flex;flex-direction:column;justify-content:flex-end;flex:none;position:relative;height:100%;cursor:default}.pgi:hover,.pgi:focus{outline:2px solid var(--paprica);outline-offset:-1px;z-index:3}.pgfs{display:flex;align-items:flex-end;flex:1;min-height:0}
.pgr{display:flex;justify-content:space-between;gap:1px;height:20px;background:#f4efe6;border-top:1px solid #2c2622;padding:1px 2px;font:600 8.3px/9px var(--sans);color:var(--terra);flex-direction:column;overflow:hidden;text-align:center}.pgr b{display:block;font-weight:600}.pgr b:first-child{color:var(--oliva)}.pgr b:last-child{color:var(--choco)}
.pgf{display:block;flex:none;mix-blend-mode:multiply}
.pg-tb{height:auto}.pg-tb .pgr{height:22px;font-size:10px;flex-direction:row;align-items:center;justify-content:center;gap:8px;border:0;border-radius:0 0 6px 6px}
.pg-dica{position:fixed;z-index:999;max-width:320px;background:var(--terra);color:var(--iogurte);border-radius:10px;padding:10px 13px;font:400 13px/1.3 var(--sans);pointer-events:none;box-shadow:0 12px 30px rgba(44,20,12,.4);display:none}.pg-dica b{display:block;font-weight:600;font-size:13.5px;margin-bottom:4px}.pg-dica table{border-collapse:collapse;width:100%}.pg-dica td{padding:1px 0;font-size:12px}.pg-dica td:first-child{opacity:.72;padding-right:10px}
.leg .ex{font:600 8.5px/1 var(--sans);font-style:normal;background:#f4efe6;border:1px solid var(--linho);padding:2px 3px;color:var(--terra)}.np{white-space:nowrap}
.pk{display:block;flex:none;box-sizing:border-box;background:var(--c);position:relative;border:1px solid rgba(0,0,0,.28);overflow:hidden;box-shadow:inset 2px 0 3px rgba(255,255,255,.28),inset -3px 0 4px rgba(0,0,0,.2)}
.pk i{position:absolute;left:1px;right:1px;top:38%;font:600 8px/1.02 var(--sans);font-style:normal;text-align:center;word-break:break-word}
.pk-p{border-radius:3px 3px 2px 2px}.pk-p:before{content:"";position:absolute;left:8%;right:8%;top:0;height:12%;background:rgba(0,0,0,.5)}
.pk-c{border-radius:3px}.pk-c:before{content:"";position:absolute;left:14%;right:14%;top:0;height:18%;background:rgba(255,255,255,.75)}
.pk-g{border-radius:40% 40% 3px 3px/18% 18% 3px 3px}.pk-g:before{content:"";position:absolute;left:32%;right:32%;top:0;height:14%;background:rgba(0,0,0,.55)}
.pk-s,.pk-b,.pk-x{border-radius:1px}
.pg-vz{display:block;flex:none;background:repeating-linear-gradient(135deg,#f2ede5 0 4px,#fff 4px 8px);border:1px dashed var(--linho);box-sizing:border-box;position:relative}.pg-vz i{position:absolute;left:3px;bottom:2px;font:500 9px var(--sans);font-style:normal;color:var(--cinza)}
.leg i.ol{background:rgba(202,148,42,.25);border:1px solid rgba(202,148,42,.6)}.leg i.hach{background:repeating-linear-gradient(135deg,#efe9df 0 3px,#fff 3px 6px);border:1px dashed var(--linho)}
.pg-tubos{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:7px}.pg-tubo{height:112px;border-radius:40px 40px 8px 8px;padding:8px 6px;box-shadow:inset 6px 0 8px rgba(255,255,255,.22),inset -8px 0 10px rgba(0,0,0,.18);display:flex;align-items:flex-end;font-size:11.5px;line-height:1.1;font-weight:500}
.pg-leg{margin-top:9px}
'''
