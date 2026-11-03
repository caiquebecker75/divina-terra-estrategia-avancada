#!/usr/bin/env python3
"""Fotos reais de embalagem para o planograma da Divina Terra.

Uso:
  python3 fonte/fotos_produtos.py harvest [fonte ...]   coleta catalogos publicos (cache no HD)
  python3 fonte/fotos_produtos.py match                 so casa e grava relatorio de casamento (sem baixar)
  python3 fonte/fotos_produtos.py run [--limite N]      casa, baixa, trata e grava assets/produtos + mapa.json
  python3 fonte/fotos_produtos.py folhas [sku ...]      gera folhas de contato para conferencia visual
  python3 fonte/fotos_produtos.py remover sku [sku ...] tira do mapa e apaga o webp (reprovado na conferencia)
  python3 fonte/fotos_produtos.py relatorio             numeros de cobertura

O valor de venda (v) so e usado localmente, para a ordem e o relatorio. As buscas usam marca e nome.
"""
import concurrent.futures as cf
import functools
import gzip
import hashlib
import html
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.parse
from collections import Counter, defaultdict
from difflib import SequenceMatcher

import numpy as np
from scipy import ndimage
import requests
import urllib3
from PIL import Image, ImageDraw

urllib3.disable_warnings()
Image.MAX_IMAGE_PIXELS = 40_000_000

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "analise", "skus_planograma_v2.json")
SAIDA = os.path.join(RAIZ, "assets", "produtos")
MAPA = os.path.join(SAIDA, "mapa.json")
HD = "/Volumes/hd caique becker/Mac Caique/Downloads/divina-terra-produtos"
CATALOGOS = os.path.join(HD, "catalog")
BRUTOS = os.path.join(HD, "raw")
LOGS = os.path.join(HD, "logs")
UA = {"User-Agent": "Mozilla/5.0 (compatible; planograma-divina-terra/1.0)", "Accept": "application/json,*/*"}
INTERVALO = 0.4  # segundos entre requisicoes no mesmo dominio (2,5 por segundo)

# ---------------------------------------------------------------- fontes
# rank menor = preferida. "marca" = loja de uma marca so (vendor vazio assume essa marca).
FONTES = {
    "divinaterra": {"tipo": "vtex_tudo", "host": "www.lojadivinaterra.com.br", "rank": 0},
    "essential": {"tipo": "magento", "host": "www.essentialnutrition.com.br", "rank": 1, "marca": "ESSENTIAL NUTRITION"},
    "oceandrop": {"tipo": "magento", "host": "www.oceandrop.com.br", "rank": 1, "marca": "OCEAN DROP"},
    "vitafor": {"tipo": "vtex_tudo", "host": "www.vitafor.com.br", "rank": 1, "marca": "VITAFOR"},
    "nutrify": {"tipo": "vtex_tudo", "host": "www.nutrify.com.br", "rank": 1, "marca": "NUTRIFY"},
    "central": {"tipo": "vtex_tudo", "host": "www.centralnutrition.com.br", "rank": 1, "marca": "CENTRAL NUTRITION"},
    "sanavita": {"tipo": "vtex_tudo", "host": "www.sanavita.com.br", "rank": 1, "marca": "SANAVITA"},
    "true": {"tipo": "shopify", "host": "vivatrue.com.br", "rank": 1, "marca": "TRUE SOURCE"},
    "bold": {"tipo": "shopify", "host": "www.boldsnacks.com.br", "rank": 1, "marca": "BOLD"},
    "caffeine": {"tipo": "shopify", "host": "www.caffeinearmy.com.br", "rank": 1},  # vende Koala e Sublyme: vale o vendor
    "guday": {"tipo": "shopify", "host": "guday.com.br", "rank": 1, "marca": "GUDAY"},
    "pincbar": {"tipo": "shopify", "host": "pincbar.com.br", "rank": 1, "marca": "PINCBAR"},
    "sublyme": {"tipo": "shopify", "host": "www.sublyme.com.br", "rank": 1, "marca": "SUBLYME"},
    "liquidz": {"tipo": "shopify", "host": "www.liquidz.com.br", "rank": 1, "marca": "LIQUIDIZ"},
    "yosen": {"tipo": "shopify", "host": "www.yosen.com.br", "rank": 1, "marca": "YOSEN"},
    "aconfiteria": {"tipo": "shopify", "host": "www.aconfiteria.com.br", "rank": 1, "marca": "A CONFITERIA"},
    "alpacas": {"tipo": "shopify", "host": "www.alpacasfoods.com.br", "rank": 1, "marca": "ALPACAS"},
    "winstage": {"tipo": "shopify", "host": "www.winstage.com.br", "rank": 1, "marca": "WINSTAGE"},
    "bendu": {"tipo": "shopify", "host": "www.bendu.com.br", "rank": 1, "marca": "BENDU"},
    "iamani": {"tipo": "shopify", "host": "www.iamani.com.br", "rank": 1, "marca": "IAMANI"},
    "haoma": {"tipo": "shopify", "host": "www.haoma.com.br", "rank": 1, "marca": "HAOMA"},
    "pod": {"tipo": "shopify", "host": "www.pod.com.br", "rank": 1, "marca": "POD"},
    "dux": {"tipo": "shopify", "host": "duxnutrition.com", "rank": 1, "marca": "DUX"},
    "chamel": {"tipo": "woo", "host": "www.chamel.com.br", "rank": 1, "marca": "CHAMEL"},
    "puroeleve": {"tipo": "woo", "host": "www.puroeleve.com.br", "rank": 1, "marca": "PURO E LEVE"},
    "veganutris": {"tipo": "woo", "host": "www.veganutris.com.br", "rank": 1, "marca": "VEGANUTRIS"},
    "pacheco": {"tipo": "vtex_marcas", "host": "www.drogariaspacheco.com.br", "rank": 3},
    "dsp": {"tipo": "vtex_marcas", "host": "www.drogariasaopaulo.com.br", "rank": 3},
    "paguemenos": {"tipo": "vtex_marcas", "host": "www.paguemenos.com.br", "rank": 3},
    "rede": {"tipo": "vtex_marcas", "host": "www.lojasrede.com.br", "rank": 4},
    "drogal": {"tipo": "vtex_marcas", "host": "www.drogal.com.br", "rank": 4},
    "americanas": {"tipo": "vtex_marcas", "host": "www.americanas.com.br", "rank": 5},
    "naturaldaterra": {"tipo": "vtex_marcas", "host": "www.naturaldaterra.com.br", "rank": 2},
    "oba": {"tipo": "vtex_marcas", "host": "www.obahortifruti.com.br", "rank": 2},
    "extrafarma": {"tipo": "vtex_marcas", "host": "www.extrafarma.com.br", "rank": 3},
    "supernosso": {"tipo": "vtex_marcas", "host": "www.supernosso.com", "rank": 3},
    "mambo": {"tipo": "vtex_marcas", "host": "www.mambo.com.br", "rank": 3},
    "giassi": {"tipo": "vtex_marcas", "host": "www.giassi.com.br", "rank": 3},
    "savegnago": {"tipo": "vtex_marcas", "host": "www.savegnago.com.br", "rank": 4},
    "bistek": {"tipo": "vtex_marcas", "host": "www.bistek.com.br", "rank": 4},
    "covabra": {"tipo": "vtex_marcas", "host": "www.covabra.com.br", "rank": 4},
    "indiana": {"tipo": "vtex_marcas", "host": "www.farmaciaindiana.com.br", "rank": 4},
    "drogaleste": {"tipo": "vtex_marcas", "host": "www.drogaleste.com.br", "rank": 4},
    "dux_site": {"tipo": "sitemap", "host": "duxhumanhealth.com", "rank": 1, "marca": "DUX"},
    "nutrata_site": {"tipo": "sitemap", "host": "nutrata.com.br", "rank": 1, "marca": "NUTRATA"},
    "glulac_site": {"tipo": "sitemap", "host": "www.glulac.com.br", "rank": 1, "marca": "GLULAC"},
    "adaptogen_site": {"tipo": "sitemap", "host": "www.adaptogen.com.br", "rank": 1, "marca": "ADAPTOGEN SCIENCE"},
    "integral_site": {"tipo": "sitemap", "host": "www.integralmedica.com.br", "rank": 1, "marca": "INTEGRALMEDICA"},
    "colorandina_site": {"tipo": "sitemap", "host": "www.colorandinafoods.com.br", "rank": 1, "marca": "COLOR ANDINA FOODS"},
    "apisflora_site": {"tipo": "sitemap", "host": "www.apisflora.com.br", "rank": 1, "marca": "APIS FLORA"},
    "evolve_site": {"tipo": "sitemap", "host": "www.lojaevolve.com.br", "rank": 1, "marca": "EVOLVE"},
    "belive_site": {"tipo": "sitemap", "host": "belive.com.br", "rank": 1, "marca": "BELIVE"},
    "tocca_site": {"tipo": "sitemap", "host": "www.tocca.com.br", "rank": 1, "marca": "TOCCA"},
    "equaliv_site": {"tipo": "sitemap", "host": "www.equaliv.com.br", "rank": 1, "marca": "EQUALIV"},
    "precopopular": {"tipo": "vtex_marcas", "host": "www.precopopular.com.br", "rank": 3},
    "harts": {"tipo": "shopify", "host": "www.hartsnatural.com", "rank": 1, "marca": "HARTS"},
    "laganexa": {"tipo": "shopify", "host": "lojalaganexa.com.br", "rank": 1, "marca": "LA GANEXA"},
    "uevo": {"tipo": "shopify", "host": "uevo.com.br", "rank": 1, "marca": "UEVO"},
    "underlabz": {"tipo": "shopify", "host": "underlabz.com.br", "rank": 1, "marca": "UNDER LABZ"},
    "elementopuro": {"tipo": "shopify", "host": "www.elementopuro.com.br", "rank": 1, "marca": "ELEMENTO PURO"},
    "blackskull": {"tipo": "vtex_tudo", "host": "www.blackskullusa.com.br", "rank": 1, "marca": "BLACK SKULL"},
    "vitalin": {"tipo": "woo", "host": "vitalin.com.br", "rank": 1, "marca": "VITALIN"},
    "sesamoreal": {"tipo": "shopify", "host": "www.sesamoreal.com.br", "rank": 1, "marca": "SESAMO REAL"},
    "madrugao": {"tipo": "woo", "host": "www.madrugaosuplementos.com.br", "rank": 5},
    "lojasuplemento": {"tipo": "woo", "host": "www.lojadosuplemento.com.br", "rank": 5},
}

# ---------------------------------------------------------------- http educado
_travas = defaultdict(threading.Lock)
_ultimo = defaultdict(float)
_mortos = {}
_robots = {}
_robots_lock = threading.Lock()


def _espera(dom):
    with _travas[dom]:
        falta = _ultimo[dom] + INTERVALO - time.time()
        if falta > 0:
            time.sleep(falta)
        _ultimo[dom] = time.time()


def _baixa(url, timeout):
    """requests com recurso ao curl quando o LibreSSL do Python 3.9 nao fecha o TLS."""
    try:
        # paginas de produto e sitemap pedem HTML: com Accept de JSON alguns servidores devolvem so um resumo
        cab = dict(UA)
        if not re.search(r"/api/|\.json|/graphql|/wp-json/", url):
            cab["Accept"] = "text/html,application/xhtml+xml,image/*,*/*;q=0.8"
        r = requests.get(url, headers=cab, timeout=timeout)
        return r.status_code, r.content
    except requests.exceptions.SSLError:
        p = subprocess.run(
            ["curl", "-sL", "-m", str(timeout), "-A", UA["User-Agent"], "-w", "\n%{http_code}", url],
            capture_output=True,
        )
        corpo, _, cod = p.stdout.rpartition(b"\n")
        return int(cod or 0), corpo


def http(url, timeout=25, tentativas=3):
    dom = urllib.parse.urlparse(url).netloc
    if dom in _mortos:
        return None, None
    for i in range(tentativas):
        _espera(dom)
        try:
            cod, corpo = _baixa(url, timeout)
        except Exception:
            time.sleep(2 + 3 * i)
            continue
        if cod == 429 or cod == 503:
            time.sleep(20 * (i + 1))
            continue
        if cod == 403:
            _mortos[dom] = "403"
            log(f"dominio {dom} respondeu 403, parando esse dominio")
            return 403, None
        return cod, corpo
    if tentativas > 1:
        _falhas_dom[dom] += 1
        if _falhas_dom[dom] >= 4:
            _mortos[dom] = "falhas/429"
            log(f"dominio {dom} falhou repetidamente, parando esse dominio")
    return None, None


_falhas_dom = Counter()


def http_json(url, **kw):
    cod, corpo = http(url, **kw)
    if corpo is None or cod not in (200, 206):
        return None
    try:
        return json.loads(corpo)
    except Exception:
        return None


def permitido(host, caminho):
    """Regras de Disallow do robots.txt para User-agent: * (com curinga)."""
    with _robots_lock:
        regras = _robots.get(host)
        if regras is None:
            regras = []
            cod, corpo = http(f"https://{host}/robots.txt", timeout=15, tentativas=1)
            if corpo and cod == 200:
                ativo = False
                for l in corpo.decode("utf8", "ignore").splitlines():
                    l = l.split("#")[0].strip()
                    if l.lower().startswith("user-agent:"):
                        ativo = l.split(":", 1)[1].strip() == "*"
                    elif ativo and l.lower().startswith("disallow:"):
                        v = l.split(":", 1)[1].strip()
                        if v:
                            regras.append(re.compile(re.escape(v).replace(r"\*", ".*").replace(r"\$", "$")))
            _robots[host] = regras
    return not any(r.match(caminho) for r in regras)


LOG_LOCK = threading.Lock()


def log(msg):
    with LOG_LOCK:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------- coleta
def cat_vtex_item(p, fonte, host):
    saida = []
    for it in p.get("items", []):
        imgs = [i.get("imageUrl") for i in it.get("images", []) if i.get("imageUrl")]
        if not imgs:
            continue
        nome = (it.get("nameComplete") or "").strip() or p.get("productName", "")
        if p.get("productName") and p["productName"].lower() not in nome.lower():
            nome = p["productName"] + " " + nome
        ref = p.get("productReference") or ""
        refs = [r.get("Value") for r in (it.get("referenceId") or []) if r.get("Value")]
        saida.append(
            {"f": fonte, "n": nome, "m": p.get("brand", ""), "u": p.get("link", ""), "i": imgs[:3], "r": list({ref, *refs})}
        )
    return saida


def h_vtex_tudo(fonte, host):
    if not permitido(host, "/api/catalog_system/pub/products/search"):
        log(f"{fonte}: robots proibe a API, pulando")
        return []
    arv = http_json(f"https://{host}/api/catalog_system/pub/category/tree/3") or []
    folhas = []

    def anda(c, path):
        p = path + "/" + str(c["id"])
        if c.get("children"):
            for k in c["children"]:
                anda(k, p)
        else:
            folhas.append(p + "/")

    for c in arv:
        anda(c, "")
    vistos, saida = set(), []
    for fq in folhas or [None]:
        ini = 0
        while ini < 2500:
            q = f"fq=C:{fq}&" if fq else ""
            j = http_json(f"https://{host}/api/catalog_system/pub/products/search?{q}_from={ini}&_to={ini+49}")
            if not j:
                break
            for p in j:
                if p["productId"] not in vistos:
                    vistos.add(p["productId"])
                    saida += cat_vtex_item(p, fonte, host)
            if len(j) < 50:
                break
            ini += 50
    return saida


def h_vtex_marcas(fonte, host):
    if not permitido(host, "/api/catalog_system/pub/products/search"):
        log(f"{fonte}: robots proibe a API, pulando")
        return []
    marcas_sku = [m for m, _ in Counter(x["marca"] for x in carrega_skus() if x["marca"] != "A GRANEL").most_common()]
    lista = http_json(f"https://{host}/api/catalog_system/pub/brand/list") or []
    por_nome = defaultdict(list)
    for b in lista:
        por_nome[chave_marca(b.get("name", ""))].append(b["id"])
    saida, vistos = [], set()
    for m in marcas_sku:
        ids = por_nome.get(chave_marca(m), [])
        for al in ALIAS_MARCA.get(chave_marca(m), []):
            ids = ids + por_nome.get(al, [])
        for bid in dict.fromkeys(ids):
            ini = 0
            while ini < 500:
                j = http_json(f"https://{host}/api/catalog_system/pub/products/search?fq=B:{bid}&_from={ini}&_to={ini+49}")
                if not j:
                    break
                for p in j:
                    if p["productId"] not in vistos:
                        vistos.add(p["productId"])
                        saida += cat_vtex_item(p, fonte, host)
                if len(j) < 50:
                    break
                ini += 50
    return saida


def h_shopify(fonte, host):
    if not permitido(host, "/products.json"):
        log(f"{fonte}: robots proibe /products.json, pulando")
        return []
    saida = []
    pag = 1
    while pag < 40:
        j = http_json(f"https://{host}/products.json?limit=250&page={pag}")
        if not j or not j.get("products"):
            break
        for p in j["products"]:
            imgs = [i["src"] for i in p.get("images", []) if i.get("src")]
            if not imgs:
                continue
            vs = p.get("variants", [])
            url = f"https://{host}/products/{p['handle']}"
            if len(vs) <= 1:
                saida.append({"f": fonte, "n": p["title"], "m": p.get("vendor", ""), "u": url, "i": imgs[:3], "r": [v.get("sku") or "" for v in vs]})
                continue
            for v in vs:
                fi = (v.get("featured_image") or {}).get("src")
                saida.append(
                    {
                        "f": fonte,
                        "n": f"{p['title']} {v.get('title','')}",
                        "m": p.get("vendor", ""),
                        "u": url,
                        "i": [fi] if fi else imgs[:1],
                        "r": [v.get("sku") or ""],
                        "compart": not fi,
                    }
                )
        pag += 1
    return saida


def h_woo(fonte, host):
    if not permitido(host, "/wp-json/wc/store/products"):
        log(f"{fonte}: robots proibe a API, pulando")
        return []
    saida = []
    pag = 1
    while pag < 40:
        j = http_json(f"https://{host}/wp-json/wc/store/products?per_page=100&page={pag}")
        if not j or not isinstance(j, list):
            break
        for p in j:
            imgs = [i.get("src") for i in p.get("images", []) if i.get("src")]
            if imgs:
                saida.append({"f": fonte, "n": html.unescape(p.get("name", "")), "m": " ".join(b.get("name", "") for b in p.get("brands", []) or []), "u": p.get("permalink", ""), "i": imgs[:3], "r": [p.get("sku") or ""]})
        if len(j) < 100:
            break
        pag += 1
    return saida


GQL = """{products(filter:{category_id:{eq:"%s"}},pageSize:100,currentPage:%d){total_count items{name sku url_key url_suffix small_image{url} media_gallery{url position disabled}}}}"""
GQL_CAT = """{categoryList{id children{id children{id}}}}"""


def h_magento(fonte, host):
    if not permitido(host, "/graphql"):
        log(f"{fonte}: robots proibe /graphql, pulando")
        return []
    saida, vistos = [], set()
    arv = http_json(f"https://{host}/graphql?query={urllib.parse.quote(GQL_CAT)}") or {}
    ids = []
    for c in ((arv.get("data") or {}).get("categoryList") or []):
        ids.append(c["id"])
        for d in c.get("children") or []:
            ids.append(d["id"])
            ids += [e["id"] for e in d.get("children") or []]
    for cid in ids:
        pag = 1
        while pag < 12:
            q = urllib.parse.quote(GQL % (cid, pag))
            j = http_json(f"https://{host}/graphql?query={q}")
            prods = ((j or {}).get("data") or {}).get("products") or {}
            items = prods.get("items") or []
            for p in items:
                if p["sku"] in vistos:
                    continue
                vistos.add(p["sku"])
                gal = sorted([m for m in (p.get("media_gallery") or []) if not m.get("disabled")], key=lambda m: m.get("position") or 0)
                imgs = [m["url"] for m in gal if m.get("url")] or ([p["small_image"]["url"]] if p.get("small_image") else [])
                imgs = [re.sub(r"/cache/[^/]+/", "/", i) for i in imgs]
                if imgs:
                    saida.append({"f": fonte, "n": p["name"], "m": "", "u": f"https://{host}/{p.get('url_key','')}{p.get('url_suffix') or ''}", "i": imgs[:3], "r": [p["sku"]]})
            if len(items) < 100:
                break
            pag += 1
    return saida


def _urls_sitemap(url, prof=0):
    cod, corpo = http(url, timeout=25, tentativas=1)
    if not corpo or cod != 200:
        return []
    if url.endswith(".gz") or corpo[:2] == b"\x1f\x8b":
        try:
            corpo = gzip.decompress(corpo)
        except Exception:
            return []
    t = corpo.decode("utf8", "ignore")
    locs = [html.unescape(x.strip()) for x in re.findall(r"<loc>\s*(.*?)\s*</loc>", t)]
    if "<sitemapindex" in t and prof < 2:
        saida = []
        for l in locs:
            if re.search(r"(post|blog|page|categor|tag|author|taxonom)", l, re.I):
                continue
            saida += _urls_sitemap(l, prof + 1)
        return saida
    return locs


def h_sitemap(fonte, host):
    urls = _urls_sitemap(f"https://{host}/sitemap.xml") or _urls_sitemap(f"https://{host}/sitemap_index.xml")
    urls = [u for u in dict.fromkeys(urls) if not re.search(r"/(blog|categoria|category|collections?|tag|author|conta|account|politica|page|paginas?)(/|$)|\.(jpg|png|webp)$", u, re.I)]
    prod = [u for u in urls if re.search(r"/(produtos?|products?)/|/p/?$", u)]
    urls = (prod or urls)[:500]
    log(f"{fonte}: {len(urls)} paginas no sitemap")
    saida = []
    for u in urls:
        pr = urllib.parse.urlparse(u)
        if not permitido(host, pr.path):
            continue
        cod, corpo = http(u, timeout=20, tentativas=1)
        if not corpo or cod != 200:
            continue
        t = corpo.decode("utf8", "ignore")
        nome, imgs = None, []
        for bloco in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', t, re.S):
            try:
                d = json.loads(bloco.strip())
            except Exception:
                continue
            for o in d if isinstance(d, list) else (d.get("@graph") or [d] if isinstance(d, dict) else []):
                if isinstance(o, dict) and "Product" in str(o.get("@type")):
                    nome = o.get("name") or nome
                    im = o.get("image")
                    if isinstance(im, dict):
                        im = im.get("url")
                    imgs = ([im] if isinstance(im, str) else [x if isinstance(x, str) else (x or {}).get("url", "") for x in (im or [])]) or imgs
        og = dict(re.findall(r'<meta[^>]+property=["\']og:(title|image|type)["\'][^>]+content=["\']([^"\']*)', t))
        if not nome and (og.get("type", "").lower().startswith("product") or re.search(r"/(produtos?|products?)/|/p/?$", u)):
            nome = re.sub(r"\s[-|]\s[^-|]{2,30}$", "", og.get("title") or "") or None
        if not nome:
            continue
        if not imgs and og.get("image"):
            imgs = [og["image"]]
        imgs = [("https:" + i if i.startswith("//") else i) for i in imgs if i]
        if imgs:
            saida.append({"f": fonte, "n": html.unescape(nome), "m": "", "u": u, "i": imgs[:3], "r": []})
    return saida


COLETORES = {"sitemap": h_sitemap, "vtex_tudo": h_vtex_tudo, "vtex_marcas": h_vtex_marcas, "shopify": h_shopify, "woo": h_woo, "magento": h_magento}


def harvest_um(fonte):
    cfg = FONTES[fonte]
    caminho = os.path.join(CATALOGOS, fonte + ".json")
    if not os.environ.get("FORCA") and os.path.exists(caminho) and os.path.getsize(caminho) > 2 and time.time() - os.path.getmtime(caminho) < 86400:
        return fonte, "cache"
    t = time.time()
    try:
        cat = COLETORES[cfg["tipo"]](fonte, cfg["host"])
    except Exception as e:
        log(f"{fonte}: erro {type(e).__name__}: {e}")
        cat = []
    if cat:
        tmp = caminho + ".tmp"
        json.dump(cat, open(tmp, "w"), ensure_ascii=False)
        os.replace(tmp, caminho)
    log(f"{fonte}: {len(cat)} itens em {time.time()-t:.0f}s")
    return fonte, len(cat)


def harvest(nomes=None):
    os.makedirs(CATALOGOS, exist_ok=True)
    nomes = nomes or list(FONTES)
    with cf.ThreadPoolExecutor(24) as ex:
        list(ex.map(harvest_um, nomes))


def carrega_catalogos():
    tudo = []
    for f in FONTES:
        c = os.path.join(CATALOGOS, f + ".json")
        if os.path.exists(c):
            tudo += json.load(open(c))
    for c in tudo:  # a Caffeine Army vende sticks sob o vendor "Material Experiencia"
        if c["f"] == "caffeine" and "material" in (c.get("m") or "").lower():
            n = c["n"].lower()
            c["m"] = "Koala" if "koala" in n else "Sublyme" if "morning shot" in n else "Liquidiz" if "liquid" in n else "Caffeine Army"
    return tudo


# ---------------------------------------------------------------- normalizacao
def carrega_skus():
    return json.load(open(ENTRADA))


@functools.lru_cache(maxsize=200000)
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    s = s.replace("&", " E ").replace("+", " MAIS ")
    s = re.sub(r"\bS/\s*", "SEM ", s)
    s = re.sub(r"\bC/\s*", "COM ", s)
    s = re.sub(r"\bP/\s*", "PARA ", s)
    s = re.sub(r"(\d)[,.](\d)", r"\1#\2", s)  # guarda decimal
    s = re.sub(r"[^A-Z0-9#]+", " ", s)
    return s.replace("#", ".").strip()


_cm = {}


def chave_marca(m):
    if m in _cm:
        return _cm[m]
    _cm[m] = r = _chave_marca(m)
    return r


def _chave_marca(m):
    t = norm(m)
    t = re.sub(r"\b(NUTRITION|FOODS|FOOD|NATURAL|SUPLEMENTOS|ALIMENTOS|BRASIL|LAB|HUMAN HEALTH)\b", " ", t)
    return re.sub(r"[^A-Z0-9]", "", t)


ALIAS_MARCA = {
    "TRUESOURCE": ["TRUE", "VIVATRUE"],
    "POD": ["PODKOMBUCHA"],
    "BOLD": ["BOLDSNACKS"],
    "NOW": ["NOWFOODS"],
    "DRPEANUT": ["DRPEANUTT"],
    "CAFFEINEARMY": ["CAFFEINE"],
    "ADAPTOGENSCIENCE": ["ADAPTOGEN"],
    "LIQUIDIZ": ["LIQUIDZ"],
    "DESINCHA": ["DESINCHAA"],
    "NUDE": ["NUDEBEBIDAS"],
    "ATALDACASTANHA": ["TALDACASTANHA"],
}


def marca_ok(sku_marca, cand_marca, marca_loja=None):
    a = chave_marca(sku_marca)
    if marca_loja and chave_marca(marca_loja) != a:
        return False
    if not cand_marca.strip():
        return bool(marca_loja)
    b = chave_marca(cand_marca)
    if a == b or b in ALIAS_MARCA.get(a, []):
        return True
    if marca_loja:  # loja de uma marca so, vendor costuma ser a razao social
        return True
    return False


TAM_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(KGS?|KILOS?|GRAMAS|GRS?|G|MLS?|LITROS?|LTS?|L|MGS?|MCG|"
    r"CAPSULAS?|CAPS?|CPS?|COMPRIMIDOS?|COMP|TABLETES?|TABS?|SOFTGELS?|SOFT|VEGCAPS?|GOMAS?|GUMMIES|PASTILHAS?|"
    r"DOSES?|SERVINGS?|PORCOES|PORCAO|"
    r"UNIDADES?|UNID|UNDS?|UNI|UN|SACHES?|SACHETS?|STICKS?|BARRAS?|LATAS?)\b"
)


@functools.lru_cache(maxsize=200000)
def tamanhos(n):
    """Extrai medidas de um nome ja normalizado."""
    t = {}
    for num, un in TAM_RE.findall(n):
        v = float(num)
        if un.startswith(("KG", "KILO")):
            t["peso"] = v * 1000
        elif un in ("G", "GR", "GRS", "GRAMAS"):
            t["peso"] = v
        elif un.startswith("ML"):
            t["peso"] = v
        elif un in ("L", "LT", "LTS") or un.startswith("LITRO"):
            t["peso"] = v * 1000
        elif un.startswith(("MG", "MCG")):
            t["mg"] = v
        elif un.startswith(("CAP", "CP", "COMP", "TAB", "SOFT", "VEGCAP", "GOMA", "GUMM", "PAST")):
            t["caps"] = v
        elif un.startswith(("DOSE", "SERV", "PORC")):
            t["doses"] = v
        else:
            t["uni"] = v
    return t


PALAVRA_FIXA = [
    (r"\bOMEGA\s*3\b", "OMEGA3"), (r"\bOMEGA\s*6\b", "OMEGA6"), (r"\bOMEGA\s*7\b", "OMEGA7"),
    (r"\bQ\s*10\b", "COQ10"), (r"\bCOENZIMA\b", ""), (r"\bCO\s*Q10\b", "COQ10"),
    (r"\bVITAMINA\s+", "VIT"), (r"\bVIT\.?\s+([A-Z]\d?)\b", r"VIT\1"),
    (r"\bSUPER\s*COFFEE\b", "SUPERCOFFEE"), (r"\bBEAUTY\s*IN\b", "BEAUTYIN"),
    (r"\bHI\s*WHEY\b", "HIWHEY"), (r"\bH\s*I\s*WHEY\b", "HIWHEY"), (r"\bWHEY\s*H\s*I\b", "HIWHEY"),
    (r"\bLINGUA DE GATO\b", "LINGUADEGATO"), (r"\bPASTA DE\b", "PASTA"),
    (r"\bCOOKIES? (AND|E|N) CREAM\b", "COOKIESCREAM"), (r"\bCOOKIES? N CREAM\b", "COOKIESCREAM"),
    (r"\bLEITE EM PO\b", "LEITEPO"), (r"\bSEM SAL\b", "SEMSAL"), (r"\bCOM SAL\b", "COMSAL"),
    (r"\bSEM ACUCAR\b", "ZEROACUCAR"), (r"\bZERO ACUCAR\b", "ZEROACUCAR"), (r"\b0 ACUCAR\b", "ZEROACUCAR"),
    (r"\bSEM GLUTEN\b", ""), (r"\bSEM LACTOSE\b", ""), (r"\bGLUTEN FREE\b", ""),
    (r"\bFRUTAS VERMELHAS\b", "FRUTASVERMELHAS"), (r"\bRED FRUITS?\b", "FRUTASVERMELHAS"), (r"\bBERRIES\b", "FRUTASVERMELHAS"),
    (r"\bFRUTAS TROPICAIS\b", "FRUTASTROPICAIS"), (r"\bMACA VERDE\b", "MACAVERDE"), (r"\bGREEN APPLE\b", "MACAVERDE"),
    (r"\bDOCE DE LEITE\b", "DOCEDELEITE"), (r"\bCREME DE AVELA\b", "CREMEAVELA"),
    (r"\bCHOCOLATE AO LEITE\b", "CHOCOLATEAOLEITE"), (r"\bCHOCOLATE BRANCO\b", "CHOCOLATEBRANCO"), (r"\bWHITE CHOCOLATE\b", "CHOCOLATEBRANCO"),
    (r"\bDARK CHOCOLATE\b", "CHOCOLATEDARK"), (r"\bCHOCOLATE AMARGO\b", "CHOCOLATEAMARGO"), (r"\bCHOCOLATE BELGA\b", "CHOCOLATEBELGA"),
    (r"\bAGUA DE COCO\b", "AGUACOCO"), (r"\bOLEO DE COCO\b", "OLEOCOCO"), (r"\bACUCAR DE COCO\b", "ACUCARCOCO"),
    (r"\bMANTEIGA DE\b", "MANTEIGA"), (r"\bFARINHA DE\b", "FARINHA"), (r"\bCHOCOLATE LINGUA DE GATO\b", "LINGUADEGATO"), (r"\bTRUE WHEY\b", "WHEY"), (r"\bTRUEBEEF\b", "BEEF"), (r"\bLINHA STEVIA\b", " "), (r"\bTIRA MORA\b", "TIRINHA MORANGA"), (r"\bW100 WHEY CONCENTRADO\b", "W100"), (r"\bPINC BAR\b", "PINCBAR"), (r"\bBARRA PROT\b", " "),
    (r"\bW100 CONCENTRADO\b", "W100"), (r"\bWHEY W100\b", "W100"), (r"\bCOLLAGEN PROTEIN HYDROLIZED\b", "COLLAGEN PROTEIN"),
    (r"\bWHEYPRIME\b", "WHEY PRIME"), (r"\bTASTYWHEY\b", "TASTY WHEY"),
]
SINONIMO = {
    "VANILLA": "BAUNILHA", "VANILA": "BAUNILHA", "STRAWBERRY": "MORANGO", "COCONUT": "COCO", "PEANUT": "AMENDOIM",
    "CREATINE": "CREATINA", "COLLAGEN": "COLAGENO", "PROTEINA": "PROTEIN", "PROTEINAS": "PROTEIN", "ISOLATE": "ISOLADO",
    "HIDROLIZED": "HIDROLISADO", "HYDROLIZED": "HIDROLISADO", "HYDROLYZED": "HIDROLISADO", "HIDROLIZADO": "HIDROLISADO",
    "VEGETAL": "VEGAN", "CONC": "CONCENTRADO", "TANJERINA": "TANGERINA", "ICECREAM": "ICE", "CHOCO": "CHOCOLATE", "CHOC": "CHOCOLATE", "CACAO": "CACAU", "COFFEE": "CAFE", "CAPUCCINO": "CAPPUCCINO", "CAPUCINO": "CAPPUCCINO",
    "CHESSECAKE": "CHEESECAKE", "PISTACHIO": "PISTACHE", "LEMON": "LIMAO", "ORANGE": "LARANJA", "PASSION": "MARACUJA",
    "TANGERINE": "TANGERINA", "GRAPE": "UVA", "BANANAS": "BANANA", "MAGNESIUM": "MAGNESIO", "ZINCO": "ZINCO", "IRON": "FERRO",
    "VEGANA": "VEGAN", "VEGANO": "VEGAN", "SACHE": "SACHE", "BEEF": "BEEF", "BARRINHA": "BARRA", "BAR": "BARRA", "SNACK": "BARRA",
    "ORIGINAL": "ORIGINAL", "TRADICIONAL": "ORIGINAL", "CLASSIC": "ORIGINAL", "CLASSICO": "ORIGINAL", "UNFLAVORED": "NEUTRO",
    "SEMSABOR": "NEUTRO", "NATURAL": "NATURAL", "CASTANHAS": "CASTANHA", "AMENDOAS": "AMENDOA", "SEMENTES": "SEMENTE",
    "MACADAMIA": "MACADAMIA", "ICE": "ICE",
}
GENERICO = set(
    """DE DA DO DAS DOS COM E EM A O AO NO NA OS AS PARA POR SABOR SABORES SUPLEMENTO SUPLEMENTOS ALIMENTAR ALIMENTO
    PO POTE LATA REFIL POUCH EMBALAGEM NOVA NOVO UNICO UNICA PADRAO U VERSAO FORMULA FRASCO CAIXINHA TUBO
    BRANCA GARRAFA PACOTE SACO SACHET VIDRO CAPSULA CAPSULAS CAPS CAP SOFTGEL SOFTGELS GOMAS GOMA GUMMIES COMPRIMIDO COMPRIMIDOS
    UNIDADE UNIDADES UN UNI UND UNID G GR KG ML L MG MCG DOSE DOSES TABS TABLETES CP CPS
    PROTEIN WHEY EM MONOHIDRATADA CREAPURE CREATINA SUPLEMENTACAO LINHA PURO PURA NUTRICAO SAUDE BEM ESTAR ENERGIA FORCA
    VEGANO SEMGLUTEN PCT UNITARIO INDIVIDUAL REFIL 100 PURE ELETROLITO COMPANY INSTANTANEO PROT V2 V3 INTEGRAL COMPRA MENSAL BIMESTRAL TRIMESTRAL SEMESTRAL FREQUENCIA MESE MES""".split()
)
DESCR_CAND = set("GOTA ZEROACUCAR OMEGA3 CAFE SOLUVEL LIQUIDO ASSINATURA TG SUPLEMENTO NATURAL TRADICIONAL YDROSOLV BIOMAX BODYBALANCE".split())
# palavras que mudam a linha do produto: se sobrarem de um lado so, nunca e o mesmo produto
LINHA = set(
    """SUPER ULTRA PLUS PRO MAX ZERO KIDS BABY ISO ISOLADO HIDRO CONCENTRADO GOLD BLACK LIGHT LIFE ADVANCED FORTE COMPLEX
    KETO SHOT VEGAN BEEF COLAGENO MINI TRAVEL PREMIUM SPORT ACTIVE IMMUNO IMUNO BEAUTY HAIR MEN WOMAN WOMEN""".split()
)
SABOR = set(
    """CHOCOLATE CHOCOLATEAOLEITE CHOCOLATEBRANCO CHOCOLATEDARK CHOCOLATEAMARGO CHOCOLATEBELGA CACAU BAUNILHA MORANGO COCO BANANA LIMAO LIMONADA
    MARACUJA LARANJA UVA TANGERINA ABACAXI MANGA FRAMBOESA CRANBERRY HIBISCO FRUTASVERMELHAS FRUTASTROPICAIS MACAVERDE MACA
    NEUTRO DOCEDELEITE AMENDOIM AVELA PISTACHE CAPPUCCINO CAFE CARAMELO SALGADO BEIJINHO LINGUADEGATO COOKIESCREAM COOKIES
    BANOFFEE CHEESECAKE BERRY CITRU CITRUS HORTELA CAPIM MACCHIATO TRUFFLE TRUFA LEITINHO MILKSHAKE SPECULOOS PAOMEL SMORE KIWI AMORA MIRTILO BLUEBERRY LAVANDA CAMOMILA CANELA GENGIBRE MENTA ROMA PESSEGO MELANCIA ACAI GOIABADA BRIGADEIRO LAJOTINHA MACADAMIA TIRAMISU NUTELLA PACOCA""".split()
)
KIT_RE = re.compile(r"\b(KIT|COMBO|LEVE \d|PAGUE \d|DUO|PACK|CAIXA|DISPLAY|GANHE|BRINDE|AMOSTRA|REVENDA|PROMOCAO|\d+X|ATACADINHO)\b")
NAO_CASAR = {"58899"}  # conferido a mao: fonte e outra formula
FREQ_RE = re.compile(r"\b(MENSAL|BIMESTRAL|TRIMESTRAL|SEMESTRAL|FREQUENCIA|COMPRA UNICA|ASSINATURA)\b")
KIT_SEG = re.compile(r"^\d+\s")


@functools.lru_cache(maxsize=200000)
def tokens_produto(texto, marca=""):
    n = norm(texto)
    n = TAM_RE.sub(" ", n)
    for a, b in PALAVRA_FIXA:
        n = re.sub(a, b, n)
    marca_t = set(norm(marca).split()) - {"A", "O", "E", "DE", "DA", "DO"}
    for al in ALIAS_MARCA.get(chave_marca(marca), []):
        marca_t.add(al)
    saida = []
    for t in n.split():
        if t in marca_t:
            continue
        if len(t) > 4 and t.endswith("S"):
            t = t[:-1]
        t = SINONIMO.get(t, t)
        saida.append(t)
    return saida


@functools.lru_cache(maxsize=2000000)
def iguais(a, b):
    if a == b:
        return True
    if a in SABOR and b in SABOR:  # CHOCOLATE nao e CHOCOLATEBRANCO
        return False
    if len(a) >= 3 and len(b) >= 3 and (a.startswith(b) or b.startswith(a)):
        return True
    return len(a) >= 4 and len(b) >= 4 and SequenceMatcher(None, a, b).ratio() >= (0.82 if min(len(a), len(b)) >= 6 else 0.88)


def compara(sku, cand):
    """Retorna (conf, motivo, pontos) ou (None, motivo, pontos)."""
    ns, nc = norm(sku["desc"]), norm(cand["n"])
    if str(sku["sku"]) in NAO_CASAR:
        return None, "nao-casar", 0
    if (KIT_RE.search(nc) or re.search(r"\s\+\s", cand["n"])) and not KIT_RE.search(ns):
        return None, "kit", 0
    if KIT_SEG.match(nc) and not KIT_SEG.match(ns):
        return None, "kit-num", 0
    A = [t for t in tokens_produto(sku["desc"], sku["marca"])]
    B = [t for t in tokens_produto(cand["n"], cand.get("m") or sku["marca"])]
    B = [t for t in B if t not in set(norm(sku["marca"]).split())]
    sa, sb = {t for t in A if t in SABOR}, {t for t in B if t in SABOR}
    resto_a = [t for t in A if t not in GENERICO]
    resto_b = [t for t in B if t not in GENERICO]
    falta = [t for t in resto_a if not any(iguais(t, x) for x in B)]
    sobra = [t for t in resto_b if not any(iguais(t, x) for x in A) and t not in DESCR_CAND]
    pontos = (len(resto_a) - len(falta)) - 0.5 * len(sobra)
    motivo = f"falta={falta} sobra={sobra}"
    if any(t in LINHA for t in falta + sobra):
        return None, "linha " + motivo, pontos
    if sa != sb and not all(any(iguais(x, y) for y in sb) for x in sa):
        return None, "sabor " + motivo, pontos
    if sb and not sa:
        return None, "sabor-extra " + motivo, pontos
    if any(not any(iguais(y, x) for x in sa) for y in sb):
        return None, "sabor-a-mais " + motivo, pontos
    # sache/stick x pote sao embalagens diferentes
    pa = tamanhos(ns).get("peso")
    pequeno_sku = bool(pa and pa <= 15)
    formato_b = {t for t in B if t in ("STICK", "SACHE", "GO")}
    if pequeno_sku:
        sobra = [t for t in sobra if t not in ("STICK", "SACHE", "GO")]
    elif formato_b - {"GO"} and "SACHE" not in A and not any(k in tamanhos(ns) for k in ("uni",)):
        return None, "formato " + motivo, pontos
    so_sabor_faltando = bool(falta) and not sobra and all(t in SABOR for t in falta) and not sb
    if (falta and not so_sabor_faltando) or sobra:
        # quase igual: uma palavra de diferenca, duas ou mais em comum e medida identica nos dois lados
        ta0, tb0 = tamanhos(ns), tamanhos(nc)
        iguais_med = [k for k in ta0 if k in tb0 and k != "mg" and abs(ta0[k] - tb0[k]) / max(ta0[k], tb0[k]) <= 0.03]
        if len(falta) + len(sobra) == 1 and len(resto_a) - len(falta) >= 2 and iguais_med and not cand.get("compart"):
            return "media", "quase " + motivo, pontos
        return None, "nome " + motivo, pontos
    # nome igual: agora o tamanho
    ta, tb = tamanhos(ns), tamanhos(nc)
    if not resto_a:
        if resto_b:
            return None, "nome-vazio", 0
        chave_a = {t for t in A if t in ("CREATINA", "WHEY", "PROTEIN", "COLAGENO")}
        if not chave_a or not chave_a & set(B):
            return None, "nome-vazio", 0
    if ta.get("mg") and tb.get("mg") and ta["mg"] != tb["mg"]:
        return None, "dose-mg", pontos
    if pequeno_sku and "peso" in tb and tb["peso"] > 15:
        return None, "formato", pontos
    if pequeno_sku and not formato_b and "peso" not in tb:
        return None, "formato", pontos
    if so_sabor_faltando:
        loja = FONTES[cand["f"]].get("marca")
        if not loja:
            return None, "sabor-omitido " + motivo, pontos
        return "media", "sabor omitido no nome da loja da marca", pontos
    if "doses" in ta and "peso" in tb and "peso" not in ta:
        g = tb["peso"] / ta["doses"]
        if 20 <= g <= 36:
            return "alta", f"{ta['doses']} doses = {tb['peso']} g", pontos
        if 3 <= g <= 45:
            return "media", f"doses x peso {ta} x {tb}", pontos
        return None, "doses-longe", pontos
    comuns = [k for k in ta if k in tb and k != "mg"]
    conflito = [k for k in comuns if abs(ta[k] - tb[k]) / max(ta[k], tb[k]) > 0.03]
    if conflito:
        if "peso" in conflito:
            r = max(ta["peso"], tb["peso"]) / max(1, min(ta["peso"], tb["peso"]))
            if r > 2.5 or min(ta["peso"], tb["peso"]) < 100:
                return None, "tamanho-longe", pontos
        return "media", f"tamanho {ta} x {tb}", pontos
    if not comuns and any(k in ta for k in ("peso", "caps", "doses", "uni")):
        if cand.get("compart") and not FREQ_RE.search(nc):
            return None, "variante-sem-foto", pontos
        return "media", f"tamanho nao confere {ta} x {tb}", pontos
    if cand.get("compart") and not FREQ_RE.search(nc):
        return "media", "foto compartilhada entre variantes", pontos
    return "alta", "ok", pontos


RANK = {f: c["rank"] for f, c in FONTES.items()}


def indice_catalogo(cat):
    por_marca = defaultdict(list)
    por_ref = {}
    for c in cat:
        if c["f"] == "divinaterra":
            for r in c.get("r") or []:
                if r:
                    por_ref[str(r)] = c
        por_marca[chave_marca(c.get("m") or "")].append(c)
    return por_marca, por_ref


def monta_indice(cat):
    """Separa catalogo por loja de marca unica e, nas multimarcas, por chave do vendor."""
    loja, multi = defaultdict(list), defaultdict(list)
    for c in cat:
        m = FONTES[c["f"]].get("marca")
        if m:
            loja[chave_marca(m)].append(c)
        else:
            multi[chave_marca(c.get("m") or "")].append(c)
    return loja, multi


def subconjunto(sku, indice):
    loja, multi = indice
    a = chave_marca(sku["marca"])
    s = list(loja.get(a, [])) + list(multi.get(a, []))
    for al in ALIAS_MARCA.get(a, []):
        s += multi.get(al, [])
    return s


def candidatos_sku(sku, cat, por_ref):
    """Lista ordenada [(conf, cand, motivo)] e melhor rejeicao (para diagnostico)."""
    saida = []
    ref = por_ref.get(str(sku["sku"]))
    if ref:
        a = tokens_produto(sku["desc"], sku["marca"])
        b = tokens_produto(ref["n"], sku["marca"])
        comum = [t for t in a if any(iguais(t, x) for x in b)]
        if comum:
            saida.append(("alta", ref, "ref-exata"))
    rej = (None, "", -9)
    for c in cat:
        loja = FONTES[c["f"]].get("marca")
        if not marca_ok(sku["marca"], c.get("m") or "", loja):
            continue
        conf, mot, pts = compara(sku, c)
        if conf:
            saida.append((conf, c, mot))
        elif pts > rej[2]:
            rej = (c["n"], mot, pts)
    peso = tamanhos(norm(sku["desc"])).get("peso") or 0
    if peso and peso <= 100:
        saida = [x for x in saida if x[1]["f"] != "bold"]
    saida.sort(key=lambda s: (0 if s[0] == "alta" else 1, RANK[s[1]["f"]]))
    return saida, rej


# ---------------------------------------------------------------- imagem
def fundo_liso_para_branco(a, borda):
    """Troca fundo uniforme por branco. Devolve None se o fundo nao for liso (foto de ambiente)."""
    aneis = np.concatenate([a[:borda].reshape(-1, 3), a[-borda:].reshape(-1, 3), a[:, :borda].reshape(-1, 3), a[:, -borda:].reshape(-1, 3)]).astype(np.int16)
    med = np.median(aneis, axis=0)
    if (np.abs(aneis - med).max(axis=1) < 16).mean() < 0.93:
        return None
    perto = np.abs(a.astype(np.int16) - med).max(axis=2) < 22
    rot, _ = ndimage.label(perto)
    tocam = np.unique(np.concatenate([rot[0], rot[-1], rot[:, 0], rot[:, -1]]))
    fundo = np.isin(rot, tocam[tocam > 0])
    if fundo.mean() < 0.25 or fundo.mean() > 0.92:
        return None
    # sobra de sombra colada no objeto: abre o objeto um pouco para nao deixar halo
    fundo = ndimage.binary_dilation(fundo, iterations=2)
    b = a.copy()
    b[fundo] = 255
    return b


def eh_tabela(a, tinta):
    """Tabela nutricional ou tela de texto: quase sem cor e cheia de bordas finas."""
    if tinta.mean() < 0.02:
        return False
    px = a[tinta]
    croma = (px.max(axis=1).astype(int) - px.min(axis=1).astype(int)) > 28
    cinza = np.asarray(Image.fromarray(a).convert("L"), dtype=np.int16)
    bordas = (np.abs(np.diff(cinza, axis=0))[:, :-1] > 70) | (np.abs(np.diff(cinza, axis=1))[:-1, :] > 70)
    medidas = (float(croma.mean()), float(bordas.mean()))
    return medidas[0] < 0.05 and medidas[1] > 0.045


def trata_imagem(dados, fino_ok=False):
    """Abre, valida como pack shot em fundo branco, faz o trim. Retorna (PIL RGB, motivo_reprova)."""
    try:
        im = Image.open(io.BytesIO(dados))
        im.load()
    except Exception:
        return None, "nao-abre"
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        fundo = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(fundo, im).convert("RGB")
    else:
        im = im.convert("RGB")
    if max(im.size) > 1000:
        im.thumbnail((1000, 1000), Image.LANCZOS)
    a = np.asarray(im)
    H, W = a.shape[:2]
    if min(H, W) < 120:
        return None, "pequena"
    claro = a.min(axis=2) >= 238
    borda = max(2, int(min(H, W) * 0.015))
    anel = np.concatenate([claro[:borda].ravel(), claro[-borda:].ravel(), claro[:, :borda].ravel(), claro[:, -borda:].ravel()])
    recorte = False
    if anel.mean() < 0.88:
        # fundo liso colorido de estudio: recorta por inundacao a partir da borda
        limpo = fundo_liso_para_branco(a, borda)
        if limpo is None:
            return None, "fundo-nao-branco"
        a, recorte = limpo, True
        im = Image.fromarray(a)
        claro = a.min(axis=2) >= 238
    # fundo quase branco (246, 248...) vira branco puro para nao aparecer como retangulo na gondola
    f = float(np.median(np.concatenate([a[:borda].reshape(-1, 3), a[-borda:].reshape(-1, 3)]).min(axis=1)))
    if 225 <= f < 254:
        a = np.clip(a.astype(np.float32) * (255.0 / f), 0, 255).astype(np.uint8)
        im = Image.fromarray(a)
    tinta = ~(a.min(axis=2) >= 244)
    if eh_tabela(a, tinta):
        return None, "tabela-ou-texto"
    linhas = np.where(tinta.mean(axis=1) > 0.004)[0]
    colunas = np.where(tinta.mean(axis=0) > 0.004)[0]
    if len(linhas) < 10 or len(colunas) < 10:
        return None, "vazia"
    y0, y1, x0, x1 = linhas[0], linhas[-1] + 1, colunas[0], colunas[-1] + 1
    h, w = y1 - y0, x1 - x0
    if h * w < 0.06 * H * W:
        return None, "objeto-minusculo"
    ar = h / w
    if ar < 0.18 or ar > 6:
        return None, f"proporcao {ar:.2f}"
    if (ar < 0.3 or ar > 4.5) and not fino_ok:
        return None, f"proporcao {ar:.2f}"
    miolo = tinta[y0:y1, x0:x1]
    if miolo.mean() < 0.33:
        return None, f"pouco-preenchida {miolo.mean():.2f}"
    # blocos separados por faixa branca indicam kit, varios objetos ou tabela ao lado
    for eixo, nome in ((0, "colunas"), (1, "linhas")):
        proj = miolo.mean(axis=eixo) > 0.003
        trechos = []
        ini = None
        for i, v in enumerate(proj):
            if v and ini is None:
                ini = i
            if not v and ini is not None:
                trechos.append(i - ini)
                ini = None
        if ini is not None:
            trechos.append(len(proj) - ini)
        if len(trechos) >= 2:
            trechos.sort(reverse=True)
            if trechos[1] > 0.14 * len(proj):
                return None, f"varios-objetos-{nome}"
    corte = im.crop((x0, y0, x1, y1))
    if fino_ok and corte.height / corte.width < 0.5:  # stick deitado fica em pe na gondola
        corte = corte.rotate(90, expand=True)
    return corte, None


def grava_webp(im, destino):
    h = 220
    w = max(1, round(im.width * h / im.height))
    peq = im.resize((w, h), Image.LANCZOS)
    for q in (72, 66, 60, 52, 45):
        buf = io.BytesIO()
        peq.save(buf, "WEBP", quality=q, method=6)
        if buf.tell() <= 25 * 1024:
            break
    tmp = destino + ".tmp"
    with open(tmp, "wb") as f:
        f.write(buf.getvalue())
    os.replace(tmp, destino)
    return buf.tell()


def url_imagem(u):
    if "vteximg.com.br" in u or "vtexassets.com" in u:
        return re.sub(r"(/ids/\d+)(-\d+-\d+)?/", r"\1-800-800/", u)
    if "cdn.shopify.com" in u or "/cdn/shop/" in u:
        return u + ("&" if "?" in u else "?") + "width=800"
    return u


def baixa_bruto(u):
    os.makedirs(BRUTOS, exist_ok=True)
    nome = hashlib.md5(u.encode()).hexdigest()
    p = os.path.join(BRUTOS, nome)
    if os.path.exists(p):
        return open(p, "rb").read()
    cod, corpo = http(url_imagem(u), timeout=30, tentativas=2)
    if corpo is None or cod != 200:
        cod, corpo = http(u, timeout=30, tentativas=2)
        if corpo is None or cod != 200:
            return None
    with open(p + ".tmp", "wb") as f:
        f.write(corpo)
    os.replace(p + ".tmp", p)
    return corpo


# ---------------------------------------------------------------- mapa
_mapa_lock = threading.Lock()


def carrega_mapa():
    if os.path.exists(MAPA):
        return json.load(open(MAPA))
    return {}


def grava_mapa(m):
    tmp = MAPA + ".tmp"
    with open(tmp, "w") as f:
        json.dump(m, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, MAPA)


NAO_FRENTE = re.compile(r"tabela|nutricion|ingrediente|beneficio|lifestyle|ambiente|banner|modo.?de.?uso|verso|costas|back[_\-.]|selo")


REPROV = os.path.join(LOGS, "reprovados.json")


def carrega_reprov():
    return json.load(open(REPROV)) if os.path.exists(REPROV) else {}


def processa(sku, cat_marca, por_ref, mapa, relato, reprov=None):
    chave = str(sku["sku"])
    cands, rej = candidatos_sku(sku, cat_marca, por_ref)
    tent = []
    vistos = set((reprov or {}).get(chave, []))
    for conf, c, mot in cands[:10]:
        for pos, u in enumerate(c["i"][:2]):
            if u in vistos or NAO_FRENTE.search(urllib.parse.unquote(u).lower()):
                continue
            vistos.add(u)
            dados = baixa_bruto(u)
            if dados is None:
                tent.append((c["f"], "sem-download"))
                continue
            fino = (tamanhos(norm(sku["desc"])).get("peso") or 99) <= 15
            im, reprova = trata_imagem(dados, fino)
            if im is None:
                tent.append((c["f"], reprova))
                continue
            ar = round(im.height / im.width, 3)
            tam = grava_webp(im, os.path.join(SAIDA, chave + ".webp"))
            with _mapa_lock:
                mapa[chave] = {"ar": ar, "fonte": c["u"], "conf": conf}
                grava_mapa(mapa)
            relato[chave] = {"st": "ok", "conf": conf, "mot": mot, "f": c["f"], "nome": c["n"], "img": u, "kb": round(tam / 1024, 1), "pos": pos}
            return
    relato[chave] = {"st": "sem", "tent": tent[:6], "rej": rej[:2], "n_cand": len(cands)}


def executa(limite=None, refazer=False):
    os.makedirs(SAIDA, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    skus = [x for x in carrega_skus() if x["marca"] != "A GRANEL"]
    if limite:
        skus = skus[:limite]
    cat = carrega_catalogos()
    log(f"catalogo: {len(cat)} itens, skus: {len(skus)}")
    por_marca, por_ref = indice_catalogo(cat)
    indice = monta_indice(cat)

    def sub(sku):
        return subconjunto(sku, indice)

    mapa = carrega_mapa()
    relpath = os.path.join(LOGS, "relato.json")
    relato = json.load(open(relpath)) if os.path.exists(relpath) else {}
    reprov = carrega_reprov()
    pendentes = [s for s in skus if str(s["sku"]) not in mapa]
    log(f"pendentes: {len(pendentes)}")
    feitos = [0]

    def um(s):
        try:
            processa(s, sub(s), por_ref, mapa, relato, reprov)
        except Exception as e:
            relato[str(s["sku"])] = {"st": "erro", "e": repr(e)}
        feitos[0] += 1
        if feitos[0] % 50 == 0:
            with _mapa_lock:
                try:
                    json.dump(dict(relato), open(relpath + ".tmp", "w"), ensure_ascii=False)
                    os.replace(relpath + ".tmp", relpath)
                except RuntimeError:
                    pass
            log(f"{feitos[0]}/{len(pendentes)} mapa={len(mapa)}")

    with cf.ThreadPoolExecutor(10) as ex:
        list(ex.map(um, pendentes))
    json.dump(relato, open(relpath + ".tmp", "w"), ensure_ascii=False)
    os.replace(relpath + ".tmp", relpath)
    log(f"fim mapa={len(mapa)}")


def relatorio():
    skus = carrega_skus()
    mapa = carrega_mapa()
    tot = sum(x["v"] for x in skus)
    gran = sum(x["v"] for x in skus if x["marca"] == "A GRANEL")
    em = [x for x in skus if str(x["sku"]) in mapa]
    sem_gr = [x for x in skus if x["marca"] != "A GRANEL"]
    print(f"cobertura: {len(em)} de {len(sem_gr)} produtos com embalagem (lista total {len(skus)}, granel {len(skus)-len(sem_gr)})")
    print(f"por venda: {sum(x['v'] for x in em)/tot*100:.1f}% do total; {sum(x['v'] for x in em)/(tot-gran)*100:.1f}% sem granel")
    top = sem_gr[:700]
    print(f"700 primeiros: {sum(str(x['sku']) in mapa for x in top)}")
    print("conf:", Counter(v["conf"] for v in mapa.values()))
    vm, cm = Counter(), Counter()
    vt, ct = Counter(), Counter()
    for x in sem_gr:
        vt[x["marca"]] += x["v"]
        ct[x["marca"]] += 1
        if str(x["sku"]) in mapa:
            vm[x["marca"]] += x["v"]
            cm[x["marca"]] += 1
    print("marcas (itens, % venda da marca):")
    for m, _ in vt.most_common(15):
        print(f"  {m}: {cm[m]}/{ct[m]} itens, {vm[m]/max(1,vt[m])*100:.0f}%")
    fs = Counter(urllib.parse.urlparse(v["fonte"]).netloc for v in mapa.values())
    print("fontes:", fs.most_common())
    tams = [os.path.getsize(os.path.join(SAIDA, f"{k}.webp")) for k in mapa if os.path.exists(os.path.join(SAIDA, f"{k}.webp"))]
    if tams:
        print(f"arquivos: {len(tams)}, media {sum(tams)/len(tams)/1024:.1f} KB, max {max(tams)/1024:.1f} KB, total {sum(tams)/1024/1024:.1f} MB")


def folhas(alvos=None, por=48, saida=None, rotulo_fonte=True):
    """Folha de contato para conferencia visual."""
    from PIL import ImageFont

    skus = {str(x["sku"]): x for x in carrega_skus()}
    mapa = carrega_mapa()
    chaves = alvos or list(mapa)
    saida = saida or os.path.join(HD, "folhas")
    os.makedirs(saida, exist_ok=True)
    try:
        fonte = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except Exception:
        fonte = ImageFont.load_default()
    arquivos = []
    colunas, ch, cw = 8, 215, 180
    for i in range(0, len(chaves), por):
        lote = chaves[i : i + por]
        linhas = (len(lote) + colunas - 1) // colunas
        folha = Image.new("RGB", (colunas * cw, linhas * ch), (235, 235, 235))
        d = ImageDraw.Draw(folha)
        for j, k in enumerate(lote):
            x, y = (j % colunas) * cw, (j // colunas) * ch
            d.rectangle([x + 2, y + 2, x + cw - 3, y + ch - 3], fill=(255, 255, 255))
            p = os.path.join(SAIDA, k + ".webp")
            if os.path.exists(p):
                im = Image.open(p).convert("RGB")
                im.thumbnail((cw - 12, 150))
                folha.paste(im, (x + (cw - im.width) // 2, y + 6))
            s = skus.get(k, {})
            txt = s.get("desc", "")[:58]
            cor = (180, 0, 0) if mapa.get(k, {}).get("conf") == "media" else (0, 0, 0)
            d.text((x + 5, y + 160), k, fill=cor, font=fonte)
            d.text((x + 5, y + 173), txt[:29], fill=(0, 0, 0), font=fonte)
            d.text((x + 5, y + 186), txt[29:], fill=(0, 0, 0), font=fonte)
        arq = os.path.join(saida, f"folha_{i//por:03d}.png")
        folha.save(arq)
        arquivos.append(arq)
    print("\n".join(arquivos))


def remover(chaves):
    """Tira do mapa, apaga o webp e guarda a imagem reprovada para nao voltar."""
    mapa = carrega_mapa()
    relpath = os.path.join(LOGS, "relato.json")
    relato = json.load(open(relpath)) if os.path.exists(relpath) else {}
    reprov = carrega_reprov()
    for k in chaves:
        img = relato.get(k, {}).get("img")
        if img:
            reprov.setdefault(k, []).append(img)
        mapa.pop(k, None)
        relato.pop(k, None)
        p = os.path.join(SAIDA, k + ".webp")
        if os.path.exists(p):
            os.remove(p)
    grava_mapa(mapa)
    json.dump(reprov, open(REPROV, "w"))
    json.dump(relato, open(relpath, "w"), ensure_ascii=False)
    print("mapa:", len(mapa), "reprovados:", sum(len(v) for v in reprov.values()))


def retrata():
    """Reprocessa os webp a partir do bruto em cache com o tratamento atual, sem rede."""
    mapa = carrega_mapa()
    relato = json.load(open(os.path.join(LOGS, "relato.json")))
    reprovados = []
    trocados = 0
    skus = {str(x["sku"]): x["desc"] for x in carrega_skus()}
    for k, v in list(mapa.items()):
        img = relato.get(k, {}).get("img")
        if not img:
            continue
        p = os.path.join(BRUTOS, hashlib.md5(img.encode()).hexdigest())
        if not os.path.exists(p):
            continue
        im, mot = trata_imagem(open(p, "rb").read(), (tamanhos(norm(skus.get(k, ""))).get("peso") or 99) <= 15)
        if im is None:
            reprovados.append((k, mot))
            continue
        grava_webp(im, os.path.join(SAIDA, k + ".webp"))
        v["ar"] = round(im.height / im.width, 3)
        trocados += 1
    grava_mapa(mapa)
    print("retratados", trocados, "agora reprovados", reprovados)
    return [k for k, _ in reprovados]


def _assina(k):
    p = os.path.join(SAIDA, k + ".webp")
    im = Image.open(p).convert("RGB").resize((24, 36), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)


LIMIAR_IRMAOS = 32


def irmaos(aplica=True):
    """Produto sem foto reaproveita a de outro sabor da mesma linha, so se a linha comprovadamente
    usa embalagem igual: 2 ou mais irmaos ja no mapa, parecidos entre si, com a mesma proporcao."""
    skus = [x for x in carrega_skus() if x["marca"] not in ("A GRANEL", "SEM MARCA", "MARCAS DIVERSAS", "CESTAS KITS CAIXAS E COMBOS")]
    mapa = carrega_mapa()
    relpath = os.path.join(LOGS, "relato.json")
    relato = json.load(open(relpath)) if os.path.exists(relpath) else {}

    CATS = {"Proteínas", "Creatina", "Colágeno", "Performance", "Cafés funcionais", "Barras e snacks"}
    skus = [x for x in skus if x["cat"] in CATS]

    def linha(x):
        # primeira palavra de conteudo + palavras que mudam a linha; o que sobra costuma ser o sabor
        t = [a for a in tokens_produto(x["desc"], x["marca"]) if a not in ("DE", "DA", "DO", "E", "COM", "A", "O", "100", "SEM")]
        t = [a for a in t if a not in SABOR]
        if not t:
            return (), None
        return tuple([t[0]] + sorted({a for a in t[1:] if a in LINHA})), tamanhos(norm(x["desc"])).get("peso")

    grupos = defaultdict(list)
    for x in skus:
        l, pes = linha(x)
        if l and pes:
            grupos[(x["marca"], l, pes)].append(x)
    novos = []
    for g, membros in grupos.items():
        tem = [x for x in membros if str(x["sku"]) in mapa]
        falta = [x for x in membros if str(x["sku"]) not in mapa]
        if len(tem) < 2 or not falta or not g[1]:
            continue
        tem.sort(key=lambda x: -x["v"])
        ass = [_assina(str(x["sku"])) for x in tem[:6]]
        ars = [mapa[str(x["sku"])]["ar"] for x in tem[:6]]
        dif = [float(np.abs(ass[i] - ass[j]).mean()) for i in range(len(ass)) for j in range(i + 1, len(ass))]
        if os.environ.get("VER_IRMAOS"):
            print(g, len(tem), len(falta), round(max(dif), 1), round(max(ars) / min(ars), 2))
        if max(dif) > LIMIAR_IRMAOS or max(ars) / min(ars) > 1.1:
            continue
        base = str(tem[0]["sku"])
        for x in falta:
            k = str(x["sku"])
            novos.append((k, x["desc"], base, tem[0]["desc"], round(max(dif), 1)))
            if aplica:
                with open(os.path.join(SAIDA, base + ".webp"), "rb") as f:
                    dados = f.read()
                with open(os.path.join(SAIDA, k + ".webp.tmp"), "wb") as f:
                    f.write(dados)
                os.replace(os.path.join(SAIDA, k + ".webp.tmp"), os.path.join(SAIDA, k + ".webp"))
                mapa[k] = {"ar": mapa[base]["ar"], "fonte": mapa[base]["fonte"], "conf": "media"}
                relato[k] = {"st": "ok", "conf": "media", "mot": "irmao " + base, "f": relato.get(base, {}).get("f", ""), "nome": tem[0]["desc"], "img": relato.get(base, {}).get("img"), "irmao": base}
    # conferidos a mao: a Essential vende um unico omega 3 de 500 mg, o Super Omega 3 TG
    for k, base in {str(o): "59284" for o in [60221, 60364]}.items():
        if aplica and k not in mapa and base in mapa:
            with open(os.path.join(SAIDA, base + ".webp"), "rb") as f:
                dados = f.read()
            with open(os.path.join(SAIDA, k + ".webp.tmp"), "wb") as f:
                f.write(dados)
            os.replace(os.path.join(SAIDA, k + ".webp.tmp"), os.path.join(SAIDA, k + ".webp"))
            mapa[k] = {"ar": mapa[base]["ar"], "fonte": mapa[base]["fonte"], "conf": "media"}
            relato[k] = {"st": "ok", "conf": "media", "mot": "manual " + base, "irmao": base, "img": relato.get(base, {}).get("img")}
            novos.append((k, "manual", base, "", 0))
    if aplica:
        grava_mapa(mapa)
        json.dump(relato, open(relpath, "w"), ensure_ascii=False)
    for n in novos:
        print(n)
    print("irmaos:", len(novos))


def duplicados():
    """Mesma imagem em SKUs diferentes: quem nao e o mais vendido do grupo fica com conf media."""
    skus = {str(x["sku"]): x for x in carrega_skus()}
    mapa = carrega_mapa()
    grupos = defaultdict(list)
    for k in mapa:
        p = os.path.join(SAIDA, k + ".webp")
        if os.path.exists(p):
            grupos[hashlib.md5(open(p, "rb").read()).hexdigest()].append(k)
    n = 0
    for ks in grupos.values():
        if len(ks) < 2:
            continue
        ks.sort(key=lambda k: -skus[k]["v"])
        toks = [{t for t in tokens_produto(skus[k]["desc"], skus[k]["marca"]) if t in SABOR} for k in ks]
        sabores_diferentes = any(t != toks[0] for t in toks)
        for k in ks if sabores_diferentes else ks[1:]:
            if mapa[k]["conf"] != "media":
                mapa[k]["conf"] = "media"
                n += 1
    grava_mapa(mapa)
    print("rebaixados para media:", n)


def casa_seco():
    """Casamento sem baixar nada, para calibrar regras."""
    skus = [x for x in carrega_skus() if x["marca"] != "A GRANEL"]
    cat = carrega_catalogos()
    _, por_ref = indice_catalogo(cat)
    indice = monta_indice(cat)
    saida = []
    for s in skus:
        cs, rej = candidatos_sku(s, subconjunto(s, indice), por_ref)
        saida.append({"sku": s["sku"], "desc": s["desc"], "marca": s["marca"], "n": len(cs), "melhor": (cs[0][0], cs[0][1]["f"], cs[0][1]["n"], cs[0][2]) if cs else None, "rej": rej[:2], "v": s["v"]})
    os.makedirs(LOGS, exist_ok=True)
    json.dump(saida, open(os.path.join(LOGS, "casamento.json"), "w"), ensure_ascii=False, indent=0)
    tot = sum(x["v"] for x in saida)
    print("com candidato:", sum(1 for x in saida if x["n"]), "de", len(saida), "venda %.1f%%" % (sum(x["v"] for x in saida if x["n"]) / tot * 100))
    print("top700:", sum(1 for x in saida[:700] if x["n"]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "relatorio"
    if cmd == "harvest":
        harvest(sys.argv[2:] or None)
    elif cmd == "match":
        casa_seco()
    elif cmd == "run":
        lim = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--limite" else None
        executa(lim)
    elif cmd == "folhas":
        folhas(sys.argv[2:] or None)
    elif cmd == "duplicados":
        duplicados()
    elif cmd == "irmaos":
        irmaos("--ver" not in sys.argv)
    elif cmd == "retrata":
        remover(retrata())
    elif cmd == "remover":
        remover(sys.argv[2:])
    else:
        relatorio()
