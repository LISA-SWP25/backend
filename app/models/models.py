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
    
    # Relationships
    agents = relationship("Agent", back_populates="role")
    behavior_templates = relationship("BehaviorTemplate", back_populates="role")

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

class BehaviorTemplate(Base):
    __tablename__ = 'behavior_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    os_type = Column(String(20), nullable=False, default='linux')
    template_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # NEW: Added role_id foreign key from migration script
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    agents = relationship("Agent", back_populates="template")
    role = relationship("Role", back_populates="behavior_templates")

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
    injection_target = Column(String(200))
    stealth_level = Column(Integer, default=1)
    
    # Foreign keys
    role_id = Column(Integer, ForeignKey('roles.id'))
    template_id = Column(Integer, ForeignKey('behavior_templates.id'))
    
    version_info = Column(JSON, default=lambda: {})
    build_time = Column(Integer)  # build time in seconds
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    role = relationship("Role", back_populates="agents")
    template = relationship("BehaviorTemplate", back_populates="agents")
    activities = relationship("AgentActivity", back_populates="agent")
    builds = relationship("AgentBuild", back_populates="agent")

class AgentBuild(Base):
    __tablename__ = 'agent_builds'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    build_config = Column(JSON, nullable=False)
    build_status = Column(String(50), nullable=False, default='pending')  # pending, building, completed, failed
    binary_path = Column(Text)
    binary_size = Column(Integer)
    build_log = Column(Text)
    build_time = Column(Integer)  # build time in seconds
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    completed_at = Column(TIMESTAMP)
    
    # Relationships
    agent = relationship("Agent", back_populates="builds")

class AgentUpdateLog(Base):
    """NEW: Agent update logs table from migration script"""
    __tablename__ = 'agent_update_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, nullable=False)
    user_id = Column(Text, nullable=False)
    old_version = Column(Text)
    new_version = Column(Text)
    update_status = Column(String(50), nullable=False)  # 'started', 'completed', 'failed'
    update_log = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class AgentActivity(Base):
    __tablename__ = 'agent_activities'
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    activity_type = Column(String(50))
    activity_data = Column(JSON)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="activities")
