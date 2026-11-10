"""Biblioteca de SFX sintéticos de cutkit (dominio público, CC0).

`ck instalar` llama a `generar()`: sintetiza con NumPy una biblioteca pequeña de efectos sutiles para vídeos de
software y servicios (aire, pops tonales, clics, ticks, brillos, tecleo, reloj, impactos, glitch y dings) y la deja en
`datos/sfx/<tipo>/<id>.wav` (48 kHz, estéreo, 24 bits) con su `catalogo.yaml`. No usa muestras de terceros: todo sale de
osciladores y ruido con semilla fija, así que el resultado es idéntico en cada máquina y no arrastra ninguna licencia.

Los `id` son los que usan el mapa de animaciones (`recursos/sfx/animaciones.yaml`) y los eventos del catálogo
(`recursos/sfx/eventos.yaml`). Para sumar tu propia biblioteca (sonidos con licencia para publicidad), define
`CK_SFX_DIR` con subcarpetas por tipo (`whoosh_corto/`, `pop/`, `click/`…): `sfx.build_catalog()` la inventaría junto
a esta.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import signal as sg

from . import _dsp as d

SR = d.SR
SEMILLA = 7
LICENCIA = ("Efectos de sonido sintetizados por cutkit (NumPy, sin muestras de terceros).\n"
            "Dedicados al dominio público con CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/\n"
            "Puedes usarlos en anuncios y vídeos comerciales sin atribución.\n")


def destino_por_defecto() -> Path:
    from ..paths import DATOS
    return DATOS / "sfx"


# ───────────────────────────── piezas básicas ─────────────────────────────
def _n(dur: float) -> int:
    return int(round(dur * SR))


def _t(n: int) -> np.ndarray:
    return np.arange(n) / SR


def _fundidos(x: np.ndarray, entrada: float = 0.001, salida: float = 0.008) -> np.ndarray:
    x = x.copy()
    a, b = max(1, _n(entrada)), max(1, _n(salida))
    x[:a] *= np.linspace(0, 1, a)
    x[-b:] *= np.linspace(1, 0, b)
    return x


def _filtro(x: np.ndarray, tipo: str, f, orden: int = 2) -> np.ndarray:
    return sg.sosfilt(sg.butter(orden, f, tipo, fs=SR, output="sos"), x)


def _seno_amortiguado(f: float, dur: float, tau: float, fase0: float = 0.0) -> np.ndarray:
    t = _t(_n(dur))
    return np.sin(2 * np.pi * f * t + fase0) * np.exp(-t / tau)


def _chasquido(rng: np.random.Generator, dur: float = 0.004, desde_hz: float = 1500.0) -> np.ndarray:
    """Transitorio de ruido muy corto (el «tac» de un clic o el ataque de un pop)."""
    n = _n(dur)
    x = _filtro(rng.standard_normal(n), "highpass", desde_hz)
    return x * np.exp(-_t(n) / (dur / 4))


def _barrido(rng: np.random.Generator, dur: float, f0: float, f1: float, pico: float, q: float = 1.3,
             f2: float | None = None) -> np.ndarray:
    """Ruido por un pasabanda que recorre f0 → f1 (→ f2): el aire de un whoosh. `pico`: fracción del máximo."""
    n = _n(dur)
    ruido = rng.standard_normal(n)
    out = np.zeros(n)
    bloque, zi = 240, None
    for i in range(0, n, bloque):
        u = i / n
        if f2 is None:
            fc = f0 * (f1 / f0) ** u
        elif u < pico:
            fc = f0 * (f1 / f0) ** (u / pico)
        else:
            fc = f1 * (f2 / f1) ** ((u - pico) / (1 - pico))
        lo, hi = max(40.0, fc * (1 - 0.5 / q)), min(SR * 0.45, fc * (1 + 0.5 / q))
        sos = sg.butter(2, [lo, hi], "bandpass", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + bloque], zi = sg.sosfilt(sos, ruido[i:i + bloque], zi=zi)
    u = np.arange(n) / n
    env = np.where(u < pico, (u / pico) ** 2, ((1 - u) / (1 - pico)) ** 1.6)
    return out * env


def _pop(rng: np.random.Generator, f: float, dur: float = 0.18, tau: float = 0.045, caida: float = 1.35,
         clic: float = 0.18) -> np.ndarray:
    """Pop tonal: seno con una caída de tono rápida (12 ms), segundo armónico corto y un chasquido de ataque."""
    n = _n(dur)
    t = _t(n)
    finst = f * (1 + (caida - 1) * np.exp(-t / 0.012))
    fase = 2 * np.pi * np.cumsum(finst) / SR
    x = np.sin(fase) * np.exp(-t / tau) + 0.22 * np.sin(2 * fase) * np.exp(-t / (tau / 2.5))
    x *= np.minimum(1.0, t / 0.0015)
    c = _chasquido(rng, 0.004, 2500)
    x[: len(c)] += clic * c / (np.abs(c).max() + 1e-9)
    return x


def _campana(f: float, dur: float, tau: float, parciales=((1.0, 1.0), (2.0, 0.45), (2.76, 0.35), (5.4, 0.18),
                                                          (8.93, 0.08))) -> np.ndarray:
    t = _t(_n(dur))
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (tau / (1 + 0.35 * k)))
            for k, (r, a) in enumerate(parciales))
    return x * np.minimum(1.0, t / 0.002)


def _cuerda(rng: np.random.Generator, f: float, dur: float, decaimiento: float = 0.996) -> np.ndarray:
    """Pulsación de cuerda (Karplus-Strong)."""
    n, p = _n(dur), int(round(SR / f))
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = decaimiento * 0.5 * (buf[j] + buf[(j + 1) % p])
    return _filtro(out, "highpass", 120)


def _brillo(rng: np.random.Generator, dur: float, centro: float, tau: float, ataque: float = 0.012) -> np.ndarray:
    """Destello agudo: varios senos alrededor de `centro` con trémolo y cola corta (no tapa la voz)."""
    t = _t(_n(dur))
    x = np.zeros_like(t)
    for _ in range(7):
        f = centro * rng.uniform(0.86, 1.18)
        x += np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * (1 + 0.5 * np.sin(2 * np.pi * rng.uniform(12, 22) * t))
    return x * np.minimum(1.0, t / ataque) * np.exp(-t / tau)


def _tecla(rng: np.random.Generator) -> np.ndarray:
    n = _n(0.05)
    t = _t(n)
    golpe = _filtro(rng.standard_normal(n), "bandpass", [1800, 6500]) * np.exp(-t / 0.004)
    cuerpo = np.sin(2 * np.pi * rng.uniform(380, 520) * t) * np.exp(-t / 0.008) * 0.35
    return golpe + cuerpo


def _secuencia(piezas: list[tuple[float, np.ndarray, float]], dur: float) -> np.ndarray:
    out = np.zeros(_n(dur))
    for t0, x, g in piezas:
        i = _n(t0)
        m = min(len(x), len(out) - i)
        if m > 0:
            out[i:i + m] += g * x[:m]
    return out


# ───────────────────────────── los efectos ─────────────────────────────
def _tecleo(rng: np.random.Generator, dur: float) -> np.ndarray:
    piezas, t = [], 0.03
    while t < dur - 0.08:
        g = rng.uniform(0.55, 1.0)
        piezas.append((t, _tecla(rng), g))
        if rng.random() < 0.35:                                     # soltar la tecla
            piezas.append((t + rng.uniform(0.03, 0.045), _tecla(rng), g * 0.3))
        t += rng.uniform(0.07, 0.16)
    return _secuencia(piezas, dur)


def _reloj(rng: np.random.Generator, dur: float, ioi: float) -> np.ndarray:
    piezas, t, k = [], 0.01, 0
    while t < dur - 0.03:
        f = 3200 if k % 2 == 0 else 2400
        x = _seno_amortiguado(f, 0.03, 0.0035)
        c = _chasquido(rng, 0.003, 2000)
        x[: len(c)] += 0.4 * c / (np.abs(c).max() + 1e-9)
        piezas.append((t, x, 1.0 if k % 2 == 0 else 0.8))
        t, k = t + ioi, k + 1
    return _secuencia(piezas, dur)


def _impacto(rng: np.random.Generator, f0: float, f1: float, dur: float, tau: float, medio: float) -> np.ndarray:
    n = _n(dur)
    t = _t(n)
    finst = f1 + (f0 - f1) * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(finst) / SR) * np.exp(-t / tau)
    golpe = _filtro(rng.standard_normal(_n(0.06)), "lowpass", 900) * np.exp(-_t(_n(0.06)) / 0.012)
    x[: len(golpe)] += 0.5 * golpe
    if medio:
        x += medio * _seno_amortiguado(420, dur, 0.06)
    return x * np.minimum(1.0, t / 0.001)


def _glitch(rng: np.random.Generator, dur: float, tonal: bool) -> np.ndarray:
    out = np.zeros(_n(dur))
    t = 0.0
    while t < dur - 0.02:
        largo = rng.uniform(0.018, 0.05)
        n = _n(largo)
        if tonal:
            f = rng.choice([330, 495, 660, 990, 1320, 1980])
            x = np.sign(np.sin(2 * np.pi * f * _t(n))) * 0.5
        else:
            paso = int(rng.integers(6, 40))                         # retención de muestra: ruido «digital»
            x = np.repeat(rng.uniform(-1, 1, n // paso + 1), paso)[:n]
        i = _n(t)
        m = min(n, len(out) - i)
        out[i:i + m] += _fundidos(x, 0.0005, 0.002)[:m] * rng.uniform(0.5, 1.0)
        t += largo + rng.uniform(0.0, 0.03)
    return _filtro(out, "highpass", 300)


def _error(rng: np.random.Generator) -> np.ndarray:
    def zumbido(f, dur):
        t = _t(_n(dur))
        x = sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 3, 5, 7))
        return _fundidos(x, 0.003, 0.02)
    return _filtro(_secuencia([(0.0, zumbido(233.08, 0.11), 1.0), (0.15, zumbido(196.0, 0.14), 1.0)], 0.32),
                   "lowpass", 3200)


def _definiciones() -> list[tuple[str, str, object]]:
    """(id, tipo, función(rng) → mono). El orden fija las semillas: añade al final, no reordenes."""
    return [
        ("aire_1", "whoosh_corto", lambda r: _barrido(r, 0.28, 800, 2600, 0.62)),
        ("aire_2", "whoosh_corto", lambda r: _barrido(r, 0.32, 600, 1900, 0.6)),
        ("aire_3", "whoosh_corto", lambda r: _barrido(r, 0.22, 1200, 3600, 0.65)),
        ("aire_medio_1", "whoosh_medio", lambda r: _barrido(r, 0.8, 420, 3000, 0.7, q=1.1)),
        ("barrido_1", "whoosh_largo", lambda r: _barrido(r, 1.4, 320, 2600, 0.55, q=1.0, f2=700)),
        ("subida_1", "riser", lambda r: _barrido(r, 1.8, 300, 6500, 0.97, q=0.9)
         + 0.25 * np.sin(2 * np.pi * np.cumsum(np.geomspace(220, 880, _n(1.8))) / SR)
         * np.linspace(0, 1, _n(1.8)) ** 2),
        ("pop_1", "pop_tonal", lambda r: _pop(r, 1174.66)),
        ("pop_2", "pop_tonal", lambda r: _pop(r, 880.0, tau=0.05)),
        ("pop_3", "pop_tonal", lambda r: _pop(r, 587.33, tau=0.06, clic=0.45)),
        ("firma_1", "firma", lambda r: _cuerda(r, 880.0, 0.45) + 0.18 * _brillo(r, 0.45, 7000, 0.12)),
        ("toc_1", "golpe", lambda r: _seno_amortiguado(700, 0.12, 0.018) + 0.5 * _seno_amortiguado(1850, 0.12, 0.008)
         + 0.3 * np.pad(_chasquido(r, 0.003, 1200), (0, _n(0.117)))[: _n(0.12)]),
        ("bip_1", "bip_ui", lambda r: _secuencia([(0.0, _fundidos(_seno_amortiguado(1318.51, 0.06, 0.2), 0.003, 0.01), 1.0),
                                                  (0.09, _fundidos(_seno_amortiguado(1760.0, 0.08, 0.2), 0.003, 0.02), 1.0)],
                                                 0.2)),
        ("ding_1", "ding", lambda r: _secuencia([(0.0, _fundidos(_seno_amortiguado(1567.98, 0.06, 0.15), 0.002, 0.01), 0.8),
                                                 (0.08, _campana(2093.0, 0.5, 0.18), 1.0)], 0.6)),
        ("ding_2", "ding", lambda r: _campana(1046.5, 0.7, 0.25)),
        ("click_1", "click", lambda r: _seno_amortiguado(6500, 0.03, 0.004) + 0.5 * np.pad(_chasquido(r, 0.004, 4000), (0, _n(0.026)))),
        ("click_2", "click_mecanico", lambda r: _secuencia([(0.0, _filtro(_chasquido(r, 0.006, 900), "lowpass", 7000), 1.0),
                                                           (0.07, _filtro(_chasquido(r, 0.005, 1400), "lowpass", 7000), 0.55)],
                                                          0.11)),
        ("tick_1", "tick", lambda r: _seno_amortiguado(2000, 0.03, 0.005)),
        ("tick_2", "tick", lambda r: _seno_amortiguado(8600, 0.025, 0.003)),
        ("tick_3", "tick", lambda r: _seno_amortiguado(2600, 0.03, 0.004)),
        ("brillo_1", "brillo", lambda r: _brillo(r, 0.35, 10500, 0.09)),
        ("brillo_2", "brillo", lambda r: _brillo(r, 0.5, 10000, 0.14, ataque=0.02)),
        ("brillo_3", "brillo", lambda r: _brillo(r, 0.4, 8000, 0.11)),
        ("tecleo_1", "tecleo", lambda r: _tecleo(r, 1.6)),
        ("tecleo_2", "tecleo", lambda r: _tecleo(r, 1.2)),
        ("tictac_1", "tictac", lambda r: _reloj(r, 2.0, 0.5)),
        ("reloj_barrido_1", "tictac", lambda r: _reloj(r, 0.75, 0.2)),
        ("impacto_1", "impacto_sub", lambda r: _impacto(r, 95, 45, 1.0, 0.35, 0.0)),
        ("impacto_2", "impacto_grave", lambda r: _impacto(r, 150, 75, 0.7, 0.18, 0.35)),
        ("glitch_1", "glitch", lambda r: _glitch(r, 0.26, tonal=False)),
        ("glitch_2", "glitch", lambda r: _glitch(r, 0.2, tonal=True)),
        ("error_1", "error", _error),
    ]


def _estereo(x: np.ndarray, rng: np.random.Generator, ancho: float) -> np.ndarray:
    """Estéreo discreto: el canal derecho lleva un retardo de 0,2–0,4 ms en los sonidos con ruido (`ancho` > 0)."""
    if ancho <= 0:
        return np.stack([x, x], axis=1)
    k = int(rng.integers(10, 20))
    r = np.concatenate([np.zeros(k), x[:-k]])
    return np.stack([x, (1 - ancho) * x + ancho * r], axis=1)


def sintetizar(ident: str) -> np.ndarray:
    """Muestras (n, 2) float64 del efecto `ident`, normalizadas a −3 dBFS de pico."""
    for k, (i, tipo, fn) in enumerate(_definiciones()):
        if i == ident:
            rng = np.random.default_rng(SEMILLA * 1000 + k)
            x = np.asarray(fn(rng), dtype=np.float64)
            x = _fundidos(x - x.mean(), 0.0005, 0.01)
            x = x / (np.abs(x).max() + 1e-12) * 10 ** (-3 / 20)
            ancho = 0.5 if tipo.startswith(("whoosh", "riser", "glitch")) or ident.startswith("brillo") else 0.0
            return _estereo(x, rng, ancho)
    raise KeyError(f"no hay SFX sintético «{ident}»")


def generar(destino: Path | None = None, forzar: bool = False) -> list[Path]:
    """Escribe la biblioteca en `destino` (por defecto `datos/sfx/`) y rehace el catálogo. Idempotente."""
    destino = Path(destino) if destino else destino_por_defecto()
    hechos = []
    for ident, tipo, _ in _definiciones():
        ruta = destino / tipo / f"{ident}.wav"
        if forzar or not ruta.exists():
            d.write(ruta, sintetizar(ident), subtype="PCM_24")
        hechos.append(ruta)
    (destino / "LICENCIA.txt").write_text(LICENCIA, encoding="utf-8")
    if destino == destino_por_defecto():
        from . import sfx
        sfx.build_catalog(force=True)
    return hechos
