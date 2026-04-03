from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize database
from tracker.db_manager import init_db
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application started")
    yield
    # Shutdown
    print("Application shutdown")

app = FastAPI(title="AI Job Applier", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    return {"message": "AI Job Applier API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/scrape-jobs")
async def scrape_jobs(platform: str = "linkedin", keywords: str = "python developer"):
    """Scrape jobs from specified platform"""
    return {"message": f"Scraping jobs for: {keywords} on {platform}"}

@app.post("/apply-jobs")
async def apply_jobs(job_ids: list):
    """Auto-apply to specified jobs"""
    return {"message": f"Applying to {len(job_ids)} jobs"}

@app.get("/applications")
async def get_applications():
    """Get list of all applications"""
    return {"applications": []}

@app.get("/jobs")
async def get_jobs(platform: str = None):
    """Get scraped jobs"""
    return {"jobs": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
