const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');

let _pool = { context: null, browser: null, userDataDir: null, initialized: false };

async function init(userDataDir = path.join(os.homedir(), '.linkedin_playwright_profile'), headless = true) {
  if (_pool.initialized && _pool.userDataDir === userDataDir) return _pool;
  try { fs.mkdirSync(userDataDir, { recursive: true }); } catch (e) {}

  // try persistent context first
  try {
    const persistentContext = await chromium.launchPersistentContext(userDataDir, { headless, args: ['--no-sandbox'] });
    _pool = { context: persistentContext, browser: null, userDataDir, initialized: true };
    return _pool;
  } catch (err) {
    const message = (err && err.message) ? err.message.toLowerCase() : '';
    if (message.includes('profile is already in use') || message.includes('opening in existing browser session')) {
      const browser = await chromium.launch({ headless, args: ['--no-sandbox'] });
      const storageStatePath = path.join(userDataDir, 'storageState.json');
      const context = fs.existsSync(storageStatePath)
        ? await browser.newContext({ storageState: storageStatePath })
        : await browser.newContext();
      _pool = { context, browser, userDataDir, initialized: true };
      return _pool;
    }
    throw err;
  }
}

function getContext() {
  if (!_pool.initialized) throw new Error('browserPool not initialized; call init() first');
  return _pool.context;
}

function getBrowser() {
  if (!_pool.initialized) throw new Error('browserPool not initialized; call init() first');
  return _pool.browser;
}

async function saveState() {
  if (!_pool.initialized || !_pool.context) return;
  try {
    const storageStatePath = path.join(_pool.userDataDir, 'storageState.json');
    const state = await _pool.context.storageState();
    fs.writeFileSync(storageStatePath, JSON.stringify(state));
  } catch (e) {}
}

async function close() {
  try { if (_pool.context) await _pool.context.close(); } catch (e) {}
  try { if (_pool.browser) await _pool.browser.close(); } catch (e) {}
  _pool = { context: null, browser: null, userDataDir: null, initialized: false };
}

// Save on exit signals
process.once('exit', () => { saveState().catch(()=>{}); });
process.once('SIGINT', () => { saveState().then(()=>process.exit(0)).catch(()=>process.exit(0)); });
process.once('SIGTERM', () => { saveState().then(()=>process.exit(0)).catch(()=>process.exit(0)); });

module.exports = { init, getContext, getBrowser, saveState, close };
