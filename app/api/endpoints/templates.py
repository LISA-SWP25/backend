from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.deps import get_db
from app.models.models import BehaviorTemplate, Role
from app.schemas import BehaviorTemplateCreate, BehaviorTemplateResponse, BehaviorTemplateUpdate

router = APIRouter()

@router.post("/behavior-templates", 
            response_model=BehaviorTemplateResponse,
            summary="Create Behavior Template",
            description="Create a new behavior template linked to a role")
def create_behavior_template(
    template: BehaviorTemplateCreate, 
    db: Session = Depends(get_db)
):
    """
    Create new behavior template
    
    **Required workflow:**
    1. First create a role using POST /api/roles
    2. Use the role ID in this template creation
    3. Template defines how agents behave (schedule, apps, patterns)
    
    **Example template_data:**
    ```json
    {
        "work_schedule": {
            "start_time": "09:00",
            "end_time": "18:00",
            "breaks": [{"start": "13:00", "duration_minutes": 60}]
        },
        "applications_used": ["VS Code", "Chrome", "Slack"],
        "activity_pattern": "Regular office hours"
    }
    ```
    """
    
    # Validate that role exists
    role = db.query(Role).filter(Role.id == template.role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(
            status_code=404, 
            detail=f"Role with id {template.role_id} not found. Create role first using POST /api/roles"
        )
    
    # Check if name already exists for the same role
    existing = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.name == template.name,
        BehaviorTemplate.role_id == template.role_id,
        BehaviorTemplate.is_active == True
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Template '{template.name}' already exists for role '{role.name}'"
        )
    
    db_template = BehaviorTemplate(
        name=template.name,
        role_id=template.role_id,
        template_data=template.template_data,
        os_type=template.os_type,
        version=template.version
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/behavior-templates", 
           response_model=List[BehaviorTemplateResponse],
           summary="List Behavior Templates",
           description="Get list of all behavior templates with optional filtering")
def list_behavior_templates(
    role_id: Optional[int] = None,
    os_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of behavior templates"""
    query = db.query(BehaviorTemplate).filter(BehaviorTemplate.is_active == True)
    
    if role_id:
        query = query.filter(BehaviorTemplate.role_id == role_id)
    if os_type:
        query = query.filter(BehaviorTemplate.os_type == os_type)
    
    templates = query.offset(skip).limit(limit).all()
    return templates

@router.get("/behavior-templates/{template_id}", 
           response_model=BehaviorTemplateResponse,
           summary="Get Behavior Template",
           description="Get specific behavior template by ID")
def get_behavior_template(template_id: int, db: Session = Depends(get_db)):
    """Get behavior template by ID"""
    template = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.id == template_id,
        BehaviorTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/behavior-templates/{template_id}", 
           response_model=BehaviorTemplateResponse,
           summary="Update Behavior Template",
           description="Update existing behavior template")
def update_behavior_template(
    template_id: int, 
    template_update: BehaviorTemplateUpdate, 
    db: Session = Depends(get_db)
):
    """Update behavior template"""
    template = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.id == template_id,
        BehaviorTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate role exists if changing role_id
    if template_update.role_id and template_update.role_id != template.role_id:
        role = db.query(Role).filter(
            Role.id == template_update.role_id, 
            Role.is_active == True
        ).first()
        if not role:
            raise HTTPException(
                status_code=404, 
                detail=f"Role with id {template_update.role_id} not found"
            )
    
    # Check name uniqueness if changing
    if template_update.name and template_update.name != template.name:
        existing = db.query(BehaviorTemplate).filter(
            BehaviorTemplate.name == template_update.name,
            BehaviorTemplate.role_id == template_update.role_id or template.role_id,
            BehaviorTemplate.is_active == True,
            BehaviorTemplate.id != template_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, 
                detail="Template name already exists for this role"
            )
    
    # Update fields
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template

@router.delete("/behavior-templates/{template_id}",
              summary="Delete Behavior Template",
              description="Soft delete behavior template")
def delete_behavior_template(template_id: int, db: Session = Depends(get_db)):
    """Delete behavior template (soft delete)"""
    template = db.query(BehaviorTemplate).filter(
        BehaviorTemplate.id == template_id,
        BehaviorTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template.is_active = False
    db.commit()
    return {"message": f"Template '{template.name}' deleted successfully"}
