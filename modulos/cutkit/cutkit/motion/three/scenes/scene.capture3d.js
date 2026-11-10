// scene.capture3d — capturas y VÍDEOS reales de un producto como pantallas en el espacio (lanzamiento de producto).
// Sustituye a media.capture_plane / media.slot cambiando solo el `component` (mismas props: fit, kb, kb_dir, sheen,
// focus {text_box, marker}, media_start, enter, exit…; cues: focus, sheen). Fallback: media.slot (vídeo) o
// media.capture_plane (imagen).
//   - Plano con esquinas redondeadas y canto fino de aluminio (como un dispositivo o una hoja); la imagen/vídeo es
//     EMISIVA (colores exactos, texto legible) con un cristal que refleja el estudio.
//   - Lienzo TRANSPARENTE: el panel real del layout (con su grano) se ve detrás; sombra blanda sobre él (VSM).
//   - Entrada: cámara girada 8–14° en Y y 4–6° en X que, con un dolly, queda casi frontal (≤ 1,5°) en 0,55 s; DOF
//     suave SOLO durante la entrada; motion blur real; deriva mínima luego (vida) y el `kb` como dolly lento.
//   - Un barrido especular (cue `sheen`); paralaje leve de una luz de fondo.
//   - focus.text_box: marcador oro (multiply) sobre la palabra real en su cue y un empuje de cámara HACIA ella
//     (la palabra queda quieta en pantalla y todo se acerca a su alrededor).
//   - Encaje: split → panel 0–768 (lienzo hasta la junta); broll_full → banda 288–1240; ≥ 900 px de ancho frontal.
//   - VÍDEO: fotogramas extraídos por html.py (props._vframes); cada seek carga el suyo (CK3D prepare + waitUntil).
(function () {
  if (!window.CK3D) return;
  const NAME = 'scene.capture3d';
  const FPS = 30, f = (n) => n / FPS;

  function hash(s) { let h = 2166136261; for (const ch of String(s)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }

  window.CK3D.scene(NAME, {
    fallback: (props, ctx) => { const m = (ctx.media || [])[0]; const v = m && ((m.ckInfo && m.ckInfo.kind) ? m.ckInfo.kind === 'video' : m.tagName === 'VIDEO'); return v ? 'media.slot' : 'media.capture_plane'; },
    options: {
      fov: 30, msaa: 4, alpha: true, shadows: true, shadowType: 'vsm',
      motionBlur: { samples: 6, shutter: 0.5 },
      dof: { enabled: true, focus: 15, aperture: 0, maxBlur: 8 },
      bloom: { strength: 0 },
      grade: { exposure: 1, vignette: 0, grain: 0, ca: 0, contrast: 1, saturation: 1, lift: 0, tonemap: 'none' },
      rect: (ctx) => {
        const L = ctx.layout || {};
        if (/split/.test(L.name || '')) return { x: 0, y: 0, w: ctx.W, h: Math.round(L.seamY || 840) };   // hasta la junta
        return { x: 0, y: 0, w: ctx.W, h: ctx.H };
      },
    },

    setup(scene, camera, renderer, ctx, props, k) {
      const { THREE, kit, tl, dur } = k;
      const E = (window.CK && window.CK.ease) || {};
      const EASE = { enter: E.enter || 'power3.out', move: E.move || 'power2.inOut' };
      const W = k.W, H = k.H;                                      // lienzo (rect)
      const FOV = 30, D = H / (2 * 100 * Math.tan(THREE.MathUtils.degToRad(FOV / 2)));
      k.framing(D, [0, 0, 0], FOV);
      camera.fov = FOV; camera.near = 0.5; camera.far = 200; camera.updateProjectionMatrix();
      const U = 0.01, wx = (x) => (x - W / 2) * U, wy = (y) => (H / 2 - y) * U;
      const L = ctx.layout || {};
      const split = /split/.test(L.name || '');
      const panel = String((L.props && L.props.panel_bg) || 'ink');
      const darkPanel = panel === 'ink' || panel === 'navy';

      // ── media: imagen (el <img> del item, ya decodificado) o vídeo (fotogramas extraídos)
      const media = (ctx.media || [])[0] || null;
      const VF = props._vframes || null;
      const isVid = !!(media && ((media.ckInfo && media.ckInfo.kind) ? media.ckInfo.kind === 'video' : media.tagName === 'VIDEO'));
      if (isVid && !VF) throw new Error('scene.capture3d: vídeo sin fotogramas (props._vframes)');
      if (!isVid && !(media && media.naturalWidth)) throw new Error('scene.capture3d: sin imagen');
      const nw = isVid ? VF.w : media.naturalWidth, nh = isVid ? VF.h : media.naturalHeight;

      // ── encaje: split → panel 0–768; broll_full → banda 288–1240. ≥ 900 px de ancho frontal si la proporción lo deja
      const zone = split ? { y0: 0, y1: (ctx.slot && ctx.slot.h) || 768 } : { y0: 288, y1: 1240 };
      const zoneH = zone.y1 - zone.y0;
      // la pantalla ENTERA (con bisel) cabe en la zona con el empuje máximo (kb + focus) y 10 px de aire
      const BZ = 4;
      const kbMax = 1 + Math.max(0, Math.min(0.08, props.kb == null ? 0.03 : props.kb));
      const pushMax = kbMax * (props.focus && props.focus.text_box ? 1 / 0.93 : 1);
      // `y` (fracción de la zona, como en media.capture_plane): centro de la pantalla; por defecto, el de la zona
      const cy = typeof props.y === 'number' && isFinite(props.y) ? zone.y0 + Math.max(0.2, Math.min(0.8, props.y)) * zoneH : zone.y0 + zoneH / 2;
      const hMax = Math.floor((Math.min(cy - zone.y0, zone.y1 - cy) - 10) * 2 / pushMax) - 2 * BZ;
      const wMax = Math.floor((Math.min(1015 - 540, 540 - 65) - 6) * 2 / pushMax) - 2 * BZ;
      let sw = Math.min(props.width || 932, wMax), sh = Math.round(sw * nh / nw);   // `width`: no ampliar de más
      if (sh > hMax) { sh = hMax; sw = Math.round(sh * nw / nh); }
      const P = new THREE.Vector3(0, wy(cy), 0);                  // centro de la pantalla (pivote de la cámara)

      // ── luz, entorno, sombra, luz de fondo (paralaje)
      scene.environment = kit.studioEnv({ blur: 0.04, ambient: '#141016', panels: [
        { pos: [0, 10, 4], size: [14, 4], intensity: 3.2 }, { pos: [-10, 3, 4], size: [2, 12], intensity: 4.2 }, { pos: [10, 2, 3], size: [2, 12], intensity: 2.6 },
      ] });
      scene.environmentIntensity = 0.6;
      scene.add(new THREE.HemisphereLight(0xffffff, new THREE.Color('#e9e2ee'), 1.2));
      const key = new THREE.DirectionalLight(0xffffff, 3.2); key.position.set(-5, P.y + 7, 9); key.target.position.copy(P); scene.add(key, key.target);
      const sl = new THREE.DirectionalLight(0xffffff, 0.0001);     // solo sombra: casi frontal, algo cenital
      sl.position.set(-0.6, P.y + 2.6, 16); sl.target.position.copy(P); sl.castShadow = true;
      sl.shadow.mapSize.set(1024, 1024); sl.shadow.radius = 18; sl.shadow.blurSamples = 16; sl.shadow.bias = -0.0005;
      Object.assign(sl.shadow.camera, { left: -7, right: 7, top: 6, bottom: -6, near: 4, far: 40 });
      scene.add(sl, sl.target);
      const catcher = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.ShadowMaterial({ color: new THREE.Color(darkPanel ? '#000000' : '#3a1028'), opacity: darkPanel ? 0.6 : 0.38 }));
      catcher.position.set(0, P.y, -0.55); catcher.receiveShadow = true; scene.add(catcher);
      const glowTex = kit.radialTexture([[0, 'rgba(255,255,255,1)'], [0.4, 'rgba(255,255,255,0.35)'], [1, 'rgba(255,255,255,0)']], 256);
      const glow = new THREE.Mesh(new THREE.PlaneGeometry(sw * U * 1.5, sw * U * 1.5), new THREE.MeshBasicMaterial({ map: glowTex, transparent: true, depthWrite: false,
        opacity: darkPanel ? 0.06 : 0.2 }));                         // mezcla normal: alfa premultiplicado correcto
      glow.position.set(P.x, P.y + 0.6, -2.4); scene.add(glow);

      // ── la pantalla: canto de aluminio + cara emisiva con cristal
      const tex = isVid ? new THREE.Texture() : new THREE.Texture(media);
      tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.generateMipmaps = true;
      tex.minFilter = THREE.LinearMipmapLinearFilter; tex.magFilter = THREE.LinearFilter;
      if (!isVid) tex.needsUpdate = true;
      const R = Math.round((props.radius != null ? props.radius : 22));
      const face = new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0xffffff, emissiveMap: tex, roughness: 0.35, metalness: 0, envMapIntensity: 0.08 });
      const sweep = kit.makeSweep({ dir: [1, -0.55], width: 0.5, intensity: 0.12, color: '#ffffff' });   // ≤ 0,15: un brillo, no una raya
      sweep.apply(face);
      const screen = new THREE.Group(); scene.add(screen);
      // canto FINO y oscuro (4 px, mate): se nota la hoja, no una maqueta de tableta; sin barrido en el canto
      const edge = new THREE.MeshStandardMaterial({ color: new THREE.Color(darkPanel ? '#18171a' : '#2a292c'), metalness: 0.1, roughness: 0.6, envMapIntensity: 0.25 });
      const body = new THREE.Mesh(new k.A.RoundedBoxGeometry(sw * U + 2 * BZ * U, sh * U + 2 * BZ * U, 0.05, 4, (R + BZ) * U), edge);
      body.castShadow = true; screen.add(body);
      const faceMesh = new THREE.Mesh(kit.roundedPlane(sw * U, sh * U, Math.max(4, R - 6) * U), face);
      faceMesh.position.z = 0.0255; screen.add(faceMesh);
      screen.position.copy(P);
      // marcador oro (multiply) sobre la palabra real
      let mark = null, Pw = P.clone();
      const fb = props.focus && props.focus.text_box;
      if (fb && fb.length === 4) {
        const [bx, by, bw, bh] = fb;
        // «underline» (por defecto; siempre en vídeo): barra oro de ~6 px bajo la base, mezcla normal, nunca encima del
        // texto (el multiply salía opaco sobre vídeo). «gold» explícito sobre imagen: el rotulador multiply de antes.
        const ul = isVid || (props.focus.marker || 'underline') !== 'gold';
        const bhU = ul ? 6 * U : bh * sh * U;
        const g = new THREE.PlaneGeometry(bw * sw * U, bhU); g.translate(bw * sw * U / 2, 0, 0);   // crece de izquierda a derecha
        mark = new THREE.Mesh(g, new THREE.MeshBasicMaterial(ul
          ? { color: new THREE.Color('#FECA1A'), depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }
          : { color: new THREE.Color('#FECA1A'), blending: THREE.MultiplyBlending,
              premultipliedAlpha: true, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }));
        mark.position.set((bx - 0.5) * sw * U, ul ? (0.5 - by - bh) * sh * U - 7 * U : (0.5 - by - bh / 2) * sh * U, 0.0275);
        mark.scale.x = 0.0001; mark.visible = false;
        screen.add(mark);
        Pw = new THREE.Vector3(P.x + (bx + bw / 2 - 0.5) * sw * U, P.y + (0.5 - by - bh / 2) * sh * U, 0.025);
      }

      // ── estado animado
      const side = (hash(ctx.item && ctx.item.id) % 2) ? 1 : -1;     // variedad: entra desde la izquierda o la derecha
      const yaw0 = side * (props.yaw != null ? props.yaw : 11), pitch0 = 5;
      const S = { yaw: yaw0, pitch: pitch0, dolly: 1.22, kb: 1, push: 1, pw: 0, ap: 70, sweep: 99, mark: 0 };
      k.state = S;
      const tIn = 0.55;
      tl.fromTo(S, { yaw: yaw0, pitch: pitch0, dolly: 1.22 }, { yaw: side * 1.2, pitch: 0.8, dolly: 1.0, duration: tIn, ease: 'power3.out', immediateRender: false }, 0);
      tl.fromTo(S, { ap: 70 }, { ap: 0, duration: tIn, ease: 'power2.out', immediateRender: false }, 0);
      if (dur - tIn > 0.2) tl.fromTo(S, { yaw: side * 1.2, pitch: 0.8 }, { yaw: side * 0.3, pitch: 0.2, duration: dur - tIn, ease: 'sine.inOut', immediateRender: false }, tIn);
      // kb del 2D como dolly lento (in/out)
      const kbv = Math.max(0, Math.min(0.08, props.kb == null ? 0.03 : props.kb));
      if (kbv > 0 && dur - tIn > 0.3) {
        const a = props.kb_dir === 'out' ? 1 + kbv : 1, b = props.kb_dir === 'out' ? 1 : 1 + kbv;
        tl.fromTo(S, { kb: a }, { kb: b, duration: dur - tIn, ease: EASE.move, immediateRender: false }, tIn);
      }
      // barrido especular, una vez
      const cueS = k.cues.sheen != null ? k.cues.sheen : Math.min(dur - 0.4, tIn + 0.1);
      if (props.sheen !== false && cueS + 0.5 < dur) {
        const ext = (sw * 0.0086 + sh * 0.0051) * U * 100 * 0.5 + 0.5;  // ≈ media diagonal proyectada en la dirección del barrido
        const c0 = P.x * 0.876 + P.y * -0.482;
        tl.fromTo(S, { sweep: c0 - ext }, { sweep: c0 + ext, duration: f(18), ease: EASE.move, immediateRender: false }, Math.max(f(6), cueS));
        if (k.ctx.event) k.ctx.event('sheen', k.ctx.item.t0 + Math.max(f(6), cueS));
        tl.set(S, { sweep: 99 }, Math.max(f(6), cueS) + f(18));
      }
      // marcador + empuje hacia la palabra
      if (mark) {
        const tF = Math.max(tIn - f(4), k.cues.focus != null ? k.cues.focus : tIn + 0.2);
        tl.set(S, { mark: 1e-4 }, tF);
        tl.fromTo(S, { mark: 1e-4 }, { mark: 1, duration: f(7), ease: EASE.enter, immediateRender: false }, tF);
        tl.fromTo(S, { pw: 0, push: 1 }, { pw: 1, push: 0.93, duration: f(16), ease: EASE.move, immediateRender: false }, tF);
        if (k.ctx.event) { k.ctx.event('focus', k.ctx.item.t0 + tF); k.ctx.event('highlight', k.ctx.item.t0 + tF); }
      }
      if (k.ctx.event) k.ctx.event('enter', k.ctx.item.t0);

      // ── vídeo: carga por índice (caché pequeña)
      const vf = isVid ? { cache: new Map(), cur: -1, pending: new Map() } : null;
      const urlOf = (i) => VF.dir + '/f_' + String(i + 1).padStart(4, '0') + '.jpg';
      const load = (i) => {
        if (vf.cache.has(i)) return Promise.resolve(vf.cache.get(i));
        if (vf.pending.has(i)) return vf.pending.get(i);
        const im = new Image(); im.decoding = 'sync'; im.src = urlOf(i);
        const p = (im.decode ? im.decode() : new Promise((r) => { im.onload = r; })).catch(() => {}).then(() => {
          vf.pending.delete(i); vf.cache.set(i, im);
          if (vf.cache.size > 8) vf.cache.delete(vf.cache.keys().next().value);
          return im;
        });
        vf.pending.set(i, p);
        return p;
      };
      const apply = (i, im) => { if (vf.cur !== i && im) { tex.image = im; tex.needsUpdate = true; vf.cur = i; } };
      k.objs = { camera, screen, mark, glow, sweep, P, Pw, D, vf, load, apply, VF, isVid };
      if (isVid) load(0).then((im) => apply(0, im));
    },

    prepare(tLocal, k) {
      const o = k.objs;
      if (!o || !o.isVid) return null;
      const i = Math.max(0, Math.min(o.VF.count - 1, Math.round(tLocal * o.VF.fps)));
      if (o.vf.cur === i) return null;
      if (o.vf.cache.has(i)) { o.apply(i, o.vf.cache.get(i)); return null; }
      if (i + 1 < o.VF.count) o.load(i + 1);                       // precarga del siguiente (solo acelera; no cambia nada)
      return o.load(i).then((im) => o.apply(i, im));
    },

    update(t, cues, k) {
      const o = k.objs, S = k.state, THREE = k.THREE;
      // cámara como rig que rota alrededor del pivote (el pivote queda fijo en pantalla) + dolly + empuje a la palabra
      const piv = o.P.clone().lerp(o.Pw, S.pw);
      const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(THREE.MathUtils.degToRad(-S.pitch), THREE.MathUtils.degToRad(S.yaw), 0, 'YXZ'));
      const base = new THREE.Vector3(0, 0, o.D).sub(piv);          // cámara frontal → pivote
      const off = base.applyQuaternion(q).multiplyScalar(S.dolly * S.push / S.kb);
      o.camera.position.copy(piv).add(off);
      o.camera.quaternion.copy(q);
      o.camera.updateMatrixWorld();
      // DOF solo en la entrada: foco en la pantalla
      k.post.focus = o.camera.position.distanceTo(o.P);
      k.post.aperture = S.ap;
      k.post.dof = S.ap > 0.5;
      o.sweep.uniforms.uSweepPos.value = S.sweep;
      if (o.mark) { o.mark.visible = S.mark > 0.001; o.mark.scale.x = Math.max(1e-4, S.mark); }
    },
  });
})();
