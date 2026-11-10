#!/usr/bin/env python3
"""Economía unitaria para Meta Ads: cuánto puedes pagar por lead, cita, prueba o venta, y qué esperar al invertir.

Modos:
  ecommerce    CPA y ROAS break-even y target por pedido (IVA, devoluciones, location fee, LTV, incrementalidad)
  leadgen      servicios y high-ticket: cash por venta, CPL / coste por cualificado, cita, show y venta break-even y
               target, simulación con una inversión y tabla de sensibilidad show × cierre
  suscripcion  SaaS: CAC máximo por suscriptor y por prueba según churn, margen y payback
  prevision    escenarios de inversión → leads, citas, ventas (o pruebas y clientes de pago) y CAC esperables, con
               bandas pesimista–optimista por supuestos y el ruido de Poisson de un mes. Para planificar y para
               propuestas: un rango honesto, no una promesa.

Base (léelas para entender cada número):
  meta-ads-kb/09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md
  meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md
  meta-ads-kb/06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md
  meta-ads-kb/13-sistema-operativo/06-framework-escalado.md §3 (curva de respuesta: conversiones ∝ gasto^b)
  Location fees (fuera del presupuesto, desde 2026-07-01): UK 0.02 · ES/FR/IT 0.03 · AT/TR 0.05
  (meta-ads-kb/00-ESTADO-ACTUAL-2026.md).

Ejemplos:
  python3 -I herramientas/economia.py ecommerce --aov 85 --iva 0.21 --cogs-pct 0.30 --envio 6 --pasarela-pct 0.02 \
      --devoluciones-pct 0.05 --fee-pais 0.03 --valor-meta con_iva
  python3 -I herramientas/economia.py leadgen --precio 5000 --iva 0 --entrega-pct 0.5 --closer-pct 0.10 \
      --cualif 0.4 --agenda 0.5 --show 0.75 --cierre 0.25 --inversion 10000 --cpl 40
  python3 -I herramientas/economia.py suscripcion --precio-mes 39 --iva 0.21 --margen 0.8 --churn 0.10 \
      --trial-a-pago 0.4 --payback-meses 6
  python3 -I herramientas/economia.py prevision --inversion 3000,6000,12000 --cpl 30-45 --cualif 0.4-0.6 \
      --agenda 0.5 --show 0.6-0.75 --cierre 0.15-0.25 --precio 5000 --entrega-pct 0.5 --closer-pct 0.1
  python3 -I herramientas/economia.py prevision --modelo saas --inversion 2000,5000 --cpl 15-25 \
      --activacion 0.3-0.5 --pago 0.15-0.25 --precio-mes 99 --margen 0.8 --churn 0.04
Rangos como «a-b» (pesimista y optimista; la base es el punto medio). Tasas entre 0 y 1.
`--cliente SLUG` toma de la ficha la moneda, el modelo por defecto de `prevision` (según el tipo), la tasa por
ubicación (`mercados`) y, en servicios, la pasarela (`stripe: true` → 3 %). `--json` en todos.

Supuestos que no pasas por argumento (bloque «supuestos» de la salida, con su origen; se cambian con su opción):
  pasarela  ecommerce 2 % (pago con tarjeta en la tienda). leadgen y prevision de servicios: 0 % con aviso (supone
            cobro por transferencia, como el IVA 0 de esos modos supone venta B2B), o 3 % si la ficha dice
            `stripe: true` (tope del rango de Stripe, ~1,5–3 %, KB 05/05). --pasarela-pct lo cambia.
  fee país  --fee-pais; si no, con --cliente, el mayor de los `mercados` de la ficha (ES/FR/IT 3 %, UK 2 %,
            AT/TR 5 %, el resto 0 %); si no, 0 %.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402

SIMBOLO = {"EUR": "€", "USD": "$", "GBP": "£", "MXN": "MX$", "COP": "COP", "ARS": "ARS", "CLP": "CLP"}
CURVA_KB = (0.6, 0.7, 0.8)  # b pesimista/base/optimista (KB 13/06 §3: típico 0,6–0,8) [STRONG INFERENCE]
# Tasa por ubicación que Meta cobra encima del gasto desde 2026-07-01 (meta-ads-kb/00-ESTADO-ACTUAL-2026.md).
# Clave: código ISO 3166-1 de dos letras (UK se acepta como alias de GB).
FEE_PAIS = {"ES": 0.03, "FR": 0.03, "IT": 0.03, "GB": 0.02, "UK": 0.02, "AT": 0.05, "TR": 0.05}
PASARELA_ECOMMERCE = 0.02
PASARELA_STRIPE = 0.03  # servicios con `stripe: true` en la ficha: tope del rango de Stripe (~1,5–3 %, KB 05/05)


class ErrorUsuario(Exception):
    pass


# ================================================================ lead gen y high-ticket (antes calculadora_funnel.py)
# Modelo (todo por venta, SIN IVA salvo que se indique):
#   cash_bruto  = cobro esperado por venta (mezcla pago único / cuotas, con impagos)
#   cash_neto   = cash_bruto sin IVA (si el precio lo incluye y no lo recuperas)
#   contribución = cash_neto·(1−reembolsos) − pasarela − comisiones − coste de entrega − coste fijo
#   BE CPA = contribución · BE por show = BE CPA·cierre · BE por cita = BE CPA·show·cierre
#   BE por cualificado = BE por cita·agenda · BE CPL = BE por cualificado·cualif · Target = BE·(1 − margen objetivo)
@dataclass
class Oferta:
    nombre: str
    precio: float                      # precio de lista (IVA incluido si iva > 0)
    iva: float = 0.0                   # 0.21 si el precio incluye IVA español y es B2C (no recuperable)
    pct_pago_unico: float = 1.0        # proporción de ventas al contado
    descuento_pago_unico: float = 0.0  # 0.10 = 10 % de descuento por pagar de golpe
    n_cuotas: int = 1                  # nº de cuotas del plan de pagos
    recargo_cuotas: float = 0.0        # 0.10 = el plan cuesta un 10 % más en total
    impago_cuotas: float = 0.0         # proporción del importe pendiente (cuotas 2..n) que no se cobra
    tasa_reembolso: float = 0.0        # proporción del cash que se devuelve (reembolsos + chargebacks)
    pasarela: float = 0.03             # comisión de Stripe/PayPal/financiera sobre el cobro bruto
    coste_entrega: float = 0.0         # % del cash neto que cuesta entregar (equipo, herramientas, soporte)
    comision_closer: float = 0.0       # % del cash neto tras reembolsos
    comision_setter: float = 0.0       # % del cash neto tras reembolsos
    coste_fijo_venta: float = 0.0      # importe fijo por venta (onboarding, licencias…)


@dataclass
class Funnel:
    lead_a_cualificado: float = 1.0
    cualificado_a_agenda: float = 1.0
    show: float = 1.0
    cierre: float = 1.0


def cash_por_venta(o: Oferta) -> dict:
    precio_pif = o.precio * (1 - o.descuento_pago_unico)
    precio_plan = o.precio * (1 + o.recargo_cuotas)
    if o.n_cuotas <= 1:
        cobro_plan = primer_cobro_plan = precio_plan
    else:
        cuota = precio_plan / o.n_cuotas
        cobro_plan = cuota + cuota * (o.n_cuotas - 1) * (1 - o.impago_cuotas)
        primer_cobro_plan = cuota
    contrato = o.pct_pago_unico * precio_pif + (1 - o.pct_pago_unico) * precio_plan
    bruto = o.pct_pago_unico * precio_pif + (1 - o.pct_pago_unico) * cobro_plan
    dia0 = o.pct_pago_unico * precio_pif + (1 - o.pct_pago_unico) * primer_cobro_plan
    neto = bruto / (1 + o.iva)
    tras_refund = neto * (1 - o.tasa_reembolso)
    pasarela = bruto * o.pasarela
    comisiones = tras_refund * (o.comision_closer + o.comision_setter)
    entrega = tras_refund * o.coste_entrega
    contribucion = tras_refund - pasarela - comisiones - entrega - o.coste_fijo_venta
    return {"contrato_medio_iva_incl": contrato, "cash_bruto_esperado": bruto, "cash_dia0_bruto": dia0,
            "cash_neto_sin_iva": neto, "cash_tras_reembolsos": tras_refund, "pasarela": pasarela,
            "comisiones_ventas": comisiones, "coste_entrega": entrega, "contribucion_por_venta": contribucion}


def break_evens(o: Oferta, f: Funnel, margen_objetivo: float = 0.5, fee_pais: float = 0.0) -> dict:
    """`fee_pais`: tasa por ubicación que Meta cobra encima del gasto (ES/FR/IT 3 %): el break-even se divide por
    1 + fee, como en ecommerce y suscripcion (hallazgo 14, I6)."""
    c = cash_por_venta(o)["contribucion_por_venta"] / (1 + fee_pais)
    be = {"BE_CPA": c, "BE_por_show": c * f.cierre, "BE_por_llamada_agendada": c * f.show * f.cierre,
          "BE_por_lead_cualificado": c * f.show * f.cierre * f.cualificado_a_agenda,
          "BE_CPL": c * f.show * f.cierre * f.cualificado_a_agenda * f.lead_a_cualificado}
    tgt = {k.replace("BE_", "TARGET_"): v * (1 - margen_objetivo) for k, v in be.items()}
    return {**be, **tgt, "lead_a_venta": f.lead_a_cualificado * f.cualificado_a_agenda * f.show * f.cierre}


def simular(o: Oferta, f: Funnel, inversion: float, cpl: float, fee_pais: float = 0.0) -> dict:
    """CPL, CPA y ROAS sobre la inversión (lo que ves en Ads Manager); el beneficio, sobre el coste con la tasa por
    ubicación."""
    cv = cash_por_venta(o)
    leads = inversion / cpl
    cualif = leads * f.lead_a_cualificado
    agendas = cualif * f.cualificado_a_agenda
    shows = agendas * f.show
    ventas = shows * f.cierre
    cash_bruto = ventas * cv["cash_bruto_esperado"]
    cash_dia0 = ventas * cv["cash_dia0_bruto"]
    contrib = ventas * cv["contribucion_por_venta"]
    return {"inversion": inversion, "CPL": cpl, "leads": leads, "cualificados": cualif, "agendas": agendas,
            "shows": shows, "ventas": ventas,
            "coste_por_agenda": inversion / agendas if agendas else None,
            "coste_por_show": inversion / shows if shows else None,
            "CPA": inversion / ventas if ventas else None,
            "cash_bruto_total_esperado": cash_bruto, "cash_dia0": cash_dia0,
            "ROAS_cash_esperado": cash_bruto / inversion if inversion else None,
            "ROAS_cash_dia0": cash_dia0 / inversion if inversion else None,
            "contribucion_total": contrib,
            **({"coste_total_con_fee": inversion * (1 + fee_pais)} if fee_pais else {}),
            "beneficio_tras_ads": contrib - inversion * (1 + fee_pais)}


def sensibilidad_be_cpl(o: Oferta, f: Funnel, shows=(0.5, 0.6, 0.7, 0.8),
                        cierres=(0.10, 0.15, 0.20, 0.25, 0.30), fee_pais: float = 0.0) -> dict:
    """CPL break-even por show rate (filas) y cierre (columnas), con el resto del funnel fijo."""
    c = cash_por_venta(o)["contribucion_por_venta"] / (1 + fee_pais)
    return {f"show {s:.0%}": {f"cierre {x:.0%}": round(c * s * x * f.cualificado_a_agenda * f.lead_a_cualificado, 2)
                              for x in cierres} for s in shows}


# ================================================================ supuestos por defecto
def _pct(v: float) -> str:
    return f"{v * 100:.2f}".rstrip("0").rstrip(".").replace(".", ",") + " %"


def _si(v) -> bool:
    return v is True or str(v).strip().lower() in ("true", "si", "sí", "yes", "1")


def fee_por_mercados(texto) -> tuple[float, str, list[str]]:
    """Tasa por ubicación a partir del campo `mercados` de la ficha («ES» o «ES, FR»): (fee, origen, avisos).

    Con varios mercados de fee distinto se toma el mayor (prudente) y se avisa."""
    codigos = [c.upper() for c in re.split(r"[,;/\s]+", str(texto or "").strip()) if c]
    if not codigos:
        return 0.0, "la ficha no tiene `mercados` rellenado: añádelo (p. ej. «mercados: ES») o pasa --fee-pais", []
    malos = [c for c in codigos if not re.fullmatch(r"[A-Z]{2}", c)]
    avisos = [f"`mercados` de la ficha: «{', '.join(malos)}» no es un código ISO de país de dos letras (ES, FR, MX…): "
              "se ignora"] if malos else []
    fees = {c: FEE_PAIS.get(c, 0.0) for c in codigos if c not in malos}
    if not fees:
        return 0.0, "ningún código válido en `mercados` de la ficha; corrígelo o pasa --fee-pais", avisos
    fee = max(fees.values())
    detalle = ", ".join(f"{c} {_pct(f)}" for c, f in fees.items())
    if len(set(fees.values())) > 1:
        avisos.append(f"Mercados con tasa por ubicación distinta ({detalle}): se aplica la mayor, {_pct(fee)}. Si el "
                      "gasto se reparte, calcula cada mercado con --fee-pais")
    return fee, f"ficha, mercados: {detalle}; cámbiala con --fee-pais", avisos


def resolver_supuestos(a, ficha: dict | None = None) -> None:
    """Fija los supuestos que no vinieron por argumento y anota su origen en `a.supuestos` (y `a.avisos_supuestos`)."""
    sup, avisos = {}, []
    servicios = a.modo == "leadgen" or (a.modo == "prevision" and a.modelo == "servicios" and a.precio
                                         and not a.contribucion_venta)
    if a.modo == "ecommerce" or servicios:
        if a.pasarela_pct is not None:
            origen = "--pasarela-pct"
        elif a.modo == "ecommerce":
            a.pasarela_pct, origen = PASARELA_ECOMMERCE, "por defecto (pago con tarjeta); cámbiala con --pasarela-pct"
        elif ficha is not None and _si(ficha.get("stripe")):
            a.pasarela_pct = PASARELA_STRIPE
            origen = "ficha con `stripe: true` (tope del rango de Stripe, KB 05/05); cámbiala con --pasarela-pct"
        else:
            a.pasarela_pct = 0.0
            origen = "por defecto: cobro por transferencia; con tarjeta, Stripe o financiera, pasa --pasarela-pct"
            avisos.append("Pasarela al 0 % por defecto (supone cobro por transferencia). Si cobras con tarjeta, Stripe "
                          "o una financiera, pasa --pasarela-pct (Stripe ~0.015–0.03; financieras, más; KB 05/05)")
        sup["pasarela"] = {"valor": a.pasarela_pct, "origen": origen}
    elif getattr(a, "pasarela_pct", None) is None and hasattr(a, "pasarela_pct"):
        a.pasarela_pct = 0.0  # no interviene en el cálculo
    if a.modo != "prevision" or servicios or (a.modelo == "saas" and a.precio_mes):
        if not getattr(a, "iva_por_defecto", False):
            origen = "--iva"
        elif a.modo == "ecommerce":
            origen = "por defecto (precio B2C con IVA español incluido); cámbialo con --iva"
        elif a.iva:
            origen = "por defecto (precio B2C con IVA español incluido); si vendes a empresas, --iva 0"
        else:
            origen = "por defecto (venta B2B: el IVA se recupera); si el precio es B2C con IVA incluido, --iva 0.21"
        sup["IVA"] = {"valor": a.iva, "origen": origen}
    if a.fee_pais is not None:
        origen = "--fee-pais"
    elif ficha is not None:
        a.fee_pais, origen, av = fee_por_mercados(ficha.get("mercados"))
        avisos += av
    else:
        a.fee_pais = 0.0
        origen = "por defecto, sin --cliente; si anuncias en ES/FR/IT pasa --fee-pais 0.03 (UK 0.02, AT/TR 0.05)"
    sup["fee país"] = {"valor": a.fee_pais, "origen": origen}
    a.supuestos, a.avisos_supuestos = sup, avisos


def _con_supuestos(a, res: dict) -> dict:
    """Pone el bloque «supuestos» delante y suma sus avisos al «aviso» del modo (este, primero)."""
    avisos = [*([res.pop("aviso")] if "aviso" in res else []), *getattr(a, "avisos_supuestos", [])]
    out = {"supuestos": getattr(a, "supuestos", {}), **res}
    if avisos:
        out["aviso"] = " · ".join(avisos)
    return out


# ================================================================ modos
def _oferta(a) -> Oferta:
    return Oferta(getattr(a, "nombre", "Oferta"), precio=a.precio, iva=a.iva, pct_pago_unico=a.pct_pago_unico,
                  descuento_pago_unico=a.descuento_pago_unico, n_cuotas=a.cuotas, recargo_cuotas=a.recargo_cuotas,
                  impago_cuotas=a.impago_cuotas, tasa_reembolso=a.reembolsos, pasarela=a.pasarela_pct,
                  coste_entrega=a.entrega_pct, comision_closer=a.closer_pct, comision_setter=a.setter_pct,
                  coste_fijo_venta=a.coste_fijo)


def ecommerce(a) -> dict:
    aov_neto = a.aov / (1 + a.iva) if a.aov_incluye_iva else a.aov
    ingreso_neto = aov_neto * (1 - a.devoluciones_pct)
    cogs = a.cogs_eur if a.cogs_eur is not None else aov_neto * a.cogs_pct
    pasarela = (a.aov if a.aov_incluye_iva else aov_neto * (1 + a.iva)) * a.pasarela_pct
    otros = aov_neto * a.otros_pct
    cm1 = ingreso_neto - cogs - a.envio - pasarela - otros
    be_cpa = cm1 / (1 + a.fee_pais)
    valor_meta = aov_neto * (1 + a.iva) if a.valor_meta == "con_iva" else aov_neto
    tgt_cpa = be_cpa * (1 - a.margen_objetivo)
    res = {
        "pedido": {
            "AOV neto (sin IVA)": round(aov_neto, 2), "ingreso neto tras devoluciones": round(ingreso_neto, 2),
            "COGS": round(cogs, 2), "envío": a.envio, "pasarela": round(pasarela, 2),
            "otros variables": round(otros, 2), "contribución por pedido (CM1)": round(cm1, 2),
            "CM1 % sobre AOV neto": round(cm1 / aov_neto, 4) if aov_neto else 0.0,
        },
        "break-even (primera compra)": {
            "CPA break-even (incluye fee país)": round(be_cpa, 2),
            "valor que recibe Meta por pedido": round(valor_meta, 2),
            "ROAS break-even en Ads Manager": round(valor_meta / be_cpa, 2) if be_cpa > 0 else None,
            "MER break-even (ingresos netos / gasto)": round(aov_neto / be_cpa, 2) if be_cpa > 0 else None,
        },
        "target": {
            "margen objetivo sobre contribución": a.margen_objetivo,
            "CPA target": round(tgt_cpa, 2),
            "ROAS target en Ads Manager": round(valor_meta / tgt_cpa, 2) if tgt_cpa > 0 else None,
        },
    }
    if cm1 <= 0:
        res["aviso"] = "La contribución por pedido es ≤ 0: ningún CPA es rentable en primera compra"
    if a.pedidos_ltv and a.pedidos_ltv > 1:
        cm_ltv = cm1 * a.pedidos_ltv
        res["con LTV (pedidos por cliente en la ventana de payback)"] = {
            "pedidos por cliente": a.pedidos_ltv, "contribución LTV": round(cm_ltv, 2),
            "nCAC break-even (LTV)": round(cm_ltv / (1 + a.fee_pais), 2),
            "nCAC target (LTV)": round(cm_ltv / (1 + a.fee_pais) * (1 - a.margen_objetivo), 2),
        }
    if a.incrementalidad and a.incrementalidad < 1:
        res["ajuste por incrementalidad"] = {
            "factor de incrementalidad (incremental / atribuido)": a.incrementalidad,
            "ROAS break-even que debe verse en Ads Manager": round(valor_meta / (be_cpa * a.incrementalidad), 2)
            if be_cpa > 0 else None,
        }
    if a.cpa:
        margen = cm1 - a.cpa * (1 + a.fee_pais)
        res["con tu CPA actual"] = {"CPA actual": a.cpa, "beneficio por pedido tras ads": round(margen, 2),
                                    "¿rentable en primera compra?": "sí" if margen > 0 else "no"}
    return _con_supuestos(a, res)


def leadgen(a) -> dict:
    o = _oferta(a)
    f = Funnel(lead_a_cualificado=a.cualif, cualificado_a_agenda=a.agenda, show=a.show, cierre=a.cierre)
    cash = {k: round(v, 2) for k, v in cash_por_venta(o).items()}
    fee = getattr(a, "fee_pais", 0.0) or 0.0
    be = {k: (round(v, 4 if k == "lead_a_venta" else 2))
          for k, v in break_evens(o, f, a.margen_objetivo, fee).items()}
    titulo = f"break-even y target (margen objetivo {a.margen_objetivo:.0%}" + (f", fee país {fee:.0%})" if fee else ")")
    res = {"cash por venta": cash, titulo: be}
    if a.inversion and a.cpl:
        sim = simular(o, f, inversion=a.inversion, cpl=a.cpl, fee_pais=fee)
        res[f"simulación: inversión {a.inversion:,.0f} a CPL {a.cpl:g}"] = {
            k: (round(v, 2) if isinstance(v, float) else v) for k, v in sim.items()}
    res["sensibilidad: CPL break-even por show (filas) y cierre (columnas)"] = sensibilidad_be_cpl(o, f, fee_pais=fee)
    if cash["contribucion_por_venta"] <= 0:
        res["aviso"] = "La contribución por venta es ≤ 0: revisa precio, comisiones y coste de entrega"
    return _con_supuestos(a, res)


def _payback_meses(cac: float, contrib_mes: float, retencion: float, tope: int = 120) -> float | None:
    """Meses hasta que la contribución acumulada (con churn) cubre el CAC; None si no llega en `tope` meses."""
    if contrib_mes <= 0:
        return None
    acumulado = 0.0
    for t in range(tope):
        paso = contrib_mes * retencion ** t
        if acumulado + paso >= cac:
            return round(t + (cac - acumulado) / paso, 1)
        acumulado += paso
    return None


def suscripcion(a) -> dict:
    p = a.precio_mes / (1 + a.iva)
    contrib_mes = p * a.margen
    retencion = 1 - a.churn
    ltv = contrib_mes / a.churn
    payback = sum(contrib_mes * retencion ** t for t in range(a.payback_meses))
    res = {
        "suscriptor": {"precio mensual neto": round(p, 2), "contribución mensual": round(contrib_mes, 2),
                       "vida media (meses)": round(1 / a.churn, 1), "LTV en contribución": round(ltv, 2)},
        f"CAC máximo con payback ≤ {a.payback_meses} meses": {
            "por suscriptor de pago": round(payback / (1 + a.fee_pais), 2),
            "por prueba / alta (× conversión prueba→pago)": round(payback / (1 + a.fee_pais) * a.trial_a_pago, 2)},
        "CAC máximo por LTV completo (sin restricción de caja)": {
            "por suscriptor de pago": round(ltv / (1 + a.fee_pais), 2),
            "por prueba / alta": round(ltv / (1 + a.fee_pais) * a.trial_a_pago, 2)},
    }
    if getattr(a, "iva_por_defecto", False):
        res["aviso"] = (f"IVA del {a.iva:.0%} supuesto por defecto (precio B2C con IVA español incluido): pasa --iva 0 "
                        "si vendes a empresas o el precio va sin IVA")
    return _con_supuestos(a, res)


# ================================================================ previsión
def rango(texto, nombre: str, tasa: bool = False) -> tuple[float, float, float]:
    """«30-45» → (30, 37.5, 45); «30» → (30, 30, 30). Admite coma decimal."""
    if texto is None:
        raise ErrorUsuario(f"Falta --{nombre}")
    t = str(texto).strip().replace(" ", "")
    m = re.fullmatch(r"([\d.,]+)(?:[-:]([\d.,]+))?", t)
    if not m:
        raise ErrorUsuario(f"--{nombre} va como número o rango «a-b»: {texto!r}")
    from registro_creativo import num_humano
    lo = num_humano(m[1])
    hi = num_humano(m[2]) if m[2] else lo
    if lo is None or hi is None:
        raise ErrorUsuario(f"--{nombre}: número no válido {texto!r}")
    lo, hi = min(lo, hi), max(lo, hi)
    if tasa and not (0 < lo and hi <= 1):
        raise ErrorUsuario(f"--{nombre} es una tasa entre 0 y 1 (usa 0.4 para un 40 %): {texto!r}")
    if not tasa and lo <= 0:
        raise ErrorUsuario(f"--{nombre} debe ser mayor que 0")
    return lo, (lo + hi) / 2, hi


def poisson_cuantil(lam: float, q: float) -> int:
    if lam <= 0:
        return 0
    k, termino = 0, math.exp(-lam)
    acumulado = termino
    while acumulado < q and k < 10 * lam + 100:
        k += 1
        termino *= lam / k
        acumulado += termino
    return k


def _coste(c0: float, inv: float, ref: float, b: float) -> float:
    """Coste por lead a la inversión `inv` si se observó `c0` a `ref` y conversiones ∝ gasto^b."""
    return c0 * (inv / ref) ** (1 - b)


def prevision(a) -> dict:
    from registro_creativo import num_humano
    inversiones = [num_humano(x) for x in re.split(r"[;,\s]+", str(a.inversion)) if x.strip()]
    if not inversiones or any(not i or i <= 0 for i in inversiones):
        raise ErrorUsuario("--inversion va como lista de importes > 0 separados por comas: 3000,6000,12000")
    inversiones = sorted(set(inversiones))
    ref = num_humano(str(a.inversion_ref)) if a.inversion_ref else inversiones[0]
    if not ref or ref <= 0:
        raise ErrorUsuario("--inversion-ref debe ser mayor que 0")
    curva = rango(a.curva, "curva", tasa=True) if a.curva else CURVA_KB
    modelo = a.modelo
    contrib_mes = None
    coste = rango(a.cpa if modelo == "ecommerce" else a.cpl, "cpa" if modelo == "ecommerce" else "cpl")
    etapas: list[tuple[str, str, tuple]] = []  # (nombre de la etapa, flag, rango de la tasa)
    if modelo == "servicios":
        etapas = [("cualificados", "cualif", rango(a.cualif, "cualif", True)),
                  ("citas", "agenda", rango(a.agenda, "agenda", True)),
                  ("shows", "show", rango(a.show, "show", True)),
                  ("ventas", "cierre", rango(a.cierre, "cierre", True))]
        if a.contribucion_venta:
            valor = a.contribucion_venta
        elif a.precio:
            valor = cash_por_venta(_oferta(a))["contribucion_por_venta"]
        else:
            valor = None
    elif modelo == "saas":
        etapas = [("activados", "activacion", rango(a.activacion, "activacion", True)),
                  ("clientes_pago", "pago", rango(a.pago, "pago", True))]
        valor = None
        contrib_mes = a.precio_mes / (1 + a.iva) * a.margen if a.precio_mes else None
    else:
        etapas = []
        valor = a.contribucion_pedido
    primera = "leads" if modelo == "servicios" else ("registros" if modelo == "saas" else "ventas")
    final = etapas[-1][0] if etapas else "ventas"

    def escenario(inv: float, cual: str) -> dict:
        idx = {"pesimista": 0, "base": 1, "optimista": 2}[cual]
        if cual == "base":
            b = curva[1]
        else:  # el peor b depende de si escalas por encima o por debajo de la referencia
            arriba = inv >= ref
            b = curva[0] if (cual == "pesimista") == arriba else curva[2]
        c0 = coste[2 - idx]  # pesimista = coste alto
        c = _coste(c0, inv, ref, b)
        r = {"coste_por_" + ("pedido" if modelo == "ecommerce" else "lead"): c, primera: inv / c}
        n = r[primera]
        for nombre, _, t in etapas:
            n = n * t[idx]
            r[nombre] = n
        r["cac"] = inv / r[final] if r[final] else None
        if modelo == "servicios":
            r["coste_por_cita"] = inv / r["citas"] if r["citas"] else None
        coste_total = inv * (1 + a.fee_pais)
        if modelo == "saas" and contrib_mes:
            r["mrr_nuevo"] = r[final] * a.precio_mes / (1 + a.iva)
            r["payback_meses"] = _payback_meses(coste_total / r[final], contrib_mes, 1 - a.churn) if r[final] and a.churn else None
            if a.churn:
                r["contribucion_ltv"] = r[final] * contrib_mes / a.churn
                r["beneficio_ltv_tras_ads"] = r["contribucion_ltv"] - coste_total
        elif valor is not None:
            r["contribucion"] = r[final] * valor
            r["beneficio_tras_ads"] = r["contribucion"] - coste_total
        return r

    filas, avisos = [], []
    for inv in inversiones:
        esc = {c: escenario(inv, c) for c in ("pesimista", "base", "optimista")}
        lam = esc["base"][final]
        fila = {"inversion": inv, "coste_total_con_fee": round(inv * (1 + a.fee_pais), 2)}
        for k in esc["base"]:
            vals = [esc[c][k] for c in ("pesimista", "base", "optimista")]
            fila[k] = {c: (round(v, 2) if v is not None else None) for c, v in zip(("pesimista", "base", "optimista"), vals)}
        fila[f"ruido_{final}"] = {"p10": poisson_cuantil(lam, 0.10), "p90": poisson_cuantil(lam, 0.90),
                                  "prob_cero": round(math.exp(-lam), 4)}
        filas.append(fila)
        if lam < 5:
            avisos.append(f"Con {_num(inv, 0)} se esperan {_num(lam, 1)} {final.replace('_', ' ')} (base): con menos "
                          f"de ~5 el resultado de un periodo es casi azar (probabilidad de 0: {math.exp(-lam):.0%}). "
                          "Preséntalo como rango, nunca como promesa [STRONG INFERENCE: Poisson]")
        if inv / ref > 3 or ref / inv > 3:
            avisos.append(f"{_num(inv, 0)} está a más de 3× de la inversión de referencia ({_num(ref, 0)}): la curva "
                          "de respuesta extrapolada tan lejos es poco fiable [HYPOTHESIS]")
    if modelo == "servicios" and valor is None:
        avisos.append("Sin --precio ni --contribucion-venta no se calcula la contribución ni el beneficio")
    if modelo == "saas" and contrib_mes and getattr(a, "iva_por_defecto", False):
        avisos.append("--precio-mes se toma sin IVA (--iva 0 por defecto; `suscripcion` supone 0,21): pasa --iva 0.21 "
                      "si el precio es B2C con IVA incluido")
    avisos += getattr(a, "avisos_supuestos", [])
    supuestos = {
        "modelo": modelo, "inversion_ref": ref, "coste_ref": {"pesimista": coste[2], "base": coste[1], "optimista": coste[0]},
        "curva_b": {"pesimista": curva[0], "base": curva[1], "optimista": curva[2]},
        "origen_curva": "--curva" if a.curva else "KB 13-sistema-operativo/06-framework-escalado.md §3 (b 0,6–0,8)",
        "tasas": {flag: {"pesimista": t[0], "base": t[1], "optimista": t[2]} for _, flag, t in etapas},
        "fee_pais": a.fee_pais,
        "valor_por_venta": round(valor, 2) if valor is not None else None,
        "fijados": getattr(a, "supuestos", {}),
    }
    return {"supuestos": supuestos, "escenarios": filas, "avisos": avisos}


# ================================================================ salida
def _num(v, dec=2) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "sí" if v else "no"
    if isinstance(v, (int, float)):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return "—"
        s = f"{v:,.{dec}f}" if isinstance(v, float) else f"{v:,}"
        return s.replace(",", "·").replace(".", ",").replace("·", ".")
    return str(v)


def _fmt(v, clave: str = "") -> str:
    k = clave.lower()
    if isinstance(v, float) and abs(v) <= 1 and any(t in k for t in ("%", "margen objetivo", "factor", "lead_a_venta",
                                                                       "tasa")):
        return f"{v:.2%}".replace(".", ",")
    return _num(v)


def _salida_texto(d: dict, titulo: str) -> None:
    print(f"== {titulo}")
    for k, v in d.items():
        if k == "supuestos":
            print("-- supuestos (de dónde sale cada uno)")
            for nombre, s in v.items():
                print(f"   {nombre} {_pct(s['valor'])} · {s['origen']}")
        elif isinstance(v, dict) and v and all(isinstance(x, dict) for x in v.values()):  # tabla
            print(f"-- {k}")
            cols = list(next(iter(v.values())).keys())
            print("   " + " " * 12 + "".join(f"{c:>13s}" for c in cols))
            for fila, vals in v.items():
                print(f"   {fila:12s}" + "".join(f"{_num(vals[c]):>13s}" for c in cols))
        elif isinstance(v, dict):
            print(f"-- {k}")
            for k2, v2 in v.items():
                print(f"   {k2:40s} {_fmt(v2, k2)}")
        else:
            print(f"   {k:40s} {_fmt(v, k)}")


ETIQUETAS = {"cac": "CAC (coste por venta o cliente)", "contribucion": "contribución",
             "beneficio_tras_ads": "beneficio tras ads (con fee)", "mrr_nuevo": "MRR nuevo",
             "payback_meses": "payback (meses)", "contribucion_ltv": "contribución LTV",
             "beneficio_ltv_tras_ads": "beneficio LTV tras ads (con fee)", "clientes_pago": "clientes de pago"}


def _texto_prevision(r: dict, moneda: str) -> None:
    s = r["supuestos"]
    print(f"== previsión ({s['modelo']}) · referencia {_num(s['inversion_ref'], 0)} {moneda} · curva b "
          f"{s['curva_b']['pesimista']}–{s['curva_b']['optimista']} · fee país {s['fee_pais']:.0%}")
    print("   Cada celda: base (pesimista – optimista). Pesimista = peor extremo de cada supuesto a la vez.\n")
    esc = r["escenarios"]
    claves = [k for k in esc[0] if isinstance(esc[0][k], dict) and "base" in esc[0][k]]
    ruido = next(k for k in esc[0] if k.startswith("ruido_"))
    cab = "| Métrica | " + " | ".join(f"{_num(e['inversion'], 0)} {moneda}" for e in esc) + " |"
    print(cab)
    print("|---|" + "---|" * len(esc))
    decimales = {"leads": 0, "registros": 0, "cualificados": 0, "activados": 0, "citas": 1, "shows": 1,
                 "ventas": 1, "clientes_pago": 1, "payback_meses": 1}
    for k in claves:
        dec = decimales.get(k, 2)
        celdas = []
        for e in esc:
            v = e[k]
            celdas.append(f"{_num(v['base'], dec)} ({_num(v['pesimista'], dec)} – {_num(v['optimista'], dec)})")
        print(f"| {ETIQUETAS.get(k, k.replace('_', ' '))} | " + " | ".join(celdas) + " |")
    final = ruido.replace("ruido_", "")
    print(f"| {final.replace('_', ' ')}: rango del 80 % por azar (base) | "
          + " | ".join(f"{e[ruido]['p10']} – {e[ruido]['p90']}" for e in esc) + " |")
    print(f"| probabilidad de 0 {final.replace('_', ' ')} (base) | "
          + " | ".join(f"{e[ruido]['prob_cero']:.1%}".replace(".", ",") for e in esc) + " |")
    print(f"\nSupuestos: coste por lead {_num(s['coste_ref']['optimista'])}–{_num(s['coste_ref']['pesimista'])} "
          f"{moneda} a {_num(s['inversion_ref'], 0)} {moneda}; "
          + "; ".join(f"{k} {v['pesimista']}–{v['optimista']}" for k, v in s["tasas"].items())
          + (f"; contribución por venta {_num(s['valor_por_venta'])} {moneda}" if s["valor_por_venta"] else "")
          + f". Curva: {s['origen_curva']}.")
    for nombre, x in s.get("fijados", {}).items():
        print(f"Supuesto: {nombre} {_pct(x['valor'])} · {x['origen']}")
    for av in r["avisos"]:
        print(f"Aviso: {av}")


# ================================================================ CLI
_numero_arg = _comun.numero_arg  # «0,175», «0.175», «5.000» o «1 200», como en el resto de herramientas


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def _args_oferta(p: argparse.ArgumentParser, precio_obligatorio: bool) -> None:
    p.add_argument("--nombre", default="Oferta")
    p.add_argument("--precio", type=_numero_arg, required=precio_obligatorio, help="precio de lista")
    p.add_argument("--iva", type=_numero_arg, default=None,
                   help="IVA incluido en el precio y no recuperable (B2C: 0.21); por defecto 0")
    p.add_argument("--pct-pago-unico", type=_numero_arg, default=1.0)
    p.add_argument("--descuento-pago-unico", type=_numero_arg, default=0.0)
    p.add_argument("--cuotas", type=int, default=1)
    p.add_argument("--recargo-cuotas", type=_numero_arg, default=0.0)
    p.add_argument("--impago-cuotas", type=_numero_arg, default=0.0)
    p.add_argument("--reembolsos", type=_numero_arg, default=0.0)
    p.add_argument("--pasarela-pct", type=_numero_arg, default=None,
                   help="comisión de pasarela o financiera sobre el cobro; por defecto 0 (transferencia) o 0.03 con "
                        "`stripe: true` en la ficha")
    p.add_argument("--entrega-pct", type=_numero_arg, default=0.0)
    p.add_argument("--closer-pct", type=_numero_arg, default=0.0)
    p.add_argument("--setter-pct", type=_numero_arg, default=0.0)
    p.add_argument("--coste-fijo", type=_numero_arg, default=0.0)


def _parser() -> argparse.ArgumentParser:
    comun = argparse.ArgumentParser(add_help=False)
    comun.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    comun.add_argument("--cliente", default=argparse.SUPPRESS, help="slug: toma la moneda y el tipo de la ficha")
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", default=False)
    ap.add_argument("--cliente", default=None)
    sub = ap.add_subparsers(dest="modo", required=True, parser_class=_Parser)

    e = sub.add_parser("ecommerce", parents=[comun], help="CPA/ROAS break-even y target por pedido")
    e.add_argument("--aov", type=_numero_arg, required=True, help="ticket medio")
    e.add_argument("--aov-sin-iva", dest="aov_incluye_iva", action="store_false",
                   help="indica que --aov ya está sin IVA (por defecto se asume que lo incluye)")
    e.add_argument("--iva", type=_numero_arg, default=None, help="por defecto 0.21 (B2C con IVA español incluido)")
    e.add_argument("--cogs-pct", type=_numero_arg, default=0.30, help="coste de producto sobre AOV neto")
    e.add_argument("--cogs-eur", type=_numero_arg, default=None, help="coste de producto por pedido (sustituye a --cogs-pct)")
    e.add_argument("--envio", type=_numero_arg, default=0.0, help="coste de envío por pedido para el negocio")
    e.add_argument("--pasarela-pct", type=_numero_arg, default=None, help="por defecto 0.02 (pago con tarjeta)")
    e.add_argument("--devoluciones-pct", type=_numero_arg, default=0.0)
    e.add_argument("--otros-pct", type=_numero_arg, default=0.0, help="packaging, fulfilment, apps… sobre AOV neto")
    e.add_argument("--fee-pais", type=_numero_arg, default=None,
                   help="location fee: ES/FR/IT 0.03, UK 0.02, AT/TR 0.05; por defecto, el de `mercados` (--cliente) o 0")
    e.add_argument("--valor-meta", choices=["con_iva", "sin_iva"], default="con_iva",
                   help="cómo envía tu tienda el valor de compra a Meta")
    e.add_argument("--margen-objetivo", type=_numero_arg, default=0.30)
    e.add_argument("--pedidos-ltv", type=_numero_arg, default=None)
    e.add_argument("--incrementalidad", type=_numero_arg, default=None, help="factor medido, p. ej. 0.7")
    e.add_argument("--cpa", type=_numero_arg, default=None, help="CPA actual para comprobar rentabilidad")

    l = sub.add_parser("leadgen", parents=[comun], help="CPL / coste por cita / show / venta break-even")
    _args_oferta(l, precio_obligatorio=True)
    l.add_argument("--cualif", type=_numero_arg, default=1.0, help="lead → cualificado")
    l.add_argument("--agenda", type=_numero_arg, default=1.0, help="cualificado → cita agendada")
    l.add_argument("--show", type=_numero_arg, default=1.0)
    l.add_argument("--cierre", type=_numero_arg, default=1.0)
    l.add_argument("--margen-objetivo", type=_numero_arg, default=0.5)
    l.add_argument("--fee-pais", type=_numero_arg, default=None,
                   help="location fee: ES/FR/IT 0.03, UK 0.02, AT/TR 0.05 (se cobra encima del gasto); por defecto, el "
                        "de `mercados` (--cliente) o 0")
    l.add_argument("--inversion", type=_numero_arg, default=None)
    l.add_argument("--cpl", type=_numero_arg, default=None)

    s = sub.add_parser("suscripcion", parents=[comun], help="CAC máximo por prueba/alta según churn y payback")
    s.add_argument("--precio-mes", type=_numero_arg, required=True)
    s.add_argument("--iva", type=_numero_arg, default=None, help="por defecto 0.21 (B2C con IVA español incluido)")
    s.add_argument("--margen", type=_numero_arg, default=0.8)
    s.add_argument("--churn", type=_numero_arg, required=True, help="churn mensual, p. ej. 0.10")
    s.add_argument("--trial-a-pago", type=_numero_arg, default=1.0)
    s.add_argument("--payback-meses", type=int, default=6)
    s.add_argument("--fee-pais", type=_numero_arg, default=None, help="por defecto, el de `mercados` (--cliente) o 0")

    p = sub.add_parser("prevision", parents=[comun], help="escenarios de inversión con bandas")
    p.add_argument("--modelo", choices=["servicios", "saas", "ecommerce"], default=None,
                   help="por defecto, según el tipo de la ficha (--cliente) o servicios")
    p.add_argument("--inversion", required=True, help="importes separados por comas: 3000,6000,12000")
    p.add_argument("--inversion-ref", help="inversión a la que se observó el coste por lead (por defecto, la menor)")
    p.add_argument("--cpl", help="coste por lead o por registro: número o rango «30-45»")
    p.add_argument("--cpa", help="e-commerce: coste por pedido, número o rango")
    p.add_argument("--curva", help="exponente b de la curva de respuesta (rango); por defecto 0.6-0.8 de la KB")
    p.add_argument("--fee-pais", type=_numero_arg, default=None, help="por defecto, el de `mercados` (--cliente) o 0")
    p.add_argument("--cualif", default="1", help="servicios: lead → cualificado (rango)")
    p.add_argument("--agenda", default="1", help="servicios: cualificado → cita (rango)")
    p.add_argument("--show", default="1", help="servicios: cita → show (rango)")
    p.add_argument("--cierre", help="servicios: show → venta (rango)")
    p.add_argument("--contribucion-venta", type=_numero_arg, help="servicios: contribución por venta (si no, se calcula "
                                                            "con --precio y los datos de la oferta)")
    _args_oferta(p, precio_obligatorio=False)
    p.add_argument("--activacion", help="SaaS: registro → activado (rango)")
    p.add_argument("--pago", help="SaaS: activado → cliente de pago (rango)")
    p.add_argument("--precio-mes", type=_numero_arg, help="SaaS: precio mensual")
    p.add_argument("--margen", type=_numero_arg, default=0.8, help="SaaS: margen bruto [HYPOTHESIS]")
    p.add_argument("--churn", type=_numero_arg, help="SaaS: churn mensual")
    p.add_argument("--contribucion-pedido", type=_numero_arg, help="e-commerce: contribución por pedido (CM1)")
    return ap


_TASAS = ("iva", "pct_pago_unico", "descuento_pago_unico", "recargo_cuotas", "impago_cuotas", "reembolsos",
          "pasarela_pct", "entrega_pct", "closer_pct", "setter_pct", "cualif", "agenda", "show", "cierre",
          "margen_objetivo", "cogs_pct", "devoluciones_pct", "otros_pct", "fee_pais", "margen", "trial_a_pago",
          "incrementalidad")


def _validar(a) -> None:
    for t in _TASAS:
        v = getattr(a, t, None)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and not 0 <= v <= 1:
            raise ErrorUsuario(f"--{t.replace('_', '-')} es una proporción entre 0 y 1 (usa 0.25 para un 25 %)")
    churn = getattr(a, "churn", None)
    if churn is not None and not 0 < churn < 1:
        raise ErrorUsuario("--churn es mensual y va entre 0 y 1 (0.05 = 5 % al mes)")
    for t in ("aov", "precio", "precio_mes", "cpl", "inversion"):
        v = getattr(a, t, None)
        if isinstance(v, (int, float)) and v <= 0:
            raise ErrorUsuario(f"--{t.replace('_', '-')} debe ser mayor que 0")
    if a.modo == "prevision":
        if a.modelo == "servicios" and not a.cierre:
            raise ErrorUsuario("prevision servicios necesita --cierre (show → venta)")
        if a.modelo == "saas" and not (a.activacion and a.pago):
            raise ErrorUsuario("prevision saas necesita --activacion y --pago")
        if a.modelo == "ecommerce" and not a.cpa:
            raise ErrorUsuario("prevision ecommerce necesita --cpa")
        if a.modelo != "ecommerce" and not a.cpl:
            raise ErrorUsuario("prevision necesita --cpl (coste por lead o registro)")


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    a = _parser().parse_args(argv)
    a.iva_por_defecto = a.iva is None
    if a.iva is None:
        a.iva = 0.21 if a.modo in ("ecommerce", "suscripcion") else 0.0
    moneda = "€"
    ficha = None
    try:
        if a.cliente:
            ficha = _comun.leer_ficha(a.cliente)
            moneda = SIMBOLO.get(str(ficha.get("moneda", "EUR")).upper(), str(ficha.get("moneda", "")))
            if a.modo == "prevision" and not a.modelo:
                tipo = str(ficha.get("tipo", "")).lower()
                a.modelo = "saas" if tipo in ("saas", "app") else ("ecommerce" if tipo == "ecommerce" else "servicios")
        if a.modo == "prevision" and not a.modelo:
            a.modelo = "servicios"
        resolver_supuestos(a, ficha)
        _validar(a)
        fn = {"ecommerce": ecommerce, "leadgen": leadgen, "suscripcion": suscripcion, "prevision": prevision}[a.modo]
        res = fn(a)
    except ErrorUsuario as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except _comun.FichaInvalida as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif a.modo == "prevision":
        _texto_prevision(res, moneda)
    else:
        _salida_texto(res, f"{a.modo} (importes en {moneda})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
