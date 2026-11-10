# Framework de lanzamiento — de cero a campaña medida

> Última verificación: 2026-10-16 · Autor: agente principal · Ámbito: secuencia completa para lanzar Meta Ads en un
> negocio (o una oferta/mercado nuevo): objetivo de negocio → economía → tracking → oferta → funnel → investigación
> creativa → producción → arquitectura → presupuesto → lanzamiento → medición. Cada fase tiene criterio de salida
> ("gate"): no se pasa a la siguiente sin cumplirlo.

## TL;DR

- **El orden importa**: economía y tracking ANTES que creatividad y estructura. Una campaña bien montada sobre una oferta
  sin margen o un píxel roto solo pierde dinero más rápido. **[STRONG INFERENCE]**
- **Gate 1 (economía)**: CPA/CPL break-even y target calculados con números reales. Sin esto no hay criterio para juzgar
  nada. → [09/08](../09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md),
  [05/05](../05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md)
- **Gate 2 (tracking)**: Pixel + CAPI deduplicados, evento de optimización disparando con valor correcto, test de compra/lead
  real verificado en Events Manager y en el backend. **[OFFICIAL META]** → [04](../04-tracking-atribucion-medicion/README.md)
- **Gate 3 (oferta + funnel)**: landing/formulario probado en móvil, carga rápida, message match, proceso comercial listo
  (speed to lead, calendario, setter/closer) o checkout probado.
- **Gate 4 (creatividad)**: conceptos *distintos* (ángulo/persona/formato), no variantes, según presupuesto: 2–4 hasta
  100 €/día, 3–6 entre 100 y 500 €/día, 8–15 por encima ([09 §A.2](09-presupuesto-pequeno-y-grande.md)), con research de mercado
  y de competencia detrás. → [03/11](../03-creatividad/11-sistema-investigacion-creativa-50-100-anuncios.md)
- **Arquitectura por defecto en 2026**: 1 campaña (Sales o Leads), 1 ad set, Advantage+ activado (presupuesto de campaña,
  Advantage+ audience, placements automáticos), evento real, puja Highest volume/value. Complejidad solo si el negocio
  la exige. **[OFFICIAL META]** + **[EMPIRICAL]**
- **Presupuesto**: ≥ ~7× CPA/día por ad set para estabilidad (50 × CPA/semana); si no llegas, consolida y acepta varianza.
- **Las 2–4 primeras semanas son de aprendizaje del NEGOCIO** (qué ángulo vende, qué calidad de lead llega), no solo del
  algoritmo. Decide con la regla de paciencia del [04-operativa](04-operativa-diaria-semanal-mensual.md).

---

## Fase 0 — Objetivo de negocio (1 h)

Preguntas obligatorias (y respuesta escrita):

| Pregunta | Por qué |
|---|---|
| ¿Qué resultado de negocio queremos y en qué plazo? (ventas, cash, citas, pacientes, MRR) | Define el evento de optimización y el KPI |
| ¿Adquisición de clientes nuevos o ventas totales? | Customer Lifecycle Strategy / exclusiones / reporting de segments |
| ¿Cuánta capacidad operativa hay? (stock, agenda del equipo comercial, plazas) | Techo de escalado; leads sin atender = dinero tirado |
| ¿Qué presupuesto mensual y qué tolerancia a pérdidas durante el aprendizaje? | Arquitectura y horizonte |
| ¿Qué mercados/idiomas? | Economía por país, location fees (UK 2 %, ES/FR/IT 3 %, AT/TR 5 %), separación |
| ¿Categoría especial o sensible? (finanzas, empleo, vivienda, salud, política) | Restricciones de targeting y de eventos → [08](../08-cuenta-politicas-seguridad/README.md) |

## Fase 1 — Economía (Gate 1)

1. Contribución por venta = ingreso neto (sin IVA, menos devoluciones/impagos) − costes variables (producto, envío,
   pasarela, comisiones de venta, entrega). **= CPA break-even.**
2. Ecommerce: ROAS break-even = (1 + fees) / CM % **en la misma base que el valor que recibe Meta** (si envías valor con
   IVA, el break-even sube). → [06/05](../06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md)
3. Lead gen: CPL máx = contribución × P(venta | lead) = contribución × cualificación × booking × show × close.
   Calculadora, desde la raíz del proyecto: `python3 -I herramientas/economia.py leadgen` (`--help` para las opciones).
4. Target = break-even × (1 − margen objetivo). Si hay LTV demostrado por cohortes, puedes pagar más en primera compra
   **solo** si la caja aguanta el payback.
5. Supuestos iniciales del funnel (si no hay histórico): usar rangos conservadores y marcarlos como hipótesis a validar
   en semana 2–4.

**Gate**: tabla con break-even y target por etapa (CPL, coste por cualificado, por cita, por show, por venta / CPA, ROAS).

## Fase 2 — Tracking (Gate 2)

Checklist mínima (detalle técnico en [04/02](../04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md)
y [04/16](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md)):

- [ ] Business Portfolio propio del cliente (no del freelance/agencia) con 2FA, ≥2 admins, dominio verificado. → [08/03](../08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md)
- [ ] **Un único dataset** para la web (reutilizar el existente si hay historial; nunca "píxel nuevo" por superstición — mito M58).
- [ ] Pixel + Conversions API con deduplicación (`event_id` + `event_name` iguales en navegador y servidor).
- [ ] Evento de optimización con `value` y `currency` correctos (ecommerce), `content_ids` si hay catálogo.
- [ ] Parámetros de cliente para matching (email/teléfono hasheados, `fbp`, `fbc`, `external_id`, IP, UA).
- [ ] Prueba real: compra/lead de test → aparece en Test Events y en el backend (Shopify/Stripe/CRM) con el mismo valor.
- [ ] Lead gen: lead ID guardado en el CRM y plan de devolución de etapas por CAPI (qualified leads exige CAPI desde abr-2026).
- [ ] UTMs dinámicos en todos los anuncios (plantilla única en [10-plantillas §8](10-plantillas.md))
      y redirecciones que no pierdan `fbclid`.
- [ ] UE: banner de consentimiento coherente con el envío de eventos; no enviar datos de salud/finanzas sensibles en parámetros.
- [ ] Opt-in de breakdowns adicionales (device/hour/frequency) si se usará la API (sin opt-in devuelven vacío desde 6-ago-2026).

**Gate**: 3 conversiones de prueba reconciliadas; EMQ "Good" o mejor (≥6,0 recomendado por Meta) en el evento principal.

## Fase 3 — Oferta y funnel (Gate 3)

- **Oferta**: ¿por qué alguien compraría HOY y a nosotros? Mecanismo, prueba, garantía, urgencia legítima. El mejor
  anuncio no arregla una mala oferta. → [03/09](../03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md)
- **Destino según modelo**:

| Modelo | Destino por defecto | Alternativas |
|---|---|---|
| Ecommerce | Página de producto/landing de oferta + checkout probado | Catálogo (Advantage+ catalog ads) si hay surtido |
| Lead gen servicios / local | Instant form Higher intent (3–5 preguntas) o website form | Click-to-WhatsApp (optimizando a leads, no a conversaciones, donde esté disponible) |
| High-ticket | VSL/landing → aplicación → calendario → setter/closer | Instant form + llamada inmediata; DM setting por IG/WhatsApp; webinar |
| Infoproducto bajo ticket | Página de venta con checkout | Webinar/challenge |
| SaaS / B2B | Trial o demo según motion | Lead magnet cualificado + nurturing |

  → [14-playbooks](../14-playbooks/)
- **Landing**: mobile-first, LCP rápido, promesa del anuncio visible above the fold (message match), una CTA, prueba
  social, objeciones resueltas. → [03/09](../03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md)
- **Ventas**: speed to lead < 5 min en horario, recordatorios de cita (show rate), guion de cualificación, registro en CRM
  con ad_id/UTM. → [05/08](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md)
- **Política**: revisar copy y landing contra Advertising Standards (claims de ingresos, salud, antes/después, atributos
  personales). → [08/08](../08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md),
  [08/11](../08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md)

**Gate**: recorrido completo probado en móvil por alguien ajeno; proceso comercial con responsable y SLA.

## Fase 4 — Investigación creativa

1. **Voice of customer**: reseñas, comentarios, llamadas de ventas, encuestas, Reddit/foros → deseos, dolores,
   objeciones, lenguaje literal.
2. **Competencia**: Meta Ad Library (en la UE con datos de alcance; fuera de la UE solo anuncios activos), 50–100 anuncios
   clasificados por ángulo/hook/formato/oferta/prueba/CTA/landing. La longevidad es una señal, no una prueba de
   rentabilidad. → [03/10](../03-creatividad/10-investigacion-competencia-ad-library.md),
   [03/11](../03-creatividad/11-sistema-investigacion-creativa-50-100-anuncios.md)
3. **Nivel de awareness y sofisticación del mercado** → qué tipo de mensaje abre (problema, mecanismo nuevo, prueba,
   identidad, oferta). → [03/03](../03-creatividad/03-estrategia-creativa-primeros-principios.md)
4. **Matriz de ángulos**: 5–10 ángulos candidatos (razón de compra × persona × awareness), priorizados por tamaño de
   demanda y diferenciación.

## Fase 5 — Producción (Gate 4)

- Primer lote: **3–6 conceptos distintos** (cuentas pequeñas, 100–500 €/día) o **8–15** (medianas), mezclando formatos
  (estático, UGC/creator, demo, founder, testimonial, carrusel) y ángulos. No 10 versiones del mismo vídeo.
  **[EMPIRICAL]** Hasta 100 €/día, **2–4**: más conceptos que presupuesto dejan la mayoría sin señal
  ([09 §A.2](09-presupuesto-pequeno-y-grande.md), regla 3, con la tabla del criterio único).
- Cada concepto con 2–3 hooks como máximo (variantes dentro de un anuncio flexible/multi-media si procede).
- Specs: 9:16 para Reels/Stories con safe zones (14 % arriba, 35 % abajo, 6 % laterales), 4:5 para Feed; subtítulos;
  primeros 2–3 s con el gancho. → [07/03](../07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md)
- **Política de defaults de IA**: decidir qué Advantage+ creative enhancements quedan ON (algunas vienen activadas por
  defecto, incluida la reescritura de texto dentro de imágenes observada desde ~jul-2026). El anunciante responde del
  contenido generado. → [03/14](../03-creatividad/14-herramientas-ia-creativa-meta.md)

**Gate**: lote aprobado por política interna (claims) y por el cliente; nomenclatura de anuncios estándar
(`AAAAMMDD_angulo_concepto_formato_h<n>[-c<n>]`, la de [10-plantillas §8](10-plantillas.md)).

## Fase 6 — Arquitectura

Default 2026 (ajustar con [02/05](../02-estructura-campanas/05-arquitectura-de-campanas.md)):

```
Campaña: objetivo Sales (o Leads / App) · Advantage+ ON (campaign budget + Advantage+ audience + placements)
  └─ Ad set único: país(es) objetivo · edad mínima solo si es legal/de negocio · evento real
       · puja Highest volume (o Highest value si hay ≥50 compras/semana con valores distintos)
       · Customer Lifecycle Strategy "adquirir clientes nuevos" si el KPI es nCAC (o exclusión de compradores)
       └─ 3–15 anuncios de conceptos distintos (según presupuesto)
```

Separar solo si: economía distinta por país/producto, objetivo distinto (adquisición vs retención), categoría especial,
o test que necesita gasto garantizado. Retargeting separado = excepción con holdout.
→ [02/09](../02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md)

## Fase 7 — Presupuesto

- Presupuesto diario por ad set ≈ **7 × CPA esperado** (50 × CPA/semana). Guía oficial más exigente: ≥10× el coste del
  performance goal; con cost per result goal ≥5× el objetivo. **[OFFICIAL META]**
- Si no llegas: 1 ad set, evento real y paciencia; o evento más barato que **siga siendo valioso** (oferta de entrada,
  lead cualificado). Nunca repartir 50 €/día en 5 ad sets.
- Daily budget = media semanal: Meta puede gastar hasta 175 % un día, ≤7× por semana. Cuentas nuevas tienen límite de
  gasto diario fijado por Meta. → [02/06](../02-estructura-campanas/06-presupuesto-por-niveles.md)
- Reservar 15–30 % del presupuesto para testing creativo desde el mes 2 (Meta recomendaba 20–30 %).

## Fase 8 — Lanzamiento (día 0)

- [ ] Revisión cruzada (otra persona) de: país, idioma, evento, ventana de atribución (verificar en el ad set: 7d click + 1d view, y si engage-through 1d está
      activado; el Help Center no documenta el default), URL + UTMs, placements/assets por formato, enhancements, exclusiones, presupuesto y fecha.
- [ ] Lanzar todo junto (no anuncio a anuncio a lo largo de días) para no encadenar learning.
- [ ] Anotar en el change log: configuración inicial, hipótesis, fecha de primera evaluación.
- [ ] Alertas: gasto anómalo, 0 eventos en X horas, rechazos, cuenta restringida.

## Fase 9 — Medición y primeras decisiones

| Momento | Qué mirar | Qué decidir |
|---|---|---|
| Día 1–3 | Entrega, gasto, eventos llegando, rechazos, CTR/hook gruesos | Solo corregir errores |
| Semana 1 | Gasto por anuncio, CPM/CTR/CVR, calidad inicial de leads | Apagar lo claramente roto (≥2–3× CPA sin conversión) |
| Semana 2–4 | CPA/CPL vs target con ventana madurada; cohortes de leads (cualificación, booking) | Nuevo lote creativo; ajustar oferta/landing; primer juicio de viabilidad |
| Mes 2 | Coste por venta real (lead gen), nCAC/MER (ecommerce) | Escalar, mantener o pivotar oferta/canal |
| Mes 3+ | Incrementalidad (holdout/geo/lift si hay volumen), LTV por cohorte | Presupuesto total y arquitectura |

**Criterio de viabilidad (semana 4)**: ¿el coste por venta/CPA está a ≤1,5× del target con tendencia a mejorar y hay
ángulos con señal? Si no, revisar en este orden: oferta → funnel/landing → evento de optimización → creatividad →
estructura. **[STRONG INFERENCE]**

## Errores frecuentes al lanzar

1. Lanzar sin break-even calculado ("a ver qué CPA sale").
2. Píxel sin CAPI o sin deduplicar; valor con IVA comparado con break-even sin IVA.
3. Cinco ad sets de intereses con 10 €/día cada uno.
4. Un solo concepto en 6 variantes.
5. Optimizar a tráfico/engagement "para calentar el píxel" (mito M59).
6. Juzgar el día 2.
7. No tener a nadie llamando a los leads en 5 minutos.
8. Copiar la estructura de una cuenta de 50.000 €/día con 100 €/día.
