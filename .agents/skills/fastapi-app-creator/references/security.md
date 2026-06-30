# Seguridad: JWT, OAuth2, RBAC y Protección

Referencia especializada para la implementación de autenticación,
autorización y protección en aplicaciones FastAPI.

## Tabla de contenidos

1. [Autenticación JWT con OAuth2](#1-autenticación-jwt-con-oauth2)
2. [Hashing de contraseñas](#2-hashing-de-contraseñas)
3. [Control de acceso basado en roles (RBAC)](#3-control-de-acceso-basado-en-roles-rbac)
4. [Dependencias de seguridad](#4-dependencias-de-seguridad)
5. [Manejo global de excepciones](#5-manejo-global-de-excepciones)
6. [CORS y headers de seguridad](#6-cors-y-headers-de-seguridad)

---

## 1. Autenticación JWT con OAuth2

Implementación de tokens JWT sin estado (stateless) con el esquema
OAuth2 Bearer de FastAPI.

### core/security.py

```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.core.exceptions import UnauthorizedException


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/auth/login",
)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Crea un token de acceso JWT.

    Args:
        data (dict): Datos a codificar en el token.
        expires_delta (timedelta | None): Duración del token.

    Returns:
        str: Token JWT codificado.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT.

    Args:
        token (str): Token JWT a decodificar.

    Returns:
        dict: Payload decodificado del token.

    Raises:
        UnauthorizedException: Si el token es inválido o
            ha expirado.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        if payload.get("sub") is None:
            raise UnauthorizedException(
                detail="Token sin sujeto válido"
            )
        return payload
    except JWTError:
        raise UnauthorizedException(
            detail="Token inválido o expirado"
        )
```

---

## 2. Hashing de contraseñas

Usar algoritmos de hashing recursivo como **Bcrypt** o **Argon2**
que son resistentes a ataques de fuerza bruta por su costo
computacional ajustable.

```python
from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Genera el hash de una contraseña.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Hash bcrypt de la contraseña.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verifica una contraseña contra su hash.

    Args:
        plain_password (str): Contraseña en texto plano.
        hashed_password (str): Hash almacenado.

    Returns:
        bool: True si la contraseña coincide.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )
```

La razón de usar bcrypt sobre algoritmos como SHA-256 es que bcrypt
tiene un factor de costo (work factor) que hace cada intento de
hashing deliberadamente lento. Un atacante con GPU no puede paralelizar
millones de intentos por segundo como con SHA-256.

---

## 3. Control de acceso basado en roles (RBAC)

El RBAC se implementa como dependencias verificadoras que interceptan
la solicitud antes de que llegue a la capa de servicios. Si el
usuario no tiene el rol requerido, se emite un 403 Forbidden.

### Modelo de roles

```python
from enum import StrEnum


class UserRole(StrEnum):
    """Roles de usuario disponibles en el sistema."""

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
```

### Dependencia de verificación de roles

```python
from fastapi import Depends, status

from src.core.exceptions import ForbiddenException
from src.core.security import get_current_user


class RequireRole:
    """
    Dependencia que verifica el rol del usuario.

    Emite 403 si el usuario no posee el rol requerido.

    Args:
        allowed_roles (list[UserRole]): Roles permitidos.
    """

    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user=Depends(get_current_user),
    ):
        """
        Verifica que el usuario tenga un rol permitido.

        Args:
            current_user: Usuario autenticado actual.

        Returns:
            User: El usuario si tiene permiso.

        Raises:
            ForbiddenException: Si el rol no es suficiente.
        """
        if current_user.role not in self.allowed_roles:
            raise ForbiddenException(
                detail="Permisos insuficientes"
            )
        return current_user
```

### Uso en routers

```python
from fastapi import APIRouter, Depends

from src.core.security import RequireRole, UserRole


router = APIRouter()


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(RequireRole([UserRole.ADMIN]))
    ],
)
async def delete_user(user_id: int) -> None:
    """
    Elimina un usuario. Solo administradores.

    Args:
        user_id (int): ID del usuario a eliminar.
    """
    ...
```

---

## 4. Dependencias de seguridad

### Obtener usuario actual

```python
from fastapi import Depends

from src.core.security import (
    decode_access_token,
    oauth2_scheme,
)
from src.core.exceptions import UnauthorizedException
from src.users.repository import UserRepository
from src.core.dependencies import get_db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session=Depends(get_db),
):
    """
    Obtiene el usuario actual desde el token JWT.

    Decodifica el token, extrae el ID del sujeto y
    consulta la base de datos para obtener el usuario.

    Args:
        token (str): Token Bearer extraído del header.
        session: Sesión de base de datos.

    Returns:
        User: Instancia del usuario autenticado.

    Raises:
        UnauthorizedException: Si el token es inválido
            o el usuario no existe.
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    repository = UserRepository(session)
    user = await repository.get_by_id(int(user_id))

    if user is None:
        raise UnauthorizedException(
            detail="Usuario no encontrado"
        )
    return user


async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    """
    Verifica que el usuario actual esté activo.

    Args:
        current_user: Usuario autenticado.

    Returns:
        User: Usuario activo verificado.

    Raises:
        ForbiddenException: Si el usuario está desactivado.
    """
    if not current_user.is_active:
        raise ForbiddenException(
            detail="Usuario desactivado"
        )
    return current_user
```

---

## 5. Manejo global de excepciones

Centralizar todas las capturas de excepciones evita la exposición
accidental de detalles internos (nombres de tablas, stack traces,
mensajes de SQLAlchemy) y normaliza la respuesta de error.

### Excepciones personalizadas

```python
from fastapi import status


class AppException(Exception):
    """Excepción base de la aplicación."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.detail = detail
        self.status_code = status_code


class UnauthorizedException(AppException):
    """Error 401: Credenciales inválidas o ausentes."""

    def __init__(
        self,
        detail: str = "No autorizado",
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    """Error 403: Permisos insuficientes."""

    def __init__(
        self,
        detail: str = "Acceso prohibido",
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(AppException):
    """Error 404: Recurso no encontrado."""

    def __init__(
        self,
        detail: str = "Recurso no encontrado",
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictException(AppException):
    """Error 409: Conflicto con el recurso."""

    def __init__(
        self,
        detail: str = "Conflicto con el recurso",
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )
```

### Registrar handlers globales

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra los manejadores de excepciones globales.

    Centraliza la captura de errores y normaliza las
    respuestas JSON según RFC 9457.

    Args:
        app (FastAPI): Instancia de la aplicación.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Maneja las excepciones de la aplicación."""
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

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: IntegrityError,
    ) -> JSONResponse:
        """
        Maneja errores de integridad de la base de datos.

        Transforma errores de SQLAlchemy en respuestas
        seguras que no exponen detalles del schema.
        """
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "type": "about:blank",
                "title": "ConflictError",
                "status": 409,
                "detail": "El recurso ya existe o viola "
                          "una restricción de unicidad",
                "instance": str(request.url),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Captura excepciones no manejadas.

        Previene la exposición de stack traces y detalles
        internos en producción.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "about:blank",
                "title": "InternalServerError",
                "status": 500,
                "detail": "Error interno del servidor",
                "instance": str(request.url),
            },
        )
```

La razón de capturar `IntegrityError` específicamente es que los
errores de unicidad y foreign key de la base de datos contienen
nombres de tablas, columnas y constraints internos que un atacante
podría usar para inferir el schema. El handler lo transforma en un
mensaje genérico seguro.

---

## 6. CORS y headers de seguridad

```python
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

### Settings para CORS

```python
class Settings(BaseSettings):
    """Configuración de la aplicación."""

    allowed_origins: list[str] = [
        "http://localhost:3000",
    ]
```

En producción, nunca usar `allow_origins=["*"]` con
`allow_credentials=True`. Esto expone la API a ataques CSRF desde
cualquier dominio. Siempre especificar los orígenes permitidos
explícitamente.
