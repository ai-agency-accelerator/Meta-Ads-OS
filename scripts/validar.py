#!/usr/bin/env python3
"""Valida el producto Meta Ads OS antes de publicarlo (contrato §13). Solo biblioteca estándar, Python ≥ 3.10.

Comprueba:
  cifras      50 skills, 20 agentes, 10 hooks, 5 workflows, 25 herramientas y 2 estilos, con los nombres del contrato
  cabeceras   skills, agentes, estilos, workflows, hooks (solo biblioteca estándar), herramientas y settings.json
  enlaces     enlaces internos de la KB, rutas `meta-ads-kb/...` citadas fuera de ella y enlaces de la documentación
  claude-md   que todo lo citado en CLAUDE.md (skills, agentes, rutas, cifras) exista
  fugas       rutas personales, IDs reales, emails, teléfonos, tokens, datos de la instancia versionados y,
              si existe, la lista negra local de nombres (contexto/fugas.txt, que git no sube)

Uso:
  python3 scripts/validar.py [--json] [--solo cifras,cabeceras,enlaces,claude-md,fugas] [--todo]
                             [--lista-negra ARCHIVO] [--raiz RUTA]

Lista negra: un término por línea (sin distinguir mayúsculas; `/regex/` para expresiones regulares; `#` comenta;
`!patrón` exime archivos, p. ej. `!LICENSE`). Sirve para que quien publica busque sus nombres propios sin
escribirlos en el producto.

Salida: 0 sin fallos (puede haber avisos) · 1 hay fallos · 2 no se puede ejecutar.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from dataclasses import asdict, dataclass

# ─────────────────────────────── contrato §2 ───────────────────────────────
SKILLS = {
    "Entradas": ["empezar", "hoy", "pregunta", "siguiente-anuncio"],
    "Sistema": ["menu", "doctor", "actualizar", "conectar", "motor"],
    "F0": ["cliente-nuevo", "economia", "oferta", "disenar-funnel", "iman-de-leads"],
    "F1": ["configurar-meta", "implementar-capi", "audiencias", "landing", "construir-landing",
           "formulario-instantaneo"],
    "F2": ["competencia", "voz-cliente"],
    "F3": ["brief-creativo", "producir-video", "producir-estatico", "variantes", "revisar-anuncio",
           "analisis-creativo", "casos-y-creadores", "organico-a-anuncios"],
    "F4": ["lanzar-campana", "publicar-anuncios", "test-creativo", "webinar"],
    "F5": ["brief-diario", "informe-semanal", "revision-mensual", "diagnostico", "ejecutar-cambio", "embudo",
           "rescate-cuenta", "reglas-automaticas", "seguimiento-leads", "anuncios-por-etapa"],
    "F6": ["escalar", "auditoria"],
    "Agencia": ["informe-cliente", "auditoria-express", "entrenar", "novedades-meta"],
}
AGENTES = ["analista-meta", "analista-cuantitativo", "auditor-cuenta", "operador-meta", "especialista-tracking",
           "ingeniero-capi", "especialista-funnel", "especialista-crm", "estratega-creativo", "redactor-anuncios",
           "investigador-competencia", "productor-ugc", "editor-video", "disenador-estaticos", "critico-creativo",
           "revisor-politicas", "revisor-estrategia", "gestor-cliente", "mentor-meta", "curador-conocimiento"]
HOOKS = ["meta_guard", "motor_guard", "ghl_guard", "stripe_guard", "eventos_guard", "control_publicacion",
         "datos_personales", "secretos", "registro_obligatorio", "contexto_sesion"]
WORKFLOWS = ["auditoria-profunda", "investigacion-mercado", "estudio-creativo", "lote-creativo",
             "lanzamiento-completo"]
HERRAMIENTAS = ["ad_library", "economia", "estadistica", "ig_competidores", "landing_check", "motor_proyectos",
                "reddit_pulso", "transcribir", "meta_ads", "ghl", "stripe_datos", "capi", "nomenclatura",
                "registro_creativo", "embudo", "estado", "notificar", "render", "editar_video", "doctor",
                "reglas_meta", "elementos_creativos", "paginas", "formularios_meta", "audiencias_meta"]
ESTILOS = ["profesor", "operador"]
CIFRAS = {"skills": 50, "agentes": 20, "hooks": 10, "workflows": 5, "herramientas": 25, "estilos": 2}
CATALOGO = {"skills": "skills.md", "agentes": "agentes.md", "hooks": "hooks.md", "workflows": "workflows.md",
            "herramientas": "herramientas.md", "estilos": "agentes.md"}

RENOMBRADAS = {"meta-conectar": "conectar", "pulso": "brief-diario", "producir-ugc": "producir-video",
               "variantes-ugc": "variantes", "actualizar-kb": "novedades-meta",
               "ugc-creative-studio": "estudio-creativo"}
SIN_INVOCACION = {"lanzar-campana", "ejecutar-cambio", "publicar-anuncios", "producir-video", "actualizar", "menu",
                  "reglas-automaticas", "formulario-instantaneo", "anuncios-por-etapa"}
UNICO_QUE_ESCRIBE = "operador-meta"
MODELOS = {"inherit", "sonnet"}
MAX_DESCRIPCION = 350

INSTANCIA = ("contexto/", "clientes/", "aprendizajes/", "logs/", "informes/", ".env")
INSTANCIA_VERSIONABLE = {"contexto/README.md", "clientes/README.md", "aprendizajes/README.md"}
COMANDOS_CLAUDE_CODE = {"mcp", "help", "clear", "config", "login", "logout", "model", "output-style", "agents",
                        "hooks", "permissions", "memory", "init", "doctor-claude", "status", "cost", "compact",
                        "resume", "review", "terminal-setup", "ide", "plugin", "context", "export", "add-dir"}

EXT_TEXTO = {".md", ".py", ".js", ".mjs", ".json", ".jsonl", ".sh", ".yml", ".yaml", ".toml", ".txt", ".html",
             ".css", ".csv", ".cfg", ".ini", ".example", ".ejemplo", ".lock", ".gitignore", ""}
DIRS_IGNORADOS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache",
                  ".ruff_cache", ".uv-cache"}


# ─────────────────────────────── resultados ───────────────────────────────
@dataclass
class R:
    seccion: str
    nivel: str          # ok | aviso | falla
    mensaje: str
    archivo: str = ""
    linea: int = 0


class Informe:
    def __init__(self) -> None:
        self.r: list[R] = []

    def ok(self, s, m, a="", l=0):
        self.r.append(R(s, "ok", m, a, l))

    def aviso(self, s, m, a="", l=0):
        self.r.append(R(s, "aviso", m, a, l))

    def falla(self, s, m, a="", l=0):
        self.r.append(R(s, "falla", m, a, l))


# ─────────────────────────────── utilidades ───────────────────────────────
def rel(raiz: pathlib.Path, p: pathlib.Path) -> str:
    try:
        return p.relative_to(raiz).as_posix()
    except ValueError:
        return p.name


def leer(p: pathlib.Path) -> str | None:
    try:
        datos = p.read_bytes()
    except OSError:
        return None
    if b"\x00" in datos[:4096]:
        return None
    return datos.decode("utf-8", errors="replace")


def archivos_producto(raiz: pathlib.Path) -> list[pathlib.Path]:
    """Lo que se versionaría: `git ls-files` (respeta .gitignore) o, sin git, un recorrido sin la instancia."""
    if shutil.which("git") and (raiz / ".git").exists():
        try:
            r = subprocess.run(["git", "-C", str(raiz), "ls-files", "-z", "--cached", "--others",
                                "--exclude-standard"], capture_output=True, timeout=60)
            if r.returncode == 0:
                vistos = sorted({x for x in r.stdout.decode("utf-8", "replace").split("\0") if x})
                return [raiz / x for x in vistos if (raiz / x).is_file()]
        except (OSError, subprocess.SubprocessError):
            pass
    salida = []
    for base, dirs, files in os.walk(raiz):
        b = pathlib.Path(base)
        dirs[:] = [d for d in dirs if d not in DIRS_IGNORADOS
                   and not (b == raiz and d in ("contexto", "clientes", "aprendizajes", "logs", "informes"))
                   and not (b.name == "motor-ia" and d in ("data", "logs"))]
        for f in files:
            if b == raiz and (f == ".env" or f.startswith(".env.")):
                continue
            salida.append(b / f)
    for readme in INSTANCIA_VERSIONABLE:
        if (raiz / readme).is_file():
            salida.append(raiz / readme)
    return sorted(set(salida))


def es_texto(p: pathlib.Path) -> bool:
    return p.suffix.lower() in EXT_TEXTO or p.name in ("LICENSE", "CLAUDE.md", "README.md")


def leer_cabecera(texto: str) -> tuple[dict | None, str]:
    """Cabecera YAML simple: `clave: valor`, cadenas con comillas, bloques `>`/`|` y listas `- x`."""
    lineas = texto.splitlines()
    if not lineas or lineas[0].strip() != "---":
        return None, "no empieza por una cabecera '---'"
    try:
        fin = next(i for i in range(1, len(lineas)) if lineas[i].strip() == "---")
    except StopIteration:
        return None, "la cabecera no se cierra con '---'"
    datos: dict = {}
    i = 1
    while i < fin:
        linea = lineas[i]
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", linea)
        if not m:
            i += 1
            continue
        clave, valor = m.group(1), m.group(2).strip()
        bloque = []
        j = i + 1
        while j < fin and (lineas[j].startswith((" ", "\t")) or lineas[j].strip().startswith("- ")):
            bloque.append(lineas[j].strip())
            j += 1
        if valor in ("", ">", ">-", ">+", "|", "|-", "|+"):
            if bloque and all(b.startswith("- ") for b in bloque if b):
                datos[clave] = [b[2:].strip().strip("'\"") for b in bloque if b]
            else:
                datos[clave] = (" " if valor.startswith(">") or valor == "" else "\n").join(bloque).strip()
        else:
            if valor.startswith('"') and valor.endswith('"') and len(valor) >= 2:
                valor = valor[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            elif valor.startswith("'") and valor.endswith("'") and len(valor) >= 2:
                valor = valor[1:-1].replace("''", "'")
            elif " #" in valor:
                valor = valor.split(" #", 1)[0].strip()
            datos[clave] = valor
        i = j
    return datos, ""


def lista_tools(valor) -> list[str]:
    if isinstance(valor, list):
        return [t.strip() for t in valor if t.strip()]
    if isinstance(valor, str):
        v = valor.strip().strip("[]")
        return [t.strip().strip("'\"") for t in v.split(",") if t.strip()]
    return []


def similitud(a: str, b: str) -> float:
    pa = {w for w in re.findall(r"\w{4,}", a.lower())}
    pb = {w for w in re.findall(r"\w{4,}", b.lower())}
    return len(pa & pb) / max(1, len(pa | pb))


# ─────────────────────────────── 1. cifras ───────────────────────────────
def inventario(raiz: pathlib.Path) -> dict[str, list[str]]:
    c = raiz / ".claude"
    skills = sorted(d.name for d in (c / "skills").iterdir() if d.is_dir()) if (c / "skills").is_dir() else []
    return {
        "skills": skills,
        "agentes": sorted(p.stem for p in (c / "agents").glob("*.md")),
        "hooks": sorted(p.stem for p in (c / "hooks").glob("[!_]*.py")),
        "workflows": sorted(p.stem for p in (c / "workflows").glob("*.js")),
        "herramientas": sorted(p.stem for p in (raiz / "herramientas").glob("[!_]*.py")),
        "estilos": sorted(p.stem for p in (c / "output-styles").glob("*.md")),
    }


def comprobar_cifras(raiz: pathlib.Path, inf: Informe) -> None:
    s = "cifras"
    esperado = {"skills": [n for g in SKILLS.values() for n in g], "agentes": AGENTES, "hooks": HOOKS,
                "workflows": WORKFLOWS, "herramientas": HERRAMIENTAS, "estilos": ESTILOS}
    hay = inventario(raiz)
    for tipo, nombres in esperado.items():
        assert len(nombres) == CIFRAS[tipo], tipo
        presentes = set(hay[tipo])
        faltan = [n for n in nombres if n not in presentes]
        sobran = [n for n in hay[tipo] if n not in nombres]
        validos = len(nombres) - len(faltan)
        if faltan:
            inf.falla(s, f"{tipo}: {validos}/{CIFRAS[tipo]} · faltan: {', '.join(faltan)}")
        else:
            inf.ok(s, f"{tipo}: {CIFRAS[tipo]}/{CIFRAS[tipo]}")
        for n in sobran:
            if n in RENOMBRADAS:
                inf.falla(s, f"{tipo}: sobra «{n}» (renombrada a «{RENOMBRADAS[n]}»): va a «A borrar»")
            else:
                inf.falla(s, f"{tipo}: sobra «{n}», que no está en el contrato §2")
    if (raiz / ".claude" / "skills").is_dir():
        for d in sorted((raiz / ".claude" / "skills").iterdir()):
            if d.is_dir() and not (d / "SKILL.md").is_file():
                inf.falla(s, f"La carpeta de skill {d.name}/ no tiene SKILL.md", rel(raiz, d))
    catalogo = raiz / "docs" / "catalogo"
    if catalogo.is_dir():                    # la documentación tiene que cubrir todo el contrato, sin huecos
        for tipo, archivo in CATALOGO.items():
            texto = leer(catalogo / archivo)
            if texto is None:
                inf.falla(s, f"Falta docs/catalogo/{archivo} ({tipo})")
                continue
            ausentes = [n for n in esperado[tipo]
                        if not re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", texto)]
            if ausentes:
                inf.falla(s, f"docs/catalogo/{archivo} no documenta {tipo}: {', '.join(ausentes)}",
                          f"docs/catalogo/{archivo}")


# ─────────────────────────────── 2. cabeceras ───────────────────────────────
VERBOS_META = {"create", "update", "delete", "activate", "boost", "connect", "disconnect", "pause", "duplicate",
               "upload", "remove", "add", "set", "publish"}
VERBOS_STRIPE = {"create", "update", "delete", "cancel", "refund", "finalize", "void", "pay", "send", "capture",
                 "close", "reject", "reverse", "resume", "pause"}


def _escribe(tool: str, prefijo: str, verbos: set[str]) -> bool:
    """`mcp__meta-ads__ads_pixel_event_create` → True. Mira palabras completas (dataset no es «set»)."""
    if tool in (prefijo.rstrip("_"), prefijo + "*"):
        return True
    return tool.startswith(prefijo) and bool(set(re.split(r"[_\-*]+", tool[len(prefijo):])) & verbos)


def comprobar_cabeceras(raiz: pathlib.Path, inf: Informe) -> None:
    s = "cabeceras"
    c = raiz / ".claude"
    descripciones: dict[str, str] = {}

    for f in sorted((c / "skills").glob("*/SKILL.md")):
        nombre, r_ = f.parent.name, rel(raiz, f)
        cab, err = leer_cabecera(leer(f) or "")
        if cab is None:
            inf.falla(s, f"skill {nombre}: {err}", r_)
            continue
        if cab.get("name") != nombre:
            inf.falla(s, f"skill {nombre}: name es «{cab.get('name', '')}» y debe ser «{nombre}»", r_)
        desc = str(cab.get("description", "")).strip()
        if not desc:
            inf.falla(s, f"skill {nombre}: falta description", r_)
        elif len(desc) > MAX_DESCRIPCION:
            inf.falla(s, f"skill {nombre}: description de {len(desc)} caracteres (máximo {MAX_DESCRIPCION})", r_)
        else:
            descripciones[nombre] = desc
        if "argument-hint" not in cab:
            inf.aviso(s, f"skill {nombre}: falta argument-hint (contrato §11)", r_)
        dmi = str(cab.get("disable-model-invocation", "")).lower() == "true"
        if nombre in SIN_INVOCACION and not dmi:
            inf.falla(s, f"skill {nombre}: escribe, gasta o actualiza: necesita disable-model-invocation: true", r_)
        elif dmi and nombre not in SIN_INVOCACION:
            inf.aviso(s, f"skill {nombre}: tiene disable-model-invocation sin estar en la lista del contrato §11", r_)
    vistos = sorted(descripciones.items())
    for i, (a, da) in enumerate(vistos):
        for b, db in vistos[i + 1:]:
            if da == db:
                inf.falla(s, f"skills {a} y {b}: misma description")
            elif similitud(da, db) > 0.6:
                inf.aviso(s, f"skills {a} y {b}: descriptions casi iguales (¿se solapan?)")

    for f in sorted((c / "agents").glob("*.md")):
        nombre, r_ = f.stem, rel(raiz, f)
        cab, err = leer_cabecera(leer(f) or "")
        if cab is None:
            inf.falla(s, f"agente {nombre}: {err}", r_)
            continue
        if cab.get("name") != nombre:
            inf.falla(s, f"agente {nombre}: name es «{cab.get('name', '')}» y debe ser «{nombre}»", r_)
        if not str(cab.get("description", "")).strip():
            inf.falla(s, f"agente {nombre}: falta description", r_)
        tools = lista_tools(cab.get("tools"))
        if not tools:
            inf.falla(s, f"agente {nombre}: falta tools (lista explícita, contrato §11)", r_)
        elif any(t in ("*", "All") for t in tools):
            inf.falla(s, f"agente {nombre}: tools no puede ser «*»: lista explícita", r_)
        modelo = str(cab.get("model", "")).strip()
        if modelo not in MODELOS:
            inf.falla(s, f"agente {nombre}: model «{modelo or '(vacío)'}» (usa inherit o sonnet)", r_)
        if nombre != UNICO_QUE_ESCRIBE:
            for t in tools:
                if _escribe(t, "mcp__meta-ads__", VERBOS_META):
                    inf.falla(s, f"agente {nombre}: «{t}» escribe en Meta y solo {UNICO_QUE_ESCRIBE} escribe", r_)
                elif _escribe(t, "mcp__stripe__", VERBOS_STRIPE):
                    inf.falla(s, f"agente {nombre}: «{t}» escribe en Stripe (Stripe es de solo lectura)", r_)
                elif t in ("mcp__ghl", "mcp__ghl__*"):
                    inf.aviso(s, f"agente {nombre}: «{t}» da todo GHL; lista las herramientas concretas", r_)

    for f in sorted((c / "output-styles").glob("*.md")):
        cab, err = leer_cabecera(leer(f) or "")
        if cab is None:
            inf.falla(s, f"estilo {f.stem}: {err}", rel(raiz, f))
        elif not cab.get("name") or not cab.get("description"):
            inf.falla(s, f"estilo {f.stem}: necesita name y description", rel(raiz, f))

    comprobar_workflows(raiz, inf)
    comprobar_python(raiz, inf)
    comprobar_settings(raiz, inf)


def _literal_meta(src: str) -> tuple[str | None, str]:
    """Extrae el objeto de `export const meta = {...}` y dice si es un literal puro (sin variables ni llamadas)."""
    m = re.search(r"export\s+const\s+meta\s*=\s*\{", src)
    if not m:
        return None, "no exporta `meta`"
    i, prof, esqueleto, n = m.end() - 1, 0, [], len(src)
    while i < n:
        ch = src[i]
        if ch in "'\"`":
            cierre, j = ch, i + 1
            while j < n and src[j] != cierre:
                if src[j] == "\\":
                    j += 1
                elif cierre == "`" and src.startswith("${", j):
                    return None, "meta usa una plantilla con ${…}: tiene que ser un literal"
                j += 1
            esqueleto.append('""')
            i = j + 1
            continue
        if src.startswith("//", i):
            i = src.find("\n", i)
            i = n if i < 0 else i
            continue
        if src.startswith("/*", i):
            k = src.find("*/", i + 2)
            i = n if k < 0 else k + 2
            continue
        esqueleto.append(ch)
        if ch == "{":
            prof += 1
        elif ch == "}":
            prof -= 1
            if prof == 0:
                break
        i += 1
    texto = "".join(esqueleto)
    resto = re.sub(r'(""|[A-Za-z_$][\w$]*)\s*:', "", texto)
    resto = re.sub(r'""|\btrue\b|\bfalse\b|\bnull\b|-?\d+(\.\d+)?', "", resto)
    resto = re.sub(r"[\s{}\[\],]", "", resto)
    if resto:
        return texto, f"meta no es un literal puro (contiene «{resto[:30]}»)"
    return texto, ""


def _sin_cadenas_js(src: str) -> str:
    """Vacía cadenas y comentarios de un JS conservando los saltos de línea (para buscar código, no texto)."""
    fuera, i, n = [], 0, len(src)
    while i < n:
        ch = src[i]
        if ch in "'\"`":
            j = i + 1
            while j < n and src[j] != ch:
                j += 2 if src[j] == "\\" else 1
            fuera.append(ch + "\n" * src.count("\n", i, j + 1) + ch)
            i = j + 1
        elif src.startswith("//", i):
            k = src.find("\n", i)
            i = n if k < 0 else k
        elif src.startswith("/*", i):
            k = src.find("*/", i + 2)
            k = n if k < 0 else k + 2
            fuera.append("\n" * src.count("\n", i, k))
            i = k
        else:
            fuera.append(ch)
            i += 1
    return "".join(fuera)


def comprobar_workflows(raiz: pathlib.Path, inf: Informe) -> None:
    s = "cabeceras"
    node = shutil.which("node")
    archivos = sorted((raiz / ".claude" / "workflows").glob("*.js"))
    if archivos and not node:
        inf.aviso(s, "node no está instalado: no compruebo la sintaxis de los workflows")
    for f in archivos:
        r_, src = rel(raiz, f), leer(f) or ""
        esqueleto, err = _literal_meta(src)
        if err:
            inf.falla(s, f"workflow {f.stem}: {err}", r_)
        elif esqueleto is not None:
            faltan = [k for k, patron in (("name", r"\bname\s*:"), ("description", r"\bdescription\s*:"),
                                          ("phases", r"\bphases\s*:\s*\[")) if not re.search(patron, esqueleto)]
            if faltan:
                inf.falla(s, f"workflow {f.stem}: a meta le falta {', '.join(faltan)}", r_)
        # El runtime no tiene módulos ni proceso, y reanuda repitiendo el guion: nada de azar ni de reloj sin argumentos.
        codigo = _sin_cadenas_js(src)
        for patron, que, grave in ((r"\brequire\s*\(", "require()", True), (r"(?m)^\s*import\s", "import", True),
                                   (r"\bprocess\.(?:env|argv|exit|cwd)\b", "process", True),
                                   (r"\bDate\.now\s*\(", "Date.now()", False),
                                   (r"\bMath\.random\s*\(", "Math.random()", False),
                                   (r"\bnew\s+Date\s*\(\s*\)", "new Date() sin argumentos", False)):
            m = re.search(patron, codigo)
            if m:
                linea = codigo.count("\n", 0, m.start()) + 1
                if grave:
                    inf.falla(s, f"workflow {f.stem}: usa {que}, que el runtime de workflows no tiene", r_, linea)
                else:
                    inf.aviso(s, f"workflow {f.stem}: usa {que}; al reanudar daría otro valor", r_, linea)
        nm = re.search(r"export\s+const\s+meta\s*=\s*\{[^}]*?\bname\s*:\s*(['\"])(.*?)\1", src, re.S)
        if nm and nm.group(2) != f.stem:
            inf.falla(s, f"workflow {f.stem}: meta.name es «{nm.group(2)}» y debe ser «{f.stem}»", r_)
        if not node:
            continue
        cuerpo = re.sub(r"\bexport\s+const\s+meta\b", "const meta", src, count=1)
        with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False, encoding="utf-8") as tmp:
            tmp.write("(async function __workflow__(args) {\n" + cuerpo + "\n})\n")
        try:
            r = subprocess.run([node, "--check", tmp.name], capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                lineas = [x for x in (r.stderr or "").splitlines() if x.strip()]
                donde = re.search(r":(\d+)\s*$", lineas[0]) if lineas else None
                linea = int(donde.group(1)) - 1 if donde else 0
                motivo = next((x for x in lineas if "Error" in x), "error de sintaxis")
                inf.falla(s, f"workflow {f.stem}: {motivo.strip()}", r_, linea)
        except (OSError, subprocess.SubprocessError) as e:
            inf.aviso(s, f"workflow {f.stem}: no he podido ejecutar node ({type(e).__name__})", r_)
        finally:
            os.unlink(tmp.name)


def comprobar_python(raiz: pathlib.Path, inf: Informe) -> None:
    s = "cabeceras"
    stdlib = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
    dir_hooks = raiz / ".claude" / "hooks"
    locales = {p.stem for p in dir_hooks.glob("*.py")}
    for f in sorted(list(dir_hooks.glob("*.py")) + list((raiz / "herramientas").glob("*.py"))
                    + list((raiz / "scripts").glob("*.py"))):
        r_, src = rel(raiz, f), leer(f) or ""
        try:
            arbol = ast.parse(src, filename=r_)
        except SyntaxError as e:
            inf.falla(s, f"{f.name}: error de sintaxis ({e.msg})", r_, e.lineno or 0)
            continue
        if f.parent != dir_hooks or not stdlib:
            continue
        for nodo in ast.walk(arbol):
            mods = []
            if isinstance(nodo, ast.Import):
                mods = [a.name for a in nodo.names]
            elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
                mods = [nodo.module]
            for mod in mods:
                raiz_mod = mod.split(".")[0]
                if raiz_mod not in stdlib and raiz_mod not in locales:
                    inf.falla(s, f"hook {f.stem}: importa «{mod}»; los hooks solo usan la biblioteca estándar "
                                 "(contrato §10)", r_, nodo.lineno)


def comprobar_settings(raiz: pathlib.Path, inf: Informe) -> None:
    s = "cabeceras"
    f = raiz / ".claude" / "settings.json"
    if not f.is_file():
        inf.falla(s, "falta .claude/settings.json (permisos y hooks)")
        return
    texto = leer(f) or ""
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        inf.falla(s, f"settings.json no es JSON válido ({e.msg}, línea {e.lineno})", rel(raiz, f), e.lineno)
        return
    citados = set(re.findall(r"\.claude/hooks/([\w-]+)\.py", texto))
    for h in sorted(citados):
        if not (raiz / ".claude" / "hooks" / f"{h}.py").is_file():
            inf.falla(s, f"settings.json lanza el hook {h}.py, que no existe", rel(raiz, f))
    for p in sorted((raiz / ".claude" / "hooks").glob("[!_]*.py")):
        if p.stem not in citados:
            inf.aviso(s, f"el hook {p.stem} no está conectado en settings.json", rel(raiz, p))
    for ruta in sorted(set(re.findall(r"herramientas/([\w-]+\.py)", texto))):
        if not (raiz / "herramientas" / ruta).is_file():
            inf.falla(s, f"settings.json cita herramientas/{ruta}, que no existe", rel(raiz, f))
    deny = " ".join((datos.get("permissions") or {}).get("deny") or [])
    if ".env" not in deny:
        inf.aviso(s, "settings.json no deniega leer .env", rel(raiz, f))


# ─────────────────────────────── 3. enlaces ───────────────────────────────
ENLACE_MD = re.compile(r"(?<!!)\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REF_KB = re.compile(r"meta-ads-kb/[\w./\-ñáéíóúü]+")
REF_KB_CORTA = re.compile(r"(?<![\w./-])((?:0\d|1[0-6])-[a-z0-9-]+/[\w.\-]+\.(?:md|py))")
EXCLUIR_DOCS = ("docs/desarrollo/notas/",)


def _sin_codigo(texto: str) -> str:
    """Quita bloques ``` para no tomar como enlaces los ejemplos de código (conserva los saltos de línea)."""
    return re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), texto, flags=re.S)


def _slug_github(titulo: str) -> str:
    t = re.sub(r"[`*_~]|\[|\]\([^)]*\)", "", titulo.strip().lower())
    return re.sub(r"[^\w\- ]", "", t).replace(" ", "-")


def _anclas(p: pathlib.Path) -> set[str]:
    texto = _sin_codigo(leer(p) or "")
    return {_slug_github(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", texto, re.M)}


def _comprobar_enlaces_md(raiz: pathlib.Path, f: pathlib.Path, inf: Informe, s: str, cache: dict) -> None:
    texto = _sin_codigo(leer(f) or "")
    for m in ENLACE_MD.finditer(texto):
        destino = m.group(1)
        if re.match(r"^[a-z][a-z0-9+.-]*:", destino, re.I) or "<" in destino or "{" in destino:
            continue
        ruta, _, ancla = destino.partition("#")
        linea = texto.count("\n", 0, m.start()) + 1
        objetivo = f if not ruta else (f.parent / urllib.parse.unquote(ruta))
        if not objetivo.exists():
            inf.falla(s, f"enlace roto: {destino}", rel(raiz, f), linea)
            continue
        if ancla and objetivo.suffix == ".md" and objetivo.is_file():
            if objetivo not in cache:
                cache[objetivo] = _anclas(objetivo)
            if ancla.lower() not in cache[objetivo]:
                inf.aviso(s, f"el ancla #{ancla} no coincide con ningún título de {rel(raiz, objetivo)}",
                          rel(raiz, f), linea)


def comprobar_enlaces(raiz: pathlib.Path, inf: Informe, archivos: list[pathlib.Path]) -> None:
    s = "enlaces"
    kb = raiz / "meta-ads-kb"
    cache: dict = {}
    fallos_antes = sum(1 for x in inf.r if x.nivel == "falla")
    n_kb = n_ref = n_doc = 0
    for f in archivos:
        r_ = rel(raiz, f)
        if r_.startswith("meta-ads-kb/") and f.suffix == ".md":
            n_kb += 1
            _comprobar_enlaces_md(raiz, f, inf, s, cache)
    for f in archivos:
        r_ = rel(raiz, f)
        if r_.startswith(("meta-ads-kb/", "tests/")) or r_.startswith(EXCLUIR_DOCS) or not es_texto(f):
            continue
        if r_ in ("scripts/validar.py",):
            continue
        texto = leer(f)
        if texto is None:
            continue
        if f.suffix == ".md":
            n_doc += 1
            _comprobar_enlaces_md(raiz, f, inf, s, cache)
        for m in REF_KB.finditer(texto):
            ruta = m.group(0).rstrip(".,:;")
            if "<" in ruta or "*" in ruta:
                continue
            n_ref += 1
            if not (raiz / ruta).exists():
                inf.falla(s, f"cita {ruta}, que no existe", r_, texto.count("\n", 0, m.start()) + 1)
        for m in REF_KB_CORTA.finditer(texto):
            ruta = m.group(1)
            if texto[max(0, m.start() - 12):m.start()].endswith("meta-ads-kb/"):
                continue
            n_ref += 1
            if not (kb / ruta).exists() and not (raiz / ruta).exists():
                inf.falla(s, f"cita {ruta} (relativa a meta-ads-kb/), que no existe", r_,
                          texto.count("\n", 0, m.start()) + 1)
    if sum(1 for x in inf.r if x.nivel == "falla") == fallos_antes:
        inf.ok(s, f"enlaces correctos: {n_kb} archivos de la KB, {n_doc} documentos y {n_ref} citas a la KB")


# ─────────────────────────────── 4. CLAUDE.md ───────────────────────────────
PATRON_CIFRAS = {"skills": r"(\d+)\s+(?:comandos|skills)", "agentes": r"(\d+)\s+agentes",
                 "hooks": r"(\d+)\s+(?:guardas|hooks)", "workflows": r"(\d+)\s+(?:modos profundos|workflows)",
                 "herramientas": r"(\d+)\s+(?:scripts|herramientas)"}


def _es_instancia(ruta: str) -> bool:
    return ruta.startswith(INSTANCIA) or ruta in ("contexto", "clientes", "aprendizajes", "logs", "informes")


def comprobar_claude_md(raiz: pathlib.Path, inf: Informe) -> None:
    s = "claude-md"
    f = raiz / "CLAUDE.md"
    texto = leer(f)
    if texto is None:
        inf.falla(s, "falta CLAUDE.md")
        return
    hay = inventario(raiz)
    skills, agentes = set(hay["skills"]), set(hay["agentes"])
    antes = len([x for x in inf.r if x.nivel == "falla"])

    for m in re.finditer(r"^@(\S+)", texto, re.M):
        ruta = m.group(1)
        plantilla = raiz / "plantillas" / ruta if _es_instancia(ruta) else raiz / ruta
        if not plantilla.exists():
            inf.falla(s, f"importa @{ruta} y no existe {rel(raiz, plantilla)} (el instalador lo crea desde ahí)",
                      "CLAUDE.md", texto.count("\n", 0, m.start()) + 1)

    for m in re.finditer(r"`([^`\n]+)`", texto):
        token = m.group(1).strip()
        linea = texto.count("\n", 0, m.start()) + 1
        cmd = re.match(r"^/([a-z][a-z0-9-]*)", token)
        if cmd:
            nombre = cmd.group(1)
            if nombre not in skills and nombre not in COMANDOS_CLAUDE_CODE:
                inf.falla(s, f"cita /{nombre}, que no es ninguna skill", "CLAUDE.md", linea)
            continue
        if re.fullmatch(r"[a-z]+(?:-[a-z]+)+", token):
            if token in AGENTES and token not in agentes:
                inf.falla(s, f"cita el agente {token}, que no existe en .claude/agents/", "CLAUDE.md", linea)
            elif token not in AGENTES and token not in skills and token not in WORKFLOWS:
                inf.aviso(s, f"cita «{token}», que no es ni skill, ni agente, ni workflow", "CLAUDE.md", linea)
            continue
        if re.fullmatch(r"[\w.@-]+(?:/[\w.@<>*-]*)+", token) or re.fullmatch(r"\.[\w./-]+/[\w.-]*", token):
            ruta = token.split()[0].rstrip("/")
            if any(c in ruta for c in "<>*") or "AAAA" in ruta or _es_instancia(ruta) or ruta.startswith(".env"):
                continue
            if not ((raiz / ruta).exists() or (raiz / "meta-ads-kb" / ruta).exists()):
                inf.falla(s, f"cita la ruta {ruta}, que no existe", "CLAUDE.md", linea)

    for tipo, patron in PATRON_CIFRAS.items():
        for m in re.finditer(patron, texto):
            if int(m.group(1)) != CIFRAS[tipo]:
                inf.falla(s, f"dice «{m.group(0)}» y el contrato fija {CIFRAS[tipo]} {tipo}", "CLAUDE.md",
                          texto.count("\n", 0, m.start()) + 1)
    readme = leer(raiz / "README.md")
    if readme:
        for tipo, patron in PATRON_CIFRAS.items():
            for m in re.finditer(patron, readme):
                if int(m.group(1)) != CIFRAS[tipo]:
                    inf.falla(s, f"README.md dice «{m.group(0)}» y el contrato fija {CIFRAS[tipo]} {tipo}",
                              "README.md", readme.count("\n", 0, m.start()) + 1)
    if len([x for x in inf.r if x.nivel == "falla"]) == antes:
        inf.ok(s, "todo lo citado en CLAUDE.md existe y las cifras cuadran")


# ─────────────────────────────── 5. fugas ───────────────────────────────
_U = "/" + "Users/"                       # construido así para que el validador no se detecte a sí mismo
_H = "/" + "home/"
MARCADORES = re.compile(r"x{3,}|X{3,}|<[^>]*>|\.\.\.|…|tu[_-]|TU_|ejemplo|example|dummy|falso|fake|prueba|"
                        r"placeholder|(.)\1{5,}", re.I)
PATRONES_FUGA: list[tuple[str, re.Pattern]] = [
    ("ruta personal", re.compile(re.escape(_U) + r"(?!<|\$|\{|tu[-_]?usuario\b|usuario\b|USUARIO\b|name\b|nombre\b)"
                                 r"[A-Za-z][\w.-]*")),
    ("ruta personal", re.compile(r"\b[A-Za-z]:\\+Users\\+(?!<|tu|usuario|USUARIO|name|nombre)[A-Za-z][\w.-]*")),
    ("ruta personal", re.compile(re.escape(_H) + r"(?!<|\$|\{|tu[-_]?usuario/|usuario/|user/|runner/|ubuntu/)"
                                 r"[a-z][\w.-]*/")),
    ("cuenta publicitaria", re.compile(r"\bact_(\d{10,})\b")),
    ("ID de Meta", re.compile(r"(?i)[\"']?\b(?:pixel|píxel|dataset|page|pagina|página|instagram|ig_user|ig|"
                              r"audience|audiencia|catalog|catalogo|catálogo|business|portfolio|ad_?account|"
                              r"campaign|campana|campaña|adset|conjunto|creative|creatividad)_?ids?\b[\"']?\s*[:=]\s*"
                              r"[\"']?(\d{12,})")),
    ("ID de Meta", re.compile(r"\"id\"\s*:\s*\"?(\d{14,})")),
    ("token de Meta", re.compile(r"\bEAA[A-Za-z0-9]{30,}")),
    ("clave de Stripe", re.compile(r"\b(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("clave de Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("token de GitHub", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("token de Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("webhook de Slack", re.compile(r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]{12,}")),
    ("token de Telegram", re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{30,}")),
    ("clave de IA", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_\-]{30,}")),
    ("token de GHL", re.compile(r"\bpit-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")),
    ("clave de AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("secreto en claro", re.compile(r"(?i)\b(?:token|secret|secreto|api[_-]?key|clave|password|contraseña)\b[\"']?"
                                    r"\s*[:=]\s*[\"']([A-Za-z0-9_\-./+=]{24,})[\"']")),
]
EMAIL = re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
TELEFONO = re.compile(r"(?<![\w+])\+\d{1,3}[ .-]?\(?\d{1,4}\)?(?:[ .-]?\d{2,4}){2,4}\b")
EMAILS_PERMITIDOS = {"noreply@business.facebook.com", "phish@fb.com", "john_smith@gmail.com", "git@github.com",
                     "noreply@github.com", "noreply@anthropic.com"}
DOMINIOS_PERMITIDOS = ("example.com", "example.org", "example.net", "ejemplo.com", "ejemplo.es", ".example",
                       ".test", ".invalid", ".local", "localhost", "users.noreply.github.com")
DOMINIOS_FICTICIOS = re.compile(r"(?:^|[.@-])(?:acme|nimbo|clinica-?sonrisa)(?:[.-]|$)")  # empresas del contrato §12
TERCEROS = ("LICENSE*", "NOTICE*", "CREDITS*", "*/vendor/*", "*OFL*", "*.min.js", "*/LICENSE*", "uv.lock",
            "*/uv.lock")


def _id_de_ejemplo(digitos: str) -> bool:
    """IDs de relleno (120000000000000123, 000…, 123456…): un ID real de Meta casi nunca tiene ≤5 cifras distintas de 0."""
    return len(set(digitos)) == 1 or digitos in "12345678901234567890" or set(digitos) <= {"0", "1"} \
        or digitos.endswith("0" * 8) or len(digitos) - digitos.count("0") <= 5


def _enmascarar(tipo: str, valor: str) -> str:
    if tipo.startswith(("token", "clave", "secreto", "webhook")):
        return valor[:4] + "…"
    if "@" in valor:
        usuario, _, dominio = valor.partition("@")
        return f"{usuario[:1]}***@{dominio}"
    return valor


def _lista_negra(ruta: pathlib.Path | None) -> tuple[list[tuple[str, re.Pattern]], list[str]]:
    if not ruta or not ruta.is_file():
        return [], []
    terminos, exentos = [], []
    for linea in (leer(ruta) or "").splitlines():
        t = linea.strip()
        if not t or t.startswith("#"):
            continue
        if t.startswith("!"):
            exentos.append(t[1:].strip())
        elif len(t) > 2 and t.startswith("/") and t.endswith("/"):
            terminos.append((t, re.compile(t[1:-1], re.I)))
        else:
            terminos.append((t, re.compile(r"(?<![\w])" + re.escape(t) + r"(?![\w])", re.I)))
    return terminos, exentos


def _coincide(r_: str, patrones) -> bool:
    return any(fnmatch.fnmatch(r_, p) or fnmatch.fnmatch(pathlib.PurePosixPath(r_).name, p) for p in patrones)


def comprobar_fugas(raiz: pathlib.Path, inf: Informe, archivos: list[pathlib.Path],
                    lista_negra: pathlib.Path | None) -> None:
    s = "fugas"
    antes = len([x for x in inf.r if x.nivel == "falla"])
    terminos, exentos = _lista_negra(lista_negra)
    revisados = 0
    for f in archivos:
        r_ = rel(raiz, f)
        if _es_instancia(r_) and r_ not in INSTANCIA_VERSIONABLE:
            inf.falla(s, f"{r_} es de la instancia y no debe versionarse (datos del operador)", r_)
            continue
        if not es_texto(f):
            continue
        texto = leer(f)
        if texto is None:
            continue
        revisados += 1
        tercero = _coincide(r_, TERCEROS)
        # Los tests de los detectores de datos personales necesitan emails y teléfonos con forma real: ahí son aviso.
        en_tests = r_.startswith("tests/") or "/tests/" in r_
        personales: list[str] = []
        for n, linea in enumerate(texto.splitlines(), 1):
            if len(linea) > 5000:
                linea = linea[:5000]
            for tipo, patron in PATRONES_FUGA:
                for m in patron.finditer(linea):
                    valor = m.group(m.lastindex or 0) if m.lastindex else m.group(0)
                    if tipo in ("cuenta publicitaria", "ID de Meta") and _id_de_ejemplo(valor):
                        continue
                    if tipo not in ("cuenta publicitaria", "ID de Meta", "ruta personal") \
                            and MARCADORES.search(m.group(0)):
                        continue
                    inf.falla(s, f"{tipo}: {_enmascarar(tipo, m.group(0))}", r_, n)
            if not tercero:
                for m in EMAIL.finditer(linea):
                    e = m.group(0).lower()
                    dominio = e.split("@", 1)[1]
                    if e in EMAILS_PERMITIDOS or dominio.endswith(DOMINIOS_PERMITIDOS) \
                            or DOMINIOS_FICTICIOS.search(dominio) or re.search(r"\.(png|jpe?g|gif|webp|svg)$", e):
                        continue
                    if en_tests:
                        personales.append(f"{n}")
                    else:
                        inf.falla(s, f"email: {_enmascarar('email', m.group(0))}", r_, n)
                for m in TELEFONO.finditer(linea):
                    digitos = re.sub(r"\D", "", m.group(0))
                    if len(digitos) < 9 or digitos.count("0") >= 5 or "555" in digitos or \
                            re.search(r"(\d)\1{4,}", digitos) or "12345678" in digitos or "23456789" in digitos:
                        continue
                    if en_tests:
                        personales.append(f"{n}")
                    else:
                        inf.falla(s, f"teléfono: {m.group(0)}", r_, n)
            if terminos and not _coincide(r_, exentos):
                for etiqueta, patron in terminos:
                    if patron.search(linea):
                        inf.falla(s, f"término de la lista negra «{etiqueta}»", r_, n)
        if personales:
            lineas = sorted(set(personales), key=int)
            inf.aviso(s, f"{len(personales)} email(s) o teléfono(s) con forma real en un test (líneas "
                         f"{', '.join(lineas[:8])}{'…' if len(lineas) > 8 else ''}): usa example.com y números "
                         "ficticios salvo que el test lo necesite", r_)
    if lista_negra and lista_negra.is_file():
        inf.ok(s, f"lista negra local aplicada ({len(terminos)} términos)")
    elif lista_negra:
        inf.aviso(s, f"no encuentro la lista negra {lista_negra.name}: sin ella no busco nombres propios")
    if len([x for x in inf.r if x.nivel == "falla"]) == antes:
        inf.ok(s, f"sin fugas en {revisados} archivos de texto")


# ─────────────────────────────── principal ───────────────────────────────
SECCIONES = ("cifras", "cabeceras", "enlaces", "claude-md", "fugas")
TITULOS = {"cifras": "Cifras (contrato §2)", "cabeceras": "Cabeceras y sintaxis", "enlaces": "Enlaces",
           "claude-md": "CLAUDE.md", "fugas": "Fugas"}


def validar(raiz: pathlib.Path, solo: list[str], lista_negra: pathlib.Path | None) -> Informe:
    inf = Informe()
    archivos = archivos_producto(raiz) if {"enlaces", "fugas"} & set(solo) else []
    if "cifras" in solo:
        comprobar_cifras(raiz, inf)
    if "cabeceras" in solo:
        comprobar_cabeceras(raiz, inf)
    if "enlaces" in solo:
        comprobar_enlaces(raiz, inf, archivos)
    if "claude-md" in solo:
        comprobar_claude_md(raiz, inf)
    if "fugas" in solo:
        comprobar_fugas(raiz, inf, archivos, lista_negra)
    return inf


def imprimir(inf: Informe, solo: list[str], todo: bool, limite: int = 40) -> None:
    print("Meta Ads OS · validación del producto\n")
    for s in solo:
        filas = [x for x in inf.r if x.seccion == s]
        print(f"== {TITULOS[s]}")
        for nivel, etiqueta in (("ok", "[OK]   "), ("falla", "[FALLA]"), ("aviso", "[AVISO]")):
            grupo = [x for x in filas if x.nivel == nivel]
            for x in grupo if todo else grupo[:limite]:
                donde = f" ({x.archivo}{':' + str(x.linea) if x.linea else ''})" if x.archivo else ""
                print(f"  {etiqueta} {x.mensaje}{donde}")
            if not todo and len(grupo) > limite:
                print(f"  …y {len(grupo) - limite} más (usa --todo para verlos)")
        print()
    fallos = sum(1 for x in inf.r if x.nivel == "falla")
    avisos = sum(1 for x in inf.r if x.nivel == "aviso")
    if fallos:
        print(f"Resultado: {fallos} fallos y {avisos} avisos. Arregla los fallos antes de publicar.")
    else:
        print(f"Resultado: sin fallos ({avisos} avisos). Listo para publicar.")


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--solo", default=",".join(SECCIONES), help="secciones separadas por comas")
    ap.add_argument("--todo", action="store_true", help="muestra todos los resultados, sin recortar")
    ap.add_argument("--lista-negra", type=pathlib.Path, default=None,
                    help="archivo de términos prohibidos (por defecto contexto/fugas.txt si existe)")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 2
    raiz = a.raiz.resolve()
    if not (raiz / "CLAUDE.md").exists() and not (raiz / ".claude").exists():
        print(f"No parece la raíz de Meta Ads OS: {raiz.name}", file=sys.stderr)
        return 2
    solo = [x.strip() for x in a.solo.split(",") if x.strip()]
    malas = [x for x in solo if x not in SECCIONES]
    if malas:
        print(f"Secciones desconocidas: {', '.join(malas)} (válidas: {', '.join(SECCIONES)})", file=sys.stderr)
        return 2
    lista = a.lista_negra or os.environ.get("VALIDAR_LISTA_NEGRA") or None
    lista_negra = pathlib.Path(lista) if lista else (raiz / "contexto" / "fugas.txt")
    if not lista and not lista_negra.is_file():
        lista_negra = None
    inf = validar(raiz, solo, lista_negra)
    fallos = sum(1 for x in inf.r if x.nivel == "falla")
    if a.json:
        print(json.dumps({"ok": fallos == 0, "fallos": fallos,
                          "avisos": sum(1 for x in inf.r if x.nivel == "aviso"),
                          "resultados": [asdict(x) for x in inf.r]}, ensure_ascii=False, indent=2))
    else:
        imprimir(inf, solo, a.todo)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
