# Cambios de presupuesto, learning, flexibilidad de gasto, budget scheduling y duplicación (2026)

> Última verificación: 2026-10-15 · Autor: A09 (agente) · Ámbito: qué dice Meta sobre presupuesto y significant edits; la "regla del 20 %"; overspend diario (75 %), límites semanales, ad set budget sharing, budget scheduling, Advantage+ campaign budget; duplicación de campañas/ad sets.

## TL;DR

- **Posición oficial vigente: un cambio de presupuesto "puede o no ser significativo, según la magnitud".** El único ejemplo que da Meta: 100 $→101 $ "no es probable" que reinicie learning; 100 $→1.000 $ "puede" hacerlo. **No existe ningún porcentaje oficial.** **[OFFICIAL META]** ([Significant edits](https://www.facebook.com/business/help/316478108955072))
- **"Regla del 20 %": UNPROVEN como regla de plataforma.** Es una convención de practitioners; no aparece en documentación de Meta (verificado 2026-10-15). En 2023 Meta llegó a recomendar en la UI subidas de +79 % "sin reentrar en learning" para una campaña concreta. **[EMPIRICAL]** ([Loomer, 2023](https://www.jonloomer.com/updates-to-meta-ads-budgeting/), [MAstratos, ago-2026](https://mastratos.com/en/resources/meta-ads-20-percent-rule/))
- **Siempre significant edits**: cualquier cambio de targeting, creatividad, evento de optimización, **añadir un anuncio**, pausar ≥7 días, cambiar bid strategy (y cambiar el disclaimer de anuncios políticos). **Condicionales por magnitud**: presupuesto, spending limit del ad set, importe del bid cap/CPR goal/ROAS goal. **[OFFICIAL META]**
- **Advantage+ campaign budget**: la redistribución automática entre ad sets **no** reinicia learning; añadir un ad set **no** reinicia a los demás; **pero cambiar el presupuesto de campaña o la bid strategy de campaña puede devolver a learning a varios ad sets a la vez**. **[OFFICIAL META]**
- **Overspend permitido: hasta +75 % en un día (máx. 175 % del presupuesto diario), nunca más de 7× el diario en la semana domingo-sábado.** Con ad set budget sharing activado: hasta 210 % al día y 8,4× a la semana. Meta considera reembolsos por encima de esos límites. **[OFFICIAL META]** ([About daily budgets](https://www.facebook.com/business/help/190490051321426))
- **Cambio de presupuesto a mitad de semana**: Meta recalcula el límite del resto de semana = nuevo diario × días restantes + 25 % de un diario. El tope del día del cambio es 175 % del **mayor** presupuesto vigente ese día. **[OFFICIAL META]** ([Changing daily budget](https://www.facebook.com/business/help/525189242169568))
- **Budget scheduling**: subidas programadas en franjas de ≥3 h, hasta 50 periodos por campaña/ad set, tope **8× el presupuesto diario** en el periodo; solo con presupuesto diario. Si reinicia learning: **no documentado**. **[OFFICIAL META]** ([About budget scheduling](https://www.facebook.com/business/help/633318028866693))
- **Ad set budget sharing (2025)**: con presupuestos de ad set, Meta puede mover hasta un 20 % entre ad sets de la misma campaña. **Ad set spending limits** dentro de A+CB pasaron de tope duro a **media** (ago-2025). **[OFFICIAL META]** + **[EMPIRICAL]** (fecha)
- **Duplicar ad sets para escalar en 2026: generalmente contraproducente** (auction overlap: en cada subasta solo compite tu anuncio de mayor valor; separar cuentas no lo evita) salvo que el duplicado cambie algo sustancial (geo, evento, oferta, bid strategy, test A/B formal). **[OFFICIAL META]** (overlap) + **[STRONG INFERENCE]**
- **Regla práctica**: cambia presupuesto en **escalones agrupados y espaciados** (una ventana por semana o cada 3–4 días), del tamaño que tu volumen permita medir; el riesgo de learning es secundario frente al **CPA marginal** del nuevo gasto. **[STRONG INFERENCE]**

---

## 1. Lo que dice Meta (textual, verificado 2026-10-15)

### 1.1 Significant edits

De [Significant edits and learning phase](https://www.facebook.com/business/help/316478108955072) **[OFFICIAL META]**:

> "Every edit that you make (during the learning phase or after it) has some effect on delivery, but not every edit causes the ad set to re-enter the learning phase."

Siempre significativos:
- Cualquier cambio de targeting.
- Cualquier cambio de creatividad.
- Cualquier cambio de evento de optimización.
- Añadir un anuncio nuevo al ad set.
- Pausar el ad set ≥7 días (reentra al reactivar).
- Cambiar la bid strategy (con A+CB, puede afectar a varios ad sets).

"May or may not be significant, depending on the magnitude":
- Spending limit del ad set.
- Importe de bid control, cost per result goal o ROAS goal.
- Importe de presupuesto (con A+CB, ajustar el presupuesto de campaña puede devolver a varios ad sets a learning).

FAQ A+CB (oficial):
- Duración del learning con A+CB = igual que con presupuestos de ad set.
- La distribución de presupuesto entre ad sets **no** provoca reentrada.
- Un significant edit en un ad set **no** afecta a los demás ad sets de la campaña.
- Añadir un ad set **no** reinicia a los demás.

### 1.2 Learning phase

- Sale "usually after about 50 results in the week after the ad set's last significant edit"; columnas "Last significant edit" y resultados desde entonces en Ads Manager. Shops ads: 17 compras web + 5 en Meta. **[OFFICIAL META]** ([About the learning phase](https://www.facebook.com/business/help/112167992830700))
- Recomendaciones oficiales: esperar a salir de learning para editar; evitar ediciones innecesarias; evitar alto volumen de ads/ad sets; **presupuestos realistas y evitar cambios frecuentes de presupuesto**. **[OFFICIAL META]**
- Learning limited = improbable llegar a ~50 eventos en la semana posterior al último significant edit; causas: audiencia pequeña, presupuesto bajo, puja/objetivo bajo, auction overlap, evento infrecuente, demasiados anuncios. "Isn't a penalty". **[OFFICIAL META]** ([About learning limited](https://www.facebook.com/business/help/269269737396981))
- Rumores 2026 de umbrales menores (25 en Advantage+ sales, 15 en app, "10 en 3 días"): **sin confirmación oficial**; la documentación de Meta consultada hoy sigue diciendo ~50. **[HYPOTHESIS]** ([AdBeacon](https://www.adbeacon.com/meta-just-lowered-the-advantage-learning-threshold/))

### 1.3 Flexibilidad del presupuesto diario

De [About daily budgets](https://www.facebook.com/business/help/190490051321426) **[OFFICIAL META]**:

| Concepto | Sin budget sharing | Con ad set budget sharing |
|---|---|---|
| Presupuesto diario | 100 $ | 100 $ |
| Gasto máximo en un día | 175 $ (+75 %) | 210 $ |
| Gasto máximo semana (dom–sáb) | 700 $ | 840 $ |
| Reembolso considerado si | día > 1,75× o semana > 7× | según reglas de sharing |

Otras reglas oficiales:
- El presupuesto diario es "un objetivo de gasto diario a lo largo de una semana natural", no un tope duro; el lifetime sí es tope duro. **[OFFICIAL META]** ([About budgets](https://www.facebook.com/business/help/214319341922580))
- Inicio a mitad de semana o cambio de presupuesto: límite resto de semana = diario × días restantes + hasta 25 % de un diario. Ejemplo oficial: bajar de 100 $ a 50 $ el miércoles 00:00 → máx. 212,50 $ mié–sáb. **[OFFICIAL META]**
- Cambio a mitad del día: el tope del día es 175 % del **mayor** presupuesto vigente ese día (y es facturable). Por eso **bajar presupuesto a las 17:00 puede no surtir efecto ese día**. **[OFFICIAL META]**
- Ad set con fecha fin: límite semanal = diario × días que corre + hasta 25 % (ejemplo oficial: 50 $/día, fin miércoles 15:00 → máx. 193,75 $). **[OFFICIAL META]**
- En learning, Meta "puede entregar de forma más agresiva", lo que explica gastos rápidos al inicio. **[OFFICIAL META]**
- **Contradicción documental**: la página de Marketing API sobre budgets todavía dice que el diario puede excederse "hasta un 25 %"; el Help Center (más reciente) dice 75 %. El dato del 25 % corresponde a la regla antigua (pre-nov-2023) y hoy solo aplica al margen semanal tras cambios/prorrateos. **[OUTDATED]** en la doc de API. ([Marketing API budgets](https://developers.facebook.com/docs/marketing-api/bidding/overview/budgets))
- Cronología: la flexibilidad del 25 % pasó al 75 % con despliegue gradual desde **nov-2023**. **[EMPIRICAL]** ([Loomer](https://www.jonloomer.com/updates-to-meta-ads-budgeting/))

Ejemplo (subida a mitad de semana): diario 100 $ → 150 $ el miércoles 00:00 → límite mié–sáb = 150 × 4 + 37,5 = **637,50 $**, más lo gastado dom–mar.

### 1.4 Ad set budget sharing y spending limits

- **Ad set budget sharing**: con presupuestos de ad set (no compatible con campaign budget), Meta puede compartir hasta el 20 % del presupuesto diario de cada ad set con otros de la campaña en tiempo real. **[OFFICIAL META]** ([Campaign vs ad set budgets](https://www.facebook.com/business/help/458847204894307)). Visto en cuentas desde jul-2025. **[EMPIRICAL]**
- **Spending limits** (mín/máx por ad set dentro de A+CB): desde ago-2025 se comportan como **media**, no como tope duro. **[EMPIRICAL]** ([Loomer 2025](https://www.jonloomer.com/meta-advertising-changes-2025/)). Meta recomienda usarlos "sparingly, or not at all", sobre todo combinados con controles de coste. **[OFFICIAL META]**
- **Placements excluidos**: desde oct-2025 Meta puede gastar hasta un 5 % del presupuesto en placements excluidos (opción desactivable). **[EMPIRICAL]**

### 1.4b Gobernanza de cambios hechos por IA (2026)

En ago–oct 2026 Meta ha desplegado agentes/conectores de IA (Meta AI en Ads Manager, servidor MCP de anuncios) capaces de sugerir o ejecutar cambios de presupuesto, audiencia y creatividad, con controles para **bloquear cambios de presupuesto por encima de un umbral** y registros de actividad de los agentes. Según una recopilación de terceros, los cambios de presupuesto por agente vendrían activados por defecto por cuenta. **[EMPIRICAL]** (recopilación de fuentes oficiales vía [Adsuploader, oct-2026](https://adsuploader.com/blog/meta-ads-updates); verificar en la cuenta). Implicación: los cambios automáticos de presupuesto cuentan igual a efectos de learning y deben entrar en el change log; fijar umbrales coherentes con la política de escalado de este documento. El detalle de IA/automatización corresponde al área 10.

### 1.5 Budget scheduling

De [About budget scheduling](https://www.facebook.com/business/help/633318028866693) **[OFFICIAL META]**:
- Programar **aumentos** de presupuesto en días/horas/fechas de alta demanda (promos, lanzamientos, eventos, horas pico).
- Solo con **presupuesto diario**; hasta **50** periodos de alta demanda por campaña/ad set; cada periodo **≥3 horas**; el total del periodo no puede exceder **8× el presupuesto diario** (100 $ → máx. 800 $).
- Distinto de ad scheduling (dayparting), que solo funciona con presupuesto lifetime.
- **Learning**: Meta no dice si un periodo programado cuenta como cambio de presupuesto "significativo". **No verificado**. Hipótesis razonable: el sistema conoce el calendario de antemano y lo trata como plan, no como edición; pero no hay prueba. **[HYPOTHESIS]**

Uso recomendado: BFCM, rebajas, lanzamientos con fecha fija, picos horarios demostrados con datos de ≥4 semanas.

## 2. La "regla del 20 %" y alternativas basadas en evidencia

### 2.1 Veredicto

| Afirmación | Veredicto | Por qué |
|---|---|---|
| "Subir >20 % reinicia learning" | **UNPROVEN / FALSE como regla fija** | Meta no publica umbral; dice "según magnitud". Meta llegó a recomendar +79 % sin reentrar (2023). |
| "Nunca toques nada en learning" | **CONTEXT-DEPENDENT** | Meta recomienda esperar, pero también dice que el learning es necesario y que hay que testear; lo dañino es editar repetidamente. |
| "Subir poco a poco es más seguro" | **CONTEXT-DEPENDENT** | Reduce el riesgo de reinicio, pero el CPA marginal sube igual; escalones minúsculos son imposibles de medir y alargan el tiempo a escala. |
| "Doblar presupuesto mata la campaña" | **UNPROVEN** | No hay datos públicos controlados; lo esperable es CPA marginal mayor + posible reentrada en learning. |

### 2.2 Qué hacer en su lugar (marco de decisión)

1. **Calcula si el nuevo presupuesto mantiene ≥50 resultados/semana al CPA *esperado* (más alto)**. Si no, no subas: consolida. (MAstratos propone exactamente esto.) **[STRONG INFERENCE]**
2. **Tamaño del escalón según objetivo**:
   - Cuenta pequeña (<100 conv/semana): escalones de +30–50 % semanales; escalones de +10 % no se distinguen del ruido (ver [12](12-razonamiento-estadistico.md)).
   - Cuenta grande y estable (>300 conv/semana): +20–30 % cada 3–4 días es medible y prudente.
   - Picos programados: budget scheduling.
   **[HYPOTHESIS]** (rangos razonados, no oficiales)
3. **Agrupa cambios** (presupuesto + nuevos anuncios en la misma ventana) para pagar un solo "coste de learning"; Meta recomienda introducir cambios en bloque con A+CB. **[OFFICIAL META]** ([A+CB best practices](https://www.facebook.com/business/help/2177212182495139))
4. **Mide el incremento**: semana tras el cambio vs semana previa → CPA marginal (ver [03](03-escalado-tipos-y-condiciones.md)).
5. **Registra cada cambio** (fecha, hora, de→a) para poder atribuir variaciones.

Referencia de practitioner (2026): Foxwell usa movimientos de +20–25 % (hasta 30 %), condicionados a cinco métricas de negocio (margen tras ads, nCAC vs margen del 1.er pedido, beneficio 90 d/CAC, payback, mix nuevos/recurrentes), y +20–30 %/semana solo si todas están "en verde"; Loomer considera que Meta es hoy "mucho más tolerante" con las subidas. Es decir, el 20 % sobrevive como **ritmo prudente de practitioners**, no como umbral técnico de la plataforma. **[EMPIRICAL]** (ver [03](03-escalado-tipos-y-condiciones.md))

Tiempo hasta duplicar presupuesto según ritmo (cálculo):

| Ritmo | Días para ×2 |
|---|---|
| +20 % cada 3 días | ~11 |
| +30 % cada 3 días | ~8 |
| +50 % cada 7 días | ~12 |
| +20 % cada 7 días | ~27 |
| ×2 de golpe | 0 (y 1 semana para medir) |

### 2.3 Bajadas de presupuesto

- También pueden ser "significativas" según magnitud. **[OFFICIAL META]**
- Precaución oficial: bajar tarde en el día puede no aplicarse a tiempo; si se baja un lifetime, el nuevo importe debe ser ≥ gastado + 10 % de lo gastado en los dos últimos días. **[OFFICIAL META]** ([Minimum budgets](https://www.facebook.com/business/help/203183363050448))
- Bajar presupuesto mejora el CPA medio (te mueves hacia abajo en la curva) — no confundir con "la campaña ha mejorado". **[STRONG INFERENCE]**

## 3. Advantage+ campaign budget (A+CB) al subir

- Un solo presupuesto que se reparte en tiempo real hacia los ad sets con mejores oportunidades; puede gastar casi todo en un ad set → analizar a nivel campaña. **[OFFICIAL META]** ([About A+CB](https://www.facebook.com/business/help/153514848493595))
- Al **subir el presupuesto de campaña**, el riesgo de learning afecta potencialmente a varios ad sets a la vez (oficial). Por eso el escalón agrupado y espaciado es aún más importante. **[OFFICIAL META]**
- Al añadir un ad set, A+CB tarda ~2 horas en reajustar; añadir ad sets en bloque. **[OFFICIAL META]**
- **No pausar/reactivar ad sets** ni pausar los de baja entrega: A+CB los descarta y puede subir el CPA de los activos. **[OFFICIAL META]**
- Ad sets con audiencias mucho mayores se llevarán más presupuesto. **[OFFICIAL META]**
- Límite práctico: ≤70 ad sets por campaña (por encima, ediciones limitadas). **[OFFICIAL META]**
- Cuándo preferir presupuestos de ad set (oficial): valores de ad set muy distintos que no puedes expresar con puja, tamaños de audiencia muy distintos, objetivos/estrategias mezclados, control estricto por ad set. **[OFFICIAL META]** ([Campaign vs ad set budgets](https://www.facebook.com/business/help/458847204894307))

## 4. Duplicación de campañas/ad sets en 2026

### 4.1 Mecánica relevante

- **Auction overlap**: si dos anuncios tuyos entran en la misma subasta, Meta elige el de mayor total value y descarta los demás (no pujas contra ti mismo). Consecuencias: el duplicado puede no gastar, quedar en learning limited y hacer el rendimiento menos predecible "especially when scaling your budget". **Ejecutar desde cuentas separadas no lo evita.** **[OFFICIAL META]** ([Auction overlap](https://www.facebook.com/business/help/537699989762051))
- Un duplicado empieza su propio learning (es un ad set nuevo). **[OFFICIAL META]** (learning ocurre al crear un ad set)
- Duplicar un anuncio creando uno nuevo pierde la prueba social del post original salvo que se reutilice el post existente (post ID). **[EMPIRICAL]** (práctica estándar; cubierta en el área creativa)

### 4.2 Cuándo SÍ tiene sentido duplicar

| Caso | Por qué | Etiqueta |
|---|---|---|
| A/B test formal (Duplicate → New split test) | Meta separa audiencias sin solapamiento y calcula ganador | [OFFICIAL META] |
| Cambiar evento de optimización, conversion location o bid strategy sin perder el original | Son significant edits; un duplicado permite comparar y conservar el original | [STRONG INFERENCE] |
| Nuevo país/idioma/oferta con unit economics distintas | Abre inventario real, presupuesto propio | [STRONG INFERENCE] |
| Mover un anuncio ganador de una campaña de testing a la de escalado (con post ID existente) | Conserva prueba social; la campaña de escala tiene más presupuesto | [EMPIRICAL] |
| Campaña estacional con calendario/presupuesto propios (BFCM) | Aísla el pico y su lectura | [STRONG INFERENCE] |

### 4.3 Cuándo NO

- **Duplicar el mismo ad set (misma audiencia, mismo evento, mismas creatividades) para "gastar más"**: competencia interna, learning múltiple, fragmentación de señal. Loomer: técnica popular, pero ad sets idénticos pueden empeorar el rendimiento por overlap. **[EMPIRICAL]**/**[STRONG INFERENCE]**
- **Duplicar para "resetear" un ad set en learning limited**: no ataca la causa (presupuesto/evento/fragmentación). Meta: combinar, ampliar, subir presupuesto/puja o cambiar evento. **[OFFICIAL META]**
- **Duplicar en otra cuenta para esquivar overlap**: Meta dice que puede no funcionar. **[OFFICIAL META]**

### 4.4 Matiz [CONTESTED]

Algunos media buyers de cuentas grandes siguen usando duplicados con **bid caps distintos** (escalera de pujas) para capturar distintos niveles de precio sin subir el CPA de la unidad principal. Funciona como forma de "segmentar por precio de subasta", pero en cada subasta solo competirá uno de tus anuncios. Sin datos públicos controlados que lo validen frente a una sola unidad con presupuesto mayor. **[CONTESTED]** — más defendible en cuentas con mucho volumen y conocimiento de su economía (lógica CTC de bid cap), menos en cuentas pequeñas.

## Implicaciones operativas

- Política de cambios: **una ventana de edición por semana** (o cada 3–4 días en cuentas grandes); agrupar presupuesto + creatividades.
- Para subir: verificar que el ad set seguirá en ≥50 conv/semana al CPA esperado; preferir escalones que puedas medir.
- Para picos conocidos: budget scheduling (≤8×, ≥3 h) en vez de editar a mano.
- No bajar presupuesto tarde en el día esperando efecto inmediato.
- Duplicar solo con un "porqué" que cambie inventario, evento o medición.
- Registrar cada cambio en un change log (ver [10](10-dashboards-reporting.md)).

## Errores frecuentes

1. Creer que el diario es un tope duro y alarmarse por días al 170 %.
2. Interpretar la regla del 20 % como dogma y tardar meses en escalar un ganador claro.
3. Hacer 5 microcambios en una semana (cada uno puede ser "significativo") en lugar de uno.
4. Pausar ad sets de baja entrega dentro de A+CB.
5. Duplicar ad sets idénticos para escalar.
6. Leer el CPA del día del cambio (gasto agresivo en learning, conversiones aún sin atribuir).

## Preguntas abiertas

- Umbral real (si existe) a partir del cual Meta considera "significativo" un cambio de presupuesto — posiblemente relativo al volumen de eventos y no un % fijo. **[HYPOTHESIS]**
- Efecto de budget scheduling sobre learning.
- Confirmación oficial de umbrales de learning más bajos en Advantage+ (rumores 2026).

## Fuentes clave

- [Significant edits and learning phase](https://www.facebook.com/business/help/316478108955072) — Meta, consultado 2026-10-15 — meta-oficial
- [About the learning phase](https://www.facebook.com/business/help/112167992830700), [About learning limited](https://www.facebook.com/business/help/269269737396981) — Meta — meta-oficial
- [About daily budgets](https://www.facebook.com/business/help/190490051321426), [About budgets](https://www.facebook.com/business/help/214319341922580), [About changing your daily budget](https://www.facebook.com/business/help/525189242169568), [Minimum budgets](https://www.facebook.com/business/help/203183363050448) — Meta — meta-oficial
- [About budget scheduling](https://www.facebook.com/business/help/633318028866693) — Meta — meta-oficial
- [About A+CB](https://www.facebook.com/business/help/153514848493595), [Best practices A+CB](https://www.facebook.com/business/help/2177212182495139), [Campaign vs ad set budgets](https://www.facebook.com/business/help/458847204894307) — Meta — meta-oficial
- [Understand auction overlap](https://www.facebook.com/business/help/537699989762051) — Meta — meta-oficial
- [Marketing API: Budgets](https://developers.facebook.com/docs/marketing-api/bidding/overview/budgets) — Meta Developers — meta-developers (contiene dato desactualizado del 25 %)
- [Updates to Meta Ads Budgeting](https://www.jonloomer.com/updates-to-meta-ads-budgeting/) — Jon Loomer, 2023-11-02 — practitioner
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — Jon Loomer — practitioner
- [The Meta 20% Budget Rule Does Not Exist](https://mastratos.com/en/resources/meta-ads-20-percent-rule/) — MAstratos, 2026-08-23 — agencia
- [Meta Just Lowered the Advantage+ Learning Threshold](https://www.adbeacon.com/meta-just-lowered-the-advantage-learning-threshold/) — AdBeacon, 2026-08-12 — vendor (baja confianza)
