/* Popup informativo (novedades / promociones), gestionado desde admin/index.html.
   Se muestra una sola vez por pestaña/sesión (sessionStorage) para no ser invasivo
   al navegar entre páginas del sitio. Consulta Supabase directo desde el navegador
   con la anon key pública — está protegida por RLS (solo lectura), igual que el
   resto de las tablas públicas del sitio (offers, le_experiences, etc.). */
(function () {
  const SUPA_URL = 'https://fjzshpilzjtfjcouzzzz.supabase.co';
  const SUPA_KEY = 'sb_publishable_gtCG2nBVE9ujjm6c28rlAw_g55hDYCY';
  const SEEN_KEY = 'sdo_popup_seen';

  if (typeof window.supabase === 'undefined') return; // CDN no cargó (ej. bloqueado)
  try { if (sessionStorage.getItem(SEEN_KEY)) return; } catch (e) { /* si falla, se muestra igual */ }

  const sb = window.supabase.createClient(SUPA_URL, SUPA_KEY);
  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD, comparable con date de Postgres

  sb.from('popups')
    .select('*')
    .eq('active', true)
    .lte('starts_on', today)
    .gte('ends_on', today)
    .order('starts_on', { ascending: false })
    .limit(1)
    .then(({ data, error }) => {
      if (error || !data || !data.length) return;
      showPopup(data[0]);
    });

  function showPopup(popup) {
    try { sessionStorage.setItem(SEEN_KEY, '1'); } catch (e) { /* ignore */ }

    const overlay = document.createElement('div');
    overlay.className = 'sdo-popup-overlay';

    const card = document.createElement('div');
    card.className = 'sdo-popup-card';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'sdo-popup-close';
    closeBtn.setAttribute('aria-label', 'Cerrar');
    closeBtn.textContent = '✕';
    closeBtn.addEventListener('click', close);

    const img = document.createElement('img');
    img.src = popup.image_url;
    img.alt = popup.title || 'Promoción Sol de Oro';

    card.appendChild(closeBtn);

    if (popup.link_url) {
      const link = document.createElement('a');
      link.href = popup.link_url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.appendChild(img);
      card.appendChild(link);
    } else {
      card.appendChild(img);
    }

    overlay.appendChild(card);
    document.body.appendChild(overlay);

    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', onEscape);

    requestAnimationFrame(() => overlay.classList.add('is-visible'));

    function close() {
      overlay.classList.remove('is-visible');
      document.removeEventListener('keydown', onEscape);
      setTimeout(() => overlay.remove(), 250);
    }
    function onEscape(e) { if (e.key === 'Escape') close(); }
  }
})();
