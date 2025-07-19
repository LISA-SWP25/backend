from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

# Enums
class OSType(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"

class BuildStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"

class UpdateStatus(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"

class DeploymentRequest(BaseModel):
    server_ip: str
    server_user: str
    server_password: str
    
# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., example="Junior Developer")
    description: str = Field(..., example="Entry-level software developer")
    category: str = Field(..., example="Development")

class RoleCreate(RoleBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Junior Developer",
                "description": "Entry-level software developer with 0-2 years experience",
                "category": "Development"
            }
        }
    )

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Senior Developer")
    description: Optional[str] = Field(None, example="Experienced software developer")
    category: Optional[str] = Field(None, example="Development")
    is_active: Optional[bool] = Field(None, example=True)

class RoleResponse(RoleBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
        
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

# Behavior Template schemas
class BehaviorTemplateBase(BaseModel):
    name: str = Field(..., example="Standard Developer Behavior")
    description: Optional[str] = Field(None, example="Standard behavior pattern for developers")
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
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Standard Developer Behavior",
                "description": "Standard behavior pattern for developers",
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
    )

class BehaviorTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Updated Developer Behavior")
    description: Optional[str] = Field(None, example="Updated behavior pattern")
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

    model_config = ConfigDict(from_attributes=True)

# Agent schemas 
class AgentConfig(BaseModel):
    name: str = Field(..., example="TestAgent01")
    role_id: int = Field(..., example=1, description="ID of the role for this agent")
    template_id: int = Field(..., example=1, description="ID of the behavior template")
    os_type: str = Field(..., example="linux")
    injection_target: Optional[str] = Field(None, example="dev-workstation-01")
    custom_config: Optional[Dict] = Field(default={}, example={
        "department": "Development",
        "location": "Headquarters",
        "custom_apps": ["IntelliJ IDEA"]
    })
    # Version info for agent updates
    version_info: Optional[Dict] = Field(default={}, example={
        "version_hash": "abc123def456",
        "build_version": "1.0.0",
        "last_updated": "2025-01-15T10:30:00Z"
    })
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "DevAgent01",
                "role_id": 1,
                "template_id": 1,
                "os_type": "linux",
                "injection_target": "dev-workstation-01",
                "custom_config": {
                    "department": "Development",
                    "location": "Headquarters"
                },
                "version_info": {
                    "version_hash": "abc123def456",
                    "build_version": "1.0.0"
                }
            }
        }
    )

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
    # Include version info and build time
    version_info: Optional[Dict] = None
    build_time: Optional[int] = None
    template_id: Optional[int] = None
    role_id: Optional[int] = None
    injection_target: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AgentHeartbeat(BaseModel):
    agent_id: str
    timestamp: datetime
    status: str
    current_activity: Optional[str] = None
    system_info: Dict


# Build schemas
class AgentBuildRequest(BaseModel):
    agent_id: str = Field(..., example="USR1234567")
    force_rebuild: bool = Field(default=False, example=False)
    compilation_options: Optional[Dict] = Field(default={}, example={
        "optimization": "release",
        "include_debug": False,
        "version_hash": "abc123def456"
    })

class AgentBuildResponse(BaseModel):
    id: int
    agent_id: int
    build_config: Dict
    build_status: str
    binary_path: Optional[str] = None
    binary_size: Optional[int] = None
    build_log: Optional[str] = None
    build_time: Optional[int] = None  # build time in seconds
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Agent Update Log schemas
class AgentUpdateLogBase(BaseModel):
    template_id: int = Field(..., example=1)
    user_id: str = Field(..., example="admin_user")
    old_version: Optional[str] = Field(None, example="1.0.0")
    new_version: str = Field(..., example="1.1.0")
    update_status: UpdateStatus = Field(..., example=UpdateStatus.STARTED)
    update_log: Optional[str] = Field(None, example="Starting update process...")

class AgentUpdateLogCreate(AgentUpdateLogBase):
    pass

class AgentUpdateLogResponse(AgentUpdateLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Build Statistics schema
class BuildStatistics(BaseModel):
    template_id: int
    template_name: Optional[str]
    role_name: Optional[str]
    total_builds: int
    successful_builds: int
    failed_builds: int
    latest_build_date: Optional[datetime]
    latest_version_hash: Optional[str]

# Running Agents schema
class RunningAgent(BaseModel):
    agent_id: str
    agent_name: str
    status: str
    last_seen: Optional[datetime]
    version_hash: Optional[str]
    user_id: Optional[str]

# Agent Build Info view schema
class AgentBuildInfo(BaseModel):
    agent_internal_id: int
    agent_id: str
    template_id: Optional[int]
    agent_name: str
    agent_status: str
    last_seen: Optional[datetime]
    last_activity: Optional[str]
    os_type: str
    config: Optional[Dict]
    version_info: Optional[Dict]
    template_name: Optional[str]
    template_description: Optional[str]
    role_name: Optional[str]
    role_category: Optional[str]
    build_id: Optional[int]
    build_status: Optional[str]
    binary_path: Optional[str]
    build_time: Optional[int]
    build_config: Optional[Dict]
    build_created_at: Optional[datetime]
    version_hash: Optional[str]

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

    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(
        json_schema_extra={
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
    )

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

    model_config = ConfigDict(from_attributes=True)

class ServerTemplate(BaseModel):
    id: int = None
    name: str = None
    description: Optional[str] = None
    ip: str = None
    login: str = None
    password: str = None
    os: str = None
