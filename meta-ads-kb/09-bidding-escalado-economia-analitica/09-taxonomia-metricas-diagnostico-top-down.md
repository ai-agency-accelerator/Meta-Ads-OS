# Taxonomía de métricas y diagnóstico top-down

> Última verificación: 2026-10-15 · Autor: A09 (agente) · Ámbito: jerarquía BUSINESS → FUNNEL → ADS → CREATIVE; definiciones y fórmulas; descomposición del CPA/ROAS; árbol de diagnóstico; trampas (mix, breakdown effect, atribución).

## TL;DR

- **Diagnostica de arriba abajo**: primero ¿el negocio está peor? (revenue, contribución, MER, CAC); luego ¿en qué etapa del funnel?; luego ¿qué palanca de anuncios (CPM, CTR, CVR, AOV)?; y solo al final ¿qué creatividad? Empezar por el CPA de un anuncio en un día es el error más caro. **[STRONG INFERENCE]**
- **Identidades base**: `CPA = CPM / (1.000 × CTR × CVR)` y `ROAS = AOV × CVR × CTR × 1.000 / CPM`. En log, el cambio de CPA se reparte exactamente: `Δln CPA = Δln CPM − Δln CTR − Δln CVR`. **[STRONG INFERENCE]** (aritmética)
- **Lead gen**: `coste por venta = CPL / (booking × show × close)`. Un CPL de 50 $ con 30 %/70 %/20 % es un coste por venta de 1.190 $. **[STRONG INFERENCE]**
- **Meta recomienda analizar al nivel donde vive el presupuesto** (campaña con A+CB, ad set con presupuesto de ad set), en semanas completas, y desconfiar de breakdowns por hora/placement/anuncio por el *breakdown effect*. **[OFFICIAL META]** ([Understand fluctuations](https://www.facebook.com/business/help/1364841787225722))
- **Con optimización a conversión, CPM no es KPI**; es una métrica diagnóstica. **[OFFICIAL META]**
- **Las métricas de Meta son atribuidas, no incrementales**, y cambiaron de definición en 2025-2026 (click-through = solo link clicks desde mar-2026; engage-through 1 día; ventanas 7d/28d view retiradas de la API en ene-2026). Las series temporales que crucen esas fechas no son comparables sin ajuste. **[EMPIRICAL]** (fuentes secundarias; el área 04 debe verificar)
- **Métricas creativas** (hook/thumbstop = 3-s plays / impresiones; hold = ThruPlays / 3-s plays, u otras variantes) **no son estándar de Meta**: declara siempre la fórmula. **[EMPIRICAL]**

---

## 1. Jerarquía de métricas

### 1.1 BUSINESS (la verdad; decide presupuesto total)

| Métrica | Definición | Frecuencia de lectura |
|---|---|---|
| Revenue neto | Ventas netas de IVA, descuentos y devoluciones | Semanal/mensual |
| Cash collected | Caja efectivamente cobrada (clave en high-ticket con planes) | Semanal |
| Margen de contribución (tras marketing) | Revenue × CM1 % − gasto marketing | Semanal/mensual |
| Profit (operativo) | Contribución − costes fijos | Mensual |
| MER | Revenue total / gasto marketing total | Semanal |
| aMER / nMER | Revenue clientes nuevos / gasto | Semanal |
| CAC / nCAC | Gasto adquisición / clientes nuevos | Semanal/mensual |
| LTV (contribución) | Por cohorte de adquisición | Mensual/trimestral |
| Payback | Meses hasta recuperar CAC | Mensual |
| Blended ROAS | Revenue total / gasto ads total | Semanal |

### 1.2 FUNNEL (dónde se rompe)

| Ecommerce | Lead gen / high-ticket |
|---|---|
| Sesiones (landing page views) | Leads (CPL) |
| Tasa de añadir al carrito | Leads cualificados (CPQL) |
| Tasa de checkout | Booking rate (coste por booked call) |
| CVR sesión→compra | Show rate (coste por show) |
| AOV, % nuevos clientes | Close rate (coste por venta), ticket medio, cash collected |
| Devoluciones | Reembolsos, impagos |

Las tasas entre etapas se miden **por cohorte** (leads de la semana X → resultados a 30/60/90 días) cuando el ciclo es largo.

### 1.3 ADS (Meta Ads Manager)

| Métrica | Fórmula | Uso |
|---|---|---|
| Spend | — | — |
| Impresiones, alcance, frecuencia | frecuencia = imp / alcance | Saturación (ver [07](07-frecuencia.md)) |
| CPM | spend / imp × 1.000 | Diagnóstico de mercado/mix/calidad |
| CTR (link / outbound) | clics enlace / imp | Relevancia y "promesa" del anuncio |
| CPC (link) | spend / clics enlace = CPM / (1.000 × CTR) | |
| LPV rate | landing page views / link clicks | Velocidad/carga de la landing, clics accidentales |
| CVR | conversiones / clics (o / LPV) | Landing, oferta, intención del tráfico |
| CPA / CPR | spend / resultados | KPI de optimización (en su ventana) |
| ROAS | valor / spend | KPI en value optimization |
| Resultados desde último significant edit | columna oficial | Learning (ver [04](04-cambios-de-presupuesto-y-duplicacion.md)) |
| Quality / engagement / conversion rate ranking | relativas a competidores; ≥500 imp; no son input de subasta | Diagnóstico creativo |

### 1.4 CREATIVE (por anuncio/concepto)

| Métrica | Fórmula habitual | Comentario |
|---|---|---|
| Hook rate / thumbstop | 3-s video plays / impresiones | Benchmarks vendor 20–35 %; muy dependiente de placement |
| Hold rate | ThruPlays / 3-s plays (Motion) o 15-s plays / impresiones (otros) | Declarar fórmula |
| Watch time medio, % reproducido 25/50/75/95 | — | Retención |
| CTR outbound | — | Promesa del anuncio |
| Engagement (shares, saves, comments) | — | Señal de resonancia; desde mar-2026 alimenta "engage-through" |
| Spend share | gasto del anuncio / gasto ad set | Lo que Meta "elige" |
| CPA/ROAS por anuncio | — | Con cautela (breakdown effect, muestras pequeñas) |

Fuentes de definiciones creativas: Motion, Vaizle, Billo (no estándar Meta). **[EMPIRICAL]**

## 2. Descomposición matemática

### 2.1 Ecommerce

```
Conversiones = Impresiones × CTR × CVR
Impresiones  = Spend / CPM × 1.000
CPA  = CPM / (1.000 × CTR × CVR)
ROAS = AOV × 1.000 × CTR × CVR / CPM
Δln CPA = Δln CPM − Δln CTR − Δln CVR     (exacto)
Δln ROAS = Δln AOV − Δln CPA
```

**Ejemplo** (semana A → semana B; mismo ad set):

| | CPM | CTR | CVR | AOV | CPA | ROAS |
|---|---|---|---|---|---|---|
| A | 14,00 | 1,20 % | 3,0 % | 70 | 38,89 | 1,80 |
| B | 16,10 | 1,05 % | 3,1 % | 68 | 49,46 | 1,37 |

CPA +27,2 %. Reparto logarítmico: CPM +15 % explica ~58 %, CTR −12,5 % explica ~56 %, CVR +3 % compensa −14 %. **Diagnóstico**: problema de "arriba del clic" (mercado/mix + atractivo creativo), no de landing. Acciones: revisar estacionalidad/mix de placements (CPM) y fatiga/nuevas creatividades (CTR). **[STRONG INFERENCE]**

### 2.2 Lead gen

```
Coste por venta = CPL / (booking × show × close)
CPL = CPM / (1.000 × CTR × CVR_formulario)
```
CPL 50 $, booking 30 %, show 70 %, close 20 % → **1.190 $ por venta**. Bajar el CPL un 20 % (40 $) equivale a subir el show rate de 70 % a 87,5 %. **[STRONG INFERENCE]**

## 3. Árbol de diagnóstico top-down

```
1. NEGOCIO: ¿contribución/MER/CAC peor que objetivo o que la semana comparable?
   ├─ No → no tocar por métricas de Meta aisladas (ver 11).
   └─ Sí → ¿es Meta o el resto?
        ├─ Tráfico orgánico/email/otros canales caen → no es (solo) Meta.
        ├─ CVR del sitio cae en TODOS los canales → landing/oferta/stock/precio/web.
        └─ Solo cae lo atribuido/asociado a Meta → 2.
2. FUNNEL: ¿qué etapa?
   ├─ Ecommerce: LPV rate, add-to-cart, checkout, CVR, AOV, % nuevos.
   └─ Lead gen: CPL vs cualificación vs booking vs show vs close (por cohorte).
3. ADS (a nivel campaña con A+CB / ad set con presupuesto propio, semana completa):
   ├─ CPM ↑ → estacionalidad/mercado, mix placement/geo, restricciones, calidad (ver 05/06).
   ├─ CTR ↓ → fatiga/relevancia creativa (ver 07), cambio de mix de placement.
   ├─ CVR ↓ → landing, oferta, precio, tracking (eventos perdidos), calidad del tráfico.
   ├─ AOV ↓ → mix de producto, descuentos, value vs volume.
   ├─ Learning / learning limited / bid limited → ver 01/04.
   └─ Tracking: caída de eventos en Events Manager, deduplicación, EMQ (área 04).
4. CREATIVE: ¿qué anuncios llevan el gasto? ¿su CTR/hook/hold caen? ¿hay sustitutos?
5. ACCIÓN: una palanca a la vez, con hipótesis y fecha de evaluación (ver 11/13).
```

**[STRONG INFERENCE]** (marco), apoyado en guía oficial de Meta: analizar resultados globales del ad set/campaña, semanas completas, focalizarse en el evento de optimización y desconfiar de breakdowns. **[OFFICIAL META]**

### 3.1 Tabla de síntomas → causas probables

| Síntoma (semana vs comparable) | Causas probables | Primer chequeo |
|---|---|---|
| CPA ↑, CPM ↑, CTR =, CVR = | Mercado/estacionalidad, mix (más Feed IG, más EE. UU.) | YoY misma semana ISO; breakdown placement/geo |
| CPA ↑, CTR ↓ en anuncios principales, frecuencia ↑ | Fatiga creativa | Delivery "Creative fatigue"; CTR por anuncio en el tiempo |
| CPA ↑, CVR ↓, CTR = | Landing, precio, stock, tracking | CVR del sitio en otros canales; Events Manager |
| ROAS ↓, CPA =, AOV ↓ | Mix de producto/descuentos | AOV por producto; value vs volume |
| Gasto ≪ presupuesto | Bid/cost limited, audiencia pequeña, overlap, rechazos | Delivery status; ver 01 |
| CPL = pero ventas ↓ | Calidad del lead (segmentos, placements, formulario) | Cohortes CRM por segmento; value rules |
| Meta ROAS ↑ pero MER = | Atribución/canibalización (retargeting, existing customers) | Audience segments; holdout |

## 4. Trampas de análisis

1. **Breakdown effect** (oficial): un placement/hora/anuncio con CPA aparente más alto puede estar capturando las conversiones más baratas disponibles en ese momento; el sistema optimiza el total, no cada segmento. No cortar segmentos por su CPA parcial. **[OFFICIAL META]**
2. **Paradoja de Simpson / efecto mix**: el CPA total puede empeorar aunque todos los segmentos mejoren, si el gasto se mueve a segmentos más caros (p. ej., más EE. UU.). Descomponer siempre en "efecto tasa" vs "efecto mix". **[STRONG INFERENCE]**
3. **Atribución incompleta en días recientes**: con 7-day click, los últimos 1–7 días tienen conversiones aún por llegar (ver [11](11-cuando-no-tocar-una-campana.md)).
4. **Cambios de definición**: click-through solo link clicks y engage-through 1 día (anunciado 3-mar-2026, efectivo ese mes); engaged-view de 10 s → 5 s (oct-2025); retirada de 7d/28d view en Ads Insights API (12-ene-2026). Marcar estas fechas en los dashboards. **[EMPIRICAL]** ([AdExchanger](https://www.adexchanger.com/social-media/meta-has-a-new-way-to-measure-social-engagement-because-clicks-dont-cut-it/), [Dataslayer](https://www.dataslayer.ai/blog/meta-ads-attribution-window-removed-january-2026), [Loomer 2025](https://www.jonloomer.com/meta-advertising-changes-2025/))
5. **Métricas estimadas/muestreadas** (alcance, frecuencia, únicas). **[OFFICIAL META]**
6. **Ventanas mezcladas**: comparar ROAS 7d click de Meta con ROAS last-click de GA4.
7. **Ruido**: diferencias de CPA con <30 conversiones por brazo rara vez son señal (ver [12](12-razonamiento-estadistico.md)).

## Implicaciones operativas

- Toda revisión empieza por la fila BUSINESS del dashboard ([10](10-dashboards-reporting.md)).
- Reportar CPA con su descomposición CPM/CTR/CVR (y AOV) y el reparto logarítmico del cambio.
- En lead gen, el KPI de gestión es coste por show/venta por cohorte; el CPL es indicador adelantado.
- Anotar en el change log los cambios de definición de Meta y los propios (ver [04](04-cambios-de-presupuesto-y-duplicacion.md)).

## Errores frecuentes

1. Diagnosticar desde el anuncio hacia arriba.
2. Perseguir CPM bajo en campañas de conversión.
3. Cortar placements/edades por CPA parcial (breakdown effect).
4. No separar efecto mix de efecto tasa.
5. Comparar periodos que cruzan cambios de definición de atribución.

## Preguntas abiertas

- Documentación oficial primaria de los cambios de click-through/engage-through (mar-2026) y de la retirada de ventanas view (ene-2026): solo se han localizado fuentes secundarias en esta investigación; el área 04 debe confirmarla.
- Benchmarks fiables de hook/hold rate por placement y vertical (los públicos son de vendors).

## Fuentes clave

- [Understand fluctuations in ad performance](https://www.facebook.com/business/help/1364841787225722) — Meta — meta-oficial
- [About ad relevance diagnostics](https://www.facebook.com/business/help/403110480493160) — Meta — meta-oficial
- [View ad set average cost](https://www.facebook.com/business/help/100158620724975) — Meta — meta-oficial
- [Key creative performance metrics](https://motionapp.com/blog/key-creative-performance-metrics) — Motion — vendor
- [Hook rate & hold rate](https://insights.vaizle.com/hook-rate-hold-rate/) — Vaizle — vendor
- [Meta has a new way to measure social engagement](https://www.adexchanger.com/social-media/meta-has-a-new-way-to-measure-social-engagement-because-clicks-dont-cut-it/) — AdExchanger, 2026-03-03 — prensa
- [Meta ads attribution window removed January 2026](https://www.dataslayer.ai/blog/meta-ads-attribution-window-removed-january-2026) — Dataslayer, 2026-01-19 — vendor
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — Jon Loomer — practitioner
