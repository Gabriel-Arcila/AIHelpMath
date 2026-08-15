"""Tests unitarios para las excepciones personalizadas y el handler RFC 9457."""

from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from src.core.exceptions import (
    AppException,
    ConflictException,
    DatabaseException,
    NotFoundException,
    ValidationException,
    register_exception_handlers,
)


class TestAppExceptions:
    """Grupo de pruebas para las excepciones personalizadas."""

    def test_app_exception_default_status_code(self) -> None:
        """Verifica los valores por defecto de AppException."""
        exc = AppException(detail="Test error")
        assert exc.detail == "Test error"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_not_found_exception_status_code(self) -> None:
        """Verifica el código de estado de NotFoundException."""
        exc = NotFoundException()
        assert exc.detail == "Resource not found"
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_conflict_exception_status_code(self) -> None:
        """Verifica el código de estado de ConflictException."""
        exc = ConflictException()
        assert exc.detail == "Request conflict"
        assert exc.status_code == status.HTTP_409_CONFLICT

    def test_validation_exception_status_code(self) -> None:
        """Verifica el código de estado de ValidationException."""
        exc = ValidationException()
        assert exc.detail == "Data validation error"
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_database_exception_status_code(self) -> None:
        """Verifica el código de estado de DatabaseException."""
        exc = DatabaseException()
        assert exc.detail == "Database operation failed"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_exception_handler_returns_rfc9457_format(self) -> None:
        """Verifica que el manejador global devuelva el formato RFC 9457."""
        test_app = FastAPI()
        register_exception_handlers(test_app)

        @test_app.get("/test-error")
        async def trigger_error() -> None:
            raise NotFoundException(detail="Custom resource not found")

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.get("/test-error")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["type"] == "about:blank"
        assert data["title"] == "NotFoundException"
        assert data["status"] == 404
        assert data["detail"] == "Custom resource not found"
        assert "instance" in data
