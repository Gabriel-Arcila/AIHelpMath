# 006 · Refactorización de Tests

## Contexto

### Situación actual

La suite de tests está organizada por tipo de capa (`api/`, `crud/`, `service/`, `unit/`) en vez de replicar la estructura de `src/` por dominio funcional. Los datos de prueba se construyen manualmente con literales duplicados y hay fixtures repetidas entre archivos conftest.

### Justificación

El roadmap (punto 6, "Siguiente" §1) establece tres requisitos:

1. Tests organizados por función (dominio), no por tipo de archivo (capa)
2. Separación de clases por tipo de transacción: `Insert`, `Select`, `Update`, `Delete`
3. Implementar Polyfactory para generación automática de datos de prueba

### Problemas identificados

| Problema | Dónde ocurre | Impacto |
|---|---|---|
| Estructura por capa, no por dominio | `tests/api/`, `tests/crud/`, `tests/service/`, `tests/unit/` | Dificulta localizar tests de un módulo específico |
| Clase única sin separación CRUD | `TestUserRouter` (1 clase, 14 tests), `TestUserRepository` (1 clase, 13 tests) | Tests difíciles de navegar y filtrar |
| Datos manuales hardcodeados | Todos los archivos de test | Duplicación, fragilidad ante cambios en schemas |
| Fixture `seed_user_role` duplicada | `tests/api/conftest.py` y `tests/crud/conftest.py` | Violación DRY |
| Import directo de conftest | `test_user_router.py` → `from tests.api.conftest import create_test_user` | Anti-patrón según `pytest-best-practices` SKILL |
| Nombres de clases inconsistentes | Service usa `Create/Read`, roadmap pide `Insert/Select` | Inconsistencia en nomenclatura |

### Objetivo

Refactorizar la suite completa para que:

1. `tests/` replique la estructura de `src/` (organización por dominio funcional)
2. Cada archivo de test CRUD separe tests en clases por tipo de transacción: `Insert`, `Select`, `Update`, `Delete`
3. Polyfactory genere todos los datos de prueba, eliminando literales manuales
4. Se consoliden fixtures duplicadas y se eliminen anti-patrones

### Riesgo

**Medio** — La refactorización toca todos los archivos de test. Un error en fixtures o factories puede romper la suite entera.

**Mitigación** — Ejecutar `uv run pytest -v` tras cada fase para verificar regresiones incrementalmente.

### Enfoque

Migración incremental por fases: baseline → factories → reestructurar directorios → migrar y refactorizar por dominio → limpieza → validación QA.

---

## Estructura actual vs. propuesta

### Estructura actual

```
tests/
├── conftest.py              # Global
├── api/                     # Por capa ❌
│   ├── conftest.py          # seed_user_role (duplicada)
│   ├── test_health.py
│   └── test_user_router.py  # 1 clase: TestUserRouter
├── crud/                    # Por capa ❌
│   ├── conftest.py          # seed_user_role (duplicada)
│   └── test_user_repository.py  # 1 clase: TestUserRepository
├── service/
│   └── test_user_service.py # 4 clases (nombres inconsistentes)
└── unit/
    ├── test_exceptions.py
    └── test_pagination.py
```

### Estructura propuesta

```
tests/
├── conftest.py              # Global (sin cambios)
├── factories.py             # Polyfactory factories centralizadas ✨
├── test_health.py           # Migrado desde api/ (endpoint de main.py)
├── users/                   # Replica src/users/ ✅
│   ├── __init__.py
│   ├── conftest.py          # seed_user_role consolidada + helpers
│   └── users/               # Replica src/users/users/ ✅
│       ├── __init__.py
│       ├── test_repository.py  # 4 clases: Insert/Select/Update/Delete
│       ├── test_service.py     # 4 clases: Insert/Select/Update/Delete
│       └── test_router.py      # 4 clases: Insert/Select/Update/Delete
├── core/                    # Replica src/core/ ✅
│   ├── __init__.py
│   └── test_exceptions.py
└── shared/                  # Replica src/shared/ ✅
    ├── __init__.py
    └── test_pagination.py
```

---

## Decisiones de diseño

### Nomenclatura de clases

Patrón: `Test{Entidad}{Capa}{Transacción}` con nombres SQL: `Insert`, `Select`, `Update`, `Delete`.

Ejemplos: `TestUserRepositoryInsert`, `TestUserRouterSelect`, `TestUserServiceDelete`.

### Tests sin separación CRUD

Los tests de excepciones (`TestAppExceptions`) y paginación (`TestPaginationParams`) **no** son CRUD de entidades sino validaciones de constructores y parámetros. Se mantienen sus clases actuales sin separación por transacción.

### Factories como clases importables

Las factory classes se centralizan en `tests/factories.py` y se importan donde se necesiten. No son fixtures sino clases utilitarias que no requieren setup/teardown.

### Relaciones SQLModel en Polyfactory

Los modelos SQLModel con `table=True` tienen campos de relación (`user_role`, `user_ai_profiles`) que Polyfactory no puede generar automáticamente. Se excluyen con `__set_relationships__ = False` en las factories de modelos.

---

## Fases de Implementación

### Fase 1: Baseline y Dependencias

**Objetivo**: Confirmar estado actual y agregar Polyfactory.

**Archivos a modificar**: `pyproject.toml`.

**Conceptos aplicados**: `AGENTS.md` (comandos de testing).

- [ ] Ejecutar `uv run pytest -v` — confirmar que todos los tests pasan (esperados: 44 tests)
- [ ] Ejecutar `uv run pytest --cov=src --cov-report=term-missing` — registrar cobertura baseline
- [ ] Guardar el resultado de cobertura en un comentario o nota para comparar en Fase 7
- [ ] Abrir `pyproject.toml` línea 40 (`[dependency-groups] dev`)
- [ ] Agregar `"polyfactory>=2.0.0"` después de `"coverage>=7.15.0"` (línea 46)
- [ ] Ejecutar `uv sync` para instalar la nueva dependencia
- [ ] Verificar instalación: ejecutar `uv run python -c "from polyfactory.factories.pydantic_factory import ModelFactory; print('OK')"`

---

### Fase 2: Crear Factories con Polyfactory

**Objetivo**: Centralizar la generación de datos de prueba con Polyfactory.

**Archivos a crear**: `tests/factories.py`.

**Conceptos aplicados**: Polyfactory `ModelFactory`, `python-best-practices` (SKILL.md §3 documentación, §4 tipado), `references/polyfactory.md`.

Factories a implementar:

| Factory | Modelo/Schema base | Uso principal |
|---|---|---|
| `UserCreateFactory` | `UserCreate` | Tests de repository y router |
| `UserUpdateFactory` | `UserUpdate` | Tests de update |
| `UserModelFactory` | `User` | Tests de service (con mocks) |
| `UserRoleModelFactory` | `UserRole` | Tests de service (con mocks) |

Ejemplo de uso:

```python
# Service test (mock-based)
user = UserModelFactory.build(id="user-123", id_role=1)

# Repository/Router test (DB-based)
user_data = UserCreateFactory.build(id_role=seed_role.id)

# Router test (HTTP payload)
payload = UserCreateFactory.build(id_role=seed_role.id).model_dump(mode="json")
```

- [ ] Crear archivo `tests/factories.py` con docstring de módulo
- [ ] Agregar imports: `from polyfactory.factories.pydantic_factory import ModelFactory`
- [ ] Agregar imports de schemas: `from src.users.schemas import UserCreate, UserUpdate`
- [ ] Agregar imports de modelos: `from src.users.models import User, UserRole`
- [ ] Implementar `UserCreateFactory`:
  - [ ] `__model__ = UserCreate`
  - [ ] Verificar que genera `EmailStr` válidos (campo `email` de `UserCreate`)
  - [ ] Verificar que genera `int` para `id_role`
  - [ ] Verificar que genera `str` para `first_name` y `last_name`
- [ ] Implementar `UserUpdateFactory`:
  - [ ] `__model__ = UserUpdate`
  - [ ] Verificar que todos los campos son opcionales (`Optional[str]`, `Optional[EmailStr]`, `Optional[int]`)
- [ ] Implementar `UserModelFactory`:
  - [ ] `__model__ = User`
  - [ ] `__set_relationships__ = False` (excluir `user_role: UserRole` y `user_ai_profiles: list[UserAIProfile]`)
  - [ ] Verificar que genera UUID válido para `id` (campo `str` con default `uuid4`)
- [ ] Implementar `UserRoleModelFactory`:
  - [ ] `__model__ = UserRole`
  - [ ] `__set_relationships__ = False` (excluir `users: list[User]`)
- [ ] Agregar docstrings Google-style a cada factory class
- [ ] Test de humo: ejecutar en consola `uv run python -c "from tests.factories import UserCreateFactory; print(UserCreateFactory.build())"` para verificar que genera datos válidos

---

### Fase 3: Nueva Estructura de Directorios y Conftest

**Objetivo**: Crear la nueva estructura que replica `src/` y consolidar fixtures duplicadas.

**Archivos a crear**: `tests/users/__init__.py`, `tests/users/conftest.py`, `tests/users/users/__init__.py`, `tests/core/__init__.py`, `tests/shared/__init__.py`.

**Conceptos aplicados**: `pytest-best-practices` (SKILL.md §5: estructura replica `src/`, conftest.py jerárquico), `AGENTS.md` (estructura del proyecto).

#### 3.1 — Crear directorios con `__init__.py`

- [ ] Crear `tests/users/__init__.py` (archivo vacío)
- [ ] Crear `tests/users/users/__init__.py` (archivo vacío)
- [ ] Crear `tests/core/__init__.py` (archivo vacío)
- [ ] Crear `tests/shared/__init__.py` (archivo vacío)

#### 3.2 — Crear `tests/users/conftest.py` consolidado

Este archivo reemplaza a `tests/api/conftest.py` y `tests/crud/conftest.py`.

- [ ] Crear archivo `tests/users/conftest.py` con docstring: `"""Fixtures compartidas para el dominio Users."""`
- [ ] Agregar imports necesarios:
  - [ ] `import pytest`
  - [ ] `from httpx import AsyncClient`
  - [ ] `from sqlalchemy.ext.asyncio import AsyncSession`
  - [ ] `from src.users.models import UserRole`
- [ ] Migrar fixture `seed_user_role` (consolidar las 2 versiones idénticas):
  - [ ] Fuente 1: `tests/api/conftest.py` líneas 10-23 → copia exacta con docstring actualizado
  - [ ] Fuente 2: `tests/crud/conftest.py` líneas 9-22 → idéntica, se descarta
  - [ ] Contenido: inserta `UserRole(name="ESTUDIANTE", description="Rol de estudiante de pruebas")`, hace `flush()`, retorna `UserRole`
  - [ ] Mantener la firma: `async def seed_user_role(db_session: AsyncSession) -> UserRole`
- [ ] Convertir `create_test_user` de función helper a fixture callable:
  - [ ] Fuente: `tests/api/conftest.py` líneas 26-43 (actualmente es una función async, no una fixture)
  - [ ] Problema: `test_user_router.py` la importa con `from tests.api.conftest import create_test_user` (anti-patrón)
  - [ ] Solución: crear fixture `create_test_user` que retorna un callable async:
    ```python
    @pytest.fixture
    def create_test_user(async_client: AsyncClient):
        async def _create(user_data: dict, role_id: int) -> dict:
            payload = {**user_data, "id_role": role_id}
            response = await async_client.post("/v1/users/", json=payload)
            return response.json()
        return _create
    ```
  - [ ] Docstring Google-style en la fixture
  - [ ] Docstring Google-style en la función interna `_create`
- [ ] Verificar que `tests/conftest.py` (global) no requiere cambios — solo revisar que `db_session`, `async_client`, `setup_database` y `event_loop` siguen disponibles

---

### Fase 4: Migrar y Refactorizar Tests de Users

**Objetivo**: Mover tests del dominio users a la nueva estructura, separar en clases por tipo de transacción y reemplazar datos manuales con Polyfactory.

**Archivos a crear**: `tests/users/users/test_repository.py`, `tests/users/users/test_service.py`, `tests/users/users/test_router.py`.

**Conceptos aplicados**: `AGENTS.md` (roadmap §6: separación por transacción), `pytest-best-practices` (SKILL.md §2: nomenclatura, §3: patrón AAA, §11: Polyfactory), `tdd` (SKILL.md: tests verifican comportamiento, no implementación).

#### 4.1 — test_repository.py

Migración de `tests/crud/test_user_repository.py` (286 líneas, 12 tests en 1 clase) → `tests/users/users/test_repository.py` (4 clases).

**Imports a cambiar:**
- [ ] Agregar: `from tests.factories import UserCreateFactory, UserUpdateFactory`
- [ ] Mantener: `from sqlalchemy.ext.asyncio import AsyncSession`
- [ ] Mantener: `from src.users.models import User, UserAIProfile, UserLevel, UserRole, UserTopic`
- [ ] Eliminar: `from src.users.schemas import UserCreate, UserUpdate` (se reemplazan por factories)
- [ ] Mantener: `from src.users.users.repository import UserRepository`

**Clase `TestUserRepositoryInsert`:**
- [ ] Crear clase con docstring: `"""Tests de inserción para UserRepository."""`
- [ ] Migrar `test_add_persists_and_returns_user`:
  - [ ] Reemplazar `UserCreate(id_role=..., first_name="Juan", last_name="Perez", email="juan.perez@example.com")` por `UserCreateFactory.build(id_role=seed_user_role.id)`
  - [ ] Ajustar asserts: en vez de `assert user.first_name == "Juan"`, usar `assert user.first_name == user_data.first_name`
  - [ ] Mantener assert `user.id is not None` y `user.id_role == seed_user_role.id`

**Clase `TestUserRepositorySelect`:**
- [ ] Crear clase con docstring: `"""Tests de lectura para UserRepository."""`
- [ ] Migrar `test_get_by_id_returns_existing_user`:
  - [ ] Reemplazar `User(id_role=..., first_name="Pedro", last_name="Gomez", email="pedro.gomez@example.com")` por creación vía `UserCreateFactory.build(id_role=seed_user_role.id)` + inserción con `repo.add()`
  - [ ] Ajustar assert de email: usar variable del factory en vez de literal `"pedro.gomez@example.com"`
- [ ] Migrar `test_get_by_id_returns_none_for_nonexistent`:
  - [ ] Sin cambios de datos (usa UUID cero hardcodeado — mantener porque es un ID inválido deliberado)
- [ ] Migrar `test_get_by_email_returns_existing_user`:
  - [ ] Reemplazar `User(id_role=..., first_name="Maria", last_name="Lopez", email="maria.lopez@example.com")` por factory
  - [ ] Ajustar assert y búsqueda por email usando variable del factory
- [ ] Migrar `test_get_by_email_returns_none_for_nonexistent`:
  - [ ] Sin cambios de datos (usa email literal deliberado para búsqueda inexistente — mantener)
- [ ] Migrar `test_get_all_returns_list`:
  - [ ] Reemplazar list comprehension manual `User(first_name=f"User{i}", ...)` por `UserCreateFactory.batch(size=3, id_role=seed_user_role.id)` + inserción con `repo.add()` por cada uno
- [ ] Migrar `test_get_all_returns_empty_list_when_no_users`:
  - [ ] Sin cambios de datos (no crea usuarios)
- [ ] Migrar `test_count_returns_zero_when_empty`:
  - [ ] Sin cambios de datos (no crea usuarios)
- [ ] Migrar `test_count_returns_correct_number`:
  - [ ] Reemplazar list comprehension manual `User(first_name=f"CountUser{i}", ...)` por factory batch
- [ ] Migrar `test_get_detailed_loads_relationships`:
  - [ ] **Excepción**: Este test crea `UserLevel`, `UserTopic` y `UserAIProfile` manualmente porque no hay factories para ellos aún. Mantener datos manuales para estas entidades auxiliares. Solo reemplazar la creación del `User` por factory
  - [ ] Mantener los asserts de relaciones (`user_role.name == "ESTUDIANTE"`, `user_ai_profiles`, etc.)

**Clase `TestUserRepositoryUpdate`:**
- [ ] Crear clase con docstring: `"""Tests de actualización para UserRepository."""`
- [ ] Migrar `test_update_modifies_fields`:
  - [ ] Reemplazar `User(first_name="OriginalName", ...)` por factory
  - [ ] Reemplazar `UserUpdate(first_name="NewName", last_name="NewLastName")` por `UserUpdateFactory.build()` con overrides
  - [ ] Ajustar asserts para usar variables del factory en vez de literales

**Clase `TestUserRepositoryDelete`:**
- [ ] Crear clase con docstring: `"""Tests de eliminación para UserRepository."""`
- [ ] Migrar `test_delete_removes_user`:
  - [ ] Reemplazar `User(first_name="DeleteMe", ...)` por factory
  - [ ] Mantener assert `deleted is None` después del `db_session.get()`

**Verificación parcial:**
- [ ] Ejecutar `uv run pytest tests/users/users/test_repository.py -v` — 12 tests pasan
- [ ] Verificar que los tests del directorio antiguo `tests/crud/test_user_repository.py` aún existen y pasan (no se eliminan hasta Fase 6)

---

#### 4.2 — test_service.py

Migración de `tests/service/test_user_service.py` (432 líneas, 16 tests en 4 clases) → `tests/users/users/test_service.py` (4 clases renombradas).

**Imports a cambiar:**
- [ ] Agregar: `from tests.factories import UserModelFactory, UserCreateFactory, UserUpdateFactory`
- [ ] Mantener: `from unittest.mock import AsyncMock`
- [ ] Mantener: `import pytest`
- [ ] Mantener: `from src.core.exceptions import ConflictException, DatabaseException, NotFoundException`
- [ ] Mantener: `from src.shared.pagination import PaginatedResponse, PaginationParams`
- [ ] Eliminar: `from src.users.models import User` (se reemplaza por `UserModelFactory`)
- [ ] Mantener: `from src.users.schemas import UserCreate, UserResponse, UserUpdate` — **NOTA**: `UserCreate` y `UserUpdate` siguen necesarios como tipos en las assertions, pero los datos se generan con factories
- [ ] Mantener: `from src.users.users.service import UserService`

**Fixtures locales a mantener en el archivo:**
- [ ] `mock_session` (líneas 18-25): `AsyncMock` con `.commit`, `.rollback`, `.refresh`
- [ ] `mock_repository` (líneas 28-31): `AsyncMock()` simple
- [ ] `user_service` (líneas 34-37): `UserService(session=mock_session, repository=mock_repository)`

**Clase `TestUserServiceCreate` → `TestUserServiceInsert`:**
- [ ] Renombrar clase: `TestUserServiceCreate` → `TestUserServiceInsert`
- [ ] Actualizar docstring: `"""Pruebas unitarias para el método UserService.create."""` → `"""Tests de inserción para UserService."""`
- [ ] Migrar `test_create_calls_commit_on_success` (4 instancias hardcodeadas):
  - [ ] Reemplazar `UserCreate(id_role=1, first_name="John", last_name="Doe", email="john@example.com")` → `UserCreateFactory.build(id_role=1)`
  - [ ] Reemplazar `User(id="user-123", id_role=1, first_name="John", ...)` → `UserModelFactory.build(id="user-123", email=user_data.email, id_role=user_data.id_role)`
  - [ ] Ajustar assert: `mock_repository.get_by_email.assert_called_once_with("john@example.com")` → `...assert_called_once_with(user_data.email)`
- [ ] Migrar `test_create_calls_rollback_on_repository_error`:
  - [ ] Reemplazar `UserCreate(...)` → `UserCreateFactory.build(id_role=1)`
  - [ ] Mantener `pytest.raises(DatabaseException, match="Database operation failed")`
- [ ] Migrar `test_create_calls_rollback_on_commit_error`:
  - [ ] Reemplazar `UserCreate(...)` y `User(...)` → factories
- [ ] Migrar `test_create_raises_conflict_for_duplicate_email`:
  - [ ] Reemplazar `UserCreate(...)` → `UserCreateFactory.build(id_role=1)`
  - [ ] Reemplazar `User(id="user-existing", ...)` → `UserModelFactory.build(email=user_data.email)`
  - [ ] Mantener `pytest.raises(ConflictException)`

**Clase `TestUserServiceRead` → `TestUserServiceSelect`:**
- [ ] Renombrar clase: `TestUserServiceRead` → `TestUserServiceSelect`
- [ ] Actualizar docstring: `"""Tests de lectura para UserService."""`
- [ ] Migrar `test_get_by_id_returns_user`:
  - [ ] Reemplazar `User(id=user_id, id_role=1, first_name="John", ...)` → `UserModelFactory.build(id=user_id)`
- [ ] Migrar `test_get_by_id_raises_not_found`:
  - [ ] Sin cambios de datos (mock retorna `None`, mantener literal `"non-existent"`)
- [ ] Migrar `test_get_detailed_returns_user`:
  - [ ] Reemplazar `User(...)` → `UserModelFactory.build(id=user_id)`
- [ ] Migrar `test_get_detailed_raises_not_found`:
  - [ ] Sin cambios de datos
- [ ] Migrar `test_get_all_returns_paginated_response`:
  - [ ] Reemplazar `User(id="user-123", ...)` → `UserModelFactory.build()`
  - [ ] Ajustar assert `result.items[0].id == "user-123"` → `result.items[0].id == expected_user.id`

**Clase `TestUserServiceUpdate` (sin renombrar):**
- [ ] Mantener nombre de clase
- [ ] Migrar `test_update_calls_commit_on_success`:
  - [ ] Reemplazar `User(id=user_id, ...)` → `UserModelFactory.build(id=user_id)`
  - [ ] Reemplazar `UserUpdate(first_name="Johnny")` → `UserUpdateFactory.build()`
  - [ ] Reemplazar `User(id=user_id, first_name="Johnny", ...)` → `UserModelFactory.build(id=user_id, first_name=update_data.first_name)`
- [ ] Migrar `test_update_calls_rollback_on_error`:
  - [ ] Reemplazar `User(...)` y `UserUpdate(...)` → factories
- [ ] Migrar `test_update_raises_conflict_for_duplicate_email`:
  - [ ] Reemplazar ambos `User(...)` → `UserModelFactory.build()` con emails distintos
  - [ ] Reemplazar `UserUpdate(email="other@example.com")` → `UserUpdateFactory.build(email=other_user.email)`
- [ ] Migrar `test_update_raises_not_found`:
  - [ ] Reemplazar `UserUpdate(first_name="Johnny")` → `UserUpdateFactory.build()`

**Clase `TestUserServiceDelete` (sin renombrar):**
- [ ] Mantener nombre de clase
- [ ] Migrar `test_delete_calls_commit_on_success`:
  - [ ] Reemplazar `User(id=user_id, id_role=1, ...)` → `UserModelFactory.build(id=user_id)`
- [ ] Migrar `test_delete_calls_rollback_on_error`:
  - [ ] Reemplazar `User(...)` → `UserModelFactory.build(id=user_id)`
- [ ] Migrar `test_delete_raises_not_found`:
  - [ ] Sin cambios de datos (mock retorna `None`)

**Verificación parcial:**
- [ ] Ejecutar `uv run pytest tests/users/users/test_service.py -v` — 16 tests pasan
- [ ] Verificar que los tests del directorio antiguo `tests/service/test_user_service.py` aún existen y pasan

---

#### 4.3 — test_router.py

Migración de `tests/api/test_user_router.py` (375 líneas, 14 tests en 1 clase `TestUserRouter`) → `tests/users/users/test_router.py` (4 clases).

**Imports a cambiar:**
- [ ] Agregar: `from tests.factories import UserCreateFactory`
- [ ] Mantener: `from httpx import AsyncClient`
- [ ] Mantener: `from src.users.models import UserRole`
- [ ] **Eliminar**: `from tests.api.conftest import create_test_user` (anti-patrón de import directo)
  - [ ] En su lugar, usar la fixture `create_test_user` de `tests/users/conftest.py` (pytest la inyecta automáticamente)

**Clase `TestUserRouterInsert`:**
- [ ] Crear clase con docstring: `"""Tests de inserción para UserRouter (POST /v1/users/)."""`
- [ ] Migrar `test_create_user_returns_201`:
  - [ ] Reemplazar payload manual `{"id_role": ..., "first_name": "Test", ...}` → `UserCreateFactory.build(id_role=seed_user_role.id).model_dump(mode="json")`
  - [ ] Ajustar asserts: `assert data["first_name"] == "Test"` → `assert data["first_name"] == payload["first_name"]`
  - [ ] Mantener assert `"id" in data` y `response.status_code == 201`
- [ ] Migrar `test_create_user_returns_422_invalid_email`:
  - [ ] Reemplazar payload manual → `UserCreateFactory.build(id_role=seed_user_role.id, email="not-an-email").model_dump(mode="json")`
  - [ ] **NOTA**: Polyfactory genera emails válidos por defecto, pero necesitamos un email inválido aquí. Usar override explícito `email="not-an-email"`
- [ ] Migrar `test_create_user_returns_409_duplicate_email`:
  - [ ] Reemplazar ambos payloads manuales por factories con override `email="duplicate@example.com"`
  - [ ] Alternativa: generar con factory y usar el email generado para el segundo payload
  - [ ] Mantener asserts RFC 9457: `data["status"] == 409`, `"title" in data`, `"type" in data`, `"instance" in data`

**Clase `TestUserRouterSelect`:**
- [ ] Crear clase con docstring: `"""Tests de lectura para UserRouter (GET /v1/users/)."""`
- [ ] Migrar `test_get_user_returns_200`:
  - [ ] Reemplazar `user_data = {"first_name": "Get", "last_name": "User", "email": "get.user@example.com"}` → generar con factory
  - [ ] Cambiar `await create_test_user(async_client, user_data, seed_user_role.id)` → `await create_test_user(user_data, seed_user_role.id)` (la fixture ya tiene `async_client` inyectado)
  - [ ] Ajustar asserts para usar variables del factory
- [ ] Migrar `test_get_user_returns_404_nonexistent`:
  - [ ] Sin cambios de datos (UUID cero intencional)
  - [ ] Mantener assert RFC 9457: `data["status"] == 404`
- [ ] Migrar `test_get_user_detailed_returns_200_with_role`:
  - [ ] Reemplazar `user_data` manual → factory
  - [ ] Cambiar llamada a `create_test_user` (fixture, no import)
  - [ ] Mantener asserts de relaciones: `data["user_role"]["name"] == "ESTUDIANTE"`, `isinstance(data["user_ai_profiles"], list)`
- [ ] Migrar `test_get_user_detailed_returns_404_nonexistent`:
  - [ ] Sin cambios de datos
- [ ] Migrar `test_list_users_returns_200_with_pagination`:
  - [ ] Reemplazar `user_data` manual → factory
  - [ ] Cambiar llamada a `create_test_user` (fixture)
  - [ ] Mantener asserts de estructura paginada: `"items"`, `"total"`, `"limit"`, `"offset"`
- [ ] Migrar `test_list_users_returns_200_empty`:
  - [ ] Sin cambios de datos (no crea usuarios)
- [ ] Migrar `test_list_users_respects_limit`:
  - [ ] Reemplazar el loop `for i in range(3): await create_test_user(async_client, {...}, ...)` → generar con factory batch
  - [ ] Cambiar cada llamada a `create_test_user` para usar la fixture
  - [ ] Mantener asserts: `len(data["items"]) == 2`, `data["total"] == 3`, `data["limit"] == 2`

**Clase `TestUserRouterUpdate`:**
- [ ] Crear clase con docstring: `"""Tests de actualización para UserRouter (PATCH /v1/users/{user_id})."""`
- [ ] Migrar `test_update_user_returns_200`:
  - [ ] Reemplazar `create_test_user(async_client, {"first_name": "Before", ...}, ...)` → factory + fixture
  - [ ] Mantener patch payload `json={"first_name": "After"}` (override intencional del test)
  - [ ] Ajustar assert `data["last_name"] == "Update"` → usar variable del factory
- [ ] Migrar `test_update_user_returns_404_nonexistent`:
  - [ ] Sin cambios de datos (UUID cero intencional)
- [ ] Migrar `test_update_user_returns_409_duplicate_email`:
  - [ ] Reemplazar ambas llamadas a `create_test_user(async_client, ...)` → factory + fixture
  - [ ] Mantener la lógica: crear user1 y user2 con emails distintos, intentar actualizar user2 con email de user1
  - [ ] Ajustar assert RFC 9457: `data["status"] == 409`

**Clase `TestUserRouterDelete`:**
- [ ] Crear clase con docstring: `"""Tests de eliminación para UserRouter (DELETE /v1/users/{user_id})."""`
- [ ] Migrar `test_delete_user_returns_204`:
  - [ ] Reemplazar `create_test_user(async_client, {"first_name": "Delete", ...}, ...)` → factory + fixture
  - [ ] Mantener asserts: `status_code == 204`, `response.text == ""`, verificación GET 404

**Verificación parcial:**
- [ ] Ejecutar `uv run pytest tests/users/users/test_router.py -v` — 14 tests pasan
- [ ] Verificar que los tests del directorio antiguo `tests/api/test_user_router.py` aún existen y pasan

---

### Fase 5: Migrar Tests de Core, Shared y Health

**Objetivo**: Completar la migración de los tests restantes a su ubicación por dominio.

**Archivos a crear**: `tests/core/test_exceptions.py`, `tests/shared/test_pagination.py`, `tests/test_health.py`.

**Conceptos aplicados**: `pytest-best-practices` (SKILL.md §5: estructura replica `src/`).

#### 5.1 — test_exceptions.py

- [ ] Copiar `tests/unit/test_exceptions.py` (70 líneas) → `tests/core/test_exceptions.py`
- [ ] Sin cambios de contenido (6 tests en clase `TestAppExceptions`)
- [ ] Verificar que los imports siguen funcionando:
  - [ ] `from fastapi import FastAPI, status`
  - [ ] `from httpx import ASGITransport, AsyncClient`
  - [ ] `from src.core.exceptions import AppException, ConflictException, DatabaseException, NotFoundException, ValidationException, register_exception_handlers`
- [ ] Ejecutar `uv run pytest tests/core/test_exceptions.py -v` — 6 tests pasan

#### 5.2 — test_pagination.py

- [ ] Copiar `tests/unit/test_pagination.py` (38 líneas) → `tests/shared/test_pagination.py`
- [ ] Sin cambios de contenido (5 tests en clase `TestPaginationParams`)
- [ ] Verificar que los imports siguen funcionando:
  - [ ] `import pytest`
  - [ ] `from pydantic import ValidationError`
  - [ ] `from src.shared.pagination import PaginationParams`
- [ ] Ejecutar `uv run pytest tests/shared/test_pagination.py -v` — 5 tests pasan

#### 5.3 — test_health.py

- [ ] Copiar `tests/api/test_health.py` (17 líneas) → `tests/test_health.py` (raíz de tests, porque `/health` está en `src/main.py` no en un dominio)
- [ ] Sin cambios de contenido (1 test en clase `TestHealthCheck`)
- [ ] Verificar que el import sigue funcionando:
  - [ ] `from httpx import AsyncClient`
- [ ] Ejecutar `uv run pytest tests/test_health.py -v` — 1 test pasa

#### 5.4 — Verificación conjunta

- [ ] Ejecutar `uv run pytest tests/core/ tests/shared/ tests/test_health.py -v` — 12 tests pasan en total

---

### Fase 6: Limpieza

**Objetivo**: Eliminar directorios y archivos obsoletos.

**Archivos a eliminar**: `tests/api/` (completo), `tests/crud/` (completo), `tests/service/` (completo), `tests/unit/` (completo).

#### 6.1 — Eliminar directorio `tests/api/`

- [ ] Eliminar `tests/api/__init__.py`
- [ ] Eliminar `tests/api/conftest.py` (fixture `seed_user_role` y helper `create_test_user` ya consolidados en `tests/users/conftest.py`)
- [ ] Eliminar `tests/api/test_health.py` (ya migrado a `tests/test_health.py`)
- [ ] Eliminar `tests/api/test_user_router.py` (ya migrado a `tests/users/users/test_router.py`)
- [ ] Eliminar directorio `tests/api/`

#### 6.2 — Eliminar directorio `tests/crud/`

- [ ] Eliminar `tests/crud/__init__.py`
- [ ] Eliminar `tests/crud/conftest.py` (fixture `seed_user_role` ya consolidada)
- [ ] Eliminar `tests/crud/test_user_repository.py` (ya migrado a `tests/users/users/test_repository.py`)
- [ ] Eliminar directorio `tests/crud/`

#### 6.3 — Eliminar directorio `tests/service/`

- [ ] Eliminar `tests/service/__init__.py`
- [ ] Eliminar `tests/service/test_user_service.py` (ya migrado a `tests/users/users/test_service.py`)
- [ ] Eliminar directorio `tests/service/`

#### 6.4 — Eliminar directorio `tests/unit/`

- [ ] Eliminar `tests/unit/__init__.py`
- [ ] Eliminar `tests/unit/test_exceptions.py` (ya migrado a `tests/core/test_exceptions.py`)
- [ ] Eliminar `tests/unit/test_pagination.py` (ya migrado a `tests/shared/test_pagination.py`)
- [ ] Eliminar directorio `tests/unit/`

#### 6.5 — Verificación post-limpieza

- [ ] Verificar que no existen los directorios: `tests/api/`, `tests/crud/`, `tests/service/`, `tests/unit/`
- [ ] Ejecutar `uv run pytest -v` — todos los tests pasan (misma cantidad que antes: 44 + los nuevos duplicados ya eliminados = 44)
- [ ] Buscar imports rotos: `grep -r "from tests.api" tests/` → sin resultados
- [ ] Buscar imports rotos: `grep -r "from tests.crud" tests/` → sin resultados
- [ ] Buscar imports rotos: `grep -r "from tests.service" tests/` → sin resultados
- [ ] Buscar imports rotos: `grep -r "from tests.unit" tests/` → sin resultados

---

### Fase 7: Validación QA (obligatoria)

**Objetivo**: Validación integral de la refactorización.

**Conceptos aplicados**: `AGENTS.md` (comandos de calidad de código).

#### 7.1 — Tests y cobertura

- [ ] `uv run pytest -v` — todos los tests pasan (44 tests esperados)
- [ ] `uv run pytest --cov=src --cov-report=term-missing` — cobertura ≥ 90%
- [ ] Comparar cobertura con baseline de Fase 1:
  - [ ] Cobertura total debe ser **igual o superior** al baseline
  - [ ] No deben aparecer líneas sin cubrir que antes estaban cubiertas

#### 7.2 — Calidad de código

- [ ] `uv run ruff check src/ tests/` — sin errores de linting
- [ ] `uv run ruff format --check src/ tests/` — formato correcto (verificar sin modificar)
- [ ] `uv run ruff format src/ tests/` — aplicar formato si hay diferencias
- [ ] `uv run mypy src/` — sin errores de tipos

#### 7.3 — Verificación estructural

- [ ] Verificar que la estructura final de `tests/` replica `src/`:
  - [ ] `tests/users/users/` corresponde a `src/users/users/`
  - [ ] `tests/core/` corresponde a `src/core/`
  - [ ] `tests/shared/` corresponde a `src/shared/`
- [ ] Verificar que no hay fixtures duplicadas:
  - [ ] `seed_user_role` existe **solo** en `tests/users/conftest.py`
  - [ ] No existe en `tests/conftest.py` ni en ningún otro conftest
- [ ] Verificar que no hay imports directos de archivos conftest:
  - [ ] `grep -r "from tests.*conftest import" tests/` → sin resultados
  - [ ] `grep -r "import tests.*conftest" tests/` → sin resultados
- [ ] Verificar que no quedan datos hardcodeados de usuarios:
  - [ ] `grep -r "first_name=\"John\"" tests/` → sin resultados (excepto posibles IDs intencionales)
  - [ ] `grep -r "UserCreate(" tests/` → solo en `tests/factories.py` (como `__model__`)
  - [ ] `grep -r "User(" tests/` → solo en `test_repository.py` para `test_get_detailed_loads_relationships` (entidades auxiliares)
- [ ] Verificar nomenclatura de clases:
  - [ ] `grep -r "class Test" tests/users/` → debe mostrar clases con sufijo `Insert`, `Select`, `Update`, `Delete`
  - [ ] No debe haber clases con nombres `TestUserServiceCreate`, `TestUserServiceRead`, `TestUserRouter` (nombres viejos)

---

## Criterios de Aceptación

1. La estructura de `tests/` replica la estructura de `src/` (`tests/users/users/`, `tests/core/`, `tests/shared/`)
2. Cada archivo de test de entidad CRUD tiene 4 clases separadas: `Test*Insert`, `Test*Select`, `Test*Update`, `Test*Delete`
3. Polyfactory genera todos los datos de prueba (no hay literales manuales de datos de usuario)
4. No existen fixtures duplicadas entre archivos conftest
5. No hay imports directos de archivos conftest
6. Todos los tests pasan (`uv run pytest -v`)
7. Cobertura ≥ 90% (`uv run pytest --cov=src`)
8. Ruff sin errores (`uv run ruff check src/ tests/`)
9. Mypy sin errores (`uv run mypy src/`)

---

## Referencias Técnicas

| Archivo | Propósito |
|---|---|
| [AGENTS.md](AGENTS.md) | Reglas del proyecto, directrices de testing, convenciones |
| [pytest-best-practices/SKILL.md](../../.agents/skills/pytest-best-practices/SKILL.md) | Patrón AAA, fixtures, conftest jerárquico, estructura |
| [tdd/SKILL.md](../../.agents/skills/tdd/SKILL.md) | Tests verifican comportamiento, no implementación |
| [python-best-practices/SKILL.md](../../.agents/skills/python-best-practices/SKILL.md) | PEP 8, documentación, tipado |
| [fastapi-app-creator/SKILL.md](../../.agents/skills/fastapi-app-creator/SKILL.md) | Arquitectura por capas, testing FastAPI |
| [pyproject.toml](../../pyproject.toml) | Configuración de pytest y dependencias |
| [tests/conftest.py](../../tests/conftest.py) | Fixtures globales actuales |
| [src/users/models.py](../../src/users/models.py) | Modelos SQLModel (base para factories) |
| [src/users/schemas.py](../../src/users/schemas.py) | Schemas Pydantic (base para factories) |

---

## Resumen de Archivos

| Archivo | Acción |
|---|---|
| `pyproject.toml` | Modificar |
| `tests/factories.py` | Crear |
| `tests/test_health.py` | Crear (migrar) |
| `tests/users/__init__.py` | Crear |
| `tests/users/conftest.py` | Crear |
| `tests/users/users/__init__.py` | Crear |
| `tests/users/users/test_repository.py` | Crear (migrar + refactorizar) |
| `tests/users/users/test_service.py` | Crear (migrar + refactorizar) |
| `tests/users/users/test_router.py` | Crear (migrar + refactorizar) |
| `tests/core/__init__.py` | Crear |
| `tests/core/test_exceptions.py` | Crear (migrar) |
| `tests/shared/__init__.py` | Crear |
| `tests/shared/test_pagination.py` | Crear (migrar) |
| `tests/conftest.py` | Revisar |
| `tests/api/` | Eliminar |
| `tests/crud/` | Eliminar |
| `tests/service/` | Eliminar |
| `tests/unit/` | Eliminar |
| `spec/roadmap.md` | Modificar |
