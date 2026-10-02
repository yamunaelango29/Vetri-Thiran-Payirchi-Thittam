from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    app_name: str = Field(default="FitBuddy – AI Fitness Plan Generator")
    debug: bool = True
    database_url: str = "sqlite:///./data/fitbuddy.db"
    gemini_api_key: str = ""
    gemini_pro_model: str = "gemini-2.5-pro"
    gemini_flash_model: str = "gemini-2.5-flash"
    demo_mode: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "FitBuddy – AI Fitness Plan Generator"),
        debug=os.getenv("DEBUG", "true").lower() == "true",
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/fitbuddy.db"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_pro_model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
        gemini_flash_model=os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash"),
        demo_mode=os.getenv("DEMO_MODE", "true").lower() == "true",
    )
