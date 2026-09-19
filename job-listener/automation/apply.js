const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');
const browserPool = require('./browserPool');

async function _createContext(userDataDir, headless) {
  try {
    const persistentContext = await chromium.launchPersistentContext(userDataDir, {
      headless,
      args: ['--no-sandbox']
    });
    return { context: persistentContext, browser: null };
  } catch (err) {
    const message = (err && err.message) ? err.message.toLowerCase() : '';
    if (message.includes('profile is already in use') || message.includes('opening in existing browser session')) {
      const browser = await chromium.launch({ headless, args: ['--no-sandbox'] });
      const storageStatePath = path.join(userDataDir, 'storageState.json');
      const context = fs.existsSync(storageStatePath)
        ? await browser.newContext({ storageState: storageStatePath })
        : await browser.newContext();
      return { context, browser };
    }
    throw err;
  }
}

async function applyToJobs(jobs, userDetails = {}, userDataDir = process.env.USER_DATA_DIR || path.join(os.homedir(), '.linkedin_playwright_profile')) {
  const headless = process.env.HEADLESS === '1' || process.env.HEADLESS === 'true';
  const results = [];
  const resolvedUserDataDir = userDataDir || process.env.USER_DATA_DIR || path.join(os.homedir(), '.linkedin_playwright_profile');

  // ensure the user data dir exists
  try { fs.mkdirSync(resolvedUserDataDir, { recursive: true }); } catch (e) { /* ignore */ }

  const storageStatePath = path.join(resolvedUserDataDir, 'storageState.json');

  let context;
  let browser = null;
  let usedBrowserPool = false;
  // Always initialize the shared browserPool so scrape and apply reuse the same persistent context/session.
  await browserPool.init(resolvedUserDataDir, headless);
  context = browserPool.getContext();
  try { browser = browserPool.getBrowser(); } catch (e) { browser = null; }
  usedBrowserPool = true;

  // If no storage exists yet and we're running headful, prompt the user to log in interactively so we can capture the session.
  if (!fs.existsSync(storageStatePath) && !headless) {
    try {
      const page = await context.newPage();
      await page.goto('https://www.linkedin.com/', { waitUntil: 'domcontentloaded' });
      console.log('\nPlease log into LinkedIn in the opened browser window. When finished, return here and press Enter to continue.');
      const readline = require('readline');
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      await new Promise((resolve) => rl.question('Press Enter after logging in...', () => { rl.close(); resolve(); }));
      try { await page.close(); } catch (e) {}
      // Save storage state after interactive login
      try {
        const state = await context.storageState();
        fs.writeFileSync(storageStatePath, JSON.stringify(state));
        console.log('Saved storage state to', storageStatePath);
      } catch (e) {
        console.warn('Failed to save storage state:', e.message);
      }
    } catch (e) {
      // ignore interactive flow failures
    }
  }

  // Helper: quick authenticated check by visiting the feed and ensuring we're not on the login page
  async function isAuthenticated(ctx) {
    let page;
    try {
      page = await ctx.newPage();
      const resp = await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(1000);
      const url = page.url();
      const loginForm = await page.$('input[name="session_key"], input#username');
      if (loginForm) return false;
      // if redirected to a sign-in path, assume unauthenticated
      if (url.includes('/login') || url.includes('/checkpoint')) return false;
      return true;
    } catch (e) {
      return false;
    } finally {
      try { if (page) await page.close(); } catch (e) {}
    }
  }

  // Verify authentication; if not authenticated, require interactive login.
  const authed = await isAuthenticated(context).catch(() => false);
  if (!authed) {
    if (headless) {
      throw new Error('Not authenticated. Run once with HEADLESS=false and the same USER_DATA_DIR to log in interactively.');
    }
    // headful: prompt for interactive login to capture storage state
    try {
      const page = await context.newPage();
      await page.goto('https://www.linkedin.com/', { waitUntil: 'domcontentloaded' });
      console.log('\nSession appears unauthenticated. Please log into LinkedIn in the opened browser window. When finished, return here and press Enter to continue.');
      const readline = require('readline');
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      await new Promise((resolve) => rl.question('Press Enter after logging in...', () => { rl.close(); resolve(); }));
      try { await page.close(); } catch (e) {}
      const state = await context.storageState();
      fs.writeFileSync(storageStatePath, JSON.stringify(state));
      console.log('Saved storage state to', storageStatePath);
    } catch (e) {
      console.warn('Interactive login failed or was cancelled:', e.message);
      throw new Error('Interactive login required but failed.');
    }
  }

  // Do not write storage state here; we only persist state after actions complete
  // to avoid creating an empty/unauthenticated storageState.json before an interactive login.

  // Default resume path if not provided in userDetails (project-local resume folder)
  const defaultResume = path.join(__dirname, '..', 'resume', 'Prashant_Pathak_Latest.pdf');
  const resumePath = (userDetails && userDetails.resumeUrl) ? userDetails.resumeUrl : defaultResume;

  function normalizeLinkedInJobUrl(url) {
    if (!url || typeof url !== 'string') return url;
    // Try to extract job id from common LinkedIn patterns
    const m = url.match(/jobs\/view\/(\d+)/);
    if (m && m[1]) return `https://www.linkedin.com/jobs/view/${m[1]}/`;
    const q = url.match(/[?&](currentJobId|jobId|position)=(\d+)/);
    if (q && q[2]) return `https://www.linkedin.com/jobs/view/${q[2]}/`;
    return url;
  }

  for (const job of jobs) {
    const r = { url: job.url, title: job.title, applied: false, message: '', missingFields: [] };
    const page = await context.newPage();

    try {
      // Use the exact URL discovered by `scrape.js` so apply visits the same link.
      await page.goto(job.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(1500);

      // Try to click Easy Apply or Apply buttons
      const easyApply = page.locator('button:has-text("Easy Apply")');
      const genericApply = page.locator('button:has-text("Apply")');

      if (await easyApply.count() > 0) {
        await easyApply.first().click();
      } else if (await genericApply.count() > 0) {
        await genericApply.first().click();
      }

      await page.waitForTimeout(1000);

      const fileInputs = await page.$$('input[type=file]');
      if (fileInputs && fileInputs.length > 0) {
        if (fs.existsSync(resumePath)) {
          try {
            await fileInputs[0].setInputFiles(resumePath);
            r.message += `Uploaded resume: ${resumePath}. `;
          } catch (e) {
            r.message += `Failed to upload resume: ${e.message}. `;
          }
        } else {
          r.missingFields.push({ field: 'resume', note: `Resume not found at ${resumePath}` });
        }
      }

      const requiredInputs = await page.$$('[required], input[aria-required="true"]');
      for (const inp of requiredInputs) {
        try {
          const name = await inp.getAttribute('name') || await inp.getAttribute('id') || await inp.getAttribute('placeholder') || 'required_field';
          const lname = (name || '').toLowerCase();
          if (lname.includes('email') && userDetails.email) await inp.fill(userDetails.email);
          else if ((lname.includes('name') || lname.includes('full')) && userDetails.fullName) await inp.fill(userDetails.fullName);
          else if (lname.includes('phone') && userDetails.phone) await inp.fill(userDetails.phone);
          else r.missingFields.push({ field: name });
        } catch (e) {
          // ignore per-field failures
        }
      }

      const submitBtn = page.locator('button:has-text("Submit"), button:has-text("Send"), button:has-text("Finish"), button:has-text("Confirm")');
      if (await submitBtn.count() > 0 && r.missingFields.length === 0) {
        try {
          await submitBtn.first().click();
          r.applied = true;
          r.message += 'Application submitted.';
        } catch (e) {
          r.message += `Submit failed: ${e.message}`;
        }
      } else if (r.missingFields.length === 0) {
        r.applied = true;
        r.message += 'No explicit submit button found; attempted steps recorded.';
      }
    } catch (err) {
      r.message = `Error during apply: ${err.message}`;
    } finally {
      try {
        await page.close();
      } catch (e) {
        // ignore page close failures
      }
    }

    results.push(r);
  }

  // Save updated storage state so future runs reuse the logged-in session
  try {
    const state = await context.storageState();
    fs.writeFileSync(storageStatePath, JSON.stringify(state));
  } catch (e) {
    // ignore storage state write failures
  }

  // If we did not use the shared browserPool, close resources. browserPool manages the shared lifecycle.
  if (!usedBrowserPool) {
    try { await context.close(); } catch (e) {}
    if (browser) try { await browser.close(); } catch (e) {}
  }
  return results;
}

module.exports = { applyToJobs };
