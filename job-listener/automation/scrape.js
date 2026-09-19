const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const browserPool = require('./browserPool');

async function scrapeJobs(query = 'full stack developer', days = 1, userDataDir) {
  const headless = process.env.HEADLESS === '1' || process.env.HEADLESS === 'true';
  let context = null;
  let browser = null;

  // Use shared browserPool persistent context when available to reuse session
  await browserPool.init(userDataDir, headless);
  const context = browserPool.getContext();
  const page = await context.newPage();

  // Add LinkedIn Easy Apply filter so the search returns only jobs with the Easy Apply badge.
  const url = 'https://www.linkedin.com/jobs/search/?keywords=full%20stack%20%20developer%20essay%20apply&origin=JOB_SEARCH_PAGE_JOB_FILTER&referralSearchId=mKTQhzkroQY9IbErLj0S6A%3D%3D&f_AL=true'
  // `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(query)}&f_EA=2`;
  await page.goto(url, { waitUntil: 'domcontentloaded' });

  // Allow some time for dynamic content to load
  await page.waitForTimeout(2000);

  // Try to wait for job anchors; non-fatal if selector not found
  try { await page.waitForSelector('a[href*="/jobs/view/"]', { timeout: 10000 }); } catch (e) {}

  const jobs = await page.$$eval('a[href*="/jobs/view/"]', anchors => {
    const seen = new Set();
    const items = [];
    anchors.forEach(a => {
      const url = a.href;
      if (!url || seen.has(url)) return;

      // Also require an Easy Apply badge inside the job card container.
      const card = a.closest('li') || a.closest('div');
      const easyApplyBadge = card && Array.from(card.querySelectorAll('span')).some(span => /easy apply/i.test(span.innerText));
      if (!easyApplyBadge) return;

      seen.add(url);

      // Title heuristics
      const titleEl = a.querySelector('h3') || a.querySelector('.sr-only');
      const title = titleEl ? titleEl.innerText.trim() : (a.innerText || '').split('\n')[0].trim();

      // Try to find company and location by looking up the DOM tree
      let container = a.closest('li') || a.closest('div');
      let company = '';
      let location = '';
      if (container) {
        const comp = container.querySelector('.base-search-card__subtitle, .job-card-container__company-name, .result-card__subtitle');
        if (comp) company = comp.innerText.trim();
        const loc = container.querySelector('.job-search-card__location, .job-card-container__metadata-item');
        if (loc) location = loc.innerText.trim();
      }

      items.push({ title, company, location, url, easyApply: true });
    });
    return items.slice(0, 500);
  });

  // Persist storage state so other modules (apply) can reuse the authenticated session
  try {
    const storageStatePath = path.join(userDataDir, 'storageState.json');
    const state = await context.storageState();
    fs.writeFileSync(storageStatePath, JSON.stringify(state));
  } catch (e) {
    // ignore failures saving state
  }

  // Do not close the shared context/browser here; browserPool manages lifecycle.
  return jobs;
}

module.exports = { scrapeJobs };
