// Tests del JavaScript de las páginas (plantillas/paginas/paginas.js y diagnostico.js) con el runner de Node.
// Sin red ni navegador: solo funciones puras. Los lanza tests/herramientas/test_paginas.py si hay `node`;
// también a mano: node --test tests/herramientas/paginas_js.test.cjs
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const RAIZ = path.resolve(__dirname, '..', '..');
const P = require(path.join(RAIZ, 'plantillas', 'paginas', 'paginas.js'));
const D = require(path.join(RAIZ, 'plantillas', 'paginas', 'diagnostico.js'));
const VECTORES = JSON.parse(fs.readFileSync(path.join(__dirname, 'paginas_vectores.json'), 'utf8'));

function almacen(inicial) {
  const datos = Object.assign({}, inicial || {});
  return {
    getItem: (k) => (k in datos ? datos[k] : null),
    setItem: (k, v) => { datos[k] = String(v); },
    removeItem: (k) => { delete datos[k]; },
    datos,
  };
}

test('parametros: UTMs, IDs y fbclid; ignora el resto y no pisa repetidos', () => {
  const r = P.parametros('?utm_source=facebook&utm_campaign=Prueba+uno&utm_content=120000000000000123&fbclid=AbC_12-x&otro=1&utm_source=ig');
  assert.deepEqual(r, { utm_source: 'facebook', utm_campaign: 'Prueba uno', utm_content: '120000000000000123', fbclid: 'AbC_12-x' });
  assert.deepEqual(P.parametros(''), {});
  assert.equal(P.parametros('?utm_term=' + 'x'.repeat(900)).utm_term.length, 500);
  assert.deepEqual(P.parametros('?utm_source=%E0%A4%A'), { utm_source: '%E0%A4%A' });
});

test('adId: prioriza ad_id y si no usa utm_content numérico', () => {
  assert.equal(P.adId({ ad_id: '120000000000000999', utm_content: '120000000000000123' }), '120000000000000999');
  assert.equal(P.adId({ utm_content: '120000000000000123' }), '120000000000000123');
  assert.equal(P.adId({ utm_content: 'video-hook-a' }), '');
  assert.equal(P.adId({ ad_id: '{{ad.id}}', utm_content: 'x' }), '');
});

test('fbcDesde: formato fb.1.<ms>.<fbclid> sin tocar mayúsculas', () => {
  assert.equal(P.fbcDesde('AbC123', 1762700000000), 'fb.1.1762700000000.AbC123');
  assert.equal(P.fbcDesde('', 1), '');
});

test('cookie y eventId', () => {
  assert.equal(P.cookie('_fbp', 'a=1; _fbp=fb.1.1700000000000.123456789; b=2'), 'fb.1.1700000000000.123456789');
  assert.equal(P.cookie('_fbc', 'a=1'), '');
  const conCripto = P.eventId('Lead', { randomUUID: () => '3f2a0000-0000-4000-8000-000000000001' });
  assert.equal(conCripto, 'lead_3f2a0000000040008000000000000001');
  assert.match(P.eventId('DiagnosticoCompletado', null), /^diagnosticocompletado_[0-9a-f]{32}$/);
  assert.notEqual(P.eventId('Lead', null), P.eventId('Lead', null));
});

test('consentimiento: pendiente, guardado, caducado y corrupto', () => {
  const a = almacen();
  assert.equal(P.leerConsentimiento(a, Date.now(), 180), 'pendiente');
  P.guardarConsentimiento(a, 'si', 1000);
  assert.equal(P.leerConsentimiento(a, 1000 + 86400000, 180), 'si');
  assert.equal(P.leerConsentimiento(a, 1000 + 181 * 86400000, 180), 'pendiente');
  assert.equal(P.leerConsentimiento(almacen({ pos_consentimiento_v1: '{malo' }), 1, 180), 'pendiente');
  assert.equal(P.leerConsentimiento(null, 1, 180), 'pendiente');
  assert.equal(P.identificadoresPermitidos('si', 'consentimiento'), true);
  assert.equal(P.identificadoresPermitidos('pendiente', 'consentimiento'), false);
  assert.equal(P.identificadoresPermitidos('no', 'interes_legitimo'), true);
});

const BASE = {
  tipoEnvio: 'diagnostico', pagina: 'diagnostico',
  url: 'https://acme.example/diagnostico.html?utm_source=facebook&fbclid=AbC123&r_tamano=1#x',
  ahoraMs: 1762700000000, campos: { nombre: 'Ana', email: 'ana@acme.example' },
  atribucion: { utm_source: 'facebook', utm_content: '120000000000000123', fbclid: 'AbC123' },
  primerClicMs: 1762699990000, fbcCookie: '', fbpCookie: 'fb.1.1700000000000.42', ua: 'Prueba/1.0',
  eventos: [{ event_name: 'Lead', event_id: 'lead_1' }, { event_name: 'DiagnosticoCompletado', event_id: 'diag_1', value: 60, currency: 'EUR' }],
  ref: '', baseLegal: 'consentimiento',
};

test('construirEnvio con consentimiento: event_id, fbc, fbp y atribución', () => {
  const c = P.construirEnvio(Object.assign({}, BASE, { consentimiento: 'si' }));
  assert.equal(c.version, 1);
  assert.equal(c.origen, 'meta-ads-os/paginas');
  assert.equal(c.event_name, 'Lead');
  assert.equal(c.event_id, 'lead_1');
  assert.deepEqual(c.eventos[1], { event_name: 'DiagnosticoCompletado', event_id: 'diag_1', value: 60, currency: 'EUR' });
  assert.equal(c.fbc, 'fb.1.1762699990000.AbC123');
  assert.equal(c.fbp, 'fb.1.1700000000000.42');
  assert.equal(c.ad_id, '120000000000000123');
  assert.equal(c.nombre, 'Ana');
  assert.equal(c.enviar_a_meta, true);
  assert.equal(c.event_source_url, 'https://acme.example/diagnostico.html');
  assert.ok(!c.url.includes('fbclid'));
  assert.ok(c.url.includes('utm_source=facebook'));
  assert.equal(c.event_time, 1762700000);
  assert.equal(c.content_name, '');
  assert.equal(P.construirEnvio(Object.assign({}, BASE, { contentName: 'webinar-2026-12-03' })).content_name,
    'webinar-2026-12-03');
});

test('construirEnvio sin consentimiento: sin identificadores de Meta, con UTMs para el CRM', () => {
  const c = P.construirEnvio(Object.assign({}, BASE, { consentimiento: 'pendiente' }));
  assert.equal(c.enviar_a_meta, false);
  assert.equal(c.event_id, '');
  assert.equal(c.fbc, '');
  assert.equal(c.fbp, '');
  assert.equal(c.fbclid, '');
  assert.deepEqual(c.eventos, [{ event_name: 'Lead' }, { event_name: 'DiagnosticoCompletado', value: 60, currency: 'EUR' }]);
  assert.equal(c.utm_source, 'facebook');
  assert.equal(c.ad_id, '120000000000000123');
});

test('construirEnvio con interés legítimo: event_id y fbc, pero nunca la cookie _fbp', () => {
  const c = P.construirEnvio(Object.assign({}, BASE, { consentimiento: 'no', baseLegal: 'interes_legitimo' }));
  assert.equal(c.event_id, 'lead_1');
  assert.equal(c.fbc, 'fb.1.1762699990000.AbC123');
  assert.equal(c.fbp, '');
});

test('esInterno y decorar', () => {
  assert.equal(P.esInterno('reserva.html', 'acme.example'), true);
  assert.equal(P.esInterno('https://acme.example/x', 'acme.example'), true);
  assert.equal(P.esInterno('https://otra.example/x', 'acme.example'), false);
  assert.equal(P.esInterno('#contacto', 'acme.example'), false);
  assert.equal(P.esInterno('mailto:hola@acme.example', 'acme.example'), false);
  assert.equal(P.decorar('reserva.html?nivel=alto#top', { nivel: 'bajo', utm_source: 'fb', vacio: '' }), 'reserva.html?nivel=alto&utm_source=fb#top');
  assert.equal(P.decorar('reserva.html', { ref: 'lead 1' }), 'reserva.html?ref=lead%201');
});

test('validarValor', () => {
  assert.equal(P.validarValor('email', 'ana@acme.example', true, 'Email'), '');
  assert.match(P.validarValor('email', 'ana@', true, 'Email'), /email/);
  assert.match(P.validarValor('texto', '  ', true, 'Empresa'), /Rellena este campo \(empresa\)/);
  assert.equal(P.validarValor('texto', '', false, 'Cargo'), '');
  assert.match(P.validarValor('tel', '600 12', true, 'Teléfono'), /teléfono/);
  assert.equal(P.validarValor('tel', '+34 600 000 000', true, 'Teléfono'), '');
  assert.match(P.validarValor('casilla', false, true, ''), /casilla/);
  assert.match(P.validarValor('numero', 'abc', true, 'Horas'), /número/);
});

test('enviar: JSON con CORS y texto sin preflight', async () => {
  const llamadas = [];
  const okFetch = (url, o) => { llamadas.push([url, o]); return Promise.resolve({ ok: true, status: 200 }); };
  assert.equal(await P.enviar(okFetch, 'https://hooks.example/x', { a: 1 }, 'json', 1000, null), true);
  assert.equal(llamadas[0][1].headers['Content-Type'], 'application/json');
  assert.equal(llamadas[0][1].credentials, 'omit');
  assert.equal(llamadas[0][1].keepalive, true);
  await P.enviar(okFetch, 'https://hooks.example/x', { a: 1 }, 'texto', 1000, null);
  assert.equal(llamadas[1][1].mode, 'no-cors');
  assert.equal(llamadas[1][1].headers['Content-Type'], 'text/plain;charset=UTF-8');
  const malFetch = () => Promise.resolve({ ok: false, status: 500 });
  await assert.rejects(P.enviar(malFetch, 'https://hooks.example/x', {}, 'json', 1000, null), /HTTP 500/);
});

test('fórmulas: mismos resultados que Python (vectores compartidos)', () => {
  for (const c of VECTORES.casos) {
    const r = D.calcularExpresion(c.formula, VECTORES.variables);
    if (typeof c.esperado === 'number') assert.ok(Math.abs(r - c.esperado) < 1e-9, `${c.formula} → ${r}`);
    else assert.equal(r, c.esperado, c.formula);
  }
  for (const e of VECTORES.errores) {
    assert.throws(() => D.calcularExpresion(e.formula, VECTORES.variables), (err) => err.message.includes(e.contiene), e.formula);
  }
});

test('números escritos por personas y formato en español', () => {
  assert.equal(D.numEntrada('1.600'), 1600);
  assert.equal(D.numEntrada('12,5'), 12.5);
  assert.equal(D.numEntrada('1.600,5'), 1600.5);
  assert.equal(D.numEntrada('1.5'), 1.5);
  assert.equal(D.numEntrada('abc'), null);
  assert.equal(D.numEntrada(''), null);
  assert.equal(D.formatear(12600, 'eur', '', 'EUR'), '12.600 €');
  assert.equal(D.formatear(9500, 'eur', '', 'EUR'), '9.500 €');
  assert.equal(D.formatear(0.8, 'pct'), '80 %');
  assert.equal(D.formatear(8.571, 'meses'), '8,6 meses');
  assert.equal(D.formatear(1, 'meses'), '1 mes');
  assert.equal(D.formatear(450, 'horas'), '450 h');
  assert.equal(D.formatear(null, 'eur'), '—');
  assert.equal(D.formatear('Pedidos', 'texto'), 'Pedidos');
  const defs = { coste: { formato: 'eur' }, tarea: { formato: 'texto' } };
  assert.equal(D.rellenar('Entre {coste_min} y {coste_max} en {tarea} ({otra})', { coste: 12600, tarea: 'Pedidos' }, defs, 'EUR', 0.25),
    'Entre 9.500 € y 16.000 € en Pedidos ({otra})');
});

test('calcular: mismo nivel y valores que Python con el diagnóstico de ejemplo', { skip: !process.env.PAGINAS_PARIDAD }, () => {
  const datos = JSON.parse(fs.readFileSync(process.env.PAGINAS_PARIDAD, 'utf8'));
  for (const esc of datos.escenarios) {
    const r = D.calcular(datos.diagnostico, esc.respuestas, esc.supuestos);
    assert.equal(r.nivel, esc.python.nivel, esc.nombre);
    for (const [k, v] of Object.entries(esc.python.valores)) {
      if (typeof v === 'number') assert.ok(Math.abs(r.valores[k] - v) < 1e-6, `${esc.nombre}: ${k} ${r.valores[k]} ≠ ${v}`);
      else assert.equal(r.valores[k], v, `${esc.nombre}: ${k}`);
    }
  }
});

// ───────────────────────── hallazgos de la revisión del 2026-11-10 (I7) ─────────────────────────
test('numEntrada: mismos números humanos que Python (vectores compartidos)', () => {
  for (const [nombre, f] of [['paginas.js', P.numEntrada], ['diagnostico.js', D.numEntrada]]) {
    for (const c of VECTORES.numeros_humanos) {
      const r = f(c.texto);
      if (c.esperado === null) assert.equal(r, null, `${nombre}: ${JSON.stringify(c.texto)} → ${r}`);
      else assert.ok(r !== null && Math.abs(r - c.esperado) < 1e-9, `${nombre}: ${JSON.stringify(c.texto)} → ${r}`);
    }
  }
});

test('hallazgo 11: un campo número con «1.200» envía 1200 y «1.500,50» se acepta', () => {
  assert.equal(P.validarValor('numero', '1.500,50', true, 'Facturas'), '');
  assert.equal(P.validarValor('numero', '1.200', true, 'Facturas'), '');
  assert.match(P.validarValor('numero', '1.2.3', true, 'Horas'), /número/);
  assert.equal(P.valorCampo('numero', '1.200'), 1200);
  assert.equal(P.valorCampo('numero', '1.500,50'), 1500.5);
  assert.equal(P.valorCampo('numero', ''), '');
  assert.equal(P.valorCampo('texto', '1.200'), '1.200');
  assert.equal(P.valorCampo('casilla', true), true);
});

test('hallazgo 23: los campos del formulario no pisan los metadatos del envío v1', () => {
  const campos = { nombre: 'Ana', email: 'ana@acme.example', origen: 'Instagram', momento: 'ayer', ref: 'Luis',
    ad_id: '1', utm_source: 'x', event_id: 'falso', enviar_a_meta: 'sí', version: 9 };
  const c = P.construirEnvio(Object.assign({}, BASE, { consentimiento: 'si', ref: 'lead_previo', campos }));
  assert.equal(c.origen, 'meta-ads-os/paginas');
  assert.equal(c.version, 1);
  assert.equal(c.ref, 'lead_previo');
  assert.match(c.momento, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/);
  assert.equal(c.ad_id, '120000000000000123');
  assert.equal(c.utm_source, 'facebook');
  assert.equal(c.event_id, 'lead_1');
  assert.equal(c.enviar_a_meta, true);
  assert.equal(c.nombre, 'Ana');
  assert.equal(c.email, 'ana@acme.example');
});

test('hallazgo 26: el calendario recibe toda la atribución (y fbclid solo con permiso)', () => {
  const atr = P.parametros('?utm_source=fb_ad&utm_medium=paid&utm_campaign=c1&utm_content=v1&utm_term=t1' +
    '&utm_id=120000000000000001&campaign_id=120000000000000001&adset_id=120000000000000002' +
    '&ad_id=120000000000000003&placement=Facebook_Mobile_Feed&site=fb&fbclid=AbC_1');
  assert.deepEqual(P.parametrosCalendario(atr, 'lead_1', true), {
    utm_source: 'fb_ad', utm_medium: 'paid', utm_campaign: 'c1', utm_term: 't1', utm_content: 'v1',
    utm_id: '120000000000000001', campaign_id: '120000000000000001', adset_id: '120000000000000002',
    ad_id: '120000000000000003', placement: 'Facebook_Mobile_Feed', site: 'fb', fbclid: 'AbC_1', ref: 'lead_1' });
  const sin = P.parametrosCalendario(atr, '', false);
  assert.equal(sin.fbclid, undefined);
  assert.equal(sin.ref, undefined);
  assert.equal(sin.ad_id, '120000000000000003');
  // sin ad_id, el de utm_content numérico (como en el envío); una macro sin sustituir no viaja
  assert.equal(P.parametrosCalendario(P.parametros('?utm_content=120000000000000123'), '', false).ad_id, '120000000000000123');
  assert.equal(P.parametrosCalendario(P.parametros('?ad_id=%7B%7Bad.id%7D%7D'), '', false).ad_id, undefined);
});

test('hallazgo 27: la cuenta atrás cuenta días naturales en la hora local', () => {
  const inicio = Date.parse('2026-12-03T18:00:00+01:00');
  const madrid = () => 60;    // minutos sobre UTC (hora de invierno peninsular)
  const cdmx = () => -360;    // Ciudad de México
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-03T08:00:00+01:00'), madrid), 'Es hoy.');
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-03T17:30:00+01:00'), madrid), 'Es hoy.');
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-02T10:00:00+01:00'), madrid), 'Es mañana.');
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-02T23:59:00+01:00'), madrid), 'Es mañana.');
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-01T00:30:00+01:00'), madrid), 'Faltan 2 días.');
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-11-23T09:00:00+01:00'), madrid), 'Faltan 10 días.');
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-03T18:30:00+01:00'), madrid), '');
  // desde México el webinar es el 3 a las 11:00: el 2 a las 23:30 de allí (06:30 en Madrid del 3) es «mañana»
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-02T23:30:00-06:00'), cdmx), 'Es mañana.');
  assert.equal(P.textoCuenta(inicio, Date.parse('2026-12-03T00:30:00-06:00'), cdmx), 'Es hoy.');
  assert.equal(P.textoCuenta(NaN, Date.now()), '');
});
