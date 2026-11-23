# Lista de execução por loja (devolutiva 4.2): compara o que cada loja vendeu nos últimos 3 meses com o planograma
# do tipo dela (tamanho x perfil, analise/planogramas12.json) e diz o que fazer com cada produto.
#   Permanece: está no planograma e a loja já vende. Vai para o nível e o módulo indicados, com as frentes indicadas.
#   Muda de setor: está no planograma e a loja já vende, mas mudou de setor em relação ao book v1. Realocar.
#   Incorpora: está no planograma e a loja ainda não vende. Pedir.
#   Lista aprovada: a loja vende, não coube no desenho, mas é complementar. Fica se houver espaço local.
#   Local regional: a loja vende e o produto é regional. Fica na parte local da loja.
#   Sai aos poucos: a loja vende, não está no desenho nem na lista. Não repõe; sai quando acabar, sem queima.
#   Reduz: a loja vende, fica pela lista aprovada, pela região ou por vender bem nela, mas com 1 frente, na parte local.
# Belém Plaza e Holambra (Sysmo, analise/sysmo3.pkl) entram com a venda de 07 a 09/2025 e a metragem de drive/m2-lojas-2026.xlsx.
# Gera kit/divina-terra-execucao-v4.xlsx (tem venda por loja: fora do repositório público).
import json, pathlib, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import receita as RC

R = RC.R
P12 = json.loads((R / 'analise/planogramas12.json').read_text())
ABR = {int(k): v for k, v in json.loads((R / 'analise/abrangencia.json').read_text()).items()}
L = pd.read_pickle(R / 'analise/lojas_cluster.pkl')
d = RC.dados(); d = d[d.p.isin(RC.MES[-3:])]
# Lojas do Sysmo com metragem na lista da rede: mesmos meses, um ano antes (2025). Perfil pela regra dos 12 tipos:
# granel 30% ou mais = Granel forte; suplemento 55% ou mais com granel abaixo de 20% = Suplemento forte; senão, Equilibrado.
SY = pd.read_pickle(R / 'analise/sysmo3.pkl'); M2 = {'DT BELEM PLAZA': 239.14, 'DT HOLAMBRA': 90.0}
dep = RC.dados().drop_duplicates('sku').assign(k=lambda x: x.sku.astype(int)).set_index('k').depto
SY['dep'] = SY.sku.map(dep).fillna(SY.depto)
extra = []
for lj, m2 in M2.items():
    t = SY[SY.loja == lj]; tot = t.valor.sum(); sup = t[t.dep == 'SUPLEMENTO'].valor.sum() / tot * 100; gra = t[t.dep == 'A GRANEL'].valor.sum() / tot * 100
    tam = 'P' if m2 <= 50 else 'M' if m2 <= 80 else 'G' if m2 <= 120 else 'GG'
    perfil = 'Granel forte' if gra >= 30 else 'Suplemento forte' if sup >= 55 and gra < 20 else 'Equilibrado'
    extra.append(dict(loja=lj, tam=tam, perfil=perfil))
L = pd.concat([L, pd.DataFrame(extra).set_index('loja')])
sy = SY[SY.loja.isin(M2) & SY.mes_n.isin([7, 8, 9])].assign(p=lambda x: x.mes_n.map(dict(zip([7, 8, 9], RC.MES[-3:]))))
d = pd.concat([d, sy[['loja', 'sku', 'desc', 'marca', 'qtd', 'valor', 'p']]], ignore_index=True)
cl = pd.read_pickle(R / 'analise/classificacao.pkl')[['sku', 'setor', 'prateleira']]; cl['sku'] = cl.sku.astype(int)
v1 = pd.read_pickle(R / 'analise/v1_categoria.pkl'); v1['sku'] = v1.sku.astype(int)
EQ = {'Proteínas': 'Proteínas', 'Creatina': 'Creatina', 'Colágeno': 'Colágeno & Beleza', 'Performance': 'Performance', 'Bem-Estar': 'Equilíbrio & Bem-Estar',
      'Longevidade': 'Longevidade Saudável', 'Vitaminas': 'Vitaminas de A a Z', 'Ômegas': 'Ômegas', 'Intestino': 'Saúde Intestinal', 'Imunidade': 'Imunidade',
      'Chás': 'Chás', 'Granel': 'Granel', 'Barras e snacks': 'Barras e snacks'}
def mudou(g1, setor, prat):
    if not isinstance(g1, str): return False
    if g1 == 'Kids e Peso': return setor not in ('Kids', 'Peso & Composição Corporal')
    if g1 == 'Cafés funcionais': return prat != 'Cafés funcionais'
    if g1 == 'Despensa': return setor not in ('Gourmet', 'Sem Glúten')
    return EQ.get(g1) != setor
mv = {r.sku: mudou(r.g, s, p) for r, s, p in zip(v1.merge(cl, on='sku', how='left').itertuples(), v1.merge(cl, on='sku', how='left').setor, v1.merge(cl, on='sku', how='left').prateleira)}
NOME_SETOR = dict(zip(cl.sku, cl.setor)); NOME_PRAT = dict(zip(cl.sku, cl.prateleira))
NIV = {1: 'Alto', 2: 'Alto', 3: 'Olhos', 4: 'Olhos', 5: 'Mão', 6: 'Baixo'}

def desenho(tipo):
    "SKU -> (setor do book, nível, módulo, frentes) no planograma do tipo de loja."
    out = {}
    for cat, c in P12[tipo]['cats'].items():
        if 'tubos' in c:
            for k, t in enumerate(c['tubos'], 1): out[t['sku']] = (cat, 'Bin', (k - 1) // 6 + 1, 1)
            continue
        for n in c['niveis']:
            for mi, m in enumerate(n['mods'], 1):
                for e in m: out[e['sku']] = (cat, n['n'], mi, e['f'])
    return out

linhas = []; resumo = []
for loja, x in d.groupby('loja'):
    if loja not in L.index or L.loc[loja, 'tam'] not in ('P', 'M', 'G', 'GG'): continue
    tipo = f"{L.loc[loja, 'tam']}|{L.loc[loja, 'perfil']}"
    if tipo not in P12: continue
    des = desenho(tipo)
    vend = x.groupby(['sku', 'desc', 'marca']).agg(v=('valor', 'sum'), q=('qtd', 'sum')).reset_index()
    vend = vend[vend.v > 0]; vs = set(vend.sku.astype(int))
    info = {int(r.sku): (r.desc, r.marca, r.v) for r in vend.itertuples()}
    cont = {}
    def add(sku, acao, desc, marca, v):
        cat, nv, mod, fr = des.get(sku, (None, None, None, None))
        if acao.startswith('Reduz'): nv, mod, fr = 'Parte local', None, 1
        a = ABR.get(sku, {})
        linhas.append([loja, tipo.replace('|', ' · '), NOME_SETOR.get(sku, ''), NOME_PRAT.get(sku, ''), sku, desc, marca, acao,
                       (f'{nv} · {NIV.get(nv, "")}' if isinstance(nv, int) else nv) or '', mod or '', fr or '', a.get('papel', ''), a.get('curva', ''), round(v, 2) if v else None])
        cont[acao] = cont.get(acao, 0) + 1
    prod = d[['sku', 'desc', 'marca']].drop_duplicates('sku').set_index('sku')
    # o que mais vende na própria loja, dentro do setor: fica, mesmo fora das listas (é a parte local da loja)
    vend['setor'] = vend.sku.astype(int).map(NOME_SETOR)
    vend = vend.sort_values(['setor', 'v'], ascending=[True, False])
    vend['ac'] = vend.groupby('setor').v.cumsum() / vend.groupby('setor').v.transform('sum')
    forte = set(vend.loc[vend.ac <= .8, 'sku'].astype(int))
    for sku in des:
        essencial = ABR.get(sku, {}).get('papel') == 'Essencial'
        if sku in vs:
            desc, marca, v = info[sku]; add(sku, 'Muda de setor' if mv.get(sku) else 'Permanece', desc, marca, v)
        elif essencial:
            desc, marca = (prod.loc[sku, 'desc'], prod.loc[sku, 'marca']) if sku in prod.index else ('', ''); add(sku, 'Incorpora', desc, marca, None)
        else:
            desc, marca = (prod.loc[sku, 'desc'], prod.loc[sku, 'marca']) if sku in prod.index else ('', ''); add(sku, 'Opcional', desc, marca, None)
    for sku in vs - set(des):
        desc, marca, v = info[sku]; p = ABR.get(sku, {}).get('papel')
        if NOME_SETOR.get(sku) in (None, 'Cafeteria da loja', 'Fora do planograma', 'Cuidados pessoais e casa', 'Geladeira e bebidas prontas', 'A classificar'): continue
        acao = 'Reduz · lista aprovada' if p in ('Complementar', 'Essencial') else 'Reduz · local regional' if p == 'Regional' else 'Reduz · local da loja' if sku in forte else 'Sai aos poucos'
        if acao != 'Lista aprovada' and mv.get(sku) and acao != 'Sai aos poucos': pass
        add(sku, acao, desc, marca, v)
    resumo.append([loja, tipo.replace('|', ' · '), len(des)] + [cont.get(k, 0) for k in ('Permanece', 'Muda de setor', 'Incorpora', 'Reduz · lista aprovada', 'Reduz · local regional', 'Reduz · local da loja', 'Sai aos poucos', 'Opcional')])

ORDEM = {'Muda de setor': 0, 'Incorpora': 1, 'Permanece': 2, 'Reduz · lista aprovada': 3, 'Reduz · local regional': 4, 'Reduz · local da loja': 5, 'Sai aos poucos': 6, 'Opcional': 7}
df = pd.DataFrame(linhas, columns=['Loja', 'Tipo de loja', 'Setor', 'Prateleira', 'SKU', 'Descrição', 'Marca', 'O que fazer', 'Nível', 'Módulo', 'Frentes', 'Papel na rede', 'Curva no setor', 'Venda na loja, 3 meses (R$)'])
df = df.assign(o=df['O que fazer'].map(ORDEM)).sort_values(['Loja', 'o', 'Setor', 'Prateleira']).drop(columns='o')
rs = pd.DataFrame(resumo, columns=['Loja', 'Tipo de loja', 'Produtos no desenho', 'Permanece', 'Muda de setor', 'Incorpora', 'Reduz · lista aprovada', 'Reduz · local regional', 'Reduz · local da loja', 'Sai aos poucos', 'Opcional'])

TERRA = '461D17'; H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor=TERRA)
def tabela(ws, t, larg):
    for j, c in enumerate(t.columns, 1):
        x = ws.cell(1, j, c); x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical='center')
        ws.column_dimensions[get_column_letter(j)].width = larg.get(c, 14)
    for i, row in enumerate(t.itertuples(index=False), 2):
        for j, v in enumerate(row, 1): ws.cell(i, j, None if (isinstance(v, float) and pd.isna(v)) else v)
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions; ws.row_dimensions[1].height = 34
wb = Workbook(); ws = wb.active; ws.title = 'Leia antes'
TX = [('Divina Terra · Lista de execução por loja (versão 4)', 't'),
      ('Resposta ao item 4.2 da devolutiva de 16/11/2026: o que cada loja faz com cada produto para aplicar o planograma.', ''), ('', ''),
      ('Como foi feito', 's'),
      ('Cada loja recebe o planograma do seu tipo (tamanho x perfil). A lista compara esse desenho com o que a loja vendeu de 07/2026 a 09/2026.', ''),
      ('Classificação dos produtos: árvore de 16 setores da rede, com revisão item a item. Papel na rede: essencial, complementar, regional ou cauda (aba Critérios).', ''), ('', ''),
      ('O que fazer', 's'),
      ('Muda de setor: a loja já vende, mas o produto mudou de setor em relação ao book v1. Levar para o setor e a prateleira indicados.', ''),
      ('Incorpora: é essencial (núcleo) e a loja ainda não vende. Pedir na próxima compra. Só o núcleo é obrigatório.', ''),
      ('Opcional: está no desenho do tipo de loja, mas não é essencial. Entra se a loja quiser, no lugar de um local que gire menos.', ''),
      ('Reduz · local da loja: não está nas listas da rede, mas é dos que mais vendem na própria loja, dentro do setor. Fica com 1 frente, na parte local.', ''),
      ('Permanece: está no desenho e a loja já vende. Colocar no nível, no módulo e com as frentes indicadas.', ''),
      ('Reduz · lista aprovada: a loja vende, não coube no desenho, mas é complementar na rede. Fica com 1 frente, se houver espaço na parte local.', ''),
      ('Reduz · local regional: a loja vende e o produto é forte só na região. Fica com 1 frente, na parte local.', ''),
      ('A parte local é de até 20% do espaço do setor. O que fica nela perde frentes antes de qualquer produto do núcleo.', ''),
      ('Sai aos poucos: não está no desenho nem nas listas e vende pouco na própria loja. Não repõe; sai quando acabar, sem queima de estoque.', ''), ('', ''),
      ('Reposição e substituição', 's'),
      ('Essencial: nunca pode faltar. Conferência diária dos líderes; faltou, etiqueta de reposição e prazo de 2 dias.', ''),
      ('Complementar: reposição semanal. Se sair de linha, entra o próximo da lista aprovada na mesma prateleira e na mesma faixa de tamanho.', ''),
      ('Frentes: as indicadas no desenho são o mínimo. Produto acima de 500 g fica nos níveis 5 e 6.', ''),
      ('Marca própria Vivea: sempre nos olhos, com pelo menos 2 frentes.', ''), ('', ''),
      ('Este arquivo tem venda por loja. Uso interno da Divina Terra e da 75 LAB.', '')]
for i, (t, k) in enumerate(TX, 1):
    c = ws.cell(i, 1, t); c.alignment = Alignment(wrap_text=True)
    if k == 't': c.font = Font(bold=True, size=16, color=TERRA)
    elif k == 's': c.font = Font(bold=True, size=12, color='7C381F')
ws.column_dimensions['A'].width = 130
ws = wb.create_sheet('Resumo por loja'); tabela(ws, rs, {'Loja': 26, 'Tipo de loja': 24})
ws = wb.create_sheet('Por loja'); tabela(ws, df, {'Loja': 22, 'Tipo de loja': 22, 'Setor': 24, 'Prateleira': 28, 'Descrição': 46, 'Marca': 18, 'O que fazer': 16})
cr = pd.DataFrame([['Essencial', 'Curva A do setor e vendido em pelo menos metade das lojas', 'Núcleo: igual em toda loja do tamanho'],
                   ['Complementar', 'Curva A ou B e vendido em pelo menos 20% das lojas', 'Lista aprovada: a loja escolhe pelo espaço'],
                   ['Regional', '85% ou mais da venda numa só região, bem acima do peso dela na rede, e vendido em menos de 30% das lojas', 'Local, só na região'],
                   ['Cauda', 'O resto', 'Não entra no desenho; sai aos poucos']], columns=['Papel', 'Critério', 'Onde entra'])
ws = wb.create_sheet('Critérios'); tabela(ws, cr, {'Papel': 16, 'Critério': 80, 'Onde entra': 44})
out = R / 'kit/divina-terra-execucao-v4.xlsx'; wb.save(out)
print(out, len(df), 'linhas,', len(rs), 'lojas'); print(rs.drop(columns=['Loja', 'Tipo de loja']).median().round(0).to_dict())
print(rs[rs.Loja.str.contains('PINHEIROS|MADALENA|ALPHAVILLE|BELEM|HOLAMBRA')].to_string(index=False))
