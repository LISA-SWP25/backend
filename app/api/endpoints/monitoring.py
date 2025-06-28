from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict
from datetime import datetime, timedelta
import json

from app.deps import get_db
from app.models.models import Agent, AgentActivity

router = APIRouter()

@router.post("/agents/{agent_id}/heartbeat")
def receive_heartbeat(
    agent_id: str,
    heartbeat: dict,
    db: Session = Depends(get_db)
):
    """Receive heartbeat from agent"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent status
    agent.last_seen = datetime.utcnow()
    agent.status = "active"
    
    # Log heartbeat
    activity = AgentActivity(
        agent_id=agent.id,
        activity_type="heartbeat",
        activity_data={
            "timestamp": heartbeat.get("timestamp", datetime.utcnow().isoformat()),
            "status": heartbeat.get("status", "active"),
            "current_activity": heartbeat.get("current_activity"),
            "system_info": heartbeat.get("system_info", {})
        }
    )
    db.add(activity)
    db.commit()
    
    return {"status": "received", "next_check_in": 60}

@router.get("/monitoring/overview")
def get_monitoring_overview(db: Session = Depends(get_db)):
    """Get system-wide monitoring overview"""
    # Get all agents
    agents = db.query(Agent).all()
    
    # Calculate statistics
    total_agents = len(agents)
    active_agents = 0
    inactive_agents = 0
    failed_agents = 0
    
    threshold = datetime.utcnow() - timedelta(minutes=5)
    
    for agent in agents:
        if agent.status == "deployment_failed":
            failed_agents += 1
        elif agent.last_seen and agent.last_seen > threshold:
            active_agents += 1
        else:
            inactive_agents += 1
    
    # Get recent activities
    recent_activities = db.query(AgentActivity).order_by(
        desc(AgentActivity.timestamp)
    ).limit(50).all()
    
    return {
        "statistics": {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "inactive_agents": inactive_agents,
            "failed_agents": failed_agents
        },
        "recent_activities": [
            {
                "agent_id": act.agent.agent_id if act.agent else "unknown",
                "agent_name": act.agent.name if act.agent else "unknown",
                "activity_type": act.activity_type,
                "timestamp": act.timestamp.isoformat() if act.timestamp else None,
                "data": act.activity_data
            } for act in recent_activities
        ],
        "system_health": "healthy" if active_agents > 0 else "degraded"
    }

@router.get("/agents/{agent_id}/logs/stream")
async def stream_agent_logs(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Stream real-time logs from agent"""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get last 100 activities
    activities = db.query(AgentActivity).filter(
        AgentActivity.agent_id == agent.id
    ).order_by(desc(AgentActivity.timestamp)).limit(100).all()
    
    return {
        "agent_id": agent_id,
        "logs": [
            {
                "timestamp": act.timestamp.isoformat() if act.timestamp else None,
                "level": "INFO",
                "message": f"{act.activity_type}: {json.dumps(act.activity_data)}"
            } for act in activities
        ]
    }
