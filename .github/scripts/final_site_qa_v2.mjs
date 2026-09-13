import { webkit } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import assert from 'node:assert';
import fs from 'node:fs';

const base = 'http://127.0.0.1:4173';
const out = 'final-site-qa-v2';
fs.mkdirSync(out, { recursive: true });

const publicRoutes = [
  '/', '/about/', '/services/', '/our-work/',
  '/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/',
  '/our-work/pizzeria-coco/', '/our-work/folake/',
  '/contact/', '/join-our-team/', '/sunday-school/',
  '/accessibility/', '/privacy-policy/', '/terms-and-conditions/', '/cookie-policy/'
];

const browser = await webkit.launch();

async function openRoute(route, viewport = { width: 390, height: 844 }) {
  let context = await browser.newContext({ viewport });
  let page = await context.newPage();
  try {
    await page.goto(base + route, { waitUntil: 'domcontentloaded', timeout: 45000 });
  } catch (err) {
    await context.close();
    context = await browser.newContext({ viewport });
    page = await context.newPage();
    await page.goto(base + route, { waitUntil: 'commit', timeout: 30000 });
    await page.waitForFunction(() => document.readyState !== 'loading', null, { timeout: 30000 }).catch(() => {});
  }
  await page.waitForTimeout(450);
  return { context, page };
}

async function closeReservation(page) {
  const close = page.locator('[aria-label="The Sunday Reservation"] button[aria-label="Close"]');
  if (await close.count() && await close.first().isVisible().catch(() => false)) {
    await close.first().evaluate(el => el.click());
    await page.waitForTimeout(120);
  }
}

async function structuralAudit(page, route) {
  const result = await page.evaluate(() => {
    const visible = el => {
      const s = getComputedStyle(el), r = el.getBoundingClientRect();
      return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
    };
    const controlName = el => {
      const aria = (el.getAttribute('aria-label') || '').trim();
      if (aria) return aria;
      const labelled = (el.getAttribute('aria-labelledby') || '').split(/\s+/).filter(Boolean).map(id => document.getElementById(id)?.textContent || '').join(' ').trim();
      if (labelled) return labelled;
      if (el.id) {
        const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
        if (label?.textContent?.trim()) return label.textContent.trim();
      }
      const wrap = el.closest('label');
      if (wrap?.textContent?.trim()) return wrap.textContent.trim();
      const txt = (el.textContent || '').replace(/\s+/g, ' ').trim();
      if (txt) return txt;
      return (el.getAttribute('title') || '').trim();
    };
    return {
      lang: document.documentElement.lang,
      title: document.title.trim(),
      mainCount: document.querySelectorAll('main#main-content').length,
      h1Count: [...document.querySelectorAll('h1')].filter(visible).length,
      unnamedControls: [...document.querySelectorAll('a[href],button,input,textarea,select')].filter(visible).filter(el => !controlName(el)).map(el => el.outerHTML.slice(0, 180)),
      missingAlt: [...document.images].filter(img => !img.hasAttribute('alt')).map(img => img.outerHTML.slice(0, 180)),
      unnamedDialogs: [...document.querySelectorAll('[role="dialog"]')].filter(visible).filter(el => !(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby'))).map(el => el.outerHTML.slice(0, 160)),
      brokenImages: [...document.images].filter(img => img.complete && img.naturalWidth === 0).map(img => img.getAttribute('src')),
      overflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });

  assert.strictEqual(result.lang, 'en', `${route}: html lang must be en`);
  assert.ok(result.title, `${route}: document title missing`);
  assert.strictEqual(result.mainCount, 1, `${route}: expected exactly one main#main-content, got ${result.mainCount}`);
  assert.strictEqual(result.h1Count, 1, `${route}: expected exactly one visible H1, got ${result.h1Count}`);
  assert.deepStrictEqual(result.unnamedControls, [], `${route}: unnamed visible controls ${JSON.stringify(result.unnamedControls)}`);
  assert.deepStrictEqual(result.missingAlt, [], `${route}: images missing alt ${JSON.stringify(result.missingAlt)}`);
  assert.deepStrictEqual(result.unnamedDialogs, [], `${route}: unnamed dialogs ${JSON.stringify(result.unnamedDialogs)}`);
  assert.deepStrictEqual(result.brokenImages, [], `${route}: broken images ${JSON.stringify(result.brokenImages)}`);
  assert.ok(result.overflowPx <= 2, `${route}: horizontal overflow ${result.overflowPx}px`);

  const axe = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  const serious = axe.violations.filter(v => ['critical', 'serious'].includes(v.impact));
  assert.deepStrictEqual(
    serious.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length })),
    [],
    `${route}: serious/critical axe violations`
  );
}

for (const route of publicRoutes) {
  console.log(`AUDIT ${route}`);
  const { context, page } = await openRoute(route);
  await closeReservation(page);
  await structuralAudit(page, route);
  await context.close();
}

// 404 gets the same structural checks separately.
{
  const { context, page } = await openRoute('/404.html');
  await closeReservation(page);
  await structuralAudit(page, '/404.html');
  await context.close();
}

// Home mobile: skip link, inquiry geometry, focus management, footer and capture.
let homeHero, footerMetrics;
{
  const { context, page } = await openRoute('/');
  await closeReservation(page);

  const skip = page.locator('a[href="#main-content"]').first();
  assert.ok(await skip.count(), 'Skip link missing');
  await skip.evaluate(el => el.click());
  await page.waitForTimeout(100);
  assert.strictEqual(await page.evaluate(() => document.activeElement?.id), 'main-content', 'Skip link did not focus main content');

  const opener = page.getByText('Start A Project', { exact: true }).first();
  await opener.focus();
  await opener.evaluate(el => el.click());
  await page.waitForTimeout(300);
  const inquiry = page.locator('[role="dialog"][aria-label="Project inquiry"]');
  assert.ok(await inquiry.isVisible(), 'Project Inquiry did not open');
  const inquiryBox = await inquiry.evaluate(el => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, height: r.height, opacity: s.opacity };
  });
  const center = (inquiryBox.top + inquiryBox.bottom) / 2;
  assert.ok(Math.abs(center - 422) <= 30, `Mobile inquiry not centered: ${JSON.stringify(inquiryBox)}`);
  assert.ok(inquiryBox.top >= 0 && inquiryBox.bottom <= 844, `Mobile inquiry clips viewport: ${JSON.stringify(inquiryBox)}`);
  assert.strictEqual(inquiryBox.opacity, '1', 'Inquiry must be fully opaque');
  assert.ok(await inquiry.evaluate(el => el.contains(document.activeElement)), 'Focus did not enter Project Inquiry');
  await page.screenshot({ path: `${out}/mobile-inquiry.png` });

  // Tab must stay in modal, Escape closes, focus returns to opener.
  for (let i = 0; i < 18; i++) await page.keyboard.press('Tab');
  assert.ok(await inquiry.evaluate(el => el.contains(document.activeElement)), 'Tab focus escaped Project Inquiry');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(160);
  assert.ok(!(await inquiry.isVisible().catch(() => false)), 'Escape did not close Project Inquiry');
  assert.ok((await page.evaluate(() => (document.activeElement?.textContent || '').replace(/\s+/g, ' ').trim())).startsWith('Start A Project'), 'Focus did not return to inquiry opener');

  // Mobile navigation focus containment and return.
  const menu = page.getByRole('button', { name: 'Open menu' });
  await menu.focus();
  await menu.click();
  await page.waitForTimeout(180);
  const sheet = page.locator('aside[aria-label="Sunday & Company navigation"]');
  assert.ok(await sheet.evaluate(el => el.contains(document.activeElement)), 'Focus did not enter mobile nav');
  for (let i = 0; i < 12; i++) await page.keyboard.press('Tab');
  assert.ok(await sheet.evaluate(el => el.contains(document.activeElement)), 'Tab focus escaped mobile nav');
  await page.keyboard.press('Escape');
  await page.waitForTimeout(150);
  assert.strictEqual(await page.evaluate(() => document.activeElement?.getAttribute('aria-label')), 'Open menu', 'Focus did not return to menu opener');

  await page.locator('footer').scrollIntoViewIfNeeded();
  await page.waitForTimeout(120);
  footerMetrics = await page.locator('footer').evaluate(el => {
    const s = getComputedStyle(el);
    const email = el.querySelector('a[href^="mailto:"]');
    const tagline = el.querySelector('[data-footer-tagline]');
    const fine = document.querySelector('[aria-label="Newsletter"] [data-news-fineprint]');
    return {
      paddingBottom: parseFloat(s.paddingBottom),
      emailSize: parseFloat(getComputedStyle(email).fontSize),
      emailWeight: getComputedStyle(email).fontWeight,
      taglineFamily: getComputedStyle(tagline).fontFamily,
      fineSize: fine ? parseFloat(getComputedStyle(fine).fontSize) : 0,
    };
  });
  assert.ok(footerMetrics.paddingBottom >= 44, `Footer bottom padding ${footerMetrics.paddingBottom}`);
  assert.ok(footerMetrics.emailSize >= 13, `Footer email size ${footerMetrics.emailSize}`);
  assert.strictEqual(footerMetrics.emailWeight, '400', `Footer email weight ${footerMetrics.emailWeight}`);
  assert.ok(footerMetrics.taglineFamily.includes('Inter Tight'), `Footer tagline font ${footerMetrics.taglineFamily}`);
  assert.ok(footerMetrics.fineSize >= 8, `Newsletter fine print ${footerMetrics.fineSize}`);
  await page.screenshot({ path: `${out}/mobile-footer.png` });
  await context.close();
}

// Homepage full-page hero is a decoded flow-based image in both screen and print media.
{
  const { context, page } = await openRoute('/');
  await closeReservation(page);
  const hero = page.locator('section#top[data-screen-hero="home"] > img[data-sunday-static-hero="true"]');
  homeHero = await hero.evaluate(el => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return { complete: el.complete, nw: el.naturalWidth, nh: el.naturalHeight, width: r.width, height: r.height, position: s.position, opacity: s.opacity, display: s.display };
  });
  assert.ok(homeHero.complete && homeHero.nw > 0 && homeHero.nh > 0, `Hero image not decoded ${JSON.stringify(homeHero)}`);
  assert.ok(homeHero.height >= 680, `Hero image flow height ${homeHero.height}`);
  assert.strictEqual(homeHero.position, 'relative', 'Hero should be in normal document flow');
  assert.strictEqual(homeHero.opacity, '1');
  await page.screenshot({ path: `${out}/mobile-home-full.png`, fullPage: true });
  await page.emulateMedia({ media: 'print' });
  const printHero = await hero.evaluate(el => ({ nw: el.naturalWidth, opacity: getComputedStyle(el).opacity, display: getComputedStyle(el).display }));
  assert.ok(printHero.nw > 0 && printHero.opacity === '1' && printHero.display !== 'none', `Print hero hidden ${JSON.stringify(printHero)}`);
  await page.screenshot({ path: `${out}/mobile-home-print.png`, fullPage: true });
  await context.close();
}

// Desktop Project Inquiry stays centered too.
{
  const { context, page } = await openRoute('/', { width: 1440, height: 1000 });
  await closeReservation(page);
  const opener = page.getByText('Start A Project', { exact: true }).first();
  await opener.evaluate(el => el.click());
  await page.waitForTimeout(280);
  const box = await page.locator('[role="dialog"][aria-label="Project inquiry"]').evaluate(el => { const r = el.getBoundingClientRect(); return { top: r.top, bottom: r.bottom }; });
  assert.ok(Math.abs(((box.top + box.bottom) / 2) - 500) <= 35, `Desktop inquiry not centered ${JSON.stringify(box)}`);
  await page.screenshot({ path: `${out}/desktop-inquiry.png` });
  await context.close();
}

// Our Work layout regression at medium/wide desktop.
for (const width of [1180, 1440]) {
  const { context, page } = await openRoute('/our-work/', { width, height: 1000 });
  await closeReservation(page);
  const layout = await page.evaluate(() => {
    const title = document.querySelector('#work-title > span');
    const receipt = document.querySelector('[data-work-receipt]');
    const a = title.getBoundingClientRect(), b = receipt.getBoundingClientRect();
    return {
      text: title.textContent.trim(),
      whiteSpace: getComputedStyle(title).whiteSpace,
      overlap: !(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top),
    };
  });
  assert.ok(layout.text.includes('A Point Of View'), `Our Work title text changed at ${width}`);
  assert.strictEqual(layout.whiteSpace, 'nowrap', `A Point Of View wraps at ${width}`);
  assert.strictEqual(layout.overlap, false, `Bill of Work overlaps title at ${width}`);
  await page.screenshot({ path: `${out}/our-work-${width}.png` });
  await context.close();
}

// Portfolio behavior protection. No removal of reveal hooks or internal screenshot frames.
for (const route of ['/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/', '/our-work/pizzeria-coco/', '/our-work/folake/']) {
  const { context, page } = await openRoute(route, { width: 1440, height: 1000 });
  await closeReservation(page);
  const protection = await page.evaluate(() => ({
    frames: document.querySelectorAll('div[style*="max-height:640px"][style*="overflow-y:auto"]').length,
    revealHooks: document.querySelectorAll('[data-reveal]').length,
    videoPreloads: [...document.querySelectorAll('video')].map(v => v.getAttribute('preload')),
  }));
  assert.ok(protection.frames >= 1, `${route}: project screenshot scroll frame missing`);
  assert.ok(protection.revealHooks >= 1, `${route}: original reveal hook missing`);
  assert.ok(protection.videoPreloads.every(v => v !== 'auto'), `${route}: eager video preload unexpectedly present`);
  await context.close();
}

// Join modal keyboard behavior and stamp readability.
{
  const { context, page } = await openRoute('/join-our-team/');
  await closeReservation(page);
  // Find first card button robustly, without relying on visual text generated on flip face.
  const cardButton = page.locator('button').filter({ hasText: 'The Fellows Table' }).first();
  if (await cardButton.count()) {
    await cardButton.evaluate(el => el.click());
    await page.waitForTimeout(950);
  }
  const details = page.getByText('View Full Details', { exact: true }).first();
  if (await details.count() && await details.isVisible().catch(() => false)) {
    await details.focus();
    await details.evaluate(el => el.click());
    await page.waitForTimeout(220);
    const dialog = page.locator('[role="dialog"][aria-label="The Fellows Table"]');
    assert.ok(await dialog.isVisible(), 'Fellows dialog did not open');
    assert.ok(await dialog.evaluate(el => el.contains(document.activeElement)), 'Focus did not enter Fellows dialog');
    const stamp = await dialog.evaluate(el => parseFloat(getComputedStyle(el, '::after').fontSize));
    assert.ok(stamp >= 7.5, `Join archive stamp too small: ${stamp}`);
    await page.screenshot({ path: `${out}/join-dialog-mobile.png` });
    await page.keyboard.press('Escape');
    await page.waitForTimeout(140);
    assert.ok(!(await dialog.isVisible().catch(() => false)), 'Escape did not close Fellows dialog');
  } else {
    throw new Error('Could not reach Fellows Table full details dialog');
  }
  await context.close();
}

await browser.close();
console.log(JSON.stringify({ status: 'PASS', homeHero, footerMetrics }, null, 2));
