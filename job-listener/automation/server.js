const express = require('express');
const path = require('path');
const os = require('os');
const { scrapeJobs } = require('./scrape');
const { applyToJobs } = require('./apply');

const app = express();
app.use(express.json());

// Minimal CORS for local development so the Vite frontend can fetch the API
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});
const PORT = process.env.PORT || 4000;

app.get('/jobs', async (req, res) => {
  const q = req.query.q || 'full stack developer';
  const days = Number(req.query.days) || 1;
  const USER_DATA_DIR = process.env.USER_DATA_DIR || path.join(os.homedir(), '.linkedin_playwright_profile');
  try {
    const jobs = await scrapeJobs(q, days, USER_DATA_DIR);
    res.json({ success: true, count: jobs.length, jobs });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/apply', (req, res) => {
  res.json({ success: false, error: 'Use POST /apply with JSON body { jobs, userDetails }' });
});

app.post('/apply', async (req, res) => {
  console.log('POST /apply received', { body: req.body });
  const { jobs, userDetails } = req.body || {}
  if (!Array.isArray(jobs) || jobs.length === 0) return res.status(400).json({ success: false, error: 'jobs array required' })

  try {
    const results = await applyToJobs(jobs, userDetails || {});
    res.json({ success: true, results });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Job listener backend running on http://localhost:${PORT}`);
});
