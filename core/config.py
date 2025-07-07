from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://lisa:pass@localhost:5432/lisa_dev"
    LISA_SERVER_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "your-secret-key-here"
    SSH_KEY_PATH: Optional[str] = None
    
    # Redis settings for caching
    REDIS_URL: str = "redis://localhost:6379"
    
    # Agent settings
    AGENT_HEARTBEAT_INTERVAL: int = 60
    AGENT_TIMEOUT_MINUTES: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
