import { webkit } from 'playwright';
import fs from 'node:fs';
import crypto from 'node:crypto';

const BASE = 'https://sundayandcompany.co';
const outDir = '/tmp/sunday-live-safari';
fs.mkdirSync(outDir, { recursive: true });
const routes = [
  '/', '/about/', '/services/', '/our-work/', '/join-our-team/', '/sunday-school/', '/contact/',
  '/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/', '/our-work/pizzeria-coco/', '/our-work/folake/',
  '/privacy-policy/', '/terms-and-conditions/', '/cookie-policy/', '/accessibility/'
];
function sha(text) { return crypto.createHash('sha256').update(text).digest('hex'); }
function assert(c, m) { if (!c) throw new Error(m); }

const deploy = {};
for (const path of ['/', '/assets/site.css?v=20260912-10', '/assets/rendered-corrections.css?v=20260912-10', '/assets/site.js?v=20260912-10']) {
  const res = await fetch(BASE + path, { redirect: 'follow', headers: { 'cache-control': 'no-cache' } });
  const text = await res.text();
  deploy[path] = {
    status: res.status,
    cache: res.headers.get('cache-control'),
    etag: res.headers.get('etag'),
    age: res.headers.get('age'),
    sha256: sha(text),
    length: text.length,
    hasV10: text.includes('20260912-10') || path.includes('20260912-10')
  };
  assert(res.ok, `Live fetch failed ${path}: ${res.status}`);
}
const localMap = {
  '/': fs.readFileSync('index.html', 'utf8'),
  '/assets/site.css?v=20260912-10': fs.readFileSync('assets/site.css', 'utf8'),
  '/assets/rendered-corrections.css?v=20260912-10': fs.readFileSync('assets/rendered-corrections.css', 'utf8'),
  '/assets/site.js?v=20260912-10': fs.readFileSync('assets/site.js', 'utf8'),
};
for (const [path, text] of Object.entries(localMap)) {
  deploy[path].repoSha256 = sha(text);
  deploy[path].matchesRepo = deploy[path].sha256 === deploy[path].repoSha256;
}
assert(deploy['/'].hasV10, `Live homepage is not serving v10: ${JSON.stringify(deploy['/'])}`);
for (const asset of ['/assets/site.css?v=20260912-10','/assets/rendered-corrections.css?v=20260912-10','/assets/site.js?v=20260912-10']) {
  assert(deploy[asset].matchesRepo, `Live asset differs from repo ${asset}: ${JSON.stringify(deploy[asset])}`);
}
fs.writeFileSync(`${outDir}/deployment.json`, JSON.stringify(deploy, null, 2));
console.log('DEPLOYMENT', JSON.stringify(deploy));

const browser = await webkit.launch();
const summary = [];

async function closeReservation(page) {
  const res = page.locator('[aria-label="The Sunday Reservation"]');
  if (await res.count() && await res.isVisible()) {
    const close = res.getByRole('button', { name: 'Close' });
    if (await close.count()) await close.evaluate(el => el.click());
    await page.waitForTimeout(120);
  }
}

async function inspect(context, label, viewport) {
  for (const route of routes) {
    const page = await context.newPage();
    await page.goto(BASE + route + `?liveqa=${Date.now()}`, { waitUntil: 'networkidle', timeout: 60000 });
    await closeReservation(page);
    const height = await page.evaluate(() => document.documentElement.scrollHeight);
    const step = Math.max(500, Math.floor(viewport.height * 0.75));
    for (let y = 0; y < height; y += step) {
      await page.evaluate(yPos => window.scrollTo(0, yPos), y);
      await page.waitForTimeout(35);
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(250);

    const state = await page.evaluate(() => {
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        return r.width > 1 && r.height > 1 && cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity) > 0;
      };
      const imgs = Array.from(document.images).map((img, i) => {
        const r = img.getBoundingClientRect(); const cs = getComputedStyle(img);
        let p = img.parentElement; const transformedAncestors = [];
        while (p && p !== document.body) { const ps = getComputedStyle(p); if (ps.transform !== 'none' || Number(ps.opacity) < 1) transformedAncestors.push({tag:p.tagName, cls:p.className || '', transform:ps.transform, opacity:ps.opacity}); p = p.parentElement; }
        return { i, src: img.currentSrc || img.src, alt: img.alt || '', complete: img.complete, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
          x:r.x, y:r.y, width:r.width, height:r.height, visible:visible(img), display:cs.display, visibility:cs.visibility, opacity:cs.opacity,
          position:cs.position, transform:cs.transform, loading:img.loading, contentVisibility:cs.contentVisibility, transformedAncestors };
      });
      const badVisible = imgs.filter(x => x.visible && (!x.complete || !x.naturalWidth || x.width <= 1 || x.height <= 1));
      const backgrounds = Array.from(document.querySelectorAll('*')).filter(el => visible(el) && getComputedStyle(el).backgroundImage !== 'none').map(el => ({tag:el.tagName, id:el.id || '', cls:el.className || '', background:getComputedStyle(el).backgroundImage})).slice(0, 80);
      const mail = document.querySelector('footer a[href^="mailto:"]');
      const loc = document.querySelector('footer [data-footer-location]');
      const footer = mail && loc ? {
        mail: {size:getComputedStyle(mail).fontSize, weight:getComputedStyle(mail).fontWeight, family:getComputedStyle(mail).fontFamily, line:getComputedStyle(mail).lineHeight},
        location: {size:getComputedStyle(loc).fontSize, weight:getComputedStyle(loc).fontWeight, family:getComputedStyle(loc).fontFamily, line:getComputedStyle(loc).lineHeight}
      } : null;
      return { title: document.title, scrollHeight: document.documentElement.scrollHeight, imgCount: imgs.length, badVisible, imgs, backgrounds, footer };
    });

    assert(state.badVisible.length === 0, `${label} ${route}: broken visible images ${JSON.stringify(state.badVisible)}`);
    if (state.footer) {
      assert(state.footer.mail.size === state.footer.location.size, `${label} ${route}: footer email size differs ${JSON.stringify(state.footer)}`);
      assert(state.footer.mail.weight === state.footer.location.weight, `${label} ${route}: footer email weight differs ${JSON.stringify(state.footer)}`);
    }
    const slug = route === '/' ? 'home' : route.replace(/^\//,'').replace(/\/$/,'').replace(/\//g,'-');
    await page.screenshot({ path: `${outDir}/${label}-${slug}-full.png`, fullPage: true });
    fs.writeFileSync(`${outDir}/${label}-${slug}.json`, JSON.stringify(state, null, 2));
    summary.push({ label, route, imgCount: state.imgCount, scrollHeight: state.scrollHeight, footer: state.footer, backgrounds: state.backgrounds.length });
    await page.close();
  }
}

const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 Version/18.6 Mobile/15E148 Safari/604.1' });
await inspect(mobile, 'mobile', { width:390, height:844 });
await mobile.close();
const desktop = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await inspect(desktop, 'desktop', { width:1440, height:900 });
await desktop.close();
await browser.close();
fs.writeFileSync(`${outDir}/summary.json`, JSON.stringify(summary, null, 2));
console.log('LIVE_SUMMARY', JSON.stringify(summary));
console.log('Live Safari diagnostic passed');
