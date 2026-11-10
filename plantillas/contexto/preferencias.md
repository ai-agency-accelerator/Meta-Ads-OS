---
nivel: principiante
estilo: profesor
brief:
  canal: ninguno
  hora: "08:00"
  clientes: todos
  programado_con: ""
motor:
  presupuesto_usd: 5
---

# Preferencias

La cabecera de arriba la leen las herramientas, los hooks y `/brief-diario`: cambia solo los valores y respeta el
formato (dos espacios de sangría, sin comentarios al final de una línea con comillas). Si dudas, pídeselo a Claude.

| Clave | Valores | Para qué sirve |
|---|---|---|
| `nivel` | `principiante` · `intermedio` · `avanzado` | Cuánto explica Claude y qué te propone primero. Lo fija `/empezar` |
| `estilo` | `profesor` · `operador` | `profesor` explica el porqué y enlaza la base de conocimiento; `operador` va al grano. Cámbialo también con `/config` → estilo de salida |
| `brief.canal` | `telegram` · `email` · `slack` · `ninguno` | Dónde recibes el brief diario. Las credenciales van en `.env` |
| `brief.hora` | `"HH:MM"` (entre comillas) | Hora local a la que se programa el brief |
| `brief.clientes` | `todos` o slugs separados por comas | Qué clientes entran en el brief |
| `brief.programado_con` | `desktop` · `sistema` · `nube` · `""` | Cómo está programado. Lo rellena `/brief-diario programar` |
| `motor.presupuesto_usd` | número | Tope global de gasto del motor de vídeo con IA, en dólares. También se puede fijar con `MOTOR_PRESUPUESTO_USD` en `.env` |

Guías: `docs/guias/brief-diario.md` (brief y canales) y `docs/guias/video-ia.md` (motor y presupuesto).

## Otras preferencias

Escribe aquí lo que quieras que Claude tenga en cuenta y no encaje arriba (formato de los informes, idioma de los
entregables para clientes, cuándo prefieres que te pregunte).

-
