# Pinheiros: revisão do mix pelo estoque de 12/11/2026 e planograma da loja física (piloto assistido do planograma).
# Entradas: estoque (HD, Downloads/divina-terra/pinheiros), venda de Pinheiros na base v2 (11/2025 a 09/2026), classificação v2,
# papel de cada produto (abrangência) e o motor de planogramas (fonte/planogramas.py), com a venda da própria loja.
# Saídas, com estoque e venda da loja, fora do repositório público: kit/pinheiros-revisao-mix.xlsx, kit/pinheiros-planograma.html.
import json, pathlib, re, sys, unicodedata, html
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import receita as RC, planogramas as PL, plano_html as PH, classificar as CL

R = RC.R
LOJA = 'DT PINHEIROS'
EST = pathlib.Path('/Volumes/hd caique becker/Mac Caique/Downloads/divina-terra/pinheiros/Estoque Pinheiros 12-11.xls')
SEM = 13  # semanas de 07 a 09/2026
FORA = {'Cuidados pessoais e casa', 'Cafeteria da loja', 'Fora do planograma', 'A classificar'}

def nz(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', s.upper().strip())

# ---------- estoque x cadastro ----------
e = pd.read_excel(EST, header=0); e.columns = ['desc', 'estoque']; e['k'] = e.desc.map(nz)
e = e.groupby('k', as_index=False).agg(desc=('desc', 'first'), estoque=('estoque', 'sum'))
c = pd.read_pickle(R / 'analise/classificacao.pkl'); c['k'] = c.desc.map(nz)
c = c.sort_values('valor', ascending=False).drop_duplicates('k')
e = e.merge(c[['k', 'sku', 'marca', 'depto', 'setor', 'prateleira']], on='k', how='left')
sem_cod = e.sku.isna()
for i in e.index[sem_cod]:
    st, pr, _ = CL.classificar({'desc': e.at[i, 'desc'], 'marca': '', 'depto': '', 'catc': ''})
    e.at[i, 'setor'], e.at[i, 'prateleira'] = st, pr
e['origem'] = ['Sem código no cadastro com venda' if s else 'Cadastro' for s in sem_cod]

# ---------- venda de Pinheiros ----------
d = PL.dados_casa().copy(); d = d.assign(mes3=d.p.isin(RC.MES[-3:]))
x = d[d.loja == LOJA]
vend = x.groupby('sku').agg(v11=('valor', 'sum'), q11=('qtd', 'sum')).join(
    x[x.mes3].groupby('sku').agg(v3=('valor', 'sum'), q3=('qtd', 'sum'))).fillna(0).reset_index()
vend['sku'] = vend.sku.astype(int)
info = d.drop_duplicates('sku').assign(sku=lambda t: t.sku.astype(int)).set_index('sku')

# ---------- universo: o que tem estoque ou vendeu ----------
e['sku'] = e.sku.astype('Int64')
u = pd.merge(e.drop(columns='k'), vend, on='sku', how='outer')
for col in ('desc', 'marca', 'depto'):
    u[col] = u[col].fillna(u.sku.map(lambda s: info[col].get(s) if pd.notna(s) and s in info.index else None))
cls = c.assign(sku=c.sku.astype(int)).set_index('sku')
u['setor'] = u.setor.fillna(u.sku.map(lambda s: cls.setor.get(s) if pd.notna(s) else None))
u['prateleira'] = u.prateleira.fillna(u.sku.map(lambda s: cls.prateleira.get(s) if pd.notna(s) else None))
u['origem'] = u.origem.fillna('Vendeu, sem estoque em 12/11')
u[['estoque', 'v11', 'q11', 'v3', 'q3']] = u[['estoque', 'v11', 'q11', 'v3', 'q3']].fillna(0)
ABR = {int(k): v for k, v in json.loads((R / 'analise/abrangencia.json').read_text()).items()}
u['papel'] = u.sku.map(lambda s: ABR.get(int(s), {}).get('papel', '') if pd.notna(s) else '')
u['giro'] = u.q3 / SEM
u['cobertura'] = [(es / g) if g > 0 else None for es, g in zip(u.estoque, u.giro)]
pm_rede = d.groupby(d.sku.astype(int)).apply(lambda t: t.valor.sum() / max(t.qtd.sum(), 1))
u['preco'] = [(v / q) if q > 0 else (pm_rede.get(int(s_)) if pd.notna(s_) else None) for v, q, s_ in zip(u.v11, u.q11, u.sku)]
u['valor_est'] = [es * p if p else None for es, p in zip(u.estoque, u.preco)]

def acao(r):
    if r.setor in FORA: return 'Fora dos 16 setores'
    if r.estoque <= 0 and r.giro >= .5: return 'Repor já: vende e está sem estoque'
    if r.estoque <= 0: return 'Sem estoque, vende pouco'
    if r.q3 == 0 and r.v11 > 0: return 'Parado: vendeu antes de julho'
    if r.q3 == 0: return 'Parado: sem venda em 11 meses'
    if r.cobertura and r.cobertura > 26 and r.estoque > 6: return 'Excesso: mais de 6 meses de estoque'
    if r.cobertura and r.cobertura > 13 and r.estoque > 6: return 'Estoque alto: de 3 a 6 meses'
    return 'Saudável'
u['acao'] = [acao(r) for r in u.itertuples()]

# ---------- planograma de Pinheiros ----------
n_, tot, gr, ch, em = PL.TAM12['G']; fs, ex = PL.PER12['Suplemento forte']
res = tot - gr - ch; su = round((res - em) * fs); de = res - su
v = x[x.g.notna()].groupby('g').valor.sum(); sem_s = x[x.setorf == 'Suplementos sem setor'].valor.sum()
M = PL._divide(v, sem_s, su, de, em, RC.SET); M['Granel'] = gr; M['Chás'] = ch
base = json.loads((R / 'analise/planogramas.json').read_text()); NUC = {}
for c_, v_ in base['P']['cats'].items():
    NUC[c_] = {q['sku'] for n in v_.get('niveis', []) for m in n['mods'] for q in m} | {t['sku'] for t in v_.get('tubos', [])}
for c_, v_ in base['M']['cats'].items():
    if c_ not in NUC: NUC[c_] = {q['sku'] for n in v_.get('niveis', []) for m in n['mods'] for q in m}
NUC = {c_: {s_ for s_ in v_ if ABR.get(s_, {}).get('papel') == 'Essencial'} for c_, v_ in NUC.items()}  # núcleo = só os essenciais da rede
nuc_all = set().union(*NUC.values())
# núcleo que Pinheiros ainda não vende: entra com a venda média de uma loja da rede, para o motor posicionar
falta = [s for s in nuc_all if s not in set(x.sku.astype(int))]
outras = d[d.sku.astype(int).isin(falta)]
med = outras.groupby('sku').agg(valor=('valor', 'sum'), qtd=('qtd', 'sum'), lojas=('loja', 'nunique')).reset_index()
fz = []
for r_ in med.itertuples():
    b = outras[outras.sku == r_.sku].iloc[0].to_dict()
    b.update(loja=LOJA, valor=r_.valor / r_.lojas, qtd=r_.qtd / r_.lojas, mes3=True); fz.append(b)
xp = pd.concat([x, pd.DataFrame(fz)], ignore_index=True)
PL.T_ATUAL = 'G'
def monta_plano(M):
    cats = {}
    for cat in PL.CATS:
        f = M.get(cat, 0)
        if f <= 0: continue
        if cat == 'Granel':
            g = x[x.setorf == 'Granel'].groupby(['sku', 'desc', 'prat']).valor.sum().reset_index().sort_values('valor', ascending=False)
            g = g[~g.desc.str.contains(PL.EXC)].head(38); it = []
            for r_ in g.itertuples():
                lo, hi = PL.preco(int(r_.sku)); it.append(dict(sku=int(r_.sku), desc=r_.desc, nome=re.sub(r'\s*A GRANEL', '', r_.desc).title()[:28], fam=r_.prat, pmin=lo, pmax=hi, v=float(r_.valor)))
            it.sort(key=lambda t: (PL.FAM_ORD.index(t['fam']), -t['v']))
            cats[cat] = dict(cat='Granel', tubos=it, skus=len(it), f=f, livres=2, cob=sum(t['v'] for t in it) / max(1, float(x[x.setorf == 'Granel'].valor.sum())))
            continue
        y = PL._linhas(xp, cat, M)
        if y.empty: continue
        cats[cat] = PL.escolher(y, cat, f, NUC.get(cat))
    return cats
def ocupacao(M, cats):
    "Parte da largura ocupada e produtos vendidos de julho a setembro que não couberam, por setor."
    oc = {}
    for cat, cc in cats.items():
        if 'tubos' in cc: continue
        larg = sum((PL.UTIL if mi + 1 <= cc['f'] else PL.UTIL / 2) for mi in range(int(cc['f'] + .999))) * len(cc['niveis'])
        usado = sum(q['w'] * q['f'] for n in cc['niveis'] for m in n['mods'] for q in m)
        dentro = {q['sku'] for n in cc['niveis'] for m in n['mods'] for q in m}
        y = PL._linhas(xp, cat, M); y = y[y.mes3 & ~y.desc.str.contains(PL.EXC)]
        oc[cat] = (usado / larg, len({int(s_) for s_ in y.sku} - dentro), cc['skus'])
    return oc
# 1ª passada pela venda e preenchimento do espaço local com o que a loja vende. Depois, setor com prateleira sobrando
# (menos de 60% ocupada) cede meio módulo por vez para setor cheio com produto vendido que não coube; e monta de novo.
def preenche_local(cats):
    "Prateleira que sobrou no desenho (espaço local) recebe o que a própria Pinheiros vende e não coube, do mais vendido para o menos."
    n_loc = 0
    for cat, cc in cats.items():
        if 'tubos' in cc: continue
        dentro = {q['sku'] for n in cc['niveis'] for m in n['mods'] for q in m}
        y = PL._linhas(xp, cat, M); y = y[y.mes3 & ~y.desc.str.contains(PL.EXC) & (y.marca != 'A GRANEL')]
        g = y.groupby(['sku', 'desc', 'marca', 'prat']).agg(v=('valor', 'sum'), q=('qtd', 'sum')).reset_index().sort_values('v', ascending=False)
        g = g[~g.sku.astype(int).isin(dentro) & ~g.sku.astype(int).isin(PL.REGIONAL)]
        for r_ in g.itertuples():
            b = PL.banda(r_.desc); w = PL.largura(r_.desc); niv_ok = (5, 6) if b == 'gde' else (1, 2, 3, 4) if b == 'dose' else (2, 3, 4, 5)
            feito = False
            for n in sorted(cc['niveis'], key=lambda n_: PL.OLHOS.index(n_['n'])):
                if n['n'] not in niv_ok: continue
                for mi, m in enumerate(n['mods']):
                    larg = PL.UTIL if mi + 1 <= cc['f'] else PL.UTIL / 2
                    if sum(q['w'] * q['f'] for q in m) + w <= larg:
                        lo, hi = PL.preco(int(r_.sku))
                        m.append(dict(sku=int(r_.sku), desc=r_.desc, marca=r_.marca, prat=r_.prat, nome=PL.curto(r_.desc, r_.marca), mc=PL.nome_marca(r_.marca), w=w, f=1,
                                      v=float(r_.v), q=float(r_.q), pm=float(r_.v / max(r_.q, 1)), mp=r_.marca == PL.MARCA_PROPRIA, b=b, s=r_.prat, pmin=lo, pmax=hi,
                                      band=PL.NOME_B[b], loc=True))
                        if not m[:-1]: n['rots'][mi] = f'{r_.prat} · {PL.NOME_B[b]} · local da loja'
                        cc['skus'] += 1; cc['frentes'] = cc.get('frentes', 0) + 1; n_loc += 1; feito = True; break
                if feito: break
    return n_loc
M0 = dict(M)
meio = lambda v: max(.5, -(-v * 2 // 1) / 2)
for rodada in range(2):
    cats = monta_plano(M); preenche_local(cats); oc = ocupacao(M, cats); base_f = dict(M)
    sobra = 0.0
    for cat, (o, nf, n) in oc.items():
        alvo = meio(M[cat] * o / .85)
        if o < .7 and alvo < M[cat]: sobra += M[cat] - alvo; M[cat] = alvo
    fila = {cat: nf for cat, (o, nf, n) in oc.items() if nf > 2 and o > .75}
    while sobra >= .5 and fila:
        cat = max(fila, key=lambda c_: fila[c_] / M[c_]); M[cat] += .5; sobra -= .5
        fila[cat] -= .5 * oc[cat][2] / max(base_f[cat], .5)
        if fila[cat] <= 2: fila.pop(cat)
    if sobra >= .5: M['Gourmet'] = M.get('Gourmet', 0) + sobra
cats = monta_plano(M); N_LOCAL = preenche_local(cats)
AJUSTE = {c_: (M0.get(c_, 0), M[c_]) for c_ in M if M0.get(c_, 0) != M[c_]}
RP = {'PIN': {'modulos': M, 'cats': cats}}

pos = {}
for cat, cc in cats.items():
    if 'tubos' in cc:
        for k, t in enumerate(cc['tubos'], 1): pos[t['sku']] = (cat, f'Tubo {k}', 'Granel', 1)
        continue
    for n in cc['niveis']:
        for mi, m in enumerate(n['mods'], 1):
            for q in m: pos[q['sku']] = (cat, f'Módulo {mi}', f'Nível {n["n"]} · {PH.NIV[n["n"]]}', q['f'])
u['planograma'] = u.sku.map(lambda s: pos[int(s)][0] if pd.notna(s) and int(s) in pos else '')
u['lugar'] = u.sku.map(lambda s: f'{pos[int(s)][1]} · {pos[int(s)][2]}' if pd.notna(s) and int(s) in pos else '')
u['frentes'] = u.sku.map(lambda s: pos[int(s)][3] if pd.notna(s) and int(s) in pos else None)
inc = [s for s in pos if s in set(falta)]
novos = pd.DataFrame([dict(sku=s, desc=info.desc.get(s, ''), marca=info.marca.get(s, ''), setor=cls.setor.get(s), prateleira=cls.prateleira.get(s),
                           estoque=0, v11=0, q11=0, v3=0, q3=0, papel=ABR.get(s, {}).get('papel', ''), giro=0, cobertura=None, preco=None, valor_est=None,
                           acao='Incorpora: núcleo da rede que a loja não tem', origem='Núcleo da rede', planograma=pos[s][0], lugar=f'{pos[s][1]} · {pos[s][2]}', frentes=pos[s][3]) for s in inc])
u = pd.concat([u, novos.astype(object)], ignore_index=True)
no_plano = u.planograma.ne('')
u.loc[(u.acao == 'Saudável') & ~no_plano & ~u.setor.isin(FORA), 'acao'] = 'Fora do planograma: reduz ou sai aos poucos'
u.loc[(u.acao == 'Sem estoque, vende pouco') & no_plano, 'acao'] = 'Repor para o planograma: entra com 1 frente'
u.loc[(u.acao == 'Sem estoque, vende pouco') & ~no_plano, 'acao'] = 'Sem estoque e fora do planograma: não repor'

# ---------- onde montar cada setor (proposta para conferir com a trena) ----------
PAREDE = ['Proteínas', 'Creatina', 'Ômegas', 'Vitaminas', 'Colágeno', 'Bem-Estar', 'Intestino', 'Longevidade', 'Imunidade']
ILHA = ['Proteínas', 'Creatina', 'Performance', 'Cafés funcionais', 'Barras e snacks', 'Kids', 'Peso', 'Sem Glúten', 'Gourmet']
monta = []; cap = 8.0
for cat in PAREDE:
    f = float(M.get(cat, 0))
    if f <= 0 or cat not in cats: continue
    ali = min(f, cap) if cat not in ('Proteínas', 'Creatina') else min(f, cap, 2.0 if cat == 'Proteínas' else 1.0)
    if ali > 0: monta.append((cat, ali, 'Parede de suplementos (M01): níveis 1 a 6; o 7º só para estoque aéreo e placa')); cap -= ali
    if f - ali > 0: monta.append((cat, f - ali, 'Ilha central (M02), ao lado da parede'))
for cat in ILHA:
    if cat in ('Proteínas', 'Creatina') or cat not in cats: continue
    f = float(M.get(cat, 0))
    if cat == 'Gourmet':
        monta.append((cat, min(3.0, f), 'Três módulos ao lado das mesas, no lugar das farinhas: À mesa, Receber, Do mundo'))
        if f > 3: monta.append((cat, f - 3, 'Ilha de Gourmet básicos (M02)'))
        continue
    monta.append((cat, f, 'Ilha central (M02)'))
monta.append(('Chás', float(M.get('Chás', 0)), 'Estante do fundo (Z06), com gancheira para chá de sachê'))
monta.append(('Granel', float(M.get('Granel', 0)), 'Módulos de granel atuais (M04): nenhum bin sai do lugar; placa visível da porta e potinho de prova'))

# ---------- planilha ----------
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
TERRA = '461D17'; H = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor=TERRA)
def tabela(ws, t, larg):
    for j, col in enumerate(t.columns, 1):
        q = ws.cell(1, j, col); q.font = H; q.fill = HF; q.alignment = Alignment(wrap_text=True, vertical='center')
        ws.column_dimensions[get_column_letter(j)].width = larg.get(col, 14)
    for i, row in enumerate(t.itertuples(index=False), 2):
        for j, val in enumerate(row, 1): ws.cell(i, j, None if (isinstance(val, float) and pd.isna(val)) or val is pd.NA else val)
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions; ws.row_dimensions[1].height = 34
COLS = {'sku': 'SKU', 'desc': 'Produto', 'marca': 'Marca', 'setor': 'Setor', 'prateleira': 'Prateleira', 'papel': 'Papel na rede', 'estoque': 'Estoque 12/11',
        'q3': 'Vendeu 07 a 09/2026 (un.)', 'giro': 'Giro por semana', 'cobertura': 'Semanas de estoque', 'v11': 'Venda 11 meses (R$)', 'valor_est': 'Estoque a preço de venda (R$)',
        'acao': 'O que fazer', 'planograma': 'Setor no planograma', 'lugar': 'Lugar', 'frentes': 'Frentes', 'origem': 'Origem'}
out = u[list(COLS)].rename(columns=COLS).copy()
for col in ('Giro por semana', 'Semanas de estoque', 'Venda 11 meses (R$)', 'Estoque a preço de venda (R$)'):
    out[col] = out[col].map(lambda val: round(float(val), 1) if pd.notna(val) else None)
ORD = ['Repor já: vende e está sem estoque', 'Incorpora: núcleo da rede que a loja não tem', 'Excesso: mais de 6 meses de estoque', 'Estoque alto: de 3 a 6 meses', 'Parado: vendeu antes de julho',
       'Parado: sem venda em 11 meses', 'Fora do planograma: reduz ou sai aos poucos', 'Repor para o planograma: entra com 1 frente', 'Saudável', 'Sem estoque e fora do planograma: não repor', 'Fora dos 16 setores']
out = out.assign(o=out['O que fazer'].map(ORD.index)).sort_values(['o', 'Setor', 'Venda 11 meses (R$)'], ascending=[True, True, False]).drop(columns='o')
rs = u.groupby('acao').agg(produtos=('desc', 'count'), estoque=('estoque', 'sum'), valor=('valor_est', 'sum')).reindex(ORD).fillna(0)
por_setor = u[~u.setor.isin(FORA)].pivot_table(index='setor', columns='acao', values='desc', aggfunc='count', fill_value=0)
wb = Workbook(); ws = wb.active; ws.title = 'Leia antes'
TX = [('Divina Terra · Pinheiros · revisão do mix e planograma da loja', 't'),
      ('Estoque de 12/11/2026 cruzado com a venda da loja (11/2025 a 09/2026), a classificação v2 e o planograma montado com a venda da própria Pinheiros.', ''), ('', ''),
      ('O que fazer', 's'),
      ('Repor já: vendeu pelo menos 1 a cada 2 semanas entre julho e setembro e está sem estoque. Pedido na próxima compra.', ''),
      ('Incorpora: produto do núcleo da rede que a loja não tem. Entra no planograma; pedir na próxima compra.', ''),
      ('Excesso: mais de 6 meses de estoque pelo giro de julho a setembro, e mais do que uma frente cheia (6 unidades). Pedido zero até baixar.', ''),
      ('Estoque alto: de 3 a 6 meses de estoque, e mais do que uma frente cheia. Pedido menor até voltar a 2 meses.', ''),
      ('Parado: tem estoque e não vendeu de julho a setembro. Não repõe. Vai para a mesa do mês ou para transferência, sem queima.', ''),
      ('Fora do planograma: vende, mas não coube no desenho. Fica com 1 frente na parte local enquanto girar; senão, sai aos poucos.', ''),
      ('Repor para o planograma: está no desenho, vende pouco e está sem estoque. Entra com 1 frente.', ''),
      ('Saudável: está no planograma, vende e tem estoque na medida.', ''), ('', ''),
      ('Sem estoque e fora do planograma: vendeu alguma vez nos 11 meses, mas não entra no desenho. Não repor.', ''),
      ('Como ler', 's'),
      ('Giro: unidades por semana, de julho a setembro de 2026. Semanas de estoque: estoque de 12/11 dividido pelo giro.', ''),
      ('Estoque a preço de venda: estoque vezes o preço médio pago na loja. Sem custo por produto, não há valor de custo.', ''),
      ('Lugar: módulo e nível no planograma de Pinheiros (aba Planograma). Medidas estimadas: conferir com trena antes de montar.', ''), ('', ''),
      ('Este arquivo tem estoque e venda da loja. Uso interno da Divina Terra e da 75 LAB.', '')]
for i, (t, k) in enumerate(TX, 1):
    q = ws.cell(i, 1, t); q.alignment = Alignment(wrap_text=True)
    if k == 't': q.font = Font(bold=True, size=16, color=TERRA)
    elif k == 's': q.font = Font(bold=True, size=12, color='7C381F')
ws.column_dimensions['A'].width = 130
ws = wb.create_sheet('Resumo'); tabela(ws, rs.reset_index().rename(columns={'acao': 'O que fazer', 'produtos': 'Produtos', 'estoque': 'Unidades em estoque', 'valor': 'Estoque a preço de venda (R$)'}).round(0), {'O que fazer': 50})
ws = wb.create_sheet('Por setor'); tabela(ws, por_setor.reset_index(), {'setor': 28})
ws = wb.create_sheet('Produto a produto'); tabela(ws, out, {'Produto': 46, 'Setor': 22, 'Prateleira': 26, 'O que fazer': 40, 'Lugar': 26, 'Origem': 26})
pl = []
for cat, cc in cats.items():
    if 'tubos' in cc:
        for k, t in enumerate(cc['tubos'], 1): pl.append([cat, 'Granel', f'Tubo {k}', '', t['sku'], t['desc'], 'A granel', 1, t['fam']])
        continue
    for n in cc['niveis']:
        for mi, m in enumerate(n['mods'], 1):
            for p_, q in enumerate(m, 1): pl.append([cat, f'Módulo {mi}', f'Nível {n["n"]} · {PH.NIV[n["n"]]}', p_, q['sku'], q['desc'], q['mc'], q['f'], n['rots'][mi - 1] if mi - 1 < len(n['rots']) else ''])
est = dict(zip(u.sku, u.estoque))
plt = pd.DataFrame(pl, columns=['Setor', 'Módulo', 'Nível', 'Posição', 'SKU', 'Produto', 'Marca', 'Frentes', 'Prateleira e tamanho'])
plt['Estoque 12/11'] = plt.SKU.map(lambda s: est.get(s, 0)); plt['Pedir'] = ['Sim' if (q or 0) <= 0 else '' for q in plt['Estoque 12/11']]
ws = wb.create_sheet('Planograma'); tabela(ws, plt, {'Produto': 46, 'Nível': 16, 'Prateleira e tamanho': 34})
ws = wb.create_sheet('Onde montar'); tabela(ws, pd.DataFrame([(a, round(b, 1), c_) for a, b, c_ in monta], columns=['Setor', 'Módulos de 0,90 m', 'Onde']), {'Setor': 22, 'Onde': 90})
xl = R / 'kit/pinheiros-revisao-mix.xlsx'; wb.save(xl)

# ---------- página do planograma ----------
br = lambda val, k=0: f'{val:,.{k}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def tab(cab, lin): return '<table class="tb"><thead><tr>' + ''.join(f'<th>{c_}</th>' for c_ in cab) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{v_}</td>' for v_ in l) + '</tr>' for l in lin) + '</tbody></table>'
k = rs['produtos']; vv = rs['valor']; med_cob = u[(u.estoque > 0) & (u.giro > 0)].cobertura.median()
cards = [('Produtos em estoque', br(len(e))), ('Repor já', br(k.get('Repor já: vende e está sem estoque', 0))), ('Incorporar do núcleo', br(k.get('Incorpora: núcleo da rede que a loja não tem', 0))),
         ('Parados com estoque', br(k.get('Parado: vendeu antes de julho', 0) + k.get('Parado: sem venda em 11 meses', 0))),
         ('Parado, a preço de venda', 'R$ ' + br((vv.get('Parado: vendeu antes de julho', 0) + vv.get('Parado: sem venda em 11 meses', 0)) / 1000) + ' mil'),
         ('Excesso, mais de 6 meses', br(k.get('Excesso: mais de 6 meses de estoque', 0)))]
lista = lambda a, n=40: tab(['Produto', 'Marca', 'Setor', 'Estoque', 'Giro/sem.', 'Lugar'], [[html.escape(str(r.desc).title()[:52]), html.escape(str(r.marca).title()), r.setor, br(r.estoque, 0 if float(r.estoque).is_integer() else 2), br(r.giro, 1), r.lugar] for r in u[u.acao == a].sort_values('v11', ascending=False).head(n).itertuples()])
ordem = [c_ for c_ in PL.CATS if c_ in cats]
def bloco(c_):
    if 'tubos' in cats[c_]: return PH.plano(RP, 'PIN', c_)
    n = int(cats[c_]['f'] + .999)
    return ''.join(f'<div class="bl">{PH.plano(RP, "PIN", c_, maxm=3, ini=k)}</div>' for k in range(0, n, 3))
onde = lambda c_: ' e '.join(o.split(':')[0].split(',')[0] for a, b, o in monta if a == c_)
planos = ''.join(f'<section class="pl" id="pl-{i}"><h3>{html.escape(c_)} <small>{br(float(M[c_]), 1)} módulo{"s" if M[c_] > 1 else ""} · {onde(c_)}</small></h3>{bloco(c_)}</section>' for i, c_ in enumerate(ordem))
pag = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><base href="../"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Pinheiros · planograma da loja</title><link rel="icon" href="assets/logos/dt-icone-terra.svg">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,400&display=swap" rel="stylesheet">
<style>@font-face{{font-family:'General Sans';src:url('assets/fontes/GeneralSans-Variable.ttf');font-weight:200 700}}
:root{{--iogurte:#F7F5F1;--aveia:#E5DDD1;--linho:#BCAD99;--cap:#AC834C;--choco:#7C381F;--terra:#461D17;--oliva:#596D49;--matcha:#A9C094;--acafrao:#CA942A;--cinza:#6F5F55;--serif:'Source Serif 4',Georgia,serif;--sans:'General Sans',system-ui,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--iogurte);color:var(--terra);font:15px/1.45 var(--sans)}}main{{max-width:1500px;margin:0 auto;padding:36px 28px 80px}}
h1,h2,h3{{font-family:var(--serif);font-weight:400;margin:0}}h1{{font-size:46px;margin:18px 0 6px}}h1 em{{color:var(--choco)}}h2{{font-size:32px;margin:44px 0 12px}}h3{{font-size:26px;margin:10px 0}}h3 small{{font-family:var(--sans);font-size:14px;color:var(--cinza);margin-left:8px}}
.lead{{font-size:18px;color:var(--cinza);max-width:1000px}}.m img{{height:24px}}.m{{display:flex;gap:12px;align-items:center}}.m img.l{{height:16px}}
.cards{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:22px 0}}.cards div{{background:var(--aveia);border-radius:12px;padding:14px 16px}}.cards b{{display:block;font-family:var(--serif);font-weight:300;font-size:36px;line-height:1}}.cards div:nth-child(2),.cards div:nth-child(3){{background:var(--terra);color:var(--iogurte)}}.cards div:nth-child(2) b,.cards div:nth-child(3) b{{color:var(--acafrao)}}
.tb{{border-collapse:collapse;width:100%;font-size:14px;background:#fff;border-radius:10px;overflow:hidden;margin:8px 0}}.tb th{{background:var(--aveia);text-align:left;padding:7px 10px;font-weight:600}}.tb td{{padding:6px 10px;border-top:1px solid var(--aveia);vertical-align:top}}
.pl{{background:#fff;border-radius:14px;padding:18px 20px;margin:16px 0}}.bl{{margin:10px 0 22px;break-inside:avoid;overflow-x:auto}}.nota{{font-size:13.5px;color:var(--cinza)}}.passo{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}.passo div{{background:#fff;border-radius:12px;padding:14px 16px}}.passo b{{display:block;color:var(--choco);font-size:13px;letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px}}
@media print{{main{{padding:12mm}}.pl{{page-break-inside:avoid}}}}
{PH.CSS}</style></head><body><main>
<div class="m"><img src="assets/logos/dt-horizontal-terra.svg" alt="Divina Terra"><span>×</span><img class="l" src="assets/logos/75lab-logo-preto.svg" alt="75 LAB"></div>
<h1>Pinheiros: <em>o planograma da loja</em></h1>
<p class="lead">Piloto assistido do planograma. O mix revisado pelo estoque de 12/11/2026 e pela venda da própria loja, e o desenho de cada setor, módulo a módulo. Os móveis são os de hoje: as medidas foram estimadas na visita de 14/10 e precisam de trena antes da montagem.</p>
<div class="cards">{''.join(f'<div><b>{v_}</b>{t_}</div>' for t_, v_ in cards)}</div>
<h2>Como montar</h2>
<div class="passo"><div><b>1. Antes</b>Conferir as medidas com trena e separar os parados (lista abaixo) para a mesa do mês ou transferência.</div><div><b>2. Pedido</b>Repor o que vende e está sem estoque e pedir os produtos do núcleo que a loja não tem.</div><div><b>3. Montagem</b>Um setor por vez, de cima para baixo, seguindo módulo e nível. Fora de horário, em duas noites.</div><div><b>4. Depois</b>Foto de cada módulo, etiqueta nova e leitura da venda nas semanas 6 e 12.</div></div>
<h2>Onde fica cada setor</h2>{tab(['Setor', 'Módulos de 0,90 m', 'Onde'], [[a, br(b, 1), o] for a, b, o in monta])}
<p class="nota">Proposta a partir do mapa de Pinheiros do book e do inventário de móveis da visita. Módulos por setor: venda da própria loja vezes o papel de cada setor, no tamanho G (39 módulos), perfil suplemento forte; depois, setor com prateleira sobrando cedeu meio módulo para setor com produto vendido que não coube. Prateleira que sobrou no desenho recebeu o que a própria loja vende, marcado como local.</p>
<h2>Planograma, setor a setor</h2><p class="nota">Cada foto é uma frente. Níveis 3 e 4 são os olhos. Núcleo, lista e local como no book.</p>{planos}
<h2>Repor já</h2><p class="nota">Vende pelo menos 1 a cada 2 semanas e está sem estoque. Os 40 que mais vendem; a lista completa está na planilha.</p>{lista('Repor já: vende e está sem estoque')}
<h2>Incorporar do núcleo</h2><p class="nota">Produtos essenciais da rede que Pinheiros ainda não tem. Já estão no planograma.</p>{lista('Incorpora: núcleo da rede que a loja não tem')}
<h2>Excesso de estoque</h2><p class="nota">Mais de 6 meses de estoque pelo giro de julho a setembro, e mais do que uma frente cheia. Pedido zero até baixar. Na loja, metade dos produtos tem mais de {br(med_cob, 0)} semanas de estoque.</p>{lista('Excesso: mais de 6 meses de estoque')}
<h2>Parados com estoque</h2><p class="nota">Têm estoque e não venderam de julho a setembro de 2026. Não repor; mesa do mês ou transferência, sem queima. Sem venda na loja, o valor usa o preço médio da rede.</p>{lista('Parado: vendeu antes de julho')}{lista('Parado: sem venda em 11 meses')}
<p class="nota">Fonte: estoque de Pinheiros em 12/11/2026; relatório de vendas de 11/2025 a 09/2026; classificação v2; motor de planogramas do book, com a venda de Pinheiros. Tem estoque e venda da loja: uso interno.</p>
</main>{PH.DICA}</body></html>'''
(R / 'kit/pinheiros-planograma.html').write_text(pag)
bad = [t for t in ('—', '–') if t in pag]
print(xl); print('módulos', {k_: v_ for k_, v_ in M.items() if v_}, 'soma', sum(M.values())); print('ajuste', AJUSTE, '| locais preenchidos', N_LOCAL)
for c_, (o_, nf_, n_) in ocupacao(M, cats).items(): print(f'  {c_:18s} {M[c_]:4} mód  ocupação {o_*100:5.1f}%  fora {nf_}')
print(rs.round(0).to_string()); print('sem código:', int(sem_cod.sum()), '| no planograma:', len(pos), '| incorpora:', len(inc), '| travessão' if bad else '| sem travessão')

