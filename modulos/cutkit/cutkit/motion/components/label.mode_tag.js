// label.mode_tag — rótulo del MODO sobre un clip real (vídeo corto de «modos/niveles»): píldora de cristal oscuro arriba y
//   centrada (y ≥ 288, fuera de la UI de Shorts/Reels) con el nombre del modo y su medidor de esfuerzo (mismo medidor que
//   viz.mode_ladder: `level` segmentos llenos de `of`). Dice QUÉ modo hizo lo que se ve; nunca rotula una mejora.
//   enter "pop": sube 32 px y aparece (8 f) con el nombre subiendo por su máscara; el medidor se llena segmento a segmento.
//   enter "swap": encadenado a otro tag en un montaje (corte seco de clip): la píldora ya está en su sitio, el nombre nuevo
//         sube por su máscara (nunca un texto puesto), los segmentos
//         hasta `from_level` ya llenos y el resto se llena (sube de nivel). `hot`: aro y medidor oro (el foco).
// props: {label, level, of?=6, hot?, enter?: pop|swap, from_level?, y?, w? (ancho fijo para montajes)}
// eventos: enter (aparece o cambia de modo), exit
(function () {
  'use strict';
  const FPS = 30;
  const f = (n) => n / FPS;
  const R = (v) => Math.round(v);
  function ev(ctx, kind, t) { try { if (ctx && typeof ctx.event === 'function' && isFinite(t)) ctx.event(kind, Math.round(t * FPS) / FPS); } catch (e) { /* opcional */ } }

  CK.register('label.mode_tag', {
    kind: 'graphic',
    mount(root, p, ctx) {
      const U = CK.util;
      const W = ctx.W || 1080;
      const of = Math.max(1, Math.min(8, p.of || 6));
      const level = Math.max(0, Math.min(of, p.level || 0));
      const from = Math.max(0, Math.min(level, p.from_level || 0));
      const wrap = U.el('div', 'mt-wrap' + (p.hot ? ' mt-hot' : ''), root);
      wrap.style.zIndex = String(ctx.z != null ? ctx.z : 50);
      const pill = U.el('div', 'mt-pill', wrap);
      U.el('div', 'mt-glass', pill);
      U.el('div', 'mt-ring', pill);
      // el nombre va en una máscara: en `swap` (montaje) la píldora sigue en su sitio y el nombre nuevo SUBE
      const nmask = U.el('div', 'mt-nmask', pill);
      const name = U.el('div', 'mt-name', nmask, null, p.label || '');
      name.setAttribute('data-ck-text', 'label');
      const meter = U.el('div', 'mt-meter', pill);
      if (p.meter === false) meter.style.display = 'none';   // rótulo simple (p. ej. el nombre del plano en un gancho)
      const segs = [];
      const fills = [];
      for (let i = 0; i < of; i++) {
        const sg = U.el('span', 'mt-seg', meter);
        segs.push(sg);
        if (i < level) fills.push(U.el('span', 'mt-fill', sg));
      }
      U.fitText(name, 620, 58, 48);
      // `w`: ancho FIJO (montaje): todas las instancias con la misma geometría, nombre a la izquierda y medidor anclado
      // a la derecha, así en los cortes solo cambian el texto y el medidor (nunca salta la píldora)
      if (p.w) { pill.style.width = R(p.w) + 'px'; pill.classList.add('mt-fixed'); }
      // centrado en x = 540; arriba, bajo la franja de 288 px de la UI de Shorts/Reels
      const w = R(pill.getBoundingClientRect().width), h = R(pill.getBoundingClientRect().height);
      const y = R(p.y != null ? p.y : Math.max(300, (ctx.slot ? ctx.slot.y : 0) + 300));
      Object.assign(wrap.style, { left: R((W - w) / 2) + 'px', top: y + 'px', width: w + 'px', height: h + 'px' });
      gsap.set(wrap, { opacity: 0 });
      const lit = fills.slice(from, level);
      gsap.set(lit, { scaleX: 0 });
      return {
        animate(tl, t0, t1) {
          const swap = p.enter === 'swap';
          // (los nombres de modo entraban ya puestos): TODO texto entra animado.
          //  pop: la píldora sube 32 px y aparece (opacidad en 10 f ≈ power2.out en 8 f) y el nombre sube por su máscara;
          //  swap: la píldora ya está (montaje) y solo el nombre nuevo sube por su máscara en 8 f.
          const T0 = Math.max(t0, 0.001);
          if (swap) {
            tl.set(wrap, { opacity: 1 }, T0);
          } else {
            tl.fromTo(wrap, { y: 32, scale: 0.96 }, { y: 0, scale: 1, duration: f(8), ease: CK.ease.enter, immediateRender: false }, T0);
            tl.fromTo(wrap, { opacity: 0 }, { opacity: 1, duration: f(10), ease: CK.ease.enter, immediateRender: false }, T0);
          }
          tl.fromTo(name, { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: f(8), ease: CK.ease.enter, immediateRender: false }, T0);
          ev(ctx, 'enter', t0);
          const s0 = t0 + (swap ? f(1) : f(4));
          lit.forEach((s, i) => tl.fromTo(s, { scaleX: 0 }, { scaleX: 1, duration: f(4), ease: CK.ease.enter, immediateRender: false }, s0 + i * f(2)));
          if (p.exit === 'soft' && t1 - t0 > f(14)) {
            tl.fromTo(wrap, { opacity: 1 }, { opacity: 0, duration: f(4), ease: CK.ease.exit, immediateRender: false }, t1 - f(5));
            ev(ctx, 'exit', t1 - f(5));
          }
        },
      };
    },
  });
})();
