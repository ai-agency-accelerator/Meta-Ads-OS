---
name: menu
description: "Muestra el mapa de Meta Ads OS: las 50 skills ordenadas en entradas, sistema, fases F0–F6 y agencia, con una línea de para qué sirve cada una a partir de su descripción real, los agentes, por dónde empezar según tu situación y las reglas de seguridad."
argument-hint: "[F0..F6|entradas|sistema|agencia|palabra clave]"
disable-model-invocation: true
---

# /menu

Filtro opcional: `$ARGUMENTS` (un grupo o una palabra clave). Solo lee archivos; no cuesta nada.

## Pasos

1. **Lee las descripciones reales.** Con la herramienta Grep, busca `^description:` y `^argument-hint:` en
   `.claude/skills/*/SKILL.md`. No inventes descripciones: resume cada una en una línea (≤110 caracteres) sin cambiar
   su sentido. El comando se escribe con su `argument-hint`.
2. **Agrupa en este orden** (contrato §2). Si una skill de la lista no existe, ponla con «(no instalada)». Si hay
   skills que no están en la lista, ve a un grupo final «Tuyas».

| Grupo | Skills |
|---|---|
| Entradas | `empezar`, `hoy`, `pregunta`, `siguiente-anuncio` |
| Sistema | `menu`, `doctor`, `actualizar`, `conectar`, `motor` |
| F0 · Negocio y oferta | `cliente-nuevo`, `economia`, `oferta`, `disenar-funnel`, `iman-de-leads` |
| F1 · Infraestructura y señal | `configurar-meta`, `implementar-capi`, `audiencias`, `landing`, `construir-landing`, `formulario-instantaneo` |
| F2 · Investigación | `competencia`, `voz-cliente` |
| F3 · Creatividad | `brief-creativo`, `producir-video`, `producir-estatico`, `variantes`, `revisar-anuncio`, `analisis-creativo`, `casos-y-creadores`, `organico-a-anuncios` |
| F4 · Lanzamiento | `lanzar-campana`, `publicar-anuncios`, `test-creativo`, `webinar` |
| F5 · Operación | `brief-diario`, `informe-semanal`, `revision-mensual`, `diagnostico`, `ejecutar-cambio`, `embudo`, `rescate-cuenta`, `reglas-automaticas`, `seguimiento-leads`, `anuncios-por-etapa` |
| F6 · Escalado | `escalar`, `auditoria` |
| Agencia | `informe-cliente`, `auditoria-express`, `entrenar`, `novedades-meta` |

3. **Filtro.** Con un grupo (`F3`, `agencia`…), enseña solo ese grupo. Con una palabra, las skills cuya descripción la
   contenga. Sin filtro, todo.
4. **Formato.** Una tabla por grupo: `Comando | Para qué`. Marca con «(pide confirmación)» las que escriben en Meta o
   gastan: `lanzar-campana`, `ejecutar-cambio`, `publicar-anuncios`, `producir-video`, `reglas-automaticas`,
   `formulario-instantaneo`, `anuncios-por-etapa` y `audiencias`. Todas ellas salvo `audiencias`, más `actualizar` y
   `menu`, solo se lanzan escribiéndolas tú (contrato §11).
5. **Por dónde empezar** (siempre, tras las tablas):
   - Primera vez o instalación a medias → `/empezar`.
   - Cada mañana o si no sabes qué toca → `/hoy`.
   - Una duda de cómo funciona Meta → `/pregunta "<duda>"`.
   - Qué anuncio hacer ahora → `/siguiente-anuncio <cliente>`.
   - Hace falta la página o el gancho de entrada → `/iman-de-leads <cliente>` y `/construir-landing <cliente>`.
   - Proteger la cuenta de noche → `/reglas-automaticas <cliente>`.
   - Algo falla en el sistema → `/doctor`.
6. **Agentes.** Lista en una línea los nombres de `.claude/agents/*.md` (Glob). Se usan solos desde las skills o
   pidiéndolos por su nombre. Solo `operador-meta` escribe en Meta, y siempre con un plan aprobado.
7. **Seguridad** (tres líneas): leer es libre; cualquier escritura en Meta, GHL o Stripe pide tu confirmación, lo nuevo
   se crea en pausa y activar pide un sí específico; borrar está bloqueado; el motor de vídeo pide confirmación de coste;
   las páginas se generan en local y nunca se despliegan solas; todo queda en `logs/` y en el change log del cliente.
