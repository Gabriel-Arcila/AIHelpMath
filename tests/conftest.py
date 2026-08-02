"""Fixtures globales de pytest para pruebas de integración y unitarias."""

import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

import src.users.models
from src.core.config import settings
from src.core.dependencies import get_db
from src.main import app

# Adaptar URL a postgresql+asyncpg:// para soporte asíncrono en la DB de pruebas
db_url = settings.test_database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Engine de test con NullPool para evitar conflictos de event loop entre hilos en tests
engine_test = create_async_engine(
    db_url,
    poolclass=NullPool,
    echo=True,
)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Crea y destruye las tablas en la base de datos de pruebas (TestAIHelpMath).

    Se ejecuta una sola vez por sesión de pytest.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine_test.dispose()


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos asíncrona aislada para pruebas.

    Cada test se ejecuta en una transacción contenedora con savepoints que realiza
    rollback automático al finalizar para garantizar el aislamiento de la base de datos.

    Yields:
        AsyncSession: Sesión de base de datos activa para el test.
    """
    async with engine_test.connect() as connection:
        transaction = await connection.begin()
        await connection.begin_nested()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        @event.listens_for(
            session.sync_session,
            "after_transaction_end",
        )
        def restart_savepoint(sync_session, trans):
            """Reinicia el savepoint tras cada commit."""
            if trans.nested and not trans._parent.nested:
                sync_session.begin_nested()

        try:
            yield session
        finally:
            await transaction.rollback()
            await session.close()


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Proporciona un cliente HTTP asíncrono configurado para las pruebas.

    Sobreescribe la dependencia de obtención de base de datos `get_db` para
    inyectar la sesión de base de datos de test con rollback automático.

    Args:
        db_session (AsyncSession): Sesión de base de datos aislada para el test.

    Yields:
        AsyncClient: Cliente HTTP asíncrono conectado a la app FastAPI.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Crea una instancia única de event loop de asyncio para toda la sesión de pruebas.

    Evita el error 'Event loop is closed' que ocurre al cerrar y abrir loops por test
    en Windows cuando se usa SQLAlchemy y drivers asíncronos.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
