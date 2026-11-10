# Folklore obsoleto por era (2015 → 2026)

> Última verificación: 2026-10-15 · Autor: A12 (agente adversarial) · Ámbito: tácticas que fueron correctas en su momento, por qué funcionaban y qué cambio de producto, privacidad o modelo las dejó obsoletas.

## TL;DR

- Casi todo el folklore de Meta Ads nació **cierto** en su época. Lo que caduca es el contexto: el targeting manual (2015-2019), la señal de píxel pre-ATT (hasta 2021), la estructura segmentada (hasta 2022-2023) y el control manual de placements y exclusiones (2025-2026). [STRONG INFERENCE]
- **Tres rupturas explican el 80% del folklore muerto:** (1) iOS 14.5/ATT (abr-2021) — menos señal, ventanas más cortas; (2) automatización Advantage+ (2022-2025) — el sistema decide audiencia, placements y presupuesto; (3) Andromeda/GEM (dic-2024 → 2026) — modelos que recuperan y rankean con muchos más candidatos y premian la diversidad creativa. [OFFICIAL META] (S12-026, S12-027)
- **2026 está matando el folklore de medición:** fin de 7d/28d view en la API (12-ene-2026), click-through solo clic en enlace (mar-2026), y la retirada de placements manuales en objetivos de conversión (despliegue 2026). [OFFICIAL META] (S12-052, S12-009, S12-012)
- Regla práctica: si una táctica requiere **controlar a quién, dónde o cuánto** a nivel de ad set, verificar si el control sigue existiendo antes de discutir si funciona.

---

## Era 1 · 2015-2019: targeting manual y "hacking" de la subasta

| Táctica / creencia | Por qué funcionaba entonces | Qué cambió y cuándo | Estado hoy |
|---|---|---|---|
| **Optimizar el "relevance score"** (1-10) | Era visible por anuncio y correlacionaba con CPM | Sustituido por 3 diagnósticos de relevancia (anuncio mar-2019; retirada ~30-abr-2019). Ni antes ni ahora era input de la subasta | **[OUTDATED]**. Los rankings actuales "no son inputs de la subasta" (S12-022, S12-074) |
| **Regla del 20% de texto en imagen** | Penalizaba entrega de imágenes con mucho texto | Eliminada en sep-2020 | **[OUTDATED]**; hoy "text only" y "producto con texto" están entre los formatos con mayor tasa de acierto en Motion 2026 (S12-066, S12-038) |
| **Stacks de intereses y un ad set por interés** | El sistema necesitaba que le dijeras dónde buscar; las audiencias eran deterministas | Expansión automática, eliminación masiva de opciones (19-ene-2022), exclusiones de detailed targeting retiradas (31-mar-2025) | **[OUTDATED]** como estructura; intereses = sugerencias (S12-021, S12-055) |
| **Lookalike 1% como "mejor audiencia"** | Mejor proxy de semejanza disponible | Advantage+ audience y expansión de lookalikes por defecto (2023-2025) | **[OUTDATED]** (S12-046) |
| **Duplicar ganadores / "surfing"** | Sin redistribución automática, duplicar = más gasto sin tocar el original | Auction overlap documentado, CBO/A+ budget, learning por ad set | **[OUTDATED]** como táctica por defecto (S12-008) |
| **"Regla del 20%" de subida de presupuesto** | Los saltos grandes desestabilizaban el pacing y reabrían learning | Meta pasó a describir "magnitud", ejemplos 100→1.000; etiqueta *High performing* | **[OUTDATED]** como regla (S12-002) |
| **Ad sets separados por placement** | AN y columna derecha arrastraban CPAs; no había personalización por placement | Advantage+ placements, asset customisation; en 2026 sin selección manual en conversiones | **[OUTDATED]** (S12-012) |
| **Campañas de engagement para "acumular prueba social" y luego cambiar de objetivo** | Social proof visible; optimizar a engagement era barato | El objetivo optimiza a quién interactúa, no a quién compra; y editar ya transfiere la prueba social en la mayoría de casos | **[OUTDATED]** salvo como táctica creativa puntual (S12-064) |
| **Métrica de "vistas de 10 segundos"** | Era el estándar de vídeo | Sustituida por ThruPlay (jul-oct 2019) | **[OUTDATED]** (S12-073) |
| **"CBO va a ser obligatorio"** | Meta anunció CBO obligatorio para sep-2019 | Retrasado y abandonado (~2020) | Histórico; hoy CBO es opción por defecto, no obligación (S12-014, S12-075) |
| **Pixel seasoning** | Plausible en la época de audiencias de píxel pequeñas | Nunca respaldado por Meta | **UNPROVEN** desde siempre (S12-045) |

## Era 2 · 2020-2021: iOS 14.5 / ATT y la pérdida de señal

| Táctica / creencia | Por qué era cierto | Qué cambió y cuándo | Estado hoy |
|---|---|---|---|
| **Ventanas 28d click / 28d view como estándar** | Atribución generosa y de largo plazo | iOS 14.5 (abr-2021): se eliminan 28d click, 28d view y 7d view para campañas activas; por defecto 7d click + 1d view (S12-076) | 28d click vuelve a estar disponible en API como ventana de consulta; 7d/28d view eliminados de la API desde 12-ene-2026 (S12-052) |
| **"Configura y prioriza tus 8 eventos (AEM)" + verificación de dominio obligatoria** | Requisito técnico para medir usuarios iOS sin opt-in | Meta retiró en **mayo de 2023** la priorización de 8 eventos y la verificación de dominio para configurar eventos web, y eliminó la pestaña AEM (despliegue gradual; algunos vendors fechan en jun-2025 la desaparición en cuentas rezagadas) (S12-092, S12-093) | **[OUTDATED]** para web; puede seguir aplicando a apps iOS (S12-065) |
| **"Los breakdowns por edad/género/región ya no funcionan"** | Tras ATT se restringieron breakdowns para conversiones | Meta recuperó breakdowns; en 2026 cambian límites de retención y opt-in por API | **[OUTDATED]**; revisar límites 2026 (S12-052) |
| **"Necesitas 50 conversiones en 7 días o no sirve"** | Umbral oficial de learning convertido en dogma de presupuesto | Meta aclara "learning limited no es penalización"; rumores de 10/25 eventos | **CONTEXT-DEPENDENT** (S12-003) |
| **"Reparte el gasto entre muchas cuentas por si te banean"** | Miedo real a bloqueos | Meta documenta que el solapamiento ocurre también entre cuentas y que dividir páginas divide aprendizaje | **[OUTDATED]** como táctica de rendimiento (S12-008, S12-010) |
| **"No pongas texto en las imágenes"** | Herencia de la regla del 20% | Regla eliminada sep-2020 | **[OUTDATED]** |

## Era 3 · 2022-2023: Advantage+ y el giro a broad

| Táctica / creencia | Por qué era cierto | Qué cambió | Estado hoy |
|---|---|---|---|
| **"Broad siempre gana"** | Con Advantage+ shopping (ago-2022, −12% coste por compra en el estudio de lanzamiento de Meta según prensa) y Advantage+ audience, broad batía stacks de intereses en DTC (S12-077) | Meta publica mejoras medias pero no recomienda A+ audience en retargeting; tests sin diferencias significativas frente a DT | **CONTEXT-DEPENDENT** (S12-020, S12-046) |
| **"Una sola ASC con 150 creatividades"** | ASC aceptaba 150 combinaciones; simplicidad ganaba a estructuras rotas | Límites y recomendaciones de volumen; Andromeda premia diversidad, no cantidad; creatividad se agrupa en anuncios multi-activo | **[OUTDATED]** en su versión "más es mejor" (S12-006, S12-043) |
| **"Existing customer budget cap al 0-20%"** | Control de canibalización dentro de ASC | Cap retirado (feb-2025); Meta dice que se replica manualmente y afirma −5% coste por compra sin cap | **[OUTDATED]** la herramienta; la pregunta de negocio sigue viva (S12-048, S12-029) |
| **Dynamic Creative Testing (DCT) y "3:2:2"** | DCT era la forma estándar de testear combinaciones | DC no disponible al crear ad sets de ventas/app desde jun-2024 → flexible format; herramienta de test creativo (2025) | **[OUTDATED]** en ventas/app (S12-006) |
| **"Los intereses están muertos"** | Eliminación masiva de opciones (19-ene-2022) | Los intereses siguen como sugerencia | **FALSE** como absoluto (S12-021, S12-078) |

## Era 4 · 2024: automatización por defecto y llegada de Andromeda

| Cambio / creencia | Fecha | Implicación para el folklore |
|---|---|---|
| Dynamic creative restringido en ventas/app; flexible format recomendado | jun-2024 | Muere el DCT como método por defecto (S12-006) |
| Rumor "learning con 10 eventos" (Madgicx) | 9-jun-2024 | No confirmado en el Help Center a 2026 (S12-050) |
| Audience segments en campañas de ventas (nuevos/engaged/existentes) | jun-2024 | Permite *medir* la canibalización en vez de suponerla (S12-048) |
| Métricas "unique" retiradas | 30-oct-2024 | Dashboards históricos rotos; no confundir con cambio de rendimiento (S12-073) |
| Flexibilidad de presupuesto diario hasta +75% (antes +25%) | anunciada el 29-may-2025 (blog v23: introducción gradual en Ads Manager) y formalizada en el changelog de la Marketing API v24 (8-oct-2025) (S12-088, S12-089) | "Meta me roba presupuesto" → diseño documentado (S12-014, S12-079) |
| **Andromeda** (retrieval con GPU, +6% recall, +8% calidad) | 2-dic-2024 | Nace el folklore "Entity ID / 50 creatividades"; lo oficial es retrieval + diversidad (S12-026) |

## Era 5 · 2025: consolidación del producto

| Cambio | Fecha aprox. | Folklore que deja obsoleto |
|---|---|---|
| Engaged-view por defecto; atribución incremental (y en "compare attribution settings" ~abr) | ~ene-2025 | "La atribución de Meta es solo clic/view" (S12-040) |
| Existing customer budget cap eliminado | ~feb-2025 | "Controla la canibalización con el cap" (S12-048) |
| Exclusiones de detailed targeting retiradas | ad sets nuevos ~jul-2024; API v22 21-ene-2025; campañas activas 31-mar-2025; boosts 10-jun-2025 (S12-086, S12-087) | "Excluye intereses de compradores/competencia" (S12-055) |
| Value rules (edad, género, ubicación, OS; luego placements ~ago, dispositivo y ubicación de conversión ~nov) | ~may-2025 | "La única forma de priorizar un segmento es separarlo en un ad set" (S12-040) |
| Advantage+ shopping → **Advantage+ sales**; configuración unificada; Opportunity score global | anunciado 6/10-feb-2025, despliegue ~Q2 (jun) 2025 | "ASC y manual son productos distintos" (S12-040) |
| Restos del límite de 8 eventos AEM (cuentas rezagadas, según vendors) | ~jun-2025; el cambio oficial es de may-2023 | "Prioriza tus 8 eventos" (S12-065, S12-092) |
| Ad set budget sharing (20%) | ~jul-2025 | "ABO = control total del gasto por ad set" (S12-018) |
| Recomendación "≤6 anuncios por ad set" desaparece | 2025 (sin anuncio) | "3-6 anuncios por ad set" (S12-043) |
| Añadir anuncios a menudo ya no reinicia learning (observado) | ~sep-2025 | "Nunca añadas anuncios al ad set ganador" — [CONTESTED] (S12-040) |
| Gasto limitado (≤5%/placement) en placements excluidos, ON por defecto en Sales/Leads | ~oct-2025 | "Si excluyo, no gasto ahí" (S12-053) |
| Engaged-view 10 s → 5 s y solo vídeo | observado ~oct-2025; comunicado oficialmente el 3-mar-2026 (S12-080) | Comparaciones históricas de conversiones por vídeo (S12-040) |
| Anuncio de retirada de 7d/28d view en API | 13/16-oct-2025 | Ver 2026 (S12-052) |
| **GEM** (+5% conversiones IG, +3% FB Feed en Q2-2025) | 10-nov-2025 | "Andromeda lo explica todo" (S12-027) |
| Herramienta de test creativo en Ads Manager | ~nov-2025 | "Para testear necesitas una campaña ABO aparte" (S12-040) |

## Era 6 · 2026 (en curso): medición y control a nivel de cuenta

| Cambio | Fecha | Folklore que deja obsoleto |
|---|---|---|
| Ads Insights API sin `7d_view` / `28d_view`; retención 13 meses (unique, horario) y 6 meses (frecuencia) | 12-ene-2026 | "Reporta con 7d view" / dashboards históricos largos (S12-052) |
| Ad sets con opciones de detailed targeting eliminadas dejan de entregar | 15-ene-2026 (prensa) | Ad sets "legacy" con intereses retirados (S12-055) |
| Click-through = solo clic en enlace; resto → engage-through (1 día; vídeo 5 s) | mar-2026 (despliegue gradual) | "Click-through incluye likes/comentarios" (S12-009, S12-054) |
| Location fees (UK 2%, FR/IT/ES 3%, AT/TR 5%) | 1-jul-2026 | Comparar costes intermensuales sin ajustar tasas (S12-056) |
| Haus: atribución incremental pasa de 0,80× a 1,26× frente a estándar | 16-jul-2026 | "La atribución incremental de Meta no funciona" (S12-033) |
| Q2-2026: GEM y modelos de ranking +15,7% conversiones en Facebook; primer modelo generativo en retrieval; Advantage+ >75.000 M$ run-rate | 29-jul-2026 | "Los modelos de Meta están estancados" (S12-028) |
| Breakdowns de dispositivo/hora/frecuencia por API requieren activación por cuenta | 6-ago-2026 (vendor changelog) | Scripts de reporting que fallan en silencio (S12-056) |
| Selección manual de placements retirada a nivel de ad set en Sales/Leads/App (Engagement no; corrección 2026-11-09) (gradual); quedan value rules y exclusiones por cuenta | test desde ~ago-2026; documentado en Help Center (visto oct-2026) | "Placements manuales" / "excluye AN en el ad set" (S12-012, S12-042, S12-057) |
| Columna *Creative diversity* (estimated, in development) | 26-ago-2026 (prensa/vendors) | "Más variantes = más diversidad" (S12-058) |
| CTC: min ROAS cumple objetivo; cost cap se pasa ~40% | ago-2026 | "Cost cap = control de precisión del CPA" (S12-036) |
| Eventos automáticos ON por defecto para píxeles nuevos (desde 3-ago-2026) | sep-2026 (vendor changelog) | Comprobar que no se dupliquen eventos manuales (S12-056) |
| "Product browsing" activado por defecto en anuncios existentes salvo opt-out | 28-oct-2026 (reportado por anunciantes, sin página pública a 15-oct) | "Las mejoras creativas solo se activan si las elijo" (S12-056) |

## Por qué caduca el folklore (primeros principios)

1. **Pérdida de control explícito → el control se mueve a los inputs:** cuando Meta absorbe audiencia, placement y presupuesto, las palancas restantes son evento de optimización, señal de conversión (calidad de datos), puja/valor, creatividad y oferta. Las tácticas que manipulaban controles desaparecidos caducan.
2. **Más candidatos y modelos más grandes → diversidad > cantidad:** un sistema que recupera miles de anuncios y estima tasas por persona se beneficia de opciones *distintas*; las variantes casi idénticas aportan poca información nueva. [STRONG INFERENCE] (S12-026)
3. **Menos señal determinista → medición experimental:** con ventanas más cortas y más modelado, la discusión "¿cuánto es real?" solo se resuelve con experimentos (lift, geo). (S12-035)

## Implicaciones operativas

- Auditar cuentas buscando **restos arqueológicos**: ad sets por interés, duplicados activos, exclusiones de placement en el ad set, reglas automáticas basadas en métricas retiradas, dashboards con 7d/28d view.
- Cada trimestre, revisar los cambios de producto y re-evaluar 3-5 creencias del equipo.

## Errores frecuentes

- Aplicar un curso de 2021 (8 eventos, verificación de dominio, LAL stacks) a una cuenta de 2026.
- Atribuir caídas de reporting de ene/mar-2026 a "el algoritmo" cuando son cambios de definición.

## Preguntas abiertas

- (Resuelto en la revisión adversarial: +75 % anunciado 29-may-2025 y formalizado en v24 el 8-oct-2025; AEM web sin 8 eventos desde may-2023.)
- ¿Llegará la retirada de placements manuales a Awareness y Traffic?

## Fuentes clave

- [Meta Andromeda](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/) — 2024-12-02 — meta-engineering
- [Meta GEM](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/) — 2025-11-10 — meta-engineering
- [About managing ad volume](https://www.facebook.com/business/help/2720085414702598) — consultado 2026-10-15 — meta-oficial
- [What's new in placement settings](https://www.facebook.com/business/help/1546753450586085) — consultado 2026-10-15 — meta-oficial
- [Attribution models and settings](https://www.facebook.com/business/help/460276478298895) — consultado 2026-10-15 — meta-oficial
- [PPC Land — attribution windows API](https://ppc.land/meta-restricts-attribution-windows-and-data-retention-in-ads-insights-api/) — 2025-10-18 — prensa
- [Jon Loomer — 83 changes in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — ~dic-2025 — practitioner
- [Social Media Today — detailed targeting exclusions](https://www.socialmediatoday.com/news/meta-removes-detailed-targeting-exclusions-from-ad-campaigns/723389/) — 2024/2025 — prensa
- Ledger: `../fuentes/ledger-12-mitos-contradicciones.md`

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- AEM: la fecha oficial es mayo de 2023 (Help Center 126789292407737 + documentación citada por Loomer el 17-may-2023); jun-2025 solo aplica a cuentas rezagadas según vendors.
- Flexibilidad del 75 %: fechada con el blog de la v23 (29-may-2025) y el changelog de la v24 (8-oct-2025).
- Exclusiones de detailed targeting: calendario completo según el Help Center "Updates to detailed targeting" y el changelog v22.
- Engaged-view a 5 s: observado en oct-2025 y comunicado oficialmente el 3-mar-2026.
