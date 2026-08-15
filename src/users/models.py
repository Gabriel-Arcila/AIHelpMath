"""Módulo que define los modelos de base de datos para el usuario y su perfil de IA."""

import uuid

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class UserLevel(SQLModel, table=True):
    """Modelo de base de datos para los niveles de conocimiento (ej. Principiante,
    Intermedio).

    Atributos:
        id (int | None): Identificador único del nivel.
        name (str): Nombre del nivel (ej. 'PRINCIPIANTE' o 'INTERMEDIO').
        quantifier (int): Cuantificador del nivel (ej. 0, 1, 2, 3).
        description (str | None): Descripción opcional del nivel.
        user_ai_profiles (list[UserAIProfile]): Lista de perfiles de IA que poseen este
        nivel.
    """

    __tablename__ = "user_level"

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(unique=True, index=True, nullable=False)
    quantifier: int = Field(unique=True, nullable=False)
    description: str | None = Field(default=None)

    user_ai_profiles: list["UserAIProfile"] = Relationship(back_populates="user_level")


class UserTopic(SQLModel, table=True):
    """Modelo de base de datos para los temas de interés o favoritos.

    Atributos:
        id (int | None): Identificador único del tema.
        name (str): Nombre del tema (ej. 'ÁLGEBRA' o 'CÁLCULO').
        description (str | None): Descripción opcional del tema.
        user_ai_profiles (list[UserAIProfile]): Lista de perfiles de IA que poseen este
        tema.
    """

    __tablename__ = "user_topic"

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(unique=True, index=True, nullable=False)
    description: str | None = Field(default=None)

    user_ai_profiles: list["UserAIProfile"] = Relationship(back_populates="user_topic")


class UserAIProfile(SQLModel, table=True):
    """Modelo de base de datos para el perfil de inteligencia artificial del usuario.

    Atributos:
        id (int | None): Identificador único del perfil de IA.
        id_user (str): Identificador del usuario al cual pertenece el perfil.
        id_user_level (int): Identificador del nivel de conocimiento.
        id_user_topic (int): Identificador del tema de interés.
        description (str | None): Descripción opcional del perfil de IA.
        user (User | None): Relación con el modelo User principal.
        user_level (UserLevel | None): Relación con el modelo UserLevel.
        user_topic (UserTopic | None): Relación con el modelo UserTopic.
    """

    __tablename__ = "user_ai_profile"
    __table_args__ = (
        UniqueConstraint("id_user", "id_user_topic", name="unique_user_topic"),
    )

    id: int | None = Field(default=None, primary_key=True)
    id_user: str = Field(foreign_key="user.id", nullable=False)
    id_user_level: int = Field(foreign_key="user_level.id", nullable=False)
    id_user_topic: int = Field(foreign_key="user_topic.id", nullable=False)

    description: str | None = Field(default=None)

    user: "User" = Relationship(back_populates="user_ai_profiles")
    user_level: "UserLevel" = Relationship(back_populates="user_ai_profiles")
    user_topic: "UserTopic" = Relationship(back_populates="user_ai_profiles")


class UserRole(SQLModel, table=True):
    """Modelo de base de datos para los roles del sistema.

    Atributos:
        id (int | None): Identificador único del rol.
        name (str): Nombre del rol (ej. 'ESTUDIANTE' o 'ADMIN').
        description (str | None): Descripción opcional de los permisos del rol.
        users (list[User]): Lista de usuarios que poseen este rol.
    """

    __tablename__ = "user_role"

    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(unique=True, index=True, nullable=False)
    description: str | None = Field(default=None)

    users: list["User"] = Relationship(back_populates="user_role")


class User(SQLModel, table=True):
    """Modelo de base de datos para el usuario.

    Atributos:
        id (str): Identificador único del usuario (ej: 'user-123').
        id_role (int): Identificador del rol asignado.
        first_name (str): Nombre del usuario.
        last_name (str): Apellido del usuario.
        email (str): Correo electrónico del usuario.
        user_role (UserRole | None): Relación con el modelo UserRole.
        user_ai_profiles (list[UserAIProfile] | None): Relación con el modelo
        UserAIProfile.
    """

    __tablename__ = "user"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    id_role: int = Field(foreign_key="user_role.id", nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)

    user_role: UserRole = Relationship(back_populates="users")
    user_ai_profiles: list[UserAIProfile] = Relationship(back_populates="user")
