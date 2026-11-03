# Passo 5 da receita: divide o espaço pela venda e confere pelo que cabe. Usado no deck e no kit.
import pandas as pd,numpy as np,math,pathlib
R=pathlib.Path(__file__).resolve().parent.parent
SET=[('Proteínas','Destino','Cuidar',30),('Creatina','Destino','Cuidar',42),('Vitaminas','Rotina','Cuidar',66),('Ômegas','Rotina','Cuidar',60),('Colágeno','Destino','Cuidar',42),('Bem-Estar','Destino','Cuidar',60),('Performance','Destino','Cuidar',42),('Longevidade','Destino','Cuidar',60),('Intestino','Rotina','Cuidar',60),('Imunidade','Ocasião','Cuidar',66),('Kids e Peso','Rotina','Cuidar',48),('Barras e snacks','Rotina','Abastecer',90),('Cafés funcionais','Rotina','Abastecer',48),('Chás','Rotina','Abastecer',60),('Despensa','Rotina','Abastecer',54)]
PESO={'Destino':1.2,'Rotina':1.0,'Ocasião':0.8,'Conveniência':0.7}
G={'Proteínas':'Proteínas','Creatina':'Creatina','Vitaminas de A a Z':'Vitaminas','Ômegas':'Ômegas','Colágeno e Beleza':'Colágeno','Equilíbrio e Bem-Estar':'Bem-Estar','Performance':'Performance','Longevidade':'Longevidade','Saúde Intestinal':'Intestino','Imunidade':'Imunidade','Kids':'Kids e Peso','Peso e Composição':'Kids e Peso','Barras e snacks':'Barras e snacks','Café e cápsulas':'Cafés funcionais','Chás':'Chás','Farinhas e despensa':'Despensa','Despensa sem setor':'Despensa'}
MES=['2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07','2026-08','2026-09']
_ch=None
def dados():
    global _ch
    if _ch is None:
        d=pd.read_pickle(R/'analise/vendas4.pkl');d=d[d.p.isin(MES)];d=d.assign(g=d.setorf.map(G));_ch=d
    return _ch
def alocar(loja,total,emp):
    d=dados();t=d[d.loja==loja];T=t.valor.sum();base=t[t.g.notna()]
    # o que está sem setor em suplemento entra proporcional nos setores de Cuidar
    sem=t[t.setorf=='Suplementos sem setor'].valor.sum()
    v=base.groupby('g').valor.sum()
    cu=[s for s,_,m,_c in SET if m=='Cuidar'];vc=v.reindex(cu).fillna(0);v=v.copy()
    for s in cu: v[s]=v.get(s,0)+sem*(vc[s]/vc.sum())
    linhas=[]
    for s,pap,mot,cap in SET:
        x=base[base.g==s].groupby('sku').valor.sum().sort_values(ascending=False)
        c=x.cumsum()/x.sum() if len(x) else x
        n80=int((c<=.8).sum())+1 if len(x) else 0;n95=int((c<=.95).sum())+1 if len(x) else 0
        fr=1.25
        linhas.append(dict(s=s,pap=pap,mot=mot,cap=cap,v=float(v.get(s,0)),n80=n80,n95=n95,mn=n80*fr/cap,mx=n95*fr/cap))
    df=pd.DataFrame(linhas);av=total-emp
    df['p']=df.v*df.pap.map(PESO);df['ideal']=av*df.p/df.p.sum();df['m']=df.ideal.clip(lower=df.mn,upper=df.mx)
    for _ in range(40):
        gap=av-df.m.sum()
        if abs(gap)<.01:break
        liv=(df.m<df.mx-1e-6) if gap>0 else (df.m>df.mn+1e-6)
        if not liv.any():
            df['m']=df.m*av/df.m.sum();break
        df.loc[liv,'m']+=gap*df.p[liv]/df.p[liv].sum();df['m']=df.m.clip(lower=df.mn,upper=df.mx) if gap!=0 else df.m
    # meio módulo é a menor unidade; soma fecha no total
    df['f']=(df.m*2).apply(math.floor)/2
    r=av-df.f.sum();ord_=(df.m-df.f).sort_values(ascending=False).index
    for i in ord_:
        if r<=0:break
        df.loc[i,'f']+=.5;r-=.5
    df['pv']=df.v/T*100
    return df
EX=[('DT PINHEIROS','Pinheiros',30,3,'Grande · suplemento forte'),('DT ALPHAVILLE','Alphaville',23,2,'Médio · suplemento forte'),('DT CAXIAS','Caxias do Sul',23,2,'Médio · equilibrado'),('DT TRAMANDAI','Tramandaí',11,1,'Pequeno · granel forte'),('DT SAO LEOPOLDO','São Leopoldo',45,4,'Muito grande · granel forte')]
if __name__=='__main__':
    pd.set_option('display.width',200)
    for l,n,t,e,_ in EX:
        a=alocar(l,t,e);print(n,t,e);print(a[['s','pap','pv','n80','n95','ideal','mn','mx','f']].round(1).to_string());print('soma',a.f.sum())
