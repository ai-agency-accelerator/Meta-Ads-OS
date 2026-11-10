/* Meta Ads OS · diagnóstico interactivo (plantillas/paginas/diagnostico.js). Sin dependencias. Necesita paginas.js.
 *
 * Preguntas paso a paso → cálculo con supuestos visibles y editables → recomendación honesta por umbrales
 * (p. ej. «no nos contrates», «empieza por un proceso», «hay proyecto») → reserva de llamada.
 * Las fórmulas se evalúan con un intérprete propio (sin eval ni Function): números, + - * / % ^, comparaciones,
 * y/o/no, y las funciones min, max, abs, redondear, limitar, si, suma, media, cuenta y mayor.
 * La misma gramática la valida herramientas/paginas.py antes de generar la página.
 * Evento DiagnosticoCompletado (contrato §16): value = valor esperado del lead por nivel [HYPOTHESIS], nunca el ahorro.
 */
(function (raiz, fabrica) {
  var api = fabrica();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  } else {
    raiz.DiagnosticoOS = api;
    if (raiz.document) api.iniciar(raiz, raiz.document);
  }
})(typeof window !== 'undefined' ? window : this, function () {
  'use strict';

  // ───────────────────────── expresiones ─────────────────────────
  var PALABRAS = { y: '&&', and: '&&', o: '||', or: '||', no: '!', not: '!' };
  var FUNCIONES = ['min', 'max', 'abs', 'redondear', 'limitar', 'si', 'suma', 'media', 'cuenta', 'mayor'];
  var DE_GRUPO = ['suma', 'media', 'cuenta', 'mayor'];

  function ErrorExpresion(mensaje) { this.name = 'ErrorExpresion'; this.message = mensaje; }
  ErrorExpresion.prototype = Object.create(Error.prototype);

  function tokenizar(texto) {
    var t = String(texto);
    var out = [];
    var i = 0;
    while (i < t.length) {
      var c = t.charAt(i);
      if (/\s/.test(c)) { i++; continue; }
      var m = /^\d+(?:\.\d+)?/.exec(t.slice(i));
      if (m) { out.push({ t: 'num', v: parseFloat(m[0]) }); i += m[0].length; continue; }
      m = /^[a-z_][a-z0-9_]*/.exec(t.slice(i));
      if (m) {
        if (PALABRAS[m[0]]) out.push({ t: 'op', v: PALABRAS[m[0]] });
        else out.push({ t: 'id', v: m[0] });
        i += m[0].length;
        continue;
      }
      m = /^(<=|>=|==|!=|&&|\|\||[-+*/%^()<>,!])/.exec(t.slice(i));
      if (m) { out.push({ t: 'op', v: m[0] }); i += m[0].length; continue; }
      throw new ErrorExpresion('Carácter no válido «' + c + '» en la posición ' + (i + 1));
    }
    return out;
  }

  function parsear(texto) {
    var tk = tokenizar(texto);
    var p = 0;
    function ver(v) { return p < tk.length && tk[p].t === 'op' && tk[p].v === v; }
    function tomar(v) { if (!ver(v)) throw new ErrorExpresion('Se esperaba «' + v + '»'); p++; }
    function o() {
      var a = y();
      while (ver('||')) { p++; a = { t: 'bin', op: '||', a: a, b: y() }; }
      return a;
    }
    function y() {
      var a = no();
      while (ver('&&')) { p++; a = { t: 'bin', op: '&&', a: a, b: no() }; }
      return a;
    }
    function no() {
      if (ver('!')) { p++; return { t: 'un', op: '!', a: no() }; }
      return comparacion();
    }
    function comparacion() {
      var a = suma();
      var ops = ['<', '<=', '>', '>=', '==', '!='];
      if (p < tk.length && tk[p].t === 'op' && ops.indexOf(tk[p].v) >= 0) {
        var op = tk[p++].v;
        a = { t: 'bin', op: op, a: a, b: suma() };
      }
      return a;
    }
    function suma() {
      var a = producto();
      while (ver('+') || ver('-')) { var op = tk[p++].v; a = { t: 'bin', op: op, a: a, b: producto() }; }
      return a;
    }
    function producto() {
      var a = unario();
      while (ver('*') || ver('/') || ver('%')) { var op = tk[p++].v; a = { t: 'bin', op: op, a: a, b: unario() }; }
      return a;
    }
    function unario() {
      if (ver('-')) { p++; return { t: 'un', op: '-', a: unario() }; }
      if (ver('+')) { p++; return unario(); }
      return potencia();
    }
    function potencia() {
      var a = primario();
      if (ver('^')) { p++; a = { t: 'bin', op: '^', a: a, b: unario() }; }
      return a;
    }
    function primario() {
      if (p >= tk.length) throw new ErrorExpresion('La fórmula termina antes de tiempo');
      var k = tk[p];
      if (k.t === 'num') { p++; return { t: 'num', v: k.v }; }
      if (k.t === 'id') {
        p++;
        if (ver('(')) {
          if (FUNCIONES.indexOf(k.v) < 0) throw new ErrorExpresion('Función desconocida «' + k.v + '»');
          p++;
          var args = [];
          if (!ver(')')) {
            args.push(o());
            while (ver(',')) { p++; args.push(o()); }
          }
          tomar(')');
          return { t: 'fn', n: k.v, args: args };
        }
        return { t: 'var', n: k.v };
      }
      if (ver('(')) { p++; var e = o(); tomar(')'); return e; }
      throw new ErrorExpresion('Símbolo inesperado «' + k.v + '»');
    }
    var arbol = o();
    if (p < tk.length) throw new ErrorExpresion('Sobra «' + tk[p].v + '» al final');
    return arbol;
  }

  function num(v) {
    if (v === null || v === undefined || v === '') return null;
    if (typeof v === 'boolean') return v ? 1 : 0;
    var n = typeof v === 'number' ? v : parseFloat(String(v).replace(',', '.'));
    return isFinite(n) ? n : null;
  }
  function verdad(v) { var n = num(v); return n !== null && n !== 0; }

  /**
   * Número escrito por una persona: «12,5», «1.600» (miles), «1.600,5», «0.175» o «1 200». Vacío o ilegible → null.
   * Copia exacta de numEntrada() de paginas.js (este archivo se prueba sin él): misma regla que _comun.numero() y
   * num_humano() de paginas.py, con los vectores de tests/herramientas/paginas_vectores.json.
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

  function evaluar(arbol, buscar) {
    switch (arbol.t) {
      case 'num': return arbol.v;
      case 'var': return buscar(arbol.n);
      case 'un': {
        if (arbol.op === '!') return verdad(evaluar(arbol.a, buscar)) ? 0 : 1;
        var x = num(evaluar(arbol.a, buscar));
        return x === null ? null : -x;
      }
      case 'bin': {
        if (arbol.op === '&&') return verdad(evaluar(arbol.a, buscar)) && verdad(evaluar(arbol.b, buscar)) ? 1 : 0;
        if (arbol.op === '||') return verdad(evaluar(arbol.a, buscar)) || verdad(evaluar(arbol.b, buscar)) ? 1 : 0;
        var a = num(evaluar(arbol.a, buscar));
        var b = num(evaluar(arbol.b, buscar));
        if (['<', '<=', '>', '>=', '==', '!='].indexOf(arbol.op) >= 0) {
          if (a === null || b === null) return 0;
          switch (arbol.op) {
            case '<': return a < b ? 1 : 0;
            case '<=': return a <= b ? 1 : 0;
            case '>': return a > b ? 1 : 0;
            case '>=': return a >= b ? 1 : 0;
            case '==': return Math.abs(a - b) < 1e-9 ? 1 : 0;
            default: return Math.abs(a - b) >= 1e-9 ? 1 : 0;
          }
        }
        if (a === null || b === null) return null;
        switch (arbol.op) {
          case '+': return a + b;
          case '-': return a - b;
          case '*': return a * b;
          case '/': return b === 0 ? null : a / b;
          case '%': return b === 0 ? null : a % b;
          default: { var r = Math.pow(a, b); return isFinite(r) ? r : null; }
        }
      }
      case 'fn': return funcion(arbol, buscar);
      default: throw new ErrorExpresion('Nodo desconocido');
    }
  }

  function funcion(arbol, buscar) {
    var n = arbol.n;
    var args = arbol.args;
    if (DE_GRUPO.indexOf(n) >= 0) {
      if (!args.length || args[0].t !== 'var') throw new ErrorExpresion(n + '() necesita el nombre de un grupo como primer argumento');
      var lista = buscar(args[0].n);
      if (!Array.isArray(lista)) lista = [];
      if (n === 'cuenta') return lista.length;
      if (args.length < 2) throw new ErrorExpresion(n + '() necesita una expresión como segundo argumento');
      var valores = lista.map(function (item) {
        return num(evaluar(args[1], function (nombre) {
          return Object.prototype.hasOwnProperty.call(item, nombre) ? item[nombre] : buscar(nombre);
        }));
      });
      if (n === 'suma') return valores.reduce(function (s, v) { return s + (v === null ? 0 : v); }, 0);
      if (n === 'media') {
        var validos = valores.filter(function (v) { return v !== null; });
        return validos.length ? validos.reduce(function (s, v) { return s + v; }, 0) / validos.length : null;
      }
      // mayor(grupo, expresion, campo): el campo del elemento con la expresión más alta
      if (args.length < 3 || args[2].t !== 'var') throw new ErrorExpresion('mayor() necesita el campo que devolver como tercer argumento');
      var mejor = -1;
      for (var i = 0; i < valores.length; i++) if (valores[i] !== null && (mejor < 0 || valores[i] > valores[mejor])) mejor = i;
      return mejor < 0 ? null : (lista[mejor][args[2].n] === undefined ? null : lista[mejor][args[2].n]);
    }
    if (n === 'si') {
      if (args.length !== 3) throw new ErrorExpresion('si() necesita 3 argumentos: condición, valor si se cumple, valor si no');
      return verdad(evaluar(args[0], buscar)) ? evaluar(args[1], buscar) : evaluar(args[2], buscar);
    }
    var v = args.map(function (a) { return num(evaluar(a, buscar)); });
    if (n === 'min' || n === 'max') {
      var ok = v.filter(function (x) { return x !== null; });
      if (!ok.length) return null;
      return n === 'min' ? Math.min.apply(null, ok) : Math.max.apply(null, ok);
    }
    if (n === 'abs') return v[0] === null || v[0] === undefined ? null : Math.abs(v[0]);
    if (n === 'redondear') {
      if (v[0] === null || v[0] === undefined) return null;
      var d = v.length > 1 && v[1] !== null ? v[1] : 0;
      var f = Math.pow(10, d);
      return Math.round(v[0] * f) / f;
    }
    if (n === 'limitar') {
      if (v.length !== 3) throw new ErrorExpresion('limitar() necesita 3 argumentos: valor, mínimo y máximo');
      if (v[0] === null) return null;
      return Math.min(Math.max(v[0], v[1] === null ? v[0] : v[1]), v[2] === null ? v[0] : v[2]);
    }
    throw new ErrorExpresion('Función desconocida «' + n + '»');
  }

  /** Atajo: evalúa un texto con un objeto de variables. */
  function calcularExpresion(texto, variables) {
    var arbol = parsear(texto);
    return evaluar(arbol, function (nombre) {
      if (variables && Object.prototype.hasOwnProperty.call(variables, nombre)) return variables[nombre];
      throw new ErrorExpresion('Variable desconocida «' + nombre + '»');
    });
  }

  // ───────────────────────── cálculo del diagnóstico ─────────────────────────
  /** Valor numérico de una respuesta: opción → su «valor», número → número, texto → texto, grupo → lista. */
  function valorRespuesta(pregunta, r) {
    if (pregunta.tipo === 'grupo') {
      return (r || []).map(function (item) {
        var out = {};
        (pregunta.campos || []).forEach(function (c) { out[c.id] = valorRespuesta(c, item[c.id]); });
        return out;
      });
    }
    if (pregunta.tipo === 'opciones') {
      var op = (pregunta.opciones || [])[r];
      return op ? op.valor : null;
    }
    if (pregunta.tipo === 'numero') return numEntrada(r);
    return r === undefined ? '' : r;
  }

  /**
   * Resultado del diagnóstico. respuestas: {id: índice de opción | número | texto | [ {campo: …} ]}.
   * supuestos: {id: valor} para sustituir los del config (los que el usuario edite en pantalla).
   * Devuelve {valores: {id: valor}, nivel: id, nivelConfig: {...}}.
   */
  function calcular(cfg, respuestas, supuestos) {
    var vars = {};
    (cfg.supuestos || []).forEach(function (s) {
      var propio = supuestos ? numEntrada(supuestos[s.id]) : null;
      vars[s.id] = propio !== null ? propio : s.valor;
    });
    (cfg.preguntas || []).forEach(function (p) { vars[p.id] = valorRespuesta(p, (respuestas || {})[p.id]); });
    function buscar(nombre) {
      if (Object.prototype.hasOwnProperty.call(vars, nombre)) return vars[nombre];
      throw new ErrorExpresion('Variable desconocida «' + nombre + '»');
    }
    var valores = {};
    (cfg.calculos || []).forEach(function (c) {
      var v = evaluar(parsear(c.formula), buscar);
      if (typeof v === 'number' && c.redondeo) v = Math.round(v / c.redondeo) * c.redondeo;
      vars[c.id] = v;
      valores[c.id] = v;
    });
    var elegido = null;
    var niveles = cfg.niveles || [];
    for (var i = 0; i < niveles.length; i++) {
      if (!niveles[i].si || verdad(evaluar(parsear(niveles[i].si), buscar))) { elegido = niveles[i]; break; }
    }
    if (!elegido && niveles.length) elegido = niveles[niveles.length - 1];
    return { valores: valores, variables: vars, nivel: elegido ? elegido.id : '', nivelConfig: elegido };
  }

  // ───────────────────────── formato en español ─────────────────────────
  function agrupar(entero) {
    var s = String(entero);
    if (s.length <= 3) return s; /* con miles siempre agrupados, los rangos se leen igual («9.500 y 16.000») */
    return s.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  }

  function numeroES(n, decimales) {
    var d = decimales === undefined ? (Math.abs(n) < 10 && n % 1 !== 0 ? 1 : 0) : decimales;
    var negativo = n < 0;
    var fijo = Math.abs(n).toFixed(d);
    var partes = fijo.split('.');
    var texto = agrupar(partes[0]) + (partes[1] && Number(partes[1]) !== 0 ? ',' + partes[1] : '');
    return (negativo ? '−' : '') + texto;
  }

  function formatear(valor, formato, unidad, moneda) {
    if (valor === null || valor === undefined || valor === '') return '—';
    if (typeof valor === 'string') return valor;
    var v = Number(valor);
    if (!isFinite(v)) return '—';
    switch (formato) {
      case 'eur':
      case 'moneda': {
        var simbolo = { EUR: '€', USD: 'US$', GBP: '£', MXN: 'MXN', COP: 'COP', ARS: 'ARS', CLP: 'CLP' }[moneda || 'EUR'] || (moneda || '€');
        return numeroES(Math.round(v), 0) + ' ' + simbolo;
      }
      case 'horas': return numeroES(v) + ' h';
      case 'pct': return numeroES(v * 100, Math.abs(v * 100) < 10 && (v * 100) % 1 !== 0 ? 1 : 0) + ' %';
      case 'meses': {
        var m = Math.round(v * 10) / 10;
        return numeroES(m, m % 1 === 0 ? 0 : 1) + (m === 1 ? ' mes' : ' meses');
      }
      default: return numeroES(v) + (unidad ? ' ' + unidad : '');
    }
  }

  /** Sustituye {id}, {id_min} y {id_max} por valores formateados. */
  function rellenar(texto, valores, defs, moneda, incertidumbre) {
    return String(texto || '').replace(/\{([a-z_][a-z0-9_]*)\}/g, function (todo, clave) {
      var base = clave;
      var factor = 1;
      if (/_min$/.test(clave) && !(clave in valores)) { base = clave.slice(0, -4); factor = 1 - (incertidumbre || 0); }
      else if (/_max$/.test(clave) && !(clave in valores)) { base = clave.slice(0, -4); factor = 1 + (incertidumbre || 0); }
      if (!(base in valores)) return todo;
      var def = defs[base] || {};
      var v = valores[base];
      if (typeof v === 'number' && factor !== 1) v = redondearBonito(v * factor);
      return formatear(v, def.formato, def.unidad, moneda);
    });
  }

  /** Redondeo para rangos: dos cifras significativas («entre 18.000 y 29.000 €», no «entre 18.137 y 29.402 €»). */
  function redondearBonito(v) {
    if (!isFinite(v) || v === 0) return v;
    var e = Math.pow(10, Math.max(0, Math.floor(Math.log(Math.abs(v)) / Math.LN10) - 1));
    return Math.round(v / e) * e;
  }

  // ───────────────────────── interfaz ─────────────────────────
  function iniciar(w, d) {
    function arrancar() {
      var P = w.PaginasOS;
      var raizDiag = d.querySelector('[data-pos-diag]');
      if (!P || !raizDiag) return;
      var cfgPagina = (P.estado().cfg.pagina || {});
      var cfg = cfgPagina.diagnostico;
      if (!cfg) return;
      var moneda = P.estado().cfg.moneda || 'EUR';
      var defs = {};
      (cfg.calculos || []).forEach(function (c) { defs[c.id] = c; });
      (cfg.supuestos || []).forEach(function (s) { defs[s.id] = s; });

      var intro = raizDiag.querySelector('[data-pos-diag-intro]');
      var panel = raizDiag.querySelector('[data-pos-diag-panel]');
      var formPreguntas = raizDiag.querySelector('[data-pos-diag-preguntas]');
      var pasos = raizDiag.querySelectorAll('[data-pos-paso]');
      var contacto = raizDiag.querySelector('[data-pos-diag-contacto]');
      var bloqueResultado = raizDiag.querySelector('[data-pos-diag-resultado]');
      var botonAtras = raizDiag.querySelector('[data-pos-diag-atras]');
      var botonSiguiente = raizDiag.querySelector('[data-pos-diag-siguiente]');
      var textoProgreso = raizDiag.querySelector('[data-pos-progreso-texto]');
      var barra = raizDiag.querySelector('[role="progressbar"]');
      var relleno = raizDiag.querySelector('[data-pos-progreso-relleno]');
      var antes = cfg.captura !== 'despues';
      var total = pasos.length + (antes ? 1 : 0);
      var actual = 0;
      var enContacto = false;
      var resultado = null;
      var supuestosUsuario = {};
      var idCompletado = '';
      var completadoDisparado = false;
      var preguntas = {};
      (cfg.preguntas || []).forEach(function (p) { preguntas[p.id] = p; });

      function progreso(i) {
        var hechos = Math.min(i, total);
        if (textoProgreso) textoProgreso.textContent = i >= pasos.length ? 'Último paso' : 'Pregunta ' + (i + 1) + ' de ' + pasos.length;
        if (barra) barra.setAttribute('aria-valuenow', String(hechos));
        if (relleno) relleno.style.transform = 'scaleX(' + (total ? hechos / total : 0) + ')';
      }

      function mostrarPaso(i, enfocar) {
        actual = i;
        enContacto = false;
        for (var k = 0; k < pasos.length; k++) pasos[k].hidden = k !== i;
        formPreguntas.hidden = false;
        if (contacto) contacto.hidden = true;
        botonAtras.hidden = i === 0 && !intro;
        botonSiguiente.textContent = i === pasos.length - 1 ? (antes ? 'Ver mi resultado' : 'Calcular') : 'Siguiente';
        progreso(i);
        if (enfocar !== false) {
          var titulo = pasos[i].querySelector('.pos-paso__pregunta');
          if (titulo) titulo.focus();
        }
      }

      function leerRespuesta(paso) {
        var id = paso.getAttribute('data-pregunta');
        var p = preguntas[id];
        if (!p) return { id: id, valor: undefined };
        if (p.tipo === 'grupo') {
          var items = paso.querySelectorAll('[data-pos-grupo-item]');
          var lista = [];
          for (var i = 0; i < items.length; i++) lista.push(leerCamposItem(items[i], p.campos || []));
          return { id: id, valor: lista };
        }
        return { id: id, valor: leerCampo(paso, p) };
      }

      function leerCampo(contenedor, p) {
        if (p.tipo === 'opciones') {
          var marcada = contenedor.querySelector('input[type="radio"][data-campo="' + p.id + '"]:checked');
          return marcada ? Number(marcada.value) : undefined;
        }
        var input = contenedor.querySelector('[data-campo="' + p.id + '"]');
        if (!input) return undefined;
        var v = String(input.value || '').trim();
        if (p.tipo === 'numero') { var n = numEntrada(v); return n === null ? (v === '' ? undefined : null) : n; }
        return v;
      }

      function leerCamposItem(item, campos) {
        var out = {};
        campos.forEach(function (c) { out[c.id] = leerCampo(item, c); });
        return out;
      }

      function errorDe(p, valor) {
        if (p.tipo === 'opciones') return valor === undefined && p.requerido !== false ? 'Elige una opción para seguir.' : '';
        if (p.tipo === 'numero') {
          if (valor === null) return 'Escribe solo el número (por ejemplo, 12 o 2,5).';
          if (valor === undefined) return p.requerido !== false ? 'Escribe un número para seguir.' : '';
          if (p.min !== undefined && valor < p.min) return 'El mínimo es ' + numeroES(p.min) + '.';
          if (p.max !== undefined && valor > p.max) return 'El máximo es ' + numeroES(p.max) + '. Si es más, pon el máximo y lo vemos en la llamada.';
          return '';
        }
        if (p.tipo === 'texto') return !valor && p.requerido ? 'Escribe una respuesta corta para seguir.' : '';
        return '';
      }

      function validarPaso(paso) {
        var id = paso.getAttribute('data-pregunta');
        var p = preguntas[id];
        var r = leerRespuesta(paso);
        var mensaje = '';
        if (p.tipo === 'grupo') {
          var items = paso.querySelectorAll('[data-pos-grupo-item]');
          for (var i = 0; i < items.length && !mensaje; i++) {
            for (var k = 0; k < (p.campos || []).length && !mensaje; k++) {
              var c = p.campos[k];
              var e = errorDe(c, r.valor[i][c.id]);
              if (e) mensaje = (p.etiqueta_item || 'Elemento') + ' ' + (i + 1) + ': ' + e.charAt(0).toLowerCase() + e.slice(1);
            }
          }
          if (!mensaje && items.length < (p.min_items || 1)) mensaje = 'Añade al menos ' + (p.min_items || 1) + '.';
        } else {
          mensaje = errorDe(p, r.valor);
        }
        var nodo = paso.querySelector('[data-pos-paso-error]');
        if (nodo) nodo.textContent = mensaje;
        return !mensaje;
      }

      function todasLasRespuestas() {
        var out = {};
        for (var i = 0; i < pasos.length; i++) {
          var r = leerRespuesta(pasos[i]);
          out[r.id] = r.valor;
        }
        return out;
      }

      function respuestasLegibles(resp) {
        var out = {};
        var resumen = [];
        (cfg.preguntas || []).forEach(function (p) {
          var r = resp[p.id];
          if (p.tipo === 'opciones') {
            var op = (p.opciones || [])[r];
            out[p.id] = op ? { etiqueta: op.etiqueta, valor: op.valor } : null;
            if (op) resumen.push((p.corta || p.id) + ': ' + op.etiqueta);
          } else if (p.tipo === 'grupo') {
            out[p.id] = (r || []).map(function (item) {
              var o = {};
              (p.campos || []).forEach(function (c) {
                if (c.tipo === 'opciones') {
                  var opc = (c.opciones || [])[item[c.id]];
                  o[c.id] = opc ? opc.etiqueta : null;
                  o[c.id + '_valor'] = opc ? opc.valor : null;
                } else {
                  o[c.id] = item[c.id] === undefined ? null : item[c.id];
                }
              });
              return o;
            });
            (r || []).forEach(function (item, i) {
              var partes = (p.campos || []).map(function (c) {
                var v = c.tipo === 'opciones' ? ((c.opciones || [])[item[c.id]] || {}).etiqueta : item[c.id];
                if (v === undefined || v === null || v === '') return null;
                return c.tipo === 'texto' ? String(v) : (c.corta || c.id) + ' ' + v;
              }).filter(Boolean);
              resumen.push((p.etiqueta_item || p.id) + ' ' + (i + 1) + ': ' + partes.join(', '));
            });
          } else {
            out[p.id] = r === undefined ? null : r;
            if (r !== undefined && r !== '') resumen.push((p.corta || p.id) + ': ' + r);
          }
        });
        return { respuestas: out, resumen: resumen.join('; ') };
      }

      function completar() {
        var resp = todasLasRespuestas();
        resultado = calcular(cfg, resp, supuestosUsuario);
        if (!idCompletado) idCompletado = P.eventId('DiagnosticoCompletado', w.crypto);
        return resp;
      }

      function valorEvento(nivel) {
        var tabla = cfg.valor_evento || {};
        return Object.prototype.hasOwnProperty.call(tabla, nivel) ? num(tabla[nivel]) : null;
      }

      function dispararCompletado() {
        if (completadoDisparado || !resultado) return;
        completadoDisparado = true;
        var v = valorEvento(resultado.nivel);
        P.evento('DiagnosticoCompletado', v === null ? {} : { value: v, currency: moneda }, idCompletado);
      }

      function pintarResultado() {
        if (!resultado || !bloqueResultado) return;
        var inc = cfg.resultado && cfg.resultado.incertidumbre ? Number(cfg.resultado.incertidumbre) : 0;
        var principal = cfg.resultado ? cfg.resultado.principal : '';
        var def = defs[principal] || {};
        var v = resultado.valores[principal];
        var cifra = bloqueResultado.querySelector('[data-pos-r-cifra]');
        var rango = bloqueResultado.querySelector('[data-pos-r-rango]');
        if (cifra) cifra.textContent = formatear(v, def.formato, def.unidad, moneda);
        if (rango) {
          rango.textContent = inc && typeof v === 'number' && v > 0
            ? 'Rango razonable con tus respuestas: entre ' + formatear(redondearBonito(v * (1 - inc)), def.formato, def.unidad, moneda) +
              ' y ' + formatear(redondearBonito(v * (1 + inc)), def.formato, def.unidad, moneda) + '.'
            : '';
        }
        var celdas = bloqueResultado.querySelectorAll('[data-pos-r-valor]');
        for (var i = 0; i < celdas.length; i++) {
          var id = celdas[i].getAttribute('data-pos-r-valor');
          var dd = defs[id] || {};
          celdas[i].textContent = formatear(resultado.valores[id], dd.formato, dd.unidad, moneda);
        }
        var n = resultado.nivelConfig || {};
        var rec = bloqueResultado.querySelector('[data-pos-r-recomendacion]');
        if (rec) {
          rec.setAttribute('data-nivel', resultado.nivel);
          rec.setAttribute('data-nivel-tono', n.tono || 'bajo');
          var titulo = rec.querySelector('[data-pos-r-titulo]');
          var texto = rec.querySelector('[data-pos-r-texto]');
          if (titulo) titulo.textContent = rellenar(n.titulo, resultado.valores, defs, moneda, inc);
          if (texto) texto.textContent = rellenar(n.texto, resultado.valores, defs, moneda, inc);
          ponerCta(rec.querySelector('[data-pos-r-cta]'), n.cta);
          ponerCta(rec.querySelector('[data-pos-r-cta2]'), n.cta_secundario);
        }
      }

      function ponerCta(nodo, cta) {
        if (!nodo) return;
        if (!cta || !cta.texto || !cta.href) { nodo.hidden = true; return; }
        nodo.hidden = false;
        nodo.textContent = cta.texto;
        var extra = {};
        var est = P.estado();
        P.PARAMS.forEach(function (k) { if (est.atribucion[k]) extra[k] = est.atribucion[k]; });
        extra.nivel = resultado.nivel;
        var ref = d.querySelector('form[data-pos-formulario="diagnostico"]');
        if (ref && ref.getAttribute('data-event-id')) extra.ref = ref.getAttribute('data-event-id');
        nodo.setAttribute('href', P.esInterno(cta.href, w.location.host) ? P.decorar(cta.href, extra) : cta.href);
      }

      function mostrarResultado() {
        pintarResultado();
        if (intro) intro.hidden = true;
        if (panel) panel.hidden = true;
        bloqueResultado.hidden = false;
        if (!antes && contacto) contacto.hidden = false;
        var t = bloqueResultado.querySelector('[data-pos-r-foco]') || bloqueResultado.querySelector('[data-pos-r-titulo]');
        if (bloqueResultado.scrollIntoView) bloqueResultado.scrollIntoView({ block: 'start' });
        if (t) t.focus();
      }

      function irAContacto() {
        enContacto = true;
        for (var k = 0; k < pasos.length; k++) pasos[k].hidden = true;
        formPreguntas.hidden = true;
        contacto.hidden = false;
        progreso(pasos.length);
        var titulo = contacto.querySelector('.pos-formulario__titulo, h2');
        if (titulo) { titulo.setAttribute('tabindex', '-1'); titulo.focus(); }
      }

      // ── extensiones del formulario de contacto (paginas.js las llama al enviar) ──
      P.extender('diagnostico', {
        preparar: function () {
          var resp = completar();
          var legibles = respuestasLegibles(resp);
          var v = valorEvento(resultado.nivel);
          var eventos = [];
          var comp = { event_name: 'DiagnosticoCompletado', event_id: idCompletado };
          if (v !== null) { comp.value = v; comp.currency = moneda; }
          if (completadoDisparado) comp.navegador = false;
          eventos.push(comp);
          var cual = cfg.cualificado || {};
          if (cual.activo && (cual.niveles || []).indexOf(resultado.nivel) >= 0) {
            eventos.push({ event_name: 'LeadCualificado', event_id: P.eventId('LeadCualificado', w.crypto) });
          }
          if (!antes) completadoDisparado = true;
          var principal = cfg.resultado ? cfg.resultado.principal : '';
          return {
            eventos: eventos,
            respuestas: legibles.respuestas,
            diagnostico: {
              nivel: resultado.nivel,
              principal: principal,
              valor_principal: resultado.valores[principal] === undefined ? null : resultado.valores[principal],
              resultados: resultado.valores,
              supuestos: (cfg.supuestos || []).reduce(function (o, s) { o[s.id] = resultado.variables[s.id]; return o; }, {}),
              supuestos_editados: Object.keys(supuestosUsuario),
              resumen: legibles.resumen,
              cualificado_automatico: eventos.some(function (e) { return e.event_name === 'LeadCualificado'; })
            },
            parametros: { nivel: resultado.nivel }
          };
        },
        alEnviar: function () {
          if (!antes) return undefined; /* después del resultado: sigue al destino del formulario (la reserva) */
          completadoDisparado = true;
          mostrarResultado();
          return false;
        }
      });

      // ── eventos de la interfaz ──
      function empezar(desde) {
        if (intro) intro.hidden = true;
        panel.hidden = false;
        mostrarPaso(desde || 0);
      }

      var botonEmpezar = raizDiag.querySelector('[data-pos-diag-empezar]');
      if (botonEmpezar) botonEmpezar.addEventListener('click', function () { empezar(0); });

      formPreguntas.addEventListener('submit', function (e) {
        e.preventDefault();
        if (!validarPaso(pasos[actual])) {
          var err = pasos[actual].querySelector('[data-pos-paso-error]');
          var primero = pasos[actual].querySelector('input, select, textarea');
          if (err && err.textContent && primero) primero.focus();
          return;
        }
        if (actual < pasos.length - 1) { mostrarPaso(actual + 1); return; }
        completar();
        if (antes) { irAContacto(); return; }
        dispararCompletado();
        mostrarResultado();
      });

      // captura después: volver a las preguntas desde el resultado
      var revisar = raizDiag.querySelector('[data-pos-diag-revisar]');
      if (revisar) revisar.addEventListener('click', function () {
        bloqueResultado.hidden = true;
        if (contacto) contacto.hidden = true;
        panel.hidden = false;
        mostrarPaso(0);
      });

      botonAtras.addEventListener('click', function () {
        if (enContacto) { mostrarPaso(pasos.length - 1); return; }
        if (actual > 0) { mostrarPaso(actual - 1); return; }
        if (intro) { panel.hidden = true; intro.hidden = false; var h = intro.querySelector('h1'); if (h) { h.setAttribute('tabindex', '-1'); h.focus(); } }
      });
      var atrasContacto = contacto ? contacto.querySelector('[data-pos-diag-atras-contacto]') : null;
      if (atrasContacto) atrasContacto.addEventListener('click', function () { panel.hidden = false; mostrarPaso(pasos.length - 1); });

      // opciones: avanzan solas al tocarlas con el dedo o el ratón (con teclado se usa «Siguiente»)
      raizDiag.addEventListener('click', function (e) {
        var op = e.target.closest ? e.target.closest('.pos-opcion') : null;
        if (!op || !e.detail || op.closest('[data-pos-grupo-item]')) return;
        var paso = op.closest('[data-pos-paso]');
        if (!paso || paso.hidden || paso.querySelectorAll('.pos-opciones').length !== 1) return;
        setTimeout(function () {
          if (!paso.hidden && validarPaso(paso)) {
            if (formPreguntas.requestSubmit) formPreguntas.requestSubmit();
            else botonSiguiente.click();
          }
        }, 220);
      });

      // números: botones − y +
      raizDiag.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-pos-paso-num]') : null;
        if (!b) return;
        var input = b.parentNode.querySelector('input');
        var paso = num(input.getAttribute('data-paso')) || 1;
        var v = numEntrada(input.value);
        if (v === null) v = num(input.getAttribute('data-defecto')) || 0;
        v = v + (b.getAttribute('data-pos-paso-num') === '+' ? paso : -paso);
        var min = num(input.getAttribute('data-min'));
        var max = num(input.getAttribute('data-max'));
        if (min !== null && v < min) v = min;
        if (max !== null && v > max) v = max;
        input.value = String(Math.round(v * 100) / 100).replace('.', ',');
        input.dispatchEvent(new w.Event('input', { bubbles: true }));
      });

      // grupos repetibles (p. ej. procesos)
      var contadores = {};
      function renumerar(lista) {
        var items = lista.querySelectorAll('[data-pos-grupo-item]');
        for (var i = 0; i < items.length; i++) {
          var marcas = items[i].querySelectorAll('[data-pos-grupo-numero]');
          for (var n = 0; n < marcas.length; n++) marcas[n].textContent = String(i + 1);
          var quitar = items[i].querySelector('[data-pos-grupo-quitar]');
          if (quitar) quitar.hidden = items.length <= 1;
        }
        var grupo = lista.closest('[data-pos-paso]');
        var p = preguntas[grupo.getAttribute('data-pregunta')] || {};
        var anadir = grupo.querySelector('[data-pos-grupo-anadir]');
        if (anadir) anadir.hidden = items.length >= (p.max_items || 5);
      }
      raizDiag.addEventListener('click', function (e) {
        var anadir = e.target.closest ? e.target.closest('[data-pos-grupo-anadir]') : null;
        var quitar = e.target.closest ? e.target.closest('[data-pos-grupo-quitar]') : null;
        if (anadir) {
          var paso = anadir.closest('[data-pos-paso]');
          var plantilla = paso.querySelector('template[data-pos-grupo-plantilla]');
          var lista = paso.querySelector('[data-pos-grupo-lista]');
          var id = paso.getAttribute('data-pregunta');
          contadores[id] = (contadores[id] || lista.querySelectorAll('[data-pos-grupo-item]').length) + 1;
          var html = plantilla.innerHTML.replace(/__i__/g, String(contadores[id]));
          var caja = d.createElement('div');
          caja.innerHTML = html;
          var nuevo = caja.firstElementChild;
          lista.appendChild(nuevo);
          renumerar(lista);
          var primero = nuevo.querySelector('input');
          if (primero) primero.focus();
        } else if (quitar) {
          var item = quitar.closest('[data-pos-grupo-item]');
          var l = item.parentNode;
          var anterior = item.previousElementSibling;
          l.removeChild(item);
          renumerar(l);
          var foco = anterior ? anterior.querySelector('input') : l.querySelector('input');
          if (foco) foco.focus();
        }
      });
      var listas = raizDiag.querySelectorAll('[data-pos-grupo-lista]');
      for (var g = 0; g < listas.length; g++) renumerar(listas[g]);

      // supuestos editables: recalculan al momento
      var editables = raizDiag.querySelectorAll('[data-pos-supuesto]');
      for (var s = 0; s < editables.length; s++) {
        editables[s].addEventListener('input', function (e) {
          var id = e.target.getAttribute('data-pos-supuesto');
          var v = numEntrada(e.target.value);
          if (v !== null && (defs[id] || {}).formato === 'pct') v = v / 100;
          if (v === null) delete supuestosUsuario[id];
          else supuestosUsuario[id] = v;
          if (resultado) { completar(); pintarResultado(); }
        });
      }

      if (!intro && panel) { panel.hidden = false; mostrarPaso(0, false); }

      // arranque desde la landing: ?r_<pregunta>=<índice de opción>
      var m = /[?&]r_([a-z0-9_]+)=(\d+)/.exec(w.location.search);
      if (m && pasos.length) {
        var primero = pasos[0];
        if (primero.getAttribute('data-pregunta') === m[1]) {
          var radio = primero.querySelector('input[type="radio"][value="' + m[2] + '"]');
          if (radio) { radio.checked = true; empezar(pasos.length > 1 ? 1 : 0); }
        }
      }
      d.documentElement.classList.add('pos-diag-listo');
    }
    if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', arrancar);
    else arrancar();
  }

  return {
    tokenizar: tokenizar, parsear: parsear, evaluar: evaluar, calcularExpresion: calcularExpresion,
    calcular: calcular, valorRespuesta: valorRespuesta, formatear: formatear, numeroES: numeroES, rellenar: rellenar,
    num: num, numEntrada: numEntrada,
    redondearBonito: redondearBonito, ErrorExpresion: ErrorExpresion, iniciar: iniciar
  };
});
