from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

# Enums
class OSType(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    
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
        
# HEARTBEAT SCHEMAS
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

# Behavior Template schemas - UPDATED
class BehaviorTemplateBase(BaseModel):
    name: str
    role_id: int
    template_data: Dict
    os_type: str
    version: str = "1.0"

class BehaviorTemplateCreate(BehaviorTemplateBase):
    pass

class BehaviorTemplateUpdate(BaseModel):
    name: Optional[str] = None
    role_id: Optional[int] = None
    template_data: Optional[Dict] = None
    os_type: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None

class BehaviorTemplateResponse(BehaviorTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Agent schemas - UPDATED
class AgentConfig(BaseModel):
    name: str
    role_id: int
    template_id: int
    os_type: str
    injection_target: Optional[str] = None
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
    stealth_level: str
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

# Build schemas - UPDATED
class AgentBuildRequest(BaseModel):
    agent_id: str
    force_rebuild: bool = False
    compilation_options: Optional[Dict] = {}

class AgentBuildResponse(BaseModel):
    id: int
    agent_id: int
    build_config: Dict
    build_status: str
    binary_path: Optional[str] = None
    binary_size: Optional[int] = None
    build_log: Optional[str] = None
    build_time: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

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

# ApplicationTemplate schemas
class ApplicationTemplateBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0"
    author: Optional[str] = None
    template_config: Dict
    os_type: str = "linux"

class ApplicationTemplateCreate(ApplicationTemplateBase):
    pass

class ApplicationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    template_config: Optional[Dict] = None
    os_type: Optional[str] = None
    is_active: Optional[bool] = None

class ApplicationTemplateResponse(ApplicationTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
