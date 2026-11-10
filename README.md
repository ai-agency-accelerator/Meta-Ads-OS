# Meta Ads OS

**El sistema operativo para llevar Meta Ads como un equipo experto, de principio a fin, dentro de Claude Code.**

Configura la cuenta según en qué punto estés, construye tus páginas de captación y tu formulario, decide cuál es el
siguiente anuncio con resultados de negocio reales, produce el anuncio (vídeo con IA, vídeo propio o estático),
lánzalo en pausa con todas las comprobaciones, deja la cuenta protegida con reglas automáticas y recibe cada mañana un
brief de tus cuentas sin tocar nada.

---

## Para quién

Para **consultoras y agencias de IA y automatización, y empresas SaaS** que usan Meta Ads para dos cosas:

- **captar sus propios clientes**: servicios high-ticket con llamada, o SaaS con prueba gratuita o demo;
- **llevar Meta Ads a sus clientes**, con un espacio y un historial por cliente.

No hace falta saber programar. Sí necesitas unos 30 minutos guiados la primera vez.

## Instalación

**Requisitos**

| Qué | Para qué |
|---|---|
| [Claude Code](https://claude.com/claude-code) con un plan **Pro o superior** | Es donde vive el sistema |
| **Git** (en Windows, [Git para Windows](https://git-scm.com/download/win), que trae Git Bash) | Descargar y actualizar el sistema |
| **Python 3.10 o superior** y **[uv](https://docs.astral.sh/uv/)** | Las herramientas y los módulos de vídeo |
| FFmpeg (opcional) | Solo si vas a montar o editar vídeo |

Si te falta alguno, el instalador te dice exactamente cómo instalarlo en tu sistema.

**1. Clona el repositorio** con git. En Windows, desde **Git Bash**:

```bash
git clone https://github.com/ai-agency-accelerator/Meta-Ads-OS.git meta-ads-os
```

Clónalo, no lo descargues como ZIP: sin git no hay actualizaciones.

**2. Ábrelo en Claude Code y escribe:**

```
/empezar
```

Claude ejecuta el instalador por ti (`bash scripts/instalar.sh`), comprueba que todo está bien y sigue con tu
configuración guiada. El instalador también se puede lanzar a mano, y es idempotente: puedes repetirlo cuando quieras y
nunca pisa lo que ya tienes.

La primera vez que abras la carpeta, Claude Code te pedirá confiar en ella y aprobar el servidor MCP `meta-ads`:
acepta las dos cosas, son las que activan los permisos, las guardas de seguridad y la conexión con Meta.

Instalación en detalle, Windows paso a paso y qué hacer si descargaste un ZIP: [docs/primeros-pasos.md](docs/primeros-pasos.md).

## Tus primeros 30 minutos

`/empezar` es una conversación guiada que se puede retomar en cualquier momento:

| Paso | Qué pasa | Tiempo |
|---|---|---|
| 1. Técnica | Instalación y comprobación del entorno | 2–5 min |
| 2. Perfil | Quién eres (agencia, consultora, SaaS o negocio), tu nivel y tu stack | 3–5 min |
| 3. Meta | Conectas el MCP oficial de Meta (inicio de sesión con tu cuenta, sin tokens) | 5–8 min |
| 4. Integraciones | GoHighLevel y Stripe, si los usas (opcional) | ≤5 min |
| 5. Primer cliente | Tu propio negocio o el de un cliente, con su ficha y sus topes de gasto | 5 min |
| 6. Primer entregable | Según la fase: tu economía, el plan de configuración, una foto inicial de la cuenta o la petición de accesos | ≤10 min |

Sales con el sistema instalado, Meta conectado, tu primer cliente situado en una fase y un entregable útil guardado.

## El día a día

Cuatro entradas y un brief. No necesitas memorizar el catálogo:

| Escribe | Y obtienes |
|---|---|
| `/hoy` | Qué toca hoy en cada cliente: semáforo, evaluaciones vencidas, siguiente paso de su fase, informes pendientes y 1–3 acciones ordenadas |
| `/pregunta "<duda>"` | La respuesta desde la base de conocimiento, con el archivo y la etiqueta de evidencia, a tu nivel |
| `/siguiente-anuncio <cliente>` | Los próximos 1–3 anuncios, elegidos con ventas, citas o pruebas reales (no con el CPL) y listos para producir |
| `/menu` | Todo el catálogo ordenado por fases |
| `/brief-diario programar` | Un brief de salud de tus cuentas cada mañana por Telegram, email o Slack, en solo lectura |

Cada cliente avanza por siete fases, de **F0 Negocio y oferta** a **F6 Escalado**, con una checklist verificable.
El recorrido completo: [docs/recorrido.md](docs/recorrido.md).

## Qué incluye

| Pieza | Cuántas | Qué son |
|---|---|---|
| Skills | 50 skills | Los comandos (`/empezar`, `/economia`, `/construir-landing`, `/lanzar-campana`…), ordenados por fases F0–F6, sistema y agencia |
| Agentes | 20 agentes | Especialistas: analista, auditor, tracking, CAPI, CRM, creativo, redactor, críticos, operador y mentor |
| Guardas | 10 hooks | Protecciones automáticas: dinero, mensajes a contactos, pagos, eventos de prueba, nombres, datos personales, secretos y change log |
| Modos profundos | 5 workflows | Varios agentes en paralelo para auditorías, investigación, estudio creativo, lotes y lanzamientos (avisan del coste antes) |
| Scripts | 25 herramientas | Python para economía, estadística, Meta (campañas, reglas automáticas, formularios y audiencias), GoHighLevel, Stripe, Conversions API (web y mensajería), páginas de captación, registro y análisis creativo, brief, render y vídeo |
| Base de conocimiento | `meta-ads-kb/` | Unas 470.000 palabras sobre Meta Ads verificadas con fuentes y etiquetadas por evidencia, más el sistema operativo y playbooks por modelo de negocio |
| Estilos de salida | `profesor` y `operador` | Con explicación y enlaces a la base, o directo al grano |
| Módulos de vídeo | `modulos/` | Motor de vídeo con IA (opcional, con tu clave) y cutkit para montar vídeo propio |

Catálogo completo con qué hace cada pieza y cuándo usarla: [docs/catalogo/](docs/catalogo/skills.md).

## Lo que cuesta

| Concepto | Coste |
|---|---|
| Meta Ads OS | Gratis (licencia MIT) |
| Claude Code | Necesita un plan de Claude **Pro como mínimo**; con uso intensivo (varios clientes, modos profundos), Max |
| Inversión en Meta | La tuya, con los topes que fijes por cliente |
| Motor de vídeo con IA (opcional) | Lo cobra Google en tu cuenta por segundo de vídeo generado; el sistema lo frena en 5 $ por defecto |
| GoHighLevel, Stripe, Telegram | Tus propias cuentas; el sistema solo lee |

Los modos profundos lanzan varios agentes a la vez y consumen bastante más uso de Claude: por eso te avisan y esperan
tu sí antes de empezar.

## Seguridad

Meta Ads OS toca dinero y personas reales, así que las protecciones no son opcionales:

- **Leer es libre; escribir pide confirmación; activar pide una confirmación específica en el momento.** Todo lo nuevo
  se crea en pausa y los borrados están bloqueados.
- **Topes por cliente**: ningún presupuesto por encima del tope de su ficha. Además, `/configurar-meta` deja puesto un
  límite de gasto del lado de Meta.
- **Solo un agente escribe en Meta** (`operador-meta`) y cada cambio queda en el change log del cliente, con su
  hipótesis y su fecha de evaluación. Sin anotarlo, Claude no puede dar el trabajo por terminado.
- **GoHighLevel**: nunca envía mensajes, emails, SMS ni WhatsApp a tus contactos ni borra nada. **Stripe**: solo
  lectura.
- **Secretos**: tus claves van en `.env`, que Claude no puede leer ni imprimir. **Datos personales** de leads solo en
  la carpeta `privado/` de cada cliente.

Cómo funciona cada capa y qué hacer si algo se filtra: [docs/seguridad.md](docs/seguridad.md).

## Tus datos son tuyos

El repositorio es el **producto**. Tus datos (`contexto/`, `clientes/`, `aprendizajes/`, `informes/`, `logs/` y `.env`)
son tu **instancia**: viven solo en tu ordenador, git no los sube y las actualizaciones no los tocan. Haz copia de
seguridad de esas carpetas en un repositorio privado propio o en tu nube.

## Actualizar

```
/actualizar
```

Enseña qué cambia, actualiza con `git pull --ff-only`, aplica las migraciones de datos que declare la versión (con
copia previa) y pasa `/doctor`. Si has modificado archivos del producto, se para y te explica cómo guardarlos sin
perder nada. Las novedades de cada versión están en [CHANGELOG.md](CHANGELOG.md).

## Estructura

```
meta-ads-os/
├── CLAUDE.md            Cómo trabaja el sistema (se carga en cada sesión)
├── .claude/             Skills, agentes, hooks, workflows, estilos y permisos
├── meta-ads-kb/         Base de conocimiento de Meta Ads
├── herramientas/        Scripts de Python
├── modulos/             Motor de vídeo con IA y cutkit (opcionales)
├── plantillas/          Cliente, contexto, plan de campaña, HTML de estáticos, páginas, integraciones y env.ejemplo
├── docs/                Documentación
├── scripts/             Instalar, actualizar, migraciones y validación
├── tests/               Tests sin red
│
├── contexto/            ┐
├── clientes/            │ Tu instancia: no se versiona
├── aprendizajes/        │
├── informes/  logs/     │
└── .env                 ┘
```

## Documentación

| Documento | Para qué |
|---|---|
| [Guía completa](docs/guia-completa.html) ([PDF](docs/guia-completa.pdf)) | Todo el sistema explicado desde cero, en una sola página: empieza aquí si es tu primera vez |
| [Primeros pasos](docs/primeros-pasos.md) | Instalación detallada, Windows, `/empezar`, copias de seguridad |
| [Recorrido por fases](docs/recorrido.md) | De F0 a F6: qué se consigue en cada fase, con qué skills y cómo se verifica |
| [Guías paso a paso](docs/README.md) | Las 19 guías: GHL, Stripe, CAPI y mensajería, páginas, formularios, webinar, creatividad, reglas automáticas, seguimiento de leads y más |
| [Catálogo](docs/catalogo/skills.md) | Skills, agentes, hooks, workflows y herramientas |
| [Conexiones](docs/conexiones.md) | Meta, GoHighLevel, Stripe, Conversions API y `.env` |
| [Seguridad y permisos](docs/seguridad.md) | Las capas de protección y qué hacer si algo va mal |
| [Agencias con varios clientes](docs/agencias.md) | Accesos de partner, tokens por cliente, informes para clientes y ventas |
| [SaaS](docs/saas.md) | Pruebas, activación y pagos con Stripe, señal desde tu backend |
| [Preguntas frecuentes](docs/preguntas-frecuentes.md) | Lo que pregunta todo el mundo |
| [Solución de problemas](docs/solucion-de-problemas.md) | Errores habituales y su arreglo |

## Licencia

MIT. Ver [LICENSE](LICENSE).
