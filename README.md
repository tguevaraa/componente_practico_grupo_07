# Caso de Estudio POO: Solucionador de Ecuaciones Diferenciales

**Asignatura:** Programación Orientada a Objetos;

**Nivel:** Intermedio — Arquitectura en capas y Polimorfismo

**Entregable:** Análisis, modelado UML y documentación del sistema

---

## Objetivo

Desarrollar un Motor de Resolución Analítica para ecuaciones diferenciales ordinarias de Segundo Orden con coeficientes constantes, aplicando los principios de la Programación Orientada a Objetos (POO). El diseño se basa en la separación de responsabilidades (Arquitectura en capas) y el uso intensivo del polimorfismo para manejar los diferentes casos matemáticos.

---

## 1. Enunciado del Problema

### 1.1 Contexto

La resolución manual de ecuaciones diferenciales del tipo $ay'' + by' + cy = 0$ requiere evaluar el discriminante de su ecuación característica para determinar el tipo de raíces (reales distintas, reales iguales o complejas) y estructurar la solución general. Para entornos académicos, se requiere una herramienta por consola que capture los coeficientes, aplique la lógica matemática correspondiente, muestre el resultado formal y mantenga un historial persistente de las operaciones en un archivo de texto.

---

### 1.2 Reglas de Negocio

El sistema debe garantizar las siguientes reglas (**invariantes del dominio**):

**Reglas matemáticas:**
- El coeficiente principal `a` no puede ser igual a 0. Si `a = 0`, la ecuación deja de ser de segundo orden.
- El discriminante ($D = b^2 - 4ac$) determina unívocamente el tipo de solución:
  - **D > 0:** Raíces reales y distintas. Modelo: $y(x) = C_1e^{r_1x} + C_2e^{r_2x}$
  - **D = 0:** Raíces reales e iguales. Modelo: $y(x) = (C_1 + C_2x)e^{rx}$
  - **D < 0:** Raíces complejas conjugadas. Modelo: $y(x) = e^{\\alpha x}[C_1\\cos(\\beta x) + C_2\\sin(\\beta x)]$

**Reglas de persistencia:**
- Cada ecuación resuelta debe anexarse (modo *append*) a un registro histórico (`lista_ecuaciones.txt`).
- El registro debe contener la notación de la ecuación original, el tipo de caso resuelto, los valores de las raíces y la solución general formateada.

---

### 1.3 Actores del Sistema

| Actor        | Descripción                                                                                       |
|--------------|---------------------------------------------------------------------------------------------------|
| **Usuario** | Estudiante o profesor que ingresa los coeficientes numéricos de la ecuación por consola.          |
| **Sistema** | Actor técnico que valida entradas, calcula raíces, aplica polimorfismo y persiste los datos.      |

---

### 1.4 Escenarios de Uso

**Escenario 1 — Ecuación con raíces reales distintas:**
El usuario ingresa los coeficientes $a=1$, $b=-3$, $c=2$ (Ecuación: $y'' - 3y' + 2y = 0$). El sistema valida que $a \\neq 0$. Calcula el discriminante ($D = 1$). Al ser $D > 0$, el sistema genera una solución de raíces reales distintas ($r_1=2, r_2=1$), muestra la solución $y(x) = C_1e^{2x} + C_2e^{1x}$ en pantalla y la anexa al archivo de historial.

**Escenario 2 — Validación de regla de negocio (a = 0):**
El usuario ingresa $a=0$, $b=4$, $c=4$. El sistema detecta que se viola la invariante del dominio ($a \\neq 0$), muestra un mensaje de error indicando que la ecuación no es de segundo orden y aborta el cálculo, solicitando un nuevo ingreso.

---

## 2. Análisis de Requerimientos

### 2.1 Requerimientos Funcionales

| ID    | Descripción                                                         |
|-------|---------------------------------------------------------------------|
| RF-01 | Capturar y validar coeficientes numéricos `a`, `b`, y `c`.          |
| RF-02 | Validar que el coeficiente `a` sea distinto de cero.                |
| RF-03 | Calcular el discriminante de la ecuación característica.            |
| RF-04 | Determinar el caso de la solución e instanciar el modelo matemático.|
| RF-05 | Mostrar la solución general estructurada por consola.               |
| RF-06 | Guardar un registro histórico de las ecuaciones resueltas en TXT.   |

### 2.2 Requerimientos No Funcionales

| ID     | Descripción                                         |
|--------|-----------------------------------------------------|
| RNF-01 | Implementación en Python sin librerías externas (solo `math` y `abc`). |
| RNF-02 | Arquitectura separada en capas (Dominio, Infraestructura, Presentación). |
| RNF-03 | Uso estricto de POO, especialmente el patrón *Factory* implícito y Polimorfismo. |
| RNF-04 | Interfaz de línea de comandos (CLI) interactiva e iterativa. |

---

## 3. Proceso de Abstracción y Análisis

> **Clave de abstracción:** Se separa la lógica matemática pura (dominio), las distintas representaciones de la solución (polimorfismo), la interacción con el usuario (presentación) y el almacenamiento en disco (infraestructura).

---

### 3.1 Identificación de Conceptos del Dominio

| Concepto                         | Tipo                    | Capa arquitectónica | Responsabilidad principal                                   |
|----------------------------------|-------------------------|---------------------|-------------------------------------------------------------|
| `Solucion`                       | Clase Abstracta (ABC)   | Dominio             | Define el contrato base para mostrar y guardar soluciones.  |
| `SolucionRealesDistintas`        | Entidad Concreta        | Dominio             | Estructura el Caso 1 (D > 0).                               |
| `SolucionRealesIguales`          | Entidad Concreta        | Dominio             | Estructura el Caso 2 (D = 0).                               |
| `SolucionComplejas`              | Entidad Concreta        | Dominio             | Estructura el Caso 3 (D < 0).                               |
| `EcuacionSegundoOrden`           | Entidad Principal       | Dominio             | Encapsula coeficientes, evalúa discriminante y crea solución|
| `GestorPersistencia`             | Servicio                | Infraestructura     | Escribe los objetos polimórficos de solución en un archivo. |
| `InterfazUsuario`                | Controlador/Vista       | Presentación        | Captura entradas seguras por consola y orquesta el flujo.   |

---

### 3.2 Análisis por Clase: Atributos y Métodos

#### `Solucion` — Interfaz Abstracta (Base)

| Método                                     | Retorno | Descripción                                                    |
|--------------------------------------------|---------|----------------------------------------------------------------|
| `mostrar_consola(ecuacion_str)`            | `None`  | Contrato abstracto para impresión estándar.                    |
| `guardar_en_archivo(archivo, ecuacion_str)`| `None`  | Contrato abstracto para inyección de la escritura en flujo IO. |

#### `EcuacionSegundoOrden` — Entidad Central

| Atributo         | Tipo    | Descripción                                  |
|------------------|---------|----------------------------------------------|
| `a`, `b`, `c`    | `float` | Coeficientes de la ecuación.                 |
| `discriminante`  | `float` | Calculado internamente en el constructor.    |

| Método                     | Descripción                                              |
|----------------------------|----------------------------------------------------------|
| `_calcular_discriminante()`| Retorna $b^2 - 4ac$. (Método privado)                    |
| `obtener_representacion()` | Formatea la ecuación matemática en un string presentable.|
| `resolver()`               | Evalúa el discriminante y retorna una subclase de `Solucion`. |

#### `GestorPersistencia` — Infraestructura

| Atributo       | Tipo   | Descripción                                 |
|----------------|--------|---------------------------------------------|
| `ruta_archivo` | `str`  | Ruta del archivo `.txt` (default: `lista_ecuaciones.txt`) |

| Método                                          | Descripción                                              |
|-------------------------------------------------|----------------------------------------------------------|
| `registrar_resolucion(ecuacion, solucion)`      | Abre el archivo en modo append y delega el formateo a la `solucion`. |

---

### 3.3 Aplicación de Técnicas POO

| # | Técnica              | Cómo se aplica en este sistema                                                                                  |
|---|----------------------|-----------------------------------------------------------------------------------------------------------------|
| 1 | **Abstracción** | `Solucion` usa el módulo `abc` para obligar a las clases derivadas a implementar métodos de salida, ocultando la complejidad de las matemáticas al resto del sistema. |
| 2 | **Polimorfismo** | `GestorPersistencia` y `InterfazUsuario` invocan `solucion.mostrar_consola()` sin importar si es el Caso 1, 2 o 3. La ejecución cambia dinámicamente según la clase concreta retornada por la ecuación. |
| 3 | **Encapsulamiento** | El cálculo del discriminante es privado (`_calcular_discriminante`) dentro de `EcuacionSegundoOrden`. El usuario externo no debe invocarlo manualmente. |
| 4 | **Inyección de Dependencias**| `GestorPersistencia` pasa el flujo de archivo (`archivo`) directamente al método `guardar_en_archivo`, permitiendo a la solución escribir sin conocer la ruta o el sistema de archivos subyacente. |
| 5 | **Factory Method** | El método `resolver()` en `EcuacionSegundoOrden` actúa como una fábrica implícita que decide qué subclase de `Solucion` instanciar según la lógica matemática. |

---

## 4. Relaciones entre Entidades (POO)

| Relación             | Clases involucradas                                         | Descripción                                                           |
|----------------------|-------------------------------------------------------------|-----------------------------------------------------------------------|
| Herencia / Realización| `SolucionRealesDistintas` ◁── `Solucion`                    | Las clases de casos matemáticos implementan la clase abstracta.       |
| Dependencia (Crea)   | `EcuacionSegundoOrden` ──► `Solucion`                       | La ecuación instancía (crea) las soluciones en el método `resolver()`.|
| Dependencia (Usa)    | `GestorPersistencia` ──► `Solucion`                         | La persistencia recibe una solución y delega la escritura.            |
| Dependencia (Orquesta)| `InterfazUsuario` ──► `EcuacionSegundoOrden`                | La interfaz crea la ecuación basándose en la entrada del usuario.     |

---

## 5. Modelado UML de Clases

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam classFontSize 12
skinparam linetype ortho

abstract class Solucion {
  + mostrar_consola(ecuacion_str: str): void
  + guardar_en_archivo(archivo: File, ecuacion_str: str): void
}

class SolucionRealesDistintas {
  - r1: float
  - r2: float
  + mostrar_consola(ecuacion_str: str): void
  + guardar_en_archivo(archivo: File, ecuacion_str: str): void
}

class SolucionRealesIguales {
  - r: float
  + mostrar_consola(ecuacion_str: str): void
  + guardar_en_archivo(archivo: File, ecuacion_str: str): void
}

class SolucionComplejas {
  - real: float
  - imag: float
  + mostrar_consola(ecuacion_str: str): void
  + guardar_en_archivo(archivo: File, ecuacion_str: str): void
}

class EcuacionSegundoOrden {
  - a: float
  - b: float
  - c: float
  - discriminante: float
  - _calcular_discriminante(): float
  + obtener_representacion(): str
  + resolver(): Solucion
}

class GestorPersistencia {
  - ruta_archivo: str
  + registrar_resolucion(ecuacion: EcuacionSegundoOrden, solucion: Solucion): void
}

class InterfazUsuario {
  + solicitar_coeficiente(nombre: str, descripcion: str): float
  + ejecutar(): void
}

SolucionRealesDistintas -up-|> Solucion
SolucionRealesIguales -up-|> Solucion
SolucionComplejas -up-|> Solucion

EcuacionSegundoOrden ..> Solucion : <<instancia>>
GestorPersistencia ..> Solucion : <<usa>>
InterfazUsuario ..> EcuacionSegundoOrden : <<crea>>
InterfazUsuario ..> GestorPersistencia : <<usa>>
@enduml