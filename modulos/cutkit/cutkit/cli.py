"""CLI `ck` — editor de vídeo de Meta Ads OS.

Se ejecuta desde la raíz del producto con `uv run --project modulos/cutkit ck <subcomando>`.

Montaje directo de un anuncio (lo normal; sin red ni coste):
  ck anuncio clientes/acme/creativos/2026-11-10_demo/brutos/toma.mp4 --cliente acme --slug demo \\
     --hook "¿Sigues copiando leads a mano?" --cta "Reserva tu demo" --subtitulos toma.srt
  → clientes/acme/creativos/<fecha>_demo/demo_9x16.mp4, demo_4x5.mp4, demo.srt, qa_anuncio.json, LEEME.md

Montaje avanzado por decisiones ancladas a palabras (motion graphics con HyperFrames; necesita Node y el extra
`avanzado`):
  ck new <slug> --cliente acme --raw <vídeo.mp4> [--fmt anuncio]
  → (agente editor-video) escribe <proyecto>/edicion/versions/v001/plan.json usando `ck context <slug>`
  ck run <slug> v001          # assets → voz → compilar → render → QA → export
  ck edit <slug> v001 --op '{"op":"remove","select":{"at":32}}' --reason "quita el B-roll del 32"
  ck run <slug> v002

Utilidades: `ck instalar` (comprueba el entorno y prepara los SFX), `ck marca <cliente>` (marca resuelta).
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import typer
import yaml
from rich import print

from .paths import RAIZ, run_dir, version_dir

app = typer.Typer(help="cutkit: editor de vídeo para anuncios de Meta (montaje directo y montaje avanzado)",
                  add_completion=False, no_args_is_help=True)


def _salir(codigo: int, mensaje: str) -> None:
    print(f"[red]error[/] {mensaje}" if codigo else mensaje)
    raise typer.Exit(codigo)


# ───────────────────────────── montaje directo ─────────────────────────────
@app.command()
def anuncio(
    entrada: Path = typer.Argument(..., help="vídeo bruto (o ya cortado) con la toma principal"),
    slug: str = typer.Option(..., help="slug del proyecto (minúsculas y guiones): carpeta <fecha>_<slug>"),
    cliente: str = typer.Option(None, help="slug del cliente: marca de clientes/<cliente>/marca/ y entrega en su carpeta"),
    hook: str = typer.Option("", help="texto del hook en pantalla (≤ 2 s); recomendado ≤ 9 palabras"),
    cta: str = typer.Option(None, help="llamada a la acción final (por defecto, cta_por_defecto de la marca)"),
    subtitulos: str = typer.Option("auto", help="auto | no | local | openai (de pago) | ruta a .srt o .json de palabras"),
    formatos: str = typer.Option("9x16,4x5", help="formatos separados por comas (9x16, 4x5)"),
    quitar_silencios: bool = typer.Option(True, "--quitar-silencios/--sin-quitar-silencios"),
    procesar_voz: bool = typer.Option(True, "--procesar-voz/--sin-procesar-voz"),
    broll: list[str] = typer.Option([], help="B-roll a pantalla completa: INICIO-FIN:ruta (segundos del montaje final); repetible"),
    musica: str = typer.Option(None, help="pista propia o libre de derechos para publicidad (sin música por defecto)"),
    etiqueta_ia: bool = typer.Option(False, "--etiqueta-ia", help="rótulo de contenido generado con IA (vídeo híbrido)"),
    logo: str = typer.Option("cta", help="cta (con la llamada final) | siempre | no"),
    mayusculas: bool = typer.Option(None, "--mayusculas/--sin-mayusculas", help="por defecto, lo que diga la marca"),
    foco: str = typer.Option("auto", help="encuadre horizontal: auto (cara) | centro | 0–1"),
    marca: Path = typer.Option(None, help="otro marca.json (prevalece sobre el del cliente)"),
    nombre: str = typer.Option(None, help="nombre base de los archivos (p. ej. el del anuncio según la nomenclatura)"),
    fecha: str = typer.Option(None, help="AAAA-MM-DD de la carpeta del proyecto (por defecto, hoy)"),
    salida: Path = typer.Option(None, help="carpeta de salida (por defecto clientes/<cliente>/creativos/<fecha>_<slug>/)"),
    perfil: str = typer.Option("anuncio", help="perfil de recursos/perfiles/"),
    idioma: str = typer.Option("es", help="idioma de la transcripción"),
    como_json: bool = typer.Option(False, "--json", help="salida en JSON"),
):
    """Monta un anuncio 9:16 y 4:5 con hook, subtítulos, CTA, logo y QA técnica (FFmpeg, sin red)."""
    from . import sistema
    from .anuncio import ErrorUsuario, Opciones, _n, montar
    from .marca import MarcaInvalida
    from .paths import ProyectoNoEncontrado

    if not cliente and not salida and not os.environ.get("CUTKIT_RUNS"):
        _salir(1, "indica --cliente <slug> (entrega en su carpeta) o --salida <carpeta>")
    op = Opciones(entrada=entrada, slug=slug, cliente=cliente, hook=hook, cta=cta, subtitulos=subtitulos,
                  formatos=tuple(f.strip() for f in formatos.split(",") if f.strip()), quitar_silencios=quitar_silencios,
                  procesar_voz=procesar_voz, broll=list(broll), musica=musica, etiqueta_ia=etiqueta_ia, logo=logo,
                  mayusculas=mayusculas, foco=foco, marca=str(marca) if marca else None, nombre=nombre, fecha=fecha,
                  salida=salida, perfil=perfil, idioma=idioma)
    try:
        res = montar(op)
    except sistema.FaltaHerramienta as e:
        _salir(2, str(e))
    except (ErrorUsuario, MarcaInvalida, ProyectoNoEncontrado, ValueError) as e:
        _salir(1, str(e))
    if como_json:
        sys.stdout.write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
    else:
        color = {"pass": "green", "warn": "yellow", "fail": "red"}[res["veredicto"]]
        print(f"[{color}]{res['veredicto']}[/] {_n(res['duracion'])} s · silencios quitados {_n(res['silencios_quitados_s'])} s"
              f" · subtítulos: {res['subtitulos']} ({res['paginas_subtitulos']} páginas) · marca: {res['marca']}")
        for f in res["archivos"]:
            print(f"  {f}")
        for q in res["qa"]:
            for i in q["issues"]:
                print(f"  [{'red' if i['severidad'] == 'block' else 'yellow'}]{q['formato']} {i['check']}[/] {i['mensaje']}")
        for a in res["avisos"]:
            print(f"  [yellow]aviso[/] {a}")
    raise typer.Exit(0 if res["ok"] else 1)


@app.command("marca")
def marca_cmd(cliente: str = typer.Argument(None, help="slug del cliente (vacío = marca neutra)"),
              ruta: Path = typer.Option(None, help="otro marca.json")):
    """Muestra la marca resuelta (colores, tipografías, logo) y sus avisos."""
    from .marca import MarcaInvalida, cargar

    try:
        m = cargar(cliente, ruta)
    except MarcaInvalida as e:
        _salir(1, str(e))
    datos = dict(m.datos)
    datos["_tipografias_resueltas"] = {r: str(m.fuente(r)) for r in ("titulos", "texto")}
    datos["_logo_para_video"] = str(m.logo("claro") or m.logo("principal") or "")
    datos["_avisos"] = m.avisos
    sys.stdout.write(json.dumps(datos, ensure_ascii=False, indent=1) + "\n")


@app.command()
def instalar(whisper: bool = typer.Option(False, "--whisper", help="descarga el modelo de whisper.cpp (~550 MB, MIT)"),
             como_json: bool = typer.Option(False, "--json")):
    """Comprueba el entorno (FFmpeg con libass, Node para el modo avanzado, transcripción) y genera los SFX libres."""
    from . import sistema
    from .audio import sfx_sinteticos

    filas = []

    def fila(ident, ok, detalle, arreglo=""):
        filas.append({"id": ident, "ok": ok, "detalle": detalle, "arreglo": arreglo})

    for b in ("ffmpeg", "ffprobe"):
        fila(b, bool(shutil.which(b)), shutil.which(b) or "no encontrado", sistema.arreglo(b))
    if shutil.which("ffmpeg"):
        import subprocess

        filtros = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        fila("ffmpeg.libass", " ass " in filtros, "filtro ass (subtítulos y rótulos)",
             "instala un FFmpeg completo (con libass): " + sistema.arreglo("ffmpeg"))
        cods = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        fila("ffmpeg.libx264", " libx264 " in cods, "codificador H.264 (el que pide Meta)",
             "instala un FFmpeg completo (con libx264): " + sistema.arreglo("ffmpeg"))
    fila("node (modo avanzado)", bool(shutil.which("npx") or shutil.which("npx.cmd")), shutil.which("npx") or "no encontrado",
         sistema.arreglo("npx"))
    try:
        import playwright  # noqa: F401
        fila("playwright (modo avanzado)", True, "instalado")
    except ImportError:
        fila("playwright (modo avanzado)", False, "no instalado",
             "uv sync --project modulos/cutkit --extra avanzado && uv run --project modulos/cutkit playwright install chromium")
    cli = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
    fila("whisper.cpp (subtítulos gratis)", bool(cli), cli or "no encontrado", sistema.arreglo("whisper-cli"))
    from .analyze import WHISPER_MODELO, modelo_whisper_local

    if whisper:
        from .paths import DATOS

        destino = DATOS / "modelos" / WHISPER_MODELO
        if not destino.exists():
            import httpx

            destino.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{WHISPER_MODELO}"
            print(f"descargando {WHISPER_MODELO} …")
            tmp = destino.with_suffix(".parcial")
            with httpx.stream("GET", url, follow_redirects=True, timeout=600) as r:
                r.raise_for_status()
                with open(tmp, "wb") as fh:
                    for chunk in r.iter_bytes(1 << 20):
                        fh.write(chunk)
            tmp.replace(destino)
    try:
        fila("modelo whisper.cpp", True, str(modelo_whisper_local()))
    except RuntimeError as e:
        fila("modelo whisper.cpp", False, str(e), "uv run --project modulos/cutkit ck instalar --whisper")
    hechos = sfx_sinteticos.generar()
    fila("sfx", bool(hechos), f"{len(hechos)} efectos de sonido sintéticos (CC0, generados aquí)")
    if como_json:
        sys.stdout.write(json.dumps(filas, ensure_ascii=False, indent=1) + "\n")
    else:
        for f in filas:
            print(f"{'[green]✔[/]' if f['ok'] else '[yellow]·[/]'} {f['id']}: {f['detalle']}"
                  + ("" if f["ok"] or not f["arreglo"] else f"  → {f['arreglo']}"))
    obligatorio = {"ffmpeg", "ffprobe", "ffmpeg.libass"}
    raise typer.Exit(2 if any(not f["ok"] and f["id"] in obligatorio for f in filas) else 0)


# ───────────────────────────── montaje avanzado ─────────────────────────────
@app.command()
def new(slug: str, cliente: str = typer.Option(None, help="slug del cliente (dueño del proyecto)"),
        raw: Path = typer.Option(None, help="vídeo bruto o ya cortado (encuadre de cara completa); por defecto "
                                            "brutos/full.mp4 del proyecto"),
        raw_split: Path = typer.Option(None, help="la MISMA toma en 50/50 (cabeza y cuerpo abajo) para los split; "
                                                  "por defecto brutos/mid.mp4 del proyecto si existe"),
        fmt: str = typer.Option("anuncio", help="perfil: anuncio | organico"),
        style: str = typer.Option("", help="perfil de estilo de referencia (solo con petición expresa)"),
        request: str = typer.Option("", help="cita literal de quien pide ese estilo"),
        no_outro: bool = typer.Option(False, "--sin-cierre", help="sin el cierre (outro) del perfil"),
        prompt: str = typer.Option("", help="contexto para el ASR (temas y nombres propios)"),
        outro: str = typer.Option("", help="variante de cierre del perfil; vacío = la por defecto"),
        fecha: str = typer.Option(None, help="AAAA-MM-DD de la carpeta del proyecto")):
    """Ingesta + análisis de la fuente (y del cierre del perfil) y paquete de contexto para el director."""
    from .analyze import analyze, transcript_md
    from .compile import load_profile
    from .ingest import ingest_source
    from .paths import ProyectoNoEncontrado, proyecto_dir

    try:
        prof = load_profile(fmt, outro)
        base = None if os.environ.get("CUTKIT_RUNS") else proyecto_dir(slug, cliente, fecha, crear=bool(cliente))
    except (ProyectoNoEncontrado, ValueError) as e:
        _salir(1, str(e))
    vertical = prof["canvas"]["height"] > prof["canvas"]["width"]
    bd = base / "brutos" if base else None
    raw = raw or (bd / "full.mp4" if bd else None)
    raw_split = raw_split or ((bd / "mid.mp4") if bd and (bd / "mid.mp4").exists() else None)
    if not raw or not Path(raw).exists():
        _salir(1, f"no encuentro el bruto: {raw} (pasa --raw o deja el vídeo en brutos/full.mp4 del proyecto)")
    run_dir(slug, cliente, crear=bool(cliente))
    srcs = [ingest_source(slug, "main", raw, vertical=vertical)]
    o = prof.get("outro", {})
    if o.get("enabled") and not no_outro and o.get("path"):
        srcs.append(ingest_source(slug, "outro", RAIZ / o["path"], vertical=vertical))
    split_src = ingest_source(slug, "main_split", raw_split, vertical=vertical) if raw_split else None
    outro_split = (ingest_source(slug, "outro_split", RAIZ / o["split_path"], vertical=vertical)
                   if o.get("enabled") and not no_outro and o.get("split_path") else None)
    mi = analyze(slug, srcs, prompt=prompt)
    if os.environ.get("CK_ALINEAR") == "mms":
        try:
            from .analyze import align
            mi = align(slug, mi)
        except Exception as e:  # sin alineación forzada se usan los tiempos del ASR
            print(f"[yellow]aviso[/] alineación forzada no disponible: {e}")
    rd = run_dir(slug)
    extra = [x for x in (split_src, outro_split) if x]
    if extra:                                       # misma toma, mismos tiempos: sin transcripción propia
        mi.sources = [s for s in mi.sources if s.id not in {x.id for x in extra}] + extra
        (rd / "media_index.json").write_text(mi.model_dump_json(indent=1))
    (rd / "transcript.md").write_text(transcript_md(mi))
    ctx = rd / "context.md"
    if not ctx.exists():
        ctx.write_text(f"# {slug}\n\n- cliente: {cliente or '—'}\n- formato: {fmt}\n- perfil_estilo: {style or 'firma'}\n"
                       + (f"- petición literal: «{request}»\n" if request else "")
                       + f"- cierre: {'no' if no_outro or not o.get('enabled') else 'sí (perfil)'}\n")
    print(f"[green]ok[/] {len(mi.words)} palabras · {len(mi.pauses)} pausas · contexto en {rd}")


@app.command("outro")
def outro_cmd(slug: str, variant: str = typer.Argument(..., help="variante de cierre definida en el perfil"),
              fmt: str = "anuncio"):
    """Cambia el cierre de un vídeo ya ingerido: ingesta del cierre (y su 50/50), transcripción, pausas y cara."""
    import json as _json

    from .analyze import load_index, track_faces, transcribe_source, transcript_md
    from .compile import load_profile
    from .ingest import ingest_source

    o = load_profile(fmt, variant)["outro"]
    if not o.get("path"):
        _salir(1, f"el perfil «{fmt}» no define un cierre «{variant}» con `path`")
    rd = run_dir(slug)
    for sid in ("outro", "outro_split"):
        for f in (f"src_{sid}.mp4", f"src_{sid}.wav", f"asr_{sid}.json", f"align_{sid}.json", f"words_{sid}.json",
                  f"voice_{sid}.wav"):
            (rd / "media" / f).unlink(missing_ok=True)       # intermedios propios de cutkit: se regeneran
    mi = load_index(slug)
    vertical = load_profile(fmt)["canvas"]["height"] > load_profile(fmt)["canvas"]["width"]
    src = ingest_source(slug, "outro", RAIZ / o["path"], vertical=vertical, force=True)
    mi.sources = [s for s in mi.sources if s.id not in ("outro", "outro_split")] + [src]
    tp = RAIZ / Path(o["path"]).parent / "transcript.json"
    if tp.exists():                                 # ids estables del cierre: su plan.json se ancla a ellos (no re-ASR)
        from .spec import Word
        raw = _json.loads(tp.read_text())
        raw = raw.get("words", raw) if isinstance(raw, dict) else raw
        ows = [Word.model_validate({**w, "src": "outro"}) for w in raw]
    else:
        ows = transcribe_source(src, "")
    mi.words = [w for w in mi.words if w.src != "outro"] + ows
    mi.faces = {k: v for k, v in mi.faces.items() if k not in ("outro", "outro_split")}
    mi.faces["outro"] = track_faces(src)
    (rd / "media_index.json").write_text(mi.model_dump_json(indent=1))
    if o.get("split_path"):
        mi.sources.append(ingest_source(slug, "outro_split", RAIZ / o["split_path"], vertical=vertical, force=True))
        (rd / "media_index.json").write_text(mi.model_dump_json(indent=1))
    (rd / "transcript.md").write_text(transcript_md(mi))
    if not tp.exists():
        tp.write_text(_json.dumps({"words": [w.model_dump() for w in mi.words_of("outro")]}, ensure_ascii=False, indent=1))
    ws = mi.words_of("outro")
    print(f"[green]ok[/] cierre «{variant}»: {len(ws)} palabras · {src.duration:.2f} s")


@app.command()
def context(slug: str):
    """Paquete de contexto para el agente director: transcripción con ids, pausas, catálogo de componentes, reglas."""
    from .analyze import load_index, transcript_md
    mi = load_index(slug)
    out = [transcript_md(mi), "\n## Pausas medidas (≥0,25 s)"]
    out += [f"- {p.src} {p.s:.2f}–{p.e:.2f} ({p.e-p.s:.2f} s, {p.kind})" for p in mi.pauses if p.e - p.s >= 0.25]
    try:
        from .motion.registry import COMPONENTS
        out.append("\n## Componentes disponibles")
        for k, v in sorted(COMPONENTS.items()):
            v = v if isinstance(v, dict) else v.__dict__
            out.append(f"- `{k}` ({v.get('kind','')}) — cuándo: {v.get('when','')} · cuándo no: {v.get('when_not','')}")
    except Exception as e:
        out.append(f"(registro de componentes no disponible: {e})")
    out.append("\n## Reglas: modulos/cutkit/README.md · modulos/cutkit/cutkit/recursos/perfiles/*.yaml · "
               "modulos/cutkit/cutkit/recursos/motion_tokens.yaml")
    txt = "\n".join(out)
    (run_dir(slug) / "director_context.md").write_text(txt)
    print(txt)


@app.command("validate")
def validate(slug: str, vid: str):
    """Valida el plan (esquema + anclas + assets + afirmaciones con fuente)."""
    from .analyze import load_index
    from .compile import load_profile
    from .spec import EditPlan
    plan = EditPlan.model_validate_json((version_dir(slug, vid) / "plan.json").read_text())
    ids = {w.id for w in load_index(slug).words}
    bad = [d.id for d in plan.decisions if d.anchor.start not in ids or (d.anchor.end and d.anchor.end not in ids)]
    nosrc = [d.id for d in plan.decisions if d.type == "graphic" and not d.source]
    # el texto entra siempre animado: `enter: "cut"` está prohibido en componentes de texto
    cut_txt = [d.id for d in plan.decisions if d.type == "graphic"
               and str(d.params.get("component") or "").split(".")[0] not in ("media", "scene", "layout", "camera")
               and (d.params.get("props") or {}).get("enter") == "cut"]
    vetos = set(load_profile(plan.format).get("componentes_vetados") or [])
    vetados = [d.id for d in plan.decisions if str(d.params.get("component") or "") in vetos]
    print({"decisiones": len(plan.decisions), "anclas_rotas": bad, "graficos_sin_fuente": nosrc, "texto_sin_entrada": cut_txt,
           "componentes_vetados": vetados})
    # `props.sfx: false` en un bloque animado deja la animación muda (regla: cada animación visible lleva su sonido).
    # Para quitar un sonido concreto: `props.sfx_skip: ["evento:n"]` («evento:*» todos)
    from .audio.sfxplan import _anim_map
    from .motion.registry import COMPONENTS
    emap = _anim_map().get("eventos") or {}

    def _sounds(comp: str) -> bool:
        spec = COMPONENTS.get(comp) or {}
        reg = spec.get("sfx") if isinstance(spec, dict) else getattr(spec, "sfx", None)
        return bool(reg) or any(k == comp or k.startswith(comp + "@") for k in emap)
    mute = [d.id for d in plan.decisions if d.type == "graphic" and (d.params.get("props") or {}).get("sfx") is False
            and _sounds(str(d.params.get("component") or ""))]
    if mute:
        print({"aviso_bloques_animados_mudos": mute,
               "por_qué": "props.sfx: false deja mudo un bloque animado (lo marca la QA sfx.silent_block). Quita `sfx` y "
                          "usa `sfx_skip: [\"evento:n\"]` para un sonido concreto."})
    if bad or cut_txt or vetados:
        raise typer.Exit(1)


@app.command()
def assets(slug: str, vid: str, budget: float = typer.Option(0.0, help="tope de gasto en $ para assets de pago")):
    """Resuelve los assets que piden las decisiones + la cama musical del perfil (si hay pista)."""
    from .compile import load_profile
    from .spec import AssetManifest, AssetRequest, EditPlan  # noqa: F401
    plan = EditPlan.model_validate_json((version_dir(slug, vid) / "plan.json").read_text())
    reqs = []
    for d in plan.decisions:
        for r in d.params.get("asset_requests", []):
            reqs.append(AssetRequest.model_validate(r | {"for_decision": d.id}))
    rd = run_dir(slug)
    from .assets import resolve
    man = resolve(slug, reqs, rd, budget_usd=budget)
    prof = load_profile(plan.format, plan.outro_variant)
    if prof.get("music", {}).get("enabled") and "music_bed" not in man.assets:
        from .analyze import load_index
        from .audio import music
        from .spec import Asset
        mi = load_index(slug)
        dur = sum(s.duration for s in mi.sources) + 2
        try:
            m = music.ensure(prof["music"]["brief"], dur, rd / "media", track=(plan.tokens or {}).get("music_track"))
            man.assets["music_bed"] = Asset(id="music_bed", kind="audio", path=str(m["path"]), origin="music_gen"
                                            if m.get("origin") == "music_gen" else "library",
                                            license=m.get("license", ""), duration=m.get("duration"))
        except music.SinMusica as e:
            print(f"[yellow]aviso[/] sin cama musical: {e}")
    (rd / "assets.json").write_text(man.model_dump_json(indent=1))
    print(f"[green]ok[/] {len(man.assets)} assets · gasto {man.spent_usd:.2f} $")


@app.command()
def voice(slug: str):
    """Cadena de voz adaptativa sobre cada fuente → media/voice_<src>.wav."""
    from .analyze import load_index
    from .audio import voice as v
    rd = run_dir(slug)
    for s in load_index(slug).sources:
        out = rd / "media" / f"voice_{s.id}.wav"
        if s.id.endswith("_split") or (out.exists() and out.stat().st_mtime >= Path(s.audio).stat().st_mtime):
            continue                                # la 50/50 suena igual que su toma; lo ya procesado y al día se reutiliza
        r = v.process(s.audio, str(out))
        print(s.id, {k: r[k] for k in list(r)[:6]} if isinstance(r, dict) else r)


@app.command("compile")
def compile_cmd(slug: str, vid: str):
    """Compila el plan de una versión a timeline + proyecto HyperFrames (sin render)."""
    from .compile import compile_plan
    tl = compile_plan(slug, vid)
    print(f"[green]ok[/] {tl.duration:.2f} s · {len(tl.items)} items · {len(tl.audio)} pistas de audio")


@app.command()
def render(slug: str, vid: str, quality: str = "looks"):
    """Renderiza una versión compilada (HyperFrames + mezcla de audio) a render.mp4 y un proxy de 540 px."""
    from .render import render_all
    print(f"[green]máster[/] {render_all(slug, vid, quality=quality)}")


@app.command()
def qa(slug: str, vid: str, judge: bool = typer.Option(False, "--judge/--no-judge",
                                                        help="juez multimodal con Gemini (de pago, con tu GEMINI_API_KEY)")):
    """QA de una versión renderizada: zonas seguras, subtítulos, audio, motion y afirmaciones (sin red salvo --judge)."""
    from .qa import run as qa_run
    rep = qa_run(slug, vid, judge=judge)
    print(f"[bold]{rep.verdict}[/] — {rep.summary_es}")


@app.command()
def run(slug: str, vid: str, quality: str = "looks",
        judge: bool = typer.Option(False, "--judge/--no-judge", help="juez multimodal con Gemini (de pago)"),
        budget: float = typer.Option(0.0, help="tope de gasto en $ para assets de pago")):
    """assets → voz → compilar → render → QA → export."""
    assets(slug, vid, budget=budget)
    rd = run_dir(slug)
    from .analyze import load_index

    def stale(s):
        out = rd / "media" / f"voice_{s.id}.wav"
        return not out.exists() or out.stat().st_mtime < Path(s.audio).stat().st_mtime
    if any(stale(s) for s in load_index(slug).sources if not s.id.endswith("_split")):
        voice(slug)
    compile_cmd(slug, vid)
    render(slug, vid, quality=quality)
    qa(slug, vid, judge=judge)
    export(slug, vid)
    # con el render exportado, los intermedios sobran (siempre se regeneran al compilar). CK_KEEP_INTERMEDIOS=1 los deja.
    vd = version_dir(slug, vid)
    if os.environ.get("CK_KEEP_INTERMEDIOS") != "1" and (vd / "render.mp4").exists():
        for n in ("hf", "video_hf.mp4", "program.mp4", "program_split.mp4"):
            p = vd / n
            shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)


@app.command()
def edit(slug: str, vid: str, op: list[str] = typer.Option(..., help="op JSON (repetible)"), reason: str = ""):
    """Aplica ops sobre las decisiones → versión hija (no destructivo)."""
    from .edit import edit as do_edit
    child = do_edit(slug, vid, [json.loads(o) for o in op], reason)
    print(f"[green]versión hija[/] {child} (padre {vid}) → uv run --project modulos/cutkit ck run {slug} {child}")


@app.command()
def versions(slug: str):
    """Lista las versiones de un proyecto con su motivo."""
    for d in sorted((run_dir(slug) / "versions").iterdir()):
        p = d / "plan.json"
        if p.exists():
            j = json.loads(p.read_text())
            qa_p = d / "qa.json"
            v = json.loads(qa_p.read_text()).get("verdict") if qa_p.exists() else "-"
            print(f"{d.name}  padre={j.get('parent')}  decisiones={len(j.get('decisions', []))}  qa={v}  «{j.get('reason','')}»")


@app.command()
def export(slug: str, vid: str):
    """Copia el máster, el SRT y la timeline a la carpeta del proyecto (o a edicion/export/ fuera del producto)."""
    from .spec import Timeline
    vd = version_dir(slug, vid)
    rd = run_dir(slug)
    ex = rd.parent if rd.name == "edicion" else rd / "export"
    ex.mkdir(exist_ok=True)
    dst = ex / f"{slug}_{vid}.mp4"                       # enlace duro: el export no duplica el disco
    dst.unlink(missing_ok=True)
    try:
        dst.hardlink_to(vd / "render.mp4")
    except OSError:
        shutil.copy2(vd / "render.mp4", dst)
    tl = Timeline.model_validate_json((vd / "timeline.json").read_text())
    caps = [i for i in tl.items if i.track == "caption"]

    def ts(t):
        h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
    srt = "\n".join(f"{k+1}\n{ts(c.t0)} --> {ts(c.t1)}\n{' '.join(w['text'] for w in c.props['words'])}\n" for k, c in enumerate(caps))
    (ex / f"{slug}_{vid}.srt").write_text(srt)
    shutil.copy2(vd / "timeline.json", ex / f"{slug}_{vid}.timeline.json")
    print(f"[green]exportado[/] {ex}")


if __name__ == "__main__":
    app()
