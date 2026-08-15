# Migración de RFC 7807 → RFC 9457

## Contexto

RFC 9457 ("Problem Details for HTTP APIs"), publicado en julio 2023, **reemplaza oficialmente** a RFC 7807. Ambos estándares son **100% retrocompatibles** — la estructura JSON (`type`, `title`, `status`, `detail`, `instance`) no cambia. RFC 9457 es una revisión evolutiva que:

- Clarifica el uso de campos y edge cases.
- Recomienda URIs absolutas para el campo `type`.
- Enfatiza registros IANA para tipos de problema.
- Agrega guías para describir errores individuales dentro de un problema.

**Esta migración no requiere cambios funcionales en el código.** Es exclusivamente una actualización de referencias textuales (comentarios, docstrings, documentación) de "RFC 7807" a "RFC 9457".

---

## Fase 1: Actualización del Código Fuente (`src/`)

**Objetivo:** Reemplazar todas las menciones de "RFC 7807" por "RFC 9457" en docstrings y comentarios del código fuente.

### Checklist

#### `src/core/exceptions.py`
- [x] Actualizar docstring del módulo: `RFC 7807` → `RFC 9457` (línea 2)
- [x] Actualizar docstring de `app_exception_handler`: `Sigue el estándar RFC 7807.` → `Sigue el estándar RFC 9457.` (línea 73)
- [x] Actualizar Returns del docstring: `según RFC 7807` → `según RFC 9457` (línea 80)
- [x] Verificar que la estructura JSON de Problem Details (`type`, `title`, `status`, `detail`, `instance`) NO se modifica

#### `src/main.py`
- [x] Actualizar comentario inline: `# Registro de manejadores de excepciones globales (RFC 7807)` → `(RFC 9457)` (línea 37)

---

## Fase 2: Actualización de la Documentación del Proyecto

**Objetivo:** Reemplazar todas las menciones de "RFC 7807" por "RFC 9457" en los archivos de documentación raíz.

### Checklist

#### `README.md`
- [x] Actualizar comentario de estructura de proyecto: `# Excepciones centralizadas (RFC 7807)` → `(RFC 9457)` (línea 65)
- [x] Actualizar sección "Patrones de Diseño y Estándares": `RFC 7807 (Problem Details for HTTP APIs)` → `RFC 9457 (Problem Details for HTTP APIs)` (línea 111)

#### `AGENTS.md`
- [x] Verificar que NO contiene la cadena "RFC 7807" (confirmado: no requiere cambios)

---

## Fase 3: Actualización de la Documentación Histórica (`spec/`) [CANCELADA]

> [!NOTE]
> Por decisión de desarrollo, esta fase no se realizará para conservar intacto el registro histórico de las especificaciones de reestructuración originales del proyecto.

**Objetivo (Original):** Reemplazar todas las menciones de "RFC 7807" por "RFC 9457" en los planes e informes existentes de la reestructuración.

### Checklist

#### `spec/reestructuracion/reestructuracion_plan_de_implementacion.md`
- [ ] [CANCELADA] Actualizar Fase 3 objetivo: `excepciones globales RFC 7807` → `RFC 9457` (línea 127)
- [ ] [CANCELADA] Actualizar checklist Fase 3: `JSON normalizado RFC 7807` → `RFC 9457` (línea 137)
- [ ] [CANCELADA] Actualizar Criterio de Aceptación #6: `RFC 7807 (Problem Details)` → `RFC 9457 (Problem Details)` (línea 297)
- [ ] [CANCELADA] Actualizar Resumen de Archivos: `handlers RFC 7807` → `handlers RFC 9457` (línea 334)

#### `spec/reestructuracion/informe_validacion_qa_fase6.md`
- [ ] [CANCELADA] Actualizar Criterio #6 en tabla de criterios: `RFC 7807` → `RFC 9457` (línea 245)
- [ ] [CANCELADA] Actualizar estructura final: `RFC 7807 (AppException + handlers)` → `RFC 9457 (AppException + handlers)` (línea 305)
- [ ] [CANCELADA] Actualizar conclusión final: `excepciones RFC 7807` → `excepciones RFC 9457` (línea 338)

---

## Fase 4: Actualización de Skills de Agentes (`.agents/skills/`)

**Objetivo:** Reemplazar todas las menciones de "RFC 7807" por "RFC 9457" en las skills que guían la generación de código.

### Checklist

#### `.agents/skills/fastapi-app-creator/SKILL.md`
- [x] Actualizar título de sección 11: `(RFC 7807)` → `(RFC 9457)` (línea 566)
- [x] Actualizar descripción de sección 11: `según RFC 7807 (Problem Details)` → `según RFC 9457 (Problem Details)` (línea 569)

#### `.agents/skills/fastapi-app-creator/references/security.md`
- [x] Actualizar docstring de `register_exception_handlers`: `según RFC 7807` → `según RFC 9457` (línea 416)

---

## Fase 5: Validación Integral (QA)

**Objetivo:** Verificar que no quedan referencias obsoletas a RFC 7807 y que no se introdujeron cambios funcionales (excluyendo la documentación histórica de `spec/`).

### Checklist

#### Ausencia de RFC 7807
- [x] Ejecutar `grep -rn "7807" src/ README.md AGENTS.md .agents/skills/` → 0 resultados
- [x] Confirmar que SOLO se modificaron strings de texto (docstrings, comentarios, Markdown)

#### Presencia de RFC 9457
- [x] Ejecutar `grep -rn "9457" src/ README.md .agents/skills/` → 10 resultados esperados (excluyendo el plan de migración y la carpeta `spec/`)

#### Integridad funcional
- [x] Verificar que la estructura JSON de Problem Details (`type`, `title`, `status`, `detail`, `instance`) permanece intacta en `src/core/exceptions.py`
- [x] Ejecutar `uv run ruff check src/ tests/` → 0 errores
- [x] Ejecutar `uv run mypy src/` → 0 errores nuevos

#### Conteo final
- [x] Confirmar 10 ocurrencias actualizadas en 5 archivos (excluyendo `spec/`)

---

## Criterios de Aceptación

| # | Criterio | Validación |
|---|----------|------------|
| 1 | No existen referencias a "RFC 7807" en código fuente ni documentación activa | `grep -rn "7807" src/ README.md .agents/skills/` retorna vacío (se excluye `spec/` por conservación histórica) |
| 2 | Todas las referencias activas ahora apuntan a "RFC 9457" | `grep -rn "9457" src/ README.md .agents/skills/` retorna 11 coincidencias (excluye `spec/` e `implementation_plan.md`) |
| 3 | La estructura JSON de Problem Details no fue alterada | `src/core/exceptions.py` emite `type`, `title`, `status`, `detail`, `instance` |
| 4 | El linter pasa sin errores | `uv run ruff check src/ tests/` → 0 errores |
| 5 | El análisis de tipos pasa sin errores nuevos | `uv run mypy src/` → sin errores nuevos |
| 6 | No se introdujeron cambios funcionales | Solo se modificaron strings en docstrings, comentarios y Markdown |

---

## Referencias Técnicas

| Archivo / Recurso | Propósito | Ubicación |
|-------------------|-----------|-----------|
| `exceptions.py` | Excepciones centralizadas y handlers Problem Details | [exceptions.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/core/exceptions.py) |
| `main.py` | Punto de entrada FastAPI con registro de handlers | [main.py](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/src/main.py) |
| `README.md` | Documentación principal del proyecto | [README.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/README.md) |
| `AGENTS.md` | Reglas y contexto para agentes IA | [AGENTS.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/AGENTS.md) |
| Plan de reestructuración | Plan original de reestructuración del proyecto | [reestructuracion_plan_de_implementacion.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/spec/reestructuracion/reestructuracion_plan_de_implementacion.md) |
| Informe QA Fase 6 | Informe de validación de la reestructuración | [informe_validacion_qa_fase6.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/spec/reestructuracion/informe_validacion_qa_fase6.md) |
| Skill `fastapi-app-creator` | Guía de arquitectura y excepciones | [SKILL.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/SKILL.md) |
| Referencia `security.md` | Guía de seguridad con handlers de excepciones | [security.md](file:///c:/Users/gabri/OneDrive/Documentos/Proyecto/IAHelpMath/.agents/skills/fastapi-app-creator/references/security.md) |
| RFC 9457 | Especificación oficial "Problem Details for HTTP APIs" | [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) |

---

## Resumen de Archivos

| Acción | Archivo | Descripción |
|--------|---------|-------------|
| ✏️ Modificar | `src/core/exceptions.py` | 3 docstrings: "RFC 7807" → "RFC 9457" |
| ✏️ Modificar | `src/main.py` | 1 comentario inline: "RFC 7807" → "RFC 9457" |
| ✏️ Modificar | `README.md` | 2 menciones en estructura y patrones de diseño |
| ❌ Sin cambios | `spec/reestructuracion/reestructuracion_plan_de_implementacion.md` | Excluido por decisión de desarrollo (conservación histórica) |
| ❌ Sin cambios | `spec/reestructuracion/informe_validacion_qa_fase6.md` | Excluido por decisión de desarrollo (conservación histórica) |
| ✏️ Modificar | `.agents/skills/fastapi-app-creator/SKILL.md` | 2 menciones en sección 11 |
| ✏️ Modificar | `.agents/skills/fastapi-app-creator/references/security.md` | 1 mención en docstring de función |
| 🔍 Revisar | `AGENTS.md` | No contiene "RFC 7807", no requiere cambios |
