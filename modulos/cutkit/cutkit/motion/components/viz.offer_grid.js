// viz.offer_grid — la columna vertebral de un vídeo de «N ofertas»: la rejilla de baldosas de cristal oscuro con los
//   iconos 3D del kit. MISMA geometría en todos los modos (las baldosas solo dependen del área), así que instancias
//   seguidas empalman sin saltos.
//   all   (gancho): las 6 baldosas entran en cascada corta (≤0,4 s) y el titular `kicker` sube debajo.
//   focus (ordinal N): en `number` la baldosa N crece y se enciende (aro de oro, icono a su color) y las demás se
//         apagan; encima del nombre aparece «N/6» en oro; en `name` sube el NOMBRE (Montserrat 900, una línea).
//   pick  (cierre): en `pick` cinco baldosas se apagan y la elegida (`focus`) queda en oro, crece y se centra.
//   Iconos: en reposo, plata (monocromo); el foco, en duotono oro (icon_focus: "color" lo deja a su color real).
// (con 7 u 8 baldosas la última fila va centrada.)
// props: {items: [{icon, label}] (≤ 9), mode: all|focus|pick, focus: 1–9, kicker?, ordinal?, icon_focus?: gold|color, canvas?, keep_start?, exit?}
// 9: band_pos «top» (banda arriba a 950 px, rejilla 3×3 debajo y ≤ 696 px),
// ordinal_style «serif» (se pinta como «sans», regla de estilo: nunca serif; ordinal_px), name (sustituye al rótulo de la baldosa), show_ordinal,
//   done (las ya contadas a media luz), also + cue «also» (más baldosas encendidas a la vez), pick_glyph «target» (la
//   elegida enseña una diana: no dice cuál), sub + cue «sub» y kicker en su palabra (cue «title») en pick.
// ordinal_style «sans» (ordinal grande en Montserrat 900 con la «ª» pequeña y elevada; ordinal «1.ª»).
// cues:  tiles, title (all; i0…i5 = cada baldosa en su palabra, en oro mientras se nombra; «all» apaga el último foco; «same» aro blanco en las seis; «lit» las seis en oro a la vez) · number, name (focus) · pick (pick)
// eventos: enter, tile (cada baldosa), focus (extra {step: N}), name, pick, exit
// `carry` / `carry_from` (arranca en el estado final de la
//   rejilla anterior; en «number» el aro VIAJA de la baldosa k−1 a la k y la cámara empuja ≤ 4 % a la activa; evento carry),
//   `tiles: "in"` (baldosas puestas en el fotograma 0, sin texto), `name_gap` (aire ordinal → nombre → rejilla) y
//   mode «combine» (la rejilla se abre; cada baldosa de `also` en su cue c0… lanza un conector de circuito con pulso al
//   foco, que late y gira con el último; `note` debajo; eventos spread, connect, merge, note). Diana del pick en el oro
//   del kit (gx.icon). Las baldosas van dentro de un «slot» (la apertura mueve el slot; los estados, la baldosa).
// ── gx:begin, kit compartido de gráficos (bloque idéntico en todos los componentes; se define una sola vez) ──
(function (CK) {
  // Versión del kit: la copia MÁS NUEVA gana sea cual sea el orden de carga (html.py carga por orden alfabético).
  // Al cambiar el kit, sube KIT_V y re-sincroniza el bloque en todos los componentes que lo llevan.
  // v14: gx.textIn / gx.maskIn (regla de entrada de TODO texto), gx.cutIn manda el texto a textIn, glifos
  // keys · terminal · braces y gx.blink (cursor). Si ya hay un kit de esta versión SIN textIn (otra copia), se completa.
  const KIT_V = 14;
  const PREV = CK.gx;
  if (PREV && (PREV.v || 0) >= KIT_V && PREV.textIn) return;
  const FPS = 30;
  const f = (n) => n / FPS; // fotogramas @30 → segundos (los tokens de motion están en fotogramas)
  // Eases: SOLO 4 tokens con nombre (QA mo.ease_tokens ≤4). CK.ease = {enter, exit, move, pop}; el runtime usa los
  // mismos nombres. Alias de compatibilidad: hero/count → enter, settle → pop. «pop» (back.out 1.4) solo en baldosas,
  // iconos y logos que se asientan (≤1 por componente), nunca en texto ni datos.
  const EASE0 = { enter: "power3.out", exit: "power2.in", move: "power2.inOut", pop: "back.out(1.3)" }; // pop único del vídeo (dirección de arte)
  function easeTokens(ctx) {
    if (!CK.ease) {
      const m = (ctx && ctx.tokens && ctx.tokens.motion && ctx.tokens.motion.ease) || (CK.tokens && CK.tokens.motion && CK.tokens.motion.ease) || {};
      const ok = (x) => typeof x === "string" && x.length > 0;
      CK.ease = { enter: ok(m.enter) ? m.enter : EASE0.enter, exit: ok(m.exit) ? m.exit : EASE0.exit,
        move: ok(m.move) ? m.move : EASE0.move, pop: ok(m.pop) ? m.pop : EASE0.pop };
    }
    return CK.ease;
  }
  const EASE = new Proxy({}, { get: (_, k) => { const e = CK.ease || EASE0; return k === "hero" || k === "count" ? e.enter : k === "settle" ? e.pop : e[k] || e.enter; } });
  function eases(ctx) {
    const e = easeTokens(ctx);
    return { enter: e.enter, exit: e.exit, move: e.move, pop: e.pop, hero: e.enter, count: e.enter, settle: e.pop };
  }
  // Fin del deslizado del layout (split con enter:"slide"): ningún texto antes de esto (saldría por encima de y=288).
  function settle(ctx, t0) {
    // El runtime monta en .ck-drop los gráficos que coinciden con el deslizado de un split: caen CON el panel.
    // Así que el primer estado va visible desde t0 (nunca un panel vacío que se rellena después).
    return t0;
  }
  const T = (t) => Math.max(t, 0.001); // nunca un set en t=0 exacto
  const R = (v) => Math.round(v);      // px enteros
  // Regla de estilo: sin punto medio en pantalla; como separador se sustituye por coma (red de seguridad).
  function nodot(t) { return t.replace(/\s*\u00B7\s*/g, ", "); }
  function el(tag, cls, parent, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = nodot(String(text));
    if (parent) parent.appendChild(n);
    return n;
  }
  function svg(tag, attrs, parent) {
    const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const k in attrs || {}) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  // Desplazamiento del root respecto al lienzo (el root del runtime es un div.clip a lienzo completo).
  function originOf(root) {
    let x = 0, y = 0, n = root;
    while (n && n.offsetParent && !(n.hasAttribute && (n.hasAttribute("data-composition-id") || n.id === "ck-content"))) {
      x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent;
    }
    return { x, y };
  }
  function zOf(ctx, d) { return ctx && ctx.z != null ? ctx.z + (d || 0) : null; }
  // Caja de contenido, CENTRADA en x=540, siempre dentro de la zona segura de TEXTO:
  //   x 65–1015 por encima de y=1000 (950 px), por debajo de y=1000, como máximo 696 px centrados (192–888), y ≥ 288.
  // , Slot a pantalla completa (broll_full): BANDA DE GRÁFICOS 288–1000, 950 px; el contenido se centra en vertical.
  // , Slot parcial (split 0–874): 288 → borde del slot, 950 px.
  // , opt.safe: zona segura clásica (texto sobre la cara: CTA, lockup over_face) → 696 px si baja de 1000.
  function area(root, ctx, cls, opt) {
    opt = opt || {};
    const W = ctx.W || 1080, H = ctx.H || 1920;
    const s = ctx.slot || { x: 0, y: 0, w: W, h: H };
    const sf = ctx.safe || { top: 288, bottom: 672, left: 65, right: 192 };
    const pad = opt.pad == null ? 0 : opt.pad;
    const full = s.y <= 0 && s.y + s.h >= H - 200;
    const SPLIT_Y = 1000, FULL_Y1 = 1240;
    let y0 = Math.max(s.y, sf.top, opt.top != null ? opt.top : 0), y1;
    if (opt.safe) y1 = Math.min(s.y + s.h, H - sf.bottom);
    else if (full) y1 = Math.min(opt.bottom != null ? opt.bottom : FULL_Y1, H - sf.bottom); // banda en «T»: 288–1240
    else y1 = Math.min(s.y + s.h, H - sf.bottom);
    // band "center" (pantalla completa): banda simétrica alrededor del centro del lienzo (460–1460), no la «T» alta
    if (opt.center && full) { y1 = H - sf.bottom; y0 = Math.max(y0, H - y1); }
    y0 += pad; y1 -= pad;
    const tee = full && !opt.safe && y1 > SPLIT_Y; // T: 950 px por encima de y=1000, ≤696 px por debajo
    const high = y1 <= SPLIT_Y || tee;
    const cx = W / 2;
    const lowW = 2 * Math.min(cx - sf.left, W - sf.right - cx);
    const maxW = high ? W - 2 * sf.left : lowW;
    const w = R(Math.max(200, Math.min(maxW, s.w - 2 * Math.max(0, sf.left - s.x)) - 2 * pad)), h = R(Math.max(160, y1 - y0));
    const x0 = cx - w / 2;
    const o = originOf(root);
    const n = el("div", "gx-area " + (cls || "") + (tee ? " gx-tee" : ""), root);
    Object.assign(n.style, { left: R(x0 - o.x) + "px", top: R(y0 - o.y) + "px", width: w + "px", height: h + "px" });
    if (zOf(ctx, 1) != null) n.style.zIndex = zOf(ctx, 1);
    const wLow = tee ? R(Math.min(w, lowW - 2 * pad)) : w, yLow = tee ? R(SPLIT_Y - y0) : h;
    if (tee) { n.style.setProperty("--wlow", wLow + "px"); n.style.setProperty("--ylow", yLow + "px"); }
    return { node: n, x: x0, y: y0, w, h, slot: s, origin: o, high, full, tee, wLow, yLow };
  }
  // Componentes anchos de verdad (dos columnas, filas a 950 px): en la «T» usan solo la banda alta (288–1000).
  function upper(A) {
    if (!A || !A.tee) return A;
    A.h = A.yLow; A.node.style.height = A.yLow + "px"; A.tee = false; A.node.classList.remove("gx-tee");
    return A;
  }
  // Banda en «T» (pantalla completa): lo que mida más de wLow tiene que acabar por encima de yLow (y=1000). Coloca el
  // contenido centrado en la banda y lo sube lo justo; si ni así cabe, reduce la escala (refit) hasta que cabe.
  // blocks: nodos a medir (por defecto, los hijos en flujo de wrap). Devuelve la escala final.
  function tfit(A, wrap, s, refit, o) {
    o = o || {};
    if (!A.tee) return s;
    const blocks = () => (o.blocks ? o.blocks() : Array.from(wrap.children).filter((n) => n.offsetParent !== null && getComputedStyle(n).position !== "absolute"));
    const lo = o.min || 0.5;
    for (let k = 0; k < 10; k++) {
      wrap.style.top = ""; wrap.style.bottom = "";
      // medidas de MAQUETA (sin transformaciones: un filete a scaleX 0 o una ficha girada miden lo que ocuparán)
      const rs = blocks().map((n) => { const t = n.offsetTop + (n.offsetParent === wrap ? 0 : 0); return { t, b: t + n.offsetHeight, w: n.offsetWidth }; }).filter((r) => r.b > r.t);
      if (!rs.length) return s;
      const top = Math.min(...rs.map((r) => r.t)), bot = Math.max(...rs.map((r) => r.b));
      const wide = rs.filter((r) => r.w > A.wLow + 1), wideBot = wide.length ? Math.max(...wide.map((r) => r.b)) : -1e9;
      const lastWide = wide.length && wideBot >= bot - 1;
      let d = R(((lastWide ? A.yLow : A.h) - (top + bot)) / 2); // centrado en la banda (en la alta si lo último es ancho)
      d = Math.min(d, A.yLow - wideBot);             // lo ancho, por encima de y=1000
      d = Math.max(d, -top);                         // sin salirse por arriba
      d = R(d);
      if (d) { wrap.style.top = d + "px"; wrap.style.bottom = -d + "px"; }
      if (wideBot + d <= A.yLow + 1 || s <= lo || !refit) return s;
      s = Math.max(lo, s * 0.95); A.node.style.setProperty("--s", s); refit(s);
    }
    return s;
  }
  // Alto real del contenido de un contenedor flex (del primer al último hijo en flujo).
  function contentH(wrap) {
    const ch = Array.from(wrap.children).filter((n) => n.offsetParent !== null && getComputedStyle(n).position !== "absolute");
    if (!ch.length) return wrap.scrollHeight;
    const a = ch[0].getBoundingClientRect(), b = ch[ch.length - 1].getBoundingClientRect();
    return b.bottom - a.top;
  }
  // Escala --s para que el contenido LLENE la banda (fill,alto) sin pasarse; refit(s) reajusta los textos.
  function autoscale(A, wrap, s, refit, o) {
    o = o || {};
    const fill = o.fill || 0.9, lo = o.min || 0.6, hi = o.max || 1.6;
    for (let k = 0; k < 4; k++) {
      const h = o.measure ? o.measure() : contentH(wrap);
      if (!(h > 0)) break;
      const r = (A.h * fill) / h;
      if (r > 0.97 && r < 1.03) break;
      const ns = Math.max(lo, Math.min(hi, s * r));
      if (Math.abs(ns - s) < 0.01) break;
      s = ns; A.node.style.setProperty("--s", s); if (refit) refit(s);
    }
    return s;
  }
  // Lienzos: paper (crema con grano), white, ink (oscuro), accent (oro), black, navy. Alias: canvas = backdrop.
  const CANVAS = { paper: "light", white: "light", accent: "accent", ink: "dark", black: "dark", navy: "dark", none: "dark" };
  const isHex = (k) => typeof k === "string" && /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(k);
  // Tema de un lienzo hex: el que dé más contraste al texto (tinta #0F0D10 frente a blanco). #F386A1 → claro.
  function hexTheme(hex) {
    let h = hex.slice(1); if (h.length === 3) h = h.split("").map((c) => c + c).join("");
    const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    const L = 0.2126 * lin(parseInt(h.slice(0, 2), 16)) + 0.7152 * lin(parseInt(h.slice(2, 4), 16)) + 0.0722 * lin(parseInt(h.slice(4, 6), 16));
    return (L + 0.05) / 0.0546 >= 1.05 / (L + 0.05) ? "light" : "dark";
  }
  function themeOfKind(k) { return isHex(k) ? hexTheme(k) : CANVAS[k] || "dark"; }
  function canvasOf(props) { const k = (props && (props.canvas || props.backdrop)) || "none"; return CANVAS[k] || isHex(k) ? k : "none"; }
  function themeOf(props) { return themeOfKind(canvasOf(props)); }
  // Instante VISUAL real de un evento (para alinear el SFX): ctx.event(kind, t) si el runtime lo expone.
  function ev(ctx, kind, t) { try { if (ctx && typeof ctx.event === "function" && isFinite(t)) ctx.event(kind, Math.round(t * FPS) / FPS); } catch (e) { /* opcional */ } }
  // ── Movimiento con oficio (dirección de arte §1.2.4)
  // Motion blur DIRECCIONAL por elemento: filtro SVG propio (feGaussianBlur «X 0» o «0 Y») cuyo stdDeviation se anima.
  let mbN = 0, mbSvg = null;
  function mblurOf(node, axis) {
    if (!mbSvg) {
      mbSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      mbSvg.setAttribute("width", "0"); mbSvg.setAttribute("height", "0");
      mbSvg.style.cssText = "position:absolute;width:0;height:0;overflow:hidden";
      (document.body || document.documentElement).appendChild(mbSvg);
    }
    const key = "_gxmb" + axis;
    if (node[key]) return node[key];
    const id = "gxmb" + (++mbN);
    const flt = svg("filter", { id, x: "-30%", y: "-30%", width: "160%", height: "160%", "color-interpolation-filters": "sRGB" }, mbSvg);
    const fe = svg("feGaussianBlur", { stdDeviation: "0 0" }, flt);
    node.style.filter = "url(#" + id + ")";
    node[key] = fe;
    return fe;
  }
  // Estela: el desenfoque direccional va de `amount` a 0 durante `dur` (para lo que se mueve > 60 px/f).
  function streak(tl, node, at, dur, axis, amount) {
    const fe = mblurOf(node, axis);
    const v = (a) => (axis === "x" ? a + " 0" : "0 " + a);
    ft(tl, fe, { attr: { stdDeviation: v(amount) } }, { attr: { stdDeviation: v(0) }, duration: dur, ease: EASE.enter }, at);
  }
  // Aterrizaje de una tarjeta/ficha/logo: anticipación (2–3 f, 4–8 px en contra), viaje con asentado `pop` y
  // follow-through de la rotación (≤2 oscilaciones de ≤2°). from: {x, y, rotation, scale, opacity}; rot = giro final.
  function land(tl, node, at, o) {
    o = o || {};
    const fr = o.from || {}, rot = o.rot || 0, dur = o.dur || f(9);
    const dx = fr.x || 0, dy = fr.y || 0, dist = Math.hypot(dx, dy);
    const op0 = fr.opacity != null ? fr.opacity : 0, sc0 = fr.scale != null ? fr.scale : 1, r0 = fr.rotation != null ? fr.rotation : rot;
    let t = at, sx = dx, sy = dy, op1 = op0;
    if (o.antic !== false && dist > 80) { // contramovimiento corto (4–8 px) antes del viaje
      const k = Math.min(8, Math.max(4, dist * 0.04)) / dist;
      sx = R(dx * (1 + k)); sy = R(dy * (1 + k)); op1 = Math.max(op0, 0.5);
      ft(tl, node, { x: dx, y: dy, rotation: r0, scale: sc0, opacity: op0 }, { x: sx, y: sy, opacity: op1, duration: f(2), ease: EASE.move }, t);
      t += f(2);
    }
    const sw = o.swing == null ? (dx ? Math.sign(dx) : 1) * 1.6 : o.swing; // follow-through ≤2°
    ft(tl, node, { x: sx, y: sy, rotation: r0, scale: sc0, opacity: op1 },
      { x: 0, y: 0, rotation: rot + sw, scale: o.scale || 1, opacity: 1, duration: dur, ease: o.pop === false ? EASE.enter : EASE.pop }, t);
    if (Math.abs(sw) > 0.05) {
      ft(tl, node, { rotation: rot + sw }, { rotation: rot - sw * 0.45, duration: f(4), ease: EASE.move }, t + dur);
      ft(tl, node, { rotation: rot - sw * 0.45 }, { rotation: rot, duration: f(5), ease: EASE.move }, t + dur + f(4));
    }
    if (o.streak && dist / (dur * FPS) > 30) streak(tl, node, t, dur * 0.7, Math.abs(dx) > Math.abs(dy) ? "x" : "y", Math.min(18, (dist / (dur * FPS)) * 0.25));
    return t + dur;
  }
  // Entrada EN EL CORTE: el gráfico ya se ve en el fotograma de corte (opacidad 0,85 y escala 0,96 → 1 en 3 f).
  // Entrada corta en un corte. Regla de estilo: NUNCA deja nada ya puesto (un texto sin
  // animación de entrada se lee como un fallo): sale de opacidad 0 y se asienta en ≥ 5 f (antes 0,85 → 1 en 3 f).
  // Un fundido de 5 f se veía al 50–80 % ya en su primer fotograma: ≥ 7 f y con una
  // subida corta (14 px), para que la entrada se lea como movimiento (la QA mo.text_entry marca los fundidos < 5 f quietos)
  // Kit v14: gx.cutIn queda para
  // lo que NO es texto (marcos, baldosas, iconos); si un destino lleva texto, entra con gx.textIn.
  function cutIn(tl, targets, at, o) {
    o = o || {};
    const arr = toList(targets);
    if (!arr) return ft(tl, targets, { opacity: 0, scale: o.scale == null ? 0.94 : o.scale, y: o.rise == null ? 14 : o.rise },
      { opacity: 1, scale: 1, y: 0, duration: f(Math.max(7, o.frames || 7)), ease: EASE.enter }, at);
    const txt = arr.filter(hasText), rest = arr.filter((n) => !hasText(n));
    let tw = null;
    if (rest.length) tw = ft(tl, rest, { opacity: 0, scale: o.scale == null ? 0.94 : o.scale, y: o.rise == null ? 14 : o.rise },
      { opacity: 1, scale: 1, y: 0, duration: f(Math.max(7, o.frames || 7)), ease: EASE.enter }, at);
    if (txt.length) textIn(tl, txt, at, { frames: Math.max(8, o.frames || 8) });
    return tw;
  }
  // ── Entrada de TEXTO (kit v14; regla de estilo: ningún texto aparece ya puesto).
  //    Empieza EN el fotograma del corte o de su palabra (nunca antes) y dura 8 f: subida de 32 px (enter) y
  //    opacidad 0 → 1 con el token enter en 10 f, que equivale a power2.out en 8 f (llega al 90 % en ~5,4 f; el runtime
  //    solo admite 4 eases). o.mask: máscara yPercent 110 → 0 (el nodo va dentro de un padre con overflow oculto), como el
  //    kicker de card.lesson. o.frames (≥ 6), o.rise (px).
  const TXT = { frames: 8, rise: 32 };
  function toList(t) {
    if (!t) return [];
    if (Array.isArray(t)) return t.filter(Boolean);
    if (typeof NodeList !== "undefined" && t instanceof NodeList) return Array.from(t);
    if (t.nodeType === 1) return [t];
    return null;   // selector u objeto: sin clasificar
  }
  function hasText(n) {
    if (!n || n.nodeType !== 1) return false;
    if (n.namespaceURI === "http://www.w3.org/2000/svg") return !!(n.textContent || "").trim() && !!n.querySelector && !!n.querySelector("text");
    const w = document.createTreeWalker(n, NodeFilter.SHOW_TEXT);
    for (let c = w.nextNode(); c; c = w.nextNode()) {
      if (!c.nodeValue.trim()) continue;
      const p = c.parentElement;
      if (p && p.closest && p.closest("svg") && !p.closest("text")) continue;
      return true;
    }
    return false;
  }
  function textIn(tl, targets, at, o) {
    o = o || {};
    const n = Math.max(6, o.frames || TXT.frames);
    const d = f(n), dOp = f(Math.round(n * 1.25));
    if (o.mask) ft(tl, targets, { yPercent: o.from == null ? 110 : o.from }, { yPercent: 0, duration: d, ease: EASE.enter }, at);
    else ft(tl, targets, { y: R(o.rise == null ? TXT.rise : o.rise) }, { y: 0, duration: d, ease: EASE.enter }, at);
    ft(tl, targets, { opacity: 0 }, { opacity: 1, duration: dOp, ease: EASE.enter }, at);
    return at + d;
  }
  function maskIn(tl, inner, at, o) { return textIn(tl, inner, at, Object.assign({}, o || {}, { mask: true })); }
  // Cursor que parpadea (glifo `terminal` y similares: nodos .cur): encendido/apagado cada 15 f entre a y b (seek-safe).
  function blink(tl, node, a, b, o) {
    o = o || {};
    const cur = node && node.querySelectorAll ? Array.from(node.querySelectorAll(".cur")) : [];
    if (!cur.length || !(b > a)) return;
    const p = f(o.frames || 15);
    let on = true;
    for (let t = a + p; t < b - f(2); t += p) { on = !on; tl.set(cur, { opacity: on ? 1 : 0 }, T(t)); }
  }
  // Todo en uno: lienzo a sangre del slot + área segura con las variables de contraste del tema (gx-th-*).
  // `canvas` fija el TEMA (contraste); el lienzo lo pinta el layout (panel_bg). Solo se pinta aquí si viene
  // `backdrop` explícito o `paint_canvas: true` (p. ej. un gráfico sobre la cara sin layout de panel).
  function stage(root, ctx, props, cls, opt) {
    const pb = ctx && ctx.layout && ctx.layout.props && ctx.layout.props.panel_bg;
    let kind = canvasOf(props);
    if (kind === "none" && !(props && props.canvas) && (CANVAS[pb] || isHex(pb))) kind = pb;
    // se pinta el lienzo si se pide backdrop/paint_canvas o si el canvas pedido NO es el que pinta el layout
    const paint = props && ((props.backdrop && props.backdrop !== "none") || props.paint_canvas ||
      (props.canvas && props.canvas !== "none" && pb && String(props.canvas).toLowerCase() !== String(pb).toLowerCase()));
    opt = Object.assign({}, opt || {}); if (props && props.band === "safe") opt.safe = true; if (props && props.band === "center") opt.center = true;
    const bd = paint ? backdrop(root, ctx, props.backdrop && props.backdrop !== "none" ? props.backdrop : kind) : null;
    const th = themeOfKind(kind);
    const pinkish = isHex(kind) && (() => { const h = kind.length === 4 ? kind.replace(/^#(.)(.)(.)$/, "#$1$1$2$2$3$3") : kind; const r = parseInt(h.slice(1, 3), 16), g = parseInt(h.slice(3, 5), 16), b = parseInt(h.slice(5, 7), 16); return r > g + 40 && b > g; })();
    const A = area(root, ctx, (cls || "") + " gx-th-" + th + " gx-cv-" + (isHex(kind) ? "hex" : kind) + (pinkish ? " gx-tint-pink" : ""), opt);
    return { A, bd, kind, theme: th };
  }
  function backdrop(root, ctx, kind) {
    if (!kind || kind === "none") return null;
    const s = ctx.slot || { x: 0, y: 0, w: ctx.W || 1080, h: ctx.H || 1920 };
    const o = originOf(root);
    const n = el("div", "gx-backdrop gx-bd-" + (isHex(kind) ? "hex" : kind) + " gx-th-" + themeOfKind(kind), root);
    if (isHex(kind)) n.style.background = kind;
    Object.assign(n.style, { left: R(s.x - o.x) + "px", top: R(s.y - o.y) + "px", width: R(s.w) + "px", height: R(s.h) + "px" });
    if (zOf(ctx, 0) != null) n.style.zIndex = zOf(ctx, 0);
    const g = el("div", "gx-grain", n);
    gsap.set(n, { opacity: 0 });
    return { node: n, grain: g };
  }
  // Grano a 12 fps: saltos con semilla mediante tl.set (seek-safe, finito).
  function grain(tl, bd, t0, t1, seed) {
    if (!bd || !bd.grain) return;
    const r = rng(seed || 7);
    for (let t = t0; t < t1; t += 1 / 12) tl.set(bd.grain, { x: R(r() * 160 - 80), y: R(r() * 160 - 80) }, T(t));
  }
  // fromTo seek-safe (immediateRender:false: el estado inicial lo fija mount con gsap.set).
  // kit v14 · red de seguridad de la regla de entrada de texto: si un fromTo hace APARECER texto (opacidad
  // 0 → ≥ 0,9) en menos de 10 f, su opacidad va en un tween aparte de 10 f con enter (≈ power2.out en 8 f: el 90 % llega en
  // ~5,4 f), para que ningún fundido corto se vea «ya puesto» en su primer fotograma. El resto de propiedades conserva su
  // duración y su ease. Las letras sueltas (cascadas letra a letra, tecleo) quedan fuera, como en la QA mo.text_entry.
  function ft(tl, targets, from, to, at) {
    const d = to && to.duration != null ? to.duration : 0.5;
    if (from && from.opacity === 0 && to && to.opacity != null && to.opacity >= 0.9 && d < f(10) - 1e-6 && to.ease !== "none") {
      const arr = toList(targets);
      if (arr && arr.some((n) => hasText(n) && (n.textContent || "").trim().length > 1)) {
        const fr = Object.assign({}, from), tr = Object.assign({}, to);
        delete fr.opacity; delete tr.opacity;
        const rest = Object.keys(fr).length ? tl.fromTo(targets, fr, Object.assign({ immediateRender: false }, tr), T(at)) : null;
        const op = { opacity: to.opacity, duration: f(10), ease: EASE.enter, immediateRender: false };
        if (to.stagger != null) op.stagger = to.stagger;
        const tw = tl.fromTo(targets, { opacity: 0 }, op, T(at));
        return rest || tw;
      }
    }
    return tl.fromTo(targets, from, Object.assign({ immediateRender: false }, to), T(at));
  }
  // Partir texto en palabras/caracteres. Las palabras van en inline-block nowrap: solo se corta en espacios.
  function split(node, text, mode) {
    node.textContent = "";
    const words = nodot(String(text)).split(/(\s+)/);
    const chars = [], ws = [];
    for (const w of words) {
      if (!w) continue;
      if (/^\s+$/.test(w)) { node.appendChild(document.createTextNode(" ")); continue; }
      const wn = el("span", "gx-w", node);
      ws.push(wn);
      if (mode === "chars") { for (const c of Array.from(w)) chars.push(el("span", "gx-ch", wn, c)); }
      else wn.textContent = w;
    }
    return mode === "chars" ? chars : ws;
  }
  // Ajuste de cuerpo: baja de `max` a `min` hasta caber en `width` (y en `lines` líneas si se pide).
  function fit(node, o) {
    const max = o.max, min = o.min || Math.round(o.max * 0.5), width = o.width;
    const lines = o.lines || 1;
    let size = max;
    for (; size >= min; size -= 2) {
      node.style.fontSize = size + "px";
      const lh = parseFloat(getComputedStyle(node).lineHeight) || size * 1.1;
      const tooWide = node.scrollWidth > width + 1;
      // una línea: solo cuenta el ancho (los glifos desbordan la caja de línea si el interlineado es ajustado)
      const tooTall = lines > 1 && node.scrollHeight > lh * lines + size * 0.35;
      if (!tooWide && !tooTall) break;
    }
    size = Math.max(size, min);
    node.style.fontSize = size + "px";
    return size;
  }
  function cue(cues, key, def) {
    const v = cues && cues[key];
    return typeof v === "number" && isFinite(v) ? v : def;
  }
  // Números: «2.000» por defecto (como las referencias); group:"rae" → 4 cifras juntas y espacio fino desde 5.
  function num(v, decimals, group) {
    const d = decimals || 0;
    const neg = v < 0; v = Math.abs(v);
    let [ent, dec] = v.toFixed(d).split(".");
    if (group === "rae") ent = ent.length >= 5 ? ent.replace(/\B(?=(\d{3})+(?!\d))/g, " ") : ent;
    else if (group !== "none") ent = ent.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    return (neg ? "−" : "") + ent + (dec ? "," + dec : "");
  }
  function rng(seed) { // mulberry32
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function hash(s) { let h = 2166136261 >>> 0; s = String(s); for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } return h; }
  // Salida estándar: limpia y terminada 1 fotograma antes de t1.
  function exit(tl, targets, t1, o) {
    o = o || {};
    const d = o.dur || f(5);
    const at = Math.max(o.after || 0, t1 - d - f(1));
    tl.to(targets, Object.assign({ opacity: 0, y: o.y == null ? -16 : o.y, duration: d, ease: EASE.exit }, o.vars || {}), at);
    return at;
  }
  // Salida según props.exit: "cut" = sin tween (desaparece en t1, cuando le sigue otro gráfico en el mismo layout).
  function out(tl, props, t1, targets, o) {
    const ts = (Array.isArray(targets) ? targets : [targets]).filter(Boolean);
    if (!ts.length) return t1;
    if (props && props.exit === "cut") { tl.set(ts, { opacity: 0 }, T(t1)); if (o && o.ctx) ev(o.ctx, "exit", t1); return t1; }
    const at = exit(tl, ts, t1, o);
    if (o && o.ctx) ev(o.ctx, "exit", at);
    return at;
  }
  function outBg(tl, props, t1, nodes, d) {
    const ts = (Array.isArray(nodes) ? nodes : [nodes]).filter(Boolean);
    if (!ts.length) return;
    if (props && props.exit === "cut") { tl.set(ts, { opacity: 0 }, T(t1)); return; }
    d = d || f(5);
    tl.to(ts, { opacity: 0, duration: d, ease: EASE.exit }, Math.max(0, t1 - d - f(1)));
  }
  // Fondo del lienzo: entra corto (o en corte) y lleva grano a 12 fps.
  function bgIn(tl, bd, t0, t1, seed, props) {
    if (!bd) return;
    grain(tl, bd, t0, t1, seed);
    tl.set(bd.node, { opacity: 1 }, T(t0)); // el lienzo entra en el corte (nunca un fundido desde 0)
    outBg(tl, props, t1, bd.node);
  }
  // Conteo seek-safe sin callbacks: GSAP asigna proxy.v al renderizar (también en seek con eventos suprimidos)
  // y el setter escribe el texto. Ancho reservado con el valor final → no empuja a los vecinos.
  function countText(tl, node, o) {
    const fmt = o.fmt || ((v) => num(v, o.decimals || 0, o.group));
    node.textContent = fmt(o.to);
    if (o.reserve !== false) node.style.minWidth = Math.ceil(node.getBoundingClientRect().width) + "px";
    node.textContent = fmt(o.from || 0);
    let cur = o.from || 0;
    const proxy = {};
    Object.defineProperty(proxy, "v", { get: () => cur, set: (x) => { cur = x; node.textContent = fmt(x); } });
    tl.fromTo(proxy, { v: o.from || 0 }, { v: o.to, duration: o.dur, ease: o.ease || EASE.count, immediateRender: false }, T(o.at));
    return o.at + o.dur;
  }
  // Texto que se cambia en un instante (seek-safe): proxy con setter, sin tl.set de textContent.
  function swapText(tl, node, texts, times) {
    let cur = 0; const proxy = {};
    Object.defineProperty(proxy, "i", { get: () => cur, set: (x) => { cur = x; node.textContent = texts[Math.max(0, Math.min(texts.length - 1, Math.round(x)))]; } });
    node.textContent = texts[0];
    times.forEach((t, k) => tl.set(proxy, { i: k + 1 }, T(t)));
  }
  // Media del item (logos, capturas): el <img> estático NO se mueve; se lee su src y se pinta como fondo de un div.
  function mediaSrc(ctx, id) {
    if (!id) return null;
    const list = (ctx && ctx.media) || [];
    const hit = list.find((m) => m && m.dataset && m.dataset.asset === id) ||
      list.find((m) => m && (m.id === id || m.id === "m_" + id || String(m.id || "").indexOf("m_" + id + "__") === 0));
    if (hit) {
      if (hit.ckWrap) gsap.set(hit.ckWrap, { opacity: 0 }); // el <img> no se mueve: el componente lo pinta en su sitio
      else if (hit.style) hit.style.opacity = "0";
      return hit.currentSrc || hit.src || hit.getAttribute("src");
    }
    if (/[./]/.test(id) && ctx && ctx.assetUrl) return ctx.assetUrl(id); // ruta directa (pruebas)
    return null;
  }
  function logo(parent, ctx, id, cls) {
    const src = mediaSrc(ctx, id);
    const n = el("div", "gx-logo " + (cls || ""), parent);
    if (src) n.style.backgroundImage = `url("${src}")`;
    else n.classList.add("gx-logo-missing");
    return n;
  }
  function color(name) {
    const map = { white: "var(--ck-white)", accent: "var(--ck-accent)", accent2: "var(--ck-accent-2)", "accent-2": "var(--ck-accent-2)",
      green: "var(--ck-green)", red: "var(--ck-red)", muted: "var(--ck-muted)", ink: "var(--ck-ink)", navy: "var(--ck-navy)" };
    return map[name] || map.white;
  }
  // Valor resuelto de una variable CSS del tema (GSAP no interpola «var(--x)»): p. ej. cssv(nodo, "--g-fg") → "#0F0D10".
  function cssv(node, name, def) {
    const v = getComputedStyle(node).getPropertyValue(name).trim();
    return v || def || "#FFFFFF";
  }
  // ── Iconos de estado en el ORO DEL KIT: un sitio común
  //    para pintar cualquier glifo de estado (estaciones, baldosas, diana, entradas del pipeline) en el oro de los iconos
  //    3D del kit, o un asset del kit teñido con su mismo duotono (filtro gx-gold = og-gold de viz.offer_grid).
  //    icon(parent, ctx, {asset?|glyph?, tone?: gold|ink|white|silver|color}, cls) → nodo (cuadrado: tamaño por CSS).
  const GOLD = { deep: "#54410F", mid: "#9F853B", hi: "#DFC05B", light: "#FFDE6B", flat: "#FECA1A" };
  function defs() {
    if (document.getElementById("gx-defs")) return;
    const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.id = "gx-defs"; s.setAttribute("width", "0"); s.setAttribute("height", "0");
    s.style.cssText = "position:absolute;width:0;height:0;overflow:hidden";
    s.innerHTML = `<defs>
      <linearGradient id="gx-gold-g" gradientUnits="userSpaceOnUse" x1="8" y1="4" x2="40" y2="46">
        <stop offset="0" stop-color="#F6DB79"/><stop offset=".5" stop-color="#CDA640"/><stop offset="1" stop-color="#83681F"/></linearGradient></defs>
      <filter id="gx-gold" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/>
        <feComponentTransfer><feFuncR type="table" tableValues="0.16 1.0"/><feFuncG type="table" tableValues="0.10 0.87"/><feFuncB type="table" tableValues="0.0 0.42"/></feComponentTransfer></filter>
      <filter id="gx-silver" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/>
        <feComponentTransfer><feFuncR type="table" tableValues="0.06 0.93"/><feFuncG type="table" tableValues="0.06 0.93"/><feFuncB type="table" tableValues="0.07 0.95"/></feComponentTransfer></filter>`;
    (document.body || document.documentElement).appendChild(s);
  }
  // glifos de línea (viewBox 48, trazo 4): neutros, nunca marcas. «.f» = relleno.
  const GLYPHS = {
    play: '<rect x="5" y="9" width="38" height="30" rx="7"/><path class="f" d="M20 17 L32 24 L20 31 Z"/>',
    wave: '<path d="M6 24 V24 M12 19 V29 M18 13 V35 M24 17 V31 M30 10 V38 M36 18 V30 M42 22 V26"/>',
    screen: '<rect x="5" y="8" width="38" height="25" rx="4"/><path d="M18 41 H30 M24 33 V41"/><path d="M12 15 H26 M12 21 H22"/>',
    mail: '<rect x="6" y="11" width="36" height="26" rx="4"/><path d="M7 13 L24 26 L41 13"/>',
    chat: '<path d="M9 10 H39 a4 4 0 0 1 4 4 V30 a4 4 0 0 1 -4 4 H22 L13 41 V34 H9 a4 4 0 0 1 -4 -4 V14 a4 4 0 0 1 4 -4 Z"/><path d="M15 20 H33 M15 26 H27"/>',
    phone: '<path d="M14 6 L20 6 L23 15 L18 19 C20 25 23 28 29 30 L33 25 L42 28 L42 34 C42 39 38 42 33 41 C19 38 10 29 7 15 C6 10 9 6 14 6 Z"/>',
    clock: '<circle cx="24" cy="24" r="18"/><path d="M24 13 V24 L31 29"/>',
    calendar: '<rect x="6" y="10" width="36" height="31" rx="5"/><path d="M6 19 H42 M15 6 V13 M33 6 V13"/><path class="f" d="M14 25 h6 v6 h-6 Z"/>',
    check: '<path d="M10 25 L20 35 L39 14"/>',
    bolt: '<path class="f" d="M27 4 L10 27 H22 L19 44 L38 19 H26 Z"/>',
    chart: '<path d="M8 40 H42"/><path class="f" d="M11 27 h7 v11 h-7 Z M21 19 h7 v19 h-7 Z M31 11 h7 v27 h-7 Z"/>',
    user: '<circle cx="24" cy="16" r="8"/><path d="M8 42 C9 32 16 27 24 27 C32 27 39 32 40 42"/>',
    doc: '<path d="M12 5 H29 L38 14 V43 H12 Z"/><path d="M29 5 V14 H38 M18 23 H32 M18 30 H32 M18 37 H27"/>',
    gear: '<circle cx="24" cy="24" r="7"/><path d="M24 5 V11 M24 37 V43 M5 24 H11 M37 24 H43 M10.6 10.6 L14.8 14.8 M33.2 33.2 L37.4 37.4 M10.6 37.4 L14.8 33.2 M33.2 14.8 L37.4 10.6"/><circle cx="24" cy="24" r="14"/>',
    search: '<circle cx="21" cy="21" r="13"/><path d="M31 31 L42 42"/>',
    globe: '<circle cx="24" cy="24" r="18"/><path d="M6 24 H42 M24 6 C17 13 17 35 24 42 C31 35 31 13 24 6"/>',
    star: '<path class="f" d="M24 5 L29.6 17.3 L43 18.8 L33 27.9 L35.8 41.2 L24 34.5 L12.2 41.2 L15 27.9 L5 18.8 L18.4 17.3 Z"/>',
    heart: '<path d="M24 40 C10 30 6 23 6 17 C6 11 10.5 7 15.5 7 C19.5 7 22.5 9.5 24 12.5 C25.5 9.5 28.5 7 32.5 7 C37.5 7 42 11 42 17 C42 23 38 30 24 40 Z"/>',
    send: '<path d="M42 6 L6 21 L21 27 L27 42 Z M21 27 L42 6"/>',
    thumb: '<path d="M14 21 H8 V41 H14 Z M14 23 L22 7 C26 7 27 10 26 14 L25 19 H38 C41 19 42 22 41 25 L38 37 C37 40 35 41 32 41 H14"/>',
    repost: '<path d="M10 20 V15 C10 12 12 10 15 10 H36 M30 4 L36 10 L30 16 M38 28 V33 C38 36 36 38 33 38 H12 M18 44 L12 38 L18 32"/>',
    clip: '<rect x="5" y="10" width="38" height="28" rx="3"/><path d="M5 17 H43 M5 31 H43 M12 10 V17 M20 10 V17 M28 10 V17 M36 10 V17 M12 31 V38 M20 31 V38 M28 31 V38 M36 31 V38"/>',
    // v14: neutros para herramientas sin logo verificado (nunca un monograma que imite una marca)
    // keys: dos fotogramas clave (rombos) sobre su pista y la curva de ease entre ellos (animación, editor de vídeo)
    keys: '<path d="M4 38 H44"/><path class="f" d="M11 31 L18 38 L11 45 L4 38 Z"/><path class="f" d="M37 31 L44 38 L37 45 L30 38 Z"/><path d="M11 25 C25 25 23 6 37 6"/><path class="f" d="M11 21.5 a3.5 3.5 0 1 0 0.01 0 Z M37 2.5 a3.5 3.5 0 1 0 0.01 0 Z"/>',
    // terminal: «>_» en una ventana; el «_» (.cur) parpadea con gx.blink
    terminal: '<rect x="5" y="8" width="38" height="32" rx="6"/><path d="M13 18.5 L20 24 L13 29.5"/><path class="cur" d="M24 30 H34"/>',
    // braces: «{ }» (JSON, canal de control)
    braces: '<path d="M19 7 C14 7 13 9.5 13 13 V19 C13 22 11.5 24 7.5 24 C11.5 24 13 26 13 29 V35 C13 38.5 14 41 19 41"/><path d="M29 7 C34 7 35 9.5 35 13 V19 C35 22 36.5 24 40.5 24 C36.5 24 35 26 35 29 V35 C35 38.5 34 41 29 41"/>',
  };
  function glyph(parent, name, cls) {
    const n = svg("svg", { viewBox: "0 0 48 48", class: "gx-glyph " + (cls || "") }, parent);
    if (name === "target") {
      [[21, "f"], [15, "p"], [9.5, "f"], [4, "d"]].forEach(([r, c]) => svg("circle", { cx: 24, cy: 24, r, class: "gx-t-" + c }, n));
      n.classList.add("gx-glyph-target");
    } else n.innerHTML = GLYPHS[name] || GLYPHS.check;
    return n;
  }
  function icon(parent, ctx, spec, cls) {
    defs();
    spec = typeof spec === "string" ? { glyph: spec } : spec || {};
    const tone = spec.tone || "gold";
    const n = el("div", "gx-icon gx-icon-" + tone + " " + (cls || ""), parent);
    if (spec.asset) {
      const lg = logo(n, ctx, spec.asset, "gx-icon-img");
      if (tone === "gold" || tone === "silver") lg.classList.add("gx-tint-" + tone);
    } else glyph(n, spec.glyph || "check", "gx-icon-svg");
    return n;
  }
  // ── Conectores de circuito (kit v13): trazo de tinta + oro (vocabulario de viz.road) que se dibuja en su cue y un
  //    pulso oro que lo recorre a velocidad constante (tramos lineales con papel «path»: no cuentan como ease).
  function polyLen(pts) { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; }
  function wire(svgParent, pts, o) {
    o = o || {};
    const d = "M " + pts.map((p) => R(p[0]) + " " + R(p[1])).join(" L ");
    const L = Math.max(1, polyLen(pts));
    const ol = svg("path", { d, class: "gx-wire-ol", "stroke-width": o.wo || 11 }, svgParent);
    const gd = svg("path", { d, class: "gx-wire", "stroke-width": o.w || 5 }, svgParent);
    [ol, gd].forEach((p) => { p.style.strokeDasharray = L + " " + L; p.style.strokeDashoffset = L; });
    // oculto hasta su cue: con el extremo redondeado, un tramo «sin dibujar» (dashoffset = L) pinta un punto suelto
    gsap.set([ol, gd], { opacity: 0 });
    return { ol, gd, L, pts };
  }
  function drawWire(tl, w, at, dur) {
    tl.set([w.ol, w.gd], { opacity: 1 }, T(at));
    ft(tl, [w.ol, w.gd], { strokeDashoffset: w.L }, { strokeDashoffset: 0, duration: dur, ease: EASE.move }, at);
    return at + dur;
  }
  function pulse(tl, node, pts, at, dur, o) {
    o = o || {};
    const L = Math.max(1, polyLen(pts)), op = o.op || 1;
    ft(tl, node, { opacity: 0, scale: 0.5 }, { opacity: op, scale: 1, duration: f(3), ease: EASE.enter }, at);
    let t = at;
    for (let i = 1; i < pts.length; i++) {
      const d = dur * Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) / L;
      if (d < 1e-3) continue;
      ft(tl, node, { x: R(pts[i - 1][0]), y: R(pts[i - 1][1]) }, { x: R(pts[i][0]), y: R(pts[i][1]), duration: d, ease: "none", data: { role: "path" } }, t);
      t += d;
    }
    ft(tl, node, { opacity: op, scale: 1 }, { opacity: 0, scale: 0.5, duration: f(3), ease: EASE.exit }, Math.max(at + f(3), t - f(2)));
    return t;
  }
  function pulseDot(parent, px) {
    const d = el("div", "gx-pulse", parent);
    Object.assign(d.style, { width: px + "px", height: px + "px", left: R(-px / 2) + "px", top: R(-px / 2) + "px" });
    gsap.set(d, { opacity: 0 });
    return d;
  }
  // ── Rótulos paralelos con el MISMO número de líneas (regla de estilo: si 2 tienen 2 líneas de texto, la
  //    tercera también, no una). lineParity(nodes, {max, min, min2?, width: px | (nodo) => px, lines?: 2, group?}) →
  //    {px, lines}: el mismo cuerpo para todos; UNA línea si todos caben a ≥ min; si no, TODOS en dos líneas equilibradas
  //    (corte por la palabra que iguala las dos mitades) al mayor cuerpo ≥ min2 que quepa. Un rótulo de una sola palabra no
  //    se puede partir (queda en una y lo dice data-ck-lines). Marca cada nodo (data-ck-lines, data-ck-group) para la QA
  //    ly.line_parity. El texto del rótulo es el del nodo o el de su único hijo (máscaras gxx-m › gxx-mi).
  let mctx = null;
  const escH = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  function textHolder(n) {
    let t = n;
    while (t.children.length === 1 && !Array.from(t.childNodes).some((c) => c.nodeType === 3 && c.nodeValue.trim())) t = t.children[0];
    return t.children.length ? null : t;   // con otros hijos (un check, un icono) no se toca
  }
  function measurer(t) {
    const cs = getComputedStyle(t), px0 = parseFloat(cs.fontSize) || 16;
    const ls = cs.letterSpacing === "normal" ? 0 : (parseFloat(cs.letterSpacing) || 0) / px0;   // em
    const up = cs.textTransform === "uppercase";
    if (!mctx) mctx = document.createElement("canvas").getContext("2d");
    return (s, size) => {
      s = up ? s.toUpperCase() : s;
      mctx.font = `${cs.fontStyle} ${cs.fontWeight} ${size}px ${cs.fontFamily}`;
      return mctx.measureText(s).width + ls * size * Math.max(0, Array.from(s).length - 1);
    };
  }
  function lineParity(nodes, o) {
    o = o || {};
    const Q = (nodes || []).filter(Boolean).map((n) => {
      const t = textHolder(n);
      if (!t) return null;
      if (t.__ckTxt == null) t.__ckTxt = (t.textContent || "").replace(/\s+/g, " ").trim();
      return { n, t, txt: t.__ckTxt, m: measurer(t), w: typeof o.width === "function" ? o.width(n) : o.width };
    }).filter(Boolean);
    if (!Q.length) return { px: o.max, lines: 1 };
    const one = (q, px) => q.m(q.txt, px);
    const split = (q, px) => {
      const ws = q.txt.split(" ");
      let best = { w: one(q, px), k: 0 };
      for (let k = 1; k < ws.length; k++) {
        const w = Math.max(q.m(ws.slice(0, k).join(" "), px), q.m(ws.slice(k).join(" "), px));
        if (k === 1 || w < best.w) best = { w, k };
      }
      return ws.length < 2 ? { w: one(q, px), k: 0 } : best;
    };
    const min = o.min || 30, min2 = o.min2 || min;
    let px = null, lines = 1;
    for (let p = Math.floor(o.max); p >= min; p--) if (Q.every((q) => one(q, p) <= q.w + 0.5)) { px = p; break; }
    if (px == null && (o.lines || 2) >= 2) {
      lines = 2;
      for (let p = Math.floor(o.max); p >= min2; p--) if (Q.every((q) => split(q, p).w <= q.w + 0.5)) { px = p; break; }
      if (px == null) px = min2;
    }
    if (px == null) px = min;
    Q.forEach((q) => {
      q.n.style.fontSize = px + "px";
      const sp = lines === 2 ? split(q, px) : { k: 0 };
      const flex = /flex|grid/.test(getComputedStyle(q.t).display);
      if (sp.k > 0) {
        const ws = q.txt.split(" "), html = escH(ws.slice(0, sp.k).join(" ")) + "<br>" + escH(ws.slice(sp.k).join(" "));
        q.t.innerHTML = flex ? `<span class="gx-lp">${html}</span>` : html;
      } else q.t.textContent = q.txt;
      q.t.style.whiteSpace = "nowrap";
      q.n.setAttribute("data-ck-lines", String(sp.k > 0 ? 2 : 1));
      q.n.setAttribute("data-ck-group", o.group || "rotulos");
      if (lines === 2 && sp.k === 0) q.n.setAttribute("data-ck-single", "1");   // una sola palabra: no se puede partir
    });
    return { px, lines };
  }
  const PUNCT = /^[\s.,;:!?¡¿…«»"'()\-–—]+$/;
  function isPunct(t) { return PUNCT.test(String(t)); }
  // Medidas relativas a un nodo base (tras cargar fuentes y ANTES de crear tweens).
  function rel(n, base) {
    const a = n.getBoundingClientRect(), b = base.getBoundingClientRect();
    return { x: a.left - b.left, y: a.top - b.top, w: a.width, h: a.height };
  }
  const css = `
  .gx-area{position:absolute;box-sizing:border-box;pointer-events:none}
  .gx-backdrop{position:absolute;overflow:hidden;pointer-events:none}
  .gx-bd-black{background:#050506}
  .gx-bd-black::after{content:"";position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 45%,rgba(0,0,0,0) 40%,rgba(0,0,0,.55) 100%)}
  .gx-bd-navy{background:var(--ck-navy)}
  .gx-bd-navy::after{content:"";position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 40%,rgba(0,0,0,0) 45%,rgba(0,0,0,.45) 100%)}
  .gx-bd-paper{background:#EEECE7}
  .gx-bd-paper::after{content:"";position:absolute;inset:0;background:radial-gradient(110% 75% at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.22) 100%)}
  .gx-grain{position:absolute;inset:-100px;opacity:.09;mix-blend-mode:screen;background-size:240px 240px;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' seed='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.6 -.35'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>")}
  .gx-bd-paper .gx-grain{mix-blend-mode:multiply;opacity:.16;filter:invert(1)}
  /* negro profesional: casi negro con una key muy suave arriba-centro y grano fino */
  .gx-bd-ink{background:#0B0B0C}
  .gx-bd-ink::before{content:"";position:absolute;inset:0;background:radial-gradient(70% 45% at 50% 34%,rgba(255,255,255,.055) 0%,rgba(255,255,255,0) 70%)}
  .gx-bd-ink::after{content:"";position:absolute;inset:0;background:radial-gradient(130% 90% at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.35) 100%)}
  .gx-bd-ink .gx-grain{opacity:.05}
  .gx-bd-white{background:#F7F7F5}
  .gx-bd-white::after{content:"";position:absolute;inset:0;background:radial-gradient(120% 85% at 50% 45%,rgba(0,0,0,0) 60%,rgba(0,0,0,.10) 100%)}
  .gx-bd-white .gx-grain{mix-blend-mode:multiply;opacity:.07;filter:invert(1)}
  .gx-bd-accent{background:var(--ck-accent)}
  .gx-bd-accent::after{content:"";position:absolute;inset:0;background:radial-gradient(120% 85% at 50% 45%,rgba(0,0,0,0) 55%,rgba(120,70,0,.18) 100%)}
  .gx-bd-accent .gx-grain{mix-blend-mode:multiply;opacity:.12;filter:invert(1)}
  /* variables de contraste por tema: los componentes SOLO usan estas para texto, tarjetas y destacados */
  .gx-th-dark{--g-fg:#FFFFFF;--g-muted:rgba(255,255,255,.58);--g-card:#18181B;--g-card-fg:#FFFFFF;--g-line:rgba(255,255,255,.09);
    --g-hi:var(--ck-accent);--g-hi-fg:var(--ck-ink);--g-hi-text:var(--ck-accent);--g-hero:var(--ck-accent);
    --g-solid:#F4F2EE;--g-solid-fg:var(--ck-ink);--g-ghost:rgba(255,255,255,.045);--g-ghost-line:rgba(255,255,255,.24);
    --g-track:rgba(255,255,255,.08);--g-bar:rgba(255,255,255,.5);--g-bar-dim:rgba(255,255,255,.16);
    --g-eyebrow:rgba(255,255,255,.5);--g-pick:var(--ck-accent);--g-pick-fg:#0B0B0C;
    --g-inv:#F4F4F1;--g-inv-fg:#0B0B0C;--g-inv-key:#77777D;--g-tab-bg:#E2E2DE;--g-tab-fg:#55555B;
    --g-dim-chip:#141416;--g-card-edge:inset 0 0 0 1px rgba(255,255,255,.07),inset 0 1px 0 rgba(255,255,255,.06);
    --g-shadow:0 1px 2px rgba(0,0,0,.4),0 14px 34px rgba(0,0,0,.42),0 36px 70px rgba(0,0,0,.3);
    --g-shadow-chip:0 1px 2px rgba(0,0,0,.35),0 8px 20px rgba(0,0,0,.32);
    --g-shadow-ink:0 1px 2px rgba(0,0,0,.3),0 12px 28px rgba(0,0,0,.36);
    --g-tshadow:0 2px 3px rgba(0,0,0,.38),0 4px 18px rgba(0,0,0,.45)}
  .gx-th-light,.gx-th-accent{--g-eyebrow:#8D877F;--g-pick:#161514;--g-pick-fg:#FFFFFF;--g-inv:#161514;--g-inv-fg:#FFFFFF;--g-inv-key:var(--ck-accent);
    --g-tab-bg:#EEEDE9;--g-tab-fg:#8D877F;--g-bar-dim:rgba(22,21,20,.13);--g-card-edge:inset 0 0 0 1px rgba(22,21,20,.04)}
  .gx-th-light,.gx-th-accent{--g-shadow:0 1px 1px rgba(30,24,14,.035),0 3px 8px rgba(30,24,14,.042),0 14px 32px rgba(30,24,14,.063),0 42px 80px -24px rgba(30,24,14,.112);
    --g-shadow-chip:0 1px 1px rgba(30,24,14,.042),0 2px 6px rgba(30,24,14,.042),0 8px 18px rgba(30,24,14,.049);
    --g-shadow-ink:0 2px 2px rgba(0,0,0,.084),0 10px 24px rgba(40,20,10,.154),0 26px 50px -12px rgba(40,20,10,.196)}
  .gx-tint-pink{--g-shadow:0 1px 1px rgba(110,18,52,.049),0 3px 8px rgba(110,18,52,.056),0 14px 32px rgba(110,18,52,.084),0 42px 80px -24px rgba(110,18,52,.154) !important;
    --g-shadow-chip:0 1px 1px rgba(110,18,52,.056),0 2px 6px rgba(110,18,52,.056),0 8px 18px rgba(110,18,52,.07) !important;
    --g-shadow-ink:0 2px 2px rgba(0,0,0,.084),0 10px 24px rgba(60,6,26,.196),0 26px 50px -12px rgba(60,6,26,.245) !important;
    --g-dim-chip:rgba(255,255,255,.78)}
  .gx-th-light{--g-fg:var(--ck-ink);--g-muted:rgba(15,13,16,.56);--g-card:#FFFFFF;--g-card-fg:var(--ck-ink);--g-line:rgba(15,13,16,.10);
    --g-hi:var(--ck-accent);--g-hi-fg:var(--ck-ink);--g-hi-text:var(--ck-ink);--g-hero:var(--ck-ink);
    --g-solid:#FFFFFF;--g-solid-fg:var(--ck-ink);--g-ghost:rgba(15,13,16,.07);--g-ghost-line:rgba(15,13,16,.36);
    --g-track:rgba(15,13,16,.08);--g-bar:rgba(15,13,16,.32);
    --g-shadow:0 1px 2px rgba(15,13,16,.07),0 8px 22px rgba(15,13,16,.07),0 24px 50px rgba(15,13,16,.07);
    --g-tshadow:none}
  .gx-th-accent{--g-fg:var(--ck-ink);--g-muted:rgba(15,13,16,.62);--g-card:#FFFFFF;--g-card-fg:var(--ck-ink);--g-line:rgba(15,13,16,.12);
    --g-hi:var(--ck-ink);--g-hi-fg:#FFFFFF;--g-hi-text:var(--ck-ink);--g-hero:var(--ck-ink);
    --g-solid:#FFFFFF;--g-solid-fg:var(--ck-ink);--g-ghost:rgba(15,13,16,.09);--g-ghost-line:rgba(15,13,16,.40);
    --g-track:rgba(15,13,16,.12);--g-bar:rgba(15,13,16,.4);
    --g-shadow:0 1px 2px rgba(80,50,0,.112),0 10px 26px rgba(80,50,0,.112);--g-tshadow:none}
  .gx-w{display:inline-block;white-space:nowrap}
  .gx-ch{display:inline-block}
  .gx-logo{background:center/contain no-repeat}
  .gx-logo-missing{border-radius:22%;box-shadow:inset 0 0 0 3px rgba(255,255,255,.25)}
  /* iconos de estado (kit v13): oro del kit en glifos de línea (degradado de los iconos 3D) y en assets (duotono) */
  .gx-icon{position:relative;flex:none}
  .gx-icon-img{position:absolute;inset:0;background:center/contain no-repeat}
  .gx-tint-gold{filter:url(#gx-gold) drop-shadow(0 6px 10px rgba(40,26,0,.22))}
  .gx-tint-silver{filter:url(#gx-silver) drop-shadow(0 6px 10px rgba(0,0,0,.22))}
  .gx-glyph{position:absolute;inset:0;width:100%;height:100%;overflow:visible;fill:none;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
  .gx-icon-gold .gx-glyph{stroke:url(#gx-gold-g)}.gx-icon-gold .gx-glyph .f{fill:url(#gx-gold-g);stroke:none}
  .gx-icon-ink .gx-glyph{stroke:#161514}.gx-icon-ink .gx-glyph .f{fill:#161514;stroke:none}
  .gx-icon-white .gx-glyph{stroke:#FFFFFF}.gx-icon-white .gx-glyph .f{fill:#FFFFFF;stroke:none}
  .gx-glyph-target circle{stroke:none}.gx-glyph-target .gx-t-f{fill:url(#gx-gold-g)}.gx-glyph-target .gx-t-p{fill:#F7F7F5}
  .gx-glyph-target .gx-t-d{fill:#54410F}
  .gx-wire-ol{fill:none;stroke:#161514;stroke-linecap:round;stroke-linejoin:round}
  .gx-wire{fill:none;stroke:var(--ck-accent);stroke-linecap:round;stroke-linejoin:round}
  .gx-th-dark .gx-wire-ol{stroke:rgba(255,255,255,.92)}
  .gx-lp{display:inline-block;text-align:inherit;white-space:nowrap}
  .gx-pulse{position:absolute;border-radius:50%;background:var(--ck-accent);box-shadow:0 0 0 4px #161514,0 4px 10px rgba(0,0,0,.25);pointer-events:none;z-index:6}
  .gx-th-dark .gx-pulse{box-shadow:0 0 0 4px #FFFFFF,0 4px 10px rgba(0,0,0,.35)}
  `;
  let st = document.querySelector('style[data-gx="kit"]');
  if (!st) { st = document.createElement("style"); st.setAttribute("data-gx", "kit"); (document.head || document.documentElement).appendChild(st); }
  st.textContent = css;
  // otra copia de la MISMA versión sin textIn: se conservan sus extras y manda esta (nunca un kit a medias)
  CK.gx = Object.assign({}, PREV && (PREV.v || 0) >= KIT_V ? PREV : {}, { v: KIT_V, FPS, f, T, R, nodot, mblurOf, streak, land, settle, easeTokens, cutIn, ev, themeOfKind, stage, canvasOf, themeOf, out, outBg, bgIn, cssv, isPunct, contentH, autoscale, tfit, upper, EASE, eases, el, svg, area, backdrop, grain, ft, split, fit, cue, num, rng, hash, exit,
    countText, swapText, mediaSrc, logo, color, rel, originOf, zOf, GOLD, defs, GLYPHS, glyph, icon,
    polyLen, wire, drawWire, pulse, pulseDot, lineParity, TXT, hasText, textIn, maskIn, blink });
})(window.CK = window.CK || {});
// ── gx:end ──
(function (CK) {
  const gx = CK.gx;
  const { f, ft, T, R } = gx;

  // filtros SVG compartidos: plata (monocromo con algo de contraste) y duotono oro (sombras ámbar → luces oro claro)
  function ensureFilters() {
    if (document.getElementById("og-silver")) return;
    const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.setAttribute("width", "0"); s.setAttribute("height", "0");
    s.style.cssText = "position:absolute;width:0;height:0;overflow:hidden";
    s.innerHTML = `
      <filter id="og-silver" color-interpolation-filters="sRGB">
        <feColorMatrix type="saturate" values="0"/>
        <feComponentTransfer><feFuncR type="table" tableValues="0.06 0.93"/><feFuncG type="table" tableValues="0.06 0.93"/><feFuncB type="table" tableValues="0.07 0.95"/></feComponentTransfer>
      </filter>
      <filter id="og-gold" color-interpolation-filters="sRGB">
        <feColorMatrix type="saturate" values="0"/>
        <feComponentTransfer><feFuncR type="table" tableValues="0.16 1.0"/><feFuncG type="table" tableValues="0.10 0.87"/><feFuncB type="table" tableValues="0.0 0.42"/></feComponentTransfer>
      </filter>`;
    (document.body || document.documentElement).appendChild(s);
  }

  // Estado FINAL de una instancia de la rejilla (para `carry`): por baldosa {op, sc, ring, gold}. Solo focus/combine/all
  // (pick mueve y escala la elegida: no se arrastra). Devuelve null si no hay estado que continuar.
  function endState(P, n) {
    if (!P) return null;
    const mode = P.mode || "all";
    const S = Array.from({ length: n }, () => ({ op: 1, sc: 1, ring: 0, gold: 0 }));
    if (mode === "focus" || mode === "combine") {
      const fi = Math.max(0, Math.min(n - 1, (P.focus | 0) - 1));
      const done = new Set((P.done || []).map((k) => (k | 0) - 1));
      const lit = new Set((mode === "combine" ? (P.also || []) : (P.also || [])).map((k) => (k | 0) - 1));
      S.forEach((x, i) => {
        if (i === fi) Object.assign(x, { op: 1, sc: 1.12, ring: 1, gold: 1 });
        else if (lit.has(i)) Object.assign(x, { op: 1, sc: 1.04, ring: 1, gold: 1 });
        else Object.assign(x, { op: done.has(i) ? 0.62 : 0.3, sc: 0.96 });
      });
      return S;
    }
    if (mode === "all") {
      const cues = P._cues || {};
      const walk = Array.from({ length: n }, (_, i) => cues["i" + i]).some((v) => v != null);
      if (walk && cues.all == null) { const last = n - 1; S[last].ring = 1; S[last].gold = 1; }
      return S;
    }
    return null;
  }
  // `carry_from` explícito ({focus, done, also} o un número) o la instancia ANTERIOR de la rejilla en el plan
  function carriedState(props, ctx, n) {
    const cf = props.carry_from;
    if (cf != null) return endState(typeof cf === "number" ? { mode: "focus", focus: cf, done: Array.from({ length: Math.max(0, cf - 1) }, (_, k) => k + 1) } : Object.assign({ mode: "focus" }, cf), n);
    if (!props.carry) return null;
    const me = ctx.item || {};
    const prev = ((ctx.spec && ctx.spec.items) || []).filter((it) => it.component === "viz.offer_grid" && it.id !== me.id && it.t0 < (me.t0 || 0) - 1e-3)
      .sort((a, b) => a.t0 - b.t0).pop();
    if (!prev || ((prev.props && prev.props.items) || []).length !== n) return null;
    const S = endState(Object.assign({}, prev.props, { _cues: prev.cues || {} }), n);
    if (S) S.prev = prev.props;
    return S;
  }
  // firma de la banda (ordinal + nombre + geometría): si la instancia anterior enseñaba la MISMA banda, se arrastra tal cual
  function bandSig(P) {
    if (!P || ["focus", "combine"].indexOf(P.mode) < 0) return null;
    const items = P.items || [], fi = Math.max(0, Math.min(items.length - 1, (P.focus | 0) - 1));
    const it = items[fi] || {};
    return JSON.stringify([P.show_ordinal !== false ? P.ordinal || "" : null, P.show_name !== false ? (P.name != null ? P.name : it.label || "") : null,
      P.ordinal_style || "", P.ordinal_px || 0, P.name_px || 0, P.name_gap == null ? null : P.name_gap, P.tile_px || 0, P.band_pos || "",
      P.ordinal_bar ? 1 : 0]);
  }

  CK.register("viz.offer_grid", {
    mount(root, props, ctx) {
      const E = gx.eases(ctx);
      ensureFilters();
      gx.defs();
      const st = gx.stage(root, ctx, props, "og");
      // `band_pos: "top"`: la banda de texto va ARRIBA (a 950 px, por encima de y=1000) y la
      // rejilla debajo, estrecha (≤ 696 px en la «T»), hasta el raíl de subtítulos; sin `top`, la geometría de siempre
      const top = props.band_pos === "top";
      const A = top ? st.A : gx.upper(st.A), bd = st.bd;
      const mode = ["all", "focus", "pick", "combine"].indexOf(props.mode) >= 0 ? props.mode : "all";
      const banded = mode === "focus" || mode === "combine";          // ordinal + nombre en la banda
      const items = (props.items || []).slice(0, 9).map((x) => (typeof x === "string" ? { label: x } : x || {}));
      const n = items.length;
      const fi = Math.max(0, Math.min(n - 1, (props.focus | 0) - 1));
      const showName = banded && props.show_name !== false;
      const showOrd = banded && props.show_ordinal !== false;
      // (regla de estilo: nunca serif cursiva): «serif» se acepta (planes antiguos) y se pinta como «sans»
      const serifOrd = false;
      // `ordinal_style: "sans"`: ordinal grande en Montserrat 900 con la «ª» pequeña y elevada («1.ª»);
      // sin `ordinal_style`, el «N/6» pequeño de siempre
      const sansOrd = props.ordinal_style === "sans" || props.ordinal_style === "serif";
      const bigOrd = serifOrd || sansOrd;
      const s = Math.max(0.75, Math.min(1.1, A.w / 950));
      A.node.style.setProperty("--s", s);
      // `cols` opcional (2|3|4); sin él, 3 como siempre (4 preguntas en 2×2)
      const cols = [2, 3, 4].indexOf(props.cols) >= 0 ? props.cols : 3, rows = Math.ceil(n / cols);
      let bandH, gap, gapB, tsz, y0, bandTop;
      const ordPx = showOrd ? R((props.ordinal_px || (serifOrd ? 150 : sansOrd ? 140 : 44)) * s) : 0;
      const namePx = R((props.name_px || 96) * s);
      // `name_gap`: aire entre el ordinal y el nombre (la mitad) y entre la banda y la rejilla (entero)
      const ng = typeof props.name_gap === "number" ? R(props.name_gap * s) : null;
      const bandGap = ng != null ? Math.max(R(8 * s), R(ng * 0.5)) : R(8 * s);
      // combine: remate opcional DEBAJO de la rejilla (cue «note»)
      const notePx = R((props.note_px || 64) * s);
      const noteGap = ng != null ? ng : R(30 * s);
      // con `carry`, la geometría es la de la rejilla anterior (sin reservar el remate): nada salta en el corte
      const carrying = props.carry || props.carry_from != null;
      const noteH = mode === "combine" && props.note && top && !carrying ? noteGap + R(notePx * 1.2) : 0;
      if (top) {
        // ── geometría arriba: banda (ordinal + nombre, o kicker + sub) y debajo la rejilla, centrado en la región útil
        const railLim = ctx.railY && ctx.railY > A.y + 200 ? ctx.railY - 60 : A.y + A.h;
        const regH = Math.max(200, Math.min(A.h, railLim - A.y));
        gap = R(18 * s); gapB = ng != null ? ng : R(30 * s);
        if (banded) bandH = (showOrd ? R(ordPx * (bigOrd ? 0.95 : 1.1)) + bandGap : 0) + (showName ? R(namePx * 1.12) : 0);
        else bandH = (props.kicker ? R(76 * s * 1.12) : 0) + (props.sub ? R(8 * s) + R(52 * s * 1.15) : 0);
        const wMax = A.tee ? A.wLow : A.w;
        const hFit = (regH - bandH - (bandH ? gapB : 0) - noteH - (rows - 1) * gap) / rows;
        tsz = R(Math.min((wMax - (cols - 1) * gap) / cols, hFit, (props.tile_px || 240) * s));
        // `tee_rows` (a pantalla completa la rejilla de 3 + 2 quedaba en
        // los 696 px de debajo de y=1000 aunque su primera fila acaba por encima): en la «T», la primera fila (la ancha) usa
        // los 950 px de la banda alta y solo la última, más corta, tiene que caber en wLow. Si con ese tamaño la primera fila
        // no acaba por encima de y=1000, se queda como antes. Sin la prop, igual que antes.
        const lastN = n - (rows - 1) * cols;
        if (props.tee_rows && A.tee && rows === 2 && lastN < cols) {
          const t2 = R(Math.min((A.w - (cols - 1) * gap) / cols, (A.wLow - (lastN - 1) * gap) / lastN, hFit, (props.tile_px || 240) * s));
          const bt2 = R(Math.max(0, (regH - (bandH + (bandH ? gapB : 0) + 2 * t2 + gap + noteH)) / 2));
          if (bt2 + bandH + (bandH ? gapB : 0) + t2 <= A.yLow) tsz = Math.max(tsz, t2);
        }
        const gh0 = rows * tsz + (rows - 1) * gap, blockH = bandH + (bandH ? gapB : 0) + gh0 + noteH;
        bandTop = R(Math.max(0, (regH - blockH) / 2));
        y0 = bandTop + bandH + (bandH ? gapB : 0);
      } else {
        // ── geometría (solo depende del área): rejilla 3×2 arriba + banda de texto abajo
        bandH = R(Math.max(150, A.h * 0.27)); gap = R(22 * s); gapB = R(22 * s);
        tsz = R(Math.min((A.w - (cols - 1) * gap) / cols, (A.h - bandH - gapB - (rows - 1) * gap) / rows, 240 * s));
        const gh0 = rows * tsz + (rows - 1) * gap, blockH = gh0 + gapB + bandH;
        y0 = R((A.h - blockH) / 2); bandTop = y0 + gh0 + gapB;
      }
      const gw = cols * tsz + (cols - 1) * gap, gh = rows * tsz + (rows - 1) * gap, x0 = R((A.w - gw) / 2);
      const wrap = gx.el("div", "og-wrap", A.node);
      // `cam`: la rejilla (baldosas, conectores, aro viajero) dentro de su propia «cámara» (empuje suave a la activa);
      // la banda de texto queda fuera (no se mueve)
      const cam = gx.el("div", "og-cam", wrap);
      const glow = gx.el("div", "og-glow", cam);
      // conectores de `combine` (por debajo de las baldosas)
      const wires = mode === "combine" ? gx.svg("svg", { class: "og-wires", width: A.w, height: A.h + 200, viewBox: `0 0 ${A.w} ${A.h + 200}` }, cam) : null;
      const tiles = items.map((it, i) => {
        // una última fila incompleta va CENTRADA (3+3+2 simétrico,
        // por simetría), no pegada a la izquierda; con 6 y 9 baldosas (filas completas) no cambia nada
        const r = Math.floor(i / cols), rowN = Math.min(cols, n - r * cols), c = (i % cols) + (cols - rowN) / 2;
        const slot = gx.el("div", "og-slot", cam);
        Object.assign(slot.style, { left: (x0 + c * (tsz + gap)) + "px", top: (y0 + r * (tsz + gap)) + "px", width: tsz + "px", height: tsz + "px" });
        const t = gx.el("div", "og-tile", slot);
        gx.el("div", "og-glass", t);
        const ring = gx.el("div", "og-ring", t);
        const ringW = gx.el("div", "og-ring og-ring-w", t);   // «same»: las seis marcadas a la vez, sin foco
        // `items[].media` = miniatura REAL del resultado (fotograma recortado)
        // en vez del icono del kit: en reposo en gris, a color en el foco (mismos estados que plata/oro)
        const th = it.media || null;
        const icS = th ? gx.logo(t, ctx, th, "og-ic og-thumb og-thumb-rest") : gx.logo(t, ctx, it.icon, "og-ic og-ic-silver");
        const icC = th ? gx.logo(t, ctx, th, "og-ic og-thumb og-thumb-hot")
          : gx.logo(t, ctx, it.icon, "og-ic og-ic-hot" + (props.icon_focus === "color" ? "" : " og-ic-gold")); // por defecto, duotono oro
        return { slot, t, ring, ringW, icS, icC, c, r, cx: x0 + c * (tsz + gap) + tsz / 2, cy: y0 + r * (tsz + gap) + tsz / 2 };
      });
      // aro viajero (`carry`): el foco viaja de la baldosa anterior a la nueva
      const trav = gx.el("div", "og-ring og-trav", cam);
      trav.style.cssText = `left:0;top:0;right:auto;bottom:auto;width:${tsz}px;height:${tsz}px`;
      // banda de texto (fija): kicker (+ sub) (all/pick) · ordinal + nombre (focus/combine)
      const band = gx.el("div", "og-band" + (top ? " og-band-top" : ""), wrap);
      Object.assign(band.style, { top: bandTop + "px", height: bandH + "px" });
      if (top && ng != null) band.style.gap = bandGap + "px";
      const kick = (!banded && props.kicker) ? gx.el("div", "og-kicker", band, props.kicker) : null;
      const sub = (!banded && props.sub) ? gx.el("div", "og-sub", band, props.sub) : null;
      const ord = showOrd ? gx.el("div", "og-ord" + (serifOrd ? " og-ord-serif" : sansOrd ? " og-ord-sans" : ""), band, (props.ordinal || `${fi + 1}/${n}`)) : null;
      if (ord && sansOrd) {   // «1.ª» → número + punto (más pequeño) + «a» volada a 0,44 em alineada arriba
        const m = String(props.ordinal || "").trim().match(/^(\d+)(\.?)([ªºao])$/);
        if (m) {
          ord.textContent = "";
          gx.el("span", "og-ord-n", ord, m[1]);
          if (m[2]) gx.el("span", "og-ord-dot", ord, ".");
          gx.el("span", "og-ord-sup", ord, m[3] === "ª" ? "a" : m[3] === "º" ? "o" : m[3]);
          // `ordinal_bar`: la «o» volada sin raya se leía «1.°» (grado);
          // con la opción lleva la raya de debajo del indicador ordinal. Sin la opción, igual que antes.
          if (props.ordinal_bar) ord.classList.add("og-ord-bar");
        }
      }
      if (ord && bigOrd) ord.style.fontSize = ordPx + "px";
      const nameTxt = props.name != null ? props.name : ((items[fi] && items[fi].label) || "");
      const name = showName ? gx.el("div", "og-name", band, nameTxt) : null;
      // `name_tone: "gold"` / `name_weight`: el nombre
      // (aquí, el USO bajo el repo) en el oro oscuro del kit y con su peso, para que no se lea con el ordinal como un solo
      // nombre («Superpowers Desarrollo»). Sin las props, igual que antes
      if (name && props.name_tone === "gold") name.style.color = "#C99A12";
      if (name && Number(props.name_weight) >= 400) name.style.fontWeight = String(Math.min(900, Number(props.name_weight) | 0));
      // remate de `combine` debajo de la rejilla (con máscara: sube desde dentro)
      let note = null, noteIn = null;
      if (mode === "combine" && props.note) {
        note = gx.el("div", "og-note", wrap);
        noteIn = gx.el("div", "og-note-in", note, props.note);
        // debajo de la rejilla si cabe por encima del raíl de subtítulos y de la zona segura; si no (con `carry` la rejilla no
        // se encoge), el remate RELEVA a la banda: el ordinal y el nombre salen y el remate sube en su sitio
        const lim = Math.min(A.h, ctx.railY && ctx.railY > A.y + 200 ? ctx.railY - 60 - A.y : A.h);
        const below = top && y0 + gh + noteGap + R(notePx * 1.2) <= lim;
        if (below) Object.assign(note.style, { top: (y0 + gh + noteGap) + "px", height: R(notePx * 1.2) + "px" });
        else { Object.assign(note.style, { top: bandTop + "px", height: bandH + "px", alignItems: "center" }); note.dataset.swap = "1"; }
      }
      // cierre «elige una» sin decir cuál (`pick_glyph: "target"`): la elegida enseña una diana en el ORO DEL KIT
      // en vez de su icono
      const target = mode === "pick" && props.pick_glyph === "target" && tiles[fi]
        ? gx.icon(tiles[fi].t, ctx, { glyph: "target", tone: "gold" }, "og-target") : null;
      Object.assign(glow.style, { width: R(tsz * 2.4) + "px", height: R(tsz * 2.4) + "px" });
      // `pick_from: "center"` (la diana nacía en la baldosa 3 y
      // viajaba al centro: se leía «elige la tercera»): una baldosa PROPIA con la diana, en el centro de la rejilla, que
      // nace mientras las cinco se apagan (ninguna crece). Solo con `pick_glyph: "target"`. Sin la prop, igual que antes
      let pickC = null;
      if (mode === "pick" && props.pick_from === "center" && props.pick_glyph === "target") {
        const slotC = gx.el("div", "og-slot og-pickc", cam);
        Object.assign(slotC.style, { left: R(x0 + gw / 2 - tsz / 2) + "px", top: R(y0 + gh / 2 - tsz / 2) + "px", width: tsz + "px", height: tsz + "px", zIndex: "6" });
        const tC = gx.el("div", "og-tile", slotC);
        gx.el("div", "og-glass", tC);
        const ringC = gx.el("div", "og-ring", tC);
        gx.icon(tC, ctx, { glyph: "target", tone: "gold" }, "og-target");
        pickC = { slot: slotC, ring: ringC };
        gsap.set(slotC, { opacity: 0 });
        gsap.set(ringC, { opacity: 0 });
      }
      const tFocus = tiles[fi];
      if (tFocus) gsap.set(glow, { x: R(tFocus.cx - tsz * 1.2), y: R(tFocus.cy - tsz * 1.2), opacity: 0 });
      // estado inicial: `carry` (el de la instancia anterior), `tiles: "in"` (puestas, en reposo) o vacío
      const S0 = carriedState(props, ctx, n);
      const tilesIn = !!S0 || props.tiles === "in";
      // banda arrastrada: la anterior enseñaba exactamente la misma (ordinal, nombre y geometría) → ya está en el corte
      const bandCarry = !!(S0 && S0.prev && banded && bandSig(S0.prev) === bandSig(Object.assign({}, props, { mode })));
      // cámara de la rejilla como (x, y, escala) con origen 0 0: el empuje de la instancia anterior se arrastra y la
      // cámara VIAJA de la baldosa anterior a la nueva (sin saltos en el corte)
      const PUSH = 1.035, ID = { x: 0, y: 0, scale: 1 };
      const camAt = (x, k) => ({ x: R(x.cx * (1 - k)), y: R(x.cy * (1 - k)), scale: k });
      const pv = S0 && S0.prev;
      const pvPush = pv && pv.mode === "focus" && pv.push !== false && (pv.carry || pv.carry_from != null || pv.push === true);
      const cam0 = pvPush ? camAt(tiles[Math.max(0, Math.min(n - 1, (pv.focus | 0) - 1))], PUSH) : ID;
      gsap.set(cam, Object.assign({ transformOrigin: "0px 0px" }, cam0));
      gsap.set(tiles.map((x) => x.icC), { opacity: 0 });
      gsap.set(tiles.map((x) => x.ring).concat(tiles.map((x) => x.ringW), [trav]), { opacity: 0 });
      gsap.set(tiles.map((x) => x.t), { opacity: 0 });
      if (tilesIn) tiles.forEach((x, i) => {
        const z = S0 ? S0[i] : { op: 1, sc: 1, ring: 0, gold: 0 };
        gsap.set(x.t, { opacity: z.op, scale: z.sc });
        gsap.set(x.ring, { opacity: z.ring });
        gsap.set(x.icC, { opacity: z.gold });
      });
      [kick, sub, ord, name, target, noteIn].filter(Boolean).forEach((nd) => gsap.set(nd, { opacity: 0 }));
      const doneSet = new Set((props.done || []).map((k) => (k | 0) - 1));
      const alsoIdx = (props.also || []).map((k) => (k | 0) - 1).filter((i) => i >= 0 && i < n && i !== fi);

      return {
        animate(tl, t0, t1, cues) {
          const ex = f(5);
          if (kick) gx.fit(kick, { max: Math.round(76 * s), min: top ? 52 : 64, width: A.w, lines: top ? 1 : 2 });
          if (sub) gx.fit(sub, { max: Math.round(52 * s), min: 40, width: A.w, lines: 1 });
          if (name) gx.fit(name, { max: top ? namePx : Math.round(96 * s), min: top ? 52 : 56, width: A.w, lines: 1 });
          if (ord) gx.fit(ord, bigOrd ? { max: ordPx, min: 90, width: A.w, lines: 1 } : { max: Math.round(44 * s), min: 34, width: A.w, lines: 1 });
          if (noteIn) gx.fit(noteIn, { max: note.dataset.swap === "1" ? Math.max(notePx, namePx) : notePx, min: 48, width: note.dataset.swap === "1" ? A.w : top && A.tee ? A.wLow : A.w, lines: 1 });
          const C = (k, d) => gx.cue(cues, k, d);
          const tS = gx.settle(ctx, t0);
          gx.ev(ctx, "enter", tS);
          // estado en el corte: lo que traiga `carry`/`tiles: "in"` ya está en el fotograma 0 (sin texto)
          const st0 = tiles.map((x, i) => (S0 ? S0[i] : { op: 1, sc: 1, ring: 0, gold: 0 }));
          if (tilesIn) tiles.forEach((x, i) => {
            tl.set(x.t, { opacity: st0[i].op, scale: st0[i].sc }, T(tS));
            tl.set(x.ring, { opacity: st0[i].ring }, T(tS));
            tl.set(x.icC, { opacity: st0[i].gold }, T(tS));
          });
          if (mode === "all") {
            // cascada corta: 6 baldosas en ≤0,4 s (6 f cada una, 1 f de stagger), en orden de lectura
            const tT = Math.max(tS, C("tiles", tS));
            // `i0…i5`: cada baldosa entra EN SU PALABRA («desarrollo web», «edición de vídeos»…) y queda en oro mientras
            // se nombra; al entrar la siguiente vuelve a plata (un solo foco). Sin esas cues, cascada corta.
            const own = tiles.map((_, i) => C("i" + i, null));
            const walk = own.some((v) => v != null);
            // walk: las 6 baldosas ya están en el corte como fantasma (el panel nunca está vacío) y cada una se
            // enciende del todo en su palabra
            const GH = 0.38;
            if (walk && !tilesIn) tl.set(tiles.map((x) => x.t), { opacity: GH, scale: 0.94, y: 0 }, T(tS));
            let prev = null;
            tiles.forEach((x, i) => {
              const at = walk ? Math.max(tS, own[i] != null ? own[i] : tT + i * 0.5) : tT + i * f(1);
              if (walk && !tilesIn) ft(tl, x.t, { opacity: GH, scale: 0.94, y: 0 }, { opacity: 1, scale: 1, y: 0, duration: f(6), ease: E.pop }, at);
              else if (walk) { ft(tl, x.t, { scale: 1 }, { scale: 1.06, duration: f(3), ease: E.enter }, at); ft(tl, x.t, { scale: 1.06 }, { scale: 1, duration: f(6), ease: E.pop }, at + f(3)); }
              else if (tilesIn) {   // ya están: la cascada es un pulso que recorre la rejilla (nada quieto, sin vacío)
                ft(tl, x.t, { scale: 1 }, { scale: 1.05, duration: f(3), ease: E.enter }, at);
                ft(tl, x.t, { scale: 1.05 }, { scale: 1, duration: f(6), ease: E.pop }, at + f(3));
              } else ft(tl, x.t, { opacity: 0, scale: 0.86, y: R(14 * s) }, { opacity: 1, scale: 1, y: 0, duration: f(6), ease: E.pop }, at);
              if (walk) {
                ft(tl, x.icC, { opacity: 0 }, { opacity: 1, duration: f(4), ease: E.enter }, at + f(1));
                ft(tl, x.ring, { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: f(5), ease: E.enter }, at + f(1));
                if (prev) {
                  ft(tl, prev.icC, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, at);
                  ft(tl, prev.ring, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, at);
                }
                prev = x;
              }
              gx.ev(ctx, "tile", at);
            });
            if (walk && prev) {
              const tEnd = C("all", null);   // «all»: el último foco se apaga (las seis quedan iguales)
              if (tEnd != null) {
                ft(tl, prev.icC, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tEnd);
                ft(tl, prev.ring, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tEnd);
              }
            }
            // «same»: «los mismos prompts…» → las seis baldosas se marcan A LA VEZ con un aro blanco (mismas condiciones)
            const tSame = C("same", null);
            if (tSame != null) {
              ft(tl, tiles.map((x) => x.ringW), { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, tSame);
              gx.ev(ctx, "focus", tSame);
            }
            // «lit» = remate: las seis se encienden A LA VEZ en oro (aro de oro
            // y su versión a color / en oro), en cascada de 1 f; el aro blanco de «same», si estaba, cede
            const tLit = C("lit", null);
            if (tLit != null) {
              tiles.forEach((x, k) => {
                const tk = tLit + k * f(1);
                ft(tl, x.icC, { opacity: 0 }, { opacity: 1, duration: f(5), ease: E.enter }, tk);
                ft(tl, x.ring, { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, tk);
                if (tSame != null) ft(tl, x.ringW, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tk);
              });
              gx.ev(ctx, "focus", tLit);
            }
            if (kick) {
              const tK = Math.max(tT + f(3), C("title", tT + f(4)));
              gx.textIn(tl, kick, tK);   // kit v14: 8 f, subida de 32 px y opacidad ≈ power2.out
            }
          } else if (!tilesIn) {
            // focus / pick / combine: la rejilla ya está en el corte (misma geometría que el gancho)
            tl.set(tiles.map((x) => x.t), { opacity: 1 }, T(tS));
            gx.cutIn(tl, cam, tS);
          }
          // ── foco en la baldosa N (focus y combine): desde su estado de partida (st0) al de foco
          let tN = null;
          if (banded && tFocus) {
            tN = Math.max(tS + f(2), C("number", C("hub", tS + f(3))));
            const z = st0[fi];
            // foco anterior (carry): la baldosa encendida y crecida (focus) o, si no, la última encendida (recorrido del gancho)
            const wasFocus = S0 && z.ring > 0.5 && z.sc > 1.08;
            let pi = S0 && !wasFocus ? st0.findIndex((q, i) => i !== fi && q.ring > 0.5 && q.sc > 1.08) : -1;
            if (S0 && !wasFocus && pi < 0) for (let i = n - 1; i >= 0; i--) if (i !== fi && st0[i].ring > 0.5) { pi = i; break; }
            // `keep_also` («1/3 → 2/3 → 3/3» apagaba las ya
            // elegidas en el corte y las volvía a encender 12–15 f después): en focus, las de `also` que ya venían
            // encendidas siguen encendidas (también la del foco anterior), sin pasar por el apagado
            const keepAlso = !!props.keep_also && mode === "focus";
            const keepLit = (i) => (mode === "combine" || keepAlso) && alsoIdx.indexOf(i) >= 0 && st0[i].ring > 0.5;   // ya encendidas: siguen
            // la N crece y se enciende (aro + icono en oro), las demás se apagan y pierden escala
            ft(tl, tFocus.t, { opacity: z.op, scale: z.sc }, { opacity: 1, scale: 1.12, duration: f(8), ease: E.pop }, tN);
            if (pi >= 0) {
              // `carry`: el foco VIAJA de la baldosa anterior a la nueva (aro viajero con estela) y la cámara empuja
              const P0 = tiles[pi];
              const tA = tN + f(11);
              if (!(keepAlso && keepLit(pi))) {
                tl.set(P0.ring, { opacity: 0 }, T(tN));
                ft(tl, P0.icC, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.exit }, tN);
              }
              // `carry_hop: "fade"` (el aro viajero pasaba por
              // encima de la baldosa de en medio): el aro se apaga en la anterior y se enciende en la nueva, sin viajar.
              // Sin la prop, el aro viaja como siempre
              const hop = props.carry_hop === "fade";
              if (hop) {
                if (!(keepAlso && keepLit(pi))) ft(tl, P0.ring, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tN);
                ft(tl, tFocus.ring, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, tN + f(3));
              } else {
              ft(tl, trav, { opacity: 1, x: R(P0.cx - tsz / 2), y: R(P0.cy - tsz / 2), scale: st0[pi].sc },
                { opacity: 1, x: R(tFocus.cx - tsz / 2), y: R(tFocus.cy - tsz / 2), scale: 1.12, duration: f(11), ease: E.move }, tN);
              gx.streak(tl, trav, tN + f(2), f(8), Math.abs(tFocus.cx - P0.cx) > Math.abs(tFocus.cy - P0.cy) ? "x" : "y", 10);
              tl.set(trav, { opacity: 0 }, T(tA));
              tl.set(tFocus.ring, { opacity: 1, scale: 1 }, T(tA));
              }
              ft(tl, tFocus.icC, { opacity: z.gold }, { opacity: 1, duration: f(5), ease: E.enter }, tA - f(3));
              ft(tl, tFocus.t, { scale: 1.12 }, { scale: 1.17, duration: f(3), ease: E.enter }, tA);
              ft(tl, tFocus.t, { scale: 1.17 }, { scale: 1.12, duration: f(7), ease: E.pop }, tA + f(3));
              gx.ev(ctx, "carry", tN);
            } else {
              ft(tl, tFocus.ring, { opacity: z.ring, scale: 1.08 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, tN);
              ft(tl, tFocus.icC, { opacity: z.gold }, { opacity: 1, duration: f(5), ease: E.enter }, tN + f(1));
            }
            ft(tl, glow, { opacity: 0 }, { opacity: 1, duration: f(8), ease: E.enter }, tN);
            // `done`: las ya contadas se quedan a media luz (se ve por dónde va la lista); las que faltan, apagadas
            tiles.forEach((x, i) => {
              if (i !== fi && keepAlso && keepLit(i)) {   // sigue encendida: solo vuelve a la escala de las elegidas
                ft(tl, x.t, { opacity: 1, scale: st0[i].sc }, { opacity: 1, scale: 1.04, duration: f(6), ease: E.enter }, tN);
                return;
              }
              if (i === fi || (keepLit(i) && i !== pi)) return;
              const q = st0[i], toOp = doneSet.has(i) ? 0.62 : 0.3;
              ft(tl, x.t, { opacity: q.op, scale: q.sc }, { opacity: toOp, scale: 0.96, duration: f(6), ease: E.enter }, tN);
              if (q.ring > 0.5 && i !== pi) ft(tl, x.ring, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tN);
              if (q.gold > 0.5 && i !== pi) ft(tl, x.icC, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tN);
            });
            // empuje de cámara suave hacia la activa (≤ 4 %): solo la rejilla, nunca la banda de texto; parte del empuje que
            // traía la instancia anterior (si lo había) y viaja a la baldosa nueva. En combine la cámara vuelve a 1 al abrirse
            if (cam0 !== ID) tl.set(cam, cam0, T(tS));
            const tP0 = tN + f(2), dP = Math.max(f(20), Math.min(2.4, t1 - tP0 - f(6)));
            if (mode === "focus" && props.push !== false && (S0 || props.push === true)) {
              if (dP > f(10)) ft(tl, cam, cam0, Object.assign({}, camAt(tFocus, PUSH), { duration: dP, ease: E.move }), tP0);
            } else if (cam0 !== ID) ft(tl, cam, cam0, Object.assign({}, ID, { duration: f(12), ease: E.move }), tP0);
            try { ctx.event("focus", Math.round(tN * 30) / 30, { step: fi + 1 }); } catch (e) { gx.ev(ctx, "focus", tN); }
            const tM = Math.max(tN + f(5), C("name", tN + 0.3));
            // `n0…nk`: el nombre se construye PALABRA A PALABRA mientras lo dice (antes caía
            // entero en su última palabra y dejaba 1–1,3 s solo con «N.ª»); cada palabra sube por su máscara en su cue
            const nWords = name && !bandCarry ? String(name.textContent).trim().split(/\s+/) : [];
            const nCues = nWords.map((_, k) => C("n" + k, null));
            const perWord = name && !bandCarry && nCues.some((v) => v != null);
            if (bandCarry) tl.set([ord, name].filter(Boolean), { opacity: 1 }, T(tS));   // continúa del plano anterior
            else {
              if (ord) gx.textIn(tl, ord, tN + f(2));
              if (name && perWord) {
                name.textContent = "";
                const inners = nWords.map((w, k) => {
                  const m = gx.el("span", "og-nw", name);
                  if (k < nWords.length - 1) name.appendChild(document.createTextNode(" "));
                  return gx.el("span", "og-nwi", m, w);
                });
                // cues que faltan: repartidas entre las vecinas conocidas (nunca antes de que entre el ordinal)
                const known = nCues.map((v, k) => [k, v]).filter(([, v]) => v != null);
                const at = nCues.map((v, k) => {
                  if (v != null) return v;
                  const pr = known.filter(([j]) => j < k).pop(), nx = known.find(([j]) => j > k);
                  if (pr && nx) return pr[1] + (nx[1] - pr[1]) * (k - pr[0]) / (nx[0] - pr[0]);
                  return pr ? pr[1] + (k - pr[0]) * 0.22 : nx[1] - (nx[0] - k) * 0.22;
                }).map((v, k, a) => Math.max(tN + f(3), v));
                for (let k = 1; k < at.length; k++) at[k] = Math.max(at[k], at[k - 1] + f(2));
                tl.set(name, { opacity: 1, y: 0 }, T(at[0]));
                gsap.set(inners, { yPercent: 110, opacity: 0 });
                inners.forEach((w, k) => gx.maskIn(tl, w, at[k]));
                gx.ev(ctx, "name", at[0]);
              } else if (name) { gx.textIn(tl, name, tM); gx.ev(ctx, "name", tM); }
            }
            // `also` (cue «also», solo focus): otras baldosas se encienden a la vez que la del foco («combinar varias
            // de las anteriores»), en cascada corta, con su aro y el icono en oro
            if (mode === "focus" && alsoIdx.length) {
              const tA = Math.max(tN + f(10), C("also", tM + 0.6));
              alsoIdx.forEach((i, k) => {
                if (keepAlso && keepLit(i)) return;   // ya encendida desde el corte
                const x = tiles[i], at = tA + k * f(2);
                ft(tl, x.t, { opacity: doneSet.has(i) ? 0.62 : 0.3, scale: 0.96 }, { opacity: 1, scale: 1.04, duration: f(7), ease: E.pop }, at);
                ft(tl, x.ring, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, at);
                ft(tl, x.icC, { opacity: 0 }, { opacity: 1, duration: f(5), ease: E.enter }, at + f(1));
              });
              gx.ev(ctx, "focus", tA);
            }
            // ── combine: la rejilla se ABRE (las baldosas se separan para dejar canales) y cada pieza de `also`
            //    se enciende en SU cue (c0…), lanza un conector de circuito (tinta + oro, por los canales, en ángulo recto)
            //    hasta el foco y un pulso lo recorre; el foco late al recibir cada pulso y GIRA al recibir el último; los
            //    pulsos siguen recorriendo el circuito hasta el final del plano; remate debajo en «note»
            if (mode === "combine" && alsoIdx.length) {
              const hub = tFocus;
              // geometría abierta: mismo encuadre (ancho de la rejilla), baldosas al 78 % y canales de 0,55 × baldosa
              const gcx = x0 + gw / 2, gcy = y0 + gh / 2, t2 = gw / (cols + (cols - 1) * 0.55), p2 = t2 * 1.55, k2 = t2 / tsz;
              const open = tiles.map((x) => ({ cx: gcx + (x.c - (cols - 1) / 2) * p2, cy: gcy + (x.r - (rows - 1) / 2) * p2 }));
              const tSp = tN + (pi >= 0 ? f(12) : f(2));
              tiles.forEach((x, i) => {
                gsap.set(x.slot, { transformOrigin: "50% 50%" });
                ft(tl, x.slot, { x: 0, y: 0, scale: 1 }, { x: R(open[i].cx - x.cx), y: R(open[i].cy - x.cy), scale: k2, duration: f(12), ease: E.move }, tSp);
              });
              gx.ev(ctx, "spread", tSp);
              const colX = (c) => gcx + (c - (cols - 1) / 2 + 0.5) * p2;      // canal entre la columna c y la c+1
              const rowY = (r) => gcy + (r - (rows - 1) / 2 + 0.5) * p2;      // canal entre la fila r y la r+1
              const H = { c: hub.c, r: hub.r, cx: open[fi].cx, cy: open[fi].cy };
              const route = (i) => {
                const S = { c: tiles[i].c, r: tiles[i].r, cx: open[i].cx, cy: open[i].cy };
                if (S.r === H.r) {
                  const y = H.r < rows - 1 ? rowY(H.r) : rowY(H.r - 1);
                  return [[S.cx, S.cy], [S.cx, y], [H.cx, y], [H.cx, H.cy]];
                }
                if (S.c === H.c) {
                  const x = H.c < cols - 1 ? colX(H.c) : colX(H.c - 1);
                  return [[S.cx, S.cy], [x, S.cy], [x, H.cy], [H.cx, H.cy]];
                }
                const y = S.r < H.r ? rowY(H.r - 1) : rowY(H.r), x = S.c < H.c ? colX(S.c) : colX(S.c - 1);
                return [[S.cx, S.cy], [x, S.cy], [x, y], [H.cx, y], [H.cx, H.cy]];
              };
              const lw = Math.max(5, R(6 * s)), lo = Math.max(10, R(13 * s)), ds = R(Math.max(22, 28 * s));
              let last = Math.max(tM + f(6), tSp + f(10)), tLast = null;
              const loops = [];
              alsoIdx.forEach((i, k) => {
                const x = tiles[i];
                const at = Math.max(tSp + f(12) + k * f(4), C("c" + k, last + 0.35));
                last = at;
                // la pieza se enciende (si ya venía encendida del plano anterior, late)
                if (keepLit(i) && i !== pi) {
                  ft(tl, x.t, { scale: 1.04 }, { scale: 1.12, duration: f(3), ease: E.enter }, at);
                  ft(tl, x.t, { scale: 1.12 }, { scale: 1.04, duration: f(7), ease: E.pop }, at + f(3));
                } else {
                  ft(tl, x.t, { opacity: doneSet.has(i) ? 0.62 : 0.3, scale: 0.96 }, { opacity: 1, scale: 1.04, duration: f(7), ease: E.pop }, at);
                  ft(tl, x.ring, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, at);
                  ft(tl, x.icC, { opacity: 0 }, { opacity: 1, duration: f(5), ease: E.enter }, at + f(1));
                }
                const pts = route(i);
                const w = gx.wire(wires, pts, { w: lw, wo: lo });
                const tD = at + f(3), dD = Math.max(f(7), Math.min(f(12), w.L / 1400));
                gx.drawWire(tl, w, tD, dD);
                gx.ev(ctx, "connect", tD);
                const dot = gx.pulseDot(cam, ds);
                const dPu = Math.max(f(8), w.L / 1100);
                const tHit = gx.pulse(tl, dot, pts, tD + dD - f(3), dPu);
                ft(tl, hub.t, { scale: 1.12 }, { scale: 1.2, duration: f(3), ease: E.enter }, tHit);
                ft(tl, hub.t, { scale: 1.2 }, { scale: 1.12, duration: f(7), ease: E.pop }, tHit + f(3));
                tLast = tHit;
                loops.push({ dot, pts, from: tHit + 0.5 + k * 0.27, d: Math.max(f(14), w.L / 900) });
              });
              // nada quieto: los pulsos vuelven a recorrer el circuito hasta el final del plano
              loops.forEach((q) => { for (let tb = Math.max(q.from, (tLast || 0) + 0.3); tb + q.d < t1 - 0.3; tb += q.d + 0.9) gx.pulse(tl, q.dot, q.pts, tb, q.d, { op: 0.9 }); });
              // el foco reacciona a la última: su icono GIRA (engranajes, sistema) y el aro brilla
              if (tLast != null) {
                if (props.spin !== false) ft(tl, [hub.icC, hub.icS], { rotation: 0 }, { rotation: 360, duration: f(18), ease: E.move }, tLast + f(1));
                ft(tl, hub.ring, { scale: 1 }, { scale: 1.12, duration: f(4), ease: E.enter }, tLast);
                ft(tl, hub.ring, { scale: 1.12 }, { scale: 1, duration: f(8), ease: E.pop }, tLast + f(4));
                gx.ev(ctx, "merge", tLast);
              }
              if (noteIn) {
                const tNo = Math.max((tLast || last) + f(6), C("note", (tLast || last) + 0.4));
                const swap = note.dataset.swap === "1";
                if (swap) tl.to([ord, name].filter(Boolean), { opacity: 0, y: -R(18 * s), duration: f(5), ease: E.exit }, tNo - f(3));
                gx.maskIn(tl, noteIn, tNo + (swap ? f(2) : 0), { from: 105 });
                gx.ev(ctx, "note", tNo);
              }
            }
          }
          if (mode === "pick" && tFocus) {
            const tP = Math.max(tS + f(4), C("pick", tS + 0.3));
            // kicker: en el corte (por defecto) o en su palabra (cue «title»); `sub` debajo en la cue «sub»
            const tK = C("title", null);
            // kit v14: kicker y `sub` con gx.textIn (8 f, subida + opacidad), en el corte o en su palabra
            if (kick) gx.textIn(tl, kick, tK == null || tK <= tS + f(2) ? tS : Math.max(tS + f(2), tK));
            if (sub) gx.textIn(tl, sub, Math.max((tK != null ? tK : tS) + f(8), C("sub", tP + 0.6)));
            // `pick_solo` (las baldosas de después
            // en el DOM se transparentaban sobre la elegida al crecer): las demás se apagan del TODO (no al 10 %) en 6 f y la
            // elegida crece 5 f después, por encima de todas. Sin la opción, igual que antes.
            const solo = !!props.pick_solo, dG = solo ? f(5) : 0;
            if (pickC) {   // `pick_from: "center"`: las CINCO se apagan a la vez y la diana nace en el centro
              tiles.forEach((x, i) => {
                ft(tl, x.t, { opacity: st0[i].op, scale: st0[i].sc }, { opacity: 0, scale: 0.92, duration: f(6), ease: E.enter }, tP);
                if (st0[i].ring) ft(tl, x.ring, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tP);
              });
              const gcx = x0 + gw / 2, gcy = y0 + gh / 2, k = Math.min(1.6, (gh * 0.98) / tsz);
              ft(tl, pickC.slot, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: k, duration: f(10), ease: E.pop }, tP + f(1));
              ft(tl, pickC.ring, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, tP + f(4));
              gsap.set(glow, { x: R(gcx - tsz * 1.2), y: R(gcy - tsz * 1.2) });
              ft(tl, glow, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: k, duration: f(10), ease: E.enter }, tP + f(2));
              gx.ev(ctx, "pick", tP + f(1));
            }
            if (solo && !pickC) gsap.set(tFocus.slot, { zIndex: 5 });
            if (target && !pickC) {   // la elegida no dice cuál: su icono cede a la diana («un problema real»)
              // (con `pick_solo` la lupa de una herramienta se
              // veía 8–13 f en la baldosa que crecía bajo «Uno o Dos»): con `pick_solo`, el icono se funde y la diana entra
              // DESDE tP (sin dG), antes de que la baldosa crezca. Sin `pick_solo`, igual que antes.
              const tI = solo ? tP : tP + f(3) + dG, tT = solo ? tP + f(1) : tP + f(5) + dG, dI = solo ? f(4) : f(5);
              // (la lupa y la diana se veían superpuestas 2 f): con
              // `pick_solo` (opcional) el icono pasa a 0 con un `set` en tP, sin fundido. Sin `pick_solo`, igual
              if (solo) {
                tl.set(tFocus.icS, { opacity: 0 }, gx.T ? gx.T(tI) : tI);
                if (st0[fi].gold) tl.set(tFocus.icC, { opacity: 0 }, gx.T ? gx.T(tI) : tI);
              } else {
                ft(tl, tFocus.icS, { opacity: 1 }, { opacity: 0, duration: dI, ease: E.exit }, tI);
                if (st0[fi].gold) ft(tl, tFocus.icC, { opacity: 1 }, { opacity: 0, duration: dI, ease: E.exit }, tI);
              }
              ft(tl, target, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, tT);
            }
            // las demás se apagan; la elegida, en duotono oro (o con su diana), crece y se centra en la rejilla
            if (!pickC) tiles.forEach((x, i) => {
              if (i === fi) return;
              ft(tl, x.t, { opacity: st0[i].op, scale: st0[i].sc }, { opacity: solo ? 0 : 0.1, scale: 0.92, duration: f(solo ? 6 : 8), ease: E.enter }, tP);
              if (st0[i].ring) ft(tl, x.ring, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tP);
            });
            const gcx = x0 + gw / 2, gcy = y0 + gh / 2, k = Math.min(1.6, (gh * 0.98) / tsz);
            if (!pickC) {
            ft(tl, tFocus.t, { x: 0, y: 0, scale: st0[fi].sc }, { x: R(gcx - tFocus.cx), y: R(gcy - tFocus.cy), scale: k, duration: f(10), ease: E.pop }, tP + f(2) + dG);
            gx.streak(tl, tFocus.t, tP + f(2) + dG, f(6), Math.abs(gcx - tFocus.cx) > Math.abs(gcy - tFocus.cy) ? "x" : "y", 8);
            ft(tl, tFocus.ring, { opacity: st0[fi].ring }, { opacity: 1, duration: f(6), ease: E.enter }, tP + f(4) + dG);
            if (!target) ft(tl, tFocus.icC, { opacity: st0[fi].gold }, { opacity: 1, duration: f(6), ease: E.enter }, tP + f(3) + dG);
            gsap.set(glow, { x: R(gcx - tsz * 1.2), y: R(gcy - tsz * 1.2) });
            ft(tl, glow, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: k, duration: f(10), ease: E.enter }, tP + f(3) + dG);
            gx.ev(ctx, "pick", tP + f(2));
            }
          }
          gx.bgIn(tl, bd, t0, t1, 61, props);
          gx.out(tl, props, t1, [wrap], { dur: ex, ctx });
        },
      };
    },
  });
})(window.CK);
