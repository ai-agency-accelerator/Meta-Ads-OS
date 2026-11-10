#!/usr/bin/env python3
"""Edición mínima de vídeo con FFmpeg: la alternativa ligera a cutkit para anuncios de Meta.

Subcomandos:
  info         duración, resolución, fps, audio y si cumple 9:16, 4:5 o 1:1 (tolerancia de Instagram: 1 %)
  cortar       recorte preciso por tiempos y, si quieres, quita los silencios (cortes de salto con la voz en sincronía)
  reformatear  9x16 (1080×1920), 4x5 (1080×1350) o 1x1 (1080×1080): recorte con foco, relleno o fondo desenfocado
  subtitular   quema un SRT con la tipografía y los colores de la marca, dentro de la zona segura
  texto-hook   rótulo del hook en los primeros segundos (2 por defecto), dentro de la zona segura

Ejemplos:
  python3 -I herramientas/editar_video.py info bruto.mp4 --json
  python3 -I herramientas/editar_video.py cortar bruto.mp4 --desde 1.2 --hasta 24 --quitar-silencios --salida corte.mp4
  python3 -I herramientas/editar_video.py reformatear corte.mp4 --formato 9x16 --modo desenfoque --salida v_9x16.mp4
  python3 -I herramientas/editar_video.py subtitular v_9x16.mp4 --srt v.srt --cliente acme --salida v_subs.mp4
  python3 -I herramientas/editar_video.py texto-hook v_subs.mp4 --texto "¿Tu CRM pierde leads?" --cliente acme

Opciones comunes: --salida <mp4> (por defecto, junto a la entrada con un sufijo), --sobrescribir, --fps 30,
--borrador (codificación rápida para revisar), --json. Marca: --cliente SLUG lee clientes/<slug>/marca/marca.json;
--marca <ruta> prevalece. Sin marca se usa una neutra (Montserrat, caja blanca y texto negro).

Zonas seguras (meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md): en 9:16 deja libre el
14 % de arriba, el 35 % de abajo y el 6 % de cada lado [OFFICIAL META]; subtítulos en el tercio central, no abajo
[STRONG INFERENCE]; en 4:5 y 1:1 se usa un margen del 5 % [HYPOTHESIS].

Códigos de salida: 0 ok · 1 error tuyo (rutas, argumentos, SRT, marca) · 2 configuración (FFmpeg ausente o
incompleto). Necesita ffmpeg y ffprobe con libass (subtítulos y hook) y un codificador H.264 (libx264).
Solo biblioteca estándar. Quita los metadatos de la fuente (p. ej. la ubicación GPS de un móvil).
"""
from __future__ import annotations

import argparse
import functools
import json
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402

PRODUCTO = pathlib.Path(__file__).resolve().parent.parent

FORMATOS = {"9x16": (1080, 1920), "4x5": (1080, 1350), "1x1": (1080, 1080)}
# (arriba, abajo, lados) en fracción del lienzo
ZONAS = {"9x16": (0.14, 0.35, 0.06), "4x5": (0.05, 0.05, 0.05), "1x1": (0.05, 0.05, 0.05)}
ZONA_GENERICA = (0.05, 0.05, 0.05)
TOLERANCIA_RATIO = 0.01  # Instagram: 1 % [OFFICIAL META]

MARCA_NEUTRA = {
    "nombre": "",
    "colores": {"primario": "#FFFFFF", "secundario": "#111111", "acento": "#FFD400", "fondo": "#000000",
                "texto": "#FFFFFF", "texto_sobre_primario": ""},
    "tipografias": {"titulos": {"familia": "", "archivo": "", "peso": 800},
                    "texto": {"familia": "", "archivo": "", "peso": 500}},
    "logo": {"principal": "", "claro": ""},
    "subtitulos": {"color": "#FFFFFF", "resaltado": "#FFD400", "contorno": "#000000", "mayusculas": False},
    "cta_por_defecto": "",
    "etiqueta_ia": "",
}

# Fuente por defecto: Montserrat ExtraBold (SIL OFL 1.1), incluida en el producto.
FUENTES_POR_DEFECTO = [
    PRODUCTO / "modulos" / "motor-ia" / "motor" / "assets" / "Montserrat-ExtraBold.ttf",
    PRODUCTO / "plantillas" / "html" / "fuentes" / "Montserrat-ExtraBold.ttf",
]
DIRS_FUENTES = [PRODUCTO / "plantillas" / "html" / "fuentes", PRODUCTO / "modulos" / "motor-ia" / "motor" / "assets"]

ARREGLO_FFMPEG = ("Instala FFmpeg y abre otra terminal: Mac `brew install ffmpeg` · Linux `sudo apt install ffmpeg` · "
                  "Windows `winget install Gyan.FFmpeg`.")


def _n(x: float, decimales: int = 2) -> str:
    """Número para leer en español: coma decimal y sin ceros sobrantes (2,5 · 1,75 · -35)."""
    t = f"{x:.{decimales}f}"
    if decimales:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


class ErrorUsuario(Exception):
    codigo = 1

    def __init__(self, mensaje: str, arreglo: str = ""):
        super().__init__(mensaje)
        self.arreglo = arreglo


class ErrorConfig(ErrorUsuario):
    codigo = 2


# ─────────────────────────────── FFmpeg ───────────────────────────────

def _bin(nombre: str) -> str:
    ruta = shutil.which(nombre)
    if not ruta:
        raise ErrorConfig(f"No encuentro `{nombre}` en el PATH.", ARREGLO_FFMPEG)
    return ruta


def _ejecutar(cmd: list[str], cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)


@functools.lru_cache(maxsize=None)
def _capacidades(ffmpeg: str) -> dict:
    def nombres(salida: str) -> set[str]:
        return {m.group(1) for m in re.finditer(r"^\s*[A-Z.|]{2,6}\s+(\S+)\s", salida, re.M)}

    filtros = nombres(_ejecutar([ffmpeg, "-hide_banner", "-filters"]).stdout)
    codificadores = nombres(_ejecutar([ffmpeg, "-hide_banner", "-encoders"]).stdout)
    m = re.search(r"ffmpeg version n?(\d+)\.(\d+)", _ejecutar([ffmpeg, "-version"]).stdout)
    version = (int(m.group(1)), int(m.group(2))) if m else (99, 0)  # compilaciones git: recientes
    return {"filtros": filtros, "codificadores": codificadores, "version": version}


def _requiere_libass(caps: dict) -> None:
    if "ass" not in caps["filtros"]:
        raise ErrorConfig("Tu FFmpeg no trae libass (filtro `ass`), que hace falta para subtítulos y rótulos.",
                          "Instala una compilación completa: Mac `brew install ffmpeg` · Linux `sudo apt install ffmpeg` · "
                          "Windows `winget install Gyan.FFmpeg` (la «full»).")


def _ffmpeg(args: list[str], cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    r = _ejecutar([_bin("ffmpeg"), "-hide_banner", "-nostdin", "-y", *args], cwd=cwd)
    if r.returncode != 0:
        cola = "\n".join(r.stderr.strip().splitlines()[-6:])
        raise ErrorUsuario(f"FFmpeg falló (código {r.returncode}):\n{cola}")
    return r


def _fraccion(texto: str | None) -> float | None:
    if not texto or texto in ("0/0", "N/A"):
        return None
    try:
        if "/" in texto:
            n, d = texto.split("/", 1)
            return float(n) / float(d) if float(d) else None
        return float(texto)
    except ValueError:
        return None


def sondear(ruta: pathlib.Path) -> dict:
    """Duración, tamaño visible (con la rotación aplicada), fps y audio de un vídeo."""
    if not ruta.is_file():
        raise ErrorUsuario(f"No existe el vídeo: {ruta}")
    r = _ejecutar([_bin("ffprobe"), "-v", "error", "-show_entries",
                   "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,duration"
                   ":stream_tags=rotate:stream_side_data=rotation", "-of", "json", str(ruta)])
    if r.returncode != 0:
        raise ErrorUsuario(f"{ruta.name} no es un vídeo legible: {r.stderr.strip()[-300:]}")
    j = json.loads(r.stdout or "{}")
    streams = j.get("streams") or []
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not v:
        raise ErrorUsuario(f"{ruta.name} no tiene pista de vídeo.")
    ancho, alto = int(v.get("width") or 0), int(v.get("height") or 0)
    rot = 0
    for sd in v.get("side_data_list") or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = rot or int(float((v.get("tags") or {}).get("rotate", 0) or 0))
    if abs(rot) % 180 == 90:
        ancho, alto = alto, ancho
    duracion = _fraccion((j.get("format") or {}).get("duration")) or _fraccion(v.get("duration")) or 0.0
    fps = _fraccion(v.get("avg_frame_rate")) or _fraccion(v.get("r_frame_rate")) or 0.0
    return {"duracion": duracion, "duracion_video": _fraccion(v.get("duration")) or duracion, "ancho": ancho,
            "alto": alto, "fps": round(fps, 3), "audio": a is not None, "codec_audio": (a or {}).get("codec_name"),
            "codec_video": v.get("codec_name")}


def detectar_formato(ancho: int, alto: int) -> str | None:
    if not ancho or not alto:
        return None
    for nombre, (w, h) in FORMATOS.items():
        if abs((ancho / alto) / (w / h) - 1) <= TOLERANCIA_RATIO:
            return nombre
    return None


def _args_video(caps: dict, borrador: bool) -> list[str]:
    cod = caps["codificadores"]
    if "libx264" in cod:
        return ["-c:v", "libx264", "-preset", "ultrafast" if borrador else "medium", "-crf", "23" if borrador else "18",
                "-profile:v", "high", "-pix_fmt", "yuv420p"]
    for alt in ("h264_videotoolbox", "h264_mf", "h264_nvenc", "h264_qsv"):
        if alt in cod:
            return ["-c:v", alt, "-b:v", "6M" if borrador else "12M", "-pix_fmt", "yuv420p"]
    raise ErrorConfig("Tu FFmpeg no trae ningún codificador H.264 (libx264).", ARREGLO_FFMPEG)


def _args_audio(info: dict, copiar: bool) -> list[str]:
    if copiar and info.get("codec_audio") == "aac":
        return ["-c:a", "copy"]
    return ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


SALIDA_COMUN = ["-movflags", "+faststart", "-map_metadata", "-1"]


def _escribir(salida: pathlib.Path, args_sin_salida: list[str], cwd: pathlib.Path | None = None) -> None:
    """Escribe a un archivo parcial y lo coloca al final: nunca deja un MP4 a medias con el nombre bueno."""
    salida.parent.mkdir(parents=True, exist_ok=True)
    parcial = salida.with_name(f".{salida.stem}.parcial{salida.suffix}")
    try:
        _ffmpeg([*args_sin_salida, str(parcial)], cwd=cwd)
        os.replace(parcial, salida)
    finally:
        if parcial.exists():
            parcial.unlink()


# ─────────────────────────────── Marca y tipografía ───────────────────────────────

def _fusionar(base: dict, extra: dict) -> dict:
    out = dict(base)
    for k, v in (extra or {}).items():
        out[k] = _fusionar(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def cargar_marca(cliente: str | None = None, ruta: str | pathlib.Path | None = None) -> tuple[dict, pathlib.Path | None, list[str]]:
    """Marca del cliente (o de un marca.json concreto) fusionada con la neutra. Devuelve (marca, carpeta, avisos)."""
    avisos: list[str] = []
    archivo: pathlib.Path | None = None
    if ruta:
        archivo = pathlib.Path(ruta).expanduser().resolve()
        if not archivo.is_file():
            raise ErrorUsuario(f"No existe el archivo de marca: {ruta}")
    elif cliente:
        try:
            carpeta = _comun.ruta_cliente(cliente)
        except _comun.FichaInvalida as e:
            raise ErrorUsuario(str(e)) from None
        archivo = carpeta / "marca" / "marca.json"
        if not archivo.is_file():
            avisos.append(f"{cliente} no tiene marca (clientes/{cliente}/marca/marca.json): uso la neutra.")
            archivo = None
    if archivo is None:
        return _fusionar(MARCA_NEUTRA, {}), None, avisos
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ErrorUsuario(f"{archivo.name} no es un JSON válido: {e}") from None
    if not isinstance(datos, dict):
        raise ErrorUsuario(f"{archivo.name} tiene que ser un objeto JSON.")
    return _fusionar(MARCA_NEUTRA, datos), archivo.parent, avisos


def _hex(color: str, campo: str) -> str:
    c = str(color or "").strip().lstrip("#")
    if re.fullmatch(r"[0-9A-Fa-f]{3}", c):
        c = "".join(x * 2 for x in c)
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", c):
        raise ErrorUsuario(f"Color no válido en la marca ({campo}): {color!r}. Usa #RRGGBB.")
    return "#" + c.upper()


def _luminancia(color: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def texto_con_contraste(fondo: str) -> str:
    """Blanco o casi negro, el que más contraste dé sobre `fondo` (criterio WCAG)."""
    lf = _luminancia(fondo)
    blanco = 1.05 / (lf + 0.05)
    negro = (lf + 0.05) / (_luminancia("#111111") + 0.05)
    return "#FFFFFF" if blanco >= negro else "#111111"


def color_ass(color: str, alfa: int = 0) -> str:
    """#RRGGBB → &HAABBGGRR (alfa 0 = opaco, 255 = transparente)."""
    return f"&H{alfa:02X}{color[5:7]}{color[3:5]}{color[1:3]}"


class Metricas:
    """Lo mínimo de un TTF/OTF/TTC para maquetar como libass: familia, peso y anchos de avance, sin dependencias."""

    def __init__(self, ruta: pathlib.Path):
        d = ruta.read_bytes()
        base = struct.unpack(">I", d[12:16])[0] if d[:4] == b"ttcf" else 0
        t = {}
        for i in range(struct.unpack(">H", d[base + 4:base + 6])[0]):
            rec = base + 12 + 16 * i
            t[d[rec:rec + 4]] = struct.unpack(">I", d[rec + 8:rec + 12])[0]
        self.d, self.t = d, t
        self.familia = self._familia()
        os2 = t.get(b"OS/2")
        self.peso = struct.unpack(">H", d[os2 + 4:os2 + 6])[0] if os2 else None
        upem = struct.unpack(">H", d[t[b"head"] + 18:t[b"head"] + 20])[0]
        # libass (como VSFilter) hace que el cuerpo ASS sea usWinAscent + usWinDescent
        alto = sum(struct.unpack(">HH", d[os2 + 74:os2 + 78])) if os2 else 0
        self.escala = 1 / (alto or upem)
        self.n_metricas = struct.unpack(">H", d[t[b"hhea"] + 34:t[b"hhea"] + 36])[0]
        self.cmap = self._cmap()
        self._cache: dict[str, int] = {}

    def _familia(self) -> str | None:
        d, t = self.d, self.t.get(b"name")
        if t is None:
            return None
        _, cuenta, inicio = struct.unpack(">HHH", d[t:t + 6])
        candidatas: dict[int, str] = {}
        for i in range(cuenta):
            pid, _eid, lid, nid, largo, off = struct.unpack(">HHHHHH", d[t + 6 + 12 * i:t + 18 + 12 * i])
            if nid != 1 or pid not in (0, 1, 3):
                continue
            crudo = d[t + inicio + off:t + inicio + off + largo]
            texto = crudo.decode("mac_roman", "ignore") if pid == 1 else crudo.decode("utf-16-be", "ignore")
            candidatas.setdefault(0 if (pid == 3 and lid == 0x409) else 1 if pid == 3 else 2, texto.strip())
        return candidatas[min(candidatas)] if candidatas else None

    def _cmap(self):
        d, c = self.d, self.t[b"cmap"]
        subtablas = {}
        for i in range(struct.unpack(">H", d[c + 2:c + 4])[0]):
            pid, eid, off = struct.unpack(">HHI", d[c + 4 + 8 * i:c + 12 + 8 * i])
            subtablas[(pid, eid)] = c + off
        for clave in ((3, 10), (0, 4), (3, 1), (0, 3), (0, 1), (0, 0)):
            if clave in subtablas:
                o = subtablas[clave]
                formato = struct.unpack(">H", d[o:o + 2])[0]
                if formato == 12:
                    n = struct.unpack(">I", d[o + 12:o + 16])[0]
                    grupos = [struct.unpack(">III", d[o + 16 + 12 * k:o + 28 + 12 * k]) for k in range(n)]
                    return lambda cp: next((g0 + cp - a for a, b, g0 in grupos if a <= cp <= b), 0)
                if formato == 4:
                    seg = struct.unpack(">H", d[o + 6:o + 8])[0] // 2
                    fin = struct.unpack(f">{seg}H", d[o + 14:o + 14 + 2 * seg])
                    ini = struct.unpack(f">{seg}H", d[o + 16 + 2 * seg:o + 16 + 4 * seg])
                    delta = struct.unpack(f">{seg}h", d[o + 16 + 4 * seg:o + 16 + 6 * seg])
                    pos_rango = o + 16 + 6 * seg
                    rango = struct.unpack(f">{seg}H", d[pos_rango:pos_rango + 2 * seg])

                    def glifo(cp: int) -> int:
                        if cp > 0xFFFF:
                            return 0
                        for k in range(seg):
                            if fin[k] >= cp:
                                if ini[k] > cp:
                                    return 0
                                if rango[k] == 0:
                                    return (cp + delta[k]) & 0xFFFF
                                dir_ = pos_rango + 2 * k + rango[k] + 2 * (cp - ini[k])
                                g = struct.unpack(">H", d[dir_:dir_ + 2])[0]
                                return (g + delta[k]) & 0xFFFF if g else 0
                        return 0
                    return glifo
        raise ValueError("cmap sin subtabla Unicode")

    def avance(self, caracter: str) -> int:
        if caracter not in self._cache:
            g = self.cmap(ord(caracter))
            h = self.t[b"hmtx"]
            k = min(g, self.n_metricas - 1)
            self._cache[caracter] = struct.unpack(">H", self.d[h + 4 * k:h + 4 * k + 2])[0]
        return self._cache[caracter]

    def ancho(self, texto: str, cuerpo: float) -> float:
        return sum(self.avance(c) for c in texto) * self.escala * cuerpo


@functools.lru_cache(maxsize=16)
def metricas(ruta: str) -> Metricas | None:
    try:
        return Metricas(pathlib.Path(ruta))
    except (OSError, struct.error, KeyError, ValueError, IndexError, StopIteration):
        return None


def elegir_fuente(marca: dict, carpeta: pathlib.Path | None, rol: str = "titulos") -> dict:
    """Tipografía para rótulos y subtítulos: la de la marca (archivo o familia instalada) o Montserrat ExtraBold."""
    avisos: list[str] = []
    t = (marca.get("tipografias") or {}).get(rol) or {}
    peso_pedido = int(t.get("peso") or 800)
    archivo = None
    if t.get("archivo"):
        candidato = (carpeta / t["archivo"]) if carpeta else pathlib.Path(t["archivo"])
        if candidato.is_file():
            archivo = candidato
        else:
            avisos.append(f"No encuentro la tipografía de la marca ({t['archivo']}): uso la de por defecto.")
    elif t.get("familia"):
        return {"archivo": None, "familia": t["familia"], "negrita": peso_pedido >= 600, "metricas": None,
                "avisos": [f"Uso la familia «{t['familia']}» instalada en el sistema; si no está, libass usará otra."]}
    if archivo is None:
        archivo = next((f for f in FUENTES_POR_DEFECTO if f.is_file()), None)
        if archivo is None:
            archivo = next((f for d in DIRS_FUENTES if d.is_dir() for f in sorted(d.glob("*.[ot]tf"))), None)
    if archivo is None:
        return {"archivo": None, "familia": "Sans", "negrita": True, "metricas": None,
                "avisos": avisos + ["No encuentro ninguna tipografía del producto: libass usará la del sistema."]}
    m = metricas(str(archivo))
    familia, peso = (m.familia, m.peso) if m else (None, None)
    if not familia:
        avisos.append(f"No puedo leer el nombre de {archivo.name}: libass puede sustituirla.")
        familia = archivo.stem
    return {"archivo": archivo, "familia": familia, "negrita": peso_pedido >= 600 and (peso or 400) < 600,
            "metricas": m, "avisos": avisos}


# ─────────────────────────────── Texto y ASS ───────────────────────────────

def _ancho_texto(texto: str, cuerpo: float, fuente: dict | None = None) -> float:
    """Ancho en píxeles tal como lo maqueta libass; sin métricas de la fuente, una estimación prudente."""
    m = (fuente or {}).get("metricas")
    if m is not None:
        return m.ancho(texto, cuerpo)
    total = 0.0
    for c in texto:
        if c == " ":
            total += 0.24
        elif c in "mwMW@%":
            total += 0.78
        elif c in "iljtfrI.,;:!'|¡":
            total += 0.28
        elif c.isupper():
            total += 0.60
        else:
            total += 0.50
    return total * cuerpo


def _partir(texto: str, ancho_max: float, cuerpo: float, fuente: dict | None = None) -> list[str]:
    lineas: list[str] = []
    actual = ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if actual and _ancho_texto(prueba, cuerpo, fuente) > ancho_max:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas


def _equilibrar(lineas: list[str], ancho_max: float, cuerpo: float, fuente: dict | None = None) -> list[str]:
    """Reparte dos líneas para que tengan un ancho parecido (se leen mejor que una larga y otra corta)."""
    if len(lineas) != 2:
        return lineas
    palabras = " ".join(lineas).split()
    mejor, peor_ancho = lineas, max(_ancho_texto(x, cuerpo, fuente) for x in lineas)
    for k in range(1, len(palabras)):
        a, b = " ".join(palabras[:k]), " ".join(palabras[k:])
        m = max(_ancho_texto(a, cuerpo, fuente), _ancho_texto(b, cuerpo, fuente))
        if m <= ancho_max and m < peor_ancho:
            mejor, peor_ancho = [a, b], m
    return mejor


SALTO = "\\N"  # salto de línea de ASS


def _texto_ass(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.replace("\\", "/").replace("{", "(").replace("}", ")")).strip()


def _t_ass(segundos: float) -> str:
    cs = int(round(max(0.0, segundos) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _cabecera_ass(ancho: int, alto: int, estilos: list[str]) -> str:
    return "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {ancho}", f"PlayResY: {alto}", "WrapStyle: 0",
        "ScaledBorderAndShadow: yes", "YCbCr Matrix: TV.709", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        *estilos, "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text", ""])


def _zonas(formato: str | None) -> tuple[float, float, float]:
    return ZONAS.get(formato or "", ZONA_GENERICA)


def leer_srt(texto: str) -> tuple[list[tuple[float, float, str]], list[str]]:
    """Parsea un SRT. Devuelve (subtítulos ordenados, avisos). Lanza ErrorUsuario si está mal formado."""
    def segundos(t: str, n: int) -> float:
        m = re.fullmatch(r"\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*", t)
        if not m:
            raise ErrorUsuario(f"Subtítulo {n} del SRT: tiempo no válido {t.strip()!r} (formato HH:MM:SS,mmm).")
        h, mi, s, ms = m.groups()
        return int(h) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000

    texto = texto.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not texto:
        raise ErrorUsuario("El SRT está vacío.")
    cues: list[tuple[float, float, str]] = []
    avisos: list[str] = []
    for n, bloque in enumerate(re.split(r"\n\s*\n", texto), start=1):
        lineas = bloque.split("\n")
        i = next((k for k, linea in enumerate(lineas[:2]) if "-->" in linea), None)
        if i is None:
            raise ErrorUsuario(f"Subtítulo {n} del SRT sin línea de tiempos «HH:MM:SS,mmm --> HH:MM:SS,mmm».")
        ini, _, fin = lineas[i].partition("-->")
        fin = re.split(r"\s{2,}|\s[A-Z]\d?:", fin.strip())[0]  # quita posiciones tipo «X1:…»
        t0, t1 = segundos(ini, n), segundos(fin, n)
        if t1 <= t0:
            raise ErrorUsuario(f"Subtítulo {n} del SRT: el final ({fin.strip()}) no va después del inicio.")
        cuerpo = " ".join(re.sub(r"<[^>]+>|\{\\[^}]*\}", "", x).strip() for x in lineas[i + 1:] if x.strip())
        if not cuerpo:
            avisos.append(f"Subtítulo {n} vacío: lo salto.")
            continue
        if t1 - t0 < 0.5:
            avisos.append(f"Subtítulo {n} dura {_n(t1 - t0)} s: con menos de 0,5 s casi no se lee.")
        cues.append((t0, t1, cuerpo))
    if not cues:
        raise ErrorUsuario("El SRT no tiene ningún subtítulo con texto.")
    cues.sort(key=lambda c: c[0])
    for (a0, a1, _), (b0, _b1, _) in zip(cues, cues[1:]):
        if b0 < a1 - 0.01:
            avisos.append(f"Hay subtítulos solapados ({_t_ass(b0)}): se apilarán en pantalla.")
            break
    return cues, avisos


def construir_ass_subtitulos(cues: list[tuple[float, float, str]], ancho: int, alto: int, formato: str | None,
                             marca: dict, fuente: dict, mayusculas: bool = False) -> tuple[str, list[str]]:
    """ASS con el estilo de la marca: máximo 2 líneas por pantalla, en el tercio central en 9:16."""
    avisos: list[str] = []
    arriba, abajo, lados = _zonas(formato)
    s = marca.get("subtitulos") or {}
    cuerpo = round(ancho * 0.056)
    margen_lat = round(ancho * lados) + round(ancho * 0.03)
    ancho_util = ancho - 2 * margen_lat
    # 9:16: el borde inferior del texto al 62,5 % del alto (tercio central, por encima del 35 % inferior)
    margen_v = alto - round(alto * 0.625) if formato == "9x16" else round(alto * abajo) + round(alto * 0.08)
    estilo = (f"Style: Subtitulo,{fuente['familia']},{cuerpo},{color_ass(_hex(s.get('color'), 'subtitulos.color'))},"
              f"&H000000FF,{color_ass(_hex(s.get('contorno'), 'subtitulos.contorno'))},&H64000000,"
              f"{-1 if fuente['negrita'] else 0},0,0,0,100,100,0,0,1,{max(2, round(cuerpo * 0.09))},0,2,"
              f"{margen_lat},{margen_lat},{margen_v},1")
    eventos = []
    partidos = 0
    for t0, t1, texto in cues:
        texto = _texto_ass(texto.upper() if mayusculas else texto)
        lineas = _partir(texto, ancho_util, cuerpo, fuente)
        grupos = [lineas[k:k + 2] for k in range(0, len(lineas), 2)]
        if len(grupos) > 1:
            partidos += 1
        total = sum(len(" ".join(g)) for g in grupos) or 1
        t = t0
        for g in grupos:
            dur = (t1 - t0) * len(" ".join(g)) / total
            g = _equilibrar(g, ancho_util, cuerpo, fuente)
            eventos.append(f"Dialogue: 0,{_t_ass(t)},{_t_ass(t + dur)},Subtitulo,,0,0,0,,{SALTO.join(g)}")
            t += dur
    if partidos:
        avisos.append(f"{partidos} subtítulo(s) no cabían en 2 líneas: los he partido en pantallas seguidas.")
    return _cabecera_ass(ancho, alto, [estilo]) + "\n".join(eventos) + "\n", avisos


def construir_ass_hook(texto: str, duracion: float, ancho: int, alto: int, formato: str | None, posicion: str,
                       marca: dict, fuente: dict, mayusculas: bool = False) -> tuple[str, list[str]]:
    """ASS del rótulo del hook: caja del color primario, texto con contraste, dentro de la zona segura."""
    avisos: list[str] = []
    arriba, _abajo, lados = _zonas(formato)
    colores = marca.get("colores") or {}
    caja = _hex(colores.get("primario"), "colores.primario")
    letra = _hex(colores["texto_sobre_primario"], "colores.texto_sobre_primario") if colores.get(
        "texto_sobre_primario") else texto_con_contraste(caja)
    texto = _texto_ass(texto.upper() if mayusculas else texto)
    base, minimo = round(ancho * 0.074), round(ancho * 0.05)
    elegido = None
    for cuerpo in range(base, minimo - 1, -2):
        relleno = round(cuerpo * 0.28)
        ancho_util = ancho - 2 * (round(ancho * lados) + relleno + round(ancho * 0.02))
        lineas = _partir(texto, ancho_util, cuerpo, fuente)
        if len(lineas) <= 3 and all(_ancho_texto(x, cuerpo, fuente) <= ancho_util for x in lineas):
            elegido = (cuerpo, relleno, _equilibrar(lineas, ancho_util, cuerpo, fuente))
            break
    if elegido is None:
        cuerpo = minimo
        relleno = round(cuerpo * 0.28)
        ancho_util = ancho - 2 * (round(ancho * lados) + relleno + round(ancho * 0.02))
        elegido = (cuerpo, relleno, _partir(texto, ancho_util, cuerpo, fuente))
        avisos.append("El hook no cabe en 3 líneas ni con el cuerpo mínimo: acórtalo.")
    cuerpo, relleno, lineas = elegido
    palabras = len(texto.split())
    if palabras > 9:
        avisos.append(f"El hook tiene {palabras} palabras: con más de 9 cuesta leerlo en 2 s [HYPOTHESIS].")
    margen_lat = round(ancho * lados) + relleno + round(ancho * 0.02)
    alineacion = 8 if posicion == "arriba" else 5
    margen_v = round(alto * arriba) + relleno + round(alto * 0.02)
    # caja opaca: libass dibuja una caja por línea y, con transparencia, los solapes entre líneas se ven como bandas
    estilo = (f"Style: Hook,{fuente['familia']},{cuerpo},{color_ass(letra)},&H000000FF,{color_ass(caja)},"
              f"&H00000000,{-1 if fuente['negrita'] else 0},0,0,0,100,100,0,0,3,{relleno},0,{alineacion},"
              f"{margen_lat},{margen_lat},{margen_v},1")
    efecto = "{\\fad(0,150)\\fscx94\\fscy94\\t(0,140,\\fscx100\\fscy100)}"
    evento = f"Dialogue: 0,{_t_ass(0)},{_t_ass(duracion)},Hook,,0,0,0,,{efecto}{SALTO.join(lineas)}"
    return _cabecera_ass(ancho, alto, [estilo]) + evento + "\n", avisos


def _quemar_ass(entrada: pathlib.Path, salida: pathlib.Path, ass: str, fuente: dict, info: dict, a) -> None:
    caps = _capacidades(_bin("ffmpeg"))
    _requiere_libass(caps)
    with tempfile.TemporaryDirectory(prefix="editar_video_") as tmp:
        t = pathlib.Path(tmp)
        (t / "rotulos.ass").write_text(ass, encoding="utf-8")
        (t / "fuentes").mkdir()
        if fuente.get("archivo"):
            shutil.copy2(fuente["archivo"], t / "fuentes" / pathlib.Path(fuente["archivo"]).name)
        # rutas relativas al directorio de trabajo: evita el escapado de rutas de Windows dentro del filtro
        vf = f"fps={a.fps:g},setsar=1,ass=filename=rotulos.ass:fontsdir=fuentes,format=yuv420p"
        _escribir(salida, ["-i", str(entrada), "-map", "0:v:0", "-map", "0:a:0?", "-vf", vf,
                           *_args_video(caps, a.borrador), *_args_audio(info, copiar=True), *SALIDA_COMUN], cwd=t)


# ─────────────────────────────── Subcomandos ───────────────────────────────

def _ruta_salida(a, sufijo: str) -> pathlib.Path:
    entrada = pathlib.Path(a.entrada).expanduser().resolve()
    salida = pathlib.Path(a.salida).expanduser().resolve() if a.salida else entrada.with_name(f"{entrada.stem}_{sufijo}.mp4")
    if salida.suffix.lower() not in (".mp4", ".mov", ".m4v"):
        raise ErrorUsuario(f"La salida tiene que ser .mp4 (o .mov): {salida.name}")
    if salida == entrada:
        raise ErrorUsuario("La salida no puede ser el mismo archivo que la entrada.")
    if salida.exists() and not a.sobrescribir:
        raise ErrorUsuario(f"Ya existe {salida}.", "Elige otra --salida o añade --sobrescribir.")
    return salida


def _resultado(subcomando: str, salida: pathlib.Path, avisos: list[str], **extra) -> dict:
    i = sondear(salida)
    return {"ok": True, "subcomando": subcomando, "salida": str(salida), "duracion": round(i["duracion"], 3),
            "ancho": i["ancho"], "alto": i["alto"], "formato": detectar_formato(i["ancho"], i["alto"]), **extra,
            "avisos": avisos}


def cmd_info(a) -> dict:
    i = sondear(pathlib.Path(a.entrada).expanduser().resolve())
    formato = detectar_formato(i["ancho"], i["alto"])
    avisos = []
    if not formato:
        avisos.append("No es 9:16, 4:5 ni 1:1 dentro de la tolerancia del 1 % de Instagram: usa `reformatear`.")
    if i["ancho"] and min(i["ancho"], i["alto"]) < 1080:
        avisos.append(f"Resolución baja ({i['ancho']}×{i['alto']}): Meta recomienda 1080 px de ancho o más.")
    if not i["audio"]:
        avisos.append("Sin pista de audio: más del 75 % de los Reels se ven con sonido [OFFICIAL META].")
    if formato == "9x16" and i["duracion"] > 15.5:
        avisos.append("Más de 15 s: en Stories se parte en tarjetas; deja el mensaje clave en los primeros 15 s.")
    return {"ok": True, "subcomando": "info", "entrada": str(a.entrada), **i, "formato": formato, "avisos": avisos}


def _silencios(entrada: pathlib.Path, desde: float, dur: float, umbral: float, minimo: float) -> list[tuple[float, float]]:
    r = _ffmpeg(["-ss", f"{desde:.3f}", "-t", f"{dur:.3f}", "-i", str(entrada), "-map", "0:a:0",
                 "-af", f"silencedetect=noise={umbral}dB:d={minimo}", "-f", "null", "-"])
    res, ini = [], None
    for linea in r.stderr.splitlines():
        m = re.search(r"silence_start:\s*(-?[\d.]+)", linea)
        if m:
            ini = max(0.0, float(m.group(1)))
            continue
        m = re.search(r"silence_end:\s*([\d.]+)", linea)
        if m and ini is not None:
            res.append((ini, min(dur, float(m.group(1)))))
            ini = None
    if ini is not None:
        res.append((ini, dur))
    return res


def tramos_con_voz(silencios: list[tuple[float, float]], dur: float, margen: float, fps: float) -> list[tuple[float, float]]:
    """Complemento de los silencios, con `margen` de aire a cada lado, fusionado y ajustado a fotogramas."""
    voz, cur = [], 0.0
    for s, e in sorted(silencios):
        if s > cur:
            voz.append((cur, s))
        cur = max(cur, e)
    if cur < dur:
        voz.append((cur, dur))
    tramos: list[tuple[float, float]] = []
    for a0, b0 in voz:
        if b0 - a0 <= 0.02:
            continue
        a1, b1 = max(0.0, a0 - margen), min(dur, b0 + margen)
        if tramos and a1 <= tramos[-1][1]:
            tramos[-1] = (tramos[-1][0], max(tramos[-1][1], b1))
        else:
            tramos.append((a1, b1))
    q = [(round(a0 * fps) / fps, round(b0 * fps) / fps) for a0, b0 in tramos]
    return [(a0, b0) for a0, b0 in q if b0 - a0 >= 2 / fps]


def cmd_cortar(a) -> dict:
    entrada = pathlib.Path(a.entrada).expanduser().resolve()
    info = sondear(entrada)
    salida = _ruta_salida(a, "corte")
    avisos: list[str] = []
    desde = a.desde or 0.0
    hasta = info["duracion"] if a.hasta is None else a.hasta
    if hasta > info["duracion"] + 0.05:
        avisos.append(f"--hasta {_n(hasta)} pasa del final ({_n(info['duracion'])} s): corto hasta el final.")
        hasta = info["duracion"]
    if desde < 0 or hasta <= desde:
        raise ErrorUsuario(f"Tramo no válido: --desde {_n(desde)} --hasta {_n(hasta)} (el vídeo dura {_n(info['duracion'])} s).")
    dur = hasta - desde
    caps = _capacidades(_bin("ffmpeg"))
    entrada_args = ["-ss", f"{desde:.3f}", "-t", f"{dur:.3f}", "-i", str(entrada)]
    if not a.quitar_silencios:
        _escribir(salida, [*entrada_args, "-map", "0:v:0", "-map", "0:a:0?",
                           "-vf", f"fps={a.fps:g},setsar=1,format=yuv420p", *_args_video(caps, a.borrador),
                           *_args_audio(info, copiar=False), *SALIDA_COMUN])
        return _resultado("cortar", salida, avisos)
    if not info["audio"]:
        raise ErrorUsuario("--quitar-silencios necesita audio y este vídeo no tiene.")
    silencios = _silencios(entrada, desde, dur, a.umbral_db, a.min_silencio)
    tramos = tramos_con_voz(silencios, dur, a.margen, a.fps)
    if not tramos:
        raise ErrorUsuario(f"Con {_n(a.umbral_db)} dB todo es silencio.",
                           "Baja el umbral (más negativo, p. ej. --umbral-db -45) o revisa que el vídeo tenga voz.")
    quitado = dur - sum(b - x for x, b in tramos)
    n = len(tramos)
    partes = [f"[0:v]setpts=PTS-STARTPTS,fps={a.fps:g},setsar=1,split={n}" + "".join(f"[vi{k}]" for k in range(n)),
              "[0:a]asetpts=PTS-STARTPTS,aresample=48000,asplit=" + str(n) + "".join(f"[ai{k}]" for k in range(n))]
    for k, (x, b) in enumerate(tramos):
        d = b - x
        f = min(0.012, d / 4)
        partes.append(f"[vi{k}]trim=start={x:.4f}:end={b:.4f},setpts=PTS-STARTPTS[v{k}]")
        partes.append(f"[ai{k}]atrim=start={x:.4f}:end={b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d={f:.3f},"
                      f"afade=t=out:st={d - f:.4f}:d={f:.3f}[a{k}]")
    partes.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    partes.append("[vc]format=yuv420p[v]")
    grafo = ";".join(partes)
    with tempfile.TemporaryDirectory(prefix="editar_video_") as tmp:
        if len(grafo) > 6000:  # límite de línea de órdenes de Windows
            (pathlib.Path(tmp) / "grafo.txt").write_text(grafo, encoding="utf-8")
            opcion = ["-/filter_complex", "grafo.txt"] if caps["version"] >= (7, 1) else ["-filter_complex_script", "grafo.txt"]
        else:
            opcion = ["-filter_complex", grafo]
        _escribir(salida, [*entrada_args, *opcion, "-map", "[v]", "-map", "[ac]", *_args_video(caps, a.borrador),
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", *SALIDA_COMUN],
                  cwd=pathlib.Path(tmp))
    if quitado < 0.05:
        avisos.append("No he encontrado silencios con esos parámetros: el corte es el tramo pedido.")
    return _resultado("cortar", salida, avisos, tramos=len(tramos), silencio_quitado=round(quitado, 2))


def cmd_reformatear(a) -> dict:
    entrada = pathlib.Path(a.entrada).expanduser().resolve()
    info = sondear(entrada)
    salida = _ruta_salida(a, a.formato)
    if not (0 <= a.foco <= 1 and 0 <= a.foco_vertical <= 1):
        raise ErrorUsuario("--foco y --foco-vertical van de 0 (izquierda/arriba) a 1 (derecha/abajo).")
    marca, _carpeta, avisos = cargar_marca(a.cliente, a.marca)
    W, H = FORMATOS[a.formato]
    iw, ih = info["ancho"], info["alto"]
    caps = _capacidades(_bin("ffmpeg"))
    cola = f"fps={a.fps:g},setsar=1,format=yuv420p"
    if a.modo == "recorte":
        escala = max(W / iw, H / ih)
        visible = min((W / H) / (iw / ih), (iw / ih) / (W / H))
        if visible < 0.6:
            lado = "a los lados" if iw / ih > W / H else "arriba y abajo"
            avisos.append(f"Recortas el {round((1 - visible) * 100)} % de la imagen ({lado}): comprueba que el sujeto y "
                          "los textos quedan dentro (ajusta --foco / --foco-vertical) o usa --modo desenfoque.")
        filtro = ["-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                         f"crop={W}:{H}:(iw-{W})*{a.foco:g}:(ih-{H})*{a.foco_vertical:g},{cola}"]
    elif a.modo == "relleno":
        escala = min(W / iw, H / ih)
        fondo = _hex(marca["colores"].get("fondo"), "colores.fondo")
        filtro = ["-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,"
                         f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x{fondo[1:]},{cola}"]
    else:
        escala = min(W / iw, H / ih)
        w4, h4 = W // 4, H // 4
        grafo = (f"[0:v]split=2[f][b];[b]scale={w4}:{h4}:force_original_aspect_ratio=increase,crop={w4}:{h4},"
                 f"gblur=sigma=14,scale={W}:{H},eq=brightness=-0.07[fondo];"
                 f"[f]scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos[primer];"
                 f"[fondo][primer]overlay=(W-w)/2:(H-h)/2,{cola}[v]")
        filtro = ["-filter_complex", grafo]
    if escala > 1.05:
        avisos.append(f"La fuente ({iw}×{ih}) es más pequeña que el destino: se amplía ×{_n(escala)} y puede perder nitidez.")
    mapa = ["-map", "[v]"] if a.modo == "desenfoque" else ["-map", "0:v:0"]
    _escribir(salida, ["-i", str(entrada), *filtro, *mapa, "-map", "0:a:0?", *_args_video(caps, a.borrador),
                       *_args_audio(info, copiar=True), *SALIDA_COMUN])
    return _resultado("reformatear", salida, avisos, modo=a.modo)


def _formato_para(a, info: dict) -> str | None:
    detectado = detectar_formato(info["ancho"], info["alto"])
    if getattr(a, "formato", None) and a.formato != detectado:
        raise ErrorUsuario(f"El vídeo es {info['ancho']}×{info['alto']}, no {a.formato}.",
                           f"Reformatea primero: editar_video.py reformatear <vídeo> --formato {a.formato}")
    return detectado


def cmd_subtitular(a) -> dict:
    entrada = pathlib.Path(a.entrada).expanduser().resolve()
    info = sondear(entrada)
    salida = _ruta_salida(a, "subtitulos")
    srt = pathlib.Path(a.srt).expanduser()
    if not srt.is_file():
        raise ErrorUsuario(f"No existe el SRT: {a.srt}")
    cues, avisos = leer_srt(srt.read_text(encoding="utf-8", errors="replace"))
    formato = _formato_para(a, info)
    marca, carpeta, av_marca = cargar_marca(a.cliente, a.marca)
    fuente = elegir_fuente(marca, carpeta)
    mayus = a.mayusculas or bool((marca.get("subtitulos") or {}).get("mayusculas"))
    ass, av_ass = construir_ass_subtitulos(cues, info["ancho"], info["alto"], formato, marca, fuente, mayus)
    fuera = sum(1 for t0, _t1, _x in cues if t0 >= info["duracion"])
    avisos = av_marca + fuente["avisos"] + avisos + av_ass
    if fuera:
        avisos.append(f"{fuera} subtítulo(s) empiezan después del final del vídeo: no se verán.")
    if not formato:
        avisos.append("El vídeo no es 9:16, 4:5 ni 1:1: uso márgenes genéricos del 5 %.")
    _quemar_ass(entrada, salida, ass, fuente, info, a)
    return _resultado("subtitular", salida, avisos, subtitulos=len(cues), fuente=fuente["familia"])


def cmd_texto_hook(a) -> dict:
    entrada = pathlib.Path(a.entrada).expanduser().resolve()
    info = sondear(entrada)
    salida = _ruta_salida(a, "hook")
    if not a.texto.strip():
        raise ErrorUsuario("--texto está vacío.")
    if a.duracion <= 0:
        raise ErrorUsuario("--duracion tiene que ser mayor que 0.")
    avisos: list[str] = []
    duracion = a.duracion
    if duracion > 3:
        avisos.append(f"El hook dura {_n(duracion)} s: el perfil de anuncio lo quiere en los 2 primeros segundos.")
    if duracion > info["duracion"]:
        avisos.append(f"El vídeo dura {_n(info['duracion'])} s: el rótulo se queda hasta el final.")
        duracion = info["duracion"]
    formato = _formato_para(a, info)
    marca, carpeta, av_marca = cargar_marca(a.cliente, a.marca)
    fuente = elegir_fuente(marca, carpeta)
    ass, av_ass = construir_ass_hook(a.texto, duracion, info["ancho"], info["alto"], formato, a.posicion, marca, fuente,
                                     a.mayusculas)
    if not formato:
        avisos.append("El vídeo no es 9:16, 4:5 ni 1:1: uso márgenes genéricos del 5 %.")
    _quemar_ass(entrada, salida, ass, fuente, info, a)
    return _resultado("texto-hook", salida, av_marca + fuente["avisos"] + avisos + av_ass, fuente=fuente["familia"])


# ─────────────────────────────── CLI ───────────────────────────────

class _Parser(argparse.ArgumentParser):
    def error(self, message):  # argparse sale con 2; el contrato reserva el 2 para configuración
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(1)


def _parser() -> _Parser:
    p = _Parser(prog="editar_video.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="subcomando", required=True, parser_class=_Parser)
    base = _Parser(add_help=False)
    base.add_argument("entrada", help="vídeo de entrada")
    base.add_argument("--json", action="store_true", help="salida en JSON")
    escribe = _Parser(add_help=False)
    escribe.add_argument("--salida", help="MP4 de salida (por defecto, junto a la entrada con un sufijo)")
    escribe.add_argument("--sobrescribir", action="store_true", help="reemplaza la salida si ya existe")
    escribe.add_argument("--fps", type=float, default=30.0, help="fotogramas por segundo de la salida (30)")
    escribe.add_argument("--borrador", action="store_true", help="codificación rápida y algo peor, para revisar")
    marca = _Parser(add_help=False)
    marca.add_argument("--cliente", help="slug: usa clientes/<slug>/marca/marca.json")
    marca.add_argument("--marca", help="ruta a un marca.json (prevalece sobre --cliente)")

    sub.add_parser("info", parents=[base], help="duración, resolución, audio y formato")
    c = sub.add_parser("cortar", parents=[base, escribe], help="recorte por tiempos y, opcional, sin silencios")
    c.add_argument("--desde", type=float, help="segundo inicial (0)")
    c.add_argument("--hasta", type=float, help="segundo final (el final del vídeo)")
    c.add_argument("--quitar-silencios", action="store_true", help="quita las pausas (cortes de salto)")
    c.add_argument("--umbral-db", type=float, default=-35.0, help="por debajo de este nivel es silencio (-35)")
    c.add_argument("--min-silencio", type=float, default=0.35, help="pausa mínima que se quita, en s (0,35)")
    c.add_argument("--margen", type=float, default=0.10, help="aire que se deja antes y después de la voz, en s (0,1)")
    r = sub.add_parser("reformatear", parents=[base, escribe, marca], help="9x16, 4x5 o 1x1 con la resolución exacta")
    r.add_argument("--formato", required=True, choices=list(FORMATOS))
    r.add_argument("--modo", choices=["recorte", "relleno", "desenfoque"], default="recorte")
    r.add_argument("--foco", type=float, default=0.5, help="recorte horizontal: 0 izquierda · 0,5 centro · 1 derecha")
    r.add_argument("--foco-vertical", type=float, default=0.5, help="recorte vertical: 0 arriba · 0,5 centro · 1 abajo")
    s = sub.add_parser("subtitular", parents=[base, escribe, marca], help="quema un SRT con el estilo de la marca")
    s.add_argument("--srt", required=True)
    s.add_argument("--formato", choices=list(FORMATOS), help="comprueba que el vídeo tiene este formato")
    s.add_argument("--mayusculas", action="store_true")
    h = sub.add_parser("texto-hook", parents=[base, escribe, marca], help="rótulo del hook en los primeros segundos")
    h.add_argument("--texto", required=True)
    h.add_argument("--duracion", type=float, default=2.0, help="segundos en pantalla (2)")
    h.add_argument("--posicion", choices=["arriba", "centro"], default="arriba")
    h.add_argument("--formato", choices=list(FORMATOS), help="comprueba que el vídeo tiene este formato")
    h.add_argument("--mayusculas", action="store_true")
    return p


ORDENES = {"info": cmd_info, "cortar": cmd_cortar, "reformatear": cmd_reformatear, "subtitular": cmd_subtitular,
           "texto-hook": cmd_texto_hook}


def _imprimir(res: dict) -> None:
    if res["subcomando"] == "info":
        print(f"{res['entrada']}: {res['ancho']}×{res['alto']} · {_n(res['duracion'])} s · {_n(res['fps'])} fps · "
              f"audio {'sí' if res['audio'] else 'no'} · formato {res['formato'] or 'ninguno de Meta'}")
    else:
        print(f"Listo: {res['salida']} ({res['ancho']}×{res['alto']}, {_n(res['duracion'])} s)")
    for aviso in res["avisos"]:
        print(f"Aviso: {aviso}")


def main(argv: list[str] | None = None) -> int:
    try:
        a = _parser().parse_args(argv)
    except SystemExit as e:
        return int(e.code or 0)
    try:
        if getattr(a, "fps", 30) <= 0 or getattr(a, "fps", 30) > 120:
            raise ErrorUsuario("--fps tiene que estar entre 1 y 120.")
        res = ORDENES[a.subcomando](a)
    except ErrorUsuario as e:
        if a.json:
            print(json.dumps({"ok": False, "error": str(e), "arreglo": e.arreglo}, ensure_ascii=False))
        else:
            print(f"Error: {e}", file=sys.stderr)
            if e.arreglo:
                print(f"Arreglo: {e.arreglo}", file=sys.stderr)
        return e.codigo
    if a.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        _imprimir(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
