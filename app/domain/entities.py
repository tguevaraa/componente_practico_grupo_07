# Contendrá: EcuacionSegundoOrden
import math
from .solutions import Solucion, SolucionRealesDistintas, SolucionRealesIguales, SolucionComplejas

class EcuacionSegundoOrden:
    """
    Clase que encapsula los coeficientes y lógica matemática de una ecuación
    diferencial homogénea de segundo orden con coeficientes constantes.
    """
    
    def __init__(self, a: float, b: float, c: float):
        self.a = a
        self.b = b
        self.c = c
        self.discriminante = self._calcular_discriminante()
        
    def _calcular_discriminante(self) -> float:
        return self.b**2 - 4 * self.a * self.c
        
    def obtener_representacion(self) -> str:
        """Retorna la representación formal de la ecuación diferencial."""
        return f"{self.a}y'' {self.b:+}y' {self.c:+}y = 0"
        
    def resolver(self) -> Solucion:
        """Resuelve la ecuación y retorna el objeto Solucion correspondiente."""
        match self.discriminante:
            case d if d > 0:
                r1 = (-self.b + math.sqrt(d)) / (2 * self.a)
                r2 = (-self.b - math.sqrt(d)) / (2 * self.a)
                return SolucionRealesDistintas(r1, r2)
                
            case 0:
                r = -self.b / (2 * self.a)
                return SolucionRealesIguales(r)
                
            case _:
                real = -self.b / (2 * self.a)
                imag = math.sqrt(-self.discriminante) / (2 * self.a)
                return SolucionComplejas(real, imag)