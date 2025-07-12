from fastapi import APIRouter, Depends, HTTPException
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
def generate_agent(config: AgentConfig, db: Session = Depends(get_db)):
    """Generate agent configuration using database models"""
    # Validate role exists
    role = db.query(Role).filter(Role.id == config.role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Validate template exists
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
    
    # Create agent in database
    db_agent = Agent(
        agent_id=agent_id,
        name=config.name,
        role_id=config.role_id,
        template_id=config.template_id,
        os_type=config.os_type,
        injection_target=config.injection_target,
        config=config.custom_config,
        status="configured"
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    # Generate agent configuration
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
        "custom_config": config.custom_config or {},
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
def download_agent_config(agent_id: str, db: Session = Depends(get_db)):
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
            "name": agent.role.name if agent.role else "Unknown",
            "description": agent.role.description if agent.role else "",
            "category": agent.role.category if agent.role else ""
        },
        "behavior_template": agent.template.template_data if agent.template else {},
        "injection_target": agent.injection_target,
        "custom_config": agent.config or {},
        "server_url": "http://localhost:8000",  # LISA backend URL
        "heartbeat_interval": 86400,  # 24 hours
        "created_at": agent.created_at.isoformat(),
        "version": "1.0"
    }
    
    # Create temporary file
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

@router.get("/agents/{agent_id}/status")
def get_agent_status(agent_id: str, db: Session = Depends(get_db)):
    """Get agent status and recent activities"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get recent activities (heartbeats, etc.)
    recent_activities = db.query(AgentActivity).filter(
        AgentActivity.agent_id == agent.id
    ).order_by(desc(AgentActivity.timestamp)).limit(10).all()
    
    return {
        "agent": {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": agent.status,
            "os_type": agent.os_type,
            "role": agent.role.name if agent.role else "Unknown",
            "template": agent.template.name if agent.template else "Unknown",
            "injection_target": agent.injection_target,
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

# SIMPLE DEPLOYMENT (Future enhancement)
@router.post("/agents/{agent_id}/deploy")
def deploy_agent_simple(agent_id: str, deployment_info: dict, db: Session = Depends(get_db)):
    """Simple agent deployment (placeholder for future)"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent status
    agent.status = "deploying"
    agent.injection_target = deployment_info.get("target_host", "localhost")
    db.commit()
    
    # Log deployment attempt
    activity = AgentActivity(
        agent_id=agent.id,
        activity_type="deployment_initiated",
        activity_data={
            "target_host": deployment_info.get("target_host", "localhost"),
            "deployment_method": deployment_info.get("method", "manual"),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    db.add(activity)
    db.commit()
    
    return {
        "status": "deployment_initiated",
        "agent_id": agent_id,
        "target_host": deployment_info.get("target_host", "localhost"),
        "message": "Deployment process started. Use config download URL to get agent configuration."
    }
