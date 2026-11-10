// viz.capture_cam — una o varias capturas REALES como hojas que entran en su palabra y se marcan en oro línea a línea
// (la respuesta real de la sesión principal y el diálogo real de permiso).
//   Nada se dibuja encima salvo la marca: el texto es el de la imagen. Sin marco, si el lienzo es del color de la captura
//   (`canvas` #161616), la hoja se funde con el fondo; con `frame`, tarjeta con sombra sobre el papel.
// props: {sheets:[{asset, img_w, img_h, left, top, width, cue?}], marks?:[{cue, sheet?, box:[x,y,w,h], kind?: underline|box}],
//         frame?: bool, drift?: 0–0.04, canvas}
//   left, top, width = px del LIENZO: quien dirige comprueba la «T». box = fracciones de SU hoja.
//   drift: empuje lento de todo el plano (power2.inOut; ≤ 4 %) alrededor de drift_at [x, y], para que no se quede quieto
// row: {idle, gold, n, cy, size?, gap?, cue, lit:[cue…]}: fila centrada de iconos bajo las hojas;
//     entra en `cue` y cada uno se enciende en su cue de `lit`. Para contar algo que la captura dice sin enseñar el detalle
// texts: [{text, px, y, cue, out?}]: rótulo Montserrat centrado en x=540, con máscara, que entra en
//     `cue` y se retira en `out`, para que la misma captura siga en pantalla sin cortar. px ≤ 96 e y ≥ 360 (zona segura)
// cues: las que nombren `sheets`, `marks` y `row`. eventos: enter, sheet, mark, box, row, lit, exit
(function (CK) {
  "use strict";
  CK.register("viz.capture_cam", {
    mount(root, props, ctx) {
      const gx = CK.gx;
      const { f, ft, R } = gx;
      const E = gx.eases(ctx);
      const st = gx.stage(root, ctx, props, "cc");
      const A = st.A, bd = st.bd;
      const wrap = gx.el("div", "cc-wrap", A.node);
      const sheets = (props.sheets || []).map((s) => {
        const n = gx.el("div", "cc-sheet" + (props.frame ? " cc-frame" : ""), wrap);
        const w = Number(s.width) || 950, h = R((w * s.img_h) / s.img_w);
        Object.assign(n.style, { left: R((s.left == null ? 65 : s.left) - A.x) + "px", top: R(s.top - A.y) + "px", width: w + "px", height: h + "px" });
        gx.logo(n, ctx, s.asset, "cc-img");
        gsap.set(n, { opacity: 0 });
        return { s, n, w, h };
      });
      const texts = (props.texts || []).map((t) => {
        const m = gx.el("div", "cc-tm", wrap), i = gx.el("div", "cc-ti", m, t.text);
        const px = Number(t.px) || 84;
        Object.assign(m.style, { left: R(65 - A.x) + "px", width: "950px", top: R(t.y - (px * 1.3) / 2 - A.y) + "px", fontSize: px + "px" });
        gsap.set(i, { yPercent: 115, opacity: 0 });
        return { t, m, i };
      });
      const rc = props.row && props.row.idle ? props.row : null;
      const rowN = rc ? Math.max(1, Math.min(8, Number(rc.n) || 1)) : 0, rowS = rc ? Number(rc.size) || 150 : 0, rowG = rc && rc.gap != null ? Number(rc.gap) : 24;
      const rowItems = Array.from({ length: rowN }, (_, k) => {
        const b = gx.el("div", "cc-b", wrap);
        Object.assign(b.style, { left: R(540 + (k - (rowN - 1) / 2) * (rowS + rowG) - rowS / 2 - A.x) + "px", top: R(rc.cy - rowS / 2 - A.y) + "px", width: rowS + "px", height: rowS + "px" });
        gx.logo(b, ctx, rc.idle, "cc-bl");
        const gold = gx.logo(b, ctx, rc.gold || rc.idle, "cc-bl");
        gsap.set(b, { opacity: 0 }); gsap.set(gold, { opacity: 0 });
        return { b, gold };
      });
      const marks = (props.marks || []).map((m) => {
        const sh = sheets[m.sheet || 0], kind = m.kind || "underline";
        const [x, y, w, h] = m.box || [0, 0, 0, 0];
        const n = gx.el("div", "cc-mk cc-mk-" + kind, sh.n);
        if (kind === "box") Object.assign(n.style, { left: R(x * sh.w) + "px", top: R(y * sh.h) + "px", width: R(w * sh.w) + "px", height: R(h * sh.h) + "px" });
        else Object.assign(n.style, { left: R(x * sh.w) + "px", top: R((y + h) * sh.h) + "px", width: R(w * sh.w) + "px" });
        gsap.set(n, kind === "box" ? { opacity: 0, scale: 1.05 } : { scaleX: 0 });
        return { m, n, kind };
      });
      return {
        animate(tl, t0, t1, cues) {
          const C = (k, d) => (k ? gx.cue(cues, k, d) : d);
          gx.ev(ctx, "enter", t0);
          gx.bgIn(tl, bd, t0, t1, 47, props);
          sheets.forEach((x, i) => {
            const at = i === 0 ? Math.max(t0, C(x.s.cue, t0)) : C(x.s.cue, t0 + f(12));
            ft(tl, x.n, { opacity: 0, y: 30, scale: 0.985 }, { opacity: 1, y: 0, scale: 1, duration: f(8), ease: E.enter }, at);
            if (i > 0) gx.ev(ctx, "sheet", at);
          });
          texts.forEach((x) => {
            const at = C(x.t.cue, t0 + f(6));
            gx.maskIn(tl, x.i, at, { frames: 8, from: 115 });
            gx.ev(ctx, "sheet", at);
            if (x.t.out) tl.to(x.m, { opacity: 0, y: -14, duration: f(4), ease: E.exit }, gx.T(C(x.t.out, t1) - f(4)));
          });
          const dr = Number(props.drift) || 0;
          if (dr > 0) {
            const p = props.drift_at || [540, 764];
            wrap.style.transformOrigin = R(p[0] - A.x) + "px " + R(p[1] - A.y) + "px";
            ft(tl, wrap, { scale: 1 }, { scale: 1 + Math.min(0.04, dr), duration: Math.max(f(10), t1 - t0), ease: E.move }, t0);
          }
          marks.forEach((x) => {
            const at = C(x.m.cue, t0 + f(10));
            if (x.kind === "box") {
              ft(tl, x.n, { opacity: 0, scale: 1.05 }, { opacity: 1, scale: 1, duration: f(7), ease: E.enter }, at);
              gx.ev(ctx, "box", at);
            } else {
              ft(tl, x.n, { scaleX: 0 }, { scaleX: 1, duration: f(8), ease: E.move }, at);
              gx.ev(ctx, "mark", at);
            }
          });
          if (rowItems.length) {
            const at = C(rc.cue, t0 + f(12));
            rowItems.forEach((x, k) => ft(tl, x.b, { opacity: 0, scale: 0.45 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, at + k * f(2)));
            gx.ev(ctx, "row", at + f(1));
            (rc.lit || []).forEach((cue, k) => {
              if (!rowItems[k]) return;
              const tk = Math.max(at + k * f(2) + f(6), C(cue, at + f(10) + k * f(8)));
              ft(tl, rowItems[k].gold, { opacity: 0 }, { opacity: 1, duration: f(5), ease: E.enter }, tk);
              gx.ev(ctx, "lit", tk + f(1));
            });
          }
          gx.out(tl, props, t1, [wrap], { dur: f(5), ctx });
        },
      };
    },
  });
})(window.CK);
