FROM python:3.11-slim

WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Configuración de Poetry
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Esto asegura que poetry esté en el PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Instalar dependencias del sistema mínimas necesarias
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

# Exponer el puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
