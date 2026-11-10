/* cutkit · three/ck3d.js — capa 3D/WebGL OPCIONAL sobre el runtime de cutkit (HyperFrames 0.8.114 + GSAP 3.15)
 * ═══════════════════════════════════════════════════════════════════════════════════════════
 * Se carga SOLO si el render_spec usa una escena 3D (html.py → ck3d/). Requiere window.THREE + THREE_ADDONS
 * (vendor/three.ck.min.js), window.fontkit (vendor/fontkit.ck.min.js), window.CK (runtime.js) y, opcional,
 * window.__CK3D_ASSETS (ck3d/assets.js: fuentes en base64 y SVG en texto, embebidos por html.py → montaje SÍNCRONO).
 *
 * API (detalle en three/README.md):
 *   CK3D.scene(name, def)   registra una escena como componente CK (CK.register) con
 *     def = {
 *       fallback?: "logo.reveal",              componente 2D al que delegar si WebGL/setup fallan
 *       options?: {fov, motionBlur:{samples, shutter}, dof:{…}, bloom:{…}, grade:{…}, shadows, msaa, fit:"full"|"slot"},
 *       setup(scene, camera, renderer, ctx, props, k)   construye la escena y anima `k.tl` (timeline GSAP PRIVADA,
 *                                                       en segundos LOCALES del item) sobre objetos JS / post,
 *       update?(tLocal, cues, k)                         estado procedimental en tLocal (subfotograma incluido),
 *     }
 *   k = {THREE, A, tl, dur, fps, W, H, cues (locales), props, ctx, post, kit, rng, frameAt(t), px(x,y,z?)}
 *
 * CÓMO SE SINCRONIZA (determinista, sin callbacks):
 *   HyperFrames hace seek de la timeline principal (`totalTime(t, …)`) y DESPUÉS despacha `hf-seek` {time} en window
 *   (adaptador «three» del runtime de HF). CK3D escucha `hf-seek` y, para cada instancia activa en t, renderiza:
 *     para cada subinstante s del obturador (motion blur real por acumulación): k.tl.totalTime(s) → update(s) → render
 *     HDR → acumula; luego DOF → bloom → grado (exposición, tonemap PBR Neutral, aberración, viñeta, grano con semilla
 *     = nº de fotograma) → canvas. Todo es función pura de t: da igual el orden de los fotogramas o el nº de workers.
 *   En la vista previa sin HF (`window.__ckSeek`, boxes.js) se envuelve __ckSeek para renderizar igual.
 * ═══════════════════════════════════════════════════════════════════════════════════════════ */
(function (global) {
  'use strict';
  const THREE = global.THREE, A = global.THREE_ADDONS, CK = global.CK;
  if (!THREE || !A || !CK) { console.error('[CK3D] faltan THREE / THREE_ADDONS / CK: la capa 3D no se carga'); return; }
  if (global.CK3D) return;

  const DEFAULTS = {
    fov: 24, near: 0.1, far: 200, fit: 'full', msaa: 4, shadows: true,
    motionBlur: { samples: 8, shutter: 0.5 },          // 180° · samples=1 lo desactiva
    dof: { enabled: false, focus: 10, aperture: 0, maxBlur: 18 },
    bloom: { strength: 0.6, radius: 0.55, threshold: 1.0 },
    grade: { exposure: 1.0, vignette: 0.38, grain: 0.035, ca: 0.0012, contrast: 1.0, saturation: 1.0, lift: 0.0, tonemap: 'neutral' },
    shadowType: 'pcfsoft',                             // 'pcfsoft' | 'vsm' (sombra blanda con radius/blurSamples)
    background: '#0F0D10',
  };
  const MAX_INSTANCES = 6;   // un contexto WebGL por instancia (Chrome admite ~16 por página)

  const CK3D = { version: '1.0.0', scenes: Object.create(null), instances: [], errors: [], fonts: Object.create(null),
    stats: { frames: 0, ms: 0, last: 0 } };

  // ─────────────────────────────────────────────── utilidades
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  function mulberry32(seed) {
    let a = (seed >>> 0) || 1;
    return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  function deepMerge(a, b) {
    const o = Array.isArray(a) ? a.slice() : Object.assign({}, a);
    for (const k in b || {}) {
      const v = b[k];
      o[k] = v && typeof v === 'object' && !Array.isArray(v) && a && typeof a[k] === 'object' ? deepMerge(a[k], v) : v;
    }
    return o;
  }
  function b64ToBytes(b64) {
    const bin = atob(b64); const n = bin.length; const out = new Uint8Array(n);
    for (let i = 0; i < n; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  const ASSETS = () => global.__CK3D_ASSETS || { fonts: {}, svg: {} };

  // ─────────────────────────────────────────────── fuentes (fontkit, síncrono desde assets.js)
  function getFont(family, style) {
    const key = family + '|' + (style || 'normal');
    if (CK3D.fonts[key]) return CK3D.fonts[key];
    const b64 = ASSETS().fonts[key];
    if (!b64) throw new Error('[CK3D] fuente no embebida: ' + key + ' (decláralo en fonts3d del registro)');
    if (!global.fontkit) throw new Error('[CK3D] falta fontkit');
    const font = global.fontkit.create(b64ToBytes(b64));
    CK3D.fonts[key] = font;
    return font;
  }

  // ─────────────────────────────────────────────── geometría: contornos → THREE.Shape
  function rdp(pts, eps) {            // Ramer–Douglas–Peucker sobre polilínea abierta
    if (pts.length < 3) return pts.slice();
    const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1;
    const stack = [[0, pts.length - 1]];
    while (stack.length) {
      const [a, b] = stack.pop(); let md = 0, mi = -1;
      const ax = pts[a].x, ay = pts[a].y, bx = pts[b].x, by = pts[b].y, dx = bx - ax, dy = by - ay, L = Math.hypot(dx, dy) || 1e-9;
      for (let i = a + 1; i < b; i++) {
        const d = Math.abs(dy * pts[i].x - dx * pts[i].y + bx * ay - by * ax) / L;
        if (d > md) { md = d; mi = i; }
      }
      if (md > eps && mi > 0) { keep[mi] = 1; stack.push([a, mi], [mi, b]); }
    }
    return pts.filter((_, i) => keep[i]);
  }
  function simplifyRing(pts, eps) {   // anillo cerrado: parte por el punto más lejano del primero
    let ring = pts.slice();
    if (ring.length > 1 && ring[0].distanceTo(ring[ring.length - 1]) < 1e-6) ring.pop();
    if (ring.length < 4 || !(eps > 0)) return ring;
    let far = 0, fd = -1;
    for (let i = 1; i < ring.length; i++) { const d = ring[i].distanceTo(ring[0]); if (d > fd) { fd = d; far = i; } }
    const a = rdp(ring.slice(0, far + 1), eps), b = rdp(ring.slice(far).concat([ring[0]]), eps);
    return a.slice(0, -1).concat(b.slice(0, -1));
  }
  /** Shapes (THREE.Shape[]) de un SVG en texto. Y hacia arriba, centradas en (0,0), alto = `height` (unidades).
   *  opts: {height=1, simplify=0 (px del viewBox, RDP), curveSegments=6} → {shapes, width, height} */
  function svgShapes(svgText, opts) {
    opts = opts || {};
    const data = new A.SVGLoader().parse(svgText);
    const raw = [];
    data.paths.forEach((p) => {
      const st = p.userData && p.userData.style || {};
      if (st.fill === 'none' || st.fill === 'transparent') return;
      A.SVGLoader.createShapes(p).forEach((s) => raw.push(s));
    });
    if (!raw.length) throw new Error('[CK3D] SVG sin rellenos');
    const seg = opts.curveSegments || 6, eps = opts.simplify || 0;
    const rings = raw.map((s) => {
      const e = s.extractPoints(seg);
      return { outer: simplifyRing(e.shape, eps), holes: e.holes.map((h) => simplifyRing(h, eps)) };
    });
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    rings.forEach((r) => r.outer.forEach((p) => { x0 = Math.min(x0, p.x); x1 = Math.max(x1, p.x); y0 = Math.min(y0, p.y); y1 = Math.max(y1, p.y); }));
    const H = opts.height || 1, s = H / (y1 - y0), cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const tr = (p) => new THREE.Vector2((p.x - cx) * s, -(p.y - cy) * s);   // SVG y↓ → y↑
    const shapes = rings.map((r) => {
      const sh = new THREE.Shape(r.outer.map(tr));
      r.holes.forEach((h) => sh.holes.push(new THREE.Path(h.map(tr))));
      return sh;
    });
    return { shapes, width: (x1 - x0) * s, height: H };
  }
  function pathToShapes(cmds, sc, ox, oy) {
    const sp = new THREE.ShapePath();
    const X = (v) => ox + v * sc, Y = (v) => oy + v * sc;
    for (const c of cmds) {
      const a = c.args;
      switch (c.command) {
        case 'moveTo': sp.moveTo(X(a[0]), Y(a[1])); break;
        case 'lineTo': sp.lineTo(X(a[0]), Y(a[1])); break;
        case 'quadraticCurveTo': sp.quadraticCurveTo(X(a[0]), Y(a[1]), X(a[2]), Y(a[3])); break;
        case 'bezierCurveTo': sp.bezierCurveTo(X(a[0]), Y(a[1]), X(a[2]), Y(a[3]), X(a[4]), Y(a[5])); break;
        case 'closePath': if (sp.currentPath) sp.currentPath.closePath(); break;
        default: break;
      }
    }
    return sp.toShapes(false);
  }
  /** Contornos de texto con la fuente local (kerning GPOS de fontkit, variaciones: wght). Unidades: `size` = em.
   *  → {glyphs:[{char, shapes, x, adv}], width, capHeight, ascent, descent} (origen: línea base, x=0 a la izquierda) */
  function textShapes(text, o) {
    o = o || {};
    let f = getFont(o.family || 'Montserrat', o.style || 'normal');
    if (o.weight && f.variationAxes && f.variationAxes.wght) f = f.getVariation({ wght: o.weight });
    const run = f.layout(String(text));
    const sc = (o.size || 1) / f.unitsPerEm, track = (o.tracking || 0) * (o.size || 1);
    const chars = Array.from(String(text));
    const glyphs = []; let x = 0;
    run.glyphs.forEach((g, i) => {
      const p = run.positions[i];
      const shapes = pathToShapes(g.path.commands, sc, x + p.xOffset * sc, p.yOffset * sc);
      glyphs.push({ char: chars[i] || '', shapes, x, adv: p.xAdvance * sc });
      x += p.xAdvance * sc + track;
    });
    return { glyphs, width: x - track, capHeight: (f.capHeight || f.ascent * 0.7) * sc, ascent: f.ascent * sc, descent: f.descent * sc };
  }
  /** Extrusión con bisel + normales con pliegue (aristas vivas, curvas suaves). groups: 0 = tapas, 1 = laterales/bisel */
  function extrude(shapes, o) {
    o = o || {};
    const g = new THREE.ExtrudeGeometry(shapes, {
      depth: o.depth != null ? o.depth : 0.2, steps: 1, curveSegments: o.curveSegments || 8,
      bevelEnabled: o.bevel !== false, bevelThickness: o.bevelThickness != null ? o.bevelThickness : 0.02,
      bevelSize: o.bevelSize != null ? o.bevelSize : 0.015, bevelOffset: 0, bevelSegments: o.bevelSegments || 4,
    });
    g.translate(0, 0, -(o.depth != null ? o.depth : 0.2) / 2);
    const out = A.BufferGeometryUtils.toCreasedNormals(g, o.crease != null ? o.crease : Math.PI / 5);
    g.dispose();
    // tapas (grupo 0) con normal PLANA: si no, el borde de la tapa se promedia con el bisel y salen vetas diagonales
    const nrm = out.attributes.normal, pos = out.attributes.position;
    const va = new THREE.Vector3(), vb = new THREE.Vector3(), vc = new THREE.Vector3();
    (out.groups || []).filter((gr) => gr.materialIndex === 0).forEach((gr) => {
      for (let i = gr.start; i < gr.start + gr.count; i += 3) {
        va.fromBufferAttribute(pos, i); vb.fromBufferAttribute(pos, i + 1); vc.fromBufferAttribute(pos, i + 2);
        vb.sub(va); vc.sub(va); vb.cross(vc).normalize();
        for (let j = 0; j < 3; j++) nrm.setXYZ(i + j, vb.x, vb.y, vb.z);
      }
    });
    nrm.needsUpdate = true;
    return out;
  }
  /** Barrido especular art-dirigible: banda diagonal en espacio de MUNDO sumada a la luz saliente del material
   *  (Standard/Physical). Uniforms compartidos → un solo tween mueve el barrido en todos los materiales.
   *  makeSweep({dir:[x,y], width, intensity, color}) → {uniforms, apply(material)} · anima uniforms.uSweepPos.value */
  function makeSweep(o) {
    o = o || {};
    const d = new THREE.Vector2().fromArray(o.dir || [1, -0.45]).normalize();
    const c = new THREE.Color(o.color || '#ffffff');
    const uniforms = { uSweepPos: { value: -99 }, uSweepWidth: { value: o.width || 0.18 }, uSweepIntensity: { value: o.intensity != null ? o.intensity : 2.5 },
      uSweepDir: { value: d }, uSweepColor: { value: new THREE.Vector3(c.r, c.g, c.b) } };
    return {
      uniforms,
      apply(material) {
        material.onBeforeCompile = (sh) => {
          Object.assign(sh.uniforms, uniforms);
          sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vCkW;')
            .replace('#include <project_vertex>', '#include <project_vertex>\nvCkW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
          sh.fragmentShader = sh.fragmentShader.replace('#include <common>',
            '#include <common>\nvarying vec3 vCkW; uniform float uSweepPos, uSweepWidth, uSweepIntensity; uniform vec2 uSweepDir; uniform vec3 uSweepColor;')
            .replace('#include <opaque_fragment>', [
              'float ckD = dot(vCkW.xy, uSweepDir) - uSweepPos;',
              'float ckB = exp(-ckD * ckD / (uSweepWidth * uSweepWidth));',
              'float ckFace = clamp(abs(dot(normalize(normal), normalize(vViewPosition))), 0.0, 1.0);',
              'outgoingLight += uSweepColor * ckB * uSweepIntensity * (0.55 + 0.45 * pow(1.0 - ckFace, 2.0));',
              '#include <opaque_fragment>'].join('\n'));
        };
        material.customProgramCacheKey = () => 'ck-sweep-v1';
        material.needsUpdate = true;
        return material;
      },
    };
  }

  // ─────────────────────────────────────────────── texturas procedimentales (deterministas)
  function canvasTexture(w, h, draw, srgb) {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = srgb === false ? THREE.NoColorSpace : THREE.SRGBColorSpace;
    t.needsUpdate = true;
    return t;
  }
  function radialTexture(stops, size) {
    size = size || 512;
    return canvasTexture(size, size, (g, w, h) => {
      const gr = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
      stops.forEach(([o, c]) => gr.addColorStop(o, c));
      g.fillStyle = gr; g.fillRect(0, 0, w, h);
    });
  }
  /** Entorno de estudio (PMREM) con softboxes emisivos: reflejos limpios tipo producto.
   *  panels: [{pos:[x,y,z], size:[w,h], intensity, color}] (miran al origen) */
  function studioEnv(renderer, o) {
    o = o || {};
    const sc = new THREE.Scene();
    const room = new THREE.Mesh(new THREE.SphereGeometry(30, 32, 16), new THREE.MeshBasicMaterial({ color: new THREE.Color(o.ambient || '#050407'), side: THREE.BackSide }));
    sc.add(room);
    const panels = o.panels || [
      { pos: [0, 9, 4], size: [14, 3], intensity: 6 },          // cenital ancho
      { pos: [-9, 2, 5], size: [1.6, 12], intensity: 9 },       // tira izquierda
      { pos: [9, 1, 3], size: [1.2, 12], intensity: 5 },        // tira derecha
      { pos: [2, -2, 10], size: [8, 4], intensity: 1.6 },       // relleno frontal suave
      { pos: [0, 3, -9], size: [10, 6], intensity: 1.2, color: '#ffd9f0' },  // contraluz
    ];
    panels.forEach((p) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(p.size[0], p.size[1]),
        new THREE.MeshBasicMaterial({ color: new THREE.Color(p.color || '#ffffff').multiplyScalar(p.intensity || 1), side: THREE.DoubleSide }));
      m.position.set(p.pos[0], p.pos[1], p.pos[2]); m.lookAt(0, 0, 0); sc.add(m);
    });
    const pm = new THREE.PMREMGenerator(renderer);
    const rt = pm.fromScene(sc, o.blur != null ? o.blur : 0.02, 0.1, 100);
    pm.dispose();
    sc.traverse((n) => { if (n.geometry) n.geometry.dispose(); if (n.material) n.material.dispose(); });
    return rt.texture;
  }

  // ─────────────────────────────────────────────── partículas con bokeh (CoC por partícula)
  /** Polvo en suspensión: discos de bokeh según su distancia al plano de foco (cámara física simplificada).
   *  o: {count, seed, box:[x0,x1,y0,y1,z0,z1], size (px de diámetro a 10 u de la cámara), color, intensity, drift:[vx,vy,vz]}
   *  aperture (update) = px de CoC por unidad de |z − foco| / z (el mismo valor que k.post.aperture para que case con el DOF)
   *  → {points, update(t, camera, focus, aperture)} */
  function bokehParticles(o) {
    o = o || {};
    const n = o.count || 160, rnd = mulberry32(o.seed || 7), b = o.box || [-4, 4, -6, 6, -6, 4];
    const pos = new Float32Array(n * 3), rnd4 = new Float32Array(n * 4);
    for (let i = 0; i < n; i++) {
      pos[i * 3] = b[0] + rnd() * (b[1] - b[0]); pos[i * 3 + 1] = b[2] + rnd() * (b[3] - b[2]); pos[i * 3 + 2] = b[4] + rnd() * (b[5] - b[4]);
      rnd4[i * 4] = rnd(); rnd4[i * 4 + 1] = rnd(); rnd4[i * 4 + 2] = rnd(); rnd4[i * 4 + 3] = rnd();
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('aRnd', new THREE.BufferAttribute(rnd4, 4));
    const col = new THREE.Color(o.color || '#ffffff');
    const mat = new THREE.ShaderMaterial({
      uniforms: { uTime: { value: 0 }, uFocus: { value: 10 }, uAperture: { value: 40 }, uSize: { value: o.size || 3 },
        uScale: { value: 1 }, uColor: { value: new THREE.Vector3(col.r, col.g, col.b) }, uIntensity: { value: o.intensity || 1 },
        uDrift: { value: new THREE.Vector3().fromArray(o.drift || [0.05, 0.12, 0]) }, uFade: { value: 1 } },
      vertexShader: `
        attribute vec4 aRnd; uniform float uTime, uFocus, uAperture, uSize, uScale; uniform vec3 uDrift;
        varying float vA; varying float vCoc;
        void main(){
          vec3 p = position + uDrift * uTime * (0.5 + aRnd.x)
                 + vec3(sin(uTime*0.7 + aRnd.y*6.28), cos(uTime*0.5 + aRnd.z*6.28), sin(uTime*0.6 + aRnd.w*6.28)) * 0.06;
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          float z = -mv.z;
          float base = uSize * (0.4 + aRnd.w) * 10.0 / max(z, 0.1);
          float coc = uAperture * abs(z - uFocus) / max(z, 0.1);
          float s = clamp(sqrt(base * base + coc * coc), 1.0, 96.0);
          vCoc = coc / max(s, 1.0);
          vA = (base * base) / (s * s) * (0.35 + 0.65 * aRnd.x);
          gl_PointSize = s; gl_Position = projectionMatrix * mv;
        }`,
      fragmentShader: `
        uniform vec3 uColor; uniform float uIntensity, uFade; varying float vA; varying float vCoc;
        void main(){
          vec2 d = gl_PointCoord - 0.5; float r = length(d) * 2.0;
          if (r > 1.0) discard;
          float disc = smoothstep(1.0, 0.86, r);
          float ring = mix(1.0, 0.75 + 0.6 * smoothstep(0.55, 0.95, r), vCoc);   // borde algo más brillante en el bokeh
          float core = mix(exp(-r*r*4.0), 1.0, vCoc);                            // en foco: punto suave
          gl_FragColor = vec4(uColor * uIntensity * vA * disc * ring * core * uFade, 1.0);
        }`,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    const points = new THREE.Points(geo, mat);
    points.frustumCulled = false;
    return {
      points, material: mat,
      update(t, camera, focus, aperture, H) {
        mat.uniforms.uTime.value = t;
        mat.uniforms.uFocus.value = focus;
        mat.uniforms.uAperture.value = aperture;
        // px por unidad a distancia 1: H / (2 tan(fov/2))
        mat.uniforms.uScale.value = (H || 1920) / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2));
      },
    };
  }

  /** Plano con esquinas redondeadas y UV 0..1 en su caja (para caras con texto/imagen nítidos, sin deformar) */
  function roundedPlane(w, h, r, seg) {
    r = Math.min(r || 0, w / 2, h / 2);
    const s = new THREE.Shape();
    s.moveTo(-w / 2 + r, -h / 2); s.lineTo(w / 2 - r, -h / 2); s.quadraticCurveTo(w / 2, -h / 2, w / 2, -h / 2 + r);
    s.lineTo(w / 2, h / 2 - r); s.quadraticCurveTo(w / 2, h / 2, w / 2 - r, h / 2); s.lineTo(-w / 2 + r, h / 2);
    s.quadraticCurveTo(-w / 2, h / 2, -w / 2, h / 2 - r); s.lineTo(-w / 2, -h / 2 + r); s.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + r, -h / 2);
    const g = new THREE.ShapeGeometry(s, seg || 10);
    const uv = g.attributes.uv, p = g.attributes.position;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, p.getX(i) / w + 0.5, p.getY(i) / h + 0.5);
    return g;
  }

  // ─────────────────────────────────────────────── planos de imagen (capturas reales) con esquinas y sombra
  /** img: HTMLImageElement/Canvas (decodificado) · o: {width (u), radius (fracción del lado corto), shadow:0..1}
   *  → THREE.Group con .userData.plane (MeshStandardMaterial con mapa) */
  function imagePlane(img, o) {
    o = o || {};
    const iw = img.naturalWidth || img.width, ih = img.naturalHeight || img.height;
    const w = o.width || 2, h = w * ih / iw, r = (o.radius != null ? o.radius : 0.04) * Math.min(w, h);
    const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
    const shape = new THREE.Shape();
    shape.moveTo(-w / 2 + r, -h / 2); shape.lineTo(w / 2 - r, -h / 2); shape.quadraticCurveTo(w / 2, -h / 2, w / 2, -h / 2 + r);
    shape.lineTo(w / 2, h / 2 - r); shape.quadraticCurveTo(w / 2, h / 2, w / 2 - r, h / 2); shape.lineTo(-w / 2 + r, h / 2);
    shape.quadraticCurveTo(-w / 2, h / 2, -w / 2, h / 2 - r); shape.lineTo(-w / 2, -h / 2 + r); shape.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + r, -h / 2);
    const geo = new THREE.ShapeGeometry(shape, 12);
    const uv = geo.attributes.uv, p = geo.attributes.position;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, p.getX(i) / w + 0.5, p.getY(i) / h + 0.5);
    const plane = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.42, metalness: 0, envMapIntensity: 0.35,
      emissive: new THREE.Color('#ffffff'), emissiveMap: tex, emissiveIntensity: o.emissive != null ? o.emissive : 0.55 }));
    const grp = new THREE.Group(); grp.add(plane); grp.userData.plane = plane;
    if (o.shadow !== 0) {
      const sh = new THREE.Mesh(new THREE.PlaneGeometry(w * 1.35, h * 1.35), new THREE.MeshBasicMaterial({
        map: canvasTexture(256, 256, (g, W, H) => {
          g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
          g.filter = 'blur(18px)'; g.fillStyle = '#fff'; g.fillRect(W * 0.16, H * 0.16, W * 0.68, H * 0.68);
        }, false), transparent: true, opacity: o.shadow != null ? o.shadow : 0.6, depthWrite: false, blending: THREE.CustomBlending,
        blendEquation: THREE.AddEquation, blendSrc: THREE.ZeroFactor, blendDst: THREE.OneMinusSrcColorFactor }));
      sh.position.set(w * 0.02, -h * 0.05, -0.05); grp.add(sh); grp.userData.shadow = sh;
    }
    return grp;
  }

  // ─────────────────────────────────────────────── postproducción
  const VS = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }';
  function makePost(renderer, W, H, opt) {
    const hf = { type: THREE.HalfFloatType, colorSpace: THREE.LinearSRGBColorSpace, depthBuffer: false };
    const depthTex = new THREE.DepthTexture(W, H); depthTex.type = THREE.FloatType;
    const rtScene = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, colorSpace: THREE.LinearSRGBColorSpace,
      samples: opt.msaa || 0, depthTexture: depthTex });
    const rtAcc = new THREE.WebGLRenderTarget(W, H, hf);
    const rtDof = new THREE.WebGLRenderTarget(W, H, hf);
    const accMat = new THREE.ShaderMaterial({ uniforms: { tex: { value: null }, w: { value: 1 } }, vertexShader: VS,
      fragmentShader: 'uniform sampler2D tex; uniform float w; varying vec2 vUv; void main(){ gl_FragColor = texture2D(tex, vUv) * w; }',
      depthTest: false, depthWrite: false, transparent: true, blending: THREE.NoBlending,
      blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor });
    const dofMat = new THREE.ShaderMaterial({
      uniforms: { tColor: { value: null }, tDepth: { value: depthTex }, near: { value: 0.1 }, far: { value: 200 }, focus: { value: 10 },
        aperture: { value: 0 }, maxBlur: { value: 18 }, texel: { value: new THREE.Vector2(1 / W, 1 / H) } },
      vertexShader: VS,
      fragmentShader: `
        uniform sampler2D tColor, tDepth; uniform float near, far, focus, aperture, maxBlur; uniform vec2 texel; varying vec2 vUv;
        float linZ(float d){ float z = d * 2.0 - 1.0; return 2.0 * near * far / (far + near - z * (far - near)); }
        float coc(float z){ return clamp(aperture * abs(z - focus) / max(z, 1e-3), 0.0, maxBlur); }
        void main(){
          float zc = linZ(texture2D(tDepth, vUv).r); float cc = coc(zc);
          vec4 acc = texture2D(tColor, vUv); float ws = 1.0;
          const int TAPS = 56; const float GA = 2.39996323;
          for (int i = 0; i < TAPS; i++) {
            float r = sqrt((float(i) + 0.5) / float(TAPS)) * maxBlur;
            float a = float(i) * GA; vec2 uv = vUv + vec2(cos(a), sin(a)) * r * texel;
            float zs = linZ(texture2D(tDepth, uv).r); float cs = coc(zs);
            if (zs > zc) cs = min(cs, cc * 2.0 + 0.5);   // el fondo no invade un primer plano nítido
            float w = smoothstep(r - 1.5, r + 1.5, cs);
            acc += texture2D(tColor, uv) * w; ws += w;
          }
          gl_FragColor = acc / ws;
        }`,
      depthTest: false, depthWrite: false });
    const gradeMat = new THREE.ShaderMaterial({
      uniforms: { tSrc: { value: null }, tonemap: { value: 1 }, exposure: { value: 1 }, vignette: { value: 0.38 }, grain: { value: 0.035 }, ca: { value: 0.0012 },
        contrast: { value: 1 }, saturation: { value: 1 }, lift: { value: 0 }, seed: { value: 0 }, res: { value: new THREE.Vector2(W, H) }, alphaMode: { value: opt.alpha ? 1 : 0 } },
      vertexShader: VS,
      fragmentShader: `
        uniform sampler2D tSrc; uniform float alphaMode; uniform float tonemap, exposure, vignette, grain, ca, contrast, saturation, lift, seed; uniform vec2 res; varying vec2 vUv;
        vec3 neutral(vec3 c){   // Khronos PBR Neutral: respeta el color de marca hasta las altas luces
          const float sc = 0.76; const float desat = 0.15;
          float x = min(c.r, min(c.g, c.b)); float off = x < 0.08 ? x - 6.25 * x * x : 0.04; c -= off;
          float peak = max(c.r, max(c.g, c.b)); if (peak < sc) return c;
          const float d = 1.0 - sc; float np = 1.0 - d * d / (peak + d - sc); c *= np / peak;
          float g = 1.0 - 1.0 / (desat * (peak - np) + 1.0); return mix(c, vec3(np), g);
        }
        vec3 toSRGB(vec3 c){ c = max(c, 0.0); return mix(c * 12.92, 1.055 * pow(c, vec3(1.0/2.4)) - 0.055, step(0.0031308, c)); }
        float hash(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
        void main(){
          vec2 d = vUv - 0.5; float r2 = dot(d * vec2(res.x / res.y, 1.0), d * vec2(res.x / res.y, 1.0));
          vec2 o = d * ca * (0.4 + 2.0 * r2);
          vec4 cc0 = texture2D(tSrc, vUv);
          float al = alphaMode > 0.5 ? clamp(cc0.a, 0.0, 1.0) : 1.0;
          vec3 c = vec3(texture2D(tSrc, vUv + o).r, cc0.g, texture2D(tSrc, vUv - o).b);
          if (alphaMode > 0.5) c = c / max(al, 1e-4);
          c = tonemap > 0.5 ? neutral(c * exposure) : clamp(c * exposure, 0.0, 1.0);   // none: colores de marca exactos
          float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
          c = mix(vec3(l), c, saturation);
          c = clamp((c - 0.5) * contrast + 0.5, 0.0, 1.0);
          c = c + lift * (1.0 - c);
          float vg = smoothstep(0.92, 0.18, length(d * vec2(1.0, 0.82)));
          c *= mix(1.0, vg, vignette);
          c = toSRGB(c);
          vec2 px = floor(gl_FragCoord.xy / 1.25);
          float n = hash(px + seed * 17.0) + hash(px * 1.7 + seed * 31.0) - 1.0;    // triangular: grano + dither anti-banding
          float lm = dot(c, vec3(0.299, 0.587, 0.114));
          c += n * grain * (0.35 + 0.65 * (1.0 - abs(lm * 2.0 - 1.0)));
          gl_FragColor = alphaMode > 0.5 ? vec4(clamp(c, 0.0, 1.0) * al, al) : vec4(c, 1.0);
        }`,
      depthTest: false, depthWrite: false });
    const quad = new A.FullScreenQuad(accMat);
    const bloom = new A.UnrealBloomPass(new THREE.Vector2(W, H), opt.bloom.strength, opt.bloom.radius, opt.bloom.threshold);
    return { rtScene, rtAcc, rtDof, accMat, dofMat, gradeMat, quad, bloom, depthTex };
  }

  // ─────────────────────────────────────────────── instancias
  function createInstance(name, def, root, props, ctx) {
    if (CK3D.instances.length >= MAX_INSTANCES) throw new Error('[CK3D] demasiadas escenas 3D (máx ' + MAX_INSTANCES + ')');
    const opt = deepMerge(deepMerge(DEFAULTS, def.options || {}), props.render || {});
    const rect = typeof opt.rect === 'function' ? opt.rect(ctx, props) : opt.fit === 'slot' && ctx.slot ? ctx.slot : { x: 0, y: 0, w: ctx.W, h: ctx.H };
    const W = Math.round(rect.w), H = Math.round(rect.h);
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H; canvas.className = 'ck3d-canvas';
    canvas.setAttribute('data-ck3d', name);
    Object.assign(canvas.style, { position: 'absolute', left: Math.round(rect.x) + 'px', top: Math.round(rect.y) + 'px',
      width: W + 'px', height: H + 'px', display: 'block', zIndex: String(ctx.z != null ? ctx.z : 300), pointerEvents: 'none' });
    root.appendChild(canvas);
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: !!opt.alpha, premultipliedAlpha: true, depth: true, stencil: false,
        preserveDrawingBuffer: true, powerPreference: 'high-performance' });
    } catch (e) {
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);   // sin contexto WebGL → el fallback 2D no hereda un lienzo vacío
      throw e;
    }
    renderer.setPixelRatio(1); renderer.setSize(W, H, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;   // el grado convierte a sRGB a mano (ShaderMaterial)
    renderer.toneMapping = THREE.NoToneMapping;
    renderer.shadowMap.enabled = !!opt.shadows; renderer.shadowMap.type = opt.shadowType === 'vsm' ? THREE.VSMShadowMap : THREE.PCFSoftShadowMap;
    renderer.shadowMap.autoUpdate = true;
    renderer.localClippingEnabled = true;
    const scene = new THREE.Scene();
    scene.background = opt.alpha ? null : new THREE.Color(opt.background);
    const camera = new THREE.PerspectiveCamera(opt.fov, W / H, opt.near, opt.far);
    const post = makePost(renderer, W, H, opt);
    const inst = { name, def, root, props, ctx, opt, canvas, renderer, scene, camera, post, W, H, t0: 0, t1: 0, dur: 0,
      k: null, ready: false, failed: false, lastT: null };
    return inst;
  }

  function makeK(inst, cuesLocal) {
    const { opt, ctx, W, H } = inst;
    const fps = ctx.fps || 30;
    const postState = {
      exposure: opt.grade.exposure, vignette: opt.grade.vignette, grain: opt.grade.grain, ca: opt.grade.ca,
      contrast: opt.grade.contrast, saturation: opt.grade.saturation, lift: opt.grade.lift,
      bloomStrength: opt.bloom.strength, bloomRadius: opt.bloom.radius, bloomThreshold: opt.bloom.threshold,
      dof: !!opt.dof.enabled, focus: opt.dof.focus, aperture: opt.dof.aperture, maxBlur: opt.dof.maxBlur,
    };
    const k = {
      THREE, A, CK, ctx, props: inst.props, fps, W, H, dur: inst.dur, cues: cuesLocal, post: postState, opt,
      tl: gsap.timeline({ paused: true }),
      rng: mulberry32, frameAt: (t) => Math.round(t * fps),
      kit: { svgShapes, textShapes, extrude, makeSweep, roundedPlane, studioEnv: (o) => studioEnv(inst.renderer, o), bokehParticles, imagePlane,
        radialTexture, canvasTexture, getFont, mulberry32 },
      /** px del lienzo → mundo (plano z=zPlane) con la cámara en su pose FINAL (fijada con k.framing). */
      px(x, y, zPlane) {
        const f = k._framing || { dist: 12, fov: inst.camera.fov, target: [0, 0, 0] };
        const d = f.dist - (zPlane || 0);
        const ppu = H / (2 * d * Math.tan(THREE.MathUtils.degToRad(f.fov) / 2));
        return new THREE.Vector3(f.target[0] + (x - W / 2) / ppu, f.target[1] + (H / 2 - y) / ppu, zPlane || 0);
      },
      /** px por unidad en el plano z=zPlane con la pose final */
      ppu(zPlane) {
        const f = k._framing || { dist: 12, fov: inst.camera.fov };
        return H / (2 * (f.dist - (zPlane || 0)) * Math.tan(THREE.MathUtils.degToRad(f.fov) / 2));
      },
      framing(dist, target, fov) { k._framing = { dist, target: target || [0, 0, 0], fov: fov || inst.camera.fov }; return k._framing; },
    };
    return k;
  }

  function poseAt(inst, t) {
    const k = inst.k;
    const tl = clamp(t, 0, inst.dur);
    k.tl.totalTime(Math.min(tl, k.tl.totalDuration()), true);
    if (inst.def.update) inst.def.update(tl, k.cues, k);
  }

  function renderInstance(inst, tLocal) {
    const { renderer, scene, camera, post, opt, k } = inst;
    const fps = k.fps;
    const N = Math.max(1, (opt.motionBlur && opt.motionBlur.samples) | 0);
    const sh = N > 1 ? clamp(opt.motionBlur.shutter == null ? 0.5 : opt.motionBlur.shutter, 0, 1) / fps : 0;
    // el subinstante central se pinta el ÚLTIMO: su profundidad alimenta el DOF y su estado el post
    const mid = Math.floor(N / 2), order = [];
    for (let i = 0; i < N; i++) if (i !== mid) order.push(i);
    order.push(mid);
    const t0 = performance.now();
    const q = post.quad;
    for (let j = 0; j < order.length; j++) {
      const i = order[j];
      const ts = N > 1 ? tLocal - sh / 2 + sh * (i + 0.5) / N : tLocal;
      poseAt(inst, ts);
      renderer.setRenderTarget(post.rtScene);
      if (opt.alpha) renderer.setClearColor(0x000000, 0); else renderer.setClearColor(scene.background || 0x000000, 1);
      renderer.clear(true, true, false);
      renderer.render(scene, camera);
      q.material = post.accMat;
      post.accMat.uniforms.tex.value = post.rtScene.texture;
      post.accMat.uniforms.w.value = 1 / N;
      post.accMat.blending = j === 0 ? THREE.NoBlending : THREE.CustomBlending;
      renderer.setRenderTarget(post.rtAcc);
      const ac = renderer.autoClear; renderer.autoClear = false; q.render(renderer); renderer.autoClear = ac;
    }
    const P = k.post;
    let src = post.rtAcc;
    if (P.dof && P.aperture > 0.01 && P.maxBlur >= 0.5) {
      const u = post.dofMat.uniforms;
      u.tColor.value = post.rtAcc.texture; u.near.value = camera.near; u.far.value = camera.far;
      u.focus.value = P.focus; u.aperture.value = P.aperture; u.maxBlur.value = P.maxBlur;
      q.material = post.dofMat; renderer.setRenderTarget(post.rtDof); q.render(renderer);
      src = post.rtDof;
    }
    if (P.bloomStrength > 0.001) {
      const b = post.bloom;
      b.strength = P.bloomStrength; b.radius = P.bloomRadius; b.threshold = P.bloomThreshold;
      b.render(renderer, null, src, 0, false);           // suma el bloom SOBRE src (UnrealBloomPass no necesita swap)
    }
    const g = post.gradeMat.uniforms;
    g.tSrc.value = src.texture; g.tonemap.value = opt.grade.tonemap === 'none' ? 0 : 1; g.exposure.value = P.exposure; g.vignette.value = P.vignette; g.grain.value = P.grain;
    g.ca.value = P.ca; g.contrast.value = P.contrast; g.saturation.value = P.saturation; g.lift.value = P.lift;
    g.seed.value = (k.frameAt(inst.t0 + tLocal) % 997) + 1;   // grano con semilla = nº de fotograma (determinista)
    q.material = post.gradeMat;
    renderer.setRenderTarget(null);
    q.render(renderer);
    const ms = performance.now() - t0;
    CK3D.stats.frames++; CK3D.stats.ms += ms; CK3D.stats.last = ms;
    inst.lastT = tLocal;
  }

  // ─────────────────────────────────────────────── bucle de seek (sin rAF, sin relojes)
  CK3D.renderAll = function (t, waitUntil) {
    const T = Number(t) || 0;
    const pend = [];
    for (const inst of CK3D.instances) {
      if (!inst.ready || inst.failed) continue;
      const fr = 0.5 / (inst.k.fps || 30);
      if (T < inst.t0 - fr || T >= inst.t1 + fr) continue;
      const tl = T - inst.t0;
      const go = () => {
        try { renderInstance(inst, tl); }
        catch (e) { inst.failed = true; CK3D.errors.push({ scene: inst.name, error: String(e && e.stack || e) }); console.error('[CK3D] render', inst.name, e); }
      };
      // recursos por instante (p. ej. el fotograma de un vídeo): si no están listos, se pinta cuando lo estén y HF
      // espera esa promesa antes de capturar (hf-seek waitUntil) → determinista sin precargar todo
      let p = null;
      try { p = inst.def.prepare ? inst.def.prepare(tl, inst.k) : null; } catch (e) { p = null; }
      if (p && typeof p.then === 'function') pend.push(p.then(go, go));
      else go();
    }
    if (!pend.length) return null;
    const all = Promise.all(pend);
    if (typeof waitUntil === 'function') { try { waitUntil(all); } catch (e) { /* fuera del despacho síncrono */ } }
    return all;
  };
  CK3D.renderAt = function (i, tLocal) { const inst = CK3D.instances[i]; if (inst && inst.ready) renderInstance(inst, tLocal); };
  if (!global.__ck3dSeekBound) {
    global.__ck3dSeekBound = true;
    global.addEventListener('hf-seek', (e) => CK3D.renderAll(e && e.detail ? e.detail.time : 0, e && e.detail ? e.detail.waitUntil : null));
  }
  function hookPreviewSeek() {      // vista previa / QA sin HyperFrames (boxes.js · window.__ckSeek)
    const orig = global.__ckSeek;
    if (typeof orig !== 'function' || orig.__ck3d) return;
    const wrapped = function (t) { const r = orig.apply(this, arguments); const p = CK3D.renderAll(t); return p ? Promise.all([r, p]).then(() => t) : r; };
    wrapped.__ck3d = true;
    global.__ckSeek = wrapped;
  }

  // ─────────────────────────────────────────────── registro de escenas
  CK3D.scene = function (name, def) {
    if (!def || typeof def.setup !== 'function') throw new Error('CK3D.scene: def.setup obligatorio (' + name + ')');
    CK3D.scenes[name] = def;
    CK.register(name, {
      kind: 'graphic', engine: 'three',
      mount(root, props, ctx) {
        hookPreviewSeek();
        let inst = null, fb = null;
        const fallback = (err) => {
          CK3D.errors.push({ scene: name, item: ctx.item && ctx.item.id, error: String(err && err.stack || err) });
          console.error('[CK3D] ' + name + ' → fallback ' + (def.fallback || '(ninguno)'), err);
          if (inst) { inst.failed = true; if (inst.canvas && inst.canvas.parentNode) inst.canvas.parentNode.removeChild(inst.canvas); }
          const fname = typeof def.fallback === 'function' ? def.fallback(props, ctx) : def.fallback;
          const fdef = fname && CK.get(fname);
          if (!fdef) throw err;
          root.setAttribute('data-ck3d-fallback', fname);
          return fdef.mount(root, props, ctx);
        };
        try { inst = createInstance(name, def, root, props, ctx); CK3D.instances.push(inst); }
        catch (e) { fb = fallback(e); return fb; }
        return {
          animate(tl, t0, t1, cues) {
            inst.t0 = t0; inst.t1 = t1; inst.dur = Math.max(1 / (ctx.fps || 30), t1 - t0);
            const cl = {};
            for (const kk in cues || {}) if (typeof cues[kk] === 'number') cl[kk] = cues[kk] - t0;
            try {
              inst.k = makeK(inst, cl);
              def.setup(inst.scene, inst.camera, inst.renderer, ctx, props, inst.k);
              if (def.animateMain) def.animateMain(tl, t0, t1, cues, inst.k);   // tweens DOM opcionales en la timeline principal
              inst.ready = true;
              inst.renderer.compile(inst.scene, inst.camera);
              renderInstance(inst, 0);                                          // calienta shaders + detecta fallos ya
              const now = Number(global.__hfThreeTime);
              if (isFinite(now)) CK3D.renderAll(now);
              if (ctx.event) ctx.event('enter', t0);
            } catch (e) {
              inst.ready = false;
              const f = fallback(e);
              if (f && typeof f.animate === 'function') f.animate(tl, t0, t1, cues);
            }
          },
        };
      },
    });
    return def;
  };

  CK3D.util = { clamp, mulberry32, svgShapes, textShapes, extrude, makeSweep, roundedPlane, radialTexture, canvasTexture, bokehParticles, imagePlane };
  global.CK3D = CK3D;
  global.__ck3dStats = CK3D.stats;
})(typeof window !== 'undefined' ? window : globalThis);
