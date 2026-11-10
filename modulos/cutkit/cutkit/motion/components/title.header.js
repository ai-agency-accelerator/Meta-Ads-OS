// title.header — cabecera FIJA pequeña (logo + nombre, p. ej. «✳ Nimbo») arriba y centrada, que se queda durante todo un
//   tramo (un gancho de tarjetas) para que el espectador no pierda de qué se habla. Va como rótulo «overlay»: no compite
//   con las tarjetas ni con los gráficos del panel.
//   `from`: geometría del héroe anterior (logo.reveal) en px del lienzo → la cabecera nace exactamente ahí (el héroe
//   corta en seco en el mismo fotograma) y se encoge a su sitio en ~0,33 s (continuidad: el héroe SE CONVIERTE en la
//   cabecera). Sin `from`: entra con un fundido corto desde 10 px más abajo.
// props: {text, asset?, y?=210 (centro), size?=68 (cuerpo del nombre), logo_size?=size×1,12, from?: {logo:[cx,cy,lado],
//         text:[cx,cy,cuerpo]}, hold?=0 (s antes de encogerse), tone?=tinta}
// eventos: enter, move
(function () {
  'use strict';
  CK.register('title.header', {
    kind: 'graphic',
    mount(root, p, ctx) {
      const gx = CK.gx;
      const { f, R } = gx;
      const W = ctx.W || 1080;
      const size = R(p.size || 68), L = R(p.logo_size || size * 1.12), gap = R(size * 0.24);
      const yc = R(p.y != null ? p.y : 210);
      const o = gx.originOf(root);
      const wrap = gx.el('div', 'th-wrap', root);
      wrap.style.zIndex = String(ctx.z != null ? ctx.z : 45);
      const src = p.asset ? gx.mediaSrc(ctx, p.asset) : null;
      const logo = src ? gx.el('div', 'th-logo gx-logo', wrap) : null;
      if (logo) { logo.style.backgroundImage = `url("${src}")`; Object.assign(logo.style, { width: L + 'px', height: L + 'px' }); }
      const txt = gx.el('div', 'th-text', wrap, String(p.text || ''));
      txt.style.fontSize = size + 'px';
      if (p.tone) txt.style.color = p.tone;
      // geometría final (px del lienzo): fila centrada en x = 540, centro vertical en y
      const tw = R(txt.offsetWidth), lw = logo ? L + gap : 0, total = lw + tw;
      const x0 = R(W / 2 - total / 2);
      const fin = {};
      if (logo) {
        Object.assign(logo.style, { left: R(x0 - o.x) + 'px', top: R(yc - L / 2 - o.y) + 'px' });
        fin.logo = { cx: x0 + L / 2, cy: yc, s: L };
      }
      Object.assign(txt.style, { left: R(x0 + lw - o.x) + 'px', top: R(yc - size / 2 - o.y) + 'px' });
      fin.text = { cx: x0 + lw + tw / 2, cy: yc, s: size };
      const parts = [logo, txt].filter(Boolean);
      gsap.set(wrap, { opacity: 0 });
      // estado de partida (FLIP): cada pieza donde y como estaba el héroe
      const fr = p.from || null;
      const start = (el, k) => {
        const g = fr && Array.isArray(fr[k]) && fr[k].length === 3 ? fr[k] : null;
        if (!g || !fin[k]) return null;
        return { x: R(g[0] - fin[k].cx), y: R(g[1] - fin[k].cy), scale: g[2] / fin[k].s };
      };
      const st = parts.map((el) => start(el, el === logo ? 'logo' : 'text'));
      parts.forEach((el, i) => { if (st[i]) gsap.set(el, st[i]); });
      return {
        animate(tl, t0, t1) {
          const E = gx.eases(ctx);
          tl.set(wrap, { opacity: 1 }, gx.T(t0));
          gx.ev(ctx, 'enter', t0);
          const flip = st.some(Boolean);
          if (flip) {
            const tm = t0 + Math.max(0, p.hold || 0);
            parts.forEach((el, i) => {
              if (st[i]) gx.ft(tl, el, st[i], { x: 0, y: 0, scale: 1, duration: f(10), ease: E.move }, tm);
            });
            gx.ev(ctx, 'move', tm);
          } else {
            gx.ft(tl, wrap, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: f(6), ease: E.enter }, t0);
          }
          if (p.exit === 'fade') tl.to(wrap, { opacity: 0, duration: f(4), ease: E.exit }, gx.T(Math.max(t0, t1 - f(5))));
          else tl.set(wrap, { opacity: 0 }, gx.T(t1));
        },
      };
    },
  });
})();
