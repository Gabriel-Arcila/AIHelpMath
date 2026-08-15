# Fixtures Avanzadas: Scopes, Factories y conftest.py

Referencia especializada para el dominio completo del sistema de
fixtures de pytest.

## Tabla de contenidos

1. [Scopes y ciclo de vida](#1-scopes-y-ciclo-de-vida)
2. [conftest.py jerárquico](#2-conftestpy-jerárquico)
3. [Factory fixtures](#3-factory-fixtures)
4. [Fixtures parametrizadas](#4-fixtures-parametrizadas)
5. [Composición de fixtures](#5-composición-de-fixtures)
6. [Teardown robusto con yield](#6-teardown-robusto-con-yield)
7. [Antipatrones comunes](#7-antipatrones-comunes)

---

## 1. Scopes y ciclo de vida

El scope controla cuándo pytest crea y destruye la fixture. Elegir
el scope correcto impacta directamente en el rendimiento y el
aislamiento.

| Scope | Ciclo de vida | Cuándo usarlo |
|---|---|---|
| `function` | Se crea/destruye por cada test | Aislamiento total (default) |
| `class` | Se comparte dentro de una clase | Tests que comparten estado de clase |
| `module` | Se comparte dentro de un archivo | Setup costoso por módulo |
| `package` | Se comparte dentro de un paquete | Setup costoso por directorio |
| `session` | Se crea una vez para toda la sesión | Inicializaciones muy costosas (DB, servicios) |

```python
import pytest


@pytest.fixture(scope="session")
def db_engine():
    """
    Engine de base de datos compartido por toda la sesión.

    Se crea una sola vez al inicio y se destruye al final.
    Usar scope session porque crear un engine es costoso.

    Yields:
        Engine: Engine de SQLAlchemy.
    """
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Sesión de base de datos aislada por test.

    Cada test obtiene su propia sesión con transacción
    independiente que se revierte al finalizar.

    Args:
        db_engine: Engine compartido de la sesión.

    Yields:
        Session: Sesión aislada con rollback.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    transaction.rollback()
    connection.close()
```

### Regla de jerarquía de scopes

Una fixture no puede depender de otra con scope más estrecho.
Un fixture `session` no puede solicitar un fixture `function`,
pero un fixture `function` sí puede solicitar uno `session`.

```
session → package → module → class → function
(más amplio)                    (más estrecho)
```

---

## 2. conftest.py jerárquico

Los archivos `conftest.py` forman una jerarquía de herencia. pytest
los descubre automáticamente sin necesidad de importarlos. Cada
nivel de directorio puede tener su propio `conftest.py`.

```
tests/
├── conftest.py              # Fixtures globales (db, client)
├── test_users/
│   ├── conftest.py          # Fixtures de usuarios (sample_user)
│   └── test_service.py
├── test_items/
│   ├── conftest.py          # Fixtures de items (sample_item)
│   └── test_service.py
└── test_auth/
    ├── conftest.py          # Fixtures de auth (auth_headers)
    └── test_login.py
```

### Reglas del conftest.py

1. **No importar fixtures**: pytest las inyecta por nombre. Si
   importas directamente, rompes el mecanismo de descubrimiento.
2. **Especificidad**: Las fixtures globales van en el conftest raíz.
   Las específicas de un dominio van en el conftest del subdirectorio.
3. **Sobrescritura**: Un conftest hijo puede redefinir una fixture
   del padre. La versión más cercana al test gana.
4. **Sin lógica de negocio**: conftest solo contiene fixtures y
   hooks de pytest. No incluir funciones utilitarias de producción.

### Ejemplo de conftest raíz

```python
import pytest


@pytest.fixture
def api_url():
    """
    URL base para las pruebas de API.

    Returns:
        str: URL del servidor de pruebas.
    """
    return "http://test"


@pytest.fixture
def auth_headers():
    """
    Headers de autenticación para pruebas.

    Returns:
        dict: Headers con token Bearer de prueba.
    """
    return {
        "Authorization": "Bearer test-token-12345"
    }
```

### Ejemplo de conftest específico

```python
# tests/test_users/conftest.py
import pytest


@pytest.fixture
def sample_user():
    """
    Usuario de prueba para el módulo de usuarios.

    Returns:
        dict: Datos del usuario de prueba.
    """
    return {
        "name": "Ana López",
        "email": "ana@example.com",
        "role": "editor",
    }


@pytest.fixture
def sample_admin():
    """
    Administrador de prueba.

    Returns:
        dict: Datos del administrador de prueba.
    """
    return {
        "name": "Admin",
        "email": "admin@example.com",
        "role": "admin",
    }
```

---

## 3. Factory fixtures

Cuando necesitas crear múltiples instancias con variaciones, las
factory fixtures devuelven una función creadora en lugar de un dato
fijo. Esto da control al test sobre los parámetros.

```python
import pytest


@pytest.fixture
def make_user():
    """
    Fábrica de usuarios de prueba.

    Permite crear usuarios con parámetros personalizados,
    con valores por defecto sensatos.

    Returns:
        Callable: Función que crea diccionarios de usuario.
    """
    created_users = []

    def _make_user(
        name: str = "Test User",
        email: str = "test@example.com",
        role: str = "viewer",
    ) -> dict:
        """
        Crea un usuario de prueba.

        Args:
            name (str): Nombre del usuario.
            email (str): Correo del usuario.
            role (str): Rol del usuario.

        Returns:
            dict: Datos del usuario creado.
        """
        user = {
            "name": name,
            "email": email,
            "role": role,
        }
        created_users.append(user)
        return user

    yield _make_user
    # Teardown: limpiar los usuarios creados
    created_users.clear()


def test_multiple_users(make_user) -> None:
    """Verifica la creación de múltiples usuarios."""
    admin = make_user(name="Admin", role="admin")
    viewer = make_user(name="Viewer", role="viewer")

    assert admin["role"] == "admin"
    assert viewer["role"] == "viewer"
```

La razón de usar factory fixtures en lugar de múltiples fixtures
fijas es la flexibilidad. Un test que necesita un usuario con email
duplicado puede crearlo ad hoc sin definir otra fixture.

---

## 4. Fixtures parametrizadas

Cuando el setup mismo necesita variar (no solo los datos de entrada),
usar `params` en `@pytest.fixture`.

```python
import pytest


@pytest.fixture(
    params=["sqlite", "postgresql"],
    ids=["sqlite", "postgres"],
)
def database(request):
    """
    Fixture parametrizada que proporciona diferentes backends.

    Cada test que use esta fixture se ejecutará dos veces:
    una con SQLite y otra con PostgreSQL.

    Args:
        request: Objeto request de pytest con los parámetros.

    Yields:
        Database: Conexión al backend seleccionado.
    """
    db = connect_to(request.param)
    yield db
    db.disconnect()


def test_insert_record(database) -> None:
    """Verifica inserción en ambos backends de base de datos."""
    database.insert({"key": "value"})
    result = database.get("key")
    assert result == "value"
```

La diferencia con `@pytest.mark.parametrize` es que la
parametrización de fixtures controla la fase de **setup**, mientras
que `parametrize` controla la fase de **datos de entrada**.

---

## 5. Composición de fixtures

Las fixtures pueden depender de otras fixtures, formando un grafo
de dependencias. pytest resuelve el grafo automáticamente.

```python
import pytest


@pytest.fixture
def db_session():
    """Sesión de base de datos aislada."""
    session = create_test_session()
    yield session
    session.rollback()


@pytest.fixture
def user_repository(db_session):
    """
    Repositorio de usuarios con sesión inyectada.

    Args:
        db_session: Sesión de base de datos.

    Returns:
        UserRepository: Repositorio configurado.
    """
    return UserRepository(db_session)


@pytest.fixture
def user_service(db_session, user_repository):
    """
    Servicio de usuarios con dependencias inyectadas.

    Args:
        db_session: Sesión de base de datos.
        user_repository: Repositorio de usuarios.

    Returns:
        UserService: Servicio configurado.
    """
    return UserService(db_session, user_repository)


def test_create_user(user_service, make_user) -> None:
    """Verifica que el servicio crea un usuario."""
    user_data = make_user(name="Test")
    result = user_service.create(user_data)
    assert result.name == "Test"
```

### Caché de fixtures

pytest invoca una fixture una sola vez por solicitud (dentro de su
scope) y reutiliza el resultado. Si `db_session` aparece en
`user_repository` y `user_service`, ambos reciben la misma instancia.

Para desactivar el caché en casos excepcionales:
```python
@pytest.fixture(autouse=False)
def unique_id():
    """Genera un ID único en cada invocación."""
    return uuid4()
```

---

## 6. Teardown robusto con yield

La fase de teardown (después del `yield`) se ejecuta siempre, incluso
si el test falla. Esto es crítico para recursos que deben liberarse.

```python
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_directory():
    """
    Directorio temporal aislado para el test.

    Se crea antes del test y se elimina completamente
    después, sin importar si el test pasó o falló.

    Yields:
        Path: Ruta al directorio temporal.
    """
    dir_path = Path(tempfile.mkdtemp())
    yield dir_path
    # Teardown: eliminar incluso si el test falló
    shutil.rmtree(dir_path, ignore_errors=True)


@pytest.fixture
def mock_server():
    """
    Servidor mock que se inicia y detiene automáticamente.

    Yields:
        MockServer: Instancia del servidor mock.
    """
    server = MockServer(port=8888)
    server.start()
    yield server
    server.stop()
```

### Teardown con try-finally

Para fixtures que necesitan garantías extra de limpieza, usar
`try-finally` dentro del generador.

```python
@pytest.fixture
def database_with_data(db_session):
    """
    Base de datos con datos de prueba precargados.

    Args:
        db_session: Sesión de base de datos.

    Yields:
        Session: Sesión con datos precargados.
    """
    try:
        db_session.execute("INSERT INTO ...")
        yield db_session
    finally:
        db_session.execute("DELETE FROM ...")
        db_session.commit()
```

---

## 7. Antipatrones comunes

### ❌ Importar fixtures directamente

```python
# ❌ INCORRECTO
from tests.conftest import db_session

def test_something(db_session):
    ...
```

pytest las descubre automáticamente por nombre. Importarlas
puede causar conflictos e instancias duplicadas.

### ❌ Fixtures con efectos secundarios globales

```python
# ❌ INCORRECTO — modifica estado global
@pytest.fixture
def set_env():
    os.environ["KEY"] = "value"
    # Sin yield ni cleanup
```

Siempre limpiar en el teardown para evitar contaminación entre
tests.

### ❌ Fixtures scope session con estado mutable

```python
# ❌ INCORRECTO — lista compartida entre tests
@pytest.fixture(scope="session")
def shared_list():
    return []  # Todos los tests modifican la misma lista
```

Las fixtures de scope amplio deben ser inmutables o de solo lectura.
Si el test necesita mutar datos, usar scope `function`.

### ❌ Lógica condicional compleja en fixtures

```python
# ❌ INCORRECTO — demasiada lógica
@pytest.fixture
def user(request):
    if request.param == "admin":
        ...
    elif request.param == "editor":
        ...
    elif request.param == "viewer":
        ...
```

Prefiere factory fixtures o fixtures parametrizadas con `params`.
