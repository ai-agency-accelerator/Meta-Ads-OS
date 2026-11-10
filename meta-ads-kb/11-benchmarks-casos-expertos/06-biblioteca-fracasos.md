# Biblioteca de fracasos: patrones documentados y cómo detectarlos

> Última verificación: 2026-10-16 · Autor: A11 (agente) · Ámbito: sobresegmentación, fragmentación, demasiados ad sets, pocos eventos, falta de creatividades, tracking roto, leads baratos sin ventas, escalado agresivo, ilusiones de atribución (retargeting y view-through), fallos de automatización y riesgo de plataforma. Cada patrón incluye mecanismo, evidencia, señales de detección y antídoto.

## TL;DR

- **Patrón n.º 1 en 2025-2026: optimizar o juzgar por un evento que no es el negocio.** Clics y conversaciones sin ventas: 8 134 clics y 0 conversaciones en un test de tráfico. Leads baratos de mayores de 65: el 45 % del gasto. ROAS de retargeting inflado: 4,2× en plataforma frente a ~1,1× estimado incremental. Repetición de clientes: "ROAS bonito, clientes nuevos planos". **[EMPIRICAL]**
- **La sobresegmentación tiene evidencia oficial antigua y evidencia nueva coherente.** Meta (2020): "4 de cada 10 anuncios activos no salen de la fase de aprendizaje", por eso limitó los anuncios por página. Loomer: 3 ad sets idénticos difieren un 25 % por azar. Haus: los repartos 50/50 Advantage+/Manual perdieron un 18 % de iROAS frente a repartos sesgados. **[OFFICIAL META]** / **[EMPIRICAL]**
- **La falta de creatividades es medible.** Las ganadoras son el ~5–8 % y la mitad de los anuncios nunca gasta (Motion). Las cuentas del top 25 % lanzan entre 2 y 3 veces más por semana que la media de su tramo. **[EMPIRICAL]**
- **El tracking roto rara vez avisa.** Desde 2026, la API devuelve **datos vacíos sin error** al pedir ventanas eliminadas (7d y 28d view) o desgloses no activados (dispositivo, hora, frecuencia desde el 6-ago-2026). Los fees de localización hacen que "Amount spent" no cuadre con la factura. **[OFFICIAL META]** / **[EMPIRICAL]**
- **El escalado agresivo falla por saturación, frecuencia y aprendizaje, no por "tocar el presupuesto" en sí.** No hay evidencia oficial de la "regla del 20 %". Lo documentado: frecuencia mensual de 7 o más en 9 de las 23 grandes cuentas de Biddyco en agosto de 2026, y CPM casi duplicado al pasar de 2 k$ a 5 k$/día (foro de Shopify). **[EMPIRICAL]** / regla del 20 % **[CONTESTED]**
- **Ilusión de atribución:** en Haus, Advantage+ sobre-reportó 12 pp frente a Manual. En Stella, marcas con ROAS de plataforma superior a 4 tenían un IF inferior a 1. En Seer, retargeting y broad tuvieron la menor incrementalidad. **[EMPIRICAL]**
- **Riesgo de plataforma como fallo de negocio:** en 2026 hubo caídas confirmadas (12-jun, 16-jul, 19-jul, 21-ago y 22-sep) y en algunas no se podía pausar mientras se seguía gastando. No hay un mecanismo público de compensación. Ha habido olas de baneos con apelaciones automatizadas que la Oversight Board calificó de ineficaces (4-jun-2026). **[OFFICIAL META]** / **[EMPIRICAL]**

---

## F1. Sobresegmentación (demasiados ad sets, audiencias y anuncios en paralelo)

**Mecanismo.** Cada ad set compite por los mismos usuarios (solapamiento de subasta) y divide los eventos de conversión. Por debajo de unos 50 eventos por semana y ad set, el sistema no sale de la fase de aprendizaje y las decisiones del media buyer se basan en ruido. **[STRONG INFERENCE]** (umbral de 50 eventos ampliamente citado como guía de Meta; ver área 01)

**Evidencia.**
- **Meta (2020):** al introducir los límites de anuncios por página, Meta explicó que "cuando un anunciante tiene demasiados anuncios a la vez, cada uno se entrega menos… menos anuncios salen del aprendizaje" y que "**4 de cada 10 anuncios activos no salen de la fase de aprendizaje**". Límites de 250 anuncios por página (gasto mensual máximo inferior a 100 k$) hasta 20 000. *Nota:* en septiembre de 2026 se observó en alguna cuenta que el límite ya no se aplicaba (no confirmado por Meta). **[OFFICIAL META]** (vía prensa de la época)
- **Loomer (test 5):** tres ad sets **idénticos** con un 25 % de diferencia de resultados. Fragmentar para "testear audiencias" genera falsos ganadores. **[EMPIRICAL]**
- **Loomer (tests 1-3):** con Advantage+ Audience, alrededor del 74 % del gasto llega a gente fuera de los inputs y un ~25 % se va a visitantes y suscriptores aunque no los segmentes. Separar audiencias "frías" y "calientes" no aísla lo que crees aislar. **[EMPIRICAL]**
- **Haus:** las configuraciones "equilibradas" 50/50 entre Advantage+ y Manual tuvieron un **18 % menos de iROAS** al final de la ventana post-test que las configuraciones con más del 75 % en una táctica. **[EMPIRICAL]**
- **Agencias** (autodeclarado): Elite Brands eliminó 14 ad sets de intereses y consolidó en broad, con un −38 % de coste de adquisición blended y escala de 12 k$ a 30 k$/día. Es promocional y la cronología no está clara. **[HYPOTHESIS]**

**Señales.** Muchos ad sets en "Learning limited". Gasto diario por ad set inferior a 7 veces el CPA objetivo. Audiencias que se solapan mucho. Decisiones de pausar tomadas con menos de 20–30 conversiones.

**Antídoto.** Separar solo por razones de negocio: objetivos distintos, productos, mercados, presupuestos o requisitos legales (Loomer y Foxwell coinciden). Testear creatividades dentro de ad sets con suficiente volumen o con la herramienta de test creativo de Meta, y recordar que 5 anuncios con 50 $/día no tienen potencia estadística (Loomer). **[STRONG INFERENCE]**

**Matiz [CONTESTED].** La consolidación no es universal. El retailer high-ticket (`05`, A5) mejoró al segmentar por estados rentables y por edad, y RocketShip recomienda separar países con más de 3 veces de diferencia de CPI. **La regla es consolidar cuando el problema es la escasez de datos y separar cuando el valor por evento es heterogéneo y el algoritmo no lo ve.**

## F2. Fragmentación de cuentas (varias cuentas o estructuras compitiendo)

**Mecanismo.** Varias cuentas (agencias distintas, países, "cuenta de testing", "cuenta de escalado") pujan por los mismos usuarios, duplican el aprendizaje y diluyen la señal del píxel o del dataset. Además se multiplican los puntos de fallo ante baneos. **[STRONG INFERENCE]**

**Evidencia.** Indirecta: Meta penaliza el solapamiento de subasta dentro de una cuenta (doc. oficial sobre *auction overlap*, ver área 01), y la lógica se extiende entre cuentas de la misma empresa. No se ha encontrado un estudio público que cuantifique el coste entre cuentas. **[HYPOTHESIS]**

**Antídoto.** Una cuenta por divisa o zona horaria y por unidad de negocio con P&L propio. Coordinar agencias para evitar campañas idénticas. Mantener cuentas de respaldo verificadas como gestión de riesgo, no como estructura de escalado. **[STRONG INFERENCE]**

## F3. Muy pocos eventos (optimizar por un evento escaso)

**Mecanismo.** Optimizar por un evento raro (compra de ticket alto, SQL, pago tras trial) con presupuesto insuficiente deja el aprendizaje sin datos. El sistema explora sin converger.

**Evidencia.**
- **RocketShip HQ (2026):** el gasto mínimo por ad set para optimizar por pago es (50 / tasa trial→paid) × coste por trial / 7. Repartir 3 000 $/día en 6 ad sets puede dejar cada uno sin datos suficientes. **[EMPIRICAL]**
- **Jon Loomer:** "optimizar por un evento de calidad (vía CAPI) donde el volumen lo permita (idealmente más de 50 a la semana)". En su prueba, optimizar por "Quality Lead" no siempre mejoró el coste por lead de calidad. **[EMPIRICAL]**

**Antídoto.** Subir en el funnel (add to cart, lead, trial) hasta tener volumen. Usar *conversion leads* o value rules cuando haya señal de CRM. Consolidar para concentrar eventos. Para eventos de alto valor y baja frecuencia, medir con geo-holdout en lugar de con la plataforma. **[STRONG INFERENCE]**

## F4. Creative starvation (falta de creatividades)

**Mecanismo.** El sistema reparte el gasto entre pocos anuncios. Cuando se fatigan, sube el CPM efectivo y baja la CVR. Con el sistema de recuperación actual, los anuncios muy parecidos compiten como si fueran uno (claim de CTC sobre Andromeda: "visually similar ads are grouped into one entity"), así que **volumen sin diversidad no equivale a más oportunidades**. **[STRONG INFERENCE]** (no confirmado por Meta en esos términos; ver área 03)

**Evidencia.**
- **Motion (1 290 M$, 578 750 creatividades):** hit rate del ~5–8 %, la mitad no recibe gasto y las ganadoras se llevan el 55 % del gasto. Top 25 %: entre 2 y 3 veces más lanzamientos por semana que la media del tramo. **[EMPIRICAL]**
- **CTC (170+ marcas, vendor):** las marcas que testean más de 20 anuncios nuevos al mes tienen un **ROAS un 65 % mayor** que las que testean menos de 10. Correlacional y con causalidad inversa probable: las marcas que crecen pueden producir más. **[EMPIRICAL]** (débil)
- **Meta (agosto de 2026):** lanzó una columna de *Creative diversity* (Baja, Media o Alta) en Ads Manager, "estimada y en desarrollo". Cuentas con estáticos, vídeo, UGC y carrusel salieron con puntuación Baja (observado). **[OFFICIAL META]** / **[EMPIRICAL]**
- **Matiz de Loomer:** lanzar 20, 30 o 50 anuncios de golpe "fue un despilfarro". Meta concentra el gasto en unos pocos igualmente, y la fatiga creativa "rara vez es el problema real hoy" salvo que estreches la audiencia. **[CONTESTED]** (ver `07`)

**Señales.** Frecuencia al alza con CTR a la baja. Uno o dos anuncios con más del 80 % del gasto durante semanas. Ningún concepto nuevo en 30 días.

**Antídoto.** Cadencia de conceptos nuevos (no variaciones) proporcional al gasto, como referencia los tramos de Motion. Diversidad de ángulos, formatos y personas. Retirar duplicados casi idénticos. **[STRONG INFERENCE]**

## F5. Tracking roto o inflado

**Mecanismos y evidencia.**

| Fallo | Qué pasa | Evidencia |
|---|---|---|
| **Duplicados Pixel + CAPI sin event_id común** | Las compras se cuentan dos veces, el ROAS se infla y el sistema optimiza hacia los duplicados | Mecanismo documentado por Meta (deduplicación por event_id). Los "casos" de blogs (214 compras reportadas frente a 107 reales) parecen ilustrativos. **[OFFICIAL META]** (mecanismo) / **[HYPOTHESIS]** (cifras) |
| **Eventos en la página equivocada o equipo interno cargando la página de confirmación** | Conversiones fantasma | Loomer: "la mayoría de resultados inflados se deben a errores de configuración". **[EMPIRICAL]** |
| **"Nuevo cliente" mal definido** | Meta contaba compras repetidas como primeras | Search Engine Land (2024): un anunciante detectó que alrededor del 25 % de las compras no-primeras contaban como de clientes nuevos. **[EMPIRICAL]** (no verificado en el texto original por bloqueo 403) |
| **Ventanas de atribución eliminadas en la API** (7d y 28d view, 12-ene-2026) | Los dashboards de terceros muestran caídas del 15–40 % "de la noche a la mañana" o datos vacíos sin error | PPC Land, Dataslayer y otros. **[EMPIRICAL]** (ver área 04) |
| **Desgloses opt-in** (dispositivo, hora, frecuencia) desde el 6-ago-2026 | La API devuelve HTTP 200 con `data` vacío | Documentación de Meta (breakdowns) y changelog. **[OFFICIAL META]** |
| **Fees de localización** fuera del "Amount spent" | El gasto real (factura) es un 2–5 % mayor que el reportado en 6 países | Anuncio de Meta, mar-2026. **[OFFICIAL META]** |
| **Purchase al crear el pedido con pagos diferidos** (OXXO, boleto) | ROAS inflado con pedidos que no se pagan | **[HYPOTHESIS]**: patrón lógico, sin caso documentado |
| **Pagos meses después del primer contacto** (infoproductos) | ROI infravalorado | Escuela de diseño: de "no rentable" a ROMI del 204 % al reconciliar (`05`, D1). **[EMPIRICAL]** |

**Antídoto.** Auditoría mensual del ratio de deduplicación en Events Manager, una compra de prueba, conciliación semanal Ads Manager frente a backend frente a factura, y alertas sobre caídas abruptas de eventos. Ver área 04. **[STRONG INFERENCE]**

## F6. Leads baratos sin ventas

**Mecanismo.** Con el evento "Lead", Meta busca a quien rellena formularios al menor coste. Si el formulario no tiene fricción y la oferta es genérica, eso significa mayores de 65, clics accidentales, Audience Network en algunas cuentas o bots. Después, el equipo comercial tarda horas o días en llamar. **[EMPIRICAL]**

**Evidencia.**
- **Loomer:** mayores de 65 = 45 % del gasto con leads de baja calidad; value rules lo bajaron a menos del 2 %. **[EMPIRICAL]**
- **Loomer (2017, histórico):** al optimizar leads y clics, el 74 % de los registros venía de países con el 3 % de las ventas. **[EMPIRICAL]**
- **Clínica estética:** CPL de 55 $ "sano" con un coste por consulta real de 440–700 $. **[EMPIRICAL]**
- **Coaching B2B:** respuesta de 52 h → 47 s; cierre del 4 % al 18 %. **[EMPIRICAL]**
- **Bots y formularios sin fricción:** los vendors anti-fraude y las agencias describen bots y relleno incentivado. Otras agencias sostienen que la mayoría de los "falsos" son personas reales con autocompletado y sin intención. **No hay datos independientes de un "aumento" en 2025-2026.** **[CONTESTED]**
- **Matiz:** Loomer dice que en sus tests los formularios instantáneos no mostraron la caída de calidad que se suele asumir. Y en Insulet, Audience Network aportó el 40 % de los leads cualificados con el 41 % del gasto. **No todo lead barato es malo, pero sin CRM no lo sabes.** **[CONTESTED]**

**Antídoto.** Formulario *Higher intent* o con preguntas de cualificación. Evento de calidad vía CAPI (Conversions API for CRM y objetivo *conversion leads*). Value rules por edad o placement. SLA de contacto en minutos. Juzgar por coste por oportunidad o por venta. **[STRONG INFERENCE]**

## F7. Escalado agresivo

**Mecanismo.** Al subir el presupuesto, el sistema agota a los usuarios con mayor probabilidad de conversión y entra en usuarios marginales: sube la frecuencia, sube el CPM efectivo y baja la CVR. Los cambios grandes pueden reiniciar el aprendizaje. **[STRONG INFERENCE]**

**Evidencia.**
- **Biddyco (jun-ago 2026, 23 cuentas grandes de EE. UU.):** la frecuencia mensual mediana pasó de 3,9 a 5,1 y en DTC de 4,2 a **7,6** en agosto. **9 cuentas con frecuencia de 7 o más gastaron 5,4 M$ ese mes.** La CVR se mantuvo, lo que sugiere que la saturación no siempre se nota en la CVR a corto plazo. **[EMPIRICAL]**
- **Foro de Shopify:** una campaña buena a 2 000 $/día pasó a 5 000 $/día con ROAS menor y **CPM casi el doble**. Anécdota. **[EMPIRICAL]** (débil)
- **Foxwell (2026):** escalar en incrementos del 20–25 % y esperar antes de recortar. También describe una estructura de puja manual (cap alto con cost o bid cap estricto) que, según él, añade 10–20 k$/día con CPA estable. **[EMPIRICAL]** (practitioner)
- **CTC (2026):** fija presupuestos en ~5 veces el gasto medio con controles de coste como restricción real. El **cost cap (cost per result goal) entregó de media el 140 % del objetivo** (pagas un 40 % más de lo que pides) en 253 cuentas y 200 M$. **[EMPIRICAL]**
- **La "regla del 20 %":** no se ha encontrado documentación oficial de Meta que la fije como umbral de reinicio del aprendizaje. Circula en blogs sin fuente. **[CONTESTED]** (ver área 09)

**Antídoto.** Escalar con creatividad nueva (más conceptos) y con nuevas audiencias o mercados, no solo con presupuesto. Vigilar la frecuencia y el coste marginal, no el medio. Usar controles de coste sabiendo que se desvían (CTC). Medir la incrementalidad del gasto incremental. **[STRONG INFERENCE]**

## F8. Ilusiones de atribución (retargeting, view-through, clientes existentes)

**Mecanismo.** Las campañas cercanas a la compra (retargeting, clientes existentes, view-through) se atribuyen ventas que habrían ocurrido igualmente. Además, Advantage+ Sales sin control envía parte del gasto a clientes existentes porque "convierten mejor".

**Evidencia.**
- **Elite Brands** (calzado, Australia; vendor): 28 días sin Meta en WA, SA y TAS (~20 % de los ingresos), con una caída de ingresos de Shopify de solo ~4 % frente a los 28 días anteriores. **ROAS de Meta de 4,2× frente a un iROAS estimado de ~1,1×.** Eliminaron unos 35 000 $/mes de campañas de retargeting y bottom-funnel y los movieron a prospección broad: +28 % de clientes nuevos en 60 días, menor ROAS de plataforma y mejor MER. Diseño pre/post sin control concurrente. **[EMPIRICAL]** (débil)
- **Haus:** Advantage+ sobre-reportó **12 pp** frente a Manual; por cada 100 $ de ingresos reportados, Manual aportó unos 12 $ más al negocio. **[EMPIRICAL]**
- **Stella:** sin relación lineal entre ROAS de plataforma e IF; hubo marcas con ROAS superior a 4 e IF inferior a 1. **[EMPIRICAL]**
- **Seer (atribución incremental de Meta):** retargeting y segmentos hiper-estrechos fueron los de menor incrementalidad. **[EMPIRICAL]**
- **Loomer:** sin inputs, Meta dedica alrededor del 20–25 % del presupuesto de Sales a remarketing (rango del 10–40 %). **[EMPIRICAL]**
- **CBazaar:** "ROAS bonito, crecimiento de clientes nuevos plano" hasta optimizar solo por clientes nuevos. **[EMPIRICAL]** (vendor)
- **Respuesta de Meta (2026):** *Customer Lifecycle Strategy* a nivel de ad set en campañas Sales manuales, con las opciones solo clientes nuevos, no compradores con engagement o todos. Clientes "nuevos" = sin compra en 180 días según el píxel, CAPI o listas. Se anunció como disponible para todos el 7-oct-2026 según CTC; otras fuentes hablan de despliegue gradual. **[EMPIRICAL]** (no verificado en fuente oficial)

**Antídoto.** Medir el % de nuevos clientes y el nCAC en el backend. Holdouts periódicos de retargeting. Excluir clientes existentes en prospección cuando el objetivo sea adquisición. Evaluar con 1d click frente a 7d click frente a incremental (ver área 04). **[STRONG INFERENCE]**

**Contrapunto [CONTESTED].** Andrew Faris (ago-2026) defiende **gastar en clientes existentes** en negocios de recompra. El problema no es gastar en existentes sino no saber cuánto y si es incremental. Ver `07`.

## F9. Fallos de automatización y creatividad generada por IA

- **Variaciones de IA no deseadas:** True Classic vio cómo un anuncio ganador con un modelo masculino era sustituido por una imagen de IA de una "abuela" (público: hombres de 30 a 45). Kirruna, una pierna torcida. Lectric, un coche volando entre nubes (detectado antes de publicarse). Tres anunciantes dijeron a Business Insider que los toggles de generación se reactivaron solos. Meta respondió que con la generación completa se pueden revisar las imágenes antes. **[EMPIRICAL]** (prensa, finales de 2025 y principios de 2026)
- **Abril de 2026 (Marketing Brew):** una agencia observa redimensionados, fondos alterados y cambios de formato no pedidos (un césped que "crece" dentro de un patio). Otra agencia (Hawke Media), con un 60–70 % de su gasto en Advantage+, ve que la automatización desplaza anuncios a "placements de baja calidad". **[EMPIRICAL]**
- **Julio de 2026:** Advantage+ reescribe por defecto el texto dentro de imágenes subidas (hasta 8 variantes) (Loomer, observado). **Septiembre de 2026:** duplicar un anuncio reactivó música, navegación de productos y promociones (un anunciante en Reddit, vía changelog). **[EMPIRICAL]**
- **Términos de Meta del 30-oct-2026:** incorporan las condiciones de IA generativa a los Self-Serve Ad Terms (confirmado en la página legal de Meta). Blogs afirman que permiten tests de entrega y creatividad sin aviso y que el anunciante responde del contenido generado por IA: **no verificado en el texto oficial**. **[OFFICIAL META]** (fecha) / **[HYPOTHESIS]** (alcance) **Actualización 2026-11-09**: las condiciones nuevas **no entraron en vigor**: se aplazaron al 20-nov y el 5-nov Meta las suspendió hasta nuevo aviso (cautelar en Noruega el 28-oct, investigación de la CMA el 30-oct). Siguen las del 22-ago-2025, que ya permiten a Meta acceder, indexar y rastrear los dominios del anunciante. [OFFICIAL META] (S10-113, S10-114 en `fuentes/ledger-10-cambios-api-ia.md`)

**Antídoto.** Revisión semanal de las mejoras de Advantage+ Creative activas a nivel de anuncio y de cuenta. Desactivar las que no aporten en categorías sensibles. Revisar tras cada duplicado. Previsualizar todas las variantes. **[STRONG INFERENCE]**

## F10. Riesgo de plataforma: caídas, gasto descontrolado y baneos

- **Caídas confirmadas en 2026** (estado de Meta): 12-jun (Ads Manager, unas 4 h), 23–24-jun (varios días), 16-jul (2 h 07 min), 19-jul (2 h 32 min, con reportes de imposibilidad de pausar mientras se gastaba), 21-ago (1 h 49 min) y 22-sep (unas 1,5 h). Marzo de 2026 (vendor): unas 17 h de interrupción de entrega. Meta no ofrece SLA ni compensación pública. **[OFFICIAL META]** (incidentes) / **[EMPIRICAL]** (efectos)
- **Gasto descontrolado:** en 2024, un CMO de suplementos superó el presupuesto en 9 200 $ en pocas horas por un bug, y Meta acreditó a algunos afectados (Marketing Brew). La norma de gasto diario de hasta un 75 % por encima del presupuesto con compensación semanal es la más citada. Afirmaciones de "50×" en blogs sin fuente oficial. **[EMPIRICAL]** / **[CONTESTED]**
- **Baneos:** en 2025 hubo olas masivas con peticiones de más de 25 000 a más de 43 500 firmas y suscriptores de Meta Verified sin soporte efectivo (TechCrunch). La Oversight Board (4-jun-2026) concluyó que las apelaciones que repiten el mismo proceso automatizado "no son efectivas" y pidió revisión humana en casos límite. Más de 750 comentarios públicos describen sistemas que "simplemente no funcionaban". **[OFFICIAL META]** (Oversight Board) / **[EMPIRICAL]**

**Antídoto.** Business Manager con admins de respaldo verificados. Límites de gasto de cuenta. Alertas externas de gasto por hora. Plan de contingencia (otras cuentas o canales). Documentar el gasto durante las caídas para reclamar. **[STRONG INFERENCE]**

## Matriz rápida de diagnóstico

| Síntoma | Fallo probable | Primera comprobación |
|---|---|---|
| CPL bajando y ventas iguales | F6 | Desglose por edad, placement y país; tiempo de respuesta comercial |
| ROAS de plataforma alto y MER del negocio bajando | F8 / F5 | % de nuevos clientes, deduplicación, retargeting |
| Muchos ad sets en *Learning limited* | F1 / F3 | Eventos por semana y ad set |
| CTR cayendo y frecuencia subiendo | F4 / F7 | Edad de las creatividades y cuota de gasto del top 1–2 |
| Dashboard con caídas del 15–40 % sin cambios en la cuenta | F5 (API, ventanas o desgloses) | Configuración de atribución y opt-in de desgloses en la API |
| Factura mayor que "Amount spent" | F5 (fees) | Países con fee de localización |
| Anuncios "raros" en circulación | F9 | Mejoras de Advantage+ Creative a nivel de anuncio y de cuenta |

## Preguntas abiertas

- ¿Cuánto cuesta realmente la fragmentación entre cuentas de una misma empresa? No hay un estudio público.
- ¿Existe un umbral oficial actual de "cambio significativo" de presupuesto que reinicie el aprendizaje? (área 01/09)
- ¿Cuál es la magnitud real de los leads de bots frente a los leads humanos sin intención? No hay datos independientes.

## Fuentes clave

- [Social Media Today: límites de anuncios por página (2020)](https://www.socialmediatoday.com/news/facebook-announces-new-limits-on-how-many-ads-pages-can-run-concurrently/584943/): sep-2020, prensa
- [PPC Land: el límite de 250 anuncios por página deja de aplicarse en algunas cuentas](https://ppc.land/meta-drops-250-ad-page-cap-in-some-accounts-as-286-ads-keep-running/): 23-sep-2026, prensa
- [Jon Loomer: 5 Meta Ads Tests](https://www.jonloomer.com/5-meta-ads-tests-targeting/): 2024/2025, practitioner
- [Jon Loomer: Master Brief](https://www.jonloomer.com/meta-ads-master-brief/): jul-2026, practitioner
- [Haus: The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments): jul-2025, vendor
- [Stella: incrementality study](https://www.stellaheystella.com/blog/incrementality-study-how-incremental-is-meta-really): 2025, vendor
- [Seer Interactive: incremental attribution](https://www.seerinteractive.com/insights/we-tested-metas-new-incremental-attribution-setting-on-1m-in-ad-spend.-heres-how-it-works): jul-2025, agencia
- [Elite Brands: blackout test](https://www.elitebrands.org/blog/measure-incremental-conversions-meta-ads): oct-2026, agencia
- [Motion: Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/): 2026, vendor
- [CTC: Meta cost controls study](https://commonthreadco.com/blogs/coachs-corner/meta-cost-controls-study-taylor-holiday-andrew-faris): 6-ago-2026, agencia
- [Biddyco: Meta Ads Benchmarks 2026](https://www.biddyco.com/blog-posts/meta-ads-benchmarks): 2026, agencia
- [Shopify Community: results dropping with increased budget](https://community.shopify.com/t/meta-ads-campaign-results-dropping-with-increased-budget/403454): 2025, comunidad
- [Shopifreaks (resumen de Business Insider): unwanted AI creative](https://www.shopifreaks.com/meta-advantage-is-forcing-unwanted-ai-creative-on-brands/): 5-ene-2026, prensa
- [Marketing Brew: Meta AI creative tools](https://www.marketingbrew.com/stories/2026/04/21/meta-ai-creative-tools-marketer-response): 21-abr-2026, prensa
- [Marketing Brew: Meta AI ad creation](https://www.marketingbrew.com/stories/2026/04/07/meta-ai-ad-creation): 7-abr-2026, prensa
- [Marketing Brew: bugs de Meta (2024)](https://www.marketingbrew.com/stories/2024/09/19/it-can-crush-our-business-ad-buyers-estimate-major-losses-from-meta-ad-platform-bugs): sep-2024, prensa
- [admakeai: changelogs de julio, agosto, septiembre y octubre de 2026](https://admakeai.com/blog/meta-ads-updates-august-2026): 2026, vendor
- [Oversight Board / Medianama: decisión sobre baneos (jun-2026)](https://www.medianama.com/2026/06/223-meta-oversight-board-users-informed-government-requests-lead-account-ban/): jun-2026, prensa
- [TechCrunch: ola de baneos y Meta Verified (2025)](https://techcrunch.com/?p=3024193): 2025, prensa
- [Meta: Ad Creative Generative AI Terms](https://www.facebook.com/legal/terms/ad_creative_generative_ai_terms): vigente desde el 30-oct-2026, meta-oficial (2026-11-09: su incorporación a las condiciones de autoservicio quedó suspendida, S10-113)
- [CTC: Customer Lifecycle Strategy](https://commonthreadco.com/blogs/coachs-corner/meta-customer-lifecycle-strategy-all-advertisers-bfcm-2026): 11-oct-2026, agencia
