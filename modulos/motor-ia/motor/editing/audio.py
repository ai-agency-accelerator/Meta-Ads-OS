"""Mezcla de audio: voz con «look de móvil», música con ducking, audio nativo de clips, SFX y loudness.

La voz sintética suena «demasiado limpia» (señal típica de IA). La cadena `PHONE_VOICE` añade lo que
tiene una grabación real con móvil: paso alto, presencia, compresión tipo AGC, sala pequeña y tono
de sala muy bajo. Todo con FFmpeg, coste ≈0.
"""

from __future__ import annotations

from pathlib import Path

from ..media import run
from ..models import AudioClip, Timeline
from ..store import ctx

PHONE_VOICE = (
    "highpass=f=95,lowpass=f=12500,"
    "equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=250:t=q:w=1.0:g=-2,"
    "acompressor=threshold=-20dB:ratio=3.2:attack=6:release=90:makeup=2,"
    "aecho=0.85:0.5:11|23:0.10|0.06"
)
STUDIO_VOICE = "highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120:makeup=1.5"


def mix(tl: Timeline, out_wav: Path, *, phone_look: bool = True, target_lufs: float = -14.0) -> Path:
    """Renderiza todas las pistas de audio de la timeline en un WAV estéreo 48 kHz normalizado."""
    dur = max(tl.duration, 0.1)
    inputs: list[str] = []
    filters: list[str] = []
    voice_labels: list[str] = []
    music_labels: list[str] = []
    other_labels: list[str] = []
    idx = 0
    has_room = False
    for clip in tl.audio:
        p = ctx().assets.abspath(clip.asset_id)
        inputs += ["-i", str(p)]
        lab = f"a{idx}"
        trim = ""
        if clip.loop_src:
            # tono de sala de la propia toma, en bucle con fundidos (sin caída a silencio digital bajo la tarjeta)
            n = int(clip.loop_src * 48000)
            trim = (f"atrim=start={clip.src_in:.3f}:end={clip.src_in + clip.loop_src:.3f},asetpts=PTS-STARTPTS,"
                    f"aresample=48000,afade=t=in:d=0.05,afade=t=out:st={max(clip.loop_src - 0.05, 0):.3f}:d=0.05,"
                    f"aloop=loop=-1:size={n},atrim=end={dur:.3f},")
        elif clip.src_in or clip.duration:
            end = f":end={clip.src_in + clip.duration:.3f}" if clip.duration else ""
            trim = f"atrim=start={clip.src_in:.3f}{end},asetpts=PTS-STARTPTS,"
        chain = f"[{idx}:a]{trim}aformat=sample_rates=48000:channel_layouts=stereo,volume={clip.gain_db}dB"
        if clip.fade_in:
            chain += f",afade=t=in:d={clip.fade_in:.3f}"
        if clip.fade_out and clip.duration:
            chain += f",afade=t=out:st={max(clip.duration - clip.fade_out, 0):.3f}:d={clip.fade_out:.3f}"
        if clip.role == "native":
            chain += ",highpass=f=80"  # quita el retumbe grave de la sala generada
        if clip.role in ("voice",):
            chain += "," + (PHONE_VOICE if phone_look else STUDIO_VOICE)
        if clip.role == "music":
            chain += f",afade=t=in:d=0.4,afade=t=out:st={max(dur - 1.2, 0):.3f}:d=1.2"
        delay_ms = int(round(clip.start * 1000))
        # FFmpeg 8: «adelay,apad,atrim=end» pierde el retardo (el clip acababa al principio de la pista y el resto mudo);
        # marcas de tiempo por muestra tras el retardo + relleno hasta la duración total → posición exacta
        chain += f",adelay=delays={delay_ms}:all=1,asetpts=N/SR/TB,apad=whole_dur={dur:.3f},atrim=end={dur:.3f}[{lab}]"
        filters.append(chain)
        (voice_labels if clip.role in ("voice", "native") else music_labels if clip.role == "music" else other_labels).append(lab)
        has_room = has_room or clip.role == "room"
        idx += 1

    if not has_room:
        # tono de sala casi inaudible: elimina el silencio digital perfecto entre frases (modo voz en off)
        inputs += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anoisesrc=color=pink:amplitude=0.0035:r=48000"]
        filters.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,lowpass=f=6000[room]")
        other_labels.append("room")
        idx += 1

    if voice_labels:
        filters.append(f"{''.join('[' + v + ']' for v in voice_labels)}amix=inputs={len(voice_labels)}:normalize=0[vox]")
    if music_labels:
        filters.append(f"{''.join('[' + m + ']' for m in music_labels)}amix=inputs={len(music_labels)}:normalize=0[mus0]")
        if voice_labels:
            filters.append("[vox]asplit=2[vox][voxsc]")
            filters.append("[mus0][voxsc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350:makeup=1[mus]")
        else:
            filters.append("[mus0]anull[mus]")
    bus = (["vox"] if voice_labels else []) + (["mus"] if music_labels else []) + other_labels
    filters.append(f"{''.join('[' + b + ']' for b in bus)}amix=inputs={len(bus)}:normalize=0[pre]")
    filters.append(f"[pre]loudnorm=I={target_lufs}:TP=-1.0:LRA=9,aresample=48000,atrim=end={dur:.3f}[out]")
    run(inputs + ["-filter_complex", ";".join(filters), "-map", "[out]", "-ac", 2, "-ar", 48000, "-c:a", "pcm_s16le", out_wav])
    return out_wav


def voice_clip(asset_id: str, start: float, gain_db: float = 0.0) -> AudioClip:
    return AudioClip(role="voice", asset_id=asset_id, start=start, gain_db=gain_db)
