# AGENTS.md

**IAHelpMath** es un backend construido con **FastAPI** diseñado para proveer un **Tutor de Inteligencia Artificial especializado en Matemáticas**. Toda contribución debe respetar la identidad del proyecto y sus reglas de negocio.

## Intruccion basicas de comportamiento

- Responda siempre en **Español** a menos que se indique explícitamente lo contrario.
- Siempre dame respuestas objetivas y tecnicas. No seas adulador ni excesivamente cortés.
- El codigo generado siempre tiene que ser en **Ingles**.
- Al terminar, indicame que realizaste y porque lo realizaste para que pueda revisarlo, sin ser demasido extenso.
- Lee el archivo `README.md` antes de hacer cualquier cambio para tener el contexto de la aplicacion. 
- Si realizaste algun principio importante que no esta considerado en los aspectos dentro de las `skills` o del `AGENTS.md`, indicamelo para la verificacion y realizacion de una mejora de las `skills` o el `AGENTS.md`.

### Que debes hacer cuando te pidan explicar el codigo
-  Explicar paso a paso el codigo con detalles.
-  Explicar el porque se realizo de esa menera.

## Testing y Pruebas

| Herramienta | Propósito | Cuándo usarla |
|---|---|---|
| `pytest` | Framework de testing | Siempre que se ejecuten pruebas. |
| `pytest-asyncio` | Soporte para tests `async/await` | Todo test que invoque código asíncrono (servicios, repositorios, endpoints). |
| `httpx` (`AsyncClient`) | Cliente HTTP asíncrono para tests | Tests de integración contra endpoints FastAPI (sin levantar servidor). |
| `typeguard` | Verificación de tipos en runtime | Para validar anotaciones de tipo durante la ejecución de tests. |
| `ruff` | Linter y formatter | Antes de cada commit para garantizar estilo y detectar errores estáticos. |
| `mypy` | Análisis estático de tipos | Para verificar la correctitud de las anotaciones de tipo en `src/`. |
| `Docker Compose` | Orquestación de contenedores | Para levantar PostgreSQL (obligatorio para tests) y la app en producción. |
| `Alembic` | Migraciones de base de datos | Al crear/modificar modelos SQLModel para sincronizar el schema de la DB. |

### Comandos

```bash
# ── Setup inicial ──────────────────────────────────────────────
cp .env.example .env                 # Crear archivo de variables de entorno
uv sync                              # Instalar dependencias (prod + dev)
docker compose up db -d              # Levantar PostgreSQL en Docker
uv run alembic upgrade head          # Aplicar migraciones pendientes

# ── Desarrollo (servidor local) ───────────────────────────────
uv run uvicorn src.main:app --reload # FastAPI en http://localhost:8000
                                     # Docs en /docs (Swagger) y /redoc

# ── Testing ────────────────────────────────────────────────────
docker compose up db -d              # Asegurar que la DB esté corriendo
uv run pytest -v                     # Ejecutar todos los tests
uv run pytest tests/api/ -v          # Solo integración (endpoints)
uv run pytest tests/crud/ -v         # Solo unitarios (repositorios)
uv run pytest --cov=src --cov-report=term-missing  # Cobertura

# ── Calidad de código ─────────────────────────────────────────
uv run ruff check src/ tests/        # Linter
uv run ruff format src/ tests/       # Formatter
uv run mypy src/                     # Análisis estático de tipos

# ── Migraciones (Alembic) ─────────────────────────────────────
uv run alembic revision --autogenerate -m "descripcion"  # Nueva migración
uv run alembic upgrade head          # Aplicar migraciones
uv run alembic downgrade -1          # Revertir última migración

# ── Docker (producción / CI) ──────────────────────────────────
docker compose up --build            # Construir y levantar todo (app + db)
docker compose down                  # Detener y eliminar contenedores
docker compose logs -f app           # Ver logs de la aplicación
```

## Skills

| Skill | Propósito | Cuándo usarlo | Ubicación |
|---|---|---|---|
| `notion-md-to-page` | Convertir archivos Markdown a páginas de Notion (vía MCP). Maneja el parseo y la segmentación (chunking). | Para exportar documentación, subir notas o migrar archivos `.md` a Notion. | `.agents/skills/notion-md-to-page/SKILL.md` |
| `skill-creator` | Crear nuevas skills, modificar y mejorar skills existentes, y medir su rendimiento. | Para crear una skill desde cero, editar o optimizar una existente, o ejecutar evaluaciones y pruebas. | `.agents/skills/skill-creator/SKILL.md` |
| `fastapi-app-creator` | Guía completa para crear aplicaciones FastAPI con mejores prácticas: arquitectura limpia, Pydantic V2, SQLAlchemy async, testing, seguridad y despliegue. | Para crear, estructurar o desarrollar aplicaciones FastAPI, configurar APIs REST con Python, o aplicar patrones de producción. | `.agents/skills/fastapi-app-creator/SKILL.md` |
| `pytest-best-practices` | Guía completa de mejores prácticas para pytest: patrón AAA, fixtures, parametrización, mocking, testing asíncrono, cobertura y CI/CD. | Para escribir pruebas unitarias o de integración, configurar pytest, crear fixtures, hacer mocking, testear código async, o integrar pytest en pipelines CI/CD. | `.agents/skills/pytest-best-practices/SKILL.md` |
| `python-best-practices` | Guía estricta de mejores prácticas y estándares de codificación en Python basados en PEP 8, PEP 20, PEP 257 y tipado moderno. | Para escribir, refactorizar o revisar código Python, asegurando el cumplimiento de estándares de calidad, convenciones y tipado. | `.agents/skills/python-best-practices/SKILL.md` |
| `tdd` | Guía para desarrollo guiado por pruebas (Test-Driven Development) usando el ciclo red-green-refactor, evitando acoplamiento a la implementación y definiendo costuras (seams) de prueba. | Cuando se requiera desarrollar características o corregir bugs test-first, se mencione 'red-green-refactor', o se requieran pruebas de integración/unitarias estructuradas. | `.agents/skills/tdd/SKILL.md` |

> [!TIP]
> **Instrucción para el Agente:** Antes de utilizar un skill, usa la herramienta de lectura de archivos para revisar su `SKILL.md` y seguir sus instrucciones al pie de la letra.

## Servidores MCP Disponibles

| Servidor MCP | Propósito | Cuándo usarlo | Integración |
|---|---|---|---|
| `notion-mcp-server` | Integración directa con la API de Notion. Permite recuperar usuarios, leer/escribir bloques, páginas, bases de datos y realizar búsquedas de forma nativa. | Para realizar operaciones directas sobre el espacio de trabajo de Notion sin necesidad de crear scripts manuales. | `~/.gemini/antigravity/mcp/notion-mcp-server` |

## Documentación

- En `README.md` esta el contexto de la aplicacion.
- En la carpeta `spec/` estan todos los planes de implementacion y documentacion tecnica generada por IA.
- Ignora el archivo `Backlog.md` en la carpeta `spec/` a menos que se te diga lo contrario.

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
| `delete` | Limpieza de codigo. |

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

## Directrices para Planes de Implementación

Cada vez que se solicite crear un plan de implementación para una nueva funcionalidad, componente o página, el plan debe generarse siguiendo estrictamente estas características y estructura:

1. **Ubicación del Archivo:** Los planes deben guardarse siempre como archivos Markdown (`.md`) dentro de una carpeta específica bajo el directorio `spec/` (por ejemplo, `spec/<nombre_implementacion>_YYYYMMDD/plan_<nombre_implementacion>_YYYYMMDD.md`).
2. **Contexto:** El plan debe incluir un resumen del contexto actual, la justificación, el objetivo, el riesgo y el enfoque de la implementación.
3. **Fases Estructuradas:** El plan debe dividirse en Fases lógicas y progresivas. Cada fase debe tener un objetivo claro y debe indicar los archivos a modificar, crear o eliminar.
4.**TDD (Test-Driven Development):** La primera fase siempre debe tratar sobre prueba unitarias con pytest en la carpeta `tests/` del proyecto.
5. **Checklist de Tareas:** Cada fase debe contar con un checklist accionable (`- [ ]`) de tareas muy específicas y granulares que permitan hacer seguimiento visual del progreso (Cada ves que termines una tarea, marcala con un 'x').
6. **Fase Obligatoria de Validación (QA y Accesibilidad):** Todo plan debe incluir como última fase la validación integral.
7. **Criterios de Aceptación:** Una lista al final de las fases definiendo qué condiciones exactas deben cumplirse para dar por exitosa la implementación.
8. **Referencias Técnicas:** Una tabla enlazando los archivos base necesarios.
9. **Resumen de Archivos:** Una tabla detallando qué archivos nuevos se crearán (`Crear`), cuáles se modificarán (`Modificar`) y cuáles solo se revisarán (`Revisar`).
10. **Actualizacion del Archivo `roadmap.md`:** Al crear, modificar o completar un plan de implementacion se debe actualizar el archivo `roadmap.md` en la seccion "Hecho" o "Siguiente" segun corresponda con el numero del plan,descripcion corta, nombre, fecha y enlace al plan.