from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Float, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from apps.api.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="RESEARCHER")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    researcher_profile = relationship("ResearcherProfile", back_populates="user", uselist=False)
    projects = relationship("Project", back_populates="user")
    memories = relationship("Memory", back_populates="user")
    sources = relationship("Source", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    skills = relationship("Skill", back_populates="user")


class ResearcherProfile(Base):
    __tablename__ = "researcher_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    interests = Column(JSONB, default=[])
    skills = Column(JSONB, default=[])
    projects = Column(JSONB, default=[])
    publications = Column(JSONB, default=[])
    research_goals = Column(JSONB, default=[])
    preferred_sources = Column(JSONB, default=[])
    preferred_models = Column(JSONB, default=[])
    preferred_languages = Column(JSONB, default=[])
    privacy_preferences = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="researcher_profile")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    memories = relationship("Memory", back_populates="project")


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(2000))
    source_type = Column(String(50), nullable=False)
    author = Column(String(500))
    doi = Column(String(255))
    publisher = Column(String(255))
    published_at = Column(DateTime)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    content_hash = Column(String(64))
    quality_score = Column(Float, default=0.0)
    visibility = Column(String(50), default="PRIVATE")
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sources")
    documents = relationship("Document", back_populates="source")
    memories = relationship("Memory", back_populates="source")
    feedback = relationship("Feedback", back_populates="source")

    __table_args__ = (
        Index("ix_sources_user_id_type", "user_id", "source_type"),
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    content = Column(Text)
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, default={})
    embedding_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    embedding_id = Column(String(255))
    confidence = Column(Float, default=0.0)
    importance = Column(Float, default=0.0)
    source_reference = Column(String(500))
    user_verified = Column(Boolean, default=False)
    visibility = Column(String(50), default="PRIVATE")
    metadata_ = Column("metadata", JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="memories")
    project = relationship("Project", back_populates="memories")
    source = relationship("Source", back_populates="memories")
    feedback = relationship("Feedback", back_populates="memory")

    __table_args__ = (
        Index("ix_memories_user_id_type", "user_id", "type"),
        Index("ix_memories_user_id_project", "user_id", "project_id"),
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id"))
    action = Column(String(50), nullable=False)
    context = Column(JSONB, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedback")
    source = relationship("Source", back_populates="feedback")
    memory = relationship("Memory", back_populates="feedback")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    input_schema = Column(JSONB, default={})
    steps = Column(JSONB, default=[])
    output_schema = Column(JSONB, default={})
    permissions = Column(JSONB, default={})
    is_builtin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="skills")
    runs = relationship("SkillRun", back_populates="skill")


class SkillRun(Base):
    __tablename__ = "skill_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    input_data = Column(JSONB, default={})
    output_data = Column(JSONB, default={})
    status = Column(String(50), default="pending")
    error = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    skill = relationship("Skill", back_populates="runs")


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    server_url = Column(String(2000), nullable=False)
    authentication = Column(JSONB, default={})
    tools = Column(JSONB, default=[])
    resources = Column(JSONB, default=[])
    permissions = Column(JSONB, default={})
    timeout = Column(Integer, default=30)
    environment = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(2000), nullable=False)
    events = Column(JSONB, default=[])
    secret = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    model = Column(String(255), nullable=False)
    endpoint = Column(String(2000))
    api_key = Column(String(255))
    parameters = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    provider = Column(String(100))
    model = Column(String(255))
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    metadata_ = Column("metadata", JSONB, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)


class EnergyEvent(Base):
    __tablename__ = "energy_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    mode = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    details = Column(JSONB, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSONB, default={})
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
