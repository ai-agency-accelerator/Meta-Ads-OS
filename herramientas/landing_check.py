#!/usr/bin/env python3
"""Chequeo rápido de una landing para tráfico de Meta: tracking, consentimiento, velocidad y mensaje.

Qué hace (solo lectura, sin ejecutar JavaScript):
  1. Descarga el HTML como un navegador y detecta: Meta Pixel (IDs en fbq('init')), fbevents.js, GTM, GA4, plataforma
     (Shopify, WordPress, Webflow, Wix, GoHighLevel, Framer…), gestor de consentimiento y eventos fbq('track').
     Píxel tras consentimiento: el que solo se carga cuando la persona acepta las cookies. En las páginas de
     `herramientas/paginas.py` (meta generator «meta-ads-os/paginas») se lee de su `pos-config`; en otras webs, el
     fbq('init') dentro de un <script type="text/plain"> que el gestor de cookies activa al aceptar. Se informa como
     «tras consentimiento», no como ausente.
  2. Comprueba si fbclid y las UTM sobreviven a las redirecciones (si se pierden, se pierde la atribución del clic).
  3. Extrae title, meta description, H1 y textos de botones para revisar el message match con el anuncio.
  4. Velocidad móvil con PageSpeed Insights (LCP, CLS, INP de campo si existen y puntuación de laboratorio).
     Opcional: PAGESPEED_API_KEY en .env para evitar límites.
  5. Con --cliente: compara los píxeles de la web con el dataset de la ficha y guarda el informe en
     clientes/<slug>/auditorias/landing_AAAA-MM-DD_<dominio>.md.

Limitación: muchos píxeles se inyectan por GTM o apps (no visibles en el HTML). Para confirmar eventos usa Events
Manager (Test Events) o el MCP de Meta (ads_get_dataset_stats / ads_get_dataset_quality).
Marco: meta-ads-kb/03-creatividad/15-landing-pages-y-cro-trafico-meta.md.

Uso:
  python3 -I herramientas/landing_check.py https://acme.example/demo [--sin-pagespeed] [--cliente acme] [--json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html as htmlmod
import json
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402

PLATAFORMAS = {
    "Shopify": r"cdn\.shopify\.com|Shopify\.theme|myshopify\.com",
    "WordPress": r"wp-content|wp-includes",
    "WooCommerce": r"woocommerce",
    "Webflow": r"webflow\.(js|com)|data-wf-page",
    "Framer": r"framerusercontent\.com|framer\.com/m/|data-framer",
    "Wix": r"wixstatic\.com|_wixCssImports",
    "Squarespace": r"squarespace\.com|static1\.squarespace",
    "ClickFunnels": r"clickfunnels",
    "GoHighLevel": r"leadconnectorhq|msgsndr\.com|highlevel",
    "Systeme.io": r"systeme\.io",
    "Kajabi": r"kajabi",
    "Hotmart": r"hotmart",
    "PrestaShop": r"prestashop",
    "Magento": r"Magento|mage/cookies",
    "Next.js": r"/_next/static|__NEXT_DATA__",
}
CMP = {
    "Cookiebot": r"cookiebot", "OneTrust": r"onetrust|optanon", "CookieYes": r"cookieyes|cookie-law-info",
    "Iubenda": r"iubenda", "Complianz": r"complianz", "Usercentrics": r"usercentrics", "Didomi": r"didomi",
    "Termly": r"termly", "Axeptio": r"axeptio", "Shopify Customer Privacy": r"customerPrivacy|privacy-banner",
}
CALENDARIOS = {"Calendly": r"calendly\.com", "GHL Calendar": r"leadconnectorhq\.com/widget/booking|/widget/bookings",
               "Cal.com": r"cal\.com/", "HubSpot Meetings": r"meetings\.hubspot\.com", "TidyCal": r"tidycal\.com"}
FBCLID_PRUEBA = "TEST_fbclid_000"
_INIT = r"fbq\(\s*['\"]init['\"]\s*,\s*['\"](\d{10,20})['\"]"
_GENERADOR = re.compile(r"<meta[^>]+name=[\"']generator[\"'][^>]+content=[\"']meta-ads-os/paginas", re.I)
_POS_CONFIG = re.compile(r"<script\b[^>]*\bid=[\"']pos-config[\"'][^>]*>(.*?)</script>", re.I | re.S)
# Scripts que el gestor de cookies deja inertes hasta que la persona acepta (Cookiebot, Complianz, Iubenda, OneTrust…)
_BLOQUEADO = re.compile(r"<script\b[^>]*\btype=[\"']text/plain[\"'][^>]*>(.*?)</script>", re.I | re.S)


def _limpio(t: str) -> str:
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def pixel_diferido(h: str) -> dict:
    """Píxel que se carga solo tras el consentimiento. paginas.py: `pixel_id` de su `pos-config` (el runtime descarga
    fbevents.js al aceptar). Otras webs: fbq('init') dentro de un script type="text/plain"."""
    config = None
    m = _POS_CONFIG.search(h)
    if m:
        try:
            config = json.loads(m.group(1))
        except ValueError:
            config = None
    generada = bool(_GENERADOR.search(h)) or config is not None
    ids: list[str] = []
    origen = None
    if isinstance(config, dict) and re.fullmatch(r"\d{6,20}", str(config.get("pixel_id") or "")):
        ids, origen = [str(config["pixel_id"])], "paginas.py"
    bloqueados = sorted({i for bloque in _BLOQUEADO.findall(h) for i in re.findall(_INIT, bloque)} - set(ids))
    if bloqueados:
        ids += bloqueados
        origen = origen or "gestor de consentimiento"
    return {"pixel_tras_consentimiento": ids, "pixel_diferido_por": origen, "pagina_generada": generada,
            "pagina_generada_sin_pixel": generada and isinstance(config, dict) and not config.get("pixel_id")}


def analizar_html(h: str) -> dict:
    r: dict = {}
    r["pixel_ids"] = sorted(set(re.findall(_INIT, h)))
    r["fbevents_js"] = bool(re.search(r"connect\.facebook\.net/[^\"']*/fbevents\.js", h))
    r["eventos_fbq"] = sorted(set(re.findall(r"fbq\(\s*['\"](?:track|trackCustom)['\"]\s*,\s*['\"]([A-Za-z_]+)['\"]", h)))
    r["consent_fbq"] = bool(re.search(r"fbq\(\s*['\"]consent['\"]", h))
    r["gtm"] = sorted(set(re.findall(r"GTM-[A-Z0-9]{4,9}", h)))
    r["ga4"] = sorted(set(re.findall(r"\bG-[A-Z0-9]{6,12}\b", h)))
    r["plataforma"] = [k for k, rx in PLATAFORMAS.items() if re.search(rx, h, re.I)]
    r["cmp"] = [k for k, rx in CMP.items() if re.search(rx, h, re.I)]
    r["calendario"] = [k for k, rx in CALENDARIOS.items() if re.search(rx, h, re.I)]
    r["scripts"] = len(re.findall(r"<script\b", h, re.I))
    r["peso_html_kb"] = round(len(h.encode("utf-8")) / 1024, 1)
    m = re.search(r"<title[^>]*>(.*?)</title>", h, re.I | re.S)
    r["title"] = _limpio(m.group(1)) if m else ""
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', h, re.I)
    r["meta_description"] = htmlmod.unescape(m.group(1)) if m else ""
    r["h1"] = [_limpio(x)[:140] for x in re.findall(r"<h1[^>]*>(.*?)</h1>", h, re.I | re.S)][:3]
    botones = re.findall(r"<(?:button|a)[^>]*(?:class|id)=[\"'][^\"']*(?:btn|button|cta|checkout|add-to-cart|comprar)"
                         r"[^\"']*[\"'][^>]*>(.*?)</(?:button|a)>", h, re.I | re.S)
    r["ctas"] = list(dict.fromkeys(t for t in (_limpio(b)[:60] for b in botones) if t))[:8]
    r["formularios"] = len(re.findall(r"<form\b", h, re.I))
    r["viewport_movil"] = bool(re.search(r'<meta[^>]+name=["\']viewport', h, re.I))
    r.update(pixel_diferido(h))
    return r


def pagespeed(url: str) -> dict:
    params = {"url": url, "strategy": "mobile", "category": "performance"}
    k = _comun.credencial("PAGESPEED_API_KEY")
    if k:
        params["key"] = k
    d = _comun.get_json("https://www.googleapis.com/pagespeedonline/v5/runPagespeed", params, timeout=120, intentos=2)
    out: dict = {}
    lh = d.get("lighthouseResult", {})
    out["puntuacion_lab"] = round((lh.get("categories", {}).get("performance", {}).get("score") or 0) * 100)
    au = lh.get("audits", {})
    for k2, nombre in (("largest-contentful-paint", "LCP_lab"), ("cumulative-layout-shift", "CLS_lab"),
                       ("total-blocking-time", "TBT_lab"), ("speed-index", "SpeedIndex_lab")):
        if k2 in au:
            out[nombre] = au[k2].get("displayValue")
    le = (d.get("loadingExperience") or {}).get("metrics") or {}
    for k2, nombre in (("LARGEST_CONTENTFUL_PAINT_MS", "LCP_campo_p75_ms"), ("CUMULATIVE_LAYOUT_SHIFT_SCORE", "CLS_campo_p75"),
                       ("INTERACTION_TO_NEXT_PAINT", "INP_campo_p75_ms")):
        if k2 in le:
            out[nombre] = le[k2].get("percentile")
            out[nombre + "_categoria"] = le[k2].get("category")
    return out


def chequear(url: str, con_pagespeed: bool = True, dataset: str = "") -> dict:
    url = url if url.startswith("http") else "https://" + url
    p = urllib.parse.urlsplit(url)
    extra = f"fbclid={FBCLID_PRUEBA}&utm_source=facebook&utm_medium=paid_social&utm_campaign=test"
    prueba = urllib.parse.urlunsplit(p._replace(query=f"{p.query}&{extra}" if p.query else extra))  # antes del #
    h, final, status = _comun.get_texto(prueba)
    q = urllib.parse.parse_qs(urllib.parse.urlparse(final).query)
    r = {"url": url, "estado_http": status, "url_final": final[:300],
         "fbclid_conservado": q.get("fbclid") == [FBCLID_PRUEBA], "utm_conservadas": "utm_source" in q,
         **analizar_html(h)}
    if dataset:
        r["dataset_ficha"] = dataset
        todos = sorted(set(r["pixel_ids"]) | set(r["pixel_tras_consentimiento"]))
        r["pixel_coincide_ficha"] = dataset in todos if todos else None
    if con_pagespeed:
        try:
            r["pagespeed"] = pagespeed(url)
        except Exception as e:  # el chequeo sigue aunque PageSpeed falle
            r["pagespeed"] = {"error": str(e)[:200]}
    return r


def _pixel_texto(r: dict) -> str:
    diferidos = r.get("pixel_tras_consentimiento") or []
    partes = [", ".join(i for i in r["pixel_ids"] if i not in diferidos)]
    if diferidos:
        partes.append(f"{', '.join(diferidos)} tras consentimiento ({r.get('pixel_diferido_por')})")
    return " · ".join(x for x in partes if x) or "no visible"


def texto(r: dict) -> str:
    si = lambda b, no="NO": "sí" if b else no  # noqa: E731
    lin = [f"# Chequeo de landing: {r['url']}", "", "## Tracking y consentimiento",
           f"- Estado HTTP: {r['estado_http']} · URL final: {r['url_final'][:160]}",
           f"- fbclid conservado tras redirecciones: "
           f"{si(r['fbclid_conservado'], 'NO (revisa las redirecciones: se pierde la atribución del clic)')}",
           f"- UTM conservadas: {si(r['utm_conservadas'])}",
           f"- Meta Pixel en el HTML: {_pixel_texto(r)} · fbevents.js: "
           f"{'tras consentimiento' if r['pixel_tras_consentimiento'] else si(r['fbevents_js'], 'no visible')}",
           f"- Eventos fbq visibles: {', '.join(r['eventos_fbq']) or 'ninguno en el HTML'} · fbq('consent'): "
           f"{si(r['consent_fbq'], 'no')}",
           f"- GTM: {', '.join(r['gtm']) or 'no'} · GA4: {', '.join(r['ga4']) or 'no'}",
           f"- Plataforma: {', '.join(r['plataforma']) or 'no identificada'} · Gestor de consentimiento: "
           f"{', '.join(r['cmp']) or 'no detectado'} · Calendario: {', '.join(r['calendario']) or 'no detectado'}"]
    if r["pixel_tras_consentimiento"]:
        lin.append("  Píxel tras consentimiento: no se descarga hasta que la persona acepta las cookies. No es un fallo "
                   "(en la UE es lo que toca); para verlo en Test Events, acepta el banner.")
        if r["pixel_diferido_por"] == "paginas.py":
            lin.append("  Página generada con herramientas/paginas.py: revisa también la carpeta local con "
                       "`python3 -I herramientas/paginas.py validar <carpeta>`.")
    elif r.get("pagina_generada_sin_pixel"):
        lin.append("  Página de paginas.py sin `tracking.pixel_id`: sin eventos del navegador ni banner (solo servidor).")
    elif not r["pixel_ids"] and not r["fbevents_js"]:
        lin.append("  Nota: el píxel puede cargarse vía GTM o una app (no visible aquí). Confírmalo en Events Manager "
                   "o con el MCP.")
    if r.get("pixel_coincide_ficha") is False:
        web = sorted(set(r["pixel_ids"]) | set(r["pixel_tras_consentimiento"]))
        lin.append(f"  ATENCIÓN: el píxel de la web ({', '.join(web)}) no es el dataset de la ficha "
                   f"({r['dataset_ficha']}): los eventos pueden ir a otro dataset.")
    lin += ["", "## Mensaje (para revisar el message match con el anuncio)",
            f"- Title: {r['title'][:140]}", f"- Meta description: {r['meta_description'][:200]}",
            f"- H1: {' | '.join(r['h1']) or '—'}", f"- CTAs detectadas: {' | '.join(r['ctas']) or '—'}",
            f"- Formularios en el HTML: {r['formularios']} · viewport móvil: {si(r['viewport_movil'])} · "
            f"scripts: {r['scripts']} · HTML: {r['peso_html_kb']} KB"]
    ps = r.get("pagespeed")
    if ps is not None:
        lin += ["", "## Velocidad móvil (PageSpeed Insights)"]
        if "error" in ps:
            lin.append(f"- No disponible ({ps['error']}). Prueba más tarde o añade PAGESPEED_API_KEY a .env")
        else:
            lin += [f"- {k}: {v}" for k, v in ps.items()]
            lcp = ps.get("LCP_campo_p75_ms")
            if lcp:
                lect = "bien (≤2,5 s)" if lcp <= 2500 else "mejorable" if lcp <= 4000 else "malo (>4 s)"
                lin.append(f"- Lectura: LCP p75 de usuarios reales {lcp / 1000:.1f} s → {lect}")
    lin += ["", "Siguiente paso: compara con el anuncio (promesa, oferta, precio) y valida los eventos en Events Manager."]
    return "\n".join(lin)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--sin-pagespeed", action="store_true")
    ap.add_argument("--cliente", help="compara con el dataset de la ficha y guarda el informe en auditorias/")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    dataset = ""
    if a.cliente:
        try:
            ficha = _comun.leer_ficha(a.cliente)
        except _comun.FichaInvalida as e:
            print(f"Error de configuración: {e}", file=sys.stderr)
            return 2
        dataset = str((ficha.get("meta") or {}).get("dataset", "") if isinstance(ficha.get("meta"), dict) else "")
    try:
        r = chequear(a.url, not a.sin_pagespeed, dataset)
    except Exception as e:
        print(f"No se pudo descargar la página: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    t = texto(r)
    if a.cliente:
        dominio = re.sub(r"[^a-z0-9.-]+", "-", urllib.parse.urlparse(r["url"]).netloc.lower()) or "web"
        destino = _comun.ruta_cliente(a.cliente) / "auditorias" / f"landing_{dt.date.today()}_{dominio}.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(t + "\n", encoding="utf-8")
        r["guardado"] = str(destino.relative_to(_comun.RAIZ))
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else t)
    if a.cliente and not a.json:
        print(f"\n[guardado] {r['guardado']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
