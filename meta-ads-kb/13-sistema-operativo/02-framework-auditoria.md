# Framework de auditoría de cuenta

> Última verificación: 2026-10-16 · Autor: agente principal · Ámbito: auditoría profesional de una cuenta de Meta Ads
> (negocio, economía, tracking, estructura, campañas, presupuesto, audiencias, creatividad, funnel, ventas, políticas,
> seguridad, medición). Modo **solo lectura**: la auditoría no modifica nada.

## TL;DR

- **Orden**: negocio y economía → seguridad y riesgo → señal (tracking) → medición → estructura → presupuesto y pujas →
  audiencias → creatividad → funnel y ventas → políticas. Lo de arriba invalida lo de abajo: no tiene sentido optimizar
  creatividades si el evento de optimización está duplicado. **[STRONG INFERENCE]**
- **Cada hallazgo** con: evidencia (dato o captura), severidad (P0–P3), impacto estimado, acción, responsable y esfuerzo.
- **P0 = pérdida de dinero o riesgo de cuenta ahora** (tracking roto/duplicado, accesos inseguros, gasto en algo que no
  convierte, incumplimiento de políticas). P1 = palanca grande de rendimiento. P2 = mejora. P3 = higiene.
- **Periodo de análisis**: 90 días + mismo trimestre del año anterior; semanas completas; marcar las discontinuidades
  de Meta (ventanas view fuera de API el 12-ene-2026; click = link click desde mar-2026).

---

## 0. Preparación

- Accesos de solo lectura (Ads Manager analista, Events Manager, Commerce Manager, backend/CRM de solo lectura).
- Ficha de cuenta ([10-plantillas §1](10-plantillas.md)) rellenada con el cliente: modelo, oferta, márgenes, objetivos,
  capacidad, histórico de cambios, problemas percibidos.
- Exportes: rendimiento por campaña/ad set/anuncio por semana (90 días), breakdowns (placement, edad, país, dispositivo —
  requieren opt-in en API desde 6-ago-2026), audience segments, Events Manager overview, backend (pedidos/leads/ventas).

## 1. Negocio y economía

| Comprobación | Qué buscar | Red flag |
|---|---|---|
| Contribución por venta y break-even | ¿Existe y es correcta? (sin IVA, devoluciones, fees por país, comisiones) | Nadie sabe el CPA/ROAS break-even |
| Base del valor enviado a Meta | ¿Con o sin IVA/envío? ¿Coherente con el break-even? | ROAS target calculado en otra base |
| Tendencia de negocio | Revenue neto, MER, nCAC, % nuevos, cash (high-ticket) vs gasto Meta | Gasto ↑ y negocio plano |
| LTV y payback | Por cohorte, en contribución | LTV "de ingresos" usado para justificar CAC |
| Capacidad | Stock, agenda comercial | Leads sin atender, roturas de stock |

## 2. Seguridad, activos y riesgo (P0 si falla)

→ [08/03](../08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md),
[08/01](../08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md)

- [ ] Propiedad de activos: Portfolio, ad accounts, Páginas, IG, dataset, catálogos, dominios son del cliente.
- [ ] 2–10 personas con *full control*, todas con 2FA/passkeys; nadie externo como admin personal; agencias como partner.
- [ ] Usuarios/partners obsoletos eliminados; peer approval de solicitudes de partner si está disponible.
- [ ] Account Quality: restricciones, historial de rechazos, anuncios en revisión.
- [ ] Verificaciones: negocio, dominio, anunciante (obligatoria en productos financieros en España y otros 9 mercados).
- [ ] Pagos: método principal + respaldo; límites de gasto; fallos recientes; location fees (jul-2026) contemplados.
- [ ] Reglas MCP / integraciones de terceros con permisos de escritura (desde ago-2026 el panel de reglas MCP se
      observó con escrituras permitidas por defecto) → bloquear lo que no se use.
- [ ] Categoría especial correctamente declarada si aplica (empleo, vivienda, servicios financieros, temas sociales).

## 3. Señal (tracking) — el 50 % de las auditorías se resuelve aquí

→ [04/16 checklist](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md),
[04/02](../04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md),
[04/03 EMQ](../04-tracking-atribucion-medicion/03-emq-advanced-matching-pii-hashing.md)

| Comprobación | Umbral de referencia | Severidad si falla |
|---|---|---|
| Purchase/Lead recibidos en Events Manager vs backend (mismo periodo, con consentimiento) | ±5 % | P0 |
| Deduplicación navegador/servidor (`event_id` + `event_name`) | overlap > 90 % | P0 si hay duplicados |
| Un único emisor por evento y fuente (sin plugins/GTM/app duplicados) | 1 | P0 |
| CAPI presente para eventos clave; cobertura CAPI/píxel | ≥75 % (ejemplo oficial de Meta) | P1 |
| EMQ del evento de optimización | "Good/Great" y ≥6,0 recomendado por Meta (developers); ≥8 es práctica sin respaldo oficial | P1 |
| `fbc`/`fbp`, IP y UA del usuario (no del servidor) en CAPI | Presentes en la mayoría | P1 |
| `value`/`currency` correctos; `content_ids` = catálogo; match rate catálogo | >90 % | P1 |
| Frescura de eventos | Real time | P2 |
| Datos sensibles en URLs/parámetros (salud, finanzas) | Ninguno | P0 (política) |
| Custom conversions "flagged" sin datos desde sep-2025 | Ninguna en uso | P1 |
| Lead gen: lead ID en CRM y etapas devueltas por CAPI | ≥2–3 etapas, subida diaria | P1 |
| Consentimiento UE: sin aceptar no hay envíos | Correcto | P0 (legal) |
| UTMs dinámicos y `fbclid` sobreviviendo a redirecciones | Sí | P2 |

## 4. Medición y atribución

- Ventana de atribución por ad set: coherente con el ciclo de compra (7d click por defecto; 1d click infra-cuenta en
  ciclos largos); engage-through activado/desactivado con criterio.
- Dashboards: ¿piden ventanas eliminadas (7d/28d view) y muestran vacío? ¿cruzan marzo-2026 sin ajuste?
- Reconciliación Meta vs backend vs GA4 (misma zona horaria, moneda, definición de valor). → [04/11](../04-tracking-atribucion-medicion/11-meta-vs-ga4-shopify-crm-stripe.md)
- ¿Existe alguna lectura de incrementalidad? (lift, geo-test, holdout, MMM, incremental attribution como columna).
- Audience segments: % de gasto y de conversiones en nuevos / engaged / existentes.

## 5. Estructura y arquitectura

→ [02/05](../02-estructura-campanas/05-arquitectura-de-campanas.md), [02/09](../02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md)

| Comprobación | Red flag |
|---|---|
| Nº de ad sets activos por objetivo vs volumen (≈50 × CPA/semana por ad set) | Muchos ad sets en learning limited permanente |
| Solapamiento (auction overlap) entre ad sets/campañas/cuentas | Duplicados del mismo ganador; varias cuentas para el mismo negocio |
| Evento de optimización vs negocio | Optimizando a Lead bruto, ATC, LPV, clics o engagement cuando hay señal más profunda posible |
| Objetivo correcto para el resultado | Tráfico/engagement para vender |
| Deuda técnica 2025–2026 | Intereses retirados (sin entrega desde 15-ene-2026), ASC/AAC legacy, ECBC, bid multipliers, qualified leads sin CAPI, placements retirados |
| Retargeting separado | Sin holdout; audiencias minúsculas con frecuencias altísimas |
| Campañas zombis / pausadas con presupuesto | — |
| Nomenclatura | Imposible agregar por ángulo/concepto |

## 6. Presupuesto y pujas

- Presupuesto por ad set vs CPA (≥ ~7× CPA/día para estabilidad; oficial ≥10× coste del goal; ≥5× con cost goal).
- Pujas: cost per result goal / ROAS goal / bid cap → ¿entregan? ¿se ajustan con ≥7 días entre cambios? ¿objetivos
  realistas (CTC: cost goal entrega ~140 % del objetivo de media)?
- Historial de cambios de presupuesto: ¿frecuencia diaria? ¿saltos que reinician learning?
- Budget scheduling vs duplicados para picos.
- Coste marginal: ¿se ha escalado más allá del break-even marginal? (comparar escalones de gasto).

## 7. Audiencias

→ [02/07](../02-estructura-campanas/07-audiencias-2026.md)
- ¿Restricciones duras sin razón de negocio (edad, género, intereses, LAL como control)?
- Exclusiones de clientes coherentes con el objetivo (adquisición vs total); Customer Lifecycle Strategy.
- Listas de clientes actualizadas (automáticas) y audience labels (HIGH_VALUE_CUSTOMERS, QUALIFIED_LEADS).
- Value rules: ¿se usan para corregir segmentos con evidencia? ¿o para "intuiciones"?
- Categorías especiales: targeting permitido.

## 8. Creatividad

→ [03](../03-creatividad/README.md), [13/05](05-framework-testing-creativo.md)

| Comprobación | Red flag |
|---|---|
| Diversidad real (ángulos/personas/formatos) | 20 anuncios = 2 conceptos; *Creative diversity* "Low" |
| Concentración del gasto | 1 anuncio con >70 % del gasto y sin relevo |
| Cadencia de anuncios nuevos | Nada nuevo en 4+ semanas |
| Hit rate y aprendizajes registrados | No hay registro; "ganadores" con 5 conversiones |
| Fatiga | CPA del anuncio sube por impresiones acumuladas; *Creative fatigue* en Delivery |
| Formatos por placement | Solo 1:1/16:9; sin 9:16 para Reels/Stories; textos en safe zones rotas |
| Enhancements de IA | Activados sin revisión (texto reescrito en imágenes, música, traducciones) |
| Prueba social | Post IDs perdidos al recrear anuncios innecesariamente |
| Comentarios | Sin moderar; preguntas sin respuesta |

## 9. Funnel y ventas

→ [03/09](../03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md), [05/09](../05-leadgen-high-ticket-crm/09-sales-feedback-loop.md)
- Landing: message match, velocidad móvil, CTA, prueba, objeciones; LPV rate (clics → LPV).
- Ecommerce: ATC → checkout → compra; AOV; % nuevos; devoluciones.
- Lead gen: cohortes lead → cualificado → cita → show → cierre → cash; speed to lead; recordatorios; motivo de pérdida.
- Diagnóstico **ad vs oferta vs landing vs ventas**: CTR bueno + CVR mala → post-clic; leads buenos + cierre malo → ventas
  u oferta; todo bueno salvo volumen → creatividad/presupuesto.

## 10. Políticas y cumplimiento

→ [08/06](../08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md), [08/08](../08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md),
[08/10](../08-cuenta-politicas-seguridad/10-landing-pages-y-politicas.md)
- Claims de ingresos/resultados, salud, antes/después, atributos personales ("¿estás endeudado?"), garantías.
- Coherencia anuncio-landing; landing funcional; sin cloaking.
- Formularios: no preguntar ingresos, deudas, salud.
- UE: anuncios que rozan "temas sociales" (economía, salud) con tono de denuncia.
- Variaciones automáticas de IA que puedan introducir claims.

## 11. Entregable de auditoría

```markdown
# Auditoría <cuenta> · <fecha> · periodo analizado
## Resumen ejecutivo (5 líneas): estado, 3 problemas principales, impacto estimado, plan 30/60/90
## Scorecard
| Área | Estado (🟢/🟡/🔴) | Hallazgo clave |
## Hallazgos
| # | Área | Hallazgo | Evidencia | Severidad P0–P3 | Impacto estimado | Acción | Esfuerzo | Responsable |
## Plan
- Semana 1 (P0): …
- 30 días (P1): …
- 60–90 días (P2/P3 + tests): …
## Supuestos y límites de la auditoría (qué no se pudo verificar)
```

Reglas del entregable: cada afirmación con dato; separar hechos de hipótesis; estimar impacto con la descomposición
CPM/CTR/CVR o con economía; no recomendar reestructuraciones masivas sin plan de medición.
