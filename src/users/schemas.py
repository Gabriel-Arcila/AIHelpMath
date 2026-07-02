"""Esquemas Pydantic optimizados para la validación de entrada/salida de usuarios.

Sigue el patrón simplificado de Create (inserción pura), Update (parcial),
y Response (lectura).
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ==========================================
# ESQUEMAS PARA USER ROLE
# ==========================================


class UserRoleCreate(BaseModel):
    """Esquema para la creación de un Rol.

    Attributes:
        name (str): Nombre del rol (ej. 'ESTUDIANTE').
        description (str | None): Descripción opcional de las funciones del rol.
    """

    name: str = Field(..., description="Role name")
    description: str | None = Field(default=None, description="Role description")


class UserRoleUpdate(BaseModel):
    """Esquema para la actualización de un Rol.

    Attributes:
        name (str | None): Nuevo nombre para el rol.
        description (str | None): Nueva descripción para el rol.
    """

    name: str | None = Field(default=None)
    description: str | None = Field(default=None)


class UserRoleResponse(UserRoleCreate):
    """Esquema de respuesta de un Rol.

    Attributes:
        id (int): Identificador único del rol.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER LEVEL
# ==========================================


class UserLevelCreate(BaseModel):
    """Esquema para la creación de un Nivel de conocimiento.

    Attributes:
        name (str): Nombre del nivel de conocimiento (ej. 'PRINCIPIANTE').
        quantifier (int): Valor numérico asignado al nivel.
        description (str | None): Descripción opcional del nivel.
    """

    name: str = Field(..., description="Knowledge level name")
    quantifier: int = Field(..., description="Numeric quantifier value")
    description: str | None = Field(default=None)


class UserLevelUpdate(BaseModel):
    """Esquema para la actualización de un Nivel de conocimiento.

    Attributes:
        name (str | None): Nuevo nombre del nivel de conocimiento.
        quantifier (int | None): Nuevo valor numérico del nivel.
        description (str | None): Nueva descripción del nivel.
    """

    name: str | None = Field(default=None)
    quantifier: int | None = Field(default=None)
    description: str | None = Field(default=None)


class UserLevelResponse(UserLevelCreate):
    """Esquema de respuesta de un Nivel de conocimiento.

    Attributes:
        id (int): Identificador único del nivel de conocimiento.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER TOPIC
# ==========================================


class UserTopicCreate(BaseModel):
    """Esquema para la creación de un Tema de interés.

    Attributes:
        name (str): Nombre del tema favorito (ej. 'ÁLGEBRA').
        description (str | None): Descripción opcional del tema de interés.
    """

    name: str = Field(..., description="Topic name")
    description: str | None = Field(default=None)


class UserTopicUpdate(BaseModel):
    """Esquema para la actualización de un Tema de interés.

    Attributes:
        name (str | None): Nuevo nombre del tema de interés.
        description (str | None): Nueva descripción del tema de interés.
    """

    name: str | None = Field(default=None)
    description: str | None = Field(default=None)


class UserTopicResponse(UserTopicCreate):
    """Esquema de respuesta de un Tema de interés.

    Attributes:
        id (int): Identificador único del tema de interés.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER AI PROFILE
# ==========================================


class UserAIProfileCreate(BaseModel):
    """Esquema para la creación de un Perfil IA de usuario.

    Attributes:
        id_user (str): Identificador único del usuario asociado.
        id_user_level (int): Identificador único del nivel asociado.
        id_user_topic (int): Identificador único del tema asociado.
        description (str | None): Descripción opcional del perfil.
    """

    id_user: str = Field(..., description="User identifier")
    id_user_level: int = Field(..., description="Associated level identifier")
    id_user_topic: int = Field(..., description="Associated topic identifier")
    description: str | None = Field(default=None)


class UserAIProfileUpdate(BaseModel):
    """Esquema para la actualización de un Perfil IA de usuario.

    Attributes:
        id_user_level (int | None): Nuevo identificador de nivel.
        id_user_topic (int | None): Nuevo identificador de tema de interés.
        description (str | None): Nueva descripción para el perfil.
    """

    id_user_level: int | None = Field(default=None)
    id_user_topic: int | None = Field(default=None)
    description: str | None = Field(default=None)


class UserAIProfileResponse(UserAIProfileCreate):
    """Esquema de respuesta de un Perfil IA de usuario.

    Attributes:
        id (int): Identificador único del perfil IA.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class UserAIProfileDetailed(UserAIProfileResponse):
    """Esquema de respuesta detallado de un Perfil IA.

    Incluye la expansión completa del nivel y tema de interés relacionados.

    Attributes:
        user_level (UserLevelResponse): Objeto de respuesta del nivel.
        user_topic (UserTopicResponse): Objeto de respuesta del tema.
    """

    user_level: UserLevelResponse
    user_topic: UserTopicResponse


# ==========================================
# ESQUEMAS PARA USER
# ==========================================


class UserCreate(BaseModel):
    """Esquema para la creación de un Usuario.

    Attributes:
        id_role (int): Identificador único del rol asignado.
        first_name (str): Nombre o nombres del usuario.
        last_name (str): Apellido o apellidos del usuario.
        email (EmailStr): Correo electrónico válido del usuario.
    """

    id_role: int = Field(..., description="Primary role identifier")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    email: EmailStr = Field(..., description="Valid email address")


class UserUpdate(BaseModel):
    """Esquema para la actualización parcial de un Usuario.

    Attributes:
        id_role (int | None): Nuevo identificador del rol.
        first_name (str | None): Nuevo nombre del usuario.
        last_name (str | None): Nuevo apellido del usuario.
        email (EmailStr | None): Nuevo correo electrónico.
    """

    id_role: int | None = Field(default=None)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)


class UserResponse(UserCreate):
    """Esquema de respuesta básico de un Usuario.

    Attributes:
        id (str): Identificador único en formato UUID asignado al usuario.
    """

    id: str
    model_config = ConfigDict(from_attributes=True)


class UserDetailed(UserResponse):
    """Esquema de respuesta detallado de un Usuario.

    Incluye la información completa del rol y todos sus perfiles IA asociados.

    Attributes:
        user_role (UserRoleResponse): Objeto de respuesta del rol.
        user_ai_profiles (list[UserAIProfileDetailed]): Lista de perfiles IA
            del usuario.
    """

    user_role: UserRoleResponse
    user_ai_profiles: list[UserAIProfileDetailed] = []
