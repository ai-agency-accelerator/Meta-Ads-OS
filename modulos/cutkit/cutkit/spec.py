"""Contratos de cutkit: lo que se pasan las etapas entre sí.

Flujo:  ingest → MediaIndex  →  (agente) ContentGraph + EditPlan (decisiones EDF ancladas a palabras)
        → assets (AssetManifest) → compile → Timeline (segundos de programa, encajados a fotograma)
        → backend HyperFrames (index.html) + AudioPlan → render → QA → export.

Reglas de oro:
- El LLM nunca escribe tiempos absolutos: ancla a ids de palabra (`w_0012`) y el compilador resuelve.
- Toda decisión lleva su porqué (`motive`) y es parcheable: editar = op sobre decisiones → versión hija.
- Ningún texto en pantalla afirma algo que no se dice o que no tenga fuente (`source`).
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

FPS_SHORTS = 30
W_SHORTS, H_SHORTS = 1080, 1920


# ───────────────────────────── transcripción / análisis ─────────────────────────────
class Word(BaseModel):
    id: str                       # w_0000… estable por fuente
    src: str                      # id de la fuente (main, outro…)
    text: str                     # texto mostrado (corregido con glosario)
    raw: str | None = None        # lo que dijo el ASR si se corrigió
    s: float                      # inicio en segundos de la FUENTE
    e: float
    punct_after: str = ""         # puntuación que sigue (. , ? !)


class Pause(BaseModel):
    src: str
    s: float
    e: float
    kind: Literal["fin_frase", "coma", "interna", "respiracion", "dramatica", "aire_muerto"] = "interna"


class FaceSample(BaseModel):
    t: float                      # segundos de la fuente
    x: float; y: float; w: float; h: float   # normalizado 0..1, origen arriba-izquierda


class Source(BaseModel):
    id: str                       # main | outro | broll_x …
    path: str                     # original
    mezzanine: str                # 1080x1920 (o 1920x1080) CFR 30 fps H.264, sin audio
    audio: str                    # WAV 48 kHz mono de la voz
    duration: float
    width: int
    height: int
    fps: float


class MediaIndex(BaseModel):
    slug: str
    sources: list[Source]
    words: list[Word]
    pauses: list[Pause] = []
    faces: dict[str, list[FaceSample]] = {}   # por fuente, ~10 muestras/s
    audio_stats: dict[str, Any] = {}

    def words_of(self, src: str) -> list[Word]:
        return [w for w in self.words if w.src == src]


# ───────────────────────────── decisiones editoriales (EDF) ─────────────────────────
MotiveCode = Literal[
    "mostrar_lo_que_se_dice", "enumeracion", "cambio_de_idea", "prueba_credibilidad", "enfasis",
    "transicion_de_seccion", "contexto_visual", "cta", "cambio_de_energia", "eliminar_pausa_o_error",
    "humor", "recuperar_atencion", "ritmo", "contencion", "cierre", "gancho",
]


class Motive(BaseModel):
    code: MotiveCode
    text: str                     # el porqué en una frase, en español


class Anchor(BaseModel):
    """Tramo anclado a palabras. `start`/`end` son ids de palabra; offsets en segundos (lead negativo = antes)."""
    start: str
    end: str | None = None        # None = sólo la palabra de inicio
    start_edge: Literal["s", "e"] = "s"
    end_edge: Literal["s", "e"] = "e"
    lead: float = -0.155          # la imagen entra ~155 ms antes de la palabra (medido en referencias)
    tail: float = 0.0
    min_dur: float | None = None


DecisionType = Literal[
    "aroll.cut",        # quitar un tramo de la fuente (params: from_word/to_word o s/e de fuente)
    "aroll.pause",      # ajustar una pausa a su clase (params: target)
    "layout",           # full_face | split_top | broll_full | card_float  (params.kind)
    "camera",           # punch_in | slow_push | reframe | hold (params.kind, scale, ease)
    "broll",            # recurso visual (params: asset, slot, treatment, component)
    "graphic",          # componente de motion (params: component, props)
    "caption.emphasis", # palabra destacada (params: treatment hero|accent|scale|color, color)
    "caption.hide",     # ocultar raíl en un tramo (cuando un gráfico ya dice el texto)
    "transition",       # light_leak | flash | whip | zoom_blur | glitch
    "sfx",              # params: kind (whoosh|pop|click|riser|impact|ding|type|glitch), gain_db, offset
    "music",            # params: track, gain_lu, dropouts:[anchors]
]


class Decision(BaseModel):
    id: str
    type: DecisionType
    anchor: Anchor
    params: dict[str, Any] = {}
    motive: Motive
    source: str | None = None     # de dónde sale lo que se afirma (palabras, URL, fichero de datos)
    confidence: float = 0.8
    alternatives: list[dict[str, Any]] = []
    by: Literal["director", "usuario", "qa", "perfil"] = "director"
    locked: bool = False          # la fijó el usuario: replan no la toca


class Beat(BaseModel):
    id: str
    start: str                    # id de palabra
    end: str
    function: str                 # gancho, explicacion, ejemplo, cifra, opinion, cta, cierre…
    summary: str
    energy: Literal["baja", "media", "alta"] = "media"


class EditPlan(BaseModel):
    slug: str
    version: str = "v001"
    parent: str | None = None
    reason: str = ""
    format: Literal["anuncio", "organico"] = "anuncio"   # perfil de recursos/perfiles/<format>.yaml
    style_profile: str = ""       # "" = estilo por defecto («firma»); un perfil de referencia solo con petición expresa
    style_request: str = ""       # cita literal del usuario si pide un perfil de referencia
    outro: bool = True            # el cierre del perfil se añade si el perfil lo tiene activado (`outro.enabled`)
    outro_variant: str = ""       # variante del outro del perfil (consultora | herramientas…); "" = la por defecto
    tokens: dict[str, Any] = {}  # tokens del vídeo (p. ej. subject_color = color de marca del tema)
    beats: list[Beat] = []
    decisions: list[Decision] = []
    notes: str = ""

    @model_validator(mode="after")
    def _ids_unicos(self):
        ids = [d.id for d in self.decisions]
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            raise ValueError(f"ids de decisión repetidos: {sorted(dup)}")
        return self


# ───────────────────────────── assets ───────────────────────────────────────────────
class Asset(BaseModel):
    id: str
    kind: Literal["image", "video", "svg", "audio", "html"]
    path: str                     # ruta local congelada (<proyecto>/edicion/media/…)
    sha256: str | None = None
    origin: Literal["usuario", "library", "logo", "web_capture", "web_scroll", "stock", "gen_image",
                    "gen_video", "programmatic", "music_gen", "sfx_library"] = "library"
    source_url: str | None = None
    license: str = ""
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    notes: str = ""


class AssetRequest(BaseModel):
    id: str
    kind: Literal["logo", "web_capture", "web_scroll", "gen_image", "gen_video", "stock", "file", "music"]
    query: str                    # entidad, URL, prompt o ruta
    params: dict[str, Any] = {}   # aspect, size, dark, selector, seconds, style…
    for_decision: str | None = None


class AssetManifest(BaseModel):
    slug: str
    assets: dict[str, Asset] = {}
    requests: list[AssetRequest] = []
    budget_usd: float = 2.0
    spent_usd: float = 0.0


# ───────────────────────────── timeline compilada ───────────────────────────────────
class ArollSegment(BaseModel):
    id: str
    src: str
    src_in: float                 # segundos de la fuente (encajados a fotograma)
    src_out: float
    prog_in: float = 0.0          # segundos de programa (los calcula el compilador)
    prog_out: float = 0.0
    hold_after: float = 0.0       # segundos de último fotograma congelado tras el tramo (respiración antes del outro)


class TimelineItem(BaseModel):
    id: str
    track: Literal["layout", "camera", "broll", "graphic", "caption", "transition", "overlay"]
    t0: float                     # segundos de programa
    t1: float
    component: str | None = None  # nombre en la librería de motion (cutkit/motion)
    props: dict[str, Any] = {}
    cues: dict[str, float] = {}   # tiempos internos (p. ej. cada elemento de una lista) en segundos de programa
    decision_ids: list[str] = []
    z: int = 10


class AudioItem(BaseModel):
    id: str
    kind: Literal["voice", "music", "sfx"]
    path: str
    t0: float                     # segundos de programa en que suena el punto de sincronía
    media_start: float = 0.0
    dur: float | None = None
    gain_db: float = 0.0
    sync_offset: float = 0.0      # ms→s desde el inicio del fichero hasta el transitorio que se alinea
    pitch: float = 0.0            # semitonos (variación de SFX repetidos / firma de plantilla)
    fade_in: float = 0.0
    fade_out: float = 0.0
    duck: bool = False
    automation: list[tuple[float, float]] = []   # (t programa, gain_db)
    decision_ids: list[str] = []


class Timeline(BaseModel):
    slug: str
    version: str
    fps: int = FPS_SHORTS
    width: int = W_SHORTS
    height: int = H_SHORTS
    duration: float = 0.0
    aroll: list[ArollSegment] = []
    items: list[TimelineItem] = []
    audio: list[AudioItem] = []
    word_times: dict[str, tuple[float, float]] = {}   # id palabra → (s, e) en programa (si sobrevive al corte)
    style: dict[str, Any] = {}    # tokens resueltos (fuentes, colores, motion)

    def frame(self, t: float) -> int:
        return int(round(t * self.fps))


# ───────────────────────────── QA ───────────────────────────────────────────────────
class QAIssue(BaseModel):
    id: str
    check: str                    # grupo.check
    severity: Literal["block", "warn", "info"]
    t0: float | None = None
    t1: float | None = None
    message: str
    evidence: dict[str, Any] = {}
    blame: list[str] = []         # ids de decisión culpables
    fix: list[dict[str, Any]] = []


class QAReport(BaseModel):
    slug: str
    version: str
    verdict: Literal["pass", "warn", "fail"]
    summary_es: str
    issues: list[QAIssue] = []
    metrics: dict[str, Any] = {}
