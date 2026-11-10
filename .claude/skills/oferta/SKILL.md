---
name: oferta
description: "Construye o mejora la oferta antes de gastar en anuncios: para quién, promesa y resultado, mecanismo, prueba, garantía o riesgo invertido, bonus, precio y forma de pago, urgencia legítima y oferta de entrada, con la ecuación de valor, objeciones reales e impacto en la economía; diagnostica si el cuello es la oferta y propone su test."
argument-hint: "<cliente> [mejorar]"
---

# /oferta

Cliente: `$ARGUMENTS`. `mejorar` = ya hay una oferta en marcha con datos. Marcos:
`meta-ads-kb/03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md` (§1 el sistema, §2 matriz de
diagnóstico, §4 diseño de oferta, §5 señales cualitativas), Fase 3 de
`meta-ads-kb/13-sistema-operativo/03-framework-lanzamiento.md` y el playbook de su modelo en `meta-ads-kb/14-playbooks/`
(consultoras y agencias de IA y automatización que venden a pymes: `playbook-consultoras-ia-automatizacion.md` §4,
ofertas de entrada y principal; agencias y consultoras en general: `playbook-agencias-consultores.md` §3; SaaS:
`playbook-saas.md` §3; high-ticket: `playbook-high-ticket.md`; local: `playbook-negocio-local.md`). Si la oferta de
entrada es un diagnóstico, una calculadora o una guía, constrúyela después con `/iman-de-leads`.

## Pasos

1. **Contexto.** Ficha (tipo, precio, mercado, economía), `investigacion/` (voz del cliente y competencia, si
   existen), registro creativo y lo que el usuario sepa de objeciones (comentarios, llamadas, chats). Sin economía →
   `/economia` primero: cambiar la oferta cambia la economía.
2. **¿Es la oferta?** (siempre con `mejorar`, o si ya hay datos). Usa la matriz de `03-creatividad/09-…` §2. Es la
   oferta si: atención y CTR normales o altos, la landing carga bien, pero la conversión es baja en **todos** los
   creativos y ángulos, y dominan las objeciones de precio o valor. Antes de tocarla tienen que haberse probado 3–5
   ángulos distintos con el message match verificado. Si los datos apuntan al creativo, a la landing o a ventas,
   dilo y redirige (`/siguiente-anuncio`, `/landing`, `/disenar-funnel`): no se toca la oferta.
3. **Entrevista breve** (≤6 preguntas): qué resultado concreto consigue su cliente y en cuánto tiempo; qué prueba tiene
   (casos con métricas del cliente, demos, datos, con permiso para usarlos); qué garantía puede sostener; qué entrega
   exactamente; capacidad; precio y forma de pago; contra qué compite (incluido «no hacer nada»).
4. **Construcción** (`estratega-creativo` redacta con todo el contexto). Campos:
   - para quién (nicho declarado) y para quién no (filtro);
   - promesa o resultado: específica, medible, sin afirmaciones prohibidas;
   - mecanismo: por qué funciona;
   - prueba;
   - entregables;
   - garantía o riesgo invertido;
   - bonus de alto valor percibido y bajo coste;
   - precio, forma de pago y financiación;
   - urgencia o escasez **legítimas** (plazas o fechas reales);
   - oferta de entrada (diagnóstico o auditoría con entregable, prueba sin tarjeta, demo de 15 minutos, tripwire);
   - CTA.
   Puntúa los cuatro términos de la ecuación de valor (resultado, probabilidad percibida, tiempo, esfuerzo), con la
   palanca concreta de cada uno. Es un criterio, no evidencia empírica.
5. **Variantes y economía.** 2–3 variantes con su efecto: vuelve a pasar `/economia` con las tasas que cambiarían
   (por ejemplo, más cierre y menos show con una auditoría de pago reembolsable) y enseña cómo se mueven el CPL y el
   coste por cita máximos. Las tasas supuestas van como `[HYPOTHESIS]`.
6. **Políticas.** `revisor-politicas` revisa promesa, garantía y prueba con
   `meta-ads-kb/08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md` y `11-copy-persuasivo-compliant-patrones.md`.
   Agencias y consultoras: nunca prometer ingresos («factura X al mes»); los casos, con métricas del cliente
   (`05-leadgen-high-ticket-crm/10-b2b-saas-local.md` §4).
7. **Test de la oferta.** Con la misma creatividad y dos landings u ofertas (`03-creatividad/09-…` §2.1). Una oferta
   necesita mucho volumen para medirse por CPA (≥100 conversiones por brazo para diferencias del 30–50 %,
   `13-sistema-operativo/05-framework-testing-creativo.md` §2): en cuentas pequeñas, test secuencial más señales
   cualitativas. Diseño y lectura → `/test-creativo`.
8. **Guardar.** `clientes/<slug>/investigacion/AAAA-MM-DD_oferta.md` (oferta elegida, variantes, economía, veredicto
   de políticas) y un resumen en la sección «Negocio» de la ficha. Marca `F0.oferta`. Siguiente: `/disenar-funnel`.
