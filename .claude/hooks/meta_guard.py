#!/usr/bin/env python3
"""Guardia de Meta Ads: MCP `meta-ads` (PreToolUse y PostToolUse) y `herramientas/meta_ads.py` vía Bash (PreToolUse).

- Registra todas las llamadas al MCP en `logs/meta-mcp.jsonl` y cada escritura ejecutada en `logs/cambios.jsonl`.
- Lecturas: no decide (las permite settings.json). Borrados: deny.
- Escrituras: ask con un motivo claro y, además:
  - **tope por cambio** (`topes.cambio_dia` de la ficha del cliente, deducido de la cuenta `act_` de la llamada, de
    los IDs ya registrados o de la única ficha): cualquier presupuesto diario, por cambio o por plan, por encima → deny.
    Ficha sin topes → deny. Cliente no deducible → el tope más estricto de todas las fichas.
  - En la API de Meta `daily_budget` va en la unidad mínima (céntimos, salvo monedas sin decimales). Si el valor es
    ambiguo, se compara también la lectura en unidades (nunca se subestima).
  - **tope diario total** (`topes.total_dia`) si existe `META_TOKEN`: suma lo activo de la cuenta con la Graph API
    (solo lectura) y bloquea si el cambio lo supera.
  - **regla de paciencia**: si la misma entidad cambió hace < 7 días, lo explica en la pregunta.
  - Solo `operador-meta` escribe: otro subagente → deny, y la sesión principal también (deny: «delega en
    operador-meta»; ninguna skill escribe desde la sesión principal). Crear algo ya ACTIVO → deny (todo se crea en
    pausa).
  - `status`/`configured_status` = DELETED en cualquier escritura → deny (borrar está bloqueado); ARCHIVED → ask
    explícito (no se puede deshacer desde aquí). `ads_boost_ig_post` → deny (no nace en pausa: se hace en Ads Manager).
  - Presupuesto que el hook no sabe leer como importe (objeto `{amount, currency}`, texto, una clave con `budget`,
    `spend_cap` o `spend_target` que no conoce) → deny. `lifetime_budget` sin `start_time`/`end_time` legibles → deny.
    Los importes se leen con el mismo `float()` que `herramientas/meta_ads.py` (`"9e3"` = 9000).
  - Si el hook falla dentro de una escritura en Meta, falla cerrado: deny («no he podido comprobar los topes»), en
    subagentes y en la sesión principal (que en el camino normal tampoco escribe). Lecturas: sin decisión.
- Bash: `meta_ads.py crear|activar|presupuesto|pausar` con las mismas reglas; escribir en graph.facebook.com con
  curl o un script en línea → deny (se saltaría topes, registro y change log).
  - En `crear <plan>` cuenta solo el presupuesto NUEVO, como `meta_ads.total_plan`: el de la campaña (CBO) o el de
    los conjuntos nuevos (ABO); los conjuntos con `id` y la campaña con `id` ya existen y no suman. También lo que
    venga en `api` (se envía tal cual a Meta). Un `status: ACTIVE` en el plan → deny.
- Bash: las otras herramientas que escriben en Meta son escrituras igual que `meta_ads.py` (solo `operador-meta`;
  ask con un motivo claro; el registro en `logs/cambios.jsonl` lo hace cada herramienta):
  - `reglas_meta.py crear|pausar|reactivar` (crear sin `--simular`): reglas que actúan solas, 24/7. Una propuesta con
    acciones que no sean avisar o pausar, o reglas que no sean programadas → deny;
  - `formularios_meta.py crear` (sin `--simular`) y `leads` (datos personales de terceros a `privado/`; lectura, así
    que no se limita a operador-meta);
  - `audiencias_meta.py crear|sincronizar` (sin `--simular`): datos de clientes hasheados a Meta.
- Bash: Python sobre herramientas/ o .claude/hooks/ que el troceo no puede leer (comodines que no dan un único
  script, variables, `-c`, `-m`, `runpy`, `exec`, `..`) → ask en la sesión principal y deny en subagentes. Un comodín
  que da un único script se trata como ese script. Todo lo que va detrás de `--` es posicional (`-- --simular` no
  simula).
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import urllib.parse
from datetime import timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "meta_guard"
KB_PACIENCIA = "meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md"

_BORRADO = {"delete", "remove", "destroy"}
_ESCRITURA = {"create", "update", "activate", "boost", "connect", "disconnect", "upload", "set", "publish",
              "duplicate", "copy", "pause", "archive", "enable", "disable", "add", "assign", "edit", "post", "send",
              "share", "launch"}
_LECTURA = {"get", "read", "search", "list", "check", "insights", "library", "preview", "estimate"}
_CLAVES_OBJETIVO = ("entity_id", "ad_entity_id", "object_id", "id", "entity_ids", "ids", "ad_entity_ids")
_CLAVES_PADRE = ("ad_id", "adset_id", "ad_set_id", "campaign_id", "creative_id")
_CLAVES_PUJA = re.compile(r"(?i)^(bid_amount|bid_strategy|bid_constraints|spend_cap|roas_average_floor|cost_cap)$")
CLI_ESCRITURA = ("crear", "activar", "presupuesto", "pausar")
CLI_CON_VALOR = ("cliente", "plan", "campana", "campana-id", "desde", "hasta", "mes", "salida", "evento", "pixel",
                 "motivo")
# Las otras herramientas que escriben en Meta: opciones que llevan valor (para no tomarlo por un posicional).
REGLAS_CON_VALOR = ("cliente", "avisar", "cpa", "evento", "madurez", "multiplicador", "campanas", "salida", "dias")
FORMULARIOS_CON_VALOR = ("cliente", "pagina", "desde", "hasta", "encaje", "horario", "salida")
AUDIENCIAS_CON_VALOR = ("cliente", "descripcion", "retencion", "etiqueta", "archivo", "contactos", "mapa",
                        "columna-etapa", "columna-estado", "columna-motivo", "columna-fecha", "pipeline", "columnas",
                        "prefijo", "pais", "motivo-timing", "excluir-etiqueta", "fecha", "control", "control-en",
                        "semilla", "agrupar", "dias-estancada", "manifiesto", "etiqueta-grupo", "etiqueta-control",
                        "segmento", "exito", "buscar")
SCRIPTS_META = ("meta_ads", "reglas_meta", "formularios_meta", "audiencias_meta")
ACCIONES_REGLA_OS = {"NOTIFICATION", "PAUSE"}


def clasificar(corto: str) -> str:
    partes = set(corto.lower().split("_"))
    if partes & _BORRADO:
        return "borrado"
    if partes & _ESCRITURA:
        return "escritura"
    if partes & _LECTURA:
        return "lectura"
    return "escritura"  # desconocida: se pregunta


def _ids(valor) -> list:
    if isinstance(valor, (list, tuple)):
        salida = []
        for v in valor:
            salida.extend(_ids(v))
        return salida
    if isinstance(valor, dict):
        return _ids(valor.get("id"))
    texto = str(valor or "").strip()
    return [texto] if re.fullmatch(r"\d{6,}", texto) else []


def ids_en(entrada: dict, claves) -> list:
    encontrados = []
    for k, v, _ in L.recorrer(entrada):
        if k.lower() in claves:
            for i in _ids(v):
                if i not in encontrados:
                    encontrados.append(i)
    return encontrados


def ids_objetivo(entrada: dict, corto: str) -> list:
    ids = ids_en(entrada, _CLAVES_OBJETIVO)
    if not ids and ("update" in corto or "activate" in corto):
        ids = ids_en(entrada, _CLAVES_PADRE)
    return ids


def _activa(entrada: dict) -> bool:
    return any(k.lower() in ("status", "configured_status") and str(v).upper() == "ACTIVE"
               for k, v, _ in L.recorrer(entrada))


def _pausa(entrada: dict) -> bool:
    return any(k.lower() in ("status", "configured_status") and str(v).upper() == "PAUSED"
               for k, v, _ in L.recorrer(entrada))


def _estado_irreversible(entrada) -> str | None:
    """DELETED o ARCHIVED si algún `status`/`configured_status` de la llamada (o del plan) lo pide."""
    estados = {str(v).strip().upper() for k, v, _ in L.recorrer(entrada)
               if k.lower() in ("status", "configured_status") and isinstance(v, str)}
    return "DELETED" if "DELETED" in estados else ("ARCHIVED" if "ARCHIVED" in estados else None)


BORRADO_POR_ESTADO = ("`status: DELETED` borra la entidad en Meta, y los borrados están bloqueados en Meta Ads OS. "
                      "Para que deje de gastar, páusala (`status: PAUSED`); si de verdad hay que borrarla, hazlo tú en "
                      "Ads Manager y anótalo en el change log.")
PROMOCIONAR = ("Promocionar publicaciones (`ads_boost_ig_post`) se hace en Ads Manager: aquí no puede nacer en pausa ni "
               "pasar por los topes de la ficha. Para anunciar una publicación existente, créala en pausa dentro de un "
               "conjunto de tu campaña (/organico-a-anuncios y /publicar-anuncios).")


def _ilegibles(lista: list) -> tuple:
    detalle = "; ".join(f"`{k}` {por_que}" for k, por_que in lista[:4])
    return ("deny", f"No sé leer el presupuesto como importe ({detalle}), así que no puedo comprobar el tope. Usa "
                    "`daily_budget` con un número en céntimos (5000 = 50 €/día) o `lifetime_budget` con `start_time` y "
                    "`end_time` en la misma llamada; o hazlo tú en Ads Manager.")


# ─────────────────────────────────────────────────────────────── topes


def comprobar_topes(cliente, como: str, pres: list, mon: str, activacion: bool) -> list:
    """Tope por cambio (`topes.cambio_dia`). Devuelve una lista de (decision, motivo)."""
    if not pres and not activacion:
        return []
    out = []
    if cliente:
        limite = L.tope(cliente, "cambio_dia")
        if limite is None:
            return [("deny", f"La ficha de «{cliente}» no tiene topes de gasto (`topes.cambio_dia` vacío o 0). Sin "
                             "topes no se crea presupuesto, ni se sube, ni se activa nada: define `topes.cambio_dia` y "
                             f"`topes.total_dia` en clientes/{cliente}/ficha.md (decisión tuya) y vuelve a intentarlo.")]
        de_quien = f"de «{cliente}»"
    else:
        topes = [t for t in (L.tope(s, "cambio_dia") for s in L.fichas()) if t]
        if not topes:
            return [("deny", f"No puedo aplicar ningún tope ({como}) y ninguna ficha tiene `topes.cambio_dia`. Crea "
                             "el cliente con /cliente-nuevo y define sus topes antes de tocar presupuestos o activar.")]
        limite = min(topes)
        de_quien = "más estricto de tus fichas"
        if pres:
            out.append(("ask", f"Ojo: {como}, así que aplico el tope por cambio más estricto de tus fichas "
                               f"({L.fmt_dinero(limite, mon)}/día). Pasa la cuenta act_… en la llamada para usar el "
                               "de su ficha."))
        else:
            out.append(("ask", f"Ojo: {como}; no puedo comprobar los topes de su ficha."))
    for p in pres:
        if p["diario"] is None:
            out.append(("deny", f"`{p['clave']}`: {p['nota']} ni comprobar el tope. Pasa `start_time` y `end_time` "
                                "legibles en la misma llamada (o en el mismo bloque del plan), usa un presupuesto "
                                "diario, o cámbialo tú en Ads Manager."))
        elif p["diario"] > limite + 1e-9:
            extra = (f" (presupuesto total de {L.fmt_dinero(p['importe_total'], mon)} en {p['dias']} días)"
                     if p.get("dias") else "")
            out.append(("deny", f"`{p['clave']}` = {L.fmt_dinero(p['diario'], mon)}/día{extra} supera el tope por "
                                f"cambio {de_quien} ({L.fmt_dinero(limite, mon)}/día). Si de verdad hace falta más, "
                                "sube `topes.cambio_dia` en la ficha (decisión tuya) o hazlo tú en Ads Manager."))
        elif p["alternativo"] and p["alternativo"] > limite + 1e-9:
            out.append(("ask", f"`{p['clave']}`: en la API de Meta el importe va en céntimos "
                               f"({L.fmt_dinero(p['diario'], mon)}/día), pero si venía en unidades serían "
                               f"{L.fmt_dinero(p['alternativo'], mon)}/día y superaría el tope "
                               f"({L.fmt_dinero(limite, mon)}/día). Comprueba la unidad antes de confirmar."))
    return out


def _graph() -> str:
    return "https://graph.facebook.com/" + os.environ.get("META_API_VERSION", "v27.0")  # igual que herramientas/_comun.py


def estado_cuenta(cuenta: str, token: str) -> dict:
    """Campañas y conjuntos de la cuenta con estado y presupuesto diario (en unidades de la moneda). Solo lectura."""
    info = L.http_get_json(f"{_graph()}/act_{cuenta}?fields=currency", token)
    mon = str(info.get("currency") or "EUR").upper()
    offset = 1 if mon in L.MONEDAS_OFFSET_1 else 100
    campos = urllib.parse.quote("id,status,daily_budget,campaign{id,status,daily_budget}")
    url = f"{_graph()}/act_{cuenta}/adsets?fields={campos}&limit=500"
    campanas: dict = {}
    conjuntos: dict = {}
    for _ in range(10):
        datos = L.http_get_json(url, token)
        for a in datos.get("data") or []:
            c = a.get("campaign") or {}
            cid = str(c.get("id") or a.get("campaign_id") or "")
            if cid and cid not in campanas:
                campanas[cid] = {"status": str(c.get("status") or ""),
                                 "diario": (L.numero(c.get("daily_budget")) or 0) / offset}
            conjuntos[str(a.get("id"))] = {"status": str(a.get("status") or ""), "campana": cid,
                                           "diario": (L.numero(a.get("daily_budget")) or 0) / offset}
        url = (datos.get("paging") or {}).get("next")
        if not url:
            break
    return {"moneda": mon, "campanas": campanas, "conjuntos": conjuntos}


def gasto_diario(estado: dict) -> float:
    total = 0.0
    for cid, c in estado["campanas"].items():
        if c["status"] != "ACTIVE":
            continue
        hijos = [a for a in estado["conjuntos"].values() if a["campana"] == cid]
        if c["diario"]:
            if any(a["status"] == "ACTIVE" for a in hijos):
                total += c["diario"]
        else:
            total += sum(a["diario"] for a in hijos if a["status"] == "ACTIVE")
    return total


def aplicar(estado: dict, cambios: list) -> None:
    """Simula los cambios. Activar es conservador: activa también padres e hijos (el peor caso de gasto)."""
    campanas, conjuntos = estado["campanas"], estado["conjuntos"]
    for tipo, eid, valor in cambios:
        if tipo == "presupuesto":
            if eid in conjuntos:
                conjuntos[eid]["diario"] = valor
            elif eid in campanas:
                campanas[eid]["diario"] = valor
        elif tipo == "activar":
            if eid in campanas:
                campanas[eid]["status"] = "ACTIVE"
                for a in conjuntos.values():
                    if a["campana"] == eid:
                        a["status"] = "ACTIVE"
            elif eid in conjuntos:
                conjuntos[eid]["status"] = "ACTIVE"
                if conjuntos[eid]["campana"] in campanas:
                    campanas[conjuntos[eid]["campana"]]["status"] = "ACTIVE"
        elif tipo == "pausar":
            if eid in campanas:
                campanas[eid]["status"] = "PAUSED"
            elif eid in conjuntos:
                conjuntos[eid]["status"] = "PAUSED"


def comprobar_total(cliente, cambios: list, extra: float = 0.0):
    """Tope diario total (`topes.total_dia`) con META_TOKEN. (decision, motivo) o None si no aplica."""
    if not cliente:
        return None
    limite = L.tope(cliente, "total_dia")
    cuenta = L.cuenta_de(cliente)
    if not limite or not cuenta:
        return None
    token = L.credencial("META_TOKEN", cliente)
    if not token:
        return None
    try:
        estado = estado_cuenta(cuenta, token)
    except Exception as e:
        return ("ask", f"No he podido comprobar el tope diario total de «{cliente}» con la API de Meta ({e}): "
                       "revisa en Ads Manager el gasto diario activo antes de confirmar.")
    mon = estado["moneda"]
    antes = gasto_diario(estado)
    aplicar(estado, cambios)
    despues = gasto_diario(estado) + extra
    if despues > limite + 1e-9 and despues > antes + 1e-9:
        return ("deny", f"Con este cambio el presupuesto diario activo de la cuenta de «{cliente}» pasaría de "
                        f"{L.fmt_dinero(antes, mon)} a {L.fmt_dinero(despues, mon)} y su tope diario total es "
                        f"{L.fmt_dinero(limite, mon)}. Baja o pausa otra cosa antes, o sube `topes.total_dia` en la "
                        "ficha (decisión tuya).")
    return ("ask", f"Presupuesto diario activo de la cuenta: {L.fmt_dinero(antes, mon)} → "
                   f"{L.fmt_dinero(despues, mon)} (tope total {L.fmt_dinero(limite, mon)}).")


def paciencia(ids: list) -> list:
    if not ids:
        return []
    limite = L.ahora() - timedelta(days=7)
    ultimos: dict = {}
    for fila in L.leer_jsonl("cambios.jsonl"):
        eid = str(fila.get("entidad_id") or "")
        if fila.get("sistema") != "meta" or eid not in ids:
            continue
        t = L.leer_ts(fila.get("ts"))
        if t and t >= limite:
            ultimos[eid] = (t, str(fila.get("accion") or "cambio"))
    salida = []
    for eid, (t, accion) in ultimos.items():
        dias = max(0, (L.ahora() - t).days)  # con META_ADS_OS_HOY en el pasado, un cambio de hoy quedaría «después»
        hace = "hoy" if dias == 0 else ("ayer" if dias == 1 else f"hace {dias} días")
        salida.append(("ask", f"Regla de paciencia: {eid} ya cambió el {t:%Y-%m-%d} ({accion}), {hace}. No lo "
                              "toques ni lo evalúes antes de 7 días salvo que algo esté roto "
                              f"({KB_PACIENCIA}, principio 7)."))
    return salida


def _solo_operador(e: dict):
    """Solo `operador-meta` escribe en Meta: ni los demás subagentes ni la sesión principal (todas las skills que
    escriben lo delegan en él; docs/desarrollo/notas/I5-seguridad.md)."""
    if L.agente(e) == "operador-meta":
        return None
    if L.es_subagente(e):
        return ("deny", f"Solo `operador-meta` escribe en Meta; `{L.agente(e)}` es de lectura. Devuelve el plan "
                        "a la sesión principal para que lo apruebe el usuario y lo ejecute operador-meta.")
    return ("deny", "Las escrituras en Meta las hace `operador-meta`, no la sesión principal: delega en operador-meta "
                    "con el plan aprobado (es lo que hacen /ejecutar-cambio, /lanzar-campana y /publicar-anuncios). "
                    "Así cada escritura pasa por sus límites, su confirmación y el change log.")


# ─────────────────────────────────────────────────────────────── MCP


def motivo_base(corto: str, entrada: dict, cliente, pres: list, activa: bool, mon: str) -> str:
    quien = f" para «{cliente}»" if cliente else ""
    if activa:
        return (f"ACTIVACIÓN en Meta{quien}: esto EMPIEZA A GASTAR dinero real. Confirma solo si el plan está "
                "aprobado, revisado por políticas y anotado en el change log.")
    if _estado_irreversible(entrada) == "ARCHIVED":
        return (f"ARCHIVAR en Meta{quien}: la entidad deja de entregar y queda archivada, y eso no se puede deshacer "
                "desde aquí. Si solo quieres que deje de gastar, páusala (`status: PAUSED`). Confirma solo si archivar "
                "es lo aprobado y anótalo en el change log.")
    if "custom_audience" in corto and ("users" in corto or "create" in corto):
        return (f"AUDIENCIA con datos de clientes{quien}: se suben datos personales (hasheados) a Meta. Confirma "
                "que hay base legal y consentimiento (RGPD) y que la lista sale de privado/, no de un archivo "
                "compartido.")
    if pres:
        lista = ", ".join(f"{p['clave']} → {L.fmt_dinero(p['diario'], mon)}/día" if p["diario"] is not None
                          else f"{p['clave']} (total)" for p in pres)
        return (f"Cambio de PRESUPUESTO en Meta{quien} ({lista}). Un salto grande puede reiniciar el aprendizaje: "
                "anota hipótesis, métrica y fecha de evaluación en el change log.")
    if any(_CLAVES_PUJA.match(k) for k, _, _ in L.recorrer(entrada)):
        return (f"Cambio de PUJA o LÍMITE DE GASTO en Meta{quien}. Comprueba la magnitud y anótalo en el change log.")
    if _pausa(entrada) and "update" in corto:
        return f"PAUSAR en Meta{quien}: deja de gastar y de aprender. Confirma que es lo aprobado."
    if "create" in corto:
        return (f"Escritura en Meta ({corto}){quien}. Lo nuevo se crea en PAUSA. Confirma que coincide con el plan "
                "aprobado.")
    return f"Escritura en Meta ({corto}){quien}. Confirma que coincide con el plan aprobado y anótalo en el change log."


def pre_mcp(e: dict):
    tool = e.get("tool_name", "")
    corto = tool.split("__")[-1]
    entrada = e.get("tool_input") or {}
    L.registrar("meta-mcp.jsonl", {"ts": L.ts(), "evento": "PreToolUse", "tool": tool, "agente": L.agente(e),
                                   "session": e.get("session_id", ""), "input": entrada})
    tipo = clasificar(corto)
    if tipo == "lectura":
        return None
    if tipo == "borrado":
        return L.pre("deny", "Los borrados en Meta están bloqueados en Meta Ads OS. Si de verdad hace falta, hazlo tú "
                             "en Ads Manager y anótalo en el change log del cliente.")
    if "boost" in corto.lower().split("_"):
        return L.pre("deny", PROMOCIONAR)
    if _estado_irreversible(entrada) == "DELETED":
        return L.pre("deny", BORRADO_POR_ESTADO)
    bloqueo = _solo_operador(e)
    if bloqueo:
        return L.pre(*bloqueo)
    if "create" in corto and _activa(entrada):
        return L.pre("deny", "Todo lo nuevo se crea en PAUSA: quita `status: ACTIVE` de la creación y activa después "
                             "con ads_activate_entity, con una confirmación específica.")
    ilegibles = L.presupuestos_ilegibles(entrada)
    if ilegibles:
        return L.pre(*_ilegibles(ilegibles))
    objetivo = ids_objetivo(entrada, corto)
    padres = ids_en(entrada, _CLAVES_PADRE)
    cliente, como = L.deducir_cliente(L.cuentas_en(entrada), objetivo + padres)
    mon = L.moneda(cliente)
    pres = L.presupuestos_en(entrada, mon)
    activa = "activate" in corto or ("update" in corto and _activa(entrada))
    decisiones = [("ask", motivo_base(corto, entrada, cliente, pres, activa, mon))]
    decisiones += comprobar_topes(cliente, como, pres, mon, activa)
    cambios = []
    if "create" not in corto:
        diarios = [p["diario"] for p in pres if p["diario"] is not None and not p["total"]]
        for eid in objetivo:
            if diarios:
                cambios.append(("presupuesto", eid, diarios[0]))
            if activa:
                cambios.append(("activar", eid, None))
    if cambios and not any(d == "deny" for d, _ in decisiones):
        total = comprobar_total(cliente, cambios)
        if total:
            decisiones.append(total)
    if "update" in corto:
        decisiones += paciencia(objetivo)
    return L.combinar(decisiones)


def _ha_fallado(resp, texto: str) -> bool:
    if isinstance(resp, dict) and (resp.get("isError") is True or resp.get("is_error") is True
                                   or ("error" in resp and not resp.get("id"))):
        return True
    if re.search(r'"(isError|is_error)"\s*:\s*true', texto):
        return True
    return isinstance(resp, str) and bool(re.match(r"(?i)\s*(error|failed)", resp))


def _ids_respuesta(texto: str) -> list:
    ids = re.findall(r'"(?:id|ad_id|adset_id|campaign_id|creative_id|entity_id|audience_id)"\s*:\s*"?(\d{6,})', texto)
    if not ids:
        ids = re.findall(r"(?<![\d_])(\d{12,20})(?!\d)", texto)
    vistos = []
    for i in ids:
        if i not in vistos:
            vistos.append(i)
    return vistos


def _resumen(entrada: dict) -> str:
    interes = re.compile(r"(?i)^(name|status|configured_status|daily_budget|lifetime_budget|bid_amount|bid_strategy|"
                         r"spend_cap|objective|optimization_goal|billing_event|entity_type|start_time|end_time)$")
    partes = []
    for k, v, _ in L.recorrer(entrada):
        if interes.match(k) and isinstance(v, (str, int, float)):
            partes.append(f"{k}={v}")
    return "; ".join(partes)[:400]


def post_mcp(e: dict):
    tool = e.get("tool_name", "")
    corto = tool.split("__")[-1]
    if clasificar(corto) == "lectura":
        return None
    entrada = e.get("tool_input") or {}
    resp = e.get("tool_response")
    texto = json.dumps(resp, ensure_ascii=False, default=str) if resp is not None else ""
    fallo = _ha_fallado(resp, texto)
    objetivo = ids_objetivo(entrada, corto)
    ids = (objetivo or _ids_respuesta(texto))[:20]
    cliente, _ = L.deducir_cliente(L.cuentas_en(entrada), ids + ids_en(entrada, _CLAVES_PADRE))
    L.registrar("meta-mcp.jsonl", {"ts": L.ts(), "evento": "PostToolUse", "tool": tool, "agente": L.agente(e),
                                   "session": e.get("session_id", ""), "input": entrada,
                                   "resultado": "error" if fallo else "ok", "ids": ids})
    if not fallo:
        detalle = _resumen(entrada)
        for eid in ids or [""]:
            L.registrar_cambio(e, "meta", corto, eid, cliente or "", detalle)
    return None


# ─────────────────────────────────────────────────────────────── Bash: meta_ads.py y escrituras directas

_CLIENTES_HTTP = {"curl", "curl.exe", "wget", "http", "https", "xh", "curlie"}


def escritura_http(seg: dict) -> bool:
    args = seg["args"]
    metodo = ""
    for i, a in enumerate(args):
        if a in ("-X", "--request", "--method") and i + 1 < len(args):
            metodo = args[i + 1].upper()
        m = re.match(r"^(?:-X|--request=|--method=)([A-Za-z]+)$", a)
        if m:
            metodo = m.group(1).upper()
    if metodo:
        return metodo != "GET"
    if any(a in ("-G", "--get") for a in args):
        return False
    if any(a.startswith(("-d", "--data", "-F", "--form", "--json", "--post-data", "--post-file", "-T", "--upload"))
           for a in args):
        return True
    return base0(seg) in ("http", "https", "xh") and any(re.fullmatch(r"(?i)(POST|PUT|PATCH|DELETE)", a)
                                                          for a in args[1:3])


def base0(seg: dict) -> str:
    return L.base(seg["args"][0]).lower() if seg["args"] else ""


def directo_a_graph(cmd: str, segs: list) -> list:
    if "graph.facebook.com" not in cmd:
        return []
    for seg in segs:
        if base0(seg) in _CLIENTES_HTTP and any("graph.facebook.com" in a for a in seg["args"]):
            urls = " ".join(a for a in seg["args"] if "graph.facebook.com" in a)
            if escritura_http(seg) and not re.search(r"/events\b", urls):
                return [("deny", "Escribir en la API de Meta con curl se salta los topes, el registro y el change log. "
                                 "Usa el MCP de Meta o `herramientas/meta_ads.py` (con operador-meta).")]
    if re.search(r"(?i)\.(post|delete)\s*\(", cmd) and not re.search(r"/events\b", cmd):
        return [("deny", "Escribir en la API de Meta desde un script en línea se salta los topes, el registro y el "
                         "change log. Usa el MCP de Meta o `herramientas/meta_ads.py` (con operador-meta).")]
    return []


def _leer_plan(ruta: str, e: dict, cwd):
    p = L.resolver_ruta(ruta, e, cwd)
    try:
        return json.loads(p.read_text(encoding="utf-8")), p
    except (OSError, ValueError):
        return None, p


def _slug_de_ruta(p) -> str | None:
    m = re.search(r"[/\\]clientes[/\\]([a-z0-9][a-z0-9-]*)[/\\]", str(p))
    return m.group(1) if m else None


def _presupuesto_propio(obj: dict, donde: str) -> list:
    """`presupuesto_diario` (o el alias `presupuesto_diario_eur`) de una campaña o un conjunto del plan, en unidades.

    Se lee con el mismo `float()` que `meta_ads.py` (`"9e3"` = 9000 €/día). Si hay valor y no se puede leer, el
    elemento va con `ilegible` (y `diario` 0) para que la pregunta no enseñe un importe falso.
    """
    crudo = obj.get("presupuesto_diario", obj.get("presupuesto_diario_eur"))
    n = L.numero(crudo)
    if n is None and crudo not in (None, "") and not isinstance(crudo, bool):
        return [{"clave": f"{donde}.presupuesto_diario", "diario": 0, "alternativo": None, "total": False,
                 "dias": None, "nota": "", "ilegible": str(crudo)[:40]}]
    if n is None or n <= 0:
        return []
    return [{"clave": f"{donde}.presupuesto_diario", "diario": n, "alternativo": None, "total": False, "dias": None,
             "nota": ""}]


def _presupuesto_api(obj: dict, donde: str, mon: str) -> list:
    """Presupuestos dentro de `api` (se envía tal cual a Meta: `daily_budget`/`lifetime_budget` en unidad mínima)."""
    api = obj.get("api")
    if not isinstance(api, dict):
        return []
    return [dict(p, clave=f"{donde}.api.{p['clave']}") for p in L.presupuestos_en(api, mon)]


def presupuestos_plan(plan: dict, mon: str) -> list:
    """Presupuesto diario NUEVO que mete un plan de `meta_ads.py crear` (mismo criterio que `meta_ads.total_plan`).

    - Campaña sin `id` con presupuesto → CBO: cuenta el de la campaña y no los de los conjuntos (no se envían).
    - Si no, cada conjunto NUEVO (sin `id`) con el suyo (ABO). Los conjuntos y la campaña con `id` ya existen: no suman.
    - Además, lo que haya en `api` de la campaña nueva y de los conjuntos nuevos, que Meta recibiría tal cual.
    """
    camp = plan.get("campana") if isinstance(plan.get("campana"), dict) else {}
    conjuntos = plan.get("conjuntos") if isinstance(plan.get("conjuntos"), list) else []
    nuevos = [c for c in conjuntos if isinstance(c, dict) and not c.get("id")]
    salida = []
    cbo = []
    if not camp.get("id"):
        cbo = _presupuesto_propio(camp, "campana")
        salida += cbo + _presupuesto_api(camp, "campana", mon)
    for i, c in enumerate(nuevos, 1):
        donde = str(c.get("nombre") or f"conjuntos[{i}]")
        if not cbo:
            salida += _presupuesto_propio(c, donde)
        salida += _presupuesto_api(c, donde, mon)
    return salida


def evaluar_cli(e: dict, sub: str, opts: dict, pos: list, cwd) -> list:
    explicito = opts.get("cliente") if isinstance(opts.get("cliente"), str) else None
    ids = [p for p in pos if re.fullmatch(r"\d{6,}", p)]
    plan, ruta_plan = None, None
    ruta = (pos[0] if sub == "crear" and pos else None) or (opts.get("plan") if isinstance(opts.get("plan"), str)
                                                            else None)
    if ruta:
        plan, ruta_plan = _leer_plan(ruta, e, cwd)
        if not explicito and isinstance(plan, dict) and isinstance(plan.get("cliente"), str):
            explicito = plan["cliente"]
        if not explicito and ruta_plan is not None:
            explicito = _slug_de_ruta(ruta_plan.resolve())
    cliente, como = L.deducir_cliente((), ids, explicito)
    mon = L.moneda(cliente)
    decisiones = []
    if sub == "crear":
        if plan is None:
            return [("ask", f"Crear en Meta con meta_ads.py, pero no he podido leer el plan «{ruta}»: no puedo "
                            "comprobar topes ni nombres. Revísalo antes de confirmar.")]
        if not isinstance(plan, dict):
            return [("ask", f"Crear en Meta con meta_ads.py, pero el plan «{ruta}» no es un objeto JSON: no puedo "
                            "comprobar topes ni nombres. Revísalo antes de confirmar.")]
        if _activa(plan):
            return [("deny", f"El plan {ruta} lleva `status: ACTIVE` (en `api` o en otro sitio): todo lo nuevo se "
                             "crea en PAUSA. Quítalo y activa después con `meta_ads.py activar --plan … --confirmo`, "
                             "con una confirmación específica.")]
        if _estado_irreversible(plan):
            return [("deny", f"El plan {ruta} lleva `status: {_estado_irreversible(plan)}`: todo lo nuevo se crea en "
                             "PAUSA (`PAUSED`). Quítalo del plan.")]
        lista = plan.get("conjuntos") if isinstance(plan.get("conjuntos"), list) else []
        bloques_api = [x.get("api") for x in [plan.get("campana")] + lista
                       if isinstance(x, dict) and isinstance(x.get("api"), dict)]
        ilegibles = [par for api in bloques_api for par in L.presupuestos_ilegibles(api)]
        if ilegibles:
            return [_ilegibles(ilegibles)]
        pres = presupuestos_plan(plan, mon)
        malos = [p for p in pres if p.get("ilegible")]
        if malos:
            return [("ask", f"Crear en Meta el plan {ruta}: importe ilegible en "
                            + ", ".join(f"`{p['clave']}` («{p['ilegible']}»)" for p in malos[:4])
                            + ". No puedo comprobar el tope ni decirte cuánto gasta: corrígelo con un número de "
                              "euros al día antes de confirmar.")]
        total = sum(p["diario"] or 0 for p in pres)
        conjuntos = plan.get("conjuntos") if isinstance(plan.get("conjuntos"), list) else []
        existentes = sum(1 for c in conjuntos if isinstance(c, dict) and c.get("id"))
        detalle = f"{len(conjuntos) - existentes} conjunto(s) nuevo(s)" + (
            f" y {existentes} existente(s) (no suman presupuesto)" if existentes else "")
        decisiones.append(("ask", f"Crear en Meta el plan {ruta}" + (f" para «{cliente}»" if cliente else "") +
                           f": {detalle}, {L.fmt_dinero(total, mon)}/día de presupuesto nuevo. Todo se crea "
                           "en PAUSA. Confirma que es el plan aprobado."))
        decisiones += comprobar_topes(cliente, como, pres, mon, False)
        limite = L.tope(cliente, "cambio_dia") if cliente else None
        if limite and len(pres) > 1 and total > limite + 1e-9:
            decisiones.append(("deny", f"El plan suma {L.fmt_dinero(total, mon)}/día y el tope por cambio de "
                                       f"«{cliente}» es {L.fmt_dinero(limite, mon)}/día (el tope vale por cambio y por "
                                       "plan). Divide el plan o sube `topes.cambio_dia` en la ficha (decisión tuya)."))
        return decisiones
    if sub == "presupuesto":
        eid = ids[0] if ids else ""
        resto = pos[pos.index(eid) + 1:] if eid in pos else pos
        eur = next((L.numero(x) for x in resto if L.numero(x) is not None), None)
        if eur is None:
            return [("ask", "Cambio de presupuesto con meta_ads.py sin importe legible: revísalo antes de confirmar.")]
        pres = [{"clave": "presupuesto", "diario": eur, "alternativo": None, "total": False, "dias": None,
                 "nota": ""}]
        decisiones.append(("ask", f"Cambio de PRESUPUESTO de {eid or '¿?'} a {L.fmt_dinero(eur, mon)}/día con "
                                  "meta_ads.py. Un salto grande puede reiniciar el aprendizaje: anota hipótesis, "
                                  "métrica y fecha de evaluación en el change log."))
        decisiones += comprobar_topes(cliente, como, pres, mon, False)
        if eid and not any(d == "deny" for d, _ in decisiones):
            total = comprobar_total(cliente, [("presupuesto", eid, eur)])
            if total:
                decisiones.append(total)
        decisiones += paciencia(ids)
        return decisiones
    if sub == "activar":
        decisiones.append(("ask", "ACTIVACIÓN con meta_ads.py" + (f" para «{cliente}»" if cliente else "") +
                           ": esto EMPIEZA A GASTAR dinero real. Confirma solo si el plan está aprobado, revisado por "
                           "políticas y anotado en el change log."))
        decisiones += comprobar_topes(cliente, como, [], mon, True)
        if not any(d == "deny" for d, _ in decisiones):
            extra = 0.0
            if isinstance(plan, dict) and not ids:  # `activar --plan` solo activa lo que creó el plan
                extra = sum(p["diario"] or 0 for p in presupuestos_plan(plan, mon))
            total = comprobar_total(cliente, [("activar", i, None) for i in ids], extra)
            if total:
                decisiones.append(total)
        return decisiones
    if sub == "pausar":
        decisiones.append(("ask", "PAUSAR con meta_ads.py" + (f" ({', '.join(ids)})" if ids else "") +
                           ": deja de gastar y de aprender. Confirma que es lo aprobado y anótalo en el change log."))
        decisiones += paciencia(ids)
    return decisiones


def _de_quien(opts: dict) -> str:
    cliente = opts.get("cliente") if isinstance(opts.get("cliente"), str) else ""
    return f" para «{cliente}»" if cliente else ""


def evaluar_reglas(e: dict, sub: str, opts: dict, pos: list, cwd) -> list:
    """`reglas_meta.py crear|pausar|reactivar`: reglas automáticas que actúan solas en los servidores de Meta."""
    ids = [p for p in pos if re.fullmatch(r"\d{6,}", p)]
    if sub == "pausar":
        return [("ask", "Desactivar reglas automáticas de Meta" + _de_quien(opts) + f" ({', '.join(ids) or '¿?'}): "
                        "dejan de proteger la cuenta. Confirma que es lo aprobado y anótalo en el change log.")]
    if sub == "reactivar":
        return [("ask", "Reactivar reglas automáticas de Meta" + _de_quien(opts) + f" ({', '.join(ids) or '¿?'}): "
                        "vuelven a actuar solas, 24/7, sin los hooks delante. Confirma que es lo aprobado.")]
    ruta = pos[0] if pos else ""
    datos, _ = _leer_plan(ruta, e, cwd) if ruta else (None, None)
    reglas = datos.get("reglas") if isinstance(datos, dict) else None
    if not isinstance(reglas, list):
        return [("ask", f"Crear reglas automáticas en Meta con reglas_meta.py, pero no he podido leer la propuesta "
                        f"«{ruta}»: no puedo comprobar qué hacen. Revísala antes de confirmar.")]
    cliente = opts.get("cliente") if isinstance(opts.get("cliente"), str) else datos.get("cliente")
    prohibidas, pausan, avisan = [], 0, 0
    for r in reglas:
        api = r.get("api") if isinstance(r, dict) else None
        api = api if isinstance(api, dict) else {}
        ejecucion = api.get("execution_spec") if isinstance(api.get("execution_spec"), dict) else {}
        evaluacion = api.get("evaluation_spec") if isinstance(api.get("evaluation_spec"), dict) else {}
        accion = str(ejecucion.get("execution_type") or "").upper()
        tipo = str(evaluacion.get("evaluation_type") or "").upper()
        if accion not in ACCIONES_REGLA_OS or tipo != "SCHEDULE":
            prohibidas.append(f"{api.get('name') or '¿sin nombre?'} ({accion or '¿?'}, {tipo or '¿?'})")
        elif accion == "PAUSE":
            pausan += 1
        else:
            avisan += 1
    if prohibidas:
        return [("deny", "El OS solo crea reglas programadas (SCHEDULE) que avisan o pausan: subir presupuesto, "
                         "encender, cambiar pujas o reglas con disparador actuarían en Meta sin topes ni hooks. Fuera de "
                         f"lo permitido: {', '.join(prohibidas[:5])}. Rehaz la propuesta con `reglas_meta.py proponer`.")]
    return [("ask", f"Crear {len(reglas)} reglas automáticas en Meta" + (f" para «{cliente}»" if cliente else "") +
                    f" ({pausan} pausan, {avisan} avisan): actúan solas, 24/7, en los servidores de Meta. Confirma que "
                    "es la propuesta aprobada y anótalo en el change log.")]


def evaluar_formularios(e: dict, sub: str, opts: dict, pos: list) -> list:
    if sub == "crear":
        plantilla = pos[0] if pos else "¿?"
        return [("ask", "Crear un FORMULARIO INSTANTÁNEO en la Página" + _de_quien(opts) + f" desde {plantilla}: no "
                        "gasta ni se usa hasta que un anuncio lo enlace, pero queda en la Página. Confirma que es la "
                        "plantilla aprobada y revisada por políticas, y anótalo en el change log.")]
    archivos = ("" if opts.get("sin-archivos")
                else " El detalle va a clientes/<cliente>/privado/ (nunca a datos/ ni a informes).")
    return [("ask", f"DESCARGAR LEADS del formulario {pos[0] if pos else '¿?'}" + _de_quien(opts) + ": son datos "
                    "personales de terceros (RGPD). Hazlo solo si hace falta (lo normal es que lleguen por el CRM)."
                    + archivos)]


def evaluar_audiencias(e: dict, sub: str, opts: dict, pos: list) -> list:
    if sub == "crear":
        nombre = pos[0] if pos else "¿?"
        return [("ask", f"Crear la audiencia de lista de clientes «{nombre}» en Meta" + _de_quien(opts) + " (vacía; "
                        "los datos se suben después con `sincronizar`). Confirma que es la del plan aprobado.")]
    archivo = opts.get("archivo") if isinstance(opts.get("archivo"), str) else "¿?"
    destino = pos[0] if pos else "¿?"
    modo = "SUSTITUYE la lista entera" if opts.get("reemplazar") else "AÑADE personas a la lista"
    fuera = "" if re.search(r"(^|[/\\])privado[/\\]", archivo) else (" Ojo: el archivo no está en "
                                                                     "clientes/<cliente>/privado/.")
    return [("ask", "AUDIENCIA con datos de clientes" + _de_quien(opts) + f": {archivo} a {destino} ({modo}). Se "
                    "suben datos personales hasheados a Meta: confirma que hay base legal y consentimiento (RGPD) y "
                    "que es el plan aprobado." + fuera)]


CONSECUENCIA_OPACA = ("Si escribe en Meta, se saltaría los topes de la ficha, la regla de paciencia y el «solo "
                      "operador-meta».")
EJEMPLO_OPACO = "python3 -I herramientas/meta_ads.py …"


def pre_bash(e: dict):
    cmd = str((e.get("tool_input") or {}).get("command") or "")
    if not any(s in cmd for s in SCRIPTS_META) and "graph.facebook.com" not in cmd and not L.lanza_python(cmd):
        return None
    segs = L.segmentos(cmd)
    decisiones = directo_a_graph(cmd, segs)
    for seg, cwd in L.con_cwd(segs, e):
        opaca = L.ejecucion_opaca(seg, e, cwd, ("herramientas", ".claude/hooks"), desconocida=True, cmd=cmd)
        if opaca:
            decisiones.append(L.decision_opaca(e, opaca, CONSECUENCIA_OPACA, EJEMPLO_OPACO))
            continue
        resto = L.args_de_script(seg, "meta_ads.py")
        if resto is not None:
            sub, opts, pos = L.parsear_args(resto, CLI_CON_VALOR)
            if sub not in CLI_ESCRITURA or (sub == "crear" and opts.get("simular")):
                continue
            decisiones += [_solo_operador(e)] if _solo_operador(e) else evaluar_cli(e, sub, opts, pos, cwd)
            continue
        resto = L.args_de_script(seg, "reglas_meta.py")
        if resto is not None:
            sub, opts, pos = L.parsear_args(resto, REGLAS_CON_VALOR)
            if sub in ("pausar", "reactivar") or (sub == "crear" and not opts.get("simular")):
                decisiones += [_solo_operador(e)] if _solo_operador(e) else evaluar_reglas(e, sub, opts, pos, cwd)
            continue
        resto = L.args_de_script(seg, "formularios_meta.py")
        if resto is not None:
            sub, opts, pos = L.parsear_args(resto, FORMULARIOS_CON_VALOR)
            if sub == "crear" and not opts.get("simular"):
                decisiones += [_solo_operador(e)] if _solo_operador(e) else evaluar_formularios(e, sub, opts, pos)
            elif sub == "leads":
                decisiones += evaluar_formularios(e, sub, opts, pos)
            continue
        resto = L.args_de_script(seg, "audiencias_meta.py")
        if resto is not None:
            sub, opts, pos = L.parsear_args(resto, AUDIENCIAS_CON_VALOR)
            if sub in ("crear", "sincronizar") and not opts.get("simular"):
                decisiones += [_solo_operador(e)] if _solo_operador(e) else evaluar_audiencias(e, sub, opts, pos)
    return L.combinar(decisiones)


def logica(e: dict):
    evento = e.get("hook_event_name")
    tool = e.get("tool_name", "")
    if tool.startswith("mcp__meta-ads__"):
        if evento == "PreToolUse":
            return pre_mcp(e)
        if evento == "PostToolUse":
            return post_mcp(e)
    elif tool == "Bash" and evento == "PreToolUse":
        return pre_bash(e)
    return None


_ESCRIBE_EN_BASH = re.compile(r"(meta_ads|reglas_meta|formularios_meta|audiencias_meta)[\s\S]*"
                              r"\b(crear|activar|presupuesto|pausar|reactivar|sincronizar)\b|graph\.facebook\.com")


def al_fallar(e: dict):
    """Si la lógica falla en una escritura en Meta, no se queda sin decisión: ask (principal) o deny (subagente)."""
    if e.get("hook_event_name") != "PreToolUse":
        return None
    tool = str(e.get("tool_name") or "")
    if tool.startswith("mcp__meta-ads__"):
        tipo = clasificar(tool.split("__")[-1])
        if tipo == "lectura":
            return None
        if tipo == "borrado":
            return L.pre("deny", "Los borrados en Meta están bloqueados en Meta Ads OS.")
    elif tool == "Bash":
        if not _ESCRIBE_EN_BASH.search(str((e.get("tool_input") or {}).get("command") or "")):
            return None
    else:
        return None
    if L.es_subagente(e):
        return L.pre("deny", "No he podido comprobar los topes (fallo interno de meta_guard; el detalle queda en "
                             "logs/hooks.jsonl): un subagente no escribe en Meta sin esa comprobación. Devuelve el plan "
                             "a la sesión principal y que el usuario lo haga en Ads Manager o arregle el hook (/doctor).")
    # La sesión principal nunca escribe en Meta (deny «delega en operador-meta» en el camino normal): el fallo no puede
    # ser más flojo que eso, así que también es deny.
    return L.pre("deny", "No he podido comprobar los topes (fallo interno de meta_guard; el detalle queda en "
                         "logs/hooks.jsonl). Además, las escrituras en Meta las hace operador-meta, no la sesión "
                         "principal. Hazlo en Ads Manager o arregla el hook (/doctor) antes de volver a intentarlo.")


def main() -> int:
    return L.ejecutar(HOOK, logica, al_fallar)


if __name__ == "__main__":
    sys.exit(main())
