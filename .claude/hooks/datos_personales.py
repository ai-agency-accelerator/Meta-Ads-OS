#!/usr/bin/env python3
"""Datos personales (RGPD) al escribir archivos (PreToolUse sobre Write, Edit, MultiEdit y NotebookEdit).

Los datos personales de leads y clientes (emails, teléfonos, listas de personas) solo pueden vivir en
`clientes/<slug>/privado/`. En el resto (informes, datos/, registro creativo, docs, lo que se comparte o se versiona)
solo van IDs y agregados. Si el texto que se va a escribir lleva emails, teléfonos o una tabla con columnas de datos
personales, pide confirmación y propone `privado/` o agregados. Nunca repite los valores encontrados.

No revisa: `clientes/*/privado/**`, `contexto/**` (datos del propio operador, p. ej. su email para el brief) ni
archivos fuera del proyecto. Los dominios de ejemplo (example.com, acme…, nimbo…) no cuentan.

Topes de gasto: en Write, Edit y MultiEdit de `clientes/<slug>/ficha.md` calcula cómo queda el archivo y compara
`topes.*` de la cabecera antes y después (0 o vacío = sin definir). Si cambian → ask «cambias los topes de gasto de
<slug>: cambio_dia 100 → 5000». Si la cabecera deja de ser válida → ask (los topes dejarían de leerse). Si no cambian,
no decide. Los topes son el freno de `meta_guard`: subirlos es una decisión del operador, no del modelo.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "datos_personales"
_COLUMNAS_PII = re.compile(
    r"(?i)^(e-?mail|correo|correo_electronico|phone|phone_number|telefono|teléfono|tel|movil|móvil|whatsapp|"
    r"first_name|last_name|full_name|nombre_completo|apellidos?|dni|nif|nie|pasaporte|direccion|dirección|address|"
    r"codigo_postal|fecha_nacimiento|birthdate|date_of_birth|ip|ip_address)$")


def _texto_nuevo(entrada: dict, tool: str) -> str:
    if tool == "Write":
        return str(entrada.get("content") or "")
    if tool == "Edit":
        return str(entrada.get("new_string") or "")
    if tool == "MultiEdit":
        return "\n".join(str(x.get("new_string") or "") for x in entrada.get("edits") or [] if isinstance(x, dict))
    if tool == "NotebookEdit":
        return str(entrada.get("new_source") or "")
    return ""


def _excluida(ruta: pathlib.Path, raiz: pathlib.Path) -> bool:
    try:
        rel = ruta.resolve().relative_to(raiz.resolve())
    except (ValueError, OSError):
        return True  # fuera del proyecto: no es asunto de este hook
    partes = [p.lower() for p in rel.parts]
    if partes and partes[0] == "contexto":
        return True
    if len(partes) >= 3 and partes[0] == "clientes" and partes[2] == "privado":
        return True
    return rel.name.startswith(".env")


def columnas_pii(texto: str) -> list:
    """Columnas de datos personales en la cabecera de una tabla CSV/TSV o Markdown con al menos 2 filas."""
    lineas = [l for l in texto.splitlines() if l.strip()]
    for i, linea in enumerate(lineas[:50]):
        separador = "|" if linea.count("|") >= 2 else ("\t" if "\t" in linea else ("," if "," in linea else ";"))
        celdas = [c.strip().strip('"').strip() for c in linea.strip().strip("|").split(separador)]
        encontradas = [c for c in celdas if _COLUMNAS_PII.match(c.replace(" ", "_"))]
        filas = [l for l in lineas[i + 1:] if separador in l and not re.fullmatch(r"[\s|:-]+", l)]
        if encontradas and len(filas) >= 2:
            return encontradas
    return []


# ─────────────────────────────────────────────────────────────── topes de la ficha
def _slug_de_ficha(ruta: pathlib.Path, raiz: pathlib.Path) -> str | None:
    try:
        rel = ruta.resolve().relative_to(raiz.resolve())
    except (ValueError, OSError):
        return None
    partes = rel.parts
    if len(partes) == 3 and partes[0] == "clientes" and partes[2].lower() == "ficha.md":
        return partes[1]
    return None


def _aplicar_edicion(texto: str, edicion: dict) -> str | None:
    """Aplica un Edit como Claude Code (None si `old_string` no está: la edición fallaría sin escribir)."""
    viejo = str(edicion.get("old_string") or "")
    nuevo = str(edicion.get("new_string") or "")
    if not viejo:
        return nuevo if not texto else None
    if viejo not in texto:
        return None
    return texto.replace(viejo, nuevo) if edicion.get("replace_all") else texto.replace(viejo, nuevo, 1)


def _contenido_despues(tool: str, entrada: dict, antes: str) -> str | None:
    if tool == "Write":
        return str(entrada.get("content") or "")
    if tool == "Edit":
        return _aplicar_edicion(antes, entrada)
    if tool == "MultiEdit":
        texto = antes
        for edicion in entrada.get("edits") or []:
            if not isinstance(edicion, dict):
                return None
            texto = _aplicar_edicion(texto, edicion)
            if texto is None:
                return None
        return texto
    return None


def _topes(texto: str):
    """{clave: importe o None} de `topes` en la cabecera, o None si la cabecera no es válida."""
    cab = L.parsear_cabecera(texto) if texto else {}
    if cab is None:
        return None
    topes = cab.get("topes") if isinstance(cab.get("topes"), dict) else {}
    salida = {}
    for clave, valor in topes.items():
        n = L.numero(valor)
        salida[clave] = n if n and n > 0 else None
    return salida


def _fmt(n) -> str:
    if n is None:
        return "sin definir"
    return str(int(n)) if float(n).is_integer() else f"{n:g}"


def decision_topes(tool: str, entrada: dict, ruta: pathlib.Path, raiz: pathlib.Path):
    """ask si la escritura cambia `topes.*` de una ficha; None si no los toca."""
    if tool not in ("Write", "Edit", "MultiEdit"):
        return None
    slug = _slug_de_ficha(ruta, raiz)
    if not slug:
        return None
    try:
        antes = ruta.read_text(encoding="utf-8", errors="replace") if ruta.is_file() else ""
    except OSError:
        antes = ""
    despues = _contenido_despues(tool, entrada, antes)
    if despues is None:
        return None  # la edición no se aplicaría: Claude Code la rechazará sin escribir nada
    t_antes, t_despues = _topes(antes), _topes(despues)
    if t_antes == t_despues:
        return None
    if t_despues is None:
        return L.pre("ask", f"La ficha de «{slug}» quedaría con la cabecera inválida: los topes de gasto "
                            "(`topes.cambio_dia`, `topes.total_dia`) dejarían de leerse y meta_guard aplicaría otros. "
                            "Confirma solo si lo arreglas a continuación.")
    t_antes = t_antes or {}
    cambios = [f"{k} {_fmt(t_antes.get(k))} → {_fmt(t_despues.get(k))}"
               for k in sorted(set(t_antes) | set(t_despues)) if t_antes.get(k) != t_despues.get(k)]
    if not cambios:
        return None
    return L.pre("ask", f"Cambias los topes de gasto de «{slug}»: {', '.join(cambios)}. Los topes frenan lo que se "
                        "puede crear, subir o activar en Meta; cambiarlos es decisión tuya. Confirma solo si lo has "
                        "decidido tú.")


def logica(e: dict):
    tool = e.get("tool_name", "")
    if e.get("hook_event_name") != "PreToolUse" or tool not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        return None
    entrada = e.get("tool_input") or {}
    ruta_txt = str(entrada.get("file_path") or entrada.get("notebook_path") or "")
    if not ruta_txt:
        return None
    raiz = L.raiz()
    ruta = pathlib.Path(ruta_txt)
    if not ruta.is_absolute():
        ruta = raiz / ruta
    topes = decision_topes(tool, entrada, ruta, raiz)
    if _excluida(ruta, raiz):
        return topes
    texto = _texto_nuevo(entrada, tool)
    if not texto:
        return topes
    pii = L.buscar_pii(texto)
    columnas = columnas_pii(texto)
    if not (pii["emails"] or pii["telefonos"] or columnas):
        return topes
    hallado = []
    if pii["emails"]:
        hallado.append(f"{pii['emails']} email(s)")
    if pii["telefonos"]:
        hallado.append(f"{pii['telefonos']} teléfono(s)")
    if columnas:
        hallado.append("una tabla con columnas de datos personales (" + ", ".join(sorted(set(columnas))[:5]) + ")")
    try:
        rel = ruta.resolve().relative_to(raiz.resolve())
    except (ValueError, OSError):
        rel = ruta
    m = re.match(r"clientes[/\\]([a-z0-9][a-z0-9-]*)", str(rel))
    destino = f"clientes/{m.group(1)}/privado/" if m else "clientes/<cliente>/privado/"
    motivo = (f"Datos personales (RGPD): vas a escribir {' y '.join(hallado)} en {rel}, que no está en privado/. "
              f"Guarda los datos de personas en {destino} y deja aquí solo IDs y agregados (por anuncio, por semana). "
              "Confirma solo si son datos tuyos o de ejemplo.")
    if topes:
        motivo = topes["hookSpecificOutput"]["permissionDecisionReason"] + " Además: " + motivo
    return L.pre("ask", motivo)


def al_fallar(e: dict):
    """Si el hook falla al escribir una ficha, pregunta: podría ser un cambio de topes que no ha podido comprobar."""
    entrada = e.get("tool_input") or {}
    ruta = str(entrada.get("file_path") or "").replace("\\", "/")
    if e.get("hook_event_name") == "PreToolUse" and re.search(r"(^|/)clientes/[^/]+/ficha\.md$", ruta):
        return L.pre("ask", "No he podido comprobar si esta edición cambia los topes de gasto de la ficha (fallo "
                            "interno de datos_personales; el detalle queda en logs/hooks.jsonl). Confirma solo si "
                            "no toca `topes` o si el cambio es decisión tuya.")
    return None


def main() -> int:
    return L.ejecutar(HOOK, logica, al_fallar)


if __name__ == "__main__":
    sys.exit(main())
