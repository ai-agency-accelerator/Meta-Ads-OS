"""Logos del vídeo frente a su original en la marca del cliente (sin catálogo externo ni descargas).

Originales (ver `cutkit.assets.logo`):
- el logo del cliente (`marca.json` → `logo`): entidad `cliente` o el slug o nombre del cliente;
- los logos de terceros aportados en `clientes/<cliente>/marca/logos/<nombre>.svg|png` (y sus variantes
  `<nombre>-<variante>.*`).

Un logo se declara en `TimelineItem.props` como {"entity": "nimbo", "src": "media/nimbo.png"} (suelto o en una lista
`logos`), o es un asset de `assets.json` cuyo id o nombre de archivo empieza por el nombre de un logo aportado. Los
assets con origen `logo` los copió el resolver del propio original, así que no se comparan. No hace falta buscar el
logo en el vídeo: el plan dice qué archivo se usa.

Comparación (Pillow + NumPy) contra cada original de la entidad, quedándose con el que mejor encaja:
- recorte a la caja del contenido (alfa o, si la imagen es opaca, lo que se separa del color del borde) y, si es una
  baldosa (logo dentro de un cuadrado o círculo de color), también el glifo interior;
- silueta normalizada a 96 × 96 px: media de IoU suave y correlación; se penaliza si cambia la proporción;
- correlación de la luminancia en escala de grises (dato de apoyo en la evidencia);
- color dominante (Lab, ΔE76) si el original es cromático.

Veredictos: coincide · dudoso (`warn`: forma entre 0,60 y 0,80, colores distintos o versión monocromo que no está
entre los originales) · otro logo (`block`: forma < 0,60, regla de oro: nunca un logo cambiado). Un SVG sin PNG
hermano ni rasterizador (Playwright) no se compara: aviso `info`.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from ..paths import CLIENTES, RAIZ, cliente_de, marca_dir
from .context import QAContext, tc

NORM = 96            # lado de la silueta normalizada
SHAPE_OK = 0.80      # forma «igual» (mismo dibujo rasterizado de otra forma: 0,85–1,00)
SHAPE_BAD = 0.60     # por debajo: otro dibujo
COLOR_OK = 28.0      # ΔE76 máximo entre paletas de marca
ACHROMA = 14.0       # croma por debajo del cual un color es gris, blanco o negro
_RANK = {"coincide": 4, "mono": 3, "color": 2, "dudoso": 1, "distinto": 0}


# ───────────────────────────── imagen → siluetas
def _rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """RGB uint8 (N, 3) → CIELAB (D65), L en 0..100. Sin matmul: el BLAS de macOS da avisos espurios."""
    c = rgb.reshape(-1, 3).astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = c[:, 0], c[:, 1], c[:, 2]
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    fx, fy, fz = (np.where(v > 216 / 24389, np.cbrt(v), (24389 / 27 * v + 16) / 116) for v in (x, y, z))
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], axis=1)


def _luma(rgb: np.ndarray) -> np.ndarray:
    rgb = rgb.astype(np.float64)
    return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0


def _filtro(mask: np.ndarray, size: int, op: str) -> np.ndarray:
    """Erosión (`min`) o dilatación (`max`) con un cuadrado de `size` px; fuera de la imagen cuenta como fondo, así
    que una forma que toca el borde también se erosiona desde ahí."""
    from scipy import ndimage

    f = ndimage.minimum_filter if op == "min" else ndimage.maximum_filter
    return f(mask.astype(np.uint8), size=size, mode="constant", cval=0) > 0


def _palette(rgb: np.ndarray, mask: np.ndarray) -> list[tuple[np.ndarray, float]]:
    """Colores dominantes (Lab, peso) del interior de la máscara (sin el borde suavizado)."""
    if mask.sum() > 400:
        inner = _filtro(mask, 3, "min")
        mask = inner if inner.sum() > 50 else mask
    px = rgb[mask]
    if len(px) == 0:
        return []
    q = (px // 32).astype(np.int32)                       # 8 niveles por canal → 512 cubetas
    idx = q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]
    counts = np.bincount(idx, minlength=512)
    out = []
    for b in np.argsort(counts)[::-1][:6]:
        w = counts[b] / len(px)
        if w < 0.06:
            break
        out.append((_rgb_to_lab(px[idx == b]).mean(axis=0), float(w)))
    tot = sum(w for _, w in out) or 1.0
    return [(c, w / tot) for c, w in out]


def _achromatic(pal: list[tuple[np.ndarray, float]]) -> bool:
    if not pal:
        return True
    return sum(w * float(np.hypot(c[1], c[2])) for c, w in pal) / max(1e-6, sum(w for _, w in pal)) < ACHROMA


def _norm(mask: np.ndarray) -> tuple[np.ndarray, float]:
    """Silueta recortada a su caja, centrada en un cuadrado y escalada a NORM px (+ proporción ancho/alto)."""
    from PIL import Image, ImageFilter

    ys, xs = np.nonzero(mask)
    crop = mask[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]
    h, w = crop.shape
    side = max(h, w)
    sq = np.zeros((side, side), np.uint8)
    sq[(side - h) // 2:(side - h) // 2 + h, (side - w) // 2:(side - w) // 2 + w] = crop.astype(np.uint8) * 255
    im = Image.fromarray(sq).resize((NORM, NORM), Image.Resampling.BOX).filter(ImageFilter.GaussianBlur(1.5))
    return np.asarray(im, np.float32) / 255.0, w / h


def _gray(rgb: np.ndarray, alpha: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Luminancia dentro de la caja de la silueta, sobre gris medio y normalizada a NORM px."""
    from PIL import Image

    ys, xs = np.nonzero(mask)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    lum = _luma(rgb[sl])
    a = alpha[sl] / 255.0
    g = lum * a + 0.5 * (1 - a)
    h, w = g.shape
    side = max(h, w)
    sq = np.full((side, side), 0.5)
    sq[(side - h) // 2:(side - h) // 2 + h, (side - w) // 2:(side - w) // 2 + w] = g
    return np.asarray(Image.fromarray((sq * 255).astype(np.uint8)).resize((NORM, NORM), Image.Resampling.BOX),
                      np.float32) / 255.0


def _lab1(rgb: np.ndarray) -> np.ndarray:
    return _rgb_to_lab(np.asarray(rgb, np.float64).round().clip(0, 255).astype(np.uint8).reshape(1, 3))[0]


def _fill_ratio(mask: np.ndarray) -> float:
    ys, xs = np.nonzero(mask)
    return float(mask.sum()) / float((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1))


def _exterior(kind: str, mask: np.ndarray, rgb: np.ndarray, bg: np.ndarray | None) -> dict[str, Any]:
    from scipy import ndimage

    filled = ndimage.binary_fill_holes(mask)
    ys, xs = np.nonzero(filled)
    bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    return {"kind": kind, "mask": mask, "filled": filled, "pal": _palette(rgb, mask),
            "tile": None if bg is None else _lab1(bg),
            "is_tile": 0.9 <= bw / bh <= 1.1 and _fill_ratio(filled) >= 0.76}


def _glifo(filled: np.ndarray, drawn: np.ndarray, rgb: np.ndarray, bg: np.ndarray | None) -> dict[str, Any] | None:
    """Glifo de una baldosa (cuadrado o círculo de color con el logo dentro): lo de dentro que no es del color de la
    baldosa, pintado encima o calado (hueco). None si la forma no es una baldosa."""
    if _fill_ratio(filled) < 0.72:
        return None
    h, w = filled.shape
    ring = filled & ~_filtro(filled, max(3, round(min(h, w) * 0.05)), "min")
    ring_px = ring & drawn
    if ring_px.sum() <= 20:
        return None
    tcol = np.median(rgb[ring_px], axis=0)
    if (np.linalg.norm(rgb[ring_px] - tcol, axis=1) < 30).mean() < 0.75:   # el borde no es de un color uniforme
        return None
    glyph = filled & ~ring & (~drawn | (np.linalg.norm(rgb - tcol, axis=2) > 50))
    share = glyph.sum() / max(1, filled.sum())
    if not (0.02 <= share <= 0.85 and glyph.sum() >= 16):
        return None
    visible = glyph & drawn
    if visible.sum() >= 0.5 * glyph.sum():
        pal = _palette(rgb, visible)
    else:                                                       # calado: se ve el fondo (o nada, si es transparente)
        pal = [(_lab1(bg), 1.0)] if bg is not None else []
    return {"kind": "glifo", "mask": glyph, "pal": pal, "tile": _lab1(tcol), "is_tile": False}


def _siluetas(img) -> list[dict[str, Any]]:
    """Siluetas de una imagen de logo: la exterior (con sus huecos) y, si es una baldosa, el glifo interior.

    Una imagen opaca con borde uniforme puede ser un logo sobre fondo o una baldosa que ocupa todo el lienzo (con las
    esquinas del color de fondo): se prueban las dos lecturas y la comparación se queda con la que mejor encaja."""
    from scipy import ndimage

    rgba = np.asarray(img.convert("RGBA"))
    rgb, a = rgba[..., :3], rgba[..., 3]
    h, w = a.shape
    bg = None
    if (a < 128).mean() >= 0.005:
        base, kind = a >= 128, "alfa"
    else:
        b = max(1, round(min(h, w) * 0.03))
        ring = np.zeros((h, w), bool)
        ring[:b, :] = ring[-b:, :] = ring[:, :b] = ring[:, -b:] = True
        bg = np.median(rgb[ring], axis=0)
        if (np.linalg.norm(rgb[ring] - bg, axis=1) < 30).mean() >= 0.7:
            base, kind = np.linalg.norm(rgb - bg, axis=2) > 40, "fondo"
        else:
            base, kind = np.ones((h, w), bool), "lleno"
    if base.sum() > 400:
        base = _filtro(_filtro(base, 3, "min"), 3, "max")       # apertura: fuera motas sueltas
    if base.sum() < 16:
        return []
    lecturas = [(kind, base, bg)]
    if kind == "fondo":
        lab, n = ndimage.label(base)
        borde = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]).tolist())) - {0}
        if borde and len(borde) < n:                            # restos pegados al borde (esquinas) y algo dentro
            marco = ~np.isin(lab, sorted(borde))
            if marco.sum() >= 16:
                lecturas.append(("marco", marco, None))
    out: list[dict[str, Any]] = []
    for kd, m, fondo in lecturas:
        s = _exterior(kd, m, rgb, fondo)
        out.append(s)
        if (g := _glifo(s["filled"], m, rgb, fondo)) is not None:
            out.append(g)
    for s in out:
        s["norm"], s["aspect"] = _norm(s["mask"])
        s["gray"] = _gray(rgb, a if kind == "alfa" else np.full_like(a, 255), s["mask"])
    return out


def _brand_palette(s: dict[str, Any]) -> list[tuple[np.ndarray, float]]:
    """Si el glifo es blanco o negro sobre una baldosa de color, el color de marca es el de la baldosa."""
    if s["kind"] in ("glifo", "fondo") and s["tile"] is not None and _achromatic(s["pal"]) \
            and float(np.hypot(*s["tile"][1:])) >= ACHROMA:
        return [(s["tile"], 1.0)]
    return s["pal"]


# ───────────────────────────── comparación
def _corr(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.ravel().astype(np.float64) - a.mean(), b.ravel().astype(np.float64) - b.mean()
    d = float(np.sqrt(np.sum(a * a) * np.sum(b * b)))
    return float(np.sum(a * b) / d) if d > 1e-9 else 0.0


def _color(c: dict[str, Any], r: dict[str, Any]) -> tuple[float | None, str, bool]:
    """(ΔE, estado, ¿los dos en color?): estado ok | distinto | mono (candidato sin color y original en color).
    Un candidato en color frente a un original sin color (p. ej. la variante blanca) es `distinto`: lleva colores
    que esa variante no tiene; si hay una variante en color que encaje, la comparación se queda con esa."""
    pc, pr = _brand_palette(c), _brand_palette(r)
    ac, ar = _achromatic(pc), _achromatic(pr)
    if ac and ar:
        return 0.0, "ok", False
    if ac != ar:
        return None, "mono" if ac else "distinto", False
    ref = [x for x, _ in pr] + ([r["tile"]] if r["tile"] is not None else [])
    d1 = sum(w * min(float(np.linalg.norm(x - y)) for y in ref) for x, w in pc)
    d2 = sum(w * min(float(np.linalg.norm(y - x)) for x, _ in pc) for y, w in pr)
    d = max(d1, d2)
    return d, "ok" if d <= COLOR_OK else "distinto", True


def _pares(cs: list[dict[str, Any]], rs: list[dict[str, Any]]) -> list[tuple[dict, dict]]:
    glifos = any(s["kind"] == "glifo" for s in cs + rs)
    pares = []
    for c in cs:
        for r in rs:
            gc, gr = c["kind"] == "glifo", r["kind"] == "glifo"
            # dos baldosas siempre se parecen entre sí: si alguna lleva glifo, solo cuentan los glifos
            if glifos and not gc and not gr and c["is_tile"] and r["is_tile"]:
                continue
            # un glifo frente a una baldosa entera no dice nada (sí frente a un símbolo suelto)
            if gc != gr and (r if gc else c)["is_tile"]:
                continue
            pares.append((c, r))
    return pares or [(c, r) for c in cs if c["kind"] != "glifo" for r in rs if r["kind"] != "glifo"]


def compare(cand_img, ref_img) -> dict[str, Any] | None:
    """Mejor emparejamiento de siluetas entre candidato y original: {veredicto, forma, iou, gris, delta_e, detalle}."""
    cs, rs = _siluetas(cand_img), _siluetas(ref_img)
    if not cs or not rs:
        return None
    best: dict[str, Any] | None = None
    for c, r in _pares(cs, rs):
        iou = float(np.minimum(c["norm"], r["norm"]).sum() / max(1e-6, np.maximum(c["norm"], r["norm"]).sum()))
        forma = 0.5 * iou + 0.5 * max(0.0, _corr(c["norm"], r["norm"]))
        ar = c["aspect"] / r["aspect"]
        ar = max(ar, 1 / ar)
        if ar > 1.25:                                           # una palabra y un subrayado no son el mismo logo
            forma *= 1.25 / ar
        gris = _corr(c["gray"], r["gray"])
        de, col, cromaticos = _color(c, r)
        nota = ""
        if col == "ok" and cromaticos and gris < 0.5:          # mismos colores, pero en otro sitio
            col, nota = "distinto", "los colores no están donde en el original"
        if forma < SHAPE_BAD:
            ver = "distinto"
        elif forma < SHAPE_OK:
            ver = "dudoso"
        elif col == "distinto":
            ver = "color"
        elif col == "mono":
            ver = "mono"
        else:
            ver = "coincide"
        res = {"veredicto": ver, "forma": round(forma, 3), "iou": round(iou, 3), "gris": round(gris, 3),
               "delta_e": None if de is None else round(de, 1), "par": f"{c['kind']}↔{r['kind']}",
               "nota": nota if ver == "color" else ""}
        if best is None or (_RANK[ver], forma) > (_RANK[best["veredicto"]], best["forma"]):
            best = res
    if best is not None:
        de = "color n/a" if best["delta_e"] is None else f"ΔE {best['delta_e']:.1f}"
        nota = f", {best['nota']}" if best["nota"] else ""
        best["detalle"] = (f"forma {best['forma']:.2f} (IoU {best['iou']:.2f}), gris {best['gris']:.2f}, {de}"
                           f"{nota}, {best['par']}")
    return best


# ───────────────────────────── declarados en el plan
def _cliente(ctx: QAContext) -> str | None:
    try:
        rel = ctx.vdir.resolve().relative_to(CLIENTES.resolve())
        if len(rel.parts) >= 2 and rel.parts[1] == "creativos":
            return rel.parts[0]
    except ValueError:
        pass
    try:
        return cliente_de(ctx.slug)
    except ValueError:
        return None


def _declared(ctx: QAContext, nombres: set[str]) -> Iterator[tuple[Any, str, str]]:
    """(item | None, entidad, ruta) de cada logo declarado."""
    from ..assets.logo import slug

    def walk(v: Any) -> Iterator[tuple[str, str]]:
        if isinstance(v, dict):
            ent = v.get("entity") or v.get("logo_entity")
            src = v.get("src") or v.get("asset") or v.get("path")
            if isinstance(ent, str) and isinstance(src, str):
                yield slug(ent), src
            for x in v.values():
                yield from walk(x)
        elif isinstance(v, list):
            for x in v:
                yield from walk(x)
    for it in ctx.timeline.items:
        for ent, src in walk(it.props):
            yield it, ent, src
    man = ctx.vdir.parent.parent / "assets.json"
    if man.exists() and nombres:
        try:
            assets = (json.loads(man.read_text(encoding="utf-8")) or {}).get("assets", {})
        except Exception:  # noqa: BLE001
            assets = {}
        for aid, a in assets.items():
            path = str(a.get("path", ""))
            if a.get("kind") not in ("svg", "image") or a.get("origin") == "logo":
                continue
            stem, ident = slug(Path(path).stem), slug(aid)
            for e in sorted(nombres, key=len, reverse=True):     # el nombre más largo gana («nimbo-crm» a «nimbo»)
                if stem.startswith(e) or ident.startswith(e):
                    yield None, e, path
                    break


def _resolve(ctx: QAContext, src: str) -> Path | None:
    p = Path(src)
    cands = [p] if p.is_absolute() else [ctx.vdir / "hf" / src, ctx.vdir / src, ctx.vdir.parent.parent / src, RAIZ / src]
    return next((c for c in cands if c.exists()), None)


def _abrir(path: Path, tmp: Path):
    from PIL import Image

    from ..assets.logo import a_png

    png, _ = a_png(path, tmp / f"{abs(hash(str(path)))}.png", 512)
    with Image.open(png) as im:
        return im.convert("RGBA")


def _evaluar(path: Path, refs: list[Path], tmp: Path) -> dict[str, Any]:
    from ..assets.library import sha256_file
    from ..assets.logo import LogoFailure

    sha = sha256_file(path)
    if any(sha256_file(r) == sha for r in refs):
        return {"status": "original", "ref": next(r.name for r in refs if sha256_file(r) == sha)}
    try:
        cand = _abrir(path, tmp)
    except LogoFailure as exc:
        return {"status": "sin_raster", "detalle": str(exc)}
    best: tuple[str, dict[str, Any]] | None = None
    sin_raster = []
    for r in refs:
        try:
            m = compare(cand, _abrir(r, tmp))
        except LogoFailure as exc:
            sin_raster.append(f"{r.name}: {exc}")
            continue
        if m and (best is None or (_RANK[m["veredicto"]], m["forma"]) > (_RANK[best[1]["veredicto"]], best[1]["forma"])):
            best = (r.name, m)
    if best is None:
        return {"status": "sin_raster" if sin_raster else "sin_comparar", "detalle": "; ".join(sin_raster)[:400]}
    return {"status": best[1]["veredicto"], "ref": best[0]} | {k: v for k, v in best[1].items() if k != "veredicto"}


def run(ctx: QAContext) -> None:
    from ..assets.logo import nombres_terceros, originales, slug

    cliente = _cliente(ctx)
    if not cliente:
        ctx.notes.append("Logos: el proyecto no es de ningún cliente (CUTKIT_RUNS), así que no hay originales con los "
                         "que comparar.")
        ctx.metrics["logos"] = []
        return
    nombres = set(nombres_terceros(cliente)) | {slug(cliente)}
    mdir = (marca_dir(cliente) or Path()).resolve()
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="ck-logos-") as td:
        tmp = Path(td)
        for it, ent, src in _declared(ctx, nombres):
            key = (ent, src)
            if key not in seen:
                res: dict[str, Any] = {"entity": ent, "src": src}
                path = _resolve(ctx, src)
                try:
                    refs = originales(ent, cliente)
                    if path is None:
                        res["status"] = "missing"
                    elif mdir in path.resolve().parents:
                        res["status"] = "original"
                    elif not refs:
                        res["status"] = "sin_original"
                    else:
                        res |= _evaluar(path, refs, tmp)
                except Exception as exc:  # noqa: BLE001 - un archivo o un marca.json roto no tumba la QA
                    res["status"] = f"error: {type(exc).__name__}: {str(exc)[:120]}"
                res["items"] = []
                seen[key] = res
            if it is not None:
                seen[key]["items"].append(it)
    base = f"clientes/{cliente}/marca"
    out = []
    for (ent, src), r in seen.items():
        items = r.pop("items")
        t0 = min((i.t0 for i in items), default=None)
        t1 = max((i.t1 for i in items), default=None)
        blame = [d for i in items for d in i.decision_ids]
        out.append(dict(r))
        donde = f"; aparece en {tc(t0)}–{tc(t1)}" if t0 is not None else ""
        ev = {k: v for k, v in r.items() if k != "src"} | {"src": src}
        fix = [{"op": "swap_asset", "src": src, "with": f'{{"kind": "logo", "query": "{ent}"}}'}]
        st = r["status"]
        if st == "distinto":
            ctx.add("logo.canonical", "block",
                    f"El logo de {ent} ({Path(src).name}) no es el original de {base} ({r.get('detalle')}){donde}.",
                    t0, t1, ev, blame, fix)
        elif st in ("dudoso", "color", "mono"):
            por = {"dudoso": "se parece pero no coincide en forma", "color": "tiene la forma pero no los colores",
                   "mono": "es una versión sin color que no está entre los originales"}[st]
            ctx.add("logo.canonical", "warn",
                    f"El logo de {ent} ({Path(src).name}) {por} ({r.get('detalle')}){donde}: revísalo o usa el "
                    f"original de {base}.", t0, t1, ev, blame, fix)
        elif st == "missing":
            ctx.add("logo.missing", "warn", f"No encuentro el archivo del logo de {ent}: {src}.", t0, t1, ev, blame)
        elif st == "sin_original":
            ctx.add("logo.unverified", "warn",
                    f"El logo de {ent} no está entre los originales del cliente: guarda el oficial en "
                    f"{base}/logos/{ent}.svg (o .png) y pídelo con kind «logo».", t0, t1, ev, blame,
                    [{"op": "add_original", "where": f"{base}/logos/{ent}.svg"}])
        elif st in ("sin_raster", "sin_comparar") or st.startswith("error"):
            ctx.add("logo.not_compared", "info",
                    f"No he podido comparar el logo de {ent} ({Path(src).name}) con su original: "
                    f"{r.get('detalle') or st}.", t0, t1, ev, blame)
    ctx.metrics["logos"] = out
