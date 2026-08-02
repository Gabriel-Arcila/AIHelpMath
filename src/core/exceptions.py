"""Definición de excepciones personalizadas y manejadores globales para la aplicación.
Sigue el estándar RFC 9457 (Problem Details para APIs HTTP).
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Excepción base para todos los errores de la aplicación.

    Args:
        detail (str): Mensaje descriptivo del error.
        status_code (int): Código de estado HTTP correspondiente.
    """

    def __init__(
        self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class NotFoundException(AppException):
    """Excepción lanzada cuando un recurso solicitado no es encontrado.

    Args:
        detail (str): Mensaje descriptivo de la ausencia del recurso.
    """

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    """Excepción lanzada cuando hay un conflicto con el estado actual del recurso.

    Args:
        detail (str): Mensaje descriptivo del conflicto.
    """

    def __init__(self, detail: str = "Request conflict") -> None:
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ValidationException(AppException):
    """Excepción lanzada cuando los datos de entrada fallan las validaciones de negocio.

    Args:
        detail (str): Mensaje descriptivo del error de validación.
    """

    def __init__(self, detail: str = "Data validation error") -> None:
        super().__init__(
            detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class DatabaseException(AppException):
    """Excepción lanzada cuando ocurre un error durante una operación de base de datos.

    Args:
        detail (str): Mensaje descriptivo del error de base de datos.
    """

    def __init__(self, detail: str = "Database operation failed") -> None:
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores de excepciones globales en la aplicación FastAPI.

    Args:
        app (FastAPI): Instancia de la aplicación a la cual registrar los manejadores.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Captura y maneja las excepciones del tipo AppException.

        Sigue el estándar RFC 9457.

        Args:
            request (Request): La solicitud HTTP que provocó el error.
            exc (AppException): La excepción capturada.

        Returns:
            JSONResponse: Respuesta JSON con el detalle del problema según RFC 9457.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "about:blank",
                "title": exc.__class__.__name__,
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url),
            },
        )
