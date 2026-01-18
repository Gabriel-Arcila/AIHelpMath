# IAHelpMath

Este es el backend para la aplicación IAHelpMath, construido con una arquitectura moderna y escalable.

## Estructura del Proyecto

- **app/**: Código fuente de la aplicación.
  - **api/**: Endpoints y rutas de la API.
  - **core/**: Configuración global y seguridad.
  - **db/**: Configuración de base de datos.
  - **models/**: Modelos de base de datos (SQLModel).
  - **schemas/**: Esquemas Pydantic para validación de datos.
  - **services/**: Lógica de negocio e integración con IA.
- **tests/**: Pruebas automatizadas.
- **docker-compose.yml**: Orquestación de servicios para desarrollo local.

## Configuración y Ejecución

### Requisitos previos

- Docker y Docker Compose
- Python 3.10+ (si se ejecuta localmente sin Docker)

### Ejecutar con Docker

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8000`.

### Desarrollo Local

1. Crear un entorno virtual: `python -m venv .venv`
2. Activar el entorno: `source .venv/bin/activate` (o `.venv\Scripts\activate` en Windows).
3. Instalar dependencias: `pip install -e .[dev]`
4. Ejecutar servidor: `uvicorn app.main:app --reload`
