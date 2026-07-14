# 004 · CRUD de Usuarios

## Contexto

| Aspecto | Detalle |
|---|---|
| **Resumen** | El sub-módulo `src/users/users/` tiene los archivos scaffolded (`repository.py`, `service.py`, `router.py`, `dependencies.py`) pero están vacíos (solo docstrings). Los modelos (`User`) y schemas (`UserCreate`, `UserUpdate`, `UserResponse`, `UserDetailed`) ya existen en los archivos compartidos del dominio. El `main.py` no registra ningún router de users. No existen tests. El archivo `src/shared/pagination.py` está vacío. |
| **Justificación** | El CRUD de usuarios es la funcionalidad base sobre la que se construirán las demás features del sistema (autenticación, perfiles IA, sesiones de chat). Sin endpoints funcionales, la API no tiene utilidad. |
| **Objetivo** | Implementar el CRUD completo (Create, Read one, Read all con paginación, Read detailed, Update, Delete) para la entidad `User` siguiendo la arquitectura Router → Service → Repository con TDD. Incluye paginación genérica reutilizable. |
| **Riesgo** | Bajo. Es la primera implementación funcional sobre una estructura ya existente. No hay código previo que pueda romperse. |
| **Enfoque** | TDD vertical (red → green) por capas. Primero tests unitarios del repository → implementación del repository → tests de integración del router → implementación del service + dependencies + router → validación QA. |

---

## Seams de Testing (TDD)

> [!IMPORTANT]
> Según la skill TDD, los seams deben acordarse antes de escribir tests. Los seams propuestos son:
> 1. **Repository (seam de datos):** Tests unitarios en `tests/crud/test_user_repository.py` — verifican las queries contra la DB real con rollback transaccional.
> 2. **Router/API (seam HTTP):** Tests de integración en `tests/api/test_user_router.py` — verifican el comportamiento end-to-end a través de `AsyncClient`.
>
> **No se testea la capa Service de forma aislada** porque la skill TDD establece "don't mock your own classes/modules" y el service coordina repository + transacciones. Su comportamiento se verifica indirectamente a través de los tests de integración del router.

---

## Decisiones de Diseño

> [!IMPORTANT]
> **Prefijo de ruta:** El router se registrará como `app.include_router(users_router, prefix="/v1/users", tags=["users"])` siguiendo la convención de versionado de la skill `fastapi-app-creator`.

> [!IMPORTANT]
> **Paginación genérica:** Se implementará un esquema `PaginatedResponse[T]` en `src/shared/pagination.py` con parámetros `offset`/`limit` y metadata (`total`, `limit`, `offset`). Será reutilizable por cualquier dominio.

> [!IMPORTANT]
> **Endpoint detallado separado:** `GET /v1/users/{user_id}/detailed` usará `UserDetailed` con eager loading de `user_role` y `user_ai_profiles`. El `GET /v1/users/{user_id}` estándar retornará `UserResponse` sin relaciones cargadas.

> [!WARNING]
> **Dependencia de `UserRole`:** El modelo `User` tiene un FK obligatorio a `user_role`. Para crear un usuario en tests es necesario que exista al menos un rol en la DB. Se creará una fixture `seed_user_role` que inserte un rol base.

---

## Fases

### Fase 1 — Tests unitarios del Repository (Red)

**Objetivo:** Escribir los tests que definen el contrato del `UserRepository` antes de implementarlo.

**Archivos a crear:**
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
- [ ] Crear `tests/crud/conftest.py` con fixture `seed_user_role` que inserte un `UserRole` base
- [ ] Crear fixture `sample_user_create` que retorne un dict con datos válidos de `UserCreate`
- [ ] Escribir los 10 tests unitarios del repository siguiendo patrón AAA
- [ ] Verificar que todos fallan: `uv run pytest tests/crud/test_user_repository.py -v` (fase Red)

---

### Fase 2 — Implementación del Repository (Green)

**Objetivo:** Implementar `UserRepository` para que los tests de la Fase 1 pasen.

**Archivos a modificar:**
- `src/users/users/repository.py`

Métodos a implementar:

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
- [ ] Implementar clase `UserRepository` con los 9 métodos
- [ ] Usar `selectinload` para eager loading en `get_detailed`
- [ ] Ejecutar `uv run pytest tests/crud/test_user_repository.py -v` — todos deben pasar (fase Green)

---

### Fase 3 — Tests de integración del Router (Red)

**Objetivo:** Escribir los tests de integración que definen el contrato HTTP del CRUD.

**Archivos a crear:**
- `tests/api/conftest.py`
- `tests/api/test_user_router.py`

Tests planificados (14):

**POST `/v1/users/`**

| # | Test | Verifica |
|---|---|---|
| 1 | `test_create_user_returns_201` | Happy path con datos válidos |
| 2 | `test_create_user_returns_422_invalid_email` | Validación Pydantic |
| 3 | `test_create_user_returns_409_duplicate_email` | Email único violado |

**GET `/v1/users/{user_id}`**

| # | Test | Verifica |
|---|---|---|
| 4 | `test_get_user_returns_200` | Happy path |
| 5 | `test_get_user_returns_404_nonexistent` | Not found |

**GET `/v1/users/{user_id}/detailed`**

| # | Test | Verifica |
|---|---|---|
| 6 | `test_get_user_detailed_returns_200_with_role` | Retorna `UserDetailed` con `user_role` |
| 7 | `test_get_user_detailed_returns_404_nonexistent` | Not found |

**GET `/v1/users/?offset=0&limit=10`**

| # | Test | Verifica |
|---|---|---|
| 8 | `test_list_users_returns_200_with_pagination` | Respuesta paginada con `total`, `offset`, `limit`, `items` |
| 9 | `test_list_users_returns_200_empty` | Lista vacía paginada |
| 10 | `test_list_users_respects_limit` | `limit` acota los resultados |

**PATCH `/v1/users/{user_id}`**

| # | Test | Verifica |
|---|---|---|
| 11 | `test_update_user_returns_200` | Happy path |
| 12 | `test_update_user_returns_404_nonexistent` | Not found |
| 13 | `test_update_user_returns_409_duplicate_email` | Email duplicado |

**DELETE `/v1/users/{user_id}`**

| # | Test | Verifica |
|---|---|---|
| 14 | `test_delete_user_returns_204` | Happy path, sin body |

Checklist:
- [ ] Crear `tests/api/conftest.py` con fixture `seed_user_role` para tests de integración
- [ ] Crear helper async `create_test_user` para crear usuarios via POST
- [ ] Escribir los 14 tests de integración siguiendo patrón AAA
- [ ] Verificar que todos fallan: `uv run pytest tests/api/test_user_router.py -v` (fase Red)

---

### Fase 4 — Implementación del Service + Paginación

**Objetivo:** Implementar la lógica de negocio y el esquema de paginación genérico.

**Archivos a modificar:**
- `src/users/users/service.py`
- `src/shared/pagination.py`

#### `src/shared/pagination.py` — Paginación genérica

| Elemento | Descripción |
|---|---|
| `PaginatedResponse[T]` | Schema genérico con `items: list[T]`, `total: int`, `limit: int`, `offset: int` |
| `PaginationParams` | Dependencia FastAPI con `offset: int = 0`, `limit: int = Query(default=10, le=100)` |

#### `src/users/users/service.py` — `UserService`

| Método | Descripción |
|---|---|
| `create` | Verifica email duplicado → `ConflictException`. Delega a `repository.add()`, `commit()` + `refresh()` |
| `get_by_id` | Delega a `repository.get_by_id()`. Si `None` → `NotFoundException` |
| `get_detailed` | Delega a `repository.get_detailed()`. Si `None` → `NotFoundException` |
| `get_all` | Delega a `repository.get_all()` + `repository.count()`. Retorna `PaginatedResponse` |
| `update` | Obtiene usuario o `NotFoundException`. Si cambia email → verifica duplicado. `commit()` + `refresh()` |
| `delete` | Obtiene usuario o `NotFoundException`. Delega a `repository.delete()`, `commit()` |

Checklist:
- [ ] Implementar `PaginatedResponse` y `PaginationParams` en `src/shared/pagination.py`
- [ ] Implementar `UserService` con los 6 métodos
- [ ] Implementar validaciones de negocio (email duplicado → `ConflictException`, no encontrado → `NotFoundException`)

---

### Fase 5 — Implementación de Dependencies + Router (Green)

**Objetivo:** Conectar la cadena de inyección y exponer los endpoints HTTP. Los tests de la Fase 3 deben pasar.

**Archivos a modificar:**
- `src/users/users/dependencies.py`
- `src/users/users/router.py`
- `src/users/users/__init__.py`
- `src/main.py`

#### Endpoints del Router

| Método | Ruta | Status | Response Model | Descripción |
|---|---|---|---|---|
| `POST` | `/` | `201` | `UserResponse` | Crear usuario |
| `GET` | `/` | `200` | `PaginatedResponse[UserResponse]` | Listar con paginación |
| `GET` | `/{user_id}` | `200` | `UserResponse` | Obtener por ID |
| `GET` | `/{user_id}/detailed` | `200` | `UserDetailed` | Obtener con relaciones |
| `PATCH` | `/{user_id}` | `200` | `UserResponse` | Actualizar parcialmente |
| `DELETE` | `/{user_id}` | `204` | `None` | Eliminar |

Checklist:
- [ ] Implementar `get_user_service` en `dependencies.py`
- [ ] Implementar los 6 endpoints en `router.py`
- [ ] Actualizar `__init__.py` del sub-módulo para exportar `router`
- [ ] Registrar router en `main.py` con `prefix="/v1/users"` y `tags=["users"]`
- [ ] Ejecutar `uv run pytest tests/api/test_user_router.py -v` — todos los tests deben pasar (fase Green)
- [ ] Ejecutar `uv run pytest -v` — toda la suite debe pasar

---

### Fase 6 — Validación (QA)

**Objetivo:** Verificar la calidad integral del código, cobertura de tests, y coherencia del proyecto.

Checklist:
- [ ] Ejecutar `uv run ruff check src/users/users/ src/shared/pagination.py tests/` — sin errores de linting
- [ ] Ejecutar `uv run ruff format src/users/users/ src/shared/pagination.py tests/` — código formateado
- [ ] Ejecutar `uv run mypy src/users/users/ src/shared/pagination.py` — sin errores de tipos
- [ ] Ejecutar `uv run pytest --cov=src/users/users --cov-report=term-missing` — cobertura ≥ 90%
- [ ] Ejecutar `uv run pytest -v` — toda la suite verde
- [ ] Verificar endpoints en Swagger UI (`/docs`) levantando `uv run uvicorn src.main:app --reload`
- [ ] Actualizar `spec/roadmap.md` con la entrada del plan 004

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

---

## Referencias Técnicas

| Archivo | Propósito |
|---|---|
| [models.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/models.py) | Modelo `User` con FK a `UserRole`, `UserAIProfile` |
| [schemas.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/schemas.py) | Schemas `UserCreate`, `UserUpdate`, `UserResponse`, `UserDetailed` |
| [exceptions.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/core/exceptions.py) | `NotFoundException`, `ConflictException`, `ValidationException` |
| [dependencies.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/core/dependencies.py) | `get_db()` proveedor global de sesión |
| [conftest.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/tests/conftest.py) | Fixtures globales (`db_session`, `async_client`) |
| [main.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/main.py) | Punto de entrada de la app |
| [pagination.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/shared/pagination.py) | Utilidades de paginación (vacío) |

---

## Resumen de Archivos

| Archivo | Acción |
|---|---|
| `tests/crud/conftest.py` | Crear |
| `tests/crud/test_user_repository.py` | Crear |
| `tests/api/conftest.py` | Crear |
| `tests/api/test_user_router.py` | Crear |
| `src/shared/pagination.py` | Modificar |
| `src/users/users/repository.py` | Modificar |
| `src/users/users/service.py` | Modificar |
| `src/users/users/router.py` | Modificar |
| `src/users/users/dependencies.py` | Modificar |
| `src/users/users/__init__.py` | Modificar |
| `src/main.py` | Modificar |
| `spec/roadmap.md` | Modificar |
| `src/users/models.py` | Revisar |
| `src/users/schemas.py` | Revisar |
| `src/core/exceptions.py` | Revisar |
| `src/core/dependencies.py` | Revisar |
| `tests/conftest.py` | Revisar |
