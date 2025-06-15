# Role management
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.deps import get_db
from app.models.models import Role
from app.schemas import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()

@router.post("/roles", response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role"""
    # Check if role name already exists
    existing = db.query(Role).filter(Role.name == role.name, Role.is_active == True).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Role '{role.name}' already exists")
    
    db_role = Role(
        name=role.name,
        description=role.description,
        category=role.category
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of roles with optional filtering"""
    query = db.query(Role).filter(Role.is_active == True)
    
    if category:
        query = query.filter(Role.category == category)
    
    roles = query.offset(skip).limit(limit).all()
    return roles

@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get role details by ID"""
    role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role_update: RoleUpdate, db: Session = Depends(get_db)):
    """Update existing role"""
    role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check name uniqueness if changing
    if role_update.name and role_update.name != role.name:
        existing = db.query(Role).filter(
            Role.name == role_update.name,
            Role.is_active == True,
            Role.id != role_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role name already exists")
    
    # Update fields
    if role_update.name:
        role.name = role_update.name
    if role_update.description is not None:
        role.description = role_update.description
    if role_update.category:
        role.category = role_update.category
    
    db.commit()
    db.refresh(role)
    return role

@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Soft delete role"""
    role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if role has active agents
    from app.models.models import Agent
    active_agents = db.query(Agent).filter(
        Agent.role_id == role_id,
        Agent.status.in_(["online", "building"])
    ).count()
    
    if active_agents > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role: {active_agents} active agents are using it"
        )
    
    role.is_active = False
    db.commit()
    return {"message": f"Role '{role.name}' deleted successfully"}
