"""Contratos de datos del motor (pydantic v2).

Todo lo que se persiste o viaja entre módulos está definido aquí. Los módulos se comunican
solo con estos tipos, de modo que un proveedor o una etapa se puede sustituir sin romper
el resto.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def now() -> float:
    return time.time()


# ───────────────────────────── Assets ─────────────────────────────


class AssetKind(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"
    font = "font"
    data = "data"


class Asset(BaseModel):
    id: str  # sha256 truncado del contenido
    kind: AssetKind
    path: str  # relativo al almacén de assets
    mime: str = ""
    bytes: int = 0
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    fps: float | None = None
    has_audio: bool | None = None
    source: str = "upload"  # upload | provider:model | render | local
    meta: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=now)


# ───────────────────────────── Marca y producto ─────────────────────────────


class BrandKit(BaseModel):
    id: str = Field(default_factory=lambda: new_id("brand"))
    name: str
    colors: dict[str, str] = Field(default_factory=lambda: {"primary": "#111111", "accent": "#FF3B30", "text": "#FFFFFF"})
    font_heading: str | None = None  # asset id de fuente o nombre de fuente incluida
    font_body: str | None = None
    logo_asset_ids: list[str] = Field(default_factory=list)
    tone: str = "cercano, directo, nada corporativo"
    do_rules: list[str] = Field(default_factory=list)
    dont_rules: list[str] = Field(default_factory=list)
    approved_claims: list[str] = Field(default_factory=list)
    disclaimers: list[str] = Field(default_factory=list)
    ctas: list[str] = Field(default_factory=list)
    locales: list[str] = Field(default_factory=lambda: ["es-ES"])
    regulatory_profile: str = "generic"  # generic | health | finance | alcohol | kids
    ai_label_policy: Literal["visible", "end_card", "metadata_only"] = "visible"
    notes: str = ""
    created_at: float = Field(default_factory=now)


class Product(BaseModel):
    id: str = Field(default_factory=lambda: new_id("prod"))
    brand_id: str
    name: str
    kind: Literal["physical", "app", "service"] = "physical"
    description: str = ""
    benefits: list[str] = Field(default_factory=list)
    proof_points: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    price: str | None = None
    url: str | None = None
    packshot_asset_ids: list[str] = Field(default_factory=list)  # fotos reales del producto
    footage_asset_ids: list[str] = Field(default_factory=list)  # vídeo real del producto
    screenshot_asset_ids: list[str] = Field(default_factory=list)  # capturas reales (apps)
    screen_recording_asset_ids: list[str] = Field(default_factory=list)  # grabaciones reales (apps)
    expected_label_text: list[str] = Field(default_factory=list)  # para QA OCR
    visual_description: str = ""  # cómo es físicamente (para prompts)
    created_at: float = Field(default_factory=now)


# ───────────────────────────── Actores persistentes ─────────────────────────────


class VoiceProfile(BaseModel):
    locale: str = "es-ES"
    provider: str = "gemini"
    voice_name: str = "Aoede"
    style_prompt: str = ""  # cómo habla: ritmo, energía, muletillas
    speaking_rate: float = 1.0
    reference_audio_asset_id: str | None = None
    model: str | None = None  # versión fijada


class Look(BaseModel):
    id: str = Field(default_factory=lambda: new_id("look"))
    name: str
    wardrobe: str  # descripción exacta de ropa
    hair_makeup: str = ""
    accessories: str = ""
    reference_asset_ids: list[str] = Field(default_factory=list)  # hoja de vestuario


class BankClip(BaseModel):
    asset_id: str
    look_id: str | None = None
    framing: Literal["closeup", "medium", "medium_wide"] = "medium"
    emotion: str = "neutral"
    location: str = ""
    duration: float = 0.0
    kind: Literal["talking", "reaction", "idle", "listening"] = "talking"
    approved: bool = True


class IdentityProfile(BaseModel):
    embedding_model: str = "opencv-sface-2021dec"
    centroid: list[float] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)
    threshold: float = 0.42  # coseno mínimo para «misma persona» (calibrable)
    calibrated: bool = False
    self_similarity: float | None = None  # similitud media ref-vs-ref (techo)
    # impostores: caras PARECIDAS (misma descripción, otros actores). El generador produce «gemelas» que SFace
    # puntúa ~0,7; el umbral fijo no las separa, compararse contra ellas sí.
    impostor_asset_ids: list[str] = Field(default_factory=list)
    impostor_embeddings: list[list[float]] = Field(default_factory=list)
    impostor_p99: float | None = None


class Actor(BaseModel):
    id: str = Field(default_factory=lambda: new_id("actor"))
    handle: str  # @actor_03
    name: str = ""
    synthetic: bool = True
    consent_asset_id: str | None = None  # obligatorio si synthetic=False
    appearance: str  # descripción canónica: edad, piel, pelo, rasgos, complexión
    persona: str = ""  # personalidad y forma de hablar
    gender: Literal["female", "male", "other"] = "female"
    sheet_views: dict[str, str] = Field(default_factory=dict)  # asset_id → vista (front_neutral, three_quarter_left…)
    master_portrait_id: str | None = None
    sheet_asset_ids: list[str] = Field(default_factory=list)  # multivista
    expression_asset_ids: list[str] = Field(default_factory=list)
    fullbody_asset_ids: list[str] = Field(default_factory=list)
    looks: list[Look] = Field(default_factory=list)
    voices: dict[str, VoiceProfile] = Field(default_factory=dict)  # por locale
    bank: list[BankClip] = Field(default_factory=list)
    identity: IdentityProfile = Field(default_factory=IdentityProfile)
    model_versions: dict[str, str] = Field(default_factory=dict)  # modelos usados al crearlo
    regression_asset_ids: list[str] = Field(default_factory=list)  # clips de regresión
    exclusive_brand_id: str | None = None
    created_at: float = Field(default_factory=now)

    @property
    def pronoun(self) -> str:
        return {"female": "She", "male": "He"}.get(self.gender, "The person")

    def look(self, look_id: str | None) -> Look | None:
        for lk in self.looks:
            if lk.id == look_id or lk.name == look_id:
                return lk
        return self.looks[0] if self.looks else None

    def all_identity_refs(self) -> list[str]:
        ids = [self.master_portrait_id] if self.master_portrait_id else []
        ids += self.sheet_asset_ids + self.expression_asset_ids
        return [i for i in ids if i]


# ───────────────────────────── Brief y plan creativo ─────────────────────────────


Platform = Literal["tiktok", "reels", "shorts", "meta_feed", "generic"]


class Brief(BaseModel):
    brand_id: str
    product_id: str
    objective: str = "conversión"
    audience: str = ""
    key_messages: list[str] = Field(default_factory=list)
    locale: str = "es-ES"
    duration_s: float = 25.0
    platform: Platform = "reels"
    aspect: Literal["9:16", "4:5", "1:1", "16:9"] = "9:16"
    actor_ids: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)  # urls o notas de referencia
    tier: Literal["A", "B", "C"] = "C"
    style_notes: str = ""
    budget_usd: float | None = None
    n_angles: int = 6
    quality: Literal["draft", "final"] = "final"


class Angle(BaseModel):
    id: str = Field(default_factory=lambda: new_id("ang"))
    family: Literal["pain", "desire", "mechanism", "social_proof", "objection", "offer", "novelty", "comparison"] = "pain"
    insight: str
    promise: str
    proof: str = ""
    hooks: list[str] = Field(default_factory=list)
    score: float = 0.0
    rationale: str = ""


class ScriptSegment(BaseModel):
    id: str = Field(default_factory=lambda: new_id("seg"))
    role: Literal["hook", "problem", "agitate", "solution", "demo", "proof", "offer", "cta"] = "hook"
    speaker: str | None = None  # actor id o None (sin voz)
    text: str = ""  # lo que se dice
    on_screen_text: str = ""  # texto en pantalla (no se genera con IA: se compone)
    emotion: str = "neutral"
    gesture: str = ""
    est_duration: float = 3.0


class Script(BaseModel):
    locale: str = "es-ES"
    title: str = ""
    angle_id: str | None = None
    segments: list[ScriptSegment] = Field(default_factory=list)
    cta: str = ""

    def full_text(self) -> str:
        return " ".join(s.text for s in self.segments if s.text)


ShotType = Literal[
    "talking_head",  # actor habla a cámara
    "reaction",  # reacción muda corta (hook)
    "actor_motion",  # actor sin hablar en movimiento
    "product_hand",  # actor con producto
    "product_hero",  # producto solo (packshot real animado o generado)
    "app_screen",  # pantalla real de la app en un móvil
    "broll",  # recurso / ambiente
    "graphic_card",  # tarjeta de texto / CTA
]


class Route(BaseModel):
    pipeline: str  # p.ej. "talking.native_dialogue", "i2v", "compose.app_phone", "library"
    provider: str  # "gemini" | "fal" | "local" | "mock"
    model: str = ""
    params: dict[str, Any] = Field(default_factory=dict)
    est_cost_usd: float = 0.0
    fallbacks: list[dict[str, Any]] = Field(default_factory=list)
    reason: str = ""


class Shot(BaseModel):
    id: str = Field(default_factory=lambda: new_id("scn"))
    index: int = 0
    shot_type: ShotType = "talking_head"
    segment_ids: list[str] = Field(default_factory=list)
    duration: float = 3.0
    description: str = ""  # qué pasa en el plano
    camera: str = "selfie_handheld"  # preset de cámara UGC
    location: str = ""
    look_id: str | None = None
    actor_id: str | None = None
    uses_product: bool = False
    keyframe_prompt: str = ""
    motion_prompt: str = ""
    dialogue: str = ""  # texto hablado en este plano
    route: Route | None = None
    seed: int = 0
    revision: int = 0
    constraints: dict[str, Any] = Field(default_factory=dict)  # refuerzos tras QA
    keyframe_asset_id: str | None = None
    clip_asset_id: str | None = None
    audio_asset_id: str | None = None
    status: Literal["planned", "generating", "ready", "rejected", "failed"] = "planned"
    attempts: int = 0
    notes: list[str] = Field(default_factory=list)
    takes: list[dict[str, Any]] = Field(default_factory=list)  # historial: tomas anteriores (nunca se borran)


class ContinuityBible(BaseModel):
    actor_id: str | None = None
    look_id: str | None = None
    location: str = ""
    lighting: str = ""
    props: list[str] = Field(default_factory=list)
    time_of_day: str = ""
    camera_device: str = "iPhone 15, cámara frontal, 30 fps"
    color_grade: str = "natural, sin look de cine"


# ───────────────────────────── Timeline (edición no destructiva) ─────────────────────────────


class Keyframe(BaseModel):
    t: float  # segundos relativos al clip
    scale: float = 1.0
    x: float = 0.5  # centro normalizado
    y: float = 0.5


class VideoClip(BaseModel):
    grade: dict[str, float] = Field(default_factory=dict)  # p. ej. {"saturation": 1.15} (corrige planos generados lavados)
    id: str = Field(default_factory=lambda: new_id("clip"))
    scene_id: str
    asset_id: str
    start: float  # en la timeline
    duration: float
    src_in: float = 0.0
    speed: float = 1.0
    fit: Literal["cover", "contain"] = "cover"
    zoom: list[Keyframe] = Field(default_factory=list)  # punch-in / ken burns
    mute: bool = True  # el audio del clip se ignora salvo que se indique
    volume: float = 1.0


class Overlay(BaseModel):
    id: str = Field(default_factory=lambda: new_id("ovl"))
    kind: Literal["image", "video", "text", "phone_screen", "logo", "label"] = "image"
    asset_id: str | None = None
    text: str = ""
    start: float = 0.0
    duration: float = 1.0
    x: float = 0.5
    y: float = 0.5
    w: float = 0.5  # ancho normalizado respecto al lienzo
    style: dict[str, Any] = Field(default_factory=dict)
    animation: Literal["none", "fade", "pop", "slide_up"] = "pop"
    corner_pin: list[list[float]] | None = None  # 4 puntos normalizados (tl,tr,br,bl)


class Word(BaseModel):
    text: str
    start: float
    end: float


class CaptionTrack(BaseModel):
    words: list[Word] = Field(default_factory=list)
    style: str = "clean"  # «tiktok_bold» (karaoke amarillo) delata plantilla de CapCut; «clean» se ve más nativo
    max_words_per_line: int = 4
    position_y: float = 0.635  # borde inferior ≈ y=1220 px: dentro de la zona segura común Meta/TikTok
    enabled: bool = True
    boxed_spans: list[tuple[float, float]] = Field(default_factory=list)  # tramos con fondo (p. ej. sobre la app)
    hidden_spans: list[tuple[float, float]] = Field(default_factory=list)  # tramos sin subtítulos (rótulo con lo mismo)


class AudioClip(BaseModel):
    id: str = Field(default_factory=lambda: new_id("aud"))
    role: Literal["voice", "music", "sfx", "native", "room"] = "voice"
    asset_id: str
    start: float
    duration: float | None = None
    gain_db: float = 0.0
    src_in: float = 0.0
    duck_under_voice: bool = False
    fade_in: float = 0.0
    fade_out: float = 0.0
    loop_src: float | None = None  # «room»: repite [src_in, src_in+loop_src] durante toda la pieza


class Timeline(BaseModel):
    width: int = 1080
    height: int = 1920
    fps: int = 30
    duration: float = 0.0
    clips: list[VideoClip] = Field(default_factory=list)
    overlays: list[Overlay] = Field(default_factory=list)
    captions: CaptionTrack = Field(default_factory=CaptionTrack)
    audio: list[AudioClip] = Field(default_factory=list)
    look: dict[str, Any] = Field(default_factory=lambda: {"grain": 0.04, "phone_audio": True, "lut": None})
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: int = 1


# ───────────────────────────── QA ─────────────────────────────


DefectCategory = Literal[
    "identity_drift",
    "wardrobe_change",
    "flicker",
    "face_artifact",
    "eyes_teeth",
    "lip_sync",
    "hands",
    "physics",
    "product_wrong",
    "logo_text",
    "caption_error",
    "continuity",
    "pacing",
    "audio",
    "voice",
    "ai_look",
    "freeze_black",
    "duration",
    "safety_compliance",
    "extra_object",  # p. ej. un segundo móvil en la mano en un selfie
    "silent_mouth",  # la boca se mueve en un plano que debe ir sin diálogo
    "burned_text",  # el generador ha incrustado subtítulos o texto en la imagen
    "other",
]


class Defect(BaseModel):
    scene_id: str | None = None
    category: DefectCategory = "other"
    severity: float = 0.5  # 0..1
    start: float | None = None
    end: float | None = None
    evidence: str = ""
    source: str = "deterministic"  # deterministic | vlm:<model>
    confidence: float = 0.5


class RegenAction(BaseModel):
    kind: Literal[
        "reroll_seed",
        "strengthen_identity",
        "shorten_shot",
        "switch_model",
        "relipsync",
        "recompose_product",
        "fix_captions",
        "rerender_only",
        "rewrite_line",
        "none",
    ] = "none"
    params: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""


class SceneVerdict(BaseModel):
    scene_id: str
    passed: bool = True
    score: float = 1.0
    defects: list[Defect] = Field(default_factory=list)
    action: RegenAction = Field(default_factory=RegenAction)

    def summary(self) -> str:
        if self.passed:
            return f"{self.scene_id} OK ({self.score:.2f})"
        cats = " + ".join(sorted({d.category for d in self.defects})) or "petición manual"
        return f"{self.scene_id} rejected → {cats} → {self.action.kind}: {self.action.reason}"


class QAReport(BaseModel):
    project_id: str
    version: int = 1
    passed: bool = False
    score: float = 0.0
    scenes: list[SceneVerdict] = Field(default_factory=list)
    global_defects: list[Defect] = Field(default_factory=list)
    checks: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=now)
    # revisión visual multimodal: done | missing (juez caído, sin saldo o simulado). «missing» nunca es APROBADO.
    visual_review: str = "done"
    needs_review: list[str] = Field(default_factory=list)  # hallazgos que un humano debe mirar antes de publicar

    @property
    def verdict(self) -> str:
        if not self.passed:
            return "rejected"
        if self.visual_review != "done":
            return "unreviewed"
        return "needs_review" if self.needs_review else "approved"


# ───────────────────────────── Proyecto ─────────────────────────────


class Project(BaseModel):
    id: str = Field(default_factory=lambda: new_id("proj"))
    name: str = ""
    brief: Brief
    status: str = "created"
    angles: list[Angle] = Field(default_factory=list)
    chosen_angle_id: str | None = None
    script: Script | None = None
    continuity: ContinuityBible = Field(default_factory=ContinuityBible)
    shots: list[Shot] = Field(default_factory=list)
    voice_asset_id: str | None = None
    words: list[Word] = Field(default_factory=list)
    timeline: Timeline | None = None
    render_asset_id: str | None = None
    qa_reports: list[QAReport] = Field(default_factory=list)
    variants: list[dict[str, Any]] = Field(default_factory=list)
    versions: list[dict[str, Any]] = Field(default_factory=list)  # cada render: timeline inmutable (asset) + vídeo
    parent_id: str | None = None  # si es variante
    variant_spec: dict[str, Any] = Field(default_factory=dict)
    log: list[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=now)
    updated_at: float = Field(default_factory=now)

    def scene_order(self) -> list[str]:
        """Numeración ÚNICA de escenas (S1, S2…): orden de aparición en el vídeo; luego las que no salen en el montaje.
        La usan la UI, las órdenes («regenera la escena 3») y el proxy del juez multimodal."""
        seen: list[str] = []
        for c in sorted(self.timeline.clips, key=lambda c: c.start) if self.timeline else []:
            if c.scene_id not in seen and any(s.id == c.scene_id for s in self.shots):
                seen.append(c.scene_id)
        return seen + [s.id for s in self.shots if s.id not in seen]

    def scene_number(self, shot_id: str) -> int:
        order = self.scene_order()
        return order.index(shot_id) + 1 if shot_id in order else 0

    def shot(self, shot_id: str) -> Shot:
        for s in self.shots:
            if s.id == shot_id or str(s.index) == str(shot_id):
                return s
        raise KeyError(shot_id)

    def segment(self, seg_id: str) -> ScriptSegment | None:
        if not self.script:
            return None
        for s in self.script.segments:
            if s.id == seg_id:
                return s
        return None


# ───────────────────────────── Costes y trabajos ─────────────────────────────


class CostEntry(BaseModel):
    id: str = Field(default_factory=lambda: new_id("cost"))
    ts: float = Field(default_factory=now)
    project_id: str | None = None
    scene_id: str | None = None
    step: str = ""  # concept | script | image | video | voice | lipsync | qa | render | storage | music
    provider: str = ""
    model: str = ""
    unit: str = ""  # second | image | 1k_tokens | request | minute
    quantity: float = 0.0
    unit_price: float = 0.0
    usd: float = 0.0
    latency_s: float = 0.0
    status: str = "ok"  # ok | error | cached | estimated
    cached: bool = False
    note: str = ""
    phase: str = ""  # produce | retake (intento extra dentro de un paso) | regeneration (bucle de QA o manual) | variant


class Job(BaseModel):
    id: str = Field(default_factory=lambda: new_id("job"))
    kind: str
    project_id: str | None = None
    status: Literal["queued", "running", "done", "failed", "cancelled"] = "queued"
    progress: float = 0.0
    message: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=now)
    updated_at: float = Field(default_factory=now)
