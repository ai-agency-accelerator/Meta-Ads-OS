"""Anuncio «estilo Flow»: varios planos por generación de vídeo, con la presentadora y el producto como ingredientes.

Por qué existe: el flujo clásico del motor fuerza al modelo de vídeo a un único plano continuo y deja el producto fuera de
la escena (packshot pegado encima). El estilo Flow hace lo contrario: la persona USA el producto en su contexto real
(una app en el portátil de su escritorio, un cepillo en el baño, una crema en el tocador) y cada generación trae varios
planos con la misma cara y la misma voz. Todo lo concreto (producto, lugar, luz, vestuario, guion y planos) sale de una
**receta JSON**; el ejemplo `examples/flow_receta_nimbo.json` muestra todos los campos.

Uso (desde la raíz de Meta Ads OS; el subcomando va SIEMPRE justo después del nombre del script):

  uv run --project modulos/motor-ia python modulos/motor-ia/scripts/flow_style.py <subcomando> --receta <receta.json> …

Gratis:
  validar                       → comprueba la receta y que existan la marca, el producto y el actor
  plan                          → prompts de cada paso y coste estimado, sin llamar a nadie
  setup                         → crea el proyecto del motor (solo base de datos local)
  check <asset>                 → transcripción, texto incrustado e identidad de una toma (local)
De pago (el hook `motor_guard` pide confirmación; con MOTOR_MOCK=1 o --simular se usan proveedores simulados, 0 $):
  keyframe [--n 2]              → candidatos de primer fotograma (presentadora usando el producto)
  gen_a <asset> [--toma 0]      → generación A (primeros planos) desde el fotograma elegido
  gen_b <asset> [--toma 0]      → extensión B (planos siguientes), misma voz e identidad
  stills [--planos a,b] [--n 2] → planos de producto limpios (si el vídeo deformó el producto)
  animate <plano> <asset> [--dur 4] → anima un plano de producto (imagen → vídeo)

El estado (fotogramas, tomas, planos) se guarda en `data/work/flow/<nombre_de_la_receta>/state.json`; la caché del motor
evita pagar dos veces la misma llamada.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

IMAGE_MODEL = "gemini-3-pro-image"
OMNI_MODEL = "gemini-omni-1.1-flash"
VEO_MODEL = "veo-3.1-fast-generate-preview"
NO_TEXT = "No subtitles, no captions and no on-screen text of any kind (the editor adds them later)."
REQUIRED = ("nombre", "marca_id", "producto_id", "actor", "producto_en", "ubicacion_en", "luz_en", "vestuario_en",
            "voz_en", "segmentos", "fotograma_clave", "generaciones")


REF_PRODUCTO = re.compile(r"producto:(captura|packshot|grabacion):(\d+)")
REF_FIELDS = {"captura": "screenshot_asset_ids", "packshot": "packshot_asset_ids", "grabacion": "screen_recording_asset_ids"}


class RecetaError(ValueError):
    pass


# ───────────────────────────── receta ─────────────────────────────


def load_receta(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise RecetaError(f"no encuentro la receta {p}")
    try:
        r = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RecetaError(f"la receta no es JSON válido (línea {e.lineno}, columna {e.colno}): {e.msg}") from None
    if not isinstance(r, dict):
        raise RecetaError("la receta debe ser un objeto JSON")
    r["_dir"] = str(p.parent)
    return r


def validate_receta(r: dict[str, Any]) -> list[str]:
    """Lista de problemas (vacía = receta válida). Mensajes pensados para arreglarlos sin leer el código."""
    errs: list[str] = []
    for k in REQUIRED:
        if k not in r or r[k] in ("", None, [], {}):
            errs.append(f"falta «{k}»")
    if errs:
        return errs
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", str(r["nombre"])):
        errs.append("«nombre» debe ir en minúsculas con guiones (se usa como carpeta de estado)")
    segs = r["segmentos"]
    if not isinstance(segs, list) or not segs:
        return errs + ["«segmentos» debe ser una lista con al menos el hook"]
    for i, s in enumerate(segs):
        if not isinstance(s, dict) or not str(s.get("texto", "")).strip():
            errs.append(f"segmento {i}: falta «texto»")
            continue
        if s.get("rol") not in ("hook", "problem", "demo", "solution", "proof", "cta", "body"):
            errs.append(f"segmento {i}: «rol» debe ser hook, problem, demo, solution, proof, body o cta")
    if segs and isinstance(segs[0], dict) and segs[0].get("rol") != "hook":
        errs.append("el primer segmento debe tener rol «hook»")
    if segs and isinstance(segs[0], dict) and len(str(segs[0].get("texto", "")).split()) > 9:
        errs.append("el hook tiene más de 9 palabras: acórtalo (regla del motor)")
    for i, s in enumerate(segs):
        if isinstance(s, dict) and len(str(s.get("texto", "")).split()) > 17:
            errs.append(f"segmento {i}: más de 17 palabras seguidas; pártelo en dos")
        if isinstance(s, dict) and re.search(r"\blo he probado\b|\bllevo (?:\w+ )?(?:semanas|meses)\b|\bme ha cambiado\b",
                                             str(s.get("texto", "")), re.I):
            errs.append(f"segmento {i}: testimonio en primera persona en boca de una persona sintética (prohibido)")
    refs = r.get("referencias_producto") or {}
    if not isinstance(refs, dict):
        errs.append("«referencias_producto» debe ser un objeto {nombre: ruta}")
        refs = {}
    for name, rel in refs.items():
        if str(rel).startswith("producto:"):
            if not REF_PRODUCTO.fullmatch(str(rel)):
                errs.append(f"referencia de producto «{name}»: «{rel}» no vale (usa producto:captura:0, "
                            "producto:packshot:0 o producto:grabacion:0)")
        elif not (Path(r["_dir"]) / rel).is_file():
            errs.append(f"referencia de producto «{name}»: no existe {rel} (rutas relativas a la receta)")
    kf = r["fotograma_clave"]
    if not str(kf.get("escena_en", "")).strip():
        errs.append("fotograma_clave: falta «escena_en» (qué se ve en el primer fotograma)")
    for name in kf.get("referencias", []):
        if name not in refs:
            errs.append(f"fotograma_clave: la referencia «{name}» no está en referencias_producto")
    spoken: set[int] = set()
    gens = r["generaciones"]
    if "a" not in gens:
        errs.append("generaciones: falta «a» (la primera generación)")
    for g, spec in gens.items():
        if g not in ("a", "b"):
            errs.append(f"generaciones: «{g}» no vale (solo «a» y «b»)")
            continue
        planos = spec.get("planos") or []
        if not planos:
            errs.append(f"generación {g}: sin «planos»")
        dur = spec.get("duracion_s", 10)
        if not isinstance(dur, (int, float)) or not 3 <= dur <= 10:
            errs.append(f"generación {g}: «duracion_s» entre 3 y 10")
        for k, pl in enumerate(planos):
            if not str(pl.get("accion_en", "")).strip():
                errs.append(f"generación {g}, plano {k}: falta «accion_en»")
            d = pl.get("dice")
            if isinstance(d, int):
                if not 0 <= d < len(segs):
                    errs.append(f"generación {g}, plano {k}: «dice» apunta al segmento {d}, que no existe")
                spoken.add(d)
            elif d not in (None, "") and not isinstance(d, str):
                errs.append(f"generación {g}, plano {k}: «dice» es el índice de un segmento o un texto literal")
        for name in spec.get("referencias", []):
            if name not in refs:
                errs.append(f"generación {g}: la referencia «{name}» no está en referencias_producto")
    literal = " ".join(str(pl.get("dice")) for spec in gens.values() if isinstance(spec, dict)
                       for pl in spec.get("planos", []) if isinstance(pl.get("dice"), str))
    for i, s in enumerate(segs):
        if i not in spoken and isinstance(s, dict) and str(s.get("texto", ""))[:12] not in literal:
            errs.append(f"el segmento {i} («{str(s.get('texto', ''))[:30]}…») no lo dice ningún plano")
    for name, spec in (r.get("planos_producto") or {}).items():
        if not str(spec.get("prompt_en", "")).strip():
            errs.append(f"plano de producto «{name}»: falta «prompt_en»")
        for ref in spec.get("referencias", []):
            if ref not in refs:
                errs.append(f"plano de producto «{name}»: la referencia «{ref}» no está en referencias_producto")
    for name in (r.get("movimientos") or {}):
        if name not in (r.get("planos_producto") or {}):
            errs.append(f"movimiento «{name}»: no hay plano de producto con ese nombre")
    return errs


def require_valid(r: dict[str, Any]) -> None:
    errs = validate_receta(r)
    if errs:
        raise RecetaError("receta no válida:\n  - " + "\n  - ".join(errs))


# ───────────────────────────── prompts (puros, sin red) ─────────────────────────────


def _line(r: dict[str, Any], pl: dict[str, Any]) -> str:
    d = pl.get("dice")
    return r["segmentos"][d]["texto"] if isinstance(d, int) else str(d or "")


def _shot(r: dict[str, Any], pl: dict[str, Any], first: bool) -> str:
    accent = r.get("acento_en", "Spanish from Spain")
    text = pl["accion_en"].strip().rstrip(".")
    line = _line(r, pl)
    said = f", and says in {accent}: «{line}»" if line else ""
    return (f"It starts exactly on Image1: {text}{said}. " if first else f"Quick cut: {text}{said}. ")


def keyframe_prompt(r: dict[str, Any], appearance: str) -> str:
    kf = r["fotograma_clave"]
    return (f"{kf['escena_en'].strip().rstrip('.')}. She is the same person as in the identity references: {appearance}. "
            f"The product is identical to the product references: {r['producto_en']}. "
            f"She wears {r['vestuario_en']}. Hair: {r.get('pelo_en', 'natural, slightly imperfect')}. "
            f"Location: {r['ubicacion_en']}. Lighting: {r['luz_en']}. Real smartphone photo: natural skin texture with pores, "
            "slight wide-angle perspective, unretouched, not a photoshoot. No text, no logos, no watermark.")


def gen_prompt(r: dict[str, Any], which: str, n_images: int) -> str:
    spec = r["generaciones"][which]
    dur = int(spec.get("duracion_s", 10))
    shots = "".join(_shot(r, pl, which == "a" and k == 0) for k, pl in enumerate(spec["planos"]))
    tail = (f"Voice: {r['voz_en']}, natural pace with real pauses and breathing. Only she speaks. Realistic facial "
            "expressions and human movement, real hands with five fingers. No subtitles, text overlays, logos, music, or "
            "cinematic style.")
    if which == "a":
        refs = " ".join(f"<IMAGE_REF_{i}>@Image{i + 2}" for i in range(max(0, n_images - 1)))
        head = (f"[# Sources <FIRST_FRAME>@Image1] [# References {refs}] " if refs else "[# Sources <FIRST_FRAME>@Image1] ")
        return (head + f"Fast-paced vertical 9:16 UGC advertisement, {dur} seconds. Smartphone-style handheld camera, "
                "authentic creator content. Visual changes every 1 to 2 seconds. Image2 is the same woman: keep her face, "
                "age, hair and skin identical in every shot. The other references show the exact product, "
                f"{r['producto_en']}; keep it identical whenever it appears, at realistic scale. " + shots + tail)
    cont = r["generaciones"]["b"].get("continuidad_en", "")
    return (f"Fast-paced direct continuation of this video, {dur} more seconds: the same woman, the same voice, the same "
            f"place and the same product ({r['producto_en']}). Visual changes every 1 to 2 seconds. Strict continuity with "
            f"the previous shots: exactly the same face, hairstyle and clothes ({r['vestuario_en']}). {cont} " + shots + tail)


def still_prompt(r: dict[str, Any], name: str) -> str:
    spec = r["planos_producto"][name]
    exact = r.get("producto_exacto_en") or r["producto_en"]
    return (f"{spec['prompt_en'].strip()} The product is {exact}. Identical to the product references. Real high-end product "
            f"photography shot on a phone-style camera in the same place ({r['ubicacion_en']}): {r['luz_en']}, true-to-life "
            "colors, sharp focus, realistic materials. No text, no logos, no watermark, no people except where stated.")


def estimate(r: dict[str, Any], n_keyframes: int = 2) -> dict[str, float]:
    """Coste estimado por paso con la tabla de precios del motor (USD; precios de la fecha de `prices.yaml`)."""
    from motor.costs import price

    img = price("gemini", IMAGE_MODEL, "2k", 0.134)
    omni = price("gemini", OMNI_MODEL, "720p", 0.101)
    veo = price("gemini", VEO_MODEL, "1080p", 0.12)
    est = {"keyframe": round(img * n_keyframes, 3)}
    for g, spec in r["generaciones"].items():
        est[f"gen_{g}"] = round(omni * float(spec.get("duracion_s", 10)), 3)
    n_st = len(r.get("planos_producto") or {})
    if n_st:
        est["stills"] = round(img * 2 * n_st, 3)
    for name in (r.get("movimientos") or {}):
        est[f"animate:{name}"] = round(veo * 4, 3)
    est["total"] = round(sum(est.values()), 3)
    return est


# ───────────────────────────── estado y contexto del motor ─────────────────────────────


def _simulated() -> bool:
    from motor.store import ctx

    return ctx().settings.mock


def _state_path(r: dict[str, Any]) -> Path:
    from motor.store import ctx

    d = ctx().settings.work_dir / "flow" / r["nombre"]
    d.mkdir(parents=True, exist_ok=True)
    return d / "state.json"


def _state(r: dict[str, Any]) -> dict[str, Any]:
    p = _state_path(r)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _save_state(r: dict[str, Any], s: dict[str, Any]) -> None:
    _state_path(r).write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")


def _entities(r: dict[str, Any]):
    from motor.models import Actor, BrandKit, Product
    from motor.store import ctx

    db = ctx().db
    try:
        brand, product = db.get(BrandKit, r["marca_id"]), db.get(Product, r["producto_id"])
        actor = db.find(Actor, r["actor"])
    except KeyError as e:
        raise RecetaError(f"no existe en el motor: {e}. Mira los ids con `motor brand list`, `motor product list` "
                          "y `motor actor list`") from None
    return brand, product, actor


def _refs(r: dict[str, Any]) -> dict[str, str]:
    from motor.store import ctx

    s = _state(r)
    want = r.get("referencias_producto") or {}
    have = s.get("refs", {})
    if set(have) != set(want):
        _brand, product, _actor = _entities(r)
        have = {}
        for k, v in want.items():
            m = REF_PRODUCTO.fullmatch(str(v))
            if m:  # un asset que el producto ya tiene en el motor (capturas reales de la app, packshots…)
                ids = getattr(product, REF_FIELDS[m.group(1)])
                if int(m.group(2)) >= len(ids):
                    raise RecetaError(f"referencia «{k}»: el producto solo tiene {len(ids)} {m.group(1)}(s)")
                have[k] = ids[int(m.group(2))]
            else:
                have[k] = ctx().assets.ingest(Path(r["_dir"]) / v, source="product:sheet").id
        s["refs"] = have
        _save_state(r, s)
    return have


def _image_provider():
    from motor.providers.mock import MockImage

    if _simulated():
        return MockImage()
    from motor.providers.gemini import GeminiImage

    return GeminiImage(IMAGE_MODEL)


# ───────────────────────────── pasos ─────────────────────────────


def cmd_setup(r: dict[str, Any]) -> str:
    from motor.models import Brief, ContinuityBible, Look, Project, Script, ScriptSegment, Shot
    from motor.store import ctx

    db = ctx().db
    brand, product, actor = _entities(r)
    look = next((lk for lk in actor.looks if lk.wardrobe == r["vestuario_en"]), None)
    if look is None:
        look = Look(name=f"{r['nombre']} · vestuario", wardrobe=r["vestuario_en"], hair_makeup=r.get("pelo_en", ""),
                    reference_asset_ids=[actor.master_portrait_id] if actor.master_portrait_id else [])
        actor.looks.append(look)
        db.put(actor)
    segs = [ScriptSegment(role=s["rol"], text=s["texto"], on_screen_text=s.get("en_pantalla", ""), speaker=actor.id,  # type: ignore[arg-type]
                          est_duration=round(len(s["texto"].split()) / 2.5, 2)) for s in r["segmentos"]]
    locale = r.get("idioma", "es-ES")
    script = Script(locale=locale, title=r.get("titulo", r["nombre"]), segments=segs, cta=brand.ctas[0] if brand.ctas else "")
    bible = ContinuityBible(actor_id=actor.id, look_id=look.id, location=r["ubicacion_en"], lighting=r["luz_en"],
                            time_of_day=r.get("momento_en", "day"), props=[product.name])
    total = sum(float(g.get("duracion_s", 10)) for g in r["generaciones"].values())
    talk = Shot(index=0, shot_type="talking_head", segment_ids=[s.id for s in segs], dialogue=" ".join(s.text for s in segs),
                duration=total, camera="selfie_handheld", description="multiplano (estilo Flow)", location=r["ubicacion_en"],
                look_id=look.id, actor_id=actor.id, uses_product=True, seed=int(r.get("semilla", 4242)))
    card = Shot(index=1, shot_type="graphic_card", duration=1.6, description="tarjeta final CTA")
    brief = Brief(brand_id=brand.id, product_id=product.id, objective=r.get("objetivo", "conversión"), locale=locale,
                  duration_s=total, platform=r.get("plataforma", "reels"), actor_ids=[actor.id],
                  audience=r.get("audiencia", ""), key_messages=[s.text for s in segs[1:3]])
    p = Project(name=f"{r.get('titulo', r['nombre'])} (estilo Flow)", brief=brief, script=script, continuity=bible,
                shots=[talk, card], variant_spec={"talk_mode": "native", "source": "flow_style", "receta": r["nombre"],
                                                  "hook_product_open": False})
    p.log.append("estilo Flow: producto en uso dentro de la escena, varios planos por generación de vídeo; sin packshot pegado")
    db.put(p)
    s = _state(r)
    s["project"] = p.id
    _save_state(r, s)
    return p.id


def _project(r: dict[str, Any]):
    from motor.models import Project
    from motor.store import ctx

    pid = _state(r).get("project")
    if not pid:
        raise RecetaError("primero ejecuta `setup` con esta receta")
    return ctx().db.get(Project, pid)


def cmd_keyframe(r: dict[str, Any], n: int = 2) -> list[str]:
    from motor.costs import scope
    from motor.pipeline.actors import best_refs_for
    from motor.providers.base import ImageRequest
    from motor.store import ctx

    pr = _refs(r)
    db = ctx().db
    _brand, _product, actor = _entities(r)
    p = _project(r)
    ids = best_refs_for(actor, "smiling selfie", n=2)
    prod = [db.get_asset(pr[k]) for k in r["fotograma_clave"].get("referencias", [])]
    roles = [f"identity reference of {actor.handle} — the same woman; keep face, age, features, skin and hair identical"] * len(ids)
    roles += ["exact product reference — keep the product's shape, details and colors identical"] * len(prod)
    req = ImageRequest(prompt=keyframe_prompt(r, actor.appearance), refs=ids + prod, ref_roles=roles, aspect="9:16",
                       size="2k", seed=int(r.get("semilla", 4242)), n=n)
    with scope(p.id, p.shots[0].id):
        cands = _image_provider().generate(req)
    s = _state(r)
    s["keyframes"] = [c.id for c in cands]
    _save_state(r, s)
    return [c.id for c in cands]


def _video(r: dict[str, Any], which: str, base_id: str, take: int) -> str:
    from motor.costs import scope
    from motor.providers.base import VideoRequest
    from motor.store import ctx

    db = ctx().db
    _brand, _product, actor = _entities(r)
    p = _project(r)
    spec = r["generaciones"][which]
    dur = int(spec.get("duracion_s", 10))
    base = db.get_asset(base_id)
    pr = _refs(r)
    if which == "a":
        imgs = [base] + ([db.get_asset(actor.master_portrait_id)] if actor.master_portrait_id else [])
        imgs += [db.get_asset(pr[k]) for k in spec.get("referencias", [])]
    else:
        imgs = []
    prompt = gen_prompt(r, which, len(imgs))
    with scope(p.id, p.shots[0].id):
        if _simulated():
            from motor.providers.mock import MockVideo

            a = MockVideo().generate(VideoRequest(prompt=f"flow {which} {take} " + prompt[:80],
                                                  first_frame=base if which == "a" else None, duration=dur, aspect="9:16"))
        else:
            from motor.providers.gemini import GeminiOmni, _b64_image

            om = GeminiOmni(OMNI_MODEL)
            if which == "a":
                a = om._call([_b64_image(i) for i in imgs], prompt, res="720p", aspect="9:16", duration=dur, task="",
                             key_parts=tuple(i.id for i in imgs) + (take,))
            else:
                a = om._call([], prompt, res="720p", aspect="9:16", duration=dur, task="extend",
                             previous_id=(base.meta or {}).get("interaction_id"), key_parts=(base_id, take))
    s = _state(r)
    s.setdefault(f"gen_{which}", []).append(a.id)
    _save_state(r, s)
    return a.id


def cmd_stills(r: dict[str, Any], which: str = "", n: int = 2) -> dict[str, list[str]]:
    from motor.costs import scope
    from motor.providers.base import ImageRequest
    from motor.store import ctx

    planos = r.get("planos_producto") or {}
    if not planos:
        raise RecetaError("la receta no define «planos_producto»")
    names = [x.strip() for x in which.split(",") if x.strip()] or list(planos)
    unknown = [x for x in names if x not in planos]
    if unknown:
        raise RecetaError(f"planos de producto desconocidos: {', '.join(unknown)} (hay: {', '.join(planos)})")
    pr = _refs(r)
    s = _state(r)
    db = ctx().db
    p = _project(r)
    room = db.get_asset(s["keyframes"][0]) if s.get("keyframes") else None
    out = s.setdefault("stills", {})
    for name in names:
        spec = planos[name]
        refs = [db.get_asset(pr[k]) for k in spec.get("referencias", [])]
        roles = ["exact product reference — reproduce the product's shape, details and colors exactly"] * len(refs)
        if room is not None and spec.get("con_escena", True):
            refs.append(room)
            roles.append("place and light reference only (same place and light; do not include the person)")
        req = ImageRequest(prompt=still_prompt(r, name), refs=refs, ref_roles=roles, aspect="9:16", size="2k",
                           seed=int(r.get("semilla", 4242)) + 1, n=n)
        with scope(p.id, p.shots[0].id):
            cands = _image_provider().generate(req)
        out[name] = [c.id for c in cands]
        _save_state(r, s)
    return {k: out[k] for k in names}


def cmd_animate(r: dict[str, Any], name: str, still_id: str, dur: int = 4) -> str:
    from motor.costs import scope
    from motor.providers.base import VideoRequest
    from motor.store import ctx

    moves = r.get("movimientos") or {}
    if name not in moves:
        raise RecetaError(f"no hay movimiento «{name}» en la receta (hay: {', '.join(moves) or 'ninguno'})")
    p = _project(r)
    req = VideoRequest(prompt=moves[name], first_frame=ctx().db.get_asset(still_id), duration=dur, aspect="9:16",
                       resolution="1080p", seed=99)
    with scope(p.id, p.shots[0].id):
        if _simulated():
            from motor.providers.mock import MockVideo

            a = MockVideo().generate(req)
        else:
            from motor.providers.gemini import GeminiVeo

            a = GeminiVeo(VEO_MODEL).generate(req)
    s = _state(r)
    s.setdefault("clips", {})[name] = a.id
    _save_state(r, s)
    return a.id


def cmd_check(r: dict[str, Any], asset_id: str, upto: int = 2) -> dict[str, Any]:
    from motor.providers import registry
    from motor.providers.local_asr import cer_in
    from motor.store import ctx

    db = ctx().db
    a = db.get_asset(asset_id)
    _brand, _product, actor = _entities(r)
    locale = r.get("idioma", "es-ES")
    expected = " ".join(s["texto"] for s in r["segmentos"][:upto])
    out: dict[str, Any] = {"dur": a.duration}
    tr = registry.transcriber()
    try:
        if hasattr(tr, "transcribe"):
            heard = tr.transcribe(a, locale)[0]
        else:  # transcriptor simulado: no «oye» nada, solo reparte el texto esperado
            heard = " ".join(w.text for w in tr.words(a, locale, text_hint=expected))
        out["oido"] = heard
        out["cer"] = round(cer_in(heard, expected), 3)
    except Exception as e:  # noqa: BLE001
        out["oido"] = f"sin transcripción ({type(e).__name__})"
    try:
        from motor.qa import visual

        txt = visual.burned_text(ctx().assets.abspath(a), start=0, dur=a.duration or 10, tag=f"flow_{asset_id[:8]}", n=8,
                                 expected=" ".join(s["texto"] for s in r["segmentos"]))
        out["texto_incrustado"] = txt.get("burned")
    except Exception as e:  # noqa: BLE001
        out["texto_incrustado"] = f"sin OCR ({type(e).__name__})"
    try:
        from motor.pipeline import identity

        idr = identity.video_identity(a, actor.identity, fps=2)
        out["identidad"] = {k: idr.get(k) for k in ("median", "min", "passed", "twin_risk")}
    except Exception as e:  # noqa: BLE001
        out["identidad"] = f"sin identidad ({type(e).__name__}: ejecuta `motor setup`)"
    return out


def cmd_plan(r: dict[str, Any]) -> dict[str, Any]:
    appearance = "<aspecto del actor guardado en el motor>"
    plan = {"keyframe": keyframe_prompt(r, appearance)}
    for g in r["generaciones"]:
        plan[f"gen_{g}"] = gen_prompt(r, g, 2 + len(r["generaciones"][g].get("referencias", [])) if g == "a" else 0)
    for name in (r.get("planos_producto") or {}):
        plan[f"still:{name}"] = still_prompt(r, name)
    for name, prompt in (r.get("movimientos") or {}).items():
        plan[f"animate:{name}"] = prompt
    return {"prompts": plan, "coste_estimado_usd": estimate(r)}


# ───────────────────────────── CLI ─────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="flow_style.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name: str, help_: str) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("--receta", required=True, help="ruta a la receta JSON")
        sp.add_argument("--simular", action="store_true", help="proveedores simulados (equivale a MOTOR_MOCK=1; 0 $)")
        return sp

    add("validar", "comprueba la receta (gratis)")
    add("plan", "prompts y coste estimado, sin llamar a nadie (gratis)")
    add("setup", "crea el proyecto del motor (gratis)")
    add("keyframe", "candidatos de primer fotograma (de pago)").add_argument("--n", type=int, default=2)
    for g in ("gen_a", "gen_b"):
        sp = add(g, f"generación {g[-1].upper()} (de pago)")
        sp.add_argument("asset", help="fotograma elegido (gen_a) o toma base a extender (gen_b)")
        sp.add_argument("--toma", type=int, default=0, help="número de toma (cambia la caché para repetir)")
    sp = add("stills", "planos de producto limpios (de pago)")
    sp.add_argument("--planos", default="", help="nombres separados por comas (por defecto, todos)")
    sp.add_argument("--n", type=int, default=2)
    sp = add("animate", "anima un plano de producto (de pago)")
    sp.add_argument("plano")
    sp.add_argument("asset")
    sp.add_argument("--dur", type=int, default=4)
    sp = add("check", "revisa una toma (gratis, local)")
    sp.add_argument("asset")
    sp.add_argument("--hasta", type=int, default=2, help="segmentos esperados en la toma")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    if a.simular:
        os.environ["MOTOR_MOCK"] = "1"
        from motor import config, store
        from motor.providers import registry

        config.reset_settings()
        store.set_ctx(None)
        registry.reset()
    try:
        r = load_receta(a.receta)
        if a.cmd == "validar":
            errs = validate_receta(r)
            print(json.dumps({"valida": not errs, "problemas": errs}, ensure_ascii=False, indent=1))
            if not errs:
                _entities(r)
            return 0 if not errs else 1
        require_valid(r)
        if a.cmd == "plan":
            res: Any = cmd_plan(r)
        elif a.cmd == "setup":
            res = {"proyecto": cmd_setup(r)}
        elif a.cmd == "keyframe":
            res = {"fotogramas": cmd_keyframe(r, a.n)}
        elif a.cmd in ("gen_a", "gen_b"):
            res = {"toma": _video(r, a.cmd[-1], a.asset, a.toma)}
        elif a.cmd == "stills":
            res = cmd_stills(r, a.planos, a.n)
        elif a.cmd == "animate":
            res = {"clip": cmd_animate(r, a.plano, a.asset, a.dur)}
        else:
            res = cmd_check(r, a.asset, a.hasta)
        if a.cmd not in ("plan", "check"):
            from motor.store import ctx

            res["simulado"] = ctx().settings.mock
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return 0
    except RecetaError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
