# Site EN/ES Translation Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing (currently inert) `ES / EN` selector in the header actually work — clicking `EN` translates the whole page to English in place with no reload (switching back to `ES` reloads, restoring the page's always-Spanish HTML source — see Task 1 Step 2 for why), the choice persists across the site's 14 pages, and every page ends up fully bilingual.

**Architecture:** Translatable elements get a `data-i18n="key"` (text) or `data-i18n-attr="attr:key"` (attributes) marker. A single combined dictionary (`assets/i18n/en.js`, `window.I18N_EN = {...}`) holds every English string, keyed `common.*` for content shared across all 14 pages (nav, mega-menus, footer, reserve bar) and `<page>.*` for page-specific content. A small engine in `assets/scripts.js` reads/writes the chosen language to `localStorage`, applies the swap on load and on toggle click, and exposes `window.getSiteLang()` for other scripts (the AI Concierge widget, in a later plan) to read the current language. No build step, no bundler — plain `<script>` tags, matching every other asset on this site.

**Tech Stack:** Vanilla HTML/CSS/JS (no framework, no build step — same as the rest of this site), `localStorage` for persistence, Node.js + Playwright for verification (already used elsewhere in this project; no other test tooling exists for this static frontend).

**Spec:** `docs/superpowers/specs/2026-08-21-site-i18n-en-toggle-design.md`

## Global Constraints

- Key naming: `common.<slug>` for content identical across all 14 pages (nav, mega-menus, footer, mobile-nav, reserve bar); `<page>.<slug>` for page-specific content, where `<page>` is the HTML file's basename without extension (e.g. `index`, `habitaciones`, `faq`).
- `localStorage` key: `site_lang`, values `"es"` (default) or `"en"`. Wrap every read/write in `try/catch` — never let a `localStorage` failure (private browsing, disabled storage) break page load; fall back to `"es"`.
- Missing dictionary key: leave the existing Spanish text untouched (never blank/`undefined`), log one `console.warn` per missing key — never throw, never interrupt the guest.
- Do not translate: proper nouns (Sol de Oro, Miraflores, Restaurante Murano), phone numbers, emails, addresses, and any URL/href value.
- Do translate: all visible text, `alt` on content-relevant images, `placeholder`/`aria-label`/`title` attributes that carry guest-facing copy, and each page's `<meta name="description">`.
- The 14 pages in scope (repo root, one HTML file each): `index.html`, `habitaciones.html`, `eventos.html`, `restaurante.html`, `servicios.html`, `experiencias.html`, `ofertas.html`, `faq.html`, `galeria.html`, `ubicacion.html`, `acerca.html`, `empresarial.html`, `privacidad.html`, `terminos.html`.
- Every page task's Step "Run coverage check" must show **zero** missing keys for that file before the task is considered done — this is the objective completion gate, not a subjective "looks translated" judgment.
- Tone: warm but formal five-star hotel voice, matching the Spanish original — not machine-translation-literal, not casual. When in doubt, match the register of the `common.*` translations written in Task 1 (they set the tone baseline).

---

### Task 1: i18n engine, dictionary skeleton, coverage-check script, and toggle markup across all 14 pages

**Files:**
- Create: `assets/i18n/en.js`
- Create: `scripts/check-i18n-coverage.js` (not shipped to the site — a local Node verification script, run from the repo root)
- Modify: `assets/scripts.js`
- Modify: all 14 pages listed in Global Constraints (only the `ES / EN` toggle markup, both the desktop header and the mobile-nav-footer copy)

**Interfaces:**
- Produces: `window.getSiteLang()` → `"es" | "en"`. `window.applyI18n(lang)` → applies `data-i18n`/`data-i18n-attr` swaps for the given language across the current page (idempotent, safe to call more than once). `window.I18N_EN` → the dictionary object, keyed as described in Global Constraints. Later page tasks (2–15) add keys to this same object; they never redefine `common.*` keys already set here.
- Consumes: nothing from earlier tasks (this is the foundation).

- [ ] **Step 1: Write `assets/i18n/en.js` with the full `common.*` dictionary**

This covers every string in the shared header (nav links + both mega-menus), footer, mobile nav, and the reservation bar (including the guest-count panel added earlier). Content transcribed from `index.html`'s current header/footer/reserve-bar markup — identical across all 14 pages.

```javascript
// assets/i18n/en.js
// English translations for the site's ES/EN toggle. Keys prefixed "common."
// are shared across all 14 pages (nav, mega-menus, footer, reserve bar).
// Keys prefixed "<page>." are specific to one page — see docs/superpowers/
// specs/2026-08-21-site-i18n-en-toggle-design.md for the key-naming rule.
window.I18N_EN = {
  // ---- common: header nav + mega-menus ----
  "common.nav.rooms": "Rooms",
  "common.nav.rooms_mega.eyebrow": "Rooms",
  "common.nav.rooms_mega.title": "Nine categories to feel at home.",
  "common.nav.rooms_mega.stat_types": "room types",
  "common.nav.rooms_mega.stat_units": "units",
  "common.nav.rooms_mega.intro": "From the Standard to the Grand Deluxe Suite. High-speed WiFi, marble bathrooms and natural Miraflores light.",
  "common.nav.rooms_mega.cta": "View all rooms",
  "common.nav.rooms_mega.card1_tag": "01 · Essential",
  "common.nav.rooms_mega.card1_name": "Standard",
  "common.nav.rooms_mega.card1_meta": "25 m² · double bed",
  "common.nav.rooms_mega.card2_tag": "02 · Comfort",
  "common.nav.rooms_mega.card2_name": "Superior King",
  "common.nav.rooms_mega.card2_meta": "27 m² · king bed",
  "common.nav.rooms_mega.card3_tag": "03 · Suite",
  "common.nav.rooms_mega.card3_name": "Junior Suite",
  "common.nav.rooms_mega.card3_meta": "40 m² · king bed",
  "common.nav.rooms_mega.card4_tag": "04 · Premium",
  "common.nav.rooms_mega.card4_name": "Grand Deluxe",
  "common.nav.rooms_mega.card4_meta": "68 m² · Pacific view",

  "common.nav.salons": "Salons",
  "common.nav.salons_mega.eyebrow": "Salons & Events",
  "common.nav.salons_mega.title": "Capacity for up to a thousand guests.",
  "common.nav.salons_mega.stat_alt": "alternatives",
  "common.nav.salons_mega.stat_guests": "guests max.",
  "common.nav.salons_mega.intro": "Modular salons with audiovisual equipment, executive boardrooms and Peruvian catering for weddings, conferences and celebrations.",
  "common.nav.salons_mega.cta": "Request a quote",
  "common.nav.salons_mega.card1_tag": "Weddings & Banquets",
  "common.nav.salons_mega.card1_name": "Salón Sol de Oro",
  "common.nav.salons_mega.card1_meta": "up to 1,000 guests",
  "common.nav.salons_mega.card2_tag": "Corporate",
  "common.nav.salons_mega.card2_name": "Executive Boardrooms",
  "common.nav.salons_mega.card2_meta": "8 to 40 people",
  "common.nav.salons_mega.card3_tag": "Conventions",
  "common.nav.salons_mega.card3_name": "Modular Salons",
  "common.nav.salons_mega.card3_meta": "flexible configuration",

  "common.nav.restaurant": "Restaurant",
  "common.nav.gallery": "Gallery",
  "common.nav.experiences": "Experiences",
  "common.nav.business": "Business",
  "common.nav.about": "About",
  "common.nav.mobile_menu_label": "Menu",
  "common.nav.mobile_close": "Close menu",
  "common.nav.mobile_open": "Open menu",
  "common.nav.mobile_reserve_cta": "Book now",

  // ---- common: reservation bar ----
  "common.reserve.tab_stay": "Stay",
  "common.reserve.tab_events": "Salons",
  "common.reserve.tab_dining": "Restaurant",
  "common.reserve.checkin": "Check-in",
  "common.reserve.checkout": "Check-out",
  "common.reserve.guests_label": "Guests",
  "common.reserve.guests_adults_default": "2 adults",
  "common.reserve.guests_adults": "Adults",
  "common.reserve.guests_children": "Children",
  "common.reserve.guests_children_age": "0-12 years",
  "common.reserve.promo": "Code",
  "common.reserve.promo_placeholder": "Promo code",
  "common.reserve.submit_stay": "Book",
  "common.reserve.dining_date": "Date",
  "common.reserve.dining_time": "Time",
  "common.reserve.dining_pax_label": "Diners",
  "common.reserve.dining_pax_default": "2 people",
  "common.reserve.dining_pax": "People",
  "common.reserve.dining_occasion": "Occasion",
  "common.reserve.dining_phone": "Phone",
  "common.reserve.submit_dining": "Book a table",
  "common.reserve.evt_type": "Event type",
  "common.reserve.evt_date": "Date",
  "common.reserve.evt_pax": "Attendees",
  "common.reserve.evt_email": "Email",
  "common.reserve.evt_phone": "Phone",
  "common.reserve.submit_events": "Get a quote",

  // ---- common: footer ----
  "common.footer.brand_intro": "A five-star hotel in the heart of Miraflores' tourist and financial district. An authentically Peruvian experience with international service.",
  "common.footer.col_hotel_title": "Hotel",
  "common.footer.col_hotel_about": "About the hotel",
  "common.footer.col_hotel_rooms": "Rooms",
  "common.footer.col_hotel_restaurant": "Restaurante Murano",
  "common.footer.col_hotel_services": "Services",
  "common.footer.col_hotel_salons": "Salons",
  "common.footer.col_hotel_gallery": "Gallery",
  "common.footer.col_hotel_location": "Location",
  "common.footer.col_stay_title": "Your Stay",
  "common.footer.col_stay_offers": "Offers",
  "common.footer.col_stay_faq": "FAQ",
  "common.footer.col_stay_cancellation": "Cancellation policy",
  "common.footer.col_stay_terms": "Terms and conditions",
  "common.footer.col_stay_privacy": "Privacy policy",
  "common.footer.col_stay_complaints": "Complaints book",
  "common.footer.col_contact_title": "Contact",
  "common.footer.col_contact_reception": "Reception",
  "common.footer.col_contact_reservations": "Reservations",
};
```

- [ ] **Step 2: Write the i18n engine in `assets/scripts.js`**

Add this as a new block, placed near the top of the file (before the other IIFEs, since `getSiteLang`/`applyI18n` are meant to be usable by any later block — e.g. the reservation-bar guest-panel code added earlier in this project doesn't need it, but future widget code will):

```javascript
  /* ---------- i18n: toggle ES/EN, persisted, no reload ----------
     data-i18n="clave" traduce textContent; data-i18n-attr="attr:clave[,attr2:clave2]"
     traduce atributos (placeholder, alt, aria-label, title, etc.). Ver spec:
     docs/superpowers/specs/2026-08-21-site-i18n-en-toggle-design.md */
  var SITE_LANG_KEY = 'site_lang';

  function getSiteLang(){
    try {
      return localStorage.getItem(SITE_LANG_KEY) === 'en' ? 'en' : 'es';
    } catch (e) {
      return 'es';
    }
  }
  window.getSiteLang = getSiteLang;

  function setSiteLang(lang){
    try { localStorage.setItem(SITE_LANG_KEY, lang); } catch (e) { /* ignore */ }
  }

  function applyI18n(lang){
    document.documentElement.lang = lang;
    if (lang !== 'en') return; // el markup ya está en español por defecto — no hay swap "a español"
    var dict = window.I18N_EN || {};
    document.querySelectorAll('[data-i18n]').forEach(function(el){
      var key = el.getAttribute('data-i18n');
      if (Object.prototype.hasOwnProperty.call(dict, key)) {
        el.textContent = dict[key];
      } else {
        console.warn('[i18n] missing EN key:', key);
      }
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function(el){
      el.getAttribute('data-i18n-attr').split(',').forEach(function(pair){
        var parts = pair.split(':');
        var attr = parts[0].trim();
        var key = parts[1] ? parts[1].trim() : '';
        if (!attr || !key) return;
        if (Object.prototype.hasOwnProperty.call(dict, key)) {
          el.setAttribute(attr, dict[key]);
        } else {
          console.warn('[i18n] missing EN key:', key);
        }
      });
    });
  }
  window.applyI18n = applyI18n;

  function wireLangToggle(){
    document.querySelectorAll('.lang-btn').forEach(function(btn){
      btn.addEventListener('click', function(){
        var lang = btn.dataset.lang;
        setSiteLang(lang);
        document.querySelectorAll('.lang-btn').forEach(function(b){
          b.classList.toggle('active', b.dataset.lang === lang);
        });
        if (lang === 'es') {
          location.reload(); // volver a español = recargar el HTML original en español
        } else {
          applyI18n('en');
        }
      });
    });
  }

  (function(){
    var lang = getSiteLang();
    document.querySelectorAll('.lang-btn').forEach(function(b){
      b.classList.toggle('active', b.dataset.lang === lang);
    });
    if (lang === 'en') applyI18n('en');
    wireLangToggle();
  })();
```

Note on the `es` branch reloading the page: swapping *from* English *back to* Spanish by reversing `textContent` would require storing the original Spanish string somewhere (a second data attribute) for every single translated node — real complexity for zero user-facing benefit, since a full reload already gets back to the (always-Spanish-by-default) HTML source instantly. Simpler and just as fast for the guest.

- [ ] **Step 3: Convert the toggle markup from inert `<span>` to clickable buttons, in all 14 pages**

In each of the 14 files listed in Global Constraints, this exact block appears **twice** (desktop header `.nav.right`, and `.mobile-nav-footer`):

```html
<span class="lang"><span class="active">ES</span> &nbsp;/&nbsp; EN</span>
```

Replace **both** occurrences in each file with:

```html
<span class="lang"><button type="button" class="lang-btn active" data-lang="es">ES</button> &nbsp;/&nbsp; <button type="button" class="lang-btn" data-lang="en">EN</button></span>
```

(Some pages wrap this inside `<li class="nav-item">...</li>` for the desktop header — leave the wrapping element untouched, only swap the inner `<span class="lang">...</span>` content as shown.)

- [ ] **Step 4: Add minimal `.lang-btn` styling to `assets/styles.css`**

The existing `.lang .active` rule already styles the active state color; add button-reset styling so `.lang-btn` doesn't inherit default `<button>` chrome (border, background, padding):

```css
  .lang-btn{
    background:none; border:none; padding:0; margin:0;
    font:inherit; color:inherit; cursor:pointer;
  }
  .lang-btn:hover{ color:var(--sand); }
```

Add this immediately after the existing `.lang .active{ color:var(--sand); }` rule (find it with `grep -n "lang .active" assets/styles.css` — it appears twice, once for desktop nav, once for mobile-nav-footer; add the block once, right after the first occurrence, since CSS rules apply globally regardless of where they're declared).

- [ ] **Step 5: Write the coverage-check script**

```javascript
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
  console.warn('UNUSED DICTIONARY KEYS (defined but not referenced by any page):');
  unused.forEach((k) => console.warn('  ' + k));
}
if (missing.length) {
  console.error(`\n${missing.length} missing, ${unused.length} unused.`);
  process.exit(1);
}
console.log(`OK — 0 missing. ${unused.length} unused key(s).`);
```

- [ ] **Step 6: Run the coverage check — expect only "unused" warnings, zero missing**

Run: `node scripts/check-i18n-coverage.js`
Expected: since no page yet has `data-i18n` attributes (Task 1 only ships the dictionary and the engine, not the tagging), output is `OK — 0 missing. <N> unused key(s).` — this confirms the script itself works and the dictionary parses correctly. `<N>` unused is expected and will drop to 0 as Tasks 2–15 tag pages against these `common.*` keys.

- [ ] **Step 7: Manual verification — toggle button appears and is clickable, no JS errors**

Run: `python -m http.server 8123` from the repo root (background), then use Playwright:

```javascript
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('http://localhost:8123/index.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(300);
  const enBtn = await page.locator('.lang-btn[data-lang="en"]').first();
  console.log('EN button visible:', await enBtn.isVisible());
  await enBtn.click();
  await page.waitForTimeout(300);
  console.log('html lang attr:', await page.getAttribute('html', 'lang'));
  console.log('errors (excluding known pre-existing bug):', JSON.stringify(errors.filter(e => !e.includes("reading 'classList'"))));
  await browser.close();
})();
```

Expected: `EN button visible: true`, `html lang attr: en`, empty errors array. Since no page content is tagged yet, no visible text should change — that's expected at this stage.

- [ ] **Step 8: Commit**

```bash
git add assets/i18n/en.js assets/scripts.js assets/styles.css scripts/check-i18n-coverage.js index.html habitaciones.html eventos.html restaurante.html servicios.html experiencias.html ofertas.html faq.html galeria.html ubicacion.html acerca.html empresarial.html privacidad.html terminos.html
git commit -m "feat(i18n): add EN/ES toggle engine, common dictionary, and coverage check"
```

---

### Task 2: Translate `index.html`

**Files:**
- Modify: `index.html`
- Modify: `assets/i18n/en.js` (add `index.*` keys)

**Interfaces:**
- Consumes: `window.applyI18n`, `window.I18N_EN`, the `.lang-btn` markup and `common.*` keys from Task 1.
- Produces: nothing new for later tasks — each page task is independent once Task 1 lands.

- [ ] **Step 1: Tag every `common.*` element on this page with `data-i18n`/`data-i18n-attr`**

Using the header/mega-menus/footer/reserve-bar markup already on this page, wire each element to its `common.*` key from Task 1's dictionary. Worked example for the header nav (apply the same pattern — add `data-i18n="<key>"` on the element whose `textContent` is the translatable string — to every other `common.*` element: both mega-menus' `eyebrow`/`h3`/`p`/stat spans/card `small`/`h4`/`span.meta`, the footer's three columns and their links, the reservation bar's labels/buttons/placeholders via `data-i18n-attr`, and the mobile-nav-footer's "Reservar ahora" link):

```html
<li class="nav-item"><a href="galeria.html" data-i18n="common.nav.gallery">Galería</a></li>
<li class="nav-item"><a href="experiencias.html" data-i18n="common.nav.experiences">Experiencias</a></li>
<li class="nav-item"><a href="empresarial.html" data-i18n="common.nav.business">Empresarial</a></li>
```

For the reservation bar's promo input (an attribute, not text content):

```html
<input class="control" type="text" name="promo" placeholder="Promocional" data-i18n-attr="placeholder:common.reserve.promo_placeholder" />
```

For the guest-panel trigger buttons (their *initial* textContent, e.g. `"2 adultos"`/`"2 personas"`, also needs a key — but note these buttons' text is overwritten live by the stepper JS from Task 10's guest-panel feature the moment the guest changes a value, so translating the key only fixes the *initial* label; that's expected and sufficient here — the stepper's own summarize() function stays Spanish-only in this task and is out of scope):

```html
<button type="button" class="control guest-trigger" aria-haspopup="true" aria-expanded="false" data-i18n="common.reserve.guests_adults_default">2 adultos</button>
```

- [ ] **Step 2: Translate the `<title>` and `<meta name="description">`**

```html
<title>Sol de Oro Hotel &amp; Suites · Miraflores · Lima</title>
<meta name="description" content="Five-star hotel in Miraflores. 123 rooms, salons for up to 1,000 guests, Restaurante Murano, spa and pool. A stay in the heart of Lima." data-i18n-attr="content:index.meta_description" />
```

Add the matching key to `assets/i18n/en.js`'s dictionary (append to the object, under a new `// ---- index.html ----` comment section): `"index.meta_description": "Five-star hotel in Miraflores. 123 rooms, salons for up to 1,000 guests, Restaurante Murano, spa and pool. A stay in the heart of Lima.",`. Leave `<title>` untranslated (the brand name + location doesn't need translation, and search-engine title tags for a bilingual small-business site commonly stay as the brand name across languages — keep it simple, don't add a second `<title>` mechanism for this one line).

- [ ] **Step 3: Tag and translate the rest of the page's unique content**

Read the full file (`index.html`) beyond what Task 1 already covered (header/footer/reserve-bar) — this includes the 4 hero slides, the "about"/intro section, and any teaser sections for rooms/events/dining/experiences/offers that appear before the footer. For each, add `data-i18n="index.<slug>"` (e.g. `index.hero.slide1.eyebrow`, `index.hero.slide1.title`, `index.hero.slide1.body`, `index.hero.slide1.cta`, `index.about.title`, ...) and a matching English entry in `en.js`, translating in the warm-but-formal five-star tone established by Task 1's `common.*` strings. Use sequential, readable slugs per section (`hero.slideN.*`, `about.*`, `rooms_teaser.*`, etc.) — there is no fixed list here because the exact sections depend on what's actually in the file; tag everything a guest would read, skip nothing.

- [ ] **Step 4: Run the coverage check scoped to this page**

Run: `node scripts/check-i18n-coverage.js`
Expected: `OK — 0 missing.` (some `unused` warnings are fine — they'll disappear as later page tasks land and start reusing the same `common.*` keys).

- [ ] **Step 5: Manual verification with Playwright**

```javascript
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:8123/index.html', { waitUntil: 'domcontentloaded' });
  await page.click('.lang-btn[data-lang="en"]');
  await page.waitForTimeout(300);
  const navText = await page.textContent('.nav.right');
  console.log('nav (should be English):', navText.trim());
  const heroTitle = await page.textContent('.slide.active h1');
  console.log('hero title (should be English):', heroTitle.trim());
  await browser.close();
})();
```

Expected: both printed strings are in English, matching what was written into `en.js`.

- [ ] **Step 6: Commit**

```bash
git add index.html assets/i18n/en.js
git commit -m "feat(i18n): translate index.html to English"
```

---

### Tasks 3–15: Translate the remaining 13 pages

Each of these follows the **identical pattern established in Task 2** — apply it once per file, in this order (grouping by likely content overlap doesn't matter; any order works since each task is independent):

`habitaciones.html`, `eventos.html`, `restaurante.html`, `servicios.html`, `experiencias.html`, `ofertas.html`, `faq.html`, `galeria.html`, `ubicacion.html`, `acerca.html`, `empresarial.html`, `privacidad.html`, `terminos.html`.

For each page (Task N, one per file above):

**Files:**
- Modify: `<page>.html`
- Modify: `assets/i18n/en.js` (add `<page>.*` keys under a new `// ---- <page>.html ----` comment section)

**Interfaces:**
- Consumes: `window.applyI18n`, `window.I18N_EN`, `.lang-btn` markup, and every `common.*` key from Task 1 (do not redefine or duplicate `common.*` keys — reuse them as-is).
- Produces: nothing later tasks depend on.

- [ ] **Step 1:** Tag this page's `common.*` elements (header, mega-menus, footer, reserve bar, mobile-nav) with `data-i18n`/`data-i18n-attr`, reusing Task 1's existing `common.*` keys exactly as done for `index.html` in Task 2, Step 1.
- [ ] **Step 2:** Translate `<meta name="description">` via `data-i18n-attr="content:<page>.meta_description"`, adding the key to `en.js` (same pattern as Task 2, Step 2).
- [ ] **Step 3:** Read the full file, tag every remaining unique string (headings, body copy, card labels, form labels, FAQ question/answer pairs, image `alt` text where it's guest-facing description rather than decorative, etc.) with `data-i18n="<page>.<slug>"`, and add the matching English translation to `en.js`, in the same tone as Task 1/2.
- [ ] **Step 4:** Run `node scripts/check-i18n-coverage.js` — expect `OK — 0 missing.` for this file (some `unused` warnings from pages not yet done is expected until Task 16).
- [ ] **Step 5:** Manual Playwright check — same shape as Task 2 Step 5, pointed at this page's URL and a representative translated element (e.g. the page's `<h1>` or first section heading) instead of the homepage's hero.
- [ ] **Step 6:** Commit — `git add <page>.html assets/i18n/en.js && git commit -m "feat(i18n): translate <page>.html to English"`.

**Note on `faq.html`:** this page's core content is question/answer pairs — tag both the question and the answer text of every FAQ item individually (`faq.q1.question` / `faq.q1.answer`, `faq.q2.question` / `faq.q2.answer`, ...), not the whole item as one block, so future edits to a single answer don't require re-keying the whole FAQ.

**Note on `privacidad.html` and `terminos.html`:** these are long legal documents. Translate them in full (same rule as every other page — no partial translation), but double-check names of Peruvian laws/authorities (Ley N.° 29733, ANPDP) are kept as their official Spanish names even in the English version, since that's how they're legally referred to — add a short parenthetical English gloss the first time each appears (e.g. "Ley N.° 29733 (Peru's Personal Data Protection Law)"), not a fabricated English legal name.

---

### Task 16: Final full-site coverage check and cross-page regression

**Files:**
- None created or modified — verification only, unless gaps are found (in which case: fix in the relevant page's `.html`/`en.js`, no new files).

**Interfaces:**
- Consumes: everything from Tasks 1–15.

- [ ] **Step 1: Run the full coverage check**

Run: `node scripts/check-i18n-coverage.js`
Expected: `OK — 0 missing. 0 unused key(s).` If anything is missing, go fix it in the page/dictionary named in the output before continuing. If anything is unused, either it's a genuine leftover (remove it from `en.js`) or a page task missed tagging an element that should reference it (go tag it).

- [ ] **Step 2: Cross-page persistence regression with Playwright**

```javascript
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:8123/index.html', { waitUntil: 'domcontentloaded' });
  await page.click('.lang-btn[data-lang="en"]');
  await page.waitForTimeout(300);
  await page.goto('http://localhost:8123/habitaciones.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(300);
  const activeBtn = await page.getAttribute('.lang-btn.active', 'data-lang');
  const navText = await page.textContent('.nav.right');
  console.log('active lang after navigating (should be en):', activeBtn);
  console.log('nav on second page (should be English):', navText.trim());
  await page.click('.lang-btn[data-lang="es"]');
  await page.waitForTimeout(500);
  const navTextEs = await page.textContent('.nav.right');
  console.log('nav after switching back to ES (should be Spanish):', navTextEs.trim());
  await browser.close();
})();
```

Expected: `active lang after navigating: en`, nav text in English on the second page (proving persistence across a real page navigation, not just a client-side swap), and Spanish nav text after clicking `ES` (proving the reload-to-Spanish path from Task 1 works).

- [ ] **Step 3: Spot-check 3 more pages not yet visually checked in earlier tasks**

Pick 3 pages at random from the 14 (e.g. `ofertas.html`, `terminos.html`, `empresarial.html`) and repeat Task 2 Step 5's check against each, confirming EN toggle visibly translates real content with no console errors (excluding the known pre-existing `reading 'classList'` bug logged earlier in this project, unrelated to i18n).

- [ ] **Step 4: Commit** (only if Step 1 required fixes; otherwise this task has nothing to commit)

```bash
git add -A
git commit -m "fix(i18n): close coverage gaps found in final full-site check"
```
