#!/usr/bin/env python3
"""Control de publicación (PreToolUse sobre el MCP de Meta y sobre Bash).

Sin un nombre de anuncio válido, el registro creativo y /siguiente-anuncio se quedan ciegos; sin veredicto de
políticas, se publica a ciegas. Por eso, al crear anuncios o creatividades (MCP o `meta_ads.py crear <plan>`):
- nombre de anuncio que no cumple la nomenclatura del contrato §7 → deny, con el nombre propuesto;
- creatividad, campaña o conjunto con nombre fuera de la nomenclatura → ask, con la regla;
- `LEEME.md` de la pieza (carpeta del vídeo o imagen, o búsqueda por nombre en `clientes/<c>/creativos/`), con la
  tabla del contrato §6: `OK` y `OK con cambios aplicados` → nada; `NO publicar` → deny; `OK con cambios`,
  `pendiente`, cualquier otro texto, sin línea de veredicto o LEEME no encontrado → ask.
`meta_ads.py crear --simular` no publica nada y no se revisa (`crear -- --simular` sí: lo que va detrás de `--` es
posicional). Sigue los `cd` y trata un comodín que da un único script como ese script (`meta_ad?.py` → `meta_ads.py`).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "control_publicacion"
POLITICAS = ("pásala por `revisor-politicas` (/revisar-anuncio): deja en su LEEME.md la línea "
             "«- **Veredicto de políticas:** OK · AAAA-MM-DD · <quién>»")
_CLAVES_NOMBRE = ("name", "nombre", "ad_name")
_CLAVES_RUTA = ("video", "imagen", "image", "miniatura", "ruta", "archivo", "creativo", "ruta_creativo", "file")


def _leemes(cliente) -> list:
    base = L.raiz() / "clientes"
    carpetas = [base / cliente / "creativos"] if cliente else sorted(base.glob("*/creativos"))
    encontrados = []
    for c in carpetas:
        if not c.is_dir():
            continue
        for patron in ("LEEME.md", "*/LEEME.md", "*/*/LEEME.md", "*/*/*/LEEME.md"):
            encontrados.extend(sorted(c.glob(patron)))
            if len(encontrados) > 800:
                return encontrados
    return encontrados


def leeme_por_ruta(ruta: str, e: dict):
    p = L.resolver_ruta(ruta, e)
    for carpeta in (p.parent, p.parent.parent, p.parent.parent.parent):
        f = carpeta / "LEEME.md"
        if f.is_file():
            return f
        if carpeta.name == "creativos":
            break
    return None


_SUFIJO_FORMATO = re.compile(r"(?i)_(?:9x16|4x5|1x1|16x9)$")


def sin_formato(nombre: str) -> str:
    """Quita el sufijo de formato (`_9x16`, `_4x5`, `_1x1`, `_16x9`) que añaden cutkit y render.py a los archivos."""
    return _SUFIJO_FORMATO.sub("", (nombre or "").strip())


def nombre_base(nombre: str) -> str:
    """Contrato §6/§7: la pieza vive en creativos/<nombre-base>/, el nombre del anuncio sin `_h<n>[-c<n>]`."""
    return re.sub(r"_h\d+(?:-c\d+)?$", "", sin_formato(nombre)).lower()


def leeme_por_nombre(nombre: str, cliente):
    partes = L.parsear_anuncio(nombre)
    base = nombre_base(nombre)
    mejor, puntos = None, 0
    for f in _leemes(cliente):
        carpeta = f.parent.name.lower()
        if base and carpeta == base:
            return f
        try:
            texto = f.read_text(encoding="utf-8", errors="replace")[:200_000]
        except OSError:
            continue
        p = 0
        if nombre in texto or nombre.lower() in carpeta:
            p = 3
        elif partes:
            fechas = (f"{partes['fecha']:%Y%m%d}", f"{partes['fecha']:%Y-%m-%d}")
            if partes["concepto"] in carpeta and any(x in carpeta for x in fechas):
                p = 2
            elif partes["concepto"] in carpeta or partes["concepto"] in texto:
                p = 1
        if p > puntos:
            mejor, puntos = f, p
    return mejor


def revisar_politicas(nombre: str, cliente, e: dict, rutas=()) -> tuple:
    """(decision|None, motivo) según el veredicto del LEEME.md de la pieza."""
    f = None
    for r in rutas:
        f = leeme_por_ruta(r, e)
        if f:
            break
    if f is None and nombre:
        f = leeme_por_nombre(nombre, cliente)
    if f is None:
        return "ask", f"No encuentro el LEEME.md de «{nombre}»: no sé si tiene veredicto de políticas. Antes de publicar, {POLITICAS}."
    try:
        veredicto = L.veredicto_leeme(f.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        veredicto = None
    try:
        donde = str(f.relative_to(L.raiz()))
    except ValueError:
        donde = str(f)
    if veredicto == "ok":
        return None, ""
    if veredicto == "no":
        return "deny", (f"El veredicto de políticas de «{nombre}» en {donde} es NO publicar. Reescribe la pieza con "
                        "revisor-politicas y actualiza el LEEME antes de crearla en Meta.")
    if veredicto == "pendiente":
        valor = L.valor_veredicto(f.read_text(encoding="utf-8", errors="replace")) or ""
        return "ask", (f"El veredicto de políticas de «{nombre}» en {donde} es «{valor[:60]}»: solo «OK» u «OK con "
                       "cambios aplicados» dejan publicar sin preguntar. Si los cambios ya están hechos, actualiza la "
                       "línea del LEEME; si no, aplícalos antes de crear el anuncio.")
    return "ask", f"{donde} no tiene veredicto de políticas. Antes de publicar «{nombre}», {POLITICAS}."


def _nombre(entrada: dict) -> str:
    for k in _CLAVES_NOMBRE:
        if isinstance(entrada.get(k), str):
            return entrada[k]
    return ""


def pre_mcp(e: dict):
    corto = e.get("tool_name", "").split("__")[-1]
    entrada = e.get("tool_input") or {}
    if corto not in ("ads_create_ad", "ads_create_creative", "ads_create_campaign", "ads_create_ad_set"):
        return None
    nombre = _nombre(entrada)
    cuentas = L.cuentas_en(entrada)
    cliente, _ = L.deducir_cliente(cuentas, ())
    decisiones = []
    if corto == "ads_create_campaign":
        ok, motivo = L.validar_nombre("campana", nombre)
        if not ok:
            decisiones.append(("ask", motivo))
    elif corto == "ads_create_ad_set":
        ok, motivo = L.validar_nombre("conjunto", nombre)
        if not ok:
            decisiones.append(("ask", motivo))
    elif corto == "ads_create_ad":
        ok, motivo = L.validar_nombre("anuncio", nombre)
        if not ok:
            decisiones.append(("deny", motivo + " Sin nombre válido, el registro creativo y /siguiente-anuncio se "
                                                "quedan ciegos."))
        else:
            decisiones.append(revisar_politicas(nombre, cliente, e))
    else:  # creatividad: suele llevar el nombre del archivo, con su sufijo de formato
        nombre = sin_formato(nombre)
        if nombre and not L.parsear_anuncio(nombre):
            decisiones.append(("ask", "Nombre de creatividad fuera de la nomenclatura de anuncios: "
                                      + L.validar_nombre("anuncio", nombre)[1]))
        elif nombre:
            decisiones.append(revisar_politicas(nombre, cliente, e))
    return L.combinar([d for d in decisiones if d[0]])


def _anuncios_del_plan(plan) -> list:
    anuncios = []
    for k, v, _ in L.recorrer(plan):
        if k.lower() in ("anuncios", "ads") and isinstance(v, list):
            anuncios.extend(a for a in v if isinstance(a, dict))
    return anuncios


def pre_bash(e: dict):
    cmd = str((e.get("tool_input") or {}).get("command") or "")
    if ("meta_ads" not in cmd and not L.lanza_python(cmd)) or "crear" not in cmd:
        return None
    decisiones = []
    # con_cwd sigue los `cd` y resuelve los comodines que dan un único archivo (`meta_ad?.py` → `meta_ads.py`); lo que
    # no se puede resolver lo frena meta_guard como ejecución opaca.
    for seg, cwd in L.con_cwd(L.segmentos(cmd), e):
        resto = L.args_de_script(seg, "meta_ads.py")
        if resto is None:
            continue
        sub, opts, pos = L.parsear_args(resto, ("cliente", "plan"))
        if sub != "crear" or opts.get("simular") or not pos:
            continue
        ruta_plan = L.resolver_ruta(pos[0], e, cwd)
        try:
            plan = json.loads(ruta_plan.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # meta_guard ya pregunta si el plan no se puede leer
        cliente = opts.get("cliente") if isinstance(opts.get("cliente"), str) else None
        if not cliente and isinstance(plan, dict) and isinstance(plan.get("cliente"), str):
            cliente = plan["cliente"]
        if not cliente:
            m = re.search(r"[/\\]clientes[/\\]([a-z0-9][a-z0-9-]*)[/\\]", str(ruta_plan.resolve()))
            cliente = m.group(1) if m else None
        campana = plan.get("campana") if isinstance(plan, dict) and isinstance(plan.get("campana"), dict) else {}
        if campana.get("nombre"):
            ok, motivo = L.validar_nombre("campana", str(campana["nombre"]))
            if not ok:
                decisiones.append(("ask", motivo))
        for conjunto in (plan.get("conjuntos") or []) if isinstance(plan, dict) else []:
            if isinstance(conjunto, dict) and conjunto.get("nombre"):
                ok, motivo = L.validar_nombre("conjunto", str(conjunto["nombre"]))
                if not ok:
                    decisiones.append(("ask", motivo))
        for anuncio in _anuncios_del_plan(plan):
            nombre = next((str(anuncio[k]) for k in _CLAVES_NOMBRE if anuncio.get(k)), "")
            ok, motivo = L.validar_nombre("anuncio", nombre)
            if not ok:
                decisiones.append(("deny", motivo + " Corrige el nombre en el plan: sin nombre válido, el registro "
                                                    "creativo y /siguiente-anuncio se quedan ciegos."))
                continue
            rutas = []
            for k in _CLAVES_RUTA:
                if isinstance(anuncio.get(k), str) and anuncio[k]:
                    r = anuncio[k]
                    if not pathlib.Path(r).is_absolute():
                        rutas.append(str(ruta_plan.parent / r))  # relativa al plan (como meta_ads.py)
                    rutas.append(r)  # o relativa a la raíz de la instancia
            decisiones.append(revisar_politicas(nombre, cliente, e, rutas))
    return L.combinar([d for d in decisiones if d[0]])


def logica(e: dict):
    if e.get("hook_event_name") != "PreToolUse":
        return None
    tool = e.get("tool_name", "")
    if tool.startswith("mcp__meta-ads__"):
        return pre_mcp(e)
    if tool == "Bash":
        return pre_bash(e)
    return None


def main() -> int:
    return L.ejecutar(HOOK, logica)


if __name__ == "__main__":
    sys.exit(main())
