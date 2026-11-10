# España y LatAm: benchmarks, comportamiento, regulación, practitioners y diferencias de enfoque

> Última verificación: 2026-10-16 · Autor: A11 (agente) · Ámbito: España, México, Colombia, Argentina, Chile y Perú (con Brasil como referencia). Benchmarks 2025-2026 de CPM, CPC, CPL y CPA; WhatsApp, pagos, contra reembolso y cuotas; regulación española que afecta a anuncios (sanitaria, financiera, cripto, juego, datos e influencers); impuestos y recargos por país; practitioners y agencias hispanohablantes con casos numéricos. Complementa `03-geografias-costes-comportamiento.md` y `04-escalado-internacional.md`. Para verificaciones y políticas en detalle, ver el área 08.

## TL;DR

- **No existe un benchmark público fiable con metodología para España ni para LatAm.** Lo disponible son rangos de agencias (sin muestra declarada) y tablas de vendors. Un informe LatAm muy citado (fuelads, Q2 2026) **deriva los CPL de LatAm desde datos de EE. UU. ajustados por CPM**; no los mide. **No uses esas cifras como benchmark.** **[EMPIRICAL]**
- **Órdenes de magnitud de CPM (2026):** España ~2,5–8 € (agencia) o 5,8–6,7 $ (vendors); México ~3,9–4,5 $ (CDMX un 30–45 % por encima de la media nacional); Chile 2,4–5,2 $; Colombia 2–4 $ (5 000–18 000 COP); Perú ~3,7 $ (S/ 8–30); Argentina ~3,8 $ (estimado). **[EMPIRICAL]** (débil)
- **Los impuestos y recargos pesan más que las diferencias de subasta.** España: +3 % de location fee (fuera de "Amount spent"). **Argentina: hasta ~53 % de recargo pagando con tarjeta** (IVA 21 % + percepción del 30 % + IIBB ~2 %; parte recuperable según el régimen). Chile: IVA digital del 19 %. Perú: IGV del 18 % (recaudado por el proveedor extranjero desde el 1-dic-2024). México: IVA del 16 %. Colombia: 19 %. **[EMPIRICAL]** (fuentes contables y de prensa) / fee **[OFFICIAL META]**
- **WhatsApp separa claramente España de LatAm:** la opción de **optimizar click-to-WhatsApp por leads no está disponible en la UE ni en Reino Unido** (tampoco en Japón ni Corea del Sur). En LatAm sí, y Meta reporta un **−24 % de CPL** frente a optimizar por conversaciones (experimento de nov-2024 con 116 000 campañas). En España solo se puede optimizar por conversaciones o enviar a formulario o web. **[OFFICIAL META]**
- **Pagos:** en México, el 23 % de los compradores online paga en efectivo en tiendas (OXXO) y los meses sin intereses son un atributo clave (los de 12 meses, los más esperados en el Buen Fin 2025). Colombia y México tienen una cultura de **contra reembolso (COD)** en dropshipping, con devoluciones del **15–35 %** según la operación (fuentes del propio nicho). En España crece Bizum (20–30 % de los clientes, según una estimación citada por Stripe). **Implicación crítica:** decide si el evento Purchase se dispara al pedir o al cobrar o entregar. **[EMPIRICAL]**
- **España tiene capas regulatorias que Meta no revisa por ti:** verificación de anunciante financiero (España está en la lista oficial de 10 mercados; el documento exacto no está confirmado públicamente); CFD y opciones binarias prohibidos globalmente por Meta; publicidad de criptoactivos sujeta a la Circular 1/2022 de la CNMV; publicidad sanitaria (RD 1907/1996 más normas autonómicas); juego (RD 958/2020, parcialmente anulado por el Supremo en 2024); cookies y píxel solo tras consentimiento (AEPD); influencers (RD 444/2024). **[OFFICIAL META]** / **[EMPIRICAL]**
- **Practitioners hispanohablantes:** no se identificó ninguno con evidencia pública y metodológica al nivel de Loomer, Haus o CTC. Las agencias publican rangos y casos autodeclarados, a menudo sin atribución declarada. Los más útiles muestran el embudo completo: CPL → calificación → cita o venta. **[EMPIRICAL]**

---

## 1. Benchmarks 2025-2026 por mercado (con calidad de fuente)

> **Advertencia general:** todas las cifras de esta sección proceden de agencias o vendors con interés comercial y casi nunca declaran muestra, periodo ni definición. Úsalas solo para ordenar mercados y detectar valores absurdos. Para decisiones, usa tu propio histórico (ver `02-como-usar-benchmarks.md`).

### 1.1 España

| Métrica | Valor | Fuente (fecha) | Calidad |
|---|---|---|---|
| CPM (conversión y leads) | **2,50–8,00 €** | Cactus Marketing, agencia de Murcia con más de 2 M€ gestionados declarados (feb-2026, act. oct-2026) | Baja: rango sin muestra |
| CPM (e-commerce, USD) | 6,65 $ / 5,80 $ (rango de 4,50–7,00 $) | Lebesgue (jul-2026) / AdAmigo ("proyección") | Baja |
| CPC mediano | 0,46 € de media (0,29 € en ene-26 → 1,13 € en jul-26) | Superads (más de 3 000 M$ de gasto global) | Media-baja; serie volátil |
| CPL servicios profesionales o legal (B2B) | 25–65 € | Cactus Marketing | Baja |
| CPL inmobiliaria (registro de visita) | 15–45 € | Cactus Marketing | Baja |
| CPL salud y clínicas (cita) | 10–35 € | Cactus Marketing | Baja |
| Coste por suscriptor (infoproducto o e-commerce) | 1,50–5,00 € | Cactus Marketing | Baja |
| Presupuesto mínimo recomendado | ~500 €/mes (agencia); 600–900 €/mes (otra guía para pymes) | Cactus; Roger Montero | Opinión |

### 1.2 México

| Métrica | Valor (USD salvo indicación) | Fuente | Calidad |
|---|---|---|---|
| CPM | 3,92 $ (Lebesgue); 4,50 $ (AdAmigo); **2–5 $ en verticales competidos**; **CDMX un 30–45 % por encima de la media nacional** | Lebesgue, AdAmigo, eXprimeNet (ago-2026) | Baja-media |
| Estacionalidad | **CPM +40–70 % en el Buen Fin (noviembre) y en el Hot Sale (mayo)** | eXprimeNet | Baja-media |
| CPL inmobiliaria residencial | 8–18 $ por lead cualificado; visita agendada a 25–45 $ | eXprimeNet (cuentas gestionadas 2024-2026 + fuentes de la industria) | Media-baja |
| CPL inmobiliaria premium (Tulum, Playa) | 20–45 $ | eXprimeNet | Media-baja |
| CPL seguros (auto, vida, gastos médicos) | 5–12 $ / 8–15 $ / 10–18 $ | eXprimeNet | Media-baja |
| CPL crédito personal / hipotecas | 4–10 $ / 12–25 $ | eXprimeNet | Media-baja |
| CPL educación superior privada | 15–40 $ (ciclo largo); 4–12 $ (corto) | eXprimeNet | Media-baja |
| CPL odontología estética / cirugía plástica | 5–12 $ / 12–25 $ | eXprimeNet | Media-baja |
| B2B SaaS | 25–80 $ por MQL; 100–300 $ por SQL enterprise | eXprimeNet | Media-baja |
| Tarifa WhatsApp *marketing* (Meta) | **0,0397 $ por mensaje** desde el 1-oct-2026 (0,0305 $ en julio) | Tarifa de Meta, vía Spur | Alta |

### 1.3 Colombia, Chile, Perú y Argentina

| País | CPM | CPC | CPL / coste por resultado | Fuente | Calidad |
|---|---|---|---|---|---|
| **Colombia** | 2,00 $ (Lebesgue); 4,00 $ (AdAmigo); **5 000–12 000 COP** o 7 000–18 000 COP (agencias) | 250–1 200 COP | 2 500–40 000 COP o 6 000–30 000 COP según el sector; "USD 3–15 típico" según otra agencia | Lebesgue; AdAmigo; Sergio Vargas; Consolidación Digital; Cangrejo Digital | Baja |
| **Chile** | 2,44 $ (Lebesgue); 5,20 $ (AdAmigo); **2 500–5 900 CLP** (agencia local) | — | Coste por resultado de 500–3 000 CLP; mensajes directos de 1 000–3 000 CLP | Lebesgue; AdAmigo; Seonet Digital | Baja |
| **Perú** | ~3,70 $ (AdAmigo); **S/ 8–30** (agencia) | S/ 0,50–6 | CPL de S/ 8–120; restauración y delivery de S/ 5–20 | AdAmigo; Flama Creators | Baja |
| **Argentina** | ~3,80 $ (AdAmigo); interpolado según otro agregador | 0,38 $ | — | AdAmigo; fuelads | Muy baja |

**Lo consistente:** Colombia y Perú están entre los CPM más bajos. México está por encima, con CDMX bastante más cara. Chile es el más caro de la región por poder adquisitivo en algunas fuentes, aunque no en todas. **Lo inconsistente:** las fuentes difieren hasta dos veces para el mismo país. **[EMPIRICAL]**

## 2. Costes ocultos: impuestos y recargos que cambian el "CPM efectivo"

| País | Recargo sobre la inversión en Meta | Recuperable | Fuente | Evidencia |
|---|---|---|---|---|
| **España** | **Location fee del 3 %** (desde el 1-jul-2026), fuera del presupuesto y de "Amount spent". Factura Meta Platforms Ireland; con un NIF-IVA válido se aplica normalmente la inversión del sujeto pasivo | El fee no; el IVA según el régimen (ver área 08) | Meta (mar-2026, vía Reuters, Medianama y eMarketer); área 08 | **[OFFICIAL META]** |
| **Argentina** | **Hasta ~53 % pagando con tarjeta:** IVA del 21 % sobre servicios digitales del exterior (RG 4240/2018), **percepción del 30 %** a cuenta de Ganancias o Bienes Personales (RG 5617/2024) e IIBB de ~2 % (CABA y Buenos Aires). El impuesto PAÍS decayó el 23-dic-2024 | Para un responsable inscripto: IVA como crédito fiscal y percepción imputable (inmoviliza caja). Para monotributistas o consumidores finales, el IVA y los IIBB son coste | DoubleTick (jun-2026; vendor de líneas de crédito en pesos); Contablix; Flux | **[EMPIRICAL]**; validar con un contador |
| **Chile** | IVA del 19 % sobre servicios digitales (incluida la publicidad en Meta). Meta no emite factura electrónica chilena: se respalda con factura de compra | Crédito fiscal según el uso | Blogs contables (Nexbu, Slim, Wasabil) | **[EMPIRICAL]** |
| **Perú** | IGV del 18 % sobre servicios digitales de no domiciliados, recaudado por el proveedor desde el 1-dic-2024 | Según el régimen | Prensa y blogs contables | **[EMPIRICAL]** |
| **México** | IVA del 16 % sobre servicios digitales (aplicación concreta a la facturación de Meta no verificada) | Según el RFC y el régimen | Blogs; TikTok documenta un 16 % para self-serve | **[STRONG INFERENCE]** |
| **Colombia** | IVA del 19 % (tasa citada por fuentes generales; aplicación a Meta no verificada) | Según el régimen | Prensa | **[STRONG INFERENCE]** |

**Implicaciones:**
- **Argentina** es el caso extremo: con el mismo CPM de subasta, el coste efectivo puede ser un 50 % mayor que el de un anunciante que factura en otro país. Valora la financiación de la cuenta en **USDC** (disponible en Argentina y Colombia desde ago-2026, según changelog) o con líneas locales en pesos con factura local, siempre validado con un contador. **[STRONG INFERENCE]**
- Incluye el recargo en el **ROAS de equilibrio** y en los objetivos de puja (ROAS goal o cost per result goal). **[STRONG INFERENCE]**

## 3. Comportamiento del usuario y del comprador

### 3.1 WhatsApp como canal dominante

| Dato | Valor | Fuente | Evidencia |
|---|---|---|---|
| Penetración de WhatsApp (población) | España ~85 %, Brasil ~85 %, Argentina ~80 %, México ~75 %, Colombia ~75 % | Infobip (2026; año de los datos sin precisar) | **[EMPIRICAL]** (vendor) |
| Preferencia en España | WhatsApp es la red preferida por el 37 % de los usuarios (Instagram 16 %, YouTube 14 %) | IAB Spain 2025 | **[EMPIRICAL]** |
| CTWA optimizando por leads | Disponible en LatAm y **no disponible en UE, Reino Unido, Japón ni Corea del Sur**. −24 % de CPL frente a conversación (experimento de Meta de nov-2024 con 116 000 campañas y 43 000 negocios) | whatsappbusiness.com | **[OFFICIAL META]** |
| Caso Braip (Brasil) | Lead frente a mensajes: +45 % de leads cualificados y −30 % de CPL | Meta | **[OFFICIAL META]** (autodeclarado) |
| WhatsApp frente a formulario (México) | En 2 cuentas B2C (seguros y educación online): **2,3 veces más leads cualificados y 3,1 veces más citas** con el mismo presupuesto y creatividad | eXprimeNet (agencia) | **[EMPIRICAL]** (débil, n=2) |
| Tarifas de mensaje *marketing* | México 0,0397 $ (oct-2026); Brasil 0,0625 $; **España subió el 1-jul-2026** (de 0,0615 $ a 0,0707 $ según YCloud; las cifras en € de otros BSP no coinciden: 0,0509–0,0585 €) | Spur, YCloud y BSP | **[OFFICIAL META]** (México y Brasil) / **[CONTESTED]** (España) |

**Lectura:** en LatAm, WhatsApp no es un canal más, sino el lugar donde se cierra la venta o se cualifica el lead. En España también es la app preferida, pero **la imposibilidad de optimizar por leads en CTWA** hace que el embudo por WhatsApp optimice hacia "gente que inicia conversaciones", no hacia gente que se convierte en lead. Mide la conversión conversación → lead → venta en el CRM y considera formularios Higher intent o la web como alternativa. **[STRONG INFERENCE]**

### 3.2 Pagos, cuotas y contra reembolso

| País | Dato | Fuente | Evidencia |
|---|---|---|---|
| México | Pago online: débito 69 %, crédito 54 %, **efectivo en tiendas (OXXO) 23 %**, transferencia 20 %. 77 M de compradores digitales en 2025 | AMVO 2025 (vía Milenio) | **[EMPIRICAL]** |
| México | Meses sin intereses: los de 12 meses son los más esperados en el Buen Fin 2025. BNPL "sin tarjeta" = 8 % en el Hot Sale 2025 (otra fuente da un 31 % con otra definición). Fintechs atribuyen al BNPL +30–40 % de ticket medio (cifras interesadas) | El Financiero; IDC; Kueski y Aplazo | **[EMPIRICAL]** / cifras de ticket **[HYPOTHESIS]** |
| Brasil | Pix con más de 160 M de usuarios | Guías de PSP | **[EMPIRICAL]** |
| Colombia | Dropshipping con COD (Dropi y otros): **devoluciones del 15–30 %** según el nicho; del 18–25 % con una operación seria frente al 35–40 % sin procesos | Talkyria; Andrey Rojas/REDKING (nicho interesado) | **[EMPIRICAL]** (débil) |
| México | COD: entrega efectiva del 60–75 % (Dropi) o del 70–85 % (99minutos) | Andrey Rojas | **[EMPIRICAL]** (débil) |
| España | Bizum: 18 600 e-commerce lo integraron entre ene y sep de 2025; lo usa entre el 20 % y el 30 % de los clientes (estimación). El efectivo sigue siendo el medio principal en tienda física para el 57 % (Banco de España, nov-2025) | Stripe; BdE | **[EMPIRICAL]** |
| España | Contra reembolso: dato reciente no encontrado (un 10,7 % en 2014, obsoleto). La tasa de devolución online fue del 25 % en 2023 | Varias | **[OUTDATED]** / **[EMPIRICAL]** |

**Implicación operativa (COD y pagos diferidos):** si el Purchase se dispara al crear el pedido, **Meta optimiza hacia gente que pide, no hacia gente que paga**. Con un 20–35 % de rechazo, el ROAS de plataforma puede estar inflado en una proporción similar y el sistema aprende de compradores que no pagan. Alternativas: enviar un evento personalizado "pedido entregado o cobrado" vía CAPI y optimizar por él cuando tenga volumen, o usar value rules o exclusiones por zonas con alto rechazo. **[STRONG INFERENCE]** (sin caso público documentado)

### 3.3 Calendario comercial

| Mercado | Picos | Dato |
|---|---|---|
| México | Hot Sale (mayo), Buen Fin (noviembre) | CPM +40–70 % (eXprimeNet); Buen Fin 2025 con 45 900 M MXN online (+31 %) |
| Chile | CyberDay, Black Friday | — |
| Colombia | Días sin IVA, Black Friday | — |
| Perú | CyberWow | — |
| Argentina | Hot Sale, CyberMonday | — |
| España | Rebajas de enero y julio, Black Friday, Navidad, Reyes | — |

## 4. Regulación española que afecta a los anuncios (no es asesoría legal)

| Ámbito | Qué aplica | Qué hace Meta | Evidencia |
|---|---|---|---|
| **Productos financieros** | Supervisores: CNMV (inversión), Banco de España (banca y crédito), DGSFP (seguros) | **España está en la lista oficial de verificación de anunciantes financieros** (con Australia, Hong Kong, India, Irlanda, Israel, Taiwán, Tailandia, Reino Unido y EE. UU.; Polonia desde el 28-ago-2026). Según la página de Meta (consultada vía terceros el 2-oct-2026), el **número de licencia** solo se pide de forma explícita en Australia, India y Taiwán; para España no se detalla públicamente qué documento se exige. CFD, opciones binarias, préstamos de 90 días o menos y payday loans están prohibidos globalmente. El crédito exige categoría especial (SAC) | **[OFFICIAL META]** / documento español **[HYPOTHESIS]** (área 08) |
| **Criptoactivos** | **Circular 1/2022 de la CNMV** (en vigor desde el 17-feb-2022): campañas masivas sujetas a **comunicación previa**, advertencia de riesgo obligatoria, registro de campañas de 2 años y facultad de la CNMV para pedir cambios o cese. MiCA (UE) superpuesto: estado de transición no verificado aquí | Meta exige autorización previa para cripto (política de cripto; ver área 08) | **[EMPIRICAL]** (despachos: PwC, Osborne Clarke, Écija) |
| **Sanidad** | **RD 1907/1996** (publicidad con fines sanitarios): la publicidad de centros debe ajustarse a su autorización sanitaria; el resto requiere autorización previa. **Normas autonómicas:** p. ej. en Madrid hay que consignar el número de registro sanitario (Decreto 51/2006); la Comunitat Valenciana exige autorización previa para productos sanitarios con impacto en la salud. Un post de Instagram con un tratamiento cuenta como publicidad sanitaria. Hay un proyecto estatal sobre publicidad de productos sanitarios en audiencia pública (estado 2026 no verificado) | Meta restringe la salud y el bienestar (restricciones de datos y eventos lower-funnel desde 2025; ver 00-ESTADO) | **[EMPIRICAL]** (guías sectoriales) |
| **Juego** | **RD 958/2020.** El Supremo (STS 527/2024, 2-abr-2024) anuló, entre otros, los arts. 13.1 y 13.3, 15 y **23.1** (prohibición general en servicios de la sociedad de la información), 25.3 y 26.2-3. La reintroducción vía reforma de la Ley del Juego no está verificada | Meta exige autorización escrita para juego online (política de juego; la página de transparencia dio 404 en esta consulta) | **[EMPIRICAL]** / Meta **[STRONG INFERENCE]** |
| **Datos, cookies y píxel** | AEPD: ningún píxel ni cookie no esencial **antes del consentimiento**; botones de aceptar y rechazar equivalentes; sin muros de cookies sin alternativa. Sanciones: Iberia 30 000 € (confirmada por la Audiencia Nacional en jun-2024), SEAT 12 000 €, Vueling 18 000 € tras reducción. **CAPI no está tratado de forma específica** en las guías revisadas: los datos server-side también requieren base legal | Meta ofrece CAPI de un clic y píxel enriquecido con IA (2026) | **[EMPIRICAL]**; asesoría legal |
| **Influencers y partnership ads** | **RD 444/2024** (usuarios de especial relevancia): umbrales de ≥300 000 € de ingresos y ≥1 M de seguidores en una plataforma o ≥2 M en total (verificar en el BOE); identificación clara de la publicidad e inscripción en el registro | Partnership ads con etiqueta "Paid partnership" | **[EMPIRICAL]** |
| **Política y temas sociales** | — | **Prohibidos en la UE desde el 6-oct-2025** | **[OFFICIAL META]** (00-ESTADO) |
| **Categorías especiales** | — | En España y Europa es obligatorio marcar la SAC en **crédito, empleo y vivienda** | **[OFFICIAL META]** (área 08) |
| **Consentimiento de anuncios (UE)** | DMA | Elección entre anuncios personalizados y LPA desde ene-2026: menos señal | **[OFFICIAL META]** |
| **Prácticas desleales** | Ley de Competencia Desleal (lista negra de la Directiva 2005/29: falsa urgencia, curas, reseñas falsas) | — | **[EMPIRICAL]** (área 08) |

## 5. Practitioners y agencias hispanohablantes con evidencia numérica

| Practitioner / agencia | Mercado | Evidencia publicada | Valoración |
|---|---|---|---|
| **Cactus Marketing** (Nacho Lagares, Murcia) | España | Rangos de CPM y CPL por sector; más de 2 M€ gestionados declarados; sin muestra ni periodo | **C**: útil como orden de magnitud |
| **eXprimeNet** | México | Rangos de CPL por vertical (USD), CPM de CDMX frente a la media nacional, estacionalidad, test WhatsApp frente a formulario (n=2), efecto de mostrar rango de precio (−18–31 % de rebote en 3 cuentas) | **B/C**: lo más detallado encontrado para México |
| **M&P** (Chile) | Chile | Casos con cifras en CLP (supuesto): B2B SaaS "Genera" con CPL en Meta de 21 048 → 7 337 (−65 %) en 15 meses con 8,5 M/mes y 374 leads/mes; "Power Energy" con CPA de 17 100 → 826 (−95 %); inmobiliaria por comunas con WhatsApp automático | **C**: cifras sin atribución ni método |
| **Alan Melnick** (consultor, Chile y LatAm) | Chile, Colombia, Perú | Skincare en Chile: de 22 campañas a 2 + CAPI + 18 UGC → ROAS de 1,8× a 8,6× y CPA −43 % en 90 días. Joyería en 3 países: TikTok con un CPA un 28 % menor que Meta | **C**: atribución no declarada (él mismo avisa de que el ROAS de Meta se infla) |
| **Multiplicalia** | España | De Arena y Sal (Feria de Sevilla): 12 compras a 12,98 € con más de 100 € de AOV | **C**: muestra mínima |
| **La Hormiga Digital** (Elche) | España | Más de 25 M€ gestionados y ROAS medio de 5× declarados; caso anónimo de moda de 5 k€ a 25 k€/mes con ROAS de 1,8× a 5× | **C**: ilustrativo |
| **Felipe Vergara / DEEPLOOK** | Colombia y LatAm | Más de 250 marcas y más de 45 M$ invertidos declarados; casos con ROAS de 10–18 en su web | **C**: formación (67 $/mes) |
| **Andrey Rojas / REDKING** | Colombia y México (COD) | Tablas de entrega y devolución por calidad operativa | **C**: útil para el COD; afiliado a Dropi |
| **Balandin Agency** | Rusohablantes (con compradores en España) | Caso completo de infoproducto (ver `05`, D1) | **B** |
| **Adri Ponce** (blog) | España | Artículos sobre el ROAS inflado; sin casos propios ni bio | **C** |

**Criterio recomendado** (coincide con los rankings LatAm): exigir capturas de Ads Manager con fechas, conciliación con el backend o CRM, el embudo completo (CPL → calificación → cita → venta) y limitaciones declaradas. Ninguno de los anteriores publica tests de incrementalidad. **[STRONG INFERENCE]**

## 6. Diferencias de enfoque entre mercados

| Dimensión | España | México | Colombia / Perú | Chile | Argentina |
|---|---|---|---|---|---|
| Señal | UE: LPA, consentimiento de cookies (AEPD), fin de anuncios políticos | Sin LPA | Sin LPA | Sin LPA | Sin LPA |
| WhatsApp | App preferida, pero **CTWA sin optimización por leads** | Canal central; CTWA→leads disponible | Canal central (COD y servicios) | Muy usado | Muy usado |
| Pago dominante | Tarjeta, Bizum, PayPal | Débito y crédito con MSI, OXXO, transferencia | COD (dropshipping), tarjeta | Tarjeta (Webpay) | Tarjeta o Mercado Pago, cuotas |
| Coste efectivo extra | +3 % de fee | IVA del 16 % (según el caso) | Colombia IVA del 19 %; Perú IGV del 18 % | IVA del 19 % | **Hasta ~53 %** con tarjeta |
| Riesgo de evento Purchase "falso" | Bajo | Medio (OXXO) | **Alto (COD)** | Bajo | Medio |
| Regulación de claims | Alta (sanitaria, financiera, cripto, juego, competencia desleal) | Media (COFEPRIS en salud) | Media | Media | Media |
| Enfoque de embudo recomendado | Formulario Higher intent o web + CRM→CAPI; WhatsApp como canal de cierre | CTWA optimizando a leads o compras + agente de WhatsApp | CTWA o landing COD con confirmación telefónica; evento "entregado" vía CAPI | Web y e-commerce con CAPI | Atención a la caja y a los impuestos; precios en ARS frente a gasto en USD |

## Implicaciones operativas

- **No traslades benchmarks de EE. UU. a España o LatAm "ajustando por CPM".** Esa es justo la metodología del informe LatAm más citado, y no sirve para decidir.
- **En España:** suma un 3 % al coste, revisa la verificación financiera si aplica, cumple la AEPD antes de disparar el píxel y no esperes optimizar WhatsApp por leads.
- **En LatAm:** usa CTWA optimizando por leads o compras donde exista. Define el evento de compra según el cobro real (COD, OXXO). Precio local con MSI o cuotas.
- **En Argentina:** modela el recargo fiscal (hasta ~53 %) y la estrategia de pago antes de comparar el CPA con otros países.
- **Multi-país hispano:** separa España de LatAm (señal, fees, WhatsApp, pagos y léxico distintos) y LatAm por tier de valor (ver `04`).

## Errores frecuentes

- Comparar el CPA de Argentina o Chile con el de España sin impuestos.
- Contar pedidos COD como ventas en el ROAS.
- Montar en España un embudo CTWA "por leads" copiado de un curso LatAm (no existe en la UE).
- Promocionar tratamientos estéticos o productos financieros en España sin revisión legal porque "Meta lo aprobó".
- Usar el mismo copy en español para España y LatAm.

## Preguntas abiertas

- ¿Qué documento exacto exige Meta para la verificación financiera en España (registro CNMV/BdE/DGSFP o solo identidad)? No es público sin sesión.
- Estado vigente de la publicidad de juego tras la STS 527/2024 y la reforma de la Ley del Juego.
- Tarifas oficiales de WhatsApp para España en EUR (los BSP no coinciden).
- Benchmarks medidos (no derivados) de CPL y CPA por vertical en México, Colombia, Chile, Perú y Argentina.
- Aplicación concreta del IVA a la facturación de Meta en México y Colombia.

## Fuentes clave

- [Cactus Marketing: cuánto cuesta Meta Ads en España 2026](https://cactusmarketing.es/blog/cuanto-cuesta-meta-ads-espana-2026): feb/oct-2026, agencia
- [eXprimeNet: Lead Generation in Mexico](https://www.e-xprimenet.com/en/hub/markets/lead-generation-mexico/): ago-2026, agencia
- [fuelads: Benchmarks CPL LatAm Q2 2026](https://fuelads.tech/benchmarks-latam-2026): 2026, vendor (metodología derivada; no usar)
- [Superads: CPC España](https://www.superads.ai/facebook-ads-costs/cpc-cost-per-click/spain): 2026, vendor
- [Lebesgue: CPM by Country](https://lebesgue.io/facebook-ads/facebook-cpm-by-country): jul-2026, vendor
- [AdAmigo: CPM/CPC by Country](https://www.adamigo.ai/blog/meta-ads-cpm-cpc-benchmarks-by-country-2026): 2026, vendor
- [Seonet Digital: costo Meta Ads Chile 2026](https://www.seonetdigital.cl/costo-publicidad-en-meta-ads-chile): 2026, agencia
- [Sergio Vargas: cuánto cuesta pautar en Colombia 2026](https://sergiovargassierra.com/cuanto-cuesta-pautar-en-facebook-ads-en-colombia/): 2026, practitioner
- [Consolidación Digital: Meta Ads Colombia 2026](https://www.consolidaciondigital.com/blog/performance-marketing/cuanto-cuesta-meta-ads-colombia): 2026, agencia
- [Flama Creators: Meta Ads Perú](https://flamacreators.com/cuanto-cuesta-meta-ads-peru): 2026, agencia
- [DoubleTick: impuestos de Meta Ads con tarjeta en Argentina 2026](https://www.doubletick.com.ar/blog/impuestos-meta-ads-tarjeta-credito-argentina-2026/): jun-2026, vendor
- [Contablix: Facturas META, IVA y Ganancias (AR)](https://contablix.ar/blog/iva-meta-ganancias-2025-retencion-argentina): 2025, prensa/blog
- [Nexbu: invoices de Meta y Google ante el SII (Chile)](https://nexbu.com/blog/como-declarar-invoices-de-meta-y-google-ads-por-servicios-digitales-ante-el-sii-en-chile): 2025-2026, blog
- [Diario Libre: impuestos a servicios digitales en LatAm](https://www.diariolibre.com/economia/finanzas/2026/05/20/asi-se-gravan-las-plataformas-digitales-en-america-latina/3539916): 20-may-2026, prensa
- [WhatsApp Business: lead generation strategies (CTWA→leads no disponible en UE/UK)](https://whatsappbusiness.com/resources/resource-library/lead-generation-strategies-smb-whatsapp/): 2025, meta-oficial
- [WhatsApp Business: Braip success story](https://whatsappbusiness.com/resources/success-stories/braip/): 2025, meta-oficial
- [YCloud: WhatsApp API pricing update 1-jul-2026](https://www.ycloud.com/blog/whatsapp-api-message-pricing-update-effective-july-1-2026): 2026, vendor
- [Infobip: tendencias de mensajería 2026](https://www.infobip.com/es/tendencias-de-mensajeria/analisis-regional): 2026, vendor
- [Milenio: AMVO, 77 M de compradores digitales](https://www.milenio.com/negocios/mexico-supera-77-millones-compradores-digitales-2025-amvo): 2025, prensa
- [IDC Online: BNPL +30 % de ticket](https://idconline.mx/finanzas/2025/04/30/compra-ahora-y-paga-despues-el-futuro-de-las-compras): abr-2025, prensa
- [El Financiero: Buen Fin 2025](https://www.elfinanciero.com.mx/empresas/2025/10/02/jovenes-impulsan-cashback-y-puntos-durante-la-edicion-xv-de-el-buen-fin/): oct-2025, prensa
- [Talkyria: dropshipping Colombia](https://talkyria.com/blog/dropshipping-colombia-guia-completa): 2026, blog
- [Andrey Rojas: contraentrega Colombia 2026](https://www.andreybusiness.com/blog/dropshipping-contraentrega-colombia-2026): 2026, practitioner
- [Stripe: Bizum](https://stripe.com/resources/more/bizum-for-buisinesses-spain): 2025, vendor
- [Meta Transparency: Financial and insurance products](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/financial-services/): vigente, meta-oficial
- [meta-ads.si: países con verificación (cita páginas de ayuda de Meta)](https://meta-ads.si/which-countries-need-advertiser-verification/): oct-2026, practitioner
- [PwC: Circular 1/2022 CNMV criptoactivos](https://periscopiofiscalylegal.pwc.es/la-cnmv-publica-una-circular-relativa-a-la-publicidad-sobre-criptoactivos-presentados-como-objeto-de-inversion/): 2022, despacho
- [Rex Digital: publicidad sanitaria en España](https://rexdigital.es/publicidad-sanitaria-espana/): 2025-2026, agencia
- [Generalitat Valenciana: autorización previa de productos sanitarios](https://sede.gva.es/es/detall-tramit?id_proc=18118&version=red): vigente, oficial autonómico
- [PwC: el Supremo anula parte del RD 958/2020](https://www.pwc.es/es/newlaw-pulse/entretenimiento-medios/tribunal-supremo-anula-parcialmente-comunicaciones-comerciales-juego.html): abr-2024, despacho
- [Cookiebot: guía de cookies de la AEPD](https://www.cookiebot.com/es/guia-cookies-aepd/): 2025, vendor
- [Prodat: sanciones de la AEPD por cookies](https://www.prodat.es/blog/cuidado-con-las-cookies-la-aepd-multa-con-la-maxima-sancion-prevista-por-no-cumplir-con-la-norma-y-sus-recomendaciones/): 2024-2025, consultora
- [Cuatrecasas: RD de Usuarios de Especial Relevancia](https://www.cuatrecasas.com/es/spain/propiedad-intelectual/art/aprobacion-real-decreto-usuarios-especial-relevancia): 2024, despacho
- [M&P: casos de éxito Chile 2026](https://www.mulleryperez.cl/casos-de-exito): 2026, agencia
- [Alan Melnick: Meta Ads 2026](https://www.alanmelnick.com/blog/meta-ads-guia-completa-2026): 16-jun-2026, practitioner
- [Multiplicalia: casos de éxito](https://www.multiplicalia.com/casos-de-exito-google-ads-meta-ads/): 2025, agencia
- [La Hormiga Digital: agencia Meta Ads e-commerce](https://lahormigadigital.com/agencia-meta-ads-ecommerce/): 2026, agencia
- [Adri Ponce: ROAS inflado](https://adriponce.com/blog/roas-meta-ads-inflado-atribucion-real/): 14-may-2026, practitioner
