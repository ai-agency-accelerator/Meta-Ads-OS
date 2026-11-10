"""Montaje: convierte el estado del proyecto en una Timeline no destructiva.

Gramática UGC (investigación de edición automática):
  - el A-roll se recorta por palabras (sin silencios al inicio/final) y se trocea por segmento con
    punch-ins alternos → jump cuts naturales sin cambiar de toma;
  - los planos de corte tapan la imagen mientras la voz continúa (como edita un creador real);
  - hook visible sin sonido (sticker de texto) en los 2–3 primeros segundos;
  - subtítulos palabra a palabra en zona segura; tarjeta CTA final; música baja con ducking;
  - etiqueta de IA según la política de la marca (visible por defecto: AI Act art. 50).
"""

from __future__ import annotations

import re

from ..editing.graphics import ai_label, cta_card, strip_unsupported, text_sticker
from ..editing.render import overlay_from_png
from ..models import AudioClip, BrandKit, CaptionTrack, Keyframe, Product, Project, Timeline, VideoClip, Word
from ..providers import registry
from ..providers.local_asr import align, norm, repeated_spans
from ..store import ctx


AI_LABEL = {"es": "Creado con IA", "en": "Made with AI", "de": "Mit KI erstellt", "fr": "Créé avec l'IA", "it": "Creato con l'IA",
            "pt": "Criado com IA", "ca": "Creat amb IA"}


def _segment_times(p: Project, words: list[Word]) -> dict[str, tuple[float, float]]:
    """Asigna a cada segmento hablado su intervalo [inicio, fin] a partir de las palabras alineadas."""
    out: dict[str, tuple[float, float]] = {}
    if not p.script:
        return out
    i = 0
    for seg in p.script.segments:
        n = len(seg.text.split())
        if n == 0 or i >= len(words):
            continue
        ws = words[i : i + n]
        out[seg.id] = (ws[0].start, ws[-1].end)
        i += n
    return out


def _q(t: float, fps: int) -> float:
    """Cuadra un instante a fotograma entero (evita el desfase audio/vídeo acumulado en cada corte)."""
    return round(round(t * fps) / fps, 4)


def _energy(a) -> tuple[list[float], float]:
    """Envolvente RMS en dB cada 10 ms del audio del A-roll (para afinar dónde empieza y acaba la voz)."""
    import numpy as np

    from ..media import read_wav_mono

    pcm = read_wav_mono(ctx().assets.abspath(a), rate=16000)
    if pcm.size < 1600:
        return [], 0.01
    hop = 160
    n = pcm.size // hop
    frames = pcm[: n * hop].reshape(n, hop).astype(np.float32)
    rms = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    db = (20 * np.log10(rms + 1e-9)).tolist()
    return db, 0.01


def _dip(env: tuple[list[float], float], a: float, b: float) -> float:
    """Instante más silencioso de [a, b] (media de 30 ms): ahí se corta sin oír media sílaba. Whisper descuadra los bordes
    de palabra hasta ~0,25 s (comprobado: «mañana» acababa en 17,32 s y Whisper decía 17,09)."""
    db, step = env
    i0, i1 = max(0, int(a / step)), min(len(db) - 2, int(b / step))
    if i1 <= i0:
        return b
    return min(range(i0, i1), key=lambda i: db[i - 1] + db[i] + db[i + 1] if i > 0 else db[i]) * step


def _voiced(env: tuple[list[float], float], a: float, b: float) -> bool:
    """¿Hay voz en [a, b]? (más de 15 dB sobre el suelo de ruido de la toma)."""
    db, step = env
    if not db:
        return True
    floor = sorted(db)[max(0, len(db) // 10)]
    seg = db[int(a / step): max(int(a / step) + 1, int(b / step))]
    return bool(seg) and max(seg) > floor + 15


def _speech_ranges(words: list[Word], env, total: float, fps: int, gap: float = 0.25, pad_in: float = 0.08,
                   pad_out: float = 0.12, extras: list[tuple[float, float]] | None = None) -> list[tuple[float, float]]:
    """Tramos de la toma con voz: se eliminan las pausas > `gap` s que de verdad son silencio (montaje UGC real) y los
    huecos donde el modelo dice algo que NO está en el guion (p. ej. repetir «por la mañana… por la mañana»)."""
    if not words:
        return [(0.0, total)]
    db, step = env
    floor = sorted(db)[max(0, len(db) // 10)] if db else -90

    def onset(t: float, limit: float) -> float:
        # Whisper adelanta los inicios de palabra: se busca el primer bloque con voz real
        if not db:
            return t
        k = int(t / step)
        while k < min(len(db), int(limit / step)) and db[k] < floor + 15:
            k += 1
        return k * step

    ranges: list[list[float]] = [[max(0.0, onset(words[0].start, words[0].end) - pad_in), 0.0]]
    for w0, w1 in zip(words, words[1:]):
        g0, g1 = w0.end + pad_out, onset(w1.start, w1.end) - pad_in
        if g1 - g0 > gap and not _voiced(env, g0 + 0.05, g1 - 0.05):
            ranges[-1][1] = g0
            ranges.append([g1, 0.0])
    ranges[-1][1] = min(total, words[-1].end + 0.3)
    for x0, x1 in extras or []:  # frases repetidas fuera (sus bordes caen en silencio: el corte no se oye)
        ranges = [y for a, b in ranges for y in (([a, b],) if x1 <= a or x0 >= b else ([a, x0], [x1, b]))]
    out = [(_q(a, fps), _q(b, fps)) for a, b in ranges if b - a > 0.15]
    return out or [(0.0, total)]


class _OutMap:
    """Correspondencia tiempo de la toma ↔ tiempo de salida tras quitar las pausas."""

    def __init__(self, ranges: list[tuple[float, float]]):
        self.segments: list[tuple[float, float, float]] = []  # (out_a, out_b, src_a)
        t = 0.0
        for a, b in ranges:
            self.segments.append((t, t + (b - a), a))
            t += b - a
        self.ranges = ranges
        self.total = round(t, 4)

    def out(self, src: float) -> float:
        for (oa, ob, sa), (a, b) in zip(self.segments, self.ranges):
            if src < a:
                return oa
            if src <= b:
                return oa + (src - a)
        return self.total

    def pieces(self, seg_starts: list[tuple[float, int]]) -> list[tuple[float, float, float, int]]:
        """Trozos de salida partidos también por cambio de segmento del guion (k alterna el punch-in)."""
        out = []
        for oa, ob, sa in self.segments:
            cuts = sorted({oa, ob} | {x for x, _k in seg_starts if oa < x < ob})
            for x0, x1 in zip(cuts, cuts[1:]):
                k = next((kk for xx, kk in reversed(seg_starts) if xx <= x0 + 1e-6), 0)
                out.append((x0, x1, sa + (x0 - oa), k))
        return out


def _segment_starts(p: Project, seg_t: dict[str, tuple[float, float]], om: _OutMap) -> list[tuple[float, int]]:
    return sorted((om.out(max(0.0, seg_t[sg.id][0] - 0.08)), k)
                  for k, sg in enumerate(p.script.segments if p.script else []) if sg.id in seg_t)


def _snap(c0: float, c1: float, bounds: list[float], hook_end: float, src_len: float, min_d: float = 0.8) -> tuple[float, float]:
    """Ajusta un plano de corte a los límites de los tramos de A-roll si dejaría restos de menos de `min_d` s."""
    before = max((b for b in bounds if b <= c0 + 1e-6), default=0.0)
    if 0 < c0 - before < min_d and before >= hook_end:
        c0 = before
    after = min((b for b in bounds if b >= c1 - 1e-6), default=c1)
    if 0 < after - c1 < min_d:
        c1 = after if after - c0 <= src_len else max(c0 + 1.0, after - min_d)
    return c0, c1


def _merge_slivers(clips: list[VideoClip], fps: int, min_d: float = 0.5) -> list[VideoClip]:
    """Planos de menos de `min_d` s: SOLO se funden con el vecino si es el mismo origen y continuo (nunca se rompe la
    sincronía labial alargando un plano con otra parte de la toma). Después todo se cuadra a fotograma."""
    out: list[VideoClip] = []
    for c in clips:
        prev = out[-1] if out else None
        cont = prev is not None and prev.asset_id == c.asset_id and abs(prev.src_in + prev.duration - c.src_in) < 0.02
        if prev is not None and cont and (c.duration < min_d or prev.duration < min_d):
            prev.duration = round(c.start + c.duration - prev.start, 4)
            continue
        out.append(c)
    for c in out:
        c.start, c.duration = _q(c.start, fps), _q(c.duration, fps)
    return out


def _product_opener(p: Project, product: Product, brand: BrandKit, talking: list, dur: float, fps: int):
    """Plano de apertura con el producto REAL (packshot recortado sobre la escena) bajo la voz del hook.

    Se activa con `hook_product_open` (lo decide el estudio creativo cuando el hook habla del aspecto del producto).
    No es un plano nuevo del guion: es un corte de montaje, gratis y sin riesgo de deformación del producto.
    """
    from ..models import Shot

    if not p.variant_spec.get("hook_product_open") or not (product.packshot_asset_ids or product.footage_asset_ids):
        return None
    from .product import packshot_clip

    from .scenes import _people_free_plate

    loc = ctx().db.get_asset(talking[0].keyframe_asset_id) if talking and talking[0].keyframe_asset_id else None
    clip = packshot_clip(product, dur + 0.4, brand=brand, tag=f"opener_{p.id}", background=_people_free_plate(p) or loc)
    sh = next((s for s in p.shots if s.constraints.get("opener")), None)
    if sh is None:
        from ..models import Route

        sh = Shot(index=len(p.shots), shot_type="product_hero", duration=dur, description="apertura: producto real bajo el hook",
                  uses_product=True, constraints={"opener": True},
                  route=Route(pipeline="compose.packshot", provider="local", reason="producto real bajo el hook"))
        p.shots.append(sh)
    sh.clip_asset_id, sh.status, sh.duration = clip.id, "ready", dur
    return sh


def _frontal_face(asset_id: str | None) -> bool:
    """¿El clip muestra una cara frontal grande? (bajo la voz parecería que habla sin mover la boca)."""
    if not asset_id:
        return False
    import cv2

    from ..media import frame_at
    from . import identity

    a = ctx().db.get_asset(asset_id)
    f = frame_at(ctx().assets.abspath(a), max(0.2, (a.duration or 2) / 2), ctx().work("edit", "face") / f"{a.id}.jpg", width=720)
    img = cv2.imread(str(f))
    if img is None:
        return False
    f = identity.detect(img)
    return f is not None and float(f[2]) >= 0.15 * img.shape[1]


def _quietest(env, win: float = 0.6) -> tuple[float, float]:
    """Ventana más silenciosa de la toma: su ruido de sala se repite bajo la tarjeta final (sin caída a silencio)."""
    db, step = env
    n = int(win / step)
    if len(db) < n * 2:
        return 0.0, 0.0
    best, at = 1e9, 0
    for k in range(0, len(db) - n, 5):
        m = sum(db[k:k + n]) / n
        if m < best:
            best, at = m, k
    return round(at * step, 3), win


def build_timeline(p: Project, brand: BrandKit, product: Product, *, music: bool = True, music_asset: str | None = None) -> Timeline:
    tl = Timeline()
    talking = [s for s in p.shots if s.shot_type == "talking_head" and s.clip_asset_id]
    cut = [s for s in p.shots if s.shot_type not in ("talking_head", "graphic_card") and s.clip_asset_id]
    card = next((s for s in p.shots if s.shot_type == "graphic_card"), None)
    assert p.script is not None
    script_text = " ".join(s.text for s in p.script.segments if s.text)

    if talking:
        aroll = ctx().db.get_asset(talking[0].clip_asset_id)  # type: ignore[arg-type]
        tl.fps = 24 if abs((aroll.fps or 30) - 24) < 0.6 else 30  # Omni sale a 24 fps: evitar el judder 24→30
        fps = tl.fps
        tr = registry.transcriber()
        _, asr_words = tr.transcribe(aroll, p.brief.locale) if hasattr(tr, "transcribe") else ("", [])
        reps: list[tuple[float, float]] = []
        if asr_words and hasattr(tr, "phrases"):
            ph = tr.phrases(aroll, p.brief.locale)
            reps = repeated_spans(ph, script_text)
            if reps:  # tiempos de palabra de la transcripción por frases (la completa los descuadra en la repetición)
                asr_words = [w for _a, _b, ws in ph for w in ws if not any(r0 - 0.02 <= w.start and w.end <= r1 + 0.02 for r0, r1 in reps)]
                p.log.append("A-roll: repetición no escrita en el guion fuera del montaje: " +
                             ", ".join(f"{a:.2f}–{b:.2f} s" for a, b in reps))
        words = align(script_text, asr_words) if asr_words else []
        if not words:
            from ..providers.mock import even_words

            words = even_words(script_text, aroll.duration or 10.0, 0.4)
        p.words = words
        seg_t = _segment_times(p, words)
        env = _energy(aroll)
        ranges = _speech_ranges(words, env, aroll.duration or words[-1].end + 0.5, fps,
                                extras=[(a, b if any(abs(b - e) < 1e-3 for _s, e, _w in ph) else _dip(env, b - 0.15, b + 0.35))
                                        for a, b in reps])  # el final de una frase entera ya cae en silencio
        omap = _OutMap(ranges)
        speech_end = omap.total
        hook_id = p.script.segments[0].id if p.script.segments else None
        hook_end = omap.out(seg_t[hook_id][1]) if hook_id in seg_t else 2.4

        # 1) planos de corte en tiempo de SALIDA: nunca dentro del hook; caras frontales mudas nunca bajo la voz
        covers: list[tuple[float, float, str]] = []
        bounds = sorted({0.0, speech_end} | {x for oa, ob, _sa, _k in omap.pieces(_segment_starts(p, seg_t, omap)) for x in (oa, ob)})
        # apertura: dura lo que pida el hook, pero si dejaría un resto de cara <0,5 s antes del siguiente corte, lo cubre
        want = min(1.6, max(0.8, hook_end - 0.35))
        nxt = min((b for b in bounds if b >= want - 1e-6), default=want)
        want = nxt if nxt - want < 0.5 else want
        opener = _product_opener(p, product, brand, talking, _q(want, fps), fps)
        if opener is not None:
            # el hook se OYE sobre el producto real (visible desde el fotograma 0) y se corta a su cara para el resto
            cut.append(opener)
            covers.append((0.0, _q(opener.duration, fps), opener.id))
        # planos que TAPAN un tramo exacto de la toma (p. ej. donde el modelo deformó el producto): la voz sigue
        # debajo y la imagen pasa al plano limpio. Se fija en tiempo de la toma: sobrevive a recortes de pausas.
        for sh in cut:
            rng = sh.constraints.get("src_cover")
            if rng:
                c0, c1 = _q(omap.out(rng[0]), fps), _q(omap.out(rng[1]), fps)
                if c1 - c0 >= 0.4 and not any(not (c1 <= x0 or c0 >= x1) for x0, x1, _ in covers):
                    covers.append((c0, c1, sh.id))
        for sh in cut:
            if sh.constraints.get("opener") or sh.constraints.get("src_cover"):
                continue  # ya colocado
            sid = sh.segment_ids[0] if sh.segment_ids else None
            if not sid or sid not in seg_t:
                p.log.append(f"{sh.id} ({sh.shot_type}): sin segmento hablado al que acompañar → fuera del montaje")
                continue
            if sh.shot_type in ("actor_motion", "reaction") and _frontal_face(sh.clip_asset_id):
                p.log.append(f"{sh.id} ({sh.shot_type}): cara frontal callada bajo la voz parecería un doblaje roto → fuera del montaje")
                continue
            a, b = omap.out(seg_t[sid][0]), omap.out(seg_t[sid][1])
            start = max(a + 0.3, hook_end + 0.05)
            prev_end = max((c1 for c0, c1, _ in covers if c1 > a), default=None)
            if prev_end is not None:
                start = max(start, prev_end + 0.8)
            src_len = max(0.0, (ctx().db.get_asset(sh.clip_asset_id).duration or sh.duration) - 0.2)  # type: ignore[arg-type]
            cap = 2.2 if sh.shot_type == "product_hero" else sh.duration  # el packshot fijo cansa: corto
            dur = min(sh.duration, cap, src_len, max(0.0, b - start + 0.25), speech_end - start)
            if dur < 1.0 or any(not (start + dur <= c0 or start >= c1) for c0, c1, _ in covers):
                p.log.append(f"{sh.id} ({sh.shot_type}): no cabe en su segmento → fuera del montaje")
                continue
            c0, c1 = _snap(start, start + dur, bounds, hook_end, src_len)
            if c1 - c0 < 1.0 or any(not (c1 <= x0 or c0 >= x1) for x0, x1, _ in covers):
                p.log.append(f"{sh.id} ({sh.shot_type}): no cabe sin dejar destellos → fuera del montaje")
                continue
            covers.append((_q(c0, fps), _q(c1, fps), sh.id))
        covers.sort()

        # 2) pista de vídeo: tramos de A-roll (jump cuts reales: las pausas ya no existen) y los cortes «recortan» encima
        for oa, ob, sa, k in omap.pieces(_segment_starts(p, seg_t, omap)):
            free = [(oa, ob)]
            for c0, c1, _sid in covers:
                free = [x for x0, x1 in free for x in (((x0, x1),) if c1 <= x0 or c0 >= x1 else
                                                       tuple(y for y in ((x0, c0), (c1, x1)) if y[1] - y[0] > 1e-3))]
            for x0, x1 in free:
                tl.clips.append(_aroll_clip(_talking_for(p, talking, k), aroll.id, sa + (x0 - oa), x1 - x0, x0, k))
        for c0, c1, sid in covers:
            cs = next(x for x in cut if x.id == sid)
            z0 = float(cs.constraints.get("zoom", 1.0))  # «punch-in»: el mismo clip, más cerrado, cuenta como plano nuevo
            tl.clips.append(VideoClip(scene_id=cs.id, asset_id=cs.clip_asset_id, start=c0, duration=c1 - c0,  # type: ignore[arg-type]
                                      src_in=float(cs.constraints.get("src_in", 0.15)),
                                      grade=dict(cs.constraints.get("grade") or {}),
                                      zoom=[Keyframe(t=0, scale=z0), Keyframe(t=c1 - c0, scale=z0 * 1.03)]
                                      if (z0 != 1.0 or cs.shot_type != "product_hero") else []))
        tl.clips = _merge_slivers(sorted(tl.clips, key=lambda c: c.start), fps)

        # 3) audio nativo por tramo (mismos cortes que el vídeo) con microfundidos + tono de sala de la propia toma
        for oa, ob, sa in omap.segments:
            tl.audio.append(AudioClip(role="native", asset_id=aroll.id, start=oa, src_in=sa, duration=ob - oa, gain_db=0.0,
                                      fade_in=0.01, fade_out=0.01))
        q0, qlen = _quietest(env)
        if qlen:
            tl.audio.append(AudioClip(role="room", asset_id=aroll.id, start=0.0, src_in=q0, loop_src=qlen, gain_db=-4.0))
        tl.captions = CaptionTrack(words=[Word(text=w.text, start=round(omap.out(w.start), 3), end=round(omap.out(w.end), 3))
                                          for w in words])
        busy = {sh.id for sh in cut if sh.shot_type == "app_screen"}
        tl.captions.boxed_spans = [(c.start, c.start + c.duration) for c in tl.clips if c.scene_id in busy]
        if opener is not None:
            tl.captions.hidden_spans = [(0.0, _q(opener.duration, fps))]  # rótulo y subtítulo dirían lo mismo a la vez
    else:
        # modo voz en off: planos en secuencia bajo la voz (TTS)
        speech_end = _voiceover_layout(p, tl, cut)

    # tarjeta CTA final (programática)
    card_d = 1.6 if p.variant_spec.get("pending_spoken_cta") else (card.duration if card else 2.2)
    work = ctx().work("render", p.id)
    logo = ctx().assets.abspath(brand.logo_asset_ids[0]) if brand.logo_asset_ids else None
    pimg = None
    if product.packshot_asset_ids:
        from .product import cutout

        pimg = cutout(ctx().db.get_asset(product.packshot_asset_ids[0]))  # producto recortado, no la foto con fondo blanco
    elif product.screenshot_asset_ids:
        pimg = ctx().assets.abspath(product.screenshot_asset_ids[0])
    cta_text = (p.script.cta if p.script and p.script.cta else (brand.ctas[0] if brand.ctas else "Descúbrelo"))
    foreign = bool(brand.locales) and p.brief.locale not in brand.locales  # variante de idioma: el botón también se transcrea
    button = (cta_text if foreign or not brand.ctas else brand.ctas[0])[:28]
    sub = cta_text
    if norm(sub) == norm(button):  # no repetir el botón: la línea de apoyo es un beneficio real y aprobado
        sub = next((b for b in (product.benefits + brand.approved_claims) if b), "")
        sub = sub[:1].upper() + sub[1:] if sub else ""
    png = cta_card(work / "cta.png", headline=strip_unsupported(product.name), sub=strip_unsupported(sub),
                   button=strip_unsupported(button), logo=logo,
                   bg=brand.colors.get("primary", "#111111"), accent=brand.colors.get("accent", "#FF3B30"),
                   fg=brand.colors.get("text", "#FFFFFF"), product_img=pimg)
    card_asset = ctx().assets.ingest(png, source="render:cta")
    tl.clips.append(VideoClip(scene_id=card.id if card else "cta", asset_id=card_asset.id, start=speech_end, duration=card_d,
                              zoom=[Keyframe(t=0, scale=1.0), Keyframe(t=card_d, scale=1.04)]))
    if card:
        card.clip_asset_id, card.status = card_asset.id, "ready"
    tl.duration = speech_end + card_d

    # hook visible sin sonido
    hook = p.script.segments[0] if p.script.segments else None
    hook_text = (hook.on_screen_text or hook.text) if hook else ""
    if hook_text:
        st = text_sticker(hook_text, work / "hook.png", max_chars=20)
        op = next((c for c in tl.clips if any(s.id == c.scene_id and s.constraints.get("opener") for s in p.shots)), None)
        hd = op.duration if op is not None else min(2.6, speech_end)
        tl.overlays.append(overlay_from_png(st, start=0.0, duration=hd, y=0.29, w=0.78, animation="none"))
    # rótulos ligados a un tramo de la toma (p. ej. «11 y 9 cm» sobre el plano de perfil)
    for k, stk in enumerate(p.variant_spec.get("stickers") or []):
        if talking and stk.get("src"):
            a0, a1 = omap.out(stk["src"][0]), omap.out(stk["src"][1])
            if a1 - a0 >= 0.5:
                png = text_sticker(stk["text"], work / f"sticker_{k}.png", max_chars=22)
                tl.overlays.append(overlay_from_png(png, start=a0, duration=a1 - a0, y=float(stk.get("y", 0.29)), w=0.7,
                                                    animation="none"))
    # sin CTA hablada (p. ej. cuota agotada): la pregunta/CTA va como rótulo en el último segundo y medio de voz
    pend = p.variant_spec.get("pending_spoken_cta") or []
    if pend:
        q = re.split(r"(?<=[?!.])\s", pend[0])[0][:40]
        stc = text_sticker(q, work / "cta_question.png", max_chars=20)
        tl.overlays.append(overlay_from_png(stc, start=max(0.0, speech_end - 1.6), duration=1.6, y=0.29, w=0.78, animation="none"))
    # etiqueta IA (política de marca; por defecto visible toda la pieza, discreta)
    if brand.ai_label_policy in ("visible", "end_card"):
        lab = ai_label(work / f"ai_label_{p.brief.locale}.png", AI_LABEL.get(p.brief.locale.split("-")[0], "Made with AI"))
        start = 0.0 if brand.ai_label_policy == "visible" else speech_end
        # y≈0,155: por debajo de las pestañas de TikTok y fuera del 14 % superior que tapa Reels
        tl.overlays.append(overlay_from_png(lab, start=start, duration=tl.duration - start, x=0.5, y=0.18, w=0.30, animation="none"))
    # música
    if music and music_asset:  # variante: misma música que el máster (no se vuelve a pagar Lyria)
        tl.audio.append(AudioClip(role="music", asset_id=music_asset, start=0.0, duration=tl.duration, gain_db=-20.0))
    elif music:
        try:
            mus = registry.music().generate(
                f"Light, warm lo-fi background music for a casual social media video, unobtrusive, no vocals, {int(tl.duration) + 2} seconds",
                tl.duration + 2)
            tl.audio.append(AudioClip(role="music", asset_id=mus.id, start=0.0, duration=tl.duration, gain_db=-20.0))
        except Exception as e:  # noqa: BLE001
            p.log.append(f"música no disponible: {str(e)[:120]}")
    tl.metadata = {"project": p.id, "angle": p.chosen_angle_id, "locale": p.brief.locale, "platform": p.brief.platform,
                   "actor": p.continuity.actor_id, "look": p.continuity.look_id, "talk_mode": p.variant_spec.get("talk_mode", "native")}
    return tl


def _talking_for(p: Project, talking: list, k: int):
    """Tramo hablado que contiene el segmento k del guion (el QA culpa y regenera la escena correcta, no siempre la 1.ª)."""
    seg = p.script.segments[k].id if p.script and k < len(p.script.segments) else None
    return next((t for t in talking if seg in t.segment_ids), talking[0])


def _aroll_clip(shot, asset_id: str, src_from: float, dur: float, at: float, k: int) -> VideoClip:
    scale = 1.0 if k % 2 == 0 else 1.08  # >1,08 sobre una fuente de 720p se ve blando
    y = 0.45 if k % 2 else 0.5
    return VideoClip(scene_id=shot.id, asset_id=asset_id, start=at, duration=dur, src_in=src_from,
                     zoom=[Keyframe(t=0, scale=scale, x=0.5, y=y)])


def _voiceover_layout(p: Project, tl: Timeline, cut: list) -> float:
    """Modo voz en off: TTS por segmento (voz persistente del actor) + planos en secuencia."""
    from ..providers.base import TTSResult

    tts = registry.tts()
    actor_voice = None
    from ..models import Actor

    try:
        actor = ctx().db.get(Actor, p.continuity.actor_id) if p.continuity.actor_id else None
    except KeyError:
        actor = None
    if actor and p.brief.locale in actor.voices:
        actor_voice = actor.voices[p.brief.locale]
    from .actors import default_voice

    # sin voz del actor para este idioma: voz nativa del idioma (nunca la castellana leyendo alemán)
    voice = actor_voice.voice_name if actor_voice else default_voice(p.brief.locale, actor.gender if actor else "female")
    style = actor_voice.style_prompt if actor_voice else "casual, cercana, natural"
    t = 0.0
    words: list[Word] = []
    assert p.script is not None
    for seg in p.script.segments:
        if not seg.text:
            continue
        r: TTSResult = tts.speak(seg.text, voice=voice, locale=p.brief.locale, style=style)
        d = r.audio.duration or 2.0
        tl.audio.append(AudioClip(role="voice", asset_id=r.audio.id, start=t))
        tr = registry.transcriber()
        ws = tr.words(r.audio, p.brief.locale, seg.text) if hasattr(tr, "words") else []
        words += [Word(text=w.text, start=w.start + t, end=w.end + t) for w in ws]
        t += d + 0.08
    tl.captions = CaptionTrack(words=words)
    vis = [s for s in p.shots if s.clip_asset_id and s.shot_type != "graphic_card"]
    if vis:
        each = t / len(vis)
        at = 0.0
        for s in vis:
            tl.clips.append(VideoClip(scene_id=s.id, asset_id=s.clip_asset_id, start=at, duration=each,
                                      zoom=[Keyframe(t=0, scale=1.0), Keyframe(t=each, scale=1.06)]))
            at += each
    return t
