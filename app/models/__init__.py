"""
Módulo de inicialización de los modelos de base de datos.
"""

from app.models.user import (
    User,
    UserNivel,
    UserPerfilIA,
    UserRol,
    UserTemaInteres,
)

__all__ = ["User", "UserPerfilIA", "UserRol", "UserNivel", "UserTemaInteres"]
