#!/usr/bin/env python3
"""Render de estáticos, carruseles e informes: plantilla HTML + datos JSON + marca del cliente → PNG o PDF.

Uso (Playwright va en el extra `render` del proyecto):
  uv run --extra render python -I herramientas/render.py png plantillas/html/estatico.html \
      --datos plantillas/html/ejemplos/estatico.json --formatos 1x1,4x5,9x16 --salida <dir> [--cliente acme]
  uv run --extra render python -I herramientas/render.py pdf plantillas/html/informe-cliente.html \
      --datos plantillas/html/ejemplos/informe-cliente.json --salida <archivo.pdf> [--cliente clinica-sonrisa]

Opciones comunes:
  --cliente SLUG   aplica la marca de `clientes/<slug>/marca/marca.json` (+ sus archivos)
  --marca RUTA     usa ese `marca.json` o la carpeta que lo contiene (prevalece sobre --cliente)
  --nombre PREFIJO prefijo de los archivos (por defecto, el nombre de la plantilla)
  --json           informe en JSON: archivos, tamaños en píxeles y avisos

Plantillas (sin dependencias, estilo «mustache» reducido):
  {{clave}} o {{a.b.c}}       valor escapado para HTML (también {{.}} = elemento actual)
  {{#lista}}…{{/lista}}       repite por cada elemento (dentro: {{@indice}}, {{@total}}, {{@primero}}, {{@ultimo}});
                              con un dict entra en él; con un valor verdadero, muestra el bloque
  {{^clave}}…{{/clave}}       muestra el bloque si la clave falta o está vacía
  {{#clave?}}…{{/clave?}}     muestra el bloque una vez si la clave no está vacía, sin entrar en ella (p. ej. para
                              envolver una lista: <ul>{{#lista}}…{{/lista}}</ul>)
  {{clave|filtro}}            filtros: uri (archivo local → data URI), mayusculas, num, eur, pct
  Claves reservadas: `marca` (nombre, colores, tipografias, logo.principal/claro como data URI, subtitulos,
  cta_por_defecto, etiqueta_ia), `formato` (id, ancho, alto, clase, zona.*) y `hoy` (AAAA-MM-DD).
  `render.py` inyecta en <head> las variables CSS de la marca y del formato (--color-primario, --fuente-titulos,
  --ancho, --zs-arriba…) y las tipografías como @font-face embebidas.
  Atributos que entiende el render:
    data-zona-segura   el elemento debe quedar dentro de la zona segura del formato (si no, aviso)
    data-ajustar       si su contenido desborda, reduce `--escala` (tamaño de letra) hasta que quepa (mín. 0,6)
    data-tarjeta       cada elemento es una imagen aparte: <plantilla>_<formato>_<nn>.png (carruseles)
  <meta name="formatos" content="1x1,4x5"> limita los formatos que admite la plantilla.

Zonas seguras (meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md):
  9x16: 14 % arriba, 35 % abajo, 6 % a los lados [OFFICIAL META] y franja derecha de Reels desde y≈1152 [STRONG INFERENCE].
  4x5 y 1x1: margen del 5 % [HYPOTHESIS].

Códigos de salida: 0 ok (aunque haya avisos) · 1 error del usuario · 2 error de configuración (Playwright o navegador).
"""
from __future__ import annotations

import argparse
import base64
import copy
import datetime as dt
import html
import json
import mimetypes
import pathlib
import re
import sys
import tempfile
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402

PLANTILLAS = pathlib.Path(__file__).resolve().parent.parent / "plantillas" / "html"
FUENTES = PLANTILLAS / "fuentes"

# ───────────────────────────── formatos y zonas seguras ─────────────────────────────
FORMATOS: dict[str, tuple[int, int]] = {"1x1": (1080, 1080), "4x5": (1080, 1350), "9x16": (1080, 1920)}
A4 = {"id": "a4", "ancho": 794, "alto": 1123}  # px CSS a 96 ppp


def zona_segura(fid: str) -> dict:
    """Zona segura en píxeles del lienzo: márgenes y rectángulos de exclusión."""
    ancho, alto = FORMATOS[fid]
    if fid == "9x16":
        z = {"arriba": round(alto * 0.14), "abajo": round(alto * 0.35), "izquierda": round(ancho * 0.06),
             "derecha": round(ancho * 0.06),
             "exclusiones": [{"x0": ancho - 227, "y0": 1152, "x1": ancho, "y1": alto,
                              "motivo": "franja de botones de Reels (abajo a la derecha)"}],
             "fuente": "[OFFICIAL META] 14/35/6 % + [STRONG INFERENCE] franja de Reels"}
    else:
        m = round(min(ancho, alto) * 0.05)
        z = {"arriba": m, "abajo": m, "izquierda": m, "derecha": m, "exclusiones": [],
             "fuente": "[HYPOTHESIS] margen del 5 %"}
    return z


def parsear_formatos(texto: str | None, admitidos: list[str] | None = None) -> list[str]:
    """«1x1, 4x5,9X16» → ['1x1','4x5','9x16']. Acepta también 1:1, 4:5 y 9:16. Lanza ValueError si no es válido."""
    if not texto:
        return list(admitidos or FORMATOS)
    salida: list[str] = []
    for parte in texto.split(","):
        f = parte.strip().lower().replace(":", "x").replace("×", "x")
        if not f:
            continue
        if f not in FORMATOS:
            raise ValueError(f"Formato no válido: {parte.strip()!r} (usa 1x1, 4x5 o 9x16)")
        if admitidos and f not in admitidos:
            raise ValueError(f"La plantilla no admite {f} (admite: {', '.join(admitidos)})")
        if f not in salida:
            salida.append(f)
    if not salida:
        raise ValueError("No has indicado ningún formato (usa --formatos 1x1,4x5,9x16)")
    return salida


def contexto_formato(fid: str) -> dict:
    if fid == "a4":
        return {**A4, "clase": "f-a4", "zona": {}}
    ancho, alto = FORMATOS[fid]
    return {"id": fid, "ancho": ancho, "alto": alto, "clase": f"f-{fid}", "zona": zona_segura(fid)}


# ───────────────────────────── errores ─────────────────────────────
class ErrorUsuario(Exception):
    """Plantilla, datos o marca que no existen o no son válidos (código 1)."""


class ErrorConfig(Exception):
    """Falta Playwright o un navegador (código 2)."""


# ───────────────────────────── marca ─────────────────────────────
MARCA_DEFECTO: dict[str, Any] = {
    "nombre": "Tu marca",
    "colores": {"primario": "#1E3A8A", "secundario": "#0F172A", "acento": "#F59E0B", "fondo": "#FFFFFF",
                "texto": "#0F172A", "texto_sobre_primario": "#FFFFFF"},
    "tipografias": {"titulos": {"familia": "Montserrat", "archivo": "", "peso": 800},
                    "texto": {"familia": "Montserrat", "archivo": "", "peso": 500}},
    "logo": {"principal": "", "claro": ""},
    "subtitulos": {"color": "#FFFFFF", "resaltado": "#F59E0B", "contorno": "#000000", "mayusculas": False},
    "cta_por_defecto": "Más información",
    "etiqueta_ia": "Contenido generado con IA",
}
MONTSERRAT = {500: "Montserrat-Medium.ttf", 600: "Montserrat-SemiBold.ttf", 700: "Montserrat-Bold.ttf",
              800: "Montserrat-ExtraBold.ttf"}
_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
_FAMILIA = re.compile(r"[\w .-]{1,60}")


def _fusionar(base: dict, extra: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _fusionar(out[k], v)
        else:
            out[k] = v
    return out


def _rel(p: pathlib.Path) -> str:
    """Ruta relativa a la raíz del producto si cae dentro (así no se filtran rutas personales en los informes)."""
    try:
        return str(pathlib.Path(p).resolve().relative_to(pathlib.Path(_comun.RAIZ).resolve()))
    except ValueError:
        return str(p)


def data_uri(ruta: pathlib.Path) -> str:
    tipo = mimetypes.guess_type(str(ruta))[0] or "application/octet-stream"
    if ruta.suffix.lower() == ".svg":
        tipo = "image/svg+xml"
    elif ruta.suffix.lower() in (".ttf", ".otf", ".woff", ".woff2"):
        tipo = {".ttf": "font/ttf", ".otf": "font/otf", ".woff": "font/woff", ".woff2": "font/woff2"}[ruta.suffix.lower()]
    return f"data:{tipo};base64," + base64.b64encode(ruta.read_bytes()).decode("ascii")


def _luminancia(hexa: str) -> float:
    h = hexa.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    canales = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a: str, b: str) -> float:
    """Relación de contraste WCAG entre dos colores hex."""
    la, lb = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def cargar_marca(cliente: str | None = None, ruta: str | pathlib.Path | None = None) -> dict:
    """Marca efectiva: la neutra por defecto fusionada con `marca.json` (de --marca o del cliente).

    Devuelve un dict con los campos del esquema más `_dir` (carpeta de la marca o None), `_origen` y `_avisos`.
    Lanza ErrorUsuario si --marca no existe, si el cliente no existe o si el JSON no es válido.
    """
    avisos: list[str] = []
    archivo: pathlib.Path | None = None
    if ruta:
        archivo = pathlib.Path(ruta)
        if archivo.is_dir():
            archivo = archivo / "marca.json"
        if not archivo.exists():
            raise ErrorUsuario(f"No existe la marca {ruta}")
    elif cliente:
        try:
            carpeta = _comun.ruta_cliente(cliente)
        except _comun.FichaInvalida as e:
            raise ErrorUsuario(str(e)) from None
        if not carpeta.exists():
            raise ErrorUsuario(f"No existe el cliente {cliente!r} (clientes/{cliente}/). Créalo con /cliente-nuevo")
        archivo = carpeta / "marca" / "marca.json"
        if not archivo.exists():
            avisos.append(f"clientes/{cliente}/marca/marca.json no existe: uso la marca neutra por defecto")
            archivo = None
    if not ruta and not cliente:
        avisos.append("Sin --cliente ni --marca: uso la marca neutra por defecto")
    datos: dict = {}
    if archivo:
        try:
            datos = json.loads(archivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ErrorUsuario(f"{_rel(archivo)} no es un JSON válido: {e}") from None
        if not isinstance(datos, dict):
            raise ErrorUsuario(f"{_rel(archivo)} debe ser un objeto JSON")
    marca = _fusionar(MARCA_DEFECTO, datos)
    if cliente and "nombre" not in datos:
        try:
            marca["nombre"] = _comun.leer_ficha(cliente).get("nombre") or cliente
        except _comun.FichaInvalida:
            marca["nombre"] = cliente
    for clave, defecto in MARCA_DEFECTO["colores"].items():
        valor = marca["colores"].get(clave)
        if not isinstance(valor, str) or not _HEX.fullmatch(valor):
            if clave in (datos.get("colores") or {}):
                avisos.append(f"Color {clave}={valor!r} no es hexadecimal (#RRGGBB): uso {defecto}")
            marca["colores"][clave] = defecto
    for clave, defecto in MARCA_DEFECTO["subtitulos"].items():
        valor = marca["subtitulos"].get(clave)
        if clave != "mayusculas" and (not isinstance(valor, str) or not _HEX.fullmatch(valor)):
            marca["subtitulos"][clave] = defecto
    c = marca["colores"]
    for a, b, que in (("texto", "fondo", "texto sobre fondo"), ("texto_sobre_primario", "primario",
                                                                 "texto sobre color primario")):
        r = contraste(c[a], c[b])
        if r < 4.5:
            avisos.append(f"Contraste bajo en {que}: {r}:1 (WCAG AA pide 4,5:1 para texto normal)")
    marca["_dir"] = archivo.parent if archivo else None
    marca["_origen"] = _rel(archivo) if archivo else "defecto"
    marca["_avisos"] = avisos
    return marca


def _resolver_archivo(valor: str, base: pathlib.Path | None) -> pathlib.Path | None:
    if not valor:
        return None
    p = pathlib.Path(valor)
    if not p.is_absolute() and base is not None:
        p = base / p
    return p if p.is_file() else None


def _fuente(tipo: str, marca: dict, avisos: list[str]) -> tuple[str, str, int]:
    """(@font-face CSS, familia CSS, peso) para «titulos» o «texto»."""
    t = marca["tipografias"].get(tipo) or {}
    familia = str(t.get("familia") or "Montserrat")
    if not _FAMILIA.fullmatch(familia):
        avisos.append(f"Familia tipográfica no válida en {tipo}: {familia!r}; uso Montserrat")
        familia = "Montserrat"
    try:
        peso = int(t.get("peso") or (800 if tipo == "titulos" else 500))
    except (TypeError, ValueError):
        peso = 800 if tipo == "titulos" else 500
    alias = "MarcaTitulos" if tipo == "titulos" else "MarcaTexto"
    archivo = _resolver_archivo(str(t.get("archivo") or ""), marca.get("_dir"))
    if t.get("archivo") and archivo is None:
        avisos.append(f"No encuentro la tipografía {t.get('archivo')!r} de {tipo}: uso Montserrat")
        familia = "Montserrat"
    if archivo is None and familia.lower() == "montserrat":
        cercano = min(MONTSERRAT, key=lambda w: abs(w - peso))
        archivo = FUENTES / MONTSERRAT[cercano]
    pila = f'"{alias}", "{familia}", system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif'
    if archivo is None:  # familia instalada en el sistema (o la de reserva)
        return "", pila, peso
    css = (f'@font-face{{font-family:"{alias}";src:url({data_uri(archivo)});'
           f"font-weight:100 900;font-style:normal;font-display:block;}}")
    return css, pila, peso


def css_inyectado(marca: dict, formato: dict, avisos: list[str]) -> str:
    c = marca["colores"]
    s = marca["subtitulos"]
    ff_t, pila_t, peso_t = _fuente("titulos", marca, avisos)
    ff_x, pila_x, peso_x = _fuente("texto", marca, avisos)
    z = formato.get("zona") or {}
    variables = {
        "--color-primario": c["primario"], "--color-secundario": c["secundario"], "--color-acento": c["acento"],
        "--color-fondo": c["fondo"], "--color-texto": c["texto"], "--color-texto-sobre-primario": c["texto_sobre_primario"],
        "--sub-color": s["color"], "--sub-resaltado": s["resaltado"], "--sub-contorno": s["contorno"],
        "--fuente-titulos": pila_t, "--fuente-texto": pila_x, "--peso-titulos": str(peso_t), "--peso-texto": str(peso_x),
        "--ancho": f"{formato['ancho']}px", "--alto": f"{formato['alto']}px",
    }
    if z:
        variables.update({"--zs-arriba": f"{z['arriba']}px", "--zs-abajo": f"{z['abajo']}px",
                          "--zs-izquierda": f"{z['izquierda']}px", "--zs-derecha": f"{z['derecha']}px"})
    for clave in ("acento", "secundario"):  # texto legible encima del acento y del secundario (botones, bandas)
        oscuro, claro = "#0F172A", "#FFFFFF"
        mejor = oscuro if contraste(c[clave], oscuro) >= contraste(c[clave], claro) else claro
        variables[f"--color-texto-sobre-{clave}"] = mejor
    cuerpo = ";".join(f"{k}:{v}" for k, v in variables.items())
    return f'<style id="render-marca">{ff_t}{ff_x}:root{{{cuerpo}}}</style>'


def contexto_marca(marca: dict, avisos: list[str]) -> dict:
    ctx = {k: v for k, v in marca.items() if not k.startswith("_")}
    logos = dict(ctx.get("logo") or {})
    for clave in ("principal", "claro"):
        valor = str(logos.get(clave) or "")
        archivo = _resolver_archivo(valor, marca.get("_dir"))
        if valor and archivo is None:
            avisos.append(f"No encuentro el logo {clave} {valor!r} (las rutas son relativas a la carpeta de la marca)")
        logos[clave] = data_uri(archivo) if archivo else ""
    if not logos["claro"]:
        logos["claro"] = logos["principal"]
    if not logos["principal"]:
        logos["principal"] = logos["claro"]
    ctx["logo"] = logos
    return ctx


# ───────────────────────────── plantillado ─────────────────────────────
_ETIQUETA = re.compile(r"\{\{\s*([#^/]?)\s*([^{}]*?)\s*\}\}")
_FALTA = object()


def _parsear(texto: str) -> list:
    """Árbol: str | ("var", nombre, filtros) | ("sec", nombre, invertida, hijos)."""
    raiz: list = []
    pila: list[tuple[str, list, bool]] = [("", raiz, False)]
    pos = 0
    for m in _ETIQUETA.finditer(texto):
        if m.start() > pos:
            pila[-1][1].append(texto[pos:m.start()])
        pos = m.end()
        tipo, nombre = m.group(1), m.group(2).strip()
        if not nombre:
            raise ErrorUsuario(f"Etiqueta vacía en la plantilla: {m.group(0)!r}")
        if tipo in ("#", "^"):
            hijos: list = []
            pila[-1][1].append(("sec", nombre, tipo == "^", hijos))
            pila.append((nombre, hijos, tipo == "^"))
        elif tipo == "/":
            if len(pila) == 1 or pila[-1][0] != nombre:
                abierta = pila[-1][0] or "ninguna"
                raise ErrorUsuario(f"Cierre {{{{/{nombre}}}}} sin apertura (sección abierta: {abierta})")
            pila.pop()
        else:
            partes = [p.strip() for p in nombre.split("|")]
            raiz_v = ("var", partes[0], partes[1:])
            pila[-1][1].append(raiz_v)
    if len(pila) > 1:
        raise ErrorUsuario(f"Falta cerrar la sección {{{{#{pila[-1][0]}}}}} con {{{{/{pila[-1][0]}}}}}")
    if pos < len(texto):
        raiz.append(texto[pos:])
    return raiz


def _buscar(pila: list, nombre: str) -> Any:
    if nombre == ".":
        return pila[-1]
    partes = nombre.split(".")
    for marco in reversed(pila):
        if isinstance(marco, dict) and partes[0] in marco:
            valor = marco[partes[0]]
            for p in partes[1:]:
                if isinstance(valor, dict) and p in valor:
                    valor = valor[p]
                elif isinstance(valor, list) and p.isdigit() and int(p) < len(valor):
                    valor = valor[int(p)]
                else:
                    return _FALTA
            return valor
    return _FALTA


def _num(valor: Any, decimales: int | None = None) -> str:
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if decimales is None:
        decimales = 0 if n == int(n) else 2
    texto = f"{n:,.{decimales}f}"  # 12,345.67
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


class Plantilla:
    """Plantilla HTML con sustitución escapada, secciones y filtros. `base` resuelve rutas del filtro `uri`."""

    def __init__(self, texto: str, base: pathlib.Path | None = None):
        self.arbol = _parsear(texto)
        self.base = base
        self.faltan: list[str] = []

    def _filtrar(self, valor: Any, filtros: list[str]) -> str:
        for f in filtros:
            if f == "uri":
                texto = str(valor or "")
                if not texto or re.match(r"^(data:|https?://)", texto):
                    valor = texto
                else:
                    archivo = _resolver_archivo(texto, self.base)
                    if archivo is None:
                        self.faltan.append(f"archivo {texto!r} (las rutas son relativas al JSON de datos)")
                        valor = ""
                    else:
                        valor = data_uri(archivo)
            elif f == "mayusculas":
                valor = str(valor).upper()
            elif f == "num":
                valor = _num(valor)
            elif f == "eur":
                valor = _num(valor, 2 if isinstance(valor, float) and valor != int(valor) else 0) + " €"
            elif f == "pct":
                valor = _num(valor, 1) + " %"
            else:
                raise ErrorUsuario(f"Filtro desconocido: |{f} (usa uri, mayusculas, num, eur o pct)")
        return "" if valor is None else str(valor)

    def _render(self, nodos: list, pila: list) -> str:
        out: list[str] = []
        for n in nodos:
            if isinstance(n, str):
                out.append(n)
            elif n[0] == "var":
                _, nombre, filtros = n
                valor = _buscar(pila, nombre)
                if valor is _FALTA:
                    self.faltan.append(nombre)
                    valor = ""
                if isinstance(valor, bool):
                    valor = "true" if valor else "false"
                elif isinstance(valor, float) and not filtros:
                    valor = _num(valor)
                elif isinstance(valor, (dict, list)) and not filtros:
                    valor = ""
                out.append(html.escape(self._filtrar(valor, filtros), quote=True))
            else:
                _, nombre, invertida, hijos = n
                condicion = nombre.endswith("?")  # {{#lista?}}: solo comprueba que no esté vacía; no entra en ella
                valor = _buscar(pila, nombre[:-1] if condicion else nombre)
                vacio = valor is _FALTA or valor in (None, "", False, 0) or (isinstance(valor, (list, dict)) and not valor)
                if invertida:
                    if vacio:
                        out.append(self._render(hijos, pila))
                    continue
                if vacio:
                    continue
                if condicion:
                    out.append(self._render(hijos, pila))
                    continue
                if isinstance(valor, list):
                    total = len(valor)
                    for i, elem in enumerate(valor):
                        meta = {"@indice": i + 1, "@indice0": i, "@total": total, "@primero": i == 0,
                                "@ultimo": i == total - 1}
                        out.append(self._render(hijos, pila + [meta, elem]))
                elif isinstance(valor, dict):
                    out.append(self._render(hijos, pila + [valor]))
                else:
                    out.append(self._render(hijos, pila))
        return "".join(out)

    def render(self, contexto: dict) -> str:
        self.faltan = []
        return self._render(self.arbol, [contexto])


def renderizar_texto(texto: str, contexto: dict, base: pathlib.Path | None = None) -> tuple[str, list[str]]:
    """Atajo: devuelve (html, claves que faltan)."""
    p = Plantilla(texto, base)
    salida = p.render(contexto)
    return salida, list(dict.fromkeys(p.faltan))


def formatos_de_plantilla(texto: str) -> list[str] | None:
    m = re.search(r'<meta\s+name=["\']formatos["\']\s+content=["\']([^"\']+)["\']', texto, re.I)
    if not m:
        return None
    return [f.strip().lower() for f in m.group(1).split(",") if f.strip()]


def _inyectar(html_txt: str, bloque: str) -> str:
    m = re.search(r"</head\s*>", html_txt, re.I)
    if m:
        return html_txt[:m.start()] + bloque + html_txt[m.start():]
    return bloque + html_txt


def construir_html(plantilla: pathlib.Path, datos: dict, base_datos: pathlib.Path | None, marca: dict,
                   formato: dict, avisos: list[str]) -> str:
    texto = plantilla.read_text(encoding="utf-8")
    for reservada in ("marca", "formato", "hoy"):
        if reservada in datos:
            avisos.append(f"La clave «{reservada}» de los datos es reservada y se ignora")
    ctx = {k: v for k, v in datos.items() if k not in ("marca", "formato", "hoy")}
    ctx.update({"marca": contexto_marca(marca, avisos), "formato": formato, "hoy": dt.date.today().isoformat()})
    cuerpo, faltan = renderizar_texto(texto, ctx, base_datos)
    for f in faltan:
        aviso = f"Falta el dato {f}" if f.startswith("archivo ") else f"Falta el dato «{f}» en --datos"
        if aviso not in avisos:
            avisos.append(aviso)
    base_href = f'<base href="{plantilla.resolve().parent.as_uri()}/">'  # rutas relativas = las de la plantilla
    return _inyectar(cuerpo, base_href + css_inyectado(marca, formato, avisos))


def leer_datos(ruta: str | None) -> tuple[dict, pathlib.Path | None]:
    if not ruta:
        return {}, None
    p = pathlib.Path(ruta)
    if not p.is_file():
        raise ErrorUsuario(f"No existe el archivo de datos {ruta}")
    try:
        datos = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ErrorUsuario(f"{ruta} no es un JSON válido: {e}") from None
    if not isinstance(datos, dict):
        raise ErrorUsuario(f"{ruta} debe ser un objeto JSON ({{…}})")
    return datos, p.resolve().parent


# ───────────────────────────── navegador ─────────────────────────────
ARREGLO_PLAYWRIGHT = "uv sync --extra render  (o ejecuta con: uv run --extra render python -I herramientas/render.py …)"
ARREGLO_NAVEGADOR = "uv run --extra render playwright install chromium  (o instala Google Chrome o Microsoft Edge)"

JS_ESPERAR = """async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].map(i => i.complete ? 0 :
    new Promise(r => { i.addEventListener('load', r); i.addEventListener('error', r); })));
  return [...document.images].filter(i => !i.naturalWidth).map(i => (i.getAttribute('src') || '').slice(0, 80));
}"""

JS_AJUSTAR = """() => {
  const out = [];
  for (const el of document.querySelectorAll('[data-ajustar]')) {
    const min = parseFloat(el.dataset.ajustarMin || '0.6');
    // Desborda si algún hijo (por su caja de margen: un margen negativo es un sangrado intencionado) se sale de el,
    // o si hay texto que no cabe a lo ancho.
    const desborda = () => {
      const c = el.getBoundingClientRect();
      if (el.scrollWidth > el.clientWidth + 1) return true;
      for (const h of el.children) {
        const r = h.getBoundingClientRect();
        if (!r.height) continue;
        const mb = parseFloat(getComputedStyle(h).marginBottom) || 0;
        if (r.bottom + Math.min(mb, 0) > c.bottom + 1 || r.right > c.right + 1) return true;
      }
      return false;
    };
    let e = 1;
    while (desborda() && e > min) { e = Math.round((e - 0.03) * 100) / 100; el.style.setProperty('--escala', e); }
    const t = el.closest('[data-tarjeta]');
    const idx = t ? [...document.querySelectorAll('[data-tarjeta]')].indexOf(t) + 1 : null;
    out.push({elemento: el.getAttribute('data-ajustar') || el.className || el.tagName, tarjeta: idx, escala: e,
              desborda: desborda()});
  }
  return out;
}"""

JS_ZONA = """(z) => {
  const out = [];
  const tarjetas = [...document.querySelectorAll('[data-tarjeta]')];
  const x0 = z.izquierda, y0 = z.arriba, x1 = z.ancho - z.derecha, y1 = z.alto - z.abajo;
  for (const el of document.querySelectorAll('[data-zona-segura]')) {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height || getComputedStyle(el).visibility === 'hidden') continue;
    const t = el.closest('[data-tarjeta]');
    let ox = 0, oy = 0, idx = null;
    if (t) { const tr = t.getBoundingClientRect(); ox = tr.left; oy = tr.top; idx = tarjetas.indexOf(t) + 1; }
    const b = {x0: r.left - ox, y0: r.top - oy, x1: r.right - ox, y1: r.bottom - oy};
    const nombre = el.getAttribute('data-zona-segura') || el.className || el.tagName.toLowerCase();
    const caja = [b.x0, b.y0, b.x1, b.y1].map(v => Math.round(v));
    if (b.x0 < x0 - 0.5 || b.y0 < y0 - 0.5 || b.x1 > x1 + 0.5 || b.y1 > y1 + 0.5)
      out.push({elemento: nombre, tarjeta: idx, caja, problema: 'fuera de la zona segura'});
    for (const ex of z.exclusiones || []) {
      if (b.x0 < ex.x1 && b.x1 > ex.x0 && b.y0 < ex.y1 && b.y1 > ex.y0)
        out.push({elemento: nombre, tarjeta: idx, caja, problema: 'pisa la ' + ex.motivo});
    }
    const st = getComputedStyle(el);
    if (el.scrollWidth > el.clientWidth + 2 || (st.overflowY !== 'visible' && el.scrollHeight > el.clientHeight + 2))
      out.push({elemento: nombre, tarjeta: idx, caja, problema: 'el texto se desborda de su caja'});
  }
  return {avisos: out, tarjetas: tarjetas.length};
}"""


def _importar_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415
    except ImportError:
        raise ErrorConfig(f"Falta Playwright (extra «render»). Arreglo: {ARREGLO_PLAYWRIGHT}") from None
    return sync_playwright


def _lanzar(pw) -> tuple[Any, str]:
    """Chromium de Playwright y, si falta, Chrome o Edge del sistema. Devuelve (navegador, cuál)."""
    errores: list[str] = []
    for canal in (None, "chrome", "msedge"):
        try:
            opciones: dict[str, Any] = {"args": ["--allow-file-access-from-files", "--font-render-hinting=none"]}
            if canal:
                opciones["channel"] = canal
            return pw.chromium.launch(**opciones), canal or "chromium"
        except Exception as e:  # noqa: BLE001 - probamos el siguiente navegador
            errores.append(f"{canal or 'chromium'}: {str(e).splitlines()[0][:120]}")
    raise ErrorConfig("No puedo abrir ningún navegador (" + " · ".join(errores) + f"). Arreglo: {ARREGLO_NAVEGADOR}")


def _escribir_temporal(html_txt: str, carpeta: pathlib.Path, nombre: str) -> pathlib.Path:
    p = carpeta / f"{nombre}.html"
    p.write_text(html_txt, encoding="utf-8")
    return p


def _dimensiones_png(ruta: pathlib.Path) -> tuple[int, int]:
    import struct  # noqa: PLC0415

    cabecera = ruta.read_bytes()[:24]
    if cabecera[:8] != b"\x89PNG\r\n\x1a\n":
        return 0, 0
    return struct.unpack(">II", cabecera[16:24])


# ───────────────────────────── órdenes ─────────────────────────────
def render_png(plantilla: str, datos: str | None, formatos: str | None, salida: str, cliente: str | None = None,
               marca_ruta: str | None = None, nombre: str | None = None) -> dict:
    p = pathlib.Path(plantilla)
    if not p.is_file():
        raise ErrorUsuario(f"No existe la plantilla {plantilla}")
    texto = p.read_text(encoding="utf-8")
    try:
        lista = parsear_formatos(formatos, formatos_de_plantilla(texto))
    except ValueError as e:
        raise ErrorUsuario(str(e)) from None
    datos_d, base = leer_datos(datos)
    marca = cargar_marca(cliente, marca_ruta)
    avisos: list[str] = list(marca["_avisos"])
    prefijo = re.sub(r"[^\w.-]+", "-", nombre or p.stem).strip("-") or p.stem
    destino = pathlib.Path(salida)
    destino.mkdir(parents=True, exist_ok=True)
    htmls = {f: construir_html(p, datos_d, base, marca, contexto_formato(f), avisos) for f in lista}
    sync_playwright = _importar_playwright()
    archivos: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="render_") as tmp, sync_playwright() as pw:
        navegador, canal = _lanzar(pw)
        try:
            for f in lista:
                ancho, alto = FORMATOS[f]
                pagina = navegador.new_page(viewport={"width": ancho, "height": alto}, device_scale_factor=1)
                pagina.goto(_escribir_temporal(htmls[f], pathlib.Path(tmp), f"{prefijo}_{f}").as_uri(), wait_until="load")
                rotas = pagina.evaluate(JS_ESPERAR)
                for src in rotas:
                    avisos.append(f"[{f}] imagen que no carga: {src}")
                for a in pagina.evaluate(JS_AJUSTAR):
                    donde = f"[{f}{'' if a['tarjeta'] is None else ' tarjeta ' + str(a['tarjeta'])}]"
                    if a["desborda"]:
                        avisos.append(f"{donde} «{a['elemento']}» no cabe ni al {int(a['escala'] * 100)} %: acorta el texto")
                    elif a["escala"] < 1:
                        avisos.append(f"{donde} «{a['elemento']}» reducido al {int(a['escala'] * 100)} % para que quepa")
                z = {**zona_segura(f), "ancho": ancho, "alto": alto}
                medida = pagina.evaluate(JS_ZONA, z)
                for a in medida["avisos"]:
                    donde = f"[{f}{'' if a['tarjeta'] is None else ' tarjeta ' + str(a['tarjeta'])}]"
                    avisos.append(f"{donde} «{a['elemento']}» {a['problema']} (caja {a['caja']})")
                n = medida["tarjetas"]
                if n:
                    if n < 2 or n > 10:
                        avisos.append(f"[{f}] {n} tarjetas: un carrusel de Meta admite de 2 a 10")
                    tarjetas = pagina.locator("[data-tarjeta]")
                    for i in range(n):
                        ruta = destino / f"{prefijo}_{f}_{i + 1:02d}.png"
                        tarjetas.nth(i).screenshot(path=str(ruta), animations="disabled")
                        w, h = _dimensiones_png(ruta)
                        if (w, h) != (ancho, alto):
                            avisos.append(f"[{f}] la tarjeta {i + 1} mide {w}×{h} y debería medir {ancho}×{alto}")
                        archivos.append({"ruta": _rel(ruta), "formato": f, "tarjeta": i + 1, "ancho": w, "alto": h})
                else:
                    ruta = destino / f"{prefijo}_{f}.png"
                    pagina.screenshot(path=str(ruta), full_page=False, animations="disabled")
                    w, h = _dimensiones_png(ruta)
                    alto_doc = pagina.evaluate("() => document.documentElement.scrollHeight")
                    if alto_doc > alto + 1:
                        avisos.append(f"[{f}] el contenido mide {alto_doc} px de alto y se recorta a {alto} px")
                    archivos.append({"ruta": _rel(ruta), "formato": f, "tarjeta": None, "ancho": w, "alto": h})
                pagina.close()
        finally:
            navegador.close()
    return {"ok": True, "orden": "png", "plantilla": _rel(p), "formatos": lista, "marca": marca["_origen"],
            "navegador": canal, "archivos": archivos, "avisos": avisos}


def _contar_paginas_pdf(ruta: pathlib.Path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", ruta.read_bytes()))


def render_pdf(plantilla: str, salida: str, datos: str | None = None, cliente: str | None = None,
               marca_ruta: str | None = None) -> dict:
    p = pathlib.Path(plantilla)
    if not p.is_file():
        raise ErrorUsuario(f"No existe la plantilla {plantilla}")
    destino = pathlib.Path(salida)
    if destino.suffix.lower() != ".pdf":
        raise ErrorUsuario(f"--salida debe acabar en .pdf (recibido: {salida})")
    datos_d, base = leer_datos(datos)
    marca = cargar_marca(cliente, marca_ruta)
    avisos: list[str] = list(marca["_avisos"])
    html_txt = construir_html(p, datos_d, base, marca, contexto_formato("a4"), avisos)
    sync_playwright = _importar_playwright()
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="render_") as tmp, sync_playwright() as pw:
        navegador, canal = _lanzar(pw)
        try:
            pagina = navegador.new_page(viewport={"width": A4["ancho"], "height": A4["alto"]})
            pagina.goto(_escribir_temporal(html_txt, pathlib.Path(tmp), p.stem).as_uri(), wait_until="load")
            for src in pagina.evaluate(JS_ESPERAR):
                avisos.append(f"imagen que no carga: {src}")
            pagina.emulate_media(media="print")
            opciones: dict[str, Any] = {"path": str(destino), "format": "A4", "print_background": True}
            if re.search(r"@page\b", html_txt):
                opciones["prefer_css_page_size"] = True  # márgenes y tamaño los decide la plantilla
            else:
                opciones["margin"] = {"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"}
            pagina.pdf(**opciones)
        finally:
            navegador.close()
    return {"ok": True, "orden": "pdf", "plantilla": _rel(p), "marca": marca["_origen"], "navegador": canal,
            "archivo": _rel(destino), "paginas": _contar_paginas_pdf(destino), "avisos": avisos}


# ───────────────────────────── CLI ─────────────────────────────
def _imprimir(res: dict, como_json: bool) -> None:
    if como_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    if res["orden"] == "png":
        print(f"Marca: {res['marca']} · formatos: {', '.join(res['formatos'])}")
        for a in res["archivos"]:
            print(f"  ✓ {a['ruta']}  ({a['ancho']}×{a['alto']})")
    else:
        print(f"Marca: {res['marca']}")
        print(f"  ✓ {res['archivo']}  ({res['paginas']} páginas)")
    if res["avisos"]:
        print("Avisos:")
        for a in res["avisos"]:
            print(f"  ! {a}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="render.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="orden", required=True)
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--datos", help="JSON con los datos de la plantilla")
    comunes.add_argument("--cliente", help="slug del cliente: aplica clientes/<slug>/marca/marca.json")
    comunes.add_argument("--marca", help="marca.json o su carpeta (prevalece sobre --cliente)")
    comunes.add_argument("--json", action="store_true", help="salida en JSON")
    a_png = sub.add_parser("png", parents=[comunes], help="plantilla → PNG en 1x1, 4x5 y/o 9x16")
    a_png.add_argument("plantilla")
    a_png.add_argument("--formatos", help="lista separada por comas: 1x1,4x5,9x16 (por defecto, los que admita)")
    a_png.add_argument("--salida", required=True, help="carpeta de salida")
    a_png.add_argument("--nombre", help="prefijo de los archivos (por defecto, el nombre de la plantilla)")
    a_pdf = sub.add_parser("pdf", parents=[comunes], help="HTML o plantilla → PDF A4")
    a_pdf.add_argument("html")
    a_pdf.add_argument("--salida", required=True, help="archivo .pdf de salida")
    a = ap.parse_args(argv)
    try:
        if a.orden == "png":
            res = render_png(a.plantilla, a.datos, a.formatos, a.salida, a.cliente, a.marca, a.nombre)
        else:
            res = render_pdf(a.html, a.salida, a.datos, a.cliente, a.marca)
    except ErrorUsuario as e:
        _error(str(e), 1, a.json)
        return 1
    except ErrorConfig as e:
        _error(str(e), 2, a.json)
        return 2
    _imprimir(res, a.json)
    return 0


def _error(msg: str, codigo: int, como_json: bool) -> None:
    if como_json:
        print(json.dumps({"ok": False, "codigo": codigo, "error": msg}, ensure_ascii=False, indent=2))
    else:
        print(f"Error: {msg}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
