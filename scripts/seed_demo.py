"""Create a harmless local demo project; never seed targets without user authorization."""
from app.database import Base, SessionLocal, engine
from app.models import Project
Base.metadata.create_all(bind=engine); db = SessionLocal()
if not db.query(Project).filter_by(name="Example authorized site").first():
    db.add(Project(name="Example authorized site", allowed_domains=["example.com"], max_pages=3)); db.commit()
print("Demo project ready")
