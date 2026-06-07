# Contendrá: InterfazUsuario (ejecución por consola)
from ..domain.entities import EcuacionSegundoOrden
from ..infrastructure.persistence import GestorPersistencia

class InterfazUsuario:
    """Clase responsable de la interacción con el usuario a través de la consola."""
    
    @staticmethod
    def solicitar_coeficiente(nombre: str, descripcion: str) -> float:
        """Solicita y valida la entrada de un coeficiente numérico float."""
        while True:
            try:
                valor = float(input(f"Ingrese el coeficiente {nombre} ({descripcion}) : "))
                return valor
            except ValueError:
                print("Entrada inválida. Por favor, ingrese un número.")
                
    def ejecutar(self) -> None:
        """Ejecuta el bucle principal de la aplicación."""
        gestor_persistencia = GestorPersistencia()
        
        while True:
            print("\n------ Ecuación de segundo orden con coeficientes constantes ------")
            a = self.solicitar_coeficiente("a", "de y'', si no tiene numero ponga 1 o si no hay el termino 'a' ponga 0")
            b = self.solicitar_coeficiente("b", "de y', si no tiene numero ponga 1 o si no hay el termino 'b' ponga 0")
            c = self.solicitar_coeficiente("c", "de y, si no tiene numero ponga 1 o si no hay el termino 'c' ponga 0")
            
            if a == 0:
                print("Error: El coeficiente 'a' no puede ser 0 para una ecuación de segundo orden.")
                print("=" * 60)
                continue
                
            try:
                ecuacion = EcuacionSegundoOrden(a, b, c)
                solucion = ecuacion.resolver()
                
                # Mostrar en consola
                print("-" * 60)
                solucion.mostrar_consola(ecuacion.obtener_representacion())
                print("-" * 60)
                
                # Guardar en archivo
                gestor_persistencia.registrar_resolucion(ecuacion, solucion)
                print("Resultado persistido correctamente en el historial.")
                
            except Exception as e:
                print(f"Ocurrió un error inesperado al resolver la ecuación: {e}")
                
            print("=" * 60)
            continuar = input("¿Desea resolver otra ecuación? (s/n): ").strip().lower()
            if continuar != 's':
                print("Finalizando aplicación...")
                break