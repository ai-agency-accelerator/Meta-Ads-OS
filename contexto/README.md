# contexto/

Quién eres y cómo quieres trabajar. Es parte de **tu instancia**: git no lo sube (salvo este archivo) y `/actualizar`
no lo toca. Si quieres copia de seguridad, guarda esta carpeta junto con `clientes/` y `aprendizajes/` en un
repositorio **privado** propio o en tu nube.

El instalador (`scripts/instalar.sh`) crea los tres primeros archivos copiando `plantillas/contexto/`, solo si no
existen. `/empezar` los rellena contigo.

| Archivo | Qué es | Quién lo escribe | Quién lo lee |
|---|---|---|---|
| `operador.md` | Tu perfil (agencia, consultora, SaaS o negocio), tu stack, tu objetivo del trimestre, cómo quieres que trabaje contigo y tus **reglas propias**. Mantenlo corto: se carga en cada sesión | `/empezar` y tú | `CLAUDE.md` lo importa (`@contexto/operador.md`) |
| `preferencias.md` | Cabecera YAML con tu nivel, el estilo de salida, el brief diario (`canal`, `hora`, `clientes`, `programado_con`) y el presupuesto del motor de vídeo (`motor.presupuesto_usd`). Formato en `docs/desarrollo/contratos.md` §15 | `/empezar`, `/brief-diario programar`, `/motor` y tú | El brief, `notificar.py`, el motor y las skills que adaptan la explicación a tu nivel |
| `instalacion.json` | En qué punto está la configuración inicial: cada fase (técnica, perfil, Meta, integraciones, cliente, entregable, brief, motor) con su estado. Permite pausar y retomar `/empezar` | `scripts/instalacion.py` (no lo edites a mano) | `/empezar`, `doctor.py` y el aviso de inicio de sesión |
| `entrenamiento.md` | Tu progreso en `/entrenar`: una fila por escenario (fecha, bloque, nivel, nota, fallo principal y siguiente) y la media por bloque. Aparece la primera vez que entrenas | `/entrenar` | `/entrenar` |
| `fugas.txt` | Opcional. Tu lista negra de nombres propios (clientes, marcas, personas) para que `scripts/validar.py` avise si alguno aparece en el producto. Una línea por término; `/regex/` para expresiones regulares; `!patrón` exime archivos. Solo la necesitas si modificas o contribuyes al producto | Tú | `scripts/validar.py --solo fugas` |

Notas:
- El estilo anotado en `preferencias.md` no activa nada por sí solo: el estilo de salida se activa en `/config` o con
  `"outputStyle"` en `.claude/settings.local.json`.
- Los datos de cada cliente no van aquí, sino en su ficha (`clientes/<slug>/ficha.md`). Tus claves tampoco: van en
  `.env`.
- Si `instalacion.json` falta o está dañado, `scripts/instalacion.py` lo rehace desde la plantilla (con una copia del
  dañado) y `/empezar` retoma desde las fases pendientes; tus otros archivos no se tocan.
