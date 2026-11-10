# Business portfolio, activos y estructura de cuenta (de la organización al anuncio)

> Última verificación: 2026-10-15 · Autor: A02 (agente) · Ámbito: Business portfolio (antes Business Manager), ad accounts, datasets/pixels, Páginas, cuentas de Instagram, catálogos, dominios, usuarios, partners, permisos, facturación; cuándo usar varias cuentas publicitarias; jerarquía Campaign → Ad set → Ad y qué decisión vive en cada nivel. Seguridad, restricciones y políticas: área 08. Tracking/datasets a fondo: área 04.

## TL;DR

- **Nomenclatura actual**: *Business portfolio* (antes Business Manager / "business account"), gestionado desde **Meta Business Suite**; permisos "Full access" (antes "full control/admin") y "Partial access" → "Basic" (antes "employee") y "Apps and integrations" (antes "developer"); "Finance access" como opción avanzada. **[OFFICIAL META]** ([HC 442345745885606](https://www.facebook.com/business/help/442345745885606))
- **Un portfolio agrupa**: Páginas, cuentas de Instagram y Threads, ad accounts, catálogos, datasets (pixel + CAPI + app + offline), apps, cuentas de WhatsApp, dominios, partners, system users. Se necesita portfolio para Business Suite, facturación mensual, anuncios políticos, verificar dominio y block lists. **[OFFICIAL META]** ([HC 486932075688253](https://www.facebook.com/business/help/486932075688253))
- **Límites oficiales**: una persona puede gestionar hasta **25 ad accounts**; una ad account puede asignarse a hasta **25 personas**; un portfolio empieza con límite de creación de **1 ad account hasta un pago confirmado**; las cuentas cerradas siguen contando. **[OFFICIAL META]** ([HC 1026272311098874](https://www.facebook.com/business/help/1026272311098874))
- **Límite de anuncios por Página (no por cuenta)**: 250 / 1.000 / 5.000 / 20.000 anuncios activos o en revisión según el gasto del mes de mayor inversión (<100k $, <1M $, <10M $, ≥10M $). Varias ad accounts que anuncian la misma Página comparten el límite. **[OFFICIAL META]** ([HC 766697140509126](https://www.facebook.com/business/help/766697140509126))
- **Separar en varias ad accounts NO evita competir contra uno mismo**: "Running ads from separate ad accounts may not help you avoid overlap… the ad delivery system may identify multiple accounts as belonging to the same advertiser". Y crear más Páginas para saltarse límites "might hurt your own performance" porque "the delivery system uses learnings from your Page". **[OFFICIAL META]** ([HC 537699989762051](https://www.facebook.com/business/help/537699989762051), [HC 766697140509126](https://www.facebook.com/business/help/766697140509126))
- **Regla de diseño**: *una marca/mercado = un portfolio propietario, una ad account principal, un dataset por web/app, una Página + IG por marca*; añadir cuentas solo por razones legales, de facturación/moneda/zona horaria, de entidad jurídica, de categoría especial o de gestión de riesgo — no por "estructura". **[STRONG INFERENCE]**
- **Controles a nivel de cuenta (Advertising settings)**: ubicaciones permitidas, edad mínima, exclusiones de marca/empleados, exclusiones de placements (Audience Network, Marketplace, right column…), audience segments, value rules. Se aplican a todas las campañas y **no apagan Advantage+**. Es la forma 2026 de imponer restricciones de negocio. **[OFFICIAL META]** ([HC 1438478636941047](https://www.facebook.com/business/help/1438478636941047))
- **Dentro de la cuenta: consolidar es el default** (Meta, Loomer, CTC, Foxwell). Se separa campaña/ad set solo para resolver un problema demostrado: objetivo de negocio distinto, economía distinta (país/producto/margen), restricción legal, necesidad de control presupuestario o test controlado. **[OFFICIAL META]** + **[EMPIRICAL]**

---

## 1. Nomenclatura y renombres (2023-2026)

| Hoy (2026) | Antes | Nota |
|---|---|---|
| Business portfolio | Business Manager / Business account | Renombre progresivo (≈2023-2024; fuentes secundarias discrepan en la fecha exacta). URLs `business.facebook.com` se mantienen. **[STRONG INFERENCE]** sobre la fecha |
| Meta Business Suite (configuración: "Settings") | Business Settings / Business Manager settings | |
| Full access | Admin / full control | **[OFFICIAL META]** |
| Basic access (partial) | Employee | **[OFFICIAL META]** |
| Apps and integrations | Developer | **[OFFICIAL META]** |
| Finance access (view/manage) | Finance analyst/editor | **[OFFICIAL META]** |
| Dataset (en Events Manager) | Pixel / offline event set / app events | El dataset unifica fuentes web, app, offline y CRM. **[OFFICIAL META]** (Events Manager, área 04) |
| Advantage+ campaign budget / "Campaign budget" / "Budget with Advantage+ on" | CBO → Advantage campaign budget | **[OFFICIAL META]** |
| Advantage+ placements | Automatic placements | **[OFFICIAL META]** |
| Advantage+ sales campaigns | Advantage+ shopping campaigns (ASC) | Ver archivo 08 |
| Cost per result goal | Cost cap | **[OFFICIAL META]** |
| ROAS goal | Minimum ROAS | **[OFFICIAL META]** |
| Highest volume / Highest value | Lowest cost | **[OFFICIAL META]** |

## 2. Los activos y qué decide cada uno

| Activo | Para qué importa en rendimiento | Recomendación por defecto |
|---|---|---|
| **Business portfolio** | Propiedad de activos, permisos, facturación, verificación, partners | El cliente/marca es *propietario*; agencias acceden como *partner*. Nunca construir los activos del cliente dentro del portfolio de la agencia |
| **Ad account** | Moneda, zona horaria, método de pago, límites de gasto, historial de entrega y calidad, controles de cuenta, audience segments, value rules | Una principal por marca/mercado con moneda/zona horaria correctas (no se pueden cambiar después sin crear otra cuenta — **[STRONG INFERENCE]**, área 08 para detalle) |
| **Dataset (pixel + CAPI + app + offline/CRM)** | Señal de optimización, audiencias, atribución | Uno por dominio/negocio, compartido a las ad accounts que lo usen; evitar varios pixels en la misma web |
| **Página de Facebook + cuenta de Instagram** | Identidad del anuncio, límite de anuncios por Página, prueba social, "learnings from your Page" | Una por marca; no multiplicar Páginas para esquivar límites |
| **Catálogo** | Advantage+ catalog ads, product sets, audiencias de catálogo | Uno por tienda/mercado; feeds por país/idioma dentro del mismo catálogo cuando sea posible ([HC 2720085414702598](https://www.facebook.com/business/help/2720085414702598)) |
| **Dominio verificado** | Control de quién edita link previews/anuncios con tu dominio | Verificar (gratuito; meta tag, HTML o DNS TXT). Desde la evolución de AEM (2023) ya no es requisito para optimizar conversiones web, pero sigue siendo recomendable. **[OFFICIAL META]** ([HC 286768115176155](https://www.facebook.com/business/help/286768115176155)) + **[EMPIRICAL]** (Loomer/Adviso sobre AEM) |
| **Partners** | Acceso de agencias/consultores a activos | Compartir activos concretos con permisos por tarea ([HC 695463587559330](https://www.facebook.com/business/help/695463587559330)) |
| **System users** | Integraciones API (CAPI, herramientas, agentes IA) | Un system user por tipo de acceso; admin system user solo para administración; tokens custodiados ([HC 327596604689624](https://www.facebook.com/business/help/327596604689624)) |
| **Usuarios** | Riesgo de seguridad, trazabilidad | Mínimo privilegio; acceso temporal (3-75 días) para colaboradores puntuales. **[OFFICIAL META]** |

### Permisos (resumen oficial)
- **Full access**: gestiona todo (ajustes, personas, activos, partners), puede borrar el portfolio. **Partial/Basic**: solo activos asignados. **Apps and integrations**: CAPI, eventos, apps, tokens. **Finance access**: ver o gestionar facturación. **Temporary access**: basic, 3-75 días, revocación automática. **[OFFICIAL META]** ([HC 442345745885606](https://www.facebook.com/business/help/442345745885606))
- A nivel de activo: full o partial (tareas: contenido, anuncios, mensajes…). **[OFFICIAL META]**

### Límites de gasto que condicionan la estructura
- **Daily spending limit fijado por Meta** para la mayoría de cuentas, que sube automáticamente con historial, cumplimiento de políticas y gasto cerca del límite; puede reajustarse con portfolio/cuenta/Página nuevos o calidad baja; no aplica con facturación mensual. **[OFFICIAL META]** ([HC 563129151097553](https://www.facebook.com/business/help/563129151097553)). Implicación: una cuenta nueva **no puede** arrancar a 5.000 €/día aunque quieras (ver archivo 10).
- **Account spending limit** (lo pones tú) y **campaign spending limit**: frenos de seguridad, no herramientas de optimización.

### Meta One (sept 2026)
- Meta anunció planes de suscripción por Página/perfil/número de WhatsApp (Essential 14,99 $ ≈ Meta Verified; Advanced 49,99 $ con 1 caso de soporte/mes; Expert 149 $ con 5; Max 499 $ ilimitado) y límites a compartir enlaces orgánicos. No afectan a la mecánica de las ad accounts, pero sí al **acceso a soporte humano**, relevante para cuentas con riesgo de restricciones. **[EMPIRICAL]** ([Loomer, 2026-09-22](https://www.jonloomer.com/meta-one-business-plans/))

## 3. ¿Cuándo usar varias ad accounts?

Primero, los costes de separar (**[OFFICIAL META]** salvo indicación):
1. **No elimina el auction overlap**: el sistema puede identificar que varias cuentas son el mismo anunciante.
2. **Comparten el límite de anuncios por Página** si usan la misma Página.
3. **Fragmentan señal y gestión**: audience segments, value rules, controles de cuenta, opportunity score, reglas automáticas y reporting son por cuenta.
4. **Cuenta nueva = límite de gasto bajo + sin historial** (ver archivo 10).

Razones legítimas para separar **[STRONG INFERENCE]** (con apoyo de práctica de agencias):

| Razón | ¿Separar cuenta? | Comentario |
|---|---|---|
| Entidad jurídica / facturación distinta | Sí | Factura y método de pago por entidad |
| Moneda o zona horaria distinta (p. ej. EUR vs USD; reporting por día local) | Sí, si importa contable/operativamente | Moneda y zona horaria se fijan al crear la cuenta |
| Marcas distintas con Páginas, webs y públicos distintos | Sí (y a menudo portfolios distintos) | Cada marca con su dataset y Página |
| Special ad categories (crédito, empleo, vivienda) o verticales sensibles junto a negocio normal | Recomendable | Aísla restricciones y revisiones; controles de cuenta no aplican a SAC ([HC 1438478636941047](https://www.facebook.com/business/help/1438478636941047)) |
| Agencia que gestiona clientes | Cuenta del cliente en el portfolio del cliente | La agencia como partner |
| Gestión de riesgo (cuenta de respaldo ante restricciones) | **[CONTESTED]** | Útil como continuidad de negocio; peligroso si se usa para eludir políticas (área 08). No aporta rendimiento |
| "Para ganar otras subastas" / "diversificar" | No | Meta indica lo contrario (overlap entre cuentas) |
| Separar prospecting y retargeting, o tests | No | Se hace con campañas/ad sets, no con cuentas |
| Límite de 25 personas por cuenta o de 5.000 ad sets no borrados | Rara vez | Archivar/borrar antes de crear cuentas |

## 4. Jerarquía Campaign → Ad set → Ad: qué vive en cada nivel (2026)

| Nivel | Decisiones que viven aquí | Consecuencia estructural |
|---|---|---|
| **Campaña** | Objetivo; Advantage+ on/off (estado derivado de budget/audience/placements); tipo de presupuesto (Advantage+ campaign budget vs ad set budget); bid strategy cuando hay campaign budget; special ad category; A/B test | Con campaign budget, el presupuesto se reparte en tiempo real entre ad sets y se evalúa a nivel de campaña ([HC 153514848493595](https://www.facebook.com/business/help/153514848493595)) |
| **Ad set** | Conversion location; performance goal y evento; atribución; conversion count; presupuesto (si ABO) y spending limits (si CBO); calendario; audiencia (controles/sugerencias); Customer lifecycle strategy; value rules; placements; Advantage+ catalog/product set | Es la unidad de learning. Cada ad set necesita su propio volumen de eventos |
| **Ad** | Creatividad (imagen/vídeo/carrusel/flexible/catálogo), textos múltiples, destino, Advantage+ creative enhancements, URL params, identidad (Página/IG), partnership ads | Límite API: 50 anuncios no archivados por ad set ([Marketing API](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign)); Meta recomienda menos anuncios con más assets por anuncio ([HC 2720085414702598](https://www.facebook.com/business/help/2720085414702598)) |

Límites técnicos útiles **[OFFICIAL META]**:
- Advantage+ campaign budget: mejor ≤70 ad sets por campaña (por encima no se puede apagar campaign budget ni cambiar bid strategy tras publicar); máximo 200 ad sets incluyendo inactivos ([HC 519856662172206](https://www.facebook.com/business/help/519856662172206)).
- 5.000 ad sets no borrados por ad account regular (10.000 en cuentas "bulk") ([Marketing API reference](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign)).
- Hasta 500 custom audiences por ad account ([HC 744354708981227](https://www.facebook.com/business/help/744354708981227)).
- Hasta 10 creative assets por anuncio en formatos multi-asset; Loomer cita hasta 30 en flexible format y 5 textos/5 titulares. **[OFFICIAL META]** / **[EMPIRICAL]**
- **[CONTESTED]**: CTC (jul 2026) habla de "150 ads per ad set" como límite actual; la referencia de API sigue diciendo 50. El "150" coincide con las "150 creative combinations" del ASC legacy. No verificado; asumir 50.

## 5. Consolidar vs separar dentro de la cuenta

Meta, en varias páginas oficiales: combinar ad sets "will help you get the conversions you need to exit learning phase sooner"; usar breakdowns en vez de ad sets para reporting por audiencia; juntar geos pequeñas; usar Advantage+ placements + asset customization en vez de ad sets por placement; varios idiomas en un ad set; menos anuncios con más assets. **[OFFICIAL META]** ([HC 2720085414702598](https://www.facebook.com/business/help/2720085414702598), [HC 2419480091640105](https://www.facebook.com/business/help/2419480091640105))

Opportunity score puntúa explícitamente "audience fragmentation" (ejemplo oficial: +35 puntos por resolver fragmentación vs +5 por Advantage+ placements). Ojo: el score mide adopción de recomendaciones, **no rendimiento**; Meta dice que no hay que apagar campañas por score bajo. **[OFFICIAL META]** ([HC 804913634782260](https://www.facebook.com/business/help/804913634782260))

### Criterios para separar (campaña o ad set)

| Separa si… | Nivel | Por qué |
|---|---|---|
| Objetivos de negocio distintos (ventas vs leads; dos productos con P&L separados) | Campaña | Eventos distintos; presupuestos que la dirección quiere fijar |
| Economía distinta por país (CPA objetivo, precio, margen, idioma) | Campaña o ad set (con spending limits) | El sistema optimiza volumen, no tu margen por país; alternativa: value rules por ubicación |
| Restricción legal o de política (edad, SAC, países) | Campaña o controles de cuenta | Controles de cuenta no apagan Advantage+ |
| Necesidad de garantizar inversión en un segmento (mercado nuevo, remarketing de gama alta, lanzamiento) | Ad set con min spend o campaña aparte | Meta lo documenta con el ejemplo California/Nueva York y min spend limits ([HC 454681230514942](https://www.facebook.com/business/help/454681230514942)) |
| Distinta bid strategy / cost control | Campaña (o ABO) | Meta recomienda ad set budgets para "mixed optimization goals or bid strategies" |
| Test controlado (A/B, lift) | Campaña/ad sets de test | Sólo con potencia estadística suficiente |
| Eventos de calendario (rebajas, lanzamientos) | Campaña "moment" | Patrón CTC: evergreen + marketing moments |

### NO separes por…
- Intereses/lookalikes distintos con el mismo objetivo (con Advantage+ audience son sugerencias; los ad sets acaban llegando a la misma gente). **[EMPIRICAL]** ([Loomer, 2026-06-23](https://www.jonloomer.com/active-ad-sets-meta-ads-campaign/))
- Edad/género "para ver qué funciona" (usa breakdowns). **[OFFICIAL META]**
- Placements (usa asset customization). **[OFFICIAL META]**
- "Testing" de creatividades con presupuestos minúsculos (usa el creative testing tool dentro del ad set o tests con potencia). **[EMPIRICAL]**

## Implicaciones operativas

- **Checklist de auditoría de estructura de cuenta**: propietario real de activos; nº de personas con full access (mínimo 2 del cliente, no más de lo necesario); system users para CAPI/herramientas; dataset único por dominio y compartido correctamente; dominio verificado; moneda/zona horaria; controles de cuenta (edad mínima, países, placements) acordes a restricciones reales; audience segments definidos; nº de ad accounts y justificación de cada una; uso del límite de anuncios por Página.
- **Agencias**: trabajar como partner con permisos por tarea; documentar quién tiene acceso; acceso temporal para freelancers.
- **Varias marcas en un grupo**: portfolio por marca (o por entidad), datasets separados por web; si comparten clientes y quieren exclusiones cruzadas, compartir custom audiences entre cuentas (Meta permite compartir listas, [HC 499290663823687](https://www.facebook.com/business/help/499290663823687)).

## Errores frecuentes

1. Activos del cliente creados en el portfolio de la agencia (pérdida de control al terminar la relación).
2. Varias ad accounts para el mismo producto/mercado "para escalar" o "por si acaso".
3. Varios pixels/datasets en la misma web, o un dataset por campaña.
4. Crear Páginas nuevas para esquivar el límite de anuncios.
5. Usar exclusiones de placements o edad a nivel de ad set cuando son restricciones de negocio (deberían ir a controles de cuenta).
6. Estructuras de 30-40 ad sets por intereses con presupuestos de 10-20 €.
7. Ignorar moneda y zona horaria al crear la cuenta (afecta a reporting diario, límites y facturación).

## Preguntas abiertas

- Cuánto "aprendizaje" vive en la ad account vs en el dataset vs en la Página vs en el anunciante (identidad cruzada). Meta solo confirma explícitamente la Página y la identificación cruzada de cuentas para overlap.
- Fecha exacta y alcance del renombre Business Manager → business portfolio (las fuentes secundarias dicen 2023 o 2024).
- Si el límite de "150 anuncios por ad set" citado por CTC es real para algunos anunciantes gestionados.

## Fuentes clave

- [About business portfolios](https://www.facebook.com/business/help/486932075688253) — Meta HC — meta-oficial
- [About business portfolio and business asset permissions](https://www.facebook.com/business/help/442345745885606) — Meta HC — meta-oficial
- [Ad account limits](https://www.facebook.com/business/help/1026272311098874) — Meta HC — meta-oficial
- [Ad limits per Page](https://www.facebook.com/business/help/766697140509126) — Meta HC — meta-oficial
- [Understand auction overlap](https://www.facebook.com/business/help/537699989762051) — Meta HC — meta-oficial
- [Set audience and placement controls for your ad account](https://www.facebook.com/business/help/1438478636941047) — Meta HC — meta-oficial
- [About daily spending limits set by Meta](https://www.facebook.com/business/help/563129151097553) — Meta HC — meta-oficial
- [About managing ad volume](https://www.facebook.com/business/help/2720085414702598) — Meta HC — meta-oficial
- [Combine ad sets and campaigns](https://www.facebook.com/business/help/2419480091640105) — Meta HC — meta-oficial
- [About Advantage+ campaign budget with 70+ ad sets](https://www.facebook.com/business/help/519856662172206) — Meta HC — meta-oficial
- [About system users](https://www.facebook.com/business/help/327596604689624) · [About partners](https://www.facebook.com/business/help/695463587559330) · [Domain verification](https://www.facebook.com/business/help/286768115176155) — Meta HC — meta-oficial
- [Ad campaign reference (limits)](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign) — Meta Developers — meta-developers
- [Meta One Business Plans](https://www.jonloomer.com/meta-one-business-plans/) — Jon Loomer, 2026-09-22 — practitioner
- [How Meta Actually Works in 2026](https://commonthreadco.com/blogs/ecommerce-playbook/how-meta-actually-works-in-2026) — CTC, 2026-07-07 — agencia
