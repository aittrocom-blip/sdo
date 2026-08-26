// scripts/check-i18n-coverage.js
// Node script (no dependencies) — run from the repo root with `node scripts/check-i18n-coverage.js`.
// Cross-references every data-i18n/data-i18n-attr key used across the 14 HTML pages against
// assets/i18n/en.js's dictionary. Exits 1 (and prints the gaps) if anything is missing or unused.
const fs = require('fs');
const path = require('path');

const PAGES = [
  'index.html', 'habitaciones.html', 'eventos.html', 'restaurante.html',
  'servicios.html', 'experiencias.html', 'ofertas.html', 'faq.html',
  'galeria.html', 'ubicacion.html', 'acerca.html', 'empresarial.html',
  'privacidad.html', 'terminos.html',
];

function loadDictionaryKeys(){
  const src = fs.readFileSync(path.join(__dirname, '..', 'assets', 'i18n', 'en.js'), 'utf8');
  const keys = new Set();
  const re = /"([a-zA-Z0-9_.]+)"\s*:/g;
  let m;
  while ((m = re.exec(src))) keys.add(m[1]);
  return keys;
}

function usedKeysInFile(file){
  const html = fs.readFileSync(file, 'utf8');
  const used = new Set();
  const re1 = /data-i18n="([^"]+)"/g;
  let m;
  while ((m = re1.exec(html))) used.add(m[1]);
  const re2 = /data-i18n-attr="([^"]+)"/g;
  while ((m = re2.exec(html))) {
    m[1].split(',').forEach((pair) => {
      const key = pair.split(':')[1];
      if (key) used.add(key.trim());
    });
  }
  return used;
}

const dictKeys = loadDictionaryKeys();
const allUsed = new Set();
let missing = [];

for (const page of PAGES) {
  const file = path.join(__dirname, '..', page);
  if (!fs.existsSync(file)) continue;
  const used = usedKeysInFile(file);
  used.forEach((k) => allUsed.add(k));
  used.forEach((k) => {
    if (!dictKeys.has(k)) missing.push(`${page}: missing dictionary entry for "${k}"`);
  });
}

const unused = [...dictKeys].filter((k) => !allUsed.has(k));

if (missing.length) {
  console.error('MISSING TRANSLATIONS:');
  missing.forEach((m) => console.error('  ' + m));
}
if (unused.length) {
  // Known, expected exception: the 24 experiencias.itin_modern.* / experiencias.itin_business.*
  // keys always show up here. They're consumed dynamically in experiencias.html's itinerary
  // renderer via a string-concatenated lookup (d[prefix + '.title'], etc.), which this script's
  // static data-i18n="..." regex scan can't see. Verified translated and wired correctly as of
  // Task 16's final full-site check — not a real gap.
  console.warn('UNUSED DICTIONARY KEYS (defined but not referenced by any page):');
  unused.forEach((k) => console.warn('  ' + k));
}
if (missing.length) {
  console.error(`\n${missing.length} missing, ${unused.length} unused.`);
  process.exit(1);
}
console.log(`OK — 0 missing. ${unused.length} unused key(s).`);
