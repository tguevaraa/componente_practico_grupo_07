# Contendrá: GestorPersistencia
from ..domain.entities import EcuacionSegundoOrden
from ..domain.solutions import Solucion

class GestorPersistencia:
    """Clase encargada del almacenamiento y persistencia de las resoluciones."""
    
    def __init__(self, ruta_archivo: str = "lista_ecuaciones.txt"):
        self.ruta_archivo = ruta_archivo
        
    def registrar_resolucion(self, ecuacion: EcuacionSegundoOrden, solucion: Solucion) -> None:
        """Guarda los detalles de la ecuación y su solución en el archivo."""
        with open(self.ruta_archivo, "a", encoding="utf-8") as archivo:
            solucion.guardar_en_archivo(archivo, ecuacion.obtener_representacion())