from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.deps import get_db
from app.models.models import Servers
from app.schemas import ServerTemplate

router = APIRouter()

@router.get("/servers/{ip}", response_model=ServerTemplate)
def get_server_by_ip(ip: int, db: Session = Depends(get_db)):
    server = db.query(Servers).filter(Servers.ip == ip).first()
    if not server:
        raise HTTPException(status_code=404, detail="server not found")
    return server

@router.get("/servers", response_model=List[ServerTemplate])
def get_all_servers(db: Session = Depends(get_db)):
    servers = db.query(Servers).all()
    return servers

@router.post("/servers", response_model=ServerTemplate)
def create_server(server: ServerTemplate, db: Session = Depends(get_db)):
    existing = db.query(Servers).filter(Servers.name == server.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already Exists")
    new_server = Servers(
        name=server.name,
        description=server.description,
        ip=server.ip,
        login=server.login,
        password=server.password,
        os=server.os
    )
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    return new_server


