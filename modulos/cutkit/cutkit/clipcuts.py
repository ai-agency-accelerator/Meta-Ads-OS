"""Cortes de clip dentro de una fuente ya montada (el usuario entrega el vídeo ya cortado: saltos de plano entre tomas).

Un cambio de layout que cae unos fotogramas antes o después de uno de estos cortes se ve como dos cortes seguidos
(el cambio debe cortarse COINCIDIENDO CON EL CORTE del clip). El compilador pega esos cambios al corte.

Detección: diferencia media por fotograma en gris a 72×128; un corte es un pico ≥ 4× la mediana local (±0,5 s) y
≥ 4 niveles absolutos. Los gestos al hablar dan ≈ 2×; los cortes de clip, 5–10×. Se cachea por fuente (ruta+tamaño+mtime).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

W, H = 72, 128
RATIO, ABS = 4.0, 4.0


def detect(path: str | Path, fps: float = 30.0) -> list[float]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    if len(f) < 3:
        return []
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    half = int(round(fps / 2))
    med = np.array([np.median(d[max(0, i - half):i + half]) for i in range(len(d))])
    out = []
    for i in range(len(d)):
        if d[i] >= ABS and d[i] >= RATIO * max(med[i], 0.3) and d[i] == d[max(0, i - 3):i + 4].max():
            out.append(round((i + 1) / fps, 4))     # primer fotograma del plano nuevo
    return out


def for_sources(mi, cache_path: Path) -> dict[str, list[float]]:
    """{source_id: [segundos de fuente]} para las fuentes de cara (no el outro: es un plano único)."""
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    out, dirty = {}, False
    for s in mi.sources:
        p = Path(s.mezzanine or s.path)
        if not p.exists():
            continue
        st = p.stat()
        key = f"{p}|{st.st_size}|{int(st.st_mtime)}"
        hit = cache.get(s.id)
        if not hit or hit.get("key") != key:
            hit = {"key": key, "cuts": detect(p, s.fps or 30.0)}
            cache[s.id] = hit
            dirty = True
        out[s.id] = hit["cuts"]
    if dirty:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=1))
    return out
