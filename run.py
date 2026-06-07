#!/usr/bin/env python3
# Punto de entrada principal de la aplicación
from app.presentation.cli import InterfazUsuario

if __name__ == "__main__":
    app = InterfazUsuario()
    app.ejecutar()