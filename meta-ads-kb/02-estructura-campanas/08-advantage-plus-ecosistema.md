# Ecosistema Advantage+ en 2026: qué automatiza cada pieza, qué controles quedan, evidencia y problemas

> Última verificación: 2026-10-16 · Autor: A02 (agente) · Ámbito: Advantage+ sales/leads/app campaigns, Advantage+ audience, placements, creative, catalog ads, campaign budget, detailed targeting/custom audience/lookalike, destination; flujo unificado de 2025 y deprecaciones de API; reporting (audience segments). IA generativa creativa en detalle: área 03. Cambios de API/automatización: área 10.

## TL;DR

- **"Advantage+" ya no es un tipo de campaña aparte: es un *estado***. En Sales, Leads y App promotion, una campaña es "Advantage+" cuando tiene **campaign budget + Advantage+ audience (o targeting relajado) + Advantage+ placements**; la API lo expone como `advantage_state` = `ADVANTAGE_PLUS_SALES` / `_APP` / `_LEADS` / `DISABLED`. **[OFFICIAL META]** ([Meta Developers](https://developers.facebook.com/docs/marketing-api/advantage-campaigns))
- **Cronología clave**: renombre ASC → Advantage+ sales y anuncio de Advantage+ leads (feb 2025); flujo de creación unificado con Advantage+ "on" por defecto (despliegue may-jun 2025); retirada del *existing customer budget cap* (2025); API v24 (8-oct-2025) bloquea crear ASC/AAC legacy; v25 (18-feb-2026) bloquea crear/actualizar ASC/AAC en v25 y en todas las versiones desde el 19-may-2026; v26 (29-jul-2026; Meta lo estimaba para septiembre) pausa las ASC/AAC restantes. **[OFFICIAL META]** (Developers) + **[EMPIRICAL]** (fechas de UI vía Loomer/PPC Land)
- **Advantage+ sales ≠ el antiguo ASC**: permite varios ad sets, sugerencias y controles de audiencia, placements editables (apagando la etiqueta), catálogo en cualquier campaña de ventas; ya no tiene el cap de clientes existentes (se replica con 2 ad sets o con Customer lifecycle strategy). Loomer: "funciona como una campaña Sales manual con los defaults puestos". **[OFFICIAL META]** + **[EMPIRICAL]**
- **Claims de Meta** (no auditados): Advantage+ sales −9 % coste por conversión; Advantage+ leads −14 % CPL y −10 % coste por lead cualificado; Advantage+ audience −7,2 % a −14,8 % coste por resultado según objetivo; Advantage+ placements −11,7 % CPA. **[OFFICIAL META]**
- **Evidencia independiente mixta**: Haus (640 geo-tests, 2025): Advantage+ ganó en iROAS solo al 42 % de marcas, −12 % iROAS medio y +12 pp de sobre-reporte, mejor a corto que a largo plazo. **[EMPIRICAL]**. Conclusión: Advantage+ es un buen *default operativo*, no una garantía de incrementalidad; hay que medir.
- **Controles que se conservan sin apagar Advantage+**: ubicación, edad mínima (≤25), idioma, exclusión de custom audiences, controles de cuenta (países, edad, placements, brand safety), value rules, spending limits por ad set dentro de campaign budget, Customer lifecycle strategy, bid strategies (incl. cost per result goal, bid cap, ROAS goal). **[OFFICIAL META]**
- **Lo que apaga Advantage+**: varios ad sets sin campaign budget; desmarcar "Use as a suggestion" en audiencia; excluir placements en cualquier ad set u optar fuera de móvil/desktop. **[OFFICIAL META]** ([HC 906206294602874](https://www.facebook.com/business/help/906206294602874)). Desde ago 2026 Meta testea **eliminar las exclusiones de placements/plataformas/dispositivos/OS a nivel de ad set** en Sales y Leads (alternativas: controles de cuenta y value rules de placement). **[EMPIRICAL]** ([Loomer, 2026-08-20](https://www.jonloomer.com/meta-removing-placement-controls-ad-sets/))
- **Problemas reportados**: sobre-inversión en clientes existentes/engaged (ROAS inflado); concentración de gasto en un solo anuncio; enhancements de Advantage+ creative activados por defecto que alteran la marca (caso "AI granny" de True Classic, 2025); bugs de audience segments y del creative testing tool (2025-2026); duplicar una campaña manual la convierte a Advantage+. **[EMPIRICAL]** + **[OFFICIAL META]** (duplicación)

---

## 1. Mapa del ecosistema (lista oficial 2026)

Meta divide Advantage+ en ([HC 2486309305148646](https://www.facebook.com/business/help/2486309305148646)): **[OFFICIAL META]**
- **End-to-end**: Advantage+ sales campaigns, Advantage+ app campaigns, Advantage+ leads campaigns.
- **Single-step**:
  - Audiencia: Advantage+ audience; Advantage+ custom audience (custom audience como sugerencia); Advantage+ lookalike; Advantage+ detailed targeting.
  - Placements: Advantage+ placements.
  - Presupuesto: Advantage+ campaign budget.
  - Creatividad: Advantage+ creative; Advantage+ catalog ads.
  - Destino: Advantage+ destination (web y app).

## 2. Cronología 2022-2026

| Fecha | Cambio | Fuente / etiqueta |
|---|---|---|
| 2022 | Lanzamiento de Advantage+ shopping campaigns (ASC), un ad set, targeting mínimo, cap de clientes existentes | Conocimiento general; **[STRONG INFERENCE]** |
| 2024-06 | Dynamic creative deja de estar disponible al crear ad sets Sales/App; se recomienda flexible format | **[OFFICIAL META]** ([HC 2720085414702598](https://www.facebook.com/business/help/2720085414702598)) |
| 2025-02 | Anuncio: ASC → Advantage+ sales; nuevo Advantage+ leads; setup simplificado (Search Engine Land 7-feb-2025) | **[EMPIRICAL]** (prensa) |
| 2025-03-31 | Eliminadas exclusiones de detailed targeting en Ads Manager | **[OFFICIAL META]** |
| 2025 (≤jun) | Retirada del existing customer budget cap en la UI | **[OFFICIAL META]** ([HC 1142614290190459](https://www.facebook.com/business/help/1142614290190459)); fecha exacta discrepante (feb vs may 2025) |
| 2025-05/06 | Despliegue del flujo unificado "Advantage+ campaign setup" (Sales/App/Leads) | **[EMPIRICAL]** ([Loomer, 2025-06-23](https://www.jonloomer.com/advantage-plus-campaign/)) |
| 2025-05-22 | Value rules disponibles | **[EMPIRICAL]** (Loomer) |
| 2025-06 | Opportunity score global | **[EMPIRICAL]** (Loomer, 19-jun-2025) |
| 2025-07 | "Advantage" → "Advantage+" en todas las funciones single-step (p. ej. Advantage+ campaign budget) | **[EMPIRICAL]** (Loomer, 6-jul-2025) |
| 2025-08/09 | Dynamic media por defecto en Advantage+ catalog ads | **[EMPIRICAL]** (PPC Land) |
| 2025-10-06 | Lookalikes no restringibles en 9 goals | **[EMPIRICAL]** |
| 2025-10-08 | API v24: bloqueo de creación ASC/AAC legacy; rutas de migración | **[OFFICIAL META]** |
| 2025-10-28 | "Limited spend on excluded placements" (hasta 5 % por placement excluido) | **[OFFICIAL META]** ([HC 830005979993164](https://www.facebook.com/business/help/830005979993164)) |
| 2026-02-18 | API v25: ASC/AAC no se pueden crear ni actualizar; `existing_customer_budget_percentage` desaparece; todas las versiones desde 19-may-2026 | **[OFFICIAL META]** ([Developers blog](https://developers.facebook.com/blog/post/2026/02/18/introducing-graph-api-v25-and-marketing-api-v25)) |
| 2026-04 | Customer lifecycle strategy en beta cerrada; qualified leads exige CAPI para nuevas campañas | **[EMPIRICAL]** (Foxwell) + **[OFFICIAL META]** |
| 2026-07-29 | API v26: (según Meta) pausa de ASC/AAC restantes; lookalikes countryless; flag `advantage_audience` explícito | **[OFFICIAL META]** |
| 2026-08-20 | Test: eliminar exclusiones de placement a nivel ad set en Sales/Leads | **[EMPIRICAL]** |
| 2026-10-13 | Exclusión automática de compradores (730 d) en "Acquire new customers" | **[EMPIRICAL]** |

## 3. Producto por producto

### 3.1 Advantage+ sales campaigns
- **Automatiza**: reparto de presupuesto entre ad sets (campaign budget), audiencia (sugerencias), placements; con catálogo, productos mostrados.
- **Controles**: ubicación/edad mínima/idioma/exclusiones; varios ad sets; spending limits; bid strategies; value rules; Customer lifecycle strategy; audience segments; catálogo; creatividades y enhancements.
- **Ventajas**: menos fragmentación, setup rápido, acceso a las optimizaciones "más avanzadas" (según Meta cuando audiencia+placement+budget están en Advantage+). **[OFFICIAL META]** ([HC 1362234537597370](https://www.facebook.com/business/help/1362234537597370))
- **Limitaciones**: mezcla prospección/remarketing/retención; ROAS de plataforma inflado si no se miran segments; sin cap nativo de existentes.
- **Best practices oficiales**: datos 1P (CAPI + pixel), creatividad diversa, "value tools", y **construir audience segments** para breakdowns new/engaged/existing. **[OFFICIAL META]**
- **Para quién**: e-commerce y venta online en general; con matices para marcas con mucha recompra (ver archivo 09).
- **Migración**: campañas API ASC con ECBC no migran automáticamente; se duplican en Ads Manager (nuevo ID, learning nuevo). Replicar ECBC: 2 ad sets (existentes con "Use as a suggestion" desmarcado + max spend; nuevos con exclusión) bajo campaign budget. **[OFFICIAL META]**

### 3.2 Advantage+ leads campaigns
- **Automatiza**: budget/audience/placements por defecto; "Website and instant forms" como location por defecto (Loomer). **[OFFICIAL META]** + **[EMPIRICAL]**
- **Controles**: todas las conversion locations (instant form, web form, calling, click-to-message) y goals (leads, qualified leads, value); sugerencias y controles de audiencia; placements manuales y ad set budgets (apagan Advantage+). **[OFFICIAL META]** ([HC 992035952809423](https://www.facebook.com/business/help/992035952809423))
- **Claim**: −14 % CPL y −10 % coste por lead cualificado vs Advantage+ off (early testing). **[OFFICIAL META]**
- **Riesgo**: optimizar volumen de leads → deriva a leads baratos de baja calidad; mitigar con qualified leads (CAPI obligatorio desde abril 2026), value rules (edad/location), formularios con fricción útil. **[EMPIRICAL]**

### 3.3 Advantage+ app campaigns
- **Estado**: el objetivo App promotion arranca con Advantage+ on (campaign budget por defecto); AAC legacy bloqueado en API (v25) y pausado en v26. **[OFFICIAL META]**
- **Comportamiento heredado del AAC legacy** (documentación aún publicada; vigencia en el nuevo flujo no confirmada): targeting solo OS/país/idioma; sin exclusiones en campaña (sí en Advertising settings); ventana de exclusión automática de 90 días para quien instaló/abrió la app; edad 18+ (ajustable en settings). **[OFFICIAL META]** ([HC 1153577308409919](https://www.facebook.com/business/help/1153577308409919)) — tratar como posiblemente desactualizado.
- **Budget scheduling** no disponible para Advantage+ app. **[OFFICIAL META]**
- Detalle: área 06.

### 3.4 Advantage+ audience
- Ver archivo 07. Claims: −14,8 % (Awareness), −9,7 % (Traffic/Engagement/Leads), −7,2 % (Sales/App). No recomendado para retargeting. **[OFFICIAL META]**
- Señales: conversiones pasadas, pixel, interacciones con anuncios. Sugerencias ya no "priorizadas" (cambio de redacción feb 2026). **[OFFICIAL META]** + **[EMPIRICAL]**

### 3.5 Advantage+ placements
- **Claim**: −11,7 % CPA vs placements manuales en un experimento. **[OFFICIAL META]** ([HC 196554084569964](https://www.facebook.com/business/help/196554084569964))
- **Controles**: exclusiones a nivel de cuenta (Audience Network, Marketplace, right column…; no apagan Advantage+); a nivel de ad set (apagan Advantage+; en test su eliminación en Sales/Leads); "Allow limited spend to excluded placements" hasta 5 % por placement excluido; value rules de placement (7 placements incl. Audience Network). **[OFFICIAL META]** + **[EMPIRICAL]**
- **Cuándo excluir**: Loomer: casi nunca; excepción típica Audience Network cuando optimizas a clicks/LPV/ThruPlay. **[EMPIRICAL]**
- **Cambios API v26**: retirados Instagram Explore Feed y Messenger Stories como placements. **[OFFICIAL META]**

### 3.6 Advantage+ creative
- **Automatiza**: variaciones de imagen/vídeo/texto y enhancements (animación, música, overlays, brillo/contraste, CTA mejorado, texto de media reescrito, generación de fondos en catálogo, tags de producto, etc.); "some enhancements may be turned on by default". **[OFFICIAL META]** ([HC 297506218282224](https://www.facebook.com/business/help/297506218282224))
- **Riesgos documentados por terceros**: ediciones no aprobadas que rompen guías de marca; caso True Classic 2025 (Meta sustituyó un anuncio top por una imagen generada de una mujer mayor); etiquetado automático de contenido modificado con IA (disclosure obligatoria desde marzo 2026 según fuentes secundarias); desde ~7-jul-2026 "Muse Image" genera variaciones. **[EMPIRICAL]** baja-media confianza ([DesignRush](https://news.designrush.com/7-worst-ai-advertising-backfires-2025), [AdMakeAI](https://admakeai.com/blog/meta-ads-updates-july-2026))
- **Recomendación**: revisar enhancements activados en cada anuncio; desactivar generativos en marcas con aprobación legal/regulada; probar enhancements no generativos (brillo, CTA) con creative testing tool. Detalle: área 03.

### 3.7 Advantage+ catalog ads (antes dynamic ads/DPA)
- **Automatiza**: qué productos mostrar a cada persona usando pixel/SDK y señales on-platform; prospección y remarketing en el mismo anuncio; enhancements de catálogo. Objetivos: Sales, App, Engagement, Leads, Traffic. En el nuevo flujo el catálogo se elige en el setup de campaña. **[OFFICIAL META]** ([HC 397103717129942](https://www.facebook.com/business/help/397103717129942))
- **Cuenta como 1 anuncio** para el límite por Página aunque muestre muchos productos. **[OFFICIAL META]**
- **Cuándo**: catálogos medianos-grandes; tiendas con mucha navegación. **Cuándo no**: 1-3 productos (mejor creatividad hecha a mano).

### 3.8 Advantage+ campaign budget
- Ver archivos 05 y 06. Matices oficiales: mejor con ≥2 ad sets; no pausar ad sets; spending limits con moderación; ≤70 ad sets; analizar a nivel campaña. **[OFFICIAL META]**

### 3.9 Advantage+ detailed targeting / custom audience / lookalike
- Detailed targeting como sugerencia; custom audience de inclusión como sugerencia (aplicado automáticamente al incluirla en "Suggest an audience"); lookalike como sugerencia (automático en campañas nuevas/duplicadas). **[OFFICIAL META]**

### 3.10 Advantage+ destination
- Permite que un anuncio genere conversiones tanto en web como en app. **[OFFICIAL META]** Útil para negocios con web y app con el mismo evento (área 06).

## 4. Mecánica "Advantage+ on/off" (UI y API)

| Palanca | On | Off |
|---|---|---|
| Budget | Campaign budget (uno o varios ad sets), spending limits opcionales | Varios ad sets con ad set budget |
| Audience | Advantage+ audience con sugerencias; edad mínima ≤25; exclusiones de custom audiences | "Further limit…" + desmarcar "Use as a suggestion" |
| Placements | Advantage+ placements; exclusiones de cuenta | Excluir placements en cualquier ad set; excluir móvil/desktop |

- La API no permite fijar `advantage_state`; se deriva. Bid strategies compatibles: LOWEST_COST_WITHOUT_CAP (recomendada), COST_CAP, LOWEST_COST_WITH_BID_CAP, LOWEST_COST_WITH_MIN_ROAS. **[OFFICIAL META]**
- Campaign score (0-100, predictivo, al crear) y opportunity score (0-100, cuenta) miden **adopción de recomendaciones**, no rendimiento; Meta lo advierte explícitamente. **[OFFICIAL META]** ([HC 3864826443789572](https://www.facebook.com/business/help/3864826443789572), [HC 804913634782260](https://www.facebook.com/business/help/804913634782260))
- **Duplicar una campaña manual en Ads Manager la crea con Advantage+ on**. **[OFFICIAL META]** ([HC 209669919072999](https://www.facebook.com/business/help/209669919072999)) — gotcha al heredar cuentas.
- Loomer: "no hay nada mágico en mantener la etiqueta Advantage+"; apagarla debería ser excepción con datos, pero la etiqueta no es un fin. **[EMPIRICAL]**

## 5. Reporting específico
- **Audience segments**: breakdown new / engaged / existing en campañas Sales (definidos a nivel de cuenta). Es la herramienta para auditar cuánto gasta Advantage+ en remarketing/retención. **[OFFICIAL META]**
- **Value rules breakdown**: resultados por regla. **[OFFICIAL META]** (HC 1643671879847552, no descargado)
- **Breakdown effect**: con campaign budget, comparar CPA por ad set/anuncio engaña; Meta lo documentó en 2025. **[OFFICIAL META]** ([HC 220698029821552](https://www.facebook.com/business/help/220698029821552))

## 6. Problemas y bugs reportados (2025-2026)

| Problema | Evidencia | Mitigación |
|---|---|---|
| Gasto excesivo en clientes existentes/engaged; ROAS inflado | Haus (sobre-reporte +12 pp); practitioners; Meta creó CLS y segments | Segments + CLS/exclusiones/value rules; medir nCAC/iROAS |
| Un anuncio se lleva todo el presupuesto | Loomer (nov 2025): a menudo deliberado; opciones: nada, nuevo anuncio distinto, testing tool, "Push delivery to this ad" (2026, test) | No forzar salvo test con propósito |
| Anuncios sin resultados 14 días apagados automáticamente | Loomer (caso propio) | Revisar estado de anuncios |
| Enhancements creativos no deseados | Prensa/agencias 2025-2026 | Auditar toggles por anuncio |
| Bugs: audience segments ausentes (ene 2026), creative testing tool (oct 2025-ene 2026), reporting de first conversion (dic 2025), no poder editar bid strategy (nov 2025) | Títulos de posts de Loomer; detalles no verificados | Comprobar en metastatus y Business Support |
| Exclusiones de clientes incompletas | Loomer (ago-oct 2026) | Definir existentes con Purchase 730 d + listas offline |
| Límites de edición con >70 ad sets | Meta | Mantener ≤70 |

## 7. Cuándo apagar (parcialmente) Advantage+

**[STRONG INFERENCE]** a partir de Meta + Loomer + CTC:
- Retargeting restringido a listas (Advantage+ audience off).
- Restricciones legales que no cubren los controles (raro).
- Necesidad de presupuestos fijos por ad set con bid strategies distintas (ad set budget).
- Placements con problema demostrado y sin alternativa en value rules/controles de cuenta.
- Tests A/B controlados donde quieres aislar una variable.

## Implicaciones operativas

- Heredar cuenta: inventario de campañas legacy ASC/AAC (ya pausadas o a punto) y su sustitución; revisar duplicados creados con Advantage+ on sin querer.
- Advantage+ sales: siempre con audience segments + revisión mensual del reparto new/engaged/existing.
- Advantage+ leads: siempre con medición de calidad (CRM) y plan para qualified leads.
- Advantage+ creative: checklist de enhancements por marca.
- Integraciones API/herramientas: deben usar v25+ y no depender de `existing_customer_budget_percentage` ni `smart_promotion_type` legacy.

## Errores frecuentes

1. Pensar que "Advantage+ sales" sigue siendo el ASC de un solo ad set y sin controles.
2. Apagar Advantage+ por costumbre (exclusiones de placements, edad máxima) sin datos.
3. No definir audience segments y leer el ROAS como prospección.
4. Dejar enhancements generativos en marcas reguladas.
5. Mantener scripts/herramientas que crean ASC por API (fallan desde v24/v25).

## Preguntas abiertas

- ¿Se generalizará la eliminación de exclusiones de placements a nivel de ad set (test ago 2026)?
- ¿Qué hace exactamente Customer lifecycle strategy más allá de excluir (Meta: "specialized treatments")?
- ¿Los resultados de Haus (2024-2025) se mantienen con el nuevo Advantage+ (multi-ad set, controles) y Andromeda/GEM?
- Vigencia de la documentación del AAC legacy en el nuevo flujo de App promotion.

## Fuentes clave

- [Advantage+ campaigns (Marketing API)](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta Developers — meta-developers
- [Introducing Graph API v25 and Marketing API v25](https://developers.facebook.com/blog/post/2026/02/18/introducing-graph-api-v25-and-marketing-api-v25) — Meta Developers, 2026-02-18 — meta-developers
- [Marketing API v26.0 changelog](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/version26.0) — Meta Developers, 2026-07-29 — meta-developers
- [Meta Advantage+ features](https://www.facebook.com/business/help/2486309305148646) — Meta HC — meta-oficial
- [What turns Advantage+ on and off](https://www.facebook.com/business/help/906206294602874) · [Create a campaign in the Advantage+ experience](https://www.facebook.com/business/help/830005979993164) — Meta HC — meta-oficial
- [About Advantage+ sales campaigns](https://www.facebook.com/business/help/1362234537597370) · [Advantage+ leads](https://www.facebook.com/business/help/992035952809423) · [Advantage+ placements](https://www.facebook.com/business/help/196554084569964) · [Advantage+ creative](https://www.facebook.com/business/help/297506218282224) · [Advantage+ catalog ads](https://www.facebook.com/business/help/397103717129942) — Meta HC — meta-oficial
- [How to replicate existing customer budget cap](https://www.facebook.com/business/help/1142614290190459) — Meta HC — meta-oficial
- [Meta deprecates legacy campaign APIs](https://ppc.land/meta-deprecates-legacy-campaign-apis-for-advantage-structure/) — PPC Land, oct 2025 — prensa
- [Advantage+ Campaign Creation: A Complete Guide](https://www.jonloomer.com/advantage-plus-campaign/) — Jon Loomer, 2025-06-23 — practitioner
- [Meta Is Removing Placement Controls From Ad Sets](https://www.jonloomer.com/meta-removing-placement-controls-ad-sets/) — Jon Loomer, 2026-08-20 — practitioner
- [When One Ad Gets All the Budget](https://www.jonloomer.com/one-ad-gets-all-the-budget/) — Jon Loomer, 2025-11-24 — practitioner
- [The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — Haus, 2025-07-28 — vendor
