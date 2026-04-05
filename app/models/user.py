"""
Módulo que define los modelos de base de datos para el usuario y su perfil de IA.
"""

import uuid

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class UserNivel(SQLModel, table=True):
    """
    Modelo de base de datos para los niveles de conocimiento (ej. Principiante,
    Intermedio).

    Atributos:
        id (int | None): Identificador único del nivel.
        nombre (str): Nombre del nivel (ej. 'PRINCIPIANTE' o 'INTERMEDIO').
        cuantificador (int): Cuantificador del nivel (ej. 0, 1, 2, 3).
        descripcion (str | None): Descripción opcional del nivel.
        user_perfiles_ia (list[UserPerfilIA]): Lista de perfiles de IA que poseen este
        nivel.
    """

    __tablename__ = "user_nivel"

    id: int | None = Field(default=None, primary_key=True)

    nombre: str = Field(unique=True, index=True, nullable=False)
    cuantificador: int = Field(unique=True, nullable=False)
    descripcion: str | None = Field(default=None)

    user_perfiles_ia: list["UserPerfilIA"] = Relationship(back_populates="user_nivel")


class UserTemaInteres(SQLModel, table=True):
    """
    Modelo de base de datos para los temas de interés o favoritos.

    Atributos:
        id (int | None): Identificador único del tema.
        nombre (str): Nombre del tema (ej. 'ÁLGEBRA' o 'CÁLCULO').
        descripcion (str | None): Descripción opcional del tema.
        user_perfiles_ia (list[UserPerfilIA]): Lista de perfiles de IA que poseen este
        tema.
    """

    __tablename__ = "user_tema_interes"

    id: int | None = Field(default=None, primary_key=True)

    nombre: str = Field(unique=True, index=True, nullable=False)
    descripcion: str | None = Field(default=None)

    user_perfiles_ia: list["UserPerfilIA"] = Relationship(
        back_populates="user_tema_interes"
    )


class UserPerfilIA(SQLModel, table=True):
    """
    Modelo de base de datos para el perfil de inteligencia artificial del usuario.

    Atributos:
        id (int | None): Identificador único del perfil de IA.
        id_user (str): Identificador del usuario al cual pertenece el perfil.
        id_user_nivel (int): Identificador del nivel de conocimiento.
        id_user_tema_interes (int): Identificador del tema de interés.
        descripcion (str | None): Descripción opcional del perfil de IA.
        user (User | None): Relación con el modelo User principal.
        user_nivel (UserNivel | None): Relación con el modelo UserNivel.
        user_tema_interes (UserTemaInteres | None): Relación con el modelo
        UserTemaInteres.
    """

    __tablename__ = "user_perfil_ia"
    __table_args__ = (
        UniqueConstraint("id_user", "id_user_tema_interes", name="unique_user_tema"),
    )

    id: int | None = Field(default=None, primary_key=True)
    id_user: str = Field(foreign_key="user.id", nullable=False)
    id_user_nivel: int = Field(foreign_key="user_nivel.id", nullable=False)
    id_user_tema_interes: int = Field(
        foreign_key="user_tema_interes.id", nullable=False
    )

    descripcion: str | None = Field(default=None)

    user: "User" = Relationship(back_populates="user_perfiles_ia")
    user_nivel: "UserNivel" = Relationship(back_populates="user_perfiles_ia")
    user_tema_interes: "UserTemaInteres" = Relationship(
        back_populates="user_perfiles_ia"
    )


class UserRol(SQLModel, table=True):
    """
    Modelo de base de datos para los roles del sistema.

    Atributos:
        id (int | None): Identificador único del rol.
        nombre (str): Nombre del rol (ej. 'ESTUDIANTE' o 'ADMIN').
        descripcion (str | None): Descripción opcional de los permisos del rol.
        usuarios (list[User]): Lista de usuarios que poseen este rol.
    """

    __tablename__ = "user_rol"

    id: int | None = Field(default=None, primary_key=True)

    nombre: str = Field(unique=True, index=True, nullable=False)
    descripcion: str | None = Field(default=None)

    usuarios: list["User"] = Relationship(back_populates="user_rol")


class User(SQLModel, table=True):
    """
    Modelo de base de datos para el usuario.

    Atributos:
        id (str): Identificador único del usuario (ej: 'user-123').
        id_rol (int): Identificador del rol asignado.
        nombre (str): Nombre del usuario.
        apellido (str): Apellido del usuario.
        email (str): Correo electrónico del usuario.
        user_rol (UserRol | None): Relación con el modelo UserRol.
        user_perfiles_ia (list[UserPerfilIA] | None): Relación con el modelo
        UserPerfilIA.
    """

    __tablename__ = "user"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    id_rol: int = Field(foreign_key="user_rol.id", nullable=False)
    nombre: str = Field(nullable=False)
    apellido: str = Field(nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)

    user_rol: UserRol = Relationship(back_populates="usuarios")
    user_perfiles_ia: list[UserPerfilIA] = Relationship(back_populates="user")
