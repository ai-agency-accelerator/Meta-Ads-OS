"""Compilador de prompts: convierte la intención del plano (estructurada) en prompts calibrados por modelo.

Inspirado en Higgsfield Cinema Studio: la UI/plan habla en presets («selfie en mano», «plano medio»),
y aquí se traducen a tokens probados para cada modelo. Objetivo: estética de móvil real, no de cine.
"""

from __future__ import annotations

from ..models import Actor, ContinuityBible, Look, Product, Shot

CAMERA_PRESETS = {
    "selfie_handheld": ("vertical selfie, one arm extended toward the lens, eye level; her other hand rests on the counter or "
                        "gestures naturally and is empty",
                        "handheld selfie video with natural micro hand shake, one arm extended toward the lens; the free hand "
                        "is empty and gestures naturally"),
    "handheld_medium": ("vertical smartphone photo, medium shot from chest up, phone on a shelf or held by a friend",
                        "handheld smartphone video, medium shot, gentle natural sway"),
    "handheld_close": ("vertical smartphone close-up, phone camera close to the subject",
                       "handheld smartphone close-up video, slight natural movement"),
    "static": ("vertical smartphone photo on a small tripod", "static smartphone video on a tripod, no camera movement"),
    "pov": ("first-person POV smartphone photo", "first-person POV handheld smartphone video"),
}

REALISM_IMAGE = (
    "Shot on an iPhone, natural available light, realistic skin texture with visible pores and tiny imperfections, "
    "natural non-retouched look, candid everyday moment, slightly imperfect framing, realistic home environment, "
    "true-to-life colors, no studio lighting, no cinematic color grade, no shallow-depth-of-field exaggeration, "
    "no text, no captions, no watermark, no logos except the real product label."
)

REALISM_VIDEO = (
    "Looks like real footage recorded on a phone by a content creator: natural blinking, subtle breathing, small "
    "unplanned head movements, relaxed natural gestures, slight auto-exposure changes. No camera cuts, no zoom effects, "
    "no subtitles, no on-screen text, no music."
)

NEGATIVE_VIDEO = ("subtitles, captions, on-screen text, watermark, music, cinematic lighting, slow motion, morphing, "
                  "distorted hands, extra fingers, warped face, plastic skin, overly smooth skin, camera cuts")


def _camera(shot: Shot) -> tuple[str, str]:
    key = shot.camera if shot.camera in CAMERA_PRESETS else ("selfie_handheld" if "selfie" in (shot.description or "").lower()
                                                              else "handheld_medium")
    return CAMERA_PRESETS[key]


def look_text(look: Look | None) -> str:
    if not look:
        return ""
    parts = [f"wearing {look.wardrobe}"]
    if look.hair_makeup:
        parts.append(look.hair_makeup)
    if look.accessories:
        parts.append(look.accessories)
    return ", ".join(parts)


def keyframe_prompt(shot: Shot, actor: Actor | None, look: Look | None, bible: ContinuityBible, product: Product | None,
                    *, n_actor_refs: int = 0, has_product_ref: bool = False, has_location_ref: bool = False) -> str:
    cam_img, _ = _camera(shot)
    subject = ""
    if actor:
        subject = (f"The person from the reference images ({actor.appearance}). Keep the face, facial features, age, skin tone, "
                   f"hair and body proportions exactly identical to the reference images. {look_text(look)}.")
    action = shot.description or ""
    emo = shot.constraints.get("emotion")
    if shot.shot_type in ("talking_head", "reaction") and actor:
        action = (f"{action}. Mid-sentence natural expression ({emo or 'friendly'}), mouth slightly open, looking into the lens"
                  if shot.shot_type == "talking_head" else f"{action}. Genuine reaction expression ({emo or 'surprised'})")
    prod = ""
    if product and shot.uses_product:
        ref = " shown in the product reference image — reproduce its exact shape, colors and label without changing any text" if has_product_ref else ""
        prod = f" The product is {product.name}{ref}."
    where = f"Location: {bible.location}. Lighting: {bible.lighting}, {bible.time_of_day}."
    if has_location_ref:
        where += " Match the room from the location reference image."
    return f"{cam_img}. {subject} {action}.{prod} {where} {REALISM_IMAGE}".replace("..", ".").strip()


def motion_prompt(shot: Shot, actor: Actor | None, look: Look | None, bible: ContinuityBible, product: Product | None) -> str:
    _, cam_vid = _camera(shot)
    who = f"A {actor.appearance}" if actor else "The scene"
    look_s = f" ({look_text(look)})" if look else ""
    act = shot.description or ""
    if shot.shot_type == "talking_head":
        act = f"talks directly to the camera with a {shot.constraints.get('emotion') or 'warm, casual'} tone, {shot.constraints.get('gesture') or 'small natural hand gestures'}"
    elif shot.shot_type == "reaction":
        act = f"silent genuine reaction: {shot.description or 'raises eyebrows, small smile'}; does not speak"
    elif shot.shot_type in ("product_hand",) and product:
        keep = "exact shape, pattern, colors and label text" if product.expected_label_text else "exact shape, pattern and colors"
        act = f"{shot.description}. Handles it slowly and gently; the product keeps its {keep} in every frame"
    elif shot.shot_type == "broll":
        who = "Ambient detail of the location"
        act = shot.description or "subtle natural movement"
    extra = shot.constraints.get("motion_extra")
    act = f"{act}. {extra}" if extra else act
    return (f"{cam_vid}. {who}{look_s} {act}. Location: {bible.location}, {bible.lighting}. {REALISM_VIDEO}").replace("..", ".").strip()
