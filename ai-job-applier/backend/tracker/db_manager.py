from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./jobs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    platform = Column(String)
    url = Column(String)
    description = Column(Text)
    salary = Column(String, nullable=True)
    location = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    job_title = Column(String)
    company = Column(String)
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, applied, rejected, interview
    tailored_resume_path = Column(String, nullable=True)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database operations
def add_job(db, job_data):
    """Add a new job to database"""
    db_job = Job(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db, platform=None):
    """Get jobs from database"""
    query = db.query(Job)
    if platform:
        query = query.filter(Job.platform == platform)
    return query.all()

def add_application(db, app_data):
    """Record a job application"""
    db_app = Application(**app_data)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

def get_applications(db, status=None):
    """Get applications"""
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    return query.all()

def update_application_status(db, app_id, status):
    """Update application status"""
    app = db.query(Application).filter(Application.id == app_id).first()
    if app:
        app.status = status
        db.commit()
    return app
