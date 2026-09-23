from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal
import os


class Settings(BaseSettings):
    # Database
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "drusti"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""

    # Application
    DRUSTI_MODE: Literal["demo", "live"] = "demo"
    SECRET_KEY: str = "dev-secret-key-replace-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Model paths
    MODEL_CLASSIFIER_PATH: str = "models/classifier/resnet50_dr.pt"
    MODEL_SEGMENTATION_PATH: str = "models/segmentation/unet_lesions.pt"
    CALIBRATION_PATH: str = "models/calibration/temperature.json"

    # Storage
    UPLOAD_DIR: str = "data/uploads"
    DEMO_DIR: str = "data/demo"
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
