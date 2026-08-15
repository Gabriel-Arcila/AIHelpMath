"""Dependencias compartidas y globales de la aplicación.

Contiene los proveedores de sesión de base de datos y otras utilidades
inyectables en los endpoints de FastAPI.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Proveedor de sesiones de base de datos asíncronas.

    Garantiza el cierre de la sesión incluso si ocurre una excepción
    durante el procesamiento de la solicitud.

    Yields:
        AsyncSession: Sesión activa de base de datos.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
