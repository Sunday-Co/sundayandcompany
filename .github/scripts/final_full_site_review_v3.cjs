const { webkit } = require('/tmp/sunday-final-v3/node_modules/playwright');
const { PNG } = require('/tmp/sunday-final-v3/node_modules/pngjs');
const fs = require('node:fs');
const assert = require('node:assert');

const base = 'http://127.0.0.1:4173';
const out = 'final-full-site-review-v3';
fs.mkdirSync(out, { recursive: true });
const issues = [];
const report = { routes: {}, forms: {}, interactions: {}, issues };
const px = value => parseFloat(value || '0');
const routes = [
  ['home','/'], ['about','/about/'], ['services','/services/'], ['our-work','/our-work/'],
  ['luckys','/our-work/luckys-cafe-bakery/'], ['pizzeria-coco','/our-work/pizzeria-coco/'],
  ['petti-pathways','/our-work/petti-pathways/'], ['folake','/our-work/folake/'],
  ['contact','/contact/'], ['join','/join-our-team/'], ['sunday-school','/sunday-school/'],
  ['privacy','/privacy-policy/'], ['terms','/terms-and-conditions/'], ['cookie','/cookie-policy/'],
  ['accessibility','/accessibility/'], ['404','/404.html']
];

function pngDiff(aBuf, bBuf) {
  const a = PNG.sync.read(aBuf), b = PNG.sync.read(bBuf);
  assert.strictEqual(a.width, b.width);
  assert.strictEqual(a.height, b.height);
  let changed = 0;
  for (let i = 0; i < a.data.length; i += 4) {
    if (a.data[i] !== b.data[i] || a.data[i+1] !== b.data[i+1] || a.data[i+2] !== b.data[i+2] || a.data[i+3] !== b.data[i+3]) changed++;
  }
  return changed;
}

function imageVariance(buffer) {
  const png = PNG.sync.read(buffer);
  let sum = 0, sumSq = 0, count = 0;
  for (let i = 0; i < png.data.length; i += 16) {
    const y = .2126*png.data[i] + .7152*png.data[i+1] + .0722*png.data[i+2];
    sum += y; sumSq += y*y; count++;
  }
  const mean = sum / Math.max(count,1);
  return sumSq / Math.max(count,1) - mean*mean;
}

async function dismissReservation(page) {
  const modal = page.locator('[aria-label="The Sunday Reservation"]');
  if (await modal.count() && await modal.isVisible().catch(() => false)) {
    const close = modal.locator('button[aria-label="Close"]');
    if (await close.count()) await close.first().click().catch(() => {});
    await page.waitForTimeout(120);
  }
}

async function settle(page) {
  await page.waitForTimeout(500);
  await dismissReservation(page);
  await page.evaluate(async () => {
    const max = document.documentElement.scrollHeight;
    for (let y = 0; y < max; y += 650) {
      window.scrollTo(0, y);
      await new Promise(r => setTimeout(r, 10));
    }
    window.scrollTo(0,0);
  });
  await page.waitForTimeout(180);
}

async function reviewRoute(context, mode, viewport, name, route) {
  const page = await context.newPage();
  const pageErrors = [], consoleErrors = [];
  page.on('pageerror', e => pageErrors.push(e.message));
  page.on('console', m => {
    if (m.type() === 'error' && !m.text().includes('fonts.googleapis.com')) consoleErrors.push(m.text());
  });
  await page.goto(base + route, { waitUntil: 'networkidle', timeout: 60000 });
  await settle(page);
  const state = await page.evaluate(() => ({
    lang: document.documentElement.lang,
    htmlWidth: document.documentElement.scrollWidth,
    bodyWidth: document.body.scrollWidth,
    innerWidth,
    main: !!document.querySelector('main#main-content'),
    images: [...document.images].map(img => ({src: img.currentSrc || img.src, complete: img.complete, nw: img.naturalWidth, nh: img.naturalHeight})),
    heroes: [...document.querySelectorAll('img[data-sunday-static-hero="true"]')].map(img => {
      const r = img.getBoundingClientRect(), s = getComputedStyle(img);
      return {src: img.currentSrc || img.src, nw: img.naturalWidth, nh: img.naturalHeight, w: r.width, h: r.height, display: s.display, visibility: s.visibility, opacity: s.opacity};
    })
  }));
  if (state.lang !== 'en') issues.push(`${mode} ${route}: html lang is ${state.lang || '(blank)'}`);
  if (!state.main) issues.push(`${mode} ${route}: main#main-content missing`);
  if (state.htmlWidth > viewport.width + 1) issues.push(`${mode} ${route}: html overflow ${state.htmlWidth}px`);
  if (state.bodyWidth > viewport.width + 1) issues.push(`${mode} ${route}: body overflow ${state.bodyWidth}px`);
  for (const img of state.images) if (!img.complete || img.nw === 0) issues.push(`${mode} ${route}: broken image ${img.src}`);
  for (const hero of state.heroes) {
    if (hero.nw === 0 || hero.w < 30 || hero.h < 80 || hero.display === 'none' || hero.visibility === 'hidden' || hero.opacity === '0') issues.push(`${mode} ${route}: hero not visible ${JSON.stringify(hero)}`);
  }
  if (pageErrors.length) issues.push(`${mode} ${route}: page errors ${pageErrors.join(' | ')}`);
  if (consoleErrors.length) issues.push(`${mode} ${route}: console errors ${consoleErrors.join(' | ')}`);

  const topPath = `${out}/${mode}-${name}-top.png`;
  const fullPath = `${out}/${mode}-${name}-full.png`;
  await page.screenshot({ path: topPath, fullPage: false });
  await page.screenshot({ path: fullPath, fullPage: true });
  const fullPng = PNG.sync.read(fs.readFileSync(fullPath));
  if (fullPng.width !== viewport.width) issues.push(`${mode} ${route}: full screenshot is ${fullPng.width}px wide, expected ${viewport.width}px`);

  const heroProofs = [];
  const heroes = page.locator('img[data-sunday-static-hero="true"]');
  for (let i = 0; i < await heroes.count(); i++) {
    const buffer = await heroes.nth(i).screenshot();
    const variance = imageVariance(buffer);
    fs.writeFileSync(`${out}/${mode}-${name}-hero-${i+1}.png`, buffer);
    if (variance < 20) issues.push(`${mode} ${route}: hero capture appears blank/uniform, variance ${variance}`);
    heroProofs.push({ variance });
  }
  report.routes[mode] ??= {};
  report.routes[mode][name] = { route, state, pageErrors, consoleErrors, screenshotWidth: fullPng.width, heroProofs };
  await page.close();
}

async function placeholderProof(page, locator, name) {
  const originalId = await locator.getAttribute('id');
  const qaId = originalId || ('qa-' + name.replace(/[^a-z0-9]/gi,'').toLowerCase());
  if (!originalId) await locator.evaluate((el,id) => el.id = id, qaId);
  const current = await locator.screenshot();
  const fieldSize = await locator.evaluate(el => getComputedStyle(el).fontSize);
  await page.evaluate(({qaId}) => {
    const s = document.createElement('style');
    s.id = 'qa-placeholder-control';
    s.textContent = `#${CSS.escape(qaId)}::placeholder,#${CSS.escape(qaId)}::-webkit-input-placeholder{font-size:12px!important}`;
    document.head.appendChild(s);
  }, {qaId});
  await page.waitForTimeout(80);
  const ref12 = await locator.screenshot();
  await page.locator('#qa-placeholder-control').evaluate((s,{qaId}) => {
    s.textContent = `#${CSS.escape(qaId)}::placeholder,#${CSS.escape(qaId)}::-webkit-input-placeholder{font-size:16px!important}`;
  }, {qaId});
  await page.waitForTimeout(80);
  const ref16 = await locator.screenshot();
  const d12 = pngDiff(current,ref12), d16 = pngDiff(current,ref16), r1216 = pngDiff(ref12,ref16);
  fs.writeFileSync(`${out}/form-${name}-current.png`, current);
  fs.writeFileSync(`${out}/form-${name}-12px-reference.png`, ref12);
  fs.writeFileSync(`${out}/form-${name}-16px-control.png`, ref16);
  if (d12 > 4) issues.push(`form ${name}: placeholder differs from 12px reference by ${d12} pixels`);
  if (d16 <= 20 || r1216 <= 20) issues.push(`form ${name}: placeholder is not visibly distinct from 16px control`);
  if (px(fieldSize) < 16) issues.push(`form ${name}: entered text ${fieldSize}, expected at least 16px`);
  await page.locator('#qa-placeholder-control').evaluate(el => el.remove());
  if (!originalId) await locator.evaluate(el => el.removeAttribute('id'));
  return { fieldSize, d12, d16, r1216 };
}

async function reviewForms(browser) {
  const context = await browser.newContext({ viewport: {width:390,height:844} });
  const page = await context.newPage();
  await page.goto(base+'/', {waitUntil:'networkidle',timeout:60000});
  await page.waitForTimeout(1000);
  let reservation = page.locator('[aria-label="The Sunday Reservation"]');
  if (!await reservation.isVisible().catch(()=>false)) {
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.reload({waitUntil:'networkidle'});
    await page.waitForTimeout(1000);
    reservation = page.locator('[aria-label="The Sunday Reservation"]');
  }
  if (!await reservation.isVisible().catch(()=>false)) issues.push('Reservation did not appear in fresh context');
  else {
    report.forms.reservationPlaceholder = await placeholderProof(page,reservation.locator('input[placeholder="you@example.com"]'),'reservation-email');
    report.forms.reservationLabel = await reservation.locator('label[for="reservationEmail"]').evaluate(el=>getComputedStyle(el).fontSize);
    if (px(report.forms.reservationLabel) > 10) issues.push(`Reservation label remains ${report.forms.reservationLabel}`);
    await page.screenshot({path:`${out}/form-reservation-mobile.png`,fullPage:false});
    await dismissReservation(page);
  }

  const projectOpener = page.getByText('Start A Project',{exact:true}).first();
  await projectOpener.evaluate(el=>el.click());
  const inquiry = page.locator('[aria-label="Project inquiry"]');
  await inquiry.waitFor({state:'visible'});
  const form = inquiry.locator('form[data-inq]');
  report.forms.projectLabels = await form.locator('label > span:first-child').evaluateAll(els=>els.map(el=>({text:el.textContent.trim(),size:getComputedStyle(el).fontSize})));
  for (const x of report.forms.projectLabels) if (px(x.size) > 10) issues.push(`Project label ${x.text} remains ${x.size}`);
  await page.screenshot({path:`${out}/form-project-step1-mobile.png`,fullPage:false});
  await form.locator('input[name="name"]').fill('QA Test');
  await form.locator('input[name="email"]').fill('qa@example.com');
  await form.locator('input[name="phone"]').fill('2025550123');
  await form.locator('input[name="business"]').fill('QA Studio');
  await form.locator('[data-stepbtns] button').first().click();
  await page.waitForTimeout(120);
  report.forms.projectWebsite = await placeholderProof(page,form.locator('input[name="website"]'),'project-website');
  report.forms.projectBudget = await placeholderProof(page,form.locator('input[name="budget"]'),'project-budget');
  report.forms.projectDatePrompt = await form.locator('[aria-haspopup="dialog"]').first().evaluate(el=>getComputedStyle(el).fontSize);
  if (px(report.forms.projectDatePrompt) > 12.6) issues.push(`Project date prompt remains ${report.forms.projectDatePrompt}`);
  await page.screenshot({path:`${out}/form-project-step2-mobile.png`,fullPage:false});
  await inquiry.locator('button[aria-label="Close"]').first().click();
  await page.waitForTimeout(120);

  await page.goto(base+'/contact/',{waitUntil:'networkidle',timeout:60000});
  await page.waitForTimeout(600);
  const contact = page.locator('[data-screen-label="Contact"] form[data-editorial-labels]');
  report.forms.contactLabels = await contact.locator('label > span:first-child').evaluateAll(els=>els.map(el=>({text:el.textContent.trim(),size:getComputedStyle(el).fontSize})));
  for (const x of report.forms.contactLabels) if (px(x.size) > 10) issues.push(`Contact label ${x.text} remains ${x.size}`);
  await contact.scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/form-contact-mobile.png`,fullPage:false});

  await page.goto(base+'/join-our-team/',{waitUntil:'networkidle',timeout:60000});
  await page.waitForTimeout(600);
  const join = page.locator('#program-interest form[data-editorial-labels]');
  report.forms.joinLabels = await join.locator('label > span:first-child').evaluateAll(els=>els.map(el=>({text:el.textContent.trim(),size:getComputedStyle(el).fontSize})));
  for (const x of report.forms.joinLabels) if (px(x.size) > 10) issues.push(`Join label ${x.text} remains ${x.size}`);
  report.forms.joinPrompt = await join.locator('[aria-haspopup="listbox"]').first().evaluate(el=>getComputedStyle(el).fontSize);
  if (px(report.forms.joinPrompt) > 12.6) issues.push(`Join program prompt remains ${report.forms.joinPrompt}`);
  await join.scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/form-join-mobile.png`,fullPage:false});

  await page.goto(base+'/sunday-school/',{waitUntil:'networkidle',timeout:60000});
  await page.waitForTimeout(600);
  report.forms.schoolPlaceholder = await placeholderProof(page,page.locator('#school-notes-email'),'sunday-school-email');
  await page.locator('#school-notes-email').scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/form-sunday-school-mobile.png`,fullPage:false});
  const footerInput = page.locator('section[aria-label="Newsletter"] input[placeholder="Email Address"]');
  report.forms.footerPlaceholder = await placeholderProof(page,footerInput,'footer-email');
  await footerInput.scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/form-footer-mobile.png`,fullPage:false});
  await context.close();
}

async function projectFocus(browser, mode, viewport) {
  const context = await browser.newContext({viewport});
  const page = await context.newPage();
  await page.goto(base+'/',{waitUntil:'networkidle',timeout:60000});
  await page.waitForTimeout(700);
  await dismissReservation(page);
  const opener = page.getByText('Start A Project',{exact:true}).first();
  await opener.focus();
  await opener.click();
  await page.waitForTimeout(220);
  const modal = page.locator('[aria-label="Project inquiry"]');
  const result = { opened: await modal.isVisible().catch(()=>false) };
  result.focusInsideAfterOpen = await modal.evaluate(el=>el.contains(document.activeElement));
  result.tabStayedInside = true;
  if (!result.opened) issues.push(`${mode} Project Inquiry did not open`);
  if (!result.focusInsideAfterOpen) issues.push(`${mode} Project Inquiry focus did not move inside`);
  for (let i=0;i<18;i++) {
    await page.keyboard.press('Tab');
    if (!await modal.evaluate(el=>el.contains(document.activeElement))) {
      result.tabStayedInside = false;
      issues.push(`${mode} Project Inquiry focus escaped after ${i+1} Tab presses`);
      break;
    }
  }
  await page.screenshot({path:`${out}/interaction-${mode}-project-inquiry.png`,fullPage:false});
  await page.keyboard.press('Escape');
  await page.waitForTimeout(260);
  result.closedWithEscape = !await modal.isVisible().catch(()=>false);
  result.focusRestored = await opener.evaluate(el=>document.activeElement===el).catch(()=>false);
  if (!result.closedWithEscape) issues.push(`${mode} Project Inquiry Escape did not close`);
  if (!result.focusRestored) issues.push(`${mode} Project Inquiry did not restore focus to opener`);
  report.interactions[`${mode}ProjectInquiry`] = result;
  await context.close();
}

async function menuFocus(browser) {
  const context = await browser.newContext({viewport:{width:390,height:844}});
  const page = await context.newPage();
  await page.goto(base+'/',{waitUntil:'networkidle',timeout:60000});
  await page.waitForTimeout(700);
  await dismissReservation(page);
  const opener = page.getByRole('button',{name:/open menu/i}).first();
  await opener.focus();
  await opener.click();
  await page.waitForTimeout(460);
  const sheet = page.locator('aside[aria-label="Sunday & Company navigation"]');
  const result = { opened: await sheet.isVisible().catch(()=>false) };
  result.focusInsideAfterOpen = await sheet.evaluate(el=>el.contains(document.activeElement));
  result.tabStayedInside = true;
  if (!result.opened) issues.push('Mobile menu did not open');
  if (!result.focusInsideAfterOpen) issues.push('Mobile menu focus did not move inside');
  for (let i=0;i<16;i++) {
    await page.keyboard.press('Tab');
    if (!await sheet.evaluate(el=>el.contains(document.activeElement))) {
      result.tabStayedInside = false;
      issues.push(`Mobile menu focus escaped after ${i+1} Tab presses`);
      break;
    }
  }
  await page.screenshot({path:`${out}/interaction-mobile-menu.png`,fullPage:false});
  await page.keyboard.press('Escape');
  /* The sheet has a 340ms close transition. Verify after that animation,
     rather than classifying an in-progress close as a failure. */
  await page.waitForTimeout(460);
  result.closedWithEscape = !await sheet.isVisible().catch(()=>false);
  result.focusRestored = await opener.evaluate(el=>document.activeElement===el).catch(()=>false);
  if (!result.closedWithEscape) issues.push('Mobile menu Escape did not close');
  if (!result.focusRestored) issues.push('Mobile menu did not restore focus to opener');
  report.interactions.mobileMenu = result;
  await context.close();
}

async function reservationFocus(browser) {
  const context = await browser.newContext({viewport:{width:390,height:844}});
  const page = await context.newPage();
  await page.goto(base+'/',{waitUntil:'networkidle',timeout:60000});
  await page.evaluate(()=>{localStorage.clear();sessionStorage.clear();});
  await page.reload({waitUntil:'networkidle'});
  await page.waitForTimeout(1000);
  const modal = page.locator('[aria-label="The Sunday Reservation"]');
  const result = { opened: await modal.isVisible().catch(()=>false) };
  if (!result.opened) issues.push('Reservation popup did not appear for keyboard test');
  else {
    result.focusInsideAfterOpen = await modal.evaluate(el=>el.contains(document.activeElement));
    result.tabStayedInside = true;
    if (!result.focusInsideAfterOpen) issues.push('Reservation focus did not move inside');
    for (let i=0;i<10;i++) {
      await page.keyboard.press('Tab');
      if (!await modal.evaluate(el=>el.contains(document.activeElement))) {
        result.tabStayedInside = false;
        issues.push(`Reservation focus escaped after ${i+1} Tab presses`);
        break;
      }
    }
    await page.screenshot({path:`${out}/interaction-reservation.png`,fullPage:false});
    await page.keyboard.press('Escape');
    await page.waitForTimeout(220);
    result.closedWithEscape = !await modal.isVisible().catch(()=>false);
    if (!result.closedWithEscape) issues.push('Reservation Escape did not close');
  }
  report.interactions.reservation = result;
  await context.close();
}

(async()=>{
  const browser = await webkit.launch();
  try {
    for (const [mode,viewport] of [['mobile',{width:390,height:844}],['desktop',{width:1440,height:900}]]) {
      const context = await browser.newContext({viewport});
      for (const [name,route] of routes) await reviewRoute(context,mode,viewport,name,route);
      await context.close();
    }
    await reviewForms(browser);
    await projectFocus(browser,'mobile',{width:390,height:844});
    await projectFocus(browser,'desktop',{width:1440,height:900});
    await menuFocus(browser);
    await reservationFocus(browser);
  } catch (err) {
    issues.push(`QA runtime exception: ${err.stack || err}`);
  } finally {
    await browser.close().catch(()=>{});
    fs.writeFileSync(`${out}/review-summary.json`,JSON.stringify(report,null,2));
    console.log('FINAL_FULL_SITE_REVIEW_V3');
    console.log(JSON.stringify({issueCount:issues.length,issues,forms:report.forms,interactions:report.interactions},null,2));
    if (issues.length) process.exit(1);
  }
})();
