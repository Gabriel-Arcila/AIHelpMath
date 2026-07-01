# Contexto

**Resumen:** En la revisión del proyecto se encontró que el dominio `users` contiene definiciones funcionales en español (modelos de base de datos, atributos, nombres de tablas, esquemas Pydantic y variables locales), lo que incumple la regla del proyecto que establece que el código generado debe estar en inglés (manteniendo los docstrings en español).

**Justificación:** Estandarizar el código al inglés permite seguir las mejores prácticas de desarrollo y facilita la mantenibilidad del proyecto a largo plazo, además de mantener la consistencia con el resto del proyecto (ej: `core`, `shared`).

**Objetivo:** Renombrar todos los componentes funcionales del módulo `users` (modelos de base de datos, esquemas Pydantic, variables locales y funciones relacionadas) al idioma inglés. Además, se deberá generar una nueva migración de Alembic para reflejar estos cambios en el esquema de la base de datos sin afectar su funcionamiento. Se establece la regla de que todos los identificadores de tablas y foráneos deben comenzar con el prefijo `id_`.

**Riesgo:** El riesgo principal es introducir errores de tipo `ImportError` o conflictos de nombres al refactorizar. Además, al renombrar tablas en la base de datos, es necesario asegurar que la migración se autogenere correctamente.

**Enfoque:** 
1. Refactorizar modelos y actualizar nombres de tabla y atributos.
2. Refactorizar esquemas (Schemas Pydantic) para coincidir con los nuevos nombres.
3. Actualizar la lógica (Repository, Service, Router, Dependencies) para que importen y usen los nuevos nombres.
4. Ajustar los tests para alinearlos a los nuevos modelos y esquemas.
5. Generar una nueva migración con Alembic.

---

# Fases Estructuradas y Checklist de Tareas

## Fase 1: Refactorización de Modelos de Base de Datos
**Objetivo:** Traducir al inglés los modelos de SQLModel y atributos internos en `src/users/models.py`.

- [ ] Renombrar la clase `UserNivel` a `UserLevel` y su tabla a `user_level`.
- [ ] Renombrar la clase `UserTemaInteres` a `UserTopic` y su tabla a `user_topic`.
- [ ] Renombrar la clase `UserPerfilIA` a `UserAIProfile` y su tabla a `user_ai_profile`.
- [ ] Renombrar la clase `UserRol` a `UserRole` y su tabla a `user_role`.
- [ ] En la clase `User`, renombrar atributos foráneos conservando el prefijo `id_`: `id_rol` -> `id_role`.
- [ ] En la clase `User`, renombrar atributos estándar: `nombre` -> `first_name`, `apellido` -> `last_name`. Cambiar relaciones: `user_rol` -> `user_role`, `user_perfiles_ia` -> `user_ai_profiles`.
- [ ] En los demás modelos, traducir atributos correspondientes (ej. `descripcion` -> `description`, `cuantificador` -> `quantifier`, `id_user_nivel` -> `id_user_level`, `id_user_tema_interes` -> `id_user_topic`, etc.).

## Fase 2: Refactorización de Esquemas Pydantic
**Objetivo:** Estandarizar los esquemas de entrada y salida al inglés en `src/users/schemas.py`.

- [ ] Traducir esquemas de roles: `UserRolCreate` -> `UserRoleCreate`, `UserRolUpdate` -> `UserRoleUpdate`, `UserRolResponse` -> `UserRoleResponse`.
- [ ] Traducir esquemas de niveles: `UserNivelCreate` -> `UserLevelCreate`, etc.
- [ ] Traducir esquemas de temas: `UserTemaInteresCreate` -> `UserTopicCreate`, etc.
- [ ] Traducir esquemas de perfil IA: `UserPerfilIACreate` -> `UserAIProfileCreate`, etc.
- [ ] Actualizar atributos de esquemas para coincidir con los modelos en inglés y el prefijo `id_` (`first_name`, `last_name`, `description`, `id_role`, `id_user_level`, etc.).

## Fase 3: Refactorización de Capa de Negocio y API
**Objetivo:** Actualizar repositorios, servicios, rutas y dependencias para usar los nuevos nombres y variables locales en inglés.

- [ ] Actualizar importaciones y tipos en `src/users/users/repository.py`. Renombrar variables locales en español.
- [ ] Actualizar importaciones y tipos en `src/users/users/service.py`.
- [ ] Actualizar importaciones, tipos y decoradores en `src/users/users/router.py`.
- [ ] Revisar `src/users/users/dependencies.py` y actualizar imports si es necesario.

## Fase 4: Refactorización de Tests
**Objetivo:** Asegurar que las pruebas pasen utilizando los nuevos nombres y estructuras.

- [ ] Revisar y modificar los fixtures y mockups en `tests/conftest.py`.
- [ ] Actualizar los tests en `tests/crud/` y `tests/api/` si están presentes, usando la nueva nomenclatura.

## Fase 5: Validación (QA y Accesibilidad)
**Objetivo:** Generar migraciones y validar que todo el backend compile, pase tests y linter sin errores.

- [ ] Ejecutar linting y formatting: `uv run ruff check src/ tests/` y `uv run ruff format src/ tests/`.
- [ ] Ejecutar comprobación estática de tipos: `uv run mypy src/`.
- [ ] Generar migración de Alembic: `uv run alembic revision --autogenerate -m "translate_functional_code_to_english"`.
- [ ] Levantar la base de datos de test (`docker compose up db -d`) y aplicar la migración (`uv run alembic upgrade head`).
- [ ] Ejecutar los tests: `uv run pytest -v`.

---

# Criterios de Aceptación

1. El archivo `src/users/models.py` contiene clases y atributos funcionales estrictamente en inglés.
2. Todos los campos que representan un identificador de modelo o clave foránea mantienen el prefijo `id_` (ej. `id_role`, `id_user_level`).
3. El archivo `src/users/schemas.py` refleja de forma exacta los nuevos esquemas en inglés con los mismos prefijos `id_`.
4. El proyecto pasa todos los chequeos de `ruff` y `mypy` sin advertencias relacionadas con el renombrado.
5. Se generó con éxito una nueva revisión de Alembic que aplica los cambios en el esquema de base de datos.
6. Los tests de `pytest` se ejecutan sin errores con la base de datos levantada.
7. El código documentado, como comentarios y docstrings, permanece en español.
8. El archivo `roadmap.md` está actualizado reflejando la inclusión de este plan en la sección "Siguiente".

---

# Referencias Técnicas

| Archivo | Rol |
|---------|-----|
| [src/users/models.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/models.py) | Definición de modelos de datos SQLModel |
| [src/users/schemas.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/schemas.py) | Definición de esquemas Pydantic |
| [src/users/users/repository.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/users/repository.py) | Patrón Repositorio para `User` |
| [src/users/users/service.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/users/service.py) | Lógica de Negocio |
| [src/users/users/router.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/users/users/router.py) | API Endpoints de `User` |

---

# Resumen de Archivos

| Archivo | Acción |
|---------|--------|
| `spec/migracion-codigo-ingles-20260701/plan_migracion_codigo_ingles_20260701.md` | Crear |
| `spec/roadmap.md` | Modificar |
| `src/users/models.py` | Modificar |
| `src/users/schemas.py` | Modificar |
| `src/users/users/repository.py` | Modificar |
| `src/users/users/service.py` | Modificar |
| `src/users/users/router.py` | Modificar |
| `src/users/users/dependencies.py` | Modificar |
| `tests/conftest.py` | Modificar |
| `migrations/versions/<hash>_translate_functional_code_to_english.py` | Crear |
