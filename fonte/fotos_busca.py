#!/usr/bin/env python3
"""Segunda passada de fotos de embalagem: busca de imagens na internet para o que os catálogos não casaram.

Uso:
  python3 fonte/fotos_busca.py run      busca, baixa, trata e grava assets/produtos/<sku>.webp (conf "busca")
  python3 fonte/fotos_busca.py folhas   folhas de contato com o nome do produto, para conferência visual
  python3 fonte/fotos_busca.py remover sku [sku ...]   reprova a foto e tenta o próximo candidato na próxima rodada

Alvo: produtos do planograma de Pinheiros (analise/pinheiros_guia.json) sem foto em assets/produtos/mapa.json.
A busca usa só marca e nome do produto. Bruto e cache no HD (divina-terra-produtos/busca).
"""
import concurrent.futures as cf
import hashlib
import html
import json
import os
import re
import sys
import threading
import time
import unicodedata
import urllib.parse

import requests
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fotos_produtos as fp  # noqa: E402  reaproveita o tratamento (fundo branco, recorte, webp)

RAIZ = fp.RAIZ
HD = os.path.join(fp.HD, "busca")
CACHE = os.path.join(HD, "bing")
BRUTO = os.path.join(HD, "bruto")
REL = os.path.join(HD, "relato.json")
REPROV = os.path.join(HD, "reprovados.json")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
      "Accept-Language": "pt-BR,pt;q=0.9"}
_trava = threading.Lock()
_ult = [0.0]
PARE = {"DE", "DA", "DO", "E", "COM", "EM", "PARA", "O", "A", "UN", "UND", "CAPS", "CAP", "CAPSULAS", "CAPSULA", "SACHES", "SACHE",
        "ML", "G", "GR", "KG", "MG", "SABOR", "TABS", "TABLETES", "SOFTGELS", "PO", "PCT", "CX", "C", "S", "SEM"}
RUIM = re.compile(r"\b(KIT|COMBO|LEVE \d|PACK \d|\d+ ?X ?\d|\d ?UNIDADES|CAIXA COM|DISPLAY|ATACADO|REFIL \+)\b")


def norm(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


def compacto(s):
    return norm(s).replace(" ", "")


def medidas(s):
    """números com unidade: 20 ML, 60 CAPS, 500 G (normalizados)."""
    t = norm(s)
    out = set()
    for n, u in re.findall(r"(\d+(?:[.,]\d+)?) ?(ML|L|G|GR|KG|MG|CAPS|CAPSULAS|CAP|CP|TABS|SACHES|UN|IU|UI|MCG)\b", t):
        u = {"GR": "G", "CAPSULAS": "CAPS", "CAP": "CAPS", "CP": "CAPS", "UI": "IU"}.get(u, u)
        v = float(n.replace(",", "."))
        if u == "KG": v, u = v * 1000, "G"
        if u == "L": v, u = v * 1000, "ML"
        out.add((round(v, 1), u))
    return out


def alvos():
    G = json.load(open(os.path.join(RAIZ, "analise/pinheiros_guia.json")))
    mapa = fp.carrega_mapa()
    vistos, out = set(), []
    for m in G["moveis"]:
        for bay in m.get("bays", []):
            for sg in bay:
                for nv in sg["nv"]:
                    for it in nv["it"]:
                        k = str(it["s"])
                        if k in vistos or k in mapa:
                            continue
                        vistos.add(k)
                        out.append({"sku": k, "n": it["n"], "m": it["m"], "setor": sg["c"]})
    extra = os.path.join(RAIZ, "analise/vitrines_fotos.json")  # produtos do calendário de vitrines que a loja não tem
    if os.path.exists(extra):
        for x in json.load(open(extra)):
            if x["sku"] not in vistos and x["sku"] not in mapa:
                vistos.add(x["sku"])
                out.append({"sku": x["sku"], "n": x["n"], "m": x["m"], "setor": "vitrine"})
    return out


def bing(q):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, hashlib.md5(q.encode()).hexdigest() + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    with _trava:
        falta = _ult[0] + 1.3 - time.time()
        if falta > 0:
            time.sleep(falta)
        _ult[0] = time.time()
    for tent in range(3):
        try:
            r = requests.get("https://www.bing.com/images/search", params={"q": q, "form": "HDRSC2", "first": 1}, headers=UA, timeout=25)
            if r.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(3 + tent * 4)
    else:
        return None
    res = []
    for m in re.findall(r'class="iusc"[^>]*m="([^"]+)"', r.text):
        try:
            d = json.loads(html.unescape(m))
        except ValueError:
            continue
        if d.get("murl"):
            res.append({"img": d["murl"], "pag": d.get("purl", ""), "t": d.get("t", "")})
    json.dump(res, open(p, "w"), ensure_ascii=False)
    return res


def pontua(alvo, c):
    """0 a 1: marca obrigatória, palavras do nome, medida igual; kit e combo fora."""
    t = norm(c["t"] + " " + urllib.parse.unquote(c["pag"]).replace("-", " ").replace("/", " "))
    tc = t.replace(" ", "")
    marca = compacto(alvo["m"])
    if marca and marca not in tc and not any(len(w) >= 4 and w in t.split() for w in norm(alvo["m"]).split()):
        return 0, "marca"
    if RUIM.search(norm(c["t"])):
        return 0, "kit"
    pal = [w for w in norm(alvo["n"]).split() if w not in PARE and not re.fullmatch(r"\d+([.,]\d+)?", w) and w not in norm(alvo["m"]).split()]
    if not pal:
        pal = norm(alvo["n"]).split()
    achou = sum(1 for w in pal if w in t.split() or (len(w) >= 5 and w in tc))
    frac = achou / len(pal)
    ma, mc = medidas(alvo["n"]), medidas(c["t"])
    nota = frac
    if ma:
        if ma & mc:
            nota += 0.25
        elif any(u == ua for _, u in mc for _, ua in ma):
            return 0, "medida-diferente"
    return nota, f"{achou}/{len(pal)}"


def baixa(u):
    os.makedirs(BRUTO, exist_ok=True)
    p = os.path.join(BRUTO, hashlib.md5(u.encode()).hexdigest())
    if os.path.exists(p):
        return open(p, "rb").read()
    try:
        r = requests.get(fp.url_imagem(u), headers={"User-Agent": UA["User-Agent"], "Accept": "image/*,*/*;q=0.8"}, timeout=25)
        if r.status_code != 200 or len(r.content) < 3000:
            return None
        dados = r.content
    except requests.RequestException:
        cod, dados = fp.http(u, timeout=25, tentativas=1)
        if dados is None or cod != 200:
            return None
    open(p, "wb").write(dados)
    return dados


def um(alvo, mapa, rel, reprov):
    k = alvo["sku"]
    q = f'{alvo["m"]} {alvo["n"]}'
    cands = bing(q) or []
    nota = sorted(((pontua(alvo, c), i, c) for i, c in enumerate(cands)), key=lambda x: (-x[0][0], x[1]))
    tent = []
    for (s, mot), i, c in nota:
        if s < 0.6 or c["img"] in reprov.get(k, []):
            continue
        dados = baixa(c["img"])
        if dados is None:
            tent.append("sem-download")
            continue
        fino = (fp.tamanhos(fp.norm(alvo["n"].upper())).get("peso") or 99) <= 15
        im, por = fp.trata_imagem(dados, fino)
        if im is None:
            tent.append(por)
            continue
        fp.grava_webp(im, os.path.join(fp.SAIDA, k + ".webp"))
        with fp._mapa_lock:
            mapa[k] = {"ar": round(im.height / im.width, 3), "fonte": c["pag"] or c["img"], "conf": "busca"}
            fp.grava_mapa(mapa)
            rel[k] = {"st": "ok", "nota": round(s, 2), "mot": mot, "t": c["t"], "img": c["img"], "pag": c["pag"], "n": alvo["n"], "m": alvo["m"]}
        return True
    with fp._mapa_lock:
        rel[k] = {"st": "sem", "n": alvo["n"], "m": alvo["m"], "tent": tent[:6], "melhor": [(round(x[0][0], 2), x[0][1], x[2]["t"][:70]) for x in nota[:3]]}
    return False


def run():
    os.makedirs(HD, exist_ok=True)
    mapa = fp.carrega_mapa()
    rel = json.load(open(REL)) if os.path.exists(REL) else {}
    reprov = json.load(open(REPROV)) if os.path.exists(REPROV) else {}
    alv = alvos()
    print("sem foto:", len(alv), flush=True)
    ok = [0]

    def vai(a):
        try:
            if um(a, mapa, rel, reprov):
                ok[0] += 1
        except Exception as e:  # um produto com erro não para a rodada
            rel[a["sku"]] = {"st": "erro", "e": repr(e), "n": a["n"], "m": a["m"]}

    with cf.ThreadPoolExecutor(4) as ex:
        for j, _ in enumerate(ex.map(vai, alv), 1):
            if j % 25 == 0:
                print(f"{j}/{len(alv)} com foto {ok[0]}", flush=True)
                with fp._mapa_lock:
                    json.dump(rel, open(REL, "w"), ensure_ascii=False)
    json.dump(rel, open(REL, "w"), ensure_ascii=False)
    print("fim: com foto", ok[0], "de", len(alv), flush=True)


def folhas():
    rel = json.load(open(REL))
    ks = [k for k, v in rel.items() if v["st"] == "ok" and os.path.exists(os.path.join(fp.SAIDA, k + ".webp"))]
    saida = os.path.join(HD, "folhas")
    os.makedirs(saida, exist_ok=True)
    f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    col, cw, ch, por = 8, 190, 225, 48
    for i in range(0, len(ks), por):
        lote = ks[i:i + por]
        fol = Image.new("RGB", (col * cw, ((len(lote) + col - 1) // col) * ch), (225, 225, 225))
        d = ImageDraw.Draw(fol)
        for j, k in enumerate(lote):
            x, y = (j % col) * cw, (j // col) * ch
            d.rectangle([x + 2, y + 2, x + cw - 3, y + ch - 3], fill=(255, 255, 255))
            im = Image.open(os.path.join(fp.SAIDA, k + ".webp")).convert("RGB")
            im.thumbnail((cw - 14, 150))
            fol.paste(im, (x + (cw - im.width) // 2, y + 6))
            t = f'{rel[k]["m"]} · {rel[k]["n"]}'
            d.text((x + 5, y + 160), k, fill=(170, 0, 0), font=f)
            d.text((x + 5, y + 175), t[:27], fill=(0, 0, 0), font=f)
            d.text((x + 5, y + 190), t[27:54], fill=(0, 0, 0), font=f)
            d.text((x + 5, y + 205), t[54:81], fill=(0, 0, 0), font=f)
        arq = os.path.join(saida, f"busca_{i // por:02d}.jpg")
        fol.save(arq, quality=80)
        print(arq)


def remover(ks):
    mapa = fp.carrega_mapa()
    rel = json.load(open(REL))
    reprov = json.load(open(REPROV)) if os.path.exists(REPROV) else {}
    for k in ks:
        if rel.get(k, {}).get("img"):
            reprov.setdefault(k, []).append(rel[k]["img"])
        rel.pop(k, None)
        mapa.pop(k, None)
        p = os.path.join(fp.SAIDA, k + ".webp")
        if os.path.exists(p):
            os.remove(p)
    fp.grava_mapa(mapa)
    json.dump(reprov, open(REPROV, "w"))
    json.dump(rel, open(REL, "w"), ensure_ascii=False)
    print("reprovados:", sum(len(v) for v in reprov.values()), "mapa:", len(mapa))


def granel(refazer=()):
    """Foto do produto solto (castanha, grão, chá) para os potes do granel: recorte quadrado, sem exigir fundo branco."""
    G = json.load(open(os.path.join(RAIZ, "analise/pinheiros_guia.json")))
    dest = os.path.join(fp.SAIDA, "granel")
    os.makedirs(dest, exist_ok=True)
    tubos = [t for m in G["moveis"] if m.get("grupo") == "granel" for t in m["tubos"]]
    usados_p = os.path.join(HD, "granel_usados.json")
    usados = json.load(open(usados_p)) if os.path.exists(usados_p) else {}
    ok = 0
    for t in tubos:
        arq = os.path.join(dest, f'{t["s"]}.webp')
        if str(t["s"]) in refazer and os.path.exists(arq):
            os.remove(arq)
        if os.path.exists(arq):
            ok += 1
            continue
        nome = re.sub(r"\b(GRANEL|A GRANEL|KG)\b", "", norm(t["n"])).strip().lower()
        consulta = f"{nome} granel" if str(t["s"]) not in refazer else f"{nome} tigela foto"
        for c in (bing(consulta) or [])[:10]:
            if c["img"] in usados.get(str(t["s"]), []):
                continue
            dados = baixa(c["img"])
            if not dados:
                continue
            try:
                im = Image.open(__import__("io").BytesIO(dados)).convert("RGB")
            except Exception:
                continue
            w, h = im.size
            if min(w, h) < 200 or max(w, h) / min(w, h) > 1.9:
                continue
            q = min(w, h)
            im = im.crop(((w - q) // 2, (h - q) // 2, (w + q) // 2, (h + q) // 2)).resize((160, 160), Image.LANCZOS)
            im.save(arq, "WEBP", quality=70)
            usados.setdefault(str(t["s"]), []).append(c["img"])
            ok += 1
            break
    json.dump(usados, open(usados_p, "w"))
    print("granel com foto:", ok, "de", len(tubos))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "granel":
        granel(set(sys.argv[2:]))
    else:
        {"run": run, "folhas": folhas}.get(cmd, lambda: remover(sys.argv[2:]))()
