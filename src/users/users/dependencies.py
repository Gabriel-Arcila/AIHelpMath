"""Inyección de dependencias para el submódulo de usuarios."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db
from src.users.users.repository import UserRepository
from src.users.users.service import UserService


async def get_user_service(
    session: AsyncSession = Depends(get_db),
) -> UserService:
    """Provee una instancia de UserService por cada solicitud.

    Construye la cadena de inyección de dependencias: session -> repository -> service.

    Args:
        session (AsyncSession): Sesión de base de datos asíncrona inyectada por FastAPI.

    Returns:
        UserService: Instancia configurada del servicio de usuarios.
    """
    repository = UserRepository(session)
    return UserService(session, repository)
