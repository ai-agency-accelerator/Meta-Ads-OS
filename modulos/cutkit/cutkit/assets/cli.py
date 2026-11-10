"""CLI de cutkit.assets (Typer). `app` se puede montar en `ck` como `ck assets …`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="Assets de edición: archivos, logos, capturas, scroll, stock y biblioteca",
                  no_args_is_help=True)


def _load_requests(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("requests", [])
    if not isinstance(data, list):
        raise typer.BadParameter("requests.json debe ser una lista de AssetRequest o {\"requests\": [...]}")
    return data


@app.command("resolve")
def resolve_cmd(
    slug: str = typer.Argument(..., help="Slug del vídeo (proyecto en clientes/<cliente>/creativos/<fecha>_<slug>/)"),
    requests: Path = typer.Option(..., "--requests", "-r", exists=True, help="JSON con las AssetRequest"),
    run_dir: Optional[Path] = typer.Option(None, "--run-dir",
                                           help="Carpeta de edición (por defecto <proyecto>/edicion)"),
    cliente: Optional[str] = typer.Option(None, "--cliente", help="Cliente de los logos (por defecto, el del proyecto)"),
    budget: float = typer.Option(2.0, "--budget", help="Tope en USD que se anota en el manifiesto "
                                                       "(cutkit no paga modelos: el B-roll con IA lo hace el motor)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Sin red: solo archivos, logos y lo que ya esté en la "
                                                          "biblioteca"),
    workers: int = typer.Option(4, "--workers", help="Peticiones en paralelo"),
    as_json: bool = typer.Option(False, "--json", help="Imprimir el manifiesto completo"),
):
    """Resuelve las peticiones y escribe <run_dir>/assets.json."""
    from .resolver import edit_dir, resolve

    m = resolve(slug, _load_requests(requests), run_dir, budget, dry_run=dry_run, workers=workers, cliente=cliente)
    if as_json:
        typer.echo(m.model_dump_json(indent=2))
        return
    for rid, a in m.assets.items():
        size = f"{a.width}x{a.height}" if a.width else "-"
        dur = f" {a.duration:.2f}s" if a.duration else ""
        reused = " (biblioteca)" if rid in m.reused else ""
        cost = f" {m.costs[rid]:.3f}$" if rid in m.costs else ""
        typer.echo(f"✔ {rid:<18} {a.kind:<5} {size:>11}{dur}{cost}{reused}  {a.path}")
    for rid, why in m.failed.items():
        typer.secho(f"✘ {rid:<18} {why}", fg=typer.colors.RED)
    typer.echo(f"gasto: {m.spent_usd:.3f} $ de {m.budget_usd:.2f} $ · manifiesto: {edit_dir(slug, run_dir) / 'assets.json'}")
    if m.failed:
        raise typer.Exit(1)


@app.command("probe")
def probe_cmd(path: Path = typer.Argument(..., exists=True)):
    """Medidas de un medio (ffprobe; SVG por su viewBox)."""
    from .probe import probe

    typer.echo(json.dumps(probe(path), ensure_ascii=False, indent=2))


@app.command("search")
def search_cmd(text: Optional[str] = typer.Argument(None), kind: Optional[str] = typer.Option(None, "--kind"),
               limit: int = typer.Option(30, "--limit")):
    """Busca en la biblioteca por tipo y texto (consulta, notas o URL)."""
    from . import library

    for r in library.search(kind, text, limit):
        used = len(json.loads(r.get("used_in") or "[]"))
        dims = f"{r['width']}x{r['height']}" if r.get("width") else "-"
        typer.echo(f"{r['sha256'][:12]} {r['kind']:<11} {dims:>11} usado×{used} {(r['query'] or '')[:50]!r}  "
                   f"{r['license'] or '-'}  {r['path']}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
