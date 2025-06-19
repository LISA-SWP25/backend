# Agent CRUD + Config generation
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import uuid
import json
import tempfile
from datetime import datetime

from app.deps import get_db
from app.models.models import Role, BehaviorTemplate, Agent, AgentActivity
from app.schemas import AgentConfig, AgentResponse, AgentGenerateResponse

router = APIRouter()

@router.post("/agents/generate", response_model=AgentGenerateResponse)
def generate_agent_config(config: AgentConfig, db: Session = Depends(get_db)):
    """Generate agent configuration (my responsibility: config generation only)"""
    # Validate role and template
    role = db.query(Role).filter(Role.id == config.role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    template = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.id == config.template_id,
        BehaviorTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate OS compatibility
    if template.os_type != config.os_type:
        raise HTTPException(
            status_code=400,
            detail=f"Template OS ({template.os_type}) doesn't match requested OS ({config.os_type})"
        )
    
    # Generate unique agent ID
    agent_id = f"USR{str(uuid.uuid4().int)[:7]}"
    
    # Create agent record in database
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
    
    # Generate configuration for download (JSON format)
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
    """Download agent configuration file"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Build complete config
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
    
    if format.lower() == "yaml":
        import yaml
        content = yaml.dump(config, default_flow_style=False)
        filename = f"{agent_id}_config.yaml"
        media_type = "application/x-yaml"
    else:
        content = json.dumps(config, indent=2)
        filename = f"{agent_id}_config.json"
        media_type = "application/json"
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format.lower()}') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    return FileResponse(
        path=tmp_path,
        filename=filename,
        media_type=media_type,
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
    """Get list of agents with filtering (DB records only)"""
    query = db.query(Agent)
    
    if status:
        query = query.filter(Agent.status == status)
    if os_type:
        query = query.filter(Agent.os_type == os_type)
    if role_id:
        query = query.filter(Agent.role_id == role_id)
    
    agents = query.order_by(desc(Agent.created_at)).offset(skip).limit(limit).all()
    return agents

@router.post("/api/agents/generate-config")
def generate_agent_config(request: dict, db: Session = Depends(get_db)):
    """Generate config for unified_agent.py"""
    
    # Create agent record
    agent_id = f"USR{str(uuid.uuid4().int)[:7]}"
    
    # Generate config matching your unified_agent.py format
    config = {
        "user_id": agent_id,
        "username": request.get("username", "john_doe"),
        "full_name": request.get("full_name", "John Doe"),
        "role": request.get("role", "Junior Developer"),
        "work_schedule": {
            "start_time": "09:00",
            "end_time": "18:00",
            "breaks": [{"start": "13:00", "duration_minutes": 60}]
        },
        "operating_system": request.get("os", "Linux Ubuntu 22.04"),
        "applications_used": [
            "Visual Studio Code", "Google Chrome", "Slack", "Docker Desktop"
        ]
    }
    
    return {
        "success": True,
        "agent_id": agent_id,
        "config": config,
        "download_url": f"/api/agents/{agent_id}/download"
    }

@router.get("/api/agents/{agent_id}/download")
def download_config(agent_id: str):
    """Download agent config as JSON"""
    # Return FileResponse with the config

@router.get("/agents/{agent_id}/status")
def get_agent_status(agent_id: str, db: Session = Depends(get_db)):
    """Get agent status from database (not runtime status)"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get recent activities from database
    recent_activities = db.query(AgentActivity).filter(
        AgentActivity.agent_id == agent.id
    ).order_by(desc(AgentActivity.timestamp)).limit(10).all()
    
    return {
        "agent": {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": agent.status,  # DB status, not runtime
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

@router.post("/agents/generate-config")
def generate_agent_config(request: dict, db: Session = Depends(get_db)):
    agent_id = f"USR{str(uuid.uuid4().int)[:7]}"
    
    config = {
        "user_id": agent_id,
        "username": request.get("username", "john_doe"),
        "role": request.get("role", "Junior Developer"),
        "work_schedule": {
            "start_time": "09:00",
            "end_time": "18:00",
            "breaks": [{"start": "13:00", "duration_minutes": 60}]
        },
        "operating_system": "Linux Ubuntu 22.04",
        "applications_used": ["Visual Studio Code", "Google Chrome", "Slack", "Docker Desktop"]
    }
    
    return {
        "agent_id": agent_id,
        "config": config,
        "download_url": f"/api/agents/{agent_id}/config"
    }
