#!/usr/bin/env python3
"""Inteligencia creativa: qué ELEMENTOS de los anuncios se asocian a ganar, no solo qué anuncio gana.

El registro creativo (`registro_creativo.py`) dice qué anuncio gana y con qué capa de verdad. Esta herramienta añade lo
que hay dentro de cada anuncio (quién habla, primer fotograma, texto inicial, duración, ritmo, demo, prueba, cifra,
si dice «IA», si filtra, CTA, subtítulos…) con un esquema fijo de etiquetas (`etiquetas esquema`) en
clientes/<S>/datos/elementos-creativos.csv, lo cruza con el registro, lee la retención del vídeo, detecta conceptos casi
iguales y calcula cuántos conceptos nuevos producir. Solo escribe archivos locales. Solo lee de Meta (y solo con
`fotogramas --api`).

Uso (`python3 -I herramientas/elementos_creativos.py <subcomando> …`, todos con `--json`):
  fotogramas --cliente S [--ad ID …] [--video RUTA] [--api] [--descargar-video] [--cuadricula] [--max 30]
      Fotogramas clave para que un agente los mire: primer fotograma (f0.jpg), arranque 0–3 s a 4 fps
      (arranque.jpg), hoja del vídeo entero (hoja.jpg) e indice.json (duración, aspecto, cortes, ritmo sugerido y
      huella visual) en clientes/<S>/creativos/_fotogramas/<ad_id>/. Fuente: la pieza local de `ruta_creativo` (o
      creativos/<nombre-base>/), un `--video` dado o, con `--api`, la miniatura y la duración desde Meta (con
      `--descargar-video`, el vídeo entero, que se borra al terminar). `--cuadricula` monta la «prueba de la
      cuadrícula» (meta-ads-kb/03-creatividad/01-creative-es-targeting.md, implicaciones operativas). Rellena los
      campos automáticos de datos/elementos-creativos.csv. FFmpeg es opcional: sin él solo hay miniaturas de la API.
  etiquetas esquema                      el esquema fijo (columnas, valores y definiciones)
  etiquetas preparar --cliente S [--todos]   una fila por anuncio con gasto del registro; conserva lo etiquetado
  etiquetas pendientes --cliente S        anuncios sin etiquetar, de más a menos gasto
  etiquetas poner --cliente S (--ad ID campo=valor … | --archivo etiquetas.json) [--por QUIEN]
  etiquetas validar --cliente S           cabecera, valores y duplicados (sale con 1 si hay errores)
  analizar --cliente S [--capa C] [--madurez citas=14 ...] [--fecha AAAA-MM-DD] [--guardar]
  retencion --cliente S --meta <csv de meta_ads.py anuncios> [--min-impresiones 1000]
  diversidad --cliente S [--umbral 0.8] [--umbral-visual 10] [--todos] [--guardar]
  suministro --cliente S [--gasto-mensual X | --gasto-diario X | --meta CSV] [--coste-objetivo X] [--capa C]
             [--guardar]

`analizar` — tres lecturas, ninguna causal (el gasto no se reparte al azar:
meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md §8.3):
  1. Coste en la capa de decisión: la capa más cercana al dinero (CAPAS de registro_creativo.py) con ≥20 eventos en
     anuncios maduros. Por cada valor de cada elemento, coste por evento con el valor frente al resto, razón de costes
     con IC 95 % (Poisson con sobredispersión estimada entre anuncios, cuasi-Poisson) y q de Benjamini-Hochberg
     (§8.2 del mismo archivo). «n insuficiente» si un lado tiene <10 eventos (N_DECIDIR de la KB 13/05 §5) o <2
     anuncios; «confundido» si el valor solo aparece en un concepto (no se separa del concepto).
  2. Ganadores frente a perdedores (veredicto del registro): proporción de ganadores y de perdedores con el valor,
     diferencia con IC de Newcombe y p exacta de Fisher; «n insuficiente» con <3 ganadores o <3 perdedores
     etiquetados [HYPOTHESIS].
  3. Atención (diagnóstico, nunca decide): hook rate, hold rate (sin vídeos de ≤15 s) y CTR por valor, cuasi-binomial.
  Valores que van siempre en los mismos anuncios (o justo en los contrarios) se prueban una vez y se informan juntos:
  con esos datos no se pueden separar. Una etiqueta «duda» saca a ese anuncio de ese elemento.
  Síntesis: repetir (señal a favor, q<0,10, [EMPIRICAL] de esta cuenta), dejar (señal en contra) y probar (pistas,
  confundidos y huecos sin probar, [HYPOTHESIS]). Con `--guardar`:
  clientes/<S>/datos/analisis-creativo/<fecha>_elementos.json (igual `diversidad` y `suministro`).

`retencion` — hook rate, hold rate, retención por cuartiles (reproducciones hasta el XX % / vistas de 3 s), tiempo
medio y la mayor caída de la curva de los primeros 15 s, por anuncio, contra las medianas de la cuenta (árbol de
meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md §4). Diagnostica; no decide.

`diversidad` — anuncios que el sistema probablemente trata como uno
(meta-ads-kb/03-creatividad/01-creative-es-targeting.md §2: el efecto es [OFFICIAL META]; el mecanismo exacto y
cualquier umbral, [HYPOTHESIS]). Dos anuncios
son el mismo concepto si comparten ángulo y concepto en el nombre, si sus etiquetas de concepto coinciden en ≥80 %
(Gower ponderado) o si su primer fotograma es casi idéntico (dHash a ≤10 bits de 64). Da grupos, conceptos efectivos
por gasto (inverso de Simpson), concentración y dimensiones sin variedad, por cuenta y por conjunto.

`suministro` — conceptos nuevos al mes = gasto mensual × explorar_explotar ÷ (2–3 × coste objetivo del evento que se
optimiza) (meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md TL;DR y
meta-ads-kb/03-creatividad/13-produccion-y-feedback-loop-creativo.md §4.2, [STRONG INFERENCE]; `explorar_explotar`
de la ficha, [HYPOTHESIS]), con iteraciones por ganador y el techo orientativo por gasto de 13/05 §3.

Códigos de salida: 0 bien · 1 error del usuario · 2 configuración (ficha, FFmpeg, token).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from statistics import NormalDist

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402
import nomenclatura  # noqa: E402
import registro_creativo as rc  # noqa: E402

ErrorUsuario = rc.ErrorUsuario
Z = NormalDist()
Z95 = Z.inv_cdf(0.975)


class ErrorConfig(Exception):
    """Falta algo del entorno (FFmpeg, token): código de salida 2."""


# ================================================================ esquema fijo de etiquetas
ARCHIVO = "elementos-creativos.csv"
DUDA, NO_APLICA = "duda", "no-aplica"
COMODINES = (DUDA, NO_APLICA)


@dataclass(frozen=True)
class Etiqueta:
    columna: str
    valores: tuple | None          # None = número (segundos)
    aplica: str                    # todas | video
    define: str
    automatica: bool = False       # la rellena `fotogramas` (se puede corregir a mano)


ESQUEMA: tuple[Etiqueta, ...] = (
    Etiqueta("soporte", ("video", "imagen", "carrusel"), "todas",
             "Qué es la pieza. Sale sola del formato del nombre o de los fotogramas.", True),
    Etiqueta("relacion_aspecto", ("9x16", "4x5", "1x1", "16x9", "otro"), "todas",
             "Relación de aspecto del archivo analizado (automática con FFmpeg).", True),
    Etiqueta("duracion_s", None, "video", "Duración en segundos (automática con FFmpeg o con la API).", True),
    Etiqueta("ritmo", ("lento", "medio", "rapido"), "video",
             "Duración media de plano: rápido < 2,5 s; medio 2,5–6 s; lento > 6 s o plano único. `fotogramas` "
             "sugiere un valor contando cortes: confírmalo con la hoja (los cortes de salto en un plano fijo a cámara "
             "a veces no se detectan)."),
    Etiqueta("persona", ("ninguna", "real", "ia"), "todas",
             "¿Aparece una persona? real = filmada o fotografiada; ia = generada con IA (presentador sintético, "
             "avatar, foto generada)."),
    Etiqueta("quien_habla", ("nadie", "fundador", "equipo", "cliente", "creador", "experto", "voz-en-off",
                             "avatar-ia"), "todas",
             "Quién lleva el mensaje: a cámara, con su voz o firmando la cita del estático. voz-en-off = narrador que "
             "no sale; nadie = solo texto o música; cliente = el cliente final del anunciante."),
    Etiqueta("primer_fotograma", ("cara", "pantalla", "texto", "dato", "antes-despues", "escena", "marca", "meme"),
             "todas",
             "Qué domina el primer fotograma (o la imagen, o la primera tarjeta): cara = persona a cámara o primer "
             "plano; pantalla = interfaz, flujo, chat o automatización; texto = titular sin cifra protagonista; dato = "
             "cifra o gráfico protagonista; antes-despues = pantalla partida o comparación; escena = alguien "
             "trabajando en su contexto sin mirar a cámara; marca = logo o pieza de marca; meme = formato meme."),
    Etiqueta("texto_0s", ("no", "si"), "todas",
             "¿Hay texto legible en pantalla desde el primer fotograma? En estáticos y carruseles, texto en la imagen."),
    Etiqueta("gancho", ("problema", "resultado", "pregunta", "contraintuitivo", "historia", "llamada-audiencia",
                        "demo", "prueba", "oferta"), "todas",
             "Mecanismo de los 3 primeros segundos (o del titular de la imagen): problema = nombra un dolor; "
             "resultado = promete o enseña un resultado; pregunta; contraintuitivo = rompe una creencia del nicho; "
             "historia = empieza un relato; llamada-audiencia = el gancho ES nombrar a quién va («Si tienes una "
             "clínica…»); demo = arranca enseñando el sistema; prueba = arranca con un caso o testimonio; oferta = "
             "arranca con lo que se ofrece."),
    Etiqueta("audiencia_nombrada", ("no", "sector", "rol", "ambos"), "todas",
             "¿Nombra a quién va dirigido en los 3 primeros segundos o en el titular? sector = «clínicas dentales», "
             "«gestorías»; rol = «gerentes», «dueños de agencia»; ambos."),
    Etiqueta("consciencia", ("inconsciente", "problema", "solucion", "producto", "total"), "todas",
             "Nivel de consciencia al que habla "
             "(meta-ads-kb/03-creatividad/03-estrategia-creativa-primeros-principios.md §3): inconsciente = no sabe que tiene el problema; problema = lo sabe y no conoce "
             "soluciones; solucion = compara soluciones; producto = conoce la tuya; total = solo le falta la oferta."),
    Etiqueta("estructura", ("caso", "demo", "antes-despues", "testimonio", "dato", "lista", "explicacion",
                            "comparativa", "opinion", "oferta", "detras-de-camaras"), "todas",
             "La idea que sostiene la pieza: caso = alguien cuenta un caso con cifras; demo = el sistema funcionando; "
             "antes-despues de un proceso; testimonio del cliente; dato = un dato protagonista (típico del estático); "
             "lista = «5 procesos que…»; explicacion = mecanismo o educativo; comparativa con la forma actual o con "
             "otra solución; opinion = tesis o crítica del nicho; oferta = directo a la oferta; detras-de-camaras."),
    Etiqueta("demo", ("no", "breve", "central"), "todas",
             "¿Se ve el sistema funcionando (pantalla real, flujo, resultado generado)? breve = menos de una cuarta "
             "parte de la pieza; central = es el núcleo."),
    Etiqueta("cifra", ("no", "gancho", "cuerpo"), "todas",
             "¿Hay una cifra concreta (horas, %, €, citas, días)? gancho = en los 3 primeros segundos o en el "
             "titular; cuerpo = después."),
    Etiqueta("menciona_ia", ("no", "gancho", "cuerpo"), "todas",
             "¿Dice «IA», «inteligencia artificial», «agente», «ChatGPT» o un nombre de modelo? gancho = en los 3 "
             "primeros segundos o en el titular; cuerpo = después. El playbook de consultoras propone probar no decir "
             "«IA» al principio (meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md §8.1)."),
    Etiqueta("filtro", ("no", "si"), "todas",
             "¿Filtra de forma explícita: para quién no es, tamaño mínimo, rango de precio o requisito («si facturas "
             "menos de…, no es para ti»)? Es el «callout» que descualifica "
             "(meta-ads-kb/03-creatividad/01-creative-es-targeting.md §4.3)."),
    Etiqueta("prueba_social", ("ninguna", "resultado-cliente", "testimonio", "logos", "volumen", "resenas", "medios"),
             "todas",
             "La prueba más fuerte que se ve (solo una): resultado-cliente = cifra de un cliente; testimonio = el "
             "cliente lo cuenta; logos de clientes; volumen = «+40 empresas»; resenas = estrellas o capturas; medios = "
             "apariciones en prensa o premios."),
    Etiqueta("cta", ("diagnostico", "auditoria", "llamada", "demo", "recurso", "prueba-gratis", "presupuesto",
                     "mensaje", "ninguno"), "todas",
             "El siguiente paso que pide la pieza (no el botón de Meta): diagnostico o calculadora; auditoria; llamada "
             "o reunión; demo; recurso descargable; prueba-gratis (SaaS); presupuesto; mensaje (WhatsApp, Messenger, "
             "DM); ninguno."),
    Etiqueta("subtitulos", ("no", "completos", "clave"), "video",
             "Subtítulos quemados: completos = todo lo hablado; clave = solo palabras clave; no."),
    Etiqueta("acabado", ("casero", "pulido", "plantilla"), "todas",
             "casero = móvil, nativo, sin grafismo; pulido = producción o edición cuidada; plantilla = diseño gráfico "
             "o plantilla de estático."),
    Etiqueta("tono", ("didactico", "cercano", "provocador", "humor", "inspirador"), "todas", "Tono dominante."),
)
POR_COLUMNA = {e.columna: e for e in ESQUEMA}
ETIQUETAS = [e.columna for e in ESQUEMA]
MANUALES = [e.columna for e in ESQUEMA if not e.automatica]
COLUMNAS = (["ad_id", "nombre"] + ETIQUETAS
            + ["huella_visual", "fuente_visual", "etiquetado_por", "fecha_etiquetado", "notas"])
EDITABLES = set(ETIQUETAS) | {"notas"}
CRITERIO_DUDA = ("Etiqueta a ciegas (sin mirar gasto ni resultados) y solo lo que se ve u oye en la pieza. Si dudas "
                 "entre dos valores o no se ve en los fotogramas, escribe «duda»: esa pieza no cuenta para ese "
                 "elemento. Mejor un hueco que una etiqueta inventada. «no-aplica» solo en elementos de vídeo de un "
                 "estático o carrusel.")
NEGATIVOS = {"no", "ninguna", "ninguno", "nadie"}

# Elementos que pesan en «¿es otro concepto?» (dimensiones de meta-ads-kb/03-creatividad/01-creative-es-targeting.md
# §4.1: persona, problema, consciencia, portavoz, formato, tono). Pesos [HYPOTHESIS].
PESOS_CONCEPTO = {"angulo": 3.0, "estructura": 2.0, "quien_habla": 1.5, "consciencia": 1.5,
                  "audiencia_nombrada": 1.0, "soporte": 1.0, "primer_fotograma": 1.0, "persona": 0.5, "tono": 0.5}
PESO_MINIMO = 5.0           # peso conocido mínimo para comparar dos anuncios por etiquetas [HYPOTHESIS]
UMBRAL_CONCEPTO = 0.8       # similitud de Gower a partir de la cual dos anuncios son el mismo concepto [HYPOTHESIS]
UMBRAL_VISUAL = 10          # bits distintos de 64 en el dHash del primer fotograma [HYPOTHESIS]

# Huecos típicos del público (consultoras, agencias de IA y SaaS): formatos del playbook de consultoras de IA §8.2
# (fundador, demo, antes-después, caso con cifras, testimonio de quien lo usa, estático, carrusel) y principios §8.1
# (prueba antes que promesa, el anuncio filtra, no decir «IA» al principio). [HYPOTHESIS] en esta cuenta.
HUECOS_CLAVE = {"quien_habla": ("fundador", "cliente"), "estructura": ("caso", "demo", "antes-despues", "testimonio"),
                "demo": ("central",), "cifra": ("gancho",), "prueba_social": ("resultado-cliente", "testimonio"),
                "primer_fotograma": ("cara", "pantalla", "dato"), "soporte": ("video", "imagen", "carrusel"),
                "persona": ("real",), "menciona_ia": ("no",), "filtro": ("si",)}
FUENTE_HUECOS = ("meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md §8.1–8.2 y "
                 "meta-ads-kb/14-playbooks/playbook-b2b.md §5")

MIN_ANUNCIOS_LADO = 2       # anuncios por lado para comparar costes [HYPOTHESIS]
MIN_VEREDICTOS = 3          # ganadores y perdedores etiquetados para comparar proporciones [HYPOTHESIS]
Q_SENAL = 0.10              # q de Benjamini-Hochberg para llamar «señal» [HYPOTHESIS]
MIN_IMPRESIONES = 2000      # filtro de atención por lado (KB 13/05 §2: 1.000–2.000 impresiones por variante)
MIN_VISTAS_HOLD = 500       # vistas de 3 s por lado para comparar hold rate [HYPOTHESIS]
TRAMOS = (("hasta-15", 15), ("16-30", 30), ("31-60", 60), ("mas-60", math.inf))
EXT_VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
EXT_IMAGEN = {".png", ".jpg", ".jpeg", ".webp"}
ORDEN_ASPECTO = ("9x16", "4x5", "1x1")


# ================================================================ utilidades
def _hoy(fecha: str | None) -> date:
    return date.fromisoformat(fecha) if fecha else date.today()


def _rel(ruta: pathlib.Path) -> str:
    try:
        return ruta.resolve().relative_to(_comun.RAIZ.resolve()).as_posix()
    except ValueError:
        return ruta.name


def normalizar_valor(valor: str) -> str:
    """«Voz en off» → voz-en-off · «Rápido» → rapido · «sí» → si."""
    t = "".join(c for c in unicodedata.normalize("NFKD", str(valor)) if not unicodedata.combining(c))
    t = re.sub(r"[\s_]+", "-", t.strip().lower())
    return t.replace(",", ".") if re.fullmatch(r"\d+,\d+", t) else t


def _num(v) -> float | None:
    return rc._f(v)


def _fmt(v, dec: int = 2) -> str:
    return rc._fmt(v, dec)


def _euros(v: float | None) -> str:
    return "—" if v is None else rc._euros(v)


def _x(v: float | None, dec: int = 2) -> str:
    return "—" if v is None else f"{v:.{dec}f}".replace(".", ",")


def _pct(v: float | None, dec: int = 1) -> str:
    return "—" if v is None else f"{v * 100:.{dec}f} %".replace(".", ",")


def nombre_base(nombre: str) -> str | None:
    p = nomenclatura.parsear_anuncio(nombre or "")
    if not p:
        return None
    return f"{p['fecha']:%Y%m%d}_{p['angulo']}_{p['concepto']}_{p['formato']}"


def tramo_duracion(segundos: float | None) -> str | None:
    if segundos is None:
        return None
    return next(t for t, tope in TRAMOS if segundos <= tope)


# ================================================================ estadística (pura, probada en los tests)
def wilson(k: float, n: float, z: float = Z95) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centro - margen), min(1.0, centro + margen)


def newcombe(a: int, n1: int, c: int, n2: int) -> tuple[float, float, float]:
    """Diferencia de proporciones a/n1 − c/n2 con el IC 95 % de Newcombe (método 10, a partir de Wilson)."""
    p1, p2 = a / n1, c / n2
    l1, u1 = wilson(a, n1)
    l2, u2 = wilson(c, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def _lcomb(n: int, k: int) -> float:
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def fisher(a: int, b: int, c: int, d: int) -> float:
    """p exacta bilateral de Fisher para la tabla [[a, b], [c, d]] (suma de tablas igual o menos probables)."""
    n1, n2, k = a + b, c + d, a + c
    lo, hi = max(0, k - n2), min(k, n1)
    total = _lcomb(n1 + n2, k)

    def lp(x: int) -> float:
        return _lcomb(n1, x) + _lcomb(n2, k - x) - total

    obs = lp(a)
    return min(1.0, sum(math.exp(lp(x)) for x in range(lo, hi + 1) if lp(x) <= obs + 1e-7))


def benjamini_hochberg(pvalores: list[float]) -> list[float]:
    m = len(pvalores)
    orden = sorted(range(m), key=pvalores.__getitem__)
    q, previo = [0.0] * m, 1.0
    for rango in range(m - 1, -1, -1):
        i = orden[rango]
        previo = min(previo, pvalores[i] * m / (rango + 1))
        q[i] = previo
    return q


def dispersion_poisson(grupos: list[list[tuple[float, float]]]) -> float | None:
    """φ de Pearson (cuasi-Poisson) con una tasa por grupo: Σ(k−g·r)²/(g·r) ÷ (anuncios − grupos).

    Las conversiones de anuncios distintos varían bastante más que un Poisson puro: sin esta corrección, los IC
    agregados salen demasiado estrechos. None si no hay réplica (gl < 1)."""
    chi, m, usados = 0.0, 0, 0
    for grupo in grupos:
        g_tot, k_tot = sum(g for g, _ in grupo), sum(k for _, k in grupo)
        if g_tot <= 0 or k_tot <= 0:
            continue
        usados += 1
        tasa = k_tot / g_tot
        for g, k in grupo:
            esperado = g * tasa
            if esperado > 0:
                chi += (k - esperado) ** 2 / esperado
                m += 1
    gl = m - usados
    return chi / gl if gl >= 1 else None


def dispersion_binomial(grupos: list[list[tuple[float, float]]]) -> float | None:
    """φ de Pearson (cuasi-binomial): grupos de (ensayos, éxitos) por anuncio."""
    chi, m, usados = 0.0, 0, 0
    for grupo in grupos:
        n_tot, x_tot = sum(n for n, _ in grupo), sum(x for _, x in grupo)
        if n_tot <= 0 or not 0 < x_tot < n_tot:
            continue
        usados += 1
        p = x_tot / n_tot
        for n, x in grupo:
            if n > 0:
                chi += (x - n * p) ** 2 / (n * p * (1 - p))
                m += 1
    gl = m - usados
    return chi / gl if gl >= 1 else None


def razon_costes(g1: float, k1: float, g0: float, k0: float, phi: float = 1.0) -> dict:
    """Coste por evento con el valor ÷ coste sin él, con IC 95 % (Wald en log, varianza × φ; Haldane si hay ceros)."""
    c = 0.5 if (k1 == 0 or k0 == 0) else 0.0
    ln_tasas = math.log(((k1 + c) / g1) / ((k0 + c) / g0))
    se = math.sqrt(max(phi, 1.0) * (1 / (k1 + c) + 1 / (k0 + c)))
    p = 2 * (1 - Z.cdf(abs(ln_tasas) / se))
    return {"razon": math.exp(-ln_tasas), "ic": [math.exp(-ln_tasas - Z95 * se), math.exp(-ln_tasas + Z95 * se)],
            "p": p}


def razon_proporciones(x1: float, n1: float, x0: float, n0: float, phi: float = 1.0) -> dict:
    """(x1/n1) ÷ (x0/n0) con IC 95 % (Wald en log, varianza × φ)."""
    c = 0.5 if (x1 == 0 or x0 == 0) else 0.0
    p1, p0 = (x1 + c) / (n1 + c), (x0 + c) / (n0 + c)
    ln_r = math.log(p1 / p0)
    se = math.sqrt(max(phi, 1.0) * ((1 - p1) / (x1 + c) + (1 - p0) / (x0 + c)))
    return {"razon": math.exp(ln_r), "ic": [math.exp(ln_r - Z95 * se), math.exp(ln_r + Z95 * se)],
            "p": 2 * (1 - Z.cdf(abs(ln_r) / se))}


def dhash_de_pixeles(px: bytes) -> str:
    """dHash de 64 bits a partir de 9×8 píxeles en gris (fila a fila): bit = píxel > su vecino derecho."""
    if len(px) != 72:
        raise ValueError("el dHash necesita 72 píxeles (9×8)")
    bits = 0
    for y in range(8):
        for x in range(8):
            bits = (bits << 1) | (px[y * 9 + x] > px[y * 9 + x + 1])
    return f"{bits:016x}"


def distancia_hamming(a: str, b: str) -> int | None:
    try:
        return bin(int(a, 16) ^ int(b, 16)).count("1")
    except (TypeError, ValueError):
        return None


# ================================================================ datos del cliente
def ruta_elementos(slug: str) -> pathlib.Path:
    return _comun.ruta_cliente(slug) / "datos" / ARCHIVO


def leer_registro(slug: str) -> list[dict]:
    ruta = _comun.ruta_cliente(slug) / "registro-creativo.csv"
    filas, _ = rc._leer_registro(ruta)
    if not filas:
        raise ErrorUsuario(f"{_rel(ruta)} no existe o está vacío: actualízalo antes con "
                           "`registro_creativo.py actualizar` (paso 1 de /analisis-creativo)")
    return [f for f in filas if (f.get("ad_id") or "").strip()]


def ultima_exportacion(slug: str) -> dict | None:
    """La exportación con la que se actualizó el registro por última vez (`registro_creativo.py` la guarda en
    datos/registro-creativo_ultima-exportacion.json): {desde, hasta, ad_ids}. None en registros de antes."""
    ruta = _comun.ruta_cliente(slug) / "datos" / rc.ULTIMA_EXPORTACION
    try:
        d = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or not isinstance(d.get("ad_ids"), list):
        return None
    return {"desde": str(d.get("desde") or ""), "hasta": str(d.get("hasta") or ""),
            "ad_ids": {str(x) for x in d["ad_ids"]}}


def registro_vigente(slug: str, todos: bool = False) -> tuple[list[dict], int, dict | None]:
    """Filas del registro que se analizan: con gasto y de la última exportación (hallazgo 19, I6: el registro
    conserva las cifras viejas de los anuncios que ya no vienen, y mezclarlas junta periodos). `todos`: todo el
    registro. Devuelve (filas, cuántos con gasto se quedan fuera por no venir en la exportación, exportación)."""
    registro = leer_registro(slug)
    exp = ultima_exportacion(slug)
    if todos:
        return registro, 0, exp
    con_gasto = [r for r in registro if (_num(r.get("gasto")) or 0) > 0]
    if exp is None:
        return con_gasto, 0, None
    dentro = [r for r in con_gasto if r["ad_id"].strip() in exp["ad_ids"]]
    return dentro, len(con_gasto) - len(dentro), exp


def _aviso_fuera(fuera: int, exp: dict | None) -> str:
    periodo = f" ({exp['desde']} a {exp['hasta']})" if exp and exp.get("desde") else ""
    return (f"{fuera} anuncios con gasto del registro no vienen en la última exportación{periodo}: se dejan fuera "
            "para no mezclar periodos (--todos para incluirlos)")


def leer_elementos(slug: str) -> tuple[dict[str, dict], list[str]]:
    ruta = ruta_elementos(slug)
    if not ruta.exists():
        return {}, []
    with ruta.open(encoding="utf-8-sig", newline="") as h:
        lector = csv.DictReader(h)
        extra = [c for c in (lector.fieldnames or []) if c and c not in COLUMNAS]
        filas = {}
        for f in lector:
            ad = (f.get("ad_id") or "").strip()
            if ad:
                filas[ad] = {c: (f.get(c) or "").strip() for c in COLUMNAS + extra}
    return filas, extra


def escribir_elementos(slug: str, filas: dict[str, dict], extra: list[str] | None = None) -> pathlib.Path:
    ruta = ruta_elementos(slug)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cols = COLUMNAS + (extra or [])
    tmp = ruta.with_suffix(".csv.tmp")
    orden = sorted(filas.values(), key=lambda f: (f.get("nombre") or "", f["ad_id"]), reverse=True)
    with tmp.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for f in orden:
            w.writerow({c: f.get(c, "") or "" for c in cols})
    tmp.replace(ruta)
    return ruta


def _fila_vacia(ad: str, nombre: str = "") -> dict:
    return {c: "" for c in COLUMNAS} | {"ad_id": ad, "nombre": nombre}


def soporte_por_formato(formato: str) -> str:
    return {"estatico": "imagen", "carrusel": "carrusel", "ugc": "video", "founder": "video", "demo": "video",
            "testimonio": "video", "podcast": "video"}.get((formato or "").strip(), "")


def _aplicar_no_aplica(fila: dict) -> None:
    if fila.get("soporte") in ("imagen", "carrusel"):
        for e in ESQUEMA:
            if e.aplica == "video" and not fila.get(e.columna):
                fila[e.columna] = NO_APLICA


def manuales_de(fila: dict) -> list[str]:
    """Etiquetas a mano que necesita la pieza (sin las de vídeo si es un estático o un carrusel)."""
    estatico = (fila.get("soporte") or "") in ("imagen", "carrusel")
    return [c for c in MANUALES if not (estatico and POR_COLUMNA[c].aplica == "video")]


def estado_etiquetado(fila: dict | None) -> str:
    if not fila:
        return "sin-fila"
    necesarias = manuales_de(fila)
    hechas = [c for c in necesarias if (fila.get(c) or "").strip()]
    if not hechas:
        return "pendiente"
    return "completa" if len(hechas) == len(necesarias) else "parcial"


def validar_valor(columna: str, valor: str) -> str | None:
    """None si vale; si no, el motivo."""
    e = POR_COLUMNA.get(columna)
    if e is None:
        return None if columna == "notas" else f"columna «{columna}» fuera del esquema"
    if valor in ("", *COMODINES):
        if valor == NO_APLICA and e.aplica != "video":
            return f"«no-aplica» solo vale en elementos de vídeo ({columna} aplica a todas las piezas)"
        return None
    if e.valores is None:
        n = _num(valor)
        return None if n is not None and n >= 0 else f"{columna} es un número de segundos ≥ 0"
    if valor not in e.valores:
        return f"«{valor}» no vale para {columna}: usa {' | '.join(e.valores)} (o duda)"
    return None


# ================================================================ etiquetas
def preparar(slug: str, todos: bool = False) -> dict:
    registro, fuera, exp = registro_vigente(slug, todos)
    filas, extra = leer_elementos(slug)
    creadas = 0
    for r in registro:
        ad = r["ad_id"].strip()
        f = filas.get(ad)
        if f is None:
            f = filas[ad] = _fila_vacia(ad, r.get("nombre", ""))
            creadas += 1
        f["nombre"] = r.get("nombre") or f.get("nombre", "")
        if not f.get("soporte"):
            f["soporte"] = soporte_por_formato(r.get("formato", ""))
        _rellenar_desde_indice(slug, f)
        _aplicar_no_aplica(f)
    ruta = escribir_elementos(slug, filas, extra)
    pend = pendientes(slug, todos=todos)
    return {"cliente": slug, "archivo": _rel(ruta), "filas": len(filas), "creadas": creadas,
            "pendientes": len(pend), "lista_pendientes": pend,
            "avisos": [_aviso_fuera(fuera, exp)] if fuera else []}


def pendientes(slug: str, todos: bool = False) -> list[dict]:
    filas, _ = leer_elementos(slug)
    dir_f = _comun.ruta_cliente(slug) / "creativos" / "_fotogramas"
    out = []
    for r in registro_vigente(slug, todos)[0]:
        gasto = _num(r.get("gasto")) or 0
        estado = estado_etiquetado(filas.get(r["ad_id"]))
        if estado == "completa":
            continue
        fila = filas.get(r["ad_id"]) or {"soporte": soporte_por_formato(r.get("formato", ""))}
        faltan = [c for c in manuales_de(fila) if not (fila.get(c) or "")]
        out.append({"ad_id": r["ad_id"], "nombre": r.get("nombre", ""), "gasto": round(gasto, 2), "estado": estado,
                    "faltan": faltan, "fotogramas": (dir_f / r["ad_id"] / "indice.json").exists()})
    return sorted(out, key=lambda x: -x["gasto"])


def _leer_cambios_archivo(ruta: str) -> list[dict]:
    p = pathlib.Path(ruta).expanduser()
    if not p.is_file():
        raise ErrorUsuario(f"No existe {ruta}")
    try:
        datos = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ErrorUsuario(f"{ruta} no es JSON válido: {e}") from None
    if isinstance(datos, dict):
        datos = [{"ad_id": k, **v} for k, v in datos.items() if isinstance(v, dict)]
    if not isinstance(datos, list) or not all(isinstance(x, dict) for x in datos):
        raise ErrorUsuario(f"{ruta}: usa una lista de objetos con ad_id (o un objeto ad_id → etiquetas)")
    return datos


def poner(slug: str, cambios: list[dict], por: str = "", hoy: date | None = None) -> dict:
    """Valida TODO antes de escribir: si un valor no vale, no se escribe nada."""
    hoy = hoy or date.today()
    filas, extra = leer_elementos(slug)
    try:
        nombres = {r["ad_id"]: r.get("nombre", "") for r in leer_registro(slug)}
    except ErrorUsuario:
        nombres = {}
    en_registro = set(nombres)
    errores, avisos, listos = [], [], []
    for cambio in cambios:
        ad = str(cambio.get("ad_id") or "").strip()
        if not re.fullmatch(r"\d{5,25}", ad):
            errores.append(f"ad_id no válido: {ad or '(vacío)'}")
            continue
        limpio = {}
        for col, valor in cambio.items():
            if col == "ad_id":
                continue
            if col not in EDITABLES:
                errores.append(f"{ad}: «{col}» no se puede poner a mano (editables: {', '.join(sorted(EDITABLES))})")
                continue
            v = str(valor).strip() if col == "notas" else normalizar_valor(valor)
            motivo = validar_valor(col, v)
            if motivo:
                errores.append(f"{ad}: {motivo}")
            else:
                limpio[col] = v
        if ad not in en_registro:
            avisos.append(f"{ad} no está en el registro creativo: no contará en el análisis hasta que lo esté")
        listos.append((ad, limpio))
    if errores:
        raise ErrorUsuario("No se ha escrito nada:\n  " + "\n  ".join(errores))
    for ad, limpio in listos:
        f = filas.setdefault(ad, _fila_vacia(ad, nombres.get(ad, "")))
        f.update(limpio)
        if any(c in MANUALES for c in limpio):
            f["etiquetado_por"] = por or f.get("etiquetado_por") or "usuario"
            f["fecha_etiquetado"] = hoy.isoformat()
        _aplicar_no_aplica(f)
    ruta = escribir_elementos(slug, filas, extra)
    return {"cliente": slug, "archivo": _rel(ruta), "anuncios": len(listos), "avisos": avisos}


def validar(slug: str) -> dict:
    ruta = ruta_elementos(slug)
    if not ruta.exists():
        raise ErrorUsuario(f"No existe {_rel(ruta)}: créalo con `etiquetas preparar`")
    errores, avisos = [], []
    with ruta.open(encoding="utf-8-sig", newline="") as h:
        lector = csv.DictReader(h)
        cabecera = lector.fieldnames or []
        filas = list(lector)
    faltan = [c for c in COLUMNAS if c not in cabecera]
    if faltan:
        errores.append(f"faltan columnas del esquema: {', '.join(faltan)}")
    sobran = [c for c in cabecera if c not in COLUMNAS]
    if sobran:
        avisos.append(f"columnas fuera del esquema (se conservan, no se analizan): {', '.join(sobran)}")
    vistos = Counter((f.get("ad_id") or "").strip() for f in filas)
    for ad, n in vistos.items():
        if ad and n > 1:
            errores.append(f"ad_id {ad} repetido {n} veces")
    try:
        en_registro = {r["ad_id"] for r in leer_registro(slug)}
    except ErrorUsuario:
        en_registro = None
    for i, f in enumerate(filas, start=2):
        ad = (f.get("ad_id") or "").strip()
        if not re.fullmatch(r"\d{5,25}", ad):
            errores.append(f"línea {i}: ad_id no válido ({ad or 'vacío'})")
            continue
        for e in ESQUEMA:
            motivo = validar_valor(e.columna, (f.get(e.columna) or "").strip())
            if motivo:
                errores.append(f"línea {i} ({ad}): {motivo}")
        if (f.get("huella_visual") or "") and not re.fullmatch(r"[0-9a-f]{16}", f["huella_visual"]):
            errores.append(f"línea {i} ({ad}): huella_visual no es un dHash de 16 caracteres hexadecimales")
        if en_registro is not None and ad not in en_registro:
            avisos.append(f"{ad} no está en el registro creativo")
    estados = Counter(estado_etiquetado({c: (f.get(c) or "").strip() for c in COLUMNAS}) for f in filas)
    return {"cliente": slug, "archivo": _rel(ruta), "filas": len(filas), "errores": errores, "avisos": avisos,
            "completas": estados.get("completa", 0), "parciales": estados.get("parcial", 0),
            "pendientes": estados.get("pendiente", 0)}


def esquema_dict() -> dict:
    return {"archivo": f"clientes/<slug>/datos/{ARCHIVO}", "columnas": COLUMNAS, "criterio_duda": CRITERIO_DUDA,
            "comodines": {DUDA: "no estoy seguro: no cuenta en el análisis de ese elemento",
                          NO_APLICA: "elemento de vídeo en un estático o carrusel"},
            "etiquetas": [{"columna": e.columna, "valores": list(e.valores) if e.valores else "número (segundos)",
                           "aplica": e.aplica, "automatica": e.automatica, "define": e.define} for e in ESQUEMA]}


# ================================================================ fotogramas
def _bin(nombre: str) -> str | None:
    return shutil.which(nombre)


def _corre(args: list[str], binario: bool = False, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=not binario, timeout=timeout, check=False)


def clasificar_aspecto(ancho: int, alto: int) -> str:
    if not ancho or not alto:
        return ""
    r = ancho / alto
    for nombre, valor, tol in (("9x16", 9 / 16, 0.03), ("4x5", 0.8, 0.03), ("1x1", 1.0, 0.03),
                               ("16x9", 16 / 9, 0.05)):
        if abs(r - valor) <= tol:
            return nombre
    return "otro"


def ritmo_por_cortes(duracion: float | None, cortes: int) -> tuple[float | None, str]:
    """(duración media de plano, ritmo): rápido < 2,5 s, medio 2,5–6 s, lento > 6 s [HYPOTHESIS]."""
    if not duracion:
        return None, ""
    plano = duracion / (cortes + 1)
    return plano, "rapido" if plano < 2.5 else ("medio" if plano <= 6 else "lento")


def sondear(ruta: pathlib.Path) -> dict:
    """Duración, ancho y alto (con rotación) con ffprobe; si no hay ffprobe, de la salida de `ffmpeg -i`."""
    sonda = _bin("ffprobe")
    if sonda:
        r = _corre([sonda, "-v", "error", "-select_streams", "v:0", "-show_entries",
                    "stream=width,height,duration:stream_tags=rotate:stream_side_data=rotation:format=duration",
                    "-of", "json", str(ruta)])
        try:
            datos = json.loads(r.stdout or "{}")
        except json.JSONDecodeError:
            datos = {}
        st = (datos.get("streams") or [{}])[0]
        ancho, alto = int(st.get("width") or 0), int(st.get("height") or 0)
        rot = st.get("tags", {}).get("rotate") or next(
            (x.get("rotation") for x in st.get("side_data_list") or [] if "rotation" in x), 0)
        try:
            if abs(int(float(rot))) % 180 == 90:
                ancho, alto = alto, ancho
        except (TypeError, ValueError):
            pass
        dur = _num((datos.get("format") or {}).get("duration")) or _num(st.get("duration"))
        return {"duracion_s": dur, "ancho": ancho, "alto": alto}
    r = _corre([_bin("ffmpeg"), "-hide_banner", "-i", str(ruta)])
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr or "")
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else None
    t = re.search(r"Video: .*?(\d{2,5})x(\d{2,5})", r.stderr or "")
    return {"duracion_s": dur, "ancho": int(t.group(1)) if t else 0, "alto": int(t.group(2)) if t else 0}


def detectar_cortes(ruta: pathlib.Path, umbral: float = 0.30) -> list[float]:
    """Instantes (s) de cambio de plano con el filtro `select=gt(scene,umbral)` de FFmpeg."""
    r = _corre([_bin("ffmpeg"), "-hide_banner", "-nostats", "-i", str(ruta), "-an", "-vf",
                f"select='gt(scene,{umbral})',showinfo", "-f", "null", "-"])
    return [round(float(x), 2) for x in re.findall(r"pts_time:\s*([\d.]+)", r.stderr or "")]


def huella(ruta_imagen: pathlib.Path) -> str:
    """dHash del primer fotograma (FFmpeg lo reduce a 9×8 en gris)."""
    ff = _bin("ffmpeg")
    if not ff:
        return ""
    r = _corre([ff, "-v", "error", "-i", str(ruta_imagen), "-vf", "scale=9:8:flags=area,format=gray",
                "-pix_fmt", "gray", "-f", "rawvideo", "-frames:v", "1", "pipe:1"], binario=True)
    try:
        return dhash_de_pixeles(r.stdout[:72]) if r.returncode == 0 and len(r.stdout) >= 72 else ""
    except ValueError:
        return ""


def _ff(args: list[str]) -> None:
    r = _corre([_bin("ffmpeg"), "-v", "error", "-y", *args])
    if r.returncode != 0:  # sin rutas absolutas en el mensaje
        detalle = (r.stderr or "").replace(str(_comun.RAIZ.resolve()) + "/", "").replace(str(_comun.RAIZ) + "/", "")
        raise ErrorUsuario(f"FFmpeg no ha podido procesar el archivo: {detalle.strip()[-300:]}")


def extraer_video(ruta: pathlib.Path, destino: pathlib.Path) -> dict:
    info = sondear(ruta)
    dur = info["duracion_s"]
    destino.mkdir(parents=True, exist_ok=True)
    _ff(["-i", str(ruta), "-frames:v", "1", "-vf", "scale='min(1080,iw)':-2", str(destino / "f0.jpg")])
    _ff(["-t", "3", "-i", str(ruta), "-vf", "fps=4,scale=270:-2,tile=4x3", "-frames:v", "1",
         str(destino / "arranque.jpg")])
    fps = f"15/{dur:.3f}" if dur and dur > 0 else "1"
    _ff(["-i", str(ruta), "-vf", f"fps={fps},scale=216:-2,tile=5x3", "-frames:v", "1", str(destino / "hoja.jpg")])
    cortes = detectar_cortes(ruta)
    plano, ritmo = ritmo_por_cortes(dur, len(cortes))
    return {**info, "cortes": cortes, "plano_medio_s": round(plano, 2) if plano else None, "ritmo_sugerido": ritmo,
            "imagenes": {"f0": "f0.jpg", "arranque": "arranque.jpg", "hoja": "hoja.jpg"},
            # segundo aproximado de cada casilla, de izquierda a derecha y de arriba abajo
            "arranque_segundos": [round(i / 4, 2) for i in range(12)],
            "hoja_segundos": [round(i * dur / 15, 1) for i in range(15)] if dur else []}


def extraer_imagenes(rutas: list[pathlib.Path], destino: pathlib.Path) -> dict:
    destino.mkdir(parents=True, exist_ok=True)
    info = sondear(rutas[0])
    _ff(["-i", str(rutas[0]), "-frames:v", "1", "-vf", "scale='min(1080,iw)':-2", str(destino / "f0.jpg")])
    imagenes = {"f0": "f0.jpg"}
    if len(rutas) > 1:
        imagenes["hoja"] = "hoja.jpg"
        _mosaico(rutas, destino / "hoja.jpg", columnas=min(5, len(rutas)), caja=(270, 338))
    return {"duracion_s": None, "ancho": info["ancho"], "alto": info["alto"], "cortes": [], "plano_medio_s": None,
            "ritmo_sugerido": "", "imagenes": imagenes, "tarjetas": len(rutas)}


def _mosaico(rutas: list[pathlib.Path], salida: pathlib.Path, columnas: int, caja: tuple[int, int]) -> None:
    """Mosaico de imágenes de tamaños distintos: primero cada una a una caja fija, luego `tile`."""
    w, h = caja
    filas = max(1, math.ceil(len(rutas) / columnas))
    with tempfile.TemporaryDirectory(prefix="mosaico-") as tmp:
        for i, r in enumerate(rutas, start=1):
            _ff(["-i", str(r), "-frames:v", "1", "-vf",
                 f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=gray",
                 str(pathlib.Path(tmp) / f"{i:04d}.png")])
        _ff(["-framerate", "1", "-i", str(pathlib.Path(tmp) / "%04d.png"), "-vf", f"tile={columnas}x{filas}",
             "-frames:v", "1", str(salida)])


def buscar_local(dir_pieza: pathlib.Path, hook: str | None) -> tuple[str, list[pathlib.Path]] | None:
    """(soporte, archivos) de la pieza: vídeo 9:16 > 4:5 > 1:1; carrusel `_01…`; imagen."""
    if not dir_pieza.is_dir():
        return None
    archivos = sorted(p for p in dir_pieza.iterdir() if p.is_file() and p.suffix.lower() in EXT_VIDEO | EXT_IMAGEN)
    if hook:
        con_hook = [p for p in archivos if re.search(rf"_{re.escape(hook)}(_|\.|$)", p.name)]
        archivos = con_hook or archivos

    def preferido(lista: list[pathlib.Path]) -> pathlib.Path:
        for asp in ORDEN_ASPECTO:
            for p in lista:
                if f"_{asp}" in p.name:
                    return p
        return lista[0]

    videos = [p for p in archivos if p.suffix.lower() in EXT_VIDEO]
    if videos:
        return "video", [preferido(videos)]
    imagenes = [p for p in archivos if p.suffix.lower() in EXT_IMAGEN]
    tarjetas = sorted(p for p in imagenes if re.search(r"_\d{2}\.\w+$", p.name))
    if len(tarjetas) >= 2:
        asp = next((a for a in ORDEN_ASPECTO if any(f"_{a}" in p.name for p in tarjetas)), None)
        return "carrusel", [p for p in tarjetas if not asp or f"_{asp}" in p.name]
    if imagenes:
        return "imagen", [preferido(imagenes)]
    return None


def _descargar(url: str, destino: pathlib.Path, maximo: int) -> None:
    """Descarga de la CDN de Meta. La URL no se imprime nunca (va firmada)."""
    peticion = urllib.request.Request(url, headers={"User-Agent": _comun.UA_NAVEGADOR})
    with urllib.request.urlopen(peticion, timeout=300) as r, destino.open("wb") as h:
        total = 0
        while True:
            trozo = r.read(1 << 20)
            if not trozo:
                break
            total += len(trozo)
            if total > maximo:
                raise ErrorUsuario(f"La descarga pasa de {maximo // (1 << 20)} MB: se corta")
            h.write(trozo)


def _medios_de_creatividad(creativa: dict) -> dict:
    oss = creativa.get("object_story_spec") or {}
    afs = creativa.get("asset_feed_spec") or {}
    video_id = (creativa.get("video_id") or (oss.get("video_data") or {}).get("video_id")
                or next((v.get("video_id") for v in afs.get("videos") or [] if v.get("video_id")), None))
    tarjetas = [c.get("picture") for c in (oss.get("link_data") or {}).get("child_attachments") or []
                if c.get("picture")]
    imagen = (creativa.get("image_url") or (oss.get("link_data") or {}).get("picture")
              or next((i.get("url") for i in afs.get("images") or [] if i.get("url")), None))
    return {"video_id": video_id, "imagen": imagen, "tarjetas": tarjetas, "creativa_id": creativa.get("id")}


def desde_api(meta, ad_id: str, destino: pathlib.Path, descargar_video: bool) -> dict:
    """Miniatura (y duración) de Meta; con `descargar_video`, el vídeo entero a un temporal que se borra."""
    ad = meta.uno(ad_id, fields="id,name,creative{id,object_type,image_url,video_id,object_story_spec,"
                                "asset_feed_spec}")
    medios = _medios_de_creatividad(ad.get("creative") or {})
    destino.mkdir(parents=True, exist_ok=True)
    if medios["video_id"]:
        vid = medios["video_id"]
        try:
            datos_video = meta.uno(vid, fields="length,picture")
        except Exception:  # noqa: BLE001 — el vídeo puede no ser legible con este token; seguimos con la miniatura
            datos_video = {}
        duracion = _num(datos_video.get("length"))
        if descargar_video and _bin("ffmpeg"):
            fuente = meta.uno(vid, fields="source").get("source")
            if fuente:
                with tempfile.TemporaryDirectory(prefix="video-meta-") as tmp:
                    local = pathlib.Path(tmp) / f"{ad_id}.mp4"
                    _descargar(fuente, local, 1 << 30)
                    info = extraer_video(local, destino)
                return {**info, "fuente": "api-video", "soporte": "video"}
        try:
            url = meta.miniatura(vid)
        except Exception:  # noqa: BLE001
            url = datos_video.get("picture")
        if not url:
            raise ErrorUsuario(f"{ad_id}: Meta no da miniatura del vídeo")
        _descargar(url, destino / "f0.jpg", 20 << 20)
        info = sondear(destino / "f0.jpg") if _bin("ffmpeg") else {"ancho": 0, "alto": 0}
        return {"duracion_s": duracion, "ancho": info["ancho"], "alto": info["alto"], "cortes": [],
                "plano_medio_s": None, "ritmo_sugerido": "", "imagenes": {"f0": "f0.jpg"},
                "fuente": "api-miniatura", "soporte": "video"}
    urls = medios["tarjetas"] or ([medios["imagen"]] if medios["imagen"] else [])
    if not urls and medios["creativa_id"]:
        url = meta.uno(medios["creativa_id"], fields="thumbnail_url", thumbnail_width=1080,
                       thumbnail_height=1080).get("thumbnail_url")
        urls = [url] if url else []
    if not urls:
        raise ErrorUsuario(f"{ad_id}: la creatividad no tiene imagen ni vídeo legibles")
    if len(urls) == 1:
        _descargar(urls[0], destino / "f0.jpg", 20 << 20)
        info = sondear(destino / "f0.jpg") if _bin("ffmpeg") else {"ancho": 0, "alto": 0}
        imagenes = {"f0": "f0.jpg"}
    else:
        locales = []
        for i, u in enumerate(urls, start=1):
            locales.append(destino / f"tarjeta_{i:02d}.jpg")
            _descargar(u, locales[-1], 20 << 20)
        shutil.copyfile(locales[0], destino / "f0.jpg")
        imagenes = {"f0": "f0.jpg"}
        if _bin("ffmpeg"):
            _mosaico(locales, destino / "hoja.jpg", columnas=min(5, len(locales)), caja=(270, 338))
            imagenes["hoja"] = "hoja.jpg"
        info = sondear(locales[0]) if _bin("ffmpeg") else {"ancho": 0, "alto": 0}
    return {"duracion_s": None, "ancho": info["ancho"], "alto": info["alto"], "cortes": [], "plano_medio_s": None,
            "ritmo_sugerido": "", "imagenes": imagenes, "fuente": "api-miniatura",
            "soporte": "carrusel" if len(urls) > 1 else "imagen"}


def _rellenar_desde_indice(slug: str, fila: dict) -> None:
    indice = _comun.ruta_cliente(slug) / "creativos" / "_fotogramas" / fila["ad_id"] / "indice.json"
    if not indice.exists():
        return
    try:
        d = json.loads(indice.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    if d.get("soporte"):
        fila["soporte"] = d["soporte"]
    if d.get("relacion_aspecto"):
        fila["relacion_aspecto"] = d["relacion_aspecto"]
    if d.get("duracion_s") is not None:
        fila["duracion_s"] = _fmt(d["duracion_s"], 1)
    if d.get("huella_visual"):
        fila["huella_visual"] = d["huella_visual"]
    fila["fuente_visual"] = d.get("fuente", fila.get("fuente_visual", ""))


def fotogramas(slug: str, ads: list[str] | None = None, video: str | None = None, api: bool = False,
               descargar_video: bool = False, cuadricula: bool = False, maximo: int = 30,
               hoy: date | None = None) -> dict:
    hoy = hoy or date.today()
    dir_c = _comun.ruta_cliente(slug)
    _comun.leer_ficha(slug)  # FichaInvalida → configuración
    try:
        registro = {r["ad_id"]: r for r in leer_registro(slug)}
        vigentes = registro_vigente(slug)[0]
    except ErrorUsuario:
        if not ads:
            raise
        registro, vigentes = {}, []
    if video and (not ads or len(ads) != 1):
        raise ErrorUsuario("--video va con un solo --ad")
    if ads:
        objetivo = ads
    else:
        con_gasto = sorted(vigentes, key=lambda r: -(_num(r.get("gasto")) or 0))
        objetivo = [r["ad_id"] for r in con_gasto[:maximo]]
    ff = _bin("ffmpeg")
    meta = None
    resultados, avisos = [], []
    filas, extra = leer_elementos(slug)
    for ad in objetivo:
        r = registro.get(ad, {"ad_id": ad, "nombre": ""})
        destino = dir_c / "creativos" / "_fotogramas" / ad
        nombre = r.get("nombre", "")
        base = nombre_base(nombre)
        hook = (nomenclatura.parsear_anuncio(nombre) or {}).get("hook")
        try:
            local = None
            if video:
                p = pathlib.Path(video).expanduser()
                if not p.is_file():
                    raise ErrorUsuario(f"No existe {video}")
                local = ("video" if p.suffix.lower() in EXT_VIDEO else "imagen", [p])
            else:
                carpeta = (r.get("ruta_creativo") or (f"creativos/{base}" if base else "")).strip()
                if carpeta:
                    local = buscar_local(dir_c / carpeta, hook)
            if local:
                if not ff:
                    raise ErrorConfig("Falta FFmpeg para sacar fotogramas de archivos locales: instálalo (/doctor "
                                      "dice cómo en tu sistema) o usa --api para la miniatura de Meta")
                soporte, archivos = local
                info = extraer_video(archivos[0], destino) if soporte == "video" else \
                    extraer_imagenes(archivos, destino)
                info.update(fuente="local", soporte=soporte)
                origen = _rel(archivos[0])
            elif api:
                if meta is None:
                    import meta_ads  # noqa: PLC0415 — solo si hace falta la API (B2)
                    meta = meta_ads.conectar(meta_ads.contexto(slug), requiere_cuenta=False)
                info = desde_api(meta, ad, destino, descargar_video)
                origen = "api"
            else:
                raise ErrorUsuario("sin archivo local (ruta_creativo o creativos/<nombre-base>/): pasa --video o "
                                   "--api")
        except ErrorConfig:
            raise
        except ErrorUsuario as e:
            resultados.append({"ad_id": ad, "ok": False, "motivo": str(e)})
            continue
        except Exception as e:  # noqa: BLE001 — un anuncio roto no para a los demás
            if getattr(e, "salida", None) == 2:  # token rechazado o sin permisos (ErrorMeta de meta_ads.py)
                raise ErrorConfig(str(e)) from None
            motivo = str(e).splitlines()[0] if str(e) else type(e).__name__
            resultados.append({"ad_id": ad, "ok": False, "motivo": re.sub(r"https?://\S+", "<url>", motivo)})
            continue
        info["relacion_aspecto"] = clasificar_aspecto(info.get("ancho") or 0, info.get("alto") or 0)
        info["huella_visual"] = huella(destino / "f0.jpg") if (destino / "f0.jpg").exists() else ""
        # Sin nombre ni ruta del archivo: llevan ángulo y concepto, y el etiquetado del paso 3.2 de
        # /analisis-creativo es a ciegas.
        indice = {"ad_id": ad, "fecha": hoy.isoformat(), **info,
                  "duracion_s": round(info["duracion_s"], 2) if info.get("duracion_s") else info.get("duracion_s")}
        (destino / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")
        fila = filas.setdefault(ad, _fila_vacia(ad, nombre))
        _rellenar_desde_indice(slug, fila)
        _aplicar_no_aplica(fila)
        resultados.append({"ad_id": ad, "ok": True, "carpeta": _rel(destino), "fuente": info["fuente"],
                           "archivo_origen": origen,
                           "soporte": info["soporte"], "duracion_s": indice["duracion_s"],
                           "relacion_aspecto": info["relacion_aspecto"], "ritmo_sugerido": info["ritmo_sugerido"],
                           "imagenes": [f"{_rel(destino)}/{v}" for v in info["imagenes"].values()]})
        if info["fuente"] == "api-miniatura":
            avisos.append(f"{ad}: solo la miniatura de Meta (no el fotograma 0 ni el arranque); para ver el vídeo "
                          "entero, --descargar-video o el archivo local")
    if any(x["ok"] for x in resultados):
        escribir_elementos(slug, filas, extra)
    salida = {"cliente": slug, "procesados": sum(x["ok"] for x in resultados), "anuncios": resultados,
              "avisos": avisos}
    if cuadricula:
        salida["cuadricula"] = _cuadricula(slug, [x["ad_id"] for x in resultados if x["ok"]], registro, hoy)
    return salida


def _cuadricula(slug: str, ads: list[str], registro: dict, hoy: date) -> dict | None:
    if not ads or not _bin("ffmpeg"):
        return None
    base = _comun.ruta_cliente(slug) / "creativos" / "_fotogramas"
    rutas = [base / ad / "f0.jpg" for ad in ads if (base / ad / "f0.jpg").exists()]
    columnas = min(6, len(rutas))
    salida = base / f"cuadricula_{hoy.isoformat()}.jpg"
    _mosaico(rutas, salida, columnas=columnas, caja=(216, 384))
    lineas = [f"# Prueba de la cuadrícula · {slug} · {hoy.isoformat()}", "",
              "Primer fotograma de cada anuncio, de izquierda a derecha y de arriba abajo. Si a un metro de distancia "
              "dos parecen el mismo anuncio, lo son para quien hace scroll y probablemente para el sistema "
              "(meta-ads-kb/03-creatividad/01-creative-es-targeting.md, implicaciones operativas).", "",
              "| Posición | ad_id | Anuncio | Gasto |", "|---|---|---|---|"]
    for i, ruta in enumerate(rutas):
        ad = ruta.parent.name
        r = registro.get(ad, {})
        lineas.append(f"| fila {i // columnas + 1}, columna {i % columnas + 1} | {ad} | {r.get('nombre', '')} | "
                      f"{_euros(_num(r.get('gasto')))} |")
    (base / f"cuadricula_{hoy.isoformat()}.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return {"imagen": _rel(salida), "indice": _rel(base / f"cuadricula_{hoy.isoformat()}.md"), "anuncios": len(rutas)}


# ================================================================ análisis
@dataclass
class Anuncio:
    ad_id: str
    nombre: str
    concepto: str
    conjunto: str
    gasto: float
    impresiones: float
    vistas_3s: float | None
    thruplay: float | None
    clics: float | None
    capas: dict
    veredicto: str
    edad: int | None
    elementos: dict = field(default_factory=dict)
    duracion_s: float | None = None
    huella: str = ""


def clave_concepto(r: dict) -> str:
    if (r.get("angulo") or "").strip() and (r.get("concepto") or "").strip():
        return f"{r['angulo'].strip()}/{r['concepto'].strip()}"
    return nombre_base(r.get("nombre", "")) or f"ad:{r.get('ad_id')}"


def cargar_anuncios(slug: str, hoy: date, todos: bool = False) -> tuple[list[Anuncio], dict]:
    registro, fuera, exp = registro_vigente(slug, todos)
    desde = (exp or {}).get("desde", "")
    etiquetas, _ = leer_elementos(slug)
    anuncios = []
    for r in registro:
        gasto = _num(r.get("gasto")) or 0.0
        imp = _num(r.get("impresiones")) or 0.0
        hook, hold, ctr = _num(r.get("hook_rate")), _num(r.get("hold_rate")), _num(r.get("ctr"))
        v3 = round(hook / 100 * imp) if hook is not None and imp else None
        tp = round(hold / 100 * v3) if hold is not None and v3 else None
        clics = round(ctr / 100 * imp) if ctr is not None and imp else None
        # Edad de la cohorte: desde el inicio del anuncio o el de la exportación, si es posterior (las cifras de
        # negocio son las del periodo). Sin fecha del anuncio, None: las capas de negocio cuentan como inmaduras.
        try:
            edad = (hoy - max(date.fromisoformat(r.get("fecha") or ""),
                              date.fromisoformat(desde) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", desde) else date.min)
                    ).days
        except ValueError:
            edad = None
        capas = {c: _num(r.get(c)) for c in set().union(*rc.CAPAS.values())}
        e = etiquetas.get(r["ad_id"], {})
        elementos = {c: e.get(c, "") for c in ETIQUETAS if c != "duracion_s"}
        dur = _num(e.get("duracion_s"))
        elementos["duracion"] = (NO_APLICA if e.get("duracion_s") == NO_APLICA else
                                 DUDA if e.get("duracion_s") == DUDA else tramo_duracion(dur) or "")
        elementos["formato"] = (r.get("formato") or "").strip()
        elementos["via"] = (r.get("via") or "").strip()
        anuncios.append(Anuncio(r["ad_id"], r.get("nombre", ""), clave_concepto(r), (r.get("conjunto") or "").strip(),
                                gasto, imp, v3, tp, clics, capas, (r.get("veredicto") or "").strip(), edad,
                                elementos, dur, e.get("huella_visual", "")))
    estados = [estado_etiquetado(etiquetas.get(a.ad_id)) for a in anuncios]
    meta = {"etiquetados": sum(e in ("parcial", "completa") for e in estados),
            "sin_etiquetar": sum(e in ("pendiente", "sin-fila") for e in estados), "fuera_de_exportacion": fuera}
    if fuera:
        meta["aviso_fuera"] = _aviso_fuera(fuera, exp)
    return anuncios, meta


def _conocido(v: str) -> bool:
    return bool(v) and v not in COMODINES


def elegir_capa(anuncios: list[Anuncio], modelo: str, madurez, forzada: str | None) -> tuple:
    """`madurez`: {capa: días} (`registro_creativo.madurez_de`) o un entero para todas las capas de negocio. Un
    anuncio sin fecha fiable cuenta como inmaduro en las capas de negocio (hallazgo 17, I6)."""
    capas = rc.CAPAS[modelo]
    if forzada and forzada not in capas:
        raise ErrorUsuario(f"--capa {forzada} no existe para {modelo}: usa {', '.join(capas)}")
    if not isinstance(madurez, dict):
        madurez = rc.madurez_de(modelo, madurez)
    descartadas = []
    for capa in ([forzada] if forzada else capas):
        dias = madurez.get(capa, 14)
        validos = [a for a in anuncios if a.capas.get(capa) is not None
                   and (capa in rc.CAPAS_SUPERFICIALES or (a.edad is not None and a.edad >= dias))]
        total = sum(a.capas[capa] for a in validos)
        if forzada or total >= 2 * rc.N_DECIDIR:
            return capa, validos, descartadas
        if any(a.capas.get(capa) is not None for a in anuncios):
            descartadas.append({"capa": capa, "eventos": int(total), "anuncios": len(validos)})
    return None, [], descartadas


def _valores_a_probar(anuncios: list[Anuncio], elemento: str) -> list[str]:
    valores = sorted({a.elementos.get(elemento, "") for a in anuncios if _conocido(a.elementos.get(elemento, ""))})
    if len(valores) < 2:
        return []
    if len(valores) == 2:  # binario: una sola comparación
        positivo = [v for v in valores if v not in NEGATIVOS]
        return [positivo[0] if len(positivo) == 1 else
                min(valores, key=lambda v: sum(a.elementos.get(elemento) == v for a in anuncios))]
    return valores


# Orden de prioridad: cuando dos valores van siempre juntos, representa al grupo el primero (lo más accionable
# del contenido antes que los descriptores de formato).
ELEMENTOS_ANALISIS = ["quien_habla", "estructura", "primer_fotograma", "gancho", "cifra", "demo", "prueba_social",
                      "texto_0s", "audiencia_nombrada", "consciencia", "menciona_ia", "filtro", "cta", "subtitulos",
                      "ritmo", "duracion", "acabado", "tono", "persona", "soporte", "relacion_aspecto", "formato", "via"]


def lente_coste(anuncios: list[Anuncio], capa: str) -> list[dict]:
    filas = []
    for el in ELEMENTOS_ANALISIS:
        conocidos = [a for a in anuncios if _conocido(a.elementos.get(el, ""))]
        for valor in _valores_a_probar(conocidos, el):
            con = [a for a in conocidos if a.elementos[el] == valor]
            sin = [a for a in conocidos if a.elementos[el] != valor]
            g1, k1 = sum(a.gasto for a in con), sum(a.capas[capa] for a in con)
            g0, k0 = sum(a.gasto for a in sin), sum(a.capas[capa] for a in sin)
            f = {"elemento": el, "valor": valor, "anuncios": [len(con), len(sin)], "gasto": [round(g1, 2), round(g0, 2)],
                 "eventos": [int(k1), int(k0)], "coste": [g1 / k1 if k1 else None, g0 / k0 if k0 else None],
                 "conceptos": len({a.concepto for a in con}), "ganadores_con": sum(a.veredicto == "ganador" for a in con),
                 "_ads": frozenset(a.ad_id for a in con), "_base": frozenset(a.ad_id for a in conocidos)}
            if g1 <= 0 or g0 <= 0:
                continue
            phi = dispersion_poisson([[(a.gasto, a.capas[capa]) for a in con], [(a.gasto, a.capas[capa]) for a in sin]])
            f["phi"] = round(phi, 2) if phi is not None else None
            f.update(razon_costes(g1, k1, g0, k0, phi or 1.0))
            if k1 < rc.N_DECIDIR or k0 < rc.N_DECIDIR or len(con) < MIN_ANUNCIOS_LADO or len(sin) < MIN_ANUNCIOS_LADO:
                f["estado"] = "n-insuficiente"
            elif f["conceptos"] < 2 or len({a.concepto for a in sin}) < 2:
                f["estado"] = "confundido"
            else:
                f["estado"] = "evaluable"
            filas.append(f)
    marcar_alias(filas)
    _clasificar(filas, "razon", favorable_si_menor=True)
    return filas


def _etq(f: dict) -> str:
    return f"{f['elemento']} = {f['valor']}"


def marcar_alias(filas: list[dict]) -> None:
    """Valores que parten los anuncios igual que otro ya probado no se pueden separar: se prueban una vez.

    Igual = mismos anuncios con el valor (`_ads`) sobre la misma base (`_base`), o justo los contrarios (persona = real
    frente a soporte = imagen cuando todos los estáticos van sin persona). La primera fila (orden de ELEMENTOS_ANALISIS)
    representa al grupo y lista las demás en `juntos`; las demás quedan en estado «alias» y no entran en
    Benjamini-Hochberg (contarlas inflaría m con pruebas repetidas)."""
    primero: dict[tuple, tuple[dict, bool]] = {}
    for f in filas:
        ads, base = f.get("_ads"), f.get("_base")
        if not ads:
            continue
        clave = (base, ads)
        inversa = (base, base - ads) if base is not None else None
        if clave in primero or (inversa and inversa in primero):
            rep, invertido = primero[clave] if clave in primero else (primero[inversa][0], True)
            nota = f"{_etq(f)} (al revés)" if invertido else _etq(f)
            rep.setdefault("juntos", []).append(nota)
            f["alias_de"], f["estado"] = _etq(rep) + (" al revés" if invertido else ""), "alias"
        else:
            primero[clave] = (f, False)


def _jaccard(a: frozenset, b: frozenset) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def _sin_internos(filas: list[dict]) -> list[dict]:
    return [{k: v for k, v in f.items() if not k.startswith("_")} for f in filas]


def _clasificar(filas: list[dict], clave: str, favorable_si_menor: bool) -> None:
    evaluables = [f for f in filas if f["estado"] == "evaluable"]
    for f, q in zip(evaluables, benjamini_hochberg([f["p"] for f in evaluables])):
        f["q"] = q
        a_favor = (f[clave] < 1) if favorable_si_menor else (f[clave] > 1)
        sentido = "a-favor" if a_favor else "en-contra"
        f["estado"] = (f"senal-{sentido}" if q < Q_SENAL else f"pista-{sentido}" if f["p"] < 0.05
                       else "sin-diferencia")


def lente_veredictos(anuncios: list[Anuncio]) -> list[dict]:
    con_veredicto = [a for a in anuncios if a.veredicto in ("ganador", "perdedor")]
    filas = []
    for el in ELEMENTOS_ANALISIS:
        conocidos = [a for a in con_veredicto if _conocido(a.elementos.get(el, ""))]
        gan = [a for a in conocidos if a.veredicto == "ganador"]
        per = [a for a in conocidos if a.veredicto == "perdedor"]
        for valor in _valores_a_probar(conocidos, el):
            a_ = sum(x.elementos[el] == valor for x in gan)
            c_ = sum(x.elementos[el] == valor for x in per)
            f = {"elemento": el, "valor": valor, "ganadores": [a_, len(gan)], "perdedores": [c_, len(per)],
                 "_ads": frozenset(x.ad_id for x in gan + per if x.elementos[el] == valor),
                 "_base": frozenset(x.ad_id for x in gan + per)}
            if len(gan) < MIN_VEREDICTOS or len(per) < MIN_VEREDICTOS:
                f["estado"] = "n-insuficiente"
                filas.append(f)
                continue
            d, lo, hi = newcombe(a_, len(gan), c_, len(per))
            f.update(diferencia=d, ic=[lo, hi], p=fisher(a_, len(gan) - a_, c_, len(per) - c_), estado="evaluable")
            filas.append(f)
    marcar_alias([f for f in filas if f["estado"] == "evaluable"])
    evaluables = [f for f in filas if f["estado"] == "evaluable"]
    for f, q in zip(evaluables, benjamini_hochberg([f["p"] for f in evaluables])):
        f["q"] = q
        sentido = "mas-en-ganadores" if f["diferencia"] > 0 else "mas-en-perdedores"
        f["estado"] = (sentido if q < Q_SENAL else f"pista-{sentido}" if f["p"] < 0.05 else "sin-diferencia")
    return filas


METRICAS_ATENCION = {
    "hook_rate": ("impresiones", "vistas_3s", MIN_IMPRESIONES),
    "hold_rate": ("vistas_3s", "thruplay", MIN_VISTAS_HOLD),
    "ctr": ("impresiones", "clics", MIN_IMPRESIONES),
}


def lente_atencion(anuncios: list[Anuncio]) -> list[dict]:
    filas = []
    for metrica, (ensayos, exitos, minimo) in METRICAS_ATENCION.items():
        base = [a for a in anuncios if getattr(a, exitos) is not None and getattr(a, ensayos)]
        if metrica == "hold_rate":  # ThruPlay infla el hold de vídeos de ≤15 s (KB 03/07 §2)
            base = [a for a in base if a.duracion_s is None or a.duracion_s > 15]
        bloque = []
        for el in ELEMENTOS_ANALISIS:
            if metrica != "ctr" and el in ("soporte",):
                continue
            conocidos = [a for a in base if _conocido(a.elementos.get(el, ""))]
            for valor in _valores_a_probar(conocidos, el):
                con = [a for a in conocidos if a.elementos[el] == valor]
                sin = [a for a in conocidos if a.elementos[el] != valor]
                n1, x1 = sum(getattr(a, ensayos) for a in con), sum(getattr(a, exitos) for a in con)
                n0, x0 = sum(getattr(a, ensayos) for a in sin), sum(getattr(a, exitos) for a in sin)
                if n1 <= 0 or n0 <= 0:
                    continue
                f = {"metrica": metrica, "elemento": el, "valor": valor, "anuncios": [len(con), len(sin)],
                     "tasa": [x1 / n1, x0 / n0], "_ads": frozenset(a.ad_id for a in con),
                     "_base": frozenset(a.ad_id for a in conocidos)}
                phi = dispersion_binomial([[(getattr(a, ensayos), getattr(a, exitos)) for a in con],
                                           [(getattr(a, ensayos), getattr(a, exitos)) for a in sin]])
                f["phi"] = round(phi, 2) if phi is not None else None
                f.update(razon_proporciones(x1, n1, x0, n0, phi or 1.0))
                f["estado"] = ("n-insuficiente" if n1 < minimo or n0 < minimo or len(con) < MIN_ANUNCIOS_LADO
                               or len(sin) < MIN_ANUNCIOS_LADO else "evaluable")
                bloque.append(f)
        marcar_alias(bloque)
        _clasificar(bloque, "razon", favorable_si_menor=False)
        filas += bloque
    return filas


UNA_CAPA = {"clientes_pago": "cliente de pago", "shows": "show", "citas": "cita", "cualificados": "lead cualificado",
            "leads": "lead", "resultado_meta": "resultado de Meta", "activaciones": "activación", "pruebas": "prueba"}


def _texto_coste(f: dict, capa: str) -> str:
    return (f"coste por {UNA_CAPA.get(capa, capa)} {_x(f['razon'])}× el del resto (IC 95 % {_x(f['ic'][0])}–"
            f"{_x(f['ic'][1])}; {f['eventos'][0]} frente a {f['eventos'][1]} {rc.NOMBRE_CAPA.get(capa, capa)}; "
            f"{f['anuncios'][0]} anuncios, {f['conceptos']} conceptos)")


def _juntos(f: dict, otras: list[dict]) -> str:
    """Aviso de colinealidad: con qué otros valores va siempre (alias) o casi siempre (Jaccard ≥ 0,8)."""
    partes = []
    if f.get("juntos"):
        partes.append(f"va siempre junto a {', '.join(f['juntos'])}: con estos anuncios no se pueden separar")
    casi = [_etq(o) for o in otras if o is not f and o.get("_ads") and f.get("_ads") and o["elemento"] != f["elemento"]
            and o["estado"] not in ("alias",) and 0.8 <= _jaccard(f["_ads"], o["_ads"]) < 1]
    if casi:
        partes.append(f"coincide en ≥80 % de los anuncios con {', '.join(casi[:3])}")
    return f" ({'; '.join(partes)})" if partes else ""


def sintetizar(coste: list[dict], veredictos: list[dict], atencion: list[dict], anuncios: list[Anuncio],
               capa: str | None) -> dict:
    repetir, probar, dejar = [], [], []
    ya = set()

    def poner_en(lista: list, f: dict, evidencia: str, por: str, otras: list[dict]) -> None:
        if _etq(f) in ya:
            return
        ya.add(_etq(f))
        lista.append({"elemento": _etq(f), "evidencia": evidencia, "por": por + _juntos(f, otras)})

    por_clave = {(f["elemento"], f["valor"]): f for f in coste}
    for f in coste:
        if f["estado"] == "senal-a-favor":
            poner_en(repetir, f, "[EMPIRICAL]", _texto_coste(f, capa), coste)
        elif f["estado"] == "senal-en-contra":
            poner_en(dejar, f, "[EMPIRICAL]", _texto_coste(f, capa), coste)
        elif f["estado"] == "pista-a-favor":
            poner_en(probar, f, "[HYPOTHESIS]", "pista sin confirmar tras corregir por comparaciones múltiples: "
                     + _texto_coste(f, capa), coste)
        elif f["estado"] == "confundido" and f["razon"] < 1 and f["ganadores_con"]:
            poner_en(probar, f, "[HYPOTHESIS]", f"solo aparece en {f['conceptos']} concepto y va con un ganador: "
                     "pruébalo en otro concepto para separar el elemento del concepto", coste)
    for f in veredictos:
        if f["estado"] in ("n-insuficiente", "alias", "sin-diferencia"):
            continue
        par = por_clave.get((f["elemento"], f["valor"]), {})
        texto = (f"{f['ganadores'][0]} de {f['ganadores'][1]} ganadores frente a {f['perdedores'][0]} de "
                 f"{f['perdedores'][1]} perdedores (diferencia {_pct(f['diferencia'], 0)}, IC 95 % "
                 f"{_pct(f['ic'][0], 0)} a {_pct(f['ic'][1], 0)})")
        if f["estado"] == "mas-en-ganadores" and not par.get("estado", "").endswith("en-contra"):
            poner_en(repetir, f, "[EMPIRICAL]", texto, veredictos)
        elif f["estado"] == "mas-en-perdedores" and not par.get("estado", "").endswith("a-favor"):
            poner_en(dejar, f, "[EMPIRICAL]", texto, veredictos)
        elif f["estado"] == "pista-mas-en-ganadores":
            poner_en(probar, f, "[HYPOTHESIS]", f"pista: {texto}", veredictos)
    nombres = {"hook_rate": "hook rate", "hold_rate": "hold rate", "ctr": "CTR"}
    for f in atencion:
        if f["estado"] == "senal-a-favor" and f["metrica"] in ("hook_rate", "hold_rate"):
            poner_en(probar, f, "[HYPOTHESIS]", f"{nombres[f['metrica']]} {_x(f['razon'])}× el del resto (IC 95 % "
                     f"{_x(f['ic'][0])}–{_x(f['ic'][1])}): filtro de atención, confírmalo con la capa de decisión "
                     "(la atención no predice negocio por sí sola: "
                     "meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md)", [x for x in atencion if x["metrica"] == f["metrica"]])
    for el, valores in HUECOS_CLAVE.items():
        vistos = {a.elementos.get(el) for a in anuncios}
        if sum(_conocido(a.elementos.get(el, "")) for a in anuncios) < 3:
            continue
        for v in valores:
            if v not in vistos and f"{el} = {v}" not in ya:
                ya.add(f"{el} = {v}")
                probar.append({"elemento": f"{el} = {v}", "evidencia": "[HYPOTHESIS]",
                               "por": f"no probado en la cuenta y recomendado para este público ({FUENTE_HUECOS})"})
    return {"repetir": repetir, "probar": probar, "dejar": dejar}


def analizar(slug: str, capa: str | None = None, dias_madurez: int | None = None, hoy: date | None = None,
             guardar: bool = False, madurez_cli: list[str] | None = None) -> dict:
    hoy = hoy or date.today()
    ficha = _comun.leer_ficha(slug)
    modelo = rc.modelo_de(ficha.get("tipo", ""))
    madurez = rc.madurez_de(modelo, dias_madurez, madurez_cli)
    anuncios, conteo = cargar_anuncios(slug, hoy)
    if not anuncios:
        raise ErrorUsuario("El registro no tiene anuncios con gasto: actualízalo con el periodo que quieras analizar")
    avisos = [conteo.pop("aviso_fuera")] if "aviso_fuera" in conteo else []
    elegida, validos, descartadas = elegir_capa(anuncios, modelo, madurez, capa)
    sin_dato = sum(a.capas.get(elegida) is None for a in anuncios) if elegida else 0
    inmaduros = len(anuncios) - len(validos) - sin_dato if elegida else 0
    if elegida is None:
        avisos.append("Ninguna capa tiene 20 eventos en anuncios maduros: no hay lectura de coste; solo ganadores "
                      "frente a perdedores y atención")
    elif elegida in rc.CAPAS_SUPERFICIALES:
        avisos.append(f"Se decide con {rc.NOMBRE_CAPA[elegida]}: es una capa superficial; confirma con la de negocio "
                      "cuando haya volumen (meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md §4)")
    if inmaduros:
        sin_fecha = sum(a.edad is None and a.capas.get(elegida) is not None for a in anuncios)
        avisos.append(f"{inmaduros} anuncios con menos de {madurez.get(elegida, 14)} días fuera de la lectura de coste: "
                      f"sus {rc.NOMBRE_CAPA[elegida]} aún no han madurado"
                      + (f" ({sin_fecha} sin fecha fiable: ponles la nomenclatura o actualiza el registro con "
                         "`meta_ads.py anuncios --por-dia`)" if sin_fecha else ""))
    if sin_dato:
        avisos.append(f"{sin_dato} anuncios sin dato de {rc.NOMBRE_CAPA[elegida]} en el registro: fuera de la lectura "
                      "de coste")
    if conteo["sin_etiquetar"]:
        avisos.append(f"{conteo['sin_etiquetar']} anuncios con gasto sin etiquetar: solo cuentan en formato y vía "
                      "(`etiquetas pendientes`)")
    dudas = {el: sum(a.elementos.get(el) == DUDA for a in anuncios) for el in ETIQUETAS}
    muchas = [f"{el} ({n})" for el, n in dudas.items() if n and n >= max(3, len(anuncios) // 4)]
    if muchas:
        avisos.append("Elementos con muchas dudas (pierden casi todo su n): " + ", ".join(muchas))
    coste = lente_coste(validos, elegida) if elegida else []
    veredictos = lente_veredictos(anuncios)
    atencion = lente_atencion(anuncios)
    sintesis = sintetizar(coste, veredictos, atencion, anuncios, elegida)
    resultado = {
        "cliente": slug, "fecha": hoy.isoformat(), "modelo": modelo, "capa_decision": elegida,
        "capas_descartadas": descartadas, "madurez": madurez,
        "anuncios": {"con_gasto": len(anuncios), "en_capa": len(validos), "inmaduros": inmaduros,
                     "sin_dato_capa": sin_dato, **conteo},
        "lectura": "Asociaciones observadas en la cuenta, no causas: el gasto no se reparte al azar y los elementos "
                   "van juntos con el concepto, la oferta y el momento "
                   "(meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md §8.3). "
                   "Para causalidad: /test-creativo.",
        "sintesis": sintesis, "coste": _sin_internos(coste), "ganadores_perdedores": _sin_internos(veredictos),
        "atencion": _sin_internos(atencion),
        "avisos": avisos,
    }
    if guardar:
        resultado["archivo"] = _guardar(slug, hoy, "elementos", resultado)
    return resultado


def _guardar(slug: str, hoy: date, tipo: str, datos: dict) -> str:
    destino = _comun.ruta_cliente(slug) / "datos" / "analisis-creativo" / f"{hoy.isoformat()}_{tipo}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return _rel(destino)


# ================================================================ retención
ALIAS_RETENCION = {
    "ad_id": ["ad id", "identificador del anuncio", "id del anuncio"],
    "nombre": ["anuncio", "ad name", "nombre del anuncio"],
    "impresiones": ["impresiones", "impressions"],
    "vistas_3s": ["vistas 3s", "3 second video plays", "reproducciones de video de 3 segundos*"],
    "thruplay": ["thruplay", "thruplays", "reproducciones de thruplay*"],
    "video_p25": ["video p25", "video plays at 25*", "reproducciones de video hasta el 25*"],
    "video_p50": ["video p50", "video plays at 50*", "reproducciones de video hasta el 50*"],
    "video_p75": ["video p75", "video plays at 75*", "reproducciones de video hasta el 75*"],
    "video_p95": ["video p95", "video plays at 95*", "reproducciones de video hasta el 95*"],
    "video_p100": ["video p100", "video plays at 100*", "reproducciones de video hasta el 100*"],
    "reproducciones": ["reproducciones", "video plays", "reproducciones de video"],
    "tiempo_medio_s": ["tiempo medio s", "video average play time*", "tiempo medio de reproduccion*"],
    "curva": ["curva retencion"],
}
TRAMOS_CURVA = [f"{s} s" for s in range(15)] + ["15–20 s", "20–25 s", "25–30 s", "30–40 s", "40–50 s", "50–60 s",
                                                 "más de 60 s"]


def retencion(slug: str, meta_csv: str, min_impresiones: int = 1000) -> dict:
    filas = rc.leer_csv(meta_csv)
    if not filas:
        raise ErrorUsuario(f"{meta_csv} está vacío")
    m = rc._mapa(list(filas[0].keys()), ALIAS_RETENCION)
    if "ad_id" not in m:
        raise ErrorUsuario("El CSV no tiene ad_id: usa la salida de `meta_ads.py anuncios`")
    avisos = []
    if not any(k in m for k in ("video_p25", "curva")):
        avisos.append("El CSV no trae columnas de retención: vuelve a exportar con `meta_ads.py anuncios` "
                      "(versión con retención) o con las columnas de reproducciones al 25/50/75/95/100 %")
    etiquetas, _ = leer_elementos(slug)
    por_ad: dict[str, dict] = {}
    redondeados = 0
    for f in filas:
        ad = (f.get(m["ad_id"]) or "").strip()
        if not re.fullmatch(r"\d{5,25}", ad):
            redondeados += rc.id_redondeado(ad)
            continue
        d = por_ad.setdefault(ad, {"ad_id": ad, "nombre": "", "curvas": [], "tiempo": []} |
                              {k: 0.0 for k in ALIAS_RETENCION if k not in ("ad_id", "nombre", "curva",
                                                                            "tiempo_medio_s")})
        if "nombre" in m and (f.get(m["nombre"]) or "").strip():
            d["nombre"] = f[m["nombre"]].strip()
        for k in d:
            if k in m and k not in ("ad_id", "nombre", "curvas", "tiempo"):
                d[k] += rc.num(f.get(m[k]), entero=True) or 0
        plays = rc.num(f.get(m["reproducciones"]), entero=True) if "reproducciones" in m else None
        peso = plays or rc.num(f.get(m["vistas_3s"]), entero=True) if "vistas_3s" in m else plays
        if "tiempo_medio_s" in m and (t := rc.num(f.get(m["tiempo_medio_s"]))) is not None:
            d["tiempo"].append((t, peso or 1))
        if "curva" in m and (f.get(m["curva"]) or "").strip():
            valores = [rc.num(x) for x in f[m["curva"]].split("|")]
            if valores and all(v is not None for v in valores):
                d["curvas"].append((valores, peso or 1))
    if redondeados:
        raise ErrorUsuario(rc.aviso_id_redondeado(redondeados))
    salida = []
    for ad, d in por_ad.items():
        if d["impresiones"] < min_impresiones or d["vistas_3s"] <= 0:
            continue
        v3 = d["vistas_3s"]
        dur = _num(etiquetas.get(ad, {}).get("duracion_s"))
        x = {"ad_id": ad, "nombre": d["nombre"], "impresiones": int(d["impresiones"]),
             "hook_rate": v3 / d["impresiones"], "hold_rate": d["thruplay"] / v3 if d["thruplay"] else None,
             "duracion_s": dur, "hold_inflado": dur is not None and dur <= 15,
             "retencion": {f"p{q}": d[f"video_p{q}"] / v3 for q in (25, 50, 75, 95, 100) if d[f"video_p{q}"]}}
        if dur:
            x["segundo_de_cada_cuartil"] = {f"p{q}": round(dur * q / 100, 1) for q in (25, 50, 75, 95, 100)}
        if d["tiempo"]:
            x["tiempo_medio_s"] = sum(t * w for t, w in d["tiempo"]) / sum(w for _, w in d["tiempo"])
        if d["curvas"]:
            largo = min(len(c) for c, _ in d["curvas"])
            total = sum(w for _, w in d["curvas"])
            curva = [sum(c[i] * w for c, w in d["curvas"]) / total for i in range(largo)]
            x["curva"] = [round(v, 1) for v in curva]
            caidas = [(curva[i] - curva[i + 1], i) for i in range(min(largo - 1, 14))]
            if caidas:
                caida, i = max(caidas)
                x["mayor_caida"] = {"entre": f"{TRAMOS_CURVA[i]} y {TRAMOS_CURVA[i + 1]}", "puntos": round(caida, 1)}
        salida.append(x)
    if not salida:
        raise ErrorUsuario(f"Ningún anuncio de vídeo con ≥{min_impresiones} impresiones y vistas de 3 s en el CSV")
    mediana = statistics.median(x["hook_rate"] for x in salida)
    holds = [x["hold_rate"] for x in salida if x["hold_rate"] is not None and not x["hold_inflado"]]
    mediana_hold = statistics.median(holds) if len(holds) >= 3 else None
    for x in salida:
        x["hook_vs_mediana"] = x["hook_rate"] / mediana if mediana else None
        x["diagnostico"] = _diagnostico_retencion(x, mediana, mediana_hold)
    if len(salida) < 5:
        avisos.append(f"Solo {len(salida)} vídeos con impresiones suficientes: la mediana de la cuenta es poco estable")
    salida.sort(key=lambda x: -x["impresiones"])
    if any(x["hold_inflado"] for x in salida):
        avisos.append("Hay vídeos de ≤15 s: su hold rate está inflado por la definición de ThruPlay; compáralos por "
                      "retención a los mismos segundos, no por hold rate (KB 03/07 §2)")
    if not any(x["duracion_s"] for x in salida):
        avisos.append("Sin duración de los vídeos: pásalos por `fotogramas` para saber en qué segundo cae cada "
                      "cuartil y si el hold está inflado")
    return {"cliente": slug, "archivo": _rel(pathlib.Path(meta_csv)), "anuncios": salida,
            "mediana_hook_rate": mediana, "mediana_hold_rate": mediana_hold, "avisos": avisos,
            "lectura": "Compara contra la mediana de esta cuenta y, si mezclas ubicaciones o públicos fríos y "
                       "calientes, sepáralos antes (03/07 §5). La retención por cuartiles solo se compara entre vídeos "
                       "de duración parecida: el 25 % de un vídeo de 12 s es el segundo 3; el de uno de 60 s, el 15.",
            "formulas": {"hook_rate": "vistas de 3 s / impresiones", "hold_rate": "ThruPlays / vistas de 3 s",
                         "retencion_pXX": "reproducciones hasta el XX % / vistas de 3 s"}}


def _diagnostico_retencion(x: dict, med_hook: float, med_hold: float | None) -> str:
    """Rama de vídeo del árbol de meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md §4, contra las medianas
    de la propia cuenta (§5). Corte de apertura: < 50 % de la mediana (13/05 §5); el de cuerpo, igual [HYPOTHESIS]."""
    if med_hook and x["hook_rate"] < 0.5 * med_hook:
        return "apertura: hook rate < 50 % de la mediana de la cuenta → itera los 3 primeros segundos"
    hold = x.get("hold_rate")
    if hold is not None and not x["hold_inflado"] and med_hold and hold < 0.5 * med_hold:
        return "cuerpo: el gancho retiene, pero el hold rate es < 50 % de la mediana → guion o ritmo tras el gancho"
    return "sin alerta de vídeo: si no convierte, sigue el árbol por CTR, promesa, oferta y landing (03/07 §4)"


# ================================================================ diversidad
def similitud_concepto(a: dict, b: dict) -> tuple[float | None, float]:
    """Similitud de Gower ponderada sobre las dimensiones de concepto conocidas en los dos anuncios."""
    num_, den = 0.0, 0.0
    for dim, peso in PESOS_CONCEPTO.items():
        va, vb = a.get(dim, ""), b.get(dim, "")
        if _conocido(va) and _conocido(vb):
            den += peso
            num_ += peso * (va == vb)
    return (num_ / den if den >= PESO_MINIMO else None), den


class _Uniones:
    def __init__(self, n: int):
        self.padre = list(range(n))

    def raiz(self, i: int) -> int:
        while self.padre[i] != i:
            self.padre[i] = self.padre[self.padre[i]]
            i = self.padre[i]
        return i

    def une(self, i: int, j: int) -> None:
        self.padre[self.raiz(i)] = self.raiz(j)


def _soporte(a: Anuncio) -> str:
    s = a.elementos.get("soporte", "")
    return s if _conocido(s) else soporte_por_formato(a.elementos.get("formato", ""))


def _grupos(anuncios: list[Anuncio], umbral: float, umbral_visual: int) -> tuple[list[list[int]], dict]:
    """Un mismo ángulo y concepto con otro soporte (vídeo frente a estático) no se une por el nombre: el formato es
    una dimensión de diversidad (03/01 §4.1). Sí puede unirse por etiquetas o por huella."""
    dims = []
    for a in anuncios:
        d = dict(a.elementos)
        d["angulo"] = a.concepto.split("/")[0] if "/" in a.concepto else ""
        dims.append(d)
    u = _Uniones(len(anuncios))
    motivos: dict[tuple[int, int], list[str]] = defaultdict(list)
    for i in range(len(anuncios)):
        for j in range(i + 1, len(anuncios)):
            a, b = anuncios[i], anuncios[j]
            sa, sb = _soporte(a), _soporte(b)
            if a.concepto == b.concepto and not a.concepto.startswith("ad:") and (not sa or not sb or sa == sb):
                motivos[(i, j)].append("mismo ángulo y concepto en el nombre (y mismo soporte)")
            sim, _ = similitud_concepto(dims[i], dims[j])
            if sim is not None and sim >= umbral:
                motivos[(i, j)].append(f"etiquetas de concepto iguales al {_pct(sim, 0)}")
            if a.huella and b.huella:
                dist = distancia_hamming(a.huella, b.huella)
                if dist is not None and dist <= umbral_visual:
                    motivos[(i, j)].append(f"primer fotograma casi idéntico ({dist}/64 bits)")
            if motivos.get((i, j)):
                u.une(i, j)
    grupos: dict[int, list[int]] = defaultdict(list)
    for i in range(len(anuncios)):
        grupos[u.raiz(i)].append(i)
    return list(grupos.values()), motivos


def _resumen_grupos(anuncios: list[Anuncio], grupos: list[list[int]], motivos: dict) -> dict:
    gasto_total = sum(a.gasto for a in anuncios) or 1.0
    salida = []
    for g in sorted(grupos, key=lambda g: -sum(anuncios[i].gasto for i in g)):
        razones = sorted({m for (i, j), ms in motivos.items() if i in g and j in g for m in ms})
        salida.append({"anuncios": [{"ad_id": anuncios[i].ad_id, "nombre": anuncios[i].nombre,
                                     "gasto": round(anuncios[i].gasto, 2)} for i in g],
                       "conceptos_en_nombre": sorted({anuncios[i].concepto for i in g}),
                       "cuota_gasto": sum(anuncios[i].gasto for i in g) / gasto_total, "motivos": razones})
    cuotas = [x["cuota_gasto"] for x in salida]
    efectivos = 1 / sum(c * c for c in cuotas) if cuotas else 0.0
    gastos = sorted((a.gasto for a in anuncios), reverse=True)
    return {"anuncios": len(anuncios), "grupos": len(salida), "conceptos_efectivos": efectivos,
            "cuota_top1": gastos[0] / gasto_total if gastos else 0.0,
            "cuota_top2": sum(gastos[:2]) / gasto_total if gastos else 0.0, "detalle": salida}


def diversidad(slug: str, umbral: float = UMBRAL_CONCEPTO, umbral_visual: int = UMBRAL_VISUAL, todos: bool = False,
               hoy: date | None = None, guardar: bool = False) -> dict:
    hoy = hoy or date.today()
    _comun.leer_ficha(slug)
    anuncios, conteo = cargar_anuncios(slug, hoy, todos=todos)
    if not anuncios:
        raise ErrorUsuario("No hay anuncios con gasto en el registro")
    grupos, motivos = _grupos(anuncios, umbral, umbral_visual)
    cuenta = _resumen_grupos(anuncios, grupos, motivos)
    por_conjunto = {}
    for conjunto in sorted({a.conjunto for a in anuncios if a.conjunto}):
        sub = [a for a in anuncios if a.conjunto == conjunto]
        if len(sub) >= 2:
            g, m = _grupos(sub, umbral, umbral_visual)
            r = _resumen_grupos(sub, g, m)
            por_conjunto[conjunto] = {k: r[k] for k in ("anuncios", "grupos", "conceptos_efectivos", "cuota_top2")}
    sin_variedad = []
    gasto_total = sum(a.gasto for a in anuncios) or 1.0
    for dim in ("quien_habla", "estructura", "consciencia", "soporte", "primer_fotograma", "audiencia_nombrada",
                "persona"):
        reparto = Counter()
        for a in anuncios:
            if _conocido(a.elementos.get(dim, "")):
                reparto[a.elementos[dim]] += a.gasto
        etiquetado = sum(reparto.values())
        if etiquetado >= 0.5 * gasto_total and reparto:
            valor, g = reparto.most_common(1)[0]
            if g / etiquetado >= 0.8:
                sin_variedad.append({"dimension": dim, "valor": valor, "cuota": g / etiquetado})
    avisos = []
    # El umbral de la KB es por conjunto; si el registro no trae conjuntos, se aplica a la cuenta.
    concentrados = {c: x["cuota_top2"] for c, x in por_conjunto.items() if x["anuncios"] >= 3 and x["cuota_top2"] > 0.8}
    if not por_conjunto and cuenta["anuncios"] >= 3 and cuenta["cuota_top2"] > 0.8:
        concentrados = {"(cuenta)": cuenta["cuota_top2"]}
    for conjunto, cuota in concentrados.items():
        avisos.append(f"{conjunto}: los 2 anuncios con más gasto se llevan el {_pct(cuota, 0)}. Si dura 2–3 semanas y "
                      "suben coste y frecuencia, toca meter conceptos nuevos, no variaciones (umbral orientativo "
                      "[HYPOTHESIS], meta-ads-kb/03-creatividad/01-creative-es-targeting.md, implicaciones operativas)")
    if conteo["sin_etiquetar"]:
        avisos.append(f"{conteo['sin_etiquetar']} anuncios sin etiquetar: solo se comparan por nombre y huella visual")
    if not any(a.huella for a in anuncios):
        avisos.append("Sin huellas visuales: pasa `fotogramas` para comparar primeros fotogramas")
    else:
        fuentes = {(e or {}).get("fuente_visual") for e in leer_elementos(slug)[0].values()} - {"", None}
        if "api-miniatura" in fuentes and len(fuentes) > 1:
            avisos.append("Huellas de fuentes distintas (primer fotograma real y miniatura de Meta, que no siempre es "
                          "el fotograma 0): una distancia alta entre ellas no descarta que sean el mismo anuncio")
    resultado = {"cliente": slug, "fecha": hoy.isoformat(), "cuenta": cuenta, "por_conjunto": por_conjunto,
                 "dimensiones_sin_variedad": sin_variedad, "avisos": avisos,
                 "umbrales": {"concepto": umbral, "visual_bits": umbral_visual, "evidencia": "[HYPOTHESIS]"},
                 "lectura": "Meta dice que los creativos demasiado parecidos pueden no tratarse como distintos "
                            "[OFFICIAL META]; el mecanismo exacto («Entity ID») y cualquier umbral no son oficiales "
                            "[HYPOTHESIS]. No pauses ganadores para subir la diversidad: los conceptos nuevos tienen "
                            "que diferir en las dimensiones sin variedad."}
    if guardar:
        resultado["archivo"] = _guardar(slug, hoy, "diversidad", resultado)
    return resultado


# ================================================================ suministro
EVENTO_A_CAPA = rc.CAPA_DE_EVENTO  # una sola tabla evento → capa (registro_creativo.capa_de_evento)
# Anuncios nuevos por semana (conceptos o iteraciones) según gasto diario: meta-ads-kb/13-sistema-operativo/
# 05-framework-testing-creativo.md §3 (orientativo).
TECHO_SEMANAL = ((100, 2, 4), (500, 4, 8), (5000, 8, 20), (math.inf, 20, 50))
SEMANAS_MES = 30.4 / 7


def _gasto_de_meta(meta_csv: str) -> tuple[float, int]:
    filas = rc.leer_csv(meta_csv)
    agregado = rc.agregar_meta(filas)
    gasto = sum(d["gasto"] for d in agregado.values())
    m = rc._mapa(list(filas[0].keys()) if filas else [], {"desde": ["desde", "date start"],
                                                          "hasta": ["hasta", "date stop"]})
    fechas = []
    for f in filas:
        for k in ("desde", "hasta"):
            if k in m and re.fullmatch(r"\d{4}-\d{2}-\d{2}", (f.get(m[k]) or "")[:10]):
                fechas.append(date.fromisoformat(f[m[k]][:10]))
    if not fechas:
        raise ErrorUsuario(f"{meta_csv} no trae fechas (desde/hasta): pasa --gasto-mensual")
    return gasto, (max(fechas) - min(fechas)).days + 1


def suministro(slug: str, gasto_mensual: float | None = None, gasto_diario: float | None = None,
               meta_csv: str | None = None, coste_objetivo: float | None = None, capa: str | None = None,
               hoy: date | None = None, guardar: bool = False) -> dict:
    hoy = hoy or date.today()
    ficha = _comun.leer_ficha(slug)
    dir_c = _comun.ruta_cliente(slug)
    avisos, origen = [], {}
    if gasto_mensual:
        origen["gasto"] = "--gasto-mensual"
    elif gasto_diario:
        gasto_mensual, origen["gasto"] = gasto_diario * 30.4, "--gasto-diario × 30,4"
    elif meta_csv:
        g, dias = _gasto_de_meta(meta_csv)
        gasto_mensual, origen["gasto"] = g / dias * 30.4, f"media diaria de {_rel(pathlib.Path(meta_csv))} ({dias} días)"
    else:
        tope = _num((ficha.get("topes") or {}).get("total_dia")) or 0
        if tope <= 0:
            raise ErrorUsuario("Falta el gasto: pasa --gasto-mensual, --gasto-diario o --meta <csv>")
        gasto_mensual, origen["gasto"] = tope * 30.4, "tope total diario de la ficha × 30,4 (es un máximo)"
        avisos.append("Gasto estimado con el tope total diario de la ficha: es el máximo, no lo que gastas")
    if gasto_mensual <= 0:
        raise ErrorUsuario("El gasto mensual tiene que ser > 0")
    bruto = ficha.get("explorar_explotar", 0.3)
    explorar = _comun.numero(bruto)
    if explorar is None:
        raise ErrorUsuario(f"explorar_explotar de la ficha no es un número ({bruto!r}): ponlo entre 0 y 1 (0.3 = 30 % "
                           "para conceptos nuevos)")
    if not 0 < explorar < 1:
        raise ErrorUsuario("explorar_explotar de la ficha va entre 0 y 1 (0.3 = 30 % para conceptos nuevos)")
    capa = capa or rc.capa_de_evento(str((ficha.get("meta") or {}).get("evento_principal") or "lead")) or "leads"
    if capa not in set().union(*rc.CAPAS.values()):
        raise ErrorUsuario(f"--capa {capa} no válida")
    if not coste_objetivo:
        objetivos = rc.objetivos_ficha((dir_c / "ficha.md").read_text(encoding="utf-8"))
        if capa in objetivos:
            coste_objetivo, origen["coste"] = objetivos[capa], "Target de la tabla «Economía» de la ficha"
        else:
            try:
                registro = leer_registro(slug)
            except ErrorUsuario:
                registro = []
            con_dato = [r for r in registro if (_num(r.get("gasto")) or 0) > 0 and _num(r.get(capa)) is not None]
            eventos = sum(_num(r.get(capa)) for r in con_dato)
            gasto = sum(_num(r.get("gasto")) for r in con_dato)
            if eventos >= rc.N_DECIDIR:
                coste_objetivo, origen["coste"] = gasto / eventos, "coste medio de la cuenta en el registro"
                avisos.append("Sin target en la ficha: uso el coste medio de la cuenta. Fíjalo con /economia")
            else:
                raise ErrorUsuario(f"No sé el coste objetivo de {rc.NOMBRE_CAPA.get(capa, capa)}: ponlo en la tabla "
                                   "«Economía» de la ficha (/economia) o pásalo con --coste-objetivo")
    else:
        origen["coste"] = "--coste-objetivo"
    presupuesto = gasto_mensual * explorar
    prudente, optimista = presupuesto / (3 * coste_objetivo), presupuesto / (2 * coste_objetivo)
    central = presupuesto / (2.5 * coste_objetivo)
    diario = gasto_mensual / 30.4
    _, lo_s, hi_s = next(t for t in TECHO_SEMANAL if diario < t[0])
    techo = (round(lo_s * SEMANAS_MES), round(hi_s * SEMANAS_MES))
    try:
        registro, fuera, exp = registro_vigente(slug)
    except ErrorUsuario:
        registro, fuera, exp = [], 0, None
    if fuera:
        avisos.append(_aviso_fuera(fuera, exp))
    ganadores = [r for r in registro if (r.get("veredicto") or "") == "ganador"]
    # Las 3–5 iteraciones se hacen una vez por ganador nuevo, no cada mes: cuento los de los últimos 30 días.
    recientes = []
    for r in ganadores:
        try:
            if 0 <= (hoy - date.fromisoformat((r.get("fecha_veredicto") or "")[:10])).days <= 30:
                recientes.append(r)
        except ValueError:
            continue
    sin_fecha = not recientes and ganadores and not any((r.get("fecha_veredicto") or "").strip() for r in ganadores)
    if sin_fecha:
        recientes = ganadores
        avisos.append("Los ganadores del registro no tienen fecha_veredicto: cuento todos como nuevos para las "
                      "iteraciones; descuenta los que ya iteraste")
    efectivos = None
    if registro:
        try:
            efectivos = diversidad(slug, hoy=hoy)["cuenta"]["conceptos_efectivos"]
        except ErrorUsuario:
            efectivos = None
    if prudente < 1:
        cada = math.ceil(1 / prudente) if prudente > 0 else None
        recomendado = f"1 concepto nuevo cada {cada} meses" if cada else "ninguno con este gasto"
        avisos.append("El presupuesto de exploración no llega para evaluar un concepto al mes con gasto garantizado "
                      "(2–3× el coste objetivo): acepta decisiones más lentas, sube explorar_explotar o usa el filtro "
                      "de atención (KB 13/05 §5, primera fila) para descartar antes; no lances más conceptos de los "
                      "que puedes leer")
    else:
        n = math.floor(prudente)
        recomendado = f"{n} concepto{'s' if n > 1 else ''} nuevo{'s' if n > 1 else ''} al mes"
    iteraciones = (3 * len(recientes), 5 * len(recientes))
    if not ganadores and explorar < 0.7:
        avisos.append(f"Sin ganadores en el registro: la KB sugiere 70–90 % de conceptos nuevos (meta-ads-kb/"
                      f"03-creatividad/13-produccion-y-feedback-loop-creativo.md §4.3) y tu ficha dice "
                      f"{_pct(explorar, 0)}: valora subir explorar_explotar")
    if efectivos is not None and efectivos < 3:
        avisos.append(f"La cuenta equivale a {efectivos:.1f} conceptos efectivos por gasto: prioriza conceptos "
                      "nuevos de verdad (otro ángulo, persona, portavoz o estructura), no variantes")
    if math.floor(prudente) + iteraciones[0] > techo[1]:
        avisos.append(f"Conceptos más iteraciones superan el techo orientativo de {techo[1]} anuncios nuevos al mes "
                      "para tu gasto (KB 13/05 §3): recorta iteraciones")
    resultado = {
        "cliente": slug, "fecha": hoy.isoformat(), "moneda": ficha.get("moneda", "EUR"),
        "gasto_mensual": round(gasto_mensual, 2), "explorar_explotar": explorar,
        "presupuesto_exploracion_mes": round(presupuesto, 2), "capa": capa, "coste_objetivo": round(coste_objetivo, 2),
        "origen": origen,
        "conceptos_nuevos_mes": {"prudente_3x": round(prudente, 1), "central_2_5x": round(central, 1),
                                 "optimista_2x": round(optimista, 1)},
        "conceptos_nuevos_semana": {"prudente_3x": round(prudente / SEMANAS_MES, 1),
                                    "optimista_2x": round(optimista / SEMANAS_MES, 1)},
        "recomendado": recomendado, "ganadores_activos": len(ganadores), "ganadores_nuevos_30d": len(recientes),
        "iteraciones_mes": {"minimo": iteraciones[0], "maximo": iteraciones[1],
                            "regla": "3–5 iteraciones (hooks, formatos, personas) por ganador nuevo, una vez "
                                     "(KB 13/05 §7); no cuentan como conceptos"},
        "techo_anuncios_nuevos_mes": {"minimo": techo[0], "maximo": techo[1], "gasto_diario": round(diario, 2)},
        "conceptos_efectivos": round(efectivos, 2) if efectivos is not None else None,
        "formula": "conceptos/mes = gasto mensual × explorar_explotar ÷ (2–3 × coste objetivo) [STRONG INFERENCE] "
                   "(meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md; el playbook de consultoras "
                   "de IA §8.6 usa 2,5×); explorar_explotar [HYPOTHESIS]",
        "avisos": avisos,
    }
    if guardar:
        resultado["archivo"] = _guardar(slug, hoy, "suministro", resultado)
    return resultado


# ================================================================ salida en texto
NOMBRE_ESTADO = {"senal-a-favor": "señal a favor", "senal-en-contra": "señal en contra", "pista-a-favor": "pista a favor",
                 "pista-en-contra": "pista en contra", "sin-diferencia": "sin diferencia distinguible",
                 "n-insuficiente": "n insuficiente", "confundido": "confundido con el concepto",
                 "mas-en-ganadores": "más en ganadores", "mas-en-perdedores": "más en perdedores",
                 "pista-mas-en-ganadores": "pista: más en ganadores", "pista-mas-en-perdedores": "pista: más en perdedores",
                 "alias": "los mismos anuncios que otro valor"}


def _estado(f: dict) -> str:
    return f"igual que {f['alias_de']} (mismos anuncios)" if f["estado"] == "alias" else NOMBRE_ESTADO[f["estado"]]


def _imprimir_analisis(r: dict) -> None:
    capa = r["capa_decision"]
    print(f"Elementos creativos · {r['cliente']} ({r['modelo']}) · {r['fecha']}")
    n = r["anuncios"]
    print(f"- Capa de decisión: {rc.NOMBRE_CAPA.get(capa, 'ninguna con n suficiente')}"
          + (f" ({n['en_capa']} anuncios)" if capa else "")
          + "".join(f" · descartada {rc.NOMBRE_CAPA.get(d['capa'], d['capa'])} ({d['eventos']} eventos)"
                    for d in r["capas_descartadas"]))
    print(f"- Anuncios con gasto: {n['con_gasto']} · etiquetados {n['etiquetados']} · sin etiquetar {n['sin_etiquetar']}")
    print(f"- {r['lectura']}\n")
    for titulo, clave in (("Qué repetir", "repetir"), ("Qué probar", "probar"), ("Qué dejar", "dejar")):
        print(titulo)
        for x in r["sintesis"][clave] or [{"elemento": "—", "evidencia": "", "por": "nada con evidencia suficiente"}]:
            print(f"- {x['elemento']}: {x['por']} {x['evidencia']}".rstrip())
        print()
    if r["coste"]:
        print(f"Detalle de coste ({rc.NOMBRE_CAPA[capa]}): valor · anuncios con/sin · eventos con/sin · razón de costes "
              "[IC 95 %] · q · estado")
        actual = None
        for f in r["coste"]:
            if f["elemento"] != actual:
                actual = f["elemento"]
                print(f"  {actual}")
            q = (f" · q {'<0,01' if f['q'] < 0.005 else _x(f['q'])}") if "q" in f else ""
            print(f"    {f['valor']:<18} {f['anuncios'][0]}/{f['anuncios'][1]} · {f['eventos'][0]}/{f['eventos'][1]} · "
                  f"{_x(f['razon'])}× [{_x(f['ic'][0])}–{_x(f['ic'][1])}]{q} · {_estado(f)}")
        print()
    evaluables = [f for f in r["ganadores_perdedores"] if f["estado"] != "n-insuficiente"]
    if evaluables:
        print("Ganadores frente a perdedores: valor · ganadores con · perdedores con · diferencia [IC 95 %] · p de "
              "Fisher · estado")
        for f in evaluables:
            print(f"  {f['elemento']} = {f['valor']}: {f['ganadores'][0]}/{f['ganadores'][1]} · "
                  f"{f['perdedores'][0]}/{f['perdedores'][1]} · {_pct(f['diferencia'], 0)} "
                  f"[{_pct(f['ic'][0], 0)} a {_pct(f['ic'][1], 0)}] · p {_x(f['p'], 3)} · {_estado(f)}")
        print()
    senales = [f for f in r["atencion"] if f["estado"].startswith(("senal", "pista"))]
    if senales:
        print("Atención (diagnóstico; no decide): métrica · valor · tasa con/sin · razón [IC 95 %] · estado")
        for f in senales:
            print(f"  {f['metrica']} · {f['elemento']} = {f['valor']}: {_pct(f['tasa'][0])} / {_pct(f['tasa'][1])} · "
                  f"{_x(f['razon'])}× [{_x(f['ic'][0])}–{_x(f['ic'][1])}] · {_estado(f)}")
        print()
    for a in r["avisos"]:
        print(f"Aviso: {a}")
    if r.get("archivo"):
        print(f"Archivo: {r['archivo']}")


def _imprimir_diversidad(r: dict) -> None:
    c = r["cuenta"]
    print(f"Diversidad de conceptos · {r['cliente']} · {r['fecha']}")
    print(f"- {c['anuncios']} anuncios con gasto → {c['grupos']} grupos · {_x(c['conceptos_efectivos'], 1)} conceptos "
          f"efectivos por gasto · top 1 {_pct(c['cuota_top1'], 0)} · top 2 {_pct(c['cuota_top2'], 0)} del gasto")
    print(f"- {r['lectura']}\n")
    for i, g in enumerate(c["detalle"], start=1):
        if len(g["anuncios"]) < 2:
            continue
        print(f"Grupo {i} ({_pct(g['cuota_gasto'], 0)} del gasto): {', '.join(g['motivos'])}")
        for a in g["anuncios"]:
            print(f"  - {a['ad_id']} · {a['nombre']} · {_euros(a['gasto'])}")
    sueltos = sum(1 for g in c["detalle"] if len(g["anuncios"]) == 1)
    print(f"\n{sueltos} anuncios son conceptos sin duplicado.")
    for conjunto, x in r["por_conjunto"].items():
        print(f"- Conjunto {conjunto}: {x['anuncios']} anuncios → {_x(x['conceptos_efectivos'], 1)} conceptos efectivos")
    for d in r["dimensiones_sin_variedad"]:
        print(f"- Sin variedad en {d['dimension']}: {d['valor']} se lleva el {_pct(d['cuota'], 0)} del gasto etiquetado")
    for a in r["avisos"]:
        print(f"Aviso: {a}")
    if r.get("archivo"):
        print(f"Archivo: {r['archivo']}")


def _imprimir_suministro(r: dict) -> None:
    m = r["moneda"]
    print(f"Plan de suministro creativo · {r['cliente']} · {r['fecha']}")
    print(f"- Gasto mensual {_euros(r['gasto_mensual'])} {m} ({r['origen']['gasto']}) × explorar_explotar "
          f"{_pct(r['explorar_explotar'], 0)} = {_euros(r['presupuesto_exploracion_mes'])} {m} para conceptos nuevos")
    print(f"- Coste objetivo por {UNA_CAPA.get(r['capa'], r['capa'])}: {_euros(r['coste_objetivo'])} {m} "
          f"({r['origen']['coste']})")
    c, s = r["conceptos_nuevos_mes"], r["conceptos_nuevos_semana"]
    print(f"- Conceptos nuevos evaluables al mes: {_x(c['prudente_3x'], 1)} con 3× (prudente) · "
          f"{_x(c['central_2_5x'], 1)} con 2,5× · {_x(c['optimista_2x'], 1)} con 2× → "
          f"{_x(s['prudente_3x'], 1)}–{_x(s['optimista_2x'], 1)} por semana")
    print(f"- Recomendado: {r['recomendado']}")
    it = r["iteraciones_mes"]
    print(f"- Iteraciones este mes: {it['minimo']}–{it['maximo']} ({r['ganadores_nuevos_30d']} ganadores nuevos en 30 "
          f"días de {r['ganadores_activos']} con gasto; {it['regla']})")
    t = r["techo_anuncios_nuevos_mes"]
    print(f"- Techo orientativo para {_euros(t['gasto_diario'])} {m}/día: {t['minimo']}–{t['maximo']} anuncios nuevos "
          "al mes (KB 13/05 §3)")
    if r["conceptos_efectivos"] is not None:
        print(f"- Conceptos efectivos hoy: {_x(r['conceptos_efectivos'], 1)}")
    print(f"- {r['formula']}")
    for a in r["avisos"]:
        print(f"Aviso: {a}")
    if r.get("archivo"):
        print(f"Archivo: {r['archivo']}")


def _imprimir_retencion(r: dict) -> None:
    print(f"Retención de vídeo · {r['cliente']} · {r['archivo']} · mediana de hook rate {_pct(r['mediana_hook_rate'])}"
          f" · de hold rate {_pct(r['mediana_hold_rate'])}")
    print(f"- {r['lectura']}")
    for x in r["anuncios"]:
        ret = " · ".join(f"{k} {_pct(v, 0)}" for k, v in x["retencion"].items())
        print(f"- {x['ad_id']} · {x['nombre'][:60]}")
        print(f"    hook {_pct(x['hook_rate'])} ({_x(x['hook_vs_mediana'])}× mediana) · hold "
              f"{_pct(x['hold_rate'])}{' (inflado: ≤15 s)' if x['hold_inflado'] else ''} · {ret or 'sin cuartiles'}"
              + (f" · tiempo medio {_x(x['tiempo_medio_s'], 1)} s" if x.get("tiempo_medio_s") else ""))
        if x.get("mayor_caida"):
            print(f"    mayor caída de la curva: entre {x['mayor_caida']['entre']} (−{_x(x['mayor_caida']['puntos'], 1)} "
                  "puntos)")
        print(f"    → {x['diagnostico']}")
    for a in r["avisos"]:
        print(f"Aviso: {a}")


# ================================================================ CLI
class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def _parser() -> argparse.ArgumentParser:
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--json", action="store_true", help="salida en JSON")
    cliente = argparse.ArgumentParser(add_help=False)
    cliente.add_argument("--cliente", required=True, help="slug del cliente")
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=_Parser)

    f = sub.add_parser("fotogramas", parents=[comunes, cliente], help="fotogramas clave para que un agente los mire")
    f.add_argument("--ad", action="append", help="ad_id (repetible); por defecto, los de más gasto del registro")
    f.add_argument("--video", help="ruta de un vídeo o imagen local (con un solo --ad)")
    f.add_argument("--api", action="store_true", help="si no hay archivo local, miniatura y duración desde Meta")
    f.add_argument("--descargar-video", action="store_true", help="con --api, descarga el vídeo entero (temporal)")
    f.add_argument("--cuadricula", action="store_true", help="monta la prueba de la cuadrícula con los primeros fotogramas")
    f.add_argument("--max", type=int, default=30, help="anuncios como máximo sin --ad (por gasto)")
    f.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy)")

    e = sub.add_parser("etiquetas", help="esquema fijo y archivo elementos-creativos.csv")
    es = e.add_subparsers(dest="accion", required=True, parser_class=_Parser)
    es.add_parser("esquema", parents=[comunes], help="columnas, valores y definiciones")
    p = es.add_parser("preparar", parents=[comunes, cliente], help="una fila por anuncio con gasto")
    p.add_argument("--todos", action="store_true", help="también los anuncios sin gasto en la última exportación")
    p = es.add_parser("pendientes", parents=[comunes, cliente], help="anuncios sin etiquetar, por gasto")
    p.add_argument("--todos", action="store_true")
    p = es.add_parser("poner", parents=[comunes, cliente], help="escribe etiquetas validadas")
    p.add_argument("--ad", help="ad_id")
    p.add_argument("pares", nargs="*", metavar="campo=valor")
    p.add_argument("--archivo", help="JSON: lista de objetos con ad_id y etiquetas, u objeto ad_id → etiquetas")
    p.add_argument("--por", default="", help="quién etiqueta (critico-creativo, usuario…)")
    p.add_argument("--fecha", help="AAAA-MM-DD")
    es.add_parser("validar", parents=[comunes, cliente], help="comprueba cabecera, valores y duplicados")

    a = sub.add_parser("analizar", parents=[comunes, cliente], help="qué elementos se asocian a ganar")
    a.add_argument("--capa", help="fuerza la capa de decisión (p. ej. citas)")
    a.add_argument("--madurez", action="append", default=[], metavar="CAPA=DÍAS",
                   help="días que tarda en madurar una capa (clientes_pago=42); por defecto, los de registro_creativo")
    a.add_argument("--dias-madurez", type=int, default=None,
                   help="los mismos días para todas las capas de negocio (antiguo; mejor --madurez)")
    a.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy)")
    a.add_argument("--guardar", action="store_true", help="guarda el JSON en datos/analisis-creativo/")

    r = sub.add_parser("retencion", parents=[comunes, cliente], help="retención de vídeo por anuncio")
    r.add_argument("--meta", required=True, help="CSV de `meta_ads.py anuncios`")
    r.add_argument("--min-impresiones", type=int, default=1000)

    d = sub.add_parser("diversidad", parents=[comunes, cliente], help="conceptos casi iguales en la cuenta")
    d.add_argument("--umbral", type=float, default=UMBRAL_CONCEPTO)
    d.add_argument("--umbral-visual", type=int, default=UMBRAL_VISUAL)
    d.add_argument("--todos", action="store_true", help="también anuncios sin gasto en la última exportación")
    d.add_argument("--fecha")
    d.add_argument("--guardar", action="store_true")

    s = sub.add_parser("suministro", parents=[comunes, cliente], help="cuántos conceptos nuevos al mes")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--gasto-mensual", type=float)
    g.add_argument("--gasto-diario", type=float)
    g.add_argument("--meta", help="CSV de `meta_ads.py anuncios` (gasto medio diario del periodo)")
    s.add_argument("--coste-objetivo", type=float, help="coste objetivo del evento que se optimiza")
    s.add_argument("--capa", help="capa del coste objetivo (por defecto, la del evento principal de la ficha)")
    s.add_argument("--fecha")
    s.add_argument("--guardar", action="store_true")
    return ap


def _pares(lista: list[str]) -> dict:
    out = {}
    for par in lista:
        if "=" not in par:
            raise ErrorUsuario(f"Las etiquetas van como campo=valor: {par!r}")
        k, v = par.split("=", 1)
        out[k.strip()] = v
    return out


def _salida(datos, en_json: bool, imprimir) -> None:
    if en_json:
        print(json.dumps(datos, ensure_ascii=False, indent=2, default=str))
    else:
        imprimir(datos)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    a = _parser().parse_args(argv)
    try:
        hoy = _hoy(getattr(a, "fecha", None))
        if a.cmd == "fotogramas":
            r = fotogramas(a.cliente, a.ad, a.video, a.api, a.descargar_video, a.cuadricula, a.max, hoy)
            _salida(r, a.json, _imprimir_fotogramas)
            return 0 if r["procesados"] or not r["anuncios"] else 1
        if a.cmd == "etiquetas":
            if a.accion == "esquema":
                _salida(esquema_dict(), a.json, _imprimir_esquema)
            elif a.accion == "preparar":
                _salida(preparar(a.cliente, a.todos), a.json, _imprimir_preparar)
            elif a.accion == "pendientes":
                _salida(pendientes(a.cliente, a.todos), a.json, _imprimir_pendientes)
            elif a.accion == "poner":
                if a.archivo and (a.ad or a.pares):
                    raise ErrorUsuario("Usa --archivo o --ad con campo=valor, no los dos")
                if a.archivo:
                    cambios = _leer_cambios_archivo(a.archivo)
                elif a.ad and a.pares:
                    cambios = [{"ad_id": a.ad, **_pares(a.pares)}]
                else:
                    raise ErrorUsuario("Falta --ad ID campo=valor … o --archivo")
                _salida(poner(a.cliente, cambios, a.por, hoy), a.json,
                        lambda r: (print(f"Etiquetas guardadas en {r['archivo']} ({r['anuncios']} anuncios)"),
                                   [print(f"Aviso: {x}") for x in r["avisos"]]))
            else:
                r = validar(a.cliente)
                _salida(r, a.json, _imprimir_validar)
                return 1 if r["errores"] else 0
            return 0
        if a.cmd == "analizar":
            _salida(analizar(a.cliente, a.capa, a.dias_madurez, hoy, a.guardar, a.madurez), a.json,
                    _imprimir_analisis)
        elif a.cmd == "retencion":
            _salida(retencion(a.cliente, a.meta, a.min_impresiones), a.json, _imprimir_retencion)
        elif a.cmd == "diversidad":
            if not 0 < a.umbral <= 1 or not 0 <= a.umbral_visual <= 64:
                raise ErrorUsuario("--umbral va entre 0 y 1 y --umbral-visual entre 0 y 64")
            _salida(diversidad(a.cliente, a.umbral, a.umbral_visual, a.todos, hoy, a.guardar), a.json,
                    _imprimir_diversidad)
        else:
            for nombre in ("gasto_mensual", "gasto_diario", "coste_objetivo"):
                v = getattr(a, nombre)
                if v is not None and v <= 0:
                    raise ErrorUsuario(f"--{nombre.replace('_', '-')} tiene que ser > 0")
            _salida(suministro(a.cliente, a.gasto_mensual, a.gasto_diario, a.meta, a.coste_objetivo, a.capa, hoy,
                               a.guardar), a.json, _imprimir_suministro)
        return 0
    except (ErrorUsuario, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (_comun.FichaInvalida, ErrorConfig) as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        return 2


def _imprimir_esquema(r: dict) -> None:
    print(f"Esquema de {r['archivo']}\nColumnas: {','.join(r['columnas'])}\n")
    print(f"Criterio de duda: {r['criterio_duda']}\n")
    for e in r["etiquetas"]:
        valores = e["valores"] if isinstance(e["valores"], str) else " | ".join(e["valores"])
        extra = " · automática" if e["automatica"] else ""
        print(f"- {e['columna']} ({'solo vídeo' if e['aplica'] == 'video' else 'todas'}{extra}): {valores}\n"
              f"    {e['define']}")


def _imprimir_preparar(r: dict) -> None:
    print(f"{r['archivo']}: {r['filas']} filas ({r['creadas']} nuevas) · {r['pendientes']} por etiquetar")
    _imprimir_pendientes(r["lista_pendientes"][:15])
    for av in r.get("avisos", []):
        print(f"  Aviso: {av}")


def _imprimir_pendientes(lista: list[dict]) -> None:
    if not lista:
        print("Todos los anuncios con gasto están etiquetados.")
    for x in lista:
        print(f"- {x['ad_id']} · {x['nombre'][:60]} · {_euros(x['gasto'])} · {x['estado']} · "
              f"{'con' if x['fotogramas'] else 'sin'} fotogramas")


def _imprimir_validar(r: dict) -> None:
    print(f"{r['archivo']}: {r['filas']} filas · completas {r['completas']} · parciales {r['parciales']} · "
          f"pendientes {r['pendientes']}")
    for x in r["errores"]:
        print(f"Error: {x}")
    for x in r["avisos"]:
        print(f"Aviso: {x}")
    if not r["errores"]:
        print("Sin errores.")


def _imprimir_fotogramas(r: dict) -> None:
    print(f"Fotogramas · {r['cliente']} · {r['procesados']} de {len(r['anuncios'])} anuncios")
    for x in r["anuncios"]:
        if x["ok"]:
            dur = f" · {_x(x['duracion_s'], 1)} s" if x.get("duracion_s") else ""
            ritmo = f" · ritmo sugerido {x['ritmo_sugerido']}" if x.get("ritmo_sugerido") else ""
            print(f"- {x['ad_id']} · {x['soporte']} {x['relacion_aspecto'] or ''}{dur}{ritmo} · {x['fuente']}")
            for img in x["imagenes"]:
                print(f"    {img}")
        else:
            print(f"- {x['ad_id']} · no: {x['motivo']}")
    if r.get("cuadricula"):
        print(f"Cuadrícula: {r['cuadricula']['imagen']} (índice: {r['cuadricula']['indice']})")
    for a in r["avisos"]:
        print(f"Aviso: {a}")


if __name__ == "__main__":
    sys.exit(main())
