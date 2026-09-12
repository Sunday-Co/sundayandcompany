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

const issues = [];
const deploy = {};
for (const path of ['/', '/assets/site.css?v=20260912-10', '/assets/rendered-corrections.css?v=20260912-10', '/assets/site.js?v=20260912-10']) {
  try {
    const res = await fetch(BASE + path, { redirect: 'follow', headers: { 'cache-control': 'no-cache' } });
    const text = await res.text();
    deploy[path] = {
      status: res.status,
      cache: res.headers.get('cache-control'), etag: res.headers.get('etag'), age: res.headers.get('age'),
      sha256: sha(text), length: text.length,
      hasV10: text.includes('20260912-10') || path.includes('20260912-10')
    };
    if (!res.ok) issues.push({ type:'live-fetch', path, status:res.status });
  } catch (error) {
    deploy[path] = { error:String(error) };
    issues.push({ type:'live-fetch-exception', path, error:String(error) });
  }
}
const localMap = {
  '/': fs.readFileSync('index.html', 'utf8'),
  '/assets/site.css?v=20260912-10': fs.readFileSync('assets/site.css', 'utf8'),
  '/assets/rendered-corrections.css?v=20260912-10': fs.readFileSync('assets/rendered-corrections.css', 'utf8'),
  '/assets/site.js?v=20260912-10': fs.readFileSync('assets/site.js', 'utf8'),
};
for (const [path, text] of Object.entries(localMap)) {
  if (!deploy[path]) continue;
  deploy[path].repoSha256 = sha(text);
  deploy[path].matchesRepo = deploy[path].sha256 === deploy[path].repoSha256;
  if (!deploy[path].matchesRepo) issues.push({ type:'deploy-mismatch', path, live:deploy[path].sha256, repo:deploy[path].repoSha256 });
}
if (!deploy['/']?.hasV10) issues.push({ type:'homepage-version', detail:'Live homepage does not advertise v10' });
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
    const consoleErrors = [];
    page.on('pageerror', e => consoleErrors.push(String(e)));
    try {
      const response = await page.goto(BASE + route + `?liveqa=${Date.now()}`, { waitUntil:'networkidle', timeout:60000 });
      await closeReservation(page);
      const height = await page.evaluate(() => document.documentElement.scrollHeight);
      const step = Math.max(500, Math.floor(viewport.height * .75));
      for (let y = 0; y < height; y += step) {
        await page.evaluate(yPos => window.scrollTo(0, yPos), y);
        await page.waitForTimeout(40);
      }
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(350);
      const state = await page.evaluate(() => {
        const visible = el => {
          const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
          return r.width > 1 && r.height > 1 && cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity) > 0;
        };
        const imgs = Array.from(document.images).map((img,i) => {
          const r=img.getBoundingClientRect(), cs=getComputedStyle(img);
          let p=img.parentElement; const transformedAncestors=[];
          while (p && p!==document.body) {
            const ps=getComputedStyle(p);
            if (ps.transform!=='none' || Number(ps.opacity)<1 || ps.contentVisibility!=='visible') transformedAncestors.push({tag:p.tagName,id:p.id||'',cls:String(p.className||''),transform:ps.transform,opacity:ps.opacity,contentVisibility:ps.contentVisibility});
            p=p.parentElement;
          }
          return {i,src:img.currentSrc||img.src,alt:img.alt||'',complete:img.complete,naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,
            x:r.x,y:r.y,width:r.width,height:r.height,visible:visible(img),display:cs.display,visibility:cs.visibility,opacity:cs.opacity,
            position:cs.position,transform:cs.transform,loading:img.loading,decoding:img.decoding,contentVisibility:cs.contentVisibility,transformedAncestors};
        });
        const badVisible=imgs.filter(x=>x.visible&&(!x.complete||!x.naturalWidth||x.width<=1||x.height<=1));
        const huge=imgs.filter(x=>x.naturalWidth*x.naturalHeight>12000000).map(x=>({src:x.src,naturalWidth:x.naturalWidth,naturalHeight:x.naturalHeight,pixels:x.naturalWidth*x.naturalHeight}));
        const transformed=imgs.filter(x=>x.transformedAncestors.length).map(x=>({src:x.src,ancestors:x.transformedAncestors}));
        const mail=document.querySelector('footer a[href^="mailto:"]');
        const loc=document.querySelector('footer [data-footer-location]');
        const firstFooterUi=document.querySelector('footer [data-footer-ui]');
        const footer=mail&&loc?{
          mail:{size:getComputedStyle(mail).fontSize,weight:getComputedStyle(mail).fontWeight,family:getComputedStyle(mail).fontFamily,line:getComputedStyle(mail).lineHeight},
          location:{size:getComputedStyle(loc).fontSize,weight:getComputedStyle(loc).fontWeight,family:getComputedStyle(loc).fontFamily,line:getComputedStyle(loc).lineHeight},
          ui:firstFooterUi?{size:getComputedStyle(firstFooterUi).fontSize,weight:getComputedStyle(firstFooterUi).fontWeight,family:getComputedStyle(firstFooterUi).fontFamily,line:getComputedStyle(firstFooterUi).lineHeight}:null
        }:null;
        const clips=Array.from(document.querySelectorAll('*')).filter(el=>{
          const cs=getComputedStyle(el); return cs.overflow==='clip'||cs.overflowX==='clip'||cs.overflowY==='clip';
        }).slice(0,100).map(el=>({tag:el.tagName,id:el.id||'',cls:String(el.className||''),overflow:getComputedStyle(el).overflow,overflowX:getComputedStyle(el).overflowX,overflowY:getComputedStyle(el).overflowY}));
        return {title:document.title,scrollHeight:document.documentElement.scrollHeight,imgCount:imgs.length,badVisible,huge,transformed,imgs,footer,clipCount:clips.length,clips};
      });
      if (state.badVisible.length) issues.push({type:'broken-visible-images',label,route,items:state.badVisible});
      if (state.huge.length) issues.push({type:'huge-decoded-images',label,route,items:state.huge});
      if (state.footer && (state.footer.mail.size!==state.footer.location.size || state.footer.mail.weight!==state.footer.location.weight)) issues.push({type:'footer-mismatch',label,route,footer:state.footer});
      const slug=route==='/'?'home':route.replace(/^\//,'').replace(/\/$/,'').replace(/\//g,'-');
      let screenshot='ok';
      try { await page.screenshot({path:`${outDir}/${label}-${slug}-full.png`,fullPage:true,animations:'disabled'}); }
      catch (e) { screenshot=String(e); issues.push({type:'fullpage-screenshot-error',label,route,error:String(e)}); }
      fs.writeFileSync(`${outDir}/${label}-${slug}.json`, JSON.stringify({...state,httpStatus:response?.status()||null,consoleErrors,screenshot},null,2));
      summary.push({label,route,httpStatus:response?.status()||null,imgCount:state.imgCount,scrollHeight:state.scrollHeight,badVisible:state.badVisible.length,huge:state.huge.length,transformed:state.transformed.length,clipCount:state.clipCount,footer:state.footer,screenshot,consoleErrors});
    } catch (error) {
      issues.push({type:'route-diagnostic-exception',label,route,error:String(error)});
      summary.push({label,route,error:String(error),consoleErrors});
    } finally { await page.close(); }
  }
}
const mobile=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 Version/18.6 Mobile/15E148 Safari/604.1'});
await inspect(mobile,'mobile',{width:390,height:844}); await mobile.close();
const desktop=await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1});
await inspect(desktop,'desktop',{width:1440,height:900}); await desktop.close();
await browser.close();
fs.writeFileSync(`${outDir}/summary.json`,JSON.stringify(summary,null,2));
fs.writeFileSync(`${outDir}/issues.json`,JSON.stringify(issues,null,2));
console.log('LIVE_SUMMARY',JSON.stringify(summary));
console.log('LIVE_ISSUES',JSON.stringify(issues));
console.log(`Live Safari diagnostic completed with ${issues.length} recorded issue(s)`);
