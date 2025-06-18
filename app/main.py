from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, List, Optional
import uuid
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

# Временное хранилище для интеграции (в продакшене будет БД)
active_agents = {}
agent_activities = {}
pending_commands = {}

# ==================== AGENT MANAGEMENT ====================

@app.post("/api/agents/register")
def register_agent(agent_data: dict):
    """Регистрация агента в системе"""
    agent_id = agent_data.get("agent_id", f"USR{str(uuid.uuid4().int)[:7]}")
    
    agent_info = {
        "agent_id": agent_id,
        "status": "online",
        "registered_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "host_info": agent_data.get("host_info", {}),
        "activities_count": 0
    }
    
    active_agents[agent_id] = agent_info
    agent_activities[agent_id] = []
    
    return {
        "success": True,
        "agent_id": agent_id,
        "message": "Agent registered successfully",
        "status": "online"
    }

@app.post("/api/agents/deploy")
def deploy_agent(deployment_config: dict):
    """Развертывание нового агента"""
    agent_id = f"USR{str(uuid.uuid4().int)[:7]}"
    
    # Симуляция процесса развертывания
    agent_config = {
        "agent_id": agent_id,
        "status": "deploying",
        "target_os": deployment_config.get("os", "linux"),
        "role": deployment_config.get("role", "user"),
        "target_host": deployment_config.get("target_host", "localhost"),
        "deployed_at": datetime.now().isoformat(),
        "deployment_status": "in_progress"
    }
    
    # Добавляем в активные агенты (в реальности будет асинхронно)
    active_agents[agent_id] = {
        **agent_config,
        "status": "online",  # Симулируем что развернулся
        "last_seen": datetime.now().isoformat(),
        "activities_count": 0
    }
    agent_activities[agent_id] = []
    
    return {
        "success": True,
        "agent_id": agent_id,
        "status": "deployed",
        "message": f"Agent deployed on {agent_config['target_host']}",
        "config": agent_config,
        "management_url": f"/api/agents/{agent_id}"
    }

@app.get("/api/agents/active")
def get_active_agents():
    """Получить список активных агентов"""
    agents_list = []
    
    for agent_id, agent_info in active_agents.items():
        # Обновляем статус (если не было активности > 5 мин = offline)
        last_seen = datetime.fromisoformat(agent_info["last_seen"].replace('Z', '+00:00'))
        time_diff = (datetime.now() - last_seen.replace(tzinfo=None)).total_seconds()
        
        status = "online" if time_diff < 300 else "offline"
        
        agents_list.append({
            "id": agent_id,
            "name": f"Agent-{agent_id[-4:]}",
            "status": status,
            "host": agent_info.get("host_info", {}).get("hostname", "unknown"),
            "last_seen": agent_info["last_seen"],
            "activities_count": agent_info["activities_count"]
        })
    
    return {
        "agents": agents_list,
        "total_count": len(agents_list),
        "online_count": len([a for a in agents_list if a["status"] == "online"])
    }

@app.get("/api/agents/{agent_id}/status")
def get_agent_status(agent_id: str):
    """Получить детальный статус агента"""
    if agent_id not in active_agents:
        return {"error": "Agent not found", "agent_id": agent_id}
    
    agent_info = active_agents[agent_id]
    
    return {
        "agent_id": agent_id,
        "name": f"Agent-{agent_id[-4:]}",
        "status": agent_info["status"],
        "last_seen": agent_info["last_seen"],
        "registered_at": agent_info.get("registered_at"),
        "host_info": agent_info.get("host_info", {}),
        "activities_count": len(agent_activities.get(agent_id, [])),
        "uptime": "2h 15m",  # Можно вычислить реально
        "performance": {
            "cpu_usage": "15%",
            "memory_usage": "45MB",
            "network_status": "connected"
        }
    }

# ==================== ACTIVITY TRACKING ====================

@app.post("/api/agents/activity")
def receive_agent_activity(activity_data: dict):
    """Получить активность от агента"""
    agent_id = activity_data.get("agent_id")
    
    if agent_id not in active_agents:
        return {"error": "Agent not registered", "agent_id": agent_id}
    
    # Обновляем last_seen
    active_agents[agent_id]["last_seen"] = datetime.now().isoformat()
    active_agents[agent_id]["activities_count"] += 1
    
    # Добавляем активность
    activity = {
        "id": len(agent_activities[agent_id]) + 1,
        "time": activity_data.get("timestamp", datetime.now().isoformat()),
        "action": activity_data.get("action", "unknown"),
        "user": activity_data.get("user", "system"),
        "details": activity_data.get("details", {})
    }
    
    agent_activities[agent_id].append(activity)
    
    # Оставляем только последние 100 активностей
    if len(agent_activities[agent_id]) > 100:
        agent_activities[agent_id] = agent_activities[agent_id][-100:]
    
    return {
        "success": True,
        "message": "Activity recorded",
        "activity_id": activity["id"]
    }

@app.get("/api/agents/{agent_id}/activities")
def get_agent_activities(agent_id: str, limit: int = 20):
    """Получить активности агента"""
    if agent_id not in agent_activities:
        return {"error": "Agent not found", "activities": []}
    
    activities = agent_activities[agent_id][-limit:]  # Последние N активностей
    activities.reverse()  # Сначала новые
    
    return {
        "agent_id": agent_id,
        "activities": activities,
        "total_count": len(agent_activities[agent_id])
    }

@app.get("/api/activities/recent")
def get_recent_activities(limit: int = 50):
    """Получить последние активности от всех агентов"""
    all_activities = []
    
    for agent_id, activities in agent_activities.items():
        for activity in activities:
            all_activities.append({
                **activity,
                "agent_id": agent_id,
                "agent_name": f"Agent-{agent_id[-4:]}"
            })
    
    # Сортируем по времени (новые сначала)
    all_activities.sort(key=lambda x: x["time"], reverse=True)
    
    return {
        "activities": all_activities[:limit],
        "total_count": len(all_activities)
    }

# ==================== COMMAND CONTROL ====================

@app.post("/api/agents/{agent_id}/command")
def send_command_to_agent(agent_id: str, command_data: dict):
    """Отправить команду агенту"""
    if agent_id not in active_agents:
        return {"error": "Agent not found"}
    
    command = {
        "command_id": f"CMD{str(uuid.uuid4().int)[:6]}",
        "action": command_data.get("action"),
        "parameters": command_data.get("parameters", {}),
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    if agent_id not in pending_commands:
        pending_commands[agent_id] = []
    
    pending_commands[agent_id].append(command)
    
    return {
        "success": True,
        "command_id": command["command_id"],
        "status": "sent",
        "message": f"Command sent to {agent_id}"
    }

@app.get("/api/agents/{agent_id}/commands")
def get_pending_commands(agent_id: str):
    """Получить ожидающие команды для агента"""
    commands = pending_commands.get(agent_id, [])
    
    # Очищаем команды после получения
    if agent_id in pending_commands:
        pending_commands[agent_id] = []
    
    return {
        "agent_id": agent_id,
        "commands": commands,
        "count": len(commands)
    }

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

# ==================== DEMO DATA ====================

@app.post("/api/demo/create-test-data")
def create_demo_data():
    """ Тестовые данные для демонстрации"""
    
    # тестовые агенты
    demo_agents = [
        {
            "agent_id": "USR1001001",
            "host_info": {"hostname": "dev-workstation", "os": "linux", "ip": "192.168.1.101"},
            "role": "developer"
        },
        {
            "agent_id": "USR2002002", 
            "host_info": {"hostname": "admin-server", "os": "linux", "ip": "192.168.1.102"},
            "role": "admin"
        },
        {
            "agent_id": "USR3003003",
            "host_info": {"hostname": "user-laptop", "os": "windows", "ip": "192.168.1.103"},
            "role": "user"
        }
    ]
    
    for agent_data in demo_agents:
        register_agent(agent_data)
    
    # тестовые активности
    demo_activities = [
        {"agent_id": "USR1001001", "action": "git commit -m 'fix: resolve API bug'", "user": "developer"},
        {"agent_id": "USR1001001", "action": "npm install axios", "user": "developer"},
        {"agent_id": "USR2002002", "action": "sudo systemctl restart nginx", "user": "admin"},
        {"agent_id": "USR2002002", "action": "tail -f /var/log/auth.log", "user": "admin"},
        {"agent_id": "USR3003003", "action": "firefox https://github.com", "user": "user"},
        {"agent_id": "USR3003003", "action": "notepad++ document.txt", "user": "user"},
    ]
    
    for activity in demo_activities:
        activity["timestamp"] = datetime.now().isoformat()
        receive_agent_activity(activity)
    
    return {
        "success": True,
        "message": "Demo data created",
        "agents_created": len(demo_agents),
        "activities_created": len(demo_activities)
    }

# Create tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

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
