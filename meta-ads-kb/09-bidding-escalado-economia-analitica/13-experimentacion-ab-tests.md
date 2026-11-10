# Experimentación para media buying: A/B tests de Meta, creative testing, holdouts y diseño correcto

> Última verificación: 2026-10-16 · Autor: A09 (agente) · Ámbito: Meta Experiments (A/B test), herramienta de creative testing (2025), A/B con holdout, cuándo test formal vs "en vivo", diseño (hipótesis, potencia, duración, una variable), errores. Conversion Lift/MMM en detalle: área 04.

## TL;DR

- **Meta no recomienda testear "a mano" (encender/apagar ad sets o comparar campañas en vivo)**: produce entrega ineficiente, audiencias solapadas y resultados poco fiables. El A/B test divide la audiencia en grupos aleatorios **sin solapamiento**. **[OFFICIAL META]** ([About A/B testing](https://www.facebook.com/business/help/1738164643098669))
- **A/B test de Meta**: hasta **5 versiones**, duración **1–30 días**, presupuesto igual recomendado, ganador por **menor coste por resultado** de la métrica elegida, calculado simulando "decenas de miles" de resultados posibles y expresado como % de confianza. Meta recomienda **≥80 % de "estimated power"** al crearlo. **[OFFICIAL META]** ([About Experiments](https://www.facebook.com/business/help/1915029282150425), [Winners](https://www.facebook.com/business/help/166313650471318), [Duplicate → A/B test](https://www.facebook.com/business/help/560857351380163))
- **A/B con holdout** permite comparar **coste por compra incremental** entre estrategias (no solo coste atribuido). **[OFFICIAL META]**
- **Creative testing tool (oct-2025)**: 2–5 anuncios nuevos duplicados del original dentro del ad set, reparto de gasto similar, sin solapamiento; Meta recomienda ≤20 % del presupuesto; 7 días por defecto; **solo Highest volume**. Tras el test Meta deja de equilibrar y no favorece necesariamente al ganador. **[EMPIRICAL]** ([Loomer, oct-2025](https://www.jonloomer.com/meta-creative-testing/))
- **La potencia manda**: para detectar un 20 % de diferencia de CPA hacen falta ~470 conversiones por brazo; un test de 2 semanas con 30 conversiones por brazo solo detecta diferencias >100 %. Diseña tests de **diferencias grandes** (estrategia, oferta, concepto). **[STRONG INFERENCE]** (ver [12](12-razonamiento-estadistico.md))
- **Una variable por test** si quieres aprender; multivariable solo para elegir entre dos "paquetes" concretos (Meta lo dice así). **[OFFICIAL META]** ([Testing more than one variable](https://www.facebook.com/business/help/455527338244675))
- **Para preguntas de incrementalidad** (¿cuánto aporta Meta/retargeting/Advantage+?), Conversion Lift o geo-holdout: Meta exige ≥7 días y ≥10 % de audiencia por celda en Conversion Lift; Haus: duración media de 18,6 días + 8,8 de post-tratamiento en 640 tests. **[EMPIRICAL]** ([Haus](https://www.haus.io/article/meta-incrementality-testing))
- **Los tests de lift pueden subir el CPM** de las campañas en test (por los grupos de control). **[OFFICIAL META]**

---

## 1. Qué herramienta para qué pregunta

| Pregunta | Herramienta | Métrica de decisión | Etiqueta |
|---|---|---|---|
| ¿Qué estrategia es mejor (bid strategy, evento de optimización, value vs volume, estructura, A+ vs manual)? | **A/B test (Experiments)**, 2–5 versiones | Coste por resultado (o por compra incremental con holdout) | [OFFICIAL META] |
| ¿Qué concepto creativo funciona mejor dentro de mi ad set? | **Creative testing tool** o A/B test de anuncio | Coste por resultado; además hook/CTR | [EMPIRICAL] |
| ¿Cuánto vende de más Meta (o una campaña)? | **Conversion Lift** o **geo-holdout** | Conversiones/ingresos incrementales, iROAS | [OFFICIAL META]/[EMPIRICAL] |
| ¿Qué presupuesto maximiza beneficio? | Test de **dosis** (geo 0×/1×/2×) o escalones sostenidos | CPA/iROAS marginal | [EMPIRICAL] (Haus) |
| ¿Funciona este ajuste menor (copy, color)? | Normalmente **no testear formalmente** (sin potencia); iterar | — | [STRONG INFERENCE] |
| Brand lift (recuerdo, awareness) | Brand Lift (requisito: ≥120.000 $ de gasto en 90 días) | Lift en encuestas | [OFFICIAL META] |

## 2. A/B test en Meta: cómo funciona (2026)

- **Creación**: desde la barra de Ads Manager (recomendado), desde Experiments, al crear campaña (puede no estar disponible) o duplicando campaña/ad set/anuncio → "New split test campaign". Variables: creatividad, audiencia, placements, custom (varias). **[OFFICIAL META]** ([Tools to create A/B tests](https://www.facebook.com/business/help/1159714227408868), [Selecting a variable](https://www.facebook.com/business/help/1597318281091985))
- **Asignación**: audiencia aleatorizada en grupos sin solapamiento ("nobody sees more than one version"). **[OFFICIAL META]**
- **Presupuesto**: si duplicas campaña, se duplica el presupuesto; Meta recomienda el mismo presupuesto por versión. **[OFFICIAL META]**
- **Duración**: 1–30 días; **estimated power** visible al configurar; recomendado ≥80 %. **[OFFICIAL META]**
- **Ganador**: menor coste por resultado en la métrica elegida; Meta simula decenas de miles de veces para estimar con qué frecuencia ganaría cada versión → % de confianza. Si no hay ganador claro, muestra "top-performing" o recomienda extender. Advierte que el ganador puede tener costes mayores si el test fue corto, con pocos resultados o sin buenas prácticas. **[OFFICIAL META]** ([Viewing results](https://www.facebook.com/business/help/1376548572415613))
- **Holdout**: añadir holdout para comparar coste por compra incremental. **[OFFICIAL META]**
- **Infra-entrega**: al dividir la audiencia, los ad sets en test son más vulnerables a infra-entrega; ampliar audiencias y presupuesto; diferencias demasiado pequeñas entre versiones impiden declarar ganador. **[OFFICIAL META]** ([Tips](https://www.facebook.com/business/help/135668260430624))

## 3. Diseño correcto (checklist)

1. **Hipótesis escrita** específica, accionable y ligada a negocio ("La optimización a valor generará ≥15 % más margen de contribución por euro que la de volumen en 3 semanas"). Meta pide elegir hipótesis antes de la variable. **[OFFICIAL META]** ([Choosing a hypothesis](https://www.facebook.com/business/help/2358258211160819))
2. **Métrica primaria única** (y su ventana de atribución) definida antes; métricas secundarias como guardarraíles (AOV, % nuevos, CPM).
3. **Tamaño de efecto mínimo relevante** (MDE) en términos de negocio → conversiones necesarias por brazo (tabla en [12](12-razonamiento-estadistico.md)) → presupuesto y días: `presupuesto por brazo ≈ conversiones necesarias × CPA esperado`.
4. **Potencia ≥80 %** (Meta lo recomienda y lo muestra).
5. **Duración fija**: mínimo 7 días (ciclo semanal); para value optimization Meta recomienda ≥3 semanas porque el pico llega tras ~2. Sin parar antes por "significancia" (peeking). **[OFFICIAL META]** + **[STRONG INFERENCE]**
6. **Una variable** (o paquete explícito si es multivariable).
7. **Nada de ediciones** durante el test (cada edición reinicia learning en ese brazo).
8. **Evitar picos estacionales** salvo que la pregunta sea sobre el pico; o asegurarse de que ambos brazos lo viven igual (lo hacen, por aleatorización, pero el resultado puede no generalizar).
9. **Learning en ambos brazos**: si cada brazo no alcanza ~50 eventos/semana, el test compara "dos cosas en learning".
10. **Registrar** en el log de tests: hipótesis, diseño, fechas, resultado, IC, decisión ([10](10-dashboards-reporting.md)).

Ejemplo de dimensionamiento: CPA esperado 40 $; queremos detectar 30 % de diferencia → ~230 conversiones por brazo → ~9.200 $ por brazo (18.400 $ total); con 2 brazos a 400 $/día cada uno → 23 días. Si eso no cabe, **testea algo con un efecto esperado mayor** o usa un evento proxy de más volumen (con el riesgo de que el proxy no prediga el evento final). **[STRONG INFERENCE]**

## 4. Creative testing: tool vs campaña de testing vs "en vivo"

| Enfoque | Pros | Contras | Cuándo |
|---|---|---|---|
| **Creative testing tool** (2025) | Reparto similar, sin solapamiento, dentro del ad set real | Solo Highest volume; duplica anuncios (original excluido); tras el test Meta no sigue el resultado | Comparar 2–5 conceptos distintos con presupuesto suficiente |
| **Campaña/ad set de testing separado** (p. ej., A+CB con anuncios nuevos) | Protege la campaña principal; volumen controlado | Auction overlap con la principal; Meta reparte desigual → no es experimento | Filtrar muchos conceptos en bruto ("qué recibe gasto y CTR") |
| **"En vivo"** (añadir anuncios al ad set principal) | Real; Meta asigna gasto a lo que predice mejor | Sin control: el gasto desigual mezcla selección y rendimiento; añadir anuncios es significant edit | Iteraciones de conceptos ya validados |
| **A/B test de anuncio** | Formal, con potencia y confianza | Más presupuesto y tiempo | Decisiones creativas estratégicas (formato, ángulo principal) |

Recomendaciones de practitioners (Loomer 2025-2026): no lanzar 20–50 anuncios a la vez; testear conceptos **sustancialmente distintos**; buscar **temas** ganadores para el siguiente lote, no "el" anuncio; no sobrerreaccionar a muestras pequeñas. **[EMPIRICAL]**

Interpretación del "gasto como voto": que Meta concentre gasto en un anuncio es señal de su predicción de rendimiento, no prueba de mejor CPA incremental; Motion define "ganador" como ≥10× la mediana de gasto, no por ROAS. **[EMPIRICAL]**

## 5. Holdouts e incrementalidad (lo esencial para media buying)

- **Factor de incrementalidad (IF)** = conversiones incrementales / conversiones reportadas por la plataforma; iROAS = ROAS plataforma × IF. Ej.: ROAS 4× × IF 0,7 = 2,8× (no rentable si el break-even es 3×). **[EMPIRICAL]** ([Haus](https://www.haus.io/article/meta-incrementality-testing))
- **Conversion Lift**: aleatoriza cuentas de usuario; ≥7 días; ≥10 % de audiencia en cada celda; requiere fuente de conversiones de calidad (p. ej., CAPI); puede reducir audiencia y subir CPM. **[OFFICIAL META]**/**[EMPIRICAL]**
- **Geo-holdout**: aleatoriza regiones; disponible para cualquiera con cobertura/volumen; control sintético más preciso que mercados emparejados (afirmación de Haus). Holdouts típicos 20–50 % durante semanas. **[EMPIRICAL]**
- **Errores**: tests sin potencia; factores externos (Haus cita un caso donde la escasez de un competidor explicó el "lift"); estacionalidad; medir solo DTC cuando hay retail/Amazon (32 % del impacto fuera de DTC en marcas omnicanal). **[EMPIRICAL]**
- **Uso en puja**: objetivo de ROAS en plataforma = ROAS break-even / IF (ver [08](08-economia-unitaria-calculadoras.md)).

## 6. Errores de diseño frecuentes

1. **Comparar dos ad sets/campañas vivas** como si fuera un test (overlap, presupuestos y learning distintos). Meta lo desaconseja.
2. **Test sin potencia** (dos semanas, 20 conversiones por brazo) y conclusión firme.
3. **Parar al ver un buen resultado** (peeking: ~20 % de falsos positivos en 14 días mirando a diario).
4. **Muchas variantes sin corrección** (k=10 → 40 % de probabilidad de al menos un falso positivo).
5. **Cambiar cosas durante el test**.
6. **Audiencias demasiado parecidas** (Meta pone el ejemplo de mujeres 18–20 vs 20–22). **[OFFICIAL META]**
7. **Métrica equivocada**: CPA atribuido cuando la pregunta es incremental; CPL cuando importa el coste por venta.
8. **Generalizar** el resultado a otros objetivos/campañas: Meta recomienda repetir el test por objetivo. **[OFFICIAL META]**
9. **Ignorar el learning** de cada brazo (comparar fases distintas).
10. **Test en semana de BFCM** y aplicar el resultado en enero.

## 7. Plantilla de test

| Campo | Ejemplo |
|---|---|
| Pregunta / hipótesis | Highest value + ROAS goal 2,4 vs Highest volume: +15 % de contribución por € |
| Tipo | A/B test (Experiments), 2 versiones, sin holdout |
| Métrica primaria / ventana | Contribución atribuida por € (calculada) — 7d click; guardarraíles: % nuevos, AOV |
| MDE / potencia / α | 20 % / 80 % / 0,05 |
| Conversiones necesarias por brazo | ~470 |
| Presupuesto y duración | 470 × CPA 35 $ ≈ 16.500 $/brazo; 21 días |
| Reglas | Sin ediciones; no mirar resultados antes del día 21 salvo roturas |
| Decisión pre-registrada | Si B gana con ≥90 % de confianza y guardarraíles OK → migrar 50 % del gasto y re-testear en 6 semanas |

## Implicaciones operativas

- Calendario trimestral de tests estratégicos (2–4 por trimestre), dimensionados por potencia.
- Creative testing continuo (concept-level) con la herramienta o campaña de testing; decisiones a nivel de tema.
- Un test de incrementalidad por año (mínimo) en la unidad de mayor gasto; actualizar IF.

## Errores frecuentes

(ver sección 6)

## Preguntas abiertas

- Umbral de confianza exacto con el que Meta declara "winner" (no localizado en la documentación consultada).
- Si la herramienta de creative testing admite ya bid strategies distintas de Highest volume (a oct-2025 no).
- Requisitos actuales de Conversion Lift self-serve (el área 04 debe verificar).

## Fuentes clave

- [About A/B testing](https://www.facebook.com/business/help/1738164643098669) — Meta — meta-oficial
- [About Experiments](https://www.facebook.com/business/help/1915029282150425) — Meta — meta-oficial
- [How winning campaigns are determined](https://www.facebook.com/business/help/166313650471318) — Meta — meta-oficial
- [Viewing and understanding A/B test results](https://www.facebook.com/business/help/1376548572415613) — Meta — meta-oficial
- [Tips for improving your A/B tests](https://www.facebook.com/business/help/135668260430624) — Meta — meta-oficial
- [Create an A/B test by duplicating](https://www.facebook.com/business/help/560857351380163) — Meta — meta-oficial
- [Testing more than one variable](https://www.facebook.com/business/help/455527338244675) — Meta — meta-oficial
- [Choosing a hypothesis](https://www.facebook.com/business/help/2358258211160819), [Selecting a variable](https://www.facebook.com/business/help/1597318281091985), [Tools to create A/B tests](https://www.facebook.com/business/help/1159714227408868) — Meta — meta-oficial
- [Meta's Creative Testing Tool](https://www.jonloomer.com/meta-creative-testing/) — Jon Loomer, 2025-10-13 — practitioner
- [Understanding Meta incrementality testing](https://www.haus.io/article/meta-incrementality-testing) — Haus, 2026 — vendor
- [The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — Haus, 2025-07-28 — vendor
