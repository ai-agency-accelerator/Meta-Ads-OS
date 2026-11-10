"""HTTP simulado para los tests de herramientas: sustituye `urllib.request.urlopen` y nunca sale a la red.

Uso:
    http = HttpSimulado()
    http.cuando("GET", r"/act_0+/campaigns$", {"data": [...]})
    http.cuando("POST", r"/events$", lambda p: {"events_received": 1})
    http.cuando("GET", r"/v1/customers$", [pagina1, pagina2])      # respuestas consumidas en orden
    http.cuando("GET", r"/contacts/x$", (401, {"message": "Invalid JWT"}))   # error HTTP
    monkeypatch.setattr(urllib.request, "urlopen", http)

Cada petición queda en `http.peticiones` con metodo, url, host, path, query, form, json y cabeceras (claves en
minúsculas). Una petición sin regla hace fallar el test.
"""
from __future__ import annotations

import io
import json
import re
import urllib.error
import urllib.parse


class _Respuesta:
    def __init__(self, cuerpo: bytes, url: str, status: int = 200):
        self._cuerpo = cuerpo
        self._url = url
        self.status = status

    def read(self, *_a) -> bytes:
        return self._cuerpo

    def geturl(self) -> str:
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *_a) -> bool:
        return False


class HttpSimulado:
    def __init__(self) -> None:
        self.reglas: list[list] = []
        self.peticiones: list[dict] = []

    def cuando(self, metodo: str, patron: str, respuesta) -> "HttpSimulado":
        cola = list(respuesta) if isinstance(respuesta, list) else None
        self.reglas.append([metodo.upper(), re.compile(patron), respuesta, cola])
        return self

    def de(self, metodo: str, patron: str) -> list[dict]:
        """Peticiones hechas con ese método cuyo path casa con el patrón."""
        r = re.compile(patron)
        return [p for p in self.peticiones if p["metodo"] == metodo.upper() and r.search(p["path"])]

    def __call__(self, peticion, timeout=None, **_kw):
        if isinstance(peticion, str):
            url, metodo, cuerpo, cabeceras = peticion, "GET", None, {}
        else:
            url, metodo, cuerpo = peticion.full_url, peticion.get_method(), peticion.data
            cabeceras = {k.lower(): v for k, v in peticion.header_items()}
        partes = urllib.parse.urlsplit(url)
        query = {k: v[0] if len(v) == 1 else v for k, v in urllib.parse.parse_qs(partes.query).items()}
        registro = {"metodo": metodo, "url": url, "host": partes.netloc, "path": partes.path, "query": query,
                    "cabeceras": cabeceras, "cuerpo": cuerpo, "form": {}, "json": None, "timeout": timeout}
        if isinstance(cuerpo, bytes):
            tipo = cabeceras.get("content-type", "")
            if "json" in tipo:
                registro["json"] = json.loads(cuerpo)
            elif "multipart" not in tipo:
                registro["form"] = {k: v[0] for k, v in urllib.parse.parse_qs(cuerpo.decode()).items()}
        self.peticiones.append(registro)
        for metodo_regla, patron, respuesta, cola in self.reglas:
            if metodo_regla != metodo or not patron.search(partes.path):
                continue
            if cola is not None:
                if not cola:
                    raise AssertionError(f"Sin más respuestas previstas para {metodo} {partes.path}")
                respuesta = cola.pop(0)
            if callable(respuesta):
                respuesta = respuesta(registro)
            if isinstance(respuesta, tuple):
                status, datos = respuesta
                raise urllib.error.HTTPError(url, status, "error", {}, io.BytesIO(json.dumps(datos).encode()))
            return _Respuesta(json.dumps(respuesta).encode(), url)
        raise AssertionError(f"Petición no prevista en el test: {metodo} {partes.path}")
