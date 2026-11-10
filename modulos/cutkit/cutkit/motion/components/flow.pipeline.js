// flow.pipeline v2 — «información desordenada» → Nimbo → «salida útil». SIMÉTRICO y de estudio:
//   - tres columnas iguales: fichas de PAPEL arriba (giro −3,2 / +2,6 / −1,6°) y fichas de TINTA abajo, mismos centros;
//   - el bloque del modelo (baldosa ≥160 px con sombra de una luz cenital y halo claro detrás) centrado en x=540, con la
//     MISMA distancia borde a borde arriba y abajo; etiquetas espejo en tinta («información desordenada» / «salida útil»)
//     si caben;
//   - match cut por oclusión: en `transform` cada ficha de papel se endereza y pasa POR DETRÁS del logo; por debajo
//     sale ya convertida en ficha de tinta con mono blanco (nunca un fundido con dos textos legibles).
// En el corte ya se ve el modelo grande y solo; en `messy` baja a su sitio y caen las fichas con anticipación, asentado
// y follow-through. Push lento 1,00 → 1,03 al final. Sin destinos inventados.
// props: {layout?: vertical (defecto) | columns, cards: [{eyebrow, text}] | ["…"], outputs: ["clave: valor"] | [{key, value}], labels?: {top, bottom},
//         steps?: [{label, kind: model, asset}], canvas?, exit?: "cut"}
// cues:  messy, label_top, label_top2, transform, label_bottom, output
// (push lento 1,00 → 1,02)
// `inputs: "tiles"` (mountTiles): baldosas rectas con glifo o icono del kit en c0…c2, rótulos ≥ 48 px, se funden
//   dentro del icono central en `transform` (sin huellas), el plano sube y sale la publicación como post en esqueleto.
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
  const ROT = [-3.2, 2.6, -1.6];
  // Los SFX no deben caer sobre la cara: ningún evento después del
  // final del item. `transform`/`output` que caen tras t1 no se emiten (y su fase no se anima).
  function evGuard(ctx, t1) { return (k, t) => { if (isFinite(t) && t <= t1 - f(1) + 1e-6) gx.ev(ctx, k, t); }; }
  // instante encajado AL fotograma siguiente: lo que cambia con un set en t se ve en ese fotograma (no en el anterior)
  const snapUp = (t) => Math.ceil(t * gx.FPS - 1e-6) / gx.FPS;


  // ── layout "vertical" (defecto; styleframe 07): etiqueta · 3 fichas de PAPEL apiladas y revueltas (820 px) · 36 ·
  //    logo (≥160 px, «Nimbo» debajo, halo) · 36 · 3 barras de TINTA (680 px, mono ≥36) · «salida útil». Eje x=540.
  //    En `transform` cada ficha se endereza, pasa POR DETRÁS del logo y sale por debajo como su barra (mismo orden; la
  //    barra lleva la pestaña de papel con el eyebrow de su ficha: se lee qué ficha da qué salida).
  const DX = [-22, 20, -6];
  function mountVertical(root, props, ctx) {
    const E = gx.eases(ctx);
    const st = gx.stage(root, ctx, props, "fp fpv");
    const A = st.A, bd = st.bd;
    const W = A.w, H = A.h;
    let s = Math.max(0.8, Math.min(1.1, W / 950));
    A.node.style.setProperty("--s", s);
    const steps = props.steps || [];
    const stepOf = (k) => steps.find((x) => x.kind === k) || {};
    const asCard = (c) => (typeof c === "string" ? { text: c } : c || { text: "" });
    const cardsT = (props.cards && props.cards.length ? props.cards : [stepOf("messy").label || ""]).map(asCard).filter((c) => c.text).slice(0, 3);
    const asOut = (o) => { if (o && typeof o === "object") return { key: o.key || "", value: o.value || "" }; const m = String(o).match(/^\s*([^:]{1,24}):\s*(.+)$/); return m ? { key: m[1], value: m[2] } : { key: "", value: String(o) }; };
    const outsT = (props.outputs && props.outputs.length ? props.outputs : [stepOf("structured").label || ""]).filter(Boolean).map(asOut).slice(0, 3);
    const model = stepOf("model");
    const labels = props.labels || {};
    const box = gx.el("div", "fp-box fpv-box", gx.el("div", "fp-wrap", A.node));
    Object.assign(box.style, { left: "0px", width: W + "px" });
    const lt = labels.top ? gx.el("div", "fp-label fp-label-top", box) : null;
    if (lt) gx.split(lt, labels.top, "chars");
    const lb = labels.bottom ? gx.el("div", "fp-label fp-label-bot", box, labels.bottom) : null;
    const cards = cardsT.map((c, i) => {
      const card = gx.el("div", "fp-card fpv-card", box);
      const eb = c.eyebrow ? gx.el("div", "fp-eyebrow", card, c.eyebrow) : null;
      const tx = gx.el("div", "fp-ctext", card, c.text);
      return { card, eb, tx, rot: ROT[i % ROT.length], dx: DX[i % DX.length], eyebrow: c.eyebrow || "" };
    });
    const halo = gx.el("div", "fp-halo", box);
    const grp = gx.el("div", "fp-grp fpv-grp", box);
    const tile = gx.el("div", "fp-tile", grp);
    if (model.asset) gx.logo(tile, ctx, model.asset, "fp-logo"); else gx.el("div", "fp-tile-label", tile, model.label || "");
    const mlab = model.label && model.asset ? gx.el("div", "fp-mlabel fpv-mlabel", grp, model.label) : null;
    const arrow = () => { const a = gx.el("div", "fpv-arrow", box); gx.el("i", "", a); return a; };
    const arA = arrow(), arB = arrow();
    const outs = outsT.map((o, i) => {
      const el = gx.el("div", "fp-out fpv-bar", box);
      const src = cards[i] && cards[i].eyebrow ? gx.el("div", "fpv-tab", el, cards[i].eyebrow) : null;
      const line = gx.el("div", "fpv-kv", el);
      const k = o.key ? gx.el("span", "fp-okey", line, o.key + ":") : null;
      const v = gx.el("span", "fp-oval", line, o.value);
      return { el, src, line, k, v };
    });
    gsap.set([...cards.map((c) => c.card), grp, halo, ...outs.map((o) => o.el), lb, arA, arB].filter(Boolean), { opacity: 0 });
    if (lt) gsap.set(lt.querySelectorAll(".gx-ch"), { opacity: 0 });

    return {
      animate(tl, t0, t1, cues) {
        const ex = f(5);
        const ev = evGuard(ctx, t1);
        // ── medidas: fichas 820 · baldosa ≥160 · barras 680 (≤696 por debajo de y=1000) · huecos espejo de 36
        // fichas: eyebrow en su columna a la izquierda (como la pestaña de las barras) → una línea por ficha si cabe
        const cw = R(Math.min(900 * s, W * 0.95)), bw = R(Math.min(680 * s, A.wLow - 12));
        let tileS = R(Math.max(160, 172 * s)), bh = R(78 * s), bgap = R(10 * s), ov = 0, labPx = Math.round(44 * s), txtPx = Math.round(32 * s), monoPx = Math.round(40 * s);
        const G = R(36 * s), g0 = R(14 * s);
        cards.forEach((c) => { c.card.style.width = cw + "px"; });
        outs.forEach((o) => { o.el.style.width = bw + "px"; });
        const fitAll = () => {
          if (lt) gx.fit(lt, { max: labPx, min: 38, width: W, lines: 1 });
          if (lb) gx.fit(lb, { max: labPx, min: 38, width: A.wLow, lines: 1 });
          cards.forEach((c) => gx.fit(c.tx, { max: txtPx, min: 30, width: cw - 2 * 26 * s - (c.eb ? c.eb.offsetWidth + 16 * s : 0), lines: 2 }));
          Object.assign(tile.style, { width: tileS + "px", height: tileS + "px" });
          if (mlab) mlab.style.fontSize = Math.max(36, Math.round(tileS * 0.22)) + "px";
          outs.forEach((o) => {
            o.el.style.height = bh + "px";
            const room = bw - 2 * 26 * s - (o.src ? o.src.offsetWidth + 18 * s : 0);
            const kvFit = (px) => { if (o.k) o.k.style.fontSize = px + "px"; o.v.style.fontSize = px + "px"; return o.line.scrollWidth <= room + 1; };
            let px = monoPx; while (px > 36 && !kvFit(px)) px -= 1; kvFit(Math.max(36, px));
          });
        };
        fitAll();
        const rad = (d) => (d * Math.PI) / 180;
        const ext = (c) => c.card.offsetHeight * Math.cos(rad(c.rot)) + cw * Math.abs(Math.sin(rad(c.rot)));
        // paso entre fichas: la de abajo (encima en z) puede montarse sobre la de arriba, pero NUNCA sobre su texto:
        // se calcula con los giros reales en los dos extremos del texto (desorden real, todo legible)
        const pitch = (a, b) => {
          const ha = a.card.offsetHeight, hb = b.card.offsetHeight, ta = rad(a.rot), tb = rad(b.rot);
          const padB = 18 * s, dxab = (a.dx - b.dx) * s, u0 = cw / 2 - 26 * s;
          let need = -1e9;
          [-u0, u0].forEach((u) => {
            const textBottomA = u * Math.sin(ta) + (ha / 2 - padB) * Math.cos(ta);   // relativo al centro de a
            const ub = u + dxab;                                                      // mismo x, en coordenadas de b
            const topB = ub * Math.sin(tb) - (hb / 2) * Math.cos(tb);                 // relativo al centro de b
            need = Math.max(need, textBottomA - topB);
          });
          return need + 4 * s - Math.min(0, ov) * 0 + Math.max(0, ov) * -1;           // ov > 0 solo como último recurso
        };
        const stackH = () => {
          if (!cards.length) return 0;
          let h = ext(cards[0]) / 2;
          for (let i = 1; i < cards.length; i++) h += pitch(cards[i - 1], cards[i]);
          return h + ext(cards[cards.length - 1]) / 2;
        };
        const logoH = () => grp.offsetHeight;
        const barsH = () => (outs.length ? outs.length * bh + (outs.length - 1) * bgap : 0);
        const labH = (n) => (n ? n.offsetHeight + g0 : 0);
        const total = () => labH(lt) + stackH() + G + logoH() + G + barsH() + labH(lb);
        for (let k = 0; k < 24 && total() > H * 0.99; k++) {
          if (labPx > 40) labPx -= 2;
          else if (bh > 72) bh -= 2;
          else if (txtPx > 30) txtPx -= 1;
          else if (ov < 10 * s) ov += 2;
          else if (tileS > 160) tileS -= 4;
          else if (monoPx > 36) monoPx -= 1;
          else break;
          fitAll();
        }
        // colocación: centrado en la banda (el logo queda en el centro óptico del plano)
        let y = R(Math.max(0, (H - total()) / 2));
        if (lt) { lt.style.top = y + "px"; y += labH(lt); }
        let cy = y + (cards.length ? ext(cards[0]) / 2 : 0);
        cards.forEach((c, i) => {
          if (i > 0) cy += pitch(cards[i - 1], c);
          c.cy = R(cy); c.x = R((W - cw) / 2 + c.dx * s);
          Object.assign(c.card.style, { left: c.x + "px", top: R(cy - c.card.offsetHeight / 2) + "px" });
          c.ghost = c.card.cloneNode(true); c.ghost.classList.add("fpv-ghost"); box.insertBefore(c.ghost, c.card);
          gsap.set(c.ghost, { opacity: 0, rotation: c.rot, transformOrigin: "50% 50%" });
        });
        y += stackH();
        const arAy = y; y += G;
        const gw = grp.offsetWidth, grpTop = R(y), tileCy = R(y + tileS / 2), cx = R(W / 2);
        Object.assign(grp.style, { left: R(W / 2 - gw / 2) + "px", top: grpTop + "px" });
        const hs = R(Math.max(560, tileS * 3.8));
        Object.assign(halo.style, { left: R(cx - hs / 2) + "px", top: R(tileCy - hs / 2) + "px", width: hs + "px", height: hs + "px" });
        y += logoH();
        const arBy = y; y += G;
        const barsTop = R(y);
        outs.forEach((o, i) => { o.top = R(barsTop + i * (bh + bgap)); Object.assign(o.el.style, { left: R((W - bw) / 2) + "px", top: o.top + "px" }); });
        y += barsH();
        // rótulo inferior: caja ≤696 px centrada (por debajo de y=1000 la zona segura es más estrecha)
        if (lb) Object.assign(lb.style, { top: R(y + g0) + "px", left: R((W - A.wLow) / 2) + "px", right: "auto", width: A.wLow + "px" });
        const ah = R(Math.min(26 * s, G * 0.72));
        [[arA, arAy], [arB, arBy]].forEach(([a, ay]) => Object.assign(a.style, { left: R(cx - 8) + "px", top: R(ay + (G - ah) / 2) + "px", height: ah + "px" }));

        const c = (k, d) => gx.cue(cues, k, d);
        const tS = gx.settle(ctx, t0);
        const tM = Math.max(tS + f(4), c("messy", c("s0", t0 + 0.4)));
        const tL1 = Math.max(tS + f(2), c("label_top", tM + f(6)));
        const tL2 = c("label_top2", null);
        const tT = Math.max(tM + f(16), c("transform", tM + 1.0));
        const tLB = c("label_bottom", null);
        // 1 · en el corte: el modelo grande y solo en el centro de la banda (su halo, la luz del plano)
        const gh = grp.offsetHeight;
        const heroK = Math.min(1.7, (H * 0.3) / Math.max(1, gh), (W * 0.8) / Math.max(1, gw)), dyHero = R(H / 2 - (grpTop + gh / 2));
        tl.set(grp, { y: dyHero, scale: heroK, transformOrigin: "50% 50%" }, T(tS));
        tl.set(halo, { y: dyHero, scale: heroK, transformOrigin: "50% 50%", opacity: 1 }, T(tS));
        gx.cutIn(tl, grp, tS);
        ev("enter", tS); ev("logo", tS);
        ft(tl, [grp, halo], { y: dyHero, scale: heroK }, { y: 0, scale: 1, duration: f(10), ease: E.move }, tM);
        // 2 · caen las fichas desde arriba con gravedad (stagger 3 f) y se quedan revueltas
        cards.forEach((x, i) => {
          const at = tM + f(4) + i * f(3);
          ev("card_drop", at);
          const r0 = rad(x.rot * 2.4), ext0 = x.card.offsetHeight * Math.cos(r0) + cw * Math.abs(Math.sin(r0));
          const room = Math.max(24, x.cy - ext0 / 2 - 8); // girada como empieza, la ficha nunca asoma por encima de y=288
          gx.land(tl, x.card, at, { from: { y: -R(Math.min(220 * s, room)), rotation: x.rot * 2.4, opacity: 0 }, rot: x.rot, dur: f(9), swing: (i % 2 ? -1 : 1) * 1.4, streak: true, antic: false });
        });
        // 3 · «información» y «desordenada» (letras levemente desalineadas que se asientan en 8 f)
        if (lt) {
          const rnd = gx.rng(gx.hash(labels.top));
          Array.from(lt.querySelectorAll(".gx-w")).forEach((w, wi) => {
            const at = wi === 0 ? tL1 : Math.max(tL1 + f(4), tL2 != null ? tL2 : tL1 + 0.45);
            const chs = Array.from(w.querySelectorAll(".gx-ch"));
            if (wi === 0) ft(tl, chs, { opacity: 0, y: R(10 * s) }, { opacity: 1, y: 0, duration: f(6), ease: E.enter }, at);
            else chs.forEach((ch) => ft(tl, ch, { opacity: 0, y: R((rnd() - 0.5) * 16 * s), rotation: (rnd() - 0.5) * 10 },
              { opacity: 1, y: 0, rotation: 0, duration: f(8), ease: E.enter }, at + rnd() * f(2)));
          });
        }
        // 4 · transformación por oclusión: enderezar (6 f) → bajar por DETRÁS del logo (8 f, estela vertical) → la barra
        //     nace detrás de la baldosa y baja a su hueco espejo (pop + follow-through de 3 px). Una a una, stagger 4 f.
        ev("flip", tT);
        ft(tl, arA, { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: f(5), ease: E.move }, tT - f(4));
        const kHide = (tileS * 0.82) / cw;
        cards.forEach((x, i) => {
          const at = tT + i * f(4);
          // huella: la ficha deja su silueta revuelta en su sitio (la entrada sigue leyéndose junto a su salida)
          tl.set(x.ghost, { opacity: 0 }, T(tS));
          ft(tl, x.ghost, { opacity: 0 }, { opacity: 1, duration: f(5), ease: E.enter }, at + f(3));
          ft(tl, x.card, { rotation: x.rot }, { rotation: 0, duration: f(6), ease: E.move }, at);
          const dx = R(cx - (x.x + cw / 2)), dy = R(tileCy - x.cy);
          ft(tl, x.card, { x: 0, y: 0, scale: 1 }, { x: dx, y: dy, scale: kHide, duration: f(8), ease: E.move }, at + f(4));
          gx.streak(tl, x.card, at + f(5), f(7), "y", 12);
          tl.set(x.card, { opacity: 0 }, T(at + f(12)));
        });
        ft(tl, tile, { scale: 1 }, { scale: 1.06, duration: f(4), ease: E.move }, tT + f(10));
        ft(tl, tile, { scale: 1.06 }, { scale: 1, duration: f(8), ease: E.pop }, tT + f(14));
        const tB0 = tT + f(12);
        ft(tl, arB, { opacity: 0, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: f(5), ease: E.move }, tB0 - f(2));
        outs.forEach((o, i) => {
          const at = tB0 + i * f(4);
          const dy = R(tileCy - (o.top + bh / 2)), k = Math.min(0.5, (tileS * 0.82) / bw);
          tl.set(o.el, { y: dy, scale: k, opacity: 1 }, T(at)); // nace detrás de la baldosa
          ft(tl, o.el, { y: dy, scale: k }, { y: 0, scale: 1, duration: f(9), ease: E.pop }, at);
          gx.streak(tl, o.el, at, f(7), "y", 12);
          ft(tl, o.el, { y: 0 }, { y: R(3 * s), duration: f(3), ease: E.move }, at + f(9));
          ft(tl, o.el, { y: R(3 * s) }, { y: 0, duration: f(4), ease: E.move }, at + f(12));
          ev(i === outs.length - 1 ? "lock" : "option", at + f(9));
        });
        const tOutEnd = tB0 + Math.max(0, outs.length - 1) * f(4) + f(9);
        // 5 · «salida útil», espejo de la etiqueta de arriba; luego quieto (contención: se lee)
        if (lb) ft(tl, lb, { opacity: 0, y: R(10 * s) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, Math.max(tB0 + f(6), tLB != null ? tLB : tOutEnd));
        gx.bgIn(tl, bd, t0, t1, 71, props);
        gx.out(tl, props, t1, [box], { dur: ex, ctx });
      },
    };
  }

  // ── `inputs: "tiles"`: entradas como BALDOSAS con glifo
  //    (play, onda, pantalla…) o icono del kit, rectas (sin giro), cada una en su cue (c0…c2) con su rótulo ≥ 48 px; en
  //    `transform` vuelan DENTRO del icono central y desaparecen del todo (sin huellas grises), el plano sube (encuadre A →
  //    B) y sale la PUBLICACIÓN como tarjeta de post en esqueleto (avatar, dos líneas e imagen), sin píldora monoespaciada.
  //    Encuadre A: rótulo de arriba · baldosas · icono central. Encuadre B: icono central · post · rótulo de abajo.
  const GLY_DEF = ["play", "wave", "screen"];
  function mountTiles(root, props, ctx) {
    const E = gx.eases(ctx);
    gx.defs();
    const st = gx.stage(root, ctx, props, "fp fpt");
    const A = st.A, bd = st.bd, W = A.w, H = A.h;
    const steps = props.steps || [];
    const model = steps.find((x) => x.kind === "model") || {};
    const cards = (props.cards || []).slice(0, 3).map((c, i) => (typeof c === "string" ? { text: c } : Object.assign({}, c || {})))
      .map((c, i) => Object.assign(c, { glyph: c.glyph || (c.asset ? null : GLY_DEF[i % 3]) }));
    const n = Math.max(1, cards.length);
    const labels = props.labels || {};
    // `clip`: paso de transformación entre el icono central y la publicación: una tira de clip cuyos
    // segmentos (2–3) se encienden en oro y se RECORTAN (lo demás se cae) en su cue. `platform`: la tarjeta de post con el
    // marco de la red (linkedin | instagram; `platform_asset` = logo verificado en la cabecera)
    const clipOn = !!props.clip, plat = ["linkedin", "instagram"].indexOf(props.platform) >= 0 ? props.platform : null;
    const B = { lab: 60, g0: 30, tile: 196, cg: 16, cap: 60, g1: 54, hub: 184, hlab: 66, g2: 44, postW: 620, postH: plat === "instagram" ? 520 : plat ? 470 : 340, g3: 30, clipH: 96, gc: 34 };
    const hA = (labels.top ? B.lab + B.g0 : 0) + B.tile + B.cg + B.cap + B.g1 + B.hub + (model.label ? B.hlab : 0);
    const hB = B.hub + (model.label ? B.hlab : 0) + B.g2 + (clipOn ? B.clipH + B.gc : 0) + B.postH + (labels.bottom ? B.g3 + B.lab : 0);
    const s = Math.max(0.62, Math.min(1.3, (H * 0.94) / Math.max(hA, hB), W / (n * B.tile * 1.5), (A.tee ? A.wLow - 16 : W) / B.postW));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    const box = gx.el("div", "fp-box fpt-box", gx.el("div", "fp-wrap", A.node));
    Object.assign(box.style, { left: "0px", width: W + "px" });
    const cx = W / 2;
    // encuadre A (centrado en la banda)
    const yA = R((H - S(hA)) / 2);
    const lt = labels.top ? gx.el("div", "fpt-lab-m", box) : null;
    const ltI = lt ? gx.el("div", "fp-label fpt-lab", lt, labels.top) : null;
    if (lt) Object.assign(lt.style, { top: yA + "px", height: S(B.lab) + 8 + "px" });
    const yT = yA + (labels.top ? S(B.lab + B.g0) : 0);
    const tw = S(B.tile), colW = Math.min(R(W / n), R(tw * 1.5));
    const xs = cards.map((_, i) => R(cx + (i - (n - 1) / 2) * colW));
    const ins = cards.map((c, i) => {
      const t = gx.el("div", "fpt-tile", box);
      Object.assign(t.style, { left: R(xs[i] - tw / 2) + "px", top: yT + "px", width: tw + "px", height: tw + "px" });
      gx.icon(t, ctx, { asset: c.asset, glyph: c.glyph, tone: c.tone || (c.asset ? "color" : "ink") }, "fpt-ic");
      const capM = gx.el("div", "fpt-cap-m", box);
      Object.assign(capM.style, { left: R(xs[i] - colW / 2) + "px", width: colW + "px", top: (yT + tw + S(B.cg)) + "px", height: S(B.cap) + 8 + "px" });
      const cap = gx.el("div", "fp-label fpt-cap", capM, c.text || "");
      return { t, capM, cap, x: xs[i], y: yT + tw / 2 };
    });
    const yH = yT + tw + S(B.cg + B.cap + B.g1), hs = S(B.hub), hubCy = yH + hs / 2;
    const hub = gx.el("div", "fpt-hub", box);
    Object.assign(hub.style, { left: R(cx - hs / 2) + "px", top: yH + "px", width: hs + "px", height: hs + "px" });
    if (model.asset) gx.icon(hub, ctx, { asset: model.asset, tone: model.tone || "gold" }, "fpt-hub-ic");
    else gx.icon(hub, ctx, { glyph: model.glyph || "gear", tone: "gold" }, "fpt-hub-ic");
    const hring = gx.el("div", "fpt-hub-ring", hub);
    const hlM = model.label ? gx.el("div", "fpt-lab-m", box) : null;
    const hl = hlM ? gx.el("div", "fp-label fpt-hlab", hlM, model.label) : null;
    if (hlM) Object.assign(hlM.style, { top: (yH + hs + S(10)) + "px", height: S(B.hlab) + "px" });
    // encuadre B: el icono central arriba; debajo el post y el rótulo de abajo
    const yHB = R((H - S(hB)) / 2), dy = yHB - yH;
    const yC = yH + hs + (model.label ? S(B.hlab) : 0) + S(B.g2);
    const yP = yC + (clipOn ? S(B.clipH + B.gc) : 0);
    const pw = Math.min(S(B.postW), A.tee ? A.wLow - 16 : W), ph = S(B.postH);
    // tira de clip: 8 fotogramas; los de `clip.keep` (por defecto [1, 2], [4], [6]: tres segmentos) se encienden y se quedan
    let strip = null, frames = [], keep = [];
    if (clipOn) {
      const nF = 8, cw2 = Math.min(pw, S(560)), fw = R((cw2 - S(16) * 2) / nF), fh = S(B.clipH) - S(26);
      strip = gx.el("div", "fpt-strip", box);
      Object.assign(strip.style, { left: R(cx - cw2 / 2) + "px", top: yC + "px", width: cw2 + "px", height: S(B.clipH) + "px" });
      const segs = Array.isArray(props.clip && props.clip.keep) ? props.clip.keep : [[1, 2], [4], [6]];
      keep = segs.flat().map((k) => k | 0).filter((k) => k >= 0 && k < nF);
      frames = Array.from({ length: nF }, (_, k) => {
        const fr = gx.el("i", "fpt-frame", strip);
        Object.assign(fr.style, { left: (S(16) + k * fw + 3) + "px", top: S(13) + "px", width: (fw - 6) + "px", height: fh + "px" });
        return { el: fr, k, keep: keep.indexOf(k) >= 0, x: S(16) + k * fw };
      });
      // recorte: los segmentos que se quedan se juntan en el centro de la tira
      const kept = frames.filter((q) => q.keep), x0k = R(cw2 / 2 - (kept.length * fw) / 2);
      kept.forEach((q, j) => { q.dx = R(x0k + j * fw - q.x); });
    }
    const post = gx.el("div", "fpt-post" + (plat ? " fpt-post-" + plat : ""), box);
    Object.assign(post.style, { left: R(cx - pw / 2) + "px", top: yP + "px", width: pw + "px", height: ph + "px" });
    const head = gx.el("div", "fpt-ph", post), av = gx.el("div", "fpt-av", head), lines = gx.el("div", "fpt-ls", head);
    const l1 = gx.el("i", "fpt-l1", lines), l2 = gx.el("i", plat === "instagram" ? "fpt-l2 fpt-hide" : "fpt-l2", lines);
    const plogo = plat && props.platform_asset ? gx.logo(head, ctx, props.platform_asset, "fpt-plogo") : null;
    const txl = plat === "linkedin" ? [gx.el("i", "fpt-tx", post), gx.el("i", "fpt-tx fpt-tx2", post)] : [];
    const img = gx.el("div", "fpt-img", post);
    const imgG = gx.el("div", "fpt-img-g", img);
    imgG.innerHTML = '<svg viewBox="0 0 120 70" preserveAspectRatio="xMidYMid meet"><circle cx="88" cy="20" r="9"/><path d="M8 66 L42 30 L64 52 L78 40 L112 66 Z"/></svg>';
    // fila de acciones de la red (glifos neutros de línea, sin marcas)
    const acts = plat ? (() => {
      const row = gx.el("div", "fpt-acts", post);
      return (plat === "instagram" ? ["heart", "chat", "send"] : ["thumb", "chat", "repost", "send"]).map((g) => gx.icon(row, ctx, { glyph: g, tone: "ink" }, "fpt-act"));
    })() : [];
    const lbM = labels.bottom ? gx.el("div", "fpt-lab-m", box) : null;
    const lb = lbM ? gx.el("div", "fp-label fpt-lab", lbM, labels.bottom) : null;
    if (lbM) Object.assign(lbM.style, { top: (yP + ph + S(B.g3)) + "px", height: S(B.lab) + 8 + "px" });
    gsap.set([hub, post].concat(ins.map((x) => x.t)), { opacity: 0 });
    gsap.set([ltI, hl, lb].concat(ins.map((x) => x.cap)).filter(Boolean), { opacity: 0 });
    gsap.set([av, l1, l2, img].concat(txl, acts, plogo ? [plogo] : []), { opacity: 0 });
    if (strip) gsap.set([strip].concat(frames.map((q) => q.el)), { opacity: 0 });
    gsap.set(hring, { opacity: 0 });

    return {
      animate(tl, t0, t1, cues) {
        const ex = f(5);
        const ev = evGuard(ctx, t1);
        const fitL = (el, w) => el && gx.fit(el, { max: Math.max(48, S(56)), min: 48, width: w, lines: 1 });
        fitL(ltI, W); fitL(lb, A.tee ? A.wLow : W); fitL(hl, W);
        const capPx = Math.min(...ins.map((x) => gx.fit(x.cap, { max: Math.max(48, S(54)), min: 48, width: colW - 8, lines: 1 })));
        ins.forEach((x) => { x.cap.style.fontSize = capPx + "px"; });
        const C = (k, d) => gx.cue(cues, k, d);
        const rise = (el, at, d) => ft(tl, el, { opacity: 0, yPercent: 100 }, { opacity: 1, yPercent: 0, duration: d || f(8), ease: E.enter }, at);
        const tS = gx.settle(ctx, t0);
        ev("enter", tS);
        // 1 · en el corte: el icono central (nunca un panel vacío); su rótulo sube
        gsap.set(hub, { opacity: 1, scale: 0.9 });     // ya está en el fotograma 0 (es imagen, no texto) y se asienta
        tl.set(hub, { opacity: 1 }, gx.T(tS));
        ft(tl, hub, { scale: 0.9 }, { scale: 1, duration: f(8), ease: E.pop }, tS);
        if (hl) rise(hl, tS + f(3));
        // 2 · las entradas, cada una en su cue (c0…c2; si no, desde `messy` en cascada)
        const tM = Math.max(tS + f(3), C("messy", tS + 0.35));
        const tin = ins.map((_, i) => Math.max(tS + f(3) + i * f(3), C("c" + i, tM + i * f(5))));
        ins.forEach((x, i) => {
          gx.land(tl, x.t, tin[i], { from: { y: -S(40), opacity: 0, scale: 0.9 }, rot: 0, swing: 0, dur: f(9), antic: false });
          rise(x.cap, tin[i] + f(3), f(7));
          ev("card_drop", tin[i]);
        });
        if (ltI) rise(ltI, Math.max(tS + f(2), C("label_top", tM + f(6))));
        // 3 · convertir: cada baldosa vuela DENTRO del icono central y se apaga del todo (sin huellas); el icono late
        const tT = Math.max(Math.max(...tin) + f(10), C("transform", Math.max(...tin) + 0.8));
        // si la conversión cae después del final del item (`transform` en W222 y
        // el item acaba en W218), no se anima ni se emite nada de ella ni de la publicación
        if (tT < t1 - f(8)) {
        ev("flip", tT);
        let tHit = tT;
        ins.forEach((x, i) => {
          const at = tT + i * f(4);
          tl.to(x.cap, { opacity: 0, yPercent: -40, duration: f(4), ease: E.exit }, at);
          ft(tl, x.t, { x: 0, y: 0, scale: 1 }, { x: R(cx - x.x), y: R(hubCy - x.y), scale: 0.32, duration: f(9), ease: E.move }, at);
          gx.streak(tl, x.t, at + f(2), f(6), Math.abs(cx - x.x) > Math.abs(hubCy - x.y) ? "x" : "y", 10);
          tl.to(x.t, { opacity: 0, duration: f(3), ease: E.exit }, at + f(6));
          const hit = at + f(9);
          ft(tl, hub, { scale: 1 }, { scale: 1.08, duration: f(3), ease: E.enter }, hit);
          ft(tl, hub, { scale: 1.08 }, { scale: 1, duration: f(6), ease: E.pop }, hit + f(3));
          tHit = hit;
        });
        if (ltI) tl.to(ltI, { opacity: 0, yPercent: -40, duration: f(5), ease: E.exit }, tT);
        ft(tl, hring, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, tHit);
        ev("merge", tHit);
        // 4 · el plano sube (encuadre B) y la publicación nace detrás del icono y baja a su sitio
        const tCam = tT + f(6);
        ft(tl, box, { y: 0 }, { y: dy, duration: f(14), ease: E.move }, tCam);
        // 4b · la tira de clip (si la hay): sale del icono, sus segmentos se encienden en oro y se recortan (`clip`)
        let tClipEnd = tHit;
        if (strip) {
          const tC0 = tCam + f(10);
          gsap.set(strip, { transformOrigin: "50% 0%" });
          ft(tl, strip, { opacity: 0, scaleY: 0.4, y: -S(20) }, { opacity: 1, scaleY: 1, y: 0, duration: f(8), ease: E.enter }, tC0);
          frames.forEach((q, k) => ft(tl, q.el, { opacity: 0 }, { opacity: 1, duration: f(3), ease: E.enter }, tC0 + f(3) + k * f(1)));
          const tCl = Math.max(tC0 + f(14), C("clip", tC0 + 0.5));
          frames.filter((q) => q.keep).forEach((q, j) => {
            ft(tl, q.el, { backgroundColor: getComputedStyle(q.el).backgroundColor }, { backgroundColor: "rgba(254,202,26,1)", duration: f(5), ease: E.enter }, tCl + j * f(4));
            ft(tl, q.el, { scale: 1 }, { scale: 1.12, duration: f(3), ease: E.enter }, tCl + j * f(4));
            ft(tl, q.el, { scale: 1.12 }, { scale: 1, duration: f(6), ease: E.pop }, tCl + j * f(4) + f(3));
          });
          ev("clip", tCl);
          const tTrim = Math.max(tCl + keep.length * f(4) + f(8), C("trim", tCl + 0.6));
          frames.forEach((q) => {
            if (q.keep) ft(tl, q.el, { x: 0 }, { x: q.dx, duration: f(10), ease: E.move }, tTrim + f(3));
            else { gsap.set(q.el, { transformOrigin: "50% 50%" }); ft(tl, q.el, { opacity: 1, scaleY: 1 }, { opacity: 0, scaleY: 0.2, duration: f(6), ease: E.exit }, tTrim); }
          });
          ev("trim", tTrim);
          tClipEnd = tTrim + f(13);
        }
        const tO = Math.max(tHit + f(3), tCam + f(8), tClipEnd, C("output", tHit + f(4)));
        const dyP = R(hubCy - (yP + ph / 2));
        ft(tl, post, { opacity: 0, y: dyP, scale: 0.3 }, { opacity: 1, y: 0, scale: 1, duration: f(11), ease: E.pop }, tO);
        gx.streak(tl, post, tO, f(7), "y", 12);
        ft(tl, av, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(6), ease: E.pop }, tO + f(6));
        [l1, l2].forEach((l, k) => ft(tl, l, { opacity: 1, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: f(8), ease: E.enter }, tO + f(8) + k * f(3)));
        ft(tl, img, { opacity: 0, scaleY: 0.6 }, { opacity: 1, scaleY: 1, duration: f(8), ease: E.enter }, tO + f(9));
        txl.forEach((l, k) => ft(tl, l, { opacity: 1, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: f(8), ease: E.enter }, tO + f(7) + k * f(3)));
        if (plogo) ft(tl, plogo, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: f(7), ease: E.pop }, tO + f(7));
        acts.forEach((a, k) => ft(tl, a, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: f(6), ease: E.pop }, tO + f(12) + k * f(2)));
        ev("lock", tO + f(9));
        if (lb) rise(lb, Math.max(tO + f(8), C("label_bottom", tO + f(10))));
        // nada quieto: el icono central respira mientras se lee
        for (let tb = tO + 1.1; tb < t1 - 0.5; tb += 1.3) {
          ft(tl, hub, { scale: 1 }, { scale: 1.04, duration: f(6), ease: E.enter }, tb);
          ft(tl, hub, { scale: 1.04 }, { scale: 1, duration: f(9), ease: E.move }, tb + f(6));
        }
        }   // fin de la conversión (solo si cabe antes de t1)
        gx.bgIn(tl, bd, t0, t1, 71, props);
        gx.out(tl, props, t1, [box], { dur: ex, ctx });
      },
    };
  }

  // ── `agent` («Agentes» flotaba sin agente, baldosas de 200 px sin
  //    conectores, el grupo se torcía mientras faltaba MCP y la fusión nunca se veía). Diagrama AGENTE → vías → APP:
  //    - arriba la insignia del agente (el MISMO glifo de robot que viz.layers_control; `count` 1–3 insignias solapadas =
  //      «los distintos agentes») con su rótulo debajo, en la cue `agent`;
  //    - en medio, las ranuras de las vías (260 px, simétricas, reservadas en fantasma desde el corte, nunca giradas);
  //    - abajo la baldosa de la app (≥ 320 px, centrada, desde el corte).
  //    `link`: el conector agente → app se dibuja (pasa por la ranura central); `pulse`: un pulso oro lo recorre;
  //    `lanes`: los carriles fantasma de las vías laterales; c0…c2: cada vía ENCAJA en su ranura sobre la línea y su
  //    carril se enciende en oro; `transform`: un pulso por cada carril a la vez y la app se enciende (merge).
  //    Eventos en el fotograma del impacto: enter, agent, link (la línea toca la app), pulse (el pulso llega a la app),
  //    card_drop (cada vía), merge, exit. Nada se anima ni se emite después de t1.
  //    En pantalla completa el conjunto va entre y=420 y y=1248 (lejos de la UI de arriba y del raíl de subtítulos).
  const AGENT_GLYPH = '<rect x="10" y="17" width="28" height="22" rx="7"/><path d="M24 17 V10"/><circle class="f" cx="24" cy="8" r="3"/>' +
    '<circle class="f" cx="19" cy="28" r="2.8"/><circle class="f" cx="29" cy="28" r="2.8"/><path d="M6 25 V31 M42 25 V31"/>';   // = AGENT de viz.layers_control
  let fpaN = 0;
  function mountAgent(root, props, ctx) {
    const E = gx.eases(ctx);
    gx.defs();
    const st = gx.stage(root, ctx, props, "fp fpa", { bottom: 1250 });
    const A = st.A, bd = st.bd, W = A.w;
    const ag = props.agent || {};
    const nAg = Math.max(1, Math.min(3, (ag.count | 0) || 1));
    const agLabel = ag.label != null ? ag.label : (props.labels && props.labels.top) || "";
    const model = (props.steps || []).find((x) => x.kind === "model") || {};
    const cards = (props.cards || []).slice(0, 3).map((c) => (typeof c === "string" ? { text: c } : Object.assign({}, c || {})))
      .map((c, i) => Object.assign(c, { glyph: c.glyph || (c.asset ? null : GLY_DEF[i % 3]) }));
    const n = cards.length;
    // banda: en pantalla completa desde y=360 hasta el final del área (1248); en un panel, el área entera
    // (el agente, sujeto de la frase, era lo más pequeño: insignia de 92 px frente a la app de
    // 320): insignia de 176 px y huecos de 36 → 884 px, que caben en 360–1248 a s≈1
    const top0 = A.full ? Math.max(0, 360 - A.y) : 0;
    const bandH = A.h - top0;
    const B = { badge: 176, g0: 4, lab: 52, g1: 36, via: 260, g2: 36, app: 320, gap: 40 };
    const hTot = B.badge + B.g0 + B.lab + B.g1 + (n ? B.via + B.g2 : 0) + B.app;
    const s = Math.max(0.5, Math.min(1, bandH / hTot, (W * 0.96) / Math.max(1, n * B.via + Math.max(0, n - 1) * B.gap)));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    const box = gx.el("div", "fp-box fpa-box", gx.el("div", "fp-wrap", A.node));
    Object.assign(box.style, { left: "0px", width: W + "px" });
    const cx = R(W / 2), bs = S(B.badge), labH = S(B.lab), vs = S(B.via), ap = S(B.app);
    const H0 = bs + S(B.g0) + labH + S(B.g1) + (n ? vs + S(B.g2) : 0) + ap;
    const yBadge = top0 + R(Math.max(0, (bandH - H0) / 2));
    const yLab = yBadge + bs + S(B.g0);
    const yV = yLab + labH + S(B.g1);
    const yApp = n ? yV + vs + S(B.g2) : yV;
    const yLine = yLab + labH + S(10);                      // el conector nace bajo el rótulo del agente (aire bajo la «g»)
    const yb1 = R(yLab + labH + S(B.g1) / 2 + S(2)), yb2 = R(yV + vs + S(B.g2) / 2);   // los buses, en medio de su hueco
    const gapV = n > 1 ? Math.min(S(B.gap), R((W * 0.96 - n * vs) / (n - 1))) : 0;
    const xs = cards.map((_, i) => R(cx + (i - (n - 1) / 2) * (vs + gapV)));
    // conectores (debajo de todo): tronco agente → app; ramas de las vías laterales (fantasma y en oro)
    const H = R(A.h);
    const sv = gx.svg("svg", { class: "fpa-svg", width: W, height: H, viewBox: `0 0 ${W} ${H}` }, box);
    Object.assign(sv.style, { left: "0px", top: "0px" });
    const defsS = gx.svg("defs", {}, sv);
    const trunkPts = [[cx, yLine], [cx, yApp]];
    const trunk = gx.wire(sv, trunkPts, { w: S(6), wo: S(12) });
    const uid = "fpa" + (++fpaN) + "_" + gx.hash((ctx.item && ctx.item.id) || "x");
    const lanes = cards.map((c, i) => {
      const x = xs[i];
      if (Math.abs(x - cx) < 2) return { onTrunk: true, x, full: trunkPts };
      const br = [[cx, yb1], [x, yb1], [x, yb2], [cx, yb2]];
      const d = "M " + br.map((p) => R(p[0]) + " " + R(p[1])).join(" L ");
      const L = Math.max(1, gx.polyLen(br));
      const mk = gx.svg("mask", { id: uid + "_m" + i, maskUnits: "userSpaceOnUse", x: 0, y: 0, width: W, height: H }, defsS);
      const mp = gx.svg("path", { d, fill: "none", stroke: "#FFFFFF", "stroke-width": S(18), "stroke-linecap": "round", "stroke-linejoin": "round" }, mk);
      mp.style.strokeDasharray = L + " " + L; mp.style.strokeDashoffset = L;
      const gh = gx.svg("path", { d, class: "fpa-ghost-lane", mask: `url(#${uid}_m${i})`, "stroke-width": Math.max(3, S(4)),
        "stroke-dasharray": S(10) + " " + S(12) }, sv);
      const gold = gx.wire(sv, br, { w: S(6), wo: S(12) });
      return { onTrunk: false, x, br, mp, L, gh, gold, full: [[cx, yLine]].concat(br, [[cx, yApp]]) };
    });
    // ranuras de las vías (fantasma, con los carriles:, antes desde el corte = 4,5 s de cajas vacías) y las vías (baldosa clara: glifo arriba, rótulo de tinta abajo)
    const slots = xs.map((x) => { const sl = gx.el("div", "fpa-slot", box); Object.assign(sl.style, { left: R(x - vs / 2) + "px", top: yV + "px", width: vs + "px", height: vs + "px" }); return sl; });
    const icS = S(118);
    const vias = cards.map((c, i) => {
      const t = gx.el("div", "fpa-via", box);
      Object.assign(t.style, { left: R(xs[i] - vs / 2) + "px", top: yV + "px", width: vs + "px", height: vs + "px" });
      const ic = gx.icon(t, ctx, { asset: c.asset, glyph: c.glyph, tone: c.tone || (c.asset ? "color" : "ink") }, "fpa-via-ic");
      Object.assign(ic.style, { left: R((vs - icS) / 2) + "px", top: S(38) + "px", width: icS + "px", height: icS + "px" });
      const lm = gx.el("div", "fpa-via-lm", t);
      Object.assign(lm.style, { top: S(170) + "px", height: S(66) + "px" });
      const lab = gx.el("span", "fpa-via-lab", lm, c.text || "");
      return { t, lab };
    });
    // la app (centrada, desde el corte) con su aro de oro
    const app = gx.el("div", "fpa-app", box);
    Object.assign(app.style, { left: R(cx - ap / 2) + "px", top: yApp + "px", width: ap + "px", height: ap + "px" });
    if (model.asset) gx.icon(app, ctx, { asset: model.asset, tone: model.tone || "color" }, "fpa-app-ic");
    else gx.icon(app, ctx, { glyph: model.glyph || "screen", tone: "gold" }, "fpa-app-ic");
    const ring = gx.el("div", "fpa-ring", app);
    // el agente: 1–3 insignias de tinta con el robot en oro (la del centro, delante) y el rótulo debajo
    const order = Array.from({ length: nAg }, (_, k) => k).sort((a, b) => Math.abs(b - (nAg - 1) / 2) - Math.abs(a - (nAg - 1) / 2));
    const badges = order.map((k) => {
      const b = gx.el("div", "fpa-badge", box);
      Object.assign(b.style, { left: R(cx + (k - (nAg - 1) / 2) * bs * 0.66 - bs / 2) + "px", top: yBadge + "px", width: bs + "px", height: bs + "px" });
      const g = gx.svg("svg", { viewBox: "0 0 48 48", class: "fpa-badge-gl" }, b);
      g.innerHTML = ag.glyph && ag.glyph !== "robot" && gx.GLYPHS[ag.glyph] ? gx.GLYPHS[ag.glyph] : AGENT_GLYPH;
      return b;
    });
    const labM = agLabel ? gx.el("div", "fpa-lab-m", box) : null;
    const labI = labM ? gx.el("span", "fpa-lab", labM, agLabel) : null;
    if (labM) Object.assign(labM.style, { top: yLab + "px", height: (labH + S(10)) + "px" });
    // pulsos (por debajo de las vías: pasan POR DENTRO de cada herramienta)
    const dots = [0, 1, 2, 3].map(() => gx.pulseDot(box, S(24)));
    gsap.set([app].concat(vias.map((v) => v.t), slots, badges), { opacity: 0 });
    if (labI) gsap.set(labI, { opacity: 0 });
    gsap.set(ring, { opacity: 0 });
    gsap.set(app, { opacity: 1, scale: 0.92 });   // imagen, no texto: está desde el corte y se asienta

    return {
      animate(tl, t0, t1, cues) {
        const ev = evGuard(ctx, t1);
        const C = (k, d) => gx.cue(cues, k, d);
        const live = (t) => t != null && isFinite(t) && t < t1 - f(8);   // nada empieza en los últimos 8 f
        // rótulos: el del agente ≥ 48 px; los de las vías, paralelos (mismo cuerpo, una línea) ≥ 44 px
        if (labI) gx.fit(labI, { max: Math.max(48, S(50)), min: 40, width: R(W * 0.9), lines: 1 });
        if (vias.length) gx.lineParity(vias.map((v) => v.lab), { max: Math.max(48, S(52)), min: 40, width: vs - S(28), lines: 1, group: "fpa-vias" });
        const bump = (at, k) => {
          gsap.set(app, { transformOrigin: "50% 50%" });
          ft(tl, app, { scale: 1 }, { scale: k, duration: f(3), ease: E.enter }, at);
          ft(tl, app, { scale: k }, { scale: 1, duration: f(7), ease: E.pop }, at + f(3));
        };
        const flash = (at, stay) => {
          ft(tl, ring, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: f(4), ease: E.enter }, at);
          if (!stay) ft(tl, ring, { opacity: 1 }, { opacity: 0, duration: f(12), ease: E.exit }, at + f(8));
        };
        const tS = gx.settle(ctx, t0);
        // 0 · en el corte: la app (se asienta); las ranuras en fantasma llegan con los carriles (paso 4)
        tl.set(app, { opacity: 1 }, T(tS));
        gsap.set(app, { transformOrigin: "50% 50%" });
        ft(tl, app, { scale: 0.92 }, { scale: 1, duration: f(8), ease: E.pop }, tS);
        ev("enter", tS);
        // 1 · el agente: insignias (pop) y el rótulo sube por su máscara en su palabra
        const tA = Math.max(tS, C("agent", C("label_top", tS + f(4))));
        if (live(tA)) {
          badges.slice().reverse().forEach((b, k) => {
            gsap.set(b, { transformOrigin: "50% 50%" });
            ft(tl, b, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, tA + k * f(2));
          });
          if (labI) gx.maskIn(tl, labI, tA);
          ev("agent", tA);
        }
        // 2 · link: el conector agente → app se dibuja (6 f, velocidad constante) y la app acusa el contacto
        const dL = f(6);
        const tL = Math.max(tA + f(6), C("link", tA + 0.5));
        let tFree = tA + f(6), linked = false;
        if (live(tL)) {
          tl.set([trunk.ol, trunk.gd], { opacity: 1 }, T(tL));
          ft(tl, [trunk.ol, trunk.gd], { strokeDashoffset: trunk.L }, { strokeDashoffset: 0, duration: dL, ease: "none", data: { role: "path" } }, tL);
          const hit = snapUp(tL + dL);
          bump(hit, 1.04);
          ev("link", hit);
          tFree = hit; linked = true;
        }
        // 3 · pulse: un pulso oro recorre el conector y la app se enciende al llegar
        const dP = f(10);
        const tP = Math.max(tFree + f(2), C("pulse", tFree + f(10)));
        if (linked && live(tP + dP)) {
          const arr = snapUp(gx.pulse(tl, dots[0], trunkPts, tP, dP));
          bump(arr, 1.06); flash(arr, false);
          ev("pulse", arr);
        }
        // 4 · carriles fantasma de las vías laterales (en «mediante herramientas») y 5 · cada vía encaja en su cue
        const tin0 = cards.map((_, i) => C("c" + i, null));
        const firstVia = tin0.find((t) => t != null);
        const tLn = Math.max(tFree, Math.min(C("lanes", (firstVia != null ? firstVia : tP + 0.6) - f(10)), (firstVia != null ? firstVia : 1e9) - f(4)));
        if (live(tLn)) lanes.forEach((ln, i) => {
          if (ln.onTrunk) return;
          ft(tl, ln.mp, { strokeDashoffset: ln.L }, { strokeDashoffset: 0, duration: f(9), ease: E.move }, tLn + i * f(2));
        });
        const tSl = live(tLn) ? tLn : tS;   // las ranuras, con los carriles (sin carriles a tiempo, como antes: en el corte)
        slots.forEach((sl, i) => ft(tl, sl, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, tSl + f(2) + i * f(1)));
        let prev = tLn;
        const tin = cards.map((_, i) => { const at = Math.max(prev + f(6), tin0[i] != null ? tin0[i] : prev + 0.5); prev = at; return at; });
        vias.forEach((v, i) => {
          const at = tin[i];
          if (!live(at)) return;
          gsap.set(v.t, { transformOrigin: "50% 50%" });
          ft(tl, v.t, { opacity: 0, scale: 0.84 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, at);
          gx.maskIn(tl, v.lab, at);
          tl.to(slots[i], { opacity: 0, duration: f(4), ease: E.exit }, at + f(3));
          const ln = lanes[i];
          if (!ln.onTrunk) { gx.drawWire(tl, ln.gold, at + f(3), f(8)); tl.to(ln.gh, { opacity: 0, duration: f(4), ease: E.exit }, at + f(9)); }
          ev("card_drop", at);
        });
        // 6 · transform: un pulso por cada carril a la vez (pasan por dentro de cada vía) y la app se enciende
        //    (con «Por tanto» a 22 f del final, el pulso de 14 f acababa en la zona muerta y la fusión no ocurría:
        //    el pulso se acorta hasta 8 f y, si ni así cabe, sale antes; la llegada nunca después de t1 − 7 f)
        const tLast = tin.length ? tin[tin.length - 1] : tP;
        const tEnd = t1 - f(7);
        let tX = Math.max(tLast + f(10), C("transform", null) != null ? C("transform", null) : tLast + 0.6);
        let dX = Math.max(f(8), Math.min(f(14), tEnd - tX));
        if (tX + dX > tEnd + 1e-6) tX = Math.max(tLast + f(4), tEnd - dX);
        if (tX + dX <= tEnd + 1e-6 && (C("transform", null) != null || cards.length)) {
          const paths = lanes.length ? lanes.map((ln) => ln.full) : [trunkPts];
          let arr = tX + dX;
          paths.forEach((p, i) => { arr = gx.pulse(tl, dots[i % dots.length], p, tX, dX); });
          arr = snapUp(arr);
          bump(arr, 1.08); flash(arr, true);
          ev("merge", arr);
        }
        gx.bgIn(tl, bd, t0, t1, 71, props);
        gx.out(tl, props, t1, [box], { dur: f(5), ctx });
      },
    };
  }

  CK.register("flow.pipeline", {
    mount(root, props, ctx) {
      if (props.agent) return mountAgent(root, props, ctx);
      if (props.inputs === "tiles") return mountTiles(root, props, ctx);
      if (props.layout !== "columns") return mountVertical(root, props, ctx); // vertical por defecto
      const E = gx.eases(ctx);
      const st = gx.stage(root, ctx, props, "fp");
      const A = st.A, bd = st.bd;
      const H = A.h, W0 = A.w, W = R(W0 * 0.97), xo = R((W0 - W) / 2);
      const s = Math.max(0.75, Math.min(1.25, W / 860, H / 700));
      A.node.style.setProperty("--s", s);
      const steps = props.steps || [];
      const stepOf = (k) => steps.find((x) => x.kind === k) || {};
      const asCard = (c) => (typeof c === "string" ? { text: c } : c || { text: "" });
      const cardsT = (props.cards && props.cards.length ? props.cards : [stepOf("messy").label || ""]).map(asCard).filter((c) => c.text).slice(0, 3);
      const asOut = (o) => { if (o && typeof o === "object") return { key: o.key || "", value: o.value || "" }; const m = String(o).match(/^\s*([^:]{1,24}):\s*(.+)$/); return m ? { key: m[1], value: m[2] } : { key: "", value: String(o) }; };
      const outsT = (props.outputs && props.outputs.length ? props.outputs : [stepOf("structured").label || ""]).filter(Boolean).map(asOut).slice(0, 3);
      const model = stepOf("model");
      const labels = props.labels || {};
      const wrap = gx.el("div", "fp-wrap", A.node);
      const box = gx.el("div", "fp-box", wrap);
      Object.assign(box.style, { left: xo + "px", width: W + "px" });

      const nCol = Math.max(cardsT.length, outsT.length, 1);
      const gapX = R(20 * s), colW = R((W - (nCol - 1) * gapX) / nCol);
      const colX = (i, n) => R((W - (n * colW + (n - 1) * gapX)) / 2 + i * (colW + gapX));
      const lt = labels.top ? gx.el("div", "fp-label fp-label-top", box) : null;
      const ltWords = lt ? gx.split(lt, labels.top, "chars") : [];
      const lb = labels.bottom ? gx.el("div", "fp-label fp-label-bot", box, labels.bottom) : null;
      const cards = cardsT.map((c, i) => {
        const card = gx.el("div", "fp-card", box);
        if (c.eyebrow) gx.el("div", "fp-eyebrow", card, c.eyebrow);
        const tx = gx.el("div", "fp-ctext", card, c.text);
        const x = colX(i, cardsT.length);
        Object.assign(card.style, { left: x + "px", width: colW + "px" });
        return { card, tx, x, rot: ROT[i % ROT.length] };
      });
      const halo = gx.el("div", "fp-halo", box);
      const grp = gx.el("div", "fp-grp", box);
      const tile = gx.el("div", "fp-tile", grp);
      if (model.asset) gx.logo(tile, ctx, model.asset, "fp-logo");
      else gx.el("div", "fp-tile-label", tile, model.label || "");
      if (model.label && model.asset) gx.el("div", "fp-mlabel", grp, model.label);
      const lnA = gx.el("div", "fp-link", box), lnB = gx.el("div", "fp-link", box);
      const outs = outsT.map((o, i) => {
        const el = gx.el("div", "fp-out", box);
        const k = o.key ? gx.el("div", "fp-okey", el, o.key + ":") : null;
        const v = gx.el("div", "fp-oval", el, o.value);
        const x = colX(i, outsT.length);
        Object.assign(el.style, { left: x + "px", width: colW + "px" });
        return { el, k, v, x };
      });
      gsap.set([...cards.map((c) => c.card), grp, halo, ...outs.map((o) => o.el), lb].filter(Boolean), { opacity: 0 });
      if (lt) gsap.set(ltWords, { opacity: 0 });
      gsap.set([lnA, lnB], { scaleY: 0 });

      return {
        animate(tl, t0, t1, cues) {
          const ex = f(5);
          const ev = evGuard(ctx, t1);
          // ── DOS ENCUADRES. A (entrada): etiqueta · fichas de papel · G · logo, centrado en la banda.
          //    B (salida): logo grande · salidas de tinta APILADAS · «salida útil», centrado y llenando la banda.
          //    Entre ambos, las fichas se absorben tras el logo y la cámara sube (el logo crece) hasta el encuadre B.
          let tileS = R(Math.max(160, Math.min(190 * s, H * 0.27)));
          let cardPx = Math.round(42 * s), labPx = Math.round(52 * s);
          let useTop = !!lt;
          const fitCards = () => cards.forEach((c) => gx.fit(c.tx, { max: cardPx, min: 32, width: colW - 2 * 20 * s, lines: 6 }));
          const sizeA = () => {
            Object.assign(tile.style, { width: tileS + "px", height: tileS + "px" });
            grp.style.setProperty("--tile", tileS + "px");
            if (lt) { gx.fit(lt, { max: labPx, min: 38, width: W, lines: 1 }); lt.style.display = useTop ? "" : "none"; }
          };
          fitCards(); sizeA();
          const rotPad = (c) => Math.abs(Math.sin((c.rot * Math.PI) / 180)) * colW;
          const topH = () => (cards.length ? Math.max(...cards.map((c) => c.card.offsetHeight + rotPad(c))) : 0);
          const labH = (n) => (n && n.style.display !== "none" ? n.offsetHeight + 14 * s : 0);
          let G = 40;
          const FIT = 0.96;
          const solveA = () => { const fixed = labH(lt) + topH() + grp.offsetHeight; G = Math.max(28, Math.min(72 * s, (H * FIT - fixed) * 0.5)); return fixed + G; };
          for (let k = 0; k < 12 && solveA() > H * FIT; k++) {
            if (cardPx > 32) { cardPx -= 2; fitCards(); } else if (tileS > 160) tileS = R(tileS * 0.94); else if (useTop) useTop = false;
            sizeA();
          }
          const totalA = solveA(), gh = grp.offsetHeight, gw = grp.offsetWidth;
          let y = R(Math.max(0, (H - totalA) / 2));
          if (lt && useTop) { lt.style.top = y + "px"; y += labH(lt); }
          const rowCy = R(y + topH() / 2); y += topH();
          const topEdge = y; y += G;
          const grpTop = R(y), grpCy = R(y + tileS / 2);
          cards.forEach((c) => { c.y = R(rowCy - c.card.offsetHeight / 2); c.card.style.top = c.y + "px"; });
          Object.assign(grp.style, { left: R(W / 2 - gw / 2) + "px", top: grpTop + "px" });
          Object.assign(halo.style, { left: R(W / 2 - gw / 2 + tileS / 2 - tileS * 2.1) + "px", top: R(grpCy - tileS * 2.1) + "px", width: R(tileS * 4.2) + "px", height: R(tileS * 4.2) + "px" });
          const cx = R(W / 2 - gw / 2 + tileS / 2); // centro de la BALDOSA (el grupo logo+nombre va centrado en x=540)
          Object.assign(lnA.style, { left: R(cx - 2) + "px", top: R(topEdge + G * 0.22) + "px", height: R(G * 0.56) + "px" });

          // encuadre B: baldosa grande, salidas apiladas (clave rosa + valor blanco en UNA línea), etiqueta espejo
          const n = outs.length;
          let tileB = R(Math.min(240 * s, H * 0.32)), oh = R(Math.min(104 * s, 104)), og = R(18 * s);
          const ow = R(Math.min(W * 0.84, 800 * s)), G2 = R(44 * s), G3 = R(30 * s);
          outs.forEach((o) => { o.el.classList.add("fp-out-row"); Object.assign(o.el.style, { left: R((W - ow) / 2) + "px", width: ow + "px" }); });
          const fitOuts = () => outs.forEach((o) => {
            o.el.style.height = oh + "px";
            const fs = Math.round(Math.min(48 * s, oh * 0.44));
            if (o.k) gx.fit(o.k, { max: Math.round(fs * 0.9), min: 30, width: ow * 0.42, lines: 1 });
            gx.fit(o.v, { max: fs, min: 32, width: ow - 56 * s - (o.k ? o.k.offsetWidth : 0), lines: 1 });
          });
          let useBot = !!lb;
          const sizeB = () => { fitOuts(); if (lb) { gx.fit(lb, { max: Math.round(56 * s), min: 40, width: W, lines: 1 }); lb.style.display = useBot ? "" : "none"; } };
          sizeB();
          const totalB = () => tileB + (n ? G2 + n * oh + (n - 1) * og : 0) + (useBot ? G3 + lb.offsetHeight : 0);
          for (let k = 0; k < 12 && totalB() > H * 0.95; k++) {
            if (oh > 84) oh -= 4; else if (tileB > 180) tileB = R(tileB * 0.95); else if (useBot) useBot = false;
            sizeB();
          }
          const topB = R(Math.max(0, (H - totalB()) / 2));
          const kB = tileB / tileS, dyCam = R(topB + tileB / 2 - grpCy);
          const cxB = R(W / 2 + kB * (cx - W / 2));
          const outY = (i) => R(topB + tileB + G2 + i * (oh + og) - dyCam); // en coordenadas de la caja (antes de la cámara)
          outs.forEach((o, i) => { o.el.style.top = outY(i) + "px"; });
          if (lb) lb.style.top = R(topB + tileB + G2 + n * oh + (n - 1) * og + G3 - dyCam) + "px";
          Object.assign(lnB.style, { left: R(cxB - 2) + "px", top: R(topB + tileB + G2 * 0.18 - dyCam) + "px", height: R(G2 * 0.64) + "px" });
          gsap.set(box, { transformOrigin: `50% ${R(H / 2 - dyCam)}px` }); // el push final escala sobre el centro del encuadre B

          const c = (k, d) => gx.cue(cues, k, d);
          const tS = gx.settle(ctx, t0);
          const tM = Math.max(tS + f(4), c("messy", c("s0", t0 + 0.4)));
          const tL1 = Math.max(tS + f(2), c("label_top", tM));
          const tL2 = c("label_top2", null);
          const tT = Math.max(tM + f(14), c("transform", tM + 0.9));
          const tLB = c("label_bottom", null);
          const tO = Math.max(tT + f(12), c("output", c("s2", tT + 0.5)));

          // 1 · en el corte: el modelo GRANDE y solo en el centro (su halo, la luz del plano)
          const heroK = Math.min(1.6, (H * 0.34) / Math.max(1, gh), (W * 0.85) / Math.max(1, gw)), dyHero = R(H / 2 - grpCy);
          tl.set(grp, { y: dyHero, scale: heroK, transformOrigin: "50% 50%" }, T(tS));
          tl.set(halo, { y: dyHero, scale: heroK, transformOrigin: "50% 50%", opacity: 1 }, T(tS));
          gx.cutIn(tl, grp, tS);
          ev("enter", tS); ev("logo", tS);
          ft(tl, [grp, halo], { y: dyHero, scale: heroK }, { y: 0, scale: 1, duration: f(10), ease: E.move }, tM);
          // 2 · caen las fichas de papel (anticipación, asentado y follow-through), una cada 3 f
          cards.forEach((x, i) => {
            const at = tM + f(2) + i * f(3);
            ev("card_drop", at);
            gx.land(tl, x.card, at, { from: { y: -R(150 * s), rotation: x.rot * 2.2, opacity: 0 }, rot: x.rot, dur: f(9), swing: (i % 2 ? -1 : 1) * 1.4, streak: true });
          });
          // 3 · etiqueta de arriba: «información» y «desordenada» (letras levemente desalineadas que se asientan)
          if (lt && useTop) {
            const words = Array.from(lt.querySelectorAll(".gx-w"));
            const rnd = gx.rng(gx.hash(labels.top));
            words.forEach((w, wi) => {
              const at = wi === 0 ? tL1 : Math.max(tL1 + f(4), tL2 != null ? tL2 : tL1 + 0.45);
              const chs = Array.from(w.querySelectorAll(".gx-ch"));
              if (wi === 0) ft(tl, chs, { opacity: 0, y: R(10 * s) }, { opacity: 1, y: 0, duration: f(6), ease: E.enter }, at);
              else chs.forEach((ch) => ft(tl, ch, { opacity: 0, y: R((rnd() - 0.5) * 16 * s), rotation: (rnd() - 0.5) * 10 },
                { opacity: 1, y: 0, rotation: 0, duration: f(8), ease: E.enter }, at + rnd() * f(2)));
            });
          }
          // 4 · transformación por oclusión: cada ficha se endereza y pasa POR DETRÁS del logo
          ev("flip", tT);
          ft(tl, lnA, { scaleY: 0 }, { scaleY: 1, duration: f(5), ease: E.move }, tT - f(4));
          cards.forEach((x, i) => {
            const at = tT + i * f(4);
            const dx = R(cx - (x.x + colW / 2)), dy = R(grpCy - (x.y + x.card.offsetHeight / 2));
            const k = Math.min(0.5, (tileS * 0.8) / Math.max(colW, x.card.offsetHeight));
            ft(tl, x.card, { rotation: x.rot }, { rotation: 0, duration: f(6), ease: E.move }, at);
            ft(tl, x.card, { x: 0, y: 0, scale: 1 }, { x: dx, y: dy, scale: k, duration: f(8), ease: E.move }, at + f(3));
            gx.streak(tl, x.card, at + f(3), f(8), "y", 10);
            tl.set(x.card, { opacity: 0 }, T(at + f(11))); // escondida tras la baldosa: el cambio de material no se ve
          });
          ft(tl, tile, { scale: 1 }, { scale: 1.06, duration: f(4), ease: E.move }, tT + f(8));
          ft(tl, tile, { scale: 1.06 }, { scale: 1, duration: f(8), ease: E.pop }, tT + f(12));
          // 4b · la cámara sube al encuadre B: la etiqueta de arriba y su conector se van; el logo crece hasta tileB
          const tCam = tT + f(4) * Math.max(0, cards.length - 1) + f(9);
          if (lt && useTop) tl.to(lt, { opacity: 0, duration: f(6), ease: E.exit }, tCam - f(4));
          tl.to(lnA, { opacity: 0, duration: f(5), ease: E.exit }, tCam - f(2));
          ft(tl, box, { y: 0 }, { y: dyCam, duration: f(14), ease: E.move }, tCam);
          ft(tl, grp, { scale: 1 }, { scale: kB, duration: f(14), ease: E.move }, tCam);
          ft(tl, halo, { x: 0, scale: 1 }, { x: cxB - cx, scale: kB, duration: f(14), ease: E.move }, tCam);
          // 5 · las salidas nacen DETRÁS de la baldosa y se apilan debajo (asentado pop + follow-through de 3 px)
          const tPop = Math.max(tCam + f(8), Math.min(tO, tCam + f(12)));
          ft(tl, lnB, { scaleY: 0 }, { scaleY: 1, duration: f(5), ease: E.move }, tPop - f(2));
          outs.forEach((o, i) => {
            const at = tPop + i * f(4);
            const dx = R(cxB - W / 2), dy = R(grpCy - (outY(i) + oh / 2));
            const k = Math.min(0.45, (tileB * 0.7) / ow);
            tl.set(o.el, { x: dx, y: dy, scale: k, opacity: 1 }, T(at)); // nace detrás de la baldosa
            ft(tl, o.el, { x: dx, y: dy, scale: k }, { x: 0, y: 0, scale: 1, duration: f(9), ease: E.pop }, at);
            gx.streak(tl, o.el, at, f(7), "y", 10);
            ft(tl, o.el, { y: 0 }, { y: R(3 * s), duration: f(3), ease: E.move }, at + f(9));
            ft(tl, o.el, { y: R(3 * s) }, { y: 0, duration: f(4), ease: E.move }, at + f(12));
          });
          const tOutEnd = tPop + Math.max(0, n - 1) * f(4) + f(9);
          // 6 · etiqueta de abajo («salida útil»), espejo de la de arriba
          if (lb && useBot) ft(tl, lb, { opacity: 0, y: R(10 * s) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, Math.max(tPop + f(6), tLB != null ? tLB : tOutEnd));
          ev("option", tPop);
          // 7 · quieto; push lento 1,00 → 1,02 sobre el centro del encuadre B
          const tPush = tOutEnd + f(6), tEnd = props.exit === "cut" ? t1 : t1 - ex - f(1);
          if (tEnd - tPush > 0.4) ft(tl, box, { scale: 1 }, { scale: 1.02, duration: tEnd - tPush, ease: E.move }, tPush);
          gx.bgIn(tl, bd, t0, t1, 71, props);
          gx.out(tl, props, t1, [wrap], { dur: ex, ctx });
        },
      };
    },
  });
})(window.CK);
