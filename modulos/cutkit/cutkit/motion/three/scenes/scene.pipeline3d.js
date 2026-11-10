// scene.pipeline3d — versión 3D VERTICAL de flow.pipeline (styleframe 07), MISMAS props y cues.
// Composición (1080×1920, eje x=540, banda 288–1240), todo espejo respecto al bloque del logo (centro y=768):
//   «información desordenada» (Montserrat 800, 44 px) · 3 fichas de PAPEL apiladas (~820–900 px) · 36 px · baldosa con
//   el logo extruido + «Nimbo» · 36 px · 3 barras de TINTA de 680 × 88 con mono blanco 36 px · «salida útil».
// Profundidad que se LEE:
//   - las fichas caen con desorden real en 3D (±8–12° en los tres ejes, tres profundidades) y sombras blandas que
//     cambian con la altura; durante el desorden la cámara ORBITA alrededor del eje vertical x=0 (±6°) con un dolly:
//     la columna central no se mueve en pantalla y todo lo que está a otra profundidad se desplaza → paralaje real;
//   - en `transform` cada ficha se endereza (una a una) y una COPIA se desprende, cruza por detrás de las fichas de
//     abajo y de la baldosa (oclusión real, motion blur real), y sale por debajo como barra de tinta que se posa en SU
//     hueco pasando por detrás de las ya colocadas: la ficha i queda arriba y su salida i abajo, en el mismo orden;
//   - el DOF enfoca la ficha que está cruzando; barrido especular y pulso en la baldosa en cada paso;
//   - en reposo: push lento (1,00 → 1,02). Sin remate ni nodos inventados.
// props: {cards:[{eyebrow,text}]|["…"], outputs:["clave: valor"]|[{key,value}], labels?:{top,bottom},
//         steps?:[{label, kind:"model", asset}], canvas?, render?}
// cues:  messy, label_top, label_top2, transform, label_bottom, output
(function () {
  if (!window.CK3D) return;
  const NAME = 'scene.pipeline3d';
  const FPS = 30, f = (n) => n / FPS;
  const INK = '#0F0D10';

  function ctx2d(w, h) { const c = document.createElement('canvas'); c.width = Math.max(2, Math.round(w)); c.height = Math.max(2, Math.round(h)); return c; }
  const MC = ctx2d(4, 4).getContext('2d');
  function font(g, weight, px, fam, ls) { g.font = `${weight} ${px}px ${fam}`; try { g.letterSpacing = (ls || 0) + 'px'; } catch (e) { /* */ } }
  function wrap(g, text, maxW) {
    const words = String(text).split(/\s+/).filter(Boolean);
    const lay = (w) => { const out = []; let cur = ''; for (const wd of words) { const tr = cur ? cur + ' ' + wd : wd; if (!cur || g.measureText(tr).width <= w) cur = tr; else { out.push(cur); cur = wd; } } if (cur) out.push(cur); return out; };
    const base = lay(maxW);
    let lo = maxW * 0.45, hi = maxW, best = base;
    for (let i = 0; i < 14; i++) {
      const mid = (lo + hi) / 2, l = lay(mid);
      if (l.length <= base.length && Math.max(...l.map((s) => g.measureText(s).width)) <= mid + 0.5) { best = l; hi = mid; } else lo = mid;
    }
    return best;
  }
  function texture(THREE, canvas) {
    const t = new THREE.CanvasTexture(canvas);
    t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.generateMipmaps = true;
    t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter; t.needsUpdate = true;
    return t;
  }
  function parseOut(o) {
    if (o && typeof o === 'object') return { key: o.key || '', value: o.value || '' };
    const m = String(o).match(/^\s*([^:]{1,24}):\s*(.+)$/);
    return m ? { key: m[1], value: m[2] } : { key: '', value: String(o) };
  }
  function logoSvg(ctx) {
    const A = window.__CK3D_ASSETS || { svg: {} };
    for (const m of (ctx.item && ctx.item.media) || []) {
      const src = String(m.src || '').replace(/^\.?\//, '');
      if (A.svg[src]) return A.svg[src];
    }
    return null;
  }

  window.CK3D.scene(NAME, {
    fallback: 'flow.pipeline',
    options: {
      fov: 30, msaa: 4, shadows: true, shadowType: 'vsm',
      motionBlur: { samples: 8, shutter: 0.5 },
      dof: { enabled: true, focus: 35.8, aperture: 0, maxBlur: 10 },
      bloom: { strength: 0 },
      grade: { exposure: 1, vignette: 0.12, grain: 0.016, ca: 0.0005, contrast: 1, saturation: 1, lift: 0, tonemap: 'none' },
      background: '#F4F2EE',
    },

    setup(scene, camera, renderer, ctx, props, k) {
      const { THREE, kit, tl, dur } = k;
      const E = (window.CK && window.CK.ease) || {};
      const EASE = { enter: E.enter || 'power3.out', exit: E.exit || 'power2.in', move: E.move || 'power2.inOut', pop: E.pop || 'back.out(1.3)' };
      const W = k.W, H = k.H;
      const FOV = 30, D = H / (2 * 100 * Math.tan(THREE.MathUtils.degToRad(FOV / 2)));   // 1 px = 0,01 u en z=0
      k.framing(D, [0, 0, 0], FOV);
      camera.fov = FOV; camera.near = 1; camera.far = 120; camera.updateProjectionMatrix();
      const U = 0.01;
      const wx = (x) => (x - W / 2) * U, wy = (y) => (H / 2 - y) * U;
      const MONT = '"Montserrat", sans-serif', MONO = '"JetBrains Mono", monospace';

      // ── contenido
      const steps = props.steps || [];
      const model = steps.find((s) => s.kind === 'model') || {};
      const cardsT = (props.cards || []).map((c) => (typeof c === 'string' ? { text: c } : c || {})).filter((c) => c.text).slice(0, 3);
      const outsT = (props.outputs || []).filter(Boolean).map(parseOut).slice(0, 3);
      const labels = props.labels || {};
      // lienzo neutro (negro/blanco profesional): hex tal cual; ink → #0B0B0C; white → #F7F7F5; paper/defecto → #F4F2EE
      const CANV = { ink: '#0B0B0C', black: '#0B0B0C', white: '#F7F7F5', paper: '#F4F2EE' };
      const bgHex = /^#[0-9a-f]{6}$/i.test(props.canvas || '') ? props.canvas : (CANV[props.canvas] || '#F4F2EE');
      const bg = new THREE.Color(bgHex);
      const lum = (() => { const h = bgHex.slice(1); const c = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) / 255); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; })();
      const DARK = lum < 0.35, FG = DARK ? '#FFFFFF' : INK;
      // salidas en Montserrat salvo que sean código (clave con _ o símbolos de programación), o `mono: true`
      const isCode = props.mono === true || outsT.some((o) => /[_{}()=<>"\[\]]/.test(o.key + o.value));
      const OUTF = isCode ? MONO : MONT;
      // icono PNG de la baldosa (asset del paso «model» sin SVG): el <img> del item, que se pinta en la baldosa
      const iconImg = (() => {
        const list = (ctx.media || []);
        const hit = list.find((m) => m && m.tagName === 'IMG' && (!model.asset || (m.dataset && m.dataset.asset === model.asset)));
        if (hit) { const w = hit.ckWrap || hit.closest && hit.closest('.ck-mwrap'); if (w) w.style.opacity = '0'; else hit.style.opacity = '0'; }
        return hit && hit.naturalWidth ? hit : null;
      })();

      // ── maquetación vertical (styleframe 07): logo en y=768 y huecos espejo de 36 px
      const GAP = 36, LAB = 48, TILE = 160, JEVPX = 44;
      const mLabel0 = model.label && (model.asset || iconImg) ? String(model.label) : '';
      const blockH = TILE + (mLabel0 ? JEVPX + 14 : 0);
      const OUT_W = 680, OUT_H = 92, OUT_GAP = 10;
      const outsH = outsT.length * OUT_H + Math.max(0, outsT.length - 1) * OUT_GAP;
      // fichas: Montserrat 700 a 44 px (baja a 36 solo si alguna pasaría de 2 líneas), ojo 30 px; ancho 820–900
      let CPX = 44; const EPX = 30, PADT = 16, PADB = 20;
      let cardW = 820, lines = [];
      const layFor = (w) => { font(MC, 700, CPX, MONT, -0.01 * CPX); return cardsT.map((c) => wrap(MC, c.text, w - 64)); };
      for (; CPX >= 36; CPX -= 4) {
        lines = []; cardW = 820;
        for (const w of [820, 860, 900]) {
          const l = layFor(w);
          if (!lines.length || l.reduce((a, x) => a + x.length, 0) < lines.reduce((a, x) => a + x.length, 0)) { cardW = w; lines = l; }
        }
        if (lines.every((l) => l.length <= 2)) break;
      }
      CPX = Math.max(36, CPX);
      const LH = Math.round(CPX * 1.1);
      const cardH = cardsT.map((c, i) => PADT + (c.eyebrow ? EPX + 4 : 0) + lines[i].length * LH + PADB);
      const sumH = cardH.reduce((a, b) => a + b, 0);
      const paired = cardsT.length === outsT.length;                         // 1:1 → la pila espeja a las salidas
      const pileH = paired ? Math.max(outsH, sumH) : sumH + Math.max(0, cardsT.length - 1) * 18;
      const labTH = labels.top ? LAB + 18 : 0, labBH = labels.bottom ? LAB + 18 : 0;
      const total = labTH + pileH + GAP + blockH + GAP + outsH + labBH;
      const top0 = 288 + Math.max(0, (952 - total) / 2);                     // el bloque, centrado en la banda 288–1240
      const pileTop = top0 + labTH, pileBot = pileTop + pileH;
      const logoTop = pileBot + GAP, logoBot = logoTop + blockH, LOGO_CY = logoTop + TILE / 2;
      const outTop = logoBot + GAP;
      const labTopCy = pileTop - 18 - LAB / 2, labBotCy = outTop + outsH + 18 + LAB / 2;
      const ov = Math.max(0, (sumH - pileH) / Math.max(1, cardsT.length - 1));            // solape de la pila (≤ PADB)
      const extra = Math.max(0, (pileH - sumH) / Math.max(1, cardsT.length - 1));
      const rest = []; let yy = pileTop;
      cardH.forEach((h, i) => { rest.push(yy + h / 2); yy += h - ov + extra; });

      // ── luz, entorno, lienzo y sombras
      scene.background = bg.clone();
      scene.environment = kit.studioEnv({ blur: 0.03, ambient: '#1a1216', panels: [
        { pos: [0, 10, 3], size: [14, 4], intensity: 3.0 }, { pos: [-10, 3, 3], size: [2, 12], intensity: 3.6 }, { pos: [10, 2, 2], size: [2, 12], intensity: 2.4 },
      ] });
      scene.environmentIntensity = 0.5;
      scene.add(new THREE.HemisphereLight(0xffffff, new THREE.Color(DARK ? '#1c1c1f' : '#e9e7e3'), DARK ? 0.9 : 1.25));
      const tgt = new THREE.Object3D(); tgt.position.set(0, wy(LOGO_CY), 0); scene.add(tgt);
      // r181: luces físicas (difuso = albedo·I·cosθ/π) → I≈4,2 a ~50° deja el papel frontal en ≈1,0
      const key = new THREE.DirectionalLight(0xffffff, 4.2); key.target = tgt; key.position.set(-5, wy(LOGO_CY) + 8, 8); scene.add(key);
      const shadowLight = new THREE.DirectionalLight(0xffffff, 0.0001);      // solo sombra, casi frontal y algo cenital
      shadowLight.target = tgt; shadowLight.position.set(-1.2, wy(LOGO_CY) + 3.4, 20); shadowLight.castShadow = true;
      shadowLight.shadow.mapSize.set(1024, 1024); shadowLight.shadow.radius = 16; shadowLight.shadow.blurSamples = 16; shadowLight.shadow.bias = -0.0006;
      Object.assign(shadowLight.shadow.camera, { left: -7.5, right: 7.5, top: 8, bottom: -8, near: 5, far: 40 });
      scene.add(shadowLight);
      const WALLZ = -3.2;
      const wallTex = kit.canvasTexture(512, 1024, (g, w, h) => {
        const cs = bg.clone(); cs.convertLinearToSRGB();
        const lift = (v, k2) => Math.round(Math.min(255, v * 255 + (255 - v * 255) * k2));
        const base = `rgb(${Math.round(cs.r * 255)},${Math.round(cs.g * 255)},${Math.round(cs.b * 255)})`;
        g.fillStyle = base; g.fillRect(0, 0, w, h);
        const gr = g.createRadialGradient(w / 2, h * (LOGO_CY / H), 0, w / 2, h * (LOGO_CY / H), w * 0.95);
        gr.addColorStop(0, `rgb(${lift(cs.r, 0.1)},${lift(cs.g, 0.1)},${lift(cs.b, 0.1)})`); gr.addColorStop(0.6, base); gr.addColorStop(1, base);
        g.fillStyle = gr; g.fillRect(0, 0, w, h);
      });
      const fh = 2 * (D * 1.06 - WALLZ) * Math.tan(THREE.MathUtils.degToRad(FOV / 2)) * 1.3, fw = fh * W / H * 1.3;
      const wall = new THREE.Mesh(new THREE.PlaneGeometry(fw, fh), new THREE.MeshBasicMaterial({ map: wallTex }));
      wall.position.set(0, 0, WALLZ); scene.add(wall);
      const catcher = new THREE.Mesh(new THREE.PlaneGeometry(fw, fh), new THREE.ShadowMaterial({ color: new THREE.Color(DARK ? '#000000' : '#2a2622'), opacity: DARK ? 0.5 : 0.28 }));
      catcher.position.set(0, 0, WALLZ + 0.02); catcher.receiveShadow = true; scene.add(catcher);
      const haloTex = kit.radialTexture([[0, 'rgba(255,255,255,0.95)'], [0.35, 'rgba(255,255,255,0.5)'], [0.7, 'rgba(255,255,255,0.1)'], [1, 'rgba(255,255,255,0)']], 512);
      const halo = new THREE.Mesh(new THREE.PlaneGeometry(6.6, 6.6), new THREE.MeshBasicMaterial({ map: haloTex, transparent: true, depthWrite: false, opacity: DARK ? 0.12 : 0.55 }));
      halo.position.set(0, wy(LOGO_CY), WALLZ + 0.05); scene.add(halo);
      const sweep = kit.makeSweep({ dir: [1, -0.6], width: 0.2, intensity: 0.9, color: '#ffffff' });

      // ── fichas de papel (original + copia que viaja)
      const paperSide = new THREE.MeshStandardMaterial({ color: DARK ? 0x1c1c1f : 0xfbf9f6, roughness: 0.9, envMapIntensity: 0.4 });
      const CARD_BG = DARK ? '#18181B' : '#FFFFFF', CARD_FG = DARK ? '#FFFFFF' : INK, CARD_EB = DARK ? '#8C8C92' : '#8D877F';
      const SC = 2;
      const makeCard = (c, i) => {
        const cw = cardW, ch = cardH[i];
        const cv = ctx2d(cw * SC, ch * SC), g = cv.getContext('2d');
        g.scale(SC, SC); g.fillStyle = CARD_BG; g.fillRect(0, 0, cw, ch); g.textAlign = 'center';
        let y = PADT;
        if (c.eyebrow) { font(g, 600, EPX, MONT, 0); g.fillStyle = CARD_EB; g.fillText(c.eyebrow, cw / 2, y + EPX * 0.8); y += EPX + 4; }
        font(g, 700, CPX, MONT, -0.01 * CPX); g.fillStyle = CARD_FG;
        lines[i].forEach((ln, j) => g.fillText(ln, cw / 2, y + j * LH + CPX * 0.84));
        const tex = texture(THREE, cv);
        const mk = () => {
          const face = new THREE.Mesh(kit.roundedPlane(cw * U, ch * U, 22 * U), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.88, envMapIntensity: 0.4, transparent: true }));
          const body = new THREE.Mesh(new k.A.RoundedBoxGeometry(cw * U, ch * U, 0.07, 4, 0.035), paperSide.clone());
          body.material.transparent = true;
          body.castShadow = true; face.position.z = 0.0355;
          const grp = new THREE.Group(); grp.add(body); grp.add(face); scene.add(grp);
          return grp;
        };
        const orig = mk();
        // sombra de contacto sobre la ficha de detrás (canto superior), solo con las fichas ya enderezadas
        let skirt = null;
        if (i > 0) {
          const st = kit.canvasTexture(8, 64, (g2, w2, h2) => {
            const gr = g2.createLinearGradient(0, h2, 0, 0);
            gr.addColorStop(0, 'rgba(24,20,16,0.26)'); gr.addColorStop(0.35, 'rgba(24,20,16,0.10)'); gr.addColorStop(1, 'rgba(24,20,16,0)');
            g2.fillStyle = gr; g2.fillRect(0, 0, w2, h2);
          });
          skirt = new THREE.Mesh(new THREE.PlaneGeometry((cw - 30) * U, 22 * U), new THREE.MeshBasicMaterial({ map: st, transparent: true, depthWrite: false, opacity: 0 }));
          skirt.position.set(0, (ch / 2 + 11) * U, -0.01);
          orig.add(skirt);
        }
        return { orig, copy: mk(), h: ch, skirt };
      };
      const MESSY = [
        { dx: -26, dy: -4, z: -0.85, rx: 10, ry: -12, rz: -9 },
        { dx: 22, dy: 6, z: 0.25, rx: -11, ry: 10, rz: 8 },
        { dx: -10, dy: 4, z: 1.05, rx: 9, ry: -9, rz: -10 },
      ];
      const cards = cardsT.map((c, i) => {
        const m = MESSY[i % 3];
        const cd = makeCard(c, i);
        cd.fy = rest[i];
        cd.messy = { x: W / 2 + m.dx, y: rest[i] + m.dy, z: m.z, rx: m.rx, ry: m.ry, rz: m.rz };
        cd.st = { x: cd.messy.x, y: rest[i] - 820, z: m.z, rx: m.rx * 2.2, ry: m.ry * 2.2, rz: m.rz * 2.2, fl: 0, o: 1, sk: 0, gh: 1 };   // cae desde arriba
        cd.cp = { x: W / 2, y: rest[i], z: 0.02 * i, s: 1, rx: 0, o: 0 };
        cd.seed = 0.7 + i * 1.9;
        return cd;
      });
      // la pose revuelta no invade la etiqueta de arriba ni el bloque del logo (8 esquinas proyectadas con la cámara)
      {
        const fpx = H / (2 * Math.tan(THREE.MathUtils.degToRad(FOV / 2)));
        const e = new THREE.Euler(), v = new THREE.Vector3();
        const span = (cd, m) => {
          e.set(THREE.MathUtils.degToRad(m.rx), THREE.MathUtils.degToRad(m.ry), THREE.MathUtils.degToRad(m.rz));
          let y0 = Infinity, y1 = -Infinity;
          for (const sx of [-1, 1]) for (const sy of [-1, 1]) for (const sz of [-1, 1]) {
            v.set(sx * cardW * U / 2, sy * cd.h * U / 2, sz * 0.035).applyEuler(e);
            const ys = H / 2 - (v.y + wy(m.y)) * fpx / (D - (v.z + m.z));
            y0 = Math.min(y0, ys); y1 = Math.max(y1, ys);
          }
          return [y0, y1];
        };
        const lo = labels.top ? labTopCy + 0.42 * LAB + 9 + 14 : 300, hi = logoTop - 12;
        cards.forEach((cd, i) => {
          for (let it = 0; it < 8; it++) {
            let [y0, y1] = span(cd, cd.messy);
            const fix = (i === 0 ? Math.max(0, lo - y0) : 0) - (i === cards.length - 1 ? Math.max(0, y1 - hi) : 0);
            if (i === 0 && i === cards.length - 1 && y1 - y0 > hi - lo) { cd.messy.rz *= 0.8; cd.messy.rx *= 0.85; continue; }
            if (Math.abs(fix) < 0.5) {
              // la de arriba y la de abajo, además, sin invadir: si la corrección no basta, se suaviza el giro en z
              if ((i === 0 && y0 < lo - 0.5) || (i === cards.length - 1 && y1 > hi + 0.5)) { cd.messy.rz *= 0.8; continue; }
              break;
            }
            cd.messy.y += fix * (D - cd.messy.z) / D;
            [y0, y1] = span(cd, cd.messy);
            if ((i !== 0 || y0 >= lo - 0.5) && (i !== cards.length - 1 || y1 <= hi + 0.5)) break;
            cd.messy.rz *= 0.85;
          }
          cd.st.x = cd.messy.x;
        });
      }

      // ── baldosa + logo + «Nimbo»
      const tileGrp = new THREE.Group(); scene.add(tileGrp);
      const tileMat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.32, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 0.55 });
      sweep.apply(tileMat);
      const tS = TILE * U, tD = 0.32;
      const tile = new THREE.Mesh(new k.A.RoundedBoxGeometry(tS, tS, tD, 6, tS * 0.22), tileMat);
      tile.castShadow = true; tileGrp.add(tile);
      const svg = logoSvg(ctx);
      if (svg) {
        const lg = kit.svgShapes(svg, { height: tS * 0.66, simplify: 1.4, curveSegments: 4 });
        const geo = kit.extrude(lg.shapes, { depth: tS * 0.08, bevelThickness: tS * 0.012, bevelSize: tS * 0.008, bevelSegments: 3, curveSegments: 4 });
        const enamel = new THREE.MeshPhysicalMaterial({ color: new THREE.Color('#E551BA'), roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 0.9 });
        const enamelSide = new THREE.MeshPhysicalMaterial({ color: new THREE.Color('#E551BA').lerp(new THREE.Color('#ffffff'), 0.15), metalness: 0.4, roughness: 0.25, clearcoat: 0.8, envMapIntensity: 1 });
        sweep.apply(enamel); sweep.apply(enamelSide);
        const logo = new THREE.Mesh(geo, [enamel, enamelSide]);
        logo.position.z = tD / 2 + tS * 0.04; tileGrp.add(logo);
      } else if (iconImg) {
        // icono 3D del kit (PNG con alfa) en la cara de la baldosa
        const tex = new THREE.Texture(iconImg); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
        const ar = (iconImg.naturalWidth || 1) / (iconImg.naturalHeight || 1), iw = tS * 0.74 * Math.min(1, ar), ih = tS * 0.74 / Math.max(1, ar);
        const ic = new THREE.Mesh(new THREE.PlaneGeometry(iw, ih), new THREE.MeshBasicMaterial({ map: tex, transparent: true, alphaTest: 0.02, depthWrite: false }));
        ic.position.z = tD / 2 + 0.006; tileGrp.add(ic);
      }
      const tileCy = logoTop + TILE / 2;
      const mLabel = mLabel0;
      if (mLabel) {
        try {
          const ts = kit.textShapes(mLabel, { family: 'Montserrat', weight: 900, size: JEVPX * U, tracking: -0.02 });
          const wg = kit.extrude(ts.glyphs.flatMap((gl) => gl.shapes), { depth: 0.04, bevelThickness: 0.006, bevelSize: 0.004, bevelSegments: 2, curveSegments: 8 });
          const inkMat = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(FG), roughness: 0.6, specularIntensity: 0.18, clearcoat: 0.35, envMapIntensity: 0.22 });
          const word = new THREE.Mesh(wg, inkMat);
          word.castShadow = true;
          // bajo la baldosa, línea base en logoBot − 2
          word.position.set(-ts.width / 2, wy(logoBot - 4) - wy(tileCy), 0.02);
          tileGrp.add(word);
        } catch (e) { console.warn('[scene.pipeline3d] sin el nombre extruido:', e); }
      }

      // ── barras de tinta
      const BAR_BG = DARK ? '#F4F4F1' : '#161514', BAR_FG = DARK ? '#0B0B0C' : '#FFFFFF', BAR_KEY = DARK ? '#77777D' : '#A8A39C';
      const inkSide = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(BAR_BG), roughness: 0.42, clearcoat: 1, clearcoatRoughness: 0.1, envMapIntensity: 0.45 });
      sweep.apply(inkSide);
      const outs = outsT.map((o, i) => {
        const cv = ctx2d(OUT_W * SC, OUT_H * SC), g = cv.getContext('2d');
        g.scale(SC, SC); g.fillStyle = BAR_BG; g.fillRect(0, 0, OUT_W, OUT_H); g.textBaseline = 'alphabetic';
        let px = 44;
        const kTxt = o.key ? o.key + ': ' : '';
        const measure = () => { font(g, 500, px, OUTF, -0.01 * px); const a = g.measureText(kTxt).width; font(g, 700, px, OUTF, -0.01 * px); return [a, g.measureText(o.value).width]; };
        let [ka, va] = measure();
        while (px > 36 && ka + va > OUT_W - 48 - 120) { px -= 1; [ka, va] = measure(); }      // nunca < 36 px
        // etiqueta de origen (el eyebrow de SU ficha) solo si fichas y salidas van 1:1
        const tag = (paired && cardsT[i] && cardsT[i].eyebrow) ? String(cardsT[i].eyebrow) : '';
        let tagW = 0;
        if (tag) {
          font(g, 600, 22, MONT, 0); tagW = Math.ceil(g.measureText(tag).width) + 22;
          const tx = 18, th = 34, ty = (OUT_H - th) / 2;
          g.fillStyle = '#E9E4DE'; g.beginPath(); g.roundRect(tx, ty, tagW, th, 9); g.fill();
          g.fillStyle = '#3B3530'; g.textAlign = 'center'; g.fillText(tag, tx + tagW / 2, ty + th / 2 + 8);
          tagW += 18 + 14;
        }
        const x0 = tagW + (OUT_W - tagW - ka - va) / 2 - (tag ? 8 : 0), by = OUT_H / 2 + px * 0.36;
        font(g, 500, px, OUTF, -0.01 * px); g.fillStyle = BAR_KEY; g.textAlign = 'left'; g.fillText(kTxt, x0, by);
        font(g, 700, px, OUTF, -0.01 * px); g.fillStyle = BAR_FG; g.fillText(o.value, x0 + ka, by);
        const faceMat = new THREE.MeshPhysicalMaterial({ map: texture(THREE, cv), roughness: 0.7, specularIntensity: 0.12, clearcoat: 0.25, clearcoatRoughness: 0.2, envMapIntensity: 0.12 });
        sweep.apply(faceMat);
        const face = new THREE.Mesh(kit.roundedPlane(OUT_W * U, OUT_H * U, 20 * U), faceMat);
        const body = new THREE.Mesh(new k.A.RoundedBoxGeometry(OUT_W * U, OUT_H * U, 0.12, 4, 0.06), inkSide);
        body.castShadow = true; face.position.z = 0.0605;
        const grp = new THREE.Group(); grp.add(body); grp.add(face); grp.visible = false; scene.add(grp);
        const fy = outTop + i * (OUT_H + OUT_GAP) + OUT_H / 2;
        return { grp, fy, st: { y: tileCy, z: -1.6, s: 0.14, rx: 0, o: 0 } };
      });

      // ── etiquetas y flechas (planos con alphaTest: el margen no escribe profundidad)
      const textPlane = (str, px, weight, color, ls) => {
        font(MC, weight, px, MONT, ls * px);
        const m = MC.measureText(str), w = Math.ceil(m.width + px * 0.3), h = Math.ceil(px * 1.35);
        const cv = ctx2d(w * SC, h * SC), g = cv.getContext('2d');
        g.scale(SC, SC); font(g, weight, px, MONT, ls * px); g.fillStyle = color; g.textAlign = 'center';
        g.fillText(str, w / 2, h * 0.5 + px * 0.36);
        const mat = new THREE.MeshBasicMaterial({ map: texture(THREE, cv), transparent: true, depthWrite: true, alphaTest: 0.04, opacity: 0 });
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w * U, h * U), mat);
        scene.add(mesh);
        return { mesh, w, h };
      };
      const labs = [];
      if (labels.top) {
        font(MC, 800, LAB, MONT, -0.02 * LAB);
        const words = String(labels.top).split(/\s+/);
        const totalW = MC.measureText(labels.top).width, spaceW = MC.measureText(' ').width;
        let x = W / 2 - totalW / 2;
        words.forEach((wd, wi) => {
          font(MC, 800, LAB, MONT, -0.02 * LAB);
          const ww = MC.measureText(wd).width;
          if (wi === 0) labs.push({ ...textPlane(wd, LAB, 800, FG, -0.02), cx: x + ww / 2, cy: labTopCy, group: 'top0', st: { o: 0, dy: 10, rz: 0 } });
          else {
            const rnd = k.rng(4242 + wi * 97);
            Array.from(wd).forEach((ch, ci) => {
              font(MC, 800, LAB, MONT, -0.02 * LAB);
              const pre = MC.measureText(wd.slice(0, ci)).width, cw2 = MC.measureText(ch).width;
              labs.push({ ...textPlane(ch, LAB, 800, FG, -0.02), cx: x + pre + cw2 / 2, cy: labTopCy, group: 'top1', zi: ci + 1,
                st: { o: 0, dy: rnd() * 12, rz: (rnd() - 0.5) * 12 }, jit: rnd() });   // desorden solo hacia abajo (arriba ≥ 288)
            });
          }
          x += ww + spaceW;
        });
      }
      if (labels.bottom) labs.push({ ...textPlane(String(labels.bottom), LAB, 800, FG, -0.02), cx: W / 2, cy: labBotCy, group: 'bot', st: { o: 0, dy: 4, rz: 0 } });
      const arrowPlane = (cy) => {
        const w = 24, h = 26, cv = ctx2d(w * SC, h * SC), g = cv.getContext('2d');
        g.scale(SC, SC); g.strokeStyle = DARK ? 'rgba(255,255,255,0.45)' : 'rgba(15,13,16,0.42)'; g.lineWidth = 2.4; g.lineCap = 'round'; g.lineJoin = 'round';
        g.beginPath(); g.moveTo(w / 2, 2); g.lineTo(w / 2, h - 3); g.moveTo(w / 2 - 6, h - 9); g.lineTo(w / 2, h - 3); g.lineTo(w / 2 + 6, h - 9); g.stroke();
        const mat = new THREE.MeshBasicMaterial({ map: texture(THREE, cv), transparent: true, depthWrite: true, alphaTest: 0.04, opacity: 0 });
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w * U, h * U), mat); scene.add(mesh);
        return { mesh, cx: W / 2, cy, group: 'arrow', st: { o: 0, dy: 0, rz: 0 } };
      };
      const arrows = [arrowPlane(logoTop - GAP / 2), arrowPlane(logoBot + GAP / 2)];
      labs.push(...arrows);

      // ── tiempos (locales)
      const c = (n, d) => (k.cues[n] != null ? k.cues[n] : d);
      const tM = Math.max(f(4), c('messy', 0.35));
      const tL1 = Math.max(tM + f(6), c('label_top', tM + 0.9));
      const tL2 = Math.max(tL1 + f(6), c('label_top2', tL1 + 0.45));
      const tT = Math.max(tM + f(24), c('transform', tL2 + 0.8));
      const tLB = Math.max(tT + f(14), c('label_bottom', tT + 0.7));
      const STAG = f(11);
      const cam = { orbit: -6, dolly: 1.06, push: 1 }, tileSt = { s: 1.62, pulse: 1, sweep: 99 }, focus = { z: 0.15 };
      k.state = { cam, tileSt, focus };
      // logo: aparece en su sitio (0,9 → 1, 9 f) y se asienta
      tl.fromTo(tileSt, { s: 1.62 }, { s: 1.72, duration: f(8), ease: EASE.enter, immediateRender: false }, f(1));
      tl.fromTo(tileSt, { s: 1.72 }, { s: 1, duration: f(11), ease: EASE.move, immediateRender: false }, tM);
      // fichas: caen desde arriba con gravedad, choque con rebote ≤ 8 px, giro amortiguado; luego flotan
      cards.forEach((cd, i) => {
        const at = tM + f(2) + i * f(3);
        tl.fromTo(cd.st, { y: cd.st.y }, { y: cd.messy.y + 8, duration: f(10), ease: 'power2.in', immediateRender: false }, at);
        tl.fromTo(cd.st, { y: cd.messy.y + 8 }, { y: cd.messy.y, duration: f(7), ease: 'power2.out', immediateRender: false }, at + f(10));
        tl.fromTo(cd.st, { rx: cd.st.rx, ry: cd.st.ry, rz: cd.st.rz }, { rx: cd.messy.rx, ry: cd.messy.ry, rz: cd.messy.rz, duration: f(18), ease: 'power3.out', immediateRender: false }, at);
        tl.fromTo(cd.st, { fl: 0 }, { fl: 1, duration: f(12), ease: 'none', immediateRender: false }, at + f(14));
        if (k.ctx.event) k.ctx.event('card_drop', k.ctx.item.t0 + at + f(10));
        // transform: se endereza (una a una) → la COPIA cruza por detrás de la baldosa → barra de tinta en su hueco
        const ti = tT + i * STAG;
        tl.fromTo(cd.st, { x: cd.messy.x, y: cd.messy.y, z: cd.messy.z, rx: cd.messy.rx, ry: cd.messy.ry, rz: cd.messy.rz, fl: 1 },
          { x: W / 2, y: cd.fy, z: 0.02 * i, rx: 0, ry: 0, rz: 0, fl: 0, duration: f(7), ease: EASE.move, immediateRender: false }, ti);
        tl.fromTo(cd.st, { sk: 0 }, { sk: 1, duration: f(6), ease: 'none', immediateRender: false }, ti + f(5));
        tl.set(cd.cp, { o: 1 }, ti + f(7));
        // recorrido legible: se adelanta (z +1,2) y baja recto POR DELANTE de la pila; al final se hunde POR DETRÁS de
        // la baldosa encogiendo (allí cambia de material, oculto)
        tl.fromTo(cd.cp, { y: cd.fy }, { y: tileCy, duration: f(12), ease: 'power2.inOut', immediateRender: false }, ti + f(7));
        tl.fromTo(cd.cp, { z: 0.02 * i + 0.01 }, { z: 1.2, duration: f(3), ease: 'power2.out', immediateRender: false }, ti + f(7));
        tl.fromTo(cd.cp, { z: 1.2 }, { z: -1.6, duration: f(4), ease: 'power2.in', immediateRender: false }, ti + f(15));
        tl.fromTo(cd.cp, { s: 1 }, { s: 0.9, duration: f(8), ease: 'none', immediateRender: false }, ti + f(7));
        tl.fromTo(cd.cp, { s: 0.9 }, { s: 0.14, duration: f(4), ease: 'power2.in', immediateRender: false }, ti + f(15));
        tl.fromTo(cd.cp, { rx: 0 }, { rx: -12, duration: f(12), ease: 'power1.in', immediateRender: false }, ti + f(7));
        tl.set(cd.cp, { o: 0 }, ti + f(19));
        tl.fromTo(cd.st, { gh: 1 }, { gh: 0.42, duration: f(8), ease: EASE.move, immediateRender: false }, ti + f(12));   // procesada: se atenúa
      });
      outs.forEach((o, j) => {
        const nC = Math.max(1, cards.length), nO = Math.max(1, outs.length);
        const i = Math.min(nC - 1, Math.floor(j * nC / nO)), ti = tT + i * STAG;
        const sub = paired ? 0 : (j - Math.ceil(i * nO / nC)) * f(6);          // varias salidas de la misma ficha: 6 f entre ellas
        if (o) {
          const at2 = ti + f(18) + Math.max(0, sub);
          tl.set(o.st, { o: 1 }, at2);
          tl.fromTo(o.st, { y: tileCy, s: 0.14 }, { y: o.fy + 3, s: 1, duration: f(11), ease: 'expo.out', immediateRender: false }, at2);
          tl.fromTo(o.st, { y: o.fy + 3 }, { y: o.fy, duration: f(4), ease: EASE.move, immediateRender: false }, at2 + f(11));   // follow-through
          tl.fromTo(o.st, { z: -1.6 }, { z: -0.75, duration: f(5), ease: 'power1.out', immediateRender: false }, at2);           // por detrás de las ya posadas
          tl.fromTo(o.st, { z: -0.75 }, { z: 0, duration: f(8), ease: EASE.move, immediateRender: false }, at2 + f(5));
          tl.fromTo(o.st, { rx: 14 }, { rx: 0, duration: f(13), ease: EASE.move, immediateRender: false }, at2);
          if (k.ctx.event) k.ctx.event('option', k.ctx.item.t0 + at2 + f(11));
        }
      });
      cards.forEach((cd, i) => {
        const ti = tT + i * STAG;
        // pulso de la baldosa en cada paso
        tl.fromTo(tileSt, { pulse: 1 }, { pulse: 1.05, duration: f(4), ease: EASE.move, immediateRender: false }, ti + f(15));
        tl.fromTo(tileSt, { pulse: 1.05 }, { pulse: 1, duration: f(6), ease: EASE.pop, immediateRender: false }, ti + f(19));
      });
      // barrido especular: baldosa durante los pasos y luego las barras ya posadas
      const tSw = tT + f(8), swDur = Math.max(1.2, (cards.length - 1) * STAG + f(30));
      tl.fromTo(tileSt, { sweep: -2.6 }, { sweep: 3.8, duration: swDur, ease: 'power1.inOut', immediateRender: false }, tSw);
      tl.set(tileSt, { sweep: 99 }, tSw + swDur);
      // etiquetas y flechas
      labs.forEach((lb) => {
        if (lb.group === 'top0') tl.fromTo(lb.st, { o: 0, dy: 10 }, { o: 1, dy: 0, duration: f(6), ease: EASE.enter, immediateRender: false }, tL1);
        else if (lb.group === 'top1') tl.fromTo(lb.st, { o: 0, dy: lb.st.dy, rz: lb.st.rz }, { o: 1, dy: 0, rz: 0, duration: f(8), ease: EASE.enter, immediateRender: false }, tL2 + lb.jit * f(2));
        else if (lb.group === 'bot') tl.fromTo(lb.st, { o: 0, dy: 4 }, { o: 1, dy: 0, duration: f(7), ease: EASE.enter, immediateRender: false }, tLB);   // tinta ≤ 1240
      });
      tl.fromTo(arrows[0].st, { o: 0 }, { o: 1, duration: f(6), ease: 'none', immediateRender: false }, tT);
      tl.fromTo(arrows[1].st, { o: 0 }, { o: 1, duration: f(6), ease: 'none', immediateRender: false }, tT + f(17));
      // cámara: órbita con dolly durante el desorden (paralaje), frontal antes del cruce, push lento en reposo
      const tOrbEnd = Math.max(tM + f(12), tT - f(10));
      tl.fromTo(cam, { orbit: -6, dolly: 1.06 }, { orbit: 5, dolly: 1.0, duration: tOrbEnd - tM, ease: 'sine.inOut', immediateRender: false }, tM);
      tl.fromTo(cam, { orbit: 5 }, { orbit: 0, duration: f(10), ease: EASE.move, immediateRender: false }, tOrbEnd);
      const tRest = tT + Math.max(cards.length - 1, outs.length - 1) * STAG + f(32);
      if (dur - tRest > 0.4) tl.fromTo(cam, { push: 1 }, { push: 1.02, duration: dur - tRest, ease: EASE.move, immediateRender: false }, tRest);
      if (k.ctx.event) k.ctx.event('flip', k.ctx.item.t0 + tT);

      k.objs = { camera, cards, outs, labs, tileGrp, tileCy, sweep, wx, wy, D, tT, STAG };
    },

    update(t, cues, k) {
      const o = k.objs, S = k.state, THREE = k.THREE, deg = THREE.MathUtils.degToRad;
      const { wx, wy } = o;
      // fichas: original (se endereza) + copia (cruza)
      let fw = 0, fz = 0;
      o.cards.forEach((cd, i) => {
        const s = cd.st, fl = s.fl || 0;
        cd.orig.visible = s.o > 0.5;
        cd.orig.position.set(wx(s.x + Math.sin(t * 0.9 + cd.seed) * 7 * fl), wy(s.y + Math.cos(t * 0.7 + cd.seed) * 5 * fl), s.z + Math.sin(t * 0.6 + cd.seed) * 0.14 * fl);
        cd.orig.rotation.set(deg(s.rx + Math.sin(t * 0.8 + cd.seed) * 1.6 * fl), deg(s.ry + Math.cos(t * 0.65 + cd.seed) * 1.8 * fl), deg(s.rz));
        if (cd.skirt) { cd.skirt.material.opacity = (s.sk || 0) * (s.gh != null ? s.gh : 1); cd.skirt.visible = (s.sk || 0) > 0.01; }
        const gh = s.gh != null ? s.gh : 1;
        cd.orig.children[0].material.opacity = gh; cd.orig.children[1].material.opacity = gh; cd.orig.children[0].castShadow = gh > 0.7;
        const p = cd.cp;
        cd.copy.visible = p.o > 0.5;
        cd.copy.position.set(wx(p.x), wy(p.y), p.z);
        cd.copy.rotation.set(deg(p.rx), 0, 0);
        cd.copy.scale.setScalar(p.s);
        // foco: la copia que está cruzando (peso suave por su progreso)
        if (p.o > 0.5) { fw += 1; fz += p.z; }
      });
      // baldosa
      const ts = S.tileSt;
      o.tileGrp.position.set(0, wy(o.tileCy), 0);
      o.tileGrp.scale.setScalar(ts.s * ts.pulse);
      o.sweep.uniforms.uSweepPos.value = ts.sweep;
      // barras de tinta
      o.outs.forEach((ou) => {
        const s = ou.st;
        ou.grp.visible = s.o > 0.5;
        ou.grp.position.set(0, wy(s.y), s.z);
        ou.grp.rotation.set(deg(s.rx), 0, 0);
        ou.grp.scale.setScalar(s.s);
      });
      // etiquetas
      o.labs.forEach((lb) => {
        const s = lb.st;
        lb.mesh.material.opacity = s.o;
        lb.mesh.visible = s.o > 0.004;
        lb.mesh.position.set(wx(lb.cx), wy(lb.cy + s.dy), 0.01 + (lb.zi || 0) * 0.0004);
        lb.mesh.rotation.z = deg(s.rz);
      });
      // cámara: órbita alrededor del eje vertical x=0,z=0 (la columna central queda fija en pantalla) + dolly + push
      const cam = o.camera, th = deg(S.cam.orbit), Dc = o.D * S.cam.dolly / S.cam.push;
      cam.position.set(Dc * Math.sin(th), 0, Dc * Math.cos(th));
      cam.rotation.set(0, th, 0);
      cam.updateMatrixWorld();
      // DOF: en el desorden, la pila; en el cruce, la ficha que cruza
      const zf = fw > 0 ? fz / fw : 0.15;
      k.post.focus = Dc - zf;
      k.post.aperture = fw > 0 ? 42 : 85;   // en el cruce, foco en la copia pero sin emborronar el plano
    },
  });
})();
