---
name: lanzar-campana
description: "Lanza una campaña nueva en Meta con gates (economía, señal, oferta y funnel, creatividad), plan revisado por revisor-estrategia y aprobado por ti, creación en pausa por operador-meta, previsualizaciones y activación solo con confirmación expresa. Modo profundo con el workflow lanzamiento-completo."
argument-hint: "<cliente> [profundo]"
disable-model-invocation: true
---

# /lanzar-campana

Entrada: `$ARGUMENTS`. **No se crea nada en Meta hasta el paso 8**, y nada se activa sin una confirmación específica en
el momento.

- **Marco:** `meta-ads-kb/13-sistema-operativo/03-framework-lanzamiento.md` (gates y fases 0–9),
  `meta-ads-kb/13-sistema-operativo/08-cuenta-nueva-y-heredada.md` (§A si la cuenta es nueva),
  `meta-ads-kb/13-sistema-operativo/09-presupuesto-pequeno-y-grande.md`, `meta-ads-kb/02-estructura-campanas/02-eventos-de-optimizacion.md`,
  `meta-ads-kb/02-estructura-campanas/05-arquitectura-de-campanas.md`, nomenclatura y UTMs en
  `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8 y el playbook del tipo de la ficha:

  | `tipo` en la ficha | Playbook en `meta-ads-kb/14-playbooks/` |
  |---|---|
  | `servicios-high-ticket` | `playbook-consultoras-ia-automatizacion.md` si vende IA o automatización a pymes; si no, `playbook-high-ticket.md` (+ `playbook-agencias-consultores.md` si vende servicios de agencia o consultoría) |
  | `saas` | `playbook-saas.md` (+ `playbook-b2b.md` si es B2B) |
  | `lead-gen` | `playbook-lead-gen.md` |
  | `local` | `playbook-negocio-local.md` |
  | `ecommerce` | `playbook-ecommerce-dtc.md` |
  | `app` | `playbook-apps.md` |
  | `infoproducto` | `playbook-cursos-infoproductos.md` (+ `playbook-webinars-eventos-lanzamientos.md` si es lanzamiento) |

- **Agentes:** `analista-cuantitativo`, `especialista-tracking`, `especialista-funnel`, `revisor-politicas`,
  `revisor-estrategia`, `operador-meta` (el único que escribe).
- **Herramientas:** `economia.py`, `nomenclatura.py`, `meta_ads.py` (`crear --simular`, `crear`, `creatividades`,
  `activar --confirmo`).
- **Lee:** ficha, `estado.md`, lote con piezas listas, LEEME de cada pieza.
- **Escribe:** `clientes/<slug>/planes/<AAAA-MM-DD>_<campana>.md` y `.json`, `change-log.md`, `registro-creativo.csv`,
  `lote.md`, LEEME (`Estado: publicado`) y `estado.md` (`F4.plan`, `F4.creada`, `F4.activa`).

## Pasos

1. **Requisitos de seguridad.** Ficha con `meta.cuenta` y **topes distintos de 0** (`topes.cambio_dia`,
   `topes.total_dia`): con topes a 0 no se crea nada; que el usuario los defina primero. Comprueba `F1.reglas-mcp`
   (límite de gasto de la cuenta y regla de presupuesto máximo del Ads MCP server); si falta → `/configurar-meta`.
2. **Gate 1 · Economía:** break-even y target por etapa en la ficha. Si faltan → `/economia` (incluye el modo
   `prevision` para enseñar leads, citas y ventas esperables por nivel de inversión).
3. **Gate 2 · Señal** (`especialista-tracking`, con `ads_get_datasets`, `ads_get_dataset_stats` y
   `ads_get_dataset_quality`): dataset único, `meta.evento_principal` llegando por navegador y servidor, deduplicación,
   calidad de coincidencia «Good» o mejor (≥6,0 recomendado por Meta), 3 conversiones de prueba reconciliadas con el
   backend o el CRM y, en lead gen, etapas del CRM volviendo a Meta. Si falla → `/implementar-capi` o
   `/configurar-meta`. El usuario puede decidir seguir, pero el riesgo queda escrito en el plan.
4. **Gate 3 · Oferta y funnel:** landing revisada en móvil (`/landing`; si no existe, `/construir-landing`) o
   formulario instantáneo creado y probado con un lead de prueba (`/formulario-instantaneo`); en lead gen, responsable
   y SLA de respuesta (≤5 min en horario), calendario y seguimiento (`/seguimiento-leads`); en SaaS, registro o prueba
   probados de punta a punta.
5. **Gate 4 · Creatividad:** conceptos **distintos** según el presupuesto del plan (2–4 hasta 100 €/día, 3–6 hasta
   500 €/día, 8–15 por encima; 13/09 §A.2), en un lote con `Estado` = `lista` y veredicto de políticas OK
   u OK con cambios aplicados en su LEEME. Si no → `/brief-creativo` y `/producir-video` o `/producir-estatico`.
6. **Plan** (`analista-cuantitativo` para presupuesto y evento), en `planes/<AAAA-MM-DD>_<campana>.md`:
   - objetivo y **evento**: el más cercano al dinero con volumen útil (servicios: lead cualificado o cita si hay CAPI
     del CRM; SaaS: prueba activada o registro mientras no haya volumen; 02/02 y principio 1 de
     `meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md`);
   - estructura por defecto: 1 campaña, 1 conjunto, Advantage+ (presupuesto de campaña, audiencia y ubicaciones);
     separar solo con razón de negocio;
   - presupuesto ≈ 7 × CPA esperado al día por conjunto, **nunca por encima de `topes.cambio_dia`**; si no llega,
     consolidar y aceptar varianza (09 §A);
   - puja (Highest volume por defecto), países, exclusión de clientes actuales o estrategia de ciclo de vida
     (`/audiencias`), categoría especial si aplica;
   - assets por ubicación (9:16 y 4:5), ventana de atribución de la ficha (a verificar en el conjunto), mejoras
     automáticas según `mejoras_automaticas` de la ficha;
   - **ajustes que Meta cambió en 2026** (`meta-ads-kb/00-ESTADO-ACTUAL-2026.md`): las ubicaciones manuales del conjunto
     solo existen fuera de Ventas, Clientes potenciales y App (en Engagement, Awareness y Traffic siguen; no lo des por
     perdido al leer un plan); en Ventas, la audiencia por creativo (`creative_audience_pairing`) viene activada: decide
     si se quiere (en B2B rara vez aporta y no sirve para testear); en Ventas con `user_device` o `user_os`, Meta activa
     la expansión de dispositivos desde la v27: `meta_ads.py` la desactiva por defecto
     (`targeting_automation.individual_setting.device = 0`) y solo la deja con `"expansion_dispositivos": true` en el
     plan; por el MCP o en Ads Manager, compruébalo a mano;
   - con formulario instantáneo y el CRM devolviendo etapas por CAPI, el conjunto puede optimizar a Conversion Leads
     (`"optimizar": "QUALITY_LEAD"` y `"dataset_crm"`, ver `_leeme` de `plantillas/plan-campana.json`) solo si el
     playbook lo justifica por volumen (el mínimo de leads es [CONTESTED]: ≥200 al mes por prudencia);
   - nombres: campaña `<MERCADO>_<OBJETIVO>_<PROPOSITO>_<PUJA>`, conjunto `<AUDIENCIA>_<EVENTO>` y anuncios del lote,
     cada uno validado con `python3 -I herramientas/nomenclatura.py validar <nivel> "<nombre>"`;
   - UTMs con la plantilla única de 10-plantillas §8 (llevan `ad_id` para unir con el CRM);
   - anuncios con texto final, URL y CTA; fecha de primera evaluación (≥7 días, 30–50 eventos y ventana madurada) y
     kill rules (`meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` §5).

   Escribe también la versión máquina `planes/<AAAA-MM-DD>_<campana>.json` con el formato de `plantillas/plan-campana.json`
   y valídala sin red: `python3 -I herramientas/meta_ads.py crear clientes/<slug>/planes/<AAAA-MM-DD>_<campana>.json --simular --cliente <slug>`.
7. **Revisiones y aprobación.** `revisor-politicas` confirma copy, piezas, landing y formulario; `revisor-estrategia`
   revisa el plan contra los principios, los mitos y la regla de paciencia. Aplica o justifica cada observación.
   Presenta: tabla del plan, presupuesto diario total, qué se va a crear (todo en pausa) y qué no (la activación).
   **Espera un «sí» explícito.** Marca `F4.plan`.
8. **Creación en pausa** (`operador-meta`; cada escritura pide confirmación y `meta_guard` bloquea presupuestos por
   encima del tope):
   - **con token** (`/conectar meta --avanzado` hecho): `python3 -I herramientas/meta_ads.py crear <plan.json> --cliente <slug>`
     sube vídeos e imágenes, crea las creatividades con las mejoras automáticas que diga `mejoras_automaticas` de la
     ficha y es idempotente (estado en `<plan>.estado.json`). `off`: todas desactivadas; `revisar`: las decide Meta
     salvo el escaparate de productos, y `crear` lista las que ha puesto para revisarlas; `on`: las que ponga Meta. Sin
     la clave, o con un valor que no sea uno de esos tres, cuenta como `off` (y con un valor desconocido, avisa);
   - **sin token:** MCP `ads_create_campaign` → `ads_create_ad_set` → `ads_create_creative` (solo imagen única) →
     `ads_create_ad`. Los vídeos los sube el usuario en Ads Manager con una checklist (en pausa, nombre exacto, UTMs,
     mejoras según la ficha, assets 9:16 y 4:5) y `operador-meta` verifica después.
9. **Verificación:** relee todo (`ads_get_ad_entities`, `ads_get_errors`), previsualizaciones en Feed y Reels/Stories
   (`ads_get_ad_preview`), mejoras automáticas como dice la ficha (`meta_ads.py creatividades --plan <plan.json>` con
   token, o `ads_get_creatives`), URL y UTMs. Enseña previsualizaciones e IDs. Marca `F4.creada`.
10. **Activación**, solo si el usuario la confirma ahora y de forma específica («activa <campaña> con <X> €/día»), y
    siempre por `operador-meta` (desde la sesión principal el hook la bloquea): `ads_activate_entity` o `python3 -I herramientas/meta_ads.py activar --plan <plan.json> --confirmo --cliente <slug>`.
    Lanza todo junto y pronto en el día (fase 8). Marca `F4.activa`.
11. **Registro:** `operador-meta` anota creación y activación en `change-log.md` (columnas del contrato, IDs
    numéricos, fecha de evaluación). Añade una fila por anuncio a `registro-creativo.csv` (`ad_id`, `nombre`, `fecha`,
    `campana`, `conjunto`, `angulo`, `concepto`, `formato`, `hook`, `via`, `ruta_creativo` = `creativos/<nombre-base>`,
    `veredicto` = `en-test`), pon `Estado` = `publicada` y el `ad_id` en `lote.md`, y `- **Estado:** publicado` en cada
    LEEME.
12. **Después:** días 1–3 solo se corrigen roturas (las vigila `/brief-diario`); la primera lectura es en
    `/informe-semanal` cuando se cumpla la regla de paciencia. Viabilidad en la semana 4 (fase 9). Si la cuenta no
    tiene reglas del OS (`python3 -I herramientas/reglas_meta.py listar --cliente <slug>` o Ads Manager), propone
    `/reglas-automaticas <cliente>` después de activar.

## Modo `profundo`

1. **Avisa del coste:** el workflow `lanzamiento-completo` (economía → funnel → señal → investigación → briefs →
   textos → políticas → plan para aprobar) lanza unos 8–9 subagentes si ya hay matriz de ángulos y lote listos, y
   hasta unos 30–35 si también tiene que generar investigación y briefs (`generar_faltantes`, activo por defecto).
   Consume mucho más uso de Claude que el modo normal. **No escribe en Meta**: termina en un plan.
2. Con un «sí», lánzalo con la herramienta Workflow y args `{"cliente": "<slug>", "nombre": "<slug de la campaña>"}`.
   Para la versión ligera, añade `"generar_faltantes": false` y manda antes a `/competencia` y `/brief-creativo`.
3. Revisa que el plan cumple el paso 6 y continúa en el paso 7.

## Reglas

- Solo `operador-meta` escribe en Meta, siempre en pausa. Si una regla del Ads MCP server o `meta_guard` bloquean algo,
  no se rodea: se ajusta el plan o el usuario cambia conscientemente sus topes en la ficha.
- Nunca circunvención: ni cuentas ni Páginas nuevas para esquivar restricciones.
