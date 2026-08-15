# Testing Asíncrono: pytest-asyncio y Patrones Async

Referencia especializada para escribir pruebas de código asíncrono
con pytest-asyncio.

## Tabla de contenidos

1. [Configuración de pytest-asyncio](#1-configuración-de-pytest-asyncio)
2. [Fixtures asíncronas](#2-fixtures-asíncronas)
3. [Cliente async para APIs (httpx)](#3-cliente-async-para-apis-httpx)
4. [Rollback transaccional async](#4-rollback-transaccional-async)
5. [Errores comunes async](#5-errores-comunes-async)

---

## 1. Configuración de pytest-asyncio

### pyproject.toml

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

| Opción | Efecto |
|---|---|
| `asyncio_mode = "auto"` | Detecta tests async automáticamente, sin necesidad de `@pytest.mark.asyncio` en cada test |
| `asyncio_default_fixture_loop_scope = "function"` | Cada test obtiene su propio event loop, previniendo fugas de estado |

### Dependencias necesarias

```
pytest-asyncio
httpx
```

### Modo auto vs explícito

Con `asyncio_mode = "auto"`, cualquier función `async def test_*`
se ejecuta como test asíncrono automáticamente:

```python
# ✅ Con modo auto: no necesita marcador
async def test_async_operation() -> None:
    """Verifica una operación asíncrona."""
    result = await fetch_data()
    assert result is not None
```

La razón de preferir modo `auto` es que reduce el boilerplate.
En equipos grandes, agregar `@pytest.mark.asyncio` en cada test es
una fuente constante de olvidos que generan errores confusos.

---

## 2. Fixtures asíncronas

Las fixtures pueden ser `async def` para realizar setup asíncrono.

```python
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@pytest.fixture(scope="session")
async def async_engine():
    """
    Engine asíncrono compartido por toda la sesión de tests.

    Se crea una sola vez y se libera al finalizar.

    Yields:
        AsyncEngine: Engine de SQLAlchemy asíncrono.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine):
    """
    Sesión asíncrona aislada por test.

    Cada test recibe su propia sesión con transacción
    que se revierte al finalizar.

    Args:
        async_engine: Engine asíncrono compartido.

    Yields:
        AsyncSession: Sesión aislada con rollback.
    """
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )
        try:
            yield session
        finally:
            await transaction.rollback()
            await session.close()
```

### Regla de scope del event loop

Cuando usas fixtures con `scope="session"`, el event loop debe
coincidir. Configura `asyncio_default_fixture_loop_scope` o usa
la fixture `event_loop_policy` para controlar el ciclo de vida
del loop.

---

## 3. Cliente async para APIs (httpx)

Para testear aplicaciones ASGI (FastAPI, Starlette), usar
`httpx.AsyncClient` con `ASGITransport`. Esto ejecuta las requests
sin un servidor de red real — más rápido y sin conflictos de puertos.

```python
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.dependencies import get_db


@pytest.fixture
async def client(async_session):
    """
    Cliente HTTP asíncrono para pruebas de endpoints.

    Sobreescribe la dependencia de base de datos para usar
    la sesión de test con rollback automático.

    Args:
        async_session: Sesión de base de datos aislada.

    Yields:
        AsyncClient: Cliente HTTP configurado.
    """

    async def override_get_db():
        """Proveedor de sesión de test."""
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Uso en tests

```python
async def test_create_item_returns_201(
    client: AsyncClient,
) -> None:
    """Verifica que crear un item retorna 201."""
    # Arrange
    item_data = {
        "name": "Widget",
        "price": 29.99,
    }

    # Act
    response = await client.post(
        "/v1/items/",
        json=item_data,
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"


async def test_list_items_with_auth(
    client: AsyncClient,
    auth_headers: dict,
) -> None:
    """Verifica que listar items requiere autenticación."""
    # Act
    response = await client.get(
        "/v1/items/",
        headers=auth_headers,
    )

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Reglas del cliente async

1. **Siempre usar `async with`**: Garantiza que las conexiones
   HTTP se cierren correctamente.
2. **Limpiar dependency_overrides**: Llamar `.clear()` al final
   para evitar contaminación entre tests.
3. **No mezclar clientes sync/async**: Usar TestClient síncrono
   con código async produce resultados inconsistentes.

---

## 4. Rollback transaccional async

El patrón de rollback transaccional es fundamental para tests de
integración con base de datos real. Cada test ejecuta dentro de una
transacción que se revierte al finalizar, sin necesidad de
`DROP TABLE`.

### Patrón con savepoints

Cuando el código bajo prueba llama a `commit()` (como un servicio),
se necesitan savepoints para que el commit actúe sobre un punto
guardado, no sobre la transacción principal.

```python
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def db_session_with_savepoint(async_engine):
    """
    Sesión con savepoints para código que llama commit().

    Permite que los servicios ejecuten commit()
    normalmente mientras la transacción principal se
    revierte al final del test.

    Args:
        async_engine: Engine asíncrono compartido.

    Yields:
        AsyncSession: Sesión con savepoint activo.
    """
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        await connection.begin_nested()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        @event.listens_for(
            session.sync_session,
            "after_transaction_end",
        )
        def restart_savepoint(sync_session, trans):
            """Reinicia el savepoint tras cada commit."""
            if trans.nested and not trans._parent.nested:
                sync_session.begin_nested()

        try:
            yield session
        finally:
            await transaction.rollback()
            await session.close()
```

La razón de usar savepoints es que el servicio llama a
`session.commit()` como parte de su lógica normal. Sin savepoints,
ese commit confirmaría la transacción principal y los datos
persistirían entre tests. Con savepoints, el commit actúa sobre el
savepoint anidado, y la transacción contenedora se revierte al
final, limpiando todo.

---

## 5. Errores comunes async

### ❌ Olvidar await

```python
# ❌ INCORRECTO — coroutine sin ejecutar
async def test_bad_await(client) -> None:
    response = client.get("/v1/items/")  # Falta await
    assert response.status_code == 200   # AttributeError
```

```python
# ✅ CORRECTO
async def test_good_await(client) -> None:
    response = await client.get("/v1/items/")
    assert response.status_code == 200
```

### ❌ Código bloqueante en test async

```python
# ❌ INCORRECTO — bloquea el event loop
import time

async def test_blocking(client) -> None:
    time.sleep(1)  # Bloquea todo el loop
    response = await client.get("/v1/items/")
```

```python
# ✅ CORRECTO
import asyncio

async def test_non_blocking(client) -> None:
    await asyncio.sleep(1)  # No bloquea
    response = await client.get("/v1/items/")
```

### ❌ Mezclar TestClient sync con app async

```python
# ❌ INCORRECTO — TestClient es síncrono
from fastapi.testclient import TestClient

def test_mixed(db_session) -> None:
    client = TestClient(app)
    response = client.get("/v1/items/")
    # Puede funcionar pero pierde cobertura async
```

```python
# ✅ CORRECTO — AsyncClient con ASGITransport
from httpx import ASGITransport, AsyncClient

async def test_async_proper() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/v1/items/")
```

### ❌ Event loop compartido entre tests

Si los tests comparten event loop (scope session), un test que
corrompa el loop afecta a todos los siguientes. Usar scope `function`
por defecto:

```toml
asyncio_default_fixture_loop_scope = "function"
```

### Timeouts para tests async

Los tests async pueden colgar indefinidamente si una coroutine nunca
completa. Integrar `pytest-timeout` para fallar rápidamente:

```toml
[tool.pytest.ini_options]
timeout = 30
```

```python
@pytest.mark.timeout(5)
async def test_should_be_fast(client) -> None:
    """Test que debe completar en menos de 5 segundos."""
    response = await client.get("/v1/health/")
    assert response.status_code == 200
```
