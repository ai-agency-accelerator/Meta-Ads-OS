# Investigación de competencia: Meta Ad Library, API, landings, ofertas y herramientas

> Última verificación: 2026-10-15 · Autor: A03 (agente) · Ámbito: qué se puede y qué no se puede saber de los anuncios de la competencia en 2026; uso de la Ad Library (web y API), diferencias UE/UK frente al resto, señales (longevidad, versiones, alcance UE), análisis de landings, ofertas, comentarios y orgánico; herramientas de terceros. El procedimiento de 50–100 anuncios está en 11.

## TL;DR

- **La Ad Library muestra todos los anuncios activos de cualquier Página en cualquier país, pero sin datos de rendimiento** para anuncios comerciales fuera de la UE/UK: ni gasto, ni impresiones, ni CTR. Se ve el creativo, el texto, las plataformas, la fecha de inicio y si hay varias versiones. **[OFFICIAL META]** (S03-056, S03-057)
- **En la UE (DSA) y el Reino Unido hay mucha más transparencia** para anuncios comerciales: targeting seleccionado (edades, género, ubicaciones), alcance desglosado por edad, género y país y, solo en la UE, alcance total estimado (`eu_total_reach`) y beneficiario/pagador. **El alcance en la UE es el mejor proxy público de escala** de un anuncio comercial. **[OFFICIAL META]** (S03-056)
- **La API de la Ad Library** (`ads_archive`) devuelve anuncios comerciales **solo si se entregaron en la UE/UK** (`ad_type=ALL` + países UE/UK). Fuera de ahí, solo anuncios políticos y de temas sociales. Gasto e impresiones solo para políticos (en rangos). Requiere verificar identidad y crear una app; límite práctico de ~200 llamadas/hora; los anuncios comerciales UE se conservan ~1 año y los políticos 7. **[OFFICIAL META]** campos / **[EMPIRICAL]** límites (S03-056, S03-058)
- **La longevidad es una señal, no una prueba de rentabilidad.** Un anuncio con 90 días activo puede ser un ganador, una campaña de marca que se mantiene igual o un anuncio con un gasto residual que nadie apaga. Además, la fecha de inicio se reinicia si el anunciante relanza el creativo con otro ID. **[STRONG INFERENCE]** (consenso de fuentes, S03-059)
- **Mejores señales combinadas de "esto funciona":** (1) longevidad + (2) muchas versiones o anuncios con el mismo creativo y texto (indica duplicación para escalar) + (3) alcance UE alto (si se anuncian en la UE) + (4) el mismo concepto iterado en varios formatos y talentos + (5) presencia en el orgánico y en otros canales. **[STRONG INFERENCE]**
- **Motion advierte que copiar lo que hace la competencia es la señal de menor confianza** para decidir qué producir ("Competitor's longest-running ad" y "Competitors did it" están al final de su escala de confianza). La competencia sirve para entender el mercado (sofisticación, promesas saturadas, huecos), no para clonar. **[EMPIRICAL]** (S03-030)
- **El análisis de la competencia va más allá del anuncio:** hay que seguir el clic (landing, oferta, precio, garantía, upsells, emails), leer comentarios y reseñas y revisar el orgánico. Ahí aparecen la oferta real y las objeciones. **[STRONG INFERENCE]**

## 1. Ad Library (web): uso práctico

**Acceso:** facebook.com/ads/library (sin necesidad de cuenta para buscar). También desde la Página del anunciante: *Transparencia de la página → Ver todo*.

**Búsqueda (S03-057, Jon Loomer, actualizado mar-2025):**
- Elegir **país** (los anuncios mostrados son los entregados en ese país) y **categoría** ("Todos los anuncios" o "Temas sociales, elecciones o política").
- Buscar por **palabra clave** (texto del anuncio) o por **anunciante**.
- Filtros: idioma, anunciante, **plataforma** (Facebook, Instagram, Audience Network, Messenger; Threads según disponibilidad), **tipo de medio** (imágenes, memes, vídeos, sin imagen/vídeo), **estado** (activo/inactivo/todos), **impresiones por fecha**, categoría especial (vivienda, empleo, crédito, política).
- **Contenido de marca (branded content)**: sección propia; muestra publicaciones de creadores con marcas (útil para ver colaboraciones).

**Qué se ve según el tipo de anuncio:**

| Tipo | Datos visibles |
|---|---|
| Comercial fuera de la UE/UK | Creativo, texto, ID, estado, fecha de inicio, plataformas, nº de versiones/anuncios con el mismo creativo. **Sin gasto, impresiones ni audiencia** |
| Comercial entregado en la UE | Lo anterior + **targeting seleccionado** (ubicación, edad, género) + **alcance** por país, edad y género + alcance total UE + beneficiario/pagador |
| Comercial entregado en UK | Targeting y desglose de alcance por edad, género y país (sin `eu_total_reach` ni beneficiario) — según los campos de la API (S03-056) |
| Político / temas sociales | Pagador ("disclaimer"), gasto e impresiones en rangos, audiencia estimada, demografía y regiones; se conservan 7 años |

**Detalles útiles:**
- **"Varias versiones" / "X anuncios usan este creativo y texto"**: el anunciante ha duplicado el creativo en varios ad sets o campañas. Suele indicar que lo está escalando o testeando en varias estructuras. **[STRONG INFERENCE]**
- **Ver detalles del resumen**: agrupa anuncios relacionados.
- **Flexible format / Dynamic creative**: se muestran varias versiones del mismo anuncio. Las combinaciones visibles no indican cuál gana.
- **Catálogo (DPA)**: se ven plantillas genéricas; poco informativo sobre los creativos de producto.

## 2. API de la Ad Library

| Aspecto | Detalle | Fuente |
|---|---|---|
| Endpoint | `ads_archive` (Graph API, objeto "Archived Ad") | S03-056 |
| Cobertura comercial | Solo anuncios **entregados en la UE/UK** (`ad_type=ALL` + `ad_reached_countries` UE/UK); fuera, solo políticos/temas sociales | S03-058 |
| Campos generales | `ad_creative_bodies`, `ad_creative_link_titles`, `ad_delivery_start_time`, `ad_delivery_stop_time`, `ad_snapshot_url`, `publisher_platforms`, `languages`, `page_id`, `ad_creation_time` | S03-056 |
| Solo UE/UK (y políticos en Brasil) | `age_country_gender_reach_breakdown`, `target_ages`, `target_gender`, `target_locations` | S03-056 |
| Solo UE | `eu_total_reach`, `beneficiary_payers` | S03-056 |
| Solo políticos | `spend`, `impressions` (rangos) | S03-056 |
| Acceso | Confirmar identidad (y ubicación) en Facebook + app de developer; token de usuario ~60 días | S03-058 |
| Límites | ~200 llamadas/hora por token (estándar Graph API); ~25 resultados por página | S03-058 (vendor) |
| Retención | Comerciales UE ~1 año desde la última entrega; políticos 7 años | S03-058, S03-057 |
| Uso de descargas | Solo análisis, conforme a los Términos de Meta | S03-056 |

Nota: `ad_delivery_start_time` es **la hora a la que el anunciante quiere empezar**, no necesariamente cuando empezó la entrega real (S03-056). `ad_creation_time` puede ser anterior.

## 3. Señales y su fiabilidad

| Señal | Qué sugiere | Fiabilidad | Trampas |
|---|---|---|---|
| Días activo (longevidad) | El anunciante no lo ha apagado → probablemente rinde o es BAU | Media | Campañas de marca, gasto residual, anunciantes desatendidos; IDs relanzados reinician la fecha |
| Nº de anuncios con el mismo creativo | Escalado o test en varias estructuras | Media-alta | Cuentas que duplican por costumbre |
| Alcance UE (`eu_total_reach`) y desglose | **Escala real** del anuncio en la UE; demografía alcanzada (¡a quién encuentra el creativo!) | **Alta** (dato oficial) | Solo para la UE; el alcance no es gasto ni rendimiento |
| Targeting seleccionado (UE/UK) | Si usan amplio o restringido por edad/género/geo | Alta | No muestra Advantage+ audience, intereses ni custom audiences |
| Iteraciones del mismo concepto (hooks, talentos, formatos) | El concepto es un ganador que exprimen | Alta | — |
| Volumen de anuncios nuevos por semana | Músculo creativo y presupuesto | Media | — |
| Persistencia de la oferta | La oferta funciona | Media | Puede ser la única que tienen |
| Comentarios (en el post) | Objeciones, deseos, lenguaje del cliente | Alta para insights | Moderación del anunciante (oculta lo negativo) |
| Aparición en orgánico (TikTok/IG) antes del pago | Prueban conceptos en orgánico | Media | — |

**Dato de contexto:** los análisis de supervivencia de anuncios muestran que la mayoría vive poco (Skaler: mediana de 3 días en 2,9M anuncios inactivos; 17 días para los de ≥500k impresiones UE) (S03-040). Un anuncio con >30–60 días activo está en la cola de supervivencia, lo que lo hace **interesante**, pero no lo **prueba**. **[EMPIRICAL]**

## 4. Más allá del anuncio: el funnel de la competencia

1. **Seguir el clic**: landing (tipo: PDP, advertorial, listicle, quiz, VSL), estructura, promesa, prueba, garantía, precio, bundles, upsells, velocidad. Guardar capturas con fecha.
2. **Entrar en su funnel**: email/SMS (secuencias, ofertas de recuperación), retargeting que recibes después, y comprar si el presupuesto lo permite (packaging, inserts, post-compra).
3. **Oferta**: precio efectivo, descuentos, trial, garantía, envío, financiación. Comparar con la propia (09).
4. **Comentarios** de sus anuncios y **reseñas** (Amazon, Trustpilot, Google): objeciones y lenguaje (03).
5. **Orgánico**: TikTok, Instagram, YouTube y creadores asociados (branded content en la Ad Library).
6. **Otros canales**: Google Ads Transparency Center y TikTok Creative Center (fuera del alcance de Meta, pero útiles para ver qué mensajes llevan a búsqueda).

## 5. Herramientas de terceros (breve, 2026)

| Herramienta | Fuerte en | Notas |
|---|---|---|
| **Foreplay** | Swipe files, biblioteca de anuncios guardados, briefs; económico | Analítica propia limitada |
| **Atria** | Biblioteca grande + inteligencia competitiva + tagging con IA + borradores con IA | Varios datasets de 2026 usan su tagging (Biddyco) |
| **Motion** | Analítica creativa de **tus** anuncios (leaderboards, tagging, informes); benchmarks 2026 | Inteligencia competitiva limitada |
| Otras (Segwise, Superads, AdSpy, Minea, BigSpy, Panoramata…) | Espionaje, tagging, alertas | Calidad y cobertura variables |

Precios y funciones cambian a menudo, y la mayoría de comparativas las escriben competidores. **[EMPIRICAL]** (S03-060). Ninguna herramienta tiene datos de rendimiento reales de la competencia: todas parten de la Ad Library más scraping y heurísticas de longevidad.

## Implicaciones operativas

- **Usar la UE como "laboratorio de transparencia"**: si el competidor se anuncia en algún país de la UE, se analizan su alcance y a quién llega cada concepto.
- **Clasificar, no coleccionar**: cada anuncio guardado se etiqueta con la taxonomía (02) y la plantilla de 11.
- **Responder a "¿qué está saturado?"** (sofisticación, 03) y "¿qué hueco queda?" antes de "¿qué copiamos?".
- **Revisión mensual** de los 5–10 competidores principales y trimestral del mercado ampliado.

## Errores frecuentes

- Tratar "activo desde hace 120 días" como "rentable".
- Copiar el anuncio más longevo del competidor sin su oferta, su marca ni su landing.
- Analizar solo el creativo e ignorar la landing y la oferta.
- Mirar solo el país propio cuando el competidor también se anuncia en la UE (donde hay datos de alcance).
- Confiar en los comentarios visibles como muestra representativa (moderación).

## Preguntas abiertas

- ¿Seguirá la UK con datos de targeting y alcance? La API lo indica a fecha de consulta.
- Retención exacta de los anuncios comerciales UE en la web frente a la API (≈1 año según fuentes secundarias).

## Fuentes clave

- [Meta for Developers — Archived Ad (Ad Library API fields)](https://developers.facebook.com/docs/graph-api/reference/archived-ad/) — vigente — meta-developers
- [Jon Loomer — Meta Ad Library](https://www.jonloomer.com/meta-ad-library/) — 2024-05-13 (mod. 2025-03-06) — practitioner
- [AdLibrary — Meta Ad Library API limitations: 7 walls in 2026](https://adlibrary.com/posts/meta-ad-library-api-limitations) — 2026-06-12 — vendor
- [Stackmatix — Meta Ads Library competitor research](https://www.stackmatix.com/blog/meta-ads-library-competitor-research) — 2026 — agencia
- [Atria — Motion alternatives / Foreplay alternatives](https://www.tryatria.com/blog/motion-alternatives) — 2026 — vendor (competidor)
- [Motion — Bootcamp 2026, homework week 3 (escala de confianza de señales)](https://motionapp.com/events/2026-creative-strategy-bootcamp/homebase/homework-week-3) — 2026 — vendor
- [Skaler — Creative fatigue in 2026 (supervivencia de anuncios)](https://skaler.app/blog/creative-fatigue-meta-ads-2026) — 2026-04-29 — vendor
