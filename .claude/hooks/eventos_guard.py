#!/usr/bin/env python3
"""Guardia de envíos a la Conversions API de Meta (PreToolUse sobre Bash).

Un evento real mandado «para probar» ensucia el dataset del cliente y lo que Meta optimiza. Por eso:
- `herramientas/capi.py enviar` sin `--test-code` (o con `--real --confirmo`) → ask con un aviso fuerte, y deny si lo
  lanza un subagente que no es `operador-meta` (los envíos reales van con un plan aprobado, como las demás escrituras
  en Meta); con `--test-code` → ask informativo (es un envío de prueba, no cuenta para la optimización). Vale igual
  para la mensajería (`business_messaging`, B14): la orden y sus opciones son las mismas.
- `curl`/`wget`/`http` o un script en línea que hace POST a `graph.facebook.com/.../events` → ask, fuerte si no lleva
  `test_event_code` (también lo busca en el archivo de `-d @archivo.json`).
Las demás órdenes de capi.py (construir, hashear, validar, origen) son locales y no se tocan.
- Python sobre herramientas/ que el troceo no puede leer (comodines que no dan un único script, variables, `-c`,
  `-m`, `runpy`, `exec`, `..`) y que puede ser un envío (`enviar`, `capi`, `/events`) → ask en la sesión principal y
  deny en subagentes. Un comodín que da un único script se trata como ese script (`cap?.py` → `capi.py`). Lo que va
  detrás de `--` es posicional.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "eventos_guard"
AVISO_REAL = ("Un evento real enviado para probar ensucia el dataset del cliente y lo que Meta optimiza. Para "
              "probar usa el código de Events Manager → Probar eventos (`--test-code`). Confirma solo si es un envío "
              "real aprobado.")


def _test_en_archivo(arg: str, e: dict) -> bool:
    ruta = arg.split("@", 1)[1] if "@" in arg else ""
    if not ruta:
        return False
    try:
        return "test_event_code" in L.resolver_ruta(ruta, e).read_text(encoding="utf-8", errors="replace")[:2_000_000]
    except OSError:
        return False


CONSECUENCIA_OPACA = ("Si envía eventos a la Conversions API, se saltaría el aviso de evento real y el «solo "
                      "operador-meta».")
EJEMPLO_OPACO = "python3 -I herramientas/capi.py enviar --test-code …"
_PUEDE_ENVIAR = re.compile(r"(?i)\benviar\b|capi|/events\b|conversions")


def evaluar(e: dict, cmd: str) -> list:
    decisiones = []
    for seg, cwd in L.con_cwd(L.segmentos(cmd), e):
        opaca = L.ejecucion_opaca(seg, e, cwd, ("herramientas",), desconocida=True, cmd=cmd)
        if opaca and _PUEDE_ENVIAR.search(" ".join(seg["args"])):
            decisiones.append(L.decision_opaca(e, opaca, CONSECUENCIA_OPACA, EJEMPLO_OPACO))
            continue
        resto = L.args_de_script(seg, "capi.py")
        if resto is not None:
            sub, opts, _ = L.parsear_args(resto, ("test-code", "test_event_code", "cliente", "dataset", "evento",
                                                  "archivo"))
            if sub != "enviar":
                continue
            codigo = opts.get("test-code") or opts.get("test_event_code")
            if isinstance(codigo, str) and codigo.strip() and not opts.get("real"):
                decisiones.append(("ask", f"Envío de PRUEBA a la Conversions API con test_event_code «{codigo}»: "
                                          "aparece en Probar eventos y no cuenta para la optimización. Confirma."))
            elif L.es_subagente(e) and L.agente(e) != "operador-meta":
                decisiones.append(("deny", f"Los envíos reales a la Conversions API los hace `operador-meta` con un plan "
                                           f"aprobado; `{L.agente(e)}` solo prueba con `--test-code`. " + AVISO_REAL))
            else:
                decisiones.append(("ask", "EVENTO REAL a la Conversions API con capi.py (sin --test-code). "
                                          + AVISO_REAL))
            continue
        args = seg["args"]
        if not args:
            continue
        programa = L.base(args[0]).lower()
        urls = " ".join(a for a in args if "graph.facebook.com" in a)
        if programa in ("curl", "curl.exe", "wget", "http", "https", "xh") and re.search(r"/events\b", urls):
            metodo = next((args[i + 1].upper() for i, a in enumerate(args[:-1]) if a in ("-X", "--request")), "")
            con_datos = any(a.startswith(("-d", "--data", "-F", "--form", "--json", "--post")) for a in args)
            if metodo in ("", "GET") and not con_datos:
                continue
            prueba = "test_event_code" in " ".join(args) or any(_test_en_archivo(a, e) for a in args if "@" in a)
            if prueba:
                decisiones.append(("ask", "Envío de PRUEBA a la Conversions API (lleva test_event_code) fuera de "
                                          "capi.py. Confirma."))
            else:
                decisiones.append(("ask", "EVENTO REAL a la Conversions API con curl (sin test_event_code). "
                                          + AVISO_REAL))
    if not decisiones and re.search(r"graph\.facebook\.com[^\s'\"]*/events", cmd) and \
            re.search(r"(?i)\.(post|request)\s*\(|fetch\s*\(|urlopen", cmd):
        prueba = "test_event_code" in cmd
        decisiones.append(("ask", ("Envío de PRUEBA a la Conversions API desde un script en línea. Confirma."
                                   if prueba else "EVENTO REAL a la Conversions API desde un script en línea (sin "
                                                  "test_event_code). " + AVISO_REAL)))
    return decisiones


def logica(e: dict):
    if e.get("tool_name") != "Bash" or e.get("hook_event_name") != "PreToolUse":
        return None
    cmd = str((e.get("tool_input") or {}).get("command") or "")
    if "capi" not in cmd and "/events" not in cmd and not (L.lanza_python(cmd) and _PUEDE_ENVIAR.search(cmd)):
        return None
    return L.combinar(evaluar(e, cmd))


def main() -> int:
    return L.ejecutar(HOOK, logica)


if __name__ == "__main__":
    sys.exit(main())
