"""Catálogo de SFX y elección determinista con variación.

`catalog()` carga `datos/sfx/catalogo.yaml`. Si no existe lo crea: las reglas evento→SFX de
`recursos/sfx/eventos.yaml` + el inventario medido (duración, sonoridad, pico, punto de sincronía, centroide) de la
biblioteca sintética CC0 de `datos/sfx/` (la genera `ck instalar`, ver `sfx_sinteticos`) y, si defines `CK_SFX_DIR`, de
tu propia biblioteca (subcarpetas por tipo: `whoosh_corto/`, `pop/`, `click/`…; el resto se clasifica por duración y
timbre). A cada fichero le añade `kind`, la clase gruesa que usan las decisiones del director
(whoosh|pop|click|riser|impact|ding|type|glitch|tick|brillo).

`pick(kind, seed)` acepta una clase gruesa (`whoosh`), un tipo fino del catálogo (`whoosh_corto`) o un evento
(`tarjeta_entra`, cuya lista `ficheros` manda el orden). Es determinista: misma semilla → mismo fichero; semillas
enteras consecutivas → ficheros distintos (nunca el mismo dos veces seguidas). Devuelve tramo, sincronía, ganancia de
normalización y variación (semitonos y dB). `Picker` lleva la cuenta en un vídeo entero (≤ 2 usos por fichero).
"""
from __future__ import annotations

import copy
import datetime as _dt
import hashlib
import os
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

from ..paths import DATOS, LIBRARY, RECURSOS
from . import _dsp as d

SFX_DIR = DATOS / "sfx"                                 # biblioteca sintética (CC0) que genera `ck instalar`
CATALOG = SFX_DIR / "catalogo.yaml"
EVENTOS = RECURSOS / "sfx" / "eventos.yaml"
PROC_DIR = LIBRARY / "sfx_proc"                         # copias procesadas (paso alto, campana) de `sfxplan`
LICENCIA_SINTETICA = "CC0 1.0 (sintetizado por cutkit, sin muestras de terceros)"


def bibliotecas() -> list[Path]:
    """Carpetas que se inventarían: la sintética y, si existe, la tuya (`CK_SFX_DIR`)."""
    out = [SFX_DIR]
    extra = os.environ.get("CK_SFX_DIR", "").strip()
    if extra and Path(extra).expanduser().is_dir():
        out.append(Path(extra).expanduser())
    return out


# tipo fino del catálogo → clase gruesa del director
KIND_OF = {
    "whoosh_corto": "whoosh", "whoosh_medio": "whoosh", "whoosh_largo": "whoosh", "whoosh_ascendente": "whoosh",
    "whoosh_giro": "whoosh", "whoosh_inverso": "riser", "paquete_whoosh": "whoosh",
    "pop": "pop", "pop_tonal": "pop", "golpe": "pop",
    "click": "click", "click_mecanico": "click", "paquete_ui": "click",
    "riser": "riser",
    "impacto_sub": "impact", "impacto_grave": "impact",
    "ding": "ding", "bip_ui": "ding", "bip_tono": "ding", "paquete_error": "ding",
    "tecleo": "type",
    "glitch": "glitch",
    "tick": "tick", "tick_contador": "tick", "paquete_tick": "tick", "tictac": "tick",
    "firma": "pop", "brillo": "brillo", "error": "ding",
}
# si una clase no tiene candidatos, a qué otras recurrir
FALLBACK = {"pop": ["click", "ding"], "click": ["pop", "tick"], "tick": ["click"], "ding": ["pop"],
            "impact": ["pop"], "riser": ["whoosh"], "glitch": ["click"]}
# nivel por defecto respecto a la voz (M máx. del SFX − loudness a corto plazo de la voz), sound_design.md §3
REL_VOICE_LU = {"whoosh": -12.0, "pop": -14.0, "click": -17.0, "riser": -8.0, "impact": -6.0, "ding": -12.0,
                "type": -19.0, "glitch": -12.0, "tick": -18.0, "brillo": -16.0}
# variación (semitonos) por clase, sound_design.md §4
PITCH_RANGE = {"whoosh": 2.0, "pop": 1.0, "click": 1.0, "tick": 1.0, "ding": 1.0, "impact": 0.5, "riser": 0.5,
               "glitch": 1.0, "type": 0.0, "brillo": 1.0}
GAIN_JITTER_DB = 1.5
# carpetas que solo se usan si el guion lo pide (por id o por evento, nunca por clase gruesa): la firma va reservada
# a su paleta (`reservados` de recursos/sfx/animaciones.yaml) y el reloj y el error cuentan algo concreto
SOLO_A_PETICION = {"ambiente", "personas", "alarma", "suspense", "firma", "tictac", "error"}


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower().strip()


def _stable(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16)


# ───────────────────────────── construcción del catálogo ─────────────────────────────
TIPOS_LOOP = ("tecleo", "tictac", "ambiente", "cama_tension", "textura_datos")


def _tipo_de(path: Path, dur: float, centroid: float) -> str:
    """Tipo fino: el nombre de la subcarpeta si es un tipo conocido; si no, por duración y timbre."""
    folder = _norm(path.parent.name)
    if folder in KIND_OF or folder in TIPOS_LOOP or folder in SOLO_A_PETICION:
        return folder
    name = _norm(path.stem)
    for clave, tipo in (("riser", "riser"), ("whoosh", "whoosh_corto"), ("swoosh", "whoosh_corto"), ("click", "click"),
                        ("tick", "tick"), ("ding", "ding"), ("pop", "pop"), ("glitch", "glitch"), ("impact", "impacto_grave"),
                        ("typing", "tecleo"), ("keyboard", "tecleo")):
        if clave in name:
            return "whoosh_medio" if tipo == "whoosh_corto" and dur >= 0.8 else tipo
    if dur < 0.12:
        return "tick" if centroid > 1500 else "click"
    if dur < 0.6:
        return "glitch" if centroid > 5000 else "pop"
    return "whoosh_medio" if dur < 2.0 else "otro"


def _licencia(raiz: Path) -> str:
    if raiz == SFX_DIR:
        return LICENCIA_SINTETICA
    lic = raiz / "LICENCIA.txt"
    if lic.exists():
        return lic.read_text(encoding="utf-8").strip().splitlines()[0][:200]
    return "biblioteca propia (CK_SFX_DIR): comprueba que su licencia permite usarla en anuncios"


def inventory(lib_dir: Path = SFX_DIR) -> list[dict]:
    """Mide cada fichero de `lib_dir` (solo lectura) y le asigna tipo por carpeta (o por duración y timbre)."""
    out = []
    licencia = _licencia(lib_dir)
    for p in sorted(lib_dir.rglob("*")):
        if p.suffix.lower() not in (".wav", ".mp3", ".aif", ".aiff", ".m4a", ".flac", ".ogg") or not p.is_file():
            continue
        x = d.load(p, channels=2)
        if len(x) == 0:
            continue
        dur = len(x) / d.SR
        m = x.mean(axis=1)
        env = np.sqrt(np.convolve(m ** 2, np.ones(240) / 240, mode="same"))       # 5 ms
        peak_i = int(np.argmax(env))
        onset_i = int(np.argmax(env > env.max() * 0.1))
        spec = np.abs(np.fft.rfft(m[: min(len(m), d.SR * 4)]))
        fr = np.fft.rfftfreq(min(len(m), d.SR * 4), 1 / d.SR)
        centroid = float((spec * fr).sum() / (spec.sum() + 1e-9))
        tipo = _tipo_de(p, dur, centroid)
        kind = KIND_OF.get(tipo, tipo)
        mmax = d.momentary_max(np.vstack([x, np.zeros((d.SR // 2, 2))]))
        loop = tipo in TIPOS_LOOP
        ref = d.integrated_lufs(x) if loop else mmax
        sync = peak_i if kind in ("whoosh", "riser") else onset_i
        tp = d.true_peak_db(x)
        ident = p.stem if lib_dir == SFX_DIR else _norm(f"{p.parent.name}_{p.stem}").replace(" ", "_")
        out.append({
            "id": ident, "ruta": str(p), "tipo": tipo, "kind": kind,
            "duracion_s": round(dur, 3), "lufs_integrado": round(d.integrated_lufs(x), 1),
            "lufs_momentaneo_max": round(mmax, 1), "true_peak_dbtp": round(tp, 1),
            "referencia_normalizacion": "I" if loop else "M_max",
            "ganancia_a_-20_lufs_db": round(-20 - ref, 1),
            "necesita_limitador": bool(tp + (-20 - ref) > -1.0),
            "punto_sincronia_ms": int(round(sync / d.SR * 1000)),
            "modo_sincronia": "pico" if kind in ("whoosh", "riser") else "onset",
            "centroide_hz": int(centroid), "confianza_clasificacion": "alta" if lib_dir == SFX_DIR else "media",
            "licencia": licencia,
        })
    return out


def build_catalog(force: bool = False) -> Path:
    """Escribe `datos/sfx/catalogo.yaml`: reglas de `recursos/sfx/eventos.yaml` + inventario de las bibliotecas."""
    if CATALOG.exists() and not force:
        return CATALOG
    if not any(SFX_DIR.rglob("*.wav")):
        from . import sfx_sinteticos
        sfx_sinteticos.generar()                       # escribe los WAV y vuelve aquí con force=True
        return CATALOG
    data = yaml.safe_load(EVENTOS.read_text(encoding="utf-8")) if EVENTOS.exists() else {"version": 1, "eventos": {}}
    data["origen"] = {"reglas": "recursos/sfx/eventos.yaml", "bibliotecas": [str(b) for b in bibliotecas()],
                      "fecha": _dt.date.today().isoformat()}
    data["ficheros"] = [f for b in bibliotecas() for f in inventory(b)]
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    header = ("# Catálogo de SFX de cutkit (generado; no lo edites: cambia recursos/sfx/eventos.yaml o tu biblioteca).\n"
              "# Regenerar: uv run --project modulos/cutkit ck instalar\n")
    CATALOG.write_text(header + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    catalog.cache_clear()
    return CATALOG


@lru_cache(maxsize=1)
def catalog() -> dict:
    """Catálogo completo: {"version", "globales", "eventos", "ficheros": [...], "origen"}."""
    if not CATALOG.exists():
        build_catalog()
    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    for f in data.get("ficheros", []):
        f.setdefault("kind", KIND_OF.get(f.get("tipo"), f.get("tipo")))
    return data


def entries() -> list[dict]:
    return catalog().get("ficheros", [])


def lookup(path_or_id: str) -> dict | None:
    """Busca por id o por ruta (absoluta o nombre de fichero). Las copias procesadas de `sfxplan`
    (`datos/biblioteca/sfx_proc/<id>__<proceso>.wav`) devuelven la entrada de su original."""
    stem = Path(str(path_or_id)).stem
    if "__" in stem and "sfx_proc" in str(path_or_id):
        base = lookup(stem.split("__", 1)[0])
        if base is not None:
            return {**base, "ruta": str(path_or_id), "procesado": stem.split("__", 1)[1]}
    key = _norm(str(path_or_id))
    for f in entries():
        if _norm(f["id"]) == key or _norm(f["ruta"]) == key:
            return f
    name = _norm(Path(str(path_or_id)).name)
    for f in entries():
        if _norm(Path(f["ruta"]).name) == name:
            return f
    return None


# ───────────────────────────── sincronía medida ─────────────────────────────
@lru_cache(maxsize=512)
def measure_sync(path: str, media_start: float, dur: float, mode: str = "onset") -> float:
    """Punto de sincronía REAL del tramo tal como sonará (tras el paso alto de 120 Hz de `mix`), en s desde
    `media_start`. `onset`: primer instante con envolvente (2 ms) ≥ 30 % del máximo (ataque de pops, clicks,
    dings); `peak`: máximo de la envolvente de 10 ms (whoosh corto). El catálogo a veces marca el cuerpo y no el
    ataque (65 ms en algunos pops con cola), y un ataque > 40 ms antes de la imagen se nota."""
    from scipy import signal as _sg
    x = d.load(path, channels=1)[:, 0]
    seg = x[int(media_start * d.SR): int((media_start + dur) * d.SR)].astype(np.float64)
    if len(seg) < 64:
        return 0.0
    seg = _sg.sosfilt(_sg.butter(2, 120, "highpass", fs=d.SR, output="sos"), seg)
    w = 96 if mode == "onset" else 480
    env = np.sqrt(np.convolve(seg ** 2, np.ones(w) / w, mode="same"))
    if mode == "onset":
        return float(np.argmax(env >= 0.3 * env.max()) / d.SR)
    return float(np.argmax(env) / d.SR)


# ───────────────────────────── elección ─────────────────────────────
def _usable(f: dict) -> bool:
    """Los paquetes solo valen por sus recortes; fuera ambientes/personas/alarmas salvo petición expresa."""
    if f.get("excluido"):                          # retirado del catálogo (p. ej. «transición»: ataque saturado)
        return False
    if str(f.get("tipo", "")).startswith("paquete") and not f.get("recortes"):
        return False
    return Path(f["ruta"]).exists()


def candidates(kind: str) -> list[dict]:
    k = _norm(kind)
    cat = catalog()
    ev = (cat.get("eventos") or {}).get(k)
    if ev:
        ids = ev.get("ficheros")
        ids = ids if isinstance(ids, list) else [i for v in (ids or {}).values() for i in v]
        out = [lookup(i) for i in ids]
        out = [f for f in out if f and _usable(f)]
        if out:
            return out
    if k in set(KIND_OF.values()):                    # clase gruesa: todos sus tipos finos
        out = [f for f in entries() if _norm(str(f.get("kind"))) == k and _usable(f)
               and _norm(Path(f["ruta"]).parent.name) not in SOLO_A_PETICION]
    else:                                              # tipo fino del catálogo
        out = [f for f in entries() if _norm(str(f.get("tipo"))) == k and _usable(f)]
    for fb in FALLBACK.get(k, []) if not out else []:
        out = [f for f in entries() if f.get("kind") == fb and _usable(f)]
        if out:
            break
    return sorted(out, key=lambda f: f["id"]) if not ev else out


def pick(kind: str, seed: int | str = 0, *, avoid: str | None = None) -> dict:
    """Elige un SFX de `kind` de forma determinista.

    Devuelve una copia de la entrada con: `path`, `media_start`, `dur` (o None), `sync_offset` (s, desde
    `media_start` hasta el transitorio), `norm_gain_db` (a −20 LUFS), `rel_voice_lu` (nivel por defecto respecto a
    la voz; el del evento si `kind` es un evento), `pitch_semitones`, `gain_jitter_db` y `mix_gain_db` (el valor
    para `AudioItem.gain_db`: desplazamiento sobre el nivel de la clase que aplica `mix` + variación).
    """
    c = candidates(kind)
    if not c:
        raise LookupError(f"no hay SFX para «{kind}» en el catálogo")
    n = len(c)
    i = (_stable("k", _norm(kind)) + seed) % n if isinstance(seed, int) else _stable(seed, _norm(kind)) % n
    if avoid is not None and n > 1 and c[i]["id"] == avoid:
        i = (i + 1) % n
    f = copy.deepcopy(c[i])
    rng = np.random.default_rng(_stable("var", seed, f["id"]))
    k = f.get("kind") or kind
    media_start, dur = 0.0, None
    sync_ms = float(f.get("punto_sincronia_ms") or 0)
    gain = float(f.get("ganancia_a_-20_lufs_db") or 0.0)
    if f.get("recortes"):
        r = f["recortes"][int(rng.integers(len(f["recortes"])))]
        media_start, dur = r["inicio_ms"] / 1000, (r["fin_ms"] - r["inicio_ms"]) / 1000
        sync_ms = r["sync_ms"] - r["inicio_ms"]
        gain = float(r.get("ganancia_a_-20_lufs_db_aprox", gain))
    elif f.get("duracion_util_ms"):
        a, b = f["duracion_util_ms"]
        media_start, dur = a / 1000, (b - a) / 1000
        sync_ms = max(0.0, sync_ms - a)
    pr = PITCH_RANGE.get(k, 1.0)
    # nivel: el del evento del catálogo si `kind` es un evento (punto medio del rango), si no el de la clase
    rel = REL_VOICE_LU.get(k, -14.0)
    ev = (catalog().get("eventos") or {}).get(_norm(kind)) or {}
    lv = ev.get("nivel_rel_voz_lu")
    if isinstance(lv, dict):
        lv = lv.get(f.get("tipo")) or lv.get("pico") or next(iter(lv.values()), None)
    if isinstance(lv, (list, tuple)) and len(lv) == 2:
        rel = float(np.mean(lv))
    jitter = float(rng.uniform(-GAIN_JITTER_DB, GAIN_JITTER_DB))
    f.update({
        "path": f["ruta"], "media_start": round(media_start, 4), "dur": None if dur is None else round(dur, 4),
        "sync_offset": round(sync_ms / 1000, 4), "norm_gain_db": round(gain, 2),
        "rel_voice_lu": rel,
        "pitch_semitones": round(float(rng.uniform(-pr, pr if k not in ("impact", "riser") else 0.0)), 2),
        "gain_jitter_db": round(jitter, 2),
        # lo que el compilador pone en AudioItem.gain_db: mix calibra la clase a REL_VOICE_LU[kind] y suma esto
        "mix_gain_db": round(rel - REL_VOICE_LU.get(k, -14.0) + jitter, 2),
    })
    return f


class Picker:
    """Elección para un vídeo entero: nunca el mismo fichero seguido en una clase y ≤ `max_uses` por fichero."""

    def __init__(self, seed: str | int = "ck", max_uses: int | None = None):
        dens = (catalog().get("globales") or {}).get("densidad") or {}
        self.seed, self.max_uses = seed, max_uses or int(dens.get("max_usos_mismo_fichero_short", 2))
        self.last: dict[str, str] = {}
        self.uses: dict[str, int] = {}
        self.n: dict[str, int] = {}

    def pick(self, kind: str) -> dict:
        c = candidates(kind)
        for attempt in range(max(1, len(c)) * 2):
            k = self.n.get(kind, 0)
            self.n[kind] = k + 1
            f = pick(kind, (_stable(self.seed) % 997) + k, avoid=self.last.get(kind))
            if self.uses.get(f["id"], 0) < self.max_uses and f["id"] != self.last.get(kind):
                break
        self.last[kind] = f["id"]
        self.uses[f["id"]] = self.uses.get(f["id"], 0) + 1
        return f
