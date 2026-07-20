"""Fixtures locales para pruebas unitarias de la capa de persistencia (CRUD)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import UserRole


@pytest.fixture
async def seed_user_role(db_session: AsyncSession) -> UserRole:
    """Inserta un rol base 'ESTUDIANTE' en la base de datos para pruebas unitarias.

    Args:
        db_session (AsyncSession): Sesión activa de base de datos de pruebas.

    Returns:
        UserRole: Instancia del rol persistido.
    """
    role = UserRole(name="ESTUDIANTE", description="Rol de estudiante de pruebas")
    db_session.add(role)
    await db_session.flush()
    return role
