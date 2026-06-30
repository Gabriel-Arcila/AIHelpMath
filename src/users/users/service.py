"""Módulo del servicio de negocio para el dominio de usuarios.

Coordina la lógica de negocio y las transacciones para la entidad User.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate
from src.users.users.repository import UserRepository


class UserService:
    """Servicio de gestión de usuarios.

    Coordina la lógica de negocio y las transacciones de base de datos.
    Se encarga de confirmar (commit) o revertir (rollback) las operaciones.
    """

    def __init__(self, session: AsyncSession, repository: UserRepository) -> None:
        self.session = session
        self.repository = repository

    async def create_user(self, user_data: UserCreate) -> User:
        """Crea un nuevo usuario y confirma la transacción en la base de datos.

        Args:
            user_data (UserCreate): Datos del nuevo usuario.

        Returns:
            User: El usuario creado con su ID generado.
        """
        user = await self.repository.add(user_data)
        try:
            await self.session.commit()
            await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            raise
        return user

    async def get_user(self, user_id: str) -> User | None:
        """Recupera un usuario por su ID sin iniciar una transacción de escritura.

        Args:
            user_id (str): ID del usuario.

        Returns:
            User | None: El usuario recuperado o None si no existe.
        """
        return await self.repository.get_by_id(user_id)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Recupera una lista de usuarios de manera paginada.

        Args:
            skip (int): Registros iniciales a omitir.
            limit (int): Número máximo de registros a retornar.

        Returns:
            list[User]: Lista de usuarios encontrados.
        """
        return await self.repository.get_all(skip, limit)

    async def update_user(self, user_id: str, user_update: UserUpdate) -> User | None:
        """Actualiza los datos de un usuario existente y confirma los cambios.

        Args:
            user_id (str): ID del usuario.
            user_update (UserUpdate): Nuevos datos para el usuario.

        Returns:
            User | None: El usuario actualizado o None si no existía.
        """
        db_user = await self.repository.get_by_id(user_id)
        if not db_user:
            return None

        updated_user = await self.repository.update(db_user, user_update)
        try:
            await self.session.commit()
            await self.session.refresh(updated_user)
        except Exception:
            await self.session.rollback()
            raise
        return updated_user

    async def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario de la base de datos y confirma la transacción.

        Args:
            user_id (str): ID del usuario a eliminar.

        Returns:
            bool: True si el usuario fue eliminado, False si no se encontró.
        """
        db_user = await self.repository.get_by_id(user_id)
        if not db_user:
            return False

        await self.repository.delete(db_user)
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return True
