---
name: fastapi-app-creator
description: >-
  Guía completa para crear, estructurar y desarrollar aplicaciones FastAPI
  con las mejores prácticas del framework. Cubre arquitectura limpia por
  capas, estructura modular de proyecto, esquemas Pydantic V2, inyección
  de dependencias, concurrencia async/sync, base de datos con SQLAlchemy
  asíncrono, testing con pytest, seguridad JWT/RBAC, y despliegue con
  Docker y Gunicorn. Usa esta skill siempre que el usuario quiera crear
  una nueva aplicación FastAPI, estructurar un proyecto existente,
  aplicar patrones de producción, configurar una API REST, o necesite
  orientación sobre cómo organizar routers, servicios, repositorios,
  schemas, modelos o middleware en FastAPI. También aplica cuando se
  mencionen conceptos como "API REST con Python", "backend con FastAPI",
  "microservicio Python", o se necesite scaffolding de proyecto.
---

# FastAPI App Creator

Skill para crear aplicaciones FastAPI robustas y listas para producción,
siguiendo una arquitectura limpia por capas y las mejores prácticas del
ecosistema Python moderno.

## Cuándo leer archivos de referencia

Esta skill incluye archivos especializados en `references/`. Consulta
el archivo relevante según la tarea:

| Archivo | Cuándo leerlo |
|---|---|
| `references/database.md` | Configurar SQLAlchemy async, sesiones, transacciones, Alembic |
| `references/testing.md` | Escribir pruebas con pytest, fixtures async, mocks |
| `references/deployment.md` | Docker, Gunicorn+Uvicorn, señales POSIX, CI/CD |
| `references/security.md` | Autenticación JWT, RBAC, manejo global de excepciones |

Lee solo el archivo que necesites para la tarea actual. No cargues
todos a la vez.

---

## 1. Arquitectura por capas

El diseño separa estrictamente las responsabilidades. El protocolo HTTP
es solo un mecanismo de transporte; la lógica de negocio no debe
depender de él.

### Capas obligatorias

```
Router  →  Service  →  Repository  →  DB/External
  ↑           ↑            ↑
Schema    Schema       Model (ORM)
```

- **Router** (`router.py`): Interfaz HTTP. Sin lógica de negocio.
  Recibe la solicitud, valida con schemas Pydantic, delega al servicio
  y devuelve la respuesta con el `response_model` adecuado.

- **Service** (`service.py`): Reglas de dominio. Coordina
  transacciones, orquesta repositorios y aplica la lógica de negocio.
  Es la única capa que ejecuta `commit()` o `rollback()`.

- **Repository** (`repository.py`): Acceso a datos. Encapsula las
  consultas a la base de datos. No confirma ni revierte transacciones.

- **Schema** (`schemas.py`): Validación Pydantic V2. Contratos de
  entrada/salida de la API.

- **Model** (`models.py`): Modelos SQLAlchemy. Representación de las
  tablas en la base de datos.

### Regla fundamental de transacciones

La confirmación (`commit`) o reversión (`rollback`) de una transacción
jamás debe ocurrir en los repositorios ni en los routers. Este control
pertenece exclusivamente a la Capa de Servicios. Esto previene fugas
de conexión y garantiza atomicidad.

---

## 2. Estructura de proyecto

Organización modular por dominio funcional (no por tipo de archivo).
Cada módulo de negocio agrupa todo lo necesario para su funcionalidad.

```
proyecto/
├── alembic/                   # Migraciones de base de datos
│   ├── versions/
│   └── env.py
├── src/
│   ├── __init__.py
│   ├── main.py                # Punto de entrada de la aplicación
│   ├── core/                  # Configuración transversal
│   │   ├── __init__.py
│   │   ├── config.py          # Settings con pydantic-settings
│   │   ├── database.py        # Engine, SessionLocal, Base
│   │   ├── dependencies.py    # Dependencias globales (get_db)
│   │   ├── exceptions.py      # Excepciones y handlers globales
│   │   └── security.py        # JWT, hashing, OAuth2
│   ├── users/                 # Módulo de dominio
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   └── dependencies.py    # Dependencias específicas
│   ├── items/                 # Otro módulo de dominio
│   │   ├── ...
│   └── shared/                # Utilidades compartidas
│       ├── __init__.py
│       └── pagination.py
├── tests/
│   ├── conftest.py            # Fixtures globales
│   ├── test_users/
│   │   ├── test_router.py
│   │   └── test_service.py
│   └── test_items/
├── .env
├── .env.example
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

### Reglas de estructura

1. Cada módulo de dominio contiene sus propios `router.py`,
   `service.py`, `repository.py`, `schemas.py` y `models.py`.
2. El directorio `core/` agrupa la configuración transversal:
   settings, base de datos, seguridad, excepciones globales.
3. El directorio `tests/` replica la estructura de `src/`.
4. La anidación de rutas se limita a un nivel máximo.

---

## 3. Configuración con pydantic-settings

Centraliza todas las variables de entorno en una clase tipada que se
valida al inicio de la aplicación.

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración central de la aplicación.

    Carga las variables de entorno desde el archivo .env
    y las valida con tipado estricto.
    """

    app_name: str = "FastAPI App"
    debug: bool = False
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
```

---

## 4. Punto de entrada (main.py)

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.users.router import router as users_router
from src.items.router import router as items_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.

    Ejecuta la lógica de inicio y cierre de recursos.
    """
    # Inicio: inicializar recursos
    yield
    # Cierre: liberar recursos


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(
    users_router,
    prefix="/v1/users",
    tags=["users"],
)
app.include_router(
    items_router,
    prefix="/v1/items",
    tags=["items"],
)
```

### Reglas del punto de entrada

- Versionado de API desde el día uno (`/v1/`).
- Rutas con sustantivos en plural, nunca verbos.
- Usar `lifespan` en lugar de los eventos `on_startup`/`on_shutdown`
  deprecados.
- Registrar los manejadores de excepciones globales.

---

## 5. Esquemas Pydantic V2

Arquitectura simplificada de 3 fases: **Create**, **Update**,
**Response**, se puede colocar una cuarta fase de **Detailed** si es necesario para mostrar información adicional. Response hereda de Create para minimizar la duplicación.

```python
from pydantic import BaseModel, ConfigDict, field_validator


class UserCreate(BaseModel):
    """
    Esquema para la creación de un usuario.

    Args:
        name (str): Nombre del usuario.
        email (str): Correo electrónico del usuario.
    """

    name: str
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """
        Valida que el correo contenga arroba.

        Args:
            value (str): Valor del correo a validar.

        Returns:
            str: Correo validado en minúsculas.
        """
        if "@" not in value:
            raise ValueError("El correo debe contener @")
        return value.lower()


class UserUpdate(BaseModel):
    """
    Esquema para la actualización parcial de un usuario.

    Args:
        name (str | None): Nombre actualizado.
        email (str | None): Correo actualizado.
    """

    name: str | None = None
    email: str | None = None


class UserResponse(UserCreate):
    """
    Esquema de respuesta para un usuario.

    Args:
        id (int): Identificador único del usuario.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)

class UserDetailed(UserResponse):
    """
    Esquema de respuesta detallada para un usuario.

    Args:
        user_rol (UserRolResponse): Rol del usuario.
        user_perfiles_ia (list[UserPerfilIADetailed]): Perfiles de IA del usuario.
    """

    user_rol: UserRolResponse
    user_perfiles_ia: list[UserPerfilIADetailed] = []
```

### Reglas de Pydantic V2

| Pydantic V1 | Pydantic V2 |
|---|---|
| Subclase `Config` | `model_config = ConfigDict(...)` |
| `.parse_obj()` | `.model_validate()` |
| `.dict()` / `.json()` | `.model_dump()` / `.model_dump_json()` |
| `orm_mode = True` | `from_attributes = True` |
| `@validator` | `@field_validator` + `@classmethod` |

**Prohibición crítica:** No realizar consultas asíncronas ni
verificaciones contra la base de datos dentro de los validadores
Pydantic, ya que estos desconocen el contexto transaccional.

---

## 6. Routers

Los routers son la interfaz HTTP. Deben ser ligeros: recibir,
validar, delegar y responder.

```python
from fastapi import APIRouter, Depends, status

from src.users.schemas import (
    SchemaUserCreate,
    SchemaUserResponse,
)
from src.users.service import UserService
from src.users.dependencies import get_user_service


router = APIRouter()


@router.post(
    "/",
    response_model=SchemaUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: SchemaUserCreate,
    service: UserService = Depends(get_user_service),
) -> SchemaUserResponse:
    """
    Crea un nuevo usuario.

    Args:
        user_data (SchemaUserCreate): Datos del usuario.
        service (UserService): Servicio de usuarios inyectado.

    Returns:
        SchemaUserResponse: Usuario creado.
    """
    return await service.create(user_data)
```

### Reglas de los routers

- Usar `response_model` en cada endpoint por seguridad.
- Aplicar los verbos HTTP correctamente (GET, POST, PUT, PATCH,
  DELETE).
- Usar códigos de estado HTTP semánticos (201 Created, 204 No Content,
  etc.).
- Inyectar dependencias con `Depends()`.
- No incluir lógica de negocio: delegar todo al servicio.

---

## 7. Servicios

La capa de servicios contiene las reglas de dominio y es la única
responsable de gestionar las transacciones.

```python
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.repository import UserRepository
from src.users.schemas import SchemaUserCreate


class UserService:
    """
    Servicio de gestión de usuarios.

    Coordina la lógica de negocio y las transacciones.

    Args:
        session (AsyncSession): Sesión de base de datos.
        repository (UserRepository): Repositorio de usuarios.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: UserRepository,
    ) -> None:
        self.session = session
        self.repository = repository

    async def create(
        self,
        user_data: SchemaUserCreate,
    ) -> "User":
        """
        Crea un usuario y confirma la transacción.

        Args:
            user_data (SchemaUserCreate): Datos del usuario.

        Returns:
            User: Instancia del usuario creado.
        """
        user = await self.repository.add(user_data)
        await self.session.commit()
        await self.session.refresh(user)
        return user
```

---

## 8. Repositorios

Encapsulan el acceso a datos. No gestionan transacciones.

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.users.schemas import SchemaUserCreate


class UserRepository:
    """
    Repositorio de acceso a datos para usuarios.

    Args:
        session (AsyncSession): Sesión de base de datos.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(
        self,
        user_data: SchemaUserCreate,
    ) -> User:
        """
        Agrega un nuevo usuario a la sesión.

        Args:
            user_data (SchemaUserCreate): Datos del usuario.

        Returns:
            User: Instancia del modelo ORM creada.
        """
        user = User(**user_data.model_dump())
        self.session.add(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Obtiene un usuario por su identificador.

        Args:
            user_id (int): ID del usuario.

        Returns:
            User | None: Usuario encontrado o None.
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

---

## 9. Concurrencia async/sync

La correcta gestión de concurrencia es el eje del rendimiento.

- **`async def`**: Para operaciones I/O no bloqueantes (consultas DB
  async, llamadas HTTP con httpx, etc.). Todas las operaciones
  internas deben usar `await`.

- **`def` (sync)**: Para SDKs síncronos heredados o librerías
  bloqueantes. FastAPI delega estas funciones a un threadpool
  secundario automáticamente.

**Regla crítica:** No ejecutar código bloqueante (CPU intensivo,
`time.sleep()`, SDKs sync) dentro de funciones `async def`. Esto
paraliza el bucle de eventos y bloquea todas las conexiones entrantes.

### Background Tasks

Las tareas en segundo plano (`BackgroundTasks`) son solo para
operaciones livianas (< 1 segundo). Para procesamientos pesados,
largos o que requieran reintentos, migrar hacia colas dedicadas como
Celery, Arq o RQ.

---

## 10. Middleware ASGI puro

Evitar `BaseHTTPMiddleware` en entornos de alta concurrencia, ya que
corrompe las variables de contexto, cancela tareas en segundo plano
inesperadamente y encubre errores del bucle de eventos. En su lugar,
construir middleware mediante la interfaz ASGI pura.

```python
from starlette.types import ASGIApp, Receive, Scope, Send


class CorrelationIdMiddleware:
    """
    Middleware ASGI para inyectar un Correlation ID.

    Genera un identificador único por solicitud para
    trazabilidad distribuida.

    Args:
        app (ASGIApp): Aplicación ASGI siguiente.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """
        Procesa la solicitud inyectando el correlation ID.

        Args:
            scope (Scope): Alcance ASGI de la solicitud.
            receive (Receive): Canal de recepción.
            send (Send): Canal de envío.
        """
        if scope["type"] == "http":
            import uuid
            from contextvars import ContextVar

            correlation_id: ContextVar[str] = ContextVar(
                "correlation_id"
            )
            token = correlation_id.set(str(uuid.uuid4()))
            try:
                await self.app(scope, receive, send)
            finally:
                correlation_id.reset(token)
        else:
            await self.app(scope, receive, send)
```

---

## 11. Manejo global de excepciones (RFC 7807)

Centralizar las excepciones con `@app.exception_handler()` emitiendo
JSON normalizado según RFC 7807 (Problem Details).

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """
    Excepción base de la aplicación.

    Args:
        detail (str): Mensaje descriptivo del error.
        status_code (int): Código HTTP del error.
    """

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.detail = detail
        self.status_code = status_code


class NotFoundException(AppException):
    """Excepción para recursos no encontrados."""

    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra los manejadores de excepciones globales.

    Args:
        app (FastAPI): Instancia de la aplicación FastAPI.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """
        Maneja las excepciones de la aplicación.

        Args:
            request (Request): Solicitud HTTP entrante.
            exc (AppException): Excepción capturada.

        Returns:
            JSONResponse: Respuesta JSON con Problem Details.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "about:blank",
                "title": type(exc).__name__,
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url),
            },
        )
```

---

## 12. Dependencias e inyección

El sistema de dependencias de FastAPI es el esqueleto del acoplamiento
flexible. Cada recurso costoso (sesión de BD, servicio, repositorio)
se inyecta con `Depends()`.

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory
from src.users.repository import UserRepository
from src.users.service import UserService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Proveedor de sesiones de base de datos.

    Yields:
        AsyncSession: Sesión asíncrona de SQLAlchemy.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_service(
    session: AsyncSession = Depends(get_db),
) -> UserService:
    """
    Proveedor del servicio de usuarios.

    Args:
        session (AsyncSession): Sesión de base de datos.

    Returns:
        UserService: Instancia configurada del servicio.
    """
    repository = UserRepository(session)
    return UserService(session, repository)
```

### Comportamiento del caché

FastAPI invoca las dependencias una sola vez por solicitud y almacena
el resultado. Para desactivar este caché:
`Depends(get_db, use_cache=False)`.
