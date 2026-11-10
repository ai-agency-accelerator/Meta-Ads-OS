"""Utilidades compartidas por los tests de cutkit (no es un test: lo importan `conftest.py` y los `test_cutkit_*`)."""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import textwrap

RAIZ_PRODUCTO = pathlib.Path(__file__).resolve().parents[3]
MODULO = RAIZ_PRODUCTO / "modulos" / "cutkit"
PAQUETE = MODULO / "cutkit"
FUENTES = PAQUETE / "recursos" / "fuentes"

# Marca de un cliente ficticio (solo colores y logo: la tipografía sale de la Montserrat del producto)
MARCA_ACME = {
    "nombre": "Acme Automations",
    "colores": {"primario": "#1D4ED8", "secundario": "#0F172A", "acento": "#F59E0B", "fondo": "#FFFFFF",
                "texto": "#0F172A", "texto_sobre_primario": "#FFFFFF"},
    "logo": {"principal": "logo.png"},
    "cta_por_defecto": "Pide tu demo",
}

SRT_BRUTO = """1
00:00:00,300 --> 00:00:01,600
¿Tu CRM pierde leads

2
00:00:01,600 --> 00:00:02,800
cada semana?

3
00:00:03,600 --> 00:00:05,600
Acme Automations los recupera.
"""


def entorno_limpio(**extra: str) -> dict[str, str]:
    """Entorno para un subproceso de cutkit: sin claves, sin ajustes CK_*/CUTKIT_* heredados ni el VIRTUAL_ENV raíz."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("VIRTUAL_ENV", "META_ADS_OS_RAIZ") and not k.startswith(("CK_", "CUTKIT_"))
           and not k.endswith(("_API_KEY", "_KEY"))}
    env.update(extra)
    return env


def ffmpeg_con(*requisitos: str) -> str | None:
    """None si FFmpeg está y tiene todo lo pedido (p. ej. `libass`, `libx264`); si no, el motivo para saltar."""
    ff = shutil.which("ffmpeg")
    if not ff or not shutil.which("ffprobe"):
        return "FFmpeg no está instalado"
    p = subprocess.run([ff, "-hide_banner", "-buildconf"], capture_output=True, text=True)
    falta = [r for r in requisitos if r not in p.stdout]
    return f"este FFmpeg no tiene {', '.join(falta)}" if falta else None


def bruto_sintetico(destino: pathlib.Path, segundos: float = 6.5) -> pathlib.Path:
    """Vídeo horizontal 1920×1080 con «voz» sintética (tono modulado en tres frases, silencios entre medias) y su SRT."""
    destino.mkdir(parents=True, exist_ok=True)
    mp4 = destino / "bruto.mp4"
    voz = "between(t,0.3,2.8)+between(t,3.6,5.6)"
    subprocess.run(["ffmpeg", "-v", "error", "-y",
                    "-f", "lavfi", "-i", f"testsrc2=size=1920x1080:rate=30:duration={segundos}",
                    "-f", "lavfi", "-i",
                    f"aevalsrc='if({voz},0.3*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*3*t)),0)':s=48000:d={segundos}",
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                    str(mp4)],
                   check=True, capture_output=True)
    (destino / "bruto.srt").write_text(SRT_BRUTO, encoding="utf-8")
    return mp4


def marca_acme(raiz: pathlib.Path) -> pathlib.Path:
    """`clientes/acme/marca/` con `marca.json` y un logo PNG generado (requiere FFmpeg)."""
    d = raiz / "clientes" / "acme" / "marca"
    d.mkdir(parents=True, exist_ok=True)
    (d / "marca.json").write_text(json.dumps(MARCA_ACME, ensure_ascii=False, indent=1), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x1D4ED8:s=600x200,format=rgba",
                    "-vf", "drawbox=x=20:y=20:w=560:h=160:color=white@0.9:t=8", "-frames:v", "1", str(d / "logo.png")],
                   check=True, capture_output=True)
    return d


def sondear(path: pathlib.Path) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type,codec_name,width,height,pix_fmt,sample_rate",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def codigo(fuente: str) -> str:
    """Código Python para `python -I -c`: sangría quitada; lo que imprima con `salida(x)` vuelve como JSON."""
    return "import json\ndef salida(x):\n    print('@@' + json.dumps(x, ensure_ascii=False))\n" + textwrap.dedent(fuente)


def leer_salida(stdout: str):
    lineas = [x for x in stdout.splitlines() if x.startswith("@@")]
    assert lineas, f"el código no devolvió nada:\n{stdout[-2000:]}"
    return json.loads(lineas[-1][2:])
