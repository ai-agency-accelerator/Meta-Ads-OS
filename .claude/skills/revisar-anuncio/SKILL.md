---
name: revisar-anuncio
description: "Revisa copy, creatividad, formulario o landing contra las políticas de Meta y el riesgo de cuenta antes de publicar, con reescrituras persuasivas que cumplen y veredicto OK / OK con cambios / NO publicar, que queda en el LEEME de la pieza. Para anuncios ya rechazados o cuentas restringidas, usa /rescate-cuenta."
argument-hint: "<texto, archivo, URL, ID de anuncio o carpeta del creativo> [cliente]"
---

# /revisar-anuncio

Entrada: `$ARGUMENTS`.

- **Marco:** `meta-ads-kb/08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md` (mapa de políticas),
  `meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md` (patrones y checklist §8),
  `meta-ads-kb/08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md` (resultados e ingresos),
  `meta-ads-kb/08-cuenta-politicas-seguridad/07-categorias-especiales-y-sensibles.md`,
  `meta-ads-kb/08-cuenta-politicas-seguridad/10-landing-pages-y-politicas.md` y, para piezas con IA,
  `meta-ads-kb/03-creatividad/14-herramientas-ia-creativa-meta.md`.
- **Agentes:** `revisor-politicas` (siempre); `critico-creativo` en paralelo si también se pide calidad creativa.
- **Lee:** el contenido, la ficha (sector, mercado, categoría especial, afirmaciones aprobadas y prohibidas, reglas
  propias) y el `LEEME.md` si es una pieza del sistema.
- **Escribe:** el veredicto en `creativos/<nombre-base>/LEEME.md` o, si es contenido suelto,
  `clientes/<slug>/creativos/_revisiones/<AAAA-MM-DD>_<tema>.md`.

## Pasos

1. **Obtén todo lo que verá el usuario y el revisor de Meta:**
   - texto principal, titular, descripción, CTA y texto en imagen o en pantalla;
   - vídeo: guion del LEEME, fotogramas clave y lo que se dice (audio);
   - ID de anuncio: `ads_get_creatives` y `ads_get_ad_preview` (Feed y Reels);
   - landing (lectura de la página y `python3 -I herramientas/landing_check.py <url>` para lo visible) y el formulario
     instantáneo si lo hay.
2. **Contexto de riesgo:** sector y mercado (en la UE, temas sociales), categoría especial, historial de rechazos de la
   cuenta y si la pieza contiene personas, voces o escenas generadas con IA.
3. **Revisión** (`revisor-politicas`): tabla `elemento | riesgo | política (ruta de la KB) | severidad | reescritura`.
   Riesgos habituales en este público:
   - resultados o ahorros sin prueba («ahorra 20 h a la semana», «duplica tus citas»): requieren prueba y contexto, o
     reformularse como mecanismo;
   - promesas de ingresos o de «negocio con IA» (08/08);
   - atributos personales («¿tu clínica está perdiendo pacientes?» frente a «¿estás arruinado?», 08/11 §3.5);
   - testimonios sin permiso o no representativos; urgencia o escasez falsas;
   - incoherencia entre anuncio y landing; formularios que piden datos sensibles;
   - personas sintéticas sin etiqueta o que fingen ser clientes.
4. **Veredicto** (contrato §6): `OK`, `OK con cambios aplicados` (reescrito y ya cambiado en los archivos),
   `OK con cambios` (hay cambios por aplicar) o `NO publicar`, con la versión reescrita, persuasiva y que cumple (sin
   ofuscar palabras ni esconder la promesa en la imagen).
5. **Registro:** si es una pieza del sistema, escribe en su `LEEME.md` la línea exacta
   `- **Veredicto de políticas:** <OK | OK con cambios aplicados | OK con cambios | NO publicar> · <AAAA-MM-DD> · revisor-politicas` y resume los
   cambios en «Calidad → Políticas». El hook `control_publicacion` lee esa línea antes de dejar crear el anuncio. Si
   los cambios afectan a la pieza, vuelve a `/producir-video`, `/producir-estatico` o `/variantes`.
6. Si el anuncio ya fue rechazado o la cuenta tiene restricciones → `/rescate-cuenta`.

## Reglas

- Nunca circunvención: nada de cambiar letras, mover la promesa a la imagen o al audio, ni landings distintas para el
  revisor (08/09 §4).
- Solo `OK` y `OK con cambios aplicados` dejan publicar sin preguntar. Cuando apliques los cambios en los archivos
  que se van a publicar, cambia la línea de `OK con cambios` a `OK con cambios aplicados`.
