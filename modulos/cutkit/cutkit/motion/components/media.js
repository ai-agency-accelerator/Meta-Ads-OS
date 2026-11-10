/* cutkit · media (B-roll): media.full, media.slot, media.screenshot_card, media.scroll, media.ui_focus, media.device
 *
 * Cada <video>/<img> del item vive en el HTML estático: .ck-mwrap (sin data-start) > .ck-mzoom (sin data-start) > media
 * con data-start/duration. Aquí solo se posicionan y animan los ENVOLTORIOS (wrap, zoom) y el decorado del root.
 * Nunca se mueve el <video> de su envoltorio ni se animan sus dimensiones.
 * Reglas: capturas e interfaces reales no rebotan (no_back_capturas); el recurso ENTRA ya visible en su t0 (la
 * antelación de ~155 ms la pone el compilador); dentro del mismo layout el cambio de recurso es corte seco.
 */
(function () {
  'use strict';
  const U = CK.util;
  const E = CK.ease;            // enter · exit · move · pop (fuente única: runtime.js)

  // ───────────────────────── helpers
  function aspectOf(m) {
    const i = m.ckInfo || {};
    if (i.width && i.height) return i.width / i.height;
    if (m.tagName === 'IMG' && m.naturalWidth) return m.naturalWidth / m.naturalHeight;
    if (m.tagName === 'VIDEO' && m.videoWidth) return m.videoWidth / m.videoHeight;
    return i.kind === 'image' ? 1 : 16 / 9;
  }
  function naturalOf(m) {
    const i = m.ckInfo || {};
    if (i.width && i.height) return { w: i.width, h: i.height };
    if (m.tagName === 'IMG' && m.naturalWidth) return { w: m.naturalWidth, h: m.naturalHeight };
    if (m.tagName === 'VIDEO' && m.videoWidth) return { w: m.videoWidth, h: m.videoHeight };
    return { w: 1600, h: 900 };
  }
  /** ¿es vídeo? Por el tipo declarado en el spec, NUNCA por la etiqueta: en la captura en paralelo HF puede servir el
   *  vídeo como <img> de fotogramas en algunos workers, y la caja cambiaba de tamaño fotograma a fotograma (un zoom
   *  raro que parpadeaba arriba en el 50/50). */
  function isVideo(m) { const i = m.ckInfo || {}; return i.kind ? i.kind === 'video' : m.tagName === 'VIDEO'; }
  /** caja de aspecto `a` contenida en `area` (centrada) */
  function contain(a, area, maxW) {
    let w = Math.min(area.w, maxW || area.w), h = w / a;
    if (h > area.h) { h = area.h; w = h * a; }
    return { x: Math.round(area.x + (area.w - w) / 2), y: Math.round(area.y + (area.h - h) / 2), w: Math.round(w), h: Math.round(h) };
  }
  function placeWrap(m, b, z) { return U.placeMedia(m, b, z); }
  /** logos/SVG/PNG con transparencia: nunca en cover (se verían gigantes) */
  function isGraphic(m) {
    const i = m.ckInfo || {};
    const src = String(i.src || m.getAttribute('src') || '').toLowerCase();
    return i.kind === 'svg' || src.endsWith('.svg') || /(^|[_/-])logo/.test(String(i.asset || m.ckAsset || src));
  }
  const isSplit = (ctx) => ctx.layout && ctx.layout.name === 'layout.split_top';
  const isCard = (ctx) => ctx.layout && ctx.layout.name === 'layout.card_float';
  /** zona para tarjetas según el layout (las capturas tienen texto: lejos de la UI superior de Shorts/Reels) */
  function cardArea(ctx) {
    if (isSplit(ctx)) {
      const bottom = ctx.slot.y + ctx.slot.h;          // J − degradado − 24 (no invade la junta)
      return { x: 60, y: 170, w: ctx.W - 120, h: bottom - 170 };
    }
    if (isCard(ctx)) return Object.assign({}, ctx.slot);
    if (ctx.layout && ctx.layout.name === 'layout.broll_full') return { x: 65, y: 288, w: ctx.W - 130, h: 1240 - 288 };   // raíl en 1363
    return { x: 60, y: ctx.safe.top, w: ctx.W - 120, h: ctx.H - ctx.safe.top - ctx.safe.bottom };
  }
  /** recorta un elemento con el degradado de la junta del split (máscara en coordenadas locales del elemento) */
  function seamMask(el, top, J, F) {
    const a = Math.round(J - top - F), b = Math.round(J - top);
    const m = `linear-gradient(to bottom, #000 ${a}px, transparent ${b}px)`;
    el.style.webkitMaskImage = m; el.style.maskImage = m;
  }
  /** caja del teléfono: en el split, grande y «naciendo» de la junta (se corta con su degradado) */
  function phoneBody(ctx, area, p) {
    if (isSplit(ctx)) {
      const h = p.height || 1180, w = Math.round(h / 2.06);
      return { x: Math.round((ctx.W - w) / 2), y: 190, w, h, cut: true };
    }
    const h = Math.min(area.h, p.height || 1180), w = Math.round(h / 2.06);
    return { x: Math.round(area.x + (area.w - w) / 2), y: Math.round(area.y + (area.h - h) / 2), w, h, cut: false };
  }
  /** si un split entra deslizando mientras el recurso está en pantalla, el recurso cae con el panel (desde el
   *  fotograma 0 del deslizado). Devuelve el instante en que acaba la caída (0 si no hay): las derivas de `y` del
   *  mismo elemento empiezan después, para no solaparse. */
  function splitDrop(tl, ctx, els) {
    const wins = U.slideWindows(ctx.item.t0, ctx.item.t1);
    return wins.length ? U.rideSlides(tl, els, wins) : 0;
  }
  /** Ken Burns del recurso (nunca de la cara) en el envoltorio de zoom */
  function kenBurns(tl, zoom, box, t0, t1, amount, dir) {
    if (!amount) return;
    const s0 = dir === 'out' ? 1 + amount : 1, s1 = dir === 'out' ? 1 : 1 + amount;
    const c = { x: box.w / 2, y: box.h / 2 };
    tl.fromTo(zoom, { x: Math.round(c.x * (1 - s0)), y: Math.round(c.y * (1 - s0)), scale: s0 },
      { x: Math.round(c.x * (1 - s1)), y: Math.round(c.y * (1 - s1)), scale: s1, duration: Math.max(0.1, t1 - t0), ease: E.move, immediateRender: false }, t0);
  }
  function cardStyle(w, r) {
    Object.assign(w.style, { borderRadius: (r || 28) + 'px', boxShadow: 'var(--ck-shadow-3)', background: '#111' });
  }
  /** capa por encima del wrap con la misma caja (hairline, brillo, anillo…) */
  function overlayFor(root, b, z, r) {
    const o = U.el('div', 'ck-m-over', root);
    U.box(o, b);
    Object.assign(o.style, { borderRadius: (r || 28) + 'px', overflow: 'hidden', zIndex: String(z), boxShadow: 'inset 0 0 0 1.5px rgba(255,255,255,.10)' });
    return o;
  }
  function mediaFit(m, fit, pos) {
    m.style.objectFit = fit || 'cover';
    if (pos) m.style.objectPosition = pos;
  }
  /** Salida del recurso. Por defecto, corte seco: el envoltorio se apaga en t1 (puerta de visibilidad del
   *  runtime) y compile.py ya no cruza nunca una captura real con otra pieza. `exit: "fade"` = se funde con el fondo del
   *  panel en sus últimos 5 f, sin nada encima. Las capas propias (anillo, oscurecido, marco) se apagan en t1. */
  function mediaExit(tl, els, t0, t1, p, fps, extra) {
    const all = els.concat(extra || []).filter(Boolean);
    if (p.exit === 'fade') {
      const d = Math.min(5 / fps, Math.max(1 / fps, (t1 - t0) / 4));
      tl.fromTo(all, { opacity: 1 }, { opacity: 0, duration: d, ease: E.exit, immediateRender: false }, U.snap(t1 - d));
    }
    if (extra && extra.length) tl.set(extra, { opacity: 0 }, U.snap(t1));
  }

  // ───────────────────────── media.full — pantalla completa, cover + Ken Burns sutil
  CK.register('media.full', {
    kind: 'media',
    mount(root, p, ctx) {
      const m = ctx.media[0];
      if (!m) return { animate() {} };
      const fit = p.fit || (isGraphic(m) ? 'contain' : 'cover');
      const b = fit === 'contain' && isGraphic(m) ? { x: 240, y: 560, w: ctx.W - 480, h: 640 } : { x: 0, y: 0, w: ctx.W, h: ctx.H };
      const w = placeWrap(m, b, ctx.z);
      mediaFit(m, fit, p.position);
      if (fit === 'contain' && !isGraphic(m)) w.style.background = U.color(p.bg || 'ink');
      return {
        animate(tl, t0, t1) {
          ctx.event('media.enter', t0);
          const enter = p.enter || 'cut';
          if (enter === 'fade') tl.fromTo(w, { opacity: 0 }, { opacity: 1, duration: 4 / ctx.fps, ease: E.enter, immediateRender: false }, t0);
          if (enter === 'zoom') {
            tl.fromTo(w, { scale: 1.1, filter: 'blur(8px)' }, { scale: 1, filter: 'blur(0px)', duration: 6 / ctx.fps, ease: E.enter, immediateRender: false }, t0);
            tl.set(w, { filter: 'none' }, t0 + 6 / ctx.fps);
          }
          kenBurns(tl, m.ckZoom, b, t0, t1, p.kb != null ? p.kb : 0.04, p.kb_dir);
          mediaExit(tl, [w], t0, t1, p, ctx.fps);
        },
      };
    },
  });

  // ───────────────────────── media.slot — el recurso en la zona útil del layout activo
  CK.register('media.slot', {
    kind: 'media',
    mount(root, p, ctx) {
      const m = ctx.media[0];
      if (!m) return { animate() {} };
      const a = aspectOf(m);
      if (!p.fit && isGraphic(m)) p = Object.assign({}, p, { fit: 'contain' });
      let b, mode, framed = false;
      if (isSplit(ctx)) {
        mode = 'split';
        if (p.fit === 'contain') {
          const J = ctx.layout.seamY || 1008;
          // logos y gráficos: tamaño de icono (≤ 440 px) centrado en la parte visible del panel
          const bottom = ctx.slot.y + ctx.slot.h;
          // capturas reales: TODO el ancho útil (950 px) para que su texto se lea en el móvil
          // capturas y vídeos reales: todo el panel por encima del raíl del subtítulo (a sangre si el aspecto coincide)
          const railTopC = (ctx.layout.railY || ctx.layout.seamY || 1008) - 46;
          const area = isGraphic(m) ? { x: (ctx.W - 440) / 2, y: Math.round((170 + bottom) / 2 - 220), w: 440, h: 440 }
            : (isVideo(m) ? { x: 0, y: 0, w: ctx.W, h: railTopC } : { x: 65, y: 250, w: ctx.W - 130, h: bottom - 250 });
          b = contain(a, area);
        } else if ((ctx.layout.geom || {}).faceFit !== 'card') {
          // en el 50/50 con corte limpio (fill y vídeo 50/50) la captura llena el
          // panel a sangre HASTA LA JUNTA, con corte limpio como el panel (sin sombra ni fundido). Antes acababa en
          // J − 60 con un degradado de 110 px (el `feather: 0` del layout caía en `|| 110`) y dejaba una franja de panel
          // de 60 px entre la captura y la junta que parecía un fallo. El subtítulo va centrado en la junta, como sobre la cara.
          const J = ctx.layout.seamY || 960;
          b = { x: 0, y: 0, w: ctx.W, h: J };
          const F = ctx.layout.feather || 0;
          if (F > 0) {
            const mask = `linear-gradient(to bottom, #000 calc(100% - ${F}px), transparent)`;
            m.ckWrap.style.webkitMaskImage = mask; m.ckWrap.style.maskImage = mask;
          }
        } else {
          // split en «card» (el lienzo sigue detrás de la tarjeta de la cara): el recurso acaba antes del raíl del
          // subtítulo (nunca texto sobre texto) y se funde con el lienzo
          const railTop = (ctx.layout.railY || ctx.layout.seamY || 1008) - 46;
          b = { x: 0, y: 0, w: ctx.W, h: Math.min(ctx.layout.seamY || 1008, Math.max(ctx.slot.y + ctx.slot.h, 0) || railTop, railTop) };
          const F = ctx.layout.feather || 110;
          const mask = `linear-gradient(to bottom, #000 calc(100% - ${F}px), transparent)`;
          m.ckWrap.style.webkitMaskImage = mask; m.ckWrap.style.maskImage = mask;
        }
      } else if (isCard(ctx)) {
        mode = 'card';
        b = contain(a, ctx.slot);
        cardStyle(m.ckWrap, p.radius || 28);
      } else {
        mode = 'full';
        const bf = !!(ctx.layout && ctx.layout.name === 'layout.broll_full');
        // pantalla completa: logos a tamaño de icono; capturas a TODO el ancho seguro (950 px, escalando hacia arriba si
        // hace falta) centradas en la banda útil de gráficos, por encima del raíl (288–1240 en broll_full: la misma zona
        // y el mismo centro, y≈764, que scene.capture3d)
        b = p.fit !== 'contain' ? { x: 0, y: 0, w: ctx.W, h: ctx.H }
          : isGraphic(m) ? contain(a, { x: 200, y: 520, w: ctx.W - 400, h: 640 })
          : contain(a, { x: 65, y: 288, w: ctx.W - 130, h: bf ? 952 : 712 });
        // una captura o vídeo REAL en contain a pantalla completa lleva el marco del resto de capturas a
        // pantalla completa (scene.capture3d: esquina pequeña, filo claro, sombra); `frame: false` lo quita
        framed = bf && p.fit === 'contain' && !isGraphic(m) && p.frame !== false;
      }
      const w = placeWrap(m, b, ctx.z);
      mediaFit(m, p.fit === 'contain' ? 'contain' : 'cover', p.position);
      if (isGraphic(m)) { w.style.overflow = 'visible'; m.style.filter = 'drop-shadow(0 18px 40px rgba(0,0,0,.45))'; }
      // marco medido en una captura real (scene.capture3d): esquina ≈ 10 px y filo claro de 2 px (≈ #2c2e30)
      if (framed) cardStyle(w, p.radius || 10);
      const over = mode === 'card' ? overlayFor(root, b, ctx.z + 1, p.radius || 28) : framed ? overlayFor(root, b, ctx.z + 1, p.radius || 10) : null;
      if (framed) over.style.boxShadow = 'inset 0 0 0 2px rgba(255,255,255,.16)';
      return {
        animate(tl, t0, t1) {
          ctx.event('media.enter', t0);
          const els = over ? [w, over] : [w];
          const dropEnd = splitDrop(tl, ctx, els);
          let entered = dropEnd > 0 && dropEnd - t0 > -1e-3;
          let tIdle = Math.max(t0, dropEnd);
          if (!entered && isGraphic(m) && p.enter !== 'cut' && mode !== 'card') {
            // logo: aparece en su palabra con un asentamiento corto (sin rebote: es una marca)
            tl.fromTo(w, { scale: 0.86, opacity: 0 }, { scale: 1, opacity: 1, duration: 5 / ctx.fps, ease: E.enter, immediateRender: false }, t0);
            entered = true;
          }
          if (!entered && mode === 'card' && p.enter !== 'cut') {
            const d = 8 / ctx.fps;
            tl.fromTo(els, { y: 70, scale: 0.94, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: d, ease: p.settle ? E.pop : E.enter, immediateRender: false }, t0);
            tIdle = t0 + d;
          }
          if (mode === 'card' && t1 - tIdle > 0.6) {
            tl.fromTo(els, { y: 0 }, { y: -14, duration: t1 - tIdle, ease: E.move, immediateRender: false }, tIdle);
          }
          if (p.fit !== 'contain') kenBurns(tl, m.ckZoom, b, t0, t1, p.kb != null ? p.kb : (mode === 'card' ? 0.025 : 0.035), p.kb_dir);
          mediaExit(tl, els, t0, t1, p, ctx.fps);
        },
      };
    },
  });

  // ───────────────────────── media.screenshot_card — captura en tarjeta con entrada 3D sutil y parallax
  CK.register('media.screenshot_card', {
    kind: 'media',
    mount(root, p, ctx) {
      const m = ctx.media[0];
      if (!m) return { animate() {} };
      const area = cardArea(ctx);
      const a = aspectOf(m);
      const R = p.radius || 28;
      let w = Math.min(area.w, p.width || 940), h = Math.round(w / a);
      let crop = false;
      if (h > area.h) { h = area.h; crop = true; }
      const b = { x: Math.round(area.x + (area.w - w) / 2), y: Math.round(area.y + (area.h - h) / 2), w: Math.round(w), h };
      const wrap = placeWrap(m, b, ctx.z);
      cardStyle(wrap, R);
      mediaFit(m, 'cover', crop ? 'top center' : (p.position || 'center'));
      const over = overlayFor(root, b, ctx.z + 1, R);
      const sheen = U.el('div', 'ck-sheen', over, { position: 'absolute', inset: '-20% -60%', mixBlendMode: 'screen',
        background: 'linear-gradient(105deg, transparent 42%, rgba(255,255,255,.0) 45%, rgba(255,255,255,.28) 50%, rgba(255,255,255,0) 55%, transparent 58%)' });
      sheen.setAttribute('data-layout-ignore', '');
      return {
        animate(tl, t0, t1) {
          ctx.event('media.enter', t0);
          const els = [wrap, over];
          gsap.set(els, { transformPerspective: 1600, transformOrigin: '50% 60%' });
          const d = (p.enter_frames || 12) / ctx.fps;
          const life = t1 - t0;
          const dropEnd = splitDrop(tl, ctx, els);
          if (!dropEnd && p.enter !== 'cut') {
            tl.fromTo(els, { rotationX: 22, y: 150, scale: 0.9, opacity: 0 },
              { rotationX: 6, y: 0, scale: 1, opacity: 1, duration: Math.min(d, life * 0.3), ease: E.enter, immediateRender: false }, t0);
          } else gsap.set(els, { rotationX: 6 });
          const tIdle = Math.max(t0 + (p.enter === 'cut' && !dropEnd ? 0 : Math.min(d, life * 0.3)), dropEnd);
          if (t1 - tIdle > 0.3) {
            tl.fromTo(els, { rotationX: 6, rotationY: 0, y: 0 },
              { rotationX: 0, rotationY: p.parallax === false ? 0 : -3, y: -18, duration: t1 - tIdle, ease: E.move, immediateRender: false }, tIdle);
          }
          if (p.sheen !== false && life > 1.2) {
            tl.fromTo(sheen, { xPercent: -60 }, { xPercent: 60, duration: 0.8, ease: E.move, immediateRender: false }, tIdle);
          } else gsap.set(sheen, { opacity: 0 });
          mediaExit(tl, els, t0, t1, p, ctx.fps);
        },
      };
    },
  });

  // ───────────────────────── media.scroll — captura larga con scroll a paradas (tarjeta, teléfono o panel)
  let scrollUid = 0;
  CK.register('media.scroll', {
    kind: 'media',
    mount(root, p, ctx) {
      const m = ctx.media[0];
      if (!m) return { animate() {} };
      const area = cardArea(ctx);
      const frame = p.frame || 'card';
      const nat = naturalOf(m);
      let b, R, chrome = null, island = null, phoneCut = null;
      if (frame === 'phone') {
        // teléfono: alto según el área; pantalla con la captura a lo ancho
        const body = phoneBody(ctx, area, p);
        const bz = 14; R = 60;
        b = { x: body.x + bz, y: body.y + bz, w: body.w - 2 * bz, h: body.h - 2 * bz };
        chrome = U.el('div', 'ck-device ck-device-phone', root);
        U.box(chrome, body);
        Object.assign(chrome.style, { zIndex: String(ctx.z - 1), borderRadius: (R + bz) + 'px', boxShadow: 'var(--ck-shadow-3), inset 0 0 0 1.5px rgba(255,255,255,.10)',
          background: 'linear-gradient(150deg, #34333a 0%, #121115 38%, #222127 100%)' });
        island = U.el('div', 'ck-device-island', root);
        U.box(island, { x: Math.round(body.x + body.w / 2 - 62), y: body.y + 26, w: 124, h: 36 });
        Object.assign(island.style, { borderRadius: '18px', background: '#000', zIndex: String(ctx.z + 2) });
        if (body.cut) { const J = ctx.layout.seamY || 1008, F = ctx.layout.feather || 110; seamMask(chrome, body.y, J, F); phoneCut = { J, F }; }
      } else if (frame === 'none') {
        b = Object.assign({}, isSplit(ctx) ? ctx.slot : area); R = 0;
      } else {
        const vw = Math.min(area.w, p.width || 900), vh = Math.min(area.h, p.height || area.h);
        b = { x: Math.round(area.x + (area.w - vw) / 2), y: Math.round(area.y + (area.h - vh) / 2), w: Math.round(vw), h: Math.round(vh) };
        R = p.radius || 28;
      }
      const wrap = placeWrap(m, b, ctx.z);
      if (R) cardStyle(wrap, R);
      wrap.style.background = '#fff';
      const ih = Math.round(b.w * nat.h / nat.w);
      Object.assign(m.style, { height: ih + 'px', bottom: 'auto', objectFit: 'fill' });
      const zoom = m.ckZoom;
      Object.assign(zoom.style, { height: ih + 'px', bottom: 'auto' });
      // desenfoque vertical por velocidad: el filtro SOLO se aplica durante cada movimiento (coste)
      const fid = 'ck-vblur-' + (++scrollUid);
      const filt = U.svgFilter(root, fid, '<feGaussianBlur stdDeviation="0 0" edgeMode="duplicate"/>');
      const gb = filt.querySelector('feGaussianBlur');
      const over = overlayFor(root, b, ctx.z + 1, R);
      if (!R) over.style.boxShadow = 'none';
      if (phoneCut) { seamMask(wrap, b.y, phoneCut.J, phoneCut.F); seamMask(over, b.y, phoneCut.J, phoneCut.F); }
      const bar = U.el('div', 'ck-scrollbar', over, { position: 'absolute', right: '10px', top: '14px', width: '7px', height: '96px', borderRadius: '4px', background: 'rgba(0,0,0,.35)', opacity: '0' });
      const range = Math.max(0, ih - b.h);
      const speedK = { slow: 1.35, normal: 1, fast: 0.7 }[p.speed || 'normal'] || 1;
      return {
        animate(tl, t0, t1) {
          ctx.event('media.enter', t0);
          const els = [wrap, over].concat(chrome ? [chrome] : [], island ? [island] : []);
          if (chrome) {
            const cx = parseFloat(chrome.style.left) + parseFloat(chrome.style.width) / 2, cy = parseFloat(chrome.style.top) + parseFloat(chrome.style.height);
            els.forEach((e) => { const bx = parseFloat(e.style.left), by = parseFloat(e.style.top); e.style.transformOrigin = `${cx - bx}px ${cy - by}px`; });
          }
          if (!splitDrop(tl, ctx, els) && p.enter !== 'cut') {
            tl.fromTo(els, { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 8 / ctx.fps, ease: E.enter, immediateRender: false }, t0);
          }
          mediaExit(tl, els, t0, t1, p, ctx.fps);
          if (range < 4) return;
          const stops = (p.stops || (range > b.h * 3 ? [0, 0.45, 1] : [0, 1])).map((v) => U.clamp(v, 0, 1));
          const moves = stops.length - 1;
          const holdStart = p.hold_start != null ? p.hold_start : 0.45;
          const holdEnd = p.hold_end != null ? p.hold_end : 0.45;
          const avail = Math.max(0.3, (t1 - t0) - holdStart - holdEnd);
          const mv = Math.min((p.move_s || 1.2) * speedK, avail / moves);
          const gap = moves > 1 ? (avail - mv * moves) / (moves - 1) : 0;
          const barRange = b.h - 28 - 96;
          for (let i = 0; i < moves; i++) {
            const at = t0 + holdStart + i * (mv + gap);
            const y0 = -Math.round(stops[i] * range), y1 = -Math.round(stops[i + 1] * range);
            tl.fromTo(zoom, { y: y0 }, { y: y1, duration: mv, ease: (E[p.ease] || E.move), immediateRender: false }, at);
            const bl = U.clamp(Math.abs(y1 - y0) / mv / 260, 0, 8).toFixed(1);
            tl.set(zoom, { filter: `url(#${fid})` }, at);
            tl.fromTo(gb, { attr: { stdDeviation: '0 0' } }, { attr: { stdDeviation: `0 ${bl}` }, duration: mv / 2, ease: E.exit, immediateRender: false }, at);
            tl.fromTo(gb, { attr: { stdDeviation: `0 ${bl}` } }, { attr: { stdDeviation: '0 0' }, duration: mv / 2, ease: E.enter, immediateRender: false }, at + mv / 2);
            tl.set(zoom, { filter: 'none' }, at + mv + 0.001);
            tl.fromTo(bar, { y: Math.round(stops[i] * barRange), opacity: 1 }, { y: Math.round(stops[i + 1] * barRange), opacity: 1, duration: mv, ease: (E[p.ease] || E.move), immediateRender: false }, at);
            tl.fromTo(bar, { opacity: 1 }, { opacity: 0, duration: 0.25, ease: E.exit, immediateRender: false }, at + mv + Math.min(0.25, Math.max(0.05, gap / 2)));
          }
        },
      };
    },
  });

  // ───────────────────────── media.ui_focus `pile` — varias capturas reales que se acumulan en una pila
  /* `pile` («Agenda, correo y Archivos se leen poco
   * y blandos; el correo dura 0,87 s; el aro pisa el asunto»): en vez de sustituirse, las capturas se ACUMULAN. Cada una
   * entra en su cue (`in`) a ancho completo con su logo encima y empuja las anteriores hacia arriba, reducidas a
   * `pile_prev` (0,6) y con su logo al lado; el aro oro se dibuja FUERA del borde de la tarjeta (nunca pisa el texto) en
   * su cue (`ring`) y se apaga cuando entra la siguiente. Todo dentro de 288–`pile_bottom` (1000 por defecto: a ancho
   * completo, la tarjeta no baja de la columna de botones). Las capturas no rebotan (ease move). Sin `pile`, nada cambia (no se llama `stack` porque compile.py ya usa esa prop para
   * «piezas que se suman en el mismo panel»). */
  function mountStack(root, p, ctx) {
    const fps = ctx.fps;
    const media = ctx.media || [];
    const byId = (id) => media.find((x) => x && x.ckAsset === id) || null;
    const units = p.pile.map((s) => ({ s: s || {}, m: s ? byId(s.asset) : null, lm: s && s.badge ? byId(s.badge) : null }))
      .filter((u) => u.m);
    if (!units.length) return { animate() {} };
    const area0 = cardArea(ctx);
    const yBot = Math.min(area0.y + area0.h, Number(p.pile_bottom) > 0 ? Number(p.pile_bottom) : 1000);
    const A = { x: area0.x, y: area0.y, w: area0.w, h: yBot - area0.y };
    const K = U.clamp(Number(p.pile_prev) || 0.6, 0.4, 0.8);
    const LB = Math.round(U.clamp(Number(p.pile_logo) || 180, 96, 240));
    const GAP = 22, GL = 14, GP = 16, RG = 10, R = p.radius || 22;
    const cw = A.w, lp = Math.round(LB * K);
    units.forEach((u) => { u.ch = Math.round(cw / aspectOf(u.m)); });
    /** estado de la pila con las unidades 0..j a la vista (la j es la actual): caja de la tarjeta y del logo de cada una */
    function layout(j) {
      const prev = units.slice(0, j).map((u) => {
        const wk = Math.round(cw * K), chk = Math.round(u.ch * K);
        return { wk, chk, uh: Math.max(u.lm ? lp : 0, chk), uw: (u.lm ? lp + GP : 0) + wk };
      });
      const cur = units[j];
      const hPrev = prev.reduce((a, q) => a + q.uh + GAP, 0);
      const Lc = cur.lm ? Math.round(U.clamp(A.h - hPrev - GL - cur.ch, 96, LB)) : 0;
      const H = hPrev + (cur.lm ? Lc + GL : 0) + cur.ch;
      let y = Math.round(A.y + Math.max(0, (A.h - H) / 2));
      const st = [];
      prev.forEach((q, i) => {
        const ux = Math.round(A.x + (A.w - q.uw) / 2), u = units[i];
        st[i] = { card: { x: ux + (u.lm ? lp + GP : 0), y: y + Math.round((q.uh - q.chk) / 2), w: q.wk, h: q.chk },
                  logo: u.lm ? { x: ux, y: y + Math.round((q.uh - lp) / 2), w: lp, h: lp } : null };
        y += q.uh + GAP;
      });
      st[j] = { logo: cur.lm ? { x: A.x, y, w: Lc, h: Lc } : null, card: null };
      if (cur.lm) y += Lc + GL;
      st[j].card = { x: A.x, y, w: cw, h: cur.ch };
      return st;
    }
    const states = units.map((_, j) => layout(j));
    const NS = 'http://www.w3.org/2000/svg';
    units.forEach((u, i) => {
      const s0 = states[i][i];
      u.F = { x: A.x, y: A.y, w: cw, h: u.ch };
      u.wrap = placeWrap(u.m, u.F, ctx.z);
      cardStyle(u.wrap, R);
      u.wrap.style.background = '#fff';
      mediaFit(u.m, 'cover');
      // aro: SVG en una caja 10 px más grande que la tarjeta (el trazo va por fuera del borde)
      u.ringBox = U.el('div', 'ck-uf-ringbox', root);
      U.box(u.ringBox, { x: u.F.x - RG, y: u.F.y - RG, w: cw + 2 * RG, h: u.ch + 2 * RG });
      Object.assign(u.ringBox.style, { zIndex: String(ctx.z + 1), pointerEvents: 'none' });
      const svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('width', cw + 2 * RG); svg.setAttribute('height', u.ch + 2 * RG);
      svg.style.position = 'absolute'; svg.style.left = '0'; svg.style.top = '0'; svg.style.overflow = 'visible';
      u.rect = document.createElementNS(NS, 'rect');
      u.rect.setAttribute('x', 3); u.rect.setAttribute('y', 3); u.rect.setAttribute('width', cw + 2 * RG - 6);
      u.rect.setAttribute('height', u.ch + 2 * RG - 6); u.rect.setAttribute('rx', R + RG); u.rect.setAttribute('pathLength', '100');
      u.rect.setAttribute('fill', 'none'); u.rect.setAttribute('stroke', U.color(p.color || 'accent'));
      u.rect.setAttribute('stroke-width', '6'); u.rect.setAttribute('stroke-dasharray', '100 100');
      u.rect.setAttribute('stroke-dashoffset', '100'); u.rect.setAttribute('stroke-linecap', 'round');
      svg.appendChild(u.rect); u.ringBox.appendChild(svg);
      gsap.set(u.ringBox, { transformOrigin: `${RG}px ${RG}px`, x: s0.card.x - u.F.x, y: s0.card.y - u.F.y, scale: 1, opacity: 0 });
      gsap.set(u.wrap, { transformOrigin: '0 0', x: s0.card.x - u.F.x, y: s0.card.y - u.F.y, scale: 1, opacity: 0 });
      if (u.lm) {
        const pad = Math.round(LB * 0.16);
        u.FB = { x: A.x, y: A.y, w: LB, h: LB };
        u.badge = U.el('div', 'ck-uf-badge', root);
        U.box(u.badge, u.FB);
        Object.assign(u.badge.style, { background: '#FFFFFF', borderRadius: Math.round(LB * 0.25) + 'px', zIndex: String(ctx.z + 3),
          boxShadow: '0 0 0 1px rgba(22,21,20,.08), 0 10px 26px rgba(0,0,0,.16)' });
        u.lw = placeWrap(u.lm, { x: A.x + pad, y: A.y + pad, w: LB - 2 * pad, h: LB - 2 * pad }, ctx.z + 4);
        Object.assign(u.lm.style, { objectFit: 'contain', width: '100%', height: '100%' });
        u.lw.style.background = 'transparent'; u.lw.style.boxShadow = 'none';
        gsap.set(u.badge, { transformOrigin: '0 0', opacity: 0 });
        gsap.set(u.lw, { transformOrigin: `${-pad}px ${-pad}px`, opacity: 0 });
      }
    });
    const tf = (F, B) => ({ x: B.x - F.x, y: B.y - F.y, scale: B.w / F.w });
    const shrink = (B, k) => ({ x: B.x + B.w * (1 - k) / 2, y: B.y + B.h * (1 - k) / 2, w: B.w * k, h: B.h * k });
    return {
      animate(tl, t0, t1) {
        const cues = ctx.item.cues || {};
        const cueOf = (name) => (name && cues[name] != null ? Number(cues[name]) : null);
        const f = (n) => n / fps;
        // instante de cada empuje: 4 f antes de su cue (la tarjeta está entera en la palabra); ≥ 12 f entre empujes
        const T = [];
        units.forEach((u, j) => {
          if (j === 0) { T.push(U.snap(t0)); return; }
          const c = cueOf(u.s.in);
          const want = c != null ? c - f(4) : t0 + j * 0.8;
          T.push(U.snap(U.clamp(want, T[j - 1] + f(12), t1 - f(12))));
        });
        const D = f(10);
        units.forEach((u, i) => {
          const sI = states[i][i];
          // entrada: la primera como cualquier captura (sube 50 px y se enciende en 8 f); las demás suben desde abajo
          const cutIn = i === 0 && p.enter === 'cut';
          const tE = i === 0 ? T[0] : U.snap(T[i] + f(2));
          const to = Object.assign({ opacity: 1 }, tf(u.F, sI.card));
          if (cutIn) tl.set(u.wrap, to, tE);
          else tl.fromTo(u.wrap, Object.assign({}, to, { opacity: 0, y: to.y + (i === 0 ? 50 : 60) }),
            Object.assign({}, to, { duration: f(i === 0 ? 8 : 9), ease: E.enter, immediateRender: false }), tE);
          ctx.event('media.enter', tE);
          if (u.badge) {
            const tB = U.snap(tE + f(i === 0 ? 2 : 3));
            const a = tf(u.FB, shrink(sI.logo, 0.6)), b = tf(u.FB, sI.logo);
            tl.fromTo([u.badge, u.lw], Object.assign({ opacity: 0 }, a), Object.assign({ opacity: 1, duration: f(8), ease: E.pop, immediateRender: false }, b), tB);
          }
          // empujes siguientes: sube y se reduce (ease move, sin rebote)
          for (let j = i + 1; j < units.length; j++) {
            const A0 = states[j - 1][i], A1 = states[j][i];
            tl.fromTo([u.wrap, u.ringBox], tf(u.F, A0.card), Object.assign({ duration: D, ease: E.move, immediateRender: false }, tf(u.F, A1.card)), T[j]);
            if (u.badge) tl.fromTo([u.badge, u.lw], tf(u.FB, A0.logo), Object.assign({ duration: D, ease: E.move, immediateRender: false }, tf(u.FB, A1.logo)), T[j]);
          }
          // aro en su cue, por fuera del borde; se apaga cuando entra la siguiente
          const tNext = i + 1 < units.length ? T[i + 1] : null;
          const c = cueOf(u.s.ring);
          if (c != null && u.s.ring !== false) {
            const tR = U.snap(Math.max(tE + f(i === 0 ? 8 : 9), Math.min(c, (tNext != null ? tNext : t1) - f(6))));
            tl.set(u.ringBox, { opacity: 1 }, tR);
            tl.fromTo(u.rect, { attr: { 'stroke-dashoffset': 100 } }, { attr: { 'stroke-dashoffset': 0 }, duration: f(p.ring_frames || 6), ease: E.move, immediateRender: false }, tR);
            ctx.event('media.ring', tR);
            if (tNext != null) tl.fromTo(u.ringBox, { opacity: 1 }, { opacity: 0, duration: f(4), ease: E.exit, immediateRender: false }, tNext);
          }
        });
        // salida: corte seco por defecto (los envoltorios se apagan en t1); `exit: "fade"`, en los últimos 5 f
        const decor = [];
        units.forEach((u) => { decor.push(u.ringBox); if (u.badge) decor.push(u.badge); });
        if (p.exit === 'fade') {
          const d = Math.min(f(5), Math.max(f(1), (t1 - T[T.length - 1]) / 4));
          const vis = [];
          units.forEach((u, i) => { vis.push(u.wrap); if (u.badge) vis.push(u.badge, u.lw); if (i === units.length - 1) vis.push(u.ringBox); });
          tl.to(vis, { opacity: 0, duration: d, ease: E.exit, immediateRender: false }, U.snap(t1 - d));
        }
        tl.set(decor, { opacity: 0 }, U.snap(t1));
      },
    };
  }

  // ───────────────────────── media.ui_focus — zoom a una región, el resto se oscurece y un anillo se dibuja
  /* Encaje a lo ANCHO del área (nunca una captura alta metida en una tira estrecha): la imagen ocupa todo el ancho
   * y, si es más alta que el área, se recorta en vertical arrancando con la región ya visible. Después, zoom a la
   * región (sin pasar de lo que cabe), oscurecido del resto y anillo que se dibuja. */
  CK.register('media.ui_focus', {
    kind: 'media',
    mount(root, p, ctx) {
      if (Array.isArray(p.pile) && p.pile.length) return mountStack(root, p, ctx);     // pila (ver mountStack)
      // `badge`: id de un logo que va en `assets` DESPUÉS de
      // la captura; se pinta en una baldosa blanca en la esquina de arriba a la izquierda de la tarjeta («esto es la Agenda»).
      // Sin la prop, igual que antes (la captura es ctx.media[0])
      const m = p.badge ? ((ctx.media || []).find((x) => x && x.ckAsset !== p.badge) || ctx.media[0]) : ctx.media[0];
      if (!m) return { animate() {} };
      // («a sangre, como en las VSL»): `bleed` en broll_full = la
      // captura ocupa el LIENZO entero (1080 de ancho, centrada en vertical; alto = 1080 / aspecto, hasta 1920), sin marco
      // ni esquinas, y el subtítulo va encima. Sin `bleed`, todo igual que antes (tarjeta de 950 en 288–1240).
      const bleed = !!p.bleed && !!ctx.layout && ctx.layout.name === 'layout.broll_full';
      const area = bleed ? { x: 0, y: 0, w: ctx.W, h: ctx.H } : cardArea(ctx);
      const R = bleed ? 0 : (p.radius || 24);
      const a = aspectOf(m);
      const bw = Math.round(Math.min(area.w, p.width || area.w));
      const ih = Math.round(bw / a);                                   // alto de la imagen a ese ancho
      // `card_h` / `card_cy` (a pantalla completa las capturas anchas eran
      // tarjetas bajas en la banda de arriba): `card_h` (px) = alto de la tarjeta aunque la imagen a ese ancho sea más baja
      // (la cámara entra lo justo para cubrirla: zoom ≥ card_h / alto de la imagen); `card_cy` (y del lienzo) = centro de la
      // tarjeta, dentro del área. Sin las props, igual que antes
      const cardH = !bleed && Number(p.card_h) > 0 ? Math.round(U.clamp(Number(p.card_h), 120, area.h)) : 0;
      const bh = cardH || Math.min(area.h, ih);
      const cardY = !bleed && Number(p.card_cy) > 0 ? Math.round(U.clamp(Number(p.card_cy) - bh / 2, area.y, area.y + area.h - bh)) : null;
      const b = { x: Math.round(area.x + (area.w - bw) / 2), y: cardY != null ? cardY : Math.round(area.y + (area.h - bh) / 2), w: bw, h: bh };
      const wrap = placeWrap(m, b, ctx.z);
      cardStyle(wrap, R);
      if (bleed) Object.assign(wrap.style, { borderRadius: '0px', boxShadow: 'none' });
      wrap.style.background = '#fff';
      Object.assign(m.style, { height: ih + 'px', bottom: 'auto', objectFit: 'fill' });
      Object.assign(m.ckZoom.style, { height: ih + 'px', bottom: 'auto' });
      const over = overlayFor(root, b, ctx.z + 1, R);
      if (bleed) Object.assign(over.style, { borderRadius: '0px', boxShadow: 'none' });
      const r = Object.assign({ x: 0.3, y: 0.3, w: 0.4, h: 0.2 }, p.region || {});
      const rc = { x: (r.x + r.w / 2) * bw, y: (r.y + r.h / 2) * ih };
      // vista inicial: la región centrada (recorte vertical), sin zoom
      const oy = Math.round(U.clamp(rc.y - bh / 2, 0, ih - bh));
      // el `zoom` del plan manda. Antes zFit (la región cabe al 92 % del ancho
      // y al 80 % del alto) lo recortaba, y con una región ancha (w 0,97) dejaba el zoom en 1: no había zoom. zFit solo
      // limita el zoom por defecto (2,4). Nunca se ve fuera del medio: el encuadre se acota a la imagen (zx, zy).
      const zFit = Math.min((bw * 0.92) / (r.w * bw), (bh * 0.80) / (r.h * ih));
      const zMin = bh > ih ? bh / ih : 1;                              // `card_h` más alto que la imagen: siempre cubierta
      const Z = Math.max(zMin, U.clamp(p.zoom != null ? p.zoom : Math.min(2.4, zFit), 1, 3.5));
      const zx = Math.round(U.clamp(bw / 2 - Z * rc.x, bw - Z * bw, 0));
      const zy = Math.round(U.clamp(bh / 2 - Z * rc.y, bh - Z * ih, 0));
      // vista inicial (sin `start_framed`): la de siempre (escala 1, la región centrada en vertical); con `card_h` más alto
      // que la imagen, la mínima que la cubre, centrada en la región
      const v0 = zMin > 1 ? { x: Math.round(U.clamp(bw / 2 - zMin * rc.x, bw - zMin * bw, 0)), y: Math.round(U.clamp(bh / 2 - zMin * rc.y, bh - zMin * ih, 0)), scale: zMin }
        : { x: 0, y: -oy, scale: 1 };
      const pad = 10;
      const RRr = { x: zx + Z * r.x * bw - pad, y: zy + Z * r.y * ih - pad, w: Z * r.w * bw + 2 * pad, h: Z * r.h * ih + 2 * pad };
      // el marcador nunca se sale de la tarjeta
      const x0 = U.clamp(RRr.x, 6, bw - 6), y0 = U.clamp(RRr.y, 6, bh - 6);
      const RR = { x: Math.round(x0), y: Math.round(y0), w: Math.round(U.clamp(RRr.x + RRr.w, 6, bw - 6) - x0), h: Math.round(U.clamp(RRr.y + RRr.h, 6, bh - 6) - y0) };
      // `path`: después del foco, la cámara recorre la MISMA captura o
      // vídeo parada a parada, cada una en su cue: encuadre `frame` (por defecto, su `ring`) con su `zoom`, y el anillo y el
      // oscurecido pasan a `ring` (null = esa parada sin anillo). Mismas cuentas que el foco. Sin la prop, nada cambia
      const camFor = (rg, zoom) => {
        const c = { x: (rg.x + rg.w / 2) * bw, y: (rg.y + rg.h / 2) * ih };
        const zf = Math.min((bw * 0.92) / (rg.w * bw), (bh * 0.80) / (rg.h * ih));
        const Zs = Math.max(zMin, U.clamp(zoom != null ? zoom : Math.min(2.4, zf), 1, 3.5));
        return { x: Math.round(U.clamp(bw / 2 - Zs * c.x, bw - Zs * bw, 0)), y: Math.round(U.clamp(bh / 2 - Zs * c.y, bh - Zs * ih, 0)), scale: Zs };
      };
      const boxFor = (rg, g) => {
        const q = { x: g.x + g.scale * rg.x * bw - pad, y: g.y + g.scale * rg.y * ih - pad, w: g.scale * rg.w * bw + 2 * pad, h: g.scale * rg.h * ih + 2 * pad };
        const qx = U.clamp(q.x, 6, bw - 6), qy = U.clamp(q.y, 6, bh - 6);
        return { x: Math.round(qx), y: Math.round(qy), w: Math.round(U.clamp(q.x + q.w, 6, bw - 6) - qx), h: Math.round(U.clamp(q.y + q.h, 6, bh - 6) - qy) };
      };
      // capa de foco: `ring: false` = zoom limpio (sin anillo ni oscurecido); `color: null` = sin anillo; `dim: 0` = sin
      // oscurecido (con las dos, también zoom limpio)
      const ringOn = p.ring !== false && p.color !== null && p.color !== 'none';
      const dimV = p.ring === false ? 0 : (p.dim != null ? p.dim : 0.55);
      const dimOn = dimV > 0.001;
      let hole = null, rect = null;
      if (dimOn) {
        hole = U.el('div', 'ck-focus-hole', over);
        U.box(hole, RR);
        Object.assign(hole.style, { borderRadius: '16px', boxShadow: `0 0 0 4000px rgba(0,0,0,${dimV})`, opacity: '0' });
      }
      if (ringOn) {
        const NS = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(NS, 'svg');
        svg.setAttribute('width', bw); svg.setAttribute('height', bh);
        svg.style.position = 'absolute'; svg.style.left = '0'; svg.style.top = '0'; svg.style.overflow = 'visible';
        rect = document.createElementNS(NS, 'rect');
        rect.setAttribute('x', RR.x); rect.setAttribute('y', RR.y); rect.setAttribute('width', RR.w); rect.setAttribute('height', RR.h);
        rect.setAttribute('rx', 16); rect.setAttribute('pathLength', '100');
        rect.setAttribute('fill', 'none'); rect.setAttribute('stroke', U.color(p.color || 'accent'));
        rect.setAttribute('stroke-width', '6'); rect.setAttribute('stroke-dasharray', '100 100'); rect.setAttribute('stroke-dashoffset', '100');
        rect.setAttribute('stroke-linecap', 'round');
        svg.appendChild(rect); over.appendChild(svg);
      }
      let badge = null, badgeM = null;
      if (p.badge && !bleed) {
        badgeM = (ctx.media || []).find((x) => x && x !== m && x.ckAsset === p.badge) || null;
        if (badgeM) {
          // `badge_pos: "above"` (en una tira baja la baldosa tapaba el
          // principio del asunto): la baldosa va ENTERA encima de la tarjeta, alineada con su borde izquierdo. Sin la prop, igual
          const above = p.badge_pos === 'above';
          const bs = 112, bx = above ? b.x : b.x + 26, by = above ? b.y - bs - 18 : b.y - Math.round(bs * 0.45);
          badge = U.el('div', 'ck-uf-badge', root);
          U.box(badge, { x: bx, y: by, w: bs, h: bs });
          Object.assign(badge.style, { background: '#FFFFFF', borderRadius: '28px', zIndex: String(ctx.z + 3),
            boxShadow: '0 0 0 1px rgba(22,21,20,.08), 0 10px 26px rgba(0,0,0,.16)' });
          const lw = placeWrap(badgeM, { x: bx + 18, y: by + 18, w: bs - 36, h: bs - 36 }, ctx.z + 4);
          Object.assign(badgeM.style, { objectFit: 'contain', width: '100%', height: '100%' });
          badgeM.ckBadgeWrap = lw;
        }
      }
      // `start_framed`: el plano abre ya encuadrado en la región (sin zoom de entrada)
      const framed = !!p.start_framed;
      gsap.set(m.ckZoom, framed ? { x: zx, y: zy, scale: Z, transformOrigin: '0 0' } : { x: v0.x, y: v0.y, scale: v0.scale, transformOrigin: '0 0' });
      return {
        animate(tl, t0, t1) {
          const fps = ctx.fps;
          ctx.event('media.enter', t0);
          const els = [wrap, over];
          const entering = !splitDrop(tl, ctx, els) && p.enter !== 'cut';
          if (entering) {
            tl.fromTo(els, { y: 50, scale: 0.96, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: 8 / fps, ease: E.enter, immediateRender: false }, t0);
          }
          // el ANILLO cae en la palabra. Antes el zoom empezaba en
          // la cue y el anillo se dibujaba en tf + 0,85·zd durante 12 f: quedaba dibujado 15–22 f tarde. Ahora el zoom
          // arranca `zoom_lead` s antes de la cue (0,35 por defecto) y el anillo se dibuja en 6 f desde la cue (o desde el
          // 70 % del zoom, si el zoom no ha podido adelantarse): queda dibujado ≤ 6 f después de la palabra.
          const cue = ctx.item.cues && ctx.item.cues.focus;
          const tEnter = t0 + (entering ? 8 / fps : 0);
          const tCue = U.snap(Math.min(t1 - 6 / fps, Math.max(tEnter, cue != null ? cue : t0 + (p.delay != null ? p.delay : 0.45))));
          const lead = p.zoom_lead != null ? Math.max(0, p.zoom_lead) : 0.35;
          let zd = (p.zoom_frames || 14) / fps;
          const tz = U.snap(Math.max(tEnter, tCue - lead));
          // sin sitio para la antelación (cue pegada al inicio), el zoom se acorta (≥ 6 f) para no llegar tarde
          if (lead > 0 && tCue - tz < 0.7 * zd) zd = Math.max(6 / fps, Math.min(zd, (tCue - tz) / 0.7));
          const zoomOn = !framed && (Math.abs(Z - v0.scale) > 1e-3 || Math.abs(zx - v0.x) > 0.5 || Math.abs(zy - v0.y) > 0.5);
          if (zoomOn) {
            tl.fromTo(m.ckZoom, { x: v0.x, y: v0.y, scale: v0.scale }, { x: zx, y: zy, scale: Z, duration: zd, ease: E.move, immediateRender: false }, tz);
            ctx.event('media.focus', tz);
          }
          const tR = U.snap(Math.max(tCue, zoomOn ? tz + 0.7 * zd : tCue));
          if (hole) tl.fromTo(hole, { opacity: 0 }, { opacity: 1, duration: 8 / fps, ease: E.enter, immediateRender: false }, U.snap(Math.max(tz, tR - 3 / fps)));
          if (rect) {
            const rd = (p.ring_frames || 6) / fps;
            tl.fromTo(rect, { attr: { 'stroke-dashoffset': 100 } }, { attr: { 'stroke-dashoffset': 0 }, duration: rd, ease: E.move, immediateRender: false }, tR);
            ctx.event('media.ring', tR);
          }
          if (Array.isArray(p.path) && p.path.length) {        // (ver `camFor`)
            const cues = ctx.item.cues || {};
            let cam = framed || zoomOn ? { x: zx, y: zy, scale: Z } : { x: v0.x, y: v0.y, scale: v0.scale };
            let box = RR, ringOnNow = !!rect, holeOnNow = !!hole;
            let tPrev = U.snap(Math.max(tR, zoomOn ? tz + zd : tR) + 2 / fps);
            p.path.forEach((s) => {
              const c0 = cues[s.cue];
              if (c0 == null) return;
              const tc = U.snap(Math.min(t1 - 6 / fps, Math.max(tPrev, c0)));
              const g = camFor(Object.assign({}, s.frame || s.ring || r), s.zoom);
              const ts = U.snap(Math.max(tPrev, tc - lead));
              let d = (s.frames || p.zoom_frames || 14) / fps;
              if (tc - ts < 0.7 * d) d = Math.max(6 / fps, Math.min(d, (tc - ts) / 0.7));
              const moves = Math.abs(g.scale - cam.scale) > 1e-3 || Math.abs(g.x - cam.x) > 0.5 || Math.abs(g.y - cam.y) > 0.5;
              if (moves) {
                tl.fromTo(m.ckZoom, { x: cam.x, y: cam.y, scale: cam.scale }, { x: g.x, y: g.y, scale: g.scale, duration: d, ease: E.move, immediateRender: false }, ts);
                ctx.event('media.focus', ts);
              }
              const rg = s.ring === null ? null : (s.ring || s.frame || null);
              const nb = rg ? boxFor(rg, g) : null;
              const tr = U.snap(Math.max(tc, moves ? ts + 0.7 * d : tc));
              if (rect) {
                if (ringOnNow) tl.fromTo(rect, { opacity: 1 }, { opacity: 0, duration: 3 / fps, ease: E.exit, immediateRender: false }, ts);
                if (nb) {
                  tl.set(rect, { attr: { x: nb.x, y: nb.y, width: nb.w, height: nb.h, 'stroke-dashoffset': 100 }, opacity: 1 }, U.snap(Math.min(tr, ts + 3 / fps)));
                  tl.fromTo(rect, { attr: { 'stroke-dashoffset': 100 } }, { attr: { 'stroke-dashoffset': 0 }, duration: (p.ring_frames || 6) / fps, ease: E.move, immediateRender: false }, tr);
                  ctx.event('media.ring', tr);
                }
              }
              if (hole) {
                const to = nb || box;
                tl.fromTo(hole, { left: box.x + 'px', top: box.y + 'px', width: box.w + 'px', height: box.h + 'px', opacity: holeOnNow ? 1 : 0 },
                  { left: to.x + 'px', top: to.y + 'px', width: to.w + 'px', height: to.h + 'px', opacity: nb ? 1 : 0, duration: moves ? d : 6 / fps, ease: E.move, immediateRender: false }, moves ? ts : U.snap(Math.max(ts, tr - 3 / fps)));
                box = to;
                holeOnNow = !!nb;
              }
              ringOnNow = !!(rect && nb);
              cam = g;
              tPrev = U.snap(Math.max(moves ? ts + d : ts, tr) + 2 / fps);
            });
          }
          // `freeze_at_focus` lo resuelve compile.py (vídeo congelado en el fotograma de la cue `focus`)
          // la capa de foco (anillo, oscurecido, filo) se apaga en t1: nunca se solapa con el plano siguiente
          const bEls = badge ? [badge, badgeM && badgeM.ckBadgeWrap].filter(Boolean) : [];
          if (bEls.length) tl.fromTo(bEls, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 8 / fps, ease: E.pop, immediateRender: false }, U.snap(tEnter + 2 / fps));
          if (bEls.length) gsap.set(bEls, { opacity: 0 });
          mediaExit(tl, [wrap].concat(bEls), t0, t1, p, fps, [over].concat(badge ? [badge] : []));
        },
      };
    },
  });

  // ───────────────────────── media.device — marco de navegador o de teléfono
  CK.register('media.device', {
    kind: 'media',
    mount(root, p, ctx) {
      const m = ctx.media[0];
      if (!m) return { animate() {} };
      const area = cardArea(ctx);
      const kind = p.device || 'browser';
      let body, screen, R;
      if (kind === 'phone') {
        body = phoneBody(ctx, area, p);
        const bz = 16; R = 74;
        screen = { x: body.x + bz, y: body.y + bz, w: body.w - 2 * bz, h: body.h - 2 * bz };
      } else {
        const bar = 60;
        const w = Math.min(area.w, p.width || 960);
        let sh = Math.round(w / aspectOf(m));
        sh = Math.min(sh, area.h - bar);
        body = { x: Math.round(area.x + (area.w - w) / 2), y: Math.round(area.y + (area.h - sh - bar) / 2), w: Math.round(w), h: sh + bar };
        screen = { x: body.x, y: body.y + bar, w: body.w, h: sh };
        R = 22;
      }
      const chrome = U.el('div', 'ck-device ck-device-' + kind, root);
      U.box(chrome, body);
      Object.assign(chrome.style, { zIndex: String(ctx.z - 1), borderRadius: (kind === 'phone' ? R : R) + 'px', boxShadow: 'var(--ck-shadow-3), inset 0 0 0 1.5px rgba(255,255,255,.10)',
        background: kind === 'phone' ? 'linear-gradient(150deg, #34333a 0%, #121115 38%, #222127 100%)' : '#17161b' });
      if (kind === 'browser') {
        const barEl = U.el('div', 'ck-device-bar', chrome, { position: 'absolute', left: '0', top: '0', right: '0', height: '60px', display: 'flex', alignItems: 'center', padding: '0 22px', gap: '12px' });
        ['#5b5960', '#5b5960', '#5b5960'].forEach((c) => U.el('i', '', barEl, { display: 'block', width: '14px', height: '14px', borderRadius: '50%', background: c }));
        if (p.url) {
          const pill = U.el('div', 'ck-device-url ck-ui', barEl, { marginLeft: '18px', flex: '1', height: '36px', borderRadius: '18px', background: 'rgba(255,255,255,.07)',
            color: 'var(--ck-muted)', fontSize: '22px', fontWeight: '500', display: 'flex', alignItems: 'center', padding: '0 18px', whiteSpace: 'nowrap', overflow: 'hidden' }, p.url);
          pill.setAttribute('data-ck-text', '');
        }
      }
      const wrap = placeWrap(m, screen, ctx.z);
      wrap.style.borderRadius = kind === 'phone' ? (R - 14) + 'px' : `0 0 ${R}px ${R}px`;
      wrap.style.background = '#fff';
      mediaFit(m, 'cover', p.position || 'top center');
      let island = null;
      if (kind === 'phone') {
        island = U.el('div', 'ck-device-island', root);
        U.box(island, { x: Math.round(body.x + body.w / 2 - 70), y: body.y + 30, w: 140, h: 40 });
        Object.assign(island.style, { borderRadius: '20px', background: '#000', zIndex: String(ctx.z + 1) });
      }
      if (body.cut) {
        const J = ctx.layout.seamY || 1008, F = ctx.layout.feather || 110;
        seamMask(chrome, body.y, J, F); seamMask(wrap, screen.y, J, F);
      }
      const els = [chrome, wrap].concat(island ? [island] : []);
      const cx = body.x + body.w / 2, cy = body.y + body.h;
      els.forEach((e) => { const bx = parseFloat(e.style.left), by = parseFloat(e.style.top); e.style.transformOrigin = `${cx - bx}px ${cy - by}px`; });
      return {
        animate(tl, t0, t1) {
          ctx.event('media.enter', t0);
          const d = 12 / ctx.fps;
          const dropEnd = splitDrop(tl, ctx, els);
          if (!dropEnd && p.enter !== 'cut') {
            tl.fromTo(els, { y: 140, scale: 0.94, opacity: 0 }, { y: 0, scale: 1, opacity: 1, duration: d, ease: E.enter, immediateRender: false }, t0);
          }
          const tI = Math.max(t0 + (p.enter === 'cut' ? 0 : d), dropEnd);
          if (t1 - tI > 0.5) tl.fromTo(els, { y: 0 }, { y: -16, duration: t1 - tI, ease: E.move, immediateRender: false }, tI);
          kenBurns(tl, m.ckZoom, screen, t0, t1, p.kb || 0, 'in');
          mediaExit(tl, els, t0, t1, p, ctx.fps);
        },
      };
    },
  });
})();
