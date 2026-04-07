"""
Módulo de inicialización de los esquemas (Pydantic) para la aplicación.
"""

from app.schemas.user import (
    UserCreate,
    UserDetailed,
    UserNivelCreate,
    UserNivelResponse,
    UserNivelUpdate,
    UserPerfilIACreate,
    UserPerfilIADetailed,
    UserPerfilIAResponse,
    UserPerfilIAUpdate,
    UserResponse,
    UserRolCreate,
    UserRolResponse,
    UserRolUpdate,
    UserTemaInteresCreate,
    UserTemaInteresResponse,
    UserTemaInteresUpdate,
    UserUpdate,
)

__all__ = [
    # UserRol
    "UserRolCreate",
    "UserRolUpdate",
    "UserRolResponse",
    # UserNivel
    "UserNivelCreate",
    "UserNivelUpdate",
    "UserNivelResponse",
    # UserTemaInteres
    "UserTemaInteresCreate",
    "UserTemaInteresUpdate",
    "UserTemaInteresResponse",
    # UserPerfilIA
    "UserPerfilIACreate",
    "UserPerfilIAUpdate",
    "UserPerfilIAResponse",
    "UserPerfilIADetailed",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserDetailed",
]
