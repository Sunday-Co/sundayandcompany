import fs from 'node:fs';
import path from 'node:path';
import { webkit } from 'playwright';

const ROOT = process.cwd();
const OUT = path.join(ROOT, 'qa-artifacts');
fs.mkdirSync(OUT, { recursive: true });

function discoverRoutes(dir = ROOT, rel = '') {
  const routes = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['.git', 'node_modules', 'qa-artifacts'].includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    const nextRel = path.join(rel, entry.name);
    if (entry.isDirectory()) routes.push(...discoverRoutes(full, nextRel));
    else if (entry.isFile() && entry.name === 'index.html') {
      const folder = path.dirname(nextRel).replaceAll('\\', '/');
      routes.push(folder === '.' ? '/' : `/${folder}/`);
    }
  }
  return routes;
}

const routes = [...new Set([...discoverRoutes(), '/404.html'])].sort();
const profiles = [
  { name: 'mobile', viewport: { width: 390, height: 844 }, isMobile: true, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' },
  { name: 'desktop', viewport: { width: 1440, height: 1000 }, isMobile: false, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15' }
];

const report = [];
let failures = 0;
const browser = await webkit.launch();

try {
  for (const profile of profiles) {
    const context = await browser.newContext({ viewport: profile.viewport, isMobile: profile.isMobile, userAgent: profile.userAgent, deviceScaleFactor: 1 });
    const page = await context.newPage();

    for (const route of routes) {
      const url = `http://127.0.0.1:4173${route}`;
      let status = 0;
      const consoleErrors = [];
      const onConsole = (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()); };
      page.on('console', onConsole);
      try {
        const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 12000 });
        status = response?.status() || 0;
        await page.waitForFunction(() => document.querySelector('#dc-root .sc-host') || document.querySelector('[data-screen-label]'), null, { timeout: 7000 }).catch(() => {});
        await page.waitForTimeout(900);

        const metrics = await page.evaluate(() => {
          const root = document.documentElement;
          const body = document.body;
          const sheet = document.querySelector('aside[aria-label="Sunday & Company navigation"]');
          const rect = sheet ? sheet.getBoundingClientRect() : null;
          const sections = Array.from(document.querySelectorAll('[data-screen-label] > section, main section'));
          const transparentSections = sections.filter((node) => Number.parseFloat(getComputedStyle(node).opacity || '1') < 0.05).length;
          return {
            innerWidth: window.innerWidth,
            docScrollWidth: root.scrollWidth,
            bodyScrollWidth: body ? body.scrollWidth : 0,
            docScrollHeight: root.scrollHeight,
            bodyScrollHeight: body ? body.scrollHeight : 0,
            sheetState: sheet?.getAttribute('data-sheet-state') || null,
            sheetDisplay: sheet ? getComputedStyle(sheet).display : null,
            sheetRight: rect ? rect.right : null,
            sheetLeft: rect ? rect.left : null,
            rootWidth: root.getBoundingClientRect().width,
            transparentSections
          };
        });

        const widthOverflow = Math.max(metrics.docScrollWidth, metrics.bodyScrollWidth) - metrics.innerWidth;
        const closedSheetPainted = metrics.sheetState === 'closed' && metrics.sheetDisplay !== 'none';
        const routeSlug = route === '/' ? 'home' : route.replace(/^\//, '').replace(/\/$/, '').replaceAll('/', '__').replace('.html', '');
        const shot = path.join(OUT, `${profile.name}__${routeSlug}.png`);
        await page.screenshot({ path: shot, fullPage: true, animations: 'disabled' });

        const passed = widthOverflow <= 2 && !closedSheetPainted && metrics.transparentSections === 0 && status < 500;
        if (!passed) failures++;
        report.push({ profile: profile.name, route, status, passed, widthOverflow, closedSheetPainted, consoleErrors, metrics, screenshot: path.basename(shot) });
      } catch (error) {
        failures++;
        report.push({ profile: profile.name, route, status, passed: false, error: String(error), consoleErrors });
      } finally {
        page.off('console', onConsole);
      }
    }
    await context.close();
  }
} finally {
  await browser.close();
}

fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify({ routes, profiles: profiles.map(p => p.name), failures, report }, null, 2));
console.log(`Checked ${report.length} route/profile combinations across ${routes.length} routes.`);
console.log(`Failures: ${failures}`);
for (const row of report.filter(r => !r.passed)) console.log(JSON.stringify(row));
if (failures) process.exit(1);
