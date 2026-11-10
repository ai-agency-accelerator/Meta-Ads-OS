#!/usr/bin/env python3
"""Secretos (PreToolUse sobre Bash): bloquea imprimir, copiar o mover tokens y el `.env`.

Bloquea (deny):
- cualquier orden que lea, copie, mueva, cargue o sobrescriba `.env` o `.env.*` (cat, grep, source, cp, python -c
  «open('.env')», > .env…). Se permiten solo comprobaciones sin contenido: ls, stat, test/[ ], chmod, touch,
  `git check-ignore` y `cp -n plantillas/env.ejemplo .env` (crearlo sin pisarlo);
- volcar el entorno (`env`, `printenv`, `export -p`, `declare -p`, `set` a secas) y expandir variables secretas
  (`$META_TOKEN`, `${GHL_TOKEN}`, `$env:STRIPE_KEY`, `%GEMINI_API_KEY%`…);
- comandos con un token pegado (EAA…, sk_live_…, pit-…, AIza…): se guarda en `.env`, no en la línea de órdenes;
- leer claves privadas o credenciales (id_rsa, *.pem, credentials*.json, .credentials.json, .netrc).
Cada argumento se mira ya resuelto: comodines (`cat .en?`, `cat .*`, con `glob` respecto al cwd o porque el patrón
casa con `.env`) y variables asignadas en la misma orden (`F=.env; cat $F`). Si alguno apunta a `.env`, deny.
Las herramientas de `herramientas/` cargan el `.env` solas: nunca hace falta leerlo desde la shell.
"""
from __future__ import annotations

import fnmatch
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "secretos"
_ENV = re.compile(r"(?<![\w-])\.env(?:\.[\w.-]+)?(?![\w-])")
_NOMBRE_SECRETO = r"[A-Z_][A-Z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD|PASSWD|CLAVE|WEBHOOK)[A-Z0-9_]*"
_VAR_SECRETA = re.compile(r"(?:\$\{?#?|\$env:)(" + _NOMBRE_SECRETO + r")|%(" + _NOMBRE_SECRETO + r")%")
_CREDENCIALES = re.compile(r"(?i)(^|[/\\])(id_rsa[\w.]*|id_ed25519[\w.]*|id_ecdsa[\w.]*|[\w.-]+\.pem|[\w.-]+\.p12|"
                           r"credentials[\w.-]*\.json|service[-_]account[\w.-]*\.json|\.credentials\.json|\.netrc|"
                           r"\.pgpass)$")
_METADATOS = {"ls", "stat", "test", "[", "[[", "chmod", "touch", "file"}
AYUDA = ("Las herramientas cargan el .env solas; para comprobar que existe usa `ls -l .env` o /doctor, y para "
         "añadir una clave ábrelo tú con tu editor.")


def _referencia_env(tok: str) -> bool:
    if tok.endswith(".ejemplo") or tok.endswith(".example"):
        return False
    return bool(_ENV.search(tok))


_NOMBRES_ENV = (".env", ".env.local", ".env.production", ".env.development")


def _apunta_a_env(tok: str, e: dict, cwd) -> bool:
    """El argumento, una vez resuelto por la shell, sería un `.env`: por glob respecto al cwd o porque su patrón
    (que empieza por punto, como `.en?` o `.*`) casa con el nombre."""
    if _referencia_env(tok):
        return True
    if not L.tiene_comodin(tok):
        return False
    final = tok.replace("\\", "/").rstrip("/").split("/")[-1]
    if final.startswith(".") and any(fnmatch.fnmatchcase(n, final) for n in _NOMBRES_ENV):
        return True
    return any(_referencia_env(r) for r in L.expandir(tok, e, cwd))


def _sustituir(tok: str, variables: dict) -> str:
    def valor(m):
        nombre = m.group(1) or m.group(2)
        return variables.get(nombre, m.group(0))
    return re.sub(r"\$\{(\w+)\}|\$(\w+)", valor, tok)


def revisar(cmd: str, e: dict | None = None):
    e = e or {}
    if L.contiene_token(cmd):
        return ("Ese comando lleva un token pegado. Los tokens van en el .env (nunca en la línea de órdenes ni en el "
                "chat). Si lo has pegado en el chat, revócalo y crea otro.")
    m = _VAR_SECRETA.search(cmd)
    if m:
        return (f"El comando expande la variable secreta {m.group(1) or m.group(2)}: podría imprimirla o mandarla fuera. Las "
                "herramientas la leen solas del .env.")
    variables: dict = {}
    for seg, cwd in L.con_cwd(L.segmentos(cmd), e):
        if not seg["args"]:
            variables.update(seg["env"])  # `F=.env; cat $F`
            continue
        if seg["args"][0] in ("export", "declare", "typeset", "local", "readonly"):
            variables.update(a.split("=", 1) for a in seg["args"][1:] if re.fullmatch(r"[A-Za-z_]\w*=.*", a))
        args = [_sustituir(a, {**variables, **seg["env"]}) for a in seg["args"]]
        programa = L.base(args[0]).lower()
        # `env` solo queda como programa si no le sigue ninguna orden (`env`, `env -u X`, `env A=1`): vuelca el entorno
        if programa in ("printenv", "env"):
            return "Volcar las variables de entorno puede imprimir tokens. Si necesitas una variable no secreta, pídela por su nombre con `echo $NOMBRE`."
        opciones = args[1:]
        if programa in ("export", "declare", "typeset") and ("-p" in opciones or all(a.startswith("-") for a in opciones)) \
                or (programa == "set" and len(args) == 1):
            return "Volcar las variables de la shell puede imprimir tokens."
        if any("/proc/" in a and "environ" in a for a in args):
            return "Leer el entorno de un proceso puede imprimir tokens."
        con_env = [a for a in args if _apunta_a_env(a, e, cwd)]
        if con_env:
            if programa in _METADATOS:
                continue
            if programa == "git" and len(args) > 1 and args[1] == "check-ignore":
                continue
            if programa == "git" and len(args) > 1 and args[1] in ("add", "commit", "stash"):
                return "El .env no se versiona nunca (lleva tus claves)."
            if programa == "cp" and "-n" in args and _referencia_env(args[-1]) and \
                    not any(_referencia_env(a) for a in args[1:-1]):
                continue
            return f"El .env no se lee, ni se copia, ni se carga, ni se sobrescribe desde la shell. {AYUDA}"
        if programa not in _METADATOS and any(_CREDENCIALES.search(a) for a in args[1:]):
            return "Ese archivo parece una clave privada o unas credenciales: no se leen ni se copian desde Claude."
    if _ENV.search(cmd) and re.search(r"(?i)\b(open|read|cat|type|get-content|load_dotenv|dotenv)\b", cmd):
        if not re.search(r"(?i)env\.(ejemplo|example)", cmd):
            return f"El .env no se lee desde la shell ni desde scripts en línea. {AYUDA}"
    return None


def logica(e: dict):
    if e.get("tool_name") != "Bash" or e.get("hook_event_name") != "PreToolUse":
        return None
    cmd = str((e.get("tool_input") or {}).get("command") or "")
    motivo = revisar(cmd, e)
    return L.pre("deny", motivo) if motivo else None


def main() -> int:
    return L.ejecutar(HOOK, logica)


if __name__ == "__main__":
    sys.exit(main())
