# Advantage+ placements, exclusiones, value rules y reporting por placement

> Última verificación: 2026-10-15 · Autor: A07 (agente) · Ámbito: cuándo dejar Advantage+ placements, cuándo y cómo restringir (exclusión a nivel cuenta, value rules, "limited spend"), personalización de assets por placement, brand safety y trampas del breakdown por placement. Cambios de 2025–2026 incluidos.

## TL;DR

- **Advantage+ placements es el punto de partida correcto para objetivos de conversión (compras, leads con evento de calidad, conversaciones cualificadas).** El modelo asigna en el margen; quitar placements "caros" en media suele subir el coste. [EMPIRICAL] (Jon Loomer 2024–2026) + [OFFICIAL META] (Meta lo recomienda "for most advertisers").
- **La excepción real son objetivos TOFU literales** (link clicks, landing page views, ThruPlay, a veces reach/impresiones): el sistema busca la acción más barata y la encuentra en Audience Network (clics accidentales, rewarded video) o en overlays de Facebook Reels. Ahí sí restringe o, mejor, cambia de objetivo. [EMPIRICAL]
- **Meta está quitando la exclusión de placements a nivel ad set.** Test documentado desde el 19–20-ago-2026 en Sales y Leads ("Excluding placements, platforms, devices and operating systems will no longer be available for your ad sets"); fuentes secundarias afirman que desde el 12-oct-2026 se extiende a Sales, Leads, Engagement y App. [STRONG INFERENCE] para el test; [CONTESTED] para el alcance/fecha de octubre (no he encontrado la página del Help Center). **Actualización 2026-11-09**: la página oficial existe ([What's new in placement settings](https://www.facebook.com/business/help/1546753450586085), releída en inglés y en español) y dice que solo **Sales, Leads y App promotion** pierden la elección manual en el conjunto; **Awareness, Traffic y Engagement no se ven afectados**; las exclusiones de cuenta por objetivo están disponibles en todos los objetivos. [OFFICIAL META] (S10-107 en `fuentes/ledger-10-cambios-api-ia.md`)
- **Sustitutos oficiales:** (1) **Placement Controls a nivel de cuenta** (Advertising settings → Account controls → Placement controls), único "bloqueo duro" que queda y aplica a todas las campañas de subasta; (2) **placement value rules** (subir/bajar puja por placement, dispositivo o SO; bajada máxima −90 %, así que no apagan un placement). [STRONG INFERENCE] (Loomer + agencias; coherente con la API `placement_controls_per_objective`).
- **"Limited spend on excluded placements" (desde 8-oct-2025):** si excluyes, Meta puede gastar **hasta un 5 % por cada placement excluido** en Sales y Leads. En API no está activo por defecto; en Ads Manager la casilla aparece **marcada por defecto**. Desmárcala si la exclusión responde a calidad o brand safety. [OFFICIAL META] (API) + [STRONG INFERENCE] (default en UI).
- **Audience Network en lead gen:** [CONTESTED]. Loomer no ha visto leads de baja calidad atribuibles al placement cuando se optimiza a conversiones; muchas agencias de lead gen lo excluyen por formularios basura. Decide con datos de CRM por placement, no por CPL.
- **El breakdown por placement es útil para detectar anomalías, no para "podar" placements por CPA medio.** Mide entrega y atribución, no incrementalidad; los recorridos son multi-placement y la asignación es marginal. [STRONG INFERENCE]
- **Personaliza assets, no excluyas:** sube 9:16 + 4:5 (+1:1), usa placement asset customization y, si tienes el nuevo flujo multimedia (test abr-2026), activa/desactiva placements por asset. [OFFICIAL META]/[EMPIRICAL]

## 1. Qué hace Advantage+ placements (y qué no)

- Hace disponibles todos los placements elegibles para el objetivo/formato y deja que la subasta y el modelo de entrega asignen impresiones donde estima el mejor resultado para tu performance goal. [OFFICIAL META]
- Meta lo recomienda "for most advertisers" y describe la exclusión limitada como "smarter alternative to blocking placements entirely" sin publicar datos de soporte. [OFFICIAL META] ([Developers blog, 8-oct-2025](https://developers.facebook.com/blog/post/2025/10/08/introducing-limited-spend-on-excluded-placements-in-marketing-api/))
- **No hay un estudio público y reciente de Meta con un % de mejora atribuible solo a Advantage+ placements.** Las cifras que circulan (−20 % coste por resultado en Advantage+ sales, −10 % coste por lead cualificado en leads) son de la suite Advantage+ completa, no de placements aislados. [STRONG INFERENCE]
- Por qué funciona desde primeros principios [STRONG INFERENCE]:
  1. Más inventario = menos presión de puja por impresión.
  2. El modelo optimiza el **coste marginal** del siguiente resultado; un placement con CPA medio alto puede contener impresiones marginales baratas.
  3. Los usuarios se mueven entre superficies; restringir superficies reduce la frecuencia útil por persona en el resto.

## 2. Cambios 2025–2026 en el control de placements

| Fecha | Cambio | Evidencia |
|---|---|---|
| 8-oct-2025 | **Limited spend on excluded placements**: hasta 5 % del gasto por placement excluido (Sales y Leads). API: campo `placement_soft_opt_out`, no activado por defecto. Ads Manager: casilla "Allow limited spending to excluded placements" marcada por defecto, con opción "Manage excluded placements" | [OFFICIAL META] ([blog developers](https://developers.facebook.com/blog/post/2025/10/08/introducing-limited-spend-on-excluded-placements-in-marketing-api/)); default UI [STRONG INFERENCE] ([PPC Land](https://ppc.land/meta-pushes-spending-5-on-excluded-placements-for-sales-and-leads-campaigns/)) |
| 2025 (fecha exacta no verificada; Loomer publicó guía de value rules "sin desactivar Advantage+" el 15-dic-2025) | Value rules por placement/dispositivo/SO disponibles sin desactivar Advantage+ (7 placements elegibles en ago-2026) | [EMPIRICAL] (Loomer) |
| 19-ago-2026 | Aviso en Ads Manager: "Excluding placements, platforms, devices and operating systems will no longer be available for your ad sets." Test en Sales y Leads, excluye categorías especiales y algunos verticales sensibles; ligado al nuevo flujo multimedia | [STRONG INFERENCE] ([Jon Loomer, 20-ago-2026](https://www.jonloomer.com/meta-removing-placement-controls-ad-sets/)) |
| 24-ago-2026 | Captura de la spec de API con `placement_controls_per_objective` | [STRONG INFERENCE] (AdsUploader) |
| 27-ago-2026 | Messenger Stories retirado; su presupuesto se redistribuye | [STRONG INFERENCE] |
| 12-oct-2026 | Según AdsUploader, el Help Center documenta el fin de exclusiones a nivel ad set para Sales, Leads, Engagement y App | [CONTESTED] (fuente secundaria; otras agencias no dan fecha) |
| releído 2026-11-09 | Help Center oficial: solo Sales, Leads y App promotion; Engagement, Awareness y Traffic conservan la elección manual; el "−10 %" pasa a "puede ayudarte a reducir el coste por resultado". La página cambió sin aviso después del 12-oct | [OFFICIAL META] (S10-107) |

**Qué sigue disponible (oct-2026):**

1. **Placement Controls de cuenta**: Advertising Settings → Account Controls → Placement Controls → "advertise only on specific placements" y desmarcar. Aplica a campañas de subasta (también con Advantage+ placements), no a Reach & Frequency. Es global a la cuenta: no puedes tener una política distinta por campaña. Cambiarlo puede reiniciar el aprendizaje de ad sets activos. [STRONG INFERENCE] ([Loomer](https://www.jonloomer.com/meta-removing-placement-controls-ad-sets/), [The Social Shepherd](https://thesocialshepherd.ca/meta-ad-placement-exclusions-2026/))
2. **Placement value rules**: bajar o subir la puja en ~7 placements elegibles (incluido Audience Network), por dispositivo o SO móvil. Bajada máxima −90 % (no apaga). [STRONG INFERENCE]
3. **Exclusiones a nivel ad set en objetivos no afectados** (Awareness, Traffic… mientras dure). [STRONG INFERENCE]
4. **Brand safety**: inventory filter (expanded/moderate/limited), block lists, publisher lists de Audience Network, verificación de terceros (IAS, DoubleVerify, Zefr) en Feed/Reels de FB e IG y, desde 2026, en el feed de Threads; block lists de Threads (mayo-2026). [OFFICIAL META] (ampliación a Threads anunciada 21-ene-2026) + [STRONG INFERENCE] (block lists Threads).

**Lectura estratégica:** la dirección de Meta es inequívoca desde 2023 (branding "Advantage+", avisos al quitar placements, 5 % de gasto en excluidos, value rules, retirada en ad set). Diseña la operación asumiendo que **no podrás excluir por campaña** en objetivos de conversión. [STRONG INFERENCE]

## 3. Cuándo restringir (y con qué herramienta)

| Situación | Problema real | Herramienta recomendada 2026 | Evidencia |
|---|---|---|---|
| Objetivo link clicks / LPV con Audience Network concentrando gasto | Clics accidentales, fraude, LPV que no convierten | 1) Cambiar a objetivo de conversión; 2) value rule −90 % en AN; 3) exclusión si el objetivo aún lo permite | [EMPIRICAL] Loomer |
| ThruPlay / vídeo views con AN Rewarded Video | Vistas incentivadas; ThruPlays > alcance | Exclusión o value rule; mejor optimizar a "2-second continuous" o a alcance con frecuencia | [EMPIRICAL] Loomer (98 % de ThruPlays en rewarded video) |
| Awareness/reach con Facebook Reels overlay al 99 % | Impresión muy barata y de baja atención | Value rule o reach con placements de alta atención; medir recuerdo (brand lift) | [EMPIRICAL] Loomer |
| Lead ads (instant forms) con muchos leads basura | Calidad, no siempre causada por placement | 1) Formulario "higher intent" + preguntas; 2) optimizar a "conversion leads" con CRM/CAPI; 3) mirar calidad por placement en CRM; solo entonces bloquear AN a nivel cuenta | [CONTESTED] |
| Brand safety (marca regulada, contenido sensible) | Adyacencia a contenido no deseado | Inventory filter "limited", block lists, verificación de terceros; AN con publisher block lists | [OFFICIAL META] |
| Formatos que no encajan (p. ej. Status/Reels sin vídeo vertical) | Recortes feos | Personalización de assets por placement, no exclusión | [OFFICIAL META] |
| Click-to-message (CTM/CTWA/IG Direct) | Algunos placements no soportan el formato (p. ej. right column en CTM) | Meta los excluye solo; no hace falta tocar | [OFFICIAL META] (docs CTM) |
| Necesidad legal/cliente "solo Instagram" | Requisito de negocio | Placement Controls de cuenta o cuenta publicitaria separada | [STRONG INFERENCE] |

### Audience Network y lead gen: dos posturas

- **Postura A (Loomer y quienes optimizan a conversión):** el sistema apenas gasta en AN si no produce el evento; los leads malos vienen del objetivo/formulario, no del placement. Quitar AN "por si acaso" es una regla vieja. [EMPIRICAL] ([Loomer](https://www.jonloomer.com/common-advertising-mistakes-placement/))
- **Postura B (agencias de lead gen local y proveedores anti-fraude):** con instant forms "more volume", AN y algunas apps generan rellenos automáticos/bots; excluirlo mejora la tasa de cualificación. Evidencia mayoritariamente anecdótica y de vendors con interés (ClickCease). [CONTESTED]
- **Cómo decidir:** exporta leads con `placement` (o con ad set dedicado como test), cruza con estado en CRM (contactado, cualificado, cita, venta) y calcula **coste por lead cualificado por placement** con al menos 50–100 leads por celda. Si AN cualifica <50 % que el resto, bloquéalo a nivel cuenta (sabiendo que afecta a todas las campañas) o aplica value rule. [HYPOTHESIS] (umbrales propios).

## 4. Personalización de assets por placement (en vez de excluir)

- **Placement asset customization**: en el anuncio, asigna un asset distinto por grupo de placements (p. ej. 9:16 para Stories/Reels/Status, 4:5 para Feeds). Meta pide al subir 1:1, 9:16 y 1.91:1, pero recomienda otros ratios en varios placements (Facebook Feed 4:5; "Ads on Facebook Reels" cae en el grupo 1:1; right column 1:1). Hay que corregir manualmente esos conflictos. [EMPIRICAL] ([Loomer, nov-2024/mar-2025](https://www.jonloomer.com/recommended-aspect-ratios-by-placement-for-meta-ad-creative/))
- **Advantage+ creative "adapt to placement" / Image touch-ups**: ajusta imágenes automáticamente; por defecto habilita placements 4:5 y 9:16. [OFFICIAL META] (docs Advantage+ creative). Revisa previews: los recortes automáticos de texto quemado fallan.
- **Nuevo flujo multimedia (test abr-2026)**: hasta 10 imágenes/vídeos por anuncio, 3 recortes por creativo, texto/URL por asset y **opt-in/out de placements por asset**, con breakdown por asset. Según Loomer, el acceso a este flujo es requisito del test que elimina exclusiones a nivel ad set: es el "nuevo sitio" donde Meta quiere que controles el encaje creativo. [EMPIRICAL] ([Loomer, 14-abr-2026](https://www.jonloomer.com/new-creative-workflow-meta-ads/))
- **Texto por placement**: Reels admite 44 caracteres de texto principal visibles; Threads recomienda 80–160 y sin hashtags/URLs. [OFFICIAL META] (Ads Guide) / [STRONG INFERENCE] (Threads).

## 5. Reporting por placement: cómo leerlo sin engañarte

1. **Qué mide el breakdown**: entrega (impresiones, alcance, CPM, clics) y resultados **atribuidos** según la ventana de atribución del ad set. Un placement puede "recibir" la conversión por view-through aunque la decisión se formara en otro. [STRONG INFERENCE]
2. **Promedio ≠ margen**: un placement con CPA medio 2x puede tener impresiones marginales baratas; el modelo ya está equilibrando. Eliminarlo cambia la subasta del resto. [STRONG INFERENCE]
3. **Para qué sí sirve**: detectar concentración anómala (un placement con >60–70 % del gasto y resultados "demasiado buenos"), métricas imposibles (ThruPlays > alcance), CTR inflado sin conversiones posteriores en analítica. Es el método de Loomer: "too good to be true" → breakdown → ¿por qué sería tan barato aquí? → verificar calidad aguas abajo. [EMPIRICAL] ([Loomer, 25-ago-2025](https://www.jonloomer.com/spot-problematic-meta-ad-placements/))
4. **Desde el 6-ago-2026** los breakdowns por dispositivo, hora y frecuencia requieren opt-in a nivel de cuenta según el changelog citado por AdsUploader; si un informe sale vacío, revisa esa opción. [STRONG INFERENCE]
5. **Threads**: algunas herramientas indican que no se desglosa en los informes por defecto; usa breakdown por placement explícito. [STRONG INFERENCE]
6. **Mensajería**: para CTWA/CTM, el breakdown por placement de "conversaciones iniciadas" es fiable como entrega, pero la calidad del chat está en tu CRM/BSP. Envía eventos de cualificación por CAPI (ver `12-…`). [OFFICIAL META]/[STRONG INFERENCE]
7. **Test causal**: si necesitas saber si un placement aporta incrementalmente, la herramienta es un A/B test (ad set con y sin, mismo presupuesto) o lift test, no el breakdown. Con la retirada de exclusiones en ad set, el A/B por placement será más difícil: tendrás que usar cuentas separadas o value rules. [STRONG INFERENCE]

## 6. Árbol de decisión rápido

```
¿Objetivo = compra / lead con evento de calidad / conversación con evento CAPI?
  └─ Sí → Advantage+ placements. Assets 9:16 + 4:5. Revisión semanal del breakdown.
           ¿Anomalía (gasto concentrado + resultados baratos + mala calidad aguas abajo)?
             └─ Sí → value rule en ese placement → si persiste, Placement Controls de cuenta.
  └─ No (clics, LPV, ThruPlay, reach) →
           ¿Puedes cambiar a un objetivo de conversión? → hazlo.
           Si no → excluye/value rule en Audience Network (y rewarded video); vigila FB Reels overlay.
¿Requisito de brand safety? → inventory filter + block lists + verificación de terceros (no exclusión de placement como primera herramienta).
¿Exclusión activa con "limited spend"? → desmarcar si el motivo es calidad/brand safety.
```

## Implicaciones operativas

- Auditoría inmediata de cuentas: (1) ad sets con exclusiones + casilla de limited spend marcada; (2) referencias a Messenger Stories/Inbox; (3) si el test de retirada te ha llegado, migra las exclusiones necesarias a Placement Controls de cuenta antes de que se fuercen.
- Separar en cuentas publicitarias distintas los negocios/clientes con políticas de placement incompatibles (p. ej. una marca que no puede aparecer en Audience Network y otra que sí lo necesita), porque el bloqueo duro pasa a ser de cuenta.
- Documentar en el playbook: "excluir placements" deja de ser palanca de optimización; las palancas son objetivo/evento, creatividad por placement y value rules.

## Errores frecuentes

- Excluir Audience Network, Marketplace y right column "por costumbre" en campañas de conversión.
- Juzgar placements por CPA medio en el breakdown y apagarlos.
- No desmarcar el 5 % de limited spend cuando la exclusión es por brand safety.
- Optimizar a link clicks y celebrar CPC bajísimos de Audience Network.
- Creer que una value rule de −90 % equivale a una exclusión (sigue pudiendo entregar).

## Preguntas abiertas

- Fecha y alcance definitivos de la retirada de exclusiones en ad set (¿Engagement y App también?, ¿mensajería?). No he encontrado la página oficial del Help Center. **Resuelto en parte el 2026-11-09**: App promotion sí, Engagement no (S10-107). Sigue abierto si caen también las exclusiones de plataforma, dispositivo y SO; la v27 ya activa la expansión de dispositivos por defecto en Ventas (ver [10/06](../10-cambios-2025-2026-api-ia-automatizacion/06-marketing-api-versiones-y-automatizacion.md)).
- Lista exacta de los ~7 placements elegibles para value rules y si se ampliará.
- ¿Habrá exclusiones por campaña vía "placement_controls_per_objective" (configuración de cuenta por objetivo)? La API sugiere controles por objetivo a nivel cuenta.
- No hay datos públicos independientes (RCT) sobre el efecto de Advantage+ placements en 2025–2026.

## Fuentes clave

- [Introducing limited spend on excluded placements in Marketing API](https://developers.facebook.com/blog/post/2025/10/08/introducing-limited-spend-on-excluded-placements-in-marketing-api/) — 2025-10-08 — meta-developers
- [Meta Is Removing Placement Controls From Ad Sets](https://www.jonloomer.com/meta-removing-placement-controls-ad-sets/) — 2026-08-20 — practitioner
- [How to Spot Problematic Meta Ad Placements](https://www.jonloomer.com/spot-problematic-meta-ad-placements/) — 2025-08-25 — practitioner
- [Common Advertising Mistakes: Placement](https://www.jonloomer.com/common-advertising-mistakes-placement/) — 2024-02 (mod. 2025-03) — practitioner
- [New Creative Workflow for Meta Ads](https://www.jonloomer.com/new-creative-workflow-meta-ads/) — 2026-04-14 — practitioner
- [Recommended Aspect Ratios by Placement](https://www.jonloomer.com/recommended-aspect-ratios-by-placement-for-meta-ad-creative/) — 2024-11 — practitioner
- [Meta pushes spending 5% on excluded placements](https://ppc.land/meta-pushes-spending-5-on-excluded-placements-for-sales-and-leads-campaigns/) — 2025-10 — prensa
- [Meta Ad Placements: Can You Still Exclude Them?](https://thesocialshepherd.ca/meta-ad-placement-exclusions-2026/) — 2026-09 — agencia
- [Meta Ads Updates (October 2026)](https://adsuploader.com/blog/meta-ads-updates) — 2026-10 — vendor
- [Meta Marketing API updates targeting, placements](https://www.socialmediatoday.com/news/meta-marketing-api-ai-updates-targeting-placements/802412/) — 2025-10-08 — prensa
