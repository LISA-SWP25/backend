from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from app.api.endpoints import heartbeat

# Database imports
from app.database import Base, engine
from app.api.endpoints import roles, templates, agents, builds, system, monitoring
from app.api import websocket

# Create tables
Base.metadata.create_all(bind=engine)

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
    """Get dashboard statistics"""
    # For now, return mock data
    # In production, this should query the database
    return {
        "total_agents": 0,
        "online_agents": 0,
        "offline_agents": 0,
        "total_activities": 0,
        "avg_activities_per_agent": 0.0,
        "system_status": "healthy"
    }

# Include routers
app.include_router(roles.router, prefix="/api", tags=["Roles"])
app.include_router(templates.router, prefix="/api", tags=["Templates"])
app.include_router(agents.router, prefix="/api", tags=["Agents"])
app.include_router(heartbeat.router, prefix="/api", tags=["Heartbeat"])
app.include_router(builds.router, prefix="/api", tags=["CI/CD"])
app.include_router(system.router, prefix="/api", tags=["System"])
app.include_router(monitoring.router, prefix="/api", tags=["Monitoring"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])


@app.get("/")
def root():
    return {
        "service": "LISA Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "integration": "enabled"
    }

# Background task for cleaning up inactive agents
@app.on_event("startup")
async def startup_event():
    # This would start a background task to monitor agent health
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup connections
    pass
