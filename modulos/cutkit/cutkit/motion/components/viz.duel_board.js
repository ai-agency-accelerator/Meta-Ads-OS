// viz.duel_board — el marcador de un vídeo «A contra B» (Nimbo Pro 2 contra Acme Plus 1…): las DOS fichas (logo verificado +
//   nombre) siempre arriba y en el mismo sitio (A izquierda, B derecha) y debajo lo que se compara. Hilo conductor.
//   table: tabla tipográfica con filetes; fila = criterio (Tiempo, Coste, Resultado); cada celda empieza en «?» y en su
//          palabra cambia a la cifra REAL con una barra proporcional a la mayor de la fila. `intro: "duel"` = gancho:
//          las fichas GRANDES con un «VS» desde el fotograma 0 que se encogen a la cabecera en «title», con el esqueleto
//          de filas en fantasma que se enciende fila a fila. `hero` = cada cifra entra GRANDE sobre el marcador velado
//          y vuela a su celda. `steps` ponen el foco (oro) en unas celdas y atenúan el resto.
//          Con UNA fila es una CARRERA: una barra por lado a todo el ancho; `run` en la celda = la barra corre desde
//          esa palabra hasta su cifra con un contador de minutos.
//   lanes: un raíl vertical bajo cada ficha (fantasma desde el corte); cada paso es un nodo en su palabra (el último,
//          en oro); el raíl corto acaba en un tope («Se Detiene»), el largo sigue (Revisar → … → Terminado).
//   pick : la recomendación: bajo cada ficha sus criterios en su palabra; la respuesta = anillo de oro en la ficha.
// props: {sides: [{label, asset}] ×2, mode: table|lanes|pick, title?, vs?, intro?: true|"duel", hero?, rows?, steps?,
//         lanes?, cols?, dim?, canvas?, keep_start?, exit?}
// cues:  h0, h1 (fichas) · title · table: r0…(filas), cue/run de cada celda, s0…(pasos) · lanes: cue/draw de cada paso ·
//        pick: cue de cada criterio, p0/p1 (respuesta)
// eventos: enter, land (ficha), row, value, highlight, node, stop, pick, exit
// Todo opcional; sin estas props,
//   el comportamiento de siempre salvo el arreglo del «?» fantasma (en todos los vídeos):
//   · «?» fantasma: la fila ya no sube su «?» al 34 % si la cifra cae antes de que acabe esa subida (salía «2?$»), y el
//     «?» queda a 0 cuando aterriza la cifra.
//   · `q: false`: celdas sin «?» (vacías hasta su cifra; las que no tienen cifra se quedan vacías).
//   · celda `hero: false`: esa cifra entra en su celda (sube 22 px, 7 f) aunque el marcador tenga `hero`.
//   · `solo: true` con UN lado (table): una sola columna centrada (la ficha y sus cifras en el eje).
//   · TRES lados (table, sin «duel» ni carrera): tres columnas con la ficha apilada (logo arriba, nombre debajo); las
//     celdas y `steps` usan c0…c2. La barra de cada celda, proporcional a la mayor de su fila.
//   · `text_in: true`: el rótulo de cabecera (`title`) y los de fila (Entrada, Salida) entran con gx.textIn (8 f, sube
//     32 px), también en el corte, en vez de los fundidos de 6–7 f.
//   · gancho («duel») con cue `eyebrow`: el `title` sube en esa palabra DURANTE el duelo (las fichas bajan lo justo para
//     dejarle sitio) y no espera al encogido. Lado `big: true`: el monograma («?») a ~58 % de la baldosa.
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

  // Ficha de un lado: baldosa de cristal con el logo verificado + nombre a su derecha.
  function badge(parent, ctx, side, cls) {
    const b = gx.el("div", "db-badge " + (cls || ""), parent);
    const tile = gx.el("div", "db-tile", b);
    gx.el("div", "db-glass", tile);
    const ring = gx.el("div", "db-ring", tile);
    // sin logo verificado: monograma tipográfico (p. ej. «NIM»; `strike` lo tacha para el lado «sin»), nunca un hueco
    if (side.asset) gx.logo(tile, ctx, side.asset, "db-logo");
    else gx.el("div", "db-mono" + (side.strike ? " db-mono-strike" : "") + (side.big ? " db-mono-big" : ""), tile, side.mono || (side.label || "?").slice(0, 3));
    const name = gx.el("div", "db-name", b, side.label || "");
    return { b, tile, ring, name };
  }
  // «1 h 17 min» ↔ 77 (contador de la carrera)
  const fmtMin = (v) => { const m = Math.max(0, Math.round(v)); return m < 60 ? `${m} min` : `${Math.floor(m / 60)} h ${m % 60} min`; };

  CK.register("viz.duel_board", {
    mount(root, props, ctx) {
      const E = gx.eases(ctx);
      const st = gx.stage(root, ctx, props, "db");
      const A = gx.upper(st.A), bd = st.bd;
      // `max_w` (opt-in) = ancho
      // máximo del marcador en px, centrado en el lienzo (696 = la zona de texto de Shorts/Reels, x 192–888)
      if (typeof props.max_w === "number" && props.max_w >= 300 && A.w > props.max_w) {
        const dw = A.w - R(props.max_w);
        A.w = R(props.max_w); A.x += dw / 2;
        A.node.style.left = R((parseFloat(A.node.style.left) || 0) + dw / 2) + "px"; A.node.style.width = A.w + "px";
      }
      const mode = ["table", "lanes", "pick"].indexOf(props.mode) >= 0 ? props.mode : "table";
      const rows = (props.rows || []).slice(0, 3);
      // columnas: 2 siempre; 1 con `solo` y un lado; 3 con tres lados (solo tabla, sin «duel» ni carrera)
      const nIn = (props.sides || []).length;
      const NS = mode !== "table" || rows.length === 1 ? 2
        : nIn === 1 && props.solo && props.intro !== "duel" ? 1 : nIn >= 3 && props.intro !== "duel" ? 3 : 2;
      const STACK = NS === 3;                                   // tres fichas: logo arriba y nombre debajo
      const sides = (props.sides || []).slice(0, NS);
      while (sides.length < NS) sides.push({ label: "" });
      const wrap = gx.el("div", "db-wrap", A.node);
      const colW = R(A.w / NS);
      const CX = sides.map((_, i) => R(i * colW + colW / 2));

      // ── altura natural a escala 1 → escala que cabe en el área (split 288–1000 o banda alta de pantalla completa)
      const title = props.title || null;
      const lanes = (props.lanes || []).slice(0, 2);
      const cols = (props.cols || []).slice(0, 2);
      const race = mode === "table" && rows.length === 1;      // carrera: una barra por lado a todo el ancho
      const EYE = title ? (race ? 128 : 78) : 0, HEAD = STACK ? 236 : 140, ROW = 190, LANE = 236;
      const STEP = 118, LTOP = 70, ITEM = 100;
      const nSteps = Math.max(1, ...lanes.map((l) => (l.steps || []).length + (l.end ? 1 : 0)));
      const nItems = Math.max(1, ...cols.map((c) => (c.items || []).length));
      const H1 = race ? EYE + 2 * LANE
        : mode === "table" ? EYE + HEAD + rows.length * ROW
          : mode === "lanes" ? EYE + HEAD + LTOP + nSteps * STEP
            : EYE + HEAD + 40 + nItems * ITEM;
      const s = Math.max(0.6, Math.min(Math.min(1.1, A.w / 950), (A.h * 0.97) / H1));
      A.node.style.setProperty("--s", s);
      const y0 = R(Math.max(0, (A.h - H1 * s) / 2));
      const S = (v) => R(v * s);

      const eye = title ? gx.el("div", "db-eyebrow", wrap, title) : null;
      if (eye) Object.assign(eye.style, { top: y0 + "px", height: S(78) + "px" });
      const yH = y0 + S(EYE);                      // arriba de la cabecera

      // ── cabecera (tabla, carriles y pick): las dos fichas SIEMPRE en el mismo sitio, centradas en su columna
      let heads = [], vs = null;
      if (!race) {
        heads = sides.map((sd, i) => {
          const h = badge(wrap, ctx, sd, STACK ? "db-badge-stack" : "");
          Object.assign(h.b.style, { left: R(i * colW) + "px", top: yH + "px", height: S(HEAD - 40) + "px", width: colW + "px" });
          return h;
        });
        if (props.vs && mode === "table" && NS === 2) {
          vs = gx.el("div", "db-vs", wrap, "VS");
          Object.assign(vs.style, { left: R(colW - S(100)) + "px", top: yH + "px", width: S(200) + "px", height: S(HEAD - 40) + "px" });
        }
      }

      // ── TABLA / CARRERA
      const trows = [];
      if (mode === "table") {
        const yR = yH + S(HEAD);
        rows.forEach((rw, r) => {
          const cells0 = (rw.cells || []).slice(0, race ? 2 : NS);
          while (cells0.length < (race ? 2 : NS)) cells0.push({});
          const ns = cells0.map((c) => (typeof c.n === "number" && c.n > 0 ? c.n : 0));
          const mx = Math.max(...ns);
          const bars = rw.bars != null ? !!rw.bars : mx > 0;
          if (race) {
            const lab = gx.el("div", "db-k", wrap, rw.k || "");
            Object.assign(lab.style, { top: R(y0 + S(80)) + "px", height: S(44) + "px" });
            const cells = cells0.map((c, i) => {
              const y = yH + i * S(LANE);
              const hb = badge(wrap, ctx, sides[i], "db-badge-left");
              Object.assign(hb.b.style, { left: "0px", top: y + "px", height: S(112) + "px", width: R(A.w * 0.5) + "px" });
              heads.push(hb);
              const box = gx.el("div", "db-cell db-cell-race", wrap);
              Object.assign(box.style, { left: R(A.w * 0.44) + "px", top: y + "px", width: R(A.w * 0.56) + "px", height: S(112) + "px" });
              const q = gx.el("div", "db-v db-q", box, "?");
              const v = c.v ? gx.el("div", "db-v", box, c.v) : null;
              const vh = c.v ? gx.el("div", "db-v db-v-hot", box, c.v) : null;
              const track = gx.el("div", "db-track db-track-race", wrap);
              Object.assign(track.style, { left: "0px", top: R(y + S(136)) + "px", width: A.w + "px" });
              let fill = null, fillH = null;
              if (ns[i] > 0) {
                const fw = Math.max(S(36), R(A.w * ns[i] / mx));
                fill = gx.el("div", "db-fill", track); fill.style.width = fw + "px";
                fillH = gx.el("div", "db-fill db-fill-hot", track); fillH.style.width = fw + "px";
              }
              return { c, box, q, v, vh, track, fill, fillH, n: ns[i], ratio: mx ? ns[i] / mx : 0, key: `r${r}c${i}`, race: true };
            });
            trows.push({ rw, rule: null, lab, cells, r, segs: [] });
            return;
          }
          const y = yR + r * S(ROW);
          const rule = gx.el("div", "db-rule", wrap);
          Object.assign(rule.style, { top: y + "px" });
          const lab = gx.el("div", "db-k", wrap, rw.k || "");
          Object.assign(lab.style, { top: R(y + S(12)) + "px", height: S(44) + "px" });
          // separadores verticales entre columnas (ninguno con una sola; dos con tres)
          const segs = Array.from({ length: NS - 1 }, (_, k) => {
            const seg = gx.el("div", "db-divider", wrap);
            Object.assign(seg.style, { left: R((k + 1) * colW - 1) + "px", top: R(y + S(64)) + "px", height: R(S(ROW) - S(80)) + "px" });
            return seg;
          });
          const cells = cells0.map((c, i) => {
            const box = gx.el("div", "db-cell", wrap);
            Object.assign(box.style, { left: R(i * colW) + "px", top: R(y + S(58)) + "px", width: colW + "px", height: S(100) + "px" });
            const q = gx.el("div", "db-v db-q", box, "?");
            const v = c.v ? gx.el("div", "db-v", box, c.v) : null;
            const vh = c.v ? gx.el("div", "db-v db-v-hot", box, c.v) : null;
            let track = null, fill = null, fillH = null;
            if (bars) {
              const bw = R(colW * 0.72);
              track = gx.el("div", "db-track", wrap);
              Object.assign(track.style, { left: R(i * colW + (colW - bw) / 2) + "px", top: R(y + S(166)) + "px", width: bw + "px" });
              if (ns[i] > 0) {
                const fw = Math.max(S(18), R(bw * ns[i] / mx));
                fill = gx.el("div", "db-fill", track); fill.style.width = fw + "px";
                fillH = gx.el("div", "db-fill db-fill-hot", track); fillH.style.width = fw + "px";
              }
            }
            return { c, box, q, v, vh, track, fill, fillH, n: ns[i], ratio: mx ? ns[i] / mx : 0, key: `r${r}c${i}` };
          });
          trows.push({ rw, rule, lab, cells, r, segs });
        });
      }
      // cifra héroe (table + hero): la cifra nueva entra GRANDE en el centro del marcador y se encoge hasta su celda
      const heroOn = mode === "table" && !race && !!props.hero;
      const veil = heroOn ? gx.el("div", "db-veil", wrap) : null;
      const hy = R(yH + S(HEAD) + (rows.length * S(ROW) - S(200)) / 2);
      if (veil) {
        Object.assign(veil.style, { top: R(yH + S(HEAD) - S(4)) + "px", height: R(rows.length * S(ROW) + S(8)) + "px" });
        trows.forEach((tr) => tr.cells.forEach((c) => {
          if (!c.v || !c.c.cue || c.c.hero === false) return;   // `hero: false`: esa cifra entra en su celda
          c.hero = gx.el("div", "db-hero", wrap, c.c.v);
          Object.assign(c.hero.style, { top: hy + "px", height: S(200) + "px" });
        }));
      }

      // ── CARRILES: bajo cada ficha un raíl vertical (fantasma desde el corte); cada paso es un nodo en su palabra
      const tlanes = [];
      if (mode === "lanes") {
        lanes.forEach((ln, i) => {
          const g = gx.el("div", "db-lane", wrap);
          const ghost = gx.el("div", "db-seg db-seg-ghost", g);
          const all = (ln.steps || []).map((p) => Object.assign({ kind: "node" }, p));
          if (ln.end) all.push(Object.assign({ kind: ln.end.kind === "stop" ? "stop" : "done" }, ln.end));
          const pts = all.map((p, k) => {
            const seg = gx.el("div", "db-seg", g);
            const gnode = p.kind === "stop" ? null : gx.el("div", "db-node db-node-ghost", g);
            const mark = gx.el("div", p.kind === "stop" ? "db-stop" : "db-node" + (p.kind === "done" ? " db-node-done" : ""), g);
            const markH = p.kind === "stop" ? null : gx.el("div", "db-node db-node-hot" + (p.kind === "done" ? " db-node-done" : ""), g);
            const lab = gx.el("div", "db-step" + (p.kind === "stop" ? " db-step-stop" : ""), g, p.label || "");
            return { p, seg, gnode, mark, markH, lab, k, y: yH + S(HEAD) + S(LTOP) + k * S(STEP) };
          });
          tlanes.push({ g, ghost, pts, ln, i });
        });
      }

      // ── PICK: criterios bajo cada ficha (en su palabra); la respuesta = anillo de oro en la ficha de arriba
      const tcols = [];
      if (mode === "pick") {
        cols.forEach((cl, i) => {
          const g = gx.el("div", "db-col", wrap);
          const its = (cl.items || []).slice(0, 4).map((it, k) => {
            const n = gx.el("div", "db-item", g, typeof it === "string" ? it : it.label || "");
            Object.assign(n.style, { left: R(i * colW + S(16)) + "px", width: R(colW - S(32)) + "px",
              top: R(yH + S(HEAD) + S(40) + k * S(ITEM)) + "px", height: S(ITEM - 8) + "px" });
            return { n, it };
          });
          tcols.push({ g, its, cl, i });
        });
      }

      // ── estado inicial (seek-safe: los tweens son fromTo con immediateRender:false)
      const intro = props.intro === "duel" ? "duel" : !!props.intro;
      heads.forEach((h) => { gsap.set(h.ring, { opacity: 0 }); if (intro === true) gsap.set(h.b, { opacity: 0 }); });
      if (vs) gsap.set(vs, { opacity: 0 });
      if (eye) gsap.set(eye, { opacity: 0 });
      if (veil) gsap.set(veil, { opacity: 0 });
      trows.forEach((tr) => tr.cells.forEach((c) => { if (c.hero) gsap.set(c.hero, { opacity: 0 }); }));
      trows.forEach((tr) => tr.cells.forEach((c) => { if (c.vh) gsap.set(c.vh, { opacity: 0 }); if (c.fillH) gsap.set(c.fillH, { opacity: 0 }); }));
      tlanes.forEach((ln) => { gsap.set(ln.ghost, { opacity: 0 });
        ln.pts.forEach((p) => { gsap.set([p.mark, p.lab], { opacity: 0 }); gsap.set(p.seg, { scaleY: 0 }); if (p.markH) gsap.set(p.markH, { opacity: 0 }); if (p.gnode) gsap.set(p.gnode, { opacity: 0 }); }); });
      tcols.forEach((c) => c.its.forEach((x) => gsap.set(x.n, { opacity: 0 })));

      return {
        animate(tl, t0, t1, cues) {
          const C = (k, d) => gx.cue(cues, k, d);
          const tS = gx.settle(ctx, t0);
          // ── ajuste de cuerpos (tras cargar fuentes)
          heads.forEach((h) => gx.fit(h.name, { max: S(54), min: 34, width: STACK ? R(colW - S(24)) : R((race ? A.w * 0.5 : colW) - S(HEAD - 40) - S(40)), lines: 1 }));
          const TXIN = props.text_in === true;     // rótulos de cabecera y de fila con gx.textIn (8 f, 32 px)
          const qOn = props.q !== false;           // `q: false` = celdas sin «?»
          // ancho REAL en el DOM (misma clase, fuente y glifos de reserva como «≈»), a un cuerpo dado
          const textW = (n, px) => {
            const sp = document.createElement("span");
            sp.className = n.className;
            sp.style.cssText = `position:absolute;visibility:hidden;display:inline-block;inset:auto;left:0;top:0;width:auto;height:auto;white-space:nowrap;font-size:${px}px`;
            sp.textContent = n.textContent || "";
            wrap.appendChild(sp);
            const w = sp.getBoundingClientRect().width;
            sp.remove();
            return w;
          };
          // todas las cifras al MISMO cuerpo (el mayor que quepa en todas)
          const vals = [];
          trows.forEach((tr) => tr.cells.forEach((c) => [c.v, c.vh].filter(Boolean).forEach((n) => vals.push(n))));
          const vMax = S(race ? 104 : 96), vW = race ? R(A.w * 0.54) : R(colW * 0.86);
          const vSize = Math.max(48, Math.min(vMax, ...vals.map((n) => Math.floor(vMax * vW / Math.max(1, textW(n, vMax))))));
          trows.forEach((tr) => tr.cells.forEach((c) => [c.q, c.v, c.vh].filter(Boolean).forEach((n) => { n.style.fontSize = vSize + "px"; })));
          tcols.forEach((c) => c.its.forEach((x) => gx.fit(x.n, { max: S(70), min: 44, width: R(colW - S(40)), lines: 1 })));
          if (eye) gx.fit(eye, { max: S(50), min: 34, width: A.w, lines: 1 });

          if (intro) gx.ev(ctx, "enter", tS);
          if (eye && intro !== "duel") {
            const te = Math.max(tS, C("title", tS));
            if (TXIN) gx.textIn(tl, eye, te <= tS + f(1) ? tS : te);
            else if (te <= tS + f(1)) gx.cutIn(tl, eye, tS); else ft(tl, eye, { opacity: 0, y: S(14) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, te);
          }

          // ── fichas
          let tShrink = tS;                         // momento en que el marcador queda armado (duelo → cabecera)
          if (intro === "duel") {
            // GANCHO: las dos fichas GRANDES (logo ~200 px) y un «VS» en Montserrat 900 desde el fotograma 0; B espera
            // al 35 % hasta su nombre (h1); en «title» el duelo se encoge exactamente a la cabecera del marcador.
            tShrink = Math.max(tS + 0.6, C("title", tS + 2.0));
            // con cue `eyebrow`, el `title` sube en esa palabra durante el duelo: las fichas bajan lo justo
            const tEyeD = eye ? C("eyebrow", null) : null;
            let yc = R(A.h * 0.46);
            if (tEyeD != null) yc = Math.max(yc, Math.min(R((parseFloat(eye.style.top) || 0) + S(78) + S(24) + S(160)), R(A.h - S(160))));
            const rv = vs ? gx.rel(vs, wrap) : null;
            const geo = heads.map((h, i) => {
              const rt = gx.rel(h.tile, wrap), rn = gx.rel(h.name, wrap);
              return { kT: S(200) / Math.max(1, rt.h), kN: 1.35,
                tx: R(CX[i] - (rt.x + rt.w / 2)), ty: R(yc - S(60) - (rt.y + rt.h / 2)),
                nx: R(CX[i] - (rn.x + rn.w / 2)), ny: R(yc + S(110) - (rn.y + rn.h / 2)) };
            });
            const th1 = Math.max(tS + f(2), Math.min(tShrink - f(8), C("h1", tS + 1.2)));
            heads.forEach((h, i) => {
              const g = geo[i];
              gsap.set(h.tile, { x: g.tx, y: g.ty, scale: g.kT });
              gsap.set(h.name, { x: g.nx, y: g.ny, scale: g.kN });
              // kit v14: las fichas y sus nombres ENTRAN en el corte (8 f, subida de 32 px y opacidad
              // ≈ power2.out), nunca «ya puestas» en el primer fotograma; B llega a su 35 % de espera
              gsap.set(h.b, { opacity: 0 });
              ft(tl, h.b, { opacity: 0 }, { opacity: i ? 0.35 : 1, duration: f(10), ease: E.enter }, tS + i * f(2));
              ft(tl, h.tile, { y: g.ty + S(32) }, { y: g.ty, duration: f(8), ease: E.enter }, tS + i * f(2));
              ft(tl, h.name, { y: g.ny + S(32) }, { y: g.ny, duration: f(8), ease: E.enter }, tS + f(2) + i * f(2));
              if (i === 1) ft(tl, h.tile, { scale: g.kT * 0.9 }, { scale: g.kT, duration: f(8), ease: E.pop }, th1);
              ft(tl, h.tile, { x: g.tx, y: g.ty, scale: g.kT }, { x: 0, y: 0, scale: 1, duration: f(12), ease: E.move }, tShrink);
              ft(tl, h.name, { x: g.nx, y: g.ny, scale: g.kN }, { x: 0, y: 0, scale: 1, duration: f(12), ease: E.move }, tShrink);
            });
            ft(tl, heads[1].b, { opacity: 0.35 }, { opacity: 1, duration: f(6), ease: E.enter }, Math.max(th1, tS + f(12)));
            gx.ev(ctx, "land", th1);
            if (vs) {
              const vy = R(yc - S(60) - (rv.y + rv.h / 2));
              gsap.set(vs, { opacity: 0, y: vy, scale: 2.6 });
              ft(tl, vs, { opacity: 0, scale: 3.0 }, { opacity: 1, scale: 2.6, duration: f(8), ease: E.enter }, tS + f(4));
              ft(tl, vs, { y: vy, scale: 2.6, opacity: 1 }, { y: 0, scale: 1, opacity: 0.6, duration: f(12), ease: E.move }, tShrink);
            }
            if (eye && tEyeD != null) gx.textIn(tl, eye, Math.max(tS + f(2), tEyeD));
            else if (eye && TXIN) gx.textIn(tl, eye, tShrink + f(6));
            else if (eye) ft(tl, eye, { opacity: 0, y: S(14) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, tShrink + f(6));
            gx.ev(ctx, "row", tShrink);
          } else {
            heads.forEach((h, i) => {
              if (!intro) { gx.cutIn(tl, h.b, tS); return; }
              let th = Math.max(tS, C("h" + i, tS + i * 0.6));
              // kit v14: en el corte también entran (antes tl.set: «ya puestas» en el primer fotograma)
              if (th <= tS + f(1)) th = tS;
              ft(tl, h.tile, { opacity: 0, scale: 0.84, y: S(16) }, { opacity: 1, scale: 1, y: 0, duration: f(8), ease: E.pop }, th);
              // apilada (tres lados): el nombre sube bajo su logo; en fila, llega desde su lado (con una sola, desde abajo)
              const nFrom = STACK || NS === 1 ? { opacity: 0, y: S(18) } : { opacity: 0, x: i ? S(18) : -S(18) };
              ft(tl, h.name, nFrom, { opacity: 1, x: 0, y: 0, duration: f(7), ease: E.enter }, th + f(2));
              tl.set(h.b, { opacity: 1 }, T(th));
              gsap.set([h.tile, h.name], { opacity: 0 });
              gx.ev(ctx, "land", th);
            });
            if (vs) gx.cutIn(tl, vs, tS);
          }

          // ── TABLA / CARRERA
          if (mode === "table") {
            const GH = 0.38;
            trows.forEach((tr) => {
              const tr0 = Math.max(tS, C("r" + tr.r, tS));
              const inst = tr0 <= tS + f(1);
              const lines = [tr.rule, tr.lab].concat(tr.segs).filter(Boolean);
              const tracks = tr.cells.map((c) => c.track).filter(Boolean);
              gsap.set(lines.concat(tracks), { opacity: 0 });
              // (pistas y divisores vacíos de columnas aún sin nombrar). `cols_in`
              // (opt-in, fila en el corte): cada columna (su pista y el divisor que la abre) entra con SU ficha (cue h<i>)
              const hT = (i) => { const th = Math.max(tS, C("h" + i, tS + i * 0.6)); return th <= tS + f(1) ? tS : th; };
              if (inst && props.cols_in === true && NS > 1 && !race) {
                const c0 = [tr.rule].concat(tr.cells[0] && tr.cells[0].track ? [tr.cells[0].track] : []).filter(Boolean);
                tl.set(c0, { opacity: 1 }, T(tS));
                if (TXIN) gx.textIn(tl, tr.lab, tS + tr.r * f(3)); else tl.set(tr.lab, { opacity: 1 }, T(tS));
                tr.segs.forEach((sg, k) => ft(tl, sg, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, hT(k + 1)));
                tr.cells.slice(1).forEach((c, j) => { if (c.track) ft(tl, c.track, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, hT(j + 1) + f(2)); });
              } else if (!inst && props.ghost === false) {
                // (nada de huecos vacíos de relleno): sin esqueleto
                // fantasma; la fila NACE en su palabra (filete que se traza, rótulo que sube, pistas)
                if (tr.rule) ft(tl, tr.rule, { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: f(9), ease: E.move }, tr0);
                const rest = tr.segs.concat(tracks);
                if (rest.length) ft(tl, rest, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, tr0 + f(1));
                if (TXIN) gx.textIn(tl, tr.lab, tr0); else ft(tl, tr.lab, { opacity: 0, y: S(28) }, { opacity: 1, y: 0, duration: f(8), ease: E.enter }, tr0);
                gx.ev(ctx, "row", tr0);
              } else if (inst && TXIN) {
                // (`text_in`): el rótulo de la fila SUBE en el corte (8 f, 32 px; filas escalonadas 3 f); el resto,
                // que no es texto, ya está
                tl.set(lines.concat(tracks).filter((n) => n !== tr.lab), { opacity: 1 }, T(tS));
                gx.textIn(tl, tr.lab, tS + tr.r * f(3));
              } else if (inst) tl.set(lines.concat(tracks), { opacity: 1 }, T(tS));
              else {
                // esqueleto fantasma en cuanto el marcador está armado; la fila se enciende EN SU PALABRA
                const tG = intro === "duel" ? tShrink + f(11) + tr.r * f(2) : tS;
                if (tr.rule) ft(tl, tr.rule, { scaleX: 0, opacity: GH }, { scaleX: 1, duration: f(9), ease: E.move }, tG);
                if (TXIN) {   // el rótulo fantasma SUBE (8 f, 28 px) en vez de aparecer por fundido
                  ft(tl, tr.segs.concat(tracks), { opacity: 0 }, { opacity: GH, duration: f(6), ease: E.enter }, tG + f(1));
                  ft(tl, tr.lab, { opacity: 0, y: S(28) }, { opacity: GH, y: 0, duration: f(8), ease: E.enter }, tG + f(1));
                } else ft(tl, [tr.lab].concat(tr.segs, tracks), { opacity: 0 }, { opacity: GH, duration: f(6), ease: E.enter }, tG + f(1));
                ft(tl, lines.concat(tracks), { opacity: GH }, { opacity: 1, duration: f(6), ease: E.enter }, tr0);
                ft(tl, tr.lab, { y: S(8) }, { y: 0, duration: f(6), ease: E.enter }, tr0);
                gx.ev(ctx, "row", tr0);
              }
              tr.cells.forEach((c, i) => {
                const hasV = !!c.v;
                const tc = hasV ? (c.c.cue ? Math.max(tS, C(c.c.cue, tr0 + 0.4 + i * 0.6)) : tS) : null;
                const filledAtCut = hasV && tc <= tS + f(1);
                gsap.set(c.q, { opacity: 0 });
                // la subida del «?» al 34 % en su fila
                // empezaba DESPUÉS del fundido a 0 de la cifra cuando fila y cifra caían en la misma palabra, y el «?» se
                // quedaba al 34 % detrás de la cifra. Cada tramo del «?» solo se programa si acaba antes de que llegue la
                // cifra; `qLvl` = nivel real del «?» en ese momento (de ahí sale su salida) y al aterrizar queda a 0
                let qLvl = 0;
                if (!filledAtCut && qOn) {
                  if (inst) { tl.set(c.q, { opacity: 0.3 }, T(tS)); qLvl = 0.3; }
                  else {
                    const tG = intro === "duel" ? tShrink + f(13) + tr.r * f(2) : tS;
                    if (!hasV || tG + f(6) <= tc - f(1)) {
                      ft(tl, c.q, { opacity: 0 }, { opacity: 0.18, duration: f(6), ease: E.enter }, tG);
                      qLvl = 0.18;
                      if (!hasV || tr0 + f(8) <= tc - f(1)) {
                        ft(tl, c.q, { opacity: 0.18 }, { opacity: 0.34, duration: f(6), ease: E.enter }, tr0 + f(2));
                        qLvl = 0.34;
                      }
                    }
                  }
                }
                if (!hasV) return;
                const hot = !!c.c.hot;
                const vN = hot ? c.vh : c.v, fN = hot ? c.fillH : c.fill;
                gsap.set(c.v, { opacity: 0 });
                if (hot && c.fill) gsap.set(c.fill, { opacity: 0 });
                if (filledAtCut) {
                  tl.set(vN, { opacity: 1 }, T(tS));
                  if (fN) tl.set(fN, { opacity: 1, scaleX: 1 }, T(tS));
                  return;
                }
                if (fN) gsap.set(fN, { opacity: 1, scaleX: 0 });
                const run = c.c.run ? C(c.c.run, null) : null;
                if (c.race && run != null && run < tc - f(6)) {
                  // CARRERA: la barra corre desde `run` hasta su cifra con un contador de minutos (la que tarda más,
                  // tarda más de verdad); la cifra queda en la palabra
                  const tR = Math.max(tS, run);
                  if (qLvl) ft(tl, c.q, { opacity: qLvl }, { opacity: 0, duration: f(4), ease: E.exit }, tR);
                  ft(tl, vN, { opacity: 0 }, { opacity: 1, duration: f(4), ease: E.enter }, tR);
                  gx.countText(tl, vN, { from: 0, to: c.n, at: tR, dur: Math.max(0.4, tc - tR), ease: "power1.in", fmt: fmtMin, reserve: false });
                  if (fN) ft(tl, fN, { scaleX: 0 }, { scaleX: 1, duration: Math.max(0.4, tc - tR), ease: "power1.in" }, tR);
                  gx.ev(ctx, "value", tc);
                  return;
                }
                const tLand = c.hero ? tc + 0.75 : tc;
                if (c.hero) {
                  // HÉROE: la cifra entra GRANDE sobre el marcador velado y vuela a su celda (FLIP con escala)
                  const hSize = Math.min(S(170), Math.floor(S(170) * A.w * 0.92 / Math.max(1, textW(c.v, S(170)))));
                  c.hero.style.fontSize = hSize + "px";
                  const box = gx.rel(c.box, wrap);
                  const dx = R(box.x + box.w / 2 - A.w / 2), dy = R(box.y + box.h / 2 - (hy + S(100))), k = vSize / hSize;
                  ft(tl, veil, { opacity: 0 }, { opacity: 0.8, duration: f(4), ease: E.enter }, tc - f(1));
                  ft(tl, c.hero, { opacity: 0, y: S(26), scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: f(6), ease: E.enter }, tc);
                  ft(tl, c.hero, { x: 0, y: 0, scale: 1 }, { x: dx, y: dy, scale: k, duration: f(9), ease: E.move }, tLand - f(9));
                  ft(tl, c.hero, { opacity: 1 }, { opacity: 0, duration: f(1), ease: E.exit }, tLand);
                  ft(tl, veil, { opacity: 0.8 }, { opacity: 0, duration: f(8), ease: E.exit }, tLand - f(8));
                  if (qLvl) ft(tl, c.q, { opacity: qLvl }, { opacity: 0, duration: f(3), ease: E.exit }, tc);
                  if (qOn) tl.set(c.q, { opacity: 0 }, T(tLand));
                  tl.set(vN, { opacity: 1 }, T(tLand));
                } else {
                  if (qLvl) ft(tl, c.q, { opacity: qLvl, y: 0 }, { opacity: 0, y: -S(16), duration: f(4), ease: E.exit }, tc - f(1));
                  if (qOn) tl.set(c.q, { opacity: 0 }, T(tc + f(4)));
                  ft(tl, vN, { opacity: 0, y: S(22) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, tc);
                }
                // con héroe la barra arranca bajo el velo mientras la cifra vuela (acaba ≈0,1 s después de aterrizar: la
                // última cifra de un bloque cae a ~1 s del corte y la barra tiene que verse llena)
                if (fN) {
                  const bt = c.hero ? tc + 0.3 : tLand;
                  const bd = f(Math.round(c.hero ? 8 + 8 * c.ratio : c.race ? 12 + 30 * c.ratio : 10 + 16 * c.ratio));
                  ft(tl, fN, { scaleX: 0 }, { scaleX: 1, duration: bd, ease: E.move }, bt);
                }
                gx.ev(ctx, hot ? "highlight" : "value", tc);
              });
            });
            // pasos: el foco (oro) pasa a unas celdas; las demás se atenúan si dim (solo se anima lo que cambia)
            const stt = {};
            trows.forEach((tr) => tr.cells.forEach((c) => { stt[c.key] = { hot: !!c.c.hot, dim: false }; }));
            (props.steps || []).forEach((stp, k) => {
              const t = Math.max(tS + f(2), C(stp.cue || "s" + k, tS + 0.5 + k * 0.8));
              const hot = new Set(stp.hot || []);
              let any = false;
              trows.forEach((tr) => tr.cells.forEach((c) => {
                if (!c.v) return;
                const s0 = stt[c.key], h1 = hot.has(c.key), d1 = !h1 && !!stp.dim;
                if (h1 && !s0.hot) {
                  ft(tl, c.vh, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, t);
                  ft(tl, c.v, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.enter }, t);
                  if (c.fillH) { gsap.set(c.fillH, { scaleX: 1 }); ft(tl, c.fillH, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, t); }
                  any = true;
                } else if (!h1 && s0.hot) {
                  ft(tl, c.vh, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.enter }, t);
                  ft(tl, c.v, { opacity: 0 }, { opacity: 1, duration: f(6), ease: E.enter }, t);
                  if (c.fillH) ft(tl, c.fillH, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.enter }, t);
                }
                if (d1 !== s0.dim) {
                  const nodes = [c.box, c.track].filter(Boolean);
                  ft(tl, nodes, { opacity: d1 ? 1 : 0.38 }, { opacity: d1 ? 0.38 : 1, duration: f(6), ease: E.enter }, t);
                }
                stt[c.key] = { hot: h1, dim: d1 };
              }));
              if (any) gx.ev(ctx, "highlight", t);
            });
          }

          // ── CARRILES (geometría tras ajustar los nombres: el raíl nace bajo la baldosa de su ficha)
          if (mode === "lanes") {
            tlanes.forEach((ln) => {
              const h = heads[ln.i], rt = gx.rel(h.tile, wrap);
              const rx = R(rt.x + rt.w / 2), yTop = R(rt.y + rt.h);
              const lx = R(rx + S(44)), lw = R((ln.i + 1) * colW - lx - S(10));
              const yEnd = ln.pts.length ? ln.pts[ln.pts.length - 1].y : yTop;
              Object.assign(ln.ghost.style, { left: R(rx - S(3)) + "px", top: yTop + "px", height: Math.max(2, yEnd - yTop) + "px" });
              let yPrev = yTop;
              ln.pts.forEach((p) => {
                Object.assign(p.seg.style, { left: R(rx - S(3)) + "px", top: yPrev + "px", height: Math.max(2, p.y - yPrev) + "px" });
                if (p.p.kind === "stop") Object.assign(p.mark.style, { left: R(rx - S(34)) + "px", top: R(p.y - S(7)) + "px" });
                else [p.mark, p.markH, p.gnode].forEach((n) => Object.assign(n.style, { left: R(rx - S(15)) + "px", top: R(p.y - S(15)) + "px" }));
                Object.assign(p.lab.style, { left: lx + "px", top: R(p.y - S(38)) + "px", width: lw + "px", height: S(76) + "px" });
                gx.fit(p.lab, { max: S(p.p.kind === "stop" ? 46 : 54), min: 34, width: lw, lines: 2 });
                yPrev = p.y + (p.p.kind === "stop" ? S(7) : S(15));
              });
              // esqueleto: raíl y nodos en fantasma desde el corte (la estructura se ve; los rótulos llegan en su palabra)
              tl.set(ln.ghost, { opacity: 1 }, T(tS));
              ln.pts.forEach((p) => { if (p.gnode) tl.set(p.gnode, { opacity: 1 }, T(tS)); });
            });
            let prevHot = null;
            tlanes.forEach((ln, li) => {
              let tPrev = tS, lastHot = null;
              ln.pts.forEach((p, k) => {
                const tp = Math.max(tS + f(2), C(p.p.cue || `l${li}p${k}`, tS + 0.5 + k * 0.6), tPrev + f(4));
                if (k === 0 && li > 0 && props.dim !== false) {
                  ft(tl, tlanes[li - 1].g, { opacity: 1 }, { opacity: 0.42, duration: f(8), ease: E.enter }, tp - f(4));
                  ft(tl, heads[li - 1].b, { opacity: 1 }, { opacity: 0.5, duration: f(8), ease: E.enter }, tp - f(4));
                  if (prevHot) ft(tl, prevHot, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.exit }, tp - f(4));
                }
                // el raíl corre desde `draw` (si lo hay) o en los 6 f previos al nodo
                const tDraw = p.p.draw ? Math.max(tPrev, C(p.p.draw, tp - f(6))) : Math.max(tPrev, tp - f(6));
                ft(tl, p.seg, { scaleY: 0 }, { scaleY: 1, duration: Math.max(f(4), tp - tDraw), ease: E.move }, tDraw);
                if (p.p.kind === "stop") {
                  ft(tl, p.mark, { opacity: 0, scaleX: 0.3 }, { opacity: 1, scaleX: 1, duration: f(6), ease: E.pop }, tp);
                  ft(tl, p.lab, { opacity: 0, x: -S(14) }, { opacity: 1, x: 0, duration: f(7), ease: E.enter }, tp + f(1));
                  gx.ev(ctx, "stop", tp);
                } else {
                  ft(tl, p.mark, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(6), ease: E.pop }, tp);
                  ft(tl, p.markH, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: f(6), ease: E.pop }, tp);
                  ft(tl, p.lab, { opacity: 0, x: -S(14) }, { opacity: 1, x: 0, duration: f(7), ease: E.enter }, tp + f(1));
                  if (lastHot) ft(tl, lastHot, { opacity: 1 }, { opacity: 0, duration: f(5), ease: E.exit }, tp);
                  lastHot = p.markH;
                  gx.ev(ctx, p.p.kind === "done" ? "highlight" : "node", tp);
                }
                tPrev = tp;
              });
              prevHot = lastHot;
            });
          }

          // ── PICK
          if (mode === "pick") {
            tcols.forEach((c, i) => {
              const h = heads[i];
              if (c.cl.built) {   // viene de la instancia anterior: criterios ya puestos (y su anillo, si `ring`)
                tl.set(c.its.map((x) => x.n), { opacity: 1 }, T(tS));
                if (c.cl.ring !== false) tl.set(h.ring, { opacity: 1 }, T(tS));
                return;
              }
              let tFirst = null;
              c.its.forEach((x, k) => {
                const tk = Math.max(tS + f(1), C(x.it.cue || `p${i}i${k}`, tS + 0.4 + k * 0.5));
                if (tFirst == null) tFirst = tk;
                ft(tl, x.n, { opacity: 0, y: S(24) }, { opacity: 1, y: 0, duration: f(7), ease: E.enter }, tk);
                gx.ev(ctx, "row", tk);
              });
              if (i > 0 && tFirst != null && props.dim !== false) {
                // el foco pasa a B: los criterios de A y su anillo se apagan (siguen leyéndose)
                ft(tl, tcols[i - 1].g, { opacity: 1 }, { opacity: 0.42, duration: f(8), ease: E.enter }, tFirst - f(3));
                ft(tl, heads[i - 1].b, { opacity: 1 }, { opacity: 0.55, duration: f(8), ease: E.enter }, tFirst - f(3));
                ft(tl, heads[i - 1].ring, { opacity: 1 }, { opacity: 0, duration: f(6), ease: E.exit }, tFirst - f(3));
              }
              const tb0 = C(c.cl.cue || "p" + i, null);
              if (tb0 == null) return;
              const tb = Math.max(tS + f(2), tb0);
              ft(tl, h.ring, { opacity: 0, scale: 1.12 }, { opacity: 1, scale: 1, duration: f(7), ease: E.enter }, tb);
              ft(tl, h.tile, { scale: 1 }, { scale: 1.08, duration: f(5), ease: E.move, yoyo: true, repeat: 1 }, tb);
              gx.ev(ctx, "pick", tb);
            });
          }

          gx.bgIn(tl, bd, t0, t1, 71, props);
          gx.out(tl, props, t1, [wrap], { dur: f(5), ctx });
        },
      };
    },
  });
})(window.CK);
