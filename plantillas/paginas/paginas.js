/* Meta Ads OS · runtime de las páginas de captación (plantillas/paginas/paginas.js). Sin dependencias.
 *
 * - Atribución: utm_*, fbclid (→ fbc), cookie _fbp, ad_id (parámetro ad_id o utm_content numérico), IDs de campaña.
 * - Consentimiento (RGPD): el píxel de Meta no se carga hasta que el usuario acepta. Sin consentimiento solo viajan
 *   al webhook los identificadores que permita la base legal configurada.
 * - Cada envío genera un event_id que usa el evento del navegador y viaja al webhook para que la Conversions API del
 *   servidor deduplique (mismo event_name + event_id, contrato §17).
 * - Formularios accesibles, enlaces internos que conservan la atribución, vídeo y calendario que cargan bajo demanda.
 * Contrato: docs/desarrollo/contratos.md §16 (etapas y eventos) y §17 (páginas). Formato del envío: plantillas/paginas/README.md.
 * Escrito en ES2015 para navegadores internos antiguos de Instagram y Facebook.
 */
(function (raiz, fabrica) {
  var api = fabrica();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    raiz.PaginasOS = api;
    if (raiz.document) api.iniciar(raiz, raiz.document);
  }
})(typeof window !== 'undefined' ? window : this, function () {
  'use strict';

  var VERSION = 1;
  var PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id',
    'campaign_id', 'adset_id', 'ad_id', 'placement', 'site', 'fbclid'];
  var ESTANDAR = ['AddPaymentInfo', 'AddToCart', 'AddToWishlist', 'CompleteRegistration', 'Contact',
    'CustomizeProduct', 'Donate', 'FindLocation', 'InitiateCheckout', 'Lead', 'PageView', 'Purchase', 'Schedule',
    'Search', 'StartTrial', 'SubmitApplication', 'Subscribe', 'ViewContent'];
  var CLAVE_CONSENTIMIENTO = 'pos_consentimiento_v1';
  var CLAVE_CLIC = 'pos_fbclid_v1';
  var CLAVE_CONTACTO = 'pos_contacto_v1';
  var PIXEL_JS = 'https://connect.facebook.net/en_US/fbevents.js';

  // ───────────────────────── funciones puras (las prueban tests/herramientas/paginas_js.test.cjs) ─────────────────────────

  /** Parámetros de atribución de una query string («?utm_source=…»). Recorta a 500 caracteres. */
  function parametros(search) {
    var out = {};
    var texto = String(search || '').replace(/^\?/, '');
    if (!texto) return out;
    texto.split('&').forEach(function (par) {
      if (!par) return;
      var i = par.indexOf('=');
      var k = decodificar(i < 0 ? par : par.slice(0, i));
      var v = i < 0 ? '' : decodificar(par.slice(i + 1));
      if (PARAMS.indexOf(k) >= 0 && v && !(k in out)) out[k] = v.slice(0, 500);
    });
    return out;
  }

  function decodificar(t) {
    try { return decodeURIComponent(String(t).replace(/\+/g, ' ')); } catch (e) { return String(t); }
  }

  /** ad_id: el parámetro ad_id de la plantilla de UTMs; si falta, utm_content cuando es un ID numérico. */
  function adId(atr) {
    if (atr && atr.ad_id && /^\d{6,25}$/.test(atr.ad_id)) return atr.ad_id;
    if (atr && atr.utm_content && /^\d{6,25}$/.test(atr.utm_content)) return atr.utm_content;
    return '';
  }

  /** fbc con el formato de la cookie _fbc: fb.1.<milisegundos del clic>.<fbclid sin tocar mayúsculas>. */
  function fbcDesde(fbclid, ms) {
    if (!fbclid) return '';
    return 'fb.1.' + Math.floor(Number(ms) || Date.now()) + '.' + String(fbclid).trim();
  }

  function cookie(nombre, texto) {
    var partes = String(texto || '').split(/;\s*/);
    for (var i = 0; i < partes.length; i++) {
      var j = partes[i].indexOf('=');
      if (j > 0 && partes[i].slice(0, j) === nombre) return decodificar(partes[i].slice(j + 1));
    }
    return '';
  }

  function uuid(cripto) {
    if (cripto && typeof cripto.randomUUID === 'function') return cripto.randomUUID();
    var b = new Array(16);
    if (cripto && typeof cripto.getRandomValues === 'function') {
      var u = new Uint8Array(16);
      cripto.getRandomValues(u);
      for (var k = 0; k < 16; k++) b[k] = u[k];
    } else {
      for (var m = 0; m < 16; m++) b[m] = Math.floor(Math.random() * 256);
    }
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    var h = b.map(function (x) { return (x + 0x100).toString(16).slice(1); }).join('');
    return h.slice(0, 8) + '-' + h.slice(8, 12) + '-' + h.slice(12, 16) + '-' + h.slice(16, 20) + '-' + h.slice(20);
  }

  /** event_id legible y único: «lead_3f2a…». El mismo para el píxel y para el webhook. */
  function eventId(nombre, cripto) {
    var base = String(nombre || 'evento').toLowerCase().replace(/[^a-z0-9]+/g, '') || 'evento';
    return base + '_' + uuid(cripto).replace(/-/g, '');
  }

  /** Estado guardado del consentimiento: 'si', 'no' o 'pendiente' (sin decidir o caducado). */
  function leerConsentimiento(almacen, ahoraMs, caducidadDias) {
    var crudo = null;
    try { crudo = almacen && almacen.getItem(CLAVE_CONSENTIMIENTO); } catch (e) { crudo = null; }
    if (!crudo) return 'pendiente';
    try {
      var d = JSON.parse(crudo);
      var dias = Number(caducidadDias) || 365;
      if (!d || (d.estado !== 'si' && d.estado !== 'no')) return 'pendiente';
      if (!d.ms || (Number(ahoraMs) - d.ms) > dias * 86400000) return 'pendiente';
      return d.estado;
    } catch (e2) {
      return 'pendiente';
    }
  }

  function guardarConsentimiento(almacen, estado, ahoraMs) {
    try { almacen.setItem(CLAVE_CONSENTIMIENTO, JSON.stringify({ estado: estado, ms: Number(ahoraMs) || Date.now(), v: VERSION })); } catch (e) { /* modo privado */ }
  }

  /** ¿Pueden viajar al servidor los identificadores de Meta (fbclid, fbc, fbp, event_id) para la CAPI? */
  function identificadoresPermitidos(estado, baseLegal) {
    return estado === 'si' || baseLegal === 'interes_legitimo';
  }

  function esEstandar(nombre) { return ESTANDAR.indexOf(nombre) >= 0; }

  /**
   * Número escrito por una persona: «1.200» = 1200, «1.500,50» = 1500,5, «0.175» = 0,175, «1 200» = 1200. Vacío o
   * ilegible → null. Misma regla que _comun.numero() y num_humano() de paginas.py (vectores compartidos en
   * tests/herramientas/paginas_vectores.json): con punto y coma, el último es el decimal; con un solo separador, son
   * miles los grupos de 3 cifras tras un primer grupo de 1 a 3 que no empieza por 0. Igual en diagnostico.js.
   */
  function numEntrada(texto) {
    if (texto === null || texto === undefined || typeof texto === 'boolean') return null;
    if (typeof texto === 'number') return isFinite(texto) ? texto : null;
    var t = String(texto).trim().replace(/(\d)[ \u00a0\u2009\u202f](?=\d{3}(?!\d))/g, '$1');
    if (!/^[-+]?(?:\d[\d.,]*|[.,]\d+)(?:[eE][-+]?\d+)?$/.test(t)) return null;
    var exp = '';
    var me = /[eE][-+]?\d+$/.exec(t);
    if (me) { exp = me[0]; t = t.slice(0, me.index); }
    var signo = t.charAt(0) === '-' ? '-' : '';
    t = t.replace(/^[-+]+/, '').replace(/[.,]+$/, '');
    if (!t || !/\d/.test(t)) return null;
    var n;
    if (t.indexOf(',') >= 0 && t.indexOf('.') >= 0) {
      var dec = t.lastIndexOf(',') > t.lastIndexOf('.') ? ',' : '.';
      var miles = dec === ',' ? '.' : ',';
      var i = t.lastIndexOf(dec);
      var entero = t.slice(0, i);
      var fraccion = t.slice(i + 1);
      if (!new RegExp('^(?:\\d{1,3}(?:\\' + miles + '\\d{3})*|\\d+)$').test(entero) || !/^\d+$/.test(fraccion)) return null;
      n = parseFloat(signo + entero.split(miles).join('') + '.' + fraccion + exp);
    } else {
      var sep = t.indexOf(',') >= 0 ? ',' : (t.indexOf('.') >= 0 ? '.' : '');
      if (sep && new RegExp('^[1-9]\\d{0,2}(?:\\' + sep + '\\d{3})+$').test(t)) n = parseFloat(signo + t.split(sep).join('') + exp);
      else if (sep && t.split(sep).length > 2) return null;
      else n = parseFloat(signo + (sep ? t.replace(sep, '.') : t) + exp);
    }
    return isFinite(n) ? n : null;
  }

  /** Valor de un campo para el envío: los números como número («1.200» → 1200); el resto, el texto recortado. */
  function valorCampo(tipo, valor) {
    if (tipo === 'casilla') return !!valor;
    var v = String(valor === null || valor === undefined ? '' : valor).trim();
    if (tipo === 'numero' && v !== '') { var n = numEntrada(v); return n === null ? v : n; }
    return v;
  }

  /**
   * Cuerpo del envío al webhook (formato v1, plantillas/paginas/README.md).
   * o = {tipoEnvio, pagina, url, ahoraMs, campos, respuestas, diagnostico, atribucion, primerClicMs, fbcCookie,
   *      fbpCookie, ua, consentimiento, baseLegal, eventos: [{event_name, event_id, value?, currency?}], ref,
   *      contentName}
   */
  function construirEnvio(o) {
    var atr = o.atribucion || {};
    var permitido = identificadoresPermitidos(o.consentimiento, o.baseLegal);
    var eventos = (o.eventos || []).map(function (ev) {
      var e = { event_name: ev.event_name, event_id: ev.event_id };
      if (ev.value !== undefined && ev.value !== null) { e.value = ev.value; e.currency = ev.currency || 'EUR'; }
      return e;
    });
    var principal = eventos[0] || { event_name: '', event_id: '' };
    var cuerpo = {
      version: VERSION,
      origen: 'meta-ads-os/paginas',
      tipo_envio: o.tipoEnvio || 'lead',
      pagina: o.pagina || '',
      url: sinFbclid(o.url || ''),
      momento: new Date(Number(o.ahoraMs) || Date.now()).toISOString(),
      event_time: Math.floor((Number(o.ahoraMs) || Date.now()) / 1000),
      ref: o.ref || '',
      content_name: o.contentName || ''
    };
    cuerpo.respuestas = o.respuestas || {};
    cuerpo.diagnostico = o.diagnostico || null;
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id', 'campaign_id', 'adset_id',
      'placement', 'site'].forEach(function (k) { cuerpo[k] = atr[k] || ''; });
    cuerpo.ad_id = adId(atr);
    cuerpo.consentimiento_marketing = o.consentimiento || 'pendiente';
    cuerpo.base_legal_servidor = o.baseLegal || 'consentimiento';
    cuerpo.enviar_a_meta = permitido;
    cuerpo.event_name = principal.event_name;
    cuerpo.event_id = permitido ? principal.event_id : '';
    cuerpo.eventos = permitido ? eventos : eventos.map(function (e) {
      var c = { event_name: e.event_name };
      if (e.value !== undefined) { c.value = e.value; c.currency = e.currency; }
      return c;
    });
    cuerpo.event_source_url = sinQuery(o.url || '');
    cuerpo.client_user_agent = o.ua || '';
    if (permitido) {
      cuerpo.fbclid = atr.fbclid || '';
      cuerpo.fbc = o.fbcCookie || fbcDesde(atr.fbclid, o.primerClicMs);
      cuerpo.fbp = o.consentimiento === 'si' ? (o.fbpCookie || '') : '';
    } else {
      cuerpo.fbclid = '';
      cuerpo.fbc = '';
      cuerpo.fbp = '';
    }
    /* Los campos del formulario van en la raíz con su id, pero nunca pisan los metadatos (origen, momento, ref…):
       paginas.py ya rechaza esos ids; esto protege los formularios hechos a mano. */
    var campos = o.campos || {};
    Object.keys(campos).forEach(function (k) { if (!Object.prototype.hasOwnProperty.call(cuerpo, k)) cuerpo[k] = campos[k]; });
    return cuerpo;
  }

  function sinQuery(url) { return String(url).split('#')[0].split('?')[0]; }
  function sinFbclid(url) {
    var u = String(url).split('#')[0];
    var i = u.indexOf('?');
    if (i < 0) return u;
    var q = u.slice(i + 1).split('&').filter(function (p) { return p && p.split('=')[0] !== 'fbclid'; });
    return u.slice(0, i) + (q.length ? '?' + q.join('&') : '');
  }

  /** ¿El enlace es de este mismo sitio (relativo o del mismo host)? */
  function esInterno(href, host) {
    var h = String(href || '').trim();
    if (!h || h.charAt(0) === '#') return false;
    if (/^(mailto:|tel:|sms:|javascript:|data:|whatsapp:)/i.test(h)) return false;
    var m = /^(?:https?:)?\/\/([^/?#]+)/i.exec(h);
    if (m) return !!host && m[1].toLowerCase() === String(host).toLowerCase();
    return true;
  }

  /** Añade a un enlace los parámetros que falten (sin pisar los que ya lleva). Conserva el #ancla. */
  function decorar(href, extra) {
    var h = String(href || '');
    var ancla = '';
    var i = h.indexOf('#');
    if (i >= 0) { ancla = h.slice(i); h = h.slice(0, i); }
    var j = h.indexOf('?');
    var base = j < 0 ? h : h.slice(0, j);
    var q = j < 0 ? [] : h.slice(j + 1).split('&').filter(Boolean);
    var presentes = q.map(function (p) { return decodificar(p.split('=')[0]); });
    Object.keys(extra || {}).forEach(function (k) {
      var v = extra[k];
      if (v === undefined || v === null || v === '' || presentes.indexOf(k) >= 0) return;
      q.push(encodeURIComponent(k) + '=' + encodeURIComponent(String(v)));
    });
    return base + (q.length ? '?' + q.join('&') : '') + ancla;
  }

  /** Valida un valor de formulario. Devuelve '' si es válido o el mensaje de error. */
  function validarValor(tipo, valor, requerido, etiqueta) {
    var v = typeof valor === 'string' ? valor.trim() : valor;
    if (tipo === 'casilla') return requerido && !v ? 'Marca la casilla para continuar.' : '';
    if (v === '' || v === null || v === undefined) return requerido ? (etiqueta ? 'Rellena este campo (' + etiqueta.toLowerCase() + ').' : 'Rellena este campo.') : '';
    if (tipo === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return 'Revisa el email: parece incompleto.';
    if (tipo === 'tel' && String(v).replace(/\D/g, '').length < 9) return 'Revisa el teléfono: faltan dígitos (incluye el prefijo si no es de España).';
    if (tipo === 'numero' && numEntrada(v) === null) return 'Escribe un número.';
    return '';
  }

  /** POST al webhook. modo 'json' (CORS) o 'texto' (petición simple sin preflight; la respuesta no se puede leer). */
  function enviar(fetchFn, url, cuerpo, modo, timeoutMs, Controlador) {
    var opciones = { method: 'POST', body: JSON.stringify(cuerpo), keepalive: true, credentials: 'omit' };
    if (modo === 'texto') {
      opciones.mode = 'no-cors';
      opciones.headers = { 'Content-Type': 'text/plain;charset=UTF-8' };
    } else {
      opciones.headers = { 'Content-Type': 'application/json' };
    }
    var temporizador = null;
    if (Controlador) {
      var c = new Controlador();
      opciones.signal = c.signal;
      temporizador = setTimeout(function () { c.abort(); }, Number(timeoutMs) || 8000);
    }
    return fetchFn(url, opciones).then(function (r) {
      if (temporizador) clearTimeout(temporizador);
      if (modo === 'texto') return true;
      if (!r || !r.ok) throw new Error('HTTP ' + (r ? r.status : '?'));
      return true;
    }, function (e) {
      if (temporizador) clearTimeout(temporizador);
      throw e;
    });
  }

  // ───────────────────────── navegador ─────────────────────────
  var estado = {
    w: null, d: null, cfg: {}, atribucion: {}, primerClicMs: 0, consentimiento: 'pendiente', pixel: false,
    cola: [], extensiones: {}, almacen: null, sesion: null
  };

  function leerConfig(d) {
    var nodo = d.getElementById('pos-config');
    if (!nodo) return {};
    try { return JSON.parse(nodo.textContent || '{}'); } catch (e) { return {}; }
  }

  function almacen(w, tipo) {
    try { var s = w[tipo]; var k = '__pos'; s.setItem(k, '1'); s.removeItem(k); return s; } catch (e) { return null; }
  }

  function prepararAtribucion() {
    var w = estado.w;
    var atr = parametros(w.location.search);
    estado.atribucion = atr;
    estado.primerClicMs = Date.now();
    if (atr.fbclid && estado.sesion && estado.consentimiento === 'si') {
      try {
        var previo = JSON.parse(estado.sesion.getItem(CLAVE_CLIC) || 'null');
        if (previo && previo.fbclid === atr.fbclid && previo.ms) estado.primerClicMs = previo.ms;
        else estado.sesion.setItem(CLAVE_CLIC, JSON.stringify({ fbclid: atr.fbclid, ms: estado.primerClicMs }));
      } catch (e) { /* sin almacenamiento */ }
    }
  }

  function parametrosParaEnlaces() {
    var atr = estado.atribucion;
    var out = {};
    PARAMS.forEach(function (k) { if (atr[k]) out[k] = atr[k]; });
    return out;
  }

  function decorarEnlaces() {
    var d = estado.d;
    var extra = parametrosParaEnlaces();
    if (!Object.keys(extra).length) return;
    var host = estado.w.location.host;
    var enlaces = d.querySelectorAll('a[href]');
    for (var i = 0; i < enlaces.length; i++) {
      var a = enlaces[i];
      if (a.hasAttribute('data-pos-sin-atribucion')) continue;
      var href = a.getAttribute('href');
      if (esInterno(href, host)) a.setAttribute('href', decorar(href, extra));
    }
  }

  // — píxel —
  function cargarPixel() {
    var w = estado.w;
    var id = estado.cfg.pixel_id;
    if (estado.pixel || !id || estado.cfg.eventos_navegador === false) return;
    if (!w.fbq) {
      /* Código base oficial del píxel, sin <noscript>: solo se ejecuta tras el consentimiento. */
      (function (f, b, e, v) {
        if (f.fbq) return;
        var n = f.fbq = function () { if (n.callMethod) n.callMethod.apply(n, arguments); else n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n;
        n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
        var t = b.createElement(e); t.async = true; t.src = v;
        var s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
      })(w, estado.d, 'script', PIXEL_JS);
    }
    w.fbq('consent', 'grant');
    w.fbq('init', id);
    estado.pixel = true;
    w.fbq('track', 'PageView', {}, { eventID: eventId('pageview', w.crypto) });
    var cola = estado.cola.splice(0);
    cola.forEach(function (ev) { dispararAhora(ev.nombre, ev.datos, ev.id); });
  }

  function dispararAhora(nombre, datos, id) {
    var w = estado.w;
    if (!w.fbq) return;
    w.fbq(esEstandar(nombre) ? 'track' : 'trackCustom', nombre, datos || {}, { eventID: id });
  }

  /** Evento del navegador. Con el consentimiento pendiente se guarda en cola (solo en esta página). */
  function evento(nombre, datosIn, id) {
    if (!nombre || !id || estado.cfg.eventos_navegador === false) return;
    var datos = {};
    Object.keys(datosIn || {}).forEach(function (k) { datos[k] = datosIn[k]; });
    if (estado.cfg.content_name && datos.content_name === undefined) datos.content_name = estado.cfg.content_name;
    if (estado.consentimiento === 'si' && estado.pixel) dispararAhora(nombre, datos, id);
    else if (estado.consentimiento === 'pendiente') estado.cola.push({ nombre: nombre, datos: datos, id: id });
  }

  function borrarCookiesMeta() {
    var d = estado.d;
    var partes = estado.w.location.hostname.split('.');
    var dominios = [''];
    for (var i = 0; i < partes.length - 1; i++) dominios.push('; domain=.' + partes.slice(i).join('.'));
    ['_fbp', '_fbc'].forEach(function (c) {
      dominios.forEach(function (dom) { d.cookie = c + '=; Max-Age=0; path=/' + dom; });
    });
  }

  /** API para el banner propio o para un gestor de consentimiento externo: PaginasOS.consentimiento('si'|'no'). */
  function consentimiento(nuevo) {
    if (nuevo !== 'si' && nuevo !== 'no') return estado.consentimiento;
    var antes = estado.consentimiento;
    estado.consentimiento = nuevo;
    guardarConsentimiento(estado.almacen, nuevo, Date.now());
    ocultarBanner();
    if (nuevo === 'si') {
      cargarPixel();
    } else {
      estado.cola = [];
      if (antes === 'si' && estado.w.fbq) estado.w.fbq('consent', 'revoke');
      borrarCookiesMeta();
      if (estado.sesion) { try { estado.sesion.removeItem(CLAVE_CLIC); } catch (e) { /* nada */ } }
    }
    return nuevo;
  }

  function banner() { return estado.d.querySelector('[data-pos-consentimiento]'); }

  function mostrarBanner() {
    var b = banner();
    if (!b) return;
    b.hidden = false;
    medirBanner();
  }

  function ocultarBanner() {
    var b = banner();
    if (b) b.hidden = true;
    medirBanner();
  }

  function medirBanner() {
    var b = banner();
    var alto = b && !b.hidden ? b.getBoundingClientRect().height : 0;
    estado.d.documentElement.style.setProperty('--alto-consentimiento', Math.round(alto) + 'px');
  }

  function prepararConsentimiento() {
    var d = estado.d;
    var cfg = estado.cfg.consentimiento || {};
    var b = banner();
    if (b) {
      var si = b.querySelector('[data-pos-aceptar]');
      var no = b.querySelector('[data-pos-rechazar]');
      if (si) si.addEventListener('click', function () { consentimiento('si'); });
      if (no) no.addEventListener('click', function () { consentimiento('no'); });
    }
    var prefs = d.querySelectorAll('[data-pos-preferencias]');
    for (var i = 0; i < prefs.length; i++) prefs[i].addEventListener('click', mostrarBanner);
    if (estado.consentimiento === 'si') cargarPixel();
    else if (estado.consentimiento === 'pendiente' && cfg.banner !== false) mostrarBanner();
    estado.w.addEventListener('resize', medirBanner);
  }

  // — formularios —
  function campoDe(form, input) {
    var envoltorio = input.closest ? input.closest('.pos-campo, .pos-casilla') : null;
    return envoltorio || input.parentNode;
  }

  function marcarError(form, input, mensaje) {
    var id = input.id + '-error';
    var nodo = form.querySelector('#' + id);
    if (mensaje) {
      input.setAttribute('aria-invalid', 'true');
      if (!nodo) {
        nodo = estado.d.createElement('p');
        nodo.className = 'pos-error';
        nodo.id = id;
        campoDe(form, input).appendChild(nodo);
      }
      nodo.textContent = mensaje;
      var desc = (input.getAttribute('aria-describedby') || '').split(' ').filter(Boolean);
      if (desc.indexOf(id) < 0) desc.push(id);
      input.setAttribute('aria-describedby', desc.join(' '));
    } else {
      input.removeAttribute('aria-invalid');
      if (nodo) nodo.parentNode.removeChild(nodo);
    }
  }

  function leerCampos(form) {
    var campos = {};
    var errores = [];
    var nodos = form.querySelectorAll('[data-pos-campo]');
    for (var i = 0; i < nodos.length; i++) {
      var n = nodos[i];
      var tipo = n.getAttribute('data-pos-campo');
      var valor = tipo === 'casilla' ? !!n.checked : String(n.value || '').trim();
      var etiqueta = n.getAttribute('data-etiqueta') || '';
      var error = validarValor(tipo, valor, n.required, etiqueta);
      marcarError(form, n, error);
      if (error) errores.push(n);
      campos[n.name] = valorCampo(tipo, valor);
    }
    return { campos: campos, errores: errores };
  }

  function mostrarEstado(form, texto, clase) {
    var nodo = form.querySelector('[data-pos-estado]');
    if (!nodo) return;
    nodo.className = 'pos-estado' + (clase ? ' pos-estado--' + clase : '');
    nodo.textContent = texto || '';
  }

  function navegar(destino, extra) {
    if (!destino) return;
    var w = estado.w;
    var url = esInterno(destino, w.location.host) ? decorar(destino, Object.assign({}, parametrosParaEnlaces(), extra || {})) : destino;
    var espera = estado.pixel ? 350 : 0; /* margen para que salga el evento del píxel antes de cambiar de página */
    setTimeout(function () { w.location.assign(url); }, espera);
  }

  function guardarContacto(campos) {
    if (!estado.sesion || estado.cfg.prefill_reserva === false) return;
    var c = {};
    ['nombre', 'apellidos', 'email', 'telefono'].forEach(function (k) { if (campos[k]) c[k] = campos[k]; });
    try { estado.sesion.setItem(CLAVE_CONTACTO, JSON.stringify(c)); } catch (e) { /* nada */ }
  }

  function enviarAlWebhook(cuerpo) {
    var w = estado.w;
    var wh = estado.cfg.webhook || {};
    if (!wh.url) {
      if (w.console) w.console.info('[PaginasOS] Modo prueba: sin webhook configurado. Esto es lo que se enviaría:', cuerpo);
      return Promise.resolve('prueba');
    }
    return enviar(w.fetch.bind(w), wh.url, cuerpo, wh.modo, wh.timeout_ms, w.AbortController);
  }

  function base(tipoEnvio, eventos, extra) {
    var w = estado.w;
    var o = {
      tipoEnvio: tipoEnvio,
      pagina: estado.cfg.tipo,
      url: w.location.href,
      ahoraMs: Date.now(),
      atribucion: estado.atribucion,
      primerClicMs: estado.primerClicMs,
      fbcCookie: estado.consentimiento === 'si' ? cookie('_fbc', estado.d.cookie) : '',
      fbpCookie: estado.consentimiento === 'si' ? cookie('_fbp', estado.d.cookie) : '',
      ua: w.navigator ? w.navigator.userAgent : '',
      consentimiento: estado.consentimiento,
      baseLegal: estado.cfg.base_legal_servidor,
      eventos: eventos,
      ref: referencia(),
      contentName: estado.cfg.content_name || ''
    };
    Object.keys(extra || {}).forEach(function (k) { o[k] = extra[k]; });
    return o;
  }

  function referencia() {
    var m = /[?&]ref=([^&#]+)/.exec(estado.w.location.search);
    return m ? decodificar(m[1]).slice(0, 80) : '';
  }

  function prepararFormulario(form) {
    form.setAttribute('novalidate', '');
    var abiertoMs = Date.now();
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (form.getAttribute('aria-busy') === 'true') return;
      var lectura = leerCampos(form);
      if (lectura.errores.length) {
        mostrarEstado(form, lectura.errores.length === 1 ? 'Revisa el campo marcado.' : 'Revisa los ' + lectura.errores.length + ' campos marcados.', 'error');
        lectura.errores[0].focus();
        return;
      }
      var trampa = form.querySelector('.pos-trampa input');
      var esBot = (trampa && trampa.value) || (Date.now() - abiertoMs < 800);
      var nombreEvento = form.getAttribute('data-evento') || 'Lead';
      if (!form.getAttribute('data-event-id')) form.setAttribute('data-event-id', eventId(nombreEvento, estado.w.crypto));
      var principal = { event_name: nombreEvento, event_id: form.getAttribute('data-event-id') };
      var ext = estado.extensiones[form.getAttribute('data-pos-formulario')] || {};
      var extraDiag = ext.preparar ? (ext.preparar(lectura.campos) || {}) : {};
      var eventos = [principal].concat(extraDiag.eventos || []);
      var cuerpo = construirEnvio(base(form.getAttribute('data-tipo-envio') || 'lead', eventos, {
        campos: lectura.campos, respuestas: extraDiag.respuestas || {}, diagnostico: extraDiag.diagnostico || null
      }));
      var boton = form.querySelector('[type="submit"]');
      var textoBoton = boton ? boton.textContent : '';
      form.setAttribute('aria-busy', 'true');
      if (boton) { boton.disabled = true; boton.textContent = 'Enviando…'; }
      mostrarEstado(form, '', '');
      var envio = esBot ? Promise.resolve(true) : enviarAlWebhook(cuerpo);
      envio.then(function (resultado) {
        if (!esBot) {
          eventos.forEach(function (e) {
            if (e.navegador === false) return; /* ya se disparó en el navegador antes (p. ej. al ver el resultado) */
            var datos = e.value !== undefined && e.value !== null ? { value: e.value, currency: e.currency } : {};
            evento(e.event_name, datos, e.event_id);
          });
          guardarContacto(lectura.campos);
        }
        if (resultado === 'prueba') mostrarEstado(form, 'Modo prueba: no hay webhook configurado y no se ha enviado nada. En la consola tienes los datos que se enviarían.', 'prueba');
        else mostrarEstado(form, form.getAttribute('data-mensaje-ok') || 'Recibido. Te llevamos al siguiente paso…', 'ok');
        form.removeAttribute('aria-busy');
        if (boton) { boton.disabled = false; boton.textContent = textoBoton; }
        var extra = { ref: principal.event_id };
        if (extraDiag.parametros) Object.keys(extraDiag.parametros).forEach(function (k) { extra[k] = extraDiag.parametros[k]; });
        if (ext.alEnviar && ext.alEnviar(extra) === false) return;
        var destino = form.getAttribute('data-siguiente');
        if (resultado === 'prueba') setTimeout(function () { navegar(destino, extra); }, 1500);
        else navegar(destino, extra);
      }, function () {
        form.removeAttribute('aria-busy');
        if (boton) { boton.disabled = false; boton.textContent = textoBoton; }
        var alt = form.getAttribute('data-alternativa');
        mostrarEstado(form, 'No hemos podido enviar tus datos. Comprueba la conexión y vuelve a intentarlo' + (alt ? ' o escríbenos: ' + alt : '.'), 'error');
      });
    });
    /* Un campo marcado se limpia mientras se escribe (no al salir de él): si el aviso desapareciera en el blur,
       el botón se movería justo al pulsarlo y el clic se perdería. */
    function revisar(e, alSalir) {
      var n = e.target;
      if (!n.hasAttribute('aria-invalid')) return;
      var tipo = n.getAttribute('data-pos-campo');
      var mensaje = validarValor(tipo, tipo === 'casilla' ? !!n.checked : n.value, n.required, n.getAttribute('data-etiqueta'));
      if (!mensaje && !alSalir) marcarError(form, n, '');
      else if (mensaje && alSalir) marcarError(form, n, mensaje);
    }
    var nodos = form.querySelectorAll('[data-pos-campo]');
    for (var i = 0; i < nodos.length; i++) {
      nodos[i].addEventListener('input', function (e) { revisar(e, false); });
      nodos[i].addEventListener('change', function (e) { revisar(e, false); });
      nodos[i].addEventListener('blur', function (e) { revisar(e, true); });
    }
  }

  // — barra fija de CTA —
  function prepararBarra() {
    var d = estado.d;
    var w = estado.w;
    var barra = d.querySelector('[data-pos-barra]');
    var hero = d.querySelector('[data-pos-hero]');
    if (!barra || !hero || !w.IntersectionObserver) return;
    var destinos = d.querySelectorAll('[data-pos-oculta-barra]');
    var visibleHero = true;
    var visiblesDestino = 0;
    function actualizar() {
      var mostrar = !visibleHero && visiblesDestino === 0;
      barra.classList.toggle('pos-barra--visible', mostrar);
      barra.setAttribute('aria-hidden', mostrar ? 'false' : 'true');
      var enlaces = barra.querySelectorAll('a, button');
      for (var i = 0; i < enlaces.length; i++) enlaces[i].tabIndex = mostrar ? 0 : -1;
      d.documentElement.style.setProperty('--alto-barra', mostrar ? Math.round(barra.getBoundingClientRect().height) + 'px' : '0px');
    }
    new w.IntersectionObserver(function (entradas) {
      visibleHero = entradas[0].isIntersecting;
      actualizar();
    }).observe(hero);
    if (destinos.length) {
      var obs = new w.IntersectionObserver(function (entradas) {
        entradas.forEach(function (e) { visiblesDestino += e.isIntersecting ? 1 : (e.target.__posVisto ? -1 : 0); e.target.__posVisto = e.isIntersecting; });
        if (visiblesDestino < 0) visiblesDestino = 0;
        actualizar();
      });
      for (var i = 0; i < destinos.length; i++) obs.observe(destinos[i]);
    }
    actualizar();
  }

  // — vídeo bajo demanda —
  function prepararVideos() {
    var d = estado.d;
    var botones = d.querySelectorAll('[data-pos-video]');
    for (var i = 0; i < botones.length; i++) {
      botones[i].addEventListener('click', function (e) {
        var b = e.currentTarget;
        var tipo = b.getAttribute('data-pos-video');
        var id = b.getAttribute('data-id') || '';
        var titulo = b.getAttribute('data-titulo') || 'Vídeo';
        var nodo;
        if (tipo === 'mp4') {
          nodo = d.createElement('video');
          nodo.src = b.getAttribute('data-src');
          nodo.controls = true; nodo.autoplay = true; nodo.playsInline = true;
          nodo.setAttribute('playsinline', '');
          var pista = b.getAttribute('data-subtitulos');
          if (pista) {
            var t = d.createElement('track');
            t.kind = 'captions'; t.src = pista; t.srclang = 'es'; t.label = 'Español'; t.default = true;
            nodo.appendChild(t);
          }
        } else {
          nodo = d.createElement('iframe');
          nodo.src = tipo === 'vimeo'
            ? 'https://player.vimeo.com/video/' + encodeURIComponent(id) + '?autoplay=1&dnt=1&playsinline=1'
            : 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0&playsinline=1';
          nodo.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
          nodo.setAttribute('allowfullscreen', '');
          nodo.title = titulo;
        }
        b.parentNode.replaceChild(nodo, b);
        if (nodo.focus) nodo.focus();
      });
    }
  }

  // — calendario de reserva —
  /**
   * Atribución que recibe la URL del calendario (la cita queda atribuida en el CRM aunque la persona llegue directa):
   * utm_*, campaign_id, adset_id, ad_id (o utm_content numérico), placement y site, más ref (el event_id del lead).
   * fbclid solo si la base legal deja enviar los identificadores de Meta.
   */
  function parametrosCalendario(atr, ref, permitido) {
    var a = atr || {};
    var out = {};
    PARAMS.forEach(function (k) { if (k !== 'fbclid' && k !== 'ad_id' && a[k]) out[k] = a[k]; });
    var ad = adId(a);
    if (ad) out.ad_id = ad;
    if (permitido && a.fbclid) out.fbclid = a.fbclid;
    if (ref) out.ref = ref;
    return out;
  }

  function prepararCalendario() {
    var d = estado.d;
    var w = estado.w;
    var caja = d.querySelector('[data-pos-calendario]');
    var cal = ((estado.cfg.pagina || {}).calendario) || null;
    if (!caja || !cal || !cal.url) return;
    var extra = {};
    if (estado.sesion && cal.prefill !== false) {
      try {
        var c = JSON.parse(estado.sesion.getItem(CLAVE_CONTACTO) || 'null') || {};
        Object.keys(cal.parametros || {}).forEach(function (k) { if (c[k]) extra[cal.parametros[k]] = c[k]; });
        estado.sesion.removeItem(CLAVE_CONTACTO);
      } catch (e) { /* nada */ }
    }
    var atr = parametrosCalendario(estado.atribucion, referencia(),
      identificadoresPermitidos(estado.consentimiento, estado.cfg.base_legal_servidor));
    Object.keys(atr).forEach(function (k) { if (!(k in extra)) extra[k] = atr[k]; });
    if (cal.proveedor === 'calendly') { extra.embed_domain = w.location.hostname; extra.embed_type = 'Inline'; }
    var iframe = d.createElement('iframe');
    iframe.title = cal.titulo || 'Calendario de reservas';
    iframe.src = decorar(cal.url, extra);
    iframe.setAttribute('loading', 'eager');
    iframe.addEventListener('load', function () { caja.classList.add('pos-calendario--listo'); });
    caja.appendChild(iframe);
    var origen = cal.origen || '';
    var registrada = false;
    w.addEventListener('message', function (e) {
      if (registrada || !origen || e.origin !== origen) return;
      var dato = e.data || {};
      var reservado = (cal.proveedor === 'calendly' && dato.event === 'calendly.event_scheduled');
      if (!reservado) return;
      registrada = true;
      reservaHecha();
    });
  }

  function reservaHecha() {
    var pag = estado.cfg.pagina || {};
    var id = eventId('Schedule', estado.w.crypto);
    var ref = referencia();
    if (pag.evento_schedule === 'navegador') evento('Schedule', {}, id);
    var tarea = Promise.resolve(true);
    if (pag.notificar_webhook) {
      tarea = enviarAlWebhook(construirEnvio(base('reserva', [{ event_name: 'Schedule', event_id: id }], {}))).then(null, function () { return false; });
    }
    tarea.then(function () {
      if (pag.siguiente) navegar(pag.siguiente, { ref: ref, reserva_registrada: '1' });
    });
  }

  // — página de gracias: evento opcional al llegar —
  function prepararGracias() {
    var pag = estado.cfg.pagina || {};
    if (estado.cfg.tipo !== 'gracias' || !pag.evento) return;
    if (/[?&]reserva_registrada=1/.test(estado.w.location.search) && pag.evento === 'Schedule') return;
    /* una recarga de la página no repite el evento (marca técnica en la sesión, solo con consentimiento) */
    var clave = 'pos_gracias_' + pag.evento + '_' + referencia();
    if (estado.sesion && estado.consentimiento === 'si') {
      try {
        if (estado.sesion.getItem(clave)) return;
        estado.sesion.setItem(clave, '1');
      } catch (e) { /* nada */ }
    }
    var id = eventId(pag.evento, estado.w.crypto);
    evento(pag.evento, {}, id);
    if (pag.notificar_webhook) {
      enviarAlWebhook(construirEnvio(base(pag.evento === 'Schedule' ? 'reserva' : 'evento', [{ event_name: pag.evento, event_id: id }], {}))).then(null, function () { return false; });
    }
  }

  // — reserva: mensaje según el resultado del diagnóstico (?nivel=…) —
  function prepararNivel() {
    var m = /[?&]nivel=([a-z0-9_-]+)/.exec(estado.w.location.search);
    if (!m) return;
    var nodos = estado.d.querySelectorAll('[data-pos-nivel-mensaje]');
    for (var i = 0; i < nodos.length; i++) nodos[i].hidden = nodos[i].getAttribute('data-pos-nivel-mensaje') !== m[1];
  }

  // — webinar: cuenta atrás ligera —
  /**
   * «Es hoy.», «Es mañana.» o «Faltan N días.» contando días naturales en la hora local de quien lo ve; '' si ya ha
   * empezado. desfase(ms) = minutos sobre UTC en ese momento (por defecto, los del navegador).
   */
  function textoCuenta(inicioMs, ahoraMs, desfase) {
    var inicio = Number(inicioMs);
    var ahora = Number(ahoraMs);
    if (!isFinite(inicio) || !isFinite(ahora) || inicio <= ahora) return '';
    var f = typeof desfase === 'function' ? desfase : function (ms) { return -new Date(ms).getTimezoneOffset(); };
    function dia(ms) { return Math.floor((ms + f(ms) * 60000) / 86400000); }
    var dias = dia(inicio) - dia(ahora);
    if (dias <= 0) return 'Es hoy.';
    if (dias === 1) return 'Es mañana.';
    return 'Faltan ' + dias + ' días.';
  }

  function prepararCuenta() {
    var nodo = estado.d.querySelector('[data-pos-cuenta]');
    if (!nodo) return;
    var inicio = Date.parse(nodo.getAttribute('data-pos-cuenta'));
    if (!inicio) return;
    nodo.textContent = textoCuenta(inicio, Date.now());
  }

  function iniciar(w, d) {
    function arrancar() {
      estado.w = w;
      estado.d = d;
      estado.cfg = leerConfig(d);
      estado.almacen = almacen(w, 'localStorage');
      estado.sesion = almacen(w, 'sessionStorage');
      estado.consentimiento = leerConsentimiento(estado.almacen, Date.now(), (estado.cfg.consentimiento || {}).caducidad_dias);
      prepararAtribucion();
      prepararConsentimiento();
      decorarEnlaces();
      var forms = d.querySelectorAll('form[data-pos-formulario]');
      for (var i = 0; i < forms.length; i++) prepararFormulario(forms[i]);
      prepararBarra();
      prepararVideos();
      prepararCalendario();
      prepararGracias();
      prepararCuenta();
      prepararNivel();
      d.documentElement.classList.add('pos-js');
    }
    if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', arrancar);
    else arrancar();
  }

  return {
    VERSION: VERSION, PARAMS: PARAMS, parametros: parametros, adId: adId, fbcDesde: fbcDesde, cookie: cookie,
    uuid: uuid, eventId: eventId, leerConsentimiento: leerConsentimiento, guardarConsentimiento: guardarConsentimiento,
    identificadoresPermitidos: identificadoresPermitidos, esEstandar: esEstandar, construirEnvio: construirEnvio,
    esInterno: esInterno, decorar: decorar, validarValor: validarValor, enviar: enviar, iniciar: iniciar,
    numEntrada: numEntrada, valorCampo: valorCampo, parametrosCalendario: parametrosCalendario, textoCuenta: textoCuenta,
    // para diagnostico.js y gestores de consentimiento externos
    consentimiento: consentimiento, evento: evento, extender: function (id, ext) { estado.extensiones[id] = ext; },
    enviarAlWebhook: function (c) { return enviarAlWebhook(c); }, construirBase: base, navegar: navegar,
    estado: function () { return estado; }
  };
});
