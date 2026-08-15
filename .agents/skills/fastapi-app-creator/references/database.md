# Base de Datos: SQLAlchemy Asíncrono, Sesiones y Alembic

Referencia especializada para la configuración y gestión de la capa de
persistencia en aplicaciones FastAPI.

## Tabla de contenidos

1. [Configuración del engine asíncrono](#1-configuración-del-engine-asíncrono)
2. [Sesiones como dependencias](#2-sesiones-como-dependencias)
3. [Límites transaccionales](#3-límites-transaccionales)
4. [Modelos SQLAlchemy](#4-modelos-sqlalchemy)
5. [Repositorios con operaciones en lote](#5-repositorios-con-operaciones-en-lote)
6. [Estrategias de escalabilidad](#6-estrategias-de-escalabilidad)
7. [Alembic para migraciones](#7-alembic-para-migraciones)

---

## 1. Configuración del engine asíncrono

El driver `asyncpg` permite soportar miles de conexiones mediante un
solo hilo. La configuración del pool de conexiones es crítica para
evitar saturación en producción.

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""

    pass
```

### Parámetros del pool explicados

| Parámetro | Propósito |
|---|---|
| `pool_size` | Conexiones permanentes en el pool |
| `max_overflow` | Conexiones extra temporales bajo carga |
| `pool_timeout` | Segundos esperando una conexión libre |
| `pool_recycle` | Recicla conexiones inactivas (evita timeouts del servidor DB) |
| `pool_pre_ping` | Verifica que la conexión está viva antes de usarla |
| `expire_on_commit=False` | Evita consultas lazy posteriores al commit |

---

## 2. Sesiones como dependencias

Las sesiones se inyectan como dependencias mediante funciones
generadoras con `yield` dentro de un bloque `try-finally` para
prevenir fugas de conexión.

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Proveedor de sesiones de base de datos.

    Garantiza el cierre de la sesión incluso si ocurre
    una excepción durante el procesamiento.

    Yields:
        AsyncSession: Sesión asíncrona de SQLAlchemy.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
```

La razón del patrón `try-finally` con `yield` es que FastAPI ejecuta
el código después del `yield` como limpieza, pero si ocurre una
excepción no manejada, el `finally` garantiza que la sesión se cierra
correctamente y no queda abierta consumiendo recursos del pool.

---

## 3. Límites transaccionales

### El antipatrón autocommit

El error más común es dispersar `commit()` y `rollback()` en
repositorios o routers. Esto rompe la atomicidad cuando una operación
de negocio involucra múltiples repositorios.

**Incorrecto** — commit en el repositorio:
```python
class UserRepository:
    async def add(self, user_data):
        user = User(**user_data.model_dump())
        self.session.add(user)
        await self.session.commit()  # ❌ No aquí
        return user
```

**Correcto** — commit en el servicio:
```python
class UserService:
    async def create_with_profile(self, user_data, profile_data):
        """
        Crea un usuario y su perfil de forma atómica.

        Si cualquiera de las operaciones falla, toda la
        transacción se revierte automáticamente.
        """
        user = await self.user_repo.add(user_data)
        profile_data.user_id = user.id
        await self.profile_repo.add(profile_data)
        await self.session.commit()  # ✅ Aquí
        await self.session.refresh(user)
        return user
```

El servicio es el único que conoce la unidad completa de trabajo.
Solo él sabe cuándo todas las operaciones de una transacción se
completaron exitosamente.

---

## 4. Modelos SQLAlchemy

Usar el estilo declarativo moderno con anotaciones de tipo.

```python
from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class User(Base):
    """
    Modelo ORM para la tabla de usuarios.

    Attributes:
        id: Identificador único autoincremental.
        name: Nombre del usuario.
        email: Correo electrónico único.
        hashed_password: Contraseña hasheada.
        is_active: Estado de activación.
        created_at: Fecha de creación automática.
        updated_at: Fecha de última actualización.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(),
    )
```

---

## 5. Repositorios con operaciones en lote

Maximizar las operaciones en lote para reducir el número de
round-trips a la base de datos.

```python
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


class UserRepository:
    """
    Repositorio de acceso a datos para usuarios.

    Encapsula las consultas y no gestiona transacciones.

    Args:
        session (AsyncSession): Sesión de base de datos.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_many(
        self,
        users: list[User],
    ) -> list[User]:
        """
        Agrega múltiples usuarios en una sola operación.

        Args:
            users (list[User]): Lista de instancias ORM.

        Returns:
            list[User]: Usuarios agregados a la sesión.
        """
        self.session.add_all(users)
        return users

    async def get_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[User]:
        """
        Obtiene usuarios con paginación.

        Args:
            offset (int): Inicio de la paginación.
            limit (int): Cantidad máxima de resultados.

        Returns:
            list[User]: Lista de usuarios paginados.
        """
        result = await self.session.execute(
            select(User)
            .offset(offset)
            .limit(limit)
            .order_by(User.id)
        )
        return list(result.scalars().all())

    async def deactivate_batch(
        self,
        user_ids: list[int],
    ) -> int:
        """
        Desactiva múltiples usuarios en una sola query.

        Args:
            user_ids (list[int]): IDs de usuarios a desactivar.

        Returns:
            int: Cantidad de registros actualizados.
        """
        result = await self.session.execute(
            update(User)
            .where(User.id.in_(user_ids))
            .values(is_active=False)
        )
        return result.rowcount
```

---

## 6. Estrategias de escalabilidad

### Lectura/Escritura separadas

Para alta carga, integrar réplicas de lectura con engines separados.

```python
write_engine = create_async_engine(
    settings.database_write_url,
    pool_size=10,
)

read_engine = create_async_engine(
    settings.database_read_url,
    pool_size=30,
)

write_session_factory = async_sessionmaker(
    write_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

read_session_factory = async_sessionmaker(
    read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Timeouts explícitos

Estipular tiempos de espera en las sesiones para prevenir la
saturación operativa bajo carga extrema.

```python
from sqlalchemy import text


async def execute_with_timeout(
    session: AsyncSession,
    stmt,
    timeout_ms: int = 5000,
):
    """
    Ejecuta una consulta con timeout explícito.

    Args:
        session (AsyncSession): Sesión de base de datos.
        stmt: Sentencia SQL a ejecutar.
        timeout_ms (int): Timeout en milisegundos.

    Returns:
        Result: Resultado de la consulta.
    """
    await session.execute(
        text(f"SET statement_timeout = {timeout_ms}")
    )
    return await session.execute(stmt)
```

---

## 7. Alembic para migraciones

### Configuración inicial

```bash
alembic init alembic
```

### env.py asíncrono

```python
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings
from src.core.database import Base

# Importar todos los modelos para que Alembic los detecte
from src.users.models import User  # noqa: F401


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Ejecuta migraciones en modo offline.

    Genera SQL sin conectar a la base de datos.
    """
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Ejecuta migraciones de forma asíncrona.

    Conecta al engine y ejecuta las migraciones dentro
    de una transacción.
    """
    connectable = create_async_engine(
        settings.database_url,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def do_run_migrations(connection) -> None:
    """
    Ejecuta las migraciones con la conexión proporcionada.

    Args:
        connection: Conexión síncrona de SQLAlchemy.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online (asíncrono)."""
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Generar y aplicar migraciones

```bash
# Generar migración automática
alembic revision --autogenerate -m "crear tabla users"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

### Buenas prácticas de Alembic

- Siempre revisar las migraciones autogeneradas antes de aplicarlas.
- Importar todos los modelos en `env.py` para que `autogenerate`
  los detecte.
- Nombrar las migraciones de forma descriptiva.
- No modificar migraciones ya aplicadas en producción.
