# AGENTS.md

## Contexto

**IAHelpMath** es un backend construido con **FastAPI** diseñado para proveer un **Tutor de Inteligencia Artificial especializado en Matemáticas**. Toda contribución debe respetar la identidad del proyecto y sus reglas de negocio.

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

## Patrones de Diseño y Estándares:

- Domain-Driven Design (DDD): El código está estructurado por dominios funcionales bajo el directorio `src/` (ej. `src/users`, `src/core`, `src/shared`), no por tipo de archivo. Cada módulo es autocontenido y debe incluir sus propias rutas, servicios, repositorios, esquemas, modelos y dependencias.
- Arquitectura en capas por dominio: Cada módulo sigue la cadena `Router → Service → Repository`. El **Router** maneja HTTP, el **Service** coordina lógica de negocio y transacciones (`commit`/`rollback`), y el **Repository** encapsula las consultas sin gestionar transacciones.
- Esquemas Pydantic separados por operación: Cada entidad define `Create` (inserción), `Update` (parcial con campos opcionales) y `Response` (lectura con `from_attributes=True`).
- Uso obligatorio de inyección de dependencias en servicios y enrutadores. No se permiten instancias globales de servicios.
- Manejo de excepciones centralizado siguiendo el estándar RFC 7807 (Problem Details for HTTP APIs).
- Límite de línea a 88 caracteres (Ruff/Black).
- Todas las consultas a la base de datos deben ser asíncronas (`AsyncSession`).

## Intruccion basicas de comportamiento

- Responda siempre en español a menos que se indique explícitamente lo contrario.
- Siempre dame respuestas objetivas y tecnicas. No seas adulador ni excesivamente cortés.
- El codigo generado siempre tiene que ser en Ingles.
- Al terminar, dime qué cambiaste para que lo
revise.

## Estructura del Proyecto

TODO: Pendiente primero hay que depurar la estructura del proyecto

## Testing y Pruebas

TODO: Pendiente

## Git y GitHub

### Commit

Sigue la especificación Conventional Commits

**Estructura:**

```
tipo(ámbito): descripción corta en imperativo
```

**Principales Tipos:**

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad para el usuario. |
| `fix` | Corrección de un bug. |
| `refactor` | Reestructuración de código sin cambiar comportamiento. |
| `docs` | Cambios exclusivamente en documentación. |
| `test` | Agregar o corregir tests. |
| `build` | Cambios en dependencias, Docker o configuración de build. |
| `ci` | Cambios en pipelines CI/CD. |
| `style` | Formato, espacios, puntos y comas (sin cambio lógico). |
| `perf` | Mejoras de rendimiento. |
| `chore` | Tareas de mantenimiento que no tocan `src/` ni `tests/`. |

**Ámbitos:** Usar los dominios del proyecto (`users`, `core`, `shared`, `api`, etc..) o infraestructura (`docker`, `deps`, `migrations`, etc..).

**Reglas:**

- Modo imperativo en la descripción: "add", no "added" ni "adding".
- Línea de asunto ≤ 72 caracteres.
- Breaking changes: agregar `!` después del ámbito (ej. `feat(users)!: remove legacy endpoint`).
- Referenciar issues en el footer, no en el ámbito: `Fixes #42`.

**Instrucciones para el agente:**

- Ejecutar revisiones antes de proponer un commit:
    - `git status`.
    - `git diff`.
    - `git diff --stat`.
    - `git diff --staged`.
    - `git diff --staged --stat`.
- Ofrecer **3 opciones** de mensaje para que el usuario elija.

## Skills

| Skill | Propósito | Cuándo usarlo | Ubicación |
|---|---|---|---|
| `notion-md-to-page` | Convertir archivos Markdown a páginas de Notion (vía MCP). Maneja el parseo y la segmentación (chunking). | Para exportar documentación, subir notas o migrar archivos `.md` a Notion. | `.agents/skills/notion-md-to-page/SKILL.md` |
| `skill-creator` | Crear nuevas skills, modificar y mejorar skills existentes, y medir su rendimiento. | Para crear una skill desde cero, editar o optimizar una existente, o ejecutar evaluaciones y pruebas. | `.agents/skills/skill-creator/SKILL.md` |
| `fastapi-app-creator` | Guía completa para crear aplicaciones FastAPI con mejores prácticas: arquitectura limpia, Pydantic V2, SQLAlchemy async, testing, seguridad y despliegue. | Para crear, estructurar o desarrollar aplicaciones FastAPI, configurar APIs REST con Python, o aplicar patrones de producción. | `.agents/skills/fastapi-app-creator/SKILL.md` |
| `pytest-best-practices` | Guía completa de mejores prácticas para pytest: patrón AAA, fixtures, parametrización, mocking, testing asíncrono, cobertura y CI/CD. | Para escribir pruebas unitarias o de integración, configurar pytest, crear fixtures, hacer mocking, testear código async, o integrar pytest en pipelines CI/CD. | `.agents/skills/pytest-best-practices/SKILL.md` |
| `python-best-practices` | Guía estricta de mejores prácticas y estándares de codificación en Python basados en PEP 8, PEP 20, PEP 257 y tipado moderno. | Para escribir, refactorizar o revisar código Python, asegurando el cumplimiento de estándares de calidad, convenciones y tipado. | `.agents/skills/python-best-practices/SKILL.md` |

> [!TIP]
> **Instrucción para el Agente:** Antes de utilizar un skill, usa la herramienta de lectura de archivos para revisar su `SKILL.md` y seguir sus instrucciones al pie de la letra.

## Servidores MCP Disponibles

| Servidor MCP | Propósito | Cuándo usarlo | Integración |
|---|---|---|---|
| `notion-mcp-server` | Integración directa con la API de Notion. Permite recuperar usuarios, leer/escribir bloques, páginas, bases de datos y realizar búsquedas de forma nativa. | Para realizar operaciones directas sobre el espacio de trabajo de Notion sin necesidad de crear scripts manuales. | `~/.gemini/antigravity/mcp/notion-mcp-server` |

## Directrices para Planes de Implementación

Cada vez que se solicite crear un plan de implementación para una nueva funcionalidad, componente o página, el plan debe generarse siguiendo estrictamente estas características y estructura:

1. **Ubicación del Archivo:** Los planes deben guardarse siempre como archivos Markdown (`.md`) dentro de una carpeta específica bajo el directorio `docsAI/` (por ejemplo, `docsAI/<nombre_implementacion>/nombre_implementacion_plan_de_implementacion.md`).
2. **Fases Estructuradas:** El plan debe dividirse en Fases lógicas y progresivas. Cada fase debe tener un objetivo claro.
3. **Checklist de Tareas:** Cada fase debe contar con un checklist accionable (`- [ ]`) de tareas muy específicas y granulares que permitan hacer seguimiento visual del progreso.
4. **Fase Obligatoria de Validación (QA y Accesibilidad):** Todo plan debe incluir como última fase la validación integral.
5. **Criterios de Aceptación:** Una lista al final de las fases definiendo qué condiciones exactas deben cumplirse para dar por exitosa la implementación.
6. **Referencias Técnicas:** Una tabla enlazando los archivos base necesarios.
7. **Resumen de Archivos:** Una tabla detallando qué archivos nuevos se crearán (`🆕 Crear`), cuáles se modificarán (`✏️ Modificar`) y cuáles solo se revisarán (`🔍 Revisar`).