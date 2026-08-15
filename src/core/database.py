"""Módulo de configuración y conexión a la base de datos.

Establece el motor asíncrono de SQLAlchemy y la factoría de sesiones
para interactuar con la base de datos PostgreSQL utilizando SQLModel.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from src.core.config import settings

# Adaptar URL a postgresql+asyncpg:// para soporte asíncrono
db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# En producción, usa echo=False
engine = create_async_engine(
    db_url,
    echo=True,
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

# Exportar metadata para Alembic
target_metadata = SQLModel.metadata
