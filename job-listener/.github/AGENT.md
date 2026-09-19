# GitHub Agent — Repository Instructions

Purpose
- Document the repository agent responsibilities and quick run instructions.

Agent responsibilities
- Run quick checks and CI jobs (lint/tests) if added.
- Run the LinkedIn scraper (`automation/scrape.js`) to gather Easy Apply jobs.
- Run the apply automation (`automation/apply.js`) when explicitly requested by maintainers.
- Provide reproducible local run steps for maintainers.

Safety & policy
- Do not store secrets in the repository. Use GitHub Secrets for any credentials required by automation.
- Automatic applications to job sites may violate terms of service; only run `apply` flows manually and with an authenticated browser profile that you control.

Local run (developer)
1. Start the backend (login once to save profile state):

```powershell
cd job-listener/automation
npm install
npm run open-profile   # opens browser to log into LinkedIn and save profile
npm start
```

2. Start the frontend dashboard:

```bash
cd job-listener/frontend
npm install
npm run dev
```

3. Open the frontend URL shown by Vite and use the dashboard to fetch jobs and trigger "Apply Selected Jobs".

API
- GET `http://localhost:4000/jobs` — returns Easy Apply jobs (JSON)
- POST `http://localhost:4000/apply` — accepts `{ jobs, userDetails }` JSON to run automation

GitHub Actions guidance
- If you add workflows under `.github/workflows/`, keep automation jobs manual or protected (require approvals) and never embed credentials directly.
- Example job names: `check`, `scrape`, `manual-apply`

Maintainers
- Primary: Prashant Pathak
- Repo root: `job-listener/`

If you want, I can also add a suggested workflow file under `.github/workflows/` that runs a non-destructive `scrape` job on demand.
