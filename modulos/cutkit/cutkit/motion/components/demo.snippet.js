// demo.snippet — mini-UI clara y GRANDE (no captura de escritorio): enseña la cosa real en vez de nombrarla.
//   chat  → 2–3 burbujas que entran por turnos (usuario a la derecha, IA a la izquierda)
//   email → cliente de correo: campos (Para, Asunto) y cuerpo que se escribe palabra a palabra
//   code  → editor con 3–14 líneas (se teclean, o prewritten); highlights [{lines:[a,b] (0-based, inclusivo), cue}]:
//           marcador oro sobre el rango en su cue, punch suave y el resto al 55 %; las líneas largas se parten dentro
//   json  → registro real con resaltado; punch-in y marcador sobre `focus_key` (el resto se atenúa)
// props: {kind, title?, lines?: [...], json?: {...}, focus_key?, canvas?: paper|white|ink|accent|none, exit?: "cut"}
// code: plain (sin colorear palabras clave), code_scale (0,9–1,35: ventana más grande), entry: "rise"
//   (con highlights, la ventana entra subiendo y fundiendo en 8 f en vez de «en el corte»)
//   chat:  lines [{role:"user"|"ai", text}], email: lines [{k,v}… , {text}], code: lines ["…", …]
// cues (opcionales): l0, l1… (cada burbuja/línea), focus (punch-in al campo), type (empieza a teclear)
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
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const KW = /\b(def|return|import|from|as|for|in|if|elif|else|while|class|with|await|async|const|let|var|function|new|try|except|raise|lambda|None|True|False|null|true|false)\b/g;

  function hlCode(line) {
    // comentarios y cadenas primero (no se resaltan sus palabras), luego palabras clave, números y llamadas
    const parts = [];
    const re = /(#.*$|\/\/.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g;
    let last = 0, m;
    while ((m = re.exec(line))) { parts.push({ t: line.slice(last, m.index) }); parts.push({ t: m[0], c: m[1] ? "cm" : "st" }); last = m.index + m[0].length; }
    parts.push({ t: line.slice(last) });
    parts.forEach((p, i) => { if (p.c === "st" && parts[i + 1] && /^\s*:/.test(parts[i + 1].t)) p.c = "k"; }); // clave: "x":
    return parts.map((p) => {
      if (p.c) return `<span class="sn-${p.c}">${esc(p.t)}</span>`;
      return esc(p.t).replace(KW, '<span class="sn-kw">$1</span>').replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="sn-nu">$1</span>')
        .replace(/\b([A-Za-z_][\w]*)(?=\()/g, '<span class="sn-fn">$1</span>');
    }).join("");
  }
  function jsonLines(obj) {
    // una línea por clave de primer nivel (registros planos de las pruebas); valores anidados en una línea
    const keys = Object.keys(obj || {});
    const out = [{ html: '<span class="sn-pu">{</span>', key: null }];
    keys.forEach((k, i) => {
      const v = obj[k];
      let vh;
      if (typeof v === "string") vh = `<span class="sn-st">"${esc(v)}"</span>`;
      else if (typeof v === "number") vh = `<span class="sn-nu">${esc(String(v))}</span>`;
      else if (typeof v === "boolean" || v === null) vh = `<span class="sn-kw">${String(v)}</span>`;
      else vh = `<span class="sn-st">${esc(JSON.stringify(v))}</span>`;
      out.push({ html: `<span class="sn-k">"${esc(k)}"</span><span class="sn-pu">: </span>${vh}${i < keys.length - 1 ? '<span class="sn-pu">,</span>' : ""}`, key: k, ind: 1 });
    });
    out.push({ html: '<span class="sn-pu">}</span>', key: null });
    return out;
  }

  CK.register("demo.snippet", {
    mount(root, props, ctx) {
      const E = gx.eases(ctx);
      const kind = ["chat", "email", "code", "json"].indexOf(props.kind) >= 0 ? props.kind : "chat";
      const st = gx.stage(root, ctx, props, "sn sn-" + kind);
      const A = st.A, bd = st.bd;
      let s = Math.max(0.72, Math.min(1.12, A.w / 900));
      A.node.style.setProperty("--s", s);
      const wrap = gx.el("div", "sn-wrap", A.node);
      // `bubble_font: "sans"` (regla de estilo: Montserrat siempre): las burbujas de chat en --ck-sans 600 en vez de
      // --ck-ui. Sin la prop, igual que antes
      if (props.bubble_font === "sans") wrap.classList.add("sn-fsans");
      const win = gx.el("div", "sn-win", wrap);
      // `code_wide`: a pantalla completa, la ventana de código usa
      // los 950 px de la banda alta (y acaba por encima de y = 1000: gx.tfit la sube; el alto se ajusta a esa banda) en vez
      // de los 696 de la «T»: un README de 8 líneas cabe a 48 px casi sin partir líneas. Sin la opción, igual que antes.
      const codeWide = kind === "code" && !!props.code_wide && !!A.tee;
      if (codeWide) win.style.width = A.w + "px";
      const cam = gx.el("div", "sn-cam", win); // capa que hace el punch-in
      let titleEl = null;
      if (kind === "code") {
        win.classList.add("sn-editor"); // editor real: cromado, pestaña, medianil con números y tema claro
        const tb = gx.el("div", "sn-title sn-chrome", cam);
        const dots = gx.el("span", "sn-dots", tb); gx.el("i", "", dots); gx.el("i", "", dots); gx.el("i", "", dots);
        if (props.title) gx.el("span", "sn-tab", tb, props.title);
      } else if (props.frame === "web") {
        // `frame: "web"`: la conversación dentro de una ventana de navegador (puntos + barra de dirección:
        // `url` real o barra en esqueleto); nada de marcas inventadas
        win.classList.add("sn-webwin");
        const tb = gx.el("div", "sn-title sn-chrome sn-web", cam);
        const dots = gx.el("span", "sn-dots", tb); gx.el("i", "", dots); gx.el("i", "", dots); gx.el("i", "", dots);
        if (props.url) gx.el("span", "sn-url", tb, props.url); else gx.el("span", "sn-url sn-url-skel", tb);
        if (props.title) { titleEl = gx.el("div", "sn-title", cam); gx.el("span", "", titleEl, props.title); }
      } else if (props.title) { titleEl = gx.el("div", "sn-title", cam); gx.el("span", "", titleEl, props.title); }
      const clip = kind === "code" ? gx.el("div", "sn-clip", cam) : null; // visor (solo si el bloque no cabe entero)
      const body = gx.el("div", "sn-body", clip || cam);
      const lines = (props.lines || []).slice(0, kind === "code" ? 14 : 10);
      const dense = kind === "code" && lines.length > 8; // bloque real largo: cuerpo compacto, sangría a 1/4 de anchura
      if (dense) win.classList.add("sn-dense");
      const items = []; // {node, kind:"line"|"bubble"|"field"|"body", chars?, words?}

      if (kind === "chat") {
        lines.slice(0, 4).forEach((l) => {
          const o = typeof l === "string" ? { role: "ai", text: l } : l;
          const row = gx.el("div", "sn-brow sn-" + (o.role === "user" ? "user" : "ai"), body);
          const b = gx.el("div", "sn-bubble" + (o.dots ? " sn-typing" : ""), row, o.dots ? null : o.text || "");
          // `dots`: burbuja de «escribiendo…» con tres puntos que laten (sin texto inventado)
          const dts = o.dots ? [gx.el("i", "", b), gx.el("i", "", b), gx.el("i", "", b)] : null;
          // `typed` (o props.typed en las del usuario): la burbuja se escribe al ritmo de la voz, LETRA A LETRA (
          // antes palabra a palabra: cada palabra salía entera de golpe y la QA de entrada de texto la marcaba)
          const typed = !o.dots && (o.typed != null ? !!o.typed : (!!props.typed && o.role === "user"));
          const words = typed ? gx.split(b, o.text || "", "chars") : null;
          // `check`: un check de oro junto a la burbuja (lo hecho), en la cue c<i> o al terminar de entrar
          const ck = o.check ? gx.el("div", "sn-check", row) : null;
          if (ck) ck.innerHTML = '<svg viewBox="0 0 48 48"><path d="M12 25 L21 34 L37 15"/></svg>';
          items.push({ node: row, inner: b, kind: "bubble", role: o.role, words, until: o.until, dts, ck, mark: typed ? o.mark : null,
                       text: o.text || "" });
        });
        // `fields`: formulario dentro del chat (lo que la IA recoge): cada campo se rellena en su cue f<k> (con
        // `v` se escribe letra a letra; sin `v`, una barra en esqueleto); `done` = check del formulario completo
        const flds = (props.fields || []).slice(0, 4);
        if (flds.length) {
          const form = gx.el("div", "sn-form", body);
          const fitems = flds.map((fd) => {
            const fr = gx.el("div", "sn-frow", form);
            if (fd.k) gx.el("span", "sn-fk", fr, fd.k);
            const val = gx.el("span", "sn-fval", fr);
            const chars = fd.v ? gx.split(val, fd.v, "chars") : null;
            const bar = fd.v ? null : gx.el("i", "sn-fbar", val);
            return { fr, chars, bar };
          });
          const fck = gx.el("div", "sn-check sn-fcheck", form);
          fck.innerHTML = '<svg viewBox="0 0 48 48"><path d="M12 25 L21 34 L37 15"/></svg>';
          items.push({ node: form, kind: "form", fitems, ck: fck });
        }
      } else if (kind === "email") {
        lines.forEach((l) => {
          if (l && l.k != null) {
            const fld = gx.el("div", "sn-field", body);
            gx.el("span", "sn-fk", fld, l.k);
            gx.el("span", "sn-fv", fld, l.v || "");
            items.push({ node: fld, kind: "field" });
          } else {
            const t = typeof l === "string" ? l : (l && l.text) || "";
            const p = gx.el("div", "sn-mail", body);
            items.push({ node: p, kind: "body", words: gx.split(p, t, props.typed ? "chars" : "words") });   // typed: letra a letra
          }
        });
      } else if (kind === "code") {
        lines.forEach((l, i) => {
          const ln = gx.el("div", "sn-line", body);
          // `line_from`: número de la primera línea (un extracto de un
          // bloque más largo, p. ej. las líneas 7–8 del README). Sin la prop, desde 1
          gx.el("span", "sn-no", ln, String((Number(props.line_from) > 1 ? props.line_from | 0 : 1) + i));
          const code = gx.el("span", "sn-code", ln);
          // la sangría se dibuja (no se teclea): a media anchura por espacio, y las filas partidas cuelgan 1 em más adentro
          const raw = String(l), ind = raw.length - raw.replace(/^ +/, "").length;
          code.style.paddingLeft = (ind * 0.25 + 1) + "em"; // sangría a 1/4 de anchura: más texto por fila a ≥40 px
          code.style.textIndent = "-1em";
          // `plain`: texto de README/salida, no código: sin colorear
          // palabras clave (en «No emojis as icons» el «as» salía en rojo)
          code.innerHTML = props.plain ? esc(raw.slice(ind)) : hlCode(raw.slice(ind));
          // caracteres: cada nodo de texto se parte en spans (conserva el resaltado)
          const chars = [];
          const walk = (n) => { Array.from(n.childNodes).forEach((c) => { if (c.nodeType === 3) { const frag = document.createDocumentFragment(); Array.from(c.textContent).forEach((ch) => { const sp = document.createElement("span"); sp.className = "sn-ch"; sp.textContent = ch; frag.appendChild(sp); chars.push(sp); }); c.replaceWith(frag); } else walk(c); }); };
          walk(code);
          items.push({ node: ln, kind: "line", chars });
        });
      } else {
        jsonLines(props.json).forEach((l) => {
          const ln = gx.el("div", "sn-line sn-j" + (l.ind ? " sn-ind" : ""), body);
          const mk = gx.el("div", "sn-mark", ln);
          const code = gx.el("span", "sn-code", ln);
          code.innerHTML = l.html;
          items.push({ node: ln, kind: "line", key: l.key, mark: mk });
        });
      }
      const caret = kind === "code" ? gx.el("div", "sn-caret", cam) : null;
      // code · highlights [{lines: [a, b], cue}] (índices 0-based, inclusivos): marcador oro sobre el rango en su cue,
      // punch suave de la ventana y el resto de líneas al 55 %
      const lineHl = kind === "code" ? (props.highlights || []).filter((h) => Array.isArray(h.lines) && h.lines.length).map((h) => {
        const a0 = Math.max(0, h.lines[0] | 0), b0 = Math.min(items.length - 1, (h.lines[1] != null ? h.lines[1] : h.lines[0]) | 0);
        const mk = gx.el("div", "sn-lmark", body);
        gsap.set(mk, { scaleX: 0 });
        return { h, a: a0, b: Math.max(a0, b0), mk };
      }) : [];
      // json, highlights [{key, cue}] (o focus_key): la fila en foco se pinta de oro EN SU SITIO en cada cue; el resto al 55 %.
      const hl = kind === "json" ? (props.highlights && props.highlights.length ? props.highlights : props.focus_key ? [{ key: props.focus_key, cue: "focus" }] : [])
        .map((h) => ({ h, it: items.find((it) => it.key && it.key === h.key) })).filter((o) => o.it) : [];


      gsap.set(win, { opacity: 0 });
      items.forEach((it) => {
        if (it.kind === "line" && kind === "code") gsap.set(it.chars, { opacity: 0 });
        else if (it.kind === "body") gsap.set(it.words, { opacity: 0 });
        else if (kind !== "json") gsap.set(it.node, { opacity: 0 });
        if (it.words && it.kind === "bubble") gsap.set(it.words, { opacity: 0 });
        if (it.ck) gsap.set(it.ck, { opacity: 0, scale: 0.4 });
        if (it.fitems) it.fitems.forEach((q) => { if (q.chars) gsap.set(q.chars, { opacity: 0 }); if (q.bar) gsap.set(q.bar, { scaleX: 0, transformOrigin: "0% 50%" }); });
        if (it.mark) gsap.set(it.mark, { scaleX: 0 });
      });
      if (caret) gsap.set(caret, { opacity: 0 });

      return {
        animate(tl, t0, t1, cues) {
          // ── ajustar: el texto cabe en el ancho (código/json a una línea por fila si se puede) y el conjunto en alto
          const fitAll = () => {
            if (kind === "code" || kind === "json") {
              const nodes = items.map((it) => it.node.querySelector(".sn-code"));
              const maxW = body.clientWidth - (kind === "code" ? 50 * s : 30 * s);
              let size = Math.round(52 * s);
              for (; size > 40; size -= 2) { body.style.fontSize = size + "px"; if (kind === "json" || nodes.every((n) => n.getBoundingClientRect().width <= maxW + 1)) break; }
              if (kind === "code") { // líneas largas partidas dentro; el mayor cuerpo que quepa en alto, nunca <40 px (QA)
                const minPx = dense ? 24 : 40;
                for (size = Math.min(Math.max(size, minPx), dense ? 40 : 52); size > minPx && win.offsetHeight > (codeWide ? A.yLow : A.h) * 0.97; size -= 1) body.style.fontSize = size + "px";
                body.style.fontSize = Math.max(minPx, size) + "px";
              }
              if (kind === "json") { // nunca se parte una palabra ni un token: el cuerpo se ajusta a la línea más larga (≥28 px)
                const fitJson = (hMax) => {
                  body.classList.add("sn-measure"); // medir cada línea en una sola fila
                  const fits = () => items.every((it) => { // ancho del texto + sangrías ≤ ancho de la línea (scrollWidth no cuenta el padding final)
                    const c = it.node.querySelector(".sn-code"), cs = getComputedStyle(it.node);
                    return c.offsetWidth + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight) <= it.node.clientWidth - 2;
                  });
                  for (size = 64; size > 28; size -= 1) { body.style.fontSize = size + "px"; if (fits() && win.offsetHeight <= hMax) break; }
                  body.style.fontSize = Math.max(28, size) + "px";
                  body.classList.remove("sn-measure"); // si a 28 px aún no cabe, se parte solo por espacios
                };
                if (A.tee) { // ~900 px si el registro entero cabe por encima de y=1000; si no, la ventana estrecha baja hasta 1240
                  win.style.width = Math.min(900, A.w) + "px"; fitJson(A.yLow * 0.96);
                  if (win.offsetHeight > A.yLow * 0.96) { win.style.width = A.wLow + "px"; fitJson(A.h * 0.96); }
                } else fitJson(A.h * 0.96);
                if (titleEl) gx.fit(titleEl, { max: Math.max(30, Math.round(40 * s)), min: 28, width: win.clientWidth - 2 * 34 * s, lines: 1 });
              }
            }
          };
          // `code_scale`: con pocas líneas cortas la ventana de 0,9
          // (≈700 px, código a ~44 px) dejaba medio panel vacío; code_scale (0,9–1,35) la agranda. Sin la opción, igual que antes.
          if (dense || kind === "code") { s = dense ? 0.75 : props.code_scale ? Math.max(0.9, Math.min(1.35, +props.code_scale)) : Math.min(s, 0.9); A.node.style.setProperty("--s", s); }
          fitAll();
          // `fill_max`: tope de esa escala (1,6 por defecto); con pocas
          // burbujas en la «T» se quedaban en ~700 de los 952 px de alto. Sin la prop, igual que antes
          const fMax = Number(props.fill_max) > 1.6 ? Math.min(2.2, Number(props.fill_max)) : 1.6;
          if (!dense && kind !== "code") s = gx.autoscale(A, wrap, s, fitAll, { fill: props.fill || 0.88, max: fMax, min: 0.6 });
          s = gx.tfit(A, wrap, s, null); // banda en «T» (pantalla completa): la ventana estrecha puede bajar de y=1000
          // `code_center`: con `code_wide`, la ventana se centra en la
          // banda ENTERA (288–1240) en vez de quedarse en la alta (dejaba ~400 px de blanco debajo). Sin la prop, igual
          if (codeWide && props.code_center) { wrap.style.top = ""; wrap.style.bottom = ""; }
          // si ni a 26 px cabe entero, la ventana es un visor del alto útil y la cámara lleva cada rango al centro
          let viewH = 0;
          const hCap = (codeWide ? A.yLow : A.h) * 0.97;   // code_wide: el alto de la banda alta
          if (kind === "code" && win.offsetHeight > hCap) {
            // visor de filas ENTERAS (como un editor): nunca media línea cortada arriba o abajo
            const rowH = parseFloat(getComputedStyle(body).lineHeight) || parseFloat(body.style.fontSize) * 1.2;
            viewH = R(Math.floor((body.offsetHeight - (win.offsetHeight - hCap)) / rowH) * rowH);
            clip.classList.add("sn-view"); clip.style.height = viewH + "px"; clip.dataset.row = rowH;
          }

          const dur = t1 - t0;
          const ex = f(5);
          const tIn = gx.settle(ctx, t0);
          // entrada EN EL CORTE: la ventana ya se ve en el fotograma de corte (0,85 → 1 y 0,96 → 1 en 3 f)
          // `entry: "rise"`: la entrada en el corte deja la pestaña
          // y los números ya legibles en el fotograma 1 (QA mo.text_entry, block); con «rise» la ventana sube 32 px y
          // funde 0 → 1 en 8 f (llega al 90 % en ~5 f) y termina igual, a 0,97, para el punch de los resaltados.
          // una revisión midió la subida en 3 f y 5 px (el ease de entrada la resolvía casi entera en los primeros
          // fotogramas): ahora 48 px en 10 f con power2.out, que se lee como movimiento. Solo con `entry: "rise"`
          if (lineHl.length && props.entry === "rise") ft(tl, win, { opacity: 0, scale: 0.93, y: R(48 * s) }, { opacity: 1, scale: 0.97, y: 0, duration: f(10), ease: "power2.out" }, tIn);
          else if (lineHl.length) ft(tl, win, { opacity: 0.85, scale: 0.93 }, { opacity: 1, scale: 0.97, duration: f(3), ease: E.enter }, tIn); // en el corte, a 0,97
          else gx.cutIn(tl, win, tIn);
          gx.ev(ctx, "enter", tIn);
          const tB = tIn + f(4);
          if (kind === "chat") {
            const n = items.length;
            const gap = Math.max(f(6), Math.min(0.55, (dur - 0.5) / Math.max(1, n)));
            // letras de una en una, nunca dos en el mismo fotograma (la QA de entrada de texto exime el tecleo así)
            const typeChars = (chars, a0, a1) => {
              const F0 = Math.round(a0 * 30), m = Math.max(1, Math.round(((a1 - a0) * 30) / Math.max(1, chars.length)));
              chars.forEach((c, k) => tl.set(c, { opacity: 1 }, T((F0 + k * m) / 30)));
              return (F0 + chars.length * m) / 30;
            };
            const popCheck = (ck, at) => { ft(tl, ck, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(8), ease: E.pop }, at); gx.ev(ctx, "check", at); };
            // `grow` — la burbuja escrita CRECE línea a línea con el texto (antes
            // nacía ya con el alto final y el texto la iba llenando); la ventana se queda arriba donde acaba y crece hacia
            // abajo (el estado final es el de siempre). `lines[i].mark` — rotulador oro sobre ese trozo literal al acabar
            // de escribirse (cue m<i>): la banda crece de izquierda a derecha por detrás y las letras pasan a tinta.
            const bubbleBox = (it) => {
              const b = it.inner;
              if (!b.dataset.box) { Object.assign(b.style, { position: "relative", zIndex: "0" }); b.dataset.box = "1"; }
              return b;
            };
            const growBubble = (it, a0, a1) => {
              // las letras aún no escritas no ocupan sitio (display:none): la burbuja crece y el texto se parte como al
              // teclear de verdad; el estado final es el de siempre. La ventana queda fija arriba (donde acaba).
              const ch = it.words;
              if (!ch || ch.length < 2) return;
              wrap.style.justifyContent = "flex-start";
              wrap.style.paddingTop = win.offsetTop + "px";
              // la palabra entera (su envoltorio) tampoco ocupa sitio hasta su primera letra: si no, los envoltorios vacíos
              // abrían una línea de más
              const wd = new Map();
              ch.forEach((c, k) => { const w = c.parentNode; if (w && !wd.has(w)) wd.set(w, { k, d: getComputedStyle(w).display }); });
              const cd = getComputedStyle(ch[0]).display;
              gsap.set(ch, { display: "none" });
              gsap.set(Array.from(wd.keys()), { display: "none" });
              const F0 = Math.round(a0 * 30), m = Math.max(1, Math.round(((a1 - a0) * 30) / Math.max(1, ch.length)));
              wd.forEach((v, w) => tl.set(w, { display: v.d }, T((F0 + v.k * m) / 30)));
              ch.forEach((c, k) => tl.set(c, { display: cd }, T((F0 + k * m) / 30)));
            };
            const markWords = (it, tM) => {
              const txt = String(it.text || ""), mk = String(it.mark || ""), idx = txt.indexOf(mk);
              if (!mk || idx < 0 || !it.words) return;
              // se mide con TODO el texto puesto (el estado final): si `grow` esconde letras, se mide antes
              const k0 = txt.slice(0, idx).replace(/\s+/g, "").length, n = mk.replace(/\s+/g, "").length;
              const sel = it.words.slice(k0, k0 + n);
              if (!sel.length) return;
              const b = bubbleBox(it), rows = [];
              sel.forEach((c) => {
                const y = c.offsetTop, r = rows.find((q) => Math.abs(q.y - y) < 4);
                if (r) { r.l = Math.min(r.l, c.offsetLeft); r.r = Math.max(r.r, c.offsetLeft + c.offsetWidth); r.h = Math.max(r.h, c.offsetHeight); }
                else rows.push({ y, l: c.offsetLeft, r: c.offsetLeft + c.offsetWidth, h: c.offsetHeight });
              });
              const pad = R(6 * s);
              // («señales reales» no se veía marcado): en tema oscuro la burbuja del
              // usuario YA es oro y la banda oro desaparecía encima. Ahí el marcado va invertido: banda de tinta y
              // letras en oro. En el resto de burbujas, como siempre (banda oro, letras a tinta).
              const inv = st.theme === "dark" && it.role === "user";
              const bands = rows.map((q) => {
                const d = gx.el("div", "sn-mk" + (inv ? " sn-mk-inv" : ""), b);
                // invertido: sin margen a la derecha (la banda de tinta se comía el primer punto de «…», tinta sobre tinta)
                Object.assign(d.style, { left: (q.l - pad) + "px", top: (q.y + q.h * 0.08) + "px", width: (q.r - q.l + (inv ? pad : 2 * pad)) + "px", height: R(q.h * 0.9) + "px" });
                gsap.set(d, { scaleX: 0 });
                return d;
              });
              ft(tl, bands, { scaleX: 0 }, { scaleX: 1, duration: f(9), ease: E.move, stagger: f(3) }, tM);
              const c0 = getComputedStyle(sel[0]).color || "#FFFFFF";
              const cTo = inv ? (getComputedStyle(b).getPropertyValue("--ck-accent").trim() || "#FECA1A") : "#161514";
              ft(tl, sel, { color: c0 }, { color: cTo, duration: f(4), ease: E.enter }, tM + f(2));
              gx.ev(ctx, "highlight", tM);
            };
            items.forEach((it, i) => {
              const at = Math.max(tIn, gx.cue(cues, "l" + i, tB + i * gap));
              if (it.kind === "form") {   // formulario: entra, cada campo se rellena en f<k>, check en `done`
                ft(tl, it.node, { opacity: 0, y: R(26 * s) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, at);
                let tf = at + f(8);
                it.fitems.forEach((q, k) => {
                  const a = Math.max(tf, gx.cue(cues, "f" + k, tf + 0.25));
                  if (q.chars) tf = typeChars(q.chars, a, a + Math.min(0.9, q.chars.length * 0.05));
                  else { ft(tl, q.bar, { scaleX: 0 }, { scaleX: 1, duration: f(10), ease: E.move }, a); tf = a + f(10); }
                  gx.ev(ctx, "field", a);
                });
                popCheck(it.ck, Math.max(tf + f(3), gx.cue(cues, "done", tf + f(4))));
                return;
              }
              if (it.words) {
                // escrita: la burbuja aparece y sus letras salen hasta su cue `w<i>` (o a ≈ 16 letras por segundo)
                ft(tl, it.node, { opacity: 0, y: R(18 * s) }, { opacity: 1, y: 0, duration: f(5), ease: E.enter }, at);
                const end = Math.max(at + f(6), gx.cue(cues, "w" + i, at + it.words.length * 0.06));
                const tEnd = typeChars(it.words, at + f(2), end);
                if (it.mark) markWords(it, Math.max(tEnd + f(4), gx.cue(cues, "m" + i, tEnd + f(6))));
                if (props.grow) growBubble(it, at + f(2), end);
                gx.ev(ctx, "type", at);
                if (it.ck) popCheck(it.ck, Math.max(tEnd + f(2), gx.cue(cues, "c" + i, tEnd + f(3))));
                return;
              }
              if (i === 0 && at - tIn <= 0.4 && !it.dts) tl.set(it.node, { opacity: 1 }, T(tIn)); // la primera ya se ve en el corte
              else ft(tl, it.node, { opacity: 0, y: R(26 * s), scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: f(7), ease: E.enter }, at);
              if (it.dts) {   // «escribiendo…»: los tres puntos laten hasta `until` (o el final) y la burbuja se va
                const tU = Math.min(t1 - 0.2, gx.cue(cues, "u" + i, it.until != null ? it.until : t1 - 0.2));
                for (let tb = at + f(6); tb < tU - 0.3; tb += 0.6) it.dts.forEach((d, k) => {
                  ft(tl, d, { y: 0, opacity: 0.45 }, { y: -R(9 * s), opacity: 1, duration: f(5), ease: E.enter }, tb + k * f(3));
                  ft(tl, d, { y: -R(9 * s), opacity: 1 }, { y: 0, opacity: 0.45, duration: f(6), ease: E.move }, tb + k * f(3) + f(5));
                });
                if (tU < t1 - 0.25) tl.to(it.node, { opacity: 0, y: -R(10 * s), duration: f(5), ease: E.exit }, tU);
              }
              if (it.ck) popCheck(it.ck, Math.max(at + f(8), gx.cue(cues, "c" + i, at + f(9))));
            });
          } else if (kind === "email") {
            let t = tB;
            items.forEach((it, i) => {
              const at = Math.max(tIn, gx.cue(cues, "l" + i, t));
              if (it.kind === "field") { tl.set(it.node, { opacity: 1 }, T(tIn)); t = Math.max(t, tIn + f(3)); } // campos ya en el corte
              else {
                // `typed`: letra a letra, una por fotograma como mucho; sin typed, palabra a palabra
                const per = props.typed ? Math.max(f(1), Math.min(0.06, (t1 - 0.6 - at) / Math.max(1, it.words.length)))
                  : Math.max(f(1), Math.min(0.09, (t1 - 0.6 - at) / Math.max(1, it.words.length)));
                const F0 = Math.round(at * 30), m = Math.max(1, Math.round(per * 30));
                it.words.forEach((w, k) => tl.set(w, { opacity: 1 }, T(props.typed ? (F0 + k * m) / 30 : at + k * per)));
                t = props.typed ? (F0 + it.words.length * m) / 30 : at + it.words.length * per;
              }
            });
          } else if (kind === "code") {
            const allChars = items.reduce((a, it) => a.concat(it.chars), []);
            let scY = 0; // desplazamiento del visor (compartido por la escritura y los resaltados)
            // con menos de 1,5 s (o prewritten) no se teclea: el código ya está escrito y el cursor parpadea al final
            if (props.prewritten || dur < 1.5) {
              tl.set(allChars, { opacity: 1 }, T(tIn));
              const last = allChars.length ? gx.rel(allChars[allChars.length - 1], cam) : { x: 0, y: 0, w: 0 };
              tl.set(caret, { opacity: 1, x: R(last.x + last.w), y: R(last.y) }, T(tIn));
              for (let u = tIn + 0.4, k = 0; u < t1 - 0.1; u += 0.4, k++) tl.set(caret, { opacity: k % 2 ? 1 : 0 }, T(u));
            } else {
            // se escribe LÍNEA A LÍNEA desde el corte y termina ≥0,4 s antes del primer resaltado (si lo hay)
            const tType = Math.max(tB, gx.cue(cues, "type", tB));
            const hl0 = lineHl.length ? Math.min(...lineHl.map((o, i) => Math.max(tIn + f(4) + i * f(8), gx.cue(cues, o.h.cue, tIn + 0.4 + i * 0.8)))) : null;
            const tEndType = hl0 != null ? hl0 - 0.4 : tType + Math.max(0.35, dur * 0.55);
            const span = Math.max(f(4), tEndType - tType), nCh = Math.max(1, allChars.length);
            const perLine = nCh / span > 60; // muy rápido para teclear letra a letra: aparece cada línea entera
            const cpos = allChars.map((c) => gx.rel(c, cam));
            const rowH = viewH ? parseFloat(clip.dataset.row) || 48 : 0, maxO = viewH ? Math.max(0, body.offsetHeight - viewH) : 0;
            let acc = 0, k0 = 0;
            const lineT = items.map((it) => { const t = tType + (acc / nCh) * span; acc += it.chars.length; return t; });
            tl.set(caret, { opacity: 1, x: cpos.length ? R(cpos[0].x) : 0, y: cpos.length ? R(cpos[0].y) : 0 }, T(tType - f(2)));
            items.forEach((it, li) => {
              const at = lineT[li], nx = li + 1 < items.length ? lineT[li + 1] : tEndType;
              if (viewH) { // el visor sigue a la línea que se escribe (a filas enteras)
                const r = gx.rel(it.node, body), bot = r.y + r.h;
                if (bot > -scY + viewH + 1) {
                  const to = -R(Math.min(maxO, Math.ceil((bot - viewH) / rowH) * rowH));
                  if (to !== scY) { ft(tl, body, { y: scY }, { y: to, duration: Math.max(f(1), Math.min(f(6), (nx - at) * 0.9)), ease: E.move }, at); scY = to; }
                }
              }
              const n = it.chars.length;
              if (!n) return;
              if (perLine) {
                tl.set(it.chars, { opacity: 1 }, T(at));
                const L = cpos[k0 + n - 1]; tl.set(caret, { x: R(L.x + L.w), y: R(L.y + scY) }, T(at));
              } else {
                const step = (nx - at) / n;
                it.chars.forEach((c, j) => { const q = cpos[k0 + j], t = at + j * step; tl.set(c, { opacity: 1 }, T(t)); tl.set(caret, { x: R(q.x + q.w), y: R(q.y + scY) }, T(t)); });
              }
              k0 += n;
            });
            for (let u = tEndType + 0.3, k = 0; u < t1 - 0.1; u += 0.4, k++) tl.set(caret, { opacity: k % 2 ? 1 : 0 }, T(u));
            }
            if (lineHl.length) {
              const bR = gx.rel(body, cam);
              const times = lineHl.map((o, i) => Math.max(tIn + f(4) + i * f(8), gx.cue(cues, o.h.cue, tIn + 0.4 + i * 0.8)));
              lineHl.forEach((o, i) => {
                const ra = gx.rel(items[o.a].node, body), rb = gx.rel(items[o.b].node, body);
                Object.assign(o.mk.style, { top: R(ra.y - 4) + "px", height: R(rb.y + rb.h - ra.y + 8) + "px" });
                const at = times[i], next = i + 1 < lineHl.length ? times[i + 1] : null;
                if (viewH) { // visor: solo se desplaza si el rango no se ve entero; a filas enteras
                  const rowH = parseFloat(clip.dataset.row) || 48, top = ra.y, bot = rb.y + rb.h, maxO = Math.max(0, body.offsetHeight - viewH);
                  const cur = -scY;
                  if (top < cur - 1 || bot > cur + viewH + 1) {
                    let o = Math.max(0, Math.min(maxO, (top + bot) / 2 - viewH / 2));
                    o = Math.round(o / rowH) * rowH;
                    if (o > top) o = Math.floor(top / rowH) * rowH;
                    if (o + viewH < bot) o = Math.ceil((bot - viewH) / rowH) * rowH;
                    const to = -R(Math.max(0, Math.min(maxO, o)));
                    if (to !== scY) { ft(tl, body, { y: scY }, { y: to, duration: f(9), ease: E.move }, at - f(2)); scY = to; }
                  }
                }
                gx.ev(ctx, "highlight", at);
                if (i === 0) ft(tl, win, { scale: 0.97 }, { scale: 1, duration: f(8), ease: E.move }, at); // punch suave
                // `push`: tras el punch, la cámara sigue empujando
                // despacio (1 → 1 + push, origen fijo en el centro: sin saltos al cambiar de línea) hasta el final. Sin la prop, nada
                const pz = Math.max(0, Math.min(0.06, +props.push || 0));
                if (pz && kind === "code") {
                  const tA = i === 0 ? at + f(8) : at, tB2 = next != null ? next : t1 - f(5);
                  const k0 = 1 + pz * Math.max(0, tA - (times[0] + f(8))) / Math.max(0.5, t1 - f(5) - times[0] - f(8));
                  const k1 = 1 + pz * Math.max(0, tB2 - (times[0] + f(8))) / Math.max(0.5, t1 - f(5) - times[0] - f(8));
                  if (tB2 - tA > f(2)) ft(tl, win, { scale: k0 }, { scale: k1, duration: tB2 - tA, ease: "none" }, tA);
                }
                ft(tl, o.mk, { scaleX: 0 }, { scaleX: 1, duration: f(7), ease: E.enter }, at);
                items.forEach((it, k) => tl.to(it.node, { opacity: k >= o.a && k <= o.b ? 1 : 0.55, duration: f(5), ease: E.enter }, at));
                if (next != null) tl.to(o.mk, { opacity: 0, duration: f(4), ease: E.exit }, next);
              });
              void bR;
            }
          } else {
            // json: entra ENTERO (con la ventana); en cada cue la lupa salta a su clave
            items.forEach((it) => tl.set(it.node, { opacity: 1 }, T(t0)));
            if (hl.length) {
              const times = hl.map((o, i) => Math.max(tIn + f(3) + i * f(8), gx.cue(cues, o.h.cue, tIn + f(5) + i * 0.6)));
              hl.forEach((o, i) => {
                const at = times[i], next = i + 1 < hl.length ? times[i + 1] : null;
                gx.ev(ctx, "highlight", at);
                if (i === 0) { ft(tl, win, { scale: 1 }, { scale: 1.025, duration: f(4), ease: E.move }, at); ft(tl, win, { scale: 1.025 }, { scale: 1, duration: f(8), ease: E.move }, at + f(4)); }
                ft(tl, o.it.mark, { scaleX: 0 }, { scaleX: 1, duration: f(7), ease: E.enter }, at);
                // el texto de la fila en foco pasa a tinta sobre el oro (y vuelve a su color al soltarla)
                const spans = Array.from(o.it.node.querySelectorAll(".sn-code span")), orig = spans.map((n) => getComputedStyle(n).color);
                const dark = A.node.classList.contains("gx-th-dark"), INKC = dark ? "#FFFFFF" : "#0B0B0C"; // en negro: texto claro sobre banda tenue
                if (spans.length) ft(tl, spans, { color: (k) => orig[k] }, { color: INKC, duration: f(3), ease: E.enter }, at + f(2));
                items.forEach((it) => tl.to(it.node, { opacity: it === o.it ? 1 : 0.55, duration: f(5), ease: E.enter }, at));
                if (next != null) {
                  tl.to(o.it.mark, { opacity: 0, duration: f(4), ease: E.exit }, next);
                  if (spans.length) tl.to(spans, { color: (k) => orig[k], duration: f(3), ease: E.enter }, next);
                }
              });
            }
          }
          gx.bgIn(tl, bd, t0, t1, 91, props);
          gx.out(tl, props, t1, [wrap], { dur: ex , ctx });
        },
      };
    },
  });
})(window.CK);
