/* ============================================================
   app.js — lógica de la interfaz web del solucionador de EDO
   Historial en localStorage → funciona en local y en Vercel
   ============================================================ */

const STORAGE_KEY_BASE = 'edo_historial';

// Clave dinámica: por usuario si hay sesión, anónima si no
function storageKey() {
  return _authUser ? `${STORAGE_KEY_BASE}_${_authUser}` : STORAGE_KEY_BASE;
}

// ------------------------------------------------------------------
// localStorage — historial del cliente
// ------------------------------------------------------------------
function storageLoad() {
  try { return JSON.parse(localStorage.getItem(storageKey()) || '[]'); }
  catch { return []; }
}

function storageSave(lista) {
  localStorage.setItem(storageKey(), JSON.stringify(lista));
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

  const items = lista.map((eq, idx) => `
    <div class="hist-item">
      <div class="hist-header">
        <span class="hist-num">#${eq.id}</span>
        <span class="caso-badge caso-${eq.caso}" style="font-size:.75rem;padding:.2rem .6rem">
          Caso ${eq.caso}
        </span>
        <span class="hist-time">${eq.timestamp || ''}</span>
        <button class="btn-delete-eq" onclick="deleteEquation(${idx})" title="Eliminar ecuación">&times;</button>
      </div>
      <div class="hist-eq">\\( ${eq.ecuacion_latex} \\)</div>
      <div class="hist-sol">\\( ${eq.solucion_latex} \\)</div>
    </div>
  `).join('');

  container.innerHTML = `<div class="hist-list">${items}</div>`;
  typeset(container);
}

// ------------------------------------------------------------------
// Delete equation from history
// ------------------------------------------------------------------
function deleteEquation(idx) {
  const lista = storageLoad();
  lista.splice(idx, 1);
  // Re-numerar ids
  lista.forEach((eq, i) => eq.id = i + 1);
  storageSave(lista);
  renderHistory(lista);
}

// ------------------------------------------------------------------
// PDF download — envía la lista del localStorage al servidor
// ------------------------------------------------------------------
function svgDownload() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
    viewBox="0 0 24 24" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>`;
}
async function handleDownloadPDF() {
  const lista = storageLoad();
  const btn   = document.getElementById('btn-pdf');
  btn.disabled = true;
  btn.textContent = 'Generando…';

  try {
    const res = await API.descargarPDF(lista);
    if (res.status === 401) {
      const body = await res.json();
      if (body.error === 'login_required') {
        btn.disabled = false;
        btn.innerHTML = svgDownload() + ' Descargar PDF';
        openAuthModal('login', true);
        return;
      }
      throw new Error(body.message || 'No autorizado');
    }
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
    btn.innerHTML = svgDownload() + ' Descargar PDF';
  }
}

// ------------------------------------------------------------------
// Auth state
// ------------------------------------------------------------------
let _authUser   = null;  // email o null
let _authNombre = null;  // nombre para mostrar en header

async function checkAuthStatus() {
  try {
    const res = await fetch('/api/auth/status');
    const data = await res.json();
    _authUser   = data.logged_in ? data.email   : null;
    _authNombre = data.logged_in ? data.nombres : null;
  } catch {
    _authUser   = null;
    _authNombre = null;
  }
  renderAuthArea();
}

function renderAuthArea() {
  const userEl    = document.getElementById('auth-user');
  const logoutBtn = document.getElementById('btn-logout');
  const loginBtn  = document.getElementById('btn-open-auth');

  if (_authUser) {
    userEl.textContent = _authNombre ? `Hola, ${_authNombre.split(' ')[0]}` : _authUser;
    userEl.classList.remove('hidden');
    logoutBtn.classList.remove('hidden');
    loginBtn.classList.add('hidden');
  } else {
    userEl.classList.add('hidden');
    logoutBtn.classList.add('hidden');
    loginBtn.classList.remove('hidden');
  }
}

async function handleLogout() {
  await fetch('/api/auth/logout', { method: 'POST' });
  _authUser   = null;
  _authNombre = null;
  renderAuthArea();
  loadHistory();  // mostrar historial anónimo al cerrar sesión
}

// ------------------------------------------------------------------
// Auth modal
// ------------------------------------------------------------------
let _currentTab = 'login';
let _pendingPdfAfterLogin = false;

function openAuthModal(tab = 'login', pendingPdf = false) {
  _pendingPdfAfterLogin = pendingPdf;
  switchTab(tab);
  document.getElementById('auth-modal').classList.remove('hidden');
  document.getElementById('auth-email').focus();
}

function closeAuthModal(e) {
  if (e && e.target !== document.getElementById('auth-modal')) return;
  document.getElementById('auth-modal').classList.add('hidden');
  document.getElementById('auth-error').classList.add('hidden');
  document.getElementById('auth-form').reset();
}

function switchTab(tab) {
  _currentTab = tab;
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
  document.getElementById('auth-btn-text').textContent = tab === 'login' ? 'Ingresar' : 'Crear cuenta';
  document.getElementById('modal-desc').textContent = tab === 'login'
    ? 'Inicia sesión para descargar PDF ilimitado.'
    : 'Crea tu cuenta gratuita — solo toma un momento.';
  document.getElementById('auth-error').classList.add('hidden');

  const isRegister = tab === 'register';
  document.getElementById('fields-login').classList.toggle('hidden', isRegister);
  document.getElementById('fields-register').classList.toggle('hidden', !isRegister);
  document.querySelector('.modal-box').classList.toggle('wide', isRegister);
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const email    = document.getElementById('auth-email').value.trim();
  const password = document.getElementById('auth-password').value;
  const errEl    = document.getElementById('auth-error');
  const submitBtn = document.getElementById('btn-auth-submit');

  errEl.classList.add('hidden');
  submitBtn.disabled = true;

  const isRegister = _currentTab === 'register';
  const endpoint   = isRegister ? '/api/auth/register' : '/api/auth/login';

  let body;
  if (isRegister) {
    const email    = document.getElementById('reg-email').value.trim();
    const email2   = document.getElementById('reg-email2').value.trim();
    const password = document.getElementById('reg-password').value;
    const password2= document.getElementById('reg-password2').value;

    if (email !== email2) {
      errEl.textContent = 'Los correos no coinciden.';
      errEl.classList.remove('hidden');
      submitBtn.disabled = false;
      return;
    }
    if (password !== password2) {
      errEl.textContent = 'Las contraseñas no coinciden.';
      errEl.classList.remove('hidden');
      submitBtn.disabled = false;
      return;
    }

    body = {
      email,
      password,
      nombres:          document.getElementById('reg-nombres').value.trim(),
      fecha_nacimiento: document.getElementById('reg-fecha').value || null,
      pais:             document.getElementById('reg-pais').value.trim(),
      provincia:        document.getElementById('reg-provincia').value.trim(),
      ciudad:           document.getElementById('reg-ciudad').value.trim(),
      rol:              document.getElementById('reg-rol').value || null,
      nivel:            document.getElementById('reg-nivel').value || null,
      genero:           document.getElementById('reg-genero').value || null,
      institucion:      document.getElementById('reg-institucion').value.trim(),
    };
  } else {
    body = { email, password };
  }

  try {
    const res  = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();

    if (!res.ok) {
      errEl.textContent = data.error || 'Error al autenticar.';
      errEl.classList.remove('hidden');
      return;
    }

    _authUser   = data.email;
    _authNombre = data.nombres || data.email;
    renderAuthArea();
    loadHistory();  // recargar historial con la key del usuario
    document.getElementById('auth-modal').classList.add('hidden');
    document.getElementById('auth-form').reset();

    if (_pendingPdfAfterLogin) {
      _pendingPdfAfterLogin = false;
      handleDownloadPDF();
    }
  } catch {
    errEl.textContent = 'Error de conexión. Inténtalo de nuevo.';
    errEl.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
  }
}

// ------------------------------------------------------------------
// Init
// ------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  checkAuthStatus();
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
  document.getElementById('auth-form').addEventListener('submit', handleAuthSubmit);
});
