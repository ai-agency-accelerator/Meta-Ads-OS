#!/usr/bin/env python3
"""Estado de cada cliente sin coste: fase, pendientes, evaluaciones vencidas, informe semanal, brief y cola.

Lo usan `/hoy`, el brief diario y el hook de inicio de sesión. Solo lee archivos de la instancia; no llama a nada.

Uso:
  python3 -I herramientas/estado.py resumen [--cliente SLUG] [--fecha AAAA-MM-DD] [--todos] [--json]

JSON (contrato §9):
  {"fecha": "AAAA-MM-DD",
   "clientes": [{"slug", "fase", "pendientes": [id], "evaluaciones_vencidas": [{"fecha", "objeto", "cambio"}],
                 "informe_semanal_pendiente": bool, "brief_hoy": bool, "cola_produccion": int}]}

Reglas:
- fase: la primera fase de `clientes/<slug>/estado.md` con puntos sin marcar (contrato §4); si está todo marcado, F6.
  `pendientes` son los puntos sin marcar de esa fase, en orden. Un punto que acaba en «Opcional.» (p. ej. `F0.iman`)
  no cuenta: ni retiene la fase ni sale en `pendientes`.
- evaluaciones vencidas: filas de `change-log.md` con «Fecha de evaluación» ≤ fecha y «Resultado» vacío (§5).
- informe semanal pendiente: el cliente ya opera (F4.activa marcado o fase F5/F6) y en `informes/` (sin contar
  `diario/`) no hay informe de la última semana natural completa. Cuenta como hecho un archivo cuyo nombre lleve la
  semana ISO analizada (`2026-W45`) o que lleve «semana»/«semanal» y una fecha entre el domingo que cierra esa semana
  y la fecha de hoy. Convención recomendada: `informes/semanal/AAAA-Www.md`.
- brief de hoy: existe `clientes/<slug>/informes/diario/<fecha>.md` (§15).
- cola de producción: carpetas de `creativos/` (salvo las que empiezan por `_` o `.`) cuyo `LEEME.md` tiene la línea
  exacta `- **Estado:** borrador` o `- **Estado:** listo` (§6). Sin `LEEME.md` no cuentan (p. ej. `<fecha>-estudio/`).
- Sin `--cliente` se recorren los clientes con ficha salvo los que están en `estado: pausa` (`--todos` los incluye).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402

FASES = ("F0", "F1", "F2", "F3", "F4", "F5", "F6")
_RX_ITEM = re.compile(r"^\s*[-*]\s*\[(?P<marca>[ xX])\]\s*(?P<id>F[0-6]\.[\w-]+)\b")
_RX_OPCIONAL = re.compile(r"\bopcional\.?\s*$", re.I)
_RX_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")
_RX_EN_COLA = re.compile(r"^- \*\*Estado:\*\* (?:borrador|listo)[ \t\r]*$", re.M)  # §6: formato fijo


# ---------------------------------------------------------------- estado.md
def leer_items(texto: str) -> list[tuple[str, bool | None]]:
    """[(id, hecho)] en el orden del archivo. `hecho` es None en un punto opcional sin marcar: no cuenta."""
    out = []
    for linea in texto.splitlines():
        m = _RX_ITEM.match(linea)
        if m:
            hecho = m["marca"].lower() == "x"
            out.append((m["id"], None if not hecho and _RX_OPCIONAL.search(linea) else hecho))
    return out


def es_opcional(texto: str, id_: str) -> bool:
    return any((m := _RX_ITEM.match(l)) and m["id"] == id_ and _RX_OPCIONAL.search(l) for l in texto.splitlines())


def fase_y_pendientes(items: list[tuple[str, bool | None]]) -> tuple[str, list[str]]:
    if not items:  # sin checklist no hay nada verificado
        return "F0", []
    for fase in FASES:
        pend = [i for i, hecho in items if i.split(".")[0] == fase and hecho is False]
        if pend:
            return fase, pend
    return "F6", []


def _items_cliente(dir_cliente: pathlib.Path) -> list[tuple[str, bool]]:
    f = dir_cliente / "estado.md"
    if f.exists():
        return leer_items(f.read_text(encoding="utf-8"))
    producto = pathlib.Path(__file__).resolve().parent.parent
    plantilla = next((p for p in (_comun.RAIZ / "plantillas" / "cliente" / "estado.md",
                                  producto / "plantillas" / "cliente" / "estado.md") if p.exists()), None)
    if plantilla:  # sin estado.md: nada verificado todavía
        print(f"[aviso] {dir_cliente.name}: falta estado.md; se usa la lista de la plantilla sin marcar",
              file=sys.stderr)
        return [(i, None if h is None else False) for i, h in leer_items(plantilla.read_text(encoding="utf-8"))]
    print(f"[aviso] {dir_cliente.name}: falta estado.md", file=sys.stderr)
    return []


# ---------------------------------------------------------------- change log
def _celdas(linea: str) -> list[str]:
    t = linea.strip()
    if t.startswith("|"):
        t = t[1:]
    if t.endswith("|") and not t.endswith("\\|"):
        t = t[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", t)]


def _norm(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.strip().lower())


def evaluaciones_vencidas(texto: str, fecha: date) -> list[dict]:
    """Filas con fecha de evaluación ≤ fecha y sin resultado, de la más antigua a la más reciente."""
    cab: list[str] | None = None
    out = []
    for linea in texto.splitlines():
        if not linea.strip().startswith("|"):
            cab = None if linea.strip() else cab
            continue
        celdas = _celdas(linea)
        nombres = [_norm(c) for c in celdas]
        if any(n.startswith("fecha de evaluaci") for n in nombres) and any(n.startswith("resultado") for n in nombres):
            cab = nombres
            continue
        if cab is None or all(re.fullmatch(r":?-{2,}:?", c) for c in celdas if c):
            continue
        fila = dict(zip(cab, celdas + [""] * (len(cab) - len(celdas))))
        ev = next((v for k, v in fila.items() if k.startswith("fecha de evaluaci")), "")
        res = next((v for k, v in fila.items() if k.startswith("resultado")), "")
        m = _RX_FECHA.search(ev)
        if not m or res.strip():
            continue
        try:
            f_ev = date.fromisoformat(m.group(0))
        except ValueError:
            continue
        if f_ev <= fecha:
            out.append({"fecha": f_ev.isoformat(),
                        "objeto": next((v for k, v in fila.items() if k.startswith("objeto")), ""),
                        "cambio": next((v for k, v in fila.items() if k.startswith("cambio")), "")})
    return sorted(out, key=lambda e: e["fecha"])


# ---------------------------------------------------------------- informes
def semana_analizada(fecha: date) -> tuple[date, date]:
    """Lunes y domingo de la última semana natural completa antes de `fecha`."""
    lunes_actual = fecha - timedelta(days=fecha.weekday())
    return lunes_actual - timedelta(days=7), lunes_actual - timedelta(days=1)


def informe_semanal_hecho(dir_informes: pathlib.Path, fecha: date) -> bool:
    if not dir_informes.is_dir():
        return False
    lunes, domingo = semana_analizada(fecha)
    iso = lunes.isocalendar()
    etiqueta = f"{iso[0]}-w{iso[1]:02d}"
    for f in dir_informes.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(dir_informes)
        if rel.parts and rel.parts[0] == "diario":
            continue
        nombre = str(rel).lower()
        if etiqueta in nombre:
            return True
        if "semana" in nombre:
            for m in _RX_FECHA.finditer(nombre):
                try:
                    d = date.fromisoformat(m.group(0))
                except ValueError:
                    continue
                if domingo <= d <= fecha:
                    return True
    return False


def cola_produccion(dir_cliente: pathlib.Path) -> int:
    """Piezas en borrador o listas para publicar. Manda el Estado del LEEME.md, no el registro creativo."""
    creativos = dir_cliente / "creativos"
    if not creativos.is_dir():
        return 0
    n = 0
    for d in sorted(creativos.iterdir()):
        if not d.is_dir() or d.name.startswith(("_", ".")):
            continue
        leeme = d / "LEEME.md"
        if leeme.is_file() and _RX_EN_COLA.search(leeme.read_text(encoding="utf-8-sig", errors="ignore")):
            n += 1
    return n


# ---------------------------------------------------------------- resumen
def _clientes(cliente: str | None, todos: bool) -> list[str]:
    if cliente:
        d = _comun.ruta_cliente(cliente)  # valida el slug
        if not d.is_dir():
            raise _comun.FichaInvalida(f"No existe la carpeta clientes/{cliente}. Crea el cliente con /cliente-nuevo")
        return [cliente]
    if not _comun.CLIENTES.is_dir():
        return []
    out = []
    for d in sorted(_comun.CLIENTES.iterdir()):
        if not d.is_dir() or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", d.name):
            continue
        if not (d / "ficha.md").exists() and not (d / "estado.md").exists():
            continue
        if not todos:
            try:
                if str(_comun.leer_ficha(d.name).get("estado", "")).lower() == "pausa":
                    continue
            except _comun.FichaInvalida as e:
                print(f"[aviso] {d.name}: {e}", file=sys.stderr)
        out.append(d.name)
    return out


def estado_cliente(slug: str, fecha: date) -> dict:
    d = _comun.ruta_cliente(slug)
    items = _items_cliente(d)
    fase, pendientes = fase_y_pendientes(items)
    hechos = {i for i, h in items if h}
    cl = d / "change-log.md"
    vencidas = evaluaciones_vencidas(cl.read_text(encoding="utf-8"), fecha) if cl.exists() else []
    opera = "F4.activa" in hechos or fase in ("F5", "F6")
    return {
        "slug": slug,
        "fase": fase,
        "pendientes": pendientes,
        "evaluaciones_vencidas": vencidas,
        "informe_semanal_pendiente": bool(opera and not informe_semanal_hecho(d / "informes", fecha)),
        "brief_hoy": (d / "informes" / "diario" / f"{fecha.isoformat()}.md").is_file(),
        "cola_produccion": cola_produccion(d),
    }


def resumen(fecha: date | None = None, cliente: str | None = None, todos: bool = False) -> dict:
    fecha = fecha or date.today()
    return {"fecha": fecha.isoformat(), "clientes": [estado_cliente(s, fecha) for s in _clientes(cliente, todos)]}


def _texto(r: dict) -> str:
    lin = [f"Estado a {r['fecha']}"]
    if not r["clientes"]:
        lin.append("No hay clientes. Crea el primero con /cliente-nuevo.")
    for c in r["clientes"]:
        pend = ", ".join(c["pendientes"][:3]) + (f" (+{len(c['pendientes']) - 3})" if len(c["pendientes"]) > 3 else "")
        lin.append(f"- {c['slug']} · {c['fase']}" + (f" · siguiente: {pend}" if pend else " · fase completa"))
        for e in c["evaluaciones_vencidas"]:
            lin.append(f"    evaluación vencida {e['fecha']}: {e['objeto']} · {e['cambio']}")
        extra = []
        if c["informe_semanal_pendiente"]:
            extra.append("informe semanal pendiente")
        extra.append("brief de hoy: sí" if c["brief_hoy"] else "brief de hoy: no")
        if c["cola_produccion"]:
            extra.append(f"cola de producción: {c['cola_produccion']}")
        lin.append("    " + " · ".join(extra))
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
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resumen", help="fase, pendientes, evaluaciones vencidas, informe semanal, brief y cola")
    r.add_argument("--cliente")
    r.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy)")
    r.add_argument("--todos", action="store_true", help="incluye los clientes en pausa")
    r.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        fecha = date.fromisoformat(a.fecha) if a.fecha else date.today()
    except ValueError:
        print("Error: --fecha va como AAAA-MM-DD", file=sys.stderr)
        return 1
    try:
        res = resumen(fecha, a.cliente, a.todos)
    except _comun.FichaInvalida as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else _texto(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
