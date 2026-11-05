#!/usr/bin/env python3
# Monta a apresentação executiva: index.html e assets/exec.*, a partir de fonte/exec/.
# Rodar da raiz, depois de fonte/build.py (que gera book.html e versao.txt): python3 fonte/exec_build.py
import pathlib
R=pathlib.Path(__file__).resolve().parent.parent;E=R/'fonte/exec'
v=(R/'versao.txt').read_text().strip()
t=(E/'telas.html').read_text()
s=(E/'shell.html').read_text().replace('__TELAS__',t).replace('__VERSAO__',v)
(R/'index.html').write_text(s);(R/'assets/exec.css').write_text((E/'exec.css').read_text());(R/'assets/exec.js').write_text((E/'exec.js').read_text())
css=(E/'exec.css').read_text();bad=[x for x in ('—','–') if x in s+css]
print('telas',s.count('class="tela '),'TRAVESSAO!' if bad else 'sem travessao')
