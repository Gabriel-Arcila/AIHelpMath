"""Mapeo de rutas para el dominio de usuarios."""

from fastapi import APIRouter, Depends, Response, status

from src.core.exceptions import NotFoundException
from src.users.schemas import UserCreate, UserResponse, UserUpdate
from src.users.users.dependencies import get_user_service
from src.users.users.service import UserService

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Crea un nuevo usuario en el sistema.

    Args:
        user_data (UserCreate): Datos del usuario a crear.
        service (UserService): Servicio de usuarios inyectado.

    Returns:
        UserResponse: El usuario creado.
    """
    db_user = await service.create_user(user_data)
    return UserResponse.model_validate(db_user)


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener lista de usuarios",
)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    """Obtiene una lista paginada de usuarios registrados.

    Args:
        skip (int): Registros iniciales a omitir.
        limit (int): Número máximo de registros a retornar.
        service (UserService): Servicio de usuarios inyectado.

    Returns:
        list[UserResponse]: Lista de usuarios encontrados.
    """
    users = await service.get_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Obtiene los detalles de un usuario específico a partir de su ID.

    Args:
        user_id (str): ID único del usuario a buscar.
        service (UserService): Servicio de usuarios inyectado.

    Returns:
        UserResponse: El usuario encontrado.

    Raises:
        NotFoundException: Si el usuario no existe.
    """
    db_user = await service.get_user(user_id)
    if not db_user:
        raise NotFoundException(f"Usuario con ID {user_id} no encontrado")
    return UserResponse.model_validate(db_user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Actualiza de forma parcial los datos de un usuario existente.

    Args:
        user_id (str): ID único del usuario a actualizar.
        user_update (UserUpdate): Nuevos datos para el usuario.
        service (UserService): Servicio de usuarios inyectado.

    Returns:
        UserResponse: El usuario actualizado.

    Raises:
        NotFoundException: Si el usuario no existe.
    """
    updated_user = await service.update_user(user_id, user_update)
    if not updated_user:
        raise NotFoundException(f"Usuario con ID {user_id} no encontrado")
    return UserResponse.model_validate(updated_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> Response:
    """Elimina un usuario del sistema a partir de su ID.

    Args:
        user_id (str): ID único del usuario a eliminar.
        service (UserService): Servicio de usuarios inyectado.

    Returns:
        Response: Respuesta vacía con código de estado 204.

    Raises:
        NotFoundException: Si el usuario no existe.
    """
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise NotFoundException(f"Usuario con ID {user_id} no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
