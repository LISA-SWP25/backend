"""
LISA Backend Configuration Management
"""
from functools import lru_cache
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Settings
    api_title: str = "LISA - Living Infrastructure Simulator Agent"
    api_description: str = "Backend API for managing cyber range user simulation"
    api_version: str = "1.0.0"
    debug: bool = Field(False, env="DEBUG")
    
    # Database
    database_url: str = Field(
        "postgresql://lisa:pass@localhost:5432/lisa_dev",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(10, env="DB_POOL_SIZE")
    database_max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    
    # Redis (for caching and message queue)
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # SSH Configuration
    ssh_timeout: int = Field(30, env="SSH_TIMEOUT")
    ssh_key_path: str = Field("~/.ssh/lisa_rsa", env="SSH_KEY_PATH")
    ssh_default_user: str = Field("lisa", env="SSH_DEFAULT_USER")
    
    # Agent Configuration
    agent_check_interval: int = Field(60, env="AGENT_CHECK_INTERVAL")  # seconds
    agent_timeout: int = Field(300, env="AGENT_TIMEOUT")  # 5 minutes
    agent_max_retries: int = Field(3, env="AGENT_MAX_RETRIES")
    
    # CI/CD Settings
    cicd_workspace: str = Field("/tmp/lisa_builds", env="CICD_WORKSPACE")
    artifact_storage: str = Field("/var/lib/lisa/artifacts", env="ARTIFACT_STORAGE")
    
    # Security
    secret_key: str = Field("your-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:5173"],
        env="ALLOWED_ORIGINS"
    )
    
    # Monitoring
    monitoring_enabled: bool = Field(True, env="MONITORING_ENABLED")
    metrics_retention_days: int = Field(30, env="METRICS_RETENTION_DAYS")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Docker Registry (for agent distribution)
    docker_registry: str = Field("localhost:5000", env="DOCKER_REGISTRY")
    docker_namespace: str = Field("lisa", env="DOCKER_NAMESPACE")
    
    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('cicd_workspace', 'artifact_storage')
    def create_directories(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "WARNING"
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-in-production":
            raise ValueError("Secret key must be changed in production")
        return v


class TestingSettings(Settings):
    database_url: str = "postgresql://lisa:pass@localhost:5432/lisa_test"
    redis_url: str = "redis://localhost:6379/1"
    testing: bool = True


def get_settings_for_env(env: str = None) -> Settings:
    """Get settings based on environment"""
    env = env or os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
