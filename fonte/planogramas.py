# Monta os planogramas P, M e G a partir da base de produtos, com as regras do passo 7. Usado no deck e no kit.
import pandas as pd,numpy as np,math,re,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import receita as RC
R=RC.R
TAM={'P':('Até 50 m²',14,3,1,1),'M':('50 a 80 m²',28,5,1,2),'G':('Acima de 80 m²',39,6,2,3)}
FATOR_SUP=.55 # perfil Equilibrado: 55% do que sobra vai para suplemento
UTIL=86 # cm úteis por nível em um módulo de 90 cm
OLHOS=[3,4,2,5,1,6] # ordem de ocupação: olhos, mãos, alto, baixo
LOCAL=0 # o desenho sai cheio; a loja pode trocar até 20% por regional, a começar do nível 1
ALVO={'P':{'Empório':36},'M':{'Empório':68},'G':{'Empório':96}}
T_ATUAL=None
SUB={
 'Proteínas':[('Vegana',r'VEG|PLANT|ERVILHA|ARROZ'),('Isolada e hidrolisada',r'ISOLAD|HIDROLIS|ISO '),('Beef',r'BEEF|CARNE'),('Whey',r'WHEY'),('Outras proteínas',r'.')],
 'Creatina':[('Em goma',r'GUMM|GOMA'),('Creapure',r'CREAPURE|CREALIFT|CREAFORT'),('Monohidratada',r'.')],
 'Ômegas':[('Vegano e algas',r'ALGA|VEG|LINHA'),('Krill',r'KRILL'),('Ômega 3',r'.')],
 'Vitaminas':[('Magnésio',r'MAGNES|\bMG\b'),('Vitaminas D e K',r'\bD3\b|\bK2\b|VITAMINA D|VIT D|VITAMINAD'),('Complexos',r'MULTI|COMPLEX|POLIVIT|\bA-Z\b|\bAZ\b'),('Vitamina C e B',r'VITAMINA C|VIT C|\bB12\b|COMPLEXO B|METIL'),('Minerais',r'ZINCO|SELEN|FERRO|CALCIO|POTASS|IODO'),('Outras',r'.')],
 'Colágeno':[('Articular',r'TIPO II|UC.?II|ARTIC|MOVE'),('Pele e beleza',r'.')],
 'Barras e snacks':[('Barras proteicas',r'BOLD|PROTEIN|PROTEICA|YOPRO|WHEY'),('Barras naturais',r'BARRA|BARRINHA'),('Chips e salgados',r'CHIPS|SALGAD|SNACK|PIPOCA'),('Outros snacks',r'.')],
 'Despensa':[('Farinhas e flocos',r'FARINHA|POLVILHO|AVEIA|FLOCO'),('Pastas e manteigas',r'PASTA|MANTEIGA|TAHINE|CREME DE'),('Adoçantes',r'XILITOL|STEVIA|ERITRITOL|ADOCANTE|ACUCAR|SWEET'),('Leites e bebidas',r'LEITE|BEBIDA|KOMBUCHA|SUCO|AGUA'),('Massas e molhos',r'MASSA|MACARRAO|ESPAGUETE|PENNE|MOLHO'),('Cereais e granolas',r'GRANOLA|CEREAL|MUESLI'),('Biscoitos e pães',r'BISCOITO|COOKIE|BOLACHA|PAO|TORRADA'),('Outros da despensa',r'.')],
 'Cafés funcionais':[('Supercoffee',r'SUPERCOFFEE'),('Cápsulas',r'CAPSULA|CAPS|NESPRESSO'),('Cafés',r'.')],
 'Chás':[('Sachês e caixas',r'SACH|\bCX\b|CAIXA|\d+\s?UN|\d+\s?SAQ'),('Folhas e misturas',r'.')],
 'Performance':[('Pré-treino',r'PRE.?TREINO|NITRO|PRE WORK'),('Aminoácidos',r'BCAA|GLUTAM|BETA|ALANIN|AMINO|EAA'),('Energia e hidratação',r'CAFEINA|ISOTON|\bGEL\b|HIDRAT|HYDRO|ELETRO'),('Outros',r'.')],
 'Longevidade':[('Coenzima Q10',r'COQ|Q10|Q 10|UBIQUI'),('NAC, glicina e taurina',r'NAC|GLYCIN|GLICIN|TAURIN'),('Cúrcuma e antioxidantes',r'CURCUM|RESVER|ASTAX'),('Outros',r'.')],
 'Intestino':[('Probióticos',r'PROBIO|LACTO|BIFIDO|SIMBIO'),('Fibras e glutamina',r'FIBRA|PSYLLIUM|INULINA|GLUTAMINA|PREBIO'),('Outros',r'.')],
 'Imunidade':[('Própolis',r'PROPOLIS'),('Vitamina C e zinco',r'VITAMINA C|VIT C|ZINCO'),('Ervas e cogumelos',r'COGUM|EQUIN|ALHO|GENGIBRE|MELALEUCA'),('Outros',r'.')],
 'Kids e Peso':[('Kids',r'KIDS|INFANT|CRIANC|JUNIOR|BABY'),('Peso e composição',r'.')],
 'Bem-Estar':[('Intestino',r'^Saúde Int'),('Imunidade',r'^Imun'),('Kids e peso',r'^(Kids|Peso)'),('Longevidade',r'^Longev'),('Bem-estar',r'.')],
 'Caixa':[('Chocolate pequeno',r'^Empório'),('Barras',r'BARRA|PROTEIN|BOLD|CHIPS|SNACK'),('Sachê',r'.')],
 'Empório':[('Chocolates e doces finos',r'^Empório: Choc'),('Massas e risotos',r'^Empório: Mass'),('Azeites e vinagres',r'^Empório: Azei'),('Geleias e mel',r'^Empório: Gele'),('Molhos e condimentos',r'^Empório: Molh'),('Conservas e temperos',r'^Empório: (Cons|Temp)'),('Cafés especiais',r'^Empório: Caf')],
}
GRANEL=[('Castanhas e nozes',r'CASTANH|NOZ|AMENDO|AMÊNDO|CAJU|PECAN|MACADAM|PISTACH'),('Sementes',r'SEMENTE|CHIA|LINHACA|GIRASSOL|ABOBORA|QUINOA'),('Frutas secas',r'DAMASCO|AMEIXA|UVA|TAMARA|CRANBERRY|BANANA|FIGO|MANGA|ABACAXI|DESIDRAT'),('Snacks e chocolates',r'CHIPS|CHOCOLATE|DRAGE|MILHO|MUSTARD|SNACK|BISCOITO'),('Mix, cacau e farinhas',r'.')]
EXC=r'KIT|DEGUST|EXPOSITOR|BRINDE|AMOSTRA|DISPLAY|SACOLA|VALE '
def peso_g(d):
    m=re.search(r'(\d+[.,]?\d*)\s?KG',d)
    if m: return float(m.group(1).replace(',','.'))*1000
    m=re.search(r'(\d+)\s?G\b',d)
    if m: return float(m.group(1))
    m=re.search(r'(\d+)\s?DOSES',d)
    return int(m.group(1))*30 if m else 0
def largura(d):
    "Largura estimada da embalagem em cm. A trena confirma."
    if re.search(r'GUMM|GOMA',d): return 9
    if re.search(r'\d+\s?(CAPS|CPS|CAP|TABS|COMP|SOFTGEL)',d): return 7
    m=re.search(r'(\d+)\s?(ML|L)\b',d)
    if m:
        v=int(m.group(1))*(1000 if m.group(2)=='L' else 1);return 6 if v<=250 else 8 if v<=500 else 10
    p=peso_g(d)
    if p and p<=80: return 7
    if p and p<=250: return 9
    if p and p<=500: return 11
    if p and p<=1000: return 14
    if p>1000: return 17
    return 9
def curto(d,marca):
    t=d
    for w in str(marca).split(): t=re.sub(r'\b'+re.escape(w)+r'\b','',t)
    t=re.sub(r'\s+',' ',t).strip(' -')
    t=t.title().replace(' G',' g') if False else t.title()
    t=re.sub(r'(\d)G\b',r'\1 g',t);t=re.sub(r'(\d)Kg\b',r'\1 kg',t);t=re.sub(r'(\d)Ml\b',r'\1 ml',t);t=re.sub(r'(\d+)Caps\b',r'\1 cáps',t);t=re.sub(r'(\d+)Uni\b',r'\1 un',t)
    t=t or d.title()
    return t if len(t)<=30 else t[:30].rsplit(' ',1)[0]
MC={'ESSENTIAL NUTRITION':'Essential','TRUE SOURCE':'True Source','VITAFOR':'Vitafor','CAFFEINE ARMY':'Caffeine Army','PURAVIDA':'Puravida','EQUALIV':'Equaliv','DUX':'DUX','NUTRIFY':'Nutrify'}
def nome_marca(m): return MC.get(m,str(m).title())
def bases():
    d=RC.dados();L=pd.read_pickle(R/'analise/lojas_cluster.pkl')
    t=L.tam.replace({'GG':'G'})
    return d.assign(tam=d.loja.map(t),mes3=d.p.isin(RC.MES[-3:])),t
def _rot(m,dep): return m
def modulos():
    "Módulos por categoria em cada tamanho: venda x papel, com meio módulo como menor unidade."
    d,_=bases();out={}
    SETs=[(s,p,m,c) for s,p,m,c in RC.SET]
    for T,(n,tot,gr,ch,em) in TAM.items():
        x=d[d.tam==T];res=tot-gr-ch-em;su=round(res*FATOR_SUP);de=res-su;v=x[x.g.notna()].groupby('g').valor.sum()
        sem=x[x.setorf=='Suplementos sem setor'].valor.sum()
        cu=[s for s,_,m,_c in SETs if m=='Cuidar'];vc=v.reindex(cu).fillna(0)
        res_={}
        for mot,av in (('Cuidar',su),('Abastecer',de)):
            ss=[(s,p) for s,p,m,_c in SETs if m==mot and s!='Chás']
            pp={s:(v.get(s,0)+(sem*vc[s]/vc.sum() if mot=='Cuidar' else 0))*RC.PESO[p] for s,p in ss}
            tt=sum(pp.values());ideal={s:av*q/tt for s,q in pp.items()}
            f={s:(math.floor(i*2)/2 if i>=.25 else 0) for s,i in ideal.items()}
            f={s:(max(.5,q) if ideal[s]>=.25 else 0) for s,q in f.items()}
            while sum(f.values())>av:
                s=max((k for k in f if f[k]>.5),key=lambda k:f[k]-ideal[k]);f[s]-=.5
            for s in sorted(ideal,key=lambda k:ideal[k]-f[k],reverse=True):
                if sum(f.values())>=av:break
                f[s]+=.5
            res_.update(f)
        res_['Granel']=gr;res_['Empório']=em;res_['Chás']=ch
        out[T]=res_
    return out
def _end90(v,cima=False):
    v=float(v)
    if v<=0: return 0
    b=math.floor(v)
    return b+.9 if (cima and v>b+.9) is False and cima else ((b+1+.9) if cima else (b-1+.9 if v<b+.9 else b+.9))
_FX=None
def faixa_precos():
    "Mínimo e máximo sugeridos: de 25% a 90% do preço pago por loja e mês, em final 0,90. Corta queima de estoque e erro de cadastro."
    global _FX
    if _FX is None:
        d=RC.dados();d=d[(d.qtd>0)&(d.valor>0)].copy();d['u']=d.valor/d.qtd
        g=d.groupby('sku').u
        _FX=pd.DataFrame({'a':g.quantile(.25),'b':g.quantile(.90),'n':g.size()})
    return _FX
def preco(sku):
    F=faixa_precos()
    if sku not in F.index: return (None,None)
    a,b=F.loc[sku,'a'],F.loc[sku,'b']
    lo=_end90(a);hi=_end90(b,True)
    if hi<=lo: hi=lo+1
    return (round(lo,2),round(hi,2))
def escolher(x,cat,f,nuc=None):
    "Escolhe e posiciona. x = venda da categoria na faixa de loja."
    n=max(1,x.loja.nunique())
    g=x.groupby(['sku','desc','marca']).agg(v=('valor','sum'),q=('qtd','sum'),l=('loja','nunique'),r=('mes3','max')).reset_index()
    g=g[(g.r)&(~g.desc.str.contains(EXC))&(g.v>0)].sort_values('v',ascending=False)
    g=g[g.marca!='A GRANEL']
    cap=f*UTIL*6*.97;esc=[];usado=0;sem=47.7;tot=max(1,g.v.sum());acum=0
    teto=ALVO.get(T_ATUAL,{}).get(cat)
    conta={};LIM={'P':2,'M':3,'G':4}.get(T_ATUAL,4)
    for i,r in enumerate(g.itertuples()):
        lin_=' '.join(re.sub(r'\d+.*','',curto(r.desc,r.marca)).split()[:2]).upper();ch_=(r.marca,lin_)
        if conta.get(ch_,0)>=LIM: continue
        conta[ch_]=conta.get(ch_,0)+1
        if (teto and len(esc)>=teto) or (not teto and acum/tot>=.90): break
        w=largura(r.desc);qs=r.q/n/sem
        fr=int(min(3,max(1,math.ceil((qs/7*21+1)/6))))
        if usado+w*fr>cap:
            if usado+w<=cap: fr=1
            else: continue
        usado+=w*fr;acum+=r.v
        esc.append(dict(sku=int(r.sku),desc=r.desc,marca=r.marca,nome=curto(r.desc,r.marca),mc=nome_marca(r.marca),w=w,f=fr,v=float(r.v),q=float(r.q),s=None,pm=float(r.v/max(r.q,1))))
    # o espaço que sobra vira frente, por ordem de venda (líder do bloco até 3, demais até 2)
    for lim in (2,3):
        for j,e in enumerate(esc):
            if lim==3 and j>=max(1,len(esc)//8): break
            while e['f']<lim and usado+e['w']<=cap: e['f']+=1;usado+=e['w']
    # ainda sobra: entram os próximos produtos da venda, até encher
    ja={e['sku'] for e in esc}
    _fm=R/'assets/produtos/mapa.json';_fm=json.loads(_fm.read_text()) if _fm.exists() else {}
    for r in sorted(g.itertuples(),key=lambda r:(str(r.sku) not in _fm,-r.v)):
        if r.sku in ja or (teto and len(esc)>=teto): continue
        w=largura(r.desc)
        if usado+w>cap: continue
        usado+=w;esc.append(dict(sku=int(r.sku),desc=r.desc,marca=r.marca,nome=curto(r.desc,r.marca),mc=nome_marca(r.marca),w=w,f=1,v=float(r.v),q=float(r.q),s=None,pm=float(r.v/max(r.q,1))))
    for e in esc:
        while usado+e['w']<=cap and e['f']<4: e['f']+=1;usado+=e['w']
    # subcategoria, com pote grande sempre embaixo
    regras=SUB.get(cat,[('Geral',r'.')])
    for e in esc:
        if peso_g(e['desc'])>=900 and cat in('Proteínas','Vitaminas','Colágeno','Performance'): e['s']='Potes grandes';continue
        alvo=e['desc'] if cat not in('Empório','Bem-Estar','Caixa') else x[x.sku==e['sku']].setorf.iloc[0]
        if cat=='Caixa' and not alvo.startswith('Empório'): alvo=e['desc']
        for nome,pad in regras:
            if re.search(pad,alvo): e['s']=nome;break
        e['s']=e['s'] or 'Geral'
    de=pd.DataFrame(esc)
    sub=(de.groupby('s').v.sum()/de.assign(fr=de.f).groupby('s').fr.sum()).sort_values(ascending=False).index.tolist() if esc else []
    baixo=[s for s in sub if s=='Potes grandes'];sub=[s for s in sub if s!='Potes grandes']
    W=f*UTIL;fila=[]
    linhas={k:[] for k in range(1,7)};ocup={k:0 for k in range(1,7)};rot={k:None for k in range(1,7)}
    def poe(itens,ordem):
        for e in itens:
            larg=e['w']*e['f'];ok=False
            for k in ordem:
                if ocup[k]+larg<=W: linhas[k].append(e);ocup[k]+=larg;ok=True;break
            if not ok:
                k=min(ocup,key=ocup.get);linhas[k].append(e);ocup[k]+=larg
    if baixo: poe(sorted([e for e in esc if e['s']=='Potes grandes'],key=lambda e:-e['v']),[6,5])
    livres=[k for k in OLHOS if ocup[k]==0]
    for s in sub:
        it=sorted([e for e in esc if e['s']==s],key=lambda e:-e['v'])
        larg=sum(e['w']*e['f'] for e in it);nn=max(1,math.ceil(larg/W))
        faixa=livres[:nn];livres=livres[nn:]
        poe(it,faixa+sorted(ocup,key=ocup.get))
    # espaço local fica no alto e embaixo: olhos e mão são os primeiros a encher
    for k in (3,4,5,2):
        for dn in (1,6,2,5):
            if dn==k or OLHOS.index(dn)<=OLHOS.index(k): continue
            for e in sorted(linhas[dn],key=lambda e:e['w']*e['f']):
                if ocup[k]+e['w']*e['f']<=W and e['s']!='Potes grandes':
                    linhas[k].append(e);linhas[dn].remove(e);ocup[k]+=e['w']*e['f'];ocup[dn]-=e['w']*e['f']
    out=[]
    for k in range(1,7):
        it=linhas[k]
        # marca em bloco e líder no centro do nível
        por=pd.DataFrame(it).groupby('mc').v.sum().sort_values(ascending=False).index.tolist() if it else []
        cen=[]
        for j,m in enumerate(por):
            bl=sorted([e for e in it if e['mc']==m],key=lambda e:-e['v'])
            b2=[]
            for q,e in enumerate(bl): (b2.append(e) if q%2==0 else b2.insert(0,e))
            cen=cen+b2 if j%2==0 else b2+cen
        # quebra por módulo
        mods=[];atual=[];soma=0;lim=min(UTIL,W)
        for e in cen:
            lg=e['w']*e['f']
            if soma+lg>lim and atual: mods.append(atual);atual=[];soma=0
            atual.append(e);soma+=lg
        if atual: mods.append(atual)
        ss=[e['s'] for e in cen]
        out.append(dict(n=k,rot=max(set(ss),key=ss.count) if ss else 'Espaço local',mods=mods,livre=round(W-ocup[k])))
    for e in esc: e['pmin'],e['pmax']=preco(e['sku'])
    return dict(cat=cat,f=f,niveis=out,skus=len(esc),frentes=sum(e['f'] for e in esc),vTop=sum(e['v'] for e in esc),vCat=float(x.valor.sum()),cob=sum(e['v'] for e in esc)/max(1,float(g.v.sum())))
def granel(x,T):
    n={'P':20,'M':32,'G':40}[T]
    g=x.groupby(['sku','desc','marca']).agg(v=('valor','sum'),r=('mes3','max')).reset_index()
    g=g[g.r&~g.desc.str.contains(EXC)].sort_values('v',ascending=False).head(n)
    it=[]
    for r in g.itertuples():
        fam=next(nm for nm,p in GRANEL if re.search(p,r.desc));nome=re.sub(r'\s*A GRANEL','',r.desc).title()
        lo,hi=preco(int(r.sku));it.append(dict(sku=int(r.sku),desc=r.desc,nome=nome[:28],fam=fam,v=float(r.v),pmin=lo,pmax=hi))
    return dict(cat='Granel',tubos=it,skus=len(it),f=TAM[T][2],cob=sum(i['v'] for i in it)/max(1,float(x.valor.sum())))
def tudo():
    d,_=bases();M=modulos();res={}
    G2={'Vitaminas':'Vitaminas','Barras e snacks':None}
    global T_ATUAL
    for T in TAM:
        T_ATUAL=T
        x=d[d.tam==T];res[T]={'modulos':M[T],'cats':{}}
        for cat in ['Proteínas','Creatina','Ômegas','Vitaminas','Colágeno','Bem-Estar','Performance','Longevidade','Intestino','Imunidade','Kids e Peso','Barras e snacks','Cafés funcionais','Despensa','Chás','Empório','Granel']:
            if cat=='Granel': res[T]['cats'][cat]=granel(x[x.setorf=='Granel'],T);continue
            if cat=='Empório': y=x[x.setorf.astype(str).str.startswith('Empório')&~x.setorf.astype(str).str.contains('Vinhos|Queijos')];f=M[T]['Empório']
            else:
                chave=cat
                mapa={k:v for k,v in RC.G.items()};nomes=[k for k,v in mapa.items() if v==chave or (cat=='Barras e snacks' and v in('Barras','Barras e snacks'))  or (cat=='Intestino' and v in('Intestino','Saúde Intestinal'))]
                y=x[x.setorf.isin(nomes)]
                f=next((M[T][s] for s in M[T] if s in {mapa[k] for k in nomes}),None)
            if cat=='Bem-Estar':
                extra=[k for k,v in RC.G.items() if v in('Intestino','Imunidade','Kids e Peso','Longevidade') and M[T].get(v,0)==0]
                if extra: y=pd.concat([y,x[x.setorf.isin(extra)]])
            if f is None or y.empty or f==0: continue
            res[T]['cats'][cat]=escolher(y,cat,f)
        # caixa: fora da conta de módulos, como o frio e o café da loja. Posição secundária de quem é pequeno
        cx=x[x.setorf.isin(['Barras e snacks','Cafés funcionais','Café e cápsulas','Empório: Chocolates e doces finos'])]
        cx=cx[cx.desc.map(lambda s:0<peso_g(s)<=60)]
        ALVO.setdefault(T,{})['Caixa']={'P':24,'M':30,'G':42}[T]
        res[T]['cats']['Caixa']=escolher(cx,'Caixa',{'P':.5,'M':.5,'G':1}[T])
    return res
if __name__=='__main__':
    r=tudo()
    (R/'analise/planogramas.json').write_text(json.dumps(r,ensure_ascii=False))
    # núcleo: está no P; lista: entra só em M ou G
    for T in r:
        print(T,{k:v for k,v in r[T]['modulos'].items()},'soma',sum(r[T]['modulos'].values()))
        print('  ',{c:(v['skus'],round(v['cob']*100)) for c,v in r[T]['cats'].items()},'skus',sum(v['skus'] for v in r[T]['cats'].values()))
    for T,cat in (('P','Proteínas'),('M','Creatina')):
        c=r[T]['cats'][cat]
        for n in c['niveis']: print(T,cat,n['n'],n['rot'],n['livre'],[[ (e['mc'],e['nome'],e['f']) for e in m] for m in n['mods']])

# ---- 12 tipos de loja: tamanho x perfil ----
TAM12={'P':('Até 50 m²',14,3,1,1),'M':('50 a 80 m²',28,5,1,2),'G':('80 a 120 m²',39,6,2,3),'GG':('Acima de 120 m²',53,8,2,4)}
PER12={'Suplemento forte':(.65,0),'Equilibrado':(.55,0),'Granel forte':(.50,1)}
def modulos12(d,L,T,per):
    n,tot,gr,ch,em=TAM12[T];fs,ex=PER12[per];gr2=gr+ex;res=tot-gr2-ch-em;su=round(res*fs);de=res-su
    lojas=L[(L.tam==T)&(L.perfil==per)].index;x=d[d.loja.isin(lojas)];v=x[x.g.notna()].groupby('g').valor.sum()
    sem=x[x.setorf=='Suplementos sem setor'].valor.sum();cu=[s for s,_,m,_c in RC.SET if m=='Cuidar'];vc=v.reindex(cu).fillna(0);r={}
    for mot,av in (('Cuidar',su),('Abastecer',de)):
        ss=[(s,p) for s,p,m,_c in RC.SET if m==mot and s!='Chás']
        pp={s:(v.get(s,0)+(sem*vc[s]/max(1,vc.sum()) if mot=='Cuidar' else 0))*RC.PESO[p] for s,p in ss};tt=sum(pp.values())
        ideal={s:av*q/tt for s,q in pp.items()};f={s:(max(.5,math.floor(i*2)/2) if i>=.25 else 0) for s,i in ideal.items()}
        while sum(f.values())>av:
            s=max((k for k in f if f[k]>.5),key=lambda k:f[k]-ideal[k]);f[s]-=.5
        for s in sorted(ideal,key=lambda k:ideal[k]-f[k],reverse=True):
            if sum(f.values())>=av:break
            f[s]+=.5
        r.update(f)
    r['Granel']=gr2;r['Chás']=ch;r['Empório']=em
    return r,len(lojas)
def tudo12():
    global T_ATUAL
    L=pd.read_pickle(R/'analise/lojas_cluster.pkl');d=RC.dados();d=d.assign(mes3=d.p.isin(RC.MES[-3:]))
    ALVO.update({'GG':{'Empório':130}});res={}
    nomes=lambda cat:[k for k,v in RC.G.items() if v==cat]
    for T in TAM12:
        T_ATUAL='G' if T=='GG' else T
        lj=L[L.tam==T].index;xT=d[d.loja.isin(lj)]
        for per in PER12:
            ALVO.setdefault(T_ATUAL,{})['Empório']={'P':36,'M':68,'G':96,'GG':130}[T]
            M,n=modulos12(d,L,T,per);cats={}
            for cat,f in M.items():
                if f<=0: continue
                if cat=='Granel':
                    nt={'P':20,'M':32,'G':40,'GG':48}[T]+(6 if per=='Granel forte' else 0)
                    g=xT[xT.setorf=='Granel'].groupby(['sku','desc']).valor.sum().reset_index().sort_values('valor',ascending=False)
                    g=g[~g.desc.str.contains(EXC)].head(nt);it=[]
                    for r in g.itertuples():
                        fam=next(nm for nm,p in GRANEL if re.search(p,r.desc));lo,hi=preco(int(r.sku));it.append(dict(sku=int(r.sku),desc=r.desc,nome=re.sub(r'\s*A GRANEL','',r.desc).title(),fam=fam,pmin=lo,pmax=hi))
                    cats[cat]=dict(f=f,tubos=it);continue
                if cat=='Empório': y=xT[xT.setorf.astype(str).str.startswith('Empório')&~xT.setorf.astype(str).str.contains('Vinhos|Queijos')]
                else:
                    y=xT[xT.setorf.isin(nomes(cat))]
                    if cat=='Bem-Estar':
                        ex=[k for k,v in RC.G.items() if v in('Intestino','Imunidade','Kids e Peso','Longevidade') and M.get(v,0)==0]
                        if ex: y=pd.concat([y,xT[xT.setorf.isin(ex)]])
                if y.empty: continue
                cc=escolher(y,cat,f);cats[cat]=dict(f=f,niveis=cc['niveis'],skus=cc['skus'],frentes=cc['frentes'])
            res[f'{T}|{per}']=dict(n=n,modulos=M,cats=cats)
            print(T,per,n,sum(M.values()),sum(c.get('skus',len(c.get('tubos',[]))) for c in cats.values()))
    (R/'analise/planogramas12.json').write_text(json.dumps(res,ensure_ascii=False));return res
