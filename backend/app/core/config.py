from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/secondhand_device"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE: int = 3600
    REFRESH_TOKEN_EXPIRE: int = 604800
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()