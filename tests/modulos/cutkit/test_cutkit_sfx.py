"""Biblioteca de SFX sintéticos (CC0): determinista, con licencia, catalogada y coherente con las reglas de eventos.

Se ejecuta con el Python de cutkit y escribe solo en una carpeta temporal (`CUTKIT_DATOS`).
"""
from __future__ import annotations

import re


def test_biblioteca_completa_catalogada_y_con_licencia(py_cutkit, tmp_path):
    r = py_cutkit("""
        import hashlib
        import numpy as np
        import yaml
        from cutkit.audio import sfx, sfx_sinteticos as s
        rutas = s.generar()
        ids = [i for i, _, _ in s._definiciones()]
        a, b = s.sintetizar("pop_1"), s.sintetizar("pop_1")
        picos = {i: float(20 * np.log10(np.abs(s.sintetizar(i)).max())) for i in ids}
        cat = sfx.catalog()
        reglas = [yaml.safe_load(f.read_text(encoding="utf-8")) for f in (sfx.EVENTOS, sfx.EVENTOS.parent / "animaciones.yaml")]
        salida({"ids": ids, "rutas": [str(p.relative_to(s.destino_por_defecto())) for p in rutas],
                "existen": all(p.exists() for p in rutas), "determinista": bool(np.array_equal(a, b)),
                "forma": list(a.shape), "finitos": all(np.isfinite(s.sintetizar(i)).all() for i in ids),
                "picos": picos, "licencia": (s.destino_por_defecto() / "LICENCIA.txt").read_text(encoding="utf-8"),
                "catalogo": {f["id"]: f["licencia"] for f in cat["ficheros"]}, "eventos": sorted(cat["eventos"]),
                "pop": [f["id"] for f in sfx.candidates("pop")], "reglas": reglas,
                "hash": hashlib.sha256(a.tobytes()).hexdigest()})
    """, timeout=300, CUTKIT_DATOS=str(tmp_path / "datos"))
    ids = r["ids"]
    assert len(ids) == len(set(ids)) == 31
    assert r["existen"] and all(re.fullmatch(r"[a-z_]+/[a-z_]+_\d\.wav", p) for p in r["rutas"])
    assert r["determinista"] and r["forma"][1] == 2 and r["finitos"]
    assert all(-3.5 <= v <= -2.5 for v in r["picos"].values()), r["picos"]          # normalizados a −3 dBFS
    assert "CC0" in r["licencia"] and "sin muestras de terceros" in r["licencia"]
    assert set(r["catalogo"]) == set(ids) and all("CC0" in v for v in r["catalogo"].values())
    assert r["eventos"] and set(r["pop"]) <= set(ids) and r["pop"]
    # toda referencia a un fichero en las reglas apunta a un id que existe (nada de nombres de otra biblioteca)
    citados = set()

    def recorrer(x):
        if isinstance(x, dict):
            for v in x.values():
                recorrer(v)
        elif isinstance(x, list):
            for v in x:
                recorrer(v)
        elif isinstance(x, str) and re.fullmatch(r"[a-z]+(?:_[a-z]+)*_\d+", x):
            citados.add(x)

    recorrer(r["reglas"])
    assert citados and citados <= set(ids), sorted(citados - set(ids))


def test_generar_es_idempotente_y_no_toca_la_biblioteca_por_defecto(py_cutkit, tmp_path):
    otra = tmp_path / "otra"
    r = py_cutkit(f"""
        from pathlib import Path
        from cutkit.audio import sfx, sfx_sinteticos as s
        d = Path({str(otra)!r})
        primera = s.generar(d)
        mtimes = [p.stat().st_mtime_ns for p in primera]
        segunda = s.generar(d)
        salida({{"n": len(primera), "iguales": mtimes == [p.stat().st_mtime_ns for p in segunda],
                 "catalogo_por_defecto": sfx.CATALOG.exists()}})
    """, CUTKIT_DATOS=str(tmp_path / "datos"))
    assert r["n"] == 31 and r["iguales"]                     # la segunda vez no reescribe nada
    assert not r["catalogo_por_defecto"]                     # un destino propio no rehace el catálogo general
