from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "docs": "/docs"
    }
