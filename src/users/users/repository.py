"""Módulo del repositorio de datos para el dominio de usuarios.

Encapsula las operaciones CRUD directas sobre la base de datos para la entidad User.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.users.models import User, UserAIProfile
from src.users.schemas import UserCreate, UserUpdate


class UserRepository:
    """Repositorio de acceso a datos para usuarios.

    Se encarga de ejecutar operaciones CRUD directas sobre la base de datos utilizando
    SQLAlchemy asíncrono.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el repositorio con la sesión de base de datos.

        Args:
            session (AsyncSession): Sesión asíncrona de base de datos activa.
        """
        self.session = session

    async def add(self, user_data: UserCreate) -> User:
        """Crea e inserta un nuevo usuario en la base de datos.

        Args:
            user_data (UserCreate): Schema con los datos del usuario a crear.

        Returns:
            User: La instancia del modelo User creada y agregada a la sesión.
        """
        user = User(**user_data.model_dump())
        self.session.add(user)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        """Busca un usuario por su identificador único (UUID).

        Args:
            user_id (str): Identificador único del usuario.

        Returns:
            User | None: Instancia del usuario si existe, de lo contrario None.
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Busca un usuario por su correo electrónico.

        Args:
            email (str): Correo electrónico del usuario.

        Returns:
            User | None: Instancia del usuario si existe, de lo contrario None.
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all(self, offset: int = 0, limit: int = 10) -> list[User]:
        """Obtiene un listado paginado de usuarios.

        Args:
            offset (int): Número de registros a omitir.
            limit (int): Número máximo de registros a retornar.

        Returns:
            list[User]: Lista de usuarios obtenidos.
        """
        result = await self.session.execute(
            select(User).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Obtiene el número total de usuarios registrados.

        Returns:
            int: Cantidad total de usuarios.
        """
        result = await self.session.execute(
            select(func.count()).select_from(User)
        )
        return result.scalar() or 0

    async def update(self, user: User, user_data: UserUpdate) -> User:
        """Actualiza de forma parcial los campos de un usuario existente.

        Args:
            user (User): Instancia del modelo a modificar.
            user_data (UserUpdate): Schema con los nuevos datos opcionales.

        Returns:
            User: La instancia del usuario actualizada.
        """
        update_dict = user_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        return user

    async def delete(self, user: User) -> None:
        """Elimina un usuario de la sesión de base de datos.

        Args:
            user (User): Instancia del usuario a eliminar.
        """
        await self.session.delete(user)

    async def get_detailed(self, user_id: str) -> User | None:
        """Obtiene un usuario cargando ansiosamente su rol y perfiles de IA asociados.

        Args:
            user_id (str): Identificador único del usuario.

        Returns:
            User | None: Instancia del usuario detallado si existe, de lo contrario None.
        """
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.user_role),
                selectinload(User.user_ai_profiles).selectinload(UserAIProfile.user_level),
                selectinload(User.user_ai_profiles).selectinload(UserAIProfile.user_topic)
            )
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
