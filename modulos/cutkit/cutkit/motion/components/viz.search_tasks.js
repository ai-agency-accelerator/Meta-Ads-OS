// viz.search_tasks — remate «encontrar la información mucho más rápido / ejecutar tareas de una forma mucho más sencilla»
//   como dos escenas 2D que se relevan en el mismo plano (contenedor que nunca corta):
//   1 · búsqueda: la barra (lupa del kit) aparece, los resultados caen AL INSTANTE con el rayo del kit y estelas de
//       velocidad, y el primero queda marcado (borde oro + check que se dibuja) en «la información»;
//   2 · tareas: la escena sube y entra una lista de tareas con engranajes del kit que giran; cada casilla se ejecuta
//       (barra oro de progreso) y se marca SOLA, una detrás de otra.
//   Las filas son esqueletos (barras grises): no se inventa ningún contenido. El único texto son los dos héroes, que
//   entran SIEMPRE con su máscara (texto animado) y con el rotulador oro en su palabra.
// props: {search:{hero, mark?, icon?, fast_icon?}, tasks:{hero, mark?, icon?, rows?=3}, canvas, anchor?=0.43}
// cues: a_in, a_fast, a_mark, a_found, b_in, b_run, b_hero, b_mark
// eventos: enter, burst, found, swap, tick, hero, mark, exit
(function (CK) {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  CK.register("viz.search_tasks", {
    mount(root, props, ctx) {
      const gx = CK.gx;
      const { f, ft, T, R } = gx;
      const E = gx.eases(ctx);
      const st = gx.stage(root, ctx, props, "sx");
      const A = st.A, bd = st.bd;
      const H = ctx.H || 1920;
      const SA = props.search || {}, SB = props.tasks || {};
      if (!SA.hero || !SB.hero) throw new Error("viz.search_tasks: search.hero y tasks.hero obligatorios");
      const s = Math.max(0.8, Math.min(1.1, A.w / 950));
      A.node.style.setProperty("--s", s);
      const S = (v) => R(v * s);
      const narrow = A.tee ? A.wLow : A.w;                    // lo que baja de y=1000 cabe en 696 px en la «T»
      const anc = (typeof props.anchor === "number" && isFinite(props.anchor) ? props.anchor : 0.43) * H - A.y;

      // ── héroe con máscara y rotulador en su palabra
      const hero = (parent, text, mark) => {
        const m = gx.el("div", "sx-hm", parent);
        const i = gx.el("div", "sx-hi", m);
        const k = mark ? text.indexOf(mark) : -1;
        let bar = null;
        if (k >= 0) {
          if (k > 0) i.appendChild(document.createTextNode(text.slice(0, k)));
          const sp = gx.el("span", "sx-mk", i);
          bar = gx.el("span", "sx-mk-bg", sp);
          gx.el("span", "sx-mk-t", sp, mark);
          if (k + mark.length < text.length) i.appendChild(document.createTextNode(text.slice(k + mark.length)));
        } else i.textContent = text;
        if (bar) gsap.set(bar, { scaleX: 0 });
        gsap.set(i, { yPercent: 115 });
        return { m, i, bar };
      };
      const skel = (parent, w, cls) => { const b = gx.el("i", "sx-sk " + (cls || ""), parent); b.style.width = w; return b; };

      // ════ escena 1 · búsqueda
      const a = gx.el("div", "sx-scene", A.node);
      const heroA = hero(a, String(SA.hero), SA.mark ? String(SA.mark) : "");
      const barW = Math.min(S(860), A.w), barH = S(124);
      const bar = gx.el("div", "sx-bar", a);
      Object.assign(bar.style, { width: barW + "px", height: barH + "px", left: R((A.w - barW) / 2) + "px" });
      const lupa = SA.icon ? gx.logo(bar, ctx, SA.icon, "sx-ic") : null;
      if (lupa) Object.assign(lupa.style, { width: S(92) + "px", height: S(92) + "px" });
      const field = gx.el("div", "sx-field", bar);
      const caret = gx.el("i", "sx-caret", field);
      const q = skel(field, "46%", "sx-sk-q");
      const scan = gx.el("i", "sx-scan", field);
      const rayo = SA.fast_icon ? gx.logo(bar, ctx, SA.fast_icon, "sx-ic sx-rayo") : null;
      if (rayo) Object.assign(rayo.style, { width: S(84) + "px", height: S(84) + "px" });
      const streaks = [0, 1, 2].map((k) => { const l = gx.el("i", "sx-streak", bar); l.style.top = R(barH * (0.32 + k * 0.18)) + "px"; l.style.width = S(70 - k * 18) + "px"; return l; });
      const resW = Math.min(S(680), narrow), resH = S(86);
      const res = gx.el("div", "sx-res", a);
      Object.assign(res.style, { width: resW + "px", left: R((A.w - resW) / 2) + "px" });
      const results = [0, 1, 2].map((k) => {
        const r = gx.el("div", "sx-row", res);
        r.style.height = resH + "px";
        gx.el("i", "sx-thumb", r);
        const tx = gx.el("div", "sx-tx", r);
        skel(tx, ["74%", "62%", "68%"][k], "sx-sk-a");
        skel(tx, ["48%", "40%", "52%"][k], "sx-sk-b");
        const edge = gx.el("i", "sx-edge", r);
        const badge = gx.el("div", "sx-badge", r);
        const sv = document.createElementNS(NS, "svg"); sv.setAttribute("viewBox", "0 0 40 40"); badge.appendChild(sv);
        const tick = document.createElementNS(NS, "path"); tick.setAttribute("d", "M10 21 L17 28 L30 13"); sv.appendChild(tick);
        tick.style.strokeDasharray = "30 30"; tick.style.strokeDashoffset = "30";
        gsap.set([edge], { scaleY: 0 }); gsap.set(badge, { opacity: 0, scale: 0.4 });
        return { r, edge, badge, tick };
      });

      // ════ escena 2 · tareas
      const b = gx.el("div", "sx-scene", A.node);
      const heroB = hero(b, String(SB.hero), SB.mark ? String(SB.mark) : "");
      const nRows = Math.max(2, Math.min(4, SB.rows || 3));
      const card = gx.el("div", "sx-card", b);
      const cardW = Math.min(S(680), narrow);
      Object.assign(card.style, { width: cardW + "px", left: R((A.w - cardW) / 2) + "px" });
      const ch = gx.el("div", "sx-chead", card);
      const gears = SB.icon ? gx.logo(ch, ctx, SB.icon, "sx-ic sx-gears") : null;
      if (gears) Object.assign(gears.style, { width: S(88) + "px", height: S(88) + "px" });
      const chs = gx.el("div", "sx-tx", ch); skel(chs, "58%", "sx-sk-h"); skel(chs, "34%", "sx-sk-b");
      const tasks = Array.from({ length: nRows }, (_, k) => {
        const r = gx.el("div", "sx-trow", card);
        r.style.height = resH + "px";
        const box = gx.el("div", "sx-box", r);
        const sv = document.createElementNS(NS, "svg"); sv.setAttribute("viewBox", "0 0 40 40"); box.appendChild(sv);
        const tick = document.createElementNS(NS, "path"); tick.setAttribute("d", "M10 21 L17 28 L30 13"); sv.appendChild(tick);
        tick.style.strokeDasharray = "30 30"; tick.style.strokeDashoffset = "30";
        const tx = gx.el("div", "sx-tx", r);
        const sk = skel(tx, ["70%", "56%", "64%", "50%"][k], "sx-sk-a");
        const prog = gx.el("i", "sx-prog", tx);
        gsap.set(prog, { scaleX: 0 });
        return { r, box, tick, sk, prog };
      });

      // ── colocación: cada escena centrada en el ancla (lo que baja de 1000 cabe en 696 px)
      const place = (scene, parts) => {
        let y = 0; const gap = S(40);
        parts.forEach((p, k) => { p.style.top = y + "px"; y += p.offsetHeight + (k < parts.length - 1 ? gap : 0); });
        scene.style.height = y + "px";
        scene.style.top = R(anc - y / 2) + "px";
      };
      gsap.set([bar, res].concat(results.map((x) => x.r)), { opacity: 0 });
      gsap.set([b, card].concat(tasks.map((x) => x.r)), { opacity: 0 });
      gsap.set([lupa, rayo, gears].filter(Boolean), { opacity: 0 });
      gsap.set(streaks, { opacity: 0, scaleX: 0.2 });
      gsap.set(scan, { opacity: 0 });

      return {
        animate(tl, t0, t1, cues) {
          const C = (k, d) => gx.cue(cues, k, d);
          // medidas con las fuentes cargadas: cuerpo común de los dos héroes (una línea) y colocación de cada escena
          const hs = Math.min(gx.fit(heroA.i, { max: S(96), min: 60, width: A.w - S(20), lines: 1 }), gx.fit(heroB.i, { max: S(96), min: 60, width: A.w - S(20), lines: 1 }));
          heroA.m.style.fontSize = heroB.m.style.fontSize = hs + "px";
          heroA.i.style.fontSize = heroB.i.style.fontSize = "";
          place(a, [heroA.m, bar, res]);
          place(b, [heroB.m, card]);
          gx.ev(ctx, "enter", t0);
          gx.bgIn(tl, bd, t0, t1, 37, props);

          // ── 1 · la barra aparece (en «encontrar»): sube y se asienta; la lupa entra con asiento y el cursor parpadea
          const tA = Math.max(t0 + f(1), C("a_in", t0 + f(1)));
          ft(tl, bar, { opacity: 0, y: S(30), scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: f(9), ease: E.enter }, tA);
          if (lupa) ft(tl, lupa, { opacity: 0, scale: 0.4, rotation: -20 }, { opacity: 1, scale: 1, rotation: 0, duration: f(10), ease: E.pop }, tA + f(2));
          for (let tc = tA + f(9), k = 0; tc < t1; tc += f(8), k++) tl.set(caret, { opacity: k % 2 ? 1 : 0 }, T(tc));
          ft(tl, scan, { opacity: 0, xPercent: -100 }, { opacity: 1, xPercent: 0, duration: f(6), ease: E.enter }, tA + f(6));
          // lupa que «busca»: vaivén corto hasta que encuentra
          const tF = Math.max(tA + f(10), C("a_fast", tA + 0.45));
          if (lupa) { const sw = [-10, 8, -6]; sw.forEach((v, k) => ft(tl, lupa, { rotation: k ? sw[k - 1] : 0 }, { rotation: v, duration: Math.max(f(3), (tF - tA - f(10)) / 3), ease: E.move }, tA + f(10) + k * Math.max(f(3), (tF - tA - f(10)) / 3))); }
          // ── 2 · AL INSTANTE: rayo + estelas, resultados que caen en 2 f de escalón, el héroe sube
          if (rayo) ft(tl, rayo, { opacity: 0, scale: 0.3, rotation: 18, x: S(40) }, { opacity: 1, scale: 1, rotation: 0, x: 0, duration: f(8), ease: E.pop }, tF);
          ft(tl, streaks, { opacity: 0.9, scaleX: 1.2, x: S(40) }, { opacity: 0, scaleX: 0.3, x: -S(120), duration: f(9), ease: E.exit, stagger: f(1) }, tF);
          if (lupa) ft(tl, lupa, { rotation: -6 }, { rotation: 0, duration: f(6), ease: E.move }, tF);
          tl.to(scan, { opacity: 0, duration: f(4), ease: E.exit }, T(tF));
          tl.set(res, { opacity: 1 }, T(tF));
          results.forEach((x, k) => ft(tl, x.r, { opacity: 0, y: -S(36) }, { opacity: 1, y: 0, duration: f(6), ease: E.enter }, tF + k * f(2)));
          gx.ev(ctx, "burst", tF);
          ft(tl, heroA.i, { yPercent: 115 }, { yPercent: 0, duration: f(8), ease: E.enter }, tF);
          gx.ev(ctx, "hero", tF);
          const tMa = Math.max(tF + f(8), C("a_mark", tF + f(8)));
          if (heroA.bar) { ft(tl, heroA.bar, { scaleX: 0 }, { scaleX: 1, duration: f(10), ease: E.move }, tMa); gx.ev(ctx, "mark", tMa); }
          // ── 3 · encontrado (en «la información»): borde oro, check que se dibuja; los demás se apagan
          const tFo = Math.max(tF + f(12), C("a_found", tF + 0.6));
          const r0 = results[0];
          ft(tl, r0.edge, { scaleY: 0 }, { scaleY: 1, duration: f(7), ease: E.enter }, tFo);
          ft(tl, r0.badge, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, tFo + f(2));
          ft(tl, r0.tick, { strokeDashoffset: 30 }, { strokeDashoffset: 0, duration: f(7), ease: E.move }, tFo + f(5));
          ft(tl, r0.r, { scale: 1 }, { scale: 1.035, duration: f(8), ease: E.enter }, tFo);
          ft(tl, results.slice(1).map((x) => x.r), { opacity: 1 }, { opacity: 0.4, duration: f(8), ease: E.enter }, tFo);
          gx.ev(ctx, "found", tFo);

          // ── 4 · relevo (en «ejecutar»): la búsqueda sube y se va, la lista entra desde abajo
          const tB = Math.max(tFo + f(10), C("b_in", tFo + 0.8));
          tl.to(a, { y: -S(90), opacity: 0, duration: f(7), ease: E.exit }, T(tB));
          tl.set(b, { opacity: 1 }, T(tB));
          ft(tl, card, { opacity: 0, y: S(70) }, { opacity: 1, y: 0, duration: f(10), ease: E.enter }, tB + f(2));
          tasks.forEach((x, k) => ft(tl, x.r, { opacity: 0, x: -S(24) }, { opacity: 1, x: 0, duration: f(7), ease: E.enter }, tB + f(5) + k * f(2)));
          if (gears) {
            ft(tl, gears, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(10), ease: E.pop }, tB + f(4));
            // engranajes que giran a golpes (45° cada 0,4 s): la máquina trabajando
            for (let k = 0, tg = tB + f(12); tg + 0.3 < t1 - f(6); k++, tg += 0.4) ft(tl, gears, { rotation: 45 * k }, { rotation: 45 * (k + 1), duration: 0.3, ease: E.move }, tg);
          }
          gx.ev(ctx, "swap", tB);
          // ── 5 · se ejecutan y se marcan SOLAS (en «tareas»), una detrás de otra
          const tR = Math.max(tB + f(14), C("b_run", tB + 0.45));
          const stepT = Math.max(f(6), Math.min(f(10), ((C("b_hero", tR + 1.0) - tR) || 0.9) / nRows));
          tasks.forEach((x, k) => {
            const tk = tR + k * stepT;
            ft(tl, x.prog, { scaleX: 0 }, { scaleX: 1, duration: stepT * 0.8, ease: E.move }, tk);
            ft(tl, x.box, { backgroundColor: "rgba(22,21,20,0)" }, { backgroundColor: "#161514", duration: f(4), ease: E.enter }, tk + stepT * 0.7);
            ft(tl, x.tick, { strokeDashoffset: 30 }, { strokeDashoffset: 0, duration: f(6), ease: E.move }, tk + stepT * 0.75);
            ft(tl, x.sk, { opacity: 1 }, { opacity: 0.5, duration: f(6), ease: E.enter }, tk + stepT * 0.8);
            ft(tl, x.prog, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.exit }, tk + stepT * 0.9);   // hecha: la barra se va
            gx.ev(ctx, "tick", tk + stepT * 0.75);
          });
          // ── 6 · el héroe de la escena 2 en su palabra, con el rotulador
          const tH = Math.max(tB + f(8), C("b_hero", tR + nRows * stepT));
          ft(tl, heroB.i, { yPercent: 115 }, { yPercent: 0, duration: f(8), ease: E.enter }, tH);
          gx.ev(ctx, "hero", tH);
          const tMb = Math.max(tH + f(8), C("b_mark", tH + f(8)));
          if (heroB.bar) { ft(tl, heroB.bar, { scaleX: 0 }, { scaleX: 1, duration: f(10), ease: E.move }, tMb); gx.ev(ctx, "mark", tMb); }
          gx.out(tl, props, t1, [a, b], { dur: f(5), ctx });
        },
      };
    },
  });
})(window.CK);
