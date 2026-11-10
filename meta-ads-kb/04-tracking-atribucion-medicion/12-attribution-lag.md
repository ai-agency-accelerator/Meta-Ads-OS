# Attribution lag: conversiones que tardan minutos, días o semanas

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: efecto del retraso entre interacción y conversión (y entre conversión y llegada del dato) sobre la optimización y el reporting de Meta; qué hacer en ciclos de venta largos.

## TL;DR

- **Hay tres retrasos distintos:** (1) *conversion lag*: del clic/vista a la conversión; (2) *signal lag*: de la conversión a que Meta recibe el evento (Pixel ≈ inmediato; CAPI según tu cola; offline/CRM horas o días; AEM con retraso agregado); (3) *processing lag*: Meta refresca insights cada ~15 min y los datos dejan de cambiar a los 28 días. [OFFICIAL META] ([S04-050]) + [STRONG INFERENCE]
- **El algoritmo solo aprende de conversiones que (a) llegan y (b) caen dentro de la ventana de atribución del ad set.** Una venta 10 días después de un clic con configuración 7d click no existe para la optimización de ese ad set. [OFFICIAL META] (ventanas, [S04-001]) + [STRONG INFERENCE] (efecto en aprendizaje)
- **Las conversiones offsite se fechan en el día en que ocurren** (no el de la impresión); por tanto, en periodos de **escalado** el ROAS reciente se ve peor de lo que será (gasto nuevo aún sin convertir) y en periodos de **recorte** se ve mejor. [OFFICIAL META] ([S04-068], [S04-050]) + [STRONG INFERENCE]
- **Los últimos 3 días casi siempre están incompletos** (eventos tardíos, usuarios iOS sin ATT medidos con retraso, offline/CRM). Meta recomendó esperar ≥ 72 h antes de analizar campañas de conversión tras iOS 14. [OFFICIAL META citado por prensa] + [EMPIRICAL]
- **Ciclos > 7 días:** optimiza a un evento más temprano que correlacione con la venta (proxy) o a etapas de CRM ≤ 28 días (Conversion Leads); envía valor (`value`/`predicted_ltv`) para que el algoritmo distinga calidad; mide el negocio con cohortes, MMM y experimentos. [OFFICIAL META] (CRM ≤ 28 días, [S04-060]) + [STRONG INFERENCE]
- **La fase de aprendizaje necesita ~50 eventos de optimización por ad set en 7 días** (umbral ampliamente citado del Help Center; no se encontraron cambios oficiales en 2025–2026). Si el evento final es escaso y lento, sube en el embudo. [OFFICIAL META citado por fuentes secundarias] ([S04-102])

## 1. Escenarios

| Retraso conversión | Qué ocurre en optimización | Qué ocurre en reporting | Qué hacer |
|---|---|---|---|
| **5 minutos** (impulso) | Señal casi en tiempo real si Pixel/CAPI son inmediatos; aprendizaje rápido | Día del clic = día de la venta; poco desfase | CAPI en tiempo real; 7d click + 1d view razonable |
| **1 día** | Dentro de cualquier ventana (incluida 1d); señal útil | Ventas de hoy aparecen mañana; el día actual siempre infra-reportado | Evaluar con ≥ 3 días de margen |
| **7 días** | Al límite de 7d click; las que caen el día 8 se pierden para optimización; con 1d click casi todo se pierde | Gasto de la última semana aún "debe" conversiones; ROAS reciente subestimado si escalas | Mantener 7d click; no usar 1d click; mirar columna 28d click como diagnóstico |
| **30 días** (B2B, high-ticket, financiación) | La venta queda fuera de toda ventana configurable; **el algoritmo no aprende de ella** | Meta reporta poca venta (solo la fracción rápida); GA4 (90 d) o CRM la ven | Optimizar a proxy (lead cualificado, cita, solicitud), CRM ≤ 28 d, valor predicho; medir con cohortes CRM y experimentos |

## 2. Efectos en la optimización (primeros principios)

1. **Ventana = definición del éxito.** La entrega aprende a encontrar personas parecidas a las que convirtieron *dentro de la ventana*. Si la mayoría de compras ocurre tarde, el sistema sobre-pondera a compradores rápidos (a menudo clientes recurrentes o tráfico caliente). [STRONG INFERENCE]
2. **Llegada tardía = señal degradada.** Un evento CAPI que llega horas después cuenta (si está en ventana y ≤ 7 días de `event_time`), pero el sistema ya tomó decisiones de puja/entrega sin él; Meta prioriza la frescura ("real time") en sus métricas de calidad. [OFFICIAL META] ([S04-016]) + [STRONG INFERENCE]
3. **Volumen mínimo.** Con ~50 eventos/semana por ad set como referencia de salida de aprendizaje, un evento de fondo de embudo lento y escaso deja el ad set en "Learning limited". [OFFICIAL META citado por fuentes secundarias] ([S04-102])
4. **Proxies tienen coste:** optimizar a AddToCart/Lead puede atraer a quien hace la acción barata y no compra. El proxy debe validarse con la correlación real proxy→venta por campaña (cohortes CRM). [STRONG INFERENCE]

## 3. Efectos en el reporting

- **Fecha de conversión:** compras web registradas el día que ocurren (desde 2021; API alineada en `mixed` desde 10-jun-2025). [OFFICIAL META] ([S04-068], [S04-050])
- **Datos tardíos rellenan días pasados:** eventos con `event_time` de ayer enviados hoy se asignan a ayer → los días recientes "crecen" durante 1–3 días (más con offline/CRM). Además, el reporting de usuarios iOS sin ATT (AEM) puede retrasarse hasta ~72 h según Meta/practicantes. [EMPIRICAL] ([S04-103])
- **Datos estables a los 28 días** (insights no cambian tras 28 días de reportados). [OFFICIAL META] ([S04-050])
- **Escalado vs ROAS:** si el gasto sube un 50 % esta semana, las conversiones de ese gasto adicional llegarán durante los próximos 1–7 días; el ROAS de "últimos 7 días" mostrará una caída que en parte es lag. Regla práctica: comparar *cohortes de gasto* (p. ej. ROAS a 7 días de clics de la semana X, medido a X+14) en lugar de ventanas móviles. [STRONG INFERENCE]

### 3.1 Ejemplo numérico: el "falso bajón" al escalar

Supuestos (ilustrativos): ROAS real constante de 3,0; de cada 100 € de ingresos atribuibles a un día de gasto, 50 € llegan el mismo día, 10 € en cada uno de los días 1–3 y 5 € en cada uno de los días 4–7. El gasto pasa de 1.000 €/día a 2.000 €/día el día 0.

| Día | Gasto | Ingresos reportados ese día | ROAS diario aparente |
|---|---|---|---|
| −1 | 1.000 | 3.000 | 3,00 |
| 0 | 2.000 | 4.500 | **2,25** |
| 1 | 2.000 | 4.800 | 2,40 |
| 3 | 2.000 | 5.400 | 2,70 |
| 6 | 2.000 | 5.850 | 2,92 |
| 7 | 2.000 | 6.000 | 3,00 |

El ROAS móvil de 7 días cae a ~2,64 entre los días 2 y 6 y no vuelve a 3,0 hasta el día 13, **sin ningún empeoramiento real**. Con lags más largos (B2B, high-ticket) el efecto es mayor y más duradero; al recortar presupuesto ocurre lo contrario (ROAS aparente inflado). Cálculo propio (simulación determinista). [STRONG INFERENCE]

Cómo evitarlo: (1) evaluar escalados con ROAS por **cohorte de gasto** a N días maduros; (2) comparar contra un grupo de control sin cambio (otra campaña/región) o (3) esperar al menos la longitud del p80 del lag antes de decidir.

## 4. Medir tu lag

1. **Desde el backend (lo más fiable):** para pedidos con `fbclid`/`fbc` persistidos, calcula `order_time − first_fbclid_time` (o `− click time` codificado en `fbc`: el tercer campo es el timestamp de creación en ms). Distribución → percentiles 50/80/95. [STRONG INFERENCE] (formato de `fbc` [OFFICIAL META], [S04-007])
2. **En Ads Manager:** compara columnas 1d click vs 7d click vs 28d click del mismo periodo: la proporción 1d/7d indica cuánto ocurre el mismo día; 7d/28d cuánto se pierde fuera de 7 días. [EMPIRICAL]
3. **En CRM:** tiempo entre lead y cada etapa (mediana y p80). Si la etapa deseada tiene p80 > 28 días, no es optimizable vía Conversion Leads. [OFFICIAL META] (≤ 28 d, [S04-060])

## 5. Estrategias para ciclos largos

| Estrategia | Cuándo | Riesgo |
|---|---|---|
| Optimizar a un evento intermedio (InitiateCheckout, Lead cualificado, cita, solicitud enviada) | Venta > 7 días o < ~50 ventas/semana | Proxy mal correlacionado |
| Conversion Leads (CRM) | Lead ads (instant forms o web) con volumen suficiente (~200 leads/mes era el mínimo hasta oct-2025), etapa ≤ 28 días con CVR 1–40 % | Requiere integración y 1–2 meses de entrenamiento |
| Valor en el evento temprano (`value` = valor esperado; `predicted_ltv` en StartTrial/Subscribe) | Diferencias de calidad conocidas por segmento/producto | Valor mal calibrado sesga la puja |
| Eventos de CRM como custom events por CAPI con `fbc` persistido | Medición propia y audiencias | Fuera de ventana no atribuyen |
| Medición de negocio con cohortes + experimentos + MMM | Siempre en ciclos largos | Requiere disciplina analítica |

Fuentes: [OFFICIAL META] (Conversion Leads, `predicted_ltv`, [S04-060], [S04-037]) + [STRONG INFERENCE].

### 5.1 Cómo validar un evento proxy (procedimiento)

1. Toma 60–90 días de datos de CRM/backend con el ID de usuario/lead y el `ad_id`/campaña de origen (persistidos vía UTM/macro o `fbclid`).
2. Para cada campaña o ad set, calcula: tasa proxy→venta, valor medio de venta y lag proxy→venta.
3. Un proxy es útil si (a) su volumen permite ~50 eventos/semana por ad set, (b) la tasa proxy→venta es **estable entre campañas** (si varía mucho, el algoritmo optimizará hacia proxies "baratos" de baja calidad) y (c) ocurre dentro de la ventana de atribución.
4. Si la calidad varía por segmento conocido (producto, país, tipo de lead), envía `value` diferenciado en el proxy (valor esperado = tasa × valor medio).
5. Re-evalúa cada trimestre o tras cambios de creatividad/oferta, y confirma con un experimento que optimizar al proxy mejora las ventas incrementales, no solo el CPA del proxy.

[STRONG INFERENCE] (procedimiento analítico); umbral de ~50 eventos: [OFFICIAL META citado por fuentes secundarias] ([S04-102]).

## Implicaciones operativas

- **Hacemos:** medir el lag real; elegir ventana y evento de optimización según el p80 del lag; enviar CAPI en tiempo real; reportar ROAS por cohortes de gasto; no evaluar campañas con < 3 días de datos maduros.
- **Evitamos:** apagar campañas por el ROAS de "hoy/ayer"; cambiar a 1d click en negocios con lag de días; optimizar a Purchase con 10 compras/semana.
- **Umbrales:** si > 30 % de las compras atribuibles caen fuera de 7 días (28d click vs 7d click), el evento Purchase es mala señal de optimización para ese negocio. [STRONG INFERENCE]

## Errores frecuentes

1. Diagnosticar "caída de rendimiento" en los últimos 2 días.
2. Confundir lag de conversión con lag de reporting.
3. Elegir un proxy por volumen sin validar correlación con venta.
4. Subir offline/CRM semanalmente (fuera de 7 días, señal inútil para optimizar).

## Preguntas abiertas

- Retraso real del reporting AEM en 2026 (la cifra de 72 h procede de 2021; no reverificada).
- Si Meta usa conversiones fuera de ventana para algún modelo de entrega a nivel cuenta (no documentado).

## Fuentes clave

- [Insights API best practices](https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights/best-practices) — vigente — meta-developers (S04-050)
- [Actions for partners and mobile web advertisers (iOS 14)](https://developers.facebook.com/blog/post/2021/01/19/actions-partners-mobile-web-advertisers/) — 2021-01-19 — meta-developers (S04-068)
- [Dataset Quality API (freshness)](https://developers.facebook.com/docs/marketing-api/conversions-api/dataset-quality-api) — 2025 — meta-developers (S04-016)
- [Conversions API for CRM Integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) — vigente — meta-developers (S04-060)
- [Meta learning phase ~50 events (síntesis secundaria)](https://ads.expert/guides/meta-learning-phase) — 2026 — practitioner (S04-102)
- [Social Media Today: Meta recommendations post-iOS 14 (72 h)](https://www.socialmediatoday.com/news/meta-provides-new-recommendations-to-help-advertisers-lessen-the-impacts-of/618899/) — 2022 — prensa (S04-103)

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Fila de Conversion Leads: el mínimo de 200 leads/mes ya no es requisito (Meta, 30-oct-2025) y el objetivo admite formularios web (Help Center 782657799338685).
