import fs from 'node:fs';
import path from 'node:path';
import { webkit } from 'playwright';

const ROOT = process.cwd();
const OUT = path.join(ROOT, 'qa-rendered-artifacts');
fs.mkdirSync(OUT, { recursive: true });

function discoverRoutes(dir = ROOT, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['.git','node_modules','qa-rendered-artifacts'].includes(e.name)) continue;
    const full = path.join(dir, e.name);
    const next = path.join(rel, e.name);
    if (e.isDirectory()) out.push(...discoverRoutes(full, next));
    else if (e.isFile() && e.name === 'index.html') {
      const folder = path.dirname(next).replaceAll('\\','/');
      out.push(folder === '.' ? '/' : `/${folder}/`);
    }
  }
  return out;
}

const allRoutes = [...new Set([...discoverRoutes(), '/404.html'])].sort();
const mobileProfile = { name:'mobile', viewport:{ width:390, height:844 }, isMobile:true, userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' };
const desktopProfile = { name:'desktop', viewport:{ width:1440, height:1000 }, isMobile:false, userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15' };
const profiles = [mobileProfile, desktopProfile];
const report = { failures:[], routes:[], specific:{} };
const browser = await webkit.launch();

function fail(msg, detail={}) { report.failures.push({ msg, ...detail }); }

async function ready(page, route) {
  const r = await page.goto(`http://127.0.0.1:4173${route}`, { waitUntil:'commit', timeout:15000 });
  await page.waitForFunction(() => document.readyState !== 'loading', null, { timeout:8000 }).catch(()=>{});
  await page.waitForFunction(() => document.querySelector('[data-screen-label], #dc-root .sc-host'), null, { timeout:10000 });
  await page.waitForFunction(() => document.querySelector('link[data-sunday-rendered-corrections]'), null, { timeout:7000 });
  await page.waitForTimeout(760);
  return r?.status() || 0;
}

async function dismissReservation(page) {
  const dlg = page.locator('[aria-label="The Sunday Reservation"]');
  if (!(await dlg.count())) return;
  if (!(await dlg.first().isVisible().catch(()=>false))) return;
  const close = dlg.first().locator('button[aria-label="Close"]');
  if (await close.count()) {
    await close.first().click({ force:true }).catch(()=>{});
    await page.waitForTimeout(100);
  }
  // QA fallback only: do not let the automatic newsletter overlay obscure the
  // page/menu being measured if the component is still transitioning out.
  await page.evaluate(() => {
    const d = document.querySelector('[aria-label="The Sunday Reservation"]');
    const overlay = d?.closest('[role="presentation"]');
    if (overlay && getComputedStyle(overlay).display !== 'none') overlay.style.display = 'none';
  });
}

async function routeBaseline(page, profile, route) {
  const status = await ready(page, route);
  await dismissReservation(page);
  const metrics = await page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const sheet = document.querySelector('aside[aria-label="Sunday & Company navigation"]');
    const link = document.querySelector('link[data-sunday-rendered-corrections]');
    const headings = [...document.querySelectorAll('h1,h2,h3')].map(h => ({
      parentWeight:getComputedStyle(h).fontWeight,
      pieces:[...h.querySelectorAll('span,em,strong')].map(el => getComputedStyle(el).fontWeight)
    }));
    const newsletter = document.querySelector('[aria-label="Newsletter"]');
    const newsInput = newsletter?.querySelector('input');
    const newsButton = newsletter?.querySelector('form button');
    const fine = newsletter?.querySelector('[data-news-fineprint]');
    const runtime = document.querySelector('#dc-root > .sc-host');
    return {
      href:link?.getAttribute('href') || '',
      overflow:Math.max(root.scrollWidth, body?.scrollWidth || 0) - innerWidth,
      closedSheetPainted:sheet?.getAttribute('data-sheet-state') === 'closed' && getComputedStyle(sheet).display !== 'none',
      headings,
      newsletterInput:newsInput ? parseFloat(getComputedStyle(newsInput).fontSize) : null,
      newsletterButton:newsButton ? parseFloat(getComputedStyle(newsButton).fontSize) : null,
      newsletterFine:fine ? parseFloat(getComputedStyle(fine).fontSize) : null,
      runtimeHeight:runtime ? runtime.getBoundingClientRect().height : null,
      scrollHeight:Math.max(root.scrollHeight, body?.scrollHeight || 0)
    };
  });
  const badWeights = metrics.headings.some(h => h.parentWeight !== '400' || h.pieces.some(w => w !== '400'));
  const runtimeShort = metrics.runtimeHeight != null && metrics.runtimeHeight + 4 < metrics.scrollHeight;
  let passed = status < 500 && metrics.href.includes('rendered-corrections.css?v=20260912-4') && metrics.overflow <= 2 && !metrics.closedSheetPainted && !badWeights && !runtimeShort;
  if (profile.name === 'mobile' && metrics.newsletterInput != null) {
    passed = passed && metrics.newsletterInput >= 16 && metrics.newsletterButton >= 10 && metrics.newsletterFine <= 8;
  }
  if (!passed) fail('route baseline', { profile:profile.name, route, status, metrics, badWeights, runtimeShort });
  report.routes.push({ profile:profile.name, route, passed, status, ...metrics, badWeights, runtimeShort });
  const slug = route === '/' ? 'home' : route.replace(/^\//,'').replace(/\/$/,'').replaceAll('/','__').replace('.html','');
  await page.screenshot({ path:path.join(OUT, `${profile.name}__${slug}.png`), fullPage:true, animations:'disabled' });
}

try {
  // Every route, mobile + desktop, from the actual rendered DOM.
  for (const profile of profiles) {
    const ctx = await browser.newContext({ viewport:profile.viewport, isMobile:profile.isMobile, userAgent:profile.userAgent, deviceScaleFactor:1 });
    for (const route of allRoutes) {
      const page = await ctx.newPage();
      try { await routeBaseline(page, profile, route); }
      catch (e) { fail('route exception', { profile:profile.name, route, error:String(e) }); }
      finally { await page.close().catch(()=>{}); }
    }
    await ctx.close();
  }

  // Homepage hierarchy + real on-scroll and hero motion.
  {
    const ctx = await browser.newContext({ viewport:mobileProfile.viewport, isMobile:true, userAgent:mobileProfile.userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/');
    await dismissReservation(page);
    const heroMotion = await page.evaluate(() => document.querySelector('#top')?.getAnimations({subtree:true}).length || 0);
    const vision = page.locator('#vision');
    await vision.scrollIntoViewIfNeeded();
    await page.waitForTimeout(120);
    const home = await page.evaluate(() => {
      const size = sel => { const n=document.querySelector(sel); return n ? parseFloat(getComputedStyle(n).fontSize) : null; };
      const weight = sel => { const n=document.querySelector(sel); return n ? getComputedStyle(n).fontWeight : null; };
      const vision = document.querySelector('#vision');
      const footerUI = [...document.querySelectorAll('footer [data-footer-ui], footer [data-footer-location], footer a[href^="mailto:"], footer a[href*="instagram.com/sundayand_co"]')].map(n => parseFloat(getComputedStyle(n).fontSize));
      return {
        fineprint:size('[aria-label="Newsletter"] [data-news-fineprint]'),
        footerUI,
        visionAnimations:vision ? vision.getAnimations({subtree:true}).length : 0,
        visionQuoteWeight:weight('#vision [data-vision-quote]'),
        visionBodySizes:[...document.querySelectorAll('#vision [data-vision-body]')].map(n=>parseFloat(getComputedStyle(n).fontSize))
      };
    });
    report.specific.mobileHome = { heroMotion, ...home };
    if (heroMotion < 1) fail('hero entrance motion absent', { heroMotion });
    if (home.visionAnimations < 1) fail('vision section motion absent', home);
    if (!(home.fineprint && home.fineprint <= 8)) fail('newsletter fine print too large', home);
    if (home.footerUI.length && Math.max(...home.footerUI)-Math.min(...home.footerUI) > .2) fail('footer UI sizes inconsistent', home);
    if (home.visionQuoteWeight !== '400') fail('vision quote weight incorrect', home);
    if (home.visionBodySizes.length >= 2 && Math.max(...home.visionBodySizes)-Math.min(...home.visionBodySizes) > .2) fail('vision body sizes inconsistent', home);
    await page.close(); await ctx.close();
  }

  // Project Inquiry: hierarchy, named stages, all functional controls, date picker.
  {
    const ctx = await browser.newContext({ viewport:mobileProfile.viewport, isMobile:true, userAgent:mobileProfile.userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/');
    await dismissReservation(page);
    await page.getByRole('button', { name:/Start A Project/i }).first().click();
    await page.waitForSelector('[aria-label="Project inquiry"]', { timeout:7000 });
    await page.waitForTimeout(120);
    const q = await page.evaluate(() => {
      const dlg=document.querySelector('[aria-label="Project inquiry"]');
      const cs=n=>n?getComputedStyle(n):null;
      const kicker=dlg?.querySelector('[data-inquiry-kicker]');
      const support=dlg?.querySelector('[data-inquiry-support]');
      const label=dlg?.querySelector('form[data-inq] label > span:first-child');
      const input=dlg?.querySelector('form[data-inq] input:not([type="hidden"])');
      const stages=[...dlg?.querySelectorAll('[data-stepnav] [aria-label="Project inquiry steps"] > span')||[]].map(n=>({text:n.textContent.trim(),size:parseFloat(cs(n).fontSize),weight:cs(n).fontWeight}));
      const dateTrigger=dlg?.querySelector('form[data-inq] button[aria-haspopup="dialog"]');
      const calendar=dlg?.querySelector('[aria-label="Choose a start date"]');
      const month=calendar?.querySelector(':scope > div:first-child > span');
      const weekdays=calendar?.querySelector(':scope > div:nth-child(2)');
      const day=calendar?.querySelector(':scope > div:last-child button');
      const check=dlg?.querySelector('[role="checkbox"]');
      const checkText=check?.querySelector('span:last-child');
      return {
        kicker:kicker?parseFloat(cs(kicker).fontSize):null,
        support:support?parseFloat(cs(support).fontSize):null,
        supportFamily:support?cs(support).fontFamily:null,
        label:label?parseFloat(cs(label).fontSize):null,
        labelWeight:label?cs(label).fontWeight:null,
        input:input?parseFloat(cs(input).fontSize):null,
        stages,
        dateTrigger:dateTrigger?parseFloat(cs(dateTrigger).fontSize):null,
        dateTriggerHeight:dateTrigger?dateTrigger.getBoundingClientRect().height:null,
        month:month?parseFloat(cs(month).fontSize):null,
        weekdays:weekdays?parseFloat(cs(weekdays).fontSize):null,
        day:day?parseFloat(cs(day).fontSize):null,
        dayHeight:day?day.getBoundingClientRect().height:null,
        checkboxHeight:check?check.getBoundingClientRect().height:null,
        checkboxText:checkText?parseFloat(cs(checkText).fontSize):null,
        checkboxWeight:checkText?cs(checkText).fontWeight:null,
        animations:dlg?dlg.getAnimations({subtree:true}).length:0
      };
    });
    report.specific.mobileInquiry=q;
    if (!(q.kicker >= 45)) fail('inquiry kicker not large enough', q);
    if (q.support !== 13 || !String(q.supportFamily).includes('Inter Tight')) fail('inquiry supporting text incorrect', q);
    if (!(q.label >= 10.5 && q.label <= 11.5) || q.labelWeight !== '400') fail('inquiry functional label hierarchy incorrect', q);
    if (q.input !== 16) fail('mobile inquiry input not 16px', q);
    const stageText=q.stages.map(s=>s.text).join(' ');
    if (!/Project Basics/i.test(stageText) || !/Timing & Budget/i.test(stageText) || !/Project Scope/i.test(stageText)) fail('named inquiry stages missing', q);
    if (q.stages.some(s=>s.size < 9.5 || s.weight !== '400')) fail('inquiry stage microtype too small/light', q);
    if (!(q.dateTrigger >= 16 && q.dateTriggerHeight >= 43)) fail('date trigger not readable/tappable', q);
    if (!(q.month >= 10.5 && q.weekdays >= 9.5 && q.day >= 11.5 && q.dayHeight >= 37)) fail('date picker functional text too small', q);
    if (!(q.checkboxHeight >= 39 && q.checkboxText >= 10.5 && q.checkboxWeight === '400')) fail('service checkbox functional UI too small/light', q);
    if (q.animations < 1) fail('inquiry entrance/step motion absent', q);
    await page.screenshot({ path:path.join(OUT,'mobile__inquiry.png'), fullPage:false, animations:'disabled' });
    await page.close(); await ctx.close();
  }

  // Services embedded Inquiry must use the same kicker/support hierarchy.
  {
    const ctx = await browser.newContext({ viewport:mobileProfile.viewport, isMobile:true, userAgent:mobileProfile.userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/services/');
    await dismissReservation(page);
    const q = await page.evaluate(() => {
      const k=document.querySelector('#inquiry [data-inquiry-kicker]');
      const s=document.querySelector('#inquiry [data-inquiry-support]');
      return { kicker:k?parseFloat(getComputedStyle(k).fontSize):null, support:s?parseFloat(getComputedStyle(s).fontSize):null, family:s?getComputedStyle(s).fontFamily:null };
    });
    report.specific.servicesInquiry=q;
    if (!(q.kicker >=45 && q.support===13 && String(q.family).includes('Inter Tight'))) fail('services inquiry hierarchy differs from popup', q);
    await page.close(); await ctx.close();
  }

  // Every editorial form: mobile functional inputs/labels/actions must be readable.
  for (const route of ['/contact/','/sunday-school/','/join-our-team/']) {
    const ctx = await browser.newContext({ viewport:mobileProfile.viewport, isMobile:true, userAgent:mobileProfile.userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, route);
    await dismissReservation(page);
    const forms = await page.evaluate(() => [...document.querySelectorAll('form[data-editorial-labels]')].map((form,idx) => {
      const visible=n=>{const s=getComputedStyle(n);return s.display!=='none'&&s.visibility!=='hidden';};
      const labels=[...form.querySelectorAll('label > span:first-child, div > span:first-child')].filter(visible).map(n=>({size:parseFloat(getComputedStyle(n).fontSize),weight:getComputedStyle(n).fontWeight,text:n.textContent.trim()}));
      const controls=[...form.querySelectorAll('input:not([type="hidden"]), textarea, select')].filter(visible).map(n=>({size:parseFloat(getComputedStyle(n).fontSize),type:n.tagName+':'+(n.type||'')}));
      const submits=[...form.querySelectorAll('button[type="submit"]')].filter(visible).map(n=>parseFloat(getComputedStyle(n).fontSize));
      const custom=form.querySelector('button[aria-haspopup="listbox"]');
      return {idx,labels,controls,submits,custom:custom?{size:parseFloat(getComputedStyle(custom).fontSize),family:getComputedStyle(custom).fontFamily,weight:getComputedStyle(custom).fontWeight}:null};
    }));
    report.specific[`forms:${route}`]=forms;
    for (const form of forms) {
      if (form.labels.some(x=>x.size<10.5||x.weight!=='400')) fail('editorial form label too small/light',{route,form});
      if (form.controls.some(x=>x.size<16)) fail('editorial mobile input below 16px',{route,form});
      if (form.submits.some(x=>x<10)) fail('editorial form action too small',{route,form});
      if (form.custom && (form.custom.size<16 || !String(form.custom.family).includes('Inter Tight') || form.custom.weight!=='400')) fail('custom form control not secondary-font/readable',{route,form});
    }
    if (route==='/contact/') {
      const instruction=await page.evaluate(()=>{const n=document.querySelector('[data-form-instruction]');return n?{size:parseFloat(getComputedStyle(n).fontSize),weight:getComputedStyle(n).fontWeight}:null;});
      report.specific.contactInstruction=instruction;
      if (!instruction || instruction.size<10.5 || instruction.weight!=='400') fail('contact required-fields instruction too small/light',{instruction});
    }
    await page.close(); await ctx.close();
  }

  // Join Our Team: no mirrored 3D face on mobile; details expand in page flow.
  {
    const ctx = await browser.newContext({ viewport:mobileProfile.viewport, isMobile:true, userAgent:mobileProfile.userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/join-our-team/');
    await dismissReservation(page);
    const before=await page.evaluate(()=>{
      const article=document.querySelector('[data-program-cards] > article');
      const wrap=article?.querySelector(':scope > div');
      const back=wrap?.querySelector(':scope > div:nth-child(2)');
      const front=wrap?.querySelector(':scope > button:first-child');
      return {wrapTransform:wrap?getComputedStyle(wrap).transform:null, backDisplay:back?getComputedStyle(back).display:null, frontLabel:front?.getAttribute('aria-label')||''};
    });
    if (before.backDisplay!=='none' || !/View full details/i.test(before.frontLabel)) fail('mobile program card still using mirrored flip face',{before});
    await page.getByRole('button',{name:/View full details for The Fellows Table/i}).click();
    await page.waitForTimeout(120);
    const after=await page.evaluate(()=>{
      const dlg=document.querySelector('[role="dialog"][aria-label="The Fellows Table"]');
      const outer=dlg?.closest('[role="presentation"]');
      return {visible:!!dlg&&getComputedStyle(outer).display!=='none', outerPosition:outer?getComputedStyle(outer).position:null, outerOverflow:outer?getComputedStyle(outer).overflowY:null, innerOverflow:dlg?getComputedStyle(dlg).overflowY:null, ariaModal:dlg?.getAttribute('aria-modal')||null};
    });
    report.specific.mobilePrograms={before,after};
    if (!after.visible || after.outerPosition!=='static' || after.outerOverflow!=='visible' || after.innerOverflow!=='visible' || after.ariaModal!=='false') fail('program details are not normal in-page mobile content',{after});
    await page.screenshot({path:path.join(OUT,'mobile__join-program-details.png'),fullPage:true,animations:'disabled'});
    await page.close(); await ctx.close();
  }

  // Mobile menu: visible entrance + row stagger, then truly removed from paint.
  {
    const ctx = await browser.newContext({ viewport:mobileProfile.viewport, isMobile:true, userAgent:mobileProfile.userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/about/');
    await dismissReservation(page);
    const menu = page.getByRole('button', { name:/Open menu/i });
    await menu.click();
    await page.waitForTimeout(90);
    const openState = await page.evaluate(() => {
      const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');
      return {display:getComputedStyle(s).display,transform:getComputedStyle(s).transform,state:s.getAttribute('data-sheet-state'),animations:s.getAnimations({subtree:true}).length};
    });
    await page.waitForTimeout(450);
    const opened = await page.evaluate(() => {const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');return {display:getComputedStyle(s).display,transform:getComputedStyle(s).transform,state:s.getAttribute('data-sheet-state')};});
    const close = page.getByRole('button', { name:/Close menu/i });
    await close.click({force:true});
    await page.waitForTimeout(430);
    const closed = await page.evaluate(() => {const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');return {display:getComputedStyle(s).display,state:s.getAttribute('data-sheet-state')};});
    report.specific.menu={openState,opened,closed};
    if (openState.display==='none'||openState.state!=='open'||openState.animations<1) fail('menu/stagger motion not visible',{openState});
    if (opened.transform!=='none'&&opened.transform!=='matrix(1, 0, 0, 1, 0, 0)') fail('menu does not finish open',{opened});
    if (closed.display!=='none'||closed.state!=='closed') fail('closed menu remains painted',{closed});
    await page.close(); await ctx.close();
  }
} finally {
  await browser.close();
}

fs.writeFileSync(path.join(OUT,'report.json'), JSON.stringify(report,null,2));
console.log(`Routes checked: ${report.routes.length}`);
console.log(`Failures: ${report.failures.length}`);
for (const f of report.failures) console.log(JSON.stringify(f));
if (report.failures.length) process.exit(1);
