# Documentación de Meta Ads OS

Si es tu primera vez, lee la [Guía completa](guia-completa.html) (también en [PDF](guia-completa.pdf)).

Empieza por **[Primeros pasos](primeros-pasos.md)** si aún no lo tienes instalado, y por el
**[Recorrido por fases](recorrido.md)** para entender cómo avanza cada cliente. El resto se consulta cuando hace falta.

## Usar el sistema

| Documento | Qué encontrarás |
|---|---|
| [Primeros pasos](primeros-pasos.md) | Requisitos, instalación en Mac, Windows y Linux, `/empezar`, actualizar y copias de seguridad |
| [Recorrido por fases](recorrido.md) | Las cuatro entradas, las fases F0–F6 con sus skills y verificaciones, y la cadencia diaria, semanal y mensual |
| [Conexiones](conexiones.md) | MCP de Meta, GoHighLevel y Stripe, token avanzado, Conversions API y cómo funciona `.env` |
| [Seguridad y permisos](seguridad.md) | Qué se puede hacer sin preguntar, qué pide confirmación, qué está bloqueado y por qué |
| [Agencias con varios clientes](agencias.md) | Accesos de partner, un espacio por cliente, tokens por cliente, informes para clientes y auditorías para vender |
| [SaaS](saas.md) | Prueba gratuita o demo, Stripe, señal desde el backend y cómo decidir con clientes de pago |
| [Preguntas frecuentes](preguntas-frecuentes.md) | Coste, planes, privacidad, idiomas, qué no hace |
| [Solución de problemas](solucion-de-problemas.md) | Instalación, conexiones, hooks, actualizaciones y vídeo |

## Catálogo

| Documento | Piezas |
|---|---|
| [Skills](catalogo/skills.md) | Los 50 comandos, por fases |
| [Agentes](catalogo/agentes.md) | Los 20 especialistas y los dos estilos de salida |
| [Hooks](catalogo/hooks.md) | Las 10 guardas de seguridad |
| [Workflows](catalogo/workflows.md) | Los 5 modos profundos |
| [Herramientas](catalogo/herramientas.md) | Los 25 scripts de Python |

## Guías paso a paso

**Conexiones y señal**

| Guía | Para |
|---|---|
| [GoHighLevel y Meta](guias/ghl-meta.md) | Formularios instantáneos, CAPI de GHL por etapas, Conversion Leads y UTMs |
| [Stripe](guias/stripe.md) | Unir pruebas y pagos con anuncios en un SaaS |
| [Conversions API](guias/capi.md) | Mandar eventos desde n8n, Make o tu backend y probarlos con `test_event_code` |
| [Mensajería medida](guias/mensajeria.md) | Click to WhatsApp, Messenger e Instagram Direct que vuelven a Meta como lead, cualificado o venta |
| [Token avanzado](guias/token-avanzado.md) | Sacar el token de usuario del sistema para las herramientas de Meta |

**Captación**

| Guía | Para |
|---|---|
| [Imán de leads](guias/iman-de-leads.md) | Un diagnóstico o una calculadora que da valor y precualifica |
| [Páginas de captación](guias/construir-landing.md) | Landing, diagnóstico, reserva, gracias y registro a un taller como HTML estático, con píxel, CAPI y consentimiento |
| [Formularios instantáneos](guias/formularios.md) | Un formulario de Meta que filtra antes de la llamada, creado por API o en Ads Manager, y la lectura de sus leads |
| [Webinar o taller](guias/webinar.md) | Del tema y la página de registro a la asistencia, la oferta y el proyecto firmado |

**Creatividad**

| Guía | Para |
|---|---|
| [Análisis creativo](guias/analisis-creativo.md) | Qué elementos de tus anuncios funcionan, no solo qué anuncio |
| [Casos y creadores](guias/casos-y-creadores.md) | Casos con permiso, socios y anuncios de colaboración |
| [Orgánico a anuncios](guias/organico-a-anuncios.md) | Convertir publicaciones que ya funcionaron en anuncios |
| [Vídeo con IA](guias/video-ia.md) | Instalar el motor, su coste y su presupuesto |
| [Vídeo propio](guias/video-propio.md) | Grabar y montar con cutkit |
| [Estáticos](guias/estaticos.md) | Estáticos, carruseles e informes en PDF con plantillas HTML |

**Gestión y ciclo largo**

| Guía | Para |
|---|---|
| [Brief diario](guias/brief-diario.md) | De cero a un brief programado por Telegram, email o Slack |
| [Reglas automáticas](guias/reglas-automaticas.md) | Que Meta pause o avise aunque nadie esté mirando, empezando en modo sombra |
| [Seguimiento de leads](guias/seguimiento-leads.md) | Responder en minutos, que más gente venga a la llamada y que las propuestas no se olviden, con GoHighLevel |
| [Anuncios por etapa](guias/anuncios-por-etapa.md) | Anuncios pequeños para quien no vino a la llamada, tiene una propuesta abierta o dijo «ahora no» |

## Cómo está construido

[Arquitectura](desarrollo/arquitectura.md): producto e instancia, cómo se conectan las piezas, formatos de archivo,
instalación, migraciones, validación y versiones. Para quien quiera adaptar el sistema o contribuir. Antes de un
release, las [evals del criterio](desarrollo/evals.md).
