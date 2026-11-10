"""cutkit.audio — voz, música, SFX y mezcla/máster. Mide antes de decidir; nunca `loudnorm`.

    voice.process(src, out_wav, ref=None) -> dict   cadena adaptativa: paso alto · (sin reductor de ruido) · nivelador ·
                                                    compresor+expansor · EQ parcial · de-esser · −16,5 LUFS (in/out)
    music.ensure(brief, duration, out_dir) -> dict  pista del cliente (marca/musica/) o fijada; Lyria solo con
                                                    CK_MUSICA_IA=1 (de pago) → pulso/compases → recorte o bucle en
                                                    downbeat; sin pista → music.SinMusica
    sfx.catalog() / sfx.pick(kind, seed) / sfx.Picker(seed)
                                                    datos/sfx/catalogo.yaml (biblioteca sintética CC0 + CK_SFX_DIR);
                                                    kind = clase (whoosh…), tipo fino o evento (tarjeta_entra…);
                                                    determinista, sin repetir seguido
    sfx_sinteticos.generar()                        sintetiza la biblioteca CC0 (lo llama `ck instalar`)
    mix.render(timeline, out_dir, profile=None) -> dict   xfade 10 ms + room tone · cama −18 LU (>300 Hz) con reentradas
                                                    al pulso · SFX en LU rel. voz · −14 LUFS / −1,5 dBTP sin loudnorm
    sfxplan.plan(…, events=None) / sfxplan.align_version(slug, vid)   SFX por prioridad, alineados a eventos visuales
    events.extract_version(slug, vid)               window.__ckEvents del HTML (Playwright) → versions/<vid>/events.json
Perfil: mix.PROFILE ← timeline.style["audio"] ← perfil (`recursos/perfiles/`).
"""
from . import events, mix, music, sfx, sfx_sinteticos, sfxplan, voice
from .mix import render
from .music import SinMusica, ensure
from .sfx import catalog, pick
from .voice import process

__all__ = ["voice", "music", "sfx", "sfx_sinteticos", "sfxplan", "events", "mix", "process", "ensure", "SinMusica",
           "catalog", "pick", "render"]
