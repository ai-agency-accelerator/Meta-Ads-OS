"""Render: proyecto HF → vídeo (sin audio) → mezcla de audio (cutkit.audio) → máster final + proxy.

El audio nunca pasa por HyperFrames: se mezcla aparte a 48 kHz con ganancia fija + limitador y se multiplexa al final.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from . import sistema
from .paths import HF_VERSION, version_dir
from .spec import Timeline


def sh(cmd: list[str], cwd: Path | None = None, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def hf_check(hf_dir: Path) -> dict:
    p = sh([sistema.npx(), "--yes", f"hyperframes@{HF_VERSION}", "lint", "--json"], cwd=hf_dir, timeout=600)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"raw": (p.stdout + p.stderr)[-4000:], "code": p.returncode}


def render_video(slug: str, vid: str, quality: str = "looks", workers: str = "auto") -> Path:
    vd = version_dir(slug, vid)
    hf = vd / "hf"
    out = vd / "video_hf.mp4"
    t = time.time()
    # CK_HF_WORKERS limita los Chrome en paralelo (cada uno llega a ~2,8 GB en un vertical 1080×1920 con dos fuentes;
    # con «auto» puede lanzar 4 y llenar la memoria de intercambio). Por defecto, 2.
    import os
    workers = os.environ.get("CK_HF_WORKERS", "2" if workers == "auto" else workers)
    # CK_HF_FRAME_FORMAT=jpg: con «auto» HyperFrames extrae en PNG las grabaciones de pantalla (B-roll de UI) y la caché
    # puede pasar de 1,4 GB a medio render. En jpg ocupa ~10 veces menos.
    fmt = os.environ.get("CK_HF_FRAME_FORMAT")
    p = sh([sistema.npx(), "--yes", f"hyperframes@{HF_VERSION}", "render", ".", "-o", str(out), "-q", quality, "-w", workers,
            "--browser-timeout", "300", "--player-ready-timeout", "180000", "--quiet",
            *(["--video-frame-format", fmt] if fmt else [])], cwd=hf, timeout=7200)
    (vd / "render_hf.log").write_text(p.stdout[-20000:] + "\n---\n" + p.stderr[-20000:])
    # la caché de fotogramas extraídos de HyperFrames ($TMPDIR/hyperframes-extract-cache-<uid>) crece ~3–4 GB por render
    # y no se vacía sola. Es un temporal del propio render: se borra al acabar salvo CK_KEEP_HF_CACHE=1.
    if os.environ.get("CK_KEEP_HF_CACHE") != "1":
        import shutil
        import tempfile
        for c in Path(tempfile.gettempdir()).glob("hyperframes-extract-cache-*"):
            shutil.rmtree(c, ignore_errors=True)
    if p.returncode != 0 or not out.exists():
        raise RuntimeError(f"hyperframes render falló ({p.returncode}); ver {vd/'render_hf.log'}")
    print(f"[render] HF {time.time()-t:.0f} s → {out}")
    return out


def render_audio(slug: str, vid: str) -> dict:
    from .audio import mix
    vd = version_dir(slug, vid)
    tl = Timeline.model_validate_json((vd / "timeline.json").read_text())
    res = mix.render(tl, vd / "audio")
    (vd / "audio" / "mix_report.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return res


def mux(slug: str, vid: str, video: Path, mix_wav: Path) -> Path:
    vd = version_dir(slug, vid)
    out = vd / "render.mp4"
    p = sh(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(mix_wav), "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)])
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-2000:])
    proxy = vd / "render_540.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-vf", "scale=540:-2", *sistema.codec_video("proxy"),
        "-c:a", "aac", "-b:a", "128k", str(proxy)])
    return out


def render_all(slug: str, vid: str, quality: str = "looks") -> Path:
    video = render_video(slug, vid, quality=quality)
    res = render_audio(slug, vid)
    return mux(slug, vid, video, Path(res["mix"]))
