# Event Match Quality, advanced matching, PII y hashing

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: cómo Meta empareja eventos con personas, qué parámetros enviar, cómo normalizar y hashear, cómo leer y subir el EMQ, y qué no hacer con datos sensibles.

## TL;DR

- **EMQ (0–10) mide el potencial de emparejamiento de los parámetros de cliente de un evento, no la tasa real de atribución.** Meta recomienda "6.0 or higher"; se consulta por evento en Events Manager y por API (`event_match_quality.composite_score`). Solo existe para eventos web. [OFFICIAL META] ([S04-056], [S04-016])
- **Prioridad de identificadores (Meta):** email, teléfono, IP, user agent, `fbp`, `fbc`, nombre y apellido son los de mayor peso en EMQ; la guía sGTM de Meta marca email y `fbc` como prioridad "High", teléfono/`external_id`/`fbp`/país/fecha nacimiento "Medium", nombre/ciudad/CP "Low". [OFFICIAL META] ([S04-017], [S04-054]) — Ambas listas son cualitativas; Meta no publica pesos.
- **Normaliza → hashea SHA-256 (hex)** para `em, ph, fn, ln, db, ge, ct, st, zp, country` (y recomendado `external_id`). **No hashees** `fbc, fbp, client_ip_address, client_user_agent, lead_id, anon_id, madid, ctwa_clid, page_scoped_user_id`. [OFFICIAL META] ([S04-006])
- **Advanced matching automático** (Pixel lee campos de formulario) y **manual** (`fbq('init', id, {em, ph, …})`, el Pixel hashea) se suman; en CAPI siempre es "manual". [OFFICIAL META] (doc. Advanced Matching)
- **Las mejoras de EMQ con mayor retorno suelen ser:** enviar email+teléfono también en eventos anteriores a la compra cuando el usuario está identificado (logged-in), `fbc` construido desde `fbclid`, IP/UA del usuario en CAPI (IPv6 cuando el Pixel la ve), y `external_id` consistente. [OFFICIAL META] (diagnósticos IPv6, [S04-016]) + [EMPIRICAL]
- **El tag oficial de Meta para sGTM normaliza el teléfono con `.replace()` de cadena**, que solo elimina la primera aparición de `+`, `-`, espacio y paréntesis: un teléfono como `+34 612-34-56-78` llega mal normalizado. Normaliza el teléfono **antes** de enviarlo al servidor. [STRONG INFERENCE] por inspección del código ([S04-081])
- **Nunca envíes datos de salud, financieros u otros sensibles en parámetros, URLs o nombres de evento.** Las restricciones de Meta (core setup, bloqueo de eventos) se aplican igual a Pixel y CAPI. [OFFICIAL META] (términos de Business Tools, no verificado el texto literal) + [EMPIRICAL] ([S04-082])

## 1. Qué es (y qué no es) el EMQ

- **Es:** una estimación, por evento, de "lo efectivos que pueden ser los parámetros de información de cliente del evento para emparejarlo con una cuenta de Meta". Escala 1–10 en Events Manager; la API la llama `composite_score` y se calcula en tiempo real. [OFFICIAL META] ([S04-056], [S04-016])
- **No es:** el % de eventos emparejados, ni el % de conversiones atribuidas, ni un factor directo de puja. Un EMQ alto con `fbc` ausente puede atribuir poco clic; un EMQ medio con `fbc` en casi todos los Purchase puede atribuir bien. [STRONG INFERENCE]
- **Por qué importa:** "solo los eventos emparejados se pueden usar para atribución y optimización de entrega"; Meta afirma que un EMQ alto "puede ayudar a reducir el coste por acción". [OFFICIAL META] ([S04-010], [S04-056])
- **Desglose disponible por API** (`match_key_feedback`): cobertura (%) por identificador (`email`, `external_id`, `ip_address`, `user_agent`, …), `potential_aly_acr_increase` por clave (incremento estimado de conversiones reportadas si mejoras esa clave) y `diagnostics` con problema, solución, % y eventos afectados. [OFFICIAL META] ([S04-016])

```bash
curl -G "https://graph.facebook.com/v25.0/dataset_quality" \
  -d "dataset_id=DATASET_ID" \
  -d "access_token=TOKEN" \
  --data-urlencode "fields=web{event_name,event_match_quality{composite_score,match_key_feedback{identifier,coverage,potential_aly_acr_increase},diagnostics},event_coverage{percentage,goal_percentage},dedupe_key_feedback,data_freshness{upload_frequency}}"
```

(Estructura de campos según la documentación de la Dataset Quality API; el parámetro opcional `agent_name` filtra por `partner_agent`.) [OFFICIAL META] ([S04-016])

## 2. Tabla de normalización por campo (antes del hash)

| Clave | Normalización | Ejemplo entrada → normalizado | Hash |
|---|---|---|---|
| `em` | trim + minúsculas | ` John_Smith@Gmail.com ` → `john_smith@gmail.com` | Sí |
| `ph` | solo dígitos, **con prefijo de país**, sin `+`, sin `00`, sin ceros iniciales nacionales | `+34 612 34 56 78` → `34612345678`; `(650)555-1212` (US) → `16505551212` | Sí |
| `fn`, `ln` | minúsculas, sin puntuación; caracteres especiales en UTF-8 (Meta prefiere a–z romano pero acepta UTF-8) | `Valéry` → `valéry` | Sí |
| `ge` | `f` o `m` | `Female` → `f` | Sí |
| `db` | `YYYYMMDD` | `2/16/1997` → `19970216` | Sí |
| `ct` | minúsculas, sin espacios ni puntuación | `New York` → `newyork` | Sí |
| `st` | EE. UU.: código ANSI 2 letras en minúsculas; fuera: minúsculas sin espacios/puntuación | `California` → `ca` | Sí |
| `zp` | minúsculas, sin espacios ni guiones; EE. UU. solo 5 dígitos | `94035-1234` → `94035`; `M1 1AE` → `m11ae` | Sí |
| `country` | ISO 3166-1 alpha-2 en minúsculas (enviar **siempre**, aunque todo el tráfico sea de un país) | `Spain` → `es` | Sí |
| `external_id` | Tu ID estable; mismo formato en todos los canales | `cust_12345` | Recomendado |
| `client_ip_address` | IPv4/IPv6 válida, real, sin espacios | `2001:db8::1` | **No** |
| `client_user_agent` | UA completo | — | **No** |
| `fbc`, `fbp` | Tal cual (case-sensitive) | — | **No** |

Fuente: [OFFICIAL META] ([S04-006]). El Pixel acepta email en claro en minúsculas o ya hasheado. [OFFICIAL META] (doc. Advanced Matching del Pixel)

**Reglas de hash:** SHA-256 de la cadena UTF-8 normalizada, salida hexadecimal en minúsculas (64 caracteres). Detecta si ya viene hasheado (`/^[a-f0-9]{64}$/i`) para no hashear dos veces — es exactamente lo que hace el tag oficial de sGTM (`isAlreadyHashed`). [OFFICIAL META] ([S04-081])

**Vectores de prueba** (útiles para tests unitarios de tu función):
- `john_smith@gmail.com` → `62a14e44f765419d10fea99367361a727c12365e2520f32218d505ed9aa0f62f` (coincide con el ejemplo de Meta). [OFFICIAL META] ([S04-053])
- `16505551212` → `e323ec626319ca94ee8bff2e4c87cf613be6ea19919ed1364124e16807ab3176` (coincide con el ejemplo de Meta). [OFFICIAL META] ([S04-053])

### 2.1 Python de referencia

```python
import hashlib, re, unicodedata

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def is_hashed(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Fa-f0-9]{64}", s or ""))

def norm_email(v): return v.strip().lower()

def norm_phone(v, cc="34"):
    d = re.sub(r"\D", "", v)          # elimina TODOS los no dígitos
    d = re.sub(r"^00", "", d)
    if len(d) <= 9:                   # número nacional (ajusta la regla a tu país)
        d = cc + d.lstrip("0")
    return d

def norm_name(v):
    v = unicodedata.normalize("NFC", v.strip().lower())
    return re.sub(r"[\s'’.,\-]", "", v)

def hashed(v, norm):
    if not v: return None
    return v.lower() if is_hashed(v) else sha256(norm(v))

assert hashed("John_Smith@gmail.com", norm_email) == \
  "62a14e44f765419d10fea99367361a727c12365e2520f32218d505ed9aa0f62f"
assert hashed("16505551212", lambda x: norm_phone(x, cc="1")) == \
  "e323ec626319ca94ee8bff2e4c87cf613be6ea19919ed1364124e16807ab3176"
```

`unicodedata.normalize("NFC")` evita que `é` compuesto vs descompuesto genere hashes distintos entre canales (inferencia técnica; Meta solo pide UTF-8). [STRONG INFERENCE]

## 3. Advanced matching en el Pixel

### 3.1 Automático
- Se activa en Events Manager (Settings del dataset). El Pixel detecta campos de formulario (email, teléfono, nombre…) y los envía hasheados. [OFFICIAL META] (doc. Advanced Matching del Pixel, enlaza a Help Center 1993001664341800)
- Pros: sin código. Contras: depende de que el formulario esté en la misma página que el evento, de selectores estándar y del consentimiento; con *core setup* activo puede dejar de funcionar. [EMPIRICAL] ([S04-083])

### 3.2 Manual
```js
fbq('init', 'PIXEL_ID', {
  em: 'john_smith@gmail.com',      // en claro (minúsculas) o SHA-256
  ph: '34612345678',
  fn: 'valéry', ln: 'dupont',
  ct: 'madrid', zp: '28001', country: 'es',
  external_id: 'cust_12345'
});
```
- Debe ir en el `init` del código base. En usuarios logueados, inyecta los datos en todas las páginas: así `ViewContent`/`AddToCart` también tienen buen EMQ (no solo Purchase). [OFFICIAL META] + [STRONG INFERENCE]
- Image pixel: `ud[em]=<sha256>` con valores ya hasheados. [OFFICIAL META]

## 4. Cómo subir el EMQ (por orden de impacto esperado)

1. **`fbc` en el máximo de eventos:** captura `fbclid` en servidor en la primera petición y persístelo (sesión/carrito/usuario); construye `fbc` si no hay cookie. Revisa redirecciones que pierden la query. [OFFICIAL META] ([S04-007]) + [STRONG INFERENCE]
2. **Email y teléfono** en todos los eventos donde el usuario esté identificado (login, checkout por pasos, lead). Pide teléfono con prefijo de país en el formulario.
3. **IP y UA del usuario** en CAPI (no del servidor). Si el Pixel ve IPv6 y tu servidor solo IPv4 (por proxy/CDN), Meta lo marca como diagnóstico: usa la Parameter Builder Library, que captura IPv6 en cliente y la pasa al servidor por cookie. [OFFICIAL META] ([S04-016], [S04-011])
4. **`fbp` en CAPI** leyendo la cookie del request (o pasándola desde el cliente).
5. **`external_id`** estable (ID de cliente/CRM), idéntico en Pixel, CAPI y app. Meta reutiliza la asociación `external_id`→usuario cuando ya hizo match con PII en otro evento (la asociación caduca periódicamente; refrescarla con frecuencia). Si no envías `external_id`, Meta usa `fbp` como tal. [OFFICIAL META] ([S04-055])
6. **Dirección** (`ct`, `st`, `zp`, `country`) y `db`/`ge` solo si los tienes con calidad; aportan poco por sí solos y ciertas combinaciones aisladas se rechazan. [OFFICIAL META] ([S04-010])

## 5. PII: qué está prohibido o es arriesgado

- **No enviar en claro** contacto por CAPI (se rechaza). [OFFICIAL META] ([S04-006])
- **No poner PII en URLs** (`?email=…` en thank-you pages o formularios GET): el Pixel envía la URL. Meta muestra avisos de "potentially violating data" en Events Manager y puede filtrar. [EMPIRICAL] — revisa Diagnostics.
- **Categorías sensibles** (salud, condiciones médicas, finanzas personales, orientación sexual, etc.): no deben viajar en `content_name`, `content_category`, parámetros custom, nombres de evento ni rutas de URL. En 2025 Meta empezó a clasificar fuentes de datos por categoría y a aplicar *core setup* o bloqueo de eventos (ver archivo 09). [EMPIRICAL] ([S04-082], [S04-083])
- **Hash ≠ anonimización** a efectos regulatorios: un email hasheado sigue siendo dato personal pseudonimizado en la UE (no es consejo jurídico; consulta a tu DPO). [STRONG INFERENCE]

## 6. Advanced matching en plataformas

| Plataforma | Cómo se envía PII |
|---|---|
| Shopify (app Facebook & Instagram) | Niveles Enhanced/Maximum comparten nombre, ubicación, email, teléfono vía CAPI; Standard solo Pixel. [OFFICIAL Shopify] ([S04-031]) |
| Meta for WooCommerce | Pixel + CAPI con Param Builder; PII del pedido en Purchase. [OFFICIAL META] ([S04-035]) |
| sGTM con tag oficial | Lee `user_data.email_address`, `phone_number`, `address.*` del evento GA4 o claves `x-fb-ud-*`; hashea si no viene hasheado; **phone mal normalizado si llega con varios separadores**. [OFFICIAL META] ([S04-054], [S04-081]) |
| CAPI Gateway | "Enhance events with additional user data" (advanced matching del Pixel reenviado). [OFFICIAL META] (índice de docs Gateway) |

## Implicaciones operativas

- **Hacemos:** una única librería de normalización/hash compartida por web, backend y CRM, con tests de vectores conocidos; prefijo de país en teléfonos desde el formulario; `fbc` persistido; IP/UA reales; `external_id` = ID de cliente estable; monitorización de `match_key_feedback` mensual.
- **Evitamos:** hashear en dos sitios; normalizaciones "creativas" (quitar acentos en un canal y no en otro); enviar email en URLs; meter datos sensibles en parámetros.
- **Umbrales:** EMQ Purchase < 6 = incidencia; 6–8 = mejorable; ≥ 8 = bueno [EMPIRICAL]. Cobertura de `fbc` en Purchase atribuibles a Meta muy por debajo del % de tráfico pagado de Meta = pérdida de click ID.

## Errores frecuentes

1. Teléfono sin prefijo país (`612345678`) → hash distinto del que Meta tiene.
2. Email con mayúsculas o espacios antes del hash.
3. Hashear `fbc`/`fbp`/IP.
4. Usar el sGTM tag oficial con teléfonos tal como los escribe el usuario (ver bug de `.replace()`).
5. Advanced matching automático + manual + CAPI con normalizaciones distintas → el mismo usuario parece tres.
6. Creer que subir EMQ de 6 a 9 "multiplica" resultados: el efecto existe pero es acotado y depende de cuántas conversiones estaban sin emparejar. [STRONG INFERENCE]

## Preguntas abiertas

- Pesos reales de cada identificador en el EMQ y cómo se combinan (no publicado).
- Si el EMQ influye directamente en la entrega o solo indirectamente vía más eventos emparejados (Meta solo dice que "puede ayudar a reducir el CPA").
- Fecha de corrección del bug de normalización de teléfono en el tag oficial de sGTM (no verificado si hay issue abierto).

## Fuentes clave

- [Customer Information Parameters](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/customer-information-parameters) — vigente — meta-developers (S04-006)
- [Dataset Quality API](https://developers.facebook.com/docs/marketing-api/conversions-api/dataset-quality-api) — 2025-05-28 — meta-developers (S04-016)
- [Verifying Your Setup](https://developers.facebook.com/documentation/ads-commerce/conversions-api/verifying-setup) — vigente — meta-developers (S04-056)
- [External ID](https://developers.facebook.com/documentation/ads-commerce/conversions-api/parameters/external-id) — vigente — meta-developers (S04-055)
- [Parameter Builder Library](https://developers.facebook.com/docs/marketing-api/conversions-api/parameter-builder-feature-library) — vigente — meta-developers (S04-011)
- [Conversions API for Server-Side GTM](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/gtm-server-side) — vigente — meta-developers (S04-054)
- [ConversionsAPI-Tag-for-GoogleTagManager (código)](https://github.com/facebookincubator/ConversionsAPI-Tag-for-GoogleTagManager) — 2026-06 — meta-developers (S04-081)
- [Omni Optimal Setup Guide](https://developers.facebook.com/documentation/ads-commerce/marketing-api/best-practices/omni-optimal-setup-guide) — vigente — meta-developers (S04-017)
