"""cutkit.qa — puertas deterministas de la edición, hojas de contacto y juez Gemini (ordena, no decide).

Interfaz:
    from cutkit import qa
    report = qa.run("mi-video", "v001", judge=True)   # → QAReport; escribe qa.json, qa_sheet_*.jpg, qa_summary.md

CLI interno: `python -m cutkit.qa run <slug> <vid> [--no-judge]`. `CUTKIT_RUNS=<dir>` apunta a otra raíz de runs.
"""
from __future__ import annotations

__all__ = ["run"]


def run(slug: str, vid: str, judge: bool = True, keep_frames: bool = False):
    from .runner import run as _run

    return _run(slug, vid, judge=judge, keep_frames=keep_frames)
