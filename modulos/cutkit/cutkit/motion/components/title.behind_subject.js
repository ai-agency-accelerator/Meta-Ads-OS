// title.behind_subject — título ENORME detrás del sujeto, con el presentador recortado por delante (styleframe 02).
// Capas (de atrás adelante): lienzo `panel_bg` con luz radial y halo detrás de la cabeza → título (Montserrat 900)
// → el presentador recortado (mate por fotograma de cutkit/tools/matte.py, inyectado por html.py en props._matte) con sombra
// suave → subtítulos (fuera de #ck-content, encima de todo).
// Encuadre del sujeto (props.subject):
//   "aroll"   = exactamente el rect vivo del A-roll (layout, cámara, punch-in): continuidad perfecta al entrar/salir;
//   "lowered" = mismo sujeto, escalado a `subject_scale` del ancho del lienzo y BAJADO para que el pelo tape la base del
//               título (styleframe: −372 px); sigue igual los movimientos relativos de cámara/punch-in;
//   "auto"    = "aroll" si el título cabe encima de la cabeza; si no, "lowered" (en full_face el pelo queda en y≈60).
// Movimiento: el título sube desde detrás de los hombros (2 f de anticipación + 9 f expo.out con desenfoque vertical
// proporcional a la velocidad) en la cue `name` − 0,155 s; paralaje 2.5D (título ×1,00→1,02, presentador ×1,00→1,045,
// sine.inOut). Salida: corte seco en t1 (vuelve la cara con su cuarto real).
// Determinismo: el canvas del sujeto se pinta en `hf-seek` (HF lo despacha tras mover la timeline GSAP) y en
// window.__ckSeek (vista previa); estado = proxy GSAP + rect vivo del #aroll + nº de fotograma. Sin rAF ni relojes.
// props: {text, by?, panel_bg?, color?, subject?, subject_scale?, subject_dy?, title_y?, width?, overlap?, halo?,
//         parallax?, shadow?, exit?: "cut", hide_captions?, _matte (lo pone html.py)}
// cues:  name (entra el título; si no, t0 + 0,25 s)
(function (CK) {
  if (!CK) return;
  const NAME = 'title.behind_subject';
  const DRAWERS = [];
  let bound = false;
  function drawAll(t) {
    const T = Number(t) || 0;
    for (const d of DRAWERS) { try { d(T); } catch (e) { console.error('[' + NAME + '] draw', e); } }
  }
  function bindSeek() {
    if (!bound) {
      bound = true;
      window.addEventListener('hf-seek', (e) => drawAll(e && e.detail ? e.detail.time : 0));
    }
    const orig = window.__ckSeek;
    if (typeof orig === 'function' && !orig.__ckSubject) {
      const w = function (t) { const r = orig.apply(this, arguments); drawAll(t); return r; };
      w.__ckSubject = true;
      window.__ckSeek = w;
    }
  }
  // lienzos con nombre del kit (negro y blanco profesionales, oro de la marca); por defecto, negro
  const NAMED = { ink: '#0B0B0C', black: '#0B0B0C', white: '#F7F7F5', accent: '#FECA1A', gold: '#FECA1A' };
  function hexRgb(h) {
    h = NAMED[String(h || '').trim().toLowerCase()] || h;
    const m = /^#?([0-9a-f]{6})$/i.exec(String(h || '').trim());
    if (!m) return [11, 11, 12];
    const n = parseInt(m[1], 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  const mix = (a, b, k) => a.map((v, i) => Math.round(v + (b[i] - v) * k));
  const rgb = (c, a) => (a == null ? `rgb(${c[0]},${c[1]},${c[2]})` : `rgba(${c[0]},${c[1]},${c[2]},${a})`);
  const R = Math.round;

  CK.register(NAME, {
    kind: 'graphic',
    mount(root, props, ctx) {
      const W = ctx.W || 1080, H = ctx.H || 1920, fps = ctx.fps || 30;
      const it = ctx.item || {};
      const z = ctx.z != null ? ctx.z : 420;
      const text = String(props.text || '').trim();
      const by = String(props.by || '').trim();
      const base = hexRgb(props.panel_bg || 'ink');
      const lum = (0.2126 * base[0] + 0.7152 * base[1] + 0.0722 * base[2]) / 255, deep = lum < 0.2;
      // tinte neutro: nada de magentas al oscurecer (negro y blanco profesionales)
      const light = mix(base, [255, 255, 255], deep ? 0.13 : 0.16), dark = mix(base, [0, 0, 0], deep ? 0.5 : 0.18);
      const shadowCol = mix(base, [0, 0, 0], 0.6);
      const color = props.color || '#FFFFFF';
      const el = (tag, css, parent) => { const n = document.createElement(tag); if (css) Object.assign(n.style, css); (parent || root).appendChild(n); return n; };

      // ── lienzo con luz radial
      const panel = el('div', { position: 'absolute', left: '0', top: '0', width: W + 'px', height: H + 'px', zIndex: String(z),
        background: `radial-gradient(ellipse 125% 72% at 50% 34%, ${rgb(light)} 0%, ${rgb(base)} 52%, ${rgb(dark)} 100%)` });
      const halo = el('div', { position: 'absolute', left: '0', top: '0', width: W + 'px', height: H + 'px' }, panel);

      // ── métricas del título (fuente ya cargada: CK.run va tras document.fonts)
      const fam = '"Montserrat", sans-serif';
      const track = -0.05;
      const mc = document.createElement('canvas').getContext('2d');
      mc.font = `900 100px ${fam}`;
      try { mc.letterSpacing = (track * 100) + 'px'; } catch (e) { /* sin letterSpacing en canvas: se corrige abajo */ }
      const m100 = mc.measureText(text || ' ');
      const ink100 = (m100.actualBoundingBoxLeft + m100.actualBoundingBoxRight) || m100.width;
      // Zona segura de TEXTO (QA, caja DOM incluida y con la escala de paralaje ×1,02): x 65–1015, arriba ≥ 288,
      // ≤ 950 px de ancho, y por encima de y=1000 también durante la entrada. La caja se ajusta a la tinta con
      // line-height ≈ altura de mayúscula (con line-height 1 sobresalía ~40 px por arriba de las letras).
      const LH = 0.72, PAR = 1.02, SAFE_TOP = 288, SAFE_X0 = 65, SAFE_X1 = 1015;
      const probeBox = document.createElement('div');
      Object.assign(probeBox.style, { position: 'absolute', left: '0', top: '0', whiteSpace: 'nowrap', font: `900 100px ${fam}`,
        lineHeight: String(LH), letterSpacing: track + 'em', visibility: 'hidden' });
      probeBox.textContent = text || ' ';
      const pb = document.createElement('i');
      Object.assign(pb.style, { display: 'inline-block', width: '0', height: '0', verticalAlign: 'baseline' });
      probeBox.appendChild(pb);
      root.appendChild(probeBox);
      const box100 = probeBox.offsetWidth, base100 = pb.offsetTop;
      root.removeChild(probeBox);
      const maxBox = Math.min(props.width || 940, SAFE_X1 - SAFE_X0 - 10);                 // ancho de caja ya escalado
      // ancho por la TINTA (contorno real): canvas con el mismo tracking; si el canvas no aplica letterSpacing, se
      // corrige con la diferencia de avance medida en el DOM
      const lsOK = Math.abs(mc.measureText(text || ' ').width - box100) < Math.max(4, Math.abs(track * 100) * 0.6);
      const inkL100 = m100.actualBoundingBoxLeft, inkR100 = m100.actualBoundingBoxRight - (lsOK ? 0 : track * 100 * Math.max(0, Array.from(text).length - 1) * -1);
      const inkW100 = Math.max(1, inkL100 + inkR100);
      const fs = Math.floor(Math.min(720, maxBox / (PAR * inkW100) * 100));
      const k = fs / 100;
      const capH = R(m100.actualBoundingBoxAscent * k);
      const inkW = Math.ceil(inkW100 * k), inkL = inkL100 * k;
      const boxW = inkW, boxH = R(LH * fs), baseOff = R(base100 * k);   // la caja DOM = la tinta (QA y centrado)
      const topMin = SAFE_TOP + 4 + Math.ceil((PAR - 1) * baseOff) + (by ? 44 + 18 : 0);  // con paralaje y autoría
      const boxTop = Math.max(topMin, props.title_y != null ? props.title_y : 300);
      const baseline = boxTop + baseOff;
      const titleTop = baseline - capH;                                                    // parte superior de las letras

      // ── geometría del sujeto
      const M = props._matte && props._matte.frames && props._matte.frames.length ? props._matte : null;
      const lay = ctx.layoutAt ? ctx.layoutAt((it.t0 || 0) + 1e-3) : null;
      const cam = (lay && lay.cam) || { x: 0, y: 0, scale: 1 };
      const ref = { x: cam.x || 0, y: cam.y || 0, w: W * (cam.scale || 1), h: H * (cam.scale || 1) };   // rect del A-roll sin punch-in
      let mode = 'none', B = null, anchor = null, faceTopPx = null, hairY = null;
      if (M) {
        const srcW = M.size[0], srcH = M.size[1];
        const tops = M.frames.map((f) => f.top).filter((v) => v != null).sort((a, b) => a - b);
        const topMed = tops.length ? tops[Math.floor(tops.length / 2)] : srcH * 0.14;
        const cxs = M.frames.map((f) => f.cx).filter((v) => v != null).sort((a, b) => a - b);
        const cxMed = cxs.length ? cxs[Math.floor(cxs.length / 2)] : srcW / 2;
        const overlap = props.overlap != null ? props.overlap : 0.18;
        const hairTarget = baseline - overlap * capH;
        const hairAroll = ref.y + topMed * ref.h / srcH;
        mode = props.subject || 'auto';
        if (mode === 'auto') mode = hairAroll >= hairTarget - 4 ? 'aroll' : 'lowered';
        if (mode === 'aroll') B = Object.assign({}, ref);
        else {
          const w = W * (props.subject_scale || 1), h = w * srcH / srcW;
          const sxp = w / srcW;
          const cxRef = ref.x + cxMed * ref.w / srcW;                // centro del sujeto en el encuadre del A-roll
          B = { x: cxRef - cxMed * sxp, y: hairTarget - topMed * sxp + (props.subject_dy || 0), w, h };
        }
        const fm = ctx.faceMedian ? ctx.faceMedian(it.t0 || 0, it.t1 || (it.t0 || 0) + 1) : null;
        const face = fm && fm.w ? fm : { x: 0.25, y: 0.3, w: 0.5, h: 0.32 };
        anchor = { x: B.x + (face.x + face.w / 2) * B.w, y: B.y + (face.y + face.h * 0.55) * B.h };   // paralaje alrededor de la cara
        faceTopPx = B.y + face.y * B.h;
        hairY = B.y + topMed * B.h / srcH;
      }
      // halo detrás de la cabeza (separa al sujeto del fondo)
      if (props.halo !== false) {
        const hx = anchor ? R(anchor.x) : W / 2;
        const hy = anchor ? R((hairY + faceTopPx) / 2 + 50) : R(baseline + 140);
        halo.style.background = `radial-gradient(circle 480px at ${hx}px ${hy}px, rgba(255,255,255,${deep ? 0.16 : 0.55}) 0%, rgba(255,255,255,${deep ? 0.06 : 0.24}) 42%, rgba(255,255,255,0) 74%)`;
      }

      // ── título (DOM: nítido y visible para la QA de textos)
      const svgNS = 'http://www.w3.org/2000/svg';
      const fid = 'ckbsblur_' + String(it.id || 'x').replace(/[^\w-]/g, '_');
      const svg = document.createElementNS(svgNS, 'svg');
      svg.setAttribute('width', '0'); svg.setAttribute('height', '0');
      Object.assign(svg.style, { position: 'absolute', width: '0', height: '0' });
      svg.innerHTML = `<defs><filter id="${fid}" x="-10%" y="-40%" width="120%" height="180%" color-interpolation-filters="sRGB">` +
        `<feGaussianBlur stdDeviation="0 0"/></filter></defs>`;
      root.appendChild(svg);
      const blurEl = svg.querySelector('feGaussianBlur');
      // NUNCA `visibility` en hijos del root: un hijo con visibility:visible anula el hidden con el que HF oculta el clip
      const tClip = el('div', { position: 'absolute', left: '0', top: '0', width: W + 'px', height: H + 'px', zIndex: String(z + 1),
        clipPath: `inset(0px 0px ${Math.max(0, H - R(baseline + 6))}px 0px)` });         // máscara: nada por debajo de la base
      const tWrap = el('div', { position: 'absolute', left: '0', top: '0', width: W + 'px', height: H + 'px' }, tClip);
      const tScale = el('div', { position: 'absolute', left: '0', top: '0', width: W + 'px', height: H + 'px',
        transformOrigin: `${W / 2}px ${baseline}px` }, tWrap);
      const title = el('div', { position: 'absolute', whiteSpace: 'nowrap', font: `900 ${fs}px ${fam}`, lineHeight: String(LH),
        letterSpacing: track + 'em', color, filter: `url(#${fid})`,
        textShadow: `0 ${R(fs * 0.03)}px ${R(fs * 0.07)}px ${rgb(shadowCol, 0.08)}` }, tScale);
      title.textContent = text;
      title.setAttribute('data-ck-text', 'title');
      title.style.lineHeight = String(LH);
      // centrado ÓPTICO por el contorno de los glifos: la caja mide lo que la tinta y el texto arranca en su apoyo
      title.style.left = R(W / 2 - inkW / 2) + 'px';
      title.style.width = inkW + 'px';
      title.style.overflow = 'visible';
      title.style.textIndent = R(inkL) + 'px';
      title.style.top = R(boxTop) + 'px';
      let byEl = null;
      if (by) {
        byEl = el('div', { position: 'absolute', left: '0', width: W + 'px', textAlign: 'center', whiteSpace: 'nowrap',
          font: `700 44px ${fam}`, lineHeight: '1', letterSpacing: '0.02em', color: 'rgba(255,255,255,0.94)',
          top: R(boxTop - 44 - 18) + 'px', textShadow: `0 4px 16px ${rgb(shadowCol, 0.08)}` }, tWrap);
        byEl.textContent = by;
        byEl.setAttribute('data-ck-text', 'by');
      }

      // ── canvas del sujeto
      let canvas = null, c2 = null;
      const imgs = [];
      const S = { k: 1 };
      if (M) {
        canvas = el('canvas', { position: 'absolute', left: '0', top: '0', width: W + 'px', height: H + 'px', zIndex: String(z + 2),
          pointerEvents: 'none', // sombra de contacto (oscurece el título justo encima del pelo) + sombra proyectada suave del styleframe (0 28 46)
          filter: props.shadow === false ? 'none' : `drop-shadow(0px 20px 40px ${rgb(shadowCol, 0.08)})` });   // una sola, ≤ 0,08
        canvas.width = W; canvas.height = H;
        c2 = canvas.getContext('2d');
        for (let i = 0; i < M.frames.length; i++) imgs.push(document.getElementById('pl_' + it.id + '_' + i));
        const pf0 = M.frames[0].pf, srcW = M.size[0], srcH = M.size[1], crop = M.crop;
        const rootEl = document.getElementById('root');
        const arollRect = () => {
          const a = document.getElementById('aroll');
          if (!a || !rootEl) return null;
          const rr = rootEl.getBoundingClientRect(), r = a.getBoundingClientRect();
          if (r.width < 2 || rr.width < 2) return null;
          const sc = W / rr.width;
          return { x: (r.left - rr.left) * sc, y: (r.top - rr.top) * sc, w: r.width * sc, h: r.height * sc };
        };
        const t0 = it.t0 || 0, t1 = it.t1 || t0 + 1, half = 0.5 / fps;
        const draw = (t) => {
          if (t < t0 - half || t >= t1 + half) return;
          const i = Math.max(0, Math.min(M.frames.length - 1, Math.round(t * fps) - pf0));
          const img = imgs[i];
          c2.clearRect(0, 0, W, H);
          if (!img || !img.complete || !img.naturalWidth) return;
          const live = arollRect() || ref;
          const s = live.w / ref.w, ox = live.x - ref.x * s, oy = live.y - ref.y * s;   // ref → vivo (cámara relativa)
          const L = { x: ox + B.x * s, y: oy + B.y * s, w: B.w * s, h: B.h * s };
          const ax = ox + anchor.x * s, ay = oy + anchor.y * s, kk = S.k;
          const px = (x) => ax + (x - ax) * kk, py = (y) => ay + (y - ay) * kk;
          const dx = px(L.x + crop[0] * L.w / srcW), dy = py(L.y + crop[1] * L.h / srcH);
          const dw = crop[2] * L.w / srcW * kk, dh = crop[3] * L.h / srcH * kk;
          c2.imageSmoothingEnabled = true;
          c2.imageSmoothingQuality = 'high';
          c2.drawImage(img, dx, dy, dw, dh);
        };
        DRAWERS.push(draw);
        bindSeek();
      }
      root.setAttribute('data-ck-subject', mode);
      if (props._matte_error) root.setAttribute('data-ck-matte-error', String(props._matte_error).slice(0, 200));

      return {
        animate(tl, t0, t1, cues) {
          const E = (CK.ease || {});
          const cue = cues && typeof cues.name === 'number' ? cues.name : t0 + 0.25;
          const tRise = Math.max(t0 + 2 / fps, cue - 0.155);
          const tAnt = tRise - 2 / fps;
          // entrada con MÁSCARA: horizonte fijo en la línea base (las letras suben desde detrás del pelo); recorrido
          // acotado para que la caja nunca baje de y=1000 ni toque el borde (QA de zona segura también en la entrada)
          const ant = 12;
          const land = tRise + 9 / fps;
          const rise = Math.max(60, Math.min(capH * 0.62, 1000 - 8 - (boxTop + boxH) - ant));
          gsap.set(tWrap, { y: rise, opacity: 0 });
          tl.fromTo(tWrap, { opacity: 0 }, { opacity: 1, duration: 3 / fps, ease: 'none', immediateRender: false }, tAnt);
          tl.fromTo(tWrap, { y: rise }, { y: rise + ant, duration: 2 / fps, ease: 'power1.in', immediateRender: false }, tAnt);
          tl.fromTo(tWrap, { y: rise + ant }, { y: 0, duration: 9 / fps, ease: 'expo.out', immediateRender: false }, tRise);
          tl.fromTo(blurEl, { attr: { stdDeviation: '0 0' } }, { attr: { stdDeviation: '0 2' }, duration: 2 / fps, ease: 'none', immediateRender: false }, tAnt);
          tl.fromTo(blurEl, { attr: { stdDeviation: '0 30' } }, { attr: { stdDeviation: '0 0' }, duration: 9 / fps, ease: 'expo.out', immediateRender: false }, tRise);
          if (byEl) {
            gsap.set(byEl, { opacity: 0, y: 18 });
            tl.fromTo(byEl, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 7 / fps, ease: E.enter || 'power3.out', immediateRender: false }, land - 3 / fps);
          }
          if (props.parallax !== false && t1 - land > 0.1) {
            tl.fromTo(tScale, { scale: 1 }, { scale: 1.02, duration: t1 - land, ease: 'sine.inOut', immediateRender: false }, land);
            if (canvas) tl.fromTo(S, { k: 1 }, { k: 1.045, duration: t1 - tRise, ease: 'sine.inOut', immediateRender: false }, tRise);
          }
          if (ctx.event) { ctx.event('enter', t0); ctx.event('title.land', tRise + 3 / fps); }
        },
      };
    },
  });
})(window.CK);
