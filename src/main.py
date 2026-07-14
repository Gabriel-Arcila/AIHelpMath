"""Punto de entrada de la aplicación FastAPI.

Configura el ciclo de vida de la aplicación, los manejadores de excepciones
globales y registra los routers de los diferentes módulos de dominio.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from src.core.config import settings
from src.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestión del ciclo de vida de la aplicación.

    Inicializa los recursos al arrancar el servidor y los libera al cerrarlo.

    Args:
        app (FastAPI): Instancia de la aplicación FastAPI.
    """
    # Lógica de inicio (startup)
    yield
    # Lógica de cierre (shutdown)


app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    lifespan=lifespan,
)

# Registro de manejadores de excepciones globales (RFC 9457)
register_exception_handlers(app)




@app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
async def health_check() -> dict[str, str]:
    """Endpoint para verificación del estado de salud de la aplicación.

    Returns:
        dict[str, str]: Estado de salud de la aplicación.
    """
    return {"status": "healthy"}
