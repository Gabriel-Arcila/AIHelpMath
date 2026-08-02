"""Pruebas unitarias para el repositorio de usuarios (UserRepository)."""

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
        # Sincroniza el estado con la DB para obtener el ID asignado
        await db_session.flush()

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
            first_name="Pedro",
            last_name="Gomez",
            email="pedro.gomez@example.com",
        )
        db_session.add(user)
        await db_session.flush()

        # Act
        found = await repo.get_by_id(user.id)

        # Assert
        assert found is not None
        assert found.id == user.id
        assert found.email == "pedro.gomez@example.com"

    async def test_get_by_id_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que get_by_id() retorna None si el ID no existe en la DB."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        found = await repo.get_by_id("00000000-0000-0000-0000-000000000000")

        # Assert
        assert found is None

    async def test_get_by_email_returns_existing_user(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que get_by_email() recupera un usuario por su email."""
        # Arrange
        repo = UserRepository(db_session)
        user = User(
            id_role=seed_user_role.id,
            first_name="Maria",
            last_name="Lopez",
            email="maria.lopez@example.com",
        )
        db_session.add(user)
        await db_session.flush()

        # Act
        found = await repo.get_by_email("maria.lopez@example.com")

        # Assert
        assert found is not None
        assert found.id == user.id

    async def test_get_by_email_returns_none_for_nonexistent(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que get_by_email() retorna None si el email no existe."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        found = await repo.get_by_email("nonexistent@example.com")

        # Assert
        assert found is None

    async def test_get_all_returns_list(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que get_all() retorna lista de usuarios con paginación."""
        # Arrange
        repo = UserRepository(db_session)
        users_to_create = [
            User(
                id_role=seed_user_role.id,
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@example.com",
            )
            for i in range(1, 4)
        ]
        db_session.add_all(users_to_create)
        await db_session.flush()

        # Act
        users = await repo.get_all(offset=0, limit=10)

        # Assert
        assert len(users) >= 3

    async def test_get_all_returns_empty_list_when_no_users(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que get_all() retorna lista vacía si no hay registros."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        users = await repo.get_all(offset=0, limit=10)

        # Assert
        # NOTA: En DB limpia debe ser exactamente 0.
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
        """Verifica que get_detailed() carga eager las relaciones de rol y
        perfiles IA.
        """
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

    async def test_count_returns_zero_when_empty(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que count() retorna 0 cuando no hay usuarios."""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        total = await repo.count()

        # Assert
        assert total == 0

    async def test_count_returns_correct_number(
        self, db_session: AsyncSession, seed_user_role: UserRole
    ) -> None:
        """Verifica que count() retorna el número exacto de usuarios."""
        # Arrange
        repo = UserRepository(db_session)
        users = [
            User(
                id_role=seed_user_role.id,
                first_name=f"CountUser{i}",
                last_name="Test",
                email=f"countuser{i}@example.com",
            )
            for i in range(3)
        ]
        db_session.add_all(users)
        await db_session.flush()

        # Act
        total = await repo.count()

        # Assert
        assert total == 3
