---
name: pregunta
description: "Responde una duda sobre Meta Ads desde la base de conocimiento con mentor-meta: mira primero lo vigente en 2026, cita archivo y etiqueta de evidencia, se adapta a tu nivel y dice claramente cuando la KB no lo cubre. Para conceptos y cómo funciona algo, no para analizar los datos de una cuenta."
argument-hint: "\"<tu duda>\""
---

# /pregunta

Duda: `$ARGUMENTS`. Si está vacío, pregunta cuál es.

## Pasos

1. **¿Es una duda de conocimiento?** Redirige si no lo es:
   - sobre los datos de una cuenta («¿por qué ha subido mi CPA esta semana?») → `/diagnostico <cliente> "<síntoma>"`;
   - sobre qué ha cambiado en Meta últimamente → `/novedades-meta`;
   - quiere practicar o examinarse → `/entrenar`.
   Si mezcla ambas cosas, responde la parte de conocimiento y ofrece la skill para la parte de datos.
2. **Contexto.** Lee `nivel` en la cabecera de `contexto/preferencias.md` (`principiante | intermedio | avanzado`;
   por defecto `intermedio`). Si la duda menciona un cliente, lee de su ficha solo `tipo`, `meta.evento_principal`,
   mercado y moneda: la respuesta cambia según el modelo de negocio.
3. **Delega en `mentor-meta`** con la pregunta literal, el nivel, el contexto del cliente y estas instrucciones:
   1. Lee primero la sección relevante de `meta-ads-kb/00-ESTADO-ACTUAL-2026.md`. Si contradice un archivo de área
      más antiguo, manda el estado actual.
   2. Localiza los archivos con `meta-ads-kb/00-INDICE-MAESTRO.md` y lee los 1–3 que importan (método en
      `meta-ads-kb/13-sistema-operativo/`, casos por modelo de negocio en `meta-ads-kb/14-playbooks/`).
   3. Si huele a folklore (regla del 20 %, frecuencia > 3 = fatiga, píxel nuevo, retargeting obligatorio,
      «50 creativos», calentar el píxel), contrasta con `meta-ads-kb/12-mitos-contradicciones/01-mitos-meta-ads-2026.md`.
   4. Estructura: respuesta directa en 1–3 frases → por qué (el mecanismo) → qué hacer, si aplica → fuentes. Cada
      afirmación importante lleva su etiqueta (`[OFFICIAL META]`, `[EMPIRICAL]`, `[STRONG INFERENCE]`, `[HYPOTHESIS]`,
      `[CONTESTED]`) y su archivo (`meta-ads-kb/<ruta>.md` §sección). En lo `[CONTESTED]`, las dos posturas y cuándo
      aplica cada una.
   5. Nivel: con principiantes, define términos, usa un ejemplo con números redondos y deja un solo paso siguiente;
      con avanzados, ve directo al matiz, las cifras y las excepciones.
   6. **Si la KB no lo cubre, o el tema cambia rápido y la fecha de «Última verificación» del archivo es antigua, dilo
      sin rodeos.** Ofrece consultar el Help Center con `ads_get_help_article` (MCP de Meta, solo lectura) o
      `/novedades-meta`. Nunca inventes cifras; un umbral que no esté en la KB va como `[HYPOTHESIS]`.
4. **Transmite la respuesta** sin quitar fuentes ni etiquetas. Unas 250 palabras como máximo, salvo que pida más.
5. **Si la duda nace de algo que ha visto en su cuenta y contradice la KB**, propón anotarlo en `aprendizajes/`
   (AAAA-MM-DD, qué se observó, en qué tipo de cuenta, sin IDs ni datos personales) para que lo revise
   `curador-conocimiento`.
