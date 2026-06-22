#!/usr/bin/env python3
from app.presentation.web import flask_app

if __name__ == '__main__':
    print("Servidor iniciado en  http://127.0.0.1:5000")
    flask_app.run(debug=True, host='127.0.0.1', port=5000)
