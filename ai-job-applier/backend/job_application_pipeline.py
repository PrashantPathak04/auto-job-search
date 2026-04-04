"""
AI Job Application Pipeline

This module orchestrates the entire job application process:
1. Scrape jobs from multiple platforms
2. Tailor resume for each job using AI
3. Auto-apply to jobs
4. Track applications in database
5. Send notifications

Usage:
    from job_application_pipeline import JobApplicationPipeline

    pipeline = JobApplicationPipeline()
    pipeline.run_pipeline(
        keywords="Python Developer",
        location="San Francisco",
        max_applications=5
    )
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import os

from scraper.linkedin_scraper import LinkedInScraper
from scraper.indeed_scraper import IndeedScraper
from scraper.naukri_scraper import NaukriScraper
from ai_tailor.resume_tailor import ResumeTailor
from automation.form_submitter import FormSubmitter
from tracker.db_manager import get_db, add_job, add_application, get_jobs
from notifier.alerts import AlertNotifier


class JobApplicationPipeline:
    def __init__(self):
        """Initialize all pipeline components"""
        self.scrapers = {
            'linkedin': LinkedInScraper(),
            'indeed': IndeedScraper(),
            'naukri': NaukriScraper()
        }

        self.resume_tailor = ResumeTailor()
        self.form_submitter = FormSubmitter(headless=True)  # Run in background
        self.notifier = AlertNotifier()

        # User profile data (would be loaded from config/database)
        self.user_profile = {
            'first_name': os.getenv('USER_FIRST_NAME', 'John'),
            'last_name': os.getenv('USER_LAST_NAME', 'Doe'),
            'email': os.getenv('USER_EMAIL', 'john.doe@example.com'),
            'phone': os.getenv('USER_PHONE', '+1-555-0123'),
            'resume_path': os.getenv('USER_RESUME_PATH', 'resume.pdf'),
            'base_resume': self._load_base_resume()
        }

    def _load_base_resume(self) -> str:
        """Load base resume content from file"""
        resume_path = os.getenv('USER_RESUME_PATH', 'resume.txt')
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Resume file not found at {resume_path}")
            return "Default resume content - please update with your actual resume"

    async def run_pipeline(self, keywords: str, location: str = "", max_applications: int = 10):
        """
        Run the complete job application pipeline

        Args:
            keywords: Job search keywords (e.g., "Python Developer")
            location: Location filter
            max_applications: Maximum number of applications to submit
        """
        print("🚀 Starting AI Job Application Pipeline")
        print(f"🔍 Searching for: {keywords} in {location or 'any location'}")

        # Step 1: Scrape jobs from all platforms
        all_jobs = await self._scrape_jobs(keywords, location)
        print(f"📊 Found {len(all_jobs)} total jobs across platforms")

        # Step 2: Filter and prioritize jobs
        prioritized_jobs = self._prioritize_jobs(all_jobs, max_applications)
        print(f"🎯 Selected {len(prioritized_jobs)} jobs to apply for")

        # Step 3: Apply to each job
        applications_submitted = 0
        for job in prioritized_jobs:
            try:
                success = await self._apply_to_job(job)
                if success:
                    applications_submitted += 1
                    print(f"✅ Applied to: {job['title']} at {job['company']}")
                else:
                    print(f"❌ Failed to apply to: {job['title']} at {job['company']}")
            except Exception as e:
                print(f"⚠️ Error applying to {job['title']}: {e}")

        # Step 4: Send summary notification
        await self._send_summary_notification(applications_submitted, len(prioritized_jobs))

        print("🎉 Pipeline completed!"        print(f"📈 Successfully applied to {applications_submitted}/{len(prioritized_jobs)} jobs")

    async def _scrape_jobs(self, keywords: str, location: str) -> List[Dict]:
        """Scrape jobs from all configured platforms"""
        all_jobs = []

        for platform, scraper in self.scrapers.items():
            try:
                print(f"🔍 Scraping {platform}...")
                jobs = scraper.search_jobs(keywords, location, num_results=25)
                for job in jobs:
                    job['platform'] = platform
                    job['scraped_at'] = datetime.utcnow()
                all_jobs.extend(jobs)
                print(f"   Found {len(jobs)} jobs on {platform}")
            except Exception as e:
                print(f"⚠️ Error scraping {platform}: {e}")

        return all_jobs

    def _prioritize_jobs(self, jobs: List[Dict], max_count: int) -> List[Dict]:
        """Prioritize jobs based on match score and other criteria"""
        scored_jobs = []

        for job in jobs:
            # Calculate match score
            match_score = self.resume_tailor.score_match(
                self.user_profile['base_resume'],
                job.get('description', '')
            )

            job['match_score'] = match_score
            scored_jobs.append(job)

        # Sort by match score (highest first) and take top N
        scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_jobs[:max_count]

    async def _apply_to_job(self, job: Dict) -> bool:
        """Apply to a single job"""
        try:
            # Step 1: Tailor resume for this job
            tailored_resume = self.resume_tailor.tailor_resume(
                self.user_profile['base_resume'],
                job.get('description', '')
            )

            # Save tailored resume (in production, save to file)
            tailored_resume_path = f"tailored_resume_{job['job_id'] or 'temp'}.pdf"

            # Step 2: Prepare application data
            application_data = {
                'first_name': self.user_profile['first_name'],
                'last_name': self.user_profile['last_name'],
                'email': self.user_profile['email'],
                'phone': self.user_profile['phone'],
                'resume_path': self.user_profile['resume_path'],  # Use original resume
                'cover_letter': self._generate_cover_letter(job, tailored_resume)
            }

            # Step 3: Submit application
            success = self.form_submitter.apply_to_job(job['url'], application_data)

            if success:
                # Step 4: Record in database
                db = next(get_db())
                add_application(db, {
                    'job_id': job.get('job_id', ''),
                    'job_title': job['title'],
                    'company': job['company'],
                    'applied_at': datetime.utcnow(),
                    'status': 'applied',
                    'tailored_resume_path': tailored_resume_path
                })

                # Step 5: Send notification
                self.notifier.send_application_alert(
                    self.user_profile['email'],
                    job['title'],
                    job['company'],
                    job['url']
                )

            return success

        except Exception as e:
            print(f"Error applying to job: {e}")
            return False

    def _generate_cover_letter(self, job: Dict, tailored_resume: str) -> str:
        """Generate a cover letter for the job"""
        # Simple template - in production, use AI to generate
        cover_letter = f"""
        Dear Hiring Manager,

        I am excited to apply for the {job['title']} position at {job['company']}.
        With my background in software development, I am confident I can contribute
        effectively to your team.

        My experience aligns well with the requirements mentioned in your job posting,
        particularly in areas such as {', '.join(self.resume_tailor.extract_keywords(job.get('description', ''))[:3])}.

        I would welcome the opportunity to discuss how my skills and experience
        can benefit {job['company']}.

        Best regards,
        {self.user_profile['first_name']} {self.user_profile['last_name']}
        """

        return cover_letter.strip()

    async def _send_summary_notification(self, submitted: int, total: int):
        """Send daily summary notification"""
        # Get today's applications from database
        db = next(get_db())
        today_applications = []  # Would query database for today's applications

        self.notifier.send_daily_summary(
            self.user_profile['email'],
            today_applications
        )

    def cleanup(self):
        """Clean up resources"""
        self.form_submitter.close()


# Example usage
if __name__ == "__main__":
    async def main():
        pipeline = JobApplicationPipeline()

        try:
            await pipeline.run_pipeline(
                keywords="Python Developer",
                location="Remote",
                max_applications=3
            )
        finally:
            pipeline.cleanup()

    asyncio.run(main())