"""Edición no destructiva: ops sobre las decisiones del plan → versión hija (como `tk spec edit`).

Ops (JSON):
  {"op":"remove", "select":{...}}                       quita decisiones (ids o selector semántico)
  {"op":"set", "select":{...}, "path":"params.props.title", "value":…}
  {"op":"retime", "select":{...}, "lead":-0.2, "tail":0.3}
  {"op":"add", "decision":{...Decision...}}
  {"op":"lock"|"unlock", "select":{...}}
  {"op":"outro", "value":false}
Selector: {"id":"d_012"} · {"type":"camera"} · {"component":"camera.punch_in"} · {"at": 32.0} (segundo de programa de
la versión que se estaba viendo) · {"word":"main_w0186"} · combinables (AND).
"""
from __future__ import annotations

import copy
import json
from typing import Any

from .paths import run_dir, version_dir
from .spec import Decision, EditPlan, Timeline


def _match(d: Decision, sel: dict, tl: Timeline | None) -> bool:
    if "id" in sel and d.id != sel["id"] and d.id not in (sel["id"] if isinstance(sel["id"], list) else []):
        return False
    if "type" in sel and d.type != sel["type"]:
        return False
    if "component" in sel and d.params.get("component") != sel["component"]:
        return False
    if "word" in sel and sel["word"] not in (d.anchor.start, d.anchor.end):
        return False
    if "at" in sel:
        if not tl:
            return False
        its = [i for i in tl.items if d.id in i.decision_ids]
        if not any(i.t0 - 0.05 <= float(sel["at"]) <= i.t1 + 0.05 for i in its):
            return False
    return True


def _set_path(obj: dict, path: str, value: Any) -> None:
    keys = path.split(".")
    for k in keys[:-1]:
        obj = obj.setdefault(k, {})
    obj[keys[-1]] = value


def apply_ops(plan: EditPlan, ops: list[dict], tl: Timeline | None = None) -> tuple[EditPlan, list[str]]:
    p = copy.deepcopy(plan)
    log = []
    for op in ops:
        kind = op["op"]
        sel = op.get("select", {})
        targets = [d for d in p.decisions if sel and _match(d, sel, tl)]
        if kind == "remove":
            ids = {d.id for d in targets if not d.locked}
            p.decisions = [d for d in p.decisions if d.id not in ids]
            log.append(f"remove {sorted(ids)}")
        elif kind == "set":
            for d in targets:
                dd = d.model_dump()
                _set_path(dd, op["path"], op["value"])
                p.decisions[p.decisions.index(d)] = Decision.model_validate(dd)
            log.append(f"set {op['path']} en {[d.id for d in targets]}")
        elif kind == "retime":
            for d in targets:
                if "lead" in op:
                    d.anchor.lead = op["lead"]
                if "tail" in op:
                    d.anchor.tail = op["tail"]
            log.append(f"retime {[d.id for d in targets]}")
        elif kind == "add":
            p.decisions.append(Decision.model_validate(op["decision"]))
            log.append(f"add {op['decision']['id']}")
        elif kind in ("lock", "unlock"):
            for d in targets:
                d.locked = kind == "lock"
            log.append(f"{kind} {[d.id for d in targets]}")
        elif kind == "outro":
            p.outro = bool(op["value"])
            log.append(f"outro={p.outro}")
        else:
            raise ValueError(f"op desconocida: {kind}")
    return EditPlan.model_validate(p.model_dump()), log


def next_vid(slug: str) -> str:
    vs = sorted(d.name for d in (run_dir(slug) / "versions").iterdir() if d.is_dir() and d.name.startswith("v"))
    n = int(vs[-1][1:]) + 1 if vs else 1
    return f"v{n:03d}"


def edit(slug: str, vid: str, ops: list[dict], reason: str = "") -> str:
    vd = version_dir(slug, vid)
    plan = EditPlan.model_validate_json((vd / "plan.json").read_text())
    tl = Timeline.model_validate_json((vd / "timeline.json").read_text()) if (vd / "timeline.json").exists() else None
    new, log = apply_ops(plan, ops, tl)
    child = next_vid(slug)
    new.version, new.parent, new.reason = child, vid, reason
    cd = version_dir(slug, child)
    (cd / "plan.json").write_text(new.model_dump_json(indent=1))
    (cd / "diff.json").write_text(json.dumps({"parent": vid, "ops": ops, "log": log, "reason": reason}, ensure_ascii=False, indent=1))
    return child
