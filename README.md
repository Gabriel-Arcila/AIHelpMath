# IAHelpMath



## Estructura del Proyecto

  - 📁 **app/** *(Código fuente principal de la API)*
    - 📄 `__init__.py`
    - 📄 `main.py` *(Punto de entrada y configuración de la instancia FastAPI)*
    - 📁 **api/** *(Enrutadores y Endpoints)*
      - 📄 `dependencies.py` *(Dependencias inyectables, ej. get_db_session)*
      - 📁 **v1/** *(Versionado de la API)*
          - 📄 `file.py`
    - 📁 **core/** *(Configuraciones globales)*
      - 📄 `config.py` *(Carga de variables de entorno con pydantic-settings)*
      - 📄 `security.py` *(Lógica de hashing y tokens JWT)*
    - 📁 **crud/** *(Operaciones de Base de Datos - Create, Read, Update, Delete)*
      - 📄 `file.py`
    - 📁 **db/** *(Configuración del motor de Base de Datos)*
      - 📄 `file.py` *(Conexión SQLAlchemy)*
    - 📁 **models/** *(Modelos ORM - Tablas de la base de datos)*
      - 📄 `file.py` *(Clases de SQLAlchemy)*
    - 📁 **schemas/** *(Modelos Pydantic - Validación de entrada/salida)*
      - 📄 `file.py`
    - 📁 **services/** *(lgica de servicios)*
       - 📄 `file.py`
  - 📁 **tests/** *(Directorio exclusivo para pruebas con pytest)*
    - 📄 `__init__.py`
    - 📄 `conftest.py` *(Fixtures de Pytest, cliente de prueba, BD de prueba)*
    - 📁 **api/** *(Pruebas e2e de los endpoints)*
      - 📄 `files.py`
    - 📁 **crud/** *(Pruebas de integración para las funciones CRUD)*
      - 📄 `files.py`
  - ⚙️ `pyproject.toml` *(Gestión de dependencias)*
  - ⚙️ `.dockerignore`
  - ⚙️ `.gitignore`
  - ⚙️ `docker-compose.yml`
  - ⚙️ `Dockerfile`
  - ⚙️ `uv.lock`
  - 📄 `AGENTS.md`
  - 📄 `README.md`

## Configuración y Ejecución

### Requisitos previos

- Docker y Docker Compose
- Python 3.10+ (si se ejecuta localmente sin Docker)

### Desarrollo Local

1. Crear un entorno virtual: `python -m venv .venv`
2. Activar el entorno: `source .venv/bin/activate` (o `.venv\Scripts\activate` en Windows).
3. Instalar dependencias: `pip install -e .[dev]`
4. Ejecutar servidor: `uvicorn app.main:app --reload`
