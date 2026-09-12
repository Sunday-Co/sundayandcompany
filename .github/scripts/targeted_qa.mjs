import { webkit } from 'playwright';
import fs from 'node:fs';

const base = 'http://127.0.0.1:4173';
const out = '/tmp/sunday-qa';
fs.mkdirSync(out, { recursive: true });
const failures = [];

function check(ok, message) {
  if (!ok) failures.push(message);
}

async function closeVisibleOverlays(page) {
  const closers = page.locator('button[aria-label="Close"]');
  const count = await closers.count();
  for (let i = count - 1; i >= 0; i--) {
    const b = closers.nth(i);
    if (await b.isVisible().catch(() => false)) {
      await b.click({ force: true }).catch(() => {});
      await page.waitForTimeout(120);
    }
  }
}

const browser = await webkit.launch();
try {
  // Mobile Join Our Team: the card must flip, not jump directly to details.
  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + '/join-our-team/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(900);
    await closeVisibleOverlays(page);
    const card = page.locator('[data-program-cards] > article').first();
    await card.scrollIntoViewIfNeeded();
    const inner = card.locator(':scope > div');
    const front = card.locator(':scope > div > button').first();
    const back = card.locator(':scope > div > div:nth-child(2)');
    check(await front.isVisible(), 'Mobile program front face is not visible');
    const before = await inner.evaluate(el => getComputedStyle(el).transform);
    await front.click({ force: true });
    await page.waitForTimeout(1050);
    const after = await inner.evaluate(el => getComputedStyle(el).transform);
    const backDisplay = await back.evaluate(el => getComputedStyle(el).display);
    const actionText = (await back.textContent()) || '';
    check(before === 'none' || before.includes('matrix'), 'Unexpected initial card transform');
    check(after !== 'none' && !/matrix\(1, 0, 0, 1, 0, 0\)/.test(after), 'Mobile program card did not flip');
    check(backDisplay !== 'none', 'Mobile program back face is hidden');
    check(actionText.includes('View Full Details'), 'Mobile flipped card is missing View Full Details');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Join Our Team mobile horizontal overflow: ${overflow}`);
    await page.screenshot({ path: out + '/join-mobile.png', fullPage: true });
    await page.close();
  }

  // Mobile Services: inquiry hierarchy must be Playfair then rose Pinyon and stay controlled.
  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + '/services/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(900);
    await closeVisibleOverlays(page);
    const inquiry = page.locator('#inquiry');
    await inquiry.scrollIntoViewIfNeeded();
    const kicker = inquiry.locator('[data-inquiry-kicker]').first();
    const h2 = kicker.locator('xpath=following-sibling::h2[1]');
    const k = await kicker.evaluate(el => { const s=getComputedStyle(el); return {family:s.fontFamily,size:parseFloat(s.fontSize)}; });
    const h = await h2.evaluate(el => { const s=getComputedStyle(el); return {family:s.fontFamily,size:parseFloat(s.fontSize),line:parseFloat(s.lineHeight),height:el.getBoundingClientRect().height,color:s.color}; });
    check(k.family.includes('Playfair'), `Inquiry lead is not Playfair: ${k.family}`);
    check(k.size >= 33 && k.size <= 37, `Inquiry mobile Playfair size out of range: ${k.size}`);
    check(h.family.includes('Pinyon'), `Inquiry response is not Pinyon: ${h.family}`);
    check(h.size <= 36, `Inquiry mobile Pinyon is too large: ${h.size}`);
    check(h.height / h.line <= 2.35, `Inquiry Pinyon wraps to too many lines: ${h.height / h.line}`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Services mobile horizontal overflow: ${overflow}`);
    await inquiry.screenshot({ path: out + '/services-inquiry-mobile.png' });
    await page.close();
  }

  // Desktop Our Work: bill of work gets the requested larger presence.
  {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await page.goto(base + '/our-work/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(700);
    await closeVisibleOverlays(page);
    const receipt = page.locator('[data-work-receipt]');
    const box = await receipt.boundingBox();
    check(!!box, 'Our Work receipt hook did not render');
    if (box) check(box.width >= 390, `Our Work desktop receipt is still too small: ${box.width}`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Our Work desktop horizontal overflow: ${overflow}`);
    await page.screenshot({ path: out + '/our-work-desktop.png', fullPage: true });
    await page.close();
  }

  // Home: the Open sign should use the continuous slower cadence.
  {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(base + '/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(900);
    await closeVisibleOverlays(page);
    const neon = page.locator('[style*="sc-warm"][style*="sc-neon"]').first();
    if (await neon.count()) {
      const anim = await neon.evaluate(el => { const s=getComputedStyle(el); return {name:s.animationName,duration:s.animationDuration,iteration:s.animationIterationCount}; });
      check(anim.name.includes('sc-neon-sunday-final'), `Open sign missing final slow neon animation: ${anim.name}`);
      check(anim.duration.includes('8.4s'), `Open sign neon cadence is not 8.4s: ${anim.duration}`);
      check(anim.iteration.includes('infinite'), `Open sign is not continuous: ${anim.iteration}`);
    } else {
      failures.push('Open sign animated element not found');
    }
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    check(overflow <= 1, `Home mobile horizontal overflow: ${overflow}`);
    await page.screenshot({ path: out + '/home-mobile.png', fullPage: true });
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
console.log('Targeted WebKit QA passed.');
