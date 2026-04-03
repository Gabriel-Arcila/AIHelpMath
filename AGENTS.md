# AGENTS.md

Estas son las intrucciones para el agente de IA.

## Intruccion de comportamiento

- Habla siempre en español.
- Utiliza PEP 8 como guia estricta para codificar:
  - Indentation: 4 espacios.
  - Longitud de línea: 79 caracteres.
  - Nombres:
    - snake_case para variables y funciones.
    - PascalCase para clases.
    - UPPER_CASE para constantes.
  - Espacios en blanco: Evita espacios innecesarios dentro de paréntesis o antes de una coma.
- Utiliza PEP 20:
  - Bello es mejor que feo.
  - Explícito es mejor que implícito.
  - Lo simple es mejor que lo complejo.
  - La legibilidad cuenta.
- Utiliza PEP 257 como guia estricta para documentar el codigo y realiza esta accion aunque no se te pida:
  - Ejemplo:

            """
            <descripcion de la funcion>
            
            Args:
                <nombre_variable> (<tipo>): <descripcion>

            Returns:
                <tipo>: <descripcion>
            """
- Utiliza PEP 484, PEP 585 y PEP 604 para anotar las funciones y variables.
- Utiliza PEP 498 para la interpolación literal de cadenas (f-strings).
- Utiliza PEP 343 para la declaración "with" (gestores de contexto).    
- No utilizar PEP 572 para las expresiones de asignación (El operador morsa :=).
- Utiliza las reglas de API REST para el proyecto:
  - Usa sustantivos en plural, nunca verbos, para las URIs.
  - Aplica correctamente los verbos HTTP.
    - GET: Obtener recursos.
    - POST: Crear recursos.
    - PUT: Actualizar recursos.
    - DELETE: Eliminar recursos.
    - PATCH: Actualizar recursos parcialmente.
  - Utiliza los códigos de estado HTTP adecuados:
    - 200 OK: Solicitud exitosa.
    - 201 Created: Recurso creado exitosamente.
    - 204 No Content: Solicitud exitosa pero sin contenido.
    - 400 Bad Request: Solicitud inválida.
    - 401 Unauthorized: Solicitud no autorizada.
    - 403 Forbidden: Solicitud prohibida.
    - 404 Not Found: Recurso no encontrado.
    - 405 Method Not Allowed: Método no permitido.
    - 409 Conflict: Conflicto con el recurso.
    - 500 Internal Server Error: Error interno del servidor.
    - etc...
  - Versiona tu API desde el día uno.
  - Usa Paginación, Filtrado y Ordenamiento.
  - Mantén la anidación a un máximo de un nivel.
- Realiza pruebas unitarias en la carpeta "tests"con pytest:
  - Convenciones de Nomenclatura Obligatorias:
    - Archivos: Deben comenzar por "test_".
    - Funciones y Métodos: Deben comenzar siempre con el prefijo "test_".
    - Clases: Deben comenzar siempre con el prefijo "Test".
  - El Patrón AAA:
    - Arrange: Configura el estado inicial, inicializa variables o crea los objetos necesarios.
    - Act: Ejecución de la función o método a probar.
    - Assert: Verificación de que el resultado es el esperado.
  - Usa Fixtures en lugar de setup/teardown.
  - Parametrización (Evita repetir código) (Utiliza @pytest.mark.parametrize).
  - Prueba las Excepciones Explícitamente (Utiliza pytest.raises).
  - deben tener dependencia absoluta.
- Reglas de FastAPI:
  - Estructura de Proyecto Modular (Usa APIRouter).
  - Separa los Esquemas (Pydantic) de los Modelos (Base de Datos).
  - Usa response_model por Seguridad.
  - Domina la Inyección de Dependencias (Depends).
  - Asincronía Consciente:
    - Usa async def solo si estás utilizando librerías asíncronas dentro de tu función.
    - Usa def normal si estás usando librerías bloqueantes o síncronas.
  - Utiliza los manejadores de excepciones globales de FastAPI (@app.exception_handler).
  - Usa pydantic-settings: Crea una clase Settings que herede de BaseSettings.
  - Tareas en Segundo Plano (Background Tasks) si es necesario.
  - Tipado Estricto de Errores con RFC 7807 (Problem Details).