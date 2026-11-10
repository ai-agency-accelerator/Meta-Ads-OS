"""Producción automática en cuanto el proveedor tenga saldo. ORDEN DE PAGO (el hook `motor_guard` pide confirmación).

Comprueba el saldo de Gemini con una llamada mínima (<0,0001 $) cada `--interval` segundos. Cuando responde, ejecuta
`orchestrator.run` sobre cada proyecto (reanudable: lo ya hecho no se repite ni se paga), y escribe un resumen en
`data/work/auto_produce.json`. El presupuesto global del motor sigue mandando: si se agota, el proyecto queda en pausa.

Con `MOTOR_MOCK=1` no hay comprobación de saldo ni llamadas reales: produce en simulado de inmediato (0 $).

Uso: uv run --project modulos/motor-ia python modulos/motor-ia/scripts/auto_produce.py proj_a proj_b [--interval 600] [--max-hours 24]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def has_credit() -> tuple[bool, str]:
    from motor.store import ctx

    s = ctx().settings
    if s.mock:
        return True, "simulado"
    if not s.has("GEMINI_API_KEY"):
        return False, "falta GEMINI_API_KEY en el .env de la raíz"
    from google import genai

    try:
        c = genai.Client(api_key=s.key("GEMINI_API_KEY"))
        c.models.generate_content(model="gemini-3.1-flash-lite", contents="ok")
        return True, "ok"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:100]}"  # nunca se imprime la clave: el SDK no la incluye en el error


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+")
    ap.add_argument("--interval", type=int, default=600)
    ap.add_argument("--max-hours", type=float, default=24)
    a = ap.parse_args(argv)
    from motor import orchestrator
    from motor.costs import summarize
    from motor.store import ctx

    out = ctx().settings.work_dir / "auto_produce.json"
    deadline = time.time() + a.max_hours * 3600
    while True:
        ok, why = has_credit()
        print(time.strftime("%H:%M:%S"), "saldo:", "SÍ" if ok else f"no ({why[:80]})", flush=True)
        if ok:
            break
        if time.time() > deadline:
            print("sin saldo tras el plazo: me detengo", flush=True)
            return 1
        time.sleep(a.interval)
    results = []
    for pid in a.projects:
        t0 = time.time()
        print(time.strftime("%H:%M:%S"), "produciendo", pid, flush=True)
        try:
            r = orchestrator.run(pid, lambda f, m: print(f"  {f * 100:5.1f}% {m}", flush=True), use_vlm=True)
        except Exception as e:  # noqa: BLE001
            r = {"project_id": pid, "status": "failed", "error": f"{type(e).__name__}: {str(e)[:300]}"}
        r["minutes"] = round((time.time() - t0) / 60, 1)
        r["cost"] = summarize(pid)
        results.append(r)
        out.write_text(json.dumps(results, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        print(json.dumps({k: r.get(k) for k in ("project_id", "status", "qa_verdict", "render", "minutes")}, ensure_ascii=False,
                         default=str), flush=True)
    print("FIN", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
