# Agentes (20) y estilos de salida

Los agentes son especialistas a los que Claude delega una parte del trabajo. Cada uno tiene una lista cerrada de
herramientas: un agente de solo lectura no puede escribir en Meta, GoHighLevel ni Stripe aunque quiera. Viven en
`.claude/agents/<nombre>.md`.

No hace falta llamarlos: las skills los invocan cuando toca. Si quieres uno en concreto, pídelo por su nombre («que lo
revise `revisor-estrategia`»).

**Modelo.** «Sesión» significa que usa el mismo modelo que tu conversación (para razonar a fondo); «Sonnet», un modelo
más barato para trabajo de volumen, para que el sistema rinda bien con el plan Pro.

## Datos y análisis

| Agente | Qué hace | Herramientas | Modelo |
|---|---|---|---|
| `analista-meta` | Saca y descompone los datos de una cuenta: salud diaria, informe semanal, cambio de CPA en CPM·CTR·CVR, anomalías frente a la banda de ruido, fatiga y errores de entrega | Meta en lectura | Sonnet |
| `analista-cuantitativo` | Todo lo que es un número con supuestos: economía unitaria, previsiones, coste marginal, potencia y lectura de tests, incrementalidad y reparto de presupuesto | Meta en lectura y scripts | Sesión |
| `auditor-cuenta` | Auditoría P0–P3 de una cuenta entera, heredada o con problemas, o en modo express para un prospecto | Meta en lectura y web | Sesión |

## Señal y negocio

| Agente | Qué hace | Herramientas | Modelo |
|---|---|---|---|
| `especialista-tracking` | Diagnostica la señal que ya existe: píxel, Conversions API, datasets, calidad de coincidencia, deduplicación, atribución y discrepancias con GA4, CRM o Stripe | Datasets y píxel en lectura | Sesión |
| `ingeniero-capi` | Construye y prueba la señal de vuelta: workflows de GHL por etapa, n8n o Make, webhooks de Stripe, eventos de backend y la mensajería (Click to WhatsApp, Messenger e Instagram Direct), solo con `test_event_code` | Código, web, datasets en lectura y `capi.py` en modo prueba | Sesión |
| `especialista-crm` | Lleva cada anuncio hasta el dinero: leads, citas, shows, ventas y cobro, o registros, pruebas, activaciones y MRR; speed to lead y calidad del lead | GoHighLevel y Stripe en lectura | Sesión |
| `especialista-funnel` | El recorrido después del clic: elegir el camino de conversión, diseñar y auditar landings, diagnósticos y formularios (las páginas las genera `paginas.py` desde `/construir-landing`), y encontrar dónde se rompe entre el clic y el cliente | Navegador y web | Sesión |

## Creatividad

| Agente | Qué hace | Herramientas | Modelo |
|---|---|---|---|
| `estratega-creativo` | Oferta, ángulos, conceptos y hooks; decide el siguiente anuncio con el registro creativo y escribe briefs para cualquier vía | Meta en lectura, Ad Library y web | Sesión |
| `redactor-anuncios` | El texto final en volumen y en la voz del cliente: texto principal, titular, descripción, texto en imagen, hooks de variantes | Lectura y escritura de archivos | Sonnet |
| `investigador-competencia` | Recoge y clasifica anuncios, landings, ofertas e Instagram de la competencia y la voz del cliente en reseñas y foros | Ad Library, navegador y web | Sonnet |
| `productor-ugc` | Convierte un guion aprobado en vídeo con el motor de IA: plan con coste, producción con confirmación de gasto, QA de fotogramas y variantes | Motor de vídeo | Sonnet |
| `editor-video` | Monta vídeo propio (fundador, equipo, creador o demo de pantalla) con cutkit o FFmpeg: hook en 2 s, subtítulos, marca y zonas seguras | cutkit, FFmpeg y transcripción | Sonnet |
| `disenador-estaticos` | Estáticos y carruseles 1:1, 4:5 y 9:16 con plantillas HTML, la marca del cliente y fotos o capturas reales | `render.py` | Sonnet |

## Revisión

| Agente | Qué hace | Herramientas | Modelo |
|---|---|---|---|
| `critico-creativo` | Mira cada pieza como un espectador que hace scroll: primeros 2 s, sin sonido, legibilidad, zonas seguras, claridad de la oferta y coherencia con la landing | Lectura y fotogramas | Sesión |
| `revisor-politicas` | Detecta rechazos probables antes de publicar y reescribe en una versión que sigue vendiendo; deja el veredicto en el `LEEME.md` | Lectura y ayuda de Meta | Sesión |
| `revisor-estrategia` | Abogado del diablo de cada plan: lo contrasta con los principios, los mitos, la regla de paciencia, el ruido estadístico, la capa de verdad y los topes | Solo lectura | Sesión |

## Ejecución

| Agente | Qué hace | Herramientas | Modelo |
|---|---|---|---|
| `operador-meta` | **El único que escribe en Meta** (MCP, `meta_ads.py`, `reglas_meta.py`, `formularios_meta.py` y `audiencias_meta.py`) y el único que hace escrituras aprobadas en GoHighLevel. Solo con un plan aprobado en la conversación: crea en pausa, cambia presupuestos o pujas, deja reglas automáticas, formularios y audiencias, y lo anota todo en el change log | Meta en escritura | Sesión |

## Cliente y conocimiento

| Agente | Qué hace | Herramientas | Modelo |
|---|---|---|---|
| `gestor-cliente` | Informes en el lenguaje del cliente y con la marca de la agencia, preparación de reuniones, expectativas y peticiones de acceso (borradores que nunca envía) | Lectura y escritura de archivos | Sonnet |
| `mentor-meta` | Responde dudas desde la base, citando archivo y etiqueta de evidencia, a tu nivel; prepara y corrige los escenarios de `/entrenar`. No mira cuentas | Base de conocimiento y ayuda de Meta | Sonnet |
| `curador-conocimiento` | Vigila y verifica novedades de Meta, dice a qué cuentas afectan y registra en `aprendizajes/` lo aprendido en cuentas reales | Web y base de conocimiento | Sesión |

## Por qué los asistentes no son agentes

`/empezar`, `/configurar-meta`, `/conectar` y `/brief-diario programar` son skills que se ejecutan en tu conversación:
un agente no puede hacerte preguntas a mitad de su tarea, y estas guías necesitan conversar contigo paso a paso.

---

## Estilos de salida (2)

Cambian cómo te habla Claude, no lo que hace. Se activan en `/config` → estilo de salida (*output style*). El que
eliges en `/empezar` queda anotado en la cabecera de `contexto/preferencias.md` (`estilo`), pero esa nota no lo
activa: hazlo en `/config` o deja fijo el estilo en `.claude/settings.local.json`, que es tuyo y git no sube:

```json
{ "outputStyle": "profesor" }
```

(u `"operador"`; si el archivo ya existe, añade solo esa línea). Se aplica al abrir la siguiente sesión.

| Estilo | Para quién | Cómo responde |
|---|---|---|
| `profesor` | Si estás aprendiendo Meta Ads (recomendado para nivel principiante e intermedio) | Explica el porqué de cada decisión, define los términos la primera vez y enlaza el archivo de la base donde profundizar |
| `operador` | Si gestionas cuentas cada semana | Directo: conclusión, números y siguiente acción, sin explicaciones que ya conoces |
