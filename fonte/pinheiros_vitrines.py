# Calendário de vitrines de Pinheiros, mês a mês, dentro do calendário de trade da estratégia (fonte/calendario.py).
# Para cada mês: tema, datas da rede, cronograma e o que entra em cada espaço da loja (vitrine da esquerda, vitrine da direita,
# mesa do mês e ponta da entrada), escolhido pela venda real: a de Pinheiros no mesmo mês do ano-base, a média da loja e,
# para o que a loja não tem, a venda por loja da rede. Regra da estratégia: suplemento sem alegação; datas de conscientização
# são conteúdo, sem produto. Saída com venda da loja, fora do Git: analise/pinheiros_vitrines.json (lido por pinheiros_guia.py).
import json, pathlib, re, sys, datetime as DT
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import planogramas as PL, calendario as CA

R = pathlib.Path(__file__).resolve().parent.parent
LOJA = 'DT PINHEIROS'
EXIGE_FOTO = '--com-foto' in sys.argv  # 1ª rodada aceita sem foto e lista o que buscar; 2ª só com foto
MESES = CA.MESES
FORA = {'Cuidados pessoais e casa', 'Cafeteria da loja', 'Fora do planograma', 'A classificar', 'Geladeira'}

c = pd.read_pickle(R / 'analise/classificacao.pkl')
c['sku'] = pd.to_numeric(c.sku, errors='coerce'); c = c[c.sku.notna() & ~c.setor.isin(FORA)].copy(); c['sku'] = c.sku.astype(int)
c = c.sort_values('valor', ascending=False).drop_duplicates('sku').set_index('sku')
d = PL.dados_casa().copy(); d['mm'] = d.p.str[5:].astype(int); d['sku'] = d.sku.astype(int)
x = d[d.loja == LOJA]
PIN = x.groupby(['sku', 'mm']).valor.sum().to_dict()
PIN11 = x.groupby('sku').valor.sum().to_dict()
lojas_mes = d.groupby('mm').loja.nunique().to_dict()
REDE = {k: v / lojas_mes[k[1]] for k, v in d.groupby(['sku', 'mm']).valor.sum().to_dict().items()}
ATIVO = set(d[d.p.isin(sorted(d.p.unique())[-3:])].sku)

G = json.loads((R / 'analise/pinheiros_guia.json').read_text())
PLANO = {}
for m in G['moveis']:
    for b in m.get('bays', []):
        for sg in b:
            for nv in sg['nv']:
                for it in nv['it']: PLANO[it['s']] = dict(n=it['n'], m=it['m'], onde=m['nome'])
TUBOS = {t['s']: dict(n=t['n'], fam=t['fam']) for m in G['moveis'] if m.get('grupo') == 'granel' for t in m['tubos']}
FOTO = set(int(k) for k in json.loads((R / 'assets/produtos/mapa.json').read_text()))

def nome(s):
    if s in PLANO: return PLANO[s]['n'], PLANO[s]['m']
    if s in TUBOS: return TUBOS[s]['n'].strip().title().replace(' Granel', ''), 'A granel'
    r = c.loc[s]; mc = str(r.marca).title() if pd.notna(r.marca) else ''
    t = str(r.desc)
    for w in str(r.marca).split():
        t = re.sub(r'^\s*' + re.escape(w) + r'\b', '', t, flags=re.I)
    t = re.sub(r'(\d)(G|ML|KG|UN)\b', r'\1 \2', t.strip()).title()
    t = re.sub(r'\b(\d+) (G|Ml|Kg|Un)\b', lambda k: k.group(1) + ' ' + k.group(2).lower(), t)
    return t, mc

def nota(s, mm):
    viz = [((mm - 2) % 12) + 1, (mm % 12) + 1]
    pm = PIN.get((s, mm), 0); pv = sum(PIN.get((s, v), 0) for v in viz)
    rm = REDE.get((s, mm), 0); rv = sum(REDE.get((s, v), 0) for v in viz)
    if mm not in lojas_mes:  # outubro não está na base: usa os vizinhos
        pm, rm = pv / 2, rv / 2
    return pm + .5 * pv + .4 * PIN11.get(s, 0) / 11 + .6 * (rm + .5 * rv)

def regra(setor=None, prat=None, desc=None, n=3, marca=None, nao=None):
    return dict(setor=setor, prat=prat, desc=desc, n=n, marca=marca, nao=nao)

def escolhe(regras, mm, usados):
    out = []
    for g in regras:
        q = c
        if g['setor']: q = q[q.setor.str.contains(g['setor'], regex=True, na=False)]
        if g['prat']: q = q[q.prateleira.str.contains(g['prat'], regex=True, na=False)]
        if g['desc']: q = q[q.desc.str.contains(g['desc'], regex=True, na=False, flags=re.I)]
        if g['nao']: q = q[~q.desc.str.contains(g['nao'], regex=True, na=False, flags=re.I)]
        if g['marca']: q = q[q.marca.str.contains(g['marca'], regex=True, na=False, flags=re.I)]
        granel = g['setor'] == 'Granel'
        cand = []
        for s in q.index:
            if s in usados: continue
            if granel and s not in TUBOS: continue
            if not granel and s not in FOTO and EXIGE_FOTO: continue
            sazonal = REDE.get((s, mm), 0) + REDE.get((s, ((mm - 2) % 12) + 1), 0) + REDE.get((s, (mm % 12) + 1), 0) > 0
            if s not in PLANO and s not in TUBOS and s not in ATIVO and not sazonal: continue
            cand.append((nota(s, mm) * (1.25 if (s in PLANO or s in TUBOS) else 1), s))
        cand.sort(reverse=True); marcas = {}
        for v, s in cand:
            if len([1 for o in out if o['regra'] is g]) >= g['n']: break
            mc = c.loc[s].marca
            if nome(s)[0].lower()[:22] in {o['n'].lower()[:22] for o in out}: continue
            if marcas.get(mc, 0) >= 2 and not granel and not g['marca']: continue
            marcas[mc] = marcas.get(mc, 0) + 1; usados.add(s)
            n_, m_ = nome(s)
            out.append(dict(regra=g, s=int(s), n=n_, m=m_, st=c.loc[s].setor, pin=bool(s in PLANO or s in TUBOS), gr=granel,
                            onde=(PLANO.get(s) or {}).get('onde', 'Granel' if granel else ''),
                            vm=round(PIN.get((s, mm), 0) if mm in lojas_mes else (PIN.get((s, mm - 1), 0) + PIN.get((s, mm + 1), 0)) / 2), v11=round(PIN11.get(s, 0)), vr=round(REDE.get((s, mm), 0) if mm in lojas_mes else (REDE.get((s, mm - 1), 0) + REDE.get((s, mm + 1), 0)) / 2)))
    for o in out: o.pop('regra')
    return out

# Espaços da loja (planta R00): vitrine da esquerda 1,20 m (lado dos suplementos), vitrine da direita 2,00 m (lado do granel),
# mesa do mês no vão central e a ponta da gôndola 1, de frente para a porta.
ESP = {'ve': ('Vitrine da esquerda', '1,20 m, lado dos suplementos'), 'vd': ('Vitrine da direita', '2,00 m, lado do granel'),
       'mesa': ('Mesa do mês', 'vão central, entre as gôndolas e o café'), 'ponta': ('Ponta da entrada', 'gôndola 1, de frente para a porta')}
CHOC = regra('Gourmet', 'Doces e chocolates', r'CHOC|BOMBOM|CACAU|TRUFA DE', 3, nao=r'PANETONE|OVO|CACAU (EM )?PO|CACAU PO')
CAST = regra('Granel', None, r'CASTANHA|NOZES|AMENDOA|PISTACHE|MIX NUTS', 3)
FRUT = regra('Granel', None, r'DAMASCO|TAMARA|AMEIXA|UVA PASSA|CRANBERRY|MIX (DE )?FRUTAS|FRUTA', 2)
PANE = regra(None, None, r'PANETONE|CHOCOTONE', 2)
CESTA = regra(None, None, r'CAIXA PRESENTE|CESTA DIVINA|KIT PRESENTE', 1)
ELET = regra('Performance', None, r'ELETROL|HIDRA|ISOTON|HYDRO', 3)
BARRA = regra('Barras e snacks', 'Barras proteicas', None, 3)
CREA = regra('Creatina', None, None, 2)
COLA = regra('Colágeno', None, None, 2)
BEM = regra('Equilíbrio', None, None, 2)
OMEGA = regra('Ômegas', 'Ômega 3', None, 2)
VITD = regra('Vitaminas', None, r'D3|VIT(AMINA)? D\b|VITA D', 2)
VITC = regra('Vitaminas', None, r'VIT(AMINA)? C\b|VITA C|ZINCO', 1)
IMUN = regra('Imunidade', None, None, 2)
CHA = regra('Chás', None, None, 3)
CAFE = regra(None, r'Cafés funcionais|Cafés, vinhos', r'CAFE|COFFEE|CAPPU', 2)
SGB = regra('Sem Glúten', 'Biscoitos e snacks', None, 3)
GELE = regra('Gourmet', None, r'GELEIA|\bMEL\b', 1)
WHEY = regra('Proteínas', 'Whey', None, 2)
KIDS = regra('Kids', None, None, 4, nao=r'IRON|FERRO|ZINC')
LANCH = regra(None, None, r'PAPAPA|KIDS|INFANTIL|BABY', 3, nao=r'IRON|ZINC|DHA|VITAMIN')
ZERO = regra('Gourmet', 'Doces e chocolates', r'ZERO|SEM ACUCAR|S/ACUCAR|STEVIA', 3)
MASSA = regra('Gourmet', 'Massas e prontos', None, 3)
SOPA = regra(None, None, r'SOPA|CALDO|BONE BROTH', 2)
MOLHO = regra('Gourmet', 'Azeites, molhos', None, 2)
OVO = regra(None, None, r'OVO (DE )?PASCOA|OVO PASCOA', 3)
CACAU = regra(None, None, r'CACAU (EM )?PO|CACAU PO', 1)
FARI = regra(None, r'Farinhas|básicos', r'FARINHA', 2)
VIVEA = regra(None, None, None, 5, marca=r'^VIVEA')
PRE = regra('Performance', 'Antes do treino|Durante', None, 2, nao=r'ELETROL|HIDRA|ISOTON')
GRAN = regra('Granel', None, None, 7)
DRAG = regra('Granel', None, r'DRAGEAD|CARAMEL|CHOCOLAT', 2)
LONGM = regra('Longevidade', 'mulher', None, 2)

def R_(*rs, n=None):  # cópia das regras com outra quantidade
    out = []
    for r_, k in rs if isinstance(rs[0], tuple) else [(r, None) for r in rs]:
        g = dict(r_); g['n'] = k or g['n']; out.append(g)
    return out

MES = [
 dict(k='2026-12', mm=12, ano=2026, cor='#7C381F', tema='Natal e Réveillon', agora=True, alvo=(2026, 12, 25),
  dt=[('25/12', 'Natal', 'Campanha'), ('31/12', 'Réveillon', 'Campanha')], vem='Já: é o mês da reinauguração',
  sp=dict(ve=('Natal de verdade', 'O Natal mais gostoso vem da natureza', R_((PANE, 2), (CHOC, 3))),
          vd=('Ceia e presentes', 'Castanha, fruta seca e presente para a ceia', R_((CAST, 3), (FRUT, 2), (CESTA, 1))),
          mesa=('Ceia e presentes', 'Monte a ceia aqui', R_((CAST, 2), (FRUT, 2), (CHOC, 3), (GELE, 1), (PANE, 2))),
          ponta=('Natal', 'Presente que cabe na meia', R_((CHOC, 4), (DRAG, 2), (CESTA, 1))))),
 dict(k='2027-01', mm=1, sp=dict(ve=('Rotina nova', 'Ano novo, rotina nova', R_((CREA, 2), (COLA, 2), (BEM, 1))),
          vd=('Verão leve', 'Verão leve, do granel à garrafinha', R_((ELET, 3), (BARRA, 2), (regra('Granel', None, r'MIX|CHIPS|BANANA'), 2))),
          mesa=('Verão leve', 'Leve para a praia', R_((ELET, 2), (CHA, 2), (BARRA, 3), (SGB, 2), (regra('Granel', None, r'MIX|CHIPS'), 1))),
          ponta=('Rotina nova', 'Começar de novo, com rotina', R_((CREA, 3), (COLA, 2), (BEM, 2), (VIVEA, 1))))),
 dict(k='2027-02', mm=2, sp=dict(ve=('Energia para o Carnaval', 'Carnaval com energia e hidratação', R_((ELET, 3), (PRE, 2))),
          vd=('Presente a dois', "Valentine's Day: um presente a dois", R_((CHOC, 4), (CAFE, 1), (DRAG, 2))),
          mesa=('Presente a dois', 'Para dividir', R_((CHOC, 4), (DRAG, 2), (GELE, 1), (CHA, 2), (CAFE, 1))),
          ponta=('Hidratação e energia', 'Bloco, praia e treino', R_((ELET, 3), (BARRA, 3), (PRE, 2))))),
 dict(k='2027-03', mm=3, sp=dict(ve=('Mulher e Consumidor, de 1 a 15/03', 'Dia da Mulher: tempo para cuidar de si', R_((COLA, 3), (LONGM, 2))),
          vd=('Páscoa', 'Páscoa feita em casa', R_((OVO, 3), (CHOC, 2), (CACAU, 1), (CAST, 1))),
          mesa=('Páscoa, kit receita', 'Receita de Páscoa: tudo nesta mesa', R_((CACAU, 1), (FARI, 2), (CAST, 2), (OVO, 2), (CHOC, 2))),
          ponta=('Dia do Consumidor, de 12 a 15/03', 'Combos de rotina com preço de kit', R_((WHEY, 2), (CREA, 2), (OMEGA, 2), (VITD, 2))))),
 dict(k='2027-04', mm=4, sp=dict(ve=('Rotina de outono', 'Outono pede rotina', R_((OMEGA, 3), (VITD, 2))),
          vd=('Café e chá da tarde', 'Café e chá da tarde', R_((CHA, 3), (CAFE, 2), (SGB, 2))),
          mesa=('Café e chá da tarde', 'Chá, café e um biscoito', R_((CHA, 3), (CAFE, 2), (SGB, 2), (GELE, 1), (CAST, 2))),
          ponta=('Rotina de outono', 'A rotina do frio que começa', R_((OMEGA, 3), (VITD, 2), (VITC, 1), (IMUN, 2))))),
 dict(k='2027-05', mm=5, sp=dict(ve=('16 anos da Divina Terra', '16 anos de Divina Terra', R_((VIVEA, 5), (WHEY, 1), (OMEGA, 1))),
          vd=('Presentes para as mães', 'Para a mãe que cuida de todo mundo', R_((COLA, 2), (BEM, 2), (CHOC, 2), (CESTA, 1))),
          mesa=('Presentes para as mães', 'Monte o presente da mãe', R_((COLA, 2), (BEM, 2), (CHOC, 2), (GELE, 1), (CHA, 2), (CESTA, 1))),
          ponta=('16 anos da Divina Terra', 'Oferta de aniversário no granel', R_((GRAN, 4), (VIVEA, 3), (CREA, 2), (COLA, 2))))),
 dict(k='2027-06', mm=6, sp=dict(ve=('Inverno', 'Inverno com a rotina em dia', R_((OMEGA, 2), (VITD, 2), (IMUN, 2))),
          vd=('Dia dos Namorados', 'Namorados: um presente a dois', R_((CHOC, 4), (CAFE, 1), (DRAG, 2))),
          mesa=('Presente a dois', 'Para dividir no frio', R_((CHOC, 4), (CHA, 2), (CAFE, 1), (DRAG, 2), (GELE, 1))),
          ponta=('Inverno', 'Chá quente e rotina', R_((CHA, 4), (IMUN, 2), (SOPA, 2))))),
 dict(k='2027-07', mm=7, sp=dict(ve=('Férias de julho', 'Férias com lancheira boa', R_((KIDS, 3), (BARRA, 2))),
          vd=('Noite fria em casa', 'Noite fria em casa', R_((MASSA, 2), (SOPA, 2), (MOLHO, 2), (CHA, 1))),
          mesa=('Noite fria em casa', 'O jantar do frio', R_((MASSA, 3), (SOPA, 2), (MOLHO, 2), (CHA, 2), (regra('Sem Glúten', 'Pães, massas', None, 2), None))),
          ponta=('Lancheira', 'Lancheira das férias', R_((BARRA, 3), (SGB, 3), (LANCH, 2))))),
 dict(k='2027-08', mm=8, sp=dict(ve=('Dia dos Pais', 'Para o pai que treina', R_((WHEY, 2), (CREA, 2), (PRE, 1))),
          vd=('Café e tábua', 'Café e tábua para o Dia dos Pais', R_((CAFE, 3), (CAST, 2), (MOLHO, 2))),
          mesa=('Café e tábua', 'Café, castanha e um bom papo', R_((CAFE, 3), (CAST, 3), (MOLHO, 2), (CHOC, 2))),
          ponta=('Presente para o pai', 'Presente para o pai', R_((WHEY, 3), (CREA, 2), (CAFE, 2), (BARRA, 1))))),
 dict(k='2027-09', mm=9, sp=dict(ve=('Semana do Cliente', 'Semana do Cliente: obrigado por voltar', R_((WHEY, 2), (OMEGA, 2), (CREA, 1))),
          vd=('Granel da semana', 'O granel da Semana do Cliente', R_((GRAN, 7))),
          mesa=('Lanche leve', 'Lanche leve para a semana', R_((BARRA, 3), (SGB, 3), (CAST, 2), (CHA, 2))),
          ponta=('Semana do Cliente', 'Preço de cliente', R_((CAST, 2), (FRUT, 2), (WHEY, 2), (OMEGA, 2))))),
 dict(k='2027-10', mm=10, sp=dict(ve=('Dia das Crianças', 'Dia das Crianças', R_((KIDS, 5))),
          vd=('Lancheira', 'Lancheira de verdade', R_((LANCH, 2), (SGB, 3), (BARRA, 2))),
          mesa=('Lancheira', 'Lanche que criança gosta', R_((LANCH, 2), (SGB, 3), (BARRA, 2), (ZERO, 3))),
          ponta=('Dia das Crianças', 'Doce sem açúcar', R_((ZERO, 4), (KIDS, 2), (DRAG, 2))))),
 dict(k='2027-11', mm=11, sp=dict(ve=('Black Friday', 'Black Friday Divina Terra', R_((WHEY, 2), (CREA, 2), (OMEGA, 1))),
          vd=('Black Friday', 'Combos de rotina com preço de kit', R_((VITD, 1), (COLA, 2), (PRE, 2), (CAST, 2))),
          mesa=('Prévia de Natal', 'Prévia de Natal', R_((PANE, 2), (CHOC, 3), (CAST, 3), (CESTA, 2))),
          ponta=('Black Friday', 'Combos da Black Friday', R_((WHEY, 2), (CREA, 2), (OMEGA, 2), (VITD, 2))))),
 dict(k='2027-12', mm=12, cor='#7C381F', sp=dict(ve=('Natal', 'O Natal mais gostoso vem da natureza', R_((PANE, 2), (CHOC, 3))),
          vd=('Ceia e Réveillon', 'Ceia, presente e Réveillon', R_((CAST, 3), (FRUT, 2), (CESTA, 1))),
          mesa=('Ceia e presentes', 'Monte a ceia aqui', R_((CAST, 2), (FRUT, 2), (CHOC, 3), (GELE, 1), (PANE, 2))),
          ponta=('Natal', 'Presente que cabe na meia', R_((CHOC, 4), (DRAG, 2), (CESTA, 1))))),
]
COR = {1: '#596D49', 2: '#CA942A', 3: '#6E3B2A', 4: '#8C6A55', 5: '#C0673C', 6: '#461D17', 7: '#6B7E4E', 8: '#7C381F', 9: '#AC834C', 10: '#D08752', 11: '#1E1512', 12: '#7C381F'}
NOTAS = {3: 'No dia 16/03 a vitrine da esquerda vira Páscoa também, até o dia 28.', 9: 'Setembro Amarelo é conteúdo: nenhum produto vinculado.',
         10: 'Outubro Rosa é conteúdo: nenhum produto vinculado.', 11: 'Vitrine preta, preço grande e faixa preta nas gôndolas que participam. Novembro Azul é conteúdo, sem produto.',
         5: 'Os 16 anos dividem a loja com o Dia das Mães: aniversário à esquerda, mães à direita.', 12: 'Suplemento recua no mês: garantir reposição, sem verba extra.',
         1: 'Começo do piloto em 18/01: a vitrine ajuda a contar que a loja mudou.', 4: 'Mês sem campanha da rede: depois da Páscoa, o que sobra sai por regra, sem queima.'}

CURTO = {12: 'Natal', 1: 'Rotina nova e verão', 2: 'Carnaval', 3: 'Mulher e Páscoa', 4: 'Outono', 5: '16 anos e Mães', 6: 'Inverno e Namorados',
         7: 'Férias', 8: 'Dia dos Pais', 9: 'Semana do Cliente', 10: 'Crianças', 11: 'Black Friday'}
TITULO = {4: 'Outono, mês sem campanha da rede', 8: 'Dia dos Pais e do Nutricionista', 5: '16 anos da Divina Terra e Dia das Mães'}
def br(dt): return dt.strftime('%d/%m')
def cron(i, ano):
    a = i.get('alvo')
    if not a:
        cal = next(x for x in CA.CAL if x['m'] == i['mm'])
        if cal['alvo']: a = (ano, *cal['alvo'])
    if a:
        dd = DT.date(*a)
        return [('Plano e pedido fechados', br(dd - DT.timedelta(45))), ('Material na loja', br(dd - DT.timedelta(15))),
                ('Vitrine montada', br(max(DT.date(dd.year, dd.month, 1) - DT.timedelta(1), dd - DT.timedelta(14)))), ('Desmontar', br(dd + DT.timedelta(1)))]
    ini = DT.date(ano, i['mm'], 1); fim = (ini.replace(day=28) + DT.timedelta(days=4)).replace(day=1) - DT.timedelta(1)
    return [('Plano e pedido fechados', br(ini - DT.timedelta(45))), ('Material na loja', br(ini - DT.timedelta(7))),
            ('Vitrine montada', br(ini - DT.timedelta(1))), ('Desmontar', br(fim))]

saida = []
for i in MES:
    mm = i['mm']; ano = i.get('ano', 2027); cal = next(x for x in CA.CAL if x['m'] == mm)
    dt = i.get('dt') or [(a, n, nv) for a, n, p, nv in cal['dt']]
    usados = set(); sp = []
    for k in ('ve', 'vd', 'mesa', 'ponta'):
        tema, promessa, regras = i['sp'][k]
        sp.append(dict(id=k, nome=ESP[k][0], onde=ESP[k][1], tema=tema, promessa=promessa, it=escolhe(regras, mm, usados)))
    tema = i.get('tema') or TITULO.get(mm) or cal['foco']
    saida.append(dict(k=i['k'], mm=mm, curto=CURTO[mm], ano=ano, mes=MESES[mm - 1], tema=tema, cor=i.get('cor') or COR[mm], agora=bool(i.get('agora')),
                      dt=[dict(d=a, n=n, nv=nv) for a, n, nv in dt], cron=cron(i, ano), sp=sp, nota=NOTAS.get(mm, ''),
                      peso=cal['peso'], C=cal['C'], A=cal['A'], E=cal['E']))
    if i.get('agora'):  # o prazo de plano já passou: pedido o quanto antes
        saida[-1]['cron'][0] = ('Pedido para a rede, o quanto antes', '28/11')
    if i['k'] == '2027-12':
        saida[-1]['nota'] = 'Repete a estrutura do Natal de 2026. Em outubro, refazer a escolha com a venda do Natal de 2026.'
(R / 'analise/pinheiros_vitrines.json').write_text(json.dumps(saida, ensure_ascii=False))
falta = sorted({it['s'] for m in saida for s_ in m['sp'] for it in s_['it'] if not it['gr'] and it['s'] not in FOTO})
(R / 'analise/vitrines_fotos.json').write_text(json.dumps([dict(sku=str(s), n=nome(s)[0], m=nome(s)[1]) for s in falta], ensure_ascii=False))
for m in saida:
    print(m['k'], m['tema'], '|', ' / '.join(f"{s_['id']}:{len(s_['it'])}" for s_ in m['sp']), '| fora da loja:', sum(1 for s_ in m['sp'] for it in s_['it'] if not it['pin']))
print('itens:', sum(len(s_['it']) for m in saida for s_ in m['sp']), 'sem foto:', len(falta))
