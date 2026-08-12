const API_URL = "http://localhost:8001/api/concierge";
const sessionId = "widget-" + Math.random().toString(36).slice(2);

// El widget crea su propio contenedor si la página anfitriona no trae uno —
// así se puede soltar en cualquier página solo con el <link>/<script>, sin
// requerir markup adicional (spec, Sección 26: "el widget debe crear su propia UI").
let root = document.getElementById("concierge-root");
if (!root) {
  root = document.createElement("div");
  root.id = "concierge-root";
  document.body.appendChild(root);
}
root.innerHTML = `
  <button class="cc-bubble" id="ccToggle" aria-label="Abrir chat con el Concierge">
    <span class="cc-blob cc-blob-1"></span>
    <span class="cc-blob cc-blob-2"></span>
    <span class="cc-blob cc-blob-3"></span>
    <span class="cc-blob-sheen"></span>
  </button>
  <div class="cc-panel" id="ccPanel">
    <div class="cc-header">Concierge · Sol de Oro</div>
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

document.getElementById("ccToggle").addEventListener("click", () => {
  panel.classList.toggle("open");
});

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `cc-msg ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addLoading() {
  const div = document.createElement("div");
  div.className = "cc-msg assistant cc-msg-loading";
  div.id = "ccLoading";
  div.innerHTML = '<span class="cc-loading" aria-label="Escribiendo..."></span>';
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function removeLoading() {
  document.getElementById("ccLoading")?.remove();
}

const sendBtn = document.getElementById("ccSend");

async function send() {
  const message = input.value.trim();
  if (!message) return;
  addMessage("user", message);
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;
  addLoading();
  try {
    const resp = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    const data = await resp.json();
    removeLoading();
    addMessage("assistant", data.message);
  } catch (err) {
    removeLoading();
    addMessage("assistant", "No pude conectarme al Concierge. Intenta de nuevo.");
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

sendBtn.addEventListener("click", send);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
