# IAHelpMath

## Misión

_Define la razón de ser del proyecto. Es la referencia que decide si una feature "encaja" o no._

### Qué construimos

**MathIA** es una plataforma web educativa impulsada por inteligencia artificial que ayuda a estudiantes a comprender, practicar y dominar las ciencias matemáticas (álgebra, cálculo, geometría) de forma personalizada e interactiva, reemplazando las explicaciones estáticas por retroalimentación dinámica y paso a paso.

_Las piezas principales del producto:_

1. **Backend API (FastAPI)** — API REST asíncrona que gestiona usuarios, autenticación, sesiones de chat con IA (LangChain + OpenAI), progreso de aprendizaje y ejercicios interactivos. Sigue una arquitectura DDD por capas (Router → Service → Repository) con PostgreSQL async.
2. **Tutor IA (LangChain)** — Motor de inteligencia artificial que genera explicaciones matemáticas adaptadas al nivel del estudiante, resolviendo dudas paso a paso con analogías y retroalimentación en tiempo real.

### Para quién

- **Estudiantes de bachillerato y universidad** que buscan un tutor matemático disponible 24/7 que se adapte a su ritmo y explique con claridad, no solo dé respuestas.
- **Estudiantes con dificultades en matemáticas** que necesitan explicaciones alternativas, pistas graduales y práctica interactiva sin la presión de una clase presencial.

### Principios

- **Entender, no memorizar** — La IA genera explicaciones paso a paso con analogías y pistas graduales en lugar de respuestas directas. El objetivo es comprensión profunda.
- **Arquitectura limpia y mantenible** — DDD con capas bien separadas (Router → Service → Repository), inyección de dependencias obligatoria, código async-first y estándares estrictos (Ruff, Mypy strict, RFC 9457).

### Qué no es

- No es un repositorio de respuestas ni un solucionario automático de tareas. La IA guía, no resuelve por el estudiante.
- No es una plataforma de cursos con videos pregrabados ni contenido estático tipo wiki.
- No es un sistema de gestión académica (LMS) ni reemplaza la relación profesor-alumno.
- No pretende cubrir todas las materias: se limita exclusivamente a ciencias matemáticas (álgebra, cálculo, geometría, estadística).

## Stack Tecnológico

### Producción

- **Framework:** FastAPI.
- **Servidor ASGI:** Uvicorn (`uvicorn[standard]`).
- **Base de Datos & ORM:** PostgreSQL con operaciones asíncronas (`asyncpg`), usando SQLAlchemy y SQLModel.
- **Migraciones:** Alembic (directorio `migrations/`, configuración en `alembic.ini`).
- **Validación:** Pydantic V2.
- **Configuración:** `pydantic-settings` (carga de `.env` vía `BaseSettings`).
- **Variables de Entorno:** `python-dotenv`.
- **Validación de Emails:** `email-validator`.
- **Inteligencia Artificial:** LangChain + `langchain-openai`.

### Desarrollo y Calidad

- **Gestor de Dependencias:** `uv` (lockfile: `uv.lock`).
- **Testing:** pytest, pytest-asyncio, httpx (cliente HTTP asíncrono para tests de integración).
- **Verificación de Tipos en Runtime:** `typeguard`.
- **Linter & Formatter:** Ruff (línea a 88 caracteres, convención Google docstrings).
- **Análisis Estático de Tipos:** Mypy (modo `strict`, plugin `pydantic.mypy`).

### Infraestructura

- **Contenerización:** Docker + Docker Compose.
- **Imagen Base:** `python:3.11-slim`.
- **Base de Datos (contenedor):** `postgres:15-alpine`.

## Estructura del Proyecto

```text
IAHelpMath/
├── .agents/                          # Configuración de agentes
│   └── skills/                       # Skills personalizadas
│       ├── fastapi-app-creator/
│       ├── notion-md-to-page/
│       ├── pytest-best-practices/
│       ├── python-best-practices/
│       ├── skill-creator/
│       └── (mas skills)/...
├── .vscode/                          # Configuración del editor
├── spec/                             # Documentación generada por IA
│   ├── reestructuracion/
│   │   ├── reestructuracion_plan_de_implementacion.md
│   │   └── informe_validacion_qa_fase6.md
│   └── (mas spec)/...
├── migrations/                       # Migraciones de Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── f850706adbdc_initial_migration.py
│       └── ... (mas migraciones)
├── src/                              # Código fuente principal
│   ├── __init__.py
│   ├── main.py                       # Punto de entrada FastAPI
│   ├── core/                         # Módulo transversal de infraestructura
│   │   ├── __init__.py
│   │   ├── config.py                 # Settings (pydantic-settings)
│   │   ├── database.py               # Engine y SessionLocal async
│   │   ├── dependencies.py           # Dependencias compartidas (get_session)
│   │   ├── exceptions.py             # Excepciones centralizadas (RFC 9457)
│   │   └── security.py               # Utilidades de seguridad
│   ├── shared/                       # Módulo de utilidades compartidas
│   │   ├── __init__.py
│   │   └── pagination.py             # Lógica de paginación
│   ├── users/                        # Dominio: Usuarios
│   │   ├── __init__.py               # Router agregador del dominio
│   │   ├── models.py                 # Modelos SQLModel del dominio
│   │   ├── schemas.py                # Schemas Pydantic del dominio
│   │   ├── users/                    # Sub-módulo: CRUD de usuarios
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py       # Inyección de dependencias
│   │   │   ├── repository.py         # Capa de acceso a datos
│   │   │   ├── router.py             # Endpoints HTTP
│   │   │   └── service.py            # Lógica de negocio
│   │   └── (mas submodulos)/         # Sub-módulo: 
│   │       └── ... (archivos)  
│   └── (mas modulos)/                #Modulos   
│       └── ... (archivos) 
├── tests/                            # Suite de pruebas
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures globales de pytest
│   ├── api/                          # Tests de integración (endpoints)
│   │   └── __init__.py
│   └── crud/                         # Tests unitarios (repositorios)
│       └── __init__.py
├── .dockerignore
├── .env                              # Variables de entorno (no versionado)
├── .env.example                      # Plantilla de variables de entorno
├── .gitignore
├── AGENTS.md                         # Reglas y contexto para agentes IA
├── Dockerfile                        # Imagen Docker de producción
├── README.md
├── alembic.ini                       # Configuración de Alembic
├── docker-compose.yml                # Orquestación local (app + PostgreSQL)
├── pyproject.toml                    # Metadatos, dependencias y config de tools
└── uv.lock                           # Lockfile de dependencias (uv)
```

## Patrones de Diseño y Estándares

- Domain-Driven Design (DDD): El código está estructurado por dominios funcionales bajo el directorio `src/` (ej. `src/users`, `src/core`, `src/shared`), no por tipo de archivo. Cada módulo es autocontenido y debe incluir sus propias rutas, servicios, repositorios, esquemas, modelos y dependencias.
- Sub-módulos dentro de un dominio: Cuando un dominio agrupa múltiples entidades con lógica CRUD independiente, se permite crear sub-módulos anidados (ej. `src/users/users/`, `src/users/usernivel/`). Cada sub-módulo contiene su propio `router.py`, `service.py`, `dependencies.py` y `repository.py`. Los archivos compartidos del dominio (`models.py` y `schemas.py`) permanecen en la raíz del módulo padre.
- Arquitectura en capas por dominio: Cada módulo sigue la cadena `Router → Service → Repository`. El **Router** maneja HTTP, el **Service** coordina lógica de negocio y transacciones (`commit`/`rollback`), y el **Repository** encapsula las consultas sin gestionar transacciones.
- Esquemas Pydantic separados por operación: Cada entidad define `Create` (inserción), `Update` (parcial con campos opcionales) y `Response` (lectura con `from_attributes=True`).
- Uso obligatorio de inyección de dependencias en servicios y enrutadores. No se permiten instancias globales de servicios.
- Manejo de excepciones centralizado siguiendo el estándar RFC 9457 (Problem Details for HTTP APIs).
- Límite de línea a 88 caracteres (Ruff/Black).
- Todas las consultas a la base de datos deben ser asíncronas (`AsyncSession`).