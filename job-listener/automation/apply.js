const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function _createContext(userDataDir, headless) {
  try {
    return { context: await chromium.launchPersistentContext(userDataDir, { headless, args: ['--no-sandbox'] }), browser: null };
  } catch (err) {
    // fallback to launching a fresh browser and use storageState if available
    const browser = await chromium.launch({ headless, args: ['--no-sandbox'] });
    const storageStatePath = path.join(userDataDir, 'storageState.json');
    const context = fs.existsSync(storageStatePath) ? await browser.newContext({ storageState: storageStatePath }) : await browser.newContext();
    return { context, browser };
  }
}

async function applyToJobs(jobs, userDetails = {}) {
  const headless = process.env.HEADLESS === '1' || process.env.HEADLESS === 'true';
  const results = [];

  const browser = await chromium.launch({ headless, args: ['--no-sandbox'] });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Default resume path if not provided in userDetails (project-local resume folder)
  const defaultResume = path.join(__dirname, '..', 'resume', 'Prashant_Pathak_Latest.pdf');
  const resumePath = (userDetails && userDetails.resumeUrl) ? userDetails.resumeUrl : defaultResume;

  for (const job of jobs) {
    const r = { url: job.url, title: job.title, applied: false, message: '', missingFields: [] };
    try {
      await page.goto(job.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(1500);

      // Try to click Easy Apply or Apply buttons
      const easyApply = page.locator('button:has-text("Easy Apply")');
      const genericApply = page.locator('button:has-text("Apply")');

      let clicked = false;
      if (await easyApply.count() > 0) { await easyApply.first().click(); clicked = true; }
      else if (await genericApply.count() > 0) { await genericApply.first().click(); clicked = true; }

      await page.waitForTimeout(1000);

      // If a file input is present in the current page/frame, upload resume
      const fileInputs = await page.$$('input[type=file]');
      if (fileInputs && fileInputs.length > 0) {
        // ensure file exists
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

      // Detect required inputs and collect names/placeholders
      const requiredInputs = await page.$$('[required], input[aria-required="true"]');
      for (const inp of requiredInputs) {
        try {
          const name = await inp.getAttribute('name') || await inp.getAttribute('id') || await inp.getAttribute('placeholder') || 'required_field';
          // simple mapping: if we have a value for common fields, fill them
          const lname = (name || '').toLowerCase();
          if (lname.includes('email') && userDetails.email) await inp.fill(userDetails.email);
          else if ((lname.includes('name') || lname.includes('full')) && userDetails.fullName) await inp.fill(userDetails.fullName);
          else if (lname.includes('phone') && userDetails.phone) await inp.fill(userDetails.phone);
          else r.missingFields.push({ field: name });
        } catch (e) { /* ignore per-field */ }
      }

      // Attempt submit if a submit button exists
      const submitBtn = page.locator('button:has-text("Submit"), button:has-text("Send"), button:has-text("Finish"), button:has-text("Confirm")');
      if (await submitBtn.count() > 0 && r.missingFields.length === 0) {
        try { await submitBtn.first().click(); r.applied = true; r.message += 'Application submitted.'; }
        catch (e) { r.message += `Submit failed: ${e.message}`; }
      } else if (r.missingFields.length === 0) {
        // no clear submit button; mark as attempted
        r.applied = true;
        r.message += 'No explicit submit button found; attempted steps recorded.';
      }
    } catch (err) {
      r.message = `Error during apply: ${err.message}`;
    }
    results.push(r);
  }

  await context.close();
  await browser.close();
  return results;
}

module.exports = { applyToJobs };
