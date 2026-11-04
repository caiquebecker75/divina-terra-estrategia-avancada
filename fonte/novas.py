# Conteúdo gerado do manual dentro do deck: planogramas, loja inteira, categorias, preços, custo por ponto.
import json,pathlib,html,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import plano_html as PH
R=PH.R
COR={'Cuidar':'#7C381F','Abastecer':'#596D49','Granel':'#AC834C','Celebrar':'#CA942A','Caixa':'#461D17'}
TOK={'#CA942A':'#2b1209'}
ORD=['Proteínas','Creatina','Colágeno','Performance','Bem-Estar','Longevidade','Vitaminas','Ômegas','Intestino','Imunidade','Kids e Peso','Barras e snacks','Cafés funcionais','Despensa','Chás','Granel','Empório','Caixa']
MOT={**{c:'Cuidar' for c in ORD[:11]},**{c:'Abastecer' for c in ORD[11:15]},'Granel':'Granel','Empório':'Celebrar','Caixa':'Caixa'}
ICO={'Cuidar':'i-cuidar','Abastecer':'i-cesta','Granel':'i-trigo','Celebrar':'i-presente','Caixa':'i-tag'}
TAMN={'P':'Até 50 m²','M':'50 a 80 m²','G':'Acima de 80 m²'}
def br(v,c=0): return f'{v:,.{c}f}'.replace(',','X').replace('.',',').replace('X','.')
def n(v): return br(v,1).replace(',0','')
def ic(i,cl=''):
    i=i if i.startswith('i-') else 'i-'+i
    return f'<svg class="ico {cl}"><use href="#{i}"/></svg>'
def legenda_motor():
    return '<div class="leg"><b>Motor</b>'+''.join(f'<span><i style="background:{v}"></i>{k}</span>' for k,v in COR.items() if k!='Caixa')+f'<span><i style="background:{COR["Caixa"]}"></i>Caixa, fora da conta de módulos</span></div>'
def plano_tabs(r,T):
    bts='';pns='';pri=True
    for cat in ORD:
        c=r[T]['cats'].get(cat)
        if not c: continue
        pg=PH.paginas(r,T,cat)
        for p in range(pg):
            k=f'{T}{ORD.index(cat)}_{p}';rot=cat+(f' {p+1}/{pg}' if pg>1 else '')
            cor=COR[MOT[cat]]
            bts+=f'<button class="aba pa{" on" if pri else ""}" data-k="{k}"><i style="background:{cor}"></i>{html.escape(rot)}</button>'
            pns+=f'<div class="painel{" on" if pri else ""}" data-k="{k}">{PH.plano(r,T,cat,maxm=4,ini=p*4)}</div>'
            pri=False
    return f'<div data-abas class="pa-abas"><div class="abas">{bts}</div>{pns}</div>'
def fora(r,T):
    z=[c for c in ('Intestino','Imunidade','Kids e Peso') if c not in r[T]['cats']]
    return ('Nesta faixa, '+', '.join(z).replace('Kids e Peso','kids e peso').lower()+' dividem a mesma gôndola de bem-estar.') if z else ''
PAREDES=[('Parede do fundo · destino',['Proteínas','Creatina','Colágeno','Performance','Bem-Estar','Longevidade']),('Parede lateral · rotina de saúde',['Vitaminas','Ômegas','Intestino','Imunidade','Kids e Peso']),('Parede lateral · abastecer',['Barras e snacks','Cafés funcionais','Despensa','Chás']),('Granel',['Granel']),('Empório e mesa',['Empório'])]
def planta_svg(T):
    w={'P':520,'M':640,'G':740}[T];h={'P':300,'M':340,'G':380}[T]
    m=T!='P'
    cx=w/2
    s=f'<svg viewBox="0 0 {w+20} {h+44}" class="pl-svg"><rect x="10" y="10" width="{w}" height="{h}" rx="6" fill="#fff" stroke="#BCAD99" stroke-width="2"/>'
    s+=f'<rect x="10" y="10" width="{w}" height="34" fill="{COR["Cuidar"]}"/><text x="{cx+10}" y="32" fill="#fff" text-anchor="middle" font-size="13" font-weight="600">Destino: proteínas, creatina, colágeno, performance</text>'
    s+=f'<rect x="10" y="44" width="34" height="{h-110}" fill="{COR["Abastecer"]}"/><text transform="translate(32,{44+(h-110)/2}) rotate(-90)" fill="#fff" text-anchor="middle" font-size="12" font-weight="600">Barras, cafés, despensa, chás</text>'
    s+=f'<rect x="{w-24}" y="44" width="34" height="{h-110}" fill="#9a5b3f"/><text transform="translate({w-2},{44+(h-110)/2}) rotate(-90)" fill="#fff" text-anchor="middle" font-size="12" font-weight="600">Vitaminas, ômegas, intestino</text>'
    s+=f'<rect x="{cx-90}" y="66" width="180" height="30" rx="4" fill="{COR["Granel"]}"/><text x="{cx}" y="86" fill="#fff" text-anchor="middle" font-size="12.5" font-weight="600">Granel</text>'
    s+=f'<rect x="{cx-90 if m else cx-50}" y="{h/2+2}" width="{180 if m else 100}" height="{42 if m else 30}" rx="{21 if m else 6}" fill="{COR["Celebrar"]}"/><text x="{cx+10-10}" y="{h/2+(28 if m else 22)}" fill="#2b1209" text-anchor="middle" font-size="12.5" font-weight="600">{"Mesa do Empório" if m else "Empório"}</text>'
    s+=f'<rect x="{w-120}" y="{h-44}" width="120" height="34" rx="4" fill="{COR["Caixa"]}"/><text x="{w-60}" y="{h-22}" fill="#fff" text-anchor="middle" font-size="12.5" font-weight="600">Caixa</text>'
    s+=f'<rect x="60" y="{h+6}" width="160" height="8" fill="#BCAD99"/><text x="140" y="{h+32}" text-anchor="middle" font-size="12.5" fill="#6F5F55">Entrada e vitrine</text>'
    pa=f'M140 {h+4} C 90 {h-60}, 90 {h/2}, {cx-60} 120 S {cx+150} 80, {w-70} 150 S {cx+90} {h/2+80}, {cx} {h/2+56} S {w-120} {h-70}, {w-90} {h-46}'
    s+=f'<path d="{pa}" fill="none" stroke="#CA3C2E" stroke-width="2" stroke-dasharray="6 7" class="marcha"/><circle r="7" fill="#CA3C2E" class="so-tela-svg"><animateMotion dur="12s" repeatCount="indefinite" path="{pa}"/></circle></svg>'
    return s
def loja_tabs(r):
    bts='';pns=''
    for i,T in enumerate('PMG'):
        M=r[T]['modulos'];tot=sum(M.values());skus=sum(v['skus'] for k,v in r[T]['cats'].items() if k!='Caixa')
        bts+=f'<button class="aba{" on" if i==0 else ""}" data-k="l{T}"><b>Loja {T}</b><span>{TAMN[T]} · {int(tot)} módulos</span></button>'
        par=''
        for nome,cats in PAREDES:
            soma=sum(M.get(c,0) for c in cats)
            if not soma: continue
            cels=''
            for c in cats:
                f=M.get(c,0)
                if not f: continue
                cor=COR[MOT[c]];tx=TOK.get(cor,'#fff')
                cels+=f'<div class="lj-c" style="flex:{f} 1 0;background:{cor};color:{tx}"><b>{n(float(f))}</b><span>{html.escape(c)}</span></div>'
            par+=f'<div class="lj-p"><div class="lj-n">{html.escape(nome)}<small>{n(float(soma))} {"módulo" if soma<=1 else "módulos"} · {br(soma*.9,1)} m</small></div><div class="lj-f">{cels}</div></div>'
        pns+=f'<div class="painel{" on" if i==0 else ""}" data-k="l{T}"><div class="lj-g"><div>{planta_svg(T)}</div><div>{par}<p class="lj-ob"><b>{skus} produtos</b> em {int(tot)} módulos de 0,90 m, mais o caixa. {fora(r,T)} Frio e café da loja ficam fora da conta.</p></div></div></div>'
    return f'<div data-abas><div class="abas">{bts}</div>{pns}</div>'
PAPEL={'Proteínas':'Destino','Creatina':'Destino','Colágeno':'Destino','Performance':'Destino','Bem-Estar':'Destino','Longevidade':'Destino','Vitaminas':'Rotina','Ômegas':'Rotina','Intestino':'Rotina','Imunidade':'Ocasião','Kids e Peso':'Rotina','Barras e snacks':'Rotina','Cafés funcionais':'Rotina','Despensa':'Rotina','Chás':'Rotina','Granel':'Rotina','Empório':'Ocasião','Caixa':'Conveniência'}
IND={'Proteínas':'Cortar a cauda. Whey, isolada, beef e vegana em prateleiras separadas.','Creatina':'Núcleo enxuto. Creapure nos olhos, goma à parte.','Colágeno':'Separar pele de articular e reduzir sobreposição.','Performance':'Agrupar por uso: pré-treino, aminoácidos, energia.','Bem-Estar':'Nomes de benefício permitidos e conversa treinada.','Longevidade':'Dar casa própria: coenzima, NAC, cúrcuma.','Vitaminas':'Organizar por nutriente, de A a Z, com régua de uso.','Ômegas':'Rotina consultiva: uma régua “para que serve”.','Intestino':'Dar casa própria, com probióticos e fibras.','Imunidade':'Crescer no inverno e reduzir no resto do ano.','Kids e Peso':'Só ganha módulo em loja maior; senão, junto com bem-estar.','Barras e snacks':'Reduzir a cauda. Ponta e caixa para os que giram.','Cafés funcionais':'Reduzir a dependência de uma só marca.','Despensa':'Recortar por uso. Selo vira atributo, não setor.','Chás':'Parede própria, com caixas e folhas.','Granel':'Parede de 20 a 40 tubos, sem ruptura, com prova.','Empório':'Entrar com curadoria: 36, 68 e 96 produtos.','Caixa':'Pequeno formato, posição secundária.'}
BASEMAP={'Proteínas':['Proteínas'],'Creatina':['Creatina'],'Colágeno':['Colágeno e Beleza'],'Performance':['Performance'],'Bem-Estar':['Equilíbrio e Bem-Estar'],'Longevidade':['Longevidade'],'Vitaminas':['Vitaminas de A a Z'],'Ômegas':['Ômegas'],'Intestino':['Saúde Intestinal'],'Imunidade':['Imunidade'],'Kids e Peso':['Kids','Peso e Composição'],'Barras e snacks':['Barras e snacks'],'Cafés funcionais':['Café e cápsulas'],'Despensa':['Despensa sem setor','Farinhas e despensa'],'Chás':['Chás'],'Granel':['Granel']}
def cat_base(): return json.loads((R/'analise/cat_base.json').read_text())
def pct(cb,c):
    if c=='Empório': return sum(v['pct'] for k,v in cb.items() if k.startswith('Empório'))
    return sum(cb[k]['pct'] for k in BASEMAP.get(c,[]) if k in cb)
def topm(cb,c):
    if c=='Empório': return 'Haoma, Puro e Leve, Konjac'
    k=BASEMAP.get(c,[None])[0]
    return ', '.join(x.replace(' Nutrition','') for x in cb[k]['top'][:3]) if k in cb else ''
def categorias_tabela(r):
    cb=cat_base();lin=''
    for c in ORD:
        mot=MOT[c];cor=COR[mot];p=pct(cb,c)
        if c=='Caixa': p_='fora'
        else: p_=br(p,1)+'%'
        mods=' · '.join(n(float(r[T]['modulos'].get(c,0))) if c!='Caixa' else {'P':'0,5','M':'0,5','G':'1'}[T] for T in 'PMG')
        barra=f'<span class="cb" style="width:{min(100,p/22*100):.0f}%;background:{cor}"></span>' if c!='Caixa' else ''
        lin+=f'<tr><td><span class="cm" style="background:{cor}">{ic(ICO[mot])}</span></td><td><b>{html.escape(c)}</b></td><td>{PAPEL[c]}</td><td class="cv"><span class="ct">{barra}</span><em>{p_}</em></td><td>{html.escape(topm(cb,c))}</td><td class="num2">{mods}</td><td>{html.escape(IND[c])}</td></tr>'
    return f'<table class="ctb"><thead><tr><th></th><th>Categoria</th><th>Papel</th><th>% da venda da rede</th><th>Marcas que mais pesam</th><th>Módulos P · M · G</th><th>Indicação</th></tr></thead><tbody>{lin}</tbody></table>'+'<div class="leg" style="margin-top:6px"><b>Como ler</b><span>Barra: % da venda da rede, na escala até 22%</span></div>'+legenda_motor()
def regua_precos():
    cb=cat_base();xs=[('Proteínas','Proteínas','Referência no whey mais comparado'),('Creatina','Creatina','Referência em Crealift e Creafort'),('Ômegas','Ômegas','Valor: paga pela orientação'),('Vitaminas','Vitaminas de A a Z','Valor, com magnésio de referência'),('Colágeno','Colágeno e Beleza','Valor'),('Cafés funcionais','Café e cápsulas','Referência em Supercoffee'),('Granel, por kg','Granel','Oportunidade no encarte'),('Barras e snacks','Barras e snacks','Referência no item de maior giro'),('Despensa','Despensa sem setor','Valor nos selos'),('Chás','Chás','Valor'),('Empório: chocolates','Empório: Chocolates e doces finos','Valor, a partir de R$ 50 nos especiais'),('Empório: azeites','Empório: Azeites e vinagres','Valor, com origem comprovada')]
    mx=300;pc=lambda v:v/mx*100
    grade=''.join(f'<i style="left:{pc(v):.1f}%"><em>R$ {v}</em></i>' for v in range(0,301,50))
    lin=''
    for nm,k,reg in xs:
        v=cb[k]
        lin+=f'<div class="rp-r"><div class="rp-l"><b>{html.escape(nm)}</b><span>{html.escape(reg)}</span></div><div class="rp-t"><span class="rp-b ax" style="left:{pc(v["p25"]):.1f}%;width:{max(.8,pc(v["p75"]-v["p25"])):.1f}%"></span><span class="rp-m lp-pulso" style="left:{pc(v["p50"]):.1f}%"></span></div><div class="rp-v">R$ {br(v["p25"])} a {br(v["p75"])} · <b>R$ {br(v["p50"])}</b></div></div>'
    return f'<div class="rp2">{lin}<div class="rp-r rp-eixo"><div></div><div class="rp-t rp-gr">{grade}</div><div></div></div></div><div class="leg" style="margin-top:6px"><b>Como ler</b><span><i style="background:#AC834C"></i>Faixa que concentra a metade do meio da venda</span><span><i style="background:#461D17;border-radius:50%"></i>Preço onde está a metade da venda</span><span>Eixo: preço médio pago por unidade, em reais. Granel: por quilo.</span></div>'
# custo por ponto: estimativa de referência, antes de cotação
PONTOS=[('Porta e vitrine','Placa e adesivo de entrada',350,800,lambda d:1,'i-loja','Não'),('Placa suspensa de setor','Lê a 8 m',90,220,lambda d:d['sus'],'i-placa','Não'),('Testeira de módulo','90 × 18 cm, lê a 8 m',45,95,lambda d:d['mod'],'i-camadas','Sim, por período'),('Faixa de categoria','Parte alta do módulo, lê a 4 m',20,45,lambda d:d['cat'],'i-camadas','Não'),('Faixa de subcategoria','Borda da prateleira, lê a 2 m',8,18,lambda d:d['sub'],'i-regua','Não'),('Régua “para que serve”','Uso, dose e formato',6,14,lambda d:d['reg'],'i-conversa','Não'),('Etiqueta de preço','6,5 × 3,5 cm, um por produto',.15,.40,lambda d:d['sku'],'i-tag','Não'),('Selo de benefício','Vegano, sem glúten, orgânico',.20,.60,lambda d:round(d['sku']*.2),'i-selo','Não'),('Stopper de destaque','Até 1 por módulo, em metade dos módulos',6,14,lambda d:round(d['mod']/2),'i-estrela','Sim'),('Comunicação do granel','Placas de família, etiqueta de tubo, potinho de prova',300,700,lambda d:1,'i-trigo','Sim, por família'),('Kit de ponta de gôndola','Comunicação da ponta, sem o móvel',280,650,lambda d:d['pon'],'i-gondola','Sim'),('Mesa do Empório','Mesa de MDF com comunicação, onde houver vão',2800,6500,lambda d:d['mes'],'i-presente','Sim, em data'),('Display de caixa','Acrílico ou MDF, no balcão',180,450,lambda d:d['cx'],'i-caixa','Sim')]
TEMPO={'Porta e vitrine':('10 a 15 dias',60,'Fixa, revisão anual'),'Placa suspensa de setor':('10 a 15 dias',20,'Fixa'),'Testeira de módulo':('10 a 15 dias',5,'Fixa'),'Faixa de categoria':('7 a 10 dias',5,'Fixa'),'Faixa de subcategoria':('7 a 10 dias',3,'Fixa, troca com o planograma'),'Régua “para que serve”':('7 a 10 dias',3,'Fixa, revisão trimestral'),'Etiqueta de preço':('3 a 5 dias',1,'Troca a cada mudança de preço'),'Selo de benefício':('3 a 5 dias',.5,'Fixa'),'Stopper de destaque':('5 a 7 dias',1,'Até 60 dias'),'Comunicação do granel':('10 a 15 dias',60,'Fixa'),'Kit de ponta de gôndola':('10 a 15 dias',30,'Por ação, 30 a 45 dias'),'Mesa do Empório':('20 a 30 dias',60,'Mesa fixa, comunicação mensal'),'Display de caixa':('15 a 20 dias',10,'Fixa, conteúdo mensal')}
MONTA=1.5 # horas para tirar, limpar, ajustar e montar um módulo pelo planograma
def horas(r,T):
    d=quant(r,T);pc=sum(fq(d)*TEMPO[nm][1] for nm,ds,a,b,fq,ico,v in PONTOS)/60;mt=d['mod']*MONTA
    return pc,mt
def quant(r,T):
    c=r[T]['cats'];M=r[T]['modulos']
    sub=set();reg=set()
    for k,v in c.items():
        if 'niveis' in v:
            for ni in v['niveis']:
                if ni['mods']:
                    sub.add((k,ni['rot']))
                    if MOT.get(k)=='Cuidar': reg.add((k,ni['rot']))
    return dict(mod=int(sum(M.values())),sus={'P':3,'M':5,'G':6}[T],cat=sum(1 for x,v in M.items() if v>0),sub=len(sub),reg=len(reg),sku=sum(v['skus'] for v in c.values()),pon={'P':1,'M':2,'G':3}[T],mes={'P':0,'M':1,'G':1}[T],cx={'P':1,'M':1,'G':2}[T])
def custo(r):
    d={T:quant(r,T) for T in 'PMG'};lin='';tot={T:[0,0] for T in 'PMG'};cor=['#461D17','#7C381F','#9a5b3f','#AC834C','#CA942A','#596D49','#A9C094','#BCAD99']
    grupos={'Sinalização da loja':[0,1],'Módulos e categorias':[2,3,4,5],'Preço e atributo':[6,7],'Destaque':[8,9,10],'Mesa do Empório':[11],'Caixa':[12]}
    dados=[]
    for i,(nm,ds,a,b,fq,ico,verba) in enumerate(PONTOS):
        qs={T:fq(d[T]) for T in 'PMG'};faixa=f'R$ {br(a,2) if a<1 else br(a)} a {br(b,2) if b<1 else br(b)}'
        cels=''
        for T in 'PMG':
            q=qs[T];tot[T][0]+=q*a;tot[T][1]+=q*b
            val=(q*(a+b)/2)
            cels+=f'<td class="num2">{br(q)}</td><td class="num2 tt">{("R$ "+br(val)) if q else "sem"}</td>'
        dados.append((nm,{T:qs[T]*(a+b)/2 for T in 'PMG'}))
        tp=TEMPO[nm];lin+=f'<tr><td><span class="cm" style="background:var(--aveia);color:var(--choco)">{ic(ico)}</span></td><td><b>{html.escape(nm)}</b><small>{html.escape(ds)}</small></td><td class="num2">{faixa}</td><td class="num2">{tp[0]}</td><td class="num2">{(str(tp[1]).replace(".",",")+" min")}</td><td>{html.escape(tp[2])}</td>{cels}<td>{verba}</td></tr>'
    tt=''.join(f'<td colspan="2" class="num2"><b>R$ {br(round(tot[T][0],-2))} a {br(round(tot[T][1],-2))}</b></td>' for T in 'PMG')
    tab=f'<table class="ctb cst"><thead><tr><th></th><th>Ponto da loja</th><th>Custo por unidade</th><th>Produção</th><th>Instalar, cada</th><th>Quanto dura</th><th colspan="2">Loja P</th><th colspan="2">Loja M</th><th colspan="2">Loja G</th><th>Verba de marca?</th></tr><tr class="sub"><th></th><th></th><th></th><th>dias úteis</th><th></th><th></th><th>Qtd.</th><th>Médio</th><th>Qtd.</th><th>Médio</th><th>Qtd.</th><th>Médio</th><th></th></tr></thead><tbody>{lin}<tr class="tot"><td></td><td><b>Total por loja</b></td><td></td><td></td><td></td><td></td>{tt}<td></td></tr></tbody></table>'
    # barras empilhadas por grupo
    mx=max(sum(x[1][T] for x in dados) for T in 'PMG');bars=''
    for T in 'PMG':
        seg=''
        for j,(g,idx) in enumerate(grupos.items()):
            v=sum(dados[i][1][T] for i in idx)
            if v>0: seg+=f'<span class="seg ax" style="width:{v/mx*100:.1f}%;background:{cor[j]}" title="{g}: R$ {br(v)}"></span>'
        s=sum(x[1][T] for x in dados)
        bars+=f'<div class="cp-b"><b>Loja {T}</b><div class="cp-t">{seg}</div><em>R$ {br(round(s,-2))}</em></div>'
    leg='<div class="leg"><b>Grupo</b>'+''.join(f'<span><i style="background:{cor[j]}"></i>{g}</span>' for j,g in enumerate(grupos))+'</div>'
    pay={T:sum(x[1][T] for x in dados) for T in 'PMG'}
    return tab,bars+leg,pay,tot
def marcas_alta_html():
    alta=[('Haoma Biscottino',33,70,'Empório'),('Yosen',27,114,'Bem-estar'),('Ocean Drop em bem-estar',28,16,'Cuidar'),('Sementes no granel',14,21,'Granel'),('Liquidz',10,49,'Performance'),('True em bem-estar',8,12,'Cuidar'),('Essential em bem-estar',7,22,'Cuidar'),('SuperCoffee',5,15,'Cafés')]
    queda=[('Essential em proteínas',-18,-11),('Bold, total',-10,-30),('Guday',-22,-32),('Sublyme',-17,-30)]
    mx=120;c=26
    def lin(n,a,b,cat=''):
        ca='#596D49' if a>=0 else '#CA3C2E';cb_='#A9C094' if b>=0 else '#e39a91'
        ba=lambda v,co:f'<span class="ma-b lp-luz ax" style="{"left:"+str(c)+"%;width:"+f"{v/mx*(100-c):.1f}" if v>=0 else "left:"+f"{c+v/mx*(100-c):.1f}"+"%;width:"+f"{-v/mx*(100-c):.1f}"}%;background:{co}"></span>'
        return f'<div class="ma-r"><div class="ma-n">{html.escape(n)}</div><div class="ma-t"><div class="ma-l">{ba(a,ca)}</div><div class="ma-l">{ba(b,cb_)}</div><i class="ma-z" style="left:{c}%"></i></div><div class="ma-v"><b>{a:+d}%</b> <span>{b:+d}%</span></div></div>'
    h='<div class="gt">Em alta e em queda dentro da rede<small>Variação da venda nas mesmas lojas. A rede inteira fez -0,7% e -5,8%</small></div>'
    h+=''.join(lin(*x[:3]) for x in alta)+'<div class="ma-sep">Em queda</div>'+''.join(lin(*x) for x in queda)
    h+='<div class="leg leg-graf"><b>Como ler</b><span><i style="background:#596D49"></i>Jul a set contra abr a jun</span><span><i style="background:#A9C094"></i>Jul a set contra nov a jan</span><span><i style="background:#CA3C2E"></i>Queda</span><span>Sem comparação ano contra ano: a base não permite.</span></div>'
    return h
MERC=[('Growth','Acima de R$ 2 bi em 2025, no online','1 SKU, sem venda'),('Supley (Max Titanium)','R$ 200 mi no varejo alimentar','Vende pouco'),('True Source','Receita +105% no 1º semestre de 2025; 7 mil pontos','Vende bem'),('Bold','Comprada pela Ferrero em 2026; 30 mil pontos','Vende bem, em queda'),('Nutrata','R$ 400 mi em 2024; colaborações Bacio di Latte e Prestígio','Vende bem'),('Haoma','R$ 35 mi em 2024; mais de 2 mil pontos','Vende bem'),('Lotus Biscoff','Negocia produção local com a Mondelez','Só fora da base'),('Sabiá e Estância das Oliveiras','Azeites nacionais em rankings de 2025','Não cadastradas'),('Luisa Abram e Baianí','Chocolate de origem; Luisa com R$ 6 mi','Não cadastradas'),('Nestlé Vital','Lançada no Brasil para 40+, em março de 2026','Não cadastrada')]
def mercado_html():
    lin=''.join(f'<tr><td><b>{html.escape(a)}</b></td><td>{html.escape(b)}</td><td><span class="st st{0 if "bem" in c.lower() else 1 if "pouco" in c.lower() or "queda" in c.lower() or "fora" in c.lower() or "1 SKU" in c else 2}">{html.escape(c)}</span></td></tr>' for a,b,c in MERC)
    return f'<div class="gt">Em alta no mercado brasileiro<small>E a situação de cada marca no portfólio da rede</small></div><table class="ctb ma-tb"><thead><tr><th>Marca</th><th>O que aconteceu</th><th>Na rede</th></tr></thead><tbody>{lin}</tbody></table><div class="leg leg-graf"><span><i style="background:#596D49"></i>Vende bem</span><span><i style="background:#CA942A"></i>Vende pouco</span><span><i style="background:#CA3C2E"></i>Falta no portfólio</span></div>'
def lacunas_html():
    rs=json.loads((R/'analise/marcas_alta.json').read_text())['recomendacoes']
    AC=[('entrar em teste','Entrar em teste','teste'),('ampliar','Ampliar','mercado'),('negociar plano','Negociar plano','handshake'),('observar','Observar','olho')]
    bts='';pns=''
    for i,(k,nm,ic_) in enumerate(AC):
        it=[r for r in rs if r['acao']==k]
        bts+=f'<button class="aba{" on" if i==0 else ""}" data-k="m{i}">{ic(ic_)} {nm} · {len(it)}</button>'
        lin=''.join(f'<tr><td><b>{html.escape(r["marcaOuTipo"])}</b><small>{html.escape(r["categoria"])} · {html.escape(r["motor"])}</small></td><td>{html.escape(r["situacao"])}</td><td>{html.escape(r["dadoInterno"])}</td><td>{html.escape(r["evidenciaExterna"])}</td><td>{html.escape(r["risco"])}</td></tr>' for r in it)
        pns+=f'<div class="painel{" on" if i==0 else ""}" data-k="m{i}"><table class="ctb la-tb"><thead><tr><th>Marca ou tipo</th><th>Situação na rede</th><th>O que a venda diz</th><th>O que o mercado diz</th><th>Cuidado</th></tr></thead><tbody>{lin}</tbody></table></div>'
    return f'<div data-abas class="la"><div class="abas">{bts}</div>{pns}</div>'
def loja3d():
    f=R/'assets/img/novas/loja3d.json'
    if not f.exists() or not (R/'assets/img/novas/loja3d-g.jpg').exists(): return '<p class="lead">Render 3D da loja em finalização: entra na próxima publicação.</p>'
    Z=json.loads(f.read_text());bts='';pns=''
    PERC=['entrada','fundo','direita','granel','mesa','esquerda','caixa']
    ETQ={'entrada':('Entrada e vitrine','porta'),'fundo':('Destino: proteínas, creatina, colágeno','whey'),'direita':('Rotina: vitaminas, ômegas, intestino','pilula'),'granel':('Granel: 20 a 40 tubos','trigo'),'mesa':('Empório','presente'),'esquerda':('Abastecer: barras, cafés, despensa, chás','cesta'),'caixa':('Caixa: pequeno formato','caixa')}
    for i,T in enumerate('gmp'):
        z=Z[T];U=T.upper();nm=TAMN[U]
        bts+=f'<button class="aba{" on" if i==0 else ""}" data-k="t{T}"><b>Loja {U}</b><span>{nm}</span></button>'
        pts=[z[k] for k in PERC if k in z];k_=100/62.5
        pa='M'+' L'.join(f'{x:.1f} {y*.625:.1f}' for x,y in pts)
        pins=''.join(f'<div class="l3-p" style="left:{z[k][0]}%;top:{z[k][1]}%"><i class="lp-pulso">{j+1}</i></div>' for j,k in enumerate(PERC) if k in z)
        ACT={'entrada':'Vê a vitrine e entra. Os primeiros passos não vendem.','fundo':'Vai ao que veio buscar: o motivo da visita conduz o fluxo.','direita':'Conversa com a atendente sobre a rotina de saúde.','granel':'Prova uma castanha e leva para a semana.','mesa':'Descobre o empório: compra não planejada.','esquerda':'Completa a despensa da semana.','caixa':'Último item, em pequeno formato.'}
        lista=''.join(f'<li><i>{j+1}</i><div><b>{ic(ETQ[k][1])} {ETQ[k][0]}</b><span>{ACT[k]}</span></div></li>' for j,k in enumerate(PERC) if k in z)
        pns+=f'<div class="painel{" on" if i==0 else ""}" data-k="t{T}"><div class="l3-g"><div class="l3"><img src="assets/img/novas/loja3d-{T}.jpg" alt="Loja {U} em 3D, simulação"><svg viewBox="0 0 100 62.5" preserveAspectRatio="none"><path d="{pa}" fill="none" stroke="#CA3C2E" stroke-width=".35" stroke-dasharray="1 .8" class="marcha2"/><circle r=".9" fill="#CA3C2E" class="so-tela-svg"><animateMotion dur="14s" repeatCount="indefinite" path="{pa}"/></circle></svg>{pins}</div><ol class="l3-l">{lista}</ol></div></div>'
    return f'<div data-abas class="l3t"><div class="abas">{bts}</div>{pns}</div>'
def aplicar(t):
    t=t.replace('{{loja3d}}',loja3d() if '{{loja3d}}' in t else '')
    t=t.replace('{{marcas_alta}}',marcas_alta_html() if '{{marcas_alta}}' in t else '').replace('{{marcas_mercado}}',mercado_html() if '{{marcas_mercado}}' in t else '').replace('{{lacunas}}',lacunas_html() if '{{lacunas}}' in t else '')
    if '{{plano_' not in t and '{{loja_tabs}}' not in t and '{{cat_tab}}' not in t: return t
    r=PH.dados()
    for T in 'PMG': t=t.replace('{{plano_%s}}'%T,plano_tabs(r,T)).replace('{{fora_%s}}'%T,fora(r,T))
    t=t.replace('{{loja_tabs}}',loja_tabs(r)).replace('{{cat_tab}}',categorias_tabela(r)).replace('{{regua_precos}}',regua_precos())
    tab,bars,pay,tot=custo(r);t=t.replace('{{custo_tab}}',tab).replace('{{custo_bars}}',bars)
    for T in 'PMG':
        pc,mt=horas(r,T)
        t=t.replace('{{hpc_%s}}'%T,n(round(pc,0))).replace('{{hmt_%s}}'%T,n(round(mt,0))).replace('{{htt_%s}}'%T,n(round(pc+mt,0))).replace('{{dia_%s}}'%T,n(round((pc+mt)/(3*6)+.49,0)))
        t=t.replace('{{cst_%s}}'%T,'R$ '+br(round(pay[T],-2)));t=t.replace('{{cpag_%s}}'%T,'R$ '+br(round(pay[T]/12/.35,-1)))
    return t
if __name__=='__main__':
    r=PH.dados();tab,bars,pay,tot=custo(r);print({T:quant(r,T) for T in 'PMG'});print(pay,tot)

# ---- Manual de cada categoria ----
GUIA={
'Proteínas':dict(sort='Cortar a cauda e manter, por linha, até 2 sabores na P, 3 na M e 4 na G. Whey, isolada, beef e vegana em prateleiras separadas.',lugar='Parede do fundo, no melhor trecho. É o principal motivo da visita e conduz a cliente pela loja.',preco='Referência no whey mais comparado. Margem nos isolados e veganos. Conferir semanalmente os preços do mercado alimentar.',com='Testeira “Proteínas”. Faixa por tipo. Selo vegano e sem lactose. Régua: dose por refeição.',promo='Encarte só no calendário. Degustação de lançamento paga pela marca. Sem desconto fixo.',repo='Pote de 900 g ou mais fica nos níveis 5 e 6. Conferir ruptura dos líderes todo dia.',pode='Bloco por marca dentro do tipo. Sachê de teste junto ao pote.',nao='Misturar whey e vegana na mesma prateleira. Prometer emagrecimento ou ganho de massa.',erro='Blocar só por marca: a cliente não acha o tipo que veio buscar.',meta='Participação na venda, ruptura nos líderes, venda por módulo'),
'Creatina':dict(sort='Núcleo enxuto: poucos produtos fazem quase toda a venda. Creapure, monohidratada e goma à parte.',lugar='Uma casa só, no fundo, ao lado de proteínas. Creapure nos olhos, comum logo abaixo, goma no alto.',preco='Crealift e Creafort na lista de referência. Comparar com farmácia e mercado.',com='Faixa “Creapure” e “Monohidratada”. Régua: como tomar. Goma com faixa própria.',promo='Combo com barra ou coqueteleira no início do ano e no verão.',repo='Reposição semanal do líder. Faltou: etiqueta e 2 dias para repor.',pode='Duas posições secundárias com prazo, como ponta em janeiro.',nao='Espalhar creatina por vários setores. Prometer desempenho além do permitido.',erro='Manter muitas marcas iguais: a venda já está concentrada em poucas.',meta='Tempo para achar, ruptura, participação de marca própria'),
'Colágeno':dict(sort='Separar pele e beleza de articular. Reduzir produtos muito parecidos.',lugar='Fundo, ao lado de proteínas, em lugar visível.',preco='Valor: a cliente paga pela orientação. Pesquisar só os líderes.',com='Faixa “Pele e beleza” e “Articular”. Régua “para que serve”.',promo='Destaque do Mês e Dia das Mães.',repo='Reposição semanal. Sem pote pesado no alto.',pode='Combinar com vitamina C na conversa, sem alegação.',nao='Prometer rejuvenescimento ou tratamento.',erro='Deixar o colágeno disperso em beleza e proteína.',meta='Itens por cupom, venda por módulo'),
'Performance':dict(sort='Agrupar por uso: pré-treino, aminoácidos, energia e hidratação. Lista curta na loja P.',lugar='Fundo, ao lado de proteínas. Sachê e gel perto do caixa.',preco='Valor, com referência no líder de cada uso.',com='Faixas por uso. Régua: quando tomar.',promo='Verão e eventos locais.',repo='Calor aumenta a saída de hidratação: revisar no verão.',pode='Teste de marcas locais de esporte, dentro dos 20%.',nao='Prometer resultado de desempenho.',erro='Deixar a categoria inflada na loja pequena.',meta='Giro, venda por módulo'),
'Bem-Estar':dict(sort='Organizar por benefício permitido. Magnésio e inositol pedem conversa.',lugar='Fundo ou lateral, junto da mentora.',preco='Valor: pouca comparação direta.',com='Nomes da árvore da rede, sem citar doença. Régua de uso.',promo='Destaque do Mês com roteiro de atendimento.',repo='Reposição semanal, com atenção à validade.',pode='Roteiro: pergunta, explica uso, respeita o profissional.',nao='Citar insônia, ansiedade ou qualquer condição.',erro='Nome de categoria que promete cura.',meta='Conversas registradas, itens por cupom'),
'Longevidade':dict(sort='Dar casa própria: coenzima, NAC e glicina, cúrcuma.',lugar='Lateral de saúde, na altura dos olhos.',preco='Valor. Pesquisar só os líderes.',com='Faixa “Longevidade” e régua de uso. A palavra não pode virar promessa.',promo='Destaque do Mês no segundo semestre.',repo='Giro menor: atenção à validade.',pode='Testar novidade para 40+, com regra de saída.',nao='Prometer viver mais ou “antienvelhecimento”.',erro='Deixar a categoria escondida em vitaminas.',meta='Venda por módulo, perda por validade'),
'Vitaminas':dict(sort='Organizar por nutriente, de A a Z. Reduzir duplicados de um mesmo nutriente.',lugar='Lateral de rotina, no caminho.',preco='Valor, com magnésio como referência.',com='Placa “Vitaminas de A a Z”. Faixa por nutriente. Régua de uso.',promo='Outono e inverno para imunidade. Combos só no calendário.',repo='Muitos itens pequenos: conferir etiqueta toda semana.',pode='Leitura alfabética dentro do nutriente.',nao='Citar gripe ou dizer que previne doença.',erro='Organizar por marca e dificultar achar o nutriente.',meta='Tempo para achar, itens por cupom'),
'Ômegas':dict(sort='Poucos produtos fazem a maior parte da venda. Separar ômega 3, krill e vegano.',lugar='Lateral de rotina, nos olhos.',preco='Valor: a cliente paga pela orientação. Mentora explica concentração.',com='Placa “Ômegas” legível da porta. Régua: “Tome com a refeição”.',promo='Agosto como mês de ômega, com verba da marca-líder.',repo='Não deixar líder faltar: a cliente volta em 30 a 40 dias.',pode='Plano com marca-líder: ponta, régua e treino.',nao='Associar a tratamento de saúde.',erro='Depender de uma só marca, sem plano negociado.',meta='Ruptura, frequência, venda por módulo'),
'Intestino':dict(sort='Probióticos, fibras e glutamina em uma casa própria.',lugar='Lateral de rotina, ao lado de ômegas.',preco='Valor.',com='Faixa por tipo e régua de uso.',promo='Destaque do Mês.',repo='Atenção a produto que pede armazenagem especial.',pode='Roteiro de atendimento sobre rotina.',nao='Citar doenças do intestino.',erro='Espalhar probióticos por vitaminas e fitoterápicos.',meta='Itens por cupom, giro'),
'Imunidade':dict(sort='Própolis, vitamina C e ervas. Cresce no inverno, reduz no resto do ano.',lugar='Lateral na época fria, depois volta ao bloco de bem-estar.',preco='Valor, com oferta no calendário.',com='Selo de atributo. Nada de citar gripe.',promo='Outono-Inverno, com ponta.',repo='Comprar por sazonalidade para evitar sobra.',pode='Ampliar frentes por data.',nao='Prometer “proteger” ou “prevenir”.',erro='Manter o mesmo espaço o ano todo.',meta='Venda no período, perda por validade'),
'Kids e Peso':dict(sort='Ganha módulo só em loja maior. Nas outras, fica na gôndola de bem-estar.',lugar='Parte baixa para kids, ao alcance da família.',preco='Valor.',com='Faixa simples.',promo='Volta às aulas.',repo='Conferir validade.',pode='Destaque por data.',nao='Prometer perda de peso.',erro='Dar módulo a categoria que não se paga.',meta='Venda por módulo'),
'Barras e snacks':dict(sort='Reduzir a cauda. Barras proteicas, naturais, chips e salgados separados.',lugar='Meio da loja, no caminho, e caixa para o que gira.',preco='Referência no item de maior giro. Baixo desembolso.',com='Faixa por tipo. Selo sem glúten ou vegano.',promo='Ponta de verão. Multipack no calendário.',repo='Alto giro: reposição diária dos líderes.',pode='Posição secundária no caixa e na ponta.',nao='Display solto fora da biblioteca.',erro='Manter centenas de itens que quase não vendem.',meta='Itens por cupom, frequência, ruptura'),
'Cafés funcionais':dict(sort='Reduzir a dependência de uma só marca. Supercoffee, cápsulas e cafés separados.',lugar='Meio da loja, perto de barras.',preco='Referência em Supercoffee, comparada com o mercado.',com='Faixa por formato.',promo='Lançamento com degustação.',repo='Reposição semanal.',pode='Sachê de 10 g no caixa.',nao='Prometer energia sem base.',erro='Concorrer só por preço com o supermercado.',meta='Participação de marca, itens por cupom'),
'Despensa':dict(sort='Recortar por uso: farinhas, pastas, adoçantes, leites, massas, cereais, biscoitos. Selo é atributo, não setor.',lugar='Parede lateral de rotina.',preco='Valor nos selos. Referência em poucos itens básicos.',com='Selos do cadastro: sem glúten, zero açúcar, vegano. Sem departamento próprio.',promo='Encarte pontual.',repo='Muitos itens: revisar cauda a cada trimestre.',pode='Regional dentro dos 20%.',nao='Criar uma prateleira por restrição alimentar.',erro='Oito departamentos diferentes para a mesma lógica.',meta='Frequência, venda por módulo, itens sem venda'),
'Chás':dict(sort='Caixas e sachês de um lado, folhas e misturas do outro.',lugar='Parede própria ou lateral, com leitura horizontal.',preco='Valor.',com='Faixa por tipo e benefício permitido.',promo='Outono-Inverno.',repo='Muitos itens: cuidar da validade.',pode='Parede horizontal, por sabor.',nao='Alegação terapêutica.',erro='Espalhar chá por vários departamentos.',meta='Venda por módulo, itens sem venda'),
'Granel':dict(sort='Parede de 20 a 40 tubos. Castanhas, sementes e frutas primeiro. 2 tubos livres para o local.',lugar='Da porta se vê. Parede ou ilha no meio da loja.',preco='Oportunidade no encarte: 1 oferta por edição. Preço por quilo sempre claro.',com='Placa “Granel”, família e etiqueta de tubo. Potinho de prova.',promo='Ponta de castanhas no fim de ano.',repo='Chegou a um terço, repõe no mesmo dia. Tubo limpo.',pode='Compra começa pequena e vira hábito.',nao='Deixar tubo vazio ou sujo.',erro='Esconder a parede nos fundos.',meta='Granel na venda, ruptura de tubo, frequência'),
'Empório':dict(sort='Entrar com curadoria: 36, 68 ou 96 produtos. Passa pelo filtro de 4 perguntas.',lugar='Mesa no vão central e módulos próprios. Azeite nos olhos, garrafa embaixo, chocolate no alto.',preco='Valor: a partir de R$ 50 nos especiais. Procedência vira motivo de compra.',com='Faixa de ocasião: “À mesa”, “Receber”, “Presentear”.',promo='Páscoa, Mães, Namorados, Inverno, Pais, Natal. 1 oferta por encarte.',repo='Regra de validade por lote. Perda acima de 5% acende o alerta.',pode='Mesa do mês com um jantar inteiro.',nao='Vinho sem CNAE e contrato verificados. Marca que o mercado vende mais barato.',erro='Empório disperso, sem ocasião clara.',meta='Empório na venda, cupons com empório, perda por validade'),
'Caixa':dict(sort='Pequeno formato: até 60 g. Barra, sachê e chocolate pequeno.',lugar='Balcão e passagem. Posição secundária, nunca a única.',preco='Baixo desembolso.',com='Display da biblioteca, sem cartaz de papel.',promo='Combos simples.',repo='Reposição diária.',pode='Trocar conforme a data.',nao='Poluir o balcão.',erro='Usar o caixa para escoar o que não vende.',meta='Itens por cupom, giro do display'),
}
def _n80(c):
    f=R/'analise/n80.json';d=json.loads(f.read_text())
    if c=='Empório': ks=[k for k in d if k.startswith('Empório')]
    else: ks=BASEMAP.get(c,[])
    a=sum(d[k][0] for k in ks if k in d);b=sum(d[k][1] for k in ks if k in d)
    return (f'{br(a)} de {br(b)}' if b else 'pequeno formato')
def _foto(e,fm,h=36):
    i=fm.get(str(e['sku']))
    return f'<img src="assets/produtos/{e["sku"]}.webp" loading="lazy" alt="" style="height:{h}px;width:auto;max-width:{h}px;object-fit:contain;mix-blend-mode:multiply">' if i else ''
def _prat(r,c,fm):
    T='M' if c in r['M']['cats'] else 'G';cc=r[T]['cats'].get(c)
    if not cc: return ''
    if 'tubos' in cc:
        fam={}
        for t in cc['tubos']: fam.setdefault(t['fam'],[]).append(t['nome'])
        return f'<div class="cmp-t">O que vai em cada fileira · loja {T}</div>'+''.join(f'<div class="cmp-n"><b>{html.escape(k)}</b><span>{html.escape(", ".join(v[:4]))}</span></div>' for k,v in fam.items())
    NI={1:'Alto',2:'Alto',3:'Olhos',4:'Olhos',5:'Mão',6:'Baixo'};out=f'<div class="cmp-t">O que vai em cima e embaixo · loja {T}, módulo 1</div>'
    for n in cc['niveis']:
        it=sorted([e for e in (n['mods'][0] if n['mods'] else [])],key=lambda e:-e['v'])[:3]
        fotos=''.join(_foto(e,fm) for e in it)
        nomes=', '.join(html.escape(e['mc']+' '+e['nome'])[:40] for e in it[:2])
        out+=f'<div class="cmp-n{" ol" if n["n"] in(3,4) else ""}"><i>{n["n"]}</i><em>{NI[n["n"]]}</em><div class="tx"><b>{html.escape(n["rot"])}</b><span>{nomes}</span></div><div class="fs">{fotos}</div></div>'
    return out
def manual_cat(r,c,fm):
    g=GUIA[c];cb=cat_base();cor=COR[MOT[c]];tx=TOK.get(cor,'#fff');p=pct(cb,c)
    k=BASEMAP.get(c,[None])[0];fx=cb.get(k) if k else None
    if c=='Empório': fx=cb.get('Empório: Chocolates e doces finos')
    mods=' · '.join(n(float(r[T]['modulos'].get(c,0))) if c!='Caixa' else {'P':'0,5','M':'0,5','G':'1'}[T] for T in 'PMG')
    prods=' · '.join(str(r[T]['cats'].get(c,{}).get('skus','junto')) for T in 'PMG')
    tiles=f'<div class="cmh"><div class="cmn" style="background:{cor};color:{tx}">{ic(ICO[MOT[c]])}<b>{html.escape(c)}</b><span>Motor {MOT[c]} · papel {PAPEL[c]}</span></div><div><em>{(br(p,1)+"%") if c!="Caixa" else "fora"}</em><span>da venda da rede</span></div><div><em>{_n80(c)}</em><span>produtos fazem 80%</span></div><div><em>{("R$ "+br(fx["p25"])+" a "+br(fx["p75"])) if fx else "baixo"}</em><span>faixa de preço{", por kg" if c=="Granel" else ""}</span></div><div><em>{mods}</em><span>módulos P · M · G</span></div><div><em>{prods}</em><span>produtos P · M · G</span></div></div>'
    pas=[('pacote','Sortimento',g['sort']),('local','Lugar',g['lugar']),('tag','Preço',g['preco']),('placa','Comunicação',g['com']),('calendario','Promoção',g['promo']),('caminhao','Reposição',g['repo'])]
    como=''.join(f'<li><span class="cic">{ic(i)}</span><div><b>{a}</b>{html.escape(b)}</div></li>' for i,a,b in pas)
    return f'''{tiles}<div class="cmg"><div><div class="cmp-t">Como fazer, passo a passo</div><ol class="cmo">{como}</ol></div><div class="cmp">{_prat(r,c,fm)}</div><div class="cmr"><div class="ok"><b>{ic('check')} Pode</b>{html.escape(g['pode'])}</div><div class="no"><b>{ic('aviso')} Não pode</b>{html.escape(g['nao'])}</div><div class="er"><b>{ic('lampada')} Erro comum</b>{html.escape(g['erro'])}</div><div class="kp"><b>{ic('grafico')} Cartão de metas</b>{html.escape(g['meta'])}</div><div class="jt"><b>{ic('alvo')} Objetivo</b>{PAPOBJ[PAPEL[c]]}</div></div></div>'''
PAPOBJ={'Destino':'Trazer a cliente à loja e dar lucro.','Rotina':'Fazer voltar toda semana.','Ocasião':'Aumentar a cesta e dar motivo para vir.','Conveniência':'Compra por impulso, no fim da visita.'}
def cat_manual_tabs(r):
    fm=PH.fotos();bts='';pns=''
    for i,c in enumerate(ORD):
        bts+=f'<button class="aba pa{" on" if i==0 else ""}" data-k="cm{i}"><i style="background:{COR[MOT[c]]}"></i>{html.escape(c)}</button>'
        pns+=f'<div class="painel{" on" if i==0 else ""}" data-k="cm{i}">{manual_cat(r,c,fm)}</div>'
    return f'<div data-abas class="pa-abas cm"><div class="abas">{bts}</div>{pns}</div>'
# ---- Ficha dos 12 tipos de loja ----
def dados12(): return json.loads((R/'analise/planogramas12.json').read_text())
T12={'P':'Até 50 m²','M':'50 a 80 m²','G':'80 a 120 m²','GG':'Acima de 120 m²'}
def _grp(nv,ids):
    sub={}
    for n in nv:
        if n['n'] not in ids: continue
        for m in n['mods']:
            for e in m: sub.setdefault(n['rot'],[]).append(e)
    out=[]
    for s,it in sub.items():
        it=sorted(it,key=lambda e:-e['v'])[:2]
        out.append(f'<b>{html.escape(s)}:</b> '+html.escape(', '.join((e['mc']+' '+e['nome'])[:30] for e in it)))
    return '<br>'.join(out[:2]) or 'Espaço da lista e do local'
def ficha12_tabs():
    R12=dados12();bts='';pns='';pri=True
    for T,tn in T12.items():
        bts+=f'<div class="f12"><b>{tn}</b>'
        for per in ('Suplemento forte','Equilibrado','Granel forte'):
            k=f'f{T}{per[:2]}';d=R12[f'{T}|{per}']
            bts+=f'<button class="aba{" on" if pri else ""}" data-k="{k}">{per}<small>{d["n"]} lojas</small></button>'
            lin=''
            for c in ORD:
                cc=d['cats'].get(c)
                if not cc: continue
                f=cc['f'];cor=COR[MOT[c]]
                if 'tubos' in cc:
                    fam={}
                    for t in cc['tubos']: fam.setdefault(t['fam'],[]).append(t['nome'])
                    fl=list(fam.items());tres=['<br>'.join(f'<b>{html.escape(a)}:</b> {html.escape(", ".join(b[:2]))}' for a,b in fl[i:j]) for i,j in((0,1),(1,3),(3,5))]
                    lin+=f'<tr><td><span class="pt" style="background:{cor}"></span><b>{html.escape(c)}</b></td><td class="num2">{n(float(f))}</td><td>{tres[0]}</td><td>{tres[1]}</td><td>{tres[2] or "Tubos livres"}</td></tr>';continue
                nv=cc['niveis']
                lin+=f'<tr><td><span class="pt" style="background:{cor}"></span><b>{html.escape(c)}</b></td><td class="num2">{n(float(f))}</td><td>{_grp(nv,(1,2))}</td><td class="olh">{_grp(nv,(3,4))}</td><td>{_grp(nv,(5,6))}</td></tr>'
            tot=int(sum(d['modulos'].values()));sk=sum(c.get('skus',len(c.get('tubos',[]))) for c in d['cats'].values())
            pns+=f'<div class="painel{" on" if pri else ""}" data-k="{k}"><p class="f12i"><b>{tn}, {per.lower()}.</b> {tot} módulos, {sk} produtos, {d["n"]} lojas neste quadro.</p><table class="ctb f12t"><thead><tr><th>Categoria</th><th>Módulos</th><th>{ic("placa")} Em cima, níveis 1 e 2</th><th>{ic("olho")} Nos olhos, níveis 3 e 4</th><th>{ic("mao")} Embaixo, níveis 5 e 6</th></tr></thead><tbody>{lin}</tbody></table></div>'
            pri=False
        bts+='</div>'
    return f'<div data-abas class="f12w"><div class="f12a">{bts}</div>{pns}</div>'
# ---- Núcleo, lista e local por categoria ----
def nucleo_tabs(r):
    fm=PH.fotos();L=json.loads((R/'analise/locais.json').read_text());bts='';pns=''
    def caixa(e):
        f=_foto(e,fm,62) or f'<span class="pk pk-{PH.formato(e["desc"])}" style="width:40px;height:56px;--c:#E5DDD1;color:#2b1209"></span>'
        return f'<div class="nl-p" title="{html.escape(e["desc"])}">{f}<span>{html.escape(e["mc"])}<small>{html.escape(e["nome"][:26])}</small></span></div>'
    i=0
    for c in ORD:
        if c=='Caixa': continue
        cats=[r[T]['cats'].get(c) for T in 'PMG']
        def lista(cc):
            if not cc: return []
            if 'tubos' in cc: return [dict(sku=t['sku'],desc=t['desc'],nome=t['nome'],mc='Granel',v=t['v']) for t in cc['tubos']]
            return [e for n_ in cc['niveis'] for m in n_['mods'] for e in m]
        P_,M_,G_=[lista(x) for x in cats]
        nucs={e['sku'] for e in P_};base=P_ or M_ or G_
        if not P_: nucs={e['sku'] for e in M_}
        nu=sorted([e for e in base],key=lambda e:-e['v'])
        ls=sorted({e['sku']:e for e in M_+G_ if e['sku'] not in nucs}.values(),key=lambda e:-e['v'])
        lo=[x for x in L.get(c,[]) if not x[0].lower().startswith(('sem marca','marcas diversas','stanley'))]
        bts+=f'<button class="aba pa{" on" if i==0 else ""}" data-k="nl{i}"><i style="background:{COR[MOT[c]]}"></i>{html.escape(c)}</button>'
        loc=''.join(f'<li><b>{html.escape(a)}</b> {b} lojas</li>' for a,b in lo[:7]) or '<li>Sem marca regional relevante hoje. A loja pode propor.</li>'
        pns+=f'<div class="painel{" on" if i==0 else ""}" data-k="nl{i}"><div class="nl-g"><div class="nl-c n1"><h4>Núcleo <small>{len(nu)} produtos na P. Vão em todas as lojas do tamanho</small></h4><div class="nl-ps">{"".join(caixa(e) for e in nu[:12])}</div></div><div class="nl-c n2"><h4>Lista aprovada <small>{len(ls)} produtos a mais nas lojas M e G</small></h4><div class="nl-ps">{"".join(caixa(e) for e in ls[:9])}</div></div><div class="nl-c n3"><h4>Local <small>Até 20%, a começar do nível 1</small></h4><p>Marcas que já vendem em poucas lojas, nesta categoria:</p><ul>{loc}</ul><p class="r">Passa pelo filtro de 4 perguntas e fica registrado no comitê.</p></div></div></div>'
        i+=1
    return f'<div data-abas class="pa-abas"><div class="abas">{bts}</div>{pns}</div>'
_ap_prev=aplicar
def aplicar(t):
    if '{{cat_manual}}' in t or '{{ficha12}}' in t or '{{nucleo_tabs}}' in t:
        r=PH.dados()
        t=t.replace('{{cat_manual}}',cat_manual_tabs(r)).replace('{{ficha12}}',ficha12_tabs()).replace('{{nucleo_tabs}}',nucleo_tabs(r))
    return _ap_prev(t)

def ficha12_manual():
    R12=dados12();h=''
    for T,tn in T12.items():
        for per in ('Suplemento forte','Equilibrado','Granel forte'):
            d=R12[f'{T}|{per}'];fil=''
            for c in ORD:
                cc=d['cats'].get(c)
                if not cc: continue
                if 'tubos' in cc:
                    fil+=''.join(f'<tr><td>{(i//7)+1}</td><td>{html.escape(c)}</td><td>Tubo {i+1}</td><td>{html.escape(t_["fam"])}</td><td>{t_["sku"]}</td><td>{html.escape(t_["desc"].title())}</td><td>1</td><td>{PH._r(t_.get("pmin"))} a {PH._r(t_.get("pmax"))}</td></tr>' for i,t_ in enumerate(cc['tubos']));continue
                for n_ in cc['niveis']:
                    for mi,m in enumerate(n_['mods']):
                        for e in m: fil+=f'<tr><td>{mi+1}</td><td>{html.escape(c)}</td><td>{n_["n"]} {PH.NIV[n_["n"]]}</td><td>{html.escape(n_["rot"])}</td><td>{e["sku"]}</td><td>{html.escape(e["desc"].title())}</td><td>{e["f"]}</td><td>{PH._r(e.get("pmin"))} a {PH._r(e.get("pmax"))}</td></tr>'
            h+=f'<details class="re noprint"><summary>{tn}, {per.lower()}: {int(sum(d["modulos"].values()))} módulos, {d["n"]} lojas</summary><table class="tb"><thead><tr><th>Módulo da categoria</th><th>Categoria</th><th>Nível</th><th>Subcategoria</th><th>SKU</th><th>Produto</th><th>Frentes</th><th>Faixa de preço, R$</th></tr></thead><tbody>{fil}</tbody></table></details>'
    return h
