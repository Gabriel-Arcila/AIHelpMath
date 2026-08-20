# Roadmap

## Hecho:

1. **001 · Reestructuración DDD** — Migración de la estructura plana (`app/`) a arquitectura Domain-Driven Design por capas con inyección de dependencias, `AsyncSession`, routers modulares y configuración de tooling (Ruff, Mypy strict). → [spec/reestructuracion/](spec/reestructuracion/reestructuracion_plan_de_implementacion.md)

2. **002 · Migración textual RFC 7807 → RFC 9457** — Actualizar todas las referencias de RFC 7807 a RFC 9457 en docstrings, comentarios y documentación. Sin cambios funcionales. → [spec/migracion-rfc-9457-20260629/](spec/migracion-rfc-9457-20260629/plan_migracion_rfc_9457_20260629.md)

3. **003 · Traducción de Código Funcional al Inglés** — Renombrar modelos, atributos, esquemas y tablas del dominio `users` al inglés, junto a una nueva migración de Alembic. → [spec/migracion-codigo-ingles-20260701/plan_migracion_codigo_ingles_20260701.md](spec/migracion-codigo-ingles-20260701/plan_migracion_codigo_ingles_20260701.md)

4. **004 · CRUD de Usuarios** — Implementar el CRUD completo (Create, Read, Read all con paginación, Read detailed, Update, Delete) para la entidad `User` con TDD, arquitectura Router → Service → Repository y paginación genérica. (2026-07-14) → [spec/crud_users_20260714/plan_crud_users_20260714.md](spec/crud_users_20260714/plan_crud_users_20260714.md)

5. **005 · Rollback en Service, Base de Datos de Test y Cobertura** — Aplicar rollback explícito en `UserService`, configurar base de datos de test separada `TestAIHelpMath` y cerrar gaps de cobertura con tests unitarios del Service, excepciones, paginación y health check. (2026-07-27 → 2026-08-02) → [spec/rollback_testdb_coverage_20260727/plan_rollback_testdb_coverage_20260727.md](spec/rollback_testdb_coverage_20260727/plan_rollback_testdb_coverage_20260727.md)

## Siguiente:

6. **006 · Refactorización de Tests** — Reorganizar tests por dominio funcional (replica de `src/`), separar clases por tipo de transacción (Insert, Select, Update, Delete) e implementar Polyfactory para generación automática de datos de prueba. (2026-08-02) → [spec/refactorizacion_tests_20260802/plan_refactorizacion_tests_20260802.md](spec/refactorizacion_tests_20260802/plan_refactorizacion_tests_20260802.md)

#TODO: ver tambie si cambiamo de unittest.mock a pytest-mock, verificar si hay otros plugins de pytest interesantes.

7. Mejorar el skills de TDD, mejorar el apartado de polyfactory, Especificar como se tiene que hacer el archivo de validaciones y revisar si el apartado de test de fasapi-app-creator con pytest-best-practices.

8. GitHub Actions para la ejecución de pruebas, revisar para realizar loggins en el proyecto.
