// viz.shapes — tres piezas de forma (sin rejillas) para «diez servicios» (evita animaciones muy iguales):
//   morph: UNA forma grande que cambia por completo con cada cliente (círculo → triángulo → estrella); las anteriores
//          bajan a una fila con «≠» y la nota cierra («cada nuevo cliente necesita algo completamente diferente»).
//   hub:   red radial: «Tú» en el centro, las oportunidades llegan y se aceptan, los servicios brotan alrededor, de cada
//          uno salen posibilidades y una se enciende en oro («tu primer cliente»). Casi sin texto.
//   loop:  un círculo que se recorre cada vez más rápido (Cliente 1 → 2 → 3, el mismo proyecto) con cuatro estaciones
//          que se encienden en su palabra (tiempo, errores, automatizar, resultado).
// props: {mode, cards:[{label}], note?, kicker?, center?, client?, stations:[{label, kind}], canvas?, keep_start?, exit?}
// cues:  morph: c0…c2, signs, note · hub: kick, opps, services, spread, client · loop: kick, c0…c2, r0…r3, best
// eventos: enter, morph, note, opps, node, spread, client, lap, station, best, exit
// `stations[].asset|glyph` (icono de estado en el oro del kit, gx.icon) y mode «dial»: reloj de 24 h de
//   instrumento (aguja que barre en `sweep`, arco de oro, estaciones en las diagonales; evento dial).
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
  const { f, ft, R } = gx;
  const NS = "http://www.w3.org/2000/svg";
  // ── Regla de entrada de TODO texto (ningún texto aparece ya
  //    puesto): un nodo con texto empieza su entrada EN el fotograma del corte o de su cue (nunca antes), dura 8 f y sube:
  //    opacidad + 32 px (riseIn) o máscara yPercent 110→0 (maskIn). Nada de gx.cutIn para texto (va fuera del kit
  //    compartido a propósito: el kit se actualiza aparte y la copia más nueva gana).
  const TXT_F = 8, TXT_RISE = 32;
  //    Con el kit v14 la regla vive en el kit; esta copia solo se usa si no está.
  function riseIn(tl, node, at, E) { if (gx.textIn) return gx.textIn(tl, node, at); ft(tl, node, { opacity: 0, y: TXT_RISE }, { opacity: 1, y: 0, duration: f(TXT_F), ease: E.enter }, at); }
  function maskIn(tl, inner, at, E) { if (gx.maskIn) return gx.maskIn(tl, inner, at); ft(tl, inner, { opacity: 0, yPercent: 110 }, { opacity: 1, yPercent: 0, duration: f(TXT_F), ease: E.enter }, at); }
  function masked(parent, text) { const m = gx.el("span", "sh-tm", parent); const i = gx.el("span", "sh-ti", m, text); return i; }

  function sv(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function box(parent, cls, x, y, w, h) {
    const n = gx.el("div", cls, parent);
    Object.assign(n.style, { left: R(x) + "px", top: R(y) + "px", width: R(w) + "px", height: R(h) + "px" });
    return n;
  }
  function svgIn(node, w, h) { return sv("g", {}, sv("svg", { width: R(w), height: R(h), viewBox: `0 0 ${R(w)} ${R(h)}`, class: "sh-svg" }, node)); }
  // formas grandes (abstractas): 0 círculo · 1 triángulo · 2 estrella · 3 cuadrado
  function shape(g, k, cx, cy, r) {
    if (k % 4 === 0) return sv("circle", { cx, cy, r, class: "sh-ink" }, g);
    if (k % 4 === 1) return sv("path", { d: `M${cx} ${cy - r * 1.05}L${cx + r * 1.12} ${cy + r * 0.86}L${cx - r * 1.12} ${cy + r * 0.86}Z`, class: "sh-gold" }, g);
    if (k % 4 === 2) {
      const p = [];
      for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.46 : r * 1.04; p.push(`${(cx + rr * Math.cos(a)).toFixed(1)} ${(cy + rr * Math.sin(a)).toFixed(1)}`); }
      return sv("path", { d: "M" + p.join("L") + "Z", class: "sh-line" }, g);
    }
    return sv("rect", { x: cx - r * 0.85, y: cy - r * 0.85, width: r * 1.7, height: r * 1.7, rx: r * 0.2, class: "sh-ink" }, g);
  }
  // pictogramas pequeños de servicio (abstractos, nunca logos), en un viewBox 100×100
  const GLY = [
    (g) => sv("circle", { cx: 50, cy: 50, r: 22, class: "sh-gf" }, g),
    (g) => sv("path", { d: "M50 26L74 70H26Z", class: "sh-gf" }, g),
    (g) => sv("rect", { x: 30, y: 30, width: 40, height: 40, rx: 7, class: "sh-gf" }, g),
    (g) => sv("path", { d: "M55 20L32 54H47L42 80L68 44H53Z", class: "sh-gf" }, g),
    (g) => sv("path", { d: "M43 24H57V43H76V57H57V76H43V57H24V43H43Z", class: "sh-gf" }, g),
    (g) => sv("path", { d: "M22 58Q36 30 50 50T78 42", class: "sh-gs" }, g),
  ];
  // iconos de las estaciones del ciclo
  function stationIcon(g, kind) {
    if (kind === "time") { sv("circle", { cx: 50, cy: 50, r: 26, class: "sh-gs" }, g); sv("path", { d: "M50 34V50L61 58", class: "sh-gs" }, g); }
    else if (kind === "errors") { sv("path", { d: "M34 50L46 62L68 38", class: "sh-gs sh-thick" }, g); }
    else if (kind === "auto") sv("path", { d: "M55 18L32 54H47L42 82L68 44H53Z", class: "sh-gf" }, g);
    else { sv("rect", { x: 28, y: 58, width: 11, height: 16, rx: 2, class: "sh-gf" }, g); sv("rect", { x: 45, y: 46, width: 11, height: 28, rx: 2, class: "sh-gf" }, g); sv("rect", { x: 62, y: 32, width: 11, height: 42, rx: 2, class: "sh-gf" }, g); }
  }

  // ── morph: una forma que cambia por completo con cada cliente
  function mountMorph(wrap, A, props, ctx) {
    const cards = (props.cards || [{ label: "Cliente 1" }, { label: "Cliente 2" }, { label: "Cliente 3" }]).slice(0, 4);
    const n = cards.length;
    const need = 72 + 30 + 360 + 34 + 96 + 30 + 84;
    const s = Math.max(0.7, Math.min(1.15, A.w / 950, (A.h * 0.96) / need));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    const y0 = R(Math.max(0, (A.h - S(need)) / 2)), cx = A.w / 2;
    const pill = box(wrap, "sh-pill", cx - S(150), y0, S(300), S(72));
    const pillTxt = masked(pill, "");   // el rótulo sube por su máscara (también en cada cambio de cliente)
    const yStage = y0 + S(72 + 30), stageH = S(360), cy = yStage + stageH / 2;
    const big = cards.map((_, k) => { const b = box(wrap, "sh-big", cx - stageH / 2, yStage, stageH, stageH); shape(svgIn(b, stageH, stageH), k, stageH / 2, stageH / 2, stageH * 0.36); return b; });
    // fila de las anteriores (pequeñas) con «≠» rojos entre ellas
    const yRow = yStage + stageH + S(34), chip = S(96), gapC = S(84), rowW = n * chip + (n - 1) * gapC, x0 = cx - rowW / 2;
    const slots = cards.map((_, k) => ({ x: x0 + k * (chip + gapC), y: yRow }));
    const neq = cards.slice(0, -1).map((_, k) => { const sg = box(wrap, "sh-neq", slots[k].x + chip, yRow, gapC, chip); sg.textContent = "≠"; return sg; });
    const note = props.note ? box(wrap, "sh-note", 0, yRow + chip + S(30), A.w, S(84)) : null;
    if (note) note.textContent = props.note;
    gsap.set(big.concat(neq, [pill, note].filter(Boolean)), { opacity: 0 });

    function animate(tl, tS, t1, cues, E) {
      const C = (k, d) => gx.cue(cues, k, d);
      pill.style.fontSize = Math.max(30, S(36)) + "px";
      if (note) gx.fit(note, { max: S(68), min: 44, width: A.w, lines: 1 });
      const tc = [];
      cards.forEach((_, k) => tc.push(Math.max(k ? tc[k - 1] + f(10) : tS, C("c" + k, tS + k * 0.5))));
      gx.swapText(tl, pillTxt, cards.map((c) => c.label), tc.slice(1));
      // la píldora (fondo) se asienta y el rótulo sube por su máscara; en cada cliente nuevo el anterior sale (3 f) y el
      // nuevo entra en su cue (regla de entrada de texto)
      gsap.set(pill, { transformOrigin: "50% 50%" });
      ft(tl, pill, { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: f(8), ease: E.enter }, tc[0]);
      maskIn(tl, pillTxt, tc[0], E);
      tc.slice(1).forEach((at, j) => {
        const o0 = Math.max(at - f(3), tc[j] + f(8));
        if (at - o0 >= f(2)) ft(tl, pillTxt, { yPercent: 0, opacity: 1 }, { yPercent: -110, opacity: 0, duration: at - o0, ease: E.exit }, o0);
        maskIn(tl, pillTxt, at, E);
      });
      big.forEach((b, k) => {
        // entra girando y se asienta; con el siguiente cliente baja a su hueco de la fila (pequeña)
        if (k === 0) gx.cutIn(tl, b, tc[0], { from: 0.9, scale: 0.9 });
        else ft(tl, b, { opacity: 0, scale: 0.55, rotation: -24 }, { opacity: 1, scale: 1, rotation: 0, duration: f(10), ease: E.pop }, tc[k]);
        gx.ev(ctx, "morph", tc[k]);
        const tOut = k + 1 < n ? tc[k + 1] : C("note", tc[k] + 0.6);
        const sc = chip / stageH, dx = R(slots[k].x + chip / 2 - cx), dy = R(slots[k].y + chip / 2 - cy);
        ft(tl, b, { x: 0, y: 0, scale: 1 }, { x: dx, y: dy, scale: sc, duration: f(10), ease: E.move }, tOut);
      });
      neq.forEach((sg, k) => ft(tl, sg, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(7), ease: E.pop }, Math.max(tc[k + 1] + f(8), C("signs", 0))));
      if (note) { const tn = Math.max(tc[n - 1] + f(6), C("note", tc[n - 1] + 0.6)); riseIn(tl, note, tn, E); gx.ev(ctx, "note", tn); }
    }
    return { animate };
  }

  // ── hub: «Tú» en el centro; oportunidades que llegan, servicios que brotan, posibilidades, el primer cliente
  function mountHub(wrap, A, props, ctx) {
    const kickH = props.kicker ? 46 : 0;
    const s = Math.max(0.7, Math.min(1.1, A.w / 950, (A.h * 0.96) / (kickH + 600)));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    const kick = props.kicker ? box(wrap, "sh-kick", 0, 0, A.w, S(kickH)) : null;
    if (kick) kick.textContent = props.kicker;
    const cx = A.w / 2, cy = S(kickH) + (A.h - S(kickH)) / 2, Rs = S(176), Ro = S(268), rc = S(86), rs = S(46);
    const lines = svgIn(box(wrap, "sh-lines", 0, 0, A.w, A.h), A.w, A.h);
    const N = 6, angs = Array.from({ length: N }, (_, i) => -Math.PI / 2 + i * 2 * Math.PI / N);
    const spokes = angs.map((a) => {
      const x2 = cx + Math.cos(a) * Rs, y2 = cy + Math.sin(a) * Rs;
      const l = sv("line", { x1: R(cx), y1: R(cy), x2: R(x2), y2: R(y2), class: "sh-spoke" }, lines);
      return { l, len: Rs };
    });
    const outs = [];   // posibilidades: dos por servicio, en el anillo de fuera
    angs.forEach((a, i) => [-0.22, 0.22].forEach((d, j) => {
      const b = a + d, x = cx + Math.cos(b) * Ro, y = cy + Math.sin(b) * Ro;
      const l = sv("line", { x1: R(cx + Math.cos(a) * Rs), y1: R(cy + Math.sin(a) * Rs), x2: R(x), y2: R(y), class: "sh-spoke2" }, lines);
      const dot = box(wrap, "sh-dot", x - S(13), y - S(13), S(26), S(26));
      outs.push({ l, dot, x, y, i, j, len: Math.hypot(x - (cx + Math.cos(a) * Rs), y - (cy + Math.sin(a) * Rs)) });
    }));
    const pick = outs[Math.min(outs.length - 1, props.pick == null ? 3 : props.pick)];
    const pickRing = box(wrap, "sh-pickring", pick.x - S(34), pick.y - S(34), S(68), S(68));
    const nodes = angs.map((a, i) => {
      const x = cx + Math.cos(a) * Rs, y = cy + Math.sin(a) * Rs;
      const nd = box(wrap, "sh-node", x - rs, y - rs, rs * 2, rs * 2);
      const g = sv("g", {}, sv("svg", { viewBox: "0 0 100 100", class: "sh-nsvg" }, nd));
      GLY[i % GLY.length](g);
      return nd;
    });
    // oportunidades: llegan de fuera del área hasta el centro y se absorben
    const r2 = gx.rng(gx.hash("sh-hub" + (props.kicker || "")));
    const NO = props.opps || 12;
    const opps = Array.from({ length: NO }, (_, i) => {
      const a = -Math.PI / 2 + ((i * 5) % NO) * 2 * Math.PI / NO + (r2() - 0.5) * 0.3, d = S(470) + r2() * S(60);
      const o = box(wrap, "sh-opp", cx - S(17), cy - S(17), S(34), S(34));
      return { o, dx: R(Math.cos(a) * d), dy: R(Math.sin(a) * d) };
    });
    const center = box(wrap, "sh-center", cx - rc, cy - rc, rc * 2, rc * 2);
    const centerTxt = masked(center, props.center || "Tú");   // el círculo se asienta y el texto sube dentro
    const client = props.client ? box(wrap, "sh-client", 0, A.h - S(64), A.w, S(64)) : null;
    if (client) client.textContent = props.client;
    gsap.set([kick, client, pickRing].filter(Boolean).concat(nodes, outs.map((o) => o.dot), opps.map((o) => o.o)), { opacity: 0 });
    spokes.forEach((sp) => { sp.l.style.strokeDasharray = `${sp.len} ${sp.len}`; sp.l.style.strokeDashoffset = sp.len; });
    outs.forEach((o) => { o.l.style.strokeDasharray = `${o.len} ${o.len}`; o.l.style.strokeDashoffset = o.len; });

    function animate(tl, tS, t1, cues, E) {
      const C = (k, d) => gx.cue(cues, k, d);
      if (kick) gx.fit(kick, { max: Math.max(30, S(34)), min: 30, width: A.w, lines: 1 });
      center.style.fontSize = S(66) + "px";
      if (client) gx.fit(client, { max: S(60), min: 40, width: A.w, lines: 1 });
      ft(tl, center, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, tS);
      maskIn(tl, centerTxt, tS, E);
      if (kick) riseIn(tl, kick, Math.max(tS, C("kick", tS)), E);
      // oportunidades que llegan y se aceptan (el centro late al absorberlas)
      const tO = Math.max(tS + f(6), C("opps", tS + 0.8));
      // llegan durante toda la frase (hasta poco antes de «servicios»), cada una late en el centro al entrar
      const tN = Math.max(tO + 1.2, C("services", tO + 2.4));
      const step = Math.max(f(3), Math.min(f(7), (tN - tO - f(16)) / Math.max(1, NO - 1)));
      opps.forEach((o, i) => {
        const at = tO + i * step, ab = at + f(13);
        ft(tl, o.o, { opacity: 0, x: o.dx, y: o.dy, scale: 1 }, { opacity: 1, x: R(o.dx * 0.42), y: R(o.dy * 0.42), duration: f(7), ease: E.enter }, at);
        ft(tl, o.o, { x: R(o.dx * 0.42), y: R(o.dy * 0.42), opacity: 1 }, { x: 0, y: 0, opacity: 0, scale: 0.5, duration: f(6), ease: E.move }, at + f(7));
        if (i % 2 === 0) {
          ft(tl, center, { scale: 1 }, { scale: 1.09, duration: f(3), ease: E.enter }, ab);
          ft(tl, center, { scale: 1.09 }, { scale: 1, duration: f(6), ease: E.move }, ab + f(3));
        }
      });
      gx.ev(ctx, "opps", tO);
      // servicios: brotan alrededor, cada uno con su radio
      nodes.forEach((nd, i) => {
        const at = tN + i * f(3);
        ft(tl, spokes[i].l, { strokeDashoffset: spokes[i].len }, { strokeDashoffset: 0, duration: f(7), ease: E.move }, at);
        ft(tl, nd, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, at + f(3));
      });
      gx.ev(ctx, "node", tN);
      // posibilidades: de cada servicio salen dos
      const tP = Math.max(tN + N * f(3) + f(4), C("spread", tN + 1.0));
      outs.forEach((o, k) => {
        const at = tP + (o.i * 2 + o.j) * f(1);
        ft(tl, o.l, { strokeDashoffset: o.len }, { strokeDashoffset: 0, duration: f(6), ease: E.move }, at);
        ft(tl, o.dot, { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: f(7), ease: E.enter }, at + f(3));
      });
      gx.ev(ctx, "spread", tP);
      // titilan (nada quieto) hasta el cliente
      const tCl = Math.max(tP + f(20), C("client", tP + 1.4));
      outs.forEach((o, k) => {
        for (let tb = tP + 0.6 + (k % 4) * 0.17; tb < tCl - 0.3; tb += 0.9) {
          ft(tl, o.dot, { scale: 1 }, { scale: 1.25, duration: f(5), ease: E.enter }, tb);
          ft(tl, o.dot, { scale: 1.25 }, { scale: 1, duration: f(8), ease: E.move }, tb + f(5));
        }
      });
      // el primer cliente: una posibilidad se enciende en oro, su camino hasta «Tú» también, y el resto cede
      ft(tl, outs.filter((o) => o !== pick).map((o) => o.dot), { opacity: 1 }, { opacity: 0.35, duration: f(8), ease: E.enter }, tCl);
      ft(tl, pick.dot, { scale: 1 }, { scale: 1.6, duration: f(8), ease: E.pop }, tCl);
      ft(tl, pick.dot, { backgroundColor: "rgba(244,242,238,1)" }, { backgroundColor: "rgba(254,202,26,1)", duration: f(6), ease: E.enter }, tCl);
      ft(tl, pickRing, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: f(9), ease: E.enter }, tCl + f(3));
      for (let tb = tCl + 0.9; tb < t1 - 0.4; tb += 1.0) {
        ft(tl, pickRing, { scale: 1, opacity: 1 }, { scale: 1.35, opacity: 0.3, duration: f(14), ease: E.enter }, tb);
        ft(tl, pickRing, { scale: 1.35, opacity: 0.3 }, { scale: 1, opacity: 1, duration: f(4), ease: E.move }, tb + f(14));
      }
      if (client) riseIn(tl, client, tCl, E);
      gx.ev(ctx, "client", tCl);
    }
    return { animate };
  }

  // ── loop: el mismo proyecto, una vuelta por cliente, cada vez más rápida; las estaciones se encienden en su palabra
  let RING_GAP_N = 0;   // ids de las máscaras de `ring_gap` (únicos por página)
  function mountLoop(wrap, A, props, ctx) {
    const st = (props.stations || []).slice(0, 4);
    const cards = (props.cards || [{ label: "Cliente 1" }, { label: "Cliente 2" }, { label: "Cliente 3" }]).slice(0, 4);
    // `scale_max`: a pantalla completa el aro medía ~470 de 1080 px;
    // con scale_max (≤1,4) crece hasta ese tope (referencia de ancho 820 px en vez de 950). Sin la opción, igual que antes.
    const sMax = props.scale_max ? Math.min(1.4, +props.scale_max) : 1.1;
    const s = Math.max(0.7, Math.min(sMax, A.w / (props.scale_max ? 820 : 950), (A.h * 0.97) / 740));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    const cx = A.w / 2, cy = A.h / 2 + S(4), Rr = S(252), rS = S(58);
    const ringBox = box(wrap, "sh-ringbox", cx - Rr - S(20), cy - Rr - S(20), (Rr + S(20)) * 2, (Rr + S(20)) * 2);
    const rg = svgIn(ringBox, (Rr + S(20)) * 2, (Rr + S(20)) * 2), rc = Rr + S(20);
    sv("circle", { cx: rc, cy: rc, r: Rr, class: "sh-ring" }, rg);
    const gold = sv("circle", { cx: rc, cy: rc, r: Rr, class: "sh-ring-gold" }, rg);
    const L = 2 * Math.PI * Rr;
    gold.style.strokeDasharray = `${L} ${L}`; gold.style.strokeDashoffset = L;
    // el cometa: un brazo que gira alrededor del centro con el punto en su extremo
    const arm = box(wrap, "sh-arm", cx, cy, 0, 0);
    const comet = box(arm, "sh-comet", -S(17), -Rr - S(17), S(34), S(34));
    // centro: «Mismo Proyecto» y el cliente que cambia con cada vuelta
    const ck = props.kicker ? box(wrap, "sh-ckick", cx - S(220), cy - S(70), S(440), S(40)) : null;
    if (ck) ck.textContent = props.kicker;
    const cl = box(wrap, "sh-clabel", cx - S(220), cy - S(26), S(440), S(80));
    const ang = [-90, 0, 90, 180];
    const stations = st.map((x, k) => {
      const a = ang[k] * Math.PI / 180, sx = cx + Math.cos(a) * Rr, sy = cy + Math.sin(a) * Rr;
      const c = box(wrap, "sh-station", sx - rS, sy - rS, rS * 2, rS * 2);
      // `stations[].asset` / `glyph`: icono del kit (o glifo) en el ORO DEL KIT (gx.icon); si no, el glifo de siempre
      if (x.asset || x.glyph) { gx.icon(c, ctx, { asset: x.asset, glyph: x.glyph, tone: x.tone || "gold" }, "sh-st-ic"); c.classList.add("sh-station-ic"); }
      else stationIcon(sv("g", {}, sv("svg", { viewBox: "0 0 100 100", class: "sh-nsvg" }, c)), x.kind || ["time", "errors", "auto", "result"][k]);
      const lw = Math.min(S(560), A.w), lh = S(50);
      const ly = k === 0 ? sy - rS - S(14) - lh : sy + rS + S(12);
      const lx = Math.max(0, Math.min(A.w - lw, sx - lw / 2));
      const lb = box(wrap, "sh-slabel", lx, ly, lw, lh);
      lb.textContent = x.label || "";
      const ring = (x.asset || x.glyph) ? box(c, "sh-st-ring", -S(7), -S(7), rS * 2 + S(14), rS * 2 + S(14)) : null;
      return { c, lb, ring };
    });
    gsap.set([ringBox, arm, cl, ck].filter(Boolean).concat(stations.map((x) => x.c), stations.map((x) => x.lb)), { opacity: 0 });
    stations.forEach((x) => { if (x.ring) gsap.set(x.ring, { opacity: 0 }); });

    function animate(tl, tS, t1, cues, E) {
      const C = (k, d) => gx.cue(cues, k, d);
      cl.style.fontSize = S(72) + "px";
      // el rótulo central iba a 72 px fijos en una caja de 440
      // sin ajuste y «Proyectos Reales» / «Tu Forma de Trabajar» se metían bajo las estaciones de los lados («▢yectos
      // Rea▢»). Ahora cabe entre las estaciones (2·(Rr − rS) − 48), hasta en 2 líneas, al mismo cuerpo para todos los
      // clientes; los rótulos cortos que ya cabían siguen a 72 px.
      {
        const wC = 2 * (Rr - rS) - S(48), midY = cy + S(14);
        Object.assign(cl.style, { width: wC + "px", left: R(cx - wC / 2) + "px", height: "auto", whiteSpace: "normal",
          textAlign: "center", lineHeight: "1.02" });
        const sizes = cards.map((c) => { cl.textContent = c.label || ""; return gx.fit(cl, { max: S(72), min: 36, width: wC, lines: 2 }); });
        cl.textContent = "";
        cl.style.fontSize = Math.min(S(72), ...sizes) + "px";
        const hC = S(200);
        Object.assign(cl.style, { height: hC + "px", top: R(midY - hC / 2) + "px" });
      }
      if (ck) ck.style.fontSize = Math.max(30, S(32)) + "px";
      const fs = Math.min(...stations.map((x) => gx.fit(x.lb, { max: Math.max(32, S(40)), min: 30, width: Math.min(S(560), A.w), lines: 1 })));
      stations.forEach((x) => { x.lb.style.fontSize = fs + "px"; });
      // la caja de cada rótulo medía S(560) y, al recortarla
      // contra el borde, los de las estaciones de los lados se corrían ~160 px hacia el centro y se leían como una línea
      // más del rótulo central («Proyectos Reales / Mejorar Probar»). Ahora mide lo que su texto y va centrada bajo su
      // estación (con 8 px de margen al borde).
      stations.forEach((x, k) => {
        if (!x.lb.textContent) return;
        x.lb.style.width = "auto";
        const tw = Math.ceil(x.lb.offsetWidth) + S(8), sx = cx + Math.cos(ang[k] * Math.PI / 180) * Rr;
        x.lb.style.width = tw + "px";
        x.lb.style.left = R(Math.max(S(8), Math.min(A.w - tw - S(8), sx - tw / 2))) + "px";
      });
      // `ring_gap` (el trazo del aro cruzaba «Mejorar» y «Probar»):
      // el aro (gris y oro) se interrumpe bajo cada rótulo con una máscara (sin cajas de color sobre el lienzo)
      if (props.ring_gap) {
        const NS = "http://www.w3.org/2000/svg", svgEl = rg.ownerSVGElement, ox = cx - Rr - S(20), oy = cy - Rr - S(20);
        const id = "sh-ringgap-" + (++RING_GAP_N);
        const defs = document.createElementNS(NS, "defs"), mk = document.createElementNS(NS, "mask");
        mk.setAttribute("id", id); mk.setAttribute("maskUnits", "userSpaceOnUse");
        const all = (Rr + S(20)) * 2;
        const full = document.createElementNS(NS, "rect");
        [["x", -S(40)], ["y", -S(40)], ["width", all + S(80)], ["height", all + S(80)], ["fill", "#fff"]].forEach(([k, v]) => full.setAttribute(k, v));
        mk.appendChild(full);
        stations.forEach((x) => {
          if (!x.lb.textContent) return;
          const q = document.createElementNS(NS, "rect"), pd = S(10);
          [["x", R(parseFloat(x.lb.style.left) - ox - pd)], ["y", R(parseFloat(x.lb.style.top) - oy - pd)],
            ["width", R(parseFloat(x.lb.style.width) + 2 * pd)], ["height", R(parseFloat(x.lb.style.height) + 2 * pd)],
            ["rx", S(14)], ["fill", "#000"]].forEach(([k, v]) => q.setAttribute(k, v));
          mk.appendChild(q);
        });
        defs.appendChild(mk); svgEl.insertBefore(defs, svgEl.firstChild);
        rg.setAttribute("mask", "url(#" + id + ")");
      }
      // `stations_in: "cue"` (los rótulos en gris adelantaban «Añadir» 1,6 s y «Mejorar» 3,5 s):
      // cada estación (forma y rótulo) entra en SU cue r<k>; sin la prop, todas en el corte como siempre
      const stIn = props.stations_in === "cue";
      gx.cutIn(tl, [ringBox].concat(stIn ? [] : stations.map((x) => x.c)), tS);              // formas (sin texto)
      stations.forEach((x, k) => {
        const at = stIn ? Math.max(tS, C("r" + k, tS)) : tS;
        if (stIn) ft(tl, x.c, { opacity: 0 }, { opacity: 1, duration: f(4), ease: E.enter }, Math.max(tS, at - f(2)));
        if (x.lb.textContent) riseIn(tl, x.lb, stIn ? Math.max(tS, at - f(2)) : tS, E);  // los rótulos suben 32 px en 8 f
      });
      if (ck) riseIn(tl, ck, Math.max(tS, C("kick", tS)), E);
      // vueltas: una por cliente (cada vez más rápida) y luego seguidas, cada vez más cortas, hasta el final
      const tc = [];
      cards.forEach((_, k) => tc.push(Math.max(k ? tc[k - 1] + f(8) : tS, C("c" + k, tS + 0.3 + k * 0.6))));
      gx.swapText(tl, cl, [""].concat(cards.map((c) => c.label)), tc);
      riseIn(tl, cl, tc[0], E);   // sube (el fundido de 5 f se leía «sin entrada»: 32 px en 8 f)
      // cada cliente nuevo también ENTRA (el anterior sale en ≤ 3 f justo antes de su cue)
      tc.slice(1).forEach((at, j) => {
        const o0 = Math.max(at - f(3), tc[j] + f(8));
        if (at - o0 >= f(2)) ft(tl, cl, { opacity: 1, y: 0 }, { opacity: 0, y: -S(12), duration: at - o0, ease: E.exit }, o0);
        riseIn(tl, cl, at, E);
      });
      tl.set(arm, { opacity: 1 }, gx.T(tc[0]));
      let rot = 0, t = tc[0], dur = 1.5;
      const laps = [];
      while (t < t1 - 0.3) {
        const d = Math.min(dur, t1 - 0.3 - t);
        if (d < 0.25) break;
        laps.push([t, d]);
        t += d; dur = Math.max(0.55, dur * 0.82);
      }
      laps.forEach(([at, d], i) => {
        ft(tl, arm, { rotation: rot }, { rotation: rot + 360, duration: d, ease: i === 0 ? E.enter : E.move }, at);
        rot += 360;
      });
      tc.slice(1).forEach((at) => gx.ev(ctx, "lap", at));
      // las estaciones: en su palabra se llenan de oro y su rótulo pasa a tinta
      stations.forEach((x, k) => {
        const at = C("r" + k, null);
        if (at == null) return;
        x.c.classList.add("sh-st" + k);
        ft(tl, x.c, { scale: 1 }, { scale: 1.18, duration: f(5), ease: E.enter }, at);
        ft(tl, x.c, { scale: 1.18 }, { scale: 1, duration: f(8), ease: E.move }, at + f(5));
        if (x.ring) ft(tl, x.ring, { opacity: 0, scale: 1.12 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, at);   // icono oro: se enciende con aro
        else ft(tl, x.c, { backgroundColor: "rgba(255,255,255,1)" }, { backgroundColor: "rgba(254,202,26,1)", duration: f(6), ease: E.enter }, at);
        ft(tl, x.lb, { color: "rgba(15,13,16,.42)" }, { color: "rgba(15,13,16,1)", duration: f(6), ease: E.enter }, at);
        gx.ev(ctx, "station", at);
      });
      const tB = C("best", null);
      if (tB != null) {
        ft(tl, gold, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: f(14), ease: E.move }, tB);
        ft(tl, comet, { backgroundColor: "rgba(22,21,20,1)" }, { backgroundColor: "rgba(254,202,26,1)", duration: f(6), ease: E.enter }, tB);
        ft(tl, cl, { scale: 1 }, { scale: 1.08, duration: f(6), ease: E.enter }, tB);
        ft(tl, cl, { scale: 1.08 }, { scale: 1, duration: f(9), ease: E.move }, tB + f(6));
        gx.ev(ctx, "best", tB);
      }
    }
    return { animate };
  }

  // ── dial: un RELOJ de 24 h de instrumento (no el anillo fino con cometa, que parecía un indicador de
  //    carga): esfera con bisel de tinta y 24 marcas que aparecen en sentido horario, aguja que BARRE la vuelta completa en
  //    su cue (`sweep`, o `best`) dejando el arco de oro, estaciones con icono del kit (oro) en las diagonales que entran
  //    en su cue (r0…r3) mientras la aguja las señala, rótulo central en su cue (c0) y, después, la aguja sigue avanzando
  //    una hora cada segundo (nada quieto).
  //    `sweep_to` (fracción de vuelta, p. ej. 5/60) = CRONÓMETRO de «unos pocos
  //    minutos»: la aguja parte de las 12 y en `sweep` barre SOLO esa fracción (power3.out; el arco de oro marca esas pocas
  //    marcas), luego sigue avanzando CONTINUA, una marca por segundo, hasta la última estación (o la cue `stop`), donde se
  //    para con su arco; antes se quedaba quieta de 7,5 a 10,1 s porque el avance solo empezaba tras el último evento. Con
  //    `sweep_to`, por defecto: placa a las 6 sobre el bisel (`plate: "bottom"`: la aguja nunca pasa por debajo),
  //    estaciones en fantasma desde el principio (`stations_ghost`) y simétricas a los dos lados, separadas del bisel
  //    (`stations_at: "sides"`), avance continuo (`advance: "continuous"`). Eventos cuando la llegada SE VE: `dial_end`
  //    con la aguja ya quieta (80 % de su tween power3.out) y `station` 2 f después de arrancar su encendido.
  const KIND_GLYPH = { time: "clock", errors: "check", auto: "bolt", result: "chart" };
  function mountDial(wrap, A, props, ctx) {
    const st = (props.stations || []).slice(0, 4);
    const label = props.center || (props.cards && props.cards[0] && props.cards[0].label) || "";
    const swTo = typeof props.sweep_to === "number" && props.sweep_to > 0 ? Math.min(1, props.sweep_to) : null;
    const plateLow = (props.plate || (swTo ? "bottom" : "center")) === "bottom";
    const sides = (props.stations_at || (swTo ? "sides" : "diagonals")) === "sides";
    const ghostSt = props.stations_ghost != null ? !!props.stations_ghost : !!swTo;
    const cont = (props.advance || (swTo ? "continuous" : "ticks")) === "continuous";
    const s = Math.max(0.7, Math.min(1.2, A.w / 950, (A.h * 0.97) / 640));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    // placa en el bisel (a las 6): sobresale media placa por abajo; el bloque esfera + placa se centra en la banda
    const plateH = plateLow ? S(76) : S(80), lowX = plateLow && label ? R(plateH / 2) : 0;
    const Rd = R(Math.min(A.h * 0.4, (A.h * 0.97 - lowX) / 2.4, S(250))), tile = R(Math.max(96, Rd * 0.46));
    const cx = A.w / 2, cy = R(A.h / 2 - lowX / 2);
    const size = Rd * 2 + S(40), o = size / 2;
    const dialBox = box(wrap, "sh-dial", cx - o, cy - o, size, size);
    const g = svgIn(dialBox, size, size);
    sv("circle", { cx: o, cy: o, r: Rd, class: "sh-d-face" }, g);
    const trackR = Rd - S(26), L = 2 * Math.PI * trackR;
    sv("circle", { cx: o, cy: o, r: trackR, class: "sh-d-track" }, g);
    const arc = sv("circle", { cx: o, cy: o, r: trackR, class: "sh-d-arc" }, g);
    arc.style.strokeDasharray = `${L} ${L}`; arc.style.strokeDashoffset = L;
    // `range`: 24 (horas, por defecto) o 60 (cronómetro de «1 minuto»: 60 marcas, la aguja avanza un
    // segundo por segundo); `ticks` manda si se da
    const range = props.range === 60 ? 60 : 24;
    const N = props.ticks || range;
    const ticks = Array.from({ length: N }, (_, k) => {
      const a = (k / N) * 2 * Math.PI - Math.PI / 2, major = k % (N === 60 ? 5 : Math.max(1, N / 4)) === 0;
      const r0 = Rd - S(major ? 70 : 58), r1 = Rd - S(44);
      return sv("line", { x1: R(o + Math.cos(a) * r0), y1: R(o + Math.sin(a) * r0), x2: R(o + Math.cos(a) * r1), y2: R(o + Math.sin(a) * r1),
        class: major ? "sh-d-tick sh-d-major" : "sh-d-tick" }, g);
    });
    sv("circle", { cx: o, cy: o, r: Rd, class: "sh-d-bezel" }, g);
    // aguja (cuerpo de tinta afilado + punta oro) y eje
    const needle = box(wrap, "sh-needle", cx, cy, 0, 0);
    const ng = svgIn(box(needle, "sh-needle-in", -S(20), -Rd, S(40), Rd + S(36)), S(40), Rd + S(36));
    const nl = Rd * 0.8, w0 = S(9);
    sv("path", { d: `M ${S(20) - w0} ${Rd + S(18)} L ${S(20) - S(3)} ${Rd - nl} L ${S(20) + S(3)} ${Rd - nl} L ${S(20) + w0} ${Rd + S(18)} Z`, class: "sh-d-needle" }, ng);
    sv("circle", { cx: S(20), cy: Rd - nl + S(4), r: S(9), class: "sh-d-tip" }, ng);
    const hub = box(wrap, "sh-d-hub", cx - S(22), cy - S(22), S(44), S(44));
    // rótulo central en PLACA (la aguja tachaba «24 Horas»): por encima del eje y de la aguja,
    // que pasa por debajo, como la ventana de un reloj; o a las 6 sobre el bisel, donde la aguja no llega
    const pw = Rd * 1.24;
    const py = plateLow ? cy + Rd - plateH / 2 : cy - Rd * 0.5 - S(40);
    const plate = label ? box(wrap, "sh-d-plate" + (plateLow ? " sh-d-plate-low" : ""), cx - pw / 2, py, pw, plateH) : null;
    const lm = plate ? box(plate, "sh-d-lab-m", 0, 0, pw, plateH) : null;
    const li = lm ? gx.el("div", "sh-d-lab", lm, label) : null;
    // estaciones: en las diagonales, fuera de la esfera; o a los lados (9 y 3), simétricas y separadas del bisel
    const ang = sides ? [270, 90, 315, 45] : [-45, 45, 135, 225];
    const dSide = Math.max(Rd + tile / 2 + S(16), Math.min(Rd + S(44) + tile / 2, A.w / 2 - tile / 2 - 4));
    // `stations[].slot` (0–3): la estación ocupa ESE hueco del reparto
    //   (con «sides»: 0 = izquierda, 1 = derecha, 2–3 = diagonales altas) en vez del de su orden; p. ej. el calendario a la
    //   derecha cuando vuelve solo, en el mismo lado que en el primer dial. Sin la prop, nada cambia
    const stations = st.map((x, k) => {
      const sl = Number.isInteger(x.slot) && x.slot >= 0 && x.slot <= 3 ? x.slot : k;
      const a = ang[sl] * Math.PI / 180, d = sides ? dSide : Rd + tile * 0.74 + S(8);   // la esquina de la baldosa no pisa el bisel
      const sx = cx + Math.sin(a) * d * 1.0, sy = cy - Math.cos(a) * d * 1.0;
      const c = box(wrap, "sh-d-st", sx - tile / 2, sy - tile / 2, tile, tile);
      gx.icon(c, ctx, { asset: x.asset, glyph: x.glyph || KIND_GLYPH[x.kind] || ["clock", "user", "calendar", "check"][k], tone: x.tone || "gold" }, "sh-d-st-ic");
      const ring = box(c, "sh-st-ring", -S(7), -S(7), tile + S(14), tile + S(14));
      return { c, ring, deg: ang[sl] < 0 ? ang[sl] + 360 : ang[sl] };
    });
    gsap.set([dialBox, needle, hub].concat(ticks, stations.map((x) => x.c), stations.map((x) => x.ring), plate ? [plate] : []), { opacity: 0 });
    if (li) gsap.set(li, { opacity: 0 });
    gsap.set(needle, { rotation: 0, transformOrigin: "0px 0px" });

    function animate(tl, tS, t1, cues, E) {
      const C = (k, d) => gx.cue(cues, k, d);
      if (li) {
        gx.fit(li, { max: Math.max(56, S(64)), min: 48, width: pw - S(36), lines: 1 });
        // (la placa de ancho fijo recortaba «Bastante Tiempo» en
        // «stante Tiem»): si ni al cuerpo mínimo cabe, la placa crece hasta el texto + S(64), centrada y sin pasar del área
        const need = Math.ceil(li.scrollWidth) + S(64);
        if (need > pw + 1) {
          const pw2 = Math.min(A.w, need);
          Object.assign(plate.style, { left: R(cx - pw2 / 2) + "px", width: R(pw2) + "px" });
          lm.style.width = R(pw2) + "px";
          gx.fit(li, { max: Math.max(56, S(64)), min: 48, width: pw2 - S(36), lines: 1 });
        }
      }
      // la esfera ya está en el corte (no es texto) y se asienta; las marcas aparecen en sentido horario
      gsap.set(dialBox, { transformOrigin: "50% 50%" });
      tl.set(dialBox, { opacity: 1 }, gx.T(tS));
      ft(tl, dialBox, { scale: 0.92 }, { scale: 1, duration: f(9), ease: E.pop }, tS);
      ticks.forEach((tk, k) => ft(tl, tk, { opacity: 0 }, { opacity: 1, duration: f(3), ease: E.enter }, tS + f(2) + k * f(0.6)));
      ft(tl, [needle, hub], { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: f(7), ease: E.pop }, tS + f(4));
      if (li) {
        // la placa (sin texto) se asienta 2 f antes; el rótulo sube por su máscara EN su cue (8 f, 110 → 0)
        const tL = Math.max(tS + f(3), C("c0", tS + f(6)));
        gsap.set(plate, { transformOrigin: "50% 50%" });
        ft(tl, plate, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: f(6), ease: E.pop }, tL - f(2));
        maskIn(tl, li, tL, E);
      }
      // estaciones: en fantasma desde el principio o desde cero; se encienden en su cue y suenan cuando YA se ven
      const GHOST = 0.36, tGhost = tS + f(2);
      const lit = st.map((_, k) => Math.max(tS + (ghostSt ? f(4) : f(6)), C("r" + k, tS + 0.5 + k * 0.5)));
      stations.forEach((x, k) => {
        gsap.set(x.c, { transformOrigin: "50% 50%" });
        if (ghostSt && lit[k] >= tGhost + f(10)) ft(tl, x.c, { opacity: 0, scale: 0.9 }, { opacity: GHOST, scale: 1, duration: f(8), ease: E.enter }, tGhost);
      });
      function light(k, at) {
        const x = stations[k];
        if (ghostSt && at >= tGhost + f(10)) {   // de fantasma a encendida: sube a 1 y late (1 → 1,1 → 1)
          ft(tl, x.c, { opacity: GHOST }, { opacity: 1, duration: f(4), ease: E.enter }, at);
          ft(tl, x.c, { scale: 1 }, { scale: 1.1, duration: f(4), ease: E.enter }, at);
          ft(tl, x.c, { scale: 1.1 }, { scale: 1, duration: f(6), ease: E.move }, at + f(4));
        } else ft(tl, x.c, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, at);
        ft(tl, x.ring, { opacity: 0, scale: 1.12 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, at + f(3));
        gx.ev(ctx, "station", at + f(2));   // cuando la estación ya se ve (antes, al arrancar un fundido invisible)
      }
      const stepDeg = 360 / range;
      if (swTo) {
        // ── cronómetro: barrido corto, avance continuo hasta la última estación y parada
        stations.forEach((_, k) => light(k, lit[k]));
        const swDeg = 360 * swTo, arcAt = (deg) => L * (1 - Math.min(1, deg / 360));
        // `sweep_from` (fracción ≤ sweep_to): la esfera NACE ya en ese
        //   punto (aguja y arco puestos en el corte: es la vuelta de un dial que ya se vio); si es igual a sweep_to, no hay
        //   barrido (ni eventos dial/dial_end) y sigue el avance continuo. Sin la prop, el barrido de siempre desde las 12
        const swFrom = typeof props.sweep_from === "number" && props.sweep_from > 0 ? Math.min(swTo, props.sweep_from) : null;
        let rot = swDeg, t;
        if (swFrom != null) {
          const d0 = 360 * swFrom;
          tl.set(needle, { rotation: d0 }, gx.T(tS));
          tl.set(arc, { strokeDashoffset: arcAt(d0) }, gx.T(tS));
          t = tS + f(8);
          if (swDeg > d0 + 0.5) {
            const tSw = Math.max(tS + f(6), C("sweep", C("best", tS + 0.5)));
            ft(tl, needle, { rotation: d0 }, { rotation: swDeg, duration: f(16), ease: E.enter }, tSw);
            ft(tl, arc, { strokeDashoffset: arcAt(d0) }, { strokeDashoffset: arcAt(swDeg), duration: f(16), ease: E.enter }, tSw);
            gx.ev(ctx, "dial", tSw);
            t = tSw + f(16);
          }
        } else {
          const tSw = Math.max(tS + f(6), C("sweep", C("best", tS + 0.5)));
          ft(tl, needle, { rotation: 0 }, { rotation: swDeg, duration: f(22), ease: E.enter }, tSw);
          ft(tl, arc, { strokeDashoffset: L }, { strokeDashoffset: arcAt(swDeg), duration: f(22), ease: E.enter }, tSw);
          gx.ev(ctx, "dial", tSw);
          gx.ev(ctx, "dial_end", tSw + f(18));   // la aguja ya está quieta (80 % del tween power3.out)
          t = tSw + f(22);
        }
        // cue `plate_pulse`: la placa del rótulo late (1 → 1,08 → 1) en esa palabra («cierto valor»).
        //   Sin la cue, nada cambia. Evento `pulse`
        const tPp = plate ? C("plate_pulse", null) : null;
        if (tPp != null && tPp > tS + f(10) && tPp < t1 - f(10)) {
          const at = Math.round(tPp * gx.FPS) / gx.FPS;
          ft(tl, plate, { scale: 1 }, { scale: 1.08, duration: f(4), ease: E.enter }, at);
          ft(tl, plate, { scale: 1.08 }, { scale: 1, duration: f(8), ease: E.move }, at + f(4));
          gx.ev(ctx, "pulse", at);
        }
        const after = lit.filter((x) => x > t + f(8));
        const tStop = C("stop", after.length ? Math.max(...after) : null);
        if (cont) {
          const dec = f(6), PR = { role: "progress" };   // velocidad constante: es tiempo que pasa (no cuenta como ease)
          const tEnd = tStop != null ? Math.min(tStop, t1 - f(2)) : t1 - f(1);
          if (tEnd - t > dec + f(2)) {
            const tLin = tStop != null ? tEnd - dec : tEnd, r1 = rot + stepDeg * (tLin - t);
            ft(tl, needle, { rotation: rot }, { rotation: r1, duration: tLin - t, ease: "none", data: PR }, t);
            ft(tl, arc, { strokeDashoffset: arcAt(rot) }, { strokeDashoffset: arcAt(r1), duration: tLin - t, ease: "none", data: PR }, t);
            rot = r1;
            if (tStop != null) {   // se para en su estación: frenada con la misma velocidad de partida (power3.out)
              const r2 = r1 + stepDeg * dec / 3;
              ft(tl, needle, { rotation: r1 }, { rotation: r2, duration: dec, ease: E.enter }, tLin);
              ft(tl, arc, { strokeDashoffset: arcAt(r1) }, { strokeDashoffset: arcAt(r2), duration: dec, ease: E.enter }, tLin);
              rot = r2;
            }
            t = tEnd;
          }
        }
        // tras la parada, si queda más de 1,2 s: una marca por segundo (nada quieto)
        if (t1 - t > 1.2) for (let tb = t + 0.6; tb < t1 - 0.3; tb += 1.0) {
          ft(tl, needle, { rotation: rot }, { rotation: rot + stepDeg, duration: f(5), ease: E.pop }, tb);
          rot += stepDeg;
        }
        return;
      }
      // ── por defecto: las estaciones (cada una en su palabra) y el barrido de la vuelta (`sweep`/`best`), en orden
      const tSw = C("sweep", C("best", null));
      const evs = stations.map((x, k) => ({ k, t: lit[k] }));
      if (tSw != null) evs.push({ k: -1, t: Math.max(tS + f(6), tSw) });
      evs.sort((a, b) => a.t - b.t);
      let rot = 0, tFree = tS;
      evs.forEach((e) => {
        const at = Math.max(e.t, tFree);
        if (e.k < 0) {   // la vuelta completa: la aguja barre 360° y deja el arco de oro
          ft(tl, needle, { rotation: rot }, { rotation: rot + 360, duration: f(22), ease: E.move }, at);
          ft(tl, arc, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: f(22), ease: E.move }, at);
          rot += 360; tFree = at + f(16);
          gx.ev(ctx, "dial", at);
          gx.ev(ctx, "dial_end", at + f(22));   // (audio): la aguja cierra la vuelta (el arco de oro se completa)
          return;
        }
        const x = stations[e.k];
        light(e.k, at);
        // la aguja señala la estación (siempre en sentido horario)
        let target = rot - (rot % 360) + x.deg;
        while (target <= rot + 1) target += 360;
        ft(tl, needle, { rotation: rot }, { rotation: target, duration: f(9), ease: E.move }, at);
        rot = target; tFree = at + f(6);
      });
      // nada quieto: la aguja avanza una marca por segundo (una hora en 24 h, un segundo en 60) hasta el final del plano
      for (let tb = Math.max(tFree + 0.6, tS + 1.0); tb < t1 - 0.3; tb += 1.0) {
        ft(tl, needle, { rotation: rot }, { rotation: rot + stepDeg, duration: f(5), ease: E.pop }, tb);
        rot += stepDeg;
      }
    }
    return { animate };
  }

  // ── tracks: «…con textos, animaciones y elementos visuales sincronizados» como la LÍNEA DE TIEMPO de un editor
  //    de vídeo. Columna de cabecera a la izquierda (icono del kit en oro, o `mono` «Aa», + rótulo, visibles desde los
  //    primeros fotogramas); a la derecha, la zona de clips con su regla y el cabezal de oro (nunca pasa por encima de los
  //    rótulos). Cada pista tiene UN clip en tinta con su fotograma clave en oro, cada uno en un sitio distinto; el clip
  //    cae en su cue. El cabezal avanza desde el corte y llega a su columna en `sync`: ahí los clips ENTEROS
  //    se deslizan hasta empezar en el cabezal, se encienden en oro y una franja de oro marca la columna (= a tiempo).
  //    A pantalla completa usa la banda entera, centrada en y ≈ 830, sin pasar del borde derecho de la zona segura de los
  //    botones de Shorts/Reels (x ≤ 888); escala hasta 1,2. Solo lo usa este modo: no toca los demás.
  //    Eventos: enter, station (cada clip), best (sync). Todo con estilos en línea.
  function mountTracks(wrap, A, props, ctx) {
    const tr = (props.tracks && props.tracks.length ? props.tracks : [{ label: "Textos", mono: "Aa" }, { label: "Animaciones", glyph: "keys" },
      { label: "Visuales", glyph: "screen" }]).slice(0, 4);
    const n = tr.length;
    const INK = "#161514", GOLD = "#FECA1A", GOLD_D = "#C99A12";
    const CW = ctx.W || 1080, sfR = (ctx.safe && ctx.safe.right) || 192;
    const xr = Math.max(420, Math.min(A.w, R(CW - sfR - A.x)));       // borde derecho del contenido (coordenadas del área)
    const cyL = A.tee || A.full ? R(830 - A.y) : R(A.h / 2);
    // rótulos (se miden para dimensionar la columna de cabecera)
    const labs = tr.map((t) => {
      const e = gx.el("div", "sh-trlabel", wrap, t.label || "");
      Object.assign(e.style, { position: "absolute", left: "0px", top: "0px", whiteSpace: "nowrap", color: INK, letterSpacing: "-.01em" });
      return e;
    });
    // `track_heads: "above"` (con la columna de cabeceras a la
    // izquierda la zona de clips medía ~400 de 823 px): icono y rótulo ENCIMA de cada carril y los carriles a todo el ancho
    // útil (0–xr), más grande (s ≤ 1,6); el cabezal y la franja de sincronía solo se ven sobre la regla y los carriles (no
    // cruzan los rótulos). Sin la prop, igual que antes
    const above = props.track_heads === "above" && (A.tee || A.full);
    let s = above ? 1.6 : 1.2;
    const setS = () => labs.forEach((e) => { e.style.font = `800 ${R(40 * s)}px/1 var(--ck-sans)`; });
    const labW = () => Math.max(...labs.map((e) => e.offsetWidth));
    const fits = () => {
      if (above) {
        const tH = R(30 * s) + R(10 * s) + n * (R(56 * s) + R(14 * s) + R(92 * s)) + (n - 1) * R(30 * s);
        return R(56 * s) + R(16 * s) + labW() <= xr && tH <= A.h * 0.9;
      }
      const zone = xr - (R(56 * s) + R(16 * s) + labW() + R(26 * s));
      const totH = R(30 * s) + R(10 * s) + n * R(92 * s) + (n - 1) * R(32 * s);
      return zone >= 380 && totH <= A.h * 0.92;
    };
    setS();
    for (; s > 0.7 && !fits(); s -= 0.05) setS();
    const S = (v) => R(v * s);
    const icS = S(56), lx = icS + S(16), lW = labW(), zs = above ? 0 : lx + lW + S(26), zw = xr - zs;
    const rulerH = S(30), rg = S(10), laneH = S(92), rowGap = above ? S(30) : S(32);
    const hdH = above ? icS + S(14) : 0;                 // `above`: fila de cabecera (icono + aire) encima de cada carril
    const totH = rulerH + rg + n * (hdH + laneH) + (n - 1) * rowGap;
    const top = R(Math.max(0, Math.min(A.h - totH, cyL - totH / 2)));
    const sync = props.sync_at != null ? Math.max(0.15, Math.min(0.55, +props.sync_at)) : 0.3;
    const X = zs + R(zw * sync);                                         // columna de sincronía
    const CLIP = [[0.42, 0.8], [0.06, 0.48], [0.6, 0.97], [0.2, 0.55]];
    // regla: solo sobre la zona de clips (20 marcas; las de cada 5, más altas)
    const ruler = box(wrap, "sh-trruler", zs, top, zw, rulerH);
    Object.assign(ruler.style, { position: "absolute", borderBottom: `${Math.max(2, S(3))}px solid rgba(22,21,20,.22)` });
    for (let i = 0; i <= 20; i++) {
      const tk = box(ruler, "sh-trtick", R(i * zw / 20) - 1, i % 5 ? R(rulerH * 0.55) : R(rulerH * 0.15), Math.max(2, S(3)), i % 5 ? R(rulerH * 0.45) : R(rulerH * 0.85));
      Object.assign(tk.style, { position: "absolute", background: "rgba(22,21,20,.28)", borderRadius: "2px" });
    }
    const y0 = top + rulerH + rg, lanesH = n * (hdH + laneH) + (n - 1) * rowGap;
    const laneY = (i) => y0 + i * (hdH + laneH + rowGap) + hdH;
    // franja de oro de la columna alineada (detrás de los clips; aparece en sync)
    const band = above ? box(wrap, "sh-trband", X - S(30), laneY(0) - S(8), S(60), laneY(n - 1) + laneH - laneY(0) + S(16))
      : box(wrap, "sh-trband", X - S(30), y0 - S(8), S(60), lanesH + S(16));
    Object.assign(band.style, { position: "absolute", background: above ? "transparent" : "rgba(254,202,26,.32)", borderRadius: S(16) + "px" });
    if (above) tr.forEach((_, i) => {   // un tramo de franja por carril (nada de oro sobre los rótulos)
      const seg = box(band, "sh-trbandseg", 0, laneY(i) - laneY(0), S(60), laneH + S(16));
      Object.assign(seg.style, { position: "absolute", background: "rgba(254,202,26,.32)", borderRadius: S(16) + "px" });
    });
    const rows = tr.map((t, i) => {
      const y = laneY(i);
      const head = above ? box(wrap, "sh-trhead", 0, y - hdH, xr, icS) : box(wrap, "sh-trhead", 0, y, zs - S(12), laneH);
      Object.assign(head.style, { position: "absolute" });
      const ic = box(head, "sh-tric", 0, above ? 0 : R((laneH - icS) / 2), icS, icS);
      Object.assign(ic.style, { position: "absolute", background: "#FFFFFF", borderRadius: R(icS * 0.26) + "px",
        boxShadow: "0 0 0 1px rgba(22,21,20,.08), 0 6px 16px rgba(0,0,0,.10)", display: "flex", alignItems: "center", justifyContent: "center" });
      if (t.mono) {
        const m = gx.el("div", "sh-trmono", ic, String(t.mono).slice(0, 3));
        Object.assign(m.style, { font: `800 ${S(30)}px/1 var(--ck-sans)`, color: GOLD_D, letterSpacing: "-.02em" });
      } else {
        const g = gx.icon(ic, ctx, { asset: t.asset, glyph: t.glyph || "screen", tone: "gold" }, "sh-tr-ic");
        Object.assign(g.style, { width: R(icS * 0.66) + "px", height: R(icS * 0.66) + "px" });
      }
      const lb = labs[i];
      head.appendChild(lb);
      Object.assign(lb.style, { left: lx + "px", top: "0px", height: (above ? icS : laneH) + "px", display: "flex", alignItems: "center" });
      const lane = box(wrap, "sh-trlane", zs, y, zw, laneH);
      Object.assign(lane.style, { position: "absolute", background: "#ECEAE6", borderRadius: S(18) + "px" });
      const c = CLIP[i % CLIP.length], cx = R(c[0] * zw), ch = laneH - S(24);
      const clip = box(lane, "sh-trclip", cx, S(12), R((c[1] - c[0]) * zw), ch);
      Object.assign(clip.style, { position: "absolute", background: INK, borderRadius: S(12) + "px", boxShadow: "0 4px 10px rgba(0,0,0,.12)" });
      const kS = S(30);
      const key = box(clip, "sh-trkey", -R(kS / 2), R((ch - kS) / 2), kS, kS);   // en el borde de entrada del clip
      Object.assign(key.style, { position: "absolute", background: GOLD, borderRadius: S(5) + "px" });
      gsap.set(key, { rotation: 45 });    // rombo (fotograma clave); la rotación vive en GSAP para no perderla en los tweens
      gsap.set(clip, { transformOrigin: "0% 50%" });
      return { head, key, lane, clip, left: zs + cx, w: R((c[1] - c[0]) * zw) };
    });
    // cabezal: solo sobre la zona de clips (de la regla a la última pista)
    const phTop = top - S(6), phBot = y0 + lanesH + S(10);
    const ph = box(wrap, "sh-trph", X - S(3), phTop, S(6), phBot - phTop);
    Object.assign(ph.style, { position: "absolute", background: above ? "transparent" : GOLD_D, borderRadius: S(3) + "px", boxShadow: above ? "none" : "0 0 0 1px rgba(22,21,20,.10)" });
    if (above) [[phTop, y0], ...tr.map((_, i) => [laneY(i) - S(6), laneY(i) + laneH + S(6)])].forEach(([a, b]) => {   // tramos: regla y carriles
      const seg = box(ph, "sh-trphseg", 0, a - phTop, S(6), b - a);
      Object.assign(seg.style, { position: "absolute", background: GOLD_D, borderRadius: S(3) + "px", boxShadow: "0 0 0 1px rgba(22,21,20,.10)" });
    });
    const knob = box(ph, "sh-trknob", -S(17), -S(4), S(40), S(30));
    Object.assign(knob.style, { position: "absolute", background: GOLD, borderRadius: `${S(8)}px ${S(8)}px ${S(20)}px ${S(20)}px`,
      boxShadow: `0 0 0 ${Math.max(2, S(3))}px ${GOLD_D}` });
    const x0 = zs + S(6) - X;    // el cabezal arranca al principio de la zona de clips
    gsap.set(rows.map((r) => r.head), { opacity: 0 });
    gsap.set(rows.map((r) => r.clip), { scaleX: 0 });
    gsap.set(rows.map((r) => r.key), { opacity: 0 });
    gsap.set([ruler, ph].concat(rows.map((r) => r.lane)), { opacity: 0 });
    gsap.set(band, { opacity: 0, scaleY: 0.6 });
    gsap.set(ph, { x: x0 });

    function animate(tl, tS, t1, cues, E) {
      const C = (k, d) => gx.cue(cues, k, d);
      // en el corte: regla, pistas y cabezal (formas sin texto); los rótulos suben enseguida (escalonados 2 f)
      // `track_in: "cue"` (con los tres carriles y rótulos ya en el
      // corte, «Visuales» se leía 2,1 s antes de decirse): en el corte solo la regla y el cabezal; la cabecera y
      // el carril de cada pista entran en SU cue (k<i>), con su clip. Sin la prop, igual que antes
      const byCue = props.track_in === "cue";
      gx.cutIn(tl, byCue ? [ruler, ph] : [ruler, ph].concat(rows.map((r) => r.lane)), tS);
      if (!byCue) rows.forEach((r, i) => gx.textIn(tl, r.head, tS + i * f(2)));
      const tk = rows.map((_, i) => Math.max(tS + f(8) + i * f(4), C("k" + i, tS + 0.3 + i * 0.5)));
      if (byCue) rows.forEach((r, i) => {
        const tL = Math.max(tS, tk[i] - f(3));
        ft(tl, r.lane, { opacity: 0 }, { opacity: 1, duration: f(5), ease: E.enter }, tL);
        gx.textIn(tl, r.head, tL);
      });
      rows.forEach((r, i) => {
        ft(tl, r.clip, { scaleX: 0 }, { scaleX: 1, duration: f(7), ease: E.enter }, tk[i]);
        ft(tl, r.key, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, tk[i] + f(5));
        gx.ev(ctx, "station", tk[i]);
      });
      const tSync = Math.max(tk[n - 1] + f(12), C("sync", t1 - 1.0));
      // el cabezal avanza desde el corte y llega a su columna en sync
      ft(tl, ph, { x: x0 }, { x: 0, duration: Math.max(f(8), tSync - tS - f(2)), ease: E.move }, tS + f(2));
      // sync: los clips enteros se deslizan hasta empezar en el cabezal y se encienden en oro (el rombo, en tinta)
      rows.forEach((r, i) => {
        ft(tl, r.clip, { x: 0 }, { x: X - r.left, duration: f(10), ease: E.move }, tSync);   // el clip EMPIEZA en el cabezal
        // `sync_equal`: en sync los clips quedan del MISMO largo (la media). Sin la prop, cada uno el suyo
        if (props.sync_equal) ft(tl, r.clip, { width: r.w }, { width: R(rows.reduce((a, q) => a + q.w, 0) / n), duration: f(10), ease: E.move }, tSync);
        ft(tl, r.clip, { backgroundColor: INK }, { backgroundColor: GOLD, duration: f(6), ease: E.enter }, tSync + f(8) + i * f(1));
        ft(tl, r.key, { backgroundColor: GOLD }, { backgroundColor: INK, duration: f(6), ease: E.enter }, tSync + f(8) + i * f(1));
      });
      ft(tl, band, { opacity: 0, scaleY: 0.6 }, { opacity: 1, scaleY: 1, duration: f(10), ease: E.enter }, tSync + f(8));
      ft(tl, knob, { scale: 1 }, { scale: 1.25, duration: f(4), ease: E.enter }, tSync + f(10));
      ft(tl, knob, { scale: 1.25 }, { scale: 1, duration: f(8), ease: E.move }, tSync + f(14));
      gx.ev(ctx, "best", tSync);
      // nada quieto: después, la franja respira (una vez por segundo) hasta el final
      for (let tb = tSync + f(28); tb + 0.9 < t1 - f(5); tb += 1.0) {
        ft(tl, band, { opacity: 1 }, { opacity: 0.55, duration: 0.45, ease: E.move }, tb);
        ft(tl, band, { opacity: 0.55 }, { opacity: 1, duration: 0.45, ease: E.move }, tb + 0.45);
      }
    }
    return { animate };
  }

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
  CK.register("viz.shapes", {
    clip: "panel",   // en el split, recortado a la junta: nada vuela sobre la cara
    mount(root, props, ctx) {
      const mode = props.mode || "morph";
      const st = gx.stage(root, ctx, props, "sh sh-" + mode);
      // con `scale_max`, el bucle usa la banda ENTERA de pantalla
      // completa (288–1240) en vez de la alta (288–1000): con la alta (712 px) el tope por alto dejaba el aro en ~470 px
      // por mucho que subiera scale_max. Sin `scale_max`, igual que antes. `tracks` también usa la
      // banda entera: se centra en y ≈ 830 y se queda dentro de la zona segura de los botones (x ≤ 888)
      const A = (mode === "loop" && props.scale_max) || mode === "tracks" ? st.A : gx.upper(st.A), bd = st.bd;
      const wrap = gx.el("div", "sh-wrap", A.node);
      const api = mode === "hub" ? mountHub(wrap, A, props, ctx) : mode === "loop" ? mountLoop(wrap, A, props, ctx)
        : mode === "dial" ? mountDial(wrap, A, props, ctx) : mode === "tracks" ? mountTracks(wrap, A, props, ctx)
        : mountMorph(wrap, A, props, ctx);
      return zoomWrap(A, props, {
        animate(tl, t0, t1, cues) {
          const E = gx.eases(ctx);
          const tS = gx.settle(ctx, t0);
          gx.ev(ctx, "enter", tS);
          api.animate(tl, tS, t1, cues, E);
          gx.bgIn(tl, bd, t0, t1, 53, props);
          gx.out(tl, props, t1, [wrap], { dur: f(5), ctx });
        },
      });
    },
  });
})(window.CK);
