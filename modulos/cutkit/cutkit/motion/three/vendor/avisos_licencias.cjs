// Escribe los avisos de licencia de las dependencias (transitivas) de un paquete npm, con el texto literal de cada
// LICENSE/NOTICE. Lo usa build.sh tras compilar los bundles. Uso: node avisos_licencias.cjs <node_modules> <paquete> <salida>
"use strict";
const fs = require("fs");
const path = require("path");

const [nm, raiz, salida] = process.argv.slice(2);
const leer = (dir) => JSON.parse(fs.readFileSync(path.join(nm, dir, "package.json"), "utf8"));
const visto = new Set();
const partes = [];

function recorrer(nombre) {
  if (visto.has(nombre)) return;
  visto.add(nombre);
  const dir = path.join(nm, nombre);
  const pkg = leer(nombre);
  const autor = typeof pkg.author === "string" ? pkg.author : (pkg.author && pkg.author.name) || "";
  const archivos = fs.readdirSync(dir).filter((f) => /^(licen[cs]e|copying|notice)/i.test(f)).sort();
  const texto = archivos.length
    ? archivos.map((f) => fs.readFileSync(path.join(dir, f), "utf8").trim()).join("\n\n")
    : `(el paquete no incluye archivo de licencia; su package.json declara «${pkg.license}»${autor ? ` y autor «${autor}»` : ""})`;
  partes.push(`${"=".repeat(100)}\n${nombre} ${pkg.version} (${pkg.license})\n${pkg.homepage || ""}\n\n${texto}\n`);
  for (const dep of Object.keys(pkg.dependencies || {}).sort()) recorrer(dep);
}

const base = leer(raiz);
for (const dep of Object.keys(base.dependencies || {}).sort()) recorrer(dep);
fs.writeFileSync(salida, `Avisos de licencia de las dependencias de ${raiz} ${base.version} incluidas en su bundle de cutkit.\n` +
  `Generado por build.sh (avisos_licencias.cjs); no lo edites a mano.\n\n${partes.join("\n")}`);
console.log(`${salida}: ${partes.length} paquetes`);
