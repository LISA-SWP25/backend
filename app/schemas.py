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
    name: str = Field(..., example="Junior Developer")
    description: str = Field(..., example="Entry-level software developer")
    category: str = Field(..., example="Development")

class RoleCreate(RoleBase):
    class Config:
        schema_extra = {
            "example": {
                "name": "Junior Developer",
                "description": "Entry-level software developer with 0-2 years experience",
                "category": "Development"
            }
        }

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Senior Developer")
    description: Optional[str] = Field(None, example="Experienced software developer")
    category: Optional[str] = Field(None, example="Development")
    is_active: Optional[bool] = Field(None, example=True)

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

# Behavior Template schemas - UPDATED WITH EXAMPLES
class BehaviorTemplateBase(BaseModel):
    name: str = Field(..., example="Standard Developer Behavior")
    role_id: int = Field(..., example=1, description="ID of the role this template belongs to")
    template_data: Dict = Field(..., example={
        "work_schedule": {
            "start_time": "09:00",
            "end_time": "18:00",
            "breaks": [{"start": "13:00", "duration_minutes": 60}]
        },
        "applications_used": [
            "Visual Studio Code",
            "Google Chrome", 
            "Slack",
            "Docker Desktop"
        ],
        "activity_pattern": "Regular office hours with lunch break",
        "productivity_metrics": {
            "code_sessions_per_day": "4-6",
            "average_session_length": "45-90 minutes",
            "break_frequency": "every 2 hours"
        }
    })
    os_type: str = Field(..., example="linux")
    version: str = Field(default="1.0", example="1.0")

class BehaviorTemplateCreate(BehaviorTemplateBase):
    class Config:
        schema_extra = {
            "example": {
                "name": "Standard Developer Behavior",
                "role_id": 1,
                "template_data": {
                    "work_schedule": {
                        "start_time": "09:00",
                        "end_time": "18:00",
                        "breaks": [{"start": "13:00", "duration_minutes": 60}]
                    },
                    "applications_used": [
                        "Visual Studio Code",
                        "Google Chrome",
                        "Slack",
                        "Terminal"
                    ],
                    "activity_pattern": "Regular office hours with lunch break",
                    "behavior_traits": {
                        "typing_speed": "medium",
                        "multitasking": True,
                        "break_habits": "regular"
                    }
                },
                "os_type": "linux",
                "version": "1.0"
            }
        }

class BehaviorTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Updated Developer Behavior")
    role_id: Optional[int] = Field(None, example=1)
    template_data: Optional[Dict] = None
    os_type: Optional[str] = Field(None, example="linux")
    version: Optional[str] = Field(None, example="1.1")
    is_active: Optional[bool] = Field(None, example=True)

class BehaviorTemplateResponse(BehaviorTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Agent schemas - UPDATED WITH EXAMPLES
class AgentConfig(BaseModel):
    name: str = Field(..., example="TestAgent01")
    role_id: int = Field(..., example=1, description="ID of the role for this agent")
    template_id: int = Field(..., example=1, description="ID of the behavior template")
    os_type: str = Field(..., example="linux")
    injection_target: Optional[str] = Field(None, example="dev-workstation-01")
    stealth_level: str = Field(default="medium", example="medium")
    custom_config: Optional[Dict] = Field(default={}, example={
        "department": "Development",
        "location": "Headquarters",
        "custom_apps": ["IntelliJ IDEA"]
    })

    class Config:
        schema_extra = {
            "example": {
                "name": "DevAgent01",
                "role_id": 1,
                "template_id": 1,
                "os_type": "linux",
                "injection_target": "dev-workstation-01",
                "stealth_level": "medium",
                "custom_config": {
                    "department": "Development",
                    "location": "Headquarters"
                }
            }
        }

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
    host: str = Field(..., example="192.168.1.100")
    username: str = Field(..., example="admin")
    password: Optional[str] = Field(None, example="secure_password")
    ssh_key_path: Optional[str] = Field(None, example="/home/user/.ssh/id_rsa")
    port: int = Field(default=22, example=22)

class DeploymentResponse(BaseModel):
    agent_id: str
    status: str
    message: str
    deployment_id: str

# Build schemas - UPDATED
class AgentBuildRequest(BaseModel):
    agent_id: str = Field(..., example="USR1234567")
    force_rebuild: bool = Field(default=False, example=False)
    compilation_options: Optional[Dict] = Field(default={}, example={
        "optimization": "release",
        "include_debug": False
    })

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
    name: str = Field(..., example="Visual Studio Code")
    display_name: Optional[str] = Field(None, example="VS Code")
    category: Optional[str] = Field(None, example="Development Tools")
    description: Optional[str] = Field(None, example="Code editor for development")
    version: str = Field(default="1.0", example="1.0")
    author: Optional[str] = Field(None, example="Microsoft")
    template_config: Dict = Field(..., example={
        "executable_path": "/usr/bin/code",
        "startup_args": ["--disable-extensions"],
        "window_behavior": {
            "minimize_probability": 0.1,
            "focus_duration_minutes": "15-45"
        }
    })
    os_type: str = Field(default="linux", example="linux")

class ApplicationTemplateCreate(ApplicationTemplateBase):
    class Config:
        schema_extra = {
            "example": {
                "name": "Visual Studio Code",
                "display_name": "VS Code",
                "category": "Development Tools",
                "description": "Lightweight but powerful source code editor",
                "version": "1.0",
                "author": "Microsoft",
                "template_config": {
                    "executable_path": "/usr/bin/code",
                    "startup_args": ["--disable-extensions"],
                    "window_behavior": {
                        "minimize_probability": 0.1,
                        "focus_duration_minutes": "15-45"
                    }
                },
                "os_type": "linux"
            }
        }

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
