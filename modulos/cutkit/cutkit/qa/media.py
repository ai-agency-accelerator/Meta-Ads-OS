"""Acceso al render con FFmpeg: sonda, sonoridad EBU R128 y UNA decodificación compartida de vídeo.

Una sola pasada (filtergraph con `split`) sirve para negros, congelados, fotogramas a 2 fps para OCR/caras y
fotogramas de 270 px para las hojas de contacto (decodificar es lo caro).
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import numpy as np


def probe(path: Path) -> dict[str, Any]:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in j.get("streams", []) if s.get("codec_type") == "audio"), {})
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    vdur = float(v.get("duration") or j.get("format", {}).get("duration") or 0)
    return {
        "width": int(v.get("width") or 0), "height": int(v.get("height") or 0), "fps": round(fps, 3),
        "frames": int(v.get("nb_frames") or 0), "duration": vdur,
        "format_duration": float(j.get("format", {}).get("duration") or 0),
        "audio_duration": float(a.get("duration") or 0) if a else None,
        "audio": bool(a), "audio_sr": int(a.get("sample_rate") or 0) if a else None,
        "vcodec": v.get("codec_name"), "acodec": a.get("codec_name") if a else None,
    }


def ebur128(path: Path) -> dict[str, Any]:
    """I, LRA y pico verdadero (peak=true) del audio del MP4 final, más la sonoridad momentánea a 10 Hz."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-v", "verbose", "-i", str(path), "-map", "0:a:0",
                        "-af", "ebur128=peak=true:framelog=verbose", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = p.stderr
    summ = err[err.rfind("Summary:"):] if "Summary:" in err else ""
    def grab(pat: str) -> float | None:
        m = re.search(pat, summ)
        return float(m.group(1)) if m else None
    mom, ftpk = [], []
    for t, m, p1, p2 in re.findall(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.inf]+)\s+S:.*?FTPK:\s*(-?[\d.inf]+)\s+(-?[\d.inf]+) dBFS", err):
        if m not in ("-inf", "inf"):
            mom.append((float(t), float(m)))
        pk = [float(x) for x in (p1, p2) if x not in ("-inf", "inf")]
        if pk:
            ftpk.append((float(t), max(pk)))   # pico verdadero de cada bloque de 100 ms (para localizarlo)
    return {"I": grab(r"I:\s*(-?[\d.]+) LUFS"), "LRA": grab(r"LRA:\s*(-?[\d.]+) LU"),
            "TP": grab(r"True peak:\s*\n\s*Peak:\s*(-?[\d.inf]+) dBFS"), "momentary": mom, "ftpk": ftpk}


def decode_audio(path: Path, sr: int = 48000, mono: bool = True, start: float | None = None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error"]
    if start:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(path), "-map", "0:a:0", "-ac", "1" if mono else "2", "-ar", str(sr), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def shared_decode(path: Path, work: Path, cfg: dict[str, Any], want_full: bool = True) -> dict[str, Any]:
    """Una pasada: blackdetect (fotograma entero), freezedetect SOLO en la franja del A-roll (0,50–0,85·H: boca y
    barbilla en full_face, cara en el split), fotogramas 1080p a `ocr_fps` (OCR, caras), de `sheet_w` px a `sheet_fps`
    (hojas) y el panel superior (0–slot_h px) a 10 fps en miniatura RGB para `ly.panel_empty`."""
    v, s, pn = cfg["video"], cfg["sampling"], cfg["panel"]
    full_dir, sheet_dir = work / "frames_full", work / "frames_sheet"
    for d in (full_dir, sheet_dir):
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.jpg"):
            f.unlink()
    panel_raw = work / "panel.rgb"
    n = 5 if want_full else 4
    labels = ["[a]", "[e]", "[d]", "[b]", "[c]"][:n]
    fg = (f"[0:v]split={n}{''.join(labels)};"
          f"[a]blackdetect=d={v['black_d']}:pix_th={v['black_pix_th']}:pic_th={v['black_pic_th']}[ao];"
          f"[e]crop=iw:ih*0.35:0:ih*0.50,freezedetect=n={v['freeze_n']}:d={v['freeze_d']}[eo];"
          f"[d]fps={pn['fps']}:round=down,crop=iw:{pn['slot_h']}*ih/1920:0:0,scale=108:-2:flags=area,format=rgb24[do];"
          # fotograma k ↔ t = k/fps: `fps` con round=down toma el primer fotograma de cada intervalo
          f"[b]fps={s['sheet_fps']}:round=down,scale={s['sheet_w']}:-2:flags=area[bo]")
    if want_full:
        fg += f";[c]fps={s['ocr_fps']}:round=down[co]"
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-y", "-i", str(path), "-filter_complex", fg,
           "-map", "[ao]", "-f", "null", "-", "-map", "[eo]", "-f", "null", "-",
           "-map", "[do]", "-f", "rawvideo", str(panel_raw),
           "-map", "[bo]", "-q:v", "4", str(sheet_dir / "f_%05d.jpg")]
    if want_full:
        cmd += ["-map", "[co]", "-q:v", "2", str(full_dir / "f_%05d.jpg")]
    p = subprocess.run(cmd, capture_output=True, text=True)
    err = p.stderr
    blacks = [(float(a), float(b)) for a, b in re.findall(r"black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)", err)]
    fs = [float(x) for x in re.findall(r"freeze_start:\s*([\d.]+)", err)]
    fe = [float(x) for x in re.findall(r"freeze_end:\s*([\d.]+)", err)]
    freezes = [(a, fe[i] if i < len(fe) else None) for i, a in enumerate(fs)]
    sheet = sorted(sheet_dir.glob("f_*.jpg"))
    full = sorted(full_dir.glob("f_*.jpg")) if want_full else []
    panel = None
    if panel_raw.exists() and panel_raw.stat().st_size:
        ph = int(round(pn["slot_h"] / 1920 * 108 * 1920 / 1080 / 2) * 2) or 1   # alto tras scale=108:-2
        raw = np.fromfile(panel_raw, np.uint8)
        fr = 108 * ph * 3
        if raw.size % fr:
            # alto real: probar alturas pares cercanas hasta que cuadre
            for cand in range(ph - 4, ph + 6, 2):
                if cand > 0 and raw.size % (108 * cand * 3) == 0:
                    ph, fr = cand, 108 * cand * 3
                    break
        if raw.size % fr == 0:
            panel = raw.reshape(-1, ph, 108, 3)
    return {
        "black": blacks, "freeze": freezes, "ok": p.returncode == 0, "stderr_tail": err[-600:],
        "sheet": [(i / s["sheet_fps"], f) for i, f in enumerate(sheet)],
        "full": [(i / s["ocr_fps"], f) for i, f in enumerate(full)],
        "panel": panel, "panel_fps": pn["fps"],
    }


def lowres_gray(path: Path, fps: int = 30, w: int = 135, h: int = 240) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf",
                          f"fps={fps},scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
