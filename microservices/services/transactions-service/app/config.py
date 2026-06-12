from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./transactions.db"
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Wompi Sandbox Configuration
    WOMPI_PUBLIC_KEY: str = "pub_stagtest_g2gOf6oEGop4jiaV3aJ4AYAQ"
    WOMPI_PRIVATE_KEY: str = "prv_stagtest_5i0ZGIofS6rp7LsRgj6tBaHiCmH"
    WOMPI_INTEGRITY_SECRET: str = "stagtest_integrity_nAIBuqayW70XpUqJS4qf4STYiISd89Fp"
    WOMPI_EVENTS_SECRET: str = "stagtest_events_pBIyEKocLioLiogS3QaI5WCLiqYBsWKH"
    
    # Redis for Celery Tasks dispatcher
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
