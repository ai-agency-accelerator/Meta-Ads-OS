/* cutkit · overlays de acabado
 *   overlay.grain    — grano determinista a 12 fps (background-position a saltos, ease steps; sin callbacks).
 *                      NUNCA sobre la cara: por defecto se recorta a la zona útil del layout (area: "slot").
 *   overlay.vignette — viñeta radial suave (no sobre la junta del split).
 */
(function () {
  'use strict';
  const U = CK.util;
  const E = CK.ease;            // enter · exit · move · pop (fuente única: runtime.js)

  CK.register('overlay.grain', {
    kind: 'overlay',
    mount(root, p, ctx) {
      const holder = U.el('div', 'ck-grain-holder', root, { position: 'absolute', overflow: 'hidden', pointerEvents: 'none' });
      const area = p.area === 'full' ? { x: 0, y: 0, w: ctx.W, h: ctx.H } : (p.area && typeof p.area === 'object' ? p.area : ctx.slot);
      U.box(holder, area);
      holder.style.zIndex = String(ctx.z);
      return {
        animate(tl, t0, t1) {
          U.grain(tl, holder, t0, t1, { opacity: U.clamp(p.opacity != null ? p.opacity : 0.05, 0.02, 0.16), fps: p.fps || 12,
            seed: p.seed || ctx.item.id, blend: p.blend || 'normal', freq: p.freq || 0.82 });
        },
      };
    },
  });

  CK.register('overlay.vignette', {
    kind: 'overlay',
    mount(root, p, ctx) {
      const s = U.clamp(p.strength != null ? p.strength : 0.25, 0.1, 0.6);
      const v = U.el('div', 'ck-vignette', root, { position: 'absolute', inset: '0', pointerEvents: 'none',
        background: `radial-gradient(${p.shape || '115% 80% at 50% 45%'}, rgba(0,0,0,0) 55%, rgba(0,0,0,${s}) 100%)` });
      v.style.zIndex = String(ctx.z);
      return {
        animate(tl, t0, t1) {
          const f = (p.fade_frames != null ? p.fade_frames : 6) / ctx.fps;
          if (f > 0 && t1 - t0 > 2 * f) {
            tl.fromTo(v, { opacity: 0 }, { opacity: 1, duration: f, ease: E.move, immediateRender: false }, t0);
          }
        },
      };
    },
  });
})();
