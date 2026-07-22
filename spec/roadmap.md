# Roadmap

## Hecho:

1. **001 · Reestructuración DDD** — Migración de la estructura plana (`app/`) a arquitectura Domain-Driven Design por capas con inyección de dependencias, `AsyncSession`, routers modulares y configuración de tooling (Ruff, Mypy strict). → [spec/reestructuracion/](spec/reestructuracion/reestructuracion_plan_de_implementacion.md)

2. **002 · Migración textual RFC 7807 → RFC 9457** — Actualizar todas las referencias de RFC 7807 a RFC 9457 en docstrings, comentarios y documentación. Sin cambios funcionales. → [spec/migracion-rfc-9457-20260629/](spec/migracion-rfc-9457-20260629/plan_migracion_rfc_9457_20260629.md)

3. **003 · Traducción de Código Funcional al Inglés** — Renombrar modelos, atributos, esquemas y tablas del dominio `users` al inglés, junto a una nueva migración de Alembic. → [spec/migracion-codigo-ingles-20260701/plan_migracion_codigo_ingles_20260701.md](spec/migracion-codigo-ingles-20260701/plan_migracion_codigo_ingles_20260701.md)

## Siguiente:

4. **004 · CRUD de Usuarios** — Implementar el CRUD completo (Create, Read, Read all con paginación, Read detailed, Update, Delete) para la entidad `User` con TDD, arquitectura Router → Service → Repository y paginación genérica. (2026-07-14) → [spec/crud_users_20260714/plan_crud_users_20260714.md](spec/crud_users_20260714/plan_crud_users_20260714.md)

5. Revisar que no hay ningun rollback en user src y cambiar a otra base de datos para tests.
6. Mejorar el skills de TDD.
7. Especificar como se tiene que hacer el archivo de validaciones.
8. Realizar pruebas de cobertura.
9. GitHub Actions para la ejecución de pruebas.
10. Generador aleatorio con faker u otra librería.
