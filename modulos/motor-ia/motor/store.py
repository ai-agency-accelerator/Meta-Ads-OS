"""Persistencia: SQLite (documentos, costes, trabajos, caché) + almacén de assets por contenido.

El almacén de assets es local por defecto (data/assets/ab/abcdef….ext). La interfaz
`AssetStore` está aislada para poder sustituirla por R2/S3 sin tocar el resto.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import shutil
import sqlite3
import subprocess
import threading
from pathlib import Path
from typing import Any, Iterable, TypeVar

from pydantic import BaseModel

from .config import Settings, settings
from .models import Actor, Asset, AssetKind, BrandKit, CostEntry, Job, Product, Project

T = TypeVar("T", bound=BaseModel)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS docs (
  kind TEXT NOT NULL, id TEXT NOT NULL, json TEXT NOT NULL, updated_at REAL NOT NULL,
  PRIMARY KEY (kind, id)
);
CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY, json TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS costs (
  id TEXT PRIMARY KEY, ts REAL, project_id TEXT, scene_id TEXT, step TEXT, provider TEXT,
  model TEXT, unit TEXT, quantity REAL, unit_price REAL, usd REAL, latency_s REAL,
  status TEXT, cached INTEGER, note TEXT, phase TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS costs_project ON costs(project_id);
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY, kind TEXT, project_id TEXT, status TEXT, progress REAL, message TEXT,
  json TEXT NOT NULL, created_at REAL, updated_at REAL
);
CREATE TABLE IF NOT EXISTS cache (
  key TEXT PRIMARY KEY, value TEXT NOT NULL, created_at REAL NOT NULL
);
"""

_KIND_MODELS: dict[str, type[BaseModel]] = {
    "brand": BrandKit,
    "product": Product,
    "actor": Actor,
    "project": Project,
}


def _kind_of(obj: BaseModel) -> str:
    for k, m in _KIND_MODELS.items():
        if isinstance(obj, m):
            return k
    raise TypeError(f"tipo no persistible: {type(obj)}")


class DB:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.RLock()
        self._local = threading.local()
        with self.conn() as c:
            c.executescript(_SCHEMA)
            cols = {r[1] for r in c.execute("PRAGMA table_info(costs)")}
            if "phase" not in cols:  # migración de bases anteriores
                c.execute("ALTER TABLE costs ADD COLUMN phase TEXT DEFAULT ''")

    def conn(self) -> sqlite3.Connection:
        c = getattr(self._local, "c", None)
        if c is None:
            c = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA synchronous=NORMAL")
            self._local.c = c
        return c

    # ── documentos ──
    def put(self, obj: BaseModel) -> None:
        import time

        kind = _kind_of(obj)
        if isinstance(obj, Project):
            obj.updated_at = time.time()
        with self._lock, self.conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO docs(kind,id,json,updated_at) VALUES(?,?,?,?)",
                (kind, obj.id, obj.model_dump_json(), time.time()),  # type: ignore[attr-defined]
            )

    def get(self, model: type[T], id_: str) -> T:
        kind = next(k for k, m in _KIND_MODELS.items() if m is model)
        row = self.conn().execute("SELECT json FROM docs WHERE kind=? AND id=?", (kind, id_)).fetchone()
        if row is None:
            raise KeyError(f"{kind} {id_} no existe")
        return model.model_validate_json(row[0])

    def find(self, model: type[T], id_or_handle: str) -> T:
        try:
            return self.get(model, id_or_handle)
        except KeyError:
            for obj in self.list(model):
                for attr in ("handle", "name"):
                    if getattr(obj, attr, None) in (id_or_handle, id_or_handle.lstrip("@")) or (
                        getattr(obj, attr, None) == "@" + id_or_handle.lstrip("@")
                    ):
                        return obj
            raise

    def list(self, model: type[T]) -> list[T]:
        kind = next(k for k, m in _KIND_MODELS.items() if m is model)
        rows = self.conn().execute("SELECT json FROM docs WHERE kind=? ORDER BY updated_at DESC", (kind,)).fetchall()
        return [model.model_validate_json(r[0]) for r in rows]

    def delete(self, model: type[BaseModel], id_: str) -> None:
        kind = next(k for k, m in _KIND_MODELS.items() if m is model)
        with self._lock, self.conn() as c:
            c.execute("DELETE FROM docs WHERE kind=? AND id=?", (kind, id_))

    # ── assets ──
    def put_asset(self, a: Asset) -> None:
        with self._lock, self.conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO assets(id,json,created_at) VALUES(?,?,?)",
                (a.id, a.model_dump_json(), a.created_at),
            )

    def get_asset(self, id_: str) -> Asset:
        row = self.conn().execute("SELECT json FROM assets WHERE id=?", (id_,)).fetchone()
        if row is None:
            raise KeyError(f"asset {id_} no existe")
        return Asset.model_validate_json(row[0])

    # ── costes ──
    def add_cost(self, e: CostEntry) -> None:
        with self._lock, self.conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO costs (id, ts, project_id, scene_id, step, provider, model, unit, quantity, "
                "unit_price, usd, latency_s, status, cached, note, phase) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    e.id, e.ts, e.project_id, e.scene_id, e.step, e.provider, e.model, e.unit,
                    e.quantity, e.unit_price, e.usd, e.latency_s, e.status, int(e.cached), e.note, e.phase,
                ),
            )

    def costs(self, project_id: str | None = None) -> list[CostEntry]:
        cols = [
            "id", "ts", "project_id", "scene_id", "step", "provider", "model", "unit",
            "quantity", "unit_price", "usd", "latency_s", "status", "cached", "note", "phase",
        ]
        q = f"SELECT {', '.join(cols)} FROM costs"
        args: tuple[Any, ...] = ()
        if project_id:
            q += " WHERE project_id=?"
            args = (project_id,)
        q += " ORDER BY ts"
        out = []
        for r in self.conn().execute(q, args).fetchall():
            d = dict(zip(cols, r))
            d["cached"] = bool(d["cached"])
            d["phase"] = d["phase"] or ""
            out.append(CostEntry(**d))
        return out

    def total_spend(self, project_id: str | None = None) -> float:
        q = "SELECT COALESCE(SUM(usd),0) FROM costs WHERE status IN ('ok','error')"
        args: tuple[Any, ...] = ()
        if project_id:
            q += " AND project_id=?"
            args = (project_id,)
        return float(self.conn().execute(q, args).fetchone()[0])

    # ── trabajos ──
    def put_job(self, j: Job) -> None:
        import time

        j.updated_at = time.time()
        with self._lock, self.conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO jobs VALUES(?,?,?,?,?,?,?,?,?)",
                (j.id, j.kind, j.project_id, j.status, j.progress, j.message, j.model_dump_json(), j.created_at, j.updated_at),
            )

    def get_job(self, id_: str) -> Job:
        row = self.conn().execute("SELECT json FROM jobs WHERE id=?", (id_,)).fetchone()
        if row is None:
            raise KeyError(id_)
        return Job.model_validate_json(row[0])

    def jobs(self, project_id: str | None = None, limit: int = 50) -> list[Job]:
        q = "SELECT json FROM jobs"
        args: tuple[Any, ...] = ()
        if project_id:
            q += " WHERE project_id=?"
            args = (project_id,)
        q += " ORDER BY created_at DESC LIMIT ?"
        args = args + (limit,)
        return [Job.model_validate_json(r[0]) for r in self.conn().execute(q, args).fetchall()]

    # ── caché de pasos ──
    def cache_get(self, key: str) -> Any | None:
        row = self.conn().execute("SELECT value FROM cache WHERE key=?", (key,)).fetchone()
        return None if row is None else json.loads(row[0])

    def cache_put(self, key: str, value: Any) -> None:
        import time

        with self._lock, self.conn() as c:
            c.execute("INSERT OR REPLACE INTO cache VALUES(?,?,?)", (key, json.dumps(value), time.time()))


# ───────────────────────────── Almacén de assets ─────────────────────────────


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: Path) -> dict[str, Any]:
    """Metadatos con ffprobe (vídeo/audio/imagen)."""
    try:
        from .media import FFPROBE

        out = subprocess.run(
            [shutil.which("ffprobe") or FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, stdin=subprocess.DEVNULL,
        )
        return json.loads(out.stdout or "{}")
    except Exception:
        return {}


def _kind_from_mime(mime: str, path: Path) -> AssetKind:
    if mime.startswith("image/"):
        return AssetKind.image
    if mime.startswith("video/"):
        return AssetKind.video
    if mime.startswith("audio/"):
        return AssetKind.audio
    if path.suffix.lower() in (".ttf", ".otf"):
        return AssetKind.font
    return AssetKind.data


class AssetStore:
    def __init__(self, root: Path, db: DB):
        self.root = root
        self.db = db
        root.mkdir(parents=True, exist_ok=True)

    def abspath(self, a: Asset | str) -> Path:
        asset = self.db.get_asset(a) if isinstance(a, str) else a
        return self.root / asset.path

    def ingest(self, src: Path | str, *, source: str = "upload", meta: dict[str, Any] | None = None, move: bool = False) -> Asset:
        src = Path(src)
        digest = sha256_file(src)[:24]
        ext = src.suffix.lower() or ".bin"
        rel = Path(digest[:2]) / f"{digest}{ext}"
        dst = self.root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            if move:
                shutil.move(str(src), dst)
            else:
                shutil.copy2(src, dst)
        elif move and src.exists() and src.resolve() != dst.resolve():
            src.unlink(missing_ok=True)
        try:
            existing = self.db.get_asset(digest)
            if meta:
                existing.meta.update(meta)
                self.db.put_asset(existing)
            return existing
        except KeyError:
            pass
        mime = mimetypes.guess_type(dst.name)[0] or ""
        kind = _kind_from_mime(mime, dst)
        a = Asset(id=digest, kind=kind, path=str(rel), mime=mime, bytes=dst.stat().st_size, source=source, meta=meta or {})
        info = probe(dst) if kind in (AssetKind.video, AssetKind.audio, AssetKind.image) else {}
        for st in info.get("streams", []):
            if st.get("codec_type") == "video":
                a.width = st.get("width")
                a.height = st.get("height")
                fr = st.get("avg_frame_rate") or st.get("r_frame_rate") or "0/1"
                try:
                    n, d = fr.split("/")
                    a.fps = round(float(n) / float(d), 3) if float(d) else None
                except Exception:
                    pass
            if st.get("codec_type") == "audio":
                a.has_audio = True
        if kind in (AssetKind.video, AssetKind.audio):
            try:
                a.duration = float(info.get("format", {}).get("duration"))
            except (TypeError, ValueError):
                pass
            if a.has_audio is None:
                a.has_audio = False
        self.db.put_asset(a)
        return a

    def ingest_bytes(self, data: bytes, ext: str, *, source: str, meta: dict[str, Any] | None = None) -> Asset:
        tmp_dir = self.root / "_tmp"
        tmp_dir.mkdir(exist_ok=True)
        tmp = tmp_dir / (hashlib.sha256(data).hexdigest()[:16] + ext)
        tmp.write_bytes(data)
        return self.ingest(tmp, source=source, meta=meta, move=True)


class Context:
    """Contenedor de dependencias compartido por todos los módulos."""

    def __init__(self, s: Settings | None = None):
        self.settings = s or settings()
        self.db = DB(self.settings.db_path)
        self.assets = AssetStore(self.settings.assets_dir, self.db)

    def work(self, *parts: str) -> Path:
        p = self.settings.work_dir.joinpath(*parts)
        p.mkdir(parents=True, exist_ok=True)
        return p


_ctx: Context | None = None
_ctx_lock = threading.Lock()


def ctx() -> Context:
    global _ctx
    with _ctx_lock:
        if _ctx is None:
            _ctx = Context()
        return _ctx


def set_ctx(c: Context | None) -> None:
    global _ctx
    _ctx = c


def iter_assets(ids: Iterable[str]) -> list[Asset]:
    c = ctx()
    out = []
    for i in ids:
        try:
            out.append(c.db.get_asset(i))
        except KeyError:
            continue
    return out
