"""Marca del cliente para el montaje: `clientes/<cliente>/marca/marca.json` + archivos.

Esquema (todos los campos opcionales; lo que falta sale de `recursos/marca_defecto.json`, una marca neutra; las rutas
son relativas a la carpeta `marca/`):

    {"nombre": "Acme Automations",
     "colores": {"primario": "#1F6FEB", "secundario": "#0B1F3A", "acento": "#FFB020", "fondo": "#FFFFFF",
                 "texto": "#0B1F3A", "texto_sobre_primario": "#FFFFFF"},
     "tipografias": {"titulos": {"familia": "Montserrat", "archivo": "fuentes/Montserrat-ExtraBold.ttf", "peso": 800},
                     "texto": {"familia": "Montserrat", "archivo": "fuentes/Montserrat-Medium.ttf", "peso": 500}},
     "logo": {"principal": "logo.svg", "claro": "logo-claro.svg"},
     "subtitulos": {"color": "#FFFFFF", "resaltado": "#FFB020", "contorno": "#000000", "mayusculas": false},
     "cta_por_defecto": "Reserva tu llamada",
     "etiqueta_ia": "Contenido generado con IA"}

El mismo esquema lo usan `herramientas/render.py` y `herramientas/editar_video.py`.
"""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .paths import FUENTES, RECURSOS, marca_dir

DEFECTO = RECURSOS / "marca_defecto.json"
_HEX = re.compile(r"^#?([0-9a-fA-F]{6})([0-9a-fA-F]{2})?$")
_RASTER = {".png", ".jpg", ".jpeg", ".webp"}


class MarcaInvalida(ValueError):
    """`marca.json` existe pero no se puede usar; el mensaje dice qué arreglar."""


def _fusion(base: dict, extra: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _fusion(out[k], v)
        elif v not in (None, ""):
            out[k] = v
    return out


def metricas_fuente(ruta: str | Path) -> dict:
    """Lo que libass necesita de una fuente TTF/OTF/TTC (primera cara), leído de sus tablas `name`, `head` y `OS/2`:
    `familia` (name ID 1, la que libass compara con el Fontname del estilo), `peso` (usWeightClass), `upm` y
    `alto_libass` (winAscent + winDescent en unidades: libass escala la fuente para que ESE alto mida el cuerpo pedido)
    y `variable` (tiene tabla `fvar`: libass pinta su instancia por defecto, que suele ser la más fina).
    Lanza `MarcaInvalida` si el archivo no es una fuente TTF/OTF utilizable.
    """
    import struct

    nombre = Path(ruta).name
    datos = Path(ruta).read_bytes()
    if datos[:4] in (b"wOFF", b"wOF2"):
        raise MarcaInvalida(f"{nombre} es WOFF/WOFF2 (fuente web): para vídeo usa el TTF u OTF de esa tipografía")
    if datos[:4] not in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"ttcf"):
        raise MarcaInvalida(f"{nombre} no es una fuente TTF/OTF")
    try:
        return _metricas_sfnt(datos, struct, Path(ruta).stem)
    except (struct.error, KeyError, IndexError):
        raise MarcaInvalida(f"{nombre} está dañada o no es una fuente TTF/OTF") from None


def _metricas_sfnt(datos: bytes, struct, nombre_por_defecto: str) -> dict:
    base = struct.unpack(">I", datos[12:16])[0] if datos[:4] == b"ttcf" else 0
    n = struct.unpack(">H", datos[base + 4:base + 6])[0]
    tablas = {}
    for i in range(n):
        tag, _, off, ln = struct.unpack(">4sIII", datos[base + 12 + 16 * i:base + 28 + 16 * i])
        tablas[tag.decode("latin-1")] = (off, ln)
    upm = struct.unpack(">H", datos[tablas["head"][0] + 18:tablas["head"][0] + 20])[0] if "head" in tablas else 1000
    peso, alto = 400, 0
    if "OS/2" in tablas:
        o = tablas["OS/2"][0]
        peso = struct.unpack(">H", datos[o + 4:o + 6])[0]
        wa, wd = struct.unpack(">HH", datos[o + 74:o + 78])
        alto = wa + wd
    if not alto and "hhea" in tablas:
        o = tablas["hhea"][0]
        asc, desc = struct.unpack(">hh", datos[o + 4:o + 8])
        alto = asc - desc
    familia = None
    if "name" in tablas:
        o = tablas["name"][0]
        _, cuenta, strs = struct.unpack(">HHH", datos[o:o + 6])
        candidatos = []
        for i in range(cuenta):
            plat, enc, idioma, nid, ln, off = struct.unpack(">HHHHHH", datos[o + 6 + 12 * i:o + 18 + 12 * i])
            if nid != 1:
                continue
            crudo = datos[o + strs + off:o + strs + off + ln]
            try:
                texto = crudo.decode("utf-16-be") if plat in (0, 3) else crudo.decode("mac_roman")
            except UnicodeDecodeError:
                continue
            candidatos.append((0 if (plat, idioma) == (3, 0x409) else 1 if plat == 3 else 2, texto))
        familia = min(candidatos)[1] if candidatos else None
    return {"familia": familia or nombre_por_defecto, "peso": peso, "upm": upm, "alto_libass": alto or upm,
            "variable": "fvar" in tablas}


def hex_valido(c: str) -> str:
    m = _HEX.match(str(c or "").strip())
    if not m:
        raise MarcaInvalida(f"color no válido: {c!r} (usa #RRGGBB)")
    return "#" + m.group(1).upper()


def ass_color(c: str, alfa: int = 0) -> str:
    """#RRGGBB → &HAABBGGRR (formato de color de ASS/libass; alfa 0 = opaco, 255 = transparente)."""
    h = hex_valido(c)[1:]
    return f"&H{alfa:02X}{h[4:6]}{h[2:4]}{h[0:2]}"


def luminancia(c: str) -> float:
    h = hex_valido(c)[1:]
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@dataclass
class Marca:
    datos: dict
    carpeta: Path | None = None
    avisos: list[str] = field(default_factory=list)

    @property
    def nombre(self) -> str:
        return str(self.datos.get("nombre") or "")

    def color(self, clave: str) -> str:
        return hex_valido(self.datos["colores"][clave])

    def sub(self, clave: str):
        return self.datos.get("subtitulos", {}).get(clave)

    def _archivo(self, rel: str | None) -> Path | None:
        if not rel:
            return None
        p = Path(rel)
        if not p.is_absolute():
            p = (self.carpeta / p) if self.carpeta and (self.carpeta / p).exists() else FUENTES / p.name
        return p if p.exists() else None

    def fuente(self, rol: str = "titulos") -> Path:
        """Archivo TTF/OTF de la tipografía del rol (`titulos` | `texto`); si falta, Montserrat (OFL) del producto."""
        t = self.datos.get("tipografias", {}).get(rol, {})
        defecto = FUENTES / ("Montserrat-ExtraBold.ttf" if rol == "titulos" else "Montserrat-SemiBold.ttf")
        p = self._archivo(t.get("archivo"))
        if p is None:
            if t.get("archivo"):
                self._avisar(f"no encuentro la tipografía {t.get('archivo')!r}: uso Montserrat")
            return defecto
        try:
            m = metricas_fuente(p)
        except MarcaInvalida as e:
            self._avisar(f"{e}: uso Montserrat")
            return defecto
        if m["variable"]:
            self._avisar(f"{p.name} es una fuente variable: libass pinta su instancia por defecto («{m['familia']}»); "
                         "para vídeo usa el archivo estático del peso que quieras (p. ej. …-ExtraBold.ttf)")
        return p

    def _avisar(self, texto: str) -> None:
        if texto not in self.avisos:
            self.avisos.append(texto)

    def logo(self, variante: str = "principal") -> Path | None:
        """Logo listo para FFmpeg (PNG/JPG/WebP). Un SVG se rasteriza si hay Pillow+resvg; si no, se avisa."""
        logos = self.datos.get("logo") or {}
        p = self._archivo(logos.get(variante) or logos.get("principal"))
        if p is None:
            return None
        if p.suffix.lower() in _RASTER:
            return p
        self.avisos.append(f"el logo {p.name} es {p.suffix}: para vídeo añade también una versión PNG con fondo "
                           "transparente (`logo.principal` o `logo.claro` en marca.json)")
        hermano = p.with_suffix(".png")
        return hermano if hermano.exists() else None


def cargar(cliente: str | None = None, ruta: str | Path | None = None) -> Marca:
    """Marca resuelta: defecto ⊕ `clientes/<cliente>/marca/marca.json` (o `ruta`, que prevalece)."""
    base = json.loads(DEFECTO.read_text(encoding="utf-8"))
    archivo: Path | None = Path(ruta) if ruta else None
    if archivo is None and cliente:
        d = marca_dir(cliente)
        archivo = d / "marca.json" if d else None
    marca = Marca(base, None)
    if archivo is None:
        return marca
    if not archivo.exists():
        if ruta:
            raise MarcaInvalida(f"no existe {archivo}")
        marca.avisos.append(f"el cliente «{cliente}» no tiene marca/marca.json: uso la marca neutra del producto")
        return marca
    try:
        extra = json.loads(archivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise MarcaInvalida(f"{archivo} no es JSON válido (línea {e.lineno}): {e.msg}") from None
    if not isinstance(extra, dict):
        raise MarcaInvalida(f"{archivo} debe ser un objeto JSON")
    marca = Marca(_fusion(base, extra), archivo.parent)
    for k, v in marca.datos.get("colores", {}).items():
        hex_valido(v)
    for k in ("color", "resaltado", "contorno"):
        if marca.sub(k):
            hex_valido(marca.sub(k))
    if contraste(marca.color("primario"), marca.color("texto_sobre_primario")) < 4.5:
        marca.avisos.append("contraste bajo entre `primario` y `texto_sobre_primario` (< 4,5:1, WCAG AA): el hook se "
                            "leerá peor en móvil")
    return marca
