# Testing: Pytest Asíncrono, Fixtures y Convenciones

Referencia especializada para la escritura de pruebas unitarias e
integración en aplicaciones FastAPI.

## Tabla de contenidos

1. [Configuración de pytest](#1-configuración-de-pytest)
2. [Fixtures globales (conftest.py)](#2-fixtures-globales-conftestpy)
3. [Rollback transaccional por test](#3-rollback-transaccional-por-test)
4. [Pruebas de endpoints](#4-pruebas-de-endpoints)
5. [Pruebas de servicios](#5-pruebas-de-servicios)
6. [Inyección de dependencias en tests](#6-inyección-de-dependencias-en-tests)
7. [Parametrización y excepciones](#7-parametrización-y-excepciones)

---

## 1. Configuración de pytest

### pyproject.toml

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
```

### Dependencias de testing

```
pytest
pytest-asyncio
httpx
```

### Convenciones de nomenclatura

| Elemento | Regla |
|---|---|
| Archivos | Prefijo `test_` (ej. `test_router.py`) |
| Funciones | Prefijo `test_` (ej. `test_create_user`) |
| Clases | Prefijo `Test` (ej. `TestUserService`) |
| Imports | Dependencia absoluta siempre |

---

## 2. Fixtures globales (conftest.py)

El archivo `conftest.py` en la raíz de `tests/` contiene las fixtures
compartidas por todas las pruebas.

```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.database import Base
from src.core.dependencies import get_db
from src.main import app


TEST_DATABASE_URL = (
    "postgresql+asyncpg://test:test@localhost:5432/test_db"
)

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
)

async_session_test = async_sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
async def setup_database():
    """
    Crea y destruye las tablas de la base de datos de test.

    Se ejecuta una sola vez por sesión de pytest.

    Yields:
        None: Las tablas existen durante la sesión.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()


@pytest.fixture
async def db_session(setup_database):
    """
    Proporciona una sesión de base de datos con rollback.

    Cada test ejecuta dentro de una transacción que se
    revierte al finalizar, garantizando aislamiento total.

    Yields:
        AsyncSession: Sesión de test aislada.
    """
    async with engine_test.connect() as connection:
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


@pytest.fixture
async def client(db_session):
    """
    Cliente HTTP asíncrono para pruebas de endpoints.

    Sobreescribe la dependencia de base de datos para usar
    la sesión de test con rollback automático.

    Args:
        db_session (AsyncSession): Sesión de test aislada.

    Yields:
        AsyncClient: Cliente HTTP configurado.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Reglas de las fixtures

- Usar fixtures en lugar de `setup`/`teardown`.
- Limpiar `app.dependency_overrides` en el `finally` o al final
  de la fixture para evitar contaminación entre tests.
- Usar `scope="session"` solo para recursos costosos (crear tablas).
- Cada fixture individual debe tener scope por defecto (`function`).

---

## 3. Rollback transaccional por test

El patrón de rollback utiliza `connection.begin()` para crear una
transacción contenedora. Al finalizar el test, se ejecuta
`transaction.rollback()` en lugar de `DROP TABLES`, lo cual es
órdenes de magnitud más rápido.

La razón de usar `begin_nested()` para savepoints es que permite
que el código bajo prueba llame a `commit()` sin que la transacción
contenedora se confirme realmente. El commit del servicio actúa
sobre el savepoint, no sobre la transacción principal.

```python
@pytest.fixture
async def db_session_with_savepoint(setup_database):
    """
    Sesión con savepoints para código que llama commit().

    Permite que los servicios ejecuten commit() normalmente
    mientras la transacción principal se revierte al final.

    Yields:
        AsyncSession: Sesión con savepoint activo.
    """
    async with engine_test.connect() as connection:
        transaction = await connection.begin()
        nested = await connection.begin_nested()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        @event.listens_for(
            session.sync_session, "after_transaction_end"
        )
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()

        try:
            yield session
        finally:
            await transaction.rollback()
            await session.close()
```

---

## 4. Pruebas de endpoints

Las pruebas de endpoints usan `httpx.AsyncClient` con
`ASGITransport` para ejecutar las solicitudes sin un servidor
de red real. Esto es más rápido y seguro.

```python
import pytest
from httpx import AsyncClient


class TestUserRouter:
    """Pruebas para los endpoints de usuarios."""

    async def test_create_user_returns_201(
        self,
        client: AsyncClient,
    ) -> None:
        """Verifica que crear un usuario retorna 201."""
        # Arrange
        user_data = {
            "name": "Juan Pérez",
            "email": "juan@example.com",
        }

        # Act
        response = await client.post(
            "/v1/users/",
            json=user_data,
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Juan Pérez"
        assert data["email"] == "juan@example.com"
        assert "id" in data

    async def test_create_user_invalid_email_returns_422(
        self,
        client: AsyncClient,
    ) -> None:
        """Verifica que un email inválido retorna 422."""
        # Arrange
        user_data = {
            "name": "Juan Pérez",
            "email": "correo-invalido",
        }

        # Act
        response = await client.post(
            "/v1/users/",
            json=user_data,
        )

        # Assert
        assert response.status_code == 422

    async def test_get_user_not_found_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        """Verifica que buscar un usuario inexistente retorna 404."""
        # Act
        response = await client.get("/v1/users/99999")

        # Assert
        assert response.status_code == 404
```

### Patrón AAA obligatorio

Cada prueba sigue el patrón **Arrange-Act-Assert**:

1. **Arrange**: Configurar estado inicial, crear datos de entrada.
2. **Act**: Ejecutar la operación bajo prueba.
3. **Assert**: Verificar el resultado esperado.

---

## 5. Pruebas de servicios

Las pruebas de la capa de servicios son unitarias y aíslan la lógica
de negocio de los detalles de infraestructura.

```python
import pytest
from unittest.mock import AsyncMock

from src.users.service import UserService
from src.users.schemas import SchemaUserCreate


class TestUserService:
    """Pruebas unitarias del servicio de usuarios."""

    @pytest.fixture
    def mock_session(self):
        """
        Sesión mock para pruebas unitarias.

        Returns:
            AsyncMock: Sesión simulada.
        """
        session = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def mock_repository(self):
        """
        Repositorio mock para pruebas unitarias.

        Returns:
            AsyncMock: Repositorio simulado.
        """
        return AsyncMock()

    async def test_create_calls_commit(
        self,
        mock_session,
        mock_repository,
    ) -> None:
        """Verifica que crear un usuario confirma la transacción."""
        # Arrange
        service = UserService(mock_session, mock_repository)
        user_data = SchemaUserCreate(
            name="Ana",
            email="ana@example.com",
        )

        # Act
        await service.create(user_data)

        # Assert
        mock_repository.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
```

---

## 6. Inyección de dependencias en tests

El mecanismo `app.dependency_overrides` permite reemplazar cualquier
dependencia durante las pruebas. Es fundamental limpiar las
sobreescrituras al finalizar para evitar contaminación.

```python
from src.core.dependencies import get_db
from src.users.dependencies import get_current_user
from src.main import app


async def override_get_db():
    """Proveedor de sesión de test."""
    yield db_session_test


async def override_get_current_user():
    """Proveedor de usuario autenticado de test."""
    return fake_user


# Configurar
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = (
    override_get_current_user
)

# Limpiar al finalizar
app.dependency_overrides.clear()
```

La razón de limpiar siempre los overrides es que el diccionario
`dependency_overrides` es global y mutable. Si un test lo modifica
sin limpiarlo, todos los tests posteriores se ejecutan con la
dependencia incorrecta, causando fallos difíciles de diagnosticar.

---

## 7. Parametrización y excepciones

### Pruebas parametrizadas

Evitar la duplicación de código con `@pytest.mark.parametrize`.

```python
import pytest


class TestSchemaValidation:
    """Pruebas de validación de esquemas Pydantic."""

    @pytest.mark.parametrize(
        "email,is_valid",
        [
            ("usuario@example.com", True),
            ("admin@empresa.org", True),
            ("correo-invalido", False),
            ("", False),
            ("@sinusuario.com", False),
        ],
    )
    async def test_email_validation(
        self,
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
            user = SchemaUserCreate(
                name="Test",
                email=email,
            )
            assert user.email == email.lower()
        else:
            with pytest.raises(ValueError):
                SchemaUserCreate(
                    name="Test",
                    email=email,
                )
```

### Pruebas de excepciones

Usar `pytest.raises` para verificar que las excepciones se lanzan
correctamente.

```python
import pytest

from src.core.exceptions import NotFoundException
from src.users.service import UserService


class TestUserServiceExceptions:
    """Pruebas de excepciones del servicio de usuarios."""

    async def test_get_nonexistent_raises_not_found(
        self,
        mock_session,
        mock_repository,
    ) -> None:
        """Verifica que buscar un usuario inexistente lanza excepción."""
        # Arrange
        mock_repository.get_by_id.return_value = None
        service = UserService(mock_session, mock_repository)

        # Act & Assert
        with pytest.raises(NotFoundException):
            await service.get_by_id(99999)
```
