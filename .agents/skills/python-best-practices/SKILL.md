---
name: python-best-practices
description: Guía estricta de mejores prácticas y estándares de codificación en Python basados en PEP 8, PEP 20, PEP 257 y tipado moderno. Usa esta skill siempre que vayas a escribir, refactorizar o revisar código Python, para asegurar que cumple con los estándares de calidad, convenciones de nomenclatura, documentación, manejo de errores y tipado requeridos por el proyecto.
---

# Python Best Practices (Mejores Prácticas en Python)

Esta skill define el estándar de codificación obligatorio para cualquier desarrollo en Python dentro de este proyecto. Asegúrate de seguir estas reglas estrictamente al escribir, revisar o refactorizar código.

## 1. Principios Generales (PEP 20 - El Zen de Python)

- Bello es mejor que feo.
- Explícito es mejor que implícito.
- Lo simple es mejor que lo complejo.
- La legibilidad cuenta.

## 2. Estructura y Estilo del Código (PEP 8)

- **Indentación:** Utiliza estrictamente **4 espacios** por cada nivel de anidación lógica. Prohibido mezclar espacios y tabulaciones.
- **Convenciones de Nomenclatura:**
  - `snake_case`: Para variables, funciones y métodos.
  - `PascalCase`: Para nombres de clases.
  - `UPPER_CASE`: Para constantes a nivel de módulo.
- **Modificadores de Acceso:** Usa el guion bajo inicial (`_variable` o `_metodo`) para indicar que una entidad es de uso interno o privado.
- **Espacios en blanco:** Evita espacios innecesarios dentro de paréntesis, corchetes, llaves o antes de una coma.
- **Importaciones:**
  - Al inicio del archivo.
  - En líneas separadas.
  - Agrupadas en tres bloques separados por una línea en blanco:
    1. Bibliotecas estándar.
    2. Dependencias de terceros.
    3. Módulos locales.
  - **PROHIBIDO:** El uso de importaciones comodín (`from modulo import *`).

## 3. Documentación (PEP 257)

Toda función, clase o módulo público DEBE documentarse usando comillas dobles triples (`"""`). Esto es obligatorio incluso si el usuario no lo pide explícitamente.

**Formato Estricto:**
```python
def example_function(param_name: str) -> int:
    """
    Descripción concisa de la función.
    
    Args:
        param_name (str): Descripción del parámetro.

    Returns:
        int: Descripción del valor de retorno.
        
    Raises:
        ValueError: Descripción de cuándo ocurre este error.
    """
    pass
```

## 4. Tipado y Sintaxis Moderna

- **Tipado Estático Moderno (PEP 484, 585 y 604):**
  - Usa Type Hints siempre.
  - Usa los tipos genéricos integrados (ej. `list[str]`, `dict[str, int]`) en lugar del módulo `typing` clásico.
  - Usa el operador `|` para uniones paramétricas (ej. `int | str | None`).
- **Interpolación de Cadenas (PEP 498):**
  - Usa siempre **f-strings** (`f"Texto {variable}"`).
- **Gestores de Contexto (PEP 343):**
  - Usa siempre la declaración `with` para el manejo de recursos (archivos, conexiones, etc.).
- **Operador Morsa (PEP 572):**
  - **PROHIBIDO:** No utilices expresiones de asignación con el operador morsa (`:=`).

## 5. Manejo de Errores y Flujo de Datos

- **Excepciones Quirúrgicas:**
  - Usa bloques `try...except` atrapando excepciones específicas (ej. `except ValueError:`).
  - **PROHIBIDO:** Atrapar errores globales con `except Exception:` sin justificación extrema.
- **Liberación de Recursos:**
  - Utiliza la cláusula `finally` incondicionalmente cuando se requiera liberar recursos del sistema (si no se usa un bloque `with`), garantizando la clausura segura.
