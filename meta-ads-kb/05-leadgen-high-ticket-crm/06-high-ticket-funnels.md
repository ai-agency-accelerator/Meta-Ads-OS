# Funnels high-ticket en Meta: VSL + aplicación + calendario, setter/closer, DM setting, webinar, tripwire y challenge

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: ofertas de 2.000-50.000 € vendidas por llamada o conversación (coaching, consultoría, formación premium, servicios de agencia). Estructura de campaña y evento de optimización por tipo de funnel, benchmarks con fuente, riesgos de cuenta. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **El funnel high-ticket es un sistema de filtros con un cuello de botella humano.** Meta trae personas; la página/formulario filtra; el calendario y el setter convierten interés en cita; el closer convierte cita en cash. Optimizar Meta sin medir agenda, show y cierre por anuncio es optimizar a ciegas. **[STRONG INFERENCE]**
- **Evento de optimización:** casi nunca la venta (volumen <50/semana y a menudo fuera de 28 días). Por orden: `Schedule`/aplicación cualificada (web) o **qualified leads** con etapa "cualificado"/"agendado" (instant form + CAPI CRM); Sequenced Events `Lead → Schedule` cuando aparezca en la cuenta. **[OFFICIAL META]** (requisitos) + **[STRONG INFERENCE]** (elección) (S05-001, S05-007, S05-034)
- **Arquitectura por defecto en 2026:** Leads objective en configuración Advantage+ (es el default: presupuesto de campaña, Advantage+ audience y placements) con pocas creatividades fuertes por ángulo; tus audiencias y lookalikes de clientes como *sugerencias*; exclusiones de clientes y leads recientes como controles. **[OFFICIAL META]** (S05-066, S05-010)
- **Benchmarks (todos de agencias/vendors, sin metodología auditada):** coste por llamada agendada desde Meta 150-350 $ (coaching 2-15 k$); booking 40-50% de aplicaciones; show 75-85% "con secuencia pre-llamada" vs 45-55% sin ella; cierre 25-40% de shows; cierre medio de ventas cross-industria 29% (HubSpot 2025). Úsalos como contraste, nunca como objetivo. **[EMPIRICAL]** débil (S05-041, S05-042, S05-087, S05-088)
- **Elegir funnel por ticket y volumen:** 2-5 k€ con mucho volumen → webinar/VSL con compra directa o llamada corta de setter; 5-20 k€ → VSL + aplicación + llamada; 20 k€+ o B2B → aplicación/diagnóstico + llamada consultiva; audiencias de Instagram con marca personal → DM setting. **[STRONG INFERENCE]**
- **Riesgo de cuenta en "make money"/oportunidades de negocio:** Meta prohíbe promesas de enriquecimiento rápido o con poco esfuerzo y exige describir el modelo de negocio; revisa anuncio + landing + formulario como un todo. Ver área 08 para el detalle. **[OFFICIAL META]** (S05-071)

---

## 1. Anatomía del funnel clásico: anuncio → VSL → aplicación → calendario → setter → closer

```
Anuncio (ángulo + prueba + llamada a ver el vídeo)
  → Landing con VSL (8-20 min) + casos + para quién NO es + (opcional) rango de precio
    → Aplicación (6-10 preguntas; multiple choice primero, contacto al final)
      → Lógica: cualificado → calendario | no cualificado → recurso gratuito/oferta low-ticket
        → Página de confirmación: vídeo "qué pasará en la llamada", casos, checklist, añadir al calendario
          → Setter (opcional): confirma por WhatsApp/llamada en minutos, cualifica, reduce no-show
            → Closer: llamada de 45-60 min → pago único / plan / financiación
              → Onboarding (el reembolso se decide en las primeras 2 semanas)
```

### Qué filtra cada pieza
| Pieza | Filtra | Métrica | Rango orientativo (fuente, confianza) |
|---|---|---|---|
| Anuncio | Relevancia, promesa | CTR enlace, coste por visita a landing | — |
| VSL | Encaje, creencias, precio | % que ve >50%, CVR landing→aplicación | Landing a aplicación 8-12% (landing) / 15-40% (VSL) según vendor (S05-087, baja) |
| Aplicación | Capacidad, urgencia, autoridad | % cualificados | Depende de tu criterio; 30-60% típico **[HYPOTHESIS]** |
| Calendario | Compromiso | Aplicación → agenda | 40-50% (S05-041, baja); 60-80% tras ver VSL completo (S05-087, baja) |
| Confirmación + setter | No-show | Show rate | 45-55% sin secuencia vs 75-85% con ella (S05-087, baja); 75-85% "típico" (S05-041, baja) |
| Closer | Decisión | Cierre sobre shows | 25-40% (S05-041, baja); 15-20% CFO fraccional, 45-50% coaching ejecutivo (S05-041) |

### Principios de diseño
1. **Pon la fricción donde filtra al no-comprador, no al comprador:** precio o rango visible, "para quién no es", preguntas de urgencia y capacidad. **[STRONG INFERENCE]**
2. **Calendario solo para cualificados** (lógica condicional en el formulario o routing del calendario). Las agendas de no cualificados cuestan horas de closer y ensucian la señal si optimizas a `Schedule`.
3. **La página de confirmación es parte del funnel de show**, no un "gracias" (archivo 08).
4. **Setter:** contacto en <5 min por el canal preferido (WhatsApp en España), reconfirmación 24 h y 1-2 h antes. **[STRONG INFERENCE]** sobre la base de S05-037/038.

## 2. Variantes y cuándo usar cada una

| Funnel | Cuándo | Evento de optimización | Ventajas | Riesgos |
|---|---|---|---|---|
| **VSL + aplicación + llamada** | 5-20 k€, oferta compleja, closer disponible | `Schedule` o "aplicación cualificada" (CAPI); Sequenced `Lead → Schedule` | Máximo control de calidad; la VSL vende antes de la llamada | CPL alto; dependes del tracking web |
| **Instant form Higher intent → setter** | Volumen, audiencias móviles, equipo de setters rápido | Qualified leads (cualificado/agendado vía CAPI CRM) | CPL bajo, aprendizaje rápido | Leads con poco contexto; exige contacto en minutos |
| **Instant form + booking embebido (2026)** | Igual que el anterior, sin setter o con setter post-booking | Qualified leads (agendado/show) | Reserva en el pico de interés; no-show menor estimado | Solo Facebook; despliegue progresivo |
| **DM setting (IG Direct / WhatsApp)** | Marca personal, coaching, audiencia IG; setters que conversan | Leads through messaging / conversaciones; compras CAPI solo Messenger/WA | Alta intención, conversación natural | IG no optimizable por eventos downstream; UE con funciones limitadas; caro en horas de setter |
| **Webinar (en directo o evergreen) → aplicación/llamada** | Educación necesaria, audiencias frías grandes | CompleteRegistration (registro) + retargeting; aplicación como evento secundario | Escala; filtra por asistencia | Show en directo bajo; el algoritmo optimiza registros, no asistentes (archivo 07) |
| **Low-ticket front-end / tripwire → llamada** | Mercados con mucha competencia por el lead, cuando quieres señal de compra | Purchase (front-end) | Autofinancia la adquisición; comprador > lead | Complejidad; si el front-end no se liquida, pierdes |
| **Challenge (3-5 días) → oferta** | Lanzamientos, comunidad, info-producto | CompleteRegistration / Purchase (si challenge de pago) | Compromiso progresivo | Calendario de lanzamiento rígido; muy dependiente del host |
| **Diagnóstico/auditoría gratuita** | B2B, servicios de agencia | Qualified leads (SQL) / Schedule | Valor percibido alto | Atrae "curiosos" si no se filtra |

## 3. Estructura de campaña por presupuesto

Punto de partida (el detalle de estructura y escalado es de las áreas 02 y 09):

| Presupuesto mensual | Estructura | Optimización |
|---|---|---|
| < 3.000 € | 1 campaña Leads (Advantage+), 1 ad set, 4-8 anuncios de 2-3 ángulos | El evento más profundo con ≥20-30 eventos/semana; normalmente "Lead" (aplicación) o qualified leads a "cualificado" |
| 3.000-15.000 € | 1 campaña prospección (Advantage+) + 1 campaña pequeña de retargeting/prueba (5-15%) | Qualified leads a "agendado" o `Schedule` si ≥30-50/semana |
| 15.000-60.000 € | Prospección consolidada + campaña de testing creativo + retargeting; posible segunda oferta/canal (webinar o DM) | Etapa más profunda viable (show) o value con valores esperados |
| > 60.000 € | Varias campañas por oferta/canal, controles de cuenta, análisis de cohortes | Igual + incrementalidad (lift tests, área 04) |

**Retargeting en high-ticket:** audiencias de visitantes de VSL >50%, aplicaciones iniciadas no enviadas, "abrió el formulario y no lo envió" (Meta lo recomienda), interacción en IG. Creatividades de **prueba** (casos, testimonios en vídeo, desglose del método) y de **objeciones** (precio, tiempo, "¿funciona para mí?"). Presupuesto típico 5-15% del total **[HYPOTHESIS]** (heurística de practicantes, sin fuente sólida). Con Advantage+ audience, gran parte del retargeting ocurre "solo"; la campaña separada sirve para controlar el mensaje.

**Exclusiones:** clientes actuales y leads de los últimos 30-90 días como *excluded custom audiences* (son controles, no sugerencias). Desde octubre de 2026 Meta ofrece además "Customer Lifecycle Strategy" con recomendaciones de excluir clientes en campañas de adquisición (S05-049). **[EMPIRICAL]**

## 4. Creatividades que funcionan en high-ticket (lo que sí sabemos)

- **Prueba > promesa:** casos con contexto (antes/después de negocio, no de ingresos personales irreales), demostración del método, autoridad del experto. Las promesas de ingresos son además un riesgo de política (§7).
- **Ángulos por segmento de dolor**, no por demografía (Advantage+ segmenta por creatividad). El área 03 cubre creative-as-targeting.
- **Formato:** vídeo del experto hablando a cámara + subtítulos para la VSL corta; carruseles de casos para retargeting; imágenes con titular para testing barato. Metadata (B2B, 2025) encontró CPL de imagen 136 $ vs vídeo 225 $ en Facebook, lo que contradice la intuición de "vídeo siempre" en lead gen. **[EMPIRICAL]** (S05-044, B2B, no coaching)
- **Filtra en el anuncio:** "No es para ti si…", rango de inversión, requisitos (p.ej. "negocios que ya facturan…" — cuidado con atributos personales, área 08).

## 5. Setter / closer: diseño del equipo y métricas

| Rol | Responsabilidad | KPIs | Notas |
|---|---|---|---|
| Setter | Contactar en <5 min, cualificar, agendar, reconfirmar | Speed to lead, tasa de contacto, lead→agenda, show rate de sus agendas | Por WhatsApp/llamada; scripts de cualificación con criterios escritos |
| Closer | Diagnóstico y cierre | Show→cierre, cash cobrado, % PIF, impagos/reembolsos de sus ventas | Comisión sobre **cash cobrado** |
| Marketing/media buyer | Volumen y calidad por anuncio | CPL, CPQL, coste por agenda, coste por show, CPA por anuncio | Informe semanal con ventas |

Compensación (fuentes débiles, ofertas de empleo y blogs): closers experimentados 10-20% de comisión, iniciales 5-10% + fijo; setters fijo bajo + bonus por agenda/show o % menor (S05-072). **[EMPIRICAL]** débil. Diseña la comisión del setter sobre **shows cualificados**, no sobre agendas brutas, para no incentivar agendar a cualquiera. **[STRONG INFERENCE]**

**Separar problema de marketing vs problema de ventas:**
- Si show y cierre son estables y el CPA sube → problema de Meta/creatividad/oferta.
- Si el coste por agenda es estable pero el CPA sube → problema de show/cierre (ventas, calendario, calidad oculta).
- Si un closer cierra el 30% y otro el 12% con los mismos leads → problema de persona, no de campaña.
- Cruza **por anuncio**: ángulos que atraen agendas que no cierran (p.ej. promesas demasiado fáciles) son la causa más común de "leads basura" en high-ticket. **[STRONG INFERENCE]**

## 6. Benchmarks con su fuente (léelos con escepticismo)

| Métrica | Valor | Fuente | Confianza |
|---|---|---|---|
| Coste por llamada agendada (Meta, coaching 2-15 k$) | 150-350 $ | 780 Marketing, 2026 (15+ clientes) | baja-media |
| Coste por llamada por tramo de precio | 60-220 $ (3-15 k), 180-550 $ (15-50 k), 400-1.200+ $ (50 k+) | Leads Now AI, 2026 (Australia) | baja |
| Booking (aplicación → agenda) | 40-50% | Inflo Partners, 2026 | baja |
| Show rate | 75-85% "típico"; <70% = problema | Inflo Partners, 2026 | baja |
| Show con/sin secuencia pre-llamada | 75-85% / 45-55% | Inflo Partners (VSL), 2026 | baja |
| No-show "lead form de paid social" | ~33% (show ~67%) | Focus Digital, 2026 (estimación) | baja-media |
| Show inbound reservado en pocos días | ≥76% "bueno"; ~60% si se reserva a 2 semanas | Leads Now AI (análisis secundario de ~6.400 reuniones) | baja |
| Cierre (sobre shows) | 25-40% | Inflo Partners, 2026 | baja |
| Cierre medio de ventas cross-industria | 29% | HubSpot State of Sales 2025 (vía resumen) | media |
| Conversión de llamadas por tamaño de deal | <10 k$: 25,73% | Focus Digital, 2026 | baja-media |

Conclusión: los rangos son coherentes entre sí (show 60-85%, cierre 15-40%) pero **ninguno tiene metodología pública fuerte**. Tu primer mes debe servir para medir tus propias tasas por canal y por anuncio.

## 7. Infoproductos, "make money" y riesgos de cuenta (solo lo que afecta al funnel)

- Meta (Transparency Center, *Unrealistic outcomes*): los anuncios de oportunidades de ingreso deben describir el producto o modelo de negocio y no pueden promover modelos de "compensación rápida por poca inversión" (incluido MLM); prohibidas las afirmaciones de enriquecimiento rápido o de ganar dinero sin apenas trabajo. **[OFFICIAL META]** (texto vía buscador, S05-071; detalle en área 08).
- **El revisor mira el conjunto**: anuncio + landing + formulario. Capturas de ingresos, "ingresos garantizados" y "gana dinero rápido" en la landing pueden tumbar un anuncio limpio. **[EMPIRICAL]** (guías secundarias)
- **Funnels típicos de riesgo:** VSL con promesas de ingresos, "sistema" para dejar el trabajo, trading/cripto/IA "sin experiencia", testimonios de ingresos sin contexto, urgencia falsa (contadores que se reinician), precio oculto + presión en llamada → reembolsos y chargebacks → riesgo también con la pasarela de pagos. **[STRONG INFERENCE]**
- **Preguntas del formulario:** no pidas ingresos/patrimonio/deudas (prohibido en instant forms, S05-016).
- **Recomendación:** venderse como formación/servicio con resultados medibles de *proceso* ("sistema de captación para clínicas") y prueba verificable; mantener el mismo tono en anuncio, VSL y llamada. Coordinar con el área 08.

## 8. Medición mínima viable para high-ticket

1. Cada lead con `ad_id` (UTM/tracking parameter) y `meta_lead_id`/`fbc`.
2. Etapas: raw_lead → contactado → cualificado → agendado → show → ganado/perdido (+ motivo) → cash cobrado por mes. Es un ejemplo: en Meta Ads OS, las etapas y los eventos son los de la tabla del contrato §16 (`docs/desarrollo/contratos.md`), de `Lead` a `Purchase`.
3. Informe semanal por anuncio: inversión, leads, cualificados, agendas, shows, ventas, cash día 0, cash esperado (archivo 09).
4. Enviar etapas a Meta (qualified leads) o eventos web (`Schedule`, aplicación cualificada).
5. Revisar cohortes por mes de captación a 30/60/90 días.

## Implicaciones operativas

- Elige el funnel por ticket y capacidad comercial; no copies el funnel de un gurú con otra economía.
- Optimiza a la etapa más profunda con ≥30-50 eventos/semana; envía todas las demás para medir.
- Mide coste por agenda y por show desde la primera semana contra el target del archivo 05.
- Antes de culpar a Meta por "leads basura", revisa speed to lead, show rate por setter y cierre por closer.

## Errores frecuentes

- Calendario abierto a todos los aplicantes → agenda llena de no cualificados, closers quemados, señal `Schedule` contaminada.
- Optimizar a "Lead" en un funnel de aplicación larga y escalar por CPL.
- Comisiones sobre contrato firmado en lugar de cash cobrado.
- Promesas de ingresos en anuncios o VSL (riesgo de cuenta y de reembolsos).
- No registrar motivos de pérdida: no se puede mejorar el anuncio que atrae al perfil equivocado.

## Preguntas abiertas

- No hay benchmarks públicos con metodología para show/cierre de high-ticket en España.
- Efecto del booking embebido (2026) sobre show y cierre en high-ticket: sin datos aún.
- Si Sequenced Events `Lead → Schedule` supera a optimizar directamente `Schedule`.

## Fuentes clave

- [About performance goals for lead ads](https://www.facebook.com/business/help/782657799338685) — meta-oficial (S05-007)
- [Conversions API for CRM integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) — meta-developers (S05-001)
- [Unrealistic outcomes (Advertising Standards)](https://transparency.meta.com/policies/ad-standards/deceptive-content/unrealistic-outcomes) — vigente — meta-oficial (S05-071)
- [Cost Per Booked Call Benchmarks for High-Ticket Coaches](https://www.780marketing.ca/articles/cost-per-booked-call-benchmarks) — 2026-07-03 — agencia (S05-042)
- [High-Ticket Sales Metrics](https://www.inflopartners.com/blog/high-ticket-sales-metrics-tracking) — 2026-09-05 — agencia (S05-041)
- [VSL Funnel for High-Ticket Coaching](https://www.inflopartners.com/blog/vsl-funnel-high-ticket-coaching) — 2026 — agencia (S05-087)
- [Average No-Show Rate by Booking Channel 2026](https://focus-digital.co/average-no-show-rate-for-booked-sales-meetings-by-booking-channel/) — 2026-09-14 — agencia (S05-040)
- [Meta ads for B2B (2026 B2B Paid Media Benchmark)](https://metadata.io/resources/blog/fb-ad-strategies) — 2026-09-11 — vendor (S05-044)
