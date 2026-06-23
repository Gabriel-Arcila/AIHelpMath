"""Esquemas Pydantic optimizados para la validación de entrada/salida de usuarios.

Sigue el patrón simplificado de Create (inserción pura), Update (parcial),
y Response (lectura).
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ==========================================
# ESQUEMAS PARA USER ROL
# ==========================================


class UserRolCreate(BaseModel):
    """Esquema para la creación de un Rol.

    Attributes:
        nombre (str): Nombre del rol (ej. 'ESTUDIANTE').
        descripcion (str | None): Descripción opcional de las funciones del rol.
    """

    nombre: str = Field(..., description="Nombre del rol")
    descripcion: str | None = Field(default=None, description="Descripción del rol")


class UserRolUpdate(BaseModel):
    """Esquema para la actualización de un Rol.

    Attributes:
        nombre (str | None): Nuevo nombre para el rol.
        descripcion (str | None): Nueva descripción para el rol.
    """

    nombre: str | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserRolResponse(UserRolCreate):
    """Esquema de respuesta de un Rol.

    Attributes:
        id (int): Identificador único del rol.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER NIVEL
# ==========================================


class UserNivelCreate(BaseModel):
    """Esquema para la creación de un Nivel de conocimiento.

    Attributes:
        nombre (str): Nombre del nivel de conocimiento (ej. 'PRINCIPIANTE').
        cuantificador (int): Valor numérico asignado al nivel.
        descripcion (str | None): Descripción opcional del nivel.
    """

    nombre: str = Field(..., description="Nombre del nivel de conocimiento")
    cuantificador: int = Field(..., description="Valor numérico de lógica")
    descripcion: str | None = Field(default=None)


class UserNivelUpdate(BaseModel):
    """Esquema para la actualización de un Nivel de conocimiento.

    Attributes:
        nombre (str | None): Nuevo nombre del nivel de conocimiento.
        cuantificador (int | None): Nuevo valor numérico del nivel.
        descripcion (str | None): Nueva descripción del nivel.
    """

    nombre: str | None = Field(default=None)
    cuantificador: int | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserNivelResponse(UserNivelCreate):
    """Esquema de respuesta de un Nivel de conocimiento.

    Attributes:
        id (int): Identificador único del nivel de conocimiento.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER TEMA INTERES
# ==========================================


class UserTemaInteresCreate(BaseModel):
    """Esquema para la creación de un Tema de interés.

    Attributes:
        nombre (str): Nombre del tema favorito (ej. 'ÁLGEBRA').
        descripcion (str | None): Descripción opcional del tema de interés.
    """

    nombre: str = Field(..., description="Nombre del tema favorito")
    descripcion: str | None = Field(default=None)


class UserTemaInteresUpdate(BaseModel):
    """Esquema para la actualización de un Tema de interés.

    Attributes:
        nombre (str | None): Nuevo nombre del tema de interés.
        descripcion (str | None): Nueva descripción del tema de interés.
    """

    nombre: str | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserTemaInteresResponse(UserTemaInteresCreate):
    """Esquema de respuesta de un Tema de interés.

    Attributes:
        id (int): Identificador único del tema de interés.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ESQUEMAS PARA USER PERFIL IA
# ==========================================


class UserPerfilIACreate(BaseModel):
    """Esquema para la creación de un Perfil IA de usuario.

    Attributes:
        id_user (str): Identificador único del usuario asociado.
        id_user_nivel (int): Identificador único del nivel asociado.
        id_user_tema_interes (int): Identificador único del tema asociado.
        descripcion (str | None): Descripción opcional del perfil.
    """

    id_user: str = Field(..., description="Identificador del usuario")
    id_user_nivel: int = Field(..., description="Identificador del nivel asociado")
    id_user_tema_interes: int = Field(
        ..., description="Identificador del tema asociado"
    )
    descripcion: str | None = Field(default=None)


class UserPerfilIAUpdate(BaseModel):
    """Esquema para la actualización de un Perfil IA de usuario.

    Attributes:
        id_user_nivel (int | None): Nuevo identificador de nivel.
        id_user_tema_interes (int | None): Nuevo identificador de tema de interés.
        descripcion (str | None): Nueva descripción para el perfil.
    """

    id_user_nivel: int | None = Field(default=None)
    id_user_tema_interes: int | None = Field(default=None)
    descripcion: str | None = Field(default=None)


class UserPerfilIAResponse(UserPerfilIACreate):
    """Esquema de respuesta de un Perfil IA de usuario.

    Attributes:
        id (int): Identificador único del perfil IA.
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class UserPerfilIADetailed(UserPerfilIAResponse):
    """Esquema de respuesta detallado de un Perfil IA.

    Incluye la expansión completa del nivel y tema de interés relacionados.

    Attributes:
        user_nivel (UserNivelResponse): Objeto de respuesta del nivel.
        user_tema_interes (UserTemaInteresResponse): Objeto de respuesta del tema.
    """

    user_nivel: UserNivelResponse
    user_tema_interes: UserTemaInteresResponse


# ==========================================
# ESQUEMAS PARA USER
# ==========================================


class UserCreate(BaseModel):
    """Esquema para la creación de un Usuario.

    Attributes:
        id_rol (int): Identificador único del rol asignado.
        nombre (str): Nombre o nombres del usuario.
        apellido (str): Apellido o apellidos del usuario.
        email (EmailStr): Correo electrónico válido del usuario.
    """

    id_rol: int = Field(..., description="Identificador del rol principal")
    nombre: str = Field(..., description="Nombres del usuario")
    apellido: str = Field(..., description="Apellidos del usuario")
    email: EmailStr = Field(..., description="Correo electrónico válido")


class UserUpdate(BaseModel):
    """Esquema para la actualización parcial de un Usuario.

    Attributes:
        id_rol (int | None): Nuevo identificador del rol.
        nombre (str | None): Nuevo nombre del usuario.
        apellido (str | None): Nuevo apellido del usuario.
        email (EmailStr | None): Nuevo correo electrónico.
    """

    id_rol: int | None = Field(default=None)
    nombre: str | None = Field(default=None)
    apellido: str | None = Field(default=None)
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
        user_rol (UserRolResponse): Objeto de respuesta del rol.
        user_perfiles_ia (list[UserPerfilIADetailed]): Lista de perfiles IA del usuario.
    """

    user_rol: UserRolResponse
    user_perfiles_ia: list[UserPerfilIADetailed] = []
