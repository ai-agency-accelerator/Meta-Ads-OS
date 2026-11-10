# Dashboards de reporting: diario, semanal, mensual, creativo, campaña y negocio

> Última verificación: 2026-10-15 · Autor: A09 (agente) · Ámbito: columnas exactas, cortes, ventanas de atribución, frecuencia de lectura y decisión que habilita cada dashboard; change log; cohortes de lead gen.

## TL;DR

- **Cada dashboard existe para una decisión.** Diario = detectar roturas (no optimizar); semanal = decidir presupuesto/creatividades/pujas; mensual = estrategia y economía; creativo = qué producir; negocio = cuánto invertir en total. **[STRONG INFERENCE]**
- **Unidad de análisis = donde vive el presupuesto** (campaña con A+CB; ad set con presupuesto propio) y **semana completa**; Meta lo recomienda explícitamente y advierte del breakdown effect. **[OFFICIAL META]** ([Understand fluctuations](https://www.facebook.com/business/help/1364841787225722), [A+CB best practices](https://www.facebook.com/business/help/2177212182495139))
- **Ventana**: reportar en la **misma ventana con la que optimizas** (7-day click por defecto en compras) y añadir 1-day click como lectura conservadora; usar "Compare attribution settings" / breakdown por ventana para ver la composición. **[OFFICIAL META]** (coherencia de ventana) + **[EMPIRICAL]** (Loomer)
- **El dashboard diario no lleva CPA de los últimos 1–3 días como señal de decisión** (atribución incompleta + ruido de Poisson). Lleva gasto vs ritmo, entregas rotas, eventos de píxel/CAPI y ventas totales del negocio. **[STRONG INFERENCE]**
- **Primera fila de todo informe = negocio** (revenue neto, contribución tras marketing, MER, nCAC); Meta va después. **[STRONG INFERENCE]**
- **Change log obligatorio**: cada edición con fecha/hora, nivel, de→a y motivo; y fechas de cambios de plataforma (p. ej., click-through = solo link clicks desde mar-2026). **[STRONG INFERENCE]**
- **Lead gen**: el informe clave es la **cohorte de leads por semana de creación** con booking/show/close/cash a 7/30/60/90 días, cortada por campaña/anuncio/segmento. **[STRONG INFERENCE]**

---

## 1. Principios de diseño

1. **Decisión → métrica → umbral**: si una columna no cambia ninguna decisión, sobra.
2. **Comparación correcta**: semana vs semana anterior **y** vs misma semana ISO del año anterior (estacionalidad).
3. **Nivel correcto**: campaña (A+CB) / ad set (presupuesto propio). Breakdowns solo para diagnóstico.
4. **Ventana coherente** con la optimización; marcar cuándo la cifra aún "madura" (últimos 7 días con 7-day click).
5. **Ruido explícito**: mostrar nº de conversiones junto a cada CPA; sombrear CPA con <30 conversiones (ver [12](12-razonamiento-estadistico.md)).
6. **Fuentes**: Meta (atribuido), plataforma de ecommerce/CRM (verdad de negocio), analítica (sesiones), y, si existe, incrementalidad/MMM.

## 2. Dashboard diario (salud / anomalías) — 5 minutos

**Decisión que habilita**: arreglar roturas (pagos, píxel, rechazos, presupuesto agotado, gasto desbocado). **No** decide optimizaciones de rendimiento.

| Columna | Corte | Ventana | Alerta |
|---|---|---|---|
| Gasto ayer vs presupuesto diario | Cuenta y campaña | Ayer | <50 % o >175 % (límite oficial) |
| Gasto semana en curso vs 7 × diario | Campaña | Dom–hoy | Ritmo fuera de ±30 % |
| Delivery status (Learning, Learning limited, Bid/Cost limited, Creative fatigue, Rejected) | Ad set / anuncio | Actual | Cualquier cambio de estado |
| Eventos recibidos (Purchase/Lead) en Events Manager vs media 7 días | Dataset | Ayer | Caída >40 % (posible rotura de tracking) |
| Ventas/leads totales del negocio (Shopify/CRM) | Total | Ayer | Fuera de banda esperada (ver [12](12-razonamiento-estadistico.md)) |
| Resultados atribuidos Meta ayer (informativo) | Cuenta | 7d click | Solo anomalías extremas |
| Anuncios rechazados / avisos de cuenta | Cuenta | — | Cualquiera |

## 3. Dashboard semanal (decisiones de media buying) — el principal

**Decisión que habilita**: subir/bajar presupuestos, ajustar objetivos de puja (±5–10 %), retirar/lanzar creatividades, consolidar ad sets, escalar.

**Periodo**: semana cerrada (lunes–domingo o dom–sáb alineado con el presupuesto de Meta) + semana previa + misma semana ISO año anterior. Releer la semana anterior "madurada".

### 3.1 Bloque negocio (fila superior)

| Columna | Fuente |
|---|---|
| Revenue neto, pedidos, AOV, % nuevos clientes | Ecommerce |
| Gasto marketing total y Meta | Plataformas |
| MER, aMER, nCAC | Cálculo |
| Contribución tras marketing (y vs objetivo) | Cálculo ([08](08-economia-unitaria-calculadoras.md)) |
| Lead gen: leads, cualificados, booked, shows, ventas, cash collected | CRM |

### 3.2 Bloque campaña/ad set (unidad de presupuesto)

| Columna | Notas |
|---|---|
| Estrategia de puja + objetivo (CPR/ROAS goal, bid cap) | De la configuración |
| Presupuesto semanal vs gastado (% de entrega) | Detecta bid-constrained |
| Resultados (evento de optimización) y **nº** | Mostrar n siempre |
| CPA/CPR y ROAS (7d click) + 1d click | Ventana de optimización + conservadora |
| CPM, CTR (link/outbound), CVR, AOV | Descomposición (ver [09](09-taxonomia-metricas-diagnostico-top-down.md)) |
| Reparto del cambio de CPA (CPM/CTR/CVR) | Δln |
| Frecuencia 7d, alcance | Saturación |
| Resultados desde el último significant edit + fecha del edit | Learning |
| Δgasto, Δconversiones, **CPA marginal** del incremento | Escalado ([03](03-escalado-tipos-y-condiciones.md)) |
| Audience segments (new / engaged / existing) % gasto y resultados | Sales objective |
| Estado vs regla (OK / vigilar / actuar) | Según umbrales del equipo |

### 3.3 Reglas de decisión semanales (ejemplo de política)

- **Escalar** (+20–50 % según volumen) si CPA marginal estimado < break-even y ≥50 conv/semana.
- **Ajustar objetivo** solo si la semana es completa y ≥7 días desde el último cambio; ±5–10 %. **[OFFICIAL META]**
- **No actuar** si n < 30 conversiones y la diferencia vs objetivo está dentro del intervalo de ruido (ver [12](12-razonamiento-estadistico.md)).

## 4. Dashboard creativo (semanal)

**Decisión que habilita**: qué conceptos iterar, cuáles retirar, qué producir la próxima semana.

| Columna | Corte | Notas |
|---|---|---|
| Concepto / ángulo / formato / hook / creador (taxonomía de naming) | Anuncio → agregado por concepto | Agregar por concepto evita conclusiones de un anuncio |
| Gasto, % del gasto del ad set | Anuncio | Lo que Meta "elige" |
| Impresiones, frecuencia 7d | Anuncio | |
| Hook rate (3-s/imp), hold rate (fórmula declarada), watch time | Anuncio (vídeo) | |
| CTR outbound, CPC | Anuncio | |
| CPA/ROAS (con n) | Anuncio | Cautela: breakdown effect |
| Quality / engagement / conversion rate rankings | Anuncio (≥500 imp) | |
| Edad del anuncio (días), tendencia CTR semana 1 → actual | Anuncio | Fatiga ([07](07-frecuencia.md)) |
| Hit rate del lote (anuncios con gasto ≥10× mediana / lanzados) | Lote semanal | Benchmark Motion ~5 % ([03](03-escalado-tipos-y-condiciones.md)) |
| Breakdown "related media"/IA generativa/flexible format (si aplica) | Anuncio | Disponibles desde 2025 |

## 5. Dashboard mensual (estrategia y economía)

**Decisión que habilita**: presupuesto del mes siguiente, mix de canales, objetivos de puja, prioridades de test, revisión de unit economics.

| Bloque | Columnas |
|---|---|
| Economía | CM1 %, break-even CPA/ROAS actualizado, contribución tras marketing, payback, LTV por cohorte (30/60/90/180) |
| Eficiencia | MER, aMER, nCAC por mes vs objetivo y vs año anterior |
| Meta vs total | % del gasto en Meta, ROAS Meta (7d click) vs MER, ratio |
| Incrementalidad | Factor de incrementalidad vigente (último lift/geo test), fecha |
| Curva de respuesta | Gasto semanal vs conversiones (scatter) y elasticidad estimada |
| Estacionalidad | Índice semanal propio vs año anterior |
| Tests | Lista de tests cerrados: hipótesis, resultado, IC, decisión ([13](13-experimentacion-ab-tests.md)) |

## 6. Dashboard de campaña/ad set (deep-dive bajo demanda)

Para auditorías: estructura, solapamiento (auction overlap), learning status histórico, breakdown por placement/edad/geo/plataforma/dispositivo, value rules breakdown, comparación de ventanas de atribución, reparto de gasto por anuncio.

## 7. Lead gen: informe de cohortes (semanal)

| Cohorte (semana de creación del lead) | Leads | % cualificados | Booked (7d/30d) | Shows | Ventas 30d / 60d / 90d | Cash 30d | Coste por show | Coste por venta |
|---|---|---|---|---|---|---|---|---|

Cortes: campaña, anuncio/concepto, formulario vs web, edad, placement, país. **Decisión**: CPL objetivo por segmento, value rules, cambio de evento de optimización (p. ej., conversion leads), calidad de formulario.

## 8. Change log (siempre)

| Fecha-hora | Usuario | Nivel (cuenta/campaña/ad set/anuncio) | Cambio (de → a) | Motivo/hipótesis | Fecha de evaluación | Resultado |
|---|---|---|---|---|---|---|

Incluir **eventos externos**: rebajas, roturas de stock, cambios de precio, caídas web, festivos, elecciones, y cambios de plataforma (p. ej., 12-ene-2026 retirada de ventanas view en API; mar-2026 click-through solo link clicks; oct-2025 engaged-view 5 s). **[EMPIRICAL]** (fechas de plataforma vía fuentes secundarias)

### 8.1 Cambios de API que rompen dashboards (2026)

- Según el changelog fuera de ciclo citado por terceros (8-may-2026, efectivo 6-ago-2026), los breakdowns de **dispositivo, hora y frecuencia** en Ads Insights API requieren opt-in por cuenta; sin él, la API devuelve resultados vacíos **sin error**. Si tu dashboard de frecuencia (ver [07](07-frecuencia.md)) se alimenta por API/conector, verifica que no esté mostrando ceros silenciosos. **[EMPIRICAL]** ([Adsuploader](https://adsuploader.com/blog/meta-ads-updates)); confirmación primaria pendiente (área 10).
- Ventanas 7d/28d view retiradas de la API (12-ene-2026) y redefinición de click-through (mar-2026): series históricas no comparables sin ajuste. **[EMPIRICAL]**

## 9. Ventanas de atribución en reporting

- Optimiza y reporta en la misma ventana; añade una columna conservadora (1-day click) y usa el breakdown por ventana para ver qué parte es 1d click / 2–7d click / engage-through / view. **[EMPIRICAL]** (Loomer, guías 2026)
- La ventana de 7 días implica que **las cifras de los últimos 7 días siguen creciendo**; el dashboard semanal debe releer la semana anterior. **[STRONG INFERENCE]**
- Loomer: evaluar en ventanas de 7 días, al menos 2 semanas tras el lanzamiento, no oscilaciones diarias. **[EMPIRICAL]** ([Master Brief](https://www.jonloomer.com/meta-ads-master-brief/))

## Implicaciones operativas

- Un único documento/semana con 4 bloques (negocio, campañas, creativos, change log) cubre el 90 % de decisiones.
- Automatizar el diario como alertas, no como informe.
- Conditional formatting en Ads Manager (abr-2025) para estados y umbrales. **[EMPIRICAL]**

## Errores frecuentes

1. Dashboards de 40 columnas sin decisión asociada.
2. CPA diario como KPI de decisión.
3. Mezclar ventanas (Meta 7d click vs GA4 last click) en la misma tabla sin etiquetar.
4. No mostrar n (número de conversiones) junto al CPA.
5. Ausencia de change log → imposible atribuir cambios de rendimiento.

## Preguntas abiertas

- Cómo integrar de forma estándar el factor de incrementalidad en el reporting semanal sin sobre-corregir (depende del área 04).

## Fuentes clave

- [Understand fluctuations in ad performance](https://www.facebook.com/business/help/1364841787225722) — Meta — meta-oficial
- [Best practices for Advantage+ campaign budget](https://www.facebook.com/business/help/2177212182495139) — Meta — meta-oficial
- [About daily budgets](https://www.facebook.com/business/help/190490051321426) — Meta — meta-oficial
- [The Master Brief](https://www.jonloomer.com/meta-ads-master-brief/) — Jon Loomer, 2026-07 — practitioner
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — Jon Loomer — practitioner
- [Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — Motion — vendor
