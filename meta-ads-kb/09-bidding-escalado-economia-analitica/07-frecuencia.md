# Frecuencia: qué significa una frecuencia alta según contexto

> Última verificación: 2026-10-15 · Autor: A09 (agente) · Ámbito: definición y cálculo, frecuencia como resultado mecánico de presupuesto/CPM/audiencia, retargeting vs prospecting, ventana temporal, ciclo de compra, fatiga creativa (definición oficial), reglas de decisión sin umbrales mágicos.

## TL;DR

- **Frecuencia = impresiones / alcance en el periodo seleccionado; es una métrica estimada y muestreada, basada en "Meta Accounts"/Accounts Center accounts** (perfiles vinculados cuentan como uno; no vinculados, por separado). **[OFFICIAL META]** ([Metrics using Meta Accounts](https://www.facebook.com/business/help/283579896000936))
- **La frecuencia depende de la ventana**: una frecuencia de 6 en 30 días puede ser ~1,4/semana si el alcance se renueva. Compara siempre en la misma ventana (recomendado: 7 días) o como **frecuencia semanal**. **[STRONG INFERENCE]** (aritmética)
- **En audiencias pequeñas la frecuencia es un resultado mecánico**: freq_semana ≈ (presupuesto_semana / CPM × 1.000) / alcance. Con 100 $/día, CPM 30 $ y 20.000 personas alcanzables, la frecuencia semanal no puede bajar de ~1,3–2,3. **[STRONG INFERENCE]**
- **No hay frecuencia "ideal" universal**; los umbrales tipo "frecuencia > 3 = malo" son heurísticas sin base oficial. Meta no publica umbrales de frecuencia para campañas de subasta. **[OFFICIAL META]** (ausencia) + **[EMPIRICAL]** (Loomer: "no ideal frequency"; "frequency is context-dependent")
- **La definición oficial de fatiga es por coste, no por frecuencia**: Meta marca "Creative limited" cuando el coste por resultado supera el de tus anuncios anteriores (<2×) y "Creative fatigue" cuando es ≥2×, considerando exposiciones recientes de esa imagen/vídeo en todas tus campañas. **[OFFICIAL META]** ([Creative fatigue](https://www.facebook.com/business/help/1346816142327858))
- **Señal de fatiga real = frecuencia ↑ + CTR/CVR ↓ + CPA ↑ en la misma creatividad, con el alcance incremental estancado**, no la frecuencia aislada. **[STRONG INFERENCE]**
- **Retargeting y ciclos de compra largos toleran (y a veces necesitan) frecuencias más altas** que la prospección de compra impulsiva; pero el retargeting muy frecuente tiene riesgo de baja incrementalidad (impactas a quien ya iba a comprar). **[STRONG INFERENCE]**
- **En 2026 la fatiga suele aparecer por restricción** (audiencia estrecha, pocas creatividades), no en campañas broad con diversidad creativa (Loomer). **[EMPIRICAL]** ([Master Brief](https://www.jonloomer.com/meta-ads-master-brief/))

---

## 1. Definición y medición

- **Frecuencia** = impresiones / alcance. **Alcance** y métricas "únicas" se basan en *Meta Accounts* (o Accounts Center accounts): son **estimadas y muestreadas**; personas con perfiles no vinculados cuentan varias veces; perfiles falsos pueden afectar. **[OFFICIAL META]**
- La frecuencia **no se suma** entre periodos ni entre ad sets: dos ad sets con frecuencia 2 cada uno sobre la misma audiencia pueden suponer frecuencia ~4 por persona a nivel cuenta. Para frecuencia real por persona, mirar a nivel **campaña/cuenta** con la ventana deseada. **[STRONG INFERENCE]**
- Desde 2024 Meta renombró "people" por "Accounts Center accounts" en definiciones de métricas, sin cambiar el cálculo. **[EMPIRICAL]** ([Loomer](https://www.jonloomer.com/meta-ads-metric-update-accounts-center-account/))

### 1.1 La ventana importa

| Frecuencia reportada | Ventana | Interpretación posible |
|---|---|---|
| 6,0 | 30 días | ~1,4/semana si el alcance se renueva; o 6 impactos a la misma gente si la audiencia está saturada |
| 2,5 | 7 días | 2,5 impactos/semana por persona alcanzada |
| 1,8 | 1 día | Muy alta para prospección; normal en retargeting pequeño |

Para comparar, usa **frecuencia de 7 días** (fijando ventana) y su tendencia semana a semana. **[STRONG INFERENCE]**

### 1.2 Frecuencia como resultado mecánico

```
impresiones_semana ≈ presupuesto_semana / CPM × 1.000
frecuencia_semana  ≈ impresiones_semana / alcance_semana
alcance_semana     ≤ tamaño de audiencia realmente alcanzable
```

Ejemplo retargeting: 20.000 visitantes, 100 $/día, CPM 30 $ → 23.333 impresiones/semana.

| Alcance semanal (% audiencia) | Frecuencia semanal |
|---|---|
| 50 % | 2,33 |
| 70 % | 1,67 |
| 90 % | 1,30 |

Si quieres menos frecuencia en esa audiencia, solo hay tres palancas: menos presupuesto, audiencia más grande o CPM más alto. **La frecuencia "alta" en una audiencia pequeña es una decisión de presupuesto, no un fallo del algoritmo.** **[STRONG INFERENCE]**

Ejemplo prospección: 1.000 $/día, CPM 12 $ en una audiencia broad de 30 M → ~583.000 impresiones/semana → alcanzas ~1,5 % de la audiencia; una frecuencia alta aquí sí indica que el sistema está concentrando en un subconjunto (o que la creatividad solo "abre" un nicho, ver Andromeda en [03](03-escalado-tipos-y-condiciones.md)).

## 2. Qué dice la evidencia sobre frecuencia y rendimiento

| Fuente | Hallazgo | Fiabilidad |
|---|---|---|
| Meta (Help Center) | Fatiga = coste por resultado ≥2× tus anuncios anteriores, considerando exposiciones recientes del asset; recomendaciones: nueva creatividad "materialmente diferente" (sin pausar la original), ampliar audiencia, Advantage+ creative | **[OFFICIAL META]** |
| Meta (Help Center, costs too high) | "If frequency is high, or if the delivery status reads Creative fatigue" → gestionar fatiga | **[OFFICIAL META]** (sin umbral numérico) |
| Loomer (2025-2026) | No hay frecuencia ideal; la frecuencia no es "el villano"; la fatiga es rara hoy salvo audiencias restringidas o pocas variaciones | **[EMPIRICAL]** practitioner |
| Cifra "rendimiento −45 % a frecuencia 4" atribuida a Meta | Citada en podcast de Loomer como dicha por Meta; fuente primaria no localizada | **[UNPROVEN]** |
| Gupta Media (2024, atribuido a Meta) | ~−40 % CTR y ~−60 % conversión hacia la 4.ª exposición repetida | **[UNPROVEN]** (direccional; primaria no localizada) |
| AdEspresso (2018, 500 campañas) | Frecuencia 2: CTR −8,9 %, CPC +50 %; frecuencia 4: CTR −23 %, CPC +68 %; frecuencia 9: CTR −50 %, CPC +161 % | **[OUTDATED]** (pre-Advantage+, pre-Andromeda; útil solo como forma de la curva) |
| Snapchat (103 campañas) | Lift de recuerdo crece fuerte hasta ~2/semana, luego modesto | **[EMPIRICAL]** (otra plataforma, awareness) |
| Heurísticas vendor 2026 | Prospección <2–3/semana; retargeting 3–8/semana | **[HYPOTHESIS]** (sin metodología) |

## 3. Interpretación por contexto

### 3.1 Prospección (broad / Advantage+ audience)

- Frecuencia semanal alta (>2,5–3) con CTR cayendo en el mismo anuncio y CPA subiendo → probable saturación del "pocket" que ese concepto creativo abre. Acción: nuevos **conceptos** (no variaciones), no restringir audiencia.
- Frecuencia alta con CTR y CPA estables → no hay problema; el anuncio sigue siendo relevante para ese público. **[STRONG INFERENCE]**

### 3.2 Retargeting / audiencias pequeñas

- Frecuencia alta es esperable (ver cálculo 1.2). La pregunta no es "¿frecuencia > X?" sino "¿el CPA **incremental** de este retargeting justifica el gasto?". Meta ya gasta 10–40 % (típico 20–25 %) del presupuesto de Sales en remarketing sin pedírselo; un ad set de retargeting separado puede duplicar impactos. **[EMPIRICAL]** (Loomer)
- Regla: si el retargeting separado tiene frecuencia semanal muy alta **y** el % de conversiones de "existing customers/engaged audience" en la campaña principal ya es alto, probar a apagarlo (o holdout) antes de "bajar frecuencia". **[HYPOTHESIS]**

### 3.3 Ciclo de compra

| Ciclo de compra | Frecuencia tolerable | Por qué |
|---|---|---|
| Impulsivo (<1 día, ticket bajo) | Baja; la conversión ocurre en las primeras exposiciones | Exposiciones repetidas a quien no compró tienen poco valor marginal |
| Considerado (días–semanas, ticket medio) | Media | Varias exposiciones con mensajes distintos (prueba social, objeciones, oferta) |
| High-ticket / B2B (semanas–meses) | Alta, con secuencia de mensajes | Se necesita "cobertura" durante el ciclo; la variedad creativa evita fatiga |

**[STRONG INFERENCE]** — principio de marketing coherente con la definición de fatiga de Meta (lo que se fatiga es el **asset**, no la persona: "all recent exposures of the ad's image or video").

### 3.4 Awareness / alcance

- En Reach & Frequency (reservation) hay **frequency caps** explícitos; ahí la frecuencia es una decisión de plan (2+/semana es habitual en planes de marca). **[OFFICIAL META]** (existencia de controles) / **[EMPIRICAL]** (valores típicos).

## 4. Reglas de decisión (en lugar de umbrales mágicos)

1. **Mide por creatividad, en ventanas de 7 días**: frecuencia, CTR (link/outbound), CVR, CPA, alcance incremental.
2. **Fatiga probable** si, en ≥2 semanas consecutivas para el mismo anuncio: frecuencia semanal ↑ **y** CTR ↓ ≥20–30 % vs sus 2 primeras semanas **y** CPA ↑ — o si Meta muestra "Creative fatigue". **[HYPOTHESIS]** (los % son orientativos) + **[OFFICIAL META]** (estado).
3. **No es fatiga** si la frecuencia sube pero CTR/CPA se mantienen; o si el CPA sube en toda la cuenta a la vez (mercado/estacionalidad, ver [05](05-cpm-que-lo-determina.md)/[06](06-estacionalidad.md)).
4. **Acción ante fatiga** (orden oficial): crear un anuncio **materialmente diferente** manteniendo el original activo; ampliar audiencia; Advantage+ creative. **[OFFICIAL META]**
5. **Retargeting**: decidir por incrementalidad (holdout), no por frecuencia.

## Implicaciones operativas

- Dashboard creativo con frecuencia 7d y CTR/CPA por anuncio (ver [10](10-dashboards-reporting.md)).
- Pipeline creativo dimensionado para que ningún concepto cargue con >50–70 % del gasto durante semanas sin sustitutos.
- Antes de recortar por frecuencia, calcular la frecuencia "mecánica" esperada por presupuesto/audiencia.

## Errores frecuentes

1. Aplicar "frecuencia > 3 = apagar" a retargeting de 10.000 personas.
2. Comparar frecuencias de ventanas distintas (30d vs 7d).
3. Sumar frecuencias de ad sets que comparten audiencia.
4. Restringir la audiencia "para bajar frecuencia" (la sube).
5. Pausar un anuncio con frecuencia alta y CPA estable.
6. Responder a la fatiga con variaciones mínimas del mismo concepto.

## Preguntas abiertas

- Fuente primaria de Meta para "−45 % a frecuencia 4" / "−40 % CTR, −60 % conversión a la 4.ª exposición": no localizada.
- Curvas frecuencia-respuesta post-Andromeda publicadas con metodología: no encontradas.

## Fuentes clave

- [About creative fatigue recommendations](https://www.facebook.com/business/help/1346816142327858) — Meta — meta-oficial
- [Metrics and estimates using Meta Accounts](https://www.facebook.com/business/help/283579896000936) — Meta — meta-oficial
- [Troubleshoot: costs too high](https://www.facebook.com/business/help/2727273724224874) — Meta — meta-oficial
- [The Master Brief](https://www.jonloomer.com/meta-ads-master-brief/) — Jon Loomer, 2026-07 — practitioner
- [Meta Ads metric update: Accounts Center account](https://www.jonloomer.com/meta-ads-metric-update-accounts-center-account/) — Jon Loomer — practitioner
- [Motion Creative Benchmarks 2026 (resumen)](https://sepia-lab.com/en/blog/ad-creative-volume-benchmarks) — Sepia Lab — vendor (incluye cifras AdEspresso 2018 y Gupta 2024)
- [Snapchat optimal ad frequency report](https://www.socialmediatoday.com/news/snapchat-publishes-new-report-on-optimal-ad-frequency-to-drive-recall-and-a/554878) — Social Media Today — prensa
