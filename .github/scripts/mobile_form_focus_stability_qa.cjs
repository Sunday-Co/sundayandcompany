const { webkit } = require('/tmp/sunday-focus/node_modules/playwright');

const base = 'http://127.0.0.1:4173';
const failures = [];
const check = (name, ok, detail = '') => {
  console.log(`${ok ? 'PASS' : 'FAIL'} | ${name}${detail ? ' | ' + detail : ''}`);
  if (!ok) failures.push(name + (detail ? ' :: ' + detail : ''));
};

async function closeReservation(page) {
  const close = page.locator('[aria-label="The Sunday Reservation"] button[aria-label="Close"]');
  if (await close.count() && await close.first().isVisible().catch(() => false)) {
    await close.first().click();
    await page.waitForTimeout(180);
  }
}

async function openInquiry(page) {
  await page.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
  const modal = page.locator('[role="dialog"][aria-label="Project inquiry"]');
  await modal.waitFor({ state: 'visible' });
  await page.waitForTimeout(180);
  return modal;
}

async function checkVisibleEditableSizes(page, prefix) {
  const rows = await page.locator('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]), textarea, select, [contenteditable="true"]').evaluateAll(nodes => nodes.map((el, i) => {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const visible = cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0;
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
}

(async () => {
  const browser = await webkit.launch();
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'no-preference' });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(String(err)));

  const routes = ['/', '/services/', '/contact/', '/join-our-team/', '/sunday-school/'];
  for (const route of routes) {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(350);
    await closeReservation(page);
    const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
    check(`${route} keeps accessible viewport scaling`, !!viewport && !/user-scalable\s*=\s*no/i.test(viewport) && !/maximum-scale\s*=\s*1(?:\D|$)/i.test(viewport), String(viewport));
    await checkVisibleEditableSizes(page, route);
  }

  // Project Inquiry: lock the page, keep the dialog anchored while the usable
  // viewport shrinks, then restore the exact page position on close.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(350);
  await closeReservation(page);
  await page.evaluate(() => window.scrollTo(0, Math.min(1100, Math.max(0, document.documentElement.scrollHeight - innerHeight - 80))));
  await page.waitForTimeout(180);
  const originalScroll = await page.evaluate(() => window.scrollY);
  const modal = await openInquiry(page);
  const locked = await page.evaluate(() => ({
    dataset: document.documentElement.getAttribute('data-sunday-form-modal'),
    position: document.body.style.position,
    top: document.body.style.top,
    overflow: document.body.style.overflow,
    visualHeight: getComputedStyle(document.documentElement).getPropertyValue('--sunday-visual-height').trim()
  }));
  check('Inquiry locks background page on mobile', locked.dataset === 'open' && locked.position === 'fixed' && locked.overflow === 'hidden' && Math.abs(parseFloat(locked.top) + originalScroll) <= 1, JSON.stringify({ originalScroll, locked }));

  const nameInput = modal.locator('input[name="name"]').first();
  const nameSize = await nameInput.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  check('Inquiry input is 16px before focus', nameSize >= 15.9, String(nameSize));
  await nameInput.focus();
  await page.waitForTimeout(180);
  const scaleBefore = await page.evaluate(() => window.visualViewport ? window.visualViewport.scale : 1);
  check('Inquiry focus does not change WebKit page scale', Math.abs(scaleBefore - 1) < 0.01, String(scaleBefore));
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
  await page.waitForTimeout(320);
  const restored = await page.evaluate(() => ({
    y: window.scrollY,
    dataset: document.documentElement.getAttribute('data-sunday-form-modal'),
    position: document.body.style.position,
    top: document.body.style.top,
    overflow: document.body.style.overflow
  }));
  check('Inquiry close restores original page position', Math.abs(restored.y - originalScroll) <= 2, JSON.stringify({ originalScroll, restored }));
  check('Inquiry close fully removes page lock', !restored.dataset && restored.position !== 'fixed', JSON.stringify(restored));

  // Reservation popup uses the same stable mobile treatment.
  await page.evaluate(() => { try { sessionStorage.removeItem('sunday-reservation-seen'); } catch (_) {} });
  await page.reload({ waitUntil: 'networkidle' });
  const reservation = page.locator('[role="dialog"][aria-label="The Sunday Reservation"]');
  await reservation.waitFor({ state: 'visible', timeout: 4000 });
  await page.waitForTimeout(180);
  const reservationEmail = reservation.locator('input[type="email"]').first();
  await reservationEmail.focus();
  const resFont = await reservationEmail.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  const resTopBefore = (await reservation.boundingBox()).y;
  const resBodyTop = await page.evaluate(() => document.body.style.top);
  await page.setViewportSize({ width: 390, height: 560 });
  await page.waitForTimeout(520);
  const resTopAfter = (await reservation.boundingBox()).y;
  const resState = await page.evaluate(() => ({ position: document.body.style.position, top: document.body.style.top, modal: document.documentElement.getAttribute('data-sunday-form-modal') }));
  check('Reservation email stays 16px', resFont >= 15.9, String(resFont));
  check('Reservation stays anchored during viewport shrink', Math.abs(resTopAfter - resTopBefore) <= 2 && resState.position === 'fixed' && resState.top === resBodyTop && resState.modal === 'open', JSON.stringify({ resTopBefore, resTopAfter, resBodyTop, resState }));
  await page.screenshot({ path: 'qa-artifacts/reservation-focus-small-viewport.png', fullPage: false });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(260);
  await reservation.locator('button[aria-label="Close"]').click();
  await page.waitForTimeout(260);

  check('No page or console errors during focus QA', consoleErrors.length === 0, JSON.stringify(consoleErrors));

  await context.close();
  await browser.close();

  if (failures.length) {
    console.error('\nFAILURES\n' + failures.join('\n'));
    process.exit(1);
  }
})().catch(err => {
  console.error(err);
  process.exit(2);
});
