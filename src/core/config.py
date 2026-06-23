"""Configuración global de la aplicación.

Carga y valida las variables de entorno necesarias para el funcionamiento del sistema.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de la aplicación.

    Define las variables de entorno requeridas y sus valores por defecto.
    Soporta la lectura insensible a mayúsculas y minúsculas desde el archivo .env.

    Attributes:
        project_name (str): Nombre del proyecto.
        project_version (str): Versión del proyecto.
        database_url (str): URL de conexión a la base de datos.
        api_v1_str (str): Prefijo de ruta para la API v1.
    """

    project_name: str = "IAHelpMath"
    project_version: str = "0.1.0"
    database_url: str = "postgresql://user:password@localhost:5432/iahelpmath"
    api_v1_str: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
