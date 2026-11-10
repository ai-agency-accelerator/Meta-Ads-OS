/* cutkit · layouts — gobiernan el A-roll (pila de cámara) y la zona útil (ctx.slot) de los demás componentes.
 *
 * El RUNTIME aplica la geometría de cámara de cada layout en su t0 (corte, o `enter: "slide"` ≈5 f power3.out);
 * aquí cada layout declara su `geometry()` y dibuja su decorado (panel, junta, fondo con grano, sombra del PiP).
 * Reglas medidas (camara_transiciones.yaml): split con junta en y=1008, degradado 110 px, cara a escala 1,0 bajada
 * ~470 px (ojos ≈1180–1260), sin Ken Burns ni grano sobre la cara; PiP abajo-izquierda 390–450 px, radio 28–40;
 * tarjeta flotante 840–900 px centrada en y≈0,42·H sobre negro con grano 0,06–0,10.
 */
(function (global) {
  'use strict';
  const U = CK.util;
  const E = CK.ease;            // enter · exit · move · pop (fuente única: runtime.js)

  // ───────────────────────── fondos de panel compartidos (split, broll_full)
  /* ink (por defecto) · navy · paper (crema con grano sutil) · white · accent (oro de marca) · #hex.
   * Devuelve {light} para que el layout ajuste grano (multiply en claros) y sombra de la junta. */
  const PANEL = {
    ink: { bg: 'linear-gradient(180deg, #121016 0%, #0F0D10 60%, #0B0A0D 100%)', light: false },
    navy: { bg: 'linear-gradient(180deg, #071A29 0%, #04121D 70%)', light: false },
    paper: { bg: 'var(--ck-paper)', light: true },
    white: { bg: '#F6F6F4', light: true },
    accent: { bg: 'var(--ck-accent)', light: true },
  };
  /** key de luz suave centrado arriba (y≈34 %) con caída leve, solo en lienzos claros/de color (el grano tapa el banding).
   *  Nunca viñeta oscura en claros. */
  function keyLight(el) {
    U.el('div', 'ck-panel-key', el, { position: 'absolute', inset: '0', pointerEvents: 'none',
      background: 'radial-gradient(ellipse 85% 55% at 50% 34%, rgba(255,255,255,0.30) 0%, rgba(255,255,255,0.12) 45%, rgba(255,255,255,0) 75%)' });
  }
  function paintPanel(el, kind) {
    const k = PANEL[kind || 'ink'];
    if (k) {
      el.style.background = k.bg;
      if (k.light) keyLight(el);
      return { light: k.light, colored: kind === 'accent' };
    }
    el.style.background = U.color(kind);
    const light = isLightPanel(kind);
    if (light) keyLight(el);
    return { light, colored: true };
  }
  /** grano de los planos TINTA para todo el vídeo: `tokens.ink_grain` (número) si el layout no trae `grain` */
  function inkGrain(kind, p) {
    if (p.grain != null || (kind || 'ink') !== 'ink') return null;
    const v = CK.tokens && CK.tokens.ink_grain;
    return typeof v === 'number' && v > 0 ? Math.min(0.2, v) : null;
  }
  function panelGrain(tl, box, t0, t1, light, p, seed) {
    if (p.grain === 0) return;
    if (p._soft) {   // grano sutil de película sobre tinta: fino y en «overlay» (no levanta el negro ni deja motas grises)
      U.grain(tl, box, t0, t1, { opacity: Math.min(0.6, p.grain * 4), seed, blend: 'overlay', freq: 0.95, fixed: true });   // overlay: grano sin levantar el negro
      return;
    }
    const colored = !!(light && light.colored);
    U.grain(tl, box, t0, t1, (light === true || (light && light.light) || colored)
      ? { opacity: p.grain || 0.05, seed, blend: 'soft-light', freq: 0.75 }      // 4–6 % en soft-light sobre todo el lienzo
      : { opacity: p.grain || 0.08, seed, blend: 'normal', freq: 0.8 });
  }
  CK.paintPanel = paintPanel;   // también para gráficos que quieran el mismo papel
  /** ¿panel claro? paper/white/accent o un hex con luminancia relativa > 0,35 (los subtítulos pasan a tinta) */
  function isLightPanel(kind) {
    if (!kind) return false;
    if (PANEL[kind]) return PANEL[kind].light;
    const m = /^#?([0-9a-f]{6})$/i.exec(String(kind).trim());
    if (!m) return false;
    const n = parseInt(m[1], 16), ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => {
      v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2] > 0.35;   // el rosa #F386A1 (0,39) cuenta como claro
  }
  CK.isLightPanel = isLightPanel;
  /** raíl en planos sin cara a pantalla completa: abajo (y≈0,75·H) para dejar 260–1300 a los gráficos.
   *  OJO: por debajo de la zona segura de texto (672 px); por encima de la UI real de Shorts/Reels (420 px). */
  /** raíl del perfil: gráficos a pantalla completa, hueco bajo el
   *  mentón y tope. Sin tokens, los valores de siempre (0,71 · 70 px · 1420). */
  function railCfg(env) {
    const tk = (env && env.tokens) || {}, c = tk.caption_rail || {};
    return { yFull: tk.rail_y_full != null ? tk.rail_y_full : (c.y_full != null ? c.y_full : 0.71),
      gap: c.chin_gap != null ? c.chin_gap : 70, max: c.max_px != null ? c.max_px : 1420 };
  }
  CK.railCfg = railCfg;
  function railFull(p, env) {
    const f = p.rail_y_full != null ? p.rail_y_full : railCfg(env).yFull;
    return Math.round(U.clamp(f, 0.5, 0.78) * env.H);
  }

  // ───────────────────────── layout.full_face
  /* El presentador encuadra muy cerrado (barbilla ≈ y+h+0,03 ≈ 0,64–0,68·H) y el raíl no puede bajar de la zona segura (≤ 1248 px).
   * Reencuadre estable por tramo (mediana de la cara, sin tracking): se escala lo justo (s ≤ 1,22; el A-roll 4K tiene
   * margen ×2) anclado abajo, para que la barbilla quede por ENCIMA del raíl y el subtítulo vaya bajo ella, nunca sobre la boca.
   * Sin bordes: con dy = H·(1−s) la barbilla queda en H·(1 − s·(1 − c)) → s = (1 − objetivo)/(1 − c). */
  const FULL = { railMax: 1340, capTop: 28, gap: 22, sMax: 1.22, chinPad: 0.035 };   // raíl bajo la barbilla, sobre el cuello
  function fullFaceGeom(p, env) {
    // En algunos zooms la pantalla completa cortaba la cara arriba, en el pelo → el plano
    // base de cara completa va a ESCALA 1 y anclado en el pelo (todos los zooms escalan desde el pelo hacia abajo: el
    // mentón baja y se recorta la camiseta, nunca el pelo; ver camera.js). Si a escala 1 el pelo medido queda a < 4 % del
    // borde, se acepta tal cual (sin zoom extra) y se apunta en __ckReport.
    // «en completa quiero el texto un poquito más bajo» → raíl en mentón + 70 px como mínimo, hasta 1420 (base ≤ 1460).
    const f = env.face;
    const hd = U.headOf(f, env.t0, env.t1);
    const hairPx = hd.hair * env.H;
    if (hairPx < 0.04 * env.H && global.__ckReport) {
      global.__ckReport.camera_clamped.push({ item: 'layout.full_face', t0: env.t0, reason: 'pelo_a_escala_1_bajo_4pc', hair_px: Math.round(hairPx) });
    }
    if (p.max_scale && p.max_scale > 1 && global.__ckReport) {
      global.__ckReport.camera_clamped.push({ item: 'layout.full_face', t0: env.t0, req: p.max_scale, to: 1, reason: 'base_a_escala_1_anclada_en_pelo' });
    }
    const chinPx = Math.round(hd.chin * env.H);
    const rc = railCfg(env);
    const railY = p.rail_y != null ? p.rail_y : Math.round(U.clamp(chinPx + rc.gap, 1150, rc.max));
    return { railY, railMaxBottom: 1460, railExplicit: true, chinY: chinPx, hairY: Math.round(hairPx), faceScale: 1,
      cam: { x: 0, y: 0, scale: 1, opacity: 1, z: env.Z.cam, clip: 'inset(0px 0px 0px 0px round 0px)' } };
  }

  CK.register('layout.full_face', {
    kind: 'layout',
    geometry(p, env) { return fullFaceGeom(p, env); },
    mount() { return { animate() {} }; },
  });

  // ───────────────────────── layout.split_top
  /* En dividida el pelo debe caber arriba y la sombra ser mínima.
   * Geometría con la cabeza ENTERA: la parte de arriba del pelo queda ≥ 16 px por debajo de la junta J durante el tramo,
   * el labio inferior por encima de y=1632 (UI de Shorts/Reels) y los ojos por encima de 1500 si se puede. El presentador encuadra muy
   * cerrado (cabeza ≈ 1000 px a ×1), así que J baja de 1008 a 900 (el panel pierde solo 46 px: slot 828) y la cara se
   * escala lo justo (≥ 0,82; ≈ 0,90 con el encuadre habitual) con los laterales rellenos por una copia desenfocada del A-roll (nunca barras).
   * Fundido panel → cara de 48 px y sombra de la junta mínima (0,03 claros / 0,08 oscuros). */
  /* En 50/50 la cabeza debe verse ENTERA (algo más pequeña si hace falta) y sin sombra extra
   * en la dividida. Junta en J = 960 (mitad exacta), corte limpio (sin sombra ni fundido) y la cabeza ENTERA
   * con aire: el pelo MEDIDO (spec.aroll.hair) ≥ 40 px bajo la junta (fill) o bajo el borde de la tarjeta (card).
   *   card (por defecto): el vídeo es una tarjeta inserta en la mitad de abajo, sobre el mismo lienzo del panel (continuo),
   *        esquinas de 28 px, SIN sombra; márgenes 40 arriba/abajo y laterales iguales (los que deja la escala).
   *   fill: a todo el ancho; los laterales que deja la escala se completan con la placa estirada (sin desenfoque) bajo un
   *        fundido de 64 px. */
  const SPLIT = { J: 960, air: 40, mouthMax: 1690, chinPad: 24, cardGapTop: 40, cardGapBottom: 40, cardRadius: 28,
    sideFeather: 64, sMin: 0.6 };
  function splitGeom(p, env) {
    const H = env.H, W = env.W;
    const hd = U.headOf(env.face || { x: 0.22, y: 0.3, w: 0.58, h: 0.33 }, env.t0, env.t1);
    const hl = hd.hair * H, ml = hd.mouth * H, cl = hd.chin * H;
    const J = p.junction_y != null ? p.junction_y : SPLIT.J;
    const mode = p.face_fit || 'fill';                 // por defecto «fill» (a todo el ancho)
    const cx = hd.cx * W;
    // aire sobre el pelo: `face_air` cuando la cabeza se mueve más que el aire por defecto (outro sin toma 50/50)
    const air = p.face_air != null ? p.face_air : SPLIT.air;
    if (mode === 'fill') {
      let s = Math.min(1, (SPLIT.mouthMax - (J + air)) / Math.max(1, ml - hl), (H - SPLIT.chinPad - (J + air)) / Math.max(1, cl - hl));
      if (p.face_scale != null) s = p.face_scale;
      s = Math.max(SPLIT.sMin, Math.round(s * 1000) / 1000);
      const y = Math.round(J + air - s * hl);
      const x = Math.round(s >= 1 ? U.clamp(W / 2 - s * cx, W * (1 - s), 0) : U.clamp(W / 2 - s * cx, 0, W * (1 - s)));
      const fe = Math.round(SPLIT.sideFeather / s);
      const mask = s < 0.999 ? `linear-gradient(to right, transparent 0px, #000 ${fe}px, #000 calc(100% - ${fe}px), transparent 100%)` : 'none';
      return { mode, J, s, x, y, mask, fill: s < 0.999, z: env.Z.cam, clip: 'inset(0px 0px 0px 0px round 0px)',
        // Los subtítulos van justo encima y alineados con la separación → la TINTA del subtítulo acaba 12 px
        // por encima de la junta; el slot de los gráficos acaba ≥ 24 px por encima del subtítulo (1 línea ≈ 80 px)
        slotH: J - 60, railY: J, railInkCenter: J, lockCenter: J,
        head: { hair: Math.round(y + s * hl), mouth: Math.round(y + s * ml), chin: Math.round(y + s * cl) } };
    }
    // card
    const top = J + SPLIT.cardGapTop, bottom = H - SPLIT.cardGapBottom;
    let s = (bottom - top - SPLIT.air - SPLIT.chinPad) / Math.max(1, cl - hl);
    if (p.face_scale != null) s = p.face_scale;
    s = U.clamp(Math.round(s * 1000) / 1000, SPLIT.sMin, 1);
    const cw = Math.min(W - 2 * 48, Math.round(W * s) - 24);           // 12 px de holgura a cada lado para centrar la cara
    const mx = Math.round((W - cw) / 2);
    const y = Math.round(top + SPLIT.air - s * hl);
    const x = Math.round(U.clamp(W / 2 - s * cx, (W - mx) - W * s, mx));
    const R = SPLIT.cardRadius;
    // recorte de la tarjeta en coordenadas locales del fotograma (el clip se escala con la placa → radio R en pantalla)
    const L = (mx - x) / s, T = (top - y) / s, Rr = W - ((W - mx) - x) / s, B = H - (bottom - y) / s;
    const clip = `inset(${T.toFixed(1)}px ${Rr.toFixed(1)}px ${B.toFixed(1)}px ${L.toFixed(1)}px round ${(R / s).toFixed(1)}px)`;
    return { mode, J, s, x, y, mask: 'none', fill: false, z: env.Z.layoutBack + 8, clip, card: { x: mx, y: top, w: cw, h: bottom - top, r: R },
      slotH: J + SPLIT.cardGapTop - 12 - 80 - 24, railY: J + SPLIT.cardGapTop - 40,
      railInkBottom: J + SPLIT.cardGapTop - 12, lockBase: J + SPLIT.cardGapTop - 12,
      head: { hair: Math.round(y + s * hl), mouth: Math.round(y + s * ml), chin: Math.round(y + s * cl) } };
  }
  CK.register('layout.split_top', {
    kind: 'layout',
    geometry(p, env) {
      // Vídeo 50/50 del presentador (spec.aroll.split_src): dentro de split_ranges la mitad de abajo es ESE vídeo (escala 1, todo el
      // ancho, recortado en la costura); el A-roll se oculta. Junta = costura exacta. Subtítulo centrado en la línea.
      if (env.splitVideo && env.splitVideo(env.t0, env.t1)) {
        const J = env.splitSeam || 960;
        return {
          slot: { x: 0, y: 0, w: env.W, h: J - 60 },
          panelH: J, seamY: J, railY: J, railInkCenter: J, lockCenter: J, railMaxBottom: J + 80,
          panelLight: isLightPanel(p.panel_bg), feather: 0, faceFit: 'split_video', splitVideo: true, faceScale: 1,
          cam: { x: 0, y: 0, scale: 1, opacity: 0, z: env.Z.cam, clip: 'inset(0px 0px 0px 0px round 0px)', mask: 'none', fill: false, splitVideo: true },
        };
      }
      const g = splitGeom(p, env);
      const J = g.J;
      const light = isLightPanel(p.panel_bg);
      return {
        slot: { x: 0, y: 0, w: env.W, h: g.slotH },
        panelH: J, seamY: J,
        railY: g.railY,                    // subtítulo centrado en la línea (centro de la tinta = railInkCenter)
        railInkCenter: g.railInkCenter != null ? g.railInkCenter : J, railMaxBottom: J + 80,
        lockCenter: g.lockCenter != null ? g.lockCenter : J,
        panelLight: light,
        feather: 0,
        faceFit: g.mode, card: g.card || null, head: g.head, faceScale: g.s,
        cam: { x: g.x, y: g.y, scale: g.s, opacity: 1, z: g.z, clip: g.clip, mask: g.mask, fill: g.fill },
      };
    },
    mount(root, p, ctx) {
      const G = ctx.seg ? ctx.seg.geom : { seamY: SPLIT.J, faceFit: 'fill' };
      const J = G.seamY || SPLIT.J;
      const card = G.faceFit === 'card';
      const sv = !!G.splitVideo;
      // lienzo del panel: en «card» ocupa TODO el plano (continuo detrás de la tarjeta); en «fill», solo la mitad de
      // arriba con corte limpio (sin sombra ni fundido)
      const panel = U.el('div', 'ck-split-panel', root);
      U.box(panel, { x: 0, y: 0, w: ctx.W, h: card ? ctx.H : J });
      panel.style.zIndex = String(ctx.Z.layoutBack + 5);
      const look = paintPanel(panel, p.panel_bg || 'ink');
      const grainBox = U.el('div', 'ck-split-grain', panel, { position: 'absolute', inset: '0', overflow: 'hidden' });
      return {
        animate(tl, t0, t1) {
          const ig = inkGrain(p.panel_bg || 'ink', p);
          panelGrain(tl, grainBox, t0, t1, look, ig != null && p.grain == null ? Object.assign({}, p, { grain: ig, _soft: true }) : p, (ctx.item.id || 'split') + ':g');
          if (p.enter === 'slide' && !sv) {
            // el panel BAJA desde arriba con su contenido (~8 f, power3.out); la cámara la mueve el runtime con la misma
            // curva (en «card», la placa se encoge hasta la tarjeta), la media cae con splitDrop y los gráficos en .ck-drop.
            // Con el vídeo 50/50 el lienzo entra en corte (no puede asomar nada por encima de la costura) y solo cae el contenido.
            const dur = (p.enter_frames || 8) / ctx.fps;
            tl.fromTo(panel, { y: -J - 40 }, { y: 0, duration: dur, ease: E.enter, immediateRender: false }, t0);
          }
        },
      };
    },
  });

  // ───────────────────────── layout.broll_full
  CK.register('layout.broll_full', {
    kind: 'layout',
    geometry(p, env) {
      const hide = p.aroll !== 'behind';
      return {
        slot: { x: 0, y: 0, w: env.W, h: env.H },
        light: hide && isLightPanel(p.panel_bg || p.bg),
        railY: railFull(p, env), railMaxBottom: 1460,
        cam: { opacity: hide ? 0 : 1, z: env.Z.cam },
      };
    },
    mount(root, p, ctx) {
      if (p.aroll === 'behind') return { animate() {} };
      const bg = U.el('div', 'ck-broll-bg', root, { inset: '0', position: 'absolute', overflow: 'hidden' });
      bg.style.zIndex = String(ctx.Z.layoutBack + 1);
      const kind = p.panel_bg || p.bg || 'ink';
      const look = paintPanel(bg, kind);
      if (!look.light) {                       // en claros sin viñeta: el blanco tiene que salir blanco
        U.el('div', 'ck-broll-vig', bg, { position: 'absolute', inset: '0',
          background: 'radial-gradient(120% 85% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)' });
      }
      return {
        animate(tl, t0, t1) {
          // tinta lisa salvo que se pida grano: `grain` del layout o, para todos los planos tinta del vídeo,
          // `tokens.ink_grain` del plan (grano sutil opcional, 0,03–0,06)
          const ig = inkGrain(kind, p);
          if (kind === 'ink' && ig == null) return;
          panelGrain(tl, bg, t0, t1, look, ig != null && p.grain == null ? Object.assign({}, p, { grain: ig, _soft: true }) : p, (ctx.item.id || 'broll') + ':g');
        },
      };
    },
  });

  // ───────────────────────── layout.card_float
  const CARD = { w: 880, cy: 0.42 };
  CK.register('layout.card_float', {
    kind: 'layout',
    geometry(p, env) {
      const w = U.clamp(p.card_width || CARD.w, 600, 960);
      const cy = Math.round((p.center_y != null ? p.center_y : CARD.cy) * env.H);
      const h = Math.min(p.max_height || 760, 2 * (cy - env.safe.top + 40));
      const slot = { x: Math.round((env.W - w) / 2), y: Math.round(cy - h / 2), w, h: Math.round(h) };
      return {
        slot,
        light: (p.bg || 'ink') === 'paper',
        railY: Math.max(railFull(p, env), slot.y + slot.h + 90), railMaxBottom: 1460,
        cam: { opacity: 0, z: env.Z.cam },
      };
    },
    mount(root, p, ctx) {
      const theme = p.bg || 'ink';
      const base = theme === 'navy' ? 'var(--ck-navy)' : theme === 'paper' ? '#E9E7E3' : '#050506';
      const bg = U.el('div', 'ck-card-bg', root, { position: 'absolute', inset: '0', background: base });
      bg.style.zIndex = String(ctx.Z.layoutBack + 1);
      // luz ambiental muy baja en el centro (profundidad, no «glow»): misma tinta, solo luminancia
      const amb = U.el('div', 'ck-card-amb', root, { position: 'absolute', inset: '0' });
      amb.style.zIndex = String(ctx.Z.layoutBack + 2);
amb.style.background = 'none';   // sin foco radial (banding en H.264); la profundidad la dan viñeta y grano
      const vig = U.el('div', 'ck-card-vig', root, { position: 'absolute', inset: '0' });
      vig.style.zIndex = String(ctx.Z.layoutBack + 4);
      vig.style.background = theme === 'paper' ? 'none' : 'radial-gradient(115% 80% at 50% 45%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.6) 100%)';
      return {
        animate(tl, t0, t1) {
          // grano a 12 fps SOLO en el fondo (por debajo de la tarjeta)
          U.grain(tl, root, t0, t1, {
            opacity: p.grain != null ? p.grain : (theme === 'paper' ? 0.05 : 0.07), seed: (ctx.item.id || 'card') + ':g',
            blend: theme === 'paper' ? 'soft-light' : 'normal', z: ctx.Z.layoutBack + 3, freq: 0.75,
          });
          if (p.enter === 'slide') {
            tl.fromTo([bg, amb, vig], { opacity: 0 }, { opacity: 1, duration: 5 / ctx.fps, ease: E.enter, immediateRender: false }, t0);
          }
        },
      };
    },
  });

  // ───────────────────────── layout.pip
  const PIP = { w: 420, h: 480, r: 34, x: 65, y: 1040 };
  function pipGeom(p, env) {
    const w = U.clamp(p.width || PIP.w, 300, 520);
    const h = Math.round(w * (p.shape === 'circle' ? 1 : (p.aspect || PIP.h / PIP.w)));
    const pos = p.position || 'bottom_left';
    const x = pos.endsWith('right') ? env.W - env.safe.right - w : (p.x != null ? p.x : PIP.x);
    const y = pos.startsWith('top') ? env.safe.top + 20 : (p.y != null ? p.y : PIP.y);
    const r = p.shape === 'circle' ? w / 2 : (p.radius || PIP.r);
    // escala: la cara ocupa ~58 % del alto de la tarjeta
    const f = env.face;
    const faceH = Math.max(0.1, f.h) * env.H;
    const s = U.clamp((h * (p.face_fill || 0.58)) / faceH, 0.2, 1);
    const cx = (f.x + f.w / 2) * env.W, cy = (f.y + f.h * 0.48) * env.H;
    let cw = w / s, ch = h / s;
    let left = U.clamp(cx - cw / 2, 0, env.W - cw), top = U.clamp(cy - ch / 2, 0, env.H - ch);
    const clip = `inset(${top.toFixed(1)}px ${(env.W - left - cw).toFixed(1)}px ${(env.H - top - ch).toFixed(1)}px ${left.toFixed(1)}px round ${(r / s).toFixed(1)}px)`;
    return { box: { x, y, w, h, r }, cam: { x: x - s * left, y: y - s * top, scale: s, opacity: 1, z: env.Z.broll + 50, clip } };
  }
  CK.register('layout.pip', {
    kind: 'layout',
    geometry(p, env) {
      const g = pipGeom(p, env);
      return { slot: { x: 0, y: 0, w: env.W, h: env.H }, pip: g.box, cam: g.cam };
    },
    mount(root, p, ctx) {
      const b = ctx.seg && ctx.seg.geom.pip;
      if (!b) return { animate() {} };
      // fondo por si no hay recurso detrás
      const bg = U.el('div', 'ck-pip-bg', root, { position: 'absolute', inset: '0', background: 'var(--ck-ink)' });
      bg.style.zIndex = String(ctx.Z.layoutBack + 1);
      const shadow = U.el('div', 'ck-pip-shadow', root);
      U.box(shadow, b);
      Object.assign(shadow.style, { borderRadius: b.r + 'px', boxShadow: '0 24px 60px rgba(0,0,0,.45), 0 4px 12px rgba(0,0,0,.35)', background: '#000' });
      shadow.style.zIndex = String(ctx.Z.broll + 45);
      const ring = U.el('div', 'ck-pip-ring', root);
      U.box(ring, b);
      Object.assign(ring.style, { borderRadius: b.r + 'px', boxShadow: 'inset 0 0 0 2px rgba(255,255,255,.16)' });
      ring.style.zIndex = String(ctx.Z.layoutFront + 1);
      return {
        animate(tl, t0) {
          if (p.enter === 'slide') {
            const d = (p.enter_frames || 8) / ctx.fps;
            tl.fromTo([shadow, ring], { opacity: 0 }, { opacity: 1, duration: d, ease: E.enter, immediateRender: false }, t0);
          }
        },
      };
    },
  });
})(typeof window !== 'undefined' ? window : globalThis);
