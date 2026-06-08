#este es el código original del algoritmo, se va a refactorizar 
#para cumplir con los principios SOLID y la arquitectura limpia, se va a dividir en varias clases y módulos para mejorar la mantenibilidad y escalabilidad del código. Además, se implementará una interfaz de usuario para interactuar con el usuario a través de la consola,
#y se añadirá una capa de persistencia para guardar el historial de ecuaciones resueltas.
import math

def resolver_ecuacion_segundo_orden(a, b, c):
    print(f"Ecuación: {a}y'' {b:+}y' {c:+}y = 0")
    discriminante = b**2 - 4*a*c

    # Usar match-case para los tres casos de raíces
    match discriminante:
        case d if d > 0:
            print("Caso 1: Raíces reales y distintas")
            r1 = (-b + math.sqrt(discriminante)) / (2*a)
            r2 = (-b - math.sqrt(discriminante)) / (2*a)
            print(f"Raíz 1: {r1:.0f}")
            print(f"Raíz 2: {r2:.0f}")
            print(f"Solución general: y(x) = C1*e^({r1:.0f}x) + C2*e^({r2:.0f}x)")
        case 0:
            print("Caso 2: Raíces reales e iguales")
            r = -b / (2*a)
            print(f"Raíz doble: {r:.0f}")
            print(f"Solución general: y(x) = (C1 + C2*x)*e^({r:.0f}x)")
        case _:
            print("Caso 3: Raíces complejas")
            real = -b / (2*a)
            imag = math.sqrt(-discriminante) / (2*a)
            print(f"Raíces: {real:.0f} ± {imag:.0f}i")
            print(f"Solución general: y(x) = e^({real:.0f}x) * [C1*cos({imag:.0f}x) + C2*sin({imag:.0f}x)]")

# Ejemplo para y'' - y' - 6y = 0

while True:
    print(f"------ Ecuación de segundo orden con coeicientes constantes ------")
    a = float(input("Ingrese el coeficiente a (de y'', si no tiene numero ponga 1 o si no hay el termino 'a' ponga 0) : "))
    b= float(input("Ingrese el coeficiente b (de y', si no tiene numero ponga 1 o si no hay el termino 'b' ponga 0) : "))
    c = float(input("Ingrese el coeficiente c (de y, si no tiene numero ponga 1 o si no hay el termino 'c' ponga 0) : "))
    resolver_ecuacion_segundo_orden(a, b, c)
    continuar = input("¿Desea resolver otra ecuación? (s/n): ").strip().lower()
    if continuar != 's':
        break