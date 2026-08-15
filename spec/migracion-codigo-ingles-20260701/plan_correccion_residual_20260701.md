# Plan de Corrección: Código Funcional Residual en Español

## Contexto

Tras completar las Fases 1-4 del plan de migración de código a inglés y ejecutar la Fase 5 de validación, se identificaron **discrepancias residuales** que impiden cumplir los criterios de aceptación. Este plan documenta los hallazgos y las correcciones pendientes.

## Resultados de Validación (Fase 5)

### `ruff format` ✅ (con observaciones)
- 2 archivos reformateados, 21 sin cambios.

### `ruff check` ❌
- **1 error** en `src/users/schemas.py:248` — Línea demasiado larga (89 > 88) en un docstring del esquema `UserDetailed`.

### `mypy` ❌
- **17 errores** en `src/users/__init__.py` — Importa y exporta los nombres **antiguos** en español (`UserNivel`, `UserRol`, `UserTemaInteres`, `UserPerfilIA`, `UserRolCreate`, `UserNivelCreate`, etc.) que ya no existen en los módulos refactorizados.

### Migración de Alembic ⏳
- Pendiente. No se puede generar la migración hasta que `mypy` y `ruff` estén libres de errores.

### `pytest` ⏳
- Pendiente. Requiere que la migración esté aplicada.

---

## Código Funcional en Español Detectado

### 1. Archivo omitido: `src/users/__init__.py`

| Línea | Problema |
|-------|----------|
| 3-9 | Importa modelos con nombres antiguos en español: `UserNivel`, `UserPerfilIA`, `UserRol`, `UserTemaInteres` |
| 10-28 | Importa esquemas con nombres antiguos en español: `UserNivelCreate`, `UserNivelResponse`, `UserNivelUpdate`, `UserPerfilIACreate`, `UserPerfilIADetailed`, `UserPerfilIAResponse`, `UserPerfilIAUpdate`, `UserRolCreate`, `UserRolResponse`, `UserRolUpdate`, `UserTemaInteresCreate`, `UserTemaInteresResponse`, `UserTemaInteresUpdate` |
| 30-55 | `__all__` exporta todos los nombres anteriores en español |

**Corrección:** Actualizar todas las importaciones y el `__all__` a los nombres en inglés (`UserLevel`, `UserRole`, `UserTopic`, `UserAIProfile`, `UserRoleCreate`, `UserLevelCreate`, etc.).

---

### 2. Strings funcionales en español: `src/users/schemas.py`

Los valores del parámetro `description=` dentro de `Field(...)` son **strings funcionales** que se renderizan en la documentación OpenAPI (Swagger/ReDoc). No son docstrings ni comentarios.

| Línea | String actual | Corrección propuesta |
|-------|--------------|---------------------|
| 22 | `"Nombre del rol"` | `"Role name"` |
| 23 | `"Descripción del rol"` | `"Role description"` |
| 63 | `"Nombre del nivel de conocimiento"` | `"Knowledge level name"` |
| 64 | `"Valor numérico de lógica"` | `"Numeric quantifier value"` |
| 106 | `"Nombre del tema favorito"` | `"Topic name"` |
| 148 | `"Identificador del usuario"` | `"User identifier"` |
| 149 | `"Identificador del nivel asociado"` | `"Associated level identifier"` |
| 150 | `"Identificador del tema asociado"` | `"Associated topic identifier"` |
| 208 | `"Identificador del rol principal"` | `"Primary role identifier"` |
| 209 | `"Nombres del usuario"` | `"User first name"` |
| 210 | `"Apellidos del usuario"` | `"User last name"` |
| 211 | `"Correo electrónico válido"` | `"Valid email address"` |

---

### 3. Strings funcionales en español: `src/users/users/router.py`

Los valores del parámetro `summary=` en los decoradores de ruta son **strings funcionales** que se renderizan en la documentación OpenAPI. No son docstrings.

| Línea | String actual | Corrección propuesta |
|-------|--------------|---------------------|
| 17 | `"Crear un nuevo usuario"` | `"Create a new user"` |
| 40 | `"Obtener lista de usuarios"` | `"Get users list"` |
| 65 | `"Obtener usuario por ID"` | `"Get user by ID"` |
| 93 | `"Actualizar usuario"` | `"Update user"` |
| 122 | `"Eliminar usuario"` | `"Delete user"` |

---

### 4. Mensajes de error en español: `src/users/users/router.py`

Los strings pasados a `NotFoundException(...)` son mensajes de error devueltos al cliente en el cuerpo JSON de la respuesta HTTP. Son **código funcional**.

| Línea | String actual | Corrección propuesta |
|-------|--------------|---------------------|
| 85 | `f"Usuario con ID {user_id} no encontrado"` | `f"User with ID {user_id} not found"` |
| 115 | `f"Usuario con ID {user_id} no encontrado"` | `f"User with ID {user_id} not found"` |
| 142 | `f"Usuario con ID {user_id} no encontrado"` | `f"User with ID {user_id} not found"` |

---

### 5. Mensajes de error por defecto en español: `src/core/exceptions.py`

Los valores por defecto de `detail=` en las excepciones son mensajes de error devueltos al cliente. Son **código funcional**.

| Línea | String actual | Corrección propuesta |
|-------|--------------|---------------------|
| 32 | `"Recurso no encontrado"` | `"Resource not found"` |
| 43 | `"Conflicto en la solicitud"` | `"Request conflict"` |
| 54 | `"Error de validación de datos"` | `"Data validation error"` |

---

### 6. Error de linting: `src/users/schemas.py`

| Línea | Problema | Corrección propuesta |
|-------|----------|---------------------|
| 248 | `E501` Línea demasiado larga (89 > 88) en docstring | Dividir la línea del docstring en dos |

---

## Checklist de Tareas

- [x] Actualizar importaciones y `__all__` en `src/users/__init__.py` a los nuevos nombres en inglés.
- [x] Traducir los `description=` de `Field(...)` en `src/users/schemas.py` al inglés.
- [x] Corregir la línea demasiado larga (E501) en `src/users/schemas.py:248`.
- [x] Traducir los `summary=` de los decoradores de ruta en `src/users/users/router.py` al inglés.
- [x] Traducir los mensajes de `NotFoundException(...)` en `src/users/users/router.py` al inglés.
- [x] Traducir los mensajes por defecto de las excepciones en `src/core/exceptions.py` al inglés.
- [x] Crear el archivo de migración manual de Alembic (`migrations/versions/e427b0c9fd1a_translate_to_english.py`) para renombrar las tablas y columnas en la base de datos preservando los datos.
- [x] Ejecutar linting y formatting final: `uv run ruff check src/ tests/` — All checks passed. `uv run ruff format src/ tests/` — 23 files left unchanged.
- [x] Ejecutar comprobación estática de tipos: `uv run mypy src/` — Success: no issues found in 19 source files.
- [x] Aplicar la migración: `uv run alembic upgrade head` — Migración `e427b0c9fd1a` aplicada exitosamente.
- [x] Ejecutar los tests: `uv run pytest -v` — 0 tests recolectados (no hay tests escritos aún). Sin fallos.

## Resumen de Archivos

| Archivo | Acción |
|---------|--------|
| `src/users/__init__.py` | Modificar |
| `src/users/schemas.py` | Modificar |
| `src/users/users/router.py` | Modificar |
| `src/core/exceptions.py` | Modificar |
