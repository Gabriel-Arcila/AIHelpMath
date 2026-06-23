"""Inicialización del módulo de dominio de usuarios."""

from src.users.models import (
    User,
    UserNivel,
    UserPerfilIA,
    UserRol,
    UserTemaInteres,
)
from src.users.schemas import (
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
    # Modelos
    "User",
    "UserNivel",
    "UserPerfilIA",
    "UserRol",
    "UserTemaInteres",
    # Schemas
    "UserCreate",
    "UserDetailed",
    "UserNivelCreate",
    "UserNivelResponse",
    "UserNivelUpdate",
    "UserPerfilIACreate",
    "UserPerfilIADetailed",
    "UserPerfilIAResponse",
    "UserPerfilIAUpdate",
    "UserResponse",
    "UserRolCreate",
    "UserRolResponse",
    "UserRolUpdate",
    "UserTemaInteresCreate",
    "UserTemaInteresResponse",
    "UserTemaInteresUpdate",
    "UserUpdate",
]
