#!/usr/bin/env python3
"""
Demo script showing the AI Job Application Pipeline in action

This script demonstrates:
1. Job scraping from Indeed
2. Resume tailoring for a sample job
3. Application data preparation
4. Database tracking
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from scraper.indeed_scraper import IndeedScraper
from ai_tailor.resume_tailor import ResumeTailor
from tracker.db_manager import init_db, get_db, add_job
from job_application_pipeline import JobApplicationPipeline


def demo_job_scraping():
    """Demo: Scrape jobs from Indeed"""
    print("🔍 Demo: Job Scraping")
    print("-" * 40)

    scraper = IndeedScraper()
    jobs = scraper.search_jobs(
        keywords="Python Developer",
        location="Remote",
        num_results=3
    )

    print(f"Found {len(jobs)} jobs:")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} at {job['company']} - {job['location']}")
        print(f"   URL: {job['url']}")
        print(f"   Salary: {job.get('salary', 'Not specified')}")
        print()

    return jobs


def demo_resume_tailoring():
    """Demo: AI Resume Tailoring"""
    print("🤖 Demo: AI Resume Tailoring")
    print("-" * 40)

    # Sample resume and job description
    sample_resume = """
    John Doe
    Python Developer with 3 years experience

    Skills: Python, Django, Flask, SQL, Git
    Experience: Software Engineer at TechCorp (2021-Present)
    - Built web applications using Python and Django
    - Worked with SQL databases
    - Used Git for version control
    """

    sample_job_desc = """
    Senior Python Developer
    Requirements:
    - 3+ years Python experience
    - Django/Flask framework experience
    - SQL database knowledge
    - REST API development
    - Git version control
    - Experience with AWS
    """

    tailor = ResumeTailor()

    # Calculate match score
    score = tailor.score_match(sample_resume, sample_job_desc)
    print(f"Match Score: {score:.1f}%")

    # Extract keywords
    keywords = tailor.extract_keywords(sample_job_desc)
    print(f"Key Skills: {', '.join(keywords)}")

    # Tailor resume (would use AI in production)
    tailored = tailor.tailor_resume(sample_resume, sample_job_desc)
    print(f"\nTailored Resume Preview:\n{tailored[:200]}...")
    print()


def demo_database_tracking():
    """Demo: Database Tracking"""
    print("💾 Demo: Database Tracking")
    print("-" * 40)

    # Initialize database
    init_db()

    # Add sample jobs
    db = next(get_db())

    sample_jobs = [
        {
            'job_id': 'demo_1',
            'title': 'Python Developer',
            'company': 'TechCorp',
            'platform': 'indeed',
            'url': 'https://example.com/job1',
            'description': 'Python development role',
            'salary': '$80k-100k',
            'location': 'Remote',
            'scraped_at': '2024-01-01T00:00:00Z'
        },
        {
            'job_id': 'demo_2',
            'title': 'Senior Python Engineer',
            'company': 'DataTech',
            'platform': 'naukri',
            'url': 'https://example.com/job2',
            'description': 'Senior Python role with ML experience',
            'salary': '$100k-120k',
            'location': 'San Francisco',
            'scraped_at': '2024-01-01T00:00:00Z'
        }
    ]

    for job_data in sample_jobs:
        add_job(db, job_data)

    print("Added sample jobs to database")
    print()


def demo_pipeline_orchestration():
    """Demo: Pipeline Orchestration"""
    print("🔄 Demo: Pipeline Orchestration")
    print("-" * 40)

    print("The JobApplicationPipeline class coordinates all components:")
    print("1. Initializes all modules (scrapers, AI tailor, automation, etc.)")
    print("2. Runs job scraping across multiple platforms")
    print("3. Prioritizes jobs based on match scores")
    print("4. Tailors resumes for each job using AI")
    print("5. Auto-applies to selected jobs")
    print("6. Tracks applications in database")
    print("7. Sends email notifications")
    print()

    # Show pipeline structure
    pipeline = JobApplicationPipeline()
    print("Pipeline initialized with:")
    print(f"- {len(pipeline.scrapers)} job scrapers")
    print("- AI resume tailor")
    print("- Form automation (Selenium)")
    print("- Database tracker")
    print("- Email notifier")
    print()


def main():
    """Run all demos"""
    print("🚀 AI Job Applier - Demo Suite")
    print("=" * 50)
    print()

    try:
        demo_job_scraping()
        demo_resume_tailoring()
        demo_database_tracking()
        demo_pipeline_orchestration()

        print("✅ All demos completed successfully!")
        print()
        print("To run the full pipeline:")
        print("python cli.py --keywords 'Python Developer' --location 'Remote' --max 3")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()