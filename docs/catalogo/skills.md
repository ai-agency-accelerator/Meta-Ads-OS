# Skills (50)

Las skills son los comandos: escribes `/nombre` y Claude sigue sus pasos, que citan los marcos de la base de
conocimiento por ruta. Viven en `.claude/skills/<nombre>/SKILL.md`. `/menu` las enseña desde tu sesión, filtradas por
fase o por palabra clave (`/menu F3`, `/menu tracking`).

Claude también puede usar una skill por su cuenta cuando la conversación lo pide. Las marcadas **(manual)** no: escriben
en Meta, gastan dinero o actualizan el sistema, así que solo se ejecutan cuando tú las escribes.

**Modo profundo.** Algunas skills aceptan `profundo`: lanzan un [workflow](workflows.md) con varios agentes en
paralelo. Antes te dicen el coste aproximado y esperan tu sí.

## Entradas

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/empezar` | Onboarding guiado y reanudable de unos 30 minutos: instalación, perfil, conexión con Meta, primer cliente y primer entregable | `/empezar` · `/empezar reiniciar` |
| `/hoy` | Qué toca hoy en todos tus clientes, sin coste: semáforo del brief, evaluaciones vencidas, siguiente punto de la fase, informes pendientes y cola de producción | `/hoy` · `/hoy acme` |
| `/pregunta` | Dudas de Meta respondidas desde la base, con archivo y etiqueta de evidencia, a tu nivel. Para conceptos, no para analizar una cuenta | `/pregunta "¿qué reinicia el aprendizaje?"` |
| `/siguiente-anuncio` | Los próximos 1–3 anuncios elegidos con la capa más baja de verdad que tenga datos suficientes, con hipótesis, test, vía de producción y coste | `/siguiente-anuncio acme` · `/siguiente-anuncio acme profundo` |

## Sistema

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/menu` (manual) | El mapa del sistema por fases, con una línea por skill y por dónde empezar | `/menu` · `/menu agencia` |
| `/doctor` | Diagnóstico de la instalación y las conexiones, con el arreglo concreto de cada fallo | `/doctor` |
| `/actualizar` (manual) | Versión nueva sin tocar tus datos: enseña qué llega, `git pull --ff-only`, migraciones y `/doctor` | `/actualizar comprobar` |
| `/conectar` | Conecta y verifica el MCP de Meta, GoHighLevel y Stripe; con `--avanzado`, el token de `meta_ads.py` | `/conectar meta` · `/conectar ghl` · `/conectar meta --avanzado` |
| `/motor` | Estado, gasto, proyectos e instalación del motor de vídeo con IA. Consúltala antes de producir | `/motor` · `/motor instalar` |

## F0 · Negocio y oferta

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/cliente-nuevo` | Alta de un cliente o de tu negocio en `clientes/<slug>/` con su ficha y su estado de fases | `/cliente-nuevo "Clínica Sonrisa"` · `/cliente-nuevo Nimbo rapido` |
| `/economia` | Cuánto puedes pagar por lead, cita, show, venta, prueba o cliente de pago; modo `prevision` para planes y propuestas | `/economia leadgen acme` · `/economia prevision acme` |
| `/oferta` | Construir o mejorar la oferta antes de gastar: promesa, mecanismo, prueba, garantía, bonus, precio y oferta de entrada | `/oferta acme mejorar` |
| `/disenar-funnel` | Elegir y especificar el camino de conversión, con su evento de optimización, eventos a medir y coste máximo por etapa | `/disenar-funnel acme` · `/disenar-funnel acme vsl-calendario` |
| `/iman-de-leads` | El imán de la oferta de entrada: diagnóstico o calculadora que da valor y precualifica, con supuestos con fuente, veredicto honesto y valor del evento, probado con escenarios | `/iman-de-leads acme diagnostico "facturas y albaranes"` |

## F1 · Infraestructura y señal

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/configurar-meta` | Dejar Meta listo según tu situación: de cero, sin señal, cuenta heredada o agencia entrando como partner, con los topes del lado de Meta | `/configurar-meta acme heredada` |
| `/implementar-capi` | Construir la señal de vuelta: píxel con `event_id` y Conversions API desde GHL, n8n, Make, Stripe o tu backend, y la de mensajería (Click to WhatsApp, Messenger, Instagram Direct), probada con `test_event_code` | `/implementar-capi acme ghl` · `/implementar-capi acme mensajeria` |
| `/audiencias` | Listas del CRM o de Stripe en Meta: excluir clientes, semillas por valor y segmentos por etapa | `/audiencias nimbo excluir` |
| `/construir-landing` | Las páginas de captación con `paginas.py` (landing, diagnóstico, reserva con o sin VSL, gracias o registro a un taller): marca del cliente, consentimiento antes del píxel, UTMs y `event_id` compartido con la CAPI. No las despliega | `/construir-landing acme diagnostico` · `/construir-landing validar clientes/acme/paginas/diagnostico` |
| `/formulario-instantaneo` (manual) | El formulario instantáneo de Meta para B2B: preguntas de cualificación, lógica condicional, privacidad, creación por API con confirmación o guía para Ads Manager, conexión con GHL y calidad de los leads por anuncio | `/formulario-instantaneo acme diagnostico` · `/formulario-instantaneo acme auditar <form_id>` |
| `/landing` | Auditoría de una landing o formulario ya publicados para tráfico de Meta: tracking, velocidad, message match, oferta y CTA. Para construirlos, `/construir-landing` | `/landing https://acme.example.com/demo acme` |

## F2 · Investigación

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/competencia` | Anuncios, landings, ofertas e Instagram de la competencia en un dataset con patrones y huecos; `vigilar` hace una foto semanal | `/competencia acme` · `/competencia vigilar acme` · `/competencia profundo acme` |
| `/voz-cliente` | Deseos, dolores, objeciones y lenguaje literal de tus clientes, de llamadas, formularios, reseñas y foros | `/voz-cliente nimbo` |

## F3 · Creatividad

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/brief-creativo` | Estrategia creativa de un lote: matriz de ángulos, conceptos, hooks, briefs y plan de test. Para cuentas u ofertas nuevas | `/brief-creativo acme 4` |
| `/producir-video` (manual) | Un vídeo a partir de un brief por la vía `ia` (motor, gasta dinero), `propio` (guion y montaje con cutkit) o `hibrido` | `/producir-video acme <brief> propio` |
| `/producir-estatico` | Estáticos y carruseles con plantillas HTML, la marca del cliente y fotos o capturas reales | `/producir-estatico nimbo <brief> carrusel` |
| `/variantes` | Iteraciones de una pieza ya producida: hooks, CTA, subtítulos, formatos y música (casi gratis), o voz e idioma (de pago) | `/variantes acme <carpeta> hooks` |
| `/revisar-anuncio` | Revisión de políticas antes de publicar, con reescrituras que siguen vendiendo y un veredicto que queda en el `LEEME.md` | `/revisar-anuncio <carpeta del creativo> acme` |
| `/analisis-creativo` | Qué elementos de tus anuncios (quién habla, primer fotograma, texto inicial, duración, demo, prueba, CTA…) se asocian a ganar, la retención del vídeo, los conceptos casi iguales y cuántos conceptos nuevos producir al mes | `/analisis-creativo acme` · `/analisis-creativo acme suministro` |
| `/casos-y-creadores` | Proyectos entregados convertidos en casos con permiso y afirmaciones aprobadas, y clientes, expertos o creadores como socios en anuncios de colaboración | `/casos-y-creadores acme caso` · `/casos-y-creadores acme creadores` |
| `/organico-a-anuncios` | El contenido orgánico propio que ya funcionó, puntuado por retención, guardados y comentarios con intención, convertido en anuncio (publicación existente o clip) | `/organico-a-anuncios acme instagram` |

## F4 · Lanzamiento

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/lanzar-campana` (manual) | Campaña nueva con gates, plan revisado y aprobado, creación en pausa, previsualizaciones y activación solo con tu confirmación | `/lanzar-campana acme` · `/lanzar-campana acme profundo` |
| `/publicar-anuncios` (manual) | Subir un lote aprobado a una campaña que ya existe, en pausa y con las mejoras automáticas desactivadas | `/publicar-anuncios acme <lote>` |
| `/test-creativo` | Diseñar o leer un experimento con potencia estadística: creativo, A/B, Conversion Lift o geográfico | `/test-creativo acme diseñar creativo` |
| `/webinar` | Un webinar o taller de captación de punta a punta: tema, páginas, campañas por fase, recordatorios, guion con la oferta y medición hasta el proyecto firmado | `/webinar acme "facturas sin teclear" --fecha 2026-12-03` · `/webinar medir acme 2026-12-03_webinar-facturas` |

## F5 · Operación

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/brief-diario` | Salud diaria de tus cuentas en solo lectura, guardada y enviada por Telegram, email o Slack; `programar` la deja automática | `/brief-diario` · `/brief-diario programar` |
| `/informe-semanal` | Informe interno de la última semana completa, de arriba abajo, con como mucho 3 decisiones | `/informe-semanal acme` |
| `/revision-mensual` | Economía, coste marginal, incrementalidad, aprendizajes por ángulo y plan del mes | `/revision-mensual acme 2026-11` |
| `/diagnostico` | Un síntoma concreto con datos reales y los árboles de decisión, hasta una causa y una acción | `/diagnostico acme "sube el CPA desde el martes"` |
| `/ejecutar-cambio` (manual) | Un cambio en una cuenta que ya funciona, con plan, regla de paciencia, topes, aprobación y change log | `/ejecutar-cambio acme "subir el conjunto principal a 80 €/día"` |
| `/embudo` | El dinero después del clic: cohortes por semana o por anuncio desde GHL o Stripe, y en qué etapa se rompe | `/embudo acme anuncio` |
| `/rescate-cuenta` | Protocolo para rechazos en cadena, restricciones, hackeos o fallos de pago. Nunca circunvención | `/rescate-cuenta acme "cuenta restringida"` |
| `/reglas-automaticas` (manual) | Protección 24/7 con las reglas automáticas de Meta: audita las que hay, propone un conjunto desde la ficha (pausa sin conversión a 4× el CPA, o 3× con volumen; gasto fuera de tope; alertas) y lo crea en modo sombra con tu sí | `/reglas-automaticas acme` · `/reglas-automaticas acme activo` |
| `/seguimiento-leads` | El seguimiento comercial tras el lead en GHL: velocidad de respuesta, recordatorios, no-shows, propuestas abiertas y reactivación. Deja los workflows con textos; nunca envía mensajes | `/seguimiento-leads acme asistencia` · `/seguimiento-leads acme medir` |
| `/anuncios-por-etapa` (manual) | Anuncios para etapas del CRM (no se presentó, propuesta enviada, perdido por timing, clientes), con exclusiones, presupuesto pequeño y grupo de control | `/anuncios-por-etapa acme disenar` · `/anuncios-por-etapa acme medir no-show` |

## F6 · Escalado

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/escalar` | Si se puede escalar y cómo: condiciones previas, coste marginal, palanca correcta y plan por escalones dentro de los topes | `/escalar acme` |
| `/auditoria` | Auditoría completa P0–P3 de una cuenta con acceso, con plan 30/60/90. Solo lectura | `/auditoria acme` · `/auditoria profundo acme` |

## Agencia y aprendizaje

| Skill | Para qué | Ejemplo |
|---|---|---|
| `/informe-cliente` | El informe interno convertido en uno para el cliente, sin jerga y con la marca de tu agencia, en Markdown y PDF. Nunca se envía solo | `/informe-cliente clinica-sonrisa mensual 2026-11` |
| `/auditoria-express` | Auditoría de un prospecto sin acceso a su cuenta, solo con fuentes públicas, para venderle | `/auditoria-express "Clínica Sonrisa" España` |
| `/entrenar` | Escenarios prácticos de agencia y SaaS que respondes tú y corrige `mentor-meta` | `/entrenar diagnostico` · `/entrenar progreso` |
| `/novedades-meta` | Qué ha cambiado en Meta, verificado, y a qué clientes afecta; también registra aprendizajes propios | `/novedades-meta` · `/novedades-meta aprendizaje acme "<qué se observó>"` |

---

¿Echas algo en falta? Pregunta primero con `/pregunta` o `/menu <palabra>`: casi siempre hay una skill que lo cubre.
Si quieres reglas propias para todas las skills, escríbelas en `contexto/operador.md` → «Reglas propias».
