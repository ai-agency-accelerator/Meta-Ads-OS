"""Costes reales: tabla de precios, libro de costes, guardián de presupuesto y caché de pasos.

Cada llamada a un proveedor pasa por `meter()`, que:
  1. comprueba el presupuesto (por proyecto y global) con una estimación previa,
  2. mide la latencia,
  3. registra el coste REAL con las unidades devueltas por el proveedor,
  4. registra también los errores (las llamadas fallidas pueden costar dinero).
"""

from __future__ import annotations

import contextvars
import hashlib
import json
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

import yaml

from .config import PACKAGE_ROOT
from .models import CostEntry
from .store import ctx

_project: contextvars.ContextVar[str | None] = contextvars.ContextVar("project", default=None)
_scene: contextvars.ContextVar[str | None] = contextvars.ContextVar("scene", default=None)
_phase: contextvars.ContextVar[str] = contextvars.ContextVar("phase", default="produce")


class BudgetExceeded(RuntimeError):
    pass


@contextmanager
def scope(project_id: str | None = None, scene_id: str | None = None) -> Iterator[None]:
    t1 = _project.set(project_id) if project_id is not None else None
    t2 = _scene.set(scene_id) if scene_id is not None else None
    try:
        yield
    finally:
        if t2 is not None:
            _scene.reset(t2)
        if t1 is not None:
            _project.reset(t1)


@contextmanager
def phase(name: str) -> Iterator[None]:
    """Etiqueta el gasto: produce | retake | regeneration | variant (para separar el coste de los arreglos)."""
    tok = _phase.set(name)
    try:
        yield
    finally:
        _phase.reset(tok)


def current_project() -> str | None:
    return _project.get()


def current_scene() -> str | None:
    return _scene.get()


# ───────────────────────────── Tabla de precios ─────────────────────────────


@lru_cache(maxsize=1)
def price_table() -> dict[str, Any]:
    p = PACKAGE_ROOT / "config" / "prices.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def price(provider: str, model: str, key: str | None = None, default: float = 0.0) -> float:
    """Devuelve el precio unitario. `key` selecciona variante (p.ej. '720p', 'input_per_m')."""
    entry = (price_table().get(provider) or {}).get(model)
    if entry is None:
        return default
    if isinstance(entry, (int, float)):
        return float(entry)
    if key is None:
        v = entry.get("price", default)
        if isinstance(v, dict):
            return float(next(iter(v.values())))
        return float(v)
    if key in entry:
        return float(entry[key])
    pv = entry.get("price")
    if isinstance(pv, dict) and key in pv:
        return float(pv[key])
    return default


def token_cost(provider: str, model: str, prompt_tokens: int, output_tokens: int, *, audio_out: bool = False,
               video_in_tokens: int = 0) -> float:
    inp = price(provider, model, "input_per_m", 0.0)
    out_key = "audio_output_per_m" if audio_out else "output_per_m"
    out = price(provider, model, out_key, price(provider, model, "output_per_m", 0.0))
    vid = price(provider, model, "video_input_per_m", inp)
    text_in = max(prompt_tokens - video_in_tokens, 0)
    return (text_in * inp + video_in_tokens * vid + output_tokens * out) / 1_000_000


# ───────────────────────────── Guardián de presupuesto ─────────────────────────────


MIN_FREE_DISK_GB = 1.5
_BUDGET_LOCK = threading.Lock()
_RESERVED = {"usd": 0.0}  # gasto estimado de llamadas en curso


def check_budget(est_usd: float, project_id: str | None = None) -> None:
    c = ctx()
    s = c.settings
    pid = project_id or current_project()
    import shutil

    free_gb = shutil.disk_usage(s.data_dir).free / 1e9
    if free_gb < MIN_FREE_DISK_GB:
        # sin disco, el resultado de un trabajo YA pagado no se podría guardar: se pausa antes de pagar
        raise BudgetExceeded(f"disco casi lleno ({free_gb:.1f} GB libres < {MIN_FREE_DISK_GB} GB): ejecuta `motor gc` y reanuda")
    glob = c.db.total_spend()
    if glob + est_usd > s.budget_global_usd + 1e-9:
        raise BudgetExceeded(
            f"presupuesto global superado: gastado {glob:.3f} + estimado {est_usd:.3f} > {s.budget_global_usd:.2f} USD"
        )
    if pid:
        proj = c.db.total_spend(pid)
        limit = s.budget_per_project_usd
        try:
            from .models import Project

            p = c.db.get(Project, pid)
            if p.brief.budget_usd:
                limit = p.brief.budget_usd
        except Exception:
            pass
        if proj + est_usd > limit + 1e-9:
            raise BudgetExceeded(
                f"presupuesto del proyecto {pid} superado: {proj:.3f} + {est_usd:.3f} > {limit:.2f} USD"
            )


@dataclass
class Meter:
    step: str
    provider: str
    model: str
    est_usd: float = 0.0
    unit: str = ""
    quantity: float = 0.0
    unit_price: float = 0.0
    usd: float | None = None
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def set(self, unit: str, quantity: float, unit_price: float, note: str = "") -> None:
        self.unit, self.quantity, self.unit_price = unit, quantity, unit_price
        self.usd = quantity * unit_price
        if note:
            self.note = note

    def set_usd(self, usd: float, unit: str = "request", quantity: float = 1.0, note: str = "") -> None:
        self.unit, self.quantity = unit, quantity
        self.unit_price = usd / quantity if quantity else usd
        self.usd = usd
        if note:
            self.note = note


@contextmanager
def meter(step: str, provider: str, model: str, est_usd: float = 0.0, *, enforce: bool = True) -> Iterator[Meter]:
    reserved = 0.0
    if enforce and est_usd > 0:
        # comprobar + reservar de forma atómica: dos hilos en paralelo no pueden pasar ambos el mismo margen
        with _BUDGET_LOCK:
            check_budget(est_usd + _RESERVED["usd"])
            _RESERVED["usd"] += est_usd
            reserved = est_usd
    m = Meter(step=step, provider=provider, model=model, est_usd=est_usd)
    t0 = time.time()
    status = "ok"
    try:
        yield m
    except Exception as e:  # registrar el intento fallido (algunos proveedores cobran)
        status = "error"
        m.note = (m.note + " " if m.note else "") + f"{type(e).__name__}: {str(e)[:200]}"
        if getattr(e, "accepted", False) and m.usd is None:
            # el proveedor aceptó el trabajo y se perdió el resultado: se asume cobrado (estimación prudente)
            m.usd = m.est_usd
            m.note = f"ACEPTADO Y PERDIDO (coste estimado, id remoto {getattr(e, 'remote_id', '?')}) · " + m.note
        raise
    finally:
        usd = m.usd if m.usd is not None else (0.0 if status == "error" else m.est_usd)
        entry = CostEntry(
            project_id=current_project(),
            scene_id=current_scene(),
            step=step,
            provider=provider,
            model=model,
            unit=m.unit or ("estimate" if m.usd is None else ""),
            quantity=m.quantity,
            unit_price=m.unit_price,
            usd=round(usd, 6),
            latency_s=round(time.time() - t0, 3),
            status=status if m.usd is not None or status == "error" else "estimated",
            note=m.note,
            phase=_phase.get(),
        )
        ctx().db.add_cost(entry)
        if reserved:
            with _BUDGET_LOCK:
                _RESERVED["usd"] = max(0.0, _RESERVED["usd"] - reserved)


def record_cached(step: str, provider: str, model: str, note: str = "") -> None:
    ctx().db.add_cost(
        CostEntry(
            project_id=current_project(), scene_id=current_scene(), step=step, provider=provider,
            model=model, usd=0.0, status="cached", cached=True, note=note, phase=_phase.get(),
        )
    )


def record_local(step: str, tool: str, seconds: float, note: str = "") -> None:
    """Pasos locales (render, QA determinista): coste de CPU estimado con tarifa de VPS."""
    rate = price("local", "cpu_second", None, 0.0000025)  # ~0,009 $/h de un VPS pequeño
    ctx().db.add_cost(
        CostEntry(
            project_id=current_project(), scene_id=current_scene(), step=step, provider="local", model=tool,
            unit="cpu_second", quantity=round(seconds, 3), unit_price=rate, usd=round(seconds * rate, 6),
            latency_s=round(seconds, 3), status="ok", note=note, phase=_phase.get(),
        )
    )


# ───────────────────────────── Caché de pasos ─────────────────────────────


def cache_key(*parts: Any) -> str:
    raw = json.dumps(parts, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def cache_get(key: str) -> Any | None:
    """Acierto de caché SOLO si el asset al que apunta sigue existiendo en disco (si no, se trata como fallo)."""
    hit = ctx().db.cache_get(key)
    if isinstance(hit, dict) and hit.get("asset"):
        try:
            a = ctx().db.get_asset(hit["asset"])
            if not ctx().assets.abspath(a).exists():
                return None
        except KeyError:
            return None
    return hit


def cache_put(key: str, value: Any) -> None:
    ctx().db.cache_put(key, value)


# ───────────────────────────── Informes ─────────────────────────────


def summarize(project_id: str | None = None) -> dict[str, Any]:
    entries = ctx().db.costs(project_id)
    by_step: dict[str, float] = {}
    by_model: dict[str, float] = {}
    by_scene: dict[str, float] = {}
    by_phase: dict[str, float] = {}
    calls = errors = cached = 0
    for e in entries:
        if e.status == "cached":
            cached += 1
            continue
        calls += 1
        if e.status == "error":
            errors += 1
        by_step[e.step] = by_step.get(e.step, 0) + e.usd
        key = f"{e.provider}:{e.model}"
        by_model[key] = by_model.get(key, 0) + e.usd
        if e.scene_id:
            by_scene[e.scene_id] = by_scene.get(e.scene_id, 0) + e.usd
        ph = e.phase or "produce"
        by_phase[ph] = by_phase.get(ph, 0) + e.usd
    total = sum(by_step.values())
    return {
        "project_id": project_id,
        "total_usd": round(total, 4),
        "calls": calls,
        "errors": errors,
        "cache_hits": cached,
        "by_step": {k: round(v, 4) for k, v in sorted(by_step.items(), key=lambda kv: -kv[1])},
        "by_model": {k: round(v, 4) for k, v in sorted(by_model.items(), key=lambda kv: -kv[1])},
        "by_scene": {k: round(v, 4) for k, v in sorted(by_scene.items(), key=lambda kv: -kv[1])},
        "by_phase": {k: round(v, 4) for k, v in sorted(by_phase.items(), key=lambda kv: -kv[1])},
    }


STORAGE_USD_PER_GB_MONTH = 0.015  # Cloudflare R2 (sin coste de salida)


def record_storage(nbytes: int, months: float = 1.0, note: str = "") -> None:
    """Almacenamiento de los assets del proyecto (precio R2), para que el coste por anuncio sea completo."""
    gb = nbytes / 1e9
    ctx().db.add_cost(
        CostEntry(
            project_id=current_project(), step="storage", provider="r2", model="object-storage", unit="gb_month",
            quantity=round(gb * months, 6), unit_price=STORAGE_USD_PER_GB_MONTH, usd=round(gb * months * STORAGE_USD_PER_GB_MONTH, 6),
            status="ok", note=note or f"{nbytes / 1e6:.1f} MB × {months} mes", phase=_phase.get(),
        )
    )


def write_report(project_id: str, path: Path) -> dict[str, Any]:
    s = summarize(project_id)
    path.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
    return s
