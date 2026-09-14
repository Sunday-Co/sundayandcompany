const { webkit } = require('/tmp/sunday-post-rollback/node_modules/playwright');

const base = 'http://127.0.0.1:4173';
const routes = [
  '/', '/about/', '/services/', '/our-work/', '/our-work/folake/',
  '/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/',
  '/our-work/pizzeria-coco/', '/contact/', '/join-our-team/',
  '/sunday-school/', '/accessibility/', '/privacy-policy/',
  '/terms-and-conditions/', '/cookie-policy/', '/404.html'
];
const failures = [];
function check(name, ok, detail='') {
  console.log(`${ok ? 'PASS' : 'FAIL'} | ${name}${detail ? ' | ' + detail : ''}`);
  if (!ok) failures.push(name + (detail ? ' :: ' + detail : ''));
}

async function closeReservation(page) {
  const c = page.locator('[aria-label="The Sunday Reservation"] button[aria-label="Close"]');
  if (await c.count() && await c.first().isVisible().catch(() => false)) {
    await c.first().click();
    await page.waitForTimeout(150);
  }
}

async function routeAudit(browser, cfg) {
  for (const route of routes) {
    const context = await browser.newContext({ viewport: { width: cfg.width, height: cfg.height }, reducedMotion: 'no-preference' });
    const page = await context.newPage();
    const pageErrors = [];
    const consoleErrors = [];
    page.on('pageerror', e => pageErrors.push(String(e)));
    page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
    try {
      const resp = await page.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
      await page.waitForTimeout(250);
      await closeReservation(page);
      const status = resp ? resp.status() : 0;
      const dims = await page.evaluate(() => ({
        htmlW: document.documentElement.scrollWidth,
        bodyW: document.body ? document.body.scrollWidth : 0,
        clientW: document.documentElement.clientWidth,
        bodyPosition: document.body ? getComputedStyle(document.body).position : '',
        modalFlag: document.documentElement.hasAttribute('data-sunday-form-modal')
      }));
      const broken = await page.evaluate(() => Array.from(document.images).filter(img => img.complete && img.naturalWidth === 0).map(img => img.currentSrc || img.src || img.alt || 'image'));
      check(`${cfg.name} ${route} HTTP`, status >= 200 && status < 400, String(status));
      check(`${cfg.name} ${route} no page errors`, pageErrors.length === 0, JSON.stringify(pageErrors));
      check(`${cfg.name} ${route} no console errors`, consoleErrors.length === 0, JSON.stringify(consoleErrors));
      check(`${cfg.name} ${route} no horizontal overflow`, dims.htmlW <= cfg.width + 1 && dims.bodyW <= cfg.width + 1, JSON.stringify(dims));
      check(`${cfg.name} ${route} no broken images`, broken.length === 0, JSON.stringify(broken));
      check(`${cfg.name} ${route} no stale modal lock`, !dims.modalFlag && dims.bodyPosition !== 'fixed', JSON.stringify(dims));
    } catch (e) {
      check(`${cfg.name} ${route} audit completes`, false, String(e));
    }
    await context.close();
  }
}

async function inquiryAudit(browser, cfg) {
  const context = await browser.newContext({ viewport: { width: cfg.width, height: cfg.height }, reducedMotion: 'no-preference' });
  const page = await context.newPage();
  const pageErrors = [];
  const consoleErrors = [];
  page.on('pageerror', e => pageErrors.push(String(e)));
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(300);
  await closeReservation(page);
  await page.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
  const modal = page.locator('[role="dialog"][aria-label="Project inquiry"]');
  await modal.waitFor({ state: 'visible', timeout: 10000 });
  await page.waitForTimeout(250);
  const box = await modal.boundingBox();
  const metrics = await modal.evaluate(el => ({
    scrollWidth: el.scrollWidth,
    clientWidth: el.clientWidth,
    scrollHeight: el.scrollHeight,
    clientHeight: el.clientHeight
  }));
  const bodyState = await page.evaluate(() => ({
    position: getComputedStyle(document.body).position,
    left: document.body.style.left,
    right: document.body.style.right,
    width: document.body.style.width,
    lockFlag: document.documentElement.hasAttribute('data-sunday-form-modal'),
    htmlW: document.documentElement.scrollWidth
  }));
  check(`${cfg.name} inquiry visible`, !!box, JSON.stringify(box));
  check(`${cfg.name} inquiry stays inside viewport`, !!box && box.x >= -1 && box.x + box.width <= cfg.width + 1, JSON.stringify({ box, viewport: cfg }));
  check(`${cfg.name} inquiry centered`, !!box && Math.abs((box.x + box.width / 2) - cfg.width / 2) <= 3, JSON.stringify({ box, viewport: cfg }));
  check(`${cfg.name} inquiry no horizontal internal clipping`, metrics.scrollWidth <= metrics.clientWidth + 1, JSON.stringify(metrics));
  check(`${cfg.name} inquiry does not body-lock/reposition`, bodyState.position !== 'fixed' && !bodyState.lockFlag, JSON.stringify(bodyState));
  check(`${cfg.name} inquiry leaves page width intact`, bodyState.htmlW <= cfg.width + 1, JSON.stringify(bodyState));

  if (cfg.name === 'mobile') {
    const visibleFields = modal.locator('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), textarea, select');
    const n = await visibleFields.count();
    const sizes = [];
    for (let i = 0; i < n; i++) {
      const el = visibleFields.nth(i);
      if (!(await el.isVisible().catch(() => false))) continue;
      sizes.push(await el.evaluate(node => ({ name: node.getAttribute('name') || node.tagName, size: parseFloat(getComputedStyle(node).fontSize) })));
    }
    check('mobile inquiry editable controls are iOS-safe', sizes.length > 0 && sizes.every(x => x.size >= 16), JSON.stringify(sizes));
    const first = visibleFields.filter({ visible: true }).first();
    if (await first.count()) {
      await first.focus();
      await page.waitForTimeout(150);
      const scale = await page.evaluate(() => window.visualViewport ? window.visualViewport.scale : 1);
      check('mobile inquiry focus does not change WebKit page scale', Math.abs(scale - 1) < 0.001, String(scale));
    }
  }

  await page.screenshot({ path: `qa-artifacts/${cfg.name}-project-inquiry.png`, fullPage: false });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(250);
  const afterClose = await page.evaluate(() => ({
    position: getComputedStyle(document.body).position,
    modalFlag: document.documentElement.hasAttribute('data-sunday-form-modal'),
    htmlW: document.documentElement.scrollWidth
  }));
  check(`${cfg.name} inquiry closes cleanly`, !(await modal.isVisible().catch(() => false)), JSON.stringify(afterClose));
  check(`${cfg.name} no stale lock after inquiry close`, afterClose.position !== 'fixed' && !afterClose.modalFlag, JSON.stringify(afterClose));
  check(`${cfg.name} inquiry no page errors`, pageErrors.length === 0, JSON.stringify(pageErrors));
  check(`${cfg.name} inquiry no console errors`, consoleErrors.length === 0, JSON.stringify(consoleErrors));
  await context.close();
}

async function mobileFormsAudit(browser) {
  const pages = ['/', '/services/', '/contact/', '/join-our-team/', '/sunday-school/'];
  for (const route of pages) {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'no-preference' });
    const page = await context.newPage();
    await page.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(250);
    await closeReservation(page);
    const fields = await page.evaluate(() => Array.from(document.querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), textarea, select')).filter(el => {
      const s = getComputedStyle(el), r = el.getBoundingClientRect();
      return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
    }).map(el => ({ name: el.getAttribute('name') || el.getAttribute('aria-label') || el.tagName, size: parseFloat(getComputedStyle(el).fontSize) })));
    check(`mobile ${route} visible editable controls are >=16px`, fields.every(f => f.size >= 16), JSON.stringify(fields));
    await context.close();
  }
}

(async () => {
  const browser = await webkit.launch();
  await routeAudit(browser, { name: 'desktop', width: 1440, height: 900 });
  await routeAudit(browser, { name: 'mobile', width: 390, height: 844 });
  await inquiryAudit(browser, { name: 'desktop', width: 1440, height: 900 });
  await inquiryAudit(browser, { name: 'mobile', width: 390, height: 844 });
  await mobileFormsAudit(browser);
  await browser.close();
  if (failures.length) {
    console.error(`\nFAILURES (${failures.length})\n` + failures.join('\n'));
    process.exit(1);
  }
  console.log('\nPOST_ROLLBACK_QA: PASS');
})().catch(err => { console.error(err); process.exit(2); });
