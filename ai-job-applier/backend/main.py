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
async def scrape_jobs(platform: str = "indeed", keywords: str = "python developer", location: str = "", limit: int = 25):
    """Scrape jobs from specified platform and store in database"""
    from tracker.db_manager import get_db, add_job
    from scraper.indeed_scraper import IndeedScraper
    from scraper.naukri_scraper import NaukriScraper
    from scraper.linkedin_scraper import LinkedInScraper
    from datetime import datetime

    # Select scraper based on platform
    scrapers = {
        "indeed": IndeedScraper(),
        "naukri": NaukriScraper(),
        "linkedin": LinkedInScraper()
    }

    if platform not in scrapers:
        return {"error": f"Platform '{platform}' not supported. Use: indeed, naukri, linkedin"}

    scraper = scrapers[platform]

    try:
        # Scrape jobs
        jobs = scraper.search_jobs(keywords, location, limit)

        # Store in database
        db = next(get_db())
        stored_count = 0

        for job in jobs:
            try:
                job_data = {
                    'job_id': job.get('job_id', f"{platform}_{hash(job.get('url', ''))}"),
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company', 'N/A'),
                    'platform': platform,
                    'url': job.get('url', ''),
                    'description': job.get('description', ''),
                    'salary': job.get('salary', 'Not specified'),
                    'location': job.get('location', ''),
                    'scraped_at': datetime.utcnow()
                }
                add_job(db, job_data)
                stored_count += 1
            except Exception as e:
                print(f"Error storing job: {e}")
                continue

        return {
            "message": f"Scraped {len(jobs)} jobs, stored {stored_count} new jobs",
            "platform": platform,
            "keywords": keywords,
            "location": location,
            "jobs_found": len(jobs),
            "jobs_stored": stored_count
        }

    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}"}

@app.post("/apply-jobs")
async def apply_jobs(job_ids: list):
    """Auto-apply to specified jobs"""
    return {"message": f"Applying to {len(job_ids)} jobs"}

@app.get("/applications")
async def get_applications(status: str = None, limit: int = 50):
    """Get list of all applications with optional status filtering"""
    from tracker.db_manager import get_db, get_applications as db_get_applications

    db = next(get_db())
    applications = db_get_applications(db, status)

    # Convert to dict format and limit results
    app_list = []
    for app in applications[:limit]:
        app_list.append({
            "id": app.id,
            "job_id": app.job_id,
            "job_title": app.job_title,
            "company": app.company,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None,
            "status": app.status,
            "tailored_resume_path": app.tailored_resume_path
        })

    return {"applications": app_list, "count": len(app_list)}

@app.get("/jobs")
async def get_jobs(platform: str = None, keywords: str = None, limit: int = 50):
    """Get scraped jobs with optional filtering"""
    from tracker.db_manager import get_db, get_jobs as db_get_jobs

    db = next(get_db())
    jobs = db_get_jobs(db, platform)

    # Filter by keywords if provided
    if keywords:
        keywords_lower = keywords.lower()
        filtered_jobs = []
        for job in jobs:
            # Search in title, company, and description
            searchable_text = f"{job.title} {job.company} {job.description or ''}".lower()
            if keywords_lower in searchable_text:
                filtered_jobs.append(job)
        jobs = filtered_jobs[:limit]
    else:
        jobs = jobs[:limit]

    # Convert to dict format
    job_list = []
    for job in jobs:
        job_list.append({
            "id": job.id,
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "platform": job.platform,
            "url": job.url,
            "description": job.description,
            "salary": job.salary,
            "location": job.location,
            "scraped_at": job.scraped_at.isoformat() if job.scraped_at else None
        })

    return {"jobs": job_list, "count": len(job_list)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
