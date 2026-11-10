# Fatiga creativa: fatiga real frente a varianza, saturación de audiencia y decay

> Última verificación: 2026-10-15 · Autor: A03 (agente) · Ámbito: cómo distinguir la fatiga de otras causas de caída, qué métricas la detectan, qué hacer. Los aspectos de subasta y estacionalidad los cubren las áreas 01 y 09.

## TL;DR

- **La mayoría de creatividades no se fatigan: nunca llegan a escalar.** Interconnections (368 creatividades, 15 cuentas DTC, abr–ago 2026): el 80% nunca alcanza 100.000 impresiones, y el top 10% se lleva el 68% del gasto. El problema principal suele ser el hit rate, no la vida útil. **[EMPIRICAL]** (S03-039)
- **La fatiga real existe pero es más suave de lo que se cree:** medida por impresiones acumuladas, el CTR cae ~5,5% al pasar de las primeras 100k a 100–250k impresiones y luego se estabiliza, mientras el CPA sube +8,8% (100–250k), +17,8% (250–500k) y +19,6% (500k–1M). **El CPM no sube con la edad del creativo**, así que una subida de CPM apunta a subasta, audiencia o temporada, no a fatiga. **[EMPIRICAL]** (S03-039)
- **Meta tiene estados oficiales en la columna Delivery:** *Creative limited* (coste por resultado mayor que en anuncios anteriores pero menos del doble) y *Creative fatigue* (≥2x). Son relativos a tu historial, aparecen sobre todo en ad sets de un solo creativo y en catálogo, y llegan tarde. Hay también una predicción de fatiga antes del lanzamiento para ad sets de un solo creativo. **[OFFICIAL META]** vía múltiples fuentes secundarias concordantes (S03-004, S03-041)
- **Los umbrales de frecuencia "2,5–3" no tienen un origen verificable.** Interconnections no encontró su fuente y los califica de "folklore". La frecuencia es un indicador útil solo junto con la tendencia del CPA y del CTR, y su nivel "correcto" depende del tamaño de la audiencia, del ciclo de compra y del objetivo. **[CONTESTED]** (S03-039)
- **Antes de llamar "fatiga" a una caída hay que descartar:** cambios de la cuenta entera (tracking, atribución, web, stock, precio), estacionalidad y subasta (CPM de toda la cuenta), cambios de presupuesto/estructura y ruido estadístico (pocas conversiones). La fatiga es un fenómeno **de un anuncio o concepto concreto**, no de la cuenta. **[STRONG INFERENCE]**
- **La similitud acelera la fatiga:** Meta dice que los creativos demasiado parecidos se muestran a las mismas audiencias y pueden acabar en "Creative limited/fatigue". Diez variaciones del mismo concepto equivalen, a efectos de saturación, casi a un solo concepto. **[OFFICIAL META]** (S03-004)
- **El remedio depende de la causa:** si el concepto está fatigado, iterar hooks o formatos (lavado de cara); si lo está el bolsillo de audiencia (el ángulo agotó su segmento), hace falta un ángulo o persona nueva; si es la oferta, cambiar la oferta. Refrescar el hook no arregla un ángulo saturado. **[STRONG INFERENCE]**
- **No apagar ganadores "por calendario".** Un creativo que se estabiliza en un CPA aceptable debe seguir funcionando (Interconnections: tras la caída inicial del CTR, el rendimiento se aplana). Disparador recomendado: CPA del anuncio frente a objetivo y tendencia por cohortes, no días en antena ni frecuencia sola. **[EMPIRICAL]** (S03-039)

## 1. Definiciones

| Término | Definición operativa | Cómo se ve |
|---|---|---|
| **Fatiga creativa (wear-out)** | Pérdida de eficacia de un creativo concreto por exposición repetida de las mismas personas a él. Atria la define como "the decline in ad performance that occurs when the same audience is repeatedly exposed to the same creative elements" (S03-041) | El CTR y el hook rate del anuncio bajan y su CPA sube **mientras** el resto de anuncios de la cuenta se mantienen; la frecuencia del anuncio sube |
| **Saturación de audiencia / bolsillo** | El segmento al que llega un ángulo se agota: quien iba a comprar con ese mensaje ya lo hizo o ya lo ha visto | Todas las variantes del mismo ángulo suben de CPA a la vez; los nuevos hooks del mismo ángulo nacen "cansados"; breakdowns sin segmentos nuevos |
| **Decay natural / regresión a la media** | El anuncio "ganó" en parte por suerte (pocas conversiones) y vuelve a su nivel real | CPA espectacular inicial con <20 conversiones que se normaliza |
| **Varianza** | Fluctuación aleatoria (Poisson) día a día | Oscilaciones sin tendencia; desaparece al agregar 7–14 días |
| **Deterioro de la cuenta / mercado** | Cambio externo: CPM de subasta, estacionalidad, competidores, tracking, landing, precio, stock | Todos los anuncios empeoran a la vez; el CPM de la cuenta sube; CVR de la web cae |
| **Fatiga de oferta** | El mercado ya ha visto la promoción o el precio; la urgencia se pierde | Todos los creativos con esa oferta caen; mejora al cambiar condiciones |

## 2. Estados oficiales de Meta

- **Creative limited**: el coste por resultado es mayor que el de anuncios anteriores, pero menos del doble.
- **Creative fatigue**: coste por resultado ≥2x el de anuncios anteriores.
- Se muestran en la columna **Delivery** del ad set o del anuncio. Son relativos al historial de la cuenta, de modo que una cuenta o un evento de optimización nuevo no tienen baseline. Aparecen sobre todo en **ad sets de un solo creativo y en catálogo**, y no conviene actuar si salen en las primeras 48 h de un anuncio nuevo (todavía en arranque).
- **Predicción previa al lanzamiento**: Meta avisa si prevé fatiga en los primeros 7 días; solo aplica a ad sets de un solo creativo (excluye catálogo, dynamic creative y Advantage+ app).
- **Columna Creative diversity** (ago-2026): mide la similitud visual dentro del ad set (ver 01). No es una métrica de fatiga, pero una diversidad baja anticipa saturación.
- **Verificado en el Help Center el 2026-10-16** ("About creative fatigue recommendations in Meta Ads Manager", S03-115): los umbrales son exactamente esos (más caro que tus anuncios anteriores pero menos del doble → *Creative limited*; ≥2x → *Creative fatigue*). Además, Meta dice que **considera "all recent exposures of the ad's image or video, including those from other campaigns from your Page"**, de modo que el mismo asset en otra campaña también suma fatiga. Recomienda crear un anuncio nuevo "materially different from the original" y señala que **mantener activo el original "may maximize results"** frente a pausarlo. La función solo existe en ad sets de un solo creativo (excluye catálogo, dynamic creative y Advantage+ app) y no está disponible en Ventas antes de que el ad set esté activo. **[OFFICIAL META]**
- Fuentes previas: Meta (página creative differentiation, S03-004) y guías de 2026 que reproducían el Help Center (S03-041).

**Valoración:** son útiles como alarma, pero **tardías** (cuando el CPA se ha duplicado ya se ha perdido dinero) y poco informativas en ad sets con muchos anuncios. No sustituyen al análisis por cohortes.

## 3. Qué dicen los datos sobre la curva de fatiga

| Fuente | Muestra | Hallazgos clave |
|---|---|---|
| Interconnections (ago-2026) (S03-039) | 368 creatividades, 15 cuentas DTC, 48M impresiones; curvas en 57 creatividades con ≥150k impresiones | Mediana: 18 días y 10.665 impresiones; p90: 76 días / 294k. CTR −5,5% (100–250k) y luego estable; CPA +8,8% → +17,8% → +19,6%; CPM +3,1% como máximo (no sube con la edad); CTR de los 3 primeros días **sin** valor predictivo (el tercio con mejor CTR temprano tuvo *menos* impresiones de vida que el peor tercio) |
| Skaler (abr-2026) (S03-040) | 2,9M anuncios inactivos (ene-2025 a abr-2026) | Mediana de días activos: 3 (p75: 8). Anuncios con ≥500k impresiones UE: mediana 17 días, p90 101. Sesgo: solo anuncios ya inactivos |
| Motion (2026) (S03-010) | 578k creatividades | Solo ~5–8% llegan a "winner"; ~50% son losers (apagados o sin gasto antes de 28 días) |
| AdEspresso (2018), vía secundaria (S03-011) | 500 campañas | Con frecuencia 2: CTR −8,9%, CPC +49,8%; frecuencia 4: CTR −23%, CPC +68%; frecuencia 9: CTR −50%, CPC +161%. **[OUTDATED]** como cifra (2018, otra subasta), vigente como dirección |
| Brainlabs (S03-047) | 46 brand lift studies | Mejor recall con 2 exposiciones cada 7 días (branding) |

**Lectura [STRONG INFERENCE]:**
1. La fatiga de un ganador es **gradual** (decenas de % en CPA a lo largo de cientos de miles de impresiones), no un precipicio. Los "precipicios" suelen ser causas externas o el agotamiento del bolsillo.
2. Que el CPM no suba con la edad del creativo contradice la creencia de que "Meta encarece los anuncios viejos". Si sube el CPM, hay que mirar subasta, temporada o audiencia.
3. Las métricas tempranas de atención no predicen la longevidad: no conviene decidir el futuro de un concepto por su CTR de 3 días.

## 4. Diagnóstico: ¿fatiga real o otra cosa?

### 4.1 Árbol de decisión

1. **¿Empeora toda la cuenta o solo algunos anuncios?**
   - Toda la cuenta (la mayoría de anuncios a la vez, también los nuevos) → **no es fatiga creativa**. Revisar tracking/atribución (cambios de mar-2026, área 04), web/CVR, precio/stock, estacionalidad, CPM de mercado, cambios de estructura o presupuesto.
   - Solo anuncios concretos → seguir.
2. **¿Hay volumen suficiente para afirmar que ha empeorado?** Con <20 conversiones por periodo, una diferencia del 30% es ruido probable (05, sección 4). Se agregan 7–14 días.
3. **¿Cómo se mueven las métricas del anuncio a lo largo de su vida (por impresiones acumuladas)?**
   - Frecuencia ↑, CTR/hook rate ↓, CPA ↑, CPM estable → **fatiga del creativo** probable.
   - CTR y hook rate estables, CVR ↓ → problema **post-clic** (landing, oferta, stock, tracking) o de calidad de tráfico.
   - CPM ↑ en todos los anuncios → **subasta/temporada**.
4. **¿Las variantes del mismo concepto o ángulo también caen?**
   - Solo la pieza concreta → fatiga del **creativo** → iterar hook o formato.
   - Todas las del ángulo, incluidas las nuevas → **saturación del bolsillo** → ángulo o persona nueva.
   - Todas las de la oferta → **fatiga de oferta**.
5. **Test de confirmación (Atria):** sustituir por una variante fresca del mismo concepto. Si se recupera en 3–5 días, era fatiga del creativo. Si no, era otra cosa. **[EMPIRICAL]** (S03-041)

### 4.2 Métricas y su uso

| Métrica | Uso en fatiga | Trampa |
|---|---|---|
| Frecuencia (impresiones/alcance) del anuncio y del ad set | Contexto: subida sostenida + caída de CTR = desgaste | Sin umbral universal; en retargeting o audiencias pequeñas, alta por diseño; la frecuencia de 7 días es más informativa que la de toda la vida del anuncio |
| CTR (link/outbound) e hook rate por cohorte de impresiones | Primera señal de desgaste del creativo | Varía por placement; cambios de mix de placement pueden simular caídas |
| CPA/CVR del anuncio | Disparador de decisión | Ruido con poco volumen; efectos de atribución |
| CPM del anuncio frente al de la cuenta | Separar subasta de creativo | Interconnections: no sube con la edad del creativo |
| Proporción de "nuevo alcance" (alcance incremental / impresiones) | Saturación | Requiere exportar alcance diario |
| Comentarios negativos / "ocultar anuncio" | Señal cualitativa de rechazo | Los comentarios acumulados en un post viejo pueden ser activo o lastre (12) |
| Columna Creative diversity | Riesgo de saturación por similitud | "En desarrollo"; no es fatiga |

### 4.3 Análisis por cohortes (recomendado)

- **Cohorte por fecha de lanzamiento** (semana o mes): CPA, CTR, gasto y % de gasto de cada cohorte a lo largo del tiempo. Si las cohortes nuevas rinden peor que las viejas a la misma edad, hay un problema de calidad del pipeline creativo, no de fatiga.
- **Curva por impresiones acumuladas** de cada ganador (índice frente a sus primeras 100k impresiones, como hace Interconnections). Permite predecir cuándo cruzará el CPA límite.
- **Share of spend de anuncios con <30 días**: si cae de forma sostenida, la cuenta depende de incumbentes envejecidos (riesgo).

## 5. Qué hacer

| Diagnóstico | Acción | Evitar |
|---|---|---|
| Fatiga de un creativo ganador (CPA sube gradualmente, CTR baja, frecuencia sube) | Iteraciones: nuevos hooks visuales y de texto, nuevo talento, nuevo formato del mismo mensaje; mantener el original mientras su CPA ≤ objetivo | Apagarlo antes de tener sustituto; "refrescar" solo el color |
| Saturación del bolsillo (todas las variantes del ángulo caen) | Nuevos ángulos y personas; ampliar geo/idioma; revisar exclusiones (área 02) | Más hooks del mismo ángulo |
| Fatiga de oferta | Cambiar la estructura de la oferta (bundle, garantía, regalo, trial) en vez de profundizar el descuento | Escalada de descuentos |
| Similitud alta (Creative diversity "Low", gasto concentrado) | Introducir conceptos distintos en el ad set | Pausar ganadores para subir el score |
| Subasta/temporada | Ajustar expectativas y presupuesto (área 09) | Rehacer todos los creativos |
| Post-clic | Landing, oferta, tracking (09, área 04) | Culpar al creativo |
| Retargeting con frecuencia alta | Rotación de mensajes por etapa (prueba, objeciones, oferta); limitar ventana y presupuesto | Un único anuncio de descuento para siempre |

**Cadencias orientativas (EMPIRICAL, de practicantes):** respuesta directa: introducir creativos nuevos cada 1–2 semanas; branding: cada 3–4 semanas; retargeting de audiencias pequeñas: más a menudo (Atria, S03-041). Meta: anuncios nuevos cada semana (S03-003). Ojo, es la cadencia de **introducción** de creativos, no de **apagado** de ganadores.

## Implicaciones operativas

- **Disparadores de refresh** basados en el CPA del anuncio frente al objetivo con tendencia (p. ej., 7 días móviles por encima de 1,2–1,3x el objetivo con ≥20 conversiones) **y** en la curva de su cohorte, no en días ni en frecuencia sola. **[HYPOTHESIS]** como umbral concreto; **[EMPIRICAL]** el principio (S03-039).
- **Pipeline siempre por delante**: tener sustitutos *antes* de que los ganadores caigan (The Performers: "replacements must come before winners die", S03-024).
- **Diversificar para retrasar la saturación**: varios ángulos activos llegan a bolsillos distintos.
- **Seguimiento semanal**: % del gasto en anuncios <30 días; nº de ganadores confirmados; curva de los top 5 anuncios.

## Errores frecuentes

- Apagar un ganador porque "lleva 3 semanas" o porque la frecuencia pasó de 3.
- Llamar fatiga a una caída de toda la cuenta (tracking, web, temporada).
- Responder a la saturación de un ángulo con más hooks del mismo ángulo.
- Reaccionar a 2–3 días malos de un anuncio con pocas conversiones (varianza).
- Confiar en "Creative fatigue" de Meta como alarma temprana (llega cuando el CPA ya se ha duplicado).
- Relanzar el mismo creativo con un ID nuevo esperando que "se resetee": las personas son las mismas (y se pierde la prueba social del post).

## Preguntas abiertas

- ¿Influye la columna Creative diversity en la entrega o en la fatiga? Sin datos.
- No hay datos públicos recientes y rigurosos de la relación frecuencia-respuesta en la subasta de 2026. Los de AdEspresso son de 2018.
- Diferencias de fatiga entre estático y vídeo: Interconnections no tenía muestra suficiente de vídeo para publicarlas.

## Fuentes clave

- [Interconnections — The Meta Creative Fatigue Benchmark](https://www.theinterconnections.com/benchmarks/meta-creative-fatigue) — 2026-08 — agencia (dataset)
- [Meta for Business — Creative differentiation](https://www.facebook.com/business/m/small-business/creative-differentiation) — vigente 2026 — meta-oficial
- [Atria — Meta creative fatigue: diagnose and fix (2026)](https://www.tryatria.com/blog/meta-creative-fatigue-diagnose-and-fix-2026) — 2026-06-03 — vendor
- [Skaler — Creative fatigue in 2026](https://skaler.app/blog/creative-fatigue-meta-ads-2026) — 2026-04-29 — vendor (dataset)
- [Motion — Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — 2026 — vendor (dataset)
- [Brainlabs — 46 Meta brand lift studies](https://www.brainlabsdigital.com/meta-brand-lift-studies-objectives-creatives-results/) — s.f. — agencia
- [Sepia Lab — resumen Motion + AdEspresso 2018](https://sepia-lab.com/en/blog/ad-creative-volume-benchmarks) — 2026 — vendor (secundario)
