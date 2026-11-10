"""Actores persistentes: creación del paquete de actor y selección de referencias.

Paquete (activos propios, nunca dependientes de un ID de proveedor):
  - retrato maestro + hoja multivista (frente, 3/4 izq/dcha, sonrisa con dientes, plano medio, cuerpo entero)
  - looks con vestuario descrito y referencia visual
  - voz por locale (catálogo o diseñada) + descripción de voz para modelos con diálogo nativo
  - perfil de identidad (centroide SFace, umbral calibrado con la propia hoja)
  - versiones de modelo usadas (para regresión cuando cambie un proveedor)

Cada vista se valida contra el retrato maestro; si se aleja, se regenera una vez.
"""

from __future__ import annotations

from ..costs import scope
from ..models import Actor, Asset, Look, VoiceProfile
from ..providers import registry
from ..providers.base import ImageRequest, ProviderError
from ..store import ctx
from ..qa import objects
from . import identity

# en positivo: nombrar el móvil (aunque sea para negarlo) lo ceba en la imagen (auditoría QA)
NO_PHONE = "Her hands are empty: relaxed at her sides, resting on the counter or out of frame."

SHEET_VIEWS = [
    ("front_neutral", "Front-facing, neutral relaxed expression, mouth closed, looking into the lens, chest-up framing."),
    ("three_quarter_left", "Head turned about 30 degrees to her left (three-quarter view), soft natural expression, chest-up framing."),
    ("three_quarter_right", "Head turned about 30 degrees to her right (three-quarter view), soft natural expression, chest-up framing."),
    ("smile_teeth", "Front-facing genuine laugh showing her natural teeth, eyes slightly squinted, chest-up framing."),
    ("medium_talking", "Medium shot from the waist up, mid-sentence talking expression, one hand gesturing naturally."),
]


def _identity_refs(actor: Actor, n: int = 3) -> list[Asset]:
    ids = actor.all_identity_refs()[:n]
    return [ctx().db.get_asset(i) for i in ids]


def create_actor(handle: str, appearance: str, *, persona: str = "", wardrobe: str = "", location_hint: str = "",
                 locale: str = "es-ES", voice_id: str | None = None, voice_hint: str = "", gender: str = "female",
                 synthetic: bool = True, n_views: int = 4, project_id: str | None = None, n_twins: int = 3) -> Actor:
    """Crea un actor sintético persistente con su paquete de referencias. Coste típico ≈0,35–0,50 $."""
    actor = Actor(handle=handle if handle.startswith("@") else "@" + handle, name=handle.lstrip("@"), synthetic=synthetic,
                  appearance=appearance, persona=persona, gender=gender if gender in ("female", "male") else "other")
    img = registry.image()
    look = Look(name="principal", wardrobe=wardrobe or "a plain casual everyday top")
    base_scene = location_hint or "a real lived-in apartment with soft daylight from a window"
    pid = project_id or f"actor:{actor.handle}"
    prompt_master = (f"Vertical smartphone photo taken by a friend, chest-up, eye level. {appearance}. Wearing {look.wardrobe}. "
                     f"In {base_scene}. Neutral relaxed expression, looking into the lens. {NO_PHONE} Ordinary real person, "
                     "not a model; realistic skin texture with visible pores and tiny imperfections; natural non-retouched look; "
                     "true-to-life colors; no studio lighting; no cinematic grade; no text.")
    with scope(pid, "master"):
        master = img.generate(ImageRequest(prompt=prompt_master, aspect="9:16", size="1k", seed=11))[0]
    if objects.image_has_phone(ctx().assets.abspath(master)).get("phone"):
        # un maestro con un móvil en la mano contamina TODAS las tomas futuras del actor: se repite una vez
        with scope(pid, "master_retry"):
            master = img.generate(ImageRequest(prompt=prompt_master + " Both hands are empty and relaxed.", aspect="9:16",
                                               size="1k", seed=77))[0]
        if objects.image_has_phone(ctx().assets.abspath(master)).get("phone"):
            raise ProviderError("el retrato maestro sigue mostrando un móvil en la mano; cambia la descripción del actor")
    actor.master_portrait_id = master.id
    prof = identity.build_profile([master])
    if not prof.centroid:
        raise ProviderError("el retrato maestro no tiene una cara detectable; prueba otra descripción")
    sheet: list[str] = []
    for name, view in SHEET_VIEWS[:n_views]:
        for attempt in range(2):
            with scope(pid, f"sheet_{name}"):
                out = img.generate(ImageRequest(
                    prompt=(f"Same person as the reference image: keep the face, facial features, age, skin tone, hair and body "
                            f"proportions exactly identical. {view} Wearing {look.wardrobe}. Same kind of real home setting, "
                            f"soft daylight. {NO_PHONE} Smartphone photo, realistic skin texture, natural non-retouched look, no text."),
                    refs=[master], ref_roles=["identity reference of the person"], aspect="9:16", size="1k",
                    seed=100 + attempt + len(sheet) * 7))[0]
            sim = identity.image_similarity(out, prof)
            if sim is not None and sim >= identity.FLOOR + 0.05:
                sheet.append(out.id)
                actor.sheet_views[out.id] = name
                break
    actor.sheet_asset_ids = sheet
    look.reference_asset_ids = [master.id]
    actor.looks = [look]
    refs = [master] + [ctx().db.get_asset(i) for i in sheet]
    actor.identity = identity.build_profile(refs)
    actor.identity = identity.add_impostors(actor.identity, _impostors(actor, img, look, pid, n_twins))
    actor.voices[locale] = VoiceProfile(locale=locale, provider="gemini", voice_name=voice_id or default_voice(locale, gender),
                                        style_prompt=voice_hint or "natural, casual, close to the phone microphone")
    actor.persona = persona or actor.persona
    actor.model_versions = {"image": getattr(img, "model", img.name), "identity": actor.identity.embedding_model}
    if voice_hint:
        actor.model_versions["voice_hint"] = voice_hint
    ctx().db.put(actor)
    return actor


def _impostors(actor: Actor, img, look, pid: str | None, n_twins: int) -> list[Asset]:
    """Caras con las que NO debe confundirse: maestros de los demás actores (gratis) + «gemelas» generadas con la
    MISMA descripción y sin referencias (~0,067 $ cada una). El generador converge a caras casi iguales para el mismo
    texto; sin ellas el control de identidad no distingue a la actriz de una parecida."""
    out: list[Asset] = []
    for other in ctx().db.list(Actor):
        if other.id != actor.id and other.master_portrait_id:
            try:
                out.append(ctx().db.get_asset(other.master_portrait_id))
            except KeyError:
                pass
    for k in range(max(0, n_twins)):
        try:
            with scope(pid, f"impostor_{k}"):
                out += img.generate(ImageRequest(
                    prompt=(f"Vertical smartphone selfie photo of {actor.appearance}, wearing {look.wardrobe}, in an ordinary home. "
                            f"{NO_PHONE} Realistic skin texture, natural non-retouched look, no text."),
                    aspect="9:16", size="1k", seed=9000 + k))
        except ProviderError as e:
            if e.billing:
                break
            continue
    return out


def default_voice(locale: str, gender: str = "female") -> str:
    """Voz de catálogo por defecto (castellano real para es-ES)."""
    if locale.startswith("es-ES"):
        return "es-es-commercial-3" if gender == "female" else "es-es-commercial-1"
    if locale.startswith("es"):
        return "Aoede" if gender == "female" else "Puck"
    return "Aoede" if gender == "female" else "Charon"


def voice_hint(actor: Actor, locale: str) -> str:
    """Timbre del actor + acento del idioma pedido (en alemán no puede «sonar de Madrid»)."""
    import re

    from ..locales import LOCALE_NAMES

    v = actor.voices.get(locale)
    hint = (v.style_prompt if v else "") or actor.model_versions.get("voice_hint", "")
    if v is None and hint:
        hint = re.sub(r"\s+from\s+[A-ZÁÉÍÓÚ]\w*(?:\s+[A-ZÁÉÍÓÚ]\w*)*", "", hint)  # quita el origen («from Madrid»)
        hint = f"{hint}, speaking as a native {LOCALE_NAMES.get(locale, locale)} speaker"
    return hint


def best_refs_for(actor: Actor, framing: str = "", n: int = 3) -> list[Asset]:
    """Elige referencias de identidad según el encuadre pedido (el retrato maestro siempre primero)."""
    ids = [actor.master_portrait_id] if actor.master_portrait_id else []
    views = actor.sheet_views or {a: v for a, (v, _) in zip(actor.sheet_asset_ids, SHEET_VIEWS)}
    f = framing.lower()
    if any(k in f for k in ("medium", "medio", "waist", "cintura")):
        want = ("medium_talking", "front_neutral")
    elif any(k in f for k in ("profile", "perfil", "side", "lado", "turn", "gira", "three-quarter", "3/4")):
        want = ("three_quarter_left", "three_quarter_right")
    elif any(k in f for k in ("smil", "sonr", "laugh", "rí", "ríe")):
        want = ("smile_teeth", "front_neutral")
    else:
        # por diversidad: el maestro ya es frontal (la vista frontal da 0,95 con él → hueco desperdiciado)
        want = ("three_quarter_left", "three_quarter_right", "smile_teeth", "front_neutral")
    pool = sorted(actor.sheet_asset_ids, key=lambda i: want.index(views[i]) if views.get(i) in want else len(want))
    ids += pool
    out = []
    for i in ids[:n]:
        try:
            out.append(ctx().db.get_asset(i))
        except KeyError:
            continue
    return out
