# IA generativa en anuncios: qué formatos funcionan en B2B y SaaS, qué evidencia hay y cuándo hay que etiquetar

> Última verificación: 2026-11-10 · Autor: agente principal · Ámbito: elección de formato en consultoras, agencias de IA
> y automatización, B2B y SaaS; usos de la IA generativa en la pieza (edición, voz, lip-sync, clon, avatar); evidencia
> de rendimiento y sus límites; etiquetado de IA (Reglamento de IA de la UE, FTC, Nueva York, qué hace Meta y qué no);
> consentimientos. Base: informe «Vídeo IA para anuncios Meta» del 2026-11-09, con verificación independiente del
> 2026-11-10 contra fuentes primarias (cuando hay conflicto, manda la verificación). Las cifras de practicantes (Reddit,
> LinkedIn, YouTube) no se pudieron verificar: se citan como anécdotas. Las herramientas nativas de IA de Meta están en
> [14](14-herramientas-ia-creativa-meta.md); el catálogo general de formatos, en [04](04-formatos-y-estilos.md).
> **No es asesoría legal.**

## TL;DR

- **En B2B, consultoras y SaaS gana la prueba real:** fundador a cámara, demo del sistema, casos con cifras del cliente
  y estáticos. La IA sirve para **editar, variar y escalar** lo real, no para fingir personas. **[STRONG INFERENCE]**
- **Por anuncio gana lo humano; la IA gana por cartera** (más conceptos por el mismo dinero). En vídeo, más de 40
  cuentas dan al humano un CPA de 36,20 $ frente a 49,60 $; en estáticos, la IA gana (28,75 $ frente a 32,15 $).
  **[EMPIRICAL]** (anecdótico, sin auditar)
- **El avatar realista es el formato peor parado** (en el caso más duro, 0,4–0,6× el ROAS y 1,6–2,2× el CPM del UGC
  real) y en la UE tiene que llevar rótulo de IA, que le quita su única ventaja: parecer humano. **[STRONG INFERENCE]**
- **Los estáticos ganan peso**, pero los que «parecen IA» no funcionan; las fotos y capturas reales, sí. En B2B, la
  imagen sale a 136 $ de CPL frente a 225 $ del vídeo (Metadata). **[EMPIRICAL]**
- **Etiquetar no depende de Meta.** El art. 50 del Reglamento de IA obliga desde el 2026-08-02 a declarar los deepfakes
  (voz clonada, lip-sync que hace decir algo nuevo, clon digital, avatar realista) de forma visible desde la primera
  exposición. La etiqueta «AI info» de Meta va dentro de un menú y casi nunca salta en un vídeo reencodado: no te
  cubre. **[OFFICIAL — regulador]** + **[STRONG INFERENCE]**
- **Mide por coste por lead cualificado o por reunión**, no por hook rate: un hook del 38 % perdió dinero y uno del 16 %
  dio el mejor coste por compra. **[EMPIRICAL]** (anecdótico)

## 1. Respuesta corta

En B2B, consultoras y SaaS el comprador compra confianza, y la confianza la da la **prueba real**: el fundador
explicando un problema concreto, la demo del sistema funcionando con la interfaz real, un caso con cifras del cliente y
estáticos que enseñan el dolor y la prueba. Es lo que coinciden en recomendar los practicantes y lo que proponen como
«controles» para cualquier test de avatar en B2B: un operador real explicando el problema, una prueba de cliente y una
demo del mecanismo ([r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1vsrt1q/realistic_ai_ugc_meta_ads_for_b2b/)).
En SaaS, «a simple screen recording from the founder usually converts better»
([r/SaaS](https://www.reddit.com/r/SaaS/comments/1slbibh/would_you_run_this_aimade_or_record_one_yourself/)).
**[EMPIRICAL]** (anecdótico)

La IA entra **detrás de la cámara**: montaje (silencios, subtítulos, encuadre), variantes de hook y CTA, estáticos
animados, b-roll de contexto sin caras, doblaje. Lo que no hace nunca es **fingir personas**: un cliente, un experto o
un empleado que no existen, o un fundador que dice algo que no grabó sin decirlo. Para una consultora que vende IA es
doblemente caro: además de engañoso y, en la UE, ilegal sin rótulo, destruye la confianza que vende. **[STRONG INFERENCE]**

«Realistic isn't the same as credible… a synthetic spokesperson making an expert claim may weaken the exact trust
needed for a large purchase» ([r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1vsrt1q/realistic_ai_ugc_meta_ads_for_b2b/)).

## 2. Ranking de opciones, de mejor a peor

Para B2B, consultoras y SaaS. El orden combina la evidencia de §3, el coste y el riesgo legal de §5.
**[STRONG INFERENCE]** En ecommerce DTC pesan más el híbrido (hook con IA + metraje real) y la voz en off con IA sobre
b-roll real (§3.1 y §3.9): este ranking no se traslada tal cual.

| # | Opción | Coste aproximado por pieza | ¿Etiqueta de IA? | Para qué y límites |
|---|---|---|---|---|
| 1 | **Fundador a cámara** (móvil + cutkit) | ≈0 $ de API: cutkit monta en local (silencios, hook, subtítulos con whisper.cpp, −14 LUFS, 9:16 y 4:5). El coste es el tiempo del fundador | No: persona real con su voz; la IA solo edita | El formato con más respaldo en B2B. Un problema concreto para un rol concreto. En ofertas basadas en expertise, el vídeo del fundador sigue ganando en frío (Heath) |
| 2 | **Caso o testimonio real con cifras** | ≈0 $ de API. El coste es conseguir el permiso y grabar | No | La prueba más fuerte en B2B. Cifras del cliente, contadas («pasó de… a…»), no prometidas al espectador; permiso firmado (`/casos-y-creadores`) |
| 3 | **Estáticos y carruseles** (dolor + prueba, antes/después del proceso, captura de resultado) | ≈0 $ con plantilla y render local; ≈0,03–0,07 $ por imagen si generas un fondo con IA | No, si la imagen es real (captura, gráfico, foto); zona gris si generas una escena realista (§5) | El formato más barato para testear ángulos y, en B2B, compite en CPL con el vídeo. Qué estáticos funcionan: §4 |
| 4 | **Demo del sistema con la voz real del fundador, sin cara** | ≈0 $: grabación de pantalla + cutkit | No | Vuelve tangible lo abstracto. La interfaz siempre real y con datos ficticios: «the AI clip creates context; the recorded UI provides truth» ([Cliprise](https://www.cliprise.app/learn/workflows/marketing/ai-saas-product-demo-video-workflow)) |
| 5 | **Estático animado o antes/después animado** (cutkit avanzado con HyperFrames) | ≈0 $: HyperFrames es Apache-2.0 y no cobra por render. Necesita Node 20+ y el extra `avanzado` de cutkit | No (gráficos y capturas reales) | Lleva el mensaje de un estático ganador a Reels y Stories. Heath predice que crecerán **[HYPOTHESIS]** |
| 6 | **Demo o explicador con voz IA genérica** | ≈0,04 $ de voz por 30 s (unos 450 caracteres a 80 $/M con ElevenLabs v4) | Zona gris: lo prudente es rotular «Voz generada con IA» | Cuando nadie quiere poner la voz. Revisión de un nativo: no hay evaluación independiente de voces IA en castellano de España |
| 7 | **Hooks nuevos con la voz clonada o lip-sync sobre vídeo real** | ≈0,07–0,40 $ por variante (2–5 s: clon de voz + Kling LipSync a 0,014 $/s o lipsync-2-pro a 0,067–0,083 $/s) | **Sí, obligatorio**: una persona real dice algo que no grabó | Iterar hooks de un ganador sin regrabar. Consentimiento técnico y contrato de cesión (§5.5) |
| 8 | **Clon digital del fundador, solo para variantes** | HeyGen por API: 0,30 / 2,42 / 3,60 $ cada 30 s (Avatar III / IV / V), más 2,13 $ por crear el gemelo | **Sí, obligatorio**, aunque haya consentimiento | Nadie ha publicado datos que lo comparen con el fundador real en B2B. Para variantes de un ganador, nunca como pieza principal |
| 9 | **Presentador o avatar IA etiquetado, solo como experimento** | ≈4–6,5 $ un anuncio de 20–30 s con el motor del OS (medido en oct-2026); ≈6–8 $ con Omni 1.2 y ≈12–15 $ con Kling 4.0 según el informe | **Sí, obligatorio**, desde el primer segundo | Presenta, explica y demuestra; nunca testifica. Una agencia de IA puede usarlo a cara descubierta para enseñar lo que sabe hacer. Solo como celda de test frente a 1, 2 y 4 |
| 10 | **Avatar que finge ser cliente, experto o empleado: nunca** | — | Etiquetarlo no lo arregla | Testimonio falso (prohibido de forma expresa en EE. UU.), engañoso en todas partes y contrario a lo que vende una consultora |

Cómo se produce en el OS: 1, 2 y 4 con `/producir-video` por la vía `propio` (`docs/guias/video-propio.md`; el caso,
con `/casos-y-creadores`); 3 con `/producir-estatico`; 5 con el montaje avanzado de cutkit; 6 a 9 con
`docs/guias/video-ia.md` o la herramienta de voz o vídeo que uses, siempre con el consentimiento de §5.5.

Fuentes de los costes: cutkit y HyperFrames ([GitHub HyperFrames](https://github.com/heygen-com/hyperframes)); imagen
([Google AI Studio pricing](https://aistudio.google.com/docs/pricing)); voz
([ElevenLabs API pricing](https://elevenlabs.io/pricing/api)); lip-sync
([fal](https://fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video); [sync.so](https://sync.so/docs/models));
clon ([HeyGen API pricing](https://help.heygen.com/en/articles/10060327-heygen-api-pricing-explained)); motor
(`docs/guias/video-ia.md` §7) y Omni 1.2 o Kling 4.0 (cálculo del informe con 2,5–3 tomas por plano útil). Los
precios de modelos cambian cada pocos meses: compruébalos antes de presupuestar.

### 2.1 Si el fundador no quiere salir en cámara

Baja por **3, 4, 5 y 6**, en ese orden: estáticos y carruseles; demo de pantalla con su voz (la voz sí, la cara no);
estático animado; y, si tampoco quiere poner la voz, demo con voz IA genérica y rotulada. Si hay caso de cliente (2),
va por delante de todo esto. **No saltes al avatar.** **[STRONG INFERENCE]**

### 2.2 Por qué el avatar no compensa

La única ventaja de un avatar realista es **parecer una persona que habla**. En la UE, las directrices de la Comisión
tratan a los avatares humanos realistas como «persons» a efectos de deepfake, así que el art. 50 obliga a rotularlo de
forma clara desde la primera exposición (§5). Con el rótulo deja de parecer humano y te quedas con todos sus costes:

- **Declarar la IA baja el CTR**: un 31,5 % en el único experimento de campo (NYU, display). **[EMPIRICAL]**
- **Rinde peor cuando se nota**: 0,4–0,6× el ROAS y 1,6–2,2× el CPM en el caso más duro. **[EMPIRICAL]** (una cuenta)
- **Resta confianza**: al 42 % le empeora la opinión de la marca una publicidad IA de baja calidad o «uncanny». **[EMPIRICAL]**
- **Cuesta más**: 4–8 $ por anuncio frente a ≈0 $ de un estático o una demo con voz real.
- **Contradice el mensaje** de una consultora de IA, que vende fiabilidad.

Conclusión: el etiquetado obligatorio anula la ventaja del avatar y deja sus inconvenientes. **[STRONG INFERENCE]** La
excepción es el avatar **declarado como tal** que demuestra lo que la agencia sabe hacer (opción 9): un SaaS lo hizo con
«i'm also ai generated, but i look like THIS» y obtuvo un 1,8 % de CTR, aunque el caso es autopromoción
([r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1t4o5c7/everyone_says_ai_ads_dont_convert_this_video_is/)).
**[EMPIRICAL]** (anecdótico)

## 3. La evidencia, con sus límites

No hay **ningún estudio independiente y controlado** de vídeo IA frente a vídeo humano en Meta con datos de conversión
en 2026. Los dos estudios grandes (Taboola y NYU) miden anuncios visuales en otras redes. Lo demás son tests de
practicantes sin auditar, que casi siempre dibujan el mismo patrón: **lo humano gana anuncio a anuncio y la IA gana por
cartera**. **[EMPIRICAL]**

### 3.1 Supervivencia a 90 días (3.941 anuncios)

- **Dato:** en el «State of UGC Ads Q4 2026» de UGC Factory, con 3.941 vídeos de 193 marcas DTC lanzados entre el
  2025-01-01 y el 2026-06-15, la **voz en off con IA sobre b-roll real sobrevive un 38,9 %**, la media un **26,7 %**, el
  creador hablando a cámara un **24,5 %** y los personajes IA animados o de dibujos un **7,3 %**.
- **Qué mide:** cuántos anuncios siguen activos en las bibliotecas públicas de anuncios a los 90 días o más. Es un
  **proxy**: un anunciante mantiene lo que le funciona, pero no se ven el ROAS ni el CPA, y un anuncio puede seguir vivo
  por inercia. No mide aparte los avatares realistas, el 60 % de la muestra es salud y suplementos (no B2B) y lo
  publica quien vende UGC con IA. La verificación no lo contrastó.
- **Lectura:** la IA que **sustituye** a la persona se descarta; la que **potencia una prueba real** sobrevive.
  **[EMPIRICAL]** (proxy de vendor) — [OpenClips/UGC Factory](https://openclips.ai/blog/ai-ugc-ads/)

### 3.2 Evan Carroll, más de 40 cuentas

- **Vídeo:** hook rate del **48 % humano frente al 32 % IA**, hold del 21 % frente al 13 %, **CPA de 36,20 $ frente a
  49,60 $** y fatiga a las 3 semanas frente a 2.
- **Estáticos:** gana la IA: **CPA de 28,75 $ frente a 32,15 $**, con un CTR casi igual (1,83 % frente a 1,89 %).
- **Límites:** un post de LinkedIn (2026-08-09) sin método publicado ni sector; no se pudo verificar.
  **[EMPIRICAL]** (anecdótico) — [LinkedIn](https://www.linkedin.com/posts/theevancarroll_human-vs-ai-ugc-data-across-40-accounts-activity-7492318478104764417-tAaC)

### 3.3 El caso duro del avatar

- **Dato:** un anunciante de suplementos en EE. UU. (30.000–80.000 $/mes en Meta) probó el mismo guion por tres vías
  durante 90 días. Con el UGC real dirigido como base, el **avatar realista de tres proveedores** salió a **1,6–2,2× el
  CPM, 0,5–0,7× el CTR y 0,4–0,6× el ROAS**: «Unusable for paid in our account». Su hipótesis: el clasificador de
  calidad de Meta penaliza el «uncanny middle ground».
- **Límites:** una sola cuenta, sin auditar. Es creíble porque no nombra herramienta y va contra la IA. Aparentemente el mismo autor
  vio en TikTok el avatar casi en línea base (0,92× el ROAS), así que la penalización parece propia de Meta o de esa
  cuenta.
- **[EMPIRICAL]** (anecdótico) — [r/PPC](https://www.reddit.com/r/PPC/comments/1ucep65/anyone_else_struggling_with_aigenerated_ugc_being/);
  [r/TikTokAds](https://www.reddit.com/r/TikTokAds/comments/1udb4j3/is_anyone_seeing_aitalkinghead_ads_actually_scale/)

### 3.4 Ben Heath y el giro a estáticos

- **Encuesta:** en la de su audiencia de octubre de 2026, el **54 %** elige el estático como mejor formato y el **38 %**
  el vídeo; dos años antes era al revés (**60 %** vídeo, **27 %** imagen). Encuesta no aleatoria, en un vídeo patrocinado.
- **Lo que observa:** Meta asigna cada vez más presupuesto a estáticos; los estáticos que **«parecen hechos con IA» no
  les funcionan en absoluto**, mientras que las fotos de producto recolocadas con IA en fondos o modelos sí, cuando
  «nadie lo nota»; crecerán los **estáticos animados** (texto que entra, elementos que se mueven). En ofertas basadas en
  expertise, el vídeo de fundador, demo o testimonio sigue ganando en frío, y a público caliente le funcionan
  estáticos con la cara del fundador.
- **[EMPIRICAL]** (agencia con gasto declarado alto; la predicción, **[HYPOTHESIS]**) —
  [Ben Heath, 2026-10-27](https://www.youtube.com/watch?v=2VWnj9C9PvQ)

### 3.5 Metadata: B2B en Meta

- **Dato:** en su benchmark de 2026 (153 anunciantes B2B, 57,6 M$ de gasto en 2025, sobre todo SaaS de EE. UU.), el CPL
  en Facebook fue de **136 $ con imagen frente a 225 $ con vídeo**.
- **Límites:** vendor de marketing B2B; no separa la IA de lo humano ni dice qué tipo de vídeo.
- **[EMPIRICAL]** — [Metadata.io, 2026-09-11](https://metadata.io/resources/blog/fb-ad-strategies);
  [05/10](../05-leadgen-high-ticket-crm/10-b2b-saas-local.md)

### 3.6 NYU: declarar la IA cuesta clics

- **Dato:** NYU Stern y Emory (nota de investigación del 2025-11-06) midieron hasta un **+19 % de CTR** en imágenes hechas
  del todo con IA frente a las de expertos humanos; las humanas retocadas con IA no mejoraron. **Decir que el anuncio
  estaba hecho con IA bajó el CTR un 31,5 %** (relativo; ~1,17 puntos absolutos según The Decoder).
- **Límites:** test de campo en Google Display Network, con imágenes, no vídeo ni Meta. Nadie ha publicado un split test
  en Meta con etiqueta frente a sin ella.
- **[EMPIRICAL]** — [NYU Stern](https://www.stern.nyu.edu/experience-stern/faculty-research/ai-advertising-paradox);
  [The Decoder](https://the-decoder.com/telling-consumers-an-ad-is-ai-generated-cuts-clicks-by-31-percent-study-finds/)

### 3.7 DoubleVerify: el 42 %

- **Dato:** en la encuesta de DoubleVerify y YouGov (2026-07-29; 22.000 consumidores de 22 mercados y 2.020
  marketers), al **42 %** le empeoraría la opinión de una marca una publicidad con IA «low-quality or uncanny» (al 24 %
  le mejoraría), el 40 % ve bien los anuncios IA pulidos y el **56 % no distingue** de forma consistente qué es IA.
- **Límites:** opinión declarada, no comportamiento; lo publica un vendor de verificación. Lo que castiga es la IA que
  **se nota**, no la IA en sí.
- **[EMPIRICAL]** — [DoubleVerify](https://doubleverify.com/company/newsroom/global-study-quality-matters-most-as-ai-transforms-online-content-and-advertising)

### 3.8 Aviso: astroturfing en Reddit

Muchos posts de «la IA gana en ROAS» repiten la **misma plantilla de cifras** en varios subreddits (100.000 $ y 220
vídeos en cuatro cubos; 85.000 $ y 195 creatividades con los mismos cuatro cubos) y nombran siempre la misma
herramienta (Creatify, Argil, Cliptalk). Creatify aparece en cuatro subreddits distintos en un mes con el mismo tono de
«números honestos». Son más creíbles los posts **sin herramienta nombrada y con resultados negativos para la IA**.
Ninguno es verificable: Reddit bloquea el acceso automatizado y nadie audita las cifras. Tampoco tiene fuente la cifra
de blogs de «un 14 % de rechazos por IA no declarada», que contradice la política oficial de Meta.
**[EMPIRICAL]** (patrón observado) — [r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1rlvjrg/i_tested_ai_ads_vs_human_ugc_with_100k_in_3/);
[r/InstagramMarketing](https://www.reddit.com/r/InstagramMarketing/comments/1sg487p/4_month_of_pitting_ai_creatives_against/);
[Common Thread Collective](https://commonthreadco.com/blogs/coachs-corner/meta-ads-changes-2026)

### 3.9 Cómo leerlo todo junto

- Los «triunfos» de la IA salen de la **economía de cartera**: un equipo vio que la IA convierte ~20 % menos por anuncio
  pero deja probar cuatro veces más conceptos, y propuso medir el **coste por ganador validado**
  ([r/PPC](https://www.reddit.com/r/PPC/comments/1wgg17q/anyone_else_testing_ai_video_ads_alongside_human/)). En un
  test de 92.000 $, la IA «de un clic» sacó un ROAS de 2,1 y la IA con un humano en el bucle, 4,7
  ([r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1rw7ynm/i_tested_ai_vs_human_ads_with_92k_in_ad_spend/)).
  **[EMPIRICAL]** (anecdótico)
- El patrón híbrido con mejor relación riesgo/resultado: **la IA pone la atención y la variedad; lo real pone la
  prueba**. Hacia el segundo 3 o 4, cuando toca demostrar, es donde la IA pierde la confianza
  ([r/AI_UGC_Marketing](https://www.reddit.com/r/AI_UGC_Marketing/comments/1s4vzad/our_hybrid_ai_hook_approach_is_outperforming/)).
  **[STRONG INFERENCE]**
- Taboola (más de 500 M de impresiones, display) encontró que los anuncios de IA que **no parecían IA** fueron los de
  más engagement ([Taboola](https://www.taboola.com/press-releases/genai-ads-study-2026/)). Encaja con todo lo
  anterior: lo que se castiga es que se note. **[EMPIRICAL]**
- Con 30–50 eventos por celda, el intervalo del cociente de CPL entre dos celdas es de ≈×/÷1,5–1,7: un test de avatar
  frente a fundador solo da por real una diferencia de 1,6× o más. **[STRONG INFERENCE]** (cálculo del informe;
  ver [05](05-testing-creativo.md))

## 4. Qué estáticos funcionan y cuáles no

**Funcionan** (en B2B y SaaS):

- **Dolor + prueba**: una frase del problema en palabras del cliente y una prueba (dato del caso, captura). Los
  estáticos de texto y de producto con texto lideran el hit rate en Motion ([04](04-formatos-y-estilos.md)).
  **[EMPIRICAL]**
- **Antes/después del proceso**: 7 pasos y 3 personas → 2 pasos y una revisión. En B2B es un diagrama, no un cuerpo,
  así que no choca con las restricciones de antes/después de salud. **[STRONG INFERENCE]**
- **Captura de resultado real**: el panel, el informe o la bandeja del cliente con permiso y sin datos personales. Nunca
  capturas de facturación propia ni promesas de ingresos ([08/08](../08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md)).
  **[STRONG INFERENCE]**
- **Fotos reales retocadas con IA cuando nadie lo nota** (producto recolocado en otro fondo): a Heath le funcionan.
  **[EMPIRICAL]**
- **Estáticos con la cara del fundador para público caliente** (Heath) y un diagrama estático del sistema junto al
  vídeo del fundador (una consultoría B2B del Reino Unido) ([r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1t5cxm7/spent_1700_on_meta_ads_for_my_b2b_acquisition/)).
  **[EMPIRICAL]** (anecdótico)
- **Estático animado** (opción 5): el mismo mensaje con movimiento para cubrir placements de vídeo. **[HYPOTHESIS]**
  sobre su rendimiento: es la predicción de Heath, sin datos.

**No funcionan:**

- **Estáticos que «parecen IA»**: no les funcionan en absoluto (Heath). «The second a real person sees it close up it
  screams generated», en un público de 25–40 años ([r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1u215y0/is_anyone_actually_getting_results_from_ai_ad/)).
  **[EMPIRICAL]**
- **Un personaje sintético fijo en todos los estáticos**: en dos cuentas se fatigó antes. En una, la frecuencia llegó a
  3,2 el día 5 (lo normal ahí, ~2,5 entre los días 10 y 12) y la vida útil fue de 5–7 días frente a ~12 de los
  estáticos de diseñador; en la otra, el día 16 ya era más cara que las fotos propias: «People just got bored of the
  same synthetic face quicker» ([r/FacebookAds](https://www.reddit.com/r/FacebookAds/comments/1vvhjc2/ai_creatives_cut_my_cpa_by_a_third_for_three/);
  [r/digital_marketing](https://www.reddit.com/r/digital_marketing/comments/1vvgvv2/i_tested_ai_creative_against_stock_photos_on_a/)).
  **[EMPIRICAL]** (anecdótico)
- **Capturas de producto B2B pasadas por un generador**: «You can't just throw boring B2B product screenshots at an AI
  and get a converting ad» ([r/SaaS](https://www.reddit.com/r/SaaS/comments/1rvfd31/aigenerated_ads_now_drive_60_of_our_meta_spend_we/)).
  **[EMPIRICAL]** (anecdótico)
- **Interfaces o pantallas inventadas**: el texto generado no es fiable en ningún modelo, y una UI que no es la tuya es
  una afirmación engañosa. Rótulos, precios y cifras, siempre en postproducción. **[STRONG INFERENCE]**
- **El carrusel por defecto**: es el asset type con peor hit rate en Motion; úsalo para pasos u objeciones, no como
  formato base ([04](04-formatos-y-estilos.md)). **[EMPIRICAL]**

**Por qué Meta mueve presupuesto a estáticos:**

- **Lo observan las agencias**: Heath ve que Meta les asigna cada vez más gasto y lo explica por la caída de la atención
  y porque casi todo el mundo abandona el vídeo antes del CTA. **[EMPIRICAL]** (anecdótico)
- **El mecanismo**: Meta reparte el gasto hacia lo que da el resultado más barato. Los estáticos salen con un CPM ~15 %
  menor y un CPA prácticamente igual que el vídeo (Biddyco, 17 cuentas), y en B2B con un CPL menor (Metadata). Si un
  estático consigue el mismo resultado por menos, el sistema le da el presupuesto. **[STRONG INFERENCE]** (datos de
  [04](04-formatos-y-estilos.md) y §3.5)
- **Meta empuja además su propia conversión de estático a vídeo**: la generación de vídeo a partir de estáticos en
  Advantage+ creative está en disponibilidad general desde el 2026-10-06; la única cifra (+10 % de CTR y +8 % de CVR)
  es de la propia Meta, de la beta y sin método, y el anuncio no menciona la UE ([14](14-herramientas-ia-creativa-meta.md)).
  **[OFFICIAL META]**
- **Matiz**: los estáticos se fatigan antes (8,3 días de media frente a 11,7 del vídeo en 47 cuentas, con método poco
  claro), así que piden más volumen ([r/PPC](https://www.reddit.com/r/PPC/comments/1t2g5ox/i_tested_metas_andromeda_creative_refresh/)).
  **[EMPIRICAL]** (anecdótico)

## 5. Etiquetado de IA

### 5.1 Caso → ¿etiqueta? → por qué

| Caso | ¿Etiqueta? | Por qué |
|---|---|---|
| Voz real del fundador o del cliente | No | No hay contenido generado ni manipulado: es una persona real diciendo lo que dijo |
| Montaje con IA (cortes, silencios, subtítulos, encuadre, mezcla de audio) | No | La IA edita, no crea ni altera lo que se ve o se oye para que parezca otra cosa |
| Gráficos, motion graphics y capturas reales de la app | No | No imitan personas, lugares ni hechos reales; la captura es la interfaz real |
| Voz clonada de una persona real | **Sí, obligatorio** | Audio que imita a una persona existente y parece auténtico (art. 3.60 y 50.4) |
| Lip-sync que hace decir algo nuevo a una persona real | **Sí, obligatorio** | Es el deepfake más claro: un fundador real diciendo palabras que no grabó |
| Clon digital del fundador, aunque haya consentimiento | **Sí, obligatorio** | El consentimiento es de la persona clonada; la transparencia se le debe al espectador |
| Avatar o presentador realista generado con IA | **Sí, obligatorio** | Las directrices de la Comisión cuentan los avatares humanos realistas como «persons» |
| Voz IA genérica (no imita a nadie concreto) | Zona gris: **lo prudente es etiquetar** | No imita a una persona existente, pero pasa por una voz humana auténtica |
| Planos realistas de lugares hechos con IA (b-roll de oficina, calle) | Zona gris: **lo prudente es etiquetar** | El art. 3.60 incluye «places»; un plano genérico puede no parecerse a un lugar existente, pero parece grabado |
| Avatar que finge ser cliente, experto o empleado | Etiquetarlo **no lo arregla**: no se hace | Testimonio falso: engañoso aunque lleve rótulo, y prohibido de forma expresa en EE. UU. |

**[OFFICIAL — regulador]** en los casos obligatorios; **[STRONG INFERENCE]** en los «no» y en la zona gris (no hay
todavía práctica de las autoridades). En la duda, etiqueta: el coste de un rótulo es pequeño y el de una multa, no.

### 5.2 Base legal

- **Reglamento de IA de la UE, art. 50.4 y 50.5**, aplicable desde el **2026-08-02**: quien despliega un sistema que
  genera o manipula un deepfake tiene que «disclose that the content has been artificially generated or manipulated»
  (50.4), de forma clara y distinguible a más tardar en la **primera exposición** (50.5). **[OFFICIAL — regulador]**
  ([AI Act Explorer](https://artificialintelligenceact.eu/article/50/); [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689))
- **Art. 3.60**: deepfake es el contenido que «resembles existing persons, objects, places, entities or events» y que
  parecería auténtico. **[OFFICIAL — regulador]**
- **Directrices de la Comisión sobre el art. 50** (publicadas el **2026-07-20**, actualizadas el 2026-11-05): entienden
  por «persons» también los «realistic AI-generated human avatars or personas», y dan como ejemplos de deepfake que no
  se libran por ser creativos un vídeo de teletienda con consumidores simulados y un «realistic synthetic influencer
  testing out a sponsored real product». El código de buenas prácticas de marcado y etiquetado es definitivo desde el
  2026-06-10. El Ómnibus Digital (Reglamento (UE) 2026/1744) **no aplazó** la obligación de quien despliega.
  **[OFFICIAL — regulador]** ([Comisión Europea](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems);
  [código de buenas prácticas](https://digital-strategy.ec.europa.eu/en/news/commission-publishes-code-practice-marking-and-labelling-ai-generated-content);
  [EUR-Lex 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng))
- **Multas (art. 99.4 y 99.6)**: hasta **15 M€ o el 3 %** de la facturación mundial, la cifra mayor; para pymes, la
  menor. **[OFFICIAL — regulador]**
- **Quién responde**: según las directrices, la empresa que solo encarga el anuncio, sin decidir ni controlar si y cómo
  se usa la IA, no es responsable del despliegue; **la agencia sí**. Una guía de IAB Austria añade que el cliente pasa a
  serlo también si elige la herramienta, da los prompts o fija los parámetros. Si produces para clientes, la obligación
  es tuya: déjalo escrito en el contrato. **[OFFICIAL — regulador]** + **[EMPIRICAL]**
  ([PPC Land sobre IAB Austria](https://ppc.land/agencies-not-clients-usually-carry-ai-label-duty-iab-austria-guide-says/))
- **España**: el proyecto de ley de IA caducó el 2026-10-06 con la disolución de las Cortes. El art. 50 se aplica igual,
  porque es un reglamento europeo; lo que queda abierto es quién sanciona y con qué procedimiento, y si la AESIA puede
  hacerlo hoy es **[CONTESTED]** ([BOE](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742)).
- **EE. UU., FTC (16 CFR 465)**, en vigor desde el 2024-10-21: prohíbe los testimonios que falseen que el testimoniante
  existe o que ha usado el producto; la norma no nombra la IA, pero su preámbulo aclara que «AI-generated reviews are
  covered by the final rule». **[OFFICIAL — regulador]** ([Federal Register](https://www.govinfo.gov/content/pkg/FR-2024-08-22/html/2024-18519.htm))
- **Nueva York, ley S.8420-A**, desde el 2026-06-09: hay que declarar de forma destacada («conspicuously disclose»)
  cualquier «synthetic performer» en publicidad cuando el anunciante lo sabe, salvo en anuncios solo de audio; multas de
  1.000 $ la primera vez y 5.000 $ las siguientes. **[OFFICIAL — regulador]**
  ([NY Senate](https://www.nysenate.gov/legislation/bills/2025/S8420/amendment/A))
- **Regla operativa** que sale de todo esto: un actor sintético puede **presentar o demostrar**; nunca afirma haber
  usado el producto, ni promete resultados personales, ni se parece a una persona real o a un famoso.
  **[STRONG INFERENCE]**
- No se ha verificado cómo se aplican la Ley de Competencia Desleal, la Ley General de Publicidad y la Directiva Ómnibus
  de consumo a los testimonios sintéticos: **revísalo con un abogado antes de vender el servicio.**

### 5.3 Por qué Meta no lo hace por ti

- **Meta no exige declarar la IA en anuncios comerciales.** La autodeclaración obligatoria es solo para anuncios
  políticos o sociales, que en la UE ya no se sirven desde el 2025-10-06. **[OFFICIAL META]**
  ([Meta Newsroom](https://about.fb.com/news/2025/07/ending-political-electoral-and-social-issue-advertising-in-the-eu/))
- **«AI info» solo salta en dos casos**: cuando el anuncio se crea o se edita de forma significativa **con las
  herramientas de Meta**, o cuando Meta detecta IA de terceros por «industry-standard signals» (no nombra C2PA ni IPTC).
  Desde el 2026-06-01 la etiqueta va **dentro de «About this ad»**, en el menú de tres puntos, y puede variar por
  región. **[OFFICIAL META]** ([Meta Newsroom](https://about.fb.com/news/2025/02/gen-ai-transparency-metas-ads-products/))
- **En la práctica casi nunca salta con vídeo de terceros**: una auditoría de 37.768 archivos de la Ad Library no
  encontró credenciales C2PA en ninguno de los 971 revisados, y Meta reconoció en 2024 que aún no detectaba las señales
  de vídeo y audio de otras empresas, sin actualización posterior. **[EMPIRICAL]** (fuente secundaria) +
  **[OFFICIAL META]** (2024) ([PPC Land](https://ppc.land/only-2-of-3-379-ai-flagged-meta-ad-files-disclosed-ai-use-resemble-ai-finds/);
  [Meta Newsroom, 2024](https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/))
- **El reencodado con FFmpeg pierde las señales.** Un vídeo montado con cutkit o con el motor llega casi seguro sin
  metadatos de procedencia y sin etiqueta automática. **[STRONG INFERENCE]**
- **Y aunque saltara, no bastaría**: una etiqueta escondida en un menú no es «clara y distinguible en la primera
  exposición». Cumplir el art. 50 depende **entera y exclusivamente de ti**. **[STRONG INFERENCE]**
- Lo que Meta sí persigue es el **engaño**: el celeb-bait (que detecta con reconocimiento facial), las estafas y las
  afirmaciones engañosas. Si usas la IA generativa de Meta, sus términos te hacen responsable del resultado y prohíben
  quitar marcas de agua o metadatos de autenticidad ([14](14-herramientas-ia-creativa-meta.md)); la actualización de
  esos términos (prevista para el 2026-10-30 y aplazada al 2026-11-20) quedó suspendida a primeros de noviembre de
  2026, así que siguen los actuales ([00-ESTADO-ACTUAL-2026](../00-ESTADO-ACTUAL-2026.md)). **[OFFICIAL META]**

### 5.4 Dónde y cómo se marca

- **Rótulo visible en el vídeo desde el primer segundo**, legible en el móvil y dentro de las zonas seguras (14 %
  arriba, 35 % abajo y 6 % a los lados en 9:16; [07/03](../07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md)).
  Mantenerlo mientras sale el contenido sintético es lo prudente. En un estático, el rótulo va en la imagen.
  **[OFFICIAL — regulador]** (primera exposición) + **[STRONG INFERENCE]** (forma)
- **Textos de ejemplo**, cortos y concretos: «Presentador generado con IA», «Avatar creado con IA», «Voz generada con
  IA», «Doblado con IA», «Versión IA de <nombre>, con su permiso», «Contenido generado con IA», «Imagen generada con
  IA». Di **qué** es IA si cabe; «Creado con IA» a secas sirve, pero informa menos.
- **No bastan**: un rótulo solo en la tarjeta final, solo en los metadatos o solo en el texto principal (que se corta en
  «Ver más»). El motor rotula de forma visible por defecto (`ai_label_policy: "visible"`); sus opciones `end_card` y
  `metadata_only` no valen para un deepfake. **[STRONG INFERENCE]**
- **cutkit**: el rótulo se activa con `--etiqueta-ia` (viene **desactivado** por defecto) y el texto sale de
  `etiqueta_ia` en `clientes/<slug>/marca/marca.json`. Úsalo siempre en los vídeos híbridos con b-roll del motor y en
  cualquier pieza de las filas «sí» o «zona gris» de §5.1.
- **`LEEME.md` de la pieza**, sección «IA y etiquetas» (plantilla `.claude/skills/producir-video/plantilla-leeme.md`):
  qué es IA (voz, cara, planos), la fila de §5.1 que aplica, el texto del rótulo y el segundo en que aparece, y la ruta
  del consentimiento en `clientes/<slug>/privado/` (sin copiar datos personales).
- **No quites nunca** las marcas de agua ni los metadatos de autenticidad (SynthID en los vídeos de Google).
- **Prueba formatos de etiqueta, no «con o sin etiqueta»**: en la UE no puedes quitarla. Prueba dónde va, qué dice y
  cómo se integra en el hook. **[STRONG INFERENCE]**

### 5.5 Consentimientos y contrato de cesión de imagen y voz

Si la cara o la voz son de alguien real, hacen falta **dos cosas distintas**: **[STRONG INFERENCE]**

1. **El consentimiento técnico de la plataforma**: HeyGen bloquea el gemelo hasta tener una declaración de
   consentimiento grabada en cámara; ElevenLabs v4 verifica cada clon (el profesional pide ≥30 min de audio); la
   replicación de voz de Gemini exige una grabación de consentimiento del mismo hablante, con una frase oficial en
   es-ES, y rechaza audio sintético como origen. Evita clonar voces con MiniMax o Seed-VC, que no documentan
   verificación de consentimiento (MiniMax solo verifica la identidad de la cuenta; Seed-VC está archivado).
   Documentación oficial de cada proveedor ([HeyGen](https://developers.heygen.com/docs/avatar-consent);
   [ElevenLabs v4](https://elevenlabs.io/v4); [Gemini API: Voice replication](https://aistudio.google.com/docs/voice-replication);
   [InVideo](https://invideo.io/blog/ai-voice-model-pricing/))
2. **Un contrato de cesión de imagen y voz** con alcance (qué piezas y qué usos: hooks nuevos, variantes, idiomas),
   territorio, duración, remuneración y **revocación** (qué pasa con los anuncios activos si la retira). También con
   los empleados y con el propio fundador: la empresa que anuncia no es la persona. Lista de lo que tiene que resolver:
   `.claude/skills/casos-y-creadores/checklist-derechos.md` §4; el permiso de cliente
   (`.claude/skills/casos-y-creadores/permiso-cliente.md`, anexo B) excluye por defecto el doblaje, la clonación y las
   imágenes generadas salvo firma expresa.

El consentimiento de la persona **no sustituye al rótulo**: cubre sus derechos, no la transparencia con el espectador.
Los actores de plataformas de avatares tienen consentimiento, pero no exclusivo, y una fuente secundaria dice que
pueden retirarlo y obligarte a retirar los anuncios: mal punto de partida para el presentador de una marca
([AdMake AI](https://admakeai.com/alternatives-to/arcads)). **[EMPIRICAL]** (secundaria)

> **No es asesoría legal.** Es un resumen operativo a 2026-11-10. Antes de vender clones, voces o avatares a clientes,
> revisa el contrato y la etiqueta con un abogado.

## 6. Qué hace el mercado

- **Los media buyers grandes usan la IA para analizar, iterar estáticos y editar**, y casi no hablan de generar vídeo.
  Ben Heath enseña la herramienta de análisis creativo de Meta; Sam Piliero y Chase Chappell conectan Claude al MCP de
  Meta o a la Ad Library para detectar ganadores y recrear variantes **estáticas**; Dara Denney quiere que el 30–50 % del
  gasto vaya a anuncios de colaboración con creadores reales (su único dato propio de IA es un 77 % de hook rate en un
  formato hecho solo con IA, sin CPA). Un V1 de anuncio montado por Claude Code a partir del metraje bruto de un creador
  tardó unos 20 minutos. **[EMPIRICAL]** (anecdótico; varios vídeos patrocinados) —
  [Ben Heath](https://www.youtube.com/watch?v=RTrRKB0iXwQ); [Sam Piliero](https://www.youtube.com/watch?v=B7z0vcKS67k);
  [Chase Chappell](https://www.youtube.com/watch?v=ReYEYoLsppk); [Dara Denney](https://www.youtube.com/watch?v=4wM-i1cxtAM);
  [Alex Cooper](https://www.youtube.com/watch?v=-AIX0QuFq7E)
- **El UGC sintético lo empujan sobre todo creadores de tutoriales con afiliación** a la plataforma que enseñan
  (Higgsfield, OpenArt, Arcads, Topview). En X circulan posts casi idénticos sobre «10 anuncios por menos de 5 $» con
  Kling 4.0, con el mismo texto y otra herramienta. Ninguno publica CPA ni ROAS con su gasto. **[EMPIRICAL]**
- **Las agencias españolas de «UGC con IA» cobran 50–150 € por vídeo** con entrega en 24–72 h (Reelmente); otra, desde
  70 € por anuncio en pack (Nexo UGC). Ninguna publica CPA, ROAS ni hook rate verificables. Como referencia, un creador
  UGC humano cobra en España 50–250 € por pieza. **[EMPIRICAL]** (precios de vendor) —
  [Reelmente, 2026-10-13](https://reelmente.com/blog/ugc-con-ia-vs-creador-humano);
  [Nexo UGC](https://nexougc.com/anuncios-con-ia/); [Salvilla](https://www.youtube.com/watch?v=psqSJJFqel8)
- **Lectura para una consultora**: competir vendiendo vídeo sintético por pieza es entrar en un mercado de precio sin
  pruebas de resultado. Lo defendible es el sistema que nadie ve: fundador, demo y estáticos editados y variados con IA,
  con el etiquetado y los consentimientos resueltos. **[HYPOTHESIS]**

## Implicaciones operativas

- **Cada lote** lleva al menos una pieza de 1, 2 o 4 y uno o dos estáticos (3). La IA se usa para editar y variar esas
  piezas antes que para crear otras. **[STRONG INFERENCE]**
- **Antes de producir cualquier pieza con IA**, el brief dice qué fila de §5.1 aplica y el texto del rótulo; el
  `LEEME.md` lo deja escrito. Sin consentimiento firmado, no hay clon ni voz clonada.
- **El avatar solo entra como celda de test** frente a tres controles (operador real explicando el problema, prueba de
  cliente y demo del mecanismo), juzgado por reuniones cualificadas, con el mismo presupuesto y vigilando el CPM.
- **Decide por la capa más baja de verdad** (reunión cualificada, propuesta, venta), no por hook rate ni CTR, y cuenta
  el **coste por ganador validado** cuando compares IA y humano.
- **Diversidad real**: cien variantes del mismo avatar valen menos que quince conceptos distintos; Meta agrupa lo
  parecido ([01](01-creative-es-targeting.md)).

## Errores frecuentes

- Creer que la etiqueta «AI info» de Meta cubre la obligación del art. 50.
- Rotular solo al final, solo en el texto principal o solo en los metadatos.
- Clonar la voz del fundador con un «sí» de palabra, sin contrato ni consentimiento técnico.
- Poner en boca de una persona sintética «lo he probado», «en mi empresa…» o resultados personales.
- Generar la interfaz del producto en vez de grabarla.
- Pasar estáticos por un generador hasta que «parecen IA».
- Dar por buena una cifra de Reddit que nombra la herramienta que vende.
- Juzgar el avatar por su hook rate.

## Preguntas abiertas

- No hay ningún estudio controlado de vídeo IA frente a humano en Meta con conversiones, ni datos de B2B en España.
- Nadie ha publicado datos que comparen el clon del fundador con el fundador real, ni el hook con IA pegado a metraje
  real del fundador, en B2B.
- No hay un split test público en Meta con etiqueta de IA frente a sin ella; el −31,5 % es de display.
- La zona gris (voz IA genérica, lugares realistas) depende de cómo apliquen el art. 50 las autoridades; en España, quién
  sanciona es [CONTESTED].
- No hay evaluación independiente de voz ni de lip-sync en castellano de España.

## Fuentes clave

- Informe «Vídeo IA para anuncios Meta» y su verificación independiente — 2026-11-09 / 2026-11-10 — investigación
  interna (`docs/desarrollo/investigacion/reports/`)
- [OpenClips / UGC Factory — State of UGC Ads Q4 2026](https://openclips.ai/blog/ai-ugc-ads/) — 2026 — vendor (dataset)
- [Evan Carroll — Human vs AI UGC across 40+ accounts](https://www.linkedin.com/posts/theevancarroll_human-vs-ai-ugc-data-across-40-accounts-activity-7492318478104764417-tAaC) — 2026-08-09 — practicante
- [r/PPC — AI-generated UGC being penalized](https://www.reddit.com/r/PPC/comments/1ucep65/anyone_else_struggling_with_aigenerated_ugc_being/) — 2026-06-22 — practicante
- [Ben Heath — This new Facebook Ads trend is crazy](https://www.youtube.com/watch?v=2VWnj9C9PvQ) — 2026-10-27 — agencia
- [Metadata.io — Meta ads for B2B (2026 B2B Paid Media Benchmark)](https://metadata.io/resources/blog/fb-ad-strategies) — 2026-09-11 — vendor (dataset)
- [NYU Stern — The AI advertising paradox](https://www.stern.nyu.edu/experience-stern/faculty-research/ai-advertising-paradox) — 2025-11-06 — académico
- [DoubleVerify — Global study: quality matters most](https://doubleverify.com/company/newsroom/global-study-quality-matters-most-as-ai-transforms-online-content-and-advertising) — 2026-07-29 — vendor (encuesta)
- [Taboola — GenAI ads study](https://www.taboola.com/press-releases/genai-ads-study-2026/) — 2026-01-28 — plataforma (dataset)
- [r/FacebookAds — Realistic AI UGC Meta ads for B2B](https://www.reddit.com/r/FacebookAds/comments/1vsrt1q/realistic_ai_ugc_meta_ads_for_b2b/) — 2026-08-19 — practicante
- [AI Act Explorer — Article 50](https://artificialintelligenceact.eu/article/50/) — vigente desde 2026-08-02 — regulador
- [Comisión Europea — Guidelines on transparency obligations (art. 50)](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems) — 2026-07-20 (act. 2026-11-05) — regulador
- [EUR-Lex — Reglamento (UE) 2026/1744 (Ómnibus Digital)](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng) — 2026-07-24 — regulador
- [Federal Register — FTC rule on consumer reviews and testimonials (16 CFR 465)](https://www.govinfo.gov/content/pkg/FR-2024-08-22/html/2024-18519.htm) — 2024-08-22 — regulador
- [NY Senate — S.8420-A (synthetic performers)](https://www.nysenate.gov/legislation/bills/2025/S8420/amendment/A) — 2025-12-11 — regulador
- [Meta Newsroom — Gen AI transparency in Meta's ads products](https://about.fb.com/news/2025/02/gen-ai-transparency-metas-ads-products/) — 2025-02-03 (act. 2026-06-01) — meta-oficial
- [PPC Land — AI-flagged Meta ad files and C2PA](https://ppc.land/only-2-of-3-379-ai-flagged-meta-ad-files-disclosed-ai-use-resemble-ai-finds/) — 2026-10-27 — prensa
- [PPC Land — Agencies, not clients, usually carry AI label duty (IAB Austria)](https://ppc.land/agencies-not-clients-usually-carry-ai-label-duty-iab-austria-guide-says/) — 2026-09-16 — prensa
- [HeyGen — Avatar consent](https://developers.heygen.com/docs/avatar-consent) y [API pricing](https://help.heygen.com/en/articles/10060327-heygen-api-pricing-explained) — 2026-11-09 — proveedor
- [Gemini API — Voice replication](https://aistudio.google.com/docs/voice-replication) — consultado 2026-11-10 — proveedor
- [Reelmente — UGC con IA vs creador humano](https://reelmente.com/blog/ugc-con-ia-vs-creador-humano) — 2026-10-13 — vendor
