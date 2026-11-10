---
name: implementar-capi
description: "Construye la señal de vuelta a Meta: mapa de eventos, píxel con event_id y Conversions API desde GHL (Allow multiple, Purchase con valor), n8n, Make, Stripe o backend, y de mensajería (Click to WhatsApp con ctwa_clid, Messenger, Instagram); hashing, deduplicación, prueba solo con test_event_code y verificación en el dataset."
argument-hint: "<cliente> [web|ghl|n8n|make|stripe|backend|mensajeria]"
---

# /implementar-capi

Entrada: `$ARGUMENTS` (cliente y, opcionalmente, la vía). Construir esta señal es también un servicio que una agencia
de automatización puede vender a sus clientes.

Marcos: `meta-ads-kb/04-tracking-atribucion-medicion/01-arquitectura-senales-pixel-capi-datasets.md`,
`04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md` (§1 mapa, §2 píxel con `eventID`, §3
payload, §4 deduplicación, §5 consentimiento, §6 validación), `04-tracking-atribucion-medicion/03-emq-advanced-matching-pii-hashing.md`,
`04-tracking-atribucion-medicion/07-custom-builds-api-directa.md` (§3 Stripe, §5 tokens),
`04-tracking-atribucion-medicion/08-eventos-offline-y-crm.md`, `04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md`,
`04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md`, `05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md`
y `05-leadgen-high-ticket-crm/04-integraciones-crm.md`; en mensajería, `07-instagram-placements-mensajeria/12-whatsapp-business-platform-medicion-revenue.md`
§4 y `07-instagram-placements-mensajeria/14-funnels-de-mensajeria.md` §6. Todas dentro de `meta-ads-kb/`. Guías paso a
paso: `docs/guias/capi.md`, `docs/guias/ghl-meta.md`, `docs/guias/stripe.md` y `docs/guias/mensajeria.md`.

Reparto: `ingeniero-capi` construye (código, flujos de n8n o Make, pasos de GHL); `especialista-tracking` diagnostica y
verifica en el dataset; `especialista-crm` define etapas y modelo de datos de GHL o Stripe.

## Pasos

1. **Contexto.** Ficha (`meta.dataset`, `meta.evento_principal`, `crm`, `stripe`) y el plan de funnel
   (`clientes/<slug>/planes/*_funnel.md`). Sin funnel → `/disenar-funnel` primero: los eventos salen de él.
2. **Diagnóstico actual** (solo lectura, `especialista-tracking`): `ads_get_datasets`, `ads_get_dataset_stats` (por
   evento y origen), `ads_get_dataset_quality` (calidad de coincidencia y deduplicación), `ads_pixel_event_read`, y
   `python3 -I herramientas/landing_check.py <url>` para píxel, GTM y consentimiento en la web.
   Trampa conocida: el mismo evento enviado por el navegador sin `eventID` y por el servidor del CRM se cuenta dos
   veces. `[EMPIRICAL]` observado en una cuenta de servicios high-ticket con `Schedule` duplicado (calendario en la web
   más la CAPI de GHL).
3. **Mapa de eventos** (`04-…/02-…` §1), una fila por evento: dónde ocurre · origen (navegador, servidor, CRM) ·
   clave de deduplicación (`event_id`, igual en navegador y servidor) · parámetros de cliente (`em`, `ph`,
   `external_id`, `fbc`, `fbp`, IP, user agent) · valor y moneda · `action_source`. Las etapas del CRM llevan
   `action_source=system_generated`, `event_source=crm` y `lead_event_source=<CRM>`, y el `event_name` **exacto de la
   tabla canónica del contrato §16** (`Lead`, `DiagnosticoCompletado`, `LeadCualificado`, `Schedule`,
   `LlamadaAsistida`, `PropuestaEnviada`, `Purchase`; `LeadPerdido` solo si se decide mandarlo, y nunca para
   optimizar). Nunca el nombre visible de la etapa en GHL ni los ejemplos de la KB (`raw_lead`, `qualified`…): Meta
   deja el nombre libre y pide que sea estable (`05-…/03-…` §3). Todas las etapas a medida que ocurren: con formulario
   instantáneo el CRM empieza por `Lead`; con formulario web, `Lead` sale del píxel y de la CAPI web con su `event_id`
   y el CRM empieza en la etapa siguiente (`docs/guias/capi.md` §2). Las conversaciones que nacen en un anuncio de mensajes van
   aparte: `action_source=business_messaging`, el canal y solo la lista cerrada de Meta (`LeadSubmitted`,
   `QualifiedLead`, `Purchase`…; ni `Lead` ni `Schedule`), sin deduplicación de Meta: cada hito, una vez
   (`docs/guias/mensajeria.md` §2 y §6). Guárdalo en `clientes/<slug>/planes/AAAA-MM-DD_capi.md` y
   **pide su aprobación antes de construir**.
4. **Construir** por vía (`ingeniero-capi`; entregables en `clientes/<slug>/planes/capi/`):
   - **web**: píxel con `eventID` más CAPI por la vía de menos esfuerzo que deduplique (CAPI de Meta en un clic,
     Gateway, GTM de servidor o la integración de la plataforma; `04-…/01-…` §2.6–2.7). Páginas hechas con
     `/construir-landing`: el envío al webhook es el payload v1 de `plantillas/paginas/README.md` (respeta
     `enviar_a_meta`, que sale `false` sin consentimiento) y el receptor sigue «Qué hace tu servidor con el envío»
     (ruta A: n8n, Make o backend → GHL + CAPI con el mismo `event_id` que el píxel). Plantilla del receptor:
     `plantillas/integraciones/paginas/` (n8n importable; Make y backend en su README).
   - **ghl**: los workflows los crea el usuario en GHL siguiendo `docs/guias/ghl-meta.md`. Lead con el *Facebook Lead
     ID* mapeado; disparador *Pipeline Stage Changed* por etapa con **Allow multiple** activado; acción de CAPI de Meta
     por etapa; la etapa ganada se llama **«Purchase»** y lleva valor y moneda; el CRM conectado como fuente en Events
     Manager (`05-…/04-…` §3.4). GHL tarda hasta un día en mostrar eventos y pide volumen para salir de «waiting»
     (`05-…/04-…` §2, `[EMPIRICAL]` del proveedor).
   - **n8n o Make**: Make tiene el módulo «Create a Lead Event» (gratis hasta febrero de 2028, `05-…/04-…`); en n8n,
     nodo HTTP al endpoint de eventos con normalización y hash. `ingeniero-capi` entrega el flujo listo para importar.
   - **stripe** (SaaS): el alta del backend guarda `utm_*`, `ad_id`, `fbc` y `fbp` en los metadatos del cliente de
     Stripe, y un webhook (`checkout.session.completed`, `customer.subscription.created`, `invoice.paid`) envía
     `StartTrial`, `Subscribe` o `Purchase` con valor (`04-…/07-…` §3). Esos metadatos los escribe el código del
     propio usuario al registrarse su cliente: el sistema nunca escribe en Stripe.
   - **backend**: worker con reintentos, lotes de ≤1.000 eventos (un error descarta el lote entero), `event_time`
     real y validación previa (`04-…/07-…` §2 y §4–6).
   - **mensajeria** (Click to WhatsApp, Messenger, Instagram Direct): elige la vía (BSP con CAPI de mensajería, Cloud
     API propia, GHL sin `ctwa_clid` o solo la app; `docs/guias/mensajeria.md` §3) y usa las plantillas de
     `plantillas/integraciones/mensajeria/` (n8n importable, Make, backend). Dos piezas: guardar el `referral` del
     **primer** mensaje (anuncio, `ctwa_clid`, PSID o IGSID) en el contacto, y mandar el evento al cambiar de etapa:
     `lead` → `LeadSubmitted`, `cualificado` (o la etapa de `--cualifica-en`) → `QualifiedLead`, `ganado` → `Purchase`
     con valor; diagnóstico, llamada, asistencia, propuesta y perdido no tienen evento de mensajería. Dataset vinculado
     a la WABA, la Página o la cuenta de Instagram; WABA y dataset de mensajería en la ficha (`meta.waba`,
     `meta.dataset_mensajeria`). La acción CAPI de GHL no cubre mensajería: con GHL, vía sin clic (teléfono hasheado)
     o webhook propio (§3 de la guía).
   - **Token de CAPI**: lo genera el usuario en Events Manager y lo pega en `.env` como `META_CAPI_TOKEN_<SLUG>` (o en
     el almacén de credenciales de n8n o Make). Nunca en el chat ni dentro de código que se comparta.
5. **Probar solo con código de prueba.** El usuario copia el código de *Test Events* de Events Manager.
   - Hash: `python3 -I herramientas/capi.py hashear --tipo em|ph|... [--prefijo 34] "<valor>"` para comprobar que
     la normalización de tu código, n8n o Make da el mismo hash (`04-…/03-…` §2 trae vectores de prueba).
   - Evento de prueba: `python3 -I herramientas/capi.py construir --evento <Lead|Schedule|Purchase|StartTrial|Subscribe>
     --origen <website|system_generated|...> --event-id <id> [--valor .. --moneda ..] [datos de cliente]
     --salida clientes/<slug>/privado/AAAA-MM-DD_evento-prueba.json` (lleva datos de cliente: va a `privado/`). Para
     una etapa del CRM, `--etapa <id del §16> --crm <CRM> [--lead-id <id>]` en vez de `--evento`: pone el nombre
     exacto (`--etapa asistio` → `LlamadaAsistida`).
   - `python3 -I herramientas/capi.py validar <payload>` y después
     `python3 -I herramientas/capi.py enviar --cliente <slug> --test-code <CÓDIGO> <payload>`. Comprueba en Test
     Events que llega, con qué parámetros y si se deduplica con el del navegador.
   - En GHL, n8n o Make, el código de prueba va en el campo `test_event_code` de la acción mientras se prueba, y se
     quita después.
   - Mensajería: `python3 -I herramientas/capi.py origen <webhook en privado/>` dice si el aviso trae el anuncio y el
     clic; `capi.py construir --canal <whatsapp|messenger|instagram> --etapa <etapa> [--cliente <slug>]
     [--desde-webhook <webhook>] --salida clientes/<slug>/privado/AAAA-MM-DD_evento-mensajeria.json`, `validar` y
     `enviar --test-code` como arriba. Prueba con el clic del propio usuario, nunca con leads reales; el `ctwa_clid`
     real solo sale de un clic en un anuncio (guía §7). Si *Test Events* no lo muestra pero `events_received` es 1,
     revisa la vista general del dataset antes de dar nada por bueno.
   - **Nunca envíes eventos reales de prueba**: ensucian el dataset y la optimización del cliente. Sin código de
     prueba, `capi.py` exige `--real --confirmo` y el hook `eventos_guard` pide confirmación: no lo uses salvo que el
     usuario lo pida expresamente para ese envío.
6. **Verificar a las 48–72 h** (`especialista-tracking`, `04-…/16-…` §1.2): el mismo evento llega por navegador y por
   servidor y se deduplica; calidad de coincidencia «Good» o mejor (≥6) en el evento principal; en CRM, cobertura de
   al menos el 60 % de los leads de Meta y `event_time` posterior a la creación del lead (`05-…/04-…` §3.3 y §5); tres
   conversiones de prueba reconciliadas con el backend (`13-sistema-operativo/03-framework-lanzamiento.md`, gate 2).
   En mensajería: origen guardado en los contactos de anuncio, eventos que cuadran con los cambios de etapa, ningún
   hito repetido y nada con más de 7 días (`docs/guias/mensajeria.md` §10).
   **Medición en el dispositivo** (*Measure conversions on customer devices*, ajuste del píxel en Events Manager):
   activada por defecto desde el 2026-11-12 y sin efecto para personas de la UE y el Reino Unido. Comprueba si está
   activada y si el cliente la quiere; si queda activada en mercados fuera de la UE, anota la fecha en «Medición» de la
   ficha: las conversiones reportadas suben sin cambio real y hay que re-baselinar los KPI desde ese día.
7. **Consentimiento** (UE): el banner tiene que ser coherente con lo que se envía, y nunca datos sensibles de salud o
   finanzas en parámetros (`04-…/09-…`).
8. **Estado y registro.** Marca `F1.dataset`, `F1.dedup` y `F1.crm` (verifica: mcp) solo tras la verificación del
   paso 6. Anota en la sección «Medición» de la ficha el método, la fecha y el estado. Si algo se cambió en Meta
   (eventos o parámetros del píxel por MCP, siempre con `operador-meta` y plan aprobado), va al change log.
9. **Siguiente.** Con cobertura suficiente, optimizar a *qualified leads* eligiendo la etapa objetivo
   (`etapa_objetivo_cl` de la ficha si existe) y sin tocarla 2–4 semanas (`05-…/04-…` §3.4; `05-…/03-…` §4) →
   `/ejecutar-cambio`. Dos contradicciones entre fuentes oficiales, ambas [CONTESTED] (`00-ESTADO-ACTUAL-2026.md` §6):
   el mínimo de leads (sin mínimo según el anuncio de 2025; ≥200 leads al mes según la guía de developers de
   2026-10-27: planifica con 200 y prueba con menos) y si funciona con formularios web o solo con formularios
   instantáneos. Listas de clientes → `/audiencias`; listas por etapa del CRM → `/anuncios-por-etapa`.

Mensajería, sin promesas que Meta no cumple: en la UE la optimización a leads por mensajes está restringida (por
defecto, maximizar conversaciones; compruébalo en Ads Manager), Instagram no optimiza a compras y un `Purchase` más de
7 días después del clic no se atribuye. La señal sigue valiendo para leer el coste por cualificado por anuncio
(`docs/guias/mensajeria.md` §1 y §11). En WhatsApp, la ventana gratuita tras un clic en un anuncio puede durar hasta
7 días y hay 1.000 mensajes de servicio gratis por número y mes [OFFICIAL META], pero los mensajes del Business Agent
de Meta se cobran también dentro de esa ventana: cuéntalo en el coste de atención.
