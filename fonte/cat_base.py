# Base por setor da v2 (classificação pela árvore da rede): % da venda, SKUs, núcleo de 80%, faixa de preço e marcas que mais pesam.
# Gera analise/cat_base.json e analise/n80.json com as chaves do book (receita.SET + Granel e Chás) e as prateleiras do Gourmet.
import json, pathlib, sys
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import receita as RC

R = RC.R
d = RC.dados()
d = d.assign(chave=d.g.where(d.g.notna(), d.setorf.where(d.setorf.isin(['Granel', 'Chás']))))
T = d.valor.sum()

def q_pond(u, w, q):
    o = np.argsort(u.values); u = u.values[o]; w = w.values[o]; c = np.cumsum(w) / w.sum()
    return float(u[min(len(u) - 1, np.searchsorted(c, q))])

def linha(x):
    s = x.groupby('sku').valor.sum().sort_values(ascending=False); c = s.cumsum() / s.sum()
    n80 = int((c <= .8).sum()) + 1
    y = x[(x.qtd > 0) & (x.valor > 0)]; u = y.valor / y.qtd
    m = x.groupby('marca').valor.sum().sort_values(ascending=False)
    top = [str(k).title() for k in m.index[:3]]
    return dict(pct=round(x.valor.sum() / T * 100, 2), sk=int(x.sku.nunique()), n80=n80,
                p25=round(q_pond(u, y.valor, .25), 2), p50=round(q_pond(u, y.valor, .5), 2), p75=round(q_pond(u, y.valor, .75), 2),
                top=top, shareTop=round(m.iloc[0] / m.sum() * 100) if len(m) else 0)

cb = {}
for k, x in d[d.chave.notna()].groupby('chave'): cb[k] = linha(x)
for k, x in d[d.setorf.str.startswith('Gourmet')].groupby('setorf'): cb[k] = linha(x)
# azeite de oliva separado de vinagre e molho: o book v1 misturava os três na faixa de preço (devolutiva 3.2 e 5.4)
az = d[d.setorf.eq('Gourmet: Azeites, molhos e antepastos') & d.desc.str.contains(r'^(?!.*(?:PAO|BISC|BATATA|SNACK|CHIPS|TORRADA|MOLHO|PESTO|ATUM|SARDINHA|AZEITONA|TOSTIQ|PIPOCA)).*AZEITE', regex=True)]
cb['Gourmet: Azeites'] = linha(az)
(R / 'analise/cat_base.json').write_text(json.dumps(cb, ensure_ascii=False, indent=1))
(R / 'analise/n80.json').write_text(json.dumps({k: [v['n80'], v['sk'], v['pct']] for k, v in cb.items()}, ensure_ascii=False))
for k, v in sorted(cb.items(), key=lambda kv: -kv[1]['pct']):
    print(f"{k:42} {v['pct']:5.2f}%  skus {v['sk']:5}  n80 {v['n80']:4}  R$ {v['p25']:.0f} {v['p50']:.0f} {v['p75']:.0f}  {', '.join(v['top'])}")
