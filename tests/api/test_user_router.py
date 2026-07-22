"""Pruebas de integración para los endpoints de la entidad User (Router HTTP)."""

from httpx import AsyncClient

from src.users.models import UserRole
from tests.api.conftest import create_test_user


class TestUserRouter:
    """Grupo de pruebas de integración para los endpoints de usuarios."""

    # -------------------------------------------------------------------------
    # POST /v1/users/
    # -------------------------------------------------------------------------

    async def test_create_user_returns_201(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que POST /v1/users/ crea un usuario y retorna status 201 Created."""
        # Arrange
        payload = {
            "id_role": seed_user_role.id,
            "first_name": "Test",
            "last_name": "User",
            "email": "test.user@example.com",
        }

        # Act
        response = await async_client.post("/v1/users/", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["email"] == "test.user@example.com"
        assert data["id_role"] == seed_user_role.id

    async def test_create_user_returns_422_invalid_email(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que POST /v1/users/ retorna 422 Unprocessable Entity
        si el email es inválido.
        """
        # Arrange
        payload = {
            "id_role": seed_user_role.id,
            "first_name": "Invalid",
            "last_name": "Email",
            "email": "not-an-email",
        }

        # Act
        response = await async_client.post("/v1/users/", json=payload)

        # Assert
        assert response.status_code == 422

    async def test_create_user_returns_409_duplicate_email(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que POST /v1/users/ retorna 409 Conflict y formato RFC 9457
        si el email ya existe.
        """
        # Arrange
        payload = {
            "id_role": seed_user_role.id,
            "first_name": "First",
            "last_name": "User",
            "email": "duplicate@example.com",
        }
        await async_client.post("/v1/users/", json=payload)

        # Act
        duplicate_payload = {
            "id_role": seed_user_role.id,
            "first_name": "Second",
            "last_name": "User",
            "email": "duplicate@example.com",
        }
        response = await async_client.post("/v1/users/", json=duplicate_payload)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data.get("status") == 409
        detail = data.get("detail", "").lower()
        assert "duplicate" in detail or "already exists" in detail
        assert "title" in data
        assert "type" in data
        assert "instance" in data

    # -------------------------------------------------------------------------
    # GET /v1/users/{user_id}
    # -------------------------------------------------------------------------

    async def test_get_user_returns_200(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que GET /v1/users/{user_id} retorna status 200 y el
        usuario correspondiente.
        """
        # Arrange
        user_data = {
            "first_name": "Get",
            "last_name": "User",
            "email": "get.user@example.com",
        }
        created = await create_test_user(async_client, user_data, seed_user_role.id)
        user_id = created["id"]

        # Act
        response = await async_client.get(f"/v1/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "get.user@example.com"

    async def test_get_user_returns_404_nonexistent(
        self, async_client: AsyncClient
    ) -> None:
        """Verifica que GET /v1/users/{user_id} retorna status 404 Not Found
        si el usuario no existe.
        """
        # Act
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(f"/v1/users/{non_existent_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data.get("status") == 404

    # -------------------------------------------------------------------------
    # GET /v1/users/{user_id}/detailed
    # -------------------------------------------------------------------------

    async def test_get_user_detailed_returns_200_with_role(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que GET /v1/users/{user_id}/detailed retorna UserDetailed
        con relaciones cargadas.
        """
        # Arrange
        user_data = {
            "first_name": "Detailed",
            "last_name": "Test",
            "email": "detailed.api@example.com",
        }
        created = await create_test_user(async_client, user_data, seed_user_role.id)
        user_id = created["id"]

        # Act
        response = await async_client.get(f"/v1/users/{user_id}/detailed")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert "user_role" in data
        assert data["user_role"]["id"] == seed_user_role.id
        assert data["user_role"]["name"] == "ESTUDIANTE"
        assert "user_ai_profiles" in data
        assert isinstance(data["user_ai_profiles"], list)

    async def test_get_user_detailed_returns_404_nonexistent(
        self, async_client: AsyncClient
    ) -> None:
        """Verifica que GET /v1/users/{user_id}/detailed retorna status 404
        si no existe el usuario.
        """
        # Act
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(f"/v1/users/{non_existent_id}/detailed")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data.get("status") == 404

    # -------------------------------------------------------------------------
    # GET /v1/users/?offset=0&limit=10
    # -------------------------------------------------------------------------

    async def test_list_users_returns_200_with_pagination(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que GET /v1/users/ retorna la estructura de PaginatedResponse."""
        # Arrange
        user_data = {
            "first_name": "List",
            "last_name": "User",
            "email": "list.user@example.com",
        }
        await create_test_user(async_client, user_data, seed_user_role.id)

        # Act
        response = await async_client.get("/v1/users/?offset=0&limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert data["offset"] == 0
        assert data["limit"] == 10
        assert isinstance(data["items"], list)
        assert data["total"] >= 1

    async def test_list_users_returns_200_empty(
        self, async_client: AsyncClient
    ) -> None:
        """Verifica que GET /v1/users/ retorna items vacíos y total 0 cuando
        no hay usuarios.
        """
        # Act
        response = await async_client.get("/v1/users/?offset=0&limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_users_respects_limit(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que el parámetro limit restrinja el número de items retornados."""
        # Arrange
        for i in range(3):
            await create_test_user(
                async_client,
                {
                    "first_name": f"User{i}",
                    "last_name": "LimitTest",
                    "email": f"limit{i}@example.com",
                },
                seed_user_role.id,
            )

        # Act
        response = await async_client.get("/v1/users/?offset=0&limit=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["limit"] == 2

    # -------------------------------------------------------------------------
    # PATCH /v1/users/{user_id}
    # -------------------------------------------------------------------------

    async def test_update_user_returns_200(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que PATCH /v1/users/{user_id} actualiza los campos especificados."""
        # Arrange
        created = await create_test_user(
            async_client,
            {
                "first_name": "Before",
                "last_name": "Update",
                "email": "before.update@example.com",
            },
            seed_user_role.id,
        )
        user_id = created["id"]

        # Act
        response = await async_client.patch(
            f"/v1/users/{user_id}",
            json={"first_name": "After"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "After"
        assert data["last_name"] == "Update"  # Permaneció intacto

    async def test_update_user_returns_404_nonexistent(
        self, async_client: AsyncClient
    ) -> None:
        """Verifica que PATCH /v1/users/{user_id} retorna 404 si el usuario
        no existe.
        """
        # Act
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.patch(
            f"/v1/users/{non_existent_id}",
            json={"first_name": "Ghost"},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data.get("status") == 404

    async def test_update_user_returns_409_duplicate_email(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que PATCH /v1/users/{user_id} retorna 409 si el nuevo email
        pertenece a otro usuario.
        """
        # Arrange
        await create_test_user(
            async_client,
            {
                "first_name": "UserOne",
                "last_name": "Test",
                "email": "user.one@example.com",
            },
            seed_user_role.id,
        )
        user2 = await create_test_user(
            async_client,
            {
                "first_name": "UserTwo",
                "last_name": "Test",
                "email": "user.two@example.com",
            },
            seed_user_role.id,
        )

        # Act - Intentar actualizar user2 con el email de user1
        response = await async_client.patch(
            f"/v1/users/{user2['id']}",
            json={"email": "user.one@example.com"},
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data.get("status") == 409

    # -------------------------------------------------------------------------
    # DELETE /v1/users/{user_id}
    # -------------------------------------------------------------------------

    async def test_delete_user_returns_204(
        self, async_client: AsyncClient, seed_user_role: UserRole
    ) -> None:
        """Verifica que DELETE /v1/users/{user_id} elimina el usuario y retorna
        status 204 No Content.
        """
        # Arrange
        created = await create_test_user(
            async_client,
            {
                "first_name": "Delete",
                "last_name": "Me",
                "email": "delete.me@example.com",
            },
            seed_user_role.id,
        )
        user_id = created["id"]

        # Act
        delete_response = await async_client.delete(f"/v1/users/{user_id}")

        # Assert
        assert delete_response.status_code == 204
        assert delete_response.text == ""

        # Verificar que ya no existe via GET
        get_response = await async_client.get(f"/v1/users/{user_id}")
        assert get_response.status_code == 404
