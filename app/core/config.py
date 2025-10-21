from pydantic_settings import BaseSettings
from pydantic import computed_field
from pathlib import Path

class Settings(BaseSettings):
    SQLITE_FILENAME: str = 'database.db'
    SQLITE_PATH: Path = Path(__file__).resolve().parent.parent / "db"
    PROJECT_NAME: str = "Ndu's HNG Stage 1 API"

    @computed_field
    @property
    def SQLITE_DB_URL(self) -> str:
        return f"sqlite:///{self.SQLITE_PATH / self.SQLITE_FILENAME}"


settings = Settings()
print(settings.SQLITE_DB_URL)