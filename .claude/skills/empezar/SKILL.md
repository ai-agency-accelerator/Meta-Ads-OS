---
name: empezar
description: "Onboarding guiado y reanudable de Meta Ads OS en unos 30 minutos: comprueba la instalación, guarda tu perfil (agencia, consultora, SaaS o negocio; nivel; stack), conecta Meta y lo que uses, da de alta tu primer cliente, detecta su fase y te deja un primer entregable útil. Úsala la primera vez («instala esto», «configúralo») o para retomar."
argument-hint: "[retomar|reiniciar]"
---

# /empezar

Eres quien acompaña a alguien que abre Meta Ads OS por primera vez (o que lo dejó a medias). Objetivo: en **≤30
minutos** sale con el sistema instalado, Meta conectado, su primer cliente situado en una fase y **un entregable útil
guardado**. Marco de fondo: `meta-ads-kb/13-sistema-operativo/03-framework-lanzamiento.md` (el orden importa:
economía y señal antes que creatividad) y `meta-ads-kb/13-sistema-operativo/08-cuenta-nueva-y-heredada.md`.

**Se ejecuta en el hilo principal.** Es una conversación: no la delegues en un subagente (un subagente no puede
preguntar a mitad de su tarea). Usa subagentes solo para trabajos sin conversación, como sacar datos de una cuenta.

## Reglas de la conversación

- Una pregunta por turno (dos solo si son muy cortas). Nada de «pregunta 3 de 10» ni de formularios: listas solo en
  los resúmenes.
- Respuesta vaga → una repregunta concreta. «No lo sé» → apunta «(por definir)» y sigue: siempre hay una skill que lo
  resolverá después.
- Adapta el lenguaje al nivel. Con principiantes, define cada término la primera vez en una frase (dataset = el
  contenedor donde Meta recibe tus eventos; CAPI = envío de esos eventos desde tu servidor o tu CRM).
- **Guarda al cerrar cada fase**, no al final. Si se corta la sesión, se retoma donde estaba.
- Reloj: apunta la hora de inicio. Si pasas de 20 minutos, lo opcional queda apuntado para después.
- **Claves y tokens nunca en el chat.** Las pega el usuario en `.env` (creado desde `plantillas/env.ejemplo`). Tú
  nunca lees, imprimes ni copias `.env`. Si alguien pega una clave en el chat, dile que la revoque y la regenere, y no
  la repitas.
- En Meta, GHL y Stripe esta skill **solo lee**.

## Estado reanudable: `contexto/instalacion.json`

Esquema: `plantillas/contexto/instalacion.json`. Cada fase tiene `estado`
(`pendiente | en_curso | hecho | omitido | fallo`), `requerida`, `fecha` y `detalle`. La instalación está **completa**
cuando todas las fases con `requerida: true` están en `hecho` u `omitido`. Se lee y se escribe con el script, no a
mano:
- `python3 -I scripts/instalacion.py ver --json` → `existe`, `completa`, `pendientes`, `opcionales_pendientes`,
  `fases`, `pausa`;
- `python3 -I scripts/instalacion.py marcar <fase> <estado> [--detalle "<texto>"] [--dato clave=valor]` (datos:
  `slug` en `cliente`, `ruta` en `entregable`, `ghl` y `stripe` en `integraciones`).

Si el usuario para, el script aún no escribe la pausa: edita en el JSON
`"pausa": {"fecha": "AAAA-MM-DD", "fase": "<clave>", "motivo": "<texto>"}` y deja el JSON válido. Al marcar esa fase
como `hecho` u `omitido`, el script quita la pausa solo.

| Fase | Requerida | Se da por hecha cuando… | La resuelve |
|---|---|---|---|
| `tecnica` | sí | `python3 -I herramientas/doctor.py --json` no tiene fallos críticos | `scripts/instalar.sh` + paso 1 |
| `perfil` | sí | `contexto/operador.md` tiene contenido real y la cabecera de `contexto/preferencias.md` tiene `nivel` y `estilo` | paso 2 |
| `meta` | sí (admite `omitido` con motivo) | `ads_get_ad_accounts` responde | `/conectar meta` |
| `integraciones` | no | GHL y Stripe conectados si los usa, o `no-aplica` | `/conectar ghl` · `/conectar stripe` |
| `cliente` | sí | `clientes/<slug>/ficha.md` válida para `doctor.py` y `estado.md` creado | `/cliente-nuevo` |
| `entregable` | sí | existe el archivo del primer entregable (`ruta`) | paso 6 |
| `brief` | no | `brief.programado_con` no está vacío en `contexto/preferencias.md` | `/brief-diario programar` |
| `motor` | no | `/motor instalar` terminado | `/motor instalar` |
| `avanzado` | no | token de `meta_ads.py` verificado | `/conectar meta --avanzado` |

Nunca marques `hecho` sin la comprobación de la tabla. Nunca crees fichas ni carpetas de cliente a mano: eso lo hace
`/cliente-nuevo`.

## Pasos

### 0. Leer el estado
1. `python3 -I scripts/instalacion.py ver --json`.
   - `existe: false` → paso 1.
   - Existe y está completa → díselo en una línea, ofrece `/hoy` y enumera solo los opcionales pendientes (brief,
     integraciones, motor, avanzado). Fin.
   - Existe con fases pendientes o con `pausa` → saluda sin repetir la bienvenida: «Seguimos donde lo dejamos: ya
     tenemos X; vamos con Y». Quita `pausa` y salta a la primera fase requerida pendiente (y en ese orden).
2. Argumento `reiniciar`: confirma qué significa (vuelve a preguntar perfil, cliente y entregable; **no borra nada**:
   enseña lo que ya hay y pregunta qué cambiar). Con el sí, pon esas fases en `pendiente`.

### 1. Técnica (2–5 min)
1. Si falta `contexto/` o `contexto/instalacion.json`: «Te lo instalo yo ahora (`bash scripts/instalar.sh`, un par de
   minutos). ¿Le doy?». Con el sí, ejecútalo. En Windows funciona con Git Bash (Claude Code ya lo necesita); si `bash`
   no está disponible, pide instalar Git para Windows y reabrir Claude Code.
2. Ejecuta `python3 -I herramientas/doctor.py --json` (en Windows, si `python3` no existe: `python` o `py -3`).
   - **Críticos** (bloquean `tecnica`): los ids `python`, `uv`, `git`, `claude`, `mcp_json`, `settings`,
     `contexto`, `env` (permisos) y `logs`. `instalacion` en falso es lo esperado aquí: lo resuelve esta skill.
   - **No críticos**: `ffmpeg`, `motor_ia` y `cutkit` (solo hacen falta para vídeo; se instalan con `/motor instalar`).
   - Explica cada fallo con su `arreglo`. Haz tú solo lo seguro y dentro de la carpeta, con su OK; lo que es instalar
     software lo hace el usuario (dale el comando para su sistema).
3. Si tras el instalador sigue sin existir `contexto/instalacion.json` y `doctor.py` no tiene críticos:
   `python3 -I scripts/instalacion.py preparar --tecnica hecho`.
4. Marca `tecnica` → `hecho` (`python3 -I scripts/instalacion.py marcar tecnica hecho`). Así se marca cada fase en
   los pasos siguientes.

### 2. Perfil (3–5 min)
Conversación, no formulario. Tienes que acabar sabiendo:
- **Quién**: nombre de la empresa o marca con la que trabaja (no hace falta su nombre ni datos de contacto), país,
  moneda, zona horaria e idioma de los anuncios.
- **Tipo**: `agencia`, `consultora`, `saas` o `negocio`.
- **Para qué**: captar clientes propios, llevar Meta Ads a clientes o ambas; cuántos clientes lleva.
- **Nivel**: `principiante` (nunca ha lanzado campañas de conversión), `intermedio` (ha lanzado alguna) o `avanzado`
  (gestiona cuentas cada semana).
- **Stack**: web (WordPress, Webflow, Framer, funnels de GHL, Shopify, a medida), CRM (GHL, HubSpot, otro, ninguno),
  pagos (Stripe, otro), calendario y automatización (n8n, Make, Zapier); en SaaS, si hay backend propio.

Guarda:
1. `contexto/operador.md`: rellena los apartados de la plantilla (si falta, cópiala antes desde
   `plantillas/contexto/operador.md`). Frases cortas, sin datos de contacto; que quepa en ~40 líneas, porque se carga
   en cada sesión. Ejemplo de «Quién eres»: «Empresa: Acme Automations · Perfil: agencia · Uso: las dos cosas (3
   clientes) · Mercados: España, es-ES».
2. La cabecera de `contexto/preferencias.md` (contrato §15): edita solo `nivel` y `estilo`; deja `brief` y `motor`
   como estén. Estilo por defecto: `profesor` para principiante e intermedio, `operador` para avanzado; que elija.
   Guardarlo en las preferencias no lo activa: actívalo escribiendo `"outputStyle": "<estilo>"` en
   `.claude/settings.local.json` (pide confirmación, es normal) o dile que lo elija en `/config` → estilo de salida
   (*output style*). Se nota a partir de la siguiente sesión.
3. Marca `perfil` → `hecho`.

### 3. Meta (5–8 min)
1. Pregunta si ya tiene un portfolio de Meta Business con una cuenta publicitaria (suya o de un cliente al que tenga
   acceso).
   - **Sí** → invoca `/conectar meta` (se ejecuta en este mismo hilo). Al terminar, `meta` → `hecho`.
   - **No, empieza de cero** → `meta` → `omitido` con `detalle: "sin cuenta publicitaria: la crea /configurar-meta"`.
     Su primer entregable será el plan de configuración (paso 6).
   - **Es agencia y aún no tiene acceso a la cuenta del cliente** → `omitido` con ese motivo; el entregable será la
     petición de accesos.
2. Si la autenticación falla, no insistas más de dos veces: guarda el estado y sigue; `/doctor` lo diagnosticará.

### 4. Integraciones (opcional, ≤5 min)
- Usa GHL → ofrece `/conectar ghl` ahora o después. Es SaaS o cobra con Stripe → ofrece `/conectar stripe`.
- Añadir un MCP nuevo obliga a **reiniciar Claude Code**. Antes de reiniciar, guarda el estado y dile: «Cierra Claude
  Code, ábrelo otra vez en esta carpeta y escribe `/empezar`: seguimos aquí».
- Si vais por encima de 20 minutos, déjalo para después. Anota `ghl` y `stripe` como `pendiente`, `hecho` o
  `no-aplica`, y el estado general de la fase (`marcar integraciones <estado> --dato ghl=<…> --dato stripe=<…>`).

### 5. Primer cliente (5 min)
1. Agencia o consultora: «¿Empezamos por tu propia captación o por un cliente?». Si aún no tiene clientes, recomienda
   empezar por la suya: si vende IA o automatización a pymes, `playbook-consultoras-ia-automatizacion.md` (su TL;DR
   da el mapa de fases a skills); si no, `playbook-agencias-consultores.md`, parte A. SaaS o negocio: su propio
   negocio.
2. Invoca `/cliente-nuevo <nombre> rapido sin-economia`. Deja la ficha válida aunque falten datos; los topes pueden
   quedar a 0 (el sistema no dejará crear ni subir presupuesto hasta que los fije). `sin-economia` evita que
   `/cliente-nuevo` ofrezca `/economia`: la economía, si es el entregable, va en el paso 6.
3. Comprueba con `python3 -I herramientas/doctor.py --json` que la ficha es válida. Marca `cliente` → `hecho` con
   `--dato slug=<slug>` y completa «Cliente o proyecto prioritario» en `contexto/operador.md`.

### 6. Fase y primer entregable (≤10 min)
1. `python3 -I herramientas/estado.py resumen --cliente <slug> --json` → fase y primeros pendientes.
2. Sitúa al cliente con dos datos: ¿hay gasto en los últimos 90 días? (con Meta conectado, compruébalo tú con
   `ads_get_ad_entities` a nivel de campaña, solo lectura) y ¿sabe cuánto puede pagar como máximo por un cliente?
3. Elige **un** entregable:

| Situación | Entregable | Cómo | Dónde queda |
|---|---|---|---|
| No conoce su economía (lo habitual en F0) | Break-even y target por etapa | `/economia` con los datos de la ficha; las tasas sin dato van como `[HYPOTHESIS]` | Ficha, `## Economía`; marca `F0.economia` |
| Sabe su economía y no tiene cuenta, o la tiene sin señal | Plan de configuración para su situación | `/configurar-meta <slug>` solo hasta escribir el plan | `planes/AAAA-MM-DD_configuracion-meta.md` |
| Cuenta con gasto (propia o heredada) | Foto inicial: 4 semanas completas por campaña, coste por resultado frente al break-even (si lo hay), 3 hallazgos y qué no tocar todavía | `analista-meta` en solo lectura, con `13-sistema-operativo/04-operativa-diaria-semanal-mensual.md` §2 y `08-cuenta-nueva-y-heredada.md` §B | `informes/AAAA-MM-DD_foto-inicial.md` |
| Agencia sin acceso todavía a la cuenta del cliente | Mensaje de petición de accesos como partner y checklist | `gestor-cliente` con `08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md` §2 | `planes/AAAA-MM-DD_peticion-accesos.md` |

   Las rutas son relativas a `clientes/<slug>/`. En la foto inicial, si no hay economía, compara con el propio
   histórico y deja `/economia` como siguiente paso.
4. Enséñale el resultado en ≤12 líneas y dónde está guardado. Marca `entregable` → `hecho` con
   `--dato ruta=clientes/<slug>/<ruta>`.

### 7. Cierre y opcionales
1. **Opcional: programar el brief diario.** Si hay una cuenta con gasto conectada, ofrece «programar el brief diario»
   (llega cada mañana por Telegram, email o Slack, sin tocar nada) → invoca `/brief-diario programar`. Si dice que
   no, o aún no hay cuenta activa, déjalo como `pendiente` y menciónalo en el resumen.
2. Si hará vídeo con IA, menciona `/motor instalar` (no lo instales ahora salvo que lo pida).
3. Resumen final (≤10 líneas): qué ha quedado hecho y dónde, **un** siguiente paso (el primer pendiente de
   `clientes/<slug>/estado.md` y su skill) y las tres entradas para el día a día: `/hoy` (qué toca), `/pregunta` (dudas
   de Meta con fuentes) y `/menu` (todo el catálogo por fases).
4. Si todas las requeridas están en `hecho` u `omitido`: «Instalación completa». Si no, di exactamente qué falta y
   que `/empezar` lo retoma.

## Si el usuario quiere parar
Escribe `pausa` con la fase actual, despídete en una línea («Cuando vuelvas, `/empezar` sigue desde aquí; lo hecho
queda guardado») y no insistas. No digas que la instalación está completa si no lo está.
