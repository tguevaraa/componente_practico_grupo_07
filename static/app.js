/* ============================================================
   app.js — lógica de la interfaz web del solucionador de EDO
   Historial en localStorage → funciona en local y en Vercel
   ============================================================ */

const STORAGE_KEY = 'edo_historial';

// ------------------------------------------------------------------
// localStorage — historial del cliente
// ------------------------------------------------------------------
function storageLoad() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
  catch { return []; }
}

function storageSave(lista) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(lista));
}

function storageAdd(datos) {
  const lista = storageLoad();
  const entrada = Object.assign({}, datos, {
    id: lista.length + 1,
    timestamp: new Date().toLocaleString('es-EC'),
  });
  lista.push(entrada);
  storageSave(lista);
  return lista;
}

// ------------------------------------------------------------------
// API helpers (solo resolver + PDF)
// ------------------------------------------------------------------
const API = {
  resolver(a, b, c) {
    return fetch('/api/resolver', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ a, b, c }),
    }).then(parseJson);
  },
  descargarPDF(lista) {
    return fetch('/api/descargar-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lista),
    });
  },
};

async function parseJson(res) {
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ------------------------------------------------------------------
// Math rendering
// ------------------------------------------------------------------
function typeset(el) {
  if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
    MathJax.typesetPromise([el]).catch(console.error);
  }
}

// ------------------------------------------------------------------
// Alert
// ------------------------------------------------------------------
function showError(msg) {
  const alert = document.getElementById('alert');
  document.getElementById('alert-msg').textContent = msg;
  alert.classList.remove('hidden');
}
function closeAlert() {
  document.getElementById('alert').classList.add('hidden');
}

// ------------------------------------------------------------------
// Spinner
// ------------------------------------------------------------------
function setLoading(loading) {
  const btn = document.getElementById('btn-resolver');
  btn.querySelector('.btn-text').textContent = loading ? 'Calculando…' : 'Resolver';
  btn.querySelector('.btn-spinner').classList.toggle('hidden', !loading);
  btn.disabled = loading;
}

// ------------------------------------------------------------------
// Result display
// ------------------------------------------------------------------
let currentResult = null;

function showResult(data) {
  currentResult = data;

  const discSign = data.discriminante > 0 ? '> 0'
                 : data.discriminante === 0 ? '= 0' : '< 0';

  const html = `
    <div class="result-eq-display">\\[ ${data.ecuacion_latex} \\]</div>

    <span class="caso-badge caso-${data.caso}">Caso ${data.caso}: ${data.tipo}</span>

    <div class="discriminant-info">
      Discriminante: D = ${fmtNum(data.discriminante)} ${discSign}
    </div>

    <div class="result-section">
      <div class="result-section-label">Raíces</div>
      <div class="result-section-math">\\[ ${data.raices_latex} \\]</div>
    </div>

    <div class="result-section">
      <div class="result-section-label">Solución general</div>
      <div class="result-section-math">\\[ ${data.solucion_latex} \\]</div>
    </div>

    <button id="btn-save" class="btn-save">Guardar esta ecuación</button>
  `;

  const content = document.getElementById('result-content');
  const empty   = document.getElementById('result-empty');

  content.innerHTML = html;
  content.classList.remove('hidden');
  empty.classList.add('hidden');

  typeset(content);

  document.getElementById('btn-save').addEventListener('click', handleGuardar);
}

function fmtNum(n) {
  if (typeof n !== 'number') return n;
  return Number.isInteger(n) ? n : parseFloat(n.toFixed(6));
}

// ------------------------------------------------------------------
// Save handler — guarda en localStorage
// ------------------------------------------------------------------
function handleGuardar() {
  if (!currentResult) return;
  const btn = document.getElementById('btn-save');
  btn.disabled = true;

  const lista = storageAdd(currentResult);
  btn.textContent = '¡Guardada ✓';
  btn.classList.add('saved');
  renderHistory(lista);
}

// ------------------------------------------------------------------
// History — lee desde localStorage
// ------------------------------------------------------------------
function loadHistory() {
  renderHistory(storageLoad());
}

function renderHistory(lista) {
  const container = document.getElementById('historial');
  const pdfBtn    = document.getElementById('btn-pdf');

  if (!lista || lista.length === 0) {
    container.innerHTML = '<p class="empty-msg">No hay ecuaciones guardadas aún.</p>';
    pdfBtn.disabled = true;
    return;
  }

  pdfBtn.disabled = false;

  const items = lista.map(eq => `
    <div class="hist-item">
      <div class="hist-header">
        <span class="hist-num">#${eq.id}</span>
        <span class="caso-badge caso-${eq.caso}" style="font-size:.75rem;padding:.2rem .6rem">
          Caso ${eq.caso}
        </span>
        <span class="hist-time">${eq.timestamp || ''}</span>
      </div>
      <div class="hist-eq">\\( ${eq.ecuacion_latex} \\)</div>
      <div class="hist-sol">\\( ${eq.solucion_latex} \\)</div>
    </div>
  `).join('');

  container.innerHTML = `<div class="hist-list">${items}</div>`;
  typeset(container);
}

// ------------------------------------------------------------------
// PDF download — envía la lista del localStorage al servidor
// ------------------------------------------------------------------
async function handleDownloadPDF() {
  const lista = storageLoad();
  const btn   = document.getElementById('btn-pdf');
  btn.disabled = true;
  btn.textContent = 'Generando…';

  try {
    const res = await API.descargarPDF(lista);
    if (!res.ok) {
      const body = await res.json();
      throw new Error(body.error || 'Error al generar el PDF');
    }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = 'historial_ecuaciones.pdf';
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    showError(err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
           viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      Descargar PDF`;
  }
}

// ------------------------------------------------------------------
// Init
// ------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  loadHistory();

  document.getElementById('form-ec').addEventListener('submit', async (e) => {
    e.preventDefault();
    closeAlert();

    const a = parseFloat(document.getElementById('coef-a').value);
    const b = parseFloat(document.getElementById('coef-b').value);
    const c = parseFloat(document.getElementById('coef-c').value);

    setLoading(true);
    try {
      const result = await API.resolver(a, b, c);
      showResult(result);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  });

  document.getElementById('btn-pdf').addEventListener('click', handleDownloadPDF);
});
