#!/usr/bin/env python3
"""Envía el brief diario al canal del propio operador: Telegram, email o Slack (solo biblioteca estándar).

Uso:
  python3 -I herramientas/notificar.py enviar --archivo informes/diario/2026-11-10.md [--canal auto] [--asunto TEXTO]
  python3 -I herramientas/notificar.py probar [--canal telegram|email|slack|auto]
  python3 -I herramientas/notificar.py telegram-chat-id [--guardar]
  (todas aceptan --json)

Canal `auto` (por defecto): el de `brief.canal` en contexto/preferencias.md. Si no hay preferencias (por ejemplo, en
una rutina en la nube), el primer canal con credenciales completas: Telegram, Slack y email, por este orden.

Credenciales en `.env` (las carga `_comun.cargar_entorno()`; este script nunca imprime sus valores):
  Telegram  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
  Slack     SLACK_WEBHOOK_URL (Incoming Webhook: https://hooks.slack.com/services/...)
  Email     SMTP_HOST, SMTP_PORT (465 SSL o 587 STARTTLS), SMTP_USUARIO, SMTP_CLAVE, EMAIL_DESTINO

Formato:
  - Telegram: Markdown → HTML de Telegram (b, i, s, code, pre, a, blockquote), troceado a 4096 caracteres por
    mensaje. Si Telegram no acepta el HTML de un trozo, ese trozo se reenvía como texto plano.
  - Slack: Markdown → mrkdwn, troceado a 4000 caracteres (lo que recomienda Slack).
  - Email: texto plano + HTML en el mismo mensaje. Asunto: --asunto, o el primer título `# ...` del archivo.

Seguridad:
  - Solo envía archivos .md de una carpeta `informes/` de la instancia (raíz o cliente), nunca de `privado/`.
  - Si el archivo parece contener una clave o un token, no envía nada (código 1).
  - Las direcciones de email que aparezcan en el texto se sustituyen por ***.
  - Cada intento queda en logs/notificaciones.jsonl (canal, archivo, ok, mensajes; nunca el contenido ni claves).

Códigos de salida (contrato §9): 0 enviado (o canal «ninguno»), 1 error de uso o el envío falló,
2 falta configuración o es inválida.
Contrato: docs/desarrollo/contratos.md §15. Guía: docs/guias/brief-diario.md.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import pathlib
import re
import smtplib
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402

GUIA = "docs/guias/brief-diario.md"
LIMITE_TELEGRAM = 4096          # Bot API: «1-4096 characters after entities parsing»
LIMITE_SLACK = 4000             # chat.postMessage: «limit the text field to 4,000 characters»
RESERVA_NUMERACION = 16         # espacio para « (2/3)» al final de cada trozo
TAMANO_MAXIMO = 200_000         # caracteres; un brief nunca debería acercarse
SEPARADOR = "──────────"

VARIABLES = {
    "telegram": ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"),
    "slack": ("SLACK_WEBHOOK_URL",),
    "email": ("SMTP_HOST", "SMTP_PORT", "SMTP_USUARIO", "SMTP_CLAVE", "EMAIL_DESTINO"),
}
ORDEN_AUTO = ("telegram", "slack", "email")
PISTAS = {
    "TELEGRAM_BOT_TOKEN": "créalo con @BotFather (/newbot) y pégalo tú en .env",
    "TELEGRAM_CHAT_ID": "escribe «hola» a tu bot y ejecuta `python3 -I herramientas/notificar.py telegram-chat-id --guardar`",
    "SLACK_WEBHOOK_URL": "crea un Incoming Webhook en tu app de Slack (api.slack.com/apps) y pega la URL en .env",
    "SMTP_HOST": "servidor de salida de tu correo (p. ej. smtp.gmail.com)",
    "SMTP_PORT": "465 (SSL) o 587 (STARTTLS)",
    "SMTP_USUARIO": "normalmente tu dirección de correo",
    "SMTP_CLAVE": "contraseña de aplicación, no la de tu cuenta",
    "EMAIL_DESTINO": "la dirección donde quieres recibir el brief",
}

_dormir = time.sleep  # los tests lo sustituyen para no esperar


class ErrorUso(Exception):
    codigo = 1


class ErrorEnvio(Exception):
    codigo = 1


class ErrorConfig(Exception):
    codigo = 2


# ------------------------------------------------------------------------------------------------ credenciales
def _credenciales(canal: str) -> dict:
    valores = {v: _comun.credencial(v) for v in VARIABLES[canal]}
    faltan = [v for v, x in valores.items() if not x]
    if faltan:
        detalle = "; ".join(f"{v}: {PISTAS[v]}" for v in faltan)
        palabra = "Falta" if len(faltan) == 1 else "Faltan"
        raise ErrorConfig(f"{palabra} en .env para el canal {canal}: {', '.join(faltan)} ({detalle}). Guía: {GUIA}")
    return valores


def _tiene_credenciales(canal: str) -> bool:
    return all(_comun.credencial(v) for v in VARIABLES[canal])


def _preferencias_brief() -> dict:
    f = _comun.RAIZ / "contexto" / "preferencias.md"
    if not f.exists():
        return {}
    try:
        cabecera = _comun.parsear_cabecera(f.read_text(encoding="utf-8"))
    except _comun.FichaInvalida as e:
        raise ErrorConfig(f"contexto/preferencias.md no tiene una cabecera válida ({e}). Compárala con "
                          f"plantillas/contexto/preferencias.md") from None
    brief = cabecera.get("brief")
    return brief if isinstance(brief, dict) else {}


def resolver_canal(canal: str) -> tuple[str, str]:
    """Devuelve (canal, de dónde sale): argumento, preferencias o credenciales."""
    if canal != "auto":
        return canal, "argumento"
    preferido = str(_preferencias_brief().get("canal", "") or "").strip().lower()
    if preferido:
        if preferido not in (*VARIABLES, "ninguno"):
            raise ErrorConfig(f"brief.canal = «{preferido}» en contexto/preferencias.md no es válido "
                              "(telegram, email, slack o ninguno)")
        return preferido, "preferencias"
    for c in ORDEN_AUTO:
        if _tiene_credenciales(c):
            return c, "credenciales"
    raise ErrorConfig("No hay canal configurado: ni brief.canal en contexto/preferencias.md ni credenciales completas "
                      f"de Telegram, Slack o email en .env. Ejecuta /brief-diario programar o lee {GUIA}")


def _limpiar(texto: str, secretos=()) -> str:
    """Quita de un mensaje cualquier secreto conocido (por si una librería lo cuela en un error)."""
    t = str(texto)
    for s in secretos:
        if s:
            t = t.replace(s, "***")
    return re.sub(r"bot\d+:[A-Za-z0-9_-]+", "bot***", t)


# ---------------------------------------------------------------------------------------------- archivo y texto
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_SECRETOS = (
    ("token de Telegram", re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{30,}")),
    ("token de Meta", re.compile(r"\bEAA[A-Za-z0-9]{30,}")),
    ("clave de Stripe", re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{10,}")),
    ("token de Slack", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("webhook de Slack", re.compile(r"hooks\.slack\.com/(?:services|triggers|workflows)/\S+")),
    ("clave de Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("clave de Google", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}")),
    ("token de GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("token de GoHighLevel", re.compile(r"\bpit-[0-9a-f]{8}-[0-9a-f-]{20,}")),
    ("clave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)
_VARIABLE_SENSIBLE = re.compile(r"TOKEN|KEY|CLAVE|SECRET|PASSWORD|WEBHOOK", re.I)


def leer_informe(ruta: str) -> tuple[str, str]:
    """Lee un informe enviable. Devuelve (texto, ruta relativa a la raíz en formato posix)."""
    raiz = _comun.RAIZ.resolve()
    p = pathlib.Path(ruta)
    if not p.is_absolute():
        p = raiz / p
    p = p.resolve()
    try:
        partes = p.relative_to(raiz).parts
    except ValueError:
        raise ErrorUso("Solo se envían informes de esta instancia (carpeta informes/ de la raíz o de un cliente)") from None
    en_informes = bool(partes) and (partes[0] == "informes"
                                    or (len(partes) > 3 and partes[0] == "clientes" and partes[2] == "informes"))
    if p.name.startswith(".env") or "privado" in partes or p.suffix.lower() != ".md" or not en_informes:
        raise ErrorUso("Solo se envían archivos .md de informes/ o clientes/<slug>/informes/ (nunca privado/ ni .env)")
    rel = "/".join(partes)
    if not p.is_file():
        raise ErrorUso(f"No existe {rel}")
    texto = p.read_text(encoding="utf-8-sig")  # sin BOM aunque lo haya escrito PowerShell 5.1
    if len(texto) > TAMANO_MAXIMO:
        raise ErrorUso(f"{rel} es demasiado largo para enviarlo ({len(texto)} caracteres); resume el brief")
    if not quitar_cabecera(texto).strip():
        raise ErrorUso(f"{rel} está vacío")
    return texto, rel


def comprobar_secretos(texto: str) -> None:
    for nombre, rx in _SECRETOS:
        if rx.search(texto):
            raise ErrorUso(f"El archivo contiene algo que parece un {nombre}: no se envía nada. Quítalo del informe")
    _comun.cargar_entorno()
    for clave, valor in os.environ.items():
        if valor and len(valor) >= 12 and _VARIABLE_SENSIBLE.search(clave) and valor in texto:
            raise ErrorUso(f"El archivo contiene el valor de {clave}: no se envía nada. Quítalo del informe")


def quitar_cabecera(texto: str) -> str:
    lineas = texto.replace("\r\n", "\n").split("\n")
    if lineas and lineas[0].strip() == "---":
        for i in range(1, len(lineas)):
            if lineas[i].strip() == "---":
                return "\n".join(lineas[i + 1:]).strip("\n")
    return texto.strip("\n")


def anonimizar_emails(texto: str) -> str:
    return _EMAIL.sub("***", texto)


# ------------------------------------------------------------------------------------------- Markdown → bloques
_RX_TITULO = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_RX_LISTA = re.compile(r"^(\s*)([-*+]|\d{1,3}[.)])\s+(.*)$")
_RX_SEPARADOR = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
_RX_FILA_SEPARADORA = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)*\|?\s*$")


def _celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def bloques(md: str) -> list[tuple]:
    """Markdown (subconjunto) → lista de bloques: titulo, parrafo, lista, cita, tabla, codigo, separador, vacio."""
    lineas = quitar_cabecera(md).split("\n")
    out: list[tuple] = []
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        s = linea.strip()
        if s.startswith("```"):
            j, codigo = i + 1, []
            while j < len(lineas) and not lineas[j].strip().startswith("```"):
                codigo.append(lineas[j])
                j += 1
            out.append(("codigo", "\n".join(codigo)))
            i = j + 1
            continue
        if s.startswith("<!--"):
            while i < len(lineas) and "-->" not in lineas[i]:
                i += 1
            i += 1
            continue
        if not s:
            out.append(("vacio",))
        elif m := _RX_TITULO.match(linea):
            out.append(("titulo", len(m.group(1)), m.group(2)))
        elif _RX_SEPARADOR.match(linea):
            out.append(("separador",))
        elif s.startswith(">"):
            cita = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                cita.append(lineas[i].strip()[1:].strip())
                i += 1
            out.append(("cita", cita))
            continue
        elif s.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append(lineas[i])
                i += 1
            cabecera = len(filas) > 1 and bool(_RX_FILA_SEPARADORA.match(filas[1]))
            cuerpo = [_celdas(f) for k, f in enumerate(filas)
                      if not _RX_FILA_SEPARADORA.match(f) and not (cabecera and k == 0)]
            out.append(("tabla", _celdas(filas[0]) if cabecera else [], cuerpo))
            continue
        elif m := _RX_LISTA.match(linea):
            out.append(("lista", len(m.group(1).replace("\t", "  ")) // 2, m.group(2), m.group(3)))
        else:
            out.append(("parrafo", s))
        i += 1
    return out


# ------------------------------------------------------------------------------------------------- en línea
_RX_CODIGO = re.compile(r"`([^`\n]+)`")
_RX_ENLACE = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
_RX_NEGRITA = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
_RX_TACHADO = re.compile(r"~~(?=\S)(.+?)(?<=\S)~~")
_RX_CURSIVA = re.compile(r"(?<![\w*\\])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])")


def _escapar_html(t: str) -> str:
    return html.escape(t, quote=False)


def _escapar_slack(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def en_linea(texto: str, destino: str) -> str:
    """Formato en línea de Markdown → `html` (Telegram y email) o `slack` (mrkdwn). Las etiquetas quedan cerradas."""
    codigos: list[str] = []
    enlaces: list[tuple[str, str]] = []

    def _guardar_codigo(m):
        codigos.append(m.group(1))
        return f"\x00C{len(codigos) - 1}\x00"

    def _guardar_enlace(m):
        enlaces.append((m.group(1), m.group(2)))
        return f"\x00E{len(enlaces) - 1}\x00"

    t = _RX_CODIGO.sub(_guardar_codigo, texto)
    t = _RX_ENLACE.sub(_guardar_enlace, t)
    t = _formato(t, destino)
    for n, (etiqueta, url) in enumerate(enlaces):
        if destino == "html":
            rep = f'<a href="{html.escape(url, quote=True)}">{_formato(etiqueta, destino)}</a>'
        else:
            rep = f"<{url}|{_formato(etiqueta, destino).replace('|', '/')}>"
        t = t.replace(f"\x00E{n}\x00", rep)
    for n, codigo in enumerate(codigos):
        rep = f"<code>{_escapar_html(codigo)}</code>" if destino == "html" else f"`{_escapar_slack(codigo)}`"
        t = t.replace(f"\x00C{n}\x00", rep)
    return t


def _formato(t: str, destino: str) -> str:
    if destino == "html":
        t = _escapar_html(t)
        t = _RX_NEGRITA.sub(r"<b>\1</b>", t)
        t = _RX_TACHADO.sub(r"<s>\1</s>", t)
        return _RX_CURSIVA.sub(r"<i>\1</i>", t)
    t = _escapar_slack(t)
    t = _RX_NEGRITA.sub("\x01\\1\x01", t)
    t = _RX_TACHADO.sub(r"~\1~", t)
    t = _RX_CURSIVA.sub(r"_\1_", t)
    return t.replace("\x01", "*")


# ------------------------------------------------------------------------------------------------ renderizado
def _vinieta(marcador: str) -> str:
    return "•" if marcador in "-*+" else marcador


def _compactar(lineas: list[str]) -> list[str]:
    out: list[str] = []
    for linea in lineas:
        if linea == "" and (not out or out[-1] == ""):
            continue
        out.append(linea)
    while out and out[-1] == "":
        out.pop()
    return out


def render_telegram(md: str) -> list[str]:
    """Bloques en HTML de Telegram; cada uno cierra sus etiquetas, así que se puede trocear entre bloques."""
    out = []
    for b in bloques(md):
        tipo = b[0]
        if tipo == "vacio":
            out.append("")
        elif tipo == "titulo":
            out.append(f"<b>{en_linea(b[2], 'html')}</b>")
        elif tipo == "parrafo":
            out.append(en_linea(b[1], "html"))
        elif tipo == "lista":
            out.append("   " * b[1] + f"{_vinieta(b[2])} {en_linea(b[3], 'html')}")
        elif tipo == "cita":
            out.append("<blockquote>" + "\n".join(en_linea(x, "html") for x in b[1]) + "</blockquote>")
        elif tipo == "tabla":
            for celdas in b[2]:
                celdas = [c for c in celdas if c]
                if celdas:
                    out.append(" · ".join([f"<b>{en_linea(celdas[0], 'html')}</b>"]
                                          + [en_linea(c, "html") for c in celdas[1:]]))
        elif tipo == "codigo":
            out.append(f"<pre>{_escapar_html(b[1])}</pre>")
        elif tipo == "separador":
            out.append(SEPARADOR)
    return _compactar(out)


def render_slack(md: str) -> list[str]:
    out = []
    for b in bloques(md):
        tipo = b[0]
        if tipo == "vacio":
            out.append("")
        elif tipo == "titulo":
            out.append(f"*{en_linea(b[2], 'slack')}*")
        elif tipo == "parrafo":
            out.append(en_linea(b[1], "slack"))
        elif tipo == "lista":
            out.append("   " * b[1] + f"{_vinieta(b[2])} {en_linea(b[3], 'slack')}")
        elif tipo == "cita":
            out.append("\n".join(f"> {en_linea(x, 'slack')}" for x in b[1]))
        elif tipo == "tabla":
            for celdas in b[2]:
                celdas = [c for c in celdas if c]
                if celdas:
                    out.append(" · ".join([f"*{en_linea(celdas[0], 'slack')}*"]
                                          + [en_linea(c, "slack") for c in celdas[1:]]))
        elif tipo == "codigo":
            out.append(f"```\n{_escapar_slack(b[1])}\n```")
        elif tipo == "separador":
            out.append(SEPARADOR)
    return _compactar(out)


def render_email(md: str) -> str:
    """HTML completo para el email (con tablas y listas de verdad)."""
    partes: list[str] = []
    lista_abierta = ""
    for b in bloques(md):
        tipo = b[0]
        if lista_abierta and tipo != "lista":
            partes.append(f"</{lista_abierta}>")
            lista_abierta = ""
        if tipo == "titulo":
            n = min(b[1], 3)
            partes.append(f'<h{n} style="margin:18px 0 8px">{en_linea(b[2], "html")}</h{n}>')
        elif tipo == "parrafo":
            partes.append(f'<p style="margin:0 0 8px">{en_linea(b[1], "html")}</p>')
        elif tipo == "lista":
            etiqueta = "ul" if b[2] in "-*+" else "ol"
            if lista_abierta != etiqueta:
                if lista_abierta:
                    partes.append(f"</{lista_abierta}>")
                partes.append(f'<{etiqueta} style="margin:0 0 8px;padding-left:22px">')
                lista_abierta = etiqueta
            partes.append(f'<li style="margin-left:{b[1] * 16}px">{en_linea(b[3], "html")}</li>')
        elif tipo == "cita":
            partes.append('<blockquote style="margin:8px 0;padding-left:10px;border-left:3px solid #c8c8c8;color:#555">'
                          + "<br>".join(en_linea(x, "html") for x in b[1]) + "</blockquote>")
        elif tipo == "tabla":
            celda = 'style="border:1px solid #ddd;padding:4px 8px;text-align:left;vertical-align:top"'
            filas = []
            if b[1]:
                filas.append("<tr>" + "".join(f"<th {celda}>{en_linea(c, 'html')}</th>" for c in b[1]) + "</tr>")
            for celdas in b[2]:
                filas.append("<tr>" + "".join(f"<td {celda}>{en_linea(c, 'html')}</td>" for c in celdas) + "</tr>")
            partes.append('<table style="border-collapse:collapse;margin:0 0 10px">' + "".join(filas) + "</table>")
        elif tipo == "codigo":
            partes.append(f'<pre style="background:#f4f4f4;padding:8px;white-space:pre-wrap">{_escapar_html(b[1])}</pre>')
        elif tipo == "separador":
            partes.append('<hr style="border:0;border-top:1px solid #ddd">')
    if lista_abierta:
        partes.append(f"</{lista_abierta}>")
    return ('<!doctype html><html><body style="font-family:-apple-system,\'Segoe UI\',Roboto,Arial,sans-serif;'
            'font-size:15px;line-height:1.5;color:#1a1a1a;max-width:680px">' + "\n".join(partes) + "</body></html>")


def a_texto_plano(html_telegram: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", html_telegram))


# -------------------------------------------------------------------------------------------------- troceado
def longitud_telegram(t: str) -> int:
    """Telegram mide en unidades UTF-16 (un emoji como 🟢 cuenta 2)."""
    return len(t.encode("utf-16-le")) // 2


def _partir_plano(texto: str, limite: int, escapar, medir) -> list[str]:
    """Parte texto sin formato en piezas que, ya escapadas, no superan el límite. Corta en espacios si puede."""
    piezas, actual, medida = [], "", 0
    for ch in texto:
        m = medir(escapar(ch))
        if medida + m > limite and actual:
            corte = actual.rfind(" ")
            if corte > len(actual) // 2:
                piezas.append(actual[:corte])
                actual = actual[corte + 1:]
            else:
                piezas.append(actual)
                actual = ""
            medida = medir(escapar(actual))
        actual += ch
        medida += m
    if actual:
        piezas.append(actual)
    return [escapar(p) for p in piezas if p.strip()]


def _partir_bloque_telegram(bloque: str, limite: int) -> list[str]:
    if bloque.startswith("<pre>") and bloque.endswith("</pre>"):
        contenido = html.unescape(bloque[5:-6])
        piezas = _partir_plano(contenido, limite - 11, _escapar_html, longitud_telegram)
        return [f"<pre>{p}</pre>" for p in piezas]
    return _partir_plano(a_texto_plano(bloque), limite, _escapar_html, longitud_telegram)


def _partir_bloque_slack(bloque: str, limite: int) -> list[str]:
    plano = html.unescape(bloque)  # el escape de Slack son las mismas tres entidades
    return _partir_plano(plano, limite, _escapar_slack, len)


def _empaquetar(bloques_render: list[str], limite: int, medir, partir) -> list[str]:
    util = limite - RESERVA_NUMERACION
    trozos: list[str] = []
    actual: list[str] = []

    def _cerrar():
        texto = "\n".join(actual).strip("\n")
        if texto.strip():
            trozos.append(texto)
        actual.clear()

    for b in bloques_render:
        if medir(b) > util:
            _cerrar()
            trozos.extend(partir(b, util))
            continue
        if actual and medir("\n".join(actual + [b])) > util:
            _cerrar()
            if b == "":
                continue
        actual.append(b)
    _cerrar()
    return trozos


def _numerar(trozos: list[str], destino: str) -> list[str]:
    if len(trozos) < 2:
        return trozos
    n = len(trozos)
    marca = "<i>({i}/{n})</i>" if destino == "html" else "_({i}/{n})_"
    return [f"{t}\n{marca.format(i=i, n=n)}" for i, t in enumerate(trozos, start=1)]


def trocear_telegram(md: str, limite: int = LIMITE_TELEGRAM) -> list[str]:
    return _numerar(_empaquetar(render_telegram(md), limite, longitud_telegram, _partir_bloque_telegram), "html")


def trocear_slack(md: str, limite: int = LIMITE_SLACK) -> list[str]:
    return _numerar(_empaquetar(render_slack(md), limite, len, _partir_bloque_slack), "slack")


# ------------------------------------------------------------------------------------------------------- HTTP
def _http(url: str, cuerpo: bytes | None = None, cabeceras: dict | None = None, secretos=(),
          intentos: int = 3, timeout: int = 30) -> tuple[int, str]:
    """Devuelve (estado, cuerpo). Reintenta fallos de red y 5xx. Nunca deja la URL (puede llevar el token) en un error."""
    h = {"User-Agent": "meta-ads-os/1.0"}
    h.update(cabeceras or {})
    req = urllib.request.Request(url, data=cuerpo, headers=h, method="POST" if cuerpo is not None else "GET")
    host = urllib.parse.urlsplit(url).hostname or "el servidor"
    ultimo = ""
    for i in range(intentos):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return getattr(r, "status", 200), r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            try:
                texto = e.read().decode("utf-8", "replace")
            except Exception:
                texto = ""
            if e.code >= 500 and i < intentos - 1:
                ultimo = f"HTTP {e.code}"
                _dormir(2 * (i + 1))
                continue
            return e.code, texto
        except (urllib.error.URLError, OSError) as e:
            ultimo = _limpiar(getattr(e, "reason", None) or type(e).__name__, secretos)
            if i < intentos - 1:
                _dormir(2 * (i + 1))
    raise ErrorEnvio(f"No hay conexión con {host} ({ultimo}). Revisa la conexión y repite")


# --------------------------------------------------------------------------------------------------- Telegram
_RX_TOKEN_TELEGRAM = re.compile(r"\d{5,}:[A-Za-z0-9_-]{30,}")


def _validar_token_telegram(token: str) -> None:
    if not _RX_TOKEN_TELEGRAM.fullmatch(token.strip()):
        raise ErrorConfig("TELEGRAM_BOT_TOKEN no tiene el formato que da @BotFather (números, dos puntos y unas 35 "
                          "letras). Vuelve a copiarlo entero en .env")


def _telegram(token: str, metodo: str, datos: dict | None = None) -> tuple[int, dict]:
    url = f"https://api.telegram.org/bot{token.strip()}/{metodo}"
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    estado, texto = _http(url, cuerpo, {"Content-Type": "application/json"} if cuerpo else None, secretos=[token])
    try:
        respuesta = json.loads(texto)
    except ValueError:
        respuesta = {"ok": False, "error_code": estado, "description": texto[:200]}
    return estado, respuesta if isinstance(respuesta, dict) else {"ok": False}


def _error_telegram(estado: int, desc: str, token: str):
    d = desc.lower()
    if estado in (401, 404):
        return ErrorConfig(f"Telegram rechaza TELEGRAM_BOT_TOKEN ({estado}): cópialo de nuevo de @BotFather")
    if "chat not found" in d or "chat_id is empty" in d:
        return ErrorConfig("TELEGRAM_CHAT_ID no corresponde a ningún chat de este bot: escribe «hola» al bot y "
                           "ejecuta `python3 -I herramientas/notificar.py telegram-chat-id`")
    if estado == 403:
        return ErrorConfig(f"Telegram no deja escribir en ese chat ({_limpiar(desc, [token])}): abre el bot, pulsa "
                           "Iniciar y desbloquéalo si hace falta")
    return ErrorEnvio(f"Telegram respondió {estado}: {_limpiar(desc, [token])[:200]}")


def _mandar_trozo_telegram(token: str, chat: str, trozo: str) -> None:
    datos = {"chat_id": chat, "text": trozo, "parse_mode": "HTML", "link_preview_options": {"is_disabled": True}}
    for _ in range(4):
        estado, r = _telegram(token, "sendMessage", datos)
        if r.get("ok"):
            return
        desc = str(r.get("description", ""))
        if estado == 429 or r.get("error_code") == 429:
            espera = int((r.get("parameters") or {}).get("retry_after", 5) or 5)
            if espera > 60:
                break
            _dormir(espera + 1)
            continue
        if estado == 400 and "parse" in desc.lower() and "parse_mode" in datos:
            datos = {"chat_id": chat, "text": a_texto_plano(trozo), "link_preview_options": {"is_disabled": True}}
            continue
        nuevo = (r.get("parameters") or {}).get("migrate_to_chat_id")
        if nuevo:  # el grupo pasó a supergrupo: su chat_id cambió (no es un secreto)
            raise ErrorConfig(f"El grupo pasó a supergrupo y su chat_id es ahora {nuevo}: cambia TELEGRAM_CHAT_ID en "
                              ".env por ese número")
        raise _error_telegram(estado, desc, token)
    raise ErrorEnvio("Telegram sigue limitando los envíos (429). Prueba de nuevo en unos minutos")


def enviar_telegram(md: str, asunto: str | None = None) -> int:
    c = _credenciales("telegram")
    token, chat = c["TELEGRAM_BOT_TOKEN"], c["TELEGRAM_CHAT_ID"].strip()
    _validar_token_telegram(token)
    trozos = trocear_telegram(md)
    for i, trozo in enumerate(trozos):
        if i:
            _dormir(1)  # ~1 mensaje por segundo al mismo chat
        try:
            _mandar_trozo_telegram(token, chat, trozo)
        except (ErrorEnvio, ErrorConfig) as e:
            if i:
                e.args = (f"{e.args[0]} (se enviaron {i} de {len(trozos)} mensajes)",)
            raise
    return len(trozos)


def chats_telegram() -> list[dict]:
    token = _comun.credencial("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ErrorConfig(f"Falta TELEGRAM_BOT_TOKEN en .env ({PISTAS['TELEGRAM_BOT_TOKEN']}). Guía: {GUIA}")
    _validar_token_telegram(token)
    estado, r = _telegram(token, "getUpdates")
    if estado == 409:
        raise ErrorConfig("Este bot tiene un webhook activo y así getUpdates no funciona. Crea con @BotFather un bot "
                          "nuevo solo para el brief")
    if not r.get("ok"):
        raise _error_telegram(estado, str(r.get("description", "")), token)
    chats: dict[str, dict] = {}
    for u in r.get("result") or []:
        for clave in ("message", "edited_message", "channel_post", "edited_channel_post", "my_chat_member"):
            m = u.get(clave) if isinstance(u, dict) else None
            ch = m.get("chat") if isinstance(m, dict) else None
            if isinstance(ch, dict) and "id" in ch:
                tipo = {"private": "conversación privada", "group": "grupo", "supergroup": "grupo",
                        "channel": "canal"}.get(ch.get("type", ""), ch.get("type", ""))
                chats[str(ch["id"])] = {"chat_id": str(ch["id"]), "tipo": tipo,
                                        "nombre": ch.get("title", "") if ch.get("type") != "private" else ""}
    if not chats:
        raise ErrorUso("El bot aún no tiene mensajes: abre Telegram, busca tu bot, pulsa Iniciar, escríbele «hola» y "
                       "repite (Telegram solo guarda los mensajes 24 horas)")
    return list(chats.values())


def guardar_chat_id(chat_id: str) -> str:
    """Añade TELEGRAM_CHAT_ID al final de .env sin tocar el resto. Nunca sobrescribe uno que ya exista."""
    existente = _comun.credencial("TELEGRAM_CHAT_ID")
    if existente:
        if existente.strip() == chat_id:
            return "ya estaba guardado"
        raise ErrorUso("Ya hay un TELEGRAM_CHAT_ID en .env (o en el entorno) y es otro: cámbialo tú a mano si quieres "
                       "usar este")
    f = _comun.RAIZ / ".env"
    nuevo = not f.exists()
    prefijo = ""
    if not nuevo and f.stat().st_size:
        with f.open("rb") as h:
            h.seek(-1, os.SEEK_END)
            prefijo = "" if h.read(1) == b"\n" else "\n"
    with f.open("a", encoding="utf-8") as h:
        h.write(f"{prefijo}TELEGRAM_CHAT_ID={chat_id}\n")
    if nuevo:
        os.chmod(f, 0o600)
    os.environ["TELEGRAM_CHAT_ID"] = chat_id
    return "guardado en .env"


# ------------------------------------------------------------------------------------------------------ Slack
def enviar_slack(md: str, asunto: str | None = None) -> int:
    url = _credenciales("slack")["SLACK_WEBHOOK_URL"].strip()
    if not url.startswith("https://hooks.slack.com/services/"):
        raise ErrorConfig("SLACK_WEBHOOK_URL no es un Incoming Webhook de Slack (debe empezar por "
                          "https://hooks.slack.com/services/)")
    trozos = trocear_slack(md)
    for i, trozo in enumerate(trozos):
        if i:
            _dormir(1)  # Slack: ~1 mensaje por segundo por canal
        estado, texto = _http(url, json.dumps({"text": trozo}).encode("utf-8"),
                              {"Content-Type": "application/json"}, secretos=[url])
        if estado == 200:
            continue
        hecho = f" (se enviaron {i} de {len(trozos)} mensajes)" if i else ""
        if estado in (403, 404, 410):
            raise ErrorConfig(f"Slack no reconoce SLACK_WEBHOOK_URL ({estado}): crea otro Incoming Webhook{hecho}")
        raise ErrorEnvio(f"Slack respondió {estado}: {_limpiar(texto[:200], [url])}{hecho}")
    return len(trozos)


# ------------------------------------------------------------------------------------------------------ Email
def _asunto_por_defecto(md: str, fecha: str) -> str:
    for b in bloques(md):
        if b[0] == "titulo":
            return a_texto_plano(en_linea(b[2], "html")).strip()[:150]
    return f"Brief diario · {fecha}"


def enviar_email(md: str, asunto: str | None = None) -> int:
    c = _credenciales("email")
    try:
        puerto = int(str(c["SMTP_PORT"]).strip())
    except ValueError:
        raise ErrorConfig("SMTP_PORT debe ser un número: 465 (SSL) o 587 (STARTTLS)") from None
    destinos = [d.strip() for d in c["EMAIL_DESTINO"].split(",") if d.strip()]
    if not destinos or not all(_EMAIL.fullmatch(d) for d in destinos):
        raise ErrorConfig("EMAIL_DESTINO no es una dirección de email válida")
    usuario, clave, host = c["SMTP_USUARIO"].strip(), c["SMTP_CLAVE"], c["SMTP_HOST"].strip()
    msg = EmailMessage()
    msg["Subject"] = asunto or _asunto_por_defecto(md, date.today().isoformat())
    msg["From"] = usuario if _EMAIL.fullmatch(usuario) else destinos[0]
    msg["To"] = ", ".join(destinos)
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="meta-ads-os.local")
    msg.set_content(quitar_cabecera(md) + "\n")
    msg.add_alternative(render_email(md), subtype="html")
    contexto = ssl.create_default_context()
    try:
        if puerto == 465:
            with smtplib.SMTP_SSL(host, puerto, context=contexto, timeout=30) as s:
                s.login(usuario, clave)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, puerto, timeout=30) as s:
                s.ehlo()
                if not s.has_extn("starttls"):
                    raise ErrorConfig(f"El servidor SMTP no ofrece cifrado (STARTTLS) en el puerto {puerto}: usa 465 o "
                                      "587. No se envían credenciales sin cifrar")
                s.starttls(context=contexto)
                s.ehlo()
                s.login(usuario, clave)
                s.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        raise ErrorConfig("El servidor SMTP rechaza SMTP_USUARIO o SMTP_CLAVE (con Gmail u Outlook necesitas una "
                          "contraseña de aplicación)") from None
    except smtplib.SMTPRecipientsRefused:
        raise ErrorConfig("El servidor SMTP rechaza EMAIL_DESTINO") from None
    except socket.gaierror:
        raise ErrorConfig("SMTP_HOST no existe o no resuelve: revísalo (p. ej. smtp.gmail.com)") from None
    except (smtplib.SMTPException, OSError) as e:
        raise ErrorEnvio(f"No se pudo enviar el email ({type(e).__name__}). Revisa SMTP_HOST y SMTP_PORT") from None
    return 1


ENVIAR = {"telegram": enviar_telegram, "slack": enviar_slack, "email": enviar_email}


# -------------------------------------------------------------------------------------------------- registro
def _registrar(canal: str, archivo: str, ok: bool, mensajes: int, detalle: str = "") -> None:
    """logs/notificaciones.jsonl. El orden de claves es fijo: brief.sh busca `"archivo": "…", "ok": true`."""
    try:
        logs = _comun.RAIZ / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        fila = {"ts": datetime.now().isoformat(timespec="seconds"), "canal": canal, "archivo": archivo, "ok": ok,
                "mensajes": mensajes, "detalle": _limpiar(detalle)[:300]}
        with (logs / "notificaciones.jsonl").open("a", encoding="utf-8") as h:
            h.write(json.dumps(fila, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ------------------------------------------------------------------------------------------------ subcomandos
def cmd_enviar(a) -> dict:
    texto, rel = leer_informe(a.archivo)
    comprobar_secretos(texto)
    texto = anonimizar_emails(texto)
    canal, origen = resolver_canal(a.canal)
    if canal == "ninguno":
        _registrar("ninguno", rel, True, 0, "canal ninguno en preferencias")
        return {"ok": True, "canal": "ninguno", "archivo": rel, "mensajes": 0,
                "texto": f"Canal «ninguno» en contexto/preferencias.md: no se envía nada. El brief está en {rel}."}
    try:
        n = ENVIAR[canal](texto, a.asunto)
    except (ErrorEnvio, ErrorConfig) as e:
        _registrar(canal, rel, False, 0, str(e))
        raise
    _registrar(canal, rel, True, n)
    plural = "mensaje" if n == 1 else "mensajes"
    return {"ok": True, "canal": canal, "origen_canal": origen, "archivo": rel, "mensajes": n,
            "texto": f"Enviado por {canal}: {n} {plural} ({rel})."}


def cmd_probar(a) -> dict:
    canal, origen = resolver_canal(a.canal)
    if canal == "ninguno":
        raise ErrorConfig("brief.canal es «ninguno» en contexto/preferencias.md: elige telegram, email o slack o pasa "
                          "--canal")
    ahora = datetime.now().strftime("%Y-%m-%d a las %H:%M")
    md = (f"# ✅ Meta Ads OS · prueba del brief diario\n\nEnviado el {ahora}. Si lo ves, el canal **{canal}** "
          "funciona y el brief de cada mañana llegará aquí.")
    try:
        n = ENVIAR[canal](md, "Meta Ads OS · prueba del brief diario")
    except (ErrorEnvio, ErrorConfig) as e:
        _registrar(canal, "", False, 0, f"prueba: {e}")
        raise
    _registrar(canal, "", True, n, "prueba")
    return {"ok": True, "canal": canal, "origen_canal": origen, "mensajes": n,
            "texto": f"Mensaje de prueba enviado por {canal}. Comprueba que te ha llegado."}


def cmd_chat_id(a) -> dict:
    chats = chats_telegram()
    lineas = ["Chats que han escrito a tu bot:"]
    for c in chats:
        nombre = f" «{c['nombre']}»" if c["nombre"] else ""
        lineas.append(f"  {c['chat_id']}  ({c['tipo']}{nombre})")
    res = {"ok": True, "chats": chats}
    if a.guardar:
        if len(chats) != 1:
            raise ErrorUso("Han escrito al bot varios chats: añade tú a mano en .env el TELEGRAM_CHAT_ID que quieras")
        estado = guardar_chat_id(chats[0]["chat_id"])
        res["guardado"] = estado
        lineas.append(f"TELEGRAM_CHAT_ID {estado}. Siguiente paso: python3 -I herramientas/notificar.py probar "
                      "--canal telegram")
    else:
        lineas.append("Guárdalo con --guardar (si solo hay uno) o añade tú a mano TELEGRAM_CHAT_ID=<número> a .env.")
    res["texto"] = "\n".join(lineas)
    return res


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # los errores de uso salen con 1, no con el 2 de argparse (contrato §9)
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> int:
    ap = _Parser(prog="notificar.py", description="Envía el brief diario por Telegram, email o Slack.")
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=_Parser)
    e = sub.add_parser("enviar", help="envía un informe .md de informes/ o clientes/<slug>/informes/")
    e.add_argument("--archivo", required=True)
    e.add_argument("--canal", choices=["telegram", "email", "slack", "auto"], default="auto")
    e.add_argument("--asunto", help="asunto del email (por defecto, el primer título del archivo)")
    e.add_argument("--json", action="store_true")
    p = sub.add_parser("probar", help="manda un mensaje de prueba al canal")
    p.add_argument("--canal", choices=["telegram", "email", "slack", "auto"], default="auto")
    p.add_argument("--json", action="store_true")
    t = sub.add_parser("telegram-chat-id", help="dice el chat_id después de que escribas a tu bot")
    t.add_argument("--guardar", action="store_true", help="añade TELEGRAM_CHAT_ID a .env si solo hay un chat")
    t.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        res = {"enviar": cmd_enviar, "probar": cmd_probar, "telegram-chat-id": cmd_chat_id}[a.cmd](a)
    except (ErrorUso, ErrorEnvio, ErrorConfig) as err:
        mensaje = _limpiar(str(err))
        if a.json:
            print(json.dumps({"ok": False, "codigo": err.codigo, "error": mensaje}, ensure_ascii=False))
        else:
            print(f"Error: {mensaje}", file=sys.stderr)
        return err.codigo
    if a.json:
        print(json.dumps({k: v for k, v in res.items() if k != "texto"}, ensure_ascii=False))
    else:
        print(res["texto"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
