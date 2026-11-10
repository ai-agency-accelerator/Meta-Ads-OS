// viz.projects — la MISMA tabla de proyectos en tres estados:
//   chaos: columnas (clientes o proyectos) cuyas celdas son TODAS distintas (forma, relleno, giro) con «≠» rojo entre ellas;
//          `big` = una forma grande por columna (gancho); `rows` = filas con su rótulo (Herramientas, Procesos, Entrega).
//   base:  la misma tabla ordenada: la columna central (la solución) se construye, se copia a los lados con «=» y, en
//          `vary`, cada copia cambia UNA pieza a oro (la pequeña variación).
//   adapt: la estructura principal (bloque de tinta con candado) y encima las piezas que se adaptan, cada una en su
//          palabra; `base` enciende la estructura y `same` estampa el sello.
// props: {mode, cards:[{label}], rows:[{label, kind?}], big?, note?, note2?, kicker?, items:[{label}], base_label?,
//         stamp?, canvas?, keep_start?, exit?}
// cues:  chaos: c0…c3, r0…r2, note, shake · base: one, copies, vary, note, note2 · adapt: i0…i5, base, same
// eventos: enter, card, row, note, copy, vary, item, base, stamp, exit
// mode «grow» (copias sin «=»; cada copia enciende más piezas en oro: 1, 2, 3…; evento grow) y `seed`
//   (la baldosa heredada del bloque anterior: grande al centro en el corte, se vuelve la cabecera de la columna).
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
  const KINDS = ["tools", "process", "delivery"];
  const REPEAT_KINDS = ["time", "errors", "auto", "result"];

  function sv(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  // ── vocabulario de formas (abstractas, nunca logos): px de la celda, u = escala
  function glyph(g, k, x, y, r, cls) {
    if (k === "circle") return sv("circle", { cx: x, cy: y, r: r * 0.78, class: cls }, g);
    if (k === "tri") return sv("path", { d: `M${x} ${y - r * 0.9}L${x + r * 0.92} ${y + r * 0.7}L${x - r * 0.92} ${y + r * 0.7}Z`, class: cls }, g);
    if (k === "sq") return sv("rect", { x: x - r * 0.72, y: y - r * 0.72, width: r * 1.44, height: r * 1.44, rx: r * 0.18, class: cls }, g);
    if (k === "bolt") return sv("path", { d: `M${x + r * 0.25} ${y - r}L${x - r * 0.62} ${y + r * 0.18}L${x - r * 0.02} ${y + r * 0.18}L${x - r * 0.28} ${y + r}L${x + r * 0.66} ${y - r * 0.22}L${x + r * 0.08} ${y - r * 0.22}Z`, class: cls }, g);
    if (k === "plus") {
      const a = r * 0.3, b = r * 0.95;
      return sv("path", { d: `M${x - a} ${y - b}H${x + a}V${y - a}H${x + b}V${y + a}H${x + a}V${y + b}H${x - a}V${y + a}H${x - b}V${y - a}H${x - a}Z`, class: cls }, g);
    }
    if (k === "ring") return sv("circle", { cx: x, cy: y, r: r * 0.66, class: cls + "-s" }, g);
    return sv("path", { d: `M${x - r * 0.85} ${y + r * 0.2}Q${x - r * 0.42} ${y - r * 0.9} ${x} ${y}T${x + r * 0.85} ${y - r * 0.2}`, class: cls + "-s" }, g);
  }
  function tile(g, x, y, sz, paint, gk, gpaint) {
    const grp = sv("g", {}, g);
    sv("rect", { x, y, width: sz, height: sz, rx: sz * 0.24, class: "pj-p-" + paint }, grp);
    glyph(grp, gk, x + sz / 2, y + sz / 2, sz * 0.3, "pj-p-" + gpaint);
    return grp;
  }
  const TOOL_GLYPHS = ["circle", "tri", "sq"];
  function toolRect(w, h, u, i) {               // baldosa i de la fila canónica (tres en línea)
    const sz = u * 62, gap = u * 15, x0 = w / 2 - (3 * sz + 2 * gap) / 2;
    return { x: x0 + i * (sz + gap), y: h / 2 - sz / 2, sz };
  }
  function drawTools(g, w, h, u, v) {
    const cy = h / 2;
    if (v === 0) { TOOL_GLYPHS.forEach((k, i) => { const t = toolRect(w, h, u, i); tile(g, t.x, t.y, t.sz, "ink", k, "paper"); }); return; }
    u *= 1.15;
    if (v === 1) {
      const sz = u * 50;
      tile(g, w / 2 - sz * 1.45, cy - sz * 0.95, sz, "gold", "bolt", "ink");
      tile(g, w / 2 - sz * 0.35, cy - sz * 0.25, sz * 1.15, "line", "plus", "ink");
      tile(g, w / 2 + sz * 0.95, cy - sz * 1.05, sz * 0.8, "ink", "circle", "gold");
    } else {
      const big = u * 84, sm = u * 44;
      tile(g, w / 2 - big * 0.85, cy - big / 2, big, "line", "ring", "ink");
      tile(g, w / 2 + big * 0.3, cy - big / 2 + u * 2, sm, "ink", "wave", "paper");
      tile(g, w / 2 + big * 0.3 + u * 12, cy + u * 8, sm * 0.8, "gold", "tri", "ink");
    }
  }
  function drawProcess(g, w, h, u, v) {
    const pts = v === 0 ? [[0.2, 0.5], [0.5, 0.5], [0.8, 0.5]]
      : v === 1 ? [[0.13, 0.72], [0.38, 0.28], [0.62, 0.72], [0.87, 0.28]]
        : [[0.5, 0.2], [0.76, 0.8], [0.24, 0.8]];
    const P = pts.map(([a, b]) => [R(a * w), R(b * h)]);
    const r = u * 17;
    if (v === 2) {                              // un bucle: curvas entre los tres nodos
      for (let i = 0; i < 3; i++) {
        const [x1, y1] = P[i], [x2, y2] = P[(i + 1) % 3];
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, cx = w / 2, cy = h * 0.6;
        sv("path", { d: `M${x1} ${y1}Q${R(mx + (mx - cx) * 0.6)} ${R(my + (my - cy) * 0.6)} ${x2} ${y2}`, class: "pj-edge" }, g);
      }
    } else sv("polyline", { points: P.map((p) => p.join(",")).join(" "), class: "pj-edge" }, g);
    const paint = v === 0 ? "ink" : v === 1 ? "gold" : "line";
    P.forEach(([x, y]) => sv("circle", { cx: x, cy: y, r, class: "pj-p-" + paint }, g));
  }
  function drawDelivery(g, w, h, u, v) {
    const cx = w / 2, cy = h / 2;
    u *= 1.08;
    if (v === 0) {                              // documento
      const dw = u * 72, dh = u * 92, x = cx - dw / 2, y = cy - dh / 2, k = u * 20;
      sv("path", { d: `M${x} ${y}H${x + dw - k}L${x + dw} ${y + k}V${y + dh}H${x}Z`, class: "pj-p-line" }, g);
      sv("path", { d: `M${x + dw - k} ${y}V${y + k}H${x + dw}`, class: "pj-edge-thin" }, g);
      [0.4, 0.58, 0.76].forEach((t, i) => sv("rect", { x: x + u * 13, y: y + dh * t - u * 3, width: (dw - u * 26) * (i === 2 ? 0.6 : 1), height: u * 6, rx: u * 3, class: "pj-p-ink" }, g));
    } else if (v === 1) {                       // paquete
      const bw = u * 100, bh = u * 66, lid = u * 18, x = cx - (bw + lid) / 2, y = cy - bh / 2 + u * 10;
      sv("path", { d: `M${x} ${y}L${x + lid} ${y - lid}H${x + bw + lid}L${x + bw} ${y}Z`, class: "pj-p-golddk" }, g);
      sv("path", { d: `M${x + bw} ${y}L${x + bw + lid} ${y - lid}V${y + bh - lid}L${x + bw} ${y + bh}Z`, class: "pj-p-golddk" }, g);
      sv("rect", { x, y, width: bw, height: bh, class: "pj-p-gold" }, g);
      sv("rect", { x: x + bw / 2 - u * 7, y, width: u * 14, height: bh, class: "pj-p-ink" }, g);
    } else {                                    // pantalla
      const sw = u * 126, sh = u * 76, x = cx - sw / 2, y = cy - sh / 2 - u * 10;
      sv("rect", { x, y, width: sw, height: sh, rx: u * 10, class: "pj-p-line" }, g);
      sv("rect", { x: x + u * 11, y: y + u * 11, width: sw - u * 22, height: sh - u * 22, rx: u * 4, class: "pj-p-ink" }, g);
      sv("rect", { x: cx - u * 6, y: y + sh, width: u * 12, height: u * 13, class: "pj-p-ink" }, g);
      sv("rect", { x: cx - u * 30, y: y + sh + u * 13, width: u * 60, height: u * 7, rx: u * 3.5, class: "pj-p-ink" }, g);
    }
  }
  function drawBig(g, w, h, v) {
    const cx = w / 2, cy = h / 2, r = Math.min(w, h) * 0.39;
    if (v % 4 === 0) return sv("circle", { cx, cy, r, class: "pj-p-ink" }, g);
    if (v % 4 === 1) return sv("path", { d: `M${cx} ${cy - r * 1.05}L${cx + r * 1.12} ${cy + r * 0.86}L${cx - r * 1.12} ${cy + r * 0.86}Z`, class: "pj-p-gold pj-thick" }, g);
    if (v % 4 === 2) {
      const pts = [];
      for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.46 : r * 1.04; pts.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]); }
      return sv("path", { d: "M" + pts.map((p) => p.map((x) => x.toFixed(1)).join(" ")).join("L") + "Z", class: "pj-p-line pj-thick" }, g);
    }
    return sv("rect", { x: cx - r * 0.85, y: cy - r * 0.85, width: r * 1.7, height: r * 1.7, rx: r * 0.2, class: "pj-p-ink" }, g);
  }
  // repetir: cada implementación del mismo proyecto, un poco mejor (esquema, sin cifras). p = 0…1 (primera → última)
  function drawRepeat(g, w, h, u, kind, p) {
    const cx = w / 2, cy = h / 2, last = p >= 1, hot = last ? "gold" : "ink", anim = [];
    if (kind === "time") {                      // lo que tardas: la barra se acorta
      const tw = w * 0.76, x = cx - tw / 2, bh = u * 18;
      sv("rect", { x, y: cy - bh / 2, width: tw, height: bh, rx: bh / 2, class: "pj-track-bg" }, g);
      const fill = sv("rect", { x, y: cy - bh / 2, width: Math.max(bh, tw * (1 - 0.66 * p)), height: bh, rx: bh / 2, class: "pj-p-" + hot }, g);
      anim.push({ kind: "grow_x", el: fill });
    } else if (kind === "errors") {             // los errores: cruces rojas que pasan a resueltos
      const errs = p <= 0 ? 3 : p < 1 ? 1 : 0;
      for (let k = 0; k < 3; k++) {
        const x = cx + (k - 1) * u * 50, r = u * 18, m = sv("g", {}, g);
        if (k < errs) {
          sv("circle", { cx: x, cy, r, class: "pj-err" }, m);
          sv("path", { d: `M${x - r * 0.42} ${cy - r * 0.42}L${x + r * 0.42} ${cy + r * 0.42}M${x + r * 0.42} ${cy - r * 0.42}L${x - r * 0.42} ${cy + r * 0.42}`, class: "pj-err-x" }, m);
        } else {
          sv("circle", { cx: x, cy, r, class: "pj-p-" + hot }, m);
          sv("path", { d: `M${x - r * 0.45} ${cy + r * 0.02}L${x - r * 0.1} ${cy + r * 0.36}L${x + r * 0.48} ${cy - r * 0.34}`, class: last ? "pj-ok-ink" : "pj-ok" }, m);
        }
        anim.push({ kind: "pop", el: m });
      }
    } else if (kind === "auto") {               // lo que automatizas: más piezas encendidas
      const lit = Math.round(2 * p), sz = u * 50, gap = u * 14, x0 = cx - (3 * sz + 2 * gap) / 2;
      for (let k = 0; k < 3; k++) {
        const on = k < lit, t = tile(g, x0 + k * (sz + gap), cy - sz / 2, sz, on ? "gold" : "line", on ? "bolt" : "circle", on ? "ink" : "ink");
        if (on) anim.push({ kind: "pop", el: t });
      }
    } else {                                    // el resultado: el nivel sube
      const bw = u * 22, gap = u * 12, hs = [u * 26, u * 44, u * 62], x0 = cx - (3 * bw + 2 * gap) / 2, base = cy + u * 32;
      const full = Math.round(1 + 2 * p);
      for (let k = 0; k < 3; k++) {
        const on = k < full, b = sv("rect", { x: x0 + k * (bw + gap), y: base - hs[k], width: bw, height: hs[k], rx: u * 5, class: on ? "pj-p-" + hot : "pj-track-bg" }, g);
        if (on) anim.push({ kind: "grow_y", el: b });
      }
    }
    return anim;
  }

  // ── tabla (chaos | base | repeat)
  function mountTable(wrap, A, props, ctx, mode) {
    const cards = (props.cards || [{ label: "1" }, { label: "2" }, { label: "3" }]).slice(0, 4);
    const n = cards.length, big = mode === "chaos" && !!props.big, rep = mode === "repeat";
    const fromChaos = mode === "base" && props.from === "chaos";
    const rows = big ? [{ kind: "big" }]
      : (props.rows || [{ label: "Herramientas" }, { label: "Procesos" }, { label: "Entrega" }]).slice(0, 4)
        .map((r, i) => ({ label: r.label, kind: r.kind || (rep ? REPEAT_KINDS[i % 4] : KINDS[i % 3]) }));
    const hasNote = !!(props.note || props.note2);
    // `grow`: la columna se repite (copias SIN «=») y cada copia enciende más piezas (1, 2, 3);
    // `seed` = la baldosa elegida del bloque anterior (asset o glifo): llega grande al centro y se vuelve la cabecera
    const grow = mode === "grow", seed = grow && props.seed && typeof props.seed === "object" ? props.seed : null;
    const headH = seed ? 140 : 72, headGap = rep ? 30 : 24, eyeH = big ? 0 : 50, cellH = big ? 300 : rep ? 96 : 124, rowGap = big ? 0 : 18;
    const noteGap = 34, noteH = 84;
    const need = headH + headGap + rows.length * (eyeH + cellH) + (rows.length - 1) * rowGap + (hasNote ? noteGap + noteH : 0);
    // grow: la nota acaba a ≥ 80 px del raíl de subtítulos (el bloque usa el alto hasta ahí)
    const Hu = grow && ctx.railY && ctx.railY > A.y + 200 ? Math.min(A.h, ctx.railY - 80 - A.y) : A.h;
    const s = Math.max(0.6, Math.min(1.15, A.w / 950, (Hu * 0.96) / need));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    const gapX = S(big ? 104 : 76), colW = R(Math.min(S(280), (A.w - (n - 1) * gapX - S(28)) / n));
    const tw = n * colW + (n - 1) * gapX, x0 = R((A.w - tw) / 2);
    const y0 = R(Math.max(0, (Hu - S(need)) / 2));
    const xs = cards.map((_, i) => x0 + i * (colW + gapX));
    const yRow = (k) => y0 + S(headH + headGap) + k * S(eyeH + cellH + rowGap);
    const yEnd = yRow(rows.length - 1) + S(eyeH + cellH);
    const mid = Math.floor((n - 1) / 2);
    // el desorden del caos (misma semilla en `chaos` y en `base` desde el caos: la tabla vuelve exactamente igual)
    const rnd = gx.rng(gx.hash(JSON.stringify(cards) + "chaos" + rows.length));
    const messOf = () => ({ rot: (rnd() * 2 - 1) * (big ? 7 : 5), dx: R((rnd() * 2 - 1) * S(10)), dy: R((rnd() * 2 - 1) * S(8)) });

    const ghosts = rows.map((r, k) => cards.map((c, i) => {
      if (props.ghost !== true) return null;
      const gd = gx.el("div", "pj-ghost", wrap);
      Object.assign(gd.style, { left: xs[i] + "px", top: (yRow(k) + S(eyeH)) + "px", width: colW + "px", height: S(cellH) + "px" });
      return gd;
    }));
    const heads = cards.map((c, i) => {
      if (seed) {   // cabecera = la baldosa heredada (misma en todas las copias) con su número en una chapa
        const z = S(headH), h = gx.el("div", "pj-seed", wrap);
        Object.assign(h.style, { left: R(xs[i] + colW / 2 - z / 2) + "px", top: y0 + "px", width: z + "px", height: z + "px" });
        gx.icon(h, ctx, { asset: seed.asset, glyph: seed.glyph || (seed.asset ? null : "target"), tone: seed.tone || "gold" }, "pj-seed-ic");
        if (c.label) h.badge = gx.el("div", "pj-badge", h, c.label);
        return h;
      }
      const h = gx.el("div", "pj-head", wrap, c.label || "");
      Object.assign(h.style, { left: xs[i] + "px", top: y0 + "px", width: colW + "px", height: S(headH) + "px" });
      return h;
    });
    const eyes = rows.map((r, k) => {
      if (big || !r.label) return null;
      const e = gx.el("div", "pj-eye", wrap, r.label);
      Object.assign(e.style, { left: "0px", width: A.w + "px", top: yRow(k) + "px", height: S(eyeH) + "px" });
      return e;
    });
    const cells = rows.map((r, k) => cards.map((c, i) => {
      const d = gx.el("div", "pj-cell pj-tile", wrap);
      const cw = colW, ch = S(cellH);
      Object.assign(d.style, { left: xs[i] + "px", top: (yRow(k) + S(eyeH)) + "px", width: cw + "px", height: ch + "px" });
      const lit = grow ? gx.el("div", "pj-lit", d) : null;   // grow: la pieza encendida (fondo oro bajo su dibujo)
      const svgN = sv("svg", { width: cw, height: ch, viewBox: `0 0 ${cw} ${ch}`, class: "pj-svg" }, d);
      const g = sv("g", {}, svgN);
      const m = mode === "chaos" || fromChaos ? messOf() : { rot: 0, dx: 0, dy: 0 };
      const out = { d, g, gK: null, gold: null, anim: [], ring: null, rot: m.rot, dx: m.dx, dy: m.dy };
      if (rep) out.anim = drawRepeat(g, cw, ch, s, r.kind, n > 1 ? i / (n - 1) : 1);
      else if (r.kind === "big") drawBig(g, cw, ch, i);
      else if (grow && r.kind === "meter") {
        // medidor de instrumento por copia (como viz.gauges): pista, marcas y arco de oro que se llena más en cada copia
        const R0 = Math.min(cw * 0.36, ch * 0.62), cx = cw / 2, cy = ch * 0.5 + R0 * 0.42, Lm = Math.PI * R0;
        const arcD = `M ${R(cx - R0)} ${R(cy)} A ${R(R0)} ${R(R0)} 0 0 1 ${R(cx + R0)} ${R(cy)}`;
        sv("path", { d: arcD, class: "pj-m-track" }, g);
        for (let q = 0; q <= 4; q++) { const a = Math.PI + (q / 4) * Math.PI, r1 = R0 + S(10), r2 = R0 + S(18);
          sv("line", { x1: R(cx + Math.cos(a) * r1), y1: R(cy + Math.sin(a) * r1), x2: R(cx + Math.cos(a) * r2), y2: R(cy + Math.sin(a) * r2), class: "pj-m-tick" }, g); }
        const fill = sv("path", { d: arcD, class: "pj-m-fill" }, g);
        fill.style.strokeDasharray = `${Lm} ${Lm}`; fill.style.strokeDashoffset = Lm;
        sv("circle", { cx: R(cx), cy: R(cy), r: S(9), class: "pj-m-hub" }, g);
        out.meter = { fill, L: Lm, frac: n > 1 ? (i + 1) / n : 1 };
      } else if (grow && r.kind === "icon") {
        // el icono real de la automatización elegida (el `seed`), igual en cada copia
        const ic = gx.icon(d, ctx, { asset: seed && seed.asset, glyph: (seed && seed.glyph) || (seed && seed.asset ? null : "target"), tone: (seed && seed.tone) || "gold" }, "pj-cell-ic");
        out.icon = ic;
      }
      else {
        const draw = r.kind === "tools" ? drawTools : r.kind === "process" ? drawProcess : drawDelivery;
        if (!(grow && (r.kind === "meter" || r.kind === "icon"))) draw(g, cw, ch, s, mode === "chaos" || fromChaos ? i % 3 : 0);
        if (fromChaos) { out.gK = sv("g", {}, svgN); draw(out.gK, cw, ch, s, 0); }   // la versión ordenada, encima
        if (mode === "base" && r.kind === "tools") {   // la pequeña variación: una baldosa distinta por copia, en oro
          const t = toolRect(cw, ch, s, i % 3);
          out.gold = gx.el("div", "pj-vary", d);
          Object.assign(out.gold.style, { left: R(t.x - S(4)) + "px", top: R(t.y - S(4)) + "px", width: R(t.sz + S(8)) + "px", height: R(t.sz + S(8)) + "px" });
          const z = R(t.sz + S(8)), gg = sv("g", {}, sv("svg", { width: z, height: z, viewBox: `0 0 ${z} ${z}`, class: "pj-svg" }, out.gold));
          tile(gg, S(4), S(4), t.sz, "gold", TOOL_GLYPHS[i % 3], "ink");
        }
      }
      if (rep && i === n - 1) out.ring = gx.el("div", "pj-best", d);
      out.lit = lit;
      return out;
    }));
    const mkSign = (txt, cls, cx, cy) => {
      const sg = gx.el("div", "pj-sign " + cls + (big ? " pj-sign-big" : ""), wrap, txt);
      Object.assign(sg.style, { left: R(cx - gapX / 2) + "px", top: R(cy - S(44)) + "px", width: gapX + "px", height: S(88) + "px" });
      return sg;
    };
    const rowSigns = (txt, cls) => rows.map((r, k) => cards.slice(0, -1).map((_, i) =>
      mkSign(txt, cls, xs[i] + colW + gapX / 2, yRow(k) + S(eyeH) + S(cellH) / 2)));
    const neq = mode === "chaos" || fromChaos ? rowSigns("≠", "pj-neq") : null;
    const eq = mode === "base" ? rowSigns("=", "pj-eq") : null;
    const arrows = rep ? cards.slice(0, -1).map((_, i) => mkSign("→", "pj-arrow", xs[i] + colW + gapX / 2, y0 + S(headH) / 2)) : [];
    const yN = yEnd + S(noteGap);
    const mkNote = (txt) => {
      if (!txt) return null;
      const nn = gx.el("div", "pj-note", wrap, txt);
      Object.assign(nn.style, { left: "0px", width: A.w + "px", top: yN + "px", height: S(noteH) + "px" });
      return nn;
    };
    const note = mkNote(props.note), note2 = mkNote(props.note2);
    const allCells = cells.flat(), allGhosts = ghosts.flat().filter(Boolean);
    const signsAll = [].concat(neq ? neq.flat() : [], eq ? eq.flat() : [], arrows);
    gsap.set(allGhosts.concat(heads, eyes.filter(Boolean), allCells.map((c) => c.d), signsAll, [note, note2].filter(Boolean)), { opacity: 0 });
    gsap.set(allCells.filter((c) => c.gold).map((c) => c.gold), { opacity: 0 });
    gsap.set(allCells.filter((c) => c.lit).map((c) => c.lit), { opacity: 0 });
    heads.forEach((h) => { if (h.badge) gsap.set(h.badge, { opacity: 0 }); });
    gsap.set(allCells.filter((c) => c.gK).map((c) => c.gK), { opacity: 0 });
    gsap.set(allCells.filter((c) => c.ring).map((c) => c.ring), { opacity: 0 });
    allCells.forEach((c) => c.anim.forEach((a) => {
      if (a.kind === "grow_x") gsap.set(a.el, { scaleX: 0, transformOrigin: "0% 50%" });
      else if (a.kind === "grow_y") gsap.set(a.el, { scaleY: 0, transformOrigin: "50% 100%" });
      else gsap.set(a.el, { opacity: 0, scale: 0.4, transformOrigin: "50% 50%" });
    }));
    if (fromChaos) allCells.forEach((c) => gsap.set(c.d, { x: c.dx, y: c.dy, rotation: c.rot }));

    function animate(tl, tS, t1, cues, E) {
      const C = (k, d) => gx.cue(cues, k, d);
      heads.forEach((h) => { h.style.fontSize = Math.max(30, S(34)) + "px"; });  // píldora de ancho fijo: cuerpo fijo
      eyes.forEach((e) => e && gx.fit(e, { max: Math.max(30, S(34)), min: 30, width: A.w, lines: 1 }));
      [note, note2].forEach((nn) => nn && gx.fit(nn, { max: S(68), min: 44, width: A.w, lines: 1 }));
      if (allGhosts.length) gx.cutIn(tl, allGhosts, tS);
      const unghost = (k, i, at) => { const gd = ghosts[k] && ghosts[k][i]; if (gd) ft(tl, gd, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.enter }, at); };
      const noteIn = (nn, at) => { gx.textIn(tl, nn, at, { rise: S(32) }); gx.ev(ctx, "note", at); };   // kit v14
      const headIn = (h, at) => gx.textIn(tl, h, at, { rise: S(32) });   // kit v14
      // los rótulos de fila se ven tenues desde el corte (la tabla ya es una tabla) y se encienden en su palabra
      // kit v14: los rótulos en fantasma también ENTRAN (8 f de subida, opacidad en 10 f), no aparecen en 4 f
      const eyeFaint = () => eyes.forEach((e) => { if (!e) return; ft(tl, e, { opacity: 0 }, { opacity: 0.3, duration: f(10), ease: E.enter }, tS); ft(tl, e, { y: S(32) }, { y: 0, duration: f(8), ease: E.enter }, tS); });
      const eyeOn = (k, at) => { if (eyes[k]) ft(tl, eyes[k], { opacity: 0.3 }, { opacity: 1, duration: f(6), ease: E.enter }, at); };
      let tLast = tS;

      if (mode === "chaos") {
        const tc = [];
        cards.forEach((_, i) => { tc.push(Math.max(i ? tc[i - 1] + f(3) : tS, C("c" + i, tS + f(2) + i * f(5)))); });
        heads.forEach((h, i) => { headIn(h, tc[i]); gx.ev(ctx, "card", tc[i]); });
        if (!big) eyeFaint();
        tLast = tc[n - 1] + f(8);
        let tPrevRow = tc[n - 1] + f(4);
        rows.forEach((r, k) => {
          const tr = big ? null : Math.max(tPrevRow, C("r" + k, tPrevRow + 0.8));
          if (!big) { eyeOn(k, tr); gx.ev(ctx, "row", tr); tPrevRow = tr + f(8); }
          cells[k].forEach((c, i) => {
            const at = big ? tc[i] + f(2) : tr + f(2) + i * f(3);
            ft(tl, c.d, { opacity: 0, x: c.dx, y: c.dy - S(big ? 70 : 44), rotation: c.rot * 3, scale: 0.8 },
              { opacity: 1, x: c.dx, y: c.dy, rotation: c.rot, scale: 1, duration: f(big ? 11 : 9), ease: E.pop }, at);
            unghost(k, i, at + f(3));
            tLast = Math.max(tLast, at + f(big ? 11 : 9));
          });
          neq[k].forEach((sg, j) => {
            const at = big ? Math.max(tc[j + 1] + f(6), C("signs", 0) + j * f(3)) : tr + f(9) + j * f(3);
            ft(tl, sg, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(7), ease: E.pop }, at);
            tLast = Math.max(tLast, at + f(7));
          });
        });
        if (note) { const tn = Math.max(tc[n - 1] + f(6), C("note", tLast + 0.3)); noteIn(note, tn); tLast = Math.max(tLast, tn + f(8)); }
        // nada quieto: piezas «nerviosas» (giro y posición con semilla); desde `shake` el desorden crece y los ≠ laten
        const tSh = C("shake", 1e9);
        allCells.forEach((c, idx) => {
          const r2 = gx.rng(gx.hash("pj-j" + idx + mode + n));
          let px = c.dx, py = c.dy, pr = c.rot;
          for (let t = tLast + f(4) + (idx % 4) * 0.13; t < t1 - 0.4; t += 0.62) {
            const amp = t >= tSh ? 3.2 : 1;
            const nx = R(c.dx + (r2() * 2 - 1) * S(5) * amp), ny = R(c.dy + (r2() * 2 - 1) * S(4) * amp), nr = c.rot + (r2() * 2 - 1) * 1.6 * amp;
            ft(tl, c.d, { x: px, y: py, rotation: pr }, { x: nx, y: ny, rotation: nr, duration: 0.58, ease: E.move }, t);
            px = nx; py = ny; pr = nr;
          }
        });
        if (tSh < t1 - 0.3) neq.flat().forEach((sg, j) => {
          const at = tSh + j * f(2);
          ft(tl, sg, { scale: 1 }, { scale: 1.42, duration: f(5), ease: E.enter }, at);
          ft(tl, sg, { scale: 1.42 }, { scale: 1, duration: f(9), ease: E.move }, at + f(5));
        });
      } else if (grow) {
        // grow: la columna 1 (con su cabecera heredada) se construye en «one»; en «copies» se copia a la derecha (sin
        // «=»); en «vary» cada copia enciende MÁS piezas (1, 2, 3…) de izquierda a derecha: cada vez mejor
        const tOne = Math.max(tS, C("one", tS + f(4)));
        if (seed) {
          const h0 = heads[0], hr = parseFloat(h0.style.left), ht = parseFloat(h0.style.top), z = S(headH);
          const k0 = Math.min(2.6, (A.h * 0.36) / z), dx0 = R(A.w / 2 - (hr + z / 2)), dy0 = R(A.h / 2 - (ht + z / 2));
          gsap.set(h0, { opacity: 1, x: dx0, y: dy0, scale: k0, transformOrigin: "50% 50%" });   // llega del plano anterior
          tl.set(h0, { opacity: 1, x: dx0, y: dy0, scale: k0 }, gx.T(tS));
          ft(tl, h0, { x: dx0, y: dy0, scale: k0 }, { x: 0, y: 0, scale: 1, duration: f(12), ease: E.move }, tOne);
          gx.streak(tl, h0, tOne + f(2), f(8), "y", 10);
          if (h0.badge) ft(tl, h0.badge, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: f(6), ease: E.pop }, tOne + f(10));
        } else headIn(heads[0], tOne);
        gx.ev(ctx, "card", tOne);
        eyes.forEach((e, k) => e && ft(tl, e, { opacity: 0, y: S(12) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, tOne + f(8) + k * f(2)));
        cells.forEach((row, k) => {
          ft(tl, row[0].d, { opacity: 0, y: S(26), scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: f(8), ease: E.enter }, tOne + f(8) + k * f(3));
          unghost(k, 0, tOne + f(10) + k * f(3));
        });
        if (note) noteIn(note, Math.max(tOne + f(10), C("note", tOne + f(12))));
        const tCp = Math.max(tOne + f(18), C("copies", tOne + 0.9));
        cards.forEach((_, i) => {
          if (i === 0) return;
          const at = tCp + (i - 1) * f(4);
          if (seed) ft(tl, heads[i], { opacity: 1, x: xs[0] - xs[i] }, { opacity: 1, x: 0, duration: f(12), ease: E.move }, at);
          else headIn(heads[i], at + f(6));   // píldora de texto: sube en su sitio (nunca un texto encima de otro)
          if (heads[i].badge) ft(tl, heads[i].badge, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: f(6), ease: E.pop }, at + f(10));
          cells.forEach((row, k) => {
            ft(tl, row[i].d, { opacity: 1, x: xs[0] - xs[i] }, { opacity: 1, x: 0, duration: f(12), ease: E.move }, at + k * f(1));
            unghost(k, i, at + f(8));
          });
        });
        gx.ev(ctx, "copy", tCp);
        // cada copia enciende más piezas: columna i → sus i+1 primeras filas en oro (acumulativo)
        const tV = Math.max(tCp + (n - 1) * f(4) + f(12), C("vary", tCp + 1.0));
        gx.ev(ctx, "vary", tV);
        cards.forEach((_, i) => {
          const tc = tV + i * f(7);
          const lit = Math.min(rows.length, i + 1);
          for (let k = 0; k < rows.length; k++) {
            const c = cells[k][i], at = tc + k * f(2);
            if (c.meter) {   // el medidor de esta copia se llena hasta su nivel (1/n, 2/n, …): cada vez mejor
              ft(tl, c.meter.fill, { strokeDashoffset: c.meter.L }, { strokeDashoffset: c.meter.L * (1 - c.meter.frac), duration: f(14), ease: E.move }, at);
              continue;
            }
            if (k >= lit) continue;
            if (c.icon) {   // el icono (oro) no se pinta sobre oro: late
              ft(tl, c.d, { scale: 1 }, { scale: 1.08, duration: f(3), ease: E.enter }, at);
              ft(tl, c.d, { scale: 1.08 }, { scale: 1, duration: f(7), ease: E.pop }, at + f(3));
              continue;
            }
            ft(tl, c.lit, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: f(6), ease: E.enter }, at);
            ft(tl, c.d, { scale: 1 }, { scale: 1.06, duration: f(3), ease: E.enter }, at);
            ft(tl, c.d, { scale: 1.06 }, { scale: 1, duration: f(7), ease: E.pop }, at + f(3));
          }
          gx.ev(ctx, "grow", tc);
        });
        if (note2) {
          const t2 = Math.max(tV + (n - 1) * f(7), C("note2", tV + f(8)));
          if (note) ft(tl, note, { opacity: 1, y: 0 }, { opacity: 0, y: -S(14), duration: f(4), ease: E.exit }, t2);
          noteIn(note2, t2 + f(4));
        }
        // nada quieto: la última copia (la mejor) late mientras se lee
        const lastCol = cells.map((row) => row[n - 1].d);
        for (let tb = tV + (n - 1) * f(7) + 1.0; tb < t1 - 0.5; tb += 1.2) {
          ft(tl, lastCol, { scale: 1 }, { scale: 1.04, duration: f(6), ease: E.enter }, tb);
          ft(tl, lastCol, { scale: 1.04 }, { scale: 1, duration: f(9), ease: E.move }, tb + f(6));
        }
      } else if (mode === "base") {
        // base: la solución (columna central) → copias a los lados con «=» → cada copia cambia una pieza a oro.
        // Con `from: "chaos"` la tabla del caos está en el corte y se ORDENA: primero la central, luego las laterales.
        const tOne = Math.max(tS, C("one", tS));
        const straighten = (c, at) => {
          ft(tl, c.d, { x: c.dx, y: c.dy, rotation: c.rot }, { x: 0, y: 0, rotation: 0, duration: f(10), ease: E.move }, at);
          ft(tl, c.g, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.enter }, at);
          ft(tl, c.gK, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, at + f(2));
        };
        if (fromChaos) {
          gx.cutIn(tl, heads.concat(eyes.filter(Boolean), allCells.map((c) => c.d), neq.flat()), tS);
          cells.forEach((row, k) => straighten(row[mid], tOne + k * f(2)));
        } else {
          eyes.forEach((e, k) => e && ft(tl, e, { opacity: 0, y: S(12) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, tOne + k * f(2)));
          cells.forEach((row, k) => {
            ft(tl, row[mid].d, { opacity: 0, y: S(26), scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: f(8), ease: E.enter }, tOne + f(2) + k * f(3));
            unghost(k, mid, tOne + f(4) + k * f(3));
          });
        }
        gx.ev(ctx, "card", tOne);
        if (note) noteIn(note, Math.max(tOne + f(4), C("note", tOne + f(6))));
        const tCp = Math.max(tOne + f(12), C("copies", tOne + 0.8));
        cards.forEach((_, i) => {
          if (i === mid) return;
          cells.forEach((row, k) => {
            const c = row[i], at = tCp + Math.abs(i - mid) * f(2) + k * f(2);
            if (fromChaos) straighten(c, at);
            else { ft(tl, c.d, { opacity: 1, x: xs[mid] - xs[i] }, { opacity: 1, x: 0, duration: f(12), ease: E.move }, tCp); unghost(k, i, tCp + f(8)); }
          });
        });
        if (!fromChaos) heads.forEach((h, i) => headIn(h, tCp + f(8) + i * f(2)));
        if (neq) neq.flat().forEach((sg) => ft(tl, sg, { opacity: 1, scale: 1 }, { opacity: 0, scale: 0.6, duration: f(4), ease: E.exit }, tCp + f(4)));
        eq.flat().forEach((sg, j) => ft(tl, sg, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(7), ease: E.pop }, tCp + f(fromChaos ? 9 : 12) + (j % (n - 1)) * f(2)));
        gx.ev(ctx, "copy", tCp);
        const tV = Math.max(tCp + f(14), C("vary", tCp + 0.8));
        const golds = allCells.filter((c) => c.gold).map((c) => c.gold);
        golds.forEach((g, j) => ft(tl, g, { opacity: 0, scale: 1.5 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, tV + j * f(4)));
        gx.ev(ctx, "vary", tV);
        if (note2) {
          const t2 = Math.max(tV, C("note2", tV + f(2)));
          if (note) ft(tl, note, { opacity: 1, y: 0 }, { opacity: 0, y: -S(14), duration: f(4), ease: E.exit }, t2);
          noteIn(note2, t2 + f(4));
        }
        for (let tb = tV + 1.1; tb < t1 - 0.5; tb += 1.1) golds.forEach((g, j) => {
          ft(tl, g, { scale: 1 }, { scale: 1.09, duration: f(6), ease: E.enter }, tb + j * f(3));
          ft(tl, g, { scale: 1.09 }, { scale: 1, duration: f(9), ease: E.move }, tb + j * f(3) + f(6));
        });
      } else {
        // repeat: el MISMO proyecto, cliente tras cliente; cada fila en su palabra y la última columna, mejor
        const tc = [];
        cards.forEach((_, i) => { tc.push(Math.max(i ? tc[i - 1] + f(4) : tS, C("c" + i, tS + f(2) + i * f(6)))); });
        heads.forEach((h, i) => { headIn(h, tc[i]); gx.ev(ctx, "card", tc[i]); });
        arrows.forEach((a, j) => ft(tl, a, { opacity: 0, x: -S(16) }, { opacity: 1, x: 0, duration: f(7), ease: E.enter }, tc[j + 1]));
        eyeFaint();
        let tPrev = tc[n - 1] + f(6);
        const tRow = [];
        rows.forEach((r, k) => {
          const tr = Math.max(tPrev, C("r" + k, tPrev + 0.9));
          tRow.push(tr);
          eyeOn(k, tr); gx.ev(ctx, "row", tr);
          cells[k].forEach((c, i) => {
            const at = tr + i * f(4);
            ft(tl, c.d, { opacity: 0, y: S(16) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, at);
            c.anim.forEach((a, j) => {
              const ta = at + f(3) + j * f(2);
              if (a.kind === "grow_x") ft(tl, a.el, { scaleX: 0 }, { scaleX: 1, duration: f(12), ease: E.move }, ta);
              else if (a.kind === "grow_y") ft(tl, a.el, { scaleY: 0 }, { scaleY: 1, duration: f(9), ease: E.enter }, ta);
              else ft(tl, a.el, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(7), ease: E.pop }, ta);
            });
          });
          tPrev = tr + f(10);
        });
        // la última columna (el siguiente cliente) late mientras se habla de su fila: el plano nunca se queda quieto
        rows.forEach((r, k) => {
          const c = cells[k][n - 1], until = k + 1 < rows.length ? tRow[k + 1] : t1 - 0.4;
          for (let tb = tRow[k] + 0.7; tb < until - 0.4; tb += 1.2) {
            ft(tl, c.d, { scale: 1 }, { scale: 1.045, duration: f(6), ease: E.enter }, tb);
            ft(tl, c.d, { scale: 1.045 }, { scale: 1, duration: f(9), ease: E.move }, tb + f(6));
          }
        });
        const tB = C("best", null);
        if (tB != null) {
          const rings = allCells.filter((c) => c.ring).map((c) => c.ring);
          rings.forEach((rg, k) => ft(tl, rg, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: f(8), ease: E.enter }, tB + k * f(2)));
          gx.ev(ctx, "best", tB);
        }
      }
    }
    return { animate };
  }

  // ── adapt: lo que se adapta, cada pieza en su palabra, sobre la base; la base es «La Misma Base» (lo que acaba de
  //    decir) hasta que nombra la estructura principal: entonces se vuelve el bloque de tinta con candado
  function mountAdapt(wrap, A, props, ctx) {
    const items = (props.items || []).slice(0, 6);
    const n = items.length, cols = 2, rowsN = Math.max(1, Math.ceil(n / cols));
    const kickH = props.kicker ? 40 : 0, kickGap = props.kicker ? 26 : 0, pillH = 88, gap = 16, baseGap = 40, baseH = 236;
    const need = kickH + kickGap + rowsN * pillH + (rowsN - 1) * gap + baseGap + baseH;
    const s = Math.max(0.72, Math.min(1.15, A.w / 950, (A.h * 0.96) / need));
    A.node.style.setProperty("--s", s);
    const S = (v) => R(v * s);
    const W = Math.min(A.w, S(900)), x0 = R((A.w - W) / 2);
    const y0 = R(Math.max(0, (A.h - S(need)) / 2));
    const kick = props.kicker ? gx.el("div", "pj-kick", wrap, props.kicker) : null;
    if (kick) Object.assign(kick.style, { left: "0px", width: A.w + "px", top: y0 + "px", height: S(kickH) + "px" });
    const pw = R((W - S(gap)) / 2), yP = y0 + S(kickH + kickGap);
    const pills = items.map((it, k) => {
      const r = Math.floor(k / cols), c = k % cols;
      const span = k === n - 1 && n % cols === 1;
      const x = span ? x0 : x0 + c * (pw + S(gap)), w = span ? W : pw, y = yP + r * S(pillH + gap);
      const p = gx.el("div", "pj-pill" + (span ? " pj-span" : ""), wrap);
      Object.assign(p.style, { left: x + "px", top: y + "px", width: w + "px", height: S(pillH) + "px" });
      const knob = gx.el("i", "pj-knob", gx.el("div", "pj-track", p));
      const tx = gx.el("div", "pj-ptx", p, it.label || "");
      const ring = gx.el("div", "pj-ring", p);
      return { p, knob, tx, ring, w };
    });
    const yB = yP + rowsN * S(pillH) + (rowsN - 1) * S(gap) + S(baseGap);
    const box = (cls) => { const b = gx.el("div", cls, wrap); Object.assign(b.style, { left: x0 + "px", top: yB + "px", width: W + "px", height: S(baseH) + "px" }); return b; };
    const ghost = box("pj-bghost");
    const glabel = gx.el("div", "pj-glabel", ghost, props.base_ghost || "La Misma Base");
    const base = box("pj-base");
    const brow = gx.el("div", "pj-brow", base);
    const lock = gx.el("div", "pj-lock", brow);
    gx.el("i", "pj-lock-arc", lock); gx.el("i", "pj-lock-body", lock);
    const bl = gx.el("div", "pj-blabel", brow, props.base_label || "Estructura Principal");
    // esqueleto: las tres filas de la tabla, ya iguales (herramientas, procesos, entrega)
    const sk = gx.el("div", "pj-skel", base);
    const skw = S(220), skh = S(78), u = s * 0.62;
    [drawTools, drawProcess, drawDelivery].forEach((fn) => {
      const g = sv("g", {}, sv("svg", { width: skw, height: skh, viewBox: `0 0 ${skw} ${skh}`, class: "pj-svg-in" }, sk));
      fn(g, skw, skh, u, 0);
    });
    const bring = gx.el("div", "pj-bring", base);
    const stamp = props.stamp ? gx.el("div", "pj-stamp", wrap, props.stamp) : null;
    // el sello cae DENTRO del bloque, donde está el esqueleto (que se atenúa): no tapa el rótulo ni sale del panel
    if (stamp) Object.assign(stamp.style, { left: R(x0 + W / 2 - S(260)) + "px", top: R(yB + S(116)) + "px", width: S(520) + "px", height: S(92) + "px" });
    gsap.set([base, bring, kick, stamp, ghost].filter(Boolean).concat(pills.map((p) => p.p), pills.map((p) => p.ring)), { opacity: 0 });

    function animate(tl, tS, t1, cues, E) {
      const C = (k, d) => gx.cue(cues, k, d);
      if (kick) gx.fit(kick, { max: Math.max(30, S(32)), min: 30, width: A.w, lines: 1 });
      const sz = pills.length ? Math.min(...pills.map((p) => gx.fit(p.tx, { max: S(46), min: 30, width: p.w - S(150), lines: 1 }))) : 0;
      pills.forEach((p) => { p.tx.style.fontSize = sz + "px"; });
      gx.fit(bl, { max: S(62), min: 40, width: W - S(140), lines: 1 });
      gx.fit(glabel, { max: S(54), min: 36, width: W - S(80), lines: 1 });
      if (stamp) gx.fit(stamp, { max: S(64), min: 40, width: S(520), lines: 1 });
      gx.cutIn(tl, ghost, tS);
      if (kick) ft(tl, kick, { opacity: 0, y: S(12) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, Math.max(tS, C("kick", tS + f(2))));
      let prev = null, tPrev = tS + f(6);
      pills.forEach((p, k) => {
        const ti = Math.max(tPrev, C("i" + k, tS + 0.6 + k * 0.7));
        ft(tl, p.p, { opacity: 0, scale: 0.92, y: S(12) }, { opacity: 1, scale: 1, y: 0, duration: f(8), ease: E.enter }, ti);
        ft(tl, p.knob, { x: 0 }, { x: S(44), duration: f(10), ease: E.move }, ti + f(4));
        ft(tl, p.ring, { opacity: 0 }, { opacity: 1, duration: f(5), ease: E.enter }, ti);
        if (prev) ft(tl, prev.ring, { opacity: 1 }, { opacity: 0, duration: f(8), ease: E.enter }, ti);
        gx.ev(ctx, "item", ti);
        prev = p; tPrev = ti + f(5);
      });
      if (prev) ft(tl, prev.ring, { opacity: 1 }, { opacity: 0, duration: f(8), ease: E.enter }, tPrev + 0.6);
      // «y este tipo de cosas»: todos los interruptores se conmutan en ola (se ve que todo eso se ajusta)
      const tT = C("toggle", null);
      if (tT != null) {
        pills.forEach((p, k) => {
          ft(tl, p.knob, { x: S(44) }, { x: 0, duration: f(7), ease: E.move }, tT + k * f(3));
          ft(tl, p.knob, { x: 0 }, { x: S(44), duration: f(8), ease: E.move }, tT + k * f(3) + f(9));
        });
        gx.ev(ctx, "toggle", tT);
      }
      const tB = Math.max(tPrev + f(4), C("base", tPrev + 0.8));
      const tD = Math.min(tB, C("dim", tB));
      ft(tl, pills.map((p) => p.p), { opacity: 1 }, { opacity: 0.72, duration: f(8), ease: E.enter }, tD);
      ft(tl, base, { opacity: 0, scale: 0.97 }, { opacity: 1, scale: 1, duration: f(8), ease: E.enter }, tB);
      ft(tl, ghost, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.enter }, tB + f(2));
      ft(tl, bring, { opacity: 0, scale: 1.05 }, { opacity: 1, scale: 1, duration: f(9), ease: E.enter }, tB + f(4));
      ft(tl, lock, { scale: 0.6, rotation: -10 }, { scale: 1, rotation: 0, duration: f(8), ease: E.pop }, tB + f(3));
      gx.ev(ctx, "base", tB);
      if (stamp) {
        const tM = Math.max(tB + f(8), C("same", tB + 1.2));
        ft(tl, sk, { opacity: 1 }, { opacity: 0.12, duration: f(4), ease: E.enter }, tM);
        ft(tl, stamp, { opacity: 0, scale: 1.35, rotation: -9 }, { opacity: 1, scale: 1, rotation: -3, duration: f(4), ease: E.enter }, tM);
        gx.ev(ctx, "stamp", tM);
      }
    }
    return { animate };
  }

  CK.register("viz.projects", {
    mount(root, props, ctx) {
      const mode = props.mode || "chaos";
      const st = gx.stage(root, ctx, props, "pj pj-" + mode);
      const A = gx.upper(st.A), bd = st.bd;
      const wrap = gx.el("div", "pj-wrap", A.node);
      const api = mode === "adapt" ? mountAdapt(wrap, A, props, ctx) : mountTable(wrap, A, props, ctx, mode);
      return {
        animate(tl, t0, t1, cues) {
          const E = gx.eases(ctx);
          const tS = gx.settle(ctx, t0);
          gx.ev(ctx, "enter", tS);
          api.animate(tl, tS, t1, cues, E);
          gx.bgIn(tl, bd, t0, t1, 47, props);
          gx.out(tl, props, t1, [wrap], { dur: f(5), ctx });
        },
      };
    },
  });
})(window.CK);
