import { webkit } from 'playwright';
import fs from 'node:fs';

const base = 'http://127.0.0.1:4173';
const out = '/tmp/sunday-qa';
fs.mkdirSync(out, { recursive: true });
const failures = [];
const check = (ok, message) => { if (!ok) failures.push(message); };

async function closeVisibleOverlays(page) {
  const closers = page.locator('button[aria-label="Close"]');
  for (let i = (await closers.count()) - 1; i >= 0; i--) {
    const b = closers.nth(i);
    if (await b.isVisible().catch(() => false)) {
      await b.click({ force: true }).catch(() => {});
      await page.waitForTimeout(120);
    }
  }
}

async function checkInquiryLockup(root, label) {
  const kicker = root.locator('[data-inquiry-kicker]').first();
  const h2 = kicker.locator('xpath=following-sibling::h2[1]');
  check(await kicker.count() > 0, `${label}: Inquiry kicker missing`);
  check(await h2.count() > 0, `${label}: Inquiry Playfair heading missing`);
  if (!(await kicker.count()) || !(await h2.count())) return;
  const k = await kicker.evaluate(el => { const s=getComputedStyle(el); return {family:s.fontFamily,size:parseFloat(s.fontSize),weight:s.fontWeight}; });
  const h = await h2.evaluate(el => { const s=getComputedStyle(el); return {family:s.fontFamily,size:parseFloat(s.fontSize),weight:s.fontWeight}; });
  const kb = await kicker.boundingBox();
  const hb = await h2.boundingBox();
  check(k.family.includes('Pinyon'), `${label}: Inquiry lead is not Pinyon: ${k.family}`);
  check(k.size >= 40 && k.size <= 44, `${label}: Inquiry mobile Pinyon size out of range: ${k.size}`);
  check(k.weight === '400', `${label}: Inquiry Pinyon weight is not 400: ${k.weight}`);
  check(h.family.includes('Playfair'), `${label}: Inquiry response is not Playfair: ${h.family}`);
  check(h.size >= 26 && h.size <= 29, `${label}: Inquiry mobile Playfair size out of range: ${h.size}`);
  check(h.weight === '400', `${label}: Inquiry Playfair weight is not 400: ${h.weight}`);
  if (kb && hb) check(hb.y - (kb.y + kb.height) > -3, `${label}: Inquiry headline lines collide`);
}

const browser = await webkit.launch();
try {
  const routes = [
    '/', '/about/', '/services/', '/our-work/', '/join-our-team/', '/sunday-school/', '/contact/',
    '/privacy-policy/', '/terms-and-conditions/', '/cookie-policy/', '/accessibility/', '/our-work/folake/',
    '/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/', '/our-work/pizzeria-coco/', '/404.html'
  ];
  for (const route of routes) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + route, { waitUntil: 'networkidle' });
    await page.waitForTimeout(300);
    await closeVisibleOverlays(page);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `${route}: mobile horizontal overflow ${overflow}`);
    check(await page.locator('link[href*="/assets/rendered-corrections.css?v=20260912-7"]').count() > 0, `${route}: v7 correction stylesheet missing`);
    check(await page.locator('script[src*="/assets/site.js?v=20260912-7"]').count() > 0, `${route}: v7 site.js missing`);
    const tooSmallInputs = await page.locator('input:not([type="hidden"]), textarea, select').evaluateAll(els => els.filter(el => {
      const s = getComputedStyle(el); const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && parseFloat(s.fontSize) < 16;
    }).map(el => `${el.tagName}:${getComputedStyle(el).fontSize}`));
    check(tooSmallInputs.length === 0, `${route}: functional mobile controls under 16px: ${tooSmallInputs.join(', ')}`);
    const badHeadings = await page.locator('h1,h2,h3,h1 span,h1 em,h2 span,h2 em,h3 span,h3 em').evaluateAll(els => els.filter(el => {
      const r=el.getBoundingClientRect(); return r.width>0 && r.height>0 && getComputedStyle(el).fontWeight !== '400';
    }).slice(0,5).map(el => `${el.tagName}:${getComputedStyle(el).fontWeight}`));
    check(badHeadings.length === 0, `${route}: visible heading weight mismatch: ${badHeadings.join(', ')}`);
    await page.close();
  }

  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + '/join-our-team/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(700);
    await closeVisibleOverlays(page);
    const cards = page.locator('[data-program-cards] > article');
    check(await cards.count() === 3, `Expected 3 program cards, found ${await cards.count()}`);
    for (let i = 0; i < Math.min(3, await cards.count()); i++) {
      const card = cards.nth(i);
      const inner = card.locator(':scope > div');
      const front = inner.locator(':scope > button:first-child');
      const back = inner.locator(':scope > div:nth-child(2)');
      const attr = (await inner.getAttribute('style')) || '';
      check(attr.includes('rotateY(0deg)'), `Program card ${i+1} does not start front-facing`);
      check((await front.evaluate(el => getComputedStyle(el).visibility)) === 'visible', `Program card ${i+1} front is not visible initially`);
      check((await back.evaluate(el => getComputedStyle(el).visibility)) === 'hidden', `Program card ${i+1} back leaks through initially`);
    }
    const first = cards.first();
    await first.scrollIntoViewIfNeeded();
    await first.locator(':scope > div > button:first-child').click({ force: true });
    await page.waitForTimeout(1050);
    const firstInner = first.locator(':scope > div');
    const firstBack = firstInner.locator(':scope > div:nth-child(2)');
    check(((await firstInner.getAttribute('style')) || '').includes('rotateY(180deg)'), 'First mobile program card did not flip to 180deg');
    check((await firstBack.evaluate(el => getComputedStyle(el).visibility)) === 'visible', 'First mobile program back is not visible after flip');
    check(((await firstBack.textContent()) || '').includes('View Full Details'), 'Mobile flipped card is missing View Full Details');
    for (let i = 1; i < Math.min(3, await cards.count()); i++) {
      const inner = cards.nth(i).locator(':scope > div');
      const front = inner.locator(':scope > button:first-child');
      const back = inner.locator(':scope > div:nth-child(2)');
      check(((await inner.getAttribute('style')) || '').includes('rotateY(0deg)'), `Untapped program card ${i+1} rotated unexpectedly`);
      check((await front.evaluate(el => getComputedStyle(el).visibility)) === 'visible', `Untapped program card ${i+1} front disappeared`);
      check((await back.evaluate(el => getComputedStyle(el).visibility)) === 'hidden', `Untapped program card ${i+1} shows mirrored back`);
    }
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Join Our Team mobile horizontal overflow: ${overflow}`);
    await page.screenshot({ path: out + '/join-mobile.png', fullPage: true });
    await page.close();
  }

  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + '/services/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(700);
    await closeVisibleOverlays(page);
    const inquiry = page.locator('#inquiry');
    await inquiry.scrollIntoViewIfNeeded();
    await checkInquiryLockup(inquiry, 'Services');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Services mobile horizontal overflow: ${overflow}`);
    await inquiry.screenshot({ path: out + '/services-inquiry-mobile.png' });
    await page.close();
  }

  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + '/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(650);
    await closeVisibleOverlays(page);
    await page.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
    const popup = page.locator('[aria-label="Project inquiry"]');
    await popup.waitFor({ state: 'visible', timeout: 3000 }).catch(() => {});
    check(await popup.isVisible().catch(() => false), 'Project Inquiry popup did not open');
    if (await popup.isVisible().catch(() => false)) {
      await checkInquiryLockup(popup, 'Popup');
      await popup.screenshot({ path: out + '/inquiry-popup-mobile.png' });
    }
    await page.close();
  }

  {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await page.goto(base + '/our-work/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(650);
    await closeVisibleOverlays(page);
    const receipt = page.locator('[data-work-receipt]');
    const box = await receipt.boundingBox();
    check(!!box, 'Our Work receipt hook did not render');
    if (box) check(box.width >= 440, `Our Work desktop receipt is still too small: ${box.width}`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Our Work desktop horizontal overflow: ${overflow}`);
    await page.screenshot({ path: out + '/our-work-desktop.png', fullPage: true });
    await page.close();
  }

  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + '/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(650);
    await closeVisibleOverlays(page);
    const sign = page.locator('[data-sign]');
    await sign.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    const neon = sign.locator('p[aria-hidden][style*="Pinyon Script"]').first();
    const swing = sign.locator(':scope > div[style*="transform-origin"]').first();
    check(await neon.count() > 0, 'Open sign neon text element not found');
    if (await neon.count()) {
      const anim = await neon.evaluate(el => { const s=getComputedStyle(el); return {name:s.animationName,duration:s.animationDuration,iteration:s.animationIterationCount}; });
      check(anim.name.includes('sc-neon-sunday-final'), `Open sign missing final slow neon animation: ${anim.name}`);
      check(anim.duration.includes('8.4s'), `Open sign neon cadence is not 8.4s: ${anim.duration}`);
      check(anim.iteration.includes('infinite'), `Open sign is not continuous: ${anim.iteration}`);
    }
    check(await swing.count() > 0, 'Open sign sway element not found');
    if (await swing.count()) {
      const anim = await swing.evaluate(el => { const s=getComputedStyle(el); return {name:s.animationName,duration:s.animationDuration,iteration:s.animationIterationCount}; });
      check(anim.name.includes('sc-sway'), `Open sign sway missing: ${anim.name}`);
      check(anim.duration.includes('12s'), `Open sign sway cadence is not 12s: ${anim.duration}`);
      check(anim.iteration.includes('infinite'), `Open sign sway is not continuous: ${anim.iteration}`);
    }
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Home mobile horizontal overflow: ${overflow}`);
    await page.screenshot({ path: out + '/home-mobile.png', fullPage: true });
    await page.close();
  }

  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
    await page.goto(base + '/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    const sign = page.locator('[data-sign]');
    await sign.scrollIntoViewIfNeeded();
    const neon = sign.locator('p[aria-hidden][style*="Pinyon Script"]').first();
    if (await neon.count()) {
      const name = await neon.evaluate(el => getComputedStyle(el).animationName);
      check(name === 'none', `Reduced motion still animates Open sign: ${name}`);
    }
    await page.close();
  }
} finally {
  await browser.close();
}

if (failures.length) {
  console.error('\nTARGETED QA FAILURES');
  failures.forEach(f => console.error(' - ' + f));
  process.exit(1);
}
console.log('Final WebKit QA passed across production routes and key interactions.');
