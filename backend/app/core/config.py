"""
Core Configuration — ATC System
All settings loaded from environment / .env file
"""

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os

# 🔥 Get project root (ATC Project/)
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ATC System"
    DEBUG: bool = False
    SECRET_KEY: str = "atc-secret-key-change-in-prod-2024"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "atc_user"
    DB_PASSWORD: str = "atc_password"
    DB_NAME: str = "atc_db"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:3000"
    ]

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]

    # 🔥 ML Models (FIXED PATHS)
    MODEL_DIR: str = str(BASE_DIR / "core_ml" / "models")
    CLASSIFIER_MODEL_PATH: str = str(BASE_DIR / "core_ml" / "models" / "model.pth")
    YOLO_MODEL_PATH: str = str(BASE_DIR / "core_ml" / "models" / "yolov8n.pt")

    # Training
    TRAIN_EPOCHS: int = 30
    TRAIN_BATCH_SIZE: int = 16
    TRAIN_LR: float = 1e-4
    IMAGE_SIZE: int = 224
    NUM_CLASSES: int = 2

    # Scoring weights (ATC formula)
    SCORE_WEIGHT_BODY_LENGTH: float = 0.15
    SCORE_WEIGHT_HEIGHT: float = 0.15
    SCORE_WEIGHT_CHEST_GIRTH: float = 0.15
    SCORE_WEIGHT_RUMP_ANGLE: float = 0.10
    SCORE_WEIGHT_RUMP_WIDTH: float = 0.10
    SCORE_WEIGHT_BODY_DEPTH: float = 0.10
    SCORE_WEIGHT_DAIRY_CHARACTER: float = 0.10
    SCORE_WEIGHT_FEET_LEGS: float = 0.075
    SCORE_WEIGHT_UDDER: float = 0.075

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()