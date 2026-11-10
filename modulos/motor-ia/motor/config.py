"""Configuración del motor.

Raíz del producto: `META_ADS_OS_RAIZ` o, si no existe, tres niveles por encima de este archivo
(`modulos/motor-ia/motor/config.py` → raíz de Meta Ads OS).

Orden de resolución de cada clave o ajuste (gana el primero que exista):
  1. variables de entorno;
  2. `.env` de la raíz del producto (el de todas las herramientas);
  3. `modulos/motor-ia/.env` (compatibilidad con instalaciones antiguas del motor);
  4. ficheros listados en `MOTOR_SECRETS_FILES` (separados por `os.pathsep`: «:» en Mac/Linux, «;» en Windows),
     de los que solo se importan las claves conocidas y autorizadas en `MOTOR_SECRETS_ALLOW`.

Los valores de las claves nunca se imprimen ni se copian a disco: `motor status` solo muestra ✔/·.

Presupuesto global del guardián (contrato §14), por orden de prioridad:
  1. `MOTOR_PRESUPUESTO_USD` del entorno o del `.env` de la raíz (alias antiguo: `MOTOR_BUDGET_GLOBAL_USD`);
  2. `motor.presupuesto_usd` de la cabecera de `contexto/preferencias.md`:
         ---
         motor:
           presupuesto_usd: 20
         ---
     (se lee de forma tolerante: cabecera entre `---` o bloque suelto, sangría de 2 o 4 espacios, coma decimal,
     comillas y `$`; la clave plana antigua `motor_presupuesto_usd: 20` también vale por compatibilidad);
  3. si no hay ninguno, 5 $.
El presupuesto por proyecto (`MOTOR_PRESUPUESTO_PROYECTO_USD`, alias `MOTOR_BUDGET_PER_PROJECT_USD`) es por defecto
igual al global.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent.parent  # modulos/motor-ia
ENGINE_ROOT = MODULE_ROOT  # nombre antiguo, se mantiene por compatibilidad
PACKAGE_ROOT = Path(__file__).resolve().parent

DEFAULT_BUDGET_USD = 5.0

KNOWN_KEYS = (
    "GEMINI_API_KEY",
    "FAL_KEY",
    "OPENAI_API_KEY",
    "BYTEPLUS_API_KEY",
    "DASHSCOPE_API_KEY",
    "MINIMAX_API_KEY",
    "HEYGEN_API_KEY",
    "SYNC_API_KEY",
    "ELEVENLABS_API_KEY",
)

_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")
_PREF_FLAT = re.compile(r"^[ \t>*+-]*`?motor_presupuesto_usd`?[ \t]*[:=][ \t]*(.+)$", re.I | re.M)
_BLOCK = re.compile(r"^([ \t]*)motor[ \t]*:[ \t]*(?:#.*)?$", re.I)
_KEY = re.compile(r"^([ \t]+)presupuesto_usd[ \t]*:[ \t]*(.+)$", re.I)


def product_root() -> Path:
    env = os.environ.get("META_ADS_OS_RAIZ")
    return Path(env).expanduser().resolve() if env else Path(__file__).resolve().parents[3]


def _parse_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        if not path.is_file():
            return out
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return out
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = _LINE.match(raw)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].strip()
        out[key] = value
    return out


def _to_float(value: str | None) -> float | None:
    """«20», «20.5», «20,5», «"20"», «$20», «20 $», «20 USD», «20  # comentario» → número; si no, None."""
    if value is None:
        return None
    t = str(value).split(" #", 1)[0].strip().strip("\"'`").strip()
    t = re.sub(r"(?i)\s*(usd|\$)\s*$", "", t).lstrip("$").strip()
    if not t:
        return None
    try:
        v = float(t.replace(",", "."))
    except ValueError:
        return None
    return v if v >= 0 else None


def _nested_budget(lines: list[str]) -> float | None:
    """Busca `presupuesto_usd` dentro de un bloque `motor:` (cualquier sangría mayor que la de `motor:`)."""
    for i, line in enumerate(lines):
        m = _BLOCK.match(line)
        if not m:
            continue
        base = len(m.group(1).expandtabs(2))
        for nxt in lines[i + 1:]:
            if not nxt.strip() or nxt.lstrip().startswith("#"):
                continue
            ind = len(nxt) - len(nxt.lstrip())
            if len(nxt[:ind].expandtabs(2)) <= base:
                break  # fin del bloque `motor:`
            k = _KEY.match(nxt)
            if k:
                v = _to_float(k.group(2))
                if v is not None:
                    return v
    return None


def budget_from_preferences(root: Path) -> float | None:
    """Presupuesto de `contexto/preferencias.md`: `motor.presupuesto_usd` (forma documentada; primero en la cabecera
    YAML entre `---` y, si no, en cualquier bloque `motor:` del archivo) o la clave plana antigua `motor_presupuesto_usd`."""
    f = root / "contexto" / "preferencias.md"
    try:
        text = f.read_text(encoding="utf-8", errors="ignore") if f.is_file() else ""
    except OSError:
        return None
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i, ln in enumerate(lines[1:], 1) if ln.strip() == "---"), len(lines))
        v = _nested_budget(lines[1:end])
        if v is not None:
            return v
    v = _nested_budget(lines)
    if v is not None:
        return v
    m = _PREF_FLAT.search(text)
    return _to_float(m.group(1)) if m else None


@dataclass
class Settings:
    data_dir: Path
    keys: dict[str, str] = field(default_factory=dict)
    budget_per_project_usd: float = DEFAULT_BUDGET_USD
    budget_global_usd: float = DEFAULT_BUDGET_USD
    budget_source: str = "por defecto"
    default_locale: str = "es-ES"
    mock: bool = False  # fuerza proveedores simulados (tests y modo de prueba sin gasto)
    root: Path = field(default_factory=product_root)

    def key(self, name: str) -> str | None:
        v = self.keys.get(name)
        return v if v else None

    def has(self, name: str) -> bool:
        return bool(self.key(name))

    @property
    def db_path(self) -> Path:
        return self.data_dir / "motor.sqlite3"

    @property
    def assets_dir(self) -> Path:
        return self.data_dir / "assets"

    @property
    def work_dir(self) -> Path:
        return self.data_dir / "work"

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def models_dir(self) -> Path:
        return self.data_dir / "models"

    def ensure_dirs(self) -> None:
        for p in (self.data_dir, self.assets_dir, self.work_dir, self.exports_dir, self.models_dir):
            p.mkdir(parents=True, exist_ok=True)


def _load() -> Settings:
    root = product_root()
    root_env = _parse_dotenv(root / ".env")
    module_env = _parse_dotenv(MODULE_ROOT / ".env") if MODULE_ROOT.resolve() != root.resolve() else {}

    def get(name: str, default: str | None = None) -> str | None:
        return os.environ.get(name) or root_env.get(name) or module_env.get(name) or default

    keys: dict[str, str] = {}
    for k in KNOWN_KEYS:  # entorno → .env de la raíz → .env del módulo
        v = os.environ.get(k) or root_env.get(k) or module_env.get(k)
        if v:
            keys[k] = v
    secret_files = [p for p in (get("MOTOR_SECRETS_FILES") or "").split(os.pathsep) if p.strip()]
    # de ficheros de otros proyectos solo se importan las claves autorizadas explícitamente (por defecto, todas)
    allow = {k.strip() for k in (get("MOTOR_SECRETS_ALLOW") or ",".join(KNOWN_KEYS)).split(",") if k.strip()}
    for sf in secret_files:
        parsed = _parse_dotenv(Path(sf.strip()).expanduser())
        for k in KNOWN_KEYS:
            if k in allow and parsed.get(k):
                keys.setdefault(k, parsed[k])

    data_dir = Path(get("MOTOR_DATA_DIR", "data") or "data").expanduser()
    if not data_dir.is_absolute():
        data_dir = (MODULE_ROOT / data_dir).resolve()

    budget, source = None, "por defecto"
    for name in ("MOTOR_PRESUPUESTO_USD", "MOTOR_BUDGET_GLOBAL_USD"):
        budget = _to_float(get(name))
        if budget is not None:
            source = name
            break
    if budget is None:
        budget = budget_from_preferences(root)
        if budget is not None:
            source = "contexto/preferencias.md"
    if budget is None:
        budget = DEFAULT_BUDGET_USD
    per_project = None
    for name in ("MOTOR_PRESUPUESTO_PROYECTO_USD", "MOTOR_BUDGET_PER_PROJECT_USD"):
        per_project = _to_float(get(name))
        if per_project is not None:
            break

    s = Settings(
        data_dir=data_dir,
        keys=keys,
        budget_per_project_usd=per_project if per_project is not None else budget,
        budget_global_usd=budget,
        budget_source=source,
        default_locale=get("MOTOR_DEFAULT_LOCALE", "es-ES") or "es-ES",
        mock=(get("MOTOR_MOCK", "0") or "0").strip().lower() in ("1", "true", "yes", "si", "sí"),
        root=root,
    )
    s.ensure_dirs()
    return s


@lru_cache(maxsize=1)
def settings() -> Settings:
    return _load()


def reset_settings() -> None:
    settings.cache_clear()
