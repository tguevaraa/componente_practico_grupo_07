import os
import hashlib

from flask import Flask, jsonify, render_template, request, send_file, session
from flask_sqlalchemy import SQLAlchemy

from ..domain.entities import EcuacionSegundoOrden
from ..infrastructure.pdf_generator import GeneradorPDF
from ..infrastructure.web_persistence import WebGestorPersistencia

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

flask_app = Flask(
    __name__,
    template_folder=os.path.join(_ROOT, 'templates'),
    static_folder=os.path.join(_ROOT, 'static'),
)

flask_app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-edo-unemi-2024')

_DB_URL = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:aqFvCTSKpezdQzGjrnZbOEuYQpQqHmCU@tokaido.proxy.rlwy.net:48787/railway'
)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = _DB_URL
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(flask_app)

PDF_FREE_LIMIT = 4


# ──────────────────────────────────────────────
# Modelo
# ──────────────────────────────────────────────

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id                 = db.Column(db.Integer, primary_key=True)
    email              = db.Column(db.String(120), unique=True, nullable=False)
    password           = db.Column(db.String(64),  nullable=False)
    nombres            = db.Column(db.String(120),  nullable=False)
    fecha_nacimiento   = db.Column(db.Date,         nullable=True)
    pais               = db.Column(db.String(80),   nullable=True)
    provincia          = db.Column(db.String(80),   nullable=True)
    ciudad             = db.Column(db.String(80),   nullable=True)
    rol                = db.Column(db.String(20),   nullable=True)   # 'estudiante' | 'maestro'
    nivel              = db.Column(db.String(20),   nullable=True)   # 'bachiller' | 'grado' | 'postgrado'
    institucion        = db.Column(db.String(180),  nullable=True)

    def verificar_password(self, password: str) -> bool:
        return self.password == _hash(password)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


with flask_app.app_context():
    db.create_all()


_gestor  = WebGestorPersistencia()
_pdf_gen = GeneradorPDF()


# ──────────────────────────────────────────────
# Páginas
# ──────────────────────────────────────────────

@flask_app.route('/')
def index():
    return render_template('index.html')


# ──────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────

@flask_app.route('/api/auth/status', methods=['GET'])
def auth_status():
    email   = session.get('user')
    nombres = session.get('nombres')
    return jsonify({'logged_in': email is not None, 'email': email, 'nombres': nombres})


@flask_app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json(silent=True) or {}

    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    nombres  = (data.get('nombres') or '').strip()

    if not email or not password or not nombres:
        return jsonify({'error': 'Email, nombre y contraseña son requeridos.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres.'}), 400
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'Ese correo ya está registrado.'}), 409

    from datetime import date
    raw_fecha = data.get('fecha_nacimiento') or ''
    fecha = None
    if raw_fecha:
        try:
            fecha = date.fromisoformat(raw_fecha)
        except ValueError:
            pass

    usuario = Usuario(
        email            = email,
        password         = _hash(password),
        nombres          = nombres,
        fecha_nacimiento = fecha,
        pais             = (data.get('pais') or '').strip() or None,
        provincia        = (data.get('provincia') or '').strip() or None,
        ciudad           = (data.get('ciudad') or '').strip() or None,
        rol              = data.get('rol') or None,
        nivel            = data.get('nivel') or None,
        institucion      = (data.get('institucion') or '').strip() or None,
    )
    db.session.add(usuario)
    db.session.commit()

    session['user'] = email
    session['nombres'] = nombres
    return jsonify({'ok': True, 'email': email, 'nombres': nombres}), 201


@flask_app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not usuario.verificar_password(password):
        return jsonify({'error': 'Correo o contraseña incorrectos.'}), 401

    session['user']    = email
    session['nombres'] = usuario.nombres
    return jsonify({'ok': True, 'email': email, 'nombres': usuario.nombres})


@flask_app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    session.pop('user', None)
    session.pop('nombres', None)
    return jsonify({'ok': True})


# ──────────────────────────────────────────────
# Resolución
# ──────────────────────────────────────────────

@flask_app.route('/api/resolver', methods=['POST'])
def resolver():
    data = request.get_json(silent=True) or {}
    try:
        a = float(data['a'])
        b = float(data['b'])
        c = float(data['c'])
    except (KeyError, TypeError, ValueError):
        return jsonify({'error': 'Coeficientes inválidos.'}), 400

    if a == 0:
        return jsonify({'error': "El coeficiente 'a' no puede ser 0 — la ecuación no sería de segundo orden."}), 400

    try:
        ecuacion = EcuacionSegundoOrden(a, b, c)
        solucion = ecuacion.resolver()
        return jsonify({
            'ecuacion_str': ecuacion.obtener_representacion(),
            'ecuacion_latex': ecuacion.to_latex(),
            'discriminante': ecuacion.discriminante,
            **solucion.to_dict(),
        })
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ──────────────────────────────────────────────
# Persistencia
# ──────────────────────────────────────────────

@flask_app.route('/api/guardar', methods=['POST'])
def guardar():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Sin datos'}), 400
    _gestor.agregar(data)
    return jsonify({'ok': True, 'total': len(_gestor.listar())})


@flask_app.route('/api/ecuaciones', methods=['GET'])
def listar_ecuaciones():
    return jsonify(_gestor.listar())


# ──────────────────────────────────────────────
# PDF (con límite freemium)
# ──────────────────────────────────────────────

@flask_app.route('/api/descargar-pdf', methods=['GET', 'POST'])
def descargar_pdf():
    if request.method == 'POST':
        ecuaciones = request.get_json(silent=True) or []
    else:
        ecuaciones = _gestor.listar()

    if not ecuaciones:
        return jsonify({'error': 'No hay ecuaciones guardadas aún.'}), 400

    if len(ecuaciones) > PDF_FREE_LIMIT and not session.get('user'):
        return jsonify({
            'error': 'login_required',
            'message': f'Para descargar un PDF con más de {PDF_FREE_LIMIT} ecuaciones necesitas una cuenta.',
        }), 401

    pdf_path = _pdf_gen.generar(ecuaciones)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name='historial_ecuaciones.pdf',
        mimetype='application/pdf',
    )
