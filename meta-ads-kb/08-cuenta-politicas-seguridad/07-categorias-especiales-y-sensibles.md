# Special Ad Categories y políticas sensibles: atributos personales, salud, finanzas, cripto, alcohol, juego, SIEP en la UE

> Última verificación: 2026-10-15 · Autor: A08 (agente) · Ámbito: Special Ad Categories (vivienda, empleo, productos y servicios financieros, SIEP), fin de SIEP en la UE y efecto en anunciantes españoles, Personal Attributes (con muchos ejemplos ES/EN), Health & Wellness (pérdida de peso, cosmética, suplementos, antes/después, imagen corporal, restricciones de datos de 2025), Financial/Crypto, Drugs, Addiction, Alcohol, Gambling, Dating, Suicide/Eating Disorders. Señales de cuándo hace falta asesoría legal.

## TL;DR

- **Special Ad Categories (SAC) actuales:** `HOUSING`, `EMPLOYMENT`, `FINANCIAL_PRODUCTS_SERVICES` (sustituyó a `CREDIT` el 14-ene-2025), `ISSUES_ELECTIONS_POLITICS` y `NONE`.
  - En **España/Europa** es obligatorio marcar SAC para **crédito, empleo y vivienda**.
  - En EE. UU., además, para cualquier producto o servicio financiero (desde el 21-ene-2025).
  - Restricciones con SAC: edad 18-65+, sin género, radio ≥15 km, sin exclusiones de detailed targeting, sin lookalikes.

  **[OFFICIAL META]** ([S08-003], [S08-061])
- **Formación de empleo:** la categoría *Employment* incluye "programas de certificación profesional", "entrevistas garantizadas o colocación" y bolsas de empleo. **No incluye** "consejos generales para triunfar en el trabajo" ni "desarrollo profesional sin ofertas concretas". Un bootcamp que vende "colocación garantizada" cae en SAC de empleo (y roza el "guaranteed jobs" de Prohibited Commercial Practices). **[OFFICIAL META]** ([S08-061], [S08-067])
- **UE (desde el 6-oct-2025): no se pueden crear ni editar anuncios SIEP.** Los "temas sociales" de la UE incluyen **Economía, Salud, Inmigración, Medio ambiente, Derechos civiles, Crimen, Valores políticos y Seguridad**.
  - Un anuncio que "toma posición" o aboga sobre esos temas se rechaza. Ejemplos: "la inflación te está robando: el Gobierno no te protegerá", "la sanidad pública no funciona: aprende a…".
  - Un anuncio comercial que solo vende un curso de finanzas no debería serlo. La frontera está en el **tono de advocacy**.

  **[OFFICIAL META]** ([S08-063], [S08-064]); frontera **[STRONG INFERENCE]**
- **Personal Attributes es la política que más rechazos "tontos" genera en infoproductos.** Prohíbe afirmar o implicar que el espectador tiene un atributo: edad, salud física o mental, **situación financiera vulnerable**, religión, orientación sexual, discapacidad, antecedentes penales, nombre, etc. Incluye **preguntas** ("¿Estás arruinado?"). El "tú" está permitido si no va unido a un atributo. **[OFFICIAL META]** ([S08-028], [S08-074])
- **Health & Wellness (vigente, change log 22-jul-2026):**
  - 18+ para productos dietéticos, de salud y de peso, y para cosmética.
  - **Prohibido:** primer plano de pellizcar grasa, wearables como única causa de resultados, "statements of inferiority" sobre la apariencia, curar enfermedades incurables listadas, clickbait de salud con resultados en un plazo **sin matices**.
  - **Permitido (18+):** suplementos y servicios de peso mostrando uso, impacto y tiempo hasta resultados visibles, y antes/después en cosmética general.
  - Además, Suicide/Self-Injury/Eating Disorders prohíbe "admisiones de conductas de pérdida de peso extrema" y antes/después de peso **no ligados a un producto o servicio**.

  **[OFFICIAL META]** ([S08-065], [S08-029], [S08-123])
- **Datos y optimización en salud (2025):** muchos anunciantes de salud y bienestar no pueden enviar ni optimizar a eventos de mitad o final de funnel (Purchase, Lead, CompleteRegistration…). Pueden usar LPV, ViewContent, Search y custom events registrados sin información sensible, y en casos graves no envían nada. Meta lo presentó como "clarifying guidance" para no recibir información sensible. **[EMPIRICAL]** + declaración de Meta ([S08-004], [S08-005], [S08-095])
- **Financial & Insurance:**
  - **prohibidos:** payday, préstamos a ≤90 días, **opciones binarias, CFDs, ICOs** y subastas de pago por puja;
  - **restringido:** 18+ y disclosures legales;
  - EE. UU.: los anuncios de inversión **no pueden sugerir interacción por mensajería directa**;
  - verificación o licencia por país (España incluida).

  **[OFFICIAL META]** ([S08-066], [S08-011])
- **Cripto:** autorización previa con licencia. **Juego online:** autorización previa con licencia por jurisdicción, 18+. **Alcohol:** 18+ como mínimo y ley local. **Fármacos con receta:** solo EE. UU./Canadá/NZ con LegitScript. **Tratamiento de adicciones en EE. UU.:** LegitScript + permiso. **[OFFICIAL META]** ([S08-062], [S08-071], [S08-072], [S08-124], [S08-115])
- **Asesoría legal obligatoria** cuando el anuncio toca salud (medicamentos, productos sanitarios, claims de salud), inversión o crédito (CNMV, Banco de España), cripto (publicidad de criptoactivos), juego (DGOJ, normativa de comunicaciones comerciales del juego), alcohol, empleo (claims de colocación) o menores. Meta exige cumplir la ley local, pero no la revisa por ti.

## 1. Special Ad Categories

### 1.1 Qué cubre cada una (ejemplos oficiales)

| SAC | Incluye | No incluye |
|---|---|---|
| **Financial products and services** (crédito en ES/UE; todo lo financiero en EE. UU.) | Tarjetas de crédito (incluidos brand ads), préstamos (coche, hipoteca, personal, empresa), financiación a largo plazo, recobro, consolidación de deudas. En EE. UU. también: cuentas bancarias, prepago, inversión, pensiones, seguros, pagos, **BNPL y pagos a plazos 0 % (también in-house)** | Gift cards, recompensas de tienda, productos financieros solo B2B, servicios fiscales y contables |
| **Housing** | Venta o alquiler, seguros de hogar o alquiler, hipotecas, tasación, búsqueda de vivienda, agregadores | Hoteles, resorts, retiros, consejos sobre comprar casa, educación sobre derechos de vivienda |
| **Employment** | Empleo a tiempo completo o parcial, prácticas, aprendizaje, **programas de certificación profesional**, ferias, bolsas de empleo, **entrevistas garantizadas o colocación**, beneficios de la empresa junto a ofertas | Consejos generales de carrera sin ofertas, hablar de la empresa sin ofertas |
| **SIEP** | Temas sociales, elecciones, política (con autorización y disclaimer) | — (en la UE no se permite) |

Fuente: [S08-061]. **[OFFICIAL META]**

**Casos frontera en infoproductos** (**[STRONG INFERENCE]**, validar caso a caso):
- *Pago fraccionado de un curso* ("paga en 3 plazos sin intereses"): en EE. UU. el BNPL y los plazos al 0 % están en el SAC financiero; en España/UE solo el **crédito** es obligatorio. Si el plazo implica financiación (financiera externa, Sequra/Klarna/Aplazame), conviene tratarlo como crédito y revisar con un abogado. Mencionar "financiación" en el anuncio aumenta la probabilidad de clasificación.
- *Bootcamps o cursos con "salida laboral garantizada"*: SAC Employment + riesgo PCP ("Offers of guaranteed jobs"). Mejor no garantizar.
- *Cursos para opositores, inmobiliaria o "invertir en pisos"*: inversión inmobiliaria ≠ vivienda (housing es para quien busca vivienda), pero "invertir para obtener rentas" entra en terreno de inversión y PCP.

### 1.2 Restricciones de audiencia con SAC

Edad generalmente 18-65+ (con excepciones para crédito en Europa), **sin selección de género**, ubicación con radio mínimo de **15 km en Europa** (25 km en EE. UU./Canadá) y sin exclusiones de ubicación, sin targeting demográfico ni de comportamiento, intereses solo de una lista aprobada, **sin lookalikes**. Si no se marca la SAC cuando aplica, el anuncio puede ser rechazado. Además, una campaña SIEP no puede mezclarse con anuncios no SIEP. **[OFFICIAL META]** ([S08-003])

### 1.3 SIEP y la UE (TTPA)

- **Desde el 6-oct-2025**, los anuncios políticos, electorales y de temas sociales **no se entregan en la UE**. No se pueden crear ni editar. Los anuncios activos con "Paid for by" fueron rechazados. Los anuncios sin disclaimer detectados como SIEP se rechazan y se retiran. El orgánico no se ve afectado. Excepción: autoridades electorales con información logística de voto. **[OFFICIAL META]** ([S08-002], [S08-064], [S08-073], [S08-106])
- **Temas sociales UE (lista oficial):** derechos civiles y sociales, crimen, **economía**, política medioambiental, **salud**, inmigración, valores políticos y gobernanza, seguridad y política exterior. "Educación" no figura en la lista de la UE (sí en otros países). **[OFFICIAL META]** ([S08-063])
- **Definición:** temas "muy debatidos" que pueden influir en elecciones o se relacionan con legislación; anuncios que buscan influir en la opinión pública mediante discusión, debate o *advocacy*. **[OFFICIAL META]** ([S08-063])
- **Efecto real:**
  - Una auditoría (Irish Times, sep-2026) encontró anuncios políticos que seguían corriendo y que Meta retiró a posteriori. Esto indica infra-detección más que sobre-bloqueo. **[EMPIRICAL]** ([S08-107])
  - Un estudio académico de 2023-2024 (antes del veto) halló >60 % de falsos positivos entre los anuncios marcados como políticos en la UE. **[EMPIRICAL — académico, pre-veto]**
  - No hemos encontrado datos sobre rechazos de anunciantes comerciales tras el veto. **[HYPOTHESIS]**: el riesgo existe en ángulos de "crítica al sistema".

**Cómo evitar que un anuncio comercial parezca "social issue" en la UE** (**[STRONG INFERENCE]**):

| Rechazable (tono de advocacy o tema social) | Compliant (comercial y centrado en la oferta) |
|---|---|
| "El sistema de pensiones va a quebrar y los políticos lo saben. Protégete." | "Curso de planificación financiera personal: aprende a calcular tu jubilación y a organizar tus ahorros." |
| "La inflación es un impuesto oculto del Gobierno contra la clase media." | "Taller práctico: cómo ajustar tu presupuesto familiar cuando suben los precios." |
| "La sanidad pública te ha abandonado: toma el control de tu salud." | "Programa de hábitos de sueño y alimentación con seguimiento de un nutricionista colegiado." |
| "Vote with your wallet: support small businesses against Big Tech." | "Online course for small business owners: build your first email list in 30 days." |
| "Stop the climate crisis: join our movement and learn solar installation." | "Professional solar installation course: 40 hours of practice, certificate on completion." |

## 2. Privacy Violations and Personal Attributes

**Regla oficial:** los anuncios no deben "afirmar o implicar atributos personales" del espectador, ni pedir o compartir información privada. Atributos protegidos:
- raza, etnia, color, origen nacional;
- religión, creencias;
- **edad**, sexo, orientación sexual, identidad de género, situación familiar;
- discapacidad, condición médica o genética, **salud física o mental**;
- **situación financiera vulnerable**;
- situación de voto, afiliación sindical, antecedentes penales, **nombre**.

También prohíbe hacerlo "de forma alternativa", por ejemplo con **preguntas**.

**Permitido:**
- "tú/tu" si no va unido a un atributo;
- referencias amplias a atributos no listados;
- **referencias de pasada** a género, grupos o rangos de edad.

Ejemplos oficiales permitidos: "Meet seniors", "Find black singles today". Prohibidos: "Meet *other* seniors", "Are you 18 years old?", "Do you have diabetes?", "Are you bankrupt?". **[OFFICIAL META]** ([S08-028], [S08-074])

Por qué existe: además de la privacidad, Meta dice que los anuncios que implican atributos tienen peor engagement (menos clics y conversiones). **[OFFICIAL META]** ([S08-028])

### 2.1 Banco de ejemplos para infoproductos y servicios (ES/EN)

Ejemplos elaborados aplicando la regla oficial. **[STRONG INFERENCE]** salvo los marcados **[OFFICIAL META]**.

| Atributo | Rechazable | Compliant |
|---|---|---|
| Situación financiera | "¿Estás endeudado hasta las cejas? Te ayudamos." | "Método en 5 pasos para ordenar deudas: guía gratuita." |
| Situación financiera | "Are you broke and tired of living paycheck to paycheck?" | "A practical budgeting system used by 2,000+ students. Free workshop." |
| Situación financiera | "Si cobras menos de 1.500 €, este curso es para ti." | "Curso de habilidades digitales con alta demanda en el mercado laboral." |
| Situación financiera | "¿Te han despedido? Empieza tu negocio online." | "Cómo validar una idea de negocio online antes de invertir: masterclass." |
| Edad | "¿Tienes más de 40 y crees que es tarde para emprender?" | "Emprender después de los 40: historias reales y un plan paso a paso." (referencia de pasada a un rango, sin "tú tienes") |
| Edad | "As a 50-year-old woman, you need this program." | "A strength program designed for women in midlife." |
| Salud mental | "¿Sufres ansiedad todos los días?" | "Técnicas de respiración y gestión del estrés: taller práctico." |
| Salud mental | "Tired of your depression? Call us." **[OFFICIAL META]** (variante del ejemplo oficial) | "Learn evidence-based tools to manage stress. Free webinar." |
| Salud física | "¿Tienes diabetes? Este método la revierte." | "Talleres de cocina saludable con pautas de un dietista-nutricionista." (sin claim de cura; la "cura" de la diabetes además está prohibida en Health) |
| Peso / apariencia | "¿Odias verte en el espejo con esa barriga?" | "Programa de entrenamiento de 12 semanas con plan de nutrición adaptable." |
| Discapacidad | "Are you disabled? We can help!" **[OFFICIAL META]** | "Accessible training programs with adapted materials." |
| Antecedentes penales | "¿Tus antecedentes te impiden encontrar trabajo?" | "Programa de reinserción laboral: formación y acompañamiento." |
| Religión / origen | "Para musulmanes que quieren invertir halal." | "Inversión con criterios éticos y finanzas islámicas: curso introductorio." |
| Orientación sexual | "Meet other LGBTQ singles on our app." **[OFFICIAL META]** | "A dating community celebrating every kind of love." |
| Situación familiar | "Madre soltera y sin tiempo: este negocio es para ti." | "Negocios online compatibles con horarios flexibles: casos reales." |
| Nombre | "Laura, este anuncio es para ti." | "Este anuncio es para emprendedores que quieren vender online." |
| Empleo / situación laboral | "¿Estás en paro?" | "Formación en marketing digital con prácticas en empresa." (y SAC de empleo si se ofertan puestos) |

**Patrones seguros:**
1. Hablar del **programa, el método, el resultado del proceso o el público en tercera persona** ("para emprendedores que…").
2. Usar "tú" con **acciones o deseos** ("¿Quieres lanzar tu primera campaña?"), no con condiciones ("¿Estás arruinado?").
3. En creatividades, **no superponer texto que nombre la condición** sobre una persona que mira a cámara.

## 3. Health & Wellness (y las restricciones de datos de 2025)

### 3.1 Política de contenido (vigente)

Según [S08-065] y [S08-029] **[OFFICIAL META]**:
- **18+ obligatorio:** productos o servicios dietéticos, de salud, de pérdida o ganancia de peso, y cosmética (productos, procedimientos, cirugías).
  - **Exentos del 18+:** bienestar general, alimentos generales (incl. proteína), cosmética no permanente y productos dentales (p. ej. blanqueamiento) (cambio del 22-jul-2026).
- **Prohibido:**
  - primer plano de una zona corporal **pellizcando grasa**;
  - afirmar que los resultados se logran **solo con un wearable**;
  - **"statements of inferiority"**: términos, descripciones o **preguntas** negativas que atacan la apariencia, partes del cuerpo o la higiene;
  - blanqueamiento de piel permanente;
  - afirmar **curar o eliminar** (aunque lo diga un profesional) diabetes, herpes, tiroides, psoriasis, ébola, cáncer, autismo, alzhéimer, párkinson, ELA o VIH (sí se permite hablar de tratar o manejar síntomas);
  - **clickbait** en salud o peso: lenguaje sensacionalista, claims extremos o "promesas de resultados concretos en un plazo **sin disclaimers ni matices**".
- **Permitido (18+):**
  - suplementos o servicios de peso mostrando uso, impacto y "una indicación clara del tiempo para ver resultados apreciables";
  - procedimientos cosméticos (la lista oficial incluye rinoplastia, rellenos, láser, etc.);
  - **antes/después en cosmética general**.
- **Salud sexual y reproductiva:** permitida con 18+ si se centra en la salud y no en el placer.
- **Suicide/Self-Injury/Eating Disorders:** prohíbe "admisiones de conductas de pérdida de peso extrema", imágenes de costillas o huesos marcados en contexto de recuperación y **antes/después de peso no relacionados con un producto o servicio** (los relacionados se rigen por Health & Wellness). **[OFFICIAL META]** ([S08-123])

**Coaching de fitness, nutrición y salud: guía rápida** (**[STRONG INFERENCE]** a partir de las reglas):

| Rechazable | Compliant |
|---|---|
| "Pierde 10 kg en 30 días garantizado." | "Programa de 12 semanas: plan de entrenamiento + menús. Los resultados dependen de tu punto de partida y adherencia." |
| Primer plano de una mano pellizcando grasa abdominal | Persona entrenando o cocinando; gráfico del plan semanal |
| "¿Te avergüenza tu cuerpo en la playa?" | "Gana fuerza y energía con 3 entrenamientos de 30 minutos por semana." |
| "Esta faja reduce cintura sin hacer nada." | (Evitar: "wearable como única causa") |
| "Cura tu tiroides con alimentación." | "Alimentación para acompañar tu tratamiento médico de tiroides: consulta siempre a tu endocrino." |
| "Lose 20 lbs fast with this one trick doctors hate." | "A structured 12-week nutrition program. Individual results vary." |
| Antes/después de pérdida de peso extrema, sin contexto | Antes/después de un cliente real del programa, con plazo realista, consentimiento y nota de que los resultados varían (y 18+) |

Notas: (a) incluir el plazo **con matices** está permitido por la propia política; prometer un resultado concreto en un plazo **sin** matices no lo está. (b) En España, los claims de salud y los productos sanitarios tienen normativa propia (asesoría legal).

### 3.2 Restricciones de datos para salud y bienestar (ene-2025)

- **Qué pasa:** Meta clasifica los *data sources* (píxel/dataset) por categoría. En salud y bienestar (y según vendors también finanzas y otras) aplica niveles:
  1. **Core setup:** se bloquean parámetros personalizados y la URL tras el dominio, lo que reduce audiencias y advanced matching.
  2. **Restricción de eventos estándar de mitad o final de funnel:** Purchase, AddToCart, CompleteRegistration, Lead, Contact, AddPaymentInfo, Schedule…
  3. **Restricción total.**

  Pueden seguir usándose PageView, ViewContent, Search y **custom events registrados** sin información sensible. **[EMPIRICAL]** ([S08-005], [S08-095])
- **Postura de Meta:** "clarifying guidance" para evitar que los anunciantes le envíen información sensible mediante las Business Tools; reafirma una política existente. **[OFFICIAL META vía Digiday]** ([S08-004])
- **Dónde verlo:** Events Manager → data source → Settings → "Manage data source categories". Se puede apelar, aunque según vendors rara vez prospera (3-7 días). **[EMPIRICAL]** ([S08-095])
- **Advertencia de cumplimiento:** renombrar eventos de compra con nombres "neutros" para esquivar la restricción de un data source **categorizado como salud** puede considerarse circunvención y además seguir enviando información sensible. Es mejor microsites o dominios de contenido no sanitario con oferta no sanitaria real, o bien optimizar a eventos permitidos. **[STRONG INFERENCE]** (ver [10](10-landing-pages-y-politicas.md)) Detalle técnico en el área 04 (tracking).
- **Quién cae en esto dentro de infoproductos:** coaches de nutrición o pérdida de peso, salud hormonal o femenina, fertilidad, psicología o terapia, adicciones, sueño, salud mental. Un vendor reporta categorizaciones erróneas en marcas de suplementos o "almohadas ergonómicas". **[EMPIRICAL]** ([S08-095])

## 4. Finanzas, inversión y cripto

**Financial and Insurance Products and Services** ([S08-066]) **[OFFICIAL META]**:
- **Prohibido:**
  - payday loans, adelantos de nómina, fianzas;
  - préstamos a devolver en ≤90 días;
  - consolidación, condonación o refinanciación de préstamos estudiantiles con prácticas engañosas;
  - **opciones binarias, CFDs ("Promote Contract for Difference trading")**, **ICOs**;
  - subastas de pago por puja.
- **Restringido** (tarjetas, seguros, préstamos >90 días): 18+, **disclosures legales** y sin pedir datos financieros o PII en el anuncio.
- **EE. UU.:** anuncios de productos u oportunidades de inversión **no pueden sugerir interacción con el anunciante por mensajería directa** (on/off-platform). Es la firma clásica de los scams de "grupo de WhatsApp de inversión".
- **Verificación y licencia:** pueden exigirse según el país; España está en la lista ([02](02-verificaciones.md)).
- **Exentos:** brand ads, noticias, educación sobre préstamos y anuncios que mencionan un producto sin forma de obtenerlo.
- Change log con cambios en nov-2025, dic-2025, mar-2026 (×2) y abr-2026, sin detalle público.

**Prohibited Commercial Practices aplicado a inversión** ([S08-067]) **[OFFICIAL META]**:
- retornos garantizados o sin riesgo;
- retornos o compensación basados en el reclutamiento;
- **"claiming or referencing successful past performance or returns to create an expectation of similar future results"**;
- retornos rápidos (p. ej. <24 h);
- "cash flip / money flip".

**Cripto** ([S08-062]) **[OFFICIAL META]**:
- autorización previa con licencia (traducción jurada si no está en inglés);
- revisión ~48 h hábiles;
- ETFs de acciones de empresas cripto y NFTs: sin autorización "por ahora";
- ETFs que contienen cripto: con autorización;
- además deben cumplirse PCP y la política financiera.

**Cursos de trading, cripto e inversión** (**[STRONG INFERENCE]**):

| Riesgo alto (rechazo, restricción o investigación) | Más seguro |
|---|---|
| "Mis alumnos ganan un 8 % mensual con mi estrategia." (rendimiento pasado → expectativa) | "Aprende análisis técnico desde cero: 20 h de vídeo, ejercicios y simulador." |
| Capturas de P&L, broker o "+3.200 € hoy" | Capturas del temario, la plataforma del curso o las clases en directo |
| "Únete a mi grupo de señales de Telegram/WhatsApp" | "Comunidad de alumnos para resolver dudas del temario" (sin señales ni recomendaciones de inversión) |
| Enlace de afiliado a broker de CFDs | Sin promoción de productos concretos; disclaimer de riesgo |
| "Sin riesgo", "método infalible", "dinero mientras duermes" | "Invertir conlleva riesgo de pérdida. Este curso es formativo y no constituye asesoramiento." |
| Copy-trading o gestión de capital de alumnos | (Actividad regulada: asesoría legal y licencia) |

**España:** la publicidad de servicios de inversión y de criptoactivos está supervisada por la CNMV (incluida su normativa específica sobre publicidad de criptoactivos) y el crédito al consumo por el Banco de España. **Asesoría legal imprescindible** antes de anunciar cualquier cosa que no sea educación pura.

## 5. Otros restringidos relevantes

| Política | Regla clave | Implicación en este nicho |
|---|---|---|
| **Alcohol** | 18+ mínimo; edades superiores en algunos países; prohibido en una lista de países; cumplir la ley local | Cursos de enología, coctelería o eventos con alcohol: 18+ y normativa española de publicidad de alcohol (asesoría) **[OFFICIAL META]** ([S08-072]) |
| **Online Gambling and Games** | Autorización previa con licencia por jurisdicción; declarar nuevas jurisdicciones; 18+; 19 mercados no soportados; landings de afiliados también cuentan | Cursos de "apuestas de valor", tipsters o "trading deportivo" = alto riesgo de que se clasifiquen como promoción de juego; en España la publicidad del juego está muy regulada (asesoría) **[OFFICIAL META]** ([S08-071], [S08-114]) |
| **Drugs and Pharmaceuticals** | Receta: LegitScript o revisión interna, solo EE. UU./CA/NZ, 18+; OTC según la ley local; suplementos "potencialmente inseguros" prohibidos a discreción de Meta; telehealth y farmacias online con LegitScript | Coaching de peso con GLP-1 o telemedicina: zona de máxima fricción **[OFFICIAL META]** ([S08-124]) |
| **Drug & Alcohol Addiction Treatment** | EE. UU.: LegitScript + permiso previo | Programas de "dejar de beber o fumar": revisar en cada país **[OFFICIAL META]** ([S08-115]) |
| **Dating** | Permiso previo y requisitos | Coaching de citas o seducción: no es "dating service", pero el contenido sexual o los atributos personales (soltería, orientación) se vigilan **[STRONG INFERENCE]** |
| **Discriminatory Practices** | Prohibido discriminar en targeting o contenido; certificación de cumplimiento | Especialmente en HEC **[OFFICIAL META]** ([S08-104]) |
| **Commercial Exploitation of Crises** | Prohibido aprovechar crisis | "La crisis te va a dejar sin trabajo: compra mi curso" = riesgo doble (crisis + atributo) **[STRONG INFERENCE]** |

## Implicaciones operativas

- **Clasificar cada oferta** antes de lanzar: ¿SAC? (crédito, empleo, vivienda) · ¿Health? · ¿Financial/Crypto? · ¿SIEP-UE por tono? · ¿Personal attributes en el hook? Un checklist de 5 preguntas evita la mayoría de los rechazos.
- **Personal attributes:** auditar todos los hooks en formato pregunta. El 80 % de los rechazos "por atributos" en infoproductos viene de preguntas del tipo "¿Estás…? / ¿Tienes…? / ¿Eres…?". **[STRONG INFERENCE]**
- **Salud:** decidir si la oferta es realmente "salud" (y aceptar optimización a eventos permitidos) o "bienestar general/educación" con una landing coherente. No mezclar.
- **Finanzas:** separar el "curso educativo" de cualquier producto de inversión o afiliación; si hay producto, licencia y asesoría.

## Errores frecuentes

- No marcar SAC en ofertas con financiación o colocación laboral.
- Hooks con preguntas sobre la situación económica, la edad o la salud del espectador.
- Usar antes/después de peso sin contexto de producto o sin matices de plazo.
- Pensar que "es un curso, no un producto financiero" cuando el embudo acaba en un broker o un grupo de señales.
- Anuncios de "concienciación" económica o sanitaria en la UE con tono político.

## Preguntas abiertas

- Detalle del cambio del 22-jul-2026 en Health & Wellness (¿cambio a revisión por claims?).
- Si el financiamiento propio de cursos (plazos sin financiera) se considera "crédito" en España a efectos de SAC (sin documentación de Meta para Europa; en EE. UU. sí incluye los plazos 0 % in-house).
- Tasa de falsos positivos SIEP en anuncios comerciales de la UE tras oct-2025.

## Fuentes clave

- [About ads for housing, employment or financial products and services](https://www.facebook.com/business/help/399587795372584) — Meta — meta-oficial
- [Special Ad Categories (Marketing API)](https://developers.facebook.com/docs/marketing-api/audiences/special-ad-category) — Meta — meta-developers
- [About social issues](https://www.facebook.com/business/help/214754279118974) / [Availability SIEP](https://www.facebook.com/business/help/2150157295276323) — Meta — meta-oficial
- [Ending Political, Electoral and Social Issue Advertising in the EU](https://about.fb.com/news/2025/07/ending-political-electoral-and-social-issue-advertising-in-the-eu/) — Meta, 2025-07/2025-10-06 — meta-oficial
- [Privacy Violations and Personal Attributes (Ad Standards)](https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes/) y [ayuda](https://www.facebook.com/business/help/2557868957763449) — Meta — meta-oficial
- [Health and Wellness](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/) y [ayuda](https://www.facebook.com/business/help/2489235377779939) — Meta — meta-oficial
- [Suicide, Self-Injury, and Eating Disorders (Ad Standards)](https://transparency.meta.com/policies/ad-standards/objectionable-content/suicide-selfinjury-eating-disorders/) — Meta, 2025-05-14 — meta-oficial
- [Financial and Insurance Products and Services](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/financial-services/) — Meta — meta-oficial
- [Cryptocurrency policy (ayuda)](https://www.facebook.com/business/help/438252513416690) — Meta — meta-oficial
- [Online Gambling and Games](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/gambling-games/) / [Alcohol](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/alcohol/) / [Drugs and Pharmaceuticals](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/drugs-pharmaceuticals/) — Meta — meta-oficial
- [As health and wellness brands brace for ad restrictions on Meta](https://digiday.com/marketing/as-health-and-wellness-brands-brace-for-ad-restrictions-on-meta-marketers-and-advertisers-seek-more-transparency/) — Digiday — prensa
- [Meta platform restrictions explained: core setup](https://oursprivacy.com/blog/meta-platform-restrictions-explained-core-setup) — Ours Privacy, 2026 — vendor
