# Basic Pydantic models
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RoleCategory(str, Enum):
    DEVELOPER = "developer"
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"
    SECURITY = "security"

class OSType(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"

class StealthLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Role schemas
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: RoleCategory

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RoleCategory] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Template schemas
class TemplateDataSchema(BaseModel):
    activities: List[Dict[str, Any]]
    schedule: Dict[str, Any]
    stealth_config: Optional[Dict[str, Any]] = None

class BehaviorTemplateCreate(BaseModel):
    name: str
    role_id: int
    os_type: OSType
    template_data: TemplateDataSchema
    version: str = "1.0"

class BehaviorTemplateResponse(BaseModel):
    id: int
    name: str
    role_id: int
    os_type: str
    template_data: Dict[str, Any]
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Agent schemas
class AgentConfig(BaseModel):
    name: str
    role_id: int
    template_id: int
    os_type: OSType
    injection_target: Optional[str] = "explorer.exe"
    stealth_level: StealthLevel = StealthLevel.MEDIUM
    custom_config: Dict[str, Any] = {}

class AgentResponse(BaseModel):
    id: int
    agent_id: str
    name: str
    role_id: int
    template_id: int
    status: str
    os_type: str
    injection_target: Optional[str]
    stealth_level: str
    last_seen: Optional[datetime]
    last_activity: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AgentGenerateResponse(BaseModel):
    success: bool = True
    agent_id: str
    message: str
    config: Dict[str, Any]
    download_url: str
    status_url: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Build schemas
class AgentBuildRequest(BaseModel):
    agent_id: str
    force_rebuild: bool = False
    compilation_options: Dict[str, Any] = {}

class AgentBuildResponse(BaseModel):
    id: int
    agent_id: int
    build_status: str
    binary_path: Optional[str]
    binary_size: Optional[int]
    build_time: Optional[int]
    build_log: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
