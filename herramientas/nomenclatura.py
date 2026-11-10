#!/usr/bin/env python3
"""Nomenclatura de campañas, conjuntos y anuncios (contrato §7). Solo biblioteca estándar.

Formatos:
  Campaña   <MERCADO>_<OBJETIVO>_<PROPOSITO>_<PUJA>        ES_LEADS_ADQ_HV · ES-MX_SALES_TEST_CC
  Conjunto  <AUDIENCIA>_<EVENTO>                           BROAD-A+_LEAD
  Anuncio   <AAAAMMDD>_<angulo>_<concepto>_<formato>_<hook> 20261110_tiempo-perdido_demo-antes-despues_demo_h2

Valores cerrados (para que los informes puedan agregar sin sorpresas):
  OBJETIVO  LEADS · SALES · TRAFFIC · AWARENESS · ENGAGEMENT · APP   (los 6 objetivos de Meta)
  PUJA      HV (volumen más alto) · VAL (valor más alto) · CC (objetivo de coste por resultado)
            BC (límite de puja) · ROAS (objetivo de ROAS)
  formato   ugc · founder · demo · testimonio · podcast · estatico · carrusel · meme · otro
  hook      h<n> con sufijo opcional -c<n> para el cuerpo (h2, h2-c1)
PROPOSITO es libre en mayúsculas (recomendados: ADQ, RET, TEST, ESC, BAU).

Por qué importa: el registro creativo (`registro_creativo.py`) y `/siguiente-anuncio` agregan resultados por ángulo y
concepto leyendo el nombre (meta-ads-kb/13-sistema-operativo/10-plantillas.md §8 y
meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md §1). Un nombre que no cumple deja al sistema ciego.

Uso:
  python3 -I herramientas/nomenclatura.py validar anuncio "20261110_tiempo-perdido_demo-antes-despues_demo_h2"
  python3 -I herramientas/nomenclatura.py validar campana "ES_LEADS_ADQ_HV"
  python3 -I herramientas/nomenclatura.py generar --fecha 2026-11-10 --angulo "Tiempo perdido" \
      --concepto "demo antes/después" --formato demo --hook 2 [--cuerpo 1]
`validar` sale con 0 si el nombre es válido y con 1 si no (imprime el motivo y una sugerencia). `--json` en ambos.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date

NIVELES = ("campana", "conjunto", "anuncio")
FORMATOS = ("ugc", "founder", "demo", "testimonio", "podcast", "estatico", "carrusel", "meme", "otro")
OBJETIVOS = ("LEADS", "SALES", "TRAFFIC", "AWARENESS", "ENGAGEMENT", "APP")
PUJAS = ("HV", "VAL", "CC", "BC", "ROAS")

# Alias habituales → valor del contrato (para sugerir, nunca para aceptar en silencio).
_ALIAS_FORMATO = {
    "static": "estatico", "estaticos": "estatico", "imagen": "estatico", "image": "estatico", "img": "estatico",
    "carousel": "carrusel", "carrousel": "carrusel", "testimonial": "testimonio", "testimonios": "testimonio",
    "review": "testimonio", "fundador": "founder", "podcast-clip": "podcast", "video-ugc": "ugc", "creator": "ugc",
    "other": "otro", "memes": "meme",
}
_ALIAS_OBJETIVO = {
    "LEAD": "LEADS", "LEADGEN": "LEADS", "CLIENTES-POTENCIALES": "LEADS", "CAPTACION": "LEADS",
    "VENTAS": "SALES", "SALE": "SALES", "CONVERSIONES": "SALES", "CONV": "SALES", "PURCHASE": "SALES",
    "TRAFICO": "TRAFFIC", "RECONOCIMIENTO": "AWARENESS", "ALCANCE": "AWARENESS", "REACH": "AWARENESS",
    "INTERACCION": "ENGAGEMENT", "APPS": "APP", "PROMOCION-APP": "APP", "APP-PROMOTION": "APP",
}
_ALIAS_PUJA = {
    "COSTCAP": "CC", "COST-CAP": "CC", "CPR": "CC", "COSTE-OBJETIVO": "CC", "BIDCAP": "BC", "BID-CAP": "BC",
    "MINROAS": "ROAS", "ROASGOAL": "ROAS", "ROAS-GOAL": "ROAS", "LOWESTCOST": "HV", "LC": "HV", "VOL": "HV",
    "VOLUMEN": "HV", "HIGHESTVALUE": "VAL", "VALOR": "VAL",
}

_KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
_RX_ANUNCIO = re.compile(
    rf"(?P<fecha>\d{{8}})_(?P<angulo>{_KEBAB})_(?P<concepto>{_KEBAB})_(?P<formato>{'|'.join(FORMATOS)})"
    r"_(?P<hook>h[1-9]\d*(?:-c[1-9]\d*)?)"
)
_PARTE_MAY = r"[A-Z0-9+]+(?:-[A-Z0-9+]+)*"
_RX_CAMPANA = re.compile(r"(?P<mercado>[A-Z]{2,6}(?:-[A-Z]{2,6})*)_(?P<objetivo>[A-Z]+)_"
                         r"(?P<proposito>[A-Z0-9]+(?:-[A-Z0-9]+)*)_(?P<puja>[A-Z0-9]+)")
_RX_CONJUNTO = re.compile(rf"(?P<audiencia>{_PARTE_MAY})_(?P<evento>{_PARTE_MAY})")
# Sufijo que añade Meta al duplicar: " - Copy", " – Copia 2"…
_RX_COPIA = re.compile(r"\s*[-–—]\s*(?:copy|copia)(?:\s*\d+)?\s*$", re.I)


# ---------------------------------------------------------------- normalización
def _sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def kebab(texto: str) -> str:
    """'Demo antes/después' → 'demo-antes-despues'."""
    return re.sub(r"[^a-z0-9]+", "-", _sin_acentos(str(texto)).lower()).strip("-")


def _mayus(texto: str, permitir_mas: bool = True) -> str:
    patron = r"[^A-Z0-9+]+" if permitir_mas else r"[^A-Z0-9]+"
    return re.sub(patron, "-", _sin_acentos(str(texto)).upper()).strip("-")


def quitar_copia(nombre: str) -> str:
    return _RX_COPIA.sub("", nombre.strip())


# ---------------------------------------------------------------- API
def parsear_anuncio(nombre: str) -> dict | None:
    """Clasificación de un nombre de anuncio o None si no cumple el formato.

    Tolera el sufijo que Meta añade al duplicar (« - Copy», « – Copia 2») para no perder la clasificación;
    `validar` sí lo marca como error.
    """
    if not isinstance(nombre, str):
        return None
    m = _RX_ANUNCIO.fullmatch(quitar_copia(nombre))
    if not m:
        return None
    try:
        fecha = date(int(m["fecha"][:4]), int(m["fecha"][4:6]), int(m["fecha"][6:]))
    except ValueError:
        return None
    return {"fecha": fecha, "angulo": m["angulo"], "concepto": m["concepto"], "formato": m["formato"],
            "hook": m["hook"]}


def generar_anuncio(fecha: date, angulo: str, concepto: str, formato: str, hook: int,
                    cuerpo: int | None = None) -> str:
    """Nombre de anuncio normalizado (minúsculas, sin acentos, kebab). Lanza ValueError si algo no encaja."""
    if not isinstance(fecha, date):
        raise ValueError("fecha debe ser un datetime.date")
    a, c = kebab(angulo), kebab(concepto)
    if not a or not c:
        raise ValueError("el ángulo y el concepto no pueden quedar vacíos")
    f = kebab(formato)
    f = _ALIAS_FORMATO.get(f, f)
    if f not in FORMATOS:
        raise ValueError(f"formato '{formato}' no válido; usa uno de: {', '.join(FORMATOS)}")
    if not isinstance(hook, int) or isinstance(hook, bool) or hook < 1:
        raise ValueError("hook debe ser un entero ≥ 1")
    h = f"h{hook}"
    if cuerpo is not None:
        if not isinstance(cuerpo, int) or isinstance(cuerpo, bool) or cuerpo < 1:
            raise ValueError("cuerpo debe ser un entero ≥ 1")
        h += f"-c{cuerpo}"
    return f"{fecha:%Y%m%d}_{a}_{c}_{f}_{h}"


def validar(nivel: str, nombre: str) -> tuple[bool, str]:
    """(True, 'OK …') o (False, 'motivo. Sugerencia: …')."""
    if nivel not in NIVELES:
        return False, f"Nivel '{nivel}' no válido: usa {', '.join(NIVELES)}"
    if not isinstance(nombre, str) or not nombre.strip():
        return False, "El nombre está vacío"
    return {"campana": _validar_campana, "conjunto": _validar_conjunto, "anuncio": _validar_anuncio}[nivel](nombre)


def _con_sugerencia(motivo: str, sugerencia: str | None, original: str) -> tuple[bool, str]:
    if sugerencia and sugerencia != original:
        return False, f"{motivo}. Sugerencia: {sugerencia}"
    return False, motivo


def _validar_campana(nombre: str) -> tuple[bool, str]:
    formato = "<MERCADO>_<OBJETIVO>_<PROPOSITO>_<PUJA>, p. ej. ES_LEADS_ADQ_HV"
    sug = _sugerir_campana(nombre)
    m = _RX_CAMPANA.fullmatch(nombre)
    if not m:
        partes = nombre.split("_")
        motivo = (f"La campaña debe tener 4 partes separadas por «_» ({formato}); tiene {len(partes)}"
                  if len(partes) != 4 else f"La campaña va en mayúsculas, sin espacios ni acentos ({formato})")
        return _con_sugerencia(motivo, sug, nombre)
    if m["objetivo"] not in OBJETIVOS:
        return _con_sugerencia(f"Objetivo '{m['objetivo']}' no válido: usa {', '.join(OBJETIVOS)}", sug, nombre)
    if m["puja"] not in PUJAS:
        return _con_sugerencia(f"Puja '{m['puja']}' no válida: usa {', '.join(PUJAS)} "
                               "(HV volumen más alto, VAL valor más alto, CC coste objetivo, BC límite de puja, "
                               "ROAS objetivo de ROAS)", sug, nombre)
    return True, f"OK: mercado {m['mercado']}, objetivo {m['objetivo']}, propósito {m['proposito']}, puja {m['puja']}"


def _sugerir_campana(nombre: str) -> str | None:
    partes = [p for p in re.split(r"[_\s]+", nombre.strip()) if p]
    if len(partes) != 4:
        return None
    mercado = _mayus(partes[0], permitir_mas=False)
    objetivo = _mayus(partes[1], permitir_mas=False)
    objetivo = _ALIAS_OBJETIVO.get(objetivo, objetivo)
    proposito = _mayus(partes[2], permitir_mas=False)
    puja = _mayus(partes[3], permitir_mas=False)
    puja = _ALIAS_PUJA.get(puja, puja)
    s = f"{mercado}_{objetivo}_{proposito}_{puja}"
    m = _RX_CAMPANA.fullmatch(s)
    return s if m and m["objetivo"] in OBJETIVOS and m["puja"] in PUJAS else None


def _validar_conjunto(nombre: str) -> tuple[bool, str]:
    if _RX_CONJUNTO.fullmatch(nombre):
        aud, ev = nombre.split("_")
        return True, f"OK: audiencia {aud}, evento {ev}"
    partes = [p for p in nombre.strip().split("_") if p]
    sug = None
    if len(partes) == 2:
        s = f"{_mayus(partes[0])}_{_mayus(partes[1])}"
        sug = s if _RX_CONJUNTO.fullmatch(s) else None
    motivo = ("El conjunto debe tener 2 partes separadas por «_»: <AUDIENCIA>_<EVENTO>, p. ej. BROAD-A+_LEAD"
              if len(partes) != 2 else
              "El conjunto va en mayúsculas, con guiones dentro de cada parte y sin espacios ni acentos "
              "(p. ej. BROAD-A+_LEAD)")
    return _con_sugerencia(motivo, sug, nombre)


def _validar_anuncio(nombre: str) -> tuple[bool, str]:
    formato = "<AAAAMMDD>_<angulo>_<concepto>_<formato>_<hook>, p. ej. 20261110_tiempo-perdido_demo-antes-despues_demo_h2"
    base = quitar_copia(nombre)
    if base != nombre.strip():
        ok_base = parsear_anuncio(base) is not None
        return _con_sugerencia("El nombre lleva el sufijo de copia que añade Meta al duplicar",
                               base if ok_base else _sugerir_anuncio(base), nombre)
    if nombre != nombre.strip():
        return _con_sugerencia("El nombre tiene espacios al principio o al final", nombre.strip(), nombre)
    p = parsear_anuncio(nombre)
    if p:
        return True, (f"OK: {p['fecha']:%Y-%m-%d} · ángulo {p['angulo']} · concepto {p['concepto']} · "
                      f"formato {p['formato']} · {p['hook']}")
    partes = nombre.split("_")
    sug = _sugerir_anuncio(nombre)
    if len(partes) != 5:
        motivo = (f"El anuncio debe tener 5 partes separadas por «_» ({formato}); tiene {len(partes)}. "
                  "Dentro de cada parte usa guiones, nunca «_»")
        return _con_sugerencia(motivo, sug, nombre)
    f_txt, ang, con, fmt, hook = partes
    if not re.fullmatch(r"\d{8}", f_txt):
        motivo = "La fecha va al principio como AAAAMMDD"
    elif _fecha_compacta(f_txt) is None:
        motivo = f"La fecha {f_txt} no existe"
    elif not re.fullmatch(_KEBAB, ang) or not re.fullmatch(_KEBAB, con):
        motivo = "El ángulo y el concepto van en minúsculas kebab, sin acentos ni espacios (tiempo-perdido)"
    elif fmt not in FORMATOS:
        motivo = f"Formato '{fmt}' no válido: usa {', '.join(FORMATOS)}"
    else:
        motivo = "El hook va como h<n> con sufijo opcional -c<n> (h2, h2-c1), con n ≥ 1"
    return _con_sugerencia(motivo, sug, nombre)


def _fecha_compacta(texto: str) -> date | None:
    try:
        return date(int(texto[:4]), int(texto[4:6]), int(texto[6:8]))
    except ValueError:
        return None


def _sugerir_fecha(texto: str) -> str | None:
    t = texto.strip()
    m = re.fullmatch(r"(\d{4})[-/.]?(\d{2})[-/.]?(\d{2})", t)
    if m:
        f = _fecha_compacta("".join(m.groups()))
        return f"{f:%Y%m%d}" if f else None
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", t)  # DD/MM/AAAA
    if m:
        try:
            return f"{date(int(m[3]), int(m[2]), int(m[1])):%Y%m%d}"
        except ValueError:
            return None
    return None


def _sugerir_hook(texto: str) -> str | None:
    m = re.fullmatch(r"(?:h|hook)[-_ ]?(\d+)(?:[-_ ]?(?:c|cuerpo|body)[-_ ]?(\d+))?", texto.strip().lower())
    if not m or int(m[1]) < 1 or (m[2] and int(m[2]) < 1):
        return None
    return f"h{int(m[1])}" + (f"-c{int(m[2])}" if m[2] else "")


def _sugerir_anuncio(nombre: str) -> str | None:
    partes = [p for p in nombre.strip().split("_") if p.strip()]
    if len(partes) < 5:
        return None
    fecha, hook = _sugerir_fecha(partes[0]), _sugerir_hook(partes[-1])
    fmt = kebab(partes[-2])
    fmt = _ALIAS_FORMATO.get(fmt, fmt)
    medio = partes[1:-2]
    if len(medio) != 2 or not fecha or not hook or fmt not in FORMATOS:
        return None
    ang, con = kebab(medio[0]), kebab(medio[1])
    if not ang or not con:
        return None
    s = f"{fecha}_{ang}_{con}_{fmt}_{hook}"
    return s if parsear_anuncio(s) else None


# ---------------------------------------------------------------- CLI
class _Parser(argparse.ArgumentParser):
    def error(self, message):  # errores de uso = error del usuario (contrato §9: código 1)
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validar", help="valida un nombre (sale con 0 si es válido, 1 si no)")
    v.add_argument("nivel", choices=NIVELES)
    v.add_argument("nombre")
    v.add_argument("--json", action="store_true")
    g = sub.add_parser("generar", help="genera un nombre de anuncio normalizado")
    g.add_argument("--fecha", required=True, help="AAAA-MM-DD")
    g.add_argument("--angulo", required=True)
    g.add_argument("--concepto", required=True)
    g.add_argument("--formato", required=True, help=" · ".join(FORMATOS))
    g.add_argument("--hook", type=int, required=True)
    g.add_argument("--cuerpo", type=int)
    g.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "validar":
        ok, msg = validar(a.nivel, a.nombre)
        if a.json:
            print(json.dumps({"ok": ok, "nivel": a.nivel, "nombre": a.nombre, "mensaje": msg}, ensure_ascii=False))
        else:
            print(msg)
        return 0 if ok else 1
    try:
        fecha = date.fromisoformat(a.fecha)
        nombre = generar_anuncio(fecha, a.angulo, a.concepto, a.formato, a.hook, a.cuerpo)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(json.dumps({"nombre": nombre}, ensure_ascii=False) if a.json else nombre)
    return 0


if __name__ == "__main__":
    sys.exit(main())
