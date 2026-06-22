# Contendrá: Solucion (ABC) y sus 3 subclases derivadas
import math
from abc import ABC, abstractmethod

class Solucion(ABC):
    """
    Clase base abstracta que define la interfaz para las soluciones de una ecuación
    diferencial de segundo orden.
    """

    @abstractmethod
    def mostrar_consola(self, ecuacion_str: str) -> None:
        """Muestra los resultados de la solución en la consola."""
        pass

    @abstractmethod
    def guardar_en_archivo(self, archivo, ecuacion_str: str) -> None:
        """Escribe los resultados de la solución en el archivo proporcionado."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Retorna la solución como diccionario serializable para la API web."""
        pass

    @staticmethod
    def _fmt_val(val: float) -> str:
        r = round(val)
        return str(r) if r != 0 else '1'

    def _fmt_exp(self, val: float) -> str:
        v = round(val)
        if v == 0:   return ''   # 0 → 1 → e^{x}
        if v == 1:   return ''
        if v == -1:  return '-'
        return str(v)


class SolucionRealesDistintas(Solucion):
    """Representa la solución para el Caso 1: Raíces reales y distintas."""
    
    def __init__(self, r1: float, r2: float):
        self.r1 = r1
        self.r2 = r2
        
    def mostrar_consola(self, ecuacion_str: str) -> None:
        print(f"Ecuación: {ecuacion_str}")
        print("Caso 1: Raíces reales y distintas")
        print(f"Raíz 1: {self.r1:.0f}")
        print(f"Raíz 2: {self.r2:.0f}")
        print(f"Solución general: y(x) = C1*e^({self.r1:.0f}x) + C2*e^({self.r2:.0f}x)")
        
    def guardar_en_archivo(self, archivo, ecuacion_str: str) -> None:
        archivo.write(f"Ecuación: {ecuacion_str}\n")
        archivo.write(f"Raíz 1: {self.r1:.0f}\n")
        archivo.write(f"Raíz 2: {self.r2:.0f}\n")
        archivo.write(f"Solución general: y(x) = C1*e^({self.r1:.0f}x) + C2*e^({self.r2:.0f}x)\n")
        archivo.write("\n" + "=" * 60 + "\n")

    def to_dict(self) -> dict:
        e1, e2 = self._fmt_exp(self.r1), self._fmt_exp(self.r2)
        v1, v2 = self._fmt_val(self.r1), self._fmt_val(self.r2)
        return {
            'tipo': 'Raíces reales y distintas',
            'caso': 1,
            'raices': {'r1': self.r1, 'r2': self.r2},
            'raices_latex': f'r_1 = {v1}, \\quad r_2 = {v2}',
            'solucion_latex': f'y(x) = C_1\\, e^{{{e1}x}} + C_2\\, e^{{{e2}x}}',
        }


class SolucionRealesIguales(Solucion):
    """Representa la solución para el Caso 2: Raíces reales e iguales."""
    
    def __init__(self, r: float):
        self.r = r
        
    def mostrar_consola(self, ecuacion_str: str) -> None:
        print(f"Ecuación: {ecuacion_str}")
        print("Caso 2: Raíces reales e iguales")
        print(f"Raíz doble: {self.r:.0f}")
        print(f"Solución general: y(x) = (C1 + C2*x)*e^({self.r:.0f}x)")
        
    def guardar_en_archivo(self, archivo, ecuacion_str: str) -> None:
        archivo.write(f"Ecuación: {ecuacion_str}\n")
        archivo.write("Caso 2: Raíces reales e iguales\n")
        archivo.write(f"Raíz doble: {self.r:.0f}\n")
        archivo.write(f"Solución general: y(x) = (C1 + C2*x)*e^({self.r:.0f}x)\n")
        archivo.write("\n" + "=" * 60 + "\n")

    def to_dict(self) -> dict:
        e = self._fmt_exp(self.r)
        vr = self._fmt_val(self.r)
        return {
            'tipo': 'Raíces reales e iguales',
            'caso': 2,
            'raices': {'r': self.r},
            'raices_latex': f'r = {vr} \\;(\\text{{raíz doble}})',
            'solucion_latex': f'y(x) = (C_1 + C_2\\, x)\\, e^{{{e}x}}',
        }


class SolucionComplejas(Solucion):
    """Representa la solución para el Caso 3: Raíces complejas."""
    
    def __init__(self, real: float, imag: float):
        self.real = real
        self.imag = imag
        
    def mostrar_consola(self, ecuacion_str: str) -> None:
        print(f"Ecuación: {ecuacion_str}")
        print("Caso 3: Raíces complejas")
        print(f"Raíces: {self.real:.0f} ± {self.imag:.0f}i")
        print(f"Solución general: y(x) = e^({self.real:.0f}x) * [C1*cos({self.imag:.0f}x) + C2*sin({self.imag:.0f}x)]")
        
    def guardar_en_archivo(self, archivo, ecuacion_str: str) -> None:
        archivo.write(f"Ecuación: {ecuacion_str}\n")
        archivo.write("Caso 3: Raíces complejas\n")
        archivo.write(f"Raíces: {self.real:.0f} ± {self.imag:.0f}i\n")
        archivo.write(f"Solución general: y(x) = e^({self.real:.0f}x) * [C1*cos({self.imag:.0f}x) + C2*sin({self.imag:.0f}x)]\n")
        archivo.write("\n" + "=" * 60 + "\n")

    def to_dict(self) -> dict:
        real = 0.0 if self.real == 0 else self.real  # normaliza -0.0
        b_str = self._fmt_val(self.imag)
        ea = self._fmt_exp(real)
        vreal = self._fmt_val(real)
        if real == 0:
            sol = f'y(x) = C_1 \\cos({b_str}x) + C_2 \\sin({b_str}x)'
        else:
            sol = (f'y(x) = e^{{{ea}x}}\\left[C_1 \\cos({b_str}x) + '
                   f'C_2 \\sin({b_str}x)\\right]')
        return {
            'tipo': 'Raíces complejas conjugadas',
            'caso': 3,
            'raices': {'real': real, 'imag': self.imag},
            'raices_latex': f'r = {vreal} \\pm {b_str}\\,i',
            'solucion_latex': sol,
        }