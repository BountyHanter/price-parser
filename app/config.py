from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE = BASE_DIR / "storage" / "app.db"


class Settings(BaseSettings):
    DB_TYPE: str = "sqlite"

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None

    SQLITE_PATH: Path = DEFAULT_SQLITE   # <-- ВАЖНО: Path

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_db_url(self) -> str:
        if self.DB_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        path = self.SQLITE_PATH

        # если вдруг из .env придёт относительный путь
        if not path.is_absolute():
            path = (BASE_DIR / path).resolve()

        return f"sqlite+aiosqlite:///{path.as_posix()}"


settings = Settings()
DATABASE_URL = settings.get_db_url()