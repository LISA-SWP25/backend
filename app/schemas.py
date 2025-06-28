from app.api.endpoints import heartbeat
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

# Enums
class OSType(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"

class StealthLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Role schemas
class RoleBase(BaseModel):
    name: str
    description: str
    category: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class RoleResponse(RoleBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AgentHeartbeatRequest(BaseModel):
    timestamp: datetime
    agent_id: str
    username: str
    role: str
    department: Optional[str] = None
    location: Optional[str] = None
    system_info: Dict
    statistics: Optional[Dict] = None
    current_activity: Optional[Dict] = None
    status: str = "active"

class AgentHeartbeatResponse(BaseModel):
    status: str
    agent_id: str
    timestamp: datetime
    message: str
    next_heartbeat_in: int
    commands: Optional[List[Dict]] = []

# Behavior Template schemas
class BehaviorTemplateBase(BaseModel):
    name: str
    description: str
    os_type: str
    template_data: Dict

class BehaviorTemplateCreate(BehaviorTemplateBase):
    pass

class BehaviorTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    os_type: Optional[str] = None
    template_data: Optional[Dict] = None
    is_active: Optional[bool] = None

class BehaviorTemplateResponse(BehaviorTemplateBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Agent schemas
class AgentConfig(BaseModel):
    name: str
    role_id: int
    template_id: int
    os_type: str
    injection_target: str
    stealth_level: str = "medium"
    custom_config: Optional[Dict] = {}

class AgentGenerateResponse(BaseModel):
    agent_id: str
    message: str
    config: Dict
    download_url: str
    status_url: str

class AgentResponse(BaseModel):
    id: int
    agent_id: str
    name: str
    status: str
    os_type: str
    last_seen: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class AgentHeartbeat(BaseModel):
    agent_id: str
    timestamp: datetime
    status: str
    current_activity: Optional[str] = None
    system_info: Dict

# Deployment schemas
class DeploymentRequest(BaseModel):
    host: str
    username: str
    password: Optional[str] = None
    ssh_key_path: Optional[str] = None
    port: int = 22

class DeploymentResponse(BaseModel):
    agent_id: str
    status: str
    message: str
    deployment_id: str

# Build schemas
class BuildConfig(BaseModel):
    agent_id: str
    target_os: str
    architecture: str = "x64"
    build_options: Optional[Dict] = {}

class BuildResponse(BaseModel):
    build_id: str
    status: str
    message: str
    download_url: Optional[str] = None
    logs_url: str

class BuildStatusResponse(BaseModel):
    build_id: str
    status: str
    progress: int
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None

# System schemas
class SystemInfoResponse(BaseModel):
    version: str
    status: str
    uptime: float
    database_status: str
    total_agents: int
    active_agents: int

class SystemConfigUpdate(BaseModel):
    log_level: Optional[str] = None
    agent_timeout_minutes: Optional[int] = None
    max_concurrent_builds: Optional[int] = None

# Activity schemas
class ActivityLog(BaseModel):
    id: int
    agent_id: str
    activity_type: str
    activity_data: Dict
    timestamp: datetime

    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_agents: int
    online_agents: int
    offline_agents: int
    total_activities: int
    avg_activities_per_agent: float
    system_status: str

# WebSocket schemas
class WSMessage(BaseModel):
    type: str
    data: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Agent Build schemas
class AgentBuildRequest(BaseModel):
    agent_id: str
    target_os: str
    architecture: str = "x64"
    build_type: str = "release"
    include_plugins: bool = True
    stealth_features: Optional[Dict] = {}

class AgentBuildResponse(BaseModel):
    build_id: str
    agent_id: str
    status: str
    message: str
    download_url: Optional[str] = None
    logs_url: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None

# Build Status schemas
class BuildStatusResponse(BaseModel):
    build_id: str
    status: str
    progress: int
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    error: Optional[str] = None

# Build Log schemas  
class BuildLogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str

class BuildLogsResponse(BaseModel):
    build_id: str
    logs: List[BuildLogEntry]
    total_lines: int
