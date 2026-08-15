## Backlog / ideas 💡

### Prioridad Alta

- **CRUD de entidades pendientes** — Implementar sub-módulos (repository/service/router/dependencies) para `UserNivel`, `UserRol`, `UserTemaInteres` y `UserPerfilIA`.
- **Testing** — Escribir tests unitarios (`tests/crud/`) y de integración (`tests/api/`) para los endpoints y repositorios existentes.
- **Autenticación y seguridad** — Reemplazar el placeholder de `security.py` (actualmente solo `get_current_user() → None`) con hashing bcrypt/argon2, JWT (access + refresh tokens), `OAuth2PasswordBearer`, y dependencias de auth inyectables (`get_current_user`, `get_current_active_user`).

### Prioridad Media

- **Configuración completa** — Agregar settings faltantes en `config.py`: `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM` (JWT), `OPENAI_API_KEY`, `CORS_ORIGINS`, `LOG_LEVEL`.
- **Paginación** — Implementar utilidades reales en `shared/pagination.py` (`PaginatedResponse`, cursor/offset pagination). El archivo existe como placeholder vacío.
- **Middleware** — Agregar CORS, logging estructurado y rate limiting como middleware de FastAPI.
- **Endpoints detallados** — Exponer endpoints que usen los schemas `UserDetailed` y `UserPerfilIADetailed` (ya definidos pero sin uso) para retornar usuarios con relaciones expandidas (rol + perfiles IA).

### Prioridad Baja

- **Tutor IA (LangChain)** — Motor de inteligencia artificial para explicaciones matemáticas paso a paso. LangChain y `langchain-openai` ya están en dependencias pero sin implementación. Requiere un dominio `src/ai_tutor/` con su propia cadena Router → Service.
- **Progreso de aprendizaje** — Tracking del avance del estudiante: ejercicios completados, niveles desbloqueados, métricas de rendimiento por tema.
- **Ejercicios interactivos** — Generación y evaluación de problemas matemáticos adaptados al nivel del estudiante, con pistas graduales y retroalimentación.
- **CI/CD** — Pipeline de integración continua (Ruff, Mypy, pytest, Docker build) en GitHub Actions.
- **Documentación API** — Mejorar metadata de OpenAPI: descripciones de endpoints, ejemplos de request/response, tags organizados por dominio.