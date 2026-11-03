# Consolida os números da base de vendas para o deck e para o kit (rodar da raiz do projeto).
import pandas as pd,numpy as np,re,json,sys,warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'analise')
from setorizar import setor,nz
df=pd.read_pickle('analise/vendas3.pkl')
L=pd.read_pickle('analise/lojas_cluster.pkl')
EXTRA=[('Equilíbrio e Bem-Estar',r'MELATONIN|THEANINE|MAGNE INOS|BRAIN|HAPPY|GABA|MORNING SHOT'),('Saúde Intestinal',r'FIBER|PROBIO|GUT\b|ENZYFOR|BIOME|SIMFORT'),('Performance',r'ELETROLITO|AMINOLIFT|BETA ACTION|MUSCLE SYNERGY|GLUTAMINE|WINSTAGE'),('Longevidade',r'LIVESTRONG|VITALIFT|UBIQUINOL|COLAG JOINT|COLAGENTEK|GUARDIAN|RESTAURE'),('Vitaminas de A a Z',r'TRIMAG|COMPLEXO B|\bMG\b|VITA\b'),('Imunidade',r'PROP VERDE|EXTR DE PROP|APIS FLORA'),('Barras e snacks',r'TIRA MORA|BRIGADEIRO|ALFAJOR|TIRINHA|BOLACHA|SALGADINHO'),('Chocolates',r'CHOCOKI')]
FB={'SUPLEMENTO':'Suplementos sem setor','VITAMINAS':'Vitaminas de A a Z','FITOTERAPICOS':'Imunidade','CHAS':'Chás','CHAS E TEMPEROS':'Chás','IMPORTACAO':'Suplementos sem setor'}
def set2(desc,dep,s):
    if s!='Sem regra': return s
    t=nz(desc)
    for n,p in EXTRA:
        if re.search(p,t): return n
    return FB.get(dep,'Despensa sem setor')
u=df.drop_duplicates('sku')[['sku','desc','depto','setor']].copy()
u['setor2']=[set2(a,b,c) for a,b,c in zip(u.desc,u.depto,u.setor)]
df=df.drop(columns=[c for c in ['setor2'] if c in df]).merge(u[['sku','setor2']],on='sku')
# junta os blocos de "flavor" enganosos: bloco de empório estrito manda; o resto volta para o setor de consumo
EMPOLD=['Vinhos e bebidas adultas','Queijos e laticínios finos','Azeites e vinagres','Massas','Molhos e temperos','Conservas e antepastos','Chocolates','Geleias e mel']
def final(r_set,bl):
    if isinstance(bl,str): return 'Empório: '+bl
    if r_set in EMPOLD: return 'Barras e snacks' if r_set in('Queijos e laticínios finos','Conservas e antepastos','Vinhos e bebidas adultas','Azeites e vinagres','Massas','Molhos e temperos') else 'Despensa sem setor'
    return r_set
df['setorf']=[final(a,b) for a,b in zip(df.setor2,df.bloco)]
T=df.valor.sum()
s=df.groupby('setorf').agg(v=('valor','sum'),skus=('sku','nunique')).sort_values('v',ascending=False); s['p']=s.v/T*100
print(s.round(2).to_string())
df.to_pickle('analise/vendas4.pkl')
