"""Montaje directo de un anuncio para Meta: bruto → 9:16 y 4:5 con hook, subtítulos, CTA, logo y QA técnica.

Es el camino por defecto para vídeo propio (fundador, equipo, creador o demo de pantalla). Determinista, sin red y sin
coste: solo FFmpeg (con libass), NumPy y Pillow. El montaje avanzado por decisiones (`ck new … ck run`) es aparte.

Pasos:
  1. Ingesta: comprueba el bruto (vídeo, audio que suena) y lo deja en `brutos/` del proyecto.
  2. Silencios: quita el aire muerto (≥ 0,35 s por defecto) y el silencio del principio, para que la voz arranque ya.
  3. Subtítulos: de un SRT o JSON de palabras, de un archivo hermano del bruto, o transcritos (whisper.cpp local, o
     whisper-1 de OpenAI solo si lo pides con `--subtitulos openai`). Páginas de 1–3 palabras con la palabra activa
     resaltada, en el tercio central.
  4. Audio: cadena de voz, cama musical opcional (propia o libre de derechos para publicidad) y máster a −14 LUFS con
     limitador a −1,5 dBTP.
  5. Por formato (9:16 y 4:5), maquetación propia dentro de su zona segura: hook en los 2 primeros segundos, subtítulos,
     CTA y logo al final, etiqueta de IA opcional y B-roll a pantalla completa en los tramos que indiques.
  6. QA: resolución exacta (tolerancia de ratio de Meta del 1 %), códecs, hook a tiempo, cobertura de subtítulos, cajas
     dentro de la zona segura, sonoridad, arranque sin negro ni silencio. Resultado en `qa_anuncio.json` y en `LEEME.md`.

Fuentes: meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md y
meta-ads-kb/03-creatividad/04-formatos-y-estilos.md.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import yaml

from . import captions as capmod
from . import sistema
from .marca import Marca, ass_color, cargar as cargar_marca, contraste
from .paths import PERFILES, RAIZ, proyecto_dir

SR = 48000
FPS = 30


def _n(x: float, d: int = 1) -> str:
    """Número para leer en español: coma decimal y signo menos tipográfico (−14,0)."""
    return f"{x:.{d}f}".replace(".", ",").replace("-", "−")


class ErrorUsuario(ValueError):
    """Error en lo que ha pedido el usuario (archivo que no existe, formato desconocido…)."""


@dataclass
class Opciones:
    entrada: Path
    slug: str
    cliente: str | None = None
    hook: str = ""
    cta: str | None = None
    subtitulos: str = "auto"            # auto | no | openai | local | <ruta .srt/.json>
    formatos: tuple[str, ...] = ("9x16", "4x5")
    quitar_silencios: bool = True
    procesar_voz: bool = True
    broll: list[str] = field(default_factory=list)     # "INICIO-FIN:ruta" en segundos del montaje final
    musica: str | None = None
    etiqueta_ia: bool = False
    logo: str = "cta"                   # cta | siempre | no
    mayusculas: bool | None = None
    foco: str = "auto"                  # auto | centro | 0..1 (posición horizontal del encuadre)
    marca: str | None = None            # ruta a otro marca.json
    nombre: str | None = None           # nombre base de los archivos (p. ej. el nombre del anuncio de la nomenclatura)
    fecha: str | None = None
    salida: Path | None = None
    perfil: str = "anuncio"
    idioma: str = "es"


# ───────────────────────────── utilidades ─────────────────────────────
def _ff(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    p = subprocess.run([sistema.requiere("ffmpeg"), "-hide_banner", "-v", "error", "-y", *args], cwd=cwd,
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"FFmpeg falló: {p.stderr.strip()[-1500:]}")
    return p


def sondear(path: Path) -> dict:
    p = subprocess.run([sistema.requiere("ffprobe"), "-v", "error", "-show_entries",
                        "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,"
                        "channels", "-of", "json", str(path)], capture_output=True, text=True)
    if p.returncode != 0:
        raise ErrorUsuario(f"no puedo leer {path.name}: ¿es un vídeo? ({p.stderr.strip()[-200:]})")
    j = json.loads(p.stdout or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in j.get("streams", []) if s.get("codec_type") == "audio"), None)
    fps = None
    if v and v.get("r_frame_rate") and "/" in v["r_frame_rate"]:
        n, d = v["r_frame_rate"].split("/")
        fps = float(n) / float(d) if float(d) else None
    return {"duration": float((j.get("format") or {}).get("duration") or 0), "video": v, "audio": a,
            "width": v and v.get("width"), "height": v and v.get("height"), "fps": fps}


def _perfil(nombre: str) -> dict:
    f = PERFILES / f"{nombre}.yaml"
    if not f.exists():
        raise ErrorUsuario(f"no existe el perfil «{nombre}» (hay: {', '.join(p.stem for p in PERFILES.glob('*.yaml'))})")
    prof = yaml.safe_load(f.read_text(encoding="utf-8"))
    if "anuncio" not in prof:
        raise ErrorUsuario(f"el perfil «{nombre}» no tiene sección `anuncio:` para el montaje directo")
    return prof


def _tc_ass(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _tc_srt(t: float) -> str:
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _ass_texto(s: str) -> str:
    return s.replace("\\", "/").replace("{", "(").replace("}", ")").replace("\n", " ")


# ───────────────────────────── subtítulos de entrada ─────────────────────────────
_SRT_T = re.compile(r"(\d+):(\d{2}):(\d{2})[,.](\d{1,3})")


def _t_srt(s: str) -> float:
    m = _SRT_T.search(s)
    if not m:
        raise ValueError(s)
    h, mi, se, ms = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, "0")) / 1000


def leer_srt(path: Path) -> list[dict]:
    """Cues del SRT → palabras con tiempos repartidos por longitud dentro de cada cue."""
    texto = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")
    bloques = [b for b in re.split(r"\n\s*\n", texto.strip()) if b.strip()]
    palabras: list[dict] = []
    for n, b in enumerate(bloques, 1):
        lineas = [x for x in b.split("\n") if x.strip()]
        k = next((i for i, x in enumerate(lineas) if "-->" in x), None)
        if k is None:
            raise ErrorUsuario(f"{path.name}: el bloque {n} no tiene línea de tiempos «00:00:01,000 --> 00:00:02,000»")
        try:
            a, z = (_t_srt(x) for x in lineas[k].split("-->"))
        except ValueError:
            raise ErrorUsuario(f"{path.name}: tiempos no válidos en el bloque {n}: {lineas[k]!r}") from None
        if z <= a:
            raise ErrorUsuario(f"{path.name}: el bloque {n} acaba antes de empezar")
        toks = re.sub(r"<[^>]+>", "", " ".join(lineas[k + 1:])).split()
        if not toks:
            continue
        pesos = [len(t) + 1 for t in toks]
        tot, cur = sum(pesos), a
        for t, w in zip(toks, pesos):
            d = (z - a) * w / tot
            palabras.append({"text": t, "s": round(cur, 3), "e": round(cur + d, 3)})
            cur += d
    if not palabras:
        raise ErrorUsuario(f"{path.name}: no tiene subtítulos")
    return palabras


def leer_palabras_json(path: Path) -> list[dict]:
    """JSON de palabras: lista o {"words": [...]} con text|word y s|start, e|end (whisper, whisper.cpp, cutkit)."""
    try:
        j = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ErrorUsuario(f"{path.name} no es JSON válido: {e.msg}") from None
    raw = j.get("words", j) if isinstance(j, dict) else j
    out = []
    for w in raw or []:
        t = str(w.get("text", w.get("word", ""))).strip()
        s, e = w.get("s", w.get("start")), w.get("e", w.get("end"))
        if t and s is not None and e is not None:
            out.append({"text": t, "s": float(s), "e": float(max(float(e), float(s) + 0.05))})
    if not out:
        raise ErrorUsuario(f"{path.name}: no encuentro palabras con tiempos (text/word, s/start, e/end)")
    return sorted(out, key=lambda w: w["s"])


def _transcribir(wav: Path, modo: str, idioma: str) -> list[dict]:
    from .analyze import asr

    j = asr(str(wav), "", modo=modo, idioma=idioma)
    return [{"text": str(w.get("word", "")).strip(), "s": float(w["start"]), "e": float(w["end"])}
            for w in j.get("words", []) if str(w.get("word", "")).strip()]


def palabras_de(op: Opciones, wav: Path, avisos: list[str]) -> tuple[list[dict], str]:
    sub = op.subtitulos
    if sub == "no":
        return [], "sin subtítulos (pedido)"
    if sub not in ("auto", "openai", "local"):
        p = Path(sub)
        if not p.exists():
            raise ErrorUsuario(f"no existe el archivo de subtítulos {p}")
        return (leer_srt(p) if p.suffix.lower() == ".srt" else leer_palabras_json(p)), p.name
    if sub == "auto":
        for c in (op.entrada.with_suffix(".srt"), op.entrada.with_suffix(".json"),
                  op.entrada.parent / f"{op.entrada.name}.srt"):
            if c.exists():
                return (leer_srt(c) if c.suffix == ".srt" else leer_palabras_json(c)), c.name
    modo = "local" if sub == "auto" else sub
    try:
        return _transcribir(wav, modo, op.idioma), f"transcripción {modo}"
    except Exception as e:  # noqa: BLE001
        if sub == "auto":
            avisos.append(f"sin subtítulos: no hay SRT/JSON junto al bruto y la transcripción local no está disponible "
                          f"({e}). Pasa `--subtitulos archivo.srt`, instala whisper.cpp (`ck instalar --whisper`) o usa "
                          "`--subtitulos openai` (≈0,006 $/min con tu OPENAI_API_KEY)")
            return [], "sin subtítulos"
        raise


# ───────────────────────────── silencios ─────────────────────────────
def tramos_con_voz(y: np.ndarray, umbral_db: float, minimo: float, margen: float) -> list[tuple[float, float]]:
    """Tramos a conservar (segundos): todo salvo silencios ≥ `minimo`, con `margen` de aire alrededor de la voz."""
    dur = len(y) / SR
    hop = int(SR * 0.02)
    n = len(y) // hop
    if n < 3:
        return [(0.0, dur)]
    rms = np.sqrt((y[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    ref = float(np.percentile(db, 95))
    fondo = float(np.percentile(db, 10))
    umbral = max(ref + umbral_db, fondo + 6.0)
    voz = db > umbral
    if not voz.any():
        return [(0.0, dur)]
    tramos, i = [], 0
    while i < n:
        if voz[i]:
            j = i
            while j < n and voz[j]:
                j += 1
            tramos.append([i * 0.02, j * 0.02])
            i = j
        else:
            i += 1
    unidos = [tramos[0]]
    for a, b in tramos[1:]:
        if a - unidos[-1][1] < minimo:
            unidos[-1][1] = b
        else:
            unidos.append([a, b])
    out = [(max(0.0, a - margen), min(dur, b + margen)) for a, b in unidos]
    fus = [list(out[0])]
    for a, b in out[1:]:
        if a <= fus[-1][1]:
            fus[-1][1] = max(fus[-1][1], b)
        else:
            fus.append([a, b])
    return [(round(a, 3), round(b, 3)) for a, b in fus if b - a >= 0.1]


def a_programa(t: float, tramos: list[tuple[float, float]]) -> float | None:
    acc = 0.0
    for a, b in tramos:
        if a - 1e-6 <= t <= b + 1e-6:
            return acc + (min(max(t, a), b) - a)
        acc += b - a
    return None


def _remapear(palabras: list[dict], tramos: list[tuple[float, float]]) -> list[dict]:
    out = []
    for w in palabras:
        s, e = a_programa(w["s"], tramos), a_programa(w["e"], tramos)
        if s is None and e is None:
            mid = a_programa((w["s"] + w["e"]) / 2, tramos)
            if mid is None:
                continue
            s, e = mid - 0.05, mid + 0.05
        s = s if s is not None else max(0.0, e - (w["e"] - w["s"]))
        e = e if e is not None else s + (w["e"] - w["s"])
        out.append({**w, "s": round(s, 3), "e": round(max(e, s + 0.05), 3)})
    for a, b in zip(out, out[1:]):
        if b["s"] < a["e"]:
            a["e"] = max(a["s"] + 0.03, b["s"])
    return out


def paginas(palabras: list[dict], dur: float) -> list[dict]:
    """Páginas de subtítulos (1–3 palabras) con la ventana de cada palabra, en tiempo de programa."""
    if not palabras:
        return []
    pw = []
    for k, w in enumerate(palabras):
        texto = w["text"]
        m = re.match(r"^(.*?)([.,;:?!…]+)$", texto)
        punct = m.group(2) if m else ""
        nxt = palabras[k + 1]["s"] if k + 1 < len(palabras) else dur
        pw.append({"id": f"w{k}", "src": "main", "text": texto, "punct": punct, "s": w["s"], "e": w["e"],
                   "gap": max(0.0, nxt - w["e"])})
    pages = capmod.group_pages(pw)
    wins = capmod.page_windows(pages, FPS, dur)
    return [{"palabras": [{"text": w["text"], "s": w["s"], "e": w["e"]} for w in p], "t0": t0, "t1": min(t1, dur)}
            for p, (t0, t1) in zip(pages, wins)]


# ───────────────────────────── audio ─────────────────────────────
def _cargar_wav(path: Path) -> np.ndarray:
    y, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if y.ndim > 1:
        y = y.mean(1)
    if sr != SR:
        raise RuntimeError(f"frecuencia inesperada {sr}")
    return y


def _cortar_audio(y: np.ndarray, tramos: list[tuple[float, float]]) -> np.ndarray:
    xf = int(SR * 0.01)
    trozos = []
    for a, b in tramos:
        seg = y[int(a * SR):int(b * SR)].copy()
        if len(seg) > 2 * xf:
            rampa = np.linspace(0.0, 1.0, xf, dtype=np.float32)
            seg[:xf] *= rampa
            seg[-xf:] *= rampa[::-1]
        trozos.append(seg)
    return np.concatenate(trozos) if trozos else y


def _lufs(y: np.ndarray) -> float:
    import pyloudnorm as pyln

    if len(y) < SR * 0.5 or float(np.max(np.abs(y))) < 1e-4:
        return -70.0
    try:
        v = float(pyln.Meter(SR).integrated_loudness(y.astype(np.float64)))
    except Exception:  # noqa: BLE001
        return -70.0
    return v if math.isfinite(v) else -70.0


def master_audio(voz: np.ndarray, work: Path, dur: float, musica: Path | None, objetivo: float, techo: float,
                 avisos: list[str]) -> Path:
    n = int(round(dur * SR))
    voz = np.pad(voz, (0, max(0, n - len(voz))))[:n]
    l_voz = _lufs(voz)
    if l_voz > -60:
        voz = voz * (10 ** ((objetivo - l_voz) / 20))
    mezcla = np.stack([voz, voz], 1)
    if musica:
        cam = work / "musica.wav"
        _ff(["-stream_loop", "-1", "-i", str(musica), "-t", f"{dur:.3f}", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le",
             str(cam)])
        m, _ = sf.read(str(cam), dtype="float32", always_2d=True)
        m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
        l_m = _lufs(m.mean(1))
        if l_m > -60:
            m = m * (10 ** ((objetivo - 18.0 - l_m) / 20))
            fi, fo = int(SR * 0.3), int(SR * min(1.0, dur / 4))
            m[:fi] *= np.linspace(0, 1, fi)[:, None]
            m[-fo:] *= np.linspace(1, 0, fo)[:, None]
            mezcla = mezcla + m
        else:
            avisos.append("la pista de música está en silencio: no se mezcla")
    crudo = work / "mezcla.wav"
    sf.write(str(crudo), np.clip(mezcla, -1.0, 1.0), SR, subtype="FLOAT")
    out = work / "master.wav"
    lim = 10 ** (techo / 20)
    _ff(["-i", str(crudo), "-af", f"alimiter=limit={lim:.4f}:attack=5:release=60:level=disabled",
         "-ar", str(SR), "-c:a", "pcm_s16le", str(out)])
    return out


# ───────────────────────────── encuadre ─────────────────────────────
def foco_horizontal(video: Path, dur: float) -> float:
    """Centro horizontal (0–1) de la cara más grande, mediana de 9 fotogramas; 0,5 si no hay caras."""
    try:
        import cv2
    except ImportError:
        return 0.5
    casc = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
    if casc.empty():
        return 0.5
    xs = []
    for k in range(9):
        t = dur * (k + 0.5) / 9
        p = subprocess.run([sistema.requiere("ffmpeg"), "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                            "-vf", "scale=480:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if p.returncode or not p.stdout:
            continue
        img = cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        caras = casc.detectMultiScale(img, scaleFactor=1.1, minNeighbors=6, minSize=(40, 40))
        if len(caras):
            x, y, w, h = max(caras, key=lambda c: c[2] * c[3])
            xs.append((x + w / 2) / img.shape[1])
    return float(np.median(xs)) if xs else 0.5


def _filtro_cubrir(w: int, h: int, foco: float) -> str:
    foco = min(1.0, max(0.0, foco))
    return (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={w}:{h}:(iw-{w})*{foco:.3f}:(ih-{h})/2,setsar=1")


# ───────────────────────────── maquetación (ASS) ─────────────────────────────
class _Medidor:
    """Mide texto como lo pintará libass: misma familia (name ID 1) y misma escala (el cuerpo ASS es el alto
    winAscent + winDescent, no el em), así que las cajas de la QA coinciden con el render."""

    def __init__(self, fuente: Path):
        from PIL import ImageFont

        from .marca import metricas_fuente

        self.fuente = fuente
        self._cache: dict[int, Any] = {}
        self.ImageFont = ImageFont
        self.metricas = metricas_fuente(fuente)
        self._escala = self.metricas["upm"] / max(1, self.metricas["alto_libass"])

    def font(self, size: int):
        if size not in self._cache:
            self._cache[size] = self.ImageFont.truetype(str(self.fuente), max(1, round(size * self._escala)))
        return self._cache[size]

    def familia(self) -> str:
        return self.metricas["familia"]

    def ancho(self, texto: str, size: int) -> float:
        return float(self.font(size).getlength(texto))

    def partir(self, texto: str, size: int, ancho_max: float) -> list[str]:
        lineas, cur = [], ""
        for p in texto.split():
            prueba = f"{cur} {p}".strip()
            if cur and self.ancho(prueba, size) > ancho_max:
                lineas.append(cur)
                cur = p
            else:
                cur = prueba
        if cur:
            lineas.append(cur)
        return lineas


def _equilibrar(med: _Medidor, texto: str, size: int, ancho_max: float, n: int) -> list[str]:
    """Mismo número de líneas con el ancho más estrecho posible: líneas parejas («¿Tu CRM pierde / leads cada
    semana?» en vez de una línea larga y una palabra suelta)."""
    lo, hi, mejor = ancho_max * 0.4, ancho_max, med.partir(texto, size, ancho_max)
    for _ in range(14):
        mid = (lo + hi) / 2
        prueba = med.partir(texto, size, mid)
        if len(prueba) <= n and all(med.ancho(x, size) <= mid + 0.5 for x in prueba):
            mejor, hi = prueba, mid
        else:
            lo = mid
    return mejor


def _ajustar(med: _Medidor, texto: str, cuerpo: int, minimo: int, ancho_max: float, max_lineas: int) -> tuple[int, list[str]]:
    size = cuerpo
    while True:
        lineas = med.partir(texto, size, ancho_max)
        if (len(lineas) <= max_lineas and all(med.ancho(x, size) <= ancho_max for x in lineas)) or size <= minimo:
            return size, (_equilibrar(med, texto, size, ancho_max, len(lineas)) if len(lineas) > 1 else lineas)
        size -= 2


def maquetar(fmt: str, cfg: dict, marca: Marca, hook: str, cta: str, pags: list[dict], dur: float, etiqueta: str | None,
             mayus: bool) -> tuple[str, list[dict]]:
    """ASS del formato y cajas de cada bloque de texto (para la QA de zona segura)."""
    W, H = cfg["width"], cfg["height"]
    f_tit, f_txt = marca.fuente("titulos"), marca.fuente("texto")
    m_tit, m_txt = _Medidor(f_tit), _Medidor(f_txt)
    fam_tit, fam_txt = m_tit.familia(), m_txt.familia()
    c_sub, c_res = marca.sub("color") or "#FFFFFF", marca.sub("resaltado") or marca.color("acento")
    c_con = marca.sub("contorno") or "#000000"
    prim, sobre = marca.color("primario"), marca.color("texto_sobre_primario")
    acento = marca.color("acento")
    sobre_acento = marca.color("texto") if contraste(acento, marca.color("texto")) >= 4.5 else (
        "#FFFFFF" if contraste(acento, "#FFFFFF") >= contraste(acento, "#000000") else "#000000")
    pad = 18
    estilos = [
        f"Style: Sub,{fam_tit},{cfg['subtitulos']['cuerpo']},{ass_color(c_sub)},{ass_color(c_res)},{ass_color(c_con)},"
        f"{ass_color('#000000', 128)},0,0,0,0,100,100,0,0,1,6,2,5,0,0,0,1",
        f"Style: Hook,{fam_tit},{cfg['hook']['cuerpo']},{ass_color(sobre)},{ass_color(sobre)},{ass_color(prim)},"
        f"{ass_color(prim)},0,0,0,0,100,100,0,0,3,{pad},0,8,0,0,0,1",
        f"Style: Cta,{fam_tit},{cfg['cta']['cuerpo']},{ass_color(sobre_acento)},{ass_color(sobre_acento)},"
        f"{ass_color(acento)},{ass_color(acento)},0,0,0,0,100,100,0,0,3,{pad},0,8,0,0,0,1",
        f"Style: Ia,{fam_txt},{cfg['etiqueta_ia']['cuerpo']},{ass_color('#FFFFFF')},{ass_color('#FFFFFF')},"
        f"{ass_color('#000000', 110)},{ass_color('#000000', 110)},0,0,0,0,100,100,0,0,3,8,0,7,0,0,0,1",
    ]
    ev: list[str] = []
    cajas: list[dict] = []

    def caja(tipo: str, t0: float, t1: float, x0: float, y0: float, x1: float, y1: float, texto: str,
             lineas: int = 1) -> None:
        cajas.append({"tipo": tipo, "t0": round(t0, 3), "t1": round(t1, 3), "texto": texto[:60], "lineas": lineas,
                      "caja": [round(x0), round(y0), round(x1), round(y1)]})

    lh = 1.02                     # libass: el cuerpo ES el alto de línea (winAscent + winDescent)
    hk = cfg["hook"]
    hook_cfg = (cfg.get("_hook") or {})
    if hook:
        texto = hook.upper() if mayus else hook
        size, lineas = _ajustar(m_tit, texto, hk["cuerpo"], hk["cuerpo_min"], hk["ancho_max"] - 2 * pad, 3)
        t1 = min(dur, float(hook_cfg.get("duracion", 2.5)))
        txt = r"\N".join(_ass_texto(x) for x in lineas)
        ev.append(f"Dialogue: 2,{_tc_ass(0)},{_tc_ass(t1)},Hook,,0,0,0,,"
                  f"{{\\an8\\pos({W // 2},{hk['y']})\\fs{size}\\fscx94\\fscy94\\t(0,160,\\fscx100\\fscy100)\\fad(0,140)}}{txt}")
        wmax = max(m_tit.ancho(x, size) for x in lineas)
        caja("hook", 0, t1, W / 2 - wmax / 2 - pad, hk["y"] - pad, W / 2 + wmax / 2 + pad,
             hk["y"] + len(lineas) * size * lh + pad, texto, len(lineas))
    sc = cfg["subtitulos"]
    for pg in pags:
        ws = pg["palabras"]
        textos = [(w["text"].upper() if mayus else w["text"]) for w in ws]
        frase = " ".join(textos)
        size = sc["cuerpo"]
        while m_tit.ancho(frase, size) > sc["ancho_max"] and size > 44:
            size -= 2
        for k, w in enumerate(ws):
            a = pg["t0"] if k == 0 else max(pg["t0"], w["s"] - 1 / FPS)
            z = pg["t1"] if k == len(ws) - 1 else max(pg["t0"], ws[k + 1]["s"] - 1 / FPS)
            if z - a < 0.02:
                continue
            partes = [(f"{{\\c{ass_color(c_res)}}}{_ass_texto(t)}{{\\c{ass_color(c_sub)}}}" if i == k else _ass_texto(t))
                      for i, t in enumerate(textos)]
            ev.append(f"Dialogue: 1,{_tc_ass(a)},{_tc_ass(z)},Sub,,0,0,0,,{{\\an5\\pos({W // 2},{sc['y_centro']})"
                      f"\\fs{size}}}{' '.join(partes)}")
        wpx = m_tit.ancho(frase, size) + 12
        caja("subtitulo", pg["t0"], pg["t1"], W / 2 - wpx / 2, sc["y_centro"] - size * lh / 2 - 6, W / 2 + wpx / 2,
             sc["y_centro"] + size * lh / 2 + 6, frase)
    ct = cfg["cta"]
    cta_cfg = cfg.get("_cta") or {}
    if cta:
        texto = cta.upper() if mayus else cta
        size, lineas = _ajustar(m_tit, texto, ct["cuerpo"], 40, ct["ancho_max"] - 2 * pad, 2)
        t0 = max(0.0, dur - float(cta_cfg.get("duracion", 2.5)))
        txt = r"\N".join(_ass_texto(x) for x in lineas)
        ev.append(f"Dialogue: 2,{_tc_ass(t0)},{_tc_ass(dur)},Cta,,0,0,0,,"
                  f"{{\\an8\\pos({W // 2},{ct['y']})\\fs{size}\\fscx92\\fscy92\\t(0,180,\\fscx100\\fscy100)\\fad(120,0)}}{txt}")
        wmax = max(m_tit.ancho(x, size) for x in lineas)
        caja("cta", t0, dur, W / 2 - wmax / 2 - pad, ct["y"] - pad, W / 2 + wmax / 2 + pad,
             ct["y"] + len(lineas) * size * lh + pad, texto, len(lineas))
    if etiqueta:
        ia = cfg["etiqueta_ia"]
        ev.append(f"Dialogue: 3,{_tc_ass(0)},{_tc_ass(dur)},Ia,,0,0,0,,{{\\an7\\pos({ia['x'] + 8},{ia['y'] - 8 - ia['cuerpo']})}}"
                  f"{_ass_texto(etiqueta)}")
        wpx = m_txt.ancho(etiqueta, ia["cuerpo"])
        caja("etiqueta_ia", 0, dur, ia["x"], ia["y"] - 16 - ia["cuerpo"] * lh, ia["x"] + wpx + 16, ia["y"], etiqueta)
    ass = "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2",
        "ScaledBorderAndShadow: yes", "YCbCr Matrix: TV.709", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
        "MarginV, Encoding",
        *estilos, "",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        *ev, ""])
    return ass, cajas


# ───────────────────────────── QA ─────────────────────────────
def _fuera_de_zona(caja: list[int], zona: dict, W: int, H: int) -> dict[str, int]:
    x0, y0, x1, y1 = caja
    der = W - zona["right"]
    fr = zona.get("franja_derecha")
    if fr and y1 > fr["desde_y"]:
        der = min(der, fr["x"])
    intr = {"arriba": zona["top"] - y0, "abajo": y1 - (H - zona["bottom"]), "izquierda": zona["left"] - x0,
            "derecha": x1 - der}
    return {k: int(v) for k, v in intr.items() if v > 2}


def _voz_al_inicio(y: np.ndarray) -> float:
    """Segundos hasta que empieza a sonar algo claramente (−40 dBFS en ventanas de 20 ms)."""
    hop = int(SR * 0.02)
    n = len(y) // hop
    if n == 0:
        return 0.0
    db = 20 * np.log10(np.sqrt((y[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12) + 1e-9)
    idx = np.nonzero(db > -40)[0]
    return float(idx[0] * 0.02) if len(idx) else float(n * 0.02)


def qa_formato(salida: Path, fmt: str, cfg: dict, prof: dict, cajas: list[dict], pags: list[dict], hook: str,
               voz_prog: np.ndarray, work: Path) -> dict:
    W, H = cfg["width"], cfg["height"]
    q = prof["anuncio"]
    issues: list[dict] = []

    def add(check: str, sev: str, msg: str, **ev):
        issues.append({"check": check, "severidad": sev, "mensaje": msg, **({"evidencia": ev} if ev else {})})

    info = sondear(salida)
    v, a = info["video"] or {}, info["audio"]
    if (v.get("width"), v.get("height")) != (W, H):
        add("formato.resolucion", "block", f"resolución {v.get('width')}×{v.get('height')}, se esperaba {W}×{H}")
    ratio = (v.get("width") or 1) / (v.get("height") or 1)
    if abs(ratio - W / H) / (W / H) > 0.01:
        add("formato.ratio", "block", "el ratio se sale de la tolerancia del 1 % de Meta")
    if v.get("codec_name") != "h264" or v.get("pix_fmt") != "yuv420p":
        add("formato.codec", "warn", f"vídeo {v.get('codec_name')}/{v.get('pix_fmt')} (recomendado h264/yuv420p)")
    if not a:
        add("audio.pista", "block", "el máster no tiene audio")
    elif a.get("codec_name") != "aac":
        add("audio.codec", "warn", f"audio {a.get('codec_name')} (recomendado AAC)")
    if info["fps"] and abs(info["fps"] - FPS) > 0.05:
        add("formato.fps", "warn", f"{_n(info['fps'], 2)} fps (se esperaban {FPS})")
    dur = info["duration"]
    if dur > q["calidad"]["duracion_max_recomendada"]:
        add("ritmo.duracion", "warn", f"dura {_n(dur)} s: para un anuncio suele rendir mejor una pieza más corta; "
                                      "pruébalo frente a una versión recortada [HYPOTHESIS]")
    # hook
    hk = [c for c in cajas if c["tipo"] == "hook"]
    if not hook:
        add("hook.texto", "warn", "sin hook escrito en pantalla: los 2 primeros segundos dependen solo de la imagen y la voz")
    elif hk and hk[0]["t0"] > q["hook"]["inicio_max"]:
        add("hook.tarde", "block", f"el hook entra en {_n(hk[0]['t0'], 2)} s (máximo {_n(q['hook']['inicio_max'])} s)")
    elif hk and hk[0]["t1"] - hk[0]["t0"] > 3.5:
        add("hook.largo", "warn", "el hook dura más de 3,5 s en pantalla")
    if hk and hk[0].get("lineas", 1) > 3:
        add("hook.texto_largo", "warn", f"el hook ocupa {hk[0]['lineas']} líneas incluso con el cuerpo mínimo: "
                                        "acórtalo a lo que se lee de un vistazo (unas 6–8 palabras) [HYPOTHESIS]")
    ct = [c for c in cajas if c["tipo"] == "cta"]
    if ct and ct[0].get("lineas", 1) > 2:
        add("cta.texto_largo", "warn", f"la CTA ocupa {ct[0]['lineas']} líneas: déjala en una acción corta "
                                       "(«Reserva tu llamada»)")
    t_voz = _voz_al_inicio(voz_prog)
    if t_voz > 0.7:
        add("hook.silencio", "warn", f"la voz empieza en {_n(t_voz, 2)} s: el arranque queda mudo [HYPOTHESIS: > 0,7 s]")
    # subtítulos
    if not pags:
        add("subtitulos.faltan", "warn", "sin subtítulos: añádelos para Feed y para quien ve sin sonido")
    else:
        cubierto = sum(p["t1"] - p["t0"] for p in pags)
        hablado = sum(w["e"] - w["s"] for p in pags for w in p["palabras"])
        if hablado and cubierto / max(hablado, 1e-6) < 0.8:
            add("subtitulos.cobertura", "warn", "los subtítulos cubren menos del 80 % del tiempo hablado")
        cortas = [p for p in pags if p["t1"] - p["t0"] < 0.3]
        if cortas:
            add("subtitulos.rapidos", "warn", f"{len(cortas)} página(s) de subtítulos duran < 0,3 s")
    # zona segura
    zona = cfg["zona_segura"]
    for c in cajas:
        fuera = _fuera_de_zona(c["caja"], zona, W, H)
        if fuera:
            sev = "block" if max(fuera.values()) >= 8 else "warn"
            add("texto.zona_segura", sev, f"{c['tipo']} «{c['texto']}» se sale de la zona segura ({fuera})", caja=c["caja"])
    # sonoridad y arranque
    wav = work / f"qa_{fmt}.wav"
    _ff(["-i", str(salida), "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(wav)])
    y = _cargar_wav(wav)
    lufs = _lufs(y)
    pico = float(20 * np.log10(np.max(np.abs(y)) + 1e-9)) if len(y) else -120.0
    obj, tol = prof["loudness"]["lufs"], q["calidad"]["lufs_tolerancia"]
    if lufs > -60 and abs(lufs - obj) > tol:
        add("audio.sonoridad", "warn", f"sonoridad {_n(lufs)} LUFS (objetivo {_n(obj)} ± {_n(tol)})")
    if pico > -0.9:
        add("audio.pico", "warn", f"pico de {_n(pico)} dBFS (techo −1,5 dBTP)")
    p = subprocess.run([sistema.requiere("ffmpeg"), "-hide_banner", "-t", "1", "-i", str(salida), "-vf",
                        "blackdetect=d=0.2:pic_th=0.95", "-an", "-f", "null", "-"], capture_output=True, text=True)
    if "black_start:0" in p.stderr:
        add("imagen.arranque_negro", "warn", "el vídeo arranca en negro: el primer fotograma tiene que enganchar")
    veredicto = "fail" if any(i["severidad"] == "block" for i in issues) else (
        "warn" if any(i["severidad"] == "warn" for i in issues) else "pass")
    return {"formato": fmt, "archivo": salida.name, "veredicto": veredicto, "duracion": round(dur, 3),
            "ancho": v.get("width"), "alto": v.get("height"), "lufs": round(lufs, 1), "pico_dbfs": round(pico, 1),
            "voz_empieza_s": round(t_voz, 2), "cajas": cajas, "issues": issues}


# ───────────────────────────── LEEME ─────────────────────────────
_INI, _FIN = "<!-- cutkit:qa -->", "<!-- /cutkit:qa -->"


def _bloque_qa(res: dict) -> str:
    filas = [f"| `{q['archivo']}` | {q['ancho']}×{q['alto']} | {_n(q['duracion'])} s | {_n(q['lufs'])} LUFS | "
             f"**{q['veredicto']}** |" for q in res["qa"]]
    avisos = [f"- {q['formato']}: {i['severidad']} · {i['check']} — {i['mensaje']}" for q in res["qa"] for i in q["issues"]]
    avisos += [f"- montaje: {a}" for a in res["avisos"]]
    return "\n".join([
        _INI, "## QA técnica (cutkit)", "",
        f"Generado por `ck anuncio` el {res['fecha']} · perfil `{res['perfil']}` · subtítulos: {res['subtitulos']} · "
        f"silencios quitados: {_n(res['silencios_quitados_s'])} s.", "",
        "| Archivo | Resolución | Duración | Sonoridad | Veredicto |", "|---|---|---|---|---|", *filas, "",
        *(avisos or ["- Sin avisos."]), _FIN])


PLANTILLA_LEEME = RAIZ / ".claude" / "skills" / "producir-video" / "plantilla-leeme.md"
_UBICACIONES = {"9x16": ("9:16", "Reels, Stories"), "4x5": ("4:5", "Feed")}


def _filas_archivos(res: dict, nombre: str, hook: str) -> list[str]:
    filas = []
    for a in res.get("archivos", []):
        p = Path(a)
        fmt = next((f for f in _UBICACIONES if p.stem.endswith(f"_{f}")), None)
        if fmt:
            ratio, ubic = _UBICACIONES[fmt]
            filas.append(f"| {p.name} | {nombre} | {ratio} | {ubic} | «{hook or '—'}» |")
    return filas


def _leeme_nuevo(nombre: str, res: dict, op: Opciones, bloque: str) -> str:
    """LEEME de una pieza nueva: la plantilla del producto (si existe) rellenada con lo que sabe cutkit."""
    via = "hibrido" if op.etiqueta_ia else "propio"
    filas = _filas_archivos(res, nombre, op.hook)
    if PLANTILLA_LEEME.exists():
        txt = PLANTILLA_LEEME.read_text(encoding="utf-8")
        lineas, fuera = [], False
        for linea in txt.splitlines():
            if linea.startswith("| <nombre-base>_"):          # filas de ejemplo de la tabla de archivos
                if not fuera:
                    lineas.extend(filas)
                    fuera = True
                continue
            lineas.append(linea)
        txt = "\n".join(lineas) + "\n"
        for viejo, nuevo in (("# <nombre-base>", f"# {nombre}"), ("**Cliente:** <slug>", f"**Cliente:** {op.cliente or '—'}"),
                             ("**Vía:** ia | propio | hibrido | estatico", f"**Vía:** {via}"),
                             ("**Proyecto del motor / run de cutkit / plantilla HTML:** <id o ruta>",
                              "**Proyecto del motor / run de cutkit / plantilla HTML:** `ck anuncio` (edicion/anuncio/)"),
                             ("- QA técnico (motor, cutkit o render): <veredicto y problemas>",
                              f"- QA técnico (cutkit): **{res['veredicto']}**; detalle en el bloque de QA de abajo"),
                             ("- Motor: <$ reales de `motor costs <id>`> · imagen IA: <$> · tiempo de grabación y montaje: <h>",
                              "- Montaje con cutkit: 0 $ (local) · tiempo de grabación y montaje: <h>")):
            txt = txt.replace(viejo, nuevo)
        if "## Coste" in txt:
            txt = txt.replace("## Coste", bloque + "\n\n## Coste", 1)
        else:
            txt = txt.rstrip() + "\n\n" + bloque + "\n"
    else:
        txt = "\n".join([
            f"# {nombre}", "",
            "- **Estado:** borrador",
            "- **Veredicto de políticas:** pendiente",
            f"- **Cliente:** {op.cliente or '—'} · **Vía:** {via} (montaje con cutkit)", "",
            "## Archivos", "", "| Archivo | Nombre del anuncio | Formato | Ubicaciones | Hook |", "|---|---|---|---|---|",
            *filas, "",
            "## Afirmaciones y prueba", "", "| Afirmación | Fuente |", "|---|---|", "",
            "## Calidad", "", f"- QA técnico (cutkit): **{res['veredicto']}**", "", bloque, ""])
    for linea in ("- **Estado:** borrador", "- **Veredicto de políticas:** pendiente"):
        if linea.split(":**")[0] not in txt:                     # el contrato exige las dos líneas
            txt = txt.replace("\n\n", f"\n\n{linea}\n", 1)
    return txt


def escribir_leeme(destino: Path, res: dict, op: Opciones) -> Path:
    """Crea el LEEME de la pieza (plantilla del producto) o, si ya existe, solo actualiza su bloque de QA."""
    f = destino / "LEEME.md"
    bloque = _bloque_qa(res)
    if f.exists():
        txt = f.read_text(encoding="utf-8")
        if _INI in txt and _FIN in txt:
            txt = txt[:txt.index(_INI)] + bloque + txt[txt.index(_FIN) + len(_FIN):]
        else:
            txt = txt.rstrip() + "\n\n" + bloque + "\n"
        f.write_text(txt, encoding="utf-8")
        return f
    f.write_text(_leeme_nuevo(op.nombre or op.slug, res, op, bloque), encoding="utf-8")
    return f


# ───────────────────────────── orquestación ─────────────────────────────
def _parse_broll(spec: str) -> tuple[float, float, Path]:
    m = re.fullmatch(r"\s*([\d.]+)\s*-\s*([\d.]+)\s*:(.+)", spec)
    if not m:
        raise ErrorUsuario(f"B-roll no válido: {spec!r} (usa INICIO-FIN:ruta, p. ej. 3.2-5.5:demo.mp4)")
    a, b, p = float(m.group(1)), float(m.group(2)), Path(m.group(3).strip())
    if b <= a:
        raise ErrorUsuario(f"B-roll {spec!r}: el fin debe ser mayor que el inicio")
    if not p.exists():
        raise ErrorUsuario(f"no existe el B-roll {p}")
    return a, b, p


def _mismo_archivo(a: Path, b: Path) -> bool:
    try:
        if a.samefile(b):
            return True
    except OSError:
        return False
    sa, sb = a.stat(), b.stat()
    return sa.st_size == sb.st_size and int(sa.st_mtime) == int(sb.st_mtime)     # copia hecha con copy2


def _guardar_bruto(entrada: Path, destino: Path) -> Path:
    """Deja el bruto en `<proyecto>/brutos/` (enlace duro o copia) y devuelve esa ruta. Nunca pisa ni confunde otro
    bruto con el mismo nombre: si ya hay uno distinto, guarda este como `<nombre>-2`, `<nombre>-3`…"""
    entrada = entrada.resolve()
    brutos = destino.resolve() / "brutos"
    if brutos in entrada.parents:
        return entrada
    brutos.mkdir(parents=True, exist_ok=True)
    dst, n = brutos / entrada.name, 2
    while dst.exists() and not _mismo_archivo(dst, entrada):
        dst, n = brutos / f"{entrada.stem}-{n}{entrada.suffix}", n + 1
    if not dst.exists():
        try:
            dst.hardlink_to(entrada)
        except OSError:
            shutil.copy2(entrada, dst)
    return dst


def montar(op: Opciones) -> dict:
    sistema.requiere("ffmpeg")
    sistema.requiere("ffprobe")
    if not op.entrada.exists():
        raise ErrorUsuario(f"no existe el bruto {op.entrada}")
    prof = _perfil(op.perfil)
    q = prof["anuncio"]
    desconocidos = [f for f in op.formatos if f not in q["formatos"]]
    if desconocidos or not op.formatos:
        raise ErrorUsuario(f"formato no soportado: {', '.join(desconocidos) or '(ninguno)'} (hay: {', '.join(q['formatos'])})")
    marca = cargar_marca(op.cliente, op.marca)
    avisos: list[str] = list(marca.avisos)
    destino = Path(op.salida) if op.salida else proyecto_dir(op.slug, op.cliente, op.fecha, crear=True)
    destino.mkdir(parents=True, exist_ok=True)
    work = destino / "edicion" / "anuncio"
    work.mkdir(parents=True, exist_ok=True)
    bruto = _guardar_bruto(op.entrada, destino) if not op.salida else op.entrada
    info = sondear(bruto)
    if not info["video"]:
        raise ErrorUsuario(f"{bruto.name} no tiene pista de vídeo")
    dur_src = info["duration"]
    if dur_src < 1.0:
        raise ErrorUsuario(f"{bruto.name} dura {_n(dur_src, 2)} s: demasiado corto para un anuncio")

    # 1. voz a 48 kHz mono
    voz_wav = work / "voz_bruta.wav"
    if info["audio"]:
        _ff(["-i", str(bruto), "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(voz_wav)])
        y = _cargar_wav(voz_wav)
        if float(np.sqrt(np.mean(y ** 2) + 1e-12)) < 10 ** (-60 / 20):
            avisos.append("el audio del bruto está prácticamente en silencio: revisa el micrófono")
    else:
        avisos.append("el bruto no tiene audio: el anuncio sale con una pista muda (en Reels se ve con sonido)")
        y = np.zeros(int(dur_src * SR), dtype=np.float32)
        sf.write(str(voz_wav), y, SR, subtype="PCM_16")

    # 2. silencios
    s_cfg = q["silencios"]
    tramos = (tramos_con_voz(y, s_cfg["umbral_db"], s_cfg["minimo"], s_cfg["margen"])
              if op.quitar_silencios and info["audio"] else [(0.0, dur_src)])
    tramos = [(a, min(b, dur_src)) for a, b in tramos if a < dur_src] or [(0.0, dur_src)]
    dur = round(sum(b - a for a, b in tramos), 3)
    quitado = dur_src - dur

    # 3. subtítulos
    palabras, origen_sub = palabras_de(op, voz_wav, avisos)
    palabras = _remapear(palabras, tramos) if palabras else []
    pags = paginas(palabras, dur)

    # 4. vídeo cortado (CFR 30) y audio
    programa = work / "programa.mp4"
    filtros = [f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,fps={FPS}[v{k}]" for k, (a, b) in enumerate(tramos)]
    filtros.append("".join(f"[v{k}]" for k in range(len(tramos))) + f"concat=n={len(tramos)}:v=1:a=0[out]")
    _ff(["-i", str(bruto), "-filter_complex", ";".join(filtros), "-map", "[out]", "-an",
         *sistema.codec_video("intermedio", FPS), str(programa)])
    voz_prog = _cortar_audio(y, tramos)
    if op.procesar_voz and info["audio"]:
        try:
            from .audio import voice as voicemod

            crudo = work / "voz_programa.wav"
            sf.write(str(crudo), voz_prog, SR, subtype="PCM_24")
            tratado = work / "voz_tratada.wav"
            voicemod.process(str(crudo), str(tratado))
            voz_prog = _cargar_wav(tratado)
        except Exception as e:  # noqa: BLE001 — la voz sin tratar es mejor que no tener anuncio
            avisos.append(f"cadena de voz no aplicada ({type(e).__name__}): se usa la voz original")
    musica = None
    if op.musica and op.musica != "no":
        musica = Path(op.musica)
        if not musica.exists():
            raise ErrorUsuario(f"no existe la pista de música {musica}")
        avisos.append("cama musical: confirma que tienes derechos de uso en publicidad (en anuncios de Reels no vale "
                      "música con licencia comercial)")
    master = master_audio(voz_prog, work, dur, musica, prof["loudness"]["lufs"], prof["loudness"]["true_peak"], avisos)

    foco = 0.5
    if op.foco == "auto":
        foco = foco_horizontal(programa, dur)
    elif op.foco != "centro":
        try:
            foco = float(op.foco)
        except ValueError:
            raise ErrorUsuario(f"--foco no válido: {op.foco!r} (auto, centro o un número de 0 a 1)") from None
    brolls = [_parse_broll(b) for b in op.broll]
    cta = op.cta if op.cta is not None else (marca.datos.get("cta_por_defecto") or "")
    mayus = bool(marca.sub("mayusculas")) if op.mayusculas is None else op.mayusculas
    etiqueta = (marca.datos.get("etiqueta_ia") or "Contenido generado con IA") if op.etiqueta_ia else None
    logo = marca.logo("claro") or marca.logo("principal") if op.logo != "no" else None
    if op.logo != "no" and logo is None and marca.datos.get("logo"):
        avisos.append("logo sin versión PNG/JPG utilizable: el vídeo sale sin logo")

    fuentes = work / "fuentes"
    fuentes.mkdir(exist_ok=True)
    for f in {marca.fuente("titulos"), marca.fuente("texto")}:
        shutil.copy2(f, fuentes / f.name)

    nombre = op.nombre or op.slug
    salidas, qas = [], []
    for fmt in op.formatos:
        cfg = dict(q["formatos"][fmt], _hook=q["hook"], _cta=q["cta"])
        W, H = cfg["width"], cfg["height"]
        ass, cajas = maquetar(fmt, cfg, marca, op.hook, cta, pags, dur, etiqueta, mayus)
        (work / f"texto_{fmt}.ass").write_text(ass, encoding="utf-8")
        entradas = ["-i", str(programa), "-i", str(master)]
        graf = [f"[0:v]{_filtro_cubrir(W, H, foco)}[b0]"]
        cur, idx = "b0", 2
        for k, (a, b, p) in enumerate(brolls):
            if a >= dur:
                avisos.append(f"B-roll {p.name} empieza después del final ({_n(a)} s ≥ {_n(dur)} s): se ignora")
                continue
            b = min(b, dur)
            entradas += ["-i", str(p)]
            graf.append(f"[{idx}:v]trim=duration={b - a:.3f},setpts=PTS-STARTPTS+{a:.3f}/TB,{_filtro_cubrir(W, H, 0.5)}"
                        f"[r{k}]")
            graf.append(f"[{cur}][r{k}]overlay=enable='between(t,{a:.3f},{b:.3f})':eof_action=pass[o{k}]")
            cur, idx = f"o{k}", idx + 1
        if logo is not None:
            l_cfg = cfg["logo"]
            t0 = 0.0 if op.logo == "siempre" else max(0.0, dur - float(q["cta"]["duracion"]))
            y_logo = l_cfg["y"] if op.logo != "siempre" else cfg["zona_segura"]["top"] + 8
            alto = l_cfg["alto"] if op.logo != "siempre" else int(l_cfg["alto"] * 0.55)
            entradas += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(logo)]
            graf.append(f"[{idx}:v]scale=-1:{alto},format=rgba,fade=t=in:st={t0:.3f}:d=0.25:alpha=1[lg]")
            x_logo = "(W-w)/2" if op.logo != "siempre" else str(cfg["zona_segura"]["left"] + 8)
            graf.append(f"[{cur}][lg]overlay=x={x_logo}:y={y_logo}:enable='gte(t,{t0:.3f})'[ol]")
            cur, idx = "ol", idx + 1
            if op.logo == "siempre" and op.hook:
                avisos.append("logo fijo arriba a la izquierda: revisa que no compita con el hook")
        graf.append(f"[{cur}]ass=texto_{fmt}.ass:fontsdir=fuentes[vout]")
        out = destino / f"{nombre}_{fmt}.mp4"
        _ff([*entradas, "-filter_complex", ";".join(graf), "-map", "[vout]", "-map", "1:a", "-t", f"{dur:.3f}",
             "-r", str(FPS), *sistema.codec_video("master", FPS), "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
             "-movflags", "+faststart", str(out.resolve())], cwd=work)
        salidas.append(out)
        qas.append(qa_formato(out, fmt, cfg, prof, cajas, pags, op.hook, voz_prog, work))

    srt = destino / f"{nombre}.srt"
    srt.write_text("".join(f"{k + 1}\n{_tc_srt(p['t0'])} --> {_tc_srt(p['t1'])}\n"
                           f"{' '.join(w['text'] for w in p['palabras'])}\n\n" for k, p in enumerate(pags)),
                   encoding="utf-8")
    import datetime as _dt

    veredicto = "fail" if any(x["veredicto"] == "fail" for x in qas) else (
        "warn" if any(x["veredicto"] == "warn" for x in qas) or avisos else "pass")
    res = {"ok": veredicto != "fail", "veredicto": veredicto, "proyecto": str(destino), "cliente": op.cliente,
           "archivos": [str(s) for s in salidas] + [str(srt)], "duracion": dur, "silencios_quitados_s": round(quitado, 2),
           "tramos": tramos, "subtitulos": origen_sub, "paginas_subtitulos": len(pags), "foco": round(foco, 3),
           "marca": marca.nombre or "neutra", "perfil": op.perfil, "cta": cta, "avisos": avisos, "qa": qas,
           "fecha": _dt.date.today().isoformat()}
    (destino / "qa_anuncio.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    escribir_leeme(destino, res, op)
    return res
