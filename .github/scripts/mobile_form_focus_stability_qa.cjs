const { webkit } = require('/tmp/sunday-focus/node_modules/playwright');

const base = 'http://127.0.0.1:4173';
const failures = [];
const check = (name, ok, detail = '') => {
  console.log(`${ok ? 'PASS' : 'FAIL'} | ${name}${detail ? ' | ' + detail : ''}`);
  if (!ok) failures.push(name + (detail ? ' :: ' + detail : ''));
};

async function waitUnlocked(page) {
  await page.waitForFunction(() => {
    return !document.documentElement.hasAttribute('data-sunday-form-modal') &&
      document.body.style.position !== 'fixed';
  }, null, { timeout: 3000 });
}

async function closeReservation(page) {
  const dialog = page.locator('[role="dialog"][aria-label="The Sunday Reservation"]');
  if (await dialog.count() && await dialog.first().isVisible().catch(() => false)) {
    await dialog.first().locator('button[aria-label="Close"]').click();
    await dialog.first().waitFor({ state: 'hidden' });
    await waitUnlocked(page);
  }
}

async function openInquiry(page) {
  await page.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
  const modal = page.locator('[role="dialog"][aria-label="Project inquiry"]');
  await modal.waitFor({ state: 'visible' });
  await page.waitForFunction(() => document.documentElement.getAttribute('data-sunday-form-modal') === 'open');
  return modal;
}

async function checkVisibleEditableSizes(page, prefix) {
  const rows = await page.locator('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]), textarea, select, [contenteditable="true"]').evaluateAll(nodes => nodes.map((el, i) => {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const visible = cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity || 1) > 0 && r.width > 0 && r.height > 0;
    return {
      i,
      visible,
      tag: el.tagName,
      name: el.getAttribute('name') || el.getAttribute('id') || el.getAttribute('aria-label') || '',
      fontSize: parseFloat(cs.fontSize),
      touchAction: cs.touchAction
    };
  }));
  const visible = rows.filter(x => x.visible);
  const undersized = visible.filter(x => x.fontSize < 15.9);
  check(`${prefix} visible editable controls stay at 16px+`, visible.length > 0 && undersized.length === 0, JSON.stringify({ visible: visible.length, undersized }));
  const badTouch = visible.filter(x => x.touchAction !== 'manipulation');
  check(`${prefix} editable controls use manipulation touch behavior`, badTouch.length === 0, JSON.stringify({ badTouch }));

  if (visible.length) {
    const first = page.locator('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]), textarea, select, [contenteditable="true"]').filter({ visible: true }).first();
    await first.focus().catch(() => {});
    await page.waitForTimeout(80);
    const scale = await page.evaluate(() => window.visualViewport ? window.visualViewport.scale : 1);
    check(`${prefix} focusing a form field keeps page scale at 1`, Math.abs(scale - 1) < 0.01, String(scale));
  }
}

(async () => {
  const browser = await webkit.launch();

  // General form pass with the timed Reservation suppressed so it cannot
  // interfere with ordinary page-form measurements.
  const routeContext = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'no-preference' });
  await routeContext.addInitScript(() => {
    try { sessionStorage.setItem('sunday-reservation-seen', 'true'); } catch (_) {}
  });
  const routePage = await routeContext.newPage();
  const consoleErrors = [];
  routePage.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  routePage.on('pageerror', err => consoleErrors.push(String(err)));

  const routes = ['/', '/services/', '/contact/', '/join-our-team/', '/sunday-school/'];
  for (const route of routes) {
    await routePage.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
    await routePage.waitForTimeout(220);
    const viewport = await routePage.locator('meta[name="viewport"]').getAttribute('content');
    check(`${route} keeps accessible viewport scaling`, !!viewport && !/user-scalable\s*=\s*no/i.test(viewport) && !/maximum-scale\s*=\s*1(?:\D|$)/i.test(viewport), String(viewport));
    await checkVisibleEditableSizes(routePage, route);
  }
  await routeContext.close();

  // Sequential modal lifecycle pass. This deliberately opens Reservation,
  // closes it, scrolls the page, then opens Inquiry. It catches stale nested
  // body locks from component re-renders or one popup handing off to another.
  const modalContext = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'no-preference' });
  const page = await modalContext.newPage();
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(String(err)));

  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 });
  const reservation = page.locator('[role="dialog"][aria-label="The Sunday Reservation"]');
  await reservation.waitFor({ state: 'visible', timeout: 4000 });
  await page.waitForFunction(() => document.documentElement.getAttribute('data-sunday-form-modal') === 'open');

  const resEmail = reservation.locator('input[type="email"]').first();
  const resFont = await resEmail.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  check('Reservation email stays 16px', resFont >= 15.9, String(resFont));
  await resEmail.focus();
  const resScale = await page.evaluate(() => window.visualViewport ? window.visualViewport.scale : 1);
  check('Reservation field focus keeps page scale at 1', Math.abs(resScale - 1) < 0.01, String(resScale));
  const resTopBefore = (await reservation.boundingBox()).y;
  const resBodyTop = await page.evaluate(() => document.body.style.top);

  await page.setViewportSize({ width: 390, height: 560 });
  await page.waitForTimeout(520);
  const resTopAfter = (await reservation.boundingBox()).y;
  const resState = await page.evaluate(() => ({
    position: document.body.style.position,
    top: document.body.style.top,
    modal: document.documentElement.getAttribute('data-sunday-form-modal'),
    visualHeight: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sunday-visual-height')),
    viewportHeight: innerHeight
  }));
  check('Reservation stays anchored during keyboard-sized viewport shrink', Math.abs(resTopAfter - resTopBefore) <= 2 && resState.position === 'fixed' && resState.top === resBodyTop && resState.modal === 'open' && resState.visualHeight <= 562, JSON.stringify({ resTopBefore, resTopAfter, resBodyTop, resState }));
  await page.screenshot({ path: 'qa-artifacts/reservation-focus-small-viewport.png', fullPage: false });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(260);
  await reservation.locator('button[aria-label="Close"]').click();
  await reservation.waitFor({ state: 'hidden' });
  await waitUnlocked(page);
  const afterReservation = await page.evaluate(() => ({
    y: window.scrollY,
    modal: document.documentElement.getAttribute('data-sunday-form-modal'),
    position: document.body.style.position,
    top: document.body.style.top,
    overflow: document.body.style.overflow
  }));
  check('Reservation close fully clears the page lock', !afterReservation.modal && afterReservation.position !== 'fixed', JSON.stringify(afterReservation));

  await page.evaluate(() => window.scrollTo(0, Math.min(1100, Math.max(0, document.documentElement.scrollHeight - innerHeight - 80))));
  await page.waitForTimeout(180);
  const originalScroll = await page.evaluate(() => window.scrollY);
  check('Page can scroll normally after Reservation closes', originalScroll > 100, String(originalScroll));

  const modal = await openInquiry(page);
  await page.waitForTimeout(180);
  const locked = await page.evaluate(() => ({
    dataset: document.documentElement.getAttribute('data-sunday-form-modal'),
    position: document.body.style.position,
    top: document.body.style.top,
    overflow: document.body.style.overflow,
    visualHeight: getComputedStyle(document.documentElement).getPropertyValue('--sunday-visual-height').trim()
  }));
  check('Inquiry captures and locks the actual pre-open page position', locked.dataset === 'open' && locked.position === 'fixed' && locked.overflow === 'hidden' && Math.abs(parseFloat(locked.top) + originalScroll) <= 1, JSON.stringify({ originalScroll, locked }));

  const nameInput = modal.locator('input[name="name"]').first();
  const nameSize = await nameInput.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  check('Inquiry input is 16px before focus', nameSize >= 15.9, String(nameSize));
  await nameInput.focus();
  await page.waitForTimeout(180);
  const scaleBefore = await page.evaluate(() => window.visualViewport ? window.visualViewport.scale : 1);
  check('Inquiry focus keeps WebKit page scale at 1', Math.abs(scaleBefore - 1) < 0.01, String(scaleBefore));
  const topBeforeShrink = (await modal.boundingBox()).y;
  const bodyTopBefore = await page.evaluate(() => document.body.style.top);

  await page.setViewportSize({ width: 390, height: 560 });
  await page.waitForTimeout(520);
  const modalBoxSmall = await modal.boundingBox();
  const overlayBoxSmall = await modal.locator('..').boundingBox();
  const smallState = await page.evaluate(() => ({
    bodyTop: document.body.style.top,
    bodyPosition: document.body.style.position,
    visualHeight: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sunday-visual-height')),
    visualTop: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sunday-visual-top')),
    viewportHeight: innerHeight,
    activeName: document.activeElement && document.activeElement.getAttribute('name')
  }));
  check('Inquiry stays top-anchored as keyboard-sized viewport shrinks', !!modalBoxSmall && Math.abs(modalBoxSmall.y - topBeforeShrink) <= 2, JSON.stringify({ topBeforeShrink, modalBoxSmall }));
  check('Inquiry background lock does not move during viewport shrink', smallState.bodyPosition === 'fixed' && smallState.bodyTop === bodyTopBefore, JSON.stringify({ bodyTopBefore, smallState }));
  check('Inquiry overlay tracks reduced usable viewport', !!overlayBoxSmall && overlayBoxSmall.height <= 562 && smallState.visualHeight <= 562, JSON.stringify({ overlayBoxSmall, smallState }));
  check('Focused field remains the active control', smallState.activeName === 'name', JSON.stringify(smallState));
  await page.screenshot({ path: 'qa-artifacts/inquiry-focus-small-viewport.png', fullPage: false });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(280);
  await page.keyboard.press('Escape');
  await modal.waitFor({ state: 'hidden' });
  await waitUnlocked(page);
  await page.waitForTimeout(160);
  const restored = await page.evaluate(() => ({
    y: window.scrollY,
    dataset: document.documentElement.getAttribute('data-sunday-form-modal'),
    position: document.body.style.position,
    top: document.body.style.top,
    overflow: document.body.style.overflow
  }));
  check('Inquiry close restores the exact pre-open page position', Math.abs(restored.y - originalScroll) <= 2, JSON.stringify({ originalScroll, restored }));
  check('Inquiry close fully removes the page lock', !restored.dataset && restored.position !== 'fixed', JSON.stringify(restored));

  check('No page or console errors during focus QA', consoleErrors.length === 0, JSON.stringify(consoleErrors));

  await modalContext.close();
  await browser.close();

  if (failures.length) {
    console.error('\nFAILURES\n' + failures.join('\n'));
    process.exit(1);
  }
})().catch(err => {
  console.error(err);
  process.exit(2);
});
