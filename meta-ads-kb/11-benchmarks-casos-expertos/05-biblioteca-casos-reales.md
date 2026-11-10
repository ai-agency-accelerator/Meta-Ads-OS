# Biblioteca de casos reales (fichas completas y valoración de utilidad)

> Última verificación: 2026-10-16 · Autor: A11 (agente) · Ámbito: casos documentados de e-commerce, lead gen, local, high-ticket, B2B/SaaS, infoproductos, apps y mensajería. Cada ficha incluye punto de partida, presupuesto, mercado, oferta, arquitectura, creatividad, cambio, resultado, medición y limitaciones, más una **nota de utilidad (1–5)**. Si falta un dato, se indica.

## TL;DR

- **Casi ningún caso público cumple el estándar completo.** De más de 25 casos revisados, solo un puñado declara presupuesto, diseño de test y método de medición a la vez. Los casos de Meta (Success Stories) no se pudieron leer en texto (requieren sesión) y sus cifras circulan sin metodología. **[EMPIRICAL]**
- **Los casos más útiles son los que miden incrementalidad o reconcilian con el backend:** Fresh Clean Threads (geo-holdout: +23 % de ventas en Amazon y +21 % DTC), Lifepro (el 57,9 % de los pedidos incrementales de Meta ocurrió en Amazon) y la escuela de diseño (el ROMI pasó de "no rentable" a 204 % al cruzar pagos con UTMs por email). **[EMPIRICAL]**
- **Patrón repetido en lead gen:** las mejoras grandes vienen **después del clic** (velocidad de contacto, recordatorios, cualificación) y de **optimizar por calidad**, no del CPL. Ejemplos: cierre del 4 % al 18 % y asistencia del 41 % al 79 % solo con el tiempo de respuesta de 52 h a 47 s; Loomer redujo el gasto en mayores de 65 del 45 % a menos del 2 % con value rules. **[EMPIRICAL]**
- **Patrón repetido en e-commerce:** enviar a Meta la señal correcta (cliente nuevo, compra cobrada, valor) cambia a quién compra. CBazaar: −63 % de nCAC al optimizar solo por compras de clientes nuevos (vendor). **[EMPIRICAL]**
- **Los casos de "consolidación mágica" a presupuesto pequeño** (guantes: CPA de 42 $ → 13 $ con una campaña, un ad set y 50 anuncios) existen, pero tienen confusores y muestras diminutas. Úsalos como hipótesis, no como receta. **[HYPOTHESIS]**
- **Contraejemplos útiles:** un retailer high-ticket (puertas de 1–5 k$) mejoró **segmentando más** (5 estados, campañas 45+, Instagram por separado), y Audience Network aportó el 40 % de los leads cualificados de Insulet con el 41 % del gasto. La regla correcta no es "consolida siempre" ni "excluye AN siempre", sino que depende de la señal y del negocio. **[CONTESTED]**
- **Hueco:** no se encontró ningún caso público completo de app de suscripción ni de SaaS con CRM a cierre. Hay guías con umbrales (RocketShip, Adapty), no casos. **[STRONG INFERENCE]**

---

## Cómo puntuamos la utilidad

| Nota | Criterio |
|---|---|
| 5 | Diseño experimental (holdout, geo-lift, A/B con split), cifras absolutas, contexto completo y fuente con poco interés comercial |
| 4 | Cifras absolutas, contexto casi completo, reconciliación con backend o test parcial |
| 3 | Contexto razonable y cifras relativas; varios cambios a la vez o métrica de plataforma |
| 2 | Pocas cifras, sin presupuesto ni método, vendor con interés directo |
| 1 | Solo titular ("+300 %"), anécdota sin verificar |

---

## A. E-commerce y DTC

### A1. Fresh Clean Threads: el halo de Meta en Amazon (Haus GeoLift)
| Campo | Detalle |
|---|---|
| Modelo / mercado | DTC de ropa masculina premium (camisetas) con web y Amazon. EE. UU. |
| Punto de partida | Sabían que Meta generaba ventas directas, pero no cuánto impulsaba Amazon. Meta era uno de sus canales con más inversión |
| Presupuesto | No declarado |
| Diseño | Geo-holdout: país dividido en tratamiento (con Meta) y control (sin Meta), **10 % de holdout y 3 semanas**. KPI principal: pedidos de Amazon. Secundarios: ingresos de Amazon, ventas e ingresos DTC |
| Resultado | **+23 % de ventas en Amazon y +21 % de ventas DTC** atribuibles a Meta. Al incluir el impacto omnicanal, el iROAS total subió un **14 %** sobre el iROAS solo DTC |
| Decisión | Usar Meta como palanca para escalar Amazon, tratándolo como top-of-funnel omnicanal |
| Limitaciones | No declara gasto, iROAS absoluto, intervalos ni pasos posteriores. Caso publicado por el vendor (abril de 2024) |
| Utilidad | **4/5**: demuestra el método y el orden de magnitud del halo |
| Fuente | [Haus, 30-abr-2024](https://www.haus.io/customer/fresh-clean-threads) |

### A2. Lifepro: Meta escalado para BFCM con MMM calibrado por lift (WorkMagic)
| Campo | Detalle |
|---|---|
| Modelo / mercado | Bienestar y fitness. Shopify + Amazon |
| Punto de partida | El ROAS y el iCPA de Meta "parecían" débiles porque la atribución no veía Amazon, lo que impedía justificar el escalado para BFCM |
| Diseño | Varios lift tests geográficos de pausa (uno en Prime Day) que calibran un MMM. Duración y holdout no declarados |
| Hallazgos | Los pedidos con origen en Meta suponían el 28,2 % de las conversiones de Shopify. **El 57,9 % de los pedidos incrementales de Meta ocurrió en Amazon.** Con el halo, los pedidos atribuibles a Meta subían un 181 % y el iCPA mejoraba un 64,5 % |
| Cambio | **+~200 % de gasto en Meta** en BFCM según la curva de respuesta del MMM, aceptando menor eficiencia a cambio de volumen |
| Resultado | ROAS final dentro de un ~2,2 % de lo que predijo el MMM (valor absoluto no publicado) |
| Limitaciones | Vendor; sin gasto absoluto, sin detalle de holdout y con fechas inconsistentes en la página |
| Utilidad | **3/5**: valida la lógica "medir el halo antes de escalar", sin números auditables |
| Fuente | [WorkMagic](https://www.workmagic.io/case-study/lifepro-meta) |

### A3. Guantes de trabajo premium: consolidación a presupuesto pequeño (Perpetual Traffic, ep. 705)
| Campo | Detalle |
|---|---|
| Modelo / mercado | Fabricante con unos 20 años, nuevo en venta online, AOV de 110–130 $. Probablemente EE. UU. |
| Punto de partida | Campañas manuales de enero a mayo de 2025: unos 4 000 $ de gasto con un **CPA de 42 $**. Promoción del Día de la Madre: unos 1 000 $ con un CPA de 33 $. CPA admisible de cliente nuevo: 45 $ |
| Presupuesto | Unos 1 000 $/mes (unos 45 $/día que luego se duplicaron o triplicaron) |
| Arquitectura | **Una campaña Advantage+ Sales, un ad set, sin targeting ni exclusiones, optimizando por Purchase y sin cost cap.** Se subieron 57 anuncios y se sirvieron 50 |
| Creatividad | Variedad de ángulos: diferenciación, features, persona a cámara, testimonios, UGC, origen ("made in Vermont since 1920"). Educativo, sin descuentos |
| Cambio | Consolidación y diversidad creativa. Sin tocar nada durante 3 semanas |
| Resultado | Unos 1 000 $ de gasto con un **CPA de 13 $** (−75 % frente a la campaña anterior). De 104 a 157 clientes nuevos por semana con unos 650 $ adicionales. +120 % de pedidos interanual en 30 días |
| Limitaciones | **Confusor:** subió también la inversión en Google Brand. Una sola cuenta, unas 3 semanas, reporte verbal del operador y conversiones de Meta modeladas (cruzadas de forma imperfecta con Shopify y Klaviyo) |
| Utilidad | **2/5**: buena hipótesis para cuentas pequeñas sobre-fragmentadas, evidencia débil |
| Fuente | [Perpetual Traffic ep. 705, 13-jun-2025](https://perpetualtraffic.com/podcast/episode-705-killer-meta-advantage-case-study-1-campaign-1-ad-set-50-adswhaa/) |

### A4. CBazaar: optimizar por cliente nuevo para frenar el "retargeting encubierto" (Wicked Reports)
| Campo | Detalle |
|---|---|
| Modelo / mercado | Moda india para la diáspora del sur de Asia (global) |
| Punto de partida | "Great-looking ROAS, flat new customer growth": Meta "ganaba" re-impactando a compradores anteriores |
| Cambio | Envío a Meta de un evento de conversión personalizado **solo para compras de clientes nuevos**, más reglas diarias de escalar, enfriar o matar basadas en el análisis del vendor |
| Resultado (vendor) | +52 % de ingresos de Meta por clientes nuevos, **+127 % de clientes nuevos** desde Meta, **−63 % de nCAC** y −17 % de gasto en Meta |
| Limitaciones | Sin cifras base absolutas ni fechas; no separa el efecto de la señal del de la herramienta de reglas; medición con la propia herramienta del vendor |
| Utilidad | **3/5**: el mecanismo es sólido y coincide con Loomer, con los datos de Haus sobre cuota de nuevos clientes y con el nuevo ajuste *Customer Lifecycle Strategy* de 2026 |
| Fuente | [Wicked Reports](https://www.wickedreports.com/case-studies/advanced-signal/cbazaar) |

### A5. Retailer de puertas y ventanas high-ticket (1–5 k$): de lead gen a e-commerce (UM Marketing)
| Campo | Detalle |
|---|---|
| Modelo / mercado | Retailer "brick-and-click" en EE. UU.; la web generaba sobre todo llamadas |
| Punto de partida | **ROAS de 1,18**. Sin retargeting ni segmentación. Placements automáticos concentrando el gasto en Facebook y descuidando Instagram. Todo EE. UU. |
| Presupuesto | No declarado |
| Oferta | "Compra online y ahorra un 10 %". Retargeting por fases: educativo → 10 % → "última llamada" del 15 % |
| Arquitectura (después) | Retargeting de visitantes y de gente que llamó sin comprar. **Geo reducido a 5 estados rentables. Campañas separadas para 45+. Prospección solo en Instagram** |
| Creatividad | Guías de "mide tu puerta", vídeos de instalación y medidas, UGC de puertas instaladas y comunicación de plazos de entrega |
| Resultado | ROAS de 1,18 → **6,47** en unos 120 días; más de 700 k$ en ingresos |
| Limitaciones | Muchos cambios simultáneos (oferta, geo, segmentación, creatividad), ROAS de plataforma sin ventana declarada y caso de agencia. Al escalar, el algoritmo derivó hacia demografías menos rentables |
| Utilidad | **3/5**: contraejemplo a "consolidar siempre". Con ticket alto, logística regional y señal escasa, **restringir geo y edad por rentabilidad** funcionó (aunque no se aísla el efecto) |
| Fuente | [UM Marketing](https://um.marketing/blog/cases/home-improvement-retailer-case-study/) (sin fecha; imágenes de 2026-03) |

### A6. A.M. Leonard (herramientas de jardinería): Advantage+ Shopping frente a BAU (Wheelhouse DMG)
| Campo | Detalle |
|---|---|
| Resultado | ASC-P: **−33 % de coste por compra** frente a BAU; con catálogo, **−44 %** frente a BAU con catálogo. CPP estable con gasto variable |
| Limitaciones | "Análisis comparativo", no un experimento aleatorizado; sin cifras absolutas, duración ni significancia |
| Utilidad | **2/5** |
| Fuente | [Wheelhouse DMG](https://www.wheelhousedmg.com/case-studies/optimize-advantage-shopping-campaigns/) |

### A7. CTC "Cyber Five 2025": 53 000 anuncios y 147 marcas (dataset agregado)
| Campo | Detalle |
|---|---|
| Muestra | Unos 53 000 anuncios, unas 147 marcas y unos 14,5 M$ de gasto entre Acción de Gracias y Cyber Monday (2025 frente a 2024) |
| Hallazgos | Unos 1 100 anuncios generaron el ~56 % de los ingresos y unos 39 000 gastaron menos de 50 $. Volumen de anuncios ×3–4 interanual. Estáticos +158 % con ROAS −8 %; vídeo +140 % con ROAS estable. UGC: el doble de probabilidad de ser ganador, pero con mayor varianza. **La estrategia de puja cambia el tipo de cliente:** AOV de ~150 $ con ROAS mínimo o cost cap frente a ~50 $ con lowest cost, y CPA aproximadamente el doble |
| Limitaciones | Transcripción de podcast con cifras inconsistentes; clientes de la agencia; correlacional |
| Utilidad | **3/5**: buena evidencia direccional sobre la concentración del gasto y sobre la puja como selector de cliente |
| Fuente | [CTC Ecommerce Playbook, 23-dic-2025](https://commonthreadco.com/blogs/ecommerce-playbook/ads-reveal-metas-andromeda-algorithm) |

## B. Lead gen, local y high-ticket

### B1. Jon Loomer: value rules por edad para leads de calidad (negocio propio)
| Campo | Detalle |
|---|---|
| Modelo | Educación y suscripción del propio Loomer (infoproducto/membresía) |
| Punto de partida | Meta concentraba el presupuesto de leads en **mayores de 65 (45 % del gasto)**, con leads baratos y de baja calidad. Restringir por edad solo movía el gasto a 55–64 y recortaba clientes valiosos |
| Cambio | **Value rules:** puja un 90 % menor en 65+ y un 20 % menor en 55–64, sin excluir a nadie |
| Resultado | El gasto en 65+ pasó del 45 % a **menos del 2 %**. Cualidad medida con un evento "Quality Lead": clic en un email en los 30 días siguientes, enviado vía CRM a Meta |
| Limitaciones | Sin CPL ni coste por lead de calidad publicados; negocio propio de presupuesto modesto |
| Utilidad | **4/5**: mecanismo claro, reproducible y documentado por un practitioner muy transparente |
| Fuente | [Jon Loomer, Master Brief, 2-jul-2026](https://www.jonloomer.com/meta-ads-master-brief/); [Lead Generation, 28-abr-2026](https://www.jonloomer.com/lead-generation-meta-ads/) |

### B2. Clínica de dermatología estética: CPL "sano" con coste por consulta de 440–700 $ (Practice Growth Co)
| Campo | Detalle |
|---|---|
| Modelo / mercado | Dermatología cosmética, suroeste de EE. UU. |
| Punto de partida | 6 meses de Meta: **CPL de ~55 $, 60–70 leads/mes, 3 500 $/mes**. Consultas reservadas estimadas en 5–8 al mes, sin trackear con exactitud |
| Oferta | "Agenda una consulta gratuita en [clínica]", sin tratamiento, resultado ni urgencia concretos |
| Diagnóstico | **Coste real por consulta de 440–700 $** antes de no-shows. El CPL ocultaba el problema |
| Benchmarks del mismo autor (campañas propias 2025-2026) | Med spa: CPL frío de 35–85 $, 25–40 % de tasa de consulta, 110–300 $/consulta. Odontología estética: 45–110 $, 20–35 %, 160–500 $. GLP-1: 25–70 $, 35–55 %, 60–200 $. Cirugía plástica: 85–200 $, 15–25 %, 400–900 $ |
| Lección | Un CPL de 120 $ con un 35 % de consulta (343 $/consulta) supera a uno de 60 $ con un 15 % (400 $/consulta) |
| Limitaciones | Agencia; caso como "antes" sin un "después" cuantificado |
| Utilidad | **3/5**: muy útil como plantilla de diagnóstico de lead gen local |
| Fuente | [Practice Growth Co, 18-may-2026](https://practicegrowthco.com/blog/meta-ads-lead-generation-healthcare) |

### B3. Insulet (Omnipod): Audience Network sí aportaba leads cualificados (Wheelhouse DMG)
| Campo | Detalle |
|---|---|
| Modelo | Dispositivo médico (diabetes). Lead gen |
| Cambio | Advantage+ Shopping para lead gen (ASC-LG) frente a BAU, y después activar Audience Network en BAU |
| Resultado | ASC-LG fue comparable a BAU (no claramente mejor). **Audience Network: el 40 % de los leads cualificados con el 41 % del gasto.** Al activar AN en BAU mejoraron volumen y eficiencia (sin cifras) |
| Limitaciones | Sin cifras absolutas, duración ni diseño experimental |
| Utilidad | **2/5**, pero valioso como contraejemplo a "excluye AN siempre" cuando se mide la **calidad** (lead cualificado) y no el clic |
| Fuente | [Wheelhouse DMG](https://www.wheelhousedmg.com/case-studies/optimize-advantage-shopping-campaigns/) |

### B4. Agencia de coaching B2B (India): la velocidad de contacto multiplica el cierre (Uber Media Labs)
| Campo | Detalle |
|---|---|
| Punto de partida | 9 lakh INR/mes en Meta + LinkedIn. CPL "sano". **Cierre del 4 %, asistencia del 41 %, respuesta media de 52 h** |
| Cambio | Todos los formularios (instant forms de Meta, LinkedIn y landing) a un único pipeline de HubSpot. Agente de voz que llama en menos de 60 s y cualifica con BANT. WhatsApp a T-24 h, T-2 h y T-15 min. Atribución server-side hasta el cierre. Regla de descartar creatividades a las 72 h según **coste por llamada reservada**, no por CPL |
| Resultado | Respuesta de 52 h → **47 s**. Asistencia del 41 % → **79 %**. Cierre del 4 % → **18 %**. **4,5×** de ingresos por rupia invertida. Payback en el día 11 |
| Limitaciones | Vendor, cliente anónimo, sin cifras absolutas y varios cambios simultáneos |
| Utilidad | **3/5**: confirma que el cuello de botella de muchas cuentas de lead gen está después del anuncio |
| Fuente | [Uber Media Labs, 18-sep-2025](https://ubermedialabs.com/case-studies/coaching/coaching-b2b-coaching-agency) |

### B5. Marca de consumo en Emiratos: click-to-WhatsApp y el error del objetivo de tráfico (Kando)
| Campo | Detalle |
|---|---|
| Mercado | Emiratos, anuncios en árabe, jun-jul 2026 |
| Fase 1 (heredada) | 455,68 $ → 75 conversaciones (**6,08 $/conv.**), CPM de 3,40 $ |
| Fase 2 (test de tráfico) | 352,31 $ → **8 134 clics y 0 conversaciones** |
| Fase 3 | Objetivo de conversaciones, presupuesto concentrado en 25–55 años árabe-parlantes (el mejor ad set a 2,89 $/conv.), estático ganador (1,78 $/conv.) y vídeo refrescado al subir la frecuencia de 1,1 a 1,5. 530,55 $ → 139 conversaciones (**3,82 $/conv.**, −37 %) |
| Total | 1 338,55 $ de gasto, 214 conversaciones y **6,26 $/conv. blended** (peor que la fase 1, por el test de tráfico) |
| Limitaciones | Presupuesto diminuto, 8 días en la fase 3, sin medir ventas tras la conversación y caso de vendor |
| Utilidad | **3/5**: cifras absolutas completas. Ilustra de forma nítida que **optimizar por clic no produce conversaciones** |
| Fuente | [Kando Marketing](https://kandomarketing.com/case-studies/meta-whatsapp-turnaround) |

### B6. Tests oficiales de Meta en mensajería (LatAm y Asia)
| Empresa (mercado) | Test | Resultado autodeclarado |
|---|---|---|
| Art di Cacao (México) | Optimizar por compra frente al enfoque habitual | +56 % de compras, +18 % de pedidos |
| Braip (Brasil) | Lead frente a optimización por mensaje | +45 % de leads cualificados, −30 % de CPL |
| Confer On (Indonesia) | Compra frente a conversación | ×3,9 compras, −79 % de coste por compra |
| Nutryfit (India y Golfo) | Lead frente a conversación (A/B del 1 al 18 de abril de 2025) | −12 % de CPL |
| Engelife (Brasil) | WhatsApp Flows frente a cualificación manual | +26 pp de cualificación, −37 % de coste por lead cualificado ("self-reported") |

- **Patrón:** optimizar por el evento de negocio (compra o lead) en lugar de por la conversación mejora el resultado. Coincide con el caso B5. **[OFFICIAL META]** (autodeclarado)
- **Limitaciones:** sin cifras absolutas; casos elegidos por Meta.
- **Utilidad:** **2/5** por caso; **3/5** como patrón.
- **Fuente:** [Spur (recopilación de casos de Meta)](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks)

## C. B2B / SaaS

### C1. 11 marcas B2B (SaaS y fintech, India, 2021-2025): Meta frente a LinkedIn por SQL (ScaleGrowth)
| Campo | Detalle |
|---|---|
| Datos (INR) | Meta: CPM de 85–180, CPL de 250–800, lead→SQL del **8–15 %** y **coste por SQL de 2 500–6 000**. LinkedIn: CPL de 1 200–3 500, lead→SQL del 18–30 % y coste por SQL de 5 000–15 000 |
| Hallazgo | Meta tuvo menor coste por SQL que LinkedIn en **7 de 11 cuentas**. En un holdout de una fintech (Q3 2024), Meta generó el **23 % del pipeline cualificado frente al 6 % que le daba el last-click**. Vídeo del CEO frente a explicativo animado: −42 % de CPL (un cliente). Lookalikes de clientes al 1–3 % como mejor audiencia |
| Qué falló | Imagen de stock corporativa, textos largos, venta enterprise con ciclos de más de 6 meses, sectores regulados con aprobación lenta y testear solo 2 anuncios por trimestre |
| Limitaciones | Agregado de agencia, rangos amplios, SQL sin definir y titulares basados en un solo caso |
| Utilidad | **3/5**: lo más parecido a un dataset B2B con funnel encontrado |
| Fuente | [ScaleGrowth.Digital, 6-feb-2026](https://scalegrowth.digital/meta-ads-b2b-data-real-campaigns/) |

## D. Infoproductos y educación

### D1. Escuela online de diseño de interiores (rusohablantes fuera de Rusia, incluida España): el ROMI aparece al reconciliar (Balandin)
| Campo | Detalle |
|---|---|
| Oferta | Curso principal (~70 000 ₽), webinars de pago, minicursos y maratones (GetCourse). Compras de 3 990 ₽ a 219 000 ₽ |
| Presupuesto 2025 | **12 971 $ en Meta** (9 207 $ en funnels de registro) |
| Arquitectura | (1) Registro directo: webinar en directo, webinar automatizado, lead magnet y funnel temático. (2) Tráfico a perfil y reels de Instagram para calentar durante meses. **4 segmentos de motivación** (baja de maternidad, cambio de carrera, reforma propia), cada uno con vídeo propio de la experta y un ad set de 10 $/día |
| Métricas | Alcance de 2,46 M, CTR del 0,93 %, 22 959 clics, **26 % de clic → registro**, **5 952 registros a 1,55 $** (2,18 $ con el gasto total) |
| Problema inicial | El cliente contaba 15 alumnos del extranjero en 28 meses y concluía que los anuncios no compensaban |
| Cambio | Export de todos los registros y pagos de 2025, cruzados por email con las UTMs: **71 compradores, 39 432 $ de ingresos y ROMI del 204 %**. Pasar a reels orgánicos promocionados tal cual (los estáticos rindieron peor) |
| Limitaciones | Atribución first-touch (sobre-atribuye ventas que habrían ocurrido igualmente); ingresos sin desglose; agencia |
| Utilidad | **4/5**: el caso más completo de infoproducto encontrado. Demuestra que **la plataforma no ve los pagos meses después** y que el ROI de lanzamientos se infravalora sin reconciliación |
| Fuente | [Balandin Agency](https://balandin.agency/cases/interior-design-online-school) |

## E. Apps (sin caso completo; guía de referencia)

- **RocketShip HQ (31-mar-2026, guía, no caso):** optimizar por inicio de trial frente a conversión de pago. Con menos de 1 000 $/día, trial start. Entre 1 000 y 5 000 $/día, testear (pago si trial→paid supera el 50 %). Por encima de 5 000 $/día, pago salvo que trial→paid sea inferior al 30 %. Gasto mínimo por ad set = (50 / tasa trial→paid) × coste por trial / 7. Ejemplo: 50 % y 5 $ → ~71 $/día. Cita una mediana de RevenueCat de trial→paid de ~52 % (25 % en entretenimiento, 70 % o más en salud y fitness). **[EMPIRICAL]** (umbrales de experiencia de la agencia)
- **Adapty (vendor):** el CPI optimizando por compra puede ser entre 5 y 10 veces el de instalación. Un caso pasó de un CPI de 3–5 $ a 8 $ al quitar las "browse installs" (más real). Ponderar trials por LTV movió la entrega a usuarios mayores y triplicó las suscripciones de pago con el mismo gasto (sin datos). **[HYPOTHESIS]**
- **Utilidad:** 2/5. **Hueco:** no hay casos públicos completos de app con CPI→trial→pago y LTV.

## F. Idioma y mercado

### F1. Pearmill: anuncios multi-idioma EN/ES en una cuenta de EE. UU.
| Campo | Detalle |
|---|---|
| Punto de partida | Cuenta con más de 2 años, broad en todos los placements, creatividades refrescadas cada 2 semanas, **frecuencia creciente y CVR cayendo** |
| Diseño | Celda A EN, celda B ES y celda C multi-idioma (un anuncio con versiones servidas según el idioma del dispositivo) |
| Resultado | Multi-idioma: **CPA un 21 % menor** que EN. ES: CTR un 20 % mayor y CPM menor. La frecuencia bajó |
| Limitaciones | 2023; sin duración, gasto, muestra ni significancia; un cliente |
| Utilidad | **2/5**: hipótesis razonable para audiencias hispanas en EE. UU. |
| Fuente | [Pearmill, 3-jul-2023](https://pearmill.com/blog/how-spanish-ads-reduced-cpa-by-20-and-connected-with-a-new-audience) |

## G. Casos metodológicos (cómo no engañarse)

### G1. Loomer, test 5: tres ad sets idénticos con un 25 % de diferencia
- A/B de **3 ad sets idénticos** (mismos anuncios y ajustes). El "ganador" generó un **25 % más** que el peor y Meta le daba un 59 % de probabilidad de volver a ganar. **El azar produce diferencias que parecen reales.** **[EMPIRICAL]**
- Test 4 del mismo artículo (2 250 $): Advantage+ Audience frente a detailed targeting frente a lookalike. A+ ganó por un 5 % y un 25 %, diferencias "negligibles" según el propio Loomer. Con broad, un ~25 % del gasto iba igualmente a visitantes y suscriptores (remarketing implícito).
- **Utilidad:** **5/5** como lección de método: muestras pequeñas = decisiones aleatorias.
- **Fuente:** [Jon Loomer, oct-2024, actualizado en mar-2025](https://www.jonloomer.com/5-meta-ads-tests-targeting/)

### G2. Haus: Advantage+ frente a Manual en tests cara a cara (agregado)
- En tests cara a cara, el **58 %** de las marcas obtuvo mejor iROAS con Manual. A mitad de test Advantage+ iba un 9 % mejor y al final un 12 % peor. Lift post-test del +17 % frente al +32 %. Advantage+ sobre-reportó 12 pp. Ver `07-expertos-mapa-y-discrepancias.md`. **[EMPIRICAL]**
- **Lección:** un test corto o medido solo en plataforma puede dar el ganador contrario.
- **Fuente:** [Haus, jul-2025](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments)

## Patrones transversales

1. **La medición cambia la decisión más que la optimización.** Halo en Amazon (A1, A2), reconciliación de pagos (D1), pipeline en holdout B2B (C1). **[EMPIRICAL]**
2. **Señal > estructura.** Cliente nuevo (A4), lead de calidad (B1), evento de negocio frente a conversación (B5, B6). **[EMPIRICAL]**
3. **Después del clic hay más palanca que en el anuncio en lead gen** (B2, B4). **[EMPIRICAL]**
4. **La consolidación ayuda cuando el problema es falta de datos (A3); la segmentación por rentabilidad ayuda cuando el problema es valor heterogéneo (A5).** Ver la discrepancia en `07`. **[CONTESTED]**
5. **Los casos de vendor y agencia casi nunca aíslan variables:** cambian oferta, creatividad, estructura y medición a la vez. Úsalos para generar hipótesis y valida con tus propios tests. **[STRONG INFERENCE]**

## Implicaciones operativas

- Antes de copiar un caso, comprueba que tu **cuello de botella** es el mismo (datos, señal, creatividad, post-clic, oferta).
- Para cualquier caso propio que quieras usar internamente, documenta la ficha completa: punto de partida, presupuesto, mercado, oferta, arquitectura, creatividad, cambio, resultado, medición y limitaciones.
- Exige reconciliación con el backend o CRM y, a partir de cierto gasto, un holdout.

## Errores frecuentes

- Citar el "+X %" de un caso sin su punto de partida ni su presupuesto.
- Atribuir el resultado al cambio más vistoso (Advantage+) cuando hubo cinco cambios a la vez.
- Ignorar confusores como otros canales que se movieron a la vez (Google Brand en A3).

## Preguntas abiertas

- Casos públicos completos de **app de suscripción** y de **SaaS con CRM hasta el cierre**: no encontrados.
- Casos con un **antes y después de Andromeda** que aíslen el cambio de sistema del cambio creativo: no encontrados.
- Casos de **España y LatAm** con ficha completa: no encontrados en fuentes públicas (solo agencias con titulares).

## Fuentes clave

- [Haus: Fresh Clean Threads](https://www.haus.io/customer/fresh-clean-threads): abr-2024, vendor
- [WorkMagic: Lifepro](https://www.workmagic.io/case-study/lifepro-meta): 2026, vendor
- [Perpetual Traffic ep. 705](https://perpetualtraffic.com/podcast/episode-705-killer-meta-advantage-case-study-1-campaign-1-ad-set-50-adswhaa/): jun-2025, youtube/podcast
- [Wicked Reports: CBazaar](https://www.wickedreports.com/case-studies/advanced-signal/cbazaar): s.f., vendor
- [UM Marketing: Home improvement retailer](https://um.marketing/blog/cases/home-improvement-retailer-case-study/): 2026, agencia
- [Wheelhouse DMG: Advantage+ Shopping](https://www.wheelhousedmg.com/case-studies/optimize-advantage-shopping-campaigns/): s.f., agencia
- [CTC: What 53,000 Ads Reveal](https://commonthreadco.com/blogs/ecommerce-playbook/ads-reveal-metas-andromeda-algorithm): dic-2025, agencia
- [Jon Loomer: Master Brief](https://www.jonloomer.com/meta-ads-master-brief/): jul-2026, practitioner
- [Jon Loomer: 5 Meta Ads Tests](https://www.jonloomer.com/5-meta-ads-tests-targeting/): oct-2024/mar-2025, practitioner
- [Practice Growth Co](https://practicegrowthco.com/blog/meta-ads-lead-generation-healthcare): may-2026, agencia
- [Uber Media Labs](https://ubermedialabs.com/case-studies/coaching/coaching-b2b-coaching-agency): sep-2025, agencia
- [Kando Marketing](https://kandomarketing.com/case-studies/meta-whatsapp-turnaround): 2026, agencia
- [ScaleGrowth.Digital](https://scalegrowth.digital/meta-ads-b2b-data-real-campaigns/): feb-2026, agencia
- [Balandin Agency](https://balandin.agency/cases/interior-design-online-school): 2026, agencia
- [RocketShip HQ: trial vs paid](https://www.rocketshiphq.com/meta-optimize-trial-starts-vs-paid-conversions-ios/): mar-2026, agencia
- [Pearmill](https://pearmill.com/blog/how-spanish-ads-reduced-cpa-by-20-and-connected-with-a-new-audience): jul-2023, agencia
- [Spur: casos de Meta en CTWA](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks): 2026, vendor
