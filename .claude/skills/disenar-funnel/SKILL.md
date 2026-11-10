---
name: disenar-funnel
description: "Elige y especifica el camino de conversión de un cliente: formulario instantáneo con reserva, landing con VSL y llamada, webinar, mensajería con agente de IA, o prueba gratuita o demo en SaaS. Define pasos, evento de optimización, eventos a medir, coste máximo por etapa, SLA comercial y datos que hay que guardar para la señal."
argument-hint: "<cliente> [A|B|C|D|E|vsl-calendario|\"<opción a valorar>\"]"
---

# /disenar-funnel

Cliente: `$ARGUMENTS`. El segundo argumento, si lo hay, es una opción que el usuario quiere valorar: una letra de
los embudos del playbook de consultoras (§5.1: `A` formulario, `B` diagnóstico, `C` VSL y llamada, `D` webinar, `E`
mensajería), `vsl-calendario` (la variante «Captación → VSL con calendario» de `/construir-landing`) o un texto libre.
Esta skill diseña el camino; para construirlo, `/iman-de-leads` (la oferta de entrada) y
`/construir-landing` (la página, con `herramientas/paginas.py`), `/formulario-instantaneo` (el formulario en Meta) y
`/webinar` (registro y gracias de un evento). Una landing ya publicada se audita con `/landing`.

Marcos: matriz de decisión de `meta-ads-kb/05-leadgen-high-ticket-crm/01-canales-captacion-comparativa.md` §3,
`05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md`, `05-leadgen-high-ticket-crm/06-high-ticket-funnels.md`,
`05-leadgen-high-ticket-crm/07-webinars-eventos-lanzamientos.md`, `05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md`,
`05-leadgen-high-ticket-crm/10-b2b-saas-local.md` §2, `07-instagram-placements-mensajeria/11-whatsapp-ads-ctwa.md`,
`07-instagram-placements-mensajeria/13-business-ai-agentes-mensajeria.md`, `07-instagram-placements-mensajeria/14-funnels-de-mensajeria.md`,
`02-estructura-campanas/02-eventos-de-optimizacion.md`, `05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md` §4,
la tabla de destinos de la Fase 3 de `13-sistema-operativo/03-framework-lanzamiento.md` y el playbook de su modelo
(`14-playbooks/playbook-agencias-consultores.md`, `playbook-saas.md`, `playbook-high-ticket.md`, `playbook-lead-gen.md`,
`playbook-negocio-local.md`, `playbook-webinars-eventos-lanzamientos.md`, `playbook-consultoras-ia-automatizacion.md`).
Todas las rutas, dentro de `meta-ads-kb/`. Mensajería medida, paso a paso: `docs/guias/mensajeria.md`.

## Pasos

1. **Contexto.** Ficha (tipo, ticket, mercado, stack, capacidad comercial) y economía. Sin economía → `/economia`
   primero: el funnel se elige también por lo que puedes pagar en cada etapa.
2. **Preguntas** (≤5): complejidad de la decisión y ticket; quién atiende los leads y en cuánto tiempo; qué CRM y
   calendario hay; presupuesto mensual; mercado. En Europa, el Help Center restringe funciones de mensajería y con
   destino WhatsApp la opción por defecto es maximizar conversaciones; la optimización a leads por mensajes llega de
   forma gradual (UE y Reino Unido: `[CONTESTED]`, compruébalo en Ads Manager). La detección automática de leads
   (Automatic Events API) no está en la UE, Reino Unido, Japón ni Corea del Sur (`00-ESTADO-ACTUAL-2026.md` §1;
   `docs/guias/mensajeria.md` §1).
3. **Candidatas** (2–3):

| Opción | Encaja cuando | Evento de optimización | Riesgo principal |
|---|---|---|---|
| Formulario instantáneo «Higher intent» + reserva embebida (Calendly o GHL) | Local con cita, servicios, high-ticket con setter rápido | `Lead` → *qualified leads* (exige CAPI desde el CRM) | Leads flojos sin fricción; la cita no aparece en Ads Manager y hay que devolverla por CAPI |
| Landing + VSL + aplicación + calendario + llamada | High-ticket de 3.000–20.000 € | `Schedule` o aplicación cualificada | CPL alto; `Schedule` necesita volumen |
| Captación → VSL con calendario → llamada (`vsl-calendario`; se construye con `/construir-landing`) | Lo mismo, cuando quieres el contacto antes del vídeo y sin formularios instantáneos | `Lead` al enviar los datos de contacto; `Schedule` desde el CRM por CAPI | Leads que no ven el vídeo ni reservan: necesitan seguimiento; el calendario no filtra si no hay preguntas de cualificación |
| Webinar o lanzamiento | Formación, educación B2B, lanzamientos con fecha | Registro → asistencia → compra | Calendario rígido y desfase entre registro y venta |
| Mensajería con persona o agente de IA (Click to WhatsApp, Messenger, Instagram Direct) | Dudas antes de dar datos, respuesta en < 5 min también fuera de horario, LatAm y sur de Europa, retargeting de quien vio un caso | Leads por mensajes (≥10 `LeadSubmitted` o compras en 30 días) donde exista; si no, conversaciones, y se decide por coste por `QualifiedLead` del CRM | Sin el `referral` del primer mensaje guardado no hay señal; GHL no reenvía el `ctwa_clid`; un `Purchase` > 7 días tras el clic no se atribuye |
| SaaS con prueba gratuita | Self-serve | `StartTrial` o `CompleteRegistration` → activación por CAPI cuando haya ~50/semana | Registros que no activan |
| SaaS con demo | Venta asistida | `Schedule` o *qualified leads* (demo celebrada) | Ciclo largo; pocas señales |

   **Mensajería en venta consultiva** (`docs/guias/mensajeria.md` §1, §9 y §12):
   - **Frente al formulario o la landing**: elígela si el comprador pregunta antes de dar sus datos y alguien (o un
     agente) responde en minutos; si solo buscas volumen que filtre comercial, formulario; si la oferta necesita
     prueba y calculadora, landing. Sin capacidad de guardar el `ctwa_clid` (solo la app de WhatsApp Business), avisa
     de que la medición será con etiquetas o no habrá.
   - **Qué optimizar por fase**: sin señal → conversaciones, leyendo el coste por cualificado en el CRM; con ≥10
     `LeadSubmitted` en 30 días por la CAPI de mensajería → leads por mensajes donde la cuenta lo ofrezca, con
     `LeadSubmitted` definido con exigencia (es lo que Meta optimiza); `QualifiedLead` para medir y decidir
     creatividades; `Purchase` con valor para la caja (compras solo en WhatsApp y Messenger, y con volumen).
   - **Límites**: la acción CAPI nativa de GHL no cubre mensajería; Instagram Direct no optimiza a compras; Meta no
     deduplica estos eventos.
   - **Frente al agente de Meta (Business Agent)**: no compitas en «responder»; vende conversaciones cualificadas
     medidas, el coste por cualificado por anuncio y la integración con su CRM y agenda. Excluye salud, finanzas y
     otros verticales, y un agente de terceros activo en el número lo bloquea: decide la arquitectura por número.

4. **Recomendación**: una opción y una alternativa para probar más adelante. Elige por la **señal que Meta puede
   optimizar y la capacidad de respuesta del equipo**, no por el CPL (`05-…/01-…`, «Implicaciones operativas»).
   Agencias que captan clientes: VSL o caso → aplicación → llamada (`playbook-agencias-consultores.md` §2).
   Consultoras de IA y automatización que venden a pymes: los cinco embudos, el formulario y las etapas del
   `playbook-consultoras-ia-automatizacion.md` §5, y el evento por volumen de su §6.
   - **Opción pedida en el argumento.** Valórala siempre como candidata principal, aunque no sea la que saldría por
     defecto: compárala con esa, di en qué condiciones encaja (con los datos de la ficha) y qué riesgos tiene. Si
     no encaja, explica por qué con números; no la descartes solo por un corte orientativo.
   - **C (VSL y llamada) o `vsl-calendario` por debajo de 15.000 €.** El playbook pone C en tickets de 15.000 € o
     más (§5.1, cortes orientativos `[STRONG INFERENCE]`), pero su §5.4 añade «o soluciones que necesitan 10 minutos
     de explicación», y `05-leadgen-high-ticket-crm/06-high-ticket-funnels.md` (TL;DR y §2) sitúa VSL + aplicación
     + llamada en 5–20 k€ con oferta compleja y closer. Puede tener sentido por debajo de 15.000 € si se cumplen las
     tres:
     1. **Capacidad:** `capacidad.llamadas_semana` cubre las llamadas esperadas (presupuesto semanal / CPL × lead →
        cita). Si no, el techo es el equipo antes que Meta (playbook §3.6): filtra antes del calendario o elige B o A.
     2. **Ticket:** la contribución por venta (`/economia`) aguanta el coste por cita de un CPL más alto (05/06 §2,
        riesgo «CPL alto») y pasa de ~1.500 € (playbook §2.2).
     3. **Ciclo de venta:** decisión compleja o ciclo largo (varios decisores, propuestas que tardan; playbook §9.4):
        la VSL responde objeciones antes de la llamada. Con ciclo corto y oferta fácil de entender, A o B. Si la
        ficha no dice el ciclo, pregúntalo y apúntalo en «Negocio».

     Que la VSL filtre mejor es `[HYPOTHESIS]` (`03-creatividad/15-landing-pages-y-cro-trafico-meta.md` §4.4):
     plantéalo como test frente a B. `vsl-calendario` saca `Lead` antes del vídeo, así que Meta optimiza un evento
     con volumen y no depende de `Schedule` `[STRONG INFERENCE]`. Esto no cambia el criterio de la KB: es cómo leer
     juntos el §5.1 y el §5.4 del playbook y 05/06.
5. **Especificación**, paso a paso (anuncio → … → venta o cliente de pago). Por cada paso:
   - herramienta del stack y quién es responsable;
   - evento con su nombre estándar de Meta y sus parámetros;
   - SLA (speed to lead < 5 minutos en horario como objetivo; `05-…/08-…`);
   - tasa esperada (`[HYPOTHESIS]` si no hay datos) y coste máximo de la etapa, sacado de `/economia` con esas tasas;
   - datos a guardar para la señal: `leadgen_id` en formularios instantáneos; `fbclid`/`_fbc`, `_fbp`, `utm_*` con
     `ad_id` y `event_id` en web (`05-leadgen-high-ticket-crm/04-integraciones-crm.md` §3.1–3.2); plantilla única de
     UTMs de `13-sistema-operativo/10-plantillas.md` §8; en mensajería, el `referral` del primer mensaje (anuncio,
     `ctwa_clid`, PSID o IGSID y hora) en los campos `mensajeria_*` del contacto
     (`plantillas/integraciones/mensajeria/README.md`);
   - qué etapas vuelven a Meta por CAPI (se construyen con `/implementar-capi`).
6. **Evento de optimización**: el más cercano al dinero que alcance volumen útil (~50 por semana y conjunto,
   `13-sistema-operativo/01-principios-de-razonamiento.md` §1). Calcula el volumen semanal esperable con el
   presupuesto y el coste por etapa. Si no llega, usa la etapa superior como puente consciente y apunta cuándo bajar.
7. **Revisión.** `especialista-funnel` revisa el diseño post-clic (formulario, preguntas de cualificación, calendario,
   página de gracias, SLA). Si la economía o el volumen están justos, `analista-cuantitativo`.
8. **Guardar.** `clientes/<slug>/planes/AAAA-MM-DD_funnel.md` (esquema en texto, tabla de pasos y eventos, SLA,
   requisitos de señal). Con su OK, actualiza `meta.evento_principal` en la cabecera de la ficha y la sección
   «Medición». Marca `F0.funnel`. Siguiente: `/implementar-capi` (señal) y el destino: `/iman-de-leads` →
   `/construir-landing` si hay que hacer la página (`/landing` cuando esté publicada), `/landing` si ya existe,
   `/formulario-instantaneo` si el lead se capta en Meta, `/webinar` si es un evento con fecha. Después,
   `/seguimiento-leads` para el speed to lead y las secuencias.
