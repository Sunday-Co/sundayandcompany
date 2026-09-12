import { webkit } from 'playwright';
import fs from 'node:fs';

const base = 'http://127.0.0.1:4173';
const outDir = '/tmp/sunday-source-truth-qa';
fs.mkdirSync(outDir, { recursive: true });
function assert(c, m) { if (!c) throw new Error(m); }
async function ready(page, route) {
  await page.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForFunction(() => Array.from(document.images).every((img) => img.complete && img.naturalWidth > 0), null, { timeout: 60000 });
}

const browser = await webkit.launch();

// Desktop Our Work at wide desktop: phrase must be one line and receipt must not overlap it.
const wide = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const work = await wide.newPage();
await ready(work, '/our-work/');
const wideState = await work.evaluate(() => {
  const title = document.querySelector('#work-title');
  const phrase = title?.querySelector('span');
  const receipt = document.querySelector('[data-work-receipt]');
  const firstReveal = document.querySelector('[data-reveal]');
  if (!title || !phrase || !receipt || !firstReveal) return null;
  const p = phrase.getBoundingClientRect();
  const r = receipt.getBoundingClientRect();
  const rs = getComputedStyle(firstReveal);
  const ps = getComputedStyle(phrase);
  return {
    phraseWhiteSpace: ps.whiteSpace,
    phraseTop: p.top,
    phraseBottom: p.bottom,
    phraseLeft: p.left,
    phraseRight: p.right,
    receiptLeft: r.left,
    receiptTop: r.top,
    revealOpacity: rs.opacity,
    revealTransform: rs.transform,
    revealTransition: rs.transitionDuration,
  };
});
assert(wideState, 'Our Work wide desktop state missing');
assert(wideState.phraseWhiteSpace === 'nowrap', `A Point Of View is not nowrap: ${JSON.stringify(wideState)}`);
assert(wideState.phraseRight < wideState.receiptLeft || wideState.receiptTop > wideState.phraseBottom, `Bill of Work overlaps headline: ${JSON.stringify(wideState)}`);
assert(wideState.revealOpacity === '1' && wideState.revealTransform === 'none' && wideState.revealTransition === '0s', `Recent Our Work reveal motion remains: ${JSON.stringify(wideState)}`);
await work.screenshot({ path: `${outDir}/our-work-wide.png`, fullPage: false });
await work.close();

// Mid desktop must preserve single-line phrase even when receipt stacks below.
const mid = await browser.newContext({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 1 });
const midWork = await mid.newPage();
await ready(midWork, '/our-work/');
const midState = await midWork.evaluate(() => {
  const phrase = document.querySelector('#work-title span');
  const receipt = document.querySelector('[data-work-receipt]');
  if (!phrase || !receipt) return null;
  const p = phrase.getBoundingClientRect();
  const r = receipt.getBoundingClientRect();
  return { whiteSpace: getComputedStyle(phrase).whiteSpace, phraseBottom: p.bottom, receiptTop: r.top };
});
assert(midState?.whiteSpace === 'nowrap', `Mid-desktop phrase wraps: ${JSON.stringify(midState)}`);
assert(midState.receiptTop > midState.phraseBottom, `Mid-desktop receipt does not clear headline: ${JSON.stringify(midState)}`);
await midWork.screenshot({ path: `${outDir}/our-work-mid.png`, fullPage: false });
await midWork.close();

// Mobile homepage: close auto reservation, verify Inquiry source hierarchy and bottom padding.
const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
const home = await mobile.newPage();
await ready(home, '/');
const autoRes = home.locator('[aria-label="The Sunday Reservation"]');
if (await autoRes.isVisible()) await autoRes.getByRole('button', { name: 'Close' }).evaluate((el) => el.click());
await home.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
const inquiry = home.locator('[aria-label="Project inquiry"]');
await inquiry.waitFor({ state: 'visible', timeout: 5000 });
const inquiryState = await inquiry.evaluate((dialog) => {
  const kicker = dialog.querySelector('[data-inquiry-kicker]');
  const inner = dialog.firstElementChild;
  if (!kicker || !inner) return null;
  const k = getComputedStyle(kicker);
  const i = getComputedStyle(inner);
  return { family: k.fontFamily, size: parseFloat(k.fontSize), weight: k.fontWeight, bottom: parseFloat(i.paddingBottom), transform: k.textTransform };
});
assert(inquiryState?.family.includes('Inter Tight'), `Inquiry kicker is not Inter Tight: ${JSON.stringify(inquiryState)}`);
assert(inquiryState.size >= 10 && inquiryState.size <= 12.5, `Inquiry kicker size wrong: ${JSON.stringify(inquiryState)}`);
assert(Number(inquiryState.weight) >= 400 && inquiryState.bottom >= 46, `Inquiry hierarchy/padding wrong: ${JSON.stringify(inquiryState)}`);
await inquiry.screenshot({ path: `${outDir}/inquiry-mobile.png` });
await inquiry.getByRole('button', { name: 'Close' }).evaluate((el) => el.click());

// Footer email must carry stronger explicit weight.
await home.locator('footer').scrollIntoViewIfNeeded();
const mail = await home.locator('footer a[href^="mailto:"]').evaluate((el) => ({ weight: getComputedStyle(el).fontWeight, size: parseFloat(getComputedStyle(el).fontSize) }));
assert(Number(mail.weight) >= 400 && mail.size >= 12, `Footer email still too light: ${JSON.stringify(mail)}`);

// Reservation desktop fine print should be small but readable and support line in Inter Tight.
const deskHome = await wide.newPage();
await ready(deskHome, '/');
await deskHome.evaluate(() => { try { sessionStorage.removeItem('sunday-reservation-seen'); } catch (e) {} });
await deskHome.reload({ waitUntil: 'networkidle' });
const res = deskHome.locator('[aria-label="The Sunday Reservation"]');
await res.waitFor({ state: 'visible', timeout: 5000 });
const resState = await res.evaluate((dialog) => {
  const h2 = dialog.querySelector('h2');
  const support = h2?.nextElementSibling;
  const fine = dialog.querySelector('[data-res-fineprint]');
  return {
    fine: fine ? parseFloat(getComputedStyle(fine).fontSize) : 0,
    supportFamily: support ? getComputedStyle(support).fontFamily : '',
  };
});
assert(resState.fine >= 8.5 && resState.fine <= 10.5, `Desktop Reservation fine print unreadable: ${JSON.stringify(resState)}`);
assert(resState.supportFamily.includes('Inter Tight'), `Reservation support copy not Inter Tight: ${JSON.stringify(resState)}`);
await res.screenshot({ path: `${outDir}/reservation-desktop.png` });
await deskHome.close();

// No-JS capture path: hero img must be valid, in normal layout and visible.
const noJsCtx = await browser.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false, deviceScaleFactor: 1 });
const noJs = await noJsCtx.newPage();
await noJs.goto(base + '/', { waitUntil: 'load', timeout: 60000 });
const heroState = await noJs.evaluate(() => {
  const img = document.querySelector('section#top img[data-sunday-static-hero="true"]');
  if (!img) return null;
  const cs = getComputedStyle(img); const r = img.getBoundingClientRect();
  return { position: cs.position, display: cs.display, visibility: cs.visibility, opacity: cs.opacity, width: r.width, height: r.height, naturalWidth: img.naturalWidth };
});
assert(heroState && heroState.position === 'relative' && heroState.display !== 'none' && heroState.visibility === 'visible' && Number(heroState.opacity) === 1 && heroState.width > 300 && heroState.height > 500 && heroState.naturalWidth > 0, `Hero is not source-capture-safe: ${JSON.stringify(heroState)}`);
await noJs.screenshot({ path: `${outDir}/home-full-nojs.png`, fullPage: true });
await noJs.close();
await noJsCtx.close();

await home.close();
await mobile.close();
await mid.close();
await wide.close();
await browser.close();
console.log('Source-truth regression QA passed');
