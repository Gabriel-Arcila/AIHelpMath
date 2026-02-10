#Imagen Base
FROM python:3.11-slim

#Directorio de trabajo
WORKDIR /app

# Variables de entorno
# PYTHONDONTWRITEBYTECODE: Evita que Python genere archivos .pyc, manteniendo el contenedor limpio
#PYTHONUNBUFFERED: Asegura que los logs de tu aplicación se muestren en tiempo real en la consola, sin retrasos
#POETRY_VERSION: Fija la versión de Poetry en 1.7.1 para consistencia
#POETRY_HOME: Define la ruta base para Poetry
#POETRY_VIRTUALENVS_CREATE: Deshabilita la creación de entornos virtuales
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Esto asegura que poetry esté en el PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Instalar dependencias del sistema mínimas necesarias
# gcc: Compilador de C, necesario para algunas librerías de Python avanzadas.
# libpq-dev: Librería de desarrollo de PostgreSQL (necesaria si usas psycopg2).
# curl: Herramienta para descargar cosas (la usamos para bajar Poetry luego).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copiar archivos de definición de dependencias
COPY pyproject.toml poetry.lock ./

# Instalar dependencias (SIN instalar el proyecto raíz aún, para aprovechar caché)
RUN poetry install --no-root --no-interaction --no-ansi

# Copiar el resto del código
COPY . .

# Crea un punto de montaje para datos persistentes (por ejemplo, logs o subidas)
#VOLUME ["/app/data"]

# Crea un punto de montaje para la base de datos
#VOLUME ["/app/db"]

# Exponer el puerto (Informativo)
EXPOSE 8000

# Comando por defecto al ejecutar el contenedor
# Inicia el servidor servidor uvicorn
# buscando el objeto app dentro del archivo app/main.py
# --host 0.0.0.0: CRUCIAL. Le dice al servidor que acepte conexiones desde fuera del contenedor
# --port 8000: Puerto en el que escucha el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
