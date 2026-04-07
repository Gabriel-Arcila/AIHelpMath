"""
Esquemas Pydantic optimizados para la validación de entrada/salida.
Patrón simplificado: Create (Inserción pura), Update (Parcial), y Response (Lectura).
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==========================================
# ESQUEMAS PARA USER ROL
# ==========================================


class UserRolCreate(BaseModel):
    """Esquema para crear un Rol (Sin ID)."""

    nombre: str = Field(..., description="Nombre del rol")
    descripcion: str | None = Field(default=None, description="Descripción del rol")


class UserRolUpdate(BaseModel):
    """Esquema para actualizar un Rol."""

    nombre: str | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserRolResponse(UserRolCreate):
    """Esquema de respuesta (Con ID compatible con Base de Datos)."""

    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER NIVEL
# ==========================================


class UserNivelCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del nivel de conocimiento")
    cuantificador: int = Field(..., description="Valor numérico de lógica")
    descripcion: str | None = Field(default=None)


class UserNivelUpdate(BaseModel):
    nombre: str | None = Field(default=None)
    cuantificador: int | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserNivelResponse(UserNivelCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER TEMA INTERES
# ==========================================


class UserTemaInteresCreate(BaseModel):
    nombre: str = Field(..., description="Nombre del tema favorito")
    descripcion: str | None = Field(default=None)


class UserTemaInteresUpdate(BaseModel):
    nombre: str | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserTemaInteresResponse(UserTemaInteresCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER PERFIL IA
# ==========================================


class UserPerfilIACreate(BaseModel):
    id_user: str = Field(..., description="Identificador del usuario")
    id_user_nivel: int = Field(..., description="Identificador del nivel asociado")
    id_user_tema_interes: int = Field(
        ..., description="Identificador del tema asociado"
    )
    descripcion: str | None = Field(default=None)


class UserPerfilIAUpdate(BaseModel):
    id_user_nivel: int | None = Field(default=None)
    id_user_tema_interes: int | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserPerfilIAResponse(UserPerfilIACreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserPerfilIADetailed(UserPerfilIAResponse):
    """Respuesta del Perfil expandiendo los detalles de su Nivel y Tema."""

    user_nivel: UserNivelResponse
    user_tema_interes: UserTemaInteresResponse


# ==========================================
# ESQUEMAS PARA USER
# ==========================================


class UserCreate(BaseModel):
    id_rol: int = Field(..., description="Identificador del rol principal")
    nombre: str = Field(..., description="Nombres del usuario")
    apellido: str = Field(..., description="Apellidos del usuario")
    email: EmailStr = Field(..., description="Correo electrónico válido")


class UserUpdate(BaseModel):
    id_rol: int | None = Field(default=None)
    nombre: str | None = Field(default=None)
    apellido: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)


class UserResponse(UserCreate):
    id: str  # El ID es manejado y devuelto por la Base de Datos
    model_config = ConfigDict(from_attributes=True)


class UserDetailed(UserResponse):
    """Respuesta profunda con la información del Rol y todos los Perfiles IA."""

    user_rol: UserRolResponse
    user_perfiles_ia: list[UserPerfilIADetailed] = []
