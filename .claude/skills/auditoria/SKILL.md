---
name: auditoria
description: "Auditoría completa de una cuenta de Meta con acceso (propia, de cliente o heredada) y severidades P0–P3: especialistas en paralelo (cuenta, señal, políticas, funnel y, si hay CRM o Stripe, negocio), consolidados en un informe con scorecard y plan 30/60/90. Solo lectura. Modo profundo con verificación cruzada."
argument-hint: "<cliente> [periodo en días] | profundo <cliente>"
---

# /auditoria

Entrada: `$ARGUMENTS`. Modos: **normal** y **`profundo`** (workflow `auditoria-profunda`). Para un prospecto sin acceso
a su cuenta, `/auditoria-express`. Solo lectura: nadie escribe en Meta, GHL ni Stripe.

- **Marco:** `meta-ads-kb/13-sistema-operativo/02-framework-auditoria.md` (orden de §1–10, severidades del TL;DR y
  entregable §11), `meta-ads-kb/13-sistema-operativo/08-cuenta-nueva-y-heredada.md` (§B si es heredada: primero accesos
  y riesgo, nada se toca la primera semana), checklist de señal en
  `meta-ads-kb/04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md`, seguridad en
  `meta-ads-kb/08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md` §8, el playbook del
  `tipo` de la ficha en `meta-ads-kb/14-playbooks/` y cambios de plataforma en `meta-ads-kb/00-ESTADO-ACTUAL-2026.md`.
- **Agentes** (en paralelo, un mensaje con varias llamadas): `auditor-cuenta`, `especialista-tracking`,
  `revisor-politicas`, `especialista-funnel` y `especialista-crm` si la ficha tiene CRM o Stripe; después
  `revisor-estrategia` (plan).
- **Herramientas:** `meta_ads.py vigente|campanas|creatividades|anuncios` (con token), `landing_check.py`,
  `registro_creativo.py sin-nomenclatura`, `economia.py`, `estadistica.py`.
- **Lee:** ficha (si no existe → `/cliente-nuevo` primero), `change-log.md`, `estado.md`, informes previos.
- **Escribe:** `clientes/<slug>/auditorias/<AAAA-MM-DD>/<area>.md` (una parte por especialista) y
  `clientes/<slug>/auditorias/<AAAA-MM-DD>-auditoria.md` (consolidado).

## Pasos

1. **Preparación:** ficha con `meta.cuenta`, URLs de las landings, periodo (90 días en semanas completas, más el mismo
   trimestre del año anterior si hay estacionalidad) y ventana de atribución. Comprueba que el MCP ve la cuenta
   (`ads_get_ad_accounts`). Marca las discontinuidades de Meta en el periodo (02 TL;DR y `00-ESTADO-ACTUAL-2026.md`).
2. **Especialistas en paralelo.** A cada uno: cliente, cuenta, URLs, periodo, ventana y dónde guardar su parte
   (`auditorias/<AAAA-MM-DD>/<area>.md`), con hallazgos en el formato de 02 §11 (evidencia, severidad, impacto, acción,
   esfuerzo, responsable):
   - `auditor-cuenta` → `cuenta.md`: economía, seguridad y accesos visibles, estructura, presupuesto y pujas,
     audiencias, creatividad (reparto del gasto, fatiga, diversidad, nomenclatura con
     `registro_creativo.py sin-nomenclatura`), mejoras automáticas activas (`meta_ads.py creatividades`), deuda técnica
     2025-2026;
   - `especialista-tracking` → `senal.md`: datasets, evento principal por navegador y servidor, deduplicación, calidad de
     coincidencia, conversiones personalizadas, etapas del CRM devueltas, reconciliación con el backend;
   - `revisor-politicas` → `politicas.md`: anuncios con más gasto (`ads_get_creatives`, `ads_get_ad_preview`), rechazos
     (`ads_get_errors`), landing y categoría especial;
   - `especialista-funnel` → `funnel.md`: landings (`python3 -I herramientas/landing_check.py <url>`), formularios,
     speed to lead y proceso comercial;
   - `especialista-crm` (si hay CRM o Stripe) → `negocio.md`: leads, citas, ventas y cash por anuncio y por cohorte
     (`ghl.py por-anuncio`, `stripe_datos.py por-anuncio`, `/embudo`), para que la auditoría decida con la capa de negocio.
3. **Verificación:** comprueba tú cada P0 y P1 con una consulta propia antes de darlo por bueno (un dato que lo
   confirme o lo tumbe). Lo que no se pueda verificar baja a «límites».
4. **Consolidación** en `clientes/<slug>/auditorias/<AAAA-MM-DD>-auditoria.md` con la plantilla de 02 §11: resumen
   ejecutivo de 5 líneas, scorecard por área (bien / vigilar / mal), hallazgos P0→P3 sin duplicados, plan (semana 1 los
   P0, 30 días los P1, 60–90 días los P2, P3 y tests) y supuestos y límites (qué requiere acceso que no hay: roles del
   portfolio, pagos, reglas del Ads MCP server, backend). Si dos agentes discrepan, explica por qué y qué dato lo
   resolvería. Cada afirmación con su dato; hechos separados de hipótesis.
5. **Revisión:** `revisor-estrategia` revisa el plan (nada de reestructuraciones masivas sin plan de medición, mitos,
   paciencia).
6. **Cierre:** las 3 acciones de mayor impacto y por dónde se ejecutan (`/ejecutar-cambio`, `/implementar-capi`,
   `/landing`, `/brief-creativo`, `/rescate-cuenta`). Nada se ejecuta desde aquí. Si `relacion: cliente`, ofrece
   `/informe-cliente` con la versión para el cliente.

## Modo `profundo`

1. **Avisa del coste:** el workflow `auditoria-profunda` lanza unos 7–13 agentes (preparación, 4–5 especialistas, un
   verificador que intenta tumbar los P0 y P1 de cada área y la consolidación). Coste alto: unas 2–3 veces la auditoría
   normal [HYPOTHESIS]. Solo lectura.
2. Solo con un «sí» explícito, lánzalo con la herramienta Workflow y args
   `{"cliente": "<slug>", "periodo_dias": 90, "urls": ["<landing>", …], "crm": "auto"}`.
3. Revisa el consolidado (`auditorias/<AAAA-MM-DD>-auditoria.md`) y sigue en los pasos 5 y 6.

## Reglas

- Lo de arriba invalida lo de abajo: con la señal rota, no se audita la creatividad como si los datos fueran buenos.
- P0 = pérdida de dinero o riesgo de cuenta ahora. No infles severidades para que el informe impresione.
