# Audiencias en 2026: controles, sugerencias, value rules y cuándo sigue teniendo sentido segmentar

> Última verificación: 2026-10-16 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A02 (agente) · Ámbito: broad, Advantage+ audience (sugerencias vs controles), detailed targeting, lookalikes, custom audiences (web, vídeo, engagement IG/FB, lead forms, compradores, high-value, value-based LAL), customer lists, exclusiones, audience labels, value rules, audience segments, restricciones por región/edad. Retargeting y exclusiones a fondo: archivo 09.

## TL;DR

- **En 2026 hay tres tipos de input de audiencia**: (1) **controles** = límites duros (ubicación, edad mínima hasta 25, idioma, exclusión de custom audiences); (2) **sugerencias** = pistas que Meta puede ignorar (edad, género, detailed targeting, lookalikes, custom audiences de inclusión); (3) **restricciones** = "Further limit the reach of your ads" + desmarcar "Use as a suggestion", que apaga Advantage+ audience. **[OFFICIAL META]** ([HC 938372127764391](https://www.facebook.com/business/help/938372127764391), [HC 25941857932125812](https://www.facebook.com/business/help/25941857932125812))
- **Un cuarto instrumento, las *value rules***, permite decir "esta audiencia vale +X % / −Y %" (hasta +1000 % / −90 %) por edad, género, ubicación, OS, plataforma, placement, conversion location y, desde 2026, custom audiences con *audience labels*. Es la forma recomendada de "segmentar" sin fragmentar. Reemplazarán a los bid multipliers en 2027. **[OFFICIAL META]** ([HC 535014515741813](https://www.facebook.com/business/help/535014515741813), [HC 1517912029291741](https://www.facebook.com/business/help/1517912029291741))
- **Meta ya no promete "priorizar" las sugerencias** (cambio de redacción detectado en feb 2026: de "prioritize audiences matching this profile" a "reach people beyond…"); Loomer no encuentra evidencia de que las sugerencias cambien la entrega de forma medible. **[EMPIRICAL]** ([Loomer, 2026-02-25](https://www.jonloomer.com/meta-no-longer-prioritizes-suggestions/))
- **Broad + Advantage+ audience es el default para objetivos de conversión**, con datos de Meta: −7,2 % coste por resultado en Sales/App, −9,7 % en Traffic/Engagement/Leads, −14,8 % en Awareness. Meta **no lo recomienda para retargeting**. **[OFFICIAL META]** ([HC 273363992030035](https://www.facebook.com/business/help/273363992030035))
- **"Broad siempre gana" es falso como dogma.** No hay estudio público independiente que lo demuestre de forma general; el único split test conocido de Loomer fue no significativo; Haus encontró que campañas "manual" ganaron en iROAS al 58 % de marcas frente a Advantage+ (aunque "manual" ≠ "intereses"). Segmentar tiene sentido cuando **tienes información que Meta no tiene** o una **restricción de negocio**. **[CONTESTED]**
- **Detailed targeting**: exclusiones eliminadas (Ads Manager desde 31-mar-2025; boosts desde 10-jun-2025; Meta cita −22,6 % de coste mediano por conversión sin exclusiones); intereses consolidados en grupos desde 23-jun-2025 (campañas antiguas dejaron de entregar el 15-ene-2026 si no se corrigieron). **[OFFICIAL META]** ([HC 458835214668072](https://www.facebook.com/business/help/458835214668072))
- **Lookalikes**: sugerencia por defecto; desde oct 2025 no restringibles en 9 performance goals de conversión/tráfico (Loomer); desde la API v26 (todas las versiones el 1-sep-2026) se crean sin país ("countryless") y siguen la ubicación del ad set. Utilidad marginal en cuentas con señal; posible ayuda en cuentas nuevas. **[EMPIRICAL]** + **[OFFICIAL META]**
- **Novedades 2026 en custom audiences**: *audience labels* (Qualified/Disqualified leads, App users, Trial users, High/Low value, At risk, Disengaged, General customers), rediseño de Audiences en torno a labels (jul 2026), *exclusion-only custom audiences* (ago 2026), "Legal and operational custom audience exclusions" + Customer lifecycle strategy para excluir clientes (jun 2026), exclusión automática de compradores de 730 días (oct 2026), control "App install status". **[OFFICIAL META]** + **[EMPIRICAL]**
- **UE**: desde enero 2026 los usuarios de la UE pueden elegir "less personalized ads" (anuncios basados en mucho menos dato). Reduce la eficacia de cualquier segmentación/retargeting en ese tramo de audiencia; no hay cifras públicas de adopción. **[STRONG INFERENCE]** ([PPC Land](https://ppc.land/metas-2026-dma-report-reveals-whatsapp-ads-a-eu200m-fine-and-a-defiant-stance-on-personalized-advertising/), [The Current](https://www.thecurrent.com/marketing/data-privacy-meta-users-option-less-personalized-ads-eu))

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Audiencia por creativo** ("Choose an audience for each ad creative", 19-oct): cada pieza del conjunto puede orientarse a una edad y un género; se ocultan la edad y el género del conjunto y Meta puede llegar también a personas con probabilidad de responder (orienta, no limita). API: `targeting_automation.creative_audience_pairing` y `creative_audience_pairing_persona`. **[OFFICIAL META]** Activada por defecto en Ventas, desactivada en el resto; solo edad mínima y género (Loomer). **[EMPIRICAL]** En B2B rara vez aporta: la edad y el género no suelen ser el eje.
> - **API v27 (4-nov)**: `lookalike_spec` con `country` o `location_spec` se rechaza (todas las versiones ~90 días después); expansión de dispositivos activada por defecto en conjuntos de Ventas que segmentan por `user_device`/`user_os` (opt-out `0`). **[OFFICIAL META]**
> - **Audience labels** (`QUALIFIED_LEADS`, `DISQUALIFIED_LEADS`, `HIGH_VALUE_CUSTOMERS`, entre otras) usables en value rules: confirmadas en Help Center 706325895111530 el 2026-11-09. Las audiencias solo de exclusión siguen sin URL oficial (prensa que cita a Meta). **[OFFICIAL META]** / **[EMPIRICAL]**
> - Fuentes: S10-099, S10-103, S10-104, S10-109 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. El modelo de 2026: controles, sugerencias, restricciones, value rules

| Instrumento | Qué hace | Ejemplos | ¿Apaga Advantage+ audience? | Cuándo usarlo |
|---|---|---|---|---|
| **Controles de cuenta** (Advertising settings) | Límites para todas las campañas | Países permitidos, edad mínima (productos regulados), exclusión de empleados, exclusiones de "brand safety", placements excluidos | No | Restricciones legales/de negocio permanentes |
| **Controles de ad set** | Límites duros | Ubicación, edad mínima (hasta 25), idiomas, exclusión de custom audiences | No | Restricciones de la campaña |
| **Sugerencias** | Pistas; Meta puede ir más allá | Edad/género, detailed targeting, lookalikes, custom audiences de inclusión | No | Cuentas nuevas o nichos donde quieras "dar una pista"; impacto no demostrado |
| **Restricciones** ("Further limit" + desmarcar suggestion) | Audiencia cerrada | Retargeting a compradores, edad máx/mín estricta, género | Sí | Retargeting tiered, requisitos legales, campañas de alcance a listas |
| **Value rules** | Ajuste de puja por segmento | −90 % a 65+, +50 % a "High value" label, −30 % a instant forms | No | Cuando un segmento rinde distinto y quieres mantenerlo pero pagando distinto |
| **Customer lifecycle strategy** | Excluir clientes existentes (y opcionalmente engaged) en Sales | "Acquire new customers" | No (es exclusión) | Adquisición pura con base de clientes relevante |

Fuentes: [HC 938372127764391](https://www.facebook.com/business/help/938372127764391), [HC 906206294602874](https://www.facebook.com/business/help/906206294602874), [HC 1438478636941047](https://www.facebook.com/business/help/1438478636941047), [HC 2016171032241412](https://www.facebook.com/business/help/2016171032241412), [HC 1740191093676743](https://www.facebook.com/business/help/1740191093676743). **[OFFICIAL META]**

Detalles oficiales importantes:
- **Ubicación**: Meta no apunta fuera de tus ubicaciones "unless you select Reach more people likely to respond to your ads" (opción de expansión geográfica). **[OFFICIAL META]**. Loomer: la segmentación por ciudad/región se expande por radio y no distingue residentes de viajeros; el país es la segmentación más fiable. **[EMPIRICAL]**
- **Edad mínima hasta 25** y **exclusión de custom audiences** no apagan Advantage+. **[OFFICIAL META]**
- **Las exclusiones de custom audiences son siempre control**, incluso si "Use as a suggestion" está marcado. **[OFFICIAL META]**
- **Menores de 18** (o más en algunos países): solo ubicación, edad y género; sin detailed targeting, custom audiences, lookalikes ni saved audiences. **[OFFICIAL META]** ([HC 414975413946182](https://www.facebook.com/business/help/414975413946182))
- **Special ad categories** (crédito/finanzas, empleo, vivienda) y política: sin Advantage+ audience; lookalikes limitados; ciertas customer lists no elegibles desde marzo 2025; value rules sin edad/género/ciertas ubicaciones. **[OFFICIAL META]**

## 2. Broad + Advantage+ audience

- **Cómo funciona** (Meta): usa conversiones pasadas, datos de pixel, interacciones con anuncios anteriores y "millions of signals". **[OFFICIAL META]** ([HC 273363992030035](https://www.facebook.com/business/help/273363992030035))
- **Remarketing incluido**: con Advantage+ audience Meta prioriza a quien ya interactuó (pixel, conversiones, anuncios). Loomer observa típicamente 20-25 % del presupuesto de Sales yendo a engaged/existentes sin inputs (rango 10-40 %); Haus, ~15 % de gasto en retargeting tanto en Advantage+ como en manual. **[EMPIRICAL]**
- **Lo que Meta NO recomienda**: Advantage+ audience para campañas de retargeting. **[OFFICIAL META]**
- **Cuándo broad funciona peor** (**[STRONG INFERENCE]** + casos):
  - Lead gen barata con instant forms: deriva hacia demografías que rellenan mucho y compran poco (65+). Remedio: value rules, no necesariamente restringir.
  - Cuentas sin señal (pixel nuevo, sin compras): el sistema tiene poco con qué orientar la exploración; una sugerencia (lookalike de clientes, intereses) puede ayudar al arranque — beneficio no demostrado.
  - Productos de nicho extremo (B2B muy específico, profesionales médicos): la creatividad y la oferta deben "auto-seleccionar"; si no basta, segmentar o usar listas.
  - Economías distintas por segmento no expresadas en el evento (p. ej. clientes nuevos valen más): el sistema optimiza lo que mide.

## 3. Detailed targeting (intereses, comportamientos, demografía)

- **Estado 2026**: casi siempre funciona como sugerencia (Advantage+ detailed targeting); para 11 performance goals comunes no puede restringirse (Loomer, mar 2026). **[EMPIRICAL]** ([Loomer targeting 2026](https://www.jonloomer.com/meta-ads-targeting-2026/))
- **Exclusiones de detailed targeting**: eliminadas. Alternativas oficiales: exclusión de custom audiences; controles de cuenta para "brand protection" (selección limitada) y empleados. **[OFFICIAL META]** ([HC 458835214668072](https://www.facebook.com/business/help/458835214668072))
- **Consolidación de intereses** (23-jun-2025): Meta agrupa intereses similares; Ads Manager ofrece alternativas; campañas anteriores sin corregir dejaron de entregar desde 15-ene-2026. Meta "do[es] not anticipate" impacto si se usa como sugerencia. **[OFFICIAL META]**
- **Cuándo sigue teniendo sentido**: objetivos donde sí se puede restringir (reach, impresiones, ThruPlay…), campañas de awareness a un público concreto; como sugerencia en cuentas nuevas (impacto incierto). **No** crear ad sets separados por interés en objetivos de conversión. **[EMPIRICAL]**
- **API**: desde v22 (todas las versiones desde 21-abr-2025), crear/actualizar ad sets con exclusiones de detailed targeting fuera de los controles de cuenta da error; al duplicar se eliminan. **[OFFICIAL META]** (Marketing API v22 changelog, vía resumen de búsqueda)

## 4. Lookalikes

- **Qué son**: personas similares a una audiencia fuente (demografía, intereses, comportamientos); % de tamaño; "an audience made from your best customers" suele rendir mejor que "all your customers". **[OFFICIAL META]** ([HC 164749007013531](https://www.facebook.com/business/help/164749007013531))
- **Value-based lookalikes**: fuente = customer list con columna de valor; Meta pondera por valor. **[OFFICIAL META]** ([HC 458132024732845](https://www.facebook.com/business/help/458132024732845))
- **Advantage+ lookalike**: activado automáticamente en campañas nuevas/duplicadas con lookalikes de web, móvil o customer list. **[OFFICIAL META]** ([HC 1212225059146059](https://www.facebook.com/business/help/1212225059146059))
- **Expansión forzada (oct 2025)**: en 9 goals (conversions, value, LPV, link clicks, app events, conversations, calls, leads, conversion leads) ya no se puede restringir a la lookalike. **[EMPIRICAL]** ([Loomer, 2025-10-06](https://www.jonloomer.com/lookalike-audiences-expand-performance-goals/))
- **Countryless (sept 2026)**: la API ignora `country`/`location_spec` de lookalikes; la entrega sigue la ubicación del ad set. Ya no tiene sentido crear "LAL 1 % ES" vs "LAL 1 % MX" separados. **[OFFICIAL META]** ([Marketing API v26](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/version26.0))
- **Uso recomendado 2026**: como sugerencia en cuentas nuevas o para audiencias de valor (value-based LAL de top clientes); no como eje de la estructura. Loomer: "little magic pixie dust". **[EMPIRICAL]**

## 5. Custom audiences

Tipos oficiales (hasta 500 por ad account): **[OFFICIAL META]** ([HC 744354708981227](https://www.facebook.com/business/help/744354708981227))
- Tus datos: web (pixel), app activity, catálogo, customer list, offline activity.
- Meta engagement: vídeo, lead form (abrieron o enviaron), Instant Experience, shopping, cuenta de Instagram, eventos, Página de Facebook, listings de Marketplace.
- **Exclusion-only custom audience** (customer list que solo sirve para excluir; no convertible; no LAL ni value rules): para opt-outs, obligaciones legales, salvaguardas permanentes. **[OFFICIAL META]** ([HC 1011010098188443](https://www.facebook.com/business/help/1011010098188443))

### Usos que siguen teniendo sentido en 2026

| Audiencia | Uso principal | Nota |
|---|---|---|
| Compradores (customer list + Purchase web 180-730 d) | **Exclusión** en adquisición; segmento "Existing customers"; fuente de LAL/value-based LAL; retención | Cuanto más completa (online + offline), mejor; la automática de 730 d solo ve Purchase del dataset |
| Leads (lead form, CRM) | Segmento "engaged"; exclusión en campañas de captación; labels Qualified/Disqualified para value rules | Instant forms: audiencia de "abrieron" ≈ alta intención |
| Visitantes web / ViewContent / ATC | Segmento "engaged"; remarketing dinámico con catálogo | Pequeñas; frecuencia alta; atribución inflada |
| Engagement IG/FB y vídeo (ThruPlay, 50-95 %) | Sugerencias para cuentas nuevas; remarketing de contenido en ciclos largos | Calidad muy variable; vídeo 3 s ≈ ruido |
| Customer list high-value | Value rules (+%) con label "High value"; value-based LAL | Requiere actualización periódica |
| App users / install status | Excluir instalados en campañas de instalación; reactivación | Control "App install status" visto en 2026 (Loomer) |

### Listas de clientes por API: lo verificado el 2026-11-09

Leído en la guía de Custom Audiences de la Marketing API y en las referencias de `/{custom-audience-id}/users` y
`/usersreplace` (ya con la v27.0), por el bloque de audiencias por etapa del OS (`herramientas/audiencias_meta.py`):
- **Reemplazar una lista** con `usersreplace` **no reinicia el aprendizaje** de los conjuntos activos que la usan;
  añadir o quitar con POST o DELETE en `/users`, sí. Un reemplazo a la vez y el mismo esquema en todos los lotes.
  **[OFFICIAL META]**
- **Hasta 10.000 personas por llamada**, en una sesión (`session_id`, `batch_seq` desde 1, `last_batch_flag`) de 90
  minutos como máximo. **[OFFICIAL META]**
- **Sin tamaño mínimo publicado** para las listas de clientes ni tasa de coincidencia esperada; el «mínimo de ~100» que
  repiten terceros no es oficial. **[OFFICIAL META]** (ausencia) + **[HYPOTHESIS]** (los ~100 como umbral de aviso)
- `delivery_status` **300** = audiencia demasiado pequeña para entregar (200 = lista). **[OFFICIAL META]**

Para audiencias por etapa del CRM con grupo de control, ver
[playbook de consultoras §9.5](../14-playbooks/playbook-consultoras-ia-automatizacion.md).

### Audience labels (2026)
- Etiquetas para customer list, web y app custom audiences: Engaged (Qualified leads, Disqualified leads, App users, Trial users, Other engaged users) y Customers (High value, Low value, At risk, Disengaged, General customers). Se usan en value rules y "may be necessary to get the most out of features we launch in the future". **[OFFICIAL META]** ([HC 706325895111530](https://www.facebook.com/business/help/706325895111530))
- Meta recomienda en value rules con labels: diferencias de valor claras, ajustes conservadores al inicio (±20-30 %), "consolidate instead of splitting" e "include lower-value audiences" con puja reducida en vez de excluir. **[OFFICIAL META]** ([HC 1517912029291741](https://www.facebook.com/business/help/1517912029291741))

### Audience segments (reporting)
- Define "Engaged audience" y "Existing customers" a nivel de cuenta (Advertising settings → Audience segments) con custom audiences (web, app, catálogo, customer list, offline, shopping; lead forms solo para existentes); habilita breakdowns new/engaged/existing en campañas Sales. Si ya estaban definidos en Advantage+ sales, se aplican a todas las campañas de ventas de la cuenta. **[OFFICIAL META]** ([HC 1212227546879178](https://www.facebook.com/business/help/1212227546879178))
- Fallos típicos (Loomer, jun 2026; artículo no accesible directamente): definiciones incompletas que hacen parecer "nuevos" a clientes. Recomendación: existentes = todos los Purchase hasta 730 d + clientes del email/CRM. **[EMPIRICAL]**

## 6. ¿Cuándo sigue teniendo sentido segmentar? ¿Cuándo perjudicamos al algoritmo?

**Segmenta (con control, restricción o value rule) cuando** **[STRONG INFERENCE]** apoyado en Meta ("Do I have better insight into a given type of targeting than Facebook would? … If you don't think you'd know better than Facebook, then you shouldn't add that to your targeting criteria", [HC 197634954160445](https://www.facebook.com/business/help/197634954160445)):
1. **Obligación legal o de política** (edad, país, opt-outs) → controles de cuenta/ad set, exclusion-only CA.
2. **Información que Meta no tiene**: calidad de lead por segmento (CRM), LTV por segmento, márgenes por país, clientes offline → value rules, audience labels, eventos de calidad vía CAPI, exclusiones.
3. **Restricción operativa**: zona de servicio, idioma de atención, capacidad comercial → ubicación/idioma.
4. **Campañas a listas conocidas** (upsell a compradores, reactivación) → restricción con Advantage+ off, Awareness/Reach con frecuencia o Sales restringido.
5. **Objetivos de alcance** (reach/awareness) donde sí quieres un público concreto.

**Perjudicas al algoritmo cuando**:
1. Restringes edad/género por "buyer persona" sin datos (Loomer lo llama el mayor error de targeting). **[EMPIRICAL]**
2. Fragmentas en ad sets por intereses/LAL que acaban solapándose (auction overlap, learning). **[OFFICIAL META]**
3. Excluyes en exceso (todos los visitantes web, todos los engagers) en adquisición: puedes quitar a la gente con mayor probabilidad de conversión incremental… o no; depende de incrementalidad, que se mide, no se supone. **[CONTESTED]**
4. Usas audiencias pequeñas con presupuesto grande (frecuencia, CPM alto, learning limited).
5. Mantienes saved audiences antiguas con intereses retirados (dejaron de entregar en enero 2026).

**Evidencia a favor y en contra de broad**:
- A favor: claims de Meta (−7 % a −15 % coste por resultado), consenso de practitioners grandes, eliminación progresiva de controles por parte de Meta.
- En contra/matiz: Loomer (test Advantage+ audience vs detailed targeting vs LAL) obtuvo más registros y +17 % de registros de calidad con Advantage+ audience, pero con 2 compras por brazo, "hardly statistically significant" ([Loomer test](https://www.jonloomer.com/test-results-advantage-plus-audience-detailed-targeting-lookalikes/)); Haus: manual > Advantage+ en iROAS para el 58 % de marcas (no aísla el efecto audiencia). **[CONTESTED]**
- Conclusión operativa: **broad es el punto de partida; la segmentación se gana con datos (breakdowns, segments, CRM) y se implementa preferentemente con value rules/exclusiones, no con ad sets separados.**

## Implicaciones operativas

- Configura en cada cuenta: controles de cuenta (edad/países/placements reales), audience segments (engaged/existing completos), labels en las custom audiences clave, exclusion-only para opt-outs.
- Para adquisición en e-commerce con base de clientes: Customer lifecycle "Acquire new customers" (exclusión automática 730 d + listas offline) **o** value rule −X % sobre "General customers"; elegir según incrementalidad medida.
- Lead gen: si un segmento demográfico da leads malos, value rule antes que restricción (mantiene Advantage+ y la exploración).
- Revisa breakdowns por edad, género, país, placement, conversion location y **audience segment** cada 1-2 semanas antes de crear ad sets nuevos.

## Errores frecuentes

1. Creer que una sugerencia de intereses "segmenta".
2. Tres ad sets LAL 1 %/3 %/5 % + uno de intereses + uno broad con el mismo objetivo.
3. Excluir "visitantes web 180 d" de prospección sin medir.
4. No definir audience segments (y leer el ROAS de Advantage+ sales como si fuera prospección).
5. Lookalikes por país separados (desde sept 2026 son countryless).
6. Exclusiones de clientes basadas solo en el pixel cuando gran parte de las ventas son offline/marketplace.

## Preguntas abiertas

- ¿Las sugerencias tienen algún efecto medible en 2026? (Loomer: no encuentra evidencia; Meta cambió la redacción.)
- ¿Cuánta audiencia de la UE ha elegido "less personalized ads" y cómo afecta a CPM/CPA por país?
- ¿Las audience labels influirán en la entrega sin value rules (Meta sugiere "features we launch in the future")?
- ¿Qué "specialized treatments" aplica Customer lifecycle strategy más allá de la exclusión? (Meta lo afirma; Loomer no lo observó en junio 2026.)

## Fuentes clave

- [About Audience controls and Audience suggestions](https://www.facebook.com/business/help/938372127764391) — Meta HC — meta-oficial
- [Choose audience settings in Advantage+ campaigns](https://www.facebook.com/business/help/25941857932125812) — Meta HC — meta-oficial
- [About Advantage+ audience](https://www.facebook.com/business/help/273363992030035) — Meta HC — meta-oficial
- [Updates to detailed targeting](https://www.facebook.com/business/help/458835214668072) — Meta HC (jun 2025) — meta-oficial
- [About value rules](https://www.facebook.com/business/help/535014515741813) · [Audience labels in value rules](https://www.facebook.com/business/help/1517912029291741) · [Audience labels](https://www.facebook.com/business/help/706325895111530) — Meta HC — meta-oficial
- [Exclusion-only custom audiences](https://www.facebook.com/business/help/1011010098188443) · [About custom audiences](https://www.facebook.com/business/help/744354708981227) · [Audience segments](https://www.facebook.com/business/help/1212227546879178) — Meta HC — meta-oficial
- [About lookalike audiences](https://www.facebook.com/business/help/164749007013531) · [Advantage+ lookalike](https://www.facebook.com/business/help/1212225059146059) · [Value-based lookalike](https://www.facebook.com/business/help/458132024732845) — Meta HC — meta-oficial
- [Marketing API v26.0 changelog](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/version26.0) — Meta Developers, 2026-07-29 — meta-developers
- [A Guide to Meta Ads Targeting in 2026](https://www.jonloomer.com/meta-ads-targeting-2026/) — Jon Loomer, 2026-03-24 — practitioner
- [Meta No Longer Prioritizes Suggestions](https://www.jonloomer.com/meta-no-longer-prioritizes-suggestions/) — Jon Loomer, 2026-02-25 — practitioner
- [Lookalike Audiences Automatically Expand](https://www.jonloomer.com/lookalike-audiences-expand-performance-goals/) — Jon Loomer, 2025-10-06 — practitioner
- [Test Results: Advantage+ Audience vs. Detailed Targeting and Lookalikes](https://www.jonloomer.com/test-results-advantage-plus-audience-detailed-targeting-lookalikes/) — Jon Loomer — practitioner (leído vía resumen)
- [Meta's 2026 DMA report](https://ppc.land/metas-2026-dma-report-reveals-whatsapp-ads-a-eu200m-fine-and-a-defiant-stance-on-personalized-advertising/) — PPC Land, 2026 — prensa
