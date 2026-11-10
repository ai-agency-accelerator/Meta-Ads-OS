# IA para nuestro propio workflow (fuera de Meta): investigación, creatividad, análisis, QA, reporting y CRM

> Última verificación: 2026-10-15 · Autor: A10 (agente) · Ámbito: cómo usar LLMs/agentes en el trabajo de un equipo de
> performance en Meta Ads (research creativo, angle mining, comment mining, guiones/variantes, competencia con Ad Library
> API, análisis, presupuesto, QA, reporting, scoring de leads, feedback CRM) y qué NO automatizar sin humano.

## TL;DR

- **La IA es una palanca de volumen y velocidad en research y variantes; no sustituye criterio en estrategia, claims,
  presupuesto ni aprobación final.** El cuello de botella en 2026 es producir **conceptos distintos** (Andromeda/GEM
  premian la diversidad) y leer bien los datos tras los cambios de medición. **[STRONG INFERENCE]**
- **Mayor ROI**: (1) angle mining sobre reseñas, tickets, llamadas de venta y comentarios; (2) etiquetado automático de
  creatividades (concepto, gancho, formato, persona) para analizar rendimiento por atributo; (3) borradores de guiones y
  variantes con guía de marca; (4) informes narrativos con números calculados por código. **[EMPIRICAL]**
- **Ad Library API sirve para competencia solo parcialmente**: devuelve anuncios comerciales **solo si alcanzaron la UE**;
  fuera de la UE solo anuncios políticos/sociales (y tipos de categoría especial). Para EE. UU./LatAm, la Biblioteca web
  manual sigue siendo necesaria. **[OFFICIAL META]** (S10-077)
- **Nunca automatizar sin humano**: publicar o cambiar presupuestos relevantes, claims de salud/finanzas/resultados,
  precios y ofertas, respuestas a crisis o comentarios negativos, testimonios o UGC sintéticos presentados como reales,
  cambios de tracking/CAPI, y decisiones de matar/escalar con poco volumen. **[STRONG INFERENCE]** + políticas de Meta.
- **Guardrails técnicos**: el contenido web/comentarios es dato (riesgo de prompt injection); números siempre calculados
  por código; PII minimizada y con base legal; log de prompts y salidas; aprobación por niveles. **[STRONG INFERENCE]**
- **Responsabilidad legal**: desde el 30-oct-2026 las condiciones de Meta incorporan los términos de IA generativa; el
  anunciante responde del contenido IA y no debe eliminar marcas/metadatos de IA. **[OFFICIAL META]** (fecha) /
  **[STRONG INFERENCE]** (detalle, S10-069)

---

## 1. Mapa de casos de uso

| # | Tarea | Inputs | Qué hace la IA | Qué hace el humano | Nivel de automatización |
|---|---|---|---|---|---|
| 1 | Creative research | Biblioteca de anuncios, webs de competidores, TikTok/Reels orgánicos, reseñas | Recopila, resume, clasifica formatos y mensajes | Decide qué es relevante y por qué | Alto (con revisión) |
| 2 | Angle mining | Reseñas propias y de competidores, tickets, transcripciones de ventas, Reddit/foros, encuestas | Extrae dolores, deseos, objeciones, lenguaje literal; agrupa y prioriza por frecuencia/intensidad | Valida, elige ángulos, conecta con oferta | Alto |
| 3 | Comment mining | Comentarios de anuncios (Graph API), respuestas en Threads (API de moderación desde mar-2026), DMs | Clasifica objeciones, preguntas, spam, sentimiento; detecta temas emergentes | Responde lo sensible; decide cambios | Medio |
| 4 | Guiones y variantes | Ángulos validados, guía de marca, restricciones legales, ganadores previos | Genera hooks, guiones (UGC, founder, demo, comparativa), estáticos, copies; diversidad forzada | Edita, elige, garantiza claims y tono | Medio (borradores) |
| 5 | Competencia | Ad Library (API UE + web manual) | Seguimiento de anuncios nuevos/longevos, cambios de oferta, formatos | Interpreta (longevidad ≠ rentabilidad) | Alto (seguimiento) |
| 6 | Análisis de rendimiento | Warehouse (insights + CRM), etiquetas creativas | SQL/explicaciones, análisis por atributo creativo, detección de fatiga | Formula hipótesis y decide tests | Medio |
| 7 | Recomendaciones de presupuesto | Curvas de rendimiento, CPA marginal, lift tests, MMM | Propone redistribuciones con supuestos explícitos | Aprueba; ejecuta en ventanas sensatas | Bajo (siempre aprobación) |
| 8 | QA | Borradores (API/MCP), landing, políticas | Revisión de copy vs marca/políticas, UTMs, URL, categoría especial, mejoras IA activas | Aprobación final | Alto (pre-check) |
| 9 | Reporting | Datos estructurados + log de cambios + incidencias de Meta | Redacta narrativa y destaca anomalías | Valida conclusiones | Alto (con números por código) |
| 10 | Scoring de calidad de leads | Respuestas de formulario, enriquecimiento, resultado CRM | Clasifica/predice probabilidad de cierre | Define criterios; audita sesgos | Medio |
| 11 | Feedback CRM → marketing | Notas de llamadas, motivos de pérdida | Resume motivos de no-cierre y objeciones por campaña/ángulo | Ajusta oferta, ángulos y cualificación | Alto |

## 2. Detalle de los flujos con más impacto

### 2.1 Angle mining (de la voz del cliente a conceptos)
1. Recolectar textos (reseñas 1–3★ y 5★, tickets, transcripciones de ventas, comentarios de anuncios, hilos de foros).
2. Extraer con LLM en esquema fijo: `dolor`, `deseo`, `objeción`, `desencadenante`, `alternativa usada`, `frase literal`.
3. Agrupar (embeddings/clustering) y puntuar por frecuencia × intensidad × relevancia para la oferta.
4. Convertir los 5–10 mejores clusters en **conceptos creativos distintos** (no variantes del mismo): cada concepto =
   ángulo + persona + formato + prueba.
5. Registrar el concepto como etiqueta para medir después (ver 2.3).
Etiqueta: **[EMPIRICAL]** como práctica de agencias; la ventaja frente a hacerlo a mano es cobertura y velocidad.

### 2.2 Guiones y variantes con diversidad forzada
- Prompt con: guía de marca, claims permitidos/prohibidos, prueba disponible (datos, testimonios reales), ángulo,
  persona, formato, duración, y **instrucción de diferenciación** (gancho, escenario, estructura distintos entre variantes).
- Salida a revisar por humano; producción con herramientas propias (p. ej., el motor de vídeo de este proyecto, `modulos/motor-ia/`, si
  aplica), Ads Creative Studio o creadores.
- Usar las mejoras de Meta (expansión, uncrop, animación, traducción) **después** para multiplicar formatos, no conceptos (ver 04).

### 2.3 Etiquetado creativo para análisis por atributo
- Un modelo de visión etiqueta cada anuncio: tipo de gancho (pregunta, dato, demostración, problema), presencia de
  persona/cara, UGC vs producción, texto en pantalla, duración, formato, oferta, ángulo.
- Agregar rendimiento por etiqueta (gasto, CPA, CTR, hold rate) con volumen mínimo; comparar con cuidado porque Meta
  sirve cada anuncio a audiencias distintas (no es un test aleatorio). **[STRONG INFERENCE]**
- Confirmar hallazgos con tests (creative testing tool o A/B) antes de convertirlos en reglas.

### 2.4 Competencia con Ad Library API
- Alcance oficial: `ad_type` = ALL / POLITICAL_AND_ISSUE_ADS / HOUSING / EMPLOYMENT / FINANCIAL_PRODUCTS_AND_SERVICES; los
  anuncios que **no alcanzaron ningún país de la UE solo se devuelven si son políticos/sociales**. Filtros por país, fechas,
  idioma, plataforma, `search_page_ids` (≤10), términos (≤100 caracteres). **[OFFICIAL META]** (S10-077)
- Requiere token y verificación de identidad del desarrollador (según guías); límites con error 613. **[EMPIRICAL]**
- Para mercados fuera de la UE: Biblioteca web manual (sin API comercial) o herramientas de terceros (cuidado con
  términos de uso/scraping). **[STRONG INFERENCE]**
- Heurística "anuncio activo mucho tiempo = ganador": útil como pista, **[CONTESTED]** como prueba (puede ser presupuesto
  bajo, marca, olvido).

### 2.5 Reporting narrativo seguro
- El código calcula todas las cifras y deltas; el LLM solo redacta a partir de una tabla ya calculada y de un log de
  cambios (propios, de Meta y de la status page).
- Plantilla con apartado obligatorio de "cambios de medición/plataforma relevantes" (p. ej., link clicks desde marzo-2026).

### 2.6 Scoring de leads y feedback al sistema
- Modelo (reglas + ML/LLM) que puntúa cada lead con datos del formulario y CRM; enviar a Meta solo **eventos de etapa**
  (lead cualificado, cita, venta) por CAPI/Conversion Leads, no puntuaciones opacas sin validar. **[OFFICIAL META]** (S10-087)
- **No usar atributos protegidos** ni proxies en categorías especiales (vivienda, empleo, finanzas); revisar sesgos.
  **[STRONG INFERENCE]** + políticas de Meta (área 08).

## 3. Lo que NO automatizamos sin supervisión humana

| No automatizar | Por qué |
|---|---|
| Publicar campañas o cambios de presupuesto por encima de un umbral (p. ej., >20% o >X €/día) | Irreversible, límites de API, riesgo financiero |
| Pausar/escalar por CPA con poco volumen | Ruido estadístico (07) |
| Claims de salud, finanzas, resultados, antes/después | Políticas de Meta, regulación, responsabilidad del anunciante |
| Precios, descuentos, condiciones, plazos | Errores con impacto legal/comercial |
| Testimonios, reseñas o UGC sintéticos presentados como reales; suplantación de personas | Engañoso; prohibido por políticas y leyes (p. ej., divulgación de "synthetic performers" en NY) |
| Respuestas a comentarios negativos, crisis, temas sensibles | Riesgo reputacional |
| Apelaciones de cuenta y comunicación con Meta | Requiere contexto y criterio |
| Cambios de tracking, CAPI, datasets, eventos de optimización | Rompen el aprendizaje y la medición |
| Envío de PII a LLMs externos sin acuerdo de tratamiento | GDPR/privacidad |
| Quitar marcas de agua o metadatos de IA | Prohibido en las nuevas condiciones (según terceros; S10-069) |

## 4. Guardrails técnicos y de proceso

1. **Contenido externo = dato**: comentarios, webs y reseñas pueden contener instrucciones maliciosas; nunca ejecutar
   acciones a partir de texto extraído sin validación. **[STRONG INFERENCE]**
2. **Números por código**: ningún cálculo de CPA/ROAS hecho por el LLM; el LLM explica.
3. **Aprobación por niveles**: auto (informes, etiquetado), revisión ligera (borradores de copy), aprobación obligatoria
   (publicación, presupuesto, claims).
4. **Evaluación**: set de casos de prueba para prompts críticos (QA de copy, scoring); revisar al cambiar de modelo.
5. **Trazabilidad**: guardar prompt, modelo, versión, salida y quién aprobó.
6. **Privacidad**: hashear/anonimizar; minimizar; proveedores con DPA; separar cuentas de clientes.
7. **Agentes con MCP**: read-only por defecto; escritura solo en borrador con reglas MCP (ver 06/08).

## 5. Cadencia semanal propuesta (equipo pequeño)

- **Lunes**: informe automático (datos + narrativa) y lista de anomalías → revisión humana 30 min.
- **Martes**: angle/comment mining de la semana → 3–5 conceptos nuevos priorizados.
- **Miércoles**: guiones/variantes en borrador → edición humana → producción.
- **Jueves**: QA automático de borradores → aprobación → lanzamiento (con creative testing tool si aplica).
- **Viernes**: análisis por atributo creativo y feedback CRM → actualización del backlog de hipótesis.

## Implicaciones operativas

- Construir primero la **base de datos de voz del cliente** y el **etiquetado creativo**; sin eso, la IA genera variantes
  genéricas.
- Mantener una **biblioteca de claims aprobados** y de pruebas reales para alimentar prompts.
- Medir el impacto de la IA en el workflow: nº de conceptos testeados/semana, % de ganadores, tiempo hasta lanzamiento.

## Errores frecuentes

- Pedir "20 variantes" del mismo anuncio y llamarlo diversidad creativa.
- Dejar que el LLM resuma el rendimiento sin datos verificados (alucinaciones numéricas).
- Usar la Ad Library API pensando que cubre anuncios comerciales de EE. UU.
- Automatizar respuestas a comentarios en categorías sensibles.

## Preguntas abiertas

- ¿Qué ganancia real aportan Ads Creative Studio/Brand Memory frente a un pipeline propio de angle mining + producción?
  No hay datos independientes a oct-2026.
- ¿Cómo tratará Meta (etiquetado/entrega) los anuncios hechos con IA de terceros detectados por C2PA?

## Fuentes clave

- [Ad Library API (ads_archive)](https://developers.facebook.com/docs/graph-api/reference/ads_archive/) — meta-developers (S10-077)
- [Conversion Leads integration](https://developers.facebook.com/docs/marketing-api/conversions-api/conversion-leads-integration) — meta-developers (S10-087)
- [2026 Out-of-Cycle Changes (Threads reply moderation)](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2026) — meta-developers (S10-002)
- [Meta Self-Serve Ad Terms](https://www.facebook.com/legal/self_service_ads_terms) — meta-oficial (S10-069)
- Earnings Q2-2026 (adopción de IA creativa) — meta-investors (S10-020)
