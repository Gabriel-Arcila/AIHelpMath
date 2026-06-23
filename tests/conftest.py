"""Fixtures globales de pytest para pruebas de integración y unitarias."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import engine
from src.core.dependencies import get_db
from src.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos asíncrona aislada para pruebas.

    Cada test se ejecuta en una transacción contenedora que realiza rollback
    automático al finalizar para garantizar el aislamiento de la base de datos.

    Yields:
        AsyncSession: Sesión de base de datos activa para el test.
    """
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )
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
