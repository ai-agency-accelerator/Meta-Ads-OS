# Preguntas frecuentes

## Antes de empezar

**¿Necesito saber programar?**
No. Todo se hace conversando con Claude Code. Lo más técnico que harás es pegar una clave en `.env` con tu editor, y
el sistema te dice exactamente dónde.

**¿Me basta el plan Pro de Claude?**
Sí para el uso normal: los agentes de trabajo de volumen (datos, textos, investigación, montaje) usan un modelo más
barato para que el plan rinda. Los modos profundos lanzan muchos agentes a la vez y consumen bastante más: resérvalos
para lo importante. Si llevas muchos clientes o los usas a menudo, el plan Max te dará margen.

**¿Funciona en Windows?**
Sí, con Git Bash (viene con Git para Windows, que Claude Code ya necesita). Ver
[Primeros pasos](primeros-pasos.md#windows).

**¿Necesito una cuenta de Meta para instalarlo?**
No. Si empiezas de cero, `/empezar` lo apunta y tu primer entregable es el plan para montarla con `/configurar-meta`.

**¿Puedo usarlo si no uso GoHighLevel ni Stripe?**
Sí. Sin CRM conectado, el sistema decide con lo que tiene (resultados de Meta y lo que tú le cuentes) y te avisa de que
está decidiendo con una capa de verdad más alta de lo ideal. Con otro CRM (HubSpot u otro), exporta los resultados por
anuncio a un CSV con columnas como `ad_id`, `leads`, `citas` o `ventas`: `herramientas/registro_creativo.py` los
cruza igual.

## Dinero y seguridad

**¿Puede gastar dinero sin que yo lo sepa?**
No. Todo lo nuevo se crea en pausa; cada escritura en Meta te pide confirmación y activar pide otra aparte; ningún
presupuesto puede superar el tope de la ficha del cliente, y además hay un límite configurado en el propio Meta. El
motor de vídeo con IA pide confirmación con el coste antes de cada orden de pago y se frena en 5 $ por defecto. Detalle
en [Seguridad](seguridad.md).

**¿Puede escribir a mis leads o a mis clientes?**
No. La guarda de GoHighLevel bloquea cualquier SMS, WhatsApp, email o llamada a contactos. Los mensajes para tus
clientes de agencia los deja como borradores que envías tú.

**¿Dónde quedan mis datos?**
En tu ordenador: `contexto/`, `clientes/`, `aprendizajes/`, `informes/`, `logs/` y `.env` no se suben a ningún
repositorio. Lo que Claude lee durante una sesión forma parte de tu conversación con Claude, como en cualquier uso de
Claude Code; por eso los datos personales de leads se quedan en `clientes/<slug>/privado/` y el análisis se hace con
IDs y agregados.

**¿Por qué no puede leer mi `.env`?**
Para que una clave nunca aparezca en una conversación, en un log o en una captura. Las herramientas lo cargan solas
cuando lo necesitan.

## Cómo decide

**¿Por qué no me deja evaluar un cambio a los dos días?**
Porque con menos de 7 días, menos de 30–50 eventos o la ventana de atribución sin madurar, lo que ves es sobre todo
ruido. Solo se actúa antes si algo está roto (`meta-ads-kb/09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md`).

**¿Por qué no elige los anuncios ganadores por el CPL?**
Porque un lead barato que no va a la llamada o no compra es caro. El sistema decide con la capa más baja de verdad que
tenga datos suficientes: venta > cita o show > cualificado > CPL (en SaaS, cliente de pago > prueba activada > prueba >
registro). Las métricas antes del clic solo descartan perdedores.

**¿Por qué desactiva las mejoras automáticas de Meta?**
Porque cambian tu anuncio sin avisarte (doblaje, música, recortes, textos generados) y entonces no sabes qué estás
probando. La ficha de cada cliente tiene `mejoras_automaticas: off | revisar | on`; por defecto, `off`.

**¿Qué significan `[OFFICIAL META]`, `[EMPIRICAL]`, `[HYPOTHESIS]`…?**
Cuánta confianza merece cada afirmación: documentación oficial de Meta, observado en datos o casos, inferencia sólida,
hipótesis o tema en disputa entre expertos. Están explicadas en `meta-ads-kb/00-CONVENCIONES.md`.

**¿La base de conocimiento está al día?**
Su estado está fechado en `meta-ads-kb/00-ESTADO-ACTUAL-2026.md`. `/novedades-meta` revisa lo que ha cambiado desde
entonces, lo verifica y te dice a qué clientes afecta. Las actualizaciones del producto traen la base revisada.

## Creatividad

**¿Sube los vídeos a Meta?**
El MCP oficial de Meta no permite subir vídeo. Con el token avanzado (`/conectar meta --avanzado`),
`/publicar-anuncios` los sube con `herramientas/meta_ads.py`; sin él, te guía para subirlos en Ads Manager.

**¿Tengo que usar vídeo con IA?**
No. Hay tres vías: vídeo con IA (motor opcional con tu clave de Google), vídeo propio (te prepara el guion y la lista
de planos, y lo monta con cutkit) e híbrido. También estáticos y carruseles con plantillas HTML.

**¿Escribe los textos en mi idioma?**
El sistema habla en español; los anuncios se escriben en el idioma de cada mercado que pongas en el perfil y en la
ficha del cliente, en la voz que saque de `/voz-cliente`.

## Lo que no hace (todavía)

- Google Ads, TikTok Ads u otras plataformas: solo Meta (Facebook, Instagram, Messenger, WhatsApp).
- Publicar tus páginas: `/construir-landing` las construye (landing, diagnóstico, reserva, gracias y registro a un
  taller, como HTML estático con píxel, CAPI y consentimiento), pero las subes tú a tu hosting o a GHL.
- Moderar comentarios de anuncios: requiere permisos de Página que el MCP de Meta no tiene.
- Conectarse a tu WhatsApp, Messenger o Instagram: la medición de mensajería se construye con `/implementar-capi`
  (`capi.py` y plantillas para n8n, Make o tu backend), pero quien escucha los webhooks y envía los eventos es tu
  automatización, no el sistema ([guía](guias/mensajeria.md)).
- Enviar mensajes a tus leads: `/seguimiento-leads` deja escritos los workflows y los textos; los activas tú en GHL.
- Un panel web: todo vive en tu carpeta y en Claude Code.

## Adaptarlo

**¿Puedo cambiar una skill o un agente?**
Puedes, pero cada cambio en un archivo del producto choca con las actualizaciones (`/actualizar` se para y te pide
guardarlo aparte). Para adaptar el comportamiento, escribe tus reglas en `contexto/operador.md` → «Reglas propias»:
se cargan en cada sesión y nunca chocan.

**¿Cómo propongo una mejora?**
Si algo de la base contradice lo que ves en tus cuentas, regístralo con `/novedades-meta aprendizaje <cliente> "<qué
observaste>"`: queda en `aprendizajes/` con su evidencia, listo para compartirlo con el equipo del producto.
