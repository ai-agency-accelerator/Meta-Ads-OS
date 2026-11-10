# Presupuesto: reglas oficiales, cálculo relativo al CPA y recomendaciones por nivel (50-100 €, 500 €, 5.000 €, 50.000 €/día)

> Última verificación: 2026-10-16 · Autor: A02 (agente) · Ámbito: mínimos, presupuesto por ad set/creativo, relación con CPA y volumen, daily vs lifetime, campaign budget, sobre-gasto diario, budget scheduling, budget sharing; escenarios por tamaño de cuenta. Estrategias de puja y escalado fino: área 09. Economía unitaria (CAC/LTV/MER): área 09/13.

## TL;DR

- **Daily budget = media semanal, no tope diario.** Meta puede gastar **hasta un 75 % más** en un día (175 % del presupuesto), pero **no más de 7× el presupuesto diario en la semana natural domingo-sábado**. Con *ad set budget sharing* activo, el máximo diario sube a **210 %** y el semanal a 8,4×. Meta considera reembolsos por encima de esos límites. **[OFFICIAL META]** ([HC 190490051321426](https://www.facebook.com/business/help/190490051321426))
- **Antes era 25 %**: el aumento a 75 % se desplegó de forma gradual (Loomer lo cubrió como novedad "para las fiestas y en adelante", probablemente finales de 2024; fecha exacta no verificada) y hoy es el texto vigente; el "25 %" sobrevive solo en la proración a mitad de semana (margen de +25 % del diario). Algunas páginas antiguas y blogs aún citan 25 %. **[OFFICIAL META]** (texto actual) + **[OUTDATED]** (la cifra del 25 % diario)
- **Reglas de dimensionado oficiales**: daily budget **≥10× el coste medio del performance goal**; con *cost per result goal*, daily budget **≥5× el objetivo de coste**; value optimization: presupuesto para **≥50 conversiones/semana** (≥100 para pLTV/profit). **[OFFICIAL META]** ([HC 355670007911605](https://www.facebook.com/business/help/355670007911605), [HC 203183363050448](https://www.facebook.com/business/help/203183363050448), [HC 296463804090290](https://www.facebook.com/business/help/296463804090290))
- **Regla práctica de referencia (no oficial pero coherente con learning):** presupuesto semanal por ad set ≈ 50 × CPA esperado → diario ≈ 7 × CPA. Con CPA 50 € → ~350 €/día por ad set. Cada ad set adicional que persigue el mismo objetivo suma. **[EMPIRICAL]** ([Loomer, 2026-02-02](https://www.jonloomer.com/meta-advertising-budget/))
- **Si estás por debajo de ese presupuesto: consolida (1 campaña, 1 ad set) y acepta menos estabilidad, o elige una acción más barata que siga siendo valiosa.** No reparte 50 €/día entre 5 ad sets ni hagas "tests" de 10 €. **[EMPIRICAL]**
- **Lifetime budget = tope duro** para todo el periodo; necesario para *ad scheduling* (dayparting). **Budget scheduling** (subidas temporales de un daily budget): hasta 50 periodos por campaña/ad set, ≤8× el diario, ≥3 h, no recurrentes, no disponible en Advantage+ app. **[OFFICIAL META]** ([HC 214319341922580](https://www.facebook.com/business/help/214319341922580), [Developers](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/high-demand-period))
- **Las cuentas nuevas tienen un daily spending limit fijado por Meta** que sube con historial y pagos; condiciona cualquier plan de arranque agresivo. **[OFFICIAL META]** ([HC 563129151097553](https://www.facebook.com/business/help/563129151097553))
- **Cambios de presupuesto grandes pueden reiniciar learning** (Meta: 100→1.000 $ puede; 100→101 $ no). No hay "regla del 20 %" oficial. **[OFFICIAL META]**

---

## 1. Mecánica oficial del gasto

### 1.1 Daily budget
- "Your daily budget tells Meta an approximate amount to spend per day over the course of the week starting Sunday and ending Saturday."
- Flexibilidad: hasta **+75 %** en días con mejores oportunidades; **máximo diario 175 %**; **máximo semanal 7×**.
- Si empiezas a mitad de semana o cambias el presupuesto: límite para el resto de la semana = nuevo diario × días restantes **+ hasta 25 % del diario**.
- Cambio a mitad del día: nuevo objetivo para el resto del día; límite = 75 % sobre el **mayor** presupuesto vigente ese día. Es facturable lo gastado hasta el 175 % del mayor presupuesto del día.
- Reembolsos: Meta "will consider" reembolsar gasto por encima de 1,75× diario o 7× semanal.
- Ejemplo oficial: 100 $/día → máx 175 $ un día, máx 700 $ semana (840 $ con budget sharing).
- **[OFFICIAL META]** ([HC 190490051321426](https://www.facebook.com/business/help/190490051321426))

Implicaciones **[STRONG INFERENCE]**:
- No juzgues "sobre-gasto" por días; mira semanas naturales.
- Bajar presupuesto a las 17:00 puede no surtir efecto ese día (Meta lo advierte en [HC 203183363050448](https://www.facebook.com/business/help/203183363050448)).
- Si el negocio tiene un tope diario estricto (caja, stock), usa lifetime budgets o account/campaign spending limits.

### 1.2 Lifetime budget
- Total para toda la vida de la campaña/ad set; **tope duro**; "standard delivery" intenta repartirlo, pero gasta más en días con mejores oportunidades. **[OFFICIAL META]** ([HC 1844835042445690](https://www.facebook.com/business/help/1844835042445690), [HC 214319341922580](https://www.facebook.com/business/help/214319341922580))
- Necesario para programar horas/días (ad scheduling). Al bajarlo, debe quedar ≥ gastado + 10 % de lo gastado en los últimos 2 días. **[OFFICIAL META]**
- **Cuándo usarlo**: campañas con fecha fin (eventos, lanzamientos, promociones), presupuestos cerrados por cliente, dayparting justificado por datos.
- **Cuándo no**: evergreen (los cambios de fecha/importe son más torpes y el pacing a fin de periodo puede forzar gasto).

### 1.3 Advantage+ campaign budget (campaign budget)
- Reparte en tiempo real entre ad sets; "best suited for campaigns with at least 2 ad sets"; con 1 ad set equivale a ad set budget; evaluar a nivel campaña; puede gastar casi todo en un ad set. **[OFFICIAL META]** ([HC 153514848493595](https://www.facebook.com/business/help/153514848493595), [HC 1602924913861363](https://www.facebook.com/business/help/1602924913861363))
- Spending limits por ad set (min/max, % o importe): usar poco; max se gestiona semanalmente; min es objetivo, no garantía; cuidado con cost controls + min spend. **[OFFICIAL META]** ([HC 454681230514942](https://www.facebook.com/business/help/454681230514942))
- Es normal que el coste medio por evento suba con el tiempo dentro de un periodo: el sistema coge primero las oportunidades más baratas. **[OFFICIAL META]** ([HC 220698029821552](https://www.facebook.com/business/help/220698029821552))

### 1.4 Ad set budget sharing (2025)
- Sin campaign budget, permite compartir hasta 20 % del diario de cada ad set con los demás; el gasto a nivel campaña no cambia. Máx diario por ad set = (diario + compartido) × 1,75; semanal = (diario + compartido) × 7. **[OFFICIAL META]** ([HC 1388266028979935](https://www.facebook.com/business/help/1388266028979935))
- Uso: cuando necesitas control por ad set (bid strategies o calendarios distintos) pero quieres algo de flexibilidad.

### 1.5 Budget scheduling (high demand periods)
- Sube un daily budget en franjas concretas (importe o %), vuelve solo al presupuesto base. ≤50 periodos por campaña/ad set; ≤8× el diario; ≥3 h; no recurrente; no en Advantage+ app campaigns. **[OFFICIAL META]** ([Developers, high demand period](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/high-demand-period))
- Mejor que duplicar campañas para BFCM/rebajas: no crea objetos nuevos. Si la subida es grande, puede considerarse significant edit (asumir inestabilidad). **[STRONG INFERENCE]**

### 1.6 Mínimos
- Meta exige un mínimo según vertical, tipo de presupuesto, buying type, bid strategy, optimización, moneda y calendario; avisa en Ads Manager. Recomendaciones: presupuesto suficiente para el evento elegido; con cost per result goal ≥5× el objetivo. **[OFFICIAL META]** ([HC 203183363050448](https://www.facebook.com/business/help/203183363050448))
- "Your daily budget should be at least 10 times the average cost of your performance goal" (ejemplo: link click a 5 $ → 50 $/día). **[OFFICIAL META]** ([HC 355670007911605](https://www.facebook.com/business/help/355670007911605))

### 1.7 "Rolling budget" — no verificado
- Foxwell (jul 2026) menciona un "rolling budget" que reparte un presupuesto diario a lo largo de 7 días y advierte de que "a big single-day budget no longer guarantees that the full amount will spend that day". No encontrado en Help Center ni Developers. **[HYPOTHESIS]** — puede ser el mismo mecanismo de flexibilidad del 75 %/7× descrito con otro nombre o una función en test.

## 2. Cómo dimensionar el presupuesto (método)

1. **Elige el evento de optimización** (archivo 02) y estima un **CPA realista** (histórico; si no hay, conservador: Loomer sugiere suponer CPA ≈ precio del producto para un producto de 100 $). **[EMPIRICAL]**
2. **Presupuesto mínimo por ad set para estabilidad** ≈ 50 × CPA / 7 por día (≈ 7 × CPA). **[EMPIRICAL]** (regla práctica)
3. **Contrasta con la guía oficial** de 10× coste del goal por día (más exigente: con CPA 30 € → 300 €/día). Interprétala como "para aprendizaje holgado", no como mínimo para empezar. **[STRONG INFERENCE]**
4. **Multiplica por nº de ad sets** que persigan el mismo objetivo (tests, remarketing, geos…). Con campaign budget puedes quedarte por debajo siempre que al menos un ad set llegue al ritmo. **[EMPIRICAL]**
5. **Si el resultado supera lo que puedes gastar**: reduce ad sets → 1; si sigue sin llegar, acepta menos eventos (más varianza, decisiones más lentas) o cambia a una acción más barata **que sea valiosa en sí** (producto de entrada, lead cualificado). Evita ATC/IC salvo como puente (archivo 02, **[CONTESTED]**).
6. **Presupuesto para creatividades**: no hay regla oficial. Para juzgar un concepto por compras necesitas del orden de **≥1-3× CPA de gasto** y, para comparar dos conceptos con algo de confianza, **≥10-20 conversiones por brazo**. Con presupuestos pequeños, deja que Meta reparta y evalúa en agregado. **[STRONG INFERENCE]**; CTC usa "spend < 3× CPA target" como criterio para dar más oportunidad a anuncios infra-gastados en una campaña aparte. **[EMPIRICAL]**
7. **Escala por pasos y mira el coste marginal, no el medio**: el CPA medio sube al agotar las oportunidades baratas. **[OFFICIAL META]** (comportamiento de campaign budget) + **[STRONG INFERENCE]**

## 3. Recomendaciones por nivel (con supuestos explícitos)

> Todos los escenarios suponen: tracking correcto (pixel + CAPI), Advantage+ on por defecto, creatividad razonable. Las cifras son **[STRONG INFERENCE]** salvo cuando se citan fuentes. Cambia la recomendación si cambian los supuestos (ver "cuándo cambiaría").

### Nivel 1 — 50-100 €/día (≈1.500-3.000 €/mes)

**Supuestos A (e-commerce)**: AOV 50-70 €, CPA real 25-40 € → 1,5-4 compras/día → **10-28 compras/semana**.
**Supuestos B (lead gen local)**: CPL 8-20 € → 25-90 leads/semana.
**Supuestos C (high-ticket/B2B)**: CPL 60-150 € → 3-12 leads/semana.

Recomendación:
- **1 campaña, 1 ad set**, Advantage+ on, país(es) objetivo, sin capas de intereses (o como sugerencia mínima), Advantage+ placements.
- **A**: optimiza a **Purchase** aunque quede "Learning limited"; 3-6 anuncios de conceptos distintos; nada de retargeting separado ni campaña de test. Si en 3-4 semanas no llegas ni a ~8-10 compras/semana con CPA viable, revisa oferta/landing/precio antes que la estructura; como puente, considera una oferta de entrada (bundle, primer pedido) antes que ATC.
- **B**: Leads con instant form "higher intent" o website form; 1 ad set; vigila calidad desde la semana 1 (CRM/hoja); con ~200 leads/mes ya cumples el mínimo de Meta para conversion leads → monta CAPI CRM para pasar a qualified leads. **[OFFICIAL META]** (umbral 200/mes)
- **C**: con <10 leads/semana el sistema apenas aprende; opciones: subir presupuesto, bajar fricción (lead magnet cualificado), o aceptar un canal que se evalúa mensualmente. No fragmentar.
- **Daily vs lifetime**: daily (evergreen).
- **Escalado**: subidas espaciadas; no esperes estabilidad estadística en días.

Cuándo cambiaría: si CPA real < 15 € (más de 30 compras/semana) → puedes plantear value optimization más adelante; si CPA > presupuesto diario → objetivo/evento inadecuado para ese presupuesto.

### Nivel 2 — ~500 €/día (≈15.000 €/mes)

**Supuestos A**: e-commerce, CPA 30-40 € → 12-17 compras/día → **85-115/semana**.
**Supuestos A'**: high-AOV (300 €), CPA 100 € → 5/día → 35/semana.
**Supuestos B**: lead gen, CPL 20-30 € → 115-175 leads/semana.

Recomendación:
- **A**: 1 campaña Sales con campaign budget y **1-2 ad sets** con propósito (p. ej. mercado principal + secundario con economía distinta, o broad + ad set de existentes con max spend si el reporting de segments muestra exceso de gasto en clientes). 10-20 anuncios activos con diversidad real; refresco por lotes. **Value optimization** es viable (≥50 compras/semana): test de 3 semanas sin ROAS goal (protocolo oficial). Definir **audience segments** desde el día 1.
- **A'**: 1 ad set; Purchase; no value optimization todavía (35/semana).
- **B**: 1 campaña Leads (Website & instant forms o la location ganadora); qualified leads con CAPI CRM; 1-2 ad sets solo si hay líneas de servicio con valor muy distinto; value rules si hay segmentos de baja calidad demostrados.
- **Testing**: creative testing tool dentro del ad set o lotes de 2-4 anuncios por concepto; una campaña de test separada aún suele fragmentar demasiado.
- **Remarketing**: no separado por defecto; mira segments (si >30-40 % del gasto va a engaged/existentes con baja incrementalidad, actúa con CLS/exclusiones/value rules — archivo 09).

Cuándo cambiaría: si hay 2-3 países con CPA muy distinto → campaña por país o value rules; si hay catálogo grande → Advantage+ catalog ads en el mismo ad set.

### Nivel 3 — ~5.000 €/día (≈150.000 €/mes)

**Supuestos A**: e-commerce multi-mercado, CPA nuevo cliente 40-60 € → 85-125 compras/día → **600-875/semana**; base de clientes de decenas de miles.
**Supuestos B**: lead gen multi-servicio, CPL 40-60 € → 85-125 leads/día.

Recomendación:
- **Arquitectura**: 2-5 campañas con razón de ser: (1) evergreen adquisición (Sales, value optimization, Customer lifecycle "Acquire new customers" o exclusiones), (2) retención/existentes si la base es grande y su economía distinta (o ad set con max spend), (3) campaña por mercado si la economía difiere, (4) "moments" para promociones, (5) opcional: campaña de testing con criterio de graduación. **[EMPIRICAL]** (CTC) + **[STRONG INFERENCE]**
- **Pujas**: empezar con highest volume/value; probar ROAS goal o cost per result goal en campañas duplicadas con el mismo pool creativo cuando el objetivo sea eficiencia marginal (área 09). Con cost per result goal, presupuesto ≥5× el objetivo. **[OFFICIAL META]**
- **Creatividad**: 20-50 anuncios nuevos/semana entre conceptos e iteraciones; vigilar el **límite de anuncios por Página** (con <1M $/mes de pico: 1.000 anuncios activos o en revisión). **[OFFICIAL META]** ([HC 766697140509126](https://www.facebook.com/business/help/766697140509126))
- **Medición**: incrementalidad trimestral (lift o geo-holdout), MER/nCAC semanal; no fiarse del ROAS de plataforma para repartir entre adquisición y retención (Haus: Advantage+ sobre-reporta ~12 pp). **[EMPIRICAL]**
- **Budget scheduling** para picos en vez de duplicar campañas.
- **Lead gen**: qualified leads/value por línea de servicio; CAPI CRM obligatorio; value rules por location/edad; considerar sequenced events si se habilita.

Cuándo cambiaría: si el CPA sube rápido con el gasto (curva de rendimientos decrecientes pronunciada) → más mercados/productos/creatividad antes que más presupuesto en la misma campaña.

### Nivel 4 — ~50.000 €/día (≈1,5 M€/mes)

**Supuestos**: anunciante grande multi-mercado o multi-línea; CPA 40-80 € → 600-1.250 conversiones/día; MMM o programa de lift existente.

Recomendación:
- **Organización**: ad accounts por mercado/entidad/moneda cuando proceda (no por "diversificar subastas"; el overlap entre cuentas existe). Facturación mensual (sin daily spending limit de Meta). **[OFFICIAL META]**
- **Arquitectura por mercado**: evergreen adquisición con portfolio de bid strategies (highest value, ROAS goal, cost per result goal, bid cap) y presupuestos "inflados" con cost controls para mover liquidez entre días/horas; retención; moments; testing industrializado (decenas-cientos de conceptos/semana); underspend campaign para anuncios con poco gasto (CTC). **[EMPIRICAL]**
- **Límites**: tier de anuncios por Página (<10 M$/mes pico → 5.000; ≥10 M$ → 20.000); ≤70 ad sets por campaña con campaign budget para no perder edición; reglas automáticas de seguridad para cost/bid caps. **[OFFICIAL META]**
- **Medición**: MMM + geo-lift + conversion lift; decisiones de presupuesto con iROAS marginal ("last-dollar"), no con medias. Haus: los efectos omnicanal (retail, Amazon) pueden ser grandes; en marcas con ≥25 % de negocio no-DTC ~32 % del impacto de Meta cae fuera de DTC. **[EMPIRICAL]** ([Haus, 2025](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments))
- **Riesgo**: plan de continuidad ante restricciones de cuenta (área 08), soporte de Meta (partner/rep).

Cuándo cambiaría: si el negocio depende de un único mercado/producto, la arquitectura debería parecerse más al nivel 3 (más presupuesto ≠ más campañas); la complejidad debe venir de la heterogeneidad del negocio, no del tamaño del presupuesto.

## 4. Cuentas pequeñas vs grandes: diferencias que importan

| Aspecto | Pequeña (<300 €/día) | Grande (>5.000 €/día) |
|---|---|---|
| Restricción dominante | Volumen de señal | Rendimientos decrecientes y saturación creativa |
| Riesgo principal | Fragmentar | Sobre-invertir en lo "atribuido" pero no incremental |
| Estructura | 1 campaña/1 ad set | Portfolio por mercado/objetivo/puja |
| Testing | Dentro del ad set, en lotes | Campaña/proceso dedicado con potencia |
| Medición | Backend + atribución de plataforma | Lift/geo/MMM |
| Pujas | Highest volume/value | Mezcla con cost controls |

## Implicaciones operativas

- Calcula y documenta para cada campaña: CPA objetivo, eventos/semana esperados por ad set, presupuesto semanal y si cumple ~50 × CPA. Si no cumple, justifica por qué hay más de un ad set.
- Revisa el gasto por semana natural, no por día.
- Para picos (BFCM, rebajas): budget scheduling o subida en la campaña existente; evita duplicar campañas con 5 días de antelación.
- Con cost per result goal: presupuesto ≥5× objetivo; si no gasta, el objetivo es demasiado bajo, no "el algoritmo está roto".

## Errores frecuentes

1. Pensar que 100 €/día de daily budget es un tope diario.
2. Repartir presupuestos pequeños en muchos ad sets o campañas.
3. Tests creativos de 5-10 €/día por anuncio juzgados con 1-2 conversiones.
4. Cambiar el presupuesto varias veces al día.
5. Cost cap con presupuesto apenas superior al cap (no entrega).
6. Lifetime budgets en evergreen sin necesidad.
7. Escalar duplicando en vez de subir presupuesto/budget scheduling.

## Preguntas abiertas

- Confirmación oficial del "rolling budget" (Foxwell 2026).
- ¿Cuándo se generalizó exactamente el 75 % de flexibilidad? (Meta lo describía en 2024 como "gradually introducing"; hoy es el texto principal.)
- Curvas reales de rendimientos decrecientes por vertical (área 11).

## Fuentes clave

- [About daily budgets](https://www.facebook.com/business/help/190490051321426) — Meta HC — meta-oficial
- [About budgets](https://www.facebook.com/business/help/214319341922580) — Meta HC — meta-oficial
- [Best practices for minimum budgets](https://www.facebook.com/business/help/203183363050448) — Meta HC — meta-oficial
- [About performance goals](https://www.facebook.com/business/help/355670007911605) — Meta HC — meta-oficial
- [About ad set budget sharing](https://www.facebook.com/business/help/1388266028979935) — Meta HC — meta-oficial
- [About lifetime budgets](https://www.facebook.com/business/help/1844835042445690) — Meta HC — meta-oficial
- [About ad set spend limits](https://www.facebook.com/business/help/454681230514942) — Meta HC — meta-oficial
- [Understand Advantage+ campaign budget results](https://www.facebook.com/business/help/220698029821552) — Meta HC — meta-oficial
- [High demand period (budget scheduling)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/high-demand-period) — Meta Developers — meta-developers
- [About daily spending limits set by Meta](https://www.facebook.com/business/help/563129151097553) — Meta HC — meta-oficial
- [How to Think About Your Meta Advertising Budget](https://www.jonloomer.com/meta-advertising-budget/) — Jon Loomer, 2026-02-02 — practitioner
- [How Meta Actually Works in 2026](https://commonthreadco.com/blogs/ecommerce-playbook/how-meta-actually-works-in-2026) — CTC, 2026-07-07 — agencia
- [The 9 Most Pressing Meta Ad Topics for Q3 2026](https://www.foxwelldigital.com/blog/the-9-most-pressing-topics-for-meta-advertisers-in-q3-2026) — Foxwell, 2026-07-03 — agencia
