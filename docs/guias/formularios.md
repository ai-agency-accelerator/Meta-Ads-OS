# Formularios instantáneos de Meta, paso a paso

Para quién: consultoras, agencias y SaaS que venden servicios o proyectos a medida a pymes y captan con formularios
instantáneos (Lead Ads). Qué consigues: un formulario que filtra antes de la llamada, creado sin errores (por API o a
mano en Ads Manager), conectado a GoHighLevel, con sus etapas de vuelta a Meta, y una lectura de la calidad de sus
leads por anuncio.

La skill que lo guía es `/formulario-instantaneo`. Las etiquetas `[OFFICIAL META]`, `[EMPIRICAL]`, `[CONTESTED]`… son
las de la base de conocimiento. «No verificado» quiere decir que no se ha podido comprobar en la documentación oficial
el 2026-11-09: compruébalo en tu pantalla.

```
plantilla JSON ──crear --simular──▶ revisión sin red ──revisor-politicas──▶ crear --confirmo (API)  ┐
                                                                        └▶ guia (Ads Manager)       ┘─▶ formulario (sin usar)
formulario ──formulario_id en el plan──▶ meta_ads.py crear (anuncio en pausa) ──▶ leads ──▶ GHL ──etapas CAPI──▶ Meta
leads ──formularios_meta.py leads──▶ privado/ (detalle) + datos/ (agregados por anuncio)
```

---

## 1. Antes de diseñar: qué tipo y para qué

| Tipo | Qué hace | Cuándo `[OFFICIAL META]` + criterio de la KB |
|---|---|---|
| **Más volumen** (*More volume*) | Envío rápido, se puede rellenar con dos toques | Recursos, talleres, listas de espera: el lead se nutre antes de hablar con nadie |
| **Mayor intención** (*Higher intent*) | Añade contexto bajo los datos de contacto y una pantalla para revisarlos antes de enviar. **Solo se entrega en el Feed de Facebook e Instagram en móvil**, no en ordenador | Diagnóstico o llamada: el lead va a una persona. Es el tipo por defecto en venta consultiva |
| **Creatividad enriquecida** (*Rich creative*) | Intro con imágenes y más contenido | Cuando hay que enseñar más antes de preguntar. **Solo en Ads Manager** (no hay parámetro en la API) |

Base: `meta-ads-kb/05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md` §2 y
`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §5.2. En anuncios de colaboración con un creador,
el formulario se muestra en formato «greeting card» `[OFFICIAL META]` (el nombre exacto de la opción en Ads Manager no
está verificado): revisa la vista previa en ese formato.

## 2. Token y permisos

Crear un formulario es una llamada a la **Página**, no a la cuenta publicitaria: `POST /{pagina}/leadgen_forms` con un
**token de la Página** de alguien que tenga en ella la tarea de crear anuncios `[OFFICIAL META]` (referencia de
`leadgen_forms`). La herramienta lo resuelve de dos formas, sin imprimir nunca el token:

1. **Token del usuario del sistema** (`META_TOKEN_<SLUG>` o `META_TOKEN`, el de `docs/guias/token-avanzado.md`). La
   herramienta pide a Meta el token de la Página con él. Para que funcione:
   - en Business Settings → Usuarios del sistema → *Asignar activos*, la **Página** con la tarea de **crear anuncios**;
   - al generar el token, además de los permisos de esa guía, **`pages_manage_ads`** (crear formularios) y
     **`leads_retrieval`** (descargar leads). La referencia pide `ads_management`, `pages_manage_ads`,
     `pages_read_engagement` y `pages_show_list` para crear, y `leads_retrieval` además para leer leads.
     `[OFFICIAL META]`
2. **Token de la Página directamente** en `.env`: `META_TOKEN_PAGINA_<SLUG>=...` (o `META_TOKEN_PAGINA`). Útil si el
   usuario del sistema no puede tener la Página. Pégalo tú en `.env`, nunca en el chat.

**Leer leads** necesita además el **acceso a clientes potenciales**: Business Settings → Integraciones → *Acceso a
clientes potenciales* (*Leads Access*) → la Página → da acceso al usuario del sistema o a su app. Si alguien lo
restringió, Meta devuelve un error de permisos (salida 2) aunque el token sea correcto `[OFFICIAL META]`.

La Página va en la ficha (`meta.pagina`; sácala con `meta_ads.py activos`). Para comprobarlo todo sin cambiar nada:

```
python3 -I herramientas/formularios_meta.py listar --cliente acme
```

Si lista los formularios de la Página, el token sirve para crear y para auditar.

**El MCP oficial de Meta no tiene herramientas de formularios ni de leads** (comprobado el 2026-11-09 en la lista de
herramientas del Ads MCP server). Por eso esto va por la Graph API o a mano.

## 3. API o Ads Manager

| Función | Por API (`crear`) | En Ads Manager (`guia`) |
|---|---|---|
| Más volumen o mayor intención | Sí (`is_optimized_for_quality`) | Sí |
| Creatividad enriquecida | No | Sí |
| Opción múltiple, respuesta corta, fecha y hora, prellenadas | Sí | Sí |
| Intro, titular de preguntas, privacidad, aviso legal con casillas, parámetros de seguimiento | Sí | Sí |
| **Lógica condicional** (otra pregunta u otro final según la respuesta) | **No documentada**: `crear` se niega salvo `--sin-logica` | Sí |
| **Exigir email de trabajo** | Sí (`should_enforce_work_email`) | Según Meta, solo se aplica en Instagram o por API (anuncio del 2025-10-30) |
| Verificar el teléfono (código por WhatsApp o SMS; lo elige Meta) | Sí (`phone_otp_verification_type` desde la v27.0; antes, `is_phone_sms_verify_enabled`) | Sí |
| **Reserva embebida** (*Book time*) | No verificado qué botón la activa: va como enlace al calendario | Sí |
| Editar después de publicar | No: se duplica con otro nombre | No: se duplica |

Si quieres a la vez lógica condicional y email de trabajo exigido, elige: lógica (Ads Manager) o email de trabajo
(API). En una pyme pequeña suele ganar la lógica: muchas usan correos personales (playbook §5.2).

## 4. La plantilla

Las tres de `.claude/skills/formulario-instantaneo/plantillas/` (diagnóstico corto, llamada cualificada, recurso o
taller) están en español de España y explican en `_leeme` qué adaptar. Copia una a `clientes/<slug>/planes/` y edítala.
Las claves que empiezan por `_` se ignoran.

| Clave | Qué es | En la API |
|---|---|---|
| `nombre` | Nombre del formulario en la Página (`<cliente>_<oferta>_v1`). Una versión nueva, un nombre nuevo | `name` |
| `tipo` | `mas_volumen` · `mayor_intencion` · `creatividad_enriquecida` (solo `guia`) | `is_optimized_for_quality` |
| `idioma` | `ES_ES` por defecto (`ES_LA`, `EN_US`, `PT_BR`…) | `locale` |
| `intro` | `titulo`, `estilo` (`lista` o `parrafo`), `contenido` (lista de textos), `boton` | `context_card` |
| `titular_preguntas` | Titular de la página de preguntas | `question_page_custom_headline` |
| `preguntas[]` | `clave`, `tipo`, `texto`, `ayuda`, `opciones[{clave, texto}]`, `encaje` (claves de opción), `exigir_email_trabajo` | `questions` |
| `verificar_telefono` | Código de un solo uso al teléfono: `true` u `"obligatorio"`, `"opcional"` (la persona puede saltarlo) o `false` / `"no"` | v27.0 o posterior: `phone_otp_verification_type` (`OTP_REQUIRED`, `OTP_OPTIONAL` con `ad_account_id`, `NOT_ENABLED`); con `META_API_VERSION` anterior, `is_phone_sms_verify_enabled` (sin modo opcional) |
| `privacidad` | `url` (https, obligatoria) y `texto_enlace` (≤70 caracteres) | `privacy_policy` |
| `aviso_legal` | `titulo`, `texto`, `casillas[{clave, texto, obligatoria}]` (siempre sin marcar por defecto) | `custom_disclaimer` |
| `final` | `titulo`, `texto`, `boton`, `texto_boton`, `url`, `telefono`, `pais` | `thank_you_page` (+ `follow_up_action_url`) |
| `finales_alternativos` + `logica` | Finales para quien no encaja y las reglas `{si: {pregunta, respuesta}, ir_a: "final:<clave>"}` | — (solo Ads Manager) |
| `parametros` | Pares clave-valor que llegan con cada lead (oferta, formulario, versión) | `tracking_parameters` |
| `solo_anuncios` | `true` por defecto: sin leads orgánicos ni compartidos | `block_display_for_non_targeted_viewer` |
| `revision_politicas` | Veredicto de `revisor-politicas` (tabla del contrato §6) | — |
| `api` | Parámetros de la API sin traducir, para lo que no cubre la plantilla (nunca `status`) | tal cual |

Tipos de pregunta: `opciones` y `texto` (personalizadas), `fecha_hora`, y las prellenadas `nombre_completo`, `nombre`,
`apellidos`, `email`, `email_trabajo`, `telefono`, `telefono_trabajo`, `whatsapp`, `empresa`, `cargo`, `web`,
`ciudad`, `provincia`, `codigo_postal`, `pais`. Botones del final: `web`, `reservar`, `descargar`, `llamar`,
`whatsapp`, `ninguno`.

Qué para la revisión (`crear --simular`), además de lo obvio (claves repetidas, opciones sueltas, URLs sin https):

- **Datos restringidos** en preguntas personalizadas: ingresos, patrimonio o deudas de la persona, salud, DNI o
  pasaporte, antecedentes, seguros, ideología o afiliación, raza, religión, orientación sexual, usuarios o contraseñas
  (`meta-ads-kb/08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md`). La lista de la herramienta no
  es exhaustiva: el veredicto es de `revisor-politicas`.
- Más de 15 preguntas personalizadas `[OFFICIAL META]`, ningún dato de contacto, verificar el teléfono sin pregunta de
  teléfono.
- Avisa (no para): facturación (zona gris: de la empresa y en rangos), dinero formulado sobre la persona y no sobre el
  proyecto, una personalizada que repite una prellenada, más de una respuesta corta, más de 5 de opción múltiple.

## 5. Crear, enlazar y probar

1. **Revisa sin red** hasta que no haya errores:
   ```
   python3 -I herramientas/formularios_meta.py crear clientes/acme/planes/2026-11-09_formulario-diagnostico.json --simular --cliente acme
   ```
2. **Políticas:** `/revisar-anuncio` sobre todos los textos; apunta el veredicto en `revision_politicas`.
3. **Crea** (solo `operador-meta`, tras el sí del usuario a ese formulario):
   ```
   python3 -I herramientas/formularios_meta.py crear clientes/acme/planes/2026-11-09_formulario-diagnostico.json --cliente acme --confirmo
   ```
   La herramienta comprueba que la Página no tenga ya un formulario con ese nombre, lo crea, lo apunta en
   `logs/cambios.jsonl` y en `clientes/acme/planes/formularios.json`, lo relee para ver que Meta guardó lo enviado e
   imprime la fila del change log. Repetirlo no duplica nada. Sin `--confirmo` no toca Meta.
   **O móntalo a mano:** `formularios_meta.py guia <plantilla> --cliente acme --salida clientes/acme/planes/2026-11-09_formulario-diagnostico.md`.
4. **Enlázalo:** el ID va al plan de campaña, en el conjunto con `"destino": "formulario"` y `"formulario_id"`, y lo
   crea `meta_ads.py crear` (en pausa). En la API, el anuncio de formulario usa el enlace `https://fb.me/` y un botón
   con `lead_gen_form_id`, y el conjunto optimiza a `LEAD_GENERATION` o, con datos del CRM, a `QUALITY_LEAD`
   `[OFFICIAL META]` (guía de creación de lead ads).
5. **Lead de prueba** con la herramienta de Meta: developers.facebook.com/tools/lead-ads-testing → Página → formulario →
   crear lead (si ya hay uno de prueba, bórralo antes: solo admite uno por formulario `[OFFICIAL META]`). Comprueba en
   GHL, en menos de un minuto: el contacto con sus respuestas, el *Facebook Lead ID*, el anuncio en su campo y el
   workflow disparado (`docs/guias/ghl-meta.md` §2). Con la CAPI de CRM ya montada, la primera etapa debe aparecer en
   *Probar eventos* (§4 de esa guía).
6. **Vista previa en el móvil** desde Ads Manager antes de activar nada.

## 6. Reserva dentro del formulario y etapas

- **Book time** pone un calendario en la pantalla final con nombre, email y teléfono ya rellenados `[OFFICIAL META]`
  (Help Center, leído el 2026-11-09):
  - solo con el enlace directo del partner (Calendly o LeadConnector/HighLevel), no con una URL propia;
  - **solo se embebe en la app de Facebook para móvil**; en Instagram, el botón abre el navegador dentro de la app;
  - **las reservas no se reportan en Ads Manager**: se ven en el calendario. Devuélvelas desde GHL como `Schedule`,
    desde una sola fuente (`docs/guias/ghl-meta.md` §5).
- Etapas del contrato §16 que devuelve GHL: `lead` → `Lead`, `diagnostico` → `DiagnosticoCompletado`, `cualificado` →
  `LeadCualificado`, `llamada` → `Schedule`, `asistio` → `LlamadaAsistida`, `propuesta` → `PropuestaEnviada`,
  `ganado` → `Purchase` con valor y moneda. Lo monta `/implementar-capi`.
- **Conversion Leads** (optimizar a leads cualificados): desde abril de 2026 no se pueden crear campañas nuevas sin la
  CAPI del CRM; hace falta el Lead ID en el CRM, subir datos a diario y una etapa objetivo en ≤28 días con el 1–40 % de
  los leads `[OFFICIAL META]`. El volumen mínimo y el origen de los leads están en disputa entre páginas oficiales
  `[CONTESTED]`: tabla completa y cuándo dar el paso en el playbook §6.

## 7. Leer los leads y su calidad

```
python3 -I herramientas/formularios_meta.py leads <form_id> --cliente acme --desde 2026-11-02 --hasta 2026-11-08
```

- Por defecto, los últimos 7 días completos hasta ayer, en la zona horaria de la ficha.
- Escribe un lead por fila **con datos personales** en `clientes/acme/privado/formulario-<form_id>_<desde>_<hasta>.csv`
  y, **sin datos personales**, `datos/formulario-…csv` (leads, orgánicos, encaje y fuera de horario por anuncio) y
  `datos/formulario-…_respuestas.csv` (reparto de las respuestas de opción múltiple por anuncio). Las respuestas
  abiertas nunca salen de `privado/`. `--sin-archivos` no guarda nada; `--json` nunca incluye datos personales.
- **Encaje declarado**: el lead eligió opciones marcadas como `encaje` (de la plantilla con `--encaje` o, si se creó
  con la herramienta, de su registro). Es una señal del formulario, **no** el `cualificado`: ese lo marca el comercial
  y es lo que manda (`meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md` §4). Cruza con
  `ghl.py por-anuncio --campo-anuncio <id>` y `embudo.py cohortes --por anuncio`.
- `--horario 9-20` cuenta los leads que llegaron fuera de horario o en fin de semana: es donde se pierde el
  *speed to lead* (`meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md`).
- **Meta solo guarda los leads 90 días** y no deja descargar nada anterior `[OFFICIAL META]`. GHL los recibe al
  momento; descarga aquí al menos una vez por semana como respaldo y para el reparto de respuestas.
- No es una escritura en Meta: no se apunta en `logs/cambios.jsonl`.

Para un formulario heredado: `formularios_meta.py ver <form_id> --cliente acme` enseña sus preguntas y lo audita contra
la KB (tipo, preguntas de cualificación, datos restringidos, privacidad, parámetros, final sin botón, leads caducados).

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Salida 2: «no recibe el token de la Página» | La Página no está asignada al usuario del sistema o falta `pages_manage_ads` / `pages_read_engagement` | §2; o pon `META_TOKEN_PAGINA_<SLUG>` |
| Salida 2 al descargar leads | Falta `leads_retrieval` o el acceso a clientes potenciales | §2, «Leer leads» |
| «La Página ya tiene un formulario …» | Ya existe uno con ese `nombre` (quizá creado a mano) | Si es otro, cambia `nombre` (`_v2`); si es el mismo, usa su ID |
| Meta rechaza la creación | Un campo que la API no acepta (el mensaje de Meta lo dice) | Corrige la plantilla; si es un parámetro nuevo, prueba con `api` |
| «Al releerlo: preguntas …» | Meta guardó otra cosa de lo enviado | Revísalo en Ads Manager antes de enlazarlo |
| Los leads no llegan a GHL | Página desconectada en GHL o LeadConnector sin acceso a clientes potenciales | `docs/guias/ghl-meta.md` §2 |
| Respuestas «(otra)» en el reparto | La respuesta no casa con la clave ni con el texto de ninguna opción (formulario distinto de la plantilla) | Pasa la plantilla correcta con `--encaje`; mira el CSV privado |
| «Mayor intención» apenas entrega | Solo sale en el Feed de Facebook e Instagram en móvil | Deja las ubicaciones en Advantage+; no fuerces ordenador |
| Muchos leads sin verificar el teléfono | Quien no verifica no cuenta como lead; un fijo no puede verificarse | Si el ICP usa fijos, quita `verificar_telefono` |

## Qué no está verificado (2026-11-09)

- Cómo se manda por API la **lógica condicional** (hay campos `conditional_questions_group_id` y
  `dependent_conditional_questions` sin documentar): por eso `crear` no la envía.
- Qué `button_type` activa la reserva embebida por API (`SCHEDULE_APPOINTMENT` o `BOOK_ON_WEBSITE` existen en la
  referencia, sin explicar): la plantilla usa `VIEW_WEBSITE` con el enlace al calendario.
- Si `field_data` de un lead devuelve la clave o el texto de la opción elegida: la herramienta casa los dos.
- Si `country_code` de la pantalla final es obligatorio siempre (la referencia lo marca así; la herramienta lo envía).
- Si el botón `DOWNLOAD` obliga a subir el archivo al formulario: la plantilla de recurso usa un botón web.
- Los campos de lectura de un formulario (`leads_count`, `expired_leads_count`, `block_display_for_non_targeted_viewer`…)
  y de un lead (`ad_name`, `campaign_name`, `is_organic`, `platform`) no están todos en la referencia oficial: si Meta
  rechaza uno, la herramienta lo quita y repite.
- La disponibilidad global de *Book time* (la prensa la anunció para octubre de 2026; la página oficial no la
  confirma) y el agente de IA o las «respuestas preferidas» dentro del formulario (en prueba según practitioners).
- Qué cuentas publicitarias son elegibles para la verificación opcional (`OTP_OPTIONAL` exige un `ad_account_id`
  elegible, sin decir cuál) y en qué formato va ese ID: la herramienta manda el número de `meta.cuenta` sin `act_`. Si
  Meta lo rechaza, usa `"obligatorio"` o `"no"`.
- Con una `META_API_VERSION` anterior a la v27.0: si `is_phone_sms_verify_enabled` (el nombre es de cuando el código
  solo iba por SMS) activa también el envío por WhatsApp que describe hoy el Help Center.
- Al leer formularios creados antes de la v27.0, `phone_otp_verification_type` puede venir vacío (`null`): `ver` lo
  enseña como «desconocida» y entonces mira `is_phone_sms_verify_enabled` o la pantalla de Ads Manager.

## Fuentes

- Referencia `Page/leadgen_forms` (parámetros de creación): developers.facebook.com/docs/graph-api/reference/page/leadgen_forms/
- Guías de lead ads de la Marketing API (crear, preguntas, leer leads, pruebas):
  developers.facebook.com/documentation/ads-commerce/marketing-api/guides/lead-ads/create.md, …/retrieving.md,
  …/testing-troubleshooting.md y developers.facebook.com/docs/marketing-api/guides/lead-ads/forms-questions
- Herramientas del Ads MCP server: developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-tools.md
- Help Center (leído el 2026-11-09): formularios de mayor intención (252352181957512), verificación del teléfono
  (898260175547909), reserva embebida (1743939330255391), 90 días de descarga (734933888443065), Conversion Leads
  (782657799338685); anuncio de Meta del 2025-10-30 (facebook.com/business/news/more-quality-leads-this-q5-with-metas-latest-ai-enabled-updates).
