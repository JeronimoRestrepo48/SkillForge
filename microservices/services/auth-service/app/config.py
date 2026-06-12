from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./auth.db"
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_MINUTES: int = 60
    JWT_REFRESH_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()
