from sqlmodel import create_engine
from .config import settings


engine = create_engine(settings.SQLITE_DB_URL, echo=True)

