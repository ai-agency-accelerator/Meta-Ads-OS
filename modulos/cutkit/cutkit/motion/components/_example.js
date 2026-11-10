/* cutkit · components/_example.js — PLANTILLA para componentes de gráficos (title.*, stat.*, list.*, logo.* …)
 * Los ficheros que empiezan por «_» NO se cargan. Copia esto a components/<familia>.js (+ .css opcional).
 * ═══════════════════════════════════════════════════════════════════════════════════════════════════════
 * CONTRATO (runtime.js)
 *   CK.register(name, { kind: 'graphic', mount(root, props, ctx) { …DOM…; return { animate(tl, t0, t1, cues) { … } } } })
 *   · mount: construye el DOM dentro de `root` (div.clip del item, con data-start/duration; HF lo oculta fuera de
 *     [t0, t1)). Se llama DESPUÉS de cargar fuentes e imágenes → puedes medir (CK.util.fitText) y usar naturalWidth.
 *   · animate: añade tweens a `tl` en TIEMPO ABSOLUTO de programa. t0/t1 ya encajados al fotograma.
 *     `cues` = tiempos internos (s de programa) que manda el compilador, p. ej. {item1: 3.9, item2: 4.6} anclados a
 *     las palabras: cada elemento de una lista entra en SU palabra (no stagger fijo).
 *
 *   ctx = { W:1080, H:1920, fps:30, spec, item, tokens, util,
 *           slot:{x,y,w,h}   zona útil del layout activo en t0 (split → 1080×1008 arriba; card_float → la tarjeta;
 *                            full_face → zona segura). Para gráficos de pantalla completa usa ctx.safeRect.
 *           safe:{top:288,bottom:672,left:65,right:192}  · safeRect:{x:65,y:288,w:950,h:960} (simétrico, centrado en 540;
 *                            por debajo de y=1000 la derecha es 192 → ctx.safeAt(y0,y1) / ctx.safeCenteredW(y) = 696)
 *           layout.geom.light  true si el panel es claro (paper/white/accent/hex claro): texto en tinta (--ck-card-ink)
 *           z                z-index base del item (CK.Z.graphic + item.z). Los hijos de root usan ctx.z (+1, +2…).
 *           layout           {name, slot, railY, seamY, t0, t1, props}; layoutAt(t) para otro instante
 *           railY            y del raíl de subtítulos: no pongas texto encima salvo que ocultes el raíl (caption.hide)
 *           media            [<img>|<video>] estáticos del item (id único; el.ckAsset / el.dataset.asset = id del asset;
 *                            el.ckWrap = envoltorio .ck-mwrap; el.ckZoom = .ck-mzoom). Para usarlos: CK.util.placeMedia(el,
 *                            {x,y,w,h}, z) → el runtime los muestra SOLO en [t0, t1). Si no los colocas, quedan ocultos.
 *                            Alternativa para logos pequeños dentro de tu DOM: crea tu propio <img src=ctx.assetUrl(el.getAttribute('src'))>.
 *           assetUrl(p), faceAt(t), faceMedian(t0,t1), cam, content,
 *           event(kind, t, extra?)  → window.__ckEvents.push({item, component, kind, t}) — llámalo en el instante en que
 *                            pasa algo VISIBLE (entra un elemento, se elige una opción, cae una ficha, aparece un logo):
 *                            el audio alinea los SFX a ese fotograma. Se calcula al animar (no depende del seek). }
 *   CK.tokens.motion (segundos y eases GSAP, de motion_tokens.yaml):
 *     dur.{text_in .233, hero_in .3, text_out .133, caption_pop .133, letter .033, number_in .233, count .7, icon_in .267,
 *          line_draw .4, arrow .233, underline .2, split_in .267, move .3, dim .5, pulse .267, hold_min .8, read_per_word .33}
 *     CK.ease = {enter power3.out · exit power2.in · move power2.inOut · pop back.out(1.4)}  ← ÚNICOS eases permitidos
 *       (qa mo.ease_tokens ≤ 4; los valores vienen de motion_tokens.yaml). pop solo para el foco del beat.
 *       Texturas y cambios discretos (grano, glitch, tecleo): tl.set por paso, sin ease.
 *     stagger.{letters .033, words .083, lines .133, list_2_3 .133, list_4_6 .1}   lead.{default .167, enfasis .1 …}
 *     limits.{min_px_lectura 48, titular_px [96,160], hero_px [180,320] …}
 *   CK.util: el(tag,cls,parent,style,text) · box(el,{x,y,w,h}) · splitWords(el) · splitChars(el) · fitText(el,maxW,maxPx,minPx,maxH)
 *            seeded(seed)→rng · hash · clamp · lerp · fr(frames)→s · snap(t) · color('accent'|'green'|…) · cleanWord
 *            grain(tl,parent,t0,t1,{opacity,fps,seed,blend,z}) · svgFilter(parent,id,inner) · placeMedia(el,box,z)
 *   Variables CSS (runtime.css): --ck-sans (Montserrat) · --ck-serif (alias de Montserrat; regla de estilo: nunca serif ni cursiva;
 *    el énfasis va con peso 800–900, tamaño u oro) · --ck-ui (Inter) ·
 *     --ck-mono (JetBrains Mono, SOLO código/prompts) · --ck-white --ck-ink --ck-navy --ck-accent (#FECA1A) ·
 *     --ck-accent-2 (color del tema) --ck-green --ck-red --ck-muted --ck-card --ck-line --ck-radius(28px) ·
 *     --ck-shadow-1/2/3 · --ck-text-shadow / --ck-text-shadow-hero. Ninguna otra fuente ni color.
 *
 * REGLAS DURAS (HF hace seek y SUPRIME callbacks; lint y QA lo comprueban)
 *   1. Solo tweens de propiedades: nada de onUpdate/onComplete para pintar, ni Math.random/Date/rAF/repeat:-1.
 *   2. fromTo(..., {immediateRender:false}) a partir de t0; el estado inicial (oculto) con gsap.set en mount.
 *   3. Nunca dos tweens solapados sobre la MISMA propiedad del MISMO elemento (encadénalos o usa otro elemento).
 *   4. Valores de px enteros (Math.round); nada de set en t=0 exacto (usa gsap.set en mount).
 *   4b. Eases: SOLO CK.ease.{enter, exit, move, pop}.
 *   5. No animes `root` ni le pongas z-index/transform/opacity (rompería el apilamiento global). Anima hijos.
 *   6. Termina las entradas antes de t1 (la ventana es [t0, t1)); la salida, ≤ 80 % de la entrada y acelerando.
 *   7. Texto ≥ 48 px si hay que leerlo, dentro de ctx.safeRect; 1 foco por momento; sin back/elastic en texto de
 *      cuerpo, datos ni capturas (prohibiciones_back_elastic). Cifras: nunca rebasan su valor.
 *   8. Marca cada bloque de texto con data-ck-text="<tipo>" (el QA mide zonas seguras con boxes.js).
 *   9. Si el solape es intencionado, data-layout-allow-overlap="true" EN CADA elemento con texto (no en el padre).
 *  10. Registra el componente en cutkit/motion/registry_graphics.py → GRAPHICS[name] = {kind, track:'graphic',
 *      props (JSON Schema), dur_min, dur_rec, sfx:[{at:'enter'|'exit'|'<cue>', offset, kind}], when, when_not, media}.
 * ═══════════════════════════════════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  const U = CK.util;

  CK.register('example.kicker_title', {
    kind: 'graphic',
    mount(root, p, ctx) {
      const M = ctx.tokens.motion;
      // 1) DOM: una tarjeta con un titular que se ajusta al ancho útil
      const box = U.el('div', 'ex-card ck-card', root);
      U.box(box, { x: ctx.safeRect.x, y: Math.round(ctx.slot.y + ctx.slot.h * 0.30), w: ctx.safeRect.w, h: 260 });
      box.style.zIndex = String(ctx.z);
      box.setAttribute('data-ck-text', 'title');
      const title = U.el('div', 'ex-title', box, { position: 'absolute', left: '40px', right: '40px', top: '48px',
        fontFamily: 'var(--ck-sans)', fontWeight: '900', color: 'var(--ck-white)', whiteSpace: 'nowrap', letterSpacing: '-0.02em' }, p.text || 'Título');
      U.fitText(title, ctx.safeRect.w - 80, 120, 56);
      const words = U.splitWords(title);
      // 2) estado inicial fuera de la timeline
      gsap.set(box, { opacity: 0, y: 40 });
      gsap.set(words, { opacity: 0, yPercent: 40 });
      return {
        animate(tl, t0, t1, cues) {
          tl.fromTo(box, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: M.dur.text_in, ease: CK.ease.enter, immediateRender: false }, t0);
          ctx.event('graphic.enter', t0);
          // cada palabra en su cue si lo hay (anclada a la voz); si no, stagger corto
          words.forEach((w, i) => {
            const at = cues['w' + i] != null ? cues['w' + i] - M.lead.enfasis : t0 + 0.08 + i * M.stagger.words;
            tl.fromTo(w, { opacity: 0, yPercent: 40 }, { opacity: 1, yPercent: 0, duration: M.dur.text_in, ease: CK.ease.enter, immediateRender: false }, at);
          });
          // salida suave que termina antes de t1 (opcional; si no, corte seco al acabar el clip)
          if (p.exit === 'soft') {
            const d = M.dur.text_out;
            tl.fromTo(box, { opacity: 1 }, { opacity: 0, duration: d, ease: CK.ease.exit, immediateRender: false }, t1 - d - 1 / ctx.fps);
          }
        },
      };
    },
  });
})();
