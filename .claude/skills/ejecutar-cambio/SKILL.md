---
name: ejecutar-cambio
description: "Ejecuta un cambio concreto en una cuenta que ya funciona (presupuesto, puja, pausar o activar, audiencias, exclusiones, experimentos, configuración del CRM) con disciplina: plan formal, regla de paciencia y topes, aprobación explícita, ejecución por operador-meta, verificación y change log. Para campañas nuevas, /lanzar-campana."
argument-hint: "<cliente> \"<cambio>\" | <cliente> <ruta del plan o ficha de test>"
disable-model-invocation: true
---

# /ejecutar-cambio

Entrada: `$ARGUMENTS`. Puede venir de una decisión de `/informe-semanal`, `/diagnostico`, `/escalar`, `/test-creativo` o
`/revision-mensual`, o de una petición directa. Para subir anuncios a una campaña existente, `/publicar-anuncios`.

- **Marco:** `meta-ads-kb/09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md` (regla de paciencia),
  `meta-ads-kb/09-bidding-escalado-economia-analitica/04-cambios-de-presupuesto-y-duplicacion.md` (magnitud y
  learning), `meta-ads-kb/13-sistema-operativo/04-operativa-diaria-semanal-mensual.md` §5 (ventana de edición, una
  palanca por vez, no cambiar tarde), change log en `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §2,
  herramientas del MCP en `meta-ads-kb/10-cambios-2025-2026-api-ia-automatizacion/11-mcp-meta-inventario-y-conexion.md`.
- **Agentes:** `analista-meta` (IDs y estado actual), `revisor-estrategia`, `revisor-politicas` (si cambia texto o
  landing), `especialista-crm` (cambios en GHL), `operador-meta` (el único que escribe en Meta).
- **Herramientas:** `meta_ads.py pausar|activar --confirmo|presupuesto --confirmo` (con token) o el MCP
  (`ads_update_entity`, `ads_activate_entity`, `ads_create_custom_audience`, `ads_update_custom_audience`,
  `ads_experiment_abtest_create_test`, `ads_experiment_lift_create_test`).
- **Lee:** ficha (topes, ventana, mejoras automáticas), `change-log.md`, `logs/cambios.jsonl`.
- **Escribe:** `change-log.md` y, si hay plan formal, `clientes/<slug>/planes/<AAAA-MM-DD>_<cambio>.md`.

## Pasos

1. **Formaliza el cambio** en una tabla: cuenta, nivel y objeto con su ID (léelo con `ads_get_ad_entities`, nunca lo
   supongas), valor actual → valor nuevo, motivo o hipótesis, métrica de éxito, fecha de evaluación y condición de
   reversión. Un cambio por unidad de presupuesto, salvo cambios agrupados a propósito.
2. **¿Conviene ahora?**
   - **Paciencia:** último cambio de ese objeto en `change-log.md` y `logs/cambios.jsonl`. Si hace <7 días, sin 30–50
     eventos o con la ventana sin madurar y no es una rotura (tracking caído, gasto descontrolado, rechazo, landing
     caída), recomienda esperar y di hasta cuándo. `meta_guard` también lo avisará.
   - **Topes:** con `topes.cambio_dia` o `topes.total_dia` a 0, no se sube ni se crea presupuesto: que el usuario los
     fije en la ficha. Un presupuesto nuevo por encima de `cambio_dia` lo bloquea `meta_guard`; no se rodea.
   - **Riesgos:** magnitud del cambio de presupuesto (puede reiniciar el aprendizaje; Ads Manager a veces indica hasta
     dónde subir sin hacerlo), edición significativa en un conjunto en test, solapamiento si alguien propone duplicar,
     categoría especial, reglas del Ads MCP server que puedan bloquearlo, hora del día (mejor por la mañana).
   - Si cambia texto, anuncio o landing → `revisor-politicas` antes.
   - **¿Lo pausó una regla?** Antes de reactivar algo, mira
     `python3 -I herramientas/reglas_meta.py historial --cliente <slug>`. Si lo pausó la regla de gasto fuera de tope,
     la causa es un presupuesto por encima de los topes: corrígelo antes de reactivar. Si lo pausó una regla de
     conversión, revisa si acertó (`/reglas-automaticas <cliente> revisar`). Crear, pausar o reactivar reglas es de
     `/reglas-automaticas`, no de esta skill.
3. **Revisión:** `revisor-estrategia` revisa el cambio contra los principios, la regla de paciencia y los mitos (regla
   del 20 %, duplicar para escalar, frecuencia > 3). Aplica o justifica cada observación.
4. **Aprobación:** presenta la tabla final, qué se ejecutará y cómo se deshace. **Espera un «sí» explícito.** Activar
   algo pausado necesita además su propia confirmación en el momento («activa <objeto>»).
5. **Ejecución** por `operador-meta` (cada escritura pide confirmación; es normal):
   - presupuesto: `python3 -I herramientas/meta_ads.py presupuesto <id> <importe> --confirmo --cliente <slug>` o
     `ads_update_entity`;
   - pausar: `meta_ads.py pausar <ids> --cliente <slug>` o `ads_update_entity` con estado en pausa;
   - activar: `meta_ads.py activar <ids> --confirmo --cliente <slug>` o `ads_activate_entity`;
   - puja, ventana, exclusiones, ubicaciones: `ads_update_entity`;
   - audiencias (exclusión de clientes, listas de CRM ya con hash): `ads_create_custom_audience` / `ads_update_custom_audience`
     (los datos personales nunca pasan por el chat);
   - experimentos: `ads_experiment_check_eligibility` y después `ads_experiment_abtest_create_test` o
     `ads_experiment_lift_create_test` con la ficha del test;
   - listas por etapa del CRM: `audiencias_meta.py crear|sincronizar --confirmo` (detalle en `/anuncios-por-etapa`);
     formularios instantáneos nuevos: `/formulario-instantaneo` (los publicados no se editan, se clonan);
   - **GHL** (`especialista-crm`): solo configuración (campos, etapas, etiquetas). Mensajes a contactos, borrados y
     facturas están bloqueados por `ghl_guard`. Stripe se usa solo en lectura.
   Borrar está bloqueado: lo que sobra se pausa.
6. **Verificación:** relee el objeto (`ads_get_ad_entities`, `ads_get_errors`) y comprueba que el valor guardado es el
   aprobado. Si Meta lo rechazó o lo bloqueó una regla, explica por qué y propone el ajuste; no lo fuerces.
7. **Change log** (`operador-meta`): fila con `Fecha/hora` · `Quién` = `operador-meta (aprobado por <operador>)` ·
   `Nivel` · `Objeto (ID)` · `Cambio (de → a)` · `Motivo / hipótesis` · `Métrica de éxito` · `Fecha de evaluación` ·
   `Resultado` vacío. `registro_obligatorio` avisa si falta.
8. **Cierre:** recuerda la fecha de evaluación y qué mirar ese día (la verán `/brief-diario` y `/informe-semanal`).

## Reglas

- Sin plan aprobado en esta conversación no se escribe nada.
- Nunca circunvención: si una restricción o una política lo impide, el cambio no se hace por otro camino.
