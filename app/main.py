from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# Database imports
from app.database import Base, engine
from app.api.endpoints import roles, templates, agents, builds, system

app = FastAPI(
    title="LISA Backend API",
    description="Legitimate Infrastructure Simulation Agent - Management API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DASHBOARD DATA ====================

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """Получить статистику для dashboard"""
    total_agents = len(active_agents)
    online_agents = 0
    total_activities = 0
    
    for agent_id, agent_info in active_agents.items():
        last_seen = datetime.fromisoformat(agent_info["last_seen"].replace('Z', '+00:00'))
        time_diff = (datetime.now() - last_seen.replace(tzinfo=None)).total_seconds()
        
        if time_diff < 300:  # Онлайн если активность < 5 мин назад
            online_agents += 1
        
        total_activities += len(agent_activities.get(agent_id, []))
    
    return {
        "total_agents": total_agents,
        "online_agents": online_agents,
        "offline_agents": total_agents - online_agents,
        "total_activities": total_activities,
        "avg_activities_per_agent": total_activities / max(total_agents, 1),
        "system_status": "healthy" if online_agents > 0 else "no_agents"
    }

# Include routers
app.include_router(roles.router, prefix="/api", tags=["Roles"])
app.include_router(templates.router, prefix="/api", tags=["Templates"])
app.include_router(agents.router, prefix="/api", tags=["Agents"])
app.include_router(builds.router, prefix="/api", tags=["CI/CD"])
app.include_router(system.router, prefix="/api", tags=["System"])

@app.get("/")
def root():
    return {
        "service": "LISA Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "integration": "enabled"
    }
