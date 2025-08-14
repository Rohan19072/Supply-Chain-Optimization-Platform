import os
from pathlib import Path
from typing import Optional

class Config:
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    MODELS_DIR = PROJECT_ROOT / "models"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///supply_chain.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    # API Keys
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # Model Parameters
    DEMAND_FORECAST_HORIZON = 90  # days
    INVENTORY_REVIEW_PERIOD = 7   # days
    ROUTE_OPTIMIZATION_FREQUENCY = 1  # hours

    # Business Parameters
    HOLDING_COST_RATE = 0.25  # 25% annual holding cost
    STOCKOUT_COST_MULTIPLIER = 3.0
    SERVICE_LEVEL_TARGET = 0.95

    # System Parameters
    MAX_WORKERS = 8
    CACHE_TTL = 3600  # 1 hour
    API_RATE_LIMIT = 1000  # requests per hour

    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        for dir_path in [cls.DATA_DIR, cls.RAW_DATA_DIR, 
                        cls.PROCESSED_DATA_DIR, cls.MODELS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
