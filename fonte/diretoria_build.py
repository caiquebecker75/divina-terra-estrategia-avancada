#!/usr/bin/env python3
# Monta a visão estratégica para a diretoria (diretoria.html): slides próprios (fonte/diretoria/novas.html)
# + slides da apresentação executiva (fonte/exec/telas.html), na ordem abaixo. Rodar depois de exec_build.py.
import pathlib, re, sys, html
R = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / 'fonte'))
import graficos, calendario as CAL

def secoes(t):
    return {m.group(2): m.group(0) for m in re.finditer(r'<section class="tela ([^"]*)" data-titulo="([^"]*)".*?</section>', t, flags=re.S)}
EX = secoes((R / 'fonte/exec/telas.html').read_text())
NV = secoes((R / 'fonte/diretoria/novas.html').read_text())
# Ordem da reunião de alinhamento de 16/11/2026: abre pelo problema (motor e regiões), passa pela posição
# competitiva e pelos três motivos, e só então coloca a pergunta do empório e a resposta. Saíram Vila Madalena
# (a evidência já está nas razões), o comparativo do piloto e o quem faz o quê: a diretoria olha o macro.
ORDEM = [('n', 'Capa'), ('n', 'Em que ponto estamos'),
         ('n', 'Hoje a rede depende de um motor'), ('n', 'O que muda em cada região'),
         ('n', 'Uma posição que ninguém ocupa'), ('n', 'Três motivos para entrar na loja'),
         ('e', 'O desafio: como incorporar o empório'), ('e', 'Nossa resposta: o empório para quem quer se cuidar'),
         ('n', 'Cinco razões para este caminho'), ('n', 'Vender mais para quem já entra'), ('n', 'O mercado abre portas para quem tem curadoria'),
         ('n', 'A experiência na loja'), ('e', 'A jornada da cliente na loja'), ('e', 'A loja organizada pelos três motivos'),
         ('e', 'Pinheiros, sem obra'), ('n', 'Mini trade book'), ('n', 'Quanto vale cada espaço'), ('n', 'Calendário promocional 2027'),
         ('n', 'O potencial: real, hipótese e meta'), ('e', 'Da decisão de hoje à rede inteira'), ('e', 'O que precisamos decidir')]
faltam = [t for f, t in ORDEM if t not in (NV if f == 'n' else EX)]
assert not faltam, faltam

# Slides da executiva que mudam só para a diretoria: Pinheiros vira o piloto assistido do planograma e o
# Gourmet ganha piloto próprio em Alphaville, na renovação da loja; a cliente entra por qualquer item.
AJUSTE = {
    'A jornada da cliente na loja': [
        ('Ela entra atrás de um ômega.', 'Ela entra atrás de um item, um ômega, uma creatina.'),
        ('<h2>Ela entra pelo ômega e sai <em>com mais do que veio buscar</em></h2>',
         '<h2>Ela entra por um item e sai <em>com mais do que veio buscar</em></h2>')],
    'Pinheiros, sem obra': [
        ('data-fala="Este é o exemplo concreto. À esquerda, Pinheiros na visita de outubro. À direita, a mesma proposta aplicada. Mesmos móveis. O que muda é a história que a loja conta."',
         'data-fala="Este é o exemplo concreto e o piloto que propomos aprovar: o planograma assistido em Pinheiros. Mesmos móveis, outra história. O Gourmet ganha um piloto próprio em Alphaville, que está em renovação."'),
        ('<h2>Em Pinheiros, sem obra: <em>mesmos móveis, outra história</em></h2>',
         '<h2>Pinheiros, sem obra: <em>o piloto assistido do planograma</em></h2>'),
        ('<p><b>Farinhas viram Gourmet</b>: 3 módulos ao lado da mesa</p>',
         '<p><b>Planograma assistido</b>: a 75 LAB acompanha a montagem e lê os números nas semanas 6 e 12</p>'),
        ('</p></div>\n  <p class="fonte">Fonte: visita a Pinheiros',
         '</p></div>\n  <p class="alpha"><b>E o Gourmet?</b> Ganha piloto próprio em Alphaville, que está em renovação e pode reinvestir a taxa em móveis e num canto Gourmet. A 75 LAB leva o Gourmet para a exposição e sugere o mix; a compra fica com a rede.</p>\n  <p class="fonte">Fonte: visita a Pinheiros'),
        ('Ainda não é o projeto executivo.', 'Ainda não é o projeto executivo. Piloto de Alphaville: reunião de alinhamento de 16/11/2026.')],
    'Da decisão de hoje à rede inteira': [
        ('Piloto em janeiro.', 'Pilotos em janeiro, Pinheiros e Alphaville.'),
        ('<span>Posição, piloto, comitê e gôndola padrão</span>', '<span>Posição, pilotos, comitê e gôndola padrão</span>'),
        ('<b>Piloto começa</b><span>Pinheiros e Moinhos</span>',
         '<b>Pilotos começam</b><span>Pinheiros, planograma assistido; Alphaville, Gourmet na renovação</span>'),
        ('<span>Uma de cada tipo, com Alphaville</span>', '<span>Uma de cada tipo</span>')],
    'O que precisamos decidir': [
        ('<li>Piloto em Pinheiros?</li>', '<li>Piloto assistido do planograma em Pinheiros?</li><li>Piloto do Gourmet em Alphaville, na renovação?</li>')],
}
for t, pares in AJUSTE.items():
    for a, b in pares:
        assert EX[t].count(a) == 1, (t, a[:70])
        EX[t] = EX[t].replace(a, b)

CAPS = [('Onde estamos', ['Em que ponto estamos']),
        ('O problema', ['Hoje a rede depende de um motor', 'O que muda em cada região']),
        ('O rumo', ['Uma posição que ninguém ocupa', 'Três motivos para entrar na loja', 'O desafio: como incorporar o empório', 'Nossa resposta: o empório para quem quer se cuidar']),
        ('Por que funciona', ['Cinco razões para este caminho', 'Vender mais para quem já entra', 'O mercado abre portas para quem tem curadoria']),
        ('Na loja', ['A experiência na loja', 'A jornada da cliente na loja', 'A loja organizada pelos três motivos', 'Pinheiros, sem obra', 'Mini trade book', 'Quanto vale cada espaço', 'Calendário promocional 2027']),
        ('O que decidir', ['O potencial: real, hipótese e meta', 'Da decisão de hoje à rede inteira', 'O que precisamos decidir'])]
assert sorted(t for _, ts in CAPS for t in ts) == sorted(t for _, t in ORDEM[1:]), 'CAPS fora da ORDEM'
TIT = [t for f, t in ORDEM]
def fio(titulo):
    "Fio da história no topo: em que parte da conversa estamos. Cada parte leva ao primeiro slide dela."
    if titulo == 'Capa': return ''
    out = ''
    for k, (nome, ts) in enumerate(CAPS, 1):
        on = ' on' if titulo in ts else ''
        out += f'<a class="fp{on}" href="#{TIT.index(ts[0]) + 1}"><i>{k}</i>{nome}</a>'
    return f'<nav class="fio">{out}</nav>'

def cal1p():
    cls = {'Campanha': 'c', 'Apoio ao trade': 'a', 'Conteúdo': 't', 'Em aberto': 'e'}
    grade = ''; det = ''
    for i in CAL.CAL:
        dts = ''.join(f'<span class="{cls[nv]}"><b>{html.escape(n)}</b>{html.escape(a) if "/" in a else ""} <small>{nv}</small></span>'
                      for a, n, p, nv in sorted(i['dt'], key=lambda x: (x[3] != 'Campanha', x[0])))
        pk = 'pk' if i['m'] in (3, 5, 9, 11) else ''
        grade += (f'<button class="mes {pk}" data-m="{i["m"]}"><h4>{CAL.MESES[i["m"] - 1][:3]}</h4><div class="dt">{dts or "<span class=sem>Sem campanha da rede: mês de execução</span>"}</div>'
                  f'<div class="fo"><b>Ponta</b>{html.escape(i["ponta"])}</div></button>')
        pz = CAL.prazos(i)
        prz = (f'<div><b>Prazos</b>Plano e pedido até {pz[0]}; material na loja até {pz[1]}; desmontar em {pz[2]}.</div>' if pz else '<div><b>Prazos</b>Tema do mês inteiro: material na loja até o dia 1º.</div>')
        det += (f'<div class="dm" data-m="{i["m"]}"><h5>{CAL.MESES[i["m"] - 1]} · {html.escape(i["foco"])}</h5>'
                f'<div><b class="cu">Cuidar</b>{html.escape(i["C"])}</div><div><b class="ab">Abastecer</b>{html.escape(i["A"])}</div><div><b class="ce">Celebrar</b>{html.escape(i["E"])}</div>'
                f'<div><b>Ponta e mesa</b>{html.escape(i["ponta"])} · {html.escape(i["mesa"])}</div><div><b>Encarte</b>{html.escape(i["enc"])}</div>{prz}</div>')
    camp = ('<div class="dm on" data-m="0"><h5>Campanhas com plano próprio · clique em um mês para ver o plano dele</h5>'
            '<div><b class="ce">15/03 Dia do Consumidor</b>Combos de rotina e progressivo no granel</div><div><b class="ce">06/05 16 anos</b>Vivea e 16 líderes com 16%, emendando com Mães</div>'
            '<div><b class="ce">15/09 Dia do Cliente</b>Preço de cliente e oferta de granel</div><div><b class="ce">26/11 Black Friday</b>Esquenta, combos e verba negociada com as marcas</div></div>')
    return f'<div class="cal">{grade}</div><div class="detcal">{camp}{det}</div>'

def espacos():
    "Quanto vale cada espaço: os pontos que a marca pode pagar, com quantidade, tempo e custo do book (novas.PONTOS)."
    import json, pandas as pd, novas as N
    r = json.load(open(R / 'analise/planogramas.json'))
    q = {T: N.quant(r, T) for T in 'PMG'}
    vd = pd.read_pickle(R / 'analise/vendas5.pkl'); L = pd.read_pickle(R / 'analise/lojas_cluster.pkl')
    tam = {lj: (L.tam.get(lj, '?')) for lj in vd.loja.unique()}
    nl = {T: sum(1 for v in tam.values() if (v.replace('GG', 'G') if v in ('P', 'M', 'G', 'GG') else 'M') == T) for T in 'PMG'}
    assert sum(nl.values()) == 71, nl
    br = N.br
    def mil(v): return br(round(v / 1000))
    def cerca(n): return br(round(n, -2)) if n >= 1000 else br(round(n, -1)) if n >= 60 else br(n)
    ESP = [  # (ponto no book, nome curto, quanto dura para a marca, o que a marca leva, a marca paga a peça?)
        ('Kit de ponta de gôndola', 'Ponta de gôndola', '30 a 45 dias, por ação', 'o lugar mais visto do corredor, com o tema do mês.', True),
        ('Mesa do mês', 'Mesa do mês', 'A data: Natal, Mães, Pais', 'a data inteira no centro da loja, só onde há vão livre.', False),
        ('Testeira de módulo', 'Testeira de módulo', 'Por período', 'o próprio nome no alto do módulo, lido a 8 m.', True),
        ('Display de caixa', 'Display de caixa', 'Conteúdo mensal', 'a última compra, no balcão: sachê, barra, presente pequeno.', True),
        ('Stopper de destaque', 'Stopper de destaque', 'Até 60 dias', 'o destaque na prateleira, até um por módulo.', True),
        ('Comunicação do granel', 'Granel por família', 'Fixa, por família', 'uma família do granel com o nome dela: placa, etiqueta e prova.', True)]
    P = {nm: (a, b, fq, ico) for nm, ds, a, b, fq, ico, v in N.PONTOS}
    simb = ''.join(re.search(r'<symbol id="%s".*?</symbol>' % P[nm][3], (R / 'book.html').read_text(), flags=re.S).group(0) for nm, *_ in ESP)
    cards = ''
    def faixa(a, b): return f'R$ {br(a / 1000, 1)} a {br(b / 1000, 1)}<small>mil por peça</small>' if b >= 1000 else f'R$ {br(a)} a {br(b)}<small>por peça</small>'
    for k, (nm, curto, dura, leva, paga) in enumerate(ESP):
        a, b, fq, ico = P[nm]
        pl = {T: fq(q[T]) for T in 'PMG'}; rede = sum(pl[T] * nl[T] for T in 'PMG')
        por = ' · '.join(f'{T} {pl[T] if pl[T] else "sem"}' for T in 'PMG')
        dx = (f'<b>{curto} na rede inteira:</b> cerca de {cerca(rede)}. '
              + (f'Só a peça: R$ {mil(rede * a)} a {mil(rede * b)} mil, paga pela marca.' if paga else 'A mesa é da loja; a marca paga a comunicação da data.')
              + f'<span>A marca leva {leva}</span>')
        cards += (f'<div class="es{" on" if k == 0 else ""}" data-det="x"><svg class="ico"><use href="#{ico}"/></svg><h3>{curto}</h3>'
                  f'<div class="rs">{faixa(a, b)}</div>'
                  f'<dl><div><dt>Quanto dura</dt><dd>{dura}</dd></div><div><dt>Por loja</dt><dd>{por}</dd></div>'
                  f'<div><dt>Na rede</dt><dd><b>{cerca(rede)}</b></dd></div></dl><div class="dx">{dx}</div></div>')
        if k == 0: d0 = dx
    regra = ('<div class="regra"><p><i>1</i>A marca paga a peça e o período; a rede dá volume, dado de venda e execução auditada.</p>'
             '<p><i>2</i>Espaço pago não muda a regra: a marca fica no setor certo. A verba compra visibilidade.</p>'
             '<p><i>3</i>Vai junto com o planograma: cada loja sabe quantos espaços tem.</p></div>')
    return (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{simb}</svg>'
            f'<div class="seis" data-det-alvo="detEsp">{cards}</div><p class="det" id="detEsp">{d0}</p>{regra}')

telas = '\n'.join(re.sub(r'(<section class="tela [^"]*" data-titulo="([^"]*)"[^>]*>)', lambda m: m.group(1) + fio(m.group(2)), (NV if f == 'n' else EX)[t], count=1) for f, t in ORDEM)
for k, ativos in (('far', ['far', 'hoje']), ('mer', ['mer', 'hoje']), ('net', ['net', 'hoje']), ('dest', ['hoje', 'dest'])):
    telas = telas.replace('{{curva_%s}}' % k, graficos.canvas(ativos))
telas = telas.replace('{{cal1p}}', cal1p()).replace('{{espacos}}', espacos())
v = (R / 'versao.txt').read_text().strip()
sh = (R / 'fonte/exec/shell.html').read_text()
sh = re.sub(r'<title>.*?</title>', '<title>Divina Terra × 75 LAB · Visão estratégica para a diretoria</title>', sh)
sh = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Visão estratégica da Divina Navegação para a diretoria da Divina Terra: ponto em que estamos, posição, razões, experiência em loja, mini trade book, calendário promocional, potencial e decisões.">', sh)
sh = sh.replace('<link rel="stylesheet" href="assets/exec.css?v=__VERSAO__">', '<link rel="stylesheet" href="assets/exec.css?v=__VERSAO__"><link rel="stylesheet" href="assets/dir.css?v=__VERSAO__">')
sh = sh.replace('href="divina-terra-apresentacao.pdf"', 'href="divina-terra-diretoria.pdf"')
sh = sh.replace('<script src="assets/exec.js?v=__VERSAO__"></script>', '<script src="assets/exec.js?v=__VERSAO__"></script><script src="assets/dir.js?v=__VERSAO__"></script>')
s = sh.replace('__TELAS__', telas).replace('__VERSAO__', v)
(R / 'diretoria.html').write_text(s)
(R / 'assets/dir.css').write_text((R / 'fonte/diretoria/dir.css').read_text())
(R / 'assets/dir.js').write_text((R / 'fonte/diretoria/dir.js').read_text())
bad = [x for x in ('—', '–') if x in s + (R / 'fonte/diretoria/dir.css').read_text()]
print('telas', s.count('class="tela '), 'TRAVESSAO!' if bad else 'sem travessao')
