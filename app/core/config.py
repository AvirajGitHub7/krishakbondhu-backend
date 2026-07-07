"""
KrishakBondhu - Application Configuration
Loads environment variables using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "krishakbondhu"

    # JWT
    JWT_SECRET_KEY: str = "change-this-to-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # HuggingFace
    HF_MODEL_NAME: str = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    HF_TOKEN: str = ""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8081,https://krishakbondhu-admin.vercel.app"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
