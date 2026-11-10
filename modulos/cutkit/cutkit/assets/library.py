"""Biblioteca persistente de medios de cutkit (direccionada por contenido).

    datos/biblioteca/<sha256[:2]>/<sha256>.<ext>    blob inmutable (solo lectura)
    datos/biblioteca/library.db                     registro SQLite (origen, licencia, URL, coste, usos)
    datos/biblioteca/_tmp/                          trabajos a medias (se limpian solos)

`datos/` es `modulos/cutkit/datos/` (o `CUTKIT_DATOS`): caché regenerable, fuera de git. Comparte carpeta con
las cachés de música (`musica/`) y SFX (`sfx_proc/`), que no chocan con los prefijos hexadecimales de los blobs.

Regla: «consultar antes de descargar». Cada petición (kind, query, params) se reduce a una clave canónica
(`request_key`); si esa clave ya produjo un blob que sigue en disco y no ha caducado, se reutiliza sin coste.
Un mismo blob puede venir de varias peticiones (p. ej. «Nimbo» y «nimbo.io» dan el mismo archivo): se guarda
una sola vez (sha256) y se apuntan las dos claves.

Los blobs se copian a la carpeta de edición como clones (copia en escritura: `cp -c` en APFS, `cp --reflink`
en Btrfs/XFS; no ocupan disco y editar la copia no toca la biblioteca); si el clon no es posible, copia normal.
Las rutas se guardan relativas a la raíz del producto cuando están dentro.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from cutkit.paths import LIBRARY, RAIZ
from cutkit.sistema import plataforma

DB_PATH = LIBRARY / "library.db"
TMP = LIBRARY / "_tmp"

# Parámetros que no cambian el resultado (no entran en la clave de la biblioteca).
VOLATILE_PARAMS = {"refresh", "max_age_days", "allow_unverified", "for_decision", "note", "notes", "subdir",
                   "keep_frames"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS media (
  sha256      TEXT PRIMARY KEY,
  ext         TEXT NOT NULL,
  path        TEXT NOT NULL,          -- relativa a la raíz del producto (absoluta si está fuera)
  kind        TEXT NOT NULL,          -- tipo de petición: file, logo, web_capture, web_scroll, stock, music...
  media_type  TEXT NOT NULL,          -- image | video | svg | audio | html
  origin      TEXT NOT NULL,          -- origen del Asset (usuario, logo, web_capture, stock, music_gen...)
  source_url  TEXT,
  license     TEXT NOT NULL DEFAULT '',
  query       TEXT,
  params      TEXT,                   -- JSON canónico de la primera petición que lo produjo
  width       INTEGER,
  height      INTEGER,
  duration    REAL,
  bytes       INTEGER,
  cost_usd    REAL NOT NULL DEFAULT 0,
  notes       TEXT NOT NULL DEFAULT '',
  meta        TEXT NOT NULL DEFAULT '{}',
  created     TEXT NOT NULL,
  used_in     TEXT NOT NULL DEFAULT '[]'   -- JSON: ["<slug>/<asset_id>", ...]
);
CREATE TABLE IF NOT EXISTS lookups (
  req_key   TEXT NOT NULL,
  sha256    TEXT NOT NULL REFERENCES media(sha256),
  kind      TEXT NOT NULL,
  query     TEXT,
  params    TEXT,
  created   TEXT NOT NULL,
  PRIMARY KEY (req_key, sha256)
);
CREATE INDEX IF NOT EXISTS idx_lookups_key ON lookups(req_key, created);
CREATE INDEX IF NOT EXISTS idx_media_kind ON media(kind, query);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel_or_abs(p: Path | str) -> str:
    """Ruta relativa a la raíz del producto si está dentro (con `/` en todos los sistemas); absoluta si no."""
    p = Path(p).resolve()
    try:
        return p.relative_to(RAIZ).as_posix()
    except ValueError:
        return str(p)


def abs_path(p: str | Path) -> Path:
    """Ruta guardada por la biblioteca (relativa a la raíz del producto) → absoluta."""
    p = Path(p)
    return p if p.is_absolute() else RAIZ / p


def user_path(p: str | Path, *bases: Path) -> Path:
    """Ruta que escribe el usuario: absoluta o con `~`; si es relativa, la primera que exista desde la carpeta
    actual, cada `bases` (p. ej. la carpeta del proyecto) y la raíz del producto. Si no existe, la de la raíz."""
    p = Path(p).expanduser()
    if p.is_absolute():
        return p
    for base in (Path.cwd(), *bases, RAIZ):
        if (base / p).exists():
            return (base / p).resolve()
    return RAIZ / p


# ───────────────────────────── claves y hashes ─────────────────────────────

def canonical_params(params: dict[str, Any] | None) -> str:
    clean = {k: v for k, v in (params or {}).items() if k not in VOLATILE_PARAMS}
    return json.dumps(clean, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def request_key(kind: str, query: str, params: dict[str, Any] | None) -> str:
    """Clave estable de una petición: mismo (kind, query, params) → misma clave."""
    q = query.strip()
    if kind in ("logo", "stock"):
        q = q.lower()
    payload = f"{kind}\x1f{q}\x1f{canonical_params(params)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ───────────────────────────── base de datos ─────────────────────────────

_initialized = False


def _connect() -> sqlite3.Connection:
    LIBRARY.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=30000")
    return con


@contextmanager
def _tx() -> Iterator[sqlite3.Connection]:
    global _initialized
    con = _connect()
    try:
        if not _initialized:
            con.executescript(_SCHEMA)
            _initialized = True
        yield con
        con.commit()
    finally:
        con.close()


def init() -> None:
    with _tx():
        pass


def blob_path(sha: str, ext: str) -> Path:
    return LIBRARY / sha[:2] / f"{sha}.{ext.lstrip('.').lower()}"


def new_tmp(ext: str) -> Path:
    """Ruta temporal dentro de la biblioteca (mismo volumen → `rename` atómico al ingerir)."""
    TMP.mkdir(parents=True, exist_ok=True)
    return TMP / f"{uuid.uuid4().hex}.{ext.lstrip('.')}"


# Clon en copia en escritura por sistema (si el volumen no lo admite, el comando falla y se copia normal).
_CLONE_CMD = {"darwin": ["cp", "-c"], "linux": ["cp", "--reflink=auto"]}


def clone_file(src: Path, dst: Path) -> None:
    """Copia src→dst como clon (sin coste de disco) si se puede; si no, copia normal. La copia queda editable."""
    src, dst = Path(src), Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink():
        dst.unlink()
    elif dst.exists():
        dst.chmod(0o644)            # en Windows, un archivo de solo lectura no se puede borrar
        dst.unlink()
    cmd = _CLONE_CMD.get(plataforma())
    if cmd and shutil.which(cmd[0]):
        try:
            r = subprocess.run([*cmd, str(src), str(dst)], capture_output=True, timeout=120)
            if r.returncode == 0:
                dst.chmod(0o644)
                return
        except (OSError, subprocess.SubprocessError):
            pass
    shutil.copy2(src, dst)
    dst.chmod(0o644)


def lookup(kind: str, query: str, params: dict[str, Any] | None, *,
           max_age_days: float | None = None) -> dict | None:
    """Último blob producido por esta misma petición, si existe en disco y no ha caducado."""
    key = request_key(kind, query, params)
    with _tx() as con:
        rows = con.execute(
            "SELECT m.*, l.created AS looked_up FROM lookups l JOIN media m ON m.sha256 = l.sha256 "
            "WHERE l.req_key = ? ORDER BY l.created DESC", (key,)).fetchall()
    for row in rows:
        d = dict(row)
        if not abs_path(d["path"]).exists():
            continue
        if max_age_days is not None:
            created = datetime.fromisoformat(d["looked_up"])
            if datetime.now(timezone.utc) - created > timedelta(days=max_age_days):
                return None   # el más reciente ya caducó: hay que volver a obtenerlo
        d["meta"] = json.loads(d.get("meta") or "{}")
        d["used_in"] = json.loads(d.get("used_in") or "[]")
        return d
    return None


def get(sha: str) -> dict | None:
    with _tx() as con:
        row = con.execute("SELECT * FROM media WHERE sha256 = ?", (sha,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["meta"] = json.loads(d.get("meta") or "{}")
    d["used_in"] = json.loads(d.get("used_in") or "[]")
    return d


def ingest(src: Path | str, *, kind: str, query: str, params: dict[str, Any] | None, media_type: str,
           origin: str, source_url: str | None = None, license: str = "", cost_usd: float = 0.0,
           notes: str = "", meta: dict[str, Any] | None = None, probe_info: dict[str, Any] | None = None,
           move: bool = False, ext: str | None = None) -> dict:
    """Guarda `src` en la biblioteca (por sha256) y registra la petición que lo produjo.

    - `move=True`: `src` es un temporal propio y se mueve (rename); si no, se clona/copia.
    - Si el blob ya existía (otra petición dio los mismos bytes) no se duplica: solo se añade la
      clave de búsqueda y, si esta vez costó dinero, se suma al coste registrado.
    """
    src = Path(src)
    sha = sha256_file(src)
    ext = (ext or src.suffix.lstrip(".") or "bin").lower()
    dst = blob_path(sha, ext)
    if dst.exists():
        if move:
            src.unlink(missing_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if move:
            os.replace(src, dst)
        else:
            clone_file(src, dst)
        dst.chmod(0o444)   # blob inmutable
    pi = probe_info or {}
    now = now_iso()
    params_json = canonical_params(params)
    with _tx() as con:
        # INSERT OR IGNORE: dos hilos pueden ingerir los mismos bytes a la vez (p. ej. dos alias del mismo logo).
        cur = con.execute(
            "INSERT OR IGNORE INTO media (sha256, ext, path, kind, media_type, origin, source_url, license, query, "
            "params, width, height, duration, bytes, cost_usd, notes, meta, created, used_in) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, '[]')",
            (sha, ext, rel_or_abs(dst), kind, media_type, origin, source_url, license, query, params_json,
             pi.get("width"), pi.get("height"), pi.get("duration"), dst.stat().st_size, float(cost_usd),
             notes, json.dumps(meta or {}, ensure_ascii=False, default=str), now))
        if cur.rowcount == 0 and cost_usd:
            con.execute("UPDATE media SET cost_usd = cost_usd + ? WHERE sha256 = ?", (float(cost_usd), sha))
        con.execute(
            "INSERT OR REPLACE INTO lookups (req_key, sha256, kind, query, params, created) VALUES (?,?,?,?,?,?)",
            (request_key(kind, query, params), sha, kind, query, params_json, now))
    rec = get(sha)
    assert rec is not None
    return rec


def mark_used(sha: str, where: str) -> None:
    """Apunta dónde se usó el blob (`<slug>/<asset_id>`), sin duplicados."""
    with _tx() as con:
        row = con.execute("SELECT used_in FROM media WHERE sha256 = ?", (sha,)).fetchone()
        if row is None:
            return
        used = json.loads(row["used_in"] or "[]")
        if where not in used:
            used.append(where)
            con.execute("UPDATE media SET used_in = ? WHERE sha256 = ?", (json.dumps(used), sha))


def search(kind: str | None = None, text: str | None = None, limit: int = 50) -> list[dict]:
    """Búsqueda simple por tipo y texto en la consulta, las notas o la URL de origen."""
    where, args = ["1=1"], []
    if kind:
        where.append("kind = ?")
        args.append(kind)
    if text:
        where.append("(query LIKE ? OR notes LIKE ? OR source_url LIKE ?)")
        args += [f"%{text}%"] * 3
    with _tx() as con:
        rows = con.execute(f"SELECT * FROM media WHERE {' AND '.join(where)} ORDER BY created DESC LIMIT ?",
                           (*args, limit)).fetchall()
    return [dict(r) for r in rows]


def clean_tmp(max_age_h: float = 6) -> int:
    """Borra temporales huérfanos (de ejecuciones interrumpidas)."""
    if not TMP.exists():
        return 0
    n, limit = 0, datetime.now().timestamp() - max_age_h * 3600
    for p in TMP.iterdir():
        try:
            if p.stat().st_mtime < limit:
                shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink()
                n += 1
        except OSError:
            pass
    return n
