# Guia de montagem de Pinheiros para o time da loja: uma página só, feita para o celular, com mapa, montagem módulo a módulo
# (foto de cada produto, cor por ação, checklist), o que tirar da gôndola, o pedido e a busca "onde vai este produto?".
# Lê analise/pinheiros_guia.json (gerado por fonte/pinheiros.py). Fotos e fonte embutidas: funciona sem internet.
# Saída com estoque da loja, fora do repositório público: kit/pinheiros-guia.html
import base64, io, json, pathlib
from PIL import Image
R = pathlib.Path(__file__).resolve().parent.parent
G = json.loads((R / 'analise/pinheiros_guia.json').read_text())
sk = {it['s'] for z in G['zonas'] for b in z['bays'] for sg in b for n in sg['nv'] for it in n['it']}
fotos = {}
for s in sk:
    f = R / f'assets/produtos/{s}.webp'
    if not f.exists(): continue
    im = Image.open(f).convert('RGBA'); h = 120; w = max(1, round(im.width * h / im.height)); im = im.resize((w, h), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=62); fotos[s] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
fonte = 'data:font/ttf;base64,' + base64.b64encode((R / 'assets/fontes/GeneralSans-Variable.ttf').read_bytes()).decode()

PAGINA = r'''<title>Pinheiros · guia de montagem</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
<style>
@font-face{font-family:'General Sans';src:url('__FONTE__') format('truetype');font-weight:200 700;font-display:swap}
/* Layout: uma coluna para o celular; a loja é lida como um percurso (mapa, montar, tirar, pedir). Cores da Divina Terra; cor de ação separada da marca. */
:root{
  --bg:#F7F5F1;--card:#FFFFFF;--fg:#2B1A14;--muted:#6F5F55;--line:#E4DACD;--aveia:#E5DDD1;--linho:#BCAD99;
  --band:#461D17;--band-fg:#F7F5F1;--accent:#7C381F;--gold:#CA942A;
  --tem:#596D49;--pedir:#C98A1B;--novo:#7C381F;--tirar:#C2452D;--olho:#FBF1DE;--shelf:#8C6A55;
  --serif:'Source Serif 4',Georgia,'Times New Roman',serif;--sans:'General Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#1B1310;--card:#271C17;--fg:#F2EBE3;--muted:#BBAA9B;--line:#3D2F27;--aveia:#33261F;--linho:#5E4C40;
  --band:#2E1E18;--band-fg:#F2EBE3;--accent:#D8875F;--gold:#E3B14E;
  --tem:#8DAA76;--pedir:#E3A93A;--novo:#D8875F;--tirar:#E26A52;--olho:#3A2D1E;--shelf:#A88972;color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#1B1310;--card:#271C17;--fg:#F2EBE3;--muted:#BBAA9B;--line:#3D2F27;--aveia:#33261F;--linho:#5E4C40;
  --band:#2E1E18;--band-fg:#F2EBE3;--accent:#D8875F;--gold:#E3B14E;
  --tem:#8DAA76;--pedir:#E3A93A;--novo:#D8875F;--tirar:#E26A52;--olho:#3A2D1E;--shelf:#A88972;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:15px/1.45 var(--sans);margin:0}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:30;background:var(--band)}
.w{max-width:1080px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3{font-family:var(--serif);font-weight:400;margin:0;text-wrap:balance}
button{font:inherit;color:inherit;cursor:pointer}
:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
/* topo */
.topo{background:var(--band);color:var(--band-fg)}
.topo .w{padding-block:22px 18px;display:grid;gap:12px}
.eb{font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;opacity:.85}
.topo h1{font-size:clamp(30px,6vw,46px);line-height:1.05}.topo h1 em{font-style:italic;color:var(--gold)}
.topo p{margin:0;max-width:62ch;opacity:.9}
.prog{display:grid;gap:6px;max-width:520px}.prog .bar{height:12px;border-radius:99px;background:rgba(247,245,241,.18);overflow:hidden}
.prog .bar i{display:block;height:100%;width:0;background:var(--gold);border-radius:99px;transition:width .4s}
.prog b{font-size:15px}
/* navegação */
nav.tabs{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--bg);border-bottom:1px solid var(--line)}
nav.tabs .w{display:flex;gap:6px;overflow-x:auto;padding-block:10px;scrollbar-width:none}
nav.tabs a{flex:none;text-decoration:none;color:var(--fg);font-weight:600;font-size:14px;padding:9px 14px;border-radius:99px;background:var(--aveia)}
nav.tabs a.on{background:var(--accent);color:#fff}
main .w{padding-block:22px 80px}
section.v{display:grid;gap:18px}section.v[hidden]{display:none}
.h2{font-size:clamp(24px,4.5vw,32px)}
.sub{color:var(--muted);margin:0;max-width:65ch}
/* legenda de ação */
.leg{display:flex;flex-wrap:wrap;gap:8px}.leg span{display:inline-flex;align-items:center;gap:7px;background:var(--card);border:1px solid var(--line);border-radius:99px;padding:6px 12px;font-size:13.5px;font-weight:500}
.dot{width:14px;height:14px;border-radius:50%;flex:none;display:inline-block}
.d-tem{background:var(--tem)}.d-pedir{background:var(--pedir)}.d-novo{background:var(--novo)}.d-livre{background:repeating-linear-gradient(135deg,var(--linho) 0 3px,transparent 3px 6px);border:1px solid var(--linho)}.d-tirar{background:var(--tirar)}
/* passos */
.passos{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.passos div{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;display:grid;gap:6px;align-content:start}
.passos svg{width:34px;height:34px;color:var(--accent)}.passos b{font-size:16px}.passos p{margin:0;color:var(--muted);font-size:14px}
.regras{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.regras div{border-radius:14px;padding:14px 16px;background:var(--aveia);display:grid;gap:4px}.regras b{font-family:var(--serif);font-size:20px;font-weight:400}.regras span{font-size:14px;color:var(--muted)}
/* mapa */
.mapa{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:12px;display:grid;gap:8px}
.mapa svg{width:100%;height:auto;max-height:72vh;display:block}
.mapa .zz{cursor:pointer}.mapa .zz rect{transition:transform .15s}.mapa .zz:hover rect,.mapa .zz:focus rect{stroke:var(--gold);stroke-width:3}
.mapa text{font-family:var(--sans);pointer-events:none}
.nota{font-size:13px;color:var(--muted);margin:0}
/* zonas */
.zonas{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;scrollbar-width:thin}
.zonas button{flex:none;border:1px solid var(--line);background:var(--card);border-radius:12px;padding:8px 12px;text-align:left;display:grid;gap:2px;min-width:132px}
.zonas button b{font-size:14px}.zonas button small{color:var(--muted);font-size:12px}
.zonas button.on{background:var(--band);color:var(--band-fg);border-color:var(--band)}.zonas button.on small{color:var(--band-fg);opacity:.8}
.zonas button.ok small::after{content:" · pronto";color:var(--tem);font-weight:600}
/* módulo */
.mod{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:18px;align-items:start}
@media(max-width:820px){.mod{grid-template-columns:1fr}}
.cab{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.cab h3{font-size:clamp(22px,4vw,28px)}.cab .zn{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.seta{display:flex;gap:8px}.seta button{width:52px;height:52px;border-radius:50%;border:none;background:var(--band);color:var(--band-fg);font-size:22px;display:grid;place-items:center}
.seta button:disabled{opacity:.3;cursor:default}
.setores{display:flex;gap:6px;flex-wrap:wrap}.setores span{font-size:13px;font-weight:600;padding:4px 10px;border-radius:99px;background:var(--aveia)}
.movel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:12px 12px 10px;display:grid;gap:8px}
.movel .med{display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}
.estante{display:grid;grid-template-columns:52px minmax(0,1fr);gap:0}
.nl{display:grid;align-content:center;justify-items:center;font-size:11px;color:var(--muted);line-height:1.1;text-align:center;border-bottom:4px solid var(--shelf);padding:2px}
.nl b{font-size:18px;color:var(--fg);font-family:var(--serif)}
.nl.olho{background:var(--olho)}.nl.olho span{color:var(--accent);font-weight:600}
.pr{display:flex;border-bottom:4px solid var(--shelf);min-height:84px;position:relative}
.pr.olho{background:var(--olho)}
.pr.ae{min-height:40px;background:repeating-linear-gradient(135deg,var(--aveia) 0 6px,transparent 6px 12px)}
.pr.ae em{margin:auto;font-size:12px;color:var(--muted);font-style:normal}
.seg{display:flex;flex-direction:column;min-width:0;border-left:1px dashed var(--linho)}.seg:first-child{border-left:none}
.seg .rot{font-size:10.5px;color:var(--muted);padding:2px 4px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.seg .its{flex:1;display:flex;align-items:flex-end;padding:0 2px;gap:1px}
.it{border:none;background:none;padding:0;display:flex;flex-direction:column;align-items:stretch;justify-content:flex-end;height:100%;min-width:0;position:relative}
.it .fr{display:flex;align-items:flex-end;justify-content:center;gap:1px;height:62px}
.it .fr img{flex:1;min-width:0;max-height:62px;object-fit:contain;object-position:bottom}
.it .fr .pk{flex:1;min-width:0;height:52px;border-radius:3px 3px 1px 1px;display:flex;align-items:center;justify-content:center;overflow:hidden;font-size:8.5px;font-weight:600;line-height:1;color:#fff;text-align:center;writing-mode:vertical-rl;transform:rotate(180deg);padding:2px 0}
.it .ac{height:6px;border-radius:2px;margin-top:2px}
.it .nu{position:absolute;top:-2px;left:50%;transform:translateX(-50%);min-width:18px;height:18px;border-radius:99px;font-size:10.5px;font-weight:700;color:#fff;display:grid;place-items:center;padding:0 4px;box-shadow:0 0 0 2px var(--card)}
.it.sel .fr{outline:3px solid var(--gold);outline-offset:1px;border-radius:4px}
.livre{flex:1;align-self:stretch;margin:16px 2px 2px;border-radius:4px;background:repeating-linear-gradient(135deg,var(--aveia) 0 5px,transparent 5px 10px);display:grid;place-items:center;font-size:10px;color:var(--muted);min-width:0}
.a-tem{background:var(--tem)}.a-pedir{background:var(--pedir)}.a-novo{background:var(--novo)}
/* lista do módulo */
.lista{display:grid;gap:12px}
.ln{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.ln h4{margin:0;padding:9px 12px;font-size:13.5px;background:var(--aveia);display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}.ln h4 small{color:var(--muted);font-weight:500}
.ln.olho h4{background:var(--olho)}
.ln ol{list-style:none;margin:0;padding:0}
.ln li{display:grid;grid-template-columns:26px minmax(0,1fr) auto;gap:10px;align-items:center;padding:8px 12px;border-top:1px solid var(--line);cursor:pointer}
.ln li:first-child{border-top:none}.ln li:hover{background:var(--olho)}
.ln li .nu{width:24px;height:24px;border-radius:99px;color:#fff;font-size:12px;font-weight:700;display:grid;place-items:center}
.ln li b{font-weight:600;display:block;line-height:1.25}.ln li small{color:var(--muted);font-size:12.5px}
.ln li .q{font-size:12.5px;text-align:right;color:var(--muted);white-space:nowrap}.ln li .q b{font-size:15px;color:var(--fg)}
/* checklist */
.chk{display:grid;gap:8px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px}
.chk label{display:flex;gap:12px;align-items:center;font-size:15.5px;font-weight:500;cursor:pointer;padding:4px 0}
.chk input{width:26px;height:26px;accent-color:var(--tem);flex:none}
.feito{background:var(--tem);color:#fff;border-radius:12px;padding:10px 14px;font-weight:600;text-align:center}
.prox{display:grid;grid-template-columns:1fr 1fr;gap:10px}.prox button{border:none;border-radius:14px;padding:16px;font-weight:600;font-size:16px;background:var(--aveia)}
.prox button.go{background:var(--band);color:var(--band-fg)}.prox button:disabled{opacity:.35;cursor:default}
/* granel */
.tubos{display:grid;grid-template-columns:repeat(auto-fill,minmax(98px,1fr));gap:8px}
.tubos div{border-radius:10px 10px 4px 4px;min-height:96px;padding:8px;display:flex;flex-direction:column;justify-content:space-between;font-size:12.5px;font-weight:600;line-height:1.2;color:#fff}
.tubos div small{font-weight:500;opacity:.9;font-size:11px}
.tubos .lv{background:repeating-linear-gradient(135deg,var(--aveia) 0 6px,var(--card) 6px 12px);color:var(--muted);border:1px dashed var(--linho)}
/* listas */
details.grp{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
details.grp summary{cursor:pointer;padding:12px 14px;font-weight:600;display:flex;justify-content:space-between;gap:10px;list-style:none}
details.grp summary::-webkit-details-marker{display:none}
details.grp summary::after{content:"+";font-size:20px;line-height:1;color:var(--accent)}details.grp[open] summary::after{content:"−"}
details.grp summary small{color:var(--muted);font-weight:500;margin-left:auto}
.tl{list-style:none;margin:0;padding:0}.tl li{display:grid;grid-template-columns:28px minmax(0,1fr) auto;gap:10px;align-items:center;padding:8px 14px;border-top:1px solid var(--line)}
.tl input{width:22px;height:22px;accent-color:var(--tirar)}.tl li.x b{text-decoration:line-through;opacity:.55}
.tl b{font-weight:500;display:block}.tl small{color:var(--muted);font-size:12.5px}.tl .q{font-weight:700;font-size:15px;white-space:nowrap}
.bigcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.bigcards div{border-radius:14px;padding:14px;color:#fff;display:grid;gap:2px}.bigcards b{font-family:var(--serif);font-size:34px;font-weight:400;line-height:1}
/* busca */
.busca input{width:100%;font:inherit;font-size:17px;padding:14px 16px;border-radius:14px;border:2px solid var(--line);background:var(--card);color:var(--fg)}
.res{display:grid;gap:8px}.res button{border:1px solid var(--line);background:var(--card);border-radius:12px;padding:10px 12px;text-align:left;display:grid;grid-template-columns:46px minmax(0,1fr);gap:10px;align-items:center}
.res img,.res .ph0{width:46px;height:46px;object-fit:contain;border-radius:6px;background:var(--aveia)}
.res b{display:block;font-weight:600}.res small{color:var(--muted)}
/* folha de detalhe */
.folha{position:fixed;inset:auto 0 0 0;z-index:40;background:var(--card);border-radius:20px 20px 0 0;box-shadow:0 -10px 40px rgba(0,0,0,.25);padding:16px max(16px,env(safe-area-inset-right,0px)) calc(18px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));max-width:620px;margin:0 auto;display:grid;gap:12px}
.folha .tp{display:grid;grid-template-columns:96px minmax(0,1fr);gap:14px;align-items:center}
.folha img,.folha .ph0{width:96px;height:110px;object-fit:contain;border-radius:10px;background:var(--aveia)}
.folha h3{font-size:22px}.folha .mk{color:var(--muted);font-size:14px}
.folha .acao{border-radius:12px;padding:12px 14px;color:#fff;font-weight:600;font-size:15.5px}
.folha dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:0;font-size:14.5px}.folha dt{color:var(--muted)}.folha dd{margin:0;font-weight:500}
.folha .fx{border:none;background:var(--aveia);border-radius:12px;padding:12px;font-weight:600}
.veu{position:fixed;inset:0;z-index:35;background:rgba(20,12,9,.45)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<header class="topo"><div class="w">
  <span class="eb">Divina Terra Pinheiros · piloto do planograma</span>
  <h1>Guia de montagem: <em>a loja nova, módulo a módulo</em></h1>
  <p>Siga o mapa, monte um módulo de 0,90 m por vez e marque quando terminar. Cada foto é uma frente. A cor embaixo do produto diz o que fazer.</p>
  <div class="prog"><b id="pgTxt">0 de 0 módulos montados</b><div class="bar"><i id="pgBar"></i></div></div>
</div></header>
<nav class="tabs" aria-label="Partes do guia"><div class="w">
  <a href="#inicio" data-v="inicio">Começar</a><a href="#mapa" data-v="mapa">Mapa</a><a href="#montar" data-v="montar">Montar</a>
  <a href="#tirar" data-v="tirar">Tirar da gôndola</a><a href="#pedido" data-v="pedido">Pedido</a><a href="#buscar" data-v="buscar">Onde vai?</a>
</div></nav>
<main><div class="w">

<section class="v" id="v-inicio">
  <h2 class="h2">Antes de começar</h2>
  <div class="passos">
    <div><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="26" height="10" rx="2"/><path d="M8 11v4M13 11v6M18 11v4M23 11v6"/></svg><b>1. Meça com trena</b><p>Cada módulo tem 0,90 m de largura. Se o móvel for diferente, ajuste as frentes e avise.</p></div>
    <div><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 10h22l-2 17H7z"/><path d="M11 10V7a5 5 0 0 1 10 0v3"/></svg><b>2. Tire o que sai</b><p>Na aba "Tirar da gôndola" está o que não volta para a prateleira. Separe antes de montar.</p></div>
    <div><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="4" width="22" height="24" rx="2"/><path d="M5 11h22M5 18h22M16 4v24"/></svg><b>3. Monte de cima para baixo</b><p>Um módulo por vez, nível 1 primeiro. Esvazie, limpe e arrume pela foto.</p></div>
    <div><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="9" width="24" height="17" rx="3"/><circle cx="16" cy="17.5" r="5"/><path d="M11 9l2-4h6l2 4"/></svg><b>4. Etiqueta e foto</b><p>Etiqueta de preço em cada produto e uma foto do módulo pronto para o grupo.</p></div>
  </div>
  <h2 class="h2">O que cada cor quer dizer</h2>
  <div class="leg"><span><i class="dot d-tem"></i>Já tem na loja: pegue e arrume aqui</span><span><i class="dot d-pedir"></i>Chega no pedido: deixe o espaço e a etiqueta</span><span><i class="dot d-novo"></i>Novo na loja: chega no pedido</span><span><i class="dot d-livre"></i>Espaço livre da loja</span></div>
  <h2 class="h2">Quatro regras de ouro</h2>
  <div class="regras">
    <div><b>Nos olhos, o que mais vende</b><span>Níveis 3 e 4, marcados em amarelo no desenho.</span></div>
    <div><b>Pesado embaixo</b><span>Pote acima de 500 g só nos níveis 5 e 6.</span></div>
    <div><b>Marca junta, líder no meio</b><span>Os produtos da mesma marca ficam lado a lado.</span></div>
    <div><b>Uma prateleira, um tipo</b><span>Cada prateleira tem um tipo de produto e um tamanho.</span></div>
  </div>
  <div class="bigcards" id="numeros"></div>
  <p class="nota">Feito pela 75 LAB com o estoque da loja de 12/11/2026 e a venda de julho a setembro de 2026. Medidas dos móveis estimadas na visita de 14/10: confira com a trena. Este guia guarda o que você marcou só neste aparelho.</p>
</section>

<section class="v" id="v-mapa" hidden>
  <h2 class="h2">Mapa da loja</h2>
  <p class="sub">Toque em uma área para montar os módulos dela. O número mostra quantos módulos já estão prontos.</p>
  <div class="mapa"><svg id="svgMapa" viewBox="0 0 420 560" role="img" aria-label="Mapa esquemático da loja de Pinheiros"></svg>
  <p class="nota">Esquema fora de escala. A entrada fica embaixo; o fundo da loja, em cima.</p></div>
</section>

<section class="v" id="v-montar" hidden>
  <div class="zonas" id="zonas" role="tablist" aria-label="Áreas da loja"></div>
  <div id="palco"></div>
</section>

<section class="v" id="v-tirar" hidden>
  <h2 class="h2">Tirar da gôndola</h2>
  <p class="sub">Faça isto antes de montar. Marque cada produto quando tirar.</p>
  <div class="bigcards"><div style="background:var(--tirar)"><b id="nTirar">0</b>parados: não vendem desde julho</div><div style="background:var(--muted)"><b id="nGuardar">0</b>ainda vendem, mas ficaram sem lugar</div></div>
  <h3 class="h2" style="font-size:22px">Parados: levar para a mesa de oferta ou para transferência</h3>
  <p class="sub">Não repor. Não precisa queimar preço: a rede decide se vão para outra loja.</p>
  <div class="lista" id="lTirar"></div>
  <h3 class="h2" style="font-size:22px">Ainda vendem: guardar no estoque</h3>
  <p class="sub">Volta para a prateleira quando abrir espaço livre no setor. Quando acabar, não repor.</p>
  <div class="lista" id="lGuardar"></div>
</section>

<section class="v" id="v-pedido" hidden>
  <h2 class="h2">O que chega no pedido</h2>
  <p class="sub">Produtos do planograma que estão sem estoque ou com pouco. Na prateleira, deixe o espaço e a etiqueta: quando chegar, é só colocar.</p>
  <div class="bigcards" id="pedNum"></div>
  <div class="lista" id="lPedido"></div>
</section>

<section class="v" id="v-buscar" hidden>
  <h2 class="h2">Onde vai este produto?</h2>
  <div class="busca"><label for="q" class="sub">Digite o nome, a marca ou o código do produto</label><input id="q" type="search" placeholder="Ex.: creatina, Essential, 886" autocomplete="off"></div>
  <div class="res" id="res"></div>
</section>
</div></main>
<div id="folha" hidden></div>

<script type="application/json" id="dados">__DADOS__</script>
<script type="application/json" id="fotos">__FOTOS__</script>
<script>
(function(){
'use strict';
const G=JSON.parse(document.getElementById('dados').textContent);
const F=JSON.parse(document.getElementById('fotos').textContent);
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const num=(v,c=0)=>Number(v).toLocaleString('pt-BR',{minimumFractionDigits:c,maximumFractionDigits:c});
const NIV={1:'Alto',2:'Alto',3:'Olhos',4:'Olhos',5:'Mão',6:'Baixo'};
const ACAO={tem:['Já tem na loja','Pegue no estoque e arrume aqui.'],pedir:['Chega no pedido','Deixe o espaço e a etiqueta. Quando chegar, coloque aqui.'],novo:['Novo na loja','Produto essencial da rede que a loja ainda não tinha. Chega no pedido.']};
const ZCOR={parede:'#7C381F',proteina:'#9A4A2A',treino:'#596D49',saude:'#7E8F5C',lanches:'#CA942A',despensa:'#AC834C',gourmet:'#461D17',chas:'#6B7E4E',granel:'#8C6A55'};
const FAM={'Castanhas e frutas secas':'#7C381F','Grãos, cereais e farinhas':'#9C8770','Sementes e temperos':'#596D49','Chás e snacks':'#B07F22'};
const PAL=['#7C381F','#596D49','#AC834C','#461D17','#8C6A55','#6B7E4E','#9A4A2A','#B07F22'];
const corMarca=m=>{let h=0;for(const c of String(m))h=(h*31+c.charCodeAt(0))>>>0;return PAL[h%PAL.length]};
// zonas, com o granel no fim
const Z=G.zonas.map(z=>Object.assign({},z));
Z.push({id:'granel',nome:'Granel',desc:'Módulos de granel de hoje: nenhum tubo sai do lugar. Placa visível da porta e potinho de prova.',bays:[[]],granel:true});
// índice de produtos para a busca e a folha
const IDX=[];
Z.forEach((z,zi)=>z.bays.forEach((b,bi)=>b.forEach(sg=>sg.nv.forEach(n=>n.it.forEach(it=>IDX.push({it,zi,bi,n:n.n,rot:n.r,setor:sg.c}))))));
G.granel.forEach((t,k)=>IDX.push({it:{s:t.s,n:t.n,m:'A granel',f:1,a:t.e>0?'tem':'pedir',e:t.e,p:0},zi:Z.length-1,bi:0,n:0,rot:t.fam,setor:'Granel',tubo:k+1}));
// progresso guardado só neste aparelho
let EST={};try{EST=JSON.parse(localStorage.getItem('pin-guia-v1')||'{}')}catch(e){EST={}}
const salva=()=>{try{localStorage.setItem('pin-guia-v1',JSON.stringify(EST))}catch(e){}};
const chave=(zi,bi)=>Z[zi].id+'-'+bi;
const total=Z.reduce((a,z)=>a+z.bays.length,0);
function progresso(){
  const ok=Object.keys(EST).filter(k=>EST[k]&&EST[k].montado&&!k.startsWith('t:')).length;
  $('#pgTxt').textContent=`${ok} de ${total} módulos montados`;$('#pgBar').style.width=(ok/total*100)+'%';
  $$('#zonas button').forEach((b,zi)=>{const z=Z[zi],n=z.bays.filter((_,bi)=>EST[chave(zi,bi)]&&EST[chave(zi,bi)].montado).length;
    b.querySelector('small').textContent=`${n} de ${z.bays.length} ${z.granel?'parte':'módulo'+(z.bays.length>1?'s':'')}`;b.classList.toggle('ok',n===z.bays.length)});
  desenhaMapa();
}
// ---------- abas ----------
const VIS=['inicio','mapa','montar','tirar','pedido','buscar'];
function mostra(v){if(!VIS.includes(v))v='inicio';VIS.forEach(x=>{$('#v-'+x).hidden=x!==v});$$('nav.tabs a').forEach(a=>a.classList.toggle('on',a.dataset.v===v));}
window.addEventListener('hashchange',()=>{mostra(location.hash.slice(1));window.scrollTo(0,0)});
// ---------- números do início ----------
const R_=G.resumo;
$('#numeros').innerHTML=[[total,'módulos para montar',ZCOR.parede],[R_.plano,'produtos no planograma',ZCOR.treino],[R_.pedir,'chegam no pedido',ZCOR.lanches],[R_.tirar,'saem da gôndola',ZCOR.gourmet]]
  .map(([v,t,c])=>`<div style="background:${c}"><b>${num(v)}</b>${t}</div>`).join('');
// ---------- mapa ----------
const AREAS=[['parede',12,120,52,330,'Parede de\nsuplementos',1],['proteina',84,138,110,46,'Ilha da Proteína'],['saude',214,138,110,46,'Ilha da Saúde'],
  ['treino',84,214,110,46,'Ilha do Treino'],['lanches',214,214,110,46,'Ilha dos Lanches'],['despensa',84,290,240,46,'Ilha da Despensa'],
  ['chas',130,30,130,34,'Chás'],['gourmet',282,30,126,60,'Gourmet\nao lado das mesas'],['granel',348,138,60,240,'Granel',1]];
function desenhaMapa(){
  const svg=$('#svgMapa');if(!svg)return;
  let s=`<rect x="4" y="4" width="412" height="552" rx="16" fill="var(--bg)" stroke="var(--linho)" stroke-width="2"/>`;
  s+=`<rect x="12" y="30" width="104" height="40" rx="8" fill="var(--aveia)"/><text x="64" y="55" text-anchor="middle" font-size="12" fill="var(--muted)">Geladeiras</text>`;
  s+=`<rect x="282" y="96" width="126" height="26" rx="8" fill="var(--aveia)"/><text x="345" y="113" text-anchor="middle" font-size="12" fill="var(--muted)">Mesas e café</text>`;
  s+=`<circle cx="204" cy="400" r="34" fill="var(--olho)" stroke="var(--gold)" stroke-dasharray="5 4" stroke-width="2"/><text x="204" y="396" text-anchor="middle" font-size="12" font-weight="600" fill="var(--fg)">Mesa</text><text x="204" y="411" text-anchor="middle" font-size="12" font-weight="600" fill="var(--fg)">do mês</text>`;
  s+=`<rect x="300" y="430" width="108" height="56" rx="10" fill="var(--aveia)"/><text x="354" y="462" text-anchor="middle" font-size="13" font-weight="600" fill="var(--muted)">Caixa</text>`;
  s+=`<rect x="12" y="506" width="396" height="40" rx="10" fill="var(--aveia)"/><text x="210" y="531" text-anchor="middle" font-size="13" font-weight="600" fill="var(--muted)">Vitrine e entrada</text>`;
  AREAS.forEach(([id,x,y,w,h,nome,vert])=>{
    const zi=Z.findIndex(z=>z.id===id);if(zi<0)return;const z=Z[zi];const n=z.bays.filter((_,bi)=>EST[chave(zi,bi)]&&EST[chave(zi,bi)].montado).length;
    const lin=nome.split('\n');const cx=x+w/2,cy=y+h/2;
    const tx=vert?`<text x="${cx}" y="${cy}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#fff" transform="rotate(-90 ${cx} ${cy})">${esc(lin.join(' '))}</text>`
      :lin.map((l,i)=>`<text x="${cx}" y="${cy-(lin.length-1)*7+i*14+4}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#fff">${esc(l)}</text>`).join('');
    s+=`<g class="zz" tabindex="0" role="button" aria-label="${esc(z.nome)}: ${n} de ${z.bays.length} prontos" data-z="${zi}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="9" fill="${ZCOR[id]}"/>${tx}
      <circle cx="${x+w-4}" cy="${y+4}" r="13" fill="${n===z.bays.length?'var(--tem)':'var(--card)'}" stroke="${ZCOR[id]}" stroke-width="2"/><text x="${x+w-4}" y="${y+8}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${n===z.bays.length?'#fff':'var(--fg)'}">${n}/${z.bays.length}</text></g>`;
  });
  svg.innerHTML=s;
  $$('.zz',svg).forEach(g=>{const go=()=>{zona=+g.dataset.z;baia=0;location.hash='montar';desenha()};g.addEventListener('click',go);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}})});
}
// ---------- montar ----------
let zona=0,baia=0,sel=null;
try{const u=JSON.parse(localStorage.getItem('pin-guia-pos')||'null');if(u){zona=Math.min(u[0],Z.length-1);baia=Math.min(u[1],Z[zona].bays.length-1)}}catch(e){}
$('#zonas').innerHTML=Z.map((z,zi)=>`<button role="tab" data-z="${zi}"><b>${esc(z.nome)}</b><small></small></button>`).join('');
$$('#zonas button').forEach(b=>b.addEventListener('click',()=>{zona=+b.dataset.z;baia=0;desenha();b.scrollIntoView({inline:'center',block:'nearest'})}));
function tile(it,k,larg){
  const f=Math.max(1,it.f);const ph=F[it.s];
  const fr=Array.from({length:f},()=>ph?`<img src="${ph}" alt="">`:`<span class="pk" style="background:${corMarca(it.m)}">${esc(it.m)}</span>`).join('');
  return `<button class="it" style="flex:0 0 ${larg}%" data-k="${k}" aria-label="${k}. ${esc(it.n)}"><span class="fr">${fr}</span><span class="ac a-${it.a}"></span><span class="nu a-${it.a}">${k}</span></button>`;
}
function desenha(){
  try{localStorage.setItem('pin-guia-pos',JSON.stringify([zona,baia]))}catch(e){}
  $$('#zonas button').forEach((b,zi)=>{b.classList.toggle('on',zi===zona);b.setAttribute('aria-selected',zi===zona)});
  const z=Z[zona],p=$('#palco');
  if(z.granel){desenhaGranel(p,z);return}
  const b=z.bays[baia],key=chave(zona,baia),st=EST[key]||{};
  const setores=[...new Set(b.map(sg=>sg.c))];
  // numeração: nível por nível, da esquerda para a direita
  const itens=[];let k=0;
  const niveis=[1,2,3,4,5,6].map(n=>{const linha=b.map(sg=>{const nv=sg.nv.find(x=>x.n===n)||{it:[],r:''};return{sg,nv,its:nv.it.map(it=>({it,k:++k}))}});linha.forEach(l=>l.its.forEach(x=>itens.push(Object.assign({n,rot:l.nv.r,setor:l.sg.c},x))));return{n,linha}});
  const larg=sg=>(sg.w>=1?86:43);
  let est=`<div class="estante">`;
  if(z.id==='parede') est+=`<div class="nl"><b>7</b>topo</div><div class="pr ae"><em>Nível 7: só estoque aéreo e placa do setor</em></div>`;
  niveis.forEach(({n,linha})=>{
    const ol=(n===3||n===4)?' olho':'';
    est+=`<div class="nl${ol}"><b>${n}</b><span>${NIV[n]}</span></div><div class="pr${ol}">`;
    linha.forEach(l=>{const W=larg(l.sg);let usado=0;
      const its=l.its.map(x=>{const lw=x.it.w*Math.max(1,x.it.f);usado+=lw;return tile(x.it,x.k,Math.min(100,lw/W*100))}).join('');
      const sobra=W-usado;
      est+=`<div class="seg" style="flex:${l.sg.w}"><span class="rot">${esc(l.nv.r||l.sg.c)}</span><div class="its">${its}${sobra>=12?`<span class="livre">${usado>0?'livre':'Livre: placa do setor ou produto da loja'}</span>`:''}</div></div>`;});
    est+=`</div>`;
  });
  est+=`</div>`;
  const lista=niveis.map(({n,linha})=>{const xs=itens.filter(x=>x.n===n);if(!xs.length)return'';const ol=(n===3||n===4)?' olho':'';
    const rots=[...new Set(linha.map(l=>l.nv.r).filter(Boolean))].join(' · ');
    return `<div class="ln${ol}"><h4>Nível ${n} · ${NIV[n]} <small>${esc(rots)}</small></h4><ol>${xs.map(x=>`<li data-k="${x.k}"><span class="nu a-${x.it.a}">${x.k}</span><span><b>${esc(x.it.n)}</b><small>${esc(x.it.m)} · ${ACAO[x.it.a][0]}${x.it.l?' · extra desta loja':''}</small></span><span class="q"><b>${x.it.f}</b> frente${x.it.f>1?'s':''}</span></li>`).join('')}</ol></div>`}).join('');
  const tot=itens.length,ped=itens.filter(x=>x.it.a!=='tem').length;
  p.innerHTML=`<div class="mod"><div style="display:grid;gap:12px;min-width:0">
    <div class="cab"><div><div class="zn">${esc(z.nome)} · módulo ${baia+1} de ${z.bays.length}</div><h3>${setores.map(esc).join(' e ')}</h3></div>
      <div class="seta"><button id="ant" aria-label="Módulo anterior" ${baia===0?'disabled':''}>‹</button><button id="seg" aria-label="Próximo módulo" ${baia===z.bays.length-1?'disabled':''}>›</button></div></div>
    <p class="sub">${esc(z.desc)}</p>
    <div class="setores">${b.map(sg=>`<span>${esc(sg.c)}${sg.w<1?' · meio módulo':''}</span>`).join('')}<span>${tot} produtos</span>${ped?`<span style="background:var(--pedir);color:#fff">${ped} chegam no pedido</span>`:''}</div>
    <div class="movel"><div class="med"><span>← 0,90 m →</span><span>toque num produto para ver o nome</span></div>${est}</div>
    <div class="leg"><span><i class="dot d-tem"></i>Já tem</span><span><i class="dot d-pedir"></i>Pedido</span><span><i class="dot d-novo"></i>Novo</span><span><i class="dot d-livre"></i>Livre</span></div>
  </div><div style="display:grid;gap:12px;min-width:0">
    <div class="chk"><b>Checklist deste módulo</b>
      <label><input type="checkbox" id="c1" ${st.limpo?'checked':''}> Esvaziei e limpei as prateleiras</label>
      <label><input type="checkbox" id="c2" ${st.montado?'checked':''}> Arrumei igual ao desenho</label>
      <label><input type="checkbox" id="c3" ${st.foto?'checked':''}> Pus as etiquetas e tirei a foto</label>
      ${st.montado?'<div class="feito">Módulo pronto. Muito bem!</div>':''}</div>
    <div class="lista">${lista}</div>
    <div class="prox"><button id="ant2" ${baia===0&&zona===0?'disabled':''}>‹ Anterior</button><button class="go" id="seg2">${baia<z.bays.length-1?'Próximo módulo ›':(zona<Z.length-1?'Próxima área ›':'Fim da montagem')}</button></div>
  </div></div>`;
  const anda=d=>{if(d>0){if(baia<z.bays.length-1)baia++;else if(zona<Z.length-1){zona++;baia=0}}else{if(baia>0)baia--;else if(zona>0){zona--;baia=Z[zona].bays.length-1}}desenha();$('#v-montar').scrollIntoView({block:'start'})};
  $('#ant').onclick=()=>anda(-1);$('#seg').onclick=()=>anda(1);$('#ant2').onclick=()=>anda(-1);$('#seg2').onclick=()=>anda(1);
  [['c1','limpo'],['c2','montado'],['c3','foto']].forEach(([id,campo])=>$('#'+id).addEventListener('change',e=>{EST[key]=Object.assign({},EST[key],{[campo]:e.target.checked});salva();progresso();if(campo==='montado')desenha()}));
  $$('.it,.ln li',p).forEach(el=>el.addEventListener('click',()=>{const x=itens.find(i=>i.k===+el.dataset.k);if(x)abre({it:x.it,n:x.n,rot:x.rot,setor:x.setor,zi:zona,bi:baia,k:x.k})}));
  progresso();
}
function desenhaGranel(p,z){
  const key=chave(zona,0),st=EST[key]||{};
  const t=G.granel.map((x,k)=>`<div style="background:${FAM[x.fam]||'#8C6A55'}"><span>${k+1}. ${esc(x.n)}</span><small>${esc(x.fam)}${x.e>0?'':' · pedido'}</small></div>`).join('')+'<div class="lv"><span>Livre</span><small>item da região</small></div><div class="lv"><span>Livre</span><small>item da região</small></div>';
  p.innerHTML=`<div class="cab"><div><div class="zn">Granel</div><h3>Tubos na ordem, por família</h3></div></div><p class="sub">${esc(z.desc)} Da esquerda para a direita, de cima para baixo. Castanhas e frutas secas na altura dos olhos.</p>
  <div class="leg">${Object.entries(FAM).map(([k,v])=>`<span><i class="dot" style="background:${v}"></i>${esc(k)}</span>`).join('')}</div>
  <div class="tubos">${t}</div>
  <div class="chk"><b>Checklist do granel</b><label><input type="checkbox" id="g1" ${st.montado?'checked':''}> Tubos na ordem e com etiqueta de preço</label><label><input type="checkbox" id="g2" ${st.foto?'checked':''}> Placa de granel visível da porta e potinho de prova</label></div>`;
  $('#g1').addEventListener('change',e=>{EST[key]=Object.assign({},EST[key],{montado:e.target.checked});salva();progresso()});
  $('#g2').addEventListener('change',e=>{EST[key]=Object.assign({},EST[key],{foto:e.target.checked});salva()});
  progresso();
}
// ---------- folha de detalhe ----------
function abre(x){
  const it=x.it,a=ACAO[it.a]||ACAO.tem,ph=F[it.s],z=Z[x.zi];
  const onde=x.setor==='Granel'?`Granel · tubo ${x.tubo}`:`${z.nome} · módulo ${x.bi+1} · nível ${x.n} (${NIV[x.n]})`;
  const pr=it.pr&&it.pr[0]?`R$ ${num(it.pr[0],2)} a R$ ${num(it.pr[1],2)}`:'';
  $('#folha').hidden=false;
  $('#folha').innerHTML=`<div class="veu" id="veu"></div><div class="folha" role="dialog" aria-modal="true" aria-label="${esc(it.n)}">
    <div class="tp">${ph?`<img src="${ph}" alt="">`:`<span class="ph0" style="background:${corMarca(it.m)}"></span>`}<div><div class="mk">${esc(it.m)} · código ${it.s}</div><h3>${esc(it.n)}</h3></div></div>
    <div class="acao a-${it.a}">${a[0]}. ${a[1]}</div>
    <dl><dt>Onde</dt><dd>${esc(onde)}</dd><dt>Prateleira</dt><dd>${esc(x.rot||x.setor)}</dd><dt>Frentes</dt><dd>${it.f}</dd>
    <dt>Estoque 12/11</dt><dd>${num(it.e||0,it.e%1?2:0)}</dd>${it.p?`<dt>Pedido</dt><dd>${it.p}</dd>`:''}${pr?`<dt>Faixa de preço</dt><dd>${pr}</dd>`:''}</dl>
    <button class="fx" id="fx">Fechar</button></div>`;
  const fecha=()=>{$('#folha').hidden=true;$('#folha').innerHTML=''};$('#fx').onclick=fecha;$('#veu').onclick=fecha;
  document.addEventListener('keydown',function k(e){if(e.key==='Escape'){fecha();document.removeEventListener('keydown',k)}});
  $('#fx').focus();
}
// ---------- tirar ----------
function grupos(lista,alvo,tipo){
  const por={};lista.forEach((x,i)=>{(por[x.st]=por[x.st]||[]).push(Object.assign({i},x))});
  $(alvo).innerHTML=Object.keys(por).sort().map(st=>{const xs=por[st];const feitos=xs.filter(x=>EST['t:'+tipo+':'+x.i]).length;
    return `<details class="grp"><summary>${esc(st)}<small>${feitos} de ${xs.length}</small></summary><ul class="tl">${xs.map(x=>`<li class="${EST['t:'+tipo+':'+x.i]?'x':''}"><input type="checkbox" data-t="${tipo}" data-i="${x.i}" ${EST['t:'+tipo+':'+x.i]?'checked':''} aria-label="Tirei ${esc(x.n)}"><span><b>${esc(x.n)}</b><small>${esc(x.m)}</small></span><span class="q">${num(x.e,x.e%1?2:0)} un.</span></li>`).join('')}</ul></details>`}).join('');
  $$('input',$(alvo)).forEach(c=>c.addEventListener('change',e=>{const k='t:'+c.dataset.t+':'+c.dataset.i;EST[k]=e.target.checked;salva();c.closest('li').classList.toggle('x',e.target.checked);
    const d=c.closest('details'),cb=$$('input',d);d.querySelector('small').textContent=`${cb.filter(i=>i.checked).length} de ${cb.length}`}));
}
$('#nTirar').textContent=num(G.tirar.length);$('#nGuardar').textContent=num(G.guardar.length);
grupos(G.tirar,'#lTirar','p');grupos(G.guardar,'#lGuardar','g');
// ---------- pedido ----------
(function(){const por={};G.pedido.forEach(x=>{(por[x.m||'Sem marca']=por[x.m||'Sem marca']||[]).push(x)});
  const ord=Object.keys(por).sort((a,b)=>por[b].length-por[a].length);
  const pri=t=>G.pedido.filter(x=>x.pri===t).length;
  $('#pedNum').innerHTML=[[pri('Repor já'),'repor já: vende bem e acabou',ZCOR.gourmet],[pri('Núcleo a incorporar'),'novos na loja',ZCOR.parede],[pri('Completar o planograma'),'para completar o planograma',ZCOR.lanches]].map(([v,t,c])=>`<div style="background:${c}"><b>${v}</b>${t}</div>`).join('');
  $('#lPedido').innerHTML=ord.map(m=>`<details class="grp"><summary>${esc(m)}<small>${por[m].length} produtos</small></summary><ul class="tl">${por[m].map(x=>`<li><span class="dot ${x.pri==='Repor já'?'d-tirar':x.pri==='Núcleo a incorporar'?'d-novo':'d-pedir'}"></span><span><b>${esc(x.n)}</b><small>${esc(x.pri)} · ${esc(x.lg)}</small></span><span class="q">${x.q} ${esc(x.un)}</span></li>`).join('')}</ul></details>`).join('');
})();
// ---------- busca ----------
const norm=t=>String(t).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
$('#q').addEventListener('input',e=>{const q=norm(e.target.value.trim());if(q.length<2){$('#res').innerHTML='';return}
  const r=IDX.filter(x=>norm(x.it.n+' '+x.it.m+' '+x.it.s).includes(q)).slice(0,40);
  $('#res').innerHTML=r.length?r.map((x,i)=>{const z=Z[x.zi];const onde=x.setor==='Granel'?`Granel · tubo ${x.tubo}`:`${z.nome} · módulo ${x.bi+1} · nível ${x.n}`;const ph=F[x.it.s];
    return `<button data-r="${i}">${ph?`<img src="${ph}" alt="">`:`<span class="ph0" style="background:${corMarca(x.it.m)}"></span>`}<span><b>${esc(x.it.n)}</b><small>${esc(onde)} · ${(ACAO[x.it.a]||ACAO.tem)[0]}</small></span></button>`}).join('')
    :'<p class="sub">Não está no planograma. Se tem na loja, veja a aba "Tirar da gôndola".</p>';
  $$('#res button').forEach(b=>b.addEventListener('click',()=>{const x=r[+b.dataset.r];zona=x.zi;baia=x.bi;location.hash='montar';desenha();abre(x)}));
});
// ---------- início ----------
$$('nav.tabs a').forEach(a=>a.addEventListener('click',()=>{if(a.dataset.v==='montar')desenha()}));
desenha();mostra(location.hash.slice(1)||'inicio');progresso();
})();
</script>'''

doc = PAGINA.replace('__FONTE__', fonte).replace('__DADOS__', json.dumps(G, ensure_ascii=False).replace('</', '<\\/')).replace('__FOTOS__', json.dumps({str(k): v for k, v in fotos.items()}))
out = R / 'kit/pinheiros-guia.html'; out.write_text(doc)
bad = [t for t in ('—', '–') if t in PAGINA]
print(out, round(len(doc.encode()) / 1e6, 2), 'MB;', len(fotos), 'fotos;', 'TRAVESSAO' if bad else 'sem travessão')
