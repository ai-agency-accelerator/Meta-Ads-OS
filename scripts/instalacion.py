#!/usr/bin/env python3
"""Estado de la instalación: `contexto/instalacion.json` (solo biblioteca estándar, Python ≥ 3.10).

Lo usan `scripts/instalar.sh` (fase `tecnica`) y `/empezar` (el resto). El esquema es el de
`plantillas/contexto/instalacion.json`; la tabla de fases y cuándo se dan por hechas está en `/empezar`.
Nunca borra nada: si el JSON está dañado, guarda una copia antes de rehacerlo.

Uso (desde la raíz del proyecto):
  python3 -I scripts/instalacion.py ver [--json]
  python3 -I scripts/instalacion.py marcar <fase> <estado> [--detalle TEXTO] [--dato clave=valor ...]
  python3 -I scripts/instalacion.py preparar [--sistema '<json>'] [--tecnica hecho|fallo] [--detalle TEXTO]
  python3 -I scripts/instalacion.py pausar [<fase>] [--motivo TEXTO] [--json]
  python3 -I scripts/instalacion.py reanudar [--json]

Fases: tecnica, perfil, meta, integraciones, cliente, entregable, brief, motor, avanzado.
Estados: pendiente, en_curso, hecho, omitido, fallo. Completa = todas las fases requeridas en hecho u omitido.
`--dato` guarda campos propios de la fase: slug (cliente), ruta (entregable), ghl y stripe (integraciones).
`pausar` escribe {"fecha", "fase", "motivo"} en `pausa` (sin fase: la primera pendiente, requeridas primero) y no
cambia el estado de ninguna fase. `reanudar` quita la pausa y dice por qué fase seguir. Marcar como hecha u omitida
la fase pausada también quita la pausa.
Códigos de salida: 0 bien · 1 error de uso · 2 error de configuración (falta la plantilla, JSON ilegible).
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import pathlib
import sys
from datetime import date, datetime

RAIZ = pathlib.Path(os.environ.get("META_ADS_OS_RAIZ") or pathlib.Path(__file__).resolve().parent.parent)
PLANTILLA_REL = pathlib.Path("plantillas") / "contexto" / "instalacion.json"
ESTADO_REL = pathlib.Path("contexto") / "instalacion.json"

FASES = ("tecnica", "perfil", "meta", "integraciones", "cliente", "entregable", "brief", "motor", "avanzado")
ESTADOS = ("pendiente", "en_curso", "hecho", "omitido", "fallo")
TERMINADAS = ("hecho", "omitido")
CAMPOS_PROTEGIDOS = ("estado", "requerida", "fecha", "detalle")


class ErrorConfig(Exception):
    """Falta la plantilla o un archivo no se puede leer: código de salida 2."""


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def version_producto(raiz: pathlib.Path) -> str:
    try:
        for linea in (raiz / "pyproject.toml").read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea.startswith("version") and "=" in linea:
                return linea.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def fusionar(base: dict, actual: dict) -> dict:
    """Devuelve `actual` con las claves de `base` que le falten (recursivo). Nunca cambia un valor existente."""
    resultado = copy.deepcopy(actual)
    for clave, valor in base.items():
        if clave not in resultado:
            resultado[clave] = copy.deepcopy(valor)
        elif isinstance(valor, dict) and isinstance(resultado[clave], dict):
            resultado[clave] = fusionar(valor, resultado[clave])
    return resultado


def leer_plantilla(raiz: pathlib.Path) -> dict:
    try:
        return json.loads((raiz / PLANTILLA_REL).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ErrorConfig(f"No puedo leer la plantilla {PLANTILLA_REL.as_posix()} ({type(e).__name__}). "
                          "Vuelve a descargar el producto.") from None


def cargar(raiz: pathlib.Path, crear: bool = False) -> dict | None:
    """Lee contexto/instalacion.json y le añade las claves nuevas de la plantilla.

    Si no existe: None, o una copia de la plantilla si `crear`. Si está dañado y `crear`, guarda una copia
    (`instalacion.json.danado-<fecha>`) y empieza de la plantilla; si no `crear`, lanza ErrorConfig.
    """
    f = raiz / ESTADO_REL
    plantilla = leer_plantilla(raiz)
    if not f.exists():
        return copy.deepcopy(plantilla) if crear else None
    texto = f.read_text(encoding="utf-8")
    try:
        datos = json.loads(texto)
        if not isinstance(datos, dict):
            raise ValueError("no es un objeto JSON")
    except (json.JSONDecodeError, ValueError) as e:
        if not crear:
            raise ErrorConfig(f"{ESTADO_REL.as_posix()} no es un JSON válido ({e}). "
                              "Ejecuta bash scripts/instalar.sh: guarda una copia y lo rehace") from None
        copia = f.with_name(f"instalacion.json.danado-{datetime.now():%Y%m%d-%H%M%S}")
        copia.write_text(texto, encoding="utf-8")
        print(f"[AVISO]  {ESTADO_REL.as_posix()} estaba dañado: copia en {copia.relative_to(raiz).as_posix()}; "
              "lo rehago desde la plantilla")
        return copy.deepcopy(plantilla)
    return fusionar(plantilla, datos)


def guardar(raiz: pathlib.Path, datos: dict) -> None:
    datos["actualizado"] = ahora()
    datos["iniciado"] = datos.get("iniciado") or datos["actualizado"]
    f = raiz / ESTADO_REL
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.name + ".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, f)


def resumen(datos: dict | None) -> dict:
    if datos is None:
        return {"existe": False, "completa": False, "pendientes": ["tecnica"], "opcionales_pendientes": [],
                "fases": {}, "pausa": None, "version": ""}
    fases = {n: f for n, f in (datos.get("fases") or {}).items() if isinstance(f, dict)}
    pendientes = [n for n, f in fases.items() if f.get("requerida") and f.get("estado") not in TERMINADAS]
    opcionales = [n for n, f in fases.items() if not f.get("requerida") and f.get("estado") not in TERMINADAS]
    return {
        "existe": True,
        "completa": not pendientes,
        "pendientes": pendientes,
        "opcionales_pendientes": opcionales,
        "fases": {n: f.get("estado", "") for n, f in fases.items()},
        "pausa": datos.get("pausa"),
        "version": (datos.get("producto") or {}).get("version", ""),
    }


def marcar(datos: dict, fase: str, estado: str, detalle: str | None = None, extra: dict | None = None) -> None:
    f = datos.setdefault("fases", {}).setdefault(fase, {"requerida": False})
    f["estado"] = estado
    f["fecha"] = date.today().isoformat()
    if detalle is not None:
        f["detalle"] = detalle
    for clave, valor in (extra or {}).items():
        f[clave] = valor
    if estado in TERMINADAS and (datos.get("pausa") or {}).get("fase") == fase:
        datos["pausa"] = None


def siguiente_fase(datos: dict) -> str | None:
    """Primera fase sin terminar, en el orden de FASES: primero las requeridas y después las opcionales."""
    r = resumen(datos)
    for lista in (r["pendientes"], r["opcionales_pendientes"]):
        ordenadas = [n for n in FASES if n in lista] + [n for n in lista if n not in FASES]
        if ordenadas:
            return ordenadas[0]
    return None


def _salida(a, datos_json: dict, texto: str) -> None:
    print(json.dumps(datos_json, ensure_ascii=False, indent=2) if a.json else texto)


def cmd_pausar(raiz: pathlib.Path, a) -> int:
    datos = cargar(raiz, crear=True)
    fase = a.fase or siguiente_fase(datos)
    if fase is None:
        print("No hay ninguna fase pendiente: indica cuál pausar (pausar <fase>).", file=sys.stderr)
        return 1
    datos["pausa"] = {"fecha": date.today().isoformat(), "fase": fase, "motivo": a.motivo or ""}
    guardar(raiz, datos)
    _salida(a, {"pausa": datos["pausa"]},
            f"[OK]     instalación en pausa en la fase {fase}; /empezar la retoma desde ahí")
    return 0


def cmd_reanudar(raiz: pathlib.Path, a) -> int:
    datos = cargar(raiz)
    if datos is None:
        _salida(a, {"pausa_anterior": None, "fase": "tecnica"},
                "Instalación sin empezar: ejecuta bash scripts/instalar.sh y después /empezar.")
        return 0
    anterior = datos.get("pausa")
    fase = (anterior or {}).get("fase")
    if fase not in (datos.get("fases") or {}) or datos["fases"][fase].get("estado") in TERMINADAS:
        fase = siguiente_fase(datos)
    if anterior is not None:
        datos["pausa"] = None
        guardar(raiz, datos)
    texto = ("Instalación completa: no queda nada pendiente." if fase is None else
             f"[OK]     {'pausa quitada; ' if anterior else ''}seguimos por la fase {fase}")
    _salida(a, {"pausa_anterior": anterior, "fase": fase}, texto)
    return 0


def cmd_ver(raiz: pathlib.Path, a) -> int:
    r = resumen(cargar(raiz))
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    if not r["existe"]:
        print("Instalación sin empezar: ejecuta bash scripts/instalar.sh y después /empezar.")
        return 0
    print(f"Meta Ads OS {r['version'] or '(versión desconocida)'} · "
          + ("instalación completa" if r["completa"] else "instalación incompleta"))
    for n, e in r["fases"].items():
        print(f"  {'✔' if e in TERMINADAS else '·'} {n}: {e}")
    if r["pausa"]:
        p = r["pausa"]
        print(f"En pausa desde {p.get('fecha', '?')} en la fase {p.get('fase', '?')}"
              + (f" ({p['motivo']})" if p.get("motivo") else "") + ".")
    if r["pendientes"]:
        print("Pendiente: " + ", ".join(r["pendientes"]) + " → /empezar lo retoma donde lo dejaste.")
    elif r["opcionales_pendientes"]:
        print("Opcional: " + ", ".join(r["opcionales_pendientes"]) + ".")
    return 0


def cmd_preparar(raiz: pathlib.Path, a) -> int:
    datos = cargar(raiz, crear=True)
    try:
        sistema = json.loads(a.sistema) if a.sistema else {}
    except json.JSONDecodeError:
        print("--sistema debe ser un objeto JSON", file=sys.stderr)
        return 1
    datos.setdefault("sistema", {}).update({k: str(v) for k, v in sistema.items()})
    datos.setdefault("producto", {})["version"] = version_producto(raiz) or datos["producto"].get("version", "")
    marcar(datos, "tecnica", a.tecnica, a.detalle)
    guardar(raiz, datos)
    return 0


def cmd_marcar(raiz: pathlib.Path, a) -> int:
    extra = {}
    for par in a.dato or []:
        clave, sep, valor = par.partition("=")
        if not sep or not clave or clave in CAMPOS_PROTEGIDOS:
            print(f"--dato no válido: {par!r} (usa clave=valor; no se pueden usar {', '.join(CAMPOS_PROTEGIDOS)})",
                  file=sys.stderr)
            return 1
        extra[clave] = valor
    datos = cargar(raiz, crear=True)
    marcar(datos, a.fase, a.estado, a.detalle, extra)
    guardar(raiz, datos)
    print(f"[OK]     fase {a.fase}: {a.estado}")
    return 0


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):  # Windows con tubería usa cp1252: sin esto, «✔» o «→» rompen la salida
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", type=pathlib.Path, default=None, help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="orden", required=True)

    v = sub.add_parser("ver", help="estado de la instalación")
    v.add_argument("--json", action="store_true")

    m = sub.add_parser("marcar", help="cambia el estado de una fase")
    m.add_argument("fase", choices=FASES)
    m.add_argument("estado", choices=ESTADOS)
    m.add_argument("--detalle", default=None)
    m.add_argument("--dato", action="append", metavar="CLAVE=VALOR")

    p = sub.add_parser("preparar", help="crea o completa el archivo y marca la fase técnica (lo usa instalar.sh)")
    p.add_argument("--sistema", default="", help="JSON con las versiones detectadas")
    p.add_argument("--tecnica", choices=("hecho", "fallo"), default="hecho")
    p.add_argument("--detalle", default=None)

    pa = sub.add_parser("pausar", help="deja la instalación en pausa para retomarla con /empezar")
    pa.add_argument("fase", nargs="?", choices=FASES, default=None)
    pa.add_argument("--motivo", default="")
    pa.add_argument("--json", action="store_true")

    re_ = sub.add_parser("reanudar", help="quita la pausa y dice por qué fase seguir")
    re_.add_argument("--json", action="store_true")

    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 1
    raiz = (a.raiz or RAIZ).resolve()
    ordenes = {"ver": cmd_ver, "marcar": cmd_marcar, "preparar": cmd_preparar, "pausar": cmd_pausar,
               "reanudar": cmd_reanudar}
    try:
        return ordenes[a.orden](raiz, a)
    except ErrorConfig as e:
        print(f"[ERROR]  {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
