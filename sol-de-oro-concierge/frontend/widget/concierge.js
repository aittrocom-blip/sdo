const API_URL = "http://localhost:8001/api/concierge";
const STREAM_URL = "http://localhost:8001/api/concierge/stream";

// El widget "sigue" al huésped por todo el sitio (como la barra flotante de reservas): usa
// sessionStorage para mantener el mismo session_id, el historial visible y si el panel estaba
// abierto entre una página y otra. sessionStorage se limpia solo cuando se cierra la pestaña/
// navegador — que es exactamente "hasta que salga del sitio y regrese".
const SS_SESSION_ID = "cc_session_id";
const SS_MESSAGES = "cc_messages";
const SS_GREETED = "cc_greeted";
const SS_OPEN = "cc_open";
const SS_LAST_ACTIVITY = "cc_last_activity";
const SS_PERSONA = "cc_persona";
const IDLE_TIMEOUT_MS = 2 * 60 * 1000; // sin actividad por este rato -> se cierra y se borra todo

// 3 concierges que rotan al azar, una vez por sesión — mismo hotel, mismos datos, pero cada
// uno con su propio nombre/foto y un matiz de tono distinto (definido en el backend).
const PERSONAS = [
  { key: "maria_paz", name: "María Paz", avatar: "maria-paz.png" },
  { key: "carlos", name: "Carlos", avatar: "carlos.png" },
  { key: "claudia", name: "Claudia", avatar: "claudia.png" },
];

function pickRandomPersona() {
  return PERSONAS[Math.floor(Math.random() * PERSONAS.length)];
}

let sessionId = sessionStorage.getItem(SS_SESSION_ID);
if (!sessionId) {
  sessionId = "widget-" + Math.random().toString(36).slice(2);
  sessionStorage.setItem(SS_SESSION_ID, sessionId);
}

let persona = PERSONAS.find((p) => p.key === sessionStorage.getItem(SS_PERSONA));
if (!persona) {
  persona = pickRandomPersona();
  sessionStorage.setItem(SS_PERSONA, persona.key);
}

function loadStoredMessages() {
  try {
    return JSON.parse(sessionStorage.getItem(SS_MESSAGES) || "[]");
  } catch {
    return [];
  }
}
function saveStoredMessages(list) {
  sessionStorage.setItem(SS_MESSAGES, JSON.stringify(list));
}

// El widget crea su propio contenedor si la página anfitriona no trae uno —
// así se puede soltar en cualquier página solo con el <link>/<script>, sin
// requerir markup adicional (spec, Sección 26: "el widget debe crear su propia UI").
let root = document.getElementById("concierge-root");
if (!root) {
  root = document.createElement("div");
  root.id = "concierge-root";
  document.body.appendChild(root);
}

function avatarUrl(p) {
  return `sol-de-oro-concierge/frontend/widget/assets/${p.avatar}?v=1`;
}
function buildGreeting(p) {
  return `¡Hola! Soy ${p.name}, Concierge Virtual del Hotel Sol de Oro. ¿Con quién tengo el gusto, y ya eres huésped del hotel o nos estás conociendo? Cuéntame también en qué te puedo ayudar.`;
}

// El botón cerrado muestra al EQUIPO (los 3 avatares superpuestos, spec: "hay un equipo de
// Concierge disponible para ayudarme"), con la persona activa de esta sesión al frente —
// las otras dos, detrás, comunican que hay respaldo sin dejar de ser claro con quién se habla.
function otherPersonas() {
  return PERSONAS.filter((p) => p.key !== persona.key);
}

root.innerHTML = `
  <button class="cc-bubble cc-team-toggle" id="ccToggle" aria-label="Abrir chat con el equipo Concierge de Sol de Oro" title="Equipo Concierge">
    <img class="cc-team-avatar cc-team-back2" src="${avatarUrl(otherPersonas()[1])}" alt="" />
    <img class="cc-team-avatar cc-team-back1" src="${avatarUrl(otherPersonas()[0])}" alt="" />
    <img class="cc-team-avatar cc-team-front" src="${avatarUrl(persona)}" alt="${persona.name}" />
  </button>
  <div class="cc-panel" id="ccPanel">
    <div class="cc-header">
      <img class="cc-avatar-small" src="${avatarUrl(persona)}" alt="${persona.name}" />
      <span id="ccHeaderName">${persona.name} · Sol de Oro</span>
      <button class="cc-minimize" id="ccMinimize" aria-label="Minimizar conversación" title="Minimizar">
        <svg viewBox="0 0 20 20" width="16" height="16" fill="none" aria-hidden="true">
          <path d="M4 7l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    <div class="cc-messages" id="ccMessages"></div>
    <div class="cc-input-row">
      <input type="text" id="ccInput" placeholder="Escribe tu pregunta..."/>
      <button id="ccSend">Enviar</button>
    </div>
  </div>
`;

const panel = document.getElementById("ccPanel");
const messagesEl = document.getElementById("ccMessages");
const input = document.getElementById("ccInput");
const sendBtn = document.getElementById("ccSend");
const toggleBtn = document.getElementById("ccToggle");

// Refleja la persona activa en el DOM — se llama al cargar y de nuevo cada vez que
// clearConversation() sortea una persona nueva (sin necesitar recargar la página).
function applyPersonaToDOM() {
  const others = otherPersonas();
  const front = document.querySelector(".cc-team-front");
  const back1 = document.querySelector(".cc-team-back1");
  const back2 = document.querySelector(".cc-team-back2");
  front.src = avatarUrl(persona);
  front.alt = persona.name;
  back1.src = avatarUrl(others[0]);
  back2.src = avatarUrl(others[1]);
  document.querySelectorAll(".cc-avatar-small").forEach((img) => {
    img.src = avatarUrl(persona);
    img.alt = persona.name;
  });
  document.getElementById("ccHeaderName").textContent = `${persona.name} · Sol de Oro`;
  toggleBtn.setAttribute("aria-label", `Abrir chat con el equipo Concierge de Sol de Oro`);
}

// --- Formato de texto: el modelo devuelve prosa en un solo bloque; para que no se vea como
// un muro de texto se separa en párrafos cortos (por oración) cuando el mensaje es largo.
// Importante: solo se corta en un terminador (. ! ?) seguido de un espacio REAL — un link con
// "?" o "." dentro (ej. wa.me/...?text=...%20...Oro.%20Mi...) no tiene espacios reales ahí
// (son %20), así que nunca se parte a la mitad de una URL. ---
function formatForDisplay(text) {
  const parts = text.split(/\n{2,}/); // respeta saltos ya existentes (ej. línea de contacto)
  return parts
    .map((part) => {
      if (part.length <= 160) return part;
      const sentences = part.split(/(?<=[.!?])\s+/);
      const paragraphs = [];
      let current = "";
      for (const s of sentences) {
        if (current && (current + " " + s).length > 160) {
          paragraphs.push(current.trim());
          current = s;
        } else {
          current = current ? current + " " + s : s;
        }
      }
      if (current.trim()) paragraphs.push(current.trim());
      return paragraphs.join("\n\n");
    })
    .join("\n\n");
}

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Esquemas seguros para un href real: http(s), mailto, o una ruta relativa del propio sitio
// (nunca empieza con un esquema). Bloquea "javascript:", "data:", "vbscript:" y variantes.
const SAFE_URL_RE = /^(https?:|mailto:|[a-z0-9][a-z0-9._/-]*\.html)/i;

// Negrita simple sobre texto YA escapado — usada para el label de un link markdown, que puede
// traer su propia **negrita** anidada (ej. CTAs: "[**Ver habitaciones →**](url)"). Escapar
// primero es seguro porque escapeHtml() no toca los asteriscos, así el marcador sobrevive.
function formatLabel(label) {
  return escapeHtml(label).replace(/\*\*([^*\n]+)\*\*/g, (_, b) => `<strong>${b}</strong>`);
}

// Formato enriquecido para los mensajes del asistente: **negrita**, *cursiva*, links markdown
// [texto](url) (internos del sitio o externos/WhatsApp) y, como red de seguridad, URLs planas
// sueltas también quedan clickeables. Todo lo demás se escapa como texto plano — no hay riesgo
// de HTML/XSS colado, y una URL inventada ya fue filtrada en el backend antes de llegar acá.
function richFormat(text) {
  const TOKEN_RE = /(\[[^\]]+\]\([^)]+\))|(\*\*[^*\n]+\*\*)|(\*[^*\n]+\*)|(https?:\/\/[^\s)]+)/g;
  let result = "";
  let lastIndex = 0;
  let m;
  while ((m = TOKEN_RE.exec(text)) !== null) {
    result += escapeHtml(text.slice(lastIndex, m.index));
    const token = m[0];
    if (token[0] === "[") {
      const [, label, url] = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      // El backend ya filtra URLs inventadas antes de mandar el texto, pero esta es la última
      // línea de defensa antes de escribir un href real: nunca "javascript:", "data:" ni
      // similares — solo http(s), mailto o una ruta relativa del propio sitio.
      if (!SAFE_URL_RE.test(url.trim())) {
        result += formatLabel(label);
      } else {
        const isExternal = /^https?:\/\//.test(url);
        const attrs = isExternal ? ' target="_blank" rel="noopener noreferrer"' : "";
        result += `<a href="${escapeHtml(url)}"${attrs}>${formatLabel(label)}</a>`;
      }
    } else if (token.startsWith("**")) {
      result += `<strong>${escapeHtml(token.slice(2, -2))}</strong>`;
    } else if (token[0] === "*") {
      result += `<em>${escapeHtml(token.slice(1, -1))}</em>`;
    } else {
      // URL suelta (no envuelta en markdown) — red de seguridad por si el modelo la escribe
      // pelada pese a la instrucción. El link de WhatsApp trae el mensaje codificado (%20,
      // %C3%B3...) — mostrarlo tal cual se ve horrible, así que se usa una etiqueta clara.
      const label = token.includes("wa.me/") ? "Abrir WhatsApp →" : token;
      result += `<a href="${escapeHtml(token)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`;
    }
    lastIndex = m.index + token.length;
  }
  result += escapeHtml(text.slice(lastIndex));
  return result;
}

function renderMessage(role, text) {
  const div = document.createElement("div");
  div.className = `cc-msg ${role}`;
  if (role === "assistant") {
    div.innerHTML = richFormat(text);
  } else {
    div.textContent = text;
  }
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

// Tira de fotos con scroll horizontal para habitaciones/espacios del hotel que la respuesta
// acaba de mencionar — un par de fotos para mostrar, no una galería (pedido explícito: "sin
// bombardeo de imágenes"). Cada foto abre a tamaño completo en una pestaña nueva al tocarla.
function renderImageStrip(images) {
  if (!images || !images.length) return;
  const strip = document.createElement("div");
  strip.className = "cc-img-strip";
  for (const img of images) {
    const a = document.createElement("a");
    a.className = "cc-img-item";
    a.href = img.url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    const el = document.createElement("img");
    el.src = img.url;
    el.alt = img.name || "";
    el.loading = "lazy";
    a.appendChild(el);
    if (img.name) {
      const caption = document.createElement("span");
      caption.className = "cc-img-caption";
      caption.textContent = img.name;
      a.appendChild(caption);
    }
    strip.appendChild(a);
  }
  messagesEl.appendChild(strip);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Efecto "escrito": revela el mensaje del asistente palabra por palabra, con un ritmo
// variable (como si alguien lo tipeara de verdad) y una pausa breve tras cada oración —
// no de golpe, y no con un tick mecánico de velocidad constante.
function typeMessage(div, text, onDone) {
  if (prefersReducedMotion) {
    div.innerHTML = richFormat(text);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    onDone?.();
    return;
  }
  const words = text.split(/(\s+)/); // conserva los espacios como tokens propios
  let i = 0;
  let shown = "";
  const tick = () => {
    if (i >= words.length) {
      div.innerHTML = richFormat(text); // al terminar, vuelve clickeable cualquier link revelado
      messagesEl.scrollTop = messagesEl.scrollHeight;
      onDone?.();
      return;
    }
    const word = words[i++];
    shown += word;
    div.innerHTML = richFormat(shown); // markdown incompleto no matchea, se ve literal hasta cerrar
    messagesEl.scrollTop = messagesEl.scrollHeight;
    const endsSentence = /[.!?…]\s*$/.test(word);
    const base = 55 + Math.random() * 55; // ritmo humano, no uniforme
    const delay = endsSentence ? base + 220 : base;
    setTimeout(tick, delay);
  };
  tick();
}

function addMessage(role, text, { persist = true, animate = false, images = [] } = {}) {
  const formatted = role === "assistant" ? formatForDisplay(text) : text;
  const div = renderMessage(role, animate ? "" : formatted);
  if (animate) {
    // Las fotos aparecen recién cuando el texto terminó de "escribirse" — no antes.
    typeMessage(div, formatted, () => { if (images.length) renderImageStrip(images); });
  } else if (images.length) {
    renderImageStrip(images);
  }
  if (persist) {
    const stored = loadStoredMessages();
    stored.push({ role, text, images });
    saveStoredMessages(stored);
  }
}

function addLoading() {
  const div = document.createElement("div");
  div.className = "cc-msg assistant cc-msg-loading";
  div.id = "ccLoading";
  // Los típicos "..." de "está escribiendo" — el efecto reconocible de apps de mensajería,
  // en vez de un spinner genérico. Se reemplaza por el texto real en cuanto llega el primer chunk.
  div.innerHTML = '<span class="cc-typing" aria-label="Escribiendo..."><span></span><span></span><span></span></span>';
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  // El equipo (avatares del botón cerrado) "respira" mientras se procesa — señal de "el
  // equipo está atendiendo tu solicitud", no un spinner de sistema genérico.
  toggleBtn.classList.add("processing");
}

function removeLoading() {
  document.getElementById("ccLoading")?.remove();
  toggleBtn.classList.remove("processing");
}

// --- Restaurar sesión previa (misma pestaña, otra página del sitio) ---
const storedMessages = loadStoredMessages();
let hasGreeted = sessionStorage.getItem(SS_GREETED) === "1";
if (storedMessages.length) {
  for (const m of storedMessages) {
    renderMessage(m.role, m.role === "assistant" ? formatForDisplay(m.text) : m.text);
    if (m.images && m.images.length) renderImageStrip(m.images);
  }
} else if (hasGreeted) {
  // Se saludó en otra página pero no quedó historial (edge case raro) — no se re-saluda solo.
}
if (sessionStorage.getItem(SS_OPEN) === "1") {
  panel.classList.add("open");
}

function setPanelOpen(open) {
  panel.classList.toggle("open", open);
  sessionStorage.setItem(SS_OPEN, open ? "1" : "0");
  if (open && !hasGreeted) {
    hasGreeted = true;
    sessionStorage.setItem(SS_GREETED, "1");
    addMessage("assistant", buildGreeting(persona), { animate: true });
  }
}

document.getElementById("ccToggle").addEventListener("click", () => {
  touchActivity();
  setPanelOpen(!panel.classList.contains("open"));
});

// Flecha hacia abajo en la esquina del header — señal visible de que la conversación se puede
// minimizar (antes solo se podía cerrar volviendo a tocar el grupo de avatares, poco obvio).
document.getElementById("ccMinimize").addEventListener("click", () => {
  touchActivity();
  setPanelOpen(false);
});

// Revela un mensaje que va llegando en vivo por SSE — misma cadencia humana palabra por
// palabra que el saludo simulado, pero acá el contenido es real (tokens del modelo), no un
// texto ya conocido de antemano. Los chunks llegan por oración completa (ya sanitizada en el
// backend), así que nunca hay que esperar más de lo que tarda el modelo en generar.
function createStreamRenderer(div) {
  let queue = "";
  let shown = "";
  let full = "";
  let ticking = false;
  let finished = false;
  let doneResolve;
  const donePromise = new Promise((res) => { doneResolve = res; });

  function finalize() {
    div.innerHTML = richFormat(full);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    doneResolve(full);
  }

  function tick() {
    if (queue.length === 0) {
      ticking = false;
      if (finished) finalize();
      return;
    }
    const m = queue.match(/^(\s*\S+\s*)/);
    const word = m ? m[1] : queue;
    queue = queue.slice(word.length);
    shown += word;
    // richFormat sobre texto a medio revelar es seguro: un token markdown incompleto (ej.
    // "**Stan" sin cerrar) simplemente no matchea ningún patrón y se muestra literal hasta
    // que su cierre llegue en una vuelta siguiente — así nunca se ven asteriscos sueltos.
    div.innerHTML = richFormat(shown);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    const endsSentence = /[.!?…]\s*$/.test(word);
    const base = 55 + Math.random() * 55;
    const delay = endsSentence ? base + 220 : base;
    setTimeout(tick, delay);
  }

  return {
    pushChunk(text) {
      full += text;
      if (prefersReducedMotion) {
        shown = full;
        div.innerHTML = richFormat(shown);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return;
      }
      queue += text;
      if (!ticking) { ticking = true; tick(); }
    },
    finish() {
      finished = true;
      if (prefersReducedMotion || queue.length === 0) finalize();
      return donePromise;
    },
  };
}

async function send() {
  const message = input.value.trim();
  if (!message) return;
  touchActivity();
  addMessage("user", message);
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;
  addLoading();
  try {
    const resp = await fetch(STREAM_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, persona: persona.key }),
    });
    if (!resp.ok || !resp.body) throw new Error("stream unavailable");

    removeLoading();
    const div = renderMessage("assistant", ""); // burbuja vacía, se llena con los chunks reales
    const renderer = createStreamRenderer(div);

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    let images = [];
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const events = buf.split("\n\n");
      buf = events.pop(); // el último fragmento puede venir incompleto — se guarda para la próxima vuelta
      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data: ")) continue;
        const data = JSON.parse(line.slice(6));
        if (data.type === "chunk") renderer.pushChunk(data.text);
        else if (data.type === "images") images = data.images;
      }
    }
    const fullText = await renderer.finish();
    if (images.length) renderImageStrip(images);
    touchActivity();
    const stored = loadStoredMessages();
    stored.push({ role: "assistant", text: fullText, images });
    saveStoredMessages(stored);
  } catch (err) {
    removeLoading();
    // Fallback: si el streaming falla a mitad de camino (navegador viejo, red inestable), se
    // reintenta con el endpoint no-streaming en vez de dejar al huésped sin respuesta.
    try {
      const resp = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId, persona: persona.key }),
      });
      const data = await resp.json();
      addMessage("assistant", data.message, { animate: true, images: data.images || [] });
      touchActivity();
    } catch (err2) {
      addMessage("assistant", "No pude conectarme al Concierge. Intenta de nuevo.");
    }
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

sendBtn.addEventListener("click", send);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });

// --- Cierre automático por inactividad: si el huésped no interactúa durante IDLE_TIMEOUT_MS,
// se cierra el panel y se borra toda la conversación — la próxima vez que abra empieza de cero.
// Se guarda la marca de tiempo en sessionStorage (no un setTimeout suelto) para que el conteo
// sobreviva si el huésped navega a otra página del sitio mientras tanto. ---
function touchActivity() {
  sessionStorage.setItem(SS_LAST_ACTIVITY, String(Date.now()));
}

function clearConversation() {
  sessionStorage.removeItem(SS_MESSAGES);
  sessionStorage.removeItem(SS_GREETED);
  sessionStorage.removeItem(SS_OPEN);
  sessionStorage.removeItem(SS_LAST_ACTIVITY);
  panel.classList.remove("open");
  messagesEl.innerHTML = "";
  hasGreeted = false;
  sessionId = "widget-" + Math.random().toString(36).slice(2);
  sessionStorage.setItem(SS_SESSION_ID, sessionId);
  // Sesión nueva -> se vuelve a sortear la persona (María Paz / Carlos / Claudia).
  persona = pickRandomPersona();
  sessionStorage.setItem(SS_PERSONA, persona.key);
  applyPersonaToDOM();
}

function checkIdle() {
  const hasConversation = loadStoredMessages().length > 0 || panel.classList.contains("open");
  if (!hasConversation) return;
  const last = Number(sessionStorage.getItem(SS_LAST_ACTIVITY) || 0);
  if (last && Date.now() - last > IDLE_TIMEOUT_MS) {
    clearConversation();
  }
}
checkIdle(); // por si el tiempo ya pasó mientras el huésped estaba en otra página del sitio
setInterval(checkIdle, 15000);
