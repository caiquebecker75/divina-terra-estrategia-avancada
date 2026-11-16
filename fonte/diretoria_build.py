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
         ('e', 'Hoje a rede depende de um motor'), ('e', 'O que muda em cada região'),
         ('e', 'Nossa resposta: o empório para quem quer se cuidar'), ('n', 'Uma posição que ninguém ocupa'),
         ('e', 'Três motivos para entrar na loja'), ('n', 'Cinco razões para este caminho'), ('e', 'Vila Madalena mostra o caminho'),
         ('n', 'A experiência na loja'), ('e', 'A jornada da cliente na loja'), ('e', 'A loja organizada pelos três motivos'),
         ('e', 'Pinheiros, sem obra'), ('n', 'Mini trade book'), ('n', 'Calendário promocional 2027'),
         ('e', 'O potencial: real, hipótese e meta'), ('e', 'O piloto: uma loja, doze semanas'),
         ('e', 'Da decisão de hoje à rede inteira'), ('e', 'O que precisamos decidir')]
faltam = [t for f, t in ORDEM if t not in (NV if f == 'n' else EX)]
assert not faltam, faltam

def cal1p():
    cls = {'Campanha': 'c', 'Apoio ao trade': 'a', 'Conteúdo': 't', 'Em aberto': 'e'}
    out = ''
    for i in CAL.CAL:
        dts = ''.join(f'<span class="{cls[nv]}"><b>{html.escape(n)}</b>{html.escape(a) if "/" in a else ""} <small>{nv}</small></span>'
                      for a, n, p, nv in sorted(i['dt'], key=lambda x: (x[3] != 'Campanha', x[0])))
        pk = ' pk' if i['m'] in (3, 5, 9, 11) else ''
        out += (f'<div class="{pk.strip()}"><h4>{CAL.MESES[i["m"] - 1][:3]}</h4><div class="dt">{dts or "<span class=sem>Sem campanha da rede: mês de execução</span>"}</div>'
                f'<div class="fo"><b>Ponta</b>{html.escape(i["ponta"])}</div></div>')
    return f'<div class="cal">{out}</div>'

telas = '\n'.join((NV if f == 'n' else EX)[t] for f, t in ORDEM)
telas = telas.replace('{{curva}}', graficos.canvas(['far', 'mer', 'net', 'hoje', 'dest'])).replace('{{cal1p}}', cal1p())
v = (R / 'versao.txt').read_text().strip()
sh = (R / 'fonte/exec/shell.html').read_text()
sh = re.sub(r'<title>.*?</title>', '<title>Divina Terra × 75 LAB · Visão estratégica para a diretoria</title>', sh)
sh = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Visão estratégica da Divina Navegação para a diretoria da Divina Terra: ponto em que estamos, posição, razões, experiência em loja, mini trade book, calendário promocional, potencial e decisões.">', sh)
sh = sh.replace('<link rel="stylesheet" href="assets/exec.css?v=__VERSAO__">', '<link rel="stylesheet" href="assets/exec.css?v=__VERSAO__"><link rel="stylesheet" href="assets/dir.css?v=__VERSAO__">')
sh = sh.replace('href="divina-terra-apresentacao.pdf"', 'href="divina-terra-diretoria.pdf"')
s = sh.replace('__TELAS__', telas).replace('__VERSAO__', v)
(R / 'diretoria.html').write_text(s)
(R / 'assets/dir.css').write_text((R / 'fonte/diretoria/dir.css').read_text())
bad = [x for x in ('—', '–') if x in s + (R / 'fonte/diretoria/dir.css').read_text()]
print('telas', s.count('class="tela '), 'TRAVESSAO!' if bad else 'sem travessao')
