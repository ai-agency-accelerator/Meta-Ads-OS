"""Generación de escenas: fotogramas clave verificados, A-roll continuo, planos de corte y composición.

  - Fotograma clave: modelo de imagen con referencias (identidad del actor + producto + localización),
    best-of-N filtrado por similitud facial SFace. Es la «preview» barata que fija composición e identidad.
  - A-roll: primer plano hablado desde el fotograma clave; las siguientes frases se generan EXTENDIENDO
    el mismo vídeo (Omni), de modo que voz, identidad, ropa y sala se mantienen en una única toma.
    Cada tramo se valida (ASR vs guion, identidad) y, si falla, se regenera SOLO ese tramo.
  - Cortes: fotograma clave → vídeo sin diálogo; producto/app → composición con píxeles reales.
"""

from __future__ import annotations

import time
from contextlib import nullcontext
from typing import Any

from ..costs import phase, scope
from ..locales import LOCALE_NAMES
from ..models import Actor, Asset, BrandKit, ContinuityBible, Product, Project, Shot
from ..providers import registry
from ..providers.base import ImageRequest, ProviderError, TalkingRequest, VideoRequest
from ..providers.local_asr import cer_in
from ..qa import objects
from ..qa import visual as qa_visual
from ..store import ctx
from . import identity, product as product_mod, prompts
from .actors import best_refs_for, voice_hint

MAX_TAKES = 2  # intentos por plano antes de cambiar de ruta


def _log(p: Project, msg: str) -> None:
    p.log.append(f"{time.strftime('%H:%M:%S')} {msg}")


# ───────────────────────────── Fotogramas clave ─────────────────────────────


def make_keyframe(p: Project, shot: Shot, actor: Actor | None, bible: ContinuityBible, product: Product | None,
                  *, location_ref: Asset | None = None, n: int = 1) -> Asset:
    look = actor.look(shot.look_id) if actor else None
    refs: list[Asset] = []
    roles: list[str] = []
    if actor and shot.shot_type != "broll":
        for a in best_refs_for(actor, shot.description, n=3):
            refs.append(a)
            roles.append(f"identity reference of {actor.handle} (same person)")
    has_product_ref = False
    if product and shot.uses_product and product.packshot_asset_ids:
        refs.append(ctx().db.get_asset(product.packshot_asset_ids[0]))
        roles.append(f"exact product reference: {product.name} (keep shape, colors and label text identical)")
        has_product_ref = True
    if location_ref is not None:
        refs.append(location_ref)
        roles.append("location and lighting reference (same room, same light; do not copy the person's pose)")
    prompt = prompts.keyframe_prompt(shot, actor if shot.shot_type != "broll" else None, look, bible, product,
                                     n_actor_refs=len(refs), has_product_ref=has_product_ref,
                                     has_location_ref=location_ref is not None)
    if shot.shot_type != "broll":
        prompt += " " + "Her free hand is empty, relaxed on the counter or out of frame, unless the action requires it."
    extra = shot.constraints.get("keyframe_extra")
    if extra:
        prompt += " " + extra
    shot.keyframe_prompt = prompt
    img = registry.image("pro" if shot.constraints.get("strong_identity") else "standard")
    with scope(p.id, shot.id):
        cands = img.generate(ImageRequest(prompt=prompt, refs=refs, ref_roles=roles, aspect="9:16", size="1k",
                                          seed=shot.seed + 1000 * shot.revision, n=max(1, n)))
    face_expected = shot.shot_type in ("talking_head", "reaction")
    if actor and face_expected:
        # el «segundo móvil» nace casi siempre en la imagen inicial (selfie): se descarta ANTES de pagar el vídeo.
        # En planos de manos con producto, «algo en la mano» es lo esperado (CLIP lo confundiría con un móvil).
        clean = [c for c in cands if not objects.image_has_phone(ctx().assets.abspath(c)).get("phone")]
        if not clean and not shot.constraints.get("hands_retry"):
            _log(p, f"{shot.id}: el fotograma clave trae un móvil en la mano → regenero con las manos vacías")
            shot.constraints["hands_retry"] = True
            shot.constraints["keyframe_extra"] = "Both of her hands are empty; one rests on the counter, the other gestures naturally."
            shot.revision += 1
            return make_keyframe(p, shot, actor, bible, product, location_ref=location_ref, n=1)
        if clean:
            cands = clean
        else:
            shot.constraints["object_risk"] = True
    if actor and face_expected and actor.identity.centroid:
        # la identidad solo se exige donde debe verse la cara (en planos de manos/POV la cara está fuera a propósito)
        scored = [(identity.image_similarity(c, actor.identity) or 0.0, c) for c in cands]
        scored.sort(key=lambda x: -x[0])
        best_sim, best = scored[0]
        shot.notes.append(f"keyframe identidad={best_sim:.3f} (n={len(cands)})")
        limit = max(identity.FLOOR + 0.05, actor.identity.threshold)
        if best_sim < limit and not shot.constraints.get("strong_identity"):
            # una sola escalada (1 imagen con el modelo pro): como mucho n+1 imágenes por plano
            _log(p, f"{shot.id}: identidad baja en fotograma clave ({best_sim:.2f}) → regenero con referencias reforzadas")
            shot.constraints["strong_identity"] = True
            shot.revision += 1
            return make_keyframe(p, shot, actor, bible, product, location_ref=location_ref, n=1)
        if best_sim < limit:
            shot.constraints["identity_risk"] = round(best_sim, 3)
            _log(p, f"{shot.id}: fotograma clave con identidad dudosa ({best_sim:.2f}) → marcado para revisión")
        return best
    return cands[0]


# ───────────────────────────── A-roll continuo ─────────────────────────────


LINE_CER_MAX = 0.12  # ≈ dos palabras cambiadas en una frase de 17


def _contains_line(asr_text: str, line: str) -> float:
    """Error por caracteres de `line` dentro de la transcripción del tramo (ver local_asr.cer_in)."""
    return cer_in(asr_text, line)


def verify_line(transcriber: Any, clip: Asset, line: str, locale: str) -> tuple[float, str]:
    """¿Se oye `line` en el clip? Devuelve (error, explicación).

    1.ª escucha sin pistas (estricta). Si falla, 2.ª escucha con el texto esperado como contexto: el ASR se equivoca
    sobre todo en frases cortas (el hook va solo en su tramo) y un falso rechazo cuesta una toma de vídeo. Se acepta
    solo si la 2.ª escucha cuadra Y la 1.ª no estaba lejos (frases <40 caracteres: ≤0,45; resto: ≤0,30).
    """
    if not hasattr(transcriber, "transcribe"):
        return 0.0, "sin ASR"
    text, _ = transcriber.transcribe(clip, locale)
    e1 = _contains_line(text, line) if text else 1.0
    if e1 <= LINE_CER_MAX:
        return e1, f"«{text[:80]}»"
    try:
        text2, _ = transcriber.transcribe(clip, locale, hint=line)
    except TypeError:
        return e1, f"«{text[:80]}»"
    e2 = _contains_line(text2, line) if text2 else 1.0
    loose = 0.45 if len("".join(line.split())) < 40 else 0.30
    if e2 <= LINE_CER_MAX and e1 <= loose:
        return e2, f"2.ª escucha guiada (1.ª CER {e1:.2f}: «{text[:60]}»)"
    return e1, f"«{text[:80]}» / guiada «{text2[:60]}»"


def heard_full(transcriber: Any, clip: Asset, locale: str) -> str:
    if not hasattr(transcriber, "transcribe"):
        return ""
    return transcriber.transcribe(clip, locale)[0]


def generate_aroll(p: Project, talking: list[Shot], actor: Actor, bible: ContinuityBible, product: Product | None,
                   *, locale: str, resolution: str = "720p") -> Asset:
    """Genera el A-roll como una única toma continua (primer plano + extensiones encadenadas)."""
    if not talking:
        raise ValueError("no hay planos hablados")
    if p.variant_spec.get("talk_mode") in ("lipsync", "avatar"):
        return generate_aroll_lipsync(p, talking, actor, bible, product, locale=locale)
    talker = registry.talking("native")
    omni = registry.video("omni")
    transcriber = registry.transcriber()
    vh = voice_hint(actor, locale)
    first = talking[0]
    kf = ctx().db.get_asset(first.keyframe_asset_id) if first.keyframe_asset_id else make_keyframe(p, first, actor, bible, product, n=2)
    first.keyframe_asset_id = kf.id
    refs = best_refs_for(actor, first.description, n=2)
    cur: Asset | None = None
    spoken_so_far = ""
    for idx, shot in enumerate(talking):
        chunk = shot.constraints.get("chunk_asset")
        if shot.status == "ready" and chunk:
            cur = ctx().db.get_asset(chunk)  # tramo ya aprobado: se reutiliza (regeneración selectiva)
            spoken_so_far = (spoken_so_far + " " + shot.dialogue).strip()
            continue
        ok = False
        for attempt in range(MAX_TAKES + 1):
            shot.attempts += 1
            # habla medida ≈72–77 % del tramo con /2,4+1,2: el silencio sobrante se pagaba a 0,10 $/s
            dur = min(10.0, max(3.0, len(shot.dialogue.split()) / 2.7 + 0.6))
            motion = prompts.motion_prompt(shot, actor, actor.look(shot.look_id), bible, product)
            try:
                with scope(p.id, shot.id), (phase("retake") if attempt else nullcontext()):
                    expired = cur is not None and shot.constraints.get("extend_expired")
                    if idx == 0 or cur is None or not hasattr(omni, "extend") or expired:
                        if expired and cur is not None:
                            # la interacción previa caducó (≤55 días): toma nueva desde el ÚLTIMO fotograma (la voz puede variar)
                            from ..media import last_frame

                            kf = ctx().assets.ingest(last_frame(ctx().assets.abspath(cur), ctx().work("aroll", p.id) / f"last_{cur.id[:8]}.png"),
                                                     source="frame:last")
                        # la variación entre tomas va en la semilla/clave de caché, no en el texto que ve el modelo
                        cand = talker.generate(TalkingRequest(prompt=motion, portrait=kf, dialogue=shot.dialogue, locale=locale,
                                                              voice_hint=vh, duration=dur, aspect="9:16", resolution=resolution, refs=refs,
                                                              seed=shot.seed + 1000 * shot.revision + attempt))
                    else:
                        lang = LOCALE_NAMES.get(locale, locale)
                        cand = omni.extend(cur, (f"{actor.pronoun} keeps talking to the camera in {lang} with exactly the same voice, same "
                                                 f"framing and same room. {shot.constraints.get('gesture') or ''} "
                                                 f"{actor.pronoun} says exactly: «{shot.dialogue}». Nobody else speaks, no music."),
                                           duration=dur, res=resolution, take=1000 * shot.revision + attempt)
            except ProviderError as e:
                if e.billing:
                    raise
                low = str(e).lower()
                if idx > 0 and any(k in low for k in ("previous_interaction", "not found", "expired", "no longer")):
                    shot.constraints["extend_expired"] = True
                    _log(p, f"{shot.id}: la toma anterior ya no se puede extender (caducada) → toma nueva desde su último fotograma")
                _log(p, f"{shot.id}: error del proveedor ({'moderación' if e.moderation else 'técnico'}): {str(e)[:160]}")
                shot.notes.append(f"error intento {attempt}: {str(e)[:120]}")
                continue
            line_wer, heard = verify_line(transcriber, cand, shot.dialogue, locale)
            id_res = identity.video_identity(cand, actor.identity, fps=1.5)
            prev_d = (cur.duration or 0.0) if (cur is not None and idx > 0 and hasattr(omni, "extend")) else 0.0
            txt = qa_visual.burned_text(ctx().assets.abspath(cand), start=prev_d, dur=max(1.0, (cand.duration or dur) - prev_d),
                                        tag=f"{p.id}_{shot.id}_{attempt}", expected=shot.dialogue)
            shot.notes.append(f"tramo {idx} intento {attempt}: CER={line_wer:.2f} {heard} id_med={id_res.get('median')} "
                              f"id_min={id_res.get('min')} texto={'SÍ ' + str(txt['hits'][:1]) if txt.get('burned') else 'no'}")
            if txt.get("burned"):
                _log(p, f"{shot.id}: el vídeo trae subtítulos/texto incrustado → regenero este tramo")
            # la extensión tiene que CONTINUAR la toma: más larga que la anterior y con todo lo dicho hasta ahora
            # (visto en real: Omni devolvió una toma más corta que se saltaba un tramo entero)
            chain_ok = True
            if prev_d:
                full_err = cer_in(heard_full(transcriber, cand, locale), (spoken_so_far + " " + shot.dialogue).strip())
                chain_ok = (cand.duration or 0) >= prev_d + 1.0 and full_err <= 0.2
                if not chain_ok:
                    _log(p, f"{shot.id}: la extensión no continúa la toma ({cand.duration:.1f}s ≤ {prev_d:.1f}s o le falta diálogo "
                            f"previo, CER {full_err:.2f}) → la repito")
            if line_wer <= LINE_CER_MAX and id_res.get("passed") is not False and not txt.get("burned") and chain_ok:
                cur = cand
                spoken_so_far = (spoken_so_far + " " + shot.dialogue).strip()
                shot.clip_asset_id = cand.id
                shot.constraints["chunk_asset"] = cand.id
                shot.status = "ready"
                ok = True
                break
            _log(p, f"{shot.id}: tramo rechazado (CER {line_wer:.2f}, identidad {id_res.get('median')}) → regenero solo este tramo")
            shot.revision += 1
        if not ok:
            shot.status = "failed"
            raise ProviderError(f"A-roll: el tramo {idx} ({shot.id}) no supera el control tras {MAX_TAKES + 1} intentos")
    assert cur is not None
    if not hasattr(omni, "extend"):
        # proveedor sin extensión: cada tramo es un clip independiente → se unen en un único A-roll
        chunks = [ctx().db.get_asset(s.constraints["chunk_asset"]) for s in talking if s.constraints.get("chunk_asset")]
        if len(chunks) > 1:
            cur = _concat_av(chunks, p.id)
    for s in talking:
        s.clip_asset_id = cur.id  # todos los planos hablados apuntan a la toma completa; el montaje la recorta
    return cur


def generate_aroll_lipsync(p: Project, talking: list[Shot], actor: Actor, bible: ContinuityBible, product: Product | None,
                           *, locale: str) -> Asset:
    """Modo voz PERSISTENTE: la voz TTS fija del actor es el reloj maestro y el vídeo se anima sobre ella (lip-sync).

    Misma voz en todos los anuncios, meses e idiomas del actor (el ID de voz no cambia). Cada tramo es independiente:
    cambiar una frase regenera SOLO ese tramo (≈0,06 $/s con Kling Avatar v2 std), no el resto del A-roll.
    """
    from .actors import default_voice

    tts = registry.tts()
    av = registry.talking("avatar")
    transcriber = registry.transcriber()
    vp = actor.voices.get(locale)
    voice = vp.voice_name if vp else default_voice(locale, actor.gender)
    style = vp.style_prompt if vp else "natural, casual, close to the phone microphone"
    first = talking[0]
    kf = ctx().db.get_asset(first.keyframe_asset_id) if first.keyframe_asset_id else make_keyframe(p, first, actor, bible, product, n=2)
    first.keyframe_asset_id = kf.id
    for idx, shot in enumerate(talking):
        if shot.status == "ready" and shot.constraints.get("chunk_asset"):
            continue
        ok = False
        for attempt in range(MAX_TAKES + 1):
            shot.attempts += 1
            try:
                with scope(p.id, shot.id), (phase("retake") if attempt else nullcontext()):
                    speech = tts.speak(shot.dialogue, voice=voice, locale=locale, style=style)
                    cand = av.generate(TalkingRequest(prompt=prompts.motion_prompt(shot, actor, actor.look(shot.look_id), bible, product),
                                                      portrait=kf, audio=speech.audio, dialogue=shot.dialogue, locale=locale,
                                                      duration=speech.audio.duration or 4.0, seed=shot.seed + 1000 * shot.revision + attempt))
            except ProviderError as e:
                if e.billing:
                    raise
                _log(p, f"{shot.id}: error del proveedor de lip-sync: {str(e)[:160]}")
                continue
            line_err, heard = verify_line(transcriber, cand, shot.dialogue, locale)
            id_res = identity.video_identity(cand, actor.identity, fps=1.5)
            shot.notes.append(f"lipsync tramo {idx} intento {attempt}: CER={line_err:.2f} {heard} id_med={id_res.get('median')}")
            if line_err <= LINE_CER_MAX and id_res.get("passed") is not False:
                shot.constraints["chunk_asset"] = cand.id
                shot.clip_asset_id, shot.status, ok = cand.id, "ready", True
                ctx().db.put(p)
                break
            shot.revision += 1
        if not ok:
            shot.status = "failed"
            raise ProviderError(f"lip-sync: el tramo {idx} ({shot.id}) no supera el control tras {MAX_TAKES + 1} intentos")
    chunks = [ctx().db.get_asset(s.constraints["chunk_asset"]) for s in talking]
    aroll = _concat_av(chunks, p.id) if len(chunks) > 1 else chunks[0]
    for s in talking:
        s.clip_asset_id = aroll.id
    return aroll


def _concat_av(chunks: list[Asset], tag: str) -> Asset:
    from ..media import h264, run

    work = ctx().work("aroll", tag)
    inputs: list = []
    fc = []
    for i, a in enumerate(chunks):
        inputs += ["-i", ctx().assets.abspath(a)]
        fc.append(f"[{i}:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1[v{i}];"
                  f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(chunks))) + f"concat=n={len(chunks)}:v=1:a=1[v][a]")
    out = work / f"aroll_{'_'.join(a.id[:6] for a in chunks)}.mp4"
    run(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", *h264(16),
                  "-c:a", "aac", "-b:a", "192k", out])
    return ctx().assets.ingest(out, source="render:aroll_concat", move=True)


# ───────────────────────────── Planos de corte ─────────────────────────────


def _people_free_plate(p: Project) -> Asset | None:
    """Fotograma clave de un plano de ambiente (sin personas) del mismo proyecto: el mejor fondo para el producto real."""
    for s in p.shots:
        if s.shot_type == "broll" and s.keyframe_asset_id:
            a = ctx().db.get_asset(s.keyframe_asset_id)
            return a.model_copy(update={"meta": {**(a.meta or {}), "people": False}})
    return None


def generate_cutaway(p: Project, shot: Shot, actor: Actor | None, bible: ContinuityBible, product: Product | None,
                     brand: BrandKit | None, *, location_ref: Asset | None = None, resolution: str = "720p") -> Asset:
    r = shot.route
    pipe = r.pipeline if r else "i2v"
    if pipe == "compose.app_phone" and product:
        k = [x.id for x in p.shots if x.route and x.route.pipeline == "compose.app_phone"].index(shot.id)
        clip = product_mod.app_screen_clip(product, shot.duration + 0.4, background=location_ref, brand=brand, tag=shot.id,
                                           focus=shot.description, index=k)
        shot.constraints["screens"] = clip.meta.get("screens", [])  # qué pantallas reales se enseñan (control de afirmaciones)
        shot.clip_asset_id, shot.status = clip.id, "ready"
        return clip
    if pipe == "compose.packshot" and product:
        earlier = [s for s in p.shots if s.shot_type == "product_hero" and s.id != shot.id
                   and (s.constraints.get("opener") or p.shots.index(s) < p.shots.index(shot))]
        framing = "detail" if (earlier or p.variant_spec.get("hook_product_open")) else "full"
        clip = product_mod.packshot_clip(product, shot.duration + 0.4, brand=brand, tag=shot.id,
                                         background=_people_free_plate(p) or location_ref, framing=framing)
        shot.clip_asset_id, shot.status = clip.id, "ready"
        return clip
    if pipe == "compose.cta":
        raise ValueError("las tarjetas CTA se componen en el montaje")
    # imagen → vídeo sin diálogo
    kf = make_keyframe(p, shot, actor if shot.shot_type != "broll" else None, bible, product, location_ref=location_ref,
                       n=2 if shot.shot_type == "product_hand" else 1)
    shot.keyframe_asset_id = kf.id
    motion = prompts.motion_prompt(shot, actor, actor.look(shot.look_id) if actor else None, bible, product)
    models = [(r.model if r else "gemini-omni-1.1-flash")] + [f.get("model", "omni") for f in (r.fallbacks if r else [])]
    last_err: Exception | None = None
    for m in models:
        key = "omni" if "omni" in m else ("veo-lite" if "lite" in m else ("veo-fast" if "fast" in m else m))
        gen = registry.video(key)
        dur = float((r.params or {}).get("duration", min(max(shot.duration + 0.6, 3.0), 6.0)) if r else 4.0)
        refs = best_refs_for(actor, shot.description, n=2) if actor and key == "omni" and shot.shot_type != "broll" else []
        try:
            with scope(p.id, shot.id):
                clip = gen.generate(VideoRequest(prompt=motion, first_frame=kf, refs=refs, duration=dur, aspect="9:16",
                                                 resolution=resolution, audio=False, negative_prompt=prompts.NEGATIVE_VIDEO,
                                                 seed=shot.seed + shot.revision))
            shot.clip_asset_id, shot.status = clip.id, "ready"
            shot.attempts += 1
            return clip
        except ProviderError as e:
            if e.billing and all(registry.provider_of(x) == registry.provider_of(m) for x in models):
                raise
            last_err = e
            shot.notes.append(f"{m} falló: {str(e)[:120]} → respaldo")
            _log(p, f"{shot.id}: {m} falló ({str(e)[:100]}) → pruebo respaldo")
            continue
    shot.status = "failed"
    raise ProviderError(f"{shot.id}: todas las rutas fallaron: {last_err}")


def summary(shots: list[Shot]) -> list[dict[str, Any]]:
    return [{"id": s.id, "type": s.shot_type, "status": s.status, "route": s.route.pipeline if s.route else None,
             "model": s.route.model if s.route else None, "attempts": s.attempts, "notes": s.notes[-2:]} for s in shots]
