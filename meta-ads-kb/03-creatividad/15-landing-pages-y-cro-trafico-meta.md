# Landing pages y CRO para tráfico de Meta (2026)

> Última verificación: 2026-10-16 · Autor: A03 (agente) · Ámbito: qué tiene de especial el tráfico que llega desde anuncios de Meta (navegador in-app, móvil, intención), velocidad, message match, formularios y páginas VSL, checkout, funciones de destino de Meta 2025-2026, diagnóstico anuncio frente a conversión y CRO con poco tráfico. Complementa [09-oferta-y-diagnóstico](09-oferta-y-diagnostico-ad-oferta-landing-ventas.md). Las políticas de landing están en el área 08, el tracking en la 04, lead gen y CRM en la 05 y el e-commerce en la 06.

## TL;DR

- **Casi todo el tráfico de Meta aterriza en el navegador in-app de Facebook/Instagram, no en Safari ni Chrome.** Meta lo confirma: los enlaces de anuncios se abren por defecto en el in-app browser y el usuario puede elegir abrirlos en el navegador del sistema. Ese navegador ofrece autofill de datos de contacto y de pago (Meta Pay), puede proponer un checkout más rápido si el usuario tiene cuenta en Shopify, Stripe, PayPal o Click-to-Pay, y desde 2026 integra Meta AI, que puede resumir tu página o responder preguntas sobre ella. **[OFFICIAL META]** (S03-078, S03-079)
- **Consecuencia práctica:** el visitante llega sin tus cookies ni sesiones (no está logueado y no tiene carrito previo) y sin el autofill o el gestor de contraseñas del navegador del sistema. Los logins sociales y algunos métodos de pago pueden fallar dentro del webview. Hay que diseñar y probar la landing y el checkout **dentro de la app de Instagram y de Facebook en un móvil real**, no en el escritorio. **[EMPIRICAL]** (varias fuentes concordantes; la magnitud del impacto en la CVR no está medida de forma independiente)
- **Meta mide la calidad de la landing y la usa en la subasta.** Entre las señales de calidad del anuncio, la documentación oficial incluye la *landing page bounce rate* y el *landing page dwell time*, además de atributos de baja calidad de la página (contenido pobre, exceso de anuncios, pop-ups/intersticiales, contenido troceado, experiencias engañosas sobre producto, plazos o atención). Las páginas o dominios con calidad baja repetida hacen que sus anuncios sean "less competitive in auctions": cuestan más y dan menos resultado. **[OFFICIAL META]** (S03-080, S03-081)
- **La ratio landing page views / link clicks es el primer termómetro técnico.** Meta recomienda comparar las dos métricas para ver cuánta gente hace clic y se va antes de que cargue la web. Las LPV se cuentan vía el in-app browser o vía pixel y, en algunos casos, mediante modelización estadística. Por eso LPV funciona sin pixel desde 2025. **[OFFICIAL META]** (S03-082, S03-083)
- **La velocidad en móvil se paga en conversión:** Core Web Vitals "buenos" = LCP ≤2,5 s, INP ≤200 ms y CLS ≤0,1 en el percentil 75 (web.dev). En un A/B con tráfico de pago, Vodafone mejoró el LCP un 31% y vendió un 8% más. En el estudio de Deloitte para Google, una mejora de 0,1 s en todo el recorrido móvil se asoció a +8,4% de conversión en retail. Meta (2022) recomienda cargar en <3 s. **[EMPIRICAL]/[OFFICIAL META]** (S03-084, S03-085, S03-086)
- **Meta puede cambiar el destino de tus clics si no lo controlas.** "Personalized destinations" en campañas de ventas a web incluye *Shops*, *Optimize website destination* (Meta elige la URL de tu web: home, producto, colección…), *browser add-ons* (botones de llamada, WhatsApp/Messenger/IG Direct o Instant Form sobre tu web) y *product browsing* (una experiencia de productos dentro de FB/IG antes de tu web). Algunas vienen activadas por defecto. Hay avisos de que product browsing se activará en anuncios existentes desde el ~28-oct-2026 salvo opt-out (sin documentación pública). En septiembre de 2026 se observó además un test de **landing generada por IA** que puede sustituir a tu web en <5% de las impresiones. **[OFFICIAL META]** (funciones) / **[EMPIRICAL]** (default de oct-2026 y test de IA) (S03-087, S03-088, S03-089, S03-090)
- **Checkout:** la tasa media de abandono de carrito es del 70,22% (50 estudios, Baymard, sep-2025). Los motivos evitables principales son los costes extra (40%), la desconfianza con la tarjeta (19%), la creación de cuenta obligatoria (18%) y un checkout largo o complicado (17%). Un checkout ideal tiene ~8 campos, frente a una media de 11,3 en 2024. **[EMPIRICAL]** (S03-091, S03-092)
- **Con poco tráfico casi nada de CRO es "testeable" en sentido estricto.** Con una CVR del 2%, detectar una mejora relativa del 20% requiere ~21.000 visitas por variante. La regla es testear **cambios grandes** (oferta, estructura, promesa, formulario), combinar evidencia cualitativa (grabaciones, heatmaps, encuestas) y no "mirar" el test cada día: los peeks repetidos inflan los falsos positivos. **[STRONG INFERENCE]** (cálculo propio + S03-093)
- **No hay que producir más creatividades si la fuga está después del clic**: CTR y hook normales con LPV/clic bajo, ATC/IC bajo o CVR baja **en todos los anuncios** indican problema de landing, oferta o checkout. Si la misma landing convierte bien con otra fuente de tráfico (email, búsqueda de marca) y mal con Meta, el problema suele ser de congruencia o de intención, no técnico. **[STRONG INFERENCE]**

## 1. Qué tiene de especial el tráfico de Meta

### 1.1 Perfil del visitante

| Rasgo | Implicación para la landing | Evidencia |
|---|---|---|
| **Llega interrumpido**, no buscando (intención baja-media; awareness variable) | La landing tiene que retomar la conversación del anuncio y no puede asumir que el visitante sabe qué es el producto | [STRONG INFERENCE]; ver 03 (awareness) |
| **Móvil casi total** (los placements son mayoritariamente de app) | Mobile-first real: el pulgar, el viewport de 360–430 px y redes móviles | [STRONG INFERENCE] |
| **Sesiones cortas y fáciles de abandonar** (volver al feed es un gesto) | La información crítica tiene que estar en los dos primeros viewports (Meta, 2022) | [OFFICIAL META] (S03-086) |
| **Dentro del in-app browser** | Sin cookies ni sesiones del navegador del sistema; autofill de Meta; el usuario puede pasar al navegador del sistema | [OFFICIAL META] (S03-078) |
| **Mezcla de niveles de awareness** (targeting amplio) | Páginas por ángulo o nivel de awareness en vez de una página para todo (sección 3) | [STRONG INFERENCE] |

### 1.2 El navegador in-app de Facebook e Instagram: qué es oficial

Según el Help Center de Meta (vigente en 2026) (S03-078):
- Los enlaces de anuncios y de contenido orgánico **se abren por defecto en el in-app browser** en iOS y Android. El usuario puede elegir en el menú abrirlos en el navegador del sistema. El anunciante **no puede** desactivar el in-app browser para sus anuncios.
- El in-app browser permite **autofill** de credenciales y datos desde el perfil, ofrece "More info" sobre la Página, guardado y compartido, *link history* y recomendaciones de compra si el usuario tiene activado el *enhanced browsing*.
- **Meta AI funciona dentro del in-app browser** y puede resumir la página o responder preguntas sobre ella.
- Meta "may collect and use website content and customers' activity on websites viewed in the in-app browser to improve advertising". El anunciante puede excluir su contenido de ese uso con `User-agent: meta-externalads / Disallow: /` en robots.txt.

Según la ayuda de Meta Pay sobre autofill (S03-079):
- El autofill guarda **datos de contacto y de pago** para rellenar formularios en Facebook, Instagram y Quest. Puede requerir autenticación biométrica del dispositivo.
- Meta "may check whether you have accounts with **Shopify, Stripe, PayPal, or Click-to-Pay** and offer faster checkout", y puede ofrecer una tarjeta virtual de un solo uso de Visa o Mastercard.
- Meta recoge la actividad de autofill (web, hora, campos rellenados, si se envió el formulario).

Además, la documentación de developers confirma que en los anuncios web con botón de mensajería "the website opens in an in-app browser for Facebook and Instagram" con un footer propio de Meta (S03-094), y la de site links dice lo mismo de esos enlaces (S03-089).

### 1.3 Lo que no es oficial pero se observa (y hay que testear)

| Fenómeno | Qué se sabe | Etiqueta | Qué hacer |
|---|---|---|---|
| **Cookies y sesiones separadas** del navegador del sistema | Varias fuentes técnicas: el webview no comparte cookies, sesiones, gestor de contraseñas ni carrito con Safari o Chrome | [EMPIRICAL] | No depender de que el usuario "ya esté logueado"; checkout como invitado; recuperación del carrito por email/teléfono; CAPI para atribución |
| **Login social / OAuth** (Google, Apple, Facebook) | Puede fallar o degradarse dentro de webviews en iOS (S03-112) | [EMPIRICAL] | Ofrecer email + código o checkout como invitado; no exigir login |
| **Apple Pay en el in-app browser** | WebKit desactiva Apple Pay en WKWebView si la app inyecta scripts, y Meta inyecta código en su in-app browser para agregar eventos de pixel (declaración de Meta recogida en 2022; base técnica en WebKit, S03-113). No hay documentación de Meta sobre Apple Pay en su in-app browser | [HYPOTHESIS] | Comprobar en iPhone real dentro de IG y FB qué botones exprés aparecen; no basar la estrategia de pago solo en Apple Pay |
| **Referrer y atribución en analítica** | Parte del tráfico del webview aparece como "direct" o sin referrer en herramientas de terceros | [EMPIRICAL] | UTMs en todos los anuncios; segmentar por user agent (`FBAN/FBAV`, `Instagram`) |
| **Impacto en la CVR** | Vendors de "redirect" afirman caídas grandes (sin metodología). Hay casos anecdóticos en foros de Shopify | [HYPOTHESIS] (magnitud) | Medir la CVR por tipo de navegador en tus datos antes de actuar |
| **Forzar la salida al navegador del sistema** | Herramientas de redirect; Flyn (vendor) advierte que ningún método es fiable en iOS y que pueden romperse sin aviso (S03-108) | [CONTESTED] | No recomendado por defecto: frágil, puede romper la medición y la experiencia; si se prueba, A/B con medición en backend |
| **Prefetch de landings** | Meta dijo en 2017 que pre-cargaba contenido de anuncios en su in-app browser (hasta ~29% menos de tiempo de carga). No hay confirmación del comportamiento actual | [OUTDATED]/no verificado | Ninguna |

**Medición del in-app browser en tus datos (recomendado):** en GA4, en tu plataforma de e-commerce o en logs, segmenta las sesiones de campañas de Meta por user agent: contiene `FBAN`/`FBAV` (Facebook), `Instagram` o ninguno (navegador del sistema). Compara CVR, AOV, abandono en el pago y uso de métodos exprés. Es la única manera de saber cuánto pesa el webview en **tu** funnel. **[STRONG INFERENCE]**

### 1.4 Implicaciones de atribución (detalle en el área 04)

- El in-app browser es un contexto de cookies propio. El pixel puede fijar `_fbp` ahí, pero si el usuario termina la compra más tarde en Safari o en la app de la tienda, solo la vinculan bien la Conversions API con datos de cliente (email, teléfono) y la atribución modelada de Meta. **[STRONG INFERENCE]**
- Las LPV se miden vía in-app browser aunque no haya pixel (S03-082). Las compras no: sin pixel ni CAPI no hay señal de conversión.
- Desde mar-2026 solo los clics en enlace cuentan como click-through (07). Las landings que dependen de interacciones previas en el anuncio verán menos conversiones "por clic".

## 2. Velocidad y calidad técnica

### 2.1 Qué dice Meta

| Afirmación | Fuente | Fecha | Etiqueta |
|---|---|---|---|
| Señales de calidad del anuncio: hide/report **y "landing page bounce rate" y "landing page dwell time"** | Help Center "Best practices to improve ad quality and performance" (S03-080) | vigente 2026 | [OFFICIAL META] |
| Las páginas, dominios o cuentas con contenido de baja calidad repetido pasan a considerarse de menor calidad: anuncios "less competitive in auctions", más caros y con menos resultados | Help Center (S03-080, S03-081) | vigente 2026 | [OFFICIAL META] |
| Atributos de landing de baja calidad: sin contenido sustantivo u original; exceso de anuncios; pop-ups o intersticiales (salvo avisos legales o logins de contenido privado); contenido troceado en varias páginas; experiencias engañosas (producto, plazos de envío, atención) | Help Center (S03-080) | vigente 2026 | [OFFICIAL META] |
| LPV = clic + carga completa del destino; comparar LPV con link clicks para ver quién se va antes de que cargue; puede haber modelización estadística | Help Center "Website landing page views" (S03-082) | vigente 2026 | [OFFICIAL META] |
| LPV optimization: muestra el anuncio a quien es más probable que haga clic y cargue la web; disponible para anunciantes "with pixel sharing challenges" desde jul-2025 | Help Center (S03-083) | 2025-2026 | [OFFICIAL META] |
| Si el objetivo son conversiones, primero optimizar a conversión (≈50 conversiones/semana); LPV como alternativa si no se llega o no hay eventos lower-funnel | Help Center "Best practices for LPV performance goals" (S03-095) | vigente 2026 | [OFFICIAL META] |
| La velocidad de carga móvil es un factor de entrega; recomendaba reducir redirecciones, plugins y acortadores; "40% of users aren't prepared to wait longer than three seconds" | Anuncio de 2017 (prensa) (S03-096) | 2017 | [OUTDATED] como cifra / principio vigente |
| Guía de "destination pages" (500 experiencias, con Branding Brand): cargar en <3 s (>50% abandona si tarda más); continuidad anuncio–página; información crítica en los dos primeros viewports; CTAs a todo el ancho y sticky; chat y promos no sticky; caso: −56% bounce, −12% coste por page view, −5% coste por compra | Meta (2022), vía SEJ (S03-086) | 2022 | [OFFICIAL META] (antiguo) |

**Lectura:** Meta no publica un "landing page score" ni un umbral de velocidad que penalice (S03-097). Pero rebote y dwell time **sí** forman parte de la calidad del anuncio, y la calidad es un componente del valor total en la subasta (área 01). Una landing lenta o que no cumple la promesa del anuncio perjudica dos veces: convierte menos **y** encarece la entrega. **[STRONG INFERENCE]** sobre la doble penalización.

### 2.2 Umbrales y datos externos

- **Core Web Vitals "good" (percentil 75 de las visitas):** LCP ≤2,5 s; INP ≤200 ms; CLS ≤0,1. "Poor": LCP >4 s, INP >500 ms, CLS >0,25 (web.dev). **[EMPIRICAL]** (estándar de Google) (S03-084)
- **Vodafone Italia** (web.dev): A/B de landing con tráfico de pago 50/50; LCP un 31% mejor → +8% de ventas, +15% lead-to-visit, +11% cart-to-visit. Técnicas: renderizar en servidor el HTML crítico, menos JS bloqueante, optimizar y redimensionar la imagen hero. **[EMPIRICAL]** (S03-085)
- **Deloitte para Google, "Milliseconds make millions"** (~2020): una mejora de 0,1 s en **todas** las páginas del recorrido móvil se asoció a +8,4% de conversión en retail y +10,1% en viajes. Es un estudio encargado por Google y correlacional. **[EMPIRICAL]** (S03-104)

### 2.3 Ratio LPV / link clicks (o / outbound clicks)

- **Qué mide:** clics que acaban en una carga completa. Las causas de una ratio baja según Meta son que la página no carga del todo o que el anuncio tiene varios destinos (S03-098).
- **Umbral de trabajo:** <70–80% de LPV sobre outbound clicks en tráfico frío de Feed/Reels merece investigación técnica (velocidad, redirecciones, consent banners que bloquean, errores). **[HYPOTHESIS]** (no hay umbral publicado; compara con tu histórico y por placement)
- **Ojo con las comparaciones:** link clicks incluye destinos dentro de Meta (formularios, mensajes, site links). Para webs, la comparación más limpia es outbound clicks → LPV.

### 2.4 Checklist técnico mínimo (móvil, dentro del in-app browser)

1. LCP ≤2,5 s en campo (CrUX/PageSpeed) **y** prueba manual en IG y FB con 4G.
2. Sin redirecciones encadenadas ni acortadores; dominio propio y HTTPS.
3. Hero optimizado (WebP/AVIF, tamaño adecuado, precarga). Nada de vídeos autoplay pesados por encima del pliegue.
4. Scripts de terceros auditados (chat, reviews, heatmaps, A/B, pixels): carga diferida.
5. Sin pop-ups ni intersticiales al entrar (atributo de baja calidad para Meta). El banner de consentimiento, compacto y sin tapar el CTA.
6. Formularios con `autocomplete` y tipos de input correctos (tel, email) para que funcionen el autofill de Meta y los teclados móviles.
7. Pixel + CAPI con deduplicación; UTMs; evento de LPV/ViewContent correcto (área 04).

## 3. Message match, anatomía de la landing y páginas por ángulo

**Principio:** la landing es la **segunda mitad del anuncio**. Lo que el anuncio prometió (persona, dolor, mecanismo, oferta, precio, estilo visual) debe reaparecer en los primeros segundos de la página. Meta lo recoge en su guía de 2022 ("continuity between the ad's images and messaging and the landing page") (S03-086). Ver 09 §3 para la lista de elementos.

### 3.1 Primer viewport (above the fold) en móvil

| Elemento | Función | Error típico |
|---|---|---|
| Titular que **repite la promesa o el ángulo** del anuncio | Confirmar "estoy en el sitio correcto" | Titular de marca genérico |
| Visual coherente con el anuncio (mismo producto, talento, contexto) | Continuidad | Foto de stock distinta |
| Oferta y precio (o "desde") si el anuncio los mencionó | Evitar sorpresas | Precio escondido |
| Prueba breve (★ y nº de reseñas, logos, cifra) | Credibilidad inmediata | Prueba al final de la página |
| CTA visible (sticky en móvil) | Acción sin buscar | CTA bajo el pliegue |

### 3.2 Cuerpo (en orden de objeciones)

Mecanismo/cómo funciona → prueba específica (reseñas con contexto, UGC, antes/después dentro de la política) → objeciones principales con respuesta (precio por uso, compatibilidad, tallas, plazos) → garantía o riesgo invertido → FAQ → CTA repetido. Meta (2022) insiste en "answer common questions", fichas de especificaciones, medidas y fotos de uso real (S03-086). **[OFFICIAL META]** (antiguo) + **[STRONG INFERENCE]**

### 3.3 ¿Una página o varias?

| Situación | Recomendación |
|---|---|
| 1 producto, 1–2 ángulos similares | 1 PDP o landing bien hecha + bloques por objeción |
| Varios ángulos o personas muy distintos (03) | 1 landing por gran ángulo o nivel de awareness (3–5), o cabecera dinámica por UTM |
| Awareness baja (unaware/problem aware) | Advertorial, listicle o página educativa antes de la PDP |
| Most aware / retargeting | PDP o checkout directo con la oferta |
| Catálogo amplio | PDP/colección; valorar Optimize website destination (sección 6) con test |

Evidencia: no hay estudios públicos de Meta que cuantifiquen páginas por ángulo frente a página única. Es **[STRONG INFERENCE]** desde message match y awareness. Mídelo con test (sección 8).

## 4. Lead gen y high-ticket: formularios web, aplicaciones, calendario y VSL

### 4.1 Web frente a Instant Form

- Meta ofrece desde nov-2025 campañas híbridas **web + instant form** en las que Meta decide quién ve cada opción, y value rules por ubicación de conversión (Jon Loomer). También el **browser add-on de Instant Form**: tu web en el in-app browser con un botón persistente que abre un Instant Form. **[EMPIRICAL]** (S03-099) — el área 05 cubre la elección y la calidad (qualified leads con CAPI desde abr-2026).
- Regla: el Instant Form maximiza volumen (autorrelleno); la web con formulario propio cualifica más y permite VSL, calendario y tracking propio. Decide por **coste por lead cualificado y cierre**, no por CPL.

### 4.2 Diseño del formulario web

| Decisión | Recomendación | Evidencia |
|---|---|---|
| Nº de campos | Los mínimos para contactar + 2–5 de cualificación que el equipo de ventas use de verdad | [STRONG INFERENCE]; los estudios de "menos campos = más leads" miden volumen, no calidad |
| Multi-step | Útil cuando hay muchas preguntas: empezar por preguntas fáciles y de cualificación y pedir los datos de contacto al final; barra de progreso | [EMPIRICAL] débil: tests publicados por vendors/agencias (p. ej., +52,9% multi-step vs +40,3% single-step frente a un control, ~1.100 visitas por variante); el "86%" atribuido a HubSpot no se ha podido verificar (S03-100) |
| Teléfono | Pedirlo si la venta es por llamada (y validarlo); en formatos de bajo compromiso, opcional | [STRONG INFERENCE] |
| Preguntas sensibles | No preguntar ingresos, deudas ni salud (políticas y protección de datos; área 08) | [OFFICIAL META] (área 08) |
| Autofill | `autocomplete` correcto para el autofill del in-app browser | [STRONG INFERENCE] apoyado en S03-079 |
| Cualificación explícita | Presupuesto mínimo, zona, plazo; descalifica con respeto | [STRONG INFERENCE]; reduce volumen y mejora el cierre (área 05) |

### 4.3 Calendario embebido y thank-you page

- **Calendario en la propia página de gracias o en el paso final** (Calendly, HubSpot, GHL…): convierte el lead en una cita en el momento de máxima intención. Meta permite además reservar citas dentro de Instant Forms desde jun-2026 (ver 00-ESTADO-ACTUAL; área 05). **[OFFICIAL META]** (para instant forms) / **[STRONG INFERENCE]** (web)
- **La thank-you page es una landing más**: confirma el siguiente paso (qué pasa, cuándo y quién llama), añade un vídeo corto de preparación y prueba social, y pide la confirmación de la cita (añadir al calendario, responder a un SMS/WhatsApp). Las cifras de "+X% de show rate" con vídeo de confirmación vienen de vendors sin metodología **[HYPOTHESIS]**. Lo que sí está respaldado por ensayos es que **los recordatorios reducen las ausencias**: en un A/B de mensajes con 161.587 pacientes, una redacción distinta del recordatorio bajó el no-show del 21,1% al 14,2%, y los meta-análisis sanitarios encuentran mejoras de asistencia con recordatorios por SMS. **[EMPIRICAL]** (contexto sanitario; transferible como principio) (S03-101)
- **Velocidad de respuesta**: contactar en <5–60 min (ver 09 §TL;DR, HBR). Una landing excelente con un lead que nadie llama no sirve.

### 4.4 Páginas VSL (high-ticket)

- **Estructura habitual:** titular que repite la promesa del anuncio → vídeo (VSL) con mecanismo, prueba y oferta → CTA a aplicación o calendario → prueba (casos, testimonios) → FAQ/objeciones → CTA.
- **Métricas propias:** % que reproduce el VSL, retención (25/50/75%), clic en CTA, inicio y fin de la aplicación, citas, show rate y cierre.
- **Evidencia:** las afirmaciones de que el VSL filtra mejor son de practicantes y vendors **[HYPOTHESIS]**. Tiene lógica en mercados de sofisticación alta (03), donde el mecanismo y la prueba necesitan tiempo. Testea VSL frente a página escrita larga con la misma oferta si el tráfico lo permite (sección 8).
- **In-app browser:** vídeo con subtítulos, que arranque rápido (no 50 MB) y con el CTA visible sin terminar el vídeo.

## 5. Checkout e-commerce desde Meta

### 5.1 Datos de referencia (Baymard)

- **Abandono medio de carrito: 70,22%** (50 estudios; actualizado el 22-sep-2025). Motivos en el checkout (EE. UU., excluyendo "solo miraba", que es el 42%): costes extra 40%; entrega lenta 20%; desconfianza con la tarjeta 19%; creación de cuenta obligatoria 18%; checkout largo o complicado 17%; errores de la web 17%; devoluciones 13%; coste total no visible por adelantado 12%; tarjeta rechazada 10%; pocos métodos de pago 9%. **[EMPIRICAL]** (S03-091)
- **Campos:** media de 11,3 campos en 2024 (12,7 en 2019) y 5,1 pasos; "most sites need only 8 form fields". Recomendaciones: campo único de nombre completo, ocultar "dirección línea 2", el cupón y la facturación separada tras un enlace, y ofrecer la creación de cuenta al final. **[EMPIRICAL]** (S03-092)

### 5.2 Pagos exprés

- **Stripe:** ofrecer Apple Pay se asoció a +22,3% de conversión y +22,5% de ingresos en checkouts elegibles, y mostrarlo antes en el flujo (Express Checkout Element) a ~2x de conversión en otro estudio. En una charla de 2024 un científico de datos de Stripe citó +10% en un A/B. Son datos del proveedor. **[EMPIRICAL]** (S03-102)
- **Shop Pay:** Shopify cita un checkout-to-order rate 1,72x superior (10.000 grandes comercios) y "hasta +50%" frente al checkout de invitado (estudio de consultora sin nombre). Son datos del proveedor. **[EMPIRICAL]** baja (S03-103)
- **Dentro del in-app browser** el contexto de pago es distinto (1.2–1.3): Meta puede ofrecer autofill de pago y un "faster checkout" si detecta cuentas de Shopify, Stripe, PayPal o Click-to-Pay. La disponibilidad de Apple Pay está sin verificar. **Hay que probarlo en el móvil, dentro de las apps.** **[OFFICIAL META]** + **[HYPOTHESIS]**
- **Checkout dentro de Meta:** el checkout nativo de Shops se ha retirado (ver 00-ESTADO-ACTUAL). En 2026 hay tests de checkout en Messenger (Business Agent + Shopify) y en Meta AI/Muse (Shop Pay, Stripe, PayPal). **[EMPIRICAL]** (S03-105; área 06)

### 5.3 Reglas de checkout para tráfico de Meta

1. **Costes totales visibles antes del checkout** (envío, impuestos, umbral de envío gratis en PDP y carrito).
2. **Checkout de invitado** por defecto; cuenta opcional al final.
3. **Botones exprés arriba** del formulario (los que funcionen en el in-app browser).
4. **≤8 campos** visibles por defecto; autocompletado de dirección.
5. **Confianza**: política de devoluciones clara, contacto visible, sellos reales, reseñas cerca del botón de compra.
6. **Recuperación**: captura temprana del email en el checkout para recuperar carritos (con consentimiento).
7. **Velocidad del checkout** (scripts mínimos) y prueba real en el in-app browser.

## 6. Funciones de Meta relacionadas con el destino (2025-2026)

| Función | Qué hace | Por defecto | Riesgo | Recomendación | Fuente |
|---|---|---|---|---|---|
| **Optimize website destination** | Meta decide a qué URL de tu web envía a cada persona (home, producto, colección, otra) | Puede venir ON (Ventas + web + imagen/vídeo único) | Rompe el message match y los tests de landing; dificulta el análisis por página | OFF en tests y en landings específicas por ángulo; probar ON con holdout en e-commerce de catálogo amplio | Help Center (S03-087) [OFFICIAL META]; Loomer: aparece desde jul-2025 |
| **Product browsing** | Antes de tu web, muestra una experiencia de navegación de productos y ofertas dentro de FB/IG | Puede venir ON; avisos de activación en anuncios existentes desde ~28-oct-2026 salvo opt-out | El clic aterriza en el catálogo, no en la página diseñada para el ángulo; cambia el formato | Opt-out en tests y en anuncios de ángulo específico; probar en un ad set con holdout | Help Center (S03-090); default oct-2026 [EMPIRICAL] (S03-105) |
| **Shops (destino)** | Envía a la web o a la shop de FB/IG según predicción | — | Funciones de Shops y checkout retiradas en parte | Solo si hay shop activa y tiene sentido | Help Center (S03-106) |
| **Browser add-ons** (llamada, WhatsApp/Messenger/IG Direct, Instant Form) | Tu web en el in-app browser con un footer/botón de Meta para llamar, escribir o abrir un formulario | Opcional | Desvía conversiones fuera de la web (y de su medición); útil en servicios locales | ON en lead gen local y servicios con venta por conversación; medir conversaciones y llamadas como conversiones | Help Center (S03-107), developers (S03-094) |
| **Site links** | 3–20 enlaces extra bajo el anuncio (solo Feed de FB/IG en móvil); se abren en el in-app browser; pueden generarse automáticamente desde tu web | Sugeridos automáticamente | Dispersan el clic y la congruencia | OFF en landings por ángulo; probar en e-commerce con categorías claras | Help Center (S03-089) |
| **Show spotlights / Reveal details over time / Show summaries (AI)** | Muestran en el propio anuncio texto e imágenes de tu web o un resumen generado con IA | "May be turned on by default" | El anuncio muestra contenido de tu web que no elegiste | Revisar previews; OFF si la web tiene claims o precios que no deben aparecer fuera de contexto | Help Center Advantage+ creative (S03-090) |
| **Instant Experience** | Destino a pantalla completa dentro de Meta que "loads nearly instantaneously"; no soportado en Stories de FB | Opcional | Paso adicional antes de la web; medición propia | Útil para catálogos/colecciones y marcas con web lenta; test frente a la web | Developers (S03-109) |
| **Landing generada por IA (test)** | "We'll use AI to generate a visual landing page from your website… people who tap your ad may see this instead of your website" | Test tras el interruptor "test new AI generation features"; <5% de impresiones | Página no aprobada por el anunciante; message match y compliance | Desactivar el interruptor salvo que se quiera probar a conciencia | Jon Loomer vía AdMakeAI (S03-110) [EMPIRICAL] |
| **LPV optimization** | Optimiza a quien hace clic **y** carga la web | — | Trae tráfico que carga, no que compra | Solo si no hay volumen de conversión (≈50/semana) o en campañas de tráfico con propósito claro | Help Center (S03-083, S03-095) |
| **Web + Instant Form en un mismo anuncio** | Meta decide quién ve la web y quién el formulario | Opcional | Mezcla calidades de lead | Medir la calidad por ubicación en CRM; value rules por ubicación | Loomer (S03-099) |

**Detalle:** desde marzo de 2026 los anuncios de media única y las colecciones de catálogo en el Feed de Facebook **no muestran la URL** en el pie del anuncio (Help Center, S03-107). El dominio deja de ser una señal visible de confianza en el anuncio, así que la landing tiene que generar confianza por sí sola. **[OFFICIAL META]**

**Política recomendada:** en cualquier test de landing o de creatividad, documentar y fijar las "Personalized destinations" y las mejoras que tocan el destino; revisar los anuncios duplicados (algunos ajustes se reactivan al duplicar, según reportes de practicantes, S03-105).

## 7. ¿Problema de anuncio o de conversión? Diagnóstico con métricas

| Patrón | Diagnóstico probable | Acción | NO hacer |
|---|---|---|---|
| Hook/CTR bajos frente a la cuenta en algunos anuncios; LPV/clic y CVR normales | Anuncio | Iterar o crear conceptos (02, 05) | Tocar la landing |
| CTR normal, **LPV/outbound bajo** (p. ej. <70–80%) | Técnico: velocidad, redirecciones, consentimiento, errores en el in-app browser | Auditoría técnica (§2.4) | Producir más creatividades |
| CTR normal, LPV normal, **tiempo en página muy bajo / scroll mínimo** en todos los anuncios | Message match roto o promesa del anuncio que la página no confirma | Alinear el primer viewport con el ángulo | Culpar a la audiencia |
| CTR normal, LPV y tiempo normales, **ATC/IC (o inicio de formulario) bajo** | Oferta, precio, prueba u objeciones sin resolver en la página | Test de landing u oferta (09) | Más hooks |
| ATC/IC normales, **compra o envío de formulario bajos** | Checkout o formulario: costes, campos, pago, errores en el webview | Baymard §5; prueba en el in-app browser | Cambiar creatividades |
| La misma landing convierte bien con **email/marca/búsqueda** y mal con Meta | Intención o congruencia del tráfico de Meta (nivel de awareness), no un fallo técnico de la página | Página por ángulo/awareness; advertorial para tráfico frío | Concluir que "Meta no funciona" sin revisar la congruencia |
| Convierte mucho peor en **in-app** que en navegador del sistema (segmentado por user agent) | Fricción específica del webview (login, pago, cookies) | Checkout de invitado, métodos exprés que funcionen, sin login social obligatorio | Forzar la salida del webview sin medirlo |
| CVR cae en **todos** los canales a la vez | Web, stock, precio o tracking | Revisar la web y el backend (área 04) | Tocar campañas |
| Lead gen: CPL bueno, calidad o cierre malos | Formulario sin fricción ni cualificación o promesa que atrae a la persona equivocada | Cualificación en landing, formulario y copy (área 05) | Bajar más el CPL |

**Cuándo NO producir más creatividades:** cuando la caída está después del LPV y aparece **en todos los conceptos y ángulos a la vez**. Ahí un hook nuevo no cambia el resultado; lo cambian la página, la oferta o el checkout. **[STRONG INFERENCE]**, coherente con 09 y con el área 13 (07-framework-diagnóstico).

**Comparación entre canales:** los benchmarks públicos de CVR por canal (paid social frente a search o email) son contradictorios (unos sitúan paid social en 0,9–2,1% y otros, como ThoughtMetric, en niveles similares a Google Ads, S03-114). Lo útil es comparar **tu** CVR por canal en la **misma** landing y en el mismo periodo. **[EMPIRICAL]** sobre la contradicción.

## 8. CRO con poco tráfico

### 8.1 Qué se puede testear con potencia

Visitantes **por variante** para detectar una mejora relativa de la CVR (α=0,05 bilateral, potencia 80%; cálculo propio):

| CVR base | +10% | +20% | +30% | +50% |
|---|---|---|---|---|
| 1% | ~163.000 | ~42.700 | ~19.800 | ~7.750 |
| 2% | ~80.700 | ~21.100 | ~9.800 | ~3.800 |
| 3% | ~53.200 | ~13.900 | ~6.450 | ~2.500 |
| 5% | ~31.200 | ~8.150 | ~3.800 | ~1.470 |
| 10% (p. ej. lead gen) | ~14.750 | ~3.850 | ~1.770 | ~690 |
| 20% (p. ej. opt-in) | ~6.500 | ~1.700 | ~770 | ~290 |

**Implicaciones [STRONG INFERENCE]:**
- Con 5.000 visitas al mes y una CVR del 2%, solo es razonable testear cambios que puedan **duplicar** o mejorar >50% la conversión: oferta, estructura de página, promesa principal, formulario, checkout. Los botones de color no.
- Usar **métricas intermedias con más eventos** (clic en el CTA, inicio del formulario, ATC) para cambios pequeños, siempre vigilando que la conversión final no empeore.
- **Fijar el tamaño de muestra o el periodo antes** y no parar al primer "significativo": mirar el test repetidamente infla los falsos positivos (Evan Miller: diez miradas convierten un 1% nominal en ~5%; simulaciones de terceros cifran en ~25–30% el error con miradas diarias durante cuatro semanas a α=0,05). Si hace falta mirar, usar métodos secuenciales diseñados para ello. **[EMPIRICAL]** (S03-093)

### 8.2 Diseños posibles según el tráfico

| Tráfico/mes a la landing | Diseño | Notas |
|---|---|---|
| >50.000 | A/B clásico con herramienta (VWO, Optimizely, Convert, AB Tasty o la de la plataforma de e-commerce) | Duración en semanas completas (≥2) |
| 10.000–50.000 | A/B solo de cambios grandes; métricas intermedias; tests secuenciales | Evitar tests multivariantes |
| <10.000 | Cambios grandes basados en investigación cualitativa + **pre/post** con controles (mismo periodo del año anterior, otras fuentes de tráfico como control, estabilidad de campañas) | Asumir que es evidencia débil; repetir si se puede |
| Split desde Meta | A/B de Meta (Experiments) o dos anuncios idénticos con URLs distintas en celdas separadas | Útil para que el tráfico sea comparable; medir conversión en backend |

### 8.3 Investigación cualitativa (la que más rinde con poco tráfico)

- **Grabaciones de sesión y heatmaps** (p. ej., Microsoft Clarity, gratuito: heatmaps, grabaciones, rage/dead clicks e integración con GA4, según fuentes de terceros): ver dónde se atascan los usuarios **del in-app browser** (filtrando por user agent). **[EMPIRICAL]** (S03-111)
- **Encuesta en página o post-compra**: "¿Qué casi te impide comprar?", "¿Qué te faltaba saber?".
- **Análisis de formularios** (campos donde se abandona).
- **Revisión de 20 grabaciones de Meta** por semana en lanzamientos.
- **Test de 5 segundos** con 5–10 personas del público objetivo: "¿qué vende esta página y para quién es?".

### 8.4 Heurísticas de mayor impacto (por orden de prioridad típico)

1. **Oferta y riesgo invertido** visibles (09).
2. **Message match** del primer viewport con el anuncio.
3. **Velocidad** móvil en el in-app browser.
4. **Prueba** específica cerca del CTA.
5. **Fricción del formulario o checkout** (campos, cuenta, costes visibles, pago exprés).
6. **Objeciones** respondidas en la página (FAQ real de ventas y soporte).
7. **CTA** claro y sticky.

Es una priorización de criterio, no medida: **[STRONG INFERENCE]**, alineada con Baymard (checkout) y con la guía de Meta (2022).

### 8.5 Cómo no confundir ruido con mejora

- Comparar **semanas completas** y evitar cambios simultáneos en campañas (presupuesto, creatividades) durante el test de landing.
- Mirar el **intervalo**, no solo el punto: con 40 conversiones por variante, una diferencia del 25% es compatible con cero.
- **Regresión a la media**: la página que "peor iba" mejorará algo sola.
- **Estacionalidad y promociones**: no comparar un pre de BFCM con un post de enero.
- **Cambios de atribución** (mar-2026) al comparar con periodos anteriores.
- Confirmar los ganadores con un **segundo periodo** o un holdout pequeño.

## 9. Checklists por tipo de negocio

### 9.1 E-commerce

- [ ] Landing/PDP específica del ángulo del anuncio (o colección coherente); Optimize website destination y product browsing **decididos a propósito** (OFF en tests)
- [ ] Primer viewport: promesa del anuncio, producto como en el anuncio, precio/oferta, ★ y nº de reseñas, CTA sticky
- [ ] LCP ≤2,5 s en campo; probado en IG y FB (iOS y Android)
- [ ] Sin pop-ups de entrada; banner de consentimiento compacto
- [ ] Costes de envío, umbral de envío gratis y plazos visibles en la PDP
- [ ] Checkout de invitado; ≤8 campos; botones exprés arriba (verificados en el in-app browser)
- [ ] Política de devoluciones y contacto visibles; reseñas cerca del botón
- [ ] Pixel + CAPI deduplicados; UTMs; segmentación por user agent en analítica
- [ ] Clarity o equivalente activo; encuesta post-compra "¿qué casi te frena?"

### 9.2 Lead gen local (clínicas, reformas, servicios)

- [ ] Página por servicio y zona, que repite la promesa y la zona del anuncio
- [ ] Teléfono clicable y WhatsApp (browser add-on o botón propio); horario visible
- [ ] Formulario de 4–7 campos con 2–3 preguntas de cualificación (zona, servicio, plazo); `autocomplete` correcto
- [ ] Prueba local: reseñas de Google, fotos reales del equipo y del local, casos de la zona
- [ ] Thank-you page con siguiente paso, plazo de llamada y calendario si aplica
- [ ] SLA de contacto <5–15 min en horario; recordatorios de cita (SMS/WhatsApp)
- [ ] Calidad del lead por anuncio y ubicación medida en CRM y devuelta por CAPI (área 05)

### 9.3 High-ticket (coaching, B2B, formación cara, servicios premium)

- [ ] Página VSL o larga escrita que repite la promesa y el mecanismo del anuncio; vídeo subtitulado y ligero
- [ ] Aplicación con cualificación (presupuesto, situación, urgencia), en multi-step si son >5 preguntas
- [ ] Calendario embebido tras la aplicación (solo para cualificados, si se puede filtrar)
- [ ] Thank-you page con vídeo de preparación, qué esperar, prueba social y confirmación de la cita
- [ ] Recordatorios (24 h + 1 h) y llamada de confirmación; seguimiento de no-shows en minutos
- [ ] Métricas por cohorte: aplicación → cualificado → cita → show → cierre, por anuncio y ángulo
- [ ] Revisión legal de claims de ingresos o resultados (área 08)

## Errores frecuentes

- Diseñar y aprobar la landing en el escritorio y no probarla nunca dentro de Instagram.
- Exigir login, crear cuenta o login social en el webview.
- Enviar todos los ángulos a la home.
- Dejar Optimize website destination, product browsing o site links activados durante un test de landing.
- Pop-up de descuento o newsletter nada más cargar (además, atributo de baja calidad para Meta).
- Leer "más leads" en un formulario más corto como éxito sin mirar la calidad.
- Parar un test de landing al tercer día porque "ya es significativo".
- Producir más creatividades cuando la fuga está en el checkout.
- Confiar en redirects "mágicos" al navegador del sistema sin medir el efecto en la conversión y la atribución.

## Preguntas abiertas

- ¿Qué métodos de pago exprés aparecen realmente en el in-app browser de IG y FB en 2026 (Apple Pay, Google Pay, Shop Pay, PayPal)? Sin documentación pública: verificar en dispositivos reales.
- Magnitud real de la diferencia de CVR entre in-app browser y navegador del sistema: no hay datos independientes publicados.
- Alcance y fecha exacta del default de product browsing (~28-oct-2026) y del test de landing generada por IA: sin documentación pública de Meta.
- ¿Cómo pondera Meta el bounce rate y el dwell time en la calidad del anuncio? Meta los lista como señales, pero no publica pesos ni umbrales.
- Efecto de Meta AI dentro del in-app browser (resúmenes de página) en la conversión. **[HYPOTHESIS]**: las páginas con información clara y estructurada se resumirán mejor.

## Fuentes clave

- [Meta Help — About the in-app browser for Facebook and Instagram](https://www.facebook.com/business/help/206578174518231) — vigente 2026 — meta-oficial
- [Meta Help (Meta Pay) — How we use autofill](https://www.meta.com/help/meta-pay/1896636927418202/) — vigente — meta-oficial
- [Meta Help — Best practices to improve ad quality and performance](https://www.facebook.com/business/help/1767120243598011) — vigente 2026 — meta-oficial
- [Meta Help — About ad quality](https://www.facebook.com/business/help/423781975167984) — vigente 2026 — meta-oficial
- [Meta Help — Website landing page views](https://www.facebook.com/business/help/361750134220832) — vigente 2026 — meta-oficial
- [Meta Help — About landing page view optimization](https://www.facebook.com/business/help/417293491972212) — 2025-2026 — meta-oficial
- [Meta Help — Best practices for landing page view performance goals](https://www.facebook.com/business/help/203012060587398) — vigente — meta-oficial
- [Meta Help — Link clicks vs landing page views](https://www.facebook.com/business/help/172641445757289) — vigente — meta-oficial
- [Meta Help — About personalized destinations](https://www.facebook.com/business/help/1842103166667481) — vigente 2026 — meta-oficial
- [Meta Help — Optimize website destination](https://www.facebook.com/business/help/1261275665394096) — vigente 2026 — meta-oficial
- [Meta Help — Call add-ons / browser add-ons](https://www.facebook.com/business/help/753973205286415) — vigente 2026 — meta-oficial
- [Meta Help — Site links](https://www.facebook.com/business/help/1127018781828932) — vigente 2026 — meta-oficial
- [Meta Help — About Advantage+ creative (product browsing, spotlights, summaries)](https://www.facebook.com/business/help/297506218282224) — vigente 2026 — meta-oficial
- [Meta Developers — Website ads that click to message](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/website-ads-click-to-message.md) — vigente — meta-developers
- [Meta Developers — Instant Experiences](https://developers.facebook.com/documentation/ads-commerce/marketing-api/guides/instant-experiences.md) — vigente — meta-developers
- [Search Engine Journal — Meta landing page whitepaper](https://www.searchenginejournal.com/meta-conversion-whitepaper/447416/) — 2022-04-26 — prensa (sobre guía Meta)
- [MarTech — Facebook pressures advertisers to cut mobile page load times](https://martech.org/facebook-pressures-advertisers-cut-mobile-page-load-speeds-itll-cut-reach/) — 2017 — prensa
- [web.dev — Defining Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds) — vigente — Google
- [web.dev — Vodafone case study](https://web.dev/case-studies/vodafone) y [Milliseconds make millions](https://web.dev/case-studies/milliseconds-make-millions) — Google
- [Baymard — Cart abandonment rate](https://baymard.com/lists/cart-abandonment-rate) — 2025-09-22 — investigación UX
- [Baymard — Checkout form fields](https://baymard.com/blog/checkout-flow-average-form-fields) — 2024-06-26 — investigación UX
- [Stripe — Testing the conversion impact of 50+ payment methods](https://stripe.com/blog/testing-the-conversion-impact-of-50-plus-global-payment-methods) — vendor
- [Evan Miller — How Not To Run an A/B Test](https://www.evanmiller.org/how-not-to-run-an-ab-test.html) — 2010 — practitioner (estadística)
- [AdsUploader — Meta Ads updates (October 2026)](https://adsuploader.com/blog/meta-ads-updates) — 2026-10 — vendor
- [AdMakeAI — Meta Ads updates October 2026 (test de landing con IA)](https://admakeai.com/blog/meta-ads-updates-october-2026) — 2026-10 — vendor
- [Jon Loomer — 83 changes to Meta advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — 2025-12 — practitioner
- Ledger: `../fuentes/ledger-03-creatividad.md` (S03-078 a S03-114)
