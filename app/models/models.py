from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, JSON, Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class ApplicationTemplate(Base):
    __tablename__ = 'applications_template'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(150))
    category = Column(String(50))
    description = Column(Text)
    version = Column(String(20), default='1.0')
    author = Column(String(100))
    template_config = Column(JSON, nullable=False)
    os_type = Column(String(20), nullable=False, default='linux')
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default='offline')
    os_type = Column(String(20), nullable=False)
    config = Column(JSON)
    last_seen = Column(TIMESTAMP)
    last_activity = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class AgentActivity(Base):
    __tablename__ = 'agent_activities'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    activity_type = Column(String(50))
    activity_data = Column(JSON)
    timestamp = Column(TIMESTAMP, server_default=func.now())
