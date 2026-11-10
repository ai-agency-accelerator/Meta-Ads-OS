# Seguridad del Business Portfolio: roles, partners, propiedad de activos, hackeos y offboarding

> Última verificación: 2026-10-15 · Autor: A08 (agente) · Ámbito: modelo de permisos actual (full control/partial access), partners vs personas, propiedad de activos, 2FA/passkeys/Advanced Protection, peer approval, agentes de IA (MCP), phishing y malware 2025-2026, recuperación de hackeos, offboarding. Checklist final.

## TL;DR

- **Nomenclatura actual** **[OFFICIAL META]** ([S08-044]):
  - Business Portfolio (antes Business Manager);
  - **Full control** (antes *admin*);
  - **Partial access** → *Basic* (antes *employee*) y *Apps and integrations* (antes *developer*);
  - opción avanzada **Finance access** (ver o gestionar);
  - **acceso temporal** de 3 a 75 días con revocación automática.

  A nivel de activo también hay full o partial access, con tareas concretas. Se puede tener full control de un activo sin tenerlo del portfolio.
- **Regla de propiedad:** el negocio (cliente) debe ser **dueño** de Página, IG, cuentas publicitarias, datasets/píxeles, catálogos, dominio, WhatsApp y apps. La agencia entra como **partner** con acceso compartido, no como dueña. Meta exige además usar **cuentas publicitarias separadas por cliente**. **[OFFICIAL META]** ([S08-001], [S08-053]) + **[STRONG INFERENCE]** sobre la propiedad
- **Mínimos de seguridad que Meta recomienda o exige:**
  - 2FA obligatoria (no desactivable) en ciertos portfolios de más de 90 días;
  - passkeys exigibles a anunciantes, portfolios con crédito o gasto alto y cuentas con Advanced Protection;
  - **2 personas activas con full control** ("second admin approval");
  - **≤10 personas con full control**;
  - quitar inactivos de más de 90 días, usuarios sin 2FA o passkey y emails de dominios públicos;
  - desactivar cuentas publicitarias sin uso en más de 1 año.

  **[OFFICIAL META]** ([S08-046], [S08-048], [S08-049])
- **Peer approval** (Security Centre) añade una segunda aprobación antes de publicar:
  - por defecto, solo anuncios sospechosos;
  - "extra", todos los anuncios (recomendado con partners o accesos temporales);
  - "custom", por encima de un presupuesto;
  - también dominios de confianza, países de confianza y bloqueo de anuncios click-to-message.

  Es la mejor defensa contra el anuncio fraudulento publicado desde una cuenta comprometida. **[OFFICIAL META]** ([S08-050])
- **El vector de ataque dominante en 2025-2026 no es la contraseña, es el engaño dentro de Meta.** Se abusa de emails reales de Meta (noreply@business.facebook.com) mediante solicitudes de partner con URLs en el nombre del negocio. Se usan señuelos de "Agency Partner Program" o "Meta Verified", falsos avisos de suspensión que llevan a "scripts de apelación" con malware, e infostealers (DuckTail/NodeStealer) que roban cookies de sesión. **[EMPIRICAL — informes de seguridad]** ([S08-084], [S08-085], [S08-086], [S08-087])
- **Meta nunca pide contraseña, datos de pago ni códigos** por chat, SMS, email o teléfono. Sus emails solo llegan desde dominios como fb.com, facebook.com, facebookmail.com, meta.com, metamail.com, instagram.com o support.facebook.com. Se puede verificar cualquier aviso en Business Support Home. **[OFFICIAL META]** ([S08-051])
- **Agentes de IA:** usar el **MCP oficial de Meta** (mcp.facebook.com/ads) con **reglas por cuenta publicitaria**: bloquear la creación de campañas, poner topes de presupuesto, etc. Las reglas las define quien tiene full control del portfolio. Los anuncios creados vía MCP nacen en pausa. **[OFFICIAL META]** ([S08-082])
- **Offboarding:** quitar a una persona del portfolio revoca su acceso a todos los activos. Quitar a un partner se hace en Settings → Partners. Si nadie tiene full control (ex-empleado, freelance desaparecido), existe un proceso de reclamación con ID, prueba de propiedad y carta firmada. **[OFFICIAL META]** ([S08-102], [S08-053], [S08-052])

## 1. Modelo de permisos (oct-2026)

### Nivel portfolio

| Rol actual | Antes | Puede | Riesgo si se compromete |
|---|---|---|---|
| **Full control** | Business admin | Todo: ajustes, personas, partners, activos, borrar el portfolio, asignarse opciones avanzadas; acceso automático a cualquier activo para completar una tarea | Máximo: puede echar a los dueños y gastar con cualquier método de pago |
| **Partial access – Basic** | Employee | Solo los activos asignados; ver quién tiene full control | Limitado a sus activos |
| **Partial access – Apps and integrations** | Developer | Configurar CAPI, monitorizar eventos, editar apps, **crear tokens de acceso** | Alto para datos y señales (los tokens persisten) |
| **Finance access (ver / gestionar)** | Finance analyst/editor | Transacciones, facturas, gasto, métodos de pago | Alto (pagos, líneas de crédito) |
| **Temporary access** | — | Basic durante 3-75 días con revocación automática | Bajo; ideal para freelancers y auditorías |

Fuente: [S08-044]. Desde sep-2026, los **perfiles de Threads** tienen permisos propios, separados de IG. **[OFFICIAL META]** ([S08-045])

### Nivel activo (tareas)

- **Página:** partial (contenido, actividad, mensajes, anuncios, insights, ingresos, creadores) / full / "full con acceso de partner". Solo full puede dar o quitar acceso y hacer "sensitive tasks".
- **Cuenta publicitaria:** partial (gestionar campañas, ver rendimiento, mockups) / full ("controlar ajustes, finanzas y permisos de la cuenta").
- **IG:** partial por tareas / full ("gestionar todo, incluido el método de pago para anuncios").
- **Datasets y píxeles:** partial (usar el dataset: ver datos, crear anuncios de conversión) / full (ajustes, eventos, accesos, crear audiencias).
- **Catálogo, WhatsApp, apps, custom conversions, offline event sets, block lists**: matrices propias.

Fuente: [S08-045]. **[OFFICIAL META]**

**Principio:** dar *partial access por tareas* siempre que sea posible. Full control de un activo solo a quien deba gestionar sus permisos. **[OFFICIAL META]** ("Giving people only the permissions they need… helps keep business portfolios… more secure.")

## 2. Propiedad de activos: quién debe ser dueño de qué

| Activo | Dueño recomendado | Acceso de la agencia/freelance | Por qué |
|---|---|---|---|
| Página de Facebook | Portfolio del negocio | Partner (partial: anuncios, contenido, mensajes según contrato) | La identidad del anunciante; si la agencia la posee, el cliente queda rehén |
| Cuenta de Instagram | Portfolio del negocio | Partner | Igual; además, Meta Verified va ligado al activo |
| Cuentas publicitarias | Portfolio del negocio (una o varias) | Partner con partial/full sobre la cuenta | Historial de pagos y cumplimiento = activo del cliente; separación por cliente obligatoria **[OFFICIAL META]** |
| Datasets/píxeles | Portfolio del negocio | Partner (usar dataset; full solo si la agencia implementa CAPI) | El historial de eventos es el activo de optimización más valioso; si se pierde la cuenta publicitaria, el dataset debe sobrevivir **[EMPIRICAL]** ([S08-092]) |
| Catálogos | Portfolio del negocio | Partner | Ídem |
| Dominio(s) | Portfolio del negocio (verificado) | — | Seguridad de dominio en peer approval; transparencia |
| Método de pago | Del negocio (tarjeta o cuenta a su nombre) | Ninguno; o línea de crédito de agencia solo si hay contrato y control | Pagos que no coinciden con el anunciante son señal de riesgo **[EMPIRICAL]**; las líneas de crédito compartidas son vector de abuso **[OFFICIAL META]** ([S08-046]) |
| WhatsApp Business Account | Portfolio del negocio | Partner | Número del negocio |
| Apps / system users / tokens | Portfolio del negocio (o de la agencia si es su herramienta, con acceso mínimo) | Apps and integrations | Los tokens no expiran con el offboarding de personas: revisar al cambiar de agencia |

**Agencias (best practice):**
1. La agencia tiene **su propio portfolio** con su equipo dentro.
2. El cliente añade a la agencia como **partner** y le comparte los activos con las tareas mínimas.
3. La agencia asigna a su personal esos activos desde su portfolio. Meta: "Si trabajas para un partner con partial access a un activo compartido, solo puedes asignar a tu gente las tareas que le asignaron a tu empresa". **[OFFICIAL META]** ([S08-044])
4. Nunca pedir al cliente "añádeme como persona con full control de tu portfolio" salvo necesidad puntual y temporal.

Ventajas:
- el offboarding se reduce a quitar al partner;
- los usuarios de la agencia no ven otros activos del cliente;
- las restricciones de un cliente no infectan por diseño los activos de otro. Matiz: Meta vincula activos asociados, así que el aislamiento no es total. **[STRONG INFERENCE]**

## 3. Capas de protección (de mayor a menor impacto)

1. **2FA para "Everyone"** en el portfolio (Settings → Business portfolio info → Two-factor authentication). Si Meta ya la ha hecho obligatoria, no se puede desactivar. Preferir **app de autenticación + códigos de recuperación guardados**. Con navegación privada o borrado de historial, pedirá código en cada login. **[OFFICIAL META]** ([S08-048], [S08-046])
2. **Passkeys** para todos los usuarios con full control. Meta puede exigirlas y retirar SMS o email como métodos una vez se usan con regularidad. No funcionan aún en las apps móviles de MBS ni de Ads Manager. **[OFFICIAL META]** ([S08-049])
3. **Dos personas activas con full control** (no más de ~10). Habilita la "second admin approval" para acciones sensibles: compartir líneas de crédito, cambiar accesos de otro full control. Cuidado: quitar a alguien puede requerir la aprobación del otro. **[OFFICIAL META]** ([S08-046], [S08-102])
4. **Peer approval** ([S08-050]):
   - *Ad account security:* default (solo sospechosos), **extra** (todos los anuncios, recomendado con partners o accesos temporales) o **custom** (por encima de un presupuesto). Los aprobadores deben haber estado activos en los últimos 90 días. Los anuncios publicados por un full control del portfolio no necesitan segunda revisión.
   - *Domain security:* lista de dominios de confianza. Cualquier anuncio a otra URL necesita aprobación (bloquea al atacante que redirige a su web de scam).
   - *Country restrictions:* países de confianza (no disponible para todos).
   - *Block CTX ads:* todos los click-to-Messenger/IG Direct/WhatsApp requieren aprobación. Los scams de inversión usan mucho este formato.
5. **Advanced Protection** en el portfolio. Obligatoria para Meta Verified for businesses y no desactivable con la suscripción activa. Meta no documenta públicamente todo lo que activa; incluye requisitos de inicio de sesión más estrictos. **[OFFICIAL META]** ([S08-059]) + **[HYPOTHESIS]** sobre el alcance
6. **Security Centre**, revisado mensualmente: inactivos, cuentas publicitarias sin uso, usuarios sin 2FA o passkey, emails públicos, malware detectado, líneas de crédito compartidas sospechosas. **[OFFICIAL META]** ([S08-046])
7. **Auditoría**: exportar los permisos de personas (último acceso, estado de 2FA) y descargar el *business history* (cambios de datos, activos y personas). **[OFFICIAL META]** ([S08-046])
8. **Account spending limit** en cada cuenta publicitaria, como freno de daños si alguien entra (no protege la cuenta, limita la pérdida). **[EMPIRICAL]** ([S08-085]) Ver [04](04-pagos-facturacion-limites.md).

## 4. Agentes de IA y automatización (relevante en 2026)

- **Vía oficial:** el MCP de Meta (beta abr-2026, abierto a developers el 16-jul-2026) y la CLI. Clientes soportados: ChatGPT, Claude, Claude Code, Perplexity. **[OFFICIAL META]** ([S08-082], [S08-009])
- **Controles:** MBS → Settings → Integrations → *Ads MCP server*, por cuenta publicitaria o catálogo. Se pueden bloquear acciones ("Create campaigns", "Edit or set budget") o limitar presupuestos (p. ej. bloquear presupuestos > USD 1.000). Los partners pueden fijar reglas para su propio personal. Según un changelog de vendor, algunas acciones de escritura venían permitidas por defecto. **Revisar y endurecer tras conectar.** **[OFFICIAL META]** + **[EMPIRICAL]** ([S08-010])
- **Postura oficial sobre baneos:** "It's safe to connect your ad account through Meta's ads MCP server, and it's unlikely that an account would be banned simply for using it… Using the ads MCP server on its own does not put your account at risk." **[OFFICIAL META]** ([S08-082])
- **Riesgos reales:**
  - automatización de navegador sobre Ads Manager (scraping/RPA);
  - herramientas no registradas con tokens personales;
  - bucles de reintentos que golpean los límites.

  Los límites de la API (4 cambios de presupuesto por ad set y hora; 10 cambios de spend cap al día) producen *throttling*, no baneos documentados. Account Integrity sí prohíbe cuentas usadas "por medios automatizados" fuera de "vías autorizadas". **[OFFICIAL META]** ([S08-083], [S08-070]) + **[STRONG INFERENCE]**

## 5. Amenazas 2025-2026 y cómo reconocerlas

| Ataque | Cómo funciona | Señal para reconocerlo | Defensa |
|---|---|---|---|
| **Solicitud de partner maliciosa** | El atacante crea un portfolio y envía una solicitud de partner. Si la apruebas, obtiene acceso persistente a Páginas, cuentas, píxeles y audiencias sin robar contraseña | Llega sin que tú o tu agencia la hayáis iniciado; nombre del negocio alarmista ("Account Restriction", "Ad Violations") o con una URL | Aprobar solo solicitudes esperadas y confirmadas por otro canal; revisar Partners mensualmente **[EMPIRICAL]** ([S08-085]) |
| **Email real de Meta con URL inyectada** | El nombre del negocio que solicita contiene una URL; la plantilla de Meta la inserta y el email pasa SPF/DKIM/DMARC | Texto raro, enlaces no clicables, invitaciones a "Agency Partner Program", "Meta Verified", monetización | No actuar desde el email: entrar a business.facebook.com y comprobar en BSH **[EMPIRICAL]** ([S08-084]) |
| **Falso aviso de suspensión** | Página clonada de "Meta Support" que pide credenciales y 2FA, o que ejecutes un "script de apelación" (PowerShell) que instala un infostealer (StealC) | Urgencia, cuenta atrás, dominio ajeno a Meta, peticiones de ID o códigos | Verificar en BSH; Meta nunca pide contraseñas ni códigos **[OFFICIAL META]** ([S08-051]) + **[EMPIRICAL]** |
| **Infostealers / robo de cookies** | Malware (DuckTail, NodeStealer…) roba la sesión del navegador y salta la 2FA | Logins desde ubicaciones desconocidas; nuevas personas o partners; anuncios que no reconoces | Dispositivos limpios y dedicados para Business Suite; no abrir ejecutables "de briefing" o ".zip de creatividades"; Security Centre detecta "users with possible malware" **[OFFICIAL META]** + **[EMPIRICAL]** ([S08-087]) |
| **Phishing masivo de marca Meta** | Miles de URLs que suplantan avisos de Meta ("Meta Mirage", 14.000+ URLs en 2025) | Dominios no oficiales | Formación del equipo; reportar a phish@fb.com **[EMPIRICAL]** ([S08-086]) |
| **Abuso del soporte IA** | Atacantes que manipulan bots de soporte para hacerse con cuentas (casos reportados en 2026) | — | Passkeys y videoselfie de recuperación preconfigurados; no depender de SMS **[EMPIRICAL — prensa]** ([S08-077]) |
| **Falsos "recuperadores de cuentas"** | Servicios que prometen desbanear y piden acceso full o credenciales | Piden credenciales o acceso total | No dar acceso; como mucho temporal y basic, nunca contraseñas **[STRONG INFERENCE]** |

## 6. Playbook: cuenta o portfolio hackeado

1. **Contener:**
   - cambiar la contraseña de Facebook y del email asociado;
   - cerrar todas las sesiones activas;
   - restablecer la 2FA si se compartió un código o se siguió una "guía".
2. **Expulsar:** en Settings, quitar **People** y **Partners** desconocidos y comprobar que conservas full control. Revisar **apps y tokens**.
3. **Frenar el gasto:**
   - pausar campañas desconocidas;
   - fijar un account spending limit bajo;
   - retirar el método de pago si es necesario;
   - avisar al banco y disputar los cargos fraudulentos. Ojo: disputar cargos legítimos puede generar restricciones de pago.
4. **Reportar:**
   - flujo de hackeo de Meta ("Secure your account", Business Support Home → actividad no reconocida);
   - si Meta detectó la intrusión, puede que ya haya quitado admins, pausado anuncios o cambiado métodos de pago. **[OFFICIAL META]** ([S08-023], [S08-118])
5. **Recuperar el control si te echaron:**
   - si queda otra persona con full control, que te vuelva a añadir;
   - si no, "Submit a request to get full control" con (a) ID, (b) prueba de propiedad (escrituras, licencia, factura de servicios, extracto bancario, o tres importes de facturas de la cuenta publicitaria + últimos 4 dígitos y caducidad de la tarjeta) y (c) carta firmada. **[OFFICIAL META]** ([S08-052])
6. **Después:**
   - activar peer approval (extra + dominios de confianza);
   - passkeys;
   - revisar la Ad Library por si se publicaron anuncios scam con tu marca;
   - en la UE, valorar obligaciones de notificación si hubo datos de clientes expuestos (asesoría legal / RGPD).

## 7. Offboarding de empleados, freelancers y agencias

**Empleado o freelance que se va:**
- [ ] Quitarlo de **People** del portfolio (revoca todos los activos). **[OFFICIAL META]**
- [ ] Revisar si tenía **full control directo sobre activos fuera del portfolio** (Páginas o IG antiguos, cuentas publicitarias personales con el método de pago de la empresa).
- [ ] Revisar los **tokens/system users/apps** creados por él (rol Apps and integrations).
- [ ] Si tenía **Finance access**, revisar métodos de pago y líneas de crédito.
- [ ] Rotar los accesos compartidos fuera de Meta (email del dominio usado para verificaciones, gestor de contraseñas, dominio/DNS).
- [ ] Revisar las reglas del MCP y los agentes conectados con su usuario.
- [ ] Para próximos freelancers, usar **acceso temporal** (3-75 días).

**Agencia que se va (lado cliente):**
- [ ] Settings → **Partners** → quitar a la agencia. **[OFFICIAL META]** ([S08-053])
- [ ] Confirmar que todos los activos son **propiedad** del portfolio del cliente (no "compartidos por" la agencia). Si la cuenta publicitaria era de la agencia, el historial se queda con ella: negociarlo contractualmente desde el inicio.
- [ ] Cambiar o retirar la línea de crédito o el método de pago de la agencia si la había.
- [ ] Revisar datasets: quién es dueño y quién tiene full.
- [ ] Descargar el business history como evidencia.

**Agencia que deja a un cliente (lado agencia):**
- [ ] Quitar al personal de la agencia de los activos del cliente y retirarse como partner.
- [ ] Devolver la propiedad de cualquier activo que la agencia hubiera creado en nombre del cliente.
- [ ] Desconectar herramientas y agentes de esas cuentas.

## 8. Checklist de seguridad (auditoría mensual, 15 minutos)

- [ ] 2FA requerida para "Everyone"; nadie sin 2FA o passkey.
- [ ] Entre 2 y 10 personas con full control, todas activas, con email corporativo.
- [ ] Cero usuarios inactivos de más de 90 días.
- [ ] Partners: todos reconocidos y con contrato vigente.
- [ ] Peer approval: "extra" en cuentas con partners o temporales; dominios de confianza configurados.
- [ ] Cuentas publicitarias sin uso de más de 12 meses → desactivadas (no se pueden borrar).
- [ ] Métodos de pago a nombre del anunciante; backup configurado; spending limit en cuentas de riesgo.
- [ ] Reglas del MCP revisadas (acciones bloqueadas y topes de presupuesto).
- [ ] Business history sin cambios inesperados.
- [ ] Ad Library: buscar la marca o el nombre del formador para detectar suplantaciones.
- [ ] Dispositivos usados para Business Suite con antimalware y sin extensiones dudosas.

## Implicaciones operativas

- En el onboarding de un cliente nuevo de alto riesgo (infoproductos), **no lanzar campañas hasta tener**:
  - 2FA para todos;
  - 2 full control del lado del cliente;
  - la agencia como partner;
  - peer approval con dominios de confianza;
  - business verification iniciada.

  El coste es 1-2 horas; el beneficio, evitar el escenario más caro (hackeo + anuncios scam con la marca del cliente + restricción por "asociación").
- **Separar identidades:** que el perfil personal del formador o fundador (expuesto a phishing y a reportes) no sea el único admin de las cuentas publicitarias. Si ese perfil se restringe, la cuenta cae con él. **[OFFICIAL META]** ([S08-022])

## Errores frecuentes

- La agencia crea las cuentas publicitarias en su propio portfolio "por comodidad". El cliente pierde historial y control y queda atado a la agencia.
- Un único admin (normalmente el freelance o el fundador).
- Aprobar solicitudes de partner que "vienen de Meta".
- Compartir la contraseña de Facebook del fundador con el equipo, en lugar de dar acceso por roles (además es contrario a los términos de uso).
- No revisar tokens y apps al cambiar de proveedor.
- Conectar agentes de IA con permisos totales sin reglas de presupuesto.

## Preguntas abiertas

- Alcance exacto de "Advanced Protection" para portfolios (no documentado públicamente en detalle).
- Criterios que convierten la 2FA en obligatoria para un portfolio de más de 90 días ("certain business portfolios").
- Si las reglas del MCP se pueden aplicar a todo el portfolio de golpe (un vendor menciona reglas en bloque vía Marketing API desde sep-2026; no verificado).

## Fuentes clave

- [About business portfolio and business asset permissions](https://www.facebook.com/business/help/442345745885606) — Meta — meta-oficial
- [Business portfolio assets and their task-based access settings](https://www.facebook.com/business/help/1242256693745272) — Meta — meta-oficial
- [Best practices for making a business portfolio more secure](https://www.facebook.com/business/help/608572510632070) — Meta — meta-oficial
- [How to require two-factor authentication](https://www.facebook.com/business/help/280940009201586) / [About 2FA for your business portfolio](https://www.facebook.com/business/help/865384580786591) — Meta — meta-oficial
- [About passkey setup for your business portfolio](https://www.facebook.com/business/help/910360017835904) — Meta — meta-oficial
- [Add another review of your ads with peer approval](https://www.facebook.com/business/help/529947753306370) — Meta — meta-oficial
- [Verify if a Meta representative contact is real](https://www.facebook.com/business/help/372703956148310) — Meta — meta-oficial
- [Submit a request to get full control of a business portfolio](https://www.facebook.com/business/help/474856681929983) — Meta — meta-oficial
- [Remove partners](https://www.facebook.com/business/help/2222659621282858) / [Remove people](https://www.facebook.com/business/help/353397428740939) — Meta — meta-oficial
- [Manage ads from an AI agent with Meta ads AI connectors](https://www.facebook.com/business/help/1456422242197840) — Meta, 2026 — meta-oficial
- [Meta Phishers Abuse Business Account Manager Service](https://www.huntress.com/blog/meta-business-manager-phishing) — Huntress, 2026-07-07 — vendor seguridad
- [Facebook Ad Account Phishing: The Email Really Is From Meta](https://www.alwaysbeyond.com/blog/facebook-ad-account-phishing) — Always Beyond, 2026-07-15 — vendor seguridad
- [CTM360 Identifies Surge in Phishing Attacks Targeting Meta Business Users](https://thehackernews.com/2025/05/ctm360-identifies-surge-in-phishing.html) — 2025-05 — prensa
