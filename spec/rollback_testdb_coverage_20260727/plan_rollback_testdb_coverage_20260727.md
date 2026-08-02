# 005 · Rollback en Service, Base de Datos de Test y Cobertura

## Contexto

### Situación actual

- **Service sin rollback explícito:** [service.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/users/service.py) ejecuta `await self.session.commit()` directamente sin `try/except`. Si ocurre un error después de operaciones parciales, el rollback depende implícitamente del cierre de sesión en `get_db()`, lo cual es frágil e impredecible.
- **Sin base de datos de test dedicada:** [conftest.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/tests/conftest.py) usa `settings.database_url` (la misma DB de desarrollo `iahelpmath`). Se limpia con `TRUNCATE` antes de la suite, pero existe riesgo de contaminar datos de desarrollo.
- **Sin tests unitarios para la capa Service:** Solo existen tests de integración HTTP (router) y tests unitarios de repositorio. No hay tests que aíslen la lógica de negocio del `UserService` con mocks.
- **Sin configuración de cobertura en `pyproject.toml`:** No hay `[tool.coverage.run]` ni `[tool.coverage.report]` con umbral mínimo.

### Justificación

| Objetivo | Riesgo que mitiga |
|---|---|
| Rollback explícito en Service | Datos inconsistentes si falla una operación post-commit parcial |
| DB de test separada (`TestAIHelpMath`) | Destrucción accidental de datos de desarrollo al ejecutar tests |
| Cobertura completa de tests | Regresiones silenciosas en lógica de negocio no testeada |

### Objetivo

Implementar los tres sub-objetivos del punto 5 del roadmap:

1. Aplicar rollback explícito en `UserService` según la skill `fastapi-app-creator`.
2. Configurar una base de datos PostgreSQL de test separada llamada `TestAIHelpMath`.
3. Analizar y cerrar los gaps de cobertura de tests del proyecto.

### Riesgo

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Rollback modifica el flujo de excepciones existente | Medio — tests de integración podrían fallar si el rollback interfiere con savepoints | Ejecutar toda la suite tras cada cambio; mantener patrón de savepoints en fixtures |
| Script de init de DB no se ejecuta en Docker existente | Bajo — `docker-entrypoint-initdb.d` solo corre en volúmenes nuevos | Documentar que se debe ejecutar `docker compose down -v` antes |
| Umbral de cobertura bloquea CI futuro | Bajo — el umbral es configurable | Configurado en 90%, ajustable si es necesario |

### Enfoque

- **TDD (Red-Green-Refactor):** Escribir tests que validen el comportamiento de rollback *antes* de implementarlo (Fase 1), luego implementar el rollback (Fase 2) para que pasen.
- **Aislamiento de DB:** Crear la DB de test vía script de inicialización de PostgreSQL en Docker (Fase 3).
- **Cierre de gaps:** Agregar tests unitarios faltantes y configurar `coverage` (Fase 4).

---

## Decisiones tomadas

| Decisión | Resolución |
|---|---|
| **Umbral mínimo de cobertura** | `fail_under = 90` en `[tool.coverage.report]` |
| **Tests del Service** | Con **mocks** (`AsyncMock`) en `tests/service/`, aislando la lógica de negocio de la DB |
| **Estrategia de rollback** | `try/except` explícito con `await self.session.rollback()` — compatible con el patrón de `commit()` manual existente y con los savepoints de las fixtures de test |

---

## Fases

---

### Fase 1 — Tests unitarios del Service (TDD — Red)

**Objetivo:** Crear tests unitarios del `UserService` con mocks que verifiquen el comportamiento de `commit`/`rollback`. Estos tests deben **fallar** (red) porque el service actual no implementa rollback.

**Conceptos aplicados:**
- Patrón AAA (Arrange-Act-Assert) — Skill [pytest-best-practices](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/pytest-best-practices/SKILL.md)
- Tests de servicios con `AsyncMock` — Skill [fastapi-app-creator](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/testing.md), sección 5
- TDD Red-Green-Refactor — Skill [tdd](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/tdd/SKILL.md)
- Reglas de transacciones exclusivas del Service — Skill [fastapi-app-creator](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/SKILL.md), sección 1 "Regla fundamental de transacciones"

**Archivos:**

| Archivo | Acción |
|---|---|
| `tests/service/__init__.py` | Crear |
| `tests/service/test_user_service.py` | Crear |

**Tests a implementar:**

- `TestUserServiceCreate`:
  - `test_create_calls_commit_on_success`
  - `test_create_calls_rollback_on_repository_error`
  - `test_create_calls_rollback_on_commit_error`
  - `test_create_raises_conflict_for_duplicate_email`
- `TestUserServiceUpdate`:
  - `test_update_calls_commit_on_success`
  - `test_update_calls_rollback_on_error`
  - `test_update_raises_conflict_for_duplicate_email`
  - `test_update_raises_not_found`
- `TestUserServiceDelete`:
  - `test_delete_calls_commit_on_success`
  - `test_delete_calls_rollback_on_error`
  - `test_delete_raises_not_found`
- `TestUserServiceRead`:
  - `test_get_by_id_returns_user`
  - `test_get_by_id_raises_not_found`
  - `test_get_detailed_returns_user`
  - `test_get_detailed_raises_not_found`
  - `test_get_all_returns_paginated_response`

**Checklist:**

- [x] Crear el directorio `tests/service/`
- [x] Crear archivo vacío `tests/service/__init__.py`
- [x] Crear archivo `tests/service/test_user_service.py` con los imports necesarios: `pytest`, `AsyncMock` de `unittest.mock`, `UserService`, `UserCreate`, `UserUpdate`, `UserResponse`, `ConflictException`, `NotFoundException`, `PaginationParams`, `PaginatedResponse`
- [x] Crear fixture `mock_session` que retorne un `AsyncMock` con métodos `commit`, `rollback` y `refresh` como `AsyncMock()`
- [x] Crear fixture `mock_repository` que retorne un `AsyncMock()` genérico
- [x] **`TestUserServiceCreate`:**
  - [x] `test_create_calls_commit_on_success` — Arrange: `mock_repository.get_by_email.return_value = None`, `mock_repository.add.return_value = User(...)`. Act: `await service.create(user_data)`. Assert: `mock_repository.add.assert_called_once()`, `mock_session.commit.assert_called_once()`, `mock_session.refresh.assert_called_once()`, `mock_session.rollback.assert_not_called()`
  - [x] `test_create_calls_rollback_on_repository_error` — Arrange: `mock_repository.get_by_email.return_value = None`, `mock_repository.add.side_effect = Exception("DB error")`. Act+Assert: `pytest.raises(Exception)`, luego `mock_session.rollback.assert_called_once()`, `mock_session.commit.assert_not_called()`
  - [x] `test_create_calls_rollback_on_commit_error` — Arrange: `mock_repository.get_by_email.return_value = None`, `mock_repository.add.return_value = User(...)`, `mock_session.commit.side_effect = Exception("Commit failed")`. Act+Assert: `pytest.raises(Exception)`, luego `mock_session.rollback.assert_called_once()`
  - [x] `test_create_raises_conflict_for_duplicate_email` — Arrange: `mock_repository.get_by_email.return_value = User(...)`. Act+Assert: `pytest.raises(ConflictException)`. Verificar que `mock_session.commit.assert_not_called()` y `mock_session.rollback.assert_not_called()` (la excepción se lanza antes del try)
- [x] **`TestUserServiceUpdate`:**
  - [x] `test_update_calls_commit_on_success` — Arrange: `mock_repository.get_by_id.return_value = User(...)`, `mock_repository.get_by_email.return_value = None`, `mock_repository.update.return_value = User(...)`. Assert: `mock_session.commit.assert_called_once()`, `mock_session.refresh.assert_called_once()`
  - [x] `test_update_calls_rollback_on_error` — Arrange: `mock_repository.get_by_id.return_value = User(...)`, `mock_repository.update.side_effect = Exception("DB error")`. Act+Assert: `pytest.raises(Exception)`, `mock_session.rollback.assert_called_once()`
  - [x] `test_update_raises_conflict_for_duplicate_email` — Arrange: usuario existente con email diferente, `mock_repository.get_by_email.return_value = User(otro)`. Assert: `pytest.raises(ConflictException)`
  - [x] `test_update_raises_not_found` — Arrange: `mock_repository.get_by_id.return_value = None`. Assert: `pytest.raises(NotFoundException)`
- [x] **`TestUserServiceDelete`:**
  - [x] `test_delete_calls_commit_on_success` — Arrange: `mock_repository.get_by_id.return_value = User(...)`. Assert: `mock_repository.delete.assert_called_once()`, `mock_session.commit.assert_called_once()`
  - [x] `test_delete_calls_rollback_on_error` — Arrange: `mock_repository.get_by_id.return_value = User(...)`, `mock_repository.delete.side_effect = Exception("DB error")`. Assert: `mock_session.rollback.assert_called_once()`
  - [x] `test_delete_raises_not_found` — Arrange: `mock_repository.get_by_id.return_value = None`. Assert: `pytest.raises(NotFoundException)`
- [x] **`TestUserServiceRead`:**
  - [x] `test_get_by_id_returns_user` — Arrange: `mock_repository.get_by_id.return_value = User(...)`. Assert: resultado no es `None`, tiene el `id` esperado
  - [x] `test_get_by_id_raises_not_found` — Arrange: `mock_repository.get_by_id.return_value = None`. Assert: `pytest.raises(NotFoundException)`
  - [x] `test_get_detailed_returns_user` — Arrange: `mock_repository.get_detailed.return_value = User(...)`. Assert: resultado no es `None`
  - [x] `test_get_detailed_raises_not_found` — Arrange: `mock_repository.get_detailed.return_value = None`. Assert: `pytest.raises(NotFoundException)`
  - [x] `test_get_all_returns_paginated_response` — Arrange: `mock_repository.get_all.return_value = [User(...)]`, `mock_repository.count.return_value = 1`. Assert: resultado es `PaginatedResponse`, `len(result.items) == 1`, `result.total == 1`
- [x] Ejecutar `uv run pytest tests/service/ -v` y verificar:
  - [x] Los tests de rollback (`*_rollback_*`) fallan (red) porque el service no tiene `try/except`
  - [x] Los tests de lectura (`TestUserServiceRead`) pasan (ya implementados)
  - [x] Los tests de excepciones de negocio (`*_conflict_*`, `*_not_found`) pasan

---

### Fase 2 — Rollback explícito en `UserService` y Excepción RFC 9457 (TDD — Green)

**Objetivo:** Implementar `try/except` con `rollback()` explícito en los métodos de escritura del `UserService` y envolver cualquier error de base de datos capturado en una excepción personalizada que cumpla con el estándar RFC 9457 (`DatabaseException` en `src/core/exceptions.py`).

**Conceptos aplicados:**
- Regla fundamental de transacciones: commit/rollback exclusivo del Service — Skill [fastapi-app-creator](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/SKILL.md), sección 1
- Límites transaccionales y antipatrón autocommit — Skill [fastapi-app-creator](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/database.md), sección 3
- Manejo centralizado de excepciones RFC 9457 — [AGENTS.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/AGENTS.md) y `src/core/exceptions.py`
- Arquitectura Router → Service → Repository — [README.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/README.md), sección "Patrones de Diseño"
- TDD Green — Skill [tdd](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/tdd/SKILL.md)

**Archivos:**

| Archivo | Acción |
|---|---|
| `src/core/exceptions.py` | Modificar |
| `src/users/users/service.py` | Modificar |
| `tests/service/test_user_service.py` | Modificar |

**Patrón a implementar:**

```python
# 1. Definición en src/core/exceptions.py
class DatabaseException(AppException):
    """Excepción lanzada cuando ocurre un error durante una operación de base de datos.

    Args:
        detail (str): Mensaje descriptivo del error de base de datos.
    """

    def __init__(self, detail: str = "Database operation failed") -> None:
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 2. Uso en src/users/users/service.py
async def create(self, user_data: UserCreate) -> User:
    # Validaciones de negocio ANTES del try (no disparan rollback)
    existing_user = await self.repository.get_by_email(user_data.email)
    if existing_user is not None:
        raise ConflictException(...)

    # Operaciones de escritura DENTRO del try
    try:
        user = await self.repository.add(user_data)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    except Exception as err:
        await self.session.rollback()
        raise DatabaseException(
            detail=f"Database operation failed: {err}"
        ) from err
```

**Checklist:**

- [x] **Modificar `UserService.create()`:**
  - [x] Mover la validación de email duplicado (`get_by_email` + `ConflictException`) **antes** del bloque `try` para que no dispare rollback
  - [x] Envolver `repository.add()`, `session.commit()` y `session.refresh()` dentro de `try`
  - [x] Agregar bloque `except Exception:` que ejecute `await self.session.rollback()`
  - [x] Verificar que el `return user` está **dentro** del `try` (después del `refresh`)
- [x] **Modificar `UserService.update()`:**
  - [x] Mover `self.get_by_id()` (que lanza `NotFoundException`) **antes** del bloque `try`
  - [x] Mover la validación de email duplicado (`get_by_email` + `ConflictException`) **antes** del bloque `try`
  - [x] Envolver `repository.update()`, `session.commit()` y `session.refresh()` dentro de `try`
  - [x] Agregar bloque `except Exception:` con `await self.session.rollback()`
- [x] **Modificar `UserService.delete()`:**
  - [x] Mover `self.get_by_id()` (que lanza `NotFoundException`) **antes** del bloque `try`
  - [x] Envolver `repository.delete()` y `session.commit()` dentro de `try`
  - [x] Agregar bloque `except Exception:` con `await self.session.rollback()`
- [x] **Crear excepción RFC 9457 para errores de DB:**
  - [x] Crear la clase `DatabaseException(AppException)` en `src/core/exceptions.py` asignando `status.HTTP_500_INTERNAL_SERVER_ERROR`.
  - [x] Reemplazar la elevación directa de `Exception` por `raise DatabaseException(...) from err` tras el `rollback()` en `create()`, `update()` y `delete()` de `UserService`.
  - [x] Actualizar la suite de pruebas en `tests/service/test_user_service.py` para validar `pytest.raises(DatabaseException)` en lugar de `pytest.raises(Exception)`.
- [x] Verificar que **ninguna** excepción de negocio (`ConflictException`, `NotFoundException`) queda dentro de un bloque `try` — deben lanzarse antes
- [x] Verificar que todos los métodos de solo lectura (`get_by_id`, `get_detailed`, `get_all`) **no** tienen `try/except` ni rollback (no modifican datos)
- [x] Ejecutar `uv run pytest tests/service/ -v` — todos los tests del service pasan con `DatabaseException` (green)
- [x] Ejecutar `uv run pytest -v` completo — 0 fallos, sin regresiones

---

### Fase 3 — Base de datos de test `TestAIHelpMath`

**Objetivo:** Configurar una base de datos PostgreSQL separada exclusiva para tests, aislando completamente los datos de desarrollo.

**Conceptos aplicados:**
- `TEST_DATABASE_URL` separado — Skill [fastapi-app-creator](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/testing.md), sección 2 "Fixtures globales"
- Fixture `setup_database` con `create_all`/`drop_all` — Skill [fastapi-app-creator](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/testing.md), sección 2
- Script de inicialización Docker — `docker-entrypoint-initdb.d` (documentación oficial PostgreSQL Docker)
- Configuración con `pydantic-settings` — [AGENTS.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/AGENTS.md), sección "Stack Tecnológico"

**Archivos:**

| Archivo | Acción |
|---|---|
| `scripts/init-test-db.sh` | Crear |
| `docker-compose.yml` | Modificar |
| `.env.example` | Modificar |
| `.env` | Modificar |
| `src/core/config.py` | Modificar |
| `tests/conftest.py` | Modificar |

**Detalle de cambios:**

1. **`scripts/init-test-db.sh`** — Script que crea la DB `TestAIHelpMath` al inicializar el contenedor PostgreSQL:
   ```bash
   #!/bin/bash
   set -e
   psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
       CREATE DATABASE "TestAIHelpMath";
       GRANT ALL PRIVILEGES ON DATABASE "TestAIHelpMath" TO "$POSTGRES_USER";
   EOSQL
   ```

2. **`docker-compose.yml`** — Montar el script en el servicio `db`:
   ```yaml
   volumes:
     - postgres_data:/var/lib/postgresql/data
     - ./scripts/init-test-db.sh:/docker-entrypoint-initdb.d/init-test-db.sh
   ```

3. **`.env.example` y `.env`** — Agregar:
   ```
   TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/TestAIHelpMath
   ```

4. **`src/core/config.py`** — Agregar campo en `Settings`:
   ```python
   test_database_url: str = "postgresql+asyncpg://user:password@localhost:5432/TestAIHelpMath"
   ```

5. **`tests/conftest.py`** — Cambios:
   - Usar `settings.test_database_url` en lugar de `settings.database_url`
   - Reemplazar `clean_database_before_suite` (TRUNCATE) por `setup_database` (`create_all`/`drop_all`)
   - Mantener el patrón de savepoints en `db_session`

**Checklist:**

- [x] **Script de inicialización Docker:**
  - [x] Crear directorio `scripts/` en la raíz del proyecto
  - [x] Crear archivo `scripts/init-test-db.sh` con el contenido del script SQL (`CREATE DATABASE "TestAIHelpMath"`)
  - [x] Asegurar que el archivo tiene line endings Unix (LF, no CRLF) para compatibilidad con el contenedor Linux
  - [x] Asegurar que el script tiene permisos de ejecución (se verificará dentro del contenedor)
- [x] **Docker Compose:**
  - [x] Agregar línea `- ./scripts/init-test-db.sh:/docker-entrypoint-initdb.d/init-test-db.sh` en la sección `volumes` del servicio `db` en `docker-compose.yml`
  - [x] No modificar ninguna otra configuración del servicio `db`
- [x] **Variables de entorno:**
  - [x] Agregar la línea `TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/TestAIHelpMath` al final de `.env.example`
  - [x] Agregar la misma línea `TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/TestAIHelpMath` al archivo `.env` local
- [x] **Configuración de la aplicación:**
  - [x] Agregar campo `test_database_url: str` en la clase `Settings` de `src/core/config.py` con valor por defecto `"postgresql+asyncpg://user:password@localhost:5432/TestAIHelpMath"`
  - [x] Verificar que el campo se carga correctamente desde `.env` con `pydantic-settings`
- [x] **Actualización de `tests/conftest.py`:**
  - [x] Cambiar la línea `db_url = settings.database_url` por `db_url = settings.test_database_url`
  - [x] Eliminar la lógica de reemplazo de esquema (`postgres://` → `postgresql+asyncpg://`) ya que `test_database_url` ya incluye el driver correcto
  - [x] Eliminar la fixture `clean_database_before_suite` completa (ya no se usa TRUNCATE)
  - [x] Crear nueva fixture `setup_database` con `scope="session"` y `autouse=True` que use `Base.metadata.create_all` en el setup y `Base.metadata.drop_all` + `engine_test.dispose()` en el teardown (vía `yield`)
  - [x] Importar `Base` o el equivalente de SQLModel para `create_all`/`drop_all` — verificar si el proyecto usa `SQLModel.metadata` directamente
  - [x] Agregar `setup_database` como dependencia de la fixture `db_session` para garantizar que las tablas existen antes de cada test
  - [x] Mantener intacto el patrón de savepoints (`begin_nested` + evento `after_transaction_end`) en `db_session`
  - [x] Mantener intacta la fixture `async_client` sin cambios
  - [x] Mantener intacta la fixture `event_loop` sin cambios
- [x] **Verificación Docker:**
  - [x] Script de inicialización montado en `docker-compose.yml` (`init-test-db.sh`)
  - [x] Base de datos de pruebas `TestAIHelpMath` disponible y verificada en el entorno PostgreSQL local
- [x] **Verificación de tests:**
  - [x] Ejecutar `uv run pytest -v` — todos los 40 tests pasan contra `TestAIHelpMath`
  - [x] Verificar en los logs de pytest (`echo=True` en `engine_test`) que las queries van a `TestAIHelpMath`
  - [x] Confirmar que la DB de desarrollo no tiene tablas truncadas ni datos alterados

---

### Fase 4 — Análisis y cierre de gaps de cobertura

**Objetivo:** Configurar `pytest-cov` con umbral mínimo y crear los tests faltantes para alcanzar la cobertura objetivo.

**Conceptos aplicados:**
- Configuración de `coverage` en `pyproject.toml` — Skill [pytest-best-practices](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/pytest-best-practices/SKILL.md)
- Patrón AAA — Skill [pytest-best-practices](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/pytest-best-practices/SKILL.md)
- Validación de Pydantic con `pytest.raises` — Skill [pytest-best-practices](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/pytest-best-practices/SKILL.md)
- Pruebas parametrizadas — Skill [fastapi-app-creator](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/testing.md), sección 7

**Análisis de gaps:**

| Módulo | Estado actual | Gap identificado |
|---|---|---|
| `src/users/users/service.py` | Cubierto indirectamente vía router tests | Sin tests unitarios aislados (resuelto en Fase 1) |
| `src/users/users/repository.py` | ✅ Cubierto | Método `count()` sin test directo |
| `src/users/users/router.py` | ✅ Cubierto | Completo |
| `src/core/exceptions.py` | Parcialmente cubierto | `ValidationException` y `AppException` base sin tests |
| `src/shared/pagination.py` | Cubierto implícitamente | Sin tests de validación de bordes |
| `src/main.py` | Parcialmente cubierto | Endpoint `/health` sin test |

**Archivos:**

| Archivo | Acción |
|---|---|
| `pyproject.toml` | Modificar |
| `tests/crud/test_user_repository.py` | Modificar |
| `tests/api/test_health.py` | Crear |
| `tests/unit/__init__.py` | Crear |
| `tests/unit/test_pagination.py` | Crear |
| `tests/unit/test_exceptions.py` | Crear |

**Detalle de cambios:**

1. **`pyproject.toml`** — Agregar:
   ```toml
   [tool.coverage.run]
   source = ["src"]
   omit = [
       "src/core/config.py",
       "src/core/security.py",
       "src/__init__.py",
       "*/__init__.py",
   ]

   [tool.coverage.report]
   fail_under = 90
   show_missing = true
   exclude_lines = [
       "pragma: no cover",
       "if __name__ == .__main__.",
       "if TYPE_CHECKING:",
   ]
   ```

2. **`tests/crud/test_user_repository.py`** — Agregar:
   - `test_count_returns_zero_when_empty`
   - `test_count_returns_correct_number`

3. **`tests/api/test_health.py`** — Crear:
   - `test_health_check_returns_200`

4. **`tests/unit/test_pagination.py`** — Crear:
   - `test_default_values`
   - `test_offset_negative_raises_validation_error`
   - `test_limit_zero_raises_validation_error`
   - `test_limit_exceeds_max_raises_validation_error`
   - `test_valid_custom_values`

5. **`tests/unit/test_exceptions.py`** — Crear:
   - `test_app_exception_default_status_code`
   - `test_not_found_exception_status_code`
   - `test_conflict_exception_status_code`
   - `test_validation_exception_status_code`
   - `test_exception_handler_returns_rfc9457_format`

**Checklist:**

- [ ] **Configuración de cobertura en `pyproject.toml`:**
  - [ ] Agregar sección `[tool.coverage.run]` con `source = ["src"]` y `omit` para archivos no testeables (`config.py`, `security.py`, `__init__.py`)
  - [ ] Agregar sección `[tool.coverage.report]` con `fail_under = 90`, `show_missing = true` y `exclude_lines` para pragmas y `TYPE_CHECKING`
- [ ] **Tests de `count()` en `tests/crud/test_user_repository.py`:**
  - [ ] `test_count_returns_zero_when_empty` — Arrange: no insertar usuarios. Act: `count = await repo.count()`. Assert: `count == 0`
  - [ ] `test_count_returns_correct_number` — Arrange: insertar 3 usuarios con `db_session.add()` + `flush()`. Act: `count = await repo.count()`. Assert: `count == 3`
- [ ] **Test de health check en `tests/api/test_health.py`:**
  - [ ] Crear archivo con imports de `AsyncClient`
  - [ ] `test_health_check_returns_200` — Act: `response = await async_client.get("/health")`. Assert: `status_code == 200`, `response.json() == {"status": "healthy"}`
- [ ] **Tests de paginación en `tests/unit/test_pagination.py`:**
  - [ ] Crear directorio `tests/unit/` y archivo `__init__.py`
  - [ ] Crear `test_pagination.py` con imports de `PaginationParams` y `pytest`
  - [ ] `test_default_values` — Act: `params = PaginationParams()`. Assert: `params.offset == 0`, `params.limit == 10`
  - [ ] `test_offset_negative_raises_validation_error` — Act+Assert: `pytest.raises(ValidationError)` al crear `PaginationParams(offset=-1)`
  - [ ] `test_limit_zero_raises_validation_error` — Act+Assert: `pytest.raises(ValidationError)` al crear `PaginationParams(limit=0)`
  - [ ] `test_limit_exceeds_max_raises_validation_error` — Act+Assert: `pytest.raises(ValidationError)` al crear `PaginationParams(limit=101)`
  - [ ] `test_valid_custom_values` — Act: `params = PaginationParams(offset=20, limit=50)`. Assert: `params.offset == 20`, `params.limit == 50`
- [ ] **Tests de excepciones en `tests/unit/test_exceptions.py`:**
  - [ ] Crear `test_exceptions.py` con imports de `AppException`, `NotFoundException`, `ConflictException`, `ValidationException`, `status`
  - [ ] `test_app_exception_default_status_code` — Act: `exc = AppException(detail="test")`. Assert: `exc.status_code == 400`, `exc.detail == "test"`
  - [ ] `test_not_found_exception_status_code` — Act: `exc = NotFoundException()`. Assert: `exc.status_code == 404`, `exc.detail == "Resource not found"`
  - [ ] `test_conflict_exception_status_code` — Act: `exc = ConflictException()`. Assert: `exc.status_code == 409`, `exc.detail == "Request conflict"`
  - [ ] `test_validation_exception_status_code` — Act: `exc = ValidationException()`. Assert: `exc.status_code == 422`, `exc.detail == "Data validation error"`
  - [ ] `test_exception_handler_returns_rfc9457_format` — Arrange: crear una request mock y una `AppException`. Act: invocar `app_exception_handler(request, exc)` o usar `async_client` con una ruta que lance la excepción. Assert: la respuesta JSON contiene las 5 claves RFC 9457 (`type`, `title`, `status`, `detail`, `instance`)
- [ ] **Verificación de cobertura:**
  - [ ] Ejecutar `uv run pytest --cov=src --cov-report=term-missing`
  - [ ] Verificar que la cobertura total es ≥ 90%
  - [ ] Revisar el reporte `term-missing` para identificar líneas no cubiertas
  - [ ] Si la cobertura es < 90%, agregar tests adicionales para las líneas faltantes reportadas

---

### Fase 5 — Validación integral (QA)

**Objetivo:** Verificar que todos los cambios funcionan correctamente en conjunto, sin regresiones, y que el código cumple con los estándares de calidad del proyecto.

**Conceptos aplicados:**
- Comandos de calidad de código — [AGENTS.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/AGENTS.md), sección "Testing y Pruebas"
- Estándares de código — Skill [python-best-practices](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/python-best-practices/SKILL.md)

**Checklist:**

- [ ] **Suite de tests completa:**
  - [ ] Ejecutar `uv run pytest -v` — resultado esperado: todos los tests pasan (0 fallos)
  - [ ] Contar el número total de tests ejecutados y registrar aquí: `___` tests
  - [ ] Verificar que no hay warnings de deprecación relevantes en la salida
- [ ] **Cobertura de código:**
  - [ ] Ejecutar `uv run pytest --cov=src --cov-report=term-missing`
  - [ ] Verificar que la cobertura total es ≥ 90% — registrar aquí: `___`%
  - [ ] Verificar que `fail_under = 90` no produce error (el comando termina con exit code 0)
  - [ ] Revisar que no hay módulos de `src/` con cobertura < 70% individual
- [ ] **Linter y formato:**
  - [ ] Ejecutar `uv run ruff check src/ tests/` — resultado esperado: 0 errores
  - [ ] Ejecutar `uv run ruff format --check src/ tests/` — resultado esperado: todos los archivos ya formateados
  - [ ] Si hay errores de formato, ejecutar `uv run ruff format src/ tests/` para corregirlos
- [ ] **Análisis estático de tipos:**
  - [ ] Ejecutar `uv run mypy src/` — resultado esperado: "Success: no issues found"
  - [ ] Si hay errores de tipo relacionados con los cambios de rollback, corregirlos
- [ ] **Aislamiento de base de datos:**
  - [ ] Verificar que la DB de desarrollo `iahelpmath` no fue afectada: conectar con `docker exec -it iahelpmath_db psql -U user -d iahelpmath -c "SELECT count(*) FROM user_role;"` — los datos de desarrollo deben estar intactos
  - [ ] Verificar que `docker compose up db -d` crea ambas bases: `docker exec -it iahelpmath_db psql -U user -l` — debe listar `iahelpmath` y `TestAIHelpMath`
- [ ] **Aplicación funcional:**
  - [ ] Ejecutar `uv run uvicorn src.main:app --reload` — el servidor arranca sin errores
  - [ ] Verificar que `GET /health` responde `200 OK` con `{"status": "healthy"}`
  - [ ] Verificar que `GET /docs` carga la documentación Swagger correctamente
- [ ] **Documentación:**
  - [ ] Actualizar `spec/roadmap.md` — mover el punto 5 de "Siguiente" a "Hecho" con la fecha de finalización
  - [ ] Verificar que el enlace al plan en el roadmap funciona correctamente

---

## Criterios de Aceptación

1. `UserService.create()`, `update()` y `delete()` ejecutan `await self.session.rollback()` explícito ante cualquier excepción durante las operaciones de escritura.
2. Los tests usan una base de datos PostgreSQL separada llamada `TestAIHelpMath`, completamente aislada de la de desarrollo.
3. La cobertura de código alcanza al menos 90% según `pytest-cov`.
4. Existen tests unitarios del `UserService` con mocks (`AsyncMock`) que verifican el comportamiento de `commit`/`rollback`.
5. Todos los tests existentes siguen pasando sin regresiones.
6. El código pasa `ruff check`, `ruff format` y `mypy` sin errores.

---

## Referencias Técnicas

| Archivo | Propósito |
|---|---|
| [SKILL.md (fastapi-app-creator)](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/SKILL.md) | Patrón de transacciones y arquitectura por capas |
| [database.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/database.md) | Límites transaccionales y antipatrón autocommit |
| [testing.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/testing.md) | Fixtures, rollback transaccional, tests de servicios |
| [SKILL.md (pytest-best-practices)](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/pytest-best-practices/SKILL.md) | Patrón AAA, parametrización, cobertura |
| [SKILL.md (tdd)](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/tdd/SKILL.md) | Ciclo Red-Green-Refactor |
| [SKILL.md (python-best-practices)](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/python-best-practices/SKILL.md) | Estándares de código Python |
| [AGENTS.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/AGENTS.md) | Reglas del proyecto, comandos y convenciones |
| [README.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/README.md) | Arquitectura y patrones de diseño del proyecto |

---

## Resumen de Archivos

| Archivo | Acción |
|---|---|
| `tests/service/__init__.py` | Crear |
| `tests/service/test_user_service.py` | Crear |
| `tests/unit/__init__.py` | Crear |
| `tests/unit/test_pagination.py` | Crear |
| `tests/unit/test_exceptions.py` | Crear |
| `tests/api/test_health.py` | Crear |
| `scripts/init-test-db.sh` | Crear |
| `src/users/users/service.py` | Modificar |
| `src/core/config.py` | Modificar |
| `tests/conftest.py` | Modificar |
| `tests/crud/test_user_repository.py` | Modificar |
| `docker-compose.yml` | Modificar |
| `.env.example` | Modificar |
| `pyproject.toml` | Modificar |
| `spec/roadmap.md` | Modificar |
| `src/users/users/repository.py` | Revisar |
| `src/users/users/router.py` | Revisar |
| `src/core/exceptions.py` | Modificar |
| `src/core/dependencies.py` | Revisar |
| `src/shared/pagination.py` | Revisar |
| `src/main.py` | Revisar |
