#!/usr/bin/env python3
"""Guardia del motor de vídeo con IA (PreToolUse sobre Bash).

El motor (`modulos/motor-ia/`, orden `uv run --project modulos/motor-ia motor <subcomando>`, o `python -m motor.cli`)
gasta dinero real con las claves del usuario (Gemini) y tiene cuota diaria. Antes de una orden de pago (contrato §14)
pide confirmación con un motivo claro y la registra en `logs/motor.jsonl`:
`run`, `regen`, `demo`, `actor create`, `edit` (con `--yes`, sin tope; sin `--yes`, hasta ~0,05 $ que el motor
ejecuta sin preguntar), `variant` con voz o idioma, `serve` (la interfaz web produce sin pasar por este hook), los
scripts de `modulos/motor-ia/scripts/` que llaman a modelos, y `gc` (borra temporales de trabajo).

Pasan sin preguntar las órdenes gratuitas (status, costs, list, plan-import, variantes de texto o formato, los
subcomandos gratuitos de los scripts) y todo lo que se ejecute con `MOTOR_MOCK=1` o `--simular` (sin gasto). Un
`MOTOR_MOCK` distinto de `1` en la orden, `env -u MOTOR_MOCK` o `env -i` desactivan la simulación.

cutkit (`uv run --project modulos/cutkit ck …`, o `python -m cutkit.cli`) es gratis y local salvo sus opciones de
pago, que también preguntan: `--subtitulos openai`, `--judge`, `--budget` mayor que 0 y las variables `CK_ASR=openai`
o `CK_MUSICA_IA` activada (`1`, `true`, `si`, `sí` o `yes`, en cualquier capitalización, como
`cutkit/audio/music.py`), en la orden, exportadas, en el entorno o en el `.env` de la raíz, que cutkit carga solo.

Python sobre modulos/ que el troceo no puede leer (comodines que no dan un único archivo, variables, `-c`, `-m`,
`..`) → ask en la sesión principal y deny en subagentes. Lo que va detrás de `--` no cuenta como opción.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "motor_guard"
VARIANTES_GRATIS = {"hook_text", "cta", "captions", "aspect", "music"}
SCRIPTS_GRATIS = {"list", "validar", "plan", "setup", "check", "--help", "-h", "help"}
SCRIPTS_SIEMPRE_DE_PAGO = {"auto_produce.py"}
_SCRIPT_MOTOR = re.compile(r"(^|[/\\])modulos[/\\]motor-ia[/\\]scripts[/\\][\w-]+\.py$")
SCRIPTS_CONOCIDOS = {"flow_style.py", "auto_produce.py", "pov_broll.py"}
_VARIABLES_CUTKIT = ("CK_ASR", "CK_MUSICA_IA")


def _posicionales(args: list) -> list:
    return [a for a in args if not a.startswith("-")]


_LANZADORES = re.compile(r"(?i)^(python[\d.]*w?|py|uv|uvx|pipx)(\.exe)?$")


def _ejecutado(args: list, i: int) -> bool:
    """El token i se ejecuta (es el programa, o lo lanza python/uv), no es un argumento de cat, grep, echo…"""
    return i == 0 or any(_LANZADORES.match(L.base(a)) for a in args[:i])


def _es_modulo(args: list, i: int, paquete: str) -> bool:
    """args[i] es `<paquete>` o `<paquete>.cli` lanzado con `python -m` (o `-m` pegado: `-mmotor.cli`)."""
    t = args[i]
    if t.startswith("-m") and len(t) > 2:
        t = t[2:]
    elif i == 0 or args[i - 1] not in ("-m", "--module"):
        return False
    return t in (paquete, f"{paquete}.cli", f"{paquete}.__main__")


def _es_motor(args: list, i: int) -> bool:
    t = args[i]
    nombre = L.base(t).lower()
    return (nombre in ("motor", "motor.exe") or nombre.endswith("scriptsmotor.exe")  # Windows sin comillas
            or _es_modulo(args, i, "motor") or t.replace("\\", "/").endswith("motor/cli.py"))


def _es_ck(args: list, i: int) -> bool:
    t = args[i]
    return (L.base(t).lower() in ("ck", "ck.exe") or _es_modulo(args, i, "cutkit")
            or t.replace("\\", "/").endswith("cutkit/cli.py"))


def _reconocido(args: list) -> bool:
    """El segmento lanza el motor, cutkit o un script conocido del motor (el hook sabe leerlo: no es opaco)."""
    def lanza(i: int, t: str) -> bool:
        return bool(_es_motor(args, i) or _es_ck(args, i) or _SCRIPT_MOTOR.search(t.replace("\\", "/"))
                    or any(t.endswith(s) for s in SCRIPTS_CONOCIDOS))
    return any(_ejecutado(args, i) and lanza(i, t) for i, t in enumerate(args))


def _partes(args: list) -> tuple:
    """(opciones y posicionales antes de `--`, posicionales): lo que va detrás de `--` siempre es posicional."""
    resto = L.antes_de_guion(args)
    detras = args[len(resto) + 1:] if "--" in args else []
    return resto, _posicionales(resto) + detras


def orden_de_pago(seg: dict):
    """Devuelve la descripción de la orden de pago del segmento, o None."""
    args = seg["args"]
    for i, t in enumerate(args):
        nombre = L.base(t).lower()
        if not _ejecutado(args, i):
            continue
        if _es_motor(args, i):
            resto, pos = _partes(args[i + 1:])
            sub = pos[0] if pos else ""
            if sub == "run":
                return "producir un anuncio completo (vídeo, imágenes y juez de calidad)"
            if sub == "demo":
                return "prueba real completa del motor (≈4–6 $)"
            if sub == "regen":
                return "regenerar una escena (vídeo)"
            if sub == "actor" and len(pos) > 1 and pos[1] == "create":
                return "crear un actor persistente (imágenes, ≈0,3 $)"
            if sub == "edit":
                if "--yes" in resto:
                    return "orden de edición de pago"
                return ("orden de edición (hasta ~0,05 $: el motor interpreta la orden con un modelo y ejecuta sin "
                        "preguntar lo que cueste menos; lo que cueste más devuelve el coste y pide --yes)")
            if sub == "serve":
                return ("arranca un servidor que puede producir vídeo de pago sin más preguntas (la interfaz en "
                        "http://127.0.0.1:8765 lanza producir, regenerar y variantes sin pasar por este hook)")
            if sub == "variant":
                tipo = pos[2] if len(pos) > 2 else ""
                if tipo not in VARIANTES_GRATIS:
                    return f"variante «{tipo or '¿?'}» con voz o idioma nuevos (A-roll de pago)"
            if sub == "gc":
                return "liberar disco del motor (borra temporales de trabajo)"
            return None
        if _SCRIPT_MOTOR.search(t.replace("\\", "/")) or any(t.endswith(s) for s in SCRIPTS_CONOCIDOS):
            resto, pos = _partes(args[i + 1:])
            if "--help" in resto or "-h" in resto:
                return None
            if nombre in SCRIPTS_SIEMPRE_DE_PAGO:
                return f"script del motor que produce con modelos de pago ({nombre})"
            if "--simular" in resto or (pos and pos[0] in SCRIPTS_GRATIS):
                return None
            return f"script del motor que llama a modelos ({nombre}{' ' + pos[0] if pos else ''})"
    return None


def _valor_opcion(args: list, opcion: str):
    """Valor de `--opcion valor` o `--opcion=valor` (el último gana), o None si no aparece."""
    valor = None
    for j, a in enumerate(args):
        if a == opcion and j + 1 < len(args):
            valor = args[j + 1]
        elif a.startswith(opcion + "="):
            valor = a.split("=", 1)[1]
    return valor


def musica_ia_activa(valor) -> bool:
    """La misma regla que `modulos/cutkit/cutkit/audio/music.py` (`musica_ia_activa`)."""
    return str(valor or "").strip().lower() in ("1", "true", "si", "sí", "yes")


def orden_cutkit_de_pago(seg: dict, variables: dict) -> list:
    """Opciones de pago de una orden `ck` (contrato §14). `variables`: CK_ASR y CK_MUSICA_IA vigentes para la orden."""
    args = seg["args"]
    for i, t in enumerate(args):
        if not _es_ck(args, i) or not _ejecutado(args, i):
            continue
        resto = L.antes_de_guion(args[i + 1:])
        if "--help" in resto or "-h" in resto:
            return []
        pagos = []
        if (_valor_opcion(resto, "--subtitulos") or "").lower() == "openai" or \
                str(variables.get("CK_ASR", "")).strip().lower() == "openai":
            pagos.append("subtítulos con OpenAI (≈0,006 $/min)")
        if "--judge" in resto:
            pagos.append("juez multimodal con Gemini")
        presupuesto = L.numero(_valor_opcion(resto, "--budget"))
        if presupuesto and presupuesto > 0:
            pagos.append(f"recursos de pago con tope de {presupuesto:g} $")
        if musica_ia_activa(variables.get("CK_MUSICA_IA")):
            pagos.append("música generada con IA (Lyria, ≈0,04–0,08 $ por canción)")
        return [f"cutkit: {p}" for p in pagos]
    return []


def _de_dotenv() -> dict:
    """CK_ASR y CK_MUSICA_IA del `.env` de la raíz, que cutkit carga sin pisar el entorno (solo esas dos claves;
    se leen con la credencial de `_lib` y nunca se imprimen ni se registran)."""
    return {k: L.credencial(k, entorno=False) for k in _VARIABLES_CUTKIT}


def _vigentes(seg: dict, shell: dict, dotenv: dict) -> dict:
    """Valor de cada variable de cutkit para esta orden: la de la orden, la de la shell (o nada si `env -u`/`env -i`
    la quitan) y, si no hay, la del `.env` (cutkit lo carga con `setdefault`)."""
    vigentes = {}
    for k in _VARIABLES_CUTKIT:
        if k in seg["env"]:
            valor = seg["env"][k]
        elif k in seg.get("unset", ()) or seg.get("vacio"):
            valor = None
        else:
            valor = shell.get(k)
        vigentes[k] = valor if valor not in (None, "") else dotenv.get(k)
    return vigentes


def _simulado(seg: dict, mock_shell: bool) -> bool:
    if "MOTOR_MOCK" in seg["env"]:
        return seg["env"]["MOTOR_MOCK"] == "1"
    if "MOTOR_MOCK" in seg.get("unset", ()) or seg.get("vacio"):
        return False
    return mock_shell


CONSECUENCIA_OPACA = ("Si produce vídeo o usa opciones de pago de cutkit, se saltaría el aviso de coste y el registro "
                      "en logs/motor.jsonl.")
EJEMPLO_OPACO = "uv run --project modulos/motor-ia motor …"


def logica(e: dict):
    if e.get("tool_name") != "Bash" or e.get("hook_event_name") != "PreToolUse":
        return None
    cmd = str((e.get("tool_input") or {}).get("command") or "")
    if not re.search(r"motor|flow_style|auto_produce|pov_broll|\bck\b|cutkit|modulos", cmd):
        return None
    mock_shell = os.environ.get("MOTOR_MOCK") == "1"
    shell = {k: os.environ.get(k) for k in _VARIABLES_CUTKIT}
    dotenv = None
    pagos = []
    opacas = []
    for seg, cwd in L.con_cwd(L.segmentos(cmd), e):
        args = seg["args"]
        if args[:1] == ["export"]:
            for a in args[1:]:
                k, igual, v = a.partition("=")
                if k == "MOTOR_MOCK" and igual:
                    mock_shell = v == "1"
                elif k in _VARIABLES_CUTKIT and igual:
                    shell[k] = v
            continue
        if args[:1] == ["unset"]:
            if "MOTOR_MOCK" in args[1:]:
                mock_shell = False
            for k in _VARIABLES_CUTKIT:
                if k in args[1:]:  # cutkit vuelve a cargar el `.env` de la raíz: unset no quita lo que diga ahí
                    shell[k] = None
            continue
        opaca = None if _reconocido(args) else L.ejecucion_opaca(seg, e, cwd, ("modulos",), desconocida=False, cmd=cmd)
        if opaca:
            opacas.append(opaca)
            continue
        if any(_es_ck(args, i) for i in range(len(args))):
            if dotenv is None:
                dotenv = _de_dotenv()
            pagos.extend(orden_cutkit_de_pago(seg, _vigentes(seg, shell, dotenv)))
        que = orden_de_pago(seg)
        if not que or _simulado(seg, mock_shell):
            continue
        pagos.append(que)
    if not pagos and not opacas:
        return None
    decisiones = [L.decision_opaca(e, o, CONSECUENCIA_OPACA, EJEMPLO_OPACO) for o in opacas]
    if pagos:
        L.registrar("motor.jsonl", {"ts": L.ts(), "session": e.get("session_id", ""), "agente": L.agente(e),
                                    "accion": "; ".join(pagos), "comando": cmd[:500]})
        decisiones.append(("ask", f"VÍDEO DE PAGO: {'; '.join(pagos)}. Gasta dinero real con tus claves (Gemini u "
                                  "OpenAI) o borra temporales. Antes, mira `/motor` (presupuesto del guardián y cuota "
                                  "del día) y confirma solo si has aprobado el coste estimado. Para probar el motor sin "
                                  "gastar, usa MOTOR_MOCK=1; cutkit sin esas opciones es gratis y local."))
    return L.combinar(decisiones)


def main() -> int:
    return L.ejecutar(HOOK, logica)


if __name__ == "__main__":
    sys.exit(main())
