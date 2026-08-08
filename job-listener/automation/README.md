# Playwright Automation Backend

This folder provides a small Express API that uses Playwright to scrape LinkedIn job listings and return them as JSON.

Setup

1. Install dependencies:

```bash
cd job-listener/automation
npm install
```

2. Open a browser and login to LinkedIn (only needed once):

```bash
npm run open-profile
```

The command opens a Chromium window using a local profile directory. Sign in to LinkedIn in that window, then press Enter in the terminal to save the profile.

3. Start the backend server:

```bash
npm start
```

4. Query the jobs endpoint from your frontend (example):

GET http://localhost:4000/jobs?q=full%20stack%20developer

Notes

- By default the service uses a persistent Playwright profile directory at `~/.linkedin_playwright_profile`. Set `USER_DATA_DIR` to change it.
- The scraper uses a LinkedIn search URL with a "past 24 hours" filter. LinkedIn's DOM may change; selectors are heuristics and may require adjustments.
