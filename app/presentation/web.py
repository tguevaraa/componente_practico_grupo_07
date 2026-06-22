import os

from flask import Flask, jsonify, render_template, request, send_file

from ..domain.entities import EcuacionSegundoOrden
from ..infrastructure.pdf_generator import GeneradorPDF
from ..infrastructure.web_persistence import WebGestorPersistencia

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

flask_app = Flask(
    __name__,
    template_folder=os.path.join(_ROOT, 'templates'),
    static_folder=os.path.join(_ROOT, 'static'),
)

_gestor = WebGestorPersistencia()
_pdf_gen = GeneradorPDF()


@flask_app.route('/')
def index():
    return render_template('index.html')


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


@flask_app.route('/api/descargar-pdf', methods=['GET', 'POST'])
def descargar_pdf():
    # POST: el cliente envía las ecuaciones (Vercel / producción)
    # GET:  se leen del archivo local (desarrollo con run_web.py)
    if request.method == 'POST':
        ecuaciones = request.get_json(silent=True) or []
    else:
        ecuaciones = _gestor.listar()

    if not ecuaciones:
        return jsonify({'error': 'No hay ecuaciones guardadas aún.'}), 400

    pdf_path = _pdf_gen.generar(ecuaciones)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name='historial_ecuaciones.pdf',
        mimetype='application/pdf',
    )
