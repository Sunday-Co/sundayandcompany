import fs from 'node:fs';
import path from 'node:path';
import { webkit } from 'playwright';

const ROOT = process.cwd();
const OUT = path.join(ROOT, 'qa-rendered-artifacts');
fs.mkdirSync(OUT, { recursive: true });

function routes(dir = ROOT, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['.git','node_modules','qa-rendered-artifacts'].includes(e.name)) continue;
    const full = path.join(dir, e.name);
    const next = path.join(rel, e.name);
    if (e.isDirectory()) out.push(...routes(full, next));
    else if (e.isFile() && e.name === 'index.html') {
      const folder = path.dirname(next).replaceAll('\\','/');
      out.push(folder === '.' ? '/' : `/${folder}/`);
    }
  }
  return out;
}

const allRoutes = [...new Set([...routes(), '/404.html'])].sort();
const profiles = [
  { name:'mobile', viewport:{ width:390, height:844 }, isMobile:true, userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' },
  { name:'desktop', viewport:{ width:1440, height:1000 }, isMobile:false, userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15' }
];

const report = { failures:[], routes:[], specific:{} };
const browser = await webkit.launch();

async function ready(page, route) {
  const r = await page.goto(`http://127.0.0.1:4173${route}`, { waitUntil:'commit', timeout:15000 });
  await page.waitForFunction(() => document.readyState !== 'loading', null, { timeout:8000 }).catch(()=>{});
  await page.waitForFunction(() => document.querySelector('[data-screen-label], #dc-root .sc-host'), null, { timeout:10000 });
  await page.waitForFunction(() => document.querySelector('link[data-sunday-rendered-corrections]'), null, { timeout:7000 });
  await page.waitForTimeout(700);
  return r?.status() || 0;
}

function fail(msg, detail={}) { report.failures.push({ msg, ...detail }); }

try {
  for (const profile of profiles) {
    const ctx = await browser.newContext({ viewport:profile.viewport, isMobile:profile.isMobile, userAgent:profile.userAgent, deviceScaleFactor:1 });
    for (const route of allRoutes) {
      const page = await ctx.newPage();
      try {
        const status = await ready(page, route);
        const metrics = await page.evaluate(() => {
          const root = document.documentElement;
          const body = document.body;
          const sheet = document.querySelector('aside[aria-label="Sunday & Company navigation"]');
          const link = document.querySelector('link[data-sunday-rendered-corrections]');
          const headings = [...document.querySelectorAll('h1,h2,h3')].map(h => {
            const parentWeight = getComputedStyle(h).fontWeight;
            const pieces = [...h.querySelectorAll('span,em,strong')].map(el => ({ weight:getComputedStyle(el).fontWeight, family:getComputedStyle(el).fontFamily }));
            return { parentWeight, pieces };
          });
          return {
            href: link?.getAttribute('href') || '',
            overflow: Math.max(root.scrollWidth, body?.scrollWidth || 0) - innerWidth,
            closedSheetPainted: sheet?.getAttribute('data-sheet-state') === 'closed' && getComputedStyle(sheet).display !== 'none',
            headings
          };
        });
        const badWeights = metrics.headings.some(h => h.parentWeight !== '400' || h.pieces.some(p => p.weight !== '400'));
        const passed = status < 500 && metrics.href.includes('rendered-corrections.css') && metrics.overflow <= 2 && !metrics.closedSheetPainted && !badWeights;
        if (!passed) fail('route baseline', { profile:profile.name, route, status, metrics });
        report.routes.push({ profile:profile.name, route, passed, status, overflow:metrics.overflow, closedSheetPainted:metrics.closedSheetPainted, badWeights });

        const slug = route === '/' ? 'home' : route.replace(/^\//,'').replace(/\/$/,'').replaceAll('/','__').replace('.html','');
        await page.screenshot({ path:path.join(OUT, `${profile.name}__${slug}.png`), fullPage:true, animations:'disabled' });
      } catch (e) {
        fail('route exception', { profile:profile.name, route, error:String(e) });
      } finally { await page.close().catch(()=>{}); }
    }
    await ctx.close();
  }

  // Mobile homepage: footer hierarchy + newsletter fine print + visible section motion.
  {
    const ctx = await browser.newContext({ viewport:{width:390,height:844}, isMobile:true, userAgent:profiles[0].userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/');
    const vision = page.locator('#vision');
    await vision.scrollIntoViewIfNeeded();
    await page.waitForTimeout(120);
    const home = await page.evaluate(() => {
      const size = sel => { const n=document.querySelector(sel); return n ? parseFloat(getComputedStyle(n).fontSize) : null; };
      const weight = sel => { const n=document.querySelector(sel); return n ? getComputedStyle(n).fontWeight : null; };
      const vision = document.querySelector('#vision');
      const footerUI = [...document.querySelectorAll('footer [data-footer-ui], footer [data-footer-location]')].map(n => parseFloat(getComputedStyle(n).fontSize));
      return {
        fineprint:size('[aria-label="Newsletter"] [data-news-fineprint]'),
        footerUI,
        visionAnimations: vision ? vision.getAnimations({subtree:true}).length : 0,
        visionQuoteWeight:weight('#vision [data-vision-quote]'),
        visionBodySizes:[...document.querySelectorAll('#vision [data-vision-body]')].map(n=>parseFloat(getComputedStyle(n).fontSize))
      };
    });
    report.specific.mobileHome = home;
    if (!(home.fineprint && home.fineprint <= 8)) fail('newsletter fine print too large', home);
    if (home.footerUI.length && (Math.max(...home.footerUI)-Math.min(...home.footerUI) > .2)) fail('footer UI sizes inconsistent', home);
    if (home.visionAnimations < 1) fail('section motion not running on vision', home);
    if (home.visionQuoteWeight !== '400') fail('vision quote weight incorrect', home);
    if (home.visionBodySizes.length >= 2 && Math.max(...home.visionBodySizes)-Math.min(...home.visionBodySizes) > .2) fail('vision body sizes inconsistent', home);
    await page.close(); await ctx.close();
  }

  // Mobile Project Inquiry hierarchy + functionality.
  {
    const ctx = await browser.newContext({ viewport:{width:390,height:844}, isMobile:true, userAgent:profiles[0].userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/');
    // Close reservation if it auto-opens.
    const resClose = page.locator('[aria-label="The Sunday Reservation"] button[aria-label="Close"]');
    if (await resClose.count()) await resClose.first().click().catch(()=>{});
    const trigger = page.getByRole('button', { name:/Start A Project/i }).first();
    await trigger.click();
    await page.waitForSelector('[aria-label="Project inquiry"]', { timeout:7000 });
    await page.waitForTimeout(120);
    const q = await page.evaluate(() => {
      const dlg=document.querySelector('[aria-label="Project inquiry"]');
      const kicker=dlg?.querySelector('[data-inquiry-kicker]');
      const support=dlg?.querySelector('[data-inquiry-support]');
      const label=dlg?.querySelector('form[data-inq] label > span:first-child');
      const input=dlg?.querySelector('form[data-inq] input');
      const steps=[...dlg?.querySelectorAll('[data-stepnav] button')||[]].map(n=>n.textContent.trim());
      return {
        kicker:kicker?parseFloat(getComputedStyle(kicker).fontSize):null,
        support:support?parseFloat(getComputedStyle(support).fontSize):null,
        label:label?parseFloat(getComputedStyle(label).fontSize):null,
        labelWeight:label?getComputedStyle(label).fontWeight:null,
        input:input?parseFloat(getComputedStyle(input).fontSize):null,
        steps,
        animations:dlg?dlg.getAnimations({subtree:true}).length:0
      };
    });
    report.specific.mobileInquiry=q;
    if (!(q.kicker >= 41)) fail('inquiry kicker not large enough', q);
    if (q.support !== 13) fail('inquiry supporting text incorrect', q);
    if (!(q.label >= 10.5 && q.label <= 11.25) || q.labelWeight !== '400') fail('inquiry functional label hierarchy incorrect', q);
    if (q.input !== 16) fail('mobile inquiry input not 16px', q);
    if (!q.steps.join(' ').match(/Project Basics/i) || !q.steps.join(' ').match(/Timing & Budget/i) || !q.steps.join(' ').match(/Project Scope/i)) fail('named inquiry stages missing', q);
    if (q.animations < 1) fail('inquiry entrance/step motion absent', q);
    await page.screenshot({ path:path.join(OUT,'mobile__inquiry.png'), fullPage:false });
    await page.close(); await ctx.close();
  }

  // Mobile menu must visibly animate open, then disappear from layout after close.
  {
    const ctx = await browser.newContext({ viewport:{width:390,height:844}, isMobile:true, userAgent:profiles[0].userAgent, deviceScaleFactor:1 });
    const page = await ctx.newPage();
    await ready(page, '/about/');
    const menu = page.getByRole('button', { name:/Open menu/i });
    await menu.click();
    await page.waitForTimeout(90);
    const openState = await page.evaluate(() => {
      const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');
      return { display:getComputedStyle(s).display, transform:getComputedStyle(s).transform, state:s.getAttribute('data-sheet-state'), animations:s.getAnimations({subtree:true}).length };
    });
    await page.waitForTimeout(450);
    const opened = await page.evaluate(() => {
      const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');
      return { display:getComputedStyle(s).display, transform:getComputedStyle(s).transform, state:s.getAttribute('data-sheet-state') };
    });
    const close = page.getByRole('button', { name:/Close menu/i });
    await close.click();
    await page.waitForTimeout(430);
    const closed = await page.evaluate(() => {
      const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');
      return { display:getComputedStyle(s).display, state:s.getAttribute('data-sheet-state') };
    });
    report.specific.menu={openState,opened,closed};
    if (openState.display === 'none' || openState.state !== 'open') fail('menu does not enter visible animated state', {openState});
    if (opened.transform !== 'none' && opened.transform !== 'matrix(1, 0, 0, 1, 0, 0)') fail('menu does not finish at open position', {opened});
    if (closed.display !== 'none' || closed.state !== 'closed') fail('closed menu remains painted', {closed});
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
