import { webkit } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base = process.env.QA_BASE_URL || 'http://127.0.0.1:4173';
const outRoot = path.resolve('qa-artifacts');

const routes = [
  '/',
  '/about/',
  '/services/',
  '/our-work/',
  '/our-work/pizzeria-coco/',
  '/our-work/petti-pathways/',
  '/our-work/luckys-cafe-bakery/',
  '/our-work/folake/',
  '/contact/',
  '/join-our-team/',
  '/sunday-school/',
  '/privacy-policy/',
  '/terms-and-conditions/',
  '/cookie-policy/',
  '/accessibility/',
  '/404.html',
];

const profiles = [
  { name: 'desktop', viewport: { width: 1440, height: 1000 } },
  { name: 'mobile', viewport: { width: 390, height: 844 }, isMobile: true },
];

function slug(route) {
  if (route === '/') return 'home';
  return route.replace(/^\//, '').replace(/\/$/, '').replaceAll('/', '--').replace(/\.html$/, '') || 'home';
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function navigate(page, route) {
  // Some case-study pages contain large media. WebKit can keep the document's
  // load lifecycle open while those files stream even though the rendered page
  // is already ready. Commit + rendered-text readiness tests the site without
  // treating a slow below-the-fold asset as a page failure.
  const response = await page.goto(base + route, { waitUntil: 'commit', timeout: 30000 });
  await page.waitForFunction(() => document.body && document.body.innerText.trim().length > 20, null, { timeout: 15000 });
  await page.waitForFunction(() => !!document.querySelector('h1'), null, { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(900);
  return response;
}

async function basicRouteCheck(page, profile, route, report) {
  const response = await navigate(page, route);
  assert(response && response.status() < 400, `${profile.name} ${route}: HTTP ${response?.status()}`);

  const metrics = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
    viewportWidth: window.innerWidth,
    h1: document.querySelector('h1')?.textContent?.trim() || '',
  }));
  const widest = Math.max(metrics.scrollWidth, metrics.bodyScrollWidth);
  assert(widest <= metrics.viewportWidth + 4, `${profile.name} ${route}: horizontal overflow ${widest}px > ${metrics.viewportWidth}px`);

  const dir = path.join(outRoot, profile.name);
  await fs.mkdir(dir, { recursive: true });
  await page.screenshot({ path: path.join(dir, `${slug(route)}.png`), fullPage: true });

  report.push({ profile: profile.name, route, status: response.status(), ...metrics });
}

async function checkHomeHero(page, profile, report) {
  await navigate(page, '/');
  const hero = await page.evaluate(() => {
    const el = document.querySelector('section#top[data-screen-hero="home"]');
    const img = el?.querySelector('img');
    if (!el) return null;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return {
      height: r.height,
      backgroundImage: cs.backgroundImage,
      backgroundColor: cs.backgroundColor,
      imageNaturalWidth: img?.naturalWidth || 0,
      imagePosition: img ? getComputedStyle(img).position : '',
    };
  });
  assert(hero, `${profile.name}: homepage hero not found`);
  assert(hero.height >= 650, `${profile.name}: homepage hero unexpectedly short (${hero.height})`);
  assert(hero.backgroundImage.includes('hero-landscape.jpg'), `${profile.name}: homepage fallback background missing`);
  assert(hero.imageNaturalWidth > 0, `${profile.name}: homepage hero image failed to load`);
  assert(hero.imagePosition === 'absolute', `${profile.name}: homepage hero image is not absolute`);
  report.push({ profile: profile.name, check: 'home-hero', ...hero });
}

async function checkInquiry(page, profile, report) {
  await navigate(page, '/');
  await page.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
  const dialog = page.locator('[aria-label="Project inquiry"]');
  await dialog.waitFor({ state: 'visible', timeout: 5000 });
  const data = await dialog.evaluate((el) => {
    const r = el.getBoundingClientRect();
    const text = (el.textContent || '').replace(/\s+/g, ' ').trim();
    return {
      left: r.left, top: r.top, width: r.width, height: r.height,
      vw: window.innerWidth, vh: window.innerHeight,
      text,
      overflowY: getComputedStyle(el).overflowY,
    };
  });
  assert(data.text.includes('01 Project Basics'), `${profile.name}: inquiry step 1 label missing`);
  assert(data.text.includes('02 Timing & Budget'), `${profile.name}: inquiry step 2 label missing`);
  assert(data.text.includes('03 Project Scope'), `${profile.name}: inquiry step 3 label missing`);
  const cx = data.left + data.width / 2;
  const cy = data.top + Math.min(data.height, data.vh) / 2;
  assert(Math.abs(cx - data.vw / 2) <= 20, `${profile.name}: inquiry not horizontally centered`);
  if (profile.name === 'desktop') assert(Math.abs(cy - data.vh / 2) <= 70, `${profile.name}: inquiry not vertically centered`);
  await page.screenshot({ path: path.join(outRoot, profile.name, 'home--inquiry.png'), fullPage: false });
  report.push({ profile: profile.name, check: 'inquiry', ...data, text: undefined });
}

async function checkMenu(page, profile, report) {
  if (!profile.isMobile) return;
  await navigate(page, '/');
  await page.locator('[aria-label="Open menu"]').click();
  const aside = page.locator('aside[aria-label="Sunday & Company navigation"]');
  await aside.waitFor({ state: 'visible' });
  await page.waitForFunction(() => document.querySelector('aside[aria-label="Sunday & Company navigation"]')?.getAttribute('data-sheet-state') === 'open');
  const data = await aside.evaluate(el => ({
    state: el.getAttribute('data-sheet-state'),
    transform: getComputedStyle(el).transform,
    width: el.getBoundingClientRect().width,
  }));
  assert(data.state === 'open', 'mobile menu state did not become open');
  assert(data.width > 250 && data.width < profile.viewport.width, `mobile menu width looks wrong (${data.width})`);
  await page.screenshot({ path: path.join(outRoot, profile.name, 'home--menu.png'), fullPage: false });
  report.push({ profile: profile.name, check: 'mobile-menu', ...data });
}

async function checkServices(page, profile, report) {
  await navigate(page, '/services/');
  const first = page.locator('#service-menu button[aria-expanded]').first();
  await first.click();
  await page.waitForTimeout(300);
  assert(await first.getAttribute('aria-expanded') === 'true', `${profile.name}: first service did not expand`);
  const body = page.locator('[data-service-body]').first();
  assert(await body.isVisible(), `${profile.name}: service body not visible after expand`);
  const bodyData = await body.evaluate(el => ({ display: getComputedStyle(el).display, animationName: getComputedStyle(el).animationName }));
  assert(bodyData.animationName.includes('sunday-accordion-in'), `${profile.name}: service content reveal animation missing`);
  await body.screenshot({ path: path.join(outRoot, profile.name, 'services--expanded.png') });
  report.push({ profile: profile.name, check: 'services-accordion', ...bodyData });
}

async function checkJoinProgram(page, profile, report) {
  if (!profile.isMobile) return;
  await navigate(page, '/join-our-team/');
  const flip = page.locator('button[aria-label="Flip The Fellows Table card"]');
  await flip.click();
  await page.waitForTimeout(850);
  const details = page.getByRole('button', { name: 'View Full Details' }).first();
  await details.click();
  await page.waitForTimeout(250);
  const dialog = page.locator('[role="dialog"][aria-label="The Fellows Table"]');
  await dialog.waitFor({ state: 'visible' });
  const data = await dialog.evaluate(el => ({
    position: getComputedStyle(el.parentElement).position,
    parentOverflowY: getComputedStyle(el.parentElement).overflowY,
    overflowY: getComputedStyle(el).overflowY,
    maxHeight: getComputedStyle(el).maxHeight,
  }));
  assert(data.position === 'static', `mobile program detail parent is ${data.position}, expected static`);
  assert(data.overflowY === 'visible', `mobile program detail still has nested scrolling (${data.overflowY})`);
  await dialog.screenshot({ path: path.join(outRoot, profile.name, 'join--fellows-details.png') });
  report.push({ profile: profile.name, check: 'join-program-mobile', ...data });
}

const browser = await webkit.launch();
const report = [];
const failures = [];

for (const profile of profiles) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await context.addInitScript(() => {
    try { sessionStorage.setItem('sunday-reservation-seen', 'true'); } catch (_) {}
  });
  const page = await context.newPage();

  for (const route of routes) {
    try {
      await basicRouteCheck(page, profile, route, report);
      console.log(`PASS ${profile.name} ${route}`);
    } catch (err) {
      failures.push(String(err?.message || err));
      console.error(`FAIL ${profile.name} ${route}:`, err?.message || err);
      await page.goto('about:blank', { waitUntil: 'commit' }).catch(() => {});
    }
  }

  for (const fn of [checkHomeHero, checkInquiry, checkMenu, checkServices, checkJoinProgram]) {
    try {
      await fn(page, profile, report);
      console.log(`PASS ${profile.name} ${fn.name}`);
    } catch (err) {
      failures.push(`${profile.name} ${fn.name}: ${String(err?.message || err)}`);
      console.error(`FAIL ${profile.name} ${fn.name}:`, err?.message || err);
    }
  }

  await context.close();
}

await browser.close();
await fs.mkdir(outRoot, { recursive: true });
await fs.writeFile(path.join(outRoot, 'report.json'), JSON.stringify({ report, failures }, null, 2));

if (failures.length) {
  console.error('\nWebKit QA failures:');
  failures.forEach(f => console.error('- ' + f));
  process.exit(1);
}

console.log(`\nWebKit QA passed: ${report.length} checks.`);
