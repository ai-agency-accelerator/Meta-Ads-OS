# Razonamiento estadístico práctico para media buying

> Última verificación: 2026-10-16 · Autor: A09 (agente) · Ámbito: ruido de Poisson en conversiones, intervalos de confianza para CPA y tasas, tamaño de muestra, comparaciones múltiples, regresión a la media, peeking, sobredispersión. **Todas las tablas están calculadas con python** (intervalos exactos de Garwood, Wilson, aproximación log-ratio y simulaciones Monte Carlo; scripts reproducibles descritos al final).

## TL;DR

- **Con gasto fijo, la incertidumbre del CPA es la del número de conversiones.** Con 10 conversiones, el CPA real puede estar entre **0,54× y 2,09×** el observado (IC95 %); con 30, entre 0,70× y 1,48×; con 100, entre 0,82× y 1,23×. **[STRONG INFERENCE]** (cálculo exacto Poisson)
- **Para que una diferencia de CPA entre dos anuncios/ad sets con el mismo gasto sea estadísticamente significativa (p<0,05)** hace falta: con 30 conversiones por brazo, ~**66 %** de diferencia; con 100, ~**32 %**; con 300, ~**17 %**. **[STRONG INFERENCE]**
- **Para detectar con 80 % de potencia una diferencia real del 20 % hacen falta ~470 conversiones por brazo; del 10 %, ~1.730.** La mayoría de "tests" de anuncios en Meta no tienen potencia para detectar diferencias del 10–20 %. **[STRONG INFERENCE]**
- **Con 10 anuncios idénticos y ~30 conversiones esperadas cada uno, el "ganador" muestra un CPA ~21 % mejor que el real por puro azar** (mediana); con 20 anuncios y 10 conversiones, ~38 % mejor. **[STRONG INFERENCE]** (simulación)
- **Regresión a la media**: el mejor de 10 anuncios en la semana 1 (15 conv. esperadas) parece 1,47× la media; en la semana 2 baja a ~1,12×. Espera que los "ganadores" con poca muestra empeoren. **[STRONG INFERENCE]** (simulación)
- **Peeking**: mirar un test A/A cada día durante 14 días y parar al primer p<0,05 da **~20–22 % de falsos positivos** en lugar de 5 %. **[STRONG INFERENCE]** (simulación)
- **Variación diaria normal**: con una media de 20 conversiones/día, el 95 % de los días cae entre 12 y 29 (−40 % / +45 %) solo por Poisson; con variación real de ±15 % día a día, entre 11 y 32. **No reacciones a un día.** **[STRONG INFERENCE]**
- **Las tasas de funnel con pocas observaciones son muy inciertas**: 4 ventas de 20 llamadas (20 %) → IC95 % 8–42 %. **[STRONG INFERENCE]** (Wilson)
- **Meta usa simulación (decenas de miles de remuestreos) para declarar ganador con un % de confianza y recomienda ≥80 % de "estimated power"** en sus A/B tests. **[OFFICIAL META]** ([How winners are determined](https://www.facebook.com/business/help/166313650471318), [Duplicate → A/B test](https://www.facebook.com/business/help/560857351380163))

---

## 1. Modelo mental: las conversiones son conteos ruidosos

- Si una campaña tiene una tasa "real" estable, el número de conversiones en un periodo sigue aproximadamente una **Poisson**: varianza = media. Desviación típica relativa ≈ 1/√n.
- En la práctica hay **sobredispersión** (día de la semana, subasta, atribución tardía, cambios de mix): la varianza real es mayor que la Poisson. Las tablas siguientes son por tanto **cotas optimistas**: la incertidumbre real es mayor. **[STRONG INFERENCE]**
- Con gasto fijo S, CPA = S / n → la incertidumbre del CPA es la de n.

## 2. Tabla 1 — Intervalo de confianza del CPA según nº de conversiones

IC95 % exacto (Garwood) para el conteo; CPA real relativo al observado (gasto fijo).

| Conversiones observadas | IC95 % del conteo | CPA real entre … del observado |
|---|---|---|
| 5 | 1,6 – 11,7 | 0,43× – 3,08× |
| 10 | 4,8 – 18,4 | 0,54× – 2,09× |
| 20 | 12,2 – 30,9 | 0,65× – 1,64× |
| 30 | 20,2 – 42,8 | 0,70× – 1,48× |
| 50 | 37,1 – 65,9 | 0,76× – 1,35× |
| 100 | 81,4 – 121,6 | 0,82× – 1,23× |
| 200 | 173,2 – 229,7 | 0,87× – 1,15× |
| 400 | 361,8 – 441,2 | 0,91× – 1,11× |
| 1.000 | 939 – 1.064 | 0,94× – 1,06× |

Ejemplo: un ad set con 1.000 $ y 10 compras (CPA 100 $) tiene un CPA real plausible entre 54 $ y 209 $. Decidir "este ad set es malo" con eso es lanzar una moneda.

## 3. Tabla 2 — ¿Qué diferencia de CPA es distinguible del ruido? (dos brazos, mismo gasto)

Aproximación log-ratio: SE(ln ratio) ≈ √(1/n₁ + 1/n₂).

| Conversiones por brazo | Diferencia de CPA observada necesaria para p<0,05 | Diferencia real detectable con 80 % de potencia (MDE) |
|---|---|---|
| 10 | ≥ 140 % (ratio 2,40) | 250 % |
| 20 | ≥ 86 % | 143 % |
| 30 | ≥ 66 % | 106 % |
| 50 | ≥ 48 % | 75 % |
| 100 | ≥ 32 % | 49 % |
| 200 | ≥ 22 % | 32 % |
| 300 | ≥ 17 % | 26 % |
| 500 | ≥ 13 % | 19 % |
| 1.000 | ≥ 9 % | 13 % |

## 4. Tabla 3 — Conversiones por brazo para detectar una diferencia de CPA (80 % potencia, α=0,05 bilateral)

| Diferencia real de CPA | Conversiones por brazo |
|---|---|
| 5 % | ~6.600 |
| 10 % | ~1.730 |
| 15 % | ~800 |
| 20 % | ~470 |
| 30 % | ~230 |
| 50 % | ~96 |

**Consecuencia**: con presupuestos normales, los tests sirven para encontrar **diferencias grandes** (conceptos, ofertas, ángulos), no para optimizar matices del 5–10 %. **[STRONG INFERENCE]**

## 5. Lectura bayesiana (más intuitiva para decidir)

P(B tiene mejor CPA real que A) con el mismo gasto (posterior Gamma con prior débil):

| A | B | CPA de B vs A | P(B mejor) |
|---|---|---|---|
| 10 | 15 | −33 % | 84 % |
| 20 | 30 | −33 % | 92 % |
| 40 | 50 | −20 % | 85 % |
| 100 | 120 | −17 % | 91 % |
| 200 | 240 | −17 % | 97 % |

Uso: para decisiones reversibles y baratas (qué anuncio recibe el siguiente euro, qué concepto iterar) un 80–90 % puede bastar; para decisiones caras o difíciles de revertir (cambiar estrategia de puja de toda la cuenta, cambiar oferta) pedir ≥95 % y replicar. **[HYPOTHESIS]** (política de decisión razonada)

## 6. Tasas de funnel (show rate, close rate…) — intervalos de Wilson

| Observado | Tasa | IC95 % |
|---|---|---|
| 2/10 | 20 % | 5,7 – 51,0 % |
| 4/20 | 20 % | 8,1 – 41,6 % |
| 10/50 | 20 % | 11,2 – 33,0 % |
| 20/100 | 20 % | 13,3 – 28,9 % |
| 30/150 | 20 % | 14,4 – 27,1 % |
| 60/300 | 20 % | 15,9 – 24,9 % |
| 140/200 | 70 % | 63,3 – 75,9 % |

Implicación para value rules o CPL objetivo por segmento ([02](02-value-optimization-y-value-rules.md), [08](08-economia-unitaria-calculadoras.md)): con 4 ventas en un segmento, su close rate puede ser la mitad o el doble del observado → ajustes conservadores.

## 7. Variación diaria esperada (bandas de control)

| Media real de conversiones/día | 95 % de los días (solo Poisson) | Con variación real ±15 % diaria |
|---|---|---|
| 3 | 0 – 7 | — |
| 10 | 4 – 17 (−60 % / +70 %) | — |
| 20 | 12 – 29 (−40 % / +45 %) | 11 – 32 (−45 % / +60 %) |
| 50 | 36 – 64 (±28 %) | — |
| 100 | 80 – 120 (±20 %) | 69 – 140 (−31 % / +40 %) |

Úsalas como **bandas de alerta** en el dashboard diario ([10](10-dashboards-reporting.md)): fuera de banda → investigar (tracking, entrega, web); dentro → no hacer nada.

Tiempo para acumular muestra:

| Conversiones/día | 30 conv. | 50 conv. | 100 conv. |
|---|---|---|---|
| 2 | 15 días | 25 días | 50 días |
| 5 | 6 días | 10 días | 20 días |
| 10 | 3 días | 5 días | 10 días |
| 20 | 2 días | 2–3 días | 5 días |

(Mínimo 7 días igualmente, por el ciclo semanal y la atribución; ver [11](11-cuando-no-tocar-una-campana.md).)

## 8. Comparaciones múltiples

### 8.1 El "ganador" de muchos anuncios iguales

Simulación: k anuncios con **el mismo CPA real** y mismo gasto. CPA aparente del "mejor":

| k anuncios | 10 conv. esperadas/anuncio | 30 conv. | 100 conv. |
|---|---|---|---|
| 2 | 0,83× | 0,91× | 0,95× |
| 5 | 0,71× | 0,83× | 0,90× |
| 10 | 0,67× | 0,79× | 0,87× |
| 20 | 0,62× | 0,75× | 0,85× |

(mediana; el p10 es aún más extremo, p. ej., 0,56× con 10 anuncios y 10 conversiones)

### 8.2 Falsos positivos acumulados

P(≥1 falso positivo) comparando k variantes contra control a α=0,05: k=3 → 14 %; k=5 → 23 %; k=10 → 40 %; k=20 → 64 %. Corrección simple: **Bonferroni** (α/k) o, mejor para muchas variantes, controlar la tasa de falsos descubrimientos (Benjamini-Hochberg). **[STRONG INFERENCE]**

### 8.3 Además, en Meta el gasto no es igual

Dentro de un ad set Meta reparte el gasto de forma desigual (Loomer: un anuncio con ~50 % del gasto es normal; Motion: ~6 % de anuncios concentran la mayoría del gasto). Comparar CPA entre anuncios con gastos muy distintos mezcla **selección del algoritmo** con rendimiento: no es un experimento. Para comparar creatividades de forma limpia, usar A/B test o la herramienta de creative testing (reparto similar, sin solapamiento). **[EMPIRICAL]** + **[OFFICIAL META]** ([About A/B testing](https://www.facebook.com/business/help/1738164643098669))

## 9. Regresión a la media

Simulación: 10 anuncios con CPA real distinto (dispersión moderada), elegir el mejor en la semana 1 y medirlo en la semana 2:

| Conv. esperadas/anuncio/semana | Ventaja del mejor en semana 1 | Ventaja en semana 2 |
|---|---|---|
| 15 | 1,47× la media | 1,12× |
| 40 | 1,34× | 1,16× |
| 150 | 1,27× | 1,22× |

Con poca muestra, **la mayor parte de la ventaja observada es suerte**. Aplica igual a: "el ad set que mejor fue ayer", "la edad que mejor convierte este mes", "el día de la semana ganador". **[STRONG INFERENCE]**

## 10. Peeking (mirar y parar antes de tiempo)

Simulación A/A (sin diferencia real), 14 días, test z diario y parada al primer p<0,05:

| Conversiones/día/brazo | Falsos positivos mirando cada día | Mirando solo al final |
|---|---|---|
| 5 | ~20 % | ~5 % |
| 20 | ~22 % | ~5 % |

Soluciones: fijar duración y tamaño **antes** (y respetarlos); usar umbrales secuenciales más estrictos si se mira a menudo; o métodos bayesianos/secuenciales diseñados para monitorización continua. **[STRONG INFERENCE]**; el problema está documentado en la literatura de experimentación online (p. ej., Evan Miller, "How Not To Run an A/B Test", 2010; Kameleoon). **[EMPIRICAL]**

## 11. Reglas prácticas (resumen)

1. **Siempre muestra n** (conversiones) junto al CPA/ROAS.
2. **<30 conversiones** por unidad: no concluyas sobre CPA salvo diferencias enormes (>2×) o problemas obvios (gasto sin una sola conversión con gasto ≥3–5× el CPA objetivo).
3. **Comparar unidades** solo con ≥50–100 conversiones por brazo, en semanas completas, y preferiblemente en experimentos con reparto controlado.
4. **Muchos anuncios**: espera que el "mejor" sea peor de lo que parece; confirma con una segunda ventana.
5. **Decide con duración prefijada**; no pares al primer resultado bonito.
6. **Tasas de funnel**: usa Wilson y ajustes conservadores.
7. **Bandas de control** para el diario; fuera de banda → investigar causas operativas antes que "optimizar".
8. La sobredispersión real hace todo lo anterior **más** estricto, no menos.

Regla rápida de "kill" con cero conversiones: si el CPA objetivo es T y llevas gastado k·T sin conversiones, la probabilidad de 0 conversiones con un CPA real = T es e^(−k): k=2 → 14 %; k=3 → 5 %; k=4 → 1,8 %. Apagar con 3× T sin conversión tiene ~5 % de riesgo de matar algo que estaba en objetivo (sin contar el retraso de atribución). **[STRONG INFERENCE]** (Poisson)

## Implicaciones operativas

- Dimensionar tests y decisiones por número de conversiones, no por días ni por gasto.
- Para creatividades: testear conceptos muy distintos (diferencias grandes, detectables) y validar ganadores en una segunda ventana.
- En reporting, sombrear métricas con n<30 y mostrar IC en las métricas clave.

## Errores frecuentes

1. "Este anuncio tiene CPA 40 $ y el otro 55 $" con 8 y 6 conversiones.
2. Lanzar 20 variantes, quedarse con la mejor y esperar que mantenga su CPA.
3. Revisar el test cada mañana y pararlo al ver "significancia".
4. Ajustar value rules por segmentos con 3–5 ventas.
5. Leer una caída diaria de −35 % con 20 conversiones/día como problema.

## Preguntas abiertas

- Grado típico de sobredispersión en cuentas Meta (depende de la cuenta; medible con la varianza de conversiones diarias vs su media en periodos estables).

## Fuentes clave

- [How winning campaigns are determined in A/B tests](https://www.facebook.com/business/help/166313650471318) — Meta — meta-oficial
- [Create an A/B test by duplicating](https://www.facebook.com/business/help/560857351380163) (≥80 % estimated power, 1–30 días) — Meta — meta-oficial
- [About A/B testing](https://www.facebook.com/business/help/1738164643098669) — Meta — meta-oficial
- [How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html) — Evan Miller, 2010 — academico/practitioner (vigente en lo conceptual)
- [Stopping A/B tests too early](https://www.kameleoon.com/blog/stopping-ab-tests-too-early) — Kameleoon — vendor
- Cálculos propios (python, stdlib): Garwood exacto, Wilson, log-ratio, Monte Carlo (semillas fijas) — 2026-10-16
