#!/usr/bin/env python3
"""Páginas de captación listas para tráfico de Meta: landing, diagnóstico interactivo, reserva, gracias y webinar.

Genera HTML estático (CSS y JS propios, sin dependencias salvo el píxel de Meta tras el consentimiento) con la marca
del cliente, y lo valida antes de publicar. El OS nunca despliega: subes tú la carpeta a tu hosting o a GHL.

Uso:
  python3 -I herramientas/paginas.py generar <landing|diagnostico|reserva|gracias|webinar|todas> \
      --config <config.json> --salida <carpeta> [--cliente SLUG | --marca RUTA] [--en-linea] [--fragmento-ghl] [--json]
  python3 -I herramientas/paginas.py validar <carpeta> [--json]
  python3 -I herramientas/paginas.py probar --config <config.json> [--respuestas <respuestas.json>] [--json]

  generar   escribe las páginas pedidas y `recursos/` (JS, logo, imágenes, fuentes, .ics). No borra nada: solo
            sobrescribe los archivos que genera.
            --en-linea       mete también el JS dentro de cada HTML (un archivo por página, más imágenes)
            --fragmento-ghl  además, `ghl/<página>.html`: fragmento para el elemento «Custom code» de GHL
  validar   peso, imágenes, tracking (config, webhook, píxel tras consentimiento), formularios, accesibilidad básica,
            enlaces y contenido de ejemplo sin sustituir. Código 1 si hay errores.
  probar    calcula el diagnóstico con unas respuestas o con los `escenarios` del config y comprueba el nivel
            (recomendación) esperado. Sirve para ajustar umbrales honestos antes de publicar.

Formato del config, del envío al webhook y de las fórmulas: plantillas/paginas/README.md.
Ejemplos: plantillas/paginas/ejemplos/acme-embudo.json (landing → diagnóstico → reserva → gracias) y
plantillas/paginas/ejemplos/nimbo-webinar.json (webinar → gracias).
Contrato: docs/desarrollo/contratos.md §16 (etapas y eventos) y §17 (páginas generadas).

Códigos de salida: 0 ok (aunque haya avisos) · 1 error del usuario o validación con errores · 2 error de configuración.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html as htmlmod
import html.parser
import json
import math
import pathlib
import re
import shutil
import struct
import sys
import urllib.parse
import zoneinfo
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402
import render  # noqa: E402
from render import ErrorUsuario  # noqa: E402

PLANTILLAS = pathlib.Path(__file__).resolve().parent.parent / "plantillas" / "paginas"
TIPOS = ("landing", "diagnostico", "reserva", "gracias", "webinar")
ARCHIVO_DEFECTO = {"landing": "index.html", "diagnostico": "diagnostico.html", "reserva": "reserva.html",
                   "gracias": "gracias.html", "webinar": "webinar.html"}
GENERADOR = "meta-ads-os/paginas"
_ID = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
_ARCHIVO = re.compile(r"^[a-z0-9][a-z0-9._-]{0,80}\.html$")
_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
# Claves del envío v1 al webhook (plantillas/paginas/README.md): un campo del formulario con uno de estos ids las
# pisaría (origen, momento, ref…), así que se rechazan. «web2» es la trampa antispam y «acepta_*», las casillas.
CLAVES_ENVIO = frozenset((
    "version", "origen", "tipo_envio", "pagina", "url", "event_source_url", "momento", "event_time", "ref",
    "content_name", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "campaign_id",
    "adset_id", "ad_id", "placement", "site", "respuestas", "diagnostico", "consentimiento_marketing",
    "base_legal_servidor", "enviar_a_meta", "event_name", "event_id", "eventos", "fbclid", "fbc", "fbp",
    "client_user_agent", "web2"))
# Símbolo de la moneda en las etiquetas (el mismo que formatear() de diagnostico.js); si no está, el código ISO.
SIMBOLO_MONEDA = {"EUR": "€", "USD": "US$", "GBP": "£"}
# Zona horaria del webinar si no se dice otra (ni en el evento ni en la ficha) y su etiqueta por defecto.
ZONA_DEFECTO = "Europe/Madrid"
ETIQUETA_ZONA = {"Europe/Madrid": "Hora peninsular española", "Atlantic/Canary": "Hora de Canarias",
                 "America/Mexico_City": "Hora del centro de México", "America/Bogota": "Hora de Colombia",
                 "America/Lima": "Hora de Perú", "America/Santiago": "Hora de Chile",
                 "America/Argentina/Buenos_Aires": "Hora de Argentina", "America/Montevideo": "Hora de Uruguay",
                 "America/Guayaquil": "Hora de Ecuador", "America/Caracas": "Hora de Venezuela",
                 "Europe/Lisbon": "Hora de Portugal", "Europe/London": "Hora de Reino Unido",
                 "America/New_York": "Hora del este de EE. UU."}

# Umbrales de validar [HYPOTHESIS]: orientativos para móvil y navegador interno de Instagram/Facebook.
PESO_TOTAL_AVISO = 600 * 1024
PESO_TOTAL_ERROR = 2 * 1024 * 1024
PESO_IMAGEN_AVISO = 300 * 1024
PESO_IMAGEN_ERROR = 1024 * 1024
PESO_HTML_AVISO = 150 * 1024

# Frases que suelen acabar en rechazo o en promesas que no puedes sostener (revisa con revisor-politicas).
PROMESAS = re.compile(r"\bgarantiz\w*|\bahorrar[aá]s\b|\bseguro que\b|\b100\s?%|\bsin riesgo\b|\bduplica\w* tus\b|"
                      r"\btriplica\w* tus\b|\bresultados? asegurados?\b", re.I)
# Reproductores de vídeo que no deben ir incrustados en el HTML (validar: video.terceros).
VIDEO_TERCEROS = re.compile(r"^(?:https?:)?//(?:[\w-]+\.)*(?:youtube(?:-nocookie)?\.com|youtu\.be|vimeo\.com|"
                            r"wistia\.(?:com|net)|loom\.com|vidyard\.com)/", re.I)


class ErrorExpresion(ValueError):
    """Fórmula mal escrita o con variables que no existen."""


# ════════════════════════════ fórmulas (misma gramática que diagnostico.js) ════════════════════════════
PALABRAS = {"y": "&&", "and": "&&", "o": "||", "or": "||", "no": "!", "not": "!"}
FUNCIONES = {"min": (1, None), "max": (1, None), "abs": (1, 1), "redondear": (1, 2), "limitar": (3, 3), "si": (3, 3),
             "suma": (2, 2), "media": (2, 2), "cuenta": (1, 1), "mayor": (3, 3)}
DE_GRUPO = {"suma", "media", "cuenta", "mayor"}
COMPARADORES = ("<", "<=", ">", ">=", "==", "!=")
_T_NUM = re.compile(r"[0-9]+(?:\.[0-9]+)?")
_T_ID = re.compile(r"[a-z_][a-z0-9_]*")
_T_OP = re.compile(r"<=|>=|==|!=|&&|\|\||[-+*/%^()<>,!]")
_PARSEFLOAT = re.compile(r"\s*[+-]?(?:[0-9]+\.?[0-9]*(?:[eE][+-]?[0-9]+)?|\.[0-9]+(?:[eE][+-]?[0-9]+)?)")


def tokenizar(texto: str) -> list[tuple[str, Any]]:
    t = str(texto)
    out: list[tuple[str, Any]] = []
    i = 0
    while i < len(t):
        c = t[i]
        if c in " \t\r\n\f\v":
            i += 1
            continue
        m = _T_NUM.match(t, i)
        if m:
            out.append(("num", float(m.group())))
            i = m.end()
            continue
        m = _T_ID.match(t, i)
        if m:
            w = m.group()
            out.append(("op", PALABRAS[w]) if w in PALABRAS else ("id", w))
            i = m.end()
            continue
        m = _T_OP.match(t, i)
        if m:
            out.append(("op", m.group()))
            i = m.end()
            continue
        raise ErrorExpresion(f"Carácter no válido «{c}» en la posición {i + 1}")
    return out


def parsear(texto: str) -> tuple:
    """Árbol: ("num", v) | ("var", n) | ("un", op, a) | ("bin", op, a, b) | ("fn", nombre, [args])."""
    tk = tokenizar(texto)
    p = 0

    def ver(v: str) -> bool:
        return p < len(tk) and tk[p][0] == "op" and tk[p][1] == v

    def tomar(v: str) -> None:
        nonlocal p
        if not ver(v):
            raise ErrorExpresion(f"Se esperaba «{v}»")
        p += 1

    def o_():
        nonlocal p
        a = y_()
        while ver("||"):
            p += 1
            a = ("bin", "||", a, y_())
        return a

    def y_():
        nonlocal p
        a = no_()
        while ver("&&"):
            p += 1
            a = ("bin", "&&", a, no_())
        return a

    def no_():
        nonlocal p
        if ver("!"):
            p += 1
            return ("un", "!", no_())
        return comparacion()

    def comparacion():
        nonlocal p
        a = suma()
        if p < len(tk) and tk[p][0] == "op" and tk[p][1] in COMPARADORES:
            op = tk[p][1]
            p += 1
            a = ("bin", op, a, suma())
        return a

    def suma():
        nonlocal p
        a = producto()
        while ver("+") or ver("-"):
            op = tk[p][1]
            p += 1
            a = ("bin", op, a, producto())
        return a

    def producto():
        nonlocal p
        a = unario()
        while ver("*") or ver("/") or ver("%"):
            op = tk[p][1]
            p += 1
            a = ("bin", op, a, unario())
        return a

    def unario():
        nonlocal p
        if ver("-"):
            p += 1
            return ("un", "-", unario())
        if ver("+"):
            p += 1
            return unario()
        return potencia()

    def potencia():
        nonlocal p
        a = primario()
        if ver("^"):
            p += 1
            a = ("bin", "^", a, unario())
        return a

    def primario():
        nonlocal p
        if p >= len(tk):
            raise ErrorExpresion("La fórmula termina antes de tiempo")
        k = tk[p]
        if k[0] == "num":
            p += 1
            return ("num", k[1])
        if k[0] == "id":
            p += 1
            if ver("("):
                if k[1] not in FUNCIONES:
                    raise ErrorExpresion(f"Función desconocida «{k[1]}»")
                p += 1
                args = []
                if not ver(")"):
                    args.append(o_())
                    while ver(","):
                        p += 1
                        args.append(o_())
                tomar(")")
                return ("fn", k[1], args)
            return ("var", k[1])
        if ver("("):
            p += 1
            e = o_()
            tomar(")")
            return e
        raise ErrorExpresion(f"Símbolo inesperado «{k[1]}»")

    arbol = o_()
    if p < len(tk):
        raise ErrorExpresion(f"Sobra «{tk[p][1]}» al final")
    return arbol


def num(v: Any) -> float | None:
    """Igual que num() de diagnostico.js: vacío → None; booleano → 1/0; texto → como parseFloat (coma decimal)."""
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(v) else None
    if isinstance(v, (list, dict)):
        return None
    m = _PARSEFLOAT.match(str(v).replace(",", ".", 1))
    if not m:
        return None
    try:
        n = float(m.group())
    except ValueError:
        return None
    return n if math.isfinite(n) else None


_MILES_ESPACIO = re.compile(r"(?<=\d)[ \u00a0\u2009\u202f](?=\d{3}(?!\d))")
_NUMERO_HUMANO = re.compile(r"[-+]?(?:\d[\d.,]*|[.,]\d+)(?:[eE][-+]?\d+)?")


def num_humano(v: Any) -> float | None:
    """Número escrito por una persona: «1.200» = 1200, «1.500,50» = 1500,5, «0.175» = 0,175, «1 200» = 1200.

    Para los valores del config (supuestos, valor_evento, min/max…) y las respuestas. Es la regla de
    `_comun.numero()` y de numEntrada() de paginas.js y diagnostico.js (vectores compartidos en
    tests/herramientas/paginas_vectores.json): con punto y coma, el último es el decimal; con un solo separador, son
    miles los grupos de 3 cifras tras un primer grupo de 1 a 3 que no empieza por 0. A diferencia de
    `_comun.numero()`, el texto entero tiene que ser el número («1.200 €» → None). `num()` sigue siendo el de las
    fórmulas (como parseFloat).
    """
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(v) else None
    if not isinstance(v, str):
        return None
    t = _MILES_ESPACIO.sub("", v.strip())
    if not _NUMERO_HUMANO.fullmatch(t):
        return None
    exp = ""
    me = re.search(r"[eE][-+]?\d+$", t)
    if me:
        t, exp = t[:me.start()], me.group(0)
    signo = "-" if t.startswith("-") else ""
    t = t.lstrip("+-").rstrip(".,")
    if not t or not re.search(r"\d", t):
        return None
    if "," in t and "." in t:
        dec = "," if t.rfind(",") > t.rfind(".") else "."
        entero, _, fraccion = t.rpartition(dec)
        miles = "." if dec == "," else ","
        if not re.fullmatch(rf"\d{{1,3}}(?:\{miles}\d{{3}})*|\d+", entero) or not fraccion.isdigit():
            return None
        n = float(f"{signo}{entero.replace(miles, '')}.{fraccion}{exp}")
    else:
        sep = "," if "," in t else ("." if "." in t else "")
        if sep and re.fullmatch(rf"[1-9]\d{{0,2}}(?:\{sep}\d{{3}})+", t):
            n = float(signo + t.replace(sep, "") + exp)
        elif sep and t.count(sep) > 1:
            return None
        else:
            n = float(signo + t.replace(sep, ".") + exp) if sep else float(signo + t + exp)
    return n if math.isfinite(n) else None


def _verdad(v: Any) -> bool:
    n = num(v)
    return n is not None and n != 0


def js_round(x: float) -> float:
    """Math.round de JavaScript (redondea .5 hacia arriba, no al par)."""
    return float(math.floor(x + 0.5))


def evaluar(arbol: tuple, buscar) -> Any:
    t = arbol[0]
    if t == "num":
        return arbol[1]
    if t == "var":
        return buscar(arbol[1])
    if t == "un":
        if arbol[1] == "!":
            return 0.0 if _verdad(evaluar(arbol[2], buscar)) else 1.0
        x = num(evaluar(arbol[2], buscar))
        return None if x is None else -x
    if t == "bin":
        op = arbol[1]
        if op == "&&":
            return 1.0 if _verdad(evaluar(arbol[2], buscar)) and _verdad(evaluar(arbol[3], buscar)) else 0.0
        if op == "||":
            return 1.0 if _verdad(evaluar(arbol[2], buscar)) or _verdad(evaluar(arbol[3], buscar)) else 0.0
        a = num(evaluar(arbol[2], buscar))
        b = num(evaluar(arbol[3], buscar))
        if op in COMPARADORES:
            if a is None or b is None:
                return 0.0
            return 1.0 if {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b,
                           "==": abs(a - b) < 1e-9, "!=": abs(a - b) >= 1e-9}[op] else 0.0
        if a is None or b is None:
            return None
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return None if b == 0 else a / b
        if op == "%":
            return None if b == 0 else math.fmod(a, b)
        try:
            r = math.pow(a, b)
        except (ValueError, OverflowError):
            return None
        return r if math.isfinite(r) else None
    if t == "fn":
        return _funcion(arbol, buscar)
    raise ErrorExpresion("Nodo desconocido")


def _funcion(arbol: tuple, buscar) -> Any:
    n, args = arbol[1], arbol[2]
    if n in DE_GRUPO:
        if not args or args[0][0] != "var":
            raise ErrorExpresion(f"{n}() necesita el nombre de un grupo como primer argumento")
        lista = buscar(args[0][1])
        if not isinstance(lista, list):
            lista = []
        if n == "cuenta":
            return float(len(lista))
        if len(args) < 2:
            raise ErrorExpresion(f"{n}() necesita una expresión como segundo argumento")
        valores = []
        for item in lista:
            def buscar_item(nombre, item=item):
                return item[nombre] if isinstance(item, dict) and nombre in item else buscar(nombre)
            valores.append(num(evaluar(args[1], buscar_item)))
        if n == "suma":
            return sum(v for v in valores if v is not None) if valores else 0.0
        if n == "media":
            validos = [v for v in valores if v is not None]
            return sum(validos) / len(validos) if validos else None
        if len(args) < 3 or args[2][0] != "var":
            raise ErrorExpresion("mayor() necesita el campo que devolver como tercer argumento")
        mejor = -1
        for i, v in enumerate(valores):
            if v is not None and (mejor < 0 or v > valores[mejor]):
                mejor = i
        return None if mejor < 0 else lista[mejor].get(args[2][1])
    if n == "si":
        if len(args) != 3:
            raise ErrorExpresion("si() necesita 3 argumentos: condición, valor si se cumple, valor si no")
        return evaluar(args[1], buscar) if _verdad(evaluar(args[0], buscar)) else evaluar(args[2], buscar)
    v = [num(evaluar(a, buscar)) for a in args]
    if n in ("min", "max"):
        ok = [x for x in v if x is not None]
        if not ok:
            return None
        return min(ok) if n == "min" else max(ok)
    if n == "abs":
        return None if not v or v[0] is None else abs(v[0])
    if n == "redondear":
        if not v or v[0] is None:
            return None
        d = v[1] if len(v) > 1 and v[1] is not None else 0
        f = math.pow(10, d)
        return js_round(v[0] * f) / f
    if n == "limitar":
        if len(v) != 3:
            raise ErrorExpresion("limitar() necesita 3 argumentos: valor, mínimo y máximo")
        if v[0] is None:
            return None
        return min(max(v[0], v[0] if v[1] is None else v[1]), v[0] if v[2] is None else v[2])
    raise ErrorExpresion(f"Función desconocida «{n}»")


def calcular_expresion(texto: str, variables: dict) -> Any:
    def buscar(nombre):
        if nombre in variables:
            return variables[nombre]
        raise ErrorExpresion(f"Variable desconocida «{nombre}»")
    return evaluar(parsear(texto), buscar)


def comprobar_formula(texto: str, conocidas: set[str], grupos: dict[str, set[str]]) -> None:
    """Valida sintaxis, aridad y que cada variable exista (sin evaluar). Lanza ErrorExpresion."""
    arbol = parsear(texto)

    def rec(nodo, ambito: set[str]):
        t = nodo[0]
        if t == "var":
            if nodo[1] not in ambito:
                pista = " (es un grupo: usa suma(), media(), cuenta() o mayor())" if nodo[1] in grupos else ""
                raise ErrorExpresion(f"Variable desconocida «{nodo[1]}»{pista}")
        elif t == "un":
            rec(nodo[2], ambito)
        elif t == "bin":
            rec(nodo[2], ambito)
            rec(nodo[3], ambito)
        elif t == "fn":
            nombre, args = nodo[1], nodo[2]
            minimo, maximo = FUNCIONES[nombre]
            if len(args) < minimo or (maximo is not None and len(args) > maximo):
                esperado = f"{minimo}" if minimo == maximo else (f"al menos {minimo}" if maximo is None
                                                                 else f"entre {minimo} y {maximo}")
                raise ErrorExpresion(f"{nombre}() lleva {esperado} argumento(s) y tiene {len(args)}")
            if nombre in DE_GRUPO:
                if args[0][0] != "var" or args[0][1] not in grupos:
                    raise ErrorExpresion(f"{nombre}() necesita como primer argumento una pregunta de tipo grupo")
                campos = grupos[args[0][1]]
                if len(args) > 1:
                    rec(args[1], ambito | campos)
                if nombre == "mayor" and (args[2][0] != "var" or args[2][1] not in campos):
                    raise ErrorExpresion("mayor() necesita como tercer argumento un campo del grupo")
            else:
                for a in args:
                    rec(a, ambito)

    rec(arbol, conocidas)


# ════════════════════════════ cálculo del diagnóstico ════════════════════════════
def valor_respuesta(pregunta: dict, r: Any) -> Any:
    tipo = pregunta.get("tipo")
    if tipo == "grupo":
        out = []
        for item in r or []:
            item = item if isinstance(item, dict) else {}
            out.append({c["id"]: valor_respuesta(c, item.get(c["id"])) for c in pregunta.get("campos", [])})
        return out
    if tipo == "opciones":
        try:
            i = int(r)
        except (TypeError, ValueError):
            return None
        ops = pregunta.get("opciones") or []
        return ops[i].get("valor") if 0 <= i < len(ops) else None
    if tipo == "numero":
        return num_humano(r)
    return "" if r is None else r


def calcular(diag: dict, respuestas: dict | None, supuestos: dict | None = None) -> dict:
    """Mismo resultado que calcular() de diagnostico.js: {valores, variables, nivel}."""
    variables: dict[str, Any] = {}
    for s in diag.get("supuestos", []):
        propio = num_humano((supuestos or {}).get(s["id"]))
        variables[s["id"]] = propio if propio is not None else s["valor"]
    for p in diag.get("preguntas", []):
        variables[p["id"]] = valor_respuesta(p, (respuestas or {}).get(p["id"]))

    def buscar(nombre):
        if nombre in variables:
            return variables[nombre]
        raise ErrorExpresion(f"Variable desconocida «{nombre}»")

    valores: dict[str, Any] = {}
    for c in diag.get("calculos", []):
        v = evaluar(parsear(c["formula"]), buscar)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and c.get("redondeo"):
            v = js_round(v / c["redondeo"]) * c["redondeo"]
        variables[c["id"]] = v
        valores[c["id"]] = v
    elegido = None
    niveles = diag.get("niveles", [])
    for n in niveles:
        if not n.get("si") or _verdad(evaluar(parsear(n["si"]), buscar)):
            elegido = n
            break
    if elegido is None and niveles:
        elegido = niveles[-1]
    return {"valores": valores, "variables": variables, "nivel": elegido["id"] if elegido else ""}


def respuestas_por_defecto(diag: dict) -> dict:
    """Respuestas «razonables» para la prueba de humo: primera opción, valor por defecto o mínimo, 1 elemento."""
    def una(p):
        if p["tipo"] == "opciones":
            return 0
        if p["tipo"] == "numero":
            return p.get("defecto", p.get("min", 1))
        if p["tipo"] == "texto":
            return "Ejemplo"
        return [{c["id"]: una(c) for c in p.get("campos", [])} for _ in range(max(1, p.get("min_items", 1)))]
    return {p["id"]: una(p) for p in diag.get("preguntas", [])}


# ════════════════════════════ utilidades ════════════════════════════
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _texto(v: Any, defecto: str = "") -> str:
    if v is None:
        return defecto
    return str(v).strip()


def _desfase(d: dt.timedelta | None) -> str:
    """timedelta(hours=2) → «+02:00»."""
    minutos = int((d or dt.timedelta()).total_seconds() // 60)
    signo = "+" if minutos >= 0 else "-"
    return f"{signo}{abs(minutos) // 60:02d}:{abs(minutos) % 60:02d}"


def _num_es(v: float, decimales: int | None = None) -> str:
    """12.5 → «12,5»; 1600 → «1600» (sin separador de miles: es para campos que la persona edita)."""
    if decimales is None:
        decimales = 0 if float(v).is_integer() else 2
    t = f"{float(v):.{decimales}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _slug(t: str) -> str:
    t = t.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"), ("ñ", "n")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60] or "x"


def _json_script(datos: Any) -> str:
    """JSON seguro dentro de <script type="application/json">."""
    t = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    return (t.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def _minificar_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def _css_base(fragmento: bool) -> str:
    css = (PLANTILLAS / "paginas.css").read_text(encoding="utf-8")
    if fragmento:  # el fragmento para GHL no toca html ni body
        css = re.sub(r"/\* documento:.*?/\* /documento \*/", "", css, flags=re.S)
    return _minificar_css(css)


def _rel(p: pathlib.Path) -> str:
    return render._rel(p)


def dimensiones_imagen(ruta: pathlib.Path) -> tuple[int, int] | None:
    """Ancho y alto de PNG, JPEG, GIF, WebP o SVG sin dependencias. None si no se puede leer."""
    try:
        datos = ruta.read_bytes()[:256 * 1024]
    except OSError:
        return None
    try:
        if datos[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", datos[16:24])
        if datos[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", datos[6:10])
        if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
            trozo = datos[12:16]
            if trozo == b"VP8 ":
                w, h = struct.unpack("<HH", datos[26:30])
                return w & 0x3FFF, h & 0x3FFF
            if trozo == b"VP8L":
                b = datos[21:25]
                w = 1 + (((b[1] & 0x3F) << 8) | b[0])
                h = 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
                return w, h
            if trozo == b"VP8X":
                w = 1 + int.from_bytes(datos[24:27], "little")
                h = 1 + int.from_bytes(datos[27:30], "little")
                return w, h
        if datos[:2] == b"\xff\xd8":
            i = 2
            while i < len(datos) - 9:
                if datos[i] != 0xFF:
                    i += 1
                    continue
                marca = datos[i + 1]
                if marca in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", datos[i + 5:i + 9])
                    return w, h
                if marca in (0xD8, 0x01) or 0xD0 <= marca <= 0xD7:
                    i += 2
                    continue
                i += 2 + struct.unpack(">H", datos[i + 2:i + 4])[0]
        if ruta.suffix.lower() == ".svg":
            texto = datos.decode("utf-8", "replace")
            etiqueta = re.search(r"<svg\b[^>]*>", texto, re.S)
            if etiqueta:
                e = etiqueta.group(0)
                w = re.search(r'\bwidth="([\d.]+)(?:px)?"', e)
                h = re.search(r'\bheight="([\d.]+)(?:px)?"', e)
                if w and h:
                    return round(float(w.group(1))), round(float(h.group(1)))
                vb = re.search(r'\bviewBox="[\d.\s-]*?([\d.]+)[\s,]+([\d.]+)"', e)
                if vb:
                    return round(float(vb.group(1))), round(float(vb.group(2)))
    except (struct.error, IndexError, ValueError):
        return None
    return None


# ════════════════════════════ marca → variables CSS ════════════════════════════
def _rgb(hexa: str) -> tuple[int, int, int]:
    h = hexa.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in rgb)


def _mezcla(a: str, b: str, t: float) -> str:
    """Color entre a (t=0) y b (t=1)."""
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def _legible_sobre(fondo: str, candidatos: list[str]) -> str:
    return max(candidatos, key=lambda c: render.contraste(c, fondo))


def tokens_marca(marca: dict, avisos: list[str]) -> dict[str, str]:
    c = marca["colores"]
    fondo, texto, primario = c["fondo"], c["texto"], c["primario"]
    secundario, acento = c["secundario"], c["acento"]
    oscuro, claro = "#0f172a", "#ffffff"
    sobre_primario = c["texto_sobre_primario"]
    if render.contraste(sobre_primario, primario) < 4.5:
        sobre_primario = _legible_sobre(primario, [claro, oscuro])
        avisos.append(f"El texto sobre el color primario no llega a 4,5:1: en los botones uso {sobre_primario}")
    sobre_secundario = _legible_sobre(secundario, [claro, oscuro, fondo, texto])
    superficie = _mezcla(fondo, texto, 0.035)
    t = 0.30
    texto_suave = _mezcla(texto, fondo, t)
    while t > 0 and min(render.contraste(texto_suave, fondo), render.contraste(texto_suave, superficie)) < 4.6:
        t -= 0.02
        texto_suave = _mezcla(texto, fondo, max(t, 0))
    t = 0.45
    borde_control = _mezcla(fondo, texto, t)
    while t < 1 and render.contraste(borde_control, fondo) < 3.0:
        t += 0.03
        borde_control = _mezcla(fondo, texto, min(t, 1))
    primario_suave = _mezcla(fondo, primario, 0.10)
    if render.contraste(texto, primario_suave) < 4.5:
        primario_suave = _mezcla(fondo, primario, 0.05)
    t = 0.22
    suave_oscuro = _mezcla(sobre_secundario, secundario, t)
    while t > 0 and render.contraste(suave_oscuro, secundario) < 4.6:
        t -= 0.02
        suave_oscuro = _mezcla(sobre_secundario, secundario, max(t, 0))
    enlace = primario if render.contraste(primario, fondo) >= 4.5 else texto
    foco = primario if render.contraste(primario, fondo) >= 3.0 else texto
    error = "#b42318" if render.contraste("#b42318", fondo) >= 4.5 else texto
    if render.contraste(texto, fondo) < 4.5:
        avisos.append(f"Contraste bajo entre texto y fondo ({render.contraste(texto, fondo)}:1): la página será difícil de leer")
    r, g, b = _rgb(texto)
    return {
        "--c-primario": primario, "--c-sobre-primario": sobre_primario, "--c-primario-suave": primario_suave,
        "--c-secundario": secundario, "--c-sobre-secundario": sobre_secundario,
        "--c-texto-suave-oscuro": suave_oscuro, "--c-borde-oscuro": _mezcla(secundario, sobre_secundario, 0.2),
        "--c-acento": acento, "--c-fondo": fondo, "--c-superficie": superficie, "--c-texto": texto,
        "--c-texto-suave": texto_suave, "--c-borde": _mezcla(fondo, texto, 0.14), "--c-borde-control": borde_control,
        "--c-enlace": enlace, "--c-foco": foco, "--c-error": error, "--c-error-fondo": _mezcla(fondo, error, 0.08),
        "--c-ok": "#166534" if render.contraste("#166534", fondo) >= 4.5 else texto,
        "--c-sombra": f"rgb({r} {g} {b} / 0.08)", "--c-sombra-fuerte": f"rgb({r} {g} {b} / 0.2)",
    }


PILA_SISTEMA = 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
_FAMILIA = re.compile(r"^[\w .-]{1,60}$")


def fuentes_marca(marca: dict, recursos: pathlib.Path | None, avisos: list[str]) -> tuple[str, dict[str, str], list[str]]:
    """(@font-face, variables CSS, precargas). Solo descarga fuentes si la marca trae un archivo; si no, sistema."""
    caras, variables, precargas = [], {}, []
    for tipo, var, var_peso in (("titulos", "--f-titulos", "--p-titulos"), ("texto", "--f-texto", "--p-texto")):
        t = (marca.get("tipografias") or {}).get(tipo) or {}
        familia = _texto(t.get("familia"))
        try:
            peso = int(t.get("peso") or (750 if tipo == "titulos" else 400))
        except (TypeError, ValueError):
            peso = 750 if tipo == "titulos" else 400
        if tipo == "texto":
            peso = min(max(peso, 350), 500)  # el texto largo se lee mejor entre 400 y 500
        pila = PILA_SISTEMA
        archivo = render._resolver_archivo(_texto(t.get("archivo")), marca.get("_dir"))
        if familia and _FAMILIA.match(familia):
            pila = f'"{familia}", {PILA_SISTEMA}'
        if archivo is not None and recursos is not None:
            ext = archivo.suffix.lower()
            if ext not in (".woff2", ".woff", ".ttf", ".otf"):
                avisos.append(f"Tipografía {archivo.name}: formato no web; uso la del sistema")
            else:
                if ext in (".ttf", ".otf"):
                    avisos.append(f"Tipografía {archivo.name} ({archivo.stat().st_size // 1024} KB): conviértela a .woff2 "
                                  "para que la página cargue antes")
                destino = recursos / "fuentes" / f"{tipo}{ext}"
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(archivo, destino)
                formato = {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype", ".otf": "opentype"}[ext]
                alias = "MarcaTitulos" if tipo == "titulos" else "MarcaTexto"
                caras.append(f'@font-face{{font-family:"{alias}";src:url(recursos/fuentes/{tipo}{ext}) '
                             f'format("{formato}");font-weight:100 900;font-display:swap}}')
                pila = f'"{alias}", {pila}'
                if ext == ".woff2" and tipo == "titulos":
                    precargas.append(f"recursos/fuentes/{tipo}{ext}")
        variables[var] = pila
        variables[var_peso] = str(peso)
    return "".join(caras), variables, precargas


# ════════════════════════════ config ════════════════════════════
class Generador:
    def __init__(self, config_ruta: str, salida: str | None, cliente: str | None = None, marca: str | None = None,
                 en_linea: bool = False, fragmento_ghl: bool = False):
        self.ruta = pathlib.Path(config_ruta)
        if not self.ruta.is_file():
            raise ErrorUsuario(f"No existe el config {config_ruta}")
        try:
            self.cfg = json.loads(self.ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ErrorUsuario(f"{self.ruta.name} no es un JSON válido: {e}") from None
        if not isinstance(self.cfg, dict):
            raise ErrorUsuario("El config debe ser un objeto JSON ({…})")
        self.base = self.ruta.resolve().parent
        self.salida = pathlib.Path(salida) if salida else None
        self.recursos = self.salida / "recursos" if self.salida else None
        self.en_linea = en_linea
        self.fragmento_ghl = fragmento_ghl
        self.avisos: list[str] = []
        self.paginas = self.cfg.get("paginas") or {}
        if not isinstance(self.paginas, dict) or not self.paginas:
            raise ErrorUsuario("El config necesita «paginas» con al menos una de: " + ", ".join(TIPOS))
        desconocidas = [k for k in self.paginas if k not in TIPOS]
        if desconocidas:
            raise ErrorUsuario(f"Páginas desconocidas en el config: {', '.join(desconocidas)} (usa {', '.join(TIPOS)})")
        self.sitio = self.cfg.get("sitio") or {}
        self.tracking = self.cfg.get("tracking") or {}
        self._marca_args = (cliente, marca)
        self._marca: dict | None = None
        self._ficha: dict | None = None
        self.moneda = self._moneda()
        self.zona_ficha = _texto(self.ficha().get("zona_horaria"))
        self._copiados: dict[str, str] = {}
        self.archivos: dict[str, str] = {}
        # Un config con una sola página (registro/ y gracias/ del flujo de /webinar) la genera como index.html: así
        # «…/registro/» y «../gracias/» no dan 404.
        unica = len(self.paginas) == 1
        for tipo, pag in self.paginas.items():
            if not isinstance(pag, dict):
                raise ErrorUsuario(f"paginas.{tipo} debe ser un objeto")
            archivo = _texto(pag.get("archivo"), "index.html" if unica else ARCHIVO_DEFECTO[tipo])
            if not _ARCHIVO.match(archivo):
                raise ErrorUsuario(f"paginas.{tipo}.archivo={archivo!r}: usa un nombre simple terminado en .html")
            self.archivos[tipo] = archivo
        if len(set(self.archivos.values())) != len(self.archivos):
            raise ErrorUsuario("Dos páginas tienen el mismo «archivo»")
        self._validar_tracking()

    def ficha(self) -> dict:
        """Cabecera de la ficha del cliente (con --cliente o marca.cliente): moneda y zona horaria. {} si no hay."""
        if self._ficha is None:
            self._ficha = {}
            slug = self._marca_args[0] or _texto((self.cfg.get("marca") or {}).get("cliente")) or None
            if slug:
                try:
                    self._ficha = _comun.leer_ficha(slug)
                except (_comun.FichaInvalida, OSError) as e:
                    self.avisos.append(f"No puedo leer la ficha de «{slug}» ({e}): uso la moneda y la zona horaria "
                                       "del config (o EUR y Europe/Madrid)")
        return self._ficha

    def _moneda(self) -> str:
        """sitio.moneda; si falta, la de la ficha (con --cliente); si no, EUR. Avisa si config y ficha no coinciden."""
        propia = _texto(self.sitio.get("moneda")).upper()
        de_ficha = _texto(self.ficha().get("moneda")).upper()
        moneda = propia or de_ficha or "EUR"
        if not re.fullmatch(r"[A-Z]{3}", moneda):
            raise ErrorUsuario(f"sitio.moneda={moneda!r}: usa el código ISO 4217 de 3 letras (EUR, USD, MXN…)")
        if propia and de_ficha and propia != de_ficha:
            self.avisos.append(f"sitio.moneda es {propia}, pero la ficha del cliente dice {de_ficha}: el value de los "
                               f"eventos y las cifras irán en {propia}. Si no es lo que quieres, quita sitio.moneda")
        return moneda

    # — enlaces entre páginas: «@diagnostico» → diagnostico.html (o la ruta pública que pongas) —
    def href(self, valor: Any, defecto: str = "") -> str:
        h = _texto(valor, defecto)
        m = re.match(r"^@(landing|diagnostico|reserva|gracias|webinar)((?:[?#].*)?)$", h)
        if m:
            tipo, resto = m.group(1), m.group(2)
            if tipo not in self.paginas:
                self.avisos.append(f"Enlace a @{tipo}, pero esa página no está en el config. Si la generas aparte, pon "
                                   "su URL o ruta relativa (p. ej. «../gracias/») en el campo que enlaza "
                                   "(formulario.siguiente, cta.href…)")
                return "#"
            publica = _texto((self.paginas[tipo] or {}).get("ruta_publica"))
            return (publica or self.archivos[tipo]) + resto
        if re.match(r"^\s*(javascript|data|vbscript):", h, re.I):
            raise ErrorUsuario(f"Enlace no permitido: {h[:40]}")
        return h

    def cta(self, valor: Any, defecto_href: str = "") -> dict | None:
        if not isinstance(valor, dict) or not _texto(valor.get("texto")):
            return None
        return {"texto": _texto(valor["texto"]), "href": self.href(valor.get("href"), defecto_href) or "#"}

    def marca(self) -> dict:
        if self._marca is None:
            cliente, ruta = self._marca_args
            conf = self.cfg.get("marca") or {}
            if not cliente and not ruta:
                cliente = _texto(conf.get("cliente")) or None
                if conf.get("ruta"):
                    ruta = str((self.base / conf["ruta"]).resolve())
            self._marca = render.cargar_marca(cliente, ruta)
            self.avisos.extend(self._marca["_avisos"])
        return self._marca

    def _validar_tracking(self) -> None:
        t = self.tracking
        pixel = _texto(t.get("pixel_id"))
        if pixel and not re.fullmatch(r"\d{10,20}", pixel):
            raise ErrorUsuario(f"tracking.pixel_id={pixel!r} no parece un ID de píxel (solo dígitos)")
        if not pixel:
            self.avisos.append("Sin tracking.pixel_id: no habrá eventos del navegador (solo los que mande tu servidor)")
        wh = t.get("webhook") or {}
        url = _texto(wh.get("url"))
        if url and not url.startswith("https://"):
            raise ErrorUsuario("tracking.webhook.url debe empezar por https://")
        if not url:
            self.avisos.append("Sin tracking.webhook.url: las páginas quedan en modo prueba (no envían nada y lo dicen)")
        if _texto(wh.get("modo"), "json") not in ("json", "texto"):
            raise ErrorUsuario("tracking.webhook.modo debe ser «json» o «texto»")
        base = _texto(t.get("base_legal_servidor"), "consentimiento")
        if base not in ("consentimiento", "interes_legitimo"):
            raise ErrorUsuario("tracking.base_legal_servidor debe ser «consentimiento» o «interes_legitimo»")
        if base == "interes_legitimo":
            self.avisos.append("base_legal_servidor=interes_legitimo: fbc y event_id viajan al servidor sin consentimiento. "
                               "Valídalo con tu asesor legal; en la UE lo habitual es pedir consentimiento [CONTESTED]")
        cons = t.get("consentimiento") or {}
        if self.necesita_consentimiento() and cons.get("banner") is False:
            self.avisos.append("Banner de consentimiento desactivado: tu gestor de cookies debe llamar a "
                               "PaginasOS.consentimiento('si'|'no'); si no, ni se carga el píxel ni el servidor puede "
                               "mandar nada a Meta (enviar_a_meta sale siempre false)")

    def medicion(self) -> tuple[bool, bool]:
        """(navegador, servidor): ¿hay píxel con eventos del navegador? ¿Manda el webhook datos para la CAPI que
        necesitan el «Aceptar» (base_legal_servidor = consentimiento)?"""
        t = self.tracking
        navegador = bool(_texto(t.get("pixel_id"))) and t.get("eventos_navegador", True) is not False
        servidor = bool(_texto((t.get("webhook") or {}).get("url"))) \
            and _texto(t.get("base_legal_servidor"), "consentimiento") == "consentimiento"
        return navegador, servidor

    def necesita_consentimiento(self) -> bool:
        """El banner está en todos los modos en que hay algo que pedir, también en «solo servidor» (hallazgo 6)."""
        return any(self.medicion())

    def consentimiento_visible(self) -> bool:
        return self.necesita_consentimiento() \
            and (self.tracking.get("consentimiento") or {}).get("banner", True) is not False

    # — archivos —
    def copiar(self, valor: Any, carpeta: str = "img") -> tuple[str, pathlib.Path | None]:
        """Copia un archivo local (relativo al config) a recursos/<carpeta>/ y devuelve (src, archivo)."""
        v = _texto(valor)
        if not v:
            return "", None
        if re.match(r"^https?://", v):
            return v, None
        origen = (self.base / v).resolve() if not pathlib.Path(v).is_absolute() else pathlib.Path(v)
        if not origen.is_file():
            raise ErrorUsuario(f"No encuentro el archivo {v} (las rutas son relativas al config)")
        clave = str(origen)
        if clave in self._copiados:
            return self._copiados[clave], origen
        nombre = _slug(origen.stem) + origen.suffix.lower()
        src = f"recursos/{carpeta}/{nombre}"
        if self.recursos is not None:
            destino = self.recursos / carpeta / nombre
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origen, destino)
        self._copiados[clave] = src
        return src, origen

    def imagen(self, conf: Any, donde: str, alt_obligatorio: bool = True) -> dict | None:
        if not conf:
            return None
        if isinstance(conf, str):
            conf = {"src": conf}
        src, archivo = self.copiar(conf.get("src"))
        if not src:
            return None
        alt = _texto(conf.get("alt"))
        if alt_obligatorio and "alt" not in conf:
            raise ErrorUsuario(f"{donde}: falta «alt» (texto alternativo; pon \"\" si la imagen es decorativa)")
        dims = dimensiones_imagen(archivo) if archivo else None
        ancho = conf.get("ancho") or (dims[0] if dims else None)
        alto = conf.get("alto") or (dims[1] if dims else None)
        if not ancho or not alto:
            self.avisos.append(f"{donde}: no sé el tamaño de la imagen; pon «ancho» y «alto» para evitar saltos (CLS)")
        if archivo and archivo.stat().st_size > PESO_IMAGEN_AVISO:
            self.avisos.append(f"{donde}: {archivo.name} pesa {archivo.stat().st_size // 1024} KB; "
                               "comprímela (WebP o AVIF, ≤ 200 KB) para móvil")
        return {"src": src, "alt": alt, "ancho": str(ancho or ""), "alto": str(alto or "")}

    def video(self, conf: Any, donde: str, carga: str = "lazy") -> dict | None:
        if not isinstance(conf, dict) or not conf:
            return None
        proveedor = _texto(conf.get("proveedor"), "youtube")
        if proveedor not in ("youtube", "vimeo", "mp4"):
            raise ErrorUsuario(f"{donde}.proveedor debe ser youtube, vimeo o mp4")
        vid, src = _texto(conf.get("id")), ""
        if proveedor == "youtube" and not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", vid):
            raise ErrorUsuario(f"{donde}.id: pon el ID del vídeo de YouTube (lo que va tras v=)")
        if proveedor == "vimeo" and not re.fullmatch(r"\d{4,15}", vid):
            raise ErrorUsuario(f"{donde}.id: pon el ID numérico del vídeo de Vimeo")
        subtitulos = ""
        if proveedor == "mp4":
            src, _ = self.copiar(conf.get("src"), "video")
            if not src:
                raise ErrorUsuario(f"{donde}.src: falta el archivo .mp4")
            subtitulos, _ = self.copiar(conf.get("subtitulos"), "video")
            if not subtitulos:
                self.avisos.append(f"{donde}: vídeo sin subtítulos (.vtt); la mayoría lo verá sin sonido")
        titulo = _texto(conf.get("titulo"), "Vídeo")
        mini = self.imagen({"src": conf.get("miniatura"), "alt": ""}, f"{donde}.miniatura", False) \
            if conf.get("miniatura") else None
        if not mini:
            self.avisos.append(f"{donde}: sin miniatura propia (no la pedimos a YouTube/Vimeo para no cargar terceros "
                               "antes de que la persona pulse)")
        return {"proveedor": proveedor, "id": vid, "src": src, "subtitulos": subtitulos, "titulo": titulo,
                "duracion": _texto(conf.get("duracion")), "vertical": bool(conf.get("vertical")),
                "miniatura": mini["src"] if mini else "", "miniatura_ancho": mini["ancho"] if mini else "",
                "miniatura_alto": mini["alto"] if mini else "", "carga": carga}

    # — formularios —
    CAMPOS = {
        "nombre": {"tipo": "texto", "etiqueta": "Nombre", "autocomplete": "given-name", "requerido": True, "media": True},
        "apellidos": {"tipo": "texto", "etiqueta": "Apellidos", "autocomplete": "family-name", "requerido": False,
                      "media": True},
        "email": {"tipo": "email", "etiqueta": "Email de trabajo", "autocomplete": "email", "requerido": True},
        "telefono": {"tipo": "tel", "etiqueta": "Teléfono", "autocomplete": "tel", "requerido": True, "media": True,
                     "ayuda": ""},
        "empresa": {"tipo": "texto", "etiqueta": "Empresa", "autocomplete": "organization", "requerido": True,
                    "media": True},
        "cargo": {"tipo": "texto", "etiqueta": "Cargo", "autocomplete": "organization-title", "requerido": False,
                  "media": True},
        "web": {"tipo": "url", "etiqueta": "Web de la empresa", "autocomplete": "url", "requerido": False},
        "mensaje": {"tipo": "textarea", "etiqueta": "¿Qué te gustaría resolver?", "requerido": False, "maxlength": 1000},
    }

    def formulario(self, conf: Any, donde: str, defecto: dict) -> dict:
        conf = dict(defecto, **(conf or {}))
        fid = _texto(conf.get("id"), "lead")
        if not _ID.match(fid):
            raise ErrorUsuario(f"{donde}.id={fid!r}: usa minúsculas, números y _")
        dom = _texto(conf.get("ancla"), fid)
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,40}", dom):
            raise ErrorUsuario(f"{donde}.ancla={dom!r}: usa minúsculas, números, - y _")
        campos_conf = conf.get("campos") or ["nombre", "email", "telefono"]
        campos = []
        nombres = set()
        for i, c in enumerate(campos_conf):
            if isinstance(c, str):
                if c not in self.CAMPOS:
                    raise ErrorUsuario(f"{donde}.campos: «{c}» no es un campo predefinido ({', '.join(self.CAMPOS)}); "
                                       "descríbelo como objeto {id, tipo, etiqueta}")
                c = dict(self.CAMPOS[c], id=c)
            elif isinstance(c, dict):
                base = self.CAMPOS.get(_texto(c.get("id")), {})
                c = dict(base, **c)
            else:
                raise ErrorUsuario(f"{donde}.campos[{i}] no es válido")
            cid = _texto(c.get("id"))
            if cid in CLAVES_ENVIO:
                raise ErrorUsuario(f"{donde}.campos[{i}].id={cid!r} está reservado: es una clave del envío al webhook "
                                   "(origen, momento, ref, ad_id, utm_*, event_id…) y la pisaría. Usa otro id, p. ej. "
                                   "«como_nos_conociste» o «recomendado_por»")
            if not _ID.match(cid) or cid in nombres or cid.startswith("acepta_"):
                raise ErrorUsuario(f"{donde}.campos[{i}].id={cid!r} no es válido, está repetido o empieza por acepta_ "
                                   "(reservado a las casillas de comunicaciones: usa «marketing»)")
            nombres.add(cid)
            tipo = _texto(c.get("tipo"), "texto")
            if tipo not in ("texto", "email", "tel", "url", "numero", "select", "textarea", "casilla"):
                raise ErrorUsuario(f"{donde}.campos[{i}].tipo={tipo!r} no es válido")
            if cid == "nombre" and "apellidos" not in [x if isinstance(x, str) else x.get("id") for x in campos_conf]:
                c.setdefault("autocomplete", "name")
                if c.get("autocomplete") == "given-name":
                    c["autocomplete"] = "name"
            opciones = []
            if tipo == "select":
                for o in c.get("opciones") or []:
                    texto = _texto(o if isinstance(o, str) else o.get("texto"))
                    valor = _texto(o if isinstance(o, str) else o.get("valor", texto))
                    opciones.append({"texto": texto, "valor": valor})
                if len(opciones) < 2:
                    raise ErrorUsuario(f"{donde}.campos[{i}]: un select necesita al menos 2 opciones")
            html_tipo = {"texto": "text", "email": "email", "tel": "tel", "url": "url", "numero": "text"}.get(tipo, "text")
            campos.append({
                "id": cid, "nombre": cid, "dom_id": f"{dom}-{cid}", "etiqueta": _texto(c.get("etiqueta"), cid.capitalize()),
                "requerido": bool(c.get("requerido", False)), "ayuda": _texto(c.get("ayuda")),
                "placeholder": _texto(c.get("placeholder")), "autocomplete": _texto(c.get("autocomplete")),
                "inputmode": {"email": "email", "tel": "tel", "url": "url", "numero": "decimal"}.get(tipo, ""),
                "sin_corrector": tipo in ("email", "url"), "maxlength": str(c.get("maxlength") or ""),
                "tipo_html": html_tipo, "validacion": {"email": "email", "tel": "tel", "numero": "numero"}.get(tipo, "texto"),
                "es_input": tipo in ("texto", "email", "tel", "url", "numero"), "es_select": tipo == "select",
                "es_textarea": tipo == "textarea", "es_casilla": tipo == "casilla", "opciones": opciones,
                "media": bool(c.get("media", False)) and tipo not in ("textarea", "casilla"),
            })
        if "email" not in nombres and "telefono" not in nombres:
            raise ErrorUsuario(f"{donde}: el formulario necesita email o teléfono (los usa el CRM para crear el contacto)")
        filas, i = [], 0
        while i < len(campos):
            if campos[i]["media"] and i + 1 < len(campos) and campos[i + 1]["media"]:
                filas.append({"doble": True, "campos": campos[i:i + 2]})
                i += 2
            else:
                filas.append({"doble": False, "campos": [campos[i]]})
                i += 1
        legal = self.sitio.get("legal") or {}
        responsable = _texto(legal.get("responsable"))
        if not responsable:
            self.avisos.append(f"{donde}: falta sitio.legal.responsable (la información básica de protección de datos "
                               "debe decir quién trata los datos)")
        finalidad = _texto(legal.get("finalidad"), "responder a tu solicitud y, si reservas, preparar la llamada")
        legal_txt = _texto(conf.get("legal")) or (
            f"Responsable: {responsable or self.sitio.get('nombre') or 'tu empresa'}. Finalidad: {finalidad}. "
            "Legitimación: tu solicitud y, si marcas la casilla, tu consentimiento para recibir comunicaciones. "
            "Destinatarios: proveedores que nos dan servicio (CRM, calendario y correo) con contrato de encargo. "
            "Derechos: acceso, rectificación, supresión y otros.")
        # Casillas de comunicaciones: opcionales, sin marcar y una por canal (email, WhatsApp…), nunca condición
        # para enviar el formulario. true = la de email por defecto; texto = esa casilla con otro texto; lista = varias.
        marketing = conf.get("marketing", True)
        if marketing is True:
            marketing = (f"Quiero recibir por email ideas y novedades de {self.sitio.get('nombre') or 'la empresa'}. "
                         "Puedo darme de baja cuando quiera.")
        if isinstance(marketing, str):
            marketing = [{"id": "acepta_comunicaciones", "texto": marketing}] if marketing.strip() else []
        if not isinstance(marketing, list):
            marketing = []
        consentimientos = []
        for j, m in enumerate(marketing):
            mid = _texto(m.get("id") if isinstance(m, dict) else "")
            texto = _texto(m.get("texto") if isinstance(m, dict) else "")
            if not re.fullmatch(r"acepta_[a-z0-9_]{2,30}", mid) or mid in [x["nombre"] for x in consentimientos] \
                    or not texto:
                raise ErrorUsuario(f"{donde}.marketing[{j}]: cada casilla lleva id «acepta_<canal>» (único) y texto, "
                                   "p. ej. {\"id\": \"acepta_whatsapp\", \"texto\": \"Quiero los recordatorios por "
                                   "WhatsApp\"}")
            consentimientos.append({"nombre": mid, "dom_id": f"{dom}-{mid.replace('_', '-')}", "texto": texto,
                                    "etiqueta_corta": mid.removeprefix("acepta_").replace("_", " ").capitalize()})
        evento = _texto(conf.get("evento"), "Lead")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{1,49}", evento):
            raise ErrorUsuario(f"{donde}.evento={evento!r} no es un nombre de evento válido")
        return {
            "id": fid, "dom_id": dom, "evento": evento,
            "tipo_envio": _texto(conf.get("tipo_envio"), "lead"), "siguiente": self.href(conf.get("siguiente")),
            "alternativa": _texto(self.sitio.get("contacto")), "titulo": _texto(conf.get("titulo")),
            "texto": _texto(conf.get("texto")), "filas": filas, "boton": _texto(conf.get("boton"), "Enviar"),
            "mensaje_ok": _texto(conf.get("mensaje_ok"), "Recibido. Te llevamos al siguiente paso…"),
            "consentimientos": consentimientos, "legal": legal_txt,
            "privacidad": self.href(legal.get("privacidad")), "plano": bool(conf.get("plano", False)),
        }

    # — secciones de landing y webinar —
    TIPOS_SECCION = ("dolor", "lista", "pasos", "beneficios", "casos", "logos", "para_quien", "oferta", "ponentes",
                     "video", "texto", "faq", "formulario", "cierre")

    def secciones(self, lista: Any, donde: str, form_defecto: dict, reservadas: tuple[str, ...] = ()) -> list[dict]:
        # ids que ya usa la plantilla (y el formulario del hero en el webinar): una sección no puede repetirlos
        out, anclas = [], {"contenido", "pos", "pos-titular", "pos-config", *reservadas}
        for i, s in enumerate(lista or []):
            if not isinstance(s, dict):
                raise ErrorUsuario(f"{donde}[{i}] debe ser un objeto")
            tipo = _texto(s.get("tipo"))
            if tipo not in self.TIPOS_SECCION:
                raise ErrorUsuario(f"{donde}[{i}].tipo={tipo!r}: usa {', '.join(self.TIPOS_SECCION)}")
            ancla = _texto(s.get("id")) or ("registro" if tipo == "formulario" else f"{tipo.replace('_', '-')}")
            base_ancla, n = ancla, 2
            while ancla in anclas:
                ancla = f"{base_ancla}-{n}"
                n += 1
            anclas.add(ancla)
            d = f"{donde}[{i}]"
            sec = {k: False for k in (f"es_{t}" for t in self.TIPOS_SECCION)}
            sec.update({
                f"es_{tipo}": True, "ancla": ancla, "titulo": _texto(s.get("titulo")),
                "entradilla": _texto(s.get("entradilla")), "oscura": bool(s.get("oscura", tipo == "cierre")),
                "oculta_barra": tipo in ("formulario", "cierre"), "puntos": [_texto(x) for x in s.get("puntos") or []],
                "pasos": [{"titulo": _texto(p.get("titulo")), "texto": _texto(p.get("texto"))} for p in s.get("pasos") or []],
                "tarjetas": [{"titulo": _texto(p.get("titulo")), "texto": _texto(p.get("texto"))}
                             for p in s.get("tarjetas") or []],
                "columnas": "2" if int(s.get("columnas") or 3) == 2 else "3", "casos": [], "varios": False,
                "aviso": "", "logos": [], "titulo_si": _texto(s.get("titulo_si"), "Es para ti si…"),
                "titulo_no": _texto(s.get("titulo_no"), "No es para ti si…"),
                "si": [_texto(x) for x in s.get("si") or []], "no": [_texto(x) for x in s.get("no") or []],
                "incluye_titulo": _texto(s.get("incluye_titulo")), "incluye": [_texto(x) for x in s.get("incluye") or []],
                "precio": _texto(s.get("precio")), "precio_nota": _texto(s.get("precio_nota")),
                "garantia": _texto(s.get("garantia")), "cta": self.cta(s.get("cta")),
                "no_incluye_titulo": _texto(s.get("no_incluye_titulo"), "Lo que no incluye"),
                "no_incluye": [_texto(x) for x in s.get("no_incluye") or []], "ponentes": [], "video": None,
                "parrafos": [_texto(x) for x in s.get("parrafos") or []],
                "preguntas": [{"pregunta": _texto(p.get("pregunta")), "respuesta": _texto(p.get("respuesta"))}
                              for p in s.get("preguntas") or []],
                "formulario": None, "texto": _texto(s.get("texto")), "ejemplo": bool(s.get("ejemplo")),
            })
            sec["cabecera_visible"] = tipo not in ("formulario", "cierre") and bool(sec["titulo"] or sec["entradilla"])
            if tipo == "casos":
                casos = []
                for c in s.get("casos") or []:
                    casos.append({"cifra": _texto(c.get("cifra")), "cifra_texto": _texto(c.get("cifra_texto")),
                                  "cita": _texto(c.get("cita")), "autor": _texto(c.get("autor")),
                                  "cargo": _texto(c.get("cargo"))})
                if not casos:
                    raise ErrorUsuario(f"{d}: la sección de casos no tiene casos")
                sec["casos"], sec["varios"] = casos, len(casos) > 1
                sec["aviso"] = _texto(s.get("aviso"))
                if sec["ejemplo"]:
                    sec["aviso"] = sec["aviso"] or ("Caso ilustrativo de ejemplo: sustitúyelo por uno real, con permiso "
                                                    "del cliente, antes de publicar.")
                    self.avisos.append(f"{d}: casos de EJEMPLO. No publiques prueba inventada: `validar` lo marcará "
                                       "como error hasta que pongas casos reales y quites «ejemplo»")
            if tipo == "logos":
                sec["logos"] = [x for x in (self.imagen(x, f"{d}.logos[{j}]") for j, x in enumerate(s.get("logos") or []))
                                if x]
                if not sec["logos"]:
                    raise ErrorUsuario(f"{d}: la sección de logos no tiene logos")
            if tipo == "ponentes":
                for j, p in enumerate(s.get("ponentes") or []):
                    foto = self.imagen({"src": p.get("foto"), "alt": ""}, f"{d}.ponentes[{j}].foto", False) \
                        if p.get("foto") else None
                    sec["ponentes"].append({"nombre": _texto(p.get("nombre")), "cargo": _texto(p.get("cargo")),
                                            "bio": _texto(p.get("bio")), "foto": foto["src"] if foto else "",
                                            "foto_ancho": foto["ancho"] if foto else "",
                                            "foto_alto": foto["alto"] if foto else ""})
            if tipo == "video":
                sec["video"] = self.video(s.get("video"), f"{d}.video")
                if not sec["video"]:
                    raise ErrorUsuario(f"{d}: falta «video»")
            if tipo == "formulario":
                sec["formulario"] = self.formulario(s.get("formulario"), f"{d}.formulario",
                                                    dict(form_defecto, ancla=f"{ancla}-form"))
            out.append(sec)
        return out

    # ════════════════════════════ diagnóstico ════════════════════════════
    def diagnostico(self, pag: dict) -> tuple[dict, dict]:
        """Devuelve (contexto para la plantilla, config para diagnostico.js). Valida todo antes."""
        d = "paginas.diagnostico"
        preguntas = pag.get("preguntas") or []
        if not preguntas:
            raise ErrorUsuario(f"{d}.preguntas está vacío")
        ids: set[str] = set()
        grupos: dict[str, set[str]] = {}
        js_preguntas, ctx_preguntas = [], []

        def nuevo_id(valor, donde):
            v = _texto(valor)
            if not _ID.match(v) or v in FUNCIONES or v in PALABRAS:
                raise ErrorUsuario(f"{donde}.id={v!r}: usa minúsculas, números y _ (y que no sea una función)")
            if v in ids:
                raise ErrorUsuario(f"{donde}.id={v!r} está repetido")
            ids.add(v)
            return v

        def campo_js(c, donde, en_grupo=False):
            tipo = _texto(c.get("tipo"), "opciones")
            permitidos = ("opciones", "numero", "texto") if en_grupo else ("opciones", "numero", "texto", "grupo")
            if tipo not in permitidos:
                raise ErrorUsuario(f"{donde}.tipo={tipo!r}: usa {', '.join(permitidos)}")
            out = {"id": c["id"], "tipo": tipo, "requerido": bool(c.get("requerido", tipo != "texto")),
                   "corta": _texto(c.get("corta")) or _texto(c.get("etiqueta")) or c["id"]}
            if tipo == "opciones":
                ops = c.get("opciones") or []
                if len(ops) < 2:
                    raise ErrorUsuario(f"{donde}: necesita al menos 2 opciones")
                out["opciones"] = []
                for j, o in enumerate(ops):
                    if not isinstance(o, dict) or not _texto(o.get("etiqueta")):
                        raise ErrorUsuario(f"{donde}.opciones[{j}]: cada opción lleva «etiqueta» y «valor»")
                    valor = o.get("valor", j)
                    if not isinstance(valor, (int, float, str)) or isinstance(valor, bool):
                        raise ErrorUsuario(f"{donde}.opciones[{j}].valor debe ser un número o un texto")
                    out["opciones"].append({"etiqueta": _texto(o["etiqueta"]), "valor": valor})
            if tipo == "numero":
                for k in ("min", "max", "paso", "defecto"):
                    if c.get(k) is not None and num_humano(c.get(k)) is None:
                        raise ErrorUsuario(f"{donde}.{k} debe ser un número")
                out["min"] = num_humano(c.get("min"))
                out["max"] = num_humano(c.get("max"))
                if out["min"] is not None and out["max"] is not None and out["min"] > out["max"]:
                    raise ErrorUsuario(f"{donde}: min es mayor que max")
                out = {k: v for k, v in out.items() if v is not None}
            return out

        def campo_ctx(c, dom_base, nombre, dentro, pid):
            tipo = _texto(c.get("tipo"), "opciones")
            paso = num_humano(c.get("paso")) or 1
            defecto = c.get("defecto")
            return {
                "es_opciones": tipo == "opciones", "es_numero": tipo == "numero", "es_texto": tipo == "texto",
                "dentro_grupo": dentro, "etiqueta": _texto(c.get("etiqueta")), "dom_id": dom_base, "campo": c["id"],
                "nombre": nombre, "dos_columnas": int(c.get("columnas") or 1) == 2,
                "opciones": [{"etiqueta": _texto(o["etiqueta"]), "indice": str(j), "dom_id": f"{dom_base}-o{j}",
                              "nombre": nombre, "campo": c["id"], "marcada": False}
                             for j, o in enumerate(c.get("opciones") or [])],
                "min": "" if c.get("min") is None else _num_es(num_humano(c["min"])),
                "max": "" if c.get("max") is None else _num_es(num_humano(c["max"])),
                "paso": _num_es(paso), "paso_texto": _num_es(paso),
                "defecto": "" if defecto is None else _num_es(num_humano(defecto) or 0),
                "valor_inicial": "" if defecto is None else _num_es(num_humano(defecto) or 0),
                "unidad": _texto(c.get("unidad")), "placeholder": _texto(c.get("placeholder")),
                "maxlength": str(int(c.get("maxlength") or 120)), "labelledby": "" if dentro else f"q-{pid}",
            }

        num_grupos = 0
        for i, p in enumerate(preguntas):
            dp = f"{d}.preguntas[{i}]"
            if not isinstance(p, dict):
                raise ErrorUsuario(f"{dp} debe ser un objeto")
            pid = nuevo_id(p.get("id"), dp)
            if not _texto(p.get("pregunta")):
                raise ErrorUsuario(f"{dp}: falta «pregunta»")
            p = dict(p, id=pid)
            js = campo_js(p, dp)
            ctx = {"id": pid, "pregunta": _texto(p["pregunta"]), "ayuda": _texto(p.get("ayuda")),
                   "es_grupo": js["tipo"] == "grupo", "items": [], "plantilla": None, "texto_anadir": ""}
            if js["tipo"] == "grupo":
                num_grupos += 1
                campos = p.get("campos") or []
                if not campos:
                    raise ErrorUsuario(f"{dp}: un grupo necesita «campos»")
                campo_ids: set[str] = set()
                js["campos"] = []
                for j, c in enumerate(campos):
                    cid = _texto(c.get("id"))
                    if not _ID.match(cid) or cid in campo_ids or cid in FUNCIONES or cid in PALABRAS:
                        raise ErrorUsuario(f"{dp}.campos[{j}].id={cid!r} no es válido, está repetido o es una palabra "
                                           "reservada de las fórmulas (y, o, no, min, max…)")
                    if not _texto(c.get("etiqueta")):
                        raise ErrorUsuario(f"{dp}.campos[{j}]: falta «etiqueta»")
                    campo_ids.add(cid)
                    js["campos"].append(campo_js(dict(c, id=cid), f"{dp}.campos[{j}]", True))
                grupos[pid] = campo_ids
                etiqueta_item = _texto(p.get("etiqueta_item"), "Elemento")
                js["etiqueta_item"] = etiqueta_item
                js["min_items"] = max(1, int(p.get("min_items") or 1))
                js["max_items"] = max(js["min_items"], int(p.get("max_items") or 5))
                inicial = min(max(int(p.get("inicial") or js["min_items"]), js["min_items"]), js["max_items"])

                def item(clave, numero, p=p, pid=pid, etiqueta_item=etiqueta_item):
                    return {"numero": str(numero), "etiqueta_item": etiqueta_item,
                            "etiqueta_item_min": etiqueta_item.lower(),
                            "campos": [campo_ctx(dict(c, id=c["id"]), f"q-{pid}-{clave}-{c['id']}",
                                                 f"p_{pid}_{clave}_{c['id']}", True, pid) for c in p["campos"]]}
                ctx["items"] = [item(str(k + 1), k + 1) for k in range(inicial)]
                ctx["plantilla"] = item("__i__", "__i__")
                ctx["texto_anadir"] = _texto(p.get("texto_anadir"), f"Añadir otro ({etiqueta_item.lower()})")
                for k in ("es_opciones", "es_numero", "es_texto", "dentro_grupo"):
                    ctx[k] = False
            else:
                ctx.update(campo_ctx(p, f"q-{pid}-campo", f"p_{pid}", False, pid))
            js_preguntas.append(js)
            ctx_preguntas.append(ctx)
        if len(preguntas) > 8:
            self.avisos.append(f"{d}: {len(preguntas)} preguntas; cada una de más baja la tasa de finalización "
                               "(apunta a 4–7) [HYPOTHESIS]")

        # supuestos
        js_sup, ctx_sup = [], []
        for i, s in enumerate(pag.get("supuestos") or []):
            ds = f"{d}.supuestos[{i}]"
            sid = nuevo_id(s.get("id"), ds)
            valor = num_humano(s.get("valor"))
            if valor is None:
                raise ErrorUsuario(f"{ds}.valor debe ser un número (p. ej. 9000 o «9.000»)")
            formato = _texto(s.get("formato"), "numero")
            if formato not in ("numero", "eur", "moneda", "horas", "pct", "meses"):
                raise ErrorUsuario(f"{ds}.formato={formato!r}: usa numero, eur, horas, pct o meses")
            etiqueta = _texto(s.get("etiqueta"))
            if not etiqueta:
                raise ErrorUsuario(f"{ds}: falta «etiqueta» (los supuestos se enseñan)")
            unidad = _texto(s.get("unidad"))
            if "€" in unidad and self.moneda != "EUR":
                self.avisos.append(f"{ds}.unidad «{unidad}» está en euros, pero la moneda es {self.moneda}: cámbiala")
            simbolo = SIMBOLO_MONEDA.get(self.moneda, self.moneda)
            sufijo = " (%)" if formato == "pct" else (f" ({unidad})" if unidad else
                                                      (f" ({simbolo})" if formato in ("eur", "moneda") else ""))
            explicacion = _texto(s.get("explicacion"))
            if s.get("fuente"):
                explicacion = (explicacion + " " if explicacion else "") + f"Fuente: {_texto(s['fuente'])}."
            if not explicacion:
                self.avisos.append(f"{ds}: sin «explicacion»; di de dónde sale el valor para que el cálculo sea creíble")
            js_sup.append({"id": sid, "valor": valor, "formato": formato, "unidad": unidad})
            if s.get("visible", True) is not False:
                ctx_sup.append({"id": sid, "etiqueta_campo": etiqueta + sufijo, "editable": s.get("editable", True) is not False,
                                "valor_texto": _num_es(valor * 100 if formato == "pct" else valor),
                                "explicacion": explicacion})
        # cálculos
        conocidas = set(ids)
        js_calc, defs = [], {}
        for i, c in enumerate(pag.get("calculos") or []):
            dc = f"{d}.calculos[{i}]"
            cid = nuevo_id(c.get("id"), dc)
            formula = _texto(c.get("formula"))
            try:
                comprobar_formula(formula, conocidas - set(grupos), grupos)
            except ErrorExpresion as e:
                raise ErrorUsuario(f"{dc}.formula «{formula}»: {e}") from None
            formato = _texto(c.get("formato"), "numero")
            if formato not in ("numero", "eur", "moneda", "horas", "pct", "meses", "texto"):
                raise ErrorUsuario(f"{dc}.formato={formato!r} no es válido")
            redondeo = num_humano(c.get("redondeo"))
            entrada = {"id": cid, "formula": formula, "formato": formato, "unidad": _texto(c.get("unidad"))}
            if redondeo:
                entrada["redondeo"] = redondeo
            js_calc.append(entrada)
            defs[cid] = dict(entrada, etiqueta=_texto(c.get("etiqueta"), cid), explicacion=_texto(c.get("explicacion")),
                             mostrar=c.get("mostrar", True) is not False)
            conocidas.add(cid)
        if not js_calc:
            raise ErrorUsuario(f"{d}.calculos está vacío: el diagnóstico tiene que calcular algo")
        # resultado
        res = pag.get("resultado") or {}
        principal = _texto(res.get("principal"), js_calc[-1]["id"])
        if principal not in defs:
            raise ErrorUsuario(f"{d}.resultado.principal={principal!r} no es un cálculo")
        incertidumbre = num_humano(res.get("incertidumbre"))
        if incertidumbre is not None and not 0 <= incertidumbre < 1:
            raise ErrorUsuario(f"{d}.resultado.incertidumbre va de 0 a 0,9 (p. ej. 0.25 = ±25 %)")
        desglose_ids = res.get("desglose") or [k for k, v in defs.items() if v["mostrar"] and k != principal]
        for k in desglose_ids:
            if k not in defs:
                raise ErrorUsuario(f"{d}.resultado.desglose: «{k}» no es un cálculo")
        explicaciones = [{"etiqueta": defs[k]["etiqueta"], "explicacion": defs[k]["explicacion"]}
                         for k in [principal] + list(desglose_ids) if defs[k]["explicacion"]]
        if not defs[principal]["explicacion"]:
            self.avisos.append(f"{d}: el cálculo principal no tiene «explicacion»; enséñala para que el resultado sea creíble")
        # niveles (recomendación honesta)
        niveles = pag.get("niveles") or []
        if not niveles:
            raise ErrorUsuario(f"{d}.niveles está vacío: define al menos la recomendación por defecto")
        js_niv, nivel_ids = [], []
        valores_texto = set(defs) | {s["id"] for s in js_sup}
        for i, n in enumerate(niveles):
            dn = f"{d}.niveles[{i}]"
            nid = _texto(n.get("id"))
            if not _ID.match(nid) or nid in nivel_ids:
                raise ErrorUsuario(f"{dn}.id={nid!r} no es válido o está repetido")
            nivel_ids.append(nid)
            si = _texto(n.get("si"))
            if si:
                try:
                    comprobar_formula(si, conocidas - set(grupos), grupos)
                except ErrorExpresion as e:
                    raise ErrorUsuario(f"{dn}.si «{si}»: {e}") from None
            elif i < len(niveles) - 1:
                self.avisos.append(f"{dn}: sin «si» y no es el último: los niveles siguientes nunca se usarán")
            tono = _texto(n.get("tono"), "medio")
            if tono not in ("bajo", "medio", "alto"):
                raise ErrorUsuario(f"{dn}.tono debe ser bajo, medio o alto")
            if not _texto(n.get("titulo")) or not _texto(n.get("texto")):
                raise ErrorUsuario(f"{dn}: cada nivel lleva «titulo» y «texto»")
            for marcador in re.findall(r"\{([a-z_][a-z0-9_]*)\}", _texto(n.get("titulo")) + _texto(n.get("texto"))):
                base_m = re.sub(r"_(min|max)$", "", marcador)
                if marcador not in valores_texto and base_m not in valores_texto:
                    self.avisos.append(f"{dn}: «{{{marcador}}}» no es un cálculo ni un supuesto; se verá tal cual")
            js_niv.append({"id": nid, "si": si, "tono": tono, "titulo": _texto(n["titulo"]), "texto": _texto(n["texto"]),
                           "cta": self.cta(n.get("cta")), "cta_secundario": self.cta(n.get("cta_secundario"))})
        if niveles[-1].get("si"):
            self.avisos.append(f"{d}: el último nivel tiene «si»; si no se cumple ninguno se usará igualmente el último")
        if not any(n["tono"] == "bajo" for n in js_niv):
            self.avisos.append(f"{d}: ningún nivel tiene tono «bajo». Un diagnóstico honesto dice también "
                               "«hoy no te compensa» cuando los números no salen")
        valor_evento = {}
        for k, v in (pag.get("valor_evento") or {}).items():
            if k not in nivel_ids:
                raise ErrorUsuario(f"{d}.valor_evento: «{k}» no es un nivel")
            if num_humano(v) is None or num_humano(v) < 0:
                raise ErrorUsuario(f"{d}.valor_evento.{k} debe ser un número ≥ 0 (en {self.moneda}, p. ej. 1200 o "
                                   "«1.200»)")
            valor_evento[k] = num_humano(v)
        if valor_evento:
            self.avisos.append(f"{d}: valor_evento es el valor ESPERADO del lead por nivel [HYPOTHESIS] (nunca el ahorro "
                               "del cliente). Recalcúlalo con /economia cuando tengas datos de cierre")
        cual = pag.get("cualificado") or {}
        if cual.get("activo"):
            for k in cual.get("niveles") or []:
                if k not in nivel_ids:
                    raise ErrorUsuario(f"{d}.cualificado.niveles: «{k}» no es un nivel")
            self.avisos.append(f"{d}: LeadCualificado automático por nivel. Lo normal es que lo marque el comercial en el "
                               "CRM (contrato §16); úsalo solo si las reglas de la ficha lo permiten")
        captura = _texto(pag.get("captura"), "antes")
        if captura not in ("antes", "despues"):
            raise ErrorUsuario(f"{d}.captura debe ser «antes» (datos antes del resultado) o «despues»")
        js_cfg = {"captura": captura, "preguntas": js_preguntas, "supuestos": js_sup, "calculos": js_calc,
                  "resultado": {"principal": principal, "incertidumbre": incertidumbre or 0},
                  "niveles": js_niv, "valor_evento": valor_evento,
                  "cualificado": {"activo": bool(cual.get("activo")), "niveles": list(cual.get("niveles") or [])}}
        # prueba de humo y escenarios
        try:
            calcular(js_cfg, respuestas_por_defecto(js_cfg))
        except ErrorExpresion as e:
            raise ErrorUsuario(f"{d}: el cálculo falla con respuestas de prueba: {e}") from None
        for j, esc in enumerate(pag.get("escenarios") or []):
            try:
                r = calcular(js_cfg, esc.get("respuestas") or {}, esc.get("supuestos"))
            except ErrorExpresion as e:
                raise ErrorUsuario(f"{d}.escenarios[{j}]: {e}") from None
            if esc.get("espera_nivel") and r["nivel"] != esc["espera_nivel"]:
                self.avisos.append(f"{d}.escenarios[{j}] «{esc.get('nombre', j)}»: sale «{r['nivel']}» y esperabas "
                                   f"«{esc['espera_nivel']}». Revisa umbrales con `probar`")
        intro = pag.get("intro", {})
        n_preg = len(preguntas)
        minutos = max(2, round(n_preg / 2) + num_grupos)
        formulario = self.formulario(pag.get("formulario"), f"{d}.formulario", {
            "id": "diagnostico", "ancla": "pos-contacto-form", "tipo_envio": "diagnostico",
            "titulo": "¿A dónde te enviamos el resultado?" if captura == "antes" else "Revisemos tu resultado juntos",
            "texto": "Tu resultado aparece en cuanto envíes. También te lo mandamos por email." if captura == "antes"
            else "Déjanos tus datos y elige hueco para la llamada.",
            "boton": "Ver mi resultado" if captura == "antes" else "Continuar a la reserva",
            "siguiente": "" if captura == "antes" else ("@reserva" if "reserva" in self.paginas else ""),
            "campos": ["nombre", "email", "empresa", "telefono"],
            "mensaje_ok": "Listo. Aquí tienes tu resultado." if captura == "antes" else "Recibido. Abrimos tu reserva…"})
        resultado = {
            "etiqueta": _texto(res.get("etiqueta"), defs[principal]["etiqueta"]),
            "desglose": [{"id": k, "etiqueta": defs[k]["etiqueta"]} for k in desglose_ids],
            "aviso": _texto(res.get("aviso"), "Es una estimación con tus respuestas y los supuestos de arriba, no una "
                                              "promesa de resultados. Lo comprobamos contigo antes de proponerte nada."),
            "titulo_supuestos": _texto(res.get("titulo_supuestos"),
                                       "Cómo lo calculamos (cambia los supuestos si no encajan contigo)"),
            "supuestos_abiertos": bool(res.get("supuestos_abiertos", False)),
        }
        if PROMESAS.search(json.dumps(pag, ensure_ascii=False)):
            self.avisos.append(f"{d}: hay frases de promesa (garantizado, ahorrarás, 100 %…). Pásalo por "
                               "revisor-politicas antes de publicar")
        ctx = {
            "nombre": _texto(pag.get("nombre"), "Diagnóstico"),
            "intro": None if intro is False else {
                "titulo": _texto((intro or {}).get("titulo"), _texto(pag.get("nombre"), "Diagnóstico gratuito")),
                "entradilla": _texto((intro or {}).get("entradilla")),
                "promesas": [_texto(x) for x in (intro or {}).get("promesas") or []],
                "boton": _texto((intro or {}).get("boton"), "Empezar el diagnóstico"),
                "duracion": _texto((intro or {}).get("duracion"),
                                   f"Son {n_preg} preguntas y tardas unos {minutos} minutos."),
                "nota": _texto((intro or {}).get("nota")), "alternativa": _texto(self.sitio.get("contacto")),
            },
            "num_preguntas": str(n_preg), "pasos_totales": str(n_preg + (1 if captura == "antes" else 0)),
            "preguntas": ctx_preguntas, "captura_antes": captura == "antes", "captura_despues": captura == "despues",
            "formulario": formulario, "resultado": resultado, "supuestos_visibles": ctx_sup,
            "explicaciones": explicaciones,
        }
        return ctx, js_cfg

    # ════════════════════════════ páginas ════════════════════════════
    def contexto(self, tipo: str) -> tuple[dict, dict]:
        pag = self.paginas[tipo]
        marca = self.marca()
        nombre = _texto(self.sitio.get("nombre")) or marca.get("nombre") or "Tu marca"
        legal = self.sitio.get("legal") or {}
        logo = {"src": "", "ancho": "", "alto": ""}
        logo_ruta = render._resolver_archivo(_texto((marca.get("logo") or {}).get("principal")), marca.get("_dir"))
        if logo_ruta is not None:
            destino = f"recursos/logo{logo_ruta.suffix.lower()}"
            if self.recursos is not None:
                self.recursos.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(logo_ruta, self.salida / destino)
            dims = dimensiones_imagen(logo_ruta) or (160, 40)
            logo = {"src": destino, "ancho": str(dims[0]), "alto": str(dims[1])}
        favicon = "data:,"
        if self.sitio.get("favicon"):
            favicon, _ = self.copiar(self.sitio["favicon"])
        url_base = _texto(self.sitio.get("url")).rstrip("/")
        if url_base and not url_base.startswith("https://"):
            raise ErrorUsuario("sitio.url debe empezar por https://")
        publica = _texto(pag.get("ruta_publica")) or self.archivos[tipo]
        url_pagina = ""
        if url_base:
            url_pagina = url_base + "/" + ("" if publica == "index.html" else publica.lstrip("/"))
        og = ""
        if pag.get("og_imagen"):
            src, _ = self.copiar(pag["og_imagen"])
            og = src if src.startswith("https://") else (f"{url_base}/{src}" if url_base else "")
            if not og:
                self.avisos.append(f"paginas.{tipo}.og_imagen necesita sitio.url para ser una URL absoluta")
        enlaces = [{"texto": t, "href": self.href(legal.get(k))} for k, t in
                   (("aviso_legal", "Aviso legal"), ("privacidad", "Privacidad"), ("cookies", "Cookies")) if legal.get(k)]
        if not legal.get("privacidad"):
            self.avisos.append("Falta sitio.legal.privacidad (enlace a la política de privacidad)")
        cons_cfg = self.tracking.get("consentimiento") or {}
        navegador, servidor = self.medicion()
        cierre_banner = "Puedes cambiarlo cuando quieras en «Preferencias de cookies»."
        if navegador and servidor:
            texto_banner = ("Si aceptas, usamos el píxel de Meta y, desde nuestro servidor, enviamos a Meta qué anuncio "
                            "te trajo y, protegidos con hash, tu email y tu teléfono, para saber qué anuncios funcionan "
                            "y mostrarte anuncios más útiles. Sin tu permiso no se activa nada. " + cierre_banner)
        elif navegador:
            texto_banner = ("Usamos el píxel de Meta para saber qué anuncios funcionan y mostrarte anuncios más útiles. "
                            "Solo se activa si aceptas, y puedes cambiarlo cuando quieras en «Preferencias de "
                            "cookies».")
        else:  # solo servidor: no hay píxel, pero el envío a la CAPI necesita el mismo permiso
            texto_banner = ("Si aceptas, desde nuestro servidor enviamos a Meta qué anuncio te trajo y, protegidos con "
                            "hash, tu email y tu teléfono, para saber qué anuncios funcionan y mostrarte anuncios más "
                            "útiles. Sin tu permiso no le enviamos nada. " + cierre_banner)
        inicio = "#contenido"
        if "landing" in self.paginas and tipo != "landing":
            inicio = self.href("@landing")
        elif url_base:
            inicio = url_base + "/"
        hero_cfg = pag.get("hero") or {}
        intro_cfg = pag.get("intro") if isinstance(pag.get("intro"), dict) else {}
        titular = _texto(hero_cfg.get("titular")) or _texto(pag.get("titulo")) or _texto(intro_cfg.get("titulo")) \
            or _texto(pag.get("nombre"))
        ctx: dict[str, Any] = {
            "tipo": tipo, **{f"es_{t}": t == tipo for t in TIPOS},
            "meta": {"idioma": _texto(self.sitio.get("idioma"), "es"),
                     "titulo": _texto(pag.get("titulo_seo")) or (f"{titular} | {nombre}" if titular else nombre),
                     "descripcion": _texto(pag.get("descripcion_seo")),
                     "noindex": bool(pag.get("noindex", tipo in ("gracias", "reserva"))),
                     "url": url_pagina, "og_imagen": og, "favicon": favicon,
                     "color_tema": marca["colores"]["fondo"]},
            "sitio": {"nombre": nombre, "inicio": inicio, "logo": logo["src"], "logo_ancho": logo["ancho"],
                      "logo_alto": logo["alto"]},
            "cabecera": {"cta": None},
            "pie": {"texto": f"© {dt.date.today().year} {_texto(legal.get('responsable')) or nombre}", "enlaces": enlaces},
            "barra": None,
            "consentimiento": {
                "mostrar": self.consentimiento_visible(),
                "titulo": _texto(cons_cfg.get("titulo"), "Cookies de medición" if navegador else "Medición de anuncios"),
                "texto": _texto(cons_cfg.get("texto"), texto_banner),
                "politica": self.href(legal.get("cookies")),
                "aceptar": _texto(cons_cfg.get("aceptar"), "Aceptar"),
                "rechazar": _texto(cons_cfg.get("rechazar"), "Rechazar"),
            },
        }
        pagina_js: dict[str, Any] = {}
        if tipo in ("landing", "webinar"):
            hero = {"titular": _texto(hero_cfg.get("titular")), "entradilla": _texto(hero_cfg.get("entradilla")),
                    "prueba": _texto(hero_cfg.get("prueba")), "imagen": None, "video": None, "arranque": None,
                    "cta": self.cta(hero_cfg.get("cta")), "cta_secundario": self.cta(hero_cfg.get("cta_secundario"))}
            if not hero["titular"]:
                raise ErrorUsuario(f"paginas.{tipo}.hero.titular es obligatorio")
            media = hero_cfg.get("media") or {}
            tipo_media = _texto(media.get("tipo"))
            if tipo_media == "imagen":
                hero["imagen"] = self.imagen(media, f"paginas.{tipo}.hero.media")
            elif tipo_media == "video":
                hero["video"] = self.video(media.get("video") or media, f"paginas.{tipo}.hero.media", "eager")
            elif tipo_media == "arranque":
                if tipo != "landing" or "diagnostico" not in self.paginas:
                    raise ErrorUsuario("hero.media.tipo=arranque necesita una página de diagnóstico en el config")
                diag_ctx, diag_js = self.diagnostico(self.paginas["diagnostico"])
                primera = diag_js["preguntas"][0]
                if primera["tipo"] != "opciones":
                    raise ErrorUsuario("Para el arranque en la landing, la primera pregunta del diagnóstico debe ser de "
                                       "opciones")
                href = self.href("@diagnostico")
                sep = "&" if "?" in href else "?"
                hero["arranque"] = {"pregunta": diag_ctx["preguntas"][0]["pregunta"],
                                    "ayuda": _texto(media.get("ayuda")),
                                    "opciones": [{"etiqueta": o["etiqueta"], "href": f"{href}{sep}r_{primera['id']}={j}"}
                                                 for j, o in enumerate(primera["opciones"])],
                                    "pie": _texto(media.get("pie"), "Es la primera pregunta del diagnóstico. "
                                                                    "Sin compromiso y sin registrarte para empezar.")}
            elif tipo_media:
                raise ErrorUsuario(f"paginas.{tipo}.hero.media.tipo: usa imagen, video o arranque")
            hero["con_media"] = bool(hero["imagen"] or hero["video"] or hero["arranque"])
            form_defecto = {"id": "lead", "boton": "Quiero mi plaza" if tipo == "webinar" else "Enviar",
                            "tipo_envio": "registro_webinar" if tipo == "webinar" else "lead",
                            "evento": "CompleteRegistration" if tipo == "webinar" else "Lead",
                            "siguiente": "@gracias" if tipo == "webinar" else
                            ("@reserva" if "reserva" in self.paginas else "@gracias" if "gracias" in self.paginas else "")}
            ctx["hero"] = hero
            ctx["secciones"] = self.secciones(pag.get("secciones"), f"paginas.{tipo}.secciones", form_defecto,
                                              ("registro",) if tipo == "webinar" else ())
            barra = pag.get("barra_cta", True)
            if barra is True and hero["cta"]:
                ctx["barra"] = dict(hero["cta"])
            elif isinstance(barra, dict):
                ctx["barra"] = self.cta(barra)
            if pag.get("cabecera_cta", True) and hero["cta"]:
                ctx["cabecera"]["cta"] = dict(hero["cta"])
            if PROMESAS.search(json.dumps(pag, ensure_ascii=False)):
                self.avisos.append(f"paginas.{tipo}: hay frases de promesa (garantizado, ahorrarás, 100 %…). Pásalo "
                                   "por revisor-politicas antes de publicar")
            if tipo == "webinar":
                ev = pag.get("evento") or {}
                info = self.evento_webinar(ev, "paginas.webinar.evento")
                form = self.formulario(pag.get("formulario"), "paginas.webinar.formulario",
                                       dict(form_defecto, id="registro", ancla="registro", evento="CompleteRegistration",
                                            titulo="Reserva tu plaza", campos=["nombre", "email", "empresa"],
                                            boton="Quiero mi plaza", mensaje_ok="Plaza reservada. Te llevamos a la "
                                                                               "confirmación…"))
                ctx["webinar"] = {"evento": info, "formulario": form}
                hero["con_media"] = True
                if not ctx["barra"] and pag.get("barra_cta", True) is not False:
                    ctx["barra"] = {"texto": form["boton"], "href": "#" + form["dom_id"]}
        elif tipo == "diagnostico":
            diag_ctx, diag_js = self.diagnostico(pag)
            ctx["diag"] = diag_ctx
            pagina_js["diagnostico"] = diag_js
        elif tipo == "reserva":
            cal = pag.get("calendario") or {}
            proveedor = _texto(cal.get("proveedor"), "ghl")
            if proveedor not in ("ghl", "calendly", "calcom", "otro"):
                raise ErrorUsuario("paginas.reserva.calendario.proveedor: usa ghl, calendly, calcom u otro")
            url = _texto(cal.get("url"))
            if url and not url.startswith("https://"):
                raise ErrorUsuario("paginas.reserva.calendario.url debe empezar por https://")
            if not url:
                self.avisos.append("paginas.reserva: sin calendario.url (la página enseña un aviso de modo prueba)")
            parametros = cal.get("parametros") or {
                "ghl": {"nombre": "first_name", "apellidos": "last_name", "email": "email", "telefono": "phone"},
                "calendly": {"nombre": "name", "email": "email"},
                "calcom": {"nombre": "name", "email": "email"}}.get(proveedor, {})
            origen = _texto(cal.get("origen"), "https://calendly.com" if proveedor == "calendly" else "")
            alto = _texto(cal.get("alto"), "46rem")
            if not re.fullmatch(r"\d{2,4}(?:\.\d+)?(?:rem|px)", alto):
                raise ErrorUsuario("paginas.reserva.calendario.alto: usa p. ej. «46rem» o «760px»")
            evento_schedule = _texto(pag.get("evento_schedule"), "navegador" if proveedor == "calendly" else "servidor")
            if evento_schedule not in ("navegador", "servidor"):
                raise ErrorUsuario("paginas.reserva.evento_schedule: usa «navegador» o «servidor»")
            if evento_schedule == "navegador" and proveedor != "calendly":
                self.avisos.append("evento_schedule=navegador solo se detecta con Calendly (mensaje del iframe). Con GHL, "
                                   "manda Schedule desde el workflow «cita reservada» o desde la página de gracias")
            mensajes = [{"nivel": k, "texto": _texto(v)} for k, v in (pag.get("mensajes_nivel") or {}).items()]
            # Embudo «Captación → VSL con calendario»: el vídeo va arriba, el calendario justo debajo y el resto
            # (puntos, anfitrión, nota) después. Mismas claves que el vídeo del hero y nada de terceros hasta pulsar.
            video = self.video(pag.get("video"), "paginas.reserva.video", "eager")
            if pag.get("video") is not None and not video:
                raise ErrorUsuario("paginas.reserva.video: pon el vídeo como en el hero, p. ej. "
                                   "{\"proveedor\": \"youtube\", \"id\": \"…\", \"miniatura\": \"…\"}")
            anfitrion = None
            if isinstance(pag.get("anfitrion"), dict):
                a = pag["anfitrion"]
                foto = self.imagen({"src": a.get("foto"), "alt": ""}, "paginas.reserva.anfitrion.foto", False) \
                    if a.get("foto") else None
                anfitrion = {"nombre": _texto(a.get("nombre")), "cargo": _texto(a.get("cargo")),
                             "foto": foto["src"] if foto else "", "foto_ancho": foto["ancho"] if foto else "",
                             "foto_alto": foto["alto"] if foto else "",
                             "carga": "lazy" if video else ""}  # con vídeo, la foto queda debajo del calendario
            texto_calendario = _texto(pag.get("texto_calendario"), "Elige día y hora para la llamada" if video else "")
            titulo_defecto = "Antes de elegir hora, mira este vídeo" if video else "Elige día y hora para la llamada"
            ctx["reserva"] = {"titulo": _texto(pag.get("titulo"), titulo_defecto),
                              "entradilla": _texto(pag.get("entradilla")), "mensajes_nivel": mensajes,
                              "puntos_titulo": _texto(pag.get("puntos_titulo"), "En la llamada"),
                              "puntos": [_texto(x) for x in pag.get("puntos") or []], "anfitrion": anfitrion,
                              "nota": _texto(pag.get("nota")), "alto": alto, "calendario_url": url,
                              "video": video, "texto_calendario": texto_calendario}
            pagina_js.update({"calendario": {"proveedor": proveedor, "url": url, "origen": origen,
                                             "titulo": _texto(cal.get("titulo"), "Calendario de reservas"),
                                             "parametros": parametros, "prefill": cal.get("prefill", True) is not False},
                              "evento_schedule": evento_schedule,
                              "notificar_webhook": bool(pag.get("notificar_webhook", False)),
                              "siguiente": self.href(pag.get("siguiente"), "@gracias" if "gracias" in self.paginas else "")})
        elif tipo == "gracias":
            evento = _texto(pag.get("evento"))
            if evento and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{1,49}", evento):
                raise ErrorUsuario("paginas.gracias.evento no es un nombre de evento válido")
            if evento == "Lead":
                self.avisos.append("paginas.gracias.evento=Lead: el Lead ya lo dispara el formulario con su event_id; "
                                   "repetirlo aquí lo duplicaría")
            info = None
            cal = pag.get("anadir_calendario")
            if isinstance(cal, dict):  # gracias generada con su propio config (carpeta aparte del registro)
                info = self.evento_webinar(cal, "paginas.gracias.anadir_calendario", ics=True)
            elif cal:
                if "webinar" not in self.paginas:
                    raise ErrorUsuario("paginas.gracias.anadir_calendario=true necesita paginas.webinar.evento en el "
                                       "mismo config; si generas gracias aparte, pon aquí los datos del evento "
                                       "(titulo, inicio, duracion_min…)")
                info = self.evento_webinar((self.paginas["webinar"] or {}).get("evento") or {},
                                           "paginas.webinar.evento", ics=True)
            botones = [b for b in (self.cta(x) for x in (pag.get("botones") or [])) if b]
            for b in botones:
                b["whatsapp"] = bool(re.match(r"^https://(wa\.me|api\.whatsapp\.com)/", b["href"]))
            ctx["gracias"] = {"titulo": _texto(pag.get("titulo"), "Hecho. Ya lo tenemos."),
                              "texto": _texto(pag.get("texto")),
                              "pasos_titulo": _texto(pag.get("pasos_titulo"), "Qué pasa ahora"),
                              "pasos": [{"titulo": _texto(p.get("titulo")), "texto": _texto(p.get("texto"))}
                                        for p in pag.get("pasos") or []],
                              "video": self.video(pag.get("video"), "paginas.gracias.video"),
                              "recurso": self.cta(pag.get("recurso")), "botones": botones, "evento_webinar": info}
            pagina_js.update({"evento": evento, "notificar_webhook": bool(pag.get("notificar_webhook", False))})
        wh = self.tracking.get("webhook") or {}
        cfg_js = {
            "v": 1, "tipo": tipo, "pixel_id": _texto(self.tracking.get("pixel_id")),
            "eventos_navegador": self.tracking.get("eventos_navegador", True) is not False,
            "webhook": {"url": _texto(wh.get("url")), "modo": _texto(wh.get("modo"), "json"),
                        "timeout_ms": int(wh.get("timeout_ms") or 8000)},
            "base_legal_servidor": _texto(self.tracking.get("base_legal_servidor"), "consentimiento"),
            "consentimiento": {"banner": ctx["consentimiento"]["mostrar"],
                               "externo": self.necesita_consentimiento() and cons_cfg.get("banner") is False,
                               "caducidad_dias": int(cons_cfg.get("caducidad_dias") or 180)},
            "moneda": self.moneda, "prefill_reserva": self.tracking.get("prefill_reserva", True) is not False,
            # p. ej. la edición de un webinar: va en custom_data de cada evento y en el envío, para separar en Meta
            "content_name": (_texto(pag.get("content_name")) or _texto(self.tracking.get("content_name")))[:100],
            "pagina": pagina_js,
        }
        return ctx, cfg_js

    def _zona(self, clave: str, donde: str) -> zoneinfo.ZoneInfo:
        try:
            return zoneinfo.ZoneInfo(clave)
        except (zoneinfo.ZoneInfoNotFoundError, ValueError):
            raise ErrorUsuario(f"{donde}={clave!r}: usa un nombre IANA como «Europe/Madrid» o «America/Mexico_City» "
                               "(si tu sistema no trae la base de zonas, instala el paquete tzdata)") from None

    def _inicio_webinar(self, ev: dict, donde: str) -> tuple[dt.datetime, str]:
        """Inicio en la hora de su zona y la etiqueta. La zona: evento.zona_horaria (IANA); si no, la de la ficha (con
        --cliente) o Europe/Madrid con la etiqueta por defecto. Sin desfase en `inicio`, se calcula para esa fecha;
        con desfase, tiene que ser el de la zona en esa fecha (hallazgo 25: el horario de verano escrito a mano)."""
        texto = _texto(ev.get("inicio"))
        try:
            inicio = dt.datetime.fromisoformat(texto)
        except ValueError:
            raise ErrorUsuario(f"{donde}.inicio: usa fecha y hora ISO, p. ej. 2026-12-03T18:00:00 (la zona sale de "
                               "evento.zona_horaria) o 2026-12-03T18:00:00+01:00") from None
        etiqueta = _texto(ev.get("zona"))
        clave = _texto(ev.get("zona_horaria"))
        if clave:
            zona = self._zona(clave, f"{donde}.zona_horaria")
        elif etiqueta and etiqueta != ETIQUETA_ZONA[ZONA_DEFECTO]:
            zona = None  # etiqueta propia sin zona IANA: no se puede contrastar
        elif self.zona_ficha and not etiqueta:
            zona = self._zona(self.zona_ficha, "zona_horaria de la ficha")
        else:
            zona = zoneinfo.ZoneInfo(ZONA_DEFECTO)
        if zona is None:
            if inicio.tzinfo is None:
                raise ErrorUsuario(f"{donde}: con la etiqueta «{etiqueta}» y sin desfase en inicio no sé a qué hora es: "
                                   "añade evento.zona_horaria (p. ej. «America/Bogota»)")
            self.avisos.append(f"{donde}: con la etiqueta «{etiqueta}» y sin evento.zona_horaria no puedo comprobar que "
                               "el desfase de inicio sea el de esa fecha (horario de verano). Pon zona_horaria con su "
                               "nombre IANA")
            return inicio, etiqueta
        if inicio.tzinfo is None:
            local = inicio.replace(tzinfo=zona)
            if local.astimezone(dt.timezone.utc).astimezone(zona).replace(tzinfo=None) != inicio:
                raise ErrorUsuario(f"{donde}.inicio={texto}: esa hora no existe en {zona.key} (es la del cambio al "
                                   "horario de verano); elige otra")
        else:
            esperado = inicio.replace(tzinfo=zona).utcoffset()
            if inicio.utcoffset() != esperado:
                verano = " (horario de verano)" if inicio.replace(tzinfo=zona).dst() else ""
                raise ErrorUsuario(
                    f"{donde}.inicio={texto}: en {zona.key}, el {inicio.date().isoformat()} el desfase es "
                    f"{_desfase(esperado)}{verano}, no {_desfase(inicio.utcoffset())}. Escribe "
                    f"{inicio.replace(tzinfo=None).isoformat()}{_desfase(esperado)} o quita el desfase y se calcula solo")
            local = inicio.astimezone(zona)
        if not etiqueta:
            etiqueta = ETIQUETA_ZONA.get(zona.key) or "Hora de " + zona.key.split("/")[-1].replace("_", " ")
        return local, etiqueta

    def evento_webinar(self, ev: dict, donde: str, ics: bool = False) -> dict:
        inicio, etiqueta = self._inicio_webinar(ev, donde)
        titulo = _texto(ev.get("titulo"))
        if not titulo:
            raise ErrorUsuario(f"{donde}.titulo es obligatorio")
        minutos = int(ev.get("duracion_min") or 60)
        fin = inicio.astimezone(dt.timezone.utc) + dt.timedelta(minutes=minutos)  # en UTC: sin saltos de hora
        horas, resto = divmod(minutos, 60)
        duracion = (f"{horas} h" if horas else "") + (f" {resto} min" if resto else "")
        info = {"dia": str(inicio.day), "mes": f"{MESES[inicio.month - 1]} {inicio.year}",
                "dia_semana": DIAS[inicio.weekday()].capitalize(), "hora": inicio.strftime("%H:%M") + " h",
                "zona": etiqueta, "duracion": duracion.strip(),
                "plataforma": _texto(ev.get("plataforma")), "inicio_iso": inicio.isoformat(), "ics": "", "google": "",
                "otras_zonas": []}
        # Varios mercados: la hora de cada país, calculada con su zona IANA (con su horario de verano).
        for j, z in enumerate(ev.get("otras_zonas") or []):
            z = z if isinstance(z, dict) else {}
            clave = _texto(z.get("zona"))
            local = inicio.astimezone(self._zona(clave, f"{donde}.otras_zonas[{j}].zona"))
            otro_dia = "" if local.date() == inicio.date() else f" del {DIAS[local.weekday()]} {local.day}"
            info["otras_zonas"].append({"pais": _texto(z.get("nombre"), clave),
                                        "hora_local": local.strftime("%H:%M") + " h" + otro_dia})
        if ics:
            utc = "%Y%m%dT%H%M%SZ"
            a, b = inicio.astimezone(dt.timezone.utc), fin.astimezone(dt.timezone.utc)
            detalle = _texto(ev.get("descripcion"))
            lugar = _texto(ev.get("enlace")) or info["plataforma"]
            nombre_ics = _slug(titulo) + ".ics"
            if self.recursos is not None:
                self.recursos.mkdir(parents=True, exist_ok=True)
                (self.recursos / nombre_ics).write_bytes(_ics(titulo, detalle, lugar, a, b).encode("utf-8"))
            info["ics"] = f"recursos/{nombre_ics}"
            info["google"] = ("https://calendar.google.com/calendar/render?action=TEMPLATE&"
                              + urllib.parse.urlencode({"text": titulo, "dates": f"{a.strftime(utc)}/{b.strftime(utc)}",
                                                        "details": detalle, "location": lugar}))
        return info

    # — render —
    def _expandir(self, texto: str, profundidad: int = 0) -> str:
        if profundidad > 5:
            raise ErrorUsuario("Parciales anidados demasiado profundos")

        def sustituir(m):
            nombre = m.group(1)
            ruta = PLANTILLAS / f"_{nombre}.html"
            if not ruta.is_file():
                raise ErrorUsuario(f"Falta el parcial _{nombre}.html")
            return self._expandir(ruta.read_text(encoding="utf-8"), profundidad + 1)
        return re.sub(r"\{\{>\s*([a-z0-9-]+)\s*\}\}", sustituir, texto)

    def pagina(self, tipo: str) -> tuple[str, str | None]:
        """(HTML completo, fragmento GHL o None)."""
        ctx, cfg_js = self.contexto(tipo)
        plantilla = self._expandir((PLANTILLAS / f"{tipo}.html").read_text(encoding="utf-8"))
        cuerpo, faltan = render.renderizar_texto(plantilla, ctx)
        if faltan:
            raise ErrorUsuario(f"Error interno de plantilla ({tipo}): faltan {', '.join(faltan[:5])}")
        marca = self.marca()
        caras, vars_fuente, precargas = fuentes_marca(marca, self.recursos, self.avisos)
        variables = dict(tokens_marca(marca, self.avisos), **vars_fuente)
        css_marca = caras + ":root{" + ";".join(f"{k}:{v}" for k, v in variables.items()) + "}"
        config = f'<script type="application/json" id="pos-config">{_json_script(cfg_js)}</script>'
        scripts = ["paginas.js"] + (["diagnostico.js"] if tipo == "diagnostico" else [])

        def bloque_scripts(en_linea: bool) -> str:
            partes = [config]
            for s in scripts:
                if en_linea:
                    codigo = (PLANTILLAS / s).read_text(encoding="utf-8")
                    if "</script" in codigo.lower():
                        raise ErrorUsuario(f"{s} contiene </script>: no se puede incrustar")
                    partes.append(f"<script>{codigo}</script>")
                else:
                    partes.append(f'<script src="recursos/{s}" defer></script>')
            return "\n".join(partes)

        cabeza = "".join(f'<link rel="preload" href="{p}" as="font" type="font/woff2" crossorigin>' for p in precargas)
        cabeza += f'\n<style id="pos-base">{_css_base(False)}</style>\n<style id="pos-marca">{css_marca}</style>'
        completo = cuerpo.replace("<!--pos:cabeza-->", cabeza).replace("<!--pos:scripts-->", bloque_scripts(self.en_linea))
        completo = re.sub(r"\n{3,}", "\n\n", completo)
        fragmento = None
        if self.fragmento_ghl:
            m = re.search(r"<!--pos:fragmento-->(.*)<!--/pos:fragmento-->", cuerpo, re.S)
            interior = m.group(1).replace("<!--pos:scripts-->", bloque_scripts(True))
            base_recursos = _texto(self.sitio.get("recursos_url")).rstrip("/")
            if base_recursos:
                interior = interior.replace('src="recursos/', f'src="{base_recursos}/').replace(
                    'href="recursos/', f'href="{base_recursos}/')
                css_marca = css_marca.replace("url(recursos/", f"url({base_recursos}/")
            elif "recursos/" in interior:
                self.avisos.append(f"ghl/{self.archivos[tipo]}: usa imágenes de recursos/. Súbelas a la biblioteca de "
                                   "GHL y pon sitio.recursos_url para que el fragmento las encuentre")
            fragmento = (f"<!-- {GENERADOR} · fragmento para GHL ({tipo}). Pégalo en un elemento «Custom code». -->\n"
                         f'<meta name="generator" content="{GENERADOR}"><meta name="pos-tipo" content="{tipo}">\n'
                         f'<style id="pos-base">{_css_base(True)}</style>\n<style id="pos-marca">{css_marca}</style>\n'
                         + re.sub(r"\n{3,}", "\n\n", interior.strip()) + "\n")
        return completo, fragmento

    def generar(self, tipos: list[str]) -> dict:
        assert self.salida is not None
        self.salida.mkdir(parents=True, exist_ok=True)
        escritos = []
        for tipo in tipos:
            if tipo not in self.paginas:
                raise ErrorUsuario(f"El config no tiene paginas.{tipo}")
        self.marca()
        if not self.en_linea:
            self.recursos.mkdir(parents=True, exist_ok=True)
            for s in ("paginas.js", "diagnostico.js"):
                if s == "diagnostico.js" and "diagnostico" not in tipos:
                    continue
                shutil.copyfile(PLANTILLAS / s, self.recursos / s)
                escritos.append(f"recursos/{s}")
        for tipo in tipos:
            completo, fragmento = self.pagina(tipo)
            (self.salida / self.archivos[tipo]).write_text(completo, encoding="utf-8")
            escritos.append(self.archivos[tipo])
            if fragmento:
                (self.salida / "ghl").mkdir(exist_ok=True)
                (self.salida / "ghl" / self.archivos[tipo]).write_text(fragmento, encoding="utf-8")
                escritos.append(f"ghl/{self.archivos[tipo]}")
        if self.recursos is not None and self.recursos.exists():
            escritos += sorted(str(p.relative_to(self.salida)) for p in self.recursos.rglob("*")
                               if p.is_file() and str(p.relative_to(self.salida)) not in escritos)
        return {"ok": True, "orden": "generar", "salida": _rel(self.salida), "paginas": tipos, "archivos": escritos,
                "marca": self.marca()["_origen"], "avisos": list(dict.fromkeys(self.avisos))}


def _ics(titulo: str, detalle: str, lugar: str, inicio: dt.datetime, fin: dt.datetime) -> str:
    def esc(t: str) -> str:
        return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    def plegar(linea: str) -> str:
        datos, out = linea.encode("utf-8"), []
        while len(datos) > 75:
            corte = 75
            while corte > 0 and (datos[corte] & 0xC0) == 0x80:  # no partir un carácter UTF-8
                corte -= 1
            out.append(datos[:corte].decode("utf-8"))
            datos = b" " + datos[corte:]
        out.append(datos.decode("utf-8"))
        return "\r\n".join(out)
    f = "%Y%m%dT%H%M%SZ"
    uid = hashlib.sha1(f"{titulo}{inicio.isoformat()}".encode()).hexdigest()[:16]
    lineas = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//meta-ads-os//paginas//ES", "CALSCALE:GREGORIAN",
              "METHOD:PUBLISH", "BEGIN:VEVENT", f"UID:{uid}@meta-ads-os",
              f"DTSTAMP:{dt.datetime.now(dt.timezone.utc).strftime(f)}", f"DTSTART:{inicio.strftime(f)}",
              f"DTEND:{fin.strftime(f)}", f"SUMMARY:{esc(titulo)}"]
    if detalle:
        lineas.append(f"DESCRIPTION:{esc(detalle)}")
    if lugar:
        lineas.append(f"LOCATION:{esc(lugar)}")
    lineas += ["END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(plegar(x) for x in lineas) + "\r\n"


# ════════════════════════════ probar ════════════════════════════
def probar(config: str, respuestas: str | None = None) -> dict:
    g = Generador(config, None)
    if "diagnostico" not in g.paginas:
        raise ErrorUsuario("El config no tiene paginas.diagnostico")
    _, diag = g.diagnostico(g.paginas["diagnostico"])
    casos = []
    if respuestas:
        p = pathlib.Path(respuestas)
        if not p.is_file():
            raise ErrorUsuario(f"No existe {respuestas}")
        try:
            datos = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ErrorUsuario(f"{p.name} no es un JSON válido: {e}") from None
        casos.append({"nombre": p.stem, "respuestas": datos.get("respuestas", datos), "supuestos": datos.get("supuestos"),
                      "espera_nivel": datos.get("espera_nivel")})
    else:
        casos = list(g.paginas["diagnostico"].get("escenarios") or [])
        if not casos:
            casos = [{"nombre": "respuestas por defecto", "respuestas": respuestas_por_defecto(diag)}]
    out = []
    for c in casos:
        try:
            r = calcular(diag, c.get("respuestas") or {}, c.get("supuestos"))
        except ErrorExpresion as e:
            raise ErrorUsuario(f"Escenario «{c.get('nombre')}»: {e}") from None
        esperado = c.get("espera_nivel")
        out.append({"nombre": c.get("nombre", ""), "nivel": r["nivel"], "espera_nivel": esperado,
                    "ok": (not esperado) or esperado == r["nivel"], "valores": r["valores"],
                    "valor_evento": diag["valor_evento"].get(r["nivel"])})
    return {"ok": all(x["ok"] for x in out), "orden": "probar", "principal": diag["resultado"]["principal"],
            "escenarios": out, "avisos": list(dict.fromkeys(g.avisos))}


# ════════════════════════════ validar ════════════════════════════
VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class _Analizador(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elementos: list[dict] = []
        self.pila: list[dict] = []
        self.textos: dict[int, list[str]] = {}
        self.en_template = 0

    def handle_starttag(self, tag, attrs):
        e = {"tag": tag, "attrs": {k: (v if v is not None else "") for k, v in attrs}, "linea": self.getpos()[0],
             "en_template": self.en_template > 0, "dentro": [x["tag"] for x in self.pila],
             "label_padre": next((x for x in reversed(self.pila) if x["tag"] == "label"), None), "texto": ""}
        self.elementos.append(e)
        if tag == "template":
            self.en_template += 1
        if tag == "img" and e["attrs"].get("alt"):
            for x in self.pila:
                if x["tag"] in ("a", "button"):
                    x["texto"] += " " + e["attrs"]["alt"]
        if tag not in VACIOS:
            self.pila.append(e)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VACIOS and self.pila and self.pila[-1]["tag"] == tag:
            self.pila.pop()

    def handle_endtag(self, tag):
        if tag == "template" and self.en_template:
            self.en_template -= 1
        for i in range(len(self.pila) - 1, -1, -1):
            if self.pila[i]["tag"] == tag:
                del self.pila[i:]
                break

    def handle_data(self, data):
        for x in self.pila:
            x["texto"] += data


def _problema(lista, nivel, pid, detalle, arreglo=""):
    lista.append({"nivel": nivel, "id": pid, "detalle": detalle, "arreglo": arreglo})


def _local(src: str) -> bool:
    return bool(src) and not re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", src, re.I)


def _dentro(ruta: pathlib.Path, carpeta: pathlib.Path) -> bool:
    try:
        ruta.relative_to(carpeta)
        return True
    except ValueError:
        return False


def _enlace_roto(href: str, ruta: pathlib.Path, carpeta: pathlib.Path, fragmento: bool) -> tuple[str, str] | None:
    """None si el enlace local lleva a un archivo; si no, (nivel, arreglo).

    «/diagnostico» (ruta_publica) se busca desde la raíz de la carpeta; sin .html, como lo sirven muchos hostings: x,
    x.html o x/index.html. Una carpeta («../gracias/») solo sirve si tiene index.html: sin él, el hosting da 404.
    """
    camino = urllib.parse.unquote(href.split("#")[0].split("?")[0])
    if not camino:
        return None
    base = carpeta if camino.startswith("/") else ruta.parent
    destino = (base / camino.lstrip("/")).resolve()
    if camino.endswith("/"):
        candidatos = [destino / "index.html"]
    else:
        candidatos = [destino, destino.with_name(destino.name + ".html"), destino / "index.html"]
    if any(c.is_file() for c in candidatos):
        return None
    arreglo = "Si en tu hosting la ruta es otra, ponla en ruta_publica o usa una URL absoluta"
    if destino.is_dir():
        return ("aviso" if fragmento else "error",
                f"La carpeta {camino} no tiene index.html: genera esa página con «\"archivo\": \"index.html\"» (es el "
                "nombre por defecto cuando el config solo tiene esa página)")
    # una ruta desde la raíz puede ser de otra parte del sitio; una carpeta de fuera, de otra orden que aún no has
    # generado: no se puede saber. Valida la carpeta que las contiene a las dos (p. ej. paginas/<edicion>/).
    if fragmento or camino.startswith("/"):
        return "aviso", arreglo
    if not _dentro(destino, carpeta.resolve()):
        return "aviso", ("Está fuera de la carpeta validada: valida la carpeta que contiene las dos (p. ej. "
                         "paginas/<edicion>/) o comprueba la URL al publicar")
    return "error", arreglo


def validar_html(ruta: pathlib.Path, carpeta: pathlib.Path) -> dict:
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    problemas: list[dict] = []
    an = _Analizador()
    an.feed(texto)
    els = an.elementos
    por_tag: dict[str, list[dict]] = {}
    for e in els:
        por_tag.setdefault(e["tag"], []).append(e)
    metas = {e["attrs"].get("name", "").lower(): e["attrs"].get("content", "") for e in por_tag.get("meta", [])}
    fragmento = "html" not in por_tag
    generada = metas.get("generator") == GENERADOR
    tipo = metas.get("pos-tipo", "")
    if not generada:
        _problema(problemas, "aviso", "meta.generador", "No la generó paginas.py: solo hago las comprobaciones generales")
    # documento
    if not fragmento:
        html_el = por_tag["html"][0]
        if not html_el["attrs"].get("lang"):
            _problema(problemas, "error", "doc.idioma", "Falta lang en <html>", 'Pon <html lang="es">')
        titulo = (por_tag.get("title") or [{"texto": ""}])[0]["texto"].strip()
        if not titulo:
            _problema(problemas, "error", "doc.titulo", "Falta <title>")
        vp = metas.get("viewport", "")
        if not vp:
            _problema(problemas, "error", "doc.viewport", "Falta <meta name=viewport>: en móvil se verá diminuta")
        elif re.search(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b", vp):
            _problema(problemas, "error", "doc.zoom", "El viewport bloquea el zoom (accesibilidad)",
                      "Quita user-scalable=no y maximum-scale=1")
        h1 = [e for e in por_tag.get("h1", []) if not e["en_template"]]
        if not h1:
            _problema(problemas, "error", "doc.h1", "No hay <h1>")
        elif len(h1) > 1:
            _problema(problemas, "aviso", "doc.h1", f"Hay {len(h1)} <h1>; deja uno por página")
        if not any(e["tag"] == "a" and e["attrs"].get("href", "").startswith("#") and "saltar" in e["attrs"].get("class", "")
                   for e in els):
            _problema(problemas, "aviso", "a11y.saltar", "Sin enlace «Saltar al contenido»")
    # peso
    peso_html = len(texto.encode("utf-8"))
    locales: dict[str, int] = {}
    if peso_html > PESO_HTML_AVISO:
        _problema(problemas, "aviso", "peso.html", f"El HTML pesa {peso_html // 1024} KB")
    # imágenes
    for i, e in enumerate(por_tag.get("img", [])):
        a = e["attrs"]
        src = a.get("src", "")
        if "alt" not in a:
            _problema(problemas, "error", "img.alt", f"Imagen sin alt (línea {e['linea']}): {src[:60]}",
                      'Describe la imagen o pon alt="" si es decorativa')
        if not a.get("width") or not a.get("height"):
            _problema(problemas, "error", "img.dimensiones", f"Imagen sin width/height (línea {e['linea']}): {src[:60]}",
                      "Pon el ancho y alto reales para evitar saltos de diseño (CLS)")
        if src.startswith("https://www.facebook.com/tr"):
            _problema(problemas, "error", "pixel.sin_consentimiento", "Píxel de imagen (<noscript>) que se carga sin "
                      "consentimiento", "Quítalo: el píxel solo se carga tras aceptar")
        if _local(src):
            archivo = (ruta.parent / urllib.parse.unquote(src.split("?")[0])).resolve()
            if not archivo.is_file():
                _problema(problemas, "aviso" if fragmento else "error", "img.falta", f"No existe la imagen {src}",
                          "En GHL, sube recursos/ a la biblioteca y pon sitio.recursos_url" if fragmento else "")
            else:
                tam = archivo.stat().st_size
                locales[str(archivo)] = tam
                if tam > PESO_IMAGEN_ERROR:
                    _problema(problemas, "error", "img.peso", f"{src} pesa {tam // 1024} KB", "Comprime a WebP/AVIF ≤ 200 KB")
                elif tam > PESO_IMAGEN_AVISO:
                    _problema(problemas, "aviso", "img.peso", f"{src} pesa {tam // 1024} KB", "Comprime a WebP/AVIF ≤ 200 KB")
        if i > 1 and a.get("loading") != "lazy" and not e["en_template"] and "fetchpriority" not in a:
            _problema(problemas, "aviso", "img.lazy", f"{src[:60]} sin loading=lazy (no es la primera imagen)")
    # scripts y píxel
    config: dict | None = None
    runtime = False
    for e in por_tag.get("script", []):
        a = e["attrs"]
        src = a.get("src", "")
        contenido = e["texto"]
        if a.get("id") == "pos-config":
            try:
                config = json.loads(contenido)
            except json.JSONDecodeError:
                _problema(problemas, "error", "tracking.config", "El JSON de #pos-config no es válido")
            continue
        if src:
            if re.search(r"fbevents\.js|connect\.facebook\.net", src):
                _problema(problemas, "error", "pixel.sin_consentimiento", "Se carga fbevents.js directamente (antes del "
                          "consentimiento)", "Quítalo: paginas.js carga el píxel cuando la persona acepta")
            elif _local(src):
                archivo = (ruta.parent / src.split("?")[0]).resolve()
                if not archivo.is_file():
                    _problema(problemas, "error", "js.falta", f"No existe {src}")
                else:
                    locales[str(archivo)] = archivo.stat().st_size
                    if archivo.name == "paginas.js":
                        runtime = True
            else:
                _problema(problemas, "aviso", "js.terceros", f"Script de terceros: {src[:80]}",
                          "Cada script externo ralentiza y puede cargar cookies sin consentimiento")
            if "head" in e["dentro"] and "defer" not in a and "async" not in a and a.get("type") != "module":
                _problema(problemas, "aviso", "js.bloqueante", f"{src[:60]} bloquea el renderizado", "Añade defer")
        else:
            if "PaginasOS" in contenido and "fbcDesde" in contenido:
                runtime = True
            elif re.search(r"fbq\(\s*['\"]init|fbevents\.js", contenido):
                _problema(problemas, "error", "pixel.sin_consentimiento", f"Código del píxel fuera de paginas.js "
                          f"(línea {e['linea']})", "Quítalo: el píxel lo carga paginas.js tras el consentimiento")
    # Un VSL pegado con el código de inserción de YouTube o Vimeo se descarga (con sus cookies) al abrir la página, antes
    # del consentimiento y antes de que la persona lo pida. La clave `video` (hero, sección, reserva o gracias) no.
    for e in por_tag.get("iframe", []):
        src = e["attrs"].get("src", "")
        if not e["en_template"] and VIDEO_TERCEROS.search(src):
            _problema(problemas, "aviso", "video.terceros", f"Vídeo de terceros incrustado que se carga al abrir la página "
                      f"(línea {e['linea']}): {src[:60]}", "Quita el código de inserción y usa la clave «video» del config "
                      "(proveedor e id): solo se carga cuando la persona pulsa")
    for e in por_tag.get("link", []):
        href = e["attrs"].get("href", "")
        if "stylesheet" in e["attrs"].get("rel", "") and not _local(href):
            _problema(problemas, "aviso", "css.terceros", f"Hoja de estilos externa: {href[:80]}")
        elif _local(href) and "stylesheet" in e["attrs"].get("rel", ""):
            archivo = (ruta.parent / href).resolve()
            if archivo.is_file():
                locales[str(archivo)] = archivo.stat().st_size
    if generada:
        if config is None:
            _problema(problemas, "error", "tracking.config", "Falta <script id=\"pos-config\">: sin él no hay atribución "
                      "ni envío")
        if not runtime:
            _problema(problemas, "error", "tracking.runtime", "Falta paginas.js (atribución, consentimiento y envío)")
    if config is not None:
        wh = config.get("webhook") or {}
        if not wh.get("url"):
            _problema(problemas, "aviso", "tracking.webhook", "Sin webhook: la página está en modo prueba y no envía nada",
                      "Pon tracking.webhook.url y vuelve a generar")
        elif not str(wh["url"]).startswith("https://"):
            _problema(problemas, "error", "tracking.webhook", "El webhook no usa https")
        pixel = str(config.get("pixel_id") or "")
        if not pixel:
            _problema(problemas, "aviso", "tracking.pixel", "Sin píxel: no hay eventos del navegador")
        elif not re.fullmatch(r"\d{10,20}", pixel):
            _problema(problemas, "error", "tracking.pixel", f"pixel_id no válido: {pixel[:20]}")
        # ¿Hay algo que pedir? El píxel, o el envío a la CAPI por servidor con base «consentimiento» (hallazgo 6).
        cons = config.get("consentimiento") or {}
        navegador = bool(pixel) and config.get("eventos_navegador", True) is not False
        servidor = bool(wh.get("url")) and (config.get("base_legal_servidor") or "consentimiento") == "consentimiento"
        # «externo» (banner: false en el config) lo escribe generar; en páginas anteriores, banner: false con píxel
        # también era el gestor propio. En «solo servidor», antes no había banner: eso es el fallo, no un gestor.
        externo = cons.get("externo") if "externo" in cons else (cons.get("banner", True) is False and navegador)
        tiene_banner = any("data-pos-consentimiento" in e["attrs"] for e in els)
        if (navegador or servidor) and externo:
            _problema(problemas, "aviso", "consentimiento.externo", "Banner propio desactivado: tu gestor de cookies "
                      "debe llamar a PaginasOS.consentimiento('si'|'no')")
        elif navegador and not tiene_banner:
            _problema(problemas, "error", "consentimiento.banner", "Hay píxel pero no banner de consentimiento")
        elif servidor and not tiene_banner:
            _problema(problemas, "error", "consentimiento.banner", "La página manda datos a tu servidor para la CAPI "
                      "con base_legal_servidor «consentimiento», pero no tiene banner: sin «Aceptar», enviar_a_meta "
                      "sale siempre false y el servidor no puede mandar nada a Meta",
                      "Vuelve a generarla con paginas.py (pone el banner también sin píxel)")
        pag = config.get("pagina") or {}
        if tipo == "diagnostico":
            diag = pag.get("diagnostico")
            if not diag:
                _problema(problemas, "error", "diag.config", "Falta la configuración del diagnóstico")
            else:
                try:
                    calcular(diag, respuestas_por_defecto(diag))
                except (ErrorExpresion, KeyError, TypeError) as ex:
                    _problema(problemas, "error", "diag.formulas", f"El cálculo falla: {ex}")
        if tipo == "reserva" and not (pag.get("calendario") or {}).get("url"):
            _problema(problemas, "aviso", "reserva.calendario", "Sin URL de calendario (modo prueba)")
    if tipo == "gracias" and not fragmento and "noindex" not in metas.get("robots", ""):
        _problema(problemas, "aviso", "gracias.noindex", "La página de gracias debería llevar noindex")
    # formularios y etiquetas
    ids: dict[str, int] = {}
    for e in els:
        i = e["attrs"].get("id")
        if i and not e["en_template"]:
            ids[i] = ids.get(i, 0) + 1
    for i, n in ids.items():
        if n > 1:
            _problema(problemas, "error", "a11y.ids", f"id repetido: {i}")
    etiquetas_for = {e["attrs"].get("for") for e in por_tag.get("label", [])}
    for e in els:
        if e["tag"] not in ("input", "select", "textarea"):
            continue
        a = e["attrs"]
        if a.get("type") in ("hidden", "submit", "button", "reset", "image"):
            continue
        if not (a.get("id") in etiquetas_for or a.get("aria-label") or a.get("aria-labelledby") or e["label_padre"]):
            _problema(problemas, "error", "a11y.etiquetas", f"Campo sin etiqueta (línea {e['linea']}): "
                      f"{a.get('name') or a.get('id') or e['tag']}", "Asocia un <label for> o aria-label")
        nombre = a.get("name", "")
        if "data-pos-campo" in a and nombre in CLAVES_ENVIO:
            _problema(problemas, "error", "form.reservado", f"El campo «{nombre}» (línea {e['linea']}) pisa una clave "
                      "del envío al webhook", "Cámbiale el id (p. ej. «como_nos_conociste»)")
        if nombre == "email" and a.get("type") != "email":
            _problema(problemas, "aviso", "form.email", "El campo email no es type=email (teclado y autocompletado)")
        if nombre == "telefono" and a.get("type") != "tel":
            _problema(problemas, "aviso", "form.tel", "El teléfono no es type=tel")
    for f in por_tag.get("form", []):
        a = f["attrs"]
        if "data-pos-formulario" not in a:
            if "data-pos-diag-preguntas" not in a and generada:
                _problema(problemas, "aviso", "form.sin_tracking", f"Formulario sin data-pos-formulario (línea {f['linea']})")
            continue
        if not a.get("data-evento"):
            _problema(problemas, "error", "form.evento", f"El formulario {a.get('id', '')} no dice qué evento dispara")
        dentro = [e for e in els if e["linea"] >= f["linea"] and "form" in e["dentro"]]
        if not any("pos-trampa" in e["attrs"].get("class", "") for e in dentro):
            _problema(problemas, "aviso", "form.trampa", f"El formulario {a.get('id', '')} no tiene campo trampa antispam")
    for e in els:
        if e["tag"] == "button" and not e["texto"].strip() and not e["attrs"].get("aria-label"):
            _problema(problemas, "error", "a11y.botones", f"Botón sin texto (línea {e['linea']})")
        if e["tag"] == "a" and "href" in e["attrs"] and not e["texto"].strip() and not e["attrs"].get("aria-label"):
            _problema(problemas, "error", "a11y.enlaces", f"Enlace sin texto (línea {e['linea']})")
    # enlaces: los <a href> y los destinos que solo usa el JS (hallazgo 24): el data-siguiente de los formularios, el
    # siguiente de la reserva y los CTA de los niveles del diagnóstico
    destinos: list[tuple[str, str]] = []
    for e in por_tag.get("a", []):
        href = e["attrs"].get("href", "")
        if href.startswith("#") and len(href) > 1 and href[1:] not in ids:
            _problema(problemas, "aviso", "enlaces.ancla", f"El ancla {href} no existe en la página")
        else:
            destinos.append((href, f"enlace de la línea {e['linea']}"))
    for f in por_tag.get("form", []):
        destinos.append((f["attrs"].get("data-siguiente", ""), f"siguiente del formulario {f['attrs'].get('id', '')}"))
    pag_cfg = (config or {}).get("pagina") or {}
    destinos.append((str(pag_cfg.get("siguiente") or ""), "siguiente de la reserva"))
    for n in ((pag_cfg.get("diagnostico") or {}).get("niveles") or []):
        for clave in ("cta", "cta_secundario"):
            if isinstance(n.get(clave), dict):
                destinos.append((str(n[clave].get("href") or ""), f"{clave} del nivel {n.get('id', '')}"))
    vistos: set[str] = set()
    for href, donde in destinos:
        if not _local(href) or href.startswith("#") or href in vistos:
            continue
        vistos.add(href)
        roto = _enlace_roto(href, ruta, carpeta, fragmento)
        if roto:
            _problema(problemas, roto[0], "enlaces.rotos", f"Enlace a {href[:60]}, que no existe en la carpeta ({donde})",
                      roto[1])
    # contenido de ejemplo
    if re.search(r"Caso ilustrativo de ejemplo", texto):
        _problema(problemas, "error", "contenido.ejemplo", "Hay casos de EJEMPLO: no publiques prueba inventada",
                  "Pon casos reales con permiso y quita «ejemplo» de la sección")
    # contraste de la marca
    m = re.search(r'<style id="pos-marca">(.*?)</style>', texto, re.S)
    if m:
        v = dict(re.findall(r"(--c-[a-z-]+):(#[0-9a-fA-F]{3,6})", m.group(1)))
        for a_, b_, que in (("--c-texto", "--c-fondo", "texto sobre fondo"),
                            ("--c-sobre-primario", "--c-primario", "texto de los botones")):
            if a_ in v and b_ in v and render.contraste(v[a_], v[b_]) < 4.5:
                _problema(problemas, "error", "a11y.contraste", f"Contraste {que}: {render.contraste(v[a_], v[b_])}:1 "
                          "(mínimo 4,5:1)")
    total = peso_html + sum(locales.values())
    if total > PESO_TOTAL_ERROR:
        _problema(problemas, "error", "peso.total", f"La página pesa {total // 1024} KB en total")
    elif total > PESO_TOTAL_AVISO:
        _problema(problemas, "aviso", "peso.total", f"La página pesa {total // 1024} KB en total",
                  "Comprime imágenes; en el navegador de Instagram cada KB cuenta")
    return {"archivo": str(ruta.relative_to(carpeta)), "tipo": tipo or ("fragmento" if fragmento else ""),
            "generada": generada, "peso_kb": round(total / 1024, 1),
            "errores": sum(1 for p in problemas if p["nivel"] == "error"),
            "avisos": sum(1 for p in problemas if p["nivel"] == "aviso"), "problemas": problemas}


def validar(carpeta: str) -> dict:
    c = pathlib.Path(carpeta)
    if not c.is_dir():
        raise ErrorUsuario(f"No existe la carpeta {carpeta}")
    archivos = sorted(p for p in c.rglob("*.html") if "recursos" not in p.relative_to(c).parts)
    if not archivos:
        raise ErrorUsuario(f"No hay archivos .html en {carpeta}")
    paginas = [validar_html(p, c) for p in archivos]
    return {"ok": all(p["errores"] == 0 for p in paginas), "orden": "validar", "carpeta": _rel(c),
            "errores": sum(p["errores"] for p in paginas), "avisos": sum(p["avisos"] for p in paginas),
            "paginas": paginas}


# ════════════════════════════ CLI ════════════════════════════
def _imprimir(res: dict, como_json: bool) -> None:
    if como_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    if res["orden"] == "generar":
        print(f"Marca: {res['marca']}. Carpeta: {res['salida']}")
        for a in res["archivos"]:
            print(f"  ✓ {a}")
        if res["avisos"]:
            print("Avisos:")
            for a in res["avisos"]:
                print(f"  ! {a}")
        print("Siguiente: python3 -I herramientas/paginas.py validar " + res["salida"])
    elif res["orden"] == "validar":
        for p in res["paginas"]:
            estado = "✓" if p["errores"] == 0 else "✗"
            print(f"{estado} {p['archivo']} ({p['tipo'] or 'html'}, {p['peso_kb']} KB): "
                  f"{p['errores']} errores, {p['avisos']} avisos")
            for x in p["problemas"]:
                marca = "  ✗" if x["nivel"] == "error" else "  !"
                print(f"{marca} [{x['id']}] {x['detalle']}" + (f" → {x['arreglo']}" if x["arreglo"] else ""))
        print(f"Total: {res['errores']} errores y {res['avisos']} avisos.")
    else:
        print(f"Resultado principal: {res['principal']}")
        def valor(v):
            if v is None:
                return "—"
            return _num_es(v, 2) if isinstance(v, float) else str(v)
        for e in res["escenarios"]:
            estado = "✓" if e["ok"] else "✗"
            espera = f" (esperado: {e['espera_nivel']})" if e["espera_nivel"] else ""
            ve = f", valor del evento {valor(e['valor_evento'])}" if e.get("valor_evento") is not None else ""
            vals = "; ".join(f"{k} = {valor(v)}" for k, v in e["valores"].items())
            print(f"{estado} {e['nombre']}: nivel {e['nivel']}{espera}{ve}. {vals}")
        for a in res["avisos"]:
            print(f"  ! {a}")


def _error(msg: str, codigo: int, como_json: bool) -> None:
    if como_json:
        print(json.dumps({"ok": False, "codigo": codigo, "error": msg}, ensure_ascii=False, indent=2))
    else:
        print(f"Error: {msg}", file=sys.stderr)


def _consola_segura() -> None:
    """✓, ✗ y → no existen en cp1252 (Git Bash en Windows con la salida redirigida): salen como «?» (hallazgo 28)."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            try:
                flujo.reconfigure(errors="replace")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    _consola_segura()
    ap = argparse.ArgumentParser(prog="paginas.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="orden", required=True)
    g = sub.add_parser("generar", help="genera páginas estáticas")
    g.add_argument("tipo", choices=list(TIPOS) + ["todas"])
    g.add_argument("--config", required=True)
    g.add_argument("--salida", required=True)
    g.add_argument("--cliente", help="slug: usa clientes/<slug>/marca/marca.json")
    g.add_argument("--marca", help="marca.json o su carpeta (prevalece sobre --cliente)")
    g.add_argument("--en-linea", action="store_true", help="JS dentro de cada HTML")
    g.add_argument("--fragmento-ghl", action="store_true", help="además, fragmentos para «Custom code» de GHL")
    g.add_argument("--json", action="store_true")
    v = sub.add_parser("validar", help="valida una carpeta de páginas")
    v.add_argument("carpeta")
    v.add_argument("--json", action="store_true")
    p = sub.add_parser("probar", help="calcula el diagnóstico con escenarios o respuestas")
    p.add_argument("--config", required=True)
    p.add_argument("--respuestas")
    p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.orden == "generar":
            gen = Generador(a.config, a.salida, a.cliente, a.marca, a.en_linea, a.fragmento_ghl)
            tipos = [t for t in TIPOS if t in gen.paginas] if a.tipo == "todas" else [a.tipo]
            res = gen.generar(tipos)
        elif a.orden == "validar":
            res = validar(a.carpeta)
        else:
            res = probar(a.config, a.respuestas)
    except ErrorUsuario as e:
        _error(str(e), 1, a.json)
        return 1
    except OSError as e:
        _error(f"No puedo leer o escribir un archivo: {e}", 2, a.json)
        return 2
    _imprimir(res, a.json)
    return 0 if res.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
