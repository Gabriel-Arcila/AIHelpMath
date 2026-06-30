# Reestructuración del Proyecto IAHelpMath

## Contexto

El proyecto IAHelpMath presenta desviaciones significativas respecto a la arquitectura definida en las skills `fastapi-app-creator` y `python-best-practices`. Se identificaron **18 problemas** (5 críticos, 7 graves, 4 moderados, 2 menores) que requieren una reestructuración completa.

### Decisiones de diseño confirmadas

| Decisión | Elección |
|----------|----------|
| ORM | SQLModel (mantener, migrar a sesiones async) |
| Naming de schemas | Sin prefijo `Schema` → `UserCreate`, `UserResponse`, etc. |
| Line-length | 88 caracteres (convención Ruff/Black) |

### Diagnóstico resumido

| Severidad | Cantidad | Ejemplos clave |
|-----------|----------|----------------|
| 🔴 Crítico | 5 | Directorio `app/` en vez de `src/`, organización por tipo, sesión BD síncrona, sin `lifespan`, sin exception handlers |
| 🟠 Grave | 7 | Settings en UPPER_CASE, falta de docstrings, instancia global en servicios, sin inyección de dependencias |
| 🟡 Moderado | 4 | Falta `core/__init__.py`, `db/` separado de `core/`, tests síncronos, Ruff incompleto |
| 🔵 Menor | 2 | `.env` con credenciales en repo, `docker-compose.yml` con `version` obsoleto |

---

## Fase 1: Migración Estructural (`app/` → `src/`, módulos de dominio)

**Objetivo:** Transformar la organización de "por tipo de archivo" a "por dominio funcional" y renombrar el directorio raíz de `app/` a `src/`.

### Estructura objetivo

```
src/
├── __init__.py
├── main.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── exceptions.py
│   └── security.py
├── users/
│   ├── __init__.py
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   ├── schemas.py
│   ├── models.py
│   └── dependencies.py
├── ai_tutor/
│   ├── __init__.py
│   ├── router.py
│   ├── service.py
│   ├── schemas.py
│   └── dependencies.py
└── shared/
    ├── __init__.py
    └── pagination.py
```

### Checklist

- [x] Crear directorio `src/` con `__init__.py`
- [x] Crear directorio `src/core/` con `__init__.py`
- [x] Migrar `app/core/config.py` → `src/core/config.py` (sin cambios de contenido aún)
- [x] Migrar `app/core/security.py` → `src/core/security.py`
- [x] Crear directorio `src/users/` con `__init__.py`
- [x] Migrar `app/models/user.py` → `src/users/models.py`
- [x] Migrar `app/schemas/user.py` → `src/users/schemas.py`
- [x] Crear `src/users/router.py` (esqueleto con `APIRouter()`)
- [x] Crear `src/users/service.py` (esqueleto de clase `UserService`)
- [x] Crear `src/users/repository.py` (esqueleto de clase `UserRepository`)
- [x] Crear `src/users/dependencies.py` (función `get_user_service`)
- [x] Crear directorio `src/ai_tutor/` con `__init__.py`
- [x] Migrar `app/services/ai_tutor.py` → `src/ai_tutor/service.py`
- [x] Crear `src/ai_tutor/router.py` (esqueleto con `APIRouter()`)
- [x] Crear `src/ai_tutor/schemas.py` (esqueleto vacío)
- [x] Crear `src/ai_tutor/dependencies.py` (función `get_ai_tutor_service`)
- [x] Crear directorio `src/shared/` con `__init__.py`
- [x] Crear `src/shared/pagination.py` (esqueleto vacío)
- [x] Migrar `app/main.py` → `src/main.py` (actualizar todas las importaciones `app.` → `src.`)
- [x] Actualizar todas las importaciones internas en los archivos migrados
- [x] Eliminar directorio `app/` completo
- [x] Verificar que Python resuelve `from src.main import app` sin errores

---

## Fase 2: Sesión de BD Asíncrona + Inyección de Dependencias

**Objetivo:** Reemplazar la sesión síncrona de SQLModel por `AsyncSession` de SQLAlchemy, crear el proveedor `get_db()` global, y cablear la inyección de dependencias por módulo.

### Checklist

- [x] Crear `src/core/database.py` con:
  - [x] `create_async_engine()` usando URL `postgresql+asyncpg://`
  - [x] `async_sessionmaker` como `async_session_factory`
  - [x] Importación de `SQLModel.metadata` para Alembic
- [x] Crear `src/core/dependencies.py` con:
  - [x] Función `get_db()` como `AsyncGenerator[AsyncSession, None]`
  - [x] Uso de `async with async_session_factory() as session` + `yield`
- [x] Implementar `src/users/repository.py` con:
  - [x] Clase `UserRepository` que recibe `AsyncSession` en `__init__`
  - [x] Métodos `add()`, `get_by_id()`, `get_all()`, `update()`, `delete()`
  - [x] Sin `commit()` ni `rollback()` (responsabilidad del servicio)
- [x] Implementar `src/users/service.py` con:
  - [x] Clase `UserService` que recibe `AsyncSession` + `UserRepository`
  - [x] Métodos con `await self.session.commit()` / `refresh()` / `rollback()`
- [x] Implementar `src/users/dependencies.py` con:
  - [x] `get_user_service(session = Depends(get_db))` → instancia `UserService`
- [x] Actualizar `src/ai_tutor/service.py`:
  - [x] Renombrar `AitutorService` → `AiTutorService`
  - [x] Eliminar instancia global `ai_tutor_service`
  - [x] Refactorizar para recibir dependencias via `__init__`
- [x] Implementar `src/ai_tutor/dependencies.py`:
  - [x] `get_ai_tutor_service()` → instancia `AiTutorService`
- [x] Eliminar `app/db/session.py` y `app/db/base.py` (ya reemplazados)
- [x] Actualizar `migrations/env.py`:
  - [x] Cambiar `from app.core.config import settings` → `from src.core.config import settings`
  - [x] Cambiar `import app.models` → `import src.users.models`
- [x] Verificar que `alembic check` pasa sin errores

---

## Fase 3: Punto de Entrada (`main.py`) + Excepciones Globales

**Objetivo:** Implementar el ciclo de vida con `lifespan`, registrar manejadores de excepciones globales RFC 7807, e integrar los routers de dominio.

### Checklist

- [x] Crear `src/core/exceptions.py` con:
  - [x] Clase base `AppException(Exception)` con atributos `detail: str` y `status_code: int`
  - [x] `NotFoundException(AppException)` → HTTP 404
  - [x] `ConflictException(AppException)` → HTTP 409
  - [x] `ValidationException(AppException)` → HTTP 422
  - [x] Función `register_exception_handlers(app: FastAPI) -> None`
  - [x] Handler que emite JSON normalizado RFC 7807 (campos: `type`, `title`, `status`, `detail`, `instance`)
- [x] Refactorizar `src/main.py` con:
  - [x] `@asynccontextmanager` + `async def lifespan(app: FastAPI)`
  - [x] Instancia `FastAPI(title=..., lifespan=lifespan)`
  - [x] Llamada a `register_exception_handlers(app)`
  - [x] `app.include_router(users_router, prefix="/v1/users", tags=["users"])`
  - [x] `app.include_router(ai_tutor_router, prefix="/v1/ai-tutor", tags=["ai_tutor"])`
  - [x] Eliminar ruta `"/"` inline (mover a un health check router si se desea)
- [x] Implementar `src/users/router.py` con:
  - [x] Endpoints CRUD: `POST /`, `GET /`, `GET /{user_id}`, `PATCH /{user_id}`, `DELETE /{user_id}`
  - [x] `response_model` en cada endpoint
  - [x] Códigos HTTP semánticos (`201 Created`, `204 No Content`)
  - [x] Inyección de `UserService` via `Depends(get_user_service)`
- [x] Implementar `src/ai_tutor/router.py` con:
  - [x] Endpoint `POST /explain` (esqueleto funcional)
  - [x] Inyección de `AiTutorService` via `Depends(get_ai_tutor_service)`
- [x] Verificar que `uvicorn src.main:app` inicia sin errores
- [x] Verificar que `/docs` (Swagger UI) carga y muestra los endpoints

---

## Fase 4: Correcciones PEP 8 / PEP 257 / PEP 484

**Objetivo:** Aplicar docstrings, type hints y convenciones de naming a todos los archivos del proyecto.

### Checklist

#### `src/core/config.py`
- [x] Renombrar atributos a `snake_case`: `PROJECT_NAME` → `project_name`, `PROJECT_VERSION` → `project_version`, `DATABASE_URL` → `database_url`, `API_V1_STR` → `api_v1_str`
- [x] Agregar `case_sensitive=False` en `model_config` para que siga leyendo variables de entorno en UPPER_CASE
- [x] Agregar docstring completo a la clase `Settings` (formato Args)
- [x] Actualizar todas las referencias en `src/main.py` y demás archivos

#### `src/core/security.py`
- [x] Agregar docstring al módulo
- [x] Agregar type hints: `def get_current_user() -> None:`
- [x] Agregar docstring a la función
- [x] Marcar como placeholder explícito con `# TODO:` documentado

#### `src/users/models.py`
- [x] Verificar que todos los docstrings siguen el formato Args/Returns (ya existentes ✅)
- [x] Verificar type hints en todos los atributos (ya existentes ✅)

#### `src/users/schemas.py`
- [x] Agregar docstring a `UserNivelCreate`
- [x] Agregar docstring a `UserNivelUpdate`
- [x] Agregar docstring a `UserNivelResponse`
- [x] Agregar docstring a `UserTemaInteresCreate`
- [x] Agregar docstring a `UserTemaInteresUpdate`
- [x] Agregar docstring a `UserTemaInteresResponse`
- [x] Agregar docstring a `UserPerfilIACreate`
- [x] Agregar docstring a `UserPerfilIAUpdate`
- [x] Agregar docstring a `UserPerfilIAResponse`
- [x] Agregar docstring a `UserCreate`
- [x] Agregar docstring a `UserUpdate`
- [x] Agregar docstring a `UserResponse`

#### `src/ai_tutor/service.py`
- [x] Agregar docstring a la clase `AiTutorService`
- [x] Agregar docstring al método `explain_problem()`
- [x] Agregar type hints completos a `__init__`

#### `src/main.py`
- [x] Agregar docstring al módulo
- [x] Agregar docstring a `lifespan()`
- [x] Agregar type hints a toda función o endpoint
- [x] Verificar que no hay funciones sin anotación de retorno

#### Archivos nuevos (Fase 1-3)
- [x] Verificar que todos los archivos creados en fases anteriores ya incluyen docstrings y type hints

---

## Fase 5: Configuración de Herramientas + Tests + DevOps

**Objetivo:** Actualizar configuración de linters, tests, Docker y archivos de entorno.

### Checklist

#### `pyproject.toml`
- [x] Mantener `line-length = 88`
- [x] Expandir `select` de Ruff: agregar `"D"` (pydocstyle), `"N"` (pep8-naming), `"UP"` (pyupgrade), `"ANN"` (flake8-annotations), `"B"` (bugbear)
- [x] Agregar `[tool.ruff.lint.pydocstyle]` con `convention = "google"`
- [x] Agregar `[tool.ruff.lint.per-file-ignores]` para excluir `ANN` en tests
- [x] Agregar sección `[tool.mypy]` con configuración estricta (`strict = true`, `plugins = ["pydantic.mypy"]`)

#### `tests/conftest.py`
- [x] Reemplazar `from typing import Generator` → `from collections.abc import AsyncGenerator`
- [x] Reemplazar `TestClient` síncrono → `httpx.AsyncClient`
- [x] Crear fixture `async_client` con `async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac`
- [x] Agregar fixture `db_session` para sesiones de test
- [x] Agregar docstrings a todos los fixtures
- [x] Actualizar import de `app.main` → `src.main`

#### Archivos DevOps
- [x] Actualizar `Dockerfile`:
  - [x] Cambiar `CMD` de `app.main:app` → `src.main:app`
- [x] Actualizar `docker-compose.yml`:
  - [x] Eliminar clave `version: "3.8"` (obsoleta en Docker Compose V2)
  - [x] Actualizar `command:` con `src.main:app`
  - [x] Cambiar `DATABASE_URL` a usar prefijo `postgresql+asyncpg://`
- [x] Actualizar `migrations/env.py` (si no se hizo en Fase 2):
  - [x] Verificar que todos los imports usan `src.`

#### Archivos de entorno
- [x] Crear `.env.example` con variables requeridas (sin credenciales reales)
- [x] Verificar que `.gitignore` incluye `.env` (ya lo incluye ✅)

---

## Fase 6: Validación Integral (QA)

**Objetivo:** Verificar que todos los cambios funcionan correctamente, que el proyecto pasa linting, type checking, y tests.

### Checklist

#### Resolución de importaciones
- [x] Ejecutar `python -c "from src.main import app; print('OK')"` sin errores
- [x] Ejecutar `python -c "from src.core.database import async_session_factory; print('OK')"` sin errores
- [x] Ejecutar `python -c "from src.users.models import User; print('OK')"` sin errores

#### Linting y tipado
- [x] Ejecutar `ruff check src/ tests/` → 0 errores
- [x] Ejecutar `ruff format --check src/ tests/` → 0 diferencias
- [x] Ejecutar `mypy src/` → 0 errores (o solo warnings aceptados)

#### Migraciones
- [x] Ejecutar `alembic check` → sin migraciones pendientes
- [x] Verificar que `alembic revision --autogenerate -m "test"` detecta los modelos correctamente

#### Ejecución del servidor
- [x] Ejecutar `uvicorn src.main:app --reload` → inicia sin errores
- [x] Verificar que `http://localhost:8000/docs` carga Swagger UI
- [x] Verificar que los endpoints `/v1/users` y `/v1/ai-tutor` aparecen en la documentación

#### Tests
- [x] Ejecutar `pytest tests/ -v` → todos pasan
- [x] Verificar que los fixtures async funcionan correctamente

#### Docker
- [x] Ejecutar `docker-compose build` → build exitoso
- [x] Ejecutar `docker-compose up` → servicio inicia y responde

#### Limpieza
- [x] Verificar que no existe el directorio `app/` (eliminado)
- [x] Verificar que no quedan imports con prefijo `app.` en ningún archivo de `src/` o `tests/`
- [x] Verificar que no quedan archivos `__pycache__` huérfanos


---

## Criterios de Aceptación

| # | Criterio | Validación |
|---|----------|------------|
| 1 | El directorio raíz del código fuente es `src/`, no `app/` | `ls src/` lista los módulos |
| 2 | La estructura es modular por dominio: `src/users/`, `src/ai_tutor/`, `src/core/`, `src/shared/` | Cada módulo contiene sus propios `router.py`, `service.py`, `repository.py`, `schemas.py`, `models.py` |
| 3 | La sesión de BD es asíncrona con `AsyncSession` + `asyncpg` | `src/core/database.py` usa `create_async_engine` y `async_sessionmaker` |
| 4 | Las dependencias se inyectan con `Depends()` | No existen instancias globales de servicios; todo se inyecta via funciones en `dependencies.py` |
| 5 | `main.py` usa `lifespan` y registra exception handlers | `FastAPI(lifespan=lifespan)` + `register_exception_handlers(app)` |
| 6 | Las excepciones siguen RFC 7807 (Problem Details) | El response JSON contiene `type`, `title`, `status`, `detail`, `instance` |
| 7 | Todos los archivos públicos tienen docstrings PEP 257 | `ruff check --select D` no reporta errores |
| 8 | Todos los atributos de `Settings` usan `snake_case` | `settings.project_name`, `settings.database_url`, etc. |
| 9 | `ruff check src/ tests/` reporta 0 errores | Linting limpio con reglas expandidas |
| 10 | `pytest tests/ -v` pasa sin fallos | Fixture async con `httpx.AsyncClient` funcional |
| 11 | `docker-compose up --build` construye y ejecuta sin errores | El servicio responde en `localhost:8000` |
| 12 | No quedan importaciones con prefijo `app.` | `grep -r "from app\." src/ tests/ migrations/` retorna vacío |

---

## Referencias Técnicas

| Archivo / Recurso | Propósito | Ubicación |
|-------------------|-----------|-----------|
| Skill `fastapi-app-creator` | Arquitectura por capas, estructura de proyecto, sesiones async, routers, servicios, repositorios, excepciones, dependencias | [SKILL.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/SKILL.md) |
| Skill `python-best-practices` | PEP 8, PEP 20, PEP 257, PEP 484, convenciones de naming, type hints | [SKILL.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/python-best-practices/SKILL.md) |
| Referencia `database.md` | SQLAlchemy async, sesiones, transacciones, Alembic | [database.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/database.md) |
| Referencia `testing.md` | Fixtures async, mocks, AsyncClient | [testing.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/testing.md) |
| Referencia `deployment.md` | Docker, Gunicorn+Uvicorn, CI/CD | [deployment.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/deployment.md) |
| Modelos actuales | Modelos ORM de User, UserRol, UserNivel, UserPerfilIA, UserTemaInteres | [user.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/app/models/user.py) |
| Schemas actuales | Schemas Pydantic de User y entidades relacionadas | [user.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/app/schemas/user.py) |
| Configuración actual | Settings con pydantic-settings | [config.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/app/core/config.py) |
| Sesión BD actual | Sesión síncrona con SQLModel | [session.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/app/db/session.py) |
| Migraciones | Alembic async con env.py configurado | [env.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/migrations/env.py) |

---

## Resumen de Archivos

| Acción | Archivo | Descripción |
|--------|---------|-------------|
| 🆕 Crear | `src/__init__.py` | Módulo raíz del código fuente |
| 🆕 Crear | `src/main.py` | Punto de entrada con `lifespan` + exception handlers + routers |
| 🆕 Crear | `src/core/__init__.py` | Init del módulo de configuración transversal |
| 🆕 Crear | `src/core/config.py` | `Settings` con `snake_case`, docstrings, `case_sensitive=False` |
| 🆕 Crear | `src/core/database.py` | `create_async_engine` + `async_sessionmaker` + metadata |
| 🆕 Crear | `src/core/dependencies.py` | `get_db()` global como `AsyncGenerator[AsyncSession, None]` |
| 🆕 Crear | `src/core/exceptions.py` | `AppException`, subclases, handlers RFC 7807 |
| 🆕 Crear | `src/core/security.py` | Placeholder con docstrings y type hints |
| 🆕 Crear | `src/users/__init__.py` | Init del módulo de dominio users |
| 🆕 Crear | `src/users/models.py` | Modelos ORM migrados de `app/models/user.py` |
| 🆕 Crear | `src/users/schemas.py` | Schemas Pydantic migrados con docstrings completos |
| 🆕 Crear | `src/users/router.py` | Endpoints CRUD con `response_model` y códigos HTTP |
| 🆕 Crear | `src/users/service.py` | `UserService` con gestión de transacciones |
| 🆕 Crear | `src/users/repository.py` | `UserRepository` con acceso a datos (sin commit) |
| 🆕 Crear | `src/users/dependencies.py` | `get_user_service()` con inyección |
| 🆕 Crear | `src/ai_tutor/__init__.py` | Init del módulo de dominio ai_tutor |
| 🆕 Crear | `src/ai_tutor/service.py` | `AiTutorService` refactorizado con docstrings |
| 🆕 Crear | `src/ai_tutor/router.py` | Endpoint `POST /explain` |
| 🆕 Crear | `src/ai_tutor/schemas.py` | Schemas de entrada/salida para ai_tutor |
| 🆕 Crear | `src/ai_tutor/dependencies.py` | `get_ai_tutor_service()` con inyección |
| 🆕 Crear | `src/shared/__init__.py` | Init del módulo de utilidades compartidas |
| 🆕 Crear | `src/shared/pagination.py` | Utilidades de paginación (esqueleto) |
| 🆕 Crear | `.env.example` | Plantilla de variables de entorno sin credenciales |
| ✏️ Modificar | `Dockerfile` | Actualizar path `app.main:app` → `src.main:app` |
| ✏️ Modificar | `docker-compose.yml` | Remover `version`, actualizar command y `DATABASE_URL` |
| ✏️ Modificar | `migrations/env.py` | Actualizar imports `app.` → `src.` |
| ✏️ Modificar | `pyproject.toml` | Expandir Ruff (`D`, `N`, `UP`, `ANN`, `B`), agregar `[tool.mypy]` |
| ✏️ Modificar | `tests/conftest.py` | Migrar a `httpx.AsyncClient`, docstrings, imports |
| 🗑️ Eliminar | `app/` | Directorio completo reemplazado por `src/` |
| 🔍 Revisar | `alembic.ini` | Verificar que `script_location` sigue apuntando a `migrations` |
| 🔍 Revisar | `.gitignore` | Verificar que `.env` está incluido |
| 🔍 Revisar | `README.md` | Actualizar estructura documentada (post-implementación) |
