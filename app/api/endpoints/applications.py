from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.deps import get_db
from app.models.models import ApplicationTemplate
from app.schemas import ApplicationTemplateCreate, ApplicationTemplateResponse, ApplicationTemplateUpdate

router = APIRouter()

@router.post(\"/application-templates\", response_model=ApplicationTemplateResponse)
def create_application_template(template: ApplicationTemplateCreate, db: Session = Depends(get_db)):
    \"\"\"Создать новый шаблон приложения\"\"\"
    # Проверяем уникальность имени
    existing = db.query(ApplicationTemplate).filter(
        ApplicationTemplate.name == template.name,
        ApplicationTemplate.is_active == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f\"Template '{template.name}' already exists\")
    
    db_template = ApplicationTemplate(
        name=template.name,
        display_name=template.display_name,
        category=template.category,
        description=template.description,
        version=template.version,
        author=template.author,
        template_config=template.template_config,
        os_type=template.os_type
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get(\"/application-templates\", response_model=List[ApplicationTemplateResponse])
def list_application_templates(
    category: Optional[str] = None,
    os_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    \"\"\"Получить список шаблонов приложений\"\"\"
    query = db.query(ApplicationTemplate).filter(ApplicationTemplate.is_active == True)
    
    if category:
        query = query.filter(ApplicationTemplate.category == category)
    if os_type:
        query = query.filter(ApplicationTemplate.os_type == os_type)
    
    templates = query.offset(skip).limit(limit).all()
    return templates

@router.get(\"/application-templates/{template_id}\", response_model=ApplicationTemplateResponse)
def get_application_template(template_id: int, db: Session = Depends(get_db)):
    \"\"\"Получить шаблон приложения по ID\"\"\"
    template = db.query(ApplicationTemplate).filter(
        ApplicationTemplate.id == template_id,
        ApplicationTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail=\"Template not found\")
    return template

@router.put(\"/application-templates/{template_id}\", response_model=ApplicationTemplateResponse)
def update_application_template(
    template_id: int, 
    template_update: ApplicationTemplateUpdate, 
    db: Session = Depends(get_db)
):
    \"\"\"Обновить шаблон приложения\"\"\"
    template = db.query(ApplicationTemplate).filter(
        ApplicationTemplate.id == template_id,
        ApplicationTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail=\"Template not found\")
    
    # Проверяем уникальность имени если оно изменяется
    if template_update.name and template_update.name != template.name:
        existing = db.query(ApplicationTemplate).filter(
            ApplicationTemplate.name == template_update.name,
            ApplicationTemplate.is_active == True,
            ApplicationTemplate.id != template_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=\"Template name already exists\")
    
    # Обновляем поля
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template

@router.delete(\"/application-templates/{template_id}\")
def delete_application_template(template_id: int, db: Session = Depends(get_db)):
    \"\"\"Удалить шаблон приложения (мягкое удаление)\"\"\"
    template = db.query(ApplicationTemplate).filter(
        ApplicationTemplate.id == template_id,
        ApplicationTemplate.is_active == True
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail=\"Template not found\")
    
    template.is_active = False
    db.commit()
    return {\"message\": f\"Template '{template.name}' deleted successfully\"}

@router.get(\"/application-templates/categories\")
def get_template_categories(db: Session = Depends(get_db)):
    \"\"\"Получить список всех категорий шаблонов\"\"\"
    categories = db.query(ApplicationTemplate.category).filter(
        ApplicationTemplate.is_active == True,
        ApplicationTemplate.category.isnot(None)
    ).distinct().all()
    
    return {\"categories\": [cat[0] for cat in categories if cat[0]]}
