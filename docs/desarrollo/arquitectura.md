# Arquitectura de Meta Ads OS

Cómo está construido el sistema y por qué. Para quien quiera entenderlo a fondo, adaptarlo o contribuir. Los nombres,
rutas, formatos y firmas exactos están en [contratos.md](contratos.md), que manda sobre este documento.

## 1. Intención

Llevar Meta Ads como un equipo experto, de principio a fin, desde Claude Code: configurar la cuenta según en qué punto
esté cada uno, resolver dudas, lanzar y gestionar campañas, decidir el siguiente anuncio y producirlo, conectar los
sistemas de negocio (GoHighLevel y Stripe) para decidir con resultados reales y recibir un brief diario sin tocar nada.

Público: consultoras y agencias de IA y automatización, y SaaS, que lo usan para captar sus propios clientes y para
llevar Meta Ads a sus clientes. Mac o Windows con Git Bash, plan Pro de Claude como mínimo, sin saber programar.

**Sería un fracaso, aunque funcionara, si:**
- gasta, activa, escribe a contactos o toca pagos sin un sí explícito en ese momento;
- un usuario pierde sus datos al actualizar;
- decide con el CPA de 1–3 días, o con el CPL cuando ya hay citas, pruebas o ventas medidas;
- la distribución filtra datos de operadores o de sus clientes (IDs, tokens, aprendizajes privados, nombres);
- guarda datos personales de leads en archivos que se comparten o se versionan;
- manda eventos reales de prueba que ensucian el dataset de un cliente;
- el usuario ve un catálogo en lugar de un camino;
- tiene piezas de relleno.

**No hace (v1):** panel web, desplegar páginas (las construye `paginas.py`, pero las sube el usuario a su hosting o a
GHL), moderar comentarios, enviar mensajes a contactos, Google Ads ni TikTok Ads.

## 2. Producto e instancia

La decisión que sostiene todo: **lo que se distribuye y lo que es de cada operador viven separados**, así se puede
actualizar sin miedo.

```
PRODUCTO (versionado)                          INSTANCIA (de cada operador, ignorada por git)
.claude/  agents · skills · hooks ·            contexto/   operador.md · preferencias.md · instalacion.json
          workflows · output-styles ·          clientes/<slug>/   ficha.md · estado.md · change-log.md ·
          settings.json                                    registro-creativo.csv · informes/ · creativos/ ·
meta-ads-kb/   herramientas/   modulos/                    datos/ · privado/ · marca/ · paginas/ · …
plantillas/    docs/   scripts/   tests/       aprendizajes/   informes/diario/   logs/   .env
CLAUDE.md  README.md  CHANGELOG.md  LICENSE
.mcp.json  pyproject.toml  .gitignore
```

- El instalador crea la instancia desde `plantillas/`. Solo se versionan los `README.md` que explican cada carpeta
  de la instancia (`clientes/README.md`, `contexto/README.md`, `aprendizajes/README.md`).
- `CLAUDE.md` es genérico e importa `@contexto/operador.md`: lo personal de cada operador entra por su instancia, no
  editando el producto.
- `/actualizar` hace `git pull --ff-only` y nunca escribe en la instancia, salvo las migraciones declaradas.
- Los aprendizajes de cada operador viven en `aprendizajes/`. Solo lo verificado y anonimizado entra en la base del
  producto (`meta-ads-kb/16-aprendizajes-propios/`), en el proceso de mantenimiento.

## 3. Cómo se conectan las piezas

```
                    CLAUDE.md (+ contexto/operador.md)
                    principios, enrutado por fases, reglas
                                  │
     usuario ── /skill ──► SKILL.md: pasos numerados que citan meta-ads-kb/ por ruta
                                  │
               ┌──────────────────┼────────────────────┬──────────────────┐
               ▼                  ▼                    ▼                  ▼
         agentes (20)       herramientas (25)     MCP: meta-ads,    workflows (5)
     tools cerradas,        python3 -I,           ghl, stripe       solo desde su skill
     model inherit|sonnet   --cliente, --json                       («profundo», con aviso de coste)
               │                  │                    │
               └──────────────────┴──── hooks (10) ────┘   antes y después de cada llamada relevante
                                         permisos de settings.json como red de seguridad
                                  │
                       clientes/<slug>/  (ficha, estado, change log, registro, entregables)
```

- **Skills** (`.claude/skills/<nombre>/SKILL.md`): cabecera con `name`, `description` (≤350 caracteres, sin solaparse
  con otras), `argument-hint` y `disable-model-invocation: true` en las que escriben, gastan o actualizan. Cuerpo con
  pasos numerados que citan la base por ruta y los agentes y herramientas por su nombre de contrato.
- **Agentes** (`.claude/agents/<nombre>.md`): `tools` como lista explícita y `model` `inherit` (razonamiento) o
  `sonnet` (volumen), pensado para que el sistema rinda con el plan Pro. Solo `operador-meta` tiene herramientas de
  escritura en Meta.
- **Los asistentes conversacionales son skills**, no agentes (`/empezar`, `/configurar-meta`, `/conectar`): un
  subagente no puede hacer preguntas a mitad de su tarea.
- **Workflows** (`.claude/workflows/<nombre>.js`): `meta` como literal puro; se lanzan siempre desde su skill, después
  de avisar del coste y recibir el sí. Ninguno escribe en sistemas externos ni ejecuta órdenes de pago.
- **Herramientas** (`herramientas/<nombre>.py`): `python3 -I herramientas/<x>.py <subcomando>`, `--cliente` lee la
  ficha, `--json`, códigos de salida `0` bien, `1` error del usuario, `2` error de configuración. `_comun.py` es la
  librería compartida (carga de `.env`, lectura de fichas, registros).
- **Hooks** (`.claude/hooks/<nombre>.py`): solo biblioteca estándar, leen el JSON de stdin y responden con el formato
  de hooks de Claude Code. Si su propia lógica falla, dejan pasar y lo registran: los permisos de `settings.json`
  siguen pidiendo confirmación. Se lanzan con `python3`, `python` o `py -3`, el primero que funcione, y bastan con
  Python 3.8 (el de las herramientas de línea de comandos de macOS es el 3.9). Contrato §10.

## 4. Recorrido por fases y estado

Cada cliente tiene `clientes/<slug>/estado.md` con una cabecera (`fase`, `actualizado`) y una checklist cuyos ids
(`F<n>.<clave>`) son canónicos en `plantillas/cliente/estado.md`. Cada punto declara cómo se verifica (`mcp`, `ghl`,
`stripe`, `archivo`, `usuario`). La fase actual es la primera con puntos sin marcar.

`herramientas/estado.py resumen --json` lo calcula sin coste: fase, pendientes, evaluaciones vencidas del change log,
informe semanal pendiente, brief de hoy y cola de producción. Lo usan `/hoy`, el brief diario y el hook
`contexto_sesion`. Explicación para usuarios: [recorrido.md](../recorrido.md).

## 5. Ejecución en Meta: dos vías

| Vía | Para | Límites |
|---|---|---|
| MCP oficial (`meta-ads`) | Leer, crear campaña, conjunto, anuncio y creatividad de imagen, cambios, audiencias y experimentos | No sube vídeo ni imagen; creatividades solo de imagen única; no crea portfolios ni cuentas |
| `herramientas/meta_ads.py` | Subir vídeo e imagen, creatividades con todas las mejoras automáticas desactivadas (y verificación posterior), planes declarativos idempotentes con `--simular`, tope total diario | Necesita token de usuario del sistema (opcional, `/conectar meta --avanzado`) |
| `reglas_meta.py`, `formularios_meta.py`, `audiencias_meta.py` | Reglas automáticas que pausan o avisan con el ordenador apagado, formularios instantáneos con preguntas de filtro, audiencias de lista de clientes por etapa | El mismo token; cada escritura con `--simular` antes y `--confirmo` después |

Las dos vías solo las usa `operador-meta` y pasan por los mismos hooks. Cada escritura de la CLI queda en
`logs/cambios.jsonl` (contrato §8).

**Topes en dos capas.** El hook controla el tope **por cambio** (el presupuesto que llega en la llamada). El gasto
total lo limita Meta en su servidor: límite de gasto de la cuenta y regla «Budgets set above this amount → Blocked» del
Ads MCP server, que deja puestos `/configurar-meta` (sin verificar si esa regla mira el presupuesto diario o el
total). Con el token avanzado, el hook suma además el presupuesto activo y
aplica el tope total de la ficha (un hook no puede llamar al MCP).

## 6. Sistemas de negocio

1. **Meta → GHL**: formularios instantáneos de forma nativa, o páginas web (las de `paginas.py` o las del usuario)
   con UTMs que llevan `ad_id` y un webhook que recibe el payload con `fbc`, `fbp` y `event_id`.
2. **GHL → Meta**: etapas del pipeline por CAPI (una por etapa, «Allow multiple», la etapa ganada como `Purchase` con
   valor). Se verifica con las estadísticas y la calidad del dataset.
3. **GHL → sistema**: MCP oficial de HighLevel (OAuth por subcuenta) en conversación; `herramientas/ghl.py` (API v2,
   token de integración privada de solo lectura) sin nadie delante. Protección: `ghl_guard`.
4. **Stripe → sistema** (SaaS): MCP oficial en solo lectura o `herramientas/stripe_datos.py` con clave restringida.
   El alta guarda `utm_*`, `ad_id`, `fbc` y `fbp` en los metadatos del cliente para unir pagos con anuncios.
   Protección: `stripe_guard`.
5. **Mensajería → Meta**: Click to WhatsApp, Messenger e Instagram Direct vuelven a Meta como `LeadSubmitted`,
   `QualifiedLead` o `Purchase` (`capi.py construir --canal`, `action_source=business_messaging`). Las etapas son las
   del embudo consultivo (contrato §16). Guía: [mensajeria.md](../guias/mensajeria.md).

Los servidores `ghl` y `stripe` se añaden con `claude mcp add --scope local`: no modifican `.mcp.json` y cada usuario
conecta los suyos.

## 7. Circuito de datos

```
Meta (MCP o meta_ads.py anuncios) ─┐
GHL (ghl.py por-anuncio) ──────────┼─► registro_creativo.py ─► clientes/<slug>/registro-creativo.csv
Stripe (stripe_datos.py por-anuncio)┘    (clasificación desde el nombre: nomenclatura.py)
                                                │
                     /siguiente-anuncio ◄───────┘  ganadores con la capa más baja de verdad con n suficiente
                             │
               producción → publicación (en pausa, mejoras off) → lectura → registro
```

- La nomenclatura del anuncio (`<AAAAMMDD>_<angulo>_<concepto>_<formato>_<hook>`) es lo que permite agregar por
  ángulo, concepto, formato y hook. Por eso `control_publicacion` la exige al publicar.
- Capas de verdad: servicios, venta > cita o show > cualificado > CPL; SaaS, cliente de pago > prueba activada >
  prueba > registro. Las métricas antes del clic solo descartan perdedores.
- `herramientas/embudo.py` monta cohortes por semana o por anuncio, con LTV y payback en SaaS.
- El reparto entre explorar y explotar (`explorar_explotar` en la ficha) es un valor por defecto marcado
  `[HYPOTHESIS]`.
- `herramientas/elementos_creativos.py` etiqueta los elementos de cada anuncio (gancho, persona, prueba, CTA…) en
  `datos/elementos-creativos.csv` y los cruza con los resultados: qué elementos ganan, no solo qué anuncio. Es
  asociación, nunca causa.
- `herramientas/audiencias_meta.py` convierte las etapas del CRM en audiencias para incluir o excluir en ciclos largos
  (`/anuncios-por-etapa`).

## 8. Producción creativa

| Vía | Cómo | Quién |
|---|---|---|
| `ia` | Motor de vídeo con IA (`modulos/motor-ia/`), con la clave del usuario y un guardián de presupuesto (5 $ por defecto) | `productor-ugc` |
| `propio` | Guion de grabación y lista de planos → brutos → montaje con cutkit (`modulos/cutkit/`) o FFmpeg (`editar_video.py`) | `editor-video` |
| `hibrido` | A-roll propio con B-roll del motor | los dos |
| estático | Plantillas HTML + `render.py` (1:1, 4:5, 9:16) con fotos o capturas reales | `disenador-estaticos` |

Los textos los escribe `redactor-anuncios`. Toda pieza pasa por `critico-creativo` y `revisor-politicas` y se entrega
en `clientes/<slug>/creativos/<nombre-base>/` con un `LEEME.md` (QA, crítica, coste, afirmaciones, etiqueta de IA y
veredicto de políticas). Los módulos de vídeo son proyectos uv independientes: cada usuario crea su entorno en su
ordenador, porque un entorno no se puede mover entre carpetas. La marca de cada cliente vive en
`clientes/<slug>/marca/`; el producto no incluye ninguna marca real.

La prueba social real (casos con permiso, socios y anuncios de colaboración) la organiza `/casos-y-creadores`, y
`/organico-a-anuncios` convierte publicaciones que ya funcionaron en anuncios. Lo que hay que saber de cada pieza
(identidad, derechos, origen) va en su `LEEME.md` (contrato §6).

## 9. Brief diario

`/brief-diario [<slug>|todos] [programar|probar]`, de solo lectura, en interactivo y sin nadie delante. Escribe un
archivo por cliente (`clientes/<slug>/informes/diario/AAAA-MM-DD.md`) y un resumen global
(`informes/diario/AAAA-MM-DD.md`) que envía `herramientas/notificar.py` por Telegram, email o Slack. El disparador vive
fuera (tarea programada de Claude Desktop, launchd, Programador de tareas, cron o una rutina en la nube) y la lógica
dentro. Sin nadie delante se ejecuta con una lista explícita de herramientas de lectura y escritura solo en las
carpetas de informes. Ni el archivo ni el mensaje llevan datos personales. Cada informe por cliente empieza con una
cabecera YAML (`semaforo`, `acciones`…) que leen `/hoy` y `contexto_sesion` sin interpretar el texto (contrato §15).

## 10. Seguridad

| Capa | Qué aporta |
|---|---|
| Permisos (`settings.json`) | allow para lecturas, ask para escrituras y borrados de archivos, deny para borrados en Meta, escrituras en Stripe y secretos |
| Hooks | Lo que los permisos no ven: presupuesto dentro de la llamada, regla de paciencia, código de prueba de CAPI, nomenclatura, veredicto de políticas, datos personales, secretos, change log obligatorio |
| Agentes con `tools` cerradas | Solo `operador-meta` escribe en Meta |
| `disable-model-invocation` | Las skills que escriben, gastan o actualizan solo las lanza el usuario |
| Límites del lado de Meta | Siguen funcionando aunque falle el ordenador del operador |
| Reglas automáticas del OS | Pausan o avisan dentro de Meta con el ordenador apagado (`/reglas-automaticas`, primero en modo sombra) |
| Proceso | Todo en pausa, activar con confirmación específica, change log con fecha de evaluación |

Explicación para usuarios: [seguridad.md](../seguridad.md).

## 11. Formatos de archivo

| Archivo | Formato | Lo leen |
|---|---|---|
| `clientes/<slug>/ficha.md` | Cabecera YAML (subconjunto simple: claves, anidación con dos espacios, sin listas) con slug, estado, tipo, relación, moneda, IDs de Meta, evento, ventana, topes, CRM, Stripe y mejoras automáticas; cuerpo en Markdown | `_comun.leer_ficha` (lanza `FichaInvalida` con el campo a arreglar) y el parser mínimo de los hooks |
| `clientes/<slug>/estado.md` | Cabecera `fase` y `actualizado`; líneas `- [ ] F<n>.<clave> — texto (verifica: …)` | `estado.py`, `/hoy`, `contexto_sesion` |
| `clientes/<slug>/change-log.md` | Tabla con `Fecha/hora`, `Quién`, `Nivel`, `Objeto (ID)`, `Cambio (de → a)`, `Motivo / hipótesis`, `Métrica de éxito`, `Fecha de evaluación`, `Resultado` (vacío = pendiente) | `estado.py`, `meta_guard`, `registro_obligatorio` |
| `clientes/<slug>/registro-creativo.csv` | Una fila por `ad_id` con identidad, clasificación, métricas de Meta, resultados de negocio y veredicto | `/siguiente-anuncio`, informes |
| `logs/*.jsonl` | Una línea por evento, `ts` en ISO 8601 local, sin tokens ni datos personales | hooks, `estado.py` |
| `clientes/<slug>/datos/elementos-creativos.csv` | Una fila por `ad_id` con los elementos etiquetados (contrato §6) | `elementos_creativos.py`, `/analisis-creativo` |
| `clientes/<slug>/marca/marca.json` | Colores, tipografías, logo, subtítulos, CTA y etiqueta de IA (contrato §14) | cutkit, `render.py`, `editar_video.py`, `paginas.py` |
| `contexto/preferencias.md` | Cabecera YAML: `nivel`, `estilo`, `brief` (`canal`, `hora`, `clientes`, `programado_con`) y `motor.presupuesto_usd` | estilos de salida, brief, motor |
| `contexto/instalacion.json` | Ver §12 | `/empezar`, `doctor.py`, `contexto_sesion` |

Las cabeceras YAML admiten un comentario al final de la línea (` # …`, con un espacio antes), también detrás de un valor
entre comillas: los dos parsers (`_comun` y el de los hooks) lo descartan. Un `#` sin espacio delante forma parte del
valor.

## 12. Instalación

`scripts/instalar.sh` (bash compatible con la 3.2 de macOS y con Git Bash):

1. **Requisitos.** Python ≥3.10 (prueba `python3`, `python` y `py -3`, y descarta el atajo de la Microsoft Store), git
   y uv obligatorios; FFmpeg y el CLI de Claude, informativos. Si falta un obligatorio, sale con 1 sin escribir nada.
2. **Instancia.** Crea `contexto/`, `clientes/`, `aprendizajes/`, `logs/` e `informes/diario/`; copia
   `plantillas/contexto/*` y `plantillas/env.ejemplo` → `.env` (chmod 600) solo si no existen.
3. **Estado.** `python3 -I scripts/instalacion.py preparar --sistema <json> --tecnica hecho|fallo` y una prueba de humo
   con `estado.py`.

Es idempotente, `--comprobar` no escribe nada y `--instalar-uv` usa el instalador oficial de uv.

`contexto/instalacion.json` (esquema en `plantillas/contexto/instalacion.json`): `esquema`, `iniciado`,
`actualizado`, `pausa` (`{fecha, fase, motivo}` o `null`), `producto.version`, `sistema` (versiones detectadas) y
`fases` (`tecnica`, `perfil`, `meta`, `integraciones`, `cliente`, `entregable`, `brief`, `motor`, `avanzado`), cada
una con `estado` (`pendiente | en_curso | hecho | omitido | fallo`), `requerida`, `fecha` y `detalle`. Completa
cuando todas las requeridas están en `hecho` u `omitido`. Se lee y escribe con `scripts/instalacion.py`:

```bash
python3 -I scripts/instalacion.py ver [--json]
python3 -I scripts/instalacion.py marcar <fase> <estado> [--detalle TEXTO] [--dato clave=valor ...]
python3 -I scripts/instalacion.py pausar [<fase>] [--motivo TEXTO] [--json]
python3 -I scripts/instalacion.py reanudar [--json]
python3 -I scripts/instalacion.py preparar [--sistema JSON] [--tecnica hecho|fallo]
```

Al cargar, el script añade las claves nuevas de la plantilla sin cambiar ningún valor existente; si el JSON está
dañado, guarda una copia antes de rehacerlo.

## 13. Actualización y migraciones

`scripts/actualizar.sh`: comprueba que es un clon con remoto, que no hay cambios en archivos del producto
(`git status --porcelain --untracked-files=no`) ni commits propios; hace `git fetch`, enseña los commits y la versión
nueva; con `--comprobar` termina ahí. Después, `git pull --ff-only`, el extracto del `CHANGELOG.md` y
`scripts/migrar.py aplicar`.

Las migraciones (`scripts/migraciones/NNNN_slug.py`) declaran `VERSION`, `DESCRIPCION`, `ARCHIVOS`,
`necesaria(raiz)` y `aplicar(raiz) -> list[str]`. No hay registro de aplicadas: cada una es idempotente y decide mirando
los datos. Antes de aplicar, `migrar.py` copia lo declarado en `ARCHIVOS` a `logs/copias-migracion/<ts>_<id>/`. Nunca
borran ni mueven, no sobrescriben valores del usuario y se detienen en el primer fallo. Formato completo y ejemplo:
[`scripts/migraciones/README.md`](../../scripts/migraciones/README.md).

## 14. Validación

`scripts/validar.py` comprueba el producto antes de publicar y en la integración continua; sale con 1 si algo falla
y dice qué y dónde.

| Sección | Comprueba |
|---|---|
| `cifras` | 50 skills, 20 agentes, 10 hooks (`.claude/hooks/[!_]*.py`), 5 workflows, 25 herramientas y 2 estilos con los nombres del contrato; sobrantes y renombradas; carpetas de skill sin `SKILL.md`; que `docs/catalogo/` documenta cada pieza |
| `cabeceras` | Campos obligatorios, longitud y solapamiento de descripciones, `disable-model-invocation` donde toca, `model` y `tools` de los agentes, que solo `operador-meta` escribe en Meta y nadie escribe en Stripe, `meta` literal y sintaxis de los workflows, sintaxis de Python, hooks solo con biblioteca estándar, `settings.json` válido y coherente |
| `enlaces` | Enlaces internos de la base y de la documentación (y sus anclas), rutas `meta-ads-kb/…` citadas en cualquier archivo |
| `claude-md` | Imports `@`, cada `/skill`, agente y ruta citados en `CLAUDE.md` existen; las cifras de `CLAUDE.md` y `README.md` coinciden con el contrato |
| `fugas` | Rutas personales, cuentas `act_` e IDs de Meta reales, tokens y claves (Meta, Stripe, Google, GitHub, Slack, Telegram, IA, GHL, AWS), emails y teléfonos, archivos de la instancia versionados y una lista negra local de nombres propios |

```bash
python3 scripts/validar.py                    # todo
python3 scripts/validar.py --solo fugas --todo
python3 scripts/validar.py --json
```

- La **lista negra** de nombres propios (clientes, marcas, personas) no se versiona: vive en `contexto/fugas.txt` o se
  pasa con `--lista-negra <archivo>` (o `VALIDAR_LISTA_NEGRA`). Una línea por término; `/regex/` para expresiones
  regulares; `!patrón` exime archivos.
- Los IDs de relleno (ceros, secuencias), los dominios de ejemplo (`example.com`) y las empresas ficticias del
  contrato (Acme Automations, Nimbo, Clínica Sonrisa) no cuentan como fuga. En `tests/`, los emails y teléfonos con
  forma real son aviso, porque los tests de los detectores de datos personales los necesitan; los tokens y las rutas
  siguen siendo fallo.

La integración continua (`.github/workflows/ci.yml`) ejecuta los tests, `validar.py` y el instalador en Ubuntu, macOS y
Windows, sin secretos.

**Evals del criterio.** Los tests comprueban el código; las evals comprueban que el OS razona como un media buyer
experto (39 casos ficticios con rúbrica). `python3 scripts/evals.py --simular` valida los casos sin gastar y corre en
la suite. La ejecución real lanza `claude -p`, gasta uso de Claude y solo se hace antes de un release, con el sí de
quien publica. Proceso, formato de los casos y criterio de salida: [evals.md](evals.md).

## 15. Versiones

Versionado semántico en `pyproject.toml` y en `CHANGELOG.md` (`## [x.y.z] — AAAA-MM-DD`, que lee `actualizar.sh`).
Una versión que cambia el formato de la instancia trae su migración y lo dice en el changelog.

## 16. Contribuir

- Español de España, tuteo, frases claras, fechas `AAAA-MM-DD`.
- Cita la base por ruta y comprueba que la ruta existe. Umbrales que no estén en la base, marcados `[HYPOTHESIS]`.
- Ejemplos solo con empresas ficticias del público objetivo: Acme Automations (agencia de automatización), Nimbo
  (SaaS B2B) y Clínica Sonrisa (cliente local de una agencia). IDs de ejemplo con ceros.
- Tests con `uv run pytest`, sin red (el HTTP se simula) y sin gasto (`MOTOR_MOCK=1`).
- Nada de relleno: cada pieza tiene que poder usarse mañana en una cuenta real.
- Antes de proponer un cambio: `uv run pytest -q` y `python3 scripts/validar.py` en verde. Si el cambio toca el
  criterio (skills, agentes, `CLAUDE.md`, la base), di qué casos de las [evals](evals.md) afecta.
