import pandas as pd,json
pd.set_option('display.width',200,'display.max_rows',200,'display.max_colwidth',52)
df=pd.read_pickle('analise/vendas4.pkl')
for st in ['Creatina','Ômegas','Proteínas']:
    t=df[df.setorf==st].groupby(['sku','desc','marca']).agg(v=('valor','sum'),q=('qtd','sum'),l=('loja','nunique')).sort_values('v',ascending=False)
    t['rs']=t.v/t.q
    print('==',st,len(t),round(t.v.sum()),'marcas',t.reset_index().marca.nunique(),'top 12 %',round(t.v.head(12).sum()/t.v.sum()*100)); print(t.head(14).round(0).to_string())
    print(t.reset_index().groupby('marca').v.sum().sort_values(ascending=False).head(8).round(0).to_dict())
g=df[df.depto=='A GRANEL']
import re
G={'Castanhas e nozes':r'CASTANHA|NOZES|AMENDOA|PISTACHE|AVELA|MACADAMIA|AMENDOIM',"Frutas secas":r'DAMASCO|AMEIXA|UVA|TAMARA|FIGO|BANANA|CRANBERRY|PASSA|ABACAXI|MANGA|MIX DE FRUTAS','Sementes e grãos':r'SEMENTE|CHIA|LINHACA|QUINOA|GERGELIM|GIRASSOL|AVEIA|ARROZ|LENTILHA|GRAO|FEIJAO','Farinhas e fibras':r'FARINHA|PSYLLIUM|FARELO|AMIDO|POLVILHO|FIBRA','Snacks e chocolates':r'CHOCO|DRAGEA|BISCOITO|CHIPS|SNACK|MILHO|GRANOLA|BALA|BANANINHA|DOCE|PACOCA|TORRADO|COCO','Temperos e chás':r'CHA\b|TEMPERO|PIMENTA|CANELA|OREGANO|ERVA|SAL\b|CURCUMA|MATE|HIBISCO'}
def gg(d):
    for k,p in G.items():
        if re.search(p,d): return k
    return 'Outros'
g=g.assign(grupo=g.desc.map(gg)); x=g.groupby('grupo').agg(v=('valor','sum'),sk=('sku','nunique')).sort_values('v',ascending=False); x['p']=x.v/x.v.sum()*100; print(x.round(1).to_string())
print(g.groupby(['grupo','desc']).valor.sum().sort_values(ascending=False).groupby(level=0).head(5).sort_index(level=0,sort_remaining=False).round(0).to_string())
