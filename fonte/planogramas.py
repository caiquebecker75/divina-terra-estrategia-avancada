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
 'Creatina':[('Em goma',r'GUMM|GOMA|\d+\s?UN\b'),('Creapure',r'CREAPURE|CREALIFT|CREAFORT'),('Monohidratada',r'.')],
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
 'Empório':[('Vinhos e espumantes',r'^Empório: Vinh'),('Biscoitos finos',r'^Empório: Choc.*(BISCOITO|COOKIE|WAFER|BISCOFF|ALFAJOR)'),('Chocolates',r'^Empório: Choc'),('Massas',r'^Empório: Mass'),('Azeites e vinagres',r'^Empório: Azei'),('Geleias e mel',r'^Empório: Gele'),('Molhos',r'^Empório: Molh'),('Conservas',r'^Empório: Cons'),('Temperos',r'^Empório: Temp'),('Cafés',r'^Empório: Caf')],
}
GRANEL=[('Mix, cacau e farinhas',r'FARINHA'),('Castanhas e nozes',r'CASTANH|NOZ|AMENDO|AMÊNDO|CAJU|PECAN|MACADAM|PISTACH'),('Sementes',r'SEMENTE|CHIA|LINHACA|GIRASSOL|ABOBORA|QUINOA'),('Frutas secas',r'DAMASCO|AMEIXA|UVA|TAMARA|CRANBERRY|BANANA|FIGO|MANGA|ABACAXI|DESIDRAT'),('Snacks e chocolates',r'CHIPS|CHOCOLATE|DRAGE|MILHO|MUSTARD|SNACK|BISCOITO'),('Mix, cacau e farinhas',r'.')]
EXC=r'OZ.MPIC|GLP.?1|CORDILHEIRA|KIT|DEGUST|EXPOSITOR|BRINDE|AMOSTRA|DISPLAY|SACOLA|VALE |GARRAFA TERM|GROWLER|COQUETELEIRA|CANECA|DIVERSOS|\bCASCO\b|CAFE DT|\bPACCO\b|STANLEY|SHAKER|SQUEEZE'
BANDAS=('dose','peq','gde') # um tamanho por prateleira, do menor (em cima) para o maior (embaixo)
NOME_B={'dose':'dose e sachê, até 100 g','peq':'até 500 g','gde':'acima de 500 g'}
def banda(d):
    "Faixa de tamanho da embalagem. Acima de 500 g só nos níveis 5 e 6."
    p=peso_g(d)
    if re.search(r'SACH[EÊ]?\b|SACHES|STICK|\bSHOT\b|\bDOSE\b',d) and p<=100 and not re.search(r'\d+\s?(SACH|STICK|UN\b|UNI)',d): return 'dose'
    if not p:
        m=re.search(r'(\d+[.,]?\d*)\s?(ML|L)\b',d)
        if m: p=float(m.group(1).replace(',','.'))*(1000 if m.group(2)=='L' else 1)
    if not p: return 'peq'
    return 'dose' if p<=100 else 'peq' if p<=500 else 'gde'
FORA_PROT=('Despensa sem setor','Farinhas e despensa','Barras e snacks','Café e cápsulas','Equilíbrio e Bem-Estar','Longevidade')
def casa(d,setor):
    "Um produto, uma casa: corrige o que o cadastro pôs na categoria errada por causa do sabor."
    if 'SUPERCOFFEE' in d and setor!='Café e cápsulas': return 'Café e cápsulas'
    if 'COENZIMA' in d and setor!='Longevidade': return 'Longevidade'
    if setor in ('Equilíbrio e Bem-Estar',) and re.search(r'GOMA XANTANA|FARINHA|POLVILHO',d): return 'Farinhas e despensa'
    if setor in ('Despensa sem setor','Farinhas e despensa') and re.search(r'\d+\s?(CAPS|CPS)\b',d): return 'Equilíbrio e Bem-Estar'
    if setor in FORA_PROT and setor!='Longevidade':
        if re.search(r'CREATIN',d): return 'Creatina'
        if re.search(r'\bOMEGA\b',d): return 'Ômegas'
    if setor in FORA_PROT or setor=='Proteínas':
        if 'COLAGENTEK' in d: return 'Colágeno e Beleza'
    if setor=='Proteínas' and peso_g(d)<200:
        if 'GRANOLA' in d: return 'Farinhas e despensa'
        if re.search(r'BARRA|\bBAR\b|CRISP|COOKIE|WAFER|ZAYTAS|CHIPS|BISCOITO|BROWNIE|CROC|\bPAO\b',d): return 'Barras e snacks'
    if setor in FORA_PROT:
        if re.search(r'POWER WHEY|WHEY COFFEE|WHEYFER',d): return setor
        if re.search(r'WHEY|CREAMASS|PROTEIN CRUSH|TRUE VEGAN|PROTEINA VEGETAL',d) and (peso_g(d)>=200 or not re.search(r'COOKIE|BISCOITO|BARRA|\bBAR\b|WAFER|BROWNIE|CRISP|CHIPS|\bPAO\b',d)): return 'Proteínas'
        if 'LIVESTRONG' in d: return 'Longevidade'
    return setor
_DC=None
def dados_casa():
    global _DC
    if _DC is None:
        d=RC.dados();pares=d[['desc','setorf']].astype(str).drop_duplicates();pares['novo']=[casa(a,b) for a,b in zip(pares.desc,pares.setorf)]
        mapa={(a,b):c for a,b,c in zip(pares.desc,pares.setorf,pares.novo)}
        setor=[mapa[k] for k in zip(d.desc.astype(str),d.setorf.astype(str))]
        _DC=d.assign(setorf=setor);_DC=_DC.assign(g=_DC.setorf.map(RC.G))
    return _DC
def peso_g(d):
    m=re.search(r'(\d+[.,]?\d*)\s?KG',d)
    if m: return float(m.group(1).replace(',','.'))*1000
    m=re.search(r'(\d+[.,]?\d*)\s?G\b',d)
    if m: return float(m.group(1).replace(',','.'))
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
    d=dados_casa();L=pd.read_pickle(R/'analise/lojas_cluster.pkl')
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
# Empório e creatina têm mapa fixo por nível, igual ao da tela do manual. Módulo inteiro: níveis 1 a 6.
MAPA={'Creatina':[['Em goma','Em goma','Creapure','Creapure','Monohidratada','Monohidratada']],
 'Empório':{1:[['Temperos|Cafés','Chocolates|Biscoitos finos','Azeites e vinagres','Massas|Molhos','Geleias e mel|Conservas','Vinhos e espumantes']],
  2:[['Temperos','Massas','Azeites e vinagres','Molhos','Conservas','Conservas|Geleias e mel'],['Cafés','Biscoitos finos|Chocolates','Chocolates','Geleias e mel','Chocolates','Vinhos e espumantes']]}}
MAPA['Empório'][3]=MAPA['Empório'][2]+[['Do mundo','Do mundo','Do mundo','Do mundo','Do mundo','Vinhos e espumantes']]
MAPA['Empório'][4]=MAPA['Empório'][3]+[['Temperos','Cafés','Chocolates','Geleias e mel','Vinhos e espumantes','Vinhos e espumantes']]
MUNDO=r'KIKKOMAN|SAKURA|SHOYU|MISSO|WASABI|TAYBE|SESAMO|TAHINE|HOMUS|HARISSA|ZAATAR|CURRY|NORI'
RESERVA={'Vinhos e espumantes':'Vinhos: só com licença'}
LIMITE={'P':2,'M':3,'G':4}
def _sub(cat,e,x):
    regras=SUB.get(cat,[('Geral',r'.')])
    alvo=e['desc'] if cat not in('Empório','Bem-Estar','Caixa') else str(x[x.sku==e['sku']].setorf.iloc[0])
    if cat=='Empório':
        if re.search(MUNDO,e['desc']): return 'Do mundo'
        alvo=alvo+' '+e['desc']
    if cat=='Caixa' and not alvo.startswith('Empório'): alvo=e['desc']
    for nome,pad in regras:
        if re.search(pad,alvo): return nome
    return 'Geral'
def _frente(r,n):
    return int(min(3,max(1,math.ceil((r.q/n/47.7/7*21+1)/6))))
def _encaixa(itens,tabuas):
    "Distribui em tábuas: marca junta, sem passar da largura. Devolve o que coube e o que sobrou."
    por={}
    for e in sorted(itens,key=lambda e:-e['v']): por.setdefault(e['mc'],[]).append(e)
    fila=[e for m in sorted(por,key=lambda m:-max(i['v'] for i in por[m])) for e in por[m]]
    res=[[] for _ in tabuas];usado=[0]*len(tabuas)
    for i,w in enumerate(tabuas):
        for e in list(fila):
            lg=e['w']*e['f']
            if usado[i]+lg<=w: res[i].append(e);usado[i]+=lg;fila.remove(e)
    return res,fila
def _centro(it):
    "Marca em bloco, com a maior no meio da prateleira e o líder no meio do bloco."
    por=pd.DataFrame(it).groupby('mc').v.sum().sort_values(ascending=False).index.tolist() if it else []
    cen=[]
    for j,m in enumerate(por):
        bl=sorted([e for e in it if e['mc']==m],key=lambda e:-e['v']);b2=[]
        for q,e in enumerate(bl): (b2.append(e) if q%2==0 else b2.insert(0,e))
        cen=cen+b2 if j%2==0 else b2+cen
    return cen
def escolher(x,cat,f,nuc=None):
    "Escolhe e posiciona. Cada tábua (módulo x nível) tem uma subcategoria e uma faixa de tamanho."
    nuc=nuc or set();n=max(1,x.loja.nunique())
    g=x.groupby(['sku','desc','marca']).agg(v=('valor','sum'),q=('qtd','sum'),l=('loja','nunique'),r=('mes3','max')).reset_index()
    g=g[(~g.desc.str.contains(EXC))&(g.v>0)&(g.marca!='A GRANEL')]
    g=g[g.r|g.sku.isin(nuc)];g=g.assign(fz=~g.sku.isin(nuc)).sort_values(['fz','v'],ascending=[True,False])
    inteiros=int(f+.999);larg=[UTIL if m+1<=f else UTIL/2 for m in range(inteiros)]
    LIM=LIMITE.get(T_ATUAL,4);teto=ALVO.get(T_ATUAL,{}).get(cat)
    cand=[];conta={}
    for r in g.itertuples():
        e=dict(sku=int(r.sku),desc=r.desc,marca=r.marca,nome=curto(r.desc,r.marca),mc=nome_marca(r.marca),w=largura(r.desc),f=1,fb=_frente(r,n),v=float(r.v),q=float(r.q),pm=float(r.v/max(r.q,1)),nc=int(r.sku) in nuc)
        e['b']=banda(r.desc);e['s']=_sub(cat,e,x);cand.append(e)
    grupos={}
    for e in cand: grupos.setdefault((e['s'],e['b']),[]).append(e)
    W=sum(larg);venda={k:sum(e['v'] for e in v) for k,v in grupos.items()}
    plano={} # (nível, módulo) -> chave do grupo
    usa_mapa=cat in MAPA
    if usa_mapa:
        mp=MAPA[cat];mp=mp.get(min(4,inteiros),mp[4]) if isinstance(mp,dict) else mp*inteiros
        for mi in range(inteiros):
            for k,nome in enumerate(mp[mi],1): plano[(k,mi)]=nome
    else:
        ordem=[(k,mi) for k in range(1,7) for mi in range(inteiros)];B=len(ordem);tv=sum(venda.values()) or 1
        vb={b:sum(v for (s,bb),v in venda.items() if bb==b) for b in BANDAS}
        dem={k:math.ceil(sum(e['w']*e['fb'] for e in v)/UTIL) for k,v in grupos.items()}
        qb={b:(max(1,round(B*vb[b]/tv)) if vb[b]>0 else 0) for b in BANDAS}
        qb['gde']=min(qb['gde'],2*inteiros,sum(dem[k] for k in dem if k[1]=='gde'))
        for b in ('dose','peq'): qb[b]=min(qb[b],sum(dem[k] for k in dem if k[1]==b))
        while sum(qb.values())>B:
            b=max(('dose','peq','gde'),key=lambda b:qb[b]-B*vb[b]/tv);qb[b]-=1
        while sum(qb.values())<B:
            pode=[b for b in BANDAS if vb[b]>0 and qb[b]<sum(dem[k] for k in dem if k[1]==b) and (b!='gde' or qb[b]<2*inteiros)]
            if not pode: break
            b=max(pode,key=lambda b:B*vb[b]/tv-qb[b]);qb[b]+=1
        # espaço sem produto do tamanho fica no nível 1: é onde entra o local
        vazio=B-sum(qb.values());ini=vazio
        for b in BANDAS:
            fatia=ordem[ini:ini+qb[b]];ini+=qb[b]
            if not fatia: continue
            fatia=sorted(fatia,key=lambda p:(OLHOS.index(p[0]),p[1]))
            ks=sorted([k for k in grupos if k[1]==b],key=lambda k:(k[0] in('Kids','Kids e peso'),-venda[k]))[:len(fatia)]
            qt={k:1 for k in ks};livres=len(fatia)-len(ks);tv2=sum(venda[k] for k in ks) or 1
            while livres>0:
                pode=[k for k in ks if qt[k]<dem[k]]
                if not pode: break
                k=max(pode,key=lambda k:venda[k]/tv2*len(fatia)-qt[k]);qt[k]+=1;livres-=1
            pos=0
            for k in ks:
                for p in fatia[pos:pos+qt[k]]: plano[p]=k
                pos+=qt[k]
    # recheia cada grupo nas tábuas que recebeu
    por_grupo={}
    for p,k in plano.items(): por_grupo.setdefault(k,[]).append(p)
    linhas={k:[[] for _ in range(inteiros)] for k in range(1,7)};esc=[]
    n_tab=max(1,len([k for k in por_grupo]));teto_t=(teto/sum(len(v) for v in por_grupo.values())) if teto else None
    for k,ps in por_grupo.items():
        ps=sorted(ps,key=lambda p:(OLHOS.index(p[0]),p[1]));tab=[larg[mi] for _,mi in ps];cap=sum(tab)
        if usa_mapa:
            nomes=k.split('|');pool=sorted([e for (s,b),v in grupos.items() if s in nomes for e in v],key=lambda e:(not e['nc'],-e['v']))
            if cat=='Creatina': pool=sorted([e for (s,b),v in grupos.items() if s==k and b!='dose' for e in v],key=lambda e:(not e['nc'],-e['v']))
            # o mesmo produto não volta em outra tábua
            pool=[e for e in pool if e not in esc and (e['b']!='gde' or min(p[0] for p in ps)>=5)]
        else: pool=list(grupos[k])
        tv3=sum(e['v'] for e in pool) or 1;tirar=[];usado=0;ac=0;conta={}
        mx=math.ceil(teto_t*len(ps)) if teto_t else None
        for e in pool:
            lin=' '.join(re.sub(r'\d+.*','',e['nome']).split()[:2]).upper();ch=(e['marca'],lin)
            if conta.get(ch,0)>=LIM and not e['nc']: continue
            if mx and len(tirar)>=mx: break
            if ac/tv3>=.90 and not e['nc']: continue
            fr=e['fb']
            if usado+e['w']*fr>cap: fr=1
            if usado+e['w']*fr>cap: continue
            e['f']=fr;usado+=e['w']*fr;ac+=e['v'];tirar.append(e);conta[ch]=conta.get(ch,0)+1
        # sobrou espaço: próximo produto da venda, depois frente para quem mais vende
        for e in pool:
            if e in tirar or (mx and len(tirar)>=mx): continue
            lin=' '.join(re.sub(r'\d+.*','',e['nome']).split()[:2]).upper();ch=(e['marca'],lin)
            if conta.get(ch,0)>=LIM: continue
            if usado+e['w']<=cap: e['f']=1;usado+=e['w'];tirar.append(e);conta[ch]=conta.get(ch,0)+1
        for j,e in enumerate(sorted(tirar,key=lambda e:-e['v'])):
            lim=3 if j==0 else 2
            while e['f']<lim and usado+e['w']<=cap: e['f']+=1;usado+=e['w']
        res,sobra=_encaixa(tirar,tab)
        # a largura de uma tábua pode não fechar: reduz frente de quem ficou de fora
        for e in sobra:
            e['f']=1
        if sobra:
            usados=[sum(i['w']*i['f'] for i in r_) for r_ in res]
            for e in sorted(sobra,key=lambda e:-e['v']):
                for i,w in enumerate(tab):
                    if usados[i]+e['w']<=w: res[i].append(e);usados[i]+=e['w'];break
        for (nv,mi),it in zip(ps,res):
            linhas[nv][mi]=it;esc+=it
    if teto and usa_mapa:
        while len(esc)>teto:
            nv,mi=max(((a,b) for a in linhas for b in range(inteiros)),key=lambda p:len(linhas[p[0]][p[1]]));e=min(linhas[nv][mi],key=lambda i:i['v']);linhas[nv][mi].remove(e);esc.remove(e)
        faltam=sorted([e for v in grupos.values() for e in v if e not in esc],key=lambda e:-e['v'])
        for e in faltam:
            if len(esc)>=teto: break
            for p,ch in plano.items():
                if e['s'] in ch.split('|') and (e['b']!='gde' or p[0]>=5):
                    it=linhas[p[0]][p[1]];lg=larg[p[1]];u=sum(i['w']*i['f'] for i in it)
                    if u+e['w']>lg:
                        for i in sorted(it,key=lambda i:i['v']):
                            while i['f']>1 and u+e['w']>lg: i['f']-=1;u-=i['w']
                    if u+e['w']<=lg: e['f']=1;it.append(e);esc.append(e);break
        # sobrou espaço na tábua: frente para quem mais vende, até 2
        for nv in linhas:
            for mi in range(inteiros):
                it=linhas[nv][mi];u=sum(i['w']*i['f'] for i in it)
                for i in sorted(it,key=lambda i:-i['v']):
                    if i['f']<2 and u+i['w']<=larg[mi]: i['f']+=1;u+=i['w']
    out=[]
    for k in range(1,7):
        def _arruma(it,ch):
            if usa_mapa and ch and '|' in ch:
                return [e for nm in ch.split('|') for e in _centro([i for i in it if i['s']==nm])]
            return _centro(it)
        mods=[_arruma(linhas[k][mi],plano.get((k,mi))) for mi in range(inteiros)];rots=[]
        for mi in range(inteiros):
            ch=plano.get((k,mi))
            if mods[mi]:
                ss=mods[mi];s0=max({e['s'] for e in ss},key=lambda q:sum(e['v'] for e in ss if e['s']==q));rots.append((ch.replace('|',' e ') if ch and len({e['s'] for e in ss})>1 else s0) if usa_mapa else f"{s0} · {NOME_B[ss[0]['b']]}")
            elif usa_mapa and ch: rots.append(RESERVA.get(ch,'Espaço local'))
            else: rots.append('Espaço local')
        tem=[r_ for r_ in rots if r_!='Espaço local']
        out.append(dict(n=k,rot=max(set(tem),key=tem.count) if tem else 'Espaço local',rots=rots,mods=mods,livre=[round(larg[mi]-sum(e['w']*e['f'] for e in mods[mi])) for mi in range(inteiros)]))
    for e in esc: e['pmin'],e['pmax']=preco(e['sku']);e['band']=NOME_B[e['b']]
    for e in esc:
        for c_ in ('fb','nc'): e.pop(c_,None)
    return dict(cat=cat,f=f,niveis=out,skus=len(esc),frentes=sum(e['f'] for e in esc),vTop=sum(e['v'] for e in esc),vCat=float(x.valor.sum()),cob=sum(e['v'] for e in esc)/max(1,float(g.v.sum())))
FAM_ORD=['Castanhas e nozes','Sementes','Frutas secas','Snacks e chocolates','Mix, cacau e farinhas']
def granel(x,T,nuc=None):
    n={'P':20,'M':32,'G':40}[T]-2;nuc=nuc or set()
    g=x.groupby(['sku','desc','marca']).agg(v=('valor','sum'),r=('mes3','max')).reset_index()
    g=g[(g.r|g.sku.isin(nuc))&~g.desc.str.contains(EXC)];g=g.assign(fz=~g.sku.isin(nuc)).sort_values(['fz','v'],ascending=[True,False]).head(n)
    it=[]
    for r in g.itertuples():
        fam=next(nm for nm,p in GRANEL if re.search(p,r.desc));nome=re.sub(r'\s*A GRANEL','',r.desc).title()
        lo,hi=preco(int(r.sku));it.append(dict(sku=int(r.sku),desc=r.desc,nome=nome[:28],fam=fam,v=float(r.v),pmin=lo,pmax=hi))
    it.sort(key=lambda t:(FAM_ORD.index(t['fam']),-t['v']))
    return dict(cat='Granel',tubos=it,skus=len(it),f=TAM[T][2],livres=2,cob=sum(i['v'] for i in it)/max(1,float(x.valor.sum())))
def tudo():
    d,_=bases();M=modulos();res={};NUC={}
    def guarda(cat,c):
        NUC.setdefault(cat,set()).update(t['sku'] for t in c['tubos']) if 'tubos' in c else NUC.setdefault(cat,set()).update(e['sku'] for n in c['niveis'] for m in n['mods'] for e in m)
        return c
    G2={'Vitaminas':'Vitaminas','Barras e snacks':None}
    global T_ATUAL
    for T in TAM:
        T_ATUAL=T
        x=d[d.tam==T];res[T]={'modulos':M[T],'cats':{}};nucs=NUC
        for cat in ['Proteínas','Creatina','Ômegas','Vitaminas','Colágeno','Bem-Estar','Performance','Longevidade','Intestino','Imunidade','Kids e Peso','Barras e snacks','Cafés funcionais','Despensa','Chás','Empório','Granel']:
            if cat=='Granel': res[T]['cats'][cat]=guarda(cat,granel(x[x.setorf=='Granel'],T,NUC.get(cat)));continue
            if cat=='Empório': y=x[x.setorf.astype(str).str.startswith('Empório')&~x.setorf.astype(str).str.contains('Queijos')];f=M[T]['Empório']
            else:
                chave=cat
                mapa={k:v for k,v in RC.G.items()};nomes=[k for k,v in mapa.items() if v==chave or (cat=='Barras e snacks' and v in('Barras','Barras e snacks'))  or (cat=='Intestino' and v in('Intestino','Saúde Intestinal'))]
                y=x[x.setorf.isin(nomes)]
                f=next((M[T][s] for s in M[T] if s in {mapa[k] for k in nomes}),None)
            if cat=='Bem-Estar':
                extra=[k for k,v in RC.G.items() if v in('Intestino','Imunidade','Kids e Peso','Longevidade') and M[T].get(v,0)==0]
                if extra: y=pd.concat([y,x[x.setorf.isin(extra)]])
            if f is None or y.empty or f==0: continue
            res[T]['cats'][cat]=guarda(cat,escolher(y,cat,f,NUC.get(cat)))
        # caixa: fora da conta de módulos, como o frio e o café da loja. Posição secundária de quem é pequeno
        cx=x[x.setorf.isin(['Barras e snacks','Cafés funcionais','Café e cápsulas','Empório: Chocolates e doces finos'])]
        cx=cx[cx.desc.map(lambda s:0<peso_g(s)<=60)]
        ALVO.setdefault(T,{})['Caixa']={'P':24,'M':30,'G':42}[T]
        res[T]['cats']['Caixa']=guarda('Caixa',escolher(cx,'Caixa',{'P':.5,'M':.5,'G':1}[T],NUC.get('Caixa')))
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
        for n in c['niveis']: print(T,cat,n['n'],n['rots'],n['livre'],[[ (e['mc'],e['nome'],e['f']) for e in m] for m in n['mods']])

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
    L=pd.read_pickle(R/'analise/lojas_cluster.pkl');d=dados_casa();d=d.assign(mes3=d.p.isin(RC.MES[-3:]))
    ALVO.update({'GG':{'Empório':130}});res={}
    base=json.loads((R/'analise/planogramas.json').read_text());NUC={}
    for c_,v_ in base['P']['cats'].items():
        NUC[c_]={e['sku'] for n in v_.get('niveis',[]) for m in n['mods'] for e in m}|{t['sku'] for t in v_.get('tubos',[])}
    for c_,v_ in base['M']['cats'].items():
        if c_ not in NUC: NUC[c_]={e['sku'] for n in v_.get('niveis',[]) for m in n['mods'] for e in m}
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
                    g=g[~g.desc.str.contains(EXC)].head(nt-2);it=[]
                    for r in g.itertuples():
                        fam=next(nm for nm,p in GRANEL if re.search(p,r.desc));lo,hi=preco(int(r.sku));it.append(dict(sku=int(r.sku),desc=r.desc,nome=re.sub(r'\s*A GRANEL','',r.desc).title(),fam=fam,pmin=lo,pmax=hi))
                    it.sort(key=lambda t:FAM_ORD.index(t['fam']))
                    cats[cat]=dict(f=f,tubos=it);continue
                if cat=='Empório': y=xT[xT.setorf.astype(str).str.startswith('Empório')&~xT.setorf.astype(str).str.contains('Queijos')]
                else:
                    y=xT[xT.setorf.isin(nomes(cat))]
                    if cat=='Bem-Estar':
                        ex=[k for k,v in RC.G.items() if v in('Intestino','Imunidade','Kids e Peso','Longevidade') and M.get(v,0)==0]
                        if ex: y=pd.concat([y,xT[xT.setorf.isin(ex)]])
                if y.empty: continue
                cc=escolher(y,cat,f,NUC.get(cat));cats[cat]=dict(f=f,niveis=cc['niveis'],skus=cc['skus'],frentes=cc['frentes'])
            res[f'{T}|{per}']=dict(n=n,modulos=M,cats=cats)
            print(T,per,n,sum(M.values()),sum(c.get('skus',len(c.get('tubos',[]))) for c in cats.values()))
    (R/'analise/planogramas12.json').write_text(json.dumps(res,ensure_ascii=False));return res
