"""`python -m cutkit.qa run <slug> <vid> [--no-judge] [--keep-frames]`"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m cutkit.qa", description="QA de una versión de cutkit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="puertas + hojas de contacto + juez → qa.json")
    r.add_argument("slug")
    r.add_argument("vid")
    r.add_argument("--no-judge", action="store_true", help="sin juez Gemini")
    r.add_argument("--keep-frames", action="store_true", help="conserva qa_work/ (fotogramas)")
    a = ap.parse_args(argv)
    from . import run

    rep = run(a.slug, a.vid, judge=not a.no_judge, keep_frames=a.keep_frames)
    print(f"[{rep.verdict.upper()}] {rep.summary_es}")
    for i in rep.issues[:40]:
        span = f"{i.t0:7.2f}–{i.t1:7.2f}" if i.t0 is not None and i.t1 is not None else "   global      "
        print(f"  {i.id} {i.severity:5s} {i.check:26s} {span}  {i.message[:110]}")
    if len(rep.issues) > 40:
        print(f"  … y {len(rep.issues) - 40} más (qa.json)")
    return 1 if rep.verdict == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
