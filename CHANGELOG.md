# Cambios

Formato: cada versión empieza con `## [x.y.z] — AAAA-MM-DD` (lo lee `scripts/actualizar.sh` para enseñarte las
novedades). Versionado semántico: el segundo número sube con funciones nuevas; el primero, con cambios que piden algo
por tu parte. Las versiones que cambian el formato de tus datos traen una migración en `scripts/migraciones/` y lo dicen
aquí.

## [0.1.0] — 2026-11-10

Primera versión pública.

### Incluye
- **Recorrido por fases** F0–F6 con estado verificable por cliente (`clientes/<slug>/estado.md`) y cuatro entradas:
  `/empezar` (onboarding reanudable de unos 30 minutos), `/hoy`, `/pregunta` y `/siguiente-anuncio`.
- **50 skills**, **20 agentes**, **10 hooks**, **5 workflows**, **25 herramientas** y dos estilos de salida
  (`profesor` y `operador`). Catálogo en `docs/catalogo/`.
- **Dos vías de ejecución en Meta**: el MCP oficial (por defecto) y `herramientas/meta_ads.py` para subir vídeo y
  crear anuncios con las mejoras automáticas desactivadas (modo avanzado, con token de usuario del sistema).
- **Sistemas de negocio**: GoHighLevel y Stripe en solo lectura para decidir con citas, ventas, pruebas y clientes
  de pago por anuncio (`/embudo`, registro creativo).
- **Conversions API**: `/implementar-capi` y `herramientas/capi.py`, con envíos de prueba solo con `test_event_code`.
  Incluye la **mensajería medida**: Click to WhatsApp, Messenger e Instagram Direct vuelven a Meta como lead,
  cualificado o venta, con plantillas para n8n, Make y backend propio.
- **Embudo consultivo** para consultoras, agencias y SaaS que venden con llamada y propuesta: etapas canónicas de lead
  a firma (contrato §16) y un playbook del nicho en la base
  (`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md`).
- **Captación**: `/iman-de-leads` (diagnóstico o calculadora que precualifica), `/construir-landing` y
  `herramientas/paginas.py` (landing, diagnóstico, reserva, gracias y registro a un taller como HTML estático, con
  consentimiento antes del píxel y deduplicación con la CAPI), `/formulario-instantaneo` y
  `herramientas/formularios_meta.py`, y `/webinar`.
- **Protección 24/7**: `/reglas-automaticas` y `herramientas/reglas_meta.py` dejan reglas dentro de Meta que pausan o
  avisan con el ordenador apagado, primero en modo sombra.
- **Ciclo largo**: `/seguimiento-leads` (respuesta, asistencia, no-shows y propuestas abiertas en GHL, sin enviar nunca
  mensajes) y `/anuncios-por-etapa` con `herramientas/audiencias_meta.py` (audiencias por etapa del CRM con grupo de
  control).
- **Producción creativa**: vídeo con IA (motor opcional, con tu clave y un tope de 5 $ por defecto), vídeo propio con
  cutkit, estáticos y carruseles con plantillas HTML, con crítica y revisión de políticas antes de entregar.
- **Inteligencia creativa y prueba social**: `/analisis-creativo` y `herramientas/elementos_creativos.py` (qué elementos
  de los anuncios se asocian a ganar, retención del vídeo, conceptos casi iguales y cuántos conceptos producir al mes),
  `/casos-y-creadores` (casos con permiso y anuncios de colaboración) y `/organico-a-anuncios`.
- **Brief diario** de solo lectura, programable, por Telegram, email o Slack.
- **Base de conocimiento** de Meta Ads (estado a 2026-11-09) con el sistema operativo y playbooks por modelo de
  negocio.
- **Evals del criterio**: 39 casos ficticios con rúbrica que comprueban que el OS razona como un media buyer experto
  (`scripts/evals.py`, [`docs/desarrollo/evals.md`](docs/desarrollo/evals.md)).
- **Instalación y actualización**: `scripts/instalar.sh` (Mac, Linux y Windows con Git Bash), `/actualizar` con
  `git pull --ff-only` y migraciones con copia previa, y `scripts/validar.py` en la integración continua.

### Cambios de interfaz
- **Nombres de eventos del CRM**: una sola tabla canónica en el contrato §16 (`LeadCualificado`, `LlamadaAsistida`…).
  `capi.py construir --etapa` sin `--canal` ya no da error: pone el `event_name` de esa tabla. Con un `--evento`
  distinto del de la etapa, sale con código 1.
- **`capi.py construir` ya no se inventa el `event_id`**: si falta, `validar` avisa de que el evento no deduplica.
- **Plantilla nueva** en `plantillas/integraciones/paginas/` (n8n, Make y backend propio) para recibir los envíos de
  las páginas: solo reenvía a la CAPI con `enviar_a_meta: true` y, con base `consentimiento`,
  `consentimiento_marketing: "si"`.
- **`herramientas/paginas.py`**:
  - el banner de consentimiento sale también en «solo servidor» (sin píxel);
  - un config con una sola página la escribe como `index.html` por defecto;
  - `validar` da `form.reservado` si un campo usa como id una clave del envío (`origen`, `momento`, `ref`…);
  - `evento.zona_horaria` (IANA; si falta, la `zona_horaria` de la ficha; si tampoco, `Europe/Madrid`), y `generar`
    se para si el desfase escrito no es el de esa fecha;
  - la moneda sale de la ficha del cliente cuando el config no la fija (antes, EUR), en los importes y en el
    `currency` de los eventos.
