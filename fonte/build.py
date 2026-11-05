#!/usr/bin/env python3
# Monta book.html e assets/deck.* a partir de src/. Rodar da raiz: python3 fonte/build.py
import re,pathlib,time,json,sys
R=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R/'fonte'))
import graficos,calendario
v=time.strftime('%Y%m%d%H%M%S')
telas=''
css=(R/'src/deck.css').read_text()
for f in sorted((R/'src').glob('c*.html')):
    t=f.read_text()
    for m in re.findall(r'<style>(.*?)</style>',t,flags=re.S): css+='\n'+m
    telas+=re.sub(r'<style>.*?</style>','',t,flags=re.S)
telas=graficos.aplicar(telas)
import novas,plano_html,aulas
telas=aulas.aplicar(telas);css+=aulas.CSS
telas=novas.aplicar(telas);css+=plano_html.CSS
KW=[('preço|teto|desconto|oferta','tag'),('venda|receita|resultado|número|meta','grafico'),('conversa|atend|fal[ao]|frase','conversa'),('treino|manual|guia|estudo|aprend','livro'),('quem|time|equipe|franque|comitê|pessoa|cliente','pessoas'),('calend|data|mês|prazo|quando|semana|trimestre','calendario'),('lugar|espaço|módulo|onde','local'),('regra|padrão|obrig|critério','regras'),('marca|fornecedor|indústria|negoci|parceir','handshake'),('risco|cuidado|não copiar|não pode|fora','aviso'),('granel|semente|castanha','trigo'),('empório|presente|ocasião|celebrar','presente'),('produto|sortimento|núcleo|lista','pacote'),('teste|piloto|hipótese|experimento','teste'),('objetivo|ganhar|o que queremos|direção','alvo'),('peça|placa|comunic|sinal','placa'),('resolve|sucesso|ganho|decisão','check')]
def _ic(tx):
    s=re.sub(r'<[^>]+>','',tx).lower()
    for pad,i in KW:
        if re.search(pad,s): return f'<svg class="ico tic"><use href="#i-{i}"/></svg>'
    return ''
telas=re.sub(r'(<(?:div|span) class="t"[^>]*>)(?!<svg)([^<]{3,60})',lambda m:m.group(1)+_ic(m.group(2))+m.group(2),telas)
telas=re.sub(r'(<h4[^>]*>)(?!<svg|<span)([^<]{3,50})(</h4>)',lambda m:m.group(1)+_ic(m.group(2))+m.group(2)+m.group(3),telas)
telas=re.sub(r'(<(?:div|span)[^>]*class=")((?:[^"]*\s)?ax(?:\s[^"]*)?")',lambda m:m.group(1)+'lp-luz '+m.group(2),telas)
telas=telas.replace('<b>Na rede</b>','<b><svg class="ico"><use href="#i-loja"/></svg>Na rede</b>').replace('<b>No mercado</b>','<b><svg class="ico"><use href="#i-mercado"/></svg>No mercado</b>').replace('<b>Na teoria</b>','<b><svg class="ico"><use href="#i-teoria"/></svg>Na teoria</b>')
caps=re.findall(r'data-capitulo="(\d+)"',telas)
n=len(caps)
def trilha(m):
    k=int(m.group(1)); return '<div class="trilha-cap">'+''.join(f'<span class="{"on" if int(c)<=k else ""}"></span>' for c in caps)+'</div>'
telas=re.sub(r'<trilha k="(\d+)"></trilha>',trilha,telas)
zj=R/'fonte/zoom.json'
if zj.exists():
    Z=json.loads(zj.read_text());idx=[-1]
    def poe(m):
        idx[0]+=1;k=str(idx[0]+1);a=Z.get(k)
        return m.group(0) if not a else f'<section data-z="{a[0]}" data-y="{a[1]}" '+m.group(1)
    telas=re.sub(r'<section ((?:id="[^"]*" )?class="tela )',poe,telas)
s=(R/'src/shell.html').read_text().replace('</svg>',(R/'fonte/icones.svg').read_text()+'</svg>',1).replace('__TELAS__',telas).replace('__VERSAO__',v)
s=s.replace('</body>',plano_html.DICA+'</body>');(R/'book.html').write_text(s);(R/'assets/deck.css').write_text(css+calendario.CSS);(R/'assets/deck.js').write_text((R/'src/deck.js').read_text());(R/'versao.txt').write_text(v)
bad=[x for x in ('—','–') if x in s+css]
print('telas',s.count('class="tela '),'capitulos',n,'tamanho',len(s)//1024,'KB','TRAVESSAO!' if bad else 'sem travessao')
