#!/usr/bin/env python3
"""Estadística práctica para media buying (Poisson): ¿es señal o ruido?

Subcomandos:
  ic-cpa     --gasto 3000 --conversiones 30          IC 95 % del CPA real
  kill       --cpa-objetivo 40 --gasto 100           P(0 o ≤1 conversiones) si el anuncio fuera bueno (falsos negativos)
  comparar   --gasto-a 500 --conv-a 12 --gasto-b 500 --conv-b 20   ¿A y B difieren de verdad?
  potencia   --diferencia 0.2 [--potencia 0.8]       conversiones por brazo para detectar una diferencia de CPA
  detectable --conversiones 50                       diferencia mínima detectable con n conversiones por brazo
  banda      --media 20 [--observado 9]              rango normal diario (95 %) de un evento con esa media y, si das el
                                                     valor de hoy, si cae fuera (lo usa el brief diario)
  lag        --conv-1d 80 --conv-7d 100 [--cpa-1d 50]   ratio de maduración y CPA estimado de días recientes
  identicos  --conversiones 10 [--umbral 0.3]        prob. de que dos anuncios IDÉNTICOS difieran ≥ umbral en CPA
Todos admiten --json.

Base: meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md y
meta-ads-kb/03-creatividad/05-testing-creativo.md
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from statistics import NormalDist

Z = NormalDist()


class ErrorUsuario(Exception):
    pass


# ---------------------------------------------------------------- Poisson
def _logpmf(k: int, lam: float) -> float:
    if lam <= 0:
        return 0.0 if k == 0 else -math.inf
    return -lam + k * math.log(lam) - math.lgamma(k + 1)


def pmf(k: int, lam: float) -> float:
    return math.exp(_logpmf(k, lam))


def cdf(k: float, lam: float) -> float:
    """P(X ≤ k) con X ~ Poisson(lam); cada término se calcula en logaritmos para no desbordar."""
    k = int(math.floor(k))
    if k < 0:
        return 0.0
    if lam <= 0:
        return 1.0
    return min(1.0, sum(pmf(i, lam) for i in range(k + 1)))


def cuantil(lam: float, q: float) -> int:
    """El menor k con P(X ≤ k) ≥ q."""
    if lam <= 0:
        return 0
    acumulado, k = 0.0, 0
    tope = int(lam + 20 * math.sqrt(lam) + 50)
    while k <= tope:
        acumulado += pmf(k, lam)
        if acumulado >= q:
            return k
        k += 1
    return tope


def _bisect(f, lo: float, hi: float, it: int = 200) -> float:
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def ic_poisson(k: int, alfa: float = 0.05) -> tuple[float, float]:
    """IC exacto (Garwood) para la media de una Poisson con k eventos observados.

    Con k > 500 usa la aproximación de Wilson-Hilferty (error < 0,1 %) para no tardar segundos.
    """
    if k > 500:
        z = Z.inv_cdf(1 - alfa / 2)
        lower = k * (1 - 1 / (9 * k) - z / (3 * math.sqrt(k))) ** 3
        upper = (k + 1) * (1 - 1 / (9 * (k + 1)) + z / (3 * math.sqrt(k + 1))) ** 3
        return lower, upper
    hi_lim = max(10.0, k * 5 + 20)
    lower = 0.0 if k == 0 else _bisect(lambda l: 1 if (1 - cdf(k - 1, l)) < alfa / 2 else -1, 0.0, hi_lim)
    upper = _bisect(lambda l: cdf(k, l) - alfa / 2, 0.0, hi_lim)
    return lower, upper


# ---------------------------------------------------------------- comandos (devuelven datos y texto)
def ic_cpa(gasto: float, conversiones: int) -> tuple[dict, list[str]]:
    k = conversiones
    lo, hi = ic_poisson(k)
    cpa = gasto / k if k else None
    cpa_lo = gasto / hi
    cpa_hi = gasto / lo if lo > 0 else None
    d = {"gasto": gasto, "conversiones": k, "cpa": cpa, "ic95_cpa": [cpa_lo, cpa_hi], "ruidoso": k < 30}
    if k == 0:
        t = [f"0 conversiones con {gasto:,.2f} de gasto: con un 95 % de confianza el CPA real es ≥ {cpa_lo:,.2f}."]
    else:
        t = [f"CPA observado: {cpa:,.2f}  (gasto {gasto:,.2f}, {k} conversiones)",
             f"IC 95 % del CPA real: {cpa_lo:,.2f} – {cpa_hi:,.2f}  ({cpa_lo / cpa:.2f}× a {cpa_hi / cpa:.2f}× "
             "el observado)"]
    if k < 30:
        t.append("Aviso: con <30 conversiones el CPA es muy ruidoso; decide con más datos o con métricas de mayor "
                 "volumen.")
    return d, t


def kill(cpa_objetivo: float, gasto: float) -> tuple[dict, list[str]]:
    lam = gasto / cpa_objetivo
    p0, p1 = math.exp(-lam), cdf(1, lam)
    d = {"veces_cpa": lam, "p_cero": p0, "p_max_una": p1}
    t = [f"Gasto = {lam:.2f}× el CPA objetivo.",
         "Si el anuncio fuera exactamente tan bueno como el objetivo:",
         f"  P(0 conversiones) = {p0:.1%}   → matar con 0 conversiones ahora descarta este % de anuncios válidos",
         f"  P(≤1 conversión)  = {p1:.1%}",
         "Regla del sistema: matar por 0 conversiones a partir de 2–3× CPA (13,5 %–5 % de falsos negativos)."]
    return d, t


def comparar(gasto_a: float, conv_a: int, gasto_b: float, conv_b: int) -> tuple[dict, list[str]]:
    ka, kb = conv_a, conv_b
    n = ka + kb
    if n == 0:
        return {"p_valor": None, "veredicto": "sin datos"}, ["Sin conversiones en ninguno de los dos."]
    p = gasto_a / (gasto_a + gasto_b)
    # test binomial condicional exacto, bilateral, en logaritmos (con miles de conversiones comb() desborda un float)
    logp = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p)
            + (n - i) * math.log(1 - p) for i in range(n + 1)]
    lobs = logp[ka]
    pval = min(1.0, sum(math.exp(x) for x in logp if x <= lobs + 1e-9))
    cpa_a = gasto_a / ka if ka else None
    cpa_b = gasto_b / kb if kb else None
    d = {"cpa_a": cpa_a, "cpa_b": cpa_b, "p_valor": pval, "real": pval < 0.05}
    fa = f"{cpa_a:,.2f}" if cpa_a else "∞"
    fb = f"{cpa_b:,.2f}" if cpa_b else "∞"
    t = [f"A: CPA {fa} ({ka} conv) · B: CPA {fb} ({kb} conv)"]
    if ka and kb:
        rr = (ka / gasto_a) / (kb / gasto_b)
        se = math.sqrt(1 / ka + 1 / kb)
        lo, hi = math.exp(math.log(rr) - 1.96 * se), math.exp(math.log(rr) + 1.96 * se)
        d["ratio_tasas"] = rr
        d["ic95_ratio"] = [lo, hi]
        t.append(f"Ratio de tasas de conversión A/B: {rr:.2f} (IC 95 % {lo:.2f}–{hi:.2f})")
    d["veredicto"] = "diferencia probablemente real" if pval < 0.05 else "no distinguible del ruido"
    t += [f"p-valor (binomial condicional, bilateral): {pval:.3f}",
          "Veredicto: " + ("diferencia probablemente real (p<0,05)" if pval < 0.05
                           else "NO distinguible del ruido con estos datos")]
    return d, t


def n_por_brazo(d: float, alfa: float = 0.05, potencia: float = 0.8) -> float:
    za, zb = Z.inv_cdf(1 - alfa / 2), Z.inv_cdf(potencia)
    return 2 * (za + zb) ** 2 / math.log(1 + d) ** 2


def potencia(diferencia: float, pot: float) -> tuple[dict, list[str]]:
    n = math.ceil(n_por_brazo(diferencia, potencia=pot))
    tabla = {f"{x:.0%}": math.ceil(n_por_brazo(x, potencia=pot)) for x in (0.1, 0.2, 0.3, 0.5, 1.0, 2.0)}
    t = [f"Para detectar una diferencia de CPA del {diferencia:.0%} (α=0,05, potencia {pot:.0%}):",
         f"  ≈ {n} conversiones por brazo", "Tabla de referencia:"]
    t += [f"  {k:>5} → {v:>6} conversiones por brazo" for k, v in tabla.items()]
    return {"diferencia": diferencia, "potencia": pot, "conversiones_por_brazo": n, "tabla": tabla}, t


def detectable(conversiones: int, pot: float) -> tuple[dict, list[str]]:
    za, zb = Z.inv_cdf(0.975), Z.inv_cdf(pot)
    d = math.exp((za + zb) * math.sqrt(2 / conversiones)) - 1
    return ({"conversiones_por_brazo": conversiones, "diferencia_minima": d},
            [f"Con {conversiones} conversiones por brazo solo se detectan diferencias de CPA ≥ {d:.0%} "
             f"(potencia {pot:.0%})."])


def banda(media: float, observado: float | None = None) -> tuple[dict, list[str]]:
    lo, hi = cuantil(media, 0.025), cuantil(media, 0.975)
    d = {"media": media, "bajo": lo, "alto": hi}
    t = [f"Con una media de {media:g} eventos/día, el 95 % de los días cae entre {lo} y {hi} sin que nada haya "
         "cambiado."]
    if observado is not None:
        if observado < lo:
            estado, p = "por debajo", cdf(observado, media)
        elif observado > hi:
            estado, p = "por encima", 1 - cdf(observado - 1, media)
        else:
            estado, p = "dentro", None
        d.update(observado=observado, estado=estado, p_cola=p)
        t.append(f"Hoy: {observado:g} → {estado} de la banda"
                 + (f" (probabilidad de un valor así o más extremo: {p:.1%}): revisa la causa" if p is not None
                    else ": ruido normal, no toques nada por esto"))
    return d, t


def lag(conv_1d: float, conv_7d: float, cpa_1d: float | None) -> tuple[dict, list[str]]:
    r = conv_7d / conv_1d
    d = {"ratio_maduracion": r}
    t = [f"Ratio de maduración (7d click / 1d click): {r:.2f}"]
    if cpa_1d:
        d["cpa_estimado"] = cpa_1d / r
        t.append(f"CPA estimado de días recientes tras madurar: {cpa_1d / r:,.2f} (desde CPA 1d click {cpa_1d:,.2f})")
    return d, t


def identicos(conversiones: float, umbral: float) -> tuple[dict, list[str]]:
    """Cálculo exacto (suma sobre la distribución conjunta) en lugar de simulación."""
    lam = conversiones
    lo = max(0, int(lam - 8 * math.sqrt(lam) - 5))
    hi = int(lam + 8 * math.sqrt(lam) + 10)
    pm = {k: pmf(k, lam) for k in range(lo, hi + 1)}
    cubierto = sum(pm.values())
    p = (1 - cubierto) * 2  # masa fuera del rango (despreciable): se cuenta como diferencia
    for x, px in pm.items():
        for y, py in pm.items():
            if x == 0 or y == 0 or abs(x / y - 1) >= umbral or abs(y / x - 1) >= umbral:
                p += px * py
    p = min(1.0, p)
    return ({"conversiones_esperadas": lam, "umbral": umbral, "probabilidad": p},
            [f"Dos anuncios IDÉNTICOS con {lam:g} conversiones esperadas difieren ≥{umbral:.0%} en CPA el {p:.0%} "
             "de las veces."])


# ---------------------------------------------------------------- CLI
class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def _parser() -> argparse.ArgumentParser:
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True, parser_class=_Parser)

    def sub(nombre):
        p = s.add_parser(nombre)
        p.add_argument("--json", action="store_true")
        return p

    p = sub("ic-cpa"); p.add_argument("--gasto", type=float, required=True); p.add_argument("--conversiones", type=int, required=True)
    p = sub("kill"); p.add_argument("--cpa-objetivo", type=float, required=True); p.add_argument("--gasto", type=float, required=True)
    p = sub("comparar")
    for x in ("gasto-a", "gasto-b"):
        p.add_argument(f"--{x}", type=float, required=True)
    for x in ("conv-a", "conv-b"):
        p.add_argument(f"--{x}", type=int, required=True)
    p = sub("potencia"); p.add_argument("--diferencia", type=float, required=True); p.add_argument("--potencia", type=float, default=0.8)
    p = sub("detectable"); p.add_argument("--conversiones", type=int, required=True); p.add_argument("--potencia", type=float, default=0.8)
    p = sub("banda"); p.add_argument("--media", type=float, required=True); p.add_argument("--observado", type=float)
    p = sub("lag"); p.add_argument("--conv-1d", type=float, required=True); p.add_argument("--conv-7d", type=float, required=True); p.add_argument("--cpa-1d", type=float)
    p = sub("identicos"); p.add_argument("--conversiones", type=float, required=True); p.add_argument("--umbral", type=float, default=0.3)
    return ap


def _validar(a) -> None:
    def pos(nombre, v, cero=False):
        if v is not None and (v < 0 or (v == 0 and not cero)):
            raise ErrorUsuario(f"--{nombre} debe ser {'≥ 0' if cero else '> 0'}")
    if a.cmd in ("ic-cpa",):
        pos("gasto", a.gasto); pos("conversiones", a.conversiones, cero=True)
    elif a.cmd == "kill":
        pos("cpa-objetivo", a.cpa_objetivo); pos("gasto", a.gasto)
    elif a.cmd == "comparar":
        pos("gasto-a", a.gasto_a); pos("gasto-b", a.gasto_b)
        pos("conv-a", a.conv_a, cero=True); pos("conv-b", a.conv_b, cero=True)
    elif a.cmd in ("potencia", "detectable"):
        if not 0 < a.potencia < 1:
            raise ErrorUsuario("--potencia va entre 0 y 1 (0.8 = 80 %)")
        if a.cmd == "potencia":
            pos("diferencia", a.diferencia)
        else:
            pos("conversiones", a.conversiones)
    elif a.cmd == "banda":
        pos("media", a.media)
        pos("observado", a.observado, cero=True)
        if a.media > 1e6:
            raise ErrorUsuario("--media demasiado grande para una banda diaria")
    elif a.cmd == "lag":
        pos("conv-1d", a.conv_1d); pos("conv-7d", a.conv_7d); pos("cpa-1d", a.cpa_1d)
    elif a.cmd == "identicos":
        pos("conversiones", a.conversiones)
        pos("umbral", a.umbral)
        if a.conversiones > 20000:
            raise ErrorUsuario("--conversiones demasiado grande: con tanto volumen dos anuncios idénticos no difieren")


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    a = _parser().parse_args(argv)
    try:
        _validar(a)
        d, t = {
            "ic-cpa": lambda: ic_cpa(a.gasto, a.conversiones),
            "kill": lambda: kill(a.cpa_objetivo, a.gasto),
            "comparar": lambda: comparar(a.gasto_a, a.conv_a, a.gasto_b, a.conv_b),
            "potencia": lambda: potencia(a.diferencia, a.potencia),
            "detectable": lambda: detectable(a.conversiones, a.potencia),
            "banda": lambda: banda(a.media, a.observado),
            "lag": lambda: lag(a.conv_1d, a.conv_7d, a.cpa_1d),
            "identicos": lambda: identicos(a.conversiones, a.umbral),
        }[a.cmd]()
    except ErrorUsuario as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(d, ensure_ascii=False, indent=2) if a.json else "\n".join(t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
