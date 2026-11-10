// viz.sessions — las SESIONES de un agente de código como un enjambre de bocadillos con volumen: el motivo visual de la
// sesión principal. Un solo plano vivo que cambia de composición en SUS
//   palabras: aparecen, se reparten en una rejilla, una lupa o un aro las recorre y se encienden, se recolocan, se
//   apartan, se funden en un sitio, brotan cables desde un centro… Ningún dato: cada `n` y cada texto llegan por props
//   con su `source`. Sin lista de pasos fija: `steps` es un guion de operaciones, cada una en su cue.
// props: {n, bubble (asset encendido), bubble_idle (asset en reposo), marker? (asset de la lupa; sin él, aro),
//         assets_map? {clave: asset}, steps:[{op, cue?, dt?, …}], canvas, band?}
//   Todas las coordenadas (x, y, cx, cy) son px del LIENZO: quien dirige comprueba la «T» (288–1240; ≤ 888 bajo y=1000).
//   ops:
//     pop      {ids, layout, within?, ev_f?}  entran en la rejilla o el círculo de `layout`, en ola (`within` f en total);
//                                         `ev_f` retrasa su evento de sonido n fotogramas (una ola rápida tarda en verse)
//     arrange  {ids, layout, dur?}        se mueven a su sitio nuevo
//     tone     {ids, gold?, o?, dur?}     se encienden o se apagan (`o` = opacidad)
//     marker_in {x, y, size} · hop {ids, until?, revert?, step?} · marker_out {}
//                                         la lupa (o el aro) entra, salta de sesión en sesión y se enciende cada una
//     text     {slot, text, px, y, x?, w?, tone?, mark?, mark_cue?}   texto con máscara; releva al anterior de su `slot`
//               typed: letra a letra en type_frames; mono: fuente de terminal; color: #hex;
//              mark_under: subrayado bajo el texto; mark_strike: tachado rojo. text_dim {slot, o?}: lo atenúa sin irse
//     marker_move {x, y, size?, dur?}      el aro pasa a otro punto sin apagarse (sin sesión debajo)
//     bar      {x, y, w, h?, color?, dur?} barra que se dibuja de izquierda a derecha
//     spin     {key, turns, until?, dur?, ease?} la pieza gira turns vueltas de su cue a `until`
//     text_out {slot}                     lo retira
//     logo     {key, asset, x, y, size} · logo_move {key, x, y, size} · swing {key, n?, deg?} · logo_out {key}
//     collapse {ids, x, y, size?}         vuelan a un punto y se funden
//     wires    {from:[x,y], r0, ids, dur?} · pulse {from:[x,y], r0, ids, dur?, step?}
//                                         cables del BORDE del centro al BORDE de cada sesión; un pulso oro los recorre
//                                         y enciende la sesión al llegar
//     ring     {x, y, r0, r1, n?, every?, strong?} ondas que salen de un punto (más opacas y duran más)
//     wires_out {dur?}                     retira los cables dibujados hasta ahora, para mudarlos a otro centro
//     logo_tone {key, o, dur?}             apaga o atenúa un logo sin quitarlo (`o` = opacidad; evento dim)
//   layout: {type:"grid", cols, size, gap, cx, cy} | {type:"ring", cx, cy, rx, ry, size, start?} | {type:"point", x, y, size}
// cues: las que nombre cada step. eventos: enter, pop, arrange, marker, hop, text, mark, fly, logo, swing, wire, pulse, dim, light, exit
(function (CK) {
  "use strict";
  CK.register("viz.sessions", {
    mount(root, props, ctx) {
      const gx = CK.gx;
      const { f, ft, T, R } = gx;
      const E = gx.eases(ctx);
      const st = gx.stage(root, ctx, props, "vs");
      const A = st.A, bd = st.bd;
      const N = Math.max(1, Math.min(40, Number(props.n) || 1));
      const steps = Array.isArray(props.steps) ? props.steps : [];
      const X = (x) => x - A.x, Y = (y) => y - A.y;
      const BASE = 260;
      const wrap = gx.el("div", "vs-wrap", A.node);
      const wires = gx.svg("svg", { class: "vs-wires", width: A.w, height: A.h + 200, viewBox: `0 0 ${A.w} ${A.h + 200}` }, wrap);
      // ── sesiones
      const B = Array.from({ length: N }, () => {
        const n = gx.el("div", "vs-b", wrap);
        Object.assign(n.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
        const idle = gx.logo(n, ctx, props.bubble_idle || props.bubble, "vs-l");
        const gold = gx.logo(n, ctx, props.bubble, "vs-l");
        gsap.set(n, { x: 0, y: 0, scale: 0.4, opacity: 0 });
        gsap.set(gold, { opacity: 0 });
        return { n, idle, gold, x: 0, y: 0, s: 0.4, o: 0, g: 0, tEnd: 0, seen: false };
      });
      // ── marcador
      const x_mono = (n) => { n.style.fontFamily = "var(--ck-mono)"; n.style.fontWeight = "600"; n.style.letterSpacing = "-.02em"; };
      const marker = props.marker ? gx.logo(wrap, ctx, props.marker, "vs-mk") : gx.el("div", "vs-mk vs-mk-ring", wrap);
      gsap.set(marker, { opacity: 0 });
      const M = { x: 0, y: 0, size: 160, o: 0 };
      // ── textos y logos de los pasos
      const TX = new Map(), LG = new Map();
      steps.forEach((s, i) => {
        if (s.op === "text") {
          const m = gx.el("div", "vs-tm", wrap);
          const inner = gx.el("div", "vs-ti", m);
          const txt = String(s.text || "");
          const k = s.mark ? txt.indexOf(s.mark) : -1;
          let bar = null;
          if (k >= 0) {
            if (k > 0) inner.appendChild(document.createTextNode(txt.slice(0, k)));
            const sp = gx.el("span", "vs-mkw", inner);
            bar = gx.el("span", "vs-mkb", sp);
            gx.el("span", "vs-mkt", sp, s.mark);
            if (k + s.mark.length < txt.length) inner.appendChild(document.createTextNode(txt.slice(k + s.mark.length)));
            gsap.set(bar, { scaleX: 0 });
          } else inner.textContent = txt;
          if (s.mono) x_mono(m);
          if (s.mark_strike && bar) Object.assign(bar.style, { bottom: ".44em", height: ".1em", background: "#E5352B", zIndex: 2 });   // tachado rojo en vez de rotulador
          if (s.mark_under && bar) { bar.style.bottom = "-.05em"; bar.style.height = ".12em"; }   // subrayado bajo el texto (texto claro sobre oscuro)
          if (s.color) inner.style.color = s.color;
          if (s.typed) {   // cada carácter en su span: el texto ya ocupa su sitio y se revela letra a letra
            const walk = (n) => Array.from(n.childNodes).forEach((c) => {
              if (c.nodeType === 3) {
                const fr = document.createDocumentFragment();
                Array.from(c.textContent).forEach((ch) => { const sp = document.createElement("span"); sp.className = "vs-ch"; sp.textContent = ch; fr.appendChild(sp); });
                c.replaceWith(fr);
              } else if (!c.classList || !c.classList.contains("vs-mkb")) walk(c);
            });
            walk(inner);
          }
          if (s.tone === "muted") inner.classList.add("vs-muted");
          gsap.set(inner, { yPercent: 115, opacity: 0 });
          if (s.typed) gsap.set(inner.querySelectorAll(".vs-ch"), { opacity: 0 });
          TX.set(i, { m, inner, bar });
        } else if (s.op === "bar") {   // (opcional): una barra que se dibuja de izquierda a derecha (línea en esqueleto)
          const n = gx.el("div", "vs-bar", wrap);
          Object.assign(n.style, { position: "absolute", left: R(X(s.x)) + "px", top: R(Y(s.y) - (s.h || 26) / 2) + "px", width: (s.w || 300) + "px", height: (s.h || 26) + "px",
            borderRadius: ((s.h || 26) / 2) + "px", background: s.color || "#9CA3AF", transformOrigin: "0 50%", zIndex: 3 });
          gsap.set(n, { scaleX: 0 });
          TX.set(i, { bar: n });
        } else if (s.op === "logo") {
          const n = gx.logo(wrap, ctx, s.asset, "vs-logo");
          gsap.set(n, { opacity: 0 });
          LG.set(s.key || "m", { n, x: 0, y: 0, size: s.size || 200 });
        }
      });
      const idsOf = (v) => {
        if (v === "all" || v == null) return B.map((_, i) => i);
        if (Array.isArray(v)) return v.filter((i) => i >= 0 && i < N);
        if (typeof v === "object") { const o = []; for (let i = v.from || 0; i <= Math.min(N - 1, v.to == null ? N - 1 : v.to); i++) o.push(i); return o; }
        return [];
      };
      const spots = (ids, L) => {
        const out = [];
        if (L.type === "ring") {
          const a0 = L.start == null ? -Math.PI / 2 : L.start;
          ids.forEach((id, k) => { const a = a0 + (k / ids.length) * Math.PI * 2; out.push({ id, x: L.cx + L.rx * Math.cos(a), y: L.cy + L.ry * Math.sin(a), size: L.size }); });
        } else if (L.type === "point") {
          ids.forEach((id) => out.push({ id, x: L.x, y: L.y, size: L.size }));
        } else {
          const cols = Math.max(1, L.cols || 5), cell = L.size + (L.gap == null ? 16 : L.gap), rows = Math.ceil(ids.length / cols);
          ids.forEach((id, k) => {
            const r = Math.floor(k / cols), inRow = r < rows - 1 ? cols : ids.length - cols * (rows - 1), c = k - r * cols;
            out.push({ id, x: L.cx + (c - (inRow - 1) / 2) * cell, y: L.cy + (r - (rows - 1) / 2) * cell, size: L.size });
          });
        }
        return out;
      };
      return {
        animate(tl, t0, t1, cues) {
          const C = (k, d) => (k ? gx.cue(cues, k, d) : d);
          gx.ev(ctx, "enter", t0);
          gx.bgIn(tl, bd, t0, t1, 41, props);
          // medidas con las fuentes ya cargadas
          steps.forEach((s, i) => {
            if (s.op !== "text") return;
            const x = TX.get(i), low = (s.y || 0) + (s.px || 60) * 0.7 > 1000;
            const maxW = Number(s.w) > 0 ? s.w : (low ? 696 : A.w);
            const px = gx.fit(x.inner, { max: s.px || 72, min: Math.min(48, s.px || 48), width: maxW, lines: 1 });
            x.m.style.fontSize = px + "px"; x.inner.style.fontSize = "";
            const h = x.m.offsetHeight;
            Object.assign(x.m.style, { left: R(X(s.x == null ? 540 : s.x) - maxW / 2) + "px", width: maxW + "px", top: R(Y(s.y || 500) - h / 2) + "px" });
          });
          const slot = {}, allWires = [];
          let tPrev = t0, last = t1;
          const toneTo = (b, g, at, dur) => {
            if (b.g === g) return;
            ft(tl, b.gold, { opacity: b.g }, { opacity: g, duration: dur || f(6), ease: E.enter }, at);
            b.g = g;
          };
          steps.forEach((s, i) => {
            const at = Math.max(t0 + f(i === 0 ? 0 : 1), C(s.cue, tPrev) + (s.dt || 0));
            tPrev = at;
            switch (s.op) {
              case "pop": {
                const P = spots(idsOf(s.ids), s.layout || {});
                const within = f(Number(s.within) || 12), gap = P.length > 1 ? within / (P.length - 1) : 0;
                P.forEach((p, k) => {
                  const b = B[p.id], ss = p.size / BASE, tk = at + k * gap;
                  ft(tl, b.n, { x: R(X(p.x)), y: R(Y(p.y)), scale: ss * 0.45, opacity: 0 }, { x: R(X(p.x)), y: R(Y(p.y)), scale: ss, opacity: 1, duration: f(8), ease: E.enter }, tk);
                  Object.assign(b, { x: X(p.x), y: Y(p.y), s: ss, o: 1, tEnd: tk + f(8), seen: true });
                });
                gx.ev(ctx, "pop", at + f(Number(s.ev_f) || 0));   // `ev_f`: el sonido, n fotogramas después (por defecto, 0)
                break;
              }
              case "arrange": {
                const P = spots(idsOf(s.ids), s.layout || {});
                const d = f(Number(s.dur) || 12);
                P.forEach((p, k) => {
                  const b = B[p.id], ss = p.size / BASE, tk = Math.max(at + k * f(s.stagger == null ? 0.25 : s.stagger), b.tEnd);
                  ft(tl, b.n, { x: R(b.x), y: R(b.y), scale: b.s }, { x: R(X(p.x)), y: R(Y(p.y)), scale: ss, duration: d, ease: E.move }, tk);
                  Object.assign(b, { x: X(p.x), y: Y(p.y), s: ss, tEnd: tk + d });
                });
                gx.ev(ctx, "arrange", at);
                break;
              }
              case "tone": {
                const d = f(Number(s.dur) || 8);
                idsOf(s.ids).forEach((id) => {
                  const b = B[id];
                  if (s.gold != null) toneTo(b, s.gold ? 1 : 0, at, d);
                  if (s.o != null && s.o !== b.o) { ft(tl, b.n, { opacity: b.o }, { opacity: s.o, duration: d, ease: E.enter }, at); b.o = s.o; }
                });
                gx.ev(ctx, s.gold ? "light" : "dim", at);
                break;
              }
              case "marker_in": {
                const size = s.size || 170, off = props.marker ? size * 0.13 : 0;
                Object.assign(marker.style, { width: size + "px", height: size + "px", left: -size / 2 + "px", top: -size / 2 + "px" });
                ft(tl, marker, { x: R(X(s.x) + off), y: R(Y(s.y) + off), scale: 0.45, opacity: 0 }, { x: R(X(s.x) + off), y: R(Y(s.y) + off), scale: 1, opacity: 1, duration: f(8), ease: E.pop }, at);
                Object.assign(M, { x: X(s.x), y: Y(s.y), size, o: 1, k: 1, t: at + f(8) });
                gx.ev(ctx, "marker", at);
                break;
              }
              case "hop": {
                const ids = idsOf(s.ids), off = props.marker ? M.size * 0.13 : 0;
                const tEnd = s.until ? C(s.until, at + ids.length * 0.4) : at + ids.length * 0.4;
                const gap = s.step ? f(s.step) : Math.max(f(5), (tEnd - at) / Math.max(1, ids.length));
                ids.forEach((id, k) => {
                  const b = B[id], tk = Math.max(at + k * gap, M.t || 0), d = Math.min(gap * 0.8, f(7));
                  ft(tl, marker, { x: R(M.x + off), y: R(M.y + off) }, { x: R(b.x + off), y: R(b.y + off), duration: d, ease: E.move }, tk);
                  Object.assign(M, { x: b.x, y: b.y, t: tk + d });
                  const tl0 = tk + d * 0.7;
                  ft(tl, b.gold, { opacity: s.revert ? 0 : b.g }, { opacity: 1, duration: f(4), ease: E.enter }, tl0);
                  if (s.revert) ft(tl, b.gold, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tl0 + Math.max(f(5), gap));
                  else b.g = 1;
                  gx.ev(ctx, "hop", tl0);
                });
                break;
              }
              case "marker_move": {   // (opcional)
                const off = props.marker ? M.size * 0.13 : 0, k0 = M.k || 1, k1 = s.size ? s.size / M.size : k0, d = f(Number(s.dur) || 10), t = Math.max(at, M.t || at);
                ft(tl, marker, { x: R(M.x + off), y: R(M.y + off), scale: k0 }, { x: R(X(s.x) + off), y: R(Y(s.y) + off), scale: k1, duration: d, ease: E.move }, t);
                Object.assign(M, { x: X(s.x), y: Y(s.y), k: k1, t: t + d });
                gx.ev(ctx, "marker", t);
                break;
              }
              case "marker_out": {
                const off = props.marker ? M.size * 0.13 : 0;
                ft(tl, marker, { opacity: 1, scale: 1 }, { opacity: 0, scale: 0.6, duration: f(6), ease: E.exit }, Math.max(at, M.t || at));
                M.o = 0; void off;
                break;
              }
              case "text": {
                const x = TX.get(i), key = s.slot || "t";
                if (slot[key]) tl.to(slot[key], { opacity: 0, y: -14, duration: f(4), ease: E.exit }, T(at - f(3)));
                if (s.typed) {
                  const chars = Array.from(x.inner.querySelectorAll(".vs-ch")), d = f(Number(s.type_frames) || 20);
                  tl.set(x.inner, { yPercent: 0, opacity: 1 }, T(at));
                  chars.forEach((ch, k) => tl.set(ch, { opacity: 1 }, T(at + (k * d) / Math.max(1, chars.length))));
                } else gx.maskIn(tl, x.inner, at, { frames: s.frames || 8, from: 115 });
                gx.ev(ctx, "text", at);
                if (x.bar) {
                  const tm = Math.max(at + f(6), C(s.mark_cue, at + f(8)));
                  ft(tl, x.bar, { scaleX: 0 }, { scaleX: 1, duration: f(9), ease: E.move }, tm);
                  gx.ev(ctx, "mark", tm);
                }
                slot[key] = x.m;
                break;
              }
              case "text_dim": {   // (opcional): el texto de ese slot se atenúa sin irse (lo tachado cede)
                const key = s.slot || "t";
                if (slot[key]) tl.to(slot[key], { opacity: s.o == null ? 0.35 : Number(s.o), duration: f(Number(s.dur) || 6), ease: E.move }, T(at));
                break;
              }
              case "text_out": {
                const key = s.slot || "t";
                if (slot[key]) { tl.to(slot[key], { opacity: 0, y: -14, duration: f(4), ease: E.exit }, T(at)); slot[key] = null; }
                break;
              }
              case "logo": {
                const g = LG.get(s.key || "m"), size = s.size || 200;
                Object.assign(g.n.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
                const ss = size / BASE;
                ft(tl, g.n, { x: R(X(s.x)), y: R(Y(s.y)), scale: ss * 0.5, opacity: 0 }, { x: R(X(s.x)), y: R(Y(s.y)), scale: ss, opacity: 1, duration: f(9), ease: E.pop }, at);
                Object.assign(g, { x: X(s.x), y: Y(s.y), s: ss });
                gx.ev(ctx, "logo", at);
                break;
              }
              case "logo_move": {
                const g = LG.get(s.key || "m"), ss = (s.size || 200) / BASE, d = f(Number(s.dur) || 12);
                ft(tl, g.n, { x: R(g.x), y: R(g.y), scale: g.s }, { x: R(X(s.x)), y: R(Y(s.y)), scale: ss, duration: d, ease: E.move }, at);
                Object.assign(g, { x: X(s.x), y: Y(s.y), s: ss });
                break;
              }
              case "bar": {
                ft(tl, TX.get(i).bar, { scaleX: 0 }, { scaleX: 1, duration: f(Number(s.dur) || 8), ease: E.move }, at);
                break;
              }
              case "spin": {   // gira de verdad (dos piezas engranadas: mismas cues, vueltas en razón inversa a sus dientes)
                const g = LG.get(s.key || "m"), r0 = g.r || 0, r1 = r0 + 360 * (Number(s.turns) || 1);
                const end = s.until ? C(s.until, at + f(Number(s.dur) || 30)) : at + f(Number(s.dur) || 30);
                g.n.style.filter = "none";   // la sombra iría girando con la pieza
                ft(tl, g.n, { rotation: r0 }, { rotation: r1, duration: Math.max(f(1), end - at), ease: s.ease || "none" }, at);
                g.r = r1;
                break;
              }
              case "swing": {   // la pieza se balancea (una campana que suena) y acaba quieta
                const g = LG.get(s.key || "m"), n = Math.max(1, s.n || 3), deg = s.deg || 10, d = f(Number(s.dur) || 5);
                for (let k = 0; k <= n; k++) {
                  const from = k === 0 ? 0 : (k % 2 ? 1 : -1) * deg * (1 - (k - 1) / n), to = k === n ? 0 : (k % 2 ? -1 : 1) * deg * (1 - k / n);
                  ft(tl, g.n, { rotation: from }, { rotation: to, duration: d, ease: E.move }, at + k * d);
                }
                gx.ev(ctx, "swing", at);
                break;
              }
              case "logo_out": {
                const g = LG.get(s.key || "m");
                ft(tl, g.n, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, at);
                break;
              }
              case "collapse": {
                const ids = idsOf(s.ids), d = f(Number(s.dur) || 12), ss = (s.size || 50) / BASE;
                ids.forEach((id, k) => {
                  const b = B[id], tk = Math.max(at + (k % 6) * f(0.6), b.tEnd);
                  ft(tl, b.n, { x: R(b.x), y: R(b.y), scale: b.s }, { x: R(X(s.x)), y: R(Y(s.y)), scale: ss, duration: d, ease: E.move }, tk);
                  ft(tl, b.n, { opacity: b.o }, { opacity: 0, duration: f(3), ease: E.exit }, tk + d - f(3));
                  Object.assign(b, { x: X(s.x), y: Y(s.y), s: ss, o: 0, tEnd: tk + d });
                });
                gx.ev(ctx, "fly", at);
                break;
              }
              case "wires": {
                const d = f(Number(s.dur) || 9), c = [X(s.from[0]), Y(s.from[1])];
                const list = idsOf(s.ids);
                list.forEach((id, k) => {
                  const b = B[id], dx = b.x - c[0], dy = b.y - c[1], L = Math.hypot(dx, dy) || 1, rb = s.rb != null ? Number(s.rb) : (b.s * BASE) * 0.46;
                  const pts = [[c[0] + (dx / L) * (s.r0 || 0), c[1] + (dy / L) * (s.r0 || 0)], [b.x - (dx / L) * rb, b.y - (dy / L) * rb]];
                  const w = gx.wire(wires, pts, { w: 4, wo: 9 });
                  allWires.push(w);
                  gx.drawWire(tl, w, at + k * f(s.stagger != null ? Number(s.stagger) : 1), d);
                  b.wirePts = pts;
                });
                gx.ev(ctx, "wire", at);
                break;
              }
              case "wires_out": {
                const d = f(Number(s.dur) || 6);
                allWires.splice(0).forEach((w) => ft(tl, [w.ol, w.gd], { opacity: 1 }, { opacity: 0, duration: d, ease: E.exit }, at));
                break;
              }
              case "logo_tone": {
                const g = LG.get(s.key || "m"), o = s.o == null ? 0.3 : Number(s.o), o0 = g.o == null ? 1 : g.o;
                ft(tl, g.n, { opacity: o0 }, { opacity: o, duration: f(Number(s.dur) || 8), ease: E.move }, at);
                g.o = o;
                gx.ev(ctx, "dim", at);
                break;
              }
              case "pulse": {
                const list = idsOf(s.ids), gap = f(Number(s.step) || 4), d = f(Number(s.dur) || 12);
                list.forEach((id, k) => {
                  const b = B[id];
                  if (!b.wirePts) return;
                  const dot = gx.pulseDot(wrap, 22), tk = at + k * gap;
                  gx.pulse(tl, dot, b.wirePts, tk, d);
                  toneTo(b, 1, tk + d - f(2), f(5));
                  gx.ev(ctx, "pulse", tk);
                });
                break;
              }
              case "ring": {
                const n = Math.max(1, s.n || 2), ev = f(Number(s.every) || 16), r0 = s.r0 || 100, r1 = s.r1 || 300;
                for (let k = 0; k < n; k++) {
                  const c = gx.el("div", "vs-wave", wrap);
                  Object.assign(c.style, { width: r1 * 2 + "px", height: r1 * 2 + "px", left: R(X(s.x) - r1) + "px", top: R(Y(s.y) - r1) + "px" });
                  gsap.set(c, { opacity: 0, scale: r0 / r1 });
                  ft(tl, c, { opacity: s.strong ? 1 : 0.85, scale: r0 / r1 }, { opacity: 0, scale: 1, duration: f(s.strong ? 30 : 22), ease: s.strong ? "power1.in" : E.enter }, at + k * ev);
                }
                break;
              }
              default: break;
            }
            last = Math.max(last, at);
          });
          gx.out(tl, props, t1, [wrap], { dur: f(5), ctx });
        },
      };
    },
  });
})(window.CK);
