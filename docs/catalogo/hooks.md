# Hooks (10)

Los hooks son guardas automáticas: Claude Code los ejecuta antes o después de ciertas acciones y pueden dejar pasar,
pedirte confirmación o bloquear. No dependen de que Claude se acuerde de las reglas: se aplican siempre. Viven en
`.claude/hooks/<nombre>.py`, usan solo la biblioteca estándar de Python y se conectan en `.claude/settings.json`.

**No los desactives ni los rodees.** Si uno te frena, lee su motivo: casi siempre te está ahorrando dinero, un rechazo
o un problema con un cliente.

| # | Hook | Cuándo actúa | Qué hace |
|---|---|---|---|
| 1 | `meta_guard` | Llamadas al MCP de Meta y a las herramientas que escriben en Meta (`meta_ads.py`, `reglas_meta.py`, `formularios_meta.py`, `audiencias_meta.py`) | Registra todo. Las escrituras piden confirmación y solo las puede hacer `operador-meta`; los borrados se bloquean, y también crear algo ya activo. Bloquea cualquier presupuesto que supere el **tope por cambio** de la ficha del cliente y, con el token avanzado, el **tope total diario**. Aplica la **regla de paciencia**: si la misma entidad cambió hace menos de 7 días, te lo dice y pide confirmación. Una regla automática que haga algo más que avisar o pausar se bloquea. También bloquea: escribir desde la sesión principal (se delega en `operador-meta`), promocionar publicaciones (`ads_boost_ig_post`), poner una entidad en `DELETED`, presupuestos que no puede leer como importe y `lifetime_budget` sin fechas. Archivar (`ARCHIVED`) pregunta avisando de que no se deshace desde aquí. Si no puede comprobar una escritura (error, orden con comodines, variables, `-c`, `-m` o `..`), falla cerrado: bloquea en subagentes y, en la sesión principal, bloquea las escrituras en Meta y pregunta el resto |
| 2 | `motor_guard` | Órdenes de pago del motor de vídeo con IA y opciones de pago de cutkit | Pide confirmación con el coste antes de generar, regenerar o crear variantes con voz o idioma, y también con las opciones de cutkit que gastan (`--subtitulos openai`, `--judge`, `--budget`, música con IA, con cualquier valor que active `CK_MUSICA_IA`, también desde el `.env`). Cubre `motor serve` (servidor que puede producir sin más preguntas), `motor edit` sin `--yes` (hasta ~0,05 $), `python -m motor.cli` y `env -u MOTOR_MOCK`. Lo registra |
| 3 | `ghl_guard` | MCP de GoHighLevel y llamadas a su API | `execute_operation` siempre pregunta (regla `ask` en `settings.json`; el hook nunca la deja pasar sola). El id de la operación solo se lee de las claves de primer nivel; si hay varios distintos, pregunta. **Bloquea** mensajes a contactos (SMS, WhatsApp, email, llamadas), borrados y facturas, y en subagentes todo lo que no sea una lectura reconocida |
| 4 | `stripe_guard` | MCP de Stripe, su CLI y su API | Solo lectura: cualquier creación, cambio, reembolso, cancelación o movimiento de dinero se bloquea, también los desconocidos. El id de la operación solo se lee de las claves de primer nivel; si no puede decidir, falla cerrado |
| 5 | `eventos_guard` | Envíos a la Conversions API (`capi.py enviar`, `curl` a `/events`) | Sin `test_event_code`, pide confirmación con un aviso fuerte: un evento real de prueba ensucia el dataset y lo que Meta optimiza |
| 6 | `control_publicacion` | Crear anuncios o creatividades (MCP o `meta_ads.py`) | Comprueba que el nombre cumple la nomenclatura (si no, propone el correcto) y que el `LEEME.md` de la pieza tiene veredicto de políticas. Sigue los `cd` y resuelve comodines para encontrar la pieza |
| 7 | `datos_personales` | Escribir o editar archivos | Si lo que se va a escribir lleva emails, teléfonos o listas de personas fuera de `clientes/<slug>/privado/`, pide confirmación y propone `privado/` o agregados (RGPD). Si una edición de `clientes/<slug>/ficha.md` cambia `topes.*`, pregunta enseñando el antes y el después («cambias los topes de gasto de acme: cambio_dia 50 → 5000») |
| 8 | `secretos` | Órdenes de terminal | Bloquea leer, imprimir, copiar o cargar `.env`, volcar el entorno y mostrar variables con claves. Resuelve comodines y variables (`cat .en?`, `F=.env; cat $F`) |
| 9 | `registro_obligatorio` | Al escribir un change log y cuando Claude va a terminar | Si en la sesión hubo escrituras en Meta, GoHighLevel o Stripe que no están anotadas en el change log de su cliente, no deja terminar y dice cuáles faltan |
| 10 | `contexto_sesion` | Al empezar la sesión | Te enseña en seis líneas como mucho: instalación, conexiones, clientes y su fase, evaluaciones vencidas y si ya tienes el brief de hoy |

## Cómo deciden

- **Dejar pasar.** Las lecturas y todo lo que no tiene riesgo. Lo deciden los permisos de `settings.json` (ver
  [Seguridad](../seguridad.md)).
- **Preguntar.** Escrituras, gasto y envíos de prueba. Verás el motivo y decides tú en ese momento.
- **Bloquear.** Lo que nunca debe pasar sin que lo hagas tú a mano fuera del sistema: borrar en Meta, mandar mensajes
  a contactos, tocar pagos, superar un tope, leer secretos.

Si la lógica interna de un hook falla (un archivo raro, un formato inesperado), lo registra en `logs/hooks.jsonl` y,
por defecto, no decide: mandan los permisos de `settings.json`, que siguen pidiendo confirmación en las escrituras.
Donde eso dejaría una puerta abierta, el hook **falla cerrado**:

- `meta_guard`: una escritura en Meta que no ha podido comprobar se bloquea.
- `ghl_guard` y `stripe_guard`: preguntan en la sesión principal y bloquean en los subagentes.
- `datos_personales`: si falla al revisar la ficha de un cliente, pregunta (podría ser un cambio de topes).

Así un error del hook nunca te deja sin trabajar, pero tampoco abre la puerta a escribir o gastar sin preguntar.

## Dónde dejan rastro

Todo en `logs/`, en JSON por líneas, sin tokens ni datos personales (emails y teléfonos se sustituyen por `***`):

| Archivo | Qué guarda |
|---|---|
| `logs/meta-mcp.jsonl` | Cada llamada al MCP de Meta |
| `logs/cambios.jsonl` | Cada escritura ejecutada en Meta, GoHighLevel, Stripe o la Conversions API |
| `logs/changelog.jsonl` | Cada vez que se anota el change log de un cliente |
| `logs/ghl-mcp.jsonl` · `logs/stripe-mcp.jsonl` | Cada llamada a esos MCP |
| `logs/motor.jsonl` | Cada orden de pago del motor y de cutkit, y su decisión |
| `logs/hooks.jsonl` | Cada decisión de un hook (dejar pasar, preguntar, bloquear) y cada fallo interno con su traza. `/doctor` lo lee para avisarte de un hook roto |

## En Windows

Cada hook se lanza con `python3`, y si no existe, con `python` o `py -3`, así que funcionan en Mac, Linux y Windows
con Git Bash sin configurar nada. Les basta Python 3.8 o superior (el de macOS sirve). Sin ningún Python, los hooks no
corren y mandan los permisos de `settings.json`, que siguen pidiendo confirmación. Si `/doctor` dice que los hooks no arrancan, mira
[Solución de problemas](../solucion-de-problemas.md#los-hooks-no-se-ejecutan).
