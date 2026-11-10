---
name: configurar-meta
description: "Te guía, en conversación y paso a paso, para dejar Meta listo según tu situación: empezar de cero, cuenta sin señal, cuenta heredada o agencia entrando en la cuenta de un cliente como partner. Portfolio, accesos, pago, Página e Instagram, dominio, dataset y los dos topes del lado de Meta, verificando con el MCP."
argument-hint: "<cliente> [cero|sin-senal|heredada|agencia]"
---

# /configurar-meta

Entrada: `$ARGUMENTS` (cliente y, opcionalmente, situación).

**Se ejecuta en el hilo principal**: el usuario hace los pasos en Meta mientras hablas con él. No la delegues en un
subagente. En Meta esta skill **solo lee**: portfolios, cuentas y ajustes los crea el usuario en la interfaz de Meta
(el MCP no crea portfolios ni cuentas). Tú explicas, verificas con el MCP y llevas la cuenta de lo hecho.

Marcos: `meta-ads-kb/13-sistema-operativo/08-cuenta-nueva-y-heredada.md`, `meta-ads-kb/02-estructura-campanas/04-business-portfolio-activos-estructura-cuenta.md`,
`meta-ads-kb/02-estructura-campanas/10-cuenta-nueva-vs-heredada.md`, `meta-ads-kb/08-cuenta-politicas-seguridad/02-verificaciones.md`,
`meta-ads-kb/08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md` y
`meta-ads-kb/08-cuenta-politicas-seguridad/04-pagos-facturacion-limites.md`.

## 0. Situar
1. Ficha del cliente; si no existe → `/cliente-nuevo`.
2. Si no te dan la situación, decídela con dos preguntas y lecturas del MCP (`ads_get_ad_accounts`; gasto de los
   últimos 90 días con `ads_get_ad_entities`; `ads_get_datasets` y `ads_get_dataset_stats`):
   - sin portfolio o sin cuenta publicitaria → **cero**;
   - cuenta sin dataset o con el dataset sin eventos → **sin-senal**;
   - cuenta con historial o montada por otros → **heredada**;
   - eres agencia y los activos son del cliente → **agencia** (se combina con cualquiera de las otras).
3. Crea `clientes/<slug>/planes/AAAA-MM-DD_configuracion-meta.md` con la checklist de su situación (estado de cada
   punto: hecho, pendiente o no aplica) y ve actualizándola.
4. Un paso cada vez: qué es y por qué (al nivel del usuario), dónde se hace (ruta de menús), confirmación de que está
   hecho y verificación si se puede.

## Situaciones

### cero (`08-cuenta-nueva-y-heredada.md` §A.1)
1. Business Portfolio a nombre del negocio (no de una persona ni de la agencia).
2. Seguridad: 2FA para todos, dos personas con control total (no más de diez) y passkeys si están disponibles
   (`08-…/03-…` §3).
3. Página de Facebook y cuenta profesional de Instagram dentro del portfolio y conectadas.
4. Cuenta publicitaria con el país, la moneda y la zona horaria de la ficha. Elígelos bien antes de crearla: son la
   base de todos los informes, y cambiarlos después no es trivial (comprueba el procedimiento vigente en el Help Center
   antes de dar nada por hecho).
5. Método de pago a nombre del negocio y uno de respaldo. Explica el límite diario inicial que pone Meta y cómo sube
   (`08-…/04-…` §2–3).
6. Verificación del negocio y del dominio (`08-…/02-verificaciones.md`). Productos financieros en España: verificación
   obligatoria.
7. Un dataset para la web en Events Manager. Si ya existe uno con historial, se reutiliza: nunca «píxel nuevo para
   empezar limpio» (mito M58). Instalar píxel y CAPI → `/implementar-capi`.
8. Landing conforme a políticas → `/landing` (si aún no existe, `/construir-landing`).

### sin-senal
1. Cuenta activa y con pago (`ads_get_ad_accounts`).
2. Diagnóstico del dataset con `especialista-tracking` en solo lectura: `ads_get_datasets`, `ads_get_dataset_details`,
   `ads_get_dataset_stats` (eventos por origen, navegador y servidor) y `ads_get_dataset_quality` (calidad de
   coincidencia y deduplicación).
3. Dominio verificado y `meta.dataset` en la ficha.
4. Construir la señal → `/implementar-capi <slug>`.

### heredada (`08-cuenta-nueva-y-heredada.md` §B)
1. **Día 1–2, accesos y riesgo**: quién es dueño de cada activo (deben ser del cliente); personas y partners con
   acceso (los que sobren los quita el usuario en Business Settings; tú solo lo recomiendas); dos personas con control
   total y 2FA; Account Quality (restricciones y rechazos: si hay restricción → `/rescate-cuenta`); pagos, límites y
   location fees.
2. **Semana 1, auditar sin tocar** → `/auditoria <slug>`. La tabla de deuda técnica 2025–2026 de §B.2 es la checklist.
3. **Conservar**: dataset, anuncios con prueba social (post IDs) y audiencias de clientes. Nada de cuenta nueva
   «limpia» (`[HYPOTHESIS]` sin evidencia; §B.3).

### agencia (`08-…/03-…` §2, «Agencias»; `14-playbooks/playbook-agencias-consultores.md` parte B)
1. La agencia tiene su propio portfolio con su equipo dentro.
2. Petición al cliente, redactada por `gestor-cliente` en `clientes/<slug>/planes/AAAA-MM-DD_peticion-accesos.md`:
   que añada a la agencia como **partner** con el ID de su portfolio (Business Settings → Partners) y comparta, con
   las tareas mínimas, la cuenta publicitaria (gestionar campañas), el dataset (usarlo; control total solo si vas a
   implementar CAPI), la Página, Instagram y el catálogo si lo hay. Nunca pedir «añádeme como persona con control total
   de tu portfolio»; para algo puntual existe el acceso temporal (3–75 días).
3. En el portfolio de la agencia, asigna esos activos a tu equipo (y a tu usuario del sistema si usas
   `/conectar meta --avanzado`).
4. Autentica el MCP con el usuario de la agencia (`/conectar meta`) y comprueba que `ads_get_ad_accounts` lista la
   cuenta del cliente.
5. Recomienda al cliente la aprobación por pares «extra» cuando trabaja con partners (`08-…/03-…` §3).
6. Reglas del Ads MCP server: las pone el control total del cliente en su cuenta; la agencia puede fijar reglas para su
   propio equipo (`08-…/03-…` §4). Acordadlas.
7. Contrato y reporting: KPI por coste por cita o por venta, no por CPL, y cláusula de SLA de contacto
   (`playbook-agencias-consultores.md` §6).

## Siempre: los dos topes del lado de Meta y los de la ficha
1. **Topes en la ficha**: `topes.cambio_dia` y `topes.total_dia` con cifras que dé el usuario. El hook `meta_guard`
   bloquea cualquier presupuesto por encima de `cambio_dia`; con 0 no deja crear ni subir presupuesto. Marca `F0.topes`.
2. **Límite de gasto de la cuenta** (*account spending limit*, en la configuración de pagos de la cuenta): tope
   acumulado de toda la cuenta que se reinicia a mano (`08-…/04-…` §2). Sugiere el presupuesto mensual más un 10–20 %
   de margen `[HYPOTHESIS]` y revisarlo cada mes. Limita el daño si alguien entra sin permiso (`08-…/03-…` §3).
3. **Regla del Ads MCP server**: Business Settings → Integrations → Ads MCP server → la cuenta → «Budgets set above
   this amount → Blocked» con el importe de `topes.cambio_dia`, y bloquear las acciones que no se usen. No está
   verificado si la regla mira el presupuesto diario o el total de la campaña o del conjunto: que lo compruebe en el
   texto de ayuda de la pantalla y, si es el total, ponga una cifra acorde. Las escrituras vienen permitidas por
   defecto según lo observado `[EMPIRICAL]`.
4. Apunta las tres cosas en la sección «Reglas del Ads MCP server» de la ficha. Si `ads_get_ad_accounts` devuelve el
   límite de gasto, compruébalo; si no, vale la confirmación del usuario.
5. **Mejoras automáticas**: confirma `mejoras_automaticas: off` y la tabla de la ficha (por qué:
   `00-ESTADO-ACTUAL-2026.md` §0 punto 7; `03-creatividad/14-herramientas-ia-creativa-meta.md`).
6. Si se van a leer informes por la API, activar *Additional breakdowns* (`13-sistema-operativo/03-framework-lanzamiento.md`, Fase 2).
7. **Reglas automáticas** (la protección que actúa de noche): cuando la cuenta ya gaste, `/reglas-automaticas <cliente>`
   monta la pausa por gasto fuera de tope y las alertas (las pausas por conversión, en modo sombra). No sustituye al
   límite de gasto de la cuenta del punto 2. Marca `F5.reglas` esa skill, no esta.

## Revisión de ajustes que Meta cambió en 2026 (`00-ESTADO-ACTUAL-2026.md`)
1. **Medición en el dispositivo** del píxel (*Measure conversions on customer devices*, Events Manager → el dataset →
   Settings): activada por defecto desde el 2026-11-12 y sin efecto para personas de la UE y el Reino Unido. Pregunta
   si se quiere; si se deja activada en mercados fuera de la UE, avisa de que hay que re-baselinar los KPI desde esa
   fecha. El detalle técnico lo lleva `/implementar-capi`.
2. **Detected offers** (Commerce Manager → Settings → Offer merchandising): revisa que Meta no muestre ofertas que el
   negocio no da.
3. **Navegación por productos y product showcase**: sin catálogo, en OFF (Meta activó la navegación en anuncios
   existentes hacia el 2026-10-28).
4. **Ubicaciones**: las exclusiones manuales a nivel de conjunto ya no existen en Ventas, Clientes potenciales y App;
   siguen en Engagement, Awareness y Traffic. Si una política de marca exige excluir ubicaciones, acuérdalo antes de
   elegir objetivo.

## Estado y cierre
- Marca en `estado.md` solo lo verificado: `F1.portfolio` (usuario), `F1.cuenta` (mcp: cuenta activa con pago),
  `F1.activos` (mcp: Página e Instagram), `F1.dominio` (usuario), `F1.reglas-mcp` (usuario). El dataset y la
  deduplicación los marca `/implementar-capi`.
- Completa en la ficha los IDs que falten (`meta.cuenta`, `meta.pagina`, `meta.instagram`, `meta.dataset`).
- Resumen: hecho, pendiente (con quién lo hace) y siguiente skill (`/implementar-capi`; para el destino, `/landing`
  si ya hay web, `/construir-landing` si hay que hacerla o `/formulario-instantaneo` si el lead se capta en Meta).

## Nunca
Crear cuentas o Páginas nuevas para esquivar una restricción, comprar o alquilar cuentas, ni abrir varias cuentas
publicitarias «para diversificar subastas» (`08-cuenta-nueva-y-heredada.md` §A.3). Es circunvención y puede tumbar
todos los activos del negocio.
