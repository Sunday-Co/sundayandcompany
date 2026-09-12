import { webkit } from 'playwright';
import fs from 'node:fs';

const outDir = '/tmp/sunday-consolidated-qa';
fs.mkdirSync(outDir, { recursive: true });
const base = 'http://127.0.0.1:4173';

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function waitForImages(page, route) {
  await page.waitForFunction(() => Array.from(document.images).every((img) => img.loading !== 'lazy'), null, { timeout: 45000 });
  await page.waitForFunction(() => Array.from(document.images).every((img) => img.complete && img.naturalWidth > 0), null, { timeout: 60000 });
  const state = await page.evaluate(() => ({
    total: document.images.length,
    lazy: Array.from(document.images).filter((img) => img.loading === 'lazy').length,
    broken: Array.from(document.images).filter((img) => !img.complete || !img.naturalWidth).map((img) => img.getAttribute('src')),
  }));
  assert(state.lazy === 0 && state.broken.length === 0, `${route}: image readiness failed ${JSON.stringify(state)}`);
}

async function load(page, route) {
  await page.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
  await waitForImages(page, route);
}

const browser = await webkit.launch();
const mobileContext = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });

const routes = [
  '/', '/about/', '/services/', '/our-work/', '/join-our-team/', '/sunday-school/', '/contact/',
  '/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/', '/our-work/pizzeria-coco/', '/our-work/folake/'
];

for (const route of routes) {
  const page = await mobileContext.newPage();
  await load(page, route);
  const state = await page.evaluate(() => ({
    lazyAttrs: document.querySelectorAll('img[loading="lazy"]').length,
    broken: Array.from(document.images).filter((img) => !img.complete || !img.naturalWidth).length,
  }));
  assert(state.lazyAttrs === 0 && state.broken === 0, `${route}: capture images are not source-ready ${JSON.stringify(state)}`);
  await page.close();
}

// Homepage: recent correction-layer motion must be gone, but original sign motion stays.
const home = await mobileContext.newPage();
await load(home, '/');

const motionState = await home.evaluate(() => {
  const step = document.querySelector('form[data-inq] [data-step-panel]');
  const service = document.querySelector('[data-service-body]');
  const pinyon = document.querySelector('#vision [style*="Pinyon Script"]');
  const arrow = document.querySelector('a[href="/contact"] svg');
  return {
    stepAnimation: step ? getComputedStyle(step).animationName : 'missing',
    serviceAnimation: service ? getComputedStyle(service).animationName : 'missing',
    pinyonAnimation: pinyon ? getComputedStyle(pinyon).animationName : 'missing',
    pinyonTransition: pinyon ? getComputedStyle(pinyon).transitionDuration : 'missing',
    arrowTransition: arrow ? getComputedStyle(arrow).transitionDuration : 'missing',
  };
});
assert(motionState.stepAnimation === 'none' || motionState.stepAnimation === 'missing', `Form-step correction motion remains: ${JSON.stringify(motionState)}`);
assert(motionState.serviceAnimation === 'none' || motionState.serviceAnimation === 'missing', `Service correction motion remains: ${JSON.stringify(motionState)}`);
assert(motionState.pinyonAnimation === 'none', `Pinyon correction motion remains: ${JSON.stringify(motionState)}`);
assert(motionState.pinyonTransition === '0s', `Pinyon correction transition remains: ${JSON.stringify(motionState)}`);
assert(motionState.arrowTransition === '0s', `Recent CTA arrow motion remains: ${JSON.stringify(motionState)}`);

// OPEN sign: on entry, original warm-up + damped swing must be present, then loop forever.
const signEl = home.locator('[data-sign]');
await signEl.scrollIntoViewIfNeeded();
await home.waitForTimeout(250);
const signEntry = await home.evaluate(() => {
  const neon = document.querySelector('[data-sign] p[aria-hidden][style*="Pinyon Script"]');
  const hanger = document.querySelector('[data-sign] > div[style*="transform-origin"]');
  if (!neon || !hanger) return null;
  const n = getComputedStyle(neon);
  const h = getComputedStyle(hanger);
  return {
    neonName: n.animationName,
    neonCount: n.animationIterationCount,
    neonDelay: n.animationDelay,
    hangerName: h.animationName,
    hangerCount: h.animationIterationCount,
    hangerDelay: h.animationDelay,
  };
});
assert(signEntry, 'OPEN sign elements are missing');
assert(signEntry.neonName.includes('sc-warm') && signEntry.neonName.includes('sc-neon'), `Original OPEN warm-up was not restored: ${JSON.stringify(signEntry)}`);
assert(signEntry.hangerName.includes('sc-rock') && signEntry.hangerName.includes('sc-sway'), `Original OPEN entrance swing was not restored: ${JSON.stringify(signEntry)}`);
assert(signEntry.neonCount.includes('infinite') && signEntry.hangerCount.includes('infinite'), `OPEN sign does not settle into infinite motion: ${JSON.stringify(signEntry)}`);

// Confirm the looping animation still exists after the one-shot swing has settled.
await home.waitForTimeout(6100);
const signSettled = await home.evaluate(() => {
  const neon = document.querySelector('[data-sign] p[aria-hidden][style*="Pinyon Script"]');
  const hanger = document.querySelector('[data-sign] > div[style*="transform-origin"]');
  if (!neon || !hanger) return null;
  const n = getComputedStyle(neon);
  const h = getComputedStyle(hanger);
  return { neonName: n.animationName, neonCount: n.animationIterationCount, hangerName: h.animationName, hangerCount: h.animationIterationCount };
});
assert(signSettled?.neonName.includes('sc-neon') && signSettled?.neonCount.includes('infinite'), `OPEN neon loop stopped: ${JSON.stringify(signSettled)}`);
assert(signSettled?.hangerName.includes('sc-sway') && signSettled?.hangerCount.includes('infinite'), `OPEN sway loop stopped: ${JSON.stringify(signSettled)}`);

// Project Inquiry mobile: rose Inter Tight eyebrow, Playfair headline, original modal-in, bottom air.
await home.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
const inquiry = home.locator('[aria-label="Project inquiry"]');
await inquiry.waitFor({ state: 'visible', timeout: 5000 });
const inquiryMobile = await inquiry.evaluate((dialog) => {
  const kicker = dialog.querySelector('[data-inquiry-kicker]');
  const h2 = kicker?.nextElementSibling;
  const inner = dialog.firstElementChild;
  if (!kicker || !h2 || !inner) return null;
  const k = getComputedStyle(kicker);
  const h = getComputedStyle(h2);
  const i = getComputedStyle(inner);
  return {
    kickerText: kicker.textContent.trim(),
    kickerFamily: k.fontFamily,
    kickerSize: parseFloat(k.fontSize),
    kickerColor: k.color,
    kickerTransform: k.textTransform,
    headlineFamily: h.fontFamily,
    headlineSize: parseFloat(h.fontSize),
    paddingBottom: parseFloat(i.paddingBottom),
    modalAnimation: getComputedStyle(dialog).animationName,
  };
});
assert(inquiryMobile, 'Project Inquiry mobile state missing');
assert(inquiryMobile.kickerFamily.includes('Inter Tight'), `Inquiry eyebrow is not secondary font: ${JSON.stringify(inquiryMobile)}`);
assert(inquiryMobile.kickerSize >= 10 && inquiryMobile.kickerSize <= 12.5, `Inquiry eyebrow size is wrong: ${JSON.stringify(inquiryMobile)}`);
assert(inquiryMobile.kickerColor === 'rgb(172, 116, 108)', `Inquiry eyebrow is not rose: ${JSON.stringify(inquiryMobile)}`);
assert(inquiryMobile.headlineFamily.includes('Playfair Display'), `Inquiry headline is not Playfair: ${JSON.stringify(inquiryMobile)}`);
assert(inquiryMobile.paddingBottom >= 40, `Inquiry bottom padding is too tight: ${JSON.stringify(inquiryMobile)}`);
assert(inquiryMobile.modalAnimation === 'sunday-modal-in', `Original inquiry modal animation was removed: ${JSON.stringify(inquiryMobile)}`);
await inquiry.screenshot({ path: `${outDir}/inquiry-mobile.png` });
await inquiry.getByRole('button', { name: 'Close' }).click();

// Reservation mobile: secondary support font and small but readable fine print.
await home.evaluate(() => { try { sessionStorage.removeItem('sunday-reservation-seen'); } catch (e) {} });
await home.reload({ waitUntil: 'networkidle' });
await waitForImages(home, '/');
const reservation = home.locator('[aria-label="The Sunday Reservation"]');
await reservation.waitFor({ state: 'visible', timeout: 5000 });
const reservationMobile = await reservation.evaluate((dialog) => {
  const h2 = dialog.querySelector('h2');
  const support = h2?.nextElementSibling;
  const fine = dialog.querySelector('[data-res-fineprint]');
  return {
    supportFamily: support ? getComputedStyle(support).fontFamily : '',
    supportSize: support ? parseFloat(getComputedStyle(support).fontSize) : 999,
    fineSize: fine ? parseFloat(getComputedStyle(fine).fontSize) : 0,
    modalAnimation: getComputedStyle(dialog).animationName,
  };
});
assert(reservationMobile.supportFamily.includes('Inter Tight'), `Reservation support copy is not secondary font: ${JSON.stringify(reservationMobile)}`);
assert(reservationMobile.fineSize >= 6.8 && reservationMobile.fineSize <= 8, `Mobile Reservation fine print is not readable/secondary: ${JSON.stringify(reservationMobile)}`);
assert(reservationMobile.modalAnimation === 'sunday-modal-in', `Original Reservation modal animation was removed: ${JSON.stringify(reservationMobile)}`);
await reservation.screenshot({ path: `${outDir}/reservation-mobile.png` });
await reservation.getByRole('button', { name: 'Close' }).click();

// Footer email must visually carry the intended body weight.
await home.locator('footer').scrollIntoViewIfNeeded();
const footerMail = await home.locator('footer a[href^="mailto:"]').evaluate((el) => {
  const cs = getComputedStyle(el);
  return { family: cs.fontFamily, size: parseFloat(cs.fontSize), weight: cs.fontWeight, opacity: cs.opacity };
});
assert(footerMail.family.includes('Inter Tight') && footerMail.size >= 12 && Number(footerMail.weight) >= 400 && Number(footerMail.opacity) === 1, `Footer email is still optically light: ${JSON.stringify(footerMail)}`);
await home.screenshot({ path: `${outDir}/home-full.png`, fullPage: true });
await home.close();

// Join Our Team modal behavior + approved archive treatment must remain.
const join = await mobileContext.newPage();
await load(join, '/join-our-team/');
const firstArticle = join.locator('[data-program-cards] > article').first();
const firstFront = firstArticle.locator(':scope > div > button').first();
await firstFront.evaluate((el) => el.click());
await join.waitForTimeout(850);
const detailsButton = firstArticle.getByRole('button', { name: 'View Full Details' });
await detailsButton.waitFor({ state: 'visible', timeout: 5000 });
await detailsButton.evaluate((el) => el.click());
const fellows = join.getByRole('dialog', { name: 'The Fellows Table' });
await fellows.waitFor({ state: 'visible', timeout: 5000 });
const joinState = await fellows.evaluate((dialog) => {
  const presentation = dialog.parentElement;
  const ps = presentation ? getComputedStyle(presentation) : null;
  const ds = getComputedStyle(dialog);
  return {
    ariaModal: dialog.getAttribute('aria-modal'),
    presentationPosition: ps?.position,
    zIndex: ps?.zIndex,
    backgroundImage: ds.backgroundImage,
    boxShadow: ds.boxShadow,
  };
});
assert(joinState.ariaModal === 'true' && joinState.presentationPosition === 'fixed' && joinState.zIndex !== 'auto', `Join details are not a fixed popup: ${JSON.stringify(joinState)}`);
assert(joinState.backgroundImage.includes('linear-gradient') && joinState.boxShadow !== 'none', `Approved archive styling disappeared: ${JSON.stringify(joinState)}`);
await join.screenshot({ path: `${outDir}/join-program-popup.png` });
await join.close();

// JavaScript-disabled WebKit approximates Safari rebuilding a Full Page/PDF snapshot.
// The hero must remain an actual source-level image, not depend on runtime markers.
const noJsContext = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, javaScriptEnabled: false });
const noJs = await noJsContext.newPage();
await noJs.goto(base + '/', { waitUntil: 'load', timeout: 60000 });
const staticHero = await noJs.evaluate(() => {
  const hero = document.querySelector('section#top[data-screen-hero="home"]');
  const img = hero?.querySelector('img[data-sunday-static-hero="true"]');
  if (!hero || !img) return null;
  const cs = getComputedStyle(img);
  const r = img.getBoundingClientRect();
  return {
    position: cs.position,
    display: cs.display,
    visibility: cs.visibility,
    opacity: cs.opacity,
    width: r.width,
    height: r.height,
    naturalWidth: img.naturalWidth,
    naturalHeight: img.naturalHeight,
  };
});
assert(staticHero && staticHero.position === 'relative' && staticHero.display !== 'none' && staticHero.visibility === 'visible' && Number(staticHero.opacity) === 1 && staticHero.naturalWidth > 0 && staticHero.height > 500, `Static homepage hero is not capture-safe without JS: ${JSON.stringify(staticHero)}`);
await noJs.screenshot({ path: `${outDir}/home-full-nojs.png`, fullPage: true });
await noJs.emulateMedia({ media: 'print' });
const printHero = await noJs.evaluate(() => {
  const img = document.querySelector('section#top img[data-sunday-static-hero="true"]');
  if (!img) return null;
  const cs = getComputedStyle(img);
  return { display: cs.display, visibility: cs.visibility, opacity: cs.opacity, position: cs.position, naturalWidth: img.naturalWidth };
});
assert(printHero && printHero.display !== 'none' && printHero.visibility === 'visible' && Number(printHero.opacity) === 1 && printHero.position === 'relative' && printHero.naturalWidth > 0, `Print-media hero is not capture-safe: ${JSON.stringify(printHero)}`);
await noJs.screenshot({ path: `${outDir}/home-print-nojs.png`, fullPage: true });
await noJs.close();
await noJsContext.close();

// Desktop-specific hierarchy and Our Work clearance.
const desktopContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const desktopHome = await desktopContext.newPage();
await load(desktopHome, '/');
await desktopHome.evaluate(() => { try { sessionStorage.removeItem('sunday-reservation-seen'); } catch (e) {} });
await desktopHome.reload({ waitUntil: 'networkidle' });
await waitForImages(desktopHome, '/');
const desktopReservation = desktopHome.locator('[aria-label="The Sunday Reservation"]');
await desktopReservation.waitFor({ state: 'visible', timeout: 5000 });
const desktopFine = await desktopReservation.locator('[data-res-fineprint]').evaluate((el) => parseFloat(getComputedStyle(el).fontSize));
assert(desktopFine >= 8.5 && desktopFine <= 10.5, `Desktop Reservation fine print is still too small or too large: ${desktopFine}`);
await desktopReservation.screenshot({ path: `${outDir}/reservation-desktop.png` });
await desktopReservation.getByRole('button', { name: 'Close' }).click();

await desktopHome.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
const desktopInquiry = desktopHome.locator('[aria-label="Project inquiry"]');
await desktopInquiry.waitFor({ state: 'visible', timeout: 5000 });
const desktopInquiryState = await desktopInquiry.evaluate((dialog) => {
  const kicker = dialog.querySelector('[data-inquiry-kicker]');
  const inner = dialog.firstElementChild;
  return {
    kickerFamily: kicker ? getComputedStyle(kicker).fontFamily : '',
    kickerSize: kicker ? parseFloat(getComputedStyle(kicker).fontSize) : 999,
    paddingBottom: inner ? parseFloat(getComputedStyle(inner).paddingBottom) : 0,
    modalAnimation: getComputedStyle(dialog).animationName,
  };
});
assert(desktopInquiryState.kickerFamily.includes('Inter Tight') && desktopInquiryState.kickerSize <= 12.5 && desktopInquiryState.paddingBottom >= 40 && desktopInquiryState.modalAnimation === 'sunday-modal-in', `Desktop inquiry correction is wrong: ${JSON.stringify(desktopInquiryState)}`);
await desktopInquiry.screenshot({ path: `${outDir}/inquiry-desktop.png` });
await desktopHome.close();

const work = await desktopContext.newPage();
await load(work, '/our-work/');
const workState = await work.evaluate(() => {
  const title = document.querySelector('#work-title');
  const receipt = document.querySelector('[data-work-receipt]');
  if (!title || !receipt) return null;
  const tr = title.getBoundingClientRect();
  const rr = receipt.getBoundingClientRect();
  return {
    titleLeft: tr.left, titleRight: tr.right, titleWidth: tr.width,
    receiptLeft: rr.left, receiptRight: rr.right, receiptWidth: rr.width,
    gap: rr.left - tr.right,
    titleFontSize: parseFloat(getComputedStyle(title).fontSize),
  };
});
assert(workState, 'Our Work desktop hero elements missing');
assert(workState.receiptWidth >= 440, `Bill of Work was shrunk: ${JSON.stringify(workState)}`);
assert(workState.gap >= 24, `Bill of Work still overlaps/hides hero text: ${JSON.stringify(workState)}`);
assert(workState.titleFontSize >= 58, `Our Work headline was improperly shrunk: ${JSON.stringify(workState)}`);
await work.screenshot({ path: `${outDir}/our-work-desktop.png`, fullPage: false });
await work.close();
await desktopContext.close();

await mobileContext.close();
await browser.close();
console.log('Consolidated Sunday revision QA passed.');
