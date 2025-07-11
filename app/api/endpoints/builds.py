from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.deps import get_db
from app.models.models import Agent, AgentBuild
from app.schemas import AgentBuildRequest, AgentBuildResponse

router = APIRouter()

@router.post("/builds", response_model=AgentBuildResponse)
def trigger_agent_build(
    request: AgentBuildRequest,
    db: Session = Depends(get_db)
):
    """Trigger CI/CD build for agent (MVP - simplified)"""
    agent = db.query(Agent).filter(Agent.agent_id == request.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if there's already a build in progress
    existing_build = db.query(AgentBuild).filter(
        AgentBuild.agent_id == agent.id,
        AgentBuild.build_status.in_(["pending", "building"])
    ).first()
    
    if existing_build and not request.force_rebuild:
        raise HTTPException(status_code=409, detail="Build already in progress")
    
    # Create new build record
    build_config = {
        "agent_id": agent.agent_id,
        "role": agent.role.name if agent.role else "Unknown",
        "template": agent.template.name if agent.template else "Unknown", 
        "os_type": agent.os_type,
        "compilation_options": request.compilation_options or {}
    }
    
    # For MVP - simulate build process
    db_build = AgentBuild(
        agent_id=agent.id,
        build_config=build_config,
        build_status="ready",  # MVP: immediately mark as ready
        binary_path=f"/builds/{agent.agent_id}_{agent.os_type}",
        binary_size=1024000,  # Mock 1MB binary
        build_log="MVP Build: Agent configuration prepared successfully.",
        build_time=5,  # Mock 5 second build time
        completed_at=datetime.utcnow()
    )
    db.add(db_build)
    
    # Update agent status
    agent.status = "built"
    
    db.commit()
    db.refresh(db_build)
    
    return db_build

@router.get("/builds", response_model=List[AgentBuildResponse])
def list_builds(
    status: Optional[str] = None,
    agent_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List agent builds"""
    query = db.query(AgentBuild)
    
    if status:
        query = query.filter(AgentBuild.build_status == status)
    
    if agent_id:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if agent:
            query = query.filter(AgentBuild.agent_id == agent.id)
    
    builds = query.order_by(AgentBuild.created_at.desc()).offset(skip).limit(limit).all()
    return builds

@router.get("/builds/{build_id}", response_model=AgentBuildResponse)
def get_build_status(build_id: int, db: Session = Depends(get_db)):
    """Get build status by ID"""
    build = db.query(AgentBuild).filter(AgentBuild.id == build_id).first()
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build

@router.delete("/builds/{build_id}")
def delete_build(build_id: int, db: Session = Depends(get_db)):
    """Delete build record"""
    build = db.query(AgentBuild).filter(AgentBuild.id == build_id).first()
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    db.delete(build)
    db.commit()
    return {"message": "Build deleted successfully"}
