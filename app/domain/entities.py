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
        def fmt(v):
            r = round(v, 9)
            return str(int(r)) if r == int(r) else f'{v:g}'
        a, b, c = fmt(self.a), fmt(self.b), fmt(self.c)
        b_sign = f'+{b}' if self.b >= 0 else b
        c_sign = f'+{c}' if self.c >= 0 else c
        return f"{a}y'' {b_sign}y' {c_sign}y = 0"
        
    def to_latex(self) -> str:
        """Retorna la ecuación como string LaTeX limpio para MathJax."""
        parts = []

        def add_term(coef, var):
            if coef == 0:
                return
            c = int(coef) if coef == int(coef) else coef
            is_first = len(parts) == 0
            if is_first:
                if c == 1:
                    parts.append(var)
                elif c == -1:
                    parts.append(f'-{var}')
                else:
                    parts.append(f'{c:g}{var}')
            else:
                if c == 1:
                    parts.append(f'+ {var}')
                elif c == -1:
                    parts.append(f'- {var}')
                elif c > 0:
                    parts.append(f'+ {c:g}{var}')
                else:
                    parts.append(f'- {abs(c):g}{var}')

        add_term(self.a, "y''")
        add_term(self.b, "y'")
        add_term(self.c, 'y')
        return ' '.join(parts) + ' = 0'

    def resolver(self) -> Solucion:
        """Resuelve la ecuación y retorna el objeto Solucion correspondiente."""
        d = self.discriminante
        if d > 0:
            r1 = (-self.b + math.sqrt(d)) / (2 * self.a)
            r2 = (-self.b - math.sqrt(d)) / (2 * self.a)
            return SolucionRealesDistintas(r1, r2)
        elif d == 0:
            r = -self.b / (2 * self.a)
            return SolucionRealesIguales(r)
        else:
            real = -self.b / (2 * self.a)
            imag = math.sqrt(-d) / (2 * self.a)
            return SolucionComplejas(real, imag)