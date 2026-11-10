/* cutkit · subtítulos
 *
 * caption.rail   — página de 1–3 palabras en el raíl (junta del split, debajo de la tarjeta o y≈0,58·H).
 *                  Las palabras se colocan ya maquetadas y aparecen EN SU SITIO al decirse (0–2 f antes) con un pop
 *                  corto sin rebote. Énfasis: "accent" (oro), "scale" (más grande y negra), "hero" (Montserrat 800
 *                  ~1,5× en su propia línea, revelada letra a letra). Sale en corte (lo hace HF al acabar el clip).
 * caption.lockup — el héroe del gancho: conectores en Montserrat 800 + 1 palabra/frase en Montserrat 900 ~1,75× que se
 *                  revela letra a letra (≈30 ms/letra, repartido sobre la duración hablada), pegada a la línea.
 * Regla de estilo: fuera toda serif cursiva. El énfasis va con peso
 *                  (800–900), tamaño u oro; `emphasis: "hero"` sigue existiendo y ya no cambia de familia.
 *
 * Props comunes: words:[{text,t0,t1,emphasis,color?}], y (fracción de H, se usa si el layout no fija raíl).
 * Recetas: tipografia_recetas.js (charRevealSerif → revelado letra a letra, emphasisPop) sin SplitText ni callbacks.
 */
(function () {
  'use strict';
  const U = CK.util;
  const E = CK.ease;            // enter · exit · move · pop (fuente única: runtime.js)
  // heroScale: 2,3 con la serif (133 px); con Montserrat 800, 1,52 → 88 px a 58 (dirección de arte §2.5: destacado 88)
  const CAP = { size: 58, weight: 800, heroScale: 1.52, scaleScale: 1.32, lead: 1 };

  /** tema del subtítulo según el layout del instante: claro (paper/white/accent/hex claro) → tinta sin sombra.
   *  En el split el subtítulo va sobre la cara: siempre oscuro (blanco con sombra). */
  function lightAt(ctx, t) {
    const L = ctx.layoutAt(t + 1e-3);
    if (!L || !L.geom) return false;
    // split: el subtítulo va CENTRADO en la línea (mitad sobre el panel, mitad sobre el vídeo) → blanco con sombra suave
    if (L.name === 'layout.split_top') return false;
    return !!L.geom.light;
  }
  function themeVars(light) {
    if (!light) {
      // sobre la cara/oscuro: brand = blanco con subrayado del color de marca (magenta sobre piel se pierde)
      return { '--cap-fg': '#FFFFFF', '--cap-shadow': 'var(--ck-text-shadow)', '--cap-shadow-hero': 'var(--ck-text-shadow-hero)',
        '--cap-accent': 'var(--ck-accent)', '--cap-mark': 'rgba(254, 202, 26, 0)',
        '--cap-brand': '#FFFFFF', '--cap-brand-line': 'var(--ck-accent-2)' };
    }
    // sobre papel/rosa/claro: oro como MARCADOR detrás (texto oro sobre papel da ~1,4:1); brand en tinta (magenta sobre
    // rosa da 1,3:1), sin subrayado
    return { '--cap-fg': '#0F0D10', '--cap-shadow': 'none', '--cap-shadow-hero': 'none',
      '--cap-accent': '#0F0D10', '--cap-mark': 'var(--ck-accent)',
      '--cap-brand': '#0F0D10', '--cap-brand-line': 'transparent' };
  }
  /** variables completas del estilo (tema + junta del split): el contorno va SIEMPRE explícito (0 fuera de la junta),
 * para que un cambio de layout dentro de una página lo quite (una página que cruzaba 50/50 → pantalla
   *  completa clara salía 5 f como mancha negra: relleno tinta + contorno negro del estilo de la junta) */
  function styleVars(light, seam) {
    const v = themeVars(light);
    v['--cap-stroke-w'] = '0px'; v['--cap-stroke-c'] = 'rgba(11,11,12,0)';
    // sobre la línea del split: sombra algo más densa para leerse también sobre el panel claro
    if (seam && !light) {
      v['--cap-shadow'] = '0 1px 2px rgba(0,0,0,.55), 0 3px 14px rgba(0,0,0,.42)'; v['--cap-shadow-hero'] = v['--cap-shadow'];
      // contorno oscuro fino (≈3 px visibles: trazo de 6 px pintado DEBAJO del relleno) → se lee igual sobre panel
      // blanco, panel negro y vídeo, sin engordar la letra
      v['--cap-stroke-w'] = '6px'; v['--cap-stroke-c'] = '#0B0B0C';
    }
    return v;
  }
  function applyTheme(el, light, seam) {
    const v = styleVars(light, seam);
    Object.keys(v).forEach((k) => el.style.setProperty(k, v[k]));
  }
  /** caja de TINTA de un bloque de líneas (px respecto a `ref`): línea base de cada línea (marcador) ± ascendente/descendente
   *  reales del texto (canvas measureText con la fuente calculada de cada palabra) */
  let inkCanvas = null;
  function inkBox(ref, lines) {
    inkCanvas = inkCanvas || document.createElement('canvas').getContext('2d');
    const r0 = ref.getBoundingClientRect().top;
    let top = Infinity, bottom = -Infinity;
    lines.forEach((L) => {
      const mk = U.el('span', 'ck-basemark', L, { display: 'inline-block', width: '0px', height: '0px', verticalAlign: 'baseline' });
      const base = mk.getBoundingClientRect().top - r0;
      mk.remove();
      const words = Array.from(L.querySelectorAll('.ck-word'));
      (words.length ? words : [L]).forEach((w) => {
        const cs = getComputedStyle(w);
        inkCanvas.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        const m = inkCanvas.measureText(w.textContent || '');
        top = Math.min(top, base - (m.actualBoundingBoxAscent || parseFloat(cs.fontSize) * 0.72));
        bottom = Math.max(bottom, base + (m.actualBoundingBoxDescent || 0));
      });
    });
    return { top, bottom };
  }
  /** ¿junta del split en t? (el subtítulo va centrado en la línea, con contorno) */
  function seamAt(ctx, t) {
    const L = ctx.layoutAt(t + 1e-3);
    return !!(L && L.name === 'layout.split_top');
  }
  /** cambios de estilo dentro de [a, b): tema (cara → panel claro) o junta (50/50 → pantalla completa y al revés). Se
   *  reestila EN el fotograma del corte de layout */
  function themeSwitches(ctx, a, b) {
    const out = [];
    let cur = lightAt(ctx, a), curS = seamAt(ctx, a);
    (CK.segments || []).forEach((sg) => {
      if (sg.t0 > a + 1e-3 && sg.t0 < b - 1e-3) {
        const l = lightAt(ctx, sg.t0), sm = seamAt(ctx, sg.t0);
        if (l !== cur || sm !== curS) { out.push({ at: U.snap(sg.t0), light: l, seam: sm, fromLight: cur, fromSeam: curS }); cur = l; curS = sm; }
      }
    });
    return out;
  }

  const slideWindows = (ctx, a, b) => U.slideWindows(a, b);
  /** ventanas de transición (pista transition) que tocan [a, b): el texto se oculta en ellas (nunca dos textos legibles) */
  // Solo el pico de la transición (su corte ± 3 f): ocultar toda la ventana dejaba frases enteras sin subtítulo
  // (p. ej. «Por cierto» al entrar el outro). Sin cue de corte, la ventana entera.
  function transitionWindows(ctx, a, b) {
    const f3 = 3 / (ctx.fps || 30);
    // las de luz/destello/desenfoque no mueven el plano: el subtítulo sigue visible (regla de estilo: nunca un parpadeo); solo
    // las que desplazan todo el plano (barridos) lo ocultan en su pico
    const STILL = /light_leak|flash|zoom_blur|dip|fade/;
    return (ctx.spec.items || []).filter((o) => o.track === 'transition' && !STILL.test(o.component || '') && o.t1 > a + 1e-3 && o.t0 < b - 1e-3)
      .map((o) => {
        const c = o.cues && o.cues.cut != null ? +o.cues.cut : null;
        return c == null ? { a: U.snap(o.t0), b: U.snap(o.t1) } : { a: U.snap(Math.max(o.t0, c - f3)), b: U.snap(Math.min(o.t1, c + f3)) };
      });
  }
  function hideDuringTransitions(tl, el, wins) {
    wins.forEach((w) => {
      tl.fromTo(el, { opacity: 1 }, { opacity: 0, duration: 0, immediateRender: false }, w.a);
      tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0, immediateRender: false }, w.b);
    });
  }
  const rideSlides = (tl, el, wins) => U.rideSlides(tl, el, wins);

  /** raíl de cara completa bajo el mentón REAL (con el punch-in activo, anclado en el pelo): mentón + 70, hasta 1420 */
  function punchRail(ctx, lay, t, base) {
    if (!lay || lay.name !== 'layout.full_face' || !lay.geom || lay.geom.chinY == null) return base;
    // la altura va por LAYOUT: si algún corte-zoom cae en este tramo de cara, el raíl baja lo que pida el zoom más
    // cerrado en TODO el tramo (antes saltaba ~140 px a mitad de frase en el corte-zoom)
    const a = lay.t0 != null ? lay.t0 : -1e9, b = lay.t1 != null ? lay.t1 : 1e9;
    const qs = (CK.punches || []).filter((r) => r.t0 < b - 1e-3 && r.t1 > a + 1e-3);
    if (!qs.length) return base;
    const chin = Math.max(...qs.map((q) => q.Py + q.k * (lay.geom.chinY - q.Py)));
    const rc = railCfg(ctx);
    return Math.round(Math.min(rc.max, Math.max(base, chin + rc.gap)));
  }
  /** perfil `captions.rail_*` (tokens.caption_rail): raíl compartido sí/no, gráficos a pantalla completa, hueco bajo el
   *  mentón y tope. Sin tokens, los valores de siempre. */
  function railCfg(ctx) {
    if (CK.railCfg) {
      const r = CK.railCfg({ tokens: ctx.tokens });
      return Object.assign(r, { shared: !ctx.tokens || !ctx.tokens.caption_rail || ctx.tokens.caption_rail.shared !== false });
    }
    return { yFull: 0.71, gap: 70, max: 1420, shared: true };
  }
  // planos sin cara a pantalla completa que comparten el raíl de la cara
  const FULLSCREEN = { 'layout.broll_full': 1, 'layout.card_float': 1 };
  /** UN SOLO raíl para cara completa y gráficos a
   *  pantalla completa. Antes la cara iba en y≈1420 (mentón + 70 con los punch-in) y los gráficos en 1363–1382
   *  (`rail_y_full`), y el subtítulo saltaba 35–40 px en cada cambio. Raíl = el más bajo de: el de cara (fullFaceRail) y,
   *  si el vídeo tiene planos a pantalla completa, el de gráficos del perfil (`captions.rail_y_full`), con tope
   *  `captions.rail_max_px`. Más bajo = más lejos de la boca y nunca
   *  encima de un gráfico, que se coloca con el raíl de su layout (≤ este). El split va aparte (centro de la junta). */
  function sharedRail(ctx) {
    const rc = railCfg(ctx);
    let best = fullFaceRail(ctx);
    if ((CK.segments || []).some((sg) => FULLSCREEN[sg.name])) best = Math.max(best, Math.round(U.clamp(rc.yFull, 0.5, 0.78) * ctx.H));
    return best > 0 ? Math.min(rc.max, best) : 0;
  }
  /** UN SOLO raíl de cara completa en todo el vídeo, con o sin punch-in: el más
   *  bajo de todos los tramos de cara (cada uno: mentón + 70, o lo que pida su zoom más cerrado), hasta 1420. Antes cada
   *  tramo tenía el suyo (≈1300 sin punch, ≈1415 con punch) y el subtítulo saltaba ~115 px de un plano de cara a otro.
   *  Los tramos con `rail_y` explícito en su layout lo conservan. Sin caché: los punch-in se registran al montar la cámara. */
  function fullFaceRail(ctx) {
    let best = 0;
    (CK.segments || []).forEach((sg) => {
      if (sg.name !== 'layout.full_face' || !sg.geom || sg.geom.chinY == null || (sg.props && sg.props.rail_y != null)) return;
      const lay = ctx.layoutAt(sg.t0 + 1e-3);
      if (!lay || lay.name !== 'layout.full_face') return;
      best = Math.max(best, punchRail(ctx, lay, sg.t0, lay.railY));
    });
    return best;
  }
  function railYFor(ctx, p, t) {
    const lay0 = ctx.layoutAt(t + 1e-3);
    const own = punchRail(ctx, lay0, t, railYBase(ctx, p, t));
    if (!lay0 || p.rail === 'fixed') return own;
    const shared = railCfg(ctx).shared;
    if (lay0.name === 'layout.full_face') {
      if (lay0.props && lay0.props.rail_y != null) return own;       // raíl explícito del plan: fuera de la regla
      const one = shared ? sharedRail(ctx) : fullFaceRail(ctx);
      return one > 0 ? Math.max(own, one) : own;
    }
    // gráficos a pantalla completa: el mismo raíl que la cara (un `rail_y_full` explícito solo puede bajarlo)
    if (shared && FULLSCREEN[lay0.name]) {
      const one = sharedRail(ctx);
      return one > 0 ? Math.max(own, one) : own;
    }
    return own;
  }
  function railYBase(ctx, p, t) {
    const lay = ctx.layoutAt(t + 1e-3);
    if (p.rail === 'fixed' && p.y != null) return Math.round(p.y * ctx.H);
    if (lay.geom && lay.geom.railExplicit) return lay.railY;
    if (p.y != null) return Math.round(p.y * ctx.H);
    return lay.railY;
  }
  function textOf(w, p) {
    let t = U.cleanWord(w.text);
    if (p.case === 'lower') t = t.toLowerCase();
    if (p.case === 'upper') t = t.toUpperCase();
    return t;
  }
  /** agrupa palabras en líneas: corridas de "hero" van en su línea; el resto, juntas */
  function groupLines(words) {
    const lines = [];
    words.forEach((w) => {
      const type = w.emphasis === 'hero' ? 'hero' : 'reg';
      const last = lines[lines.length - 1];
      if (last && last.type === type) last.words.push(w); else lines.push({ type, words: [w] });
    });
    return lines;
  }
  /** revela letras sincronizadas con la voz (receta charRevealSerif adaptada; hoy en Montserrat) */
  function charReveal(tl, chars, at, spoken, fps) {
    const n = chars.length;
    if (!n) return at;
    const each = U.clamp((spoken || n * 0.03) / n, 0.018, 0.07);
    const dur = 7 / fps;
    tl.fromTo(chars, { opacity: 0, yPercent: 22, filter: 'blur(10px)' },
      { opacity: 1, yPercent: 0, filter: 'blur(0px)', duration: dur, ease: E.enter, stagger: { each }, immediateRender: false }, at);
    const end = at + each * (n - 1) + dur;
    tl.set(chars, { filter: 'none' }, end + 1e-3);
    return end;
  }

  // ───────────────────────── caption.rail
  CK.register('caption.rail', {
    kind: 'caption',
    mount(root, p, ctx) {
      const it = ctx.item;
      const pages = p.pages && p.pages.length ? p.pages : [{ words: p.words || [], t0: it.t0, t1: it.t1 }];
      const size = p.size || CAP.size;
      const built = [];
      pages.forEach((pg, pi) => {
        let words = (pg.words || []).filter((w) => U.cleanWord(w.text));
        if (!words.length) return;
        const pgT0 = pg.t0 != null ? pg.t0 : it.t0;
        const layP = ctx.layoutAt(pgT0 + 1e-3);
        if (layP.name === 'layout.full_face' || layP.name === 'layout.split_top') {
          // raíl en cara completa (y≈1200): no hay sitio bajo la barbilla para una línea héroe → 900 1,35× en línea
          words = words.map((w) => (w.emphasis === 'hero' ? Object.assign({}, w, { emphasis: 'scale', _heroAlt: true }) : w));
        }
        const page = U.el('div', 'ck-cap-page', root);
        page.setAttribute('data-ck-text', 'caption');
        // centrado en x=540; el raíl está por debajo de y=1000 → ancho simétrico respecto a la derecha de 192 px
        const capW = ctx.safeCenteredW ? ctx.safeCenteredW(ctx.H) : ctx.safeRect.w;
        Object.assign(page.style, { left: Math.round((ctx.W - capW) / 2) + 'px', width: capW + 'px', top: '0px', zIndex: String(ctx.z) });
        const vis = U.el('div', 'ck-cap-vis', page);          // se oculta durante los deslizados del split
        const trh = U.el('div', 'ck-cap-tr', vis);            // se oculta durante las transiciones (luz, whip…)
        const inner = U.el('div', 'ck-cap-inner', trh);
        if (p.plate === 'pill') inner.classList.add('ck-cap-pill');
        inner.style.fontSize = size + 'px';
        const spans = [];
        let anchor = null;
        groupLines(words).forEach((ln) => {
          const L = U.el('div', 'ck-cap-line ' + (ln.type === 'hero' ? 'ck-cap-hero' : 'ck-cap-reg'), inner);
          ln.words.forEach((w, i) => {
            if (i > 0) L.appendChild(document.createTextNode(' '));
            const s = U.el('span', 'ck-word', L, null, textOf(w, p));
            if (w.emphasis === 'accent') s.classList.add('ck-cap-accent');
            if (w.emphasis === 'brand') s.classList.add('ck-cap-brand');
            if (w.emphasis === 'scale') s.classList.add('ck-cap-scale');
            if (w._heroAlt) s.classList.add('ck-cap-heroalt');
            if (w.color) s.style.color = U.color(w.color);
            spans.push({ s, w, hero: ln.type === 'hero' });
          });
          if (ln.type === 'hero') {
            U.fitText(L, capW, Math.round(size * CAP.heroScale), Math.round(size * 1.1));
          } else if (!anchor) anchor = L;
          if (ln.type !== 'hero') U.fitText(L, capW, size, 44);
        });
        if (!anchor) anchor = inner.firstChild;
        // posición vertical: la primera línea normal centrada en el raíl; el resto cuelga.
        // Se evalúa en CADA tramo de layout que cruza la página (una página que cruza split→cara cambia de raíl en el corte).
        const aMid = anchor.offsetTop + anchor.offsetHeight / 2;
        const ph = inner.offsetHeight;
        // borde inferior de la TINTA de la última línea respecto a la página: línea base (+ descendentes si los hay)
        const lastLine = inner.lastElementChild;
        const mk = U.el('span', 'ck-basemark', lastLine, { display: 'inline-block', width: '0px', height: '0px', verticalAlign: 'baseline' });
        const baseOff = mk.getBoundingClientRect().top - page.getBoundingClientRect().top;
        mk.remove();
        const lastPx = Math.max.apply(null, Array.from(lastLine.querySelectorAll('.ck-word')).map((w) => parseFloat(getComputedStyle(w).fontSize) || size));
        const inkBottom = baseOff + (/[gjpqyç,;]/.test(lastLine.textContent) ? 0.21 * lastPx : 0);
        const ink = inkBox(page, Array.from(inner.querySelectorAll('.ck-cap-line')));
        const topFor = (y, t) => {
          const L = ctx.layoutAt(t + 1e-3);
          const maxBottom = (L.geom && L.geom.railMaxBottom) || (ctx.H - ctx.safe.bottom);
          // split: el BLOQUE entero centrado en la línea de la junta (la héroe no cuelga
          // hacia la cara); resto: la primera línea normal en el raíl y la héroe debajo, sin pasar de la zona segura
          if (L.name === 'layout.split_top') {
            // Centrado EXACTO en el corte: el CENTRO de la caja de tinta cae en la línea (mitad arriba, mitad abajo)
            const c = (L.geom && L.geom.railInkCenter != null) ? L.geom.railInkCenter : (L.seamY || 960);
            return Math.round(c - (ink.top + ink.bottom) / 2);
          }
          let top = Math.round(L.name === 'layout.split_top' ? y - ph / 2 : y - aMid);
          if (top + ph > maxBottom) top = maxBottom - ph;      // si no cabe por abajo, la línea héroe sube
          return Math.max(ctx.safe.top, top);
        };
        const pa = pg.t0 != null ? pg.t0 : it.t0, pb = pg.t1 != null ? pg.t1 : it.t1;
        const top0 = topFor(railYFor(ctx, p, pa), pa);
        page.style.top = top0 + 'px';
        const moves = [];
        // el raíl cambia en cada corte de layout y al empezar/acabar un punch-in (el mentón baja con el zoom)
        const cuts = [];
        (CK.segments || []).forEach((sg) => cuts.push(sg.t0));
        (CK.punches || []).forEach((q) => { cuts.push(q.t0); cuts.push(q.t1); });
        cuts.filter((c) => c > pa + 1e-3 && c < pb - 1e-3).sort((x, y) => x - y).forEach((c) => {
          moves.push({ at: U.snap(c), dy: topFor(railYFor(ctx, p, c), c) - top0 });
        });
        applyTheme(page, lightAt(ctx, pa), ctx.layoutAt(pa + 1e-3).name === 'layout.split_top');
        const themes = themeSwitches(ctx, pa, pb);
        // geometría de cada línea para la revelación centrada
        const lineGeo = Array.from(inner.querySelectorAll('.ck-cap-line')).map((L) => {
          const ws = Array.from(L.querySelectorAll(':scope > .ck-word'));
          if (!ws.length) return null;
          const left = ws[0].offsetLeft, right = ws[ws.length - 1].offsetLeft + ws[ws.length - 1].offsetWidth;
          return { L, ws, left, right };
        }).filter(Boolean);
        // letras de las palabras héroe
        spans.forEach((o) => { if (o.hero) o.chars = U.splitChars(o.s); });
        gsap.set(spans.map((o) => o.s), { opacity: 0 });
        if (p.plate === 'pill') gsap.set(inner, { opacity: 0 });
        built.push({ page, vis, trh, inner, spans, moves, themes, lineGeo, slides: slideWindows(ctx, pa, pb), t0: pa, t1: pb, multi: pages.length > 1, idx: pi });
      });
      return {
        animate(tl, t0, t1) {
          const fps = ctx.fps, pop = 4 / fps, lead = (p.lead_frames != null ? p.lead_frames : CAP.lead) / fps;
          const holds = (CK.captionHolds || []).filter((h) => h.t1 > t0 && h.t0 < t1);
          const afterHold = (t) => { holds.forEach((h) => { if (t >= h.t0 - 1e-3 && t < h.t1) t = h.t1; }); return t; };
          built.forEach((B, bi) => {
            const nb = built[bi + 1];
            // varias páginas en un item: la saliente se apaga 1 f antes de que entre la siguiente (nunca dos a la vez)
            const pt0 = U.snap(Math.max(t0, B.t0));
            const pt1 = U.snap(Math.min(t1, B.t1, nb ? Math.max(B.t0 + 1 / ctx.fps, nb.t0) : Infinity));   // relevo en el mismo fotograma
            if (B.multi) {
              // varias páginas en un mismo item: cada página se enciende y se apaga en seco
              gsap.set(B.page, { opacity: 0 });
              tl.set(B.page, { opacity: 1 }, pt0);
              tl.set(B.page, { opacity: 0 }, pt1);
            }
            if (B.moves.length) {
              gsap.set(B.page, { y: 0 });
              let prev = 0;
              B.moves.forEach((mv) => {
                if (mv.dy !== prev) { tl.fromTo(B.page, { y: prev }, { y: mv.dy, duration: 0, immediateRender: false }, mv.at); prev = mv.dy; }
              });
            }
            // NUNCA visibility: un hijo con visibility:visible anula el hidden con el que HF oculta el clip (dejaba
            // páginas viejas en pantalla). Al entrar un split deslizando, el subtítulo se oculta hasta que el panel ha
            // recorrido ≥ 60 % y aparece en la junta con un pop de 4 f (si viajase con el panel saldría recortado arriba).
            // al entrar un split deslizando, el subtítulo ya está en la junta desde el primer fotograma (antes se ocultaba
            // ~4 f hasta que el panel recorría el 60 %: se veía como parpadeo en cada entrada al 50/50)
            if (B.slides.length) gsap.set(B.vis, { y: 0, opacity: 1 });
            const trw = transitionWindows(ctx, B.t0, B.t1);
            if (trw.length) { gsap.set(B.trh, { opacity: 1 }); hideDuringTransitions(tl, B.trh, trw); }
            B.themes.forEach((th) => {
              const from = styleVars(th.fromLight, th.fromSeam), to = styleVars(th.light, th.seam);
              tl.fromTo(B.page, from, Object.assign({}, to, { duration: 0, immediateRender: false }), th.at);
            });
            if (p.plate === 'pill') tl.fromTo(B.inner, { opacity: 0 }, { opacity: 1, duration: pop, ease: E.enter, immediateRender: false }, pt0);
            const reveal = p.reveal || 'word';
            const shown = new Map();                                // span → instante en que aparece
            B.spans.forEach((o, i) => {
              let wt = reveal === 'page' ? pt0 : U.snap(Math.max(pt0, (o.w.t0 != null ? o.w.t0 : pt0) - lead));
              // la primera palabra de la página entra con la página: si esperase a decirse, el subtítulo quedaría
              // vacío 2–5 f entre frases (parpadeo entre frases)
              if (i === 0 && wt - pt0 < 0.6) wt = pt0;
              wt = U.snap(afterHold(wt));
              if (wt >= pt1 - 1e-3) return;                         // tapado entero por el lockup: no se muestra
              shown.set(o.s, wt);
              if (o.hero) {
                tl.set(o.s, { opacity: 1 }, wt);
                gsap.set(o.chars, { opacity: 0 });
                charReveal(tl, o.chars, wt, (o.w.t1 || wt + 0.35) - (o.w.t0 || wt), fps);
              } else if (i === 0 && wt <= pt0 + 1e-3) {
                // primera palabra de la página en su primer fotograma: ya visible (relevo seco de frase, sin hueco)
                tl.fromTo(o.s, { opacity: 1, scale: o.w.emphasis === 'scale' ? 1.1 : 0.96 }, { opacity: 1, scale: 1, duration: pop, ease: E.enter, immediateRender: false }, wt);
              } else if (o.w.emphasis === 'scale') {
                tl.fromTo(o.s, { opacity: 0, scale: 1.22 }, { opacity: 1, scale: 1, duration: 5 / fps, ease: E.enter, immediateRender: false }, wt);
              } else {
                tl.fromTo(o.s, { opacity: 0, y: 10, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: pop, ease: E.enter, immediateRender: false }, wt);
              }
            });
            // revelación centrada: la línea se desplaza para que lo ya dicho quede centrado en x=540
            // (con `build: "in_place"` las palabras aparecen en su sitio definitivo, como en las referencias)
            if ((p.build || 'center') === 'center' && reveal !== 'page') {
              B.lineGeo.forEach((g) => {
                const steps = [];
                g.ws.forEach((w) => {
                  const at = shown.get(w);
                  if (at == null) return;
                  const off = Math.round((g.right - (w.offsetLeft + w.offsetWidth)) / 2);
                  const last = steps[steps.length - 1];
                  // palabras a < 3 f una de otra: un solo desplazamiento (dos tweens de x solapados se pisan al buscar
                  // fotogramas hacia atrás y la línea salta ±90 px fotograma a fotograma: el «parpadeo» de «difícil»)
                  if (last && at - last.at < 3 / fps - 1e-3) last.off = off; else steps.push({ at, off });
                });
                if (!steps.length) return;
                gsap.set(g.L, { x: steps[0].off });
                // el desplazamiento ACABA cuando aparece la palabra (empieza d
                // antes): la línea ya le ha hecho sitio y la palabra nace en su sitio, sin deslizarse con ella. Antes
                // empezaba en su aparición y la palabra recorría ~½ ancho durante 3 f. Nunca antes del paso anterior.
                for (let k = 1; k < steps.length; k++) {
                  const d = Math.min(3 / fps, steps[k].at - steps[k - 1].at);
                  if (steps[k].off === steps[k - 1].off) continue;
                  tl.fromTo(g.L, { x: steps[k - 1].off }, { x: steps[k].off, duration: d, ease: E.enter, immediateRender: false }, steps[k].at - d);
                }
              });
            }
          });
        },
      };
    },
  });

  // ───────────────────────── caption.lockup
  /** Construye grupos {type: line|hero|big, words} desde words[] (o desde props.lines/hero) */
  function lockupGroups(p) {
    if (p.lines || p.hero) {
      const g = (p.lines || []).map((l) => ({ type: l.weight === 'black' ? 'big' : 'line', words: [{ text: l.text, t0: l.t0, t1: l.t1, color: l.color }], weight: l.weight }));
      if (p.hero) {
        const h = { type: 'hero', words: [{ text: p.hero.text, t0: p.hero.t0, t1: p.hero.t1, color: p.hero.color }] };
        if (p.hero_position === 'above') g.unshift(h); else g.push(h);
      }
      return g;
    }
    const words = (p.words || []).filter((w) => U.cleanWord(w.text));
    const runs = [];
    let cur = null;
    words.forEach((w) => {
      const type = w.emphasis === 'hero' ? 'hero' : w.emphasis === 'scale' ? 'big' : 'line';
      if (!cur || cur.type !== type) { cur = { type, words: [] }; runs.push(cur); }
      cur.words.push(w);
    });
    // las corridas de conectores se parten en líneas EQUILIBRADAS (≤ max_chars por línea, sin dejar una palabra sola)
    const maxc = p.max_chars || 22;
    const groups = [];
    runs.forEach((r) => {
      if (r.type !== 'line') { groups.push(r); return; }
      const total = r.words.reduce((a, x) => a + U.cleanWord(x.text).length + 1, -1);
      const n = Math.max(1, Math.ceil(total / maxc));
      if (n === 1) { groups.push(r); return; }
      const target = total / n;
      let line = { type: 'line', words: [] }, len = -1;
      r.words.forEach((w, i) => {
        const l = U.cleanWord(w.text).length + 1;
        const left = r.words.length - i;
        if (line.words.length && len + l > target + 3 && groups.filter((g) => g.type === 'line').length < n - 1 && left >= 1) {
          groups.push(line); line = { type: 'line', words: [] }; len = -1;
        }
        line.words.push(w); len += l;
      });
      groups.push(line);
    });
    return groups;
  }

  CK.register('caption.lockup', {
    kind: 'caption',
    mount(root, p, ctx) {
      const groups = lockupGroups(p);
      const base = p.size || 62;
      const ride = U.el('div', 'ck-lk-ride', root, { position: 'absolute', inset: '0', zIndex: String(ctx.z + 5) });
      const lkTr = U.el('div', 'ck-lk-tr', ride, { position: 'absolute', inset: '0' });
      const box = U.el('div', 'ck-lockup', lkTr);
      box.setAttribute('data-ck-text', 'lockup');
      applyTheme(box, lightAt(ctx, ctx.item.t0), ctx.layout && ctx.layout.name === 'layout.split_top');
      box.setAttribute('data-layout-allow-overlap', 'true');   // la héroe se pega a la línea a propósito (margen negativo)
      const align = p.align || 'center';
      // ancho centrado en 540: si el bloque puede bajar de y=1000 (raíl, cara, junta), simétrico a la derecha de 192
      const lay0 = ctx.layout;
      const low = !(p.anchor === 'top' || p.anchor === 'center');
      const LW = low && ctx.safeCenteredW ? ctx.safeCenteredW(ctx.H) : ctx.safeRect.w;
      Object.assign(box.style, { left: Math.round((ctx.W - LW) / 2) + 'px', width: LW + 'px', top: '0px', zIndex: String(ctx.z + 5), textAlign: align });
      const lines = [];
      let lineIdx = 0;
      groups.forEach((g) => {
        const L = U.el('div', 'ck-lk-line ck-lk-' + g.type, box);
        L.setAttribute('data-layout-allow-overlap', 'true');
        const spans = [];
        g.words.forEach((w, i) => {
          if (i > 0) L.appendChild(document.createTextNode(' '));
          const s = U.el('span', 'ck-word', L, null, U.cleanWord(w.text));
          if (w.emphasis === 'accent') s.classList.add('ck-cap-accent');
          if (w.emphasis === 'brand') s.classList.add('ck-cap-brand');
          if (w.color) s.style.color = U.color(w.color);
          spans.push({ s, w });
        });
        if (g.type === 'hero') {
          if (p.hero_color) L.style.color = U.color(p.hero_color);
          // Montserrat 900: 1,75× (108 px a 62) y como mínimo 1,05× (antes, serif 2,7× / 1,6×: un 50 % más estrecha)
          U.fitText(L, LW - 20, p.hero_size || Math.round(base * 1.75), Math.round(base * 1.05));
        } else if (g.type === 'big') {
          U.fitText(L, LW, p.big_size || Math.round(base * 2.2), Math.round(base * 1.3));
        } else {
          L.style.fontSize = base + 'px';
          if (g.weight === 'light' || (p.light_second && lineIdx === 1)) L.classList.add('ck-lk-light');
          U.fitText(L, LW, base, 44);
          if (p.stagger_align && align === 'center') L.style.transform = `translateX(${lineIdx % 2 ? 36 : -36}px)`;
          lineIdx++;
        }
        lines.push({ L, g, spans });
      });
      // anclaje vertical — se calcula para CADA tramo de layout que cruza el lockup (si cruza cara → split, en el corte
      // salta a la posición del nuevo layout; nunca se queda en la de cara completa sobre los ojos del split)
      let altDone = false;
      const placeFor = (lay) => {
        let anchor = p.anchor || 'auto';
        // auto: cara completa → bajo la barbilla; split → centrado en la junta (manda SIEMPRE, aunque llegue props.y)
        if (anchor === 'auto') anchor = lay.name === 'layout.full_face' ? 'face' : lay.name === 'layout.split_top' ? 'seam' : 'rail';
        let hh = box.offsetHeight;
        if (anchor === 'face') {
          // Cara completa: arriba ≥ chinY + 12 y base ≤ 1248. Se limita el TAMAÑO (no se acerca la cara):
          // si la héroe quedaría < 64 px de cuerpo, pasa a 900 a 1,35× (línea «alt»).
          const ta = Math.max(ctx.item.t0, lay.t0 || 0), tb = Math.min(ctx.item.t1, lay.t1 || ctx.item.t1);
          const f = ctx.faceMedian(ta, tb);
          const c = lay.cam || { y: 0, scale: 1 };
          // barbilla REAL en pantalla: layout + punch-in activo (ancla y escala del punch) + zoom lento máximo
          let chinL = (f.y + f.h + 0.035) * ctx.H, mouthL = (f.y + 0.82 * f.h) * ctx.H;
          (CK.punches || []).forEach((q) => { if (q.t1 > ta + 1e-3 && q.t0 < tb - 1e-3) {
            chinL = Math.max(chinL, q.Py + q.k * ((f.y + f.h + 0.035) * ctx.H - q.Py));
            mouthL = Math.max(mouthL, q.Py + q.k * ((f.y + 0.82 * f.h) * ctx.H - q.Py)); } });
          (CK.pushes || []).forEach((q) => { if (q.t1 > ta + 1e-3 && q.t0 < tb - 1e-3) {
            chinL = Math.max(chinL, q.Py + q.k * (chinL - q.Py)); mouthL = Math.max(mouthL, q.Py + q.k * (mouthL - q.Py)); } });
          const chinY = Math.round((c.y || 0) + (c.scale || 1) * chinL);
          const mouthY = Math.round((c.y || 0) + (c.scale || 1) * mouthL);
          // tope inferior: zona segura de texto (1248) salvo que el perfil/compilador lo cambie (p. ej. 1460 = sobre la UI real)
          const zBotTok = p.bottom_y != null ? p.bottom_y : (ctx.tokens.lockup_full_bottom != null ? ctx.tokens.lockup_full_bottom : null);
          const zBot = zBotTok != null ? Math.round(zBotTok) : ((lay.geom && lay.geom.railMaxBottom) || (ctx.H - ctx.safe.bottom));
          // bajo el mentón si hay sitio (≥ 120 px); si no (punch-in), sobre el cuello y el mentón, nunca sobre la boca
          let zTop = Math.round(chinY + 12);
          if (zBot - zTop < 120) zTop = Math.min(zTop, Math.round(mouthY + 36));
          const avail = Math.max(1, zBot - zTop);
          let k = Math.min(1, avail / hh);
          const heroLines = lines.filter((o) => o.g.type === 'hero');
          const heroPx = heroLines.length ? parseFloat(heroLines[0].L.style.fontSize) || 0 : 0;
          if (!altDone && heroLines.length && heroPx * k < 64) {
            heroLines.forEach((o) => { o.g.type = 'big'; o.L.className = 'ck-lk-line ck-lk-alt'; U.fitText(o.L, LW, Math.round(base * 1.35), 44); });
            altDone = true;
            hh = box.offsetHeight;
            k = Math.min(1, avail / hh);
          }
          k = Math.max(0.55, k);                                 // por debajo de 0,55 no se lee: la base sigue en 1248
          ctx.item._ckLockupFit = { chinY, avail, scale: +k.toFixed(2), alt: altDone };
          return { top: Math.round(zBot - hh / 2 - (k * hh) / 2), scale: k };
        }
        if (anchor === 'seam') {
          // Centrado en la línea de la junta (railY = J − F/2); si no cabe en la banda simétrica entre el recurso del
          // panel y esa línea, se escala desde el centro (≥ 0,6). Nunca cuelga hacia la cara.
          // Con la cabeza entera bajo la junta no cabe un lockup centrado en la línea sin pisar el pelo: la BASE queda
          // en J+8 (nunca sobre el pelo, que empieza en J+16) y el bloque crece hacia arriba sobre el panel, como mucho
          // 230 px por encima de la junta; si no cabe, se escala desde la base (≥ 0,7).
          // centrado en la línea del split (como los subtítulos): el centro de su caja de tinta en J
          const J = (lay.geom && lay.geom.lockCenter) || lay.seamY || 960;
          const ib = inkBox(box, Array.from(box.querySelectorAll('.ck-lk-line')));
          const inkH = ib.bottom - ib.top, maxH = 240;
          const k = inkH > maxH ? Math.max(0.7, maxH / inkH) : 1;
          const cy = (ib.top + ib.bottom) / 2;
          return { top: Math.round(J - cy), scale: k, origin: `50% ${Math.round(cy)}px` };
        }
        let top;
        if (typeof anchor === 'number') top = anchor - hh / 2;
        else if (anchor === 'top') top = ctx.safe.top + 16;
        else if (anchor === 'center') top = ctx.H * 0.42 - hh / 2;
        else top = (p.y != null ? p.y * ctx.H : (lay.railY || ctx.railY)) - hh * 0.35;
        return { top: U.clamp(Math.round(top), ctx.safe.top, ctx.H - ctx.safe.bottom - hh), scale: 1 };
      };
      const pl0 = placeFor(ctx.layout);
      // la conversión a sans puede cambiar la altura: recalcular la primera colocación
      const P0 = altDone ? placeFor(ctx.layout) : pl0;
      box.style.top = P0.top + 'px';
      gsap.set(box, { transformOrigin: P0.origin || '50% 50%', scale: P0.scale, y: 0 });
      const lkJumps = [];
      (CK.segments || []).forEach((sg) => {
        if (sg.t0 > ctx.item.t0 + 1e-3 && sg.t0 < ctx.item.t1 - 1e-3) {
          const L = ctx.layoutAt(sg.t0 + 1e-3);
          const pl = placeFor(L);
          lkJumps.push({ at: U.snap(sg.t0), dy: pl.top - P0.top, scale: pl.scale });
        }
      });
      lines.forEach((o) => {
        // solape intencionado (la héroe pegada a la línea): HF lo exige en cada elemento de texto, no en el ancestro
        o.spans.forEach((sp) => sp.s.setAttribute('data-layout-allow-overlap', 'true'));
        if (o.g.type === 'hero') o.spans.forEach((sp) => {
          sp.chars = U.splitChars(sp.s);
          sp.chars.forEach((c) => c.setAttribute('data-layout-allow-overlap', 'true'));
          gsap.set(sp.chars, { opacity: 0 });
        });
        else gsap.set(o.spans.map((sp) => sp.s), { opacity: 0 });
      });
      return {
        animate(tl, t0, t1) {
          const fps = ctx.fps;
          let lastEnd = t0;
          ctx.event('lockup.enter', t0);
          const wins = slideWindows(ctx, t0, t1);
          if (wins.length) U.hideDuringSlides(tl, ride, wins);
          const trw = transitionWindows(ctx, t0, t1);
          if (trw.length) hideDuringTransitions(tl, lkTr, trw);
          lines.forEach((o) => {
            o.spans.forEach((sp) => {
              const wt = U.snap(Math.max(t0, (sp.w.t0 != null ? sp.w.t0 : t0) - 1 / fps));
              if (o.g.type === 'hero') {
                const spoken = (sp.w.t1 != null && sp.w.t0 != null) ? sp.w.t1 - sp.w.t0 : 0.4;
                ctx.event('lockup.hero', wt);   // (audio): la palabra héroe se escribe → trazo (animaciones.yaml)
                lastEnd = Math.max(lastEnd, charReveal(tl, sp.chars, wt, spoken, fps));
              } else if (o.g.type === 'big') {
                tl.fromTo(sp.s, { opacity: 0, scale: 1.18 }, { opacity: 1, scale: 1, duration: 6 / fps, ease: E.enter, immediateRender: false }, wt);
                lastEnd = Math.max(lastEnd, wt + 6 / fps);
              } else {
                const d = 6 / fps;
                tl.fromTo(sp.s, { opacity: 0, y: Math.round(base * 0.35), filter: 'blur(6px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: d, ease: E.enter, immediateRender: false }, wt);
                tl.set(sp.s, { filter: 'none' }, wt + d + 1e-3);
                lastEnd = Math.max(lastEnd, wt + d);
              }
            });
          });
          // se sostiene ≥ 0,8 s tras terminar la revelación: si el clip acaba antes, se alarga (HF relee data-duration),
          // pero nunca más allá del corte de su layout ni del inicio de otro gráfico/lockup (evita textos superpuestos).
          // Mientras se sostiene, el raíl calla (CK.captionHolds; caption.rail retrasa sus palabras hasta el final).
          let need = U.snap(lastEnd + 0.8);
          const lay = ctx.layoutAt(t0 + 1e-3);
          let cap = Math.min(ctx.spec.duration || need, lay.t1);
          (ctx.spec.items || []).forEach((o) => {
            if (o === ctx.item) return;
            const blocking = o.track === 'graphic' || o.component === 'caption.lockup' || (o.track === 'layout' && o.t0 > t0 + 1e-3);
            if (blocking && o.t0 > t0 + 1e-3) cap = Math.min(cap, o.t0);
          });
          need = Math.min(need, U.snap(cap));
          if (need > t1 + 1e-3) {
            root.setAttribute('data-duration', String(Math.floor((need - t0) * 1e6) / 1e6));
            t1 = need;
          }
          (CK.captionHolds = CK.captionHolds || []).push({ t0, t1, id: ctx.item.id });
          ctx.event('lockup.hero_done', lastEnd);
          let cy = 0, cs = P0.scale;
          lkJumps.forEach((j) => {
            if (j.at >= t1) return;
            tl.fromTo(box, { y: cy, scale: cs }, { y: j.dy, scale: j.scale, duration: 0, immediateRender: false }, j.at);
            cy = j.dy; cs = j.scale;
          });
          if (p.exit === 'soft') {
            const d = 6 / fps;
            const at = Math.max(lastEnd + 0.02, t1 - d - 1 / fps);
            tl.fromTo(box, { opacity: 1, y: cy }, { opacity: 0, y: cy - Math.round(base * 0.2), duration: d, ease: E.exit, immediateRender: false }, at);
          }
        },
      };
    },
  });
})();
