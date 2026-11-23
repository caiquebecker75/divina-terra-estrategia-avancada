# Gera versoes/index.html a partir de fonte/versoes.json.
# A versão sem "pasta" e com "data" é a atual e aponta para a raiz do site.
# A versão sem "data" está em produção e aparece sem links.
import json, pathlib, html

R = pathlib.Path(__file__).resolve().parent.parent
V = json.loads((R / 'fonte/versoes.json').read_text())
E = html.escape

def mb(p):
    return f'{p.stat().st_size / 1e6:.0f} MB'.replace('.', ',') if p.exists() else ''

def links(v):
    base = R / 'versoes' / v['pasta'] if v['pasta'] else R
    pre = f"{v['pasta']}/" if v['pasta'] else '../'
    tela = [('Apresentação', 'index.html'), ('Visão para a diretoria', 'diretoria.html'), ('Book', 'book.html'), ('Manual', 'manual.html'), ('Resposta à devolutiva', 'devolutiva.html'), ('Guia de Pinheiros', 'pinheiros.html')]
    pdf = [('Apresentação', 'divina-terra-apresentacao.pdf'), ('Diretoria', 'divina-terra-diretoria.pdf'), ('Book', 'divina-terra-book.pdf'), ('Manual', 'manual-divina-terra.pdf')]
    a = ''.join(f'<a class="bt" href="{pre}{f}">{t}</a>' for t, f in tela if (base / f).exists())
    b = ''.join(f'<a class="bt pdf" href="{pre}{f}" download>{t} <small>PDF · {mb(base / f)}</small></a>' for t, f in pdf if (base / f).exists())
    return f'<div class="links"><div><span class="rot">Abrir no navegador</span>{a}</div><div><span class="rot">Baixar</span>{b}</div></div>'

itens = []
for v in sorted(V, key=lambda v: -v['n']):
    if v['data'] is None:
        estado, cls = 'Em produção', 'prod'
    elif v['pasta'] is None:
        estado, cls = 'Versão atual', 'atual'
    else:
        estado, cls = 'Arquivada', 'arq'
    mud = ''.join(f'<li>{E(m)}</li>' for m in v['mudou'])
    itens.append(f'''<article class="v {cls}">
  <div class="num">v{v['n']}</div>
  <div class="corpo">
    <p class="meta"><span class="tag">{estado}</span>{E(v['data'] or 'sem data')}</p>
    <h2>{E(v['titulo'])}</h2>
    <p class="res">{E(v['resumo'])}</p>
    <ul>{mud}</ul>
    {links(v) if v['data'] else ''}
  </div>
</article>''')

doc = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Versões · Divina Terra</title>
<link rel="icon" href="../assets/logos/dt-icone-terra.svg">
<style>
@font-face{{font-family:'General Sans';src:url('../assets/fontes/GeneralSans-Variable.ttf') format('truetype');font-weight:200 700}}
:root{{--iogurte:#F7F5F1;--aveia:#E5DDD1;--choco:#7C381F;--terra:#461D17;--acafrao:#CA942A;--oliva:#596D49;--cinza:#6F5F55}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--iogurte);color:var(--terra);font-family:'General Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased;padding:56px 16px 80px}}
main{{max-width:880px;margin:0 auto}}
header img{{height:30px}}
.sob{{margin-top:44px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--choco);font-weight:600}}
h1{{font-size:clamp(34px,6vw,52px);font-weight:500;letter-spacing:-.02em;line-height:1.05;margin:10px 0 14px}}
.intro{{font-size:17px;line-height:1.55;color:var(--cinza);max-width:620px}}
.v{{display:grid;grid-template-columns:92px 1fr;gap:24px;border-top:1px solid #d9cfc1;padding:34px 0}}
.v:first-of-type{{margin-top:44px}}
.num{{font-size:44px;font-weight:500;color:var(--choco);line-height:1}}
.prod .num{{color:#b9ab98}}
.meta{{display:flex;gap:12px;align-items:center;font-size:14px;color:var(--cinza)}}
.tag{{font-size:12px;font-weight:600;padding:4px 10px;border-radius:999px;background:var(--aveia);color:var(--terra)}}
.atual .tag{{background:var(--oliva);color:#fff}}
.prod .tag{{background:#f0e6cf;color:#7a5a12}}
h2{{font-size:26px;font-weight:500;margin:12px 0 8px;letter-spacing:-.01em}}
.res{{font-size:16px;line-height:1.55;color:var(--cinza)}}
ul{{margin:14px 0 0 18px;font-size:15px;line-height:1.7}}
.links{{margin-top:22px;display:grid;gap:12px}}
.links>div{{display:flex;flex-wrap:wrap;gap:8px;align-items:center}}
.rot{{width:150px;font-size:13px;color:var(--cinza)}}
.bt{{display:inline-flex;gap:6px;align-items:baseline;padding:9px 15px;border-radius:999px;background:var(--terra);color:var(--iogurte);text-decoration:none;font-size:14px;font-weight:500}}
.bt:hover{{background:var(--choco)}}
.bt.pdf{{background:transparent;color:var(--terra);box-shadow:inset 0 0 0 1px #cbbfae}}
.bt.pdf:hover{{background:var(--aveia)}}
.bt small{{font-size:12px;color:var(--cinza)}}
footer{{margin-top:40px;font-size:13px;color:var(--cinza)}}
@media(max-width:620px){{.v{{grid-template-columns:1fr;gap:8px}}.num{{font-size:34px}}.rot{{width:100%}}}}
</style></head><body><main>
<header><img src="../assets/logos/dt-horizontal-terra.svg" alt="Divina Terra"></header>
<p class="sob">Estratégia de trade · Divina Navegação</p>
<h1>Versões do material</h1>
<p class="intro">Cada entrega fica guardada como foi apresentada. A versão atual sempre abre no link principal; as anteriores continuam aqui para consulta e comparação.</p>
{''.join(itens)}
<footer>75 LAB para Divina Terra</footer>
</main></body></html>
'''
(R / 'versoes').mkdir(exist_ok=True)
(R / 'versoes/index.html').write_text(doc)
print('versoes/index.html', len(V), 'versões')
