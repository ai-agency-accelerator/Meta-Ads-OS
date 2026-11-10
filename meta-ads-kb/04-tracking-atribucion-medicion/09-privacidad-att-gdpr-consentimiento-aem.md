# Privacidad y señal: ATT, AEM, GDPR/ePrivacy, consentimiento, LDU, categorías sensibles y "anuncios menos personalizados"

> Última verificación: 2026-10-16 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A04 (agente) · Ámbito: impacto publicitario y técnico de las restricciones de privacidad sobre la medición en Meta. **No es consejo jurídico**: describe cómo se implementa y qué efecto tiene; las decisiones de base legal corresponden al responsable del tratamiento y su asesoría (remitir a AEPD/EDPB, textos oficiales y términos de Meta).

## TL;DR

- **AEM (Aggregated Event Measurement) ya no requiere configurar 8 eventos ni verificar dominio para web desde mayo de 2023** (anuncio de Meta del 15-may-2023: fin de priorización, value sets, selección de dominio de conversión y pestaña AEM). Los blogs que lo datan en "junio 2025" muy probablemente describen el final del despliegue o se equivocan. Algunas páginas legadas de Meta aún mencionan "8 eventos". [OFFICIAL META vía practitioner] ([S04-069], [S04-070]) + [CONTESTED] (fecha) + [OUTDATED] (la configuración de 8 eventos para web)
- **ATT (iOS ≥ 14.5):** opt-in medio global ~38 % en Q1-2026 según Adjust (35 % en Q1-2025); otras fuentes dan ~50 % (AppsFlyer, vía secundaria). Para apps, Meta mide con SKAdNetwork/AdAttributionKit o con AEM (elección por campaña). Para web, los usuarios iOS que rechazan ATT en apps de Meta siguen pudiendo medirse de forma agregada/modelada; los informes de esos usuarios llegan con retraso (hasta ~72 h según Meta/practicantes). [EMPIRICAL] ([S04-076]) + [OFFICIAL META] (AEM apps, [S04-043], [S04-071])
- **UE/EEE:** el Pixel y CAPI necesitan una base legal; con consentimiento como base, usa `fbq('consent','revoke'|'grant')` y filtra CAPI en servidor. **Meta no ofrece un "consent mode" con modelado equivalente al de Google**: si no hay consentimiento, no envíes; la pérdida se ve como menos conversiones atribuidas. [OFFICIAL META] ([S04-040]) + [STRONG INFERENCE]
- **EE. UU.: Limited Data Use (LDU)** disponible en 14 estados a 2026 (incl. Minnesota 2-jun-2025, Maryland 9-sep-2025, Rhode Island 17-nov-2025). Activarlo limita retargeting y medición. [OFFICIAL META] ([S04-067])
- **Categorías sensibles (2025–2026):** Meta clasifica fuentes de datos (desde inicios de 2025) y aplica tres niveles: *core setup* (elimina todo lo que va tras el dominio en URLs y los parámetros custom), restricción de eventos estándar de mitad/final de embudo, y bloqueo total en algunas regiones; afecta igual a Pixel y CAPI. Desde **2-sep-2025**, custom conversions y custom audiences "flagged" (p. ej. condiciones de salud o situación financiera) no se pueden usar en campañas nuevas y una custom conversion flagged deja de emparejarse. [OFFICIAL META] (flagged, [S04-095], [S04-096]) + [EMPIRICAL] (niveles, [S04-082], [S04-083])
- **"Anuncios menos personalizados" (LPA, UE):** lanzados en nov-2024; desde **enero de 2026**, por el acuerdo con la Comisión Europea bajo la DMA, los usuarios de la UE eligen entre compartir todos sus datos (anuncios totalmente personalizados) o compartir menos (personalización limitada). Meta afirma que LPA usa ~90 % menos datos y que en feedback temprano generó −70 % conversiones onsite y −61 % offsite. No hay datos públicos de adopción. [OFFICIAL META] ([S04-041]) + [EMPIRICAL — prensa] ([S04-042])
- **Safari/iOS:** cookies JS capadas a 7 días (24 h tras link decoration desde dominios rastreadores), Advanced Fingerprinting Protection por defecto en todo Safari desde iOS 26 y eliminación de parámetros en Mail/Mensajes/navegación privada. Efecto: menos `fbc` persistente → menos atribución de clic. [OFFICIAL WebKit] ([S04-073], [S04-074]) + [EMPIRICAL] ([S04-075])

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **iOS 27.2 se publicó el 26-oct-2026** (build 24B119) con el aviso ATT alternativo en la UE, obligatorio en FR, DE, IT, PL y RO, y re-petición anual. **[EMPIRICAL]** (la nota de Apple no se pudo leer)
> - La **medición en el dispositivo** de Meta (12-nov-2026) no está activa para personas en la UE ni en el Reino Unido. **[OFFICIAL META]**
> - Fuentes: S10-105, S10-130 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

## 1. ATT y AEM

### 1.1 Qué cambió con ATT
- Desde iOS 14.5 (abr-2021), las apps necesitan permiso ATT para acceder al IDFA y rastrear entre apps/webs de otras empresas. Meta respondió con AEM (web y app), SKAdNetwork para apps, reporting por fecha de conversión para eventos offsite y modelado estadístico. [OFFICIAL META] ([S04-068], [S04-043])
- Opt-in ATT 2025–2026: ~35 % (Adjust Q1-2025) → ~38 % (Adjust Q1-2026); cifras muy distintas según panel y vertical. [EMPIRICAL] ([S04-076])

### 1.2 AEM hoy (web)
- **Qué es:** protocolo de Meta para medir eventos web y de app de personas en iOS 14.5+ que optaron por no ser rastreadas, de forma agregada. [OFFICIAL META] ([S04-043])
- **Qué ya no hace falta (desde 2023):** configurar/priorizar 8 eventos por dominio, value sets para optimizar por valor, verificar dominio "para configuración de eventos", elegir dominio de conversión en el anuncio. La verificación de dominio sigue recomendada para control de enlaces. [OFFICIAL META vía practitioner] ([S04-069], [S04-070])
- **Qué sigue implicando:** retrasos y agregación en el reporting de esos usuarios; resultados parcialmente modelados; breakdowns limitados para eventos offsite (Meta los fue restaurando). [OFFICIAL META] ([S04-068]) + [EMPIRICAL]
- **Contradicción documental:** la página de developers "AEM and Limitations of SKAdNetwork" todavía dice que AEM "limita dominios y apps a 8 eventos configurables" — es texto legado. [OUTDATED] ([S04-071])

### 1.3 AEM para apps
- Integración vía SDK de Meta (Universal Links/deep links pasados al SDK), elección `campaign_attribution = AEM` o `SKADNETWORK` por ad set en campañas iOS 14+. Detalle en `15-apps-sdk-skan-mmp.md`. [OFFICIAL META] ([S04-043], [S04-071])

## 2. UE/EEE: GDPR, ePrivacy, consentimiento (implementación, no asesoría)

### 2.1 Marco (descriptivo)
- La Directiva ePrivacy (art. 5.3) exige consentimiento para almacenar/leer información en el terminal salvo que sea estrictamente necesario; el GDPR exige base legal para el tratamiento posterior. En la práctica de mercado, los píxeles publicitarios en la UE se condicionan a consentimiento de marketing vía CMP. [STRONG INFERENCE] — confirma con tu DPO; consulta guías de la AEPD/EDPB.
- **CAPI y consentimiento:** que el dato viaje servidor-a-servidor no elimina la necesidad de base legal; el criterio conservador de mercado es aplicar a CAPI el mismo consentimiento que al Pixel. [STRONG INFERENCE]

### 2.2 Implementación con Meta
```js
// En cada página, antes de init:
fbq('consent', 'revoke');
fbq('init', 'PIXEL_ID');
fbq('track', 'PageView');
// Callback del CMP al aceptar marketing:
fbq('consent', 'grant');
```
- Documentado por Meta para GDPR: "You need to call revoke on every page". No se documenta si los eventos durante *revoke* se encolan. [OFFICIAL META] ([S04-040])
- **Shopify:** Customer Privacy API + web pixels aplican el consentimiento automáticamente (re-emiten eventos tras aceptar). [OFFICIAL Shopify] ([S04-032], [S04-033])
- **WooCommerce (oficial):** hold/release de señales para integrar CMPs y reenviar eventos encolados tras aceptar. [OFFICIAL META] ([S04-036])
- **sGTM:** el tag oficial de CAPI no comprueba consentimiento; el de Stape sí ofrece la opción. [OFFICIAL META] ([S04-081]) + [EMPIRICAL] ([S04-092])

### 2.3 GPC y opt-outs: el Pixel no los aplica solo
- Una auditoría (webXray, publicada por 404 Media, abr-2026) sobre > 7.000 webs accesibles desde California con Global Privacy Control activo afirmó que Meta "falló" en el 69 % de los casos (cookies publicitarias pese al opt-out, "sin comprobación de opt-out en el código"); Meta lo disputa y alega que ciertas implementaciones permiten a los sitios anular la señal. [CONTESTED] ([S04-114])
- Lectura técnica: el Pixel no implementa por sí mismo GPC ni el banner; la responsabilidad recae en la implementación del sitio (CMP, `fbq('consent')`, LDU, Shopify Customer Privacy API que sí aplica GPC en regiones opt-out). [STRONG INFERENCE] + [OFFICIAL Shopify] ([S04-032])

### 2.4 "AI enrichment" del Pixel (abril de 2026)
- El Pixel añade automáticamente contexto de página y producto (título, descripción, tipo de página, nombre/precio/moneda/disponibilidad, nombre y ubicación del negocio); se activa por defecto tras 30 días de aviso en Events Manager, con opción de desactivar categorías de datos. Excluido para fuentes con límites de datos (categorías especiales: financieros, empleo, salud, vivienda). Meta afirma que está diseñado para contexto de producto/negocio, no atributos sensibles del usuario. [EMPIRICAL — prensa que cita a Meta] ([S04-113])
- Implicación: revisa qué contenido de tus páginas podría acabar en eventos (p. ej. títulos de páginas de servicios sensibles) y decide si desactivarlo; documenta la decisión en el registro de tratamientos. [STRONG INFERENCE]

### 2.5 Impacto en medición
| Escenario | Efecto en Meta |
|---|---|
| Rechazo de cookies de marketing | Ni Pixel ni (si así lo decides) CAPI → conversión invisible para Meta; no hay modelado específico publicado para este caso |
| Aceptación tardía (tras la landing) | Si el CMP/plataforma re-emite eventos, se recupera parte; `fbclid` sigue en la URL de la landing solo si se capturó |
| Usuarios con LPA (UE) | Menos datos para personalización; Meta no documenta cómo afecta a la atribución de esos usuarios (no verificado) |

Consecuencia práctica: en la UE, la tasa de consentimiento es un multiplicador directo de las conversiones reportadas. Mide la tasa de aceptación (CMP) y úsala para explicar diferencias Meta vs backend. [STRONG INFERENCE]

## 3. EE. UU.: Limited Data Use

- Estados con LDU (Business Tools y Audience Network SDK): California, Colorado, Connecticut, Delaware, Florida, Montana, Nebraska, New Hampshire, New Jersey, Oregon, Texas, Minnesota (2-jun-2025), Maryland (9-sep-2025), Rhode Island (17-nov-2025). Customer List Custom Audiences: solo California. [OFFICIAL META] ([S04-067])
- Pixel: `fbq('dataProcessingOptions', ['LDU'], 0, 0)` (geolocaliza Meta) o `(['LDU'], 1, 1000)` (California). CAPI: `data_processing_options: ["LDU"]`, `data_processing_options_country: 1|0`, `data_processing_options_state: 1000…1013|0`. Array vacío = sin LDU explícito. [OFFICIAL META] ([S04-067])
- Efecto: "retargeting and measurement capabilities will be limited". [OFFICIAL META] ([S04-067])
- Nota: la página de *server event parameters* solo menciona el código 1000 (California): está desactualizada respecto a la página de Data Processing Options. [OUTDATED] ([S04-008] vs [S04-067])

## 4. Categorías sensibles: salud, bienestar, finanzas

### 4.1 Qué hace Meta (2025–2026)
| Nivel | Qué bloquea | Fuente |
|---|---|---|
| **Core setup** | URL más allá del dominio (rutas, query, UTMs) y parámetros custom; puede afectar a advanced matching automático, audiencias por URL y visibilidad en Events Manager (incluido Test Events) | [EMPIRICAL] ([S04-082], [S04-083]) |
| **Restricción de eventos estándar** | Eventos de mitad/final de embudo (Purchase, AddToCart, Lead, CompleteRegistration, Schedule, AddPaymentInfo…); suelen quedar PageView/ViewContent/Search | [EMPIRICAL] ([S04-083]) |
| **Restricción total** | Todo el envío de eventos de la fuente en ciertas regiones (Pixel y CAPI) | [EMPIRICAL] ([S04-082]) |
| **Custom conversions/audiences flagged** (desde 2-sep-2025) | No utilizables en nuevas campañas; custom conversion flagged deja de emparejarse; revisión solo en interfaces nativas | [OFFICIAL META] ([S04-095], [S04-096]) |

- La clasificación se ve en Events Manager > dataset > Settings > *Data source categories* (ruta según fuentes secundarias; puede variar). Se puede solicitar revisión. [EMPIRICAL] ([S04-083])
- **CAPI no evita las restricciones**: se aplican las mismas comprobaciones a Pixel y CAPI. [EMPIRICAL] ([S04-082])
- Contexto: acciones de la FTC (2023) contra BetterHelp y GoodRx por compartir datos de salud vía píxeles. [EMPIRICAL] ([S04-083])
- Además, desde ene-2025 la categoría especial de anuncios **Financial products and services** sustituye a `CREDIT` (restricciones de segmentación, no de tracking). [OFFICIAL META] ([S04-048])

### 4.2 Qué hacer (técnico)
- Nombres de eventos neutros (`Lead`, no `DepressionAppointmentBooked`); sin condiciones médicas o datos financieros en `content_name`, `content_category`, parámetros custom ni rutas de URL (`/tratamiento-ansiedad/` → considera rutas neutras).
- sGTM o backend como "filtro": eliminar query strings y parámetros sensibles antes de enviar a Meta. [EMPIRICAL] ([S04-082])
- Optimización sin eventos de fondo de embudo: eventos proxy neutros, CRM con etapas genéricas, y medición de negocio fuera de Meta (MMM/geo tests) — ver archivos 12–14.
- No es asesoramiento regulatorio (HIPAA, GDPR art. 9…): coordinar con legal.

## 5. "Anuncios menos personalizados" (LPA) y DMA

| Fecha | Hito |
|---|---|
| Nov-2024 | Meta lanza LPA en la UE (alternativa a la suscripción sin anuncios); anuncios basados en edad, género, ubicación y actividad en la sesión; anuncios no saltables para compensar | [EMPIRICAL — prensa] (Bloomberg/TechCrunch nov-2024) |
| Abr-2025 | La Comisión Europea declara no conforme el modelo "pay or consent" y multa con 200 M€ (DMA) | [OFFICIAL META] (10-Q, [S04-099]) |
| Jul-2025 | Meta afirma: LPA usa ~90 % menos datos; −70 % conversiones onsite, −61 % offsite en feedback temprano | [OFFICIAL META] ([S04-041]) |
| 8-dic-2025 | La Comisión anuncia que Meta ofrecerá desde enero de 2026 la elección de "compartir menos datos" | [EMPIRICAL — prensa] ([S04-042]) |
| Ene-2026 | Despliegue de la nueva elección en la UE; la Comisión monitoriza la adopción | [EMPIRICAL — prensa] ([S04-042]) |

Implicaciones (inferencias, sin datos públicos de adopción):
- Parte de la audiencia UE es menos segmentable y probablemente menos atribuible; los anuncios a esos usuarios se parecen más a medios contextuales. Esto **reduce el ROAS atribuido** sin que necesariamente cambie la incrementalidad real en la misma proporción. [HYPOTHESIS]
- Ads Manager no muestra qué proporción de tu audiencia UE está en LPA (afirmación de terceros; no verificado en documentación de Meta). [HYPOTHESIS]
- Medir UE con experimentos geo/holdout gana valor relativo. [STRONG INFERENCE]

## 6. Navegadores

- **Safari/WebKit:** 7 días para storage/cookies JS sin interacción; 24 h para cookies JS en landings con link decoration desde dominios clasificados; 7 días para cookies HTTP con CNAME/IP cloaking de terceros. [OFFICIAL WebKit] ([S04-073], [S04-074])
- **iOS 26:** Advanced Fingerprinting Protection activo por defecto en todo Safari; limita a scripts de fingerprinting conocidos leer query params y referrer; eliminación de parámetros de seguimiento documentada para Mail, Mensajes y navegación privada (en pestañas normales solo si el usuario lo activa para "All Browsing"). [EMPIRICAL] ([S04-075])
- **Ad blockers / Brave / Firefox ETP:** bloquean `connect.facebook.net` → solo CAPI llega. [EMPIRICAL]

## Implicaciones operativas

- **Hacemos:** inventario de consentimiento por región (tasa de aceptación), CAPI condicionado al mismo consentimiento, LDU para EE. UU. si el negocio lo requiere, auditoría de nombres de eventos/URLs en sectores sensibles, revisión de "Data source categories" y de custom conversions flagged.
- **Evitamos:** usar CAPI como "atajo" sin consentimiento; meter datos sensibles en parámetros; interpretar la caída de conversiones UE de 2026 solo como caída de rendimiento sin considerar LPA/consentimiento.
- **Umbral:** si la tasa de consentimiento de marketing < 60 % en la UE, espera infra-reporte relevante en Meta y apóyate en MMM/geo (archivo 13–14). [STRONG INFERENCE]

## Errores frecuentes

1. Configurar "8 eventos AEM" o verificar dominio pensando que es requisito de medición web en 2026. [OUTDATED]
2. Disparar el Pixel antes de que el CMP cargue (fuga sin consentimiento) o no dispararlo nunca tras aceptar (pérdida).
3. Creer que CAPI esquiva las restricciones de salud/finanzas.
4. Mantener custom conversions con nombres o reglas de URL que reflejan condiciones de salud (flag → dejan de recibir datos).

## Preguntas abiertas

- Adopción real de la opción "compartir menos datos" en la UE en 2026 y su efecto en atribución (no publicado).
- Si Meta modela conversiones de usuarios sin consentimiento en la UE (no documentado).
- Ruta exacta y texto oficial de "core setup" en el Business Help Center (no se pudo descargar la página oficial; descripción basada en fuentes secundarias concordantes).

## Fuentes clave

- [Meta Pixel — GDPR](https://developers.facebook.com/docs/meta-pixel/implementation/gdpr) — vigente — meta-developers (S04-040)
- [Data Processing Options for US Users](https://developers.facebook.com/documentation/ads-commerce/marketing-api/overview/data-processing-options) — vigente — meta-developers (S04-067)
- [Graph API v24 / flagged audiences & conversions](https://developers.facebook.com/blog/post/2025/10/08/introducing-graph-api-v24-and-marketing-api-v24/) — 2025-10-08 — meta-developers (S04-095)
- [Why the Commission's Decision Undermines the Goals of the DMA](https://about.fb.com/news/2025/07/why-the-commissions-decision-undermines-the-goals-of-the-dma/) — 2025-07-02 — meta-oficial (S04-041)
- [Meta's tweaked ad experience gets EU nod](https://www.siliconrepublic.com/business/meta-facebook-instagram-european-commission-ads-data-protection-digital-markets-act) — 2025-12-09 — prensa (S04-042)
- [Meta Announces Big Changes to Website Conversion Campaigns](https://www.jonloomer.com/meta-announces-big-changes-to-website-conversion-campaigns/) — 2023-05-16 — practitioner (S04-069)
- [Stape: Meta data sharing restrictions (healthcare)](https://stape.io/news/meta-data-sharing-restrictions-healthcare) — 2026-03 — vendor (S04-082)
- [WebKit Tracking Prevention](https://webkit.org/tracking-prevention/) — vigente — WebKit (S04-073)
- [Adjust 2026 mobile report](https://www.businesswire.com/news/home/20260218837408/en/Adjust-Mobile-App-Use-Grew-Globally-In-2025-With-Continued-Move-To-Multi-Platform) — 2026-02-18 — vendor (S04-076)

## Actualización (2026-10-16, agente principal): ATT en la UE con iOS 27.2

- **Qué**: Apple (Developer News, 16-sep-2026) introduce con iOS/iPadOS 27.2 una versión alternativa del aviso de ATT en la
  UE: botones "Allow" y "Reject" (desaparece "Ask App Not to Track" y la palabra "track"), formato de hoja completa con
  texto enriquecido y botón opcional de información adicional. En **Alemania, Francia, Italia, Polonia y Rumanía** es la
  única versión permitida. Los usuarios de la UE pueden volver a ver el aviso **un año después** de su última respuesta,
  aunque hubieran rechazado (no si desactivaron "permitir que las apps soliciten…"). El ajuste se renombra en la UE.
  **[OFFICIAL Apple]** ([Apple Developer News](https://developer.apple.com/news/?id=idsft9ai)); la re-pregunta anual
  procede de la documentación de la beta según prensa especializada → confirmar con la versión final.
- **Impacto esperado** **[STRONG INFERENCE]**: más usuarios iOS de la UE con ATT aceptado → más conversiones emparejadas y
  atribuidas en Meta sin que cambien las ventas reales. Anotar la fecha de llegada de iOS 27.2 a la audiencia y no comparar
  ROAS/CPA de plataforma a través de ella sin contrastar con backend.
- Fuente adicional de contexto: hilo de r/FacebookAds del 23-sep-2026 (vía Arctic Shift), ver 11/08 R11.
