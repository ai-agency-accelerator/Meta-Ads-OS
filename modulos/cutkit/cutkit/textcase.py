"""Title Case «inteligente» en español para los rótulos de las tarjetas (p. ej. «Citas a la Semana», «Parte de Ventas»).

Mayúscula inicial en las palabras con contenido; en minúscula los artículos, preposiciones y conjunciones salvo si abren el
rótulo. Siglas (IA, JSON, API) y palabras con mayúsculas internas se respetan.

Se aplica a los rótulos (claves de `CLAVES`) que no son prosa ni código: una frase acabada en punto, un texto de más de
8 palabras, un nombre de archivo o un fragmento de código no se tocan.
"""
from __future__ import annotations

import re

MENORES = {
    "a", "al", "ante", "bajo", "con", "contra", "de", "del", "desde", "durante", "en", "entre", "hacia", "hasta",
    "mediante", "para", "por", "según", "sin", "sobre", "tras", "vía",
    "y", "e", "o", "u", "ni", "que",
    "el", "la", "los", "las", "lo", "un", "una", "unos", "unas",
}
# claves de props que son rótulos de tarjeta (no prosa, no código, no subtítulos)
CLAVES = {"label", "title", "kicker", "sub", "tail", "prompt_label", "candidates_label", "question", "badge", "name", "by"}
_PALABRA = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.UNICODE)
# marcas que se escriben siempre así (en minúscula): nunca se capitalizan ni cuentan para decidir si es un rótulo
MARCAS = {"n8n"}
_MARCA = re.compile(r"(?<!\w)(" + "|".join(re.escape(m) for m in sorted(MARCAS)) + r")(?!\w)", re.IGNORECASE)


_CODIGO = re.compile(r"[_/\\{}\"=<>]|\.\w|^\W*$")


def _es_rotulo(s: str) -> bool:
    """Rótulo en Title Case «ingenuo» (todas las palabras con mayúscula) o rótulo corto en minúscula («instrucción»).
    Una frase (asunto de un correo, prompt) o un encabezado mixto escrito a propósito no se tocan."""
    ws = _PALABRA.findall(_MARCA.sub(" ", s))
    if not ws or len(ws) > 10 or _CODIGO.search(s) or s.rstrip().endswith((".", "…")):
        return False
    return (len(ws) >= 2 and all(w[0].isupper() for w in ws)) or (len(ws) <= 3 and all(w.islower() for w in ws))


def titulo(s: str) -> str:
    """«Directos A La Semana» → «Directos a la Semana». Devuelve `s` intacto si no es un rótulo en Title Case."""
    if not isinstance(s, str) or not _es_rotulo(s):
        return s
    out, primera = [], True

    def rep(m: re.Match) -> str:
        nonlocal primera
        w = m.group(0)
        cap = lambda x: x[:1].upper() + x[1:]
        if primera:
            primera = False
            return cap(w)
        if any(c.isupper() for c in w[1:]):         # siglas y marcas (IA, FitPro, AcmeFlow)
            return w
        if m.end() < len(m.string) and m.string[m.end()].isdigit():   # códigos (E001, S001)
            return w
        if w.lower() in MENORES:
            return w.lower()
        return cap(w)

    # tras dos puntos o un paréntesis, la palabra vuelve a abrir rótulo («Siguiente Token (Esquema)»)
    for parte in re.split(r"([:(¿¡])", s):
        if parte in (":", "(", "¿", "¡"):
            out.append(parte)
            primera = True
            continue
        for trozo in _MARCA.split(parte):            # «n8n» tal cual (la marca va en minúsculas)
            if trozo and trozo.lower() in MARCAS:
                out.append(trozo.lower())
                primera = False
            else:
                out.append(_PALABRA.sub(rep, trozo))
    return "".join(out)


def props_titulo(props, _clave: str = "") -> object:
    """Aplica `titulo` a los rótulos de unas props (recursivo; también `lines[].text` de los lockups)."""
    if isinstance(props, dict):
        return {k: (titulo(v) if isinstance(v, str) and (k in CLAVES or (k == "text" and _clave == "lines"))
                    else props_titulo(v, k)) for k, v in props.items()}
    if isinstance(props, list):
        return [props_titulo(x, _clave) for x in props]
    return props
