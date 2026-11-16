# Base de vendas da v2: a mesma venda da v1 (71 lojas, 10/2025 a 10/2026), com setor e prateleira da classificação v2
# (fonte/classificar.py + revisão item a item). Gera analise/vendas5.pkl, que todos os geradores do book leem.
# A coluna setorf usa o vocabulário dos geradores; setorf_v1 guarda o setor antigo, para comparar.
import pathlib
import pandas as pd

R = pathlib.Path(__file__).resolve().parent.parent
MAPA = {'Proteínas': 'Proteínas', 'Creatina': 'Creatina', 'Vitaminas de A a Z': 'Vitaminas de A a Z', 'Ômegas': 'Ômegas',
        'Colágeno & Beleza': 'Colágeno e Beleza', 'Equilíbrio & Bem-Estar': 'Equilíbrio e Bem-Estar', 'Performance': 'Performance',
        'Longevidade Saudável': 'Longevidade', 'Saúde Intestinal': 'Saúde Intestinal', 'Imunidade': 'Imunidade', 'Kids': 'Kids',
        'Peso & Composição Corporal': 'Peso e Composição', 'Barras e snacks': 'Barras e snacks', 'Chás': 'Chás',
        'Sem Glúten': 'Sem Glúten', 'Granel': 'Granel', 'Geladeira e bebidas prontas': 'Geladeira', 'Cafeteria da loja': 'Café da loja',
        'Cuidados pessoais e casa': 'Fora de setor', 'Fora do planograma': 'Fora de setor'}

def setorf(setor, prat):
    if setor == 'Performance' and prat == 'Cafés funcionais':
        return 'Café e cápsulas'
    if setor == 'Gourmet':
        return 'Gourmet: ' + prat
    if setor == 'A classificar':
        return 'Suplementos sem setor' if prat == 'Suplemento sem regra' else 'Fora de setor'
    return MAPA[setor]

if __name__ == '__main__':
    v = pd.read_pickle(R / 'analise/vendas4.pkl')
    c = pd.read_pickle(R / 'analise/classificacao.pkl')[['sku', 'setor', 'prateleira']]
    c['sku'] = c.sku.astype(str)
    v['sku_s'] = v.sku.astype(str)
    v = v.merge(c.rename(columns={'sku': 'sku_s', 'setor': 'setor_v2', 'prateleira': 'prat'}), on='sku_s', how='left').drop(columns='sku_s')
    sem = v.setor_v2.isna()
    print('linhas sem classificação:', int(sem.sum()))
    v.loc[sem, 'setor_v2'] = 'A classificar'; v.loc[sem, 'prat'] = 'Alimento sem regra'
    v['setorf_v1'] = v.setorf.astype(str)
    v['setorf'] = [setorf(a, b) for a, b in zip(v.setor_v2, v.prat)]
    v.to_pickle(R / 'analise/vendas5.pkl')
    t = v.groupby('setorf').valor.sum().sort_values(ascending=False) / v.valor.sum() * 100
    print(t.round(2).to_string())
