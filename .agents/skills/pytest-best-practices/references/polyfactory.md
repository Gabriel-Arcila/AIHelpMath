# Polyfactory: Generación de Datos de Prueba

Polyfactory genera automáticamente instancias válidas de modelos
Pydantic y SQLModel a partir de sus definiciones de tipo. Reemplaza
la construcción manual de datos con literales hardcodeados.

---

## 1. Instalación

Polyfactory se agrega como dependencia de desarrollo:

```toml
[dependency-groups]
dev = [
    "polyfactory>=2.0.0",
]
```

---

## 2. Definición de Factories

Las factories se centralizan en `tests/factories.py` para que
todos los archivos de test las importen desde un único lugar.

```python
from polyfactory.factories.pydantic_factory import ModelFactory

from src.users.schemas import UserCreate, UserUpdate
from src.users.models import User, UserRole


class UserCreateFactory(ModelFactory):
    """Factory para generar instancias válidas de UserCreate."""

    __model__ = UserCreate


class UserUpdateFactory(ModelFactory):
    """Factory para generar instancias válidas de UserUpdate."""

    __model__ = UserUpdate


class UserModelFactory(ModelFactory):
    """Factory para generar instancias de User (tests con mocks)."""

    __model__ = User
    __set_relationships__ = False


class UserRoleModelFactory(ModelFactory):
    """Factory para generar instancias de UserRole."""

    __model__ = UserRole
    __set_relationships__ = False
```

### Atributo `__model__`

Define el modelo Pydantic o SQLModel que la factory genera.
Polyfactory inspecciona los campos del modelo, sus tipos y
restricciones para generar valores válidos automáticamente.

### Atributo `__set_relationships__`

En modelos SQLModel con `table=True`, las relaciones declaradas
con `Relationship()` (ej. `user_role`, `user_ai_profiles`) no se
pueden generar automáticamente porque dependen de registros
existentes en la base de datos. Establecer
`__set_relationships__ = False` indica a Polyfactory que ignore
estos campos.

---

## 3. Métodos de generación

### `.build()` — Instancia sin persistencia

Genera una instancia del modelo sin guardarla en base de datos.
Es el método más usado en tests.

```python
# Valores completamente aleatorios (pero válidos)
user_data = UserCreateFactory.build()

# Con overrides para campos específicos del test
user_data = UserCreateFactory.build(id_role=1)

# Múltiples instancias
users = UserCreateFactory.batch(size=5, id_role=1)
```

### `.build()` con overrides

Los overrides permiten fijar valores específicos que son relevantes
para la aserción del test, dejando que Polyfactory genere el resto.

```python
# Solo fijamos el email porque el test valida duplicados
user_data = UserCreateFactory.build(
    email="duplicate@example.com",
    id_role=seed_role.id,
)
```

La regla es: **override solo lo que el test necesita verificar**.
Los demás campos se generan automáticamente para reducir
acoplamiento con la implementación.

---

## 4. Patrones de uso por capa

### Tests de Repository (DB real)

Los tests de repository usan la base de datos real. Generan datos
con factories de schemas (no de modelos) y los pasan al repository.

```python
from tests.factories import UserCreateFactory

class TestUserRepositoryInsert:
    async def test_add_persists_and_returns_user(
        self,
        db_session,
        seed_user_role,
    ) -> None:
        # Arrange
        repo = UserRepository(db_session)
        user_data = UserCreateFactory.build(
            id_role=seed_user_role.id,
        )

        # Act
        user = await repo.add(user_data)

        # Assert
        assert user.email == user_data.email
```

### Tests de Service (mocks)

Los tests de service usan mocks. Generan instancias de modelos
completos con factories de modelos.

```python
from tests.factories import UserModelFactory, UserCreateFactory

class TestUserServiceInsert:
    async def test_create_returns_user(
        self,
        user_service,
        mock_repository,
    ) -> None:
        # Arrange
        user_data = UserCreateFactory.build(id_role=1)
        expected_user = UserModelFactory.build(
            email=user_data.email,
            id_role=user_data.id_role,
        )
        mock_repository.get_by_email.return_value = None
        mock_repository.add.return_value = expected_user

        # Act
        result = await user_service.create(user_data)

        # Assert
        assert result.email == expected_user.email
```

### Tests de Router (HTTP)

Los tests de router envían JSON via `AsyncClient`. Usan
`.model_dump(mode="json")` para convertir la instancia a dict
serializable.

```python
from tests.factories import UserCreateFactory

class TestUserRouterInsert:
    async def test_create_user_returns_201(
        self,
        async_client,
        seed_user_role,
    ) -> None:
        # Arrange
        payload = UserCreateFactory.build(
            id_role=seed_user_role.id,
        ).model_dump(mode="json")

        # Act
        response = await async_client.post(
            "/v1/users/",
            json=payload,
        )

        # Assert
        assert response.status_code == 201
```

---

## 5. Manejo de tipos especiales

### EmailStr

Polyfactory genera emails válidos automáticamente para campos
tipados como `EmailStr`. No requiere configuración adicional.

### UUID

Para campos `str` que representan UUIDs (como `User.id`),
Polyfactory genera strings aleatorios. Si necesitas un UUID
válido, usa un override:

```python
import uuid

user = UserModelFactory.build(id=str(uuid.uuid4()))
```

### Campos opcionales

Polyfactory respeta `Optional[T]` y puede generar `None` o un
valor válido. Si tu test necesita un valor concreto, usa override.

---

## 6. Reglas

1. **Un `tests/factories.py` centralizado**: Todas las factories
   en un solo archivo, importables desde cualquier test.
2. **Un factory por modelo/schema**: `UserCreate` → `UserCreateFactory`,
   `User` → `UserModelFactory`.
3. **`.build()` por defecto**: No usar `.create()` ni persistencia
   automática. La persistencia la manejan las fixtures o el
   repository directamente.
4. **Override mínimo**: Solo fijar los campos que el test necesita
   verificar. El resto lo genera Polyfactory.
5. **`__set_relationships__ = False`**: Obligatorio en modelos
   SQLModel con `table=True` que tengan `Relationship()`.
6. **No hardcodear datos**: Si un test construye un modelo
   manualmente con literales, reemplázalo por una factory call.
