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

async function send() {
  const message = input.value.trim();
  if (!message) return;
  addMessage("user", message);
  input.value = "";
  try {
    const resp = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    const data = await resp.json();
    addMessage("assistant", data.message);
  } catch (err) {
    addMessage("assistant", "No pude conectarme al Concierge. Intenta de nuevo.");
  }
}

document.getElementById("ccSend").addEventListener("click", send);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
