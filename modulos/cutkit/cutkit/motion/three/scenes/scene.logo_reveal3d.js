// scene.logo_reveal3d — revelación de logo + nombre con acabado de estudio (capa 3D OPCIONAL, motor ck3d.js).
// Sustituye a logo.reveal cambiando SOLO el `component` de la decisión: mismas props ({asset, name, by, sweep…}) y
// cues ({name}). Si WebGL o el montaje fallan, delega en logo.reveal (2D).
//   · logo SVG verificado extruido con bisel (esmalte con clearcoat + cantos de metal teñido), autosombra suave;
//   · dolly-in con arco y alabeo leve, foco que se ajusta (rack focus) en los primeros ~0,4 s;
//   · barrido especular (RectAreaLight en diagonal) + rotación del entorno de estudio (reflejos que se deslizan);
//   · polvo en suspensión con bokeh, halo de color de marca detrás, bloom, grano, viñeta, aberración sutil;
//   · «name» en Montserrat 900 extruido que sube a través de una máscara (plano de recorte) en su cue;
//     «by» en Montserrat 600 plano debajo. Motion blur real (8 subfotogramas, obturador 180°).
// Composición (pose final, lienzo 1080×1920): logo centrado en y≈555 (alto `size`, 470 px), nombre con línea base en
// y=1000, autoría en y≈1070 → libre la banda de subtítulos (y≈1180).
(function () {
  if (!window.CK3D) return;
  const NAME = 'scene.logo_reveal3d';

  function brandColor(props, svg) {
    if (props.color && /^#[0-9a-f]{6}$/i.test(props.color)) return props.color;
    const m = /fill\s*[:=]\s*["']?(#[0-9a-fA-F]{6})/.exec(svg || '');
    return m ? m[1] : '#E551BA';
  }
  function logoSvg(ctx) {
    const A = window.__CK3D_ASSETS || { svg: {} };
    const ms = (ctx.item && ctx.item.media) || [];
    for (const m of ms) {
      const src = String(m.src || '').replace(/^\.?\//, '');
      if (A.svg[src]) return A.svg[src];
    }
    throw new Error('scene.logo_reveal3d: falta el SVG del logo en ck3d/assets.js (media del item)');
  }

  window.CK3D.scene(NAME, {
    fallback: 'logo.reveal',
    options: {
      fov: 24, msaa: 4, shadows: true,
      motionBlur: { samples: 8, shutter: 0.5 },
      dof: { enabled: true, focus: 12, aperture: 0, maxBlur: 16 },
      bloom: { strength: 0.4, radius: 0.5, threshold: 1.5 },
      grade: { exposure: 1.0, vignette: 0.32, grain: 0.03, ca: 0.0011, contrast: 1.03, saturation: 1.02, lift: 0.012 },
      background: '#0B0A0E',
    },

    setup(scene, camera, renderer, ctx, props, k) {
      const { THREE, kit, tl, dur } = k;
      const E = (ctx.tokens && ctx.tokens.motion && ctx.tokens.motion.ease) || {};
      const EASE = { enter: E.enter || 'power3.out', move: E.move || 'power2.inOut', exit: E.exit || 'power2.in' };
      const svg = logoSvg(ctx);
      const color = new THREE.Color(brandColor(props, svg));
      const D = 12, FOV = 24;
      k.framing(D, [0, 0, 0], FOV);
      camera.fov = FOV; camera.updateProjectionMatrix();

      // ── entorno de estudio + luces
      scene.environment = kit.studioEnv({ blur: 0.02, ambient: '#100c13', panels: [
        { pos: [0, 9, 4], size: [14, 3], intensity: 5 },            // cenital ancho
        { pos: [-9, 2, 5], size: [1.6, 12], intensity: 8 },         // tira izquierda (canto vivo)
        { pos: [9, 1, 3], size: [1.2, 12], intensity: 4.5 },        // tira derecha
        { pos: [2, -2, 10], size: [9, 5], intensity: 1.4 },         // relleno frontal suave
        { pos: [0, -8, 3], size: [14, 4], intensity: 1.1, color: '#ffe3f4' },  // rebote de suelo (cantos inferiores)
        { pos: [0, 3, -9], size: [10, 6], intensity: 1.2, color: '#ffd9f0' },  // contraluz
      ] });
      scene.environmentIntensity = 1.0;
      const key = new THREE.DirectionalLight(0xffffff, 2.0);
      key.position.set(2.5, 4.5, 6); key.castShadow = true;
      key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 5; key.shadow.bias = -0.0004; key.shadow.normalBias = 0.012;
      Object.assign(key.shadow.camera, { left: -2.2, right: 2.2, top: 2.6, bottom: -2.6, near: 1, far: 20 });
      scene.add(key);
      const rim = new THREE.DirectionalLight(new THREE.Color('#ffd6f1'), 1.6);
      rim.position.set(-3, 3.5, -5); scene.add(rim);
      // barrido especular: banda diagonal (arriba-izquierda → abajo-derecha) sobre logo y nombre, por shader
      const sweepOn = props.sweep !== false;
      const sweep = kit.makeSweep({ dir: [1, -0.5], width: 0.13, intensity: sweepOn ? 1.55 : 0, color: '#fff2fa' });

      // ── fondo: tinta de estudio con un velo de color de marca + halo detrás del logo
      const bgTex = kit.radialTexture([[0, '#2a2030'], [0.35, '#17121b'], [0.75, '#0e0b10'], [1, '#08070a']], 512);
      const back = new THREE.Mesh(new THREE.PlaneGeometry(30, 38), new THREE.MeshBasicMaterial({ map: bgTex }));
      back.position.set(0, 1.4, -9); scene.add(back);
      const haloTex = kit.radialTexture([[0, 'rgba(255,255,255,1)'], [0.2, 'rgba(255,255,255,0.55)'], [0.5, 'rgba(255,255,255,0.16)'], [0.8, 'rgba(255,255,255,0.03)'], [1, 'rgba(255,255,255,0)']], 512);
      const haloCol = color.clone().lerp(new THREE.Color('#ffffff'), 0.2).multiplyScalar(0.085);
      const halo = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), new THREE.MeshBasicMaterial({ map: haloTex, color: haloCol,
        transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0 }));
      scene.add(halo);

      // ── logo extruido
      const sizePx = props.size || 470;
      const logoC = k.px(540, 555);
      const logoH = sizePx / k.ppu(0);
      const lg = kit.svgShapes(svg, { height: logoH, simplify: 1.4, curveSegments: 4 });
      const geo = kit.extrude(lg.shapes, { depth: logoH * 0.1, bevelThickness: logoH * 0.012, bevelSize: logoH * 0.0085,
        bevelSegments: 4, curveSegments: 4, crease: Math.PI / 4.5 });
      const mat = props.material || 'enamel';
      let face, side;
      if (mat === 'metal') {
        face = new THREE.MeshPhysicalMaterial({ color: color.clone().lerp(new THREE.Color('#ffffff'), 0.15), metalness: 1, roughness: 0.16, clearcoat: 0.4 });
        side = face;
      } else if (mat === 'glass') {
        face = new THREE.MeshPhysicalMaterial({ color, metalness: 0, roughness: 0.06, transmission: 0.85, thickness: logoH * 0.1, ior: 1.5,
          attenuationColor: color, attenuationDistance: logoH * 0.25, clearcoat: 1, clearcoatRoughness: 0.02 });
        side = face;
      } else {
        face = new THREE.MeshPhysicalMaterial({ color, metalness: 0.0, roughness: 0.3, clearcoat: 1.0, clearcoatRoughness: 0.035,
          emissive: color, emissiveIntensity: 0.06, sheen: 0.4, sheenColor: new THREE.Color('#ffffff'), sheenRoughness: 0.4 });
        side = new THREE.MeshPhysicalMaterial({ color: color.clone().lerp(new THREE.Color('#ffffff'), 0.18), metalness: 0.55, roughness: 0.24,
          clearcoat: 0.8, clearcoatRoughness: 0.06, emissive: color, emissiveIntensity: 0.04 });
      }
      if (mat !== 'glass') { sweep.apply(face); if (side !== face) sweep.apply(side); }
      const logo = new THREE.Mesh(geo, [face, side]);
      logo.castShadow = true; logo.receiveShadow = true;
      const logoPivot = new THREE.Group();
      logoPivot.position.copy(logoC); logoPivot.add(logo); scene.add(logoPivot);
      halo.position.set(logoC.x, logoC.y, -1.6);

      // ── nombre (Montserrat 900 extruido) y autoría (Montserrat 600 plano), con máscara = plano de recorte
      const ppu = k.ppu(0);
      const nameStr = String(props.name || '').trim();
      const byStr = String(props.by || '').trim();
      const letters = [], byLetters = [];
      const baseY = k.px(540, 1000).y;
      const clipName = new THREE.Plane(new THREE.Vector3(0, 1, 0), -(baseY - 0.006));
      let capName = 0;
      if (nameStr) {
        const capPx = Math.min(165, 820 / Math.max(1, nameStr.length) * 1.35);
        const ts = kit.textShapes(nameStr, { family: 'Montserrat', weight: 900, size: capPx / 0.7 / ppu, tracking: -0.01 });
        capName = ts.capHeight;
        const nameFace = new THREE.MeshPhysicalMaterial({ color: new THREE.Color('#ECE8EF'), metalness: 0, roughness: 0.36, clearcoat: 0.7,
          clearcoatRoughness: 0.12, clippingPlanes: [clipName], side: THREE.DoubleSide });
        const nameSide = new THREE.MeshPhysicalMaterial({ color: new THREE.Color('#d9d3de'), metalness: 0.85, roughness: 0.22,
          clippingPlanes: [clipName], side: THREE.DoubleSide });
        sweep.apply(nameFace); sweep.apply(nameSide);
        ts.glyphs.forEach((g) => {
          if (!g.shapes.length) return;
          const gg = kit.extrude(g.shapes, { depth: capName * 0.22, bevelThickness: capName * 0.02, bevelSize: capName * 0.014, bevelSegments: 3, curveSegments: 10 });
          gg.computeBoundingBox();
          const cx = (gg.boundingBox.min.x + gg.boundingBox.max.x) / 2;
          gg.translate(-cx, 0, 0);
          const m = new THREE.Mesh(gg, [nameFace, nameSide]);
          m.castShadow = false; m.receiveShadow = true;
          const holder = new THREE.Group();
          holder.position.set(cx - ts.width / 2, baseY, 0);
          holder.add(m); scene.add(holder);
          letters.push({ holder, mesh: m, st: { y: -capName * 1.25, rx: 0.55 } });
        });
      }
      const byBase = k.px(540, 1072).y;
      const clipBy = new THREE.Plane(new THREE.Vector3(0, 1, 0), -(byBase - 0.004));
      if (byStr) {
        const ts2 = kit.textShapes(byStr, { family: 'Montserrat', weight: 600, size: 46 / ppu, tracking: 0.02 });
        const byMat = new THREE.MeshBasicMaterial({ color: new THREE.Color('#BFB8C8'), clippingPlanes: [clipBy], transparent: true, opacity: 1 });
        ts2.glyphs.forEach((g) => {
          if (!g.shapes.length) return;
          const gg = new THREE.ShapeGeometry(g.shapes, 8);
          const m = new THREE.Mesh(gg, byMat);
          const holder = new THREE.Group();
          holder.position.set(-ts2.width / 2, byBase, 0.02);
          holder.add(m); scene.add(holder);
          byLetters.push({ holder, st: { y: -ts2.capHeight * 1.4 } });
        });
      }

      // ── polvo con bokeh
      const dust = props.dust === false ? null : kit.bokehParticles({ count: 170, seed: 1729,
        box: [-5.5, 5.5, -7.5, 7.5, -9, 7], size: 3.4, color: color.clone().lerp(new THREE.Color('#ffffff'), 0.6), intensity: 5,
        drift: [0.04, 0.16, 0.02] });
      if (dust) scene.add(dust.points);

      // ── estado animado (timeline PRIVADA, segundos locales; nunca dos tweens sobre la misma propiedad)
      const S = { cam: 0, roll: 0.035, rotY: -0.62, rotX: 0.2, lz: -0.7, ls: 0.86, focusMix: 0, halo: 0, sweepX: -1.65, env: -0.55 };
      k.state = S;
      const cName = Math.max(0.12, Math.min(dur - 0.55, k.cues.name != null ? k.cues.name : 0.25));
      // cámara: el tween dura más que el item → sigue acercándose al cortar (nunca queda congelada)
      tl.fromTo(S, { cam: 0 }, { cam: 1, duration: Math.max(1.6, dur * 1.25), ease: 'power3.out', immediateRender: false }, 0);
      tl.fromTo(S, { roll: 0.035 }, { roll: 0, duration: 0.9, ease: EASE.move, immediateRender: false }, 0);
      tl.fromTo(S, { rotY: -0.62, rotX: 0.2 }, { rotY: -0.07, rotX: 0.03, duration: Math.max(1.3, dur), ease: 'power3.out', immediateRender: false }, 0);
      tl.fromTo(S, { lz: -0.7, ls: 0.86 }, { lz: 0, ls: 1, duration: 0.7, ease: EASE.enter, immediateRender: false }, 0);
      tl.fromTo(S, { focusMix: 0 }, { focusMix: 1, duration: 0.42, ease: 'power2.inOut', immediateRender: false }, 0.02);
      tl.fromTo(S, { halo: 0 }, { halo: 1, duration: 0.55, ease: EASE.enter, immediateRender: false }, 0.05);
      // recorre SOLO el rango de logo + nombre (≈ −1,3…0,9 en dot(xy, dir)) en ~0,65 s: se lee como un destello que pasa
      tl.fromTo(S, { sweepX: -1.65 }, { sweepX: 1.25, duration: Math.min(0.68, dur - 0.3), ease: 'power1.inOut', immediateRender: false }, 0.28);
      tl.fromTo(S, { env: -0.55 }, { env: 0.4, duration: dur, ease: 'none', immediateRender: false }, 0);
      tl.fromTo(k.post, { exposure: 0.3 }, { exposure: 1.0, duration: 0.24, ease: 'power2.out', immediateRender: false }, 0);
      if (props.exit === 'fade') tl.to(k.post, { exposure: 0, duration: 0.2, ease: EASE.exit }, dur - 0.2);
      letters.forEach((L, i) => {
        tl.fromTo(L.st, { y: -capName * 1.25, rx: 0.55 }, { y: 0, rx: 0, duration: 0.38, ease: EASE.enter, immediateRender: false }, cName + i * 0.05);
      });
      byLetters.forEach((L, i) => {
        tl.fromTo(L.st, { y: L.st.y }, { y: 0, duration: 0.3, ease: EASE.enter, immediateRender: false }, cName + 0.2 + i * 0.016);
      });
      k.objs = { scene, logo, logoPivot, halo, sweep, letters, byLetters, dust, camera, D };
      k.cName = cName;
    },

    update(t, cues, k) {
      const S = k.state, o = k.objs, cam = o.camera, THREE = k.THREE;
      // arco de cámara: Bézier cuadrática (lejos-derecha-abajo → control → pose final) + alabeo
      const p = S.cam, q = 1 - p;
      const P0 = [1.7, -0.75, 15.8], P1 = [1.1, 0.55, 13.6], P2 = [0.2, 0.06, 11.7];
      cam.position.set(q * q * P0[0] + 2 * q * p * P1[0] + p * p * P2[0], q * q * P0[1] + 2 * q * p * P1[1] + p * p * P2[1],
        q * q * P0[2] + 2 * q * p * P1[2] + p * p * P2[2]);
      cam.up.set(Math.sin(S.roll), Math.cos(S.roll), 0);
      cam.lookAt(0, 0.18 * q, 0);
      cam.updateMatrixWorld();
      o.logo.rotation.set(S.rotX, S.rotY, 0);
      o.logoPivot.position.z = S.lz;
      o.logoPivot.scale.setScalar(S.ls);
      o.halo.material.opacity = S.halo;
      o.sweep.uniforms.uSweepPos.value = S.sweepX;
      if (o.scene.environmentRotation) o.scene.environmentRotation.set(0, S.env, 0);
      o.letters.forEach((L) => { L.mesh.position.y = L.st.y; L.mesh.rotation.x = L.st.rx; });
      o.byLetters.forEach((L) => { L.holder.children[0].position.y = L.st.y; });
      // foco: de un plano delantero (logo desenfocado) al logo
      const dLogo = cam.position.distanceTo(o.logoPivot.position);
      const focus = THREE.MathUtils.lerp(dLogo * 0.55, dLogo, S.focusMix);
      const P = k.post;
      P.focus = focus;
      P.aperture = 26;
      if (o.dust) o.dust.update(t, cam, focus, 26, k.H);
    },
  });
})();
