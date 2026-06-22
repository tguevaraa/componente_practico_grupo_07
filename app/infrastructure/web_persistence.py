import json
import os
import tempfile
from datetime import datetime


class WebGestorPersistencia:
    """Persistencia JSON para la interfaz web. Diseñada para migrar a Google Drive."""

    def __init__(self, ruta_archivo: str = None):
        # Usa /tmp en Vercel (solo lectura en /var/task) y AppData\Local\Temp en Windows
        if ruta_archivo is None:
            ruta_archivo = os.path.join(tempfile.gettempdir(), 'ecuaciones_web.json')
        self.ruta_archivo = ruta_archivo
        if not os.path.exists(self.ruta_archivo):
            with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def listar(self) -> list:
        if not os.path.exists(self.ruta_archivo):
            return []
        with open(self.ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)

    def agregar(self, datos: dict) -> None:
        ecuaciones = self.listar()
        entrada = dict(datos)
        entrada['id'] = len(ecuaciones) + 1
        entrada['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ecuaciones.append(entrada)
        with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(ecuaciones, f, ensure_ascii=False, indent=2)
