/* cutkit · cámara virtual sobre el A-roll.
 *   #ck-cam (layout, lo mueve el runtime) > #ck-cam-push (camera.slow_push) > #ck-cam-move (punch_in / reframe) > frame > video
 * Todo con x/y/scale y transformOrigin "0 0": un zoom alrededor de un punto P es x = P·(1−s). Valores enteros (autoRound).
 * Reglas (perfil de edición): punch en el presentador ×1,25–1,5 (nunca > ×2,0; zona muerta 1,03–1,10 prohibida),
 * origen en los ojos, golpe = 4 f expo.out con 2–3 px de desenfoque; slow_push de respiración 1,00→1,06 en 3–6 s
 * o expresivo 1,00→1,16 en 0,9–2,3 s; nunca Ken Burns ni micro sobre la cara del split.
 */
(function (global) {
  'use strict';
  const U = CK.util;
  const E = CK.ease;            // enter · exit · move · pop (fuente única: runtime.js)

  /** punto de anclaje en coordenadas del fotograma (px).
   *  En cara completa (el raíl va bajo la cara) el ancla por defecto es la BARBILLA: el zoom la deja fija en pantalla,
   *  así el subtítulo nunca acaba sobre la boca y la cara crece hacia arriba (se corta pelo, nunca barbilla).
   *  En el split (subtítulo en la junta, arriba) el ancla son los ojos. */
  function focusPoint(ctx, t0, t1, focus) {
    if (focus && typeof focus === 'object') return { x: focus.x * ctx.W, y: focus.y * ctx.H };
    if (focus === 'center') return { x: ctx.W / 2, y: ctx.H * 0.42 };
    const f = ctx.faceMedian(t0, t1);
    const lay = ctx.layoutAt(t0 + 1e-3);
    const railBelow = lay && lay.name !== 'layout.split_top' && lay.railY > (f.y + f.h * 0.5) * ctx.H;
    if (focus === 'chin') return { x: (f.x + f.w / 2) * ctx.W, y: Math.min(ctx.H, (f.y + f.h + 0.035) * ctx.H) };
    if (focus === 'hair' || (focus !== 'eyes' && railBelow)) {
      // Regla de estilo: todos los zooms de cara completa se anclan ARRIBA, en el pelo medido (nunca se corta el pelo)
      const hd = U.headOf(f, t0, t1);
      return { x: (f.x + f.w / 2) * ctx.W, y: Math.max(0.04 * ctx.H, hd.hair * ctx.H) };
    }
    return { x: (f.x + f.w / 2) * ctx.W, y: (f.y + f.h * 0.40) * ctx.H };   // ojos
  }
  /** Tope de zoom por la cabeza (una cabeza que no cabe en pantalla es demasiado zoom). Para un zoom k de #ck-cam-move
   *  (o del push) alrededor de un punto P del fotograma, encadenado con el layout (y el push máximo activo):
   *   - la parte de arriba del pelo queda ≥ 3 % del alto (cara completa) o ≥ J+16 (split: siempre bajo la junta);
   *   - la cabeza entera ≤ 70 % del alto del plano;
   *   - la boca no baja al raíl de subtítulos (cara completa) ni de y=1632 (split).
   *  Prefiere el ancla `pref` (barbilla o ojos); si con ella el pelo se sale, sube el ancla; si aun así no cabe, baja k.
   *  Devuelve {k, P, clamped}; si k < 1,03 → sin zoom (k=1). Lo apunta en __ckReport.camera_clamped. */
  function safeZoom(ctx, t0, t1, kReq, pref, opts) {
    opts = opts || {};
    const L = ctx.layoutAt(t0 + 1e-3);
    const cam = L.cam || { x: 0, y: 0, scale: 1 };
    const f = ctx.faceMedian(t0, t1);
    const hd = U.headOf(f, t0, t1), H = ctx.H;
    const split = L.name === 'layout.split_top';
    // push activo (zoom lento de #ck-cam-push) por encima: se toma su escala máxima y su ancla
    const pm = opts.push || 1, Pc = opts.pushP != null ? opts.pushP : hd.chin * H;
    const A = (cam.y || 0) + (cam.scale || 1) * Pc * (1 - pm), B = (cam.scale || 1) * pm;
    const scr = (yl) => A + B * yl;                       // y local del fotograma (tras el zoom de move) → pantalla
    const hl = hd.hair * H, ml = hd.mouth * H, lenl = hd.len * H;
    const top = split ? (L.seamY || 960) + 40 : 0.04 * H;            // pelo ≥ 4 % (≈77 px) en cara completa
    const bottom = split ? 1690 : ((L.railY || 1300) - 40);          // boca por encima del raíl
    const kHead = (0.70 * H) / (B * lenl);
    let k = Math.min(kReq, kHead), P = pref, why = kReq > kHead ? 'cabeza_70' : null;
    for (let it = 0; it < 80 && k > 1.0001; it++) {
      const m = (top - A) / B;                            // pelo local mínimo tras el zoom
      const Pmax = (k * hl - m) / (k - 1);                // ancla más baja que deja el pelo dentro
      P = Math.min(pref, Pmax);
      const okHair = k * hl - m >= 0 && P >= 0;
      const mouthS = scr(k * ml + P * (1 - k));
      if (okHair && mouthS <= bottom) break;
      why = why || (okHair ? 'boca' : 'pelo');
      k = Math.round((k - 0.01) * 1000) / 1000;
    }
    if (k < 1.03) { k = 1; P = pref; }
    const clamped = k < kReq - 1e-3;
    if (clamped && global.__ckReport) {
      global.__ckReport.camera_clamped.push({ item: ctx.item.id, component: ctx.item.component, req: kReq, to: +k.toFixed(3), reason: why, layout: L.name });
    }
    return { k, P, clamped };
  }

  /** zoom lento (camera.slow_push) activo en [t0, t1): {push: escala máx, pushP: ancla y} para encadenar topes */
  function pushAt(t0, t1) {
    const its = (CK.pushes || []).filter((q) => q.t1 > t0 + 1e-3 && q.t0 < t1 - 1e-3);
    if (!its.length) return {};
    const q = its.reduce((a, b) => (b.k > a.k ? b : a));
    return { push: q.k, pushP: q.Py };
  }
  /** tramos de layout (CK.segments) que cruzan [t0, t1) */
  function segmentsIn(t0, t1) {
    return (CK.segments || []).filter((sg) => sg.t1 > t0 + 1e-3 && sg.t0 < t1 - 1e-3);
  }
  const zoomAt = (P, s) => ({ x: Math.round(P.x * (1 - s)), y: Math.round(P.y * (1 - s)), scale: s });
  const IDENT = { x: 0, y: 0, scale: 1 };

  // ───────────────────────── camera.punch_in
  CK.register('camera.punch_in', {
    kind: 'camera',
    mount(root, p, ctx) {
      let s = U.clamp(p.scale != null ? p.scale : 1.3, 1.0, 2.0);
      if (s > 1.0 && s < 1.12) s = 1.12;                                  // fuera de la zona muerta
      const cut = p.cut !== false;
      const frames = p.frames != null ? p.frames : (cut ? 0 : 4);
      // plan del zoom en el MONTAJE (los subtítulos montan después y colocan su raíl bajo el mentón real del punch)
      const T0 = U.snap(ctx.item.t0), T1 = U.snap(ctx.item.t1);
      // si el layout cambia a mitad del zoom, el zoom se CORTA con el layout (no se re-ancla ni vuelve aparte)
      const segs0 = segmentsIn(T0, T1).slice(0, 1);
      const T1c = segs0.length && segmentsIn(T0, T1).length > 1 ? U.snap(segmentsIn(T0, T1)[1].t0) : T1;
      const plan = segs0.map((sg, i) => {
        const a = T0, b = T1c;
        const Pk0 = focusPoint(ctx, a, b, p.focus);
        const zk = safeZoom(ctx, a, b, s, Pk0.y, pushAt(a, b));
        return { a, b, P: { x: Pk0.x, y: zk.P }, k: zk.k };
      });
      plan.forEach((q) => { if (q.k > 1) (CK.punches = CK.punches || []).push({ t0: q.a, t1: q.b, k: q.k, Py: q.P.y }); });
      return {
        animate(tl, t0, t1) {
          // el ancla depende del layout: si el punch cruza un cambio de layout, se re-ancla en el corte (salto invisible)
          const segs = segs0;
          const sEff = plan.length ? plan[0].k : 1;
          const P = plan.length ? plan[0].P : focusPoint(ctx, t0, t1, p.focus);
          let to = zoomAt(P, sEff);
          const from = p.from != null ? zoomAt(P, U.clamp(Math.min(p.from, sEff), 1, 2)) : IDENT;
          if (sEff > 1) ctx.event('camera.punch', frames <= 0 ? t0 : t0 + Math.min(frames, 2) / ctx.fps, { scale: sEff, cut: frames <= 0 });
          if (frames <= 0) {
            tl.set(ctx.cam.move, to, t0);
          } else {
            const d = frames / ctx.fps;
            tl.fromTo(ctx.cam.move, from, Object.assign({}, to, { duration: d, ease: (E[p.ease] || E.enter), immediateRender: false }), t0);
            const blur = p.blur != null ? p.blur : 2.5;
            if (blur > 0) {
              tl.fromTo(ctx.cam.frame, { filter: `blur(${blur}px)` }, { filter: 'blur(0px)', duration: d, ease: E.enter, immediateRender: false }, t0);
              tl.set(ctx.cam.frame, { filter: 'none' }, t0 + d);
            }
          }
          for (let i = 1; i < plan.length; i++) {
            const nk = zoomAt(plan[i].P, plan[i].k);
            if (nk.x !== to.x || nk.y !== to.y || nk.scale !== to.scale) { tl.fromTo(ctx.cam.move, to, Object.assign({}, nk, { duration: 0, immediateRender: false }), plan[i].a); to = nk; }
          }
          // vuelta: corte (por defecto) o suave de 12 f que TERMINA en t1
          const out = p.out || 'cut';
          if (out === 'ease') {
            const d = Math.min(12 / ctx.fps, (t1 - t0) * 0.4);
            tl.fromTo(ctx.cam.move, to, Object.assign({}, IDENT, { duration: d, ease: E.move, immediateRender: false }), t1 - d);
          } else if (out !== 'hold') {
            tl.set(ctx.cam.move, IDENT, Math.min(t1, T1c));
          }
        },
      };
    },
  });

  // ───────────────────────── camera.slow_push
  CK.register('camera.slow_push', {
    kind: 'camera',
    mount(root, p, ctx) {
      const lay = ctx.layout && ctx.layout.name;
      if (lay === 'layout.split_top' && !p.force) {
        console.warn('[CK] camera.slow_push ignorado: la cara del split va fija');
        return { animate() {} };
      }
      const mode = p.mode || 'breath';
      const amount = p.amount != null ? p.amount : (mode === 'expressive' ? 0.14 : 0.04);
      let from = p.from != null ? p.from : (p.direction === 'out' ? 1 + amount : 1);
      let to = p.to != null ? p.to : (p.direction === 'out' ? 1 : 1 + amount);
      // plan en el MONTAJE (punch y subtítulos lo leen)
      let T1p = U.snap(ctx.item.t1);
      const T0p = U.snap(ctx.item.t0);
      const sp0 = segmentsIn(T0p, T1p).find((sg) => sg.t0 > T0p + 1e-3);
      if (sp0 && !p.force) T1p = U.snap(sp0.t0);      // se corta con el primer cambio de layout
      const P0m = focusPoint(ctx, T0p, T1p, p.focus);
      const zMax = safeZoom(ctx, T0p, T1p, Math.max(from, to), P0m.y, {});
      from = Math.min(from, zMax.k); to = Math.min(to, zMax.k);
      const Pm = { x: P0m.x, y: zMax.P };
      (CK.pushes = CK.pushes || []).push({ t0: T0p, t1: T1p, k: Math.max(from, to), Py: Pm.y });
      return {
        animate(tl, t0, t1) {
          t1 = Math.min(t1, T1p);
          const P = Pm;
          if (Math.abs(from - to) < 0.005 && from <= 1.0001) return;
          const dur = Math.max(0.1, (t1 - t0) - (p.hold_end || 0));
          const ease = E[p.ease] || (mode === 'expressive' ? E.enter : E.move);
          tl.fromTo(ctx.cam.push, zoomAt(P, from), Object.assign(zoomAt(P, to), { duration: dur, ease, immediateRender: false }), t0);
          if (p.out !== 'hold') tl.set(ctx.cam.push, IDENT, t1);
        },
      };
    },
  });

  // ───────────────────────── camera.reframe
  CK.register('camera.reframe', {
    kind: 'camera',
    mount(root, p, ctx) {
      const s = U.clamp(p.scale != null ? p.scale : 1.15, 1, 2);
      return {
        animate(tl, t0, t1) {
          const f = ctx.faceMedian(t0, t1);
          const fx = (f.x + f.w / 2) * ctx.W, fy = (f.y + f.h * 0.4) * ctx.H;
          const tx = (p.target && p.target.x != null ? p.target.x : 0.5) * ctx.W;
          const ty = (p.target && p.target.y != null ? p.target.y : 0.40) * ctx.H;
          const to = {
            x: Math.round(U.clamp(tx - s * fx, ctx.W - s * ctx.W, 0)),
            y: Math.round(U.clamp(ty - s * fy, ctx.H - s * ctx.H, 0)),
            scale: s,
          };
          const zr = safeZoom(ctx, t0, t1, s, fy, pushAt(t0, t1));
          if (zr.k < s) {                                       // recortado: zoom seguro alrededor del ancla permitida
            const z = zoomAt({ x: fx, y: zr.P }, zr.k); to.x = z.x; to.y = z.y; to.scale = z.scale;
          }
          const frames = p.frames != null ? p.frames : 0;
          if (frames <= 0) tl.set(ctx.cam.move, to, t0);
          else tl.fromTo(ctx.cam.move, IDENT, Object.assign({}, to, { duration: frames / ctx.fps, ease: (E[p.ease] || E.move), immediateRender: false }), t0);
          const out = p.out || 'cut';
          if (out === 'ease') {
            const d = Math.min(12 / ctx.fps, (t1 - t0) * 0.4);
            tl.fromTo(ctx.cam.move, to, Object.assign({}, IDENT, { duration: d, ease: E.move, immediateRender: false }), t1 - d);
          } else if (out !== 'hold') tl.set(ctx.cam.move, IDENT, t1);
        },
      };
    },
  });
})(typeof window !== 'undefined' ? window : globalThis);
