"""Plan de SFX de una timeline: eventos de los componentes + decisiones `sfx` → `AudioItem`s (sustituye a
`compile.plan_sfx`). Reglas de diseño sonoro del catálogo (`recursos/sfx/eventos.yaml`) y del mapa de animaciones:

- Presupuesto por PRIORIDAD y EQUILIBRIO a lo largo del vídeo (no por orden de llegada): se elige el candidato de más
  prioridad penalizado por los SFX ya elegidos a ±10 s. ≤ `max_per_min`/min (tecleo y click no cuentan), ≤ `max_hits`
  remates, nunca dos SFX a < 1,2 s.
- Misma plantilla, mismo tratamiento: apariciones repetidas de un componente usan el MISMO fichero con tono
  0, +1, +2, +3 st; el whoosh de entrada solo en la primera (o si la anterior queda a ≥ 30 s).
- `tarjeta_entra`: whoosh corto (≤ 0,4 s), empieza como mucho 150 ms antes; nunca largo ni grave bajo la voz.
- `transicion_luz`: un único fichero de la familia (subida_1, aire_medio_1, brillo_2) para todas las luces, ±1 st.
- Impacto/drop solo si una decisión lo pide: capa sub + capa media, ≤ 1,5 s, con 150–400 ms sin voz antes.
- `viz.decision` choose: pop_1 a −16 LU, 20 ms antes del resaltado (18-oct: firma_1 queda reservado a la
  firma `foco_oferta`; `reservados` de `animaciones.yaml`).
- Tecleo ≤ 1,5 s con fundidos de 80 ms y solo si algo se teclea en pantalla; click solo con cursor/botón visible.
- `item.props.sfx == False` → sin sonido (18-oct: PROHIBIDO en un bloque animado; lo avisan `ck validate` y la QA
  `sfx.silent_block`; para quitar un sonido concreto, `props.sfx_skip`). Duración ≤ su clase (≤ 0,9 s salvo riser) y
  nunca más allá del item.
- Densidad (18-oct-2026): tope del perfil en GESTOS (24/min en Shorts); un gesto = un sonido con sus capas. Guarda
  local: ≤ `sfx.racimo_1s_max` (2) gestos en 1 s.
- Sincronía con el evento VISUAL: con `events` (de `window.__ckEvents`, ver `cutkit.audio.events`) cada SFX suena
  20 ms antes de su evento (opción resaltada, corte, aterrizaje); sin evento, cae a la cue de la palabra.
  `align_version(slug, vid)` es la segunda pasada tras `build_project` (extrae eventos y reescribe los SFX).
- Variedad: nunca el mismo fichero dos veces en 20 s (salvo la firma de plantilla), ≤ 2 risers por vídeo, la familia
  de luz rota; el soplido de una transición dura ≤ su ventana visual + 0,2 s.
`LAST_REPORT` guarda lo elegido y lo descartado con su motivo (para QA y para el crítico).
"""
from __future__ import annotations

import math
from cutkit.spec import AudioItem

from . import sfx as sfxlib

LAST_REPORT: dict = {}

MIN_GAP_S = 1.2
SAME_ITEM_GAP_S = 0.6                                # secuencia de un mismo componente (transform → output): ≥ 0,6 s
GESTURE_MERGE_S = 0.6                                # misma cadena a < 0,6 s = un gesto (norma de diseño sonoro)
BALANCE_MAX_GAP_S = 20.0                             # equilibrio: ningún tramo más largo sin SFX si hay candidato
CLASS_MAX_S = {"riser": 2.5, "type": 1.5}            # resto: 0,9 s
RISER_TAIL_S = 0.2                                   # un riser explícito suena hasta su punto de sincronía + esto
DEFAULT_MAX_S = 0.9
WHOOSH_CARD_MAX_S = 0.4
WHOOSH_MAX_PRE_S = 0.15
UI_KINDS = {"type", "click"}                         # no cuentan para la densidad
HERO_EVENTS = {"riser_revelacion", "impacto_remate", "riser", "impact"}
LIGHT_FAMILY = ["subida_1", "aire_medio_1", "brillo_2"]
CHOOSE_FILE, CHOOSE_REL_LU, CHOOSE_LEAD_S = "pop_1", -16.0, 0.02   # 18-oct: 13 reservado a la firma foco_oferta
TYPE_CPS = 28.0                                      # viz.token_stream teclea el prompt a ~28 car/s
REPEAT_WINDOW_S = 30.0
NO_TOY = ("videojuego",)                             # nada de 8 bits salvo petición expresa


def _resolve(d, wt: dict, fps: int, dur: float):
    try:
        from cutkit.compile import resolve_anchor
        return resolve_anchor(d, wt, fps, dur)
    except Exception:                                # noqa: BLE001 — respaldo local (misma lógica)
        a = d.anchor
        if a.start not in wt:
            return None
        s0 = wt[a.start][0 if a.start_edge == "s" else 1] + a.lead
        e_id = a.end or a.start
        t1 = wt.get(e_id, wt[a.start])[1 if a.end_edge == "e" else 0] + a.tail
        return (max(0.0, s0), min(dur, t1)) if t1 > s0 else None


def _voice_at(wt: dict, a: float, b: float) -> bool:
    return any(s < b and e > a for s, e in wt.values())


TRANSIENTS = ("pop", "click", "ding", "tick", "glitch", "retro")
MOVE_MAX_S = 0.06                                    # un SFX de prio < 5 que pisa el arranque de una palabra se mueve
#                                                      (≤ 60 ms: con el adelanto de 20 ms queda a ≤ +40 ms del evento)
MOVE_PRIO = 5                                        # al hueco de voz más cercano (≤ 150 ms) o se descarta
ACCENT_OVER_VOICE_LU = -12.0                         # acento que no puede salir de la voz: −12 LU (+ brillo); a −7 tapaba la palabra clave
POP_OVER_VOICE_LU = -12.0                            # pop que suena sobre voz: −12 LU con paso alto 250 Hz y +4 dB a 3 kHz
POP_OVER_VOICE_EQ = {"hp": 250, "peak_hz": 3000, "peak_db": 4.0}
# 20-oct (crítica de audio de un vídeo de prueba, medido por bandas de tercio de octava): un transitorio con el centroide
# en la banda de la voz (pop_1 1,2 kHz, pop_2 0,9 kHz, tick_1 2 kHz) que cae sobre el arranque de
# una palabra queda TAPADO (SFX − voz y cama ≤ +3 dB en su mejor banda: sfx_00, 09, 17.e1/e2, 23, 23.e1), y los que
# llevan algo por encima de 6 kHz asoman (+11…+41 dB: el encendido 8 + brillo 6, click_1 a 6,5 kHz). Regla: si el
# golpe (el principal o uno de escalera) pisa una palabra y su centroide < BRIGHT_MAX_HZ, se le añade la capa de brillo
# brillo_1 (10,5 kHz) a BRIGHT_REL_DB de su nivel, salvo que el gesto ya lleve una capa aguda. Es parte del gesto
# (id «sfx_NN.bK»): no cuenta en la densidad ni en la QA de sincronía.
BRIGHT_FILE = "brillo_1"
BRIGHT_MAX_HZ = 5000.0
BRIGHT_HIGH_HZ = 6000.0                              # una capa con centroide ≥ esto ya es «aguda»
BRIGHT_REL_DB = -5.0                                 # el encendido (capa a −6) ya asomaba +11 dB
BRIGHT_MAX_S = 0.30


def _over_voice(wt: dict, t: float, body: float = 0.12) -> bool:
    return any(s < t + body and e > t - 0.02 for s, e in wt.values())


def _phone_presence(fid: str) -> float:
    """dB por encima de 350 Hz (RMS de los primeros 120 ms tras el ataque) por LU de momentánea máxima, del SFX ya
    procesado para ir sobre voz. Sirve para elegir el acento que más asoma en el altavoz de un móvil."""
    return _phone_presence_cached(fid)


from functools import lru_cache as _lru  # noqa: E402


@_lru(maxsize=64)
def _phone_presence_cached(fid: str) -> float:
    import numpy as _np
    from scipy import signal as _sg
    from . import _dsp as _d
    f = sfxlib.lookup(fid)
    if f is None:
        return -99.0
    g = _processed(f, hp=POP_OVER_VOICE_EQ["hp"], peak_hz=POP_OVER_VOICE_EQ["peak_hz"], peak_db=POP_OVER_VOICE_EQ["peak_db"])
    ms, du, _ = _entry_span(g)
    x = _d.load(g["ruta"], channels=2)[int(ms * _d.SR): int((ms + du) * _d.SR)]
    if len(x) < 480:
        return -99.0
    mm = _d.momentary_max(_np.vstack([x, _np.zeros((_d.SR // 2, 2))]))
    on = int(sfxlib.measure_sync(g["ruta"], ms, du, "onset") * _d.SR)
    y = _sg.sosfilt(_sg.butter(4, 350, "highpass", fs=_d.SR, output="sos"), x.mean(axis=1))[on: on + int(0.12 * _d.SR)]
    return float(_d.db(_np.sqrt(_np.mean(y ** 2)))) - mm


def _processed(f: dict, hp: float | None = None, peak_hz: float | None = None, peak_db: float = 0.0) -> dict:
    """Copia procesada del SFX (mismo timing: paso alto de fase cero + campana) en `datos/biblioteca/sfx_proc/`.
    Para que un pop asome en el altavoz del móvil sobre la voz, o para dejar solo el aire de un barrido."""
    import numpy as _np
    from scipy import signal as _sg
    from . import _dsp as _d
    if f.get("procesado"):                         # siempre desde el ORIGINAL (nunca procesar dos veces una copia)
        base = sfxlib.lookup(f["id"])
        if base is not None:
            f = {**base, **({"_slice": f["_slice"]} if f.get("_slice") else {})}
    tag = f"hp{int(hp or 0)}_pk{int(peak_hz or 0)}x{peak_db:g}"
    out = sfxlib.PROC_DIR / f"{f['id']}__{tag}.wav"
    if not out.exists():
        x = _d.load(f["ruta"], channels=2).astype(_np.float64)
        if hp:
            x = _sg.sosfiltfilt(_sg.butter(2, hp, "highpass", fs=_d.SR, output="sos"), x, axis=0)
        if peak_hz and peak_db:
            x = _sg.sosfilt(_d.peaking_sos(peak_hz, peak_db, 1.0), x, axis=0)
        _d.write(out, x, subtype="FLOAT")
    return {**f, "ruta": str(out), "procesado": tag}


def _mobile(f: dict | None) -> dict | None:
    """La MISMA cadena para todo SFX (17-oct-2026): el procesado de móvil de `animaciones.yaml` (`eq_movil`: paso alto
    250 Hz + campana +4 dB a 3 kHz). Antes la CTA (`aparece_elemento_clave`), la luz de las transiciones, la firma de
    elección, los fijos del registro y los del catálogo sonaban sin él (~24 dB más de graves que el resto). Solo los
    subgraves de un impacto se quedan sin paso alto."""
    if f is None:
        return None
    eqm = _anim_map().get("eq_movil") or POP_OVER_VOICE_EQ
    return _processed(f, hp=eqm.get("hp"), peak_hz=eqm.get("peak_hz"), peak_db=float(eqm.get("peak_db", 0.0)))


ANIM_MAP = sfxlib.EVENTOS.parent / "animaciones.yaml"     # recursos/sfx/animaciones.yaml (mapa componente → paleta)
ROLE_PRIO = {"acento": 6, "entrada": 5, "textura": 3}
ESCALERA_ST = [0, 0, 0, 0, 0]                        # sin escalera de tono (15-oct, crítica de audio de un vídeo de prueba): la
#                                                      variedad sale de rotar ficheros; antes 0, 5, 7, 10, 12 st
MAX_PITCH_ST = 2.0                                   # ningún SFX de animación se desafina más de ±2 st


_AMAP: dict = {}


def _anim_map() -> dict:
    """`animaciones.yaml` (en caché mientras no cambie el fichero; se lee muchas veces por plan). Solo lectura."""
    import yaml
    try:
        mt = ANIM_MAP.stat().st_mtime_ns
        if _AMAP.get("mt") != mt:
            _AMAP.update({"mt": mt, "data": yaml.safe_load(ANIM_MAP.read_text(encoding="utf-8")) or {}})
        return _AMAP["data"]
    except Exception:                                       # noqa: BLE001
        return {}


def _pal_file(spec) -> dict | None:
    """Fichero de una paleta: «id» o «id#k» = el recorte k de un paquete del catálogo (p. ej. «aire_3»), que va
    como `_slice` (inicio, duración, sincronía desde el inicio) con la sincronía del catálogo."""
    fid, _, k = str(spec).partition("#")
    f = sfxlib.lookup(fid)
    if f is None or not k:
        return f
    rec = f.get("recortes") or []
    try:
        r = rec[int(k)]
    except (ValueError, IndexError):
        return f
    a, b = r["inicio_ms"] / 1000, r["fin_ms"] / 1000
    return {**f, "_slice": (a, b - a, max(0.0, r["sync_ms"] / 1000 - a)), "_recorte": int(k)}


def _centroid_exempt() -> set[str]:
    """Ficheros de paletas con `excepcion_centroide` (la firma): pasan por la cadena de móvil aunque sean graves."""
    pals = _anim_map().get("paletas") or {}
    return {str(i).partition("#")[0] for p in pals.values() if p.get("excepcion_centroide") for i in p.get("ficheros", [])}


def _mobile_ok(f: dict | None) -> bool:
    """Regla del 18-oct-2026: ninguna muestra con centroide (catálogo) < `centroide_min_hz` (250 Hz) por la cadena de
    móvil (paso alto 250 Hz): aire_1 (87 Hz) quedaba en un soplo inaudible. Salvo excepción declarada (la firma)."""
    if f is None or f.get("_subgrave"):
        return f is not None
    c = f.get("centroide_hz")
    lim = float(_anim_map().get("centroide_min_hz", 250))
    return c is None or float(c) >= lim or f["id"] in _centroid_exempt()


def _reserved_swap(f: dict | None, palette: str | None, ok=None) -> tuple[dict | None, bool]:
    """Ficheros reservados (`reservados` de animaciones.yaml): fuera de sus paletas suena `sustituto_reservado` (uno o
    una lista: el primero que `ok(id)` dé por bueno, p. ej. que no suene ya 4 veces en ese minuto).
    18-oct: firma_1 es la firma `foco_oferta` y nada más (registro de flow.pipeline, elección de viz.decision,
    catálogo de «aparece_elemento_clave», capa media de un impacto…)."""
    if f is None:
        return f, False
    am = _anim_map()
    res = (am.get("reservados") or {}).get(f["id"])
    if res is None:
        return f, False
    # forma larga (18-oct, ronda final): {paletas: [...], sustituto: [...]}; corta: [paletas] + `sustituto_reservado`
    allowed = res.get("paletas", []) if isinstance(res, dict) else res
    if palette in allowed:
        return f, False
    subs = (res.get("sustituto") if isinstance(res, dict) else None) or am.get("sustituto_reservado") or "pop_1"
    subs = [x for x in (sfxlib.lookup(str(i)) for i in (subs if isinstance(subs, list) else [subs])) if x is not None]
    if not subs:
        return f, False
    return next((x for x in subs if ok is None or ok(x["id"])), subs[0]), True


def _keystrokes(fid: str) -> list[float]:
    return _keystrokes_cached(fid)


from functools import lru_cache as _lru_k  # noqa: E402


@_lru_k(maxsize=8)
def _keystrokes_cached(fid: str) -> list[float]:
    """Instantes (s) de cada pulsación de un fichero de tecleo: para sonar UNA tecla (≤ 0,1 s), nunca un tecleo largo."""
    import numpy as _np
    from scipy import signal as _sg
    from . import _dsp as _d
    f = sfxlib.lookup(fid)
    if f is None:
        return []
    x = _d.load(f["ruta"], channels=1)[:, 0]
    env = _np.sqrt(_np.convolve(x.astype(_np.float64) ** 2, _np.ones(96) / 96, mode="same"))
    pk, _ = _sg.find_peaks(env, height=env.max() * 0.25, distance=int(0.06 * _d.SR))
    out = []
    for k in pk:
        j = k
        while j > 0 and env[j] > 0.3 * env[k]:
            j -= 1
        out.append(round(j / _d.SR, 4))
    return out


GENERIC_RULES = ("class",)                           # SFX genéricos del registro (`kind` sin fichero ni nivel)
TIME_UNITS = {"segundo", "segundos", "seg", "s", "minuto", "minutos", "min", "hora", "horas", "h", "día", "días",
              "dia", "dias", "semana", "semanas", "mes", "meses", "año", "años", "ms"}


def _variants(it) -> list[str]:
    """Variantes de un item para el mapa («componente@variante»): `props.style`, `props.mode` y `props.inputs`."""
    p = (it.props or {}) if it is not None else {}
    return [str(p[k]) for k in ("style", "mode", "inputs") if isinstance(p.get(k), str) and p.get(k)]


def _texture_for(it, comp: str | None, kind: str | None, done: set) -> str | None:
    """Textura (capa larga y suave dentro del gesto) para este evento, una vez por item (18-oct-2026):
    `props.sfx_texture: "reloj"` (o {textura, evento}) en cualquier item; automática (`reloj`) en el `number` de
    `stat.big_number` si `suffix`/`unit`/`prefix` es una unidad de tiempo; `props.sfx_texture: false` la quita."""
    import re
    if it is None or it.id in done:
        return None
    tex_all = _anim_map().get("texturas") or {}
    p = it.props or {}
    want = p.get("sfx_texture")
    if want is False:
        return None
    if isinstance(want, dict):
        name, ev = want.get("textura"), want.get("evento")
    else:
        name, ev = want, None
    if name is None and comp == "stat.big_number":
        words = set(re.findall(r"[a-záéíóúñ]+", " ".join(str(p.get(k) or "") for k in ("suffix", "unit", "prefix")).lower()))
        if words & TIME_UNITS:
            name = "reloj"
    if not name or name not in tex_all:
        return None
    # en qué evento: el pedido ({textura, evento}); con `sfx_texture: "reloj"` a secas, el primero del item que suene;
    # automática, los `eventos` de la textura (`number`)
    if ev is not None and kind != ev:
        return None
    if want is None and kind not in (tex_all[name].get("eventos") or []):
        return None
    done.add(it.id)
    return str(name)


def _event_candidates(events: list[dict], items: list, existing: list[dict], drops: list[dict] | None = None,
                      layout_cuts: list[float] | None = None) -> list[dict]:
    """Norma «cada animación lleva su sonido»: un candidato por evento visual mapeado en `animaciones.yaml`, salvo
    que ya haya uno del registro/decisiones en el mismo item a < `dedupe_s`. Entre dos animaciones del mismo item a
    < `dedupe_s`, queda la de más prioridad (papel: acento > entrada > textura).
    18-oct-2026:
    - el mapa manda sobre un SFX GENÉRICO del registro (regla `class`: `kind` sin fichero ni nivel declarado) del mismo
      item a < `dedupe_s` si su papel tiene más prioridad (el «stamp» genérico, prio 3, tapaba el sello «Gratis» de
      card.lesson, acento, y el tope lo quitaba antes que el «play»);
    - `sfx_skip: ["evento:n"]` quita la n-ésima APARICIÓN de ese evento (antes contaba solo las que sonaban, así que
      «step:1» callaba todos los pasos desde el segundo); `"evento:*"` las quita todas;
    - paletas con `ancla_corte_s`: si hay un corte de layout ≤ ese margen antes del primer fotograma visible, el SFX
      suena en el corte (−20 ms) y su `event_ref` es el corte (la firma `foco_oferta`)."""
    amap = _anim_map()
    emap, dedupe = amap.get("eventos") or {}, float(amap.get("dedupe_s", 0.25))
    pals = amap.get("paletas") or {}
    by_id = {it.id: it for it in items}
    out: list[dict] = []
    seq: dict[tuple, int] = {}
    seen: dict[tuple, int] = {}                        # apariciones de cada evento por item (para `sfx_skip`)
    tex_done: set = set()
    stairs_open: dict[tuple, dict] = {}                # (item, evento) → cabeza de su escalera
    cuts = sorted(layout_cuts or [])
    evs = list(events or [])
    # reserva: componentes del mapa de `cues` cuyos items no emiten NINGÚN evento → sus cues como eventos «de cue»
    with_events = {str(e.get("item")) for e in evs}
    for it in items:
        cmap = (amap.get("cues") or {}).get(it.component or "")
        if cmap and it.id not in with_events and it.props.get("sfx") is not False:
            evs += [{"item": it.id, "component": it.component, "kind": k, "t": float(v), "_cue": True,
                     "_spec": cmap[k]} for k, v in it.cues.items() if k in cmap]
    # eventos DERIVADOS (18-oct): una clave «evento+s» del mapa suena s segundos después de ese evento (p. ej. el cierre
    # de la vuelta de la aguja de viz.shapes@dial, que el componente no emite: `dial+0.733` = 22 f del barrido)
    for e in list(evs):
        it = by_id.get(str(e.get("item")))
        comp = e.get("component") or (it.component if it is not None else None)
        for m in [emap.get(f"{comp}@{v}") or {} for v in _variants(it)] + [emap.get(comp) or {}]:
            for key in m:
                base, _, off = str(key).partition("+")
                if off and base == e.get("kind"):
                    try:
                        evs.append({**e, "kind": key, "t": float(e["t"]) + float(off), "_derivado": True})
                    except ValueError:
                        pass
    for e in sorted(evs, key=lambda e: float(e["t"])):
        iid = str(e.get("item"))
        it = by_id.get(iid)
        if it is not None and it.props.get("sfx") is False:
            continue
        comp = e.get("component") or (it.component if it is not None else None)
        if comp == "media.capture_plane" and e.get("kind") == "enter" and it is not None and it.props.get("enter") == "cut":
            continue                           # entra por corte (sin movimiento): sin soplido
        k_occ = seen.get((iid, e.get("kind")), 0)
        seen[(iid, e.get("kind"))] = k_occ + 1
        skip = (it.props.get("sfx_skip") or []) if it is not None else []
        if f"{e.get('kind')}:{k_occ}" in skip or f"{e.get('kind')}:*" in skip:
            continue                           # `sfx_skip: ["option:1"]` = sin SFX en la 2.ª aparición de ese evento
        # «componente@variante» manda sobre «componente»: la variante es `props.style`, `props.mode` o `props.inputs`
        # (18-oct: viz.projects@grow, viz.shapes@dial, flow.pipeline@tiles…)
        style, spec = None, e.get("_spec")
        for v in (_variants(it) if spec is None else []):
            spec = (emap.get(f"{comp}@{v}") or {}).get(e.get("kind"))
            if spec:
                style = v
                break
        spec = spec or (emap.get(comp) or {}).get(e.get("kind"))
        if not spec:
            continue
        # 20-oct: «opcional» en el mapa = solo suena si el plan lo pide para ese item con su nivel
        # (`props.sfx_rel: {"word": -18}`); p. ej. una palabra por línea en title.lockup_grid
        if "opcional" in spec and (it is None or e.get("kind") not in ((it.props or {}).get("sfx_rel") or {})):
            continue
        pal, role = spec[0], spec[1]
        pal_d = pals.get(pal) or {}
        opts = dict(str(x).split("=", 1) for x in spec[2:] if "=" in str(x))     # p. ej. «lu=-16», «ms=70»
        # 20-oct: «prop=ring» = solo si `props.ring` del item no es false (media.ui_focus sin anillo: sin trazo)
        if opts.get("prop") and it is not None and (it.props or {}).get(opts["prop"], True) is False:
            continue
        # el evento marca el ARRANQUE del tween; la pieza se ve unos fotogramas después (retardo_ms de la paleta). 19-oct:
        # «ms=<x>» en el mapa suma un retardo propio del evento (la baldosa de viz.offer_grid y el nodo de viz.road se ven
        # cambiar 2–4 f después de su arranque: la QA por píxeles los medía de −67 a −133 ms)
        land = (float(pal_d.get("retardo_ms", 0)) + float(opts.get("ms", 0))) / 1000
        # 20-oct: en un evento «de cue» (componente sin eventos) vale el «ms» del mapa, sin el retardo de la paleta
        t = float(e["t"]) + (float(opts.get("ms", 0)) / 1000 if e.get("_cue") else land - EVENT_LEAD_S)
        ev_ref = None if e.get("_cue") else {"kind": e.get("kind"), "t": float(e["t"]), "item": iid,
                                            "t_visible": round(float(e["t"]) + land, 4)}
        anchored = None
        if pal_d.get("ancla_corte_s") and ev_ref is not None and cuts:
            # 18-oct: la firma suena en el corte de layout que la precede (≤ 0,1 s), en el silencio de antes de la
            # palabra, no +67 ms después encima de su arranque
            vis = float(e["t"]) + land
            lc = max((x for x in cuts if -1e-6 <= vis - x <= float(pal_d["ancla_corte_s"]) + 1e-6), default=None)
            if lc is not None:
                anchored = lc
                t = lc - EVENT_LEAD_S
                ev_ref = {"kind": "layout.cut", "t": round(lc, 4), "item": iid, "t_visible": round(lc, 4),
                          "evento": e.get("kind"), "t_evento": float(e["t"])}
        prio_new = ROLE_PRIO.get(role, 4)
        # ESCALERA (18-oct, ronda final): el mismo evento repetido en el mismo item (logos, tarjetas, pasos, opciones,
        # conectores, baldosas, teclas) es UN gesto: la cabeza a nivel de paleta y cada golpe siguiente a −4 dB con
        # ±2 st y su propio ritmo. Cuenta uno en el tope y en la guarda de racimo.
        if "escalera" in spec and stairs_open.get((iid, e.get("kind"))) in out:
            head = stairs_open[(iid, e.get("kind"))]
            last_t = head["stairs"][-1]["t"] if head["stairs"] else head["t"]
            if t - last_t < float(pal_d.get("escalera_min_s", STAIR_MIN_S)):
                continue                       # golpes pegados (cascada a 30 ms): con uno basta
            if any(c is not head and c.get("item_id") == iid and (abs(c["t"] - t) < dedupe or any(
                    abs(h["t"] - t) < dedupe for h in c.get("stairs", []))) for c in out):
                continue                       # otro gesto del mismo item ya suena a < 0,25 s
            if any(c.get("item_id") == iid and abs(c["t"] - t) < dedupe and not c.get("_sustituido")
                   and c["prio"] >= head["prio"] for c in existing):
                continue                       # 20-oct: ni encima del SFX del registro del mismo item (el héroe de
                #                                title.lockup_grid y la última palabra caen en el mismo fotograma)
            head["stairs"].append({"t": t, "event_ref": ev_ref})
            continue
        near = [c for c in existing if c.get("item_id") == iid and abs(c["t"] - t) < dedupe and not c.get("_sustituido")]
        if "sustituye" in spec:                 # el estilo tiene su gesto: fuera el SFX del registro de ese instante
            for c in near:
                if c["rule"] != "explicit":
                    c["_sustituido"] = f"{comp}:{e.get('kind')} (gesto propio del mapa)"
        elif near and all(c["rule"] in GENERIC_RULES and not c.get("declared") and c["prio"] < prio_new for c in near):
            for c in near:                      # el mapa manda sobre el SFX genérico del registro de menos prioridad
                c["_sustituido"] = f"{comp}:{e.get('kind')} ({role}, prio {prio_new} > {c['prio']})"
        if any(not c.get("_sustituido") for c in near):
            continue
        # duplicado con otra animación del mismo item (p. ej. `enter` y `focus` de viz.offer_grid en el mismo
        # fotograma): gana el de MÁS prioridad, no el que llega antes (17-oct-2026: se perdía la firma `foco_oferta`)
        dups = [c for c in out if c.get("item_id") == iid and abs(c["t"] - t) < dedupe]
        hit_dups = [(c, h) for c in out if c.get("item_id") == iid for h in c.get("stairs", []) if abs(h["t"] - t) < dedupe]
        if dups and max(c["prio"] for c in dups) >= prio_new:
            continue
        if hit_dups and max(c["prio"] for c, _ in hit_dups) >= prio_new:
            continue
        for c, h in hit_dups:                   # un golpe de escalera cede ante un gesto de más prioridad
            c["stairs"].remove(h)
        for c in dups:
            out.remove(c)
            if drops is not None:
                drops.append({"id": iid, "t": round(c["t"], 3), "event": c["event"],
                              "why": f"duplicado a < {dedupe:g} s de {comp}:{e.get('kind')} (gana el de más prioridad)"})
        key = (iid, e.get("kind"))
        k = seq.get(key, 0)
        seq[key] = k + 1
        did = (it.decision_ids[0] if it is not None and it.decision_ids else iid)
        step = e.get("step") or (e.get("extra") or {}).get("step") or (e.get("data") or {}).get("step")
        if "escalera" in spec:
            stairs_open[(iid, e.get("kind"))] = None          # se rellena con la cabeza que se añade ahora
        out.append({"t": t, "rule": "anim", "event": f"{comp}:{e.get('kind')}", "palette": pal, "role": role, "step": step,
                    "stairs": [], "rel_spec": float(opts["lu"]) if "lu" in opts else None,
                    "protegido": bool(pal_d.get("protegido")) or "protegido" in spec,
                    "prio": prio_new, "item_id": iid, "item": iid, "comp": comp, "chain": iid, "k": k,
                    "escalera": "escalera" in spec, "counts": role != "textura", "hero": False, "did": did,
                    "gain": 0.0, "sync_src": "cue" if e.get("_cue") else "event", "t_cue": float(e["t"]) if e.get("_cue") else None,
                    # t_visible: primer fotograma visible de la pieza (arranque del tween + retardo_ms de la paleta); la
                    # QA sfx.visual_sync mide contra él (17-oct-2026). Con `ancla_corte_s`, el corte de layout (18-oct)
                    "event_ref": ev_ref, "anclado_corte": anchored, "firma": bool(pal_d.get("firma")),
                    "textura": _texture_for(it, comp, e.get("kind"), tex_done),
                    "style": style, "why": f"animación: {comp}{'@' + style if style else ''} {e.get('kind')}"
                    + (f" (en el corte de layout de {anchored:.2f} s)" if anchored is not None else "")})
        if "escalera" in spec:
            stairs_open[(iid, e.get("kind"))] = out[-1]
    return out


def _onset_collision(wt: dict, t: float) -> bool:
    """¿El transitorio pisa voz? Arranque de palabra entre −10 y +50 ms, o una palabra que YA está sonando."""
    return any(-0.01 <= s - t <= 0.05 or (s < t < e - 0.02) for s, e in wt.values())


def _bright_layers(layers: list, c: dict, wt: dict) -> list:
    """Capa de brillo por voz (20-oct-2026, ver BRIGHT_*): a cada golpe del gesto (el principal y los de escalera) que
    es transitorio, pisa voz (`_onset_collision`) y tiene el centroide < BRIGHT_MAX_HZ, una capa «.bN» de brillo_1
    en su mismo instante, BRIGHT_REL_DB por debajo, hasta el golpe siguiente del gesto (≤ BRIGHT_MAX_S). Nada si el
    gesto ya lleva una capa aguda (≥ BRIGHT_HIGH_HZ: el brillo del encendido, el del visto, click_1)."""
    def cen(f_: dict) -> float:
        return float(f_.get("centroide_hz") or (sfxlib.lookup(str(f_.get("id", ""))) or {}).get("centroide_hz") or 0.0)

    if any(cen(f_) >= BRIGHT_HIGH_HZ for (f_, *_r) in layers):
        return layers
    hits = []                                            # (instante, índice de capa, nivel, extra)
    for li, (f_, rel_, _p, _m, _pre, _fi, _fo, *ex) in enumerate(layers):
        xl = ex[0] if ex else {}
        if li != 0 and xl.get("tag") != "e":
            continue
        t_h = float(xl["at"]) if "at" in xl else c["t"] + float(xl.get("dt", 0.0))
        hits.append((t_h, li, float(rel_), xl, f_))
    times = sorted(h[0] for h in hits)
    bright = None
    new = list(layers)
    for t_h, li, rel_, xl, f_ in hits:
        if _class_of(f_, "pop") not in TRANSIENTS or cen(f_) >= BRIGHT_MAX_HZ or not _onset_collision(wt, t_h):
            continue
        nxt = [t for t in times if t > t_h + 1e-6]
        max_b = min(BRIGHT_MAX_S, nxt[0] - t_h if nxt else BRIGHT_MAX_S)
        if max_b < 0.06:
            continue
        bright = bright or _mobile(_pal_file(BRIGHT_FILE))
        if bright is None:
            return layers
        # el brillo de un golpe de escalera va al nivel del de la cabeza (sin los −4 dB de la escalera): a −25,8 LU
        # no asomaba sobre la voz (logo.row de un vídeo de prueba, +2,5 dB en su mejor banda)
        rel_b = max(rel_, float(layers[0][1])) if xl.get("tag") == "e" else rel_
        new.append((bright, rel_b + BRIGHT_REL_DB, 0.0, max_b, None, 0.002, 0.03,
                    {"at": t_h, "ref": xl.get("ref") or c.get("event_ref"), "tag": "b", "brillo_de": li}))
        c.setdefault("brillo_por_voz", []).append(round(t_h, 3))
    return new


ACCENT_KINDS = {"pop", "ding", "riser", "riser_revelacion", "impact", "impacto_remate", "impacto_sub", "drop",
                "aparece_elemento_clave", "check", "sello", "stamp"}
ACCENT_CLASSES = {"riser", "ding", "impact"}
ACCENT_PRIO = 7                                      # revelación del registro (logo.reveal «name»)


def _is_protected_accent(c: dict, layers: list) -> bool:
    """Acento MARCADO que la guarda de palabra de `mix` no puede hundir (20-oct-2026, crítica de audio de un vídeo de prueba
    v002: la revelación quedó a −19,9 LU, −9,9 dB de lo pedido, por la guarda sobre «como»): una decisión `sfx`
    explícita de clase acento (`kind` riser/ding/pop/impacto…, o fichero de clase riser/ding/impacto), un remate (`hero`)
    o el golpe de revelación del registro (prio ≥ 7). Los clics, soplidos y texturas no."""
    if c.get("hero"):
        return True
    main = layers[0][0] if layers else None
    if c["rule"] == "anim":                          # acento del mapa con nivel declarado («lu=»): p. ej. el sello
        return c.get("role") == "acento" and c.get("rel_spec") is not None
    if c["rule"] == "explicit":
        return str(c.get("event")) in ACCENT_KINDS or _class_of(main, "") in ACCENT_CLASSES
    return c["rule"] == "class" and int(c.get("prio") or 0) >= ACCENT_PRIO and not c.get("group")


def _gap_shift(wt: dict, t: float, max_s: float = MOVE_MAX_S, body_s: float = 0.08) -> float | None:
    """Desplazamiento mínimo (|Δ| ≤ max_s, pasos de 5 ms) que deja el transitorio en un hueco de voz: sin palabra
    sonando en [t', t' + body_s] ni arranque a −10…+50 ms."""
    words = list(wt.values())
    # hacia atrás como mucho 20 ms: con el adelanto de 20 ms del evento, el sonido nunca va > 40 ms antes de la imagen
    for k in sorted(range(-4, int(max_s / 0.005) + 1), key=lambda k: (abs(k), k)):
        tt = t + k * 0.005
        if any(s < tt + body_s and e > tt for s, e in words):
            continue
        if any(-0.01 <= s - tt <= 0.05 for s, _ in words):
            continue
        return round(k * 0.005, 3)
    return None


def _cue_times(it, at: str) -> list[tuple[str, float]]:
    """Instantes del evento `at` en el item. Un item puede agrupar varias escenas de la misma plantilla con cues
    prefijadas (`s0_choose`, `s1_choose`…): cada una es una aparición. `cut` usa la cue si existe."""
    name = at.split(":", 1)[-1]
    if name == "sheen" and "sheen" not in it.cues and it.props.get("sheen", True) is not False:
        # sin evento ni cue: el instante por defecto del componente (+0,15 s: el brillo ya cruza lo visible)
        #   scene.capture3d: max(6 f, min(dur − 0,4, 0,65)) · media.capture_plane: 0,45 s
        dur_it = it.t1 - it.t0
        start = 0.45 if it.component == "media.capture_plane" else max(6 / 30, min(dur_it - 0.4, 0.65))
        if start + 0.5 < dur_it:
            return [("", it.t0 + start + 0.15)]
        return []
    if name == "hero":                                     # title.lockup_grid: la cue de la línea con role = hero
        hero = next((ln.get("cue") for ln in (it.props.get("lines") or []) if isinstance(ln, dict) and ln.get("role") == "hero"), None)
        if hero and hero in it.cues:
            return [("", float(it.cues[hero]))]
        return []
    if name in it.cues:
        return [("", float(it.cues[name]))]
    pref = sorted(((k[: -len(name) - 1], float(v)) for k, v in it.cues.items() if k.endswith("_" + name)),
                  key=lambda kv: kv[1])
    if pref:
        return pref
    if at == "enter":
        return [("", it.t0)]
    if at == "exit":
        return [("", it.t1)]
    if at in ("cut", "mid"):
        return [("", (it.t0 + it.t1) / 2)]
    return []


def _class_of(entry: dict | None, fallback: str) -> str:
    return (entry or {}).get("kind") or fallback


def _ok_file(f: dict, *, allow_toy: bool = False) -> bool:
    if f.get("excluido"):                            # retirado del catálogo (ataque saturado…)
        return False
    if not _mobile_ok(f):                            # 18-oct: centroide < 250 Hz por la cadena de móvil
        return False
    return allow_toy or not any(t in f["id"] for t in NO_TOY)


# ───────────────────────────── candidatos ─────────────────────────────
def _candidates(decisions, items, wt, fps, dur, drops) -> list[dict]:
    from cutkit.motion.registry import COMPONENTS
    cands: list[dict] = []
    # 1) decisiones explícitas
    for d in decisions:
        if getattr(d, "type", None) != "sfx":
            continue
        r = _resolve(d, wt, fps, dur)
        if not r:
            drops.append({"id": d.id, "why": "ancla sin resolver"}); continue
        p = d.params or {}
        kind = str(p.get("kind", "pop"))
        cands.append({"t": r[0] + float(p.get("offset", 0.0)), "rule": "explicit", "event": kind, "prio": 10,
                      "item_id": p.get("item"), "at": p.get("at", "enter"), "explicit_offset": float(p.get("offset", 0.0)),
                      "gain": float(p.get("gain_db", 0.0)), "did": d.id, "room": float(p.get("max_dur", 1.5)),
                      "hero": kind in HERO_EVENTS, "counts": kind not in ("tecleo", "click_ui", "type", "click"),
                      # opcionales: fichero del catálogo, duración máxima y nivel (LU respecto a la voz) propios
                      "file": p.get("file"), "max_s": p.get("max_s"), "rel": p.get("rel_lu"), "start_s": p.get("start_s"),
                      "why": (d.motive.text if getattr(d, "motive", None) else "decisión sfx")})
    # 2) eventos de componentes, con firma por plantilla. Una «aparición» es un item o una escena prefijada (s0_, s1_…)
    occ: list[tuple] = []                                # (t_inicio, item, prefijo)
    for it in items:
        if it.track == "caption":
            continue
        if it.props.get("sfx") is False:
            drops.append({"id": it.id, "why": "props.sfx = False"}); continue
        prefixes = sorted({k.split("_", 1)[0] for k in it.cues if k[:1] == "s" and "_" in k and k.split("_", 1)[0][1:].isdigit()},
                          key=lambda p: int(p[1:]))
        if prefixes:
            for p in prefixes:
                ts = [v for k, v in it.cues.items() if k.startswith(p + "_")]
                occ.append((min(ts), it, p))
        else:
            occ.append((it.t0, it, ""))
    chain: dict[str, tuple[float, int]] = {}             # plantilla → (último inicio, índice en la cadena)
    for t_start, it, pfx in sorted(occ, key=lambda o: o[0]):
        comp = it.component or ""
        spec = COMPONENTS.get(comp) or {}
        evs = spec.get("sfx", []) if isinstance(spec, dict) else getattr(spec, "sfx", [])
        if not evs:
            continue
        last = chain.get(comp)
        k = last[1] + 1 if last and t_start - last[0] < REPEAT_WINDOW_S else 0     # repetición dentro de 30 s
        chain[comp] = (t_start, k)
        did = it.decision_ids[0] if it.decision_ids else it.id
        # las transiciones pueden sonar hasta 0,2 s después de su corte aunque el item acabe antes
        t_end = max(it.t1, float(it.cues.get("cut", it.t1)) + 0.2) if it.track == "transition" else it.t1
        chain_key = it.id
        if it.track == "transition":                     # cadena del item que entra en el corte (whoosh → su gráfico)
            cut = float(it.cues.get("cut", (it.t0 + it.t1) / 2))
            nxt = [j for j in items if j.track in ("graphic", "broll") and abs(j.t0 - cut) <= 0.25]
            if nxt:
                chain_key = nxt[0].id
        for ev in evs:
            at, ekind = ev.get("at", "enter"), ev.get("kind", "pop")
            # 27-oct-2026 (en un vídeo de prueba) · `sfx_skip: ["class:<at>"]` quita el sonido del REGISTRO
            #   del componente en ese momento (p. ej. el «aparece_elemento_clave» de logo.reveal en `enter`); los
            #   «evento:n» siguen valiendo solo para el mapa de animaciones. Sin ese token, nada cambia
            if f"class:{at}" in (it.props.get("sfx_skip") or []):
                drops.append({"id": f"{it.id}:{at}", "why": f"sfx_skip class:{at}"}); continue
            hits = [(pp, tt) for pp, tt in _cue_times(it, at) if pp == pfx or not pfx]
            if pfx and not hits:
                hits = [(pfx, t_start)] if at == "enter" else []
            if not hits:
                continue
            t = hits[0][1] + float(ev.get("offset", 0.0))
            rel_over = (it.props.get("sfx_rel") or {}).get(at)          # `sfx_rel: {"hero": -15}`: nivel propio del item
            base = {"t": t, "did": did, "item": f"{it.id}{':' + pfx if pfx else ''}", "comp": comp, "k": k,
                    "t1": t_end, "gain": float(ev.get("gain_db", 0.0)), "hero": False, "counts": True,
                    "item_id": it.id, "at": at, "pfx": pfx, "win": (it.t0, it.t1) if it.track == "transition" else None,
                    "chain": chain_key,
                    # campos opcionales del registro: fichero fijo, tono, nivel y duración máxima
                    "file": ev.get("file"), "file_alt": ev.get("file_alt"), "rel": rel_over if rel_over is not None else ev.get("rel_lu"),
                    "max_s": ev.get("max_s"), "pitch": ev.get("pitch"), "layers": ev.get("layers") or [],
                    "hp_hz": ev.get("hp_hz"),
                    # declarado a mano en el registro (nivel, fichero o duración propios): el equilibrio no lo cede
                    "declared": any(k in ev for k in ("file", "rel_lu", "max_s", "prio", "signature"))}
            if ev.get("file") and (ekind not in ("whoosh",) or ev.get("hp_hz")):
                is_sig = bool(ev.get("signature"))              # p. ej. el «output» del pipeline cierra la escalera
                cands.append({**base, "rule": "fixed", "event": f"{comp}:{at}",
                              "prio": int(ev.get("prio") or (5 if is_sig else 4)),
                              "counts": not (ev.get("rel_lu") is not None and float(ev["rel_lu"]) <= SOFT_LU),
                              "group": f"firma:{ev['signature']}" if is_sig else None,
                              "why": f"{comp}: {at} (registro: {ev.get('file')} {float(ev.get('pitch') or 0):+g} st)"})
                continue
            if it.track == "transition":
                if comp in ("transition.light_leak", "transition.flash"):
                    cands.append({**base, "rule": "luz", "event": "transicion_luz", "prio": 6,
                                  "why": f"{comp}: aire que se corta en el destello"})
                elif comp == "transition.glitch":
                    cands.append({**base, "rule": "class", "event": "glitch", "prio": 5, "why": "glitch visual"})
                else:
                    cands.append({**base, "rule": "card", "event": "whip", "prio": 6, "why": f"{comp}: barrido"})
                continue
            if comp == "viz.decision" and at == "choose":
                cands.append({**base, "t": t - CHOOSE_LEAD_S, "rule": "choose", "event": "elige_opcion", "prio": 5,
                              "group": f"firma:{comp}", "pitch": float(min(k, 3)),
                              "why": f"viz.decision #{k + 1}: se resalta la opción (firma, {min(k, 3):+d} st)"})
                continue
            if ekind == "whoosh":
                # whoosh de entrada: solo en la primera aparición QUE SUENE (la «repetición < 30 s» se decide al
                # seleccionar, frente a lo ya elegido; antes se contaba también lo descartado)
                cands.append({**base, "rule": "card", "event": "tarjeta_entra", "prio": 5 if k == 0 else 4,
                              "entry_whoosh": at in ("enter", "input", "right", "left"), "pitch": 0.0,
                              "why": f"{comp}: entra deslizando ({at})"})
            elif ekind == "type":
                prompt = str(it.props.get("prompt") or it.props.get("typing") or "")
                if not prompt:
                    drops.append({"id": f"{it.id}:{at}", "why": "tecleo sin texto tecleándose en pantalla"}); continue
                tp = it.cues.get("prompt")
                if tp is None:
                    drops.append({"id": f"{it.id}:{at}", "why": "tecleo sin cue `prompt`"}); continue
                t_type = tp + 8 / fps                       # el componente empieza a escribir 8 fotogramas después
                cands.append({**base, "t": t_type, "rule": "type", "event": "tecleo", "prio": 2, "counts": False,
                              "room": min(1.5, len(prompt) / TYPE_CPS, it.t1 - t_type), "why": "se teclea el prompt"})
            elif ekind == "click":
                if not (it.props.get("cursor") or it.props.get("button") or it.props.get("click")):
                    # 20-oct: si el mapa de animaciones tiene gesto para ese momento (media.ui_focus `media.focus`),
                    # suena el del mapa; el clic del registro no es un descarte (el crítico lo leía como «sin SFX»)
                    mapped = [k for m in [_anim_map().get("eventos", {}).get(f"{comp}@{v}") or {} for v in _variants(it)]
                              + [(_anim_map().get("eventos") or {}).get(comp) or {}] for k in m
                              if str(k) == at or str(k).endswith("." + at)]
                    drops.append({"id": f"{it.id}:{at}", "why": f"click del registro sin cursor: suena el gesto del mapa ({mapped[0]})"
                                  if mapped else "click sin cursor ni botón visible"}); continue
                cands.append({**base, "rule": "class", "event": "click", "prio": 2, "counts": False, "why": "click de UI"})
            elif ekind in ("impact", "pop") and comp.startswith("cta."):
                # la CTA suena al ENTRAR el bloque (en el silencio antes de «Comenta»), no en la palabra clave
                cands.append({**base, "t": it.t0, "at": "enter", "match_related": True, "rule": "class",
                              "event": "aparece_elemento_clave", "prio": 6, "file": "pop_1",
                              "why": f"{comp}: entra la llamada a la acción"})
            elif ekind in ("impact", "pop"):
                tt = it.cues.get("name", t) if comp == "logo.reveal" else t
                cands.append({**base, "t": tt, "rule": "class", "event": "aparece_elemento_clave",
                              "prio": 7 if comp == "logo.reveal" else 4,
                              # en el CTA (a cámara, sin cama) el pop grave suena a chasquido de boca: pop tonal
                              "file": "pop_1" if comp.startswith("cta.") else None,
                              "why": f"{comp}: aparece el elemento clave" + (" (impacto solo con decisión)" if ekind == "impact" else "")})
            elif ekind == "ding":
                cands.append({**base, "rule": "class", "event": "check", "prio": 4, "why": f"{comp}: check"})
            elif ekind == "riser":
                cands.append({**base, "rule": "class", "event": "riser_revelacion", "prio": 6, "hero": True, "why": "revelación"})
            else:
                cands.append({**base, "rule": "class", "event": ekind, "prio": 3, "why": f"{comp}: {ekind}"})
    return cands


# ───────────────────────────── alineación con eventos VISUALES ─────────────────────────────
EVENT_LEAD_S = 0.02                                   # el SFX suena 20 ms antes del evento visual
AT_KEYS = {"enter": ["enter", "land", "appear"], "exit": ["exit", "leave"], "cut": ["cut"], "mid": ["cut", "mid"],
           "choose": ["choose", "chosen", "select", "pick", "highlight"], "input": ["input", "enter"],
           "right": ["right", "option"], "left": ["left", "option"], "name": ["name", "land", "reveal"], "keyword": ["keyword", "highlight"],
           "point": ["point", "arrow"], "prompt": ["type", "typing", "prompt"],
           "loop": ["type", "typing"], "append": ["append"], "transform": ["flip", "transform"],
           "output": ["option", "output"], "hero": ["word"], "sheen": ["sheen"], "focus": ["focus", "highlight"]}
NOT_TARGETS = ("layout.", "lockup.", "camera.")       # eventos que no son destino de un SFX de componente
SPECIFIC_ATS = {"sheen", "focus", "hero", "transform", "output", "choose"}
SOFT_LU = -18.0                                       # SFX a ≤ −18 LU (tic, aire): textura, no cuentan para la densidad


def _align_events(cands: list[dict], events: list[dict], drops: list[dict]) -> dict:
    """Mueve cada candidato al instante de su evento visual (−20 ms). Sin evento → se queda en la cue.
    Devuelve estadísticas {event, cue, sin_eventos_por_componente}."""
    stats = {"event": 0, "cue": 0, "missing": {}}
    used: set[int] = set()
    by_item: dict[str, list[tuple[int, dict]]] = {}
    for i, e in enumerate(events or []):
        if not str(e.get("kind", "")).startswith(NOT_TARGETS):
            by_item.setdefault(str(e.get("item")), []).append((i, e))
    for c in cands:
        c["t_cue"] = round(c["t"], 4)
        c["sync_src"] = "cue"
        pool = by_item.get(str(c.get("item_id")), []) if c.get("item_id") else []
        if c.get("match_related") and c.get("item_id"):          # también la entrada de su layout (`<item>_split`…)
            pool = pool + [(i, e) for i, e in enumerate(events or [])
                           if str(e.get("item", "")).startswith(str(c["item_id"]) + "_")]
        if c["rule"] == "explicit" and not pool:
            # decisión anclada a palabra: si hay un evento visual a ±0,25 s (aterrizaje, corte), manda el evento
            pool = [(i, e) for i, e in enumerate(events or []) if not str(e.get("kind", "")).startswith(NOT_TARGETS)
                    and abs(float(e["t"]) - c["t"]) <= 0.25]
        # 18-oct: sin `exit`: un SFX que pisa voz no se corre a la SALIDA del bloque (la elección de viz.decision caía en
        # su salida y «no cabía en el item»)
        c["item_event_ts"] = sorted(float(e["t"]) for _, e in pool if str(e.get("kind", "")) not in ("exit", "leave"))
        keys = AT_KEYS.get(c.get("at") or "enter", [c.get("at") or "enter"])
        if c["rule"] == "type":
            keys = AT_KEYS["prompt"]
        match = [(i, e) for i, e in pool if i not in used and any(k in str(e.get("kind", "")).lower() for k in keys)]
        if c["rule"] == "explicit" and not match:
            match = [(i, e) for i, e in pool if i not in used]
        if not match and c.get("item_id") and c.get("at") not in SPECIFIC_ATS:
            # el componente no emite ese tipo de evento: vale el evento visible más cercano del propio item (±0,6 s)
            # (no para momentos concretos como el brillo o el marcador: esos van a su cue)
            match = [(i, e) for i, e in pool if i not in used and abs(float(e["t"]) - c["t"]) <= 0.6]
        if match:
            i, e = min(match, key=lambda ie: abs(float(ie[1]["t"]) - c["t"]))
            if abs(float(e["t"]) - c["t"]) <= 2.0:
                used.add(i)
                lead = 0.0 if c["rule"] == "type" else EVENT_LEAD_S
                c["t"] = float(e["t"]) - lead + (c.get("explicit_offset", 0.0) if c["rule"] == "explicit" and c.get("item_id") else 0.0)
                c["sync_src"], c["event_ref"] = "event", {"kind": e.get("kind"), "t": float(e["t"]), "item": e.get("item")}
                if not c.get("item_id"):
                    c["item_id"] = e.get("item")
                stats["event"] += 1
                continue
        stats["cue"] += 1
        if c.get("comp"):
            stats["missing"][c["comp"]] = stats["missing"].get(c["comp"], 0) + 1
    return stats


# ───────────────────────────── selección equilibrada ─────────────────────────────
def count_gestures(items: list[tuple]) -> int:
    """Gestos que percibe el oído. `items` = (t, grupo, cadena). Una firma (grupo) cuenta una vez por racimo
    (< 10 s entre apariciones); SFX de una misma cadena (un componente, o la transición que entra en él) a < 0,6 s
    unos de otros cuentan uno."""
    pts: list[tuple[float, str | None]] = []
    for g in {it[1] for it in items if it[1]}:
        ts = sorted(it[0] for it in items if it[1] == g)
        clusters = [[ts[0]]]
        for a, b in zip(ts, ts[1:]):
            if b - a > 10.0:
                clusters.append([b])
            else:
                clusters[-1].append(b)
        pts += [(c[0], f"grupo:{g}") for c in clusters]
    pts += [(it[0], it[2] if len(it) > 2 else None) for it in items if not it[1]]
    pts.sort()
    n, last = 0, None
    for t, ch in pts:
        if last is not None and ch and ch == last[1] and t - last[0] < GESTURE_MERGE_S:
            last = (t, ch)
            continue
        n += 1
        last = (t, ch)
    return n


def _is_air(c: dict) -> bool:
    """Soplido/aire (transición, entrada de tarjeta, brillo) frente a transitorio (pop, tic, golpe)."""
    return c["rule"] in ("card", "luz") or bool(c.get("win")) or str(c.get("event", "")).endswith(":sheen")


def _min_gap(x: dict, c: dict) -> float:
    """Separación mínima entre dos SFX: 0,6 s entre partes de un mismo componente (transform → output, tríada) o
    entre un soplido y un transitorio (gestos distintos que no se enmascaran); 1,2 s en el resto."""
    if x.get("item_id") and x.get("item_id") == c.get("item_id") and x["rule"] != c["rule"]:
        return SAME_ITEM_GAP_S
    if _is_air(x) != _is_air(c):
        return SAME_ITEM_GAP_S
    return MIN_GAP_S


def _is_entry(c: dict) -> bool:
    """Entradas de gráficos (y transiciones): con la norma de diseño sonoro nunca las descarta el presupuesto."""
    return bool(c.get("win")) or c["rule"] == "card" or (c["rule"] == "anim" and c.get("role") in ("entrada", "textura")) \
        or (c["rule"] == "fixed" and c.get("declared"))


STAIR_MIN_S = 0.09                                   # dos golpes de una escalera, como mínimo a 3 f
STAIR_DB = -4.0                                      # los golpes que siguen a la cabeza, más bajos
STAIR_ST = [2, 0, -2, 0]                             # y con ±2 st (semitonos enteros), en este ciclo
HOOK_PROTECT_S = 8.0                                 # el gancho (t < 8 s) nunca pierde SFX por el tope total
LAYOUT_CUT_TOL_S = 0.1                               # un SFX a ≤ 0,1 s de un cambio de layout marca ese corte


def _select_every(cands: list[dict], dur: float, profile: dict, drops: list[dict],
                  layout_cuts: list[float] | None = None) -> list[dict]:
    """Norma «cada animación»: solo se descartan duplicados a < `dedupe_s` (queda el de más prioridad) y, por
    presupuesto (`max_per_min`, en gestos), lo que no es entrada; las texturas (≤ −18 LU) no cuentan.
    Después, la guarda local de racimos (≤ `racimo_1s_max` gestos en 1 s, `_cap_cluster`) y el tope TOTAL en gestos
    (18-oct-2026: 24/min; nunca el primer evento de un bloque, un corte de layout ni nada del gancho, `_cap_total`)."""
    ps = (profile or {}).get("sfx", {}) or {}
    budget = max(1, int(math.floor(float(ps.get("max_per_min", 24)) * dur / 60.0)))
    dedupe = float(_anim_map().get("dedupe_s", 0.25))
    chosen: list[dict] = []
    # a igualdad de prioridad, la firma declarada va primero (no la tapa otro SFX a < 0,25 s, p. ej. una luz en su corte)
    for c in sorted(cands, key=lambda c: (-(10 if c["rule"] == "explicit" else c["prio"]), not c.get("firma"), c["t"])):
        if -0.3 <= c["t"] < 0:                       # evento del primer fotograma (entrada en t≈0): suena en 0, no se pierde
            c["t"] = 0.0
        if c["t"] < 0 or c["t"] > dur:
            drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"], "why": "fuera del programa"})
            continue
        dup = [x for x in chosen if abs(x["t"] - c["t"]) < dedupe]
        if dup:
            drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"],
                          "why": f"duplicado a < {dedupe:g} s de {dup[0]['event']}"})
            continue
        # el presupuesto lo gastan solo los acentos/transiciones: las entradas ni se descartan ni lo consumen
        if not _is_entry(c) and c["counts"] and \
                count_gestures([(x["t"], x.get("group"), x.get("chain") or x.get("item_id"))
                                for x in chosen + [c] if x["counts"] and not _is_entry(x)]) > budget:
            drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"],
                          "why": f"presupuesto de densidad agotado ({budget})"})
            continue
        chosen.append(c)
    chosen = _cap_cluster(chosen, ps, drops, layout_cuts or [])
    return _cap_total(chosen, dur, ps, drops, layout_cuts or [])


def _n_files(c: dict, pals: dict) -> int:
    """Ficheros que suenan por un candidato (el principal + la capa de su paleta + la textura + las capas del
    registro). SOLO INFORMATIVO desde el 18-oct-2026: el tope cuenta GESTOS (un sonido con sus capas = 1)."""
    return 1 + (1 if (pals.get(c.get("palette")) or {}).get("capa") else 0) + (1 if c.get("textura") else 0) \
        + len(c.get("layers") or [])


def _block_seq(chosen: list[dict]) -> None:
    """Posición de cada SFX dentro de su bloque (item): `_seq` 0 = el que abre el bloque."""
    seq: dict[str, int] = {}
    for c in sorted(chosen, key=lambda c: c["t"]):
        blk = str(c.get("item_id") or c.get("item") or c.get("did") or id(c))
        c["_seq"] = seq.get(blk, 0)
        seq[blk] = c["_seq"] + 1


def _at_layout_cut(c: dict, layout_cuts: list[float]) -> bool:
    return bool(c.get("win")) or c["rule"] == "luz" or c.get("anclado_corte") is not None \
        or any(abs(c["t"] - lc) <= LAYOUT_CUT_TOL_S for lc in layout_cuts)


HOLE_MAX_S = 5.0                                     # el tope evita abrir tramos mudos más largos que esto
CLUSTER_WIN_S = 1.08                                 # 1 s de la QA + el corrimiento por consonante (≤ 60 ms) + margen


def _cap_cluster(chosen: list[dict], ps: dict, drops: list[dict], layout_cuts: list[float]) -> list[dict]:
    """Guarda local de racimos (18-oct-2026): nunca más de `racimo_1s_max` (2) GESTOS en 1 s, como la QA
    `sfx.cluster`; con el tope a 24/min es lo que evita los racimos encima de la voz. Se quita el de menos prioridad
    del racimo (a igualdad, el más interno de su bloque y el último); nunca explícitos, remates, transiciones ni la
    firma anclada a su corte. Si todo el racimo está protegido, se queda (y lo cuenta `LAST_CAP["racimos"]`)."""
    lim = int(ps.get("racimo_1s_max", 2))
    chosen = sorted(chosen, key=lambda c: c["t"])
    _block_seq(chosen)
    kept_over = 0

    def safe(c):
        return c["rule"] == "explicit" or c.get("hero") or bool(c.get("win")) or c["rule"] == "luz" \
            or c.get("anclado_corte") is not None or c.get("protegido")

    k = 0
    while k < len(chosen):
        grp = [c for c in chosen[k:] if c["t"] - chosen[k]["t"] <= CLUSTER_WIN_S]
        if len(grp) <= lim:
            k += 1
            continue
        pool = [c for c in grp if not safe(c)]
        if not pool:
            kept_over += 1
            k += 1
            continue
        c = min(pool, key=lambda c: (c["prio"], -c["_seq"], -c["t"]))
        drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"],
                      "why": f"racimo: más de {lim} gestos en 1 s (guarda local; queda lo de más prioridad)"})
        if c.get("stairs"):
            # una escalera no se pierde entera por su primer golpe: el siguiente pasa a cabeza (18-oct, ronda final)
            h = c["stairs"].pop(0)
            c["t"], c["event_ref"] = h["t"], h.get("event_ref") or c.get("event_ref")
            chosen.sort(key=lambda x: x["t"])
            k = max(0, k - 1)
            continue
        chosen.remove(c)
    LAST_CAP["racimos_protegidos"] = kept_over
    return chosen


def _cap_total(chosen: list[dict], dur: float, ps: dict, drops: list[dict], layout_cuts: list[float]) -> list[dict]:
    """Tope TOTAL en GESTOS (`max_per_min` del perfil: 24/min en Shorts desde el 18-oct-2026; antes 14 contando cada
    fichero). Un gesto es un sonido con sus capas: la capa de la paleta (el brillo de la firma), la textura y los
    `layers` del registro NO cuentan aparte y el tope nunca los quita (en v005 la firma `foco_oferta` perdía su
    brillo > 6 kHz y quedaba tapada por la voz). Como en la QA (sfx.density ≤ 0,40 gestos/s) y en el mezclador.
    Política (17-oct-2026; antes se quitaba a ciegas y caía el PRIMER SFX de cada secuencia):
      1. se quitan los eventos INTERNOS de cada bloque (k > 0 dentro de su item), de menos a más prioridad y, a
         igualdad, del último de la secuencia hacia atrás (se conserva el primero);
      2. nunca: el primer evento de un bloque, un corte de layout (transición, firma anclada o SFX a ≤ 0,1 s de un
         cambio de layout), nada del gancho (t < 8 s), las decisiones explícitas ni los remates. Si aun así se pasa,
         se queda (lo dice `LAST_REPORT["tope_total"]`)."""
    mpm = float(ps.get("max_per_min", 24))
    cap = max(1, int(math.floor(mpm * dur / 60.0)))
    pals = _anim_map().get("paletas") or {}
    why_cap = f"tope total de densidad ({cap} gestos = {mpm:g}/min)"
    chosen = sorted(chosen, key=lambda c: c["t"])
    _block_seq(chosen)

    def protected(c):
        return (c["rule"] == "explicit" or c.get("hero") or c["_seq"] == 0 or _at_layout_cut(c, layout_cuts)
                or c["t"] < HOOK_PROTECT_S or c.get("firma") or c.get("protegido")
                or str(c.get("group") or "").startswith("firma:"))

    def hole(c):
        """Hueco sin SFX que deja quitar `c` (del final del anterior, con su escalera, al siguiente)."""
        i = chosen.index(c)
        a = max([chosen[i - 1]["t"]] + [h["t"] for h in chosen[i - 1].get("stairs") or []]) if i > 0 else 0.0
        b = chosen[i + 1]["t"] if i + 1 < len(chosen) else dur
        return b - a

    # repetición de un mismo tipo de evento dentro de su bloque (0 = la primera vez que ese bloque hace ESO)
    kseq: dict[tuple, int] = {}
    for c in chosen:
        key = (str(c.get("item_id") or c.get("item") or c.get("did")), str(c.get("event")))
        c["_kseq"] = kseq.get(key, 0)
        kseq[key] = c["_kseq"] + 1

    # eventos internos de cada bloque (las capas no cuentan: son parte de su gesto). 18-oct: primero los que no abren
    # un hueco > HOLE_MAX_S (en v005 quedaban 9–13 s mudos), luego el de menos prioridad, después las REPETICIONES de
    # un mismo tipo de animación antes que la primera vez que el bloque la hace (el primer conector del circuito suena
    # aunque caigan los otros cuatro) y, a igualdad, el del tramo más denso y el más interno de su bloque
    while len(chosen) > cap:
        pool = [c for c in chosen if not protected(c)]
        if not pool:
            break
        c = min(pool, key=lambda c: (hole(c) > HOLE_MAX_S, c["prio"], c["_kseq"] == 0, round(hole(c), 1), -c["_seq"], -c["t"]))
        chosen.remove(c)
        drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"],
                      "why": f"{why_cap}: evento interno n.º {c['_seq'] + 1} de su bloque"})
    over = len(chosen) - cap
    LAST_CAP.update({"tope": cap, "gestos": len(chosen), "ficheros": sum(_n_files(c, pals) for c in chosen),
                     "por_encima": max(0, over),
                     "nota": "lo que queda por encima está protegido (primeros de bloque, cortes de layout, gancho, "
                             "explícitos)" if over > 0 else ""})
    return sorted(chosen, key=lambda c: c["t"])


LAST_CAP: dict = {}


def _select(cands: list[dict], dur: float, profile: dict, drops: list[dict], every: bool = False,
            layout_cuts: list[float] | None = None) -> list[dict]:
    if every:
        return _select_every(cands, dur, profile, drops, layout_cuts)
    ps = (profile or {}).get("sfx", {}) or {}
    budget = max(1, int(math.floor(float(ps.get("max_per_min", 6)) * dur / 60.0)))
    max_hits = int(ps.get("max_hits", 2))
    left = sorted(cands, key=lambda c: (-c["prio"], c["t"]))
    chosen: list[dict] = []
    over_budget: list[dict] = []

    def n_counted(sel):
        return count_gestures([(x["t"], x.get("group"), x.get("chain") or x.get("item_id")) for x in sel if x["counts"]])

    # 1.ª pasada (por tiempo): lo que tiene que sonar — transiciones, decisiones explícitas y SFX declarados en el
    # registro con prioridad ≥ 6 (acento héroe, CTA). Solo los frena la separación mínima entre ellos.
    must = sorted([c for c in left if c.get("win") or c["rule"] == "explicit" or (c["prio"] >= 6 and c.get("declared"))
                   or (c["prio"] >= 6 and c["rule"] in ("luz", "class") and c.get("file"))], key=lambda c: c["t"])
    for c in must:
        left.remove(c)
        clash = [x for x in chosen if abs(x["t"] - c["t"]) < _min_gap(x, c)]
        if clash and not (c["rule"] == "explicit" and all(x["rule"] != "explicit" for x in clash)):
            drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"],
                          "why": "a < 1,2 s de otro SFX obligatorio"})
            continue
        for x in clash:                                   # una decisión explícita desplaza a lo no explícito
            chosen.remove(x)
            drops.append({"id": x.get("item") or x.get("did"), "t": round(x["t"], 3), "event": x["event"],
                          "why": f"desplazado por la decisión explícita de {c['t']:.2f} s"})
        chosen.append(c)
    while left:
        def score(c):
            near = sum(1 for x in chosen if x["counts"] and not x.get("group") and abs(x["t"] - c["t"]) <= 10.0)
            same = any(x["event"] == c["event"] and abs(x["t"] - c["t"]) <= 15.0 and c["rule"] not in ("choose", "luz")
                       for x in chosen)
            # equilibrio: penaliza amontonar y premia rellenar tramos largos sin sonido (≥ 12 s del SFX más cercano)
            far = all(abs(x["t"] - c["t"]) >= 12.0 for x in chosen if x["counts"]) if chosen else False
            return c["prio"] - 1.5 * near - (0.5 if same else 0.0) + (1.0 if far else 0.0)
        left.sort(key=lambda c: (-score(c), c["t"]))
        c = left.pop(0)
        why = None
        if c["t"] < 0 or c["t"] > dur:
            why = "fuera del programa"
        elif any(abs(x["t"] - c["t"]) < _min_gap(x, c) for x in chosen):
            clash = [x for x in chosen if abs(x["t"] - c["t"]) < _min_gap(x, c)]
            # una transición desplaza a entradas de tarjeta de menos prioridad (los barridos suenan siempre)
            if c.get("win") and all(x["rule"] == "card" and not x.get("win") and x["prio"] < c["prio"]
                                    and not x.get("group") for x in clash):
                for x in clash:
                    chosen.remove(x)
                    drops.append({"id": x.get("item") or x.get("did"), "t": round(x["t"], 3), "event": x["event"],
                                  "why": f"desplazado por la transición de {c['t']:.2f} s"})
            else:
                why = "a < 1,2 s de otro SFX"
        elif c["counts"] and n_counted(chosen + [c]) > budget:
            why = f"presupuesto de densidad agotado ({budget})"
        elif c["hero"] and sum(x["hero"] for x in chosen) >= max_hits:
            why = "tope de remates"
        elif c.get("entry_whoosh") and any(x.get("entry_whoosh") and x.get("comp") == c.get("comp")
                                           and abs(x["t"] - c["t"]) < REPEAT_WINDOW_S for x in chosen):
            why = "whoosh de entrada solo en la primera aparición que suena (repetición < 30 s)"
        if why:
            drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"], "why": why})
            if why.startswith("presupuesto"):
                over_budget.append(c)
            continue
        chosen.append(c)
        if c.get("group"):                               # la firma entra entera (si respeta los 1,2 s)
            for m in [x for x in left if x.get("group") == c["group"]]:
                left.remove(m)
                if any(abs(x["t"] - m["t"]) < _min_gap(x, m) for x in chosen):
                    drops.append({"id": m.get("item"), "t": round(m["t"], 3), "event": m["event"], "why": "a < 1,2 s de otro SFX"})
                else:
                    chosen.append(m)
    # equilibrio final: ningún tramo > 20 s sin SFX si hay un candidato descartado solo por presupuesto dentro;
    # se cambia por el SFX menos prioritario de la zona más densa (nunca firmas, explícitos ni remates)
    for _ in range(4):
        ts = sorted(x["t"] for x in chosen if x["counts"])
        bounds = [0.0] + ts + [dur]
        a, b = max(zip(bounds, bounds[1:]), key=lambda ab: ab[1] - ab[0])
        if b - a <= BALANCE_MAX_GAP_S:
            break
        inside = [c for c in over_budget if a + MIN_GAP_S <= c["t"] <= b - MIN_GAP_S]
        if not inside:
            break
        add = min(inside, key=lambda c: (-c["prio"], abs(c["t"] - (a + b) / 2)))

        def crowd(x):
            others = [y["t"] for y in chosen if y is not x and y["counts"]]
            return min((abs(x["t"] - t) for t in others), default=99.0)
        swappable = [x for x in chosen if x["counts"] and not x.get("group") and x["rule"] != "explicit" and not x.get("declared")
                     and not x.get("win")                        # las transiciones nunca se ceden
                     and not x["hero"] and x["prio"] <= add["prio"] + 1 and not (a < x["t"] < b)]
        if not swappable:
            break
        out_ = min(swappable, key=lambda x: (x["prio"], crowd(x)))
        chosen.remove(out_)
        chosen.append(add)
        over_budget.remove(add)
        drops.append({"id": out_.get("item") or out_.get("did"), "t": round(out_["t"], 3), "event": out_["event"],
                      "why": f"cedido por equilibrio a {add['event']} en {add['t']:.2f} s (tramo de {b - a:.1f} s sin SFX)"})
    return sorted(chosen, key=lambda c: c["t"])


# ───────────────────────────── ficheros, tramos y niveles ─────────────────────────────
def _entry_span(f: dict) -> tuple[float, float, float]:
    """(media_start, dur, sync) del tramo útil (recorte si es un paquete)."""
    if f.get("recortes"):
        r = f["recortes"][0]
        return r["inicio_ms"] / 1000, (r["fin_ms"] - r["inicio_ms"]) / 1000, (r["sync_ms"] - r["inicio_ms"]) / 1000
    a, b = f.get("duracion_util_ms") or [0, int(float(f.get("duracion_s", 1.0)) * 1000)]
    sync = max(0.0, float(f.get("punto_sincronia_ms") or 0) - a) / 1000
    return a / 1000, (b - a) / 1000, sync


def _gain_offset(f: dict, rel_lu: float) -> float:
    """Desplazamiento para `AudioItem.gain_db`: `mix` calibra la clase a REL_VOICE_LU[kind] y suma esto."""
    return rel_lu - sfxlib.REL_VOICE_LU.get(f.get("kind") or "pop", -14.0)


def _event_rel(event: str, f: dict) -> float:
    ev = (sfxlib.catalog().get("eventos") or {}).get(event) or {}
    lv = ev.get("nivel_rel_voz_lu")
    if isinstance(lv, dict):
        lv = lv.get(f.get("tipo")) or lv.get("pico") or next(iter(lv.values()), None)
    if isinstance(lv, (list, tuple)) and len(lv) == 2:
        return float(sum(lv) / 2)
    return sfxlib.REL_VOICE_LU.get(f.get("kind") or "pop", -14.0)


def _pick_card(event: str, used: dict, comp: str, wt: dict, t: float) -> dict:
    """Whoosh corto (≤ 0,4 s, no grave) — misma plantilla, mismo fichero."""
    key = ("card", comp)
    if key in used:
        return used[key]
    pool = [f for f in sfxlib.candidates(event) if _ok_file(f)]
    pool = [f for f in pool if f.get("tipo") == "whoosh_corto" and float(f.get("centroide_hz") or 999) >= 300]
    if not pool:
        pool = [f for f in sfxlib.candidates("whoosh_corto") if float(f.get("centroide_hz") or 999) >= 300]
    taken = {v["id"] for kk, v in used.items() if kk[0] == "card"}
    free = [f for f in pool if f["id"] not in taken] or pool
    f = free[len(taken) % len(free)]
    used[key] = f
    return f


SAME_FILE_MIN_GAP_S = 20.0                           # nunca el mismo fichero dos veces en 20 s (salvo una firma)
SAME_FILE_PER_MIN = 4                                # = QA sfx.density misma_muestra_por_min_max (paletas de animación)
MAX_RISERS = 2                                       # remates de clase riser por vídeo


def _events_in_items(events: list[dict], items: list, fps: int, drops: list[dict] | None = None) -> list[dict]:
    """Solo los eventos que caen DENTRO de su item: [t0 − 1 f, t1] (20-oct-2026, crítica de audio de un vídeo de prueba
    v002: `flip`, `merge` y `lock` de flow.pipeline se emitían en 69,37–70,33 s, después de que el item acabara en
    68,27, y sonaban sobre la cara). Un evento de un item que no está en la timeline se queda (no se puede juzgar)."""
    win = {it.id: (float(it.t0), float(it.t1)) for it in items}
    tol = 1.0 / max(1, int(fps or 30))
    out = []
    for e in events or []:
        w = win.get(str(e.get("item")))
        try:
            t = float(e["t"])
        except (KeyError, TypeError, ValueError):
            out.append(e)
            continue
        if w is not None and (t < w[0] - tol - 1e-6 or t > w[1] + 1e-3):
            if drops is not None:
                drops.append({"id": str(e.get("item")), "t": round(t, 3), "event": str(e.get("kind")),
                              "why": f"evento fuera de su item ({w[0]:.2f}–{w[1]:.2f} s): no se ve, no suena"})
            continue
        out.append(e)
    return out


def plan(decisions: list, items: list, word_times: dict, fps: int, dur: float, profile: dict,
         events: list[dict] | None = None) -> list[AudioItem]:
    """Devuelve los `AudioItem` de SFX (kind="sfx") para `mix.render`. Ver reglas en el docstring del módulo.
    `events`: eventos visuales de `events.json` (ver `cutkit.audio.events`); sin ellos, cada SFX va a su cue."""
    global LAST_REPORT
    drops: list[dict] = []
    every = bool(((profile or {}).get("sfx") or {}).get("every_animation"))
    events = _events_in_items(events or [], items, fps, drops)
    cands = _candidates(decisions, items, word_times, fps, dur, drops)
    ev_stats = _align_events(cands, events or [], drops)
    layout_cuts = sorted({round(float(it.t0), 4) for it in items if it.track == "layout" and it.t0 > 0.05})
    if every:                                   # norma de diseño sonoro: cada animación visible lleva su sonido
        for c in cands:
            c.pop("entry_whoosh", None)         # también las entradas repetidas (cada tarjeta suena)
        anim = _event_candidates(events or [], items, cands, drops, layout_cuts=layout_cuts)
        ev_stats["anim"] = len(anim)
        for c in [c for c in cands if c.get("_sustituido")]:
            drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": c["event"],
                          "why": f"sustituido por el gesto del mapa de animaciones: {c['_sustituido']}"
                          if isinstance(c.get("_sustituido"), str) else "sustituido por el gesto propio del estilo"})
        cands = [c for c in cands if not c.get("_sustituido")] + anim
    LAST_CAP.clear()
    chosen = _select(cands, dur, profile, drops, every=every, layout_cuts=layout_cuts)
    out: list[AudioItem] = []
    used: dict = {}
    picker = sfxlib.Picker(seed="sfxplan")
    light_n = 0
    report = []
    history: list[tuple[str, float]] = []            # (fichero, t) ya colocados
    main_hist: list[tuple[str, float]] = []          # solo el fichero principal de cada gesto (como la QA sfx.repeat)
    anim_count: dict[str, int] = {}                  # rotación de ficheros por paleta
    anim_last: dict[tuple, dict] = {}                # último fichero por item y paleta (informativo)
    by_item_props = {it.id: (it.props or {}) for it in items}
    risers = [0]

    def fresh(f: dict, t: float) -> bool:
        if f is None:
            return False
        if _class_of(f, "") == "riser" and risers[0] >= MAX_RISERS:
            return False
        return not any(fid == f["id"] and abs(t - th) < SAME_FILE_MIN_GAP_S for fid, th in history)

    for n, c in enumerate(chosen):
        layers = []                                      # (entry, rel_lu, pitch, max_dur, pre_max, fade_in, fade_out)
        ev = c["event"]
        win = c.get("win")
        trans_max = (win[1] - win[0]) + 0.2 if win else None      # soplido de transición ≤ su ventana + 0,2 s
        if c["rule"] == "luz":
            fam = [sfxlib.lookup(i) for i in LIGHT_FAMILY]
            fam = [f for f in fam if f and _ok_file(f)]
            k0 = light_n % len(fam)
            order = fam[k0:] + fam[:k0]                  # rota la familia y salta lo usado en 20 s / risers agotados
            f = next((g for g in order if fresh(g, c["t"])), None)
            if f is None:
                drops.append({"id": c.get("item"), "t": round(c["t"], 3), "event": ev,
                              "why": "toda la familia de luz usada en los últimos 20 s o tope de risers"})
                continue
            pitch = [0.0, 1.0, -1.0][light_n % 3]; light_n += 1
            layers.append((f, _event_rel("transicion_luz", f), pitch, min(DEFAULT_MAX_S, trans_max or 9), None, 0.06, 0.05))
        elif c["rule"] == "anim":
            amap = _anim_map()
            pal = (amap.get("paletas") or {}).get(c["palette"]) or {}
            # «id#k» = recorte k de un paquete; fuera lo que no pasa la regla de centroide (18-oct) salvo excepción
            files = [g for g in (_pal_file(i) for i in pal.get("ficheros", [])) if g is not None and _ok_file(g)]
            if not files:
                drops.append({"id": c.get("item"), "t": round(c["t"], 3), "event": ev, "why": f"paleta {c['palette']} vacía"})
                continue
            n_pal = anim_count.get(c["palette"], 0)
            anim_count[c["palette"]] = n_pal + 1
            # rota la paleta y, con 24 gestos/min, salta el fichero que ya suena SAME_FILE_PER_MIN veces en este minuto
            # (como fichero principal de otro gesto: click_1 está en pop_suave, click_ui y resaltado); la QA
            # sfx.repeat cuenta igual, por gesto, minuto natural y sin la firma declarada (18-oct-2026)
            order = files[n_pal % len(files):] + files[:n_pal % len(files)]
            spare = [g for g in (_pal_file(i) for i in pal.get("reserva", [])) if g is not None and _ok_file(g)]
            f = next((g for g in order + spare if pal.get("firma") or sum(1 for h, th in main_hist if h == g["id"]
                                                                          and abs(c["t"] - th) < 60.0) < SAME_FILE_PER_MIN),
                     order[0])
            anim_last[(c["item_id"], c["palette"])] = f   # sin forzar el mismo fichero: rota 13 → 8 → 7 (15-oct)
            lo, hi = (pal.get("tono") or [0, 0])[:2]
            # semilla ESTABLE (18-oct: `hash()` de Python cambia en cada proceso y el nivel variaba ±1 LU entre pasadas)
            rng = __import__("numpy").random.default_rng(sfxlib._stable(c["item_id"], c["event"], round(c["t"], 2)) % (2 ** 32))
            # semitonos enteros e intervalos consonantes: los medios tonos y la escalera cromática desafinaban con la cama
            pitch = float(ESCALERA_ST[min(c["k"], len(ESCALERA_ST) - 1)]) + lo if c.get("escalera") \
                else float(round(float(rng.uniform(lo, hi))))
            if pal.get("paso_st") is not None and c.get("step"):   # firma con escalera entre items (ordinal 1…6)
                pitch = lo + (int(c["step"]) - 1) * float(pal["paso_st"])
            pitch = max(-MAX_PITCH_ST, min(MAX_PITCH_ST, pitch))
            # nivel propio del item por tipo de evento (`sfx_rel: {"word": -18}`)
            rel_item = ((by_item_props.get(c["item_id"]) or {}).get("sfx_rel") or {}).get(str(ev).split(":")[-1])
            base_lvl = float((amap.get("niveles") or {}).get(c["role"], -15.0))
            var = float(amap.get("variacion_lu", 1.0))
            rel_a = base_lvl + round(float(rng.uniform(-var, var)), 1) if c["role"] != "textura" else base_lvl
            if pal.get("nivel_lu") is not None:                  # firma: nivel fijo, igual en todas sus apariciones
                rel_a = float(pal["nivel_lu"])
                c["nivel_fijo"] = True                           # 18-oct: sin el −2 dB de `collide` (−12 salía a −14)
            if c.get("rel_spec") is not None:                    # nivel del mapa («lu=-16»)
                rel_a = float(c["rel_spec"])
            if rel_item is not None:
                rel_a = float(rel_item)
            eqm = amap.get("eq_movil") or POP_OVER_VOICE_EQ
            fp = _processed(f, hp=eqm.get("hp"), peak_hz=eqm.get("peak_hz"), peak_db=float(eqm.get("peak_db", 0.0)))
            if pal.get("pulsacion"):                      # tecleo: UNA pulsación real (≤ 0,1 s)
                ks = _keystrokes(f["id"])
                if ks:
                    k0 = ks[(c["k"] * 3 + n_pal) % len(ks)]
                    fp = {**fp, "_slice": (max(0.0, k0 - 0.005), float(pal.get("max_s", 0.1)), 0.005)}
            layers.append((fp, rel_a, pitch, float(pal.get("max_s", 0.3)),
                           WHOOSH_MAX_PRE_S if _class_of(f, "") == "whoosh" else None, 0.003, 0.03))
            capa = pal.get("capa")                       # 18-oct: la capa es parte del gesto; el tope ya no la quita
            if capa and _pal_file(capa.get("fichero", "")) is not None:   # capa (papel del sello, brillo del encendido)
                g = _processed(_pal_file(capa["fichero"]), hp=eqm.get("hp"), peak_hz=eqm.get("peak_hz"),
                               peak_db=float(eqm.get("peak_db", 0.0)))
                # `offset_s` (18-oct): la capa se adelanta o retrasa respecto al golpe (el aire de `juntar` picaba tarde)
                layers.append((g, rel_a + float(capa.get("rel", -5)), pitch, float(pal.get("max_s", 0.3)), None, 0.002, 0.03,
                               {"dt": float(capa.get("offset_s", 0.0)), "tag": "c"}))
            tex = (amap.get("texturas") or {}).get(c.get("textura") or "")
            if tex and _pal_file(tex.get("fichero", "")) is not None:  # textura (tics de reloj): nivel absoluto, sin tono
                g = _processed(_pal_file(tex["fichero"]), hp=eqm.get("hp"), peak_hz=eqm.get("peak_hz"),
                               peak_db=float(eqm.get("peak_db", 0.0)))
                x_tex = {"tag": "t"}
                if tex.get("inicio") == "palabra_siguiente":     # 18-oct: tras la cifra, nunca encima de ella
                    ws = sorted(word_times.values())
                    k_w = next((i for i, (s_, e_) in enumerate(ws) if e_ > c["t"] + 0.02), None)
                    if k_w is not None and k_w + 1 < len(ws) and ws[k_w + 1][0] - c["t"] <= 2.0:
                        x_tex["at"] = float(ws[k_w + 1][0])
                layers.append((g, float(tex.get("rel_lu", -20.0)), 0.0, float(tex.get("max_s", 1.5)), None,
                               float(tex.get("fade_in", 0.03)), float(tex.get("fade_out", 0.3)), x_tex))
            # escalera: cada golpe que sigue a la cabeza, mismo fichero, −4 dB y ±2 st, en su propio instante
            ks_all = _keystrokes(f["id"]) if pal.get("pulsacion") else []
            for j, h in enumerate(c.get("stairs") or [], 1):
                fh = fp
                if ks_all:
                    k1 = ks_all[(c["k"] * 3 + n_pal + j) % len(ks_all)]
                    fh = {**fp, "_slice": (max(0.0, k1 - 0.005), float(pal.get("max_s", 0.1)), 0.005)}
                ph = max(-MAX_PITCH_ST, min(MAX_PITCH_ST, pitch + STAIR_ST[(j - 1) % len(STAIR_ST)]))
                layers.append((fh, rel_a + float(pal.get("escalera_db", STAIR_DB)), ph, float(pal.get("max_s", 0.3)),
                               WHOOSH_MAX_PRE_S if _class_of(f, "") == "whoosh" else None, 0.003, 0.03,
                               {"at": float(h["t"]), "ref": h.get("event_ref"), "tag": "e"}))
        elif c["rule"] == "choose":
            f = sfxlib.lookup(CHOOSE_FILE)
            layers.append((f, CHOOSE_REL_LU, c.get("pitch", 0.0), DEFAULT_MAX_S, None, 0.0, 0.04))
        elif c["rule"] == "fixed":
            f = sfxlib.lookup(c["file"])
            if f is not None and not c.get("group") and not fresh(f, c["t"]) and c.get("file_alt"):
                f = sfxlib.lookup(c["file_alt"]) or f
            if f is None:
                drops.append({"id": c.get("item"), "t": round(c["t"], 3), "event": ev, "why": f"no existe {c['file']}"})
                continue
            rel_f = float(c["rel"]) if c.get("rel") is not None else _event_rel("aparece_elemento_clave", f)
            if c.get("hp_hz"):
                f = _processed(f, hp=float(c["hp_hz"]))
            layers.append((f, rel_f, float(c.get("pitch") or 0.0), float(c.get("max_s") or DEFAULT_MAX_S),
                           WHOOSH_MAX_PRE_S if _class_of(f, "") == "whoosh" else None, 0.0, 0.04))
            for lay in ([] if c.get("sin_capa") else c.get("layers") or []):   # capas declaradas (cuerpo grave bajo un golpe…)
                g = sfxlib.lookup(lay.get("file", ""))
                if g is not None:
                    layers.append((g, float(lay.get("rel_lu", rel_f - 6)), float(lay.get("pitch", 0.0)),
                                   float(lay.get("max_s", DEFAULT_MAX_S)), None, 0.0, 0.05))
        elif c["rule"] == "card" or ev in ("tarjeta_entra", "whip"):
            f = _pick_card(ev if ev in ("tarjeta_entra", "whip") else "tarjeta_entra", used, c.get("comp", ev), word_times, c["t"])
            if not fresh(f, c["t"]):                     # misma plantilla, mismo fichero… salvo que suene a copia
                alt = [g for g in sfxlib.candidates("whoosh_corto") if _ok_file(g) and float(g.get("centroide_hz") or 999) >= 300
                       and fresh(g, c["t"])]
                if alt:
                    f = alt[n % len(alt)]
            pitch = float(c["pitch"]) if c.get("pitch") is not None else float(min(c.get("k", 0), 3))
            rel_w = float(c["rel"]) if c.get("rel") is not None else _event_rel("tarjeta_entra", f)
            if every and not c.get("win") and c.get("rel") is None:   # norma de diseño sonoro: entradas a −16…−14 LU
                rel_w = float((_anim_map().get("niveles") or {}).get("entrada", -15.0))
                f = _processed(f, hp=POP_OVER_VOICE_EQ["hp"], peak_hz=POP_OVER_VOICE_EQ["peak_hz"], peak_db=POP_OVER_VOICE_EQ["peak_db"])
            layers.append((f, rel_w, pitch, min(WHOOSH_CARD_MAX_S, trans_max or 9, float(c.get("max_s") or 9)),
                           WHOOSH_MAX_PRE_S, 0.01, 0.05))
        elif ev in ("impacto_remate", "impact", "impacto_sub", "drop"):
            # solo llega aquí desde una decisión explícita: exige 150–400 ms sin voz antes y lleva capa media
            if _voice_at(word_times, c["t"] - 0.15, c["t"] - 0.005):
                drops.append({"id": c["did"], "t": round(c["t"], 3), "event": ev,
                              "why": "impacto sin 150 ms de silencio de voz antes → pop de elemento clave"})
                f = sfxlib.pick("aparece_elemento_clave", n)
                layers.append((f, _event_rel("aparece_elemento_clave", f), 0.0, DEFAULT_MAX_S, None, 0.0, 0.04))
            else:
                sub = picker.pick("impacto_remate")
                mid = sfxlib.lookup("firma_1")
                layers.append(({**sub, "_subgrave": True}, -6.0, 0.0, 1.5, None, 0.0, 0.4))   # sin paso alto
                layers.append((mid, -12.0, 0.0, DEFAULT_MAX_S, None, 0.0, 0.04))
        elif ev == "tecleo" or c["rule"] == "type":
            f = used.setdefault("type", next(f for f in sfxlib.candidates("tecleo") if _ok_file(f)))
            rel_t = float(c["rel"]) if c.get("rel") is not None else _event_rel("tecleo", f)
            if c.get("start_s") is not None:              # cada tecleo arranca en un punto distinto del fichero
                f = {**f, "_slice": (float(c["start_s"]), max(0.2, c.get("room", 1.5)), 0.005)}
            layers.append((f, rel_t, 0.0, max(0.2, c.get("room", 1.5)), None, 0.08, 0.08))
        elif c.get("file"):
            f = _pal_file(c["file"])                     # 20-oct: «id#k» = recorte k de un paquete, como en las paletas
            if f is None:
                drops.append({"id": c.get("did"), "t": round(c["t"], 3), "event": ev, "why": f"no existe {c['file']}"})
                continue
            rel_e = float(c["rel"]) if c.get("rel") is not None else _event_rel(ev, f)
            max_e = min(DEFAULT_MAX_S, float(c.get("max_s") or DEFAULT_MAX_S))
            if _class_of(f, "") == "riser":
                # 20-oct (un vídeo de prueba, riser subida_1 en el destello): el riser suena HASTA su punto de
                # sincronía (la cima/el corte en seco, 1,07 s) y un poco más; con el tope de 0,9 s acababa 165 ms antes
                # del corte y su cima no sonaba
                max_e = min(CLASS_MAX_S["riser"], max(max_e, _entry_span(f)[2] + RISER_TAIL_S))
            layers.append((f, rel_e, 0.0, max_e, None, 0.005, 0.05))
        else:
            try:
                f = picker.pick(ev)
                tries = 0
                while (not _ok_file(f, allow_toy=c["rule"] == "explicit" and "retro" in ev) or not fresh(f, c["t"])) \
                        and tries < 8:
                    f = picker.pick(ev); tries += 1
            except LookupError:
                drops.append({"id": c.get("did"), "t": round(c["t"], 3), "event": ev, "why": "sin fichero en el catálogo"})
                continue
            klass = _class_of(f, "pop")
            layers.append((f, _event_rel(ev, f), 0.0, CLASS_MAX_S.get(klass, DEFAULT_MAX_S), None, 0.005, 0.05))

        # la MISMA cadena para todo SFX (17-oct-2026): procesado de móvil (`eq_movil`) también en la CTA, la luz, la
        # elección, los fijos del registro, el tecleo y los del catálogo; salvo los subgraves de un impacto y lo que ya
        # trae su propio procesado (`hp_hz` del registro, entradas de tarjeta)
        # 18-oct: ficheros reservados (firma_1 = firma foco_oferta): fuera de su paleta suena el sustituto, sin tono
        sw_layers = []
        for (f_, rel_, pit_, *rest_) in layers:
            g_, sw_ = _reserved_swap(f_, c.get("palette"), ok=lambda fid: sum(
                1 for h, th in main_hist if h == fid and abs(c["t"] - th) < 60.0) < SAME_FILE_PER_MIN)
            if sw_:
                c.setdefault("reservado_sustituido", []).append(f_["id"])
                f_, pit_ = g_, 0.0
            sw_layers.append((f_, rel_, pit_, *rest_))
        layers = sw_layers
        layers = [((_mobile(f_) if f_ is not None and not f_.get("procesado") and not f_.get("_subgrave") else f_), *rest_)
                  for (f_, *rest_) in layers]
        # 20-oct: acento protegido (explícito de acento, remate, revelación o acento del mapa con nivel declarado): su
        # nivel no baja por consonante (−3/−2 dB) y la guarda de palabra de `mix` solo le recorta la banda 1–4 kHz
        protect = _is_protected_accent(c, layers)
        # norma «cada animación»: sincronía con el evento ±40 ms; un transitorio sobre el arranque de una palabra se
        # corre lo justo (≤ 40 ms) y, si no puede, baja 3 dB
        raise_to = None
        if c["rule"] == "anim" and layers and _class_of(layers[0][0], "pop") in TRANSIENTS + ("type",) \
                and any(-0.01 <= s_ - c["t"] <= 0.05 for s_, _ in word_times.values()):
            # el total respecto al evento (−20 ms de adelanto + corrimiento) se queda en ±40 ms: el corrimiento hacia
            # atrás llega a −15 ms (no −20): los eventos van en fotogramas de 1/30 s y −40 ms justos daban −40,3 (en un vídeo de prueba)
            er = c.get("event_ref") or {}
            ev_t = er.get("t_visible", er.get("t"))     # contra el primer fotograma visible (retardo_ms de la paleta)
            lo_s, hi_s = -0.015, 0.06
            if ev_t is not None:                         # el total respecto al evento, dentro de ±40 ms
                lo_s, hi_s = max(lo_s, float(ev_t) - 0.04 - c["t"]), min(hi_s, float(ev_t) + 0.04 - c["t"])
            shifts = sorted((k * 0.005 for k in range(-3, 13) if lo_s - 1e-9 <= k * 0.005 <= hi_s + 1e-9), key=abs)
            ok = next((sh for sh in shifts if not any(-0.01 <= s_ - (c["t"] + sh) <= 0.05 for s_, _ in word_times.values())), None)
            if ok is not None:
                c["t"] += ok
                c["consonant_shift"] = round(ok, 3)
            elif not protect:
                layers[0] = (layers[0][0], layers[0][1] - 3.0, *layers[0][2:])
                c["consonant_db"] = -3.0
        # sin realce de 3 kHz si el transitorio cae sobre el arranque de una palabra (competía con la consonante)
        if c["rule"] == "anim" and layers and any(-0.01 <= s_ - c["t"] <= 0.05 for s_, _ in word_times.values()):
            eqm_ = _anim_map().get("eq_movil") or POP_OVER_VOICE_EQ
            nl = []
            for (f_, *rest_) in layers:
                orig = sfxlib.lookup(f_["id"]) if f_.get("procesado") else None
                if orig is not None:
                    g_ = _processed(orig, hp=eqm_.get("hp"))
                    f_ = {**g_, "_slice": f_["_slice"]} if f_.get("_slice") else g_
                nl.append((f_, *rest_))
            layers = nl
            c["no_presence_boost"] = True
        if c["rule"] != "anim" and layers and _class_of(layers[0][0], "pop") in TRANSIENTS and _onset_collision(word_times, c["t"]):
            sh = _gap_shift(word_times, c["t"])
            # 20-oct (crítica de audio de un vídeo de prueba): una decisión EXPLÍCITA nunca salta al evento siguiente
            # del item (el clic de «Imagen» acababa sobre «Vídeo», 0,6 s después): se queda en su evento, sobre la voz,
            # con la capa de brillo (y a −12 LU si el director no fijó nivel)
            nxt = [] if c["rule"] == "explicit" else \
                [te - EVENT_LEAD_S for te in c.get("item_event_ts", []) if c["t"] + 0.05 < te - EVENT_LEAD_S <= c["t"] + 0.6
                 and not _onset_collision(word_times, te - EVENT_LEAD_S)]
            if sh is not None:
                c["t"] = c["t"] + sh
                c["moved_for_word"] = sh
            elif nxt:
                # al evento visual siguiente del item: vuelve a estar sincronizado (−20 ms) con algo que se ve
                c["moved_to_next_event"] = round(nxt[0] - c["t"], 3)
                c["t"] = nxt[0]
                c["event_ref"] = {"kind": "siguiente", "t": round(nxt[0] + EVENT_LEAD_S, 4), "item": c.get("item_id")}
            elif c["rule"] == "explicit" or (c["prio"] >= 7 and not c.get("group")):
                raise_to = ACCENT_OVER_VOICE_LU                 # acento pedido que no puede salir de la voz
            elif c.get("group") or c["prio"] >= 6:
                pass                                            # firma / declarado: se queda (pop sobre voz: brillo y −12 LU)
            else:
                drops.append({"id": c.get("item") or c.get("did"), "t": round(c["t"], 3), "event": ev,
                              "why": "pisa voz y no hay hueco a ≤ 150 ms ni evento visual siguiente en hueco"})
                continue
        # 20-oct: lo que el director fija en una decisión `sfx` (fichero y/o nivel) se respeta sobre la voz: ni se cambia
        # el fichero por el de más presencia ni se sube a −12 LU (antes se ignoraban `file` y `rel_lu`); la presencia
        # la da la capa de brillo (más abajo)
        dir_file = c["rule"] == "explicit" and bool(c.get("file"))
        dir_level = c["rule"] == "explicit" and c.get("rel") is not None
        if raise_to is not None and layers and c["rule"] == "explicit" and not dir_file:
            # sobre voz manda lo que asoma en el móvil: el candidato con más energía > 350 Hz por LU, ya procesado
            # 20-oct: sin ficheros reservados (elegía firma_1, la firma `foco_oferta`, por presencia)
            reserved = set((_anim_map().get("reservados") or {}).keys())
            pool = [g for g in sfxlib.candidates(ev) if _ok_file(g) and _class_of(g, "pop") in TRANSIENTS
                    and g["id"] not in reserved]
            best = max(pool, key=lambda g: _phone_presence(g["id"]), default=None)
            if best is not None:
                layers[0] = (best, *layers[0][1:])
        if raise_to is not None and dir_level:
            c["nivel_director"] = True                   # se queda donde lo puso el director (con la capa de brillo)
        elif raise_to is not None:
            layers = [(_processed(f_, hp=POP_OVER_VOICE_EQ["hp"], peak_hz=POP_OVER_VOICE_EQ["peak_hz"],
                                  peak_db=POP_OVER_VOICE_EQ["peak_db"]), max(r_, raise_to), *rest) if i_ == 0 else (f_, r_, *rest)
                      for i_, (f_, r_, *rest) in enumerate(layers)]
            c["raised_over_voice"] = raise_to
        elif c["rule"] != "anim" and layers and _class_of(layers[0][0], "pop") in TRANSIENTS and _over_voice(word_times, c["t"]) \
                and not any(-0.01 <= s_ - c["t"] <= 0.05 for s_, _ in word_times.values()):
            # pop sobre voz (también la firma): que asome en el móvil → paso alto 250 Hz, +4 dB a 3 kHz y −12 LU
            f0, r0_, *rest0 = layers[0]
            # los suaves (tic del marcador, ≤ −18 LU) ganan brillo pero siguen suaves: no compiten con la voz
            lvl = r0_ if not c.get("counts", True) or dir_level else max(r0_, POP_OVER_VOICE_LU)
            layers[0] = (_processed(f0, hp=POP_OVER_VOICE_EQ["hp"], peak_hz=POP_OVER_VOICE_EQ["peak_hz"],
                                    peak_db=POP_OVER_VOICE_EQ["peak_db"]), lvl, *rest0)
            c["pop_over_voice"] = True
        # 20-oct: capa de brillo (brillo_1) para los golpes que pisan voz con el centroide en su banda; no en la
        # firma, la elección, el tecleo, la luz, los de nivel fijo ni las paletas con `brillo_por_voz: false`
        pal_b = (_anim_map().get("paletas") or {}).get(c.get("palette") or "") or {}
        if layers and c["rule"] not in ("choose", "type", "luz") and not c.get("nivel_fijo") and not c.get("firma") \
                and not str(c.get("group") or "").startswith("firma:") and pal_b.get("brillo_por_voz", True) is not False:
            layers = _bright_layers(layers, c, word_times)
        gid = f"sfx_{n:02d}"                                 # 18-oct: un id por GESTO; capas «.cN», escalera «.eN»
        collide_li: dict[int, bool] = {}
        for li, (f, rel, pitch, max_d, pre_max, fin, fout, *ex_) in enumerate(layers):
            xl = ex_[0] if ex_ else {}
            t_l = float(xl["at"]) if "at" in xl else c["t"] + float(xl.get("dt", 0.0))
            ms, d_util, sync = f["_slice"] if f.get("_slice") else _entry_span(f)
            klass = _class_of(f, "pop")
            # sincronía medida: ataque en transitorios, pico suave en whoosh corto (la luz y los risers usan el
            # punto del catálogo: el corte del aire / la cima)
            if f.get("_slice"):
                pass                                            # pulsación: el ataque ya es el inicio del tramo
            elif c["rule"] != "luz" and klass in ("pop", "click", "ding", "tick", "glitch", "type", "retro"):
                sync = sfxlib.measure_sync(f["ruta"], ms, d_util, "onset")
            elif c["rule"] != "luz" and klass == "whoosh":
                sync = sfxlib.measure_sync(f["ruta"], ms, d_util, "peak")
            if pre_max is not None and sync > pre_max:          # que empiece como mucho `pre_max` antes
                ms, d_util, sync = ms + (sync - pre_max), d_util - (sync - pre_max), pre_max
            pre_luz = min(0.75, 0.7 * max_d) if c["rule"] == "luz" else None
            if pre_luz is not None and sync > pre_luz:          # aire de la luz: como mucho el 70 % antes del corte
                ms, d_util, sync = ms + (sync - pre_luz), d_util - (sync - pre_luz), pre_luz
            speed = 2 ** (pitch / 12)
            start = t_l - sync / speed
            if start < 0:                                       # 20-oct: un evento en el fotograma 0 (el gancho) perdía
                t_l, start = t_l - start, 0.0                   # el ataque al recortarse en 0: suena entero, ≤ 25 ms tarde
            dd = min(d_util / speed, max_d)
            if c.get("t1") is not None:                          # nunca más allá del item
                dd = min(dd, c["t1"] - start)
            dd = min(dd, dur - start)
            if dd < min(0.06, 0.8 * d_util / speed):
                drops.append({"id": c.get("did"), "t": round(c["t"], 3), "event": ev, "why": "no cabe en el item"})
                continue
            src_dur = dd * speed                                 # `dur` del AudioItem en tiempo del fichero
            # enmascaramiento: un transitorio encima del arranque de una palabra (consonante) suma pico → −2 dB
            # (no se aplica a la firma `choose` ni a decisiones explícitas: su nivel viene dado)
            # 18-oct: una paleta con `nivel_lu` declarado (la firma) queda exenta: su nivel es el declarado
            collide = c["rule"] not in ("choose", "explicit", "fixed") and c.get("raised_over_voice") is None \
                and not c.get("pop_over_voice") and not c.get("nivel_fijo") and not protect \
                and klass in TRANSIENTS and _onset_collision(word_times, t_l)
            collide_li[li] = collide
            if collide or (xl.get("tag") == "b" and collide_li.get(xl.get("brillo_de", -1))):
                rel -= 2.0                                       # el brillo baja con su golpe: sigue a −5 dB de él
            out.append(AudioItem(
                id=gid if li == 0 else f"{gid}.{xl.get('tag', 'c')}{li}", kind="sfx", path=f["ruta"], t0=round(t_l, 4),
                media_start=round(ms, 4),
                # sync_offset 0 = «usa el catálogo» en mix: por eso al menos 1e-4
                dur=round(src_dur, 4), sync_offset=max(1e-4, round(sync, 4)),
                gain_db=round(_gain_offset(f, rel) + c.get("gain", 0.0), 2),
                pitch=pitch, fade_in=fin if fin else 0.0, fade_out=min(fout, dd / 3), decision_ids=[c["did"]]))
            history.append((f["id"], t_l))
            if li == 0:
                main_hist.append((f["id"], t_l))
            if klass == "riser" and li == 0:
                risers[0] += 1
            report.append({"id": out[-1].id, "gesto": gid, "escalera": xl.get("tag") == "e",
                           "t0": round(t_l, 3), "event": ev, "file": f["id"], "rel_lu": rel,
                           "sync_src": c.get("sync_src"), "t_cue": c.get("t_cue"),
                           "event_ref": xl.get("ref") or c.get("event_ref"),
                           "moved_for_word": c.get("moved_for_word"), "moved_to_next_event": c.get("moved_to_next_event"),
                           "raised_over_voice": c.get("raised_over_voice"), "pop_over_voice": c.get("pop_over_voice"),
                           "processed": f.get("procesado"), "counts": c.get("counts", True),
                           "chain": c.get("chain") or c.get("item_id"), "role": c.get("role"), "palette": c.get("palette"),
                           "consonant_shift": c.get("consonant_shift"), "consonant_db": c.get("consonant_db"),
                           "item_id": c.get("item_id"),
                           # 18-oct: firma declarada (la QA sfx.repeat no la cuenta), anclada al corte de layout, textura,
                           # fichero reservado sustituido y nivel fijo de paleta (sin `collide`)
                           "firma": bool(c.get("firma")) or str(c.get("group") or "").startswith("firma:"),
                           "anclado_corte": c.get("anclado_corte"), "textura": c.get("textura"),
                           "reservado_sustituido": c.get("reservado_sustituido"), "nivel_fijo": c.get("nivel_fijo"),
                           "word_onset_collision": collide, "group": c.get("group"),
                           # 20-oct: capa de brillo por voz («.bN») y nivel que fijó el director (sin subir a −12 LU)
                           "brillo_por_voz": xl.get("tag") == "b" or None, "nivel_director": c.get("nivel_director"),
                           # 20-oct: acento marcado (explícito riser/ding/pop…, remate o revelación de prio ≥ 7): la
                           # guarda de palabra de `mix` solo le recorta la banda 1–4 kHz (ver mix._word_mask_guard)
                           "acento_protegido": protect or None,
                           "pitch": pitch, "dur": round(dd, 3), "layer": li, "why": c.get("why"), "prio": c["prio"]})
    # densidad en gestos: sin tecleo/click ni suaves; firmas por racimo; SFX a < 1,2 s = un gesto
    counted = count_gestures([(r["t0"], r["group"], r.get("chain")) for r in report if r["layer"] == 0 and r.get("counts", True)
                              and r["event"] not in ("tecleo", "click")])
    # 18-oct: GESTOS = sonidos con sus capas (lo que cuenta el tope del perfil, la QA sfx.density y el mezclador)
    n_gest = len({r["gesto"] for r in report})           # capas y golpes de escalera van dentro de su gesto
    n_stairs = sum(1 for r in report if r.get("escalera"))
    muted = [it.id for it in items if it.track != "caption" and (it.props or {}).get("sfx") is False]
    LAST_REPORT = {"chosen": report, "dropped": drops, "candidates": len(cands), "events": ev_stats,
                   "per_min": round(counted / (dur / 60), 2) if dur else 0.0,
                   "gestos": n_gest, "gestos_por_min": round(n_gest / (dur / 60), 2) if dur else 0.0,
                   "audio_items": len(out), "golpes_de_escalera": n_stairs,
                   "mudos_por_props_sfx_false": muted, "tope_total": dict(LAST_CAP)}
    return out


def align_version(slug: str, vid: str, extract: bool = True) -> dict:
    """Segunda pasada tras `build_project`: lee los eventos visuales del HTML (`events.json`; los extrae si
    `extract`), vuelve a planificar los SFX alineados a esos eventos y reescribe los SFX de `timeline.json`.
    Escribe `versions/<vid>/sfx_plan.json` (lo elegido, lo descartado y el origen de cada sincronía)."""
    import json
    from cutkit.compile import load_plan, load_profile, outro_decisions
    from cutkit.paths import version_dir
    from cutkit.spec import Timeline
    from . import events as evmod
    vd = version_dir(slug, vid)
    ev = evmod.extract_version(slug, vid) if extract or not (vd / "events.json").exists() else \
        json.loads((vd / "events.json").read_text())
    tl = Timeline.model_validate_json((vd / "timeline.json").read_text())
    pl = load_plan(slug, vid)
    prof = load_profile(pl.format, pl.outro_variant)
    decs = list(pl.decisions)
    if pl.outro and prof.get("outro", {}).get("enabled"):
        have = {d.id for d in decs}
        decs += [d for d in outro_decisions(prof) if d.id not in have]
    sfx_items = plan(decs, tl.items, tl.word_times, tl.fps, tl.duration, prof, events=ev.get("events", []))
    tl.audio = [a for a in tl.audio if a.kind != "sfx"] + sfx_items
    (vd / "timeline.json").write_text(tl.model_dump_json(indent=1))
    rep = {**LAST_REPORT, "events_file": {"ok": ev.get("ok"), "n": ev.get("n"), "error": ev.get("error")}}
    (vd / "sfx_plan.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return rep
