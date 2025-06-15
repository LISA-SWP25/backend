from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, JSON, Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    behavior_templates = relationship("BehaviorTemplate", back_populates="role")
    agents = relationship("Agent", back_populates="role")

class BehaviorTemplate(Base):
    __tablename__ = "behavior_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    template_data = Column(JSON, nullable=False)
    os_type = Column(String(20), nullable=False)
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    role = relationship("Role", back_populates="behavior_templates")
    agents = relationship("Agent", back_populates="template")

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    template_id = Column(Integer, ForeignKey("behavior_templates.id"))
    status = Column(String(20), default="offline")
    os_type = Column(String(20), nullable=False)
    config = Column(JSON)
    injection_target = Column(String(100))
    stealth_level = Column(String(20), default="medium")
    last_seen = Column(TIMESTAMP)
    last_activity = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    role = relationship("Role", back_populates="agents")
    template = relationship("BehaviorTemplate", back_populates="agents")
    activities = relationship("AgentActivity", back_populates="agent")
    builds = relationship("AgentBuild", back_populates="agent")

class AgentActivity(Base):
    __tablename__ = "agent_activities"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    activity_type = Column(String(50))
    activity_data = Column(JSON)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    agent = relationship("Agent", back_populates="activities")

class AgentBuild(Base):
    __tablename__ = "agent_builds"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    build_config = Column(JSON, nullable=False)
    binary_path = Column(String(255))
    binary_size = Column(Integer)
    build_status = Column(String(20), default="pending")
    build_log = Column(Text)
    build_time = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)
    
    agent = relationship("Agent", back_populates="builds")
