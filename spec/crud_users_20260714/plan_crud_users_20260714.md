# 004 · CRUD de Usuarios — Plan Revisado

## Análisis de discrepancias con el skill `fastapi-app-creator`

El plan original es **estructuralmente correcto** en su enfoque general (TDD, capas Router → Service → Repository), pero presenta deficiencias en el nivel de detalle de las tareas pendientes (Fases 3–5) y omite aspectos clave que el skill define como obligatorios.

### Discrepancias identificadas

| # | Aspecto | Plan original | Skill `fastapi-app-creator` | Acción |
|---|---|---|---|---|
| 1 | **Cadena de inyección** | Solo menciona "Implementar `get_user_service`" sin detalle | Define explícitamente la cadena: `get_session → UserRepository(session) → UserService(session, repository)` (sección 12) | Detallar la cadena completa en Dependencies |
| 2 | **Firmas del Router** | Lista endpoints en tabla pero no especifica firmas de funciones, decoradores ni inyección | Sección 6 define que cada endpoint debe tener `response_model`, `status_code`, y recibir el `service` vía `Depends()` | Agregar firmas completas de cada endpoint |
| 3 | **Firmas del Service** | Lista métodos con descripción pero sin firmas tipadas | Sección 7 muestra `__init__(self, session, repository)` y métodos async con tipos explícitos | Agregar firmas tipadas completas |
| 4 | **Docstrings** | No se mencionan | Las skills `python-best-practices` y `fastapi-app-creator` requieren docstrings Google-style en todas las clases y métodos | Agregar como tarea explícita |
| 5 | **Tareas granulares Fase 3** | 4 tareas genéricas para 14 tests | Deberían desglosarse por endpoint para facilitar seguimiento | Desglosar por grupo de endpoint |
| 6 | **Tareas granulares Fase 4** | 3 tareas para Service + Paginación | La paginación y el service son componentes distintos que requieren detalle independiente | Separar en subtareas específicas |
| 7 | **Tareas granulares Fase 5** | 6 tareas para Dependencies + Router + registro | El router tiene 6 endpoints individuales que merecen detalle | Desglosar endpoint por endpoint |
| 8 | **Validación `__init__.py`** | Solo "Actualizar `__init__.py` para exportar router" | Debería exportar el `router` con nombre descriptivo para evitar colisiones | Especificar qué se exporta |

---

## Contexto

| Aspecto | Detalle |
|---|---|
| **Resumen** | El sub-módulo `src/users/users/` tiene los archivos scaffolded (`repository.py`, `service.py`, `router.py`, `dependencies.py`) pero están vacíos (solo docstrings). Los modelos (`User`) y schemas (`UserCreate`, `UserUpdate`, `UserResponse`, `UserDetailed`) ya existen. El `main.py` no registra ningún router. No existen tests de integración. `src/shared/pagination.py` está vacío. **Las Fases 1 y 2 ya están completadas**: el `UserRepository` está implementado y sus 10 tests pasan. |
| **Justificación** | El CRUD de usuarios es la funcionalidad base sobre la que se construirán las demás features del sistema (autenticación, perfiles IA, sesiones de chat). Sin endpoints funcionales, la API no tiene utilidad. |
| **Objetivo** | Completar la implementación del CRUD (Create, Read one, Read all con paginación, Read detailed, Update, Delete) para la entidad `User` siguiendo la arquitectura Router → Service → Repository con TDD. |
| **Riesgo** | Bajo. Es la primera implementación funcional sobre una estructura existente. Las Fases 1-2 ya validaron el acceso a datos. |
| **Enfoque** | Continuar TDD vertical (red → green). Escribir tests de integración del router → Implementar paginación → Service → Dependencies → Router → Validación QA. |

---

## Seams de Testing (TDD)

> [!IMPORTANT]
> Según la skill TDD, los seams deben acordarse antes de escribir tests. Los seams son:
> 1. **Repository (seam de datos):** Tests unitarios en `tests/crud/test_user_repository.py` — ✅ **Completados (10 tests)**.
> 2. **Router/API (seam HTTP):** Tests de integración en `tests/api/test_user_router.py` — verifican el comportamiento end-to-end a través de `AsyncClient`.
>
> **No se testea la capa Service de forma aislada** porque la skill TDD establece "don't mock your own classes/modules" y el service coordina repository + transacciones. Su comportamiento se verifica indirectamente a través de los tests de integración del router.

---

## Decisiones de Diseño

> [!IMPORTANT]
> **Prefijo de ruta:** El router se registrará como `app.include_router(users_router, prefix="/v1/users", tags=["users"])` siguiendo la convención de versionado del skill `fastapi-app-creator` (sección 4).

> [!IMPORTANT]
> **Paginación genérica:** Se implementará un esquema `PaginatedResponse[T]` en `src/shared/pagination.py` con parámetros `offset`/`limit` y metadata (`total`, `limit`, `offset`). Será reutilizable por cualquier dominio.

> [!IMPORTANT]
> **Endpoint detallado separado:** `GET /v1/users/{user_id}/detailed` usará `UserDetailed` con eager loading de `user_role` y `user_ai_profiles`. El `GET /v1/users/{user_id}` estándar retornará `UserResponse` sin relaciones cargadas.

> [!IMPORTANT]
> **Cadena de inyección (skill sección 12):** La dependencia `get_user_service` en `dependencies.py` construirá la cadena completa:
> ```python
> async def get_user_service(
>     session: AsyncSession = Depends(get_session),
> ) -> UserService:
>     repository = UserRepository(session)
>     return UserService(session, repository)
> ```
> Esto sigue exactamente el patrón del skill: la sesión se inyecta desde `core/dependencies.py`, el repositorio se instancia con esa sesión, y el servicio recibe ambos.

> [!WARNING]
> **Dependencia de `UserRole`:** El modelo `User` tiene un FK obligatorio a `user_role`. Para crear un usuario en tests es necesario que exista al menos un rol en la DB. La fixture `seed_user_role` ya existe en `tests/crud/conftest.py` y se reutilizará en `tests/api/conftest.py`.

---

## Fases completadas

### ~~Fase 1 — Tests unitarios del Repository (Red)~~ ✅

**Objetivo:** Escribir los tests que definen el contrato del `UserRepository` antes de implementarlo.

**Archivos creados:**
- `tests/crud/conftest.py`
- `tests/crud/test_user_repository.py`

Tests planificados (10):

| # | Test | Verifica |
|---|---|---|
| 1 | `test_add_persists_and_returns_user` | `add()` inserta un usuario y retorna instancia con `id` |
| 2 | `test_get_by_id_returns_existing_user` | `get_by_id()` retorna el usuario correcto |
| 3 | `test_get_by_id_returns_none_for_nonexistent` | Retorna `None` si no existe |
| 4 | `test_get_by_email_returns_existing_user` | Búsqueda por email funciona |
| 5 | `test_get_by_email_returns_none_for_nonexistent` | Retorna `None` si no existe |
| 6 | `test_get_all_returns_list` | `get_all()` retorna lista de usuarios |
| 7 | `test_get_all_returns_empty_list` | Lista vacía cuando no hay registros |
| 8 | `test_update_modifies_fields` | `update()` modifica solo campos proporcionados |
| 9 | `test_delete_removes_user` | `delete()` elimina el registro |
| 10 | `test_get_detailed_loads_relationships` | `get_detailed()` carga `user_role` y `user_ai_profiles` |

Checklist:
- [x] Crear `tests/crud/conftest.py` con fixture `seed_user_role` que inserte un `UserRole` base
- [x] Crear fixture `sample_user_create` que retorne un dict con datos válidos de `UserCreate`
- [x] Escribir los 10 tests unitarios del repository siguiendo patrón AAA
- [x] Verificar que todos fallan: `uv run pytest tests/crud/test_user_repository.py -v` (fase Red)

---

### ~~Fase 2 — Implementación del Repository (Green)~~ ✅

**Objetivo:** Implementar `UserRepository` para que los tests de la Fase 1 pasen.

**Archivo modificado:**
- `src/users/users/repository.py`

Métodos implementados:

| Método | Firma | Descripción |
|---|---|---|
| `__init__` | `(self, session: AsyncSession) -> None` | Recibe la sesión inyectada |
| `add` | `(self, user_data: UserCreate) -> User` | Crea instancia y agrega a sesión |
| `get_by_id` | `(self, user_id: str) -> User \| None` | Query por PK |
| `get_by_email` | `(self, email: str) -> User \| None` | Query por email único |
| `get_all` | `(self, offset: int, limit: int) -> list[User]` | Query con offset/limit |
| `count` | `(self) -> int` | Cuenta total de registros |
| `update` | `(self, user: User, user_data: UserUpdate) -> User` | Actualiza campos no-`None` |
| `delete` | `(self, user: User) -> None` | Elimina instancia de la sesión |
| `get_detailed` | `(self, user_id: str) -> User \| None` | Query con eager loading de relaciones |

Checklist:
- [x] Implementar clase `UserRepository` con los 9 métodos
- [x] Usar `selectinload` para eager loading en `get_detailed`
- [x] Ejecutar `uv run pytest tests/crud/test_user_repository.py -v` — todos deben pasar (fase Green)

---

## Fases pendientes

### ~~Fase 3 — Tests de integración del Router (Red)~~ ✅

**Objetivo:** Escribir los tests de integración que definen el contrato HTTP del CRUD antes de implementar Service, Dependencies y Router.

**Archivos creados:**
- `tests/api/conftest.py`
- `tests/api/test_user_router.py`

**Tests planificados (14):**

#### POST `/v1/users/`

| # | Test | Status esperado | Verifica |
|---|---|---|---|
| 1 | `test_create_user_returns_201` | `201 Created` | Body válido con `UserCreate` → retorna `UserResponse` con `id`, `created_at`, `updated_at` |
| 2 | `test_create_user_returns_422_invalid_email` | `422 Unprocessable Entity` | Email inválido → validación Pydantic (`EmailStr`) |
| 3 | `test_create_user_returns_409_duplicate_email` | `409 Conflict` | Email duplicado → `ConflictException` con formato RFC 9457 |

#### GET `/v1/users/{user_id}`

| # | Test | Status esperado | Verifica |
|---|---|---|---|
| 4 | `test_get_user_returns_200` | `200 OK` | UUID existente → retorna `UserResponse` |
| 5 | `test_get_user_returns_404_nonexistent` | `404 Not Found` | UUID inexistente → `NotFoundException` con formato RFC 9457 |

#### GET `/v1/users/{user_id}/detailed`

| # | Test | Status esperado | Verifica |
|---|---|---|---|
| 6 | `test_get_user_detailed_returns_200_with_role` | `200 OK` | Retorna `UserDetailed` con `user_role` (objeto) y `user_ai_profiles` (lista) |
| 7 | `test_get_user_detailed_returns_404_nonexistent` | `404 Not Found` | UUID inexistente |

#### GET `/v1/users/?offset=0&limit=10`

| # | Test | Status esperado | Verifica |
|---|---|---|---|
| 8 | `test_list_users_returns_200_with_pagination` | `200 OK` | Respuesta con claves `items`, `total`, `offset`, `limit` |
| 9 | `test_list_users_returns_200_empty` | `200 OK` | Sin usuarios → `items: []`, `total: 0` |
| 10 | `test_list_users_respects_limit` | `200 OK` | Crear 3 usuarios, `limit=2` → `len(items) == 2`, `total == 3` |

#### PATCH `/v1/users/{user_id}`

| # | Test | Status esperado | Verifica |
|---|---|---|---|
| 11 | `test_update_user_returns_200` | `200 OK` | Actualización parcial → retorna `UserResponse` con campo modificado |
| 12 | `test_update_user_returns_404_nonexistent` | `404 Not Found` | UUID inexistente |
| 13 | `test_update_user_returns_409_duplicate_email` | `409 Conflict` | Email ya existente en otro usuario |

#### DELETE `/v1/users/{user_id}`

| # | Test | Status esperado | Verifica |
|---|---|---|---|
| 14 | `test_delete_user_returns_204` | `204 No Content` | Eliminación exitosa, sin body |

**Checklist:**

- [x] **Crear `tests/api/conftest.py`** con:
  - [x] Fixture `seed_user_role` (reutilizar lógica de `tests/crud/conftest.py`) que inserte un `UserRole` base y retorne la instancia
  - [x] Helper async `create_test_user(async_client, user_data, role_id)` que cree un usuario via `POST /v1/users/` y retorne el JSON de respuesta
- [x] **Escribir tests del endpoint `POST /v1/users/`** (tests 1-3):
  - [x] `test_create_user_returns_201`: Enviar `{"name": "Test", "email": "test@example.com", "user_role_id": "<role_uuid>"}` → verificar status 201, verificar que el body contiene `id`, `name`, `email`, `created_at`, `updated_at`
  - [x] `test_create_user_returns_422_invalid_email`: Enviar email inválido → verificar status 422
  - [x] `test_create_user_returns_409_duplicate_email`: Crear usuario → intentar crear otro con mismo email → verificar status 409 y que el body sigue formato RFC 9457 (`type`, `title`, `status`, `detail`, `instance`)
- [x] **Escribir tests del endpoint `GET /v1/users/{user_id}`** (tests 4-5):
  - [x] `test_get_user_returns_200`: Crear usuario via helper → `GET /v1/users/{id}` → verificar status 200 y campos de `UserResponse`
  - [x] `test_get_user_returns_404_nonexistent`: `GET /v1/users/{uuid_aleatorio}` → verificar status 404 y formato RFC 9457
- [x] **Escribir tests del endpoint `GET /v1/users/{user_id}/detailed`** (tests 6-7):
  - [x] `test_get_user_detailed_returns_200_with_role`: Crear usuario → `GET /v1/users/{id}/detailed` → verificar que el body contiene `user_role` como objeto con `id`, `name`, `description` y `user_ai_profiles` como lista
  - [x] `test_get_user_detailed_returns_404_nonexistent`: UUID inexistente → status 404
- [x] **Escribir tests del endpoint `GET /v1/users/`** (tests 8-10):
  - [x] `test_list_users_returns_200_with_pagination`: Crear 1 usuario → `GET /v1/users/?offset=0&limit=10` → verificar claves `items`, `total`, `limit`, `offset` en el body
  - [x] `test_list_users_returns_200_empty`: Sin crear usuarios → `GET /v1/users/` → verificar `items: []`, `total: 0`
  - [x] `test_list_users_respects_limit`: Crear 3 usuarios → `GET /v1/users/?limit=2` → verificar `len(items) == 2` y `total == 3`
- [x] **Escribir tests del endpoint `PATCH /v1/users/{user_id}`** (tests 11-13):
  - [x] `test_update_user_returns_200`: Crear usuario → `PATCH /v1/users/{id}` con `{"name": "Updated"}` → verificar status 200 y `name == "Updated"`
  - [x] `test_update_user_returns_404_nonexistent`: `PATCH` a UUID inexistente → status 404
  - [x] `test_update_user_returns_409_duplicate_email`: Crear 2 usuarios → intentar actualizar email del segundo al del primero → status 409
- [x] **Escribir tests del endpoint `DELETE /v1/users/{user_id}`** (test 14):
  - [x] `test_delete_user_returns_204`: Crear usuario → `DELETE /v1/users/{id}` → verificar status 204 y body vacío → verificar con `GET` que retorna 404
- [x] **Verificar que todos los tests fallan:** `uv run pytest tests/api/test_user_router.py -v` (fase Red)

---

### ~~Fase 4 — Implementación de `PaginatedResponse` y `PaginationParams`~~ ✅

**Objetivo:** Implementar el esquema de paginación genérico reutilizable antes del Service, ya que el Service depende de `PaginatedResponse`.

**Archivo modificado:** `src/shared/pagination.py`

#### Especificación de `PaginatedResponse[T]`

```python
class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response schema.

    Args:
        items: List of items for the current page.
        total: Total number of items across all pages.
        limit: Maximum number of items per page.
        offset: Number of items skipped from the start.
    """
    items: list[T]
    total: int
    limit: int
    offset: int
```

#### Especificación de `PaginationParams`

```python
class PaginationParams(BaseModel):
    """
    Query parameters for pagination.

    Args:
        offset: Number of items to skip. Defaults to 0.
        limit: Maximum items per page. Defaults to 10, max 100.
    """
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
```

**Checklist:**

- [x] Implementar `PaginatedResponse[T]` como schema Pydantic genérico con `Generic[T]`
  - [x] Campos: `items: list[T]`, `total: int`, `limit: int`, `offset: int`
  - [x] Docstring Google-style con descripción de la clase y cada campo
- [x] Implementar `PaginationParams` como dependencia inyectable
  - [x] Campo `offset: int = Field(default=0, ge=0)` — no puede ser negativo
  - [x] Campo `limit: int = Field(default=10, ge=1, le=100)` — entre 1 y 100
  - [x] Docstring Google-style
- [x] Verificar que los imports funcionan: `from src.shared.pagination import PaginatedResponse, PaginationParams`

---

### Fase 5 — Implementación del Service

**Objetivo:** Implementar la capa de lógica de negocio. Según el skill (sección 7), el Service es la **única capa que ejecuta `commit()` o `rollback()`** y coordina el repositorio.

**Archivo a modificar:** `src/users/users/service.py`

#### Especificación del `UserService`

| Método | Firma | Responsabilidad | Excepciones |
|---|---|---|---|
| `__init__` | `(self, session: AsyncSession, repository: UserRepository) -> None` | Almacena sesión y repositorio inyectados | — |
| `create` | `async (self, user_data: UserCreate) -> User` | 1. Verificar email duplicado via `repository.get_by_email()` → `ConflictException` si existe. 2. `repository.add(user_data)`. 3. `session.commit()`. 4. `session.refresh(user)`. 5. Retornar `user`. | `ConflictException` |
| `get_by_id` | `async (self, user_id: str) -> User` | 1. `repository.get_by_id(user_id)`. 2. Si `None` → `NotFoundException`. 3. Retornar `user`. | `NotFoundException` |
| `get_detailed` | `async (self, user_id: str) -> User` | 1. `repository.get_detailed(user_id)`. 2. Si `None` → `NotFoundException`. 3. Retornar `user` con relaciones cargadas. | `NotFoundException` |
| `get_all` | `async (self, pagination: PaginationParams) -> PaginatedResponse[UserResponse]` | 1. `repository.get_all(pagination.offset, pagination.limit)`. 2. `repository.count()`. 3. Construir y retornar `PaginatedResponse`. | — |
| `update` | `async (self, user_id: str, user_data: UserUpdate) -> User` | 1. `get_by_id(user_id)` → `NotFoundException` si no existe. 2. Si `user_data.email` no es `None` y difiere del actual → `repository.get_by_email()` → `ConflictException` si existe. 3. `repository.update(user, user_data)`. 4. `session.commit()`. 5. `session.refresh(user)`. 6. Retornar `user`. | `NotFoundException`, `ConflictException` |
| `delete` | `async (self, user_id: str) -> None` | 1. `get_by_id(user_id)` → `NotFoundException` si no existe. 2. `repository.delete(user)`. 3. `session.commit()`. | `NotFoundException` |

**Checklist:**

- [ ] Implementar `UserService.__init__` que reciba `session: AsyncSession` y `repository: UserRepository`
  - [ ] Docstring Google-style describiendo la clase y sus dependencias
- [ ] Implementar `UserService.create`:
  - [ ] Verificar email duplicado con `self.repository.get_by_email(user_data.email)`
  - [ ] Si existe → `raise ConflictException(detail=f"User with email '{user_data.email}' already exists")`
  - [ ] Delegar a `self.repository.add(user_data)` (sin commit — eso lo hace el service)
  - [ ] `await self.session.commit()`
  - [ ] `await self.session.refresh(user)` para obtener valores generados por la DB (`id`, `created_at`)
  - [ ] Retornar `user`
- [ ] Implementar `UserService.get_by_id`:
  - [ ] Delegar a `self.repository.get_by_id(user_id)`
  - [ ] Si `None` → `raise NotFoundException(detail=f"User with id '{user_id}' not found")`
  - [ ] Retornar `user`
- [ ] Implementar `UserService.get_detailed`:
  - [ ] Delegar a `self.repository.get_detailed(user_id)`
  - [ ] Si `None` → `raise NotFoundException(detail=f"User with id '{user_id}' not found")`
  - [ ] Retornar `user` (con relaciones ya cargadas por eager loading)
- [ ] Implementar `UserService.get_all`:
  - [ ] Obtener items: `self.repository.get_all(pagination.offset, pagination.limit)`
  - [ ] Obtener total: `self.repository.count()`
  - [ ] Construir `PaginatedResponse(items=items, total=total, limit=pagination.limit, offset=pagination.offset)`
  - [ ] Retornar `PaginatedResponse`
- [ ] Implementar `UserService.update`:
  - [ ] Obtener usuario existente via `self.get_by_id(user_id)` (reutiliza la validación de existencia)
  - [ ] Si `user_data.email` no es `None` y difiere de `user.email` → verificar duplicado con `self.repository.get_by_email(user_data.email)` → `ConflictException` si existe
  - [ ] Delegar a `self.repository.update(user, user_data)`
  - [ ] `await self.session.commit()`
  - [ ] `await self.session.refresh(user)`
  - [ ] Retornar `user`
- [ ] Implementar `UserService.delete`:
  - [ ] Obtener usuario via `self.get_by_id(user_id)`
  - [ ] Delegar a `self.repository.delete(user)`
  - [ ] `await self.session.commit()`
- [ ] Verificar que todos los métodos tienen docstrings Google-style con `Args` y `Returns`/`Raises`

---

### Fase 6 — Implementación de Dependencies + Router + Registro (Green)

**Objetivo:** Conectar la cadena de inyección de dependencias, implementar los endpoints HTTP y registrar el router en `main.py`. Los tests de la Fase 3 deben pasar al completar esta fase.

**Archivos a modificar:**
- `src/users/users/dependencies.py`
- `src/users/users/router.py`
- `src/users/users/__init__.py`
- `src/main.py`

#### 6.1 Dependencies — Cadena de inyección

Siguiendo el patrón del skill (sección 12):

```python
async def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    """
    Provide a UserService instance per request.

    Builds the dependency chain: session → repository → service.

    Args:
        session: Async database session injected by FastAPI.

    Returns:
        UserService: Configured service instance.
    """
    repository = UserRepository(session)
    return UserService(session, repository)
```

#### 6.2 Router — Endpoints HTTP

Siguiendo las reglas del skill (sección 6): cada endpoint usa `response_model`, `status_code` semántico, e inyecta el service con `Depends()`.

| Función | Decorador | Inyección | Delegación |
|---|---|---|---|
| `create_user` | `@router.post("/", response_model=UserResponse, status_code=201)` | `service: UserService = Depends(get_user_service)` | `service.create(user_data)` |
| `list_users` | `@router.get("/", response_model=PaginatedResponse[UserResponse])` | `service + PaginationParams` | `service.get_all(pagination)` |
| `get_user` | `@router.get("/{user_id}", response_model=UserResponse)` | `service` | `service.get_by_id(user_id)` |
| `get_user_detailed` | `@router.get("/{user_id}/detailed", response_model=UserDetailed)` | `service` | `service.get_detailed(user_id)` |
| `update_user` | `@router.patch("/{user_id}", response_model=UserResponse)` | `service` | `service.update(user_id, user_data)` |
| `delete_user` | `@router.delete("/{user_id}", status_code=204)` | `service` | `service.delete(user_id)` |

> [!IMPORTANT]
> **Orden de los endpoints importa.** `GET /{user_id}/detailed` debe definirse **antes** de `GET /{user_id}` para evitar que FastAPI interprete `"detailed"` como un `user_id`. Alternativamente, ambos usan `{user_id}` como path parameter y no hay conflicto porque `/detailed` es un sub-path.

#### 6.3 Registro en `main.py`

```python
from src.users.users.router import router as users_router

app.include_router(
    users_router,
    prefix="/v1/users",
    tags=["users"],
)
```

**Checklist:**

- [ ] **Implementar `dependencies.py`:**
  - [ ] Importar `Depends` de FastAPI, `AsyncSession` de SQLAlchemy, `get_session` de `src.core.dependencies`
  - [ ] Importar `UserRepository` y `UserService` del sub-módulo
  - [ ] Implementar `get_user_service(session = Depends(get_session)) -> UserService` que instancie `UserRepository(session)` y retorne `UserService(session, repository)`
  - [ ] Docstring Google-style con `Args` y `Returns`
- [ ] **Implementar `router.py`:**
  - [ ] Crear instancia `router = APIRouter()`
  - [ ] Importar schemas: `UserCreate`, `UserUpdate`, `UserResponse`, `UserDetailed` de `src.users.schemas`
  - [ ] Importar `PaginatedResponse`, `PaginationParams` de `src.shared.pagination`
  - [ ] Importar `get_user_service` de `dependencies.py`
  - [ ] Implementar `create_user`:
    - [ ] Decorador: `@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)`
    - [ ] Parámetros: `user_data: UserCreate`, `service: UserService = Depends(get_user_service)`
    - [ ] Body: `return await service.create(user_data)`
    - [ ] Docstring Google-style
  - [ ] Implementar `list_users`:
    - [ ] Decorador: `@router.get("/", response_model=PaginatedResponse[UserResponse])`
    - [ ] Parámetros: `pagination: PaginationParams = Depends()`, `service: UserService = Depends(get_user_service)`
    - [ ] Body: `return await service.get_all(pagination)`
    - [ ] Docstring Google-style
  - [ ] Implementar `get_user`:
    - [ ] Decorador: `@router.get("/{user_id}", response_model=UserResponse)`
    - [ ] Parámetros: `user_id: str`, `service: UserService = Depends(get_user_service)`
    - [ ] Body: `return await service.get_by_id(user_id)`
    - [ ] Docstring Google-style
  - [ ] Implementar `get_user_detailed`:
    - [ ] Decorador: `@router.get("/{user_id}/detailed", response_model=UserDetailed)`
    - [ ] Parámetros: `user_id: str`, `service: UserService = Depends(get_user_service)`
    - [ ] Body: `return await service.get_detailed(user_id)`
    - [ ] Docstring Google-style
  - [ ] Implementar `update_user`:
    - [ ] Decorador: `@router.patch("/{user_id}", response_model=UserResponse)`
    - [ ] Parámetros: `user_id: str`, `user_data: UserUpdate`, `service: UserService = Depends(get_user_service)`
    - [ ] Body: `return await service.update(user_id, user_data)`
    - [ ] Docstring Google-style
  - [ ] Implementar `delete_user`:
    - [ ] Decorador: `@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)`
    - [ ] Parámetros: `user_id: str`, `service: UserService = Depends(get_user_service)`
    - [ ] Body: `await service.delete(user_id)`, sin return
    - [ ] Docstring Google-style
- [ ] **Actualizar `__init__.py` del sub-módulo:**
  - [ ] Exportar `router` con alias: `from src.users.users.router import router as users_router`
  - [ ] Definir `__all__ = ["users_router"]`
- [ ] **Registrar router en `main.py`:**
  - [ ] Agregar import: `from src.users.users.router import router as users_router`
  - [ ] Agregar: `app.include_router(users_router, prefix="/v1/users", tags=["users"])`
- [ ] **Ejecutar tests:**
  - [ ] `uv run pytest tests/api/test_user_router.py -v` — los 14 tests de integración deben pasar (fase Green)
  - [ ] `uv run pytest -v` — toda la suite (24 tests) debe pasar

---

### Fase 7 — Validación (QA)

**Objetivo:** Verificar la calidad integral del código, cobertura de tests y coherencia del proyecto.

**Checklist:**

- [ ] **Linting:**
  - [ ] `uv run ruff check src/users/users/ src/shared/pagination.py tests/` — sin errores
  - [ ] `uv run ruff format src/users/users/ src/shared/pagination.py tests/` — código formateado
- [ ] **Análisis estático de tipos:**
  - [ ] `uv run mypy src/users/users/ src/shared/pagination.py` — sin errores
- [ ] **Cobertura de tests:**
  - [ ] `uv run pytest --cov=src/users/users --cov-report=term-missing` — cobertura ≥ 90%
- [ ] **Suite completa:**
  - [ ] `uv run pytest -v` — toda la suite verde
- [ ] **Verificación manual en Swagger:**
  - [ ] Levantar servidor: `uv run uvicorn src.main:app --reload`
  - [ ] Verificar que los 6 endpoints aparecen en `/docs`
  - [ ] Probar `POST /v1/users/` con datos válidos
  - [ ] Probar `GET /v1/users/` con paginación
  - [ ] Probar `GET /v1/users/{id}/detailed`
- [ ] **Actualizar `spec/roadmap.md`:**
  - [ ] Mover el plan 004 de la sección "Siguiente" a "Hecho"

---

## Criterios de Aceptación

1. Los 6 endpoints responden con los status codes correctos (201, 200, 204, 404, 409, 422).
2. `GET /v1/users/` retorna respuesta paginada con `items`, `total`, `limit`, `offset`.
3. `GET /v1/users/{user_id}/detailed` retorna `UserDetailed` con `user_role` y `user_ai_profiles` cargados.
4. Email duplicado retorna `409 Conflict` con formato RFC 9457.
5. Usuario inexistente retorna `404 Not Found` con formato RFC 9457.
6. Todos los tests (24 total: 10 unitarios + 14 integración) pasan con `uv run pytest -v`.
7. Cobertura de `src/users/users/` ≥ 90%.
8. Ruff y Mypy sin errores sobre los archivos modificados/creados.
9. El router está registrado en `main.py` y accesible en Swagger UI.
10. Todos los métodos y clases tienen docstrings Google-style.
11. La cadena de inyección sigue el patrón `get_session → UserRepository → UserService`.
12. El Service es la única capa que ejecuta `commit()`/`rollback()`.

---

## Referencias Técnicas

| Archivo | Propósito |
|---|---|
| `src/users/models.py` | Modelo `User` con FK a `UserRole`, `UserAIProfile` |
| `src/users/schemas.py` | Schemas `UserCreate`, `UserUpdate`, `UserResponse`, `UserDetailed` |
| `src/core/exceptions.py` | `NotFoundException`, `ConflictException`, `ValidationException` |
| `src/core/dependencies.py` | `get_session()` proveedor global de sesión |
| `tests/conftest.py` | Fixtures globales (`db_session`, `async_client`) |
| `tests/crud/conftest.py` | Fixtures `seed_user_role`, `sample_user_data` |
| `src/main.py` | Punto de entrada de la app (sin routers registrados) |
| `src/shared/pagination.py` | Utilidades de paginación (vacío) |
| `.agents/skills/fastapi-app-creator/SKILL.md` | Skill de referencia para la arquitectura |

---

## Resumen de Archivos

| Archivo | Acción | Estado |
|---|---|---|
| `tests/crud/conftest.py` | — | ✅ Ya existe |
| `tests/crud/test_user_repository.py` | — | ✅ Ya existe (10 tests) |
| `src/users/users/repository.py` | — | ✅ Ya implementado |
| `tests/api/conftest.py` | Crear | ✅ Creado |
| `tests/api/test_user_router.py` | Crear | ✅ Creado (14 tests) |
| `src/shared/pagination.py` | Modificar | ✅ Implementado |
| `src/users/users/service.py` | Modificar | ⏳ Pendiente |
| `src/users/users/dependencies.py` | Modificar | ⏳ Pendiente |
| `src/users/users/router.py` | Modificar | ⏳ Pendiente |
| `src/users/users/__init__.py` | Modificar | ⏳ Pendiente |
| `src/main.py` | Modificar | ⏳ Pendiente |
| `spec/roadmap.md` | Modificar | ⏳ Pendiente |
| `src/users/models.py` | Revisar | 📋 Referencia |
| `src/users/schemas.py` | Revisar | 📋 Referencia |
| `src/core/exceptions.py` | Revisar | 📋 Referencia |
| `src/core/dependencies.py` | Revisar | 📋 Referencia |
| `tests/conftest.py` | Revisar | 📋 Referencia |
