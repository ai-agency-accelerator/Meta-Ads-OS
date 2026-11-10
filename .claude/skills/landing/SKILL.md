---
name: landing
description: "Audita una landing o formulario web para tráfico de Meta: tracking (píxel, fbclid, UTMs, consentimiento), velocidad móvil y navegador in-app, message match con el anuncio, oferta, prueba y CTA, formulario o calendario y políticas del destino. Devuelve un semáforo y 5–10 cambios priorizados con cómo medirlos. Construirla: /construir-landing."
argument-hint: "<url> [cliente] [anuncio o ángulo]"
---

# /landing

Entrada: `$ARGUMENTS` (URL y, opcionalmente, cliente y el anuncio o ángulo que lleva tráfico). Esta skill audita: no
edita la landing. Para construirla o rehacerla, `/construir-landing` (y `/iman-de-leads` si falta la oferta de
entrada); para un formulario instantáneo, `/formulario-instantaneo`. Para un síntoma de la cuenta (CPA que sube, leads que no cierran) usa `/diagnostico`;
para auditar la cuenta de un prospecto como agencia, `/auditoria-express`; si solo necesitas el veredicto de
políticas de una pieza antes de publicar, `/revisar-anuncio`.

Marcos: `meta-ads-kb/03-creatividad/15-landing-pages-y-cro-trafico-meta.md` (§1 navegador in-app, §2 velocidad y
checklist técnico, §3 message match y anatomía, §4 formularios, calendario y VSL, §5 checkout, §7 ¿anuncio o
conversión?, §8 CRO con poco tráfico, §9 checklists por negocio), `meta-ads-kb/03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md`
§3 (message match) y `meta-ads-kb/08-cuenta-politicas-seguridad/10-landing-pages-y-politicas.md` (§1–5).

## Pasos

1. **Contexto.** Con cliente: ficha (`tipo`, `meta.dataset`, `meta.evento_principal`, categoría sensible) y plan de
   funnel si existe. Con anuncio o ángulo: su copy y creatividad (`ads_get_creatives`, `ads_get_ad_preview`, o el
   brief en `clientes/<slug>/creativos/`). Sin cliente, la auditoría se hace igual y se ofrece guardarla.
2. **¿Es la landing?** Si hay datos de Meta (`analista-meta`, últimas 2–4 semanas completas): CTR, ratio de visitas a
   la página sobre clics salientes y conversión por anuncio. Encaja el patrón en la tabla de `15-…` §7. Si el problema
   está antes del clic (hook o CTR bajos con conversión normal), dilo y redirige a `/siguiente-anuncio`: tocar la
   landing no lo arregla.
3. **Chequeo técnico:** `python3 -I herramientas/landing_check.py <url>` (con `--sin-pagespeed` si PageSpeed falla o
   devuelve 429; entonces la velocidad se mide a mano en PageSpeed Insights). Lee:
   - el ID del píxel frente a `meta.dataset` de la ficha (si no coinciden, alarma);
   - si `fbclid` y `utm_*` sobreviven a las redirecciones;
   - gestor de consentimiento, eventos `fbq('track')` y plataforma;
   - LCP, CLS e INP en móvil (`15-…` §2.4: LCP ≤2,5 s).

   Si el HTML lleva `<meta name="generator" content="meta-ads-os/paginas">`, la página salió de `/construir-landing`:
   su píxel se carga tras el consentimiento y `landing_check.py` puede no verlo. Valida además la carpeta local con
   `python3 -I herramientas/paginas.py validar <carpeta>` (`clientes/<slug>/paginas/…`).
4. **Tracking.** La herramienta no ejecuta JavaScript: un píxel cargado por GTM o por una app no se ve en el HTML, así
   que no concluyas «no hay píxel» solo con ella. Si el ID no coincide, se pierden parámetros o no hay eventos
   visibles, `especialista-tracking` lo comprueba en el dataset (`ads_get_dataset_stats`, `ads_get_dataset_quality`) o
   con Test Events. Arreglar la señal → `/implementar-capi`.
5. **Navegador in-app y velocidad** (`15-…` §1.2–1.3 y §2.4): redirecciones, pop-ups al entrar, banner de
   consentimiento que tapa el CTA, scripts pesados, `autocomplete` y tipos de input en formularios. Pide al usuario
   que abra la URL desde un anuncio o un enlace en Instagram y Facebook con 4G y te cuente qué ve.
6. **Mensaje y conversión** (`especialista-funnel`):
   - primer viewport en móvil y message match con el anuncio o ángulo (`15-…` §3.1; `09-…` §3): la promesa del
     anuncio tiene que confirmarse en la primera pantalla;
   - cuerpo ordenado por objeciones, prueba específica cerca del CTA, oferta y riesgo invertido visibles (`15-…` §3.2);
   - formulario, aplicación, calendario embebido, VSL y página de gracias (`15-…` §4), o checkout y prueba gratuita
     en SaaS (`15-…` §5);
   - checklist de su tipo de negocio (`15-…` §9).
7. **Políticas** (`revisor-politicas`, `08-…/10-…` §1–5): funcionalidad, coherencia con el anuncio, nada que parezca
   cloaking, testimonios y resultados con disclaimers, datos que pide el formulario. Prioridad alta en
   infoproductos, high-ticket, salud y finanzas.
8. **Entrega**:
   - semáforo por bloque: tracking · velocidad e in-app · mensaje y message match · conversión (formulario, calendario
     o checkout) · políticas;
   - 5–10 cambios priorizados por impacto y esfuerzo con el orden de `15-…` §8.4 (oferta y riesgo, message match,
     velocidad, prueba, fricción, objeciones, CTA). Por cada uno: qué cambiar, por qué (con su etiqueta de evidencia),
     quién lo hace y **cómo medirlo**;
   - cómo medir según el tráfico (`15-…` §8.1–8.2): con menos de 10.000 visitas al mes, solo cambios grandes y
     comparación antes y después en semanas completas con controles, asumiendo que es evidencia débil; métricas
     intermedias (clic en CTA, inicio de formulario) para cambios pequeños. Sin cambios simultáneos en campañas
     mientras se mide (`15-…` §8.5).
9. **Guardar.** Con cliente: `clientes/<slug>/auditorias/AAAA-MM-DD_landing.md`. Marca `F1.landing` (verifica:
   archivo) cuando tracking y políticas no estén en rojo. Si los cambios los aplica otra persona (su diseñador, el
   cliente de la agencia), añade al final un brief de cambios listo para pasárselo.
