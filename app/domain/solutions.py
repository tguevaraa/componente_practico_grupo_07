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