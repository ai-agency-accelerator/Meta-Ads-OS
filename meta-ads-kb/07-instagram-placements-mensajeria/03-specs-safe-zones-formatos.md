# Specs, safe zones y formatos por placement (2026)

> Última verificación: 2026-10-15 · Autor: A07 (agente) · Ámbito: especificaciones técnicas y de texto por placement, safe zones verticales, formatos de anuncio disponibles y cómo producir un "kit" mínimo de assets que cubra todo el inventario. Las cifras oficiales proceden del Ads Guide de Meta; donde no hay ficha oficial accesible se indica.

## TL;DR

- **Kit mínimo que cubre el 95 % del inventario:** vídeo/imagen **9:16 (1440×2560 o 1080×1920)** para Stories/Reels/Status + **4:5 (1440×1800 o 1080×1350)** para Feeds/Explore/Threads (+ **1:1** para catálogo, right column y búsqueda de Facebook). [OFFICIAL META] (Ads Guide) + [EMPIRICAL] (Loomer).
- **Safe zone vertical oficial (Instagram Stories y Reels): 14 % arriba, 35 % abajo, 6 % a cada lado** libres de texto, logos y elementos clave. Para Reels hay además una franja derecha (botones) que ocupa la parte baja. [OFFICIAL META] ([Reels Ads Guide](https://www.facebook.com/business/ads-guide/update/video/instagram-reels), [Stories Ads Guide](https://www.facebook.com/business/ads-guide/update/video/instagram-story))
- **Tolerancia de ratio en Instagram: 1 %**. Exporta exactamente 4:5 o 9:16, no "aproximadamente". [OFFICIAL META]
- **Texto visible útil**: Reels muestra ~44 caracteres de texto principal; Feed de Instagram recomienda 125; Feed de Facebook vídeo 50–150 y titular 27. Todo lo importante debe ir en los primeros ~40 caracteres y/o dentro del vídeo. [OFFICIAL META]
- **Música con licencia**: no se puede usar en Reels ads ni en partnership ads; usa audio original o la biblioteca libre de Meta. Es la causa nº 1 de que un Reel orgánico no pueda promocionarse. [OFFICIAL META]
- **La "zona segura unificada 9:16 desde marzo de 2026"** que repiten algunos blogs **no la he podido verificar en Meta**; en la práctica, las cifras 14/35/6 ya son comunes a Stories y Reels de Instagram. [CONTESTED]
- **Stories de más de 15 s** se cortan en tarjetas (1–3 según usuario); si el mensaje depende de la secuencia, mantén ≤15 s por tarjeta. [OFFICIAL META]
- **Threads**: 4:5 recomendado, 1:1 soportado, sin hashtags ni URLs en el texto; **WhatsApp Status**: 9:16, segmentación limitada. No he encontrado ficha oficial accesible del Ads Guide para ninguno de los dos. [STRONG INFERENCE]

## 1. Tabla de specs por placement

Cifras de Meta Ads Guide consultado 2026-10-15 salvo indicación. "Rec." = recomendado.

| Placement | Ratio rec. | Resolución rec. | Archivo / duración | Texto | Notas |
|---|---|---|---|---|---|
| **Instagram Feed – imagen** | 4:5 (soporta 1.91:1 a 4:5) | 1440×1800 | JPG/PNG, ≤30 MB, ancho mín. 500 px | Texto principal 125 rec.; titular 40; ≤30 hashtags | Tolerancia de ratio 1 % [OFFICIAL META] |
| **Instagram Stories – vídeo** | 9:16 | 1440×2560 | MP4/MOV/GIF, ≤4 GB, 1 s–60 min técnico | Texto principal 125 rec. | <16 s se reproduce entero; ≥16 s se divide en tarjetas (1–3); safe zone 14/35/6 % [OFFICIAL META] |
| **Instagram Reels – vídeo** | 9:16 | 1440×2560 | MP4/MOV, ≤4 GB, 0 s–15 min; ancho mín. 250 px (<30 s) o 500 px (≥30 s) | Texto principal 44 | Safe zone 14/35/6 %; no música con licencia, efectos de cámara, GIFs ni product labels; no Reels publicados antes del 15-oct-2021 [OFFICIAL META] |
| **Facebook Feed – vídeo** | 4:5 | 1440×1800 | MP4/MOV/GIF, ≤4 GB, 1 s–241 min | Texto principal 50–150; titular 27 | En objetivos de awareness/reach/2-s views/impresiones/engagement, el footer (titular, descripción, CTA) no aparece en móvil [OFFICIAL META] |
| **Facebook Feed – imagen** | 4:5 (Meta pide 1:1 al subir) | 1440×1800 | JPG/PNG | — | Personalizar asset por placement [EMPIRICAL] Loomer |
| **Facebook Stories** | 9:16 | 1080×1920 mín. | — | — | Vídeo: márgenes medidos 14 % arriba/20 % abajo; imagen 14/35/6 [STRONG INFERENCE] (AdKit) |
| **Facebook Reels** | 9:16 | 1080×1920 | — | — | Al subir, "Ads on Facebook Reels" cae en el grupo 1:1 → personalizar [EMPIRICAL] Loomer |
| **Ads on Facebook Reels (overlay)** | Cuadrado (banner/sticker) | — | — | Banner ~30 caracteres; sticker solo marca | Specs no publicadas formalmente [STRONG INFERENCE] |
| **Facebook In-stream** | 16:9 o 4:5 | — | Vídeo | — | Meta pide 1:1 al subir; conflicto [EMPIRICAL] |
| **Facebook Right column** | 1:1 (pide 1.91:1) | — | Imagen/vídeo/carrusel | — | Escritorio [EMPIRICAL] |
| **Facebook Search results** | 1:1 | — | — | — | [EMPIRICAL] |
| **Instagram Explore home** | 4:5 o 9:16 | — | — | — | La miniatura de la cuadrícula es lo que se ve primero [EMPIRICAL] |
| **Threads Feed** | 4:5 (1:1 soportado) | 1080×1350 | JPG/PNG; MP4; ≤30 MB | Texto 80–160 rec.; titular ~40; sin hashtags/URLs | Lo más alto se recorta y centra; solo móvil [STRONG INFERENCE] (Postory/Metricool) |
| **WhatsApp Status** | 9:16 | 1080×1920 | JPG/PNG; MP4/MOV (límites en Ads Manager) | — | Disponibilidad gradual por país/cuenta; requiere IG Stories en API [STRONG INFERENCE] + [OFFICIAL META] |
| **Audience Network** | 9:16 (apps & sites) y otros | — | — | — | Hereda de Feeds/Stories [EMPIRICAL] |
| **Messenger (destino)** | — | — | — | Greeting ≤300 caracteres; ice breakers título ≤80, respuesta ≤300; hasta 5 plantillas | Ver `10-messenger-ads.md` [OFFICIAL META] |

Fuentes: [IG Feed imagen](https://www.facebook.com/business/ads-guide/update/image/instagram-feed), [IG Stories vídeo](https://www.facebook.com/business/ads-guide/update/video/instagram-story), [IG Reels vídeo](https://www.facebook.com/business/ads-guide/update/video/instagram-reels), [FB Feed vídeo](https://www.facebook.com/business/ads-guide/update/video/facebook-feed), [Jon Loomer ratios](https://www.jonloomer.com/recommended-aspect-ratios-by-placement-for-meta-ad-creative/), [AdKit safe zones](https://adkit.so/tools/safe-zones/meta), [Postory Threads](https://postory.io/blog/meta-threads-ads).

## 2. Safe zones verticales: qué tapa la interfaz

Lienzo 1080×1920 (multiplica ×1,333 para 1440×2560):

| Zona | % | Píxeles (1080×1920) | Qué tapa |
|---|---|---|---|
| Superior | 14 % | ~269 px | Foto de perfil, nombre, etiqueta "Sponsored"/"Patrocinado", barra de progreso de Stories |
| Inferior | 35 % | ~672 px | CTA, texto principal, audio, likes/comentarios (Reels), botón "Enviar mensaje" |
| Laterales | 6 % cada uno | ~65 px | Recortes en pantallas largas (20:9) y botones laterales |
| Reels: franja derecha inferior | — | AdKit mide ~227 px de ancho a partir de y≈1152 | Columna de iconos (like, comentar, compartir, audio) |
| Reels con disclaimer (p. ej. anuncios con avisos legales/categorías especiales) | ~40 % inferior | ~768 px | Texto legal adicional |

[OFFICIAL META] para 14/35/6; [STRONG INFERENCE] para la franja derecha y el 40 % con disclaimer (mediciones de [AdKit](https://adkit.so/tools/safe-zones/meta), sep-2026).

**Regla práctica:** todo lo que deba leerse (titular quemado, precio, logo, subtítulos) dentro de un rectángulo central de ~950×1000 px en un lienzo de 1080×1920 que empiece a ~280 px desde arriba. Subtítulos en el tercio central, no abajo. [STRONG INFERENCE]

**Discrepancias conocidas** [CONTESTED]:
- Algunos medidores dan para Reels 13 % arriba / 23,4 % abajo / 3,2 % lados (medido sobre previews, mar-2026). Son menos conservadores que Meta; usa las cifras de Meta.
- La "zona unificada" de marzo de 2026 (Billo, Adsuploader) no está corroborada en Meta. No cambia nada operativo si ya usas 14/35/6.

## 3. Formatos de anuncio y dónde funcionan

| Formato | Placements típicos | Notas 2026 |
|---|---|---|
| Imagen única | Todos salvo in-stream | Advantage+ creative puede animarla ("static-to-video" GA oct-2026 según AdsUploader) [STRONG INFERENCE] |
| Vídeo único | Todos | Producir 9:16 nativo; derivar 4:5 |
| Carrusel | Feeds, Stories, Reels (render adaptado), Threads (desde 6-oct-2025) | En Threads 2–10 tarjetas |
| Colección / Instant Experience | Feeds, Stories | Más ecommerce (ver área 06) |
| Advantage+ catalog | Feeds, Stories, Reels, Threads (desde 28-oct-2025) | — |
| Mensaje (CTM/CTWA/IG Direct/multidestino) | Feeds, Stories, Reels, Status, Explore… (no right column en CTM) | Ver `05`, `10`, `11` |
| Partnership ads | FB/IG: Feeds, Stories, Reels, Live (IG Live GA anunciada 29-sep-2026) | Cabecera con creador; música con licencia no permitida |
| Reels trending ads | Tras Reels top 5 % de creadores (FB+IG) | Vía rep de Meta |
| Overlay (banner/sticker) en FB Reels | Facebook Reels de creadores | Formato de marca de baja atención |

## 4. Producción: el kit mínimo y cómo derivarlo

1. **Rodar/diseñar en 9:16** con la acción y el texto dentro del rectángulo seguro. [STRONG INFERENCE]
2. **Derivar 4:5** recortando arriba/abajo (por eso el rectángulo seguro debe ser central): la misma pieza sirve para Feed/Explore/Threads.
3. **1:1** solo si hay right column, catálogo o búsqueda de Facebook relevantes para la cuenta.
4. **Asignar por placement** en el anuncio (placement asset customization) y revisar previews de: Facebook Feed (4:5), Facebook Reels (9:16), Instagram Explore home (miniatura), Threads (4:5), WhatsApp Status (9:16).
5. **Audio**: original o libre de derechos; subtítulos quemados dentro de la zona segura; el 1.er segundo debe funcionar sin sonido.
6. **Texto principal**: frase clave en ≤44 caracteres (Reels), versión larga para Feed de Facebook.
7. **Para mensajería**: la creatividad debe "pedir" la conversación (pregunta, oferta, "escríbenos 'PRECIO'") y el greeting/ice breakers deben coincidir con ella.

## Implicaciones operativas

- Plantillas de diseño con guías de safe zone integradas (14/35/6) y una variante de Reels con la franja derecha.
- QA de creatividades: checklist de ratio exacto (tolerancia 1 %), música, texto en zona segura, primer frame.
- Para cuentas que reciclan Reels orgánicos: comprobar música con licencia antes de planificar la promoción.

## Errores frecuentes

- Exportar 1080×1350 "casi 4:5" o 1080×1900 "casi 9:16" (rechazo o recorte).
- Subtítulos al pie del vídeo, justo debajo del CTA.
- Precios o códigos de descuento en el 14 % superior (tapados por el nombre de la cuenta).
- Usar un Reel con canción de la biblioteca comercial como anuncio o partnership ad.
- Stories de 30 s con el mensaje clave al final (puede no mostrarse la tarjeta).

## Preguntas abiertas

- Ficha oficial del Ads Guide para Threads y WhatsApp Status (no accesible en la consulta; 404).
- ¿Se mantienen las specs de "Ads on Facebook Reels" (overlay) en 2026? Sin documentación formal.
- Confirmar si existe una safe zone "unificada" oficial publicada en 2026.

## Fuentes clave

- [Meta Ads Guide – Instagram Reels (vídeo)](https://www.facebook.com/business/ads-guide/update/video/instagram-reels) — vigente 2026 — meta-oficial
- [Meta Ads Guide – Instagram Stories (vídeo)](https://www.facebook.com/business/ads-guide/update/video/instagram-story) — vigente 2026 — meta-oficial
- [Meta Ads Guide – Instagram Feed (imagen)](https://www.facebook.com/business/ads-guide/update/image/instagram-feed) — vigente 2026 — meta-oficial
- [Meta Ads Guide – Facebook Feed (vídeo)](https://www.facebook.com/business/ads-guide/update/video/facebook-feed) — vigente 2026 — meta-oficial
- [Recommended Aspect Ratios by Placement](https://www.jonloomer.com/recommended-aspect-ratios-by-placement-for-meta-ad-creative/) — 2024-11 — practitioner
- [AdKit Meta safe zones](https://adkit.so/tools/safe-zones/meta) — 2026-09-10 — vendor
- [Threads Ads in 2026](https://postory.io/blog/meta-threads-ads) — 2026 — vendor
- [WhatsApp Status Ads: Setup, Pricing & Ad Specs](https://www.ycloud.com/blog/whatsapp-status-ads) — 2026-09-12 — vendor
- [Billo: 2026 Unified Creative Updates](https://billo.app/?p=50654) — 2026-06-16 — vendor (no verificado)
