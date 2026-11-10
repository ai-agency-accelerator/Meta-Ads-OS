# Operativa: monitorización diaria, revisión semanal, revisión mensual

> Última verificación: 2026-10-16 · Autor: agente principal · Ámbito: qué mirar, con qué frecuencia, qué decidir y qué
> NO tocar. Basado en [09/10-dashboards](../09-bidding-escalado-economia-analitica/10-dashboards-reporting.md),
> [09/11-cuando-no-tocar](../09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md) y
> [09/12-estadística](../09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md).

## TL;DR

- **Diario = salud, no rendimiento.** Se buscan roturas (tracking, gasto, entrega, rechazos, web, ventas comerciales sin
  atender). No se toman decisiones de optimización con el CPA de ayer. **[STRONG INFERENCE]**
- **Semanal = decisiones tácticas** (creatividades, presupuesto, pujas) en una ventana de edición fija, sobre semanas
  completas y con la ventana de atribución madurada. **[OFFICIAL META]** (Meta: analizar al menos una semana completa;
  esperar 7 días tras ajustes en goal-based)
- **Mensual = estrategia y economía** (presupuesto total, mix adquisición/retención, oferta, incrementalidad, roadmap
  creativo, deuda técnica por cambios de Meta). **[STRONG INFERENCE]**
- **Regla de paciencia**: no evaluar un cambio hasta cumplir ≥7 días, ≥30–50 eventos desde el cambio y ventana madurada
  (tope práctico 14–21 días en cuentas de bajo volumen).
- **Toda edición entra en el change log** con hipótesis y fecha de evaluación.

---

## 1. Monitorización diaria (10–20 min)

### Qué mirar

| Bloque | Señal | Umbral de alarma (orientativo) | Acción |
|---|---|---|---|
| Ventas del negocio | Pedidos/leads/citas totales en backend vs media del mismo día de la semana | Caída > banda de ruido (≈ ±2√n eventos) o 0 eventos en horas de actividad | Revisar web, checkout, formularios, tracking |
| Tracking | Eventos en Events Manager (pixel y servidor), errores de deduplicación, diagnósticos | Evento principal a 0 o desfase servidor/navegador anómalo | Actuar ya (prioridad 1) |
| Gasto | Gasto de hoy vs ritmo semanal | >175 % del diario en un día sin budget sharing/scheduling; o gasto ≈ 0 | Revisar delivery, pagos, límites |
| Entrega | Estado de campañas/ad sets/anuncios, rechazos, "learning limited" nuevo | Anuncios rechazados, cuenta restringida, pago fallido | Resolver; ver [08](../08-cuenta-politicas-seguridad/README.md) |
| Comercial (lead gen) | Leads sin contactar, tiempo de respuesta, citas del día | Speed to lead > 5–15 min en horario; leads sin dueño | Escalar al equipo comercial |
| Comentarios | Comentarios negativos/spam en anuncios con gasto | Spam, ataques, preguntas sin responder | Ocultar (mejor que borrar), responder |
| Plataforma | Status page de Meta, cambios anunciados | Incidente activo | No tocar nada; anotar |

### Qué NO hacer a diario

- Pausar anuncios o ad sets por el CPA de 1–3 días (ruido de Poisson + atribución incompleta).
- Bajar o subir presupuesto por un día malo/bueno.
- Cambiar pujas o cost caps antes de 7 días desde el último ajuste.
- Leer el CPA de "ayer" como definitivo: con 7d click aún llegarán conversiones durante una semana.
- Cortar placements/horas/edades por su CPA parcial (*breakdown effect*).

### Bandas de ruido rápidas (Poisson)

| Eventos medios/día | Rango normal 95 % (aprox.) |
|---|---|
| 5 | 1–10 |
| 10 | 4–17 |
| 20 | 12–29 |
| 50 | 37–64 |

Fuera de la banda varios días seguidos → investigar; un día fuera → anotar y esperar. **[STRONG INFERENCE]**

## 2. Revisión semanal (60–120 min, día fijo)

**Unidad**: donde vive el presupuesto (campaña con campaign budget o ad set con presupuesto propio). **Periodo**: semana
natural completa, comparada con la anterior y con la misma semana del año pasado si hay estacionalidad.

### Orden (de arriba abajo)

1. **Negocio**: revenue neto, contribución tras marketing, MER, nCAC/% clientes nuevos, cash collected (high-ticket),
   comparado con target. ¿Hay problema? Si no lo hay, no se fuerza ninguna optimización.
2. **Funnel**: ecommerce (LPV rate, ATC, checkout, CVR, AOV); lead gen por cohorte (CPL → CPQL → coste por cita → por show
   → por venta, con lag). Identificar la etapa que se rompe.
3. **Anuncios**: CPA/ROAS en la ventana de optimización + lectura conservadora 1d click; descomposición CPM/CTR/CVR del
   cambio; frecuencia y alcance; audience segments (nuevos/engaged/existentes); estado de learning; gasto vs presupuesto.
4. **Creatividad**: spend share por anuncio y concepto; hook/hold/CTR de los que llevan el gasto; anuncios nuevos con y sin
   gasto; señales de fatiga por cohorte de antigüedad (CPA por impresiones acumuladas, no frecuencia sola).
5. **Decisiones** (máx. 1–3 palancas por unidad):
   - Lote creativo nuevo (siempre hay uno en cola).
   - Apagar anuncios con ≥2–3× CPA sin conversión o CPA ≥2–3× la media con gasto relevante.
   - Presupuesto: subir si CPA marginal estimado < break-even y hay ≥2 semanas estables; bajar si coste marginal >
     break-even.
   - Pujas: ajustes de 5–10 % en goal-based, con ≥7 días entre cambios.
   - Value rules / exclusiones si un segmento demostrado (≥ semanas de datos) rinde mal.
6. **Change log**: cada decisión con hipótesis, métrica de éxito y fecha de evaluación.

### Plantilla de semana

| Métrica | Semana actual | Semana anterior | Δ | Target | Comentario |
|---|---|---|---|---|---|
| Revenue neto / cash | | | | | |
| Gasto Meta | | | | | |
| MER / nCAC | | | | | |
| CPA (7d click) / CPA (1d click) | | | | | |
| CPM / CTR link / CVR | | | | | |
| % gasto en clientes existentes (segments) | | | | | |
| Anuncios nuevos lanzados / con gasto > 1× CPA | | | | | |
| (Lead gen) CPL / CPQL / coste por cita / por show / por venta (cohorte) | | | | | |

## 3. Revisión mensual (medio día)

| Bloque | Preguntas |
|---|---|
| Economía | ¿Siguen vigentes break-even y targets? (precios, márgenes, close rate, refunds, fees de Meta por país) ¿LTV por cohorte confirma lo que pagamos? |
| Presupuesto total | ¿Dónde está el coste marginal? ¿Subir, mantener o bajar el gasto total? ¿Mix adquisición/retención? |
| Incrementalidad | ¿Qué parte de lo atribuido es incremental? (holdout, geo-test, Conversion Lift, incremental attribution como lectura adicional) ¿Retargeting/existing customers inflan? |
| Creatividad | Aprendizajes por ángulo/persona/formato; hit rate; volumen vs capacidad; roadmap del mes siguiente |
| Oferta y funnel | ¿El cuello de botella es la oferta, la landing o ventas? ¿Qué test de oferta/landing toca? |
| Estructura | ¿Hay fragmentación? ¿Ad sets en learning limited permanente? ¿Duplicados? ¿Campañas zombis? |
| Señal | EMQ, cobertura CAPI, deduplicación, etapas CRM devueltas, eventos con valor correcto |
| Plataforma | Cambios de Meta del mes (changelog) y su impacto: atribución, placements, defaults de IA, API, políticas |
| Riesgo | Account Quality, rechazos, admins y accesos (offboarding), métodos de pago de respaldo |

**Salida**: plan del mes con 3–5 prioridades, presupuesto, calendario creativo y tests (con hipótesis y potencia).

## 4. Revisión trimestral

- Test de incrementalidad (si hay volumen) o, como mínimo, análisis pre/post y geo natural.
- Revisión de arquitectura completa contra el [framework de auditoría](02-framework-auditoria.md).
- Re-baseline de KPIs si Meta cambió definiciones (p. ej. click-through solo link clicks desde mar-2026).
- Actualizar [00-ESTADO-ACTUAL-2026](../00-ESTADO-ACTUAL-2026.md) con lo aprendido.

## 5. Disciplina

1. **Ventana de edición fija** (p. ej., martes): las decisiones de rendimiento se agrupan ahí.
2. **Una palanca por vez** por unidad de presupuesto (salvo cambios agrupados intencionadamente).
3. **Evitar cambios tarde en el día** (pueden no aplicarse a tiempo; el límite diario se calcula sobre el mayor
   presupuesto del día). **[OFFICIAL META]**
4. **Alertas automáticas solo para roturas**, nunca reglas que pausen por CPA diario con poco volumen (destruyen valor:
   un anuncio con CPA = objetivo gasta 2× sin convertir el 13,5 % de las veces). → [10/07](../10-cambios-2025-2026-api-ia-automatizacion/07-reglas-automaticas.md)
5. **Estado de maduración** visible en el dashboard (día provisional vs definitivo).
