# app/api/endpoints/system.py - System endpoints
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.deps import get_db
from app.models.models import Role, BehaviorTemplate, Agent, AgentBuild

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """System health check"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow(),
        "components": {
            "database": db_status,
            "api": "healthy"
        },
        "version": "0.1.0"
    }

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    stats = {
        "roles": {
            "total": db.query(Role).filter(Role.is_active == True).count(),
            "by_category": {}
        },
        "templates": {
            "total": db.query(BehaviorTemplate).filter(BehaviorTemplate.is_active == True).count(),
            "by_os": {}
        },
        "agents": {
            "total": db.query(Agent).count(),
            "by_status": {},
            "by_os": {}
        },
        "builds": {
            "total": db.query(AgentBuild).count(),
            "by_status": {}
        }
    }
    
    # Role stats by category
    role_categories = db.query(
        Role.category, func.count(Role.id)
    ).filter(Role.is_active == True).group_by(Role.category).all()
    
    for category, count in role_categories:
        stats["roles"]["by_category"][category] = count
    
    # Template stats by OS
    template_os = db.query(
        BehaviorTemplate.os_type, func.count(BehaviorTemplate.id)
    ).filter(BehaviorTemplate.is_active == True).group_by(BehaviorTemplate.os_type).all()
    
    for os_type, count in template_os:
        stats["templates"]["by_os"][os_type] = count
    
    # Agent stats
    agent_status = db.query(
        Agent.status, func.count(Agent.id)
    ).group_by(Agent.status).all()
    
    for status, count in agent_status:
        stats["agents"]["by_status"][status] = count
    
    # Build stats
    build_status = db.query(
        AgentBuild.build_status, func.count(AgentBuild.id)
    ).group_by(AgentBuild.build_status).all()
    
    for status, count in build_status:
        stats["builds"]["by_status"][status] = count
    
    return stats

@router.get("/demo/workflow")
def demo_workflow():
    """Demo workflow for MVP V0"""
    return {
        "title": "LISA System Workflow (Backend/CI-CD Perspective)",
        "description": "Database and CI/CD process flow",
        "steps": [
            {
                "step": 1,
                "title": "Create Role (Backend)",
                "endpoint": "POST /api/roles",
                "responsibility": "Backend API"
            },
            {
                "step": 2,
                "title": "Create Template (Backend)",
                "endpoint": "POST /api/behavior-templates",
                "responsibility": "Backend API"
            },
            {
                "step": 3,
                "title": "Generate Config (Backend)",
                "endpoint": "POST /api/agents/generate",
                "responsibility": "Backend API"
            },
            {
                "step": 4,
                "title": "Trigger Build (CI/CD)",
                "endpoint": "POST /api/builds",
                "responsibility": "CI/CD Pipeline"
            },
            {
                "step": 5,
                "title": "Monitor Build (CI/CD)",
                "endpoint": "GET /api/builds/{id}",
                "responsibility": "CI/CD Pipeline"
            }
        ],
        "my_responsibilities": [
            "Database management",
            "CRUD API endpoints",
            "CI/CD build pipeline",
            "Configuration generation",
            "Agent deployment automation"
        ],
        "not_my_responsibilities": [
            "Agent runtime logic",
            "Process injection",
            "Activity simulation",
            "OS log generation"
        ]
    }
