from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db
from src.users.repository import UserRepository
from src.users.service import UserService


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    """Proveedor del servicio de usuarios para la inyección de dependencias de FastAPI.

    Args:
        session (AsyncSession): Sesión de base de datos activa.

    Returns:
        UserService: Instancia de UserService con su repositorio inicializado.
    """
    repository = UserRepository(session)
    return UserService(session, repository)
