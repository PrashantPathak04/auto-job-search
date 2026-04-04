# AI Job Applier

An intelligent job application automation system that scrapes job postings, tailors resumes using AI, and automatically submits applications across multiple job platforms.

## Features

- **Job Scraping**: Automatically scrape job postings from LinkedIn, Indeed, and Naukri
- **AI Resume Tailoring**: Use AI to customize resumes for each job based on job description keywords
- **Automated Form Submission**: Automatically fill and submit job application forms
- **Application Tracking**: Keep detailed records of all submitted applications
- **Smart Matching**: Score resumes against job descriptions to identify best matches
- **Email Notifications**: Receive alerts for each successful application and daily summaries
- **REST API**: FastAPI backend for easy integration and management

## Project Structure

```
ai-job-applier/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── scraper/
│   │   ├── linkedin_scraper.py
│   │   ├── indeed_scraper.py
│   │   └── naukri_scraper.py
│   ├── ai_tailor/
│   │   └── resume_tailor.py    # AI-powered resume customization
│   ├── automation/
│   │   └── form_submitter.py   # Automated form filling
│   ├── tracker/
│   │   └── db_manager.py       # SQLite database management
│   └── notifier/
│       └── alerts.py           # Email notifications
├── frontend/
│   └── react-dashboard/        # React monitoring dashboard
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Google Chrome (for Selenium automation)
- OpenAI API key (for resume tailoring)
- Gmail account with app password (for email alerts)

### 1. Clone and Setup

```bash
cd ai-job-applier/backend
python -m venv venv
# On Windows:
venv\Scripts\Activate.ps1
# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials:
# - OpenAI API key
# - Gmail SMTP credentials
# - Database URL
```

### 4. Initialize Database

```bash
python -c "from tracker.db_manager import init_db; init_db()"
```

### 5. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Job Scraping
- `POST /scrape-jobs` - Scrape jobs from a platform
  ```json
  {
    "platform": "indeed",
    "keywords": "python developer",
    "location": "San Francisco"
  }
  ```

### Job Applications
- `GET /jobs` - List all scraped jobs
- `POST /apply-jobs` - Submit applications to selected jobs
  ```json
  {
    "job_ids": [1, 2, 3]
  }
  ```

### Tracking
- `GET /applications` - View all submitted applications
- `GET /health` - Health check endpoint

## Pipeline Architecture

The system follows a modular pipeline architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Job Scraping  │ -> │  AI Resume       │ -> │  Auto Apply     │
│   (Indeed,      │    │  Tailoring       │    │  (Selenium)     │
│    Naukri,      │    │  (OpenAI/Ollama) │    │                 │
│    LinkedIn)    │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         v                       v                       v
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │    │   Notifications  │    │   Dashboard     │
│   Tracking      │    │   (Email/SMS)    │    │   (React)       │
│   (SQLite)      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

1. **Job Scrapers** (`scraper/`)
   - `indeed_scraper.py`: Scrapes Indeed.com
   - `naukri_scraper.py`: Scrapes Naukri.com
   - `linkedin_scraper.py`: LinkedIn scraper (requires API)

2. **AI Resume Tailor** (`ai_tailor/`)
   - Analyzes job descriptions
   - Tailors resume content using AI
   - Generates cover letters

3. **Application Automation** (`automation/`)
   - Selenium-based form filling
   - Document uploads
   - Application submission

4. **Database Tracker** (`tracker/`)
   - SQLite database for persistence
   - Application status tracking
   - Job history

5. **Notification System** (`notifier/`)
   - Email alerts for applications
   - Daily summary reports
   - Interview notifications

6. **Pipeline Orchestrator** (`job_application_pipeline.py`)
   - Coordinates all components
   - Handles error recovery
   - Manages application limits

## Quick Start

### Command Line Interface

```bash
# Apply to 5 Python Developer jobs
python cli.py --keywords "Python Developer" --location "Remote" --max 5

# Just scrape jobs without applying
python cli.py --scrape-only --keywords "Data Scientist"

# Check application status
python cli.py --status
```

### Direct Python Script

```python
from job_application_pipeline import JobApplicationPipeline
import asyncio

pipeline = JobApplicationPipeline()
asyncio.run(pipeline.run_pipeline(
    keywords="Python Developer",
    location="San Francisco",
    max_applications=3
))
pipeline.cleanup()
```

### Run Demo

```bash
python demo.py
```

This will show how each component works without actually applying to jobs.

## Usage Examples

### 1. Scrape Jobs from Indeed
```python
from scraper.indeed_scraper import IndeedScraper

scraper = IndeedScraper()
jobs = scraper.search_jobs(
    keywords="Python Developer",
    location="New York",
    num_results=25
)

for job in jobs:
    print(f"{job['title']} at {job['company']}")
```

### 2. Tailor Resume
```python
from ai_tailor.resume_tailor import ResumeTailor

tailor = ResumeTailor()
tailored = tailor.tailor_resume(
    base_resume=open("resume.txt").read(),
    job_description=job['description']
)

# Get match score
score = tailor.score_match(open("resume.txt").read(), job['description'])
print(f"Match Score: {score}%")
```

### 3. Auto-Apply to Jobs
```python
from automation.form_submitter import FormSubmitter

submitter = FormSubmitter()
success = submitter.apply_to_job(
    job_url="https://example.com/job/123",
    application_data={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+1-555-0000",
        "resume_path": "/path/to/resume.pdf",
        "cover_letter": "I am interested in this position..."
    }
)

submitter.close()
```

### 4. Email Notifications
```python
from notifier.alerts import AlertNotifier

notifier = AlertNotifier()
notifier.send_application_alert(
    recipient_email="user@example.com",
    job_title="Senior Python Developer",
    company="TechCorp",
    url="https://example.com/job/123"
)
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# AI and APIs
OPENAI_API_KEY=sk-...

# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_16_digit_app_password

# Database
DATABASE_URL=sqlite:///./jobs.db

# Server
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Gmail App Password Setup
1. Enable 2-Factor Authentication on your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Create an App Password for "Mail" and "Windows Computer"
4. Use this 16-character password as `SENDER_PASSWORD`

## Important Notes

- **LinkedIn Scraping**: LinkedIn has strong anti-scraping measures. Consider using LinkedIn's official API or li_at cookies with Selenium.
- **Ethics**: Always ensure applications are genuine and your information is accurate. Use this tool responsibly.
- **Rate Limiting**: Implement delays between requests to avoid being blocked by job sites.
- **Monitoring**: Regularly check the job applications dashboard to monitor status.

## Troubleshooting

### Chrome Driver Issues
```bash
pip install webdriver-manager
# Then update form_submitter.py to use:
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
```

### SMTP Email Issues
- Check Gmail allows "Less secure app access" or use App Passwords
- Verify firewall allows SMTP on port 587
- Check email credentials in `.env`

### Database Issues
```bash
# Reset database
rm jobs.db
python -c "from tracker.db_manager import init_db; init_db()"
```

## Frontend Setup

The React dashboard is available in `frontend/react-dashboard/`:

```bash
cd frontend/react-dashboard
npm install
npm start
```

This will display a dashboard to monitor job applications, view statistics, and manage settings.

## Future Enhancements

- [ ] LinkedIn API integration
- [ ] Advanced AI matching algorithms
- [ ] Support for more job platforms (FlexJobs, ZipRecruiter, etc.)
- [ ] Interview scheduling automation
- [ ] Performance analytics and reporting
- [ ] Mobile app for notifications
- [ ] Advanced filtering and saved searches

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Disclaimer

This tool is for educational purposes. Always ensure that your job applications are genuine and comply with the terms of service of each job platform. Do not use this tool to submit false information or engage in any deceptive practices.

## Support

For issues, questions, or contributions, please create an issue in the repository or contact the maintainers.

---

**Last Updated**: April 2026
**Version**: 1.0.0

