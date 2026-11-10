// viz.token_stream — un LLM genera token a token (diagrama que se construye en un solo plano).
//
// phase "intro": la instrucción se teclea (cue prompt) → la respuesta sale token a token (generate) → en «tokens»
//                se encienden los resaltados alternos y se ve dónde empieza y acaba cada token.
// phase "loop":  el contexto se «lee» (context) → candidatos al siguiente token (compute) → se elige (next) → viaja y
//                se acopla (append) → vueltas cada vez más rápidas (repeat) → fase rápida (loop) → se para (final).
// phase "full":  intro + loop en UN item: prompt tecleado → primeros tokens en «tokens» → sigue el bucle sin reiniciar.
// Callbacks y continuidad: prewritten (prompt ya escrito), burst (todos los tokens en ≤1,2 s), from_tokens: N (el
// prompt y los N primeros tokens ya están: el segundo item continúa el diagrama del primero sin reiniciar).
//
// props: {phase, prompt, tokens:["Hola"," Marta",…], candidates?: [[…]|null,…] (alineadas con tokens; el elegido
//         debe estar en su lista), probs?: [[…]] (SOLO reales; si no, barras de esquema sin cifra), show_pct?,
//         candidates_label?: "Candidatos, esquema", intro_tokens?, prewritten?, burst?, from_tokens?, compact?,
//         canvas?: paper|white|ink|accent|none, exit?: "cut", style?: text|chips, prompt_label?}
// Un token con espacio inicial (" Marta") va separado; sin espacio ("irnos") se pega al anterior.
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
  const SCHEME = [0.74, 0.17, 0.07, 0.03]; // pesos de ESQUEMA (sin cifra en pantalla)


  // ── style "chips" (styleframe 03): instrucción en píldora (con `prompt_label` encima), respuesta en FICHAS (una por
  // token) centradas por fila que crecen desde un HUECO discontinuo con cursor; la última ficha en oro. Candidatos en
  // fichas pequeñas con barras de esquema; el ganador pasa a oro y VUELA en arco a su hueco (9 f, estela). El bucle
  // acelera de verdad (0,45 → 0,12 s por token) y para en seco en «final». El diagrama va anclado ARRIBA de la banda y
  // con medidas que solo dependen del ancho: el item de continuación (from_tokens) queda en el mismo sitio tras el corte.
  function parseToks(props) {
    const toks = (props.tokens || []).slice(0, 48).map((t) => (typeof t === "string" ? { text: t } : t || { text: "" }));
    const candL = props.candidates || [], probL = props.probs || [];
    toks.forEach((t, i) => {
      let c = t.candidates || candL[i];
      if (!Array.isArray(c) || !c.length) { t.cands = null; return; }
      c = c.slice(0, 4).map((x, k) => (typeof x === "string" ? { text: x, p: probL[i] ? probL[i][k] : null } : x));
      const word = String(t.text).trim();
      if (!c.some((x) => String(x.text).trim() === word)) { console.warn("[viz.token_stream] candidatos sin el token elegido:", word); t.cands = null; return; }
      t.cands = c;
    });
    return toks;
  }
  function mountChips(root, props, ctx) {
    const E = gx.eases(ctx);
    const phase = ["intro", "loop", "full"].indexOf(props.phase) >= 0 ? props.phase : "loop";
    const pre = Math.max(0, props.from_tokens | 0);
    const typed = !(props.prewritten || pre > 0 || phase === "loop");
    const st = gx.stage(root, ctx, props, "ts tc tc-" + phase);
    const A = gx.upper(st.A), bd = st.bd; // filas de fichas a 950 px: en pantalla completa, banda alta
    let s = Math.max(0.7, Math.min(1.05, A.w / 950));
    A.node.style.setProperty("--s", s);
    if (A.h < 700) A.node.classList.add("tc-split"); // panel de split: fichas ≥56 px, márgenes compactos
    if (A.h < 520) A.node.classList.add("tc-tight"); // panel bajo: sin rótulo «instrucción» (decide el alto, no el contenido:
                                                     // dos items seguidos del mismo diagrama quedan iguales)
    const cam = gx.el("div", "tc-cam", A.node); // encuadre: centra el diagrama y sube cuando entran los candidatos
    const wrap = gx.el("div", "tc-wrap", cam);
    const toks = parseToks(props);
    const N = toks.length;
    // maqueta de la frase FINAL (huecos fijos): layout_tokens permite que el intro use la frase completa de la continuación
    const LT = (Array.isArray(props.layout_tokens) && props.layout_tokens.length >= N ? props.layout_tokens : toks.map((t) => t.text)).map((t) => String(typeof t === "string" ? t : (t && t.text) || ""));
    const NL = LT.length;
    // instrucción
    const head = gx.el("div", "tc-top", wrap);
    const plab = props.prompt_label ? gx.el("div", "tc-lab", head, String(props.prompt_label)) : null;
    const pill = gx.el("div", "tc-pill", head);
    const ptxt = gx.el("div", "tc-ptxt", pill);
    const pparts = gx.split(ptxt, String(props.prompt || ""), typed ? "chars" : "words");
    const pcaret = gx.el("div", "tc-pcaret", pill);
    // respuesta en fichas (posición = capa exterior; entrada = capa interior)
    const out = gx.el("div", "tc-out", wrap);
    const ch = LT.map((raw) => {
      const txt = String(raw == null ? "" : raw).trim();
      const o = gx.el("div", "tc-pos", out);
      const c = gx.el("div", "tc-chip" + (gx.isPunct(txt) ? " tc-p" : ""), o, txt);
      return { o, c };
    });
    const slotO = gx.el("div", "tc-pos tc-slotpos", out); // detrás de las fichas: la ficha nace tapando el hueco
    const slot = gx.el("div", "tc-slot", slotO);
    const caret = gx.el("div", "tc-caret", slot);
    // candidatos (solo las vueltas lentas)
    const slow = phase !== "intro" ? toks.map((t, i) => ({ t, i })).filter((o) => o.i >= pre && o.t.cands) : [];
    const panel = gx.el("div", "tc-panel", wrap);
    if (!slow.length) panel.style.display = "none";
    if (props.candidates_label) gx.el("div", "tc-head", panel, String(props.candidates_label));
    const rowsBox = gx.el("div", "tc-rows", panel);
    const nRows = Math.min(4, Math.max(1, ...slow.map((o) => o.t.cands.length)));
    rowsBox.style.height = `calc(${nRows} * var(--crow) + ${nRows - 1} * var(--cgap))`;
    const cycles = slow.map(({ t, i }) => {
      const g = gx.el("div", "tc-group", rowsBox);
      const real = t.cands.every((c) => typeof c.p === "number" && isFinite(c.p));
      const SCH = [1, 0.46, 0.22, 0.1]; // esquema del styleframe (rotulado «esquema»: solo dice más/menos probable)
      const cands = t.cands.map((c, k) => ({ text: String(c.text).trim(), p: real ? Math.max(0, Math.min(1, c.p)) : SCH[k] }));
      const win = cands.findIndex((c) => c.text === String(t.text).trim());
      if (!real && win !== 0) { const w = cands[win].p; cands[win].p = cands[0].p; cands[0].p = w; }
      const rows = cands.map((c) => {
        const r = gx.el("div", "tc-row", g);
        const chip = gx.el("div", "tc-cchip", r, c.text);
        const track = gx.el("div", "tc-track", r);
        const fill = gx.el("div", "tc-fill", track);
        return { r, chip, fill, p: c.p };
      });
      return { g, rows, win, idx: i };
    });
    const flyer = gx.el("div", "tc-chip tc-flyer", cam);

    gsap.set([flyer, pcaret, ...cycles.map((c) => c.g)], { opacity: 0 });
    if (slow.length) gsap.set(panel, { opacity: 0 });
    if (typed) gsap.set(pparts, { opacity: 0 });
    if (pre === 0) gsap.set([head, slotO], { opacity: 0 });
    ch.forEach((x, i) => { if (i >= pre) gsap.set(x.c, { opacity: 0 }); });
    cycles.forEach((c) => c.rows.forEach((r) => gsap.set(r.fill, { scaleX: 0 })));

    return {
      animate(tl, t0, t1, cues) {
        const GOLD = "#FECA1A", INK = "#0B0B0C", WHITE = gx.cssv(A.node, "--g-card") || "#FFFFFF", CFG = gx.cssv(A.node, "--g-card-fg") || "#161514";
        // ── medidas (solo dependen del ancho) y maquetación de fichas: filas centradas en el eje
        let cw, chH, sw, GX, GY;
        const split = A.h < 700;
        const WMAX = split ? A.w - 12 : A.w * 0.97; // en split, casi todo el ancho útil (margen para el pop de las fichas)
        const measure = () => { cw = ch.map((x) => x.c.offsetWidth); chH = ch.length ? ch[0].c.offsetHeight : R(70 * s); sw = slot.offsetWidth; GX = R((split ? 10 : 12) * s); GY = R((split ? 10 : 12) * s); };
        const layout = (k, withSlot) => { // posiciones de las fichas 0..k-1 (sin hueco: la frase final ya los reserva)
          const ws = cw.slice(0, k); if (withSlot === true) ws.push(sw);
          const rows = []; let row = [], rw = 0;
          ws.forEach((w, i) => { if (row.length && rw + GX + w > WMAX) { rows.push({ row, rw }); row = []; rw = 0; } rw += (row.length ? GX : 0) + w; row.push(i); });
          if (row.length) rows.push({ row, rw });
          const P = [];
          rows.forEach((r, ri) => { let x = (A.w - r.rw) / 2; r.row.forEach((i) => { P[i] = { x: R(x), y: R(ri * (chH + GY)) }; x += ws[i] + GX; }); });
          return { P, n: rows.length };
        };
        // alto reservado: con panel de candidatos, solo las filas que existen mientras el panel vive (el panel va justo
        // debajo de la frase, como en el styleframe); la frase sigue creciendo hacia abajo cuando el panel ya se ha ido
        const lastSlow = slow.length ? Math.max(...slow.map((o) => o.i)) + 1 : N;
        const rowsH = (n) => R(n * chH + (n - 1) * GY);
        // si no cabe en la banda (frase muy larga), todo se escala; las medidas solo dependen del ancho, así que dos items
        // seguidos del mismo diagrama comparten escala mientras ambos quepan
        let hStart = 0, hPanel = 0, hFinal = 0, PF = [], rowY = [];
        const rowsUpTo = (i) => { const y = PF[Math.max(0, Math.min(NL - 1, i))].y; return rowY.indexOf(y) + 1; }; // filas hasta la ficha/hueco i
        for (let k = 0; k < 7; k++) {
          measure();
          PF = layout(NL).P; rowY = [...new Set(PF.map((p) => p.y))].sort((a, b) => a - b);
          out.style.height = rowsH(rowsUpTo(Math.min(lastSlow, NL - 1))) + "px";
          hPanel = slow.length ? panel.offsetTop + panel.offsetHeight : out.offsetTop + out.offsetHeight;
          hFinal = out.offsetTop + rowsH(rowsUpTo(N < NL ? N : N - 1));
          hStart = out.offsetTop + rowsH(rowsUpTo(phase === "intro" ? (N < NL ? N : N - 1) : Math.min(pre, NL - 1)));
          if (Math.max(hPanel, hFinal) <= A.h * 0.98 || s <= 0.72) break;
          s = Math.max(0.72, s * 0.94); A.node.style.setProperty("--s", s);
        }
        // encuadre: el estado de partida centrado en la banda (el final del intro = el inicio de la continuación, así el
        // corte entre los dos items no mueve nada); al entrar los candidatos el plano sube lo justo para centrar todo
        const Y0 = R(Math.max(0, (A.h - hStart) / 2)), Y1 = slow.length ? R(Math.max(0, Math.min(Y0, (A.h - hPanel) / 2))) : Y0;
        const outR = gx.rel(out, cam), outH0 = out.offsetHeight;
        // posiciones FIJAS: cada ficha en su hueco de la frase final; el hueco discontinuo marca el siguiente
        ch.forEach((x, i) => { gsap.set(x.o, PF[i]); if (i >= N) x.o.style.display = "none"; });
        const slotAt = (i) => (i < NL ? { x: PF[i].x, y: PF[i].y, w: cw[i] } : null);
        const s0p = slotAt(Math.min(pre, NL)); if (s0p) { gsap.set(slotO, { x: s0p.x, y: s0p.y }); gsap.set(slot, { width: s0p.w, height: chH }); } else gsap.set(slotO, { opacity: 0 });
        if (pre > 0 && pre <= N) gsap.set(ch[pre - 1].c, { backgroundColor: GOLD, color: INK });
        cycles.forEach((c) => { const w = Math.max(...c.rows.map((r) => r.chip.offsetWidth)); c.rows.forEach((r) => (r.chip.style.width = w + "px")); }); // barras alineadas
        const cr = cycles.map((c) => gx.rel(c.rows[c.win].chip, cam));
        gsap.set(cam, { y: Y0 });

        const ex = f(5), tEnd = props.exit === "cut" ? t1 - f(1) : t1 - ex - f(1);
        const tS = gx.settle(ctx, t0);
        gx.ev(ctx, "enter", tS);
        // kit v14: la etiqueta de la instrucción también ENTRA (antes se veía ya puesta en el corte)
        if (pre === 0) { tl.set([head, slotO], { opacity: 1 }, T(tS)); gx.cutIn(tl, pill, tS); if (plab) gx.textIn(tl, plab, tS); }
        else if (tS - t0 > 0.02) { tl.set(cam, { opacity: 0 }, T(t0)); gx.cutIn(tl, cam, tS); } // vuelve tras un corte: no viaja con el panel que entra
        const C = (k, d) => gx.cue(cues, k, d);

        // ── instrucción tecleada
        let tReady = tS + f(4);
        if (typed) {
          const pc = pparts.map((c) => gx.rel(c, pill));
          const tP = Math.max(tS + f(3), C("prompt", tS + f(6)));
          const cps = Math.min(40, Math.max(24, pparts.length / 1.0));
          if (pc.length) tl.set(pcaret, { opacity: 1, x: R(pc[0].x - 6), y: R(pc[0].y) }, T(tP - f(2)));
          pparts.forEach((c, k) => { const at = tP + k / cps; tl.set(c, { opacity: 1 }, T(at)); tl.set(pcaret, { x: R(pc[k].x + pc[k].w + 2), y: R(pc[k].y) }, T(at)); });
          tReady = tP + pparts.length / cps;
          tl.to(pcaret, { opacity: 0, duration: f(3), ease: E.exit }, tReady + f(5));
        }

        // ── calendario: landT[i] para cada token que llega en este item; fly[i] si llega volando desde un candidato
        const landT = [], fly = {};
        let tPanelOut = null, tStopAll = null;
        if (phase === "intro") {
          const tG = Math.max(tReady + f(3), C("generate", C("tokens", tReady + f(8))));
          const n = N - pre, room = props.burst ? Math.min(1.2, Math.max(0.3, tEnd - 0.5 - tG)) : Math.max(0.5, tEnd - 0.8 - tG);
          const step = n > 0 ? Math.max(f(2), Math.min(props.burst ? 0.12 : 0.24, room / n)) : 0;
          for (let i = pre; i < N; i++) landT[i] = tG + (i - pre) * step;
          const tK = C("tokens", null), lastL = landT[N - 1] || tG;
          if (tK != null && tK > lastL + f(4)) ch.forEach((x, i) => { // «token a token»: una ola recorre las fichas
            ft(tl, x.c, { scale: 1 }, { scale: 1.06, duration: f(3), ease: E.move }, tK + i * f(1));
            ft(tl, x.c, { scale: 1.06 }, { scale: 1, duration: f(4), ease: E.move }, tK + i * f(1) + f(3));
          });
        } else {
          // «leen el contexto»: la píldora late una vez (1 → 1,04 → 1, 8 f)
          const tCtx = C("context", null);
          if (tCtx != null && tCtx > tS + f(4)) { ft(tl, pill, { scale: 1 }, { scale: 1.04, duration: f(3), ease: E.move }, tCtx); ft(tl, pill, { scale: 1.04 }, { scale: 1, duration: f(5), ease: E.move }, tCtx + f(3)); }
          let iStart = pre, tNext = Math.max(tReady, tCtx != null ? tCtx + f(8) : tReady);
          if (phase === "full") {
            const firstSlow = slow.length ? slow[0].i : N;
            const nIntro = props.intro_tokens != null ? Math.max(0, props.intro_tokens | 0) : Math.max(1, firstSlow - pre);
            const tG = Math.max(tReady + f(3), C("tokens", C("generate", tReady + f(8))));
            for (let k = 0; k < nIntro && pre + k < N; k++) landT[pre + k] = tG + k * 0.2;
            iStart = pre + nIntro; tNext = Math.max(tNext, tG + nIntro * 0.2);
          }
          const cyc = cycles.filter((c) => c.idx >= iStart);
          cycles.filter((c) => c.idx < iStart).forEach((c) => gsap.set(c.g, { display: "none" }));
          const n = cyc.length;
          const tC = Math.max(tNext + f(3), C("compute", tNext + f(6)));
          const tPick0 = C("next", null), tAdd0 = Math.max(tC + 0.9, C("append", tC + 1.7));
          let t = Math.max(tAdd0 + f(8), C("repeat", tAdd0 + f(10)));
          const tFastCue = C("loop", null);
          let d = n > 1 && tFastCue != null ? Math.max(0.55, Math.min(1.2, (tFastCue - t) / (1 + 0.72 * (n - 2) || 1))) : 1.0;
          cyc.forEach((c, k) => {
            const a = k === 0 ? tC : t, ld = k === 0 ? tAdd0 : t + d * 0.86;
            const pick = k === 0 && tPick0 != null && tPick0 > tC + 0.4 && tPick0 < tAdd0 - f(10) ? tPick0 : a + (ld - a) * 0.5;
            fly[c.idx] = { a, pick, ld, c, ci: cycles.indexOf(c) };
            landT[c.idx] = ld;
            if (k > 0) { t += d; d = Math.max(0.45, d * 0.72); }
          });
          // fase rápida: intervalos 0,45 → 0,12 s (geométrica) que terminan en «final» (parada en seco)
          const fastIdx = []; for (let i = iStart; i < N; i++) if (landT[i] == null) fastIdx.push(i);
          const lastSlow = n ? Math.max(...cyc.map((c) => fly[c.idx].ld)) : tNext;
          const tStop = Math.min(tEnd - 0.5, C("final", tEnd - 0.6));
          const tF0 = Math.max(lastSlow + f(6), tFastCue != null ? tFastCue : lastSlow + f(8));
          if (fastIdx.length) {
            const m = fastIdx.length, r = m > 2 ? Math.pow(0.12 / 0.45, 1 / (m - 2)) : 1;
            const iv = []; for (let j = 0; j < m - 1; j++) iv.push(0.45 * Math.pow(r, j));
            const sum = iv.reduce((a, b) => a + b, 0), avail = Math.max(f(2) * (m - 1), tStop - tF0);
            const k = sum > 0 ? Math.max(0.5, Math.min(1.3, avail / sum)) : 1;
            let u = Math.max(tF0, tStop - sum * k);
            fastIdx.forEach((i, j) => { landT[i] = u; if (j < m - 1) u += Math.max(f(2), iv[j] * k); });
            tStopAll = landT[fastIdx[m - 1]];
          } else tStopAll = lastSlow;
          if (slow.length) tPanelOut = Math.max(lastSlow + f(4), (fastIdx.length ? landT[fastIdx[0]] : tStopAll) - f(5));
        }

        // ── vueltas lentas: candidatos, barras de esquema, elección en oro y vuelo en arco
        if (slow.length) {
          const tP0 = Math.min(...Object.values(fly).map((o) => o.a));
          if (Y1 !== Y0) ft(tl, cam, { y: Y0 }, { y: Y1, duration: f(10), ease: E.move }, tP0 - f(4));
          ft(tl, panel, { opacity: 0, y: R(12 * s) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, tP0);
        }
        const flyTexts = [""], flyTimes = [];
        Object.values(fly).forEach((o) => {
          const { a, pick, ld, c, ci } = o, win = c.rows[c.win];
          tl.set(c.g, { opacity: 1 }, T(a));
          c.rows.forEach((row, j) => ft(tl, row.r, { opacity: 0, y: R(8 * s) }, { opacity: 1, y: 0, duration: f(6), ease: E.enter }, a + j * f(3)));
          c.rows.forEach((row, j) => ft(tl, row.fill, { scaleX: 0 }, { scaleX: Math.max(0.04, row.p), duration: f(12), ease: E.enter }, a + f(4) + j * f(2)));
          gx.ev(ctx, "choose", pick);
          ft(tl, win.chip, { backgroundColor: WHITE, color: CFG }, { backgroundColor: GOLD, color: INK, duration: f(3), ease: E.enter }, pick);
          ft(tl, win.fill, { backgroundColor: gx.cssv(A.node, "--g-bar-dim") || "rgba(22,21,20,.13)" }, { backgroundColor: GOLD, duration: f(3), ease: E.enter }, pick);
          const tFly = Math.max(pick + f(4), ld - f(9)), dur = ld - tFly;
          c.rows.forEach((row, j) => { if (j !== c.win) tl.to(row.r, { opacity: 0, duration: f(4), ease: E.exit }, tFly); });
          tl.set(win.chip, { opacity: 0 }, T(tFly));
          const P = PF[c.idx], to = { x: outR.x + P.x, y: outR.y + P.y, w: cw[c.idx], h: chH }, fr = cr[ci];
          const k0 = Math.max(0.5, Math.min(1, fr.h / chH));
          const fx = R(fr.x + fr.w / 2 - to.w / 2), fy = R(fr.y + fr.h / 2 - chH / 2);
          tl.set(flyer, { opacity: 1 }, T(tFly));
          ft(tl, flyer, { x: fx, scale: k0 }, { x: R(to.x), scale: 1, duration: dur, ease: E.enter }, tFly);
          ft(tl, flyer, { y: fy }, { y: R(to.y), duration: dur, ease: E.move }, tFly); // x adelantada a y → arco que entra al hueco desde abajo
          if (Math.hypot(to.x - fx, to.y - fy) / (dur * gx.FPS) > 30) gx.streak(tl, flyer, tFly + f(1), Math.max(f(3), dur - f(2)), Math.abs(to.x - fx) > Math.abs(to.y - fy) ? "x" : "y", 10);
          tl.set(flyer, { opacity: 0 }, T(ld));
          tl.to(c.g, { opacity: 0, duration: f(4), ease: E.exit }, ld + f(4));
          flyTexts.push(ch[c.idx].c.textContent); flyTimes.push(tFly - f(1));
        });
        if (flyTimes.length) gx.swapText(tl, flyer, flyTexts, flyTimes);
        if (tPanelOut != null) {
          tl.to(panel, { opacity: 0, y: R(8 * s), duration: f(5), ease: E.exit }, tPanelOut);
          // sin candidatos, el plano vuelve a centrar la frase (que sigue creciendo hacia abajo)
          const Yf = R(Math.max(0, Math.min(Y0, (A.h - hFinal) / 2)));
          if (Math.abs(Yf - Y1) > 12) ft(tl, cam, { y: Y1 }, { y: Yf, duration: f(12), ease: E.move }, tPanelOut + f(2));
        }

        // ── aterrizajes: la ficha nace del hueco (2 f de anticipación + 4 f de deslizamiento), pasa a ser la de oro,
        //    la anterior vuelve a blanco y la fila se recentra (el hueco se desplaza)
        const order = []; for (let i = pre; i < N; i++) if (landT[i] != null) order.push(i);
        order.sort((a, b) => landT[a] - landT[b] || a - b);
        let lastLand = tS;
        // aterrizaje EN SU HUECO: la ficha aparece en su sitio (opacidad + pop corto); nada de lo ya leído se mueve.
        // El hueco discontinuo salta al siguiente, con el ancho de la ficha que viene. Con vuelo, el hueco espera al vuelo.
        order.forEach((i, j) => {
          const at = landT[i], s0 = fly[i] ? at : at - f(1), sN = j + 1 < order.length ? landT[order[j + 1]] - f(1) : Infinity;
          const dd = Math.max(f(1), Math.min(f(3), (sN - s0) * 0.9));
          if (fly[i]) tl.set(ch[i].c, { opacity: 1 }, T(at));
          else {
            ft(tl, ch[i].c, { opacity: 0 }, { opacity: 1, duration: Math.min(f(3), dd + f(1)), ease: E.enter }, s0);
            ft(tl, ch[i].c, { scale: 0.9 }, { scale: 1, duration: f(5), ease: E.pop }, s0);
          }
          tl.set(ch[i].c, { backgroundColor: GOLD, color: INK }, T(s0));
          if (i > 0) ft(tl, ch[i - 1].c, { backgroundColor: GOLD, color: INK }, { backgroundColor: WHITE, color: CFG, duration: Math.min(f(3), dd), ease: E.enter }, s0);
          const a0 = slotAt(i), a1 = slotAt(i + 1);
          const below = a1 && tPanelOut != null && s0 < tPanelOut + f(5) && a1.y >= outH0 - 2; // fila aún tapada por el panel
          if (a1 && below) { // el hueco espera a que se vaya el panel para aparecer en la fila de abajo
            const tb = tPanelOut + f(5);
            tl.to(slotO, { opacity: 0, duration: f(2), ease: E.exit }, s0);
            tl.set(slotO, { x: a1.x, y: a1.y }, T(tb)); tl.set(slot, { width: a1.w }, T(tb));
            tl.to(slotO, { opacity: 1, duration: f(3), ease: E.enter }, tb);
          } else if (a1) { ft(tl, slotO, { x: a0.x, y: a0.y }, { x: a1.x, y: a1.y, duration: dd, ease: E.move }, s0); ft(tl, slot, { width: a0.w }, { width: a1.w, duration: dd, ease: E.move }, s0); }
          else tl.to(slotO, { opacity: 0, duration: f(3), ease: E.exit }, s0);
          gx.ev(ctx, "token", at);
          lastLand = Math.max(lastLand, at);
        });
        // parada en seco (loop/full): el hueco ya se ha ido con la última ficha; si queda frase, el cursor parpadea
        if (!(phase !== "intro" && order.length && landT[N - 1] != null && N >= NL)) {
          for (let u = lastLand + 0.45, k = 0; u < tEnd - 0.1; u += 0.45, k++) tl.set(caret, { opacity: k % 2 ? 1 : 0 }, T(u));
        }
        void tStopAll;
        gx.bgIn(tl, bd, t0, t1, 11, props);
        gx.out(tl, props, t1, [wrap, flyer], { dur: ex, ctx });
      },
    };
  }

  CK.register("viz.token_stream", {
    mount(root, props, ctx) {
      if (props.style === "chips") return mountChips(root, props, ctx);
      const E = gx.eases(ctx);
      const phase = ["intro", "loop", "full"].indexOf(props.phase) >= 0 ? props.phase : "loop";
      const pre = Math.max(0, props.from_tokens | 0);
      const prewritten = !!props.prewritten || pre > 0 || phase === "loop";
      const burst = !!props.burst;
      const st = gx.stage(root, ctx, props, "ts ts-" + phase + (props.compact ? " ts-compact" : ""));
      const A = gx.upper(st.A), bd = st.bd;
      let s = Math.max(0.72, Math.min(1.12, A.w / 860)) * (props.compact ? 0.9 : 1);
      A.node.style.setProperty("--s", s);
      const wrap = gx.el("div", "ts-wrap", A.node);

      // tokens + candidatos (alineados por índice; una lista que no contiene su token se ignora: no se inventa)
      const toks = (props.tokens || []).slice(0, 48).map((t) => (typeof t === "string" ? { text: t } : t || { text: "" }));
      const candL = props.candidates || [], probL = props.probs || [];
      toks.forEach((t, i) => {
        let c = t.candidates || candL[i];
        if (!Array.isArray(c) || !c.length) { t.cands = null; return; }
        c = c.slice(0, 4).map((x, k) => (typeof x === "string" ? { text: x, p: probL[i] ? probL[i][k] : null } : x));
        const word = String(t.text).trim();
        if (!c.some((x) => String(x.text).trim() === word)) { console.warn("[viz.token_stream] candidatos sin el token elegido:", word); t.cands = null; return; }
        t.cands = c;
      });
      const usesLoop = phase !== "intro";

      // 1, Contexto / instrucción
      const ctxBox = gx.el("div", "ts-ctx", wrap);
      const bar = gx.el("div", "ts-bar", ctxBox);
      const ptxt = gx.el("div", "ts-prompt", bar);
      const typed = !prewritten && phase !== "loop";
      const pparts = gx.split(ptxt, String(props.prompt || ""), typed ? "chars" : "words");
      const pcaret = gx.el("div", "ts-pcaret", bar);
      const head = gx.el("div", "ts-readhead", bar);

      // 2, Respuesta: texto en línea; cada token es un span que se muestra al aterrizar (display), con su resaltado
      //     continuo (box-decoration-break) y el cursor en línea pegado al último token visible.
      const out = gx.el("div", "ts-out", wrap);
      const tk = toks.map((t, i) => {
        const txt = String(t.text == null ? "" : t.text);
        const sp = gx.el("span", "ts-tk", out);
        if (/^\s/.test(txt) && i > 0) sp.appendChild(document.createTextNode(" "));
        const w = gx.el("span", "ts-tw" + (gx.isPunct(txt) ? " ts-p" : ""), sp, txt.trim());
        return { sp, w, punct: gx.isPunct(txt), alt: i % 2 };
      });
      const caret = gx.el("span", "ts-caret", out);

      // 3, Panel de candidatos (vueltas lentas)
      const slow = usesLoop ? toks.map((t, i) => ({ t, i })).filter((o) => o.i >= pre && o.t.cands) : [];
      const panel = gx.el("div", "ts-panel", wrap);
      if (!slow.length) panel.style.display = "none";
      const head2 = props.candidates_label ? gx.el("div", "ts-head", panel, String(props.candidates_label)) : null; // sin cabecera si no se pide
      const rowsBox = gx.el("div", "ts-rows", panel);
      const nRows = Math.min(4, Math.max(1, ...slow.map((o) => o.t.cands.length)));
      rowsBox.style.height = `calc(${nRows} * var(--row) + ${nRows - 1} * var(--rowgap))`;
      const showPct = !!props.show_pct;
      const cycles = slow.map(({ t, i }) => {
        const g = gx.el("div", "ts-group", rowsBox);
        const real = t.cands.every((c) => typeof c.p === "number" && isFinite(c.p));
        const cands = t.cands.map((c, k) => ({ text: String(c.text).trim(), p: real ? Math.max(0, Math.min(1, c.p)) : SCHEME[k] }));
        let win = cands.findIndex((c) => c.text === String(t.text).trim());
        if (!real && win !== 0) { const w = cands[win].p; cands[win].p = cands[0].p; cands[0].p = w; } // el elegido, barra mayor
        const rows = cands.map((c) => {
          const r = gx.el("div", "ts-row", g);
          const chip = gx.el("div", "ts-chip", r, c.text);
          const track = gx.el("div", "ts-track", r);
          const fill = gx.el("div", "ts-fill", track);
          const pct = real && showPct ? gx.el("div", "ts-pct", r, Math.round(c.p * 100) + " %") : null;
          return { r, chip, fill, pct, p: c.p };
        });
        return { g, rows, win, idx: i };
      });
      const flyer = gx.el("div", "ts-chip ts-flyer", A.node);

      gsap.set([ctxBox, out, flyer, pcaret, head, ...cycles.map((c) => c.g)], { opacity: 0 });
      if (slow.length) gsap.set(panel, { opacity: 0 });
      if (typed) gsap.set(pparts, { opacity: 0 });
      else if (usesLoop && pre === 0) gsap.set(pparts, { opacity: 0.4 });
      cycles.forEach((c) => c.rows.forEach((r) => gsap.set(r.fill, { scaleX: 0 })));

      return {
        animate(tl, t0, t1, cues) {
          // ── ajuste: la respuesta completa cabe en ≤3 líneas; si el conjunto no cabe en alto, se escala todo
          const fitOut = () => { out.style.height = ""; gx.fit(out, { max: Math.round(78 * s), min: 52, width: out.clientWidth, lines: 3 }); out.style.height = out.offsetHeight + "px"; };
          fitOut(); // alto final fijo: el panel no se mueve mientras crece la respuesta
          s = gx.autoscale(A, wrap, s, fitOut, { fill: props.compact ? 0.8 : 0.9, max: 1.5, min: 0.6 });
          const fg = gx.cssv(A.node, "--g-fg"), INK = "#0F0D10";
          const tintA = "rgba(254,202,26,.42)", tintB = "rgba(254,202,26,.17)", tint0 = "rgba(254,202,26,0)";
          // ── MEDIR (fuentes cargadas, todo visible) y después ocultar lo que aún no ha llegado
          const M = (n) => gx.rel(n, A.node);
          const tr = tk.map((x) => M(x.w));
          const cr = cycles.map((c) => M(c.rows[c.win].chip));
          const pc = typed ? pparts.map((c) => gx.rel(c, bar)) : [];
          const prs = !typed ? pparts.map((w) => gx.rel(w, bar)) : [];
          tk.forEach((x, i) => { if (i >= pre) gsap.set(x.sp, { display: "none" }); else if (!x.punct) gsap.set(x.w, { backgroundColor: x.alt ? tintB : tintA }); });

          const ex = f(5), tEnd = props.exit === "cut" ? t1 - f(1) : t1 - ex - f(1);
          const tS = gx.settle(ctx, t0);
          gx.cutIn(tl, ctxBox, tS); // en el corte ya se ve la barra de contexto
          gx.ev(ctx, "enter", tS);
          tl.set(out, { opacity: 1 }, T(tS));
          if (slow.length) ft(tl, panel, { opacity: 0, y: R(16 * s) }, { opacity: 1, y: 0, duration: f(8), ease: E.enter }, tS + f(5));

          // aterrizaje de un token: se muestra (empuja el cursor), destello de oro y se asienta en su resaltado
          const land = (i, at, dim, tintNow) => {
            const x = tk[i];
            tl.set(x.sp, { display: "inline" }, T(at));
            if (x.punct) return;
            // kit v14: el token aparece con opacidad en 10 f (≈ power2.out en 8 f), no de golpe; el destello de oro sigue
            ft(tl, x.sp, { opacity: 0 }, { opacity: 1, duration: f(10), ease: E.enter }, at);
            if (tintNow === false) { ft(tl, x.w, { color: INK, backgroundColor: "rgba(254,202,26,1)" }, { color: fg, backgroundColor: tint0, duration: dim, ease: E.enter }, at); return; }
            ft(tl, x.w, { color: INK, backgroundColor: "rgba(254,202,26,1)" }, { color: fg, backgroundColor: x.alt ? tintB : tintA, duration: dim, ease: E.enter }, at);
          };
          let lastLand = t0 + 0.3;

          // ── instrucción
          let tReady = t0 + f(6);
          if (typed) {
            const tP = Math.max(t0 + f(4), gx.cue(cues, "prompt", t0 + f(8)));
            const cps = Math.min(34, Math.max(22, pparts.length / 1.3));
            if (pc.length) tl.set(pcaret, { opacity: 1, x: R(pc[0].x - 6), y: R(pc[0].y) }, T(tP - f(3)));
            pparts.forEach((c, k) => { const at = tP + k / cps; tl.set(c, { opacity: 1 }, T(at)); tl.set(pcaret, { x: R(pc[k].x + pc[k].w + 2), y: R(pc[k].y) }, T(at)); });
            tReady = tP + pparts.length / cps;
            tl.to(pcaret, { opacity: 0, duration: f(3), ease: E.exit }, tReady + f(5));
          }

          if (phase === "intro") {
            const tG = Math.max(tReady + f(3), gx.cue(cues, "generate", gx.cue(cues, "tokens", tReady + f(8))));
            const n = tk.length - pre;
            const room = burst ? Math.min(1.2, Math.max(0.3, tEnd - 0.5 - tG)) : Math.max(0.5, tEnd - 0.8 - tG);
            const step = n > 0 ? Math.max(f(2), Math.min(burst ? 0.12 : 0.24, room / n)) : 0;
            const tK = burst ? null : Math.max(tG + f(6), gx.cue(cues, "tokens", tG + n * step + f(6)));
            for (let i = pre; i < tk.length; i++) land(i, tG + (i - pre) * step, f(burst ? 5 : 4), burst ? true : false);
            if (tk.length > pre) gx.ev(ctx, "token", tG); // ráfaga agrupada
            lastLand = tG + Math.max(0, n - 1) * step;
            // «token a token»: se encienden los resaltados alternos (en cascada de 1 f)
            if (tK != null) tk.forEach((x, i) => { if (!x.punct && i >= pre) ft(tl, x.w, { backgroundColor: tint0 }, { backgroundColor: x.alt ? tintB : tintA, duration: f(6), ease: E.enter }, Math.max(tK + (i - pre) * f(1), tG + (i - pre) * step + f(6))); });
          } else {
            // ── lectura del contexto (cada palabra se ilumina y el cabezal la subraya)
            let tNext = tReady;
            if (!typed && prs.length && pre === 0) {
              const tRead = Math.max(t0 + f(6), gx.cue(cues, "context", t0 + f(10)));
              const readDur = Math.min(1.4, 0.15 * prs.length + 0.3), per = readDur / prs.length;
              const hb = (i) => ({ x: R(prs[i].x), y: R(prs[i].y + prs[i].h - 2), width: R(prs[i].w) });
              gsap.set(head, hb(0));
              ft(tl, head, { opacity: 0 }, { opacity: 1, duration: f(3), ease: E.enter }, tRead);
              pparts.forEach((w, i) => {
                const at = tRead + i * per;
                ft(tl, w, { opacity: 0.4 }, { opacity: 1, duration: f(4), ease: E.enter }, at);
                if (i > 0) ft(tl, head, hb(i - 1), Object.assign(hb(i), { duration: per * 0.85, ease: E.move }), at - per * 0.1);
              });
              tl.to(head, { opacity: 0, duration: f(4), ease: E.exit }, tRead + readDur + f(3));
              tNext = tRead + readDur;
            } else if (pre > 0) {
              // continuación: el contexto ya leído se marca de un barrido (sin volver a teclear)
              const tRead = gx.cue(cues, "context", t0 + f(6));
              if (prs.length) {
                const a = prs[0], b = prs[prs.length - 1];
                gsap.set(head, { x: R(a.x), y: R(a.y + a.h - 2), width: R(b.x + b.w - a.x), scaleX: 0, transformOrigin: "0 50%" });
                ft(tl, head, { opacity: 1, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: f(12), ease: E.move }, tRead);
                tl.to(head, { opacity: 0, duration: f(4), ease: E.exit }, tRead + f(16));
              }
              tNext = tRead + 0.5;
            }
            // primeros tokens en «full» (antes de las vueltas lentas)
            let iStart = pre;
            if (phase === "full") {
              const firstSlow = slow.length ? slow[0].i : tk.length;
              const nIntro = props.intro_tokens != null ? Math.max(0, props.intro_tokens | 0) : Math.max(1, firstSlow - pre);
              const tG = Math.max(tReady + f(3), gx.cue(cues, "tokens", gx.cue(cues, "generate", tReady + f(8))));
              for (let k = 0; k < nIntro && pre + k < tk.length; k++) land(pre + k, tG + k * 0.2, f(6));
              iStart = pre + nIntro;
              lastLand = tG + Math.max(0, nIntro - 1) * 0.2;
              tNext = Math.max(tNext, lastLand + f(6));
            }
            const cyc = cycles.filter((c) => c.idx >= iStart);
            cycles.filter((c) => c.idx < iStart).forEach((c) => gsap.set(c.g, { display: "none" }));
            // ── calendario de vueltas: la 1.ª anclada a compute/next/append; luego aceleran
            const n = cyc.length;
            const tC = Math.max(tNext + f(3), gx.cue(cues, "compute", tNext + f(6)));
            const tPick0 = gx.cue(cues, "next", null);
            const tAdd0 = Math.max(tC + 0.9, gx.cue(cues, "append", tC + 1.7));
            const starts = [], lands = [], picks = [];
            if (n) { starts.push(tC); lands.push(tAdd0); picks.push(tPick0 != null && tPick0 > tC + 0.4 && tPick0 < tAdd0 - f(4) ? tPick0 : null); }
            let t = Math.max(tAdd0 + f(6), gx.cue(cues, "repeat", tAdd0 + f(8)));
            const tFastCue = gx.cue(cues, "loop", null);
            let d = 1.0;
            if (n > 1 && tFastCue != null) d = Math.max(0.5, Math.min(1.2, ((tFastCue - t) * 0.28) / (1 - Math.pow(0.72, n - 1))));
            for (let k = 1; k < n; k++) { starts.push(t); lands.push(t + d * 0.86); picks.push(null); t += d; d = Math.max(0.4, d * 0.72); }
            const done = new Set(cyc.map((c) => c.idx));
            const fastIdx = []; for (let i = iStart; i < tk.length; i++) if (!done.has(i)) fastIdx.push(i);
            const tStop = Math.min(tEnd - 0.4, gx.cue(cues, "final", tEnd - 0.6));
            const tFast = Math.max(n ? t : tNext + f(4), tFastCue != null ? tFastCue : t);
            const step = fastIdx.length ? Math.max(f(2), Math.min(0.2, (tStop - tFast) / fastIdx.length)) : 0;

            cyc.forEach((c, k) => {
              const a = starts[k], ld = lands[k], span = ld - a;
              const win = c.rows[c.win];
              const ci = cycles.indexOf(c);
              tl.set(c.g, { opacity: 1 }, T(a));
              c.rows.forEach((row, j) => ft(tl, row.r, { opacity: 0, x: R(-14 * s) }, { opacity: 1, x: 0, duration: Math.min(f(7), span * 0.3), ease: E.enter }, a + j * Math.min(f(3), span * 0.08)));
              const tPick = picks[k] != null ? picks[k] : a + span * 0.58;
              const tBars = a + span * 0.14, barDur = Math.max(f(6), tPick - tBars - f(1));
              c.rows.forEach((row) => ft(tl, row.fill, { scaleX: 0 }, { scaleX: Math.max(0.03, row.p), duration: barDur, ease: E.enter }, tBars));
              ft(tl, win.chip, { backgroundColor: "rgba(254,202,26,0)", color: fg }, { backgroundColor: "rgba(254,202,26,1)", color: INK, duration: f(3), ease: E.enter }, tPick);
              ft(tl, win.fill, { backgroundColor: gx.cssv(A.node, "--g-bar") }, { backgroundColor: "rgba(254,202,26,1)", duration: f(3), ease: E.enter }, tPick);
              c.rows.forEach((row, j) => { if (j !== c.win) tl.to(row.r, { opacity: 0.28, duration: f(4), ease: E.enter }, tPick); });
              // vuelo al hueco del token en la respuesta
              const tFly = Math.max(tPick + f(3), ld - Math.min(f(11), span * 0.38));
              const from = cr[ci], to = tr[c.idx];
              const sc = Math.max(0.6, Math.min(1.6, to.h / Math.max(1, from.h)));
              tl.set(win.chip, { opacity: 0 }, T(tFly));
              ft(tl, flyer, { opacity: 1, x: R(from.x), y: R(from.y), scale: 1, width: R(from.w) },
                { x: R(to.x + (to.w - from.w) / 2), y: R(to.y + (to.h - from.h) / 2), scale: sc, duration: ld - tFly, ease: E.move }, tFly);
              tl.set(flyer, { opacity: 0 }, T(ld));
              land(c.idx, ld, Math.min(f(12), Math.max(f(5), span * 0.6)));
              gx.ev(ctx, "token", ld); gx.ev(ctx, "choose", tPick);
              const nextA = k + 1 < n ? starts[k + 1] : tFast;
              tl.to(c.g, { opacity: 0, duration: f(4), ease: E.exit }, Math.max(ld + f(2), nextA - f(5)));
            });
            if (cyc.length) gx.swapText(tl, flyer, ["", ...cyc.map((c) => c.rows[c.win].chip.textContent)], starts.map((a) => a + f(1)));
            if (slow.length) tl.to(panel, { opacity: 0, y: R(10 * s), duration: f(5), ease: E.exit }, Math.max(tFast - f(5), (lands[n - 1] || tFast) + f(2)));
            fastIdx.forEach((i, j) => land(i, tFast + j * step, f(6)));
            if (fastIdx.length) gx.ev(ctx, "token", tFast); // fase rápida: una ráfaga
            lastLand = Math.max(lastLand, ...lands, fastIdx.length ? tFast + (fastIdx.length - 1) * step : 0);
          }

          // el cursor: sólido mientras escribe; al parar, parpadea a saltos (finito) hasta la salida
          ft(tl, caret, { opacity: 0 }, { opacity: 1, duration: f(2), ease: E.enter }, t0 + f(4));
          for (let u = lastLand + 0.45, k = 0; u < tEnd - 0.1; u += 0.45, k++) tl.set(caret, { opacity: k % 2 ? 1 : 0 }, T(u));

          gx.bgIn(tl, bd, t0, t1, 11, props);
          gx.out(tl, props, t1, [wrap, flyer], { dur: ex , ctx });
        },
      };
    },
  });
})(window.CK);
