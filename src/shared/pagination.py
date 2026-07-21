"""Esquemas y utilidades de paginación compartidas para los endpoints de la API."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Esquema genérico de respuesta paginada.

    Attributes:
        items (list[T]): Lista de elementos para la página actual.
        total (int): Número total de elementos en todas las páginas.
        limit (int): Número máximo de elementos por página.
        offset (int): Número de elementos omitidos desde el inicio.
    """

    items: list[T] = Field(..., description="List of items for the current page")
    total: int = Field(..., description="Total number of items across all pages")
    limit: int = Field(..., description="Maximum number of items per page")
    offset: int = Field(..., description="Number of items skipped from the start")


class PaginationParams(BaseModel):
    """Parámetros de consulta para la paginación.

    Attributes:
        offset (int): Número de elementos a omitir desde el inicio. Debe ser >= 0.
        limit (int): Número máximo de elementos por página. Debe estar entre 1 y 100.
    """

    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(
        default=10, ge=1, le=100, description="Maximum number of items per page"
    )
