from sqlmodel import create_engine, Session
from app.core.config import settings

# En producción, usa echo=False
engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
