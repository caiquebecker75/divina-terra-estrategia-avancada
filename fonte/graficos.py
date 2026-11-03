# Gráficos e planogramas gerados com os dados reais da base. Marcadores {{nome}} no HTML.
import pandas as pd,numpy as np,pathlib,html
R=pathlib.Path(__file__).resolve().parent.parent
C={'iog':'#F7F5F1','ave':'#E5DDD1','cho':'#7C381F','lin':'#BCAD99','cap':'#AC834C','ter':'#461D17','aca':'#CA942A','oli':'#596D49','mat':'#A9C094','pap':'#CA3C2E','cin':'#6F5F55'}
def br(v,c=0): return f'{v:,.{c}f}'.replace(',','X').replace('.',',').replace('X','.')
_df=None
def df():
    global _df
    if _df is None: _df=pd.read_pickle(R/'analise/vendas4.pkl')
    return _df
def scatter():
    L=pd.read_pickle(R/'analise/lojas_cluster.pkl');W,H=880,560;x0,y0=60,20;pw,ph=W-x0-20,H-y0-50
    X=lambda v:x0+(v-10)/(90-10)*pw;Y=lambda v:y0+ph-(v/65)*ph
    s=f'<svg viewBox="0 0 {W} {H}" class="grafico">'
    s+=f'<rect x="{X(10)}" y="{Y(65)}" width="{pw}" height="{Y(30)-Y(65)}" fill="{C["mat"]}" opacity=".22"/><rect x="{X(55)}" y="{Y(20)}" width="{X(90)-X(55)}" height="{Y(0)-Y(20)}" fill="{C["aca"]}" opacity=".18"/>'
    for v in range(10,91,20): s+=f'<text x="{X(v)}" y="{H-22}" text-anchor="middle" font-size="14" fill="{C["cin"]}">{v}%</text>'
    for v in range(0,61,20): s+=f'<text x="{x0-10}" y="{Y(v)+5}" text-anchor="end" font-size="14" fill="{C["cin"]}">{v}%</text><line x1="{x0}" x2="{W-20}" y1="{Y(v)}" y2="{Y(v)}" stroke="{C["ave"]}"/>'
    s+=f'<text x="{x0+pw/2}" y="{H-2}" text-anchor="middle" font-size="15" font-weight="600" fill="{C["ter"]}">Suplemento na venda da loja</text><text transform="translate(16,{y0+ph/2}) rotate(-90)" text-anchor="middle" font-size="15" font-weight="600" fill="{C["ter"]}">Granel na venda da loja</text>'
    s+=f'<text x="{X(11)}" y="{Y(62)}" font-size="15" font-weight="600" fill="{C["oli"]}">Granel forte · 16 lojas</text><text x="{X(89)}" y="{Y(19)-0}" text-anchor="end" font-size="15" font-weight="600" fill="{C["choco"] if "choco" in C else C["cho"]}">Suplemento forte · 16 lojas</text>'
    cor={'Granel forte':C['oli'],'Suplemento forte':C['aca'],'Equilibrado':C['lin']}
    SP=['DT PINHEIROS','DT ALPHAVILLE','DT PERDIZES','DT VILA MADALENA','DT AMERICANA','DT CARAGUATATUBA']
    for l,r in L.iterrows():
        if l in SP: continue
        s+=f'<circle cx="{X(r.sup):.1f}" cy="{Y(r.gra):.1f}" r="7" fill="{cor[r.perfil]}"><title>{html.escape(l)}: {r.sup:.0f}% suplemento, {r.gra:.0f}% granel</title></circle>'
    pos={'DT PINHEIROS':(10,-12,'start','Pinheiros'),'DT ALPHAVILLE':(-10,18,'end','Alphaville'),'DT VILA MADALENA':(-10,-12,'end','Vila Madalena'),'DT PERDIZES':(-10,6,'end','Perdizes')}
    for l in SP:
        if l not in L.index: continue
        r=L.loc[l];s+=f'<circle cx="{X(r.sup):.1f}" cy="{Y(r.gra):.1f}" r="9" fill="{C["pap"]}" stroke="{C["iog"]}" stroke-width="2"><title>{html.escape(l)}</title></circle>'
        if l in pos:
            a,b,c,n=pos[l];s+=f'<text x="{X(r.sup)+a:.1f}" y="{Y(r.gra)+b:.1f}" text-anchor="{c}" font-size="15" font-weight="600" fill="{C["ter"]}">{n}</text>'
    for l,n,a,b,c in [('DT SAO MIGU F01','São Miguel',12,5,'start'),('DT SOBRADINHO','Sobradinho',12,5,'start'),('DT VILA VELHA ES','Vila Velha',-12,-8,'end'),('DT SAO LEOPOLDO','São Leopoldo',12,-6,'start'),('DT VITORIA','Vitória',12,-6,'start')]:
        if l in L.index:
            r=L.loc[l];s+=f'<text x="{X(r.sup)+a:.1f}" y="{Y(r.gra)+b:.1f}" text-anchor="{c}" font-size="14" fill="{C["cin"]}">{n}</text>'
    return s+'</svg>'
def lorenz():
    d=df();v=d.groupby('sku').valor.sum().sort_values(ascending=False).values;c=np.cumsum(v)/v.sum();n=len(v);W,H=640,500;x0,y0=54,14;pw,ph=W-x0-14,H-y0-46
    X=lambda p:x0+p*pw;Y=lambda p:y0+ph-p*ph
    idx=np.unique(np.round(np.geomspace(1,n,160)).astype(int))-1
    pts=' '.join(f'{X(i/n):.1f},{Y(c[i]):.1f}' for i in idx)
    s=f'<svg viewBox="0 0 {W} {H}" class="grafico">'
    for p in (0,.25,.5,.75,1):
        s+=f'<line x1="{x0}" x2="{W-14}" y1="{Y(p)}" y2="{Y(p)}" stroke="{C["ave"]}"/><text x="{x0-8}" y="{Y(p)+5}" text-anchor="end" font-size="14" fill="{C["cin"]}">{int(p*100)}%</text><text x="{X(p)}" y="{H-24}" text-anchor="middle" font-size="14" fill="{C["cin"]}">{int(p*100)}%</text>'
    s+=f'<polygon points="{X(0)},{Y(0)} {pts} {X(1)},{Y(0)}" fill="{C["ave"]}" opacity=".6"/><polyline points="{pts}" fill="none" stroke="{C["cho"]}" stroke-width="4"/>'
    p9=2006/n
    s+=f'<line x1="{X(p9)}" x2="{X(p9)}" y1="{Y(0)}" y2="{Y(.8)}" stroke="{C["pap"]}" stroke-width="2" stroke-dasharray="5 5"/><line x1="{X(0)}" x2="{X(p9)}" y1="{Y(.8)}" y2="{Y(.8)}" stroke="{C["pap"]}" stroke-width="2" stroke-dasharray="5 5"/><circle cx="{X(p9)}" cy="{Y(.8)}" r="8" fill="{C["pap"]}"/><text x="{X(p9)+16}" y="{Y(.8)+26}" font-size="20" font-weight="600" fill="{C["ter"]}">9% dos SKUs, 80% da venda</text>'
    s+=f'<text x="{x0+pw/2}" y="{H-3}" text-anchor="middle" font-size="15" font-weight="600" fill="{C["ter"]}">SKUs com venda, do que mais vende ao que menos vende</text></svg>'
    return s
def linha():
    d=df();ms=sorted(d.p.unique());T=d.groupby('p').valor.sum()
    g=(d[d.depto=='GOURMET'].groupby('p').valor.sum()/T*100).reindex(ms);e=(d[d.bloco.notna()].groupby('p').valor.sum()/T*100).reindex(ms)
    W,H=820,430;x0,y0=48,26;pw,ph=W-x0-140,H-y0-42;X=lambda i:x0+i/(len(ms)-1)*pw;Y=lambda v:y0+ph-v/3*ph
    nom=['out','nov','dez','jan','fev','mar','abr','mai','jun','jul','ago','set','out']
    s=f'<svg viewBox="0 0 {W} {H}" class="grafico">'
    for v in (0,1,2,3): s+=f'<line x1="{x0}" x2="{x0+pw}" y1="{Y(v)}" y2="{Y(v)}" stroke="{C["ave"]}"/><text x="{x0-8}" y="{Y(v)+5}" text-anchor="end" font-size="14" fill="{C["cin"]}">{v}%</text>'
    for i,n in enumerate(nom): s+=f'<text x="{X(i)}" y="{H-14}" text-anchor="middle" font-size="14" fill="{C["cin"]}">{n}</text>'
    for ser,c,w in ((g,C['pap'],4),(e,C['oli'],4)):
        s+=f'<polyline fill="none" stroke="{c}" stroke-width="{w}" points="'+' '.join(f'{X(i):.1f},{Y(v):.1f}' for i,v in enumerate(ser.values))+'"/>'
    s+=f'<text x="{X(12)+10}" y="{Y(g.values[-1])+6}" font-size="17" font-weight="600" fill="{C["pap"]}">Gourmet {br(g.values[-1],1)}%</text><text x="{X(12)+10}" y="{Y(e.values[-1])+6}" font-size="17" font-weight="600" fill="{C["oli"]}">Empório {br(e.values[-1],1)}%</text></svg>'
    return s
def treemap():
    d=df();T=d.valor.sum();p=(d.groupby('setorf').valor.sum()/T*100).to_dict()
    Z=[('Cuidar · suplementos',C['cho'],'#fff',[('Proteínas',['Proteínas']),('Creatina',['Creatina']),('Vitaminas de A a Z',['Vitaminas de A a Z']),('Ômegas',['Ômegas']),('Colágeno e Beleza',['Colágeno e Beleza']),('Equilíbrio e Bem-Estar',['Equilíbrio e Bem-Estar']),('Performance',['Performance']),('Longevidade',['Longevidade']),('Saúde Intestinal',['Saúde Intestinal']),('Imunidade',['Imunidade']),('Kids, Peso',['Kids','Peso e Composição']),('A classificar',['Suplementos sem setor'])]),
    ('Abastecer · granel e despensa',C['oli'],'#fff',[('Granel',['Granel']),('Barras e snacks',['Barras e snacks']),('Cafés funcionais',['Café e cápsulas']),('Farinhas e básicos',['Farinhas e despensa']),('Chás',['Chás']),('Café da loja',['Café da loja']),('A classificar',['Despensa sem setor','Fora de setor'])]),
    ('Celebrar · empório',C['aca'],C['ter'],[('Chocolates',['Empório: Chocolates e doces finos']),('Geleias e mel',['Empório: Geleias e mel']),('Massas, molhos',['Empório: Massas e risotos','Empório: Molhos e condimentos']),('Azeites, conservas, vinhos, queijos, cafés e temperos',['Empório: Azeites e vinagres','Empório: Conservas e antepastos','Empório: Vinhos e espumantes','Empório: Queijos','Empório: Cafés especiais','Empório: Temperos e especiarias'])])]
    o='<div class="tree">'
    for nome,cor,tx,it in Z:
        tot=sum(sum(p.get(k,0) for k in ks) for _,ks in it)
        fl=max(tot,14)
        o+=f'<div class="zona" style="flex:{fl:.1f}"><div class="zt"><b>{nome}</b><span>{br(tot,1)}%</span></div><div class="zc">'
        for n,ks in it:
            v=sum(p.get(k,0) for k in ks);op='.55' if n=='A classificar' else '1'
            h=max(v,.9 if tot>10 else 3)
            o+=f'<div class="st" style="flex:{h:.2f} 1 0;background:{cor};color:{tx};opacity:{op}"><span>{n}</span><b>{br(v,1)}%</b></div>'
        o+='</div></div>'
    return o+'</div>'
# planograma do Empório: módulo de parede 0,90 m, 6 níveis
B={'Presentes':(C['lin'],C['ter']),'Chocolates':(C['ter'],'#fff'),'Azeites':(C['oli'],'#fff'),'Massas':(C['aca'],C['ter']),'Molhos':(C['pap'],'#fff'),'Conservas':(C['mat'],C['ter']),'Vinhos':(C['cho'],'#fff'),'Cafés':('#8a5a3c','#fff'),'Temperos':(C['cap'],'#fff'),'Biscoitos finos':('#d9c7ad',C['ter']),'Geleias e mel':('#e1b866',C['ter']),'Árabe':('#7f9266','#fff'),'Asiático':('#a65a44','#fff'),'Importados saudáveis':(C['ave'],C['ter']),'Vinagres':('#71845c','#fff'),'Adega':(C['cho'],'#fff'),'Espumantes':('#96502f','#fff')}
M1=[[('Presentes',5)],[('Chocolates',7)],[('Azeites',4),('Vinagres',2)],[('Massas',4),('Molhos',3)],[('Conservas',6)],[('Vinhos',5)]]
M2=[[[('Temperos',7)],[('Azeites',4),('Vinagres',3)],[('Massas',5)],[('Molhos',5)],[('Conservas',6)],[('Conservas',3),('Geleias e mel',3)]],[[('Presentes',5)],[('Biscoitos finos',6)],[('Chocolates',8)],[('Cafés',5),('Geleias e mel',2)],[('Espumantes',5)],[('Vinhos',5)]]]
M3=M2+[[[('Importados saudáveis',7)],[('Importados saudáveis',7)],[('Árabe',7)],[('Asiático',7)],[('Asiático',3),('Árabe',3)],[('Adega',5)]]]
GG=[[('Presentes',8)],[('Chocolates',4),('Biscoitos finos',4)],[('Azeites',3),('Conservas',4)],[('Adega',7)]]
M4=M3+[[[('Presentes',6)],[('Temperos',7)],[('Cafés',6)],[('Geleias e mel',6)],[('Adega',5)],[('Adega',5)]]]
def modulo(niv,w=206,h=440,nome=''):
    lv=len(niv);top=30;gh=(h-top-12)/lv;s=f'<svg viewBox="0 0 {w} {h}" class="mod"><rect x="0" y="0" width="{w}" height="{h}" rx="6" fill="{C["ter"]}"/><rect x="6" y="6" width="{w-12}" height="20" rx="3" fill="{C["iog"]}"/><text x="{w/2}" y="21" text-anchor="middle" font-size="12" font-weight="600" fill="{C["ter"]}">{nome}</text>'
    for i,row in enumerate(niv):
        y=top+i*gh;tot=sum(f for _,f in row);x=6;ww=w-12
        for n,f in row:
            bw=ww*f/tot;c,tx=B[n]
            s+=f'<rect x="{x+1:.1f}" y="{y+2:.1f}" width="{bw-2:.1f}" height="{gh-7:.1f}" rx="3" fill="{c}"/>'
            lab=n if bw>70 else n[:6]+'.'
            s+=f'<text x="{x+bw/2:.1f}" y="{y+gh/2-2:.1f}" text-anchor="middle" font-size="{12.5 if bw>110 else 11}" font-weight="600" fill="{tx}">{lab}</text><text x="{x+bw/2:.1f}" y="{y+gh/2+13:.1f}" text-anchor="middle" font-size="11" fill="{tx}" opacity=".85">{f} fr.</text>'
            x+=bw
        s+=f'<rect x="4" y="{y+gh-5:.1f}" width="{w-8}" height="3" fill="{C["lin"]}"/>'
    return s+'</svg>'
def frentes(ms): return sum(f for m in ms for r in m for _,f in r)
def emp(n):
    ms={1:[M1],2:M2,3:M3,4:M4}[n];nm={1:['Empório'],2:['À mesa, na cozinha','Para receber e presentear'],3:['À mesa, na cozinha','Para receber e presentear','Do mundo'],4:['À mesa, na cozinha','Para receber e presentear','Do mundo','Adega e presentes']}[n]
    return '<div class="mods">'+''.join(modulo(m,nome=nm[i]) for i,m in enumerate(ms))+'</div>'
# simulador: tamanho x perfil
TAM={'P':dict(n='Até 50 m²',tot=14,gr=3,ch=1,em=1),'M':dict(n='50 a 80 m²',tot=28,gr=5,ch=1,em=2),'G':dict(n='80 a 120 m²',tot=39,gr=6,ch=2,em=3),'GG':dict(n='Acima de 120 m²',tot=53,gr=8,ch=2,em=4)}
PER={'SF':('Suplemento forte',.65,0),'EQ':('Equilibrado',.55,0),'GF':('Granel forte',.50,1)}
CONT={('P','SF'):3,('P','EQ'):3,('P','GF'):3,('M','SF'):8,('M','EQ'):16,('M','GF'):8,('G','SF'):3,('G','EQ'):7,('G','GF'):2,('GG','SF'):2,('GG','EQ'):2,('GG','GF'):2}
EX={('P','SF'):'Sinop, Vila Velha, Campeche',('P','EQ'):'Caraguatatuba, Gurupi Centro, Eusébio Terrazo',('P','GF'):'Tramandaí, Pinhalzinho, Sobradinho',('M','SF'):'Alphaville, Campos, Sorriso, Moinhos',('M','EQ'):'Caxias, Torres, Santa Maria, Bento Gonçalves',('M','GF'):'São Miguel, Erechim, Osório, Venâncio',('G','SF'):'Vitória, Pinheiros, Americana',('G','EQ'):'Balneário, Lajeado, Campo Bom, Xanxerê',('G','GF'):'Novo Hamburgo, Dois Irmãos',('GG','SF'):'Chapecó, Praia de Belas',('GG','EQ'):'Joinville, Curitiba',('GG','GF'):'São Leopoldo, Florianópolis'}
def simulador():
    bts='';pns='';first=True
    for t,dt in TAM.items():
        for p,(pn,fs,extra) in PER.items():
            k=t+p;gr=dt['gr']+extra;em=dt['em'];ch=dt['ch'];res=dt['tot']-gr-em-ch;su=round(res*fs);de=res-su
            cells=[('Cuidar',su,C['cho'],'#fff'),('Abastecer',de,C['oli'],'#fff'),('Granel',gr,C['cap'],'#fff'),('Chás',ch,C['mat'],C['ter']),('Celebrar',em,C['aca'],C['ter'])]
            w=''.join(''.join(f'<i style="background:{c}"></i>' for _ in range(n)) for _,n,c,_ in cells)
            leg=''.join(f'<li><i style="background:{c}"></i><b>{n}</b> {nm}</li>' for nm,n,c,_ in cells)
            pns+=f'<div class="painel{" on" if first else ""}" data-k="{k}"><div class="parede t{t}">{w}</div><ul class="leg">{leg}</ul><div class="infos"><div><span class="num">{CONT[(t,p)]}</span><small>lojas neste quadro hoje</small></div><p class="p"><b>{pn}, {dt["n"]}.</b> Exemplos: {EX[(t,p)]}. Empório com {em} módulo{"s" if em>1 else ""} e {br(sum(1 for _ in range(0)))if False else ""}{ {1:"36",2:"68",3:"96",4:"130"}[em]} produtos.</p></div></div>'
            first=False
    tab='<table class="grade"><tr><th></th>'+''.join(f'<th>{v[0]}</th>' for v in PER.values())+'</tr>'
    for t,dt in TAM.items():
        tab+=f'<tr><th>{dt["n"]}</th>'+''.join(f'<td><button class="aba{" on" if t=="P" and p=="SF" else ""}" data-k="{t}{p}"><b>{CONT[(t,p)]}</b></button></td>' for p in PER)+'</tr>'
    return tab+'</table>',pns
def aplicar(t):
    a,b=simulador()
    M={'scatter':scatter,'lorenz':lorenz,'linha':linha,'treemap':treemap,'emp1':lambda:emp(1),'emp2':lambda:emp(2),'emp3':lambda:emp(3),'emp4':lambda:emp(4),'simgrade':lambda:a,'simpaineis':lambda:b}
    for k,f in M.items():
        if '{{'+k+'}}' in t: t=t.replace('{{'+k+'}}',f())
    return t

def ficha():
    M=M2
    return '<div class="mods" style="margin:10px 0 0 150px;gap:8px">'+''.join(modulo(m,nome=n).replace('class="mod"','class="mod" style="height:372px;margin:0"') for m,n in zip(M,['À mesa, na cozinha','Para receber e presentear']))+'</div>'
def planta(prop):
    c=dict(C)
    z=lambda x,y,w,h,f,t,tc='#fff',fs=13: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{f}"/><text x="{x+w/2}" y="{y+h/2+4.5}" text-anchor="middle" font-size="{fs}" font-weight="600" fill="{tc}">{t}</text>'
    s=f'<svg class="plan" viewBox="0 0 1500 400" font-family="General Sans"><rect x="0" y="0" width="1500" height="400" rx="8" fill="{c["ave"]}"/><rect x="26" y="20" width="1150" height="360" fill="{c["iog"]}"/><rect x="1176" y="150" width="310" height="230" fill="#ddd3c5"/><text x="1330" y="270" text-anchor="middle" font-size="15" fill="{c["cin"]}">Cozinha e estoque</text>'
    s+=z(30,60,30,110,c['lin'],'',c['ter'])+z(30,250,30,100,c['lin'],'',c['ter'])
    s+=f'<text x="16" y="205" font-size="13" fill="{c["cin"]}" transform="rotate(-90 16 205)" text-anchor="middle">Vitrine e fachada</text>'
    if not prop:
        for i in range(8): s+=z(70+i*88,24,84,44,c['cho'],'Suplem.')
        s+=z(780,24,90,44,c['mat'],'Freezer',c['ter'])
        s+=z(1040,24,130,44,c['cho'],'Encapsulados')
        for x,w,t in ((110,120,'Gôndola G'),(290,90,'Gôndola P'),(390,120,'Gôndola G'),(560,90,'Gôndola P')): s+=z(x,110,w,62,c['lin'],t,c['ter'])
        s+=z(860,105,190,60,c['ter'],'Caixa')
        s+=z(120,232,70,66,c['oli'],'Kombucha')+z(205,240,150,44,c['ave'],'Balança, expositor',c['ter'])
        s+=f'<rect x="240" y="180" width="330" height="50" rx="8" fill="none" stroke="{c["pap"]}" stroke-width="2.5" stroke-dasharray="7 6"/><text x="405" y="210" text-anchor="middle" font-size="14" font-weight="600" fill="{c["pap"]}">Vão central: 11 m² parados</text>'
        for x,w,t in ((70,60,'Granel P'),(135,130,'Granel 18'),(270,60,'Granel M'),(335,80,'Chás')): s+=z(x,336,w,40,c['cap'],t)
        for i in range(3): s+=z(420+i*88,336,84,40,c['aca'],'Farinhas',c['ter'])
        for x in (720,880): s+=z(x,250,120,70,c['ave'],'Mesas',c['ter'])
    else:
        n=['Proteínas','Proteínas','Creatina','Ômegas','A a Z','Colágeno','Bem-Estar','Intestino']
        for i,t in enumerate(n): s+=z(70+i*88,24,84,44,c['cho'],t,'#fff',12.5)
        s+=z(780,24,90,44,c['mat'],'Freezer',c['ter'])
        s+=z(1040,24,130,44,c['cho'],'Longevidade')
        for x,w,t,f,tc in ((110,120,'Barras e Snacks',c['oli'],'#fff'),(290,90,'Kids',c['oli'],'#fff'),(390,120,'Despensa',c['oli'],'#fff'),(560,90,'Sem Glúten',c['oli'],'#fff')): s+=z(x,110,w,62,f,t,tc,12.5)
        s+=z(860,105,190,60,c['ter'],'Caixa + chocolates')
        s+=z(120,240,70,58,c['oli'],'Kombucha')
        s+=f'<rect x="240" y="186" width="290" height="110" rx="55" fill="{c["aca"]}"/><text x="385" y="238" text-anchor="middle" font-size="17" font-weight="600" fill="{c["ter"]}">Mesa do Empório</text><text x="385" y="258" text-anchor="middle" font-size="13" fill="{c["ter"]}">tema do mês e degustação</text>'
        s+=z(70,336,345,40,c['cap'],'Granel: 20 tubos e prova, com placa visível da porta')
        for i,t in enumerate(['À mesa','Receber','Do mundo']): s+=z(420+i*88,336,84,40,c['aca'],t,c['ter'])
        for x in (720,880): s+=z(x,250,120,70,c['ave'],'Mesas',c['ter'])
        s+=f'<text x="650" y="300" font-size="13.5" font-weight="600" fill="{c["ter"]}">Empório perto</text><text x="650" y="318" font-size="13.5" font-weight="600" fill="{c["ter"]}">de quem fica</text>'
        for x,t in ((230,'PROTEÍNAS E CREATINA'),(500,'SAÚDE'),(405,'')): pass
    s+=f'<rect x="1000" y="330" width="170" height="44" rx="4" fill="{c["ave"]}"/><text x="1085" y="357" text-anchor="middle" font-size="13" fill="{c["ter"]}">Café e balcão</text></svg>'
    return s
_ap=aplicar
def aplicar(t):
    for k,f in {'ficha':ficha,'planta_a':lambda:planta(False),'planta_b':lambda:planta(True)}.items():
        if '{{'+k+'}}' in t: t=t.replace('{{'+k+'}}',f())
    return _ap(t)


def pontos(cols,grupos,tam=26):
    # grade de pontos: grupos = [(qtd,cor)]
    o=f'<div class="pontos" style="grid-template-columns:repeat({cols},{tam}px)">'
    k=0
    for q,c in grupos:
        for _ in range(q):
            o+=f'<i style="background:{c};--d:{k}"></i>';k+=1
    return o+'</div>'
_ap2=aplicar
def aplicar(t):
    M={'p100canal':lambda:pontos(10,[(48,C['lin']),(24,C['cap']),(15,C['oli']),(8,C['pap']),(5,C['ave'])],34),
       'p100sku':lambda:pontos(10,[(9,C['cho']),(91,C['ave'])],34),
       'p100venda':lambda:pontos(10,[(80,C['cho']),(20,C['ave'])],34),
       'rogers':rogers}
    for k,f in M.items():
        if '{{'+k+'}}' in t: t=t.replace('{{'+k+'}}',f())
    return _ap2(t)
def rogers():
    import math
    W,H=1000,330;pts=[]
    f=lambda x:math.exp(-((x-500)/170)**2/2)
    for x in range(0,1001,10): pts.append((x,H-60-f(x)*230))
    seg=[(0,160,C['aca'],'2 lojas','Piloto: Pinheiros e Alphaville'),(160,330,C['oli'],'8 lojas','Uma de cada tipo, com quem tem vontade'),(330,1000,C['cho'],'70 lojas','A rede, em lotes de 10 a 15 por mês')]
    s=f'<svg viewBox="0 0 {W} {H}" class="grafico" font-family="General Sans">'
    for a,b,c,_,_2 in seg:
        po=[p for p in pts if a<=p[0]<=b]
        s+=f'<polygon points="{a},{H-60} '+' '.join(f'{x},{y:.1f}' for x,y in po)+f' {b},{H-60}" fill="{c}"/>'
    s+=f'<line x1="0" x2="{W}" y1="{H-60}" y2="{H-60}" stroke="{C["ter"]}" stroke-width="3"/>'
    for a,b,c,n,d in seg:
        x=(a+b)/2 if b<1000 else 660
        s+=f'<text x="{x}" y="{H-32}" text-anchor="middle" font-size="19" font-weight="600" fill="{C["ter"]}">{n}</text>'
    return s+'</svg>'

def receita_tela():
    import receita as RC
    COR={'Cuidar':C['cho'],'Abastecer':C['oli']}
    bts='';pns=''
    for i,(l,n,t,e,tp) in enumerate(RC.EX):
        a=RC.alocar(l,t,e);k=f'r{i}'
        bts+=f'<button class="aba{" on" if i==0 else ""}" data-k="{k}"><b>{n}</b><span>{tp} · {t} módulos</span></button>'
        tiles=''
        for _,r in a.sort_values(['mot','f'],ascending=[False,False]).iterrows():
            if r.f<=0: continue
            tiles+=f'<div class="mdl" style="flex:{r.f} 1 0;background:{COR[r.mot]}"><b>{br(r.f,1).replace(",0","")}</b><span>{r.s}</span></div>'
        tiles+=f'<div class="mdl" style="flex:{e} 1 0;background:{C["aca"]};color:{C["ter"]}"><b>{e}</b><span>Empório</span></div>'
        cr=a[a.s=='Creatina'].iloc[0]
        pns+=f'<div class="painel{" on" if i==0 else ""}" data-k="{k}"><div class="parede2">{tiles}</div><p class="obs2">Creatina faz {br(cr.pv,1)}% da venda desta loja, mas {int(cr.n80)} produtos respondem por 80% dela: {br(cr.f,1).replace(",0","")} módulo basta, se estiver no melhor lugar. Número = módulos de 0,90 m, sem contar granel, frio, café e caixa.</p></div>'
    return bts,pns
_ap3=aplicar
def aplicar(t):
    if '{{rec_bts}}' in t:
        a,b=receita_tela();t=t.replace('{{rec_bts}}',a).replace('{{rec_pns}}',b)
    return _ap3(t)


def mapa_br():
    D={'RS':34,'SC':15,'SP':9,'PR':5,'RJ':3,'TO':3,'ES':2,'MT':2,'AM':2,'CE':2,'PA':1,'RR':1,'PB':1}
    P={'RR':(2,0),'AP':(4,0),'AM':(1,1),'PA':(3,1),'MA':(4,1),'CE':(5,1),'RN':(6,1),'AC':(0,2),'RO':(1,2),'TO':(3,2),'PI':(4,2),'PE':(5,2),'PB':(6,2),'MT':(2,3),'GO':(3,3),'BA':(4,3),'SE':(5,3),'AL':(6,3),'MS':(2,4),'DF':(3,4),'MG':(4,4),'ES':(5,4),'SP':(3,5),'RJ':(4,5),'PR':(3,6),'SC':(3,7),'RS':(3,8)}
    s=60;o=f'<svg viewBox="0 0 {7*s} {9*s}" class="grafico" font-family="General Sans">';k=0
    for uf,(x,y) in P.items():
        n=D.get(uf,0);c=C['ave'] if not n else (C['ter'] if n>=15 else C['cho'] if n>=5 else C['cap'])
        tx=C['lin'] if not n else '#fff'
        o+=f'<g class="apop" style="--d:{k};transform-box:fill-box;transform-origin:center"><rect x="{x*s+3}" y="{y*s+3}" width="{s-6}" height="{s-6}" rx="9" fill="{c}"/><text x="{x*s+s/2}" y="{y*s+s/2-(5 if n else -5)}" text-anchor="middle" font-size="14" fill="{tx}">{uf}</text>'
        if n:o+=f'<text x="{x*s+s/2}" y="{y*s+s/2+15}" text-anchor="middle" font-size="19" font-weight="600" fill="#fff">{n}</text>'
        o+='</g>';k+=1
    return o+'</svg>'
CURVAS={'far':('Farmácia',[4,5,3,2,2,1,1],C['lin']),'mer':('Supermercado premium',[3,4,5,1,2,4,3],C['oli']),'net':('Internet',[5,5,5,1,1,1,1],C['cap']),'hoje':('Divina Terra hoje',[2,3,3,5,5,2,3],C['pap']),'dest':('Divina Terra em 2028',[3,3,3,5,5,4,5],C['cho'])}
EIX=['Preço baixo','Conveniência','Variedade','Explicação','Curadoria de saúde','Curadoria de prazer','Experiência na loja']
def canvas(ativos,cor=True):
    W,H=1000,400;x0,y0=44,20;pw,ph=W-x0-30,H-y0-70;X=lambda i:x0+i*pw/6;Y=lambda v:y0+ph-(v-1)/4*ph
    o=f'<svg viewBox="0 0 {W} {H}" class="grafico" font-family="General Sans">'
    for v,l in ((1,'Pouco'),(5,'Muito')):
        o+=f'<text x="{x0-8}" y="{Y(v)+5}" text-anchor="end" font-size="13" fill="{C["cin"]}">{l}</text><line x1="{x0}" x2="{x0+pw}" y1="{Y(v)}" y2="{Y(v)}" stroke="{C["ave"]}"/>'
    for i,e in enumerate(EIX):
        a,*b=e.split(' ',1) if ' ' in e else (e,)
        o+=f'<line x1="{X(i)}" x2="{X(i)}" y1="{y0}" y2="{y0+ph}" stroke="{C["ave"]}"/><text x="{X(i)}" y="{H-42}" text-anchor="middle" font-size="16" font-weight="600" fill="{C["ter"]}">{a}</text>'
        if b:o+=f'<text x="{X(i)}" y="{H-22}" text-anchor="middle" font-size="16" font-weight="600" fill="{C["ter"]}">{b[0]}</text>'
    for k in ativos:
        n,v,c=CURVAS[k];w=6 if k=='dest' else 4
        o+='<polyline class="traco" fill="none" stroke="'+c+f'" stroke-width="{w}" stroke-linejoin="round" points="'+' '.join(f'{X(i)},{Y(z)}' for i,z in enumerate(v))+'"/>'
        for i,z in enumerate(v):o+=f'<circle cx="{X(i)}" cy="{Y(z)}" r="{7 if k=="dest" else 5}" fill="{c}"/>'
    return o+'</svg>'
def caminhada():
    b=planta(True)
    ov='''<path id="rotaCli" d="M40 300 C 120 300, 150 215, 240 215 S 420 90, 600 90 S 760 200, 640 250 S 420 305, 380 245 S 700 170, 900 150" fill="none" stroke="#CA3C2E" stroke-width="4" stroke-dasharray="8 9" stroke-linecap="round"/><circle r="13" fill="#CA3C2E" stroke="#fff" stroke-width="3"><animateMotion dur="16s" repeatCount="indefinite" rotate="0"><mpath href="#rotaCli"/></animateMotion></circle>'''
    for n,x,y in ((1,50,300),(2,240,215),(3,600,90),(4,640,250),(5,380,245),(6,900,150)):
        ov+=f'<circle cx="{x}" cy="{y}" r="16" fill="#461D17"/><text x="{x}" y="{y+6}" text-anchor="middle" font-size="17" font-weight="600" fill="#fff">{n}</text>'
    return b.replace('</svg>',ov+'</svg>')
_ap4=aplicar
def aplicar(t):
    M={'mapabr':mapa_br,'caminhada':caminhada,'canvas_far':lambda:canvas(['far','hoje']),'canvas_mer':lambda:canvas(['mer','hoje']),'canvas_net':lambda:canvas(['net','hoje']),'canvas_dest':lambda:canvas(['hoje','dest'])}
    for k,f in M.items():
        if '{{'+k+'}}' in t:t=t.replace('{{'+k+'}}',f())
    return _ap4(t)
