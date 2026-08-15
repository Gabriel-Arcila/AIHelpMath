# Despliegue: Docker, Gunicorn y Producción

Referencia especializada para el despliegue de aplicaciones FastAPI
en entornos de producción.

## Tabla de contenidos

1. [Orquestación ASGI con Gunicorn](#1-orquestación-asgi-con-gunicorn)
2. [Configuración multi-núcleo](#2-configuración-multi-núcleo)
3. [Dockerfile optimizado](#3-dockerfile-optimizado)
4. [Docker Compose](#4-docker-compose)
5. [Señales POSIX y graceful shutdown](#5-señales-posix-y-graceful-shutdown)
6. [Variables de entorno en producción](#6-variables-de-entorno-en-producción)

---

## 1. Orquestación ASGI con Gunicorn

En producción, Uvicorn no se ejecuta solo. Se utiliza **Gunicorn**
como gestor de procesos que engendra múltiples workers de Uvicorn.
Gunicorn supervisa los procesos, los reinicia si fallan y distribuye
las conexiones.

```bash
gunicorn src.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile -
```

La razón de usar Gunicorn como proceso padre es que proporciona:
- Supervisión y reinicio automático de workers caídos.
- Gestión de señales POSIX para shutdown ordenado.
- Pre-fork de workers para maximizar el rendimiento.
- Protección contra fugas de memoria con `max-requests`.

---

## 2. Configuración multi-núcleo

La regla clásica de `2 × N_CPU + 1` workers está obsoleta para
aplicaciones ASGI asíncronas. Cada worker de Uvicorn ya gestiona
miles de conexiones concurrentes mediante el bucle de eventos.

**Recomendación:** Un worker por núcleo de CPU.

```bash
# Para un servidor de 4 núcleos
--workers 4
```

Agregar más workers que núcleos físicos causa contención de CPU
entre workers, overhead de cambio de contexto del sistema operativo,
y degradación del rendimiento por competencia de recursos.

### Parámetros de producción recomendados

| Parámetro | Valor | Razón |
|---|---|---|
| `--workers` | 1 por CPU | Evita contención |
| `--timeout` | 120 | Tiempo máximo de respuesta |
| `--graceful-timeout` | 30 | Tiempo para cerrar conexiones |
| `--max-requests` | 10000 | Recicla workers (previene memory leaks) |
| `--max-requests-jitter` | 1000 | Evita reinicio simultáneo |

---

## 3. Dockerfile optimizado

La topología de la imagen Docker separa la instalación de
dependencias (capa inmutable y cacheable) de la copia del código
fuente (capa que cambia frecuentemente).

```dockerfile
# --- Etapa 1: Dependencias ---
FROM python:3.12-slim AS dependencies

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar SOLO los archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalar dependencias Python
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev

# --- Etapa 2: Aplicación ---
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=dependencies /app/.venv /app/.venv

# Copiar código fuente
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Configurar el PATH para el entorno virtual
ENV PATH="/app/.venv/bin:$PATH"

# Usuario no-root por seguridad
RUN useradd --create-home appuser
USER appuser

# Exponer puerto
EXPOSE 8000

# CMD en formato JSON (exec form)
CMD ["gunicorn", "src.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-"]
```

### Reglas del Dockerfile

1. **Multi-stage builds**: Separar dependencias de código.
2. **`--no-cache-dir`**: No almacenar caché de pip en la imagen.
3. **Copiar dependencias antes que código**: Aprovecha la caché de
   capas de Docker. Si solo cambia el código, no se reinstalan
   las dependencias.
4. **CMD en formato JSON**: El formato `CMD ["..."]` (exec form)
   ejecuta el proceso directamente sin shell intermedio. Esto es
   crítico porque garantiza que las señales del sistema (como
   `SIGTERM`) lleguen directamente al proceso de Gunicorn, no a
   un shell padre que las ignora.
5. **Usuario no-root**: Ejecutar como usuario sin privilegios por
   seguridad.

---

## 4. Docker Compose

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Buenas prácticas de Docker Compose

- Usar `depends_on` con `condition: service_healthy` para esperar
  a que la base de datos esté lista.
- No incluir volúmenes de código en producción (solo en desarrollo).
- Definir `restart: unless-stopped` para resiliencia.
- Usar variables de entorno desde `.env` con `env_file`.

---

## 5. Señales POSIX y graceful shutdown

### El problema del shell form

```dockerfile
# ❌ Shell form — señales no llegan al proceso
CMD gunicorn src.main:app --workers 4

# ✅ Exec form — señales llegan directamente
CMD ["gunicorn", "src.main:app", "--workers", "4"]
```

Con shell form, Docker envía `SIGTERM` al proceso shell (`/bin/sh`),
no a Gunicorn. El shell ignora la señal y Gunicorn nunca se entera
de que debe cerrar. Después del timeout (10 segundos por defecto),
Docker envía `SIGKILL`, matando el proceso abruptamente. Esto causa
conexiones cortadas, transacciones incompletas y pérdida de datos.

### Shutdown ordenado en FastAPI

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.

    Inicio: Inicializa pools de conexiones, caches, etc.
    Cierre: Cierra conexiones, guarda estado, limpia recursos.
    """
    # Inicio
    print("Iniciando aplicación...")
    yield
    # Cierre (se ejecuta al recibir SIGTERM)
    print("Cerrando conexiones...")
    await engine.dispose()
```

El `lifespan` context manager de FastAPI es el lugar correcto para
el código de cleanup porque se ejecuta cuando Uvicorn recibe la
señal de terminación. Esto garantiza un cierre ordenado de las
conexiones de base de datos, caches y otros recursos.

---

## 6. Variables de entorno en producción

### .env.example

Incluir un archivo `.env.example` documentado en el repositorio.
**Nunca** incluir `.env` real en el control de versiones.

```env
# Base de datos
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DATABASE_READ_URL=postgresql+asyncpg://user:password@read-replica:5432/dbname

# Seguridad
SECRET_KEY=cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Aplicación
APP_NAME=FastAPI App
DEBUG=false

# Base de datos de test
TEST_DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test_db
```

### .gitignore

```gitignore
.env
*.pyc
__pycache__/
.venv/
```
