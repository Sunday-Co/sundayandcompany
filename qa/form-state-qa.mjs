import { webkit } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const base = 'http://127.0.0.1:4173';
const outRoot = path.resolve('form-qa-artifacts');
const profiles = [
  { name: 'desktop', viewport: { width: 1440, height: 1000 } },
  { name: 'mobile', viewport: { width: 390, height: 844 } },
];

function assert(v, msg) { if (!v) throw new Error(msg); }

async function mockForms(context) {
  await context.route('https://api.web3forms.com/submit', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    headers: { 'Access-Control-Allow-Origin': '*' },
    body: JSON.stringify({ success: true, message: 'QA mock success' }),
  }));
  await context.route('**/*.mp4', route => route.abort());
}

async function ready(page, route) {
  await page.goto(base + route, { waitUntil: 'commit', timeout: 30000 });
  await page.waitForFunction(() => document.body && document.body.innerText.trim().length > 20, null, { timeout: 15000 });
  await page.waitForTimeout(900);
}

async function screenshot(page, profile, name, locator = null) {
  const dir = path.join(outRoot, profile.name);
  await fs.mkdir(dir, { recursive: true });
  const file = path.join(dir, `${name}.png`);
  if (locator) await locator.screenshot({ path: file });
  else await page.screenshot({ path: file, fullPage: false });
}

async function testInquiry(browser, profile, report) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await context.addInitScript(() => sessionStorage.setItem('sunday-reservation-seen', 'true'));
  await mockForms(context);
  const page = await context.newPage();
  await ready(page, '/');
  await page.evaluate(() => window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
  const dialog = page.locator('[aria-label="Project inquiry"]');
  await dialog.waitFor({ state: 'visible' });
  await page.waitForTimeout(450);
  await screenshot(page, profile, 'inquiry-step-1');

  const form = dialog.locator('form[data-inq]');
  await form.locator('input[name="name"]').fill('QA Test');
  await form.locator('input[name="email"]').fill('qa@example.com');
  await form.locator('input[name="phone"]').fill('2025550199');
  await form.locator('input[name="business"]').fill('Sunday QA');
  await form.getByRole('button', { name: 'Next' }).click();
  await page.waitForTimeout(260);
  assert((await form.getAttribute('data-cur')) === '2', `${profile.name}: inquiry did not reach step 2`);
  await screenshot(page, profile, 'inquiry-step-2');

  await form.locator('input[name="budget"]').fill('2500');
  await form.getByRole('button', { name: 'Next' }).click();
  await page.waitForTimeout(260);
  assert((await form.getAttribute('data-cur')) === '3', `${profile.name}: inquiry did not reach step 3`);
  await screenshot(page, profile, 'inquiry-step-3');

  await form.locator('[role="checkbox"]').first().click();
  await form.locator('textarea[name="notes"]').fill('QA form-state verification only.');
  await form.locator('button[type="submit"]').click();
  await dialog.getByText('Your Inquiry Is In.', { exact: true }).last().waitFor({ state: 'visible', timeout: 5000 });
  await page.waitForTimeout(250);
  await screenshot(page, profile, 'inquiry-confirmation');

  report.push({ profile: profile.name, form: 'project-inquiry', states: ['step-1','step-2','step-3','confirmation'], pass: true });
  await context.close();
}

async function testReservation(browser, profile, report) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await mockForms(context);
  const page = await context.newPage();
  await ready(page, '/');
  const dialog = page.locator('[aria-label="The Sunday Reservation"]');
  await dialog.waitFor({ state: 'visible', timeout: 5000 });
  await page.waitForTimeout(400);
  const fine = dialog.locator('[data-res-fineprint]').first();
  const fineSize = await fine.evaluate(el => parseFloat(getComputedStyle(el).fontSize));
  if (profile.name === 'mobile') assert(fineSize <= 8.5, `mobile reservation fine print too large: ${fineSize}px`);
  await screenshot(page, profile, 'reservation-signup');

  await dialog.locator('input[name="email"]').fill('qa@example.com');
  await dialog.locator('form button[type="submit"]').click();
  await dialog.getByText('You’re On The List.').waitFor({ state: 'visible', timeout: 5000 });
  await page.waitForTimeout(250);
  await screenshot(page, profile, 'reservation-confirmation');
  report.push({ profile: profile.name, form: 'reservation-popup', states: ['signup','confirmation'], fineSize, pass: true });
  await context.close();
}

async function testFooterNewsletter(browser, profile, report) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await context.addInitScript(() => sessionStorage.setItem('sunday-reservation-seen', 'true'));
  await mockForms(context);
  const page = await context.newPage();
  await ready(page, '/');
  const section = page.locator('[aria-label="Newsletter"]');
  await section.scrollIntoViewIfNeeded();
  await section.locator('input[name="email"]').fill('qa@example.com');
  await screenshot(page, profile, 'footer-newsletter-signup', section);
  await section.locator('button[type="submit"]').click();
  await section.locator('[data-news-receipt]').waitFor({ state: 'visible', timeout: 5000 });
  await screenshot(page, profile, 'footer-newsletter-confirmation', section);
  report.push({ profile: profile.name, form: 'footer-newsletter', states: ['signup','confirmation'], pass: true });
  await context.close();
}

async function testContact(browser, profile, report) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await context.addInitScript(() => sessionStorage.setItem('sunday-reservation-seen', 'true'));
  await mockForms(context);
  const page = await context.newPage();
  await ready(page, '/contact/');
  const form = page.locator('[data-screen-label="Contact"] form[data-editorial-labels]').first();
  await form.scrollIntoViewIfNeeded();
  await form.locator('input[name="name"]').fill('QA Test');
  await form.locator('input[name="email"]').fill('qa@example.com');
  await form.locator('input[name="message_subject"]').fill('QA State Test');
  await form.locator('textarea[name="message"]').fill('This is intercepted and is not sent.');
  await screenshot(page, profile, 'contact-form', form);
  await form.locator('button[type="submit"]').click();
  const card = page.locator('[data-screen-label="Contact"]').getByText('Your Note Is Sent.');
  await card.waitFor({ state: 'visible', timeout: 5000 });
  await screenshot(page, profile, 'contact-confirmation', card.locator('xpath=..'));
  report.push({ profile: profile.name, form: 'contact', states: ['form','confirmation'], pass: true });
  await context.close();
}

async function testSundaySchool(browser, profile, report) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await context.addInitScript(() => sessionStorage.setItem('sunday-reservation-seen', 'true'));
  await mockForms(context);
  const page = await context.newPage();
  await ready(page, '/sunday-school/');
  const section = page.locator('#class-notes');
  await section.scrollIntoViewIfNeeded();
  await section.locator('#school-notes-email').fill('qa@example.com');
  await screenshot(page, profile, 'sunday-school-signup', section);
  await section.locator('button[type="submit"]').click();
  await section.getByText('You’re On The List.').waitFor({ state: 'visible', timeout: 5000 });
  await screenshot(page, profile, 'sunday-school-confirmation', section);
  report.push({ profile: profile.name, form: 'sunday-school', states: ['signup','confirmation'], pass: true });
  await context.close();
}

async function testJoinInterest(browser, profile, report) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await context.addInitScript(() => sessionStorage.setItem('sunday-reservation-seen', 'true'));
  await mockForms(context);
  const page = await context.newPage();
  await ready(page, '/join-our-team/');
  const section = page.locator('#program-interest');
  const form = section.locator('form[data-editorial-labels]');
  await form.scrollIntoViewIfNeeded();
  await form.locator('input[name="name"]').fill('QA Test');
  await form.locator('input[name="email"]').fill('qa@example.com');
  await form.locator('input[name="phone"]').fill('2025550199');
  await form.locator('[aria-haspopup="listbox"]').click();
  await form.getByRole('option', { name: 'The Fellows Table' }).click();
  await screenshot(page, profile, 'join-interest-form', section);
  await form.locator('button[type="submit"]').click();
  await section.getByText('Your Interest Is Saved.').waitFor({ state: 'visible', timeout: 5000 });
  await screenshot(page, profile, 'join-interest-confirmation', section);
  report.push({ profile: profile.name, form: 'join-interest', states: ['form','confirmation'], pass: true });
  await context.close();
}

async function testServicesEmbedded(browser, profile, report) {
  const context = await browser.newContext({ viewport: profile.viewport });
  await context.addInitScript(() => sessionStorage.setItem('sunday-reservation-seen', 'true'));
  await mockForms(context);
  const page = await context.newPage();
  await ready(page, '/services/');
  const section = page.locator('#inquiry');
  const form = section.locator('form[data-inq]');
  await form.waitFor({ state: 'visible' });
  const text = (await form.locator('[aria-label="Project inquiry steps"]').innerText()).replace(/\s+/g, ' ').toUpperCase();
  assert(text.includes('01 PROJECT BASICS') && text.includes('02 TIMING & BUDGET') && text.includes('03 PROJECT SCOPE'), `${profile.name}: Services inquiry does not use shared named steps`);
  await section.scrollIntoViewIfNeeded();
  await screenshot(page, profile, 'services-embedded-inquiry', section);
  report.push({ profile: profile.name, form: 'services-embedded-inquiry', states: ['step-1-shared-source'], pass: true });
  await context.close();
}

const browser = await webkit.launch();
const report = [];
const failures = [];
const tests = [testInquiry, testReservation, testFooterNewsletter, testContact, testSundaySchool, testJoinInterest, testServicesEmbedded];

for (const profile of profiles) {
  for (const test of tests) {
    try {
      await test(browser, profile, report);
      console.log(`PASS ${profile.name} ${test.name}`);
    } catch (err) {
      const msg = `${profile.name} ${test.name}: ${String(err?.message || err)}`;
      failures.push(msg);
      console.error('FAIL ' + msg);
    }
  }
}

await browser.close();
await fs.mkdir(outRoot, { recursive: true });
await fs.writeFile(path.join(outRoot, 'report.json'), JSON.stringify({ report, failures }, null, 2));
if (failures.length) process.exit(1);
console.log(`Form-state QA passed: ${report.length} form/profile checks.`);
