from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
import uuid
import json
import tempfile
import subprocess
from datetime import datetime

from app.deps import get_db
from app.models.models import Role, BehaviorTemplate, Agent, AgentActivity
from app.schemas import AgentConfig, AgentResponse, AgentGenerateResponse

router = APIRouter()

class ConfigRequest(BaseModel):
    username: str = "john_doe"
    role: str = "Junior Developer"
    full_name: str = "John Doe"

# Simplified config generation for unified_agent.py
@router.post("/agents/generate-config")
def generate_agent_config(request: ConfigRequest, db: Session = Depends(get_db)):
    """Generate config for unified_agent.py"""
    agent_id = f"USR{str(uuid.uuid4().int)[:7]}"
    
    config = {
        "user_id": agent_id,
        "username": request.username,
        "full_name": request.full_name,
        "role": request.role,
        "work_schedule": {
            "start_time": "09:00",
            "end_time": "18:00",
            "breaks": [{"start": "13:00", "duration_minutes": 60}]
        },
        "operating_system": "Linux Ubuntu 22.04",
        "applications_used": [
            "Visual Studio Code", "Google Chrome", "Slack", "Docker Desktop"
        ],
        "activity_pattern": "Regular office hours with lunch break",
        "department": "Development",
        "location": "Headquarters"
    }
    
    return {
        "agent_id": agent_id,
        "config": config,
        "download_url": f"/api/agents/{agent_id}/config"
    }

@router.get("/agents/{agent_id}/config")
def download_config(agent_id: str):
    """Download agent config as JSON"""
    config = {
        "user_id": agent_id,
        "username": "john_doe",
        "full_name": "John Doe",
        "role": "Junior Developer",
        "work_schedule": {
            "start_time": "09:00",
            "end_time": "18:00",
            "breaks": [{"start": "13:00", "duration_minutes": 60}]
        },
        "operating_system": "Linux Ubuntu 22.04",
        "applications_used": [
            "Visual Studio Code", "Google Chrome", "Slack", "Docker Desktop"
        ],
        "activity_pattern": "Regular office hours with lunch break",
        "department": "Development",
        "location": "Headquarters"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        temp_path = f.name
    
    return FileResponse(
        temp_path,
        filename=f"{agent_id}_config.json",
        media_type="application/json"
    )

@router.post("/agents/{agent_id}/deploy")
def deploy_agent(agent_id: str, target_host: str = "localhost"):
    """Deploy agent via dropper"""
    dropper_cmd = f"python3 dropper.py --config {agent_id}_config.json --target {target_host}"
    result = subprocess.run(dropper_cmd, shell=True, capture_output=True)
    return {"status": "deployed" if result.returncode == 0 else "failed"}

# Database-based config generation (original complex version)
@router.post("/agents/generate", response_model=AgentGenerateResponse)
def generate_agent_db_config(config: AgentConfig, db: Session = Depends(get_db)):
    """Generate agent configuration using database models"""
    role = db.query(Role).filter(Role.id == config.role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    template = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.id == config.template_id,
        BehaviorTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.os_type != config.os_type:
        raise HTTPException(
            status_code=400,
            detail=f"Template OS ({template.os_type}) doesn't match requested OS ({config.os_type})"
        )
    
    agent_id = f"USR{str(uuid.uuid4().int)[:7]}"
    
    db_agent = Agent(
        agent_id=agent_id,
        name=config.name,
        role_id=config.role_id,
        template_id=config.template_id,
        os_type=config.os_type,
        injection_target=config.injection_target,
        stealth_level=config.stealth_level,
        config=config.custom_config,
        status="configured"
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    agent_config = {
        "agent_id": agent_id,
        "name": config.name,
        "target_os": config.os_type,
        "role": {
            "name": role.name,
            "description": role.description,
            "category": role.category
        },
        "behavior_template": template.template_data,
        "injection_target": config.injection_target,
        "stealth_level": config.stealth_level,
        "custom_config": config.custom_config,
        "generated_at": datetime.utcnow().isoformat(),
        "version": "1.0"
    }
    
    return AgentGenerateResponse(
        agent_id=agent_id,
        message=f"Agent '{config.name}' configured successfully",
        config=agent_config,
        download_url=f"/api/agents/{agent_id}/config/download",
        status_url=f"/api/agents/{agent_id}/status"
    )

@router.get("/agents/{agent_id}/config/download")
def download_agent_config(agent_id: str, format: str = "json", db: Session = Depends(get_db)):
    """Download agent configuration file from database"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    config = {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "target_os": agent.os_type,
        "role": {
            "name": agent.role.name,
            "description": agent.role.description,
            "category": agent.role.category
        },
        "behavior_template": agent.template.template_data,
        "injection_target": agent.injection_target,
        "stealth_level": agent.stealth_level,
        "custom_config": agent.config or {},
        "created_at": agent.created_at.isoformat(),
        "version": "1.0"
    }
    
    content = json.dumps(config, indent=2)
    filename = f"{agent_id}_config.json"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    return FileResponse(
        path=tmp_path,
        filename=filename,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/agents", response_model=List[AgentResponse])
def list_agents(
    status: Optional[str] = None,
    os_type: Optional[str] = None,
    role_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of agents with filtering"""
    query = db.query(Agent)
    
    if status:
        query = query.filter(Agent.status == status)
    if os_type:
        query = query.filter(Agent.os_type == os_type)
    if role_id:
        query = query.filter(Agent.role_id == role_id)
    
    agents = query.order_by(desc(Agent.created_at)).offset(skip).limit(limit).all()
    return agents

@router.post("/agents/{agent_id}/deploy")
def deploy_agent_to_target(agent_id: str, target_config: dict, db: Session = Depends(get_db)):
    """Deploy enhanced agent to target machine"""
    
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Create enhanced config for the agent
    enhanced_config = {
        "user_id": agent.agent_id,
        "username": target_config.get("username", "user"),
        "full_name": target_config.get("full_name", "Generic User"),
        "role": agent.role.name,
        "work_schedule": {
            "start_time": "09:00",
            "end_time": "18:00",
            "breaks": [{"start": "13:00", "duration_minutes": 60}]
        },
        "applications_used": ["Visual Studio Code", "Google Chrome", "Slack"],
        "plugin_support": {
            "enabled": True,
            "plugins_directory": "/opt/linux_agent/plugins",
            "auto_load": True,
            "fallback_to_builtin": True
        }
    }
    
    # Call dropper service to deploy
    dropper_payload = {
        "agent_id": agent_id,
        "target_host": target_config["target_host"],
        "credentials": target_config["credentials"],
        "agent_config": enhanced_config,
        "injection_method": target_config.get("injection_method", "dropper")
    }
    
    # This would call the dropper service
    return {"status": "deployment_initiated", "config": enhanced_config}

@router.get("/agents/{agent_id}/activities")
def get_agent_activities(agent_id: str, db: Session = Depends(get_db)):
    """Get real-time activities from deployed agent"""
    
    # This would read from agent logs or status
    return {
        "agent_id": agent_id,
        "current_status": "active",
        "current_application": "Visual Studio Code",
        "last_activity": "Editing main.py",
        "work_session_time": "2h 15m",
        "activities_today": 47
    }

@router.get("/agents/{agent_id}/status")
def get_agent_status(agent_id: str, db: Session = Depends(get_db)):
    """Get agent status from database"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    recent_activities = db.query(AgentActivity).filter(
        AgentActivity.agent_id == agent.id
    ).order_by(desc(AgentActivity.timestamp)).limit(10).all()
    
    return {
        "agent": {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": agent.status,
            "os_type": agent.os_type,
            "role": agent.role.name,
            "template": agent.template.name,
            "last_seen": agent.last_seen,
            "created_at": agent.created_at
        },
        "recent_activities": [
            {
                "id": activity.id,
                "type": activity.activity_type,
                "data": activity.activity_data,
                "timestamp": activity.timestamp
            } for activity in recent_activities
        ]
    }
