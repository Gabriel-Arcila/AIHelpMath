"""Módulo del repositorio de datos para el dominio de usuarios.

Encapsula las operaciones CRUD directas sobre la base de datos para la entidad User.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.users.schemas import UserCreate, UserUpdate


class UserRepository:
    """Repositorio de acceso a datos para usuarios.

    Encapsula las consultas a la base de datos y no gestiona transacciones
    (los commits y rollbacks se delegan a la capa de servicios).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user_data: UserCreate) -> User:
        """Agrega un nuevo usuario a la sesión.

        Args:
            user_data (UserCreate): Datos de creación del usuario.

        Returns:
            User: Instancia del usuario agregada.
        """
        user = User(**user_data.model_dump())
        self.session.add(user)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        """Obtiene un usuario por su identificador único.

        Args:
            user_id (str): ID del usuario.

        Returns:
            User | None: El usuario encontrado o None.
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)  # type: ignore[arg-type]
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Obtiene todos los usuarios de forma paginada.

        Args:
            skip (int): Registros a omitir.
            limit (int): Límite de registros a recuperar.

        Returns:
            list[User]: Lista de usuarios encontrados.
        """
        result = await self.session.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, db_user: User, user_update: UserUpdate) -> User:
        """Actualiza de manera parcial los datos de un usuario en la sesión.

        Args:
            db_user (User): Instancia del usuario en base de datos.
            user_update (UserUpdate): Datos de actualización parcial.

        Returns:
            User: Instancia del usuario actualizada.
        """
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        self.session.add(db_user)
        return db_user

    async def delete(self, db_user: User) -> None:
        """Marca para eliminación un usuario en la sesión.

        Args:
            db_user (User): Instancia del usuario a eliminar.
        """
        await self.session.delete(db_user)
