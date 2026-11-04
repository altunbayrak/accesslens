from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    allowed_domains: list[str] = Field(min_length=1)
    max_pages: int = Field(default=5, ge=1, le=50)
    schedule_cron: str | None = Field(default=None, max_length=100)

    @field_validator("allowed_domains")
    @classmethod
    def normalize_domains(cls, values):
        return [v.lower().strip().removeprefix("https://").removeprefix("http://").split("/")[0] for v in values]


class ProjectOut(ProjectCreate):
    id: int
    created_at: datetime
    class Config: from_attributes = True


class ScanCreate(BaseModel):
    source: str = Field(default="manual", max_length=40)


class FindingOut(BaseModel):
    id: int; category: str; severity: str; title: str; detail: str; remediation: str
    url: str | None; selector: str | None; evidence: dict
    class Config: from_attributes = True


class ScanOut(BaseModel):
    id: int; project_id: int; status: str; source: str; started_at: datetime | None; completed_at: datetime | None
    summary: dict; error: str | None; findings: list[FindingOut] = []
    class Config: from_attributes = True
