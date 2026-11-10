#!/usr/bin/env python3
"""Conversions API de Meta: construir, hashear, validar y enviar eventos de servidor (solo biblioteca estándar).

Para qué: probar la señal que mandas desde GHL, n8n, Make, Stripe o tu backend antes de fiarte de ella. La guía es
`docs/guias/capi.md`; el porqué, `meta-ads-kb/04-tracking-atribucion-medicion/03-emq-advanced-matching-pii-hashing.md`
y `07-custom-builds-api-directa.md`.

  python3 -I herramientas/capi.py hashear "Ana.Lopez@Ejemplo.com" --tipo em
  python3 -I herramientas/capi.py hashear "612 34 56 78" --tipo ph --prefijo 34
  python3 -I herramientas/capi.py hashear --archivo clientes/acme/privado/clientes.csv --columnas email,telefono \
      --prefijo 34 [--salida clientes/acme/privado/clientes-hash.csv] [--conservar valor] [--sobrescribir]
  python3 -I herramientas/capi.py construir --evento Lead --origen website --url https://acme-automations.example/gracias \\
      --email prueba@acme-automations.example --ip 203.0.113.7 --ua "Mozilla/5.0 ..." --event-id lead_123 --salida ev.json
  python3 -I herramientas/capi.py construir --etapa cualificado --crm GHL --lead-id 1234567890123456 --email ...
  python3 -I herramientas/capi.py construir --entrada eventos-en-claro.json --salida payload.json
  python3 -I herramientas/capi.py validar payload.json
  python3 -I herramientas/capi.py enviar payload.json --cliente acme --test-code TEST12345
  python3 -I herramientas/capi.py enviar payload.json --cliente acme --real --confirmo   # solo con el sí del usuario

Mensajería (Click to WhatsApp, Messenger e Instagram Direct; guía `docs/guias/mensajeria.md`):
  python3 -I herramientas/capi.py origen clientes/acme/privado/webhook.json      # ¿llega el clic del anuncio?
  python3 -I herramientas/capi.py construir --canal whatsapp --etapa cualificado --cliente acme \\
      --desde-webhook clientes/acme/privado/webhook.json --salida clientes/acme/privado/ev-mensajeria.json
  python3 -I herramientas/capi.py construir --canal whatsapp --etapa ganado --waba 100000000000001 \\
      --ctwa-clid <clid> --valor 4800 --moneda EUR
  python3 -I herramientas/capi.py construir --canal messenger --etapa lead --pagina <id> --psid <psid>
  python3 -I herramientas/capi.py enviar clientes/acme/privado/ev-mensajeria.json --cliente acme --test-code TEST12345

  Etapas del CRM (Conversion Leads): `--etapa <id del §16> --crm <CRM>` pone el event_name exacto de la tabla del
  contrato §16 (cualificado → LeadCualificado, asistio → LlamadaAsistida, ganado → Purchase…), con
  action_source=system_generated, event_source=crm y lead_event_source. `validar` avisa si un nombre no es el del §16
  (raw_lead, qualified, «Cualificado», el nombre visible de la etapa de GHL…): dos nombres para el mismo hito reparten
  la señal de la etapa objetivo.

  Las etapas son las del contrato §16. En mensajería Meta solo admite su lista cerrada de eventos (LeadSubmitted,
  QualifiedLead, Purchase…): lead → LeadSubmitted, cualificado → QualifiedLead (o la etapa de --cualifica-en),
  ganado → Purchase con valor. Diagnóstico, llamada, asistencia y propuesta no tienen evento de mensajería: se quedan
  en el CRM o, si ocurren en tu web, van por la CAPI web. Meta no deduplica estos eventos: cada hito, una sola vez.

Reglas:
- `enviar` solo manda con `--test-code` (Events Manager → Probar eventos). Sin código exige `--real --confirmo`: un
  evento real de prueba ensucia el dataset y la optimización del cliente.
- Ojo: Meta tampoco descarta los eventos con `test_event_code` (dice que se usan para segmentación y medición).
  Prueba con tu propia identidad (tu email, tu teléfono), nunca con datos de leads reales.
- Antes de enviar siempre valida; con errores no manda nada.
- `construir --entrada` acepta eventos con la forma de Meta y datos en claro, normaliza y hashea lo que toca y deja
  igual lo que ya viene hasheado o no se hashea (fbc, fbp, IP, user agent, lead_id...).
- Nunca imprime el token. Las direcciones de email y teléfonos en claro no se guardan en ningún registro.
- `hashear --archivo` prepara una lista de clientes para un público (excluir clientes o usarlos de semilla) sin que
  salga ningún dato en claro: normaliza cada columna según Meta, la hashea con SHA-256 y escribe solo las columnas
  hasheadas con los nombres de la plantilla de listas de clientes (email, phone, fn, ln, ct, st, zip, country, gen,
  doby/dobm/dobd, extern_id). Entrada y salida van en clientes/<slug>/privado/: los hashes siguen siendo datos
  personales. Por pantalla solo salen recuentos, nunca valores.

Credenciales (`.env`): `META_CAPI_TOKEN` (o `META_CAPI_TOKEN_<SLUG>`), el token de la Conversions API del dataset
(Events Manager → Configuración → Generar token de acceso). El dataset sale de `meta.dataset` de la ficha.
Para mensajería, `META_CAPI_MENSAJERIA_TOKEN` (o `_<SLUG>`): un token con `whatsapp_business_manage_events`,
`page_events` o `instagram_manage_events` según el canal; si no existe se prueba con `META_CAPI_TOKEN`. El dataset
es `meta.dataset_mensajeria` si la ficha lo tiene (el vinculado a la WABA, la Página o la cuenta de Instagram) y si no,
`meta.dataset`. La WABA sale de `meta.waba`, la Página de `meta.pagina` y la cuenta de Instagram de `meta.instagram`
(solo si es numérico), o de las opciones de la orden.
Versión de la API: `META_API_VERSION` (por defecto la de `VERSION`).

Interfaz estable. La usan skills (`/implementar-capi`, `/audiencias`, `/construir-landing`, `/webinar`), las
plantillas de n8n, Make y backend propio de `plantillas/integraciones/` y `herramientas/audiencias_meta.py`: no cambia
sin anotarlo en CHANGELOG.md.
- Órdenes y opciones: las de `--help` de cada orden (hashear, construir, validar, origen, enviar). Las etapas de
  `--etapa` y `--cualifica-en` son las del contrato §16; los códigos de salida, los de abajo (contrato §9).
- `construir` escribe {"data": [eventos]}, lo que lee `enviar` (que acepta también un evento suelto o una lista); el
  código de prueba no va en el payload sino en `enviar --test-code`.
- `hashear --archivo` escribe solo hashes, con las cabeceras de SALIDA_LISTA (email, phone, fn, ln, ct, st, zip,
  country, gen, doby, dobm, dobd, extern_id); `external_id` se hashea igual que en `construir`.
- Funciones que importan otras herramientas: sha256, es_hash, hashear_para_lista, SALIDA_LISTA, ALIAS_COLUMNAS,
  Invalido, _leer_tabla, _columnas_pedidas, _cabecera_normal, _ruta y _rel (el guion bajo es histórico: también son
  estables). tests/herramientas/test_capi.py comprueba que siguen ahí.

Códigos de salida: 0 bien · 1 error del usuario (evento inválido, falta confirmación) · 2 configuración (ficha, token).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import os
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun as comun  # noqa: E402

VERSION = "v27.0"  # desde el 2026-11-10 (salió el 2026-11-04); lo que cambia y lo revisado: docs/desarrollo/notas/I4.md
GRAPH = "https://graph.facebook.com"

ORIGENES = ("website", "app", "email", "phone_call", "chat", "physical_store", "system_generated",
            "business_messaging", "other")
ESTANDAR = ("AddPaymentInfo", "AddToCart", "AddToWishlist", "CompleteRegistration", "Contact", "CustomizeProduct",
            "Donate", "FindLocation", "InitiateCheckout", "Lead", "PageView", "Purchase", "Schedule", "Search",
            "StartTrial", "SubmitApplication", "Subscribe", "ViewContent")
# Claves de user_data que Meta pide normalizadas y hasheadas con SHA-256 (external_id: hash recomendado).
HASHEAR = ("em", "ph", "fn", "ln", "db", "ge", "ct", "st", "zp", "country", "external_id")
# Claves que van tal cual: hashearlas rompe el emparejamiento. Las dos últimas son de la CAPI de mensajería.
SIN_HASH = ("client_ip_address", "client_user_agent", "fbc", "fbp", "lead_id", "subscription_id", "fb_login_id",
            "anon_id", "madid", "page_id", "page_scoped_user_id", "ctwa_clid", "ig_account_id", "ig_sid",
            "whatsapp_business_account_id", "instagram_business_account_id")
# Identificadores que Meta quiere en claro: un hash aquí es siempre un error.
NUNCA_HASH = ("fbc", "fbp", "client_ip_address", "client_user_agent", "ctwa_clid", "page_id", "page_scoped_user_id",
              "ig_sid", "ig_account_id", "whatsapp_business_account_id", "instagram_business_account_id")
MAX_EVENTOS = 1000
MAX_DIAS = 7
_HASH = re.compile(r"[0-9a-f]{64}")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_FBC = re.compile(r"fb\.\d\.\d{10,13}\.\S+")
_FBP = re.compile(r"fb\.\d\.\d{10,13}\.\d+")


class Invalido(ValueError):
    """Dato que no se puede normalizar."""


def _salir(mensaje: str, codigo: int) -> None:
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


# ---------------------------------------------------------------- normalizar y hashear

def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def es_hash(valor) -> bool:
    return isinstance(valor, str) and bool(_HASH.fullmatch(valor.lower()))


def _sin_puntuacion(valor: str) -> str:
    v = unicodedata.normalize("NFC", valor.strip().lower())
    return "".join(c for c in v if c.isalnum())


def normalizar_email(v: str) -> str:
    v = v.strip().lower()
    if not _EMAIL.fullmatch(v):
        raise Invalido(f"no parece un email: {v[:3]}***")
    return v


def normalizar_telefono(v: str, prefijo: str | None = None) -> str:
    """Solo dígitos y con prefijo de país (Meta lo exige aunque todo el tráfico sea de un país)."""
    bruto = v.strip()
    internacional = bruto.startswith(("+", "00"))
    d = re.sub(r"\D", "", bruto)
    if d.startswith("00"):
        d = d[2:]
    if internacional:
        resultado = d
    elif prefijo:
        p = re.sub(r"\D", "", prefijo)
        resultado = d if d.startswith(p) and len(d) >= len(p) + 8 else p + d.lstrip("0")
    else:
        raise Invalido("teléfono sin prefijo de país: escríbelo como +34… o pasa --prefijo")
    if not 7 <= len(resultado) <= 15:
        raise Invalido("teléfono con una longitud imposible tras normalizar")
    return resultado


def normalizar_fecha(v: str) -> str:
    t = v.strip()
    for formato in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(t, formato).strftime("%Y%m%d")
        except ValueError:
            pass
    raise Invalido("fecha de nacimiento como AAAA-MM-DD o AAAAMMDD")


def normalizar_genero(v: str) -> str:
    t = v.strip().lower()
    if t in ("f", "m"):
        return t
    mapa = {"mujer": "f", "femenino": "f", "female": "f", "hombre": "m", "masculino": "m", "male": "m"}
    if t in mapa:
        return mapa[t]
    raise Invalido("género: f o m")


def normalizar_pais(v: str) -> str:
    t = v.strip().lower()
    if not re.fullmatch(r"[a-z]{2}", t):
        raise Invalido("país como código ISO de 2 letras (es, mx, co...)")
    return t


def normalizar_cp(v: str) -> str:
    t = v.strip().lower()
    if re.fullmatch(r"\d{5}-\d{4}", t):  # EE. UU.: solo los 5 primeros dígitos
        return t[:5]
    return re.sub(r"[\s-]", "", t)


def normalizar(clave: str, valor, prefijo: str | None = None) -> str:
    v = str(valor)
    if clave == "em":
        return normalizar_email(v)
    if clave == "ph":
        return normalizar_telefono(v, prefijo)
    if clave in ("fn", "ln", "ct", "st"):
        r = _sin_puntuacion(v)
        if not r:
            raise Invalido(f"{clave} vacío tras normalizar")
        return r
    if clave == "db":
        return normalizar_fecha(v)
    if clave == "ge":
        return normalizar_genero(v)
    if clave == "country":
        return normalizar_pais(v)
    if clave == "zp":
        return normalizar_cp(v)
    if clave == "external_id":
        return v.strip()  # sin cambiar mayúsculas: tiene que ser idéntico en web, CRM y backend
    raise Invalido(f"clave desconocida: {clave}")


def hashear(clave: str, valor, prefijo: str | None = None) -> str:
    """Normaliza y hashea. Si ya viene hasheado (64 hex), lo deja en minúsculas sin volver a hashear."""
    if es_hash(valor):
        return str(valor).lower()
    return sha256(normalizar(clave, valor, prefijo))


def hashear_user_data(ud: dict, prefijo: str | None = None) -> dict:
    """Devuelve una copia de user_data con las claves de HASHEAR en listas de hashes."""
    salida: dict = {}
    for clave, valor in ud.items():
        if clave in HASHEAR:
            valores = valor if isinstance(valor, list) else [valor]
            hashes = [hashear(clave, x, prefijo) for x in valores if str(x).strip()]
            if hashes:
                salida[clave] = hashes
        else:
            salida[clave] = valor
    return salida


def fbc_desde_fbclid(fbclid: str, momento_ms: int | None = None) -> str:
    """`fb.1.<milisegundos>.<fbclid>`: el formato de la cookie _fbc (el fbclid se copia sin tocar mayúsculas)."""
    return f"fb.1.{momento_ms or int(time.time() * 1000)}.{fbclid.strip()}"


# ---------------------------------------------------------------- validar

def _como_lista(payload) -> list:
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"] if isinstance(payload["data"], list) else [payload["data"]]
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return [payload]
    return []


def validar(payload, ahora: float | None = None) -> tuple[list[str], list[str]]:
    """(errores, avisos). Con errores Meta rechazaría el lote entero o el evento no serviría."""
    ahora = ahora if ahora is not None else time.time()
    errores: list[str] = []
    avisos: list[str] = []
    eventos = _como_lista(payload)
    if not eventos:
        return ["el payload no tiene eventos (usa {\"data\": [ ... ]})"], []
    if len(eventos) > MAX_EVENTOS:
        errores.append(f"{len(eventos)} eventos en un lote: el máximo es {MAX_EVENTOS} (mejor lotes pequeños)")
    vistos: set[tuple] = set()
    hitos: set[tuple] = set()
    canales_lote: set[str] = set()
    for i, ev in enumerate(eventos, 1):
        donde = f"evento {i}"
        if not isinstance(ev, dict):
            errores.append(f"{donde}: no es un objeto JSON")
            continue
        nombre = ev.get("event_name")
        if not isinstance(nombre, str) or not nombre.strip():
            errores.append(f"{donde}: falta event_name")
            nombre = ""
        else:
            donde = f"evento {i} «{nombre}»"
            parecido = next((e for e in ESTANDAR if e.lower() == nombre.lower() and e != nombre), None)
            if parecido:
                avisos.append(f"{donde}: ¿querías «{parecido}»? Los nombres distinguen mayúsculas")
            elif ev.get("action_source") != "business_messaging" and "messaging_channel" not in ev:
                canonico = nombre_canonico(nombre)
                if canonico and canonico != nombre:
                    avisos.append(f"{donde}: no es el nombre del contrato §16: usa «{canonico}». El mismo hito con "
                                  "dos nombres reparte la señal de la etapa objetivo en el dataset")
        t = ev.get("event_time")
        if not isinstance(t, int) or isinstance(t, bool):
            errores.append(f"{donde}: event_time tiene que ser un entero (segundos Unix)")
        elif t > 10 ** 11:
            errores.append(f"{donde}: event_time parece en milisegundos; Meta lo quiere en segundos")
        elif t > ahora + 300:
            errores.append(f"{donde}: event_time está en el futuro")
        elif ahora - t > MAX_DIAS * 86400:
            errores.append(f"{donde}: event_time tiene más de {MAX_DIAS} días: Meta lo rechaza")
        origen = ev.get("action_source")
        if origen not in ORIGENES:
            errores.append(f"{donde}: action_source «{origen}» no válido ({', '.join(ORIGENES)})")
        url = ev.get("event_source_url")
        if origen == "website":
            if not (isinstance(url, str) and url.startswith(("https://", "http://"))):
                errores.append(f"{donde}: con action_source=website, event_source_url es obligatorio")
            if not (ev.get("user_data") or {}).get("client_user_agent"):
                errores.append(f"{donde}: con action_source=website, user_data.client_user_agent es obligatorio")
            if not ev.get("event_id"):
                avisos.append(f"{donde}: sin event_id no se deduplica con el píxel (mismo event_id y event_name)")
        if isinstance(url, str) and (_EMAIL.search(urllib.parse.unquote(url)) or re.search(r"[?&](email|phone|tel)=", url, re.I)):
            errores.append(f"{donde}: event_source_url lleva datos personales: quítalos de la URL")
        ud = ev.get("user_data")
        if not isinstance(ud, dict) or not ud:
            errores.append(f"{donde}: user_data vacío: hace falta al menos un dato de cliente")
            ud = {}
        for clave, valor in ud.items():
            if clave in HASHEAR:
                valores = valor if isinstance(valor, list) else [valor]
                sin_hash = [x for x in valores if not es_hash(x)]
                if sin_hash and clave == "external_id":
                    avisos.append(f"{donde}: external_id sin hashear (Meta recomienda hashearlo; usa el mismo valor en todos los canales)")
                elif sin_hash:
                    errores.append(f"{donde}: user_data.{clave} parece en claro: hashéalo (capi.py construir --entrada)")
            elif clave in SIN_HASH:
                if clave in NUNCA_HASH and es_hash(valor):
                    errores.append(f"{donde}: user_data.{clave} está hasheado y Meta lo quiere tal cual")
                elif clave == "fbc" and not _FBC.fullmatch(str(valor)):
                    avisos.append(f"{donde}: fbc no tiene el formato fb.1.<ms>.<fbclid>")
                elif clave == "fbp" and not _FBP.fullmatch(str(valor)):
                    avisos.append(f"{donde}: fbp no tiene el formato fb.1.<ms>.<número>")
                elif clave == "client_ip_address":
                    try:
                        ipaddress.ip_address(str(valor))
                    except ValueError:
                        errores.append(f"{donde}: client_ip_address no es una IP válida")
                elif clave == "lead_id":
                    if not re.fullmatch(r"\d+", str(valor)):
                        errores.append(f"{donde}: lead_id tiene que ser el ID numérico del formulario de Meta")
                    elif not 15 <= len(str(valor)) <= 17:
                        avisos.append(f"{donde}: lead_id suele tener 15–17 dígitos (¿se ha redondeado en una hoja de cálculo?)")
            else:
                avisos.append(f"{donde}: user_data.{clave} no es un parámetro de cliente conocido")
        if origen == "business_messaging" or "messaging_channel" in ev:
            hito = _validar_mensajeria(ev, nombre, origen, ud, donde, errores, avisos)
            if hito and hito in hitos:
                avisos.append(f"{donde}: el mismo hito para la misma conversación ya va en este lote y Meta no "
                              "deduplica la mensajería: mándalo una sola vez")
            hitos.add(hito)
            canales_lote.add("mensajeria")
        else:
            canales_lote.add("otro")
            if ud.get("ctwa_clid"):
                avisos.append(f"{donde}: ctwa_clid solo sirve con action_source=business_messaging y "
                              "messaging_channel=whatsapp")
        cd = ev.get("custom_data") or {}
        if not isinstance(cd, dict):
            errores.append(f"{donde}: custom_data tiene que ser un objeto")
            cd = {}
        if nombre == "Purchase" and ("value" not in cd or "currency" not in cd):
            errores.append(f"{donde}: Purchase necesita custom_data.value y custom_data.currency")
        if "value" in cd:
            if not isinstance(cd["value"], (int, float)) or isinstance(cd["value"], bool):
                errores.append(f"{donde}: custom_data.value tiene que ser un número")
            elif cd["value"] < 0:
                errores.append(f"{donde}: value negativo: no envíes devoluciones como valores negativos")
            if "currency" not in cd:
                errores.append(f"{donde}: value sin currency")
        if "currency" in cd and not re.fullmatch(r"[A-Za-z]{3}", str(cd["currency"])):
            errores.append(f"{donde}: currency como código ISO 4217 de 3 letras (EUR, USD, MXN...)")
        if _EMAIL.search(json.dumps(cd, ensure_ascii=False)):
            errores.append(f"{donde}: custom_data lleva un email: los datos personales solo van hasheados en user_data")
        if cd.get("event_source") == "crm":
            if origen != "system_generated":
                errores.append(f"{donde}: un evento del CRM va con action_source=system_generated")
            if not cd.get("lead_event_source"):
                errores.append(f"{donde}: un evento del CRM necesita custom_data.lead_event_source (p. ej. «GHL»)")
            if not ud.get("lead_id"):
                avisos.append(f"{donde}: sin lead_id solo empareja por email o teléfono (peor para Conversion Leads)")
        clave = (nombre, ev.get("event_id"))
        if ev.get("event_id") and clave in vistos:
            avisos.append(f"{donde}: event_id repetido en el lote: Meta se quedará con uno")
        vistos.add(clave)
    if len(canales_lote) > 1:
        avisos.append("el lote mezcla eventos de mensajería con eventos web o de CRM: mándalos en lotes separados "
                      "(otro token, otros permisos y, si uno falla, Meta descarta el lote entero)")
    return errores, avisos


# ---------------------------------------------------------------- mensajería (Conversions API for Business Messaging)
# Referencia: developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging (2026-11-09) y
# meta-ads-kb/07-instagram-placements-mensajeria/12-whatsapp-business-platform-medicion-revenue.md §4.

CANALES = ("whatsapp", "messenger", "instagram")
# Lista cerrada de Meta: con action_source=business_messaging rechaza Lead, Schedule y los nombres personalizados.
EVENTOS_MENSAJERIA = ("LeadSubmitted", "QualifiedLead", "Purchase", "InitiateCheckout", "AddToCart", "ViewContent",
                      "OrderCreated", "OrderShipped", "OrderDelivered", "OrderCanceled", "OrderReturned",
                      "CartAbandoned", "RatingProvided", "ReviewProvided")
# Etapas canónicas del embudo consultivo (contrato §16), en orden.
ETAPAS = ("lead", "diagnostico", "cualificado", "llamada", "asistio", "propuesta", "ganado", "perdido")
# Etapas de un taller o webinar (contrato §16, «Eventos»): preceden a «cualificado» en el mismo dataset.
ETAPAS_TALLER = ("registro_evento", "asistio_evento", "hasta_oferta")
# La tabla canónica etapa → event_name (web y CRM) del contrato §16. Es la única: páginas, plantillas de n8n y Make,
# skills y guías usan estos nombres tal cual (mayúsculas incluidas). La mensajería tiene la suya (evento_de_etapa).
EVENTO_ETAPA = {"lead": "Lead", "diagnostico": "DiagnosticoCompletado", "cualificado": "LeadCualificado",
                "llamada": "Schedule", "asistio": "LlamadaAsistida", "propuesta": "PropuestaEnviada",
                "ganado": "Purchase", "perdido": "LeadPerdido", "registro_evento": "CompleteRegistration",
                "asistio_evento": "WebinarAsistido", "hasta_oferta": "WebinarHastaOferta"}
# Etapas que casi siempre salen del CRM (sin --crm, Conversion Leads no las reconoce).
ETAPAS_SOLO_CRM = ("asistio", "propuesta", "ganado", "perdido", "asistio_evento", "hasta_oferta")
# Otros nombres del mismo hito (los de la KB, los nombres visibles de GHL, en inglés…) → el nombre del §16.
# Clave: en minúsculas, sin tildes ni nada que no sea una letra.
ALIAS_ETAPA = {
    "rawlead": "Lead", "leadbruto": "Lead", "nuevolead": "Lead", "newlead": "Lead", "leadsubmitted": "Lead",
    "diagnostico": "DiagnosticoCompletado", "diagnosticohecho": "DiagnosticoCompletado",
    "cualificado": "LeadCualificado", "qualified": "LeadCualificado", "qualifiedlead": "LeadCualificado",
    "leadqualified": "LeadCualificado", "cualificada": "LeadCualificado",
    "llamada": "Schedule", "booked": "Schedule", "bookedcall": "Schedule", "cita": "Schedule",
    "citaagendada": "Schedule", "llamadaagendada": "Schedule", "agendado": "Schedule", "agendada": "Schedule",
    "asistio": "LlamadaAsistida", "showed": "LlamadaAsistida", "show": "LlamadaAsistida",
    "llamadarealizada": "LlamadaAsistida", "asistida": "LlamadaAsistida",
    "propuesta": "PropuestaEnviada", "proposal": "PropuestaEnviada", "proposalsent": "PropuestaEnviada",
    "ganado": "Purchase", "won": "Purchase", "closedwon": "Purchase", "cerrado": "Purchase",
    "cerradoganado": "Purchase", "venta": "Purchase", "compra": "Purchase",
    "perdido": "LeadPerdido", "lost": "LeadPerdido", "disqualified": "LeadPerdido", "descalificado": "LeadPerdido",
    "nocualificado": "LeadPerdido", "leaddescalificado": "LeadPerdido",
    "registroevento": "CompleteRegistration", "registrado": "CompleteRegistration",
    "asistioevento": "WebinarAsistido", "webinarattended": "WebinarAsistido", "asistioaltaller": "WebinarAsistido",
    "asistioalwebinar": "WebinarAsistido",
    "hastaoferta": "WebinarHastaOferta", "stayedtopitch": "WebinarHastaOferta",
    "sequedoalaoferta": "WebinarHastaOferta",
}
# Etapas que pueden hacer de «lead cualificado» en mensajería (una sola por cliente: --cualifica-en).
CUALIFICA_EN = ("cualificado", "llamada", "asistio", "propuesta")
SIN_EVENTO_MENSAJERIA = {
    "diagnostico": "la CAPI de mensajería no admite eventos personalizados (DiagnosticoCompletado). Si el "
                   "diagnóstico se completa en tu web, va por la CAPI web; si es la conversación la que cualifica, "
                   "usa la etapa «cualificado»",
    "llamada": "Schedule no está entre los eventos de mensajería. Si la llamada se reserva en tu web con el píxel, "
               "Schedule va por la CAPI web (mismo event_id que el píxel). Si el agente agenda dentro del chat y "
               "agendar es tu filtro de calidad, usa --cualifica-en llamada",
    "asistio": "no hay evento de mensajería para la asistencia: se queda en el CRM (coste por show en ghl.py "
               "por-anuncio). Si la asistencia es tu criterio de calidad, usa --cualifica-en asistio",
    "propuesta": "no hay evento de mensajería para la propuesta: se queda en el CRM. Si es tu criterio de calidad, "
                 "usa --cualifica-en propuesta",
    "perdido": "no se envía a Meta: sirve para audiencias y exclusiones, con el motivo en el CRM (contrato §16)",
    "registro_evento": "el registro al taller va por la CAPI web (CompleteRegistration con el event_id del píxel)",
    "asistio_evento": "la asistencia al taller va por el CRM (WebinarAsistido, contrato §16)",
    "hasta_oferta": "quedarse a la oferta va por el CRM (WebinarHastaOferta, contrato §16)",
}
# Por canal: (clave de la cuenta del negocio, clave de la persona) en user_data.
IDENTIDAD = {"whatsapp": ("whatsapp_business_account_id", "ctwa_clid"),
             "messenger": ("page_id", "page_scoped_user_id"),
             "instagram": ("instagram_business_account_id", "ig_sid")}
# Datos de cliente que sirven para emparejar en WhatsApp sin ctwa_clid (external_id no cuenta, según Meta).
DATOS_SIN_CLIC = ("em", "ph", "fn", "ln", "ct", "st", "zp", "country", "ge", "db")
SUGERENCIA_EVENTO = {"lead": "LeadSubmitted", "contact": "LeadSubmitted", "completeregistration": "LeadSubmitted",
                     "submitapplication": "LeadSubmitted", "leadcualificado": "QualifiedLead",
                     "cualificado": "QualifiedLead", "qualified": "QualifiedLead", "qualifiedlead": "QualifiedLead",
                     "leadsubmitted": "LeadSubmitted", "purchase": "Purchase", "compra": "Purchase"}
VENTANA_CLIC_DIAS = 7  # ventana de atribución por clic más larga que ofrece Meta (7d_click)
_DIGITOS = re.compile(r"\d{5,25}")


def evento_de_etapa(etapa: str, cualifica_en: str = "cualificado") -> str:
    """Etapa del §16 → evento de la CAPI de mensajería. Si la etapa no tiene evento, `Invalido` explica qué hacer."""
    etapa = (etapa or "").strip().lower()
    if etapa in ETAPAS_TALLER:
        raise Invalido(f"la etapa «{etapa}» no tiene evento de mensajería: {SIN_EVENTO_MENSAJERIA[etapa]}")
    if etapa not in ETAPAS:
        raise Invalido(f"etapa «{etapa}» desconocida: usa una del contrato §16 ({', '.join(ETAPAS)})")
    if cualifica_en not in CUALIFICA_EN:
        raise Invalido(f"--cualifica-en tiene que ser una de {', '.join(CUALIFICA_EN)}")
    if etapa == "lead":
        return "LeadSubmitted"
    if etapa == "ganado":
        return "Purchase"
    if etapa == cualifica_en:
        return "QualifiedLead"
    if etapa == "cualificado":
        raise Invalido(f"en este cliente QualifiedLead se manda en «{cualifica_en}»: mandarlo también en "
                       "«cualificado» duplicaría el hito (Meta no deduplica la mensajería)")
    raise Invalido(f"la etapa «{etapa}» no tiene evento de mensajería: {SIN_EVENTO_MENSAJERIA[etapa]}")


def nombre_canonico(nombre: str) -> str | None:
    """El event_name del §16 para un nombre de etapa (canónico con otras mayúsculas, alias o id de etapa). None si
    no se parece a ninguno."""
    clave = "".join(c for c in unicodedata.normalize("NFKD", str(nombre or "").lower()) if "a" <= c <= "z")
    for canonico in EVENTO_ETAPA.values():
        if clave == canonico.lower():
            return canonico
    return ALIAS_ETAPA.get(clave)


def _sugerir_evento(nombre: str) -> str:
    clave = re.sub(r"[^a-z]", "", nombre.lower())
    if clave == "schedule":
        return " Schedule no existe en mensajería: " + SIN_EVENTO_MENSAJERIA["llamada"]
    s = SUGERENCIA_EVENTO.get(clave)
    return f" ¿Querías «{s}»?" if s else ""


def _validar_mensajeria(ev: dict, nombre: str, origen, ud: dict, donde: str, errores: list, avisos: list):
    """Reglas de la CAPI de mensajería. Devuelve la clave del hito (evento, canal, persona) para ver duplicados."""
    canal = ev.get("messaging_channel")
    if origen != "business_messaging":
        errores.append(f"{donde}: messaging_channel solo va con action_source=business_messaging")
    if canal not in CANALES:
        errores.append(f"{donde}: messaging_channel «{canal}» no válido ({', '.join(CANALES)})")
        return None
    if nombre and nombre not in EVENTOS_MENSAJERIA:
        errores.append(f"{donde}: Meta no admite «{nombre}» en mensajería (solo {', '.join(EVENTOS_MENSAJERIA[:3])}, "
                       f"…).{_sugerir_evento(nombre)}")
    if ev.get("event_source_url"):
        avisos.append(f"{donde}: event_source_url no se usa en mensajería: el evento ocurre en la conversación")
    if (ev.get("custom_data") or {}).get("event_source") == "crm":
        errores.append(f"{donde}: un evento de mensajería no lleva event_source=crm (eso es la CAPI de CRM con "
                       "system_generated)")
    cuenta, persona = IDENTIDAD[canal]
    if canal == "instagram" and not ud.get(cuenta) and ud.get("ig_account_id"):
        avisos.append(f"{donde}: la guía de mensajería de Meta pide instagram_business_account_id; ig_account_id es el "
                      "nombre de la lista general de parámetros. Si Meta lo rechaza, cámbialo")
        cuenta = "ig_account_id"
    for clave in (cuenta, persona, "page_id"):
        valor = ud.get(clave)
        if valor and clave != "ctwa_clid" and not es_hash(valor) and not _DIGITOS.fullmatch(str(valor)):
            errores.append(f"{donde}: user_data.{clave} tiene que ser el ID numérico tal cual (sin espacios ni hash)")
    if not ud.get(cuenta):
        errores.append(f"{donde}: en {canal} falta user_data.{cuenta} (" + {
            "whatsapp": "el ID de la cuenta de WhatsApp Business, WABA",
            "messenger": "el ID de la Página",
            "instagram": "el ID de la cuenta profesional de Instagram"}[canal] + ")")
    if canal == "whatsapp":
        clid = ud.get("ctwa_clid")
        if clid:
            if not isinstance(clid, str) or re.search(r"\s", clid) or len(clid) < 10:
                avisos.append(f"{donde}: ctwa_clid no parece el del webhook (cópialo entero, tal cual)")
            return (nombre, canal, str(clid))
        datos = [k for k in DATOS_SIN_CLIC if ud.get(k)]
        if not ud.get("page_id") or not datos:
            errores.append(f"{donde}: WhatsApp sin ctwa_clid necesita page_id y al menos un dato de cliente hasheado "
                           "(ph con el número de la conversación, em…). external_id no cuenta para emparejar aquí")
        else:
            avisos.append(f"{donde}: sin ctwa_clid Meta empareja por {', '.join(datos)}: la atribución al anuncio es "
                          "menos precisa (normal en anuncios de Estados de WhatsApp, que no traen clic)")
        return (nombre, canal, str(ud.get("ph") or ud.get("em")))
    if not ud.get(persona):
        errores.append(f"{donde}: en {canal} falta user_data.{persona} (" +
                       ("el PSID de quien escribe" if canal == "messenger" else "el IGSID de quien escribe") + ")")
    return (nombre, canal, str(ud.get(persona)))


def evento_mensajeria(canal: str, evento: str, momento: int, *, waba: str | None = None,
                      ctwa_clid: str | None = None, pagina: str | None = None, psid: str | None = None,
                      ig_cuenta: str | None = None, igsid: str | None = None, datos: dict | None = None,
                      prefijo: str | None = None, valor: float | None = None, moneda: str | None = None,
                      event_id: str | None = None, custom: dict | None = None) -> dict:
    """Un evento de la CAPI de mensajería con la identidad que pide Meta para cada canal.

    WhatsApp: WABA + ctwa_clid (vía documentada con clic) o, sin clic, page_id + WABA + datos hasheados (`datos`, en
    claro: se normalizan y hashean aquí). Messenger: page_id + PSID. Instagram: cuenta profesional + IGSID.
    """
    if canal not in CANALES:
        raise Invalido(f"canal «{canal}» no válido ({', '.join(CANALES)})")
    if evento not in EVENTOS_MENSAJERIA:
        raise Invalido(f"Meta no admite «{evento}» en mensajería.{_sugerir_evento(evento)}")
    ud: dict = {}
    if canal == "whatsapp":
        if not waba:
            raise Invalido("falta la WABA (--waba, meta.waba en la ficha o el webhook)")
        ud["whatsapp_business_account_id"] = str(waba)
        if ctwa_clid:
            ud["ctwa_clid"] = ctwa_clid.strip()
        else:
            claro = {k: v for k, v in (datos or {}).items() if k in DATOS_SIN_CLIC and v}
            if not pagina or not claro:
                raise Invalido("sin ctwa_clid hacen falta la Página (--pagina o meta.pagina) y un dato de cliente "
                               "(--telefono con el número de la conversación o --email)")
            ud = {"page_id": str(pagina), **ud, **hashear_user_data(claro, prefijo)}
    elif canal == "messenger":
        if not pagina or not psid:
            raise Invalido("Messenger necesita la Página (--pagina o meta.pagina) y el PSID de quien escribe (--psid)")
        ud = {"page_id": str(pagina), "page_scoped_user_id": str(psid)}
    else:
        if not ig_cuenta or not igsid:
            raise Invalido("Instagram necesita la cuenta profesional (--ig-cuenta o meta.instagram con el ID numérico) "
                           "y el IGSID de quien escribe (--igsid)")
        ud = {"instagram_business_account_id": str(ig_cuenta), "ig_sid": str(igsid)}
    ev: dict = {"event_name": evento, "event_time": int(momento), "action_source": "business_messaging",
                "messaging_channel": canal, "user_data": ud}
    if event_id:
        ev["event_id"] = event_id
    cd: dict = dict(custom or {})
    if valor is not None:
        cd["value"] = valor
    if moneda:
        cd["currency"] = moneda.upper()
    if evento == "Purchase" and ("value" not in cd or "currency" not in cd):
        raise Invalido("ganado = Purchase: pasa --valor (importe del proyecto) y --moneda (o --cliente con la moneda "
                       "de la ficha)")
    if cd:
        ev["custom_data"] = cd
    return ev


# ---------------------------------------------------------------- webhooks de mensajería (dónde viene el clic)

def _segundos(t) -> int | None:
    try:
        n = int(float(t))
    except (TypeError, ValueError):
        return None
    return n // 1000 if n > 10 ** 11 else n


def parsear_webhook(payload) -> list[dict]:
    """Mensajes entrantes de un webhook de WhatsApp Cloud API, Messenger o Instagram, con el origen del clic.

    Cada mensaje: canal, cuenta (WABA, Página o cuenta de Instagram), mensaje_id (wamid o mid: Meta reintenta los
    avisos, así que úsalo para no procesar dos veces), identidad (wa_id, BSUID, PSID o IGSID),
    telefono (solo WhatsApp con número), momento (segundos), anuncio, ctwa_clid, ref y avisos. Ignora los ecos de
    tus propios mensajes y los estados de entrega.
    """
    if not isinstance(payload, dict):
        raise Invalido("el webhook tiene que ser un objeto JSON (lo que Meta manda a tu URL)")
    objeto = payload.get("object")
    mensajes: list[dict] = []
    if objeto == "whatsapp_business_account":
        for entrada in payload.get("entry") or []:
            waba = str(entrada.get("id") or "")
            for cambio in entrada.get("changes") or []:
                valor = cambio.get("value") or {}
                contactos = valor.get("contacts") or []
                for m in valor.get("messages") or []:
                    tel = m.get("from") or ((contactos[0] if contactos else {}).get("wa_id"))
                    bsuid = m.get("from_user_id") or ((contactos[0] if contactos else {}).get("user_id"))
                    ref = m.get("referral") or {}
                    msg = {"canal": "whatsapp", "cuenta": waba, "mensaje_id": str(m.get("id") or ""),
                           "numero_negocio": str(
                        (valor.get("metadata") or {}).get("phone_number_id") or ""),
                        "identidad": str(tel or bsuid or ""), "tipo_identidad": "wa_id" if tel else "bsuid",
                        "telefono": str(tel) if tel else None, "momento": _segundos(m.get("timestamp")),
                        "anuncio": str(ref.get("source_id") or "") or None, "ctwa_clid": ref.get("ctwa_clid"),
                        "ref": None, "avisos": []}
                    if not ref:
                        msg["avisos"].append("sin referral: no viene de un anuncio (o no es el primer mensaje tras el "
                                             "clic, que es el único que lo trae)")
                    elif not msg["ctwa_clid"]:
                        msg["avisos"].append("referral sin ctwa_clid: anuncio de Estados de WhatsApp (Meta lo omite). "
                                             "Vía sin clic: page_id + teléfono hasheado")
                    if not tel:
                        msg["avisos"].append("la persona usa nombre de usuario y el webhook no trae su número: sin "
                                             "ctwa_clid no hay con qué emparejar")
                    mensajes.append(msg)
    elif objeto in ("page", "instagram"):
        canal = "messenger" if objeto == "page" else "instagram"
        for entrada in payload.get("entry") or []:
            cuenta = str(entrada.get("id") or "")
            for ev in entrada.get("messaging") or []:
                mensaje = ev.get("message") or {}
                if mensaje.get("is_echo"):
                    continue  # lo ha escrito el negocio
                ref = (mensaje.get("referral") or ev.get("referral") or (ev.get("postback") or {}).get("referral")
                       or {})
                if not mensaje and not ref and not ev.get("postback"):
                    continue  # lecturas, entregas, reacciones…
                persona = str((ev.get("sender") or {}).get("id") or "")
                msg = {"canal": canal, "cuenta": str((ev.get("recipient") or {}).get("id") or cuenta),
                       "mensaje_id": str(mensaje.get("mid") or ""), "numero_negocio": None, "identidad": persona,
                       "tipo_identidad": "psid" if canal == "messenger" else "igsid", "telefono": None,
                       "momento": _segundos(ev.get("timestamp")),
                       "anuncio": str(ref.get("ad_id") or "") or None if ref.get("source") == "ADS" else None,
                       "ctwa_clid": None, "ref": ref.get("ref"), "avisos": []}
                if ref.get("source") != "ADS":
                    msg["avisos"].append("sin referral de anuncio: conversación orgánica o mensaje posterior al primero")
                mensajes.append(msg)
    else:
        raise Invalido(f"no reconozco el webhook (object «{objeto}»): espero whatsapp_business_account, page o "
                       "instagram, tal como lo manda Meta")
    return mensajes


def _tapar(valor, visibles: int = 4) -> str:
    v = str(valor or "")
    if not v:
        return "—"
    return v[:visibles] + "…" if len(v) > visibles + 2 else "***"


def _tapar_telefono(valor) -> str:
    v = str(valor or "")
    return f"***{v[-2:]}" if len(v) > 4 else ("—" if not v else "***")


def _cuenta_de_ficha(meta: dict, clave: str) -> str | None:
    v = str(meta.get(clave) or "").strip()
    return v if _DIGITOS.fullmatch(v) and not re.fullmatch(r"0+", v) else None


def construir_mensajeria(a: argparse.Namespace) -> tuple[dict, list[str]]:
    """`construir --canal/--desde-webhook`: el evento y avisos propios (ventana de clic, vía sin clic)."""
    for opcion, valor in (("--url", a.url), ("--ip", a.ip), ("--ua", a.ua), ("--fbc", a.fbc), ("--fbclid", a.fbclid),
                          ("--fbp", a.fbp), ("--lead-id", a.lead_id), ("--crm", a.crm), ("--external-id", a.external_id)):
        if valor:
            raise Invalido(f"{opcion} no va en un evento de mensajería (la identidad es la de la conversación)")
    if a.origen and a.origen != "business_messaging":
        raise Invalido("con --canal el origen es business_messaging: quita --origen")
    meta: dict = {}
    moneda_ficha = None
    if a.cliente:
        try:
            ficha = comun.leer_ficha(a.cliente)
        except comun.FichaInvalida as e:
            _salir(str(e), 2)
        meta = ficha.get("meta") or {}
        moneda_ficha = ficha.get("moneda")
    avisos: list[str] = []
    msg: dict = {}
    if a.desde_webhook:
        mensajes = parsear_webhook(_leer_json(a.desde_webhook))
        if not mensajes:
            raise Invalido("el webhook no trae ningún mensaje entrante (¿es un estado de entrega o un eco?)")
        msg = next((m for m in mensajes if m["anuncio"]), mensajes[0])
        avisos += [f"webhook: {x}" for x in msg["avisos"]]
    canal = a.canal or msg.get("canal")
    if msg and a.canal and a.canal != msg["canal"]:
        raise Invalido(f"--canal {a.canal} pero el webhook es de {msg['canal']}")
    if not a.evento and not a.etapa:
        raise Invalido("di la etapa (--etapa cualificado) o el evento (--evento QualifiedLead)")
    evento = a.evento or evento_de_etapa(a.etapa, a.cualifica_en)
    de_web = msg.get("cuenta") or None
    waba = a.waba or (de_web if canal == "whatsapp" else None) or _cuenta_de_ficha(meta, "waba")
    pagina = a.pagina or (de_web if canal == "messenger" else None) or _cuenta_de_ficha(meta, "pagina")
    ig_cuenta = a.ig_cuenta or (de_web if canal == "instagram" else None) or _cuenta_de_ficha(meta, "instagram")
    clid = a.ctwa_clid or msg.get("ctwa_clid")
    datos: dict = {}
    if a.email:
        datos["em"] = a.email
    telefonos = list(a.telefono or [])
    if canal == "whatsapp" and not clid and msg.get("telefono") and not telefonos:
        telefonos = ["+" + msg["telefono"].lstrip("+")]  # wa_id ya lleva el prefijo de país
    if telefonos:
        datos["ph"] = telefonos
    for clave, valor in (("fn", a.nombre), ("ln", a.apellido), ("ct", a.ciudad), ("st", a.provincia), ("zp", a.cp),
                         ("country", a.pais), ("db", a.nacimiento), ("ge", a.genero)):
        if valor:
            datos[clave] = valor
    if clid and datos:
        avisos.append("con ctwa_clid uso la vía documentada (WABA + clic): los datos de cliente no se envían")
    custom: dict = {}
    for par in a.custom or []:
        k, sep, v = par.partition("=")
        if not sep or not k:
            raise Invalido(f"--custom como clave=valor: {par!r}")
        custom[k] = v
    momento = _momento(a.momento)
    ev = evento_mensajeria(canal, evento, momento, waba=waba, ctwa_clid=clid, pagina=pagina,
                           psid=a.psid or (msg.get("identidad") if canal == "messenger" else None),
                           ig_cuenta=ig_cuenta, igsid=a.igsid or (msg.get("identidad") if canal == "instagram" else None),
                           datos=datos, prefijo=a.prefijo, valor=a.valor, moneda=a.moneda or (
                               moneda_ficha if evento == "Purchase" else None),
                           event_id=a.event_id, custom=custom)
    entrada = msg.get("momento") or (_momento(a.entrada_conversacion) if a.entrada_conversacion else None)
    if entrada and momento - entrada > VENTANA_CLIC_DIAS * 86400:
        avisos.append(f"han pasado más de {VENTANA_CLIC_DIAS} días desde que entró la conversación: Meta recibe el "
                      "evento pero no lo atribuirá al clic del anuncio (sirve para tus informes, no para optimizar)")
    return ev, avisos


# ---------------------------------------------------------------- construir

def _momento(texto: str | None) -> int:
    if not texto:
        return int(time.time())
    if re.fullmatch(r"\d{9,10}", texto):
        return int(texto)
    try:
        dt = datetime.fromisoformat(texto)
    except ValueError:
        raise Invalido("--momento como AAAA-MM-DDTHH:MM[:SS][+zona] o segundos Unix") from None
    if not dt.tzinfo:
        dt = dt.astimezone()  # hora local del equipo
    return int(dt.timestamp())


def construir_evento(a: argparse.Namespace) -> dict:
    origen = "system_generated" if a.crm else (a.origen or "website")
    if origen == "business_messaging":
        raise Invalido("para mensajería usa --canal whatsapp|messenger|instagram (pone la identidad que pide Meta)")
    ud: dict = {}
    for clave, valores in (("em", a.email), ("ph", a.telefono)):
        if valores:
            ud[clave] = valores
    for clave, valor in (("fn", a.nombre), ("ln", a.apellido), ("ct", a.ciudad), ("st", a.provincia),
                         ("zp", a.cp), ("country", a.pais), ("db", a.nacimiento), ("ge", a.genero),
                         ("external_id", a.external_id)):
        if valor:
            ud[clave] = valor
    ud = hashear_user_data(ud, a.prefijo)
    for clave, valor in (("client_ip_address", a.ip), ("client_user_agent", a.ua), ("fbp", a.fbp),
                         ("lead_id", a.lead_id)):
        if valor:
            ud[clave] = valor
    if a.fbc:
        ud["fbc"] = a.fbc
    elif a.fbclid:
        ud["fbc"] = fbc_desde_fbclid(a.fbclid)
    ev: dict = {"event_name": a.evento, "event_time": _momento(a.momento), "action_source": origen,
                "user_data": ud}
    if a.lead_id and re.fullmatch(r"\d+", a.lead_id):
        ud["lead_id"] = int(a.lead_id)
    if a.event_id:
        ev["event_id"] = a.event_id
    # Sin --event-id no se inventa uno: no coincidiría con el del píxel (no deduplica) y taparía el aviso de validar.
    if a.url:
        ev["event_source_url"] = a.url
    cd: dict = {}
    if a.valor is not None:
        cd["value"] = a.valor
    if a.moneda:
        cd["currency"] = a.moneda.upper()
    if a.crm:
        cd["event_source"] = "crm"
        cd["lead_event_source"] = a.crm
    for par in a.custom or []:
        k, sep, v = par.partition("=")
        if not sep or not k:
            raise Invalido(f"--custom como clave=valor: {par!r}")
        cd[k] = v
    if cd:
        ev["custom_data"] = cd
    return ev


def construir_desde_entrada(payload, prefijo: str | None) -> dict:
    eventos = []
    for ev in _como_lista(payload):
        if not isinstance(ev, dict):
            raise Invalido("cada evento tiene que ser un objeto JSON")
        nuevo = dict(ev)
        ud = dict(ev.get("user_data") or {})
        if ud.get("fbclid") and not ud.get("fbc"):
            ud["fbc"] = fbc_desde_fbclid(ud.pop("fbclid"))
        ud.pop("fbclid", None)
        nuevo["user_data"] = hashear_user_data(ud, prefijo)
        if isinstance(nuevo.get("event_time"), str):
            nuevo["event_time"] = _momento(nuevo["event_time"])
        eventos.append(nuevo)
    return {"data": eventos}


# ---------------------------------------------------------------- enviar

def _leer_json(ruta: str):
    try:
        return json.loads(pathlib.Path(ruta).expanduser().read_text(encoding="utf-8"))
    except FileNotFoundError:
        _salir(f"No existe {ruta}.", 1)
    except json.JSONDecodeError as e:
        _salir(f"{ruta} no es JSON válido: {e}", 1)


def _dataset(slug: str, forzado: str | None, mensajeria: bool = False) -> str:
    if forzado:
        ds = forzado
    else:
        try:
            meta = comun.leer_ficha(slug).get("meta") or {}
        except comun.FichaInvalida as e:
            _salir(str(e), 2)
        ds = str((meta.get("dataset_mensajeria") if mensajeria else "") or meta.get("dataset") or "")
    if not re.fullmatch(r"\d{6,20}", ds) or re.fullmatch(r"0+", ds):
        donde = "meta.dataset_mensajeria o meta.dataset" if mensajeria else "meta.dataset"
        _salir(f"El dataset de {slug} no está en la ficha ({donde}) o es el de ejemplo. Sácalo de Events Manager.", 2)
    return ds


def enviar_eventos(payload: dict, dataset: str, token: str, test_code: str | None, timeout: int = 30) -> dict:
    version = os.environ.get("META_API_VERSION") or VERSION
    cuerpo = {"data": json.dumps(payload["data"], ensure_ascii=False), "access_token": token}
    if test_code:
        cuerpo["test_event_code"] = test_code
    peticion = urllib.request.Request(f"{GRAPH}/{version}/{dataset}/events",
                                      data=urllib.parse.urlencode(cuerpo).encode(), method="POST",
                                      headers={"Content-Type": "application/x-www-form-urlencoded",
                                               "User-Agent": "meta-ads-os/1.0"})
    # Sin reintentos automáticos: un reintento sin el mismo event_id duplicaría eventos.
    try:
        with urllib.request.urlopen(peticion, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
        except ValueError:
            err = {"message": f"HTTP {e.code}"}
        detalle = " · ".join(x for x in (err.get("error_user_title"), err.get("error_user_msg")) if x)
        raise RuntimeError(f"Meta rechazó el envío ({err.get('code')}/{err.get('error_subcode')}): "
                           f"{err.get('message')}" + (f" — {detalle}" if detalle else "")) from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"No se pudo conectar con Meta: {e.reason}") from None


# ---------------------------------------------------------------- CLI

def _imprimir(datos, como_json: bool) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2) if como_json or isinstance(datos, (dict, list)) else datos)


def cmd_hashear(a: argparse.Namespace) -> None:
    if a.archivo:
        if a.valor:
            _salir("O un valor o --archivo, no los dos.", 1)
        return cmd_hashear_archivo(a)
    if not a.valor or not a.tipo:
        _salir("Di qué hashear: un valor con --tipo (em, ph...) o --archivo <csv>.", 1)
    try:
        norm = str(a.valor).lower() if es_hash(a.valor) else normalizar(a.tipo, a.valor, a.prefijo)
    except Invalido as e:
        _salir(f"No se puede normalizar: {e}", 1)
    h = norm if es_hash(a.valor) else sha256(norm)
    if a.json:
        _imprimir({"tipo": a.tipo, "normalizado": norm, "sha256": h}, True)
    else:
        print(f"normalizado: {norm}\nsha256:      {h}")


# ---------------------------------------------------------------- listas de clientes (públicos personalizados)

# Columna del CSV (normalizada) → tipo. «estado» y «name» no entran: suelen ser el estado del lead y el nombre completo.
ALIAS_COLUMNAS = {
    "em": ("email", "e mail", "correo", "correo electronico", "mail", "em"),
    "ph": ("telefono", "telefono movil", "movil", "celular", "whatsapp", "tel", "phone", "phone number", "mobile", "ph"),
    "fn": ("nombre", "first name", "firstname", "fn"),
    "ln": ("apellido", "apellidos", "last name", "lastname", "surname", "ln"),
    "ct": ("ciudad", "localidad", "municipio", "city", "ct"),
    "st": ("provincia", "region", "state", "st"),
    "zp": ("cp", "codigo postal", "zip", "zip code", "postal code", "postcode", "zp"),
    "country": ("pais", "codigo pais", "country", "country code"),
    "ge": ("genero", "sexo", "gender", "gen", "ge"),
    "db": ("fecha nacimiento", "fecha de nacimiento", "nacimiento", "birthday", "date of birth", "dob", "db"),
    "external_id": ("external id", "extern id", "id externo", "id cliente", "customer id", "contact id"),
}
# Tipo → columnas de salida (cabeceras de la plantilla de listas de clientes de Meta).
SALIDA_LISTA = {"em": ("email",), "ph": ("phone",), "fn": ("fn",), "ln": ("ln",), "ct": ("ct",), "st": ("st",),
                "zp": ("zip",), "country": ("country",), "ge": ("gen",), "db": ("doby", "dobm", "dobd"),
                "external_id": ("extern_id",)}


def _cabecera_normal(texto: str) -> str:
    t = "".join(c for c in unicodedata.normalize("NFKD", str(texto)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def _latino(valor: str) -> str:
    """Sin tildes ni eñes: para públicos Meta pide a-z en ciudad y provincia y lo recomienda en nombre y apellido."""
    return "".join(c for c in unicodedata.normalize("NFKD", valor) if not unicodedata.combining(c) and c.isalnum())


def hashear_para_lista(tipo: str, valor, prefijo: str | None = None) -> tuple[str, ...]:
    """Valor de una celda → hashes de sus columnas de salida (db da año, mes y día). Ya hasheado: tal cual."""
    if es_hash(valor):
        if tipo == "db":
            raise Invalido("fecha de nacimiento ya hasheada: Meta la pide en año, mes y día por separado")
        return (str(valor).lower(),)
    v = normalizar(tipo, valor, prefijo)
    if tipo in ("fn", "ln", "ct", "st"):
        v = _latino(v)
        if not v:
            raise Invalido(f"{tipo} vacío tras normalizar")
    if tipo == "db":
        return sha256(v[:4]), sha256(v[4:6]), sha256(v[6:])
    return (sha256(v),)


def _ruta(texto: str) -> pathlib.Path:
    r = pathlib.Path(texto).expanduser()
    return (r if r.is_absolute() else comun.RAIZ / r).resolve()


def _en_privado(ruta: pathlib.Path) -> bool:
    """¿Está dentro de clientes/<slug>/privado/?"""
    try:
        partes = ruta.resolve().relative_to(comun.CLIENTES.resolve()).parts
    except ValueError:
        return False
    return len(partes) >= 3 and partes[1] == "privado"


def _rel(ruta: pathlib.Path) -> str:
    try:
        return str(ruta.relative_to(comun.RAIZ.resolve()))
    except ValueError:
        return ruta.name


def _leer_tabla(ruta: pathlib.Path) -> tuple[list[str], list[list[str]]]:
    for codificacion in ("utf-8-sig", "cp1252", "latin-1"):  # Excel en español suele guardar en cp1252
        try:
            texto = ruta.read_text(encoding=codificacion)
            break
        except UnicodeDecodeError:
            continue
    muestra = texto[:20000]
    try:
        dialecto = csv.Sniffer().sniff(muestra, delimiters=",;\t|")
    except csv.Error:
        dialecto = csv.excel
    filas = list(csv.reader(texto.splitlines(), dialecto))
    if not filas:
        raise Invalido("el archivo está vacío")
    return filas[0], filas[1:]


def _columnas_pedidas(cabeceras: list[str], pedidas: str | None) -> list[tuple[int, str, str]]:
    """[(índice, cabecera, tipo)]. Sin --columnas, todas las que se reconocen por el nombre."""
    normal = {_cabecera_normal(h): i for i, h in enumerate(cabeceras)}
    por_alias = {alias: tipo for tipo, nombres in ALIAS_COLUMNAS.items() for alias in nombres}
    salida = []
    if not pedidas:
        for i, h in enumerate(cabeceras):
            if _cabecera_normal(h) in por_alias:
                salida.append((i, h, por_alias[_cabecera_normal(h)]))
        if not salida:
            raise Invalido("no reconozco ninguna columna de datos de cliente: indícalas con --columnas "
                           "(p. ej. --columnas correo=em,movil=ph)")
        return salida
    for trozo in (x.strip() for x in pedidas.split(",") if x.strip()):
        nombre, _, tipo = trozo.replace(":", "=", 1).partition("=")
        clave = _cabecera_normal(nombre)
        if clave not in normal:
            raise Invalido(f"no hay ninguna columna «{nombre.strip()}» (columnas: {', '.join(cabeceras)})")
        tipo = tipo.strip().lower() or por_alias.get(clave, "")
        if tipo not in SALIDA_LISTA:
            raise Invalido(f"no sé qué dato es «{nombre.strip()}»: escríbelo como {nombre.strip()}=<tipo> con un tipo "
                           f"de {', '.join(SALIDA_LISTA)}")
        salida.append((normal[clave], cabeceras[normal[clave]], tipo))
    return salida


def hashear_archivo(entrada: pathlib.Path, salida: pathlib.Path, columnas: str | None, prefijo: str | None,
                    conservar: str | None) -> dict:
    """Lee un CSV con datos en claro y escribe otro solo con hashes (y las columnas de --conservar)."""
    cabeceras, filas = _leer_tabla(entrada)
    elegidas = _columnas_pedidas(cabeceras, columnas)
    normal = {_cabecera_normal(h): i for i, h in enumerate(cabeceras)}
    por_alias = {alias for nombres in ALIAS_COLUMNAS.values() for alias in nombres}
    extra = []
    for nombre in (x.strip() for x in (conservar or "").split(",") if x.strip()):
        clave = _cabecera_normal(nombre)
        if clave not in normal:
            raise Invalido(f"no hay ninguna columna «{nombre}» para conservar")
        if clave in por_alias or normal[clave] in {i for i, _, _ in elegidas}:
            raise Invalido(f"«{nombre}» es un dato de cliente: no se copia en claro (hashéalo con --columnas)")
        extra.append((normal[clave], cabeceras[normal[clave]]))
    stats = [{"columna": h, "tipo": tipo, "salida": list(SALIDA_LISTA[tipo]), "validos": 0, "vacios": 0,
              "invalidos": 0, "ya_hasheados": 0} for _, h, tipo in elegidas]
    vistas: set = set()
    escritas: list[list[str]] = []
    sin_identificadores = duplicadas = 0
    for fila in filas:
        if not any(c.strip() for c in fila):
            continue
        hashes: list[str] = []
        alguno = False
        for (i, _, tipo), st in zip(elegidas, stats):
            celda = fila[i].strip() if i < len(fila) else ""
            ancho = len(SALIDA_LISTA[tipo])
            if not celda:
                st["vacios"] += 1
                hashes += [""] * ancho
                continue
            try:
                hashes += list(hashear_para_lista(tipo, celda, prefijo))
                st["ya_hasheados" if es_hash(celda) else "validos"] += 1
                alguno = True
            except Invalido:
                st["invalidos"] += 1
                hashes += [""] * ancho
        if not alguno:
            sin_identificadores += 1
            continue
        valores_extra = [fila[i].strip() if i < len(fila) else "" for i, _ in extra]
        if any(_EMAIL.search(v) for v in valores_extra):
            raise Invalido("una columna de --conservar trae emails: no se copia en claro")
        clave = tuple(hashes + valores_extra)
        if clave in vistas:
            duplicadas += 1
            continue
        vistas.add(clave)
        escritas.append(hashes + valores_extra)
    if not escritas:
        raise Invalido("ninguna fila tiene un dato válido: no se ha escrito nada")
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([c for _, _, tipo in elegidas for c in SALIDA_LISTA[tipo]] + [h for _, h in extra])
        w.writerows(escritas)
    avisos = []
    telefonos = [s for s in stats if s["tipo"] == "ph"]
    if telefonos and not prefijo and any(s["invalidos"] for s in telefonos):
        avisos.append("hay teléfonos sin prefijo de país que se han quedado fuera: repite con --prefijo 34 (o el tuyo)")
    for s in stats:
        total = s["validos"] + s["invalidos"] + s["ya_hasheados"]
        if total and s["invalidos"] / total > 0.2:
            avisos.append(f"«{s['columna']}»: {s['invalidos']} de {total} valores no se han podido normalizar")
    return {"entrada": _rel(entrada), "salida": _rel(salida), "filas": sum(1 for f in filas if any(c.strip() for c in f)),
            "escritas": len(escritas), "sin_identificadores": sin_identificadores, "duplicadas": duplicadas,
            "columnas": stats, "conservadas": [h for _, h in extra], "avisos": avisos}


def cmd_hashear_archivo(a: argparse.Namespace) -> None:
    entrada = _ruta(a.archivo)
    if not entrada.is_file():
        _salir(f"No existe {a.archivo}.", 1)
    if not _en_privado(entrada):
        print("Aviso: el archivo de entrada tiene datos personales y está fuera de clientes/<slug>/privado/. "
              "Muévelo ahí (privado/ no se versiona ni se comparte).", file=sys.stderr)
    if a.salida:
        salida = _ruta(a.salida)
    elif _en_privado(entrada):
        salida = entrada.with_name(f"{entrada.stem}-hash.csv")
    else:
        _salir("Di dónde guardarlo con --salida clientes/<slug>/privado/<nombre>-hash.csv.", 1)
    if not _en_privado(salida):
        _salir("La salida tiene que ir en clientes/<slug>/privado/: los hashes siguen siendo datos personales.", 1)
    if salida == entrada:
        _salir("La salida no puede ser el mismo archivo que la entrada.", 1)
    if salida.exists() and not a.sobrescribir:
        _salir(f"Ya existe {_rel(salida)}: elige otro --salida o añade --sobrescribir.", 1)
    try:
        r = hashear_archivo(entrada, salida, a.columnas, a.prefijo, a.conservar)
    except Invalido as e:
        _salir(f"No se puede hashear el archivo: {e}", 1)
    if a.json:
        return _imprimir(r, True)
    print(f"{r['escritas']} filas hasheadas de {r['filas']} → {r['salida']}"
          f" ({r['sin_identificadores']} sin ningún dato válido, {r['duplicadas']} repetidas)")
    for s in r["columnas"]:
        print(f"  {s['columna'][:28]:<30}→ {', '.join(s['salida']):<18} válidos {s['validos']} · ya hasheados "
              f"{s['ya_hasheados']} · vacíos {s['vacios']} · no válidos {s['invalidos']}")
    for aviso in r["avisos"]:
        print(f"Aviso: {aviso}")
    print("Súbelo en Públicos → Crear público → Lista de clientes, o pásalo a /audiencias. No lo saques de privado/.")


def cmd_construir(a: argparse.Namespace) -> None:
    propios: list[str] = []
    try:
        if a.entrada:
            payload = construir_desde_entrada(_leer_json(a.entrada), a.prefijo)
        elif a.canal or a.desde_webhook:
            ev, propios = construir_mensajeria(a)
            payload = {"data": [ev]}
        else:
            if a.etapa:
                canonico = EVENTO_ETAPA[a.etapa]
                if a.evento and a.evento != canonico:
                    _salir(f"--etapa {a.etapa} se envía como «{canonico}» (contrato §16), no como «{a.evento}»: "
                           "quita --evento o usa ese nombre.", 1)
                a.evento = canonico
                if a.etapa in ETAPAS_SOLO_CRM and not a.crm:
                    propios.append(f"«{a.etapa}» suele salir del CRM: con --crm <CRM> (GHL, HubSpot…) va como "
                                   "evento de Conversion Leads (system_generated, event_source=crm)")
            if not a.evento:
                _salir("Di qué evento: --etapa cualificado (contrato §16), --evento Lead o --entrada archivo.json.", 1)
            payload = {"data": [construir_evento(a)]}
    except Invalido as e:
        _salir(f"No se puede construir: {e}", 1)
    errores, avisos = validar(payload)
    avisos = propios + avisos
    mensajeria = any(ev.get("action_source") == "business_messaging" for ev in payload["data"])
    if mensajeria and a.salida and not _en_privado(_ruta(a.salida)):
        avisos.append("el payload lleva el identificador de la conversación (ctwa_clid, PSID o IGSID): guárdalo en "
                      "clientes/<slug>/privado/")
    texto = json.dumps(payload, ensure_ascii=False, indent=2)
    if a.salida:
        destino = pathlib.Path(a.salida).expanduser()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto + "\n", encoding="utf-8")
        print(f"Payload con {len(payload['data'])} evento(s) en {a.salida} (datos de cliente ya hasheados).")
    else:
        print(texto)
    for x in avisos:
        print(f"aviso: {x}", file=sys.stderr)
    if errores:
        _salir("Errores:\n  - " + "\n  - ".join(errores), 1)


def cmd_validar(a: argparse.Namespace) -> None:
    errores, avisos = validar(_leer_json(a.payload))
    if a.json:
        _imprimir({"ok": not errores, "errores": errores, "avisos": avisos}, True)
    else:
        for x in errores:
            print(f"✗ {x}")
        for x in avisos:
            print(f"⚠ {x}")
        print("Válido." if not errores else f"{len(errores)} error(es): Meta rechazaría el lote.")
    sys.exit(1 if errores else 0)


def cmd_enviar(a: argparse.Namespace) -> None:
    if a.test_code and a.real:
        _salir("--test-code y --real se excluyen: o es una prueba o es real.", 1)
    if not a.test_code and not (a.real and a.confirmo):
        _salir("No se ha enviado nada. Sin --test-code, un evento real entra en el dataset del cliente y en su "
               "optimización.\n  Prueba: --test-code <código de Events Manager → Probar eventos>\n"
               "  Real (solo con el sí del usuario en este momento): --real --confirmo", 1)
    payload = _leer_json(a.payload)
    if isinstance(payload, dict) and payload.get("test_event_code") and payload["test_event_code"] != a.test_code:
        _salir("El payload trae test_event_code: pásalo con --test-code (el mismo) para que quede claro que es una prueba.", 1)
    payload = {"data": _como_lista(payload)}
    errores, avisos = validar(payload)
    for x in avisos:
        print(f"⚠ {x}", file=sys.stderr)
    if errores:
        _salir("No se ha enviado nada. Errores:\n  - " + "\n  - ".join(errores), 1)
    de_mensajeria = [ev.get("action_source") == "business_messaging" for ev in payload["data"]]
    mensajeria = all(de_mensajeria)
    if any(de_mensajeria) and not mensajeria:
        _salir("No se ha enviado nada: el lote mezcla mensajería con eventos web o de CRM. Mándalos por separado.", 1)
    dataset = _dataset(a.cliente, a.dataset, mensajeria)
    sufijo = a.cliente.upper().replace("-", "_")
    token = comun.credencial("META_CAPI_MENSAJERIA_TOKEN", a.cliente) if mensajeria else None
    if mensajeria and not token:
        token = comun.credencial("META_CAPI_TOKEN", a.cliente)
        if token:
            print("⚠ Sin META_CAPI_MENSAJERIA_TOKEN: pruebo con META_CAPI_TOKEN. Si Meta responde con un error de "
                  "permisos, crea un token con whatsapp_business_manage_events, page_events o instagram_manage_events "
                  "(docs/guias/mensajeria.md §2).", file=sys.stderr)
    elif not mensajeria:
        token = comun.credencial("META_CAPI_TOKEN", a.cliente)
    if not token:
        if mensajeria:
            _salir(f"Falta META_CAPI_MENSAJERIA_TOKEN (o META_CAPI_MENSAJERIA_TOKEN_{sufijo}) en .env: un token del "
                   "usuario del sistema con permiso de eventos del canal (docs/guias/mensajeria.md §2).", 2)
        _salir(f"Falta META_CAPI_TOKEN (o META_CAPI_TOKEN_{sufijo}) en .env. "
               "Events Manager → tu dataset → Configuración → Conversions API → Generar token.", 2)
    try:
        r = enviar_eventos(payload, dataset, token, a.test_code)
    except RuntimeError as e:
        _salir(str(e), 1)
    nombres: dict[str, int] = {}
    for ev in payload["data"]:
        nombres[ev["event_name"]] = nombres.get(ev["event_name"], 0) + 1
    resumen = ", ".join(f"{n}×{k}" for k, n in nombres.items())
    canales = sorted({ev.get("messaging_channel") for ev in payload["data"] if ev.get("messaging_channel")})
    comun.registrar_cambio("capi", "cli", "enviar_prueba" if a.test_code else "enviar_real", dataset, a.cliente,
                           f"{resumen}; "
                           + (f"mensajeria={','.join(canales)}; " if canales else "")
                           + f"recibidos={r.get('events_received')}; "
                           + (f"test_event_code={a.test_code}; " if a.test_code else "")
                           + f"fbtrace_id={r.get('fbtrace_id', '')}")
    if a.json:
        _imprimir({"modo": "prueba" if a.test_code else "real", "dataset": dataset,
                   **({"mensajeria": canales} if canales else {}), **r}, True)
        return
    print(f"{'PRUEBA' if a.test_code else 'REAL'} · dataset {dataset} · enviados {resumen}"
          + (f" ({', '.join(canales)})" if canales else "")
          + f" · recibidos por Meta: {r.get('events_received')} · fbtrace_id {r.get('fbtrace_id', '—')}")
    for m in r.get("messages") or []:
        print(f"  Meta: {m}")
    if a.test_code:
        print("Míralo en Events Manager → Probar eventos (tarda segundos). Meta no lo descarta: usa siempre datos de "
              "prueba propios, nunca de leads reales.")
        if canales:
            print("Mensajería: si no aparece en Probar eventos, mira el resumen del dataset (no está verificado que esa "
                  "pantalla muestre los eventos de business_messaging). El clic tiene que ser tuyo, nunca el de un lead.")


def cmd_origen(a: argparse.Namespace) -> None:
    try:
        mensajes = parsear_webhook(_leer_json(a.webhook))
    except Invalido as e:
        _salir(f"No se puede leer: {e}", 1)
    if not mensajes:
        _salir("El webhook no trae mensajes entrantes (¿estados de entrega, lecturas o ecos de tus mensajes?).", 1)
    if a.salida:
        destino = _ruta(a.salida)
        if not _en_privado(destino):
            _salir("La salida tiene que ir en clientes/<slug>/privado/: lleva teléfonos e identificadores de personas.", 1)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(mensajes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tapados = [{**m, "identidad": _tapar_telefono(m["identidad"]) if m["tipo_identidad"] == "wa_id"
                else _tapar(m["identidad"]), "telefono": _tapar_telefono(m["telefono"]) if m["telefono"] else None,
                "ctwa_clid": _tapar(m["ctwa_clid"], 6) if m["ctwa_clid"] else None,
                "momento": datetime.fromtimestamp(m["momento"], timezone.utc).isoformat(timespec="seconds")
                if m["momento"] else None} for m in mensajes]
    if a.json:
        _imprimir({"mensajes": tapados, "de_anuncio": sum(1 for m in mensajes if m["anuncio"]),
                   "con_clic": sum(1 for m in mensajes if m["ctwa_clid"])}, True)
    else:
        for m in tapados:
            print(f"{m['canal']:<9} cuenta {m['cuenta'] or '—'} · {m['tipo_identidad']} {m['identidad']} · "
                  f"anuncio {m['anuncio'] or '—'} · ctwa_clid {m['ctwa_clid'] or '—'} · {m['momento'] or 'sin hora'}")
            for x in m["avisos"]:
                print(f"  ⚠ {x}")
        con = sum(1 for m in mensajes if m["anuncio"])
        print(f"{len(mensajes)} mensaje(s) entrante(s), {con} con el anuncio de origen."
              + (f" Completo (sin tapar) en {_rel(_ruta(a.salida))}." if a.salida else ""))


def _consola_segura() -> None:
    """✓, ⚠ y → no existen en cp1252 (Git Bash en Windows con la salida redirigida): salen como «?»."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            try:
                flujo.reconfigure(errors="replace")
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> None:
    _consola_segura()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)

    h = sub.add_parser("hashear", help="normaliza y hashea un dato de cliente o una lista entera (--archivo)")
    h.add_argument("valor", nargs="?", help="un dato suelto (con --tipo)")
    h.add_argument("--tipo", choices=HASHEAR, help="clave de user_data del dato suelto")
    h.add_argument("--prefijo", help="prefijo de país para teléfonos sin + (34, 52, 57...)")
    h.add_argument("--archivo", help="CSV con datos en claro dentro de clientes/<slug>/privado/")
    h.add_argument("--columnas", help="columnas a hashear: email,telefono o correo=em,movil=ph (por defecto, las "
                                      "que se reconocen por el nombre)")
    h.add_argument("--salida", help="CSV de salida en privado/ (por defecto <archivo>-hash.csv)")
    h.add_argument("--conservar", help="columnas sin datos personales que se copian tal cual (p. ej. valor)")
    h.add_argument("--sobrescribir", action="store_true", help="reemplaza la salida si ya existe")
    h.add_argument("--json", action="store_true")

    c = sub.add_parser("construir", help="construye un evento con los datos de cliente hasheados")
    c.add_argument("--entrada", help="JSON con eventos en la forma de Meta y datos en claro")
    c.add_argument("--evento", help="Lead, Schedule, Purchase, StartTrial, Subscribe…; para una etapa del CRM, mejor "
                                    "--etapa (el nombre exacto del contrato §16); en mensajería, LeadSubmitted, "
                                    "QualifiedLead, Purchase…")
    c.add_argument("--origen", choices=ORIGENES, help="action_source (por defecto website)")
    m = c.add_argument_group("mensajería (Click to WhatsApp, Messenger, Instagram Direct)")
    m.add_argument("--canal", choices=CANALES, help="evento de la CAPI de mensajería (action_source=business_messaging)")
    c.add_argument("--etapa", choices=ETAPAS + ETAPAS_TALLER,
                   help="etapa del contrato §16: pone el event_name canónico (cualificado → LeadCualificado…); en "
                        "mensajería, lead, cualificado y ganado tienen evento")
    m.add_argument("--cualifica-en", default="cualificado", choices=CUALIFICA_EN,
                   help="etapa que se manda como QualifiedLead (por defecto cualificado; una sola por cliente)")
    m.add_argument("--desde-webhook", help="webhook de Meta (en privado/) del que sacar canal, cuenta, clic y persona")
    m.add_argument("--cliente", help="slug: WABA, Página, cuenta de Instagram y moneda de la ficha")
    m.add_argument("--waba", help="ID de la cuenta de WhatsApp Business (WhatsApp)")
    m.add_argument("--ctwa-clid", help="ID del clic del anuncio (referral.ctwa_clid del primer mensaje)")
    m.add_argument("--pagina", help="ID de la Página (Messenger, o WhatsApp sin ctwa_clid)")
    m.add_argument("--psid", help="ID de la persona en la Página (Messenger)")
    m.add_argument("--ig-cuenta", help="ID de la cuenta profesional de Instagram")
    m.add_argument("--igsid", help="ID de la persona en Instagram")
    m.add_argument("--entrada-conversacion", help="cuándo entró la conversación (avisa si el evento cae fuera de la "
                                                  "ventana de 7 días del clic)")
    c.add_argument("--crm", help="nombre del CRM (GHL, HubSpot...): evento de etapa para Conversion Leads")
    c.add_argument("--momento", help="cuándo ocurrió (ISO 8601 o segundos Unix); por defecto ahora")
    c.add_argument("--event-id", help="el mismo que manda el píxel, para deduplicar")
    c.add_argument("--url", help="event_source_url (obligatoria en website)")
    c.add_argument("--email", action="append", help="email en claro (repetible); se normaliza y hashea")
    c.add_argument("--telefono", action="append", help="teléfono en claro (repetible); con --prefijo si no lleva +")
    c.add_argument("--prefijo", help="prefijo de país para teléfonos sin +")
    c.add_argument("--nombre", help="nombre de pila (fn)")
    c.add_argument("--apellido", help="primer apellido (ln)")
    c.add_argument("--ciudad", help="ct")
    c.add_argument("--provincia", help="st")
    c.add_argument("--cp", help="código postal (zp)")
    c.add_argument("--pais", help="código ISO de 2 letras")
    c.add_argument("--nacimiento", help="AAAA-MM-DD")
    c.add_argument("--genero", help="f o m")
    c.add_argument("--external-id", help="ID del contacto en tu CRM (se hashea)")
    c.add_argument("--ip", help="IP del navegador del usuario (en claro)")
    c.add_argument("--ua", help="user agent del navegador del usuario")
    c.add_argument("--fbc", help="cookie _fbc (en claro)")
    c.add_argument("--fbclid", help="construye fbc si no tienes la cookie")
    c.add_argument("--fbp", help="cookie _fbp (en claro)")
    c.add_argument("--lead-id", help="ID del lead del formulario instantáneo (Conversion Leads)")
    c.add_argument("--valor", type=float, help="value (con --moneda)")
    c.add_argument("--moneda", help="currency en ISO 4217 (EUR, USD...)")
    c.add_argument("--custom", action="append", help="clave=valor en custom_data (repetible)")
    c.add_argument("--salida", help="archivo donde guardar el payload")

    v = sub.add_parser("validar", help="comprueba un payload contra las reglas de Meta")
    v.add_argument("payload", help="JSON de `construir` o con la forma de Meta")
    v.add_argument("--json", action="store_true")

    o = sub.add_parser("origen", help="lee un webhook de WhatsApp, Messenger o Instagram y dice si trae el anuncio y "
                                      "el clic (solo local)")
    o.add_argument("webhook", help="JSON tal como lo manda Meta (guárdalo en clientes/<slug>/privado/)")
    o.add_argument("--salida", help="JSON completo, sin tapar, en clientes/<slug>/privado/")
    o.add_argument("--json", action="store_true")

    e = sub.add_parser("enviar", help="envía con --test-code; real solo con --real --confirmo")
    e.add_argument("payload", help="JSON de `construir`")
    e.add_argument("--cliente", required=True, help="slug del cliente (dataset y token)")
    e.add_argument("--dataset", help="ID del dataset si no es el de la ficha")
    e.add_argument("--test-code", help="código de Events Manager → Probar eventos")
    e.add_argument("--real", action="store_true", help="envío real al dataset (exige --confirmo)")
    e.add_argument("--confirmo", action="store_true", help="el usuario ha dicho que sí en este momento")
    e.add_argument("--json", action="store_true")

    a = p.parse_args(argv)
    {"hashear": cmd_hashear, "construir": cmd_construir, "validar": cmd_validar, "enviar": cmd_enviar,
     "origen": cmd_origen}[a.comando](a)


if __name__ == "__main__":
    main()
