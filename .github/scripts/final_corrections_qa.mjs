import { webkit } from 'playwright';
import fs from 'node:fs';

const outDir = '/tmp/sunday-final-qa';
fs.mkdirSync(outDir, { recursive: true });

const browser = await webkit.launch();
const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
const base = 'http://127.0.0.1:4173';

async function waitForImages(page, route) {
  await page.waitForFunction(() => Array.from(document.images).every((img) => img.loading !== 'lazy'), null, { timeout: 15000 });
  await page.waitForFunction(() => Array.from(document.images).every((img) => img.complete && img.naturalWidth > 0), null, { timeout: 60000 });
  const state = await page.evaluate(() => ({
    total: document.images.length,
    lazy: Array.from(document.images).filter((img) => img.loading === 'lazy').length,
    broken: Array.from(document.images).filter((img) => !img.complete || !img.naturalWidth).map((img) => img.getAttribute('src')),
  }));
  if (state.lazy || state.broken.length) throw new Error(`${route}: image readiness failed ${JSON.stringify(state)}`);
}

async function load(page, route) {
  await page.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
  await waitForImages(page, route);
}

const routes = [
  '/', '/about/', '/services/', '/our-work/', '/join-our-team/', '/sunday-school/', '/contact/',
  '/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/', '/our-work/pizzeria-coco/', '/our-work/folake/'
];

for (const route of routes) {
  const page = await context.newPage();
  await load(page, route);
  const lazyAttrCount = await page.locator('img[loading="lazy"]').count();
  if (lazyAttrCount !== 0) throw new Error(`${route}: lazy image attributes remain at runtime`);
  await page.close();
}

const home = await context.newPage();
await load(home, '/');

const hero = await home.evaluate(() => {
  const section = document.querySelector('[data-screen-hero="home"]');
  const img = section?.querySelector(':scope > img[data-sunday-hero-img="true"]');
  if (!section || !img) return null;
  const cs = getComputedStyle(img);
  const r = img.getBoundingClientRect();
  return {
    grid: section.getAttribute('data-sunday-grid-hero'),
    position: cs.position,
    display: cs.display,
    visibility: cs.visibility,
    opacity: cs.opacity,
    width: r.width,
    height: r.height,
    naturalWidth: img.naturalWidth,
  };
});
if (!hero || hero.grid !== 'true' || hero.position !== 'relative' || hero.visibility !== 'visible' || Number(hero.opacity) !== 1 || hero.height < 500 || hero.naturalWidth < 1) {
  throw new Error(`Homepage hero is not capture-stable: ${JSON.stringify(hero)}`);
}

const recentMotion = await home.evaluate(() => {
  const vision = document.querySelector('#vision');
  const pinyon = vision?.querySelector('[style*="Pinyon Script"]');
  return {
    sectionAnimations: vision ? vision.getAnimations().length : -1,
    pinyonAnimations: pinyon ? pinyon.getAnimations().length : -1,
  };
});
if (recentMotion.sectionAnimations !== 0 || recentMotion.pinyonAnimations !== 0) {
  throw new Error(`Recent section/text motion is still active: ${JSON.stringify(recentMotion)}`);
}

const sign = await home.evaluate(() => {
  const neon = document.querySelector('[data-sign] p[aria-hidden][style*="Pinyon Script"]');
  const hanger = document.querySelector('[data-sign] > div[style*="transform-origin"]');
  if (!neon || !hanger) return null;
  const n = getComputedStyle(neon);
  const h = getComputedStyle(hanger);
  return {
    neonName: n.animationName,
    neonCount: n.animationIterationCount,
    hangerName: h.animationName,
    hangerCount: h.animationIterationCount,
  };
});
if (!sign || !sign.neonName.includes('sc-neon-sunday-final') || sign.neonCount !== 'infinite' || !sign.hangerName.includes('sc-sway-sunday-continuous') || sign.hangerCount !== 'infinite') {
  throw new Error(`OPEN sign loop is wrong: ${JSON.stringify(sign)}`);
}

await home.screenshot({ path: `${outDir}/home-full.png`, fullPage: true });

// Reservation receipt hierarchy.
await home.evaluate(() => { try { sessionStorage.removeItem('sunday-reservation-seen'); } catch (e) {} });
await home.reload({ waitUntil: 'networkidle' });
const reservation = home.locator('[aria-label="The Sunday Reservation"]');
await reservation.waitFor({ state: 'visible', timeout: 5000 });
const reservationState = await reservation.evaluate((dialog) => {
  const h2 = dialog.querySelector('h2');
  const support = h2?.nextElementSibling;
  const fine = dialog.querySelector('[data-res-fineprint]');
  return {
    supportFamily: support ? getComputedStyle(support).fontFamily : '',
    supportSize: support ? parseFloat(getComputedStyle(support).fontSize) : 999,
    fineSize: fine ? parseFloat(getComputedStyle(fine).fontSize) : 999,
  };
});
if (!reservationState.supportFamily.includes('Inter Tight') || reservationState.supportSize > 10 || reservationState.fineSize > 6.2) {
  throw new Error(`Reservation receipt hierarchy is wrong: ${JSON.stringify(reservationState)}`);
}
await reservation.screenshot({ path: `${outDir}/reservation-mobile.png` });
await reservation.getByRole('button', { name: 'Close' }).click();

// Project inquiry hierarchy and subtle overlap.
await home.evaluate(() => window.dispatchEvent(new Event('sunday:open-inquiry')));
const inquiry = home.locator('[aria-label="Project inquiry"]');
await inquiry.waitFor({ state: 'visible', timeout: 5000 });
const inquiryState = await inquiry.evaluate((dialog) => {
  const kicker = dialog.querySelector('[data-inquiry-kicker]');
  const h2 = kicker?.nextElementSibling;
  if (!kicker || !h2) return null;
  const k = getComputedStyle(kicker);
  const h = getComputedStyle(h2);
  const kr = kicker.getBoundingClientRect();
  const hr = h2.getBoundingClientRect();
  return {
    kickerText: kicker.textContent.trim(),
    kickerFamily: k.fontFamily,
    kickerSize: parseFloat(k.fontSize),
    kickerColor: k.color,
    headlineFamily: h.fontFamily,
    headlineSize: parseFloat(h.fontSize),
    overlap: kr.bottom - hr.top,
    dialogAnimation: getComputedStyle(dialog).animationName,
  };
});
if (!inquiryState || inquiryState.kickerText !== 'A Seat At Our Table' || !inquiryState.kickerFamily.includes('Pinyon Script') || inquiryState.kickerSize > 31 || !inquiryState.headlineFamily.includes('Playfair Display') || inquiryState.headlineSize > 28 || inquiryState.overlap < 0 || inquiryState.overlap > 8 || inquiryState.dialogAnimation !== 'none') {
  throw new Error(`Inquiry hierarchy is wrong: ${JSON.stringify(inquiryState)}`);
}
await inquiry.screenshot({ path: `${outDir}/inquiry-mobile.png` });
await inquiry.getByRole('button', { name: 'Close' }).click();
await home.close();

// Join Our Team full details must be a fixed popup on mobile, never inline.
const join = await context.newPage();
await load(join, '/join-our-team/');
const firstFront = join.locator('[data-program-cards] article').first().locator('button').first();
await firstFront.click();
await join.waitForTimeout(1000);
const detailsButton = join.getByRole('button', { name: 'View Full Details' }).first();
await detailsButton.click();
const fellows = join.getByRole('dialog', { name: 'The Fellows Table' });
await fellows.waitFor({ state: 'visible', timeout: 5000 });
const modalState = await fellows.evaluate((dialog) => {
  const presentation = dialog.parentElement;
  const ps = presentation ? getComputedStyle(presentation) : null;
  return {
    ariaModal: dialog.getAttribute('aria-modal'),
    position: ps?.position,
    insetTop: ps?.top,
    zIndex: ps?.zIndex,
    backdrop: ps?.backgroundColor,
    dialogMaxHeight: getComputedStyle(dialog).maxHeight,
  };
});
if (modalState.ariaModal !== 'true' || modalState.position !== 'fixed' || modalState.zIndex === 'auto' || modalState.backdrop === 'rgba(0, 0, 0, 0)') {
  throw new Error(`Join Our Team details are not a popup: ${JSON.stringify(modalState)}`);
}
await join.screenshot({ path: `${outDir}/join-program-popup.png`, fullPage: false });
await join.close();

await browser.close();
console.log('Final corrections WebKit QA passed.');
