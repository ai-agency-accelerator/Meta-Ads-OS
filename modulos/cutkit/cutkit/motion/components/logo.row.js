// logo.row — varios logos que se encienden cada uno en SU palabra (Nimbo, Acme, Orbita). Estado 0 visible desde t0:
// las baldosas ya están, en fantasma (parecían imágenes rotas), y se encienden al
// nombrarlas. Cue `off`: las encendidas vuelven a fantasma (evento off).
// Baldosas iguales y grandes (la fila ocupa el ancho del panel); asentamiento corto solo en la baldosa.
// Items sin `asset` → baldosa de TEXTO del mismo tamaño y estilo, con un glifo neutro (sobre, bocadillo, onda) o un
// monograma; nunca un icono de marca inventado. Pantalla completa: baldosas grandes (2–3 → ~300–360 px) y, con 4–5,
// rejilla en 2 filas (2+2, 3+2) con posiciones fijas desde el inicio; en una fila, reacomodo suave (8 f) al llegar.
// Etiquetas, todas al mismo cuerpo (el menor que quepa en una línea, ≥48 px; si no cabe, 2 líneas a 48).
// props: {items:[{label, asset?, glyph?: mail|chat|wave|text}], size?: px, compact?, labels?: bool (true),
//         ghost?: bool (true), canvas?, backdrop?, exit?: "cut"}
// cues: off: las baldosas encendidas vuelven a fantasma y los rótulos quedan al 35 % (evento off)
// cues:  <label en minúsculas> (nimbo, acme, orbita…) o i0, i1…; merge
// `connect` (circuito de tinta + oro de baldosa en baldosa, dibujado en la entrada de cada una, con un pulso
//   que lo recorre mientras dura el plano; evento connect) y `merge` ({asset|glyph, label}: en su cue las baldosas vuelan
//   al centro y se juntan en un icono final; evento merge).
// glifo `coin` (moneda con «$»,
//   de este componente); item `hot` (baldosa con aro de oro y rótulo en oro: el foco del plano); cue `dim` con
//   `dim_items: [i…]` (esas baldosas y sus rótulos bajan al 38 % sin desaparecer: «no solo X, sino también…»; evento
//   off); item `grow: {from, to, scale?}` (entre esas dos cues la baldosa crece a saltos, como un contador sin cifra,
//   hasta `scale` (1,14); evento grow).
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
  const key = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "");
  // glifos neutros (trazo de tinta) para baldosas sin logo
  const GLYPH = {
    mail: '<rect x="6" y="11" width="36" height="26" rx="4"/><path d="M7 13 L24 26 L41 13"/>',
    chat: '<path d="M9 10 H39 a4 4 0 0 1 4 4 V30 a4 4 0 0 1 -4 4 H22 L13 41 V34 H9 a4 4 0 0 1 -4 -4 V14 a4 4 0 0 1 4 -4 Z"/><path d="M15 20 H33 M15 26 H27"/>',
    wave: '<path d="M6 24 V24 M12 18 V30 M18 12 V36 M24 16 V32 M30 9 V39 M36 17 V31 M42 22 V26"/>',
    // moneda con «$» (coste, precio; nunca una marca)
    coin: '<circle cx="24" cy="24" r="18"/><path d="M29.6 17.6 C28.2 16.1 26.2 15.4 24 15.4 C20.8 15.4 18.6 17.1 18.6 19.6 C18.6 25.4 29.6 22.5 29.6 28.4 C29.6 31 27.2 32.6 24 32.6 C21.6 32.6 19.5 31.8 18 30.3 M24 11.6 V15.4 M24 32.6 V36.4"/>',
  };
  // (una baldosa con siglas junto a un icono real imitaba un icono de marca → marca inventada): sin
  // logo, SIEMPRE un glifo neutro del kit (`keys`, `terminal`, `braces`, `screen`…); el monograma solo si el plan lo pide
  // con `glyph: "text"` (nunca para una marca de terceros).
  const pathOf = (g) => GLYPH[g] || (gx.GLYPHS && gx.GLYPHS[g]) || null;
  const KW = [[/email|correo|gmail|mail/, "mail"], [/sms|mensaje|chat|whatsapp/, "chat"], [/voz|voice|llamada|telefono|audio/, "wave"],
    [/^(cli|terminal|consola|comandos?|shell|bash)$/, "terminal"], [/^(json|codigo|code|api)$/, "braces"],
    [/aftereffects|keyframes?|fotogramasclave|^animacion(es)?$/, "keys"]];
  const glyphOf = (it) => {
    if (it.glyph === "text" || it.glyph === "mono") return "text";
    if (it.glyph && pathOf(it.glyph)) return it.glyph;
    const k = key(it.label);
    for (const [re, g] of KW) if (re.test(k)) return g;
    return "screen";
  };
  const mono = (label) => { const w = String(label || "").trim().split(/\s+/).filter(Boolean); return (w.length > 1 ? w[0][0] + w[w.length - 1][0] : (w[0] || "?").slice(0, 3)).toUpperCase(); };

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
  CK.register("logo.row", {
    mount(root, props, ctx) {
      const E = gx.eases(ctx);
      const st = gx.stage(root, ctx, props, "lr" + (props.compact ? " lr-compact" : "") + (props.ghost === true ? " lr-ghosts" : ""));
      const A = st.A, bd = st.bd;
      const items = (props.items || []).slice(0, 5);
      const n = Math.max(1, items.length);
      const tall = A.h >= 700;                                   // pantalla completa (banda alta o centrada)
      // `rows`: reparto explícito por filas (p. ej. [2, 3]: «Nimbo o Acme» arriba, los canales abajo)
      const want = Array.isArray(props.rows) ? props.rows.map((x) => Math.max(1, x | 0)) : null;
      const rows = want && want.reduce((a, b) => a + b, 0) === n ? want
        : (tall && n >= 4 ? (n === 4 ? [2, 2] : [3, 2]) : [n]);
      const perRow = Math.max(...rows);
      // `row_gap` (px, a pantalla completa): hueco entre filas (56 por
      //   defecto); más bajo = baldosas más grandes en una columna 1+1+1
      // `stack_gap` (px, 60–200, a pantalla completa): hueco
      //   entre filas que manda sobre row_gap (el circuito recto de una columna medía ~30 px: con 140, ≥ 90 px). Sin la prop, igual
      const rowGap0 = tall && Number(props.stack_gap) > 0 ? Math.max(60, Math.min(200, Number(props.stack_gap)))
        : tall && Number(props.row_gap) > 0 ? Math.max(8, Math.min(56, Number(props.row_gap))) : 56;
      // `split_row_gap` (px): hueco entre filas FUERA de pantalla
      //   completa (en el 50/50 era 0 y los rótulos de la fila de arriba tocaban las baldosas de abajo). Sin la prop, 0
      const splitGap = Number(props.split_row_gap) > 0 ? Math.max(8, Math.min(80, Number(props.split_row_gap))) : 0;
      // `label_gap` (px, 6–26): hueco baldosa → rótulo (26 por defecto);
      //   el alto reservado al rótulo baja lo mismo (baldosas algo mayores): cada rótulo queda pegado a SU baldosa y lejos de
      //   la siguiente. Sin la prop, nada cambia
      const lGap = props.labels !== false && Number(props.label_gap) > 0 ? Math.max(6, Math.min(26, Number(props.label_gap))) : null;
      const gap = R(tall ? 40 : 36), rowGap = R(tall ? rowGap0 : splitGap), labH = props.labels === false ? 0 : 84 - (lGap != null ? 26 - lGap : 0);
      // región vertical: en rejilla (2 filas) toda la banda útil desde y=288 hasta el raíl de subtítulos; en una fila, el área
      const railLim = ctx.railY && ctx.railY > A.y + 200 ? ctx.railY - 60 : A.y + A.h;
      const regTop = rows.length > 1 ? Math.min(0, 288 - A.y) : 0, regBot = Math.min(A.h, railLim - A.y);
      const regH = regBot - regTop;
      const cap = props.size || (props.compact ? 250 : tall ? (n <= 2 ? 360 : n === 3 ? 320 : 300) : 280);
      let tile = R(Math.min(cap, (A.w - (perRow - 1) * gap) / perRow, (regH * 0.96 - rows.length * labH - (rows.length - 1) * rowGap) / rows.length, rows.length > 1 ? 1e9 : A.h * 0.55));
      // `cy`: el bloque se centra en esa y del lienzo (p. ej. 960) con las filas fijas desde el corte (sin el
      // salto vertical al nacer la segunda fila); en la «T» todas las filas caben en 696 px
      const cyMode = typeof props.cy === "number" && props.cy > 0;
      if (cyMode && A.tee) tile = R(Math.min(tile, A.wLow / perRow - gap * 0.5));
      // rejilla con una fila inferior ancha (p. ej. [2, 3]: Chat, Email, SMS abajo) en pantalla completa: si no cabe en
      // los 696 px de debajo de y=1000, toda la rejilla sube por encima de y=1000 (ancho completo) con baldosas que quepan
      let above = false, aTop = regTop, aBot = regBot;
      if (A.tee && rows.length > 1 && rows.slice(1).some((k) => k * (tile + gap * 0.5) > A.wLow)) {
        above = true; aTop = Math.min(0, 288 - A.y); aBot = Math.min(regBot, A.yLow - 28);   // margen: la entrada baja 16 px
        tile = R(Math.min(tile, ((aBot - aTop) * 0.98 - rows.length * labH - (rows.length - 1) * rowGap) / rows.length));
      }
      // `connect`: true (todas en orden), [i, j, k] (esas, en cadena) o [[2, 3], [3, 4]]
      const okI = (k) => Number.isInteger(k) && k >= 0 && k < items.length;
      const cp = props.connect;
      const pairs = cp === true ? items.slice(1).map((_, i) => [i, i + 1])
        : Array.isArray(cp) && cp.length && Array.isArray(cp[0]) ? cp.filter((q) => Array.isArray(q) && q.length === 2 && okI(q[0] | 0) && okI(q[1] | 0) && q[0] !== q[1]).map((q) => [q[0] | 0, q[1] | 0])
        : Array.isArray(cp) ? cp.map((k) => k | 0).filter(okI).slice(1).map((k, i, a) => [i === 0 ? (cp.map((x) => x | 0).filter(okI))[0] : a[i - 1], k]) : [];
      const connIdx = Array.from(new Set(pairs.flat()));
      if (connIdx.length > 1) {
        const rowOf = (i) => { let acc = 0; for (let r = 0; r < rows.length; r++) { acc += rows[r]; if (i < acc) return r; } return rows.length - 1; };
        new Set(connIdx.map(rowOf)).forEach((r) => {
          const lim = ((r > 0 || cyMode) && A.tee && !above ? A.wLow : A.w) / rows[r];
          tile = R(Math.min(tile, lim / 1.42));
        });
      }
      A.node.style.setProperty("--tile", tile + "px");
      A.node.style.setProperty("--gap", gap + "px");
      const wrap = gx.el("div", "lr-wrap" + (rows.length > 1 ? " lr-grid" : ""), A.node);
      if (cyMode) { // caja simétrica alrededor de cy (el contenido flex se centra en ella aunque la desborde)
        const c = props.cy - A.y, hh = Math.max(40, Math.min(c, A.h - c));
        aTop = R(c - hh); aBot = R(c + hh);
      }
      Object.assign(wrap.style, { top: aTop + "px", bottom: (A.h - aBot) + "px" });
      if (rows.length > 1) wrap.style.rowGap = rowGap + "px";
      // ancho de celda por fila: usa el ancho útil (etiquetas en una línea), pero la fila que quede por debajo de y=1000
      // (la segunda de la rejilla) cabe en 696 px
      // `cell_gap` (el 2 × 2 tenía columnas distintas arriba y abajo):
      // rejilla de verdad: cada celda mide lo que su baldosa y entre columnas hay `cell_gap` px (las mismas columnas en todas
      // las filas). Sin la prop, igual que antes
      const cGap = Number(props.cell_gap) > 0 ? Math.max(16, Math.min(200, Number(props.cell_gap))) : 0;
      const cellW = (r) => cGap ? tile : R(Math.max(tile + gap * 0.5, Math.min(A.w / rows[r], (r > 0 || cyMode) && A.tee && !above ? A.wLow / rows[r] : 1e9, tile * 1.45)));
      const rowEls = rows.map(() => gx.el("div", "lr-row", wrap));
      if (cGap) rowEls.forEach((e) => { e.style.gap = cGap + "px"; });
      let ri = 0, used = 0;
      const cells = items.map((it) => {
        if (used >= rows[ri]) { ri++; used = 0; }
        used++;
        const c = gx.el("div", "lr-cell" + (it.hot ? " lr-hot" : ""), rowEls[ri]);
        c.style.width = cellW(ri) + "px"; c.dataset.row = ri;
        if (lGap != null) c.style.gap = lGap + "px";
        // fantasma (estado 0): SOLO el contorno (con el «?» las
        // ranuras se leían como imágenes rotas)
        const slot = gx.el("div", "lr-slot", c);
        const t = gx.el("div", "lr-tile", c);
        if (it.asset) {
          const lg = gx.logo(t, ctx, it.asset, "lr-logo");
          // `items[].fill` (0,62–0,9): fracción de la baldosa que ocupa el icono (0,62 por defecto, el
          //   inset del 19 %); p. ej. 0,84 para un objeto apaisado (las monedas) que a 0,62 se quedaba en ~58 % de la baldosa
          const fl = Number(it.fill);
          if (fl >= 0.62 && fl <= 0.9) lg.style.inset = ((1 - fl) * 50).toFixed(2) + "%";
        } else { // baldosa sin logo: glifo neutro (monograma solo con glyph: "text")
          const g = glyphOf(it), P = g === "text" ? null : pathOf(g);
          if (P) { const sv = gx.svg("svg", { viewBox: "0 0 48 48", class: "lr-glyph lr-g-" + g }, t); sv.innerHTML = P; }
          else gx.el("div", "lr-mono", t, mono(it.label));
          t.classList.add("lr-textile");
        }
        const lab = props.labels === false ? null : gx.el("div", "lr-label", c, it.label || "");
        return { it, c, slot, t, lab };
      });
      const ghost = props.ghost === true;
      // `connect`: circuito de tinta + oro de baldosa en baldosa (true = todas en orden; [i, j…] = solo esas)
      const conn = pairs.length ? connIdx : null;
      // en UNA fila, el circuito vive dentro de la fila (se reacomoda con ella); si cruza filas, en el área y esas filas
      // quedan fijas desde el corte
      const connRows = conn ? Array.from(new Set(conn.map((i) => +cells[i].c.dataset.row))) : [];
      const inRow = connRows.length === 1 ? rowEls[connRows[0]] : null;
      const wires = conn ? gx.svg("svg", { class: "lr-wires", width: inRow ? 10 : A.w, height: inRow ? 10 : A.h }, inRow || A.node) : null;
      if (wires) { if (inRow) cells.forEach((x) => { x.c.style.zIndex = "1"; }); else wrap.style.zIndex = "2"; }
      // `merge`: en su cue, las baldosas se juntan en UN icono final ({asset|glyph, label?, tone?})
      const mg = props.merge && typeof props.merge === "object" ? props.merge : null;
      let mBox = null, mLab = null;
      if (mg) {
        mBox = gx.el("div", "lr-merge lr-tile", A.node);
        gx.icon(mBox, ctx, { asset: mg.asset, glyph: mg.glyph || (mg.asset ? null : "gear"), tone: mg.tone || (mg.asset ? "color" : "gold") }, "lr-merge-ic");
        if (mg.label) { const mm = gx.el("div", "lr-mlab-m", A.node); mLab = { m: mm, i: gx.el("div", "lr-label lr-mlab", mm, mg.label) }; }
        gsap.set(mBox, { opacity: 0 });
        if (mLab) gsap.set(mLab.i, { opacity: 0 });
      }
      gsap.set(cells.map((x) => x.t), { opacity: 0 });
      cells.forEach((x) => { if (x.lab) gsap.set(x.lab, { opacity: 0 }); gsap.set(x.slot, { opacity: 0 }); });

      return zoomWrap(A, props, {
        animate(tl, t0, t1, cues) {
          const ex = f(5);
          // etiquetas: todas al MISMO cuerpo, el menor que quepa en una línea (≥48 px); si no, 2 líneas a 48
          const colW = R(Math.min(...cells.map((x) => x.c.offsetWidth)) - 8);
          const labs = cells.map((x) => x.lab).filter(Boolean);
          const maxPx = props.compact ? 56 : (tall ? 64 : 60);
          // Regla de estilo: cada rótulo en UNA línea («Agente de Voz»): todas al mismo cuerpo hasta 38 px antes de partir; si hay que
          // partir, se parten TODAS en dos líneas equilibradas (mismo número de líneas en el grupo, gx.lineParity)
          // hueco entre rótulos vecinos ≥ 0,25 × baldosa: cada rótulo cabe en su celda menos ese hueco; si no
          // cabe, baja el cuerpo de TODO el grupo (`label_px` = tope)
          // («Editor de Imagen / Editor de Vídeo» a ~41 px): a pantalla
          // completa, si con el hueco de 0,25 × baldosa no caben en una línea a ≥ 48 px, se prueba el hueco REAL entre
          // vecinos (centros medidos) de 1 em y dentro de la banda segura (696 px en la «T»): «Editor de Vídeo» queda en una
          // línea a 48 px junto a «Editor de Imagen». Si ni así caben, lo de antes (una línea hasta 38 px; luego dos)
          // `label_min`: cuerpo mínimo antes de partir (38 por defecto)
          const LMIN = Number.isFinite(Number(props.label_min)) && Number(props.label_min) > 0 ? Math.max(30, Math.min(72, Number(props.label_min))) : 38;
          let lpo = { max: Math.max(props.label_px || maxPx, LMIN), min: LMIN, min2: LMIN, width: (n) => Math.max(60, n.parentElement.offsetWidth - R(tile * 0.25)), group: "logo.row" };
          if (tall && labs.length && lpo.max >= 48) {
            const AR0 = A.node.getBoundingClientRect(), half = (A.tee ? A.wLow : A.w) / 2, cx0 = A.x + A.w / 2;
            // `label_band: "row"`: cada rótulo se mide contra el ancho
            //   seguro de SU altura (todo el ancho del área si acaba por encima de y=1000; 696 px si no), con margen por lo
            //   que crece al subir de cuerpo. Sin la prop, 696 px para todos (lo de siempre)
            const bandRow = props.label_band === "row" && !!A.tee;
            const meas = labs.map((l) => { l.style.fontSize = "48px"; l.style.whiteSpace = "nowrap";
              const c = l.parentElement.getBoundingClientRect(); return { l, w48: l.scrollWidth, cx: c.left - AR0.left + A.x + c.width / 2, row: l.parentElement.dataset.row, bot48: l.getBoundingClientRect().bottom - AR0.top }; });
            const std = meas.every((m) => m.w48 <= m.l.parentElement.offsetWidth - R(tile * 0.25) + 0.5);
            if (!std) {
              const ok = (px) => meas.every((m, i) => {
                const w = m.w48 * px / 48;
                const hh = bandRow && m.bot48 + (px - 48) * 1.6 <= A.yLow ? A.w / 2 : half;
                if (m.cx - w / 2 < cx0 - hh - 0.5 || m.cx + w / 2 > cx0 + hh + 0.5) return false;
                const nx = meas[i + 1];
                return !nx || nx.row !== m.row || (nx.cx - m.cx) - (w + nx.w48 * px / 48) / 2 >= px;
              });
              let pick = null;
              for (let px = Math.floor(lpo.max); px >= Math.max(48, LMIN) && pick == null; px--) if (ok(px)) pick = px;
              if (pick != null) lpo = Object.assign(lpo, { max: pick, min: pick, min2: pick, width: (n) => (meas.find((m) => m.l === n) || { w48: 9999 }).w48 * pick / 48 + 2 });
            }
          }
          // `label_two_px` (px, 64–120): a pantalla completa, TODOS
          //   los rótulos en dos líneas equilibradas (gx.lineParity, mismo cuerpo) al mayor cuerpo ≤ esa cifra con el que cada
          //   rótulo, MEDIDO ya colocado, cabe en el ancho seguro de su altura (en la «T»: el área entera si acaba por encima de
          //   y=1000; 696 px si no), nunca bajo `label_min`: frases largas en una columna 1+1+1 a ~90 px en vez de una línea a
          //   ~63. Sin la prop, nada cambia
          const L2 = Number(props.label_two_px);
          if (tall && labs.length && L2 >= 64) {
            const L2max = Math.min(120, L2), L2min = Math.min(L2max, LMIN), AR = A.node.getBoundingClientRect();
            const hl = (A.tee ? A.wLow : A.w) / 2, c2 = A.w / 2;
            const fits = () => labs.every((l) => {
              const q = l.getBoundingClientRect(), x0 = q.left - AR.left, x1 = q.right - AR.left, y1 = q.bottom - AR.top;
              const h = A.tee && y1 <= A.yLow ? A.w / 2 : hl;
              return x0 >= c2 - h - 0.5 && x1 <= c2 + h + 0.5;
            });
            for (let p = L2max; p >= L2min; p--) {
              gx.lineParity(labs, { max: p, min: 1e4, min2: p, lines: 2, width: () => A.w, group: "logo.row" });
              if (fits()) break;
            }
            lpo = null;
          }
          if (labs.length && lpo) gx.lineParity(labs, lpo);
          cells.forEach((x) => { if (x.t.classList.contains("lr-textile")) { const m = x.t.querySelector(".lr-mono"); if (m) gx.fit(m, { max: R(tile * 0.36), min: 30, width: tile * 0.78, lines: 1 }); } });
          // banda en «T»: lo que mida más de 696 px acaba por encima de y=1000 (una fila: se centra y sube lo justo)
          if (cyMode) { /* centrado en cy: sin recolocar */ }
          else if (rows.length === 1) gx.tfit(A, wrap, 1, null, { blocks: () => rowEls });
          else if (A.tee && !above) { // rejilla: la primera fila (ancha) por encima de y=1000
            const r0 = rowEls[0], b0 = wrap.offsetTop + r0.offsetTop + r0.offsetHeight;
            if (r0.offsetWidth > A.wLow + 1 && b0 > A.yLow) { const d = Math.max(-(wrap.offsetTop + r0.offsetTop - (288 - A.y)), A.yLow - b0); wrap.style.top = (regTop + d) + "px"; wrap.style.bottom = (A.h - regBot - d) + "px"; }
          }
          const tS = gx.settle(ctx, t0);
          // `ghost: true`: TODAS las ranuras en fantasma desde el corte (el contorno entra en 6 f; sin «?»
          // con la regla de texto) y cada una se enciende en su palabra; las baldosas no se mueven (sin recentrado)
          // (puede haber ~2,9 s de ranuras antes de la primera herramienta): entrada
          // ESCALONADA (4 f entre ranuras, 8 f, sube 12 px) y, mientras esperan, el contorno RESPIRA (opacidad 1 → 0,5 y escala
          // 1 → 0,985, ciclo de 1,3 s, desfasado entre ranuras); solo respiraciones completas antes de que se encienda su baldosa
          const gIn = (i) => tS + i * f(4);
          if (ghost) {
            cells.forEach((x, i) => {
              ft(tl, x.slot, { opacity: 0, scale: 0.92, y: 12 }, { opacity: 1, scale: 1, y: 0, duration: f(8), ease: E.enter }, gIn(i));
            });
            gx.ev(ctx, "enter", tS);   // (el corte a las ranuras entraba mudo)
          }
          const step = Math.min(0.5, (t1 - t0 - 1) / n);
          const times = cells.map((x, i) => {
            const at = Math.max(tS + f(1), gx.cue(cues, key(x.it.label), gx.cue(cues, "i" + i, t0 + f(4) + i * step)));
            return i === 0 && !ghost && at - tS <= 0.6 ? tS : at;   // nunca un panel vacío: la primera, en el corte
          });
          // TODAS las baldosas con el mismo pop de 8 f, también la primera (antes la
          // primera entraba «en el corte» con cutIn); el rótulo sube 7 f, 3 f después del pop de su baldosa
          cells.forEach((x, i) => {
            const at = times[i];
            gx.ev(ctx, "logo", at);
            if (i === 0 && at <= tS + 1e-3) tl.set(x.c, { opacity: 1 }, T(tS));
            // `first_from` (0,4–1): la PRIMERA baldosa, si entra en el corte, ya se ve en ese fotograma
            //   (opacidad first_from, escala 0,92 → 1): ningún fotograma en blanco en el relevo. Sin la prop, lo de siempre
            const ff = Number(props.first_from);
            if (i === 0 && at <= tS + 1e-3 && ff >= 0.4 && ff <= 1) ft(tl, x.t, { opacity: ff, scale: 0.92, y: 0 }, { opacity: 1, scale: 1, y: 0, duration: f(8), ease: E.pop }, at);
            else ft(tl, x.t, { opacity: 0, scale: 0.8, y: R(16) }, { opacity: 1, scale: 1, y: 0, duration: f(8), ease: E.pop }, at);
            if (ghost) tl.to(x.slot, { opacity: 0, duration: f(3), ease: E.exit }, at + f(2));
            if (x.lab) gx.textIn(tl, x.lab, at + f(3), { frames: 7 });
            if (x.t.querySelector(".cur")) gx.blink(tl, x.t, at + f(8), t1 - f(5));   // `terminal`: el cursor parpadea
          });
          if (ghost) {
            const per = 1.3;
            cells.forEach((x, i) => {
              const end = times[i] - f(1);
              for (let tb = gIn(i) + f(12) + i * per * 0.4; tb + per <= end; tb += per) {
                ft(tl, x.slot, { opacity: 1, scale: 1 }, { opacity: 0.5, scale: 0.985, duration: per / 2, ease: E.move }, tb);
                ft(tl, x.slot, { opacity: 0.5, scale: 0.985 }, { opacity: 1, scale: 1, duration: per / 2, ease: E.move }, tb + per / 2);
              }
            });
          }
          // siempre centrado con lo que ya ha entrado (sin fantasmas):
          //  · cada fila se centra en horizontal con sus baldosas presentes (reacomodo suave de 8 f al llegar otra);
          //  · el bloque se centra en vertical con las filas que existen: mientras solo hay una, baja media fila; cuando
          //    nace la segunda, la primera sube (8 f). Con todos los items, la composición final es la de siempre.
          // `reserve`: cada baldosa nace en su sitio FINAL
          //   (las filas no se recentran al llegar la siguiente: nada salta 240 px). Sin la prop, igual que antes
          if (!ghost && !props.reserve) {
            rowEls.forEach((row, r) => {
              if (wires && !inRow && connRows.indexOf(r) >= 0) return;   // circuito entre filas: tablero fijo
              const idx = cells.map((x, i) => (+x.c.dataset.row === r ? i : -1)).filter((i) => i >= 0);
              if (!idx.length) return;
              const Cw = row.clientWidth / 2;
              const shift = (k) => { const a = cells[idx[0]].c, b = cells[idx[k - 1]].c; return R(Cw - (a.offsetLeft + b.offsetLeft + b.offsetWidth) / 2); };
              tl.set(row, { x: shift(1) }, T(Math.max(0.001, times[idx[0]] - f(1))));
              // (una baldosa con siglas entraba cortada por el borde): la fila HACE SITIO antes y el
              // recentrado ACABA cuando entra la baldosa nueva (empieza ≤ 8 f antes, nunca antes de que la anterior se pose)
              for (let k = 2; k <= idx.length; k++) {
                const tNew = times[idx[k - 1]], a = Math.max(times[idx[k - 2]] + f(2), tNew - f(8));
                ft(tl, row, { x: shift(k - 1) }, { x: shift(k), duration: Math.max(f(3), tNew - a), ease: E.move }, a);
              }
            });
            if (rowEls.length > 1 && !cyMode) {   // con `cy`, filas fijas: la segunda nace en su sitio, sin salto
              const r0 = rowEls[0], r1 = rowEls[1];
              // `solo_size`: mientras la primera baldosa está sola (y grande), su fila se centra en el bloque ENTERO
              //   (con 3 filas, no solo entre las dos primeras); sin la prop, media fila + hueco, como siempre
              const k0 = rows[0] === 1 ? Math.min(2.4, Number(props.solo_size) / tile) : 0, SOLO = k0 > 1.01;
              const rEnd = SOLO ? rowEls[rowEls.length - 1] : r1;
              let dy = R((rEnd.offsetTop + rEnd.offsetHeight - r0.offsetTop - r0.offsetHeight) / 2); // media fila + hueco
              if (A.tee && r0.offsetWidth > A.wLow + 1) dy = Math.min(dy, A.yLow - (wrap.offsetTop + r0.offsetTop + r0.offsetHeight)); // lo ancho, sobre y=1000
              dy = Math.max(0, dy);
              const i1 = cells.findIndex((x) => +x.c.dataset.row === 1);
              if (dy > 0 && i1 > 0) {
                tl.set(r0, { y: dy }, T(Math.max(0.001, times[0] - f(1))));
                const a = Math.max(times[i1 - 1] + f(2), times[i1] - f(8));   // acaba cuando nace la segunda fila
                ft(tl, r0, { y: dy }, { y: 0, duration: Math.max(f(3), times[i1] - a), ease: E.move }, a);
                // `solo_size` (px): con la PRIMERA fila de una sola
                //   baldosa, mientras está sola mide eso y baja a su tamaño con ESTE movimiento (la celda escala desde el
                //   centro de la baldosa; el rótulo, contraescalado desde su borde de arriba, sigue a su cuerpo y pegado al
                //   borde de la baldosa). Sin la prop, igual
                if (SOLO && i1 === 1) {
                  const c0 = cells[0], d0 = Math.max(f(3), times[i1] - a), tA = T(Math.max(0.001, times[0] - f(1)));
                  gsap.set(c0.c, { transformOrigin: `50% ${R(tile / 2)}px` });
                  tl.set(c0.c, { scale: k0 }, tA);
                  ft(tl, c0.c, { scale: k0 }, { scale: 1, duration: d0, ease: E.move }, a);
                  if (c0.lab) {
                    gsap.set(c0.lab, { transformOrigin: "50% 0%" });
                    tl.set(c0.lab, { scale: 1 / k0 }, tA);
                    ft(tl, c0.lab, { scale: 1 / k0 }, { scale: 1, duration: d0, ease: E.move }, a);
                  }
                }
              }
            }
          }
          // ── circuito: geometría medida (baldosas en su sitio final; con `connect` las filas no se reacomodan)
          const AR = A.node.getBoundingClientRect();
          const geo = (i) => {
            const x = cells[i];
            if (inRow) {   // coordenadas de la fila (offsets: sin transformaciones)
              const cl = x.c.offsetLeft, ct = x.c.offsetTop, tl0 = cl + x.t.offsetLeft, tt = ct + x.t.offsetTop;
              return { cx: tl0 + x.t.offsetWidth / 2, cy: tt + x.t.offsetHeight / 2, tr: tl0 + x.t.offsetWidth, cr: cl + x.c.offsetWidth,
                top: tt, bot: ct + x.c.offsetHeight };
            }
            const r = x.t.getBoundingClientRect(), c = x.c.getBoundingClientRect();
            return { cx: r.left - AR.left + r.width / 2, cy: r.top - AR.top + r.height / 2, tr: r.right - AR.left, cr: c.right - AR.left,
              top: r.top - AR.top, bot: c.bottom - AR.top };
          };
          const geoA = (i) => { const r = cells[i].t.getBoundingClientRect(); return { cx: r.left - AR.left + r.width / 2, cy: r.top - AR.top + r.height / 2 }; };
          const extra = [];
          let chain = null;
          if (wires) {
            const lw = Math.max(5, R(tile * 0.03)), lo = lw + 7;
            // rótulos en las mismas coordenadas que el circuito: el canal pasa a ≥ 24 px de cualquier rótulo
            const labBox = (i) => {
              const l = cells[i].lab; if (!l) return null;
              if (inRow) { const c = cells[i].c; return { l: c.offsetLeft + l.offsetLeft, r: c.offsetLeft + l.offsetLeft + l.offsetWidth, t: c.offsetTop + l.offsetTop, b: c.offsetTop + l.offsetTop + l.offsetHeight }; }
              const q = l.getBoundingClientRect(); return { l: q.left - AR.left, r: q.right - AR.left, t: q.top - AR.top, b: q.bottom - AR.top };
            };
            const route = (ia, ib) => {
              const a = geo(ia), b = geo(ib);
              if (Math.abs(a.cy - b.cy) < 2) return [[a.cx, a.cy], [b.cx, b.cy]];   // misma fila: por el hueco entre baldosas
              // `connect_route: "straight"` (
              // en la columna 1 + 1 el codo salía por la derecha y moría en el aire): baldosas en columna (mismo centro x) →
              // trazo RECTO vertical de debajo del rótulo de la de arriba al centro de la de abajo (bajo la baldosa: se ve
              // hasta su borde). Sin la opción, el codo de siempre.
              if (props.connect_route === "straight" && Math.abs(a.cx - b.cx) < 4) {
                const up = b.cy < a.cy, la = labBox(ia);
                const ya = up ? a.top - R(tile * 0.06) : (la ? la.b : a.bot) + R(tile * 0.06);
                return [[a.cx, ya], [b.cx, b.cy]];
              }
              // cambio de fila: sale por la derecha, baja por fuera de los rótulos y cruza por el canal entre filas
              const up = b.cy < a.cy, rowA = +cells[ia].c.dataset.row;
              const labsA = cells.map((_, i) => i).filter((i) => +cells[i].c.dataset.row === rowA).map(labBox).filter(Boolean);
              const la = labBox(ia);
              let xr = Math.max(a.cr, a.tr + 24, la ? la.r + 24 : 0);
              const labBot = Math.max(a.bot, ...labsA.map((q) => q.b)), labTop = Math.min(a.top, ...labsA.map((q) => q.t));
              let yg = up ? (b.bot + labTop) / 2 : (labBot + b.top) / 2;
              if (!up) yg = Math.max(yg, Math.min(labBot + 24, b.top - lw)); else yg = Math.min(yg, Math.max(labTop - 24, b.bot + lw));
              return [[a.cx, a.cy], [xr, a.cy], [xr, yg], [b.cx, yg], [b.cx, b.cy]];
            };
            const tOf = (i) => times[i];
            const segs = pairs.map(([ia, ib]) => {
              const pts = route(ia, ib), w = gx.wire(wires, pts, { w: lw, wo: lo });
              const late = tOf(ib) >= tOf(ia) ? ib : ia;              // el tramo se dibuja cuando entra la última de sus dos
              const tD = tOf(late) + f(4);
              gx.drawWire(tl, w, tD, f(9));
              gx.ev(ctx, "connect", tD);
              extra.push(w.ol, w.gd);
              const bt = cells[late].t;   // la baldosa que recibe el trazo late
              ft(tl, bt, { scale: 1 }, { scale: 1.06, duration: f(3), ease: E.enter }, tD + f(8));
              ft(tl, bt, { scale: 1.06 }, { scale: 1, duration: f(6), ease: E.pop }, tD + f(11));
              return { pts, tD, ia, ib, w };
            });
            // el circuito como cadenas continuas (pares que se encadenan: el final de uno es el principio del siguiente)
            const chains = [];
            segs.forEach((g) => {
              const c = chains.find((q) => q.end === g.ia);
              if (c) { c.pts.push(...g.pts.slice(1)); c.end = g.ib; c.t = Math.max(c.t, g.tD); }
              else chains.push({ pts: g.pts.slice(), end: g.ib, t: g.tD });
            });
            chain = chains[0] ? chains[0].pts : null;
            // pulso que recorre el circuito mientras el plano siga (nada quieto)
            const tEnd0 = mg ? gx.cue(cues, "merge", t1) - f(4) : t1 - 0.3;
            // cue `cross`: el tramo `cross_pair` (índice del par; 0) se
            //   ROMPE en esa palabra: el pulso deja de correr 2 f antes, el trazo baja al 22 % y un disco con «×» cae en su
            //   punto medio (la unión era falsa: «cualquier proceso → buena oferta»). Sin la cue, nada cambia. Evento `off`
            const tXc = gx.cue(cues, "cross", null);
            const tEnd = tXc != null && !mg ? Math.min(tEnd0, tXc - f(2)) : tEnd0;
            chains.forEach((c, k) => {
              const L = gx.polyLen(c.pts), dP = Math.max(0.6, Math.min(1.6, L / 800));
              const dot = gx.pulseDot(inRow || A.node, R(Math.max(22, tile * 0.11)));
              extra.push(dot);
              for (let tb = c.t + f(10) + k * 0.2; tb + dP < tEnd; tb += dP + 0.55) gx.pulse(tl, dot, c.pts, tb, dP);
            });
            if (tXc != null && !mg && segs.length) {
              const sg = segs[Math.max(0, Math.min(segs.length - 1, props.cross_pair | 0))];
              const at = Math.max(sg.tD + f(9), Math.round(tXc * gx.FPS) / gx.FPS);
              if (at < t1 - f(4)) {
                // punto medio del recorrido (por longitud)
                const P = sg.pts, Lh = gx.polyLen(P) / 2;
                let acc = 0, mp = P[0];
                for (let i = 1; i < P.length; i++) {
                  const d = Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]);
                  if (acc + d >= Lh) { const u = d ? (Lh - acc) / d : 0; mp = [P[i - 1][0] + (P[i][0] - P[i - 1][0]) * u, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * u]; break; }
                  acc += d;
                }
                const cs = R(Math.max(72, tile * 0.36));
                const xd = gx.el("div", "lr-cross" + (props.cross_tone === "ink" ? " lr-cross-ink" : ""), inRow || A.node);
                Object.assign(xd.style, { left: R(mp[0] - cs / 2) + "px", top: R(mp[1] - cs / 2) + "px", width: cs + "px", height: cs + "px" });
                const xs = gx.svg("svg", { viewBox: "0 0 48 48", class: "lr-cross-g" }, xd);
                xs.innerHTML = '<path d="M15 15 L33 33 M33 15 L15 33"/>';
                gsap.set(xd, { opacity: 0, transformOrigin: "50% 50%" });
                ft(tl, [sg.w.ol, sg.w.gd], { opacity: 1 }, { opacity: 0.22, duration: f(5), ease: E.exit }, at);
                ft(tl, xd, { opacity: 0, scale: 1.6, rotation: -24 }, { opacity: 1, scale: 1, rotation: 0, duration: f(6), ease: E.enter }, at);
                ft(tl, xd, { scale: 1 }, { scale: 1.08, duration: f(3), ease: E.enter }, at + f(6));
                ft(tl, xd, { scale: 1.08 }, { scale: 1, duration: f(6), ease: E.move }, at + f(9));
                gx.ev(ctx, "off", at);
                extra.push(xd);
              }
            }
          }
          // ── fusión: las baldosas vuelan al centro del bloque y se convierten en un icono final
          if (mg) {
            const tM = Math.max(Math.max(...times) + f(10), gx.cue(cues, "merge", t1 - 0.9));
            const G = cells.map((_, i) => geoA(i));
            const mx = G.reduce((a, g) => a + g.cx, 0) / G.length, my = G.reduce((a, g) => a + g.cy, 0) / G.length;
            const ms = R(tile * 1.2);
            Object.assign(mBox.style, { left: R(mx - ms / 2) + "px", top: R(my - ms / 2) + "px", width: ms + "px", height: ms + "px", position: "absolute" });
            if (mLab) { Object.assign(mLab.m.style, { left: "0px", width: A.w + "px", top: R(my + ms / 2 + 26) + "px" }); gx.fit(mLab.i, { max: props.compact ? 56 : 64, min: 48, width: A.w, lines: 1 }); }
            if (extra.length) tl.to(extra, { opacity: 0, duration: f(5), ease: E.exit }, tM);
            cells.forEach((x, i) => {
              const at = tM + i * f(1);
              if (x.lab) tl.to(x.lab, { opacity: 0, y: -R(10), duration: f(4), ease: E.exit }, at);
              ft(tl, x.t, { x: 0, y: 0, scale: 1 }, { x: R(mx - G[i].cx), y: R(my - G[i].cy), scale: 0.55, duration: f(10), ease: E.move }, at);
              gx.streak(tl, x.t, at + f(2), f(7), Math.abs(mx - G[i].cx) > Math.abs(my - G[i].cy) ? "x" : "y", 10);
              tl.to(x.t, { opacity: 0, duration: f(3), ease: E.exit }, at + f(8));
            });
            const tA = tM + (cells.length - 1) * f(1) + f(9);
            ft(tl, mBox, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: f(9), ease: E.pop }, tA);
            if (mLab) ft(tl, mLab.i, { opacity: 0, yPercent: 105 }, { opacity: 1, yPercent: 0, duration: f(8), ease: E.enter }, tA + f(4));
            gx.ev(ctx, "merge", tA);
            for (let tb = tA + 1.0; tb < t1 - 0.5; tb += 1.3) {   // el icono final respira
              ft(tl, mBox, { scale: 1 }, { scale: 1.05, duration: f(6), ease: E.enter }, tb);
              ft(tl, mBox, { scale: 1.05 }, { scale: 1, duration: f(9), ease: E.move }, tb + f(6));
            }
          }
          // `cross_item` + cue `cross` SIN circuito: el disco con «×» cae
          //   sobre esa baldosa (abajo a la derecha, por encima de ella) y la baldosa y su rótulo bajan al 38 % («no elijas
          //   el que más molesta»). Sin la prop, nada cambia. Evento `off`
          // `crosses: [{item, cue}]`: el mismo gesto en varias baldosas de la
          //   misma fila, cada una en su palabra («ni una nueva versión ni un nuevo modelo»: la lista acaba junta). Opcional:
          //   sin la prop, `cross_item` + cue `cross` siguen igual
          const xList = Array.isArray(props.crosses) && props.crosses.length
            ? props.crosses.map((c) => [c.item, gx.cue(cues, c.cue, null)])
            : [[props.cross_item, gx.cue(cues, "cross", null)]];
          xList.forEach(([xi, tXi]) => {
          if (tXi != null && !pairs.length && Number.isInteger(xi) && xi >= 0 && xi < cells.length) {
            const x = cells[xi], at = Math.max(times[xi] + f(8), Math.round(tXi * gx.FPS) / gx.FPS);
            if (at < t1 - f(4)) {
              const cs = R(Math.max(72, tile * 0.42));
              const xd = gx.el("div", "lr-cross" + (props.cross_tone === "ink" ? " lr-cross-ink" : ""), x.c);
              Object.assign(xd.style, { left: R(x.t.offsetLeft + x.t.offsetWidth * 0.8 - cs / 2) + "px", top: R(x.t.offsetTop + x.t.offsetHeight * 0.8 - cs / 2) + "px", width: cs + "px", height: cs + "px", zIndex: "3" });
              const xs = gx.svg("svg", { viewBox: "0 0 48 48", class: "lr-cross-g" }, xd);
              xs.innerHTML = '<path d="M15 15 L33 33 M33 15 L15 33"/>';
              gsap.set(xd, { opacity: 0, transformOrigin: "50% 50%" });
              ft(tl, [x.t].concat(x.lab ? [x.lab] : []), { opacity: 1 }, { opacity: 0.38, duration: f(6), ease: E.exit }, at);
              ft(tl, xd, { opacity: 0, scale: 1.6, rotation: -24 }, { opacity: 1, scale: 1, rotation: 0, duration: f(6), ease: E.enter }, at);
              ft(tl, xd, { scale: 1 }, { scale: 1.08, duration: f(3), ease: E.enter }, at + f(6));
              ft(tl, xd, { scale: 1.08 }, { scale: 1, duration: f(6), ease: E.move }, at + f(9));
              gx.ev(ctx, "off", at);
            }
          }
          });
          // cue `dim`: `dim_items` bajan al 38 % (baldosa y rótulo) y siguen leyéndose; el foco pasa a otras
          const tDim = gx.cue(cues, "dim", null), dimIdx = Array.isArray(props.dim_items) ? props.dim_items : null;
          if (tDim != null && dimIdx && dimIdx.length) {
            const at = Math.round(tDim * gx.FPS) / gx.FPS;
            const dc = cells.filter((_, i) => dimIdx.indexOf(i) >= 0 && times[i] + f(8) <= at);
            if (dc.length && at < t1 - f(4)) {
              ft(tl, dc.map((x) => x.t).concat(dc.map((x) => x.lab).filter(Boolean)), { opacity: 1 }, { opacity: 0.38, duration: f(6), ease: E.exit }, at);
              gx.ev(ctx, "off", at);
            }
          }
          // cue `hot`: las baldosas `hot` se encienden EN esa palabra (el
          //   aro de oro entra, el rótulo pasa a oro y la baldosa late) en vez de estar encendidas desde que entran. Sin la
          //   cue, nada cambia. Evento `hot` (sin sonido propio en el mapa: si lo quiere, una decisión sfx con at: "hot")
          const tHot = gx.cue(cues, "hot", null);
          if (tHot != null) {
            const at = Math.round(tHot * gx.FPS) / gx.FPS;
            const hc = cells.filter((x, i) => x.it.hot && times[i] + f(8) <= at && at < t1 - f(4));
            if (hc.length) {
              const fg = gx.cssv(A.node, "--g-fg", "#161514"), acc = gx.cssv(A.node, "--ck-accent", "#FECA1A");
              hc.forEach((x) => {
                x.c.classList.remove("lr-hot");
                const ring = gx.el("div", "lr-hotring", x.t);
                gsap.set(ring, { opacity: 0, transformOrigin: "50% 50%" });
                ft(tl, ring, { opacity: 0, scale: 1.16 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, at);
                if (x.lab) ft(tl, x.lab, { color: fg }, { color: acc, duration: f(5), ease: E.enter }, at);
              });
              gx.ev(ctx, "hot", at);
            }
          }
          // cue `pulse_all`: TODAS las baldosas presentes laten a la vez
          //   (1 → 1,08 → 1), sin destacar ninguna (opciones paralelas). Sin la cue, nada cambia. Evento `pulse`
          const tPa = gx.cue(cues, "pulse_all", null);
          if (tPa != null) {
            const at = Math.round(tPa * gx.FPS) / gx.FPS;
            const pc = cells.filter((x, i) => times[i] + f(8) <= at && at < t1 - f(10));
            if (pc.length) {
              pc.forEach((x) => {
                gsap.set(x.t, { transformOrigin: "50% 50%" });
                ft(tl, x.t, { scale: 1 }, { scale: 1.08, duration: f(4), ease: E.enter }, at);
                ft(tl, x.t, { scale: 1.08 }, { scale: 1, duration: f(8), ease: E.move }, at + f(4));
              });
              gx.ev(ctx, "pulse", at);
            }
          }
          // item `grow`: entre `from` y `to` la baldosa crece a saltos (asentamiento corto en cada uno)
          cells.forEach((x, i) => {
            const g = x.it.grow;
            if (!g || typeof g !== "object") return;
            const a = Math.max(times[i] + f(10), gx.cue(cues, g.from, times[i] + f(10))), b = Math.min(t1 - f(6), gx.cue(cues, g.to, a + 1.2));
            if (!(b > a + f(8))) return;
            const k1 = Math.max(1.02, Math.min(1.25, g.scale || 1.14)), n = Math.max(2, Math.min(6, Math.round((b - a) / 0.4)));
            gsap.set(x.t, { transformOrigin: "50% 50%" });
            for (let k = 0; k < n; k++) {
              const s0 = 1 + (k1 - 1) * k / n, s1 = 1 + (k1 - 1) * (k + 1) / n;
              ft(tl, x.t, { scale: s0 }, { scale: s1, duration: f(5), ease: E.pop }, a + k * (b - a) / n);
            }
            gx.ev(ctx, "grow", a);
          });
          // cue `off` (antes seguían encendidas mientras se decía
          // «no tanto… sino»): las baldosas encendidas se apagan (6 f) y vuelve su contorno fantasma; los rótulos
          // quedan atenuados (35 %) para que se siga leyendo qué se apaga. Evento `off` en el fotograma en que empieza
          const tOff = gx.cue(cues, "off", null);
          if (tOff != null && !mg && tOff > Math.max(...times) + f(4) && tOff < t1 - f(4)) {
            const at = Math.round(tOff * gx.FPS) / gx.FPS;
            cells.forEach((x) => {
              tl.to(x.t, { opacity: 0, scale: 0.9, duration: f(6), ease: E.exit }, at);
              ft(tl, x.slot, { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, at + f(1));
              if (x.lab) tl.to(x.lab, { opacity: 0.35, duration: f(6), ease: E.exit }, at);
            });
            if (extra.length) tl.to(extra, { opacity: 0, duration: f(5), ease: E.exit }, at);
            gx.ev(ctx, "off", at);
          }
          gx.bgIn(tl, bd, t0, t1, 51, props);
          gx.out(tl, props, t1, [wrap].concat(wires ? [wires] : [], mBox ? [mBox] : [], mLab ? [mLab.m] : []), { dur: ex, ctx });
        },
      });
    },
  });
})(window.CK);
