# Sales feedback loop: de anuncio a cash y de vuelta a Meta

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: diseño del sistema ad → lead → CRM → cualificado → agendado → show → cierre → valor → feedback a Meta y al equipo creativo; campos de CRM, UTMs/ad_id, informes por anuncio hasta cash, rituales. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **El objetivo del loop es doble:** (1) que Meta optimice hacia leads que se convierten en dinero (qualified leads vía CAPI CRM o eventos web profundos) y (2) que **tú** decidas presupuesto y creatividades por coste por agenda/show/venta y cash, no por CPL. Sin (2), (1) se rompe en silencio. **[STRONG INFERENCE]**
- **La llave es el ID:** en instant forms, cada lead ya trae `id` (lead ID), `ad_id`, `adset_id`, `campaign_id`, `form_id`, `is_organic`, `platform`; en web, usa los parámetros dinámicos oficiales `{{ad.id}}`, `{{adset.id}}`, `{{campaign.id}}`, `{{placement}}`, `{{site_source_name}}` y guarda `fbclid`/`_fbc`. **[OFFICIAL META]** (S05-090, S05-091)
- **Ojo con los cambios:** los parámetros por **nombre** quedan congelados al nombre de la publicación original, y **cambiar parámetros de URL tras publicar puede devolver el ad set a learning**. Define la convención antes de lanzar. **[OFFICIAL META]** (S05-091)
- **Envía a Meta todas las etapas** (p. ej. raw_lead → … → won/lost; en Meta Ads OS, los nombres de la tabla del contrato §16, `docs/desarrollo/contratos.md`) con nombres estables y timestamps reales; ≥60% de cobertura; diario como mínimo (archivo 03/04). **[OFFICIAL META]**
- **Informe por anuncio hasta cash, semanal**, con cohortes por semana de captación: inversión → leads → cualificados → agendas → shows → ventas → cash día 0 → cash esperado. Decide con la métrica más profunda que ya haya "madurado" para esa cohorte. **[STRONG INFERENCE]**
- **La atribución de Meta y la de tu CRM no van a coincidir** (ventanas, view-through/engage-through, cambio de definición de clic en marzo 2026). Para decisiones de presupuesto por anuncio usa el CRM (atribución por ID del lead); para incrementalidad, tests de lift (área 04). **[STRONG INFERENCE]** + ledger área 04 (S04-003)
- **El loop humano importa tanto como el técnico:** motivo de pérdida obligatorio, revisión semanal marketing+ventas, y escucha de llamadas para extraer objeciones que vuelven a los anuncios. **[STRONG INFERENCE]**

---

## 1. El sistema completo

```
                ┌──────────────────────────────────────────────────────────────────┐
                │                         META ADS                                  │
                │  Campaña ─ Ad set ─ Anuncio (ad_id)                                │
                └───────┬──────────────────────────────────────────────▲───────────┘
                        │ lead (instant form) / clic (web, fbclid)        │ CAPI CRM: etapas + valor
                        ▼                                                 │ (lead_id / fbc / em / ph)
     ┌───────────────────────────────┐   webhook/API    ┌────────────────┴──────────────┐
     │ Instant form / Landing+form   │ ───────────────▶ │ CRM (sistema de verdad)        │
     │ (ad_id, form_id, lead_id,     │                  │ etapas, motivos, setter,       │
     │  fbclid, utm_*)               │                  │ closer, valor, cash, cuotas    │
     └───────────────────────────────┘                  └───────┬──────────────┬────────┘
                                                                 │              │
                                       speed to lead / setter ◀──┘              └──▶ BI / hoja: informe por anuncio,
                                       closer / pagos                                cohortes, decisiones de presupuesto
```

## 2. Campos de CRM (mínimo y recomendado)

| Bloque | Campo | Origen | Obligatorio |
|---|---|---|---|
| Identidad Meta | meta_lead_id | Lead ads (`id`) | Sí (IF) |
| | fbclid / fbc / fbp | Landing (campos ocultos / cookie) | Sí (web) |
| | ctwa_clid / psid | Webhook de mensajería | Sí (mensajería) |
| Atribución | campaign_id, adset_id, ad_id (+ nombres) | Lead ads o `{{…}}` en URL | Sí |
| | placement, site_source_name | `{{placement}}`, `{{site_source_name}}` | Recomendado |
| | form_id / landing / variante | Lead ads / URL | Sí |
| | is_organic, platform | Lead ads | Recomendado |
| Cualificación | respuestas del formulario | Formulario | Sí |
| | phone_number_verified | Lead ads (descarga; puede no llegar por CRM) | Recomendado |
| Proceso | first_touch_at, primer_intento_at, contactado_at | CRM/telefonía | Sí (speed to lead) |
| | setter, closer | CRM | Sí |
| Etapas | etapa actual + timestamp de cada etapa | CRM | Sí |
| | motivo_perdida (lista cerrada) | Setter/closer | **Sí** |
| Dinero | valor_contrato, forma_pago (PIF/plan/financiación), nº cuotas | Closer/pasarela | Sí |
| | cash_cobrado_acumulado, impago, reembolso (fecha, importe) | Pasarela | Sí |

**Lista cerrada de motivos de pérdida** (ejemplo): no contesta · número/email falso · no recuerda el formulario · sin presupuesto · no es decisor · mal momento · no encaje (perfil) · eligió competidor · no-show sin reprogramar · objeción de confianza · spam/bot. Cada motivo apunta a un dueño distinto (Meta/creatividad, setter, oferta, closer).

## 3. Tracking: convención de parámetros

**Web (en el campo URL parameters del anuncio):**
```
utm_source=meta&utm_medium=paid&utm_campaign={{campaign.id}}&utm_content={{ad.id}}&utm_term={{adset.id}}&placement={{placement}}&site={{site_source_name}}
```
- Usa **IDs** (estables) en vez de nombres (congelados a la publicación original y frágiles). **[OFFICIAL META]** (S05-091)
- Captura en la landing: todos los `utm_*`, `fbclid`, cookies `_fbc`/`_fbp`, y pásalos como campos ocultos al formulario/aplicación y al calendario.
- `{{placement}}` permite ver si Audience Network o Reels traen agendas o basura (útil ahora que las exclusiones por ad set desaparecen en Leads).
- Cambiar parámetros tras publicar puede reiniciar el learning: añádelos desde el primer día.

**Instant forms:**
- El lead ya trae `ad_id`, `adset_id`, `campaign_id`, `form_id`, `is_organic`, `platform` (S05-090).
- Añade **tracking parameters** del formulario (ocultos) para lo que no está en el lead: oferta, ángulo, versión del formulario (S05-024).

**Mensajería:** guarda `ctwa_clid` y el `ad_id` del objeto *referral* del webhook (WhatsApp/Messenger) en el contacto. **[OFFICIAL META]** (S05-025)

## 4. Devolver la señal a Meta

| Funnel | Qué enviar | Cómo |
|---|---|---|
| Instant form | Todas las etapas por `lead_id` (+ em/ph) con `event_source=crm` | CAPI for CRM (partner o directa) → qualified leads |
| Web (VSL/aplicación/calendario) | `Lead` y `Schedule` por pixel + CAPI (dedupe con `event_id`); etapas CRM posteriores con `fbc`/em/ph | CAPI web + CAPI CRM; Sequenced Events si disponible |
| Webinar | `CompleteRegistration`, `WebinarAttended` (ejemplo; en Meta Ads OS, `WebinarAsistido`: contrato §16), `Purchase` | Pixel + CAPI desde webhooks |
| Mensajería | `LeadSubmitted`, `QualifiedLead`, `Purchase` con `ctwa_clid`/PSID | CAPI business messaging (optimización solo compras en Messenger/WA) |

Valor: envía `value` y `currency` en `won` (cash esperado o contribución, sé consistente) para poder evaluar campañas por valor y, con volumen, usar value optimization.

## 5. Informes: por anuncio hasta cash

### 5.1 Tabla semanal por anuncio (cohorte = semana de captación)

| ad_id | Ángulo | Inversión | Leads | CPL | % cualif | Agendas | Coste/agenda | Show % | Shows | Ventas | CPA | Cash día 0 | Cash esperado | ROAS cash 0 | Motivo de pérdida nº1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Reglas de lectura:
- **Madurez:** la cohorte de la semana pasada solo tiene datos fiables hasta "agenda"; la de hace 4-6 semanas, hasta "venta". Compara anuncios en la etapa madura más profunda.
- **Mínimos de muestra:** no saques conclusiones de cierre con <10 shows por anuncio; agrupa por ángulo o creativo-concepto si hay muchos anuncios.
- **Contra targets del archivo 05:** coste por agenda vs target por agenda; coste por show vs target por show; CPA vs target CPA.

### 5.2 Vistas complementarias
- **Por canal de captura** (IF vs web vs WhatsApp vs DM).
- **Por placement/site_source** (¿hay placements con leads baratos y 0 agendas?).
- **Por setter y closer** (para no culpar a la campaña de un problema de ventas).
- **Por franja horaria de captación** (leads nocturnos vs diurnos → decisión de ad scheduling).
- **Cohortes de cash** a 30/60/90 días (impagos y reembolsos por campaña).

## 6. Rituales (el loop humano)

| Frecuencia | Reunión | Entradas | Salidas |
|---|---|---|---|
| Diario (10 min) | Pipeline del día | Leads sin contactar, agendas de hoy/mañana, no-shows | Reasignaciones, reconfirmaciones |
| Semanal (45 min) | Marketing + ventas | Tabla por anuncio, motivos de pérdida, 3-5 extractos de llamadas | Anuncios a pausar/escalar, nuevos ángulos desde objeciones reales, ajustes de formulario |
| Mensual | Economía | Tasas reales, contribución por venta, impagos/reembolsos | Recalcular BE/targets (calculadora), etapa objetivo de qualified leads |
| Trimestral | Estrategia | Cohortes, LTV, canal | Mix de canales, oferta, precio |

**Del CRM a la creatividad:** las objeciones y frases literales de clientes en llamadas son la mejor fuente de hooks; los motivos de pérdida dicen qué promesa del anuncio atrae al perfil equivocado. **[STRONG INFERENCE]**

## 7. Atribución: qué número usar para qué

| Pregunta | Fuente | Por qué |
|---|---|---|
| ¿Qué anuncio trajo esta venta? | CRM por `ad_id` del lead | Determinista, sin ventanas |
| ¿Cuánto debo invertir en total? | Cohortes de cash del CRM + incrementalidad | El CRM no ve el efecto de view/engage en otros canales |
| ¿Está aprendiendo Meta? | Ads Manager: resultados de la etapa objetivo, learning, diagnóstico del dataset CRM | Es lo que ve el algoritmo |
| ¿Funciona Meta frente a no hacer nada? | Conversion lift / test geográfico (área 04) | Única medida causal |

Meta cambió en marzo de 2026 la definición de clic para conversiones web (solo link clicks; "engage-through" para interacciones) → comparativas antes/después de esa fecha requieren cuidado (ledger del área 04, S04-003). **[OFFICIAL META]** (vía área 04)

## Implicaciones operativas

- Diseña campos, motivos de pérdida y parámetros de URL **antes** de la primera campaña.
- Usa IDs en parámetros; captura `fbclid`/`_fbc` y `meta_lead_id` siempre.
- Envía todas las etapas a Meta; decide presupuesto con el CRM.
- Ritual semanal marketing+ventas con la tabla por anuncio; sin él, la calidad del lead se discute con opiniones.

## Errores frecuentes

- Atribuir ventas con UTMs de nombre que cambian cuando alguien renombra un anuncio.
- Añadir parámetros de URL a anuncios ya en marcha (reinicio de learning).
- Tomar decisiones de cierre con cohortes inmaduras (la semana pasada "no vendió nada").
- Motivos de pérdida en texto libre (no analizables).
- Informe de marketing que acaba en "leads" y de ventas que empieza en "llamadas": nadie ve el coste por venta por anuncio.

## Preguntas abiertas

- ¿Cómo atribuye Meta las etapas CRM a anuncios cuando el lead viene de Advantage+ con varias creatividades dinámicas? (Las IDs del lead son las del anuncio, pero la mezcla de assets no es visible).
- Calidad del matching por `fbc` + email en funnels web para qualified leads (sin cifras públicas de cobertura típica).

## Fuentes clave

- [Information included when you download your leads data](https://www.facebook.com/business/help/974763215942961) — vigente 2026-10-16 — meta-oficial (S05-090)
- [Specifications for dynamic URL parameters](https://www.facebook.com/business/help/2360940870872492) — vigente 2026-10-16 — meta-oficial (S05-091)
- [Set up tracking parameters for your lead ads](https://www.facebook.com/business/help/1974877976152436) — meta-oficial (S05-024)
- [Conversions API for CRM: Integrate as a Platform](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/conversions-api-crm-for-platforms) — meta-developers (S05-002)
- [Conversions API for Business Messaging](https://developers.facebook.com/docs/marketing-api/conversions-api/business-messaging/) — meta-developers (S05-025)
