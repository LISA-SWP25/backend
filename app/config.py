import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://lisa:pass@localhost:5432/lisa_dev"
    database_url_test: Optional[str] = None
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Agent Configuration
    agent_heartbeat_timeout: int = 300  # 5 min
    max_agents_per_role: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/lisa.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
