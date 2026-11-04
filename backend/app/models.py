import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class ScanStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    allowed_domains: Mapped[list] = mapped_column(JSON, default=list)
    max_pages: Mapped[int] = mapped_column(Integer, default=5)
    schedule_cron: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    scans: Mapped[list["Scan"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    status: Mapped[ScanStatus] = mapped_column(Enum(ScanStatus), default=ScanStatus.queued)
    source: Mapped[str] = mapped_column(String(40), default="manual")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    project: Mapped[Project] = relationship(back_populates="scans")
    findings: Mapped[list["Finding"]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"))
    category: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(255))
    detail: Mapped[str] = mapped_column(Text)
    remediation: Mapped[str] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    selector: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    scan: Mapped[Scan] = relationship(back_populates="findings")
