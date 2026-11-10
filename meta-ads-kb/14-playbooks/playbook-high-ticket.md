# Playbook: High-ticket (coaching, consultoría, formación premium 3.000-50.000 €)

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: ofertas vendidas por llamada o conversación con setter/closer. Base: `05-leadgen-high-ticket-crm/06-high-ticket-funnels.md`, `05-…`, `08-…`, `09-…`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Meta funciona para high-ticket cuando la oferta es clara, el experto tiene prueba verificable y existe capacidad comercial;** el cuello de botella casi nunca es el CPL sino show y cierre. **[STRONG INFERENCE]**
- **Funnel por defecto:** anuncio → VSL → aplicación (calendario solo a cualificados) → confirmación con vídeo → setter (WhatsApp/llamada) → closer. Alternativa a testear: instant form Higher intent + SMS + booking embebido o WhatsApp. **[STRONG INFERENCE]**
- **Evento:** `Schedule`/aplicación cualificada (web) o qualified leads con etapa "cualificado"/"agendado" (instant form + CAPI CRM). La venta solo para medir y valor. **[OFFICIAL META]** requisitos (S05-001, S05-007)
- **Números de control (coaching 10.000 €, archivo 05):** contribución 4.603 €/venta; **target 299 € por llamada agendada (BE 598 €)**, target CPL de aplicación 84 € (BE 168 €). Agencias reportan 150-350 $ por llamada agendada desde Meta. **[STRONG INFERENCE]** + **[EMPIRICAL]** débil (S05-042)
- **Riesgo de cuenta:** nada de promesas de ingresos/enriquecimiento rápido en anuncio, VSL ni formulario. **[OFFICIAL META]** (S05-071)

---

## 1. Cuándo usar Meta

| Sí | No todavía |
|---|---|
| Oferta probada con ≥5-10 clientes y casos documentables | Oferta sin validar (vende primero a mano/orgánico) |
| Closer disponible (o fundador) con cierre ≥15-20% sobre shows | Nadie para hacer llamadas en <24-72 h |
| Contribución por venta ≥ 1.500-2.000 € | Margen que no soporta 300-600 € por llamada |
| Audiencia identificable por problema (dueños de negocio, profesionales, etc.) | Nicho minúsculo sin volumen |

## 2. Arquitectura por presupuesto

| Presupuesto/mes | Estructura | Evento |
|---|---|---|
| 2.000-5.000 € | 1 campaña Leads/Sales (Advantage+), 1 ad set, 4-8 anuncios (2-3 ángulos) a la VSL; retargeting incluido en Advantage+ | Aplicación enviada (`Lead`) si `Schedule` < 20/semana |
| 5.000-20.000 € | Prospección + campaña pequeña de retargeting de prueba (casos, objeciones; 5-15%) + testing creativo | `Schedule` o qualified leads "agendado" |
| 20.000-60.000 € | + canal secundario (instant form + booking, DM setting, webinar) | Etapa más profunda viable (show) o Sequenced `Lead → Schedule` |
| > 60.000 € | Varias ofertas/segmentos; control de cuenta; lift tests | + value con valores esperados por etapa |

Exclusiones (controles): clientes, leads últimos 30-90 días. Audiencias de clientes y visitantes VSL como sugerencias.

## 3. Evento de optimización

Regla del archivo 03: etapa más profunda con 1-40% de conversión sobre leads, ≤28 días y ~50 eventos/semana.
- 300 aplicaciones/mes (~70/semana) con 28% de agenda → ~20 agendas/semana → optimiza a **aplicación cualificada** (≈30/semana) y mide agenda/show/venta.
- 1.000 aplicaciones/mes → agenda (~65/semana) viable; show (~42/semana) casi.
- Si aparece **Sequenced Events** en tu cuenta (`Lead → Schedule`), haz A/B frente a `Schedule` directo. (S05-034)

## 4. Creatividades

- **Prueba > promesa:** casos con contexto de *proceso* (qué hizo, en qué plazo, con qué punto de partida), demostraciones del método, el experto explicando un error común.
- **Filtros explícitos:** "No es para ti si…", requisitos, rango de inversión.
- **Formato:** vídeos del experto a cámara (hook en 3 s), carruseles de casos, imágenes con titular para testing rápido.
- **Retargeting:** objeciones (precio, tiempo, "¿me sirve a mí?"), testimonios en vídeo, desglose de la oferta.
- Nunca: capturas de ingresos, "gana X en Y días", urgencia falsa. (S05-071)

## 5. Funnel y proceso comercial

| Paso | Estándar |
|---|---|
| Aplicación | 6-10 preguntas; opción múltiple primero; sin preguntas de ingresos personales |
| Routing | Cualificado → calendario; no cualificado → recurso gratuito / low-ticket |
| Calendario | Citas en ≤72 h; pocas franjas; datos y UTMs pasan al CRM |
| Confirmación | Vídeo "qué pasará en la llamada", casos, añadir al calendario |
| Setter | Contacto en <5 min, reconfirmación 24 h y 1-2 h, reprogramación fácil |
| Closer | Diagnóstico → oferta → PIF/plan/financiación; registrar motivo de pérdida |
| Post-venta | Onboarding inmediato (reduce reembolsos) |

Comisiones sobre **cash cobrado**; setter por **shows cualificados**, no por agendas brutas.

## 6. Métricas y umbrales (coaching 10.000 € de ejemplo)

| Métrica | BE | Target | Acción |
|---|---|---|---|
| CPL de aplicación | 167,56 € | 83,78 € | Diagnóstico |
| Coste por lead cualificado | 418,89 € | 209,44 € | > BE 2 semanas → ángulo/oferta |
| **Coste por llamada agendada** | **598,41 €** | **299,21 €** | Métrica principal de los primeros 7-14 días |
| Coste por show | 920,63 € | 460,32 € | Si sube y la agenda no → show (archivo 08) |
| CPA | 4.603,17 € | 2.301,58 € | Validar con cohorte madura (4-6 semanas) |
| Show rate | — | ≥65-75% | < 60% → plazo de cita, confirmación |
| Cierre sobre shows | — | ≥20% | Por closer; < 15% → ventas/oferta, no Meta |

## 7. Ejemplo numérico completo

Oferta 10.000 € (IVA incl.), 50% PIF / 50% en 6 cuotas (+10%, 20% de impago en pendientes), 5% reembolsos, 3% pasarela, 20% entrega, closer 10% + setter 5% → **contribución 4.603 €/venta**; cash día 0 = 62% del cash esperado.

Funnel: 40% de aplicaciones cualifican, 70% agenda, 65% show, 20% cierre → lead→venta 3,64%.

20.000 € a 60 € por aplicación → 333 aplicaciones → 133 cualificadas → 93 agendas → 61 shows → **12,1 ventas**; coste por agenda 214 € (< target 299 €), CPA 1.648 €; cash esperado 116.278 € (día 0: 71.789 €); contribución 55.852 € → **beneficio tras ads 35.852 €**.

Sensibilidad: con show 50% y cierre 15%, el BE CPL baja a 96,67 € (de 167,56 €): el mismo CPL de 60 € sigue siendo rentable pero el margen se reduce a la mitad. (Archivo 05 §6.)

## 8. Plan de arranque (primeros 45 días)

| Semana | Acciones | Criterio de paso |
|---|---|---|
| 0 | Economía (contribución, BE/target por agenda y show); VSL, aplicación con routing, página de confirmación con vídeo; CRM con etapas y motivos; pixel+CAPI (`Lead`, `Schedule`) con `event_id`; UTMs con `{{ad.id}}` | Prueba completa: aplicación → agenda → CRM → evento en Events Manager |
| 1-2 | 1 campaña, 4-8 anuncios (2-3 ángulos); optimizar a aplicación (o `Schedule` si se espera volumen); setter con SLA <5 min | Coste por agenda medido por anuncio |
| 3-4 | Pausar ángulos con coste por agenda > BE y ≥5 agendas esperadas; nuevos anuncios desde objeciones de llamadas; revisar show por setter | Show ≥60%, coste por agenda ≤ target |
| 5-6 | Primeras cohortes maduras: CPA y cash por anuncio; si `Schedule` ≥30-50/semana, probar optimizar a `Schedule` (o Sequenced Events); test de canal secundario (instant form + booking o DM) | CPA de cohorte ≤ target → escalar 20-30% cada 3-4 días |

## 9. Reglas de decisión rápidas

- Coste por agenda estable y CPA sube → problema de show/cierre (ventas), no de Meta.
- Coste por agenda sube y show/cierre estables → creatividad/fatiga/oferta.
- Un ángulo con muchas agendas y cierre muy bajo → promesa demasiado fácil; reescribir o pausar aunque el coste por agenda sea bueno.
- No escales más rápido que la capacidad de llamadas del closer (agendas a >72 h hunden el show).

## 10. Errores frecuentes

- Calendario abierto a todos; closers con 40% de llamadas no cualificadas.
- Optimizar a `Lead` y escalar por CPL de aplicación.
- Ignorar el cash flow de planes de pago al escalar.
- Culpar a Meta de un cierre del 10% de un closer concreto.
- Promesas de resultados económicos en la VSL (rechazos, reembolsos, chargebacks).

## Preguntas abiertas

- Efecto del booking embebido de Meta (2026) en show/cierre high-ticket.
- Rendimiento de Sequenced Events frente a `Schedule`.

## Fuentes clave

- `05-leadgen-high-ticket-crm/06-high-ticket-funnels.md`, `05-economia-funnel-lead-gen-calculadoras.md`
- [Conversions API for CRM integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) (S05-001)
- [Cost Per Booked Call Benchmarks for High-Ticket Coaches](https://www.780marketing.ca/articles/cost-per-booked-call-benchmarks) — 2026-07-03 (S05-042)
- [Unrealistic outcomes](https://transparency.meta.com/policies/ad-standards/deceptive-content/unrealistic-outcomes) (S05-071)
