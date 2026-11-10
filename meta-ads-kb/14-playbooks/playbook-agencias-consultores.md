# Playbook: Agencias y consultores (captar clientes propios y gestionar lead gen de clientes)

> Última verificación: 2026-11-09 · Autor: A05 (agente), ampliado por B16 · Ámbito: (A) agencias/consultores que se anuncian para captar clientes (servicio B2B high-ticket recurrente); (B) agencias que gestionan lead gen para clientes. Base: `05-leadgen-high-ticket-crm/04`, `06`, `09`, `10`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.
>
> **¿Eres una consultora, agencia o freelance de IA y automatización que vende proyectos a pymes** (diagnóstico →
> llamada → propuesta → cierre)? Tu playbook es
> [playbook-consultoras-ia-automatizacion.md](playbook-consultoras-ia-automatizacion.md): economía con el coste de
> vender, ofertas de entrada que precualifican, embudos, evento por volumen, creatividad anti-hype y un ejemplo completo.
> La parte A de este archivo queda para agencias de servicios con retainer mensual (marketing, captación, contenidos);
> la parte B sirve a todos los que gestionan Meta para clientes.

## TL;DR

- **(A) Captar clientes:** funciona con nicho declarado, oferta de diagnóstico tangible, casos con métricas **del cliente** y un funnel VSL/caso → aplicación → llamada. Con un retainer de 2.000 €/mes y 8 meses de vida media, el BE es **~1.358 € por llamada agendada** (target ~679 €); con solo los 3 primeros meses, mucho menos. **[STRONG INFERENCE]** Si vendes proyectos de IA o automatización, ve al [playbook de consultoras de IA](playbook-consultoras-ia-automatizacion.md).
- **(B) Gestionar clientes:** el diferencial vendible en 2026 es montar **CAPI CRM + qualified leads + informe por anuncio hasta cash**; la mayoría de pymes no lo tiene y desde abril de 2026 sin integración no hay qualified leads en campañas nuevas. **[OFFICIAL META]** (S05-007; verificado de nuevo el 2026-11-09)
- **Activos del cliente, siempre en su Business Manager y su dataset:** cambiar de dataset reinicia el aprendizaje. **[OFFICIAL META]** (S05-002)
- **Separar en el reporting problema de marketing vs de ventas del cliente** (velocidad, show, cierre) para no perder clientes por un problema que no es tuyo. **[STRONG INFERENCE]**
- **Reporta y decide por cohortes maduras, no por el mes natural:** con pocas ventas al mes, un mes malo puede ser azar (sección 7). **[STRONG INFERENCE]**

---

## Parte A — Agencia/consultor captando clientes

> Para consultoras de IA y automatización (proyecto a medida + diagnóstico + propuesta investigada), esta parte se
> queda corta: usa el [playbook de consultoras de IA y automatización](playbook-consultoras-ia-automatizacion.md).

### 1. Cuándo usar Meta
- ICP = dueños de pymes/negocios locales/profesionales (accesibles en Meta).
- Tienes 3-5 casos con métricas verificables y un nicho.
- Capacidad de cierre (fundador o closer).
- Para cargos concretos en empresas grandes o listas cerradas de cuentas, LinkedIn y el outbound van primero y Meta hace de cobertura ([playbook de consultoras de IA §2](playbook-consultoras-ia-automatizacion.md)). **[STRONG INFERENCE]**

### 2. Arquitectura
| Presupuesto/mes | Estructura | Evento |
|---|---|---|
| 1.500-5.000 € | 1 campaña Leads/Sales a VSL o caso de estudio; 4-6 anuncios del fundador | Aplicación (`Lead`) o `Schedule` si ≥20-30/semana |
| 5.000-15.000 € | + retargeting de casos y objeciones; test instant form Higher intent + booking embebido | `Schedule` / qualified leads "agendado" |
| > 15.000 € | Varios nichos/ofertas; webinars B2B | Etapa más profunda viable |

Nota sobre el booking embebido en el formulario: solo funciona en la app de Facebook para móvil y las reservas no se reportan en Ads Manager; devuélvelas por la CAPI. **[OFFICIAL META]** (verificado el 2026-11-09; detalle en el [playbook de consultoras de IA §5.2](playbook-consultoras-ia-automatizacion.md))

### 3. Oferta y creatividades
- Diagnóstico/auditoría con entregable (p.ej. "auditoría de tu embudo de captación en 30 min con 3 acciones").
- Casos: "Clínica X: de 35 € a 18 € por cita en 60 días" (métricas de cliente), nunca capturas de facturación propia ("gana 10k/mes con tu agencia" es justo el tipo de promesa que Meta prohíbe en *Prohibited commercial practices*: recompensa económica irreal por un esfuerzo mínimo, S05-071).
- El fundador explicando un error frecuente del nicho.
- Filtro: "solo trabajamos con [nicho] que ya invierte X en publicidad".

### 4. Ejemplo numérico
Retainer 2.000 €/mes, vida media 8 meses, margen 50%, pasarela 1%, comisión closer 600 € → **contribución 7.240 €/cliente**. Funnel: 45% cualifica, 60% agenda, 75% show, 25% cierre → lead→cliente 5,06%.
- **BE CPL 366,53 € / target 183,26 €; BE por agenda 1.357,50 € / target 678,75 €.**
- 6.000 € a CPL 50 € → 120 leads → 32,4 agendas (185 €/agenda) → 24,3 shows → **6,1 clientes**, CAC 988 €, contribución 43.983 € → beneficio 37.983 € **si** la vida media de 8 meses se cumple.
- **Conservador (solo 3 meses de contrato mínimo):** contribución ≈ 3 × 2.000 × 0,5 − 600 − 60 ≈ 2.340 € → BE CPL ≈ 118 €, BE por agenda ≈ 439 €. Planifica la caja con este escenario.
- **Falta el coste de vender:** si cada cliente exige varias llamadas y una propuesta preparada, súmalo como coste por venta (`--coste-fijo` en `herramientas/economia.py leadgen`); el método está en el [playbook de consultoras de IA §3.2](playbook-consultoras-ia-automatizacion.md). **[STRONG INFERENCE]**

## Parte B — Agencia gestionando lead gen de clientes

### 5. Checklist de onboarding (semana 1-2)

**Negocio y economía**
- [ ] Ficha del cliente con `/cliente-nuevo`: `relacion: cliente`, su `tipo` real, su moneda, su ventana de atribución y su política de IA. Sin ficha no se recomiendan presupuestos ni targets (regla del OS).
- [ ] Economía del cliente: contribución por venta, tasas actuales, BE/target (calculadora, archivo 05; `/economia`).
- [ ] **Capacidad comercial del cliente** (citas o llamadas que puede atender por semana) y techo de gasto que se deriva ([playbook de consultoras de IA §3.6](playbook-consultoras-ia-automatizacion.md)).
- [ ] CRM del cliente y responsables de cada etapa; definición escrita de "cualificado" y de cada etapa (las del contrato §16 si vende con propuesta; menos si es un negocio local).

**Activos, accesos y protección**
- [ ] **Activos en su Business Portfolio y su dataset**; la agencia entra como partner con los roles mínimos (`/configurar-meta`, situación «agencia»; `docs/agencias.md`).
- [ ] Topes en la ficha (`topes.cambio_dia`, `topes.total_dia`), `mejoras_automaticas: off` salvo decisión explícita y las reglas del Ads MCP Server en Business Settings.
- [ ] Una regla de protección por cuenta (`/reglas-automaticas`): pausar y avisar ante gasto sin resultados que solo puede ser una rotura. **[STRONG INFERENCE]**
- [ ] **Encargo de tratamiento firmado** (RGPD, art. 28) y avisos de privacidad y cookies del cliente que cubran píxel, CAPI y audiencias de lista ([04/09](../04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md)). **[OFFICIAL — regulador]**

**Señal**
- [ ] Integración lead retrieval + **CAPI CRM** (partner: Zapier/Make/HubSpot/GHL/Salesforce) con `meta_lead_id` y raw lead. En GHL: workflow por cambio de etapa con «Allow Multiple», `Purchase` con valor y moneda, un servidor por sub-cuenta (`ghl-<slug>`) y token de solo lectura (`docs/guias/ghl-meta.md`).
- [ ] Parámetros dinámicos `{{ad.id}}` etc. y tracking parameters en formularios.
- [ ] Leads de formulario sincronizados a diario: Meta solo los guarda 90 días. **[OFFICIAL META]**

**Proceso comercial**
- [ ] SLA de respuesta del cliente (≤5 min en horario) y ad scheduling acorde.
- [ ] Citas a ≤72 h, confirmación activa y recordatorios (`/seguimiento-leads`).
- [ ] Informe semanal por anuncio hasta venta/cash (archivo 09).

### 6. Contrato y reporting
- KPI acordado: coste por cita/lead cualificado/venta según el modelo, **no CPL**, medido sobre **cohortes maduras** (una cohorte de leads solo cuenta para ventas cuando ha pasado su ciclo de venta habitual).
- Cláusula de dependencia: si el cliente no contacta en el SLA o no actualiza el CRM, los KPIs de calidad no son exigibles.
- Propiedad: cuentas, dataset, audiencias y creatividades pagadas por el cliente son del cliente; la tarjeta de pago de los anuncios, también. **[STRONG INFERENCE]**
- Reporting con tres bloques: Meta (inversión, CPL, learning), CRM (cualificado, cita, show, venta, motivos de pérdida), economía (CPA vs target, cash).
- **Cómo en el OS:** `/informe-cliente` con `gestor-cliente`; cohortes con `embudo.py cohortes --por semana|anuncio`; resultados por anuncio con `ghl.py por-anuncio`; cada cambio en el `change-log.md` del cliente.
- **Cadencia:** semanal breve (qué cambió, 1–3 decisiones con fecha de evaluación), mensual con economía (CAC de cohortes maduras frente al target) y trimestral para presupuesto y oferta.
- **Siempre en el informe:** periodo con fechas absolutas, ventana de atribución, qué cohortes aún no han madurado y la diferencia entre lo atribuido por Meta y lo que dice el CRM.

### 7. Reglas de decisión para la cuenta del cliente

- Si el cliente no cumple el SLA de contacto o no actualiza etapas, el problema de "calidad" no se puede diagnosticar: priorizar proceso antes que presupuesto.
- Coste por cita estable y ventas a la baja → reunión con ventas del cliente (show/cierre), no cambios de campaña.
- Antes de proponer más inversión, presenta el BE/target por cita con la calculadora y la capacidad comercial del cliente.
- **Paciencia estadística:** no evaluar cambios con menos de 7 días, 30–50 eventos o una ventana sin madurar, salvo roturas ([13/01 §8](../13-sistema-operativo/01-principios-de-razonamiento.md)). Apagar anuncios a 2–3× el CPA o coste objetivo sin conversión, nunca a 1×. **[STRONG INFERENCE]**
- **Expectativas con pocas ventas:** si el cliente espera 2 ventas al mes, la probabilidad de un mes con cero por azar es ~14 % (Poisson); acuerda evaluar por trimestre. **[STRONG INFERENCE]**
- **Escalar** por coste marginal y capacidad del cliente, con subidas espaciadas ≥7 días y condición de reversión (`/escalar`).
- **Cada cambio** en el `change-log.md` del cliente (de → a, motivo, métrica, fecha de evaluación, IDs); las escrituras en Meta solo con plan aprobado y a través de `operador-meta`.

### 8. Errores frecuentes
- Montar todo en el Business Manager/dataset de la agencia (el cliente pierde historial y aprendizaje al irse).
- Vender "leads a X €" sin control del proceso comercial del cliente.
- Casos con métricas de vanidad (CPL) en vez de negocio.
- Prometer ingresos o "sistema para facturar X" en tu propia publicidad.
- Informes sin ventana de atribución ni madurez de cohortes, o que mezclan lo atribuido por Meta con las ventas del CRM.
- Tocar la campaña cada día porque el cliente pregunta: el aprendizaje se reinicia y nada llega a madurar.
- Subir listas de prospección del cliente sin base legal ([playbook de consultoras de IA §2.3](playbook-consultoras-ia-automatizacion.md)).
- Dejar encendidas las mejoras automáticas de Advantage+ creative en cuentas con claims sensibles (salud, ahorro, ingresos).

### 9. Primeros 30 días con un cliente nuevo

| Semana | Qué haces | Criterio para pasar |
|---|---|---|
| 1 | Ficha, economía, accesos como partner, encargo de tratamiento, auditoría de la cuenta si es heredada (`/auditoria` o `/auditoria-express`) | BE/target por etapa en la ficha; lista de P0 |
| 2 | Señal: CAPI web y de CRM, etapas, UTMs y parámetros; formulario o landing; SLA y recordatorios del cliente | Lead de prueba en el CRM en < 1 min con `ad_id`; eventos sin duplicar |
| 3 | Primer lote creativo (3–4 conceptos distintos) revisado por políticas; campaña en pausa y activación con confirmación | Gasto estable, leads entrando |
| 4 | Primera lectura por anuncio hasta la etapa madura; primer informe con expectativas por cohorte | Coste por cualificado o por cita medido; decisiones con fecha |

**[STRONG INFERENCE]** (orden del [framework de lanzamiento](../13-sistema-operativo/03-framework-lanzamiento.md))

### 10. Modelo de precio de la agencia

| Modelo | Cuándo encaja | Riesgo |
|---|---|---|
| Fijo mensual + puesta en marcha | Por defecto: alinea a la agencia con el sistema, no con el volumen | Que el cliente no vea el vínculo con resultados: informes por cohorte |
| % de la inversión | Cuentas grandes con presupuesto estable | Incentiva gastar más, no gastar mejor |
| Por lead o por cita | Solo si controlas el proceso comercial | Incentiva leads baratos y malos; disputas sobre qué es «válido» |
| Fijo + bonus por coste por cita o por venta de cohortes maduras | Clientes con CRM fiable y SLA cumplido | Necesita definiciones escritas y datos del CRM al día |

**[STRONG INFERENCE]** Sea cual sea, el contrato fija definiciones de etapa, SLA del cliente y cláusula de dependencia (sección 6).

## Preguntas abiertas

- ¿Cuenta la sync nativa de HubSpot del cliente como "integración CAPI" para qualified leads tras abril de 2026? Verificar en cada cuenta.
- ¿Admite Conversion Leads formularios web en la cuenta del cliente? El Help Center dice que sí y la guía de developers (2026-10-27), que no ([playbook de consultoras de IA §6.2](playbook-consultoras-ia-automatizacion.md)).

## Fuentes clave

- `05-leadgen-high-ticket-crm/04-integraciones-crm.md`, `06-high-ticket-funnels.md`, `09-sales-feedback-loop.md`
- [Playbook de consultoras y agencias de IA y automatización](playbook-consultoras-ia-automatizacion.md) (verificación oficial del 2026-11-09)
- [About performance goals for lead ads](https://www.facebook.com/business/help/782657799338685) (S05-007)
- [Conversions API for CRM: Integrate as a Platform](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/conversions-api-crm-for-platforms) (S05-002)
- [Prohibited commercial practices](https://transparency.meta.com/policies/ad-standards/deceptive-content/prohibited-commercial-practices/) (sustituye a la página «Unrealistic outcomes» de S05-071, reorganizada desde fin de 2025)
- `docs/agencias.md` y `docs/guias/ghl-meta.md` (operativa del OS con varios clientes y GHL)
