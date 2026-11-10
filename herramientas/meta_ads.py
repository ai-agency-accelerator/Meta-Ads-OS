#!/usr/bin/env python3
"""Meta Ads por cliente desde la terminal: leer la cuenta, montar campañas en pausa desde un plan y activarlas solo
con confirmación. Es la «vía avanzada» del diseño (§5.4): la usa `operador-meta` cuando hay que subir vídeo o imagen,
crear creatividades con las mejoras automáticas apagadas o montar un plan entero. Para lo demás, el MCP de Meta.

Leer (no cambia nada, no pregunta nada; vale para el brief diario):
  python3 -I herramientas/meta_ads.py cuentas [--cliente SLUG]          cuentas que ve el token (para sacar el act_…)
  python3 -I herramientas/meta_ads.py activos --cliente acme             página, Instagram, datasets y públicos
  python3 -I herramientas/meta_ads.py campanas --cliente acme            campañas con gasto, de la más reciente a la más antigua
  python3 -I herramientas/meta_ads.py vigente --cliente acme             lo que puede gastar ahora: presupuesto, gasto y resultados de 7 días
  python3 -I herramientas/meta_ads.py anuncios --cliente acme --desde 2026-11-02 --hasta 2026-11-08 [--por-dia] [--por-pais]
  python3 -I herramientas/meta_ads.py anuncios --cliente acme --mes 2026-10 [--campana TEXTO] [--acciones] [--estado]
  python3 -I herramientas/meta_ads.py eventos --cliente acme [--desde AAAA-MM-DD --hasta AAAA-MM-DD]
  python3 -I herramientas/meta_ads.py creatividades --cliente acme --campana-id <id> | --plan <plan.json>

Escribir (solo `operador-meta`, con un plan aprobado; los hooks piden confirmación y el change log es obligatorio):
  python3 -I herramientas/meta_ads.py crear <plan.json> --cliente acme --simular   revisa y dibuja el plan, sin red
  python3 -I herramientas/meta_ads.py crear <plan.json> --cliente acme             lo crea TODO EN PAUSA (0 de gasto)
  python3 -I herramientas/meta_ads.py pausar <id>… | --plan <plan.json> --cliente acme
  python3 -I herramientas/meta_ads.py activar <id>… | --plan <plan.json> --cliente acme --confirmo
  python3 -I herramientas/meta_ads.py presupuesto <id> <importe/día> --cliente acme --confirmo

Opciones comunes: `--cliente SLUG` (cuenta, moneda, zona horaria y topes salen de clientes/<slug>/ficha.md) y `--json`.
Las lecturas que escriben archivo aceptan `--sin-archivos` (solo salida por pantalla).

Topes (cabecera `topes` de la ficha, en la moneda de la ficha):
- `cambio_dia`: presupuesto diario máximo que puede fijar un único cambio o plan (`crear`, `activar`, `presupuesto`).
- `total_dia`: presupuesto diario máximo sumando todo lo que está activo en la cuenta (`activar`, `presupuesto`).
- A 0 significan «sin definir»: no se crea ni se sube presupuesto hasta fijarlos.

`crear` lee un plan (formato y explicación en plantillas/plan-campana.json), sube vídeos e imágenes y crea campaña,
conjuntos, creatividades y anuncios con estado PAUSED. Guarda los IDs en clientes/<slug>/planes/<plan>.estado.json:
si se corta, se vuelve a lanzar y sigue sin duplicar nada.
Para añadir anuncios a lo que ya existe, el plan lleva `id` en el conjunto (o `campana.id` para conjuntos nuevos en
una campaña existente): se comprueba que son de la cuenta, no se cambian, y `activar`/`pausar --plan` no los tocan.
Mejoras automáticas de Advantage+ creative, según `mejoras_automaticas` de la ficha (después de crear se lee qué
quedó activo y se avisa):
  off      todas en OPT_OUT (las de MEJORAS)
  revisar  solo product showcase (`product_extensions`, activo por defecto desde la v27) en OPT_OUT; el resto, lo que
           decida Meta
  on       lo que decida Meta
Claves del plan que no salen en todos los ejemplos:
  conjunto.optimizar          con destino formulario, LEAD_GENERATION (por defecto) o QUALITY_LEAD (Conversion
                              Leads: el conjunto optimiza a leads de calidad con el dataset que recibe las etapas
                              del CRM, `dataset_crm` del conjunto o del plan, o el de la ficha)
  expansion_dispositivos      (conjunto o plan) true deja a Meta entregar fuera del dispositivo o sistema operativo
                              segmentado en Ventas; por defecto se manda targeting_automation.individual_setting.device=0
  anuncio.publicacion_ig      ID del medio de Instagram: anuncio desde esa publicación (texto y medio, los publicados;
                              `url` y `cta` ponen el botón a la web). No vale IGTV ni reels con música con derechos
  anuncio.publicacion_fb      «<pagina>_<post>»: ídem con una publicación de la Página de Facebook
  api                         (campaña, conjunto o anuncio) parámetros de la API que el plan no cubre; se envían tal
                              cual salvo el estado (todo nace en PAUSED: otro valor es un error). Un presupuesto en
                              `api` solo vale como `lifetime_budget` (unidad mínima: céntimos) de un conjunto nuevo
                              sin CBO, con inicio y fin; cuenta para el tope repartido por días
Los anuncios de colaboración (con la identidad de un creador: /casos-y-creadores) y los carruseles siguen en Ads
Manager.

`anuncios` guarda los agregados por anuncio en clientes/<slug>/datos/ (CSV con las columnas de COLUMNAS: los
porcentajes van en %, los importes en la moneda de la cuenta, punto decimal) y saca el resumen por campaña. Con
`--estado` lista además los anuncios rechazados, con problemas o en revisión (DISAPPROVED, WITH_ISSUES,
PENDING_REVIEW) con su motivo, hayan gastado o no: sirve para ver rechazos sin el MCP.
Retención de vídeo (fórmulas fijas de meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md §2; hook rate y
hold rate no son métricas oficiales de Meta, son cocientes de métricas oficiales):
  hook_rate       = vistas de 3 s (acción `video_view`) / impresiones × 100
  hold_rate       = ThruPlays (`video_thruplay_watched_actions`) / vistas de 3 s × 100 — inflado en vídeos de ≤15 s,
                    que cuentan como ThruPlay al terminar: no compares el de un vídeo de 10 s con el de uno de 45 s
  retencion_pXX   = reproducciones hasta el XX % (`video_pXX_watched_actions`, XX = 25, 50, 75, 95, 100) / vistas de
                    3 s × 100 — en vídeos de menos de 12 s el 25 % llega antes de los 3 s y puede pasar de 100
  reproducciones  = `video_play_actions` (inicios de reproducción) · vistas_2s_continuas =
                    `video_continuous_2_sec_watched_actions` · tiempo_medio_s = `video_avg_time_watched_actions`
  curva_retencion = `video_play_curve_actions`: % de reproducciones que llegan a cada segundo, separados por «|»
                    (posiciones 0–14 = segundos 0 a 14; 15–17 = [15,20), [20,25), [25,30); 18–20 = [30,40),
                    [40,50), [50,60); 21 = más de 60 s)
Si Meta rechaza alguno de los campos de retención nuevos (error 100), se repite la petición sin ellos y se avisa: el
CSV sale igual, con esas columnas vacías.

Credenciales (`.env` en la raíz, nunca se imprimen):
  META_TOKEN          token de un usuario del sistema con ads_read y ads_management (docs/guias/token-avanzado.md).
                      Por cliente: META_TOKEN_<SLUG> (p. ej. META_TOKEN_CLINICA_SONRISA); si no, el global.
  META_APP_SECRET     opcional (también por cliente): solo si la app exige appsecret_proof.
  META_API_VERSION    opcional: por defecto la de VERSION.

Códigos de salida: 0 bien · 1 error del usuario (plan inválido, tope superado, falta --confirmo, Meta rechaza algo) ·
2 configuración (ficha, token, cuenta de ejemplo, moneda distinta).
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import hmac
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone, tzinfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun as comun  # noqa: E402

VERSION = "v27.0"  # desde el 2026-11-10 (salió el 2026-11-04); lo que cambia y lo revisado: docs/desarrollo/notas/I4.md
GRAPH = "https://graph.facebook.com"
GRAPH_VIDEO = "https://graph-video.facebook.com"
MAX_VIDEO = 1024 ** 3  # subida simple; por encima, expórtalo más ligero
REINTENTABLES = {1, 2, 4, 17, 341, 613, 80004}
LIMITES = {4, 17, 341, 613, 80004}  # al escribir solo se reintenta esto: reintentar un error genérico duplicaría objetos
# Monedas que Meta cuenta sin decimales (offset 1, developers.facebook.com/docs/marketing-api/currencies).
SIN_DECIMALES = {"CLP", "COP", "CRC", "HUF", "ISK", "IDR", "JPY", "KRW", "PYG", "TWD", "VND"}

# Objetivo de campaña → qué optimiza el conjunto por defecto (el plan puede cambiarlo con "optimizar").
OPTIMIZA = {"OUTCOME_LEADS": "OFFSITE_CONVERSIONS", "OUTCOME_SALES": "OFFSITE_CONVERSIONS",
            "OUTCOME_AWARENESS": "REACH", "OUTCOME_TRAFFIC": "LANDING_PAGE_VIEWS", "OUTCOME_ENGAGEMENT": "THRUPLAY"}
CTA_FORMULARIO = ("APPLY_NOW", "DOWNLOAD", "GET_QUOTE", "LEARN_MORE", "SIGN_UP", "SUBSCRIBE")
# Con formulario instantáneo el conjunto optimiza a leads (LEAD_GENERATION) o a leads de calidad con los datos del CRM
# (QUALITY_LEAD, Conversion Leads: `promoted_object` con la Página y el dataset que recibe las etapas del CRM).
OPTIMIZA_FORMULARIO = ("LEAD_GENERATION", "QUALITY_LEAD")
# Segmentación por dispositivo o sistema operativo. Desde la v27.0 (y en todas las versiones hacia feb-2027), en los
# conjuntos nuevos de Ventas Meta puede entregar fuera de lo segmentado («expansión de dispositivos») salvo
# `targeting_automation.individual_setting.device = 0`. `crear` lo manda salvo `"expansion_dispositivos": true`.
DISPOSITIVO = ("user_device", "user_os")
# Anuncio desde una publicación que ya existe (guía «Use posts as ads»): Instagram por el ID del medio, Facebook por
# «<pagina>_<post>». El texto y el medio son los de la publicación.
PUBLICACION = ("publicacion_ig", "publicacion_fb")
MEDIOS = ("video", "imagen", "video_id", "imagen_hash") + PUBLICACION
# Mejoras automáticas de Advantage+ creative que cambian lo que dice o enseña el anuncio. Lista de la documentación
# de Meta (Advantage+ creative → Get started y Add site links), comprobada el 2026-11-09. `standard_enhancements` está
# deprecado desde v22.0. Si Meta rechaza alguna clave al crear, se reintenta sin ella y la verificación posterior
# avisa de lo que haya quedado activo.
MEJORAS = ("adapt_to_placement", "add_text_overlay", "creative_stickers", "description_automation", "enhance_cta",
           "image_animation", "image_background_gen", "image_brightness_and_contrast", "image_templates",
           "image_text_translation", "image_touchups", "image_uncrop", "inline_comment", "media_type_automation",
           "pac_relaxation", "product_extensions", "reveal_details_over_time", "site_extensions",
           "text_optimizations", "text_translation", "translate_voiceover", "video_auto_crop", "video_filtering",
           "video_uncrop")

# UTMs dinámicas de Meta. Los IDs son la clave para unir con el CRM o Stripe (los nombres cambian). Con GHL,
# utm_source lleva «fb_ad» para que HighLevel clasifique el contacto como Paid Social (su ayuda, 2026-08-26); sin GHL,
# la plantilla de meta-ads-kb/13-sistema-operativo/10-plantillas.md §8.
_UTM_RESTO = ("&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_term={{adset.name}}"
              "&utm_content={{ad.name}}&campaign_id={{campaign.id}}&adset_id={{adset.id}}&ad_id={{ad.id}}"
              "&placement={{placement}}&site={{site_source_name}}")
UTM_GHL = "utm_source=fb_ad" + _UTM_RESTO
UTM_GENERICA = "utm_source=facebook" + _UTM_RESTO

# Qué action_type de Meta es el resultado de cada evento optimizado, por orden de preferencia.
ACCIONES = {
    "LEAD": ["lead", "offsite_conversion.fb_pixel_lead", "onsite_conversion.lead_grouped"],
    "COMPLETE_REGISTRATION": ["complete_registration", "offsite_conversion.fb_pixel_complete_registration"],
    "SCHEDULE": ["schedule_total", "schedule_website", "offsite_conversion.fb_pixel_schedule"],
    "PURCHASE": ["purchase", "omni_purchase", "offsite_conversion.fb_pixel_purchase"],
    "START_TRIAL": ["start_trial_total", "start_trial_website", "offsite_conversion.fb_pixel_start_trial"],
    "SUBSCRIBE": ["subscribe_total", "subscribe_website", "offsite_conversion.fb_pixel_subscribe"],
    "CONTACT": ["contact_total", "contact_website", "offsite_conversion.fb_pixel_contact"],
    "SUBMIT_APPLICATION": ["submit_application_total", "submit_application_website",
                           "offsite_conversion.fb_pixel_submit_application"],
}
LANDING = ["landing_page_view", "omni_landing_page_view"]
CAMPOS_BASE = ["ad_id", "ad_name", "adset_id", "adset_name", "campaign_id", "campaign_name", "spend", "impressions",
               "reach", "frequency", "inline_link_clicks", "actions", "conversions", "video_p25_watched_actions",
               "video_p50_watched_actions", "video_p75_watched_actions", "video_p100_watched_actions",
               "video_thruplay_watched_actions"]
# Retención de vídeo (B12). Nombres de la referencia de Insights de la Marketing API comprobados el 2026-11-09
# (docs/desarrollo/notas/B12.md). Si Meta rechaza alguno, `anuncios` repite la petición con CAMPOS_BASE.
CAMPOS_RETENCION = ["video_p95_watched_actions", "video_play_actions", "video_continuous_2_sec_watched_actions",
                    "video_avg_time_watched_actions", "video_play_curve_actions"]
CAMPOS = CAMPOS_BASE + CAMPOS_RETENCION
CUARTILES = (25, 50, 75, 95, 100)
COLUMNAS = ["ad_id", "anuncio", "campana_id", "campana", "conjunto_id", "conjunto", "desde", "hasta", "pais",
            "gasto", "impresiones", "alcance", "frecuencia", "cpm", "clics_enlace", "ctr", "vistas_landing",
            "vistas_3s", "thruplay", "hook_rate", "hold_rate", "video_p25", "video_p50", "video_p75", "video_p95",
            "video_p100", "reproducciones", "vistas_2s_continuas", "tiempo_medio_s", "retencion_p25",
            "retencion_p50", "retencion_p75", "retencion_p95", "retencion_p100", "curva_retencion",
            "evento_resultado", "resultado_meta", "coste_resultado_meta", "citas_meta"]


class ErrorMeta(Exception):
    """Meta rechazó la petición. `salida` es el código de salida que corresponde (2 = token o permisos)."""

    def __init__(self, mensaje: str, codigo=None, salida: int = 1):
        super().__init__(mensaje)
        self.codigo = codigo
        self.salida = salida


def _salir(mensaje: str, codigo: int) -> None:
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


# ---------------------------------------------------------------- cliente y conexión

@dataclass
class Contexto:
    slug: str
    ficha: dict
    cuenta: str
    moneda: str
    zona: tzinfo
    tope_cambio: float
    tope_total: float

    @property
    def cuenta_valida(self) -> bool:
        return bool(re.fullmatch(r"act_\d{5,}", self.cuenta)) and not re.fullmatch(r"act_0+", self.cuenta)


def _zona(nombre: str) -> tzinfo:
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(nombre)
    except Exception:  # Windows sin base de zonas horarias: hora local del equipo
        print(f"Aviso: no encuentro la zona horaria «{nombre}»; uso la del equipo.", file=sys.stderr)
        return datetime.now().astimezone().tzinfo or timezone.utc


def contexto(slug: str | None) -> Contexto:
    if not slug:
        _salir("Falta --cliente <slug> (la cuenta, la moneda y los topes salen de su ficha).", 1)
    try:
        ficha = comun.leer_ficha(slug)
    except comun.FichaInvalida as e:
        _salir(str(e), 2)
    meta = ficha.get("meta") or {}
    cuenta = str(meta.get("cuenta") or "").strip()
    if cuenta and not cuenta.startswith("act_"):
        cuenta = f"act_{cuenta}"
    topes = ficha.get("topes") or {}
    try:
        tope_cambio, tope_total = float(topes.get("cambio_dia") or 0), float(topes.get("total_dia") or 0)
    except (TypeError, ValueError):
        _salir(f"Los topes de la ficha de {slug} tienen que ser números.", 2)
    return Contexto(slug, ficha, cuenta, str(ficha.get("moneda") or "EUR").upper(),
                    _zona(str(ficha.get("zona_horaria") or "UTC")), tope_cambio, tope_total)


def a_minimo(importe: float, moneda: str) -> int:
    """Importe → unidad mínima de la moneda (céntimos salvo las monedas sin decimales)."""
    return round(importe * (1 if moneda in SIN_DECIMALES else 100))


def de_minimo(valor, moneda: str) -> float | None:
    if valor in (None, "", "0", 0):
        return None
    return int(valor) / (1 if moneda in SIN_DECIMALES else 100)


class Meta:
    def __init__(self, token: str, cuenta: str = "", app_secret: str | None = None, version: str | None = None):
        self.token = token
        self.version = version or os.environ.get("META_API_VERSION") or VERSION
        self.proof = hmac.new(app_secret.encode(), token.encode(), hashlib.sha256).hexdigest() if app_secret else None
        self.cuenta = cuenta

    def _firma(self, params: dict) -> dict:
        params = {k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                  for k, v in params.items() if v is not None}
        params["access_token"] = self.token
        if self.proof:
            params["appsecret_proof"] = self.proof
        return params

    def _url(self, ruta: str, params: dict) -> str:
        return f"{GRAPH}/{self.version}/{ruta}?{urllib.parse.urlencode(self._firma(params))}"

    def _pide(self, peticion, reintentables: set[int], timeout: int = 90) -> dict:
        for intento in range(3):
            try:
                with urllib.request.urlopen(peticion, timeout=timeout) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                try:
                    err = json.load(e).get("error", {})
                except ValueError:
                    err = {"message": f"HTTP {e.code}"}
                codigo = err.get("code")
                if codigo in reintentables and intento < 2:
                    time.sleep(20 * (intento + 1))
                    continue
                if codigo == 190:
                    raise ErrorMeta("Meta rechaza el token (caducado o revocado): genera otro "
                                    "(docs/guias/token-avanzado.md) y cámbialo en .env.", codigo, 2) from None
                detalle = " · ".join(x for x in (err.get("error_user_title"), err.get("error_user_msg")) if x)
                salida = 2 if codigo in (10, 200, 294) or (isinstance(codigo, int) and 200 <= codigo < 300) else 1
                raise ErrorMeta(f"Error de Meta ({codigo}/{err.get('error_subcode')}): {err.get('message')}"
                                + (f"\n  {detalle}" if detalle else ""), codigo, salida) from None
            except urllib.error.URLError as e:
                if intento < 2 and not isinstance(peticion, urllib.request.Request):
                    time.sleep(5)
                    continue
                raise ErrorMeta(f"No se pudo conectar con Meta: {e.reason}") from None
        raise AssertionError("inalcanzable")

    def uno(self, ruta: str, **params) -> dict:
        return self._pide(self._url(ruta, params), REINTENTABLES)

    def lista(self, ruta: str, **params):
        url: str | None = self._url(ruta, params)
        while url:
            datos = self._pide(url, REINTENTABLES)
            yield from datos.get("data", [])
            url = datos.get("paging", {}).get("next")
            if url and self.proof and "appsecret_proof=" not in url:
                url += f"&appsecret_proof={self.proof}"

    def escribe(self, ruta: str, **params) -> dict:
        """POST que crea o cambia algo. Solo reintenta cuando Meta corta por límite de llamadas."""
        cuerpo = urllib.parse.urlencode(self._firma(params)).encode()
        return self._pide(urllib.request.Request(f"{GRAPH}/{self.version}/{ruta}", data=cuerpo, method="POST",
                                                 headers={"Content-Type": "application/x-www-form-urlencoded"}),
                          LIMITES)

    def sube_imagen(self, ruta: pathlib.Path) -> str:
        datos = self.escribe(f"{self.cuenta}/adimages", bytes=base64.b64encode(ruta.read_bytes()).decode())
        return next(iter(datos["images"].values()))["hash"]

    def sube_video(self, ruta: pathlib.Path) -> str:
        if ruta.stat().st_size > MAX_VIDEO:
            raise ErrorMeta(f"{ruta.name} pasa de 1 GB: expórtalo más ligero.")
        limite = f"----{uuid.uuid4().hex}"
        partes = [f'--{limite}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                  for k, v in self._firma({"name": ruta.stem}).items()]
        partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="source"; filename="{ruta.name}"\r\n'
                      f"Content-Type: video/mp4\r\n\r\n".encode() + ruta.read_bytes() + f"\r\n--{limite}--\r\n".encode())
        peticion = urllib.request.Request(f"{GRAPH_VIDEO}/{self.version}/{self.cuenta}/advideos",
                                          data=b"".join(partes), method="POST",
                                          headers={"Content-Type": f"multipart/form-data; boundary={limite}"})
        return self._pide(peticion, LIMITES, timeout=900)["id"]

    def espera_video(self, video_id: str, nombre: str) -> None:
        for _ in range(120):  # hasta 10 min de procesado
            estado = self.uno(video_id, fields="status").get("status", {})
            if estado.get("video_status") == "ready":
                return
            if estado.get("video_status") == "error":
                raise ErrorMeta(f"Meta no pudo procesar {nombre}: {estado}")
            time.sleep(5)
        raise ErrorMeta(f"{nombre} sigue procesándose en Meta tras 10 min: vuelve a lanzar `crear` más tarde.")

    def miniatura(self, video_id: str) -> str:
        fotos = list(self.lista(f"{video_id}/thumbnails", fields="uri,is_preferred"))
        if not fotos:
            raise ErrorMeta(f"El vídeo {video_id} no tiene miniatura: pon \"miniatura\" en el anuncio.")
        return next((f for f in fotos if f.get("is_preferred")), fotos[0])["uri"]


def conectar(ctx: Contexto | None, requiere_cuenta: bool = True) -> Meta:
    slug = ctx.slug if ctx else None
    token = comun.credencial("META_TOKEN", slug)
    if not token:
        var = f"META_TOKEN_{slug.upper().replace('-', '_')} o META_TOKEN" if slug else "META_TOKEN"
        _salir(f"Falta {var} en .env. Es el token de un usuario del sistema: docs/guias/token-avanzado.md. "
               "Sin él, trabaja con el MCP de Meta.", 2)
    if ctx and requiere_cuenta and not ctx.cuenta_valida:
        _salir(f"La ficha de {ctx.slug} no tiene una cuenta real en meta.cuenta (act_…). "
               "Sácala con `meta_ads.py cuentas`.", 2)
    return Meta(token, ctx.cuenta if ctx else "", comun.credencial("META_APP_SECRET", slug))


def _comprueba_moneda(meta: Meta, ctx: Contexto, estricto: bool) -> None:
    moneda = meta.uno(ctx.cuenta, fields="currency").get("currency")
    if moneda and moneda != ctx.moneda:
        msg = (f"La cuenta {ctx.cuenta} factura en {moneda} y la ficha dice {ctx.moneda}: corrige la ficha "
               "(los presupuestos y los topes van en la moneda de la cuenta).")
        if estricto:
            _salir(msg, 2)
        print(f"Aviso: {msg}", file=sys.stderr)


# ---------------------------------------------------------------- métricas

def _acciones(r: dict) -> dict[str, float]:
    """Acciones y conversiones juntas: algunas (las citas) solo vienen en `conversions`."""
    acc = {x["action_type"]: float(x["value"]) for x in r.get("conversions") or []}
    return acc | {x["action_type"]: float(x["value"]) for x in r.get("actions") or []}


def _primera(acc: dict[str, float], tipos: list[str]) -> str | None:
    return next((t for t in tipos if acc.get(t)), None)


def _evento(acc: dict[str, float], optimizado: str | None = None) -> str | None:
    """El resultado: lo que optimizaban los conjuntos; si no se sabe, Lead o CompleteRegistration (el mayor)."""
    if optimizado and optimizado.startswith("offsite_conversion.custom."):
        return optimizado if acc.get(optimizado) else None
    if optimizado in ACCIONES and (tipo := _primera(acc, ACCIONES[optimizado])):
        return tipo
    candidatos = [t for t in (_primera(acc, ACCIONES["LEAD"]), _primera(acc, ACCIONES["COMPLETE_REGISTRATION"])) if t]
    return max(candidatos, key=acc.__getitem__, default=None)


def _cita(acc: dict[str, float]) -> str | None:
    return _primera(acc, ACCIONES["SCHEDULE"]) or next((t for t in acc if "schedule" in t), None)


def _video(r: dict, campo: str) -> int:
    return int(sum(float(x["value"]) for x in r.get(campo) or []))


def _pct(a: float, b: float) -> float | str:
    return round(a / b * 100, 2) if b else ""


def _tiempo_medio(r: dict) -> float | str:
    """Segundos de `video_avg_time_watched_actions` (Meta lo da como media; vacío si no hay vídeo)."""
    for x in r.get("video_avg_time_watched_actions") or []:
        try:
            return round(float(x["value"]), 2)
        except (KeyError, TypeError, ValueError):
            continue
    return ""


def _curva(r: dict) -> str:
    """`video_play_curve_actions` (AdsHistogramStats): la lista de porcentajes, separada por «|»."""
    for x in r.get("video_play_curve_actions") or []:
        valor = x.get("value") if isinstance(x, dict) else None
        if isinstance(valor, str):
            valor = [v for v in re.split(r"[,;| ]+", valor.strip("[]")) if v]
        if isinstance(valor, list) and valor:
            try:
                return "|".join(str(round(float(v))) for v in valor)
            except (TypeError, ValueError):
                return ""
    return ""


def fila_anuncio(r: dict, evento: str | None, cita: str | None, sin_retencion: bool = False) -> dict:
    """`sin_retencion`: la petición se repitió sin CAMPOS_RETENCION; sus columnas van vacías, no a 0."""
    acc = _acciones(r)
    gasto = float(r.get("spend") or 0)
    imp = int(r.get("impressions") or 0)
    clics = int(r.get("inline_link_clicks") or 0)
    resultados = int(acc.get(evento, 0)) if evento else 0
    landing = _primera(acc, LANDING)
    vistas_3s = int(acc.get("video_view", 0))
    thruplay = _video(r, "video_thruplay_watched_actions")
    pasos = {q: _video(r, f"video_p{q}_watched_actions") for q in CUARTILES}
    retencion = {f"retencion_p{q}": _pct(pasos[q], vistas_3s) if vistas_3s else "" for q in CUARTILES}
    return {
        "ad_id": r.get("ad_id", ""), "anuncio": r.get("ad_name", ""),
        "campana_id": r.get("campaign_id", ""), "campana": r.get("campaign_name", ""),
        "conjunto_id": r.get("adset_id", ""), "conjunto": r.get("adset_name", ""),
        "desde": r.get("date_start", ""), "hasta": r.get("date_stop", ""), "pais": r.get("country", ""),
        "gasto": round(gasto, 2), "impresiones": imp, "alcance": int(r.get("reach") or 0),
        "frecuencia": round(float(r.get("frequency") or 0), 2),
        "cpm": round(gasto / imp * 1000, 2) if imp else "", "clics_enlace": clics, "ctr": _pct(clics, imp),
        "vistas_landing": int(acc[landing]) if landing else 0, "vistas_3s": vistas_3s, "thruplay": thruplay,
        "hook_rate": _pct(vistas_3s, imp) if vistas_3s else "",      # vistas de 3 s / impresiones
        "hold_rate": _pct(thruplay, vistas_3s) if vistas_3s else "",  # ThruPlay / vistas de 3 s
        "video_p25": pasos[25], "video_p50": pasos[50], "video_p75": pasos[75], "video_p95": pasos[95],
        "video_p100": pasos[100], "reproducciones": _video(r, "video_play_actions"),
        "vistas_2s_continuas": _video(r, "video_continuous_2_sec_watched_actions"),
        "tiempo_medio_s": _tiempo_medio(r), **retencion,  # retencion_pXX = reproducciones hasta el XX % / vistas de 3 s
        "curva_retencion": _curva(r),
        **({c: "" for c in ("video_p95", "retencion_p95", "reproducciones", "vistas_2s_continuas", "tiempo_medio_s",
                            "curva_retencion")} if sin_retencion else {}),
        "evento_resultado": evento or "", "resultado_meta": resultados,
        "coste_resultado_meta": round(gasto / resultados, 2) if resultados else "",
        "citas_meta": int(acc.get(cita, 0)) if cita else "",
    }


# ---------------------------------------------------------------- salida

def _n(x: float, dec: int = 0) -> str:
    """Número a la española: 1.234,56."""
    return f"{x:,.{dec}f}".replace(",", "·").replace(".", ",").replace("·", ".")


def _json(datos) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2, default=str))


def resumen_por_campana(filas: list[dict]) -> list[dict]:
    grupos: dict[str, list[dict]] = defaultdict(list)
    for f in filas:
        grupos[f["campana"]].append(f)
    salida = []
    for nombre, fs in [*sorted(grupos.items()), ("TOTAL", filas)]:
        g = sum(f["gasto"] for f in fs)
        imp = sum(f["impresiones"] for f in fs)
        clics = sum(f["clics_enlace"] for f in fs)
        res = sum(f["resultado_meta"] for f in fs)
        con_citas = [f for f in fs if f["citas_meta"] != ""]
        citas = sum(f["citas_meta"] for f in con_citas)
        g_citas = sum(f["gasto"] for f in con_citas)  # coste por cita solo con el gasto de lo que mide citas
        salida.append({"campana": nombre, "gasto": round(g, 2), "impresiones": imp,
                       "cpm": round(g / imp * 1000, 2) if imp else None, "clics_enlace": clics,
                       "ctr": round(clics / imp * 100, 2) if imp else None,
                       "vistas_landing": sum(f["vistas_landing"] for f in fs), "resultados": res,
                       "coste_resultado": round(g / res, 2) if res else None,
                       "citas_meta": citas if con_citas else None,
                       "coste_cita_meta": round(g_citas / citas, 2) if citas else None})
    return salida


def _imprime_resumen(resumen: list[dict], moneda: str) -> None:
    cab = (f"{'Campaña':<34}{'Gasto':>11}{'Impr.':>10}{'CPM':>8}{'Clics':>7}{'CTR %':>7}{'Landing':>9}"
           f"{'Result.':>8}{'Coste':>8}{'Citas':>7}{'€/cita' if moneda == 'EUR' else 'x/cita':>9}")
    print(cab)
    print("-" * len(cab))
    for x in resumen:
        if x["campana"] == "TOTAL":
            print("-" * len(cab))
        print(f"{x['campana'][:33]:<34}{_n(x['gasto'], 2):>11}{_n(x['impresiones']):>10}"
              f"{_n(x['cpm'], 2) if x['cpm'] is not None else '—':>8}{_n(x['clics_enlace']):>7}"
              f"{_n(x['ctr'], 2) if x['ctr'] is not None else '—':>7}{_n(x['vistas_landing']):>9}"
              f"{_n(x['resultados']):>8}{_n(x['coste_resultado'], 2) if x['coste_resultado'] else '—':>8}"
              f"{_n(x['citas_meta']) if x['citas_meta'] is not None else '—':>7}"
              f"{_n(x['coste_cita_meta'], 2) if x['coste_cita_meta'] else '—':>9}")


def _rel(ruta: pathlib.Path) -> str:
    try:
        return str(ruta.relative_to(comun.RAIZ))
    except ValueError:
        return str(ruta)


def fila_change_log(nivel: str, objeto: str, cambio: str, dias_evaluacion: int = 7) -> str:
    """Fila lista para pegar en clientes/<slug>/change-log.md (contrato §5). Motivo y métrica los pone quien decide."""
    ahora = datetime.now()
    return (f"| {ahora:%Y-%m-%d %H:%M} | operador-meta (meta_ads.py) | {nivel} | {objeto} | {cambio} "
            f"| <motivo / hipótesis> | <métrica de éxito> | {(ahora + timedelta(days=dias_evaluacion)):%Y-%m-%d} | |")


# ---------------------------------------------------------------- leer

def cmd_cuentas(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente) if a.cliente else None
    meta = conectar(ctx, requiere_cuenta=False)
    estados = {1: "activa", 2: "desactivada", 3: "pago pendiente", 7: "en revisión", 9: "en periodo de gracia",
               100: "pendiente de cierre", 101: "cerrada"}
    filas = [{"id": c["id"], "nombre": c.get("name", ""), "moneda": c.get("currency", ""),
              "zona_horaria": c.get("timezone_name", ""),
              "estado": estados.get(c.get("account_status"), c.get("account_status"))}
             for c in meta.lista("me/adaccounts", fields="id,name,account_status,currency,timezone_name", limit=100)]
    if a.json:
        return _json(filas)
    if not filas:
        print("El token no ve ninguna cuenta publicitaria: asigna la cuenta al usuario del sistema "
              "(docs/guias/token-avanzado.md).")
    for c in filas:
        marca = "  ← ficha" if ctx and c["id"] == ctx.cuenta else ""
        print(f"{c['id']:<24}{c['nombre'][:40]:<42}{c['moneda']:<5}{c['zona_horaria']:<22}{c['estado']}{marca}")


def cmd_activos(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente)
    meta = conectar(ctx)
    info = meta.uno(ctx.cuenta, fields="name,currency,spend_cap,amount_spent")
    moneda = info.get("currency") or ctx.moneda
    tope_cuenta = de_minimo(info.get("spend_cap"), moneda)
    bloques = [("paginas", "promote_pages", "id,name", lambda x: x.get("name", "")),
               ("instagram", "instagram_accounts", "id,username", lambda x: "@" + x.get("username", "")),
               ("datasets", "adspixels", "id,name,last_fired_time",
                lambda x: f"{x.get('name', '')} · último evento {(x.get('last_fired_time') or '—')[:16]}"),
               ("publicos", "customaudiences", "id,name,subtype,approximate_count_lower_bound",
                lambda x: f"{x.get('name', '')} · {x.get('subtype', '')} · ≥{_n(x.get('approximate_count_lower_bound') or 0)}")]
    datos = {clave: list(meta.lista(f"{ctx.cuenta}/{ruta}", fields=campos, limit=200))
             for clave, ruta, campos, _ in bloques}
    if a.json:
        return _json({"cuenta": ctx.cuenta, "nombre": info.get("name"), "moneda": moneda,
                      "gastado_total": de_minimo(info.get("amount_spent"), moneda),
                      "limite_gasto_cuenta": tope_cuenta, "topes_ficha": {"cambio_dia": ctx.tope_cambio,
                                                                          "total_dia": ctx.tope_total}, **datos})
    print(f"{info.get('name')} ({ctx.cuenta}, {moneda}) · gastado en total "
          f"{_n(de_minimo(info.get('amount_spent'), moneda) or 0, 2)} · límite de gasto de la cuenta: "
          f"{_n(tope_cuenta, 2) if tope_cuenta else 'NINGUNO (ponlo con /configurar-meta)'} · topes de la ficha: "
          f"{_n(ctx.tope_cambio)} por cambio, {_n(ctx.tope_total)} al día en total\n")
    titulos = {"paginas": "Páginas (pagina_id)", "instagram": "Instagram (instagram_id)",
               "datasets": "Datasets / píxeles (pixel_id)", "publicos": "Públicos personalizados"}
    for clave, _, _, fmt in bloques:
        print(titulos[clave])
        for x in datos[clave]:
            print(f"  {x['id']:<22}{fmt(x)}")
        print()


def cmd_campanas(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente)
    meta = conectar(ctx)
    info = {c["id"]: c for c in meta.lista(
        f"{ctx.cuenta}/campaigns", fields="id,objective,effective_status,start_time,stop_time,created_time", limit=200)}
    filas = []
    for g in meta.lista(f"{ctx.cuenta}/insights", level="campaign", date_preset="maximum",
                        fields="campaign_id,campaign_name,spend,impressions", limit=500):
        c = info.get(g["campaign_id"], {})
        filas.append({"inicio": (c.get("start_time") or c.get("created_time") or "")[:10],
                      "fin": (c.get("stop_time") or "")[:10], "gasto": round(float(g.get("spend") or 0), 2),
                      "campana": g.get("campaign_name", ""), "objetivo": c.get("objective", ""),
                      "estado": c.get("effective_status", "archivada/borrada"), "id": g["campaign_id"]})
    filas.sort(key=lambda f: (f["inicio"], f["gasto"]), reverse=True)
    if a.json:
        return _json(filas)
    print(f"{'Inicio':<12}{'Fin':<12}{'Gasto':>11}  {'Campaña':<40}{'Objetivo':<22}{'Estado':<20}id")
    for f in filas:
        print(f"{f['inicio']:<12}{f['fin']:<12}{_n(f['gasto'], 2):>11}  {f['campana'][:39]:<40}"
              f"{f['objetivo'][:21]:<22}{f['estado'][:19]:<20}{f['id']}")


def _fin(x: dict) -> datetime | None:
    """Fin de un conjunto (end_time) o de una campaña (stop_time), en cualquier Python ≥ 3.8 (hallazgo 22, I6)."""
    return comun.fecha_iso(x.get("end_time") or x.get("stop_time"))


def diario_de(x: dict, moneda: str, ahora: datetime) -> float:
    """Ritmo diario de un conjunto o una campaña: `daily_budget`, o el presupuesto total (lo que le queda,
    `budget_remaining`, si Meta lo da) repartido entre los días que le quedan, desde ahora o desde su inicio si aún
    no ha empezado (días completos, mínimo 1). Sin fin conocido, el total en un día (nunca se subestima); ya
    terminado, 0. Hallazgo 8, I6:
    antes un presupuesto total contaba 0 para los topes."""
    diario = de_minimo(x.get("daily_budget"), moneda)
    if diario:
        return diario
    total = de_minimo(x.get("budget_remaining"), moneda) or de_minimo(x.get("lifetime_budget"), moneda)
    if not total or not de_minimo(x.get("lifetime_budget"), moneda):
        return 0.0
    fin = _fin(x)
    if fin is None:
        return total
    if fin.tzinfo is None:
        fin = fin.replace(tzinfo=ahora.tzinfo)
    inicio = comun.fecha_iso(x.get("start_time"))
    if inicio is not None and inicio.tzinfo is None:
        inicio = inicio.replace(tzinfo=ahora.tzinfo)
    desde = max(ahora, inicio) if inicio else ahora
    segundos = (fin - desde).total_seconds()
    if fin <= ahora or segundos <= 0:
        return 0.0
    # Días completos que quedan (mínimo 1): redondear hacia abajo sobrestima el ritmo, nunca lo subestima.
    return total / max(1, int(segundos // 86400))


CAMPOS_PRESUPUESTO = "daily_budget,lifetime_budget,budget_remaining,start_time"


def presupuesto_activo(meta: Meta, ctx: Contexto) -> tuple[float, list[dict]]:
    """Ritmo diario que puede gastar la cuenta ahora (conjuntos activos y sin terminar, con sus presupuestos
    diarios o totales y los de sus campañas CBO) y esos conjuntos."""
    ahora = datetime.now(timezone.utc)
    conjuntos = [c for c in meta.lista(
        f"{ctx.cuenta}/adsets", effective_status=["ACTIVE"], limit=200,
        fields=f"id,name,{CAMPOS_PRESUPUESTO},end_time,promoted_object,"
               f"campaign{{id,name,{CAMPOS_PRESUPUESTO},stop_time,effective_status}}")
        if not _fin(c) or _fin(c) > ahora]
    total = sum(diario_de(c, ctx.moneda, ahora) for c in conjuntos)
    cbo = {c["campaign"]["id"]: diario_de(c["campaign"], ctx.moneda, ahora) for c in conjuntos}
    return total + sum(cbo.values()), conjuntos


def cmd_vigente(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente)
    meta = conectar(ctx)
    total, conjuntos = presupuesto_activo(meta, ctx)
    datos = {}
    if conjuntos:
        datos = {r["adset_id"]: r for r in meta.lista(
            f"{ctx.cuenta}/insights", level="adset", date_preset="last_7d", limit=500,
            fields="adset_id,spend,impressions,frequency,actions,conversions",
            filtering=[{"field": "adset.id", "operator": "IN", "value": [c["id"] for c in conjuntos]}])}
    filas = []
    for c in sorted(conjuntos, key=lambda c: (c["campaign"]["name"], c["name"])):
        r = datos.get(c["id"], {})
        acc = _acciones(r)
        po = c.get("promoted_object") or {}
        ev = _evento(acc, f"offsite_conversion.custom.{po['custom_conversion_id']}"
                     if po.get("custom_conversion_id") else po.get("custom_event_type"))
        res = int(acc.get(ev, 0)) if ev else 0
        gasto = float(r.get("spend") or 0)
        filas.append({"campana": c["campaign"]["name"], "conjunto": c["name"], "id": c["id"],
                      "presupuesto_dia": diario_de(c, ctx.moneda, datetime.now(timezone.utc))
                      or diario_de(c["campaign"], ctx.moneda, datetime.now(timezone.utc)) or None,
                      "presupuesto_de": "conjunto" if c.get("daily_budget") else (
                          "campaña" if c["campaign"].get("daily_budget") else "total"),
                      "fin": (c.get("end_time") or "")[:10], "gasto_7d": round(gasto, 2), "resultados_7d": res,
                      "evento": ev or "", "coste_resultado_7d": round(gasto / res, 2) if res else None,
                      "frecuencia_7d": round(float(r.get("frequency") or 0), 2)})
    if a.json:
        return _json({"cuenta": ctx.cuenta, "moneda": ctx.moneda, "presupuesto_diario_activo": round(total, 2),
                      "tope_total_dia": ctx.tope_total, "conjuntos": filas})
    if not filas:
        print("No hay nada entregando ahora: ningún conjunto activo sin terminar.")
        return
    print(f"{'Campaña':<30}{'Conjunto':<28}{'/día':>8}{'Fin':>12}{'Gasto 7d':>10}{'Result.':>8}{'Coste':>8}{'Frec.':>7}")
    for f in filas:
        print(f"{f['campana'][:29]:<30}{f['conjunto'][:27]:<28}"
              f"{_n(f['presupuesto_dia'], 2) if f['presupuesto_dia'] else '—':>8}{f['fin']:>12}"
              f"{_n(f['gasto_7d'], 2):>10}{f['resultados_7d']:>8}"
              f"{_n(f['coste_resultado_7d'], 2) if f['coste_resultado_7d'] else '—':>8}{_n(f['frecuencia_7d'], 2):>7}")
    aviso = f" (tope de la ficha: {_n(ctx.tope_total, 2)})" if ctx.tope_total else ""
    print(f"\nPresupuesto diario en marcha: {_n(total, 2)} {ctx.moneda}{aviso}. "
          "Los presupuestos totales (lifetime) no se suman.")


def _fechas(a: argparse.Namespace) -> tuple[str | None, str | None]:
    try:
        if a.mes:
            ini = date.fromisoformat(f"{a.mes}-01")
            fin = (ini.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            return ini.isoformat(), fin.isoformat()
        if a.hasta and not a.desde:
            _salir("--hasta necesita --desde.", 1)
        if a.desde:
            return (date.fromisoformat(a.desde).isoformat(),
                    date.fromisoformat(a.hasta or date.today().isoformat()).isoformat())
    except ValueError:
        _salir("Fechas como AAAA-MM-DD y mes como AAAA-MM.", 1)
    return None, None


def _optimizados(meta: Meta, cuenta: str, campanas: list[str]) -> dict[str, str]:
    """El evento que optimizaban los conjuntos de cada campaña (el más repetido)."""
    cuentas: dict[str, Counter] = defaultdict(Counter)
    for c in meta.lista(f"{cuenta}/adsets", fields="campaign_id,promoted_object", limit=500,
                        filtering=[{"field": "campaign.id", "operator": "IN", "value": campanas}]):
        po = c.get("promoted_object") or {}
        if po.get("custom_conversion_id"):
            cuentas[c["campaign_id"]][f"offsite_conversion.custom.{po['custom_conversion_id']}"] += 1
        elif ev := po.get("custom_event_type"):
            cuentas[c["campaign_id"]][ev] += 1
    return {c: n.most_common(1)[0][0] for c, n in cuentas.items()}


# Estados de entrega que piden mirar el anuncio: rechazado, con problemas o en revisión.
PROBLEMAS = ["DISAPPROVED", "WITH_ISSUES", "PENDING_REVIEW"]


def anuncios_con_problemas(meta: Meta, ctx: Contexto, a: argparse.Namespace) -> list[dict]:
    """Anuncios rechazados, con problemas o en revisión, tengan o no entrega en el periodo (los insights no los
    traen si no han gastado). Mismo filtro de campaña que `anuncios`."""
    filas = []
    for r in meta.lista(f"{ctx.cuenta}/ads", fields="id,name,effective_status,campaign_id,campaign{name},issues_info,"
                        "ad_review_feedback", effective_status=PROBLEMAS, limit=200):
        campana = (r.get("campaign") or {}).get("name", "")
        if a.campana_id and str(r.get("campaign_id")) not in a.campana_id:
            continue
        if a.campana and a.campana.lower() not in campana.lower():
            continue
        motivos = [i.get("error_summary") or i.get("error_message") for i in r.get("issues_info") or []]
        motivos += [str(v) for v in ((r.get("ad_review_feedback") or {}).get("global") or {}).values()]
        filas.append({"ad_id": r.get("id"), "anuncio": r.get("name", ""), "campana_id": r.get("campaign_id"),
                      "campana": campana, "estado": r.get("effective_status"),
                      "motivo": " · ".join(m for m in motivos if m)[:300]})
    return sorted(filas, key=lambda f: (f["estado"], f["campana"], f["anuncio"]))


def cmd_anuncios(a: argparse.Namespace) -> None:
    if a.mes and (a.desde or a.hasta):
        _salir("--mes no se combina con --desde/--hasta.", 1)
    ctx = contexto(a.cliente)
    meta = conectar(ctx)
    desde, hasta = _fechas(a)
    params: dict = {"level": "ad", "fields": ",".join(CAMPOS), "use_unified_attribution_setting": "true",
                    "limit": 500}
    if desde:
        params["time_range"] = {"since": desde, "until": hasta}
    else:
        params["date_preset"] = "maximum"
    filtros = []
    if a.campana:
        filtros.append({"field": "campaign.name", "operator": "CONTAIN", "value": a.campana})
    if a.campana_id:
        filtros.append({"field": "campaign.id", "operator": "IN", "value": a.campana_id})
    if filtros:
        params["filtering"] = filtros
    if a.por_pais:
        params["breakdowns"] = "country"
    if a.por_dia:
        params["time_increment"] = 1
    _comprueba_moneda(meta, ctx, estricto=False)
    problemas = anuncios_con_problemas(meta, ctx, a) if a.estado else None
    sin_retencion = False
    try:
        filas_api = list(meta.lista(f"{ctx.cuenta}/insights", **params))
    except ErrorMeta as e:
        if e.codigo != 100:  # 100 = parámetro no válido: puede ser un campo de retención que esta cuenta no admite
            raise
        print(f"Aviso: Meta rechaza la petición con los campos de retención de vídeo ({str(e).splitlines()[0]}). "
              "Repito sin ellos: las columnas de retención saldrán vacías.", file=sys.stderr)
        params["fields"] = ",".join(CAMPOS_BASE)
        filas_api = list(meta.lista(f"{ctx.cuenta}/insights", **params))
        sin_retencion = True
    extra = {} if problemas is None else {"con_problemas": problemas}
    if not filas_api:
        if a.json:
            return _json({"cuenta": ctx.cuenta, "desde": desde, "hasta": hasta, "filas": 0, "por_campana": [],
                          **extra})
        print("Meta no devuelve ningún anuncio con entrega para ese filtro y periodo.")
        _imprime_problemas(problemas)
        return
    # El evento del resultado y el de la cita se eligen por campaña, no por anuncio, para no mezclar.
    por_campana: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for r in filas_api:
        for t, v in _acciones(r).items():
            por_campana[r["campaign_id"]][t] += v
    optimizado = _optimizados(meta, ctx.cuenta, list(por_campana))
    evento = {c: a.evento if a.evento != "auto" else _evento(acc, optimizado.get(c)) for c, acc in por_campana.items()}
    cita = {c: _cita(acc) for c, acc in por_campana.items()}
    filas = [fila_anuncio(r, evento.get(r["campaign_id"]), cita.get(r["campaign_id"]), sin_retencion) for r in filas_api]
    filas.sort(key=lambda f: (f["campana"], f["anuncio"], f["pais"], f["desde"]))

    ruta = None
    if a.salida == "-":
        w = csv.DictWriter(sys.stdout, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
        return
    if not a.sin_archivos:
        nombre = "meta-anuncios" + (f"_{re.sub(r'[^a-z0-9]+', '-', a.campana.lower()).strip('-')}" if a.campana else "")
        nombre += f"_{desde}_{hasta}" if desde else "_historico"
        nombre += "_por-pais" if a.por_pais else ""
        nombre += "_por-dia" if a.por_dia else ""
        ruta = pathlib.Path(a.salida).expanduser() if a.salida else comun.ruta_cliente(ctx.slug) / "datos" / f"{nombre}.csv"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNAS)
            w.writeheader()
            w.writerows(filas)
    resumen = resumen_por_campana(filas)
    if a.json:
        return _json({"cuenta": ctx.cuenta, "moneda": ctx.moneda, "desde": desde, "hasta": hasta,
                      "atribucion": "la de cada conjunto (use_unified_attribution_setting)", "filas": len(filas),
                      "eventos_resultado": sorted({e for e in evento.values() if e}), "por_campana": resumen,
                      "csv": _rel(ruta) if ruta else None, **extra})
    print(f"{ctx.cuenta} · {f'{desde} → {hasta}' if desde else 'desde el principio'} · {len(filas)} filas · "
          f"resultado = {', '.join(sorted({e for e in evento.values() if e})) or 'ninguno'} · "
          f"atribución de cada conjunto\n")
    _imprime_resumen(resumen, ctx.moneda)
    if a.acciones:
        nombres = {r["campaign_id"]: r.get("campaign_name", "") for r in filas_api}
        for c, acc in por_campana.items():
            print(f"\nAcciones que cuenta Meta en «{nombres[c]}»:")
            for t, v in sorted(acc.items(), key=lambda x: -x[1]):
                print(f"  {_n(v):>9}  {t}")
    _imprime_problemas(problemas)
    if ruta:
        print(f"\nCSV: {_rel(ruta)}")


def _imprime_problemas(problemas: list[dict] | None) -> None:
    if problemas is None:
        return
    if not problemas:
        print("\nNingún anuncio rechazado, con problemas ni en revisión.")
        return
    print(f"\n{len(problemas)} anuncios que mirar (estado de entrega de hoy, no del periodo):")
    for f in problemas:
        print(f"  {f['estado']:<15} {f['anuncio']} ({f['ad_id']}) · {f['campana']}"
              + (f"\n                  {f['motivo']}" if f["motivo"] else ""))


def cmd_eventos(a: argparse.Namespace) -> None:
    """Lo que recibió el dataset por día (zona de la ficha), venga o no de un anuncio."""
    ctx = contexto(a.cliente)
    meta = conectar(ctx)
    pixel = a.dataset or str((ctx.ficha.get("meta") or {}).get("dataset") or "")
    if not re.fullmatch(r"\d{6,20}", pixel) or re.fullmatch(r"0+", pixel):
        _salir("Pon el dataset en la ficha (meta.dataset) o pásalo con --dataset (`activos` lo lista).", 2)
    try:
        hasta = date.fromisoformat(a.hasta) if a.hasta else date.today()
        desde = date.fromisoformat(a.desde) if a.desde else hasta - timedelta(days=6)
    except ValueError:
        _salir("Fechas como AAAA-MM-DD.", 1)
    t0 = int(datetime.combine(desde, datetime.min.time(), ctx.zona).timestamp())
    t1 = int(datetime.combine(hasta + timedelta(days=1), datetime.min.time(), ctx.zona).timestamp())
    por_dia: dict[str, dict[str, Counter]] = {"event": defaultdict(Counter), "event_source": defaultdict(Counter)}
    for agregado, tabla in por_dia.items():
        for b in meta.lista(f"{pixel}/stats", aggregation=agregado, start_time=t0, end_time=t1):
            dia = datetime.strptime(b["start_time"], "%Y-%m-%dT%H:%M:%S%z").astimezone(ctx.zona).date().isoformat()
            for d in b.get("data", []):
                tabla[dia][d["value"]] += int(d["count"])
    dias = sorted(set(por_dia["event"]) | set(por_dia["event_source"]))
    if a.json:
        return _json({"dataset": pixel, "desde": desde.isoformat(), "hasta": hasta.isoformat(),
                      "dias": {d: {"eventos": dict(por_dia["event"][d]), "fuente": dict(por_dia["event_source"][d])}
                               for d in dias}})
    nombres = {"PageView": "Visita", "Lead": "Lead", "CompleteRegistration": "Registro", "Schedule": "Cita",
               "StartTrial": "Prueba", "Subscribe": "Suscrip.", "Purchase": "Compra"}
    vistos = {e for c in por_dia["event"].values() for e in c}
    cols = [c for c in nombres if c in vistos] + sorted(vistos - set(nombres))
    print(f"Dataset {pixel} · {desde} → {hasta} (zona de la ficha) · todos los eventos, sin atribución\n")
    print(f"{'Día':<12}" + "".join(f"{nombres.get(c, c)[:12]:>13}" for c in cols) + f"{'navegador':>11}{'servidor':>10}")
    for dia in dias:
        fila, fuente = por_dia["event"][dia], por_dia["event_source"][dia]
        print(f"{dia:<12}" + "".join(f"{fila.get(c, 0):>13}" for c in cols)
              + f"{fuente.get('BROWSER', 0):>11}{fuente.get('SERVER', 0):>10}")
    print("\nSi la web y el CRM mandan el mismo evento (navegador + servidor) sin un event_id común, cuenta doble.")


def _mejoras_activas(creative: dict) -> list[str]:
    spec = (creative.get("degrees_of_freedom_spec") or {}).get("creative_features_spec") or {}
    return sorted(f for f, v in spec.items() if isinstance(v, dict) and v.get("enroll_status") == "OPT_IN")


def cmd_creatividades(a: argparse.Namespace) -> None:
    """Qué textos lleva cada anuncio y qué mejoras automáticas de Meta tiene activadas."""
    ctx = contexto(a.cliente)
    meta = conectar(ctx)
    if a.plan:
        _, ruta_estado = lee_plan(a.plan, ctx.slug)
        if not ruta_estado.exists():
            _salir(f"No hay {_rel(ruta_estado)}: ese plan no se ha creado todavía.", 1)
        campanas_ = [json.loads(ruta_estado.read_text(encoding="utf-8"))["campana"]]
    elif a.campana_id:
        campanas_ = a.campana_id
    else:
        _salir("Di qué: --campana-id <id> o --plan <plan.json>.", 1)
    filas = []
    for cid in campanas_:
        for ad in meta.lista(f"{cid}/ads", limit=200, fields="id,name,effective_status,creative{id,asset_feed_spec"
                             "{bodies,titles},degrees_of_freedom_spec}"):
            cr = ad.get("creative", {})
            afs = cr.get("asset_feed_spec") or {}
            textos, titulos = len(afs.get("bodies") or []), len(afs.get("titles") or [])
            activas = _mejoras_activas(cr)
            filas.append({"id": ad["id"], "nombre": ad["name"], "estado": ad.get("effective_status", ""),
                          "textos": max(textos, 1), "titulos": max(titulos, 1), "mejoras_activas": activas,
                          "problema": bool(activas or textos > 1 or titulos > 1)})
    if a.json:
        return _json(filas)
    for f in filas:
        print(f"{'⚠' if f['problema'] else '✓'} {f['nombre'][:44]:<46}{f['estado']:<12}"
              f"textos {f['textos']} · títulos {f['titulos']}"
              + (f" · activas: {', '.join(f['mejoras_activas'])}" if f["mejoras_activas"] else ""))
    avisos = sum(f["problema"] for f in filas)
    if avisos:
        print(f"\n{avisos} anuncios con varias versiones de texto o mejoras activas. Quítalas en el Administrador "
              "(Creatividad de Advantage+ y opciones de texto) antes de activar.")
    else:
        print("\nTodos con un solo texto y sin mejoras automáticas.")


# ---------------------------------------------------------------- plan de campaña

def lee_plan(ruta_plan: str, slug: str) -> tuple[dict, pathlib.Path]:
    ruta = pathlib.Path(ruta_plan).expanduser()
    try:
        plan = json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _salir(f"No existe {ruta_plan}.", 1)
    except json.JSONDecodeError as e:
        _salir(f"{ruta_plan} no es JSON válido: {e}", 1)
    if not isinstance(plan, dict):
        _salir(f"{ruta_plan} tiene que ser un objeto JSON (formato en plantillas/plan-campana.json).", 1)
    return plan, comun.ruta_cliente(slug) / "planes" / f"{ruta.stem}.estado.json"


def _presupuesto(x: dict) -> float | None:
    v = x.get("presupuesto_diario", x.get("presupuesto_diario_eur"))
    return float(v) if v not in (None, "") else None


CLAVES_ESTADO = ("status", "configured_status")
VENTANA_META = "7d_click_1d_view"  # la que pone Meta a un conjunto nuevo si no se envía attribution_spec
CLAVES_PRESUPUESTO_API = ("daily_budget", "lifetime_budget")


def api_de(x: dict) -> dict:
    """El bloque `api` que se envía: sin las claves de estado (todo se crea en pausa)."""
    api = x.get("api")
    return {k: v for k, v in api.items() if k not in CLAVES_ESTADO} if isinstance(api, dict) else {}


def dias_de(c: dict) -> int | None:
    """Días entre inicio y fin del conjunto (los de `api` mandan, porque se envían después). None si falta alguno."""
    api = c.get("api") if isinstance(c.get("api"), dict) else {}
    ini, fin = api.get("start_time") or c.get("inicio"), api.get("end_time") or c.get("fin")
    if not (ini and fin):
        return None
    a, b = comun.fecha_iso(ini), comun.fecha_iso(fin)
    if a is None or b is None:
        return None
    if (a.tzinfo is None) != (b.tzinfo is None):
        a, b = a.replace(tzinfo=None), b.replace(tzinfo=None)
    segundos = (b - a).total_seconds()
    return max(1, -(-int(segundos) // 86400)) if segundos > 0 else None


def presupuesto_api(x: dict, moneda: str) -> float:
    """Presupuesto diario que mete el bloque `api`: `daily_budget`, y `lifetime_budget` repartido entre los días
    (sin fechas, entero en un día: nunca se subestima). Van en la unidad mínima, como los manda Meta."""
    api = x.get("api") if isinstance(x.get("api"), dict) else {}
    total = de_minimo(api.get("daily_budget"), moneda) or 0.0
    if api.get("lifetime_budget") not in (None, "", 0, "0"):
        total += (de_minimo(api["lifetime_budget"], moneda) or 0.0) / (dias_de(x) or 1)
    return total


def _revisa_api(x: dict, nivel: str, donde: str, cbo: float | None, ctx: "Contexto", errores: list,
                avisos: list) -> None:
    """`api` se envía tal cual: aquí se frena lo que no puede ir (estado activo, presupuestos fuera del tope)."""
    if "api" not in x:
        return
    api = x["api"]
    if not isinstance(api, dict):
        errores.append(f"{donde}: «api» tiene que ser un objeto JSON")
        return
    for k in CLAVES_ESTADO:
        if k in api and str(api[k]).upper() != "PAUSED":
            errores.append(f"{donde}: api.{k} = {api[k]} — todo se crea en pausa (PAUSED); se activa después con "
                           "`activar … --confirmo`, con un sí en ese momento")
    presupuestos = [k for k in CLAVES_PRESUPUESTO_API if api.get(k) not in (None, "", 0, "0")]
    if not presupuestos:
        return
    for k in presupuestos:
        if not re.fullmatch(r"\d+", str(api[k])):
            errores.append(f"{donde}: api.{k} va en la unidad mínima de la moneda (un entero: céntimos)")
            return
    if nivel != "conjunto":
        errores.append(f"{donde}: api.{' y api.'.join(presupuestos)} no — "
                       + ("el presupuesto de la campaña va en campana.presupuesto_diario (CBO)" if nivel == "campana"
                          else "un anuncio no lleva presupuesto"))
    elif "daily_budget" in presupuestos:
        errores.append(f"{donde}: api.daily_budget no — el presupuesto diario va en presupuesto_diario, en la moneda "
                       "de la ficha, para que cuente para el tope")
    elif cbo:
        errores.append(f"{donde}: api.lifetime_budget con presupuesto de campaña (CBO): el conjunto no lleva "
                       "presupuesto propio")
    elif _presupuesto(x) is not None:
        errores.append(f"{donde}: lleva presupuesto_diario y api.lifetime_budget; deja solo uno")
    elif not dias_de(x):
        errores.append(f"{donde}: api.lifetime_budget necesita inicio y fin (para repartirlo por día y compararlo con "
                       "el tope)")
    else:
        avisos.append(f"{donde}: api.lifetime_budget = {_n(de_minimo(api['lifetime_budget'], ctx.moneda), 2)} "
                      f"{ctx.moneda} en {dias_de(x)} días; para el tope cuenta como "
                      f"{_n(presupuesto_api(x, ctx.moneda), 2)} {ctx.moneda}/día")


def _es_ejemplo(valor) -> bool:
    return bool(re.fullmatch(r"0+", str(valor or "")))


def _momento(texto: str, zona: tzinfo) -> datetime:
    """«2026-11-16» o «2026-11-16 08:00», en la zona de la ficha si no lleva zona; también «…T08:00:00+0100»."""
    dt = comun.fecha_iso(texto)
    if dt is None:
        raise ValueError(f"fecha no válida: {texto!r}")
    return dt if dt.tzinfo else dt.replace(tzinfo=zona)


def validar_nombre(nivel: str, nombre: str) -> tuple[bool | None, str]:
    """Usa herramientas/nomenclatura.py (contrato §7). None si la herramienta no está disponible."""
    try:
        import nomenclatura  # noqa: PLC0415 — import perezoso: es de otro bloque
    except ImportError:
        return None, "no se ha podido validar la nomenclatura (falta herramientas/nomenclatura.py)"
    return nomenclatura.validar(nivel, nombre)


def resuelve_medio(rel: str, bases: list[pathlib.Path]) -> pathlib.Path | None:
    p = pathlib.Path(rel).expanduser()
    if p.is_absolute():
        return p if p.exists() else None
    return next((b / p for b in bases if (b / p).exists()), None)


def revisa_plan(plan: dict, ctx: Contexto, bases: list[pathlib.Path]) -> tuple[list[str], list[str], list[str]]:
    """(errores, pendientes, avisos). Errores: el plan está mal. Pendientes: el plan está bien pero falta algo para
    crearlo de verdad (archivos, IDs de ejemplo, cuenta). Avisos: no bloquean."""
    errores: list[str] = []
    pendientes: list[str] = []
    avisos: list[str] = []

    def nombre_ok(nivel: str, nombre: str, donde: str) -> None:
        ok, msg = validar_nombre(nivel, nombre)
        if ok is None:
            if msg not in avisos:
                avisos.append(msg)
        elif not ok:
            errores.append(f"{donde}: nomenclatura — {msg}")

    def id_existente(valor, donde: str) -> None:
        if _es_ejemplo(valor):
            pendientes.append(f"{donde}: ID de ejemplo (ceros)")
        elif not re.fullmatch(r"\d{5,25}", str(valor)):
            errores.append(f"{donde}: el id tiene que ser el ID numérico de Meta")

    camp = plan.get("campana") or {}
    conjuntos = plan.get("conjuntos") or []
    nuevos = [c for c in conjuntos if not c.get("id")]
    camp_existente = bool(camp.get("id"))
    objetivo = camp.get("objetivo", "OUTCOME_LEADS")
    cbo = _presupuesto(camp)
    if camp_existente:
        id_existente(camp["id"], "campaña existente")
        if cbo is not None:
            errores.append("campaña existente (campana.id): su presupuesto no se cambia desde un plan; usa `presupuesto`")
        cbo = None
    elif nuevos:
        if not camp.get("nombre"):
            errores.append("campana.nombre vacío (o campana.id para usar una campaña que ya existe)")
        else:
            nombre_ok("campana", camp["nombre"], "campaña")
    if not camp_existente:
        _revisa_api(camp, "campana", "campaña", cbo, ctx, errores, avisos)
    elif camp.get("api"):
        avisos.append("campaña existente: «api» se ignora (la campaña ya existe y no se cambia)")
    if objetivo not in OPTIMIZA:
        errores.append(f"campana.objetivo «{objetivo}» no es uno de {', '.join(OPTIMIZA)}")
    if cbo is not None and cbo <= 0:
        errores.append("campana.presupuesto_diario tiene que ser mayor que 0")
    if not conjuntos:
        errores.append("el plan no tiene conjuntos")
    vistos: set[str] = set()
    for i, c in enumerate(conjuntos, 1):
        formulario = c.get("destino") == "formulario"
        if c.get("id"):
            donde = f"conjunto existente {c.get('nombre') or c['id']}"
            id_existente(c["id"], donde)
            if _presupuesto(c) is not None:
                errores.append(f"{donde}: un conjunto existente no lleva presupuesto_diario (cámbialo con `presupuesto`)")
            for k in ("segmentacion", "inicio", "fin", "evento", "optimizar", "api"):
                if c.get(k):
                    avisos.append(f"{donde}: «{k}» se ignora (el conjunto ya existe y no se cambia)")
            clave = str(c.get("nombre") or c["id"])
            if clave in vistos:
                errores.append(f"{donde}: repetido")
            vistos.add(clave)
        else:
            donde = f"conjunto {i} «{c.get('nombre', '?')}»"
            if not c.get("nombre"):
                errores.append(f"conjunto {i} sin nombre (o id para usar uno que ya existe)")
            elif c["nombre"] in vistos:
                errores.append(f"{donde}: nombre repetido")
            else:
                nombre_ok("conjunto", c["nombre"], donde)
            vistos.add(c.get("nombre", ""))
            _revisa_conjunto_nuevo(c, plan, objetivo, cbo, camp_existente, ctx, donde, errores, pendientes, avisos)
            _revisa_api(c, "conjunto", donde, cbo, ctx, errores, avisos)
        if c.get("destino") not in (None, "web", "formulario"):
            errores.append(f"{donde}: destino «{c['destino']}» no válido (web o formulario)")
        anuncios_ = c.get("anuncios") or []
        if not anuncios_:
            errores.append(f"{donde}: sin anuncios")
        nombres: set[str] = set()
        for j, an in enumerate(anuncios_, 1):
            d = f"{donde}, anuncio {j} «{an.get('nombre', '?')}»"
            if not an.get("nombre") or an["nombre"] in nombres:
                errores.append(f"{d}: sin nombre o repetido")
            else:
                nombre_ok("anuncio", an["nombre"], d)
            nombres.add(an.get("nombre", ""))
            _revisa_api(an, "anuncio", d, cbo, ctx, errores, avisos)
            medios = [k for k in MEDIOS if an.get(k)]
            if len(medios) != 1:
                errores.append(f"{d}: lleva uno y solo uno de {', '.join(f'«{k}»' for k in MEDIOS)}")
            publicacion = next((k for k in PUBLICACION if an.get(k)), None)
            for campo in ("video", "imagen", "miniatura"):
                if an.get(campo) and not publicacion and not resuelve_medio(an[campo], bases):
                    pendientes.append(f"{d}: no encuentro {an[campo]} (junto al plan, en la carpeta del cliente o "
                                      "desde la raíz)")
            for campo in ("video_id", "imagen_hash"):
                if an.get(campo) and _es_ejemplo(an[campo]):
                    pendientes.append(f"{d}: {campo} de ejemplo")
            if publicacion:
                _revisa_publicacion(an, publicacion, plan, ctx, formulario, d, errores, pendientes, avisos)
            elif not an.get("texto"):
                errores.append(f"{d}: falta texto")
            if formulario:
                form = an.get("formulario_id") or c.get("formulario_id")
                if not form:
                    errores.append(f"{d}: falta formulario_id (en el anuncio o en el conjunto)")
                elif _es_ejemplo(form):
                    pendientes.append(f"{d}: formulario_id de ejemplo")
                if an.get("cta", "SIGN_UP") not in CTA_FORMULARIO:
                    errores.append(f"{d}: con formulario, cta es uno de {', '.join(CTA_FORMULARIO)}")
            else:
                url = str(an.get("url", ""))
                if not url.startswith("https://"):
                    errores.append(f"{d}: url tiene que empezar por https://")
                elif re.search(r"\.example(/|$)", urllib.parse.urlsplit(url).netloc + "/"):
                    pendientes.append(f"{d}: url de ejemplo ({urllib.parse.urlsplit(url).netloc})")
    try:
        total = total_plan(plan, ctx.moneda)
    except (TypeError, ValueError):
        errores.append("algún presupuesto (presupuesto_diario o el de «api») no es un número")
        total = 0.0
    if ctx.tope_cambio <= 0:
        errores.append(f"la ficha de {ctx.slug} no tiene topes (topes.cambio_dia = 0): fíjalos antes de crear nada")
    elif total > ctx.tope_cambio:
        errores.append(f"el plan suma {_n(total, 2)} {ctx.moneda}/día y el tope por cambio de la ficha es "
                       f"{_n(ctx.tope_cambio, 2)} {ctx.moneda}/día")
    for clave, campo in (("pagina_id", "pagina"), ("instagram_id", "instagram"), ("pixel_id", "dataset")):
        valor = plan.get(clave) or (ctx.ficha.get("meta") or {}).get(campo)
        if valor and _es_ejemplo(valor):
            pendientes.append(f"{clave}: el del plan o la ficha es de ejemplo (ceros)")
    if not ctx.cuenta_valida:
        pendientes.append(f"la ficha de {ctx.slug} no tiene una cuenta real en meta.cuenta")
    _, aviso_mejoras = mejoras_de(ctx.ficha)
    if aviso_mejoras:
        avisos.append(aviso_mejoras)
    ventana = str((ctx.ficha.get("meta") or {}).get("ventana_atribucion") or "").strip()
    sin_spec = [c for c in nuevos if "attribution_spec" not in api_de(c)]
    if ventana and ventana.lower() != VENTANA_META and sin_spec:
        avisos.append(f"la ficha pide la ventana de atribución {ventana} y `crear` no la envía: los conjuntos nuevos "
                      f"salen con la de Meta ({VENTANA_META}). Cámbiala en Ads Manager (conjunto → Configuración de "
                      "atribución) o pon api.attribution_spec en el conjunto")
    return errores, pendientes, avisos


def _revisa_publicacion(an: dict, clave: str, plan: dict, ctx: Contexto, formulario: bool, d: str,
                        errores: list, pendientes: list, avisos: list) -> None:
    """Anuncio desde una publicación existente: el ID con el formato de Meta, de la Página del plan, y sin textos
    propios (manda lo publicado)."""
    valor = str(an[clave])
    if clave == "publicacion_ig":
        if _es_ejemplo(valor):
            pendientes.append(f"{d}: publicacion_ig de ejemplo (ceros)")
        elif not re.fullmatch(r"\d{5,25}", valor):
            errores.append(f"{d}: publicacion_ig es el ID numérico del medio de Instagram (no el enlace ni el código "
                           "del permalink): sácalo con ads_get_ig_media")
    else:
        m = re.fullmatch(r"(\d{5,25})_(\d{5,25})", valor)
        if not m:
            errores.append(f"{d}: publicacion_fb va como «<id de la Página>_<id de la publicación>»")
        elif _es_ejemplo(m.group(1)) or _es_ejemplo(m.group(2)):
            pendientes.append(f"{d}: publicacion_fb de ejemplo (ceros)")
        else:
            pagina = str(plan.get("pagina_id") or (ctx.ficha.get("meta") or {}).get("pagina") or "")
            if pagina and not _es_ejemplo(pagina) and pagina != m.group(1):
                errores.append(f"{d}: publicacion_fb es de la Página {m.group(1)}, no de la del plan o la ficha "
                               f"({pagina})")
    if formulario:
        errores.append(f"{d}: publicación existente con formulario instantáneo: la vía por API no está verificada; "
                       "móntalo en Ads Manager o usa el vídeo o la imagen")
    ignorados = [k for k in ("texto", "titulo", "descripcion", "miniatura") if an.get(k)]
    if ignorados:
        avisos.append(f"{d}: {', '.join(ignorados)} se ignora{'n' if len(ignorados) > 1 else ''}: el anuncio "
                      "enseña el texto y el medio de la publicación")


def _revisa_conjunto_nuevo(c: dict, plan: dict, objetivo: str, cbo: float | None, camp_existente: bool,
                           ctx: Contexto, donde: str, errores: list, pendientes: list, avisos: list) -> None:
    formulario = c.get("destino") == "formulario"
    propio = _presupuesto(c)
    if cbo and propio:
        errores.append(f"{donde}: con presupuesto de campaña (CBO) el conjunto no lleva presupuesto propio")
    total_api = isinstance(c.get("api"), dict) and c["api"].get("lifetime_budget") not in (None, "", 0, "0")
    if not cbo and not camp_existente and propio is None and not total_api:
        errores.append(f"{donde}: falta presupuesto_diario (o ponlo en la campaña)")
    if propio is not None and propio <= 0:
        errores.append(f"{donde}: presupuesto_diario tiene que ser mayor que 0")
    if formulario and objetivo != "OUTCOME_LEADS":
        errores.append(f"{donde}: el formulario instantáneo va con campana.objetivo OUTCOME_LEADS")
    seg = c.get("segmentacion") or {}
    if not seg.get("geo_locations"):
        errores.append(f"{donde}: segmentacion.geo_locations es obligatorio")
    for aud in (seg.get("excluded_custom_audiences") or []) + (seg.get("custom_audiences") or []):
        if _es_ejemplo(aud.get("id") if isinstance(aud, dict) else aud):
            pendientes.append(f"{donde}: sustituye el público de ejemplo (ID con ceros) o quítalo")
    if not formulario and c.get("optimizar", OPTIMIZA.get(objetivo)) == "OFFSITE_CONVERSIONS" \
            and not c.get("evento", plan.get("evento")):
        errores.append(f"{donde}: falta evento (LEAD, COMPLETE_REGISTRATION, SCHEDULE, START_TRIAL...)")
    optimizar = c.get("optimizar")
    if formulario and optimizar and optimizar not in OPTIMIZA_FORMULARIO:
        errores.append(f"{donde}: con formulario, optimizar es {' o '.join(OPTIMIZA_FORMULARIO)}")
    if optimizar == "QUALITY_LEAD":
        if not formulario:
            errores.append(f"{donde}: QUALITY_LEAD (Conversion Leads) va con destino formulario; en la web, optimiza "
                           "al evento del CRM con «evento»")
        else:
            dataset = c.get("dataset_crm") or plan.get("dataset_crm") or plan.get("pixel_id") \
                or (ctx.ficha.get("meta") or {}).get("dataset")
            if dataset and _es_ejemplo(dataset):
                pendientes.append(f"{donde}: dataset_crm de ejemplo (ceros)")
            avisos.append(f"{donde}: QUALITY_LEAD necesita que el dataset {dataset or '(el de la ficha)'} reciba ya "
                          "las etapas del CRM por CAPI (docs/guias/capi.md) y volumen suficiente: el mínimo está en "
                          "disputa [CONTESTED], ≥200 leads/mes por prudencia (playbook de consultoras §6)")
    seg_dispositivo = [k for k in DISPOSITIVO if seg.get(k)]
    expansion = c.get("expansion_dispositivos", plan.get("expansion_dispositivos"))
    if expansion is not None and not isinstance(expansion, bool):
        errores.append(f"{donde}: expansion_dispositivos es true o false")
    elif seg_dispositivo and objetivo == "OUTCOME_SALES" and not _categorias(plan):
        if expansion is True:
            avisos.append(f"{donde}: expansion_dispositivos: true — Meta puede entregar fuera de "
                          f"{' y '.join(seg_dispositivo)}")
        elif "device" not in ((seg.get("targeting_automation") or {}).get("individual_setting") or {}):
            avisos.append(f"{donde}: segmenta por {' y '.join(seg_dispositivo)}: se manda "
                          "targeting_automation.individual_setting.device = 0 para que Meta no lo amplíe (expansión "
                          "de dispositivos de la v27); \"expansion_dispositivos\": true para dejársela")
    try:
        ini = _momento(c["inicio"], ctx.zona) if c.get("inicio") else None
        fin = _momento(c["fin"], ctx.zona) if c.get("fin") else None
        if ini and fin and fin <= ini:
            errores.append(f"{donde}: fin antes que inicio")
        if ini and ini < datetime.now(timezone.utc):
            avisos.append(f"{donde}: el inicio ya ha pasado; empezará a entregar al activarlo")
    except (ValueError, TypeError):
        errores.append(f"{donde}: fechas como «AAAA-MM-DD» o «AAAA-MM-DD HH:MM» (zona de la ficha)")


def _categorias(plan: dict) -> list:
    return list((plan.get("campana") or {}).get("categorias_especiales") or [])


def segmentacion_api(c: dict, plan: dict, objetivo: str) -> dict:
    """La segmentación del conjunto tal como va a Meta. Es la del plan, salvo en Ventas con dispositivo o sistema
    operativo (y sin categoría especial, a la que no aplica): ahí se añade `device = 0` para que Meta respete lo
    segmentado, salvo `"expansion_dispositivos": true` o un valor puesto a mano en `targeting_automation`."""
    seg = dict(c.get("segmentacion") or {})
    if objetivo != "OUTCOME_SALES" or _categorias(plan) or not any(seg.get(k) for k in DISPOSITIVO):
        return seg
    if c.get("expansion_dispositivos", plan.get("expansion_dispositivos")) is True:
        return seg
    auto = dict(seg.get("targeting_automation") or {})
    individual = dict(auto.get("individual_setting") or {})
    if "device" in individual:
        return seg
    individual["device"] = 0
    auto["individual_setting"] = individual
    seg["targeting_automation"] = auto
    return seg


MODOS_MEJORAS = ("off", "revisar", "on")


def mejoras_de(ficha: dict) -> tuple[str, str]:
    """(modo, aviso) de `mejoras_automaticas`. Lo que no sea off, revisar u on (false, no, {}, true, vacío…) se
    trata como off, que es lo seguro, y se avisa: antes dejaba todas las mejoras de IA a Meta (hallazgo 10, I6)."""
    if "mejoras_automaticas" not in ficha:
        return "off", ""
    bruto = ficha.get("mejoras_automaticas")
    modo = str(bruto).strip().lower() if isinstance(bruto, str) else None
    if modo in MODOS_MEJORAS:
        return modo, ""
    return "off", (f"mejoras_automaticas: {bruto!r} no es off, revisar ni on: se crea con todas las mejoras "
                   "automáticas apagadas (off). Escribe on si quieres dejárselas a Meta.")


def spec_mejoras(mejoras: str) -> dict | None:
    """`degrees_of_freedom_spec` según `mejoras_automaticas` de la ficha. off: todas en OPT_OUT. revisar: solo
    product showcase (`product_extensions`, por defecto desde la v27: añade productos del catálogo al anuncio) en
    OPT_OUT y el resto lo que decida Meta, que `crear` lista después. on: lo que decida Meta."""
    if mejoras == "off":
        apagadas = MEJORAS
    elif mejoras == "revisar":
        apagadas = ("product_extensions",)
    else:
        return None
    return {"creative_features_spec": {f: {"enroll_status": "OPT_OUT"} for f in apagadas}}


def total_plan(plan: dict, moneda: str = "EUR") -> float:
    """Presupuesto diario NUEVO que mete el plan: el de una campaña CBO nueva o el de los conjuntos nuevos, más lo que
    lleve el bloque `api` de la campaña nueva y de los conjuntos nuevos (se envía tal cual a Meta)."""
    camp = plan.get("campana") or {}
    nuevos = [c for c in plan.get("conjuntos") or [] if not c.get("id")]
    extra = sum(presupuesto_api(c, moneda) for c in nuevos)
    if not camp.get("id"):
        extra += presupuesto_api(camp, moneda)
        if _presupuesto(camp):
            return _presupuesto(camp) + extra
    return sum(_presupuesto(c) or 0 for c in nuevos) + extra


def dibuja_plan(plan: dict, ctx: Contexto) -> None:
    camp = plan.get("campana") or {}
    cbo = _presupuesto(camp)
    print(f"Cliente  {ctx.slug} · cuenta {ctx.cuenta or '—'} · {ctx.moneda} · topes {_n(ctx.tope_cambio)} por "
          f"cambio / {_n(ctx.tope_total)} al día · mejoras automáticas: {mejoras_de(ctx.ficha)[0]}")
    if camp.get("id"):
        print(f"Campaña  existente {camp.get('nombre') or ''} ({camp['id']}): no se cambia · presupuesto nuevo "
              f"{_n(total_plan(plan, ctx.moneda), 2)} {ctx.moneda}/día")
    elif any(not c.get("id") for c in plan["conjuntos"]):
        print(f"Campaña  {camp.get('nombre')} · {camp.get('objetivo', 'OUTCOME_LEADS')}"
              + (f" · {_n(cbo, 2)}/día de campaña (CBO)" if cbo else " · presupuesto por conjunto (ABO)")
              + f" · total {_n(total_plan(plan, ctx.moneda), 2)} {ctx.moneda}/día")
    else:
        print("Campaña  la de cada conjunto existente: solo se añaden anuncios (sin presupuesto nuevo)")
    for c in plan["conjuntos"]:
        if c.get("id"):
            print(f"  Conjunto  existente {c.get('nombre') or ''} ({c['id']}): no se cambia; se le añaden anuncios")
            for an in c["anuncios"]:
                medio = next((f"{k} {an[k]}" for k in MEDIOS if an.get(k)), "—")
                destino_an = f"formulario {an.get('formulario_id') or c.get('formulario_id')}" \
                    if c.get("destino") == "formulario" else an.get("url", "—")
                print(f"    Anuncio  {an['nombre']} · {medio} · {an.get('cta', 'LEARN_MORE')} → {destino_an}")
            continue
        fechas = f"{c.get('inicio', 'al activar')} → {c.get('fin') or 'sin fin'}"
        dinero = f"{_n(_presupuesto(c), 2)}/día · " if _presupuesto(c) else ""
        destino = f"formulario instantáneo ({c.get('optimizar', 'LEAD_GENERATION')})" \
            if c.get("destino") == "formulario" else f"evento {c.get('evento', plan.get('evento', '—'))}"
        print(f"  Conjunto  {c['nombre']} · {dinero}{fechas} · {destino}")
        for an in c["anuncios"]:
            medio = next((f"{k} {an[k]}" for k in MEDIOS if an.get(k)), "—")
            destino_an = f"formulario {an.get('formulario_id') or c.get('formulario_id')}" \
                if c.get("destino") == "formulario" else an.get("url", "—")
            print(f"    Anuncio  {an['nombre']} · {medio} · {an.get('cta', 'LEARN_MORE')} → {destino_an}")


def _identidad(meta: Meta, plan: dict, ctx: Contexto) -> dict[str, str | None]:
    """Página, Instagram y dataset: los del plan, los de la ficha o, si la cuenta solo tiene uno, ese."""
    ficha = ctx.ficha.get("meta") or {}
    salida: dict[str, str | None] = {}
    for clave, campo, ruta, opcional in [("pagina_id", "pagina", "promote_pages", False),
                                         ("instagram_id", "instagram", "instagram_accounts", True),
                                         ("pixel_id", "dataset", "adspixels", False)]:
        valor = plan.get(clave) or ficha.get(campo)
        if valor:
            salida[clave] = str(valor)
            continue
        opciones = list(meta.lista(f"{ctx.cuenta}/{ruta}", fields="id", limit=50))
        if len(opciones) == 1:
            salida[clave] = opciones[0]["id"]
        elif not opciones and opcional:
            print("Aviso: la cuenta no tiene Instagram vinculado; los anuncios saldrán solo con la Página.",
                  file=sys.stderr)
            salida[clave] = None
        else:
            raise ErrorMeta(f"Di cuál ({clave} en el plan o meta.{campo} en la ficha): la cuenta tiene "
                            f"{len(opciones)} (ver `activos`).")
    return salida


def _de_la_cuenta(meta: Meta, ctx: Contexto, entidad_id: str, campos: str) -> dict:
    """Lee una campaña o un conjunto que ya existe y comprueba que es de la cuenta de la ficha."""
    info = meta.uno(entidad_id, fields=f"account_id,{campos}")
    if str(info.get("account_id", "")).removeprefix("act_") != ctx.cuenta.removeprefix("act_"):
        raise ErrorMeta(f"{entidad_id} no es de la cuenta de la ficha ({ctx.cuenta}).")
    return info


def creatividad_publicacion(an: dict, ids: dict, url_tags: str) -> dict:
    """Creatividad de un anuncio hecho con una publicación que ya existe (guía «Use posts as ads»). Instagram:
    `object_id` (la Página) + `instagram_user_id` + `source_instagram_media_id`. Facebook: `object_story_id` (+
    `instagram_user_id`, para que salga también en Instagram). Con `url`, botón a la web (`cta`, LEARN_MORE por
    defecto) y las UTMs."""
    params: dict = {"name": an["nombre"]}
    if an.get("publicacion_ig"):
        if not ids.get("instagram_id"):
            raise ErrorMeta(f"«{an['nombre']}»: publicacion_ig necesita la cuenta de Instagram (instagram_id en el plan "
                            "o meta.instagram en la ficha).")
        params |= {"object_id": ids["pagina_id"], "instagram_user_id": ids["instagram_id"],
                   "source_instagram_media_id": str(an["publicacion_ig"])}
    else:
        pagina = str(an["publicacion_fb"]).partition("_")[0]
        if pagina != str(ids["pagina_id"]):
            raise ErrorMeta(f"«{an['nombre']}»: la publicación {an['publicacion_fb']} es de otra Página "
                            f"(la del plan es {ids['pagina_id']}).")
        params["object_story_id"] = str(an["publicacion_fb"])
        if ids.get("instagram_id"):
            params["instagram_user_id"] = ids["instagram_id"]
    if an.get("url"):
        params["call_to_action"] = {"type": an.get("cta", "LEARN_MORE"), "value": {"link": an["url"]}}
        params["url_tags"] = url_tags
    return params


def _crea_creatividad(meta: Meta, ctx: Contexto, params: dict) -> tuple[str, list[str]]:
    """Crea la creatividad; si Meta rechaza alguna clave de mejoras, reintenta sin ella. Devuelve (id, rechazadas)."""
    rechazadas: list[str] = []
    for _ in range(4):
        try:
            return meta.escribe(f"{ctx.cuenta}/adcreatives", **params)["id"], rechazadas
        except ErrorMeta as e:
            spec = ((params.get("degrees_of_freedom_spec") or {}).get("creative_features_spec") or {})
            culpables = [k for k in spec if k in str(e)]
            if not culpables:
                raise
            for k in culpables:
                spec.pop(k)
            rechazadas += culpables
    raise ErrorMeta("Meta sigue rechazando las mejoras automáticas de la creatividad.")


def cmd_crear(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente)
    ruta = pathlib.Path(a.plan).expanduser().resolve()
    plan, ruta_estado = lee_plan(a.plan, ctx.slug)
    bases = [ruta.parent, comun.ruta_cliente(ctx.slug), comun.RAIZ]
    errores, pendientes, avisos = revisa_plan(plan, ctx, bases)
    if errores:
        if a.json:
            _json({"ok": False, "errores": errores, "pendientes": pendientes, "avisos": avisos})
            sys.exit(1)
        _salir("El plan no se puede crear:\n  - " + "\n  - ".join(errores)
               + ("\nAdemás falta:\n  - " + "\n  - ".join(pendientes) if pendientes else ""), 1)
    if a.simular:
        if a.json:
            return _json({"ok": True, "simulado": True, "total_dia": total_plan(plan, ctx.moneda),
                          "moneda": ctx.moneda,
                          "pendientes": pendientes, "avisos": avisos, "estado": _rel(ruta_estado)})
        dibuja_plan(plan, ctx)
        for x in avisos:
            print(f"Aviso: {x}")
        if pendientes:
            print("\nPlan correcto. Antes de crearlo de verdad falta:\n  - " + "\n  - ".join(pendientes))
        print("\nNo se ha tocado Meta (--simular).")
        return
    if pendientes:
        _salir("No se ha tocado Meta. Antes de crear falta:\n  - " + "\n  - ".join(pendientes), 1)

    meta = conectar(ctx)
    _comprueba_moneda(meta, ctx, estricto=True)
    estado = json.loads(ruta_estado.read_text(encoding="utf-8")) if ruta_estado.exists() else {}
    if estado.get("cuenta") not in (None, ctx.cuenta):
        _salir(f"{_rel(ruta_estado)} es de otra cuenta ({estado['cuenta']}).", 1)
    estado.setdefault("cuenta", ctx.cuenta)
    estado.setdefault("plan", _rel(ruta))
    for k in ("conjuntos", "anuncios", "medios"):
        estado.setdefault(k, {})

    def guarda() -> None:
        ruta_estado.parent.mkdir(parents=True, exist_ok=True)
        ruta_estado.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def anota(accion: str, entidad: str, detalle: str) -> None:
        comun.registrar_cambio("meta", "cli", accion, entidad, ctx.slug, detalle)

    di = (lambda *_x, **_k: None) if a.json else print
    if not a.json:
        dibuja_plan(plan, ctx)
        print()
    camp = plan.get("campana") or {}
    objetivo = camp.get("objetivo", "OUTCOME_LEADS")
    cbo = None if camp.get("id") else _presupuesto(camp)
    cbo_existente = False
    mejoras = mejoras_de(ctx.ficha)[0]
    utm_defecto = UTM_GHL if (ctx.ficha.get("crm") or {}).get("tipo") == "ghl" else UTM_GENERICA
    existentes = estado.setdefault("existentes", [])
    try:
        ids = _identidad(meta, plan, ctx)
        # Lo que ya existe se comprueba antes de crear nada: que es de la cuenta y que encaja con el plan.
        if camp.get("id"):
            info = _de_la_cuenta(meta, ctx, str(camp["id"]), "name,objective,daily_budget,lifetime_budget")
            objetivo = info.get("objective") or objetivo
            cbo_existente = bool(info.get("daily_budget") or info.get("lifetime_budget"))
            estado["campana"] = str(camp["id"])
            if estado["campana"] not in existentes:
                existentes.append(estado["campana"])
            for c in plan["conjuntos"]:
                if c.get("id"):
                    continue
                if cbo_existente and _presupuesto(c):
                    raise ErrorMeta(f"La campaña {camp['id']} reparte el presupuesto (CBO): quita presupuesto_diario "
                                    f"de «{c['nombre']}».")
                if not cbo_existente and not _presupuesto(c):
                    raise ErrorMeta(f"La campaña {camp['id']} no tiene presupuesto de campaña: pon presupuesto_diario "
                                    f"en «{c['nombre']}».")
        for c in plan["conjuntos"]:
            if c.get("id") and str(c.get("nombre") or c["id"]) not in estado["conjuntos"]:
                info = _de_la_cuenta(meta, ctx, str(c["id"]), "name,campaign_id")
                if camp.get("id") and str(info.get("campaign_id")) != str(camp["id"]):
                    raise ErrorMeta(f"El conjunto {c['id']} no es de la campaña {camp['id']}.")
                estado["conjuntos"][str(c.get("nombre") or c["id"])] = str(c["id"])
                existentes.append(str(c["id"]))
                if not estado.get("campana") and info.get("campaign_id"):
                    estado["campana"] = str(info["campaign_id"])  # la del conjunto: tampoco es del plan
                    existentes.append(estado["campana"])
                guarda()
        if not estado.get("campana") and any(not c.get("id") for c in plan["conjuntos"]):
            params = {"name": camp["nombre"], "objective": objetivo, "status": "PAUSED",
                      "special_ad_categories": camp.get("categorias_especiales", []), **api_de(camp)}
            if cbo:
                params |= {"daily_budget": a_minimo(cbo, ctx.moneda), "bid_strategy": "LOWEST_COST_WITHOUT_CAP"}
            else:
                params["is_adset_budget_sharing_enabled"] = False
            estado["campana"] = meta.escribe(f"{ctx.cuenta}/campaigns", **params)["id"]
            guarda()
            anota("crear_campana", estado["campana"], f"{camp['nombre']} en pausa"
                  + (f", {cbo} {ctx.moneda}/día (CBO)" if cbo else ""))
            di(f"✓ campaña {estado['campana']}")

        def medio(rel: str, tipo: str) -> str:
            clave = f"{tipo}:{rel}"
            if clave not in estado["medios"]:
                fichero = resuelve_medio(rel, bases)
                di(f"  subiendo {fichero.name}…", flush=True)
                if tipo == "video":
                    vid = meta.sube_video(fichero)
                    meta.espera_video(vid, fichero.name)
                    estado["medios"][clave] = vid
                else:
                    estado["medios"][clave] = meta.sube_imagen(fichero)
                guarda()
                anota(f"subir_{tipo}", estado["medios"][clave], fichero.name)
            return estado["medios"][clave]

        for c in plan["conjuntos"]:
            formulario = c.get("destino") == "formulario"
            nombre_c = str(c.get("nombre") or c.get("id"))
            if nombre_c not in estado["conjuntos"]:
                params = {"name": c["nombre"], "campaign_id": estado["campana"], "status": "PAUSED",
                          "billing_event": "IMPRESSIONS", "targeting": segmentacion_api(c, plan, objetivo),
                          "start_time": _momento(c["inicio"], ctx.zona).isoformat() if c.get("inicio") else None,
                          "end_time": _momento(c["fin"], ctx.zona).isoformat() if c.get("fin") else None}
                if formulario:
                    optimizar = c.get("optimizar", "LEAD_GENERATION")
                    params |= {"optimization_goal": optimizar, "destination_type": "ON_AD",
                               "promoted_object": {"page_id": ids["pagina_id"]}}
                    if optimizar == "QUALITY_LEAD":  # Conversion Leads: el dataset que recibe las etapas del CRM
                        params["promoted_object"]["pixel_id"] = str(
                            c.get("dataset_crm") or plan.get("dataset_crm") or ids["pixel_id"])
                else:
                    params["optimization_goal"] = c.get("optimizar", OPTIMIZA[objetivo])
                    if evento := c.get("evento", plan.get("evento")):
                        params["promoted_object"] = {"pixel_id": ids["pixel_id"], "custom_event_type": evento}
                if not (cbo or cbo_existente):
                    params["bid_strategy"] = "LOWEST_COST_WITHOUT_CAP"
                    if _presupuesto(c) is not None:
                        params["daily_budget"] = a_minimo(_presupuesto(c), ctx.moneda)
                params |= api_de(c)
                estado["conjuntos"][c["nombre"]] = meta.escribe(f"{ctx.cuenta}/adsets", **params)["id"]
                guarda()
                total_c = de_minimo(api_de(c).get("lifetime_budget"), ctx.moneda)
                anota("crear_conjunto", estado["conjuntos"][c["nombre"]], f"{c['nombre']} en pausa"
                      + ("" if cbo or cbo_existente else f", {total_c} {ctx.moneda} en total" if total_c
                         else f", {_presupuesto(c)} {ctx.moneda}/día"))
                di(f"✓ conjunto {c['nombre']}")
            for an in c["anuncios"]:
                clave = f"{nombre_c}/{an['nombre']}"
                hecho = estado["anuncios"].setdefault(clave, {})
                if not hecho.get("creatividad") and any(an.get(k) for k in PUBLICACION):
                    params = creatividad_publicacion(an, ids, an.get("utm", plan.get("utm", utm_defecto)))
                    if spec_dof := spec_mejoras(mejoras):
                        params["degrees_of_freedom_spec"] = spec_dof
                    hecho["creatividad"], rechazadas = _crea_creatividad(meta, ctx, params)
                    if rechazadas:
                        hecho["mejoras_no_aceptadas"] = rechazadas
                    hecho["mejoras_activas"] = _mejoras_activas(
                        meta.uno(hecho["creatividad"], fields="degrees_of_freedom_spec"))
                    hecho["publicacion"] = str(an.get("publicacion_ig") or an.get("publicacion_fb"))
                    guarda()
                    anota("crear_creatividad", hecho["creatividad"], f"{an['nombre']} desde una publicación de "
                          + ("Instagram" if an.get("publicacion_ig") else "Facebook"))
                if not hecho.get("creatividad"):
                    form = an.get("formulario_id") or c.get("formulario_id")
                    if formulario:
                        cta = {"type": an.get("cta", "SIGN_UP"), "value": {"lead_gen_form_id": str(form)}}
                    else:
                        cta = {"type": an.get("cta", "LEARN_MORE"), "value": {"link": an["url"]}}
                    if an.get("video") or an.get("video_id"):
                        if formulario:
                            cta["value"]["link"] = "https://fb.me/"
                        datos = {"video_id": an.get("video_id") or medio(an["video"], "video"),
                                 "message": an["texto"], "title": an.get("titulo"),
                                 "link_description": an.get("descripcion"), "call_to_action": cta}
                        if an.get("miniatura"):
                            datos["image_hash"] = medio(an["miniatura"], "imagen")
                        else:
                            datos["image_url"] = meta.miniatura(datos["video_id"])
                        historia = {"video_data": {k: v for k, v in datos.items() if v}}
                    else:
                        datos = {"image_hash": an.get("imagen_hash") or medio(an["imagen"], "imagen"),
                                 "link": "https://fb.me/" if formulario else an["url"], "message": an["texto"],
                                 "name": an.get("titulo"), "description": an.get("descripcion"),
                                 "call_to_action": cta}
                        historia = {"link_data": {k: v for k, v in datos.items() if v}}
                    spec = {"page_id": ids["pagina_id"], **historia}
                    if ids.get("instagram_id"):
                        spec["instagram_user_id"] = ids["instagram_id"]
                    params = {"name": an["nombre"], "object_story_spec": spec}
                    if not formulario:
                        params["url_tags"] = an.get("utm", plan.get("utm", utm_defecto))
                    if spec_dof := spec_mejoras(mejoras):
                        params["degrees_of_freedom_spec"] = spec_dof
                    hecho["creatividad"], rechazadas = _crea_creatividad(meta, ctx, params)
                    if rechazadas:
                        hecho["mejoras_no_aceptadas"] = rechazadas
                    hecho["mejoras_activas"] = _mejoras_activas(
                        meta.uno(hecho["creatividad"], fields="degrees_of_freedom_spec"))
                    guarda()
                    anota("crear_creatividad", hecho["creatividad"], an["nombre"])
                if not hecho.get("anuncio"):
                    hecho["anuncio"] = meta.escribe(f"{ctx.cuenta}/ads", **(
                        {"name": an["nombre"]} | api_de(an) | {"adset_id": estado["conjuntos"][nombre_c],
                                                               "status": "PAUSED",
                                                               "creative": {"creative_id": hecho["creatividad"]}}))["id"]
                    guarda()
                    anota("crear_anuncio", hecho["anuncio"], f"{an['nombre']} en pausa")
                    di(f"  ✓ anuncio {an['nombre']}")
    except ErrorMeta as e:
        _salir(f"{e}\nLo creado hasta aquí está en {_rel(ruta_estado)}: corrige y vuelve a lanzar `crear` "
               "(sigue donde se quedó, sin duplicar).", e.salida)

    con_mejoras = {k: v["mejoras_activas"] for k, v in estado["anuncios"].items() if v.get("mejoras_activas")}
    if a.json:
        return _json({"ok": True, "estado": _rel(ruta_estado), "campana": estado["campana"],
                      "conjuntos": estado["conjuntos"], "anuncios": estado["anuncios"],
                      "mejoras_activas": con_mejoras})
    numero = ctx.cuenta.removeprefix("act_")
    print(f"\nCreado TODO EN PAUSA: no gasta nada hasta que se active. IDs en {_rel(ruta_estado)}.")
    if existentes:
        print(f"Lo que ya existía ({', '.join(existentes)}) no se ha tocado, y `activar --plan` tampoco lo toca: "
              "si está en pausa, los anuncios nuevos no entregan hasta que lo actives tú.")
    if con_mejoras:
        print("⚠ Meta ha dejado mejoras automáticas activas en:" if mejoras == "off" else
              f"Mejoras automáticas activas (la ficha dice «{mejoras}»):")
        for k, v in con_mejoras.items():
            print(f"    {k}: {', '.join(v)}")
        if mejoras == "off":
            print("  Quítalas en el Administrador antes de activar y comprueba con `creatividades --plan`.")
    print(f"Revísalo en el Administrador: https://adsmanager.facebook.com/adsmanager/manage/campaigns"
          f"?act={numero}&selected_campaign_ids={estado['campana']}")
    nuevos_c = len(estado["conjuntos"]) - sum(1 for x in estado["conjuntos"].values() if x in existentes)
    if estado["campana"] in existentes:
        fila = fila_change_log("campaña", f"{camp.get('nombre') or ''} ({estado['campana']})".strip(),
                               f"— → {nuevos_c} conjuntos y {len(estado['anuncios'])} anuncios nuevos en pausa "
                               f"({_n(total_plan(plan, ctx.moneda), 2)} {ctx.moneda}/día nuevos al activar)")
    else:
        fila = fila_change_log("campaña", f"{camp.get('nombre') or ''} ({estado['campana']})".strip(),
                               f"— → creada en pausa ({nuevos_c} conjuntos, {len(estado['anuncios'])} anuncios, "
                               f"{_n(total_plan(plan, ctx.moneda), 2)} {ctx.moneda}/día al activar)")
    print("Fila para el change log:\n" + fila)
    print(f"Para activarlo, con el sí en ese momento: python3 -I herramientas/meta_ads.py activar --plan {a.plan} "
          f"--cliente {ctx.slug} --confirmo")


# ---------------------------------------------------------------- cambiar estado y presupuesto

def _ids(a: argparse.Namespace, ctx: Contexto) -> list[str]:
    if a.plan:
        _, ruta_estado = lee_plan(a.plan, ctx.slug)
        if not ruta_estado.exists():
            _salir(f"No hay {_rel(ruta_estado)}: ese plan no se ha creado todavía.", 1)
        estado = json.loads(ruta_estado.read_text(encoding="utf-8"))
        ya = set(estado.get("existentes") or [])  # lo que no creó el plan no se activa ni se pausa con --plan
        return [i for i in [estado.get("campana"), *estado["conjuntos"].values(),
                            *(x["anuncio"] for x in estado["anuncios"].values() if x.get("anuncio"))]
                if i and i not in ya]
    if not a.ids:
        _salir("Di qué: IDs o --plan <plan.json>.", 1)
    return a.ids


def _describe(meta: Meta, ctx: Contexto, ids: list[str]) -> list[dict]:
    """Nombre, nivel, estado y presupuesto de cada ID (campaña, conjunto o anuncio) de la cuenta de la ficha."""
    filtro = [{"field": "id", "operator": "IN", "value": ids}]
    vistos: dict[str, dict] = {}
    ahora = datetime.now(timezone.utc)
    for nivel, ruta, campos in [("campaña", "campaigns",
                                 f"id,name,status,effective_status,{CAMPOS_PRESUPUESTO},stop_time"),
                                ("conjunto", "adsets",
                                 f"id,name,status,effective_status,{CAMPOS_PRESUPUESTO},campaign_id,end_time"),
                                ("anuncio", "ads", "id,name,status,effective_status")]:
        for x in meta.lista(f"{ctx.cuenta}/{ruta}", fields=campos, filtering=filtro, limit=500):
            # dia: presupuesto diario propio (el que cambia `presupuesto`); efectivo: también el total, por día.
            vistos[x["id"]] = {**x, "nivel": nivel, "dia": de_minimo(x.get("daily_budget"), ctx.moneda),
                               "efectivo": diario_de(x, ctx.moneda, ahora)}
    if faltan := [i for i in ids if i not in vistos]:
        _salir(f"No están en {ctx.cuenta} (o están archivados): {', '.join(faltan)}", 1)
    return [vistos[i] for i in ids]


def _imprime(filas: list[dict], moneda: str) -> None:
    for x in filas:
        dinero = (f"{_n(x['dia'], 2)} {moneda}/día" if x.get("dia") else
                  f"total ≈ {_n(x['efectivo'], 2)} {moneda}/día" if x.get("efectivo") else "")
        print(f"  {x['nivel']:<9}{x['name'][:48]:<50}{x.get('status', ''):<9}{dinero:>16}")


def _tope_definido(ctx: Contexto) -> None:
    if ctx.tope_cambio <= 0:
        _salir(f"La ficha de {ctx.slug} no tiene topes (topes.cambio_dia = 0): fíjalos antes de mover presupuesto.", 1)


def cmd_pausar(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente)
    meta = conectar(ctx)
    ids = _ids(a, ctx)
    filas = _describe(meta, ctx, ids)
    try:
        for x in filas:
            meta.escribe(x["id"], status="PAUSED")
            comun.registrar_cambio("meta", "cli", "pausar", x["id"], ctx.slug, f"{x['nivel']} {x['name']}")
    except ErrorMeta as e:
        _salir(str(e), e.salida)
    if a.json:
        return _json({"ok": True, "pausados": ids})
    print(f"En pausa ({len(ids)}):")
    _imprime(filas, ctx.moneda)
    print("Fila para el change log:\n" + "\n".join(
        fila_change_log(x["nivel"], f"{x['name']} ({x['id']})", f"{x.get('status')} → PAUSED") for x in filas))


def presupuesto_que_entra(filas: list[dict], campanas: dict[str, dict], hijos: dict[str, list[dict]], moneda: str,
                          ahora: datetime) -> float:
    """Ritmo diario que empieza a gastar al activar `filas` (las de `_describe`). Puro, para poder probarlo.
    - Lo que no está activo suma su presupuesto diario o su presupuesto total por día (`diario_de`).
    - Un conjunto sin presupuesto propio de una campaña CBO activa que no entregaba (`otros_activos` falso) mete el
      presupuesto de la campaña (`campanas`: {id: campaña con otros_activos}); si la campaña se activa en la misma
      orden, ya cuenta por sí misma.
    - Una campaña ABO en pausa mete los presupuestos de sus conjuntos activos (`hijos`: {id: conjuntos}).
    Hallazgo 8, I6 (meta-ads-kb/02-estructura-campanas/06-presupuesto-por-niveles.md §1)."""
    ids = {str(x["id"]) for x in filas}
    dia = 0.0
    for x in filas:
        if x.get("status") == "ACTIVE" or x.get("nivel") == "anuncio":
            continue
        propio = diario_de(x, moneda, ahora)
        dia += propio
        if x.get("nivel") == "conjunto" and not propio:
            camp = campanas.get(str(x.get("campaign_id") or ""))
            if camp and str(camp.get("id")) not in ids and camp.get("status") == "ACTIVE" \
                    and not camp.get("otros_activos"):
                dia += diario_de(camp, moneda, ahora)
        elif x.get("nivel") == "campaña" and not propio:
            dia += sum(diario_de(c, moneda, ahora) for c in hijos.get(str(x["id"]), [])
                       if str(c.get("id")) not in ids and c.get("status") == "ACTIVE")
    return dia


def cmd_activar(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente)
    _tope_definido(ctx)
    meta = conectar(ctx)
    ids = _ids(a, ctx)
    filas = _describe(meta, ctx, ids)
    ahora = datetime.now(timezone.utc)
    campanas: dict[str, dict] = {}
    hijos: dict[str, list[dict]] = {}
    for x in filas:
        if x.get("status") == "ACTIVE" or x["efectivo"]:
            continue
        if x["nivel"] == "conjunto" and x.get("campaign_id") and str(x["campaign_id"]) not in campanas:
            cid = str(x["campaign_id"])
            camp = meta.uno(cid, fields=f"id,name,status,{CAMPOS_PRESUPUESTO},stop_time")
            hermanos = meta.lista(f"{cid}/adsets", fields="id,status", limit=200)
            campanas[cid] = {**camp, "otros_activos": any(str(h["id"]) not in ids and h.get("status") == "ACTIVE"
                                                          for h in hermanos)}
        elif x["nivel"] == "campaña":
            hijos[str(x["id"])] = meta.lista(f"{x['id']}/adsets", fields=f"id,status,{CAMPOS_PRESUPUESTO},end_time",
                                             limit=200)
    dia = presupuesto_que_entra(filas, campanas, hijos, ctx.moneda, ahora)
    activo, _ = presupuesto_activo(meta, ctx)
    if not a.json:
        print(f"Se va a ACTIVAR ({len(ids)}) · presupuesto diario que entra en juego (los totales, por día; el de "
              f"la campaña CBO, si es el que empieza a gastar): {_n(dia, 2)} {ctx.moneda} · "
              f"activo ahora en la cuenta: {_n(activo, 2)} {ctx.moneda}")
        _imprime(filas, ctx.moneda)
    if dia > ctx.tope_cambio:
        _salir(f"Suma {_n(dia, 2)} {ctx.moneda}/día y el tope por cambio de la ficha es {_n(ctx.tope_cambio, 2)}.", 1)
    if ctx.tope_total > 0 and activo + dia > ctx.tope_total:
        _salir(f"Con esto la cuenta pasaría a {_n(activo + dia, 2)} {ctx.moneda}/día y el tope diario total de la "
               f"ficha es {_n(ctx.tope_total, 2)}.", 1)
    if not a.confirmo:
        if a.json:
            _json({"ok": False, "motivo": "falta --confirmo", "presupuesto_que_entra": dia, "activo_ahora": activo})
        _salir("\nNo se ha activado nada. Solo con el sí del usuario en este momento: repite con --confirmo.", 1)
    orden = {"anuncio": 0, "conjunto": 1, "campaña": 2}  # de abajo arriba: la campaña se enciende la última
    try:
        for x in sorted(filas, key=lambda x: orden.get(x["nivel"], 0)):
            meta.escribe(x["id"], status="ACTIVE")
            comun.registrar_cambio("meta", "cli", "activar", x["id"], ctx.slug,
                                   f"{x['nivel']} {x['name']}" + (f", {x['dia']} {ctx.moneda}/día" if x["dia"] else ""))
    except ErrorMeta as e:
        _salir(f"{e}\nRevisa con `vigente` qué ha quedado activo.", e.salida)
    if a.json:
        return _json({"ok": True, "activados": ids, "presupuesto_que_entra": dia})
    print("\nActivado. Meta lo revisa antes de entregarlo (minutos u horas): `vigente` dice qué está gastando.")
    print("Fila para el change log:\n" + "\n".join(
        fila_change_log(x["nivel"], f"{x['name']} ({x['id']})", f"{x.get('status')} → ACTIVE")
        for x in filas if x["nivel"] != "anuncio" or len(filas) <= 3))


def cmd_presupuesto(a: argparse.Namespace) -> None:
    ctx = contexto(a.cliente)
    _tope_definido(ctx)
    if a.importe <= 0:
        _salir("El presupuesto tiene que ser mayor que 0 (para parar, usa `pausar`).", 1)
    meta = conectar(ctx)
    x = _describe(meta, ctx, [a.id])[0]
    antes = x["dia"]
    if antes is None:
        _salir(f"«{x['name']}» no tiene presupuesto diario propio (está en la campaña o en el conjunto).", 1)
    if a.importe > ctx.tope_cambio:
        _salir(f"{_n(a.importe, 2)} {ctx.moneda}/día pasa del tope por cambio de la ficha "
               f"({_n(ctx.tope_cambio, 2)}).", 1)
    activo, conjuntos = presupuesto_activo(meta, ctx)
    entrega = x["id"] in {c["id"] for c in conjuntos} | {c["campaign"]["id"] for c in conjuntos}
    nuevo_total = activo - antes + a.importe if entrega else activo
    if not a.json:
        print(f"{x['nivel']} «{x['name']}» ({x.get('effective_status')}): {_n(antes, 2)} → {_n(a.importe, 2)} "
              f"{ctx.moneda}/día · la cuenta quedaría en {_n(nuevo_total, 2)} {ctx.moneda}/día activos")
    if ctx.tope_total > 0 and nuevo_total > ctx.tope_total:
        _salir(f"Pasa del tope diario total de la ficha ({_n(ctx.tope_total, 2)}).", 1)
    if not a.confirmo:
        if a.json:
            _json({"ok": False, "motivo": "falta --confirmo", "antes": antes, "despues": a.importe,
                   "total_activo_despues": nuevo_total})
        _salir("No se ha cambiado nada. Solo con el sí del usuario en este momento: repite con --confirmo.", 1)
    try:
        meta.escribe(a.id, daily_budget=a_minimo(a.importe, ctx.moneda))
    except ErrorMeta as e:
        _salir(str(e), e.salida)
    comun.registrar_cambio("meta", "cli", "presupuesto", a.id, ctx.slug,
                           f"{x['nivel']} {x['name']}: {antes} → {a.importe} {ctx.moneda}/día")
    if a.json:
        return _json({"ok": True, "id": a.id, "antes": antes, "despues": a.importe, "moneda": ctx.moneda})
    print("Cambiado. Puede reiniciar el aprendizaje: no lo evalúes antes de 7 días.")
    print("Fila para el change log:\n" + fila_change_log(
        x["nivel"], f"{x['name']} ({x['id']})", f"presupuesto {_n(antes, 2)} → {_n(a.importe, 2)} {ctx.moneda}/día"))


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> None:
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--cliente", help="slug del cliente (clientes/<slug>/ficha.md)")
    comunes.add_argument("--json", action="store_true", help="salida en JSON")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("cuentas", parents=[comunes], help="cuentas publicitarias que ve el token")
    sub.add_parser("activos", parents=[comunes], help="página, Instagram, datasets y públicos (IDs para un plan)")
    sub.add_parser("campanas", parents=[comunes], help="campañas con gasto, de la más reciente a la más antigua")
    sub.add_parser("vigente", parents=[comunes], help="lo que puede gastar ahora, con gasto y resultados de 7 días")
    an = sub.add_parser("anuncios", parents=[comunes], help="métricas anuncio a anuncio → CSV en datos/ + resumen")
    an.add_argument("--campana", help="solo campañas cuyo nombre contiene este texto")
    an.add_argument("--campana-id", dest="campana_id", action="append", help="solo esta campaña (repetible)")
    an.add_argument("--mes", help="AAAA-MM")
    an.add_argument("--desde", help="AAAA-MM-DD")
    an.add_argument("--hasta", help="AAAA-MM-DD (por defecto hoy)")
    an.add_argument("--por-pais", action="store_true", help="una fila por anuncio y país")
    an.add_argument("--por-dia", action="store_true", help="una fila por anuncio y día (para ver el cansancio)")
    an.add_argument("--evento", default="auto", help="action_type que cuenta como resultado (auto = el optimizado)")
    an.add_argument("--acciones", action="store_true", help="lista todas las acciones que cuenta Meta por campaña")
    an.add_argument("--salida", help="ruta del CSV, o - para sacarlo por pantalla")
    an.add_argument("--sin-archivos", action="store_true", help="no guarda el CSV (solo el resumen)")
    an.add_argument("--estado", action="store_true",
                    help="añade los anuncios rechazados, con problemas o en revisión (con_problemas en --json)")
    ev = sub.add_parser("eventos", parents=[comunes], help="eventos que recibió el dataset por día, sin atribución")
    ev.add_argument("--desde", help="AAAA-MM-DD (por defecto, hace 7 días)")
    ev.add_argument("--hasta", help="AAAA-MM-DD (por defecto, hoy)")
    ev.add_argument("--dataset", help="ID del dataset si no es el de la ficha")
    cv = sub.add_parser("creatividades", parents=[comunes], help="textos y mejoras automáticas activas de cada anuncio")
    cv.add_argument("--campana-id", dest="campana_id", action="append", help="campaña (repetible)")
    cv.add_argument("--plan", help="la campaña creada desde este plan")
    cr = sub.add_parser("crear", parents=[comunes], help="crea un plan de campaña, todo en pausa")
    cr.add_argument("plan", help="ruta del plan (formato en plantillas/plan-campana.json)")
    cr.add_argument("--simular", action="store_true", help="solo revisa el plan y lo dibuja; no toca Meta")
    for nombre, ayuda in [("pausar", "pone en pausa campañas, conjuntos o anuncios"),
                          ("activar", "activa campañas, conjuntos o anuncios (requiere --confirmo)")]:
        x = sub.add_parser(nombre, parents=[comunes], help=ayuda)
        x.add_argument("ids", nargs="*", help="IDs de campaña, conjunto o anuncio")
        x.add_argument("--plan", help="todo lo creado desde este plan")
        if nombre == "activar":
            x.add_argument("--confirmo", action="store_true", help="el usuario ha dicho que sí en este momento")
    pr = sub.add_parser("presupuesto", parents=[comunes],
                        help="cambia el presupuesto diario de una campaña o conjunto (requiere --confirmo)")
    pr.add_argument("id")
    pr.add_argument("importe", type=float, help="presupuesto diario en la moneda de la ficha")
    pr.add_argument("--confirmo", action="store_true", help="el usuario ha dicho que sí en este momento")
    a = p.parse_args(argv)
    ordenes = {"cuentas": cmd_cuentas, "activos": cmd_activos, "campanas": cmd_campanas, "vigente": cmd_vigente,
               "anuncios": cmd_anuncios, "eventos": cmd_eventos, "creatividades": cmd_creatividades,
               "crear": cmd_crear, "pausar": cmd_pausar, "activar": cmd_activar, "presupuesto": cmd_presupuesto}
    try:
        ordenes[a.comando](a)
    except ErrorMeta as e:
        _salir(str(e), e.salida)


if __name__ == "__main__":
    main()
