# Estrategias de puja en Meta Ads (2026): mecánica, cuándo usar cada una y cómo fijar objetivos

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A09 (agente) · Ámbito: Highest volume, Highest value, Cost per result goal, ROAS goal, Bid cap; nomenclatura API; fijación de objetivos; diagnóstico bid-limited vs budget-limited.

## TL;DR

- **Nomenclatura vigente en Ads Manager (oct-2026): Highest volume, Highest value (spend-based), Cost per result goal, ROAS goal (goal-based) y Bid cap (manual).** En la API siguen llamándose `LOWEST_COST_WITHOUT_CAP`, `COST_CAP`, `LOWEST_COST_WITH_MIN_ROAS` y `LOWEST_COST_WITH_BID_CAP`. Cost per result goal = antiguo *cost cap*; ROAS goal = antiguo *minimum ROAS*; Highest volume = antiguo *lowest cost*. **[OFFICIAL META]** ([About bid strategies](https://www.facebook.com/business/help/1619591734742116), [Marketing API bid strategy](https://developers.facebook.com/docs/marketing-api/bidding/overview/bid-strategy))
- **Spend-based (Highest volume/value) prioriza gastar todo el presupuesto aunque el mercado se encarezca; goal-based (Cost per result goal/ROAS goal) prioriza respetar el objetivo aunque no gaste todo.** Es la diferencia operativa más importante: con goal-based, un objetivo demasiado agresivo se traduce en *infra-gasto*, no en CPA alto. **[OFFICIAL META]**
- **Los goal-based trabajan sobre medias semanales**, no por subasta ni por día: Meta puja por encima y por debajo del objetivo para que la media semanal quede cerca. Meta pide evaluar en semanas y esperar ≥7 días tras cada ajuste. **[OFFICIAL META]** ([About cost per result goal](https://www.facebook.com/business/help/272336376749096))
- **Volumen mínimo recomendado para goal-based: 50–100+ conversiones/semana por ad set.** Por debajo, el control es impreciso; Meta recomienda consolidar, ampliar audiencia o relajar el objetivo. **[OFFICIAL META]**
- **Objetivo inicial oficial: Cost per result goal = CPA reciente +10–20 %; ROAS goal = ROAS reciente −10–20 %**, medido en la misma ventana de atribución con la que optimizas. Sin histórico: 2 semanas en Highest volume/value para tener línea base. **[OFFICIAL META]** ([Best practices CPR goal](https://www.facebook.com/business/help/176339196621566), [Best practices ROAS goal](https://www.facebook.com/business/help/288309751798466))
- **Bid cap limita la puja por acción estimada en cada subasta, no el coste que verás en reporting.** Solo para quien sabe estimar tasas de conversión; el riesgo típico es "Bid limited" → no gasta. **[OFFICIAL META]** ([About bid cap](https://www.facebook.com/business/help/272503946776144))
- **Evidencia agregada más grande disponible (CTC, 253 cuentas, 200 M$ analizados, mar-2025→jul-2026): ROAS goal aterrizó de media al 96,5 % del objetivo; Cost per result goal al ~140 % del objetivo (CPA un 40 % más caro que el target) en 7-day click; bid cap al 123 %.** CTC cambió su control por defecto de cost per result goal a bid cap. **[EMPIRICAL]** (una sola fuente, ecommerce; ver matices) ([CTC](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers))
- **Valor por defecto razonable: Highest volume (o Highest value si hay dispersión de AOV y datos de valor).** Practitioners de referencia lo usan ~90 % del tiempo y añaden controles solo cuando hay una restricción económica clara (break-even) y volumen suficiente. **[EMPIRICAL]** ([Jon Loomer](https://www.jonloomer.com/bid-strategies-best-practices-for-meta-advertising/))
- **Cambiar la estrategia de puja es siempre significant edit; cambiar el importe del objetivo "puede serlo o no" según magnitud.** Con Advantage+ campaign budget, cambiar la estrategia a nivel campaña puede devolver a learning a varios ad sets a la vez. **[OFFICIAL META]** ([Significant edits](https://www.facebook.com/business/help/316478108955072))
- **Un "bid" bajo en un segmento que convierte mejor no mejora la eficiencia**: Meta recomienda fijar el objetivo en "lo máximo que tu negocio puede pagar" y usar value rules para expresar diferencias de valor entre segmentos. **[OFFICIAL META]**

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **"Flexible ROAS goal"** y **"Performance-based budget increase" (beta)**: una única agencia (2026-11-06) que cita una sesión de Meta sin enlace. **[HYPOTHESIS]** No los des por disponibles hasta verlos en una cuenta o en el Help Center.
> - **Q3-2026**: precio medio por anuncio +14 % e impresiones +10 % interanual. **[OFFICIAL META]** Más presión de CPM: recalcula los objetivos de coste por resultado con la economía del cliente.
> - Fuentes: S10-117, S10-124 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Nomenclatura actual y mapeo

| Ads Manager (2026) | Familia (Meta) | API `bid_strategy` | Nombre antiguo | Performance goal requerido | Parámetro |
|---|---|---|---|---|---|
| **Highest volume** | Spend-based | `LOWEST_COST_WITHOUT_CAP` | Lowest cost | Maximizar nº de conversiones (u otros eventos) | — |
| **Highest value** | Spend-based | `LOWEST_COST_WITHOUT_CAP` + `optimization_goal=VALUE` | Lowest cost con value optimization | Maximizar valor de conversiones | — |
| **Cost per result goal** | Goal-based | `COST_CAP` | Cost cap (no confundir con *target cost*, estrategia distinta deprecada en API v9 en favor de cost cap) | Maximizar nº de conversiones | `bid_amount` |
| **ROAS goal** | Goal-based | `LOWEST_COST_WITH_MIN_ROAS` | Minimum ROAS | Maximizar valor de conversiones | `roas_average_floor` (entero ×10.000; 15000 = 1,5) |
| **Bid cap** | Manual | `LOWEST_COST_WITH_BID_CAP` | Lowest cost with bid cap | Cualquiera compatible | `bid_amount` |

Notas de verificación:
- La página de ayuda "About cost per result goal" conserva el mismo ID de artículo que el antiguo "About cost cap" (272336376749096) y el texto de la API para `COST_CAP` ("adherence to cost cap limits is not guaranteed") es el mismo que el de Help Center para cost per result goal. **[OFFICIAL META]** para la equivalencia funcional.
- Inconsistencia interna de Meta: la página de bid strategies llama a ROAS goal "goal-based", pero la página de value rules dice "value rules are not available for manual bid strategies such as ROAS goal or bid cap", y la API agrupa `COST_CAP`, `MIN_ROAS` y `BID_CAP` como "manual bidding". La taxonomía comercial (spend/goal/manual) es la de 2025-2026; la de la API es la histórica. **[OFFICIAL META]** (contradicción documental, no de comportamiento).
- No se ha encontrado ninguna estrategia nueva o renombrada en 2025-2026 más allá de esta taxonomía. Lo que sí cambió en 2025-2026 alrededor de la puja: value rules (ampliadas a todos los objetivos, placements, device, conversion location), value optimization para eventos no-purchase y para *profit*, y requisito de volumen para value optimization (ver [02](02-value-optimization-y-value-rules.md)). **[OFFICIAL META]**/**[EMPIRICAL]**

## 2. Cómo funciona la puja por dentro (primeros principios)

### 2.1 La subasta y el "total value"

Meta adjudica cada impresión al anuncio con mayor **total value** = combinación de **bid** + **estimated action rate (EAR)** + **ad quality**, sujeto a un precio mínimo. Un anuncio más relevante puede ganar a uno con más puja. **[OFFICIAL META]** ([About ad auctions](https://www.facebook.com/business/help/430291176997542))

Para optimización a conversión, Meta documenta explícitamente:

```
bid por impresión = bid por acción estimada × estimated action rate
```

**[OFFICIAL META]** ([About bid cap](https://www.facebook.com/business/help/272503946776144))

Consecuencias prácticas:
- Lo que fijas (o lo que Meta fija por ti) es una puja **por resultado**; el sistema la convierte en puja por impresión multiplicando por la probabilidad predicha de conversión de *esa persona con ese anuncio*.
- Dos anuncios con el mismo bid cap pujan muy distinto: si el EAR de A es 0,2 % y el de B 0,1 %, A puja el doble por la misma impresión.
- Por eso **la creatividad y la landing (que mueven EAR y calidad) son palancas de "puja" más potentes que el número que pones en el campo de bid**. **[STRONG INFERENCE]**

Ejemplo (bid cap 50 $):

| EAR predicho (compra/impresión) | Puja por impresión | CPM máximo equivalente |
|---|---|---|
| 0,1 % | 0,05 $ | 50 $ |
| 0,2 % | 0,10 $ | 100 $ |
| 0,4 % | 0,20 $ | 200 $ |

Lo que se paga finalmente es menor o igual que la puja (Meta: los ajustes de subasta "no harán que te cobremos más que tu puja"). **[OFFICIAL META]**

### 2.2 Pacing: donde se cruzan presupuesto y estrategia

Meta define pacing como "la intersección de tu presupuesto y tu bid strategy", con dos componentes que trabajan juntos: **budget pacing** (repartir el gasto a lo largo del calendario) y **bid pacing** (ajustar pujas para cumplir los objetivos de coste). **[OFFICIAL META]** ([About pacing](https://www.facebook.com/business/help/1754368491258883))

- En Highest volume, el sistema "busca primero las oportunidades de mayor volumen/menor coste; cuando se agotan, pasa a opciones más caras", por lo que **el coste por resultado tiende a subir a lo largo del calendario y al subir presupuesto**. **[OFFICIAL META]** ([Understand fluctuations](https://www.facebook.com/business/help/1364841787225722))
- Esto es la base mecánica de los **rendimientos marginales decrecientes** (ver [03](03-escalado-tipos-y-condiciones.md)).

### 2.3 Spend-based vs goal-based vs manual

| | Spend-based (Highest volume / value) | Goal-based (CPR goal / ROAS goal) | Manual (Bid cap) |
|---|---|---|---|
| Qué prioriza | Gastar todo el presupuesto | Respetar el objetivo (media semanal) | No superar la puja máxima en ninguna subasta |
| Si el mercado se encarece | Sigue gastando; sube CPA/baja ROAS | Gasta menos para proteger el objetivo | Pierde subastas; gasta menos |
| Horizonte de control | Ninguno | Media **semanal** "over the campaign lifetime" | **Cada subasta** |
| Riesgo típico | Sobrepagar en picos (BFCM, fatiga) | Infra-gasto; "learning limited" por objetivo bajo | "Bid limited", gasto ~0 |
| Volumen recomendado | Ninguno específico (learning ≈50/sem) | 50–100+ conv/sem | Alto conocimiento de CVR predicho |

Fuente de la tabla: **[OFFICIAL META]** ([About bid strategies](https://www.facebook.com/business/help/1619591734742116)). Cita textual clave: *"Goal-based bidding uses AI to dynamically adjust bids above or below your target on a weekly average basis. It works best with a flexible target bid and 50–100 or more weekly conversions. When the market becomes too competitive, the system prioritises respecting your target over additional scale."*

## 3. Cada estrategia en detalle

### 3.1 Highest volume

- **Mecánica:** "lo máximo posible de resultados con tu presupuesto"; **no optimiza el CPA**: si la competencia sube, el CPA sube. **[OFFICIAL META]** ([About highest volume](https://www.facebook.com/business/help/721453268045071))
- **Cuándo:** lanzamientos, cuentas/eventos nuevos sin línea base, cuando gastar el presupuesto importa más que el coste exacto, y como estrategia por defecto en la mayoría de cuentas (incluye lead gen, mensajes, tráfico).
- **Prerrequisitos:** ninguno más allá de la señal del evento.
- **Riesgos:** sin guardarraíl. En semanas caras (Q4, eventos) o con fatiga creativa, el CPA puede dispararse sin que el sistema frene. La protección es **presupuesto** + vigilancia del CPA semanal.
- **Escalado:** escala vía presupuesto; espera CPA marginal creciente.
- **Compatibilidad 2025-2026:** es la estrategia requerida por la herramienta de creative testing (oct-2025). **[EMPIRICAL]** ([Loomer, creative testing](https://www.jonloomer.com/meta-creative-testing/))

### 3.2 Highest value

- **Mecánica:** gasta todo el presupuesto buscando el mayor **valor** de compra, no el mayor número de compras. Ejemplo oficial: con 200 $, optimizar a número de compras da 4 compras/250 $ (ROAS 1,25); optimizar a valor da 3 compras/500 $ (ROAS 2,5). **[OFFICIAL META]** ([About maximising value](https://www.facebook.com/business/help/296463804090290))
- **Cuándo:** ecommerce con catálogo amplio y dispersión de precios/AOV; suscripciones con valores distintos; cuando el ROAS importa más que el número de pedidos.
- **Prerrequisitos (2026):** evento con valor y moneda vía CAPI (Meta lo marca como requerido) + pixel; **≥100 eventos con ≥5 valores distintos en los últimos 14 días (recomendado)** para eventos web estándar/custom. Meta advierte que "highest value requires a good distribution of values across different products". **[OFFICIAL META]** ([Requirements](https://www.facebook.com/business/help/571188993373447), [About highest value](https://www.facebook.com/business/help/168777633739990))
- **Riesgos:** menos conversiones → learning más lento; con valores poco variados (AOV casi único) no aporta frente a Highest volume.
- Detalle completo en [02-value-optimization-y-value-rules.md](02-value-optimization-y-value-rules.md).

### 3.3 Cost per result goal (antes cost cap)

- **Mecánica:** fijas un CPA medio objetivo; la IA sube y baja pujas por subasta para mantener la **media semanal** cerca del objetivo. Coste diario fluctúa; "adherence is not guaranteed". Puede **no gastar el presupuesto** cuando el mercado está caro. **[OFFICIAL META]** ([About CPR goal](https://www.facebook.com/business/help/272336376749096))
- **Cuándo (Meta):** cuando tienes un CPA objetivo y quieres escalar con guardarraíl de coste; cuando mantener el coste importa más que gastar todo.
- **Prerrequisitos:**
  - 50–100+ conversiones semanales en el ad set. **[OFFICIAL META]**
  - **Presupuesto diario ≥ 5 × objetivo de CPR** (p. ej., objetivo 5 $ → presupuesto ≥ 25 $). **[OFFICIAL META]** ([Minimum budgets](https://www.facebook.com/business/help/203183363050448))
  - Con iOS 14.5+, el ad set debe programarse ≥3 días completos. **[OFFICIAL META]** ([About cost and bid controls](https://www.facebook.com/business/help/491846184627504))
- **Cómo fijar el objetivo inicial (oficial):** CPA medio de los últimos 30 días **+10–20 %** (ej.: CPA 20 $ → objetivo 22 $). Sin histórico: ≥2 semanas en Highest volume y usar ese CPA. Si vienes de bid cap, **no** uses el valor del bid cap (es puja máxima, no coste medio); usa el CPA histórico. **[OFFICIAL META]** ([Best practices CPR goal](https://www.facebook.com/business/help/176339196621566))
- **Escalado (oficial):** correr ≥3 semanas antes de escalar; subir presupuesto gradualmente; **cambiar el objetivo solo tras una semana**. Reglas de ajuste:
  - *Bid constrained* (queda mucho presupuesto semanal sin gastar): subir objetivo **5–10 %**; si además el CPA semanal está por encima del objetivo, consolidar ad sets hasta 50–100+ conv/sem.
  - *Budget constrained* (gasta todo y quieres más): si el CPA es bueno, subir presupuesto y reajustar objetivo tras una semana; si gasta todo con CPA muy por encima, **bajar** objetivo 5–10 %.
  **[OFFICIAL META]**
- **Comportamiento real observado:** en el estudio de CTC (253 cuentas, 2025-2026), el CPR goal entregó de media un CPA ≈140 % del objetivo con 7-day click (IC95 % 145–164 % en su "factor"), y el 75 % de cuentas quedó >5 % por encima del objetivo. Explicación de CTC: es difícil fijar bien un objetivo de CPA cuando hay muchos SKUs/AOVs. **[EMPIRICAL]** (fuente única, ecommerce DTC; no extrapolar sin cuidado a lead gen de un solo evento) ([CTC](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers))
- **Implicación:** si tu CPA máximo admisible (break-even o target) es 36 $ y observas un sesgo realizado/objetivo de ~1,4, un objetivo de ~26 $ es el que te deja dentro del límite. Pero eso tensiona la entrega. Mide **tu** ratio realizado/objetivo durante 2–4 semanas antes de corregir así. **[HYPOTHESIS]** como regla general.

### 3.4 ROAS goal (antes minimum ROAS)

- **Mecánica:** objetivo de ROAS medio (expresado de 0,001 a 1.000; 1,00 = break-even de *ingresos*, no de beneficio); la IA ajusta pujas para mantener el ROAS **semanal** cerca del objetivo; puede no gastar todo. **[OFFICIAL META]** ([About ROAS goal](https://www.facebook.com/business/help/1113453135474912))
- **Prerrequisitos:** performance goal "Maximise value of conversions" + elegibilidad de value optimization (ver arriba) + pixel/SDK funcional. 50–100+ conversiones semanales recomendadas.
- **Objetivo inicial (oficial):** ROAS medio reciente **−10–20 %** (ROAS habitual 1 → probar 0,8–0,9), medido en tu ventana de atribución. Sin histórico: ≥2 semanas en Highest value. **[OFFICIAL META]** ([Best practices ROAS goal](https://www.facebook.com/business/help/288309751798466))
- **Ajustes (oficial):** bid constrained → **bajar** ROAS goal 5–10 %; budget constrained con ROAS bajo el objetivo → **subir** ROAS goal 5–10 %. Evaluar tras una semana. **[OFFICIAL META]**
- **Recomendación oficial de secuencia:** "Test initially without a ROAS goal" (Highest value primero), añadir ROAS goal después. **[OFFICIAL META]** ([About maximising value](https://www.facebook.com/business/help/296463804090290))
- **Evidencia:** en CTC fue el control más preciso en agregado (ROAS medio 228 vs objetivo 236 → 96,5 %; IC95 % 90–101 %), aunque el 67 % de cuentas quedó >5 % por debajo del objetivo; 7-day click se acercó más al objetivo que 1-day click. **[EMPIRICAL]**
- **No compatible con value rules** (según Help Center de value rules). **[OFFICIAL META]**

### 3.5 Bid cap

- **Mecánica:** fija la **puja máxima por acción estimada** en cada subasta. Meta puede pujar menos si gastarías demasiado rápido. No controla el CPA de reporting; el CPA puede superar el cap (sobre todo en learning). **[OFFICIAL META]** ([About bid cap](https://www.facebook.com/business/help/272503946776144), [Best practices bid cap](https://www.facebook.com/business/help/586282251886816))
- **Cuándo:** anunciantes avanzados que conocen sus tasas de conversión predichas y su economía; necesidades de "nunca pagar más de X por subasta" (márgenes muy estrechos, arbitraje, picos de CPM donde no quieres entrar).
- **Ejemplo oficial:** una marca de skincare sabe que conversiones >40 $ dan pérdida; tras pruebas pone **bid cap 50 $** (más alto que el CPA límite) porque así reduce los días con conversiones >40 $ sin reducir mucho el gasto los demás días. Moraleja: **el bid cap óptimo suele estar por encima del CPA objetivo**, porque se paga menos que la puja y el EAR es una predicción. **[OFFICIAL META]**
- **Riesgo principal:** cap bajo → estado "Bid limited" → no gasta. Solución oficial: subir/quitar el cap, ampliar audiencia o mejorar calidad del anuncio (creatividad). **[OFFICIAL META]**
- **Evidencia empírica:** en CTC el bid cap entregó un CPA ≈123 % del cap (muestra pequeña, ~3 M$) y CTC lo adoptó como control por defecto en 2026. **[EMPIRICAL]**/**[CONTESTED]**: Meta y Loomer lo reservan para avanzados; CTC/Andrew Faris lo prefieren históricamente. Ambos tienen razón en su contexto: con buen conocimiento de la economía y capacidad creativa alta, el bid cap protege de picos de subasta; sin ese conocimiento, ahoga la entrega.

## 4. Árbol de decisión práctico

1. **¿Tienes <50 conversiones/semana en el ad set previsto?** → Highest volume (o Highest value si cumples requisitos de valor). Si no llegas a 50/sem, primero consolida o sube de evento (ver [11](11-cuando-no-tocar-una-campana.md)); un control de coste solo empeorará el aprendizaje. **[OFFICIAL META]** (learning limited menciona "low bid or cost control" como causa)
2. **¿Tu negocio tiene un CPA/ROAS máximo duro (break-even calculado, ver [08](08-economia-unitaria-calculadoras.md)) y estás *pasándotelo* en semanas caras?** → goal-based (CPR goal si un solo valor; ROAS goal si AOV variable).
3. **¿Prefieres gastar todo el presupuesto aunque una semana salga cara (p. ej., BFCM con conversión alta)?** → spend-based.
4. **¿Quieres excluir explícitamente subastas caras (picos de CPM), conoces tus CVR y tienes volumen?** → bid cap, empezando alto (≥ CPA objetivo) y bajando.
5. **¿Hay segmentos (edad, placement, OS, ubicación) que valen más o menos para tu negocio?** → mantener la estrategia y añadir **value rules** (no bajar la puja global). **[OFFICIAL META]**

Regla de coherencia: **el objetivo se fija en la misma ventana de atribución en la que optimiza el ad set** (7-day click por defecto en compras). Meta lo pide explícitamente; mezclar ventanas (p. ej., fijar ROAS goal con un ROAS de GA4 o de 1-day click) produce objetivos irreales. **[OFFICIAL META]**

## 5. Ejemplos trabajados

### 5.1 Ecommerce, AOV 80 $, margen de contribución antes de ads 45 %

- CPA break-even = 80 × 0,45 = **36 $**; ROAS break-even = 1/0,45 = **2,22**.
- CPA de los últimos 30 días en Highest volume = 20 $ → objetivo inicial oficial de CPR goal: **22–24 $**. Está holgadamente por debajo de 36 $, así que no hay razón económica para un control: el control solo tiene sentido si en picos el CPA se acerca a 36 $.
- Para sostener 50–100 conv/semana a ~22 $ necesitas **1.100–2.200 $/semana (≈157–314 $/día)**; el mínimo oficial de presupuesto para CPR goal (5 × 22 = 110 $/día) se queda corto para el volumen recomendado.
- ROAS histórico 3,0 → ROAS goal inicial **2,4–2,7** (por encima del break-even 2,22: correcto). Si tu ROAS histórico fuera 2,4, el rango oficial (1,9–2,2) quedaría *por debajo* del break-even: en ese caso **el problema no es la puja sino la economía o la creatividad**.

### 5.2 Lead gen high-ticket

- CPL histórico 40 $, CPL máximo calculado (ver [08](08-economia-unitaria-calculadoras.md)) 95 $. El CPR goal tiene poco sentido mientras el CPL esté lejos del máximo; el riesgo real es la **calidad** del lead (no la controla la puja). Prioridad: optimizar a un evento más profundo (conversion leads, cualificado) o value rules por segmento (Loomer bajó la puja un 90 % a 65+ y un 20 % a 55–64; el gasto en 65+ pasó del 45 % a <2 %). **[EMPIRICAL]** ([Loomer Master Brief, jul-2026](https://www.jonloomer.com/meta-ads-master-brief/))

## 6. Diagnóstico: ¿bid-limited o budget-limited?

| Síntoma (semana completa) | Diagnóstico | Acción oficial |
|---|---|---|
| Gasto semanal ≪ presupuesto, CPA ≤ objetivo | Objetivo demasiado estricto (bid constrained) | Subir CPR goal 5–10 % / bajar ROAS goal 5–10 % |
| Gasto ≪ presupuesto, CPA > objetivo | Señal insuficiente (pocas conversiones) | Consolidar a 50–100+ conv/sem, ampliar audiencia |
| Gasto = presupuesto, CPA ≤ objetivo | Budget constrained, sano | Subir presupuesto; reajustar objetivo tras 1 semana |
| Gasto = presupuesto, CPA ≫ objetivo | Objetivo demasiado laxo para el presupuesto | Bajar CPR goal 5–10 % / subir ROAS goal 5–10 % |
| "Bid limited" con bid cap | Cap bajo para el EAR actual | Subir/quitar cap, mejorar creatividad, ampliar audiencia |

**[OFFICIAL META]** ([Best practices CPR goal](https://www.facebook.com/business/help/176339196621566), [ROAS goal](https://www.facebook.com/business/help/288309751798466), [bid cap](https://www.facebook.com/business/help/586282251886816))

## Implicaciones operativas

- **Por defecto:** Highest volume (leads, eventos de un solo valor) o Highest value (catálogo con AOV disperso y ≥100 compras/14 días con ≥5 valores distintos).
- **Añadir control** solo si: (a) hay un CPA/ROAS límite calculado, (b) el ad set tiene ≥50 conv/semana, (c) has visto semanas en que el spend-based se pasa del límite.
- **Objetivo inicial:** CPA30d × 1,10–1,20 o ROAS × 0,80–0,90, nunca más estricto que el break-even/objetivo económico sin aceptar menos volumen.
- **Cadencia de ajuste:** un cambio de objetivo por semana como máximo, de 5–10 %, evaluando semanas completas.
- **Presupuesto con CPR goal:** ≥5× el objetivo (mínimo oficial) y, para estabilidad, ≥ objetivo × 50/7 al día.
- **Bid cap:** empezar por encima del CPA objetivo, bajar en escalones; vigilar "Bid limited".
- **No mezclar estrategias** dentro de una campaña con Advantage+ campaign budget (no se puede): campaña separada por estrategia. **[OFFICIAL META]**

## Errores frecuentes

1. Poner un CPR goal = CPA "deseado" (aspiracional) en lugar del histórico +10–20 % → infra-gasto y learning limited.
2. Leer el bid cap como "lo que pagaré por compra".
3. Juzgar goal-based por días: Meta compensa dentro de la semana.
4. Fijar ROAS goal con un ROAS de otra herramienta/otra ventana.
5. Cambiar de estrategia durante learning (reinicio garantizado) o cambiar objetivo cada 2–3 días.
6. Usar CPR goal con 10–20 conversiones/semana.
7. Bajar la puja en segmentos "que convierten bien" pensando que se ahorra: Meta lo desaconseja explícitamente.
8. Culpar a la puja de un problema creativo: un CPA que sube con frecuencia creciente y CTR cayendo es fatiga, no bidding.

## Preguntas abiertas

- ¿El sesgo de CPR goal (~140 % del objetivo en CTC) se reproduce en lead gen con un único evento y valor homogéneo? No hay datos publicados comparables. **[HYPOTHESIS]**
- Meta no publica qué tolerancia semanal aplica a los goal-based (ni si es simétrica).
- ¿Cuánto penaliza un cambio del 5–10 % del objetivo en términos de learning? Meta dice "puede o no" ser significativo.

## Fuentes clave

- [About bid strategies](https://www.facebook.com/business/help/1619591734742116) — Meta Help Center, consultado 2026-10-15 — meta-oficial
- [About cost per result goal](https://www.facebook.com/business/help/272336376749096) / [Best practices](https://www.facebook.com/business/help/176339196621566) — Meta — meta-oficial
- [About ROAS goal](https://www.facebook.com/business/help/1113453135474912) / [Best practices](https://www.facebook.com/business/help/288309751798466) — Meta — meta-oficial
- [About bid cap](https://www.facebook.com/business/help/272503946776144) / [Best practices](https://www.facebook.com/business/help/586282251886816) — Meta — meta-oficial
- [About highest volume](https://www.facebook.com/business/help/721453268045071), [About highest value](https://www.facebook.com/business/help/168777633739990), [About cost and bid controls](https://www.facebook.com/business/help/491846184627504) — Meta — meta-oficial
- [Marketing API: Bid strategy](https://developers.facebook.com/docs/marketing-api/bidding/overview/bid-strategy) — Meta Developers — meta-developers
- [About ad auctions](https://www.facebook.com/business/help/430291176997542), [About pacing](https://www.facebook.com/business/help/1754368491258883) — Meta — meta-oficial
- [Taylor and Andrew debate cost controls (we ran the numbers)](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers) — CTC, 2026-08-06 — agencia
- [Bid Strategies Best Practices](https://www.jonloomer.com/bid-strategies-best-practices-for-meta-advertising/) — Jon Loomer, 2023 (act. 2025-03) — practitioner
- [The Master Brief](https://www.jonloomer.com/meta-ads-master-brief/) — Jon Loomer, 2026-07-02 — practitioner
