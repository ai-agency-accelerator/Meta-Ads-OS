# Integraciones CRM ↔ Meta: qué soporta cada herramienta y arquitectura recomendada

> Última verificación: 2026-10-15 · Autor: A05 (agente) · Ámbito: conectar Meta Lead Ads / funnels web con CRMs (HubSpot, GoHighLevel, Salesforce, Zapier, Make, Pipedrive, Zoho, Kommo, Close…) en ambas direcciones. El detalle técnico de CAPI web (deduplicación, parámetros) es del área 04. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Son dos integraciones distintas:** (1) *descarga de leads* Meta → CRM (webhook/Graph API, lo que todo el mundo tiene) y (2) **Conversions API for CRM**: CRM → Meta, enviando las etapas del lead para qualified leads. La segunda es la que mejora la optimización y la que muchos negocios no tienen. Meta insiste en que es una integración **separada** de la CAPI web. **[OFFICIAL META]** (S05-001, S05-002)
- **Salesforce:** la más madura oficialmente: integración "Salesforce Webhooks" documentada por Meta (Outbound Message + Flow, sin código; Lead.Status y Opportunity.StageName → `event_name`) y conexión directa de Sales Cloud anunciada para noviembre de 2025, además de Data Cloud. **[OFFICIAL META]** (S05-003, S05-005)
- **HubSpot:** la sincronización nativa envía cambios de *lifecycle stage* (y formularios/visitas) a Meta con click ID, email y teléfono; según su KB (actualizada 09-09-2026) solo cuenta para campañas de lead gen con objetivo conversion/qualified leads. La comunidad reporta que **no envía el Meta Lead ID**; la vía que Meta documenta para HubSpot es Zapier con una propiedad personalizada que guarda el lead ID. **[OFFICIAL META]** + **[EMPIRICAL]** (S05-004, S05-027, S05-028)
- **GoHighLevel:** soporte nativo vía workflows (trigger *Pipeline Stage Changed* → acción Meta CAPI "Lead Event", mapeando el Facebook Lead ID); además es partner de lanzamiento de la reserva embebida en instant forms (junio 2026). **[EMPIRICAL]** (documentación del vendor, S05-029, S05-062)
- **Zapier y Make:** conectores oficiales/documentados para cualquier CRM. Zapier: acción "Send Funnel Event"; Meta anunció hasta 100.000 eventos gratis (oct-2025). Make: módulo "Create a Lead Event", gratis del 27-02-2026 a febrero de 2028; desde octubre de 2025 el Lead ID ya no es obligatorio si se envía email. **[OFFICIAL META]** + **[EMPIRICAL]** (S05-004, S05-005, S05-030)
- **Pipedrive, Zoho, Close:** sin integración nativa verificada con CAPI for CRM; se resuelve con Zapier/Make o conectores (Stape, Datahash, CustomerLabs, LeadsBridge). **Kommo** tiene un widget de CAPI por etapa del pipeline orientado a click-to-message (solo plan Pro desde 01-06-2026). **[EMPIRICAL]** (S05-068 a S05-070)
- **Arquitectura recomendada:** un único "sistema de verdad" (CRM) que guarde `leadgen_id` o `fbc/fbclid` + IDs de anuncio, envíe **cada cambio de etapa** a un dataset CRM de Meta en tiempo real o cada hora, con nombres de etapa estables, y tenga alertas de error y de cobertura (≥60%). **[OFFICIAL META]** + **[STRONG INFERENCE]**

---

## 1. Las tres tuberías (no las confundas)

```
[Anuncio Meta] ──(1) Lead Ads Retrieval: webhook leadgen / Graph API / CRM nativo──▶ [CRM]
[Landing web]  ──(2) Pixel + CAPI web (Lead, Schedule…) con event_id, fbc, fbp ────▶ [Dataset web]
[CRM]          ──(3) Conversions API for CRM: etapas (p. ej. raw_lead, qualified, booked, showed, won…) ──▶ [Dataset CRM]
```

Los nombres de etapa del esquema son ejemplos: Meta deja el `event_name` libre. En Meta Ads OS, usa los de la tabla del
contrato §16 (`docs/desarrollo/contratos.md`): `Lead`, `LeadCualificado`, `Schedule`, `LlamadaAsistida`,
`PropuestaEnviada`, `Purchase`.

- (1) sin (3) = tienes los leads pero Meta no aprende qué leads fueron buenos.
- (3) requiere que (1) guarde el `leadgen_id` (instant forms) o que tu landing capture `fbclid`/`_fbc` y lo lleve al CRM (web).
- Offline Conversions API: retirada con Graph API v16 (mayo de 2025). Todo va por la CAPI estándar. **[OFFICIAL META]** vía secundarias (S05-052)
- Las etapas del CRM deben llevar `action_source = system_generated`, `event_source = crm` y `lead_event_source = <CRM>`; sin esto no sirven para qualified leads (S05-002, S05-003).

## 2. Tabla de soporte por herramienta (estado 2026-10-15)

| Herramienta | (1) Recibe leads de Meta | (3) Envía etapas a Meta (CAPI CRM) | Lead ID | Notas / limitaciones | Confianza |
|---|---|---|---|---|---|
| **Salesforce** | Sí (integración directa) | **Sí:** Salesforce Webhooks (Meta, sin código), Sales Cloud directo (desde nov-2025), Data Cloud | Campo custom `Meta Lead ID` → `lead_id` (máxima prioridad) | Requiere perfil System Administrator, Flow activado, salida HTTP; eventos visibles en ~1 h | alta |
| **HubSpot** | Sí (nativo) | **Parcial:** sync de lifecycle stage, formularios HubSpot y page views vía CAPI; Marketing Hub Starter/Pro/Enterprise (5/50/100 eventos) | Matching por click ID, email, teléfono; la KB no menciona lead ID; comunidad: no lo envía | Solo cuenta cambios posteriores a crear el evento; solo formularios HubSpot; Meta solo usa lifecycle de contactos de campañas de lead gen con conversion/qualified leads. Alternativa: Zapier + propiedad con lead ID | media-alta |
| **GoHighLevel** | Sí (formularios FB mapeados) | **Sí:** workflow *Pipeline Stage Changed* → acción Meta CAPI "Lead Event" (pixel ID + token) | Mapeo "Facebook Lead ID for lead events" | GHL cita ≥250 leads/mes y ≥50 eventos en 7 días para salir de "waiting"; activar "Allow multiple" en workflows; eventos tardan hasta 1 día en verse. Partner de booking embebido | media-alta |
| **Zapier** | Sí | **Sí:** "Facebook Conversions → Send Funnel Event" | Mapear propiedad con lead ID | Triggers de muchos CRMs son *polling* (retraso según plan); 100.000 eventos gratis (Meta, oct-2025) | alta |
| **Make** | Sí | **Sí:** "Create a Lead Event" | Opcional si hay email (desde oct-2025) | Gratis 27-02-2026 → feb-2028; `event_time` hasta 7 días atrás; admite valor y moneda | alta |
| **Pipedrive** | Vía apps/Zapier | Vía Stape, Datahash, CustomerLabs, LeadJourney, Zapier/Make | Según app (Stape: campo con lead ID) | Sin integración nativa verificada | media |
| **Zoho CRM** | Sí (nativo/marketplace) | Vía Datahash, Stape, Zapier/Make | Según app | Sin integración nativa verificada | media |
| **Kommo** | Fuentes FB/IG/WhatsApp | **Widget CAPI** por etapa del pipeline (eventos Lead y Purchase) | No documentado | "Mejora solo anuncios click-to-message"; solo plan Pro desde 01-06-2026 | media |
| **Close** | Vía Zapier/apps | Vía Zapier/Make | — | No verificado | baja |
| **LeadsBridge / Datahash / Stape / CustomerLabs** | Sí | Sí (conectores CAPI CRM) | Sí | Vendors; Datahash exige ≥2 etapas mapeadas | media |

Fuentes: S05-003, S05-004, S05-005, S05-027 a S05-030, S05-068 a S05-070.

## 3. Arquitectura recomendada (servicios / high-ticket)

### 3.1 Captura
- **Instant form:** CRM con integración nativa o webhook que guarde: `leadgen_id`, `form_id`, `ad_id`, `adset_id`, `campaign_id`, `created_time`, respuestas, `phone_number_verified` (si llega), tracking parameters. **[OFFICIAL META]** (S05-024)
- **Web:** campos ocultos en el formulario/aplicación con `fbclid`, `_fbc`, `_fbp`, `utm_*` (incluido `utm_content={{ad.id}}` o similar), `event_id` del Lead para deduplicar pixel/CAPI. El calendario (Calendly/GHL) debe recibir esos parámetros o el email para casar la reserva. **[STRONG INFERENCE]** + área 04.
- **Mensajería:** guarda `ctwa_clid` (WhatsApp) o PSID/page_id (Messenger) desde el webhook; sin Cloud API no hay trazabilidad fiable. **[OFFICIAL META]** (S05-025)

### 3.2 Modelo de datos mínimo en el CRM

| Campo | Ejemplo | Para qué |
|---|---|---|
| meta_lead_id | 1234567890123456 | Matching CAPI CRM |
| fbc / fbclid | fb.1.1729…. | Matching web |
| ad_id, adset_id, campaign_id | 1202… | Informe por anuncio hasta cash |
| canal_captura | instant_form / web_vsl / ctwa / ig_dm / call | Comparar canales |
| etapa | raw_lead → contacted → qualified → booked → showed → won / lost / disqualified (ejemplo; en Meta Ads OS, las etapas y los `event_name` del contrato §16, `docs/desarrollo/contratos.md`) | Señal y funnel |
| fecha_por_etapa | timestamps | Velocidad, ventana 28 días |
| motivo_descalificacion | sin presupuesto / no encaje / no contesta / spam | Diagnóstico creativo y de audiencia |
| valor_contrato, cash_cobrado, plan_pagos, reembolso | 10.000 / 5.000 / 6 cuotas / no | Economía real |
| setter, closer | nombres | Separar problema de marketing vs ventas |

### 3.3 Envío de etapas a Meta
- **Qué:** todas las transiciones a medida que ocurren, también la inicial (confirma recepción y cobertura). Nombres estables; no renombres a mitad de campaña. Meta deja el `event_name` libre; en Meta Ads OS se escribe exactamente como en la tabla del contrato §16 (`docs/desarrollo/contratos.md`), con sus mayúsculas (`Lead`, `LeadCualificado`, `Schedule`, `LlamadaAsistida`, `PropuestaEnviada`, `Purchase`), nunca con el nombre visible de la etapa en el CRM. Etapa inicial: con instant form, el CRM manda `Lead` con `lead_id`; con formulario web, `Lead` ya llega por píxel + CAPI web con el mismo `event_id` y el CRM empieza en la etapa siguiente para no contarlo dos veces. **[STRONG INFERENCE]**
- **Cuándo:** en tiempo real (webhook) o batch horario/diario; mínimo diario. **[OFFICIAL META]**
- **Cómo:** `lead_id` (+ `em`, `ph` hasheados) para instant forms; `fbc` + `em`/`ph` para web. `event_time` = momento real del cambio y siempre posterior a la creación del lead.
- **Valor:** añade `value`/`currency` en la etapa ganada (`won` en el ejemplo, `Purchase` en Meta Ads OS) y, opcionalmente, valor esperado en etapas intermedias (archivo 03 §5).
- **Errores:** un error descarta el batch completo (≤1.000 eventos) → valida antes de enviar y registra errores con alertas.
- **Cobertura:** objetivo ≥60% de leads de Meta con eventos CRM; la causa típica de baja cobertura es no guardar el lead ID o no enviar el raw lead. **[OFFICIAL META]** (S05-002, S05-003)

### 3.4 Configuración en Meta
1. Events Manager → conectar fuente → **CRM** → crear o elegir dataset CRM (no cambiarlo después).
2. Elegir partner (Salesforce Webhooks, Zapier, Make, HubSpot, GHL…) o integración directa.
3. Verificación de datos (1-2 días) → configurar el **funnel** (orden de etapas) en los ajustes del dataset.
4. En Ads Manager: Leads → instant forms (o web) → **Maximize number of qualified leads** → elegir etapa objetivo.
5. Learning 2-4 semanas sin tocar la etapa objetivo.

## 4. Elección según tu stack

| Tu situación | Recomendación |
|---|---|
| Agencia/negocio pequeño, todo en GHL | Workflows nativos de GHL + booking embebido; revisar que el Lead ID se mapea y que llegan ≥50 eventos/7 días |
| HubSpot Marketing Hub | Probar la sync nativa de lifecycle **y** verificar cobertura/estado en Events Manager; si Meta marca "CRM incompleto", usar Zapier/Make con propiedad `meta_lead_id` |
| Salesforce | Salesforce Webhooks (oficial) o Sales Cloud directo; Opportunity solo si tu funnel de venta vive ahí |
| Pipedrive / Zoho / Close / Notion / hojas | Make (gratis hasta 2028) o Zapier; o conector tipo Stape/Datahash |
| Venta por WhatsApp/IG con Kommo | Widget CAPI de Kommo por etapa (plan Pro); asumir que optimiza click-to-message, no instant forms |
| Equipo técnico propio | Integración directa con la API (3-4 semanas según Meta), webhooks en tiempo real, cola con reintentos |

## 5. QA antes de escalar (checklist)

- [ ] ¿Cada lead de Meta tiene `meta_lead_id` en el CRM? (muestra de 20)
- [ ] ¿Llega la etapa inicial a Events Manager para ≥60% de leads? (`raw_lead` en el ejemplo de §3.2; en Meta Ads OS, `Lead` con `lead_id` desde el CRM si es instant form: contrato §16, `docs/desarrollo/contratos.md`.)
- [ ] ¿Las etapas aparecen en el orden correcto en la configuración del funnel?
- [ ] ¿`event_time` > `created_time` siempre?
- [ ] ¿Hay alertas si falla el envío (batch descartado) o si la cobertura cae?
- [ ] ¿Los IDs de anuncio se guardan para el informe por anuncio?
- [ ] ¿La definición de cada etapa está escrita y el equipo comercial la aplica igual?
- [ ] ¿Los leads se sincronizan en <1 minuto (para speed to lead)?

## Implicaciones operativas

- Prioriza la integración (3) frente a cualquier optimización creativa si ya inviertes >3.000 €/mes en leads: es la única palanca que cambia lo que Meta persigue.
- Si usas HubSpot, no asumas que "conectado" = "qualified leads funcionando": comprueba cobertura y estado del dataset.
- Usa Make/Zapier como puente rápido aunque luego construyas algo propio: el coste es ~0 hasta 2028 (Make).

## Errores frecuentes

- Conectar la CAPI web y creer que ya estás enviando etapas del CRM.
- Crear un dataset nuevo cada vez que cambia el freelancer (reinicia el aprendizaje).
- Etapas que se marcan en lote a final de mes (timestamps falsos, fuera de 28 días).
- Workflows sin "allow multiple" que solo envían la primera transición (GHL).
- No registrar motivos de descalificación: pierdes el diagnóstico creativo.

## Preguntas abiertas

- ¿La sync nativa de HubSpot cuenta como "integración CAPI" válida para la regla de abril de 2026?
- La reserva embebida (Calendly/LeadConnector) **no** se reporta en Ads Manager (Meta, S05-095): la cita solo llega a Meta si tu CRM/calendario la envía como etapa por CAPI CRM. Abierto: si Meta lo cambiará.
- Estado real de Close y Pipedrive (sin documentación nativa encontrada).

## Fuentes clave

- [Conversions API for CRM: Integrate as a Platform](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/conversions-api-crm-for-platforms) — meta-developers (S05-002)
- [Salesforce Webhooks guide](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/salesforce-webhooks) — 2026 — meta-developers (S05-003)
- [Zapier — Step 1: Implement integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration/zapier/step-1-implement-integration) — meta-developers (S05-004)
- [HubSpot: Create and sync ad conversion events with Meta](https://knowledge.hubspot.com/create-and-sync-ad-conversion-events-with-your-facebook-ads-account) — 2026-09-09 — vendor (S05-027)
- [HighLevel: Facebook Conversion Leads walkthrough](https://help.gohighlevel.com/support/solutions/articles/48001233833-facebook-conversion-leads-walkthrough) — 2026-06-01 — vendor (S05-029)
- [Make: Facebook Conversions API for CRM](https://apps.make.com/facebook-conversion-leads) — 2026 — vendor (S05-030)
- [Kommo: Meta Conversions API overview](https://support.kommo.com/docs/meta-conversions-api-capi-overview.md) — 2026-05-19 — vendor (S05-068)
