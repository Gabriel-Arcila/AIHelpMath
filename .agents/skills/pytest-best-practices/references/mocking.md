# Mocking: monkeypatch, pytest-mock y Parches

Referencia especializada para simulaciones, parches y aislamiento
de dependencias en pruebas.

## Tabla de contenidos

1. [monkeypatch integrado](#1-monkeypatch-integrado)
2. [pytest-mock y el fixture mocker](#2-pytest-mock-y-el-fixture-mocker)
3. [Regla de vinculación de parches](#3-regla-de-vinculación-de-parches)
4. [Patrones comunes de mocking](#4-patrones-comunes-de-mocking)
5. [Cuándo no hacer mock](#5-cuándo-no-hacer-mock)

---

## 1. monkeypatch integrado

`monkeypatch` es una fixture integrada de pytest destinada
exclusivamente a mutaciones ambientales temporales: variables de
entorno, atributos globales y diccionarios.

```python
def test_reads_api_key_from_env(monkeypatch) -> None:
    """Verifica que la configuración lee la API key del entorno."""
    # Arrange
    monkeypatch.setenv("API_KEY", "test-key-123")

    # Act
    config = load_config()

    # Assert
    assert config.api_key == "test-key-123"


def test_missing_env_raises_error(monkeypatch) -> None:
    """Verifica que la ausencia de variable de entorno falla."""
    # Arrange
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Act & Assert
    with pytest.raises(ValueError, match="DATABASE_URL"):
        load_config()
```

### Métodos de monkeypatch

| Método | Propósito |
|---|---|
| `setenv(name, value)` | Establece variable de entorno |
| `delenv(name)` | Elimina variable de entorno |
| `setattr(obj, name, value)` | Modifica atributo de un objeto |
| `delattr(obj, name)` | Elimina atributo de un objeto |
| `setitem(dict, key, value)` | Modifica entrada de un diccionario |
| `delitem(dict, key)` | Elimina entrada de un diccionario |
| `chdir(path)` | Cambia el directorio de trabajo |
| `syspath_prepend(path)` | Agrega ruta al inicio de `sys.path` |

Todos los cambios se revierten automáticamente al finalizar el test.
No se necesita cleanup manual.

### Cuándo usar monkeypatch vs mock

- **monkeypatch**: Variables de entorno, atributos de módulos,
  configuraciones globales. Mutaciones simples sin comportamiento.
- **mock**: Simular comportamiento de funciones y clases.
  Verificar que se llamaron con argumentos específicos.

---

## 2. pytest-mock y el fixture mocker

Para simulaciones complejas (interceptar llamadas de red, simular
respuestas de APIs, verificar interacciones), usar `pytest-mock`
y su fixture `mocker`.

La ventaja sobre `unittest.mock` directo es que `mocker` automatiza
la destrucción del mock al finalizar el test, evitando fugas de
estado entre pruebas.

```python
def test_sends_email_on_registration(mocker) -> None:
    """Verifica que el registro envía un email de bienvenida."""
    # Arrange
    mock_send = mocker.patch(
        "src.users.service.send_welcome_email",
    )
    service = UserService()
    user_data = {"name": "Ana", "email": "ana@example.com"}

    # Act
    service.register(user_data)

    # Assert
    mock_send.assert_called_once_with("ana@example.com")


def test_handles_payment_gateway_error(mocker) -> None:
    """Verifica el manejo de error del gateway de pagos."""
    # Arrange
    mocker.patch(
        "src.payments.service.PaymentGateway.charge",
        side_effect=PaymentError("Tarjeta rechazada"),
    )
    service = PaymentService()

    # Act & Assert
    with pytest.raises(
        PaymentError,
        match="Tarjeta rechazada",
    ):
        service.process_payment(amount=100)
```

### Métodos principales de mocker

| Método | Propósito |
|---|---|
| `mocker.patch(target)` | Reemplaza un objeto con un Mock |
| `mocker.patch.object(obj, attr)` | Reemplaza un atributo de un objeto |
| `mocker.spy(obj, attr)` | Espía una función sin reemplazarla |
| `mocker.stub(name)` | Crea un mock sin target |

### Verificaciones de llamadas

```python
# Verificar que se llamó exactamente una vez
mock_fn.assert_called_once()

# Verificar argumentos específicos
mock_fn.assert_called_once_with("arg1", key="value")

# Verificar que nunca se llamó
mock_fn.assert_not_called()

# Verificar número exacto de llamadas
assert mock_fn.call_count == 3

# Verificar última llamada
mock_fn.assert_called_with("last_arg")
```

---

## 3. Regla de vinculación de parches

Esta es la regla más importante del mocking y la fuente más
frecuente de errores: **parchar donde se consume, no donde se
define**.

### El problema

```python
# src/utils.py
def get_timestamp():
    return datetime.now()

# src/users/service.py
from src.utils import get_timestamp

class UserService:
    def create(self, data):
        data["created_at"] = get_timestamp()
        ...
```

### ❌ Incorrecto — parchar donde se define

```python
# ❌ No funciona: el import ya copió la referencia
mocker.patch("src.utils.get_timestamp")
```

Cuando `service.py` ejecuta `from src.utils import get_timestamp`,
copia la referencia a la función dentro de su propio espacio de
nombres. Parchar el original en `src.utils` no afecta la copia.

### ✅ Correcto — parchar donde se consume

```python
# ✅ Funciona: parcha la referencia local en service.py
mocker.patch(
    "src.users.service.get_timestamp",
    return_value=datetime(2025, 1, 1),
)
```

Al parchar `src.users.service.get_timestamp`, se reemplaza la
referencia que el servicio realmente usa. La regla es: parchar
el nombre completo en el módulo que lo importa.

---

## 4. Patrones comunes de mocking

### Mock de respuestas HTTP

```python
def test_fetches_external_data(mocker) -> None:
    """Verifica que se procesan los datos externos."""
    # Arrange
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "value"}

    mocker.patch(
        "src.clients.external.httpx.get",
        return_value=mock_response,
    )

    # Act
    result = fetch_external_data()

    # Assert
    assert result == {"data": "value"}
```

### Mock con side_effect para secuencias

```python
def test_retry_mechanism(mocker) -> None:
    """Verifica que el retry funciona tras fallos iniciales."""
    # Arrange: falla 2 veces, luego tiene éxito
    mocker.patch(
        "src.clients.api.call_api",
        side_effect=[
            ConnectionError("Timeout"),
            ConnectionError("Refused"),
            {"status": "ok"},
        ],
    )

    # Act
    result = call_with_retry(max_retries=3)

    # Assert
    assert result == {"status": "ok"}
```

### Spy para verificar sin reemplazar

```python
def test_logs_on_creation(mocker) -> None:
    """Verifica que se registra un log al crear usuario."""
    # Arrange — espía sin cambiar el comportamiento
    spy_log = mocker.spy(logger, "info")
    service = UserService()

    # Act
    service.create({"name": "Ana"})

    # Assert
    spy_log.assert_called_once()
    assert "Ana" in str(spy_log.call_args)
```

### AsyncMock para funciones asíncronas

```python
async def test_async_external_call(mocker) -> None:
    """Verifica mock de una función asíncrona."""
    # Arrange
    mocker.patch(
        "src.services.external.fetch_data",
        new_callable=mocker.AsyncMock,
        return_value={"key": "value"},
    )

    # Act
    result = await process_external_data()

    # Assert
    assert result["key"] == "value"
```

---

## 5. Cuándo no hacer mock

El mocking excesivo crea tests que solo verifican la estructura del
código, no su comportamiento real. Los tests se vuelven frágiles
y se rompen con cualquier refactorización.

### No hacer mock de:

- **Modelos Pydantic**: Son objetos de datos puros. Usa instancias
  reales.
- **Funciones utilitarias puras**: Sin efectos secundarios. Testea
  con datos reales.
- **La propia clase bajo prueba**: Si necesitas mockear la clase
  que estás testeando, el test está mal diseñado.

### Sí hacer mock de:

- **Llamadas de red**: APIs externas, bases de datos remotas.
- **Operaciones de filesystem costosas**: Lectura/escritura de
  archivos grandes.
- **Servicios de terceros**: Gateways de pago, servicios de email.
- **Tiempo y aleatoriedad**: `datetime.now()`, `uuid4()`, `random`.
- **Recursos con costo real**: APIs facturadas, SMS, etc.

La regla general es: mockea las fronteras del sistema (I/O, red,
tiempo), nunca la lógica interna.
