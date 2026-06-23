# AGENTS

Este documento define el contexto principal y las instrucciones para el agente de IA que trabaja en este proyecto. 
**Contexto para el Agente:** Al leer este archivo, asume estas directrices como tu base de conocimiento y reglas de comportamiento. Además de las reglas aquí descritas, ten presente que cuentas con **Servidores MCP (Model Context Protocol)** y **Skills** especializadas; utilízalas siempre que sean relevantes para optimizar la resolución de tareas.

## Intruccion basicas de comportamiento

- Responda siempre en español a menos que se indique explícitamente lo contrario.
- Siempre dame respuestas objetivas y tecnicas. No seas adulador ni excesivamente cortés.
- El codigo generado siempre tiene que ser en Ingles

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