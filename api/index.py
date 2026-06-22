import sys, os
# Asegura que el directorio raíz del proyecto esté en el path de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.presentation.web import flask_app as app  # Vercel busca una variable llamada 'app'
