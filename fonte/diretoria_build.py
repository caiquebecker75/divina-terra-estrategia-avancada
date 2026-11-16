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
ORDEM = [('n', 'Capa'), ('n', 'Em que ponto estamos'), ('e', 'O desafio: como incorporar o empório'),
         ('n', 'Hoje a rede depende de um motor'), ('n', 'O que muda em cada região'),
         ('e', 'Nossa resposta: o empório para quem quer se cuidar'), ('n', 'Uma posição que ninguém ocupa'),
         ('n', 'Três motivos para entrar na loja'), ('n', 'Cinco razões para este caminho'),
         ('n', 'O mercado abre portas para quem tem curadoria'), ('n', 'Vender mais para quem já entra'), ('e', 'Vila Madalena mostra o caminho'),
         ('n', 'A experiência na loja'), ('e', 'A jornada da cliente na loja'), ('e', 'A loja organizada pelos três motivos'),
         ('e', 'Pinheiros, sem obra'), ('n', 'Mini trade book'), ('n', 'Calendário promocional 2027'),
         ('n', 'O potencial: real, hipótese e meta'), ('e', 'O piloto: uma loja, doze semanas'),
         ('n', 'Quem faz o quê nos próximos 90 dias'), ('e', 'Da decisão de hoje à rede inteira'), ('e', 'O que precisamos decidir')]
faltam = [t for f, t in ORDEM if t not in (NV if f == 'n' else EX)]
assert not faltam, faltam

CAPS = [('Onde estamos', ['Em que ponto estamos']),
        ('O problema', ['O desafio: como incorporar o empório', 'Hoje a rede depende de um motor', 'O que muda em cada região']),
        ('O rumo', ['Nossa resposta: o empório para quem quer se cuidar', 'Uma posição que ninguém ocupa', 'Três motivos para entrar na loja']),
        ('Por que funciona', ['Cinco razões para este caminho', 'O mercado abre portas para quem tem curadoria', 'Vender mais para quem já entra', 'Vila Madalena mostra o caminho']),
        ('Na loja', ['A experiência na loja', 'A jornada da cliente na loja', 'A loja organizada pelos três motivos', 'Pinheiros, sem obra', 'Mini trade book', 'Calendário promocional 2027']),
        ('O que decidir', ['O potencial: real, hipótese e meta', 'O piloto: uma loja, doze semanas', 'Quem faz o quê nos próximos 90 dias', 'Da decisão de hoje à rede inteira', 'O que precisamos decidir'])]
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

telas = '\n'.join(re.sub(r'(<section class="tela [^"]*" data-titulo="([^"]*)"[^>]*>)', lambda m: m.group(1) + fio(m.group(2)), (NV if f == 'n' else EX)[t], count=1) for f, t in ORDEM)
for k, ativos in (('far', ['far', 'hoje']), ('mer', ['mer', 'hoje']), ('net', ['net', 'hoje']), ('dest', ['hoje', 'dest'])):
    telas = telas.replace('{{curva_%s}}' % k, graficos.canvas(ativos))
telas = telas.replace('{{cal1p}}', cal1p())
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
