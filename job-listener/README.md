# Job Listener

This repository contains a LinkedIn job automation project with a React dashboard and a Playwright backend.

## Project structure

- `frontend/`: React + Vite dashboard
  - Lists scraped jobs
  - Lets you select jobs with checkboxes
  - Sends selected jobs to the backend for Easy Apply automation
- `automation/`: Express + Playwright backend
  - Scrapes LinkedIn jobs filtered for Easy Apply
  - Exposes `GET /jobs`
  - Exposes `POST /apply`

## Setup

### Frontend

```bash
cd job-listener/frontend
npm install
npm run dev
```

Open the front-end app in your browser at the Vite URL shown in the terminal.

### Automation backend

```bash
cd job-listener/automation
npm install
npm run open-profile
npm start
```

- `npm run open-profile` opens LinkedIn in a browser so you can log in once and save the profile state.
- `npm start` starts the backend server on `http://localhost:4000`.

## API

### GET /jobs

Fetches Easy Apply jobs from LinkedIn and returns JSON:

```json
{ "success": true, "count": 10, "jobs": [ ... ] }
```

### POST /apply

Sends selected jobs for automation. The request body should include:

```json
{ "jobs": [ ... ], "userDetails": { ... } }
```

## Notes

- The scraper currently uses LinkedIn's Easy Apply filter.
- Only jobs selected in the frontend are sent to the apply endpoint.
- Resume file handling is configured by the automation backend.
