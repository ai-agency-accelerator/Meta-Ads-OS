# Value optimization, ROAS goal y value rules

> Última verificación: 2026-10-15 · Autor: A09 (agente) · Ámbito: Maximise value of conversions (purchase, eventos no-purchase, profit, pLTV), ROAS goal, value rules (bid adjustments por segmento), cuándo pasar de volumen a valor.

## TL;DR

- **Value optimization ("Maximise value of conversions") optimiza a valor total, no a número de conversiones: acepta más CPA y menos compras a cambio de pedidos más valiosos.** Meta avisa de que verás CPA más alto y menos conversiones, sobre todo en learning. **[OFFICIAL META]** ([About maximising value](https://www.facebook.com/business/help/296463804090290))
- **Requisitos 2026 (web):** integración activa (Meta dice que **CAPI es "required"** para enviar valor, más pixel), evento con valor y moneda, y **≥100 eventos con ≥5 valores distintos en 14 días (recomendado)**. En 2025 el umbral publicado por terceros era ≥30 conversiones atribuidas con 5 valores distintos en 14 días: **el listón ha subido**. **[OFFICIAL META]** + **[EMPIRICAL]** del cambio ([Requirements](https://www.facebook.com/business/help/571188993373447), [Loomer 2025](https://www.jonloomer.com/meta-advertising-changes-2025/))
- **Secuencia oficial: test ≥3 semanas sin ROAS goal (Highest value), ≥50 conv/semana; luego añadir ROAS goal.** Meta dice que el pico de rendimiento llega tras ~2 semanas y recomienda medir con A/B test o Conversion Lift. **[OFFICIAL META]**
- **Profit optimization ya es oficial:** valor tipo "Profit" vía `net_revenue` (CAPI/pixel) o `estimated_margin` en catálogo; ≥3 valores de beneficio positivos distintos; no 100 % correlacionado con el ingreso; Meta pide **~100 conversiones diarias por campaña** para testearlo bien. **[OFFICIAL META]** ([Set up profit](https://www.facebook.com/business/help/2118807428848752))
- **pLTV:** ≥100 conversiones/semana atribuidas a Meta en cada una de las últimas 4 semanas, ≥5 valores pLTV positivos con máx ≥3× mín, enviados ≤7 días tras la conversión; ~2 semanas de entrenamiento. **[OFFICIAL META]** ([pLTV](https://www.facebook.com/business/help/2519794055122336))
- **Value rules = multiplicadores de puja por segmento** (edad, género, ubicación, OS, device platform, placements seleccionados, conversion location y, según Loomer, custom audiences): +1.000 % / −90 %, hasta 10 reglas por set, 2 criterios por regla, **solo aplica la primera regla que coincide**. Meta avisa: "your overall cost per result may increase". **[OFFICIAL META]** ([About value rules](https://www.facebook.com/business/help/535014515741813))
- **Value rules no están disponibles con ROAS goal ni bid cap** (Help Center, 2026). Funcionan con Highest volume / Cost per result goal. **[OFFICIAL META]**
- **Meta sustituirá los bid multipliers (API) por value rules: obligatorio "by 2027".** **[OFFICIAL META]**
- **Las value rules resuelven problemas demostrados (p. ej., Meta gastando el 45 % en 65+ en lead gen), no son un "mejorador" por defecto.** Practitioners serios (Loomer, Breznica, CustomerLabs) coinciden: sin datos de valor por segmento, solo suben el CPA. **[EMPIRICAL]** ([PPC Land, ene-2026](https://ppc.land/metas-value-rules-might-actually-cost-more-than-theyre-worth/))
- **2026: value rules como sustituto de exclusiones de placement.** Reportado como test desde ago-2026 y ya documentado en Help Center (oct-2026): en Sales, Leads y App promotion (Engagement no; corrección 2026-11-09) no se eligen placements a nivel ad set (despliegue gradual); quedan placement value rules (mínimo −90 %, no apagan del todo) y exclusiones a nivel de cuenta por objetivo. **[OFFICIAL META]** ([What's new in placement settings](https://www.facebook.com/business/help/1546753450586085), [PPC Land](https://ppc.land/some-meta-advertisers-lose-placement-controls-with-bid-cuts-capped-at-90/))

---

## 1. Qué hace realmente value optimization

### 1.1 Mecánica

Con "Maximise value of conversions", el sistema predice no solo la probabilidad de conversión (EAR) sino también el **valor esperado** de esa conversión para cada persona y puja en consecuencia. Puja más por personas con mayor valor esperado y menos por compradores de ticket bajo. **[OFFICIAL META]** (descripción funcional) + **[STRONG INFERENCE]** (la forma exacta del modelo no es pública).

Ejemplo oficial con 200 $ de presupuesto:

| Optimización | Compras | Ingresos | CPA | ROAS |
|---|---|---|---|---|
| Número de compras | 4 | 250 $ | 50 $ | 1,25 |
| Valor de compras | 3 | 500 $ | 66,7 $ | 2,50 |

**[OFFICIAL META]**. La lección: **comparar campañas de valor por CPA es un error de diagnóstico**; se comparan por ROAS/margen (o mejor, por beneficio incremental).

### 1.2 Tipos de valor (2026)

| Tipo | Qué envías | Requisito clave | Cuándo |
|---|---|---|---|
| Purchase / non-purchase value | Valor monetario del evento (compra, suscripción, trial…) | ≥100 eventos, ≥5 valores distintos, 14 días (recomendado) | Catálogo con AOV disperso; suscripciones con planes distintos |
| Custom event value | Valor definido por ti (KPI interno: nuevo vs recurrente, mercado, producto core) | Evento revisado en Events Manager | Cuando el valor de negocio ≠ ingreso del pedido |
| **Profit** | `net_revenue` en Purchase (CAPI/pixel) o `estimated_margin` en catálogo | ≥3 valores de beneficio positivos distintos; match rate catálogo >90 %; no 100 % correlacionado con el ingreso | Márgenes muy distintos entre productos |
| **pLTV** | Valor predicho (90 días/1 año) ≤7 días tras la conversión | ≥100 conv/sem × 4 semanas; ≥5 valores; máx ≥3× mín; modelo validado | Suscripción / cohortes donde el primer pedido predice mal el LTV |

**[OFFICIAL META]** ([About maximising value](https://www.facebook.com/business/help/296463804090290), [Profit](https://www.facebook.com/business/help/2118807428848752), [pLTV](https://www.facebook.com/business/help/2519794055122336))

Matices importantes:
- Para profit y pLTV, los valores **pueden indexarse/normalizarse** (no tienen que ser monetarios) mientras se mantenga la proporción relativa. Útil si no quieres exponer márgenes reales a Meta. **[OFFICIAL META]**
- **Nunca retrasar el evento Purchase** esperando calcular beneficio o pLTV: "Delayed Purchase events may not be counted". Para pLTV usa `AppendValue` diferido. **[OFFICIAL META]**
- Si el beneficio es siempre el 50 % del ingreso (100 % correlacionado), profit optimization no aporta nada frente a value optimization. **[OFFICIAL META]**
- Value optimization por eventos no-purchase y por profit aparecieron en 2025 (Loomer #54, #55); profit estaba "en testing" en 2025 y en 2026 tiene artículo de setup oficial con partners (Elevar, Stape, Profitmetrics, etc.). **[OFFICIAL META]**/**[EMPIRICAL]**

### 1.3 Ventanas de atribución

Value optimization funcionó inicialmente solo con 7-day click; en 2025 se añadió 1-day view y engaged-view. pLTV es compatible con incremental attribution, view-through y engaged-view, pero Meta recomienda **1-day o 7-day click en el primer test**. **[OFFICIAL META]**/**[EMPIRICAL]** ([Loomer 2025](https://www.jonloomer.com/meta-advertising-changes-2025/), [pLTV](https://www.facebook.com/business/help/2519794055122336))

## 2. ¿Cuándo pasar de volumen a valor?

### 2.1 Condiciones necesarias (todas)

1. **Elegibilidad**: ≥100 eventos con ≥5 valores distintos en 14 días (recomendado). **[OFFICIAL META]**
2. **Dispersión real de valor.** Meta: "Highest value requires a good distribution of values across different products". Si el 90 % de los pedidos tiene el mismo valor, no hay nada que optimizar. **[OFFICIAL META]**
3. **Volumen suficiente tras el cambio**: value optimization suele dar **menos conversiones**; si en volumen tienes 60/semana, en valor puedes caer por debajo de 50 y quedar en learning limited. **[OFFICIAL META]** + **[STRONG INFERENCE]**
4. **Valor fiable**: el valor que envías debe ser el que te importa (neto de descuentos/IVA de forma consistente). Valores erróneos (duplicados, moneda mal, IVA mezclado) hacen que el sistema persiga ruido. **[STRONG INFERENCE]**

### 2.2 Regla de decisión cuantitativa (propuesta)

Calcula, con 60–90 días de pedidos atribuidos a Meta:
- **CV del valor de pedido** = desviación típica / media.
- **Ratio P90/P10** del valor de pedido.

| Situación | Recomendación |
|---|---|
| CV < 0,3 y P90/P10 < 2 (ticket casi único) | Quédate en volumen (Highest volume / CPR goal). El valor no tiene de dónde sacar ventaja. |
| CV 0,3–0,7 | Test A/B volumen vs valor (3+ semanas, ≥50 conv/sem por brazo). |
| CV > 0,7 o P90/P10 > 4 (catálogo amplio) | Valor como hipótesis principal; test contra volumen. |
| Márgenes por producto muy distintos (p. ej., 15 % vs 60 %) | Probar Profit value optimization. |
| LTV a 12 meses poco correlacionado con el primer pedido | pLTV (si cumples volumen). |

**[HYPOTHESIS]** — los cortes de CV/P90-P10 son propuesta razonada (no publicados por Meta); el principio (necesidad de dispersión) es **[OFFICIAL META]**. Validar siempre con A/B test o lift, como pide Meta.

### 2.3 Cómo medir la decisión

- Meta recomienda **A/B test o Conversion Lift**, **≥3 semanas** (el pico se alcanza tras ~2 semanas) y no juzgar en la primera semana. **[OFFICIAL META]**
- Métrica de decisión: **margen de contribución atribuido (o incremental) por euro invertido**, no CPA ni ROAS de ingresos si los márgenes difieren entre productos. Ver [08](08-economia-unitaria-calculadoras.md).
- Evidencia de campo: en el estudio de CTC (253 cuentas, 2025-2026), la configuración de valor con ROAS goal fue la mayoritaria por gasto y la más precisa respecto al objetivo; CTC recomienda correr **ambas** configuraciones (valor y volumen) en ecommerce. **[EMPIRICAL]** ([CTC](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers))

## 3. ROAS goal en profundidad

(Mecánica general en [01](01-estrategias-de-puja.md).)

- **Escala**: 0,001–1.000; 1,00 = recuperas el gasto en *ingresos atribuidos*. **Un ROAS goal de 1,0 no es break-even de negocio**: el break-even de negocio es 1 / margen de contribución (p. ej., margen 40 % → 2,5). **[OFFICIAL META]** (escala) + aritmética.
- **Objetivo inicial**: ROAS reciente −10–20 % en tu ventana de atribución. **[OFFICIAL META]**
- **Si el ROAS reciente −20 % < ROAS break-even**: el ROAS goal "correcto" según Meta te hará perder dinero; o aceptas el ROAS break-even como objetivo (y menos volumen) o atacas creatividad/oferta. **[STRONG INFERENCE]**
- **Ajuste**: semanal, 5–10 %. Infra-gasto → bajar objetivo; gasto completo con ROAS bajo → subir objetivo. **[OFFICIAL META]**
- **Precisión observada**: media 96,5 % del objetivo (IC95 % 90–101 %) en CTC; 67 % de cuentas >5 % por debajo. En 1-day click falló más a menudo que en 7-day click. **[EMPIRICAL]**
- **Incompatible con value rules.** Si necesitas expresar valor por segmento, usa Highest value + valores diferenciados por evento, o Highest volume/CPR goal + value rules. **[OFFICIAL META]**

## 4. Value rules

### 4.1 Qué son y cómo operan

- Reglas a nivel de cuenta ("Advertising settings → Value rules") que aplicas por ad set. Ajustan la puja para personas/impresiones que cumplen criterios: **+1.000 % máximo, −90 % máximo**. Hasta **10 reglas** por set y **2 criterios** por regla. **[OFFICIAL META]** ([How to set up](https://www.facebook.com/business/help/1172579563848778))
- **Orden = prioridad**: si una persona encaja en varias reglas, solo aplica la primera. Ejemplo oficial: regla 1 +20 % mujeres en California, regla 2 +50 % mujeres con cierto OS → una mujer de California con ese OS recibe solo +20 %. **[OFFICIAL META]**
- Quien no encaja en ninguna regla puja "sin ajustar". **[OFFICIAL META]**
- Criterios disponibles (2026): edad, género, ubicación, OS, device platform, placements seleccionados, conversion location. En categorías especiales (vivienda, empleo, crédito…) edad, género y ciertas ubicaciones están vetados (provoca rechazo). **[OFFICIAL META]** Loomer añade custom audiences como criterio (jul-2026). **[EMPIRICAL]**
- **Reporting**: breakdown "Value rules" (dic-2025) para ver resultados por regla; Meta recuerda que puedes necesitar analítica externa para validar mejoras en métricas de fondo de embudo. **[OFFICIAL META]** ([Value rules breakdown](https://www.facebook.com/business/help/1643671879847552))
- **Learning**: un vendor (Bïrch) afirma que adjuntar/desadjuntar value rules no resetea learning; **no confirmado por Meta**. **[HYPOTHESIS]**

### 4.2 Cronología

| Fecha | Cambio | Evidencia |
|---|---|---|
| Ago-2024 | Primeras pruebas de conversion value rules | [EMPIRICAL] PPC Land |
| May-2025 | Lanzamiento amplio (edad, género, ubicación, OS) en Sales/App | [EMPIRICAL] Loomer #48 |
| Jul/ago-2025 | Value rules por placement | [EMPIRICAL] Loomer #49, PPC Land |
| Ago-2025 | Disponibles en todos los objetivos y cuentas | [EMPIRICAL] Loomer #51, PPC Land |
| Nov-2025 | Device platform (móvil vs desktop) y conversion location (web vs Instant Forms) | [EMPIRICAL] Loomer #50, #52 |
| Dic-2025 | Breakdown de value rules | [EMPIRICAL] Loomer #72 |
| 2026 | Help Center: bid multipliers → value rules obligatorio "by 2027" | [OFFICIAL META] |
| Ago-2026 | Test: retirada de controles de placement en ad sets Sales/Leads, sustituidos por value rules | [EMPIRICAL] Loomer (20-ago-2026), PPC Land (25-ago-2026); sin anuncio oficial |
| Oct-2026 | Help Center "What's new in placement settings": en **Sales, Leads y App promotion (Engagement no; corrección 2026-11-09) ya no se eligen placements manualmente a nivel ad set** (despliegue gradual; Awareness y Traffic no cambian). Alternativas oficiales: personalizar media por placement (multi-media ads, hasta 10 assets), **placement value rules** (subir/bajar puja por placement) y **exclusiones de placement a nivel de cuenta por objetivo** (Account controls: Audience Network, Marketplace, columna derecha…), la única exclusión dura. Meta cita un experimento: Advantage+ placements −10 % de coste por resultado medio vs manual (actualización 2026-11-09: la página releída ya no da la cifra y dice que "puede ayudarte a reducir el coste por resultado") | **[OFFICIAL META]** ([What's new in placement settings](https://www.facebook.com/business/help/1546753450586085), leído 2026-10-16) |

### 4.3 Cómo fijar el porcentaje (método)

Meta: usa tus datos de negocio (LTV, ROAS, margen) para estimar **valor relativo**; si no tienes número, empieza con **+50 %** para la audiencia de alto valor, y monitoriza con métricas internas y el breakdown. Ejemplo oficial: si mujeres generan 115 y hombres 100 de valor, +15 % a mujeres. **[OFFICIAL META]** ([Choose percentage](https://www.facebook.com/business/help/1027101802923936))

Fórmula práctica (consistente con lo anterior):

```
ajuste_segmento = (valor_por_conversión_segmento / valor_por_conversión_medio) − 1
```

donde "valor por conversión" debe ser **de negocio** (margen, LTV o tasa de cierre × ticket), no el valor que ya ve Meta (si Meta ya lo ve, value optimization lo capta sin reglas).

**Ejemplo lead gen high-ticket** (datos de CRM a 90 días):

| Segmento | Leads | Ventas | Close rate | Valor/lead (ticket 3.000 $ × margen 70 %) | Ajuste |
|---|---|---|---|---|---|
| 25–54 | 600 | 30 | 5,0 % | 105 $ | +24 % |
| 55–64 | 250 | 8 | 3,2 % | 67 $ | −21 % |
| 65+ | 400 | 4 | 1,0 % | 21 $ | −75 % |
| **Media** | 1.250 | 42 | 3,36 % | 84,7 $ | — |

Con muestras así de pequeñas (4–8 ventas por segmento), los intervalos de confianza son enormes (ver [12](12-razonamiento-estadistico.md)): empieza con ajustes **más suaves** que el cálculo bruto (p. ej., la mitad), y amplía cuando acumules datos. **[STRONG INFERENCE]**

### 4.4 Cuándo usarlas y cuándo no

**Usar** cuando hay un **problema demostrado**:
- Meta concentra gasto en un segmento que convierte barato pero vale poco (caso Loomer: 45 % del gasto en 65+ en lead gen → <2 % tras −90 %/−20 %). **[EMPIRICAL]** ([Master Brief](https://www.jonloomer.com/meta-ads-master-brief/))
- Placements que generan conversiones de baja calidad (Audience Network en lead gen) y no quieres/no puedes excluirlos. **[EMPIRICAL]**
- Diferencias de LTV o margen por geografía (p. ej., zonas con más devoluciones o envíos caros).
- Consolidación: sustituir campañas separadas por geo/edad por una sola con reglas (Meta lo promueve así). **[OFFICIAL META]**

**No usar** cuando:
- No tienes datos de valor por segmento (solo intuición): Breznica (>1,5 M€ gestionados) las evita en la mayoría de cuentas; CustomerLabs: "amplifican tus supuestos; si son erróneos, sube el coste sin ganancia". **[EMPIRICAL]**/**[CONTESTED]**
- Quieres "abaratar" un segmento que ya convierte bien: Meta lo desaconseja (bajar la puja no mejora eficiencia, limita oportunidades). **[OFFICIAL META]**
- Usas ROAS goal o bid cap (no compatibles).

### 4.5 Riesgos

- **CPA medio sube**: es el comportamiento esperado (pagas más por lo que vale más). Evaluar por valor de negocio, no por CPA. **[OFFICIAL META]**
- **Regla mal ordenada** → ajustes que nunca se aplican.
- **−90 % no es exclusión**: con presupuesto suficiente el segmento puede seguir recibiendo gasto. **[OFFICIAL META]** (límite) + **[STRONG INFERENCE]**.
- **Ruido**: con pocos datos por segmento, el ajuste puede perseguir aleatoriedad (regresión a la media). Ver [12](12-razonamiento-estadistico.md).

## Implicaciones operativas

- Ecommerce con AOV disperso: Highest value por defecto cuando cumplas ≥100 eventos/5 valores/14 días; ROAS goal solo cuando tengas ≥3 semanas de línea base y un ROAS límite calculado.
- Márgenes heterogéneos: priorizar **profit** sobre revenue cuando la integración sea posible (Meta recomienda probarlo con split test o lift y volumen alto).
- Lead gen: value rules para corregir sesgos demográficos/placement medidos en CRM, con ajustes conservadores y revisión mensual.
- Antes de 2027: migrar bid multipliers (API) a value rules.
- Revisar que no se combinan value rules con ROAS goal/bid cap.

## Errores frecuentes

1. Activar value optimization con un único precio de producto.
2. Juzgar valor vs volumen por CPA o por la primera semana.
3. Fijar ROAS goal = 1 pensando que es break-even.
4. Enviar valores con IVA en unos eventos y sin IVA en otros; enviar valor 0 en suscripciones con trial.
5. Retrasar Purchase para incluir margen/pLTV.
6. Value rules basadas en "intuición" sin datos de CRM; reglas solapadas en orden incorrecto.
7. Esperar que −90 % equivalga a excluir.

## Preguntas abiertas

- ¿El cambio de umbral de elegibilidad (≈30 → 100 eventos/14 días) es un requisito duro o una recomendación? El texto dice "(recommended)". 
- ¿Reinicia learning adjuntar/cambiar value rules? Sin confirmación oficial.
- ¿Cuántos placements quedarán sin exclusión posible si el test de ago-2026 se generaliza?
- No hay estudios independientes publicados de profit optimization vs revenue optimization con tamaño muestral conocido.

## Fuentes clave

- [About maximising the value of conversions](https://www.facebook.com/business/help/296463804090290) — Meta, consultado 2026-10-15 — meta-oficial
- [Requirements to use Maximise value of conversions](https://www.facebook.com/business/help/571188993373447) — Meta — meta-oficial
- [Set up maximise value of conversions for profit](https://www.facebook.com/business/help/2118807428848752) — Meta — meta-oficial
- [Set up maximise value of conversions for pLTV](https://www.facebook.com/business/help/2519794055122336) — Meta — meta-oficial
- [About value rules](https://www.facebook.com/business/help/535014515741813), [How to set up](https://www.facebook.com/business/help/1172579563848778), [Choose percentage](https://www.facebook.com/business/help/1027101802923936), [Breakdown](https://www.facebook.com/business/help/1643671879847552) — Meta — meta-oficial
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — Jon Loomer, dic-2025 — practitioner
- [Meta's value rules might actually cost more than they're worth](https://ppc.land/metas-value-rules-might-actually-cost-more-than-theyre-worth/) — PPC Land, 2026-01-06 — prensa
- [Some Meta advertisers lose placement controls](https://ppc.land/some-meta-advertisers-lose-placement-controls-with-bid-cuts-capped-at-90/) — PPC Land, ago-2026 — prensa
- [CTC: cost controls, we ran the numbers](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers) — CTC, 2026-08-06 — agencia
