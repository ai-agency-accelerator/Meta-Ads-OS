#!/usr/bin/env python3
"""Reglas automáticas de Meta por cliente: la protección que sigue actuando con el ordenador apagado.

Las reglas viven en los servidores de Meta y se evalúan solas, también de madrugada. Esta herramienta solo crea
reglas que AVISAN o PAUSAN: nunca suben presupuesto, ni encienden nada, ni cambian pujas, porque eso se haría en los
servidores de Meta sin pasar por los topes de la ficha ni por los hooks.

Leer (no cambia nada):
  python3 -I herramientas/reglas_meta.py listar --cliente acme             reglas de la cuenta, auditadas contra la KB
  python3 -I herramientas/reglas_meta.py historial --cliente acme [--dias 7] [--todas]  qué han hecho las reglas
                                                         (--todas: también lo que solo avisaron, para el modo sombra)
  python3 -I herramientas/reglas_meta.py destinatarios --cliente acme       personas de la cuenta (IDs para --avisar)

Proponer (sin red; solo escribe un archivo):
  python3 -I herramientas/reglas_meta.py proponer --cliente acme [--cpa 80] [--evento Lead] [--madurez 0]
      [--conversiones-semana N] [--multiplicador 4] [--activo] [--campanas ID,ID] [--avisar ID,ID] [--salida RUTA]
  → clientes/acme/planes/reglas-AAAA-MM-DD.json (CPA objetivo, topes y evento salen de la ficha)
  Por defecto, modo sombra: las pausas por conversión solo avisan las primeras 1–2 semanas (KB 07 §6.2). Tras revisar
  qué habrían hecho, `proponer --activo` + `crear` y `pausar` las versiones «-sombra».

Escribir (solo `operador-meta`, con el sí del usuario; los permisos piden confirmación):
  python3 -I herramientas/reglas_meta.py crear <json> --cliente acme --simular [--pasos]  revisa sin red; --pasos
                                                                                     = guía para Ads Manager
  python3 -I herramientas/reglas_meta.py crear <json> --cliente acme --confirmo   crea en Meta (no duplica por nombre)
  python3 -I herramientas/reglas_meta.py pausar <id>… --cliente acme --confirmo   desactiva reglas (no las borra)
  python3 -I herramientas/reglas_meta.py reactivar <id>… --cliente acme --confirmo  solo reglas que avisan o pausan

Conjunto por defecto (detalle y porqués en docs/guias/reglas-automaticas.md):
  PROTECT  anuncio sin conversión tras k× el CPA objetivo de gasto ya madurado y más de 2.000 impresiones · en
           cuentas con volumen (--conversiones-semana ≥ 30), también el conjunto. k = 4 en cuentas pequeñas (por
           defecto: <30 conversiones/semana por campaña, KB 07 «Implicaciones operativas»; ahí el conjunto solo
           avisa) y 3 con volumen; nunca por debajo de 2; en sombra solo avisan · gasto de hoy de un conjunto por
           encima de 2,2× topes.cambio_dia (pausa siempre, también en sombra: es seguridad de dinero)
  ALERT    gasto de hoy por encima de 1,75× el tope · sin conversiones recientes · CPA > 2× con ≥3 resultados en una
           ventana madurada · conjunto que ayer no entregó
«Madurez» = días que tarda en llegar el evento principal (0 para Lead; más para cita, lead cualificado o venta B2B):
el gasto de esos últimos días no cuenta para matar nada, porque sus conversiones aún no han tenido tiempo de llegar.

API: objetos `adrules_library` de la Marketing API (evaluation_spec SCHEDULE, execution_spec, schedule_spec).
Importes en la unidad mínima de la moneda (céntimos en EUR). Versión de la Graph API: la de `meta_ads.py`.

Credenciales (`.env` en la raíz, nunca se imprimen): META_TOKEN_<SLUG> o META_TOKEN (usuario del sistema,
docs/guias/token-avanzado.md). Sin token, `proponer` y `crear --simular --pasos` sirven para hacerlo en Ads Manager.

Códigos de salida: 0 bien · 1 error del usuario (JSON inválido, regla prohibida, falta --confirmo, algo pendiente) ·
2 configuración (ficha, topes, CPA objetivo, token, cuenta de ejemplo, moneda distinta).
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun as comun  # noqa: E402
import meta_ads as M  # noqa: E402

FORMATO = "reglas-meta-os/1"
ACCIONES_OS = ("NOTIFICATION", "PAUSE")
MARCA_OS = "_OS_"

# Gasto diario: Meta puede gastar hasta el 175 % del presupuesto diario en un día (210 % con ad set budget sharing).
# [OFFICIAL META] meta-ads-kb/02-estructura-campanas/06-presupuesto-por-niveles.md §1
ALERTA_GASTO = 1.75   # × topes.cambio_dia: el máximo legal sin budget sharing
PAUSA_GASTO = 2.2     # × topes.cambio_dia: por encima del máximo con budget sharing (2,1) + margen [HYPOTHESIS]
CPA_ALERTA = 2        # × CPA objetivo, con ≥3 resultados en ventana madurada [STRONG INFERENCE]
MIN_RESULTADOS = 3
HORAS_MIN = 72        # KB_REGLAS §4.B.1 [EMPIRICAL]
IMPRESIONES_MIN = 100  # entrega casi nula (§4.A.1) [EMPIRICAL]
IMPRESIONES_KILL = 2000  # kill switch lifetime a nivel de anuncio (§4.B.1) [STRONG INFERENCE]
# Cuenta pequeña: <30 conversiones/semana por campaña → solo alertas + kill switch lifetime ≥4×C por anuncio
# (KB_REGLAS, «Implicaciones operativas»). Sin el dato, se supone pequeña: es lo normal en B2B de ticket alto y lo
# prudente (a 4× cae un 1,8 % de anuncios buenos; a 3×, un 5 %).
CONVERSIONES_SEMANA_GRANDE = 30
K_PEQUENA, K_GRANDE = 4.0, 3.0
CPA_TOPE_MIN = 0.05   # k × CPA por debajo del 5 % del tope por cambio: casi seguro una celda mal leída [HYPOTHESIS]
CAMBIO_CLIC = "2026-03-03"  # click-through solo con link clicks: umbrales anteriores, a recalibrar (§3)

KB_REGLAS = "meta-ads-kb/10-cambios-2025-2026-api-ia-automatizacion/07-reglas-automaticas.md"
KB_PRINCIPIOS = "meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md"
KB_PACIENCIA = "meta-ads-kb/09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md"
KB_PRESUPUESTO = "meta-ads-kb/02-estructura-campanas/06-presupuesto-por-niveles.md"
KB_MITOS = "meta-ads-kb/12-mitos-contradicciones/01-mitos-meta-ads-2026.md"

SIN_TOKEN = ("Sin token no puedo leer ni crear reglas: el MCP de Meta no tiene herramientas de reglas automáticas. "
             "Opciones: hazlo en Ads Manager → Reglas automatizadas (`crear <json> --simular --pasos` te da los pasos) "
             "o configura META_TOKEN (docs/guias/token-avanzado.md, `/conectar meta --avanzado`).")


def _salir(mensaje: str, codigo: int) -> None:
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


def _json(datos) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2, default=str))


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def _clave(texto: str) -> str:
    return re.sub(r"[^a-z]", "", _norm(texto))


# ---------------------------------------------------------------- eventos y madurez

@dataclass(frozen=True)
class Evento:
    nombre: str
    fila: str | None              # inicio (normalizado) de la fila de «Economía» de la ficha con su coste objetivo
    objetivos: tuple[str, ...]    # optimization_goal de los conjuntos que persiguen este evento
    madurez: int | dict           # días que tarda en llegar [HYPOTHESIS]; dict por `tipo` de la ficha ("_" = resto)


_WEB = ("OFFSITE_CONVERSIONS",)
EVENTOS = {_clave(e.nombre): e for e in [
    Evento("Lead", "cpl", ("OFFSITE_CONVERSIONS", "LEAD_GENERATION"), 0),
    Evento("Contact", "cpl", _WEB, 0),
    Evento("SubmitApplication", "cpl", ("OFFSITE_CONVERSIONS", "LEAD_GENERATION"), 0),
    Evento("CompleteRegistration", "cpl", _WEB, 0),
    Evento("DiagnosticoCompletado", "cpl", _WEB, 0),
    Evento("StartTrial", "coste por prueba", _WEB, 0),
    Evento("LeadCualificado", "coste por lead cualificado", ("OFFSITE_CONVERSIONS", "QUALITY_LEAD"), 3),
    Evento("Schedule", "coste por cita", _WEB, 3),
    Evento("LlamadaAsistida", None, _WEB, 7),
    Evento("PropuestaEnviada", None, _WEB, 14),
    Evento("Subscribe", "coste por venta", _WEB, {"saas": 14, "_": 0}),
    Evento("Purchase", "coste por venta", ("OFFSITE_CONVERSIONS", "VALUE"),
           {"ecommerce": 0, "infoproducto": 0, "app": 0, "saas": 14, "_": 28}),
]}

# Gasto «reciente» que se descuenta por madurez: (madurez máxima en días, prefijo de la API, días que cubre).
# Para LIFETIME (incluye hoy) se resta un periodo que también incluye hoy: hoy + los últimos `madurez` días.
RECIENTE = [(0, "today_", 1), (1, "last_2_days_", 2), (2, "last_3_days_", 3), (6, "last_7_days_", 7),
            (13, "last_14_days_", 14), (27, "last_28_days_", 28), (29, "last_30_days_", 30)]
# Para una ventana cerrada (sin hoy) se resta un periodo cerrado: los últimos `madurez` días antes de hoy.
RECIENTE_CERRADO = [(1, "yesterday_", 1), (3, "last_3d_", 3), (7, "last_7d_", 7), (14, "last_14d_", 14),
                    (28, "last_28d_", 28), (30, "last_30d_", 30)]
# Ventanas cerradas (sin hoy): (días, time_preset, prefijo).
VENTANAS = [(3, "LAST_3D", "last_3d_"), (7, "LAST_7D", "last_7d_"), (14, "LAST_14D", "last_14d_"),
            (28, "LAST_28D", "last_28d_"), (30, "LAST_30D", "last_30d_")]
MADUREZ_MAX = 29
VENTANA_MAX_SIN_CONVERSIONES = 14  # más larga ya no es «reciente» [HYPOTHESIS]


def evento(nombre: str) -> tuple[Evento, bool]:
    """(evento, conocido). Acepta «Lead», «LEAD», «lead_cualificado», «COMPLETE_REGISTRATION»…"""
    e = EVENTOS.get(_clave(nombre))
    return (e, True) if e else (Evento(str(nombre), None, _WEB, 7), False)


def madurez_por_defecto(e: Evento, tipo: str) -> int:
    if isinstance(e.madurez, dict):
        return e.madurez.get(tipo, e.madurez["_"])
    return e.madurez


def reciente(dias: int) -> tuple[str, int]:
    """Periodo con hoy que cubre hoy + `dias` días: lo que se resta al gasto de por vida."""
    for tope, prefijo, cubre in RECIENTE:
        if dias <= tope:
            return prefijo, cubre
    raise ValueError(dias)


def reciente_cerrado(dias: int) -> tuple[str, int]:
    """Periodo sin hoy que cubre los últimos `dias` días cerrados (dias ≥ 1): lo que se resta a una ventana cerrada."""
    for tope, prefijo, cubre in RECIENTE_CERRADO:
        if dias <= tope:
            return prefijo, cubre
    raise ValueError(dias)


def ventana_alcanzable(minimo: int, maximo: int, sin_madurar: int, umbral: float,
                       tope_dia: float) -> tuple[tuple[int, str, str] | None, int]:
    """(ventana, días ya madurados) más corta entre `minimo` y `maximo` días en la que un conjunto que gasta el tope
    cada día llega a `umbral` con el gasto ya madurado. (None, 0) si ninguna: la regla no saltaría nunca."""
    for v in VENTANAS:
        maduros = v[0] - sin_madurar
        if minimo <= v[0] <= maximo and maduros > 0 and umbral / maduros <= tope_dia + 1e-9:
            return v, maduros
    return None, 0


# ---------------------------------------------------------------- CPA objetivo desde la ficha

def numero(celda: str) -> float | None:
    """Primer número de una celda: «80 €», «1.200,50», «1 200 €», «1,200», «≈ 95», «80.5 (sin IVA)». None si no hay
    o si no es positivo. La regla es la de `_comun.numero`, la misma en todas las herramientas."""
    v = comun.numero(celda)
    return v if v and v > 0 else None


def celda_de_ficha(slug: str, fila: str | None) -> tuple[float | None, str, str]:
    """(importe, columna, texto de la celda) de la tabla «Economía» de la ficha: target y, si no hay, break-even."""
    if not fila:
        return None, "", ""
    texto = (comun.ruta_cliente(slug) / "ficha.md").read_text(encoding="utf-8")
    for linea in texto.splitlines():
        if not linea.strip().startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 3 or not _norm(celdas[0]).startswith(fila):
            continue
        objetivo, equilibrio = numero(celdas[2]), numero(celdas[1])
        if objetivo:
            return objetivo, "target", celdas[2]
        if equilibrio:
            return equilibrio, "break-even", celdas[1]
        return None, "", ""
    return None, "", ""


def cpa_de_ficha(slug: str, fila: str | None) -> tuple[float | None, str]:
    """(importe, columna) de la tabla «Economía» de la ficha: target y, si no hay, break-even."""
    importe, columna, _ = celda_de_ficha(slug, fila)
    return importe, columna


# ---------------------------------------------------------------- dinero

def a_minimo(importe: float, moneda: str) -> int:
    return M.a_minimo(importe, moneda)


def de_minimo(valor, moneda: str) -> float:
    return float(valor) / (1 if moneda in M.SIN_DECIMALES else 100)


def dinero(importe: float, moneda: str) -> str:
    return f"{M._n(importe, 0 if moneda in M.SIN_DECIMALES else 2)} {moneda}"


def _corto(importe: float) -> str:
    """80 → «80», 80.5 → «80,5», 1.75 → «1,75» (para nombres y textos)."""
    return f"{float(importe):.2f}".rstrip("0").rstrip(".").replace(".", ",")


def _pct(x: float) -> str:
    return f"{x * 100:.1f}".replace(".", ",") + " %"


# ---------------------------------------------------------------- construir el conjunto por defecto

def _f(campo: str, operador: str, valor) -> dict:
    return {"field": campo, "value": valor, "operator": operador}


def _a_las(*horas: int) -> dict:
    return {"schedule_type": "CUSTOM",
            "schedule": [{"start_minute": h * 60, "end_minute": h * 60} for h in horas]}


CADA_MEDIA_HORA = {"schedule_type": "SEMI_HOURLY"}


@dataclass
class Opciones:
    moneda: str
    evento: Evento
    cpa: float
    k: float
    madurez: int
    tope_cambio: float
    sombra: bool
    campanas: list[int]
    avisar: list[int]
    pequena: bool = False


def _base(o: Opciones, nivel: str, preset: str, conversion: bool) -> list[dict]:
    filtros = [_f("entity_type", "EQUAL", nivel), _f("time_preset", "EQUAL", preset),
               _f("attribution_window", "EQUAL", "ACCOUNT_DEFAULT")]
    if conversion:
        campo = "adset.optimization_goal" if nivel == "AD" else "optimization_goal"
        filtros.append(_f(campo, "IN", list(o.evento.objetivos)))
        if o.campanas:
            filtros.append(_f("campaign.id", "IN", o.campanas))
    return filtros


def _ejecucion(accion: str, avisar: list[int]) -> dict:
    spec: dict = {"execution_type": accion}
    if avisar:
        spec["execution_options"] = [_f("user_ids", "EQUAL", list(avisar))]
    return spec


def _regla(o: Opciones, *, clave: str, tipo: str, nivel: str, accion: str, nombre: str, filtros: list[dict],
           horario: dict, resumen: str, por_que: str, evidencia: list[str], ads_manager: list[str]) -> dict:
    return {"clave": clave, "tipo": tipo, "nivel": nivel, "accion": accion, "resumen": resumen, "por_que": por_que,
            "evidencia": evidencia, "ads_manager": ads_manager,
            "api": {"name": nombre, "status": "ENABLED",
                    "evaluation_spec": {"evaluation_type": "SCHEDULE", "filters": filtros},
                    "execution_spec": _ejecucion(accion, o.avisar), "schedule_spec": horario}}


def _aplicar_a(o: Opciones, nivel: str, conversion: bool) -> str:
    quien = "todos los anuncios activos" if nivel == "AD" else "todos los conjuntos de anuncios activos"
    if conversion and o.campanas:
        return (f"Aplicar regla a: {quien} de las campañas {', '.join(map(str, o.campanas))} "
                "(selecciónalas en Ads Manager antes de crear la regla).")
    if conversion:
        return (f"Aplicar regla a: {quien}. Si la cuenta tiene campañas que optimizan otro evento distinto de "
                f"{o.evento.nombre}, selecciona solo las de {o.evento.nombre} antes de crear la regla.")
    return f"Aplicar regla a: {quien}."


def _avisos_am() -> str:
    return "Notificación: en Facebook y por correo electrónico; añade como suscriptores a quien lleve la cuenta."


def construir(o: Opciones) -> tuple[list[dict], list[dict]]:
    """(reglas, descartadas por la madurez o porque no saltarían nunca con el tope). Puro: sin red ni archivos."""
    C = a_minimo(o.cpa, o.moneda)
    kC = a_minimo(o.k * o.cpa, o.moneda)
    T1 = o.tope_cambio
    ev = o.evento.nombre
    prefijo, cubre = reciente(o.madurez)
    gasto_madurado = f"lifetime_spent - {prefijo}spent"
    txt_madurez = ("sin contar el gasto de hoy" if o.madurez == 0 else
                   f"sin contar el gasto de los últimos {cubre} días (hoy incluido): el evento tarda hasta "
                   f"{o.madurez} días en llegar")
    k_txt = _corto(o.k)
    reglas: list[dict] = []
    descartadas: list[dict] = []
    evid_kill = [
        f"[STRONG INFERENCE] Con un CPA real igual al objetivo, la probabilidad de 0 conversiones tras {k_txt}× es "
        f"{_pct(math.exp(-o.k))} (Poisson; {KB_REGLAS} §2 y {KB_PRINCIPIOS} §7). Nunca a 1× (37 %).",
        f"[STRONG INFERENCE] ≥3× el CPA objetivo sin conversión es una de las excepciones que permiten actuar sin "
        f"esperar los 7 días, pero solo en un evento frecuente ({KB_PRINCIPIOS} §8): con eventos lentos se descuenta el "
        "gasto que aún no ha madurado.",
        f"[OFFICIAL META] + [EMPIRICAL] Ads Manager imputa la conversión al día de la impresión o el clic y con 7 días "
        f"clic sigue llegando hasta una semana después: los últimos días siempre se ven peor ({KB_PACIENCIA}).",
        f"[EMPIRICAL] Edad mínima de {HORAS_MIN} h ({KB_REGLAS} §4.B.1).",
        f"[HYPOTHESIS] Madurez de {o.madurez} días para {ev} y evaluación a las 06:00 (deja a Meta 6 h para atribuir "
        "lo de ayer y actúa antes del grueso del gasto del día).",
    ]
    for nivel, quien, clave in (("AD", "anuncio", "anuncio-sin-conversion"),
                                ("ADSET", "conjunto", "conjunto-sin-conversion")):
        # Cuenta pequeña: el conjunto entero solo avisa (pausarlo para la campaña; KB_REGLAS, implicaciones).
        solo_alerta = o.pequena and nivel == "ADSET"
        accion = "NOTIFICATION" if o.sombra or solo_alerta else "PAUSE"
        tipo = "ALERT" if solo_alerta else "PROTECT"
        nombre = (f"{tipo}{MARCA_OS}{clave}_{k_txt}x{_corto(o.cpa)}{o.moneda}"
                  + ("-sombra" if o.sombra and not solo_alerta else ""))
        verbo = ("Avisa del" if solo_alerta else "Avisa (modo sombra) del") if accion == "NOTIFICATION" else "Pausa el"
        extra_am = ([f"impresiones > {M._n(IMPRESIONES_KILL, 0)}"] if nivel == "AD" else [])
        if o.madurez == 0:
            am = [_aplicar_a(o, nivel, True),
                  "Acción: " + ("solo enviar notificación." if accion == "NOTIFICATION" else
                                f"desactivar {'anuncios' if nivel == 'AD' else 'conjuntos de anuncios'}."),
                  f"Condiciones (todas): importe gastado > {dinero(o.k * o.cpa, o.moneda)} · resultados = 0 · "
                  + "".join(f"{x} · " for x in extra_am) + f"horas desde la creación > {HORAS_MIN}.",
                  "Intervalo de tiempo: toda la duración (de por vida).",
                  "Programación: personalizada, todos los días a las 06:00.", _avisos_am(), f"Nombre: {nombre}"]
        else:
            am = [_aplicar_a(o, nivel, True), "Acción: solo enviar notificación.",
                  f"Condiciones (todas): importe gastado > {dinero(o.k * o.cpa, o.moneda)} · resultados = 0 · "
                  + "".join(f"{x} · " for x in extra_am)
                  + f"horas desde la creación > {max(HORAS_MIN, 24 * (o.madurez + 3))}.",
                  "Intervalo de tiempo: toda la duración (de por vida).",
                  "Programación: personalizada, todos los días a las 06:00.", _avisos_am(), f"Nombre: {nombre}",
                  f"Por qué solo avisa aquí: Ads Manager no puede descontar el gasto de los últimos {cubre} días, que "
                  f"aún no ha tenido tiempo de convertir en {ev}. Pausar con el gasto de por vida mataría anuncios "
                  "que todavía pueden convertir. Con token, la versión de la API sí lo descuenta y puede pausar."]
        reglas.append(_regla(
            o, clave=clave, tipo=tipo, nivel=nivel, accion=accion, nombre=nombre,
            filtros=_base(o, nivel, "LIFETIME", True) + [
                _f("hours_since_creation", "GREATER_THAN", HORAS_MIN),
                _f(gasto_madurado, "GREATER_THAN", kC),
                _f("results", "LESS_THAN", 1)]
            + ([_f("impressions", "GREATER_THAN", IMPRESIONES_KILL)] if nivel == "AD" else []),
            horario=_a_las(6),
            resumen=(f"{verbo} {quien} que ha gastado más de {dinero(o.k * o.cpa, o.moneda)} ({k_txt}× el CPA "
                     f"objetivo de {dinero(o.cpa, o.moneda)}) {txt_madurez}, sin ningún resultado ({ev})."),
            por_que=(f"Gastar {k_txt}× el CPA objetivo sin una sola conversión ya no es mala suerte: es una pieza o un "
                     "conjunto que no funciona, o un tracking roto. Si pasa de madrugada, nadie lo para hasta el brief."
                     + (" Cuenta pequeña (<30 conversiones por semana y campaña): pausar el conjunto para la campaña "
                        f"entera, así que solo avisa; la pausa automática es por anuncio ({KB_REGLAS}, implicaciones "
                        "operativas)." if solo_alerta else "")
                     + (" Modo sombra: 1–2 semanas solo avisando para ver cuántas veces habría actuado y si habría "
                        f"acertado ({KB_REGLAS} §6). Si acierta, `proponer --activo` y desactiva esta."
                        if o.sombra and not solo_alerta else "")),
            evidencia=evid_kill + ([f"[STRONG INFERENCE] Kill switch lifetime por anuncio con más de "
                                    f"{M._n(IMPRESIONES_KILL, 0)} impresiones ({KB_REGLAS} §4.B.1)."]
                                   if nivel == "AD" else []), ads_manager=am))

    # Gasto de hoy fuera del tope de la ficha (todos los conjuntos de la cuenta).
    nombre = f"PROTECT{MARCA_OS}gasto-hoy-fuera-de-tope_{_corto(PAUSA_GASTO)}x{_corto(T1)}{o.moneda}"
    umbral = PAUSA_GASTO * T1
    reglas.append(_regla(
        o, clave="gasto-hoy-fuera-de-tope", tipo="PROTECT", nivel="ADSET", accion="PAUSE", nombre=nombre,
        filtros=_base(o, "ADSET", "TODAY", False) + [_f("spent", "GREATER_THAN", a_minimo(umbral, o.moneda))],
        horario=CADA_MEDIA_HORA,
        resumen=(f"Pausa el conjunto que hoy ya ha gastado más de {dinero(umbral, o.moneda)} ({_corto(PAUSA_GASTO)}× "
                 f"el tope por cambio de la ficha, {dinero(T1, o.moneda)}/día)."),
        por_que=("Con presupuestos dentro del tope, Meta no puede gastar eso en un día: hasta el 175 % del presupuesto "
                 "diario, o el 210 % con budget sharing. Si pasa, alguien ha puesto un presupuesto fuera del tope "
                 "(un cero de más, un acceso que no debía) o algo va mal. Es seguridad de dinero, no rendimiento: por "
                 "eso mira el gasto de hoy y actúa cada media hora."),
        evidencia=[f"[OFFICIAL META] Máximo diario 175 % (210 % con ad set budget sharing) ({KB_PRESUPUESTO} §1).",
                   f"[HYPOTHESIS] Margen de {_corto(PAUSA_GASTO)}× sobre el 2,1× oficial por redondeos de facturación.",
                   f"[EMPIRICAL] El tope total de la cuenta lo protege el límite de gasto de la cuenta, no una regla "
                   f"({KB_REGLAS} §4.B.4)."],
        ads_manager=[f"Antes de crearla: en Ads Manager, columna Presupuesto de campañas y conjuntos activos (o "
                     f"`ads_get_ad_entities` por el MCP), comprueba que ninguno pasa de {dinero(T1, o.moneda)}/día, ni "
                     "un presupuesto total cuyo ritmo diario lo supere. Si alguno pasa, esta regla lo pausaría cualquier "
                     "día que gaste por encima del umbral aunque sea legal: baja ese presupuesto o sube "
                     "topes.cambio_dia en la ficha (decisión tuya) y vuelve a proponer.",
                     _aplicar_a(o, "ADSET", False), "Acción: desactivar conjuntos de anuncios.",
                     f"Condición: importe gastado > {dinero(umbral, o.moneda)}.", "Intervalo de tiempo: hoy.",
                     "Programación: continuamente (cada 30 minutos).", _avisos_am(), f"Nombre: {nombre}"]))

    nombre = f"ALERT{MARCA_OS}gasto-hoy-alto_{_corto(ALERTA_GASTO)}x{_corto(T1)}{o.moneda}"
    umbral = ALERTA_GASTO * T1
    reglas.append(_regla(
        o, clave="gasto-hoy-alto", tipo="ALERT", nivel="ADSET", accion="NOTIFICATION", nombre=nombre,
        filtros=_base(o, "ADSET", "TODAY", False) + [_f("spent", "GREATER_THAN", a_minimo(umbral, o.moneda))],
        horario=_a_las(10, 14, 18, 22),
        resumen=(f"Avisa si un conjunto lleva hoy más de {dinero(umbral, o.moneda)} ({_corto(ALERTA_GASTO)}× el tope "
                 "por cambio)."),
        por_que=("Es el máximo que Meta puede gastar en un día con el presupuesto en el tope (sin budget sharing). "
                 "Llegar ahí es raro: suele ser un presupuesto por encima del tope. Avisa antes de que actúe la pausa."),
        evidencia=[f"[OFFICIAL META] 175 % del presupuesto diario como máximo en un día ({KB_PRESUPUESTO} §1).",
                   "[HYPOTHESIS] Cuatro comprobaciones al día (10, 14, 18 y 22 h) para no repetir el aviso cada media "
                   "hora."],
        ads_manager=[_aplicar_a(o, "ADSET", False), "Acción: solo enviar notificación.",
                     f"Condición: importe gastado > {dinero(umbral, o.moneda)}.", "Intervalo de tiempo: hoy.",
                     "Programación: personalizada, todos los días a las 10:00, 14:00, 18:00 y 22:00.", _avisos_am(),
                     f"Nombre: {nombre}"]))

    # Sin conversiones recientes en conjuntos que ya llevan días (tracking o formulario roto). La ventana es la más
    # corta en la que un conjunto con el presupuesto del tope puede llegar a gastar k×C ya madurado: con menos gasto,
    # 0 conversiones no es señal y la regla no saltaría nunca.
    cerrado = reciente_cerrado(o.madurez) if o.madurez else ("", 0)
    v, maduros = ventana_alcanzable(cerrado[1] + 3, VENTANA_MAX_SIN_CONVERSIONES, cerrado[1], o.k * o.cpa, T1)
    if v:
        campo_gasto = "spent" if o.madurez == 0 else f"{v[2]}spent - {cerrado[0]}spent"
        factor = v[0] / maduros
        nombre = f"ALERT{MARCA_OS}sin-conversiones-{v[0]}d_{k_txt}x{_corto(o.cpa)}{o.moneda}"
        am_umbral = o.k * o.cpa * factor
        minimo_dia = o.k * o.cpa / maduros
        reglas.append(_regla(
            o, clave="sin-conversiones", tipo="ALERT", nivel="ADSET", accion="NOTIFICATION", nombre=nombre,
            filtros=_base(o, "ADSET", v[1], True) + [
                _f("hours_since_creation", "GREATER_THAN", HORAS_MIN),
                _f(campo_gasto, "GREATER_THAN", kC), _f("results", "LESS_THAN", 1)],
            horario=_a_las(7),
            resumen=(f"Avisa si un conjunto lleva {v[0]} días cerrados sin ningún {ev} habiendo gastado más de "
                     f"{dinero(o.k * o.cpa, o.moneda)} {'' if o.madurez == 0 else 'ya madurados '}en ellos. Solo "
                     f"vigila conjuntos que gastan de media más de {dinero(minimo_dia, o.moneda)}/día: por debajo, "
                     "0 conversiones en esa ventana no es señal."),
            por_que=("Detecta lo que se rompe en una cuenta que funcionaba: píxel o CAPI caídos, formulario o webhook "
                     "rotos, landing caída. La pausa por conversión no lo ve si el conjunto convirtió alguna vez. Solo "
                     "avisa: decide tú tras mirar el dataset. En conjuntos pequeños, el tracking roto lo detecta antes "
                     "/brief-diario con la señal del dataset."),
            evidencia=[f"[EMPIRICAL] Kill switch de alerta: gasto de 3 días > 3× CPA y 0 resultados ({KB_REGLAS} §4.A.3).",
                       f"[STRONG INFERENCE] Ventana ampliada hasta que el gasto posible con el tope llega al umbral, y "
                       f"gasto sin madurar descontado ({KB_PACIENCIA}).",
                       f"[HYPOTHESIS] Ventana máxima de {VENTANA_MAX_SIN_CONVERSIONES} días: más larga ya no es «reciente»."],
            ads_manager=[_aplicar_a(o, "ADSET", True), "Acción: solo enviar notificación.",
                         f"Condiciones (todas): importe gastado > {dinero(am_umbral, o.moneda)} · resultados = 0 · "
                         f"horas desde la creación > {HORAS_MIN}.",
                         f"Intervalo de tiempo: últimos {v[0]} días (sin hoy si te deja elegir).",
                         "Programación: personalizada, todos los días a las 07:00.", _avisos_am(), f"Nombre: {nombre}"]
            + ([f"El umbral es mayor que en la API ({dinero(o.k * o.cpa, o.moneda)}) porque Ads Manager no descuenta "
                f"los últimos {cerrado[1]} días sin madurar: se compensa suponiendo un gasto parejo."]
               if o.madurez else [])))
    elif cerrado[1] + 3 > VENTANA_MAX_SIN_CONVERSIONES:
        descartadas.append({"regla": "ALERT sin conversiones recientes",
                            "por_que": f"Con {o.madurez} días de madurez no queda una ventana reciente (hasta "
                                       f"{VENTANA_MAX_SIN_CONVERSIONES} días) con días ya madurados. Míralo en el "
                                       "informe semanal con cohortes (`embudo.py cohortes`)."})
    else:
        descartadas.append({"regla": "ALERT sin conversiones recientes",
                            "por_que": f"Con presupuestos dentro del tope ({dinero(T1, o.moneda)}/día), un conjunto no "
                                       f"llega a gastar {dinero(o.k * o.cpa, o.moneda)} ya madurados en "
                                       f"{VENTANA_MAX_SIN_CONVERSIONES} días: 0 conversiones nunca sería señal y la "
                                       "regla no saltaría. El tracking roto lo vigila /brief-diario (señal del "
                                       "dataset)."})

    # CPA disparado con ventana suficiente: solo avisa, nunca pausa. Necesita ≥3 resultados a más de 2× el CPA, o sea,
    # un gasto de 6×C ya madurado dentro de la ventana.
    necesario = MIN_RESULTADOS * CPA_ALERTA * o.cpa
    v, maduros = ventana_alcanzable(max(14, cerrado[1] + 7), 30, cerrado[1], necesario, T1)
    if v:
        dosC = CPA_ALERTA * C
        if o.madurez == 0:
            gasto, resultados = "spent", "results"
        else:
            gasto = f"{v[2]}spent - {cerrado[0]}spent"
            resultados = f"{v[2]}results - {cerrado[0]}results"
        nombre = f"ALERT{MARCA_OS}cpa-disparado-{v[0]}d_{CPA_ALERTA}x{_corto(o.cpa)}{o.moneda}"
        reglas.append(_regla(
            o, clave="cpa-disparado", tipo="ALERT", nivel="ADSET", accion="NOTIFICATION", nombre=nombre,
            filtros=_base(o, "ADSET", v[1], True) + [
                _f(resultados, "GREATER_THAN", MIN_RESULTADOS - 1),
                _f(f"({gasto}) - {dosC} * ({resultados})" if o.madurez else f"{gasto} - {dosC} * {resultados}",
                   "GREATER_THAN", 0)],
            horario=_a_las(7),
            resumen=(f"Avisa si un conjunto tiene un CPA de más de {dinero(CPA_ALERTA * o.cpa, o.moneda)} "
                     f"({CPA_ALERTA}× el objetivo) con al menos {MIN_RESULTADOS} resultados en {v[0]} días cerrados"
                     + ("" if o.madurez == 0 else f", sin contar los últimos {cerrado[1]} días sin madurar")
                     + f". Solo puede saltar en conjuntos que gastan de media más de "
                       f"{dinero(necesario / maduros, o.moneda)}/día."),
            por_que=("Con CPA solo se detectan diferencias grandes: el doble del objetivo con varios resultados y una "
                     "semana o más de datos ya es señal, no ruido. Es una alerta para revisar en /diagnostico, nunca "
                     "una pausa automática: con 3 resultados el CPA real puede estar entre 0,35× y 5× el observado."),
            evidencia=[f"[STRONG INFERENCE] Umbral 2× con ≥3 resultados ({KB_REGLAS} §4.B.2 y §2) y ≥7 días madurados "
                       f"({KB_PRINCIPIOS} §8).",
                       "[STRONG INFERENCE] Se expresa como gasto − 2×CPA × resultados > 0 para no dividir por cero ni "
                       "depender de la definición de «coste por resultado»."],
            ads_manager=[_aplicar_a(o, "ADSET", True), "Acción: solo enviar notificación.",
                         f"Condiciones (todas): coste por resultado > {dinero(CPA_ALERTA * o.cpa, o.moneda)} · "
                         f"resultados > {MIN_RESULTADOS - 1}.",
                         f"Intervalo de tiempo: últimos {v[0]} días (sin hoy si te deja elegir).",
                         "Programación: personalizada, todos los días a las 07:00.", _avisos_am(), f"Nombre: {nombre}"]
            + ([f"En Ads Manager no se descuentan los últimos {cerrado[1]} días: el aviso puede salir antes de tiempo. "
                "Tómalo como «mira esto», no como veredicto."] if o.madurez else [])))
    elif max(14, cerrado[1] + 7) > 30:
        descartadas.append({"regla": "ALERT CPA disparado",
                            "por_que": f"Con {o.madurez} días de madurez, el CPA de cualquier ventana de Meta (hasta 30 "
                                       "días) está inflado por conversiones que aún no han llegado. Se lee por "
                                       "cohortes en el informe semanal."})
    else:
        descartadas.append({"regla": "ALERT CPA disparado",
                            "por_que": f"Con presupuestos dentro del tope ({dinero(T1, o.moneda)}/día), un conjunto no "
                                       f"llega en 30 días a {MIN_RESULTADOS} resultados a {CPA_ALERTA}× el CPA "
                                       f"({dinero(necesario, o.moneda)} ya madurados): con tan pocos datos el CPA no "
                                       "se puede juzgar por conjunto. Se lee en el informe semanal."})

    nombre = f"ALERT{MARCA_OS}sin-entrega-ayer"
    reglas.append(_regla(
        o, clave="sin-entrega", tipo="ALERT", nivel="ADSET", accion="NOTIFICATION", nombre=nombre,
        filtros=_base(o, "ADSET", "YESTERDAY", False) + [
            _f("hours_since_creation", "GREATER_THAN", 48), _f("impressions", "LESS_THAN", IMPRESIONES_MIN)],
        horario=_a_las(8),
        resumen=f"Avisa a las 08:00 si un conjunto activo ayer tuvo menos de {IMPRESIONES_MIN} impresiones.",
        por_que=("Un pago rechazado, anuncios rechazados o un problema de entrega dejan de traer leads sin hacer ruido. "
                 "Un viernes por la noche eso es un fin de semana perdido."),
        evidencia=[f"[EMPIRICAL] Alerta de entrega cero ({KB_REGLAS} §4.A.1).",
                   "[HYPOTHESIS] Día cerrado (ayer) en vez de «hoy a mediodía», para que no salte con presupuestos "
                   "pequeños y CPM altos de B2B."],
        ads_manager=[_aplicar_a(o, "ADSET", False), "Acción: solo enviar notificación.",
                     f"Condiciones (todas): impresiones < {IMPRESIONES_MIN} · horas desde la creación > 48.",
                     "Intervalo de tiempo: ayer.", "Programación: personalizada, todos los días a las 08:00.",
                     _avisos_am(), f"Nombre: {nombre}"]))
    return reglas, descartadas


DESCARTADAS_SIEMPRE = [
    {"regla": "Frecuencia > 3 → pausar o avisar",
     "por_que": f"Folklore: Meta mide la fatiga por coste por resultado frente a tu histórico, no por frecuencia "
                f"({KB_MITOS} M37)."},
    {"regla": "Subir presupuesto (+20 % o cualquier cifra) si el CPA es bueno",
     "por_que": f"El 20 % es un mito ({KB_MITOS} M05) y una regla que sube presupuesto actúa en Meta sin los topes de "
                f"la ficha ni los hooks. Escalar se decide por coste marginal con /escalar ({KB_REGLAS} §4.C [CONTESTED])."},
    {"regla": "Pausar si el CPA de hoy o de ayer supera el objetivo",
     "por_que": f"Ruido y latencia de atribución: mata ganadores ({KB_REGLAS} §2 y §5)."},
    {"regla": "Encender lo que ayer fue bien / apagar y encender por horas",
     "por_que": f"Bucles de ruido y regresión a la media; reinicia la entrega ({KB_REGLAS} §5)."},
    {"regla": "Reequilibrar presupuesto entre conjuntos (REBALANCE_BUDGET)",
     "por_que": f"Con poco volumen concentra el dinero en el ruido ({KB_REGLAS} §5)."},
    {"regla": "CPM por encima de la mediana o caída del CTR",
     "por_que": "Necesitan la banda normal de la cuenta: los lee el brief diario con `estadistica.py banda`, que "
                "compara con el ruido real en vez de un umbral fijo."},
]


# ---------------------------------------------------------------- análisis de una regla (crear y listar)

METADATOS = {"id", "entity_type", "name", "adlabel_ids", "objective", "start_time", "stop_time", "buying_type",
             "billing_event", "optimization_goal", "is_autobid", "daily_budget", "lifetime_budget", "spend_cap",
             "bid_amount", "created_time", "updated_time", "effective_status", "placement.page_types",
             "budget_reset_period", "hours_since_creation", "estimated_budget_spending_percentage",
             "audience_reached_percentage", "active_time", "current_time", "time_preset", "attribution_window",
             "aggregation_id"}
CON_TIEMPO = {"daily_ratio_spent", "lifetime_ratio_spent"}
CORTAS = {"TODAY", "YESTERDAY", "LAST_2_DAYS", "LAST_2D"}
_PREFIJO = re.compile(r"^(?:(?:ad|adset|campaign)\.)?(?:\w+:)?")
_TIEMPO = re.compile(r"^(lifetime_|today_|yesterday_|last_\d+_days_|last_\d+d_|this_month_|"
                     r"this_week_(?:mon|sun)_today_|last_nd_\w+?_\d+_)")
_PRESET_DE_PREFIJO = {"today_": "TODAY", "yesterday_": "YESTERDAY", "last_2_days_": "LAST_2_DAYS", "last_2d_": "LAST_2D"}


def _tokens(campo: str) -> list[str]:
    return [t for t in re.split(r"[\s()+\-*/]+", str(campo)) if t and not re.fullmatch(r"[\d.]+", t)]


def _partes(token: str) -> tuple[str, str]:
    """(prefijo de tiempo, campo base) de un campo de la API: «adset.7d_click:lifetime_spent» → («lifetime_», «spent»)."""
    t = _PREFIJO.sub("", token)
    if t in METADATOS or t in CON_TIEMPO:
        return "", t
    m = _TIEMPO.match(t)
    return (m.group(1), t[m.end():]) if m else ("", t)


def _es_coste(base: str) -> bool:
    return base in {"cost_per", "cpa", "cpc", "cpm", "cpp", "ctr", "link_ctr", "result_rate",
                    "cost_per_unique_click"} or base.startswith("cost_per_") or base.endswith("_roas")


def _es_conversion(base: str) -> bool:
    return base in {"results", "leadgen"} or base.startswith(
        ("offsite_conversion", "offline_conversion", "app_custom_event", "mobile_app_install"))


def _valor(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def _spec(regla: dict, clave: str) -> dict:
    s = _valor(regla.get(clave) or {})
    return s if isinstance(s, dict) else {}


def _filtros(regla: dict) -> list[dict]:
    return [f for f in (_spec(regla, "evaluation_spec").get("filters") or []) if isinstance(f, dict)]


def _num(v) -> float | None:
    try:
        return float(_valor(v))
    except (TypeError, ValueError):
        return None


def _opcion(regla: dict, campo: str):
    for x in _spec(regla, "execution_spec").get("execution_options") or []:
        if isinstance(x, dict) and x.get("field") == campo:
            return _valor(x.get("value"))
    return None


def destinatarios_de(regla: dict) -> list:
    v = _opcion(regla, "user_ids")
    return v if isinstance(v, list) else ([v] if v else [])


def analizar(regla: dict, cpa_minimo: int | None = None) -> list[tuple[str, str]]:
    """Problemas de una regla según la KB: [(«bloquea»|«aviso», texto)]. `crear` no crea nada con «bloquea»."""
    out: list[tuple[str, str]] = []
    ev = _spec(regla, "evaluation_spec")
    ex = _spec(regla, "execution_spec")
    accion = str(ex.get("execution_type") or "").upper()
    filtros = _filtros(regla)

    if accion in ("CHANGE_BUDGET", "CHANGE_CAMPAIGN_BUDGET"):
        cambio = _opcion(regla, "change_spec") or {}
        cantidad = _num(cambio.get("amount")) if isinstance(cambio, dict) else None
        if cantidad is not None and cantidad < 0:
            out.append(("bloquea", "Baja presupuestos sola: cada cambio puede reiniciar el aprendizaje y choca con el "
                                   f"límite de 4 cambios por hora por conjunto ({KB_REGLAS} §3)."))
        else:
            out.append(("bloquea", "SUBE presupuesto en los servidores de Meta, sin los topes de la ficha ni los hooks "
                                   f"del OS. El 20 % es un mito ({KB_MITOS} M05); escala con /escalar."))
        frec = _num(_opcion(regla, "action_frequency"))
        if frec is not None and frec < 60:
            out.append(("aviso", f"Cambia cada {frec:.0f} min: Meta bloquea el conjunto 1 h tras 4 cambios de "
                                 f"presupuesto en una hora ({KB_REGLAS} §3)."))
    elif accion == "UNPAUSE":
        out.append(("bloquea", "ENCIENDE cosas sola: gasta sin el sí del momento y crea bucles de ruido (encender lo "
                               f"que ayer fue bien es regresión a la media, {KB_REGLAS} §5)."))
    elif accion == "REBALANCE_BUDGET":
        out.append(("bloquea", f"Reequilibra presupuesto: con poco volumen concentra el dinero en el ruido ({KB_REGLAS} §5)."))
    elif accion == "CHANGE_BID":
        out.append(("bloquea", "Cambia pujas sola: el OS no automatiza pujas en los servidores de Meta."))
    elif accion == "ROTATE":
        out.append(("bloquea", "Rota anuncios (pausa uno y enciende otro): enciende cosas sin confirmación."))
    elif accion not in ACCIONES_OS:
        out.append(("bloquea", f"Acción «{accion or '¿vacía?'}»: el OS solo crea reglas que avisan (NOTIFICATION) o "
                               "pausan (PAUSE)."))

    tipo = str(ev.get("evaluation_type") or "").upper()
    if tipo != "SCHEDULE":
        out.append(("bloquea", f"Evaluación «{tipo or '¿vacía?'}»: las reglas por disparador solo existen por API y no "
                               "se ven en Ads Manager. El OS solo crea reglas programadas (SCHEDULE)."))
    campos = [str(f.get("field") or "") for f in filtros]
    if not ({"entity_type", "id"} & set(campos)):
        out.append(("bloquea", "Sin entity_type ni id: Meta no sabe a qué nivel aplicarla."))
    presets = {str(_valor(f.get("value"))).upper() for f in filtros if f.get("field") == "time_preset"}
    for f in filtros:
        if f.get("field") == "attribution_window" and str(_valor(f.get("value"))) != "ACCOUNT_DEFAULT":
            out.append(("bloquea", "attribution_window solo admite ACCOUNT_DEFAULT."))

    sin_tiempo, frecuencia, coste, cortas = False, False, False, set(presets & CORTAS)
    cero_resultados, gasto_umbral, ratio = False, None, None
    for f in filtros:
        campo, op, valor = str(f.get("field") or ""), str(f.get("operator") or "").upper(), _num(f.get("value"))
        toks = _tokens(campo)
        partes = [_partes(t) for t in toks]
        for tiempo, base in partes:
            if base in METADATOS:
                continue
            if base in CON_TIEMPO:
                ratio = valor if base == "daily_ratio_spent" and op == "GREATER_THAN" else ratio
                continue
            if not tiempo:
                sin_tiempo = True
            if tiempo in _PRESET_DE_PREFIJO and len(toks) == 1:
                # En una fórmula, un periodo corto suele ser lo que se RESTA (gasto sin madurar), no lo que se mide.
                cortas.add(_PRESET_DE_PREFIJO[tiempo])
            if base == "frequency":
                frecuencia = True
            if _es_coste(base):
                coste = True
        bases = [b for _, b in partes]
        if len(toks) > 1 and "spent" in bases and any(_es_conversion(b) for b in bases):
            coste = True  # fórmula de CPA: gasto − X × resultados
        elif len(toks) == 1 and _es_conversion(bases[0]) and (
                (op == "EQUAL" and valor == 0) or (op == "LESS_THAN" and valor is not None and valor <= 1)):
            cero_resultados = True
        elif "spent" in bases and op == "GREATER_THAN" and valor is not None and not any(
                _es_conversion(b) for b in bases):
            gasto_umbral = valor if gasto_umbral is None else max(gasto_umbral, valor)
    if sin_tiempo and not presets:
        out.append(("bloquea", "Usa métricas sin time_preset: Meta lo exige con cualquier filtro de estadísticas."))
    if frecuencia:
        # Pausar por frecuencia es folklore; avisar en prospección lo recomienda la KB (KB_REGLAS §4.A.5).
        out.append(("bloquea" if accion == "PAUSE" else "aviso",
                    "Regla por frecuencia: «frecuencia > 3 = fatiga» es folklore; Meta mide la fatiga por coste por "
                    f"resultado frente a tu histórico ({KB_MITOS} M37)"
                    + (". No pauses por ella." if accion == "PAUSE" else
                       f". Como aviso en prospección vale ({KB_REGLAS} §4.A.5): mira el coste por resultado antes de "
                       "tocar nada.")))
    if accion == "PAUSE":
        if (coste or cero_resultados) and cortas:
            out.append(("bloquea", f"Pausa por rendimiento con el periodo {', '.join(sorted(cortas))}: es ruido más "
                                   f"latencia de atribución y mata ganadores ({KB_REGLAS} §2 y §5)."))
        elif coste:
            out.append(("aviso", "Pausa por CPA o por una tasa: con pocas conversiones el CPA es ruido. El OS prefiere "
                                 f"una alerta y decidir con /diagnostico ({KB_PACIENCIA})."))
        if cero_resultados and gasto_umbral is not None and cpa_minimo:
            k = gasto_umbral / cpa_minimo
            p = _pct(math.exp(-k))
            if k < 2 - 1e-9:
                out.append(("bloquea", f"Mata a {_corto(k)}× el CPA objetivo sin conversión: descarta un {p} de "
                                       f"anuncios buenos. Mínimo 2×, por defecto 3× ({KB_PRINCIPIOS} §7)."))
            elif k < 3 - 1e-9:
                out.append(("aviso", f"Mata a {_corto(k)}× el CPA objetivo: un {p} de anuncios buenos caerían "
                                     "(a 3×, un 5 %)."))
        if cero_resultados and "hours_since_creation" not in " ".join(campos):
            out.append(("aviso", "Pausa sin edad mínima (hours_since_creation): puede matar en las primeras horas."))
        if ratio is not None and ratio < 1.75:
            out.append(("bloquea", f"Pausa si el gasto de hoy pasa de {_corto(ratio)}× el presupuesto diario: hasta 1,75× es "
                                   f"legal desde 2025 ({KB_PRESUPUESTO} §1; {KB_REGLAS} §3)."))
    if not destinatarios_de(regla):
        out.append(("aviso", "Sin destinatarios (user_ids): solo avisa a quien la creó; si la creó un usuario del "
                             "sistema, no la ve nadie."))
    estado = str(regla.get("status") or "").upper()
    if estado == "HAS_ISSUES":
        out.append(("aviso", f"Meta la marca con problemas (disable_error_code {regla.get('disable_error_code')}): "
                             "no está actuando."))
    fecha = str(regla.get("updated_time") or regla.get("created_time") or "")[:10]
    if fecha and fecha < CAMBIO_CLIC and (coste or cero_resultados or gasto_umbral):
        out.append(("aviso", f"Umbral calibrado antes del {CAMBIO_CLIC} (clics = solo clics en enlace): recalíbralo "
                             f"con datos de después de abril de 2026 ({KB_REGLAS} §3)."))
    return out


# ---------------------------------------------------------------- describir

_NOMBRES = {"spent": "gasto", "results": "resultados", "impressions": "impresiones", "cost_per": "coste por resultado",
            "cpa": "CPA", "cpc": "CPC", "cpm": "CPM", "ctr": "CTR", "link_ctr": "CTR de enlace",
            "frequency": "frecuencia", "reach": "alcance", "daily_ratio_spent": "gasto de hoy / presupuesto diario",
            "hours_since_creation": "horas desde la creación", "leadgen": "leads de formulario",
            "optimization_goal": "objetivo de optimización", "entity_type": "nivel", "id": "id", "name": "nombre",
            "effective_status": "estado", "daily_budget": "presupuesto diario"}
_TIEMPOS = {"lifetime_": "de por vida", "today_": "de hoy", "yesterday_": "de ayer"}
_OPS = {"GREATER_THAN": ">", "LESS_THAN": "<", "EQUAL": "=", "NOT_EQUAL": "≠", "IN": "en", "NOT_IN": "fuera de",
        "IN_RANGE": "entre", "NOT_IN_RANGE": "fuera de", "CONTAIN": "contiene", "NOT_CONTAIN": "no contiene"}
_NIVELES = {"AD": "anuncios", "ADSET": "conjuntos", "CAMPAIGN": "campañas"}
_ACCIONES = {"NOTIFICATION": "avisa", "PAUSE": "pausa", "UNPAUSE": "ENCIENDE", "CHANGE_BUDGET": "cambia presupuesto",
             "CHANGE_CAMPAIGN_BUDGET": "cambia presupuesto de campaña", "CHANGE_BID": "cambia puja",
             "ROTATE": "rota anuncios", "REBALANCE_BUDGET": "reequilibra presupuesto", "PING_ENDPOINT": "webhook"}


def _tiempo_txt(prefijo: str) -> str:
    if prefijo in _TIEMPOS:
        return _TIEMPOS[prefijo]
    m = re.fullmatch(r"last_(\d+)_days_", prefijo)
    if m:
        return f"de los últimos {m.group(1)} días (con hoy)"
    m = re.fullmatch(r"last_(\d+)d_", prefijo)
    return f"de los últimos {m.group(1)} días cerrados" if m else prefijo.rstrip("_")


def _es_dinero(base: str) -> bool:
    return base in {"spent", "cost_per", "cpa", "cpc", "cpm", "cpp", "cost_per_unique_click"} or base.startswith(
        "cost_per_") or "budget" in base


def describir_filtro(f: dict, moneda: str) -> str | None:
    """Condición legible; los importes (unidad mínima en la API) en la moneda de la cuenta."""
    campo, op, valor = str(f.get("field") or ""), str(f.get("operator") or "").upper(), _valor(f.get("value"))
    if campo in ("time_preset", "attribution_window", "entity_type"):
        return None
    toks = _tokens(campo)
    if len(toks) > 1:
        texto = f"«{campo}»"
    else:
        tiempo, base = _partes(campo)
        texto = _NOMBRES.get(base, base) + (f" {_tiempo_txt(tiempo)}" if tiempo else "")
        if campo.startswith(("adset.", "campaign.")):
            texto += f" ({'del conjunto' if campo.startswith('adset.') else 'de la campaña'})"
    dinero_campo = bool(toks) and all(_es_dinero(_partes(t)[1]) for t in toks)
    if dinero_campo and isinstance(valor, (int, float)) and not isinstance(valor, bool):
        valor_txt = dinero(de_minimo(valor, moneda), moneda)
    elif isinstance(valor, list):
        valor_txt = ", ".join(map(str, valor))
    else:
        valor_txt = str(valor)
    return f"{texto} {_OPS.get(op, op)} {valor_txt}"


def describir_horario(spec: dict) -> str:
    tipo = str(spec.get("schedule_type") or "")
    if tipo == "SEMI_HOURLY":
        return "cada media hora"
    if tipo == "HOURLY":
        return "cada hora"
    if tipo == "DAILY":
        return "cada día a medianoche (zona de la cuenta)"
    if tipo == "CUSTOM":
        horas = sorted({int(x.get("start_minute")) for x in spec.get("schedule") or [] if isinstance(x, dict)
                        and x.get("start_minute") is not None})
        if horas:
            return "cada día a las " + ", ".join(f"{h // 60:02d}:{h % 60:02d}" for h in horas)
        return "personalizada"
    return tipo.lower() or "sin horario (por disparador)"


def resumen_regla(regla: dict, moneda: str) -> dict:
    ev = _spec(regla, "evaluation_spec")
    ex = _spec(regla, "execution_spec")
    filtros = _filtros(regla)
    nivel = next((str(_valor(f.get("value"))) for f in filtros if f.get("field") == "entity_type"), "")
    preset = next((str(_valor(f.get("value"))) for f in filtros if f.get("field") == "time_preset"), "")
    return {"id": str(regla.get("id") or ""), "nombre": regla.get("name", ""), "estado": regla.get("status", ""),
            "del_os": MARCA_OS in str(regla.get("name", "")),
            "accion": str(ex.get("execution_type") or ""), "nivel": nivel, "periodo": preset,
            "evaluacion": str(ev.get("evaluation_type") or ""),
            "horario": describir_horario(_spec(regla, "schedule_spec")) if ev.get("evaluation_type") == "SCHEDULE"
            else "en tiempo real (disparador)",
            "condiciones": [d for d in (describir_filtro(f, moneda) for f in filtros) if d],
            "destinatarios": len(destinatarios_de(regla))}


# ---------------------------------------------------------------- utilidades de cliente

def _contexto(slug: str | None) -> M.Contexto:
    return M.contexto(slug)


def _conectar(ctx: M.Contexto) -> M.Meta:
    if not comun.credencial("META_TOKEN", ctx.slug):
        _salir(SIN_TOKEN, 2)
    return M.conectar(ctx)


def _rel(ruta: pathlib.Path) -> str:
    return M._rel(ruta)


def _ids(texto: str | None, que: str) -> list[int]:
    if not texto:
        return []
    salida = []
    for x in re.split(r"[,\s]+", texto.strip()):
        if not x:
            continue
        if not re.fullmatch(r"\d{3,25}", x):
            _salir(f"{que}: «{x}» no es un ID numérico.", 1)
        salida.append(int(x))
    return salida


def _cpa_minimo(datos: dict, moneda: str) -> int | None:
    v = _num(datos.get("cpa_objetivo"))
    return a_minimo(v, moneda) if v else None


def fila_change_log(objeto: str, cambio: str, motivo: str, metrica: str, dias: int = 14) -> str:
    ahora = datetime.now()
    return (f"| {ahora:%Y-%m-%d %H:%M} | operador-meta (reglas_meta.py) | regla | {objeto} | {cambio} | {motivo} "
            f"| {metrica} | {(ahora + timedelta(days=dias)):%Y-%m-%d} | |")


# ---------------------------------------------------------------- proponer

def cmd_proponer(a: argparse.Namespace) -> None:
    ctx = _contexto(a.cliente)
    if ctx.tope_cambio <= 0:
        _salir(f"La ficha de {ctx.slug} no tiene topes (topes.cambio_dia = 0): sin tope no hay protección de gasto. "
               "Fíjalos en la ficha (decisión tuya; /configurar-meta te guía) y vuelve a proponer.", 2)
    nombre_ev = a.evento or str((ctx.ficha.get("meta") or {}).get("evento_principal") or "")
    if not nombre_ev:
        _salir(f"La ficha de {ctx.slug} no tiene meta.evento_principal: ponlo o pásalo con --evento.", 2)
    ev, conocido = evento(nombre_ev)
    avisos: list[str] = []
    if not conocido:
        avisos.append(f"Evento «{ev.nombre}» desconocido: supongo madurez de 7 días y conjuntos OFFSITE_CONVERSIONS. "
                      "Ajústalo con --madurez si tarda menos.")
    if a.cpa is not None:
        if a.cpa <= 0:
            _salir("--cpa tiene que ser mayor que 0.", 1)
        cpa, origen = a.cpa, "--cpa"
    else:
        cpa, columna, celda = celda_de_ficha(ctx.slug, ev.fila)
        if not cpa:
            fila = f"la fila «{ev.fila}» de la tabla Economía" if ev.fila else "una fila de coste para ese evento"
            _salir(f"No encuentro el coste objetivo de {ev.nombre} en la ficha de {ctx.slug} ({fila}). Calcúlalo con "
                   "/economia y anótalo en la ficha, o pásalo con --cpa.", 2)
        origen = f"ficha, {columna} de «{ev.fila}»: «{celda}»"
        if columna == "break-even":
            avisos.append(f"La ficha no tiene target para {ev.nombre}: uso el break-even ({dinero(cpa, ctx.moneda)}). "
                          "Las reglas saltarán más tarde; pon el target en la ficha si lo tienes.")
    # Hallazgo 9 (I6): k y niveles según el volumen de la cuenta (KB_REGLAS, implicaciones operativas).
    if a.conversiones_semana is not None and a.conversiones_semana < 0:
        _salir("--conversiones-semana no puede ser negativo.", 1)
    pequena = a.conversiones_semana is None or a.conversiones_semana < CONVERSIONES_SEMANA_GRANDE
    k = a.multiplicador if a.multiplicador is not None else (K_PEQUENA if pequena else K_GRANDE)
    if a.conversiones_semana is None:
        avisos.append(f"Sin --conversiones-semana supongo cuenta pequeña (<{CONVERSIONES_SEMANA_GRANDE} conversiones por "
                      "semana y campaña, lo normal en B2B de ticket alto): pausa automática solo por anuncio a "
                      f"{_corto(k)}× y el conjunto solo avisa ({KB_REGLAS}, implicaciones operativas). Si tienes más "
                      "volumen, pásalo (lo da `analista-meta`).")
    if k < 2:
        _salir(f"--multiplicador {_corto(k)}: nunca por debajo de 2× (a 1× se descarta un 37 % de "
               f"anuncios buenos; {KB_PRINCIPIOS} §7).", 1)
    if k < 3:
        avisos.append(f"Multiplicador {_corto(k)}: un {_pct(math.exp(-k))} de anuncios "
                      "buenos caerían (a 3×, un 5 %).")
    if k > 5:
        avisos.append(f"Multiplicador {_corto(k)}: deja gastar mucho antes de actuar.")
    elif k < 4 and pequena:
        avisos.append("Con menos de 30 conversiones por semana y campaña (lo normal en B2B de ticket "
                      f"alto), la KB aconseja ≥4× para las pausas automáticas ({KB_REGLAS}, Implicaciones): "
                      "--multiplicador 4 (a 4× caen un 1,8 % de anuncios buenos; a 3×, un 5 %).")
    if k * cpa < CPA_TOPE_MIN * ctx.tope_cambio:
        celda_txt = f" (celda leída: «{celda}»)" if a.cpa is None else ""
        avisos.append(f"El CPA objetivo, {dinero(cpa, ctx.moneda)}{celda_txt}, es minúsculo frente al tope por cambio "
                      f"({dinero(ctx.tope_cambio, ctx.moneda)}/día): las pausas saltarían con "
                      f"{dinero(k * cpa, ctx.moneda)} de gasto. Comprueba la ficha antes de crear nada.")
    madurez = a.madurez if a.madurez is not None else madurez_por_defecto(ev, str(ctx.ficha.get("tipo") or ""))
    if madurez < 0:
        _salir("--madurez no puede ser negativa.", 1)
    if madurez > MADUREZ_MAX:
        _salir(f"Madurez de {madurez} días para {ev.nombre}: ninguna regla puede saber a tiempo si un anuncio funciona. "
               "Protege con un evento anterior (--evento Lead o LeadCualificado, con su coste) y decide el resto "
               "en el informe semanal con cohortes (`embudo.py cohortes`).", 1)
    campanas = _ids(a.campanas, "--campanas")
    avisar = _ids(a.avisar, "--avisar")
    o = Opciones(ctx.moneda, ev, float(cpa), float(k), madurez, ctx.tope_cambio, not a.activo,
                 campanas, avisar, pequena)
    reglas, descartadas = construir(o)
    pendientes = []
    if not avisar:
        pendientes.append("A quién avisar: sin --avisar, Meta solo avisa a quien crea la regla (si es el usuario del "
                          "sistema del token, a nadie). Saca los IDs con `destinatarios` o créalas en Ads Manager.")
    if not ctx.cuenta_valida:
        pendientes.append(f"La ficha de {ctx.slug} no tiene una cuenta real en meta.cuenta: por la API no se puede "
                          "crear; en Ads Manager, sí.")
    if not campanas:
        avisos.append(f"Las reglas de conversión miran todos los conjuntos que optimizan {', '.join(ev.objetivos)}. "
                      f"Si alguno persigue otro evento distinto de {ev.nombre}, limita con --campanas.")
    if madurez:
        avisos.append(f"Madurez {madurez} días: las pausas descuentan el gasto reciente con fórmulas de la API. Si Meta "
                      "rechaza una fórmula al crear, `crear` dice cuál; en Ads Manager esas reglas solo avisan.")
    hoy = date.today().isoformat()
    datos = {"formato": FORMATO, "cliente": ctx.slug, "cuenta": ctx.cuenta, "moneda": ctx.moneda, "fecha": hoy,
             "evento": ev.nombre, "cpa_objetivo": float(cpa), "cpa_origen": origen,
             "multiplicador": float(k), "madurez_dias": madurez,
             "conversiones_semana": a.conversiones_semana, "cuenta_pequena": pequena,
             "modo": "activo" if a.activo else "sombra",
             "topes": {"cambio_dia": ctx.tope_cambio, "total_dia": ctx.tope_total},
             "ambito": {"campanas": campanas}, "avisar": avisar, "pendientes": pendientes, "avisos": avisos,
             "descartadas": descartadas + DESCARTADAS_SIEMPRE, "reglas": reglas}
    if a.salida:
        ruta = pathlib.Path(a.salida).expanduser()
    else:
        carpeta = comun.ruta_cliente(ctx.slug) / "planes"
        ruta, n = carpeta / f"reglas-{hoy}.json", 2
        while ruta.exists():  # nunca se pisa una propuesta anterior
            ruta, n = carpeta / f"reglas-{hoy}-{n}.json", n + 1
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if a.json:
        return _json({**datos, "archivo": _rel(ruta)})
    print(f"{ctx.slug} · {ctx.cuenta or '—'} · evento {ev.nombre} · CPA objetivo {dinero(cpa, ctx.moneda)} ({origen}) · "
          f"kill a {_corto(k)}× · madurez {madurez} días · modo {datos['modo']} · tope por cambio "
          f"{dinero(ctx.tope_cambio, ctx.moneda)}/día\n")
    for r in reglas:
        print(f"{r['api']['name']}\n  {r['resumen']}\n  {describir_horario(r['api']['schedule_spec'])}")
    if descartadas:
        print("\nNo incluidas (no podrían saltar con esta madurez o este tope):")
        for d in descartadas:
            print(f"  - {d['regla']}: {d['por_que']}")
    for x in avisos:
        print(f"Aviso: {x}")
    if pendientes:
        print("\nAntes de crearlas por la API falta:\n  - " + "\n  - ".join(pendientes))
    print(f"\nPropuesta: {_rel(ruta)}\nSiguiente: revisión con revisor-estrategia y, con tu sí, "
          f"`crear {_rel(ruta)} --cliente {ctx.slug} --simular` (añade --pasos para hacerlo en Ads Manager).")


# ---------------------------------------------------------------- crear

def _lee_propuesta(ruta_txt: str, ctx: M.Contexto) -> tuple[dict, pathlib.Path]:
    ruta = pathlib.Path(ruta_txt).expanduser()
    if not ruta.is_absolute() and not ruta.exists() and (comun.RAIZ / ruta).exists():
        ruta = comun.RAIZ / ruta  # la ruta que imprime `proponer` es relativa a la raíz del OS
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _salir(f"No existe {ruta_txt}.", 1)
    except json.JSONDecodeError as e:
        _salir(f"{ruta_txt} no es JSON válido: {e}", 1)
    if not isinstance(datos, dict) or datos.get("formato") != FORMATO or not isinstance(datos.get("reglas"), list):
        _salir(f"{ruta_txt} no es una propuesta de reglas ({FORMATO}): genérala con `proponer`.", 1)
    if datos.get("cliente") != ctx.slug:
        _salir(f"{ruta_txt} es de «{datos.get('cliente')}», no de «{ctx.slug}».", 1)
    if str(datos.get("moneda") or "").upper() != ctx.moneda:
        _salir(f"La propuesta está en {datos.get('moneda')} y la ficha en {ctx.moneda}: los umbrales van en la moneda "
               "de la cuenta. Vuelve a proponer.", 2)
    if datos.get("cuenta") and ctx.cuenta and datos["cuenta"] != ctx.cuenta and ctx.cuenta_valida:
        _salir(f"La propuesta es de la cuenta {datos['cuenta']} y la ficha dice {ctx.cuenta}. Vuelve a proponer.", 1)
    return datos, ruta


def revisar_propuesta(datos: dict, ctx: M.Contexto) -> tuple[list[str], list[str], list[str]]:
    """(errores, pendientes, avisos) de todas las reglas de la propuesta."""
    errores, pendientes, avisos = [], [], []
    cpa = _cpa_minimo(datos, ctx.moneda)
    nombres, sin_aviso = set(), []
    if not datos["reglas"]:
        errores.append("la propuesta no tiene reglas")
    for i, r in enumerate(datos["reglas"], 1):
        api = r.get("api") if isinstance(r, dict) else None
        if not isinstance(api, dict) or not api.get("name"):
            errores.append(f"regla {i}: falta api.name")
            continue
        if api["name"] in nombres:
            errores.append(f"{api['name']}: nombre repetido")
        nombres.add(api["name"])
        for gravedad, texto in analizar(api, cpa):
            if texto.startswith("Sin destinatarios"):
                sin_aviso.append(api["name"])
            elif gravedad == "bloquea":
                errores.append(f"{api['name']}: {texto}")
            else:
                avisos.append(f"{api['name']}: {texto}")
    if sin_aviso:
        pendientes.append(f"destinatarios de los avisos (user_ids) en {len(sin_aviso)} de {len(nombres)} reglas: "
                          "pásalos con --avisar (los IDs salen de `destinatarios`)")
    if not ctx.cuenta_valida:
        pendientes.append(f"la ficha de {ctx.slug} no tiene una cuenta real en meta.cuenta (act_…)")
    return errores, pendientes, avisos


def _con_destinatarios(datos: dict, avisar: list[int]) -> None:
    for r in datos["reglas"]:
        if not isinstance(r, dict) or not isinstance(r.get("api"), dict):
            continue  # revisar_propuesta lo marca como error
        ex = r["api"].setdefault("execution_spec", {})
        opciones = [x for x in ex.get("execution_options") or []
                    if not (isinstance(x, dict) and x.get("field") == "user_ids")]
        opciones.append(_f("user_ids", "EQUAL", avisar))
        ex["execution_options"] = opciones
    datos["avisar"] = avisar


_CLAVE_OS = re.compile(r"^(?:PROTECT|ALERT)" + MARCA_OS + r"([^_]+)")


def clave_os(nombre: str) -> str | None:
    """Clave de una regla del OS sin sus parámetros: «PROTECT_OS_conjunto-sin-conversion_3x40EUR-sombra» y
    «ALERT_OS_conjunto-sin-conversion_4x80EUR» → «conjunto-sin-conversion»; «ALERT_OS_sin-conversiones-7d_…» →
    «sin-conversiones». None si no es del OS. Los nombres llevan el CPA, el tope y la ventana: al cambiar la ficha
    sale otro nombre para la misma protección."""
    m = _CLAVE_OS.match(str(nombre or "").removesuffix("-sombra"))
    return re.sub(r"-\d+d$", "", m.group(1)) if m else None


def _campanas_de(regla: dict) -> set[str] | None:
    """IDs del filtro campaign.id de una regla; None si mira toda la cuenta."""
    for f in _filtros(regla):
        if f.get("field") == "campaign.id":
            v = _valor(f.get("value"))
            return {str(x) for x in (v if isinstance(v, list) else [v])}
    return None


def solapadas(nuevas: list[dict], existentes: dict[str, dict]) -> list[dict]:
    """Reglas del OS activas en la cuenta con la misma clave que una de la propuesta, pero otro nombre (otros
    parámetros), que miran las mismas campañas. Quedarían actuando a la vez que las nuevas (hallazgo 5, I6). La
    versión «-sombra» de una regla nueva se trata aparte (es el paso de sombra a activo)."""
    nombres = {r["api"]["name"] for r in nuevas}
    por_clave: dict[str, list[dict]] = {}
    for r in nuevas:
        c = clave_os(r["api"]["name"])
        if c:
            por_clave.setdefault(c, []).append(r["api"])
    out = []
    for nombre, x in existentes.items():
        c = clave_os(nombre)
        if (not c or c not in por_clave or nombre in nombres or nombre.removesuffix("-sombra") in nombres
                or str(x.get("status") or "").upper() != "ENABLED"):
            continue
        suyas = _campanas_de(x)
        if any(suyas is None or (mias := _campanas_de(api)) is None or suyas & mias for api in por_clave[c]):
            out.append(x)
    return out


def _dibuja(datos: dict, moneda: str, pasos: bool) -> None:
    print(f"Cliente {datos['cliente']} · cuenta {datos.get('cuenta') or '—'} · evento {datos.get('evento')} · CPA "
          f"objetivo {dinero(float(datos.get('cpa_objetivo') or 0), moneda)} · madurez {datos.get('madurez_dias')} "
          f"días · modo {datos.get('modo')}")
    for r in datos["reglas"]:
        api = r["api"]
        accion = _ACCIONES.get(api.get("execution_spec", {}).get("execution_type"), "?")
        print(f"\n{api['name']}  [{accion} · {describir_horario(api.get('schedule_spec') or {})}]")
        if r.get("resumen"):
            print(f"  {r['resumen']}")
        if pasos:
            for n, paso in enumerate(r.get("ads_manager") or [], 1):
                print(f"    {n}. {paso}")


def _avisos_simular(datos: dict, ctx: M.Contexto) -> list[str]:
    """Lo que `crear --simular` no comprueba porque no usa la red (hallazgo 21, I6)."""
    out = []
    if any(r.get("clave") == "gasto-hoy-fuera-de-tope" for r in datos["reglas"] if isinstance(r, dict)):
        out.append("Sin red no se han comprobado los presupuestos activos: antes de crear la regla de gasto, mira que "
                   f"ningún conjunto o campaña activos pasa de {dinero(ctx.tope_cambio, ctx.moneda)}/día (Ads Manager o "
                   "`ads_get_ad_entities` por el MCP); si alguno pasa, la regla lo pausaría.")
    out.append("Sin red no se han comprobado las reglas _OS_ que ya hay en la cuenta: si cambiaste el CPA, el tope o el "
               "evento, desactiva las antiguas de la misma protección (Ads Manager → Reglas automatizadas) para que "
               "no actúen a la vez que las nuevas.")
    return out


def cmd_crear(a: argparse.Namespace) -> None:
    ctx = _contexto(a.cliente)
    datos, ruta = _lee_propuesta(a.propuesta, ctx)
    avisar = _ids(a.avisar, "--avisar")
    if avisar:
        _con_destinatarios(datos, avisar)
    errores, pendientes, avisos = revisar_propuesta(datos, ctx)
    if errores:
        if a.json:
            _json({"ok": False, "errores": errores, "pendientes": pendientes, "avisos": avisos})
            sys.exit(1)
        _salir("La propuesta no se puede crear:\n  - " + "\n  - ".join(errores), 1)
    if a.simular:
        if a.json:
            return _json({"ok": True, "simulado": True, "reglas": [r["api"]["name"] for r in datos["reglas"]],
                          "pendientes": pendientes, "avisos": avisos + _avisos_simular(datos, ctx),
                          "ads_manager": {r["api"]["name"]: r.get("ads_manager") or [] for r in datos["reglas"]}
                          if a.pasos else None})
        if a.pasos:
            print("En Ads Manager: menú → Reglas automatizadas → Crear regla → Regla personalizada. Una regla por "
                  "bloque; los nombres de los campos pueden variar algo según la versión y el idioma.\n")
        _dibuja(datos, ctx.moneda, a.pasos)
        for x in avisos:
            print(f"Aviso: {x}")
        if pendientes:
            print("\nPropuesta correcta. Para crearla por la API falta:\n  - " + "\n  - ".join(pendientes))
        print("\nNo se ha tocado Meta (--simular).")
        for x in _avisos_simular(datos, ctx):
            print(f"Aviso: {x}")
        return
    if pendientes:
        _salir("No se ha tocado Meta. Antes de crear falta:\n  - " + "\n  - ".join(pendientes), 1)

    meta = _conectar(ctx)
    try:
        M._comprueba_moneda(meta, ctx, estricto=True)
        existentes = {r.get("name"): r for r in meta.lista(f"{ctx.cuenta}/adrules_library",
                                                           fields="id,name,status,evaluation_spec", limit=200)}
        # La pausa por gasto no puede tocar algo que hoy ya tiene un presupuesto por encima del tope.
        _, conjuntos = M.presupuesto_activo(meta, ctx)
    except M.ErrorMeta as e:
        _salir(str(e), e.salida)
    fuera = []
    ahora = datetime.now(timezone.utc)
    for c in conjuntos:
        # Diarios y totales (por día, `meta_ads.diario_de`), del conjunto y de su campaña CBO (hallazgo 8, I6).
        for de, x in (("conjunto", c), ("campaña", c.get("campaign") or {})):
            dia = M.diario_de(x, ctx.moneda, ahora)
            if dia and dia > ctx.tope_cambio + 1e-9:
                total = "" if M.de_minimo(x.get("daily_budget"), ctx.moneda) else " (presupuesto total, por día)"
                fuera.append(f"{c.get('name')} ({c.get('id')}): {de} con {dinero(dia, ctx.moneda)}/día{total}")
    if fuera and any(r.get("clave") == "gasto-hoy-fuera-de-tope" for r in datos["reglas"]):
        _salir("No se ha tocado Meta. Hay presupuestos activos por encima del tope por cambio de la ficha "
               f"({dinero(ctx.tope_cambio, ctx.moneda)}/día) y la regla de gasto los pausaría:\n  - " + "\n  - ".join(fuera)
               + "\nBaja esos presupuestos o sube topes.cambio_dia en la ficha (decisión tuya) y vuelve a lanzar.", 1)
    viejas = solapadas(datos["reglas"], existentes)
    if viejas:
        ids = " ".join(str(x.get("id")) for x in viejas)
        _salir("No se ha tocado Meta. Hay reglas del OS activas para las mismas protecciones con otros parámetros "
               "(otro CPA, tope, evento o ventana); actuarían a la vez que las nuevas:\n  - "
               + "\n  - ".join(f"{x.get('name')} ({x.get('id')})" for x in viejas)
               + f"\nDesactívalas primero (no se borran): `pausar {ids} --cliente {ctx.slug} --confirmo`, y vuelve a "
                 "lanzar `crear`.", 1)
    nuevas = [r for r in datos["reglas"] if r["api"]["name"] not in existentes]
    ya = [r["api"]["name"] for r in datos["reglas"] if r["api"]["name"] in existentes]
    apagadas = [f"{n} ({existentes[n].get('id')})" for n in ya if existentes[n].get("status") != "ENABLED"]
    # Al pasar de sombra a activo, las versiones «-sombra» siguen avisando: hay que desactivarlas.
    sombras = [str(existentes[n + "-sombra"].get("id")) for n in (r["api"]["name"] for r in nuevas)
               if n + "-sombra" in existentes and existentes[n + "-sombra"].get("status") == "ENABLED"]
    if apagadas:
        avisos.append("Ya existen pero no están activas (no las toco; `reactivar` si las quieres): " + ", ".join(apagadas))
    if sombras:
        avisos.append(f"Al crear las versiones activas, desactiva las de sombra: `pausar {' '.join(sombras)} --cliente "
                      f"{ctx.slug} --confirmo`.")
    if not a.confirmo:
        if a.json:
            _json({"ok": False, "motivo": "falta --confirmo", "nuevas": [r["api"]["name"] for r in nuevas],
                   "ya_existen": ya, "avisos": avisos})
            sys.exit(1)
        _dibuja({**datos, "reglas": nuevas}, ctx.moneda, False)
        if ya:
            print(f"\nYa existen (no se tocan): {', '.join(ya)}")
        for x in avisos:
            print(f"Aviso: {x}")
        _salir(f"\nNo se ha creado nada. Se crearían {len(nuevas)} reglas que actúan solas 24/7. Solo con el sí del "
               "usuario en este momento: repite con --confirmo.", 1)
    ruta_estado = ruta.with_name(ruta.stem + ".estado.json")
    estado = json.loads(ruta_estado.read_text(encoding="utf-8")) if ruta_estado.exists() else {}
    estado.setdefault("cuenta", ctx.cuenta)
    estado.setdefault("reglas", {})
    for nombre in ya:
        estado["reglas"].setdefault(nombre, str(existentes[nombre].get("id") or ""))
    creadas = []
    try:
        for r in nuevas:
            api = r["api"]
            rid = str(meta.escribe(f"{ctx.cuenta}/adrules_library", name=api["name"], status=api.get("status", "ENABLED"),
                                   evaluation_spec=api["evaluation_spec"], execution_spec=api["execution_spec"],
                                   schedule_spec=api.get("schedule_spec"))["id"])
            estado["reglas"][api["name"]] = rid
            ruta_estado.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            comun.registrar_cambio("meta", "cli", "crear_regla", rid, ctx.slug,
                                   f"{api['name']}: {api['execution_spec'].get('execution_type')}")
            creadas.append((r, rid))
    except M.ErrorMeta as e:
        hechas = ", ".join(rid for _, rid in creadas) or "ninguna"
        _salir(f"{e}\nCreadas antes del error: {hechas} (en {_rel(ruta_estado)}). Si Meta rechaza una fórmula, "
               "corrige esa regla o quítala de la propuesta y relanza: las que ya existen no se duplican.", e.salida)
    if a.json:
        return _json({"ok": True, "creadas": {r["api"]["name"]: rid for r, rid in creadas}, "ya_existian": ya,
                      "estado": _rel(ruta_estado), "avisos": avisos})
    print(f"Creadas {len(creadas)} reglas en {ctx.cuenta}" + (f"; ya existían {len(ya)}" if ya else "") + ".")
    print("Compruébalas en Ads Manager → Reglas automatizadas: suscriptores de los avisos y próxima ejecución.")
    for x in avisos:
        print(f"Aviso: {x}")
    if creadas:
        print("Filas para el change log:")
        for r, rid in creadas:
            accion = r["api"]["execution_spec"].get("execution_type")
            print(fila_change_log(f"{r['api']['name']} ({rid})", f"— → regla activa ({_ACCIONES.get(accion, accion)})",
                                  f"Protección 24/7: {r.get('resumen', '')}",
                                  "0 pausas erróneas; revisar `historial` (cuántas veces actuó y si acertó)"))


# ---------------------------------------------------------------- pausar y reactivar

def _reglas_de_la_cuenta(meta: M.Meta, ctx: M.Contexto, ids: list[str]) -> list[dict]:
    salida = []
    for rid in ids:
        r = meta.uno(rid, fields="id,name,status,account_id,evaluation_spec,execution_spec,schedule_spec")
        if str(r.get("account_id", "")).removeprefix("act_") != ctx.cuenta.removeprefix("act_"):
            _salir(f"La regla {rid} no es de la cuenta de la ficha ({ctx.cuenta}).", 1)
        salida.append(r)
    return salida


def _cambiar_estado(a: argparse.Namespace, nuevo: str) -> None:
    ctx = _contexto(a.cliente)
    ids = [str(x) for x in a.ids]
    if any(not re.fullmatch(r"\d{3,25}", x) for x in ids):
        _salir("Los IDs de regla son numéricos (los da `listar`).", 1)
    meta = _conectar(ctx)
    try:
        reglas = _reglas_de_la_cuenta(meta, ctx, ids)
    except M.ErrorMeta as e:
        _salir(str(e), e.salida)
    if nuevo == "ENABLED":
        for r in reglas:
            graves = [t for g, t in analizar(r) if g == "bloquea"]
            if graves:
                _salir(f"No reactivo «{r.get('name')}» ({r['id']}): {graves[0]}", 1)
    verbo = "desactivar" if nuevo == "DISABLED" else "reactivar"
    if not a.json:
        for r in reglas:
            print(f"  {r['id']:<20}{str(r.get('name'))[:60]:<62}{r.get('status')} → {nuevo}")
    if not a.confirmo:
        if a.json:
            _json({"ok": False, "motivo": "falta --confirmo", "reglas": ids})
            sys.exit(1)
        _salir(f"No se ha cambiado nada. Solo con el sí del usuario en este momento: repite con --confirmo para "
               f"{verbo}.", 1)
    try:
        for r in reglas:
            meta.escribe(r["id"], status=nuevo)
            comun.registrar_cambio("meta", "cli", f"{verbo}_regla", r["id"], ctx.slug, str(r.get("name")))
    except M.ErrorMeta as e:
        _salir(str(e), e.salida)
    if a.json:
        return _json({"ok": True, "estado": nuevo, "reglas": ids})
    print(("Desactivadas" if nuevo == "DISABLED" else "Reactivadas") + f" ({len(ids)}). Fila para el change log:")
    for r in reglas:
        print(fila_change_log(f"{r.get('name')} ({r['id']})", f"{r.get('status')} → {nuevo}", "<motivo>",
                              "<métrica>", dias=7))


def cmd_pausar(a: argparse.Namespace) -> None:
    _cambiar_estado(a, "DISABLED")


def cmd_reactivar(a: argparse.Namespace) -> None:
    _cambiar_estado(a, "ENABLED")


# ---------------------------------------------------------------- leer

def cmd_listar(a: argparse.Namespace) -> None:
    ctx = _contexto(a.cliente)
    meta = _conectar(ctx)
    cpa = a_minimo(a.cpa, ctx.moneda) if a.cpa else None
    if cpa is None:
        ev, _ = evento(str((ctx.ficha.get("meta") or {}).get("evento_principal") or ""))
        valor, _ = cpa_de_ficha(ctx.slug, ev.fila)
        cpa = a_minimo(valor, ctx.moneda) if valor else None
    try:
        reglas = list(meta.lista(f"{ctx.cuenta}/adrules_library", limit=200,
                                 fields="id,name,status,evaluation_spec,execution_spec,schedule_spec,created_time,"
                                        "updated_time,disable_error_code"))
    except M.ErrorMeta as e:
        _salir(str(e), e.salida)
    filas = []
    for r in reglas:
        x = resumen_regla(r, ctx.moneda)
        x["problemas"] = [{"gravedad": g, "texto": t} for g, t in analizar(r, cpa)]
        filas.append(x)
    if a.json:
        return _json({"cuenta": ctx.cuenta, "moneda": ctx.moneda, "cpa_objetivo": de_minimo(cpa, ctx.moneda)
                      if cpa else None, "reglas": filas})
    if not filas:
        print(f"{ctx.cuenta} no tiene reglas automáticas: nada protege la cuenta fuera del horario del brief. "
              f"Siguiente: `proponer --cliente {ctx.slug}`.")
        return
    activas = sum(1 for x in filas if x["estado"] == "ENABLED")
    print(f"Reglas de {ctx.cuenta} ({ctx.slug}): {len(filas)}, {activas} activas"
          + ("" if cpa else " · sin CPA objetivo en la ficha: no puedo juzgar los umbrales de pausa") + "\n")
    for x in filas:
        print(f"[{x['estado']:<9}] {x['nombre']} ({x['id']}){' · del OS' if x['del_os'] else ''}")
        print(f"   {_ACCIONES.get(x['accion'], x['accion'])} {_NIVELES.get(x['nivel'], x['nivel'] or '¿?')} · "
              f"{x['periodo'] or 'sin periodo'} · {x['horario']} · avisa a {x['destinatarios']} persona(s)")
        if x["condiciones"]:
            print("   si: " + " · ".join(x["condiciones"]))
        for p in x["problemas"]:
            print(f"   {'PROHIBIDA' if p['gravedad'] == 'bloquea' else 'AVISO'}: {p['texto']}")
    graves = [x for x in filas if any(p["gravedad"] == "bloquea" for p in x["problemas"]) and x["estado"] == "ENABLED"]
    if graves:
        print(f"\n{len(graves)} reglas activas hacen algo que el OS no haría (marcadas PROHIBIDA). Desactivarlas es "
              f"una escritura: `pausar <id> --cliente {ctx.slug} --confirmo`, con el sí del usuario.")


def _fecha(valor) -> datetime | None:
    if isinstance(valor, (int, float)):
        return datetime.fromtimestamp(valor, timezone.utc)
    if not valor:
        return None
    t = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", str(valor).replace("Z", "+00:00"))
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def cmd_historial(a: argparse.Namespace) -> None:
    ctx = _contexto(a.cliente)
    meta = _conectar(ctx)
    desde = datetime.now(timezone.utc) - timedelta(days=a.dias)
    try:
        nombres = {str(r["id"]): r.get("name", "") for r in meta.lista(f"{ctx.cuenta}/adrules_library",
                                                                     fields="id,name", limit=200)}
        filas = []
        # hide_no_changes=true deja solo las ejecuciones que cambiaron algo (pausas); --todas incluye también las que
        # solo avisaron, que es lo que hay que revisar al acabar el modo sombra.
        for h in meta.lista(f"{ctx.cuenta}/adrules_history", hide_no_changes="false" if a.todas else "true",
                            limit=200):
            cuando = _fecha(h.get("timestamp"))
            if cuando and cuando < desde:
                break  # Meta lo devuelve de más reciente a más antiguo
            resultados = [x for x in h.get("results") or [] if isinstance(x, dict)]
            if not resultados and not h.get("exception_message"):
                continue  # evaluación sin ningún objeto que cumpliera la regla
            for res in resultados or [{}]:
                acciones = [str(x.get("action") or x.get("field") or "") for x in res.get("actions") or []
                            if isinstance(x, dict)]
                filas.append({"fecha": cuando.astimezone(ctx.zona).strftime("%Y-%m-%d %H:%M") if cuando else "",
                              "regla_id": str(h.get("rule_id") or ""),
                              "regla": nombres.get(str(h.get("rule_id") or ""), ""),
                              "objeto": str(res.get("object_id") or ""), "nivel": str(res.get("object_type") or ""),
                              "acciones": [x for x in acciones if x],
                              "error": h.get("exception_message") or ""})
    except M.ErrorMeta as e:
        _salir(str(e), e.salida)
    if a.json:
        return _json({"cuenta": ctx.cuenta, "desde": desde.date().isoformat(), "acciones": filas})
    if not filas:
        print(f"Ninguna regla ha {'actuado' if a.todas else 'cambiado nada'} en {ctx.cuenta} en los últimos {a.dias} "
              "días." + ("" if a.todas else " Las que solo avisan se ven con --todas."))
        return
    print(f"Lo que han hecho las reglas en {ctx.cuenta} desde {desde.date()} (hora de la ficha):")
    for f in filas:
        print(f"  {f['fecha']:<17}{(f['regla'] or f['regla_id'])[:48]:<50}{f['nivel']:<8}{f['objeto']:<20}"
              f"{', '.join(f['acciones']) or '—'}{'  ERROR: ' + f['error'] if f['error'] else ''}")
    print("Antes de dar por buena una pausa, comprueba en el conjunto que de verdad no convertía (dataset y CRM).")


def cmd_destinatarios(a: argparse.Namespace) -> None:
    ctx = _contexto(a.cliente)
    meta = _conectar(ctx)
    try:
        personas = list(meta.lista(f"{ctx.cuenta}/users", fields="id,name", limit=100))
    except M.ErrorMeta as e:
        _salir(f"{e}\nSi Meta no deja listar las personas, crear las reglas por la API sin --avisar no sirve (no "
               "avisarían a nadie): créalas en Ads Manager, donde eliges a los suscriptores en la propia regla.",
               e.salida)
    if a.json:
        return _json([{"id": p.get("id"), "nombre": p.get("name", "")} for p in personas])
    if not personas:
        print("La cuenta no devuelve personas: elige los suscriptores en Ads Manager.")
        return
    print("Personas con acceso a la cuenta (usa sus IDs en --avisar; no se guardan nombres en ningún archivo):")
    for p in personas:
        print(f"  {p.get('id', ''):<22}{p.get('name', '')}")


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> None:
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--cliente", help="slug del cliente (clientes/<slug>/ficha.md)")
    comunes.add_argument("--json", action="store_true", help="salida en JSON")
    p = argparse.ArgumentParser(description="Reglas automáticas de Meta que avisan o pausan, 24/7.")
    sub = p.add_subparsers(dest="comando", required=True)
    ls = sub.add_parser("listar", parents=[comunes], help="reglas de la cuenta, auditadas contra la KB")
    ls.add_argument("--cpa", type=comun.numero_arg, help="CPA objetivo para juzgar los umbrales (por defecto, el de la ficha)")
    pr = sub.add_parser("proponer", parents=[comunes], help="propuesta por defecto desde la ficha (sin red)")
    pr.add_argument("--cpa", type=comun.numero_arg, help="CPA objetivo del evento (por defecto, la tabla Economía de la ficha)")
    pr.add_argument("--evento", help="evento principal (por defecto, meta.evento_principal de la ficha)")
    pr.add_argument("--madurez", type=int, help="días que tarda en llegar el evento (por defecto, según el evento)")
    pr.add_argument("--multiplicador", type=comun.numero_arg, default=None,
                    help="kill a k× el CPA objetivo sin conversión (≥2); por defecto 4 en cuentas pequeñas y 3 con "
                         "≥30 conversiones/semana")
    pr.add_argument("--conversiones-semana", type=comun.numero_arg, default=None,
                    help="conversiones por semana y campaña del evento (sin el dato se supone cuenta pequeña, <30)")
    pr.add_argument("--activo", action="store_true",
                    help="las pausas por conversión pausan (sin esto, modo sombra: solo avisan, KB 07 §6.2)")
    pr.add_argument("--campanas", help="IDs de campaña, separados por comas, para las reglas de conversión")
    pr.add_argument("--avisar", help="IDs de usuario que reciben los avisos (los da `destinatarios`)")
    pr.add_argument("--salida", help="ruta del JSON (por defecto clientes/<slug>/planes/reglas-<fecha>.json)")
    cr = sub.add_parser("crear", parents=[comunes], help="crea las reglas de una propuesta (requiere --confirmo)")
    cr.add_argument("propuesta", help="JSON de `proponer`")
    cr.add_argument("--simular", action="store_true", help="solo revisa y dibuja; no toca Meta")
    cr.add_argument("--pasos", action="store_true", help="con --simular: pasos para crearlas en Ads Manager")
    cr.add_argument("--avisar", help="IDs de usuario que reciben los avisos (sustituye a los de la propuesta)")
    cr.add_argument("--confirmo", action="store_true", help="el usuario ha dicho que sí en este momento")
    for nombre, ayuda in (("pausar", "desactiva reglas (no las borra; requiere --confirmo)"),
                          ("reactivar", "reactiva reglas que solo avisan o pausan (requiere --confirmo)")):
        x = sub.add_parser(nombre, parents=[comunes], help=ayuda)
        x.add_argument("ids", nargs="+", help="IDs de regla (los da `listar`)")
        x.add_argument("--confirmo", action="store_true", help="el usuario ha dicho que sí en este momento")
    hi = sub.add_parser("historial", parents=[comunes], help="qué han cambiado las reglas")
    hi.add_argument("--dias", type=int, default=7, help="días hacia atrás (por defecto 7)")
    hi.add_argument("--todas", action="store_true", help="también las ejecuciones que solo avisaron (modo sombra)")
    sub.add_parser("destinatarios", parents=[comunes], help="personas de la cuenta (IDs para --avisar)")
    a = p.parse_args(argv)
    ordenes = {"listar": cmd_listar, "proponer": cmd_proponer, "crear": cmd_crear, "pausar": cmd_pausar,
               "reactivar": cmd_reactivar, "historial": cmd_historial, "destinatarios": cmd_destinatarios}
    try:
        ordenes[a.comando](a)
    except M.ErrorMeta as e:
        _salir(str(e), e.salida)


if __name__ == "__main__":
    main()
