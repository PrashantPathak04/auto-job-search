const { chromium } = require('playwright');
const path = require('path');
const os = require('os');
const readline = require('readline');

const userDataDir = process.env.USER_DATA_DIR || path.join(os.homedir(), '.linkedin_playwright_profile');

(async () => {
  const context = await chromium.launchPersistentContext(userDataDir, { headless: false });
  const page = await context.newPage();
  await page.goto('https://www.linkedin.com/login');
  console.log('\nA browser window has opened. Please sign in to LinkedIn in that window.');
  console.log('After you finish signing in, return here and press Enter to continue.');

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  await new Promise(resolve => rl.question('', () => { rl.close(); resolve(); }));

  // Save storage state (optional)
  try {
    await context.storageState({ path: path.join(userDataDir, 'storageState.json') });
    console.log('Saved storageState.json');
  } catch (e) { }

  await context.close();
  console.log('Profile setup complete. You can now run the backend server.');
})();
