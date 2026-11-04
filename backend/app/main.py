from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from .config import settings
from .database import Base, engine, get_db
from .models import Project, Scan
from .schemas import ProjectCreate, ProjectOut, ScanCreate, ScanOut
from .scanner import scan_project


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AccessLens API", version="0.1.0", description="Authorized, passive web quality audits.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["*"], allow_headers=["*"], allow_credentials=True)


@app.get("/health")
def health(): return {"status": "ok", "version": settings.app_version, "demo_mode": settings.demo_mode}


@app.post("/api/v1/projects", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump()); db.add(project); db.commit(); db.refresh(project); return project


@app.get("/api/v1/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)): return db.query(Project).order_by(Project.id.desc()).all()


@app.get("/api/v1/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project: raise HTTPException(404, "Project not found")
    return project


@app.post("/api/v1/projects/{project_id}/scans", response_model=ScanOut, status_code=202)
def create_scan(project_id: int, payload: ScanCreate, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project: raise HTTPException(404, "Project not found")
    scan = Scan(project_id=project.id, source=payload.source); db.add(scan); db.commit(); db.refresh(scan)
    tasks.add_task(_run_scan, scan.id); return scan


def _run_scan(scan_id: int):
    from .database import SessionLocal
    db = SessionLocal()
    try:
        scan = db.query(Scan).options(joinedload(Scan.project)).get(scan_id)
        if scan: scan_project(db, scan)
    finally: db.close()


@app.get("/api/v1/projects/{project_id}/scans", response_model=list[ScanOut])
def list_scans(project_id: int, db: Session = Depends(get_db)):
    return db.query(Scan).options(joinedload(Scan.findings)).filter(Scan.project_id == project_id).order_by(Scan.id.desc()).all()


@app.get("/api/v1/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).options(joinedload(Scan.findings)).filter(Scan.id == scan_id).first()
    if not scan: raise HTTPException(404, "Scan not found")
    return scan


@app.get("/api/v1/scans/{scan_id}/export")
def export_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = get_scan(scan_id, db)
    return ScanOut.model_validate(scan).model_dump(mode="json")
