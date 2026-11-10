"""Eventos VISUALES reales de un proyecto HyperFrames → `versions/<vid>/events.json` (para alinear SFX).

El runtime (`cutkit/motion/runtime.js`) expone `ctx.event(kind, t)`: cada componente lo llama en el instante en que
algo se ve (una opción que se resalta, un logo que aterriza, el corte de una transición) y se acumula en
`window.__ckEvents` = [{item, component, kind, t, …}] (t en segundos de programa, encajado a fotograma).
Aquí se carga `hf/index.html` en Chromium headless (Playwright, servido por HTTP local, sin descargar los MP4), se
espera al montaje (`window.__timelines.main`) y se leen. `sfxplan` alinea cada SFX a su evento (−20 ms) y, si no
hay evento para ese item, cae a las cues de la timeline.
"""
from __future__ import annotations

import functools
import http.server
import json
import threading
from pathlib import Path
from typing import Any


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a: Any) -> None:
        pass


class _Srv(http.server.ThreadingHTTPServer):
    def handle_error(self, request: Any, client_address: Any) -> None:
        pass


def extract(hf_dir: str | Path, out_json: str | Path | None = None, timeout_s: float = 90.0) -> dict:
    """Lee `window.__ckEvents` del proyecto HF. Devuelve {"events": [...], "n": int, "ok": bool, "error": str|None}
    y, si se da `out_json`, lo escribe."""
    from playwright.sync_api import sync_playwright
    hf_dir = Path(hf_dir)
    srv = _Srv(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(hf_dir)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    res: dict = {"events": [], "n": 0, "ok": False, "error": None, "source": str(hf_dir / "index.html")}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            pg = b.new_page(viewport={"width": 540, "height": 960})
            pg.route("**/*.{mp4,mov,webm,m4a,mp3,wav}", lambda r: r.abort())     # el montaje no necesita el vídeo
            pg.goto(url, wait_until="domcontentloaded", timeout=timeout_s * 1000)
            pg.wait_for_function("() => window.__timelines && window.__timelines.main && Array.isArray(window.__ckEvents)",
                                 timeout=timeout_s * 1000)
            ev = pg.evaluate("() => JSON.parse(JSON.stringify(window.__ckEvents || []))")
            b.close()
        res.update({"events": ev, "n": len(ev), "ok": True})
    except Exception as e:                                  # noqa: BLE001 — sin eventos: sfxplan cae a cues
        res["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    finally:
        srv.shutdown()
    if out_json is not None:
        Path(out_json).write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res


def extract_version(slug: str, vid: str) -> dict:
    """`clientes/<cliente>/creativos/<fecha>_<slug>/edicion/versions/<vid>/hf` → `versions/<vid>/events.json`."""
    from cutkit.paths import version_dir
    vd = version_dir(slug, vid)
    return extract(vd / "hf", vd / "events.json")


def load(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text()).get("events", [])
    except Exception:                                       # noqa: BLE001
        return []
