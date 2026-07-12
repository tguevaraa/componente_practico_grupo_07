#!/usr/bin/env python3
import os
from pathlib import Path

# Cargar .env si existe
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

from app.presentation.web import flask_app

if __name__ == '__main__':
    print("Servidor iniciado en  http://127.0.0.1:5000")
    flask_app.run(debug=True, host='127.0.0.1', port=5000)
