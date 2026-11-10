#!/usr/bin/env python3
"""Formularios instantáneos de Meta (Lead Ads) por cliente: diseñarlos como plantilla JSON, revisarlos sin red, crearlos
en la Página con confirmación, auditar los que ya existen y descargar sus leads separando lo personal de lo agregado.

Leer (no cambia nada en Meta):
  python3 -I herramientas/formularios_meta.py listar --cliente acme                    formularios de la Página
  python3 -I herramientas/formularios_meta.py ver <form_id> --cliente acme             preguntas, final y auditoría
  python3 -I herramientas/formularios_meta.py leads <form_id> --cliente acme --desde 2026-11-02 --hasta 2026-11-08
        [--encaje <plantilla.json>] [--horario 9-20] [--sin-archivos]

Sin red (no hace falta token):
  python3 -I herramientas/formularios_meta.py crear <plantilla.json> --simular [--cliente acme]   revisa y dibuja
  python3 -I herramientas/formularios_meta.py guia <plantilla.json> [--cliente acme] [--salida <md>]
        el mismo formulario paso a paso para montarlo a mano en Ads Manager (vía sin token o con lógica condicional)

Escribir (solo `operador-meta`, con el plan aprobado y el sí del usuario en ese momento):
  python3 -I herramientas/formularios_meta.py crear <plantilla.json> --cliente acme --confirmo [--sin-logica]

Plantillas: `.claude/skills/formulario-instantaneo/plantillas/*.json` (formato explicado en su `_leeme`). Las claves
que empiezan por `_` se ignoran. `crear` traduce la plantilla a `POST /{pagina}/leadgen_forms` de la Graph API.
- Un formulario creado no gasta nada y no se usa hasta que un anuncio lo enlaza (`formulario_id` en el plan de
  `meta_ads.py crear`, destino `formulario`).
- Los formularios no se editan ni se borran (se archivan): una versión nueva es un formulario nuevo con otro
  `nombre`. `crear` no duplica: si la Página ya tiene un formulario con ese nombre, para. También para si la Página
  ya tiene 100: según la KB, el siguiente sobrescribiría el más antiguo.
- La lógica condicional (otra pregunta u otro final según la respuesta) no está documentada en la API: con `logica`
  en la plantilla, `crear` se niega salvo `--sin-logica`; móntalo con `guia` en Ads Manager.
- `verificar_telefono`: true u "obligatorio", "opcional" (la persona puede saltarlo) o false / "no". Con la API v27.0
  o posterior va como `phone_otp_verification_type` (el opcional, con la cuenta de la ficha como `ad_account_id`); con
  una META_API_VERSION anterior, como `is_phone_sms_verify_enabled` y sin modo opcional.
- `revision_politicas` en la plantilla sigue la tabla del contrato §6: `NO publicar` bloquea; `OK` u
  `OK con cambios aplicados` deja crear; cualquier otro valor queda pendiente (`/revisar-anuncio`).

`leads` (los leads solo se pueden descargar 90 días; meta-ads-kb/05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md §8):
- Una fila por lead CON datos personales → clientes/<slug>/privado/formulario-<form_id>_<desde>_<hasta>.csv
  (no empieza por `leads`: `embudo.py` no lo confunde con las cohortes del CRM).
- Agregados SIN datos personales → clientes/<slug>/datos/formulario-<form_id>_<desde>_<hasta>.csv (por anuncio) y
  `…_respuestas.csv` (reparto de las respuestas de opción múltiple). Las respuestas abiertas nunca salen de privado/.
- «Encaje declarado» = el lead eligió opciones marcadas como `encaje` en la plantilla. Es una señal temprana, no el
  cualificado del contrato §16: ese lo decide el equipo comercial después de hablar con él y vuelve a Meta por la CAPI
  del CRM (meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md §4).

Credenciales (`.env` en la raíz, nunca se imprimen):
  META_TOKEN_PAGINA   token de la Página (o META_TOKEN_PAGINA_<SLUG>). Si no está, se pide a Meta con META_TOKEN
                      (usuario del sistema con la Página asignada; docs/guias/formularios.md §2).
  META_TOKEN          por cliente META_TOKEN_<SLUG>. Permisos: ads_management, pages_manage_ads, pages_read_engagement,
                      pages_show_list y, para `leads`, leads_retrieval y acceso a clientes potenciales en la Página.
  META_APP_SECRET     opcional (appsecret_proof).

Códigos de salida: 0 bien · 1 error del usuario (plantilla inválida, falta --confirmo, Meta rechaza algo) ·
2 configuración (ficha, Página, token o permisos).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import pathlib
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun as comun  # noqa: E402
import meta_ads as ma  # noqa: E402  — cliente de la Graph API compartido (errores, reintentos, appsecret_proof)

# ---------------------------------------------------------------- formato de la plantilla
# Tipos de formulario que se pueden crear por API. «Creatividad enriquecida» (Rich creative) no tiene parámetro en la
# referencia de leadgen_forms (comprobado el 2026-11-09): solo en Ads Manager.
TIPOS = {"mas_volumen": False, "mayor_intencion": True}
SOLO_ADS_MANAGER = {"creatividad_enriquecida"}

# Tipo en la plantilla → tipo de la API (referencia Page/leadgen_forms, `questions.type`).
PREGUNTAS = {
    "opciones": "CUSTOM", "texto": "CUSTOM", "fecha_hora": "DATE_TIME",
    "nombre_completo": "FULL_NAME", "nombre": "FIRST_NAME", "apellidos": "LAST_NAME",
    "email": "EMAIL", "email_trabajo": "WORK_EMAIL", "telefono": "PHONE", "telefono_trabajo": "WORK_PHONE_NUMBER",
    "whatsapp": "WHATSAPP_NUMBER", "empresa": "COMPANY_NAME", "cargo": "JOB_TITLE", "web": "WEBSITE",
    "ciudad": "CITY", "provincia": "PROVINCE", "codigo_postal": "POST_CODE", "pais": "COUNTRY",
}
CONTACTO = {"EMAIL", "WORK_EMAIL", "PHONE", "WORK_PHONE_NUMBER", "WHATSAPP_NUMBER"}
# Botón de la pantalla final → `thank_you_page.button_type`. «reservar» va como enlace al calendario: la reserva
# embebida (Book time) se activa en Ads Manager; no está verificado qué `button_type` la activa por API.
BOTONES = {"web": "VIEW_WEBSITE", "reservar": "VIEW_WEBSITE", "descargar": "DOWNLOAD", "llamar": "CALL_BUSINESS",
           "whatsapp": "WHATSAPP", "ninguno": "NONE"}
CON_URL = {"web", "reservar", "descargar"}
IDIOMAS = {"AR_AR", "CS_CZ", "DA_DK", "DE_DE", "EL_GR", "EN_GB", "EN_US", "ES_ES", "ES_LA", "FI_FI", "FR_FR", "HE_IL",
           "HI_IN", "HU_HU", "ID_ID", "IT_IT", "JA_JP", "KO_KR", "NB_NO", "NL_NL", "PL_PL", "PT_BR", "PT_PT", "RO_RO",
           "RU_RU", "SV_SE", "TH_TH", "TR_TR", "VI_VN", "ZH_CN", "ZH_HK", "ZH_TW"}
MAX_PERSONALIZADAS = 15          # [OFFICIAL META] meta-ads-kb/05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md TL;DR
MAX_FORMULARIOS = 100            # [OFFICIAL META] según la KB 05/02 §1: el 101 sobrescribe el más antiguo (no verificado)
MAX_TEXTO_PRIVACIDAD = 70        # referencia de leadgen_forms: privacy_policy.link_text
DIAS_DESCARGA = 90               # [OFFICIAL META] los leads solo se descargan 90 días
KB_FORMULARIOS = "meta-ads-kb/05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md"
KB_RESTRINGIDOS = "meta-ads-kb/08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md"

# Datos que Meta restringe en Lead Ads (requieren permiso previo; KB 08/06 y 08/11 §7). Se buscan en el texto de las
# preguntas, normalizado sin tildes. No es exhaustivo: lo decide `revisor-politicas`.
RESTRINGIDOS = [
    ("información financiera personal", r"cuanto ganas|tus ingresos|ingresos personales|sueldo|salario|nomina\b|"
                                        r"patrimonio|deudas?\b|endeudad|credit score|historial crediticio|"
                                        r"numero de cuenta|iban\b|tarjeta de credito"),
    ("salud", r"\bsalud\b|enfermedad|dolencia|sintoma|medicacion|embaraz|discapacidad|diagnostico medico"),
    ("antecedentes penales", r"antecedentes penales|condena|\bdelito"),
    ("identificadores oficiales", r"\bdni\b|\bnie\b|pasaporte|seguridad social"),
    ("seguros", r"\bpoliza\b|tu seguro|aseguradora"),
    ("afiliación política o sindical", r"partido politico|a quien votas|ideologia|sindicato|afiliacion sindical"),
    ("raza o etnia", r"\braza\b|etnia|origen etnico"),
    ("religión", r"religion|creencias religiosas"),
    ("orientación sexual", r"orientacion sexual"),
    ("usuarios o contraseñas", r"contrasena|password|nombre de usuario"),
]
# Pregunta personalizada que pide lo mismo que una prellenada (solo se mira el texto de la pregunta, no la ayuda).
DUPLICA_PRELLENADA = (r"\b(tu|vuestro|su) (email|e mail|correo|telefono|movil|whatsapp|nombre|cargo|puesto)\b|"
                      r"\b(email|correo|telefono|movil) de (contacto|trabajo|empresa)\b|nombre y apellidos|"
                      r"nombre de (tu|la|vuestra) empresa|\bcodigo postal\b|\ben que ciudad\b")
ZONA_GRIS_FACTURACION = r"facturacion|facturais|factura tu empresa"
DINERO = r"presupuesto|invertir|inversion"
DINERO_DEL_PROYECTO = r"proyecto|programa|servicio|implantacion|automatizacion|solucion"

# Verificación del teléfono (`verificar_telefono` en la plantilla). Desde la v27.0, `phone_otp_verification_type`;
# antes, el booleano `is_phone_sms_verify_enabled`, que sigue valiendo si no se manda el nuevo. El código llega por
# WhatsApp o SMS (lo elige Meta). OTP_OPTIONAL (la persona puede saltarse la verificación) exige un `ad_account_id`
# elegible: no está documentado cuál lo es.
VERIFICACION = {"obligatorio": "OTP_REQUIRED", "opcional": "OTP_OPTIONAL", "no": "NOT_ENABLED"}
VERSION_OTP = 27

CAMPOS_LISTA = ["id", "name", "status", "locale", "created_time", "leads_count", "expired_leads_count"]
CAMPOS_FORM = CAMPOS_LISTA + ["questions", "privacy_policy_url", "follow_up_action_url", "is_optimized_for_quality",
                              "thank_you_page", "context_card", "tracking_parameters",
                              "question_page_custom_headline", "block_display_for_non_targeted_viewer", "page_id",
                              "phone_otp_verification_type", "is_phone_sms_verify_enabled"]
CAMPOS_LEAD = ["id", "created_time", "ad_id", "ad_name", "adset_id", "adset_name", "campaign_id", "campaign_name",
               "form_id", "field_data", "is_organic", "platform"]
COLUMNAS_ANUNCIO = ["form_id", "ad_id", "anuncio", "campaign_id", "campana", "leads", "organicos", "encaje",
                    "encaje_pct", "fuera_horario", "desde", "hasta"]
COLUMNAS_RESPUESTAS = ["form_id", "ad_id", "anuncio", "pregunta", "respuesta", "leads", "pct"]
VEREDICTOS_OK = ("ok", "ok con cambios aplicados")


def _salir(mensaje: str, codigo: int) -> None:
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


def _json(datos) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2, default=str))


def _norm(texto) -> str:
    """minúsculas, sin tildes, solo letras y números separados por un espacio."""
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def _n(x: float, dec: int = 0) -> str:
    return f"{x:,.{dec}f}".replace(",", "·").replace(".", ",").replace("·", ".")


def _rel(ruta: pathlib.Path) -> str:
    try:
        return str(ruta.relative_to(comun.RAIZ))
    except ValueError:
        return str(ruta)


def _es_ejemplo_id(valor) -> bool:
    return bool(re.fullmatch(r"0+", str(valor or "")))


def _dominio_de_ejemplo(url: str) -> bool:
    host = re.sub(r"^https?://", "", str(url or "")).split("/", 1)[0].lower()
    return bool(re.search(r"(\.example|\.test|\.invalid|example\.(com|org|net)|ejemplo\.(com|es))$", host))


def _bool_api(valor: bool) -> str:
    return "true" if valor else "false"


def version_api(version: str | None = None) -> int:
    """Número de la versión de la Graph API que se va a usar (META_API_VERSION o la de meta_ads.py)."""
    texto = str(version or os.environ.get("META_API_VERSION") or ma.VERSION)
    m = re.match(r"v?(\d+)", texto)
    return int(m.group(1)) if m else 0


def verificacion(p: dict) -> str | None:
    """`verificar_telefono` de la plantilla → 'obligatorio' | 'opcional' | 'no' (None si no lo dice; el texto tal cual
    si no es válido). true = obligatorio y false = no, como antes de la v27."""
    if "verificar_telefono" not in p:
        return None
    v = p["verificar_telefono"]
    if v is True:
        return "obligatorio"
    if v is False or v is None:
        return "no"
    return str(v).strip().lower()


def verifica_telefono(p: dict) -> bool:
    return verificacion(p) in ("obligatorio", "opcional")


def verificacion_leida(form: dict) -> str:
    """Lo que dice Meta de un formulario: obligatoria, opcional, no o desconocida (formularios antiguos: null)."""
    otp = form.get("phone_otp_verification_type")
    inverso = {v: k for k, v in VERIFICACION.items()}
    if otp in inverso:
        return {"obligatorio": "obligatoria", "opcional": "opcional", "no": "no"}[inverso[otp]]
    legado = form.get("is_phone_sms_verify_enabled")
    if legado is not None:
        return "obligatoria" if legado in (True, "true", 1) else "no"
    return "desconocida"


# ---------------------------------------------------------------- plantilla: lectura y revisión

def lee_plantilla(ruta: str) -> tuple[dict, pathlib.Path]:
    p = pathlib.Path(ruta).expanduser()
    try:
        datos = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _salir(f"No existe {ruta}.", 1)
    except json.JSONDecodeError as e:
        _salir(f"{ruta} no es JSON válido: {e}", 1)
    if not isinstance(datos, dict):
        _salir(f"{ruta} tiene que ser un objeto JSON (formato en las plantillas de /formulario-instantaneo).", 1)
    return datos, p


def preguntas_de(plantilla: dict) -> list[dict]:
    return [q for q in plantilla.get("preguntas") or [] if isinstance(q, dict)]


def tipo_api(q: dict) -> str:
    t = str(q.get("tipo") or "")
    return PREGUNTAS.get(t, t.upper())


def es_personalizada(q: dict) -> bool:
    return tipo_api(q) in ("CUSTOM", "DATE_TIME")


def clave_de(q: dict) -> str:
    return str(q.get("clave") or tipo_api(q).lower())


def veredicto(plantilla: dict) -> str:
    """'ok' | 'no' | 'pendiente' según `revision_politicas` (tabla del contrato §6)."""
    valor = re.split(r"\s*·", str(plantilla.get("revision_politicas") or ""), maxsplit=1)[0]
    valor = re.sub(r"\s+", " ", valor).strip(" .").lower()
    if valor.startswith("no publicar"):
        return "no"
    return "ok" if valor in VEREDICTOS_OK else "pendiente"


def reglas_encaje(plantilla: dict) -> dict[str, set[str]]:
    """{clave de pregunta: {claves de opción que cuentan como encaje}}. Se comparan normalizadas (`encaje_de`)."""
    if isinstance(plantilla.get("encaje"), dict):  # formato corto: {"tamano": ["10_49", …]}
        return {str(k): {str(x) for x in v} for k, v in plantilla["encaje"].items() if v}
    return {clave_de(q): {str(x) for x in q["encaje"]} for q in preguntas_de(plantilla) if q.get("encaje")}


def revisa_plantilla(p: dict, pagina: str | None = None,
                     version: str | None = None) -> tuple[list[str], list[str], list[str]]:
    """(errores, pendientes, avisos). Errores: la plantilla está mal o pide datos restringidos. Pendientes: está bien
    pero falta algo para crearla de verdad (Página, URLs de ejemplo, revisión de políticas). Avisos: no bloquean."""
    errores: list[str] = []
    pendientes: list[str] = []
    avisos: list[str] = []

    if not str(p.get("nombre") or "").strip():
        errores.append("falta `nombre` (así se llama el formulario en la Página; una versión nueva = nombre nuevo)")
    tipo = p.get("tipo", "mayor_intencion")
    if tipo in SOLO_ADS_MANAGER:
        errores.append("«creatividad_enriquecida» solo se puede crear en Ads Manager (usa `guia`)")
    elif tipo not in TIPOS:
        errores.append(f"`tipo` «{tipo}» no válido: mas_volumen o mayor_intencion")
    if p.get("idioma", "ES_ES") not in IDIOMAS:
        errores.append(f"`idioma` «{p.get('idioma')}» no es un locale de Meta (ES_ES, ES_LA, EN_US, PT_BR…)")

    qs = preguntas_de(p)
    if not qs:
        errores.append("el formulario no tiene `preguntas`")
    claves: set[str] = set()
    tipos = [tipo_api(q) for q in qs]
    personalizadas = [q for q in qs if es_personalizada(q)]
    abiertas = [q for q in qs if tipo_api(q) == "CUSTOM" and not q.get("opciones")]
    for i, q in enumerate(qs, 1):
        t, clave = tipo_api(q), clave_de(q)
        donde = f"pregunta {i} «{clave}»"
        if q.get("tipo") not in PREGUNTAS and not re.fullmatch(r"[A-Z][A-Z_]+", str(q.get("tipo") or "")):
            errores.append(f"{donde}: tipo «{q.get('tipo')}» no válido ({', '.join(PREGUNTAS)})")
        if clave in claves:
            errores.append(f"{donde}: clave repetida")
        claves.add(clave)
        if t in ("CUSTOM", "DATE_TIME"):
            if not re.fullmatch(r"[a-z0-9_]{1,40}", str(q.get("clave") or "")):
                errores.append(f"{donde}: las personalizadas llevan `clave` en minúsculas, números y _")
            if not str(q.get("texto") or "").strip():
                errores.append(f"{donde}: falta `texto` (la pregunta que ve la persona)")
        if q.get("tipo") == "opciones":
            ops = [o for o in q.get("opciones") or [] if isinstance(o, dict)]
            if len(ops) < 2:
                errores.append(f"{donde}: una pregunta de opciones necesita al menos 2 opciones")
            vistas = set()
            for o in ops:
                if not re.fullmatch(r"[a-z0-9_]{1,40}", str(o.get("clave") or "")) or not str(o.get("texto") or ""):
                    errores.append(f"{donde}: cada opción lleva `clave` (minúsculas, números y _) y `texto`")
                if o.get("clave") in vistas:
                    errores.append(f"{donde}: opción «{o.get('clave')}» repetida")
                vistas.add(o.get("clave"))
            if len(ops) > 6:
                avisos.append(f"{donde}: {len(ops)} opciones; Meta recomienda rangos cortos en vez de listas largas "
                              f"({KB_FORMULARIOS} §4)")
            for e in q.get("encaje") or []:
                if e not in vistas:
                    errores.append(f"{donde}: `encaje` cita «{e}», que no es una opción de esta pregunta")
        elif q.get("encaje"):
            errores.append(f"{donde}: `encaje` solo vale en preguntas de opciones")
        if q.get("tipo") == "texto" and q.get("opciones"):
            errores.append(f"{donde}: una pregunta `texto` no lleva opciones (usa `opciones`)")
        if q.get("exigir_email_trabajo") and t != "WORK_EMAIL":
            errores.append(f"{donde}: `exigir_email_trabajo` va en una pregunta `email_trabajo`")
        if t in ("CUSTOM", "DATE_TIME"):
            texto = _norm(f"{q.get('texto', '')} {q.get('ayuda', '')}")
            for categoria, patron in RESTRINGIDOS:
                if re.search(patron, texto):
                    errores.append(f"{donde}: pide {categoria}, un dato restringido en Lead Ads sin permiso previo de "
                                   f"Meta ({KB_RESTRINGIDOS}). Pregunta por la empresa o el proyecto, no por la persona")
            if re.search(DUPLICA_PRELLENADA, _norm(q.get("texto"))):
                avisos.append(f"{donde}: parece repetir una pregunta prellenada; Meta prohíbe las «sustancialmente "
                              f"iguales» a las prellenadas: usa el tipo `email`, `telefono`, `empresa`… "
                              f"({KB_FORMULARIOS} §4)")
            if re.search(ZONA_GRIS_FACTURACION, texto):
                avisos.append(f"{donde}: «facturación» es zona gris en B2B: siempre la de la empresa y en rangos "
                              f"({KB_FORMULARIOS} §4)")
            if re.search(DINERO, texto) and not re.search(DINERO_DEL_PROYECTO, texto):
                avisos.append(f"{donde}: formula el dinero sobre tu proyecto o servicio («¿encaja una inversión de…?»), "
                              f"nunca sobre la persona ({KB_FORMULARIOS} §4)")
    if len(personalizadas) > MAX_PERSONALIZADAS:
        errores.append(f"{len(personalizadas)} preguntas personalizadas: Meta admite {MAX_PERSONALIZADAS}")
    if len(abiertas) > 1:
        avisos.append(f"{len(abiertas)} preguntas de respuesta corta: Meta recomienda limitarlas; cada una baja la "
                      f"conversión ({KB_FORMULARIOS} §4)")
    if qs and not CONTACTO & set(tipos):
        errores.append("sin email ni teléfono el lead no sirve: añade `email`, `email_trabajo` o `telefono`")
    modo = verificacion(p)
    if modo is not None and modo not in VERIFICACION:
        errores.append("`verificar_telefono` es true (= obligatorio), false (= no), \"obligatorio\", \"opcional\" o "
                       "\"no\"")
    elif verifica_telefono(p):
        if "PHONE" not in tipos:  # no admite el teléfono de trabajo (KB 05/02 §3)
            errores.append("`verificar_telefono` necesita una pregunta `telefono` (no vale `telefono_trabajo`)")
        else:
            avisos.append("verificar el teléfono: Meta manda el código por WhatsApp o SMS (elige él); quien no lo "
                          "verifica no cuenta como lead y un fijo no puede verificarse")
        if modo == "opcional":
            if version_api(version) < VERSION_OTP:
                errores.append(f"`verificar_telefono: \"opcional\"` necesita la API v{VERSION_OTP}.0 o posterior "
                               "(META_API_VERSION)")
            else:
                avisos.append("verificación opcional (OTP_OPTIONAL): Meta exige que la cuenta publicitaria sea "
                              "elegible (se manda meta.cuenta de la ficha) y no documenta cuál lo es; si la rechaza, "
                              "usa \"obligatorio\" o \"no\"")
    if any(q.get("exigir_email_trabajo") for q in qs):
        avisos.append("«exigir email de trabajo» solo se aplica en Instagram o creado por API (anuncio de Meta del "
                      "2025-10-30): créalo con `crear`; en Ads Manager puede no aparecer")
    if len([q for q in qs if q.get("tipo") == "opciones"]) > 5:
        avisos.append("más de 5 preguntas de opción múltiple: más calidad pero menos envíos; quédate con las que "
                      f"cambian lo que hará el comercial ({KB_FORMULARIOS} §4)")

    priv = p.get("privacidad") or {}
    if not priv.get("url"):
        errores.append("falta `privacidad.url`: Meta exige la política de privacidad para publicar")
    elif not str(priv["url"]).startswith("https://"):
        errores.append("`privacidad.url` tiene que empezar por https://")
    elif _dominio_de_ejemplo(priv["url"]):
        pendientes.append("`privacidad.url` es de ejemplo: pon la de la web del cliente")
    if len(str(priv.get("texto_enlace") or "")) > MAX_TEXTO_PRIVACIDAD:
        errores.append(f"`privacidad.texto_enlace` pasa de {MAX_TEXTO_PRIVACIDAD} caracteres")

    intro = p.get("intro")
    if intro:
        if not str(intro.get("titulo") or "").strip():
            errores.append("`intro` necesita `titulo`")
        if intro.get("estilo", "lista") not in ("lista", "parrafo"):
            errores.append("`intro.estilo` es lista o parrafo")
        if not isinstance(intro.get("contenido"), list) or not intro["contenido"]:
            errores.append("`intro.contenido` es una lista de textos (qué recibe, qué pasa después, para quién no es)")
    elif tipo == "mayor_intencion":
        avisos.append(f"sin `intro`: es el filtro más barato (qué pasa después y para quién no es; {KB_FORMULARIOS} §5)")

    def revisa_final(f: dict, donde: str) -> None:
        if not isinstance(f, dict) or not str(f.get("titulo") or "").strip():
            errores.append(f"{donde}: falta `titulo`")
            return
        boton = f.get("boton", "web")
        if boton not in BOTONES:
            errores.append(f"{donde}: `boton` «{boton}» no válido ({', '.join(BOTONES)})")
        if boton in CON_URL:
            url = str(f.get("url") or "")
            if not url.startswith("https://"):
                errores.append(f"{donde}: con `boton` {boton} hace falta `url` https://")
            elif _dominio_de_ejemplo(url):
                pendientes.append(f"{donde}: `url` de ejemplo ({url.split('/')[2]})")
        if boton == "llamar" and not re.fullmatch(r"\+\d{8,15}", str(f.get("telefono") or "").replace(" ", "")):
            errores.append(f"{donde}: con `boton` llamar hace falta `telefono` con prefijo (+34…)")
        if boton == "ninguno":
            avisos.append(f"{donde}: sin botón, la pantalla de más intención se queda sin siguiente paso "
                          f"({KB_FORMULARIOS} §6)")

    revisa_final(p.get("final"), "final")
    if (p.get("final") or {}).get("boton") == "reservar":
        avisos.append("final «reservar»: por API va como enlace al calendario; la reserva embebida (Book time) se "
                      "activa en Ads Manager con el enlace directo de Calendly o HighLevel, solo se embebe en la app de "
                      "Facebook en móvil (en Instagram abre el navegador) y no se reporta en Ads Manager: la cita vuelve "
                      f"a Meta solo si la manda el CRM como `Schedule` ({KB_FORMULARIOS} §6)")
    if tipo == "mas_volumen" and (p.get("final") or {}).get("boton") in ("reservar", "llamar"):
        avisos.append(f"más volumen para un lead que va a una persona: usa mayor_intencion ({KB_FORMULARIOS} §2)")
    if tipo == "mayor_intencion":
        avisos.append("mayor intención solo entrega en el Feed de Facebook e Instagram en móvil")

    finales = p.get("finales_alternativos") or {}
    for k, f in finales.items():
        revisa_final(f, f"finales_alternativos.{k}")
    opciones_de = {clave_de(q): {o.get("clave") for o in q.get("opciones") or []} for q in qs}
    for i, r in enumerate(p.get("logica") or [], 1):
        si = r.get("si") or {}
        preg, resp = si.get("pregunta"), si.get("respuesta") or []
        resp = [resp] if isinstance(resp, str) else resp
        if preg not in opciones_de or not opciones_de[preg]:
            errores.append(f"logica {i}: «{preg}» no es una pregunta de opciones de la plantilla")
        elif any(x not in opciones_de[preg] for x in resp):
            errores.append(f"logica {i}: alguna respuesta no es opción de «{preg}»")
        destino = str(r.get("ir_a") or "")
        tipo_d, _, objetivo = destino.partition(":")
        if tipo_d == "final" and objetivo not in finales:
            errores.append(f"logica {i}: `ir_a` final:{objetivo} no está en finales_alternativos")
        elif tipo_d == "pregunta" and objetivo not in opciones_de:
            errores.append(f"logica {i}: `ir_a` pregunta:{objetivo} no existe")
        elif tipo_d not in ("final", "pregunta"):
            errores.append(f"logica {i}: `ir_a` es final:<clave> o pregunta:<clave>")
    if p.get("logica"):
        avisos.append("la lógica condicional no está documentada en la API: `crear` la deja fuera solo con "
                      "--sin-logica; para tenerla, monta el formulario en Ads Manager con `guia`")
    elif finales:
        avisos.append("hay `finales_alternativos` sin `logica` que lleve a ellos")

    for k, v in (p.get("parametros") or {}).items():
        if not re.fullmatch(r"[a-z0-9_]{1,40}", str(k)) or not isinstance(v, str) or not v:
            errores.append(f"parametros.{k}: claves en minúsculas y _ con valor de texto")
    if not p.get("parametros"):
        avisos.append("sin `parametros` de seguimiento: llegan al CSV y al CRM y separan oferta y versión "
                      f"({KB_FORMULARIOS} §8)")
    aviso_legal = p.get("aviso_legal")
    if aviso_legal:
        if not str(aviso_legal.get("texto") or "").strip():
            errores.append("`aviso_legal` necesita `texto`")
        vistas = set()
        for c in aviso_legal.get("casillas") or []:
            if not re.fullmatch(r"[a-z0-9_]{1,40}", str(c.get("clave") or "")) or not c.get("texto"):
                errores.append("cada casilla de `aviso_legal` lleva `clave` y `texto`")
            if c.get("clave") in vistas:
                errores.append(f"aviso_legal: casilla «{c.get('clave')}» repetida")
            vistas.add(c.get("clave"))
    if p.get("solo_anuncios") is False:
        avisos.append(f"`solo_anuncios: false` abre la puerta a leads orgánicos y compartidos ({KB_FORMULARIOS} §1)")
    if "status" in (p.get("api") or {}):
        errores.append("`api.status` no se envía: el estado lo decide Meta y un formulario no se activa ni se archiva "
                       "desde aquí")

    v = veredicto(p)
    if v == "no":
        errores.append("revision_politicas dice «NO publicar»: aplica la reescritura de revisor-politicas antes")
    elif v == "pendiente":
        pendientes.append("revisión de políticas pendiente: /revisar-anuncio sobre los textos del formulario y anota "
                          "`revision_politicas: OK · AAAA-MM-DD · revisor-politicas`")
    if pagina is not None and (not pagina or _es_ejemplo_id(pagina)):
        pendientes.append("falta la Página (meta.pagina en la ficha o --pagina)")
    return errores, pendientes, avisos


# ---------------------------------------------------------------- plantilla → API

def construir(p: dict, version: str | None = None, cuenta: str | None = None) -> dict:
    """Parámetros de `POST /{pagina}/leadgen_forms` (referencia Page/leadgen_forms, comprobada el 2026-11-09; la
    verificación del teléfono, con el changelog de la v27.0). Sin la lógica condicional (no documentada en la API).
    `version`: la de la API (por defecto META_API_VERSION o la de meta_ads.py). `cuenta`: la cuenta publicitaria de la
    ficha, solo para la verificación opcional."""
    preguntas = []
    for q in preguntas_de(p):
        t = tipo_api(q)
        api: dict = {"type": t}
        if t in ("CUSTOM", "DATE_TIME"):
            api |= {"key": q["clave"], "label": q["texto"]}
            if q.get("opciones"):
                api["options"] = [{"key": o["clave"], "value": o["texto"]} for o in q["opciones"]]
        elif q.get("clave"):
            api["key"] = q["clave"]
        if q.get("ayuda"):
            api["inline_context"] = q["ayuda"]
        if t == "WORK_EMAIL" and q.get("exigir_email_trabajo"):
            api["should_enforce_work_email"] = True
        preguntas.append(api)

    def final(f: dict) -> dict:
        boton = f.get("boton", "web")
        pagina_final = {"title": f["titulo"], "button_type": BOTONES[boton],
                        "country_code": str(f.get("pais") or p.get("pais") or "ES").upper()}
        for clave, api in (("texto", "body"), ("texto_boton", "button_text")):
            if f.get(clave):
                pagina_final[api] = f[clave]
        if boton in CON_URL:
            pagina_final["website_url"] = f["url"]
        if boton == "llamar":
            pagina_final["business_phone_number"] = str(f["telefono"]).replace(" ", "")
        return pagina_final

    payload: dict = {
        "name": p["nombre"],
        "locale": p.get("idioma", "ES_ES"),
        "questions": preguntas,
        "is_optimized_for_quality": _bool_api(TIPOS.get(p.get("tipo", "mayor_intencion"), True)),
        "block_display_for_non_targeted_viewer": _bool_api(p.get("solo_anuncios", True) is not False),
        "privacy_policy": {k: v for k, v in (("url", (p.get("privacidad") or {}).get("url")),
                                             ("link_text", (p.get("privacidad") or {}).get("texto_enlace"))) if v},
        "thank_you_page": final(p["final"]),
    }
    if (p["final"].get("boton", "web")) in ("web", "reservar"):
        payload["follow_up_action_url"] = p["final"]["url"]
    modo = verificacion(p)
    if modo is not None:  # el código va por WhatsApp o SMS: lo elige Meta
        if version_api(version) >= VERSION_OTP:
            payload["phone_otp_verification_type"] = VERIFICACION.get(modo, "NOT_ENABLED")
            if modo == "opcional" and cuenta and re.fullmatch(r"(act_)?\d{5,25}", str(cuenta)):
                payload["ad_account_id"] = str(cuenta).removeprefix("act_")  # formato no documentado
        elif modo == "opcional":
            raise ValueError(f"verificación opcional: necesita la API v{VERSION_OTP}.0 o posterior")
        else:
            payload["is_phone_sms_verify_enabled"] = _bool_api(modo == "obligatorio")
    if p.get("intro"):
        i = p["intro"]
        payload["context_card"] = {"title": i["titulo"],
                                   "style": "PARAGRAPH_STYLE" if i.get("estilo") == "parrafo" else "LIST_STYLE",
                                   "content": list(i["contenido"])}
        if i.get("boton"):
            payload["context_card"]["button_text"] = i["boton"]
    if p.get("titular_preguntas"):
        payload["question_page_custom_headline"] = p["titular_preguntas"]
    if p.get("parametros"):
        payload["tracking_parameters"] = dict(p["parametros"])
    if p.get("aviso_legal"):
        a = p["aviso_legal"]
        payload["custom_disclaimer"] = {
            "body": {"text": a["texto"], "url_entities": []},
            "checkboxes": [{"key": c["clave"], "text": c["texto"], "is_required": bool(c.get("obligatoria", False)),
                            "is_checked_by_default": False} for c in a.get("casillas") or []]}
        if a.get("titulo"):
            payload["custom_disclaimer"]["title"] = a["titulo"]
    payload |= {k: v for k, v in (p.get("api") or {}).items() if k != "status"}
    return payload


def huella(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- salida legible

def _etiqueta_tipo(p: dict) -> str:
    return {"mas_volumen": "más volumen (envío rápido, todas las ubicaciones)",
            "mayor_intencion": "mayor intención (pantalla de revisión; solo Feed de FB e IG en móvil)"}.get(
        p.get("tipo", "mayor_intencion"), str(p.get("tipo")))


def _describe_final(f: dict) -> str:
    boton = f.get("boton", "web")
    destino = f.get("url") or f.get("telefono") or ""
    return (f"«{f.get('titulo', '')}» · botón {BOTONES.get(boton, boton)}"
            + (f" «{f['texto_boton']}»" if f.get("texto_boton") else "") + (f" → {destino}" if destino else ""))


def _describe_logica(p: dict) -> list[str]:
    salida = []
    for r in p.get("logica") or []:
        si = r.get("si") or {}
        resp = si.get("respuesta") or []
        resp = [resp] if isinstance(resp, str) else resp
        tipo_d, _, obj = str(r.get("ir_a") or "").partition(":")
        destino = (f"final «{(p.get('finales_alternativos') or {}).get(obj, {}).get('titulo', obj)}»"
                   if tipo_d == "final" else f"pregunta «{obj}»")
        salida.append(f"si «{si.get('pregunta')}» = {' o '.join(resp)} → {destino}")
    return salida


def dibuja(p: dict, pagina: str | None) -> None:
    qs = preguntas_de(p)
    personalizadas = [q for q in qs if es_personalizada(q)]
    abiertas = [q for q in qs if tipo_api(q) == "CUSTOM" and not q.get("opciones")]
    print(f"Formulario  «{p.get('nombre')}» · {_etiqueta_tipo(p)} · {p.get('idioma', 'ES_ES')}")
    print(f"Página      {pagina if pagina and not _es_ejemplo_id(pagina) else '— (falta)'}")
    if p.get("intro"):
        i = p["intro"]
        puntos = len(i.get("contenido") or [])
        print(f"Intro       «{i.get('titulo')}» ({'párrafo' if i.get('estilo') == 'parrafo' else 'lista'}, {puntos} "
              f"{'punto' if puntos == 1 else 'puntos'})"
              + (f" · botón «{i['boton']}»" if i.get("boton") else ""))
    print(f"Preguntas   {len(personalizadas)} personalizadas de {MAX_PERSONALIZADAS} · {len(abiertas)} de respuesta "
          f"corta · ✓ = encaje")
    for n, q in enumerate(qs, 1):
        t = tipo_api(q)
        if q.get("tipo") == "opciones":
            ops = " · ".join(f"{o['clave']}{' ✓' if o['clave'] in (q.get('encaje') or []) else ''}"
                             for o in q.get("opciones") or [])
            print(f"  {n}. [opciones] {q.get('clave')} · {q.get('texto')}\n       {ops}")
        elif t in ("CUSTOM", "DATE_TIME"):
            print(f"  {n}. [{'respuesta corta' if t == 'CUSTOM' else 'fecha y hora'}] {q.get('clave')} · {q.get('texto')}")
        else:
            extra = " (exige email de trabajo)" if q.get("exigir_email_trabajo") else ""
            print(f"  {n}. [prellenada] {t}{extra}")
    print(f"Filtros     verificar teléfono (WhatsApp o SMS): {_verificacion_texto(p)} · solo anuncios "
          f"(sin leads orgánicos): {'no' if p.get('solo_anuncios') is False else 'sí'}")
    priv = p.get("privacidad") or {}
    print(f"Privacidad  {priv.get('url', '—')}" + (f" («{priv['texto_enlace']}»)" if priv.get("texto_enlace") else ""))
    if p.get("aviso_legal"):
        casillas = p["aviso_legal"].get("casillas") or []
        print(f"Aviso legal {len(casillas)} casilla(s): " + (", ".join(
            f"{c.get('clave')} ({'obligatoria' if c.get('obligatoria') else 'opcional'})" for c in casillas) or "—"))
    if p.get("final"):
        print(f"Final       {_describe_final(p['final'])}")
    for k, f in (p.get("finales_alternativos") or {}).items():
        print(f"  alt. {k}: {_describe_final(f)}")
    if p.get("parametros"):
        print("Parámetros  " + " · ".join(f"{k}={v}" for k, v in p["parametros"].items()))
    for linea in _describe_logica(p):
        print(f"Lógica      {linea}  (solo en Ads Manager)")
    print(f"Políticas   {p.get('revision_politicas') or 'pendiente'}")


def _verificacion_texto(p: dict) -> str:
    return {"obligatorio": "sí", "opcional": "opcional (se puede saltar)"}.get(verificacion(p) or "", "no")


def guia_markdown(p: dict, pagina: str | None, cliente: str | None) -> str:
    """El formulario paso a paso para montarlo a mano en Ads Manager (vía sin token o con lógica condicional)."""
    qs = preguntas_de(p)
    tipo = {"mas_volumen": "Más volumen (More volume)", "mayor_intencion": "Mayor intención (Higher intent)",
            "creatividad_enriquecida": "Creatividad enriquecida (Rich creative)"}.get(p.get("tipo", "mayor_intencion"))
    l = [f"# Formulario «{p.get('nombre')}» en Ads Manager",
         "",
         f"Cliente: {cliente or '—'} · Página: {pagina or '—'} · generado el {date.today().isoformat()} con "
         "`formularios_meta.py guia`. Los nombres de los botones pueden variar según el idioma de tu Ads Manager.",
         "",
         "1. **Dónde.** Ads Manager → menú → *Formularios instantáneos* (o, dentro del anuncio, *Destino → Formulario "
         "instantáneo → Crear formulario*). Hazlo desde Ads Manager, no desde la Página: las opciones avanzadas solo "
         f"están ahí ({KB_FORMULARIOS} §1).",
         f"2. **Nombre:** `{p.get('nombre')}`. **Tipo:** {tipo}.",
         f"3. **Idioma:** {p.get('idioma', 'ES_ES')}."]
    paso = 4
    if p.get("intro"):
        i = p["intro"]
        l.append(f"{paso}. **Introducción** (activada) · estilo {'párrafo' if i.get('estilo') == 'parrafo' else 'lista'}"
                 f" · titular: «{i.get('titulo')}»")
        l += [f"   - {x}" for x in i.get("contenido") or []]
        if i.get("boton"):
            l.append(f"   - Botón: «{i['boton']}»")
        paso += 1
    l.append(f"{paso}. **Preguntas**" + (f" · titular de la página: «{p['titular_preguntas']}»"
                                         if p.get("titular_preguntas") else "") + ":")
    for n, q in enumerate(qs, 1):
        t = tipo_api(q)
        if q.get("tipo") == "opciones":
            l.append(f"   {n}. *Opción múltiple* · «{q.get('texto')}» (clave `{q.get('clave')}`)")
            l += [f"      - {o.get('texto')} (`{o.get('clave')}`)" for o in q.get("opciones") or []]
        elif t == "CUSTOM":
            l.append(f"   {n}. *Respuesta corta* · «{q.get('texto')}» (clave `{q.get('clave')}`)")
        elif t == "DATE_TIME":
            l.append(f"   {n}. *Solicitud de cita* · «{q.get('texto')}» (solo preferencia de franja; no es un calendario)")
        else:
            extra = (" · activa *Exigir email de trabajo* si aparece (según Meta solo se aplica en Instagram o por "
                     "API: si no lo ves, crea este formulario con `crear`)") if q.get("exigir_email_trabajo") else ""
            l.append(f"   {n}. *Prellenada* · {t}{extra}")
        if q.get("ayuda"):
            l.append(f"      - Texto de ayuda: «{q['ayuda']}»")
    paso += 1
    if p.get("logica"):
        l.append(f"{paso}. **Lógica condicional** (activa el interruptor al final de las preguntas):")
        l += [f"   - {x}" for x in _describe_logica(p)]
        l.append("   - El resto de respuestas sigue a la siguiente pregunta y al final principal.")
        paso += 1
    priv = p.get("privacidad") or {}
    l.append(f"{paso}. **Política de privacidad:** {priv.get('url', '—')}"
             + (f" · texto del enlace «{priv['texto_enlace']}»" if priv.get("texto_enlace") else ""))
    paso += 1
    if p.get("aviso_legal"):
        a = p["aviso_legal"]
        l.append(f"{paso}. **Aviso legal personalizado:** «{a.get('texto')}»")
        l += [f"   - Casilla `{c.get('clave')}` ({'obligatoria' if c.get('obligatoria') else 'opcional'}, sin marcar "
              f"por defecto): «{c.get('texto')}»" for c in a.get("casillas") or []]
        paso += 1
    finales = [("Pantalla final", p.get("final") or {})] + [(f"Final alternativo «{k}»", f)
                                                           for k, f in (p.get("finales_alternativos") or {}).items()]
    for titulo, f in finales:
        l.append(f"{paso}. **{titulo}:** titular «{f.get('titulo')}»" + (f" · texto «{f['texto']}»" if f.get("texto")
                                                                         else ""))
        boton = f.get("boton", "web")
        if boton == "reservar":
            l.append(f"   - Botón *Reservar* (Book time) con el enlace directo del calendario del partner "
                     f"(Calendly o HighLevel/LeadConnector; no vale una URL propia): {f.get('url')}. Se embebe solo en "
                     "la app de Facebook en móvil; en Instagram abre el navegador de la app. La reserva no llega a Ads "
                     "Manager: la devuelve el CRM como `Schedule`.")
        elif boton == "llamar":
            l.append(f"   - Botón *Llamar a la empresa*: {f.get('telefono')}")
        elif boton == "whatsapp":
            l.append("   - Botón *Chatear por WhatsApp* (la Página tiene que tener WhatsApp vinculado)")
        elif boton != "ninguno":
            l.append(f"   - Botón «{f.get('texto_boton', 'Ver web')}» → {f.get('url')}")
        paso += 1
    l.append(f"{paso}. **Ajustes:** *Compartir* = Restringido"
             + ("" if p.get("solo_anuncios") is not False else " (la plantilla pide Abierto: revísalo)")
             + (" · parámetros de seguimiento: " + ", ".join(f"`{k}` = `{v}`" for k, v in p["parametros"].items())
                if p.get("parametros") else ""))
    paso += 1
    if verifica_telefono(p):
        l.append(f"{paso}. **Verificación del teléfono:** actívala"
                 + (" en modo opcional (la persona puede saltarla), si tu Ads Manager lo ofrece" if verificacion(p) ==
                    "opcional" else "")
                 + " (puede aparecer en el formulario o en el anuncio, *Destino → filtros de calidad*). Meta manda el "
                 "código por WhatsApp o SMS; quien no verifica no cuenta como lead y los fijos no pueden verificarse.")
        paso += 1
    l += [f"{paso}. **Revisa la vista previa en el móvil** y publica. Publicar el formulario no gasta nada: solo se usa "
          "cuando un anuncio lo enlaza. Un formulario publicado no se edita: para cambiarlo, duplícalo con otro nombre.",
          f"{paso + 1}. **Copia el ID** del formulario (biblioteca de formularios) a `formulario_id` del plan de campaña "
          "y prueba un lead con la herramienta de pruebas de anuncios para clientes potenciales "
          "(developers.facebook.com/tools/lead-ads-testing) antes de lanzar: tiene que llegar al CRM en menos de un "
          "minuto con sus respuestas y el ID del lead.",
          "",
          f"Revisión de políticas: {p.get('revision_politicas') or 'pendiente'}."]
    return "\n".join(l) + "\n"


# ---------------------------------------------------------------- conexión

def _ficha(slug: str) -> dict:
    try:
        return comun.leer_ficha(slug)
    except comun.FichaInvalida as e:
        _salir(str(e), 2)


def pagina_de(ficha: dict | None, explicita: str | None) -> str:
    return str(explicita or ((ficha or {}).get("meta") or {}).get("pagina") or "").strip()


def conectar_pagina(slug: str, pagina: str) -> ma.Meta:
    """Cliente de la Graph API con el token de la Página (META_TOKEN_PAGINA o pedido con META_TOKEN)."""
    if not re.fullmatch(r"\d{5,25}", pagina or "") or _es_ejemplo_id(pagina):
        _salir(f"La ficha de {slug} no tiene una Página real en meta.pagina (o pásala con --pagina). "
               "Sácala con `meta_ads.py activos`.", 2)
    secreto = comun.credencial("META_APP_SECRET", slug)
    token_pagina = comun.credencial("META_TOKEN_PAGINA", slug)
    if token_pagina:
        return ma.Meta(token_pagina, app_secret=secreto)
    token = comun.credencial("META_TOKEN", slug)
    sufijo = slug.upper().replace("-", "_")
    if not token:
        _salir(f"Falta META_TOKEN_PAGINA_{sufijo} (o META_TOKEN_{sufijo} / META_TOKEN) en .env: "
               "docs/guias/formularios.md §2. Sin token, crea el formulario en Ads Manager con `guia`.", 2)
    sistema = ma.Meta(token, app_secret=secreto)
    try:
        datos = sistema.uno(pagina, fields="access_token")
    except ma.ErrorMeta as e:
        _salir(f"No puedo pedir el token de la Página {pagina}: {e}\nAsigna la Página al usuario del sistema con la "
               "tarea de crear anuncios (docs/guias/formularios.md §2).", 2)
    if not datos.get("access_token"):
        _salir(f"El token no recibe el token de la Página {pagina}: asígnale la Página con la tarea de crear anuncios "
               "y los permisos pages_manage_ads y pages_read_engagement (docs/guias/formularios.md §2).", 2)
    return ma.Meta(datos["access_token"], app_secret=secreto)


def con_campos(llamada, campos: list[str]):
    """Llama con `fields`; si Meta no conoce un campo (error 100), lo quita y repite. Devuelve (resultado, campos)."""
    campos = list(campos)
    for _ in range(len(campos)):
        try:
            return llamada(",".join(campos)), campos
        except ma.ErrorMeta as e:
            texto = str(e)
            culpables = [c for c in campos if c != "id" and re.search(rf"(?<![\w]){re.escape(c)}(?![\w])", texto)]
            if e.codigo != 100 or not culpables:
                raise
            campos = [c for c in campos if c not in culpables]
    raise ma.ErrorMeta("Meta rechaza todos los campos pedidos.")


def _estado_ruta(slug: str) -> pathlib.Path:
    return comun.ruta_cliente(slug) / "planes" / "formularios.json"


def lee_estado(slug: str) -> dict:
    ruta = _estado_ruta(slug)
    if ruta.exists():
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            if isinstance(datos, dict):
                datos.setdefault("formularios", {})
                return datos
        except ValueError:
            pass
    return {"formularios": {}}


def guarda_estado(slug: str, estado: dict) -> None:
    ruta = _estado_ruta(slug)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fila_change_log(objeto: str, cambio: str, motivo: str = "<motivo / hipótesis>", dias: int = 14) -> str:
    ahora = datetime.now()
    return (f"| {ahora:%Y-%m-%d %H:%M} | operador-meta (formularios_meta.py) | formulario | {objeto} | {cambio} "
            f"| {motivo} | <métrica: coste por lead cualificado o por llamada> | "
            f"{(ahora + timedelta(days=dias)):%Y-%m-%d} | |")


# ---------------------------------------------------------------- órdenes: crear y guía (sin red salvo crear)

def cmd_crear(a: argparse.Namespace) -> None:
    plantilla, ruta = lee_plantilla(a.plantilla)
    slug = a.cliente or (plantilla.get("cliente") if isinstance(plantilla.get("cliente"), str) else None)
    ficha = _ficha(slug) if slug else None
    pagina = pagina_de(ficha, a.pagina)
    errores, pendientes, avisos = revisa_plantilla(plantilla, pagina if (slug or a.pagina) else None)
    cuenta = str(((ficha or {}).get("meta") or {}).get("cuenta") or "")
    cuenta_real = re.fullmatch(r"act_\d{5,25}", cuenta) and not _es_ejemplo_id(cuenta.removeprefix("act_"))
    if verificacion(plantilla) == "opcional" and slug and not cuenta_real:
        pendientes.append("verificación opcional: falta la cuenta publicitaria real en meta.cuenta de la ficha")
    if errores:
        if a.json:
            _json({"ok": False, "errores": errores, "pendientes": pendientes, "avisos": avisos})
            sys.exit(1)
        _salir("La plantilla no se puede crear:\n  - " + "\n  - ".join(errores)
               + ("\nAdemás falta:\n  - " + "\n  - ".join(pendientes) if pendientes else ""), 1)
    payload = construir(plantilla, cuenta=cuenta)
    if a.simular:
        if a.json:
            return _json({"ok": True, "simulado": True, "pagina": pagina or None, "payload": payload,
                          "logica": _describe_logica(plantilla), "pendientes": pendientes, "avisos": avisos})
        dibuja(plantilla, pagina)
        for x in avisos:
            print(f"Aviso: {x}")
        if pendientes:
            print("\nPlantilla correcta. Antes de crearla de verdad falta:\n  - " + "\n  - ".join(pendientes))
        print("\nNo se ha tocado Meta (--simular).")
        return
    if not slug:
        _salir("Para crear hace falta --cliente <slug> (la Página y el token salen de su ficha).", 1)
    if plantilla.get("logica") and not a.sin_logica:
        _salir("La plantilla tiene lógica condicional y la API no la documenta: no se ha creado nada.\n"
               f"  - Para tenerla: `python3 -I herramientas/formularios_meta.py guia {a.plantilla} --cliente {slug}` y "
               "móntalo en Ads Manager.\n  - Para crearlo sin ella (todos ven el final principal): repite con "
               "--sin-logica.", 1)
    if pendientes:
        _salir("No se ha tocado Meta. Antes de crear falta:\n  - " + "\n  - ".join(pendientes), 1)
    if not a.confirmo:
        if not a.json:
            dibuja(plantilla, pagina)
        _salir("\nNo se ha creado nada. Solo con el sí del usuario en este momento: repite con --confirmo.", 1)

    clave = f"{pagina}:{plantilla['nombre']}"
    estado = lee_estado(slug)
    previo = estado["formularios"].get(clave)
    if previo and previo.get("id"):
        if a.json:
            return _json({"ok": True, "ya_existia": True, "id": previo["id"], "nombre": plantilla["nombre"]})
        print(f"Ya creado el {previo.get('creado')}: «{plantilla['nombre']}» = {previo['id']} (no se duplica). "
              "Para una versión nueva, cambia `nombre`.")
        return
    api = conectar_pagina(slug, pagina)
    try:
        existentes, _ = con_campos(lambda f: list(api.lista(f"{pagina}/leadgen_forms", fields=f, limit=100)),
                                   ["id", "name", "status"])
        igual = next((x for x in existentes if x.get("name") == plantilla["nombre"]), None)
        if igual:
            _salir(f"La Página ya tiene un formulario «{plantilla['nombre']}» ({igual.get('id')}, "
                   f"{igual.get('status', '¿?')}). Los formularios no se editan: para una versión nueva, cambia "
                   "`nombre` (p. ej. _v2). No se ha creado nada.", 1)
        if len(existentes) >= MAX_FORMULARIOS:
            _salir(f"La Página ya tiene {len(existentes)} formularios. Según la KB ({KB_FORMULARIOS} §1), Meta guarda "
                   f"{MAX_FORMULARIOS} y uno nuevo sobrescribe el más antiguo, con lo que se perdería sin que nadie "
                   "lo haya decidido. No se ha creado nada: decide con el usuario qué formulario sobra (archivarlo o "
                   "perderlo es una decisión suya, por escrito) y repite.", 1)
        nuevo = api.escribe(f"{pagina}/leadgen_forms", **payload)["id"]
    except ma.ErrorMeta as e:
        _salir(f"{e}\nNo se ha creado nada.", e.salida)
    qs = preguntas_de(plantilla)
    detalle = (f"«{plantilla['nombre']}» en la Página {pagina}: {plantilla.get('tipo', 'mayor_intencion')}, "
               f"{len(qs)} preguntas ({sum(es_personalizada(q) for q in qs)} personalizadas), "
               f"verificar teléfono {_verificacion_texto(plantilla)}"
               + (", sin la lógica condicional" if plantilla.get("logica") else "")
               + "; sin usar hasta que un anuncio lo enlace")
    comun.registrar_cambio("meta", "cli", "crear_formulario", nuevo, slug, detalle)
    estado["formularios"][clave] = {"id": str(nuevo), "nombre": plantilla["nombre"], "pagina": pagina,
                                    "plantilla": _rel(ruta.resolve()), "huella": huella(payload),
                                    "creado": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "logica_pendiente": bool(plantilla.get("logica")),
                                    "encaje": {k: sorted(v) for k, v in reglas_encaje(plantilla).items()}}
    guarda_estado(slug, estado)

    # Releer: la API a veces responde OK sin guardar un campo.
    diferencias = []
    try:
        leido, _ = con_campos(lambda f: api.uno(str(nuevo), fields=f),
                              ["id", "name", "status", "is_optimized_for_quality", "questions",
                               "phone_otp_verification_type"])
        if "questions" in leido and len(leido.get("questions") or []) != len(payload["questions"]):
            diferencias.append(f"preguntas: enviadas {len(payload['questions'])}, guardadas "
                               f"{len(leido.get('questions') or [])}")
        if "is_optimized_for_quality" in leido and \
                bool(leido["is_optimized_for_quality"]) != (payload["is_optimized_for_quality"] == "true"):
            diferencias.append("el tipo (mayor intención) no coincide con la plantilla")
        if payload.get("phone_otp_verification_type") and leido.get("phone_otp_verification_type") not in (
                None, payload["phone_otp_verification_type"]):
            diferencias.append(f"verificación del teléfono: enviada {payload['phone_otp_verification_type']}, "
                               f"guardada {leido['phone_otp_verification_type']}")
    except ma.ErrorMeta as e:
        diferencias.append(f"no he podido releerlo ({e})")
    if a.json:
        return _json({"ok": True, "id": nuevo, "nombre": plantilla["nombre"], "pagina": pagina,
                      "estado": _rel(_estado_ruta(slug)), "diferencias": diferencias,
                      "logica_pendiente": bool(plantilla.get("logica"))})
    print(f"Formulario creado: «{plantilla['nombre']}» = {nuevo} en la Página {pagina}. No gasta nada y no se usa "
          "hasta que un anuncio lo enlace.")
    for d in diferencias:
        print(f"⚠ Al releerlo: {d}. Revísalo en Ads Manager antes de enlazarlo.")
    if plantilla.get("logica"):
        print("⚠ Sin lógica condicional (--sin-logica): todos ven el final principal.")
    print("Siguiente:\n"
          f"  1. Lead de prueba: developers.facebook.com/tools/lead-ads-testing → Página y formulario {nuevo}; tiene que "
          "llegar al CRM en menos de un minuto (docs/guias/formularios.md §5).\n"
          f"  2. En el plan de campaña: conjunto con \"destino\": \"formulario\" y \"formulario_id\": \"{nuevo}\".")
    print("Fila para el change log:\n" + fila_change_log(f"{plantilla['nombre']} ({nuevo})", "— → creado (sin usar)"))


def cmd_guia(a: argparse.Namespace) -> None:
    plantilla, _ = lee_plantilla(a.plantilla)
    slug = a.cliente or (plantilla.get("cliente") if isinstance(plantilla.get("cliente"), str) else None)
    ficha = _ficha(slug) if slug else None
    pagina = pagina_de(ficha, a.pagina)
    errores, pendientes, avisos = revisa_plantilla(plantilla, None)
    errores = [e for e in errores if "creatividad_enriquecida" not in e]  # en Ads Manager sí se puede
    if errores:
        _salir("Arregla la plantilla antes de montarla:\n  - " + "\n  - ".join(errores), 1)
    texto = guia_markdown(plantilla, pagina or None, slug)
    # Lo que la propia guía ya explica en su paso no se repite al final.
    avisos = [x for x in avisos if not x.startswith(("la lógica condicional", "final «reservar»",
                                                     "«exigir email de trabajo»", "verificar el teléfono"))]
    if pendientes or avisos:
        texto += "\n## Antes de publicar\n\n" + "".join(f"- {x}\n" for x in pendientes + avisos)
    if a.salida:
        ruta = pathlib.Path(a.salida).expanduser()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        print(f"Guía en {_rel(ruta)}")
    else:
        print(texto, end="")


# ---------------------------------------------------------------- órdenes de lectura

def cmd_listar(a: argparse.Namespace) -> None:
    ficha = _ficha(a.cliente)
    pagina = pagina_de(ficha, a.pagina)
    api = conectar_pagina(a.cliente, pagina)
    formularios, _ = con_campos(lambda f: list(api.lista(f"{pagina}/leadgen_forms", fields=f, limit=100)),
                                CAMPOS_LISTA)
    estado = lee_estado(a.cliente)["formularios"]
    nuestros = {v.get("id"): v for v in estado.values()}
    filas = [{"id": f.get("id"), "nombre": f.get("name", ""), "estado": f.get("status", ""),
              "idioma": f.get("locale", ""), "creado": str(f.get("created_time", ""))[:10],
              "leads": f.get("leads_count"), "caducados": f.get("expired_leads_count"),
              "plantilla": (nuestros.get(f.get("id")) or {}).get("plantilla")} for f in formularios]
    if a.json:
        return _json({"pagina": pagina, "formularios": filas})
    if not filas:
        print(f"La Página {pagina} no tiene formularios instantáneos.")
        return
    print(f"{'ID':<20}{'Creado':<12}{'Estado':<10}{'Leads':>7}{'Cad.':>6}  Nombre")
    for f in filas:
        print(f"{f['id']:<20}{f['creado']:<12}{f['estado'][:9]:<10}{'' if f['leads'] is None else f['leads']:>7}"
              f"{'' if f['caducados'] is None else f['caducados']:>6}  {f['nombre'][:60]}"
              + (f"  ← {f['plantilla']}" if f["plantilla"] else ""))
    print(f"\n{len(filas)} formularios en esta Página. Según la KB ({KB_FORMULARIOS} §1) Meta guarda "
          f"{MAX_FORMULARIOS} y uno nuevo sobrescribe el más antiguo: `crear` para al llegar ahí. "
          "«Cad.» = leads de más de 90 días, ya no descargables.")


def auditar(form: dict) -> list[tuple[str, str]]:
    """Revisión de calidad de un formulario existente (KB 05/02). [(nivel, texto)] con nivel ✗ | ⚠ | ✓."""
    qs = [q for q in form.get("questions") or [] if isinstance(q, dict)]
    tipos = [str(q.get("type") or "") for q in qs]
    opciones = [q for q in qs if q.get("type") == "CUSTOM" and q.get("options")]
    abiertas = [q for q in qs if q.get("type") == "CUSTOM" and not q.get("options")]
    hallazgos: list[tuple[str, str]] = []
    if "is_optimized_for_quality" in form:
        if form.get("is_optimized_for_quality"):
            hallazgos.append(("✓", "mayor intención (pantalla de revisión antes de enviar)"))
        else:
            hallazgos.append(("⚠", "más volumen: si el lead va a una persona, mayor intención filtra envíos "
                                   f"accidentales ({KB_FORMULARIOS} §2)"))
    if not CONTACTO & set(tipos):
        hallazgos.append(("✗", "sin email ni teléfono"))
    if len(opciones) < 2:
        hallazgos.append(("⚠", f"{len(opciones)} preguntas de opción múltiple: con menos de 2–3 el comercial no sabe a "
                               f"quién llamar primero ({KB_FORMULARIOS} §4)"))
    elif len(opciones) > 5:
        hallazgos.append(("⚠", f"{len(opciones)} preguntas de opción múltiple: cada una resta envíos"))
    else:
        hallazgos.append(("✓", f"{len(opciones)} preguntas de opción múltiple para cualificar"))
    if len(abiertas) > 1:
        hallazgos.append(("⚠", f"{len(abiertas)} preguntas de respuesta corta: limítalas a una"))
    for q in qs:
        texto = _norm(f"{q.get('label', '')} {q.get('inline_context', '')}")
        if q.get("type") in ("CUSTOM", "DATE_TIME"):
            for categoria, patron in RESTRINGIDOS:
                if re.search(patron, texto):
                    hallazgos.append(("✗", f"«{q.get('label')}» pide {categoria} (dato restringido; {KB_RESTRINGIDOS})"))
    if "privacy_policy_url" in form and not form.get("privacy_policy_url"):
        hallazgos.append(("✗", "sin política de privacidad"))
    if "tracking_parameters" in form and not form.get("tracking_parameters"):
        hallazgos.append(("⚠", "sin parámetros de seguimiento (oferta, versión) para el CRM"))
    if form.get("block_display_for_non_targeted_viewer") is False:
        hallazgos.append(("⚠", "admite leads orgánicos y compartidos (Compartir = Abierto)"))
    gracias = form.get("thank_you_page") or {}
    if isinstance(gracias, dict) and gracias.get("button_type") in ("NONE", None) and "thank_you_page" in form:
        hallazgos.append(("⚠", "pantalla final sin botón: es el momento de más intención para reservar o abrir "
                               f"WhatsApp ({KB_FORMULARIOS} §6)"))
    if form.get("expired_leads_count"):
        hallazgos.append(("⚠", f"{form['expired_leads_count']} leads caducados (más de 90 días): ya no se descargan; "
                               "el CRM tiene que recibirlos al momento"))
    if form.get("status") == "ARCHIVED":
        hallazgos.append(("⚠", "archivado: no se puede usar en anuncios"))
    if "phone_otp_verification_type" in form or "is_phone_sms_verify_enabled" in form:
        estado = verificacion_leida(form)
        if estado in ("obligatoria", "opcional"):
            hallazgos.append(("✓", f"verifica el teléfono ({estado}; código por WhatsApp o SMS)"))
        elif estado == "desconocida":
            hallazgos.append(("⚠", "Meta no dice si verifica el teléfono (campo vacío: formulario anterior a la "
                                   "v27): míralo en Ads Manager"))
    return hallazgos


def cmd_ver(a: argparse.Namespace) -> None:
    ficha = _ficha(a.cliente)
    pagina = pagina_de(ficha, a.pagina)
    api = conectar_pagina(a.cliente, pagina)
    form, _ = con_campos(lambda f: api.uno(a.id, fields=f), CAMPOS_FORM)
    hallazgos = auditar(form)
    if a.json:
        return _json({"formulario": form, "auditoria": [{"nivel": n, "texto": t} for n, t in hallazgos]})
    print(f"«{form.get('name')}» ({form.get('id')}) · {form.get('status', '')} · {form.get('locale', '')} · creado "
          f"{str(form.get('created_time', ''))[:10]} · leads {form.get('leads_count', '—')}")
    if form.get("context_card"):
        c = form["context_card"]
        print(f"Intro: «{c.get('title', '')}»" if isinstance(c, dict) else f"Intro: {c}")
    for n, q in enumerate(form.get("questions") or [], 1):
        ops = " · ".join(str(o.get("value") or o.get("key")) for o in q.get("options") or [])
        print(f"  {n}. {q.get('type')} {q.get('key', '')}" + (f" · {q.get('label')}" if q.get("label") else "")
              + (f"\n       {ops}" if ops else ""))
    if form.get("thank_you_page"):
        g = form["thank_you_page"]
        print(f"Final: «{g.get('title', '')}» · {g.get('button_type', '')}" + (f" → {g['website_url']}"
                                                                              if g.get("website_url") else ""))
    print(f"Verificación del teléfono: {verificacion_leida(form)}")
    if form.get("tracking_parameters"):
        tp = form["tracking_parameters"]  # la lectura puede devolver {clave: valor} o [{key, value}]: no verificado
        pares = tp.items() if isinstance(tp, dict) else ((x.get("key"), x.get("value")) for x in tp
                                                         if isinstance(x, dict))
        print("Parámetros: " + ", ".join(f"{k}={v}" for k, v in pares))
    print("\nAuditoría (" + KB_FORMULARIOS + "):")
    for nivel, texto in hallazgos:
        print(f"  {nivel} {texto}")


# ---------------------------------------------------------------- leads

def _fechas(a: argparse.Namespace) -> tuple[date, date]:
    try:
        hasta = date.fromisoformat(a.hasta) if a.hasta else date.today() - timedelta(days=1)
        desde = date.fromisoformat(a.desde) if a.desde else hasta - timedelta(days=6)
    except ValueError:
        _salir("Fechas como AAAA-MM-DD.", 1)
    if desde > hasta:
        _salir("--desde es posterior a --hasta.", 1)
    return desde, hasta


def _horario(texto: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d{1,2})-(\d{1,2})", texto or "")
    if not m or not 0 <= int(m.group(1)) < int(m.group(2)) <= 24:
        _salir("--horario como 9-20 (horas de atención, en la zona de la ficha).", 1)
    return int(m.group(1)), int(m.group(2))


def _instante(texto: str) -> datetime | None:
    try:
        return datetime.strptime(str(texto), "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        try:
            dt = datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def respuestas(lead: dict) -> dict[str, str]:
    return {str(x.get("name")): "; ".join(str(v) for v in x.get("values") or [])
            for x in lead.get("field_data") or [] if isinstance(x, dict)}


def mapa_opciones(form: dict) -> dict[str, dict[str, str]]:
    """{clave de pregunta: {valor normalizado (clave o texto de la opción): clave de la opción}} de las preguntas de
    opción múltiple. El lead puede traer la clave o el texto de la opción (no verificado cuál): se casan los dos."""
    salida: dict[str, dict[str, str]] = {}
    for q in form.get("questions") or []:
        if q.get("type") == "CUSTOM" and q.get("options") and q.get("key"):
            salida[str(q["key"])] = {}
            for o in q["options"]:
                clave = str(o.get("key") or o.get("value"))
                for v in (o.get("key"), o.get("value")):
                    if v:
                        salida[str(q["key"])][_norm(v)] = clave
    return salida


def encaje_de(resp_opciones: dict[str, str], reglas: dict[str, set[str]]) -> int | str:
    if not reglas:
        return ""
    """1 si el lead eligió una opción de encaje en todas las preguntas con regla; 0 si no; "" sin reglas."""
    normalizadas = {_norm(k): _norm(v) for k, v in resp_opciones.items()}
    return int(all(normalizadas.get(_norm(q)) in {_norm(o) for o in ops} for q, ops in reglas.items()))


def _guardar_csv(ruta: pathlib.Path, filas: list[dict], columnas: list[str]) -> str:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    return _rel(ruta)


def cmd_leads(a: argparse.Namespace) -> None:
    ficha = _ficha(a.cliente)
    zona = ma._zona(str(ficha.get("zona_horaria") or "UTC"))
    desde, hasta = _fechas(a)
    abre, cierra = _horario(a.horario)
    reglas: dict[str, set[str]] = {}
    if a.encaje:
        reglas = reglas_encaje(lee_plantilla(a.encaje)[0])
    else:
        previo = next((v for v in lee_estado(a.cliente)["formularios"].values() if v.get("id") == a.id), None)
        if previo and previo.get("encaje"):
            reglas = {k: set(v) for k, v in previo["encaje"].items()}
    pagina = pagina_de(ficha, a.pagina)
    api = conectar_pagina(a.cliente, pagina)
    t0 = int(datetime.combine(desde, datetime.min.time(), zona).timestamp())
    t1 = int(datetime.combine(hasta + timedelta(days=1), datetime.min.time(), zona).timestamp())
    try:
        form, _ = con_campos(lambda f: api.uno(a.id, fields=f), ["id", "name", "questions"])
        filtro = [{"field": "time_created", "operator": "GREATER_THAN_OR_EQUAL", "value": t0},
                  {"field": "time_created", "operator": "LESS_THAN", "value": t1}]
        brutos, _ = con_campos(lambda f: list(api.lista(f"{a.id}/leads", fields=f, filtering=filtro, limit=500)),
                               CAMPOS_LEAD)
    except ma.ErrorMeta as e:
        pista = ("\nPara descargar leads, el token necesita leads_retrieval y la Página tiene que dar acceso a clientes "
                 "potenciales a ese usuario o app (docs/guias/formularios.md §2).") if e.salida == 2 else ""
        _salir(f"{e}{pista}", e.salida)
    opciones = mapa_opciones(form)
    orden_preguntas = [str(q.get("key")) for q in form.get("questions") or [] if q.get("key")]
    # Una regla sobre una pregunta que este formulario no tiene dejaría el encaje siempre a 0: se ignora y se avisa.
    presentes = {_norm(k) for k in opciones}
    ignoradas = sorted(q for q in reglas if _norm(q) not in presentes)
    reglas = {q: v for q, v in reglas.items() if _norm(q) in presentes}

    leads = []
    for x in brutos:
        cuando = _instante(x.get("created_time"))
        if cuando is None or not t0 <= cuando.timestamp() < t1:
            continue  # por si el filtro no se aplicara
        r = respuestas(x)
        r_opc = {q: opciones[q].get(_norm(v), "(otra)") for q, v in r.items() if q in opciones}
        local = cuando.astimezone(zona)
        organico = str(x.get("is_organic")).lower() in ("true", "1")
        leads.append({"lead": x, "respuestas": r, "opciones": r_opc, "local": local, "organico": organico,
                      "encaje": encaje_de(r_opc, reglas),
                      "fuera": local.weekday() >= 5 or not abre <= local.hour < cierra})

    # Agregados por anuncio (sin datos personales)
    grupos: dict[str, dict] = {}
    for l in leads:
        x = l["lead"]
        ad = "" if l["organico"] else str(x.get("ad_id") or "")
        g = grupos.setdefault(ad, {"form_id": a.id, "ad_id": ad,
                                   "anuncio": "(orgánico)" if l["organico"] else (x.get("ad_name") or ""),
                                   "campaign_id": x.get("campaign_id") or "", "campana": x.get("campaign_name") or "",
                                   "leads": 0, "organicos": 0, "encaje": 0 if reglas else "", "fuera_horario": 0,
                                   "desde": desde.isoformat(), "hasta": hasta.isoformat()})
        g["leads"] += 1
        g["organicos"] += l["organico"]
        g["fuera_horario"] += l["fuera"]
        if reglas:
            g["encaje"] += l["encaje"]
    por_anuncio = sorted(grupos.values(), key=lambda g: -g["leads"])
    for g in por_anuncio:
        g["encaje_pct"] = round(g["encaje"] / g["leads"] * 100, 1) if reglas and g["leads"] else ""

    reparto: dict[tuple[str, str], Counter] = defaultdict(Counter)
    total_por_ad: Counter = Counter()
    for l in leads:
        ad = "" if l["organico"] else str(l["lead"].get("ad_id") or "")
        total_por_ad[ad] += 1
        for q, op in l["opciones"].items():
            reparto[(ad, q)][op] += 1
            reparto[("TOTAL", q)][op] += 1
    nombres = {g["ad_id"]: g["anuncio"] for g in por_anuncio} | {"TOTAL": "TOTAL"}
    filas_resp = []
    for (ad, q), cuenta in sorted(reparto.items(), key=lambda kv: (kv[0][0] != "TOTAL", kv[0][0], kv[0][1])):
        base = len(leads) if ad == "TOTAL" else total_por_ad[ad]
        for op, n in cuenta.most_common():
            filas_resp.append({"form_id": a.id, "ad_id": ad, "anuncio": nombres.get(ad, ""), "pregunta": q,
                               "respuesta": op, "leads": n, "pct": round(n / base * 100, 1) if base else ""})

    total = len(leads)
    resumen = {"form_id": a.id, "formulario": form.get("name"), "desde": desde, "hasta": hasta, "leads": total,
               "organicos": sum(l["organico"] for l in leads),
               "encaje": sum(l["encaje"] for l in leads) if reglas else None,
               "encaje_pct": round(sum(l["encaje"] for l in leads) / total * 100, 1) if reglas and total else None,
               "fuera_horario": sum(l["fuera"] for l in leads), "horario": f"{abre}-{cierra}",
               "por_dia": dict(sorted(Counter(l["local"].date().isoformat() for l in leads).items())),
               "por_plataforma": dict(Counter(str(l["lead"].get("platform") or "—") for l in leads)),
               "reglas_encaje": {k: sorted(v) for k, v in reglas.items()}, "encaje_ignorado": ignoradas,
               "caducados_en_periodo": (date.today() - desde).days > DIAS_DESCARGA}
    if not a.sin_archivos and leads:
        columnas_preg = orden_preguntas + sorted({k for l in leads for k in l["respuestas"]} - set(orden_preguntas))
        detalle = []
        for l in leads:
            x = l["lead"]
            detalle.append({"leadgen_id": x.get("id", ""), "fecha_hora": l["local"].isoformat(timespec="seconds"),
                            "form_id": a.id, "ad_id": x.get("ad_id") or "", "anuncio": x.get("ad_name") or "",
                            "adset_id": x.get("adset_id") or "", "conjunto": x.get("adset_name") or "",
                            "campaign_id": x.get("campaign_id") or "", "campana": x.get("campaign_name") or "",
                            "plataforma": x.get("platform") or "", "organico": int(l["organico"]),
                            "encaje": l["encaje"], **l["respuestas"]})
        cols = ["leadgen_id", "fecha_hora", "form_id", "ad_id", "anuncio", "adset_id", "conjunto", "campaign_id",
                "campana", "plataforma", "organico", "encaje"] + columnas_preg
        sufijo = f"{a.id}_{desde}_{hasta}"
        cliente = comun.ruta_cliente(a.cliente)
        resumen["csv_privado"] = _guardar_csv(cliente / "privado" / f"formulario-{sufijo}.csv", detalle, cols)
        resumen["csv"] = _guardar_csv(cliente / "datos" / f"formulario-{sufijo}.csv", por_anuncio, COLUMNAS_ANUNCIO)
        resumen["csv_respuestas"] = _guardar_csv(cliente / "datos" / f"formulario-{sufijo}_respuestas.csv",
                                                 filas_resp, COLUMNAS_RESPUESTAS)
    if a.json:
        return _json({**resumen, "por_anuncio": por_anuncio,
                      "respuestas": [f for f in filas_resp if f["ad_id"] == "TOTAL"]})

    print(f"«{form.get('name')}» ({a.id}) · {desde} → {hasta} (zona de la ficha) · {total} leads"
          f" · {resumen['organicos']} orgánicos · {resumen['fuera_horario']} fuera del horario {abre}-{cierra} h o en "
          "fin de semana")
    if resumen["caducados_en_periodo"]:
        print(f"⚠ El periodo empieza hace más de {DIAS_DESCARGA} días: Meta ya no da esos leads; solo el CRM los tiene.")
    if not total:
        print("Sin leads en el periodo.")
        return
    print(f"\n{'Anuncio':<54}{'Leads':>6}{'Encaje':>8}{'Fuera h.':>9}")
    for g in por_anuncio:
        enc = f"{_n(g['encaje_pct'], 1)} %" if g["encaje_pct"] != "" else "—"
        print(f"{(g['anuncio'] or g['ad_id'] or '—')[:53]:<54}{g['leads']:>6}{enc:>8}{g['fuera_horario']:>9}")
    for q in orden_preguntas:
        cuenta = reparto.get(("TOTAL", q))
        if cuenta:
            print(f"\n{q}: " + " · ".join(f"{op} {round(n / total * 100)} %" for op, n in cuenta.most_common()))
    if reglas:
        print(f"\nEncaje declarado: {resumen['encaje']} de {total} ({_n(resumen['encaje_pct'] or 0, 1)} %) según "
              + "; ".join(f"{q} ∈ {{{', '.join(sorted(v))}}}" for q, v in reglas.items())
              + ".\nEs lo que dicen en el formulario, no el cualificado: ese lo marca el comercial y vuelve a Meta "
                "(contrato §16). Cruza con `ghl.py por-anuncio` y `embudo.py cohortes`.")
    else:
        print("\nSin reglas de encaje (--encaje <plantilla.json>): solo se cuentan leads y respuestas.")
    if ignoradas:
        print(f"⚠ El formulario no tiene {', '.join(ignoradas)}: esas reglas de encaje no se aplican (¿plantilla de "
              "otro formulario?).")
    if resumen.get("csv"):
        print(f"\nAgregados (sin datos personales): {resumen['csv']} y {resumen['csv_respuestas']}")
        print(f"Un lead por fila, CON datos personales: {resumen['csv_privado']} (no lo compartas ni lo subas a git)")


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> None:
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--cliente", help="slug del cliente (Página, zona horaria y credenciales de su ficha)")
    comunes.add_argument("--pagina", help="ID de la Página si no es meta.pagina de la ficha")
    comunes.add_argument("--json", action="store_true", help="salida en JSON (sin datos personales)")
    p = argparse.ArgumentParser(description="Formularios instantáneos de Meta: plantillas, creación con confirmación, "
                                            "auditoría y descarga de leads.")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("listar", parents=[comunes], help="formularios de la Página con leads y estado")
    ve = sub.add_parser("ver", parents=[comunes], help="preguntas, final y auditoría de calidad de un formulario")
    ve.add_argument("id", help="ID del formulario")
    cr = sub.add_parser("crear", parents=[comunes], help="crea un formulario desde una plantilla (requiere --confirmo)")
    cr.add_argument("plantilla", help="plantilla JSON (en clientes/<slug>/planes/)")
    cr.add_argument("--simular", action="store_true", help="solo revisa y dibuja la plantilla; no toca Meta")
    cr.add_argument("--confirmo", action="store_true", help="el usuario ha dicho que sí en este momento")
    cr.add_argument("--sin-logica", dest="sin_logica", action="store_true",
                    help="crea el formulario aunque la plantilla tenga lógica condicional (queda fuera)")
    gu = sub.add_parser("guia", parents=[comunes], help="la plantilla paso a paso para montarla en Ads Manager")
    gu.add_argument("plantilla")
    gu.add_argument("--salida", help="guarda la guía en este .md (p. ej. clientes/<slug>/planes/…_formulario.md)")
    le = sub.add_parser("leads", parents=[comunes], help="leads del periodo → privado/ (detalle) y datos/ (agregados)")
    le.add_argument("id", help="ID del formulario")
    le.add_argument("--desde", help="AAAA-MM-DD (por defecto, hace 7 días)")
    le.add_argument("--hasta", help="AAAA-MM-DD (por defecto, ayer)")
    le.add_argument("--encaje", help="plantilla con las opciones marcadas como encaje (por defecto, la de su creación)")
    le.add_argument("--horario", default="9-20", help="horas de atención para contar leads fuera de horario (9-20)")
    le.add_argument("--sin-archivos", dest="sin_archivos", action="store_true", help="no guarda nada (solo agregados)")
    a = p.parse_args(argv)
    if a.comando in ("listar", "ver", "leads") and not a.cliente:
        _salir("Falta --cliente <slug> (la Página y el token salen de su ficha).", 1)
    ordenes = {"listar": cmd_listar, "ver": cmd_ver, "crear": cmd_crear, "guia": cmd_guia, "leads": cmd_leads}
    try:
        ordenes[a.comando](a)
    except ma.ErrorMeta as e:
        _salir(str(e), e.salida)


if __name__ == "__main__":
    main()
