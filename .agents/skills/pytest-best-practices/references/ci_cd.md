# CI/CD: Plugins, Cobertura y Pipelines

Referencia especializada para la integración de pytest en pipelines
de integración continua y ecosistemas de plugins.

## Tabla de contenidos

1. [Plugins esenciales](#1-plugins-esenciales)
2. [Cobertura con pytest-cov](#2-cobertura-con-pytest-cov)
3. [Ejecución paralela con pytest-xdist](#3-ejecución-paralela-con-pytest-xdist)
4. [Reporte JUnit XML](#4-reporte-junit-xml)
5. [Pipeline CI/CD con GitHub Actions](#5-pipeline-cicd-con-github-actions)
6. [Buenas prácticas de CI/CD](#6-buenas-prácticas-de-cicd)

---

## 1. Plugins esenciales

| Plugin | Propósito | Instalación |
|---|---|---|
| `pytest-asyncio` | Tests asíncronos con `async def` | `pip install pytest-asyncio` |
| `pytest-cov` | Auditoría topográfica de cobertura | `pip install pytest-cov` |
| `pytest-xdist` | Ejecución paralela en múltiples CPUs | `pip install pytest-xdist` |
| `pytest-randomly` | Reordena tests aleatoriamente | `pip install pytest-randomly` |
| `pytest-mock` | Mock con cleanup automático | `pip install pytest-mock` |
| `pytest-timeout` | Timeout por test (evita cuelgues) | `pip install pytest-timeout` |

### pytest-randomly

Reordena la ejecución de los tests en cada corrida para detectar
dependencias ocultas entre tests. Si un test falla solo cuando
se ejecuta después de otro, es una señal de contaminación de estado.

```bash
# Ejecutar con semilla reproducible
pytest --randomly-seed=12345

# Desactivar temporalmente
pytest -p no:randomly
```

### pytest-timeout

Establece un tiempo máximo por test. Los tests que excedan el
timeout fallan automáticamente, evitando cuelgues en CI.

```toml
[tool.pytest.ini_options]
timeout = 30
```

---

## 2. Cobertura con pytest-cov

### Configuración en pyproject.toml

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "if TYPE_CHECKING:",
]
```

### Ejecutar con cobertura

```bash
# Reporte en terminal
pytest --cov=src --cov-report=term-missing

# Reporte HTML (para revisión visual)
pytest --cov=src --cov-report=html

# Reporte XML (para CI/CD)
pytest --cov=src --cov-report=xml
```

### Interpretar la cobertura

| Métrica | Significado |
|---|---|
| **Stmts** | Total de sentencias ejecutables |
| **Miss** | Sentencias no ejecutadas por ningún test |
| **Cover** | Porcentaje de cobertura |
| **Missing** | Números de línea sin cobertura |

### Reglas de cobertura

- **No perseguir el 100%**: Un 80-90% es un objetivo realista y
  productivo. El último 10% suele requerir esfuerzo desproporcionado.
- **Cubrir caminos críticos**: Priorizalos caminos de negocio,
  validaciones y manejo de errores.
- **`pragma: no cover`**: Usar solo para código genuinamente
  imposible de testear (bloques `if TYPE_CHECKING`, `__main__`).
- **`fail_under`**: Establecer un umbral mínimo en CI para evitar
  regresiones de cobertura.

---

## 3. Ejecución paralela con pytest-xdist

`pytest-xdist` fragmenta el test suite en múltiples procesos
(workers) que ejecutan en paralelo, reduciendo drásticamente el
tiempo total.

```bash
# Usar todos los CPUs disponibles
pytest -n auto

# Número fijo de workers
pytest -n 4

# Distribuir por archivo (agrupa tests del mismo archivo)
pytest -n auto --dist loadfile
```

### Estrategias de distribución

| Estrategia | Comportamiento |
|---|---|
| `load` (default) | Distribuye tests individuales entre workers |
| `loadfile` | Agrupa tests del mismo archivo en un worker |
| `loadscope` | Agrupa tests del mismo scope (clase/módulo) |

### Consideraciones para tests paralelos

1. **Aislamiento total**: Cada test debe ser hermético. No compartir
   estado global, archivos temporales ni puertos.
2. **Base de datos**: Usar una base de datos de test por worker o
   transacciones aisladas para evitar conflictos.
3. **Fixtures de scope session**: Se crean una vez por worker, no
   una vez en total. Si necesitas un recurso compartido entre
   workers, considerar `--dist loadscope`.
4. **Orden aleatorio**: `pytest-randomly` + `pytest-xdist` juntos
   son especialmente útiles para detectar dependencias ocultas.

---

## 4. Reporte JUnit XML

Todo pipeline de CI debe exportar telemetría en formato JUnit XML
para la ingesta y visualización por el integrador continuo.

```bash
pytest --junitxml=reports/junit.xml
```

### Combinando reportes

```bash
# Cobertura + JUnit XML + verbose
pytest \
    --cov=src \
    --cov-report=xml:reports/coverage.xml \
    --junitxml=reports/junit.xml \
    -v
```

Los archivos XML generados son leídos automáticamente por la mayoría
de plataformas CI (GitHub Actions, GitLab CI, Jenkins) para mostrar
resúmenes de tests y tendencias de cobertura.

---

## 5. Pipeline CI/CD con GitHub Actions

### Ejemplo completo

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: >-
            pip-${{ runner.os }}-
            ${{ matrix.python-version }}-
            ${{ hashFiles('**/pyproject.toml') }}
          restore-keys: |
            pip-${{ runner.os }}-${{ matrix.python-version }}-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run tests
        env:
          DATABASE_URL: >-
            postgresql+asyncpg://test:test@localhost:5432/test_db
        run: |
          pytest \
            --cov=src \
            --cov-report=xml:reports/coverage.xml \
            --junitxml=reports/junit.xml \
            -n auto \
            -v

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.python-version }}
          path: reports/
```

### Despliegue matricial

La estrategia `matrix` ejecuta los tests en múltiples versiones de
Python para detectar incompatibilidades tempranas. La razón de
incluir varias versiones es que bibliotecas y la propia sintaxis de
Python pueden comportarse diferente entre versiones.

---

## 6. Buenas prácticas de CI/CD

### Caché de dependencias

No cachear el entorno virtual completo (`.venv/`). Esto causa
corrupciones cuando las dependencias cambian. En su lugar, cachear
solo el directorio de descarga del gestor de paquetes (ej.
`~/.cache/pip`) vinculándolo al hash del lockfile.

```yaml
# ✅ CORRECTO — cachea descargas, no binarios
key: pip-${{ hashFiles('**/pyproject.toml') }}

# ❌ INCORRECTO — cachea el entorno virtual
key: venv-${{ hashFiles('**/pyproject.toml') }}
```

### Principio de menor privilegio

Los workflows de CI deben ejecutarse con permisos mínimos. En
GitHub Actions, configurar:

```yaml
permissions:
  contents: read
```

Esto previene que un test comprometido pueda escribir en el
repositorio o acceder a secretos innecesarios.

### Categorización de tests

Separar tests rápidos (unit) de lentos (integration) usando
marcadores. En CI, ejecutar primero los rápidos para feedback
inmediato.

```bash
# Paso 1: tests unitarios rápidos
pytest -m "not slow and not integration" --fail-fast

# Paso 2: tests de integración (solo si paso 1 pasó)
pytest -m integration
```

### Fail fast

Usar `--fail-fast` o `-x` en CI para detener la ejecución en el
primer fallo. Esto ahorra minutos de computación cuando un test
fundamental falla.

```bash
pytest -x --tb=short
```
