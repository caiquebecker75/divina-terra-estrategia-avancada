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
        larg = sum(cc['larg'] if cc.get('larg') else [(PL.UTIL if mi + 1 <= cc['f'] else PL.UTIL / 2) for mi in range(int(cc['f'] + .999))]) * len(cc['niveis'])
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
                    larg = cc['larg'][mi] if cc.get('larg') else (PL.UTIL if mi + 1 <= cc['f'] else PL.UTIL / 2)
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
# ---------- os móveis reais de Pinheiros (planta R00 de 02/01/2026, folha 02/11, conferida com as fotos da visita de 14/10) ----------
# Metros: X da fachada (vitrine) para o fundo da loja; Y da parede de suplementos (esquerda de quem entra) para a parede do granel.
# Cada módulo leva a largura útil real (largura do móvel menos 4 cm de montante). Destino no fundo, rotina no caminho.
def mv(id_, nome, grupo, x0, x1, y0, y1, bays, alt=1.6, niv=6, olha='', nota=''):
    return dict(id=id_, nome=nome, grupo=grupo, x0=x0, x1=x1, y0=y0, y1=y1, bays=bays, alt=alt, niv=niv, olha=olha, nota=nota)
PS = [(0.63, 1.43), (1.43, 2.23), (2.23, 3.33), (3.33, 4.43), (4.43, 5.53), (5.53, 6.63), (6.63, 7.73), (7.73, 8.71)]
SUP = [[('Vitaminas', 76)], [('Ômegas', 76)], [('Colágeno', 53), ('Imunidade', 53)], [('Creatina', 106)], [('Proteínas', 106)], [('Proteínas', 106)], [('Proteínas', 106)], [('Proteínas', 94)]]
MOVEIS = [mv(f'S{k + 1}', f'Parede de suplementos · módulo {k + 1}', 'parede', a, b, 0.0, 0.32, [SUP[k]], alt=2.2, niv=7, olha='y+',
             nota='Módulo de parede de 7 níveis: o 7º, no alto, fica só para estoque aéreo e placa do setor.') for k, (a, b) in enumerate(PS)]
GON = [('1', 1.58, 3.39, [[('Peso', 86)], [('Cafés funcionais', 86)]], [[('Barras e snacks', 86)], [('Barras e snacks', 86)]]),
       ('2', 4.24, 5.54, [[('Performance', 126)]], [[('Barras e snacks', 126)]]),
       ('3', 5.54, 7.34, [[('Performance', 86)], [('Performance', 86)]], [[('Sem Glúten', 86)], [('Sem Glúten', 86)]]),
       ('4', 8.19, 9.49, [[('Proteínas', 126)]], [[('Sem Glúten', 126)]])]
for g, a, b, A, B_ in GON:
    MOVEIS.append(mv(f'G{g}A', f'Gôndola {g} · lado da parede', 'gondola', a, b, 1.56, 1.955, A, olha='y-', nota='Lado virado para a parede de suplementos. Na gôndola, o nível 1 é o topo.'))
    MOVEIS.append(mv(f'G{g}B', f'Gôndola {g} · lado do balcão', 'gondola', a, b, 1.955, 2.35, B_, olha='y+', nota='Lado virado para o balcão da balança e o granel. Na gôndola, o nível 1 é o topo.'))
FUNDO = [(0.0, 0.95, [('Longevidade', 91)]), (0.95, 1.90, [('Intestino', 91)]), (1.90, 2.85, [('Bem-Estar', 91)])]
for k, (a, b, bay) in enumerate(FUNDO):
    MOVEIS.append(mv(f'E{k + 1}', f'Parede de encapsulados · módulo {k + 1}', 'fundo', 13.87, 14.17, a, b, [bay], alt=2.0, olha='x-',
                     nota='Parede do fundo, ao lado do caixa: cápsulas e frascos de uso diário.'))
MOVEIS.append(mv('C1', 'Chás', 'direita', 5.81, 7.04, 6.09, 6.39, [[('Chás', 119)]], alt=2.0, olha='y-', nota='Painel do lado direito: caixinhas nas prateleiras e sachês na gancheira.'))
for k, (a, b) in enumerate([(7.04, 7.99), (7.99, 8.94), (8.94, 9.89)]):
    MOVEIS.append(mv(f'R{k + 1}', f'Gourmet · módulo {k + 1}', 'direita', a, b, 6.09, 6.39, [[('Gourmet', 91)]], alt=2.0, olha='y-',
                     nota='Onde ficavam as farinhas, perto das mesas: o Gourmet de quem senta para o café.'))
# planograma de cada setor nos módulos reais, na ordem dos móveis
ordem_mod = {}
for m_ in MOVEIS:
    for bi, bay in enumerate(m_['bays']):
        for si, (cat, wcm) in enumerate(bay): ordem_mod.setdefault(cat, []).append((m_['id'], bi, si, wcm))
MF = {c_: len(v_) for c_, v_ in ordem_mod.items()}
cats_f = {}
for cat, lst_ in ordem_mod.items():
    y = PL._linhas(xp, cat, MF)
    if y.empty: continue
    cc = PL.escolher(y, cat, len(lst_), NUC.get(cat), larg_in=[w_ for *_, w_ in lst_]); cc['larg'] = [w_ for *_, w_ in lst_]; cc['onde'] = lst_
    cats_f[cat] = cc
cats_f['Granel'] = cats['Granel']
M = {c_: round(sum(cc['larg']) / PL.UTIL, 1) if cc.get('larg') else cc.get('f', 0) for c_, cc in cats_f.items()}
cats = cats_f; N_LOCAL = preenche_local(cats)
RP = {'PIN': {'modulos': M, 'cats': cats}}

pos = {}
for cat, cc in cats.items():
    if 'tubos' in cc:
        for k, t in enumerate(cc['tubos'], 1): pos[t['sku']] = (cat, f'Tubo {k}', 'Granel', 1)
        continue
    NOME_MV = {m_['id']: m_['nome'] for m_ in MOVEIS}
    for n in cc['niveis']:
        for mi, m in enumerate(n['mods'], 1):
            onde_ = NOME_MV[cc['onde'][mi - 1][0]] + (f' (módulo {cc["onde"][mi - 1][1] + 1})' if len([o for o in cc['onde'] if o[0] == cc['onde'][mi - 1][0]]) > 1 else '') if cc.get('onde') else f'Módulo {mi}'
            for q in m: pos[q['sku']] = (cat, onde_, f'Nível {n["n"]} · {PH.NIV[n["n"]]}', q['f'])
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

# ---------- onde montar cada setor: móveis reais ----------
monta = []
for cat, cc in cats.items():
    if cat == 'Granel': monta.append(('Granel', 0, 'Granel P, Granel 18 e Granel M, à direita de quem entra: nenhum pote sai do lugar')); continue
    lugares = []
    for mid, bi, si, wcm in cc.get('onde', []):
        nm = next(m_['nome'] for m_ in MOVEIS if m_['id'] == mid)
        if nm not in lugares: lugares.append(nm)
    monta.append((cat, round(sum(cc.get('larg', [])) / 100, 2), '; '.join(lugares)))
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
ws = wb.create_sheet('Onde montar'); tabela(ws, pd.DataFrame([(a, b, c_) for a, b, c_ in monta], columns=['Setor', 'Metros de prateleira por nível', 'Onde']), {'Setor': 22, 'Onde': 110})
xl = R / 'kit/pinheiros-revisao-mix.xlsx'; wb.save(xl)

pag = ''
br = lambda val, k=0: f'{val:,.{k}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
# ---------- lista de pedido (23/11/2026) ----------
# Alvo: 4 semanas de venda até a próxima compra + 1 de segurança, e nunca menos que as frentes do planograma (+ 1 unidade se vende 1 a cada 2 semanas ou mais).
# Granel em kg: 3 semanas, mínimo de 2 kg. Essencial que a loja não vende usa o giro médio de uma loja da rede.
# Não entra no pedido: parado, excesso e estoque alto. Valor a preço de venda (não há custo por produto).
import math
SEM11 = 47.8
giro_rede = {int(r_.sku): r_.qtd / r_.lojas / SEM11 for r_ in med.itertuples()}
ped = []
for r_ in u.itertuples():
    if pd.isna(r_.sku): continue
    s_ = int(r_.sku); no_pl = s_ in pos
    if not no_pl and r_.acao != 'Repor já: vende e está sem estoque': continue
    if r_.acao.startswith(('Parado', 'Excesso', 'Estoque alto')) or r_.setor in FORA: continue
    gir = r_.giro if r_.giro > 0 else giro_rede.get(s_, 0)
    fr = pos[s_][3] if no_pl else 1
    granel_ = (pos[s_][0] == 'Granel') if no_pl else (r_.setor == 'Granel')
    alvo = max(2, math.ceil(gir * 3)) if granel_ else max(fr + (1 if gir >= .5 else 0), math.ceil(gir * 5))
    pedir = math.ceil(max(0, alvo - (r_.estoque or 0)))
    if pedir <= 0: continue
    pri = ('1. Repor já' if r_.acao == 'Repor já: vende e está sem estoque' else '2. Núcleo a incorporar' if r_.acao.startswith('Incorpora') else '3. Completar o planograma')
    preco_ = r_.preco if pd.notna(r_.preco) and r_.preco else pm_rede.get(s_)
    ped.append(dict(Prioridade=pri, Marca=str(r_.marca).title() if r_.marca else '', SKU=s_, Produto=str(r_.desc).title(), Setor=r_.setor, Lugar=r_.lugar or 'Parte local, 1 frente',
                    Frentes=fr, Estoque=round(float(r_.estoque or 0), 2), Giro=round(gir, 2), Alvo=alvo, Pedir=pedir, Unidade='kg' if granel_ else 'un.',
                    Valor=round(pedir * preco_, 2) if preco_ else None))
P = pd.DataFrame(ped).sort_values(['Prioridade', 'Marca', 'Setor', 'Produto'])
RM = P.groupby('Marca').agg(Produtos=('SKU', 'count'), Repor_ja=('Prioridade', lambda t: (t == '1. Repor já').sum()), Nucleo=('Prioridade', lambda t: (t == '2. Núcleo a incorporar').sum()),
                            Valor=('Valor', 'sum')).sort_values('Valor', ascending=False).reset_index()
RM.columns = ['Marca', 'Produtos', 'Repor já', 'Núcleo a incorporar', 'Pedido a preço de venda (R$)']; RM['Pedido a preço de venda (R$)'] = RM['Pedido a preço de venda (R$)'].round(0)
RP_ = P.groupby('Prioridade').agg(Produtos=('SKU', 'count'), Valor=('Valor', 'sum')).reset_index()
wb = Workbook(); ws = wb.active; ws.title = 'Leia antes'
TX = [('Divina Terra · Pinheiros · lista de pedido para o planograma', 't'),
      ('O que pedir para montar o planograma da loja, a partir do estoque de 12/11/2026 e da venda de julho a setembro de 2026.', ''), ('', ''),
      ('Prioridade', 's'),
      ('1. Repor já: vende pelo menos 1 a cada 2 semanas e está sem estoque.', ''),
      ('2. Núcleo a incorporar: produto essencial da rede que a loja ainda não tem. Já tem lugar no planograma.', ''),
      ('3. Completar o planograma: está no desenho e o estoque não cobre as frentes ou as próximas semanas de venda.', ''), ('', ''),
      ('Quanto pedir', 's'),
      ('Alvo = 4 semanas de venda até a próxima compra + 1 semana de segurança, e nunca menos que as frentes do planograma; quem vende 1 a cada 2 semanas ou mais ganha 1 unidade a mais. Pedir = alvo menos o estoque de 12/11.', ''),
      ('Granel, em kg: 3 semanas de venda, com mínimo de 2 kg por tubo. Essencial que a loja não vende: giro médio de uma loja da rede.', ''),
      ('Não entram: produtos parados, com excesso ou com estoque alto (lista na revisão do mix). Black Friday e o teste de Natal pedem compra à parte.', ''), ('', ''),
      ('Antes de enviar', 's'),
      ('Conferir o estoque do dia: a lista usa o estoque de 12/11 e a venda até setembro. Ajustar pelo pedido mínimo e pela embalagem de cada fornecedor.', ''),
      ('Valor a preço de venda médio da loja (sem custo por produto, não há valor de compra).', ''), ('', ''),
      ('Uso interno da Divina Terra e da 75 LAB.', '')]
for i, (t, k) in enumerate(TX, 1):
    q = ws.cell(i, 1, t); q.alignment = Alignment(wrap_text=True)
    if k == 't': q.font = Font(bold=True, size=16, color=TERRA)
    elif k == 's': q.font = Font(bold=True, size=12, color='7C381F')
ws.column_dimensions['A'].width = 130
ws = wb.create_sheet('Resumo'); tabela(ws, RP_.rename(columns={'Valor': 'Pedido a preço de venda (R$)'}).round(0), {'Prioridade': 30})
ws = wb.create_sheet('Por marca'); tabela(ws, RM, {'Marca': 28})
ws = wb.create_sheet('Pedido'); tabela(ws, P.rename(columns={'Giro': 'Giro por semana', 'Estoque': 'Estoque 12/11', 'Valor': 'Valor a preço de venda (R$)'}),
                                     {'Prioridade': 24, 'Marca': 20, 'Produto': 46, 'Setor': 22, 'Lugar': 28})
xp_ = R / 'kit/pinheiros-pedido.xlsx'; wb.save(xp_)

# versão para imprimir, por marca
grp = ''
ordem_m = RM.Marca.tolist()
for mca in ordem_m:
    t = P[P.Marca == mca]
    lin = ''.join(f'<tr><td>{html.escape(r_.Prioridade[3:])}</td><td>{r_.SKU}</td><td>{html.escape(r_.Produto[:56])}</td><td>{html.escape(str(r_.Setor))}</td><td>{html.escape(r_.Lugar)}</td>'
                  f'<td class="n">{br(r_.Estoque, 0 if float(r_.Estoque).is_integer() else 2)}</td><td class="n"><b>{r_.Pedir}</b> {r_.Unidade}</td><td class="n">{("R$ " + br(r_.Valor, 0)) if pd.notna(r_.Valor) else ""}</td></tr>' for r_ in t.itertuples())
    grp += f'<section class="mc"><h3>{html.escape(mca or "Sem marca")} <small>{len(t)} produtos · R$ {br(t.Valor.sum() / 1000, 1)} mil a preço de venda</small></h3><table class="tb"><thead><tr><th>Prioridade</th><th>SKU</th><th>Produto</th><th>Setor</th><th>Lugar no planograma</th><th>Estoque 12/11</th><th>Pedir</th><th>Valor</th></tr></thead><tbody>{lin}</tbody></table></section>'
cards2 = [(f'{len(P)}', 'produtos a pedir'), (f'{(P.Prioridade == "1. Repor já").sum()}', 'repor já'), (f'{(P.Prioridade == "2. Núcleo a incorporar").sum()}', 'núcleo a incorporar'),
          (f'{(P.Prioridade == "3. Completar o planograma").sum()}', 'para completar o planograma'), (f'R$ {br(P.Valor.sum() / 1000, 0)} mil', 'a preço de venda'), (f'{P.Marca.nunique()}', 'marcas')]
pg2 = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><base href="../"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Pinheiros · lista de pedido</title><link rel="icon" href="assets/logos/dt-icone-terra.svg">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,400&display=swap" rel="stylesheet">
<style>@font-face{{font-family:'General Sans';src:url('assets/fontes/GeneralSans-Variable.ttf');font-weight:200 700}}
:root{{--iogurte:#F7F5F1;--aveia:#E5DDD1;--choco:#7C381F;--terra:#461D17;--acafrao:#CA942A;--cinza:#6F5F55;--serif:'Source Serif 4',Georgia,serif;--sans:'General Sans',system-ui,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--iogurte);color:var(--terra);font:13px/1.4 var(--sans)}}main{{max-width:1100px;margin:0 auto;padding:30px 24px 60px}}
h1,h3{{font-family:var(--serif);font-weight:400;margin:0}}h1{{font-size:40px;margin:14px 0 6px}}h1 em{{color:var(--choco)}}h3{{font-size:22px;margin:22px 0 6px}}h3 small{{font-family:var(--sans);font-size:12.5px;color:var(--cinza);margin-left:6px}}
.m img{{height:22px}}.m{{display:flex;gap:12px;align-items:center}}.m img.l{{height:15px}}.lead{{font-size:15px;color:var(--cinza)}}
.cards{{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:16px 0}}.cards div{{background:var(--aveia);border-radius:10px;padding:10px 12px}}.cards b{{display:block;font-family:var(--serif);font-weight:300;font-size:24px;line-height:1.05;white-space:nowrap}}.cards div:nth-child(2){{background:var(--terra);color:var(--iogurte)}}.cards div:nth-child(2) b{{color:var(--acafrao)}}
.regra{{background:#fff;border-radius:10px;padding:10px 14px;font-size:13px}}.tb{{border-collapse:collapse;width:100%;background:#fff;border-radius:8px;overflow:hidden}}.tb th{{background:var(--aveia);text-align:left;padding:5px 8px;font-weight:600;font-size:12px}}.tb td{{padding:4px 8px;border-top:1px solid var(--aveia);vertical-align:top}}.n{{text-align:right;white-space:nowrap}}
.mc h3{{break-after:avoid}}.tb tr{{break-inside:avoid}}.tb thead{{display:table-header-group}}.f{{font-size:12px;color:var(--cinza);margin-top:20px}}</style></head><body><main>
<div class="m"><img src="assets/logos/dt-horizontal-terra.svg" alt="Divina Terra"><span>×</span><img class="l" src="assets/logos/75lab-logo-preto.svg" alt="75 LAB"></div>
<h1>Pinheiros: <em>lista de pedido</em></h1><p class="lead">O que pedir para montar o planograma da loja, por marca. Estoque de 12/11/2026 e venda de julho a setembro de 2026.</p>
<div class="cards">{''.join(f'<div><b>{v_}</b>{t_}</div>' for v_, t_ in cards2)}</div>
<p class="regra"><b>Quanto pedir:</b> 4 semanas de venda até a próxima compra mais 1 de segurança, e nunca menos que as frentes do planograma (mais 1 unidade para quem vende 1 a cada 2 semanas ou mais). Granel em kg, 3 semanas, mínimo de 2 kg. Antes de enviar, conferir o estoque do dia e o pedido mínimo de cada fornecedor. Não entram parados, excesso nem estoque alto. Black Friday e o teste de Natal pedem compra à parte.</p>
{grp}
<p class="f">Fonte: estoque de Pinheiros em 12/11/2026; relatório de vendas até 09/2026; planograma de Pinheiros. Valor a preço de venda médio da loja; sem custo por produto. Uso interno.</p>
</main></body></html>'''
(R / 'kit/pinheiros-pedido.html').write_text(pg2)
print(xp_, len(P), 'produtos'); print(RP_.round(0).to_string(index=False)); print(RM.head(12).to_string(index=False))
print('travessão' if any(t in pg2 for t in ('—', '–')) else 'sem travessão')

# ---------- dados do guia da loja (fonte/pinheiros_guia.py): móveis reais, com posição na planta ----------
def item_guia(q):
    s_ = q['sku']; r_ = u[u.sku == s_]
    es = float(r_.estoque.iloc[0]) if len(r_) else 0.0
    ac = 'novo' if s_ in set(inc) else ('tem' if es > 0 else 'pedir')
    pq = P[P.SKU == s_].Pedir; pq = int(pq.iloc[0]) if len(pq) else 0
    return dict(s=int(s_), n=q['nome'], m=q['mc'], f=int(q['f']), w=float(q['w']), a=ac, l=bool(q.get('loc')), e=round(es, 2), p=pq,
                pr=[q.get('pmin'), q.get('pmax')], b=q.get('band', ''))
moveis_g = []
for m_ in MOVEIS:
    bays = []
    for bi, bay in enumerate(m_['bays']):
        segs = []
        for si, (cat, wcm) in enumerate(bay):
            cc = cats.get(cat)
            if not cc: continue
            k = next(ix for ix, o in enumerate(cc['onde']) if o[0] == m_['id'] and o[1] == bi and o[2] == si)
            niv = [dict(n=n['n'], r=(n['rots'][k] if k < len(n['rots']) else ''), it=[item_guia(q) for q in n['mods'][k]] if k < len(n['mods']) else []) for n in cc['niveis']]
            segs.append(dict(c=cat, w=wcm, nv=niv))
        bays.append(segs)
    moveis_g.append(dict(id=m_['id'], nome=m_['nome'], grupo=m_['grupo'], x0=m_['x0'], x1=m_['x1'], y0=m_['y0'], y1=m_['y1'], alt=m_['alt'], niv=m_['niv'],
                         olha=m_['olha'], nota=m_['nota'], bays=bays))
gr_ = cats.get('Granel')
granel_g = [dict(s=t['sku'], n=t['nome'], fam=t['fam'], e=float(u[u.sku == t['sku']].estoque.iloc[0]) if len(u[u.sku == t['sku']]) else 0.0) for t in gr_['tubos']] if gr_ else []
# granel nos três móveis de hoje, na ordem das famílias: Granel P (1,25 m), Granel 18 (2,10 m, dispensers) e Granel M (0,90 m)
GRM = [('GP', 'Granel P', 1.56, 2.81, 5.94, 6.39, 12), ('G18', 'Granel 18', 2.81, 4.91, 5.94, 6.39, 18), ('GM', 'Granel M', 4.91, 5.81, 5.94, 6.39, 99)]
k0 = 0
for gid, gnome, a_, b_, c_, d_, n_ in GRM:
    moveis_g.append(dict(id=gid, nome=gnome, grupo='granel', x0=a_, x1=b_, y0=c_, y1=d_, alt=2.0, niv=0, olha='y-',
                         nota='Granel de hoje: nenhum pote sai do lugar. Placa de granel visível da porta e potinho de prova.', tubos=granel_g[k0:k0 + n_], k0=k0))
    k0 += n_
# o resto da loja, para o mapa e a vista em 3D
OBJ = [dict(t='vitrine', n='Vitrine', x0=0.0, x1=0.3, y0=0.3, y1=1.5), dict(t='porta', n='Entrada', x0=0.0, x1=0.3, y0=1.5, y1=2.6),
       dict(t='vitrine', n='Vitrine', x0=0.0, x1=0.3, y0=3.37, y1=5.37),
       dict(t='kombucha', n='Kombucha', x0=2.2, x1=2.98, y0=3.78, y1=4.73), dict(t='balcao', n='Balança e moinho', x0=3.6, x1=4.0, y0=3.82, y1=4.55),
       dict(t='balcao', n='Balcão do granel', x0=4.0, x1=6.42, y0=3.82, y1=4.55), dict(t='balcao', n='Expositor', x0=6.48, x1=7.44, y0=3.86, y1=4.36),
       dict(t='frio', n='Freezer', x0=9.0, x1=10.3, y0=0.0, y1=0.63), dict(t='caixa', n='Caixa', x0=10.63, x1=12.66, y0=1.12, y1=1.81),
       dict(t='caixa', n='', x0=12.66, x1=12.89, y0=0.91, y1=1.64), dict(t='balcao', n='Produtos', x0=12.82, x1=13.84, y0=0.0, y1=0.2),
       dict(t='mesa', n='', x0=10.57, x1=11.14, y0=3.42, y1=3.99), dict(t='mesa', n='', x0=12.0, x1=13.17, y0=3.42, y1=3.99),
       dict(t='mesa', n='', x0=10.57, x1=11.14, y0=5.18, y1=5.74), dict(t='mesa', n='', x0=12.0, x1=13.17, y0=5.18, y1=5.74),
       dict(t='cafe', n='Balcão do café', x0=10.47, x1=13.27, y0=5.84, y1=6.34), dict(t='mesames', n='Mesa do mês, em teste', x0=8.3, x1=9.5, y0=3.5, y1=4.6)]
for g, a_, b_, *_ in GON:
    for xx, lado in ((a_, 'frente'), (b_, 'fundo')):
        OBJ.append(dict(t='ponta', n=f'Ponta da gôndola {g}', x0=xx - .18 if lado == 'frente' else xx, x1=xx if lado == 'frente' else xx + .18, y0=1.56, y1=2.35))
tirar = u[u.acao.str.startswith('Parado') & (u.estoque > 0)].sort_values(['setor', 'desc'])
guardar = u[(u.acao == 'Fora do planograma: reduz ou sai aos poucos') & (u.estoque > 0)].sort_values(['setor', 'desc'])
lst = lambda t: [dict(s=(int(r_.sku) if pd.notna(r_.sku) else None), n=str(r_.desc).title(), m=str(r_.marca).title() if pd.notna(r_.marca) else '', st=str(r_.setor), e=float(r_.estoque)) for r_ in t.itertuples()]
guia = dict(moveis=moveis_g, obj=OBJ, granel=granel_g, tirar=lst(tirar), guardar=lst(guardar),
            pedido=[dict(pri=r_.Prioridade[3:], m=r_.Marca, s=int(r_.SKU), n=r_.Produto, st=r_.Setor, lg=r_.Lugar, q=int(r_.Pedir), un=r_.Unidade) for r_ in P.itertuples()],
            resumo=dict(estoque=int(len(e)), plano=int(len(pos)), novo=int(len(inc)), pedir=int(len(P)), tirar=int(len(tirar)), guardar=int(len(guardar))))
(R / 'analise/pinheiros_guia.json').write_text(json.dumps(guia, ensure_ascii=False))
print('guia:', len(moveis_g), 'móveis', sum(len(m_['bays']) for m_ in moveis_g if m_['grupo'] != 'granel'), 'módulos', 'granel', len(granel_g), 'tirar', len(tirar), 'guardar', len(guardar))
print(rs.round(0).to_string()); print('no planograma:', len(pos), '| incorpora:', len(inc))
for c_, (o_, nf_, n_) in ocupacao(M, cats).items(): print(f'  {c_:18s} {round(sum(cats[c_]["larg"])):4d} cm/nível  ocupação {o_*100:5.1f}%  fora {nf_}')
