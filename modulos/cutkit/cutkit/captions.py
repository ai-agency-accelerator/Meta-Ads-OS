"""Subtítulos: agrupa palabras del programa en páginas de 1–3 palabras por prosodia y sintaxis.

Reglas (criterios de subtítulos + perfil de referencias):
- Programación dinámica: se prefieren páginas de 2 palabras; se corta en puntuación y pausas; nunca se deja colgando
  una palabra funcional al final de la página («de», «la», «que»…); ≤ 18 caracteres por página.
- La página entra 1 fotograma antes de su primera palabra y se mantiene hasta la siguiente (sin huecos si la pausa es
  corta); si hay una pausa > 0,45 s, la página sale 0,15 s después de su última palabra.
- Énfasis por palabra lo deciden las decisiones `caption.emphasis` (no el agrupador).
- No se corta DENTRO de un nombre de varias palabras (modelo, herramienta), p. ej. «de lanzar Nimbo | Pro 2» o
  «Nimbo Pro | 2 cuesta»: penalización `NAME_CUT` en el corte entre dos palabras que forman nombre (ver `_bond`).
- Un nombre de 3–4 palabras va en su propia página (hasta 4 palabras y MAX_CHARS + 4), y la palabra funcional que
  lo presenta («es» en «es Acme Flow Studio») puede quedarse al final de la página anterior si no cabe con él. En una muestra de 256 frases solo cambian 4,
  todas con nombre.
"""
from __future__ import annotations

import re

FUNC = {"de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "u", "que", "a", "al", "en", "por",
        "para", "con", "sin", "se", "le", "les", "lo", "su", "sus", "es", "si", "no", "ni", "mi", "tu", "como", "sino",
        "pero", "más", "muy", "cuál", "qué", "este", "esta", "ese", "esa"}
MAX_CHARS = 18
NAME_CUT = 2.6                                      # cortar dentro de un nombre («Nimbo | Pro 2») cuesta más que una página de 1
_SENT = re.compile(r"[.;:?!…]")
_VERSION = re.compile(r"^\d+([.,]\d+)?[a-z]?$", re.I)


def _proper(t: str) -> bool:
    t = t.strip("¿¡«»\"'()")
    return bool(t) and t[0].isupper() and t.lower() not in FUNC


def _bond(a: dict, b: dict, prev: dict | None) -> bool:
    """¿`a` y `b` (seguidas) son parte del MISMO nombre propio de varias palabras? Sin puntuación entre ellas y:
    - una versión tras un nombre propio: «Nimbo 4», «Pro 5.5», «Acme 6»;
    - un nombre propio tras una versión o un modelo con cifra: «4 Pro», «Acme-6 Flow», «5.5 Pro»;
    - dos nombres propios seguidos que no abren frase: «Acme Flow», «Nimbo Pro», «Acme Studio»."""
    if a.get("punct") and re.search(r"[.,;:?!…]", a["punct"]):
        return False
    ta, tb = a["text"].strip(), b["text"].strip()
    if _VERSION.match(tb) and _proper(ta):
        return True
    if _proper(tb) and (_VERSION.match(ta) or (re.search(r"\d", ta) and re.search(r"[A-Za-z]", ta))):
        return True
    starts = prev is None or bool(prev.get("punct") and _SENT.search(prev["punct"]))
    return _proper(ta) and _proper(tb) and not starts


def _cost_page(ws: list[dict], name: bool = False, before_name: bool = False) -> float:
    """name: la página ES un nombre entero de varias palabras («Nimbo Pro 2», «Acme Flow Studio»): se admite de 4
    palabras y hasta MAX_CHARS + 4 caracteres (el subtítulo se ajusta al ancho). before_name: tras esta página empieza un
    nombre de varias palabras, así que su última palabra funcional («es») puede quedarse al final («El segundo es |
    Acme Flow Studio» en vez de «es Acme | Flow Studio»)."""
    n = len(ws)
    chars = sum(len(w["text"]) for w in ws) + n - 1
    c = {1: 1.4, 2: 0.0, 3: 0.5, 4: 0.8 if (name or before_name) else 99.0}.get(n, 99.0)
    lim = MAX_CHARS + 4 if name else MAX_CHARS
    if chars > lim:
        c += 3 + (chars - lim) * 0.4
    last = ws[-1]
    if last["text"].lower().strip("¿¡") in FUNC and not last.get("punct") and not before_name:
        c += 2.5                                    # no dejar «de», «la»… colgando
    for w in ws[:-1]:                               # puntuación o pausa dentro de la página = mal corte
        if w.get("punct") and re.search(r"[.,;:?!…]", w["punct"]):
            c += 3.0
        if w.get("gap", 0) > 0.22:
            c += 2.0
    return c


def group_pages(words: list[dict]) -> list[list[dict]]:
    """words: [{id,text,s,e,punct,gap}] en tiempo de programa (gap = silencio hasta la siguiente)."""
    n = len(words)
    best = [0.0] + [1e9] * n
    back = [0] * (n + 1)
    for i in range(1, n + 1):
        for k in (1, 2, 3, 4):
            j = i - k
            if j < 0:
                continue
            # no saltar entre fuentes ni a través de cortes largos
            seg = words[j:i]
            if any(seg[m]["src"] != seg[0]["src"] for m in range(len(seg))):
                continue
            # ¿la página entera es un nombre de varias palabras? (4 palabras solo si lo es)
            name = k >= 2 and all(_bond(seg[m], seg[m + 1], seg[m - 1] if m else (words[j - 1] if j else None))
                                  for m in range(k - 1))
            # tras la página empieza un nombre que NO cabe con la palabra funcional en una página («es» + «Acme Flow
            # Studio»: 3+ palabras o > MAX_CHARS); «de Nimbo Pro» sigue junto, como siempre
            run = 1
            while i + run < n and _bond(words[i + run - 1], words[i + run], words[i + run - 2]):
                run += 1
            nm_chars = sum(len(w["text"]) for w in words[i:i + run]) + run - 1
            before_name = k >= 2 and run >= 2 and (run >= 3 or len(seg[-1]["text"]) + 1 + nm_chars > MAX_CHARS)
            # 4 palabras: el nombre entero, o la frase corta que lo presenta («Y el cuarto es | UI UX Pro Max»; si no,
            # «es» se quedaba solo en una página de 0,3 s)
            if k == 4 and not (name or (before_name and sum(len(w["text"]) for w in seg) + 3 <= MAX_CHARS)):
                continue
            c = best[j] + _cost_page(seg, name, before_name)
            if i < n and _bond(words[i - 1], words[i], words[i - 2] if i >= 2 else None):
                c += NAME_CUT                       # el corte tras esta página partiría un nombre
            if c < best[i]:
                best[i], back[i] = c, j
    pages, i = [], n
    while i > 0:
        pages.append(words[back[i]:i])
        i = back[i]
    return pages[::-1]


def page_windows(pages: list[list[dict]], fps: int, end_time: float) -> list[tuple[float, float]]:
    f = 1.0 / fps
    out = []
    for k, p in enumerate(pages):
        t0 = max(0.0, p[0]["s"] - f)
        if k + 1 < len(pages):
            nxt = max(0.0, pages[k + 1][0]["s"] - f)
            gap = pages[k + 1][0]["s"] - p[-1]["e"]
            t1 = min(nxt, p[-1]["e"] + 0.15) if gap > 0.45 else nxt
        else:
            t1 = min(end_time, p[-1]["e"] + 0.35)
        out.append((round(t0, 4), round(max(t1, t0 + 0.3), 4)))
    return out
