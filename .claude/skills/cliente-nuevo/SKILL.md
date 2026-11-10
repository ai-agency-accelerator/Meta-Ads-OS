---
name: cliente-nuevo
description: "Da de alta un cliente o tu propio negocio en clientes/<slug>/ desde la plantilla y rellena su ficha: la cabecera que leen herramientas y hooks (tipo, moneda, mercados, IDs de Meta, evento, topes, CRM, Stripe) y el cuerpo de negocio y medición, y su estado. Con rapido, lo mínimo; con sin-economia, deja la economía a quien la llama."
argument-hint: "<nombre> [rapido] [sin-economia]"
---

# /cliente-nuevo

Entrada: `$ARGUMENTS` (nombre y, opcionalmente, `rapido` y `sin-economia`). Si falta el nombre, pregúntalo.
`sin-economia` es para cuando te llama otra skill que hace la economía en su propio paso (`/empezar`): así no se
pisan. Formato de la ficha:
contrato §3 y `plantillas/cliente/ficha.md`; estado: contrato §4 y `plantillas/cliente/estado.md`.

## Pasos

1. **Slug**: minúsculas, sin acentos, palabras con guiones (`Clínica Sonrisa` → `clinica-sonrisa`); solo
   `[a-z0-9-]`, empezando por letra o número. Si `clientes/<slug>/` ya existe, **no lo sobrescribas**: ábrelo y
   completa lo que falte.
2. **Copia la plantilla**: `cp -R plantillas/cliente clientes/<slug>` (vale en Mac, Linux y Git Bash). Sustituye
   `<slug>`, `<nombre>` y `<cliente>` en `ficha.md`, `change-log.md`, `aprendizajes-creativos.md` y
   `cohortes-leads.md`.
3. **Entrevista** (una o dos preguntas por turno, como mucho 8 turnos). Con `rapido`, solo las marcadas ★; el resto
   queda «(por definir)».
   - ★ Nombre, `tipo` (`servicios-high-ticket | saas | ecommerce | lead-gen | local | app | infoproducto`) y `relacion`
     (`propio` = tu negocio; `cliente` = de tu agencia).
   - ★ `moneda` y `zona_horaria` (las de la cuenta publicitaria, si ya existe).
   - ★ Oferta principal y precio (con o sin IVA), mercados e idiomas. Los países donde se anuncia van en `mercados`,
     en códigos ISO separados por comas (`ES`, `ES, FR`): `economia.py --cliente` aplica con ellos la tasa por
     ubicación de Meta (ES, FR e IT 3 %; UK 2 %; AT y TR 5 %). Los idiomas, en el cuerpo («Mercados e idiomas»).
   - Objetivo del trimestre en resultado de negocio (no en métricas de Meta) y capacidad (agenda comercial, plazas,
     onboarding).
   - Categoría especial o sensible (finanzas, salud, empleo, vivienda) → `meta-ads-kb/08-cuenta-politicas-seguridad/07-categorias-especiales-y-sensibles.md`.
   - ★ Stack: web, CRM (`crm.tipo`: `ghl | hubspot | ninguno`), Stripe (`stripe: true|false`), calendario,
     automatizaciones.
   - Presupuesto mensual previsto y cuánto acepta perder mientras se aprende.
   - ★ **Topes** en euros: `cambio_dia` (máximo de presupuesto diario en un solo cambio o plan) y `total_dia` (suma
     diaria de todo lo activo). **Solo cifras que diga el usuario.** Como referencia, `cambio_dia` ≈ el presupuesto
     diario que piensa poner a una campaña y `total_dia` ≈ la suma de todas `[HYPOTHESIS]`. Si no lo sabe, quedan a 0
     y explícale que con 0 el sistema no deja crear ni subir presupuestos (hook `meta_guard`).
   - `meta.evento_principal` (`Lead`, `Schedule`, `Purchase`, `StartTrial`, `Subscribe` o un evento del CRM). Si no lo
     sabe, vacío: lo decide `/disenar-funnel`.
   - `meta.ventana_atribucion`: `7d_click_1d_view` por defecto, y hay que verificarla en el conjunto de anuncios
     (`meta-ads-kb/00-ESTADO-ACTUAL-2026.md` §6).
   - `mejoras_automaticas`: `off` por defecto. Explica por qué: Meta activa por defecto mejoras con IA (reescritura de
     texto en imágenes, doblaje, música) que pueden cambiar el mensaje o meter afirmaciones no aprobadas
     (`00-ESTADO-ACTUAL-2026.md` §0 punto 7 y `meta-ads-kb/03-creatividad/14-herramientas-ia-creativa-meta.md`).
   - `explorar_explotar`: 0,3 por defecto `[HYPOTHESIS]` (fracción del presupuesto creativo para conceptos nuevos).
   - **Playbook** del tipo (la misma tabla que `/lanzar-campana`), en la línea «Playbook:» de «Negocio». Si es
     `servicios-high-ticket` o cualquier venta consultiva con llamada (consultoras y agencias de IA y automatización
     que venden a pymes, aunque el tipo sea `lead-gen`), propone leer
     `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` (§3 economía con el coste de vender y el
     techo de capacidad, §6 evento por volumen) y pregunta por los campos opcionales del contrato §3, sin inventar
     ninguno:
     - `capacidad.llamadas_semana` y `capacidad.propuestas_semana`: lo que el equipo puede atender de verdad; es el
       techo de gasto antes que el de Meta (§3.6);
     - `coste_vender_por_venta`: horas de venta por proyecto × coste por hora (va a `economia.py --coste-fijo`);
     - `etapa_objetivo_cl`: la etapa del §16 candidata a Conversion Leads (normalmente `cualificado`);
     - `definicion_cualificado`: qué es un lead cualificado, por escrito; no se cambia con campañas activas;
     - `umbral_no_compensa`: ahorro neto anual mínimo para que el diagnóstico diga «compensa» (si usa
       `/iman-de-leads` con calculadora);
     - el ciclo de venta (días de la primera llamada a la firma y cuántos deciden), en «Negocio»: lo usa
       `/disenar-funnel` para valorar la VSL.

     Con `rapido`, solo el playbook; los campos quedan en 0 o vacíos.
   - Mensajería: si va a usar WhatsApp, `meta.waba` y, si es otro, `meta.dataset_mensajeria` (`docs/guias/mensajeria.md`).
4. **Escribe la ficha**: la cabecera con las claves exactas del contrato §3 y el cuerpo (Negocio, Medición, Política
   de mejoras automáticas, Reglas propias, Afirmaciones aprobadas, Audiencias) con lo que sepas. «Afirmaciones
   aprobadas» empieza vacía: solo entra lo que el cliente apruebe por escrito, con su fuente. Fecha de «Última actualización» de hoy.
5. **IDs de Meta**, si el MCP está conectado: `ads_get_ad_accounts` → el usuario elige la cuenta (`meta.cuenta`);
   después `ads_get_ad_account_pages`, `ads_get_ig_accounts` y `ads_get_datasets` (y `ads_catalog_list_catalogs` en
   ecommerce). `meta.instagram` es el ID numérico de la cuenta profesional, no el @usuario. Confirma con él cuál es
   cuál; no lo adivines. Sin MCP, vacíos y sugiere `/conectar meta`.
6. **Economía**: esta skill no la calcula ni lanza `/economia` por su cuenta.
   - Con `sin-economia`, sáltate el paso: quien te llamó la hace en el suyo.
   - Si no, sin `rapido` y con precio y tasas del embudo, **ofrece** `/economia <slug>` y lánzala solo si el usuario
     dice que sí.
   - Si no, queda para después (`F0.economia`).
7. **Valida**: `python3 -I herramientas/doctor.py --json` debe dar la ficha por válida. Si falla, el mensaje dice qué
   campo arreglar.
8. **Estado** (`clientes/<slug>/estado.md`): pon `actualizado` a hoy y marca solo lo verificado ahora: `F0.ficha` si
   Negocio está completo, `F0.topes` si los dos topes son mayores que 0, `F0.economia` si la tabla está rellena. La
   cabecera `fase` es la primera fase con puntos sin marcar.
9. **Datos personales**: la ficha no lleva emails, teléfonos ni nombres de leads o clientes finales. Contactos del
   cliente, como rol («responsable comercial»), no como persona.
10. **Siguiente paso** según la situación (con `sin-economia`, ninguno: devuelve el control a quien te llamó): sin
    economía → `/economia`; sin cuenta o sin señal → `/configurar-meta`;
    cuenta de un cliente con histórico → `/configurar-meta <slug> heredada` y después `/auditoria <slug>`; sin oferta
   de entrada (venta consultiva) → `/oferta` y `/iman-de-leads`. No añadas
    el cliente a `clientes/README.md`: ese archivo se versiona y no lleva datos.
