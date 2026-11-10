---
name: rescate-cuenta
description: "Protocolo de emergencia ante anuncios rechazados en cadena, una cuenta, Página, portfolio o dominio restringidos, un hackeo o un fallo de pago: congela lanzamientos, identifica la capa y el motivo, decide revisar, editar o rehacer, redacta la petición de revisión para un admin y deja la prevención. Nunca circunvención."
argument-hint: "<cliente> [qué ha pasado o ID del anuncio o activo]"
---

# /rescate-cuenta

Entrada: `$ARGUMENTS`. Las peticiones de revisión las envía **un admin** desde Business Support Home: este comando
prepara todo, no envía nada.

- **Marco:** `meta-ads-kb/08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md` (§1 capas, §2 causas,
  §4 flujo de revisión, §5 qué funciona en apelaciones, §6 circunvención),
  `meta-ads-kb/08-cuenta-politicas-seguridad/09-rechazos-apelaciones-que-no-hacer.md` (§1 árbol ante un rechazo, §2
  editar, rehacer o pedir revisión, §4 lo que no se hace, §5 protocolo de agencia),
  `meta-ads-kb/08-cuenta-politicas-seguridad/05-soporte-meta-canales-elegibilidad.md` (§3 escalera de soporte, §4
  plantilla del mensaje), `meta-ads-kb/08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md`
  (§6 hackeo), `meta-ads-kb/08-cuenta-politicas-seguridad/04-pagos-facturacion-limites.md` (§4 fallos de pago), árbol 14
  de `meta-ads-kb/13-sistema-operativo/07-framework-diagnostico.md`.
- **Agentes:** `revisor-politicas` (causa y versión que cumple), `analista-meta` (lectura del estado), `especialista-funnel`
  (si es la landing o el dominio), `gestor-cliente` (comunicación con el cliente), `operador-meta` (solo para pausar,
  con aprobación).
- **Lee:** ficha, `change-log.md`, anuncios y landings afectados, `creativos/` (LEEME y veredictos previos).
- **Escribe:** `clientes/<slug>/auditorias/<AAAA-MM-DD>-rescate.md`, `change-log.md` y las reglas propias de la ficha
  (frases prohibidas y alternativas aprobadas, con tu sí).

## Pasos

1. **Congela.** Ningún lanzamiento nuevo, ninguna subida de presupuesto y ningún anuncio duplicado en esa cuenta hasta
   cerrar el rescate. **No borres anuncios rechazados**: se pierde la posibilidad de pedir revisión y no limpia el
   historial. Si hay sospecha de hackeo, el paso 3 va antes que todo lo demás.
2. **Identifica la capa y el motivo literal** (`analista-meta`): `ads_get_errors` y `ads_get_ad_entities` (estados y
   motivos de rechazo), `ads_get_creatives` y `ads_get_ad_preview` de los anuncios afectados, historial de la cuenta
   (`ads_account_get_activity_logs`). Pide al usuario lo que el MCP no ve: captura de Business Support Home →
   Account status overview (qué activo: anuncio, cuenta, portfolio, Página, perfil, dominio, dataset, catálogo; motivo
   y opciones de «What you can do»). Clasifica según 08/01 §1 y anota si es una restricción «suave» (límite de gasto
   bajado, sin poder añadir admins).
3. **Seguridad** (si hay accesos raros, cambios que nadie reconoce o gasto inesperado): guía al usuario con 08/03 §6:
   asegurar perfiles (contraseña, sesiones, 2FA), quitar intrusos, revisar métodos de pago y partners. Nunca pidas ni
   aceptes contraseñas o códigos, ni recomiendes «recuperadores» de pago.
4. **Decide la ruta:**
   - **anuncio rechazado** (árbol 08/09 §1 y tabla §2): falso positivo claro → una petición de revisión; infracción leve
     → editar; concepto problemático → anuncio nuevo con otro enfoque (`/revisar-anuncio` y `/brief-creativo`); landing o
     dominio → arreglar la landing (`/landing`), nunca cambiar de dominio para seguir igual; categoría especial →
     rehacer la campaña con la categoría correcta;
   - **cuenta, portfolio, Página o perfil:** corregir primero la causa (retirar o corregir anuncios, landing, 2FA,
     verificaciones que pida «What you can do», con datos que cuadren exactamente) y después una sola petición de
     revisión bien preparada. Recuerda: revisiones limitadas, decisión final y 6 meses de plazo en cuentas
     deshabilitadas;
   - **pago:** método de pago de respaldo, saldo y límite de gasto (08/04 §4);
   - **dataset restringido por categoría:** revisión de la categorización en Events Manager y `especialista-tracking`.
   - **más de 3 rechazos en 30 días:** auditoría de copy y landing de toda la cuenta con `revisor-politicas` (08/09 §5).
5. **Pausas** (solo si hace falta, por ejemplo anuncios con la misma infracción aún activos): plan, «sí» explícito y
   `operador-meta` con `ads_update_entity`. Se registra en el change log.
6. **Borrador de la petición de revisión** con la plantilla de 08/05 §4: activos con IDs, motivo literal, explicación
   breve y factual, medidas adoptadas (anuncios corregidos con IDs, cambios de landing, 2FA, verificación, revisión
   interna) y adjuntos. Sin discutir la política. Si la revisión automática falla, la escalera de soporte de 08/05 §3
   (asistente de Meta AI, Meta Verified o partner).
7. **Comunicación** (si `relacion: cliente`): `gestor-cliente` redacta el mensaje al cliente (qué pasó, qué se ha hecho,
   qué se espera y plazos realistas, sin prometer resultados). No se envía sin tu revisión.
8. **Informe y prevención** en `clientes/<slug>/auditorias/<AAAA-MM-DD>-rescate.md`: cronología, capa, motivo, ruta
   elegida, borrador de la petición, estado y próxima comprobación, y registro de rechazos (fecha, ID, motivo literal,
   decisión, resultado, aprendizaje). Propón añadir a «Reglas propias del cliente» de la ficha las frases prohibidas y
   sus alternativas aprobadas. Fila en el change log con `Quién` = `Meta (plataforma)` para la restricción.

## Reglas

- **Nunca circunvención** (08/01 §6 y 08/09 §4): ni cuentas, Páginas, portfolios o dominios nuevos para seguir
  anunciando lo mismo, ni cuentas alquiladas, ni cloaking, ni ofuscar palabras, ni landings distintas para el revisor.
  Si el usuario lo pide, explica el riesgo (puede arrastrar a todos los activos del dueño) y no lo ayudes a hacerlo.
- Una petición de revisión por activo y bien preparada vale más que varias impulsivas.
