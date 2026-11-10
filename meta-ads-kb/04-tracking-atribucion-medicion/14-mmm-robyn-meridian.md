# Marketing Mix Modeling (MMM): cuándo importa, Robyn, Meridian, PyMC-Marketing y triangulación

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: MMM aplicado a decisiones de inversión en Meta; estado de las herramientas open source verificado contra GitHub/CRAN/PyPI el 2026-10-15/16; requisitos de datos; combinación MMM + experimentos + atribución.

## TL;DR

- **MMM responde "¿cuánto aporta cada canal al negocio total y dónde está la saturación?"** usando series temporales agregadas (sin cookies ni IDs). Es la herramienta adecuada para presupuesto entre canales y para marcas con ventas fuera de la web; **no** sirve para optimizar ad sets o creatividades. [STRONG INFERENCE]
- **Cuándo importa:** gasto relevante en ≥ 3 canales, ≥ 2 años de historial semanal (o geo-diario), ventas omnicanal (Amazon/retail/offline), fuerte pérdida de señal (UE con bajo consentimiento, LPA, iOS). **Cuándo no:** un solo canal, poco historial, gasto plano sin variación (el modelo no puede identificar efectos), o decisiones tácticas. [STRONG INFERENCE]
- **Estado 2026 de las herramientas:**
  - **Meta Robyn:** no archivado, pero en **mantenimiento bajo**: última release GitHub v3.12.0 (dic-2024), última versión CRAN 3.12.1 (2-jul-2025), último commit en `main` nov-2024, `robynpy` 0.3.6 (abr-2025). [OFFICIAL META] (repos, [S04-025])
  - **Google Meridian:** GA el 29-ene-2025; Scenario Planner sin código (19-feb-2026); **v2.0.0 (2-sep-2026)** cambia el backend por defecto a JAX y añade calibración de priors con experimentos tipo **Meridian GeoX** (repo open source desde abr-2026); v2.1.0 (17-sep-2026). Desarrollo muy activo. [OFFICIAL Google] ([S04-026], [S04-027], [S04-028], [S04-108])
  - **PyMC-Marketing:** v1.0.0 (7-ago-2026), v1.2.0 (29-sep-2026); MMM bayesiano + CLV; muy activo. [EMPIRICAL — vendor] ([S04-030])
- **Datos de Meta para MMM:** `breakdowns=mmm` en Insights API (impresiones y gasto **estimado**, a nivel ad set, diario, solo export CSV asíncrono desde 2026). [OFFICIAL META] ([S04-065], [S04-001])
- **Triangulación:** experimentos (verdad causal puntual) → calibran priors del MMM (verdad agregada continua) → el MMM fija presupuestos y curvas de saturación → la atribución de plataforma (ajustada por *incrementality factor*) guía la táctica diaria. Meridian 2.0 y GeoX formalizan este ciclo. [OFFICIAL Google] ([S04-026], [S04-108]) + [STRONG INFERENCE]

## 1. Qué hace (y qué no) un MMM

- Regresión (habitualmente bayesiana) de un KPI (ventas, conversiones) sobre variables de medios transformadas con **adstock** (efecto retardado) y **saturación** (rendimientos decrecientes, p. ej. Hill), más controles (precio, promociones, estacionalidad, festivos, macro, tendencia, búsqueda de marca). [STRONG INFERENCE] (estándar del campo)
- Salidas: contribución por canal, ROI/mROI (marginal), curvas de respuesta, presupuesto óptimo.
- **Es inferencia causal observacional:** depende de supuestos (Meridian lo dice explícitamente: "designed for causal inference, not prediction"). Sin variación en el gasto, o con gasto que sigue a la demanda (sube en temporada alta), los efectos se confunden. [OFFICIAL Google] (FAQ Meridian, [S04-109])

## 2. Requisitos de datos (prácticos)

| Elemento | Recomendación | Comentario |
|---|---|---|
| Granularidad temporal | Semanal (nacional) o diaria/semanal por geo | Meridian está diseñado para modelos geo jerárquicos y requiere `population` [OFFICIAL Google] ([S04-109]) |
| Historial | ≥ 2 años semanales (rango típico 2–3) | Para capturar estacionalidad; no hay mínimo oficial publicado en las páginas consultadas [STRONG INFERENCE] |
| Medios | Gasto + impresiones (o reach & frequency) por canal y, si se puede, por táctica (prospecting/retargeting) | Meridian modela R&F de forma nativa [OFFICIAL Google] ([S04-027]) |
| KPI | Ventas de negocio (backend), no conversiones atribuidas por plataformas | Usar conversiones de Meta como KPI es circular |
| Controles | Precio, promociones, stock, festivos, competencia, búsquedas de marca (GQV en Meridian), macro | La omisión de controles sesga los efectos |
| Variación | Cambios de gasto suficientes; idealmente experimentos (go-dark/heavy-up) | Sin variación, el prior domina |
| Experimentos | Lift/geo para calibrar priors | Meridian `roi_calibration` / GeoX [OFFICIAL Google] ([S04-109]) |

**Datos de Meta:**
```bash
curl -X POST \
  -F "access_token=<TOKEN>" \
  -F "breakdowns=mmm" -F "export_format=csv" \
  -F "level=adset" -F "time_increment=1" \
  -F "time_range={'since':'2024-10-01','until':'2026-09-30'}" \
  "https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/insights"
# → report_run_id → poll async_status → descargar async_report_url (CSV)
```
Métricas soportadas: `impressions` y `spend` (estimado); no admite otros breakdowns; agregación por Business Manager = iterar cuentas. [OFFICIAL META] ([S04-065]) — El breakdown geográfico estadounidense pasa de DMA (Nielsen) a **Comscore Markets** (22-jun-2026) en la API de Insights: afecta a MMM/geo tests en EE. UU. [OFFICIAL META] ([S04-049])

## 3. Herramientas

### 3.1 Meta Robyn (R, con port Python)
- MMM con ridge regression + optimización multiobjetivo (Nevergrad) y calibración con experimentos; muy usado 2021–2024. [OFFICIAL META] ([S04-025]) (descripción del repo)
- **Estado verificado:** repo no archivado; releases GitHub hasta v3.12.0 (19-dic-2024); CRAN 3.12.1 (2-jul-2025, mantenedor Bernardo Lares); `main` sin commits desde nov-2024 (hay ramas con actividad hasta ene-2026); `robynpy` 0.3.6 (3-abr-2025). Interpretación: **utilizable pero sin evolución activa** en 2025–2026. [OFFICIAL META] (datos de repositorio, [S04-025]) + [STRONG INFERENCE] (interpretación)
- Implicación: para nuevos proyectos, preferir Meridian o PyMC-Marketing salvo que el equipo ya domine Robyn. [STRONG INFERENCE]

### 3.2 Google Meridian (Python, bayesiano)
- GA 29-ene-2025, programa de >20 partners certificados; modela R&F, admite priors desde experimentos, variables no-media (precio, promos). [OFFICIAL Google] ([S04-027])
- 19-feb-2026: **Scenario Planner** (interfaz sin código para escenarios de presupuesto). [OFFICIAL Google] ([S04-028])
- 2-sep-2026, **v2.0.0**: backend por defecto JAX (64 bits), calibración de priors con experimentos de incrementalidad "such as Meridian GeoX", recomendaciones de calibración por canal; 2.1.0: vocabulario declarativo para calibración/holdouts por fechas y nombres. [OFFICIAL Google] ([S04-026])
- **Meridian GeoX** (repo `google/meridian-geox`, creado abr-2026): librería open source de geo-experimentos multi-celda (holdback, go-dark, heavy-up) que sugiere experimentos a partir del MMM y alimenta priors. [OFFICIAL Google] ([S04-108])
- Sesgo potencial: herramienta de Google; incluye datos propietarios de Google (GQV, R&F de YouTube vía MMM Data Platform). Valida que los priors y datos de Meta tengan el mismo tratamiento que los de Google. [STRONG INFERENCE]

### 3.3 PyMC-Marketing (Python, bayesiano)
- Alcanzó **1.0.0 (7-ago-2026)**; 1.2.0 (29-sep-2026); MMM + CLV/BTYD; flexible (priors, efectos variables en el tiempo) y agnóstico de plataforma. [EMPIRICAL — vendor] ([S04-030])

### 3.4 Vendors
- Recast (MMM bayesiano continuo, informes ajustados por incrementalidad), Haus (geo-experimentos + "causal MMM"), Measured, Lifesight, Mutinex, Cassandra, etc. Selección: transparencia del modelo, calibración con experimentos, frecuencia de actualización, independencia de plataformas. [HYPOTHESIS] (vendors no auditados individualmente en esta investigación)

## 4. Triangulación (cómo combinar)

```
Experimentos (Conversion Lift, geo, holdouts)  ──►  priors/calibración ──► MMM
        ▲                                                         │
        │ diseñar siguientes tests donde el MMM tiene más incertidumbre │
        └─────────────────────────────────────────────────────────┘
MMM ──► presupuesto por canal + curvas de saturación + mROI
Atribución Meta (× incrementality factor) ──► reparto táctico dentro del canal (campañas, ad sets, creatividades)
```

| Nivel de decisión | Fuente | Frecuencia |
|---|---|---|
| Presupuesto anual/trimestral por canal | MMM calibrado | Trimestral (o mensual si el modelo es continuo) |
| ¿Es Meta (o una táctica) incremental? | Experimento | 1 por trimestre por táctica clave |
| Reparto dentro de Meta | Atribución (ajustada) / Incremental attribution | Semanal |
| Alarmas de tracking | Events Manager vs backend | Diario/semanal |

[STRONG INFERENCE]; Meridian implementa explícitamente la calibración con experimentos ([S04-026], [S04-109]).

## 5. Cuándo un MMM te puede engañar

1. Gasto correlacionado con estacionalidad (todo sube en Black Friday) → el modelo atribuye al medio lo que es demanda.
2. Cambios de medición (p. ej. definición de click de Meta en mar-2026) no afectan al MMM si usas gasto/impresiones, pero sí si usas conversiones de plataforma como input (no lo hagas).
3. Priors demasiado informativos (o "vendidos" por una plataforma) dominan los datos.
4. Pocas observaciones y muchos canales → sobreajuste.
5. Ignorar efectos de largo plazo/marca: los MMM de ventanas cortas infravaloran upper funnel (Haus observó mayores efectos post-test y halo omnicanal en mid/upper funnel). [EMPIRICAL] ([S04-021])

## Implicaciones operativas

- **Hacemos:** extraer `breakdowns=mmm` de Meta mensualmente (CSV async) a un data warehouse; mantener un dataset de MMM limpio (gasto, impresiones, controles, ventas backend); planificar experimentos que generen variación útil; preferir Meridian/PyMC-Marketing para proyectos nuevos.
- **Evitamos:** MMM con < 1 año de datos para decisiones grandes; usar el ROAS de Meta como KPI del MMM; decidir solo con MMM sin experimentos de contraste.
- **Umbral orientativo:** MMM empieza a compensar con gasto multicanal sostenido y significativo (orden de magnitud: decenas de miles de €/mes en ≥ 3 canales) — [HYPOTHESIS], depende de la varianza de ventas.

## Errores frecuentes

1. Tratar el MMM como verdad sin intervalos de credibilidad.
2. No incluir precio/promociones.
3. Modelos nacionales cuando hay datos geo disponibles (se pierde potencia).
4. Asumir que Robyn sigue evolucionando como en 2022–2023.

## Preguntas abiertas

- ¿Meta tiene una herramienta MMM sucesora de Robyn o se apoya en partners? (no encontrado).
- Requisitos mínimos oficiales de Meridian (semanas/geos): no localizados en las páginas consultadas.

## Fuentes clave

- [facebookexperimental/Robyn](https://github.com/facebookexperimental/Robyn) — CRAN 3.12.1 2025-07-02 — meta-oficial (S04-025)
- [google/meridian CHANGELOG](https://github.com/google/meridian/blob/main/CHANGELOG.md) — v2.0.0 2026-09-02 — vendor (S04-026)
- [Meridian open to everyone](https://blog.google/products/ads-commerce/meridian-marketing-mix-model-open-to-everyone/) — 2025-01-29 — vendor (S04-027)
- [Meridian Scenario Planner](https://blog.google/products/ads-commerce/new-meridian-tool-puts-mmm-insights-directly-in-marketers-hands/) — 2026-02-19 — vendor (S04-028)
- [google/meridian-geox](https://github.com/google/meridian-geox) — 2026 — vendor (S04-108)
- [Meridian FAQ](https://developers.google.com/meridian/docs/faqs) — vigente — vendor (S04-109)
- [pymc-labs/pymc-marketing](https://github.com/pymc-labs/pymc-marketing) — v1.2.0 2026-09-29 — vendor (S04-030)
- [MMM Breakdown on Insights API](https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights/marketing-mix-modeling) — vigente — meta-developers (S04-065)
