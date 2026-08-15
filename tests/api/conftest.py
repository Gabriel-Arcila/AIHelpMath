"""Fixtures locales para pruebas de integración de la API (Endpoints)."""

from typing import Any, cast

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import UserRole


@pytest.fixture
async def seed_user_role(db_session: AsyncSession) -> UserRole:
    """Inserta un rol base 'ESTUDIANTE' en la base de datos para pruebas de integración.

    Args:
        db_session (AsyncSession): Sesión activa de base de datos de pruebas.

    Returns:
        UserRole: Instancia del rol persistido.
    """
    role = UserRole(name="ESTUDIANTE", description="Rol de estudiante de pruebas")
    db_session.add(role)
    await db_session.flush()
    return role


async def create_test_user(
    async_client: AsyncClient,
    user_data: dict[str, Any],
    role_id: int | None,
) -> dict[str, Any]:
    """Helper asíncrono para crear un usuario a través del endpoint POST /v1/users/.

    Args:
        async_client (AsyncClient): Cliente HTTP de pruebas.
        user_data (dict[str, Any]): Datos del usuario a crear.
        role_id (int | None): ID del rol a asociar.

    Returns:
        dict[str, Any]: Cuerpo de la respuesta JSON retornada por el endpoint.
    """
    payload = {**user_data, "id_role": role_id}
    response = await async_client.post("/v1/users/", json=payload)
    return cast("dict[str, Any]", response.json())
