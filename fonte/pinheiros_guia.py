# Guia de montagem de Pinheiros para o time da loja. A planta executiva da loja (R00 de 02/01/2026, folha 02/11) é o mapa:
# cada módulo real é clicável e abre o que vai nele. Vista em 3D da loja montada sobre a mesma planta, com as fotos dos produtos
# nas prateleiras. Módulo a módulo com checklist, o que tirar da gôndola, o pedido e a busca "onde vai este produto?".
# Lê analise/pinheiros_guia.json (gerado por fonte/pinheiros.py). Saída com estoque da loja, fora do Git: kit/pinheiros-guia.html
import base64, io, json, pathlib, sys
import fitz
from PIL import Image
R = pathlib.Path(__file__).resolve().parent.parent
G = json.loads((R / 'analise/pinheiros_guia.json').read_text())
PLANTA = pathlib.Path('/Volumes/hd caique becker/Mac Caique/Projetos/divina-terra-diagnostico/drive/planta-pinheiros-exec.pdf')
# planta: 56,64 pontos por metro; origem na fachada (X) e na parede de suplementos (Y), medida pelas cotas da folha 02/11
X0, Y0, ESC = 315.3, 108.3, 56.64
MX0, MX1, MY0, MY1 = -0.35, 14.5, -0.5, 6.85
pg = fitz.open(PLANTA)[20]
clip = fitz.Rect(X0 + MX0 * ESC, Y0 + MY0 * ESC, X0 + MX1 * ESC, Y0 + MY1 * ESC)
pix = pg.get_pixmap(dpi=165, clip=clip)
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
b = io.BytesIO(); im.save(b, 'JPEG', quality=74); planta = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
sk = {it['s'] for m in G['moveis'] for bay in m.get('bays', []) for sg in bay for n in sg['nv'] for it in n['it']}
VIT = R / 'analise/pinheiros_vitrines.json'  # calendário de vitrines (fonte/pinheiros_vitrines.py)
G['vit'] = json.loads(VIT.read_text()) if VIT.exists() else []
sk |= {it['s'] for m in G['vit'] for sp_ in m['sp'] for it in sp_['it'] if not it['gr']}
fotos = {}
for s in sk:
    f = R / f'assets/produtos/{s}.webp'
    if not f.exists(): continue
    ph = Image.open(f).convert('RGBA'); h = 120; w = max(1, round(ph.width * h / ph.height)); ph = ph.resize((w, h), Image.LANCZOS)
    bb = io.BytesIO(); ph.save(bb, 'WEBP', quality=62); fotos[s] = 'data:image/webp;base64,' + base64.b64encode(bb.getvalue()).decode()
for m in G['moveis']:  # foto do produto solto nos potes do granel
    for t in m.get('tubos', []):
        f = R / f'assets/produtos/granel/{t["s"]}.webp'
        if f.exists(): fotos['g' + str(t['s'])] = 'data:image/webp;base64,' + base64.b64encode(f.read_bytes()).decode()
fonte = 'data:font/ttf;base64,' + base64.b64encode((R / 'assets/fontes/GeneralSans-Variable.ttf').read_bytes()).decode()
G['planta'] = dict(x0=MX0, x1=MX1, y0=MY0, y1=MY1)
def svg_uri(f, de=None, para=None):
    t = f.read_text()
    if de: t = t.replace(de, para)
    return 'data:image/svg+xml;base64,' + base64.b64encode(t.encode()).decode()
LOGO = svg_uri(R / 'assets/logos/dt-horizontal-claro.svg')
LAB = svg_uri(R / 'assets/logos/75lab-logo-lime.svg', '#C0EE4E', '#F6F4F1')
SPRITE = (R / 'fonte/icones.svg').read_text()
hf = Image.open(R / 'assets/img/f53.jpg').convert('RGB'); hf.thumbnail((900, 1200)); bh = io.BytesIO(); hf.save(bh, 'WEBP', quality=68)
HEROI = 'data:image/webp;base64,' + base64.b64encode(bh.getvalue()).decode()
# --publico: versão para o site (repositório público), sem estoque e sem venda em R$ por produto. Grava pinheiros.html na raiz.
PUBLICO = '--publico' in sys.argv
if PUBLICO:
    for m in G['moveis']:
        for bay in m.get('bays', []):
            for sg in bay:
                for nv in sg['nv']:
                    for it in nv['it']: it.pop('e', None)
        for t in m.get('tubos', []): t['e'] = 1 if t['e'] > 0 else 0
    for x in G['tirar'] + G['guardar']: x.pop('e', None)
    for mv in G['vit']:
        for sp_ in mv['sp']:
            for it in sp_['it']:
                for k in ('vm', 'v11', 'vr'): it.pop(k, None)

PAGINA = r'''<title>Pinheiros · planograma da loja</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
<style>
@font-face{font-family:'General Sans';src:url('__FONTE__') format('truetype');font-weight:200 700;font-display:swap}
/* Layout: a planta da loja é a tela principal; cada módulo abre o planograma dele. Cores da Divina Terra; cor de ação separada da cor do setor. */
:root{
  --bg:#F7F5F1;--card:#FFFFFF;--fg:#2B1A14;--muted:#6F5F55;--line:#E4DACD;--aveia:#E5DDD1;--linho:#BCAD99;
  --band:#461D17;--band-fg:#F7F5F1;--accent:#7C381F;--gold:#CA942A;
  --tem:#596D49;--pedir:#C98A1B;--novo:#7C381F;--tirar:#C2452D;--olho:#FBF1DE;--shelf:#8C6A55;--cap:#AC834C;
  --serif:'Source Serif 4',Georgia,'Times New Roman',serif;--sans:'General Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#1B1310;--card:#271C17;--fg:#F2EBE3;--muted:#BBAA9B;--line:#3D2F27;--aveia:#33261F;--linho:#5E4C40;
  --band:#2E1E18;--band-fg:#F2EBE3;--accent:#D8875F;--gold:#E3B14E;
  --tem:#8DAA76;--pedir:#E3A93A;--novo:#D8875F;--tirar:#E26A52;--olho:#3A2D1E;--shelf:#A88972;--cap:#D2AE7C;color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#1B1310;--card:#271C17;--fg:#F2EBE3;--muted:#BBAA9B;--line:#3D2F27;--aveia:#33261F;--linho:#5E4C40;
  --band:#2E1E18;--band-fg:#F2EBE3;--accent:#D8875F;--gold:#E3B14E;
  --tem:#8DAA76;--pedir:#E3A93A;--novo:#D8875F;--tirar:#E26A52;--olho:#3A2D1E;--shelf:#A88972;--cap:#D2AE7C;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:15px/1.45 var(--sans);margin:0}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:30;background:var(--band)}
.w{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3{font-family:var(--sans);font-weight:500;letter-spacing:-.022em;margin:0;text-wrap:balance}
h1 em,h2 em,h3 em{font-family:var(--serif);font-style:italic;font-weight:300;letter-spacing:-.01em;color:var(--accent)}
.ic{width:18px;height:18px;flex:none}
.eb2{display:flex;align-items:center;gap:8px;font-size:12.5px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--cap)}
.eb2 .ic{width:16px;height:16px}
.sec{display:grid;gap:8px;padding-top:10px}
button{font:inherit;color:inherit;cursor:pointer}
:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.topo{background:var(--band);color:var(--band-fg)}
.topo .w{padding-block:18px 26px;display:grid;gap:22px}
.marca{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.marca .lg{height:30px;width:auto;display:block}
.marca .sep{width:1px;height:24px;background:rgba(247,245,241,.28)}
.marca .loja{font-weight:600;font-size:15px;letter-spacing:.02em}
.marca .por{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:12.5px;opacity:.75}
.marca .por img{height:15px;width:auto;display:block}
.heroi{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:28px;align-items:end}
.heroi .ht{display:grid;gap:14px;align-content:end}
.topo .eb2{color:var(--gold)}
.topo h1{font-size:clamp(34px,6vw,60px);line-height:1.02;letter-spacing:-.03em}.topo h1 em{color:var(--gold)}
.topo p{margin:0;max-width:58ch;opacity:.88;font-size:15.5px}
.hf{margin:0;position:relative;border-radius:14px;overflow:hidden;aspect-ratio:4/3;max-width:100%}
.hf img{width:100%;height:100%;object-fit:cover;display:block}
.hf figcaption{position:absolute;left:0;right:0;bottom:0;padding:22px 12px 9px;font-size:12px;background:linear-gradient(transparent,rgba(27,14,10,.75));color:#F2EBE3}
@media(max-width:760px){.heroi{grid-template-columns:1fr;gap:18px}.hf{order:-1;aspect-ratio:16/8}.marca .por{display:none}}
.prog{display:grid;grid-template-columns:auto 1fr;align-items:center;gap:6px 14px;max-width:560px;margin-top:4px}
.prog b{font-size:13.5px;font-weight:600}.prog .bar{grid-column:1/-1;height:8px;border-radius:99px;background:rgba(247,245,241,.16);overflow:hidden}
.prog .bar i{display:block;height:100%;width:0;background:var(--gold);border-radius:99px;transition:width .4s}
.rod{background:var(--band);color:var(--band-fg);margin-top:20px}
.rod .w{padding-block:28px calc(28px + env(safe-area-inset-bottom,0px));display:grid;gap:14px}
.rod .lg{height:26px;width:auto}
.rod p{margin:0;max-width:62ch;font-size:13.5px;opacity:.82;line-height:1.55}
.rod .lab{height:12px;width:auto;vertical-align:-1px;margin:0 2px}
nav.tabs{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--bg);border-bottom:1px solid var(--line)}
nav.tabs .w{display:flex;gap:22px;overflow-x:auto;scrollbar-width:none}
nav.tabs a{flex:none;display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--muted);font-weight:600;font-size:14.5px;padding:15px 0 12px;border-bottom:3px solid transparent}
nav.tabs a:hover{color:var(--fg)}
nav.tabs a.on{color:var(--fg);border-bottom-color:var(--gold)}
nav.tabs a.on .ic{color:var(--accent)}
@media(max-width:760px){nav.tabs .w{gap:4px}nav.tabs a{flex-direction:column;gap:4px;font-size:11.5px;padding:10px 8px 8px;min-width:66px;text-align:center}nav.tabs a .ic{width:21px;height:21px}}
main .w{padding-block:20px 80px}
section.v{display:grid;gap:18px}
.sec+.passos,.sec+.leg,.sec+.regras{margin-top:-2px}
/* fora da aba Loja o topo encolhe: sobra tela para trabalhar */
body.compacto .hf,body.compacto .topo p{display:none}body.compacto .heroi{grid-template-columns:1fr}body.compacto .topo .w{gap:14px;padding-block:14px 18px}body.compacto .topo h1{font-size:clamp(24px,3.4vw,34px)}body.compacto .heroi .ht{gap:10px}section.v[hidden]{display:none}
.h2{font-size:clamp(23px,4.4vw,31px)}
.sub{color:var(--muted);margin:0;max-width:70ch}
.leg{display:flex;flex-wrap:wrap;gap:8px 18px}.leg span{display:inline-flex;align-items:center;gap:8px;font-size:13.5px;font-weight:500}
.dot{width:14px;height:14px;border-radius:50%;flex:none;display:inline-block}
.d-tem{background:var(--tem)}.d-pedir{background:var(--pedir)}.d-novo{background:var(--novo)}.d-livre{background:repeating-linear-gradient(135deg,var(--linho) 0 3px,transparent 3px 6px);border:1px solid var(--linho)}.d-tirar{background:var(--tirar)}
.passos{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.passos div{padding:4px 0;display:grid;gap:8px;align-content:start}
.passos .pn{display:flex;align-items:center;gap:10px;color:var(--accent)}
.passos .pn i{font-style:normal;width:30px;height:30px;border-radius:50%;background:var(--band);color:var(--band-fg);display:grid;place-items:center;font-weight:600;font-size:14px}
.passos .pn .ic{width:24px;height:24px}
.passos b{font-size:16.5px;font-weight:600}.passos p{margin:0;color:var(--muted);font-size:14.5px;line-height:1.5}
.regras{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.regras div{border-radius:12px;padding:16px;background:var(--aveia);display:grid;gap:6px;align-content:start}
.regras .ic{width:22px;height:22px;color:var(--accent)}
.regras b{font-size:17px;font-weight:600;letter-spacing:-.01em}.regras span{font-size:14px;color:var(--muted)}
.bigcards{display:flex;flex-wrap:wrap;border-block:1px solid var(--line)}
.bigcards div{flex:1 1 160px;padding:14px 18px 15px;border-left:1px solid var(--line);display:grid;gap:3px;font-size:13.5px;color:var(--muted);line-height:1.3}
.bigcards div:first-child{border-left:none;padding-left:0}
.bigcards b{font-family:var(--sans);font-size:clamp(30px,4.4vw,42px);font-weight:500;letter-spacing:-.03em;line-height:1;color:var(--k,var(--fg));font-variant-numeric:tabular-nums}
.h3s{font-size:19px;font-weight:600;letter-spacing:-.01em;margin-top:6px}
.nota{font-size:13px;color:var(--muted);margin:0}
/* loja: planta e 3D */
.modo{display:inline-flex;background:var(--aveia);border-radius:99px;padding:4px;gap:4px}
.modo button{border:none;background:none;border-radius:99px;padding:8px 16px;font-weight:600}
.modo button.on{background:var(--band);color:var(--band-fg)}
.planta{background:var(--card);border-radius:14px;padding:10px;overflow-x:auto;box-shadow:0 1px 0 var(--line),0 12px 30px -18px rgba(70,29,23,.35)}
.planta svg{display:block;width:100%;min-width:900px;height:auto}
.planta .bay{cursor:pointer}.planta .bay rect.f{transition:fill-opacity .15s}
.planta .bay:hover rect.f,.planta .bay:focus rect.f{fill-opacity:.9}
.planta .bay.sel rect.f{stroke:var(--gold);stroke-width:.06}
.planta text{font-family:var(--sans);pointer-events:none}
.tres{position:relative;background:var(--card);border-radius:14px;box-shadow:0 12px 30px -18px rgba(70,29,23,.35);overflow:hidden;height:min(72vh,640px)}
.tres canvas{display:block;width:100%;height:100%;touch-action:none}
.tres .cams{position:absolute;left:10px;top:10px;display:flex;gap:6px;flex-wrap:wrap;z-index:2}
.tres .cams button{border:none;border-radius:99px;padding:8px 12px;font-weight:600;font-size:13px;background:var(--band);color:var(--band-fg);opacity:.92}
.tres .dica3d{position:absolute;right:10px;top:12px;z-index:2;font-size:12px;color:var(--muted);background:var(--card);border-radius:99px;padding:5px 10px;opacity:.9}
@media(max-width:600px){.tres .dica3d{top:auto;bottom:10px;left:10px;right:auto}}
.tres .aviso{position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:20px;color:var(--muted)}
.cartao{position:absolute;left:10px;right:10px;bottom:10px;z-index:3;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;display:flex;gap:12px;align-items:center;justify-content:space-between;box-shadow:0 8px 24px rgba(0,0,0,.18)}
.cartao b{display:block}.cartao small{color:var(--muted)}
.cartao button{border:none;border-radius:12px;padding:12px 16px;font-weight:600;background:var(--band);color:var(--band-fg);flex:none}
.legset{display:flex;flex-wrap:wrap;gap:6px 16px}.legset span{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}
/* montar */
.grupos{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;scrollbar-width:thin}
.grupos button{flex:none;border:none;border-bottom:3px solid var(--line);background:none;border-radius:0;padding:8px 4px 9px;margin-right:14px;text-align:left;display:grid;gap:2px;min-width:118px}
.grupos button b{font-size:14px}.grupos button small{color:var(--muted);font-size:12px}
.grupos button.on{border-bottom-color:var(--gold)}.grupos button.on b{color:var(--accent)}
.grupos button.ok small::after{content:" · pronto";color:var(--tem);font-weight:600}
.mod{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:18px;align-items:start}
@media(max-width:860px){.mod{grid-template-columns:1fr}}
.cab{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.cab h3{font-size:clamp(24px,4vw,32px)}.cab .zn{font-size:12.5px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--cap)}
.seta{display:flex;gap:8px}.seta button{width:52px;height:52px;border-radius:50%;border:none;background:var(--band);color:var(--band-fg);font-size:22px;display:grid;place-items:center}
.seta button:disabled{opacity:.3;cursor:default}
.minimapa{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:6px;overflow:hidden}
.minimapa svg{display:block;width:100%;height:auto}
.setores{display:flex;gap:6px;flex-wrap:wrap}.setores span{font-size:13px;font-weight:600;padding:4px 10px;border-radius:99px;background:var(--aveia)}
.movel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:12px 12px 10px;display:grid;gap:8px}
.movel .med{display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}
.estante{display:grid;grid-template-columns:52px minmax(0,1fr)}
.nl{display:grid;align-content:center;justify-items:center;font-size:11px;color:var(--muted);line-height:1.1;text-align:center;border-bottom:4px solid var(--shelf);padding:2px}
.nl b{font-size:18px;color:var(--fg);font-family:var(--serif)}
.nl.olho{background:var(--olho)}.nl.olho span{color:var(--accent);font-weight:600}
.pr{display:flex;border-bottom:4px solid var(--shelf);min-height:84px}
.pr.olho{background:var(--olho)}
.pr.ae{min-height:40px;background:repeating-linear-gradient(135deg,var(--aveia) 0 6px,transparent 6px 12px)}
.pr.ae em{margin:auto;font-size:12px;color:var(--muted);font-style:normal}
.seg{display:flex;flex-direction:column;min-width:0;border-left:2px dashed var(--linho)}.seg:first-child{border-left:none}
.seg .rot{font-size:10.5px;color:var(--muted);padding:2px 4px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.seg .its{flex:1;display:flex;align-items:flex-end;padding:0 2px;gap:1px}
.it{border:none;background:none;padding:0;display:flex;flex-direction:column;align-items:stretch;justify-content:flex-end;height:100%;min-width:0;position:relative}
.it .fr{display:flex;align-items:flex-end;justify-content:center;gap:1px;height:62px}
.it .fr img{flex:1;min-width:0;max-height:62px;object-fit:contain;object-position:bottom}
.it .fr .pk{flex:1;min-width:0;height:52px;border-radius:3px 3px 1px 1px;display:flex;align-items:center;justify-content:center;overflow:hidden;font-size:8.5px;font-weight:600;line-height:1;color:#fff;text-align:center;writing-mode:vertical-rl;transform:rotate(180deg);padding:2px 0}
.it .ac{height:6px;border-radius:2px;margin-top:2px}
.it .nu{position:absolute;top:-2px;left:50%;transform:translateX(-50%);min-width:18px;height:18px;border-radius:99px;font-size:10.5px;font-weight:700;color:#fff;display:grid;place-items:center;padding:0 4px;box-shadow:0 0 0 2px var(--card)}
.livre{flex:1;align-self:stretch;margin:16px 2px 2px;border-radius:4px;background:repeating-linear-gradient(135deg,var(--aveia) 0 5px,transparent 5px 10px);display:grid;place-items:center;font-size:10px;color:var(--muted);min-width:0;text-align:center;padding:2px}
.a-tem{background:var(--tem)}.a-pedir{background:var(--pedir)}.a-novo{background:var(--novo)}
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
.chk{display:grid;gap:8px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px}
.chk label{display:flex;gap:12px;align-items:center;font-size:15.5px;font-weight:500;cursor:pointer;padding:4px 0}
.chk input{width:26px;height:26px;accent-color:var(--tem);flex:none}
.feito{background:var(--tem);color:#fff;border-radius:12px;padding:10px 14px;font-weight:600;text-align:center}
.prox{display:grid;grid-template-columns:1fr 1fr;gap:10px}.prox button{border:none;border-radius:14px;padding:16px;font-weight:600;font-size:16px;background:var(--aveia)}
.prox button.go{background:var(--band);color:var(--band-fg)}.prox button:disabled{opacity:.35;cursor:default}
.tubos{display:grid;grid-template-columns:repeat(auto-fill,minmax(98px,1fr));gap:8px}
.tubos div{border-radius:12px 12px 4px 4px;min-height:96px;padding:8px;display:flex;flex-direction:column;gap:6px;justify-content:space-between;font-size:12.5px;font-weight:600;line-height:1.2;color:#fff}
.tubos img{width:72px;height:72px;border-radius:50%;object-fit:cover;align-self:center;border:3px solid rgba(255,255,255,.85);background:#fff}
.tubos div small{font-weight:500;opacity:.9;font-size:11px}
details.grp{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
details.grp summary{cursor:pointer;padding:12px 14px;font-weight:600;display:flex;justify-content:space-between;gap:10px;list-style:none}
details.grp summary::-webkit-details-marker{display:none}
details.grp summary::after{content:"+";font-size:20px;line-height:1;color:var(--accent)}details.grp[open] summary::after{content:"−"}
details.grp summary small{color:var(--muted);font-weight:500;margin-left:auto}
.tl{list-style:none;margin:0;padding:0}.tl li{display:grid;grid-template-columns:28px minmax(0,1fr) auto;gap:10px;align-items:center;padding:8px 14px;border-top:1px solid var(--line)}
.tl input{width:22px;height:22px;accent-color:var(--tirar)}.tl li.x b{text-decoration:line-through;opacity:.55}
.tl b{font-weight:500;display:block}.tl small{color:var(--muted);font-size:12.5px}.tl .q{font-weight:700;font-size:15px;white-space:nowrap}
.busca input{width:100%;font:inherit;font-size:17px;padding:14px 16px;border-radius:14px;border:2px solid var(--line);background:var(--card);color:var(--fg)}
.res{display:grid;gap:8px}.res button{border:1px solid var(--line);background:var(--card);border-radius:12px;padding:10px 12px;text-align:left;display:grid;grid-template-columns:46px minmax(0,1fr);gap:10px;align-items:center}
.res img,.res .ph0{width:46px;height:46px;object-fit:contain;border-radius:6px;background:var(--aveia)}
.res b{display:block;font-weight:600}.res small{color:var(--muted)}
.folha::before{content:"";justify-self:center;width:44px;height:5px;border-radius:99px;background:var(--line);margin-top:-6px}
.folha{position:fixed;inset:auto 0 0 0;z-index:40;background:var(--card);border-radius:20px 20px 0 0;box-shadow:0 -10px 40px rgba(0,0,0,.25);padding:16px max(16px,env(safe-area-inset-right,0px)) calc(18px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));max-width:620px;margin:0 auto;display:grid;gap:12px}
.folha .tp{display:grid;grid-template-columns:96px minmax(0,1fr);gap:14px;align-items:center}
.folha img,.folha .ph0{width:96px;height:110px;object-fit:contain;border-radius:10px;background:var(--aveia)}
.folha h3{font-size:22px}.folha .mk{color:var(--muted);font-size:14px}
.folha .acao{border-radius:12px;padding:12px 14px;color:#fff;font-weight:600;font-size:15.5px}
.folha dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:0;font-size:14.5px}.folha dt{color:var(--muted)}.folha dd{margin:0;font-weight:500}
.folha .fx{border:none;background:var(--aveia);border-radius:12px;padding:12px;font-weight:600}
.veu{position:fixed;inset:0;z-index:35;background:rgba(20,12,9,.45)}
/* vitrines */
.ano{display:grid;grid-template-columns:repeat(13,minmax(84px,1fr));gap:6px;overflow-x:auto;padding:2px 2px 6px;scrollbar-width:thin}
.ano button{border:1px solid var(--line);border-top:6px solid var(--c);background:var(--card);border-radius:12px;padding:7px 9px 9px;text-align:left;display:grid;gap:2px;align-content:start}
.ano button b{font-size:14.5px}.ano button small{font-size:11.5px;color:var(--muted);line-height:1.2}
.ano button.on{background:var(--c);border-color:var(--c);color:#fff}.ano button.on small{color:#fff;opacity:.88}
.ano .ag{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--gold)}.ano button.on .ag{color:#fff}
.vt-cab{border-radius:18px;padding:18px 18px 16px;color:#fff;background:var(--c);display:grid;gap:12px}
.vt-cab h3{font-size:clamp(26px,5vw,40px);line-height:1.05}
.vt-dts{display:flex;flex-wrap:wrap;gap:6px}.vt-dts span{background:rgba(255,255,255,.17);border-radius:99px;padding:5px 12px;font-size:13.5px}
.vt-dts em{font-style:normal;opacity:.8;margin-left:6px;font-size:11.5px;text-transform:uppercase;letter-spacing:.05em}
.cron{display:grid;grid-template-columns:repeat(4,1fr)}
.cron div{display:grid;gap:1px;justify-items:center;text-align:center;font-size:12.5px;line-height:1.2;position:relative;padding:22px 4px 0}
.cron div::before{content:"";position:absolute;top:7px;left:0;right:0;height:3px;background:rgba(255,255,255,.35)}
.cron div:first-child::before{left:50%}.cron div:last-child::before{right:50%}
.cron div::after{content:"";position:absolute;top:1px;left:50%;width:15px;height:15px;margin-left:-7.5px;border-radius:50%;background:#fff;box-shadow:0 0 0 3px var(--c)}
.cron b{font:400 19px var(--serif)}
.fach{border-radius:18px;overflow:hidden;border:1px solid var(--line);background:#3d2c25}
.letreiro{background:#461D17;color:#F7F5F1;text-align:center;padding:11px;font-weight:600;font-size:15px;letter-spacing:.34em}
.vidros{display:flex;gap:10px;padding:12px 12px 0}
.vid{position:relative;border-radius:6px 6px 0 0;background:var(--vbg);box-shadow:inset 0 0 0 4px #2B1A14;min-height:320px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden}
.vid::after{content:"";position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.38) 0 18%,transparent 18% 40%,rgba(255,255,255,.16) 40% 46%,transparent 46%);pointer-events:none}
.adesivo{margin:16px 14px 0;text-align:center;font:italic 400 clamp(19px,2.6vw,27px)/1.12 var(--serif);color:var(--c);text-wrap:balance}
.vid.preta .adesivo{color:#F2EBE3}
.degraus{display:grid;gap:0;padding:12px 12px 0;margin-top:auto}
.dg{display:flex;justify-content:center;align-items:flex-end;gap:6px;padding:0 6px;border-bottom:9px solid #9C7A5E;margin:0 auto;width:100%}
.dg:nth-child(1){width:70%}.dg:nth-child(2){width:86%}
.vp{border:none;background:none;padding:0;position:relative;display:flex;align-items:flex-end;justify-content:center;flex:0 1 auto;min-width:0}
.vp img{height:78px;max-width:96px;object-fit:contain;object-position:bottom;filter:drop-shadow(0 3px 4px rgba(0,0,0,.18))}
.dg:nth-child(1) .vp img{height:64px}.dg:last-child .vp img{height:88px}
.vp.gr img{width:74px;height:74px;max-width:none;border-radius:50%;object-fit:cover;border:5px solid #E5DDD1;box-shadow:0 4px 0 #9C7A5E,0 6px 10px rgba(0,0,0,.18);filter:none}
.dg:nth-child(1) .vp.gr img{width:62px;height:62px}.mesa-il .vp.gr img,.ponta-il .vp.gr img{width:56px;height:56px;border-width:4px}
.vp .pk{width:52px;height:70px;border-radius:4px;color:#fff;font-size:9px;display:grid;place-items:center;text-align:center;padding:2px}
.vp .nu{position:absolute;top:-6px;left:-4px;min-width:20px;height:20px;border-radius:99px;font:700 11px/20px var(--sans);font-style:normal;color:#fff;background:#461D17;box-shadow:0 0 0 2px #fff;text-align:center;padding:0 4px}
.vp em{position:absolute;bottom:2px;left:50%;transform:translateX(-50%);font:700 9.5px var(--sans);font-style:normal;text-transform:uppercase;letter-spacing:.04em;background:var(--pedir);color:#fff;border-radius:99px;padding:1px 6px;white-space:nowrap}
.vrot{position:relative;z-index:1;background:#2B1A14;color:#F2EBE3;font-size:12.5px;padding:7px 10px;display:flex;gap:8px;align-items:center}
.vrot i,.tt i{font-style:normal;width:22px;height:22px;border-radius:50%;background:var(--gold);color:#2B1A14;font-weight:700;display:grid;place-items:center;flex:none}
.porta{flex:.75;border-radius:6px 6px 0 0;background:linear-gradient(90deg,#2B1A14,#4a382f 50%,#2B1A14);box-shadow:inset 0 0 0 4px #2B1A14;position:relative;display:grid;place-items:end center;padding-bottom:16px;color:#F2EBE3;font-size:12px;letter-spacing:.2em;text-transform:uppercase}
.porta::before{content:"";position:absolute;right:16%;top:46%;width:5px;height:42px;border-radius:3px;background:#CA942A}
.calcada{height:16px;background:repeating-linear-gradient(90deg,#BCAD99 0 46px,#a8977f 46px 48px)}
@media(max-width:720px){.vidros{flex-direction:column;padding:10px}.porta{display:none}.vid{min-height:250px;border-radius:6px}.vp img{height:66px;max-width:78px}.dg:last-child .vp img{height:74px}.dg:nth-child(1) .vp img{height:56px}}
.vt-g{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
@media(max-width:980px){.vt-g{grid-template-columns:1fr 1fr}}@media(max-width:640px){.vt-g{grid-template-columns:1fr}}
.cartao2{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;display:grid;gap:10px;align-content:start}
.tt{display:flex;gap:9px;align-items:center}.tt b{font-size:15px}.tt small{display:block;color:var(--muted);font-size:12.5px;font-weight:400}
.cartao2 h4{margin:0;font:400 22px/1.1 var(--serif)}
.mesa-il{display:grid;justify-items:center;padding-top:6px}
.mesa-il .prods{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-end;gap:4px 6px;padding:0 8px;width:100%}
.mesa-il .vp img{height:58px;max-width:70px}
.tampo{width:100%;height:16px;border-radius:8px;background:linear-gradient(#d6c1a6,#b39577);box-shadow:0 4px 0 #8C6A55}
.pes{display:flex;justify-content:space-between;width:78%}.pes i{width:9px;height:46px;background:#8C6A55;border-radius:0 0 3px 3px}
.ponta-il{border:5px solid #8C6A55;border-top:none;border-radius:0 0 6px 6px;background:var(--olho);display:grid}
.testeira{background:var(--c);color:#fff;text-align:center;font-weight:600;font-size:14px;padding:7px;border-radius:6px 6px 0 0}
.ponta-il .prat{display:flex;justify-content:center;align-items:flex-end;gap:5px;min-height:74px;padding:6px 6px 0;border-bottom:7px solid #8C6A55}
.ponta-il .vp img{height:58px;max-width:64px}
.mini2 svg{display:block;width:100%;height:auto;border-radius:10px}
.vt-g2{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:14px;align-items:start}
@media(max-width:860px){.vt-g2{grid-template-columns:1fr}}
.ln li .tag{font-size:11.5px;font-weight:600;border-radius:99px;padding:2px 8px;color:#fff;background:var(--tem)}.ln li .tag.pd{background:var(--pedir)}
.ln li img.th{width:34px;height:34px;object-fit:contain}
.est3{display:grid;gap:8px}.est3 div{border-left:5px solid var(--k);background:var(--card);border-radius:8px;padding:8px 12px;font-size:14px}.est3 b{display:block;color:var(--k);font-size:12.5px}
.peso{display:flex;height:22px;border-radius:6px;overflow:hidden;font-size:11.5px;font-weight:700;color:#fff}.peso span{display:grid;place-items:center}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<header class="topo"><svg width="0" height="0" style="position:absolute" aria-hidden="true">__SPRITE__</svg><div class="w">
  <div class="marca"><img class="lg" src="__LOGO__" alt="Divina Terra"><span class="sep"></span><span class="loja">Pinheiros</span><span class="por">Guia da loja por <img src="__LAB__" alt="75 LAB"></span></div>
  <div class="heroi">
    <div class="ht">
      <span class="eb2"><svg class="ic"><use href="#i-gondola"/></svg>Piloto do planograma · dezembro de 2026</span>
      <h1>A loja nova, <em>módulo a módulo</em></h1>
      <p>Toque num móvel da planta para ver o que vai nele. Monte um módulo por vez e marque quando terminar. Cada foto é uma frente, e a cor embaixo do produto diz o que fazer.</p>
      <div class="prog"><b id="pgTxt">0 módulos montados</b><div class="bar"><i id="pgBar"></i></div></div>
    </div>
    <figure class="hf"><img src="__HEROI__" alt="Corredor da loja de Pinheiros, com as gôndolas e a parede de suplementos"><figcaption>Pinheiros, na visita de 14/10/2026</figcaption></figure>
  </div>
</div></header>
<nav class="tabs" aria-label="Partes do guia"><div class="w">
  <a href="#loja" data-v="loja"><svg class="ic"><use href="#i-mapa"/></svg><span>Loja</span></a><a href="#montar" data-v="montar"><svg class="ic"><use href="#i-gondola"/></svg><span>Montar</span></a><a href="#vitrines" data-v="vitrines"><svg class="ic"><use href="#i-loja"/></svg><span>Vitrines</span></a><a href="#inicio" data-v="inicio"><svg class="ic"><use href="#i-livro"/></svg><span>Como montar</span></a>
  <a href="#tirar" data-v="tirar"><svg class="ic"><use href="#i-pacote"/></svg><span>Tirar</span></a><a href="#pedido" data-v="pedido"><svg class="ic"><use href="#i-caminhao"/></svg><span>Pedido</span></a><a href="#buscar" data-v="buscar"><svg class="ic"><use href="#i-busca"/></svg><span>Onde vai?</span></a>
</div></nav>
<main><div class="w">

<section class="v" id="v-loja">
  <div class="cab"><div class="sec"><span class="eb2"><svg class="ic"><use href="#i-mapa"/></svg>Planta da loja · 93,53 m²</span><h2 class="h2">Pinheiros, <em>como ela é</em></h2><p class="sub">Cada móvel está pintado com o setor que vai nele. Toque num módulo para abrir o planograma.</p></div>
    <div class="modo" role="tablist" aria-label="Vista"><button id="mPl" class="on" role="tab">Planta</button><button id="m3d" role="tab">3D</button></div></div>
  <div id="boxPlanta" class="planta"><svg id="svgPlanta" role="img" aria-label="Planta da loja de Pinheiros com os módulos clicáveis"></svg></div>
  <div id="box3d" class="tres" hidden><div class="cams"><button data-c="geral">A loja toda</button><button data-c="entrada">Entrando</button><button data-c="cima">De cima</button><button data-c="fundo">Do caixa</button></div><div class="dica3d">Arraste para girar · dois dedos para aproximar · toque num móvel</div><div class="aviso" id="aviso3d">Carregando a loja em 3D…</div></div>
  <div class="legset" id="legSet"></div>
  <p class="nota">Planta do projeto executivo (Arquitetura de Consumo, R00 de 02/01/2026, folha 02/11), conferida com as fotos da visita de 14/10. A entrada fica à esquerda. Arraste para o lado no celular. Confira as medidas com trena antes de montar.</p>
</section>

<section class="v" id="v-montar" hidden>
  <div class="grupos" id="grupos" role="tablist" aria-label="Móveis da loja"></div>
  <div id="palco"></div>
</section>

<section class="v" id="v-vitrines" hidden>
  <div class="sec"><span class="eb2"><svg class="ic"><use href="#i-calendario"/></svg>Dezembro de 2026 a dezembro de 2027</span><h2 class="h2">Uma vitrine <em>por mês</em></h2><p class="sub">Um tema por mês, ligado às datas da rede. Para cada mês: o que vai nas duas vitrines, na mesa do mês e na ponta da entrada, com a data de montar e de desmontar. Toque num mês e num produto.</p></div>
  <div class="ano" id="ano" role="tablist" aria-label="Meses"></div>
  <div id="mesv" style="display:grid;gap:16px"></div>
</section>

<section class="v" id="v-inicio" hidden>
  <div class="sec"><span class="eb2"><svg class="ic"><use href="#i-livro"/></svg>Antes de começar</span><h2 class="h2">Como <em>montar</em></h2></div>
  <div class="passos">
    <div><span class="pn"><i>1</i><svg class="ic"><use href="#i-regua"/></svg></span><b>Meça com trena</b><p>Cada módulo tem a medida da planta: 0,80 ou 1,10 m na parede, 0,90 ou 1,30 m na gôndola. Se for diferente, avise.</p></div>
    <div><span class="pn"><i>2</i><svg class="ic"><use href="#i-pacote"/></svg></span><b>Tire o que sai</b><p>Na aba "Tirar da gôndola" está o que não volta para a prateleira. Separe antes de montar.</p></div>
    <div><span class="pn"><i>3</i><svg class="ic"><use href="#i-camadas"/></svg></span><b>Monte de cima para baixo</b><p>Um módulo por vez, nível 1 primeiro. Esvazie, limpe e arrume pela foto.</p></div>
    <div><span class="pn"><i>4</i><svg class="ic"><use href="#i-tag"/></svg></span><b>Etiqueta e foto</b><p>Etiqueta de preço em cada produto e uma foto do módulo pronto para o grupo.</p></div>
  </div>
  <div class="sec"><span class="eb2"><svg class="ic"><use href="#i-olho"/></svg>Legenda</span><h2 class="h2">O que cada <em>cor</em> quer dizer</h2></div>
  <div class="leg"><span><i class="dot d-tem"></i>Já tem na loja: pegue e arrume aqui</span><span><i class="dot d-pedir"></i>Chega no pedido: deixe o espaço e a etiqueta</span><span><i class="dot d-novo"></i>Novo na loja: chega no pedido</span><span><i class="dot d-livre"></i>Espaço livre da loja</span></div>
  <div class="sec"><span class="eb2"><svg class="ic"><use href="#i-regras"/></svg>Exposição</span><h2 class="h2">Quatro regras <em>de ouro</em></h2></div>
  <div class="regras">
    <div><svg class="ic"><use href="#i-olho"/></svg><b>Nos olhos, o que mais vende</b><span>Níveis 3 e 4, marcados em amarelo no desenho.</span></div>
    <div><svg class="ic"><use href="#i-balanca"/></svg><b>Pesado embaixo</b><span>Pote acima de 500 g só nos níveis 5 e 6.</span></div>
    <div><svg class="ic"><use href="#i-selo"/></svg><b>Marca junta, líder no meio</b><span>Os produtos da mesma marca ficam lado a lado.</span></div>
    <div><svg class="ic"><use href="#i-grade"/></svg><b>Uma prateleira, um tipo</b><span>Cada prateleira tem um tipo de produto e um tamanho.</span></div>
  </div>
  <div class="bigcards" id="numeros"></div>
</section>

<section class="v" id="v-tirar" hidden>
  <div class="sec"><span class="eb2"><svg class="ic"><use href="#i-pacote"/></svg>Antes de montar</span><h2 class="h2">O que <em>sai</em> da gôndola</h2><p class="sub">Faça isto antes de montar. Marque cada produto quando tirar.</p></div>
  <div class="bigcards"><div style="--k:var(--tirar)"><b id="nTirar">0</b>parados: não vendem desde julho</div><div style="--k:var(--muted)"><b id="nGuardar">0</b>ainda vendem, mas ficaram sem lugar</div></div>
  <h3 class="h3s">Parados: levar para a mesa de oferta ou para transferência</h3>
  <p class="sub">Não repor. Não precisa queimar preço: a rede decide se vão para outra loja.</p>
  <div class="lista" id="lTirar"></div>
  <h3 class="h3s">Ainda vendem: guardar no estoque</h3>
  <p class="sub">Volta para a prateleira quando abrir espaço livre no setor. Quando acabar, não repor.</p>
  <div class="lista" id="lGuardar"></div>
</section>

<section class="v" id="v-pedido" hidden>
  <div class="sec"><span class="eb2"><svg class="ic"><use href="#i-caminhao"/></svg>Pedido para a rede</span><h2 class="h2">O que <em>chega</em> no pedido</h2></div>
  <p class="sub">Produtos do planograma sem estoque ou com pouco. Na prateleira, deixe o espaço e a etiqueta: quando chegar, é só colocar.</p>
  <div class="bigcards" id="pedNum"></div>
  <div class="lista" id="lPedido"></div>
</section>

<section class="v" id="v-buscar" hidden>
  <div class="sec"><span class="eb2"><svg class="ic"><use href="#i-busca"/></svg>Busca</span><h2 class="h2">Onde vai <em>este produto?</em></h2></div>
  <div class="busca"><label for="q" class="sub">Digite o nome, a marca ou o código do produto</label><input id="q" type="search" placeholder="Ex.: creatina, Essential, 886" autocomplete="off"></div>
  <div class="res" id="res"></div>
</section>
</div></main>
<footer class="rod"><div class="w">
  <img class="lg" src="__LOGO__" alt="Divina Terra">
  <p>Guia de montagem da Divina Terra Pinheiros, feito pela <img class="lab" src="__LAB__" alt="75 LAB"> com a planta executiva da loja (R00, folha 02/11), o estoque de 12/11 e a venda de julho a setembro de 2026. O que você marca fica salvo só neste aparelho.</p>
</div></footer>
<div id="folha" hidden></div>

<script type="application/json" id="dados">__DADOS__</script>
<script type="application/json" id="fotos">__FOTOS__</script>
<script type="application/json" id="planta">"__PLANTA__"</script>
<script>
(function(){
'use strict';
const G=JSON.parse(document.getElementById('dados').textContent);
const F=JSON.parse(document.getElementById('fotos').textContent);
const PLANTA=JSON.parse(document.getElementById('planta').textContent);
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=t=>String(t==null?'':t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const num=(v,c=0)=>Number(v).toLocaleString('pt-BR',{minimumFractionDigits:c,maximumFractionDigits:c});
const NIV={1:'Alto',2:'Alto',3:'Olhos',4:'Olhos',5:'Mão',6:'Baixo'};
const ACAO={tem:['Já tem na loja','Pegue no estoque e arrume aqui.'],pedir:['Chega no pedido','Deixe o espaço e a etiqueta. Quando chegar, coloque aqui.'],novo:['Novo na loja','Produto essencial da rede que a loja ainda não tinha. Chega no pedido.']};
const COR={'Proteínas':'#7C381F','Creatina':'#A0482A','Vitaminas':'#C0673C','Ômegas':'#D08752','Colágeno':'#C98F78','Imunidade':'#A86E50','Bem-Estar':'#8C4F3A','Intestino':'#B07355','Longevidade':'#6E3B2A',
  'Performance':'#596D49','Cafés funcionais':'#7E8F5C','Peso':'#95A97D','Barras e snacks':'#CA942A','Sem Glúten':'#AC834C','Gourmet':'#461D17','Chás':'#6B7E4E','Granel':'#8C6A55'};
const FAM={'Castanhas e frutas secas':'#7C381F','Grãos, cereais e farinhas':'#9C8770','Sementes e temperos':'#596D49','Chás e snacks':'#B07F22'};
const PAL=['#7C381F','#596D49','#AC834C','#461D17','#8C6A55','#6B7E4E','#9A4A2A','#B07F22'];
const corMarca=m=>{let h=0;for(const c of String(m))h=(h*31+c.charCodeAt(0))>>>0;return PAL[h%PAL.length]};
const MV=G.moveis;
// paradas na ordem do percurso: parede, gôndolas, encapsulados, lado direito
const ST=[];MV.forEach((m,mi)=>{if(m.grupo==='granel')ST.push({mi,bi:0,gr:true});else m.bays.forEach((_,bi)=>ST.push({mi,bi}))});
const GRUPOS=[['Parede de suplementos',m=>m.grupo==='parede'],['Gôndola 1',m=>m.id.startsWith('G1')],['Gôndola 2',m=>m.id.startsWith('G2')],['Gôndola 3',m=>m.id.startsWith('G3')],['Gôndola 4',m=>m.id.startsWith('G4')],
  ['Encapsulados',m=>m.grupo==='fundo'],['Chás e Gourmet',m=>m.grupo==='direita'],['Granel',m=>m.grupo==='granel']];
const grupoDe=si=>GRUPOS.findIndex(([_,f])=>f(MV[ST[si].mi]));
const setoresDe=st=>st.gr?['Granel']:[...new Set(MV[st.mi].bays[st.bi].map(s=>s.c))];
const nomeSt=st=>{const m=MV[st.mi];return m.bays&&m.bays.length>1?`${m.nome}, módulo ${st.bi+1}`:m.nome};
const larguraSt=st=>{const m=MV[st.mi];if(st.gr)return m.x1-m.x0;return MV[st.mi].bays[st.bi].reduce((a,s)=>a+s.w,0)/100+0.04};
// índice para busca
const IDX=[];ST.forEach((st,si)=>{if(st.gr){MV[st.mi].tubos.forEach((t,k)=>IDX.push({si,it:{s:t.s,n:t.n,m:'A granel',f:1,a:t.e>0?'tem':'pedir',e:t.e,p:0},n:0,rot:t.fam,setor:'Granel',tubo:MV[st.mi].k0+k+1}));return}
  MV[st.mi].bays[st.bi].forEach(sg=>sg.nv.forEach(n=>n.it.forEach(it=>IDX.push({si,it,n:n.n,rot:n.r,setor:sg.c}))))});
// progresso guardado só neste aparelho
let EST={};try{EST=JSON.parse(localStorage.getItem('pin-plano-v2')||'{}')}catch(e){EST={}}
const salva=()=>{try{localStorage.setItem('pin-plano-v2',JSON.stringify(EST))}catch(e){}};
const chave=si=>MV[ST[si].mi].id+'-'+ST[si].bi;
const pronto=si=>!!(EST[chave(si)]&&EST[chave(si)].montado);
function progresso(){
  const ok=ST.filter((_,si)=>pronto(si)).length;
  $('#pgTxt').textContent=`${ok} de ${ST.length} módulos montados`;$('#pgBar').style.width=(ok/ST.length*100)+'%';
  $$('#grupos button').forEach((b,gi)=>{const sis=ST.map((_,si)=>si).filter(si=>grupoDe(si)===gi);const n=sis.filter(pronto).length;b.querySelector('small').textContent=`${n} de ${sis.length} prontos`;b.classList.toggle('ok',n===sis.length&&n>0)});
  desenhaPlanta();
}
const VIS=['loja','montar','vitrines','inicio','tirar','pedido','buscar'];
function mostra(v){if(!VIS.includes(v))v='loja';document.body.classList.toggle('compacto',v!=='loja');VIS.forEach(x=>{$('#v-'+x).hidden=x!==v});$$('nav.tabs a').forEach(a=>a.classList.toggle('on',a.dataset.v===v));if(v==='montar')desenha();if(v==='vitrines')desenhaV();}
window.addEventListener('hashchange',()=>{mostra(location.hash.slice(1));window.scrollTo(0,0)});
// ---------- legenda de setores ----------
$('#legSet').innerHTML=Object.entries(COR).map(([k,v])=>`<span><i class="dot" style="background:${v}"></i>${esc(k)}</span>`).join('');
// ---------- planta ----------
const P=G.planta;
function retangulos(m,bi){ // retângulo de cada módulo dentro do móvel, na planta
  if(m.grupo==='granel'||!m.bays)return[{x:m.x0,y:m.y0,w:m.x1-m.x0,h:m.y1-m.y0}];
  const tot=m.bays.reduce((a,b)=>a+b.reduce((s,x)=>s+x.w,0),0);let acc=0;const out=[];
  m.bays.forEach(b=>{const wb=b.reduce((s,x)=>s+x.w,0)/tot;if(m.grupo==='fundo')out.push({x:m.x0,y:m.y0+acc*(m.y1-m.y0),w:m.x1-m.x0,h:wb*(m.y1-m.y0)});else out.push({x:m.x0+acc*(m.x1-m.x0),y:m.y0,w:wb*(m.x1-m.x0),h:m.y1-m.y0});acc+=wb});
  return bi==null?out:[out[bi]];
}
let selSt=null;
function desenhaPlanta(){
  const svg=$('#svgPlanta');const W=P.x1-P.x0,H=P.y1-P.y0;
  svg.setAttribute('viewBox',`${P.x0} ${P.y0} ${W} ${H}`);
  let s=`<image href="${PLANTA}" x="${P.x0}" y="${P.y0}" width="${W}" height="${H}" preserveAspectRatio="none"/>`;
  ST.forEach((st,si)=>{const m=MV[st.mi];const r=retangulos(m,st.gr?null:st.bi)[0];const sets=setoresDe(st);
    const partes=st.gr?[{c:'Granel',w:1}]:m.bays[st.bi];const tw=partes.reduce((a,p)=>a+p.w,0);let acc=0;
    let fill='';partes.forEach(p=>{const fw=p.w/tw;const rr=m.grupo==='fundo'?{x:r.x,y:r.y+acc*r.h,w:r.w,h:fw*r.h}:{x:r.x+acc*r.w,y:r.y,w:fw*r.w,h:r.h};acc+=fw;
      const vt=m.grupo==='fundo',tx=st.gr?m.nome:p.c,lx=rr.x+rr.w/2,ly=rr.y+rr.h/2,fz=Math.min(.19,(vt?rr.h:rr.w)/Math.max(4,tx.length)*1.45,(vt?rr.w:rr.h)*.62);
      fill+=`<rect class="f" x="${rr.x}" y="${rr.y}" width="${rr.w}" height="${rr.h}" fill="${COR[p.c]||'#8C6A55'}" fill-opacity=".74" stroke="#fff" stroke-width=".025"/>
        <text x="${lx}" y="${ly+fz*.36}" text-anchor="middle" font-size="${fz}" font-weight="700" fill="#fff" ${vt?`transform="rotate(-90 ${lx} ${ly})"`:''}>${esc(tx)}</text>`});
    const ok=pronto(si);const rot=st.gr?m.nome:sets.join(' + ');
    s+=`<g class="bay${selSt===si?' sel':''}" tabindex="0" role="button" data-si="${si}" aria-label="${esc(nomeSt(st))}: ${esc(rot)}">${fill}
      ${ok?`<circle cx="${r.x+r.w-.12}" cy="${r.y+.12}" r=".11" fill="var(--tem)" stroke="#fff" stroke-width=".02"/><path d="M${r.x+r.w-.17} ${r.y+.12}l.04 .04l.08-.08" stroke="#fff" stroke-width=".03" fill="none"/>`:''}</g>`;
  });
  // pontas e mesa do mês, para orientar
  G.obj.filter(o=>o.t==='ponta'||o.t==='mesames').forEach(o=>{s+=`<rect x="${o.x0}" y="${o.y0}" width="${o.x1-o.x0}" height="${o.y1-o.y0}" fill="${o.t==='ponta'?'#CA942A':'#FBF1DE'}" fill-opacity="${o.t==='ponta'?.85:.9}" stroke="#CA942A" stroke-width=".03" ${o.t==='mesames'?'stroke-dasharray=".08 .06" rx=".2"':''}/>`;
    if(o.t==='mesames')s+=`<text x="${(o.x0+o.x1)/2}" y="${(o.y0+o.y1)/2+.06}" text-anchor="middle" font-size=".17" font-weight="700" fill="#461D17">Mesa do mês</text>`});
  s+=`<text x="${P.x0+.15}" y="${2.1}" font-size=".2" font-weight="700" fill="#461D17" transform="rotate(-90 ${P.x0+.15} 2.1)">ENTRADA</text>`;
  svg.innerHTML=s;
  $$('.bay',svg).forEach(g=>{const go=()=>abreSt(+g.dataset.si);g.addEventListener('click',go);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}})});
}
function abreSt(si){cur=si;selSt=si;location.hash='montar';mostra('montar');window.scrollTo(0,0)}
// ---------- montar ----------
let cur=0;
try{const u=+localStorage.getItem('pin-plano-pos');if(u>=0&&u<ST.length)cur=u}catch(e){}
$('#grupos').innerHTML=GRUPOS.map(([n],gi)=>`<button role="tab" data-g="${gi}"><b>${esc(n)}</b><small></small></button>`).join('');
$$('#grupos button').forEach(b=>b.addEventListener('click',()=>{const gi=+b.dataset.g;cur=ST.findIndex((_,si)=>grupoDe(si)===gi);desenha();b.scrollIntoView({inline:'center',block:'nearest'})}));
function tile(it,k,larg){const f=Math.max(1,it.f);const ph=F[it.s];
  const fr=Array.from({length:f},()=>ph?`<img src="${ph}" alt="">`:`<span class="pk" style="background:${corMarca(it.m)}">${esc(it.m)}</span>`).join('');
  return `<button class="it" style="flex:0 0 ${larg}%" data-k="${k}" aria-label="${k}. ${esc(it.n)}"><span class="fr">${fr}</span><span class="ac a-${it.a}"></span><span class="nu a-${it.a}">${k}</span></button>`}
function miniMapa(si){const st=ST[si];const m=MV[st.mi];const r=retangulos(m,st.gr?null:st.bi)[0];
  return `<div class="minimapa"><svg viewBox="${P.x0} ${P.y0} ${P.x1-P.x0} ${P.y1-P.y0}" aria-label="Onde fica este módulo"><image href="${PLANTA}" x="${P.x0}" y="${P.y0}" width="${P.x1-P.x0}" height="${P.y1-P.y0}" preserveAspectRatio="none" opacity=".55"/>
    <rect x="${r.x-.12}" y="${r.y-.12}" width="${r.w+.24}" height="${r.h+.24}" fill="#CA942A" fill-opacity=".85" stroke="#461D17" stroke-width=".06" rx=".06"/><circle cx="${r.x+r.w/2}" cy="${r.y+r.h/2}" r=".45" fill="none" stroke="#CA942A" stroke-width=".08"/></svg></div>`}
function desenha(){
  try{localStorage.setItem('pin-plano-pos',String(cur))}catch(e){}
  const gi=grupoDe(cur);$$('#grupos button').forEach((b,i)=>{b.classList.toggle('on',i===gi);b.setAttribute('aria-selected',i===gi)});
  const st=ST[cur],m=MV[st.mi],p=$('#palco'),key=chave(cur),stt=EST[key]||{};
  const anda=d=>{cur=Math.max(0,Math.min(ST.length-1,cur+d));selSt=cur;desenha();$('#v-montar').scrollIntoView({block:'start'})};
  const cab=`<div class="cab"><div><div class="zn">Parada ${cur+1} de ${ST.length} · ${esc(GRUPOS[gi][0])}</div><h3>${esc(nomeSt(st))}</h3></div>
    <div class="seta"><button id="ant" aria-label="Módulo anterior" ${cur===0?'disabled':''}>‹</button><button id="seg" aria-label="Próximo módulo" ${cur===ST.length-1?'disabled':''}>›</button></div></div>`;
  const checks=(a,b,c)=>`<div class="chk"><b>Checklist deste módulo</b>
      <label><input type="checkbox" id="c1" ${stt.limpo?'checked':''}> ${a}</label><label><input type="checkbox" id="c2" ${stt.montado?'checked':''}> ${b}</label><label><input type="checkbox" id="c3" ${stt.foto?'checked':''}> ${c}</label>
      ${stt.montado?'<div class="feito">Módulo pronto. Muito bem!</div>':''}</div>`;
  const prox=`<div class="prox"><button id="ant2" ${cur===0?'disabled':''}>‹ Anterior</button><button class="go" id="seg2" ${cur===ST.length-1?'disabled':''}>${cur<ST.length-1?'Próximo módulo ›':'Fim da montagem'}</button></div>`;
  if(st.gr){
    const t=m.tubos.map((x,k)=>`<div style="background:${FAM[x.fam]||'#8C6A55'}">${F['g'+x.s]?`<img src="${F['g'+x.s]}" alt="">`:''}<span>${m.k0+k+1}. ${esc(x.n)}</span><small>${esc(x.fam)}${x.e>0?'':' · pedido'}</small></div>`).join('');
    p.innerHTML=`<div class="mod"><div style="display:grid;gap:12px;min-width:0">${cab}${miniMapa(cur)}<p class="sub">${esc(m.nota)} Na ordem, por família: castanhas e frutas secas na altura dos olhos.</p>
      <div class="leg">${Object.entries(FAM).map(([k,v])=>`<span><i class="dot" style="background:${v}"></i>${esc(k)}</span>`).join('')}</div><div class="tubos">${t}</div></div>
      <div style="display:grid;gap:12px;min-width:0">${checks('Limpei os potes e os dispensers','Coloquei na ordem, com etiqueta de preço','Placa de granel visível da porta e potinho de prova')}${prox}</div></div>`;
  }else{
    const b=m.bays[st.bi];const itens=[];let k=0;
    const niveis=[1,2,3,4,5,6].map(n=>{const linha=b.map(sg=>{const nv=sg.nv.find(x=>x.n===n)||{it:[],r:''};return{sg,nv,its:nv.it.map(it=>({it,k:++k}))}});linha.forEach(l=>l.its.forEach(x=>itens.push(Object.assign({n,rot:l.nv.r,setor:l.sg.c},x))));return{n,linha}});
    let est='<div class="estante">';
    if(m.niv===7)est+=`<div class="nl"><b>7</b>topo</div><div class="pr ae"><em>Nível 7: só estoque aéreo e placa do setor</em></div>`;
    niveis.forEach(({n,linha})=>{const ol=(n===3||n===4)?' olho':'';est+=`<div class="nl${ol}"><b>${n}</b><span>${NIV[n]}</span></div><div class="pr${ol}">`;
      linha.forEach(l=>{const W=l.sg.w;let usado=0;const its=l.its.map(x=>{const lw=x.it.w*Math.max(1,x.it.f);usado+=lw;return tile(x.it,x.k,Math.min(100,lw/W*100))}).join('');
        const sobra=W-usado;est+=`<div class="seg" style="flex:${l.sg.w}"><span class="rot">${esc(l.nv.r||l.sg.c)}</span><div class="its">${its}${sobra>=12?`<span class="livre">${usado>0?'livre':'Livre: placa ou produto da loja'}</span>`:''}</div></div>`});
      est+='</div>'});
    est+='</div>';
    const lista=niveis.map(({n,linha})=>{const xs=itens.filter(x=>x.n===n);if(!xs.length)return'';const ol=(n===3||n===4)?' olho':'';const rots=[...new Set(linha.map(l=>l.nv.r).filter(Boolean))].join(' · ');
      return `<div class="ln${ol}"><h4>Nível ${n} · ${NIV[n]} <small>${esc(rots)}</small></h4><ol>${xs.map(x=>`<li data-k="${x.k}"><span class="nu a-${x.it.a}">${x.k}</span><span><b>${esc(x.it.n)}</b><small>${esc(x.it.m)} · ${ACAO[x.it.a][0]}${x.it.l?' · extra desta loja':''}</small></span><span class="q"><b>${x.it.f}</b> frente${x.it.f>1?'s':''}</span></li>`).join('')}</ol></div>`}).join('');
    const ped=itens.filter(x=>x.it.a!=='tem').length;
    p.innerHTML=`<div class="mod"><div style="display:grid;gap:12px;min-width:0">${cab}${miniMapa(cur)}<p class="sub">${esc(m.nota)}</p>
      <div class="setores">${b.map(sg=>`<span style="background:${COR[sg.c]};color:#fff">${esc(sg.c)}</span>`).join('')}<span>${itens.length} produtos</span>${ped?`<span style="background:var(--pedir);color:#fff">${ped} chegam no pedido</span>`:''}</div>
      <div class="movel"><div class="med"><span>← ${num(larguraSt(st),2)} m →</span><span>toque num produto para ver o nome</span></div>${est}</div>
      <div class="leg"><span><i class="dot d-tem"></i>Já tem</span><span><i class="dot d-pedir"></i>Pedido</span><span><i class="dot d-novo"></i>Novo</span><span><i class="dot d-livre"></i>Livre</span></div></div>
      <div style="display:grid;gap:12px;min-width:0">${checks('Esvaziei e limpei as prateleiras','Arrumei igual ao desenho','Pus as etiquetas e tirei a foto')}<div class="lista">${lista}</div>${prox}</div></div>`;
    $$('.it,.ln li',p).forEach(el=>el.addEventListener('click',()=>{const x=itens.find(i=>i.k===+el.dataset.k);if(x)abre({it:x.it,n:x.n,rot:x.rot,setor:x.setor,si:cur})}));
  }
  $('#ant').onclick=()=>anda(-1);$('#seg').onclick=()=>anda(1);$('#ant2').onclick=()=>anda(-1);$('#seg2').onclick=()=>anda(1);
  [['c1','limpo'],['c2','montado'],['c3','foto']].forEach(([id,campo])=>$('#'+id).addEventListener('change',e=>{EST[key]=Object.assign({},EST[key],{[campo]:e.target.checked});salva();progresso();if(campo==='montado')desenha()}));
  progresso();
}
// ---------- folha de detalhe ----------
function abre(x){
  const it=x.it,a=ACAO[it.a]||ACAO.tem,ph=F[it.s]||F['g'+it.s],st=ST[x.si];
  const onde=x.setor==='Granel'?`${MV[st.mi].nome} · pote ${x.tubo}`:`${nomeSt(st)} · nível ${x.n} (${NIV[x.n]})`;
  const pr=it.pr&&it.pr[0]?`R$ ${num(it.pr[0],2)} a R$ ${num(it.pr[1],2)}`:'';
  $('#folha').hidden=false;
  $('#folha').innerHTML=`<div class="veu" id="veu"></div><div class="folha" role="dialog" aria-modal="true" aria-label="${esc(it.n)}">
    <div class="tp">${ph?`<img src="${ph}" alt="">`:`<span class="ph0" style="background:${corMarca(it.m)}"></span>`}<div><div class="mk">${esc(it.m)} · código ${it.s}</div><h3>${esc(it.n)}</h3></div></div>
    <div class="acao a-${it.a}">${a[0]}. ${a[1]}</div>
    <dl><dt>Onde</dt><dd>${esc(onde)}</dd><dt>Prateleira</dt><dd>${esc(x.rot||x.setor)}</dd><dt>Frentes</dt><dd>${it.f}</dd>
    ${it.e!=null?`<dt>Estoque 12/11</dt><dd>${num(it.e,it.e%1?2:0)}</dd>`:''}${it.p?`<dt>Pedido</dt><dd>${it.p}</dd>`:''}${pr?`<dt>Faixa de preço</dt><dd>${pr}</dd>`:''}</dl>
    <button class="fx" id="fx">Fechar</button></div>`;
  const fecha=()=>{$('#folha').hidden=true;$('#folha').innerHTML=''};$('#fx').onclick=fecha;$('#veu').onclick=fecha;
  document.addEventListener('keydown',function k(e){if(e.key==='Escape'){fecha();document.removeEventListener('keydown',k)}});$('#fx').focus();
}
// ---------- 3D ----------
let T3=null;
$('#mPl').onclick=()=>{$('#mPl').classList.add('on');$('#m3d').classList.remove('on');$('#boxPlanta').hidden=false;$('#box3d').hidden=true};
$('#m3d').onclick=()=>{$('#m3d').classList.add('on');$('#mPl').classList.remove('on');$('#boxPlanta').hidden=true;$('#box3d').hidden=false;if(!T3)carrega3D();else T3.resize()};
function script(src){return new Promise((ok,erro)=>{const s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=erro;document.head.appendChild(s)})}
async function carrega3D(){
  T3={resize(){}};
  try{if(!window.THREE)await script('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js');
    if(!THREE.OrbitControls)await script('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js');}
  catch(e){$('#aviso3d').textContent='A vista em 3D precisa de internet. A planta funciona sem.';return}
  monta3D();
}
function monta3D(){
  const box=$('#box3d');$('#aviso3d').remove();
  const ren=new THREE.WebGLRenderer({antialias:true,alpha:true});ren.setPixelRatio(Math.min(2,window.devicePixelRatio||1));box.appendChild(ren.domElement);
  const cena=new THREE.Scene();cena.background=new THREE.Color(matchMedia('(prefers-color-scheme: dark)').matches?0x1b1310:0xefe9e1);const cam=new THREE.PerspectiveCamera(48,1,.1,200);
  const ctl=new THREE.OrbitControls(cam,ren.domElement);ctl.enableDamping=true;ctl.maxPolarAngle=Math.PI*.49;ctl.minDistance=2;ctl.maxDistance=30;
  cena.add(new THREE.HemisphereLight(0xfff6ea,0x6f5f55,.95));const sol=new THREE.DirectionalLight(0xffffff,.55);sol.position.set(4,10,2);cena.add(sol);
  const tl=new THREE.TextureLoader();
  // chão = a própria planta
  const tex=tl.load(PLANTA);const piso=new THREE.Mesh(new THREE.PlaneGeometry(P.x1-P.x0,P.y1-P.y0),new THREE.MeshLambertMaterial({map:tex}));
  piso.rotation.x=-Math.PI/2;piso.position.set((P.x0+P.x1)/2,0,(P.y0+P.y1)/2);cena.add(piso);
  const caixa=(x0,x1,z0,z1,h,cor,op=1,y0=0)=>{const g=new THREE.BoxGeometry(Math.max(.02,x1-x0),h,Math.max(.02,z1-z0));const mt=new THREE.MeshLambertMaterial({color:cor,transparent:op<1,opacity:op});const ms=new THREE.Mesh(g,mt);ms.position.set((x0+x1)/2,y0+h/2,(z0+z1)/2);cena.add(ms);return ms};
  // parede de suplementos e fundo, baixas, para ver por dentro (a do granel fica de fora para a câmera entrar)
  caixa(0,14.45,-.1,0,2.5,0xe5ddd1,.55);caixa(14.45,14.55,-.1,6.39,2.5,0xe5ddd1,.55);
  const OB={vitrine:[0x9fc3d6,.22,2.4],porta:[0xffffff,.05,.05],kombucha:[0x2f6b3a,1,1.4],balcao:[0x8c6a55,1,1.0],frio:[0xf3f3f3,1,1.9],caixa:[0x8c6a55,1,1.05],mesa:[0xcdb79e,1,.75],cafe:[0x9c8770,1,1.05],ponta:[0xe0b45a,1,1.35],mesames:[0xfbf1de,1,.85]};
  G.obj.forEach(o=>{const c=OB[o.t];if(c&&o.t!=='porta')caixa(o.x0,o.x1,o.y0,o.y1,c[2],c[0],c[1])});
  const texCache={};const texDe=s=>texCache[s]||(texCache[s]=tl.load(F[s]));
  const alvos=[];
  const rotulo=(txt,x,y,z)=>{const cv=document.createElement('canvas');cv.width=512;cv.height=96;const c=cv.getContext('2d');c.fillStyle='rgba(70,29,23,.88)';c.fillRect(0,0,512,96);c.fillStyle='#fff';c.font='600 40px sans-serif';c.textAlign='center';c.textBaseline='middle';c.fillText(txt.length>24?txt.slice(0,23)+'…':txt,256,50);
    const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(cv)}));sp.scale.set(.85,.16,1);sp.position.set(x,y,z);cena.add(sp)};
  ST.forEach((st,si)=>{const m=MV[st.mi];const r=retangulos(m,st.gr?null:st.bi)[0];const H=m.alt||1.6;
    const corp=caixa(r.x,r.x+r.w,r.y,r.y+r.h,st.gr?.95:H,new THREE.Color(st.gr?'#9C7A5E':COR[setoresDe(st)[0]]).lerp(new THREE.Color('#ffffff'),st.gr?.15:.35));corp.userData.si=si;alvos.push(corp);
    // frente do móvel
    const nrm=m.olha==='y+'?[0,1]:m.olha==='y-'?[0,-1]:[-1,0];
    const fx=nrm[0]<0?r.x-.012:nrm[0]>0?r.x+r.w+.012:null, fz=nrm[1]>0?r.y+r.h+.012:nrm[1]<0?r.y-.012:null;
    const ang=nrm[0]<0?-Math.PI/2:nrm[1]<0?Math.PI:0;
    const topo=m.niv===7?H-.45:H-.22;const passo=(topo-.12)/5;
    if(st.gr){const cols=Math.max(4,Math.ceil(m.tubos.length/3));const raio=Math.min(.075,r.w/cols*.34);
      m.tubos.forEach((t,k)=>{const cx=r.x+(k%cols+.5)*r.w/cols;const cy=1.12+Math.floor(k/cols)*.36;
        const tb=new THREE.Mesh(new THREE.CylinderGeometry(raio,raio,.3,18),new THREE.MeshLambertMaterial({color:FAM[t.fam]||'#8C6A55',transparent:true,opacity:.9}));tb.position.set(cx,cy,r.y+.15);cena.add(tb)});}
    else{let x0=0;m.bays[st.bi].forEach(sg=>{const fr=sg.w/100;sg.nv.forEach(nv=>{let usado=0;const yb=.12+(6-nv.n)*passo;
        const prat=new THREE.Mesh(new THREE.BoxGeometry(nrm[0]?0.05:fr,.02,nrm[0]?fr:0.05),new THREE.MeshLambertMaterial({color:0x8c6a55}));
        nv.it.forEach(it=>{const f=Math.max(1,it.f);for(let k2=0;k2<f;k2++){const w=it.w/100*.96;const centro=x0+usado+w/2;usado+=it.w/100;
          const mat=F[it.s]?new THREE.MeshBasicMaterial({map:texDe(it.s),transparent:true,alphaTest:.1}):new THREE.MeshBasicMaterial({color:corMarca(it.m)});
          const pl=new THREE.Mesh(new THREE.PlaneGeometry(w,Math.min(.2,passo*.85)),mat);const yy=yb+Math.min(.2,passo*.85)/2+.01;
          if(nrm[0]<0)pl.position.set(fx,yy,r.y+r.h-centro);else if(nrm[1]>0)pl.position.set(r.x+centro,yy,fz);else pl.position.set(r.x+r.w-centro,yy,fz);
          pl.rotation.y=ang;cena.add(pl)}});
        if(nrm[0]<0)prat.position.set(fx,yb,r.y+r.h-x0-fr/2);else if(nrm[1]>0)prat.position.set(r.x+x0+fr/2,yb,fz);else prat.position.set(r.x+r.w-x0-fr/2,yb,fz);cena.add(prat)});x0+=fr});}
    const lz=m.olha==='y-'?r.y-.05:m.olha==='y+'?r.y+r.h+.05:r.y+r.h/2,lx=m.olha==='x-'?r.x-.05:r.x+r.w/2;
    rotulo(st.gr?m.nome:setoresDe(st).join(' + '),lx,(st.gr?.95:H)+.16,lz);
  });
  const CAM={geral:[[7.2,7.5,13.5],[7.2,0,2.6]],entrada:[[-2.6,3.1,3.2],[7,0.5,3.2]],cima:[[7.2,15,3.6],[7.2,0,3.2]],fundo:[[13.6,2.6,5.2],[4,0.8,2]]};
  const vai=k=>{const[c,t]=CAM[k];const f=cam.aspect<1?1.75:1;cam.position.set(t[0]+(c[0]-t[0])*f,t[1]+(c[1]-t[1])*f,t[2]+(c[2]-t[2])*f);ctl.target.set(...t);ctl.update()};
  $$('.cams button',box).forEach(b=>b.addEventListener('click',()=>vai(b.dataset.c)));
  const ray=new THREE.Raycaster(),pt=new THREE.Vector2();let dn=null,cartao=null,marcado=null;
  ren.domElement.addEventListener('pointerdown',e=>{dn=[e.clientX,e.clientY]});
  ren.domElement.addEventListener('pointerup',e=>{if(!dn||Math.hypot(e.clientX-dn[0],e.clientY-dn[1])>6)return;const rc=ren.domElement.getBoundingClientRect();
    pt.set((e.clientX-rc.left)/rc.width*2-1,-(e.clientY-rc.top)/rc.height*2+1);ray.setFromCamera(pt,cam);const h=ray.intersectObjects(alvos)[0];
    if(marcado){marcado.material.emissive&&marcado.material.emissive.set(0x000000)}
    if(cartao){cartao.remove();cartao=null}
    if(!h)return;marcado=h.object;marcado.material.emissive.set(0x5a3a10);const si=h.object.userData.si,st=ST[si];
    cartao=document.createElement('div');cartao.className='cartao';cartao.innerHTML=`<div><b>${esc(nomeSt(st))}</b><small>${esc(setoresDe(st).join(' + '))}${pronto(si)?' · pronto':''}</small></div><button>Abrir módulo</button>`;
    box.appendChild(cartao);cartao.querySelector('button').onclick=()=>abreSt(si)});
  const tam=()=>{const w=box.clientWidth,h=box.clientHeight;ren.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix()};tam();window.addEventListener('resize',tam);vai('geral');
  T3={resize:tam};(function loop(){requestAnimationFrame(loop);ctl.update();ren.render(cena,cam)})();
}
// ---------- vitrines ----------
const V=G.vit||[];const ABR=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
let vSel=0;try{const u=localStorage.getItem('pin-vit-mes');const i=V.findIndex(m=>m.k===u);vSel=i>=0?i:Math.max(0,V.findIndex(m=>m.agora))}catch(e){vSel=Math.max(0,V.findIndex(m=>m.agora))}
const baseAno=mm=>mm>=11?`${MESN[mm-1]} de 2025`:mm===10?'setembro e novembro (média)':`${MESN[mm-1]} de 2026`;
const MESN=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
const fotoV=it=>it.gr?F['g'+it.s]:F[it.s];
function tileV(it,k){const ph=fotoV(it);return `<button class="vp${it.gr?' gr':''}" data-k="${k}" aria-label="${k}. ${esc(it.n)}">${ph?`<img src="${ph}" alt="">`:`<span class="pk" style="background:${corMarca(it.m)}">${esc(it.m)}</span>`}<i class="nu">${k}</i>${it.pin?'':'<em>pedir</em>'}</button>`}
function degraus(s){const its=s.it.map((it,i)=>[it,s.k0+i+1]);const n=its.length;const t=n<=3?[[],[],its]:n<=5?[[],its.slice(0,2),its.slice(2)]:[its.slice(0,Math.round(n/3)),its.slice(Math.round(n/3),Math.round(2*n/3)),its.slice(Math.round(2*n/3))];
  return '<div class="degraus">'+t.filter(x=>x.length).map(x=>`<div class="dg">${x.map(([it,k])=>tileV(it,k)).join('')}</div>`).join('')+'</div>'}
function vidro(s,w,m){return `<div class="vid${m.mm===11?' preta':''}" style="flex:${w}"><div class="adesivo">${esc(s.promessa)}</div>${degraus(s)}<div class="vrot"><i>${s.n}</i><span><b>${esc(s.nome)}</b> · ${esc(s.onde)}</span></div></div>`}
function mapaV(){const P=G.planta,vs=G.obj.filter(o=>o.t==='vitrine').sort((a,b)=>a.y0-b.y0),ms=G.obj.find(o=>o.t==='mesames'),pt=G.obj.filter(o=>o.t==='ponta').sort((a,b)=>a.x0-b.x0)[0];
  const mk=[[vs[0],1],[vs[1],2],[ms,3],[pt,4]].filter(x=>x[0]);
  return `<svg viewBox="${P.x0} ${P.y0} ${P.x1-P.x0} ${P.y1-P.y0}" role="img" aria-label="Onde ficam os quatro espaços"><image href="${PLANTA}" x="${P.x0}" y="${P.y0}" width="${P.x1-P.x0}" height="${P.y1-P.y0}" preserveAspectRatio="none" opacity=".6"/>`+
    mk.map(([o,n])=>{const cx=(o.x0+o.x1)/2+(n<=2?.45:0),cy=(o.y0+o.y1)/2;return `<rect x="${o.x0}" y="${o.y0}" width="${o.x1-o.x0}" height="${o.y1-o.y0}" fill="#CA942A" fill-opacity=".55"/><circle cx="${cx}" cy="${cy}" r=".42" fill="#CA942A" stroke="#461D17" stroke-width=".06"/><text x="${cx}" y="${cy+.14}" text-anchor="middle" font-size=".42" font-weight="700" fill="#461D17">${n}</text>`}).join('')+'</svg>'}
function desenhaV(){
  if(!V.length){$('#mesv').innerHTML='<p class="sub">O calendário ainda não foi gerado.</p>';return}
  try{localStorage.setItem('pin-vit-mes',V[vSel].k)}catch(e){}
  $('#ano').innerHTML=V.map((m,i)=>`<button role="tab" aria-selected="${i===vSel}" style="--c:${m.cor}" class="${i===vSel?'on':''}" data-i="${i}">${m.agora?'<span class="ag">Próximo</span>':''}<b>${ABR[m.mm-1]} ${String(m.ano).slice(2)}</b><small>${esc(m.curto)}</small></button>`).join('');
  $$('#ano button').forEach(b=>b.addEventListener('click',()=>{vSel=+b.dataset.i;desenhaV()}));
  const m=V[vSel];let k=0;const S={};m.sp.forEach((s,i)=>{S[s.id]=Object.assign({},s,{k0:k,n:i+1});k+=s.it.length});
  const est=EST['v:'+m.k]||{};const tot=k,ped=m.sp.reduce((a,s)=>a+s.it.filter(x=>!x.pin).length,0);
  const lista=Object.values(S).map(s=>`<div class="ln"><h4><span class="nu" style="background:var(--gold);color:#2B1A14;width:22px;height:22px;border-radius:50%;display:inline-grid;place-items:center">${s.n}</span>${esc(s.nome)} <small>${esc(s.tema)}</small></h4><ol>${s.it.map((it,i)=>{const ph=fotoV(it);return `<li data-k="${s.k0+i+1}"><span class="nu" style="background:#461D17">${s.k0+i+1}</span><span><b>${esc(it.n)}</b><small>${esc(it.m)}${it.pin&&it.onde?' · '+esc(it.onde):''}</small></span><span class="q"><span class="tag${it.pin?'':' pd'}">${it.pin?'Tem na loja':'Pedir à rede'}</span></span></li>`}).join('')}</ol></div>`).join('');
  const prat=its=>{const n=its.length,a=Math.ceil(n/3),b=Math.ceil((n-a)/2);return [its.slice(0,a),its.slice(a,a+b),its.slice(a+b)].filter(x=>x.length).map(x=>`<div class="prat">${x.map(([it,kk])=>tileV(it,kk)).join('')}</div>`).join('')};
  const p=m.peso;
  $('#mesv').innerHTML=`
  <div class="vt-cab" style="--c:${m.cor}"><span class="eb">${m.mes} de ${m.ano}${m.agora?' · o próximo mês':''}</span><h3>${esc(m.tema)}</h3>
    <div class="vt-dts">${m.dt.map(x=>`<span><b>${x.d}</b> ${esc(x.n)}<em>${esc(x.nv)}</em></span>`).join('')||'<span>Sem data da rede no mês</span>'}</div>
    <div class="cron">${m.cron.map(([t,d])=>`<div><b>${d}</b><span>${esc(t)}</span></div>`).join('')}</div></div>
  <div class="fach" style="--c:${m.cor};--vbg:${m.mm===11?'#211A17':`color-mix(in srgb, ${m.cor} 12%, #FBF8F3)`}"><div class="letreiro">DIVINA TERRA</div>
    <div class="vidros">${vidro(S.ve,1.2,m)}<div class="porta">Entrada</div>${vidro(S.vd,2,m)}</div><div class="calcada"></div></div>
  <div class="vt-g">
    <div class="cartao2" style="--c:${m.cor}"><div class="tt"><i>3</i><span><b>${esc(S.mesa.nome)}</b><small>${esc(S.mesa.onde)}</small></span></div><h4>${esc(S.mesa.tema)}</h4>
      <div class="mesa-il"><div class="prods">${S.mesa.it.map((it,i)=>tileV(it,S.mesa.k0+i+1)).join('')}</div><div class="tampo"></div><div class="pes"><i></i><i></i></div></div><p class="sub" style="font-size:14px">Placa da mesa: ${esc(S.mesa.promessa)}</p></div>
    <div class="cartao2" style="--c:${m.cor}"><div class="tt"><i>4</i><span><b>${esc(S.ponta.nome)}</b><small>${esc(S.ponta.onde)}</small></span></div><h4>${esc(S.ponta.tema)}</h4>
      <div class="ponta-il"><div class="testeira">${esc(S.ponta.promessa)}</div>${prat(S.ponta.it.map((it,i)=>[it,S.ponta.k0+i+1]))}</div></div>
    <div class="cartao2"><div class="tt"><span><b>Onde fica cada espaço</b><small>1 e 2 vitrines, 3 mesa do mês, 4 ponta da entrada</small></span></div><div class="mini2">${mapaV()}</div>
      <div class="setores"><span>${tot} produtos no mês</span>${ped?`<span style="background:var(--pedir);color:#fff">${ped} pedir à rede até ${m.cron[0][1]}</span>`:''}</div>
      ${m.nota?`<p class="nota" style="font-size:13.5px">${esc(m.nota)}</p>`:''}</div>
  </div>
  <div class="vt-g2"><div class="lista">${lista}</div>
    <div style="display:grid;gap:12px">
      <div class="chk"><b>Checklist do mês</b>${[['mat','Material e produtos chegaram'],['vit','Vitrines montadas, com foto no grupo'],['mes','Mesa e ponta montadas'],['des','Desmontado no dia certo']].map(([id,t])=>`<label><input type="checkbox" data-c="${id}" ${est[id]?'checked':''}> ${t}</label>`).join('')}</div>
      <div class="cartao2"><b>Na estratégia deste mês</b><div class="peso" title="Peso do trade no mês, proposta">${[['Cuidar',p[0],'#7C381F'],['Abastecer',p[1],'#596D49'],['Celebrar',p[2],'#CA942A']].map(([n,v,c])=>`<span style="flex:${v};background:${c}">${v>=30?n+' ':''}${v>=12?v+'%':''}</span>`).join('')}</div>
        <div class="est3"><div style="--k:#7C381F"><b>Cuidar</b>${esc(m.C)}</div><div style="--k:#596D49"><b>Abastecer</b>${esc(m.A)}</div><div style="--k:#AC834C"><b>Celebrar</b>${esc(m.E)}</div></div>
        <p class="nota">Produtos escolhidos pela venda de Pinheiros no mesmo mês do ano passado e pela média da loja; o que a loja não tem vem da venda por loja da rede. Suplemento sem promessa de saúde; datas de conscientização são conteúdo, sem produto.</p></div>
    </div></div>`;
  const todos=[];m.sp.forEach(s=>s.it.forEach(it=>todos.push([it,S[s.id]])));
  $$('#mesv .vp,#mesv .ln li').forEach(el=>el.addEventListener('click',()=>{const x=todos[+el.dataset.k-1];if(x)abreV(x[0],x[1],m)}));
  $$('#mesv .chk input').forEach(c=>c.addEventListener('change',e=>{EST['v:'+m.k]=Object.assign({},EST['v:'+m.k],{[c.dataset.c]:e.target.checked});salva()}));
  const on=$('#ano button.on');if(on)on.scrollIntoView({inline:'center',block:'nearest'});
}
function abreV(it,s,m){
  const ph=fotoV(it);
  $('#folha').hidden=false;
  $('#folha').innerHTML=`<div class="veu" id="veu"></div><div class="folha" role="dialog" aria-modal="true" aria-label="${esc(it.n)}">
    <div class="tp">${ph?`<img src="${ph}" alt="">`:`<span class="ph0" style="background:${corMarca(it.m)}"></span>`}<div><div class="mk">${esc(it.m)} · código ${it.s}</div><h3>${esc(it.n)}</h3></div></div>
    <div class="acao ${it.pin?'a-tem':'a-pedir'}">${it.pin?`Tem na loja. Pegue ${it.gr?'no granel':'na gôndola'}${it.onde&&!it.gr?': '+esc(it.onde):''}.`:`Pinheiros não tem. Pedir à rede até ${m.cron[0][1]}.`}</div>
    <dl><dt>Onde vai</dt><dd>${esc(s.nome)} · ${esc(s.tema)}</dd><dt>Mês</dt><dd>${m.mes} de ${m.ano}</dd>
    ${it.vm?`<dt>Em Pinheiros</dt><dd>R$ ${num(it.vm)} vendidos em ${baseAno(m.mm)}</dd>`:''}${it.v11?`<dt>Em 11 meses</dt><dd>R$ ${num(it.v11)} em Pinheiros</dd>`:''}${!it.pin&&it.vr?`<dt>Na rede</dt><dd>R$ ${num(it.vr)} por loja no mês</dd>`:''}</dl>
    <button class="fx" id="fx">Fechar</button></div>`;
  const fecha=()=>{$('#folha').hidden=true;$('#folha').innerHTML=''};$('#fx').onclick=fecha;$('#veu').onclick=fecha;$('#fx').focus();
}
// ---------- tirar ----------
function grupos(lista,alvo,tipo){
  const por={};lista.forEach((x,i)=>{(por[x.st]=por[x.st]||[]).push(Object.assign({i},x))});
  $(alvo).innerHTML=Object.keys(por).sort().map(st=>{const xs=por[st];const feitos=xs.filter(x=>EST['t:'+tipo+':'+x.i]).length;
    return `<details class="grp"><summary>${esc(st)}<small>${feitos} de ${xs.length}</small></summary><ul class="tl">${xs.map(x=>`<li class="${EST['t:'+tipo+':'+x.i]?'x':''}"><input type="checkbox" data-t="${tipo}" data-i="${x.i}" ${EST['t:'+tipo+':'+x.i]?'checked':''} aria-label="Tirei ${esc(x.n)}"><span><b>${esc(x.n)}</b><small>${esc(x.m)}</small></span><span class="q">${x.e!=null?num(x.e,x.e%1?2:0)+' un.':''}</span></li>`).join('')}</ul></details>`}).join('');
  $$('input',$(alvo)).forEach(c=>c.addEventListener('change',e=>{const k='t:'+c.dataset.t+':'+c.dataset.i;EST[k]=e.target.checked;salva();c.closest('li').classList.toggle('x',e.target.checked);
    const d=c.closest('details'),cb=$$('input',d);d.querySelector('small').textContent=`${cb.filter(i=>i.checked).length} de ${cb.length}`}));
}
$('#nTirar').textContent=num(G.tirar.length);$('#nGuardar').textContent=num(G.guardar.length);
grupos(G.tirar,'#lTirar','p');grupos(G.guardar,'#lGuardar','g');
// ---------- pedido ----------
(function(){const por={};G.pedido.forEach(x=>{(por[x.m||'Sem marca']=por[x.m||'Sem marca']||[]).push(x)});
  const ord=Object.keys(por).sort((a,b)=>por[b].length-por[a].length);const pri=t=>G.pedido.filter(x=>x.pri===t).length;
  $('#pedNum').innerHTML=[[pri('Repor já'),'repor já: vende bem e acabou','#461D17'],[pri('Núcleo a incorporar'),'novos na loja','#7C381F'],[pri('Completar o planograma'),'para completar o planograma','#CA942A']].map(([v,t,c])=>`<div style="--k:${c}"><b>${v}</b>${t}</div>`).join('');
  $('#lPedido').innerHTML=ord.map(m=>`<details class="grp"><summary>${esc(m)}<small>${por[m].length} produtos</small></summary><ul class="tl">${por[m].map(x=>`<li><span class="dot ${x.pri==='Repor já'?'d-tirar':x.pri==='Núcleo a incorporar'?'d-novo':'d-pedir'}"></span><span><b>${esc(x.n)}</b><small>${esc(x.pri)} · ${esc(x.lg)}</small></span><span class="q">${x.q} ${esc(x.un)}</span></li>`).join('')}</ul></details>`).join('');
})();
// ---------- números ----------
const R_=G.resumo;
$('#numeros').innerHTML=[[ST.length,'módulos para montar','#7C381F'],[R_.plano,'produtos no planograma','#596D49'],[R_.pedir,'chegam no pedido','#CA942A'],[R_.tirar,'saem da gôndola','#461D17']].map(([v,t,c])=>`<div style="--k:${c}"><b>${num(v)}</b>${t}</div>`).join('');
// ---------- busca ----------
const norm=t=>String(t).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
$('#q').addEventListener('input',e=>{const q=norm(e.target.value.trim());if(q.length<2){$('#res').innerHTML='';return}
  const r=IDX.filter(x=>norm(x.it.n+' '+x.it.m+' '+x.it.s).includes(q)).slice(0,40);
  $('#res').innerHTML=r.length?r.map((x,i)=>{const st=ST[x.si];const onde=x.setor==='Granel'?`${MV[st.mi].nome} · pote ${x.tubo}`:`${nomeSt(st)} · nível ${x.n}`;const ph=F[x.it.s]||F['g'+x.it.s];
    return `<button data-r="${i}">${ph?`<img src="${ph}" alt="">`:`<span class="ph0" style="background:${corMarca(x.it.m)}"></span>`}<span><b>${esc(x.it.n)}</b><small>${esc(onde)} · ${(ACAO[x.it.a]||ACAO.tem)[0]}</small></span></button>`}).join('')
    :'<p class="sub">Não está no planograma. Se tem na loja, veja a aba "Tirar da gôndola".</p>';
  $$('#res button').forEach(b=>b.addEventListener('click',()=>{const x=r[+b.dataset.r];abreSt(x.si);abre(x)}));
});
desenhaPlanta();mostra(location.hash.slice(1)||'loja');progresso();
})();
</script>'''

doc = (PAGINA.replace('__FONTE__', fonte).replace('__PLANTA__', planta).replace('__LOGO__', LOGO).replace('__LAB__', LAB).replace('__SPRITE__', SPRITE).replace('__HEROI__', HEROI)
       .replace('__DADOS__', json.dumps(G, ensure_ascii=False).replace('</', '<\\/')).replace('__FOTOS__', json.dumps({str(k): v for k, v in fotos.items()})))
if PUBLICO:
    out = R / 'pinheiros.html'
    out.write_text('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="robots" content="noindex">\n'
                   + doc.replace('</style>', 'body{min-height:100vh}</style>', 1).replace('<header class="topo">', '</head><body>\n<header class="topo">', 1) + '\n</body></html>\n')
else:
    out = R / 'kit/pinheiros-guia.html'; out.write_text(doc)
bad = [t for t in ('—', '–') if t in PAGINA]
print(out, round(len(doc.encode()) / 1e6, 2), 'MB;', len(fotos), 'fotos; planta', im.size, ';', 'TRAVESSAO' if bad else 'sem travessão')
