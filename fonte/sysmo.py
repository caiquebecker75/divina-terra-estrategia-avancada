# Três lojas que ainda vendem pelo sistema Sysmo (Belém Plaza, Holambra e São José dos Campos), enviadas pela rede em
# 19/11/2026: venda por produto e mês, jan a dez de 2025. Gera analise/sysmo3.pkl no formato da base v2 (vendas5),
# com setor e prateleira da classificação v2: pelo código do produto quando ele existe no cadastro da rede e, senão,
# pelas mesmas regras de fonte/classificar.py. O arquivo bruto fica no HD, fora do repositório.
import pathlib, sys
import pandas as pd
R = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / 'fonte'))
import classificar as CL, base_v2 as B2

ARQ = pathlib.Path('/Volumes/hd caique becker/Mac Caique/Downloads/divina-terra/sysmo/Sysmo geral 2025.xlsx')
LOJA = {'Belem': 'DT BELEM PLAZA', 'Holambra': 'DT HOLAMBRA', 'São José dos Campos': 'DT SAO JOSE DOS CAMPOS'}
MES = {m: i for i, m in enumerate(['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'], 1)}
CAFE_FUNC = r'SUPERCOFFEE|ULTRACOFFEE|CAPPUCCINOFIT|V-COFFEE|COFFEE.*(?:PROTEIN|COLLAGEN|TCM|MCT)|\bFIT\b.*CAPPUC'
FUNC_MARCAS = {'CAFFEINE ARMY', 'PLANTPOWER', 'ELEMENTO PURO', 'MAHTA', 'VITAFOR', 'SUPER NUTRITION', 'NUTRATA', 'TOPWAY',
               'PURAVIDA', 'SANAVITA', 'DOBRO', 'SHARK PRO', 'ADA', 'SOU FIT', 'MUSHIN', 'ESSENTIAL NUTRITION', 'EQUALIV', 'TRUE SOURCE', 'NUTRIFY'}

def carregar():
    fr = []
    for aba, d in pd.read_excel(ARQ, sheet_name=None).items():
        d = d.rename(columns={d.columns[0]: 'MES'})
        fr.append(pd.DataFrame({'mes_n': d.MES.map(MES), 'ano': d.ANO.astype(int), 'loja': LOJA[aba], 'sku': d.PRODUTO.astype(int),
                                'desc': d.DESCRICAO.astype(str).str.strip(), 'marca': d.MARCA.astype(str).str.strip(),
                                'depto': d.DEPARTAMENTO.astype(str).str.strip(), 'qtd': d.QUANTIDADE.astype(float), 'valor': d.VALOR_TOTAL.astype(float)}))
    s = pd.concat(fr, ignore_index=True)
    assert s.mes_n.notna().all() and set(s.ano) == {2025}
    return s

def classificar(s):
    c = pd.read_pickle(R / 'analise/classificacao.pkl')[['sku', 'setor', 'prateleira']]
    c['sku'] = c.sku.astype(str)
    c = c.drop_duplicates('sku').set_index('sku')
    k = s.sku.astype(str)
    s['setor_v2'] = k.map(c.setor); s['prat'] = k.map(c.prateleira); s['origem'] = 'Cadastro da rede'
    novos = s[s.setor_v2.isna()].drop_duplicates('sku')
    res = {}
    for r in novos.to_dict('records'):
        st, pr, _ = CL.classificar({'desc': r['desc'], 'marca': r['marca'], 'depto': r['depto'], 'catc': ''})
        if st == 'Gourmet' and pr == 'Cafés, vinhos e presenteáveis' and (r['marca'] in FUNC_MARCAS or pd.Series([r['desc']]).str.contains(CAFE_FUNC).iloc[0]):
            st, pr = 'Performance', 'Cafés funcionais'
        res[r['sku']] = (st, pr)
    m = s.setor_v2.isna()
    s.loc[m, 'setor_v2'] = s.loc[m, 'sku'].map(lambda x: res[x][0]); s.loc[m, 'prat'] = s.loc[m, 'sku'].map(lambda x: res[x][1])
    s.loc[m, 'origem'] = 'Regra da classificação v2'
    s['setorf'] = [B2.setorf(a, b) for a, b in zip(s.setor_v2, s.prat)]
    return s

SUPL = {'Proteínas', 'Creatina', 'Vitaminas de A a Z', 'Ômegas', 'Colágeno e Beleza', 'Equilíbrio e Bem-Estar', 'Performance', 'Longevidade',
        'Saúde Intestinal', 'Imunidade', 'Kids', 'Peso e Composição', 'Suplementos sem setor', 'Café e cápsulas'}
def motor(setorf):
    if setorf == 'Granel': return 'Granel'
    if setorf.startswith('Gourmet'): return 'Gourmet'
    if setorf in SUPL: return 'Suplemento'
    return 'Despensa e outros'

if __name__ == '__main__':
    s = classificar(carregar())
    s.to_pickle(R / 'analise/sysmo3.pkl')
    t = s.groupby('origem').valor.sum() / s.valor.sum() * 100
    print('origem da classificação (% do valor):', t.round(1).to_dict())
    print('a classificar (%% do valor): %.1f' % (s[s.setor_v2.eq('A classificar')].valor.sum() / s.valor.sum() * 100))
    s['motor'] = s.setorf.map(motor)
    p = s.pivot_table(index='loja', columns='motor', values='valor', aggfunc='sum')
    print((p.div(p.sum(axis=1), axis=0) * 100).round(1).assign(ano_mi=(p.sum(axis=1) / 1e6).round(2), mes_mil=(p.sum(axis=1) / 12e3).round(0)).to_string())
