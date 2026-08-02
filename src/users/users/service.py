"""Módulo del servicio de negocio para el dominio de usuarios.

Coordina la lógica de negocio y las transacciones para la entidad User.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    ConflictException,
    DatabaseException,
    NotFoundException,
)
from src.shared.pagination import PaginatedResponse, PaginationParams
from src.users.models import User
from src.users.schemas import UserCreate, UserResponse, UserUpdate
from src.users.users.repository import UserRepository


class UserService:
    """Servicio de gestión de lógica de negocio para usuarios.

    Coordina el acceso a datos a través del repositorio y administra
    las transacciones en la base de datos.

    Attributes:
        session (AsyncSession): Sesión asíncrona de base de datos.
        repository (UserRepository): Instancia del repositorio de usuarios.
    """

    def __init__(self, session: AsyncSession, repository: UserRepository) -> None:
        """Inicializa el servicio de usuarios con sus dependencias.

        Args:
            session (AsyncSession): Sesión de base de datos inyectada.
            repository (UserRepository): Repositorio de usuarios inyectado.
        """
        self.session = session
        self.repository = repository

    async def create(self, user_data: UserCreate) -> User:
        """Crea un nuevo usuario en el sistema.

        Verifica que el correo electrónico no esté registrado previamente.

        Args:
            user_data (UserCreate): Datos para la creación del usuario.

        Returns:
            User: Instancia del usuario creado y persistido.

        Raises:
            ConflictException: Si el email ya está en uso.
        """
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user is not None:
            raise ConflictException(
                detail=f"User with email '{user_data.email}' already exists"
            )

        try:
            user = await self.repository.add(user_data)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as err:
            await self.session.rollback()
            raise DatabaseException(
                detail=f"Database operation failed: {err}"
            ) from err

    async def get_by_id(self, user_id: str) -> User:
        """Obtiene un usuario por su identificador único.

        Args:
            user_id (str): Identificador UUID del usuario.

        Returns:
            User: Instancia del usuario encontrado.

        Raises:
            NotFoundException: Si el usuario no existe.
        """
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(detail=f"User with id '{user_id}' not found")
        return user

    async def get_detailed(self, user_id: str) -> User:
        """Obtiene un usuario con sus relaciones cargadas (rol y perfiles IA).

        Args:
            user_id (str): Identificador UUID del usuario.

        Returns:
            User: Instancia del usuario con sus relaciones.

        Raises:
            NotFoundException: Si el usuario no existe.
        """
        user = await self.repository.get_detailed(user_id)
        if user is None:
            raise NotFoundException(detail=f"User with id '{user_id}' not found")
        return user

    async def get_all(
        self, pagination: PaginationParams
    ) -> PaginatedResponse[UserResponse]:
        """Obtiene una lista paginada de usuarios.

        Args:
            pagination (PaginationParams): Parámetros de paginación (offset y limit).

        Returns:
            PaginatedResponse[UserResponse]: Respuesta con la lista de usuarios y
                metadata de paginación.
        """
        items = await self.repository.get_all(pagination.offset, pagination.limit)
        total = await self.repository.count()
        user_responses = [UserResponse.model_validate(item) for item in items]
        return PaginatedResponse[UserResponse](
            items=user_responses,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    async def update(self, user_id: str, user_data: UserUpdate) -> User:
        """Actualiza los datos de un usuario existente.

        Si se actualiza el email, verifica que no esté registrado por otro usuario.

        Args:
            user_id (str): Identificador UUID del usuario a actualizar.
            user_data (UserUpdate): Datos a modificar.

        Returns:
            User: Instancia del usuario actualizado.

        Raises:
            NotFoundException: Si el usuario no existe.
            ConflictException: Si el nuevo email ya pertenece a otro usuario.
        """
        user = await self.get_by_id(user_id)

        if user_data.email is not None and user_data.email != user.email:
            existing_user = await self.repository.get_by_email(user_data.email)
            if existing_user is not None:
                raise ConflictException(
                    detail=f"User with email '{user_data.email}' already exists"
                )

        try:
            updated_user = await self.repository.update(user, user_data)
            await self.session.commit()
            await self.session.refresh(updated_user)
            return updated_user
        except Exception as err:
            await self.session.rollback()
            raise DatabaseException(
                detail=f"Database operation failed: {err}"
            ) from err

    async def delete(self, user_id: str) -> None:
        """Elimina un usuario del sistema.

        Args:
            user_id (str): Identificador UUID del usuario a eliminar.

        Raises:
            NotFoundException: Si el usuario no existe.
        """
        user = await self.get_by_id(user_id)
        try:
            await self.repository.delete(user)
            await self.session.commit()
        except Exception as err:
            await self.session.rollback()
            raise DatabaseException(
                detail=f"Database operation failed: {err}"
            ) from err
