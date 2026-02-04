# AGENTS.md

Estas son las intrucciones para el agente de IA.

## Intruccion de comportamiento

- Habla siempre en español.
- Utiliza PEP 8 como guia estricta para codificar. 

## Contexto

<!-- ├── app/
│   ├── __init__.py
│   ├── main.py              # 🚀 El punto de entrada (Lanza la app)
│   ├── api/                 # 🌐 Capa de Interface (Rutas/Endpoints)
│   │   ├── __init__.py
│   │   └── v1/              # Versionado de API (Vital para no romper clientes futuros)
│   │       ├── __init__.py
│   │       └── endpoints/   # Aquí viven tus rutas (ej: explicacion.py)
│   ├── core/                # ⚙️ Configuración Global
│   │   ├── config.py        # Variables de entorno (Secrets)
│   │   └── security.py      # Autenticación (si la hubiera)
│   ├── db/                  # 💾 Capa de Datos (Infraestructura)
│   │   ├── session.py       # Conexión a Postgres
│   │   └── base.py          # Importador de modelos para migraciones
│   ├── models/              # 🗄️ Modelos de Base de Datos (SQLModel - Tablas)
│   │   └── user.py
│   ├── schemas/             # 📜 Contratos Pydantic (Request/Response)
│   │   └── explanation.py   # Lo que el Frontend envía y recibe
│   └── services/            # 🧠 Lógica de Negocio (Aquí vive la IA/LangChain)
│       └── ai_tutor.py      # El cerebro que no sabe nada de HTTP ni de DB
├── tests/                   # 🧪 TDD (Aquí pasaremos mucho tiempo)
│   ├── __init__.py
│   ├── conftest.py          # Configuración de los tests
│   └── api/                 # Tests de integración
├── .gitignore               # Higiene Git
├── docker-compose.yml       # 🐳 Infraestructura Efímera (DB local)
├── Dockerfile               # Para despliegue
├── pyproject.toml           # 📦 Dependencias (Moderno: reemplaza requirements.txt)
└── README.md                # Documentación para otros devs -->