"""Mapeo de rutas y endpoints HTTP para la gestión de usuarios."""

from fastapi import APIRouter, Depends, status

from src.shared.pagination import PaginatedResponse, PaginationParams
from src.users.schemas import UserCreate, UserDetailed, UserResponse, UserUpdate
from src.users.users.dependencies import get_user_service
from src.users.users.service import UserService

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Crea un nuevo usuario en la plataforma.

    Args:
        user_data (UserCreate): Datos del usuario a registrar.
        service (UserService): Servicio de negocio de usuarios inyectado.

    Returns:
        UserResponse: Datos del usuario creado.
    """
    user = await service.create(user_data)
    return UserResponse.model_validate(user)


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
)
async def list_users(
    pagination: PaginationParams = Depends(),
    service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserResponse]:
    """Obtiene un listado paginado de usuarios registrados.

    Args:
        pagination (PaginationParams): Parámetros de paginación inyectados.
        service (UserService): Servicio de negocio de usuarios inyectado.

    Returns:
        PaginatedResponse[UserResponse]: Respuesta con la lista de usuarios y metadata.
    """
    return await service.get_all(pagination)


@router.get(
    "/{user_id}/detailed",
    response_model=UserDetailed,
)
async def get_user_detailed(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserDetailed:
    """Obtiene la información detallada de un usuario incluyendo su rol y perfiles IA.

    Args:
        user_id (str): Identificador único del usuario.
        service (UserService): Servicio de negocio de usuarios inyectado.

    Returns:
        UserDetailed: Datos detallados del usuario con sus relaciones.
    """
    user = await service.get_detailed(user_id)
    return UserDetailed.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Obtiene los datos básicos de un usuario por su identificador único.

    Args:
        user_id (str): Identificador único del usuario.
        service (UserService): Servicio de negocio de usuarios inyectado.

    Returns:
        UserResponse: Datos del usuario solicitado.
    """
    user = await service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Actualiza parcialmente los datos de un usuario existente.

    Args:
        user_id (str): Identificador único del usuario.
        user_data (UserUpdate): Datos a modificar.
        service (UserService): Servicio de negocio de usuarios inyectado.

    Returns:
        UserResponse: Datos del usuario actualizado.
    """
    user = await service.update(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> None:
    """Elimina un usuario del sistema.

    Args:
        user_id (str): Identificador único del usuario a eliminar.
        service (UserService): Servicio de negocio de usuarios inyectado.
    """
    await service.delete(user_id)
