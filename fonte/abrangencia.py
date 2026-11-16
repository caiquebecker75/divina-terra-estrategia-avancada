# Abrangência de cada produto na rede (devolutiva 2.2, 5.1 e 5.2): curva ABC dentro do setor, quantas lojas vendem
# e se a venda se concentra numa região. Define o papel do produto no sortimento:
#   Essencial: curva A do setor e vendido em pelo menos metade das lojas. Vai para o núcleo, igual em toda loja do tamanho.
#   Complementar: curva A ou B e vendido em pelo menos 20% das lojas. Forma a lista aprovada, da qual a loja escolhe.
#   Regional: 85% ou mais da venda numa só região, 30% acima do peso dessa região na rede, e vendido em menos de 30% das lojas.
#   Só entra como local, na região dele.
#   Cauda: o resto. Não entra no desenho; a loja que vende pode manter enquanto girar.
# Gera analise/abrangencia.json (por SKU) e analise/locais.json (marcas regionais por setor, com as chaves do book).
import json, pathlib, sys
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import receita as RC

R = RC.R
d = RC.dados()
L = pd.read_pickle(R / 'analise/lojas_cluster.pkl')
d = d.assign(reg=d.loja.map(L.reg), chave=d.g.where(d.g.notna(), d.setorf.where(d.setorf.isin(['Granel', 'Chás']))))
d = d[d.chave.notna()]
n_lojas = d.loja.nunique()
g = d.groupby(['chave', 'sku']).agg(v=('valor', 'sum'), lojas=('loja', 'nunique'), marca=('marca', 'first'), desc=('desc', 'first')).reset_index()
rg = d.groupby(['sku', 'reg']).valor.sum().unstack(fill_value=0)
conc = (rg.max(axis=1) / rg.sum(axis=1).clip(lower=1)); reg_top = rg.idxmax(axis=1)
g['conc'] = g.sku.map(conc).fillna(0); g['reg_top'] = g.sku.map(reg_top)
peso_reg = d.groupby('reg').valor.sum() / d.valor.sum()  # o Sul pesa muito na rede: a concentração é comparada com o peso da região
g['lift'] = g.conc / g.reg_top.map(peso_reg).fillna(1)
g['pl'] = g.lojas / n_lojas
g = g.sort_values(['chave', 'v'], ascending=[True, False])
g['acum'] = g.groupby('chave').v.cumsum() / g.groupby('chave').v.transform('sum')
g['curva'] = ['A' if a <= .8 else 'B' if a <= .95 else 'C' for a in g.acum]
def papel(r):
    if r.conc >= .85 and r.lift >= 1.3 and r.pl < .3: return 'Regional'
    if r.curva == 'A' and r.pl >= .5: return 'Essencial'
    if r.curva in ('A', 'B') and r.pl >= .2: return 'Complementar'
    return 'Cauda'
g['papel'] = [papel(r) for r in g.itertuples()]
out = {str(int(r.sku)): dict(c=r.chave, curva=r.curva, lojas=int(r.lojas), pl=round(r.pl, 3), conc=round(r.conc, 2), reg=r.reg_top, papel=r.papel) for r in g.itertuples()}
(R / 'analise/abrangencia.json').write_text(json.dumps(out, ensure_ascii=False))
# marcas regionais por setor: a marca inteira vende quase só numa região e em poucas lojas (não basta um item da marca)
bm = d.groupby(['marca', 'reg']).valor.sum().unstack(fill_value=0)
bconc = bm.max(axis=1) / bm.sum(axis=1).clip(lower=1); breg = bm.idxmax(axis=1)
blift = bconc / breg.map(peso_reg).fillna(1); blojas = d.groupby('marca').loja.nunique() / n_lojas
regionais = set(bm.index[(bconc >= .85) & (blift >= 1.3) & (blojas.reindex(bm.index) < .3)]) - {'A GRANEL', 'SEM MARCA', 'MARCAS DIVERSAS', 'DIVINA TERRA'}
loc = {}
for c, x in d[d.marca.isin(regionais)].groupby('chave'):
    m = x.groupby('marca').agg(v=('valor', 'sum'), lojas=('loja', 'nunique')).sort_values('v', ascending=False)
    loc[c] = [[f'{str(a).title()} ({breg[a]})', int(l)] for a, l in zip(m.index, m.lojas)][:10]
(R / 'analise/locais.json').write_text(json.dumps(loc, ensure_ascii=False))
print(g.groupby('papel').agg(skus=('sku', 'count'), v=('v', 'sum')).assign(pct=lambda t: (t.v / t.v.sum() * 100).round(1)).drop(columns='v'))
print(peso_reg.round(3).to_dict());print(g[g.desc.str.contains('FIT SWEET|SHARK PRO')].head(6)[['chave', 'desc', 'lojas', 'conc', 'reg_top', 'papel']].to_string())
print({k: v[:3] for k, v in loc.items()})
