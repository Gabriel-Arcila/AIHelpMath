#Imagen Base
FROM python:3.11-slim

#Directorio de trabajo
WORKDIR /app

# Variables de entorno
# PYTHONDONTWRITEBYTECODE: Evita que Python genere archivos .pyc, manteniendo el contenedor limpio
# PYTHONUNBUFFERED: Asegura que los logs de tu aplicación se muestren en tiempo real
# UV_PROJECT_ENVIRONMENT: Ubicación del entorno virtual para evitar que choque con montajes locales de Windows
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Instalar dependencias del sistema mínimas necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv de manera compatible con cualquier arquitectura
RUN pip install uv

# Copiar archivos de definición de dependencias
COPY pyproject.toml uv.lock* ./

# Instalar dependencias (SIN instalar el proyecto raíz aún, para aprovechar caché de Docker)
RUN uv sync --no-dev --no-install-project

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
