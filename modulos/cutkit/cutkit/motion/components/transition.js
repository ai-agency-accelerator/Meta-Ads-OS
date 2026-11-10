/* cutkit · transiciones (solo al cambiar de bloque o de layout; dentro del bloque, corte seco)
 *
 * Convención de tiempos: el item va de t0 a t1 (≤ 0,4 s) y el CORTE editorial de las capas de debajo cae en
 * `cues.cut` (segundos de programa). Si no viene, se estima: light_leak 45 % de la duración, flash 1 f, resto 50 %.
 * Todo son tweens de propiedades (HF hace seek y suprime callbacks): opacidad/transform de capas, `filter` de
 * #ck-content y atributos de filtros SVG (attr). Recetas: transiciones_recetas.js · camara_transiciones.yaml.
 */
(function () {
  'use strict';
  const U = CK.util;
  const E = CK.ease;            // enter · exit · move · pop (fuente única: runtime.js)
  let uid = 0;

  function cutOf(ctx, t0, t1, cues, frac) {
    const c = cues && cues.cut != null ? cues.cut : (ctx.item.cues && ctx.item.cues.cut);
    return U.snap(c != null ? c : t0 + (t1 - t0) * frac);
  }
  function framesOf(p, dflt, lo, hi, fps) { return U.clamp(Math.round(p.frames || dflt), lo, Math.min(hi, Math.floor(0.4 * fps))); }
  const layer = (parent, css, z) => {
    const d = U.el('div', 'ck-tr-layer', parent);
    d.style.cssText = 'position:absolute;inset:0;pointer-events:none;' + (css || '');
    if (z != null) d.style.zIndex = String(z);
    return d;
  };

  // ───────────────────────── transition.light_leak
  /* LLAMARADA cálida y cromática que llena el plano y tapa el corte: estela naranja/dorada ancha con aberración roja y
   * cian, más un resplandor amplio, todo en `screen` (pico ≈ 0,85, nunca un blanco plano). 6–8 f: sube 1 f, se sostiene
   * del corte −2 f al corte +2 f y cae 2–3 f, barriendo en una dirección. Los subtítulos se ocultan en la ventana. */
  const PALETAS = {
    dorado: { hot: '255 222 160', mid: '255 160 64', deep: '236 92 28' },
    iris: { hot: '235 244 255', mid: '150 200 255', deep: '200 140 255' },
    rojo: { hot: '255 200 160', mid: '255 104 60', deep: '210 40 40' },
    rosa: { hot: '255 218 238', mid: '255 130 190', deep: '190 90 255' },
    plata: { hot: '255 255 255', mid: '226 228 232', deep: '128 132 140', chroma: false },   // neutra: negro y blanco
  };
  CK.register('transition.light_leak', {
    kind: 'transition',
    mount(root, p, ctx) {
      const c = PALETAS[p.palette || 'dorado'] || PALETAS.dorado;
      const dir = p.direction === 'left' ? -1 : 1;
      const ang = dir > 0 ? 104 : 76;
      const L = layer(root, 'mix-blend-mode:screen;opacity:0;overflow:hidden;', ctx.z);
      const band = (css) => layer(L, 'inset:-20% -90%;' + css);
      // resplandor amplio que llena el plano (cálido, con caída) + estela ancha + bordes con aberración
      const glow = band(`background:radial-gradient(ellipse 60% 70% at 50% 46%, rgb(${c.mid} / 75%) 0%, rgb(${c.deep} / 45%) 45%, rgb(${c.deep} / 18%) 75%, transparent 100%);`);
      const main = band(`background:linear-gradient(${ang}deg, transparent 18%, rgb(${c.deep} / 55%) 30%, rgb(${c.mid} / 90%) 41%, rgb(${c.hot}) 48%, rgb(${c.hot}) 52%, rgb(${c.mid} / 88%) 59%, rgb(${c.deep} / 50%) 70%, transparent 82%);`);
      const ab = c.chroma === false ? 0 : 1;   // la paleta neutra no lleva aberración de color
      const red = band(`background:linear-gradient(${ang}deg, transparent 26%, rgba(255,60,40,${.42 * ab}) 33%, transparent 41%);`);
      const cyan = band(`background:linear-gradient(${ang}deg, transparent 59%, rgba(60,200,255,${.30 * ab}) 66%, transparent 74%);`);
      return {
        animate(tl, t0, t1, cues) {
          const fps = ctx.fps, fr = (n) => n / fps;
          const frames = U.clamp(Math.round(p.frames || 7), 6, 8);
          const cut = cutOf(ctx, t0, t1, cues, 0.45);
          const start = Math.max(t0, cut - fr(3));
          const end = Math.min(t1 - 0.001, start + fr(frames));
          // `peak` (0,05–0,88) fija la opacidad máxima a mano (p. ej. 0,35: luz plata discreta); si no, la de siempre
          const peak = p.peak != null ? U.clamp(p.peak, 0.05, 0.88) : U.clamp(0.85 * (p.intensity != null ? Math.max(0.8, p.intensity) : 1), 0.7, 0.88);
          ctx.event('transition.cut', cut, { peak_from: U.snap(cut - fr(2)), peak_to: U.snap(cut + fr(2)) });
          const holdFrom = Math.min(cut - fr(2), start + fr(1)), holdTo = Math.min(end - fr(1), cut + fr(2));
          tl.fromTo(L, { opacity: 0 }, { opacity: peak, duration: Math.max(fr(0.5), holdFrom - start), ease: E.enter, immediateRender: false }, start);
          tl.fromTo(L, { opacity: peak }, { opacity: 0, duration: Math.max(fr(1), end - holdTo), ease: E.exit, immediateRender: false }, holdTo);
          const sweep = (el, a, b2) => tl.fromTo(el, { xPercent: a * dir }, { xPercent: b2 * dir, duration: end - start, ease: E.move, immediateRender: false }, start);
          sweep(main, -30, 30); sweep(red, -34, 26); sweep(cyan, -26, 34); sweep(glow, -12, 12);
        },
      };
    },
  });

  // ───────────────────────── transition.flash
  CK.register('transition.flash', {
    kind: 'transition',
    mount(root, p, ctx) {
      const f = layer(root, `background:${p.color || '#FFFFFF'};opacity:0;`, ctx.z + 1);
      const b = p.bloom === false ? null : layer(root, 'mix-blend-mode:screen;opacity:0;background:radial-gradient(ellipse 70% 50% at 50% 45%, rgb(255 250 235 / 90%), rgb(255 230 200 / 35%) 55%, transparent 80%);', ctx.z);
      return {
        animate(tl, t0, t1, cues) {
          const fps = ctx.fps, fr = (n) => n / fps;
          const cut = cutOf(ctx, t0, t1, cues, 0);
          const peak = p.peak != null ? p.peak : 1;
          ctx.event('transition.cut', cut);
          const at = Math.max(t0, cut - fr(1));
          tl.fromTo(f, { opacity: 0 }, { opacity: peak, duration: Math.max(fr(0.5), cut - at), ease: E.exit, immediateRender: false }, at);
          tl.fromTo(f, { opacity: peak }, { opacity: 0, duration: fr(4), ease: E.enter, immediateRender: false }, cut + fr(1));
          if (b) {
            tl.fromTo(b, { opacity: 0 }, { opacity: 0.8 * peak, duration: Math.max(fr(0.5), cut - at), ease: E.exit, immediateRender: false }, at);
            tl.fromTo(b, { opacity: 0.8 * peak }, { opacity: 0, duration: Math.min(fr(7), t1 - cut - fr(1) - 0.001), ease: E.enter, immediateRender: false }, cut + fr(1));
          }
        },
      };
    },
  });

  // ───────────────────────── transition.whip — barrido con desenfoque direccional simulado
  CK.register('transition.whip', {
    kind: 'transition',
    mount(root, p, ctx) {
      const id = 'ck-whip-' + (++uid);
      const filt = U.svgFilter(root, id, '<feGaussianBlur stdDeviation="0 0" edgeMode="duplicate"/>');
      const gb = filt.querySelector('feGaussianBlur');
      return {
        animate(tl, t0, t1, cues) {
          const fps = ctx.fps;
          const frames = framesOf(p, 4, 3, 5, fps), dur = frames / fps;
          const cut = cutOf(ctx, t0, t1, cues, 0.5);
          const start = Math.max(t0, cut - dur / 2), end = Math.min(t1 - 0.001, cut + dur / 2);
          ctx.event('transition.cut', cut);
          const dir = p.direction || 'left';
          const horiz = dir === 'left' || dir === 'right';
          const sign = (dir === 'left' || dir === 'up') ? -1 : 1;
          const travel = Math.round((p.travel || 110) * (horiz ? 1 : 1.4));
          const maxB = U.clamp(p.blur || 36, 12, 48);
          const prop = horiz ? 'x' : 'y';
          const over = 1 + (2 * travel) / (horiz ? ctx.W : ctx.H) + 0.03;
          const sd = (b) => (horiz ? `${b} 0` : `0 ${b}`);
          const C = ctx.content;
          tl.set(C, { filter: `url(#${id})`, transformOrigin: '50% 50%' }, start);
          tl.fromTo(C, { [prop]: 0, scale: 1 }, { [prop]: sign * travel, scale: over, duration: cut - start, ease: E.exit, immediateRender: false }, start);
          tl.fromTo(C, { [prop]: -sign * travel, scale: over }, { [prop]: 0, scale: 1, duration: end - cut, ease: E.enter, immediateRender: false }, cut);
          tl.fromTo(gb, { attr: { stdDeviation: sd(0) } }, { attr: { stdDeviation: sd(maxB) }, duration: cut - start, ease: E.exit, immediateRender: false }, start);
          tl.fromTo(gb, { attr: { stdDeviation: sd(maxB) } }, { attr: { stdDeviation: sd(0) }, duration: end - cut, ease: E.enter, immediateRender: false }, cut);
          tl.set(C, { filter: 'none' }, end + 0.0005);
        },
      };
    },
  });

  // ───────────────────────── transition.zoom_blur — entra/sale con zoom y desenfoque hacia un punto focal
  CK.register('transition.zoom_blur', {
    kind: 'transition',
    mount(root, p, ctx) {
      return {
        animate(tl, t0, t1, cues) {
          const fps = ctx.fps;
          const frames = framesOf(p, 6, 4, 8, fps), dur = frames / fps;
          const cut = cutOf(ctx, t0, t1, cues, 0.5);
          const start = Math.max(t0, cut - dur / 2), end = Math.min(t1 - 0.001, cut + dur / 2);
          let fx = ctx.W / 2, fy = ctx.H * 0.42;
          if (p.focus && typeof p.focus === 'object') { fx = p.focus.x * ctx.W; fy = p.focus.y * ctx.H; }
          else if (p.focus !== 'center') {
            const L = ctx.layoutAt(cut + 1e-3), f = ctx.faceAt(cut), c = L.cam || { x: 0, y: 0, scale: 1 };
            fx = c.x + c.scale * (f.x + f.w / 2) * ctx.W; fy = c.y + c.scale * (f.y + f.h * 0.4) * ctx.H;
          }
          const s = U.clamp(p.scale || 1.3, 1.1, 1.35), b = U.clamp(p.blur || 12, 6, 16);
          ctx.event('transition.cut', cut);
          const C = ctx.content;
          tl.set(C, { transformOrigin: `${Math.round(fx)}px ${Math.round(fy)}px` }, start);
          tl.fromTo(C, { scale: 1, filter: 'blur(0px) brightness(1)' }, { scale: s, filter: `blur(${b}px) brightness(1.15)`, duration: cut - start, ease: E.exit, immediateRender: false }, start);
          tl.fromTo(C, { scale: s, filter: `blur(${b}px) brightness(1.15)` }, { scale: 1, filter: 'blur(0px) brightness(1)', duration: end - cut, ease: E.enter, immediateRender: false }, cut);
          tl.set(C, { filter: 'none' }, end + 0.0005);
        },
      };
    },
  });

  // ───────────────────────── transition.glitch — separación RGB + desplazamiento por franjas (raro: ≤ 2 por vídeo)
  CK.register('transition.glitch', {
    kind: 'transition',
    mount(root, p, ctx) {
      const id = 'ck-glitch-' + (++uid);
      const seed = (U.hash(ctx.item.id) % 97) + 1;
      const filt = U.svgFilter(root, id,
        '<feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>' +
        '<feOffset in="r" dx="0" dy="0" result="ro"/>' +
        '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0" result="gb"/>' +
        '<feOffset in="gb" dx="0" dy="0" result="gbo"/>' +
        '<feBlend in="ro" in2="gbo" mode="screen" result="rgb"/>' +
        `<feTurbulence type="fractalNoise" baseFrequency="0.0002 0.045" numOctaves="1" seed="${seed}" result="n"/>` +
        '<feDisplacementMap in="rgb" in2="n" scale="0" xChannelSelector="R" yChannelSelector="G"/>');
      const offs = filt.querySelectorAll('feOffset');
      const turb = filt.querySelector('feTurbulence');
      const disp = filt.querySelector('feDisplacementMap');
      return {
        animate(tl, t0, t1, cues) {
          const fps = ctx.fps;
          const frames = framesOf(p, 5, 3, 6, fps), dur = frames / fps;
          const cut = cutOf(ctx, t0, t1, cues, 0.5);
          const start = Math.max(t0, cut - dur / 2), end = Math.min(t1 - 0.001, cut + dur / 2);
          const px = U.clamp(p.rgb_offset || 10, 6, 14);
          const C = ctx.content;
          ctx.event('transition.cut', cut);
          // un estado por fotograma (tl.set: sin ease): desplazamiento RGB y franjas con envolvente que pica en el corte
          const rnd = U.seeded(ctx.item.id + ':glitch');
          const nF = Math.max(2, Math.round((end - start) * fps));
          tl.set(C, { filter: `url(#${id})` }, start);
          for (let i = 0; i < nF; i++) {
            const t = U.snap(start + i / fps);
            const env = 1 - Math.abs((t - cut) / Math.max(1 / fps, (end - start) / 2));
            const k = Math.max(0.25, env);
            const dx = Math.round(px * k * (rnd() < 0.5 ? -1 : 1));
            tl.set(offs[0], { attr: { dx } }, t);
            tl.set(offs[1], { attr: { dx: -dx } }, t);
            tl.set(disp, { attr: { scale: Math.round(70 * k * (0.5 + rnd() * 0.5)) } }, t);
            tl.set(turb, { attr: { seed: seed + i * 37 } }, t);
          }
          tl.set(offs[0], { attr: { dx: 0 } }, end + 0.0005);
          tl.set(offs[1], { attr: { dx: 0 } }, end + 0.0005);
          tl.set(disp, { attr: { scale: 0 } }, end + 0.0005);
          tl.set(C, { filter: 'none' }, end + 0.0005);
        },
      };
    },
  });
})();
