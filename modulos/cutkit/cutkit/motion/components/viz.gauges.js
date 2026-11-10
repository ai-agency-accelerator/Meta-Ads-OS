// viz.gauges — «cuánto gastamos y lo cerca que estamos de los límites»: título con su icono del kit, una línea debajo y
//   2–3 MEDIDORES semicirculares (instrumento: pista, marcas, aguja con eje, tope de límite) que se dibujan, se llenan
//   en SU palabra y siguen vivos (la aguja tiembla un poco al leer). Sin cifras ni porcentajes: el nivel es la imagen de
//   «cerca o lejos del límite» (cuanto más lleno, más cálido). Todo texto entra animado (máscara que sube).
// props: {title, sub?, icon? (asset del kit), gauges:[{label, level 0–1, cue?}] (2–3), canvas, anchor?}
// opcionales y sin efecto si no se dan:
//   hero? (asset del kit: el objeto GRANDE y centrado ENCIMA del título, ya en el corte, en vez del icono pegado al
//   título), hero_size? (px, 220; 160–320), label_fit? (rótulos medidos de verdad: al mayor cuerpo ≤ 58 px·s que quepa
//   en su columna, nunca por debajo de label_min (48) y con la caja ajustada al texto, no a toda la columna)
// opcionales y sin efecto si no se dan: span_w? (px: la fila de medidores ocupa solo ese ancho,
//   centrada —696 = el ancho seguro bajo y=1000— y el radio se ajusta para que no se toquen), quick? (sin draw_each: las
//   pistas se dibujan CON el título y cada medidor se llena en SU cue con 4–6 f de margen, no ~1,2 s después del título)
// limit? (false = sin tope de límite ni evento `limit`; el nivel puede llegar a 1)
// fill_ease? / gauges[].ease? ("move" por defecto | "enter": la aguja gira visible desde el 1.er f)
// opcionales y sin efecto si no se dan: gauges[].brand (asset) o
//   gauges[].brand_text: la marca DENTRO del medidor desde que se dibuja su pista; label_hide (true: sin rótulo debajo);
//   titles [{text, cue}]: el título se releva en esas cues; jump_marker (true: una barra oro bajo el medidor en curso que
//   salta al siguiente cuando este llega a su nivel)
// cues: title, sub, gauges (las pistas se dibujan), limits (topes), g0…g2 (cada medidor se llena y su rótulo sube)
// eventos: enter, title, sub, draw, limit, fill, exit
(function (CK) {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  // `zoom` {k, from:[x,y], to:[x,y]} (px del lienzo), opcional: a
  //   pantalla completa, el gráfico ENTERO se escala ×k alrededor de `from` y ese punto va a `to` (envoltorio con
  //   translate + scale; el ítem, sus medidas y sus tiempos no cambian). Se aplica AL FINAL de animate, cuando ya se ha
  //   medido todo (los ajustes de texto miden sin escala). Quien la usa comprueba la «T» de la zona segura con la caja
  //   escalada. Sin la prop, nada cambia
  function zoomWrap(A, props, api) {
    const z = props && props.zoom;
    if (!z || !(Number(z.k) > 0) || !Array.isArray(z.from) || !Array.isArray(z.to) || !A || !A.node) return api;
    const an = api.animate;
    api.animate = function () {
      const r = an.apply(this, arguments);
      const k = Math.max(0.5, Math.min(2.5, Number(z.k))), o = A.origin || { x: 0, y: 0 };
      if (A.node.parentNode && A.node.parentNode.classList && A.node.parentNode.classList.contains("gx-zoom")) return r;   // ya envuelto
      const zw = document.createElement("div");
      zw.className = "gx-zoom";
      zw.style.cssText = "position:absolute;left:0;top:0;width:0;height:0;overflow:visible;transform-origin:0 0";
      const tx = (Number(z.to[0]) - o.x) - k * (Number(z.from[0]) - o.x), ty = (Number(z.to[1]) - o.y) - k * (Number(z.from[1]) - o.y);
      zw.style.transform = "translate(" + tx.toFixed(2) + "px," + ty.toFixed(2) + "px) scale(" + k + ")";
      if (A.node.style.zIndex) zw.style.zIndex = A.node.style.zIndex;
      A.node.parentNode.insertBefore(zw, A.node);
      zw.appendChild(A.node);
      return r;
    };
    return api;
  }
  CK.register("viz.gauges", {
    mount(root, props, ctx) {
      const gx = CK.gx, gxx = CK.gxx;
      const { f, ft, T, R } = gx;
      const E = gx.eases(ctx);
      const gauges = (props.gauges || []).filter((g) => g && g.label).slice(0, 3);
      if (gauges.length < 1) throw new Error("viz.gauges: al menos un medidor {label, level}");
      const st = gx.stage(root, ctx, props, "vg");
      const A = st.A, bd = st.bd;
      const n = gauges.length;
      // geometría base (escala s para que el bloque quepa en el área)
      const sw0 = n === 3 ? 26 : 30;
      const spanW = Number(props.span_w) > 0 ? Math.min(A.w, Math.max(300, Number(props.span_w))) : null;
      // `radius` (px): radio del medidor (168 con 1–2, 128 con 3); p. ej. 290 = un medidor de ~610 px
      let r0 = Number(props.radius) > 0 ? Math.max(80, Math.min(320, Number(props.radius))) : (n === 3 ? 128 : 168);
      // `column: true` (2–3 medidores): uno DEBAJO de otro, centrados y
      //   del mismo radio (`radius`), en vez de en fila: a pantalla completa crecen en alto (en fila los limita el ancho de la
      //   «T», 696 px bajo y=1000). `span_w` no se usa. Sin la prop, la fila de siempre. (Se llamaba `stack`: chocaba con el
      // `stack` de la compilación de los relevos, compile.py)
      // `column_gap` (px, 16–120): con `column`, hueco entre un medidor
      //   (con su rótulo) y el de debajo (28 por defecto): el rótulo queda más cerca de SU medidor que del siguiente
      const STACK = props.column === true && n > 1, gapS = STACK && Number(props.column_gap) > 0 ? Math.max(16, Math.min(120, Number(props.column_gap))) : 28;
      if (spanW && !STACK) r0 = Math.max(80, Math.min(r0, Math.floor((spanW / n - 48 - sw0) / 2)));   // `span_w`: radio que cabe
      const base = { titleH: 124, gap1: 8, subH: props.sub ? 58 : 0, gap2: 46, gH: r0 + sw0 / 2 + 26, gap3: 22, labH: 64 };
      const rowH0 = base.gH + base.gap3 + base.labH;
      // `hero`: el objeto encima del título suma su alto (+28 de aire) al bloque; sin `hero`, 0
      const heroId = typeof props.hero === "string" && props.hero ? props.hero : null;
      const heroS0 = heroId ? Math.max(160, Math.min(320, Number(props.hero_size) || 220)) : 0;
      const heroH = heroId ? heroS0 + 28 : 0;
      const H0 = heroH + base.titleH + base.gap1 + base.subH + base.gap2 + (STACK ? n * rowH0 + (n - 1) * gapS : rowH0);
      const s = Math.max(0.7, Math.min(1.12, (A.h * 0.94) / H0, A.w / 950));
      A.node.style.setProperty("--s", s);
      const S = (v) => R(v * s);
      // `limit: false`: sin tope de límite (ni su evento `limit`) y el
      //   nivel puede llegar a 1 (arco entero: sin el muñón gris de pista con la marca al final). Sin la prop, nada cambia
      const NOLIM = props.limit === false;
      const sw = S(sw0), r = spanW && !STACK ? Math.max(40, Math.min(S(r0), R((spanW / n - S(48) - sw) / 2))) : S(r0);
      const wrap = gx.el("div", "vg-wrap", A.node);
      const blockH = S(H0);
      const anc = typeof props.anchor === "number" && isFinite(props.anchor) ? props.anchor * (ctx.H || 1920) - A.y : null;
      const y0 = anc != null ? R(anc - blockH / 2) : R(Math.max(0, (A.h - blockH) / 2));

      // ── título (icono del kit + texto con máscara) y línea de debajo
      const hero = heroId ? gx.logo(wrap, ctx, heroId, "vg-hero") : null;
      if (hero) Object.assign(hero.style, { left: R((A.w - S(heroS0)) / 2) + "px", top: y0 + "px", width: S(heroS0) + "px", height: S(heroS0) + "px" });
      const head = gx.el("div", "vg-head", wrap);
      Object.assign(head.style, { top: (y0 + S(heroH)) + "px", height: S(base.titleH) + "px" });
      const icon = props.icon ? gx.logo(head, ctx, props.icon, "vg-icon") : null;
      if (icon) Object.assign(icon.style, { width: S(112) + "px", height: S(112) + "px" });
      const title = gxx.maskLine(head, "vg-title", String(props.title || ""));
      const relays = (Array.isArray(props.titles) ? props.titles : []).filter((t) => t && t.text).map((t) => {
        const h = gx.el("div", "vg-head", wrap);
        Object.assign(h.style, { top: head.style.top, height: head.style.height });
        return { t, l: gxx.maskLine(h, "vg-title", String(t.text)) };
      });
      const yS = y0 + S(heroH + base.titleH + base.gap1);
      const sub = props.sub ? gxx.maskLine(wrap, "vg-sub", String(props.sub)) : null;
      if (sub) Object.assign(sub.m.style, { top: yS + "px" });

      // ── medidores
      const yG = y0 + S(heroH + base.titleH + base.gap1 + base.subH + base.gap2);
      const cyG0 = yG + r + sw / 2;                                  // centro (eje) de cada semicírculo (el primero, con `column`)
      const span = STACK ? A.w : (spanW || A.w) / n, ox = spanW && !STACK ? (A.w - spanW) / 2 : 0;
      const svg = document.createElementNS(NS, "svg");
      svg.setAttribute("class", "vg-svg"); svg.setAttribute("width", A.w); svg.setAttribute("height", A.h + 400);
      wrap.appendChild(svg);
      const defs = document.createElementNS(NS, "defs"); svg.appendChild(defs);
      const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); (parent || svg).appendChild(e); return e; };
      const L = Math.PI * r;
      const G = gauges.map((g, i) => {
        const cx = STACK ? R(A.w / 2) : R(ox + span * (i + 0.5));
        const cyG = STACK ? R(cyG0 + i * S(rowH0 + gapS)) : cyG0;   // `column`: cada medidor en su fila
        const gid = "vgg" + (ctx.item && ctx.item.id ? String(ctx.item.id).replace(/\W/g, "") : "x") + i;
        const lg = mk("linearGradient", { id: gid, x1: cx - r, y1: 0, x2: cx + r, y2: 0, gradientUnits: "userSpaceOnUse" }, defs);
        // `ramp: "gold"` = rampa en el oro del kit (sin naranja-rojo);
        //   sin la prop, la cálida de siempre
        const RAMP = props.ramp === "gold" ? ["#FBE38E", "#FECA1A", "#D9A514"] : ["#F2C230", "#F0A23A", "#E0652F"];
        mk("stop", { offset: "0%", "stop-color": RAMP[0] }, lg);
        mk("stop", { offset: "62%", "stop-color": RAMP[1] }, lg);
        mk("stop", { offset: "100%", "stop-color": RAMP[2] }, lg);
        const d = `M ${cx - r} ${cyG} A ${r} ${r} 0 0 1 ${cx + r} ${cyG}`;
        const grp = mk("g", { class: "vg-g" });
        const track = mk("path", { d, class: "vg-track", "stroke-width": sw }, grp);
        const fill = mk("path", { d, class: "vg-fill", "stroke-width": sw, stroke: `url(#${gid})` }, grp);
        [track, fill].forEach((p) => { p.style.strokeDasharray = `${L} ${L + 4}`; p.style.strokeDashoffset = String(L + 2); });
        // marcas del instrumento (dentro del arco)
        const ticks = [];
        for (let k = 0; k <= 10; k++) {
          const a = Math.PI - (k / 10) * Math.PI, big = k % 5 === 0;
          const r1 = r - sw / 2 - S(big ? 30 : 20), r2 = r - sw / 2 - S(8);
          ticks.push(mk("line", { x1: R(cx + Math.cos(a) * r1), y1: R(cyG - Math.sin(a) * r1), x2: R(cx + Math.cos(a) * r2), y2: R(cyG - Math.sin(a) * r2), class: "vg-tick" + (big ? " vg-tick-big" : ""), "stroke-width": S(big ? 5 : 3) }, grp));
        }
        // tope del límite (al final de la pista)
        const lim = mk("line", { x1: cx + r - sw / 2 - S(10), y1: cyG + S(2), x2: cx + r + sw / 2 + S(10), y2: cyG + S(2), class: "vg-limit", "stroke-width": S(8) }, grp);
        // aguja (apunta a las 12 en reposo; se gira con svgOrigin en el eje) y eje
        const nd = mk("g", { class: "vg-needle" }, grp);
        mk("line", { x1: cx, y1: cyG, x2: cx, y2: cyG - (r - sw / 2 - S(36)), "stroke-width": S(9), class: "vg-needle-l" }, nd);
        const hub = mk("circle", { cx, cy: cyG, r: S(15), class: "vg-hub" }, grp);
        // rótulo debajo (texto con máscara)
        const lab = gxx.maskLine(wrap, "vg-label", String(g.label));
        const lw = R(span - S(48));    // caja del rótulo dentro de la zona segura (no hasta el borde del área)
        Object.assign(lab.m.style, { left: R(cx - lw / 2) + "px", width: lw + "px", top: (cyG + S(base.gap3 + 16)) + "px" });
        const level = Math.max(0.04, Math.min(NOLIM ? 1 : 0.98, Number(g.level) || 0.5));
        if (props.label_hide === true) lab.m.style.visibility = "hidden";
        // la marca dentro del medidor, debajo de la aguja (antes del svg en el DOM)
        let brand = null, brandT = null;
        if (g.brand) {
          brand = gx.logo(wrap, ctx, g.brand, "vg-brand");
          const bs = R(r * 0.62);
          Object.assign(brand.style, { position: "absolute", left: R(cx - bs / 2) + "px", top: R(cyG - r * 0.52 - bs / 2) + "px", width: bs + "px", height: bs + "px" });
          wrap.insertBefore(brand, svg);
          gsap.set(brand, { opacity: 0 });
        } else if (g.brand_text) {
          brandT = gxx.maskLine(wrap, "vg-label", String(g.brand_text));
          const bw = R(r * 1.5), bp = Math.max(52, S(52));
          Object.assign(brandT.m.style, { left: R(cx - bw / 2) + "px", width: bw + "px", top: R(cyG - r * 0.4 - bp * 0.62) + "px", fontSize: bp + "px", fontWeight: 900 });
          wrap.insertBefore(brandT.m, svg);
        }
        return { g, i, cx, cy: cyG, track, fill, ticks, lim, nd, hub, lab, level, brand, brandT };
      });
      G.forEach((x) => gsap.set(x.nd, { svgOrigin: `${x.cx} ${x.cy}`, rotation: -90, opacity: 0 }));
      gsap.set(G.flatMap((x) => x.ticks.concat([x.lim, x.hub])), { opacity: 0 });
      gsap.set(G.map((x) => x.lim), { scaleX: 0.2, transformOrigin: "50% 50%" });
      if (icon) gsap.set(icon, { opacity: 0 });
      if (hero) gsap.set(hero, { opacity: 0 });
      gsap.set(wrap, { opacity: 1 });

      return zoomWrap(A, props, {
        animate(tl, t0, t1, cues) {
          const C = (k, d) => gx.cue(cues, k, d);
          // tamaños: título en una línea dentro del ancho (con el icono), rótulos en una línea
          // `title_max` (px): tope del título (que no mande sobre el medidor); por defecto 92·s
          const tMax = Number(props.title_max) > 0 ? Math.max(52, Math.min(S(92), Number(props.title_max))) : S(92);
          gx.fit(title.m, { max: tMax, min: 52, width: A.w - (icon ? S(132) : 0), lines: 1 });
          if (sub) gx.fit(sub.m, { max: S(48), min: 34, width: A.w, lines: 1 });
          if (props.label_fit === true) {
            // (`label_fit`): la caja del rótulo mide la columna entera, así que gx.fit la veía siempre «demasiado
            // ancha» y bajaba al mínimo (36 px). Aquí se mide el TEXTO (caja a su ancho) contra la columna, todos al mismo
            // cuerpo (el menor), nunca por debajo de label_min, y la caja queda ajustada al texto y centrada en su medidor
            const lmin = Math.max(40, Math.min(72, Number(props.label_min) || 48));
            const lmax = Math.max(lmin, S(58));
            const lpF = Math.min(...G.map((x) => {
              x.lab.m.style.width = "auto";
              return gx.fit(x.lab.m, { max: lmax, min: lmin, width: span - S(56), lines: 1 });
            }));
            G.forEach((x) => {
              x.lab.m.style.fontSize = lpF + "px";
              const w = Math.ceil(x.lab.m.scrollWidth) + 4;
              Object.assign(x.lab.m.style, { left: R(x.cx - w / 2) + "px", width: w + "px" });
            });
          } else {
            const lp = Math.min(...G.map((x) => gx.fit(x.lab.m, { max: S(58), min: 36, width: span - S(56), lines: 1 })));
            G.forEach((x) => { x.lab.m.style.fontSize = lp + "px"; });
          }
          gx.ev(ctx, "enter", t0);
          gx.bgIn(tl, bd, t0, t1, 41, props);
          // 1 · título: el icono se asienta (pop solo en el icono) y el texto sube por su máscara, en su palabra
          const tT = Math.max(t0 + f(2), C("title", t0 + f(2)));
          if (icon) ft(tl, icon, { opacity: 0, scale: 0.5, rotation: -10 }, { opacity: 1, scale: 1, rotation: 0, duration: f(10), ease: E.pop }, tT);
          gxx.rise(tl, title.i, tT + f(2), { dur: f(8), ease: E.enter });
          gx.ev(ctx, "title", tT);
          let tLast = tT + f(10);
          // `hero`: el objeto ya está en el corte (no es texto: nunca papel vacío en el relevo) y se asienta en 10 f
          if (hero) {
            gsap.set(hero, { transformOrigin: "50% 60%" });
            tl.set(hero, { opacity: 1 }, T(t0));
            ft(tl, hero, { scale: 0.86, y: S(14) }, { scale: 1, y: 0, duration: f(10), ease: E.pop }, t0);
          }
          if (sub) { const tSu = Math.max(tT + f(8), C("sub", tT + 0.6)); gxx.rise(tl, sub.i, tSu, { dur: f(8), ease: E.enter }); gx.ev(ctx, "sub", tSu); tLast = tSu + f(8); }
          // icono vivo: la moneda se balancea despacio mientras el plano dura
          if (icon) {
            const val = (k) => (k < 0 ? 0 : (k % 2 ? -4 : 4));
            for (let k = 0, tk = tT + f(10); tk + 0.8 < t1 - f(6); k++, tk += 0.8) ft(tl, icon, { rotation: val(k - 1) }, { rotation: val(k), duration: 0.8, ease: E.move }, tk);
          }
          if (hero) {   // el héroe también vive: balanceo lento de ±3° mientras dura el plano
            const val = (k) => (k < 0 ? 0 : (k % 2 ? -3 : 3));
            for (let k = 0, tk = t0 + f(10); tk + 0.8 < t1 - f(6); k++, tk += 0.8) ft(tl, hero, { rotation: val(k - 1) }, { rotation: val(k), duration: 0.8, ease: E.move }, tk);
          }
          // (medidores vacíos ~2 s antes de llenarse = relleno). `draw_each: true`
          //   (opt-in): cada pista se dibuja f(16) antes de SU llenado y su tope llega al acabar de dibujarse
          const EACH = props.draw_each === true;
          if (EACH) {
            let tp = tLast + f(16);
            G.forEach((x, i) => { x.tg = Math.max(tp, C(x.g.cue || "g" + i, tp + 0.5)); x.td = x.tg - f(16); tp = x.tg + f(10); });
            // con cue `gauges`, la PRIMERA pista se dibuja en esa palabra (si cae antes): el título no se queda solo
            const tDc = C("gauges", null);
            if (tDc != null) G[0].td = Math.max(tLast - f(8), Math.min(G[0].td, tDc));
          }
          // 2 · pistas: se dibujan de izquierda a derecha con sus marcas y el eje
          // `quick`: las pistas con el título; los topes 10 f después; los llenados en su cue (4–6 f de margen)
          const QUICK = props.quick === true && !EACH;
          const tD = EACH ? G[0].td : QUICK ? Math.max(t0 + f(1), C("gauges", tT)) : Math.max(tLast, C("gauges", tLast + 0.4));
          G.forEach((x, i) => {
            const td = EACH ? x.td : tD + i * f(4);
            ft(tl, x.track, { strokeDashoffset: L + 2 }, { strokeDashoffset: 0, duration: f(14), ease: E.move }, td);
            ft(tl, x.ticks, { opacity: 0 }, { opacity: 1, duration: f(4), ease: E.enter, stagger: f(1) }, td + f(3));
            ft(tl, [x.hub, x.nd], { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, td + f(6));
            if (x.brand) ft(tl, x.brand, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: f(8), ease: E.enter }, td + f(2));
            if (x.brandT) gxx.rise(tl, x.brandT.i, td + f(2), { dur: f(8), ease: E.enter });
          });
          gx.ev(ctx, "draw", tD);
          // 3 · topes del límite
          const tLi = EACH ? G[0].td + f(10) : QUICK ? tD + f(10) : Math.max(tD + f(16), C("limits", tD + f(16)));
          if (!NOLIM) {
            G.forEach((x, i) => ft(tl, x.lim, { opacity: 0, scaleX: 0.2 }, { opacity: 1, scaleX: 1, duration: f(7), ease: E.enter }, EACH ? x.td + f(10) : tLi + i * f(2)));
            gx.ev(ctx, "limit", tLi);
          }
          // 4 · cada medidor se llena en SU palabra: la aguja barre con la misma curva y su rótulo sube
          let tPrev = QUICK ? tD + f(4) : tLi + f(8);
          // `fill_ease` / `gauges[].ease` ("move" | "enter"): curva del
          //   llenado (arco y aguja juntos). "enter" = token de entrada (power3.out): la aguja gira de forma visible desde el
          //   primer fotograma del tween (con "move", power2.inOut, apenas se mueve los primeros ~3 f y el SFX del evento
          //   `fill` suena antes de que se vea girar). Sin la prop, "move" (lo de siempre)
          const fEase = (x) => ((x.g.ease || props.fill_ease) === "enter" ? E.enter : E.move);
          G.forEach((x, i) => {
            const tg = EACH ? x.tg : Math.max(tPrev, C(x.g.cue || "g" + i, tPrev + 0.5 + i * 0.8));
            const dur = f(20);
            ft(tl, x.fill, { strokeDashoffset: L + 2 }, { strokeDashoffset: R(L * (1 - x.level)), duration: dur, ease: fEase(x) }, tg);
            const so = `${x.cx} ${x.cy}`;
            ft(tl, x.nd, { rotation: -90, svgOrigin: so }, { rotation: -90 + 180 * x.level, svgOrigin: so, duration: dur, ease: fEase(x) }, tg);
            if (props.label_hide !== true) gxx.rise(tl, x.lab.i, tg, { dur: f(8), ease: E.enter });
            x.tEnd = tg + dur;
            gx.ev(ctx, "fill", tg);
            // lectura viva: la aguja tiembla ±1,5° hasta el final del plano
            const a = -90 + 180 * x.level;
            const jv = (k) => (k < 0 ? 0 : (k % 2 ? -1.5 : 1.5));
            // `still: true` = la aguja llega y se queda (sin temblor;
            //   los «minirebotes» y temblores parecen fallo)
            if (props.still !== true) for (let k = 0, tk = tg + dur; tk + 0.42 < t1 - f(6); k++, tk += 0.42) ft(tl, x.nd, { rotation: a + jv(k - 1), svgOrigin: so }, { rotation: a + jv(k), svgOrigin: so, duration: 0.42, ease: E.move }, tk);
            tPrev = tg + (QUICK ? f(6) : f(10));
          });
          // (opcional) · relevo del título en sus cues (solo opacidad: la caja no sube fuera de la zona segura)
          let curT = title.m;
          relays.forEach((e) => {
            gx.fit(e.l.m, { max: tMax, min: 52, width: A.w, lines: 1 });
            const at = Math.max(tT + f(10), C(e.t.cue, tT + 1));
            tl.to(curT, { opacity: 0, duration: f(4), ease: E.exit }, T(at - f(3)));
            gxx.rise(tl, e.l.i, at, { dur: f(8), ease: E.enter });
            gx.ev(ctx, "title", at);
            curT = e.l.m;
          });
          // (opcional) · la barra oro salta al medidor siguiente cuando el suyo llega a su nivel
          if (props.jump_marker === true) {
            const mw = R(r * 1.2), mh = S(16), my = G[0].cy + S(36);
            const jm = gx.el("div", "vg-jump", wrap);
            Object.assign(jm.style, { position: "absolute", left: "0", top: "0", width: mw + "px", height: mh + "px", borderRadius: mh / 2 + "px", background: "#F2C230" });
            gsap.set(jm, { x: G[0].cx - mw / 2, y: my, opacity: 0 });
            ft(tl, jm, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, tD + f(8));
            G.slice(0, -1).forEach((x, i) => {
              const tj = x.tEnd;
              ft(tl, jm, { x: x.cx - mw / 2 }, { x: G[i + 1].cx - mw / 2, duration: f(10), ease: E.move }, tj);
              ft(tl, jm, { y: my }, { y: my - S(44), duration: f(5), ease: "power2.out" }, tj);
              ft(tl, jm, { y: my - S(44) }, { y: my, duration: f(5), ease: "power2.in" }, tj + f(5));
              gx.ev(ctx, "limit", tj);
            });
          }
          // en el resto, los rótulos sin medidor lleno aún no se ven (nada adelanta lo que no ha dicho)
          gx.out(tl, props, t1, [wrap], { dur: f(5), ctx });
        },
      });
    },
  });
})(window.CK);
