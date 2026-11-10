# Account Quality, restricciones y cuentas deshabilitadas

> Última verificación: 2026-10-15 · Autor: A08 (agente) · Ámbito: tipos de restricción (perfil, cuenta publicitaria, Business Portfolio, Página, dominio, data source), causas, señales tempranas, flujos de revisión/apelación 2025-2026, revisión por IA, "circumventing systems"/evasión, oleadas de baneos.

## TL;DR

- **El enforcement de Meta opera en capas y se contagia entre activos.** Meta puede restringir el Business Portfolio, la cuenta publicitaria, la Página o el perfil personal de quien anuncia. Desde el 9-sep-2026 Meta dice además que, ante infracciones repetidas, las sanciones pueden extenderse a "usuarios, Páginas y Business Portfolios asociados". **[OFFICIAL META]** ([S08-022], [S08-068])
- **Una cuenta deshabilitada por política tiene 6 meses para ser reinstaurada.** Pasado ese plazo ya no puede reinstaurarse, y Meta puede quedarse el saldo prepago no usado "donde la ley lo permita". Meta puede además deshabilitarla de forma permanente antes de los 6 meses. **[OFFICIAL META]** ([S08-022], [S08-023])
- **Las revisiones de restricciones de cuenta se hacen en Business Support Home** (Account status overview → "What you can do" → Request review). Solo puede pedirlas un admin. Meta dice que se resuelven "típicamente en 48 h". El número de intentos es limitado y la decisión tras la revisión es final. Los anuncios no se reactivan solos al levantarse la restricción. **[OFFICIAL META]** ([S08-024])
- **Las causas oficiales no son solo de contenido.** Meta también restringe por sospecha de hackeo, por no cumplir la 2FA obligatoria, por pagos fallidos, disputados o inusuales, y por "actividad inusual o de alto riesgo". En casos de agencias, una parte relevante de los bloqueos viene de pagos y seguridad, no de anuncios. **[OFFICIAL META]** ([S08-022]) Un vendor de gestión de accesos atribuye el 45 % a política, el 34 % a pagos, el 9 % a hackeos y el 7 % a inactividad. **[EMPIRICAL — dato de vendor, muestra no auditada]** ([S08-091])
- **Evadir el enforcement es la infracción que convierte un problema recuperable en uno terminal.** Entra aquí crear cuentas o activos nuevos para repetir infracciones, coordinar redes de cuentas, hacer cloaking o usar redirecciones engañosas. Meta lo trata como Account Integrity y Spam (antes "Circumventing systems"), y puede deshabilitar cuentas del mismo dueño que una cuenta ya deshabilitada. **[OFFICIAL META]** ([S08-025], [S08-069], [S08-070])
- **La revisión es cada vez más automatizada con LLMs.** Según el FT, los LLMs hacían en jun-2026 ~50 % de la revisión de contenido y anuncios, con objetivo >90 % en 2027. Meta dice que las apelaciones de deshabilitación de cuentas siguen pasando por humanos. Hay casos documentados de denegaciones rápidas sin explicación útil. **[OFFICIAL META]** sobre humanos en apelaciones ([S08-076], [S08-111]); **[CONTESTED]** sobre la calidad real ([S08-077], [S08-078])
- **El historial cuenta.** Meta reconoce que puede considerar "el historial de cumplimiento del anunciante" y el feedback de usuarios para decidir cuánta revisión aplica a un anuncio. Las cuentas con historial limpio sufren menos fricción. **[OFFICIAL META]** ([S08-034])
- **Usar el MCP oficial de Meta con agentes de IA (Claude Code incluido) no es en sí motivo de baneo**, según Meta. La narrativa de 2026 sobre "agentes de IA que banean cuentas" viene de vendors y apunta sobre todo a automatización de navegador o herramientas no registradas. **[OFFICIAL META]** ([S08-082]); el riesgo de la automatización no oficial es **[STRONG INFERENCE]** ([S08-007], [S08-008])

## 1. Mapa de capas de enforcement

| Capa | Qué se restringe | Cómo se ve | Consecuencia típica | Recuperación |
|---|---|---|---|---|
| **Anuncio** | Un anuncio concreto | "Rejected" en Ads Manager, email y Business Support Home | No se entrega; suma al historial de infracciones | Editar, crear nuevo o pedir revisión (ver [09](09-rechazos-apelaciones-que-no-hacer.md)) |
| **Cuenta publicitaria** | Ad account (sus anuncios y "algunos de sus activos publicitarios") | "Ad account disabled/restricted" en Business Support Home | Todos los anuncios parados; a los 6 meses sin reinstaurar, pérdida definitiva y posible pérdida de saldo prepago | Request review en BSH **[OFFICIAL META]** |
| **Business Portfolio** | El portfolio no puede anunciar | Banner en Business Suite/BSH | Afecta a todas las cuentas publicitarias que posee; a veces pérdida de capacidad de añadir admins/partners o crear cuentas | Request review; verificar identidad/empresa |
| **Página** | La Página no puede anunciar | Estado en BSH / "Page restricted from advertising" | No se pueden publicar anuncios con esa identidad | Request review |
| **Perfil personal** | La persona no puede usar productos de Meta para anunciar | "Your account is restricted from advertising" | Si es el único usuario de una cuenta publicitaria, esa cuenta también puede deshabilitarse; otros miembros del portfolio pueden seguir anunciando **[OFFICIAL META]** | Confirmar identidad (ID, a veces videoselfie) + request review |
| **Dominio** | Enlaces a ese dominio | Rechazo: "Ads must not promote restricted domains…" | Bloqueo de 60 días, renovable si continúa la actividad sospechosa **[OFFICIAL META]** ([S08-030]) | Usar otro dominio que cumpla (no para evadir una infracción real) |
| **Data source (píxel/dataset)** | Eventos que se pueden compartir/optimizar | Events Manager → Settings → "Data source categories" | Core setup / sin eventos estándar de mitad-final de funnel / restricción total (sobre todo salud) | Apelar la categorización en Events Manager; rara vez prospera según vendors **[EMPIRICAL]** ([S08-095]) |
| **Catálogo / commerce** | Productos o tienda | Commerce Manager / BSH | Productos rechazados o shop restringida | Revisión en BSH |

Notas:
- **Restricciones "suaves"** que no son un baneo pero sí una advertencia: límite diario de gasto más bajo, umbral de pago más bajo, pérdida de algunas funciones de pago o de anuncios, imposibilidad de añadir admins, partners o usuarios, e imposibilidad de crear cuentas publicitarias nuevas. Meta las aplica "temporalmente" mientras investiga actividad inusual. **[OFFICIAL META]** ([S08-022])
- Meta escribe "Business Support Home"; el índice de Advertising Standards aún dice que la revisión se pide "through Account Quality". Es la misma superficie (Account Quality es el nombre heredado). **[OFFICIAL META]** ([S08-001], [S08-033])

## 2. Causas oficiales de restricción

Según "About advertising restrictions" ([S08-022]) y "Common examples of violations" ([S08-025]):

1. **Infracciones de política graves o repetidas** de Community Standards, Advertising Standards, Commerce Policies u otros términos. No hace falta un "strike" grave: la acumulación basta. "Editing or deleting an ad that was rejected… will not remove the violation from your account." **[OFFICIAL META]** ([S08-031])
2. **Evasión del enforcement:**
   - crear cuentas publicitarias o activos nuevos "con la intención de repetir infracciones" tras una deshabilitación;
   - coordinar una red de cuentas o activos que publican anuncios iguales o parecidos que infringen de forma persistente o grave.
3. **Asociación con redes infractoras:** un activo "en estrecha conexión" con una red de cuentas que infringen o evaden puede ser restringido.
4. **Sospecha de compromiso o hackeo** del portfolio o de sus activos.
5. **No cumplir los requisitos de 2FA.** Es obligatoria en ciertos portfolios de más de 90 días y en ciertas regiones (ver [03](03-seguridad-business-portfolio-roles-partners.md)).
6. **Actividad de pago inusual**, alta tasa de pagos fallidos o pagos disputados (chargebacks).
7. **Límites temporales "hasta asegurarse de que el anunciante cumple de forma consistente"**, típicos en cuentas nuevas o tras infracciones.
8. **Verificación no completada en plazo:** si Meta exige verificación de anunciante y no se completa, los anuncios se pausan y "en algunos casos" la cuenta queda restringida hasta verificar. **[OFFICIAL META]** ([S08-058])

Causas reportadas por practitioners (no confirmadas por Meta como reglas):
- Método de pago a nombre distinto del negocio verificado, tarjeta de otro país, o tarjeta reutilizada de una cuenta deshabilitada. **[EMPIRICAL — agencias]** ([S08-092])
- Subidas bruscas de gasto en cuentas nuevas. **[HYPOTHESIS]**: coherente con que Meta controla el riesgo vía límite diario, pero no hay evidencia oficial de que escalar rápido cause baneos.
- Accesos desde muchas ubicaciones o VPN en agencias. **[EMPIRICAL — vendor]** ([S08-091])
- Reutilizar la misma creatividad infractora entre cuentas de varios clientes. Encaja con la "red coordinada" oficial. **[STRONG INFERENCE]**
- Inactividad prolongada (cifras como "56 días sin gasto" o "15 meses"). **[HYPOTHESIS — no verificado en fuentes de Meta]** ([S08-091])

## 3. Señales tempranas de riesgo (antes del baneo)

Prioridad para monitorizar semanalmente en cuentas de infoproductos y servicios:

| Señal | Dónde mirarla | Por qué importa | Evidencia |
|---|---|---|---|
| Rechazos acumulados (sobre todo por el mismo motivo) | BSH → anuncios rechazados (14/30/90 días) | Las restricciones llegan por infracciones "graves o repetidas" | **[OFFICIAL META]** |
| Anuncios aprobados y luego rechazados | Ads Manager / email | Re-revisión disparada por ocultaciones, bloqueos y reportes o por engagement inusual: señal de feedback negativo | **[OFFICIAL META]** ([S08-032]) |
| Bajada del límite diario de gasto o del umbral de pago | Billing & payments → Payment settings | Meta lo reajusta por infracciones, baja calidad o feedback | **[OFFICIAL META]** ([S08-037]) |
| Petición de verificar identidad, teléfono o anunciante | Notificaciones Ads Manager/MBS | Si no se completa en plazo: anuncios pausados o cuenta restringida | **[OFFICIAL META]** ([S08-058]) |
| Feedback score bajo (Página/commerce) | BSH | Afecta a entrega y puede llevar a restricciones | **[OFFICIAL META]** que existe y se revisa ([S08-033]); umbrales concretos (2.0/1.0) **[EMPIRICAL]** ([S08-092]) |
| Dominio con rechazos "restricted domain" | Rechazos | Bloqueo de 60 días; suele indicar que el dominio está asociado a cuentas deshabilitadas | **[OFFICIAL META]** ([S08-030]) |
| Data source recategorizado (salud/finanzas) | Events Manager | Pierdes eventos de optimización sin aviso continuo | **[EMPIRICAL]** ([S08-095]) |
| Usuarios del portfolio sin 2FA/passkey, o inactivos >90 días | Security Centre | Meta los marca como riesgo; pueden disparar restricciones | **[OFFICIAL META]** ([S08-046]) |

## 4. Flujo de revisión de restricciones de cuenta (oct-2026)

**Ruta oficial** ([S08-023], [S08-024]):
1. En ordenador, Business Support Home → **Account status overview**.
2. Seleccionar la cuenta restringida.
3. En **"What you can do"**, completar lo que pida Meta: confirmar identidad, completar verificación, asegurar la cuenta (hackeo) o **Request review**.
4. Seguir los pasos en pantalla. Meta revisa "típicamente en 48 horas, aunque puede tardar más".
5. Resultado: se mantiene (cuenta bloqueada) o se levanta (cuenta reinstaurada). **Los anuncios no se reactivan automáticamente.**

**Reglas duras oficiales:**
- Solo un **admin** de la cuenta puede pedir revisión.
- El número de revisiones de restricción es **limitado**. Una vez completada la revisión, "la decisión es final". Pedir revisión "no perjudica tu reputación con Meta".
- Ventana de **6 meses** para cuentas deshabilitadas por política. Después, imposible reinstaurar.

**Canales complementarios (2025-2026):**
- **Meta AI business assistant** (beta global desde abr-2026) en Ads Manager, Business Suite y BSH. Meta dice que ayuda a "resolver problemas de cuenta, incluido restaurar cuentas deshabilitadas", actualizar límites de gasto y resolver errores de pago, con un +20 % de resolución en pymes (dato de Meta). **[OFFICIAL META vía prensa]** ([S08-088])
- **Asistente de soporte Meta AI** para perfiles personales de Facebook/Instagram (dic-2025, ampliado mar-2026). Gestiona apelaciones de retirada de contenido y la recuperación de cuentas, con "apelaciones más rápidas y con asistencia de IA para casos elegibles". **[OFFICIAL META]** ([S08-075])
- Soporte humano vía Meta Verified/Meta One, partner o account manager: ver [05](05-soporte-meta-canales-elegibilidad.md).

**Revisión por IA y humanos.** Meta anunció el 19-mar-2026 que reduce moderadores externos y despliega IA para enforcement. Las "decisiones más complejas y de alto impacto", incluidas las apelaciones de deshabilitación de cuentas, siguen en manos de humanos. **[OFFICIAL META vía CNBC/TechCrunch]** ([S08-076], [S08-111]) Prensa basada en el FT: LLMs al ~50 % de la revisión de contenido y anuncios, objetivo >90 % en 2027, y Meta afirma un −13 % de errores frente a humanos. **[OFFICIAL META — cifras no auditadas]** ([S08-077]) Casos reportados por el NYT (jul-2026): negocios con cientos de miles de seguidores deshabilitados por "fraud and deception" y apelación denegada en una semana con aviso de que no podían pedir otra revisión. **[EMPIRICAL — casos periodísticos]** ([S08-078])
- **Postura:** **[CONTESTED]**. Meta sostiene que hay menos errores. Anunciantes y prensa documentan falsos positivos sin vía humana efectiva. Ambas cosas pueden ser ciertas a la vez: menos errores en media, pero los errores que quedan son más difíciles de revertir.

## 5. Qué funciona y qué no en apelaciones de cuenta

**Funciona (o al menos maximiza la probabilidad):**
- **Corregir la causa antes de apelar:** retirar o corregir los anuncios infractores, arreglar la landing (claims, páginas legales, coherencia), activar 2FA para todos y quitar usuarios sospechosos. **[STRONG INFERENCE]**: Meta revisa la cuenta y su contexto, no solo el texto de la apelación.
- **Completar todas las verificaciones** que pida "What you can do" con documentos que cuadren exactamente: nombre legal, dirección, web HTTPS, email del dominio. **[OFFICIAL META]** ([S08-055])
- **Apelación breve y factual:** qué activo, qué crees que se interpretó mal, qué has cambiado y qué controles has puesto. **[EMPIRICAL — agencias]** ([S08-092], [S08-093])
- **Escalar por un canal con humano** (Meta Verified/Meta One con casos de soporte, partner con representante) cuando la revisión automática falla. **[EMPIRICAL]**; la eficacia no está garantizada (ver [05](05-soporte-meta-canales-elegibilidad.md)).
- **Si el problema fue un hackeo:** asegurar las cuentas primero (contraseñas, sesiones, 2FA, quitar intrusos). Meta pide "Secure your account" como paso propio. **[OFFICIAL META]** ([S08-023])

**No funciona / empeora:**
- **Abrir cuentas o portfolios nuevos para seguir anunciando lo mismo.** Es exactamente la "evasión" que Meta lista, y puede arrastrar a los activos nuevos y a los asociados. **[OFFICIAL META]** ([S08-025], [S08-070])
- **Apelaciones en bucle o con textos genéricos:** gastan intentos limitados. **[OFFICIAL META]** sobre el límite; **[EMPIRICAL]** sobre la ineficacia.
- **Pagar a "recuperadores" que piden credenciales o te hacen ejecutar scripts.** Es un vector de phishing y malware documentado en 2025-2026. **[EMPIRICAL — informes de seguridad]** ([S08-084], [S08-085])
- **Esperar sin actuar:** el reloj de 6 meses corre.

## 6. "Circumventing systems" y evasión: qué es en 2026

La antigua política publicitaria "Circumventing Systems" ya no aparece como página propia en el índice de Advertising Standards. Su contenido vive ahora en:
- **Account Integrity (Community Standard), aplicable a activos de negocio:** evadir enforcement o procesos de revisión; cuentas del mismo dueño que cuentas deshabilitadas; cuentas creadas o reutilizadas para evadir una retirada previa; reincidencia; vinculación o coordinación con redes infractoras; cuentas creadas por medios automatizados "salvo vías autorizadas". **[OFFICIAL META]** ([S08-070])
- **Spam (Community Standard):** **cloaking** ("mostrar intencionadamente a los sistemas de integridad un contenido distinto del que ven los usuarios"), enlaces engañosos, redirecciones engañosas, funcionalidad falsa (botones de play que no reproducen), pop-ups trampa y suplantación de dominio. **[OFFICIAL META]** ([S08-069])
- **"Things you should know"** de Advertising Standards: prohibido vender, alquilar, comprar o intercambiar privilegios (p. ej. acceso de admin) y ayudar a evadir enforcement. Quien gestiona anuncios de terceros debe usar **cuentas publicitarias separadas por cliente**. **[OFFICIAL META]** ([S08-001])

Ejemplos prácticos que Meta trata como evasión o circunvención (combinando política y práctica):
- Landing distinta para el revisor y para el usuario (cloaking por IP, user-agent o geolocalización).
- Cambiar la URL o el contenido de la landing tras la aprobación para introducir claims prohibidos.
- Escribir palabras con caracteres raros o Unicode ("d1nero", "ɢᴀɴᴀʀ") para esquivar clasificadores. **[EMPIRICAL — agencias]** ([S08-092])
- Relanzar en masa el mismo anuncio rechazado con microcambios.
- Usar cuentas publicitarias "alquiladas", "agency accounts" de terceros o perfiles de otras personas para seguir anunciando tras un baneo.
- Crear un portfolio nuevo con la misma tarjeta, dominio, Página o personas tras un baneo por política.

## 7. Oleadas de baneos 2025-2026: qué sabemos

| Periodo | Qué pasó | Evidencia |
|---|---|---|
| Jun-jul 2025 | Oleada de deshabilitaciones erróneas de cuentas de Instagram/Facebook (muchas por supuestas infracciones de explotación infantil), petición en Change.org, cobertura de BBC/ABC/TechCrunch; Meta restauró algunas tras la presión de la prensa | **[EMPIRICAL — prensa]** ([S08-079]) |
| Dic-2025 | Meta anuncia un nuevo hub de soporte, asistente IA y apelaciones "más rápidas"; dice que la IA ha ayudado a evitar deshabilitaciones erróneas (sin cifras) | **[OFFICIAL META]** ([S08-075]) |
| Mar-2026 | IA de enforcement a escala; menos moderadores externos | **[OFFICIAL META]** ([S08-076]) |
| May-jul 2026 | Narrativa de "ban wave" ligada a agentes de IA o herramientas conectadas a Ads Manager (vendors). Meta lanza el MCP oficial (beta abr-2026, abierto 16-jul-2026) y afirma que usarlo no pone la cuenta en riesgo | Vendors: **[HYPOTHESIS/EMPIRICAL débil]** ([S08-007], [S08-008]); Meta: **[OFFICIAL META]** ([S08-082]) |
| Jul-2026 | NYT documenta baneos erróneos de negocios; petición >60.000 firmas | **[EMPIRICAL — prensa]** ([S08-078]) |
| Sep-2026 | Consolidación de "Prohibited Commercial Practices" con sanciones que pueden extenderse a activos asociados | **[OFFICIAL META]** ([S08-068]) |

Lectura operativa: no hay evidencia oficial de una "oleada" en un momento concreto que afecte a anunciantes de infoproductos como tal. Sí hay tres tendencias estructurales que suben el riesgo de falsos positivos en nichos "scam-adjacent" (ganar dinero, trading, IA para negocio, salud): (1) más automatización de la revisión; (2) presión regulatoria anti-scam con objetivos de verificación; (3) sanciones que se propagan a activos asociados. **[STRONG INFERENCE]**

## Implicaciones operativas

- **Arquitectura defensiva:**
  - activos clave (Página, IG, datasets, dominio) en el portfolio del dueño del negocio;
  - al menos 2 personas con full control;
  - 2FA/passkeys para todos;
  - cuentas publicitarias separadas por cliente o por línea de riesgo (p. ej. una cuenta para ofertas de "negocio/ingresos" y otra para contenido educativo general).

  Esto no sirve para "esquivar" sanciones, ya que Meta vincula activos asociados; sirve para aislar errores operativos y facilitar el diagnóstico. **[STRONG INFERENCE]**
- **Umbral de alarma:**
  - 2-3 rechazos por el mismo motivo en 30 días → congelar ese ángulo, revisar copy y landing antes de lanzar más;
  - cualquier bajada del límite diario o del umbral de pago → revisión completa de cumplimiento y seguridad. **[STRONG INFERENCE]**
- **Ante una restricción de cuenta:**
  1. no crear cuentas nuevas;
  2. diagnosticar (política vs pago vs seguridad);
  3. arreglar la causa;
  4. completar verificaciones;
  5. pedir revisión una vez, bien argumentada;
  6. escalar por canal humano;
  7. documentarlo todo (IDs, capturas, fechas).
- **Agentes de IA:** conectar vía el MCP oficial con reglas por cuenta (sin creación de campañas o con límite de presupuesto). Nunca usar automatización de navegador sobre Ads Manager ni tokens personales en herramientas no registradas. **[OFFICIAL META]** + **[STRONG INFERENCE]** ([S08-082], [S08-083])

## Errores frecuentes

- Confundir "rechazo de anuncio" con "restricción de cuenta" y reaccionar igual (crear cuentas nuevas por un simple rechazo).
- Borrar anuncios rechazados creyendo que limpia el historial: no lo limpia y además impide pedir revisión. **[OFFICIAL META]** ([S08-031])
- Que el único admin sea un freelancer o la agencia: si su perfil cae, la cuenta queda huérfana o deshabilitada (ver la nota oficial sobre "único usuario adjunto"). **[OFFICIAL META]** ([S08-022])
- Ignorar avisos de verificación con plazo.
- Reactivar campañas tras la reinstauración sin revisar qué las tumbó.

## Preguntas abiertas

- ¿Cuántos intentos exactos de "request review" permite Meta por tipo de restricción? Los foros hablan de ~3. **[HYPOTHESIS]**
- ¿Qué peso tienen las asociaciones (tarjeta, IP, dominio, personas) en la propagación de sanciones tras el cambio de sep-2026? Meta no publica umbrales.
- ¿Se pueden llevar las restricciones de cuentas publicitarias ante órganos de resolución extrajudicial de la DSA (Appeals Centre Europe)? Sus FAQ no mencionan anuncios (ver [05](05-soporte-meta-canales-elegibilidad.md)). **[HYPOTHESIS]**
- Reglas de inactividad (días sin gasto → desactivación): no verificadas en fuentes de Meta.

## Fuentes clave

- [About advertising restrictions](https://www.facebook.com/business/help/975570072950669) — Meta, vivo 2026 — meta-oficial
- [Troubleshoot a disabled or restricted account](https://www.facebook.com/business/help/422289316306981) — Meta, vivo — meta-oficial
- [Request a review for a restricted advertising account](https://www.facebook.com/business/help/530209463124901) — Meta, vivo — meta-oficial
- [Common examples of Meta advertising policy violations](https://www.facebook.com/business/help/3858246497787265) — Meta, vivo — meta-oficial
- [About ads in review](https://www.facebook.com/business/help/204798856225114) — Meta, vivo — meta-oficial
- [Account Integrity (Community Standard)](https://transparency.meta.com/policies/community-standards/account-integrity/) — Meta, último cambio 2026-05-28 — meta-oficial
- [Spam (Community Standard)](https://transparency.meta.com/policies/community-standards/spam/) — Meta — meta-oficial
- [Our Prohibited Commercial Practices policy](https://transparency.meta.com/policies/other-policies/our-prohibited-commercial-practices-policy/) — Meta, 2026-09-09 — meta-oficial
- [Manage ads from an AI agent with Meta ads AI connectors](https://www.facebook.com/business/help/1456422242197840) — Meta, 2026 — meta-oficial
- [Meta rolls out new AI content enforcement systems…](https://techcrunch.com/2026/03/19/meta-rolls-out-new-ai-content-enforcement-systems-while-reducing-reliance-on-third-party-vendors) — TechCrunch, 2026-03-19 — prensa
- [Meta To Use LLMs For Majority Of Content, Ad Review](https://www.mediapost.com/publications/article/416127/meta-to-use-llms-for-majority-of-content-ad-revie.html) — MediaPost/FT, 2026-06-26 — prensa
- [Meta's AI is deleting accounts…](https://thenextweb.com/news/meta-ai-moderation-account-bans) — TNW/NYT, 2026-07-22 — prensa
- [How to recover a disabled Facebook ad account in 2026](https://www.leadsie.com/blog/recover-disabled-facebook-ad-account) — Leadsie, 2026-10-02 — vendor
