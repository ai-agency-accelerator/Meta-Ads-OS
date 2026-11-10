#!/usr/bin/env python3
"""Proyectos del motor de vídeo con IA (modulos/motor-ia): estado, marca, coste real y estimado. Solo lectura.

Lee la base de datos del motor en modo solo lectura: `MOTOR_DATA_DIR/motor.sqlite3` si defines esa variable (ruta
absoluta o relativa a modulos/motor-ia) y, si no, `modulos/motor-ia/data/motor.sqlite3`. No gasta nada.

Uso:
  python3 -I herramientas/motor_proyectos.py [--marca <id o nombre>] [--estado paused_billing] [--max 40] [--json]
Detalle de costes de un proyecto: uv run --project modulos/motor-ia motor costs <proyecto>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402


def ruta_db() -> pathlib.Path:
    modulo = _comun.RAIZ / "modulos" / "motor-ia"
    _comun.cargar_entorno()
    datos = os.environ.get("MOTOR_DATA_DIR")
    if datos:
        p = pathlib.Path(datos).expanduser()
        return (p if p.is_absolute() else (modulo / p)) / "motor.sqlite3"
    return modulo / "data" / "motor.sqlite3"


def proyectos(db: pathlib.Path, marca: str | None = None, estado: str | None = None) -> list[dict]:
    c = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        costes: dict = {}
        try:
            cols = [r[1] for r in c.execute("pragma table_info(costs)")]
            pcol = next((x for x in ("project_id", "project") if x in cols), None)
            ucol = next((x for x in ("usd", "cost_usd", "amount_usd") if x in cols), None)
            if pcol and ucol:
                costes = dict(c.execute(f"select {pcol}, sum({ucol}) from costs group by {pcol}").fetchall())
        except sqlite3.Error:
            pass
        marcas = {}
        for i, j in c.execute("select id, json from docs where kind='brand'"):
            try:
                marcas[i] = json.loads(j).get("name") or i
            except (json.JSONDecodeError, AttributeError):
                marcas[i] = i
        out = []
        for pid, j, upd in c.execute("select id, json, updated_at from docs where kind='project' "
                                     "order by updated_at desc"):
            try:
                d = json.loads(j)
            except json.JSONDecodeError:
                continue
            b = (d.get("brief") or {}).get("brand_id")
            if marca and marca not in (b, marcas.get(b)):
                continue
            if estado and d.get("status") != estado:
                continue
            real = costes.get(pid)
            est = (d.get("variant_spec") or {}).get("estimated_cost_usd")
            out.append({"proyecto": pid, "nombre": (d.get("name") or "")[:48], "estado": d.get("status"),
                        "marca": marcas.get(b, b), "variante_de": d.get("parent_id") or "",
                        "coste_real_usd": round(real, 2) if isinstance(real, (int, float)) else None,
                        "estimado_usd": round(est, 2) if isinstance(est, (int, float)) else None,
                        "actualizado": dt.datetime.fromtimestamp(float(upd)).strftime("%Y-%m-%d %H:%M") if upd else ""})
        return out
    finally:
        c.close()


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--marca", help="id o nombre de la marca en el motor")
    ap.add_argument("--estado", help="p. ej. done, running, paused_billing, failed")
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    db = ruta_db()
    if not db.exists():
        print("El motor de vídeo no tiene datos todavía (no está instalado o no ha producido nada). Instálalo con "
              "/motor instalar o prueba sin gastar con MOTOR_MOCK=1.", file=sys.stderr)
        return 2
    try:
        filas = proyectos(db, a.marca, a.estado)
    except sqlite3.Error as e:
        print(f"No se pudo leer la base de datos del motor: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(filas[: a.max], ensure_ascii=False, indent=2))
        return 0
    print("| Proyecto | Nombre | Estado | Marca | Variante de | Coste real $ | Estimado $ | Actualizado |")
    print("|---|---|---|---|---|---|---|---|")
    for f in filas[: a.max]:
        real = f"{f['coste_real_usd']:.2f}" if f["coste_real_usd"] is not None else "—"
        est = f"{f['estimado_usd']:.2f}" if f["estimado_usd"] is not None else "—"
        print(f"| {f['proyecto']} | {f['nombre']} | {f['estado']} | {f['marca']} | {f['variante_de']} | {real} | {est} "
              f"| {f['actualizado']} |")
    total = sum(f["coste_real_usd"] or 0 for f in filas)
    print(f"\n{len(filas)} proyectos · coste real total {total:.2f} $. "
          "Detalle: uv run --project modulos/motor-ia motor costs <proyecto>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
