from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./certificates.db"
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # AWS S3 (Bucket para guardar PDFs de certificados)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_STORAGE_BUCKET_NAME: str = ""
    AWS_S3_REGION_NAME: str = "us-east-1"
    
    # Comunicación interna
    CATALOG_SERVICE_URL: str = "http://catalog-service:8000"

    class Config:
        env_file = ".env"

settings = Settings()
