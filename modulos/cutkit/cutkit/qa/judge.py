"""Juez Gemini (vídeo + audio): rúbrica sí/no de `qa_motion_gates.yaml` + estilo de referencia resumido →
issues localizados en JSON. Sus issues entran como `warn` con `check="judge.*"`: el juez ORDENA, no decide
(regla de oro 7; qa.md §4: los VLM son ciegos a lo que dura < 1 s y tienden a preferir lo recargado).

Se sube un proxy 540×960 del render (mismo contenido, menos bytes) con la File API y se muestrea a 2 fps.
De pago (Gemini, con tu GEMINI_API_KEY del `.env` de la raíz): solo corre con `ck qa --judge` o `ck run --judge`.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from ..paths import cargar_entorno
from .config import GEMINI_MODEL, rhythm_profile, rubric, style_profile
from .context import QAContext, tc

PROMPT = """Eres el control de calidad de un editor de vídeo senior. Revisa este vídeo {formato} en español: un anuncio
o una pieza de marca para redes de una empresa de software o servicios. Míralo y escúchalo entero, como lo vería alguien
en el móvil con el sonido activado.

## Estilo de referencia
{estilo}

## Transcripción con tiempos (segundos de programa)
{transcripcion}

## Texto que el plan pone en pantalla (gráficos, con sus tiempos)
{texto_pantalla}

## Rúbrica (contesta cada pregunta con «si» o «no»; si es «no», da los tramos)
Para cada pregunta busca PRIMERO un contraejemplo concreto en el vídeo; contesta «si» solo si no encuentras ninguno.
El vídeo no está aprobado: tu trabajo es encontrar lo que un editor senior exigente cambiaría.
{rubrica}

## Qué devolver
SOLO JSON válido, sin texto alrededor, con esta forma:
{{"rubrica": [{{"id": "r01", "respuesta": "si|no", "tramos": [[t0, t1]], "nota": "una frase"}}],
  "issues": [{{"t0": 12.3, "t1": 14.0, "problema": "qué está mal, concreto", "severidad_sugerida": "alta|media|baja",
              "arreglo": "qué cambiarías (quitar, mover, acortar, cambiar layout…)", "rubrica_id": "r04"}}],
  "resumen": "dos frases"}}
Reglas: tiempos en SEGUNDOS con un decimal (no mm:ss). Solo problemas que se vean u oigan de verdad; si dudas, omite.
Máximo 15 issues, ordenados por gravedad. No premies lo recargado: restar suele mejorar. No opines de cosas que
duran menos de 1 s (no las ves bien)."""


def _style_summary(ctx: QAContext) -> str:
    prof = ctx.plan.style_profile if ctx.plan and ctx.plan.style_profile else ""
    name, ritmo = rhythm_profile(prof)
    lines = []
    if prof:
        lines.append(f"Perfil de estilo pedido para este vídeo: {prof}.")
    else:
        lines.append("Estilo por defecto: tipografía limpia y legible, colores de la marca del cliente con un solo acento, la "
                     "persona real a cámara, sin plantillas genéricas de IA. Hook claro en los 2 primeros segundos."
                     + (f" La referencia de ritmo medida es la del perfil «{name}»: úsala solo como orientación." if name else ""))
    p = style_profile(name) if name else {}
    est = p.get("estilo", {}) or {}
    if ritmo:
        iv = ritmo.get("intervalo_cambio_visual_s", {})
        lines.append(f"- Ritmo: cambio visual cada {iv.get('p50')} s de mediana (p90 {iv.get('p90')} s); "
                     f"{(ritmo.get('cortes_por_min') or {}).get('p50')} cambios/min. Recurso visual desde el fotograma 0.")
    tr = est.get("transiciones", {}) or {}
    if tr.get("gramatica"):
        lines.append(f"- Transiciones: {tr['gramatica']}.")
    sync = (est.get("sincronia_imagen_voz", {}) or {}).get("antelacion_ms", {})
    if sync:
        lines.append(f"- La imagen entra ~{sync.get('p50')} ms ANTES de la palabra que la dispara.")
    cap = (est.get("captions", {}) or {}).get("rail", {})
    if cap:
        lines.append(f"- Subtítulos: {cap.get('palabras_por_bloque', {}).get('p50')} palabras por bloque, en blanco, dentro de la "
                     "zona segura (nada de texto en el 35 % inferior ni en la columna derecha de botones).")
    cont = (p.get("criterio", {}) or {}).get("contencion", [])
    if cont:
        lines.append("- Contención (tan importante como editar): " + "; ".join(cont[:4]) + ".")
    lines.append("- Nada en pantalla puede afirmar algo que la voz no dice. Un único foco por momento. Opiniones y tesis, a cámara.")
    return "\n".join(lines)


def _transcript(ctx: QAContext, max_chars: int = 9000) -> str:
    wt = ctx.word_text()
    words = ctx.words_sorted()
    if not words:
        return "(sin transcripción en la timeline)"
    out, cur, t0 = [], [], None
    for wid, s, e in words:
        if t0 is None:
            t0 = s
        cur.append(wt.get(wid, "·"))
        if s - t0 > 4.0:
            out.append(f"[{t0:.1f}] " + " ".join(cur))
            cur, t0 = [], None
    if cur:
        out.append(f"[{t0:.1f}] " + " ".join(cur))
    txt = "\n".join(out)
    return txt[:max_chars]


def _screen_text(ctx: QAContext, max_chars: int = 3000) -> str:
    from .context import item_texts

    rows = []
    for it in sorted(ctx.items(["graphic", "overlay", "broll"]), key=lambda i: i.t0):
        tx = item_texts(it)
        if tx:
            rows.append(f"[{it.t0:.1f}–{it.t1:.1f}] " + " · ".join(tx))
    return ("\n".join(rows) or "(el plan no declara texto en gráficos)")[:max_chars]


def _proxy(ctx: QAContext) -> Path:
    if ctx.render.stat().st_size < 40e6:
        return ctx.render
    out = (ctx.work or ctx.vdir) / "judge_proxy.mp4"
    if not out.exists() or out.stat().st_mtime < ctx.render.stat().st_mtime:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ctx.render), "-vf", "scale=540:-2,fps=30", "-c:v", "libx264",
                        "-preset", "veryfast", "-crf", "26", "-c:a", "aac", "-b:a", "128k", str(out)], check=True)
    return out


def _secs(x: Any) -> float | None:
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        m = re.fullmatch(r"\s*(?:(\d+):)?(\d+(?:[.,]\d+)?)\s*", x)
        if m:
            return int(m.group(1) or 0) * 60 + float(m.group(2).replace(",", "."))
    return None


def _parse_json(txt: str) -> dict[str, Any]:
    txt = txt.strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.M).strip()
    try:
        return json.loads(txt)
    except Exception:
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else {}


def run(ctx: QAContext, model: str | None = None) -> dict[str, Any]:
    cargar_entorno()
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        ctx.notes.append("Juez Gemini omitido: falta GEMINI_API_KEY en el .env de la raíz.")
        return {"status": "skip", "reason": "sin GEMINI_API_KEY"}
    from google import genai
    from google.genai import types

    model = model or GEMINI_MODEL
    client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=600_000))
    t_start = time.time()
    src = _proxy(ctx)
    f = client.files.upload(file=str(src), config={"mime_type": "video/mp4"})
    for _ in range(120):
        f = client.files.get(name=f.name)
        st = getattr(f.state, "name", str(f.state))
        if st == "ACTIVE":
            break
        if st == "FAILED":
            ctx.notes.append("Juez Gemini: el procesado del vídeo falló.")
            return {"status": "error", "reason": "file FAILED"}
        time.sleep(2)
    rub = "\n".join(f"- {r['id']} (peso {r.get('peso', 1)}): {r['pregunta']}" for r in rubric()) or "- r01: ¿La edición está bien?"
    prompt = PROMPT.format(formato="vertical (9:16)" if ctx.is_short else "horizontal", estilo=_style_summary(ctx),
                           transcripcion=_transcript(ctx), texto_pantalla=_screen_text(ctx), rubrica=rub)
    video = types.Part(file_data=types.FileData(file_uri=f.uri, mime_type="video/mp4"),
                       video_metadata=types.VideoMetadata(fps=2))
    cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
    resp, last = None, None
    for attempt in range(6):
        try:
            resp = client.models.generate_content(model=model, contents=[video, prompt], config=cfg)
            break
        except Exception as exc:   # 503/429/500: reintentar con espera creciente
            last = exc
            code = int(getattr(exc, "code", 0) or 0)
            if code and code not in (408, 429, 500, 502, 503, 504):
                break
            time.sleep(min(60, 4 * 2 ** attempt))
    try:
        client.files.delete(name=f.name)
    except Exception:
        pass
    if resp is None:
        ctx.notes.append(f"Juez Gemini falló: {type(last).__name__}: {str(last)[:200]}")
        return {"status": "error", "reason": str(last)[:300]}
    data = _parse_json(resp.text or "")
    um = getattr(resp, "usage_metadata", None)
    usage = {"input_tokens": getattr(um, "prompt_token_count", None), "output_tokens": getattr(um, "candidates_token_count", None)}
    n = 0
    for it in data.get("issues", []) or []:
        t0, t1 = _secs(it.get("t0")), _secs(it.get("t1"))
        if t0 is None:
            continue
        t1 = t1 if t1 is not None and t1 >= t0 else t0 + 1.0
        rid = str(it.get("rubrica_id") or "general").strip() or "general"
        ctx.add(f"judge.{rid}", "warn", f"[juez] {it.get('problema', '').strip()}", t0, t1,
                {"severidad_sugerida": it.get("severidad_sugerida"), "arreglo": it.get("arreglo"), "modelo": model},
                ctx.blame(t0, t1), [{"op": "review", "suggestion": it.get("arreglo")}] if it.get("arreglo") else [])
        n += 1
    rub_ans = data.get("rubrica", []) or []
    weights = {r["id"]: r.get("peso", 1) for r in rubric()}
    yes = sum(weights.get(r.get("id"), 1) for r in rub_ans if str(r.get("respuesta", "")).lower().startswith("s"))
    tot = sum(weights.get(r.get("id"), 1) for r in rub_ans) or 1
    out = {"status": "ok", "model": model, "issues": n, "rubrica": rub_ans, "score_ponderado": round(yes / tot, 3),
           "resumen": data.get("resumen"), "usage": usage, "wall_s": round(time.time() - t_start, 1),
           "upload": src.name}
    (ctx.vdir / "qa_judge.json").write_text(json.dumps({**out, "raw": data}, ensure_ascii=False, indent=1), encoding="utf-8")
    return out
