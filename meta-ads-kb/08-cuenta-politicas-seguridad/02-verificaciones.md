# Verificaciones en Meta: identidad, empresa, dominio, anunciante, sectores regulados y Meta Verified

> Última verificación: 2026-10-15 · Autor: A08 (agente) · Ámbito: todas las verificaciones que afectan a anunciar en Meta (2025-2026), cuándo son obligatorias, para qué sirven y cómo afectan a infoproductos, formación, high-ticket y agencias en España/UE.

## TL;DR

- **Hay al menos 9 verificaciones distintas** y no se sustituyen entre sí:
  - teléfono (anunciante nuevo);
  - identidad personal (ID);
  - Business verification (Security Centre);
  - verificación de dominio;
  - advertiser/payer verification (transparencia);
  - autorizaciones sectoriales (financieros, cripto, juego, adicciones, fármacos, política);
  - verificación del método de pago;
  - 2FA/passkeys;
  - Meta Verified (de pago).

  Verificar la empresa "no da badge" y Meta Verified "no es" business verification. **[OFFICIAL META]** ([S08-054], [S08-059])
- **Meta está empujando la verificación como arma anti-scam.** Objetivo declarado: que el 90 % de sus ingresos publicitarios venga de anunciantes verificados a finales de 2026 (70 % en 2025). Pide verificación según dónde se entregan los anuncios, el historial de incumplimientos y si el tipo de anuncio es "más susceptible de abuso". **[OFFICIAL META]** ([S08-015], [S08-014])
- **España está en la lista de verificación obligatoria para anuncios de productos/servicios financieros**, junto con Australia, Hong Kong, India, Irlanda, Israel, Taiwán, Tailandia, Reino Unido y EE. UU. Polonia se añadió el 28-ago-2026. No hemos podido verificar la fecha de inclusión de España ni los requisitos concretos de su desplegable. **[OFFICIAL META]** ([S08-011], [S08-014])
- **La educación financiera sin capacidad de contratar suele estar exenta de esa verificación.** Exentos: brand ads de bancos/aseguradoras, noticias, "información sobre educación financiera", formación para pedir o gestionar préstamos, y anuncios educativos que no permiten obtener ni conectar con el producto. Un curso de trading que enlaza con un broker, da señales o capta inversión deja de ser "solo educación". **[OFFICIAL META]** para las exenciones; la frontera es **[STRONG INFERENCE]** y requiere asesoría legal.
- **UE (DSA):** desde el 5-jun-2023, todo anuncio nuevo o editado dirigido a la UE (o "worldwide") requiere declarar **advertiser** y **payer**. Desde mar-2026 Meta usa el término "advertiser" en lugar de "beneficiary". Sin estos datos, el anuncio no se publica. **[OFFICIAL META]** ([S08-013], [S08-058])
- **Business verification acelera la subida del límite diario de gasto** y es requisito para varias funciones (Advanced Access en apps, badge de Meta Business Partner, WhatsApp Business Platform, transparencia de Páginas en EE. UU.). Resolución: de 10 minutos a 14 días hábiles. **[OFFICIAL META]** ([S08-038], [S08-054], [S08-055])
- **Meta Verified for businesses** (de pago) da badge, protección contra suplantación y soporte humano por chat/email. Plus añade prioridad, Premium llamada y Max monitorización de casos. **Exige activar Advanced Protection en el portfolio, sin posibilidad de desactivarlo después.** Desde el 15-sep-2026 coexiste con los planes de negocio de **Meta One** (Essential/Advanced/Expert/Max). **[OFFICIAL META]** ([S08-059], [S08-060], [S08-019])
- **Recomendación para nichos de alto riesgo:** completar de forma proactiva business verification, verificación de dominio y advertiser verification antes de escalar. Meta dice explícitamente que conviene "verificar proactivamente para preparar la cuenta para requisitos futuros". **[OFFICIAL META]** ([S08-058]); el beneficio en reducción de fricción es **[STRONG INFERENCE]**

## 1. Tabla maestra de verificaciones

| Verificación | Qué demuestra | Quién la hace | ¿Obligatoria? | Dónde | Plazo de revisión | Notas clave |
|---|---|---|---|---|---|---|
| **Teléfono del anunciante** | Que hay una persona/negocio contactable | Full control de la cuenta publicitaria | A anunciantes nuevos se les puede exigir antes de publicar | MBS → Authorizations and verifications; Ads Manager | Inmediato (código válido 30 min) | SMS, llamada o WhatsApp; también para anunciantes vía Marketing API **[OFFICIAL META]** ([S08-057]) |
| **Identidad personal (ID)** | Que el perfil es una persona real | El titular del perfil | Si el perfil está restringido, para SIEP, o si el advertiser/payer es una persona | BSH ("Confirm your identity"), Authorizations and verifications | Variable | Puede incluir videoselfie en recuperación **[OFFICIAL META]** ([S08-023], [S08-075]) |
| **Business verification** | Que el portfolio pertenece a una entidad legal real y que tú la representas | Full control del portfolio | No por defecto. Sí para ciertas funciones; Meta lo pide a veces por email | MBS → Security Centre → Start verification | Hasta 14 días hábiles | Datos legales exactos, web HTTPS, conexión por email de dominio, teléfono, SMS, WhatsApp o dominio. Editar los datos obliga a re-verificar **[OFFICIAL META]** ([S08-055]) |
| **Dominio** | Que controlas el dominio | Full control del portfolio + admin del dominio | Necesaria para algunas funciones (brand safety, commerce); útil como método de conexión en business verification | MBS → Brand safety → Domains | Inmediato tras detectar meta-tag/HTML/DNS TXT | Se puede retirar la etiqueta después sin perder el estado **[OFFICIAL META]** ([S08-056]) |
| **Advertiser & payer (transparencia DSA/UE)** | Quién se beneficia del anuncio y quién paga | Admin/anunciante de la cuenta | Declarar: siempre en UE. Verificar: cuando Meta lo exige (país, tipo de anuncio, riesgo) | Ads Manager → Advertising settings; MBS → Authorizations and verifications | ~2 días hábiles | Agencias: advertiser = cliente; payer = cliente (o el revendedor dueño del portfolio) **[OFFICIAL META]** ([S08-058], [S08-013]) |
| **Servicios financieros (por país)** | Licencia o identidad para anunciar productos financieros | Advertiser/payer | Sí en 10 mercados (incluida España) + Polonia | Ads Manager / MBS | ~2 días hábiles (proceso común) | AU (AFSL), IN (SEBI), TW (licencia) piden número de licencia **[OFFICIAL META]** ([S08-011], [S08-058]) |
| **Cripto** | Licencia de un marco regulatorio cripto | Portfolio/ad accounts | Sí para promover trading cripto, exchanges y ETFs que contienen cripto | MBS → Authorizations and verifications → Cryptocurrency ads | ~48 h hábiles | NFTs y ETFs de acciones de empresas cripto no requieren autorización "por ahora" **[OFFICIAL META]** ([S08-062]) |
| **Juego online** | Licencia en cada jurisdicción | Portfolio | Sí; declarar cada jurisdicción nueva | MBS → Authorizations and verifications | n/d | 18+; 19 mercados no soportados **[OFFICIAL META]** ([S08-071]) |
| **SIEP (temas sociales/elecciones/política)** | Identidad + disclaimer "Paid for by" | Persona/organización | Sí donde se permite; **en la UE no se pueden publicar desde el 6-oct-2025** | MBS → Authorizations | n/d | Ver [07](07-categorias-especiales-y-sensibles.md) **[OFFICIAL META]** ([S08-064]) |
| **Método de pago (para el límite diario)** | Titularidad del método de pago | Admin de la cuenta | No; opcional si Meta te ofrece la subida | Payment settings → "Verify payment method" | Inmediato (OTP o cargo de USD 1 con código) | Re-verificar posible tras 30 días si Meta reajusta el límite **[OFFICIAL META]** ([S08-038]) |
| **2FA / passkeys** | Seguridad de acceso | Cada usuario | Obligatoria en ciertos portfolios >90 días y en ciertas regiones; passkeys obligatorias en algunos casos | Accounts Centre; MBS → Business portfolio info | Inmediato | Sin 2FA Meta puede quitar el acceso a anunciar o métodos de pago **[OFFICIAL META]** ([S08-047], [S08-049]) |
| **Meta Verified for businesses** | Autenticidad del negocio + badge | Full control del portfolio | No (de pago) | MBS → Settings → Meta Verified | Hasta 3 días hábiles | Requiere Advanced Protection en el portfolio; ver §5 **[OFFICIAL META]** ([S08-059]) |

## 2. Advertiser verification (transparencia) — lo que cambia en 2025-2026

**Cuándo la pide Meta** ([S08-058], [S08-012]):
- según si eres organización o persona, y si pagas anuncios en beneficio de otro (agencias, revendedores);
- si entregas anuncios en un país cuya ley o guía exige verificación;
- si promocionas anuncios "más susceptibles de abuso por scammers";
- por antigüedad de la cuenta (teléfono en cuentas nuevas), por categoría o targeting, por 2FA, por funciones usadas, y por sospecha de compromiso o infracción.

**Estados posibles:**
1. **Sin plazo:** aviso para verificar cuando quieras. Meta recomienda adelantarse.
2. **Con plazo:** si no verificas a tiempo, se pausan los anuncios.
3. **Anuncios pausados:** no puedes publicar nuevos hasta verificar.
4. **Cuenta restringida:** en algunos casos, restricción inmediata hasta completar la verificación.

**Organización vs persona:**
- *Organización:* Meta intenta encontrarla en bases de datos de terceros. Si no la encuentra, pide documentos (certificado de constitución, licencia de actividad) que deben coincidir con nombre legal, teléfono y dirección. La conexión se confirma por email (el dominio debe coincidir con la web declarada), llamada, SMS, WhatsApp o ID de un *stakeholder* que figure en el registro.
- *Persona:* ID oficial. Si el advertiser o payer no tiene acceso a la cuenta, se le puede dar acceso parcial o puede verificar desde su propia cuenta y reutilizar la verificación.

**Agencias:** el **advertiser es el cliente** y el **payer es el cliente** cuyos anuncios publicas. En reventa, el payer es el revendedor dueño del portfolio. **[OFFICIAL META]** Implicación: la agencia necesita los datos del cliente y, a veces, que el cliente verifique. No se puede "prestar" la identidad de la agencia a un cliente de riesgo. **[STRONG INFERENCE]**

**UE/DSA** ([S08-013]):
- Advertiser y payer son obligatorios en todo anuncio nuevo o editado dirigido a la UE o con "worldwide".
- Se publican en la Ad Library (no en el anuncio) y se conservan 1 año desde la última impresión.
- Meta afirma que no afectan a entrega, coste ni revisión.
- Para fijar valores por defecto hace falta full control de la cuenta publicitaria.
- España incluye Canarias, Ceuta y Melilla en la lista.

## 3. Verificación para anunciantes financieros (foco España)

**Lo verificado** ([S08-011]):
- Lista vigente: Australia, Hong Kong, India, Irlanda, Israel, **España**, Taiwán, Tailandia, Reino Unido y EE. UU. "Requirements for each region may be significantly different." Si un país no aparece, "no hay requisito de verificación… por ahora".
- Productos en alcance (pueden requerir licencia): seguros, hipotecas, préstamos, productos y oportunidades de inversión, solicitudes de tarjetas de crédito.
- Exentos (si el anuncio no se centra en un producto en alcance):
  - brand ads de bancos y aseguradoras;
  - noticias sobre productos financieros;
  - información de educación financiera;
  - formación para solicitar o gestionar préstamos;
  - anuncios educativos que no dan la capacidad de obtener ni de conectar con el producto.
- Polonia: desde el 28-ago-2026, verificación para *todos* los anunciantes de servicios financieros dirigidos a Polonia, tras la presión del gobierno polaco. **[OFFICIAL META]** ([S08-014])

**Lo no verificado:**
- La fecha en que España entró en la lista y qué documento concreto pide Meta para España (el desplegable por país no se renderiza sin sesión). Por analogía con el Reino Unido (registro FCA) y con Google en España (autorización CNMV/Banco de España desde 2023), es plausible que Meta pida una autorización o registro de un supervisor español. **[HYPOTHESIS]**
- La cifra de "38 países" que circula en blogs. No la respalda ninguna fuente de Meta. **[HYPOTHESIS — tratar como no fiable]**

**Implicaciones para formación e infoproductos financieros:**

| Oferta | ¿Probable alcance de verificación financiera? | Evidencia |
|---|---|---|
| Curso de finanzas personales (presupuesto, ahorro) sin productos | Exento (educación financiera) | **[OFFICIAL META]** exenciones |
| Curso de inversión/trading que enseña conceptos | Probablemente exento si no conecta con el producto | **[STRONG INFERENCE]** |
| Curso + enlace de afiliado a broker / apertura de cuenta / copy-trading / señales | Probablemente en alcance (conecta con un producto de inversión) y además sujeto a la regulación de la CNMV | **[STRONG INFERENCE]**; asesoría legal |
| Mentoría de "oportunidades de inversión" (inmobiliaria, cripto, fondos) | En alcance + riesgo de "investment scheme" en Prohibited Commercial Practices | **[STRONG INFERENCE]** |
| Servicios de asesoría financiera o intermediación de crédito (high-ticket) | En alcance; además SAC de crédito obligatoria en España si hay crédito | **[OFFICIAL META]** ([S08-061]) |

**Asesoría legal obligatoria:** la publicidad de servicios de inversión y criptoactivos en España tiene regulación propia (CNMV, incluida la circular sobre publicidad de criptoactivos) y la intermediación crediticia la tiene del Banco de España. Este documento no evalúa el cumplimiento legal.

## 4. Business verification: cuándo merece la pena (casi siempre en este nicho)

Para qué sirve, según Meta ([S08-054]):
- Puede permitir subir el **límite diario de gasto más rápido**.
- **Advanced Access** a permisos de Meta for Developers. Relevante si usas apps propias, CAPI vía app o el MCP con app propia.
- Requisito para ser **Meta Business Partner** con badge.
- WhatsApp Business Platform (algunas funciones).
- Transparencia de Páginas con gran audiencia en EE. UU. o con anuncios SIEP en EE. UU.
- Agencias con sede en China.
- Prerrequisito habitual en verificaciones de servicios financieros.

Cómo hacerla bien ([S08-055]):
- Datos **idénticos** al registro mercantil o censo de Hacienda (razón social, dirección, teléfono).
- Web que cargue y use **HTTPS**.
- Para el email de verificación, un **email del dominio** de la web (no Gmail).
- Si no hay match en bases de datos: escritura o certificado de constitución, alta censal o documento fiscal que muestre nombre, dirección y teléfono.
- **Cada edición de los datos de empresa obliga a re-verificar.** Hay que decidir bien qué entidad legal será la dueña del portfolio antes de verificar.
- Si se factura con monthly invoicing, se puede verificar con la línea de crédito propia, sin documentos.
- Dar información falsa o intentar verificar un negocio que no representas → Meta puede retirar la verificación y "tomar acciones adicionales en la cuenta". **[OFFICIAL META]**

Autónomos y personas físicas: algunos portfolios aparecen como "Ineligible for verification" en Security Centre. Meta indica que entonces no hace falta verificar ahí, aunque otras superficies pueden pedir verificación por otros flujos. **[OFFICIAL META]** ([S08-055])

## 5. Meta Verified for businesses y Meta One (2026)

**Meta Verified for businesses** ([S08-059], [S08-060]):
- Planes: **Standard** (badge, protección contra suplantación, soporte por chat y email), **Plus** (soporte priorizado), **Premium** (llamadas del soporte, protección de suplantación para 2 empleados) y **Max** (monitorización activa de casos, 5 empleados).
- Precios: la página pública de Meta Verified (oct-2026) muestra para creadores Standard 14,99, Plus 49,99, Premium 149,99 y Max 499,99 USD al mes, "no disponible en todas las regiones". Para empresas remite a otra web sin precios visibles. La misma página dice ya que "Meta Verified features are now available in Meta One". **[OFFICIAL META]** ([S08-112]) Algunas guías citan precios promocionales de negocio (44,99/119,99/349,99 USD el primer año), que no hemos verificado. **[HYPOTHESIS]**
- **Requisitos:**
  - activos elegibles: Página de Facebook, perfil profesional de IG o perfil de WhatsApp Business;
  - hasta 2 o 3 activos del mismo portfolio;
  - **Advanced Protection activada en el portfolio, que no se puede desactivar con la suscripción activa**;
  - datos que coincidan con el negocio.
- El soporte cubre: gestión de la suscripción, pagos, estado de verificación, "acceso general a la cuenta o problemas de seguridad" y edición de perfil o Página. **No menciona expresamente cuentas publicitarias restringidas.** **[OFFICIAL META]** Practitioners: da acceso más fácil a humanos, pero no garantiza reinstauraciones. **[EMPIRICAL]** ([S08-091])
- Para contactar el soporte desde MBS hace falta full control del portfolio y ordenador. En la app de IG basta con tener acceso a la cuenta profesional. Los casos se cierran solos si no respondes en 7 días.

**Meta One (15-sep-2026)** ([S08-019], [S08-090]):
- Planes de negocio: **Essential** (desde 14,99 USD), **Advanced** (49,99), **Expert** (149) y **Max** (499), por perfil o Página.
- Essential incluye badge e impersonation protection "pending verification". Jon Loomer lo describe como "esencialmente Meta Verified".
- Casos de soporte humano según practitioners: Essential 0, Advanced 1/mes, Expert 5/mes, Max ilimitados. **[EMPIRICAL — no confirmado en la nota oficial]**
- Meta no ha dicho oficialmente que Meta One sustituya a Meta Verified. El Help Center de oct-2026 sigue documentando Meta Verified. **[OFFICIAL META]** + migración futura **[HYPOTHESIS]**

**¿Merece la pena para infoproductos y agencias?** **[CONTESTED]**
- *A favor:* soporte humano en español por chat/email cuando falla todo lo demás; protección contra suplantación (muy relevante para formadores con marca personal, que son blanco de celeb-bait y perfiles falsos).
- *En contra:* no compra inmunidad ni reinstauraciones; el alcance del soporte sobre cuentas publicitarias no está documentado; obliga a Advanced Protection (bueno para seguridad, pero añade fricción operativa).
- *Regla práctica:* si la marca personal genera más de unos pocos miles de euros al mes vía Meta, o hay suplantaciones activas, el plan de entrada se paga solo como seguro de soporte. **[STRONG INFERENCE]**

## 6. La ofensiva de verificación anti-scam y por qué afecta a anunciantes legítimos

- **Mar-2026:** Meta anuncia la ampliación de la verificación de anunciantes. Pedirá verificar según la ubicación de entrega, el historial de incumplimientos y los tipos de anuncio "más susceptibles de abuso". Objetivo: 90 % de los ingresos de anunciantes verificados a fin de 2026 (frente al 70 %). El 10 % restante serían negocios de bajo riesgo "como una heladería local". **[OFFICIAL META]** ([S08-015])
- Según Reuters (vía prensa), Meta estimó internamente que la verificación universal costaría unos USD 2.000 M. Taiwán, tras una ley que obliga a verificar, reportó un −96 % de anuncios de inversión fraudulentos. **[EMPIRICAL — prensa sobre documentos internos]** ([S08-097])
- Singapur ha empujado la verificación de todos los anunciantes dirigidos a su mercado y el reconocimiento facial. **[EMPIRICAL — prensa]** ([S08-110])

**Lectura para el nicho:** "ganar dinero", formación de negocio, trading o cripto, IA para negocio y salud o pérdida de peso son exactamente las categorías que Meta y los reguladores asocian con scams. **[STRONG INFERENCE]** Lo esperable es:
1. más avisos de verificación con plazo;
2. menos tolerancia con cuentas no verificadas en estos ángulos;
3. más revisión manual o adicional si el historial tiene rechazos.

Verificar todo de antemano reduce la probabilidad de que una pausa por verificación coincida con un lanzamiento. **[STRONG INFERENCE]**

## Implicaciones operativas

- **Antes de escalar una cuenta nueva de un cliente de formación o high-ticket**, completar en este orden:
  1. 2FA/passkeys de todos los usuarios;
  2. business verification del portfolio del cliente;
  3. verificación de dominio;
  4. advertiser/payer por defecto (cliente/cliente);
  5. verificación del teléfono de la cuenta publicitaria.
- **Ofertas con producto financiero real** (crédito, inversión, seguros): verificación financiera española + SAC si hay crédito + revisión legal del copy por la CNMV/Banco de España. Sin esto, no lanzar.
- **Mantener un "dossier de verificación"** por cliente: escrituras o alta, CIF/NIF, recibo con dirección, dominio y email corporativo, licencias, ID de los administradores. Acelera apelaciones y re-verificaciones.
- **No reutilizar verificaciones de la agencia para clientes.** El advertiser y el payer deben reflejar al cliente real.

## Errores frecuentes

- Verificar el portfolio con un email @gmail o con datos que no coinciden letra por letra con el registro.
- Editar el nombre o la dirección de la empresa después de verificar (pierdes la verificación).
- Comprar Meta Verified esperando que "desbanee" una cuenta publicitaria.
- Pensar que en la UE el campo advertiser/payer es opcional: sin él, el anuncio no se publica.
- Ignorar que un "curso de trading" con enlace al broker deja de ser educación financiera.

## Preguntas abiertas

- Requisito exacto de verificación financiera para España (¿número de registro de la CNMV o del Banco de España? ¿desde cuándo?).
- Si Meta ampliará en 2026-2027 la verificación obligatoria de todos los anunciantes financieros a otros países de la UE además de Polonia.
- Alcance real del soporte de Meta Verified/Meta One en cuentas publicitarias restringidas.
- Si los anunciantes de "make money/business opportunity" entran en la categoría "más susceptible de abuso" que dispara verificación (muy probable, no confirmado).

## Fuentes clave

- [About verification requirements that may affect financial services advertisers](https://www.facebook.com/business/help/719892839342050) — Meta, vivo — meta-oficial
- [Verification requirements for advertisers](https://www.facebook.com/business/help/810450577622394) — Meta, vivo — meta-oficial
- [About advertiser verification for ads transparency](https://www.facebook.com/business/help/983527276402621) — Meta, vivo (cambio mar-2026) — meta-oficial
- [Advertiser and payer requirements for ads targeting the EU](https://www.facebook.com/business/help/605021638170961) — Meta, desde 2023-06-05 — meta-oficial
- [About business verification](https://www.facebook.com/business/help/1095661473946872) y [Verifying your business](https://www.facebook.com/business/help/2058515294227817) — Meta — meta-oficial
- [Verify your domain](https://www.facebook.com/business/help/321167023127050) — Meta — meta-oficial
- [How do I verify my phone number as a new Meta advertiser?](https://www.facebook.com/business/help/1064155054687612) — Meta — meta-oficial
- [About Meta Verified for businesses](https://www.facebook.com/business/help/308979828303560) y [Contact Meta Verified support](https://www.facebook.com/business/help/832027668252804) — Meta — meta-oficial
- [Meta Launches New Anti-Scam Tools…](https://about.fb.com/news/2026/03/meta-launches-new-anti-scam-tools-deploys-ai-technology-to-fight-scammers-and-protect-people/) — Meta, 2026-03-11 — meta-oficial
- [Wzmacniamy w Polsce ochronę przed oszustwami](https://about.fb.com/news/2026/08/wzmacniamy-w-polsce-ochrone-przed-oszustwami/) — Meta, 2026-08-28 — meta-oficial
- [Introducing Meta One](https://about.fb.com/news/2026/09/introducing-meta-one-subscription-service-more-features-ai/) — Meta, 2026-09-15 — meta-oficial
- [Meta One Business Plans](https://www.jonloomer.com/meta-one-business-plans/) — Jon Loomer, 2026-09-22 — practitioner
