# CI/CD Build Management
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import subprocess
import os

from app.deps import get_db
from app.models.models import Agent, AgentBuild
from app.schemas import AgentBuildRequest, AgentBuildResponse

router = APIRouter()

async def build_agent_task(agent_id: str, db_session: Session):
    """Background task for CI/CD build process"""
    agent = db_session.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        return
    
    # Get build record
    build = db_session.query(AgentBuild).filter(
        AgentBuild.agent_id == agent.id,
        AgentBuild.build_status == "building"
    ).first()
    
    if not build:
        return
    
    try:
        # Step 1: Download agent config
        config_path = f"/tmp/{agent_id}_config.json"
        # This would call the config download endpoint
        
        # Step 2: Call agent builder (provided by Agent Development team)
        build_command = [
            "python", "agent_builder.py",
            "--config", config_path,
            "--os", agent.os_type,
            "--output", f"/builds/{agent_id}"
        ]
        
        result = subprocess.run(build_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Build successful
            binary_path = f"/builds/{agent_id}.exe" if agent.os_type == "windows" else f"/builds/{agent_id}"
            binary_size = os.path.getsize(binary_path) if os.path.exists(binary_path) else 0
            
            build.build_status = "ready"
            build.binary_path = binary_path
            build.binary_size = binary_size
            build.build_log = result.stdout
            build.completed_at = datetime.utcnow()
            
            # Update agent status
            agent.status = "built"
            
        else:
            # Build failed
            build.build_status = "failed"
            build.build_log = result.stderr
            build.completed_at = datetime.utcnow()
            
            agent.status = "error"
    
    except Exception as e:
        build.build_status = "failed"
        build.build_log = f"Build error: {str(e)}"
        build.completed_at = datetime.utcnow()
        agent.status = "error"
    
    db_session.commit()

@router.post("/builds", response_model=AgentBuildResponse)
def trigger_agent_build(
    request: AgentBuildRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger CI/CD build for agent"""
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
        "role": agent.role.name,
        "template": agent.template.name,
        "os_type": agent.os_type,
        "compilation_options": request.compilation_options
    }
    
    db_build = AgentBuild(
        agent_id=agent.id,
        build_config=build_config,
        build_status="building"
    )
    db.add(db_build)
    
    # Update agent status
    agent.status = "building"
    
    db.commit()
    db.refresh(db_build)
    
    # Start background build task
    background_tasks.add_task(build_agent_task, agent.agent_id, db)
    
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
