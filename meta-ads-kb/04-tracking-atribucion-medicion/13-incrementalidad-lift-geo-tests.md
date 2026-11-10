# Incrementalidad: Conversion Lift, Brand Lift, holdouts, geo tests e incremental attribution

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: cómo saber qué ventas *causó* Meta frente a las que *reclamó*; diseño de experimentos, herramientas de Meta y de terceros, evidencia publicada sobre incrementalidad de Meta, retargeting y view-through.

## TL;DR

- **Atribución ≠ causalidad.** La atribución asigna crédito a quien estuvo cerca de la conversión; la incrementalidad compara con un contrafactual (grupo de control que no vio anuncios). Métodos observacionales sofisticados fallan: en 663 experimentos de Facebook, DML y *propensity score matching* tuvieron errores absolutos medianos del 115 %, 107 % y 62 % del lift (embudo alto/medio/bajo) frente a lifts reales medianos de 28 %, 19 % y 6 %. [EMPIRICAL — académico] ([S04-078])
- **Pero el last-click no es inútil para predecir incrementalidad, solo es pobre:** con 2.226 RCTs de Meta, un modelo PIE predice incrementalidad por dólar con R² 0,88 fuera de muestra frente a 0,19 del last-click 7 días. Es la base conceptual de herramientas como *incremental attribution*. [EMPIRICAL — académico] ([S04-077])
- **Evidencia agregada más grande disponible (Haus, 640 experimentos, 2024–2025):** Meta generó de media **+19 % de lift** en el KPI principal; 96 % de los estudios a nivel cuenta detectaron lift significativo a mitad de test; con atribución 7d click Meta **infra-reporta** su incrementalidad un 15 % de media (DTC); en marcas omnicanal (≥ 25 % del negocio fuera de DTC) ~32 % del impacto cae fuera de DTC (Amazon, retail). [EMPIRICAL] ([S04-021], [S04-024])
- **Herramientas de Meta:** Conversion Lift (holdout aleatorio a nivel de *Accounts Center account*; vía Experiments; acceso por API "currently limited"), Brand Lift (encuestas; self-serve en Experiments desde finales de 2023), A/B tests (comparan estrategias, no incrementalidad absoluta), Incremental attribution (modelo, no experimento), GeoLift (open source, control sintético aumentado). [OFFICIAL META] ([S04-064], [S04-029]) + [EMPIRICAL] (Brand Lift self-serve, Jon Loomer)
- **Geo tests** son la vía independiente de la plataforma: GeoLift (Meta, R, ASCM), Haus, Recast, Measured, etc. Requieren series diarias estables por región, análisis de potencia previo y al menos un ciclo de compra de duración. Ojo: desde el **22-jun-2026** el breakdown `dma` de Nielsen desaparece en la API y se sustituye por `comscore_market`. [OFFICIAL META] ([S04-049]) + [OFFICIAL META open source] (GeoLift docs, [S04-104])
- **Retargeting y view-through** son donde la atribución más sobre-reclama; las cifras concretas que circulan ("retargeting 40–70 % menos incremental", "28 % de incrementalidad mediana") son de fuentes secundarias no verificadas. Lo defendible: Haus encontró que campañas de mitad/alto embudo **infra-reportan** su lift y que Advantage+ sobre-reportó ~12 pp frente a manual. [EMPIRICAL] ([S04-021]) + [HYPOTHESIS] (cifras de retargeting)
- **Regla de decisión:** usar atribución de plataforma para optimización táctica *dentro* de Meta; usar experimentos para fijar el *incrementality factor* (incrementales ÷ reportadas) por tipo de campaña y recalibrar trimestralmente; usar MMM calibrado con esos experimentos para el presupuesto total (archivo 14). [STRONG INFERENCE]

## 1. Conceptos

| Concepto | Definición operativa |
|---|---|
| Lift | (conversiones test − conversiones control escaladas) ÷ conversiones control escaladas |
| Conversiones incrementales | test − control (escalado al tamaño del test) |
| iROAS / iCPA | Ingresos incrementales ÷ gasto; gasto ÷ conversiones incrementales |
| Incrementality factor (IF) | Conversiones incrementales ÷ conversiones reportadas por la plataforma (IF < 1: la plataforma sobre-reclama) [EMPIRICAL] (definición Haus/Recast) |
| MDE | Efecto mínimo detectable con la potencia y significación elegidas |
| Intención de tratar (ITT) vs *ghost ads* | ITT compara grupos asignados (diluido por quien no llegó a ver anuncios); *ghost ads*/opportunity logging registra en control a quien *habría* visto el anuncio, mejorando precisión [EMPIRICAL — académico] ([S04-105]) |

**Por qué los experimentos de anuncios son caros:** en 25 grandes experimentos con retailers, el intervalo de confianza mediano del ROI superó los 100 puntos porcentuales (Lewis & Rao, 2015): las ventas son muy ruidosas frente al efecto de la publicidad. Consecuencia: potencia y duración importan más que la intuición. [EMPIRICAL — académico] ([S04-106])

## 2. Conversion Lift (Meta)

- **Diseño:** Meta aleatoriza personas (Accounts Center accounts) en test y control; el control no ve los anuncios del estudio; Meta compara conversiones (Pixel/CAPI/app events) entre grupos, incluidas personas convertidas e ingresos. Admite multi-celda (varias estrategias, cada una con su holdout). [OFFICIAL META] ([S04-064])
- **Ventana de observación post-test:** entre `end_time` y `observation_end_time` los anuncios se entregan normalmente a ambos grupos pero no se "registran" nuevos usuarios, y Meta sigue emparejando conversiones de los ya asignados (captura efecto retardado). [OFFICIAL META] ([S04-064])
- **Restricciones:** una vez iniciado, no se puede cambiar `start_time` ni `treatment_percentage` ni quitar entidades del test. [OFFICIAL META] ([S04-064])
- **Acceso:** por API, "Conversion Lift Measurement is currently limited. Please contact your Meta Representative"; en Ads Manager > Experiments puede estar disponible self-serve según cuenta. Requisitos de gasto/volumen publicados por terceros (p. ej. "≈30.000 $/mes", "500 conversiones") **no verificados**. [OFFICIAL META] (API) + [CONTESTED] (self-serve y mínimos)
- **2026:** el MCP server oficial de Meta expone herramientas para crear y leer lift studies y comprobar elegibilidad de A/B tests (señal de que Meta quiere facilitar la experimentación). [OFFICIAL META] ([S04-066])
- **Dependencia de la señal:** el lift se mide con los eventos que recibe Meta; si el tracking pierde conversiones de forma correlacionada con la exposición (p. ej. ad blockers), el lift se sesga. Mide también con datos de backend cuando sea posible. [EMPIRICAL] (TrackBee, vendor) + [STRONG INFERENCE]

## 3. Brand Lift

- Encuestas a grupos test/control sobre recuerdo, notoriedad, consideración, intención. Self-serve en Experiments desde finales de 2023 (antes requería representante). Presupuestos mínimos por país citados por terceros (15.000–30.000 $) no verificados. [EMPIRICAL] (Jon Loomer, LinkedIn dic-2023) + [HYPOTHESIS] (mínimos)
- Útil para campañas de alcance/vídeo donde la conversión directa es baja; no sustituye a Conversion Lift.

## 4. Geo tests

### 4.1 Cuándo
- Cuando no hay acceso a Conversion Lift, cuando quieres medir **todo el negocio** (incluido Amazon/retail/offline) o comparar canales con la misma vara.

### 4.2 GeoLift (Meta open source)
- **Método:** Augmented Synthetic Control (ASCM) con opción Ridge o Generalized Synthetic Control ("best"); efectos fijos por defecto; α = 0,1 por defecto. [OFFICIAL META open source] ([S04-104])
- **Datos:** ubicación, fecha, KPI (diario en el ejemplo); sin huecos; series con patrones parecidos entre regiones. El ejemplo usa 40 ubicaciones, 90 días de pre-periodo y 15 días de test. [OFFICIAL META open source] ([S04-104])
- **Selección de mercados y potencia:** `GeoLiftMarketSelection()` evalúa combinaciones (duración, nº de mercados) por potencia, desequilibrio escalado y sesgo; `GeoLiftPower()` estima MDE e inversión usando un CPIC (coste por conversión incremental) de MMM/lift previos. Regla: duración ≥ un ciclo de compra completo. [OFFICIAL META open source] ([S04-104])
- **Estado del proyecto:** sin releases desde v2.6.06 (may-2023); actividad reciente solo de mantenimiento (dependabot) en 2026. Usable, pero sin evolución. [OFFICIAL META] ([S04-029])

### 4.3 Diseño correcto (checklist)
1. Pregunta única (p. ej. "¿cuál es el iROAS de prospecting en Meta?").
2. KPI de negocio (ventas backend por región, no conversiones de Meta).
3. Unidad geográfica coherente con la segmentación de Meta (en EE. UU., **Comscore Markets** desde 2025–2026; en España, provincias/CCAA o códigos postales agregados).
4. Pre-periodo ≥ varias veces la duración del test con datos limpios (sin cambios de precio o stock dispares entre regiones).
5. Análisis de potencia: MDE realista (los lifts de Meta suelen ser de un dígito a decenas de %; Haus: media 19 % a nivel cuenta).
6. Diseño *go-dark* (apagar en regiones de control) o *heavy-up* (aumentar en regiones test) según riesgo.
7. Congelar cambios en otras palancas durante el test; registrar incidencias.
8. Ventana post-test (Haus: media 8,8 días) para capturar efectos retardados. [EMPIRICAL] ([S04-021])
9. Pre-registrar criterio de decisión (umbral de iROAS).

## 5. Holdouts propios (pre-post, audiencias)

- **Holdout de audiencia** (excluir un % aleatorio de un CRM de retargeting) es válido si la exclusión es aleatoria y se mide en backend.
- **Pre-post (encender/apagar en todo el país)** es el diseño más débil: confunde estacionalidad y otras palancas. Úsalo solo como indicio. [STRONG INFERENCE]

Haus (may-2026) recomienda revalidar la incrementalidad tras los cambios de atribución de Meta, porque "afectan a la señal que usa el algoritmo", y testear IA con lift tests en lugar de adoptarla o descartarla por defecto. [EMPIRICAL] ([S04-023])

## 6. Incremental attribution (recordatorio)

Modelo de Meta que estima qué conversiones fueron causadas por el anuncio y puede usarse para optimizar o solo reportar. En pruebas independientes (Haus) pasó de 0,80× iROAS vs standard (jul-24/jun-25) a **1,26×** (jul-25/jun-26), más en DTC (1,38×) que omnicanal (1,02×). No sustituye a un experimento propio; puede ser el primer paso cuando no hay acceso a lift. Ver archivo 10. [EMPIRICAL] ([S04-022])

## 7. Lo que dice la evidencia sobre Meta

| Hallazgo | Fuente | Evidencia |
|---|---|---|
| Lift medio +19 % en KPI principal; récord 74 % | Haus 2025 (640 tests) | [EMPIRICAL] ([S04-021]) |
| 7d click infra-reporta incrementalidad un 15 % (DTC): por cada 100 $ atribuidos, ~115 $ incrementales | Haus 2025 | [EMPIRICAL] ([S04-024]) |
| Advantage+ vs manual: 58 % de marcas con mayor iROAS en manual; A+ −12 % iROAS con −18 % gasto diario; A+ sobre-reporta ~12 pp | Haus 2025 | [EMPIRICAL] ([S04-021]) — contrastar con área 02/12 |
| Campañas mid/upper-funnel: menor iROAS DTC pero más halo omnicanal y nuevos clientes; factor de incrementalidad (incremental ÷ reportado) relativo al bajo embudo: mid 1,3×, tráfico 2,4×, alcance 6,0× (es decir, Meta infra-reporta más cuanto más arriba en el embudo) | Haus 2025 | [EMPIRICAL] ([S04-021]) |
| Métodos observacionales no recuperan el efecto causal | Gordon et al. 2019 y 2023 | [EMPIRICAL — académico] ([S04-107], [S04-078]) |
| Retargeting "40–70 % menos incremental de lo reportado" | Blogs que citan a Haus/Measured | [HYPOTHESIS] (no localizado en fuente primaria) |

**Lectura para view-through:** las impresiones sí pueden ser incrementales (Meta es un medio de vídeo/feed), pero el view-through de 1 día sobre audiencias que ya iban a comprar (clientes, carritos) es la parte más propensa a sobre-reclamar. Decídelo con experimentos por tipo de audiencia, no con dogmas. [STRONG INFERENCE]

## 8. Alternativas a Meta para medir

| Herramienta | Tipo | Notas |
|---|---|---|
| Haus | Geo experiments (control sintético) + causal MMM | Publicaciones con meta-análisis de Meta (2025–2026) [EMPIRICAL — vendor] |
| Recast | MMM bayesiano + "incrementality factor" | Plantillas de informes ajustados por incrementalidad [EMPIRICAL — vendor] |
| Measured | Experimentos geo/audiencia + MMM | [HYPOTHESIS] (no verificado en esta investigación) |
| GeoLift | Open source (R) | Ver 4.2 |
| Google Meridian + GeoX | MMM open source calibrable con experimentos | Meridian 2.0 añadió calibración de priors con experimentos tipo GeoX [OFFICIAL Google] ([S04-026]) |

## Implicaciones operativas

- **Hacemos:** al menos un experimento de incrementalidad por trimestre para cuentas con gasto significativo; IF por tipo de campaña (prospecting, retargeting, A+, mid-funnel); decisiones de presupuesto basadas en iROAS; registrar diseño y resultados en un repositorio.
- **Evitamos:** "validar" Meta comparando con GA4; pre-post como prueba concluyente; tests sin análisis de potencia; leer un lift no significativo como "Meta no funciona" (puede ser falta de potencia).
- **Umbrales:** si IF < 0,5 en retargeting → recortar o rediseñar; si iROAS de prospecting ≥ objetivo → escalar con MMM como freno de saturación.

## Errores frecuentes

1. Usar conversiones de Meta como KPI del geo test (circular).
2. Tests de 7 días en negocios con ciclo de 21.
3. Contaminación: campañas de otros equipos llegando a regiones de control.
4. Cambiar presupuesto/creatividades a mitad de test.
5. Ignorar el efecto omnicanal (Amazon/retail) en marcas que venden fuera de su web.

## Preguntas abiertas

- Requisitos actuales (2026) de Conversion Lift self-serve en Ads Manager.
- Metodología exacta de Incremental attribution.
- Equivalencias de Comscore Markets para geo tests en EE. UU. y su impacto en tests históricos basados en DMA.

## Fuentes clave

- [Haus: The Meta Report (640 experimentos)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor (S04-021)
- [Haus: Is Meta Incremental?](https://www.haus.io/blog/is-meta-incremental) — 2025-08-13 — vendor (S04-024)
- [Haus: IA vs standard](https://www.haus.io/blog/is-metas-incremental-attribution-outperforming-standard-attribution-what-the-data-shows) — 2026-07-16 — vendor (S04-022)
- [Lift Study (Marketing API)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/guides/lift-studies) — vigente — meta-developers (S04-064)
- [GeoLift walkthrough](https://facebookincubator.github.io/GeoLift/docs/GettingStarted/Walkthrough/) — vigente — meta-oficial (S04-104)
- [Close Enough? (Marketing Science 2023)](https://pubsonline.informs.org/doi/10.1287/mksc.2022.1413) — 2023 — academico (S04-078)
- [PIE for Ad Measurement](https://pubsonline.informs.org/doi/10.1287/mnsc.2023.01108) — 2023–2026 — academico (S04-077)
- [A Comparison of Approaches to Advertising Measurement (Facebook)](https://www.kellogg.northwestern.edu/faculty/gordon_b/files/fb_comparison.pdf) — 2019 — academico (S04-107)
- [Ghost Ads (JMR 2017)](https://www.kellogg.northwestern.edu/faculty/research/detail/2017/ghost-ads-improving-the-economics-of-measuring-online-ad) — 2017 — academico (S04-105)
- [The Unfavorable Economics of Measuring the Returns to Advertising (QJE 2015)](https://doi.org/10.1093/qje/qjv023) — 2015 — academico (S04-106)
- [2026 Out-of-cycle changes (DMA → Comscore)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/out-of-cycle-changes/occ-2026) — 2026 — meta-developers (S04-049)

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Fila de Haus sobre mid/upper funnel: decía "ratios plataforma/incremental", lo que invierte el sentido. Haus define el incrementality factor como ventas incrementales ÷ ventas reportadas y los 1,3×/2,4×/6,0× son ese factor relativo al de bajo embudo (ejemplo de Haus: 100 $ reportados en alcance ≈ 600 $ incrementales). Verificado en el post de Haus (2025-07-28) el 2026-10-16.
