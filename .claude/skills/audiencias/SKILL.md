---
name: audiencias
description: "Lleva tus listas del CRM o de Stripe a Meta: excluir clientes de la captación, listas solo de exclusión, etiquetas para value rules, semillas de lookalike por valor y segmentos de nuevos y existentes. Prepara los datos en privado/, decide qué conviene y la crea con operador-meta tras tu aprobación; aplicarla a campañas va por /ejecutar-cambio."
argument-hint: "<cliente> [excluir|semilla|etiquetas|segmentos|actualizar]"
---

# /audiencias

Entrada: `$ARGUMENTS` (cliente y, opcionalmente, el objetivo). En 2026 la audiencia la decide sobre todo la
creatividad: las listas sirven para **excluir, informar al sistema y ajustar pujas**, no para estrechar el targeting.

Marcos: `meta-ads-kb/02-estructura-campanas/07-audiencias-2026.md` (§4 lookalikes, §5 custom audiences, etiquetas y
segmentos, §6 cuándo segmentar), `meta-ads-kb/02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md` §4
(excluir o no), `meta-ads-kb/06-ecommerce-apps/04-clientes-nuevos-vs-existentes.md` §3–4 (herramientas y cómo
construir la lista de existentes), `meta-ads-kb/09-bidding-escalado-economia-analitica/02-value-optimization-y-value-rules.md`
§4 (value rules), `meta-ads-kb/04-tracking-atribucion-medicion/03-emq-advanced-matching-pii-hashing.md` §2 y §5
(normalización y hash) y `meta-ads-kb/04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md`
§2 y §4 (consentimiento y categorías sensibles).

## Reglas de datos
- Los datos personales (emails, teléfonos, nombres) **solo** se guardan en `clientes/<slug>/privado/`. Fuera de ahí,
  solo recuentos, IDs de audiencia y agregados. Nunca se pegan listas en el chat.
- Antes de subir nada, el usuario confirma por escrito la base legal (consentimiento o interés legítimo recogido en su
  política de privacidad) y que ha aceptado los términos de listas de clientes de Meta. Esto es implementación, no
  asesoría legal.
- **Categorías sensibles**: una lista de pacientes de una clínica (como Clínica Sonrisa) o de clientes de un producto
  financiero revela datos especiales. No se sube sin revisión legal del cliente; propón alternativas (exclusión por
  eventos del dataset, value rules por criterios no sensibles).
- Los borrados de audiencias están bloqueados en este sistema. Si sobra alguna, se anota y la borra el usuario en Ads
  Manager.

## Pasos

1. **Contexto.** Ficha (`tipo`, `crm`, `stripe`, `meta.cuenta`, `meta.evento_principal`), plan de funnel y economía.
   El tipo de negocio decide qué es «cliente»: en servicios, contrato firmado; en SaaS, suscripción de pago activa (y
   las pruebas activas, que también se excluyen de la captación de pruebas).
2. **Inventario** (solo lectura): `ads_get_ad_account_custom_audiences`, y por cada audiencia relevante
   `ads_get_custom_audience` (tamaño, fuente, fecha de actualización) y `ads_get_custom_audience_adsets` (dónde se
   usa). Con token, `python3 -I herramientas/audiencias_meta.py listar --cliente <slug>` da lo mismo de un vistazo
   (tamaño, si es demasiado pequeña para entregar, reemplazo en curso) y si la cuenta ha aceptado las condiciones de
   listas de clientes. Reutiliza lo que sirva antes de crear nada: hay un máximo de 500 audiencias por cuenta y las
   duplicadas confunden. Las audiencias por etapa del pipeline (no-show, propuesta, perdido por timing) y su grupo de
   control son de `/anuncios-por-etapa`.
3. **Decidir qué hace falta** (como mucho 2–3 audiencias por ronda):

| Objetivo | Qué crear | Cómo se usa | Cuándo no |
|---|---|---|---|
| `excluir` clientes de la captación | Lista del CRM o de Stripe con todos los clientes (2–3 años) más compradores del dataset | Campañas de Ventas: estrategia de ciclo de vida «Acquire new customers»; Leads y otras: exclusión de la audiencia en el conjunto | Base pequeña o lista incompleta: excluir mal da falsa sensación de control (`09-…` §4.2) |
| `excluir` leads abiertos (servicios) | Lista de oportunidades abiertas del CRM y audiencia de formulario enviado | Exclusión en campañas de captación, para no pagar dos veces por el mismo lead | Ciclos de venta largos en los que el retoque ayuda: entonces, value rule a la baja |
| Solo exclusión | *Exclusion-only custom audience* | Bajas, opt-outs, empleados, obligaciones legales | No sirve como semilla ni para value rules |
| `etiquetas` para value rules | Lista con etiqueta (*Qualified* o *Disqualified leads*, *High* o *Low value*) | Value rule con ajuste conservador (±20–30 % al inicio) | Sin datos de valor por segmento: amplifica supuestos (`09-bidding-…/02-…` §4.4) |
| `semilla` de lookalike por valor | Lista de los mejores clientes con columna de valor (LTV o ticket) | Sugerencia en cuentas nuevas o de poco volumen; desde oct-2025 el sistema expande igualmente (`07-…` §4) | Como eje de la estructura, o «un lookalike por país» (desde sept-2026 no tiene sentido) |
| `segmentos` | Definir *Engaged audience* y *Existing customers* a nivel de cuenta | Desgloses de nuevos, engaged y existentes; existentes = compras hasta 730 días más clientes del CRM | — |

   En SaaS con prueba, excluir clientes de pago y pruebas activas suele ser lo primero (`06-…/04-…` §4). Con
   `[CONTESTED]` (excluir o usar value rules), aplica la tabla de `09-…` §4.2 y explica la elección.
4. **Plan.** Escribe `clientes/<slug>/planes/AAAA-MM-DD_audiencias.md`: audiencias a crear (nombre con la
   nomenclatura de `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8), fuente, columnas, recuento esperado
   (sin datos personales), uso previsto, cadencia de refresco y vía de subida. **Para aquí y pide aprobación.**
5. **Extraer** a `privado/`, nunca a otra carpeta. Las herramientas guardan ahí solas el detalle con datos
   personales y por pantalla solo dan agregados; por defecto miran 7 días, así que pasa el periodo completo de la
   lista:
   - GHL: `python3 -I herramientas/ghl.py oportunidades --cliente <slug> --desde <hace 2–3 años> --hasta <ayer>`
     (ganadas = clientes; abiertas = leads en curso) y `ghl.py contactos` con el mismo periodo para completar emails y
     teléfonos. O una exportación de GHL que el usuario deja en `clientes/<slug>/privado/`.
   - Stripe: `python3 -I herramientas/stripe_datos.py clientes --cliente <slug> --desde <…> --hasta <…>` y
     `stripe_datos.py suscripciones` con el mismo periodo, para separar pago, prueba y bajas.
   - Une y deja en `clientes/<slug>/privado/AAAA-MM-DD_<audiencia>.csv` las columnas `email`, `phone`, `fn`, `ln`,
     `ct`, `zp`, `country` y, para semillas por valor, `value`. Más identificadores = más coincidencia.
6. **Normalizar** con las reglas de `04-…/03-…` §2: teléfono con prefijo de país y sin `+`, email en minúsculas, país
   siempre. Comprueba la normalización con 2–3 filas de ejemplo:
   `python3 -I herramientas/capi.py hashear --tipo ph --prefijo 34 "<teléfono>"` (o `--tipo em`). Informa solo del
   recuento y del porcentaje de filas con email o teléfono válidos.
   - Vía Ads Manager: basta el archivo normalizado; Meta lo hashea en el navegador antes de subirlo.
   - Vía herramienta o MCP: la lista entera tiene que ir hasheada.
     `python3 -I herramientas/capi.py hashear --archivo clientes/<slug>/privado/AAAA-MM-DD_<audiencia>.csv --prefijo 34`
     normaliza, hashea y deja `privado/AAAA-MM-DD_<audiencia>-hash.csv` solo con hashes y las cabeceras de la
     plantilla de Meta.
7. **Subir**, por la vía aprobada en el plan. La **semilla por valor** solo va por Ads Manager, con el archivo
   normalizado sin hashear y la columna `value`: ni `audiencias_meta.py` (no crea audiencias por valor y rechaza la
   columna) ni `capi.py hashear` (que la descarta) suben el valor.
   - **Ads Manager** (recomendada para listas grandes, y la única para segmentos de cuenta): el usuario sube el archivo
     en Audiences → Create audience → Customer list, o conecta la sincronización nativa de su CRM si la tiene. Meta
     hashea en el navegador.
   - **Herramienta** (con token; los hashes no pasan por la conversación): `operador-meta` crea la audiencia vacía con
     `python3 -I herramientas/audiencias_meta.py crear "<nombre>" --cliente <slug> --confirmo` (si ya existe una con
     ese nombre, da su ID y no crea otra) y sube el CSV hasheado con
     `audiencias_meta.py sincronizar <id> --cliente <slug> --archivo <csv hasheado de privado/> --reemplazar --confirmo`.
     Comprueba que la cuenta ha aceptado las condiciones, rechaza celdas sin hashear, sube en lotes de 10.000 y deja la
     fila del change log. Prueba antes con `--simular`.
   - **MCP** (listas pequeñas): `operador-meta` crea la audiencia con `ads_create_custom_audience` y añade los
     usuarios hasheados con `ads_update_custom_audience_users`, después de comprobar el esquema de entrada de esa
     herramienta (campos y si espera el hash ya hecho). Los hashes pasan por la conversación: siguen siendo datos
     personales seudonimizados, así que úsala solo si el usuario la elige sabiéndolo.
   - Las etiquetas (`QUALIFIED_LEADS`, `DISQUALIFIED_LEADS`, `HIGH_VALUE_CUSTOMERS`, entre otras **[OFFICIAL META]**)
     se ponen al crear: `audiencias_meta.py crear … --etiqueta QUALIFIED_LEADS`. El formato del parámetro en la API no
     está verificado: si Meta lo rechaza, crea la audiencia sin etiqueta y ponla en Ads Manager.
8. **Verificar** a las 24–48 h con `ads_get_custom_audience` o `audiencias_meta.py listar` (estado listo y tamaño
   aproximado). Una audiencia que no llega a un tamaño útil no se usa como semilla.
9. **Aplicar** las exclusiones a conjuntos, la estrategia de ciclo de vida o las value rules es un cambio en
   campañas: va por `/ejecutar-cambio` con su plan (las value rules, solo con datos de valor por segmento). Cada
   creación o cambio en Meta se anota en `clientes/<slug>/change-log.md` con el ID de la audiencia.
10. **Refresco** (`actualizar`): repite los pasos 5–7 sobre las mismas audiencias. Por la herramienta, con
    `sincronizar --reemplazar`: sustituye la lista entera sin reiniciar el aprendizaje de los conjuntos que la usan;
    añadir o quitar personas, sí lo reinicia **[OFFICIAL META]**. Las listas de exclusión de
    clientes, como mínimo cada semana (`06-…/04-…` §4); las semillas, cada mes. Control de calidad: compara el % de
    resultados que Meta atribuye a «existentes» con el % real de recurrentes del CRM o de Stripe; si Meta ve muchos
    menos, la lista está incompleta o coincide poco.
11. **Cierre.** Anota en la sección «Audiencias» de la ficha (contrato §3: `| Audiencia | ID | Uso | Origen y
    actualización |`) las audiencias activas con su nombre, ID, uso (incluir o excluir, en qué conjuntos) y cadencia de
    refresco. Si la ficha es antigua y no tiene esa sección, créala antes de «Notas y aprendizajes clave». Los archivos de `privado/` con datos personales se pueden borrar tras la subida, pero solo si el
    usuario lo confirma por escrito.
