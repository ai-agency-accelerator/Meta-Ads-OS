"""Umbrales de las puertas de `ck qa` y carga de las fuentes externas (perfil de estilo y `qa_motion_gates.yaml`).

Los valores son de partida: calíbralos con ediciones aprobadas (las tuyas o las de tu cliente). Severidades:
block = no se entrega · warn = va al informe para revisión humana · info.
Zona segura: la de Meta para 9:16 (14 % arriba, 35 % abajo, 6 % a los lados [OFFICIAL META]) y la franja de botones de
Reels a la derecha desde y≈1152 (~227 px) [STRONG INFERENCE] (meta-ads-kb/07-instagram-placements-mensajeria/
03-specs-safe-zones-formatos.md).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .. import paths as _paths
from ..paths import DATOS, RECURSOS

MOTION_GATES = RECURSOS / "qa_motion_gates.yaml"
# Perfiles de estilo de referencia (opcionales): `<carpeta>/<nombre>/perfil_estilo.yaml` con `estilo.ritmo` medido
# sobre vídeos de referencia. Tuyos en datos/estilos/ (no se versionan); el producto no trae ninguno.
PROFILES_DIRS = (DATOS / "estilos", RECURSOS / "estilos")
DEFAULT_RHYTHM_PROFILE = ""           # sin perfil de referencia: la QA de ritmo solo informa

GEMINI_MODEL = os.environ.get("CUTKIT_JUDGE_MODEL", "gemini-3.8-flash")

DEFAULTS: dict[str, Any] = {
    "audio": {
        "lufs_target": -14.0, "lufs_tol": 1.0,          # integrado −14 ± 1 LUFS
        "tp_max_dbtp": -1.0,                             # pico verdadero medido en el MP4 final (AES TD1008)
        "lrd_warn_lu": 10.0, "lrd_block_lu": 7.0,        # voz − fondo integrado (Torcoli 2019)
        "win3_warn_db": 8.0,                             # ventana de 3 s con voz
        "word_warn_db": 6.0, "word_low_db": 3.0,         # por palabra (sin prueba ASR no bloquea)
        "voice_silence_db": -45.0,                       # silencio en el stem de voz
        "voice_silence_min_s": 0.40,
        "pause_warn_s": 1.2,                             # hueco entre palabras sin justificar
        "total_silence_db": -60.0, "total_silence_min_s": 0.25,
    },
    "video": {
        "black_d": 0.03, "black_pix_th": 0.10, "black_pic_th": 0.999,   # 0,999: un logo sobre negro no es un parpadeo
        "freeze_n": 0.001, "freeze_d": 0.5,             # −60 dB, 0,5 s (qa.md §3)
        "dur_tol_frames": 1,
    },
    "captions": {
        "lead_frames": (0.0, 2.0),      # la página entra 0–2 fotogramas antes de su primera palabra
        "late_block_ms": 150.0,          # subtítulo después de la palabra > 150 ms → block
        "early_block_ms": 300.0,         # subtítulo > 300 ms antes → block
        "min_dur_s": 0.30, "min_dur_block_frames": 2,
        "face_overlap_block": 0.10,      # fracción de la zona ojos/boca tapada
    },
    "safe": {   # 1080×1920, zona segura de Meta (Reels y Stories); `right` solo por debajo de `right_from_y`
        "ref_w": 1080, "ref_h": 1920, "top": 269, "bottom": 672, "left": 65, "right": 227, "right_from_y": 1152,
        "ocr_tol_px": 8,                 # holgura por imprecisión del OCR
        "key_min_px": 44, "min_px": 30, "tiny_px": 24,
    },
    "sampling": {"boxes_fps": 4.0, "ocr_fps": 2.0, "sheet_fps": 2.0, "sheet_w": 270, "sheet_cols": 6, "sheet_rows": 4},
    "claims": {"coverage_min": 0.60, "window_s": 10.0},
    "pacing": {"hook_first_change_s": 1.5},
    "panel": {"fps": 10, "slot_h": 874, "occ_min": 0.004, "empty_min_s": 0.3, "diff": 50},   # ly.panel_empty
    "motion": {   # sobrescrito por qa_motion_gates.yaml si existe
        "simultaneous_window_s": 0.08, "simultaneous_max": 2,
        "sfx_per_s_max": 0.40, "sfx_same_per_min_max": 4, "sfx_cluster_1s_max": 2,   # 18-oct: GESTOS/s (24/min)
        "sfx_silent_min_s": 2.5, "sfx_silent_win_s": 0.25,                              # sfx.silent_block
        "tr_per_min_short": 4.0, "tr_per_min_long": 1.5,
        "tr_mid_sentence_pause_s": 0.18,
        "camera_motion_pct_max": 40.0, "punch_dead_zone": (1.03, 1.10),
        "zoom_warn": 1.0, "zoom_block": 1.25,
        "entry_lead_ms": (-370.0, -60.0), "entry_late_tol_ms": 120.0, "entry_pct_min": 75.0,
        "dwell_min_s": 0.8, "dwell_chars_per_s": 15.0, "dwell_extra_s": 0.3,
        "concurrent_blocks_max": 2, "concurrent_words_max": 12,
        "breathing_every_s": 20.0, "breathing_clean_s": 2.0,
        "orphan_after_s": 1.5,
        "eases_max": 4, "overshoot_pct_max": 10.0, "overshoot_param_max": 1.7,
        "component_repeat_max_short": 3,
    },
}


def runs_root() -> Path:
    """Carpeta que agrupa los proyectos (`clientes/` o `CUTKIT_RUNS` en pruebas)."""
    return _paths.runs_root()


@lru_cache(maxsize=1)
def motion_gates() -> dict[str, Any]:
    """Lee `recursos/qa_motion_gates.yaml` (puertas de motion medibles y rúbrica del juez)."""
    if not MOTION_GATES.exists():
        return {}
    try:
        return yaml.safe_load(MOTION_GATES.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def gate(gid: str) -> dict[str, Any]:
    for g in motion_gates().get("gates", []) or []:
        if g.get("id") == gid:
            return g
    return {}


def gate_severity(gid: str, default: str = "warn", key: str | None = None) -> str:
    sev = gate(gid).get("severidad", default)
    if isinstance(sev, dict):
        sev = sev.get(key, default) if key else default
    return sev if sev in ("block", "warn", "info") else default


def motion_thresholds() -> dict[str, Any]:
    """Umbrales de motion: los del YAML mandan sobre los valores por defecto cuando existen."""
    m = dict(DEFAULTS["motion"])
    u = lambda gid: gate(gid).get("umbral", {}) or {}  # noqa: E731
    if (x := u("mo.simultaneous_entries").get("max")) is not None:
        m["simultaneous_max"] = x
    s = u("sfx.density")
    m["sfx_per_s_max"] = s.get("por_s_max", m["sfx_per_s_max"])
    m["sfx_same_per_min_max"] = s.get("misma_muestra_por_min_max", m["sfx_same_per_min_max"])
    m["sfx_cluster_1s_max"] = s.get("racimo_1s_max", m["sfx_cluster_1s_max"])
    sb = u("sfx.silent_block")
    m["sfx_silent_min_s"] = sb.get("dur_min_s", m["sfx_silent_min_s"])
    m["sfx_silent_win_s"] = sb.get("ventana_s", m["sfx_silent_win_s"])
    t = u("tr.rate")
    m["tr_per_min_short"] = t.get("max_por_min_short", m["tr_per_min_short"])
    m["tr_per_min_long"] = t.get("max_por_min_longform", m["tr_per_min_long"])
    if (x := u("mo.camera_motion_ratio").get("pct_max")) is not None:
        m["camera_motion_pct_max"] = x
    if (x := u("mo.punch_dead_zone").get("zona_prohibida")) is not None:
        m["punch_dead_zone"] = tuple(x)
    e = u("sync.entry_lead")
    if "rango_ms" in e:
        m["entry_lead_ms"] = tuple(e["rango_ms"])
    m["entry_late_tol_ms"] = e.get("tolerancia_tarde_ms", m["entry_late_tol_ms"])
    m["entry_pct_min"] = e.get("pct_en_rango_min", m["entry_pct_min"])
    c = u("ly.concurrent_text")
    m["concurrent_blocks_max"] = c.get("bloques_max", m["concurrent_blocks_max"])
    m["concurrent_words_max"] = c.get("palabras_max", m["concurrent_words_max"])
    b = u("ly.breathing")
    m["breathing_every_s"] = b.get("tramo_limpio_cada_s", m["breathing_every_s"])
    o = u("mo.overshoot_budget")
    m["overshoot_pct_max"] = o.get("pct_max", m["overshoot_pct_max"])
    m["overshoot_param_max"] = o.get("overshoot_param_max", m["overshoot_param_max"])
    if (x := u("mo.ease_tokens").get("eases_distintos_max")) is not None:
        m["eases_max"] = x
    if (x := u("mo.component_repeat").get("max_por_short")) is not None:
        m["component_repeat_max_short"] = x
    if (x := u("tr.mid_sentence")) and "pausa_max_s" in x:
        m["tr_mid_sentence_pause_s"] = x["pausa_max_s"]
    return m


def rubric() -> list[dict[str, Any]]:
    """Rúbrica sí/no del juez (qa_motion_gates.yaml → rubrica_juez)."""
    return list(motion_gates().get("rubrica_juez", []) or [])


@lru_cache(maxsize=8)
def style_profile(name: str) -> dict[str, Any]:
    p = next((d / name / "perfil_estilo.yaml" for d in PROFILES_DIRS if (d / name / "perfil_estilo.yaml").exists()), None)
    if p is None:
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def rhythm_profile(name: str | None) -> tuple[str, dict[str, Any]]:
    """Distribución de ritmo del perfil activo; si no tiene, la del perfil de referencia por defecto (solo avisos)."""
    for cand in [name, DEFAULT_RHYTHM_PROFILE]:
        if not cand:
            continue
        r = (style_profile(cand).get("estilo", {}) or {}).get("ritmo", {})
        if r:
            return cand, r
    return "", {}
