/* cutkit · runtime.js — motor de motion graphics sobre HyperFrames 0.8.114 + GSAP 3.15
 * ═══════════════════════════════════════════════════════════════════════════════════════════
 * API PÚBLICA (estable: el agente de gráficos programa contra ella)
 *
 *   CK.register(name, def)        def = {
 *                                   kind?: "layout"|"camera"|"media"|"graphic"|"caption"|"transition"|"overlay",
 *                                   geometry?(props, env) → {slot, railY, seamY, cam}   (solo layouts),
 *                                   clip?: 'panel' (gráficos: en layout.split_top, recortados a la junta),
 *                                   mount(root, props, ctx) → { animate(tl, t0, t1, cues) }
 *                                 }
 *   CK.tokens                     { ...spec.tokens, motion: <tokens de motion normalizados, ver normalizeMotion()> }
 *   CK.util                       splitWords, splitChars, fitText, seeded, clamp, lerp, fr, snap, el, box, hash…
 *   CK.run(spec, tl)              monta todo y añade las animaciones a `tl` en TIEMPO ABSOLUTO de programa.
 *   CK.Z                          bases de z-index por capa (ver runtime.css).
 *
 *   ctx = { W, H, fps, spec, item, tokens, util,
 *           slot:{x,y,w,h}        zona útil (px) según el layout activo en t0,
 *           safe:{top:288,bottom:672,left:65,right:192}  márgenes de la zona segura de Shorts/Reels,
 *           safeRect:{x,y,w,h}    la zona segura como rectángulo,
 *           media:[HTMLElement]   <video>/<img> del item (cada uno con .ckWrap y .ckZoom: envoltorios SIN data-start),
 *           assetUrl(p),          ruta relativa servible,
 *           z                     z-index base de este item (CK.Z[capa] + item.z),
 *           layout                {name, slot, railY, seamY} activo en t0;  layoutAt(t) para otros instantes,
 *           railY                 y (px) del raíl de subtítulos en t0,
 *           faceAt(t) / faceMedian(t0,t1)  caja de la cara normalizada {x,y,w,h},
 *           cam                   {layout, push, move, frame, video}  (solo layouts y cámara deberían tocarla),
 *           event(kind, t, extra?) registra en window.__ckEvents {item, component, kind, t} un instante VISIBLE
 *                                 (entrada, caída, elección, corte) para alinear los SFX al fotograma real,
 *           content               #ck-content (la escena; las transiciones le aplican filtros) }
 *
 * REGLAS (HyperFrames hace seek fotograma a fotograma y SUPRIME los callbacks):
 *   - Nada de onUpdate/onComplete/eventCallback para estado visual: SOLO tweens de propiedades (tl.set/fromTo/to).
 *   - Nada de Math.random sin semilla, Date, rAF, repeat:-1 ni animaciones CSS infinitas.
 *   - No animes `root` (es el div.clip del item; HF controla su visibilidad). Anima hijos.
 *   - El root NO tiene z-index: sus hijos se apilan en el contexto global con ctx.z (o CK.Z.*).
 *   - Usa fromTo con immediateRender:false para que el seek hacia atrás sea exacto.
 *   - Los <video>/<img> de media NO se mueven de su envoltorio (están en el HTML estático, fuera del clip).
 * ═══════════════════════════════════════════════════════════════════════════════════════════ */
(function (global) {
  'use strict';

  const REG = Object.create(null);
  /* Sistema de eases ÚNICO (qa: mo.ease_tokens ≤ 4). Todos los componentes usan SOLO estos cuatro nombres;
   * los valores salen de recursos/motion_tokens.yaml (spec.tokens.motion) en CK.run.
   *   enter  power3.out      entra y se posa          · exit  power2.in   sale acelerando
   *   move   power2.inOut    A→B, cámara, Ken Burns    · pop   back.out(1.3)  único con rebote (solo el foco)
   * Texturas (grano, glitch) y cambios discretos van con tl.set (sin ease). */
  const EASE = { enter: 'power3.out', exit: 'power2.in', move: 'power2.inOut', pop: 'back.out(1.3)' };
  const Z = { bg: 0, cam: 100, layoutBack: 200, broll: 300, layoutFront: 380, graphic: 400, transition: 600, caption: 650, overlay: 700 };
  const TRACK_Z = { layout: Z.layoutBack, camera: Z.cam, broll: Z.broll, graphic: Z.graphic, caption: Z.caption, transition: Z.transition, overlay: Z.overlay };
  const TRACK_ORDER = ['layout', 'camera', 'broll', 'graphic', 'caption', 'transition', 'overlay'];
  const SAFE = { top: 288, bottom: 672, left: 65, right: 192 };

  // ───────────────────────────────────────────────────────── util
  const util = {
    clamp: (v, a, b) => Math.min(b, Math.max(a, v)),
    lerp: (a, b, u) => a + (b - a) * u,
    invLerp: (a, b, v) => (b === a ? 0 : (v - a) / (b - a)),
    fps: 30,
    fr(n) { return n / util.fps; },                        // fotogramas → segundos
    /** encaja al fotograma, 1 µs ANTES de su instante exacto: GSAP redondea posiciones a 1e-7 y 1151/30 = 38,3666667 >
     *  38,36666… → el tween no arrancaba en su primer fotograma (el panel salía un fotograma en y=0). */
    snap(t) { return Math.max(0, Math.round(t * util.fps) / util.fps - 1e-6); },
    /** instante exacto del fotograma (para informar, p. ej. eventos de SFX) */
    frameT(t) { return Math.round(Math.round(t * util.fps) / util.fps * 1e6) / 1e6; },
    round(v, d = 2) { const k = Math.pow(10, d); return Math.round(v * k) / k; },
    /** hash entero determinista (32 bits) de un número o texto */
    hash(v) {
      let h = 2166136261 >>> 0;
      const s = String(v);
      for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
      return h >>> 0;
    },
    /** RNG con semilla (mulberry32) → función () => [0,1) */
    seeded(seed) {
      let a = (typeof seed === 'number' ? seed : util.hash(seed)) >>> 0;
      return function () {
        a = (a + 0x6D2B79F5) >>> 0;
        let t = a;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    },
    /** crea un elemento: el('div', 'cls a', parent, {left:'10px'}, 'texto') */
    el(tag, cls, parent, style, text) {
      const d = document.createElement(tag);
      if (cls) d.className = cls;
      if (style) Object.assign(d.style, style);
      if (text != null) d.textContent = text;
      if (parent) parent.appendChild(d);
      return d;
    },
    /** posiciona en absoluto: box(el, {x,y,w,h}) en px */
    box(el, b) {
      Object.assign(el.style, { position: 'absolute', left: b.x + 'px', top: b.y + 'px', width: b.w + 'px', height: b.h + 'px' });
      return el;
    },
    /** separa el texto de `el` en <span class="ck-word"> (los espacios quedan como texto: el ajuste de línea funciona) */
    splitWords(el) {
      const text = el.textContent;
      el.textContent = '';
      const out = [];
      text.split(/(\s+)/).forEach((tok) => {
        if (!tok) return;
        if (/^\s+$/.test(tok)) { el.appendChild(document.createTextNode(' ')); return; }
        const w = util.el('span', 'ck-word', el, null, tok);
        out.push(w);
      });
      return out;
    },
    /** separa en letras dentro de palabras (no parte palabras al ajustar). Devuelve [chars] con .words = [words] */
    splitChars(el) {
      const words = util.splitWords(el);
      const chars = [];
      words.forEach((w) => {
        const t = w.textContent; w.textContent = '';
        Array.from(t).forEach((ch) => { const c = util.el('span', 'ck-char', w, null, ch); c.ckWord = w; chars.push(c); });
      });
      chars.words = words;
      return chars;
    },
    /** ajusta font-size (px enteros) para que el texto quepa en maxW (y maxH si se da). Devuelve el px elegido. */
    fitText(el, maxW, maxPx, minPx, maxH) {
      minPx = minPx || 12;
      let lo = minPx, hi = Math.max(minPx, Math.floor(maxPx)), best = lo;
      const range = document.createRange();
      const fits = (px) => {
        el.style.fontSize = px + 'px';
        range.selectNodeContents(el);                       // ancho REAL del texto (no el de la caja de bloque)
        const r = range.getBoundingClientRect();
        const w = r.width, h = Math.max(r.height, el.scrollHeight);
        return w <= maxW + 0.5 && (!maxH || h <= maxH + 0.5);
      };
      if (fits(hi)) return hi;
      while (lo <= hi) {
        const mid = (lo + hi) >> 1;
        if (fits(mid)) { best = mid; lo = mid + 1; } else hi = mid - 1;
      }
      el.style.fontSize = best + 'px';
      return best;
    },
    /** tesela de ruido SVG (data URI) determinista por semilla */
    noiseTile(seed, size, freq, octaves, fixed) {
      size = size || 256; freq = freq || 0.82; octaves = octaves || 2;
      const s = (util.hash(seed || 1) % 997) + 1;
      // `fixed`: la referencia al filtro va como «#n» (encodeURIComponent la codifica una vez). Sin él, el
      // «%23n» de siempre queda doblemente codificado y la tesela sale lisa (sin ruido); se deja así para no cambiar el
      // aspecto de los paneles existentes
      return "url(\"data:image/svg+xml," + encodeURIComponent(
        `<svg xmlns='http://www.w3.org/2000/svg' width='${size}' height='${size}'>` +
        `<filter id='n' x='0' y='0'><feTurbulence type='fractalNoise' baseFrequency='${freq}' numOctaves='${octaves}' seed='${s}' stitchTiles='stitch'/>` +
        `<feColorMatrix type='saturate' values='0'/></filter><rect width='100%' height='100%' filter='url(${fixed ? "#" : "%23"}n)'/></svg>`) + "\")";
    },
    /** grano animado SIN callbacks ni eases: background-position salta `fps` veces por segundo con tl.set
     *  (posiciones por hash de semilla+paso → determinista; los set no cuentan como ease). */
    grain(tl, parent, t0, t1, o) {
      o = Object.assign({ opacity: 0.08, fps: 12, seed: 7, blend: 'overlay', z: null, size: 256, freq: 0.82 }, o || {});
      const g = util.el('div', 'ck-grain', parent, {
        position: 'absolute', inset: '0', pointerEvents: 'none', backgroundImage: util.noiseTile(o.seed, o.size, o.freq, null, o.fixed),
        backgroundSize: `${o.size}px ${o.size}px`, mixBlendMode: o.blend, opacity: String(o.opacity),
      });
      if (o.z != null) g.style.zIndex = String(o.z);
      const n = Math.max(1, Math.round(Math.max(0.04, t1 - t0) * o.fps));
      const pos = (k) => { const h = util.hash(o.seed + ':' + k); return `${h % o.size}px ${(h >>> 9) % o.size}px`; };
      gsap.set(g, { backgroundPosition: pos(0) });
      for (let k = 1; k < n; k++) tl.set(g, { backgroundPosition: pos(k) }, util.snap(t0 + k / o.fps));
      return g;
    },
    /** crea (una vez) un <svg> de filtros en `parent` y devuelve el <filter> con id */
    svgFilter(parent, id, inner) {
      const NS = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('width', '0'); svg.setAttribute('height', '0');
      svg.style.position = 'absolute';
      svg.innerHTML = `<filter id="${id}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">${inner}</filter>`;
      parent.appendChild(svg);
      return svg.querySelector('filter');
    },
    /** cubic-bezier [x1,y1,x2,y2] → ease GSAP (CustomEase si está, si no el fallback) */
    bezier(name, cb, fallback) {
      if (global.CustomEase && cb && cb.length === 4) {
        try { global.CustomEase.create(name, cb.join(',')); return name; } catch (e) { /* noop */ }
      }
      return fallback || 'power2.out';
    },
    /** coloca un <video>/<img> de ctx.media: caja (px), z-index y lo marca como «colocado» (el runtime lo
     *  mostrará solo en [t0, t1) del item). Devuelve el envoltorio (.ck-mwrap) para darle estilo o animarlo. */
    placeMedia(m, b, z) {
      const w = m.ckWrap || m.closest('.ck-mwrap');
      if (!w) return null;
      if (b) util.box(w, b);
      if (z != null) w.style.zIndex = String(z);
      w.dataset.ckPlaced = '1';
      return w;
    },
    css(name) { return `var(--ck-${name})`; },
    /** Medidas de la cabeza del presentador a partir de la caja de cara (normalizado 0..1 del fotograma). Medido en 26 fotogramas de
     *  una toma de prueba: parte de arriba del pelo = y − 0,48·h (p50; máx. 0,57 → se usa 0,55), ojos ≈ y + 0,40·h, labio inferior
     *  ≈ y + 0,82·h, barbilla ≈ y + h + 0,035. Cabeza (pelo → barbilla) ≈ 0,51–0,55 del alto. */
    headOf(f, t0, t1) {
      // pelo MEDIDO en el A-roll si está (spec.aroll.hair, ≈1/s): el punto más alto en [t0 − 0,6, t1 + 0,6]
      let hair = f.y - 0.55 * f.h;
      const tr = CK.hairTrack;
      if (tr && tr.length && t0 != null) {
        const a = t0 - 0.6, b = (t1 != null ? t1 : t0) + 0.6;
        let m = Infinity;
        for (let i = 0; i < tr.length; i++) if (tr[i][0] >= a && tr[i][0] <= b) m = Math.min(m, tr[i][1]);
        if (!isFinite(m)) { let best = null; tr.forEach((q) => { if (!best || Math.abs(q[0] - t0) < Math.abs(best[0] - t0)) best = q; }); m = best ? best[1] : hair; }
        hair = m;
      }
      return { hair, eyes: f.y + 0.40 * f.h, mouth: f.y + 0.82 * f.h, chin: f.y + f.h + 0.035,
        cx: f.x + f.w / 2, len: (f.y + f.h + 0.035) - hair };
    },
    /** TEXTO durante el deslizado de un split: oculto hasta que el panel ha recorrido ≥ 60 % (power3.out → ~3 f de 8)
     *  y entonces aparece EN SU SITIO con un pop de 4 f. Nunca fuera del lienzo ni cruzando la cara. Solo opacidad e
     *  `y` pequeña del elemento (no usar `visibility`: anula el hidden con el que HF oculta el clip). */
    hideDuringSlides(tl, el, wins) {
      (wins || []).forEach((w) => {
        const N = Math.max(1, Math.round(w.d * util.fps));
        let k = 1;
        while (k < N && 1 - Math.pow(1 - k / N, 3) < 0.6) k++;
        const at = w.at + k / util.fps;
        tl.fromTo(el, { opacity: 1 }, { opacity: 0, duration: 0, immediateRender: false }, w.at);
        tl.fromTo(el, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 4 / util.fps, ease: EASE.enter, immediateRender: false }, at);
      });
    },
    /** splits que entran deslizando cuyo deslizado [t0, t0+d) toca [a, b) */
    slideWindows(a, b) {
      return (CK.segments || []).filter((sg) => sg.name === 'layout.split_top' && sg.props && sg.props.enter === 'slide')
        .map((sg) => ({ at: util.snap(sg.t0), d: (sg.props.enter_frames || 8) / util.fps, J: (sg.geom && sg.geom.seamY) || 1008 }))
        .filter((w) => w.at < b - 1e-3 && w.at + w.d > a + 1e-3);
    },
    /** el elemento cae con el panel del split (mismo recorrido, curva y fotogramas que el panel). Par encadenado:
     *  fromTo de duración 0 en el corte (0 → arriba) + caída (arriba → 0) → seek exacto en ambos sentidos.
     *  No mezclar con otros tweens de `y` del mismo elemento que se solapen con la ventana. Devuelve el fin de la caída. */
    rideSlides(tl, el, wins) {
      let end = 0;
      (wins || []).forEach((w) => {
        const off = -(w.J + 40);
        tl.fromTo(el, { y: 0 }, { y: off, duration: 0, immediateRender: false }, w.at);
        tl.fromTo(el, { y: off }, { y: 0, duration: w.d, ease: EASE.enter, immediateRender: false }, w.at + 0.0001);
        end = Math.max(end, w.at + w.d);
      });
      return end;
    },
    /** color semántico → CSS: accent | accent2 | green | red | white | muted | #hex */
    color(c) {
      if (!c) return null;
      if (c[0] === '#' || c.startsWith('rgb')) return c;
      const map = { accent: 'var(--ck-accent)', accent2: 'var(--ck-accent-2)', subject: 'var(--ck-accent-2)', green: 'var(--ck-green)',
        red: 'var(--ck-red)', white: 'var(--ck-white)', muted: 'var(--ck-muted)', ink: 'var(--ck-ink)', navy: 'var(--ck-navy)' };
      return map[c] || c;
    },
    /** quita puntuación final de subtítulo (mantiene ¿? ¡! internos) */
    cleanWord(t) { return String(t || '').replace(/[.,;:…]+$/u, '').replace(/^[«"“]+|[»"”]+$/gu, ''); },
  };

  // ───────────────────────────────────────────────────────── tokens de motion
  /** Normaliza motion_tokens.yaml (ya parseado, en spec.tokens.motion) a segundos + eases GSAP.
   *  Claves estables: dur.*, ease.*, stagger.*, lead.*, limits.*  (si falta el YAML se usan los valores por defecto). */
  function normalizeMotion(raw, fps) {
    raw = raw || {};
    const f = (n) => util.round(n / fps, 4);
    const D = (raw.duraciones || {});
    const pa = D.por_accion || {}, tr = D.transiciones || {};
    const pick = (o, k, dflt) => (o && o[k] != null ? (typeof o[k] === 'object' ? (o[k].default != null ? o[k].default : dflt) : o[k]) : dflt);
    const E = raw.eases || {};
    const g = (grp, k, dflt) => { const v = E[grp] && E[grp][k]; return v && v.gsap ? v : { gsap: dflt }; };
    // registra CustomEase con los nombres del YAML (o fallback)
    const ce = (v, name, fb) => {
      const s = v.gsap || fb;
      if (s.startsWith('CustomEase:')) return util.bezier(s.slice(11), v.cubic_bezier, fb);
      return s;
    };
    const st = raw.stagger || {};
    const leadF = (raw.sincronia && raw.sincronia.voz) || {};
    const byCause = leadF.antelacion_por_causa_f || {};
    const m = {
      fps,
      dur: {
        text_in: f(pick(pa, 'texto_entrada', 7)),
        hero_in: f(pick(pa, 'texto_entrada_hero', 9)),
        text_out: f(pick(pa, 'texto_salida', 4)),
        caption_pop: f(pick(pa, 'caption_pop', 4)),
        caption_out: f(pick(pa, 'caption_salida', 0)),
        letter: f(1),
        number_in: f(pick(pa, 'numero_aparicion', 7)),
        count: f(pick(pa, 'numero_conteo', 21)),
        icon_in: f(pick(pa, 'icono_logo_entrada', 8)),
        line_draw: f(12),
        arrow: f(pick(pa, 'flecha_dibujo', 7)),
        underline: f(pick(pa, 'subrayado_tachado', 6)),
        split_in: f(pick(pa, 'panel_split_entrada', 8)),
        move: f(9),
        punch: f(4),                                   // punch animado (golpe); el de corte es 0
        dim: f(pick(pa, 'atenuar_fondo', 15)),
        pulse: f(pick(pa, 'emphasize_pulso', 8)),
        slow_zoom_per_s: (pa.zoom_lento && pa.zoom_lento.default) || 0.015,
        light_leak: f(pick(tr, 'light_leak', 10)),
        whip: f(pick(tr, 'whip_pan', 4) * 2),          // whip completo (salida + entrada)
        flash: f(pick(tr, 'flash_blanco', 3)),
        zoom_blur: f(pick(tr, 'zoom_blur', 6)),
        glitch: f(pick(tr, 'glitch', 4)),
        cross_blur: f(pick(tr, 'desenfoque_cruzado', 7)),
        shared: f(pick(tr, 'shared_element', 10)),
        hold_min: (D.sostener && D.sostener.min_s) || 0.8,
        read_per_word: (D.sostener && D.sostener.lectura_s_por_palabra) || 0.33,
      },
      ease: {
        enter: g('enter', 'default', 'power3.out').gsap,
        enter_soft: g('enter', 'suave', 'power2.out').gsap,
        enter_expr: g('enter', 'expresivo', 'expo.out').gsap,
        exit: g('exit', 'default', 'power2.in').gsap,
        exit_fast: g('exit', 'rapido', 'power3.in').gsap,
        fade_out: g('exit', 'fade', 'power1.in').gsap,
        move: g('move', 'default', 'power2.inOut').gsap,
        move_expr: g('move', 'expresivo', 'expo.inOut').gsap,
        camera: g('move', 'camara_lenta', 'sine.inOut').gsap,
        linear: 'none',
        pulse: 'power2.out',
        hit: g('emphasize', 'golpe', 'back.out(1.3)').gsap,
        settle_soft: g('settle', 'sutil', 'back.out(1.2)').gsap,
        settle: g('settle', 'default', 'back.out(1.3)').gsap,
        settle_strong: g('settle', 'marcado', 'back.out(1.7)').gsap,
        count: (E.count_up && E.count_up.gsap) || 'power2.out',
        cross: (E.opacity_cross && E.opacity_cross.gsap) || 'sine.inOut',
        draw: g('emphasize', 'trazo', 'power2.inOut').gsap,
      },
      stagger: {
        letters: f((st.letras && st.letras.each_f) || 1),
        words: f(Array.isArray(st.palabras && st.palabras.each_f) ? st.palabras.each_f[0] : 2.5),
        lines: f(Array.isArray(st.lineas && st.lineas.each_f) ? st.lineas.each_f[0] : 4),
        list_2_3: f(4), list_4_6: f(3), list_7_12_amount: f(12), amount_max: f(st.amount_max_f || 15),
        overlap_min: st.solape_minimo_pct || 0.5,
      },
      lead: {
        default: f(leadF.antelacion_f ? (leadF.antelacion_f.default || 5) : 5),
        caption: f(1),
        enfasis: f(byCause.enfasis || 3), enumeracion: f(byCause.enumeracion || 4), cambio_de_idea: f(byCause.cambio_de_idea || 5),
        transicion_de_seccion: f(byCause.transicion_de_seccion || 5), mostrar_lo_que_se_dice: f(byCause.mostrar_lo_que_se_dice || 5),
        prueba_credibilidad: f(byCause.prueba_credibilidad || 7),
      },
      limits: Object.assign({ min_px_lectura: 48, subtitulo_px: [56, 64], titular_px: [96, 160], hero_px: [180, 320] },
        (raw.limites && raw.limites.texto) || {}),
      raw,
    };
    // eases con nombre del YAML (m3*), por si un componente los pide
    const m3 = (grp, k, name, fb) => { const v = E[grp] && E[grp][k]; m.ease[name] = v ? ce(v, null, fb) : fb; };
    m3('enter', 'm3_emphasized_decelerate', 'm3_decel', 'expo.out');
    m3('exit', 'm3_emphasized_accelerate', 'm3_accel', 'power3.in');
    m3('move', 'm3_standard', 'm3_standard', 'power2.inOut');
    m3('move', 'm1_standard', 'm1_standard', 'power2.inOut');
    return m;
  }

  // ───────────────────────────────────────────────────────── caras
  function makeFaces(spec) {
    const raw = (spec.aroll && spec.aroll.faces) || [];
    const rows = raw.map((r) => (Array.isArray(r) ? { t: +r[0], x: +r[1], y: +r[2], w: +r[3], h: +r[4] } : r))
      .filter((r) => r && isFinite(r.t) && r.w > 0 && r.h > 0).sort((a, b) => a.t - b.t);
    const DEF = { x: 0.32, y: 0.24, w: 0.36, h: 0.30 };
    function faceAt(t) {
      if (!rows.length) return Object.assign({}, DEF);
      let lo = 0, hi = rows.length - 1;
      while (lo < hi) { const mid = (lo + hi) >> 1; if (rows[mid].t < t) lo = mid + 1; else hi = mid; }
      const r = (lo > 0 && Math.abs(rows[lo - 1].t - t) < Math.abs(rows[lo].t - t)) ? rows[lo - 1] : rows[lo];
      return { x: r.x, y: r.y, w: r.w, h: r.h };
    }
    function faceMedian(t0, t1) {
      if (!rows.length) return Object.assign({}, DEF);
      const sel = rows.filter((r) => r.t >= t0 - 0.05 && r.t <= t1 + 0.05);
      if (!sel.length) return faceAt((t0 + t1) / 2);
      const med = (k) => { const v = sel.map((r) => r[k]).sort((a, b) => a - b); return v[v.length >> 1]; };
      return { x: med('x'), y: med('y'), w: med('w'), h: med('h') };
    }
    return { faceAt, faceMedian, rows };
  }

  // ───────────────────────────────────────────────────────── layouts (segmentos)
  const FULL_GEOM = (env) => ({
    slot: Object.assign({}, env.safeRect),
    railY: null, seamY: null,
    cam: { x: 0, y: 0, scale: 1, opacity: 1, z: Z.cam, clip: insetFull(env) },
  });
  function insetFull() { return 'inset(0px 0px 0px 0px round 0px)'; }

  function buildLayoutSegments(spec, env) {
    const items = (spec.items || []).filter((it) => it.track === 'layout' && REG[it.component])
      .sort((a, b) => a.t0 - b.t0);
    const segs = [];
    let cursor = 0;
    const D = spec.duration || 0;
    const pushDefault = (a, b) => { if (b - a > 1e-3) segs.push({ name: 'layout.full_face', t0: a, t1: b, props: {}, item: null, implicit: true }); };
    items.forEach((it) => {
      if (it.t0 > cursor + 1e-3) pushDefault(cursor, it.t0);
      segs.push({ name: it.component, t0: Math.max(it.t0, cursor), t1: it.t1, props: it.props || {}, item: it });
      cursor = Math.max(cursor, it.t1);
    });
    pushDefault(cursor, Math.max(D, cursor));
    segs.forEach((s, i) => {
      const def = REG[s.name] || REG['layout.full_face'];
      const envS = Object.assign({}, env, { t0: s.t0, t1: s.t1, face: env.faceMedian(s.t0, s.t1) });
      let g = null;
      try { g = def && def.geometry ? def.geometry(s.props || {}, envS) : null; } catch (e) { console.error('[CK] geometry', s.name, e); }
      const base = FULL_GEOM(env);
      s.geom = Object.assign({}, base, g || {});
      s.geom.cam = Object.assign({}, base.cam, (g && g.cam) || {});
      s.geom.railExplicit = !!(g && g.railY != null);
      if (s.geom.railY == null) s.geom.railY = env.defaultRailY;
      // un split que «desliza» viniendo de un plano SIN cara (lienzo, B-roll a pantalla completa) entra en corte: si el
      // panel cayera, durante 1–2 f se vería el relleno desenfocado por encima de la placa
      const prev = segs[i - 1];
      if (prev && prev.geom && prev.geom.cam && prev.geom.cam.opacity === 0 && s.props && s.props.enter === 'slide') {
        s.props = Object.assign({}, s.props, { enter: 'cut', enter_requested: 'slide' });
        if (s.item) s.item.props = s.props;
      }
    });
    return segs;
  }

  // ───────────────────────────────────────────────────────── timeline protegida
  /** GSAP 3.15: un fromTo en posición NEGATIVA desplaza TODA la timeline hacia delante (medido: un tween en −0,033
   *  retrasaba 1 fotograma todo el vídeo). Los componentes reciben un proxy que fija a 0 las posiciones < 0. */
  /** Set de eases CERRADO a los 4 tokens del kit. Cualquier ease que pida un
   *  componente (o el runtime) se traduce a su papel: *.out / expo / sine.out → enter · *.in → exit · *.inOut → move ·
   *  back/elastic/bounce → pop. El lineal ('none') solo se queda con papel declarado (`data: {role}` = progress, typing,
   *  scroll o path: una velocidad constante, no una curva); si no, pasa a move. Sin ease en un tween con duración →
   *  enter. Lo traducido se cuenta en __ckReport.ease_remap (diagnóstico). Las funciones de ease se respetan. */
  const LINEAR_ROLES = { progress: 1, typing: 1, scroll: 1, path: 1 };
  function ease4(v, report) {
    if (!v || typeof v !== 'object' || v.duration === 0) return v;
    const e = v.ease;
    if (typeof e === 'function') return v;
    const T4 = [EASE.enter, EASE.exit, EASE.move, EASE.pop];
    if (e != null && T4.indexOf(e) >= 0) return v;
    let to;
    if (e == null) to = EASE.enter;
    else {
      const s = String(e).toLowerCase();
      if (s === 'none' || s === 'linear' || s.indexOf('power0') === 0) {
        const role = v.data && (v.data.role || v.data.kind);
        if (role && LINEAR_ROLES[role]) return v;
        to = EASE.move;
      } else if (/^(back|elastic|bounce)/.test(s)) to = EASE.pop;
      else if (/inout/.test(s)) to = EASE.move;
      else if (/\.in(\(|$)/.test(s)) to = EASE.exit;
      else to = EASE.enter;   // *.out, expo, circ, sine.out, power2… (y CustomEase con nombre desconocido)
    }
    if (!to) return v;
    const k = String(e) + ' → ' + to;
    report.ease_remap = report.ease_remap || {};
    report.ease_remap[k] = (report.ease_remap[k] || 0) + 1;
    return Object.assign({}, v, { ease: to });
  }
  function guardTimeline(tl, report) {
    const fix = (a, i) => {
      if (typeof a[i] === 'number' && a[i] < 0) { report.negative_positions = (report.negative_positions || 0) + 1; a[i] = 0; }
      return a;
    };
    const e4 = (a, i) => { if (a[i] && typeof a[i] === 'object' && !Array.isArray(a[i])) a[i] = ease4(a[i], report); return a; };
    return new Proxy(tl, {
      get(target, prop) {
        if (prop === 'fromTo') return (...a) => target.fromTo(...fix(e4(a, 2), 3));
        if (prop === 'to' || prop === 'from') return (...a) => target[prop](...fix(e4(a, 1), 2));
        if (prop === 'set') return (...a) => target[prop](...fix(a, 2));
        if (prop === 'add') return (...a) => target.add(...fix(a, 1));
        if (prop === 'call') return (...a) => target.call(...fix(a, 2));
        const v = target[prop];
        return typeof v === 'function' ? v.bind(target) : v;
      },
    });
  }

  // ───────────────────────────────────────────────────────── run
  function run(spec, tlRaw) {
    const W = spec.width || 1080, H = spec.height || 1920, fps = spec.fps || 30;
    util.fps = fps;
    const rootEl = document.getElementById('root');
    const content = document.getElementById('ck-content');
    const stage = document.getElementById('ck-stage');
    const report = { mounted: [], errors: [], missing: [], negative_positions: 0, camera_clamped: [] };
    global.__ckReport = report;            // los componentes apuntan aquí (p. ej. camera_clamped) durante el montaje
    const tl = guardTimeline(tlRaw, report);
    // fuera de HyperFrames (vista previa/QA) el root no tiene tamaño: se lo damos desde data-width/height
    if (rootEl && rootEl.offsetHeight < 2) { rootEl.style.width = W + 'px'; rootEl.style.height = H + 'px'; }

    // tokens
    const tk = Object.assign({}, spec.tokens || {});
    tk.motion = normalizeMotion((spec.tokens && spec.tokens.motion) || {}, fps);
    tk.safe = Object.assign({}, SAFE, (spec.tokens && spec.tokens.safe) || {});
    CK.tokens = tk;
    // los cuatro eases desde los tokens (mismo objeto: los componentes guardan la referencia)
    const rawE = (spec.tokens && spec.tokens.motion && spec.tokens.motion.eases) || {};
    const pickE = (grp, k) => rawE[grp] && rawE[grp][k] && rawE[grp][k].gsap && !String(rawE[grp][k].gsap).startsWith('CustomEase');
    if (pickE('enter', 'default')) EASE.enter = rawE.enter.default.gsap;
    if (pickE('exit', 'default')) EASE.exit = rawE.exit.default.gsap;
    if (pickE('move', 'default')) EASE.move = rawE.move.default.gsap;
    if (pickE('settle', 'default')) EASE.pop = rawE.settle.default.gsap;
    tk.motion.ease = Object.assign(tk.motion.ease, { enter: EASE.enter, exit: EASE.exit, move: EASE.move, pop: EASE.pop });
    if (tk.subject_color) rootEl.style.setProperty('--ck-accent-2', tk.subject_color);
    if (tk.accent) rootEl.style.setProperty('--ck-accent', tk.accent);

    const faces = makeFaces(spec);
    CK.hairTrack = (spec.aroll && spec.aroll.hair) || [];
    const safe = tk.safe;
    // Zona segura dependiente de y: por encima de y=1000 no hay botones de la plataforma → derecha = izquierda (65) y el
    // contenido se centra en x=540; por debajo, derecha = 192. safeRect = rectángulo simétrico (centrado en 540);
    // para algo que baje de y=1000 usa safeAt(y0, y1) / safeCenteredW(y1).
    const SAFE_SPLIT_Y = (spec.tokens && spec.tokens.safe_right_from_y) || 1000;
    const safeRect = { x: safe.left, y: safe.top, w: W - 2 * safe.left, h: H - safe.top - safe.bottom };
    const safeAt = (y0, y1) => {
      const low = (y1 != null ? y1 : y0) > SAFE_SPLIT_Y;
      return { x0: safe.left, x1: W - (low ? safe.right : safe.left) };
    };
    const safeCenteredW = (y1) => (y1 > SAFE_SPLIT_Y ? 2 * Math.min(W / 2 - safe.left, W - safe.right - W / 2) : W - 2 * safe.left);
    const capY = tk.caption_y != null ? tk.caption_y : 0.58;
    const aro = spec.aroll || {};
    const splitRanges = aro.split_src ? (aro.split_ranges || []) : [];
    const splitVideo = (a, b) => splitRanges.some((r) => a >= r[0] - 1e-3 && b <= r[1] + 1e-3);
    const env = { W, H, fps, tokens: tk, safe, safeRect, safeAt, safeCenteredW, splitVideo: splitRanges.length ? splitVideo : null,
      splitSeam: aro.split_seam || 960, faceAt: faces.faceAt, faceMedian: faces.faceMedian, defaultRailY: Math.round(capY * H), Z };

    // cámara
    const cam = {
      layout: document.getElementById('ck-cam'),
      push: document.getElementById('ck-cam-push'),
      move: document.getElementById('ck-cam-move'),
      frame: document.getElementById('ck-cam-frame'),
      video: document.getElementById('aroll'),
    };

    // segmentos de layout
    const segs = buildLayoutSegments(spec, env);
    function segAt(t) {
      for (let i = 0; i < segs.length; i++) if (t >= segs[i].t0 - 1e-4 && t < segs[i].t1 - 1e-4) return segs[i];
      return segs[segs.length - 1] || { name: 'layout.full_face', geom: Object.assign(FULL_GEOM(env), { railY: env.defaultRailY }) };
    }
    function layoutAt(t) { const s = segAt(t); return { name: s.name, slot: s.geom.slot, railY: s.geom.railY, seamY: s.geom.seamY, feather: s.geom.feather, cam: s.geom.cam, geom: s.geom, t0: s.t0, t1: s.t1, props: s.props || {} }; }
    CK.layoutAt = layoutAt;
    CK.segments = segs;

    // cámara: estado inicial + cambios por segmento (cut o slide), centralizados aquí para que no choquen
    const camProps = (c) => ({ x: Math.round(c.x), y: Math.round(c.y), scale: c.scale, opacity: c.opacity, clipPath: c.clip });
    if (cam.layout && segs.length) {
      const c0 = segs[0].geom.cam;
      // estado inicial FUERA de la timeline (un set en t=0 es ambiguo al volver atrás)
      gsap.set(cam.layout, Object.assign(camProps(c0), { zIndex: c0.z, transformOrigin: '0 0' }));
      gsap.set([cam.push, cam.move], { x: 0, y: 0, scale: 1, transformOrigin: '0 0' });
      // máscara de bordes laterales (placa del split con escala < 1): cambios discretos en el instante en que la placa
      // deja de cubrir el lienzo (mismo instante que el relleno desenfocado → nunca se ve el relleno sin placa encima)
      const maskOf = (c) => (c && c.mask) || 'none';
      const setMask = (m, at) => tl.set(cam.layout, { webkitMaskImage: m, maskImage: m }, at);
      gsap.set(cam.layout, { webkitMaskImage: maskOf(c0), maskImage: maskOf(c0) });
      CK.camBgWindows = [];
      if (c0.fill && c0.scale < 0.999 && c0.opacity !== 0) CK.camBgWindows.push({ a: 0, b: segs[0].t1, cam: c0 });
      for (let i = 1; i < segs.length; i++) {
        const prev = segs[i - 1].geom.cam, cur = segs[i].geom.cam, s = segs[i];
        const enter = (s.props && s.props.enter) || 'cut';
        const at = util.snap(s.t0);
        tl.set(cam.layout, { zIndex: cur.z }, at);
        // Sin asentamientos automáticos al volver a la cara (los mini zooms se ven raros): corte limpio
        const back = false;
        // instante en que la placa deja de cubrir el lienzo (para la máscara y el relleno)
        let fillAt = at;
        if (cur.splitVideo || prev.splitVideo) {
          tl.set(cam.layout, camProps(cur), at);            // entra/sale el vídeo 50/50: corte
        } else if (enter === 'slide' && prev.opacity !== 0) {
          const dur = (s.props.enter_frames ? s.props.enter_frames / fps : tk.motion.dur.split_in);
          tl.fromTo(cam.layout, camProps(prev), Object.assign(camProps(cur), { duration: dur, ease: EASE.enter, immediateRender: false }), at);
          // power3.out: primer fotograma en que la escala baja de 1 (antes la placa aún cubre el lienzo entero)
          const N = Math.max(1, Math.round(dur * fps));
          for (let kf = 0; kf <= N; kf++) {
            const u = 1 - Math.pow(1 - kf / N, 3), sc = prev.scale + (cur.scale - prev.scale) * u;
            if (sc < 0.999) { fillAt = at + kf / fps; break; }
          }
        } else if (enter === 'slide') {
          // venía de un plano sin cara (cámara oculta): la placa entra ya en su sitio (sin fundir desde opacidad 0, que
          // dejaba ver el relleno desenfocado a pantalla completa) y el panel cae encima
          tl.set(cam.layout, camProps(cur), at);
        } else if (back && s.props.return !== 'cut') {
          // vuelta a la cara: corte + asentamiento de 5 f (×1,05 → ×1 alrededor de la cara), nunca un fundido a negro
          const f = env.faceMedian(s.t0, Math.min(s.t1, s.t0 + 1));
          // origen en la BARBILLA: la cara se asienta sin bajar hacia el raíl de subtítulos
          const hdR = util.headOf(f, s.t0, Math.min(s.t1, s.t0 + 1));
          const P = { x: cur.x + cur.scale * (f.x + f.w / 2) * W, y: cur.y + cur.scale * Math.max(0.04, hdR.hair) * H };   // ancla en el pelo
          const k = 1.05, from = Object.assign(camProps(cur), { x: Math.round(P.x - k * (P.x - cur.x)), y: Math.round(P.y - k * (P.y - cur.y)), scale: cur.scale * k });
          tl.fromTo(cam.layout, from, Object.assign(camProps(cur), { duration: 5 / fps, ease: EASE.enter, immediateRender: false }), at);
        } else {
          tl.set(cam.layout, camProps(cur), at);
        }
        if (maskOf(cur) !== maskOf(prev)) setMask(maskOf(cur), at);   // activa desde el primer fotograma (sin borde duro)
        if (cur.fill && cur.scale < 0.999 && cur.opacity !== 0) CK.camBgWindows.push({ a: enter === 'slide' ? at : fillAt, b: s.t1, cam: cur });
      }
    }

    // relleno lateral (split con escala < 1): copia del A-roll a pantalla completa, desenfocada y oscurecida.
    // Se pinta pequeña (¼) y se escala ×4: el desenfoque cuesta 16× menos. Visible solo en esos tramos (tl.set display).
    const camBg = document.getElementById('ck-cam-bg');
    if (camBg) {
      gsap.set(camBg, { display: 'none' });
      (CK.camBgWindows || []).forEach((w) => {
        const a = util.snap(w.a), b = util.snap(w.b);
        // misma y y escala vertical que la placa; a lo ancho, el lienzo entero (estirado 1/s: imperceptible en los bordes)
        const geo = { display: 'block', x: 0, y: Math.round(w.cam.y), scaleX: 1, scaleY: w.cam.scale };
        if (a <= 1e-3) gsap.set(camBg, geo); else tl.set(camBg, geo, a);
        tl.set(camBg, { display: 'none' }, b);
      });
    }

    // vídeo 50/50: visible solo en los tramos de split que lo usan
    const splitCam = document.getElementById('ck-split-cam');
    if (splitCam) {
      gsap.set(splitCam, { display: 'none' });
      segs.forEach((sg) => {
        if (!(sg.geom && sg.geom.splitVideo)) return;
        const a = util.snap(sg.t0), b = util.snap(sg.t1);
        if (a <= 1e-3) gsap.set(splitCam, { display: 'block' }); else tl.set(splitCam, { display: 'block' }, a);
        tl.set(splitCam, { display: 'none' }, b);
      });
    }

    // media por item
    const mediaOf = (it) => (it.media || []).map((m) => {
      const elm = document.getElementById(m.id);
      if (elm) { elm.ckWrap = elm.closest('.ck-mwrap'); elm.ckZoom = elm.closest('.ck-mzoom'); elm.ckInfo = m; elm.ckAsset = m.asset || elm.dataset.asset || null; }
      return elm;
    }).filter(Boolean);

    const assetUrl = (p) => (p ? String(p).replace(/^\.?\//, '') : p);

    // montaje: layouts reales + implícitos primero (los implícitos no tienen root → no dibujan)
    CK.captionHolds = [];
    CK.pushes = [];                         // zooms lentos ya montados (los punch encadenan su tope con ellos)
    CK.punches = [];                        // punch-in ya montados {t0, t1, k, Py} (los subtítulos leen la barbilla real)
    global.__ckEvents = [];                 // eventos visibles {item, kind, t, ...} para alinear SFX (cutkit/audio)
    // orden: pista y luego t0; dentro de subtítulos, los lockups ANTES que el raíl (registran sus retenciones)
    const capRank = (it) => (it.component === 'caption.lockup' ? 0 : 1);
    const items = (spec.items || []).slice().sort((a, b) => (TRACK_ORDER.indexOf(a.track) - TRACK_ORDER.indexOf(b.track))
      || (a.track === 'caption' ? capRank(a) - capRank(b) : 0) || (a.t0 - b.t0));
    const ctrls = [];
    const dropTweens = [];
    items.forEach((it) => {
      const def = REG[it.component];
      const root = document.getElementById(it.id);
      if (!def) { report.missing.push(it.component); console.warn('[CK] componente no registrado:', it.component); return; }
      if (!root) { report.errors.push({ id: it.id, error: 'sin root en el HTML' }); return; }
      const lay = layoutAt(it.t0 + 1e-3);
      const zBase = (TRACK_Z[it.track] != null ? TRACK_Z[it.track] : Z.graphic) + (it.z != null ? it.z : 10);
      const seg = it.track === 'layout' ? segs.find((s) => s.item === it) : null;
      // gráficos visibles durante el deslizado de un split: se montan en un envoltorio .ck-drop que cae con el panel
      // desde el fotograma 0 del deslizado (también los que empiezan dentro de la ventana)
      let mountRoot = root;
      const wins = it.track === 'graphic' ? util.slideWindows(it.t0, it.t1) : [];
      if (wins.length) {
        mountRoot = util.el('div', 'ck-drop', root, { position: 'absolute', inset: '0', zIndex: String(zBase) });
        dropTweens.push({ el: mountRoot, wins });
      }
      // recorte al panel del split: un gráfico que lo declara (`clip: 'panel'` en su CK.register) y empieza en
      // layout.split_top se monta en un envoltorio con overflow:hidden de alto = la junta → nada de lo que vuela cruza a la
      // cara. overflow y no clip-path: la QA de entrada de texto (mo.text_entry) lee los clip-path de los antepasados.
      // Si el layout cambia dentro del item, el alto sigue a cada tramo (otro split → su junta; otro layout → lienzo entero).
      if (it.track === 'graphic' && def.clip === 'panel' && lay.name === 'layout.split_top') {
        const J0 = Math.round(lay.seamY || (lay.geom && lay.geom.panelH) || H);
        const clipBox = util.el('div', 'ck-panel-clip', mountRoot, { position: 'absolute', left: '0px', top: '0px', width: W + 'px', height: J0 + 'px', overflow: 'hidden' });
        segs.filter((sg) => sg.t0 > it.t0 + 1e-3 && sg.t0 < it.t1 - 1e-3).forEach((sg) => {
          const J = sg.name === 'layout.split_top' ? Math.round((sg.geom && sg.geom.seamY) || J0) : H;
          tl.set(clipBox, { height: J }, util.snap(sg.t0));
        });
        mountRoot = clipBox;
      }
      const ctx = {
        W, H, fps, spec, item: it, tokens: tk, util, slot: Object.assign({}, lay.slot), safe: Object.assign({}, safe), safeRect: Object.assign({}, safeRect), safeAt, safeCenteredW,
        media: mediaOf(it), assetUrl, z: zBase, layout: lay, layoutAt, railY: lay.railY, seamY: lay.seamY,
        faceAt: faces.faceAt, faceMedian: faces.faceMedian, cam, content, stage, Z,
        seg, prevSeg: seg ? segs[segs.indexOf(seg) - 1] || null : null, nextSeg: seg ? segs[segs.indexOf(seg) + 1] || null : null,
        /** registra un instante en que pasa algo VISIBLE (entra un elemento, cae una ficha, se elige una opción, un corte):
         *  t en segundos de programa (se encaja al fotograma). Se llama al montar/animar (calculado, no depende del seek). */
        event(kind, t, extra) {
          if (t == null || !isFinite(t)) return;
          if (it.props && it.props.preroll && t < it.t0) t = it.t0;     // `preroll`: el sonido, en el primer fotograma visible
          global.__ckEvents.push(Object.assign({ item: it.id, component: it.component, kind: String(kind), t: util.frameT(t) }, extra || {}));
        },
      };
      try {
        const c = def.mount(mountRoot, it.props || {}, ctx);
        if (c && typeof c.animate === 'function') ctrls.push({ it, c });
        root.setAttribute('data-ck-mounted', '1');
        report.mounted.push(it.id);
      } catch (e) {
        root.setAttribute('data-ck-error', String(e && e.message || e));
        report.errors.push({ id: it.id, component: it.component, error: String(e && e.stack || e) });
        console.error('[CK] mount', it.component, it.id, e);
      }
    });
    // puerta de visibilidad de los envoltorios de media (no son .clip): display en [t0, t1), sin callbacks.
    // Va ANTES de los animate() de los componentes; los componentes animan opacidad/transform, nunca display.
    items.forEach((it) => {
      (it.media || []).forEach((m) => {
        const el = document.getElementById(m.id);
        const w = el && el.closest('.ck-mwrap');
        if (!w || w.dataset.ckPlaced !== '1') return;
        const a = util.snap(it.t0), b = util.snap(it.t1);
        if (a <= 1e-3) gsap.set(w, { display: 'block' }); else { gsap.set(w, { display: 'none' }); tl.set(w, { display: 'block' }, a); }
        tl.set(w, { display: 'none' }, b);
      });
    });
    ctrls.forEach(({ it, c }) => {
      // `preroll` (fotogramas, 1–6; en los cortes de cara a blanco, que
      // la entrada empiece 2 f antes del corte): el reloj de la animación arranca N f antes del t0 del item, pero el item
      // sigue visible desde su t0 (data-start): en el corte la entrada ya va por su fotograma N y el panel no sale vacío.
      // Sin la prop, igual que antes
      const pre = it.props && Number(it.props.preroll) > 0 ? Math.min(6, Math.round(Number(it.props.preroll))) / fps : 0;
      try { c.animate(tl, util.snap(it.t0 - pre), util.snap(it.t1), it.cues || {}); }
      catch (e) { report.errors.push({ id: it.id, component: it.component, error: String(e && e.stack || e) }); console.error('[CK] animate', it.component, it.id, e); }
    });
    dropTweens.forEach((o) => util.rideSlides(tl, o.el, o.wins));
    // cambios de layout (incluidos los implícitos): «layout.enter» en t0 y, si desliza, «layout.settle» al posarse
    segs.forEach((sg, i) => {
      if (i === 0 && sg.t0 < 1e-3) return;
      const id = sg.item ? sg.item.id : 'layout_implicit_' + i;
      global.__ckEvents.push({ item: id, component: sg.name, kind: 'layout.enter', t: util.frameT(sg.t0), enter: (sg.props && sg.props.enter) || 'cut' });
      if (sg.props && sg.props.enter === 'slide') {
        global.__ckEvents.push({ item: id, component: sg.name, kind: 'layout.settle', t: util.frameT(sg.t0 + (sg.props.enter_frames || 8) / fps) });
      }
    });
    global.__ckEvents.sort((a, b) => a.t - b.t || String(a.item).localeCompare(String(b.item)));
    global.__ckReport = report;
    return report;
  }

  const CK = {
    version: '0.2.0',
    Z, SAFE, util, tokens: {}, ease: EASE,
    register(name, def) {
      if (!name || !def || typeof def.mount !== 'function') throw new Error('CK.register: def.mount obligatorio (' + name + ')');
      def.name = name;
      REG[name] = def;
      return def;
    },
    get(name) { return REG[name]; },
    list() { return Object.keys(REG).sort(); },
    normalizeMotion,
    run,
  };
  global.CK = CK;
})(typeof window !== 'undefined' ? window : globalThis);
