  /* Manifiesto de imágenes — lee assets/images.json y reemplaza cada
     elemento con data-img="key" usando el src/alt definidos. Permite
     editar todas las imágenes del sitio desde editor-imagenes.html sin
     tocar el HTML. Si el fetch falla (ej. abierto con file://) se mantiene
     el src/background-image inline como fallback. */
  (function(){
    const slots = document.querySelectorAll('[data-img]');
    if (!slots.length) return;
    function applyOverrides(images){
      // Permitir overrides en localStorage para preview en vivo
      try {
        const draft = JSON.parse(localStorage.getItem('soldeoro.images.draft') || 'null');
        if (draft && typeof draft === 'object') Object.assign(images, draft);
      } catch(e){ /* ignore */ }
      return images;
    }
    function setImage(el, entry){
      const src = entry && entry.src;
      if (!src) return;
      if (el.tagName === 'IMG'){
        el.src = src;
        if (entry.alt) el.alt = entry.alt;
      } else {
        el.style.backgroundImage = `url('${src}')`;
      }
    }
    fetch('assets/images.json', { cache: 'no-cache' })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (!data || !data.images) return;
        const images = applyOverrides({ ...data.images });
        slots.forEach(el => {
          const key = el.dataset.img;
          if (images[key]) setImage(el, images[key]);
        });
      })
      .catch(() => { /* fallback a src inline */ });
  })();

  /* Hero slider */
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.hero-dot');
  let current = 0, timer;
  function go(i){
    slides[current].classList.remove('active');
    dots[current].classList.remove('active');
    current = (i + slides.length) % slides.length;
    slides[current].classList.add('active');
    dots[current].classList.add('active');
  }
  function autoplay(){
    clearInterval(timer);
    timer = setInterval(()=>go(current+1), 4000);
  }
  dots.forEach(d => d.addEventListener('click', ()=>{ go(parseInt(d.dataset.go,10)); autoplay(); }));
  autoplay();

  /* Mobile nav drawer */
  (function(){
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.getElementById('mobileNav');
    const closeBtn = document.querySelector('.mobile-nav-close');
    let overlay = document.querySelector('.mobile-nav-overlay');
    
    if (!toggle || !nav) return;
    
    // Crear overlay si no existe
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'mobile-nav-overlay';
      document.body.appendChild(overlay);
    }
    
    function open(){
      nav.classList.add('is-open');
      overlay.classList.add('is-visible');
      toggle.classList.add('is-open');
      nav.setAttribute('aria-hidden','false');
      toggle.setAttribute('aria-expanded','true');
      document.body.classList.add('nav-open');
    }
    function close(){
      nav.classList.remove('is-open');
      overlay.classList.remove('is-visible');
      toggle.classList.remove('is-open');
      nav.setAttribute('aria-hidden','true');
      toggle.setAttribute('aria-expanded','false');
      document.body.classList.remove('nav-open');
    }
    toggle.addEventListener('click', () => nav.classList.contains('is-open') ? close() : open());
    if (closeBtn) closeBtn.addEventListener('click', close);
    overlay.addEventListener('click', close);
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', close));
    document.addEventListener('keydown', e => { if(e.key==='Escape') close(); });
  })();

  /* Mega menu — open with small leave delay so the cursor can travel
     from the trigger to the centered panel without it collapsing. */
  document.querySelectorAll('.nav-item.has-mega').forEach(item => {
    const mega = item.querySelector('.mega');
    if(!mega) return;
    let leaveTimer;
    const open = () => {
      clearTimeout(leaveTimer);
      document.querySelectorAll('.nav-item.has-mega.mega-open').forEach(o => {
        if(o !== item) o.classList.remove('mega-open');
      });
      item.classList.add('mega-open');
    };
    const scheduleClose = () => {
      clearTimeout(leaveTimer);
      leaveTimer = setTimeout(() => item.classList.remove('mega-open'), 220);
    };
    item.addEventListener('mouseenter', open);
    item.addEventListener('mouseleave', scheduleClose);
    mega.addEventListener('mouseenter', open);
    mega.addEventListener('mouseleave', scheduleClose);
    item.addEventListener('focusin', open);
    item.addEventListener('focusout', scheduleClose);
  });

  /* Header adaptativo — transparente sobre secciones oscuras (hero, page-hero,
     award-band, footer); sólido (blanco con texto oscuro) sobre secciones claras */
  (function(){
    const hdr = document.getElementById('siteHeader');
    if (!hdr) return;
    const darkSelector = '.hero, .page-hero, .award-band, .site-footer';
    let darkSections = [...document.querySelectorAll(darkSelector)];

    function probe(){ return (hdr.offsetHeight || 80) * 0.6; }

    function update(){
      const p = probe();
      let onDark = false;
      for (const s of darkSections){
        const r = s.getBoundingClientRect();
        if (r.top <= p && r.bottom >= p){ onDark = true; break; }
      }
      // 'scrolled' = sobre sección clara (blanco + texto oscuro)
      hdr.classList.toggle('scrolled', !onDark);
    }

    window.addEventListener('scroll', update, { passive:true });
    window.addEventListener('resize', update, { passive:true });
    window.addEventListener('scroll', () => {
      hdr.classList.toggle('has-scrolled', window.scrollY > 10);
    }, { passive:true });
    /* Re-detect en load por si las imágenes cambian la altura de las secciones */
    window.addEventListener('load', () => {
      darkSections = [...document.querySelectorAll(darkSelector)];
      update();
    });
    update();
  })();

  /* Reveal on scroll */
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if(e.isIntersecting){
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal, .loc-scatter').forEach(el => io.observe(el));

  /* Default dates */
  (function(){
    const today = new Date();
    const tomorrow = new Date(today.getTime() + 86400000);
    const fmt = d => d.toISOString().slice(0,10);
    const ci = document.querySelector('input[name="checkin"]');
    const co = document.querySelector('input[name="checkout"]');
    if(ci) ci.value = fmt(today);
    if(co) co.value = fmt(tomorrow);
    const evtDate = document.querySelector('input[name="evt-date"]');
    if(evtDate){
      const future = new Date(today.getTime() + 30*86400000);
      evtDate.value = fmt(future);
    }
    const diningDate = document.querySelector('input[name="dining-date"]');
    if(diningDate) diningDate.value = fmt(today);
  })();

  /* Tabs toggle + init según data-reserve-mode del body */
  function setReserveMode(mode){
    document.querySelectorAll('.reserve-tabs .tab').forEach(x => {
      const on = x.dataset.mode === mode;
      x.classList.toggle('active', on);
      x.setAttribute('aria-selected', on);
    });
    document.querySelectorAll('.reserve').forEach(f => {
      f.classList.toggle('active', f.dataset.mode === mode);
    });
  }
  document.querySelectorAll('.reserve-tabs .tab').forEach(t => {
    t.addEventListener('click', () => {
      setReserveMode(t.dataset.mode);
      // En mobile, desplegar el formulario hacia arriba
      if (window.innerWidth <= 560) {
        document.body.classList.add('reserve-docked');
        // Scroll suave al formulario
        setTimeout(() => {
          const reserveSection = document.querySelector('.reserve-section');
          if (reserveSection) {
            reserveSection.scrollIntoView({ behavior: 'smooth', block: 'end' });
          }
        }, 300);
      }
    });
  });
  /* Activar el tab correcto según la página */
  (function(){
    const initial = document.body.dataset.reserveMode;
    if (initial) setReserveMode(initial);
  })();

  /* Mesa de fotos: filtro, layout dinámico (hasta 2 filas) y nav lateral */
  (function(){
    const wrap = document.querySelector('.loc-scatter-wrap');
    const scatter = document.getElementById('locScatter');
    if (!wrap || !scatter) return;
    const prev = wrap.querySelector('.loc-nav-prev');
    const next = wrap.querySelector('.loc-nav-next');

    function cardWidth(){
      const w = window.innerWidth;
      if (w <= 560) return 170;
      if (w <= 980) return 200;
      return 230;
    }

    function gapX(){ return window.innerWidth <= 560 ? 18 : 26; }
    function padX(){
      const w = window.innerWidth;
      if (w <= 560) return 16;
      if (w <= 980) return 20;
      return 24;
    }

    function relayout(){
      const cards = [...scatter.querySelectorAll('.loc-card')].filter(c => !c.classList.contains('is-hidden'));
      const n = cards.length;
      if (!n){
        scatter.style.setProperty('--cols', 1);
        scatter.style.setProperty('--rows', 1);
        updateNav();
        return;
      }
      const cw = cardWidth(), gx = gapX(), px = padX();
      const avail = scatter.clientWidth - (px * 2);
      const fitsOneRow = (n * cw + (n - 1) * gx) <= avail;
      if (fitsOneRow){
        scatter.style.setProperty('--cols', n);
        scatter.style.setProperty('--rows', 1);
      } else {
        scatter.style.setProperty('--cols', Math.ceil(n / 2));
        scatter.style.setProperty('--rows', 2);
      }
      requestAnimationFrame(updateNav);
    }

    function updateNav(){
      const max = scatter.scrollWidth - scatter.clientWidth;
      const x = scatter.scrollLeft;
      const overflow = max > 4;
      if (prev) prev.classList.toggle('is-visible', overflow && x > 8);
      if (next) next.classList.toggle('is-visible', overflow && x < max - 8);
    }

    function step(dir){
      const cw = cardWidth(), gx = gapX();
      scatter.scrollBy({ left: dir * (cw + gx) * 2, behavior:'smooth' });
    }

    if (prev) prev.addEventListener('click', () => step(-1));
    if (next) next.addEventListener('click', () => step(1));
    scatter.addEventListener('scroll', updateNav, { passive:true });
    window.addEventListener('resize', relayout);

    /* Rueda del mouse → scroll horizontal */
    scatter.addEventListener('wheel', (e) => {
      const max = scatter.scrollWidth - scatter.clientWidth;
      if (max <= 0) return;
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)){
        e.preventDefault();
        scatter.scrollLeft += e.deltaY;
      }
    }, { passive:false });

    /* Filtro por categoría */
    document.querySelectorAll('.loc-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const cat = tab.dataset.cat;
        document.querySelectorAll('.loc-tab').forEach(t => t.classList.toggle('active', t === tab));
        document.querySelectorAll('.loc-card').forEach(card => {
          const visible = cat === 'all' || card.dataset.cat === cat;
          card.classList.toggle('is-hidden', !visible);
        });
        scatter.scrollTo({ left:0, behavior:'smooth' });
        relayout();
      });
    });

    relayout();
    window.addEventListener('load', relayout);
  })();

  /* Showcase genérico (habitaciones / salones / etc.): swap principal al click
     de thumbnail + flechas. Funciona con cualquier .rooms-showcase y su
     .rs-thumbs hermano (siguiente .rs-thumbs en el DOM dentro del mismo
     contenedor padre). */
  document.querySelectorAll('.rooms-showcase').forEach(showcase => {
    // Buscar el .rs-thumbs hermano (siguiente sibling del mismo padre)
    let thumbsWrap = showcase.nextElementSibling;
    while (thumbsWrap && !thumbsWrap.classList.contains('rs-thumbs')) {
      thumbsWrap = thumbsWrap.nextElementSibling;
    }
    if (!thumbsWrap) return;

    const thumbs = [...thumbsWrap.querySelectorAll('.rs-thumb')];
    const images = [...showcase.querySelectorAll('.rs-img')];
    const counter = showcase.querySelector('.rs-counter');
    const detail = showcase.querySelector('.rs-detail');
    if (!detail || !thumbs.length) return;

    const fields = {
      cat: detail.querySelector('[data-field="cat"]'),
      name: detail.querySelector('[data-field="name"]'),
      lead: detail.querySelector('[data-field="lead"]'),
      size: detail.querySelector('[data-field="size"]'),
      bed: detail.querySelector('[data-field="bed"]'),
      view: detail.querySelector('[data-field="view"]'),
      cap: detail.querySelector('[data-field="cap"]'),
      features: detail.querySelector('[data-field="features"]')
    };

    function setActive(idx){
      idx = (idx + thumbs.length) % thumbs.length;
      thumbs.forEach((t, i) => t.classList.toggle('is-active', i === idx));
      images.forEach((img, i) => img.classList.toggle('is-active', i === idx));
      const t = thumbs[idx];
      Object.keys(fields).forEach(key => {
        if (!fields[key]) return;
        if (key === 'features') {
          const feats = (t.dataset.features || '').split('|').filter(Boolean);
          fields.features.innerHTML = feats.map(f => `<li>${f}</li>`).join('');
        } else {
          if (t.dataset[key] !== undefined) fields[key].textContent = t.dataset[key];
        }
      });
      if (counter) counter.textContent = String(idx + 1).padStart(2, '0') + ' / ' + String(thumbs.length).padStart(2, '0');
      showcase.dataset.current = idx;
    }

    thumbs.forEach((t, i) => t.addEventListener('click', () => setActive(i)));
    showcase.querySelectorAll('.rs-arrow').forEach(btn => {
      btn.addEventListener('click', () => {
        const cur = parseInt(showcase.dataset.current || '0', 10);
        const dir = parseInt(btn.dataset.dir, 10);
        setActive(cur + dir);
      });
    });
    setActive(0);
  });

  /* Galería: filtro por categoría */
  (function(){
    const grid = document.getElementById('galleryGrid');
    if (!grid) return;
    document.querySelectorAll('.gallery-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const cat = tab.dataset.cat;
        document.querySelectorAll('.gallery-tab').forEach(t => t.classList.toggle('active', t === tab));
        grid.querySelectorAll('.gallery-item').forEach(item => {
          const visible = cat === 'all' || item.dataset.cat === cat;
          item.classList.toggle('is-hidden', !visible);
        });
      });
    });
  })();

  /* Salones · filtro por piso (eventos.html) */
  (function(){
    const filters = document.querySelectorAll('.salones-filter');
    const cards = document.querySelectorAll('.salon-card');
    if (!filters.length || !cards.length) return;
    filters.forEach(btn => {
      btn.addEventListener('click', () => {
        const piso = btn.dataset.piso;
        filters.forEach(b => b.classList.toggle('is-active', b === btn));
        cards.forEach(card => {
          const visible = piso === 'all' || card.dataset.piso === piso;
          card.classList.toggle('is-hidden', !visible);
        });
      });
    });
  })();

  /* Floating reservation bar — always docked on desktop, inline on mobile */
  (function(){
    function check(){
      const docked = window.innerWidth > 1100;
      document.body.classList.toggle('reserve-docked', docked);
    }
    window.addEventListener('resize', check);
    check();
  })();

  /* Hospedaje → iHotelier con parámetros pre-cargados desde la barra
     Parámetros iHotelier: datein / dateout (MM/DD/YYYY), rooms, adults, children */
  (function(){
    const form = document.querySelector('.form-stay');
    if (!form) return;

    function isoToIhotelier(iso){
      if (!iso) return '';
      const [y, m, d] = iso.split('-');
      return `${m}/${d}/${y}`;
    }

    form.onsubmit = function(e){
      e.preventDefault();

      const checkin  = (form.querySelector('[name="checkin"]')  || {}).value  || '';
      const checkout = (form.querySelector('[name="checkout"]') || {}).value  || '';
      const adults   = (form.querySelector('[name="adults"]')   || {}).value  || '2';
      const kids     = (form.querySelector('[name="kids"]')     || {}).value  || '0';
      const promoEl  = form.querySelector('[name="promo"]');
      const promo    = promoEl ? promoEl.value.trim() : '';

      const params = new URLSearchParams({
        datein   : isoToIhotelier(checkin),
        dateout  : isoToIhotelier(checkout),
        rooms    : '1',
        adults   : adults,
        children : kids,
      });
      if (promo) params.set('discount', promo);

      const url = 'https://soldeoro.ihotelier.com/es/book/dates-of-stay?' + params.toString();
      window.open(url, '_blank', 'noopener,noreferrer');
    };
  })();

  /* Restaurante & Salones → WhatsApp al agente
     Número: +51 924 664 487 */
  (function(){
    const WA = 'https://wa.me/51924664487?text=';

    function fmtDate(iso){
      if (!iso) return '—';
      const [y, m, d] = iso.split('-');
      return `${d}/${m}/${y}`;
    }

    function val(form, name){
      const el = form.querySelector(`[name="${name}"]`);
      return el ? (el.value || '').trim() : '';
    }

    /* —— RESTAURANTE —— */
    const formDining = document.querySelector('.form-dining');
    if (formDining) {
      formDining.onsubmit = function(e){
        e.preventDefault();
        const fecha    = fmtDate(val(formDining, 'dining-date'));
        const hora     = val(formDining, 'dining-time')     || '—';
        const pax      = val(formDining, 'dining-pax')      || '—';
        const ocasion  = val(formDining, 'dining-occasion') || '—';
        const tel      = val(formDining, 'dining-tel')      || '—';

        const msg =
`🍽 *Reserva Restaurante – Sol de Oro*

📅 Fecha: ${fecha}
⏰ Hora: ${hora}
👥 Comensales: ${pax}
🎉 Ocasión: ${ocasion}
📞 Teléfono: ${tel}`;

        window.open(WA + encodeURIComponent(msg), '_blank', 'noopener,noreferrer');
      };
    }

    /* —— SALONES / EVENTOS —— */
    const formEvents = document.querySelector('.form-events');
    if (formEvents) {
      formEvents.onsubmit = function(e){
        e.preventDefault();
        const tipo   = val(formEvents, 'evt-type')  || '—';
        const fecha  = fmtDate(val(formEvents, 'evt-date'));
        const pax    = val(formEvents, 'evt-pax')   || '—';
        const email  = val(formEvents, 'evt-email') || '—';
        const tel    = val(formEvents, 'evt-tel')   || '—';

        const msg =
`🏛 *Cotización Salones – Sol de Oro*

🎯 Tipo de evento: ${tipo}
📅 Fecha: ${fecha}
👥 Asistentes: ${pax}
📧 Email: ${email}
📞 Teléfono: ${tel}`;

        window.open(WA + encodeURIComponent(msg), '_blank', 'noopener,noreferrer');
      };
    }
  })();

  /* Cotización de eventos (eventos.html) — el tipo de evento es de 2 pasos: primero Social o
     Corporativo, después el subtipo exacto que corresponde en Zoho (Tipo_evento_social /
     Tipo_evento_corp). Los dos <select> de subtipo tienen name distinto cada uno (mapea 1 a 1
     a su campo de Zoho); el que no está activo queda disabled para no enviarse. La fecha
     comparte un solo input visible, pero su name se renombra según el rubro elegido. */
  (function(){
    const vertical = document.getElementById('evtVertical');
    if (!vertical) return;
    const socialWrap = document.getElementById('evtTipoSocialWrap');
    const corpWrap = document.getElementById('evtTipoCorpWrap');
    const socialSelect = document.getElementById('evtTipoSocial');
    const corpSelect = document.getElementById('evtTipoCorp');
    const fecha = document.getElementById('evtFecha');
    function syncTipoEvento() {
      const isSocial = vertical.value === 'Social';
      const isCorp = vertical.value === 'Corporativo';
      // .form-field ya trae display:flex propio, que le gana a la regla por defecto de
      // [hidden] — se fuerza display:none/'' directamente en vez de confiar en el atributo.
      socialWrap.style.display = isSocial ? '' : 'none';
      corpWrap.style.display = isCorp ? '' : 'none';
      socialSelect.disabled = !isSocial;
      corpSelect.disabled = !isCorp;
      if (fecha) fecha.name = isCorp ? 'Fecha de evento (corporativo)' : 'Fecha de evento (social)';
    }
    vertical.addEventListener('change', syncTipoEvento);
    syncTipoEvento(); // estado inicial: ninguno seleccionado -> ambos ocultos
  })();

  /* Formularios que envían por email (empresarial.html, eventos.html "Solicitar cotización")
     — vía Formspree (formspree.io), sin backend propio que mantener.
     ACTIVAR: crear una cuenta gratuita en formspree.io, verificar reservas@soldeoro.pe o
     comercial@soldeoro.pe como destino, crear un form, y reemplazar el ID de abajo (lo que va
     después de "/f/") por el que te da Formspree. Mientras tanto, el envío fallará limpio y el
     formulario muestra un aviso para escribir directo al correo — nunca finge un éxito falso. */
  const FORMSPREE_ENDPOINT = 'https://formspree.io/f/TU_FORM_ID_AQUI';

  document.querySelectorAll('[data-email-form]').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalLabel = submitBtn ? submitBtn.textContent : '';
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Enviando…'; }

      try {
        const resp = await fetch(FORMSPREE_ENDPOINT, {
          method: 'POST',
          headers: { 'Accept': 'application/json' },
          body: new FormData(form),
        });
        if (!resp.ok) throw new Error('Formspree respondió ' + resp.status);

        const successMsg = form.dataset.successMsg || 'Gracias. Nos pondremos en contacto pronto.';
        form.textContent = ''; // limpia los campos sin usar innerHTML (el texto es propio, pero se evita por buena práctica)
        const p = document.createElement('p');
        p.style.cssText = 'color:var(--sand-deep);font-weight:500;text-align:center;padding:24px 0';
        p.textContent = successMsg;
        form.appendChild(p);
      } catch (err) {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = originalLabel; }
        let notice = form.querySelector('.email-form-error');
        if (!notice) {
          notice = document.createElement('p');
          notice.className = 'email-form-error';
          notice.style.cssText = 'color:#b3261e;font-size:.85rem;margin-top:10px;text-align:center;';
          form.appendChild(notice);
        }
        notice.textContent = 'No pudimos enviar tu solicitud. Escríbenos directo a comercial@soldeoro.pe mientras lo resolvemos.';
      }
    });
  });
