from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DB_TYPE: str = "sqlite"

    # postgres (опционально)
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None

    SQLITE_PATH: str = "app.db"

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

        # default — sqlite
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"


settings = Settings()
DATABASE_URL = settings.get_db_url()