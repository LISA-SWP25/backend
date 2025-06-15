# Behavior templates
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.deps import get_db
from app.models.models import Role, BehaviorTemplate
from app.schemas import BehaviorTemplateCreate, BehaviorTemplateResponse

router = APIRouter()

@router.post("/behavior-templates", response_model=BehaviorTemplateResponse)
def create_behavior_template(template: BehaviorTemplateCreate, db: Session = Depends(get_db)):
    """Create a new behavior template"""
    # Verify role exists
    role = db.query(Role).filter(Role.id == template.role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check for duplicate name within the same role
    existing = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.name == template.name,
        BehaviorTemplate.role_id == template.role_id,
        BehaviorTemplate.is_active == True
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Template '{template.name}' already exists for this role"
        )
    
    db_template = BehaviorTemplate(
        name=template.name,
        role_id=template.role_id,
        os_type=template.os_type,
        template_data=template.template_data.dict(),
        version=getattr(template, 'version', "1.0")
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/behavior-templates", response_model=List[BehaviorTemplateResponse])
def list_behavior_templates(
    os_type: Optional[str] = None,
    role_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of behavior templates with filtering"""
    query = db.query(BehaviorTemplate).filter(BehaviorTemplate.is_active == True)
    
    if os_type:
        if os_type not in ["windows", "linux"]:
            raise HTTPException(status_code=400, detail="os_type must be 'windows' or 'linux'")
        query = query.filter(BehaviorTemplate.os_type == os_type)
    
    if role_id:
        query = query.filter(BehaviorTemplate.role_id == role_id)
    
    templates = query.offset(skip).limit(limit).all()
    return templates

@router.get("/behavior-templates/{template_id}", response_model=BehaviorTemplateResponse)
def get_behavior_template(template_id: int, db: Session = Depends(get_db)):
    """Get behavior template by ID"""
    template = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.id == template_id,
        BehaviorTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
