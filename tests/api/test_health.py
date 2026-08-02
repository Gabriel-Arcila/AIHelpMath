"""Tests de integración para el endpoint de estado de salud (/health)."""

from httpx import AsyncClient


class TestHealthCheck:
    """Grupo de pruebas para la ruta /health."""

    async def test_health_check_returns_200(self, async_client: AsyncClient) -> None:
        """Verifica que el endpoint /health responda 200 OK con el status correcto."""
        # Act
        response = await async_client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
