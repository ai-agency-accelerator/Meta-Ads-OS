# Instant forms a fondo: tipos, preguntas, filtros de calidad, spam y optimización

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A05 (agente) · Ámbito: lead ads con instant form (Facebook/Instagram), configuración, qué preguntar y qué no, leads falsos, integración y medición. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Tres tipos de formulario:** *More volume* (por defecto, envío rápido en móvil), *Higher intent* (texto que avisa de que el negocio contactará + **pantalla de revisión**; solo Feed de FB/IG en móvil) y *Rich creative* (marca, imágenes, intro obligatoria). Para servicios y high-ticket, el punto de partida razonable es Higher intent. **[OFFICIAL META]** (S05-009)
- **Filtros de calidad oficiales:** verificación del teléfono con un código OTP (llega por WhatsApp o SMS, lo elige Meta; filtra bots y números falsos; puede venir activada por defecto; solo móvil), requerir email de trabajo (Instagram o Marketing API según Meta en 2025), test de verificación de dirección, desactivar autofill (visto en cuentas en 2025), lógica condicional y respuestas condicionales. **[OFFICIAL META]** (S05-005, S05-010, S05-031, help 761812391313386)
- **La regla de Meta sobre preguntas:** "menos preguntas de opción múltiple = más envíos; más preguntas = más leads de calidad"; limitar las de respuesta corta. Máximo 15 preguntas personalizadas. **[OFFICIAL META]** (S05-011, S05-013)
- **Prohibido preguntar** ingresos, patrimonio, deudas, credit score, salud, etc. En high-ticket esto afecta a la típica pregunta "¿cuánto ganas?": usa preguntas de **capacidad de inversión/presupuesto para el proyecto** con cautela y sin pedir datos financieros personales. **[OFFICIAL META]** (S05-016) + **[HYPOTHESIS]** sobre dónde está la línea exacta.
- **Instant form vs landing: la evidencia está dividida.** El test más limpio publicado (Jon Loomer, 630 leads) dio la misma tasa de calidad (29,1% vs 29,0%) y la mitad de coste por lead de calidad con instant forms; agencias reportan lo contrario en sus nichos. **[CONTESTED]** → prueba en tu funnel midiendo hasta venta. (S05-032)
- **Spam y leads falsos:** las causas principales son la optimización a "envío" + autofill + placements de baja calidad (Audience Network) + bots. Las exclusiones de placement por ad set están desapareciendo en Leads/Sales (test desde 19-ago-2026, guía oficial 12-oct-2026): la exclusión que queda es **a nivel de cuenta** y afecta a todas las campañas. **[EMPIRICAL]** + **[OFFICIAL META]** (S05-049, S05-064, S05-065)
- **Los leads solo se pueden descargar durante 90 días** desde el envío: integra un CRM desde el día 1. **[OFFICIAL META]** (S05-019)
- **Reserva de cita embebida (junio-octubre 2026):** tras enviar el formulario, el lead puede reservar en Calendly o HighLevel sin salir de Facebook (HubSpot anunciado). Solo Facebook, despliegue progresivo con disponibilidad global prevista en octubre (SMT) o noviembre (otra fuente). Es la mayor palanca nueva para "speed to booking". **[OFFICIAL META]** vía prensa/partners (S05-059 a S05-062)

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **API v27**: `phone_otp_verification_type` (`NOT_ENABLED`/`OTP_REQUIRED`/`OTP_OPTIONAL`); el legacy `is_phone_sms_verify_enabled` sigue; `OTP_OPTIONAL` exige un `ad_account_id` elegible; en formularios antiguos puede venir `null`. **[OFFICIAL META]**
> - **Verificación de teléfono**: el código llega por WhatsApp o SMS (lo elige Meta); sin verificar no cuenta como lead; un fijo no puede verificar; no disponible para negocios con sede en Irak, Marruecos, Nigeria, Pakistán, Sri Lanka ni Uzbekistán. *Higher intent* solo se entrega en el feed móvil de Facebook e Instagram. *Require work email*: solo Instagram o API (anuncio del 30-oct-2025). Meta guarda los leads 90 días. **[OFFICIAL META]**
> - **Reserva de citas en el formulario**: solo app móvil de Facebook (en Instagram abre el navegador de la app); no se reporta en Ads Manager; Calendly y LeadConnector integrados; HubSpot se menciona pero no figura como calendario integrado; la disponibilidad global no está confirmada. **[OFFICIAL META]**
> - Evento de seguimiento "Leads with WhatsApp conversations" para instant forms. **[OFFICIAL META]** *Preferred lead answers* y el agente de IA dentro del formulario son pruebas descritas por Loomer, sin fuente oficial. **[HYPOTHESIS]**
> - Fuentes: S10-099, S10-136, S10-141 a S10-143 (verificación oficial de lead ads del mismo día) en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Anatomía de un instant form (2026)

Según Meta (help 761812391313386, 791294492679966):

1. **Form type:** More volume / Higher intent / Rich creative.
2. **Intro (opcional; obligatoria en Rich creative):** imagen de fondo, saludo (headline + descripción). Aquí va la *context card*: qué recibe, qué pasa después, para quién NO es.
3. **Questions:** prellenadas (contacto, nombre, demográficos, trabajo, IDs nacionales LATAM) + hasta **15 personalizadas** (multiple choice, short answer, conditional, store locator, appointment request). Conditional logic on/off. Mensaje de "por qué recogemos estos datos".
4. **Privacy policy:** URL obligatoria para publicar en FB/IG (la página "requirements" la llama opcional pero "about" la requiere; ponla siempre).
5. **Custom disclaimer:** opt-ins de marketing, avisos legales (RGPD).
6. **Ending:** headline, descripción, CTA, link, promo code, "Start conversations on Messenger" (chat con leads), "Chat on WhatsApp", llamada al negocio, **Book time** (reserva embebida, 2026).
7. **Destination (nivel anuncio):** *Require SMS verification to submit form*, *Require work email* (quality filters).

Restricciones útiles:
- **Solo se guardan 100 formularios**; el 101 sobrescribe el más antiguo. **[OFFICIAL META]** (Pendiente de verificar en la referencia de `leadgen_forms` de la Marketing API: no se encontró el 2026-11-09. Por prudencia, `formularios_meta.py crear` se para al llegar a 100 en vez de dejar que Meta sobrescriba uno.)
- Las funciones avanzadas solo están si creas el formulario en **Ads Manager** (desde Business Suite/Página: formulario simple; desde la Página solo short answer). **[OFFICIAL META]**
- **Organic leads:** si en Settings activas *Sharing → Open*, aparecen botones de compartir y leads orgánicos (no contados en Ads Manager, solo en la descarga de Business Suite). Por defecto *Restricted*. Para high-ticket, déjalo en Restricted. **[OFFICIAL META]** (S05-056)
- El envío del formulario en móvil solo funciona dentro de la app de Facebook/Instagram, no en navegadores móviles. **[OFFICIAL META]** (S05-017)

## 2. Tipos de formulario: cuándo cada uno

| Tipo | Qué cambia | Delivery | Úsalo cuando |
|---|---|---|---|
| More volume (default) | Envío en 1-2 toques con autofill | Todos los placements compatibles | Lead magnets, newsletters, registros a webinar gratuito, sorteos; cuando el coste de un lead malo es casi cero (email automatizado) |
| Higher intent | Texto inline "el negocio puede contactarte" + pantalla de revisión antes de enviar | **Solo Feed FB e IG en móvil** | Cualquier lead que vaya a una persona (setter, closer, comercial, técnico) |
| Rich creative | Colores, imágenes, texto largo de producto | Solo app de Facebook móvil (según la guía de creación) | Cuando necesitas *educar* dentro del formulario (oferta compleja, varios servicios) |

Evidencia sobre Higher intent: Meta describe el objetivo ("submissions más intencionales, evitar a los marginalmente interesados") pero **no publica el efecto en volumen ni en calidad**. Las cifras que circulan (−20 a −40% de volumen, 70-85% de tasa de contacto vs 40-65%) vienen de blogs sin metodología → **[HYPOTHESIS]**. Lo que sí es **[STRONG INFERENCE]**: la pantalla de revisión + aviso de contacto reduce envíos accidentales y "no me acuerdo de haber rellenado nada", que es la queja nº1 de los equipos de ventas.

## 3. Filtros de calidad oficiales

### Verificación por SMS (OTP)
- El lead debe introducir un código enviado a su móvil para poder enviar (por WhatsApp o SMS, lo elige Meta; nota del 2026-11-10, ver la caja de la v27 arriba). Meta: mejora la calidad "filtrando leads falsos como spam bots y malos actores". Si no verifica, **no cuenta como lead ni aparece en los datos**. **[OFFICIAL META]** (S05-010)
- No admite fijos ni teléfono de trabajo; la verificación de un número vale 90 días.
- **Puede venir activada por defecto** para anunciantes elegibles; revisa la casilla.
- **Solo placements de Facebook e Instagram en móvil.**
- Columna `phone_number_verified` en la descarga (puede **no** llegar vía integración CRM).
- No disponible en Irak, Marruecos, Nigeria, Pakistán, Sri Lanka y Uzbekistán.
- Caso oficial (The First Group, inmobiliaria de Dubái): −45% de números inválidos y +11% de tasa de conversión de calidad. **[OFFICIAL META]** (S05-005)
- Meta avisa de que puede afectar al número de leads y al CPL.

### Email de trabajo
- "Require work email": exige email corporativo válido. Útil en B2B; destruye volumen en B2C/autónomos. Disponible en Instagram o vía Marketing API según el anuncio de 2025; la guía de 2026 lo muestra como *quality filter* en Ads Manager. **[OFFICIAL META]**

### Desactivar autofill
- Visto en cuentas en abril 2025 (casilla en email/teléfono). Obliga a escribir. Reduce envíos impulsivos y errores de datos prellenados antiguos. **[EMPIRICAL]** (S05-031). No documentado como general en el Help Center a 2026-10-15.

### Lógica condicional y respuestas condicionales
- **Respuestas condicionales:** las opciones de la siguiente pregunta cambian según la respuesta anterior (CSV UTF-8). Las preguntas no cambian.
- **Lógica condicional:** cambia la *siguiente pregunta o la pantalla final* según la respuesta. Permite **descalificar** (enviar a un final distinto: "no es para ti, aquí tienes un recurso gratuito"). **[OFFICIAL META]** (S05-012, help 761812391313386)
- Compatible con verificación SMS.

### Preferred lead answers (test)
- Marcar respuestas preferidas en opción múltiple sin cambiar la experiencia; visto en test en agosto de 2026. **[HYPOTHESIS]** sobre su efecto (S05-033).

## 4. Qué preguntar y qué NO (fricción vs cualificación)

Principio: cada pregunta debe (a) cambiar lo que hará el equipo comercial con ese lead, o (b) filtrar a quien no puedes atender. Si no hace ninguna de las dos, sobra.

Meta: "Usa preguntas de opción múltiple para cualificar… menos preguntas = más envíos, más preguntas = más calidad. Limita las de respuesta corta" (S05-013). Recomendado por Meta: rangos en vez de listas largas (S05-011).

### Plantilla para servicios / high-ticket (instant form Higher intent)

| # | Pregunta | Tipo | Para qué |
|---|---|---|---|
| 1 | ¿Qué describe mejor tu situación? (3-4 opciones de etapa/encaje) | Multiple choice | Segmentar y descalificar con lógica condicional |
| 2 | ¿Cuál es tu principal objetivo en los próximos 90 días? | Multiple choice | Contexto para el setter, relevancia |
| 3 | ¿Cuándo quieres empezar? (Ya / 1-3 meses / Solo investigando) | Multiple choice | Urgencia (predictor fuerte de cierre) |
| 4 | Si encajamos, ¿estás en disposición de invertir en [rango de precio del programa]? (Sí / Necesitaría financiación / No) | Multiple choice | Capacidad de inversión **sin pedir ingresos** |
| 5 | ¿Por dónde prefieres que te contactemos? (WhatsApp / llamada / email) + franja | Multiple choice | Aumenta tasa de contacto |
| 6 | (Opcional) Cuéntanos en una frase tu reto | Short answer, min. 20 caracteres | Filtra bots; da material al setter |
| — | Nombre, email, teléfono | Prellenado | Contacto (con SMS verification) |

**Sobre la pregunta 4:** Meta prohíbe pedir "información financiera… ingresos, patrimonio, estado de deuda" (S05-016). Preguntar si el usuario está dispuesto a invertir una cantidad concreta en *tu* servicio no es, literalmente, pedir sus ingresos, y es práctica habitual; pero el revisor puede interpretarlo de forma amplia. **[HYPOTHESIS]**: formula siempre en términos de la oferta ("¿encaja una inversión de X?") y nunca "¿cuánto ganas/facturas?" en B2C. En B2B, "tamaño de empresa / facturación de la empresa" es habitual en las plantillas de Meta (empleados sí aparece en su tabla oficial), pero "facturación" es zona gris.

**Qué NO preguntar:**
- Lo que Meta ya prellena con otro nombre (está prohibido hacer preguntas "sustancialmente iguales" a las prellenadas). **[OFFICIAL META]**
- Salud, situación financiera personal, credit score, historial penal, orientación sexual, religión, afiliación política, raza, números de cuenta, contraseñas. **[OFFICIAL META]**
- Varias preguntas abiertas largas: matan la conversión y Meta lo desaconseja.
- Preguntas cuya respuesta no vas a usar.

### Lead magnet / registro a webinar (More volume)
Nombre + email (+ teléfono solo si vas a hacer SMS/WhatsApp de recordatorio con consentimiento) + 1 pregunta de segmentación (nivel/situación). Aquí la fricción cuesta más de lo que filtra: la cualificación ocurre después (asistencia, aplicación).

## 5. Context card / intro: el filtro más barato

La intro es texto que el usuario lee *antes* de las preguntas. Úsala para:
- Decir qué pasa después ("Un especialista te escribirá por WhatsApp en menos de 15 minutos en horario laboral").
- Decir para quién **no** es ("No es para quien busca resultados sin trabajo", "Solo empresas con equipo comercial").
- Anclar precio o rango si quieres filtrar por capacidad ("Programa de acompañamiento desde X €").

Meta recomienda usar la intro para explicar qué se recibe y qué esperar (S05-013). El efecto de anclar precio en la intro no está medido públicamente → **[HYPOTHESIS]**, pero es la misma lógica que el "precio en la landing" de los funnels de aplicación.

## 6. Pantalla final (ending) y siguiente paso

La pantalla final es el momento de mayor intención. Opciones 2026:
- **Book time (reserva embebida):** el calendario de Calendly o LeadConnector/HighLevel aparece en la pantalla de agradecimiento con nombre, email y teléfono prellenados; el proveedor de calendario gestiona confirmaciones. Según el Help Center (2026-10-16): **solo se embebe en la app móvil de Facebook** (en Instagram y otros placements el CTA "Book time" abre el enlace en un navegador in-app), hay que pegar el **enlace directo** del partner (no URLs propias ni páginas con calendario embebido) y **"los datos de reserva no se reportan en Ads Manager"** → la cita no es una señal optimizable salvo que la devuelvas tú vía CAPI CRM. Lanzado el 24-06-2026; disponibilidad global prevista en octubre (SMT) o noviembre (otra fuente). **[OFFICIAL META]** (S05-095, S05-059 a S05-062). Focus Digital estima un no-show del 8% para "booking instantáneo al rellenar" frente al 33% de "lead form de paid social" sin booking (estimaciones, confianza baja-media, S05-040).
- **Chat con leads por Messenger / WhatsApp (lead nurturing):** sección *Lead nurturing → Follow-up channels* (Chat on Messenger / Instagram / WhatsApp) con automatización integrada o plantilla de partner; "Chat on WhatsApp" puede activarse automáticamente si la Página tiene WhatsApp vinculado; puede no estar disponible en todas las cuentas (S05-096). Meta reporta +~10% de mensajes de alta intención con "Chat with leads on Messenger" (S05-005); y con qualified leads + Meta source, "Leads with WhatsApp conversations" como evento de follow-up (S05-007).
- **Llamar al negocio** (botón en la pantalla de mensaje para leads).
- **Link a web** (VSL, caso de éxito, página de "qué esperar de la llamada").

Pregunta de cita nativa (*appointment request*): no es un calendario real; disponibilidad fija L-D 7:00-22:00, **solo app de Facebook móvil**. Úsala solo como preferencia de franja. **[OFFICIAL META]** (S05-018)

## 7. Spam, bots y leads falsos: causas y soluciones

### Causas (por orden de impacto probable)

1. **El objetivo:** "Maximize leads" busca a quien más envía formularios. **[STRONG INFERENCE]**
2. **Autofill + More volume:** envíos en dos toques, a veces sin leer; datos de perfil antiguos o falsos ("Mrs. Magic Woman" en un caso documentado). **[EMPIRICAL]**
3. **Placements de baja calidad**, en especial **Audience Network**, señalado por agencias y vendors anti-fraude como fuente de envíos incentivados o automatizados. **[EMPIRICAL]** (fuentes agencia/vendor, S05-051, S05-085; Meta no reconoce el problema públicamente).
4. **Bots/granjas** dirigidos a formularios, más frecuentes en verticales de alto pago por lead (seguros, finanzas, inmobiliaria). **[EMPIRICAL]** (la propia Meta presenta el SMS OTP como filtro de "spam bots y malos actores").
5. **Organic leads** y compartidos (si Sharing = Open).
6. **Problemas de proceso:** el lead es real pero no recuerda haber rellenado porque le llamaste 3 días después. Esto se confunde a menudo con "lead falso". **[STRONG INFERENCE]**

### Soluciones (de más a menos estructural)

| Palanca | Efecto | Coste |
|---|---|---|
| Qualified leads + CAPI CRM (enviar "basura" como etapa propia) | Cambia el objetivo del algoritmo | Integración (horas con partner) |
| SMS verification | Elimina números falsos/bots | Menos volumen, solo móvil |
| Higher intent + context card honesta | Menos envíos accidentales | Menos volumen |
| Pregunta short answer con mínimo de caracteres / lógica condicional de descalificación | Filtra bots simples y mal encaje | Fricción |
| Contacto <5 min + recordatorio de "dónde nos conociste" | Recupera leads "olvidadizos" | Proceso comercial |
| Exclusión de placements | Corta fuentes malas | **Desde ago-2026 solo a nivel de cuenta en Leads/Sales** (afecta a todas las campañas) y "Allow limited spending to excluded placements" podía gastar hasta un 5% en excluidos |
| Funnel web o mensajería | Más intención, menos volumen | CPL más alto |

**Cambio 2026 importante:** Meta está retirando las exclusiones de placement a nivel de ad set en Sales, Leads y App promotion (Engagement no; corrección 2026-11-09) (avisos desde 19-20 de agosto de 2026; guía oficial de alternativas difundida el 12-10-2026). Alternativas: exclusiones a nivel de cuenta por objetivo, *value rules* por placement (rebaja de puja máx. −90%, no bloquea) y creatividad por placement. **[OFFICIAL META]** + **[EMPIRICAL]** (S05-049, S05-064, S05-065). Consecuencia: si Audience Network te mete basura, la exclusión ya no es quirúrgica. Antes de bloquear, mira el **breakdown por placement de leads → cualificados → agendas** (no de CPL) a 30 días.

## 8. Medición e integración

- **Descarga limitada a 90 días** → CRM obligatorio (S05-019).
- **Integración:** directa (lista de CRMs en Business Suite), terceros (Zapier, LeadsBridge…) o custom (Webhooks + Graph API) (S05-023). Puedes conectar **varios CRMs** y elegir cuál recibe cada formulario (S05-057).
- **Tracking parameters** en el instant form: parámetros ocultos (campaña, ad set, anuncio, ángulo) que llegan al CSV y al CRM integrado → imprescindible para el informe por anuncio hasta cash (archivo 09). **[OFFICIAL META]** (S05-024)
- **Guarda `leadgen_id`, `ad_id`, `adset_id`, `campaign_id`, `form_id`** en el contacto del CRM. El lead ID es la llave de qualified leads; los IDs de anuncio son la llave del informe.
- **Lookalikes:** Meta recomienda semillas de **clientes**, no de quien rellenó formularios (S05-013).
- **Retargeting de abandono:** audiencia de engagement "abrió el formulario y no lo envió". Meta lo recomienda (S05-013).

## 9. Instant form vs formulario web: lo que dice la evidencia

| Fuente | Resultado | Confianza |
|---|---|---|
| Jon Loomer, test A/B (mayo 2024, 630 leads, mismo anuncio/audiencia) | IF: 392 leads a 2,04 $; web: 238 a 3,77 $. Calidad (clic en emails): 29,1% vs 29,0%. Coste por lead de calidad 7,03 $ vs 13,01 $. Entregabilidad email 83,7% vs 92,4% | alta (un anunciante, lead magnet) |
| Meta (oct-2025) | Campañas híbridas web + IF: −14 a −24% CPL vs solo web | media (autorreportado) |
| Meta (2026) | Qualified leads: −21% coste por lead de calidad en IF, −9,5% en web | media (autorreportado) |
| Agencias B2B y servicios locales (varias, 2025-2026) | Leads de formulario cierran a la mitad o peor que los de landing; contacto más bajo | baja (sin metodología pública) |

Conclusión **[CONTESTED]**: para un lead magnet o captación B2C sencilla, el instant form suele ganar en coste por lead útil. Para high-ticket y B2B con ciclo comercial, la diferencia depende de la fricción que pongas (higher intent, SMS, preguntas) y de la velocidad de contacto. La forma honesta de decidir es un test con el **mismo** anuncio, presupuesto igual, y medir hasta agenda/venta en el CRM durante ≥4 semanas.

## Implicaciones operativas

- Por defecto para servicios/high-ticket: **Higher intent + SMS verification + 3-5 preguntas de opción múltiple + intro con "qué pasa después" + ending con Book time o WhatsApp**.
- Para lead magnets: More volume + 1 pregunta de segmentación; la calidad se trabaja en el nurturing.
- Nunca lances sin CRM integrado, tracking parameters y `leadgen_id` guardado.
- Revisa la casilla de SMS: puede estar activada por defecto (y limita placements a móvil).
- Mide placements por coste por agenda, no por CPL, antes de tocar exclusiones de cuenta.

## Errores frecuentes

- Pedir 8-10 preguntas abiertas "para cualificar": hunde la conversión y no mejora la calidad tanto como 3-4 de opción múltiple bien elegidas.
- Preguntar ingresos o patrimonio (prohibido) → anuncio rechazado.
- Usar el formulario desde la Página (sin opciones avanzadas).
- No mirar la pantalla final: es el mejor momento para agendar o abrir WhatsApp.
- Dejar Sharing en Open en ofertas de pago.
- Descargar CSVs a mano y llamar al día siguiente.

## Preguntas abiertas

- Efecto cuantificado de Higher intent y de desactivar autofill (Meta no publica cifras).
- ~~Si la reserva embebida envía un evento a Meta~~ → resuelto: Meta dice que los datos de reserva no se reportan en Ads Manager (S05-095). Queda abierto si lo hará en el futuro.
- Hasta dónde llega la prohibición de "información financiera" en preguntas sobre presupuesto/capacidad de inversión.
- Impacto de la retirada de exclusiones por ad set en la calidad media de lead en cuentas españolas.

## Fuentes clave

- [About instant form types](https://www.facebook.com/business/help/252352181957512) — vigente 2026-10-15 — meta-oficial (S05-009)
- [Enable the SMS verification feature](https://www.facebook.com/business/help/898260175547909) — vigente 2026-10-15 — meta-oficial (S05-010)
- [Add custom questions](https://www.facebook.com/business/help/774623835981457) — meta-oficial (S05-011)
- [Best practices to create lead ads](https://www.facebook.com/business/help/435270316658768) — meta-oficial (S05-013)
- [Questions prohibited on your instant form](https://www.facebook.com/business/help/219356599612120) — meta-oficial (S05-016)
- [About expired leads](https://www.facebook.com/business/help/1526849577619206) — meta-oficial (S05-019)
- [Testing quality leads (Instant Forms vs website)](https://www.jonloomer.com/testing-quality-leads/) — 2024-05-06 — practitioner (S05-032)
- [Meta launches integrated booking for lead ads](https://www.socialmediatoday.com/news/meta-launches-integrated-booking-for-lead-ads/823711/) — 2026-06-24 — prensa (S05-059)
- [Meta Ad Placements: Can You Still Exclude Them?](https://thesocialshepherd.ca/meta-ad-placement-exclusions-2026/) — 2026-09-16 — agencia (S05-064)
