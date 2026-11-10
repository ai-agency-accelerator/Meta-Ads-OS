# Contratos entre bloques

> Fuente de verdad de nombres, rutas, formatos y firmas. Cada bloque construye contra este documento. Si un bloque
> necesita cambiar un contrato, no toca archivos de otro bloque: lo apunta en `docs/desarrollo/notas/<bloque>.md` y se
> adapta al contrato vigente. La integración final resuelve esas notas.
>
> Revisado en la integración del 2026-11-10 con las peticiones de las notas B1–B21.

## 1. Producto e instancia

El **producto** es todo lo versionado:

```
.claude/{agents,skills,hooks,workflows,output-styles}/   settings.json
meta-ads-kb/          herramientas/        modulos/{motor-ia,cutkit}/
plantillas/           docs/                scripts/            tests/
CLAUDE.md  README.md  CHANGELOG.md  LICENSE  .mcp.json  pyproject.toml  .gitignore  .gitattributes
```

La **instancia** son los datos de cada operador. Todo está ignorado por git y lo crea el instalador a partir de
`plantillas/`:

```
contexto/      operador.md · instalacion.json · preferencias.md · (entrenamiento.md, fugas.txt)
clientes/<slug>/   ficha.md · estado.md · change-log.md · registro-creativo.csv · aprendizajes-creativos.md
                   cohortes-leads.md · informes/ · auditorias/ · creativos/ · investigacion/ · planes/
                   datos/ (exportaciones sin datos personales) · privado/ (con datos personales, nunca se comparte)
                   marca/ (marca.json + archivos, §14) · paginas/ (salida de paginas.py, §17)
informes/diario/AAAA-MM-DD.md   (resumen global del brief)
aprendizajes/  logs/  .env
```

- `.env` se crea en la instalación copiando `plantillas/env.ejemplo` (no `.env.example`: los permisos niegan leer
  `.env.*`), con permisos 600.
- `clientes/README.md`, `contexto/README.md` y `aprendizajes/README.md` sí se versionan: explican la carpeta, no
  contienen datos.
- `/actualizar` nunca escribe en la instancia, salvo las migraciones que declare `scripts/migraciones/`.

## 2. Nombres fijos

**Servidores MCP**
- `meta-ads`: en `.mcp.json`, URL `https://mcp.facebook.com/ads`.
- `ghl`: `https://services.leadconnectorhq.com/mcp/anthropic/v2`.
- `stripe`: `https://mcp.stripe.com`.

`ghl` y `stripe` los añade `/conectar` con `claude mcp add --transport http --scope local <nombre> <url>`. Así no
modifican `.mcp.json` y cada usuario conecta los suyos. Los prefijos de herramienta son `mcp__meta-ads__`, `mcp__ghl__`
y `mcp__stripe__`. Una agencia con varias sub-cuentas de GHL añade un servidor por sub-cuenta llamado `ghl-<slug>`
(prefijo `mcp__ghl-<slug>__`) y lo apunta en la ficha en `crm.servidor_mcp`. Guardas y permisos cubren `ghl` y
`ghl-*` (y `stripe-*`): los hooks con un matcher regex y `/conectar` con reglas explícitas por servidor en
`.claude/settings.local.json` (§10).

**Skills (50)** — carpeta `.claude/skills/<nombre>/SKILL.md`

| Grupo | Skills |
|---|---|
| Entradas | `empezar`, `hoy`, `pregunta`, `siguiente-anuncio` |
| Sistema | `menu`, `doctor`, `actualizar`, `conectar`, `motor` |
| F0 | `cliente-nuevo`, `economia`, `oferta`, `disenar-funnel`, `iman-de-leads` |
| F1 | `configurar-meta`, `implementar-capi`, `audiencias`, `landing`, `construir-landing`, `formulario-instantaneo` |
| F2 | `competencia`, `voz-cliente` |
| F3 | `brief-creativo`, `producir-video`, `producir-estatico`, `variantes`, `revisar-anuncio`, `analisis-creativo`, `casos-y-creadores`, `organico-a-anuncios` |
| F4 | `lanzar-campana`, `publicar-anuncios`, `test-creativo`, `webinar` |
| F5 | `brief-diario`, `informe-semanal`, `revision-mensual`, `diagnostico`, `ejecutar-cambio`, `embudo`, `rescate-cuenta`, `reglas-automaticas`, `seguimiento-leads`, `anuncios-por-etapa` |
| F6 | `escalar`, `auditoria` |
| Agencia | `informe-cliente`, `auditoria-express`, `entrenar`, `novedades-meta` |

Renombradas en la v1 (las carpetas antiguas ya no están en el producto): `meta-conectar` → `conectar`, `pulso` →
`brief-diario`, `producir-ugc` → `producir-video`, `variantes-ugc` → `variantes`, `actualizar-kb` → `novedades-meta`.
`/brief-diario`: ver §15.

**Agentes (20)** — archivo `.claude/agents/<nombre>.md`:
`analista-meta`, `analista-cuantitativo`, `auditor-cuenta`, `operador-meta`, `especialista-tracking`, `ingeniero-capi`,
`especialista-funnel`, `especialista-crm`, `estratega-creativo`, `redactor-anuncios`, `investigador-competencia`,
`productor-ugc`, `editor-video`, `disenador-estaticos`, `critico-creativo`, `revisor-politicas`, `revisor-estrategia`,
`gestor-cliente`, `mentor-meta`, `curador-conocimiento`.

**Hooks (10)** — archivo `.claude/hooks/<nombre>.py` (`_lib.py` es la librería común y no cuenta):
`meta_guard`, `motor_guard`, `ghl_guard`, `stripe_guard`, `eventos_guard`, `control_publicacion`, `datos_personales`,
`secretos`, `registro_obligatorio`, `contexto_sesion`.

**Workflows (5)** — archivo `.claude/workflows/<nombre>.js`:
`auditoria-profunda`, `investigacion-mercado`, `estudio-creativo` (sustituye a `ugc-creative-studio`),
`lote-creativo`, `lanzamiento-completo`.

**Herramientas (25)** — archivo `herramientas/<nombre>.py`. `_comun.py` es la librería compartida y no cuenta:
`ad_library`, `economia`, `estadistica`, `ig_competidores`, `landing_check`, `motor_proyectos`, `reddit_pulso`,
`transcribir`, `meta_ads`, `ghl`, `stripe_datos`, `capi`, `nomenclatura`, `registro_creativo`, `embudo`, `estado`,
`notificar`, `render`, `editar_video`, `doctor`, `reglas_meta`, `elementos_creativos`, `paginas`, `formularios_meta`,
`audiencias_meta`.

Subcomandos de las 5 de la segunda ola (opciones completas en §9):

| Herramienta | Subcomandos | Escrituras |
|---|---|---|
| `reglas_meta.py` | `listar`, `proponer`, `crear <json> [--simular [--pasos]]`, `pausar <id>…`, `reactivar <id>…`, `historial`, `destinatarios` | `crear`, `pausar` y `reactivar` exigen `--confirmo`; solo reglas programadas que avisan o pausan; nunca borra |
| `elementos_creativos.py` | `fotogramas`, `etiquetas esquema\|preparar\|pendientes\|poner\|validar`, `analizar`, `retencion`, `diversidad`, `suministro` | Solo archivos locales (`datos/`, `datos/analisis-creativo/`, `creativos/_fotogramas/`); solo lee de Meta (`fotogramas --api`) |
| `paginas.py` | `generar <landing\|diagnostico\|reserva\|gracias\|webinar\|todas> --config <json> --salida <dir>`, `validar <dir>`, `probar --config <json>` | Solo archivos locales; nunca borra |
| `formularios_meta.py` | `listar`, `ver <id>`, `crear <json> [--simular]`, `guia <json>`, `leads <id> --desde --hasta` | `crear` exige `--confirmo`; `leads` escribe en `privado/` (detalle) y `datos/` (agregados) |
| `audiencias_meta.py` | `listar`, `etapas` (CSV hasheados por etapa desde `privado/`), `crear <nombre>`, `sincronizar <id> --archivo <csv> [--reemplazar]`, `medir` | `crear` y `sincronizar` exigen `--confirmo` |

- `calculadora_funnel.py` se integró en `economia.py` y ya no está en la KB.
- `notificar.py`: ver §15.

**Estilos de salida (2)** — `.claude/output-styles/profesor.md` y `.claude/output-styles/operador.md`. Se activan con
`/config` o con `"outputStyle"` en `.claude/settings.local.json`; el campo `estilo` de las preferencias no activa nada
por sí solo.

## 3. Ficha del cliente: `clientes/<slug>/ficha.md`

Cabecera YAML legible por máquina. El cuerpo en Markdown es el de `plantillas/cliente/ficha.md`.

```yaml
---
slug: acme-automations          # minúsculas, guiones
nombre: Acme Automations
estado: activo                  # activo | pausa | prospecto
tipo: servicios-high-ticket     # servicios-high-ticket | saas | ecommerce | lead-gen | local | app | infoproducto
relacion: propio                # propio (mi negocio) | cliente (de mi agencia)
moneda: EUR
zona_horaria: Europe/Madrid
mercados: ES                    # opcional: países donde se anuncia, códigos ISO separados por comas (ES, FR)
meta:
  cuenta: act_000000000000000
  pagina: ""
  instagram: ""                 # ID numérico de la cuenta profesional de Instagram (no el @usuario)
  dataset: ""
  catalogo: ""
  waba: ""                      # opcional: ID de la cuenta de WhatsApp Business (mensajería, §16)
  dataset_mensajeria: ""        # opcional: dataset vinculado a la WABA, la Página o Instagram, si no es `dataset`
  evento_principal: Lead
  ventana_atribucion: 7d_click_1d_view
topes:
  cambio_dia: 100               # € máximos de presupuesto diario en un único cambio o plan (hook meta_guard)
  total_dia: 300                # € diarios máximos sumando todo lo activo (necesita token de meta_ads.py)
crm:
  tipo: ninguno                 # ghl | hubspot | ninguno
  servidor_mcp: ghl
stripe: false
mejoras_automaticas: off        # off | revisar | on  (off = meta_ads.py las desactiva todas)
explorar_explotar: 0.3          # fracción del presupuesto creativo para conceptos nuevos [HYPOTHESIS]
capacidad:                      # opcional (venta con llamada): techo de gasto antes que Meta
  llamadas_semana: 0
  propuestas_semana: 0
coste_vender_por_venta: 0       # opcional: € de tiempo comercial por venta (economia.py --coste-fijo)
etapa_objetivo_cl: ""           # opcional: etapa del §16 candidata a Conversion Leads (p. ej. cualificado)
definicion_cualificado: ""      # opcional: texto; no cambiarla con campañas activas
umbral_no_compensa: 0           # opcional: ahorro neto anual mínimo (€) para el veredicto del diagnóstico
---
```

- Los campos marcados «opcional» pueden faltar: ninguna herramienta falla sin ellos. `capacidad`,
  `coste_vender_por_venta`, `etapa_objetivo_cl`, `definicion_cualificado` y `umbral_no_compensa` salen del playbook de
  consultoras (`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §3.6, §3.3, §6 y §4.3).
- `mercados` lo usa `economia.py --cliente` para la tasa por ubicación que Meta cobra encima del gasto (ES, FR e IT
  3 %; UK o GB 2 %; AT y TR 5 %; el resto 0 %). Con varios mercados de tasa distinta aplica la mayor y avisa; vacío o
  ausente, 0 % y lo dice. `--fee-pais` manda sobre la ficha.
- `meta.waba` y `meta.dataset_mensajeria` los usa `capi.py` en mensajería: si falta `dataset_mensajeria`, usa
  `dataset`. `meta.instagram` solo cuenta si es numérico.

**Cuerpo de la ficha (secciones que leen herramientas o skills)**
- **Negocio**: incluye una línea `Playbook: meta-ads-kb/14-playbooks/<archivo>.md`.
- **Economía**: tabla `| Métrica | Break-even | Target | Fuente o supuesto |`, una fila por evento o etapa.
  `reglas_meta.py` toma el CPA objetivo de la columna Target de la fila del evento (y, si está vacía, el break-even con
  aviso). Entiende importes como «1.200,50 €».
- **Afirmaciones aprobadas** (bajo «Reglas propias del cliente»), la única fuente de cifras y citas de clientes para
  `/brief-creativo`, `redactor-anuncios` y `revisor-politicas`:

  ```markdown
  ## Afirmaciones aprobadas
  | Afirmación (texto exacto) | Fuente | Medida o estimada | Aprobada (fecha · por quién) | Caduca | Uso |
  |---|---|---|---|---|---|
  ```
- **Audiencias** (antes de «Notas y aprendizajes clave»), el inventario que mantienen `/audiencias` y
  `/anuncios-por-etapa`:

  ```markdown
  ## Audiencias
  | Audiencia | ID | Uso (incluir o excluir, en qué conjuntos) | Origen y actualización |
  |---|---|---|---|
  ```

Lectura en Python: `herramientas/_comun.py` expone `leer_ficha(slug: str) -> dict`. Si la cabecera falta o está mal,
lanza `FichaInvalida` con un mensaje que dice qué campo arreglar. Los hooks usan su propio parser mínimo (solo
biblioteca estándar) sobre el mismo formato. Subconjunto de YAML: claves, anidación con dos espacios y sin listas.
Un comentario al final de la línea (` # …`, con un espacio delante) se descarta, también detrás de un valor entre
comillas.

## 4. Estado y fases: `clientes/<slug>/estado.md`

```markdown
---
fase: F1                        # F0..F6
actualizado: 2026-11-09
---
- [x] F0.economia — Break-even y target en la ficha (verifica: archivo)
- [ ] F1.dataset — Dataset con el evento principal recibiendo datos (verifica: mcp)
```

- Cada línea: `- [ ]` o `- [x]`, un id `F<n>.<clave>`, ` — `, el texto y `(verifica: mcp|ghl|stripe|archivo|usuario)`.
- La lista canónica de ids está en `plantillas/cliente/estado.md`.
- La fase actual es la primera con ítems sin marcar.
- Ids de la segunda ola (texto de referencia; manda la plantilla):
  - `F0.iman` — Imán de entrada diseñado y probado con `/iman-de-leads` (verifica: archivo). Opcional.
  - `F3.prueba` — Al menos 1 caso con permiso y afirmaciones aprobadas, o un socio con derechos firmados (verifica:
    archivo).
  - `F5.reglas` — Reglas automáticas del OS creadas y revisadas tras el modo sombra (verifica: archivo). Se comprueba
    con las filas `Nivel = regla` del change log.

## 5. Change log: `clientes/<slug>/change-log.md`

Tabla con estas columnas exactas:

`| Fecha/hora | Quién | Nivel | Objeto (ID) | Cambio (de → a) | Motivo / hipótesis | Métrica de éxito | Fecha de evaluación | Resultado |`

- `Fecha/hora`: `AAAA-MM-DD HH:MM`.
- `Quién`: `operador-meta (aprobado por <operador>)` en escrituras del OS, `operador-meta (<herramienta>.py)` en las
  filas que imprimen las herramientas, `usuario en Ads Manager (verificado por operador-meta)` en lo que se crea a mano
  (anuncios de colaboración, publicaciones existentes) y `Meta (plataforma)` en restricciones y cambios de plataforma.
- `Nivel` ∈ `cuenta | campaña | conjunto | anuncio | creatividad | audiencia | formulario | regla | dataset | catalogo | crm`:
  - `crm`: workflows y etapas del CRM que afectan a la señal o al seguimiento (`/seguimiento-leads`); no es una
    escritura en Meta;
  - `regla`: reglas automáticas de Meta (`reglas_meta.py`, `/reglas-automaticas`);
  - `formulario`: formularios instantáneos (`formularios_meta.py`);
  - `audiencia`: audiencias de lista de clientes (`audiencias_meta.py`, MCP).
- `Objeto (ID)` contiene el ID numérico de Meta cuando existe.
- `Fecha de evaluación`: `AAAA-MM-DD`.
- `Resultado` vacío = evaluación pendiente.

## 6. Registro creativo: `clientes/<slug>/registro-creativo.csv`

Cabecera exacta (UTF-8, coma, una fila por `ad_id`):

```
ad_id,nombre,fecha,campana,conjunto,angulo,concepto,formato,hook,via,identidad,ruta_creativo,gasto,impresiones,hook_rate,hold_rate,ctr,cpm,resultado_meta,coste_resultado_meta,leads,cualificados,citas,shows,pruebas,activaciones,clientes_pago,cash,coste_cita,coste_venta,n_suficiente,veredicto,fecha_veredicto,motivo
```

- `via` ∈ `ia|propio|hibrido|estatico|""`.
- `identidad` ∈ `pagina|colaboracion|""`. Separa las dos versiones de una misma pieza (Página y anuncio de colaboración),
  que comparten nombre y `utm_content`: solo las distingue el `ad_id`. Mientras `registro_creativo.py` no la rellene
  sola, sale de la tabla de identidades del LEEME.
- `veredicto` ∈ `ganador|perdedor|sin-datos|en-test|""`. Un `motivo` que empieza por `manual:` bloquea el recálculo.
- Los números van con punto decimal, sin símbolo de moneda. Porcentajes de 0 a 100.

**Piezas y LEEME**
- Cada pieza vive en `clientes/<slug>/creativos/<nombre-base>/` (el nombre del anuncio sin `_h<n>[-c<n>]`) con un
  `LEEME.md` (plantilla: `.claude/skills/producir-video/plantilla-leeme.md`). Los archivos se llaman
  `<nombre-base>_h<n>[-c<n>]_<9x16|4x5|1x1>.<mp4|png>`.
- Líneas con formato fijo que leen herramientas y hooks:
  - `- **Estado:** borrador|listo|publicado|descartado`;
  - `- **Veredicto de políticas:** <valor> · AAAA-MM-DD · <quién>` (lo escribe `revisor-politicas`). Solo cuenta la
    línea al principio de línea y fuera de comentarios HTML. Valores:

    | Valor | Qué hace `control_publicacion` |
    |---|---|
    | `OK` | Deja pasar |
    | `OK con cambios aplicados` | Deja pasar |
    | `OK con cambios` (hay cambios sin aplicar) | Pide confirmación |
    | `pendiente` | Pide confirmación |
    | `NO publicar` | Bloquea (también `NO publicar (motivo)`) |

    Cualquier otro texto cuenta como `pendiente`.
  - `- Veredicto crítico: PUBLICAR | ARREGLAR | DESCARTAR | pendiente`, bajo «Calidad» (lo escribe
    `critico-creativo`; `operador-meta` no publica una pieza con `DESCARTAR`).
  - Opcional, bajo «Ángulo» (`/organico-a-anuncios`):
    `- **Origen orgánico:** <red> · <publicacion-existente|clip> · <permalink o archivo> · publicado <AAAA-MM-DD> · <ID>`.
    Una pieza con `publicacion-existente` no tiene archivos 9:16 ni 4:5: se publica con la publicación original.
  - El bloque de QA de cutkit va entre `<!-- cutkit:qa -->` y `<!-- /cutkit:qa -->`; `ck anuncio` solo reescribe ese
    bloque.
- Sección opcional al final del LEEME, `/casos-y-creadores` (B13). Dice con qué identidad y qué prueba se publica; la
  línea `Origen orgánico` dice de dónde sale la pieza. Son compatibles:

  ```markdown
  ## Prueba social y derechos
  - **Identidad:** pagina | colaboracion (socio: cliente | experto | creador | partner | fundador)
  - **Prueba:** caso-real | experto | creador | ninguna
  - **Caso o socio:** investigacion/casos/<caso>/caso.md | alias · **Permiso firmado:** privado/… (ruta, sin copiar datos)
  - **Derechos hasta:** AAAA-MM-DD · canales · ediciones permitidas · IA: no
  - **Permiso en Meta:** codigo | cuenta | mismo-negocio | no aplica · estado: pendiente | aprobado
  | ad_id | Identidad | Socio (alias) | Cabecera (ambas | una) | Publicación existente o contenido nuevo |
  |---|---|---|---|---|
  ```

  Con `- **Identidad:** colaboracion`, la pieza no se sube con la Página: el alta es guiada en Ads Manager
  (`/casos-y-creadores`, `publicar-colaboracion.md`), en pausa, y `operador-meta` la verifica en solo lectura. Los
  datos personales del socio (contratos, permisos, contactos) solo van en `privado/`; fuera, alias.

**Carpetas de `creativos/`**
- Lotes: `creativos/_lotes/<AAAA-MM-DD>_<lote>/lote.md` (+ `briefs/`). Revisiones sueltas:
  `creativos/_revisiones/<AAAA-MM-DD>_<tema>.md`. Fotogramas: `creativos/_fotogramas/<ad_id>/`.
- Las carpetas que empiezan por `_` o `.` no son piezas.
- Cola de producción = piezas cuyo `LEEME.md` dice `borrador` o `listo`. Una carpeta sin `LEEME.md` (por ejemplo,
  `creativos/<fecha>-estudio/` de `estudio-creativo`) no cuenta.

**Elementos creativos: `clientes/<slug>/datos/elementos-creativos.csv`**

Una fila por `ad_id`, cabecera exacta:

```
ad_id,nombre,soporte,relacion_aspecto,duracion_s,ritmo,persona,quien_habla,primer_fotograma,texto_0s,gancho,audiencia_nombrada,consciencia,estructura,demo,cifra,menciona_ia,filtro,prueba_social,cta,subtitulos,acabado,tono,huella_visual,fuente_visual,etiquetado_por,fecha_etiquetado,notas
```

- Valores en minúsculas y kebab sin acentos. El esquema y las definiciones los da
  `elementos_creativos.py etiquetas esquema`.
- Comodines: `duda` (no cuenta para ese elemento) y `no-aplica` (elementos de vídeo en estáticos y carruseles).
- Columnas automáticas: `soporte`, `relacion_aspecto`, `duracion_s`, `huella_visual` (dHash de 16 hex) y
  `fuente_visual` (`local|api-video|api-miniatura`).
- Solo se escribe con `elementos_creativos.py etiquetas poner`, que valida antes. Ninguna columna lleva datos
  personales.
- Análisis en `datos/analisis-creativo/<fecha>_{elementos,diversidad,suministro}.json`; informe en
  `informes/analisis-creativo/<fecha>.md`. Todo es asociación, nunca causa.

## 7. Nomenclatura (`herramientas/nomenclatura.py`)

| Nivel | Formato | Ejemplo |
|---|---|---|
| Campaña | `<MERCADO>_<OBJETIVO>_<PROPOSITO>_<PUJA>` (mayúsculas; el mercado con guiones si son varios: `ES-MX`) | `ES_LEADS_ADQ_HV` |
| Conjunto | `<AUDIENCIA>_<EVENTO>` (mayúsculas, guiones dentro de cada parte) | `BROAD-A+_LEAD` |
| Anuncio | `<AAAAMMDD>_<angulo>_<concepto>_<formato>_<hook>` | `20261110_tiempo-perdido_demo-antes-despues_demo_h2` |

En el anuncio:
- `angulo` y `concepto` van en minúsculas kebab.
- `formato` ∈ `ugc|founder|demo|testimonio|podcast|estatico|carrusel|meme|otro`.
- `hook` = `h<n>`, con un sufijo opcional `-c<n>` para el cuerpo.
- Las piezas de un caso real llevan el concepto `caso-<caso>`, con `<caso>` = `<sector>-<palanca>` y nunca el nombre
  del cliente.

Listas cerradas de la herramienta: objetivos `LEADS, SALES, TRAFFIC, AWARENESS, ENGAGEMENT, APP`; pujas
`HV, VAL, CC, BC, ROAS`. `parsear_anuncio` tolera el sufijo de copia de Meta («- Copia»); `validar` no.

Otros nombres que fija el OS:
- Reglas automáticas: `PROTECT_OS_<regla>_<umbral>[-sombra]` (pausan) y `ALERT_OS_<regla>` (avisan). La marca `_OS_`
  hace la idempotencia de `reglas_meta.py crear` (por nombre).
- Audiencias de lista: `ETAPA_<SEGMENTO>_<FUENTE>` y, para excluir, `EXCL_<…>`.
- Formularios instantáneos: un formulario publicado no se edita; la versión nueva lleva sufijo `_v2`, `_v3`…
- Ediciones de un webinar o taller: `<AAAA-MM-DD del taller>_webinar-<tema>`.

API:
- `parsear_anuncio(nombre: str) -> dict | None` → claves `fecha` (`date`), `angulo`, `concepto`, `formato`, `hook`.
- `validar(nivel: Literal["campana","conjunto","anuncio"], nombre: str) -> tuple[bool, str]` → mensaje con el motivo
  y una sugerencia.
- `generar_anuncio(fecha: date, angulo: str, concepto: str, formato: str, hook: int, cuerpo: int | None = None) -> str`
  → normaliza (minúsculas, sin acentos, kebab).

CLI: `python3 -I herramientas/nomenclatura.py validar <nivel> "<nombre>"` → sale con 0 o 1 e imprime el mensaje.
`generar` crea el nombre del anuncio. Al cruzar archivos con nombres de anuncio, los sufijos de formato (`_9x16`,
`_4x5`, `_1x1`, `_16x9`) no cuentan.

## 8. Registros (`logs/`, JSONL, una línea por evento)

| Archivo | Lo escribe | Campos |
|---|---|---|
| `logs/meta-mcp.jsonl` | `meta_guard` | `ts, evento, tool, agente, session, input`; en PostToolUse, además `resultado` (`ok\|error`) e `ids` |
| `logs/cambios.jsonl` | `meta_guard`, `ghl_guard`, `stripe_guard`, `meta_ads.py`, `capi.py`, `reglas_meta.py`, `formularios_meta.py`, `audiencias_meta.py` | `ts, session, sistema (meta\|ghl\|stripe\|capi), via (mcp\|cli), accion, entidad_id, cliente, detalle` — solo escrituras ejecutadas |
| `logs/changelog.jsonl` | hook PostToolUse sobre Write/Edit de `clientes/*/change-log.md` (`registro_obligatorio`) | `ts, session, cliente` |
| `logs/ghl-mcp.jsonl` · `logs/stripe-mcp.jsonl` | sus guardas | todas las llamadas: `ts, evento, tool, agente, session, operacion, [metodo], input` |
| `logs/hooks.jsonl` | todos los hooks (`_lib.ejecutar`) | Una fila por decisión: `ts, hook, evento, tool, session, agente, decision, motivo`. Una fila por fallo interno: `decision: "error"`, `error` y `traza`. `/doctor` la lee para ver hooks rotos |
| `logs/motor.jsonl` | `motor_guard` | órdenes del motor y de cutkit, y su decisión |
| `logs/notificaciones.jsonl` | `notificar.py` | `ts, canal, archivo, ok, mensajes, detalle`, en ese orden (los lanzadores buscan la subcadena `"archivo": "informes/diario/<hoy>.md", "ok": true`). Nunca contenido ni claves |
| `logs/brief-diario-AAAA-MM.log` | `brief.sh`, `brief.ps1` | Inicio, salida de `claude`, código de salida, envío o aviso |
| `logs/brief-diario-launchd.log` | launchd | Lo que falla antes de arrancar `brief.sh` (p. ej. permisos de macOS) |
| `logs/brief-diario.ultimo` | lanzadores e instaladores | Fecha del último intento, o `forzar` para que la próxima ejecución no espere |
| `logs/copias-migracion/<ts>_<id>/` | `scripts/migrar.py` | Copia de lo que va a cambiar una migración |

Acciones de `cambios.jsonl` por la vía `cli` (`sistema: meta` salvo que se diga):
- `meta_ads.py`: `crear_campana`, `crear_conjunto`, `crear_creatividad`, `crear_anuncio`, `pausar`, `activar`,
  `presupuesto`.
- `reglas_meta.py`: `crear_regla`, `desactivar_regla`, `reactivar_regla`.
- `formularios_meta.py`: `crear_formulario` (`leads` no se registra: no escribe en Meta).
- `audiencias_meta.py`: `crear_audiencia`, `reemplazar_audiencia`, `anadir_audiencia`, y el sufijo `_parcial` si el
  envío se corta a mitad.
- `capi.py` (`sistema: capi`): `enviar_prueba`, `enviar_real`; en mensajería el detalle lleva `mensajeria=<canal>`.

Reglas:
- `ts` en ISO 8601 local con segundos.
- `session` = `CLAUDE_SESSION_ID`, que exporta `contexto_sesion` (en `CLAUDE_ENV_FILE`) para que la CLI firme sus filas.
- Nunca se guardan tokens ni datos personales: todo pasa por `limpiar()` (hooks) o `anonimizar()` (`_comun`), y los
  valores de email o teléfono se sustituyen por `***`.
- `logs/meta-mcp-cambios.jsonl` (del sistema de origen) ya no se escribe: lo sustituye `cambios.jsonl`. Si existe en una
  instancia, es un dato del usuario y no lo borra nadie.

## 9. CLI de las herramientas

Todas se ejecutan como `python3 -I herramientas/<x>.py <subcomando> ...`:
- `--cliente SLUG` lee la ficha.
- `--json` saca la salida en JSON.
- `--sin-archivos` (en las lecturas que guardan CSV) no escribe nada: es lo que usa el brief diario.
- Códigos de salida: `0` ok (aunque haya avisos), `1` error del usuario, `2` error de configuración (ficha, token,
  credencial que falta: dice qué variable, nunca su valor).
- Ninguna lectura pregunta nada (`input()`): todas funcionan sin nadie delante.
- Las credenciales salen de `.env` en la raíz, cargado por `_comun.cargar_entorno()`. Variables por cliente:
  `<VAR>_<SLUG_EN_MAYUSCULAS_CON_GUION_BAJO>`, con la variable global como alternativa.
- Versión de la Graph API: la de `VERSION` en `meta_ads.py` y `capi.py` (hoy `v27.0`, desde el 2026-11-10), y el valor
  por defecto de `_comun.py` y `meta_guard.py`; `META_API_VERSION` la cambia. Se cambia a la vez en los cuatro sitios,
  nunca en una herramienta sola.

| Herramienta | Subcomandos | Credenciales |
|---|---|---|
| `estado.py` | `resumen [--cliente] [--fecha AAAA-MM-DD] [--todos] [--json]` → `{"fecha":..,"clientes":[{"slug","fase","pendientes":[id],"evaluaciones_vencidas":[{"fecha","objeto","cambio"}],"informe_semanal_pendiente":bool,"brief_hoy":bool,"cola_produccion":int}]}` | — |
| `meta_ads.py` | `cuentas`, `activos`, `campanas`, `vigente`, `anuncios [--desde --hasta] [--mes] [--campana\|--campana-id] [--por-dia] [--por-pais] [--evento] [--salida] [--sin-archivos]`, `eventos`, `creatividades`, `crear <plan> [--simular]`, `pausar`, `activar <ids>\|--plan … --confirmo`, `presupuesto <id> <importe> --confirmo` (más `--cliente`). En el plan, `campana.id` y `conjuntos[].id` apuntan a una campaña o un conjunto existentes, que no se cambian | `META_TOKEN` (usuario del sistema), `META_APP_SECRET` opcional |
| `ghl.py` | `contactos`, `oportunidades`, `citas`, `pagos`, `por-anuncio --desde --hasta [--campo-anuncio ID] [--cualificado TEXTO]`, todas con `--json` y `--sin-archivos` | `GHL_TOKEN`, `GHL_LOCATION` |
| `stripe_datos.py` | `clientes`, `suscripciones`, `pagos`, `por-anuncio --desde --hasta`, todas con `--json` y `--sin-archivos` | `STRIPE_KEY` (restringida, de lectura; rechaza `sk_`), `STRIPE_API_VERSION` opcional |
| `capi.py` | `construir`, `hashear [--tipo] <valor>` o `hashear --archivo <csv> [--columnas] --salida <privado/…> [--conservar] [--sobrescribir]`, `validar <payload>`, `origen <webhook> [--salida privado/…] [--json]`, `enviar --test-code CODE` (sin código de prueba exige `--real --confirmo`). En mensajería: `construir --canal whatsapp\|messenger\|instagram --etapa <§16> [--cualifica-en llamada\|asistio\|propuesta] [--desde-webhook <json>] [--cliente] [--waba --ctwa-clid \| --pagina --psid \| --ig-cuenta --igsid] [--entrada-conversacion]`; un lote no mezcla mensajería y web | `META_CAPI_TOKEN`; `META_CAPI_MENSAJERIA_TOKEN` opcional (si falta, usa `META_CAPI_TOKEN` y avisa) |
| `registro_creativo.py` | `actualizar --meta <csv> [--ghl <csv>] [--stripe <csv>]`, `sin-nomenclatura` | — |
| `embudo.py` | `cohortes --por semana\|anuncio [--modelo]` | — |
| `render.py` | `png <plantilla.html> --datos <json> --formatos 1x1,4x5,9x16 --salida <dir>`, `pdf <html> --salida <pdf>`. Se lanza con `uv run --extra render python -I herramientas/render.py …` | — |
| `editar_video.py` | `info`, `cortar`, `subtitular`, `reformatear`, `texto-hook` | — |
| `doctor.py` | `[--json]` → lista de comprobaciones `{id, ok, detalle, arreglo}` | — |
| `notificar.py` | Ver §15 | Ver §15 |
| `reglas_meta.py` | `listar [--cpa N]`, `proponer [--cpa N] [--evento X] [--madurez D] [--multiplicador K] [--activo] [--campanas IDs] [--avisar IDs] [--salida RUTA]` → `clientes/<slug>/planes/reglas-<fecha>.json` (`formato: reglas-meta-os/1`), `crear <json> [--simular [--pasos]] [--avisar IDs] [--confirmo]`, `pausar <id>… --confirmo`, `reactivar <id>… --confirmo`, `historial [--dias 7] [--todas]`, `destinatarios` (más `--cliente` y `--json`) | `META_TOKEN` (usuario del sistema), `META_APP_SECRET` opcional |
| `elementos_creativos.py` | `fotogramas [--ad ID…] [--video RUTA] [--api] [--descargar-video] [--cuadricula] [--max N]`, `etiquetas esquema\|preparar [--todos]\|pendientes\|poner (--ad ID campo=valor… \| --archivo <json>) [--por QUIEN]\|validar`, `analizar [--capa C] [--dias-madurez 14] [--fecha] [--guardar]`, `retencion --meta <csv>`, `diversidad [--umbral 0.8] [--umbral-visual 10] [--guardar]`, `suministro [--gasto-mensual X \| --gasto-diario X \| --meta CSV] [--coste-objetivo X] [--capa C]` (más `--cliente` y `--json`). Escribe en `datos/`, `datos/analisis-creativo/` y `creativos/_fotogramas/` | `META_TOKEN` solo con `fotogramas --api` (solo GET) |
| `paginas.py` | `generar <landing\|diagnostico\|reserva\|gracias\|webinar\|todas> --config <json> --salida <dir> [--cliente SLUG \| --marca RUTA] [--en-linea] [--fragmento-ghl] [--json]`, `validar <carpeta> [--json]`, `probar --config <json> [--respuestas <json>] [--json]`. Solo archivos locales; nunca borra. `1` también si `validar` encuentra errores | — |
| `formularios_meta.py` | `listar`, `ver <id>` (con auditoría), `crear <json> [--simular] [--confirmo] [--sin-logica]`, `guia <json> [--salida <md>]`, `leads <id> [--desde] [--hasta] [--encaje <json>] [--horario 9-20] [--sin-archivos]` (más `--cliente`, `--pagina` y `--json`). `leads` → `privado/formulario-<id>_<desde>_<hasta>.csv` y agregados en `datos/` | `META_TOKEN_PAGINA` o `META_TOKEN` (usuario del sistema con la Página asignada; `pages_manage_ads`, `leads_retrieval`), `META_APP_SECRET` opcional |
| `audiencias_meta.py` | `listar [--buscar TXT]`; `etapas --archivo <csv en privado/> [--contactos] [--mapa "Etapa=segmento,…"\|"Nombre=propio:<segmento>"] [--pipeline] [--columnas] [--prefijo] [--pais] [--control 0.2] [--control-en] [--semilla] [--agrupar] [--bajas] [--por-anuncio] [--sin-archivos] [--sobrescribir] [--fecha]` → `privado/audiencias/<fecha>/` (y con `--por-anuncio`, `datos/etapas-por-anuncio_<fecha>.csv`); `crear <nombre> [--descripcion] [--retencion 1..180] [--etiqueta] [--simular] --confirmo`; `sincronizar <id> --archivo <csv hasheado en privado/> [--reemplazar] [--exclusion] [--simular] --confirmo`; `medir --archivo <exportación> (--manifiesto … \| --etiqueta-grupo … --etiqueta-control …) [--segmento] [--exito]` (más `--cliente` y `--json`) | `META_TOKEN` (usuario del sistema con `ads_management`), `META_APP_SECRET` opcional |

**Formatos de salida que leen otras herramientas** (porcentajes de 0 a 100, punto decimal, sí/no como 1/0, fechas
`AAAA-MM-DD`; los alias tolerantes de `registro_creativo.py` y `embudo.py` aceptan además nombres en español e inglés y
exportaciones de Ads Manager):

| Salida | Archivo | Columnas |
|---|---|---|
| `meta_ads.py anuncios` | `datos/meta-anuncios[_<campaña>]_<desde>_<hasta>[_por-pais][_por-dia].csv` | `ad_id, anuncio, campana_id, campana, conjunto_id, conjunto, desde, hasta, pais, gasto, impresiones, alcance, frecuencia, cpm, clics_enlace, ctr, vistas_landing, vistas_3s, thruplay, hook_rate, hold_rate, video_p25, video_p50, video_p75, video_p95, video_p100, reproducciones, vistas_2s_continuas, tiempo_medio_s, retencion_p25, retencion_p50, retencion_p75, retencion_p95, retencion_p100, curva_retencion, evento_resultado, resultado_meta, coste_resultado_meta, citas_meta` |
| `ghl.py por-anuncio` | `datos/ghl-por-anuncio_<desde>_<hasta>.csv` | `ad_id, utm_content, campana, leads, cualificados, citas, shows, clientes_pago, cash, valor_ganado, moneda` |
| `ghl.py por-anuncio` | `privado/leads-ghl_<desde>_<hasta>.csv` (uno por lead) | `contact_id, fecha, ad_id, utm_content, utm_campaign, cualificado, cita, show, venta, cash, fecha_cash` |
| `stripe_datos.py por-anuncio` | `datos/stripe-por-anuncio_<desde>_<hasta>.csv` | `ad_id, utm_content, campana, registros, pruebas, clientes_pago, cash, reembolsos, mrr, moneda` |
| `stripe_datos.py por-anuncio` | `privado/clientes-stripe_<desde>_<hasta>.csv` (uno por cliente) | `customer_id, fecha, ad_id, utm_content, utm_campaign, trial, fecha_primer_pago, cash, fecha_cash, mrr, fecha_baja` |

- Retención de `meta_ads.py anuncios`: `hook_rate` = vistas de 3 s ÷ impresiones × 100; `hold_rate` = ThruPlays ÷
  vistas de 3 s × 100; `retencion_pXX` = `video_pXX_watched_actions` ÷ vistas de 3 s × 100; `curva_retencion` = valores
  de `video_play_curve_actions` separados por «|». Si Meta rechaza esos campos (error 100), las columnas salen vacías,
  no a 0.
- Los detalles de las órdenes sueltas en `privado/` se llaman `ghl-<orden>_…` y `stripe-<orden>_…`, para que el glob
  `leads*.csv` de `embudo.py` no los recoja.

Reglas de salida de datos:
- Las salidas con datos personales van a `clientes/<slug>/privado/`.
- Los agregados por anuncio van a `clientes/<slug>/datos/`.

## 10. Hooks

- Solo biblioteca estándar y **Python 3.8 o superior**: los hooks no corren con `uv`, sino con el Python del sistema, y
  el de las herramientas de línea de comandos de macOS es el 3.9. (Las herramientas y los scripts piden 3.10+.)
- Leen el JSON de stdin y responden con el formato de hooks de Claude Code (`hookSpecificOutput.permissionDecision`
  `allow|ask|deny` + `permissionDecisionReason`, o `decision: block` en Stop).
- Nunca imprimen secretos.
- Si su propia lógica falla, dejan pasar y lo registran en `logs/hooks.jsonl`. Los permisos de `settings.json` son la
  red de seguridad.
- `.claude/settings.json` lo mantiene el bloque B3 (en la integración, la integración).

**Lanzador.** Cada hook se registra en `settings.json` con este comando, en una sola línea y sin script intermedio (así
no hay problemas de CRLF):

`python3 -I "$CLAUDE_PROJECT_DIR/.claude/hooks/<hook>.py" || python -I "…/<hook>.py" || py -3 -I "…/<hook>.py"`

- Funciona en Mac, en Linux y en Windows con Git Bash, que es la shell con la que Claude Code ejecuta los hooks. En
  Windows a veces solo existe `python` o `py`, y `python3` es el aviso de la Microsoft Store, que sale con 9009 sin leer
  stdin. El intérprete siguiente recibe la entrada intacta.
- Con un Python más antiguo que el 3.8, el hook sale con 3 sin leer stdin y el lanzador prueba el siguiente.
- Sin ningún Python, el comando sale con 127. Es un error no bloqueante: mandan los permisos de `settings.json`.
- Los hooks solo salen con 0 (nunca con 2) y escriben JSON en ASCII, para que no se rompa en consolas de Windows.
- Timeouts: 10 s por defecto, 15 s para `contexto_sesion` y 30 s para `meta_guard` (consulta Graph si hay
  `META_TOKEN`). Ningún hook espera entrada, así que el modo `claude -p` / `dontAsk` no se queda colgado.
- Windows sin Git Bash (PowerShell puro) no ejecuta los hooks: `/doctor` lo avisa.

**Escrituras por Bash que vigilan los hooks** (además del MCP): `meta_ads.py crear|activar|presupuesto|pausar`,
`reglas_meta.py crear|pausar|reactivar`, `formularios_meta.py crear`, `audiencias_meta.py crear|sincronizar` (sin
`--simular`: solo `operador-meta` y con `ask`), `capi.py enviar` (`eventos_guard`) y las órdenes de pago del motor y de
cutkit (`motor_guard`, §14). `formularios_meta.py leads` pide confirmación en `settings.json` porque descarga datos
personales.

**Sub-cuentas.** En `allow` el comodín solo vale tras `mcp__<servidor>__`: el nombre del servidor no admite glob. Por
eso `/conectar`, al crear `ghl-<slug>` o `stripe-<slug>`, añade a `.claude/settings.local.json` las reglas explícitas
de ese servidor (lecturas en `allow`; en Stripe, escrituras y pagos en `deny`; en GHL, ninguna regla para
`execute_operation`, que va en `ask` en `settings.json` (siempre pregunta) y que `ghl_guard` bloquea en mensajes, borrados y pagos, y en subagentes salvo lecturas reconocidas).

## 11. Skills, agentes y workflows

**Skill**
- Cabecera:
  - `name` (igual que la carpeta);
  - `description` (español; qué hace y cuándo usarla; ≤ 350 caracteres; sin solaparse con otras);
  - `argument-hint`;
  - `disable-model-invocation: true` en las skills que escriben en Meta, GHL o Stripe, gastan dinero o actualizan el
    sistema: `lanzar-campana`, `ejecutar-cambio`, `publicar-anuncios`, `producir-video`, `actualizar`, `menu`,
    `reglas-automaticas`, `formulario-instantaneo`, `anuncios-por-etapa`;
  - `allowed-tools` (opcional, lista YAML): las herramientas que la skill puede usar sin pedir permiso durante su turno.
    Hace falta en las que corren sin nadie delante (`brief-diario`: lecturas, escritura solo en las carpetas de
    informes y `notificar.py enviar`).
- Cuerpo: pasos numerados que citan los marcos de `meta-ads-kb/` por ruta. Los agentes y herramientas se citan por su
  nombre de contrato. Los archivos de apoyo (plantillas, guiones, checklists) van dentro de la carpeta de la skill.

**Agente**
- Cabecera: `name`, `description` (con «Úsalo para…» y lo que no hace y quién lo hace), `tools` (lista explícita, nunca
  el servidor MCP entero), `model` (`inherit` o `sonnet`; ver el diseño §5.11).
- Ningún agente lleva `Agent` ni `AskUserQuestion`: la orquestación vive en las skills y los workflows.
- El formato o la ruta que pida quien llama (skill o workflow) manda sobre la entrega del agente; el método y los
  límites no cambian.

**Workflow**
- Se lanza siempre desde su skill («modo profundo»), después de avisar del coste aproximado y de recibir el sí.
- `meta` es un literal puro con `name` (igual que el archivo), `description` y `phases`. Sin `require`, `import` ni
  `process`.

## 12. Idioma y contenido

- Español de España, tutear, frases claras.
- Fechas `AAAA-MM-DD`.
- Etiquetas de evidencia de la KB: `[OFFICIAL META]`, `[EMPIRICAL]`, `[STRONG INFERENCE]`, `[HYPOTHESIS]`,
  `[CONTESTED]`. Fuera de Meta se admiten variantes como `[OFFICIAL — regulador]` u `[OFFICIAL — INE]`.
- Ningún dato personal ni de clientes reales:
  - ni rutas `/Users/...`;
  - ni IDs reales;
  - ni nombres de personas o marcas concretas.

  Los ejemplos usan empresas ficticias del público objetivo: «Acme Automations» (agencia de automatización), «Nimbo»
  (SaaS B2B) y «Clínica Sonrisa» (cliente local de una agencia). Los socios y creadores van por alias (`creador-a`,
  `experta-a`).
- Público: consultoras y agencias de IA y automatización, y SaaS.

## 13. Tests

- `pytest` en `tests/` (`tests/herramientas/`, `tests/hooks/`, `tests/modulos/`, `tests/scripts/`), sin red: el HTTP se
  simula.
- Fixture compartida `instancia` en `tests/conftest.py`: instancia temporal con el cliente ficticio `acme` (topes
  100/300, CRM ghl), `META_ADS_OS_RAIZ` y `CLAUDE_PROJECT_DIR` apuntando a ella y `_comun` recargado. No se modifica:
  si hace falta otra fixture, cada bloque la crea en su propio `conftest.py` de subcarpeta.
- Se ejecutan con `uv run pytest`.
- Cada herramienta y cada hook nuevo tiene tests.
- `scripts/validar.py` comprueba:
  - las cifras: 50 skills, 20 agentes, 10 hooks, 5 workflows, 25 herramientas y 2 estilos, y que `docs/catalogo/`
    documenta cada pieza;
  - las cabeceras;
  - los enlaces a la KB;
  - que todo nombre citado en CLAUDE.md exista;
  - que no hay fugas (rutas `/Users/`, `act_` con 10 o más dígitos fuera de ejemplos, emails, tokens).
- **Evals del criterio** (`scripts/evals.py`, casos en `tests/evals/casos/`): `--simular` corre dentro de la suite, sin
  red ni gasto. La ejecución real (`claude -p`) gasta uso de Claude y solo se lanza antes de un release, con el sí de
  quien publica. Proceso, formato de los casos y coste: [`docs/desarrollo/evals.md`](evals.md). Los resultados
  (`tests/evals/resultados/`) no se versionan.

## 14. Módulos de vídeo

Los dos son opcionales y se instalan con `/motor instalar` (el motor) y `/producir-video` la primera vez (cutkit).
Cada uno es un proyecto uv independiente con su propio entorno, creado en el ordenador del usuario (nunca se versiona
un entorno: no se pueden mover entre carpetas).

| Módulo | Orden | Python | Claves |
|---|---|---|---|
| `modulos/motor-ia/` | `uv run --project modulos/motor-ia motor <subcomando>` | ≥3.11 | `GEMINI_API_KEY` y las demás del usuario en el `.env` de la raíz |
| `modulos/cutkit/` | `uv run --project modulos/cutkit ck <subcomando>` | 3.12 | ninguna obligatoria |

- `MOTOR_MOCK=1` simula el motor sin gastar (para tests y para `/motor` en modo prueba). `MOTOR_DATA_DIR=<dir>` aísla
  la base de datos del simulado.
- El presupuesto global del guardián del motor por defecto es **5 $** en el producto. El usuario lo sube en la
  cabecera de `contexto/preferencias.md` (bloque `motor:` → `presupuesto_usd: 5`) o con `MOTOR_PRESUPUESTO_USD` en el
  `.env`, que tiene prioridad. El motor lee exactamente esa clave anidada. `motor status` dice el presupuesto restante y
  de dónde sale la cifra.
- Órdenes de pago del motor (las que `motor_guard` frena): `run`, `regen`, `demo`, `actor create`, `edit --yes`,
  `variant` con voz o idioma, los scripts de `modulos/motor-ia/scripts/` que llaman a modelos (`auto_produce.py`
  siempre) y los pasos de pago de `flow_style.py`. Gratis: `flow_style.py validar|plan|setup|check` y cualquier script
  con `--simular`.
- Opciones de pago de cutkit (también las frena `motor_guard`):
  - `ck anuncio … --subtitulos openai` (o `CK_ASR=openai` delante);
  - `ck run|qa … --judge`;
  - `ck run … --budget` mayor que 0;
  - cualquier `ck` precedido de `CK_MUSICA_IA=1` (música con Lyria).

  El resto de `ck` es local y gratis. `ck instalar --whisper` es gratis pero descarga unos 550 MB: se avisa antes.
- La marca de cada cliente para cutkit, `render.py`, `editar_video.py` y `paginas.py` vive en
  `clientes/<slug>/marca/` (`marca.json` + archivos). El producto no incluye ninguna marca real; el ejemplo es
  `plantillas/html/marca-ejemplo/` (Acme). Esquema de `marca.json`:

  ```json
  {
    "nombre": "Acme Automations",
    "colores": {"primario": "#1F4FD1", "secundario": "#0B1F3A", "acento": "#FFB020",
                "fondo": "#F7F8FB", "texto": "#0B1F3A", "texto_sobre_primario": "#FFFFFF"},
    "tipografias": {"titulos": {"familia": "Montserrat", "archivo": "", "peso": 800},
                    "texto":   {"familia": "Montserrat", "archivo": "", "peso": 500}},
    "logo": {"principal": "logo.png", "claro": "logo-claro.png"},
    "subtitulos": {"color": "#FFFFFF", "resaltado": "#FFB020", "contorno": "#000000", "mayusculas": false},
    "cta_por_defecto": "Reserva tu diagnóstico",
    "etiqueta_ia": "Imagen generada con IA"
  }
  ```

  - Rutas relativas a `marca/`. Para vídeo, el logo en PNG y la tipografía en TTF u OTF estática (una variable o una
    WOFF avisan y caen en Montserrat). Sin `archivo`, se usa la familia instalada o la de sistema.
  - `paginas.py` copia la tipografía a `recursos/` y avisa si no es `.woff2`.

## 15. Brief diario

**Qué es.** `/brief-diario [<slug>|todos] [programar|probar]`. Solo lectura. Funciona en interactivo y sin nadie
(`claude -p`), sin hacer preguntas.

**Contenido por cliente**
- semáforo;
- gasto frente al ritmo previsto;
- errores y rechazos;
- anomalías frente a la banda de ruido (`estadistica.py banda --observado`);
- señal del dataset en las últimas 24–48 h;
- cambios de la cuenta desde el último brief, incluidas las pausas de las reglas automáticas (`reglas_meta.py
  historial`, con token);
- leads, citas y pruebas de ayer y **del alta a la cita** (`horas_hasta_cita_mediana` de `ghl.py por-anuncio`, 7 días)
  si hay GHL o Stripe. `ghl.py` no lee los mensajes salientes, así que el speed to lead de verdad se mira en GHL;
- evaluaciones que vencen hoy (`estado.py`);
- qué NO tocar;
- 1–3 acciones, solo si hay algo roto.

**Archivos**
- Por cliente: `clientes/<slug>/informes/diario/AAAA-MM-DD.md`. `estado.py` pone `brief_hoy: true` si existe el de
  la fecha. Empieza con esta cabecera YAML, que leen `/hoy` y `contexto_sesion` sin interpretar texto:

  ```yaml
  ---
  fecha: 2026-11-10
  cliente: acme-automations
  semaforo: ambar            # verde | ambar | rojo | sin-datos
  acciones: 0                # número de acciones (0 salvo en rojo)
  generado: 2026-11-10 08:03
  fuente_meta: mcp           # mcp | meta_ads.py | ninguna
  ventana_atribucion: 7d_click_1d_view
  ---
  ```

  Las cuatro primeras son obligatorias. `ambar`, no `amarillo`.
- Resumen global (lo que se envía): `informes/diario/AAAA-MM-DD.md` en la raíz de la instancia. Con un solo `<slug>`
  se envía el informe del cliente, para no pisar el resumen de la mañana.
- Si el método sistema no consigue enviar el brief, escribe `informes/diario/AAAA-MM-DD-aviso.md` y lo manda.
- Ni el archivo ni el mensaje llevan datos personales: solo IDs y agregados.

**Preferencias.** `contexto/preferencias.md` tiene una cabecera YAML (el mismo subconjunto que la ficha, legible con
`_comun.parsear_cabecera`):

```yaml
---
nivel: principiante             # principiante | intermedio | avanzado
estilo: profesor                # profesor | operador
brief:
  canal: telegram               # telegram | email | slack | ninguno
  hora: "08:00"
  clientes: todos               # todos | lista de slugs separada por comas
  programado_con: ""            # desktop | sistema | nube | "" (sin programar)
motor:
  presupuesto_usd: 5
---
```

**Credenciales (`.env`)**
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- Slack: `SLACK_WEBHOOK_URL`.
- Email: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USUARIO`, `SMTP_CLAVE`, `EMAIL_DESTINO`.
- Método sistema, solo si el lanzador no encuentra la sesión de Claude Code: `CLAUDE_CODE_OAUTH_TOKEN` (de
  `claude setup-token`, dura un año). Los lanzadores solo leen esa línea, sin mostrarla.

**`herramientas/notificar.py`**
- `enviar --archivo <md> [--canal telegram|email|slack|auto] [--asunto TEXTO] [--json]`:
  - `auto` usa `brief.canal` de las preferencias y, si no hay preferencias (la nube no tiene `contexto/`), el primer
    canal con credenciales completas (telegram, slack, email);
  - Telegram en HTML, troceado a 4096 caracteres;
  - solo envía `.md` de `informes/` o `clientes/<slug>/informes/` (nunca `privado/` ni `.env*`), y se niega si el
    archivo contiene algo con forma de clave.
- `probar [--canal] [--json]`: manda un mensaje de prueba.
- `telegram-chat-id [--guardar] [--json]`: lee `getUpdates` y dice el `chat_id` después de que el usuario escriba al
  bot; `--guardar` lo añade a `.env` sin leerlo ni mostrarlo.
- Solo envía al canal del propio operador. Salidas: `0` enviado (o canal `ninguno`), `1` uso, fallo de envío o clave
  detectada en el archivo, `2` falta configuración (dice qué variable, nunca su valor).

**Programación** (`/brief-diario programar`)
- **desktop (por defecto):** tarea programada de Claude Desktop.
- **sistema:** launchd en Mac, Programador de tareas en Windows o cron en Linux. Lanza
  `claude -p "/brief-diario todos"` en modo `dontAsk` con una lista explícita de herramientas de lectura,
  `notificar.py` y escritura solo en las carpetas de informes (`programacion/herramientas-permitidas.txt` y
  `herramientas-denegadas.txt`).
- **nube (ligero, experimental):** rutina de Claude Code. Solo lee Meta, GHL y Stripe y envía; no guarda archivos.
- Las plantillas y scripts de programación viven dentro de `.claude/skills/brief-diario/`.
- Permisos: `notificar.py` va en `allow`. Sin nadie delante, cualquier escritura se deniega. Ni GHL ni Stripe por MCP
  sin nadie: `ghl.py` y `stripe_datos.py` con `--json --sin-archivos`.

## 16. Embudo consultivo: etapas canónicas

Para consultoras, agencias y SaaS que venden soluciones con llamada y propuesta (ticket alto, pocos leads, ciclo de
semanas). Las usan la ficha, el pipeline de GHL, la CAPI (web y mensajería), las audiencias por etapa, el embudo y el
registro creativo.

**Esta es la tabla canónica de eventos: la única fuente de verdad.** El `event_name` se escribe exactamente así, con
sus mayúsculas, en el navegador, en el servidor y en el CRM. La usan tal cual `paginas.py`, `capi.py construir --etapa`
(`capi.EVENTO_ETAPA`), las plantillas de `plantillas/integraciones/`, las skills y las guías;
`tests/herramientas/test_capi.py` comprueba que esta tabla y `capi.py` coinciden.

| Id | Etapa | Evento a Meta (`event_name` exacto) | Mensajería | Notas |
|---|---|---|---|---|
| `lead` | Envía sus datos de contacto (formulario, paso de contacto del diagnóstico o mensaje) | `Lead` | `LeadSubmitted` | Web: navegador + servidor con el mismo `event_id`. Formulario instantáneo: el CRM lo manda como primera etapa |
| `diagnostico` | Completa el diagnóstico o la calculadora de entrada | `DiagnosticoCompletado` (personalizado) | — | Puede llevar `value` = valor esperado del lead `[HYPOTHESIS]`, nunca el ahorro bruto del cliente |
| `cualificado` | Pasa el filtro (reglas de la ficha o del comercial) | `LeadCualificado` (personalizado) | `QualifiedLead` | Candidato habitual a Conversion Leads |
| `llamada` | Agenda la llamada | `Schedule` | — | Por navegador con Calendly; con GHL, desde el CRM |
| `asistio` | Se presenta a la llamada | `LlamadaAsistida` (personalizado) | — | |
| `propuesta` | Recibe propuesta | `PropuestaEnviada` (personalizado) | — | |
| `ganado` | Firma | `Purchase` con `value` y `currency` | `Purchase` | Importe del proyecto, en la moneda de la ficha (en GHL, la etapa se llama «Purchase» para que lleve el valor) |
| `perdido` | Descartado o perdido | `LeadPerdido` (personalizado, opcional) | — | Por defecto no se envía. Si se envía, nunca se optimiza. Sirve para audiencias y exclusiones; motivo en el CRM |

**Reglas de los nombres:**
- Nunca el nombre visible de la etapa en GHL («Cualificado», «Cita agendada»), ni el id en minúscula (`cualificado`),
  ni los ejemplos de la KB (`raw_lead`, `qualified`, `booked_call`, `showed`, `won`, `disqualified`). Con dos nombres
  para el mismo hito, el volumen de la etapa objetivo se reparte y el embudo de Conversion Leads del dataset deja de
  coincidir con lo que llega. `capi.py validar` avisa y propone el nombre de la tabla.
- **Compatible con Conversion Leads.** Meta deja el `event_name` libre (es el nombre de la etapa del CRM) y pide
  `[OFFICIAL META]` (`meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md` §3):
  - nombres estables;
  - todas las etapas a medida que ocurren, también la inicial;
  - en cada evento del CRM, `action_source=system_generated`, `custom_data.event_source=crm`,
    `custom_data.lead_event_source=<CRM>` y `user_data.lead_id` (o email y teléfono con hash).

  `raw_lead`, `qualified` y los demás son ejemplos de la KB, no un requisito.
- **Etapa inicial.** Con formulario instantáneo, el CRM manda `Lead` (con `lead_id`) como primera etapa. Con
  formulario web, `Lead` ya lo mandan el píxel y la CAPI web con el mismo `event_id`, y el CRM empieza en la etapa
  siguiente: la acción de CAPI de GHL no lleva `event_id` y lo contaría dos veces `[STRONG INFERENCE]`.
- No se renombra a mitad de campaña. Si un cliente ya optimiza con otro nombre, se mantiene hasta la campaña siguiente
  y se anota en su ficha.

- **`Lead` es el momento en que la persona envía sus datos de contacto**, esté donde esté ese paso. En el diagnóstico
  de `paginas.py` lo decide `captura` (§17): con `antes` (por defecto), `Lead` y `DiagnosticoCompletado` salen a la vez
  al enviar los datos; con `despues`, `DiagnosticoCompletado` sale al ver el resultado y `Lead` al enviar los datos. Si
  un diagnóstico pide el contacto en el primer paso, `Lead` va en ese primer paso.
- Qué evento optimizar según el volumen lo decide el playbook del nicho
  (`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md`).
- En GHL, el pipeline usa estas etapas en este orden; los nombres visibles pueden traducirse, pero el evento enviado
  es el de la tabla, escrito a mano en la acción de CAPI de cada etapa (nunca el nombre de la etapa).

**Mensajería** (Click to WhatsApp, Messenger e Instagram Direct; `capi.py construir --canal`,
`action_source=business_messaging`). Solo tres etapas tienen evento en la lista cerrada de Meta: `LeadSubmitted`,
`QualifiedLead` y `Purchase` (columna «Mensajería»). Las demás van por el CRM o por la CAPI web con `event_id`. Con
`--cualifica-en llamada|asistio|propuesta`, esa etapa manda `QualifiedLead` y sustituye a `cualificado`, que deja de
mandar para no contar dos veces. Meta no deduplica la mensajería: cada hito se envía una sola vez y sin reintentos
automáticos (la idempotencia va en el CRM o en el backend). Paso a paso: `docs/guias/mensajeria.md`.

**Eventos (taller o webinar).** Un pipeline propio («Taller») puede preceder a `cualificado`; desde ahí siguen las
etapas y los eventos de la tabla de arriba, en el mismo dataset:

| Etapa del evento | Qué pasa | Evento a Meta | Notas |
|---|---|---|---|
| `registro_evento` | Se registra | `CompleteRegistration` | Evento por defecto del tipo `webinar` de `paginas.py`; el `Lead` del embudo principal queda limpio. `content_name` = identificador de la edición |
| `asistio_evento` | Asiste al directo (o a la repetición, separado por etiqueta) | `WebinarAsistido` (personalizado) | Desde el CRM o la plataforma del evento, por servidor |
| `hasta_oferta` | Se queda hasta la oferta | `WebinarHastaOferta` (personalizado) | Opcional |

La KB los llama `WebinarAttended` y `StayedToPitch`; aquí se usan `WebinarAsistido` y `WebinarHastaOferta`.

En GHL: Registrado → Asistió al taller → [Se quedó a la oferta] → Cualificado → Llamada agendada → Llamada asistida →
Propuesta enviada → Purchase → Perdido. La oportunidad no cambia de pipeline.

**Segmentos de audiencia** (`audiencias_meta.py etapas`). Además de las etapas, `no-show` (agendó y no se presentó;
va entre `llamada` y `asistio`) y `perdido-timing` (perdido por «mal momento», por el motivo de pérdida o por una
etiqueta). Los segmentos propios de un taller se declaran con `--mapa "Nombre=propio:<segmento>"`
(`registrado-sin-asistir`, `asistio-sin-llamada`, `hasta-oferta-sin-reserva`).

## 17. Páginas generadas (`paginas.py`)

- Salida estática (HTML, CSS y JS propios, sin dependencias externas salvo el píxel), publicable en cualquier hosting o
  como código personalizado en GHL (`--fragmento-ghl`). El OS nunca despliega: el usuario sube la carpeta. `generar`
  nunca borra: solo sobrescribe lo que genera. Salida habitual: `clientes/<slug>/paginas/<pagina o edicion>/`.
- Tipos: `landing`, `diagnostico`, `reserva`, `gracias`, `webinar` (o `todas` las del config). Formato del config,
  fórmulas del diagnóstico y ejemplos: `plantillas/paginas/README.md` y `plantillas/paginas/ejemplos/`.
- Captura `utm_*`, `fbclid` (→ `fbc`), `fbp` y el `ad_id` del parámetro `ad_id` o, si falta, de `utm_content` numérico;
  los envía con el formulario al webhook configurado (GHL u otro). El formato del envío es el **payload v1** de
  `plantillas/paginas/README.md` (con `eventos[]` y `enviar_a_meta`).
  - Los campos del formulario no pueden usar como id una clave del payload v1 (`origen`, `momento`, `ref`, `ad_id`,
    `utm_*`, `event_id`…) ni `web2` (la trampa antispam) ni `acepta_*` (las casillas): `generar` lo rechaza y
    `validar` lo marca (`form.reservado`). Si aun así llegan, los metadatos prevalecen sobre los campos.
  - El calendario de la reserva recibe la misma atribución que los enlaces: `utm_*`, `campaign_id`, `adset_id`,
    `ad_id`, `placement`, `site` y `ref`, y `fbclid` solo si `enviar_a_meta` lo permite.
  - Plantilla del receptor (n8n, Make o backend): `plantillas/integraciones/paginas/`.
- Cada envío dispara el evento del navegador con un `event_id` y manda ese mismo `event_id` al webhook para deduplicar
  con la CAPI del servidor. Cada envío lleva `content_name` (identificador de la página o de la edición) en el payload
  y en `custom_data`.
- Eventos por página: landing `Lead` (o el de `formulario.evento`); webinar `CompleteRegistration`; diagnóstico `Lead`
  + `DiagnosticoCompletado` (con `value` = `valor_evento` del nivel); `LeadCualificado` solo con `cualificado.activo`;
  reserva `Schedule` (por navegador con Calendly; con GHL, desde el servidor); gracias, el que se configure.
- **Diagnóstico, `captura`:** `antes` (por defecto: preguntas → datos de contacto → resultado) o `despues` (preguntas →
  resultado → datos para reservar). `Lead` se dispara siempre al enviar los datos de contacto (§16).
- Consentimiento (RGPD): `fbevents.js` no se descarga hasta que el usuario acepta. Sin consentimiento solo se envía al
  servidor lo que permita la base legal configurada (`base_legal_servidor`, por defecto `consentimiento`: sale
  `enviar_a_meta: false` y sin `fbc`, `fbp` ni `event_id`).
  - **El banner está en todos los modos en los que hay algo que pedir:** con píxel y eventos del navegador, y también
    sin píxel o con `eventos_navegador: false` si hay webhook y la base es `consentimiento` (modo «solo servidor»).
    En ese modo el texto por defecto habla del envío desde el servidor, no del píxel. Solo con
    `consentimiento.banner: false` lo pone tu gestor de cookies (`PaginasOS.consentimiento('si'|'no')`).
  - Cada envío lleva el estado (`consentimiento_marketing`) y la decisión (`enviar_a_meta`). El receptor solo manda a
    la CAPI los envíos con `enviar_a_meta: true`; los demás van al CRM sin identificadores de Meta.
  - `validar` da error (`consentimiento.banner`) si la página necesita banner y no lo tiene.
- Rápida en móvil y en el navegador interno de Instagram y Facebook; `validar` lo comprueba (peso, imágenes, tracking,
  formularios, accesibilidad básica, contraste, enlaces y contenido de ejemplo sin sustituir, que es error).
  - Los enlaces que comprueba son los `<a href>`, el `data-siguiente` de los formularios, el `siguiente` de la
    reserva y los CTA de los niveles del diagnóstico. Una carpeta sin `index.html` es un enlace roto.
- **Un config con una sola página** (el flujo de `/webinar`: `registro/` y `gracias/`, cada una con su config) la
  genera como `index.html`, salvo que diga otro `archivo`. Así `…/registro/` y `../gracias/` no dan 404.
- **Moneda:** la de `sitio.moneda`; si falta y se genera con `--cliente`, la de la ficha (aviso si no coinciden). Va
  en el `currency` de los eventos y en las cifras.
- **Números del config y de los formularios:** se leen como las escribe una persona, con la regla de
  `_comun.numero()` («1.200» = 1200, «1.500,50» = 1500,5, «0.175» = 0,175). `numEntrada()` de `paginas.js` y
  `diagnostico.js` hace lo mismo (vectores compartidos en `tests/herramientas/paginas_vectores.json`).
- **Webinar, hora y zona:** `evento.zona_horaria` (IANA); si falta, la de la ficha con `--cliente`, o
  `Europe/Madrid` con la etiqueta por defecto. Sin desfase en `inicio`, se calcula para esa fecha (horario de
  verano incluido); con desfase, tiene que coincidir con el de la zona en esa fecha o `generar` da error.
- Las páginas llevan `<meta name="generator" content="meta-ads-os/paginas">` y su configuración en
  `<script type="application/json" id="pos-config">`; así `landing_check.py` y `/landing` las reconocen.
