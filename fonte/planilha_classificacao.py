# Gera kit/divina-terra-classificacao-v2.xlsx: SKU, categoria atual, categoria sugerida e justificativa
# (pedido 2.2 da devolutiva de 16/11/2026). Tem venda por SKU: fica fora do repositório público.
import pathlib, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

R = pathlib.Path(__file__).resolve().parent.parent
s = pd.read_pickle(R / 'analise/classificacao.pkl')
v1 = pd.read_pickle(R / 'analise/v1_categoria.pkl')
v1['sku'] = v1.sku.astype(str)
def nome_v1(g, sf):
    if isinstance(g, str): return g
    sf = str(sf)
    if sf.startswith('Empório'): return 'Empório'
    return {'Café da loja': 'Cafeteria', 'Sem regra': 'Sem setor', 'Fora de setor': 'Sem setor'}.get(sf, sf)
v1['book_v1'] = [nome_v1(g, sf) for g, sf in zip(v1.g, v1.setorf)]
s['sku'] = s.sku.astype(str)
s = s.merge(v1[['sku', 'book_v1']], on='sku', how='left')
s['book_v1'] = s.book_v1.fillna('Sem setor')

# equivalência entre os nomes do book v1 e os setores da rede, para marcar o que mudou
EQ = {'Proteínas': 'Proteínas', 'Creatina': 'Creatina', 'Colágeno': 'Colágeno & Beleza', 'Performance': 'Performance',
      'Bem-Estar': 'Equilíbrio & Bem-Estar', 'Longevidade': 'Longevidade Saudável', 'Vitaminas': 'Vitaminas de A a Z',
      'Ômegas': 'Ômegas', 'Intestino': 'Saúde Intestinal', 'Imunidade': 'Imunidade', 'Chás': 'Chás', 'Granel': 'Granel',
      'Barras e snacks': 'Barras e snacks', 'Cafeteria': 'Cafeteria da loja'}
def mudou(r):
    if r.book_v1 == 'Kids e Peso':
        return 'Não' if r.setor in ('Kids', 'Peso & Composição Corporal') else 'Sim'
    if r.book_v1 == 'Cafés funcionais':
        return 'Não' if r.prateleira == 'Cafés funcionais' else 'Sim'
    if r.book_v1 in ('Empório', 'Despensa'):
        return 'Não' if r.setor == 'Gourmet' else 'Sim'
    return 'Não' if EQ.get(r.book_v1) == r.setor else 'Sim'
s['mudou'] = [mudou(r) for r in s.itertuples()]

s = s.sort_values('valor', ascending=False).reset_index(drop=True)
ac = s.valor.cumsum() / s.valor.sum()
s['curva'] = ['A' if a <= .8 else 'B' if a <= .95 else 'C' for a in ac]

cols = [('sku', 'SKU', 9), ('desc', 'Descrição', 48), ('marca', 'Marca', 20), ('depto', 'Departamento no sistema', 22),
        ('catc', 'Categoria no sistema', 22), ('book_v1', 'Categoria no book v1', 18), ('setor', 'Setor sugerido', 26),
        ('prateleira', 'Prateleira sugerida', 30), ('tipo', 'Tipo de setor', 18), ('mudou', 'Mudou em relação ao book v1', 14),
        ('justificativa', 'Justificativa', 70), ('origem', 'Como foi decidido', 18), ('curva', 'Curva', 7),
        ('valor', 'Venda 10/2025 a 10/2026 (R$)', 16), ('lojas', 'Lojas com venda', 10)]

TERRA, AVEIA, IOG = '461D17', 'E5DDD1', 'F7F5F1'
H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor=TERRA)
def tabela(ws, df, cs):
    for j, (c, t, w) in enumerate(cs, 1):
        x = ws.cell(1, j, t); x.font = H; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical='center')
        ws.column_dimensions[get_column_letter(j)].width = w
    for i, row in enumerate(df[[c for c, _, _ in cs]].itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            ws.cell(i, j, None if (isinstance(v, float) and pd.isna(v)) else v)
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions; ws.row_dimensions[1].height = 34
    for j, (c, _, _) in enumerate(cs, 1):
        if c == 'valor':
            for i in range(2, len(df) + 2): ws.cell(i, j).number_format = '#,##0'

wb = Workbook()
ws = wb.active; ws.title = 'Leia antes'
import json
n = len(s); mud = (s.mudou == 'Sim').sum(); cor = (s.origem == 'Corrigido na revisão item a item').sum()
pl = {str(d['sku']) for d in json.loads((R / 'analise/skus_planograma_v2.json').read_text())}
rev = len(set(s.sku.head(2000)) | (pl & set(s.sku)))
br = lambda v: f'{v:,}'.replace(',', '.')
pct = lambda d: f'{d.valor.sum() / s.valor.sum() * 100:.1f}'.replace('.', ',')
pa = s[s.tipo == 'Proposta 75 LAB']; ac_ = s[s.setor == 'A classificar']
txt = [
    ('Divina Terra · Classificação de produtos v2', 'titulo'),
    ('Resposta ao item 2.2 da devolutiva de 16/11/2026: relação de produtos com SKU, categoria atual, categoria sugerida e justificativa.', ''),
    ('', ''),
    ('O que mudou no método', 'sub'),
    ('No book v1 a categoria saía de palavras da descrição do produto. Isso gerou erros como coenzima Q10 em saúde intestinal, kombucha em chás e desodorante em barras.', ''),
    ('Na v2 cada produto segue a árvore de 16 setores do material Setores e Categorias da própria rede, com as regras de domicílio de lá: linha infantil só em Kids, magnésio em Equilíbrio, cromo em Peso, coenzima Q10 em Ômegas, glutamina e cúrcuma em Saúde Intestinal, vitamina C, D e zinco em Vitaminas, chá pelo formato.', ''),
    (f'Depois da regra, os {br(rev)} produtos que mais pesam (os 2.000 mais vendidos e todos os que apareceram nos planogramas) foram revisados um a um; {br(cor)} tiveram a regra corrigida.', ''),
    ('', ''),
    ('Números', 'sub'),
    (f'{br(n)} produtos com venda entre 10/2025 e 10/2026.', ''),
    (f'{br(mud)} mudaram de categoria em relação ao book v1.', ''),
    (f'{br(len(ac_))} ficaram sem setor definido ({pct(ac_)}% da venda) e estão na aba A validar.', ''),
    ('', ''),
    ('Pontos que dependem de validação da Divina Terra', 'sub'),
    ('1. Barras e snacks como área própria (item 2.6 da devolutiva). A árvore da rede não tem esse setor; hoje as barrinhas ficam espalhadas.', ''),
    ('2. Geladeira e bebidas prontas como área própria (item 2.5): kombucha, bebidas proteicas prontas, iogurtes e queijos vegetais saem de chás e de suplementos em pó.', ''),
    ('3. Cafés funcionais (Supercoffee, Ultracoffee, Cappuccinofit e similares) em Performance, numa prateleira própria: a ficha de Performance da rede lista a marca Caffeine. Café especial torrado continua em Gourmet. Cafés termogênicos (Desincoffee, Supercafé, Drenocoffee) ficam em Peso & Composição Corporal.', ''),
    ('4. "Caixa" deixa de ser categoria: é um ponto de exposição secundária, com regra própria no planograma.', ''),
    ('5. Produtos sem setor definido (aba A validar): a rede indica o domicílio.', ''),
    ('6. Ômegas continua setor próprio, colado em Vitaminas (item 2.4): ômega vende 4,6% da rede e a coenzima Q10, que a rede põe em Ômegas, mais 1,7%; Vitaminas vende 2,6%. Na loja mediana são cerca de 50 itens de ômega. Em loja pequena, os dois dividem a mesma gôndola.', ''),
    ('7. O material Setores e Categorias da rede se contradiz sobre vitamina C: a regra 1 diz que toda vitamina C fica em Imunidade; a regra 2 e a ficha de Vitaminas dizem que a linha completa de C, D e zinco mora em Vitaminas de A a Z. Seguimos a regra 2.', ''),
    ('8. Ervas medicinais em pacote (unha de gato, ipê roxo, guaco, quebra-pedra) não cabem nas quatro prateleiras de Chás: ficaram em Energia e sabor até a rede decidir.', ''),
    ('9. Pizzas e pratos congelados e água de coco do departamento sem glúten ficaram em Sem Glúten, mas precisam de frio.', ''),
    ('', ''),
    ('Abas', 'sub'),
    ('Resumo por setor: quantos produtos e quanto da venda em cada setor e prateleira.', ''),
    ('Produtos: a lista completa, com filtro em todas as colunas.', ''),
    ('A validar: produtos em áreas e prateleiras propostas pela 75 LAB e produtos sem setor.', ''),
    ('', ''),
    ('Este arquivo tem venda por SKU. Uso interno da Divina Terra e da 75 LAB.', ''),
]
for i, (t, k) in enumerate(txt, 1):
    c = ws.cell(i, 1, t); c.alignment = Alignment(wrap_text=True, vertical='top')
    if k == 'titulo': c.font = Font(bold=True, size=16, color=TERRA)
    elif k == 'sub': c.font = Font(bold=True, size=12, color='7C381F')
ws.column_dimensions['A'].width = 130

ws = wb.create_sheet('Resumo por setor')
r = s.groupby(['tipo', 'setor', 'prateleira']).agg(skus=('sku', 'count'), valor=('valor', 'sum'), mud=('mudou', lambda x: (x == 'Sim').sum())).reset_index()
r['pct'] = (r.valor / s.valor.sum() * 100).round(2)
ordem = {'Árvore da rede': 0, 'Proposta 75 LAB': 1, 'Fora dos setores': 2}
tot = r.groupby('setor').valor.transform('sum')
r = r.assign(o=r.tipo.map(ordem), t=-tot).sort_values(['o', 't', 'valor'], ascending=[True, True, False])
tabela(ws, r, [('tipo', 'Tipo de setor', 18), ('setor', 'Setor', 28), ('prateleira', 'Prateleira', 34), ('skus', 'Produtos', 10),
               ('pct', '% da venda', 11), ('mud', 'Mudaram desde o book v1', 14)])

ws = wb.create_sheet('Produtos'); tabela(ws, s, cols)
ws = wb.create_sheet('A validar')
tabela(ws, s[(s.tipo == 'Proposta 75 LAB') | (s.setor == 'A classificar') | (s.prateleira == 'Cafés funcionais')], cols)

out = R / 'kit/divina-terra-classificacao-v2.xlsx'
out.parent.mkdir(exist_ok=True)
wb.save(out)
print(out, n, 'produtos;', mud, 'mudaram;', rev, 'revisados item a item')
