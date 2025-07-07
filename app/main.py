from app.database import Base, engine
from app.api.endpoints import roles, templates, agents, builds, system, monitoring
from app.api import websocket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# Create app first
app = FastAPI(
    title=\"LISA Backend API\",
    description=\"Legitimate Infrastructure Simulation Agent - Management API\",
    version=\"0.1.0\",
    docs_url=\"/docs\",
    redoc_url=\"/redoc\"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"http://localhost:3000\", \"http://localhost:5173\", \"*\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

# Database setup with error handling
try:
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print(\"Database tables created\")
except Exception as e:
    print(f\"Database setup failed: {e}\")

# ==================== DASHBOARD DATA ====================

@app.get(\"/api/dashboard/stats\")
def get_dashboard_stats():
    \"\"\"Get dashboard statistics\"\"\"
    try:
        # Try to get real data from database
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Count agents if table exists
            try:
                result = conn.execute(text(\"SELECT COUNT(*) FROM agents\"))
                total_agents = result.scalar() or 0
            except:
                total_agents = 0
            
            # Count application templates if table exists
            try:
                result = conn.execute(text(\"SELECT COUNT(*) FROM applications_template WHERE is_active = true\"))
                app_templates = result.scalar() or 0
            except:
                app_templates = 2  # Mock data
        
        return {
            \"total_agents\": total_agents,
            \"online_agents\": 0,
            \"offline_agents\": total_agents,
            \"total_activities\": 0,
            \"application_templates\": app_templates,
            \"avg_activities_per_agent\": 0.0,
            \"system_status\": \"healthy\"
        }
    except Exception as e:
        # Fallback to mock data
        return {
            \"total_agents\": 0,
            \"online_agents\": 0,
            \"offline_agents\": 0,
            \"total_activities\": 0,
            \"application_templates\": 2,
            \"avg_activities_per_agent\": 0.0,
            \"system_status\": \"database_unavailable\"
        }

# Safe router imports with error handling
routers_loaded = []

# Heartbeat router
try:
    from app.api.endpoints import heartbeat
    app.include_router(heartbeat.router, prefix=\"/api\", tags=[\"Heartbeat\"])
    routers_loaded.append(\"heartbeat\")
except ImportError as e:
    print(f\"Warning: Could not import heartbeat router: {e}\")

# Roles router
try:
    from app.api.endpoints import roles
    app.include_router(roles.router, prefix=\"/api\", tags=[\"Roles\"])
    routers_loaded.append(\"roles\")
except ImportError as e:
    print(f\"Warning: Could not import roles router: {e}\")

# Templates router
try:
    from app.api.endpoints import templates
    app.include_router(templates.router, prefix=\"/api\", tags=[\"Templates\"])
    routers_loaded.append(\"templates\")
except ImportError as e:
    print(f\"Warning: Could not import templates router: {e}\")

# Agents router
try:
    from app.api.endpoints import agents
    app.include_router(agents.router, prefix=\"/api\", tags=[\"Agents\"])
    routers_loaded.append(\"agents\")
except ImportError as e:
    print(f\"Warning: Could not import agents router: {e}\")

# Builds router
try:
    from app.api.endpoints import builds
    app.include_router(builds.router, prefix=\"/api\", tags=[\"CI/CD\"])
    routers_loaded.append(\"builds\")
except ImportError as e:
    print(f\"Warning: Could not import builds router: {e}\")

# System router
try:
    from app.api.endpoints import system
    app.include_router(system.router, prefix=\"/api\", tags=[\"System\"])
    routers_loaded.append(\"system\")
except ImportError as e:
    print(f\"Warning: Could not import system router: {e}\")

# Monitoring router
try:
    from app.api.endpoints import monitoring
    app.include_router(monitoring.router, prefix=\"/api\", tags=[\"Monitoring\"])
    routers_loaded.append(\"monitoring\")
except ImportError as e:
    print(f\"Warning: Could not import monitoring router: {e}\")

# WebSocket router
try:
    from app.api import websocket
    app.include_router(websocket.router, prefix=\"/api\", tags=[\"WebSocket\"])
    routers_loaded.append(\"websocket\")
except ImportError as e:
    print(f\"Warning: Could not import websocket router: {e}\")

# Applications router (ApplicationTemplate)
try:
    from app.api.endpoints import applications
    app.include_router(applications.router, prefix=\"/api\", tags=[\"Applications\"])
    routers_loaded.append(\"applications\")
except ImportError as e:
    print(f\"Warning: Could not import applications router: {e}\")
    
    # Create fallback applications endpoints
    from fastapi import APIRouter
    applications_fallback = APIRouter()
    
    @applications_fallback.get(\"/application-templates\")
    def list_templates_fallback():
        return [
            {
                \"id\": 1,
                \"name\": \"vscode\",
                \"display_name\": \"Visual Studio Code\",
                \"category\": \"development\",
                \"version\": \"1.0\",
                \"os_type\": \"linux\",
                \"is_active\": True,
                \"template_config\": {\"installation\": {\"check_command\": \"code --version\"}}
            },
            {
                \"id\": 2,
                \"name\": \"firefox\",
                \"display_name\": \"Firefox Browser\",
                \"category\": \"browser\",
                \"version\": \"1.0\",
                \"os_type\": \"linux\",
                \"is_active\": True,
                \"template_config\": {\"installation\": {\"check_command\": \"firefox --version\"}}
            }
        ]
    
    @applications_fallback.post(\"/application-templates\")
    def create_template_fallback(template: dict):
        return {
            \"id\": 999,
            \"name\": template.get(\"name\", \"new-app\"),
            \"display_name\": template.get(\"display_name\", \"New App\"),
            \"message\": \"Template created (fallback mode)\"
        }
    
    @applications_fallback.get(\"/application-templates/categories\")
    def categories_fallback():
        return {\"categories\": [\"development\", \"browser\", \"communication\", \"office\"]}
    
    app.include_router(applications_fallback, prefix=\"/api\", tags=[\"Applications (Fallback)\"])
    routers_loaded.append(\"applications-fallback\")

@app.get(\"/\")
def root():
    return {
        \"service\": \"LISA Backend API\",
        \"version\": \"0.1.0\",
        \"status\": \"running\",
        \"docs\": \"/docs\",
        \"integration\": \"enabled\",
        \"routers_loaded\": routers_loaded,
        \"timestamp\": datetime.now().isoformat()
    }

@app.get(\"/api/health\")
def health():
    try:
        from app.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text(\"SELECT 1\"))
        db_status = \"connected\"
    except Exception as e:
        db_status = f\"error: {str(e)}\"
    
    return {
        \"status\": \"healthy\",
        \"timestamp\": datetime.now().isoformat(),
        \"database\": db_status,
        \"routers_active\": len(routers_loaded),
        \"loaded_modules\": routers_loaded
    }

@app.get(\"/api/stats\")
def get_stats():
    return get_dashboard_stats()

# Background task for cleaning up inactive agents
@app.on_event(\"startup\")
async def startup_event():
    print(f\" LISA Backend started with {len(routers_loaded)} routers: {', '.join(routers_loaded)}\")
    # This would start a background task to monitor agent health
    pass

@app.on_event(\"shutdown\")
async def shutdown_event():
    print(\" LISA Backend shutting down...\")
    # Cleanup connections
    pass

if __name__ == \"__main__\":
    import uvicorn
    uvicorn.run(app, host=\"0.0.0.0\", port=8000)

