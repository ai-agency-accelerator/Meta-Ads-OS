---
name: entrenar
description: "Práctica guiada para el operador o su equipo: escenarios realistas de agencia y SaaS (economía, diagnóstico, testing, escalado, tracking, políticas, mitos) adaptados a tu nivel, que respondes tú y corrige mentor-meta con rúbrica, nota y fuente en la base. Guarda tu progreso y propone el siguiente."
argument-hint: "[tema | caso A–J | árbol 1–15 | mitos | progreso]"
---

# /entrenar

Entrada: `$ARGUMENTS`. Sin tema, el siguiente que toca según tu progreso. Con `progreso`, solo enseña el historial.

- **Marco:** `meta-ads-kb/15-escenarios-validacion/README.md` (casos A–J en `01-casos-A-E.md` y `02-casos-F-J.md`),
  árboles de `meta-ads-kb/13-sistema-operativo/07-framework-diagnostico.md`, principios en
  `meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md`, mitos en
  `meta-ads-kb/12-mitos-contradicciones/01-mitos-meta-ads-2026.md`, economía en
  `meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md` y estadística en
  `meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md`.
- **Agente:** `mentor-meta` (prepara el escenario con su rúbrica y corrige).
- **Herramientas** (las puede usar quien entrena, como en el trabajo real): `economia.py`, `estadistica.py`.
- **Lee:** `contexto/preferencias.md` (`nivel`, `estilo`), `contexto/operador.md` (perfil y tipo de clientes),
  `contexto/entrenamiento.md` (progreso).
- **Escribe:** `contexto/entrenamiento.md`.

## Pasos

1. **Nivel y perfil:** `nivel` de la cabecera de `contexto/preferencias.md` (principiante, intermedio o avanzado; si
   falta, intermedio) y el perfil de `contexto/operador.md` (agencia, consultora, SaaS). Si `contexto/entrenamiento.md`
   no existe, créalo con la tabla del paso 7.
2. **Elige el escenario:** el tema pedido o, si no hay, el bloque con peor nota o sin practicar, en este orden de
   prioridad: economía y break-even → evento de optimización → lectura con ruido (n pequeño, kill a 2–3× CPA) →
   diagnóstico (árboles 1, 4, 5, 9, 12) → testing → escalado y coste marginal → tracking (árboles 10, 11, 13) →
   políticas → mitos. Principiante: un concepto por escenario; avanzado: casos con varias dependencias y
   contradicciones abiertas.
3. **Preparación** (`mentor-meta`): un escenario basado en un caso o árbol de la KB, **con los números cambiados** y
   llevado al público del operador (Acme Automations vendiendo implantaciones de IA, Nimbo como SaaS, Clínica Sonrisa
   como cliente local de una agencia). Devuelve por separado `ENUNCIADO` (datos y una pregunta concreta) y `RÚBRICA`
   (respuesta esperada, 3–5 criterios con su peso sobre 10, errores típicos y rutas de la KB).
4. **Enseña solo el `ENUNCIADO`.** La rúbrica no se enseña ni se insinúa hasta corregir. Pide la respuesta como la
   daría en una cuenta real: decisión, porqué y qué dato le falta. Si pide una pista, una sola y sin la respuesta.
5. **Corrección** (`mentor-meta`, con enunciado, rúbrica y respuesta): nota por criterio y total sobre 10, qué faltó o
   sobró con su fuente (ruta de la KB y etiqueta de evidencia), la respuesta modelo y el error de razonamiento de
   fondo si lo hay (decidir con ruido, optimizar una métrica que no es el negocio, creerse un mito).
6. **Siguiente:** propone el siguiente escenario (refuerzo si la nota es < 6, avance si es ≥ 8 [HYPOTHESIS]). Con tres
   notas seguidas ≥ 8 en el nivel actual, propone subir `nivel` en `contexto/preferencias.md`; solo se cambia con tu sí.
7. **Progreso** en `contexto/entrenamiento.md`:

   ```markdown
   | Fecha | Bloque | Escenario (fuente) | Nivel | Nota /10 | Fallo principal | Siguiente |
   |---|---|---|---|---|---|---|
   ```

   Debajo, una línea por bloque con la media y la tendencia.

## Reglas

- Los escenarios son ficticios: ni datos ni nombres de clientes reales, aunque los haya en `clientes/`.
- Se corrige con la base de conocimiento, no con la opinión del momento; si la KB no cubre algo, se dice.
