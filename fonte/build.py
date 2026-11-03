#!/usr/bin/env python3
# Monta index.html e assets/deck.* a partir de src/. Rodar da raiz: python3 fonte/build.py
import re,pathlib,time,json,sys
R=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R/'fonte'))
import graficos
v=time.strftime('%Y%m%d%H%M%S')
telas=''
css=(R/'src/deck.css').read_text()
for f in sorted((R/'src').glob('c*.html')):
    t=f.read_text()
    for m in re.findall(r'<style>(.*?)</style>',t,flags=re.S): css+='\n'+m
    telas+=re.sub(r'<style>.*?</style>','',t,flags=re.S)
telas=graficos.aplicar(telas)
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
s=(R/'src/shell.html').read_text().replace('__TELAS__',telas).replace('__VERSAO__',v)
(R/'index.html').write_text(s);(R/'assets/deck.css').write_text(css);(R/'assets/deck.js').write_text((R/'src/deck.js').read_text());(R/'versao.txt').write_text(v)
bad=[x for x in ('—','–') if x in s+css]
print('telas',s.count('class="tela '),'capitulos',n,'tamanho',len(s)//1024,'KB','TRAVESSAO!' if bad else 'sem travessao')
