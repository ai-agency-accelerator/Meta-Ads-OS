// viz.session_tree — un proyecto y sus conversaciones como ESQUEMA (no es la interfaz de un agente de código: carpeta, trazo de
// árbol y filas con icono). Dos modos sobre el mismo dibujo, para que la
//   lista de «uno de los proyectos» vuelva cuando el agente crea la conversación nueva:
//   build: la carpeta entra grande, se asienta como cabecera y cada fila cuelga del árbol en SU palabra; al final las
//          demás se apagan y la elegida se marca con su coletilla («Sin Terminar»).
//   grow:  nace una conversación suelta y grande; llega el árbol ya hecho; el agente (logo) se le pega; se enciende en
//          «generarla», vuela a su sitio en «colocarla», se traza su rama en «correcta» y en «fijarla» cae la chincheta
//          y sube a la primera fila. Arriba, los tres verbos se acumulan (las listas acaban juntas).
// grow + `recall`: el árbol ya es conocido, así que entra montado en el corte, sin título grande que
//          repita la burbuja anterior. La conversación nace suelta bajo el árbol, junto a su hueco, nunca encima de la
//          carpeta; `head` late en «proyecto»; el agente entra junto a la cabecera y un cable oro baja hasta ella.
// props: {mode, head:{asset, label}, rows:[{label, asset, cue?}], flag?:{row, text},
//         born?:{label, asset, idle_asset, agent, pin}, verbs?:[{text, cue}], top?, row_h?, icon?, px?, head_px?, canvas}
// cues: build: head, settle, r0…r4, dim, flag · grow: tree, agent, solid, place, ok, pin, glow (+ las de `verbs`)
// eventos: enter, head, row, dim, flag, born, tree, agent, light, fly, branch, pin, glow, verb, exit
(function (CK) {
  "use strict";
  const BASE = 260;
  CK.register("viz.session_tree", {
    mount(root, props, ctx) {
      const gx = CK.gx;
      const { f, ft, T, R } = gx;
      const E = gx.eases(ctx);
      const st = gx.stage(root, ctx, props, "vt");
      const A = st.A, bd = st.bd;
      const X = (x) => x - A.x, Y = (y) => y - A.y;
      const GROW = props.mode === "grow";
      const rowsIn = (props.rows || []).filter((r) => r && r.label);
      const iconS = Number(props.icon) || (GROW ? 86 : 116);
      const rowH = Number(props.row_h) || (GROW ? 104 : 136);
      const px = Number(props.px) || (GROW ? 52 : 60);
      const headS = Number(props.head_size) || (GROW ? 96 : 130);
      const headPx = Number(props.head_px) || (GROW ? 60 : 76);
      const trunkX = Number(props.trunk_x) || 130;       // x de lienzo del tronco del árbol
      const arm = Number(props.arm) || 40;
      const wrap = gx.el("div", "vt-wrap", A.node);
      // ── cabecera (carpeta + rótulo)
      const head = props.head || {};
      const hIc = gx.logo(wrap, ctx, head.asset, "vt-hic");
      Object.assign(hIc.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
      const hLw = gx.el("div", "vt-hlw", wrap);
      const hLm = gx.el("div", "vt-m", hLw);
      const hLi = gx.el("div", "vt-i", hLm, String(head.label || ""));
      hLm.style.fontSize = headPx + "px";
      gsap.set(hIc, { opacity: 0 }); gsap.set(hLi, { yPercent: 115, opacity: 0 });
      // ── filas
      const mkElbow = (cls) => {
        const s = gx.svg("svg", { class: "vt-el " + (cls || ""), width: arm + 8, height: rowH + 8, viewBox: `-4 ${-rowH - 4} ${arm + 8} ${rowH + 8}` }, wrap);
        const p = gx.svg("path", { d: `M 0 ${-rowH} V 0 H ${arm}` }, s);
        const L = rowH + arm;
        p.style.strokeDasharray = L + " " + L; p.style.strokeDashoffset = L;
        gsap.set(s, { opacity: 0 });
        return { s, p, L };
      };
      const rows = rowsIn.map((r) => {
        const el = mkElbow();
        const ic = gx.logo(wrap, ctx, r.asset, "vt-ic");
        Object.assign(ic.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
        const lw = gx.el("div", "vt-lw", wrap);
        const m = gx.el("div", "vt-m", lw);
        const li = gx.el("div", "vt-i", m, String(r.label));
        m.style.fontSize = px + "px";
        gsap.set(ic, { opacity: 0 }); gsap.set(li, { yPercent: 115, opacity: 0 }); gsap.set(lw, { opacity: 1 });
        return { r, el, ic, lw, m, li, y: 0 };
      });
      // ── coletilla de `flag`
      const fl = props.flag && props.flag.text ? (() => {
        const lw = gx.el("div", "vt-lw", wrap);
        const m = gx.el("div", "vt-m vt-flag", lw);
        const wr = gx.el("div", "vt-i", m);
        const sp = gx.el("span", "vt-mkw", wr);
        const bar = gx.el("span", "vt-mkb", sp);
        gx.el("span", "vt-mkt", sp, String(props.flag.text));
        gsap.set(bar, { scaleX: 0 }); gsap.set(wr, { yPercent: 115, opacity: 0 });
        return { lw, m, wr, bar };
      })() : null;
      // ── tarjeta de foco
      const hl = gx.el("div", "vt-hl", wrap);
      gsap.set(hl, { opacity: 0 });
      // ── la conversación que nace (grow)
      const bn = GROW && props.born ? (() => {
        const n = gx.el("div", "vt-bb", wrap);
        Object.assign(n.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
        const idle = gx.logo(n, ctx, props.born.idle_asset || props.born.asset, "vt-l");
        const gold = gx.logo(n, ctx, props.born.asset, "vt-l");
        const lw = gx.el("div", "vt-lw vt-blw", wrap);
        const m = gx.el("div", "vt-m", lw);
        const li = gx.el("div", "vt-i", m, String(props.born.label || ""));
        m.style.fontSize = px + "px";
        const agent = props.born.agent ? gx.logo(wrap, ctx, props.born.agent, "vt-ag") : null;
        const pin = props.born.pin ? gx.logo(wrap, ctx, props.born.pin, "vt-pin") : null;
        const el = mkElbow("vt-el-new");
        gsap.set([n, li].concat(agent ? [agent] : []).concat(pin ? [pin] : []), { opacity: 0 });
        gsap.set(gold, { opacity: 0 });
        gsap.set(li, { yPercent: 115 });
        return { n, idle, gold, lw, m, li, agent, pin, el };
      })() : null;
      // ── verbos de arriba
      const verbs = GROW ? (props.verbs || []).map((v) => {
        const lw = gx.el("div", "vt-vw", wrap);
        const m = gx.el("div", "vt-m vt-v", lw);
        const wr = gx.el("div", "vt-i", m);
        const sp = gx.el("span", "vt-mkw", wr);
        const bar = gx.el("span", "vt-mkb", sp);
        gx.el("span", "vt-mkt", sp, String(v.text));
        gsap.set(bar, { scaleX: 0 }); gsap.set(wr, { yPercent: 115, opacity: 0 });
        return { v, lw, m, wr, bar };
      }) : [];

      return {
        animate(tl, t0, t1, cues) {
          const C = (k, d) => gx.cue(cues, k, d);
          gx.ev(ctx, "enter", t0);
          gx.bgIn(tl, bd, t0, t1, 43, props);
          const rowX = trunkX + arm + iconS / 2;                  // centro del icono
          const lblX = trunkX + arm + iconS + Math.max(16, iconS * 0.2);   // arranque del rótulo
          // medidas con las fuentes ya cargadas (la «T»: bajo y=1000 el rótulo acaba en 888)
          const fitLbl = (m, inner, py, max) => {
            const room = (py + max * 0.65 > 1000 ? 888 : 1015) - lblX;
            const s = gx.fit(inner, { max, min: 48, width: room, lines: 1 });
            m.style.fontSize = s + "px"; inner.style.fontSize = "";
            return s;
          };
          // rótulos paralelos: todos al mismo cuerpo, el mayor que quepa en la fila más ancha
          const fitRows = (room) => {
            let sz = px;
            rows.forEach((r) => { sz = Math.min(sz, gx.fit(r.li, { max: px, min: 48, width: room, lines: 1 })); r.li.style.fontSize = ""; });
            rows.forEach((r) => { r.m.style.fontSize = sz + "px"; });
            return sz;
          };
          const setRow = (r, y) => { r.y = y; };
          const place = (r, y, o) => {          // estado inicial de una fila ya en su y
            setRow(r, y);
            const ss = iconS / BASE;
            gsap.set(r.ic, { x: R(X(rowX)), y: R(Y(y)), scale: ss });
            gsap.set(r.lw, { x: R(X(lblX)), y: R(Y(y)) });
            gsap.set(r.el.s, { x: R(X(trunkX) - 4), y: R(Y(y) - rowH - 4) });
            void o;
          };
          const toRow = (r, y, at, d) => {       // una fila baja o sube a otro hueco
            const ss = iconS / BASE;
            ft(tl, r.ic, { x: R(X(rowX)), y: R(Y(r.y)), scale: ss }, { x: R(X(rowX)), y: R(Y(y)), scale: ss, duration: d, ease: E.move }, at);
            ft(tl, r.lw, { x: R(X(lblX)), y: R(Y(r.y)) }, { x: R(X(lblX)), y: R(Y(y)), duration: d, ease: E.move }, at);
            ft(tl, r.el.s, { x: R(X(trunkX) - 4), y: R(Y(r.y) - rowH - 4) }, { x: R(X(trunkX) - 4), y: R(Y(y) - rowH - 4), duration: d, ease: E.move }, at);
            r.y = y;
          };
          if (!GROW) {
            // ════ build
            const H = headS + 34 + rows.length * rowH;
            const top = Number(props.top) || R(764 - H / 2);
            const hy = top + headS / 2, ry = (i) => top + headS + 34 + (i + 0.5) * rowH;
            const hx = trunkX, hlx = trunkX + headS / 2 + 26;
            rows.forEach((r, i) => { place(r, ry(i)); });
            fitRows(1015 - lblX);
            const bigS = Number(props.head_big) || 380, bigY = Number(props.head_big_y) || 610;
            const bigK = (Number(props.head_big_px) || 104) / headPx;
            hLw.style.left = "0"; hLw.style.top = "0";
            gsap.set(hLw, { x: 0, y: 0 });
            const hw = hLi.offsetWidth * bigK;
            const big = { x: R(X(540) - hw / 2), y: R(Y(bigY + bigS / 2 + 74)) };
            const hLwEnd = { x: R(X(hlx)), y: R(Y(hy)) };
            gsap.set(hLw, { x: big.x, y: big.y, scale: bigK });
            const tH = Math.max(t0 + f(1), C("head", t0 + f(1)));
            ft(tl, hIc, { x: R(X(540)), y: R(Y(bigY)), scale: (bigS / BASE) * 0.55, opacity: 0 }, { x: R(X(540)), y: R(Y(bigY)), scale: bigS / BASE, opacity: 1, duration: f(9), ease: E.pop }, tH);
            gx.maskIn(tl, hLi, tH + f(2), { frames: 8, from: 115 });
            gx.ev(ctx, "head", tH);
            const tS = Math.max(tH + f(10), C("settle", tH + 0.5));
            ft(tl, hIc, { x: R(X(540)), y: R(Y(bigY)), scale: bigS / BASE }, { x: R(X(hx)), y: R(Y(hy)), scale: headS / BASE, duration: f(11), ease: E.move }, tS);
            ft(tl, hLw, { x: big.x, y: big.y, scale: bigK }, { x: hLwEnd.x, y: hLwEnd.y, scale: 1, duration: f(11), ease: E.move }, tS);
            let tPrev = tS + f(8);
            rows.forEach((r, i) => {
              const at = Math.max(tPrev, C("r" + i, tPrev + 0.4));
              tl.set(r.el.s, { opacity: 1 }, T(at));
              ft(tl, r.el.p, { strokeDashoffset: r.el.L }, { strokeDashoffset: 0, duration: f(6), ease: E.move }, at);
              ft(tl, r.ic, { x: R(X(rowX)), y: R(Y(r.y)), scale: (iconS / BASE) * 0.5, opacity: 0 }, { x: R(X(rowX)), y: R(Y(r.y)), scale: iconS / BASE, opacity: 1, duration: f(8), ease: E.pop }, at + f(2));
              gx.maskIn(tl, r.li, at + f(3), { frames: 7, from: 115 });
              gx.ev(ctx, "row", at + f(3));   // el primer fotograma en que el icono ya se ve (a +2 f su opacidad es 0)
              tPrev = at + f(5);
            });
            // ── se apagan las demás y la elegida se destaca
            const fi = props.flag && Number.isInteger(props.flag.row) ? props.flag.row : rows.length - 1;
            const tD = C("dim", null);
            if (tD != null) {
              const others = rows.filter((_, i) => i !== fi);
              const t = others.reduce((a, r) => a.concat([r.ic, r.lw]), []);
              ft(tl, t, { opacity: 1 }, { opacity: 0.32, duration: f(8), ease: E.enter }, tD);
              gx.ev(ctx, "dim", tD);
            }
            const tF = C("flag", null);
            if (fl && tF != null) {
              const r = rows[fi], y = r.y, dy = R(px * 0.62);
              fitLbl(fl.m, fl.wr, y + dy, Number(props.flag.px) || 52);
              ft(tl, r.lw, { y: R(Y(y)) }, { y: R(Y(y - dy)), x: R(X(lblX)), duration: f(8), ease: E.move }, tF);
              gsap.set(fl.lw, { x: R(X(lblX)), y: R(Y(y + dy)) });
              gx.maskIn(tl, fl.wr, tF + f(2), { frames: 8, from: 115 });
              ft(tl, fl.bar, { scaleX: 0 }, { scaleX: 1, duration: f(9), ease: E.move }, tF + f(7));
              Object.assign(hl.style, { left: R(X(trunkX + arm - 16)) + "px", top: R(Y(y - rowH * 0.62)) + "px", width: R(888 - (trunkX + arm - 16)) + "px", height: R(rowH * 1.24) + "px" });
              ft(tl, hl, { opacity: 0, scale: 0.97 }, { opacity: 1, scale: 1, duration: f(8), ease: E.enter }, tF);
              ft(tl, r.ic, { scale: iconS / BASE }, { scale: (iconS / BASE) * 1.08, duration: f(8), ease: E.enter }, tF);
              gx.ev(ctx, "flag", tF);
            }
          } else if (props.recall) {
            // ════ grow + recall
            const b = bn, hy = Number(props.top) || 470, tT = t0 + f(1);
            const ry = (i) => hy + headS / 2 + 16 + (i + 0.5) * rowH;
            const hlx = trunkX + headS / 2 + 22;
            hLw.style.left = "0"; hLw.style.top = "0";
            rows.forEach((r, i) => { place(r, ry(i)); });
            const rowPx = fitRows(888 - lblX);
            // ── 0 · el árbol, montado en el corte; todo su texto entra con su máscara
            ft(tl, hIc, { x: R(X(trunkX)), y: R(Y(hy)), scale: (headS / BASE) * 0.6, opacity: 0 }, { x: R(X(trunkX)), y: R(Y(hy)), scale: headS / BASE, opacity: 1, duration: f(9), ease: E.pop }, tT);
            gsap.set(hLw, { x: R(X(hlx)), y: R(Y(hy)) });
            gx.maskIn(tl, hLi, tT + f(1), { frames: 8, from: 115 });
            gx.ev(ctx, "tree", tT + f(1));
            rows.forEach((r, i) => {
              const at = tT + f(2) + i * f(2);
              tl.set(r.el.s, { opacity: 1 }, T(at));
              ft(tl, r.el.p, { strokeDashoffset: r.el.L }, { strokeDashoffset: 0, duration: f(6), ease: E.move }, at);
              ft(tl, r.ic, { opacity: 0, scale: (iconS / BASE) * 0.6 }, { opacity: 1, scale: iconS / BASE, duration: f(8), ease: E.enter }, at);
              gx.maskIn(tl, r.li, at + f(1), { frames: 7, from: 115 });
            });
            // ── 1 · nace suelta bajo el árbol, junto a su hueco (el rótulo acaba en 884: la «T» bajo y=1000)
            const yN = ry(rows.length), cS = Number(props.card_icon) || 116, cG = 20;
            b.m.style.fontSize = rowPx + "px";
            const lwW = b.li.offsetWidth;
            const k = Math.min((Number(props.card_px) || 58) / rowPx, (884 - 150 - cS - cG) / lwW);
            const cW = cS + cG + lwW * k, cL = Math.min(540 - cW / 2, 884 - cW);
            const cY = Number(props.card_y) || R(yN + 76);
            const cIc = { x: R(X(cL + cS / 2)), y: R(Y(cY)) }, cLb = { x: R(X(cL + cS + cG)), y: R(Y(cY)) };
            const tBorn = Math.max(tT + f(10), C("born", tT + 1));
            gsap.set(b.lw, { x: cLb.x, y: cLb.y, scale: k });
            ft(tl, b.n, { x: cIc.x, y: cIc.y, scale: (cS / BASE) * 0.5, opacity: 0 }, { x: cIc.x, y: cIc.y, scale: cS / BASE, opacity: 1, duration: f(9), ease: E.pop }, tBorn);
            gx.maskIn(tl, b.li, tBorn + f(2), { frames: 8, from: 115 });
            gx.ev(ctx, "born", tBorn + f(1));
            // ── 2 · «proyecto»: la carpeta late
            const tH = C("proj", null);
            if (tH != null && tH > tBorn) {
              ft(tl, hIc, { scale: headS / BASE }, { scale: (headS / BASE) * 1.22, duration: f(5), ease: E.enter }, tH);
              ft(tl, hIc, { scale: (headS / BASE) * 1.22 }, { scale: headS / BASE, duration: f(8), ease: E.move }, tH + f(5));
              gx.ev(ctx, "head", tH + f(1));
            }
            // ── 3 · el agente entra junto a la cabecera y un cable oro baja hasta la conversación
            const agX = Number(props.agent_x) || 930, agS = Number(props.agent_size) || 130;
            const tA = Math.max(tBorn + f(10), C("agent", tBorn + 1));
            if (b.agent) {
              Object.assign(b.agent.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
              ft(tl, b.agent, { x: R(X(agX)), y: R(Y(hy) - 90), scale: (agS / BASE) * 0.5, opacity: 0 }, { x: R(X(agX)), y: R(Y(hy)), scale: agS / BASE, opacity: 1, duration: f(9), ease: E.pop }, tA);
              gx.ev(ctx, "agent", tA + f(1));
            }
            const tS = Math.max(tA + f(14), C("solid", tA + 0.8));
            const tW = Math.min(tS - f(8), Math.max(tA + f(6), C("wire", tA + f(8))));
            const wSvg = gx.svg("svg", { class: "vt-wires", width: A.w, height: A.h + 300, viewBox: `0 0 ${A.w} ${A.h + 300}` }, wrap);
            const pts = [[X(agX), Y(hy) + agS * 0.56], [X(agX), Y(cY)], [X(cL + cW + 12), Y(cY)]];
            const w = gx.wire(wSvg, pts, { w: 5, wo: 10 });
            gx.drawWire(tl, w, tW, Math.min(f(9), tS - tW));
            gx.ev(ctx, "branch", tW + f(1));
            const dot = gx.pulseDot(wrap, 22);
            gx.pulse(tl, dot, pts, Math.max(tW + f(2), tS - f(10)), Math.min(f(10), tS - tW - f(2)));
            // ── 4 · «generarla»: se enciende
            ft(tl, b.gold, { opacity: 0 }, { opacity: 1, duration: f(7), ease: E.enter }, tS);
            gx.ev(ctx, "light", tS + f(1));
            // ── 5 · «colocarla»: el cable se va y ella sube a su hueco
            const tP = Math.max(tS + f(8), C("place", tS + 0.7)), dP = f(14);
            const nIc = { x: R(X(rowX)), y: R(Y(yN)) }, nLb = { x: R(X(lblX)), y: R(Y(yN)) };
            ft(tl, [w.ol, w.gd], { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.exit }, tP);
            ft(tl, b.n, { x: cIc.x, y: cIc.y, scale: cS / BASE }, { x: nIc.x, y: nIc.y, scale: iconS / BASE, duration: dP, ease: E.move }, tP);
            ft(tl, b.lw, { x: cLb.x, y: cLb.y, scale: k }, { x: nLb.x, y: nLb.y, scale: 1, duration: dP, ease: E.move }, tP);
            gx.ev(ctx, "fly", tP);
            // ── 6 · «estructura»: su rama se traza; «correcta»: un destello de la tarjeta la da por buena
            const tO = Math.max(tP + dP - f(2), C("ok", tP + dP));
            gsap.set(b.el.s, { x: R(X(trunkX) - 4), y: R(Y(yN) - rowH - 4) });
            tl.set(b.el.s, { opacity: 1 }, T(tO));
            ft(tl, b.el.p, { strokeDashoffset: b.el.L }, { strokeDashoffset: 0, duration: f(8), ease: E.move }, tO);
            gx.ev(ctx, "branch", tO);
            const hlW = R(Math.min(A.w - X(trunkX + arm - 14), lblX - trunkX + b.li.offsetWidth + 10));
            const tR = C("right", null);
            const tPin = Math.max(tO + f(10), C("pin", tO + 1));
            if (tR != null && tR > tO + f(4) && tR < tPin - f(14)) {
              const fl2 = gx.el("div", "vt-hl", wrap);
              Object.assign(fl2.style, { left: R(X(trunkX + arm - 14)) + "px", top: R(Y(yN) - rowH * 0.5 - 4) + "px", width: hlW + "px", height: R(rowH + 8) + "px" });
              gsap.set(fl2, { opacity: 0 });
              ft(tl, fl2, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, tR);
              ft(tl, fl2, { opacity: 1 }, { opacity: 0, duration: f(8), ease: E.exit }, tR + f(12));
              gx.ev(ctx, "glow", tR + f(1));
            }
            // ── 7 · «fijarla»: cae la chincheta y sube a la primera fila
            const y0Row = ry(0);
            if (b.pin) {
              const ps = Number(props.pin_size) || 92;
              Object.assign(b.pin.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
              const px0 = R(nIc.x - iconS * 0.46), py0 = R(nIc.y - iconS * 0.46);
              ft(tl, b.pin, { x: px0 - 40, y: py0 - 260, scale: (ps / BASE) * 1.6, opacity: 0, rotation: -88 }, { x: px0, y: py0, scale: ps / BASE, opacity: 1, rotation: -64, duration: f(9), ease: E.enter }, tPin);
              gx.ev(ctx, "pin", tPin + f(7));
              const tUp = tPin + f(12), dU = f(14);
              ft(tl, b.pin, { x: px0, y: py0 }, { x: px0, y: R(Y(y0Row) - iconS * 0.46), duration: dU, ease: E.move }, tUp);
              ft(tl, b.n, { x: nIc.x, y: nIc.y }, { x: nIc.x, y: R(Y(y0Row)), duration: dU, ease: E.move }, tUp);
              ft(tl, b.lw, { x: nLb.x, y: nLb.y }, { x: nLb.x, y: R(Y(y0Row)), duration: dU, ease: E.move }, tUp);
              ft(tl, b.el.s, { y: R(Y(yN) - rowH - 4) }, { y: R(Y(y0Row) - rowH - 4), duration: dU, ease: E.move }, tUp);
              rows.forEach((r, i) => toRow(r, ry(i + 1), tUp + i * f(0.5), dU));
              // ── 8 · «importantes»: la tarjeta de foco la rodea
              Object.assign(hl.style, { left: R(X(trunkX + arm - 14)) + "px", top: R(Y(y0Row) - rowH * 0.5 - 4) + "px", width: hlW + "px", height: R(rowH + 8) + "px" });
              const tG = Math.max(tUp + dU - f(2), C("glow", tUp + dU));
              ft(tl, hl, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: f(8), ease: E.enter }, tG);
              ft(tl, rows.reduce((a, r) => a.concat([r.ic, r.lw]), []), { opacity: 1 }, { opacity: 0.38, duration: f(8), ease: E.enter }, tG);
              gx.ev(ctx, "glow", tG + f(1));
            }
          } else {
            // ════ grow
            const tree0 = Number(props.top) || 590;       // y del centro de la cabecera mientras la tarjeta espera arriba
            const tree1 = Number(props.top_after) || 440; // y al recolocarse sin la tarjeta
            const slots = rows.length + 1;                // las filas + la nueva
            const ry = (top, i) => top + headS / 2 + 16 + (i + 0.5) * rowH;
            const hlx = trunkX + headS / 2 + 22;
            hLw.style.left = "0"; hLw.style.top = "0";
            rows.forEach((r, i) => { place(r, ry(tree0, i)); });
            const rowPx = fitRows(888 - lblX);
            const tBorn = t0 + f(1);
            const bigY = Number(props.born_big_y) || 600, bigS = Number(props.born_big) || 320, cardY = Number(props.card_y) || 468, cardS = Number(props.card_icon) || 124;
            const cardPx = Number(props.card_px) || 66, bigPx = Number(props.born_big_px) || 88;
            // ── 0 · nace suelta y grande
            const b = bn;
            b.m.style.fontSize = rowPx + "px";
            const lwW = b.li.offsetWidth;
            const kBig = bigPx / rowPx, kCard = cardPx / rowPx;
            const bigLbl = { x: R(X(540) - (lwW * kBig) / 2), y: R(Y(bigY + bigS / 2 + 76)) };
            const cardW = cardS + 24 + lwW * kCard, cardL = 540 - cardW / 2;
            const cardIc = { x: R(X(cardL + cardS / 2)), y: R(Y(cardY)) }, cardLbl = { x: R(X(cardL + cardS + 24)), y: R(Y(cardY)) };
            gsap.set(b.lw, { x: bigLbl.x, y: bigLbl.y, scale: kBig });
            ft(tl, b.n, { x: R(X(540)), y: R(Y(bigY)), scale: (bigS / BASE) * 0.5, opacity: 0 }, { x: R(X(540)), y: R(Y(bigY)), scale: bigS / BASE, opacity: 1, duration: f(9), ease: E.pop }, tBorn);
            gx.maskIn(tl, b.li, tBorn + f(2), { frames: 8, from: 115 });
            gx.ev(ctx, "born", tBorn);
            // ── 1 · llega el árbol y ella sube a esperar
            const tT = Math.max(tBorn + f(10), C("tree", tBorn + 1.2));
            const dT = f(12);
            ft(tl, b.n, { x: R(X(540)), y: R(Y(bigY)), scale: bigS / BASE }, { x: cardIc.x, y: cardIc.y, scale: cardS / BASE, duration: dT, ease: E.move }, tT);
            ft(tl, b.lw, { x: bigLbl.x, y: bigLbl.y, scale: kBig }, { x: cardLbl.x, y: cardLbl.y, scale: kCard, duration: dT, ease: E.move }, tT);
            const hy0 = tree0, rise = 70;
            ft(tl, hIc, { x: R(X(trunkX)), y: R(Y(hy0 + rise)), scale: (headS / BASE) * 0.6, opacity: 0 }, { x: R(X(trunkX)), y: R(Y(hy0)), scale: headS / BASE, opacity: 1, duration: f(10), ease: E.pop }, tT + f(2));
            gsap.set(hLw, { x: R(X(hlx)), y: R(Y(hy0)) });
            gx.maskIn(tl, hLi, tT + f(3), { frames: 8, from: 115 });
            gx.ev(ctx, "tree", tT);
            rows.forEach((r, i) => {
              const at = tT + f(4) + i * f(2);
              tl.set(r.el.s, { opacity: 1 }, T(at));
              ft(tl, r.el.p, { strokeDashoffset: r.el.L }, { strokeDashoffset: 0, duration: f(6), ease: E.move }, at);
              ft(tl, r.ic, { opacity: 0, scale: (iconS / BASE) * 0.6 }, { opacity: 1, scale: iconS / BASE, duration: f(8), ease: E.enter }, at);
              gx.maskIn(tl, r.li, at + f(1), { frames: 7, from: 115 });
            });
            // ── 2 · el agente se le pega
            const tA = Math.max(tT + f(14), C("agent", tT + 1));
            const agS = Number(props.agent_size) || 92;
            if (b.agent) {
              Object.assign(b.agent.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
              const ax = R(cardIc.x + cardS * 0.42), ay = R(cardIc.y - cardS * 0.42);
              ft(tl, b.agent, { x: ax, y: ay - 90, scale: (agS / BASE) * 0.5, opacity: 0 }, { x: ax, y: ay, scale: agS / BASE, opacity: 1, duration: f(9), ease: E.pop }, tA);
              gx.ev(ctx, "agent", tA);
            }
            // ── 3 · se enciende en «generarla»
            const tS = Math.max(tA + f(6), C("solid", tA + 0.6));
            ft(tl, b.gold, { opacity: 0 }, { opacity: 1, duration: f(7), ease: E.enter }, tS);
            gx.ev(ctx, "light", tS + f(1));
            // ── 4 · vuela a su sitio y todo sube a llenar el hueco
            const tP = Math.max(tS + f(8), C("place", tS + 0.7));
            const dP = f(14);
            const hy1 = tree1;
            ft(tl, hIc, { y: R(Y(hy0)), x: R(X(trunkX)), scale: headS / BASE }, { y: R(Y(hy1)), x: R(X(trunkX)), scale: headS / BASE, duration: dP, ease: E.move }, tP);
            ft(tl, hLw, { y: R(Y(hy0)), x: R(X(hlx)) }, { y: R(Y(hy1)), x: R(X(hlx)), duration: dP, ease: E.move }, tP);
            rows.forEach((r, i) => toRow(r, ry(hy1, i), tP, dP));
            const newI = rows.length, yN = ry(hy1, newI);
            const nIc = { x: R(X(rowX)), y: R(Y(yN)) }, nLb = { x: R(X(lblX)), y: R(Y(yN)) };
            ft(tl, b.n, { x: cardIc.x, y: cardIc.y, scale: cardS / BASE }, { x: nIc.x, y: nIc.y, scale: iconS / BASE, duration: dP, ease: E.move }, tP);
            ft(tl, b.lw, { x: cardLbl.x, y: cardLbl.y, scale: kCard }, { x: nLb.x, y: nLb.y, scale: 1, duration: dP, ease: E.move }, tP);
            if (b.agent) {
              const ax = R(cardIc.x + cardS * 0.42), ay = R(cardIc.y - cardS * 0.42);
              const kA = 0.62 * agS / BASE;
              ft(tl, b.agent, { x: ax, y: ay, scale: agS / BASE }, { x: R(nIc.x + iconS * 0.42), y: R(nIc.y - iconS * 0.42), scale: kA, duration: dP, ease: E.move }, tP);
            }
            gx.ev(ctx, "fly", tP);
            // ── 5 · su rama se traza
            const tO = Math.max(tP + dP - f(2), C("ok", tP + dP));
            gsap.set(b.el.s, { x: R(X(trunkX) - 4), y: R(Y(yN) - rowH - 4) });
            tl.set(b.el.s, { opacity: 1 }, T(tO));
            ft(tl, b.el.p, { strokeDashoffset: b.el.L }, { strokeDashoffset: 0, duration: f(8), ease: E.move }, tO);
            gx.ev(ctx, "branch", tO);
            // ── 6 · en «fijarla» cae la chincheta y sube a la primera fila
            const tPin = Math.max(tO + f(10), C("pin", tO + 1));
            const y0Row = ry(hy1, 0);
            if (b.pin) {
              const ps = Number(props.pin_size) || 92;
              Object.assign(b.pin.style, { width: BASE + "px", height: BASE + "px", left: -BASE / 2 + "px", top: -BASE / 2 + "px" });
              const px0 = R(nIc.x - iconS * 0.46), py0 = R(nIc.y - iconS * 0.46);
              ft(tl, b.pin, { x: px0 - 40, y: py0 - 260, scale: (ps / BASE) * 1.6, opacity: 0, rotation: -88 }, { x: px0, y: py0, scale: ps / BASE, opacity: 1, rotation: -64, duration: f(9), ease: E.enter }, tPin);
              gx.ev(ctx, "pin", tPin + f(7));
              const tUp = tPin + f(12), dU = f(14);
              ft(tl, b.pin, { x: px0, y: py0 }, { x: px0, y: R(Y(y0Row) - iconS * 0.46), duration: dU, ease: E.move }, tUp);
              ft(tl, b.n, { x: nIc.x, y: nIc.y }, { x: nIc.x, y: R(Y(y0Row)), duration: dU, ease: E.move }, tUp);
              ft(tl, b.lw, { x: nLb.x, y: nLb.y }, { x: nLb.x, y: R(Y(y0Row)), duration: dU, ease: E.move }, tUp);
              if (b.agent) ft(tl, b.agent, { x: R(nIc.x + iconS * 0.42), y: R(nIc.y - iconS * 0.42) }, { x: R(nIc.x + iconS * 0.42), y: R(Y(y0Row) - iconS * 0.42), duration: dU, ease: E.move }, tUp);
              ft(tl, b.el.s, { y: R(Y(yN) - rowH - 4) }, { y: R(Y(y0Row) - rowH - 4), duration: dU, ease: E.move }, tUp);
              rows.forEach((r, i) => toRow(r, ry(hy1, i + 1), tUp + i * f(0.5), dU));
              // ── 7 · la tarjeta de foco la rodea
              Object.assign(hl.style, { left: R(X(trunkX + arm - 14)) + "px", top: R(Y(y0Row) - rowH * 0.5 - 4) + "px", width: R(Math.min(A.w - X(trunkX + arm - 14), lblX - trunkX + b.li.offsetWidth + 10)) + "px", height: R(rowH + 8) + "px" });
              const tG = Math.max(tUp + dU - f(2), C("glow", tUp + dU));
              ft(tl, hl, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: f(8), ease: E.enter }, tG);
              const dimT = rows.reduce((a, r) => a.concat([r.ic, r.lw]), []);
              ft(tl, dimT, { opacity: 1 }, { opacity: 0.38, duration: f(8), ease: E.enter }, tG);
              gx.ev(ctx, "glow", tG + f(1));
            }
            void slots;
          }
          if (GROW) {
            // ── verbos arriba: se acumulan, cada uno en su palabra, con el rotulador
            const vY = Number(props.verbs_y) || 322, vPx = Number(props.verbs_px) || 56, vGap = 34;
            verbs.forEach((v) => { v.m.style.fontSize = vPx + "px"; });
            const widths = verbs.map((v) => v.wr.offsetWidth);
            const tot = widths.reduce((a, w) => a + w, 0) + vGap * (verbs.length - 1);
            let xv = 540 - tot / 2, tvPrev = t0;
            verbs.forEach((v, i) => {
              gsap.set(v.lw, { x: R(X(xv)), y: R(Y(vY)) });
              xv += widths[i] + vGap;
              const at = Math.max(tvPrev + f(6), C(v.v.cue, tvPrev + 0.6));
              gx.maskIn(tl, v.wr, at, { frames: 8, from: 115 });
              ft(tl, v.bar, { scaleX: 0 }, { scaleX: 1, duration: f(9), ease: E.move }, at + f(5));
              gx.ev(ctx, "verb", at);
              tvPrev = at;
            });
          }
          gx.out(tl, props, t1, [wrap], { dur: f(5), ctx });
        },
      };
    },
  });
})(window.CK);
