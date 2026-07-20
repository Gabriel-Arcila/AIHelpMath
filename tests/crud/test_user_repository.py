"""Pruebas unitarias para el repositorio de usuarios (UserRepository)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User, UserAIProfile, UserLevel, UserRole, UserTopic
from src.users.schemas import UserCreate, UserUpdate
from src.users.users.repository import UserRepository


class TestUserRepository:
    """Grupo de pruebas unitarias para UserRepository."""

    async def test_add_persists_and_returns_user(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que add() persiste un usuario en la base de datos y genera su ID."""
        # Arrange
        repo = UserRepository(db_session)
        user_data = UserCreate(
            id_role=seed_user_role.id,
            first_name="Juan",
            last_name="Perez",
            email="juan.perez@example.com",
        )

        # Act
        user = await repo.add(user_data)
        await db_session.flush()  # Sincroniza el estado con la base de datos para obtener el ID

        # Assert
        assert user.id is not None
        assert user.first_name == "Juan"
        assert user.last_name == "Perez"
        assert user.email == "juan.perez@example.com"
        assert user.id_role == seed_user_role.id

    async def test_get_by_id_returns_existing_user(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que get_by_id() recupera un usuario existente por su ID."""
        # Arrange
        repo = UserRepository(db_session)
        user = User(
            id_role=seed_user_role.id,
            first_name="Maria",
            last_name="Gomez",
            email="maria.gomez@example.com",
        )
        db_session.add(user)
        await db_session.flush()

        # Act
        retrieved_user = await repo.get_by_id(user.id)

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == "maria.gomez@example.com"

    async def test_get_by_id_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que get_by_id() retorna None si el usuario no existe."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        retrieved_user = await repo.get_by_id("non-existent-uuid")

        # Assert
        assert retrieved_user is None

    async def test_get_by_email_returns_existing_user(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que get_by_email() obtiene un usuario por su email."""
        # Arrange
        repo = UserRepository(db_session)
        user = User(
            id_role=seed_user_role.id,
            first_name="Carlos",
            last_name="Ruiz",
            email="carlos.ruiz@example.com",
        )
        db_session.add(user)
        await db_session.flush()

        # Act
        retrieved_user = await repo.get_by_email(user.email)

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == "carlos.ruiz@example.com"

    async def test_get_by_email_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que get_by_email() retorna None si el email no existe."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        retrieved_user = await repo.get_by_email("unknown@example.com")

        # Assert
        assert retrieved_user is None

    async def test_get_all_returns_list(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que get_all() retorna una lista paginada de usuarios."""
        # Arrange
        repo = UserRepository(db_session)
        user1 = User(
            id_role=seed_user_role.id,
            first_name="User1",
            last_name="Test",
            email="user1@example.com",
        )
        user2 = User(
            id_role=seed_user_role.id,
            first_name="User2",
            last_name="Test",
            email="user2@example.com",
        )
        db_session.add_all([user1, user2])
        await db_session.flush()

        # Act
        users = await repo.get_all(offset=0, limit=10)

        # Assert
        assert len(users) >= 2
        emails = [u.email for u in users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails

    async def test_get_all_returns_empty_list_when_no_users(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que get_all() retorna lista vacía si no hay registros."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        users = await repo.get_all(offset=0, limit=10)

        # Assert
        # NOTA: En un entorno de base de datos de prueba limpio, debería ser exactamente 0.
        assert len(users) == 0

    async def test_update_modifies_fields(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que update() modifica los campos correspondientes de un usuario."""
        # Arrange
        repo = UserRepository(db_session)
        user = User(
            id_role=seed_user_role.id,
            first_name="OriginalName",
            last_name="OriginalLastName",
            email="original@example.com",
        )
        db_session.add(user)
        await db_session.flush()

        update_data = UserUpdate(
            first_name="NewName",
            last_name="NewLastName",
        )

        # Act
        updated_user = await repo.update(user, update_data)
        await db_session.flush()

        # Assert
        assert updated_user.first_name == "NewName"
        assert updated_user.last_name == "NewLastName"
        assert updated_user.email == "original@example.com"  # No cambió

    async def test_delete_removes_user(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que delete() elimina un usuario de la base de datos."""
        # Arrange
        repo = UserRepository(db_session)
        user = User(
            id_role=seed_user_role.id,
            first_name="DeleteMe",
            last_name="Test",
            email="deleteme@example.com",
        )
        db_session.add(user)
        await db_session.flush()

        # Act
        await repo.delete(user)
        await db_session.flush()

        # Assert
        deleted = await db_session.get(User, user.id)
        assert deleted is None

    async def test_get_detailed_loads_relationships(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que get_detailed() carga eager las relaciones de rol y perfiles IA."""
        # Arrange
        repo = UserRepository(db_session)
        
        # Necesitamos crear UserLevel, UserTopic y UserAIProfile para probar la relación
        level = UserLevel(name="PRINCIPIANTE", quantifier=0, description="Nivel básico")
        topic = UserTopic(name="ALGEBRA", description="Tema de álgebra")
        db_session.add_all([level, topic])
        await db_session.flush()

        user = User(
            id_role=seed_user_role.id,
            first_name="Detailed",
            last_name="User",
            email="detailed.user@example.com",
        )
        db_session.add(user)
        await db_session.flush()

        profile = UserAIProfile(
            id_user=user.id,
            id_user_level=level.id,
            id_user_topic=topic.id,
            description="Perfil de álgebra básica",
        )
        db_session.add(profile)
        await db_session.flush()

        # Act
        detailed_user = await repo.get_detailed(user.id)

        # Assert
        assert detailed_user is not None
        assert detailed_user.id == user.id
        
        # Verificar que el rol está cargado y es el correcto
        assert detailed_user.user_role is not None
        assert detailed_user.user_role.name == "ESTUDIANTE"

        # Verificar que el perfil de IA está cargado en la colección
        assert len(detailed_user.user_ai_profiles) == 1
        loaded_profile = detailed_user.user_ai_profiles[0]
        assert loaded_profile.description == "Perfil de álgebra básica"
        assert loaded_profile.user_level.name == "PRINCIPIANTE"
        assert loaded_profile.user_topic.name == "ALGEBRA"
