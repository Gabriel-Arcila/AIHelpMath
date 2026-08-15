"""Tests unitarios para la lógica de paginación en src/shared/pagination.py."""

import pytest
from pydantic import ValidationError

from src.shared.pagination import PaginationParams


class TestPaginationParams:
    """Grupo de pruebas para los parámetros de paginación."""

    def test_default_values(self) -> None:
        """Verifica los valores por defecto de PaginationParams."""
        params = PaginationParams()
        assert params.offset == 0
        assert params.limit == 10

    def test_valid_custom_values(self) -> None:
        """Verifica que se acepten valores personalizados dentro del rango válido."""
        params = PaginationParams(offset=20, limit=50)
        assert params.offset == 20
        assert params.limit == 50

    def test_offset_negative_raises_validation_error(self) -> None:
        """Verifica que un offset negativo lance un ValidationError."""
        with pytest.raises(ValidationError):
            PaginationParams(offset=-1)

    def test_limit_zero_raises_validation_error(self) -> None:
        """Verifica que un limit igual a cero lance un ValidationError."""
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)

    def test_limit_exceeds_max_raises_validation_error(self) -> None:
        """Verifica que un limit mayor a 100 lance un ValidationError."""
        with pytest.raises(ValidationError):
            PaginationParams(limit=101)
