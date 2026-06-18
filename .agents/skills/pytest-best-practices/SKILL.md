---
name: pytest-best-practices
description: >-
  Guía completa de mejores prácticas para escribir pruebas con pytest
  en cualquier proyecto Python. Cubre el patrón AAA, fixtures con
  yield y scopes, conftest.py jerárquico, parametrización avanzada,
  manejo de excepciones con pytest.raises y match, monkeypatch,
  pytest-mock, pruebas asíncronas con pytest-asyncio, tolerancias
  numéricas con pytest.approx, plugins esenciales (xdist, cov,
  randomly), configuración estricta en pyproject.toml, y estrategias
  de CI/CD con JUnit XML. Usa esta skill siempre que el usuario
  necesite escribir pruebas unitarias o de integración, configurar
  pytest, crear fixtures, parametrizar tests, hacer mocking, testear
  código asíncrono, o integrar pytest en pipelines de CI/CD. También
  aplica cuando se mencionen conceptos como "tests en Python",
  "pruebas unitarias", "coverage", "test fixtures", "mocks",
  "testing asíncrono", o cualquier referencia a pytest y su ecosistema.
---

# Pytest Best Practices

Skill para escribir pruebas robustas, mantenibles y de alto
rendimiento con pytest en proyectos Python de cualquier escala.

## Cuándo leer archivos de referencia

Esta skill incluye archivos especializados en `references/`. Consulta
el archivo relevante según la tarea:

| Archivo | Cuándo leerlo |
|---|---|
| `references/fixtures.md` | Crear fixtures, conftest.py, scopes, yield, factory fixtures |
| `references/mocking.md` | Monkeypatch, pytest-mock, parches, simulaciones de red |
| `references/async_testing.md` | Pruebas asíncronas con pytest-asyncio, clientes async |
| `references/ci_cd.md` | Plugins, pytest-xdist, cobertura, pipelines CI/CD, JUnit XML |

Lee solo el archivo que necesites para la tarea actual.

---

## 1. Fundamentos de pytest

pytest reemplaza a frameworks más rígidos como `unittest` gracias a
su sistema de inyección de dependencias modular (fixtures) y la
reescritura del Árbol de Sintaxis Abstracta (AST) que habilita el
uso de la instrucción nativa `assert` con introspección contextualizada.

Cuando un `assert` falla, pytest genera automáticamente un análisis
diferencial detallado de las variables, mostrando exactamente qué
valor se esperaba y qué valor se obtuvo, sin necesidad de métodos
especiales como `assertEqual` o `assertIn`.

---

## 2. Convenciones de nomenclatura

| Elemento | Regla | Ejemplo |
|---|---|---|
| Archivos | Prefijo `test_` | `test_users.py` |
| Funciones | Prefijo `test_` | `test_create_user` |
| Clases | Prefijo `Test` | `TestUserService` |
| Imports | Dependencia absoluta | `from src.users.service import UserService` |

Las clases de test no requieren herencia de ninguna clase base.
pytest las descubre automáticamente por el prefijo `Test`.

---

## 3. El patrón AAA (Arrange-Act-Assert)

Toda prueba sigue esta estructura de tres fases claramente
separadas. Es la base de una prueba legible y mantenible.

```python
async def test_create_user_returns_correct_name(
    client,
) -> None:
    """Verifica que crear un usuario retorna el nombre correcto."""
    # Arrange — configurar estado inicial
    user_data = {
        "name": "Ana López",
        "email": "ana@example.com",
    }

    # Act — ejecutar la operación bajo prueba
    response = await client.post(
        "/v1/users/",
        json=user_data,
    )

    # Assert — verificar el resultado esperado
    assert response.status_code == 201
    assert response.json()["name"] == "Ana López"
```

### Reglas del patrón AAA

- Cada fase debe ser visualmente distinguible (comentarios o
  separación con línea en blanco).
- **Arrange**: Inicializa variables, crea objetos, configura
  fixtures. No debe contener lógica de negocio.
- **Act**: Una sola operación. Si necesitas más de una, considera
  dividir en dos tests.
- **Assert**: Verificaciones específicas y atómicas. Evitar asserts
  redundantes que verifican lo mismo de distinta forma.

---

## 4. Configuración en pyproject.toml

Centralizar toda la configuración de pytest en `pyproject.toml`.
No usar archivos `pytest.ini`, `setup.cfg` ni `tox.ini` para la
configuración de pytest.

```toml
[tool.pytest.ini_options]
# Modo de importación: evita colisiones de nombres
addopts = "--import-mode=importlib --strict-markers"
# Directorios donde buscar tests
testpaths = ["tests"]
# Descubrimiento automático
python_files = ["test_*.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
# Marcadores estrictos: error si usas un marcador no registrado
markers = [
    "slow: pruebas lentas que no se ejecutan por defecto",
    "integration: pruebas de integración con servicios externos",
]
# Fallos esperados estrictos: xpass es error
xfail_strict = true
# Advertencias como errores: fuerza actualización temprana
filterwarnings = ["error"]
# Modo asyncio automático (si usas pytest-asyncio)
asyncio_mode = "auto"
```

### Explicación de las opciones estrictas

| Opción | Efecto |
|---|---|
| `--strict-markers` | Un marcador no registrado genera error fatal |
| `--import-mode=importlib` | Elimina colisiones de nombres entre módulos y no requiere `__init__.py` en tests |
| `xfail_strict = true` | Si una prueba `xfail` pasa inesperadamente, falla el test |
| `filterwarnings = ["error"]` | Convierte `DeprecationWarning` en fallos, forzando actualización de dependencias |

La razón de activar `--strict-markers` es que un marcador con typo
(`@pytest.mark.solw` en vez de `@pytest.mark.slow`) se ejecutaría
silenciosamente sin filtrar nada. Con marcadores estrictos, pytest
te alerta inmediatamente del error.

---

## 5. Estructura de directorios (src layout)

El patrón *src layout* aísla el código importable en `src/` y las
pruebas en `tests/`, impidiendo importaciones implícitas accidentales.

```
proyecto/
├── src/
│   ├── __init__.py
│   └── users/
│       ├── __init__.py
│       ├── service.py
│       └── models.py
├── tests/
│   ├── conftest.py          # Fixtures globales
│   ├── test_users/
│   │   ├── conftest.py      # Fixtures específicas de users
│   │   ├── test_service.py
│   │   └── test_models.py
│   └── test_items/
│       └── test_service.py
├── pyproject.toml
└── .env.test
```

### Reglas estructurales

1. **`tests/` replica la estructura de `src/`**: Facilita localizar
   los tests de cada módulo.
2. **`conftest.py` jerárquico**: Fixtures globales en la raíz de
   `tests/`, fixtures específicas en cada subdirectorio.
3. **No importar fixtures desde conftest**: pytest las descubre
   automáticamente. Importarlas rompe el mecanismo de inyección.
4. **Cada test es independiente**: No debe depender del orden de
   ejecución ni de efectos secundarios de otro test.

---

## 6. Fixtures básicas con yield

Las fixtures reemplazan los métodos `setup`/`teardown`. Usan `yield`
para separar la fase de preparación (antes del yield) de la fase de
limpieza (después del yield).

```python
import pytest


@pytest.fixture
def sample_user():
    """
    Proporciona un usuario de prueba.

    Yields:
        dict: Datos del usuario de prueba.
    """
    user = {
        "name": "Test User",
        "email": "test@example.com",
    }
    yield user
    # Teardown: limpiar recursos si es necesario
```

La razón de preferir `yield` sobre `return` es que el código después
del `yield` se ejecuta siempre como limpieza, incluso si el test
falla con una excepción. Esto garantiza que los recursos se liberen
correctamente.

Para patrones avanzados de fixtures (scopes, factory fixtures,
fixtures parametrizadas), consultar `references/fixtures.md`.

---

## 7. Parametrización

Evita la duplicación de tests que solo difieren en los datos de
entrada. `@pytest.mark.parametrize` ejecuta la misma lógica contra
múltiples escenarios.

```python
import pytest


@pytest.mark.parametrize(
    "email,is_valid",
    [
        ("user@example.com", True),
        ("admin@empresa.org", True),
        ("correo-invalido", False),
        ("", False),
        ("@sin-usuario.com", False),
    ],
    ids=[
        "email_valido_comun",
        "email_valido_org",
        "sin_arroba",
        "vacio",
        "sin_usuario",
    ],
)
def test_email_validation(
    email: str,
    is_valid: bool,
) -> None:
    """
    Verifica la validación del campo email.

    Args:
        email (str): Correo a validar.
        is_valid (bool): Si se espera que sea válido.
    """
    if is_valid:
        result = validate_email(email)
        assert result is True
    else:
        with pytest.raises(ValueError):
            validate_email(email)
```

### Reglas de parametrización

- **Usar `ids`**: Asignar identificadores semánticos a cada caso.
  En la terminal aparecerá `test_email_validation[email_valido_comun]`
  en lugar de `test_email_validation[user@example.com-True]`.
- **No anidar excesivamente**: Apilar múltiples `@parametrize` genera
  explosión combinatoria. Si necesitas más de 20 combinaciones,
  replantea la estrategia.
- **Parametrizar fixtures**: Cuando necesitas parametrizar la fase de
  setup (no solo los datos), usa `params` en `@pytest.fixture`.

---

## 8. Manejo de excepciones

### pytest.raises con match

Usar `pytest.raises` para verificar que una excepción se lanza
correctamente. Acotar el bloque `with` exclusivamente a la
instrucción que genera la excepción.

```python
import pytest


def test_division_by_zero_raises_error() -> None:
    """Verifica que dividir por cero lanza ZeroDivisionError."""
    # Act & Assert
    with pytest.raises(
        ZeroDivisionError,
        match=r"division by zero",
    ):
        divide(10, 0)


def test_negative_age_raises_value_error() -> None:
    """Verifica que una edad negativa lanza ValueError."""
    with pytest.raises(
        ValueError,
        match=r"La edad debe ser positiva",
    ):
        create_person(name="Ana", age=-5)
```

### Reglas de excepciones

- **Tipo exacto**: Siempre especificar el tipo de excepción concreto
  (`ValueError`, no `Exception`).
- **`match` con regex**: Confirmar que el mensaje del error coincide
  con el estímulo esperado, no con otro error del mismo tipo.
- **Bloque mínimo**: El `with pytest.raises(...)` debe contener
  solo la línea que genera la excepción. Si envuelve demasiado
  código, una excepción inesperada podría pasar como válida.

---

## 9. Tolerancias numéricas

Los errores de punto flotante (IEEE 754) causan que comparaciones
como `0.1 + 0.2 == 0.3` fallen. Usar `pytest.approx` para manejar
tolerancias.

```python
import pytest


def test_calculation_with_tolerance() -> None:
    """Verifica cálculos con tolerancia de punto flotante."""
    result = 0.1 + 0.2
    assert result == pytest.approx(0.3)


def test_vector_comparison() -> None:
    """Verifica comparación de vectores con tolerancia."""
    expected = [0.1 + 0.2, 0.2 + 0.4]
    actual = [0.3, 0.6]
    assert actual == pytest.approx(expected)


def test_custom_tolerance() -> None:
    """Verifica con tolerancia personalizada."""
    assert 2.0 + 1e-8 == pytest.approx(2.0, abs=1e-6)
```

`pytest.approx` funciona con escalares, listas y diccionarios. Usa
tolerancias relativas por defecto (`1e-6`), pero acepta tolerancias
absolutas con `abs=` y relativas con `rel=`.

---

## 10. Marcadores personalizados

Los marcadores permiten categorizar y filtrar pruebas.

```python
import pytest


@pytest.mark.slow
def test_heavy_computation() -> None:
    """Prueba que tarda varios segundos."""
    result = compute_large_dataset()
    assert result is not None


@pytest.mark.integration
def test_external_api_connection() -> None:
    """Prueba que requiere conexión a un servicio externo."""
    response = call_external_api()
    assert response.status_code == 200
```

### Ejecutar por marcador

```bash
# Solo pruebas rápidas (excluir lentas)
pytest -m "not slow"

# Solo pruebas de integración
pytest -m integration

# Combinar marcadores
pytest -m "not slow and not integration"
```

Todos los marcadores deben registrarse en `pyproject.toml` bajo
`markers` para que `--strict-markers` funcione correctamente.

---

## Resumen de convenciones

| Aspecto | Regla |
|---|---|
| Patrón de test | AAA (Arrange-Act-Assert) |
| Nomenclatura archivos | `test_*.py` |
| Nomenclatura funciones | `test_*` |
| Nomenclatura clases | `Test*` |
| Imports | Dependencia absoluta |
| Fixtures | `yield` para teardown, no `setup/teardown` |
| Parametrización | `@pytest.mark.parametrize` con `ids` |
| Excepciones | `pytest.raises` con tipo exacto y `match` |
| Punto flotante | `pytest.approx` |
| Configuración | `pyproject.toml` exclusivamente |
| Independencia | Cada test es hermético e independiente |
| Marcadores | Registrados y estrictos |
