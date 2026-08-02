"""Tests unitarios para la capa UserService utilizando AsyncMock."""

from unittest.mock import AsyncMock

import pytest

from src.core.exceptions import (
    ConflictException,
    DatabaseException,
    NotFoundException,
)
from src.shared.pagination import PaginatedResponse, PaginationParams
from src.users.models import User
from src.users.schemas import UserCreate, UserResponse, UserUpdate
from src.users.users.service import UserService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture que provee un AsyncMock de AsyncSession."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Fixture que provee un AsyncMock de UserRepository."""
    return AsyncMock()


@pytest.fixture
def user_service(mock_session: AsyncMock, mock_repository: AsyncMock) -> UserService:
    """Fixture que provee una instancia de UserService con dependencias simuladas."""
    return UserService(session=mock_session, repository=mock_repository)


class TestUserServiceCreate:
    """Pruebas unitarias para el método UserService.create."""

    async def test_create_calls_commit_on_success(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_data = UserCreate(
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        expected_user = User(
            id="user-123",
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_by_email.return_value = None
        mock_repository.add.return_value = expected_user

        result = await user_service.create(user_data)

        assert result == expected_user
        mock_repository.get_by_email.assert_called_once_with("john@example.com")
        mock_repository.add.assert_called_once_with(user_data)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(expected_user)
        mock_session.rollback.assert_not_called()

    async def test_create_calls_rollback_on_repository_error(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_data = UserCreate(
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_by_email.return_value = None
        mock_repository.add.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Database operation failed"):
            await user_service.create(user_data)

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()

    async def test_create_calls_rollback_on_commit_error(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_data = UserCreate(
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        expected_user = User(
            id="user-123",
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_by_email.return_value = None
        mock_repository.add.return_value = expected_user
        mock_session.commit.side_effect = Exception("Commit failed")

        with pytest.raises(DatabaseException, match="Database operation failed"):
            await user_service.create(user_data)

        mock_session.rollback.assert_called_once()

    async def test_create_raises_conflict_for_duplicate_email(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_data = UserCreate(
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        existing_user = User(
            id="user-existing",
            id_role=1,
            first_name="Existing",
            last_name="User",
            email="john@example.com",
        )
        mock_repository.get_by_email.return_value = existing_user

        with pytest.raises(ConflictException):
            await user_service.create(user_data)

        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_not_called()


class TestUserServiceUpdate:
    """Pruebas unitarias para el método UserService.update."""

    async def test_update_calls_commit_on_success(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "user-123"
        existing_user = User(
            id=user_id,
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        update_data = UserUpdate(first_name="Johnny")
        updated_user = User(
            id=user_id,
            id_role=1,
            first_name="Johnny",
            last_name="Doe",
            email="john@example.com",
        )

        mock_repository.get_by_id.return_value = existing_user
        mock_repository.update.return_value = updated_user

        result = await user_service.update(user_id, update_data)

        assert result == updated_user
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(updated_user)
        mock_session.rollback.assert_not_called()

    async def test_update_calls_rollback_on_error(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "user-123"
        existing_user = User(
            id=user_id,
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        update_data = UserUpdate(first_name="Johnny")

        mock_repository.get_by_id.return_value = existing_user
        mock_repository.update.side_effect = Exception("DB error")

        with pytest.raises(DatabaseException, match="Database operation failed"):
            await user_service.update(user_id, update_data)

        mock_session.rollback.assert_called_once()
        mock_session.refresh.assert_not_called()
        mock_session.commit.assert_not_called()

    async def test_update_raises_conflict_for_duplicate_email(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "user-123"
        existing_user = User(
            id=user_id,
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        update_data = UserUpdate(email="other@example.com")
        other_user = User(
            id="user-456",
            id_role=1,
            first_name="Other",
            last_name="User",
            email="other@example.com",
        )

        mock_repository.get_by_id.return_value = existing_user
        mock_repository.get_by_email.return_value = other_user

        with pytest.raises(ConflictException):
            await user_service.update(user_id, update_data)

        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()
        mock_session.rollback.assert_not_called()

    async def test_update_raises_not_found(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "non-existent"
        update_data = UserUpdate(first_name="Johnny")
        mock_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await user_service.update(user_id, update_data)

        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()
        mock_session.rollback.assert_not_called()


class TestUserServiceDelete:
    """Pruebas unitarias para el método UserService.delete."""

    async def test_delete_calls_commit_on_success(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "user-123"
        existing_user = User(
            id=user_id,
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_by_id.return_value = existing_user

        await user_service.delete(user_id)

        mock_repository.delete.assert_called_once_with(existing_user)
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()

    async def test_delete_calls_rollback_on_error(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "user-123"
        existing_user = User(
            id=user_id,
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_by_id.return_value = existing_user
        mock_repository.delete.side_effect = Exception("DB error")

        with pytest.raises(DatabaseException, match="Database operation failed"):
            await user_service.delete(user_id)

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    async def test_delete_raises_not_found(
        self,
        user_service: UserService,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "non-existent"
        mock_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await user_service.delete(user_id)

        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_not_called()


class TestUserServiceRead:
    """Pruebas unitarias para los métodos de lectura de UserService."""

    async def test_get_by_id_returns_user(
        self,
        user_service: UserService,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "user-123"
        expected_user = User(
            id=user_id,
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_by_id.return_value = expected_user

        result = await user_service.get_by_id(user_id)

        assert result == expected_user
        assert result.id == user_id

    async def test_get_by_id_raises_not_found(
        self,
        user_service: UserService,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "non-existent"
        mock_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await user_service.get_by_id(user_id)

    async def test_get_detailed_returns_user(
        self,
        user_service: UserService,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "user-123"
        expected_user = User(
            id=user_id,
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_detailed.return_value = expected_user

        result = await user_service.get_detailed(user_id)

        assert result == expected_user

    async def test_get_detailed_raises_not_found(
        self,
        user_service: UserService,
        mock_repository: AsyncMock,
    ) -> None:
        user_id = "non-existent"
        mock_repository.get_detailed.return_value = None

        with pytest.raises(NotFoundException):
            await user_service.get_detailed(user_id)

    async def test_get_all_returns_paginated_response(
        self,
        user_service: UserService,
        mock_repository: AsyncMock,
    ) -> None:
        pagination = PaginationParams(offset=0, limit=10)
        expected_user = User(
            id="user-123",
            id_role=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        mock_repository.get_all.return_value = [expected_user]
        mock_repository.count.return_value = 1

        result = await user_service.get_all(pagination)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.total == 1
        assert isinstance(result.items[0], UserResponse)
        assert result.items[0].id == "user-123"
