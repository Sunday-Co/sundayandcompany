import { webkit } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const OUT = '/tmp/sunday-capture-integrity';
fs.mkdirSync(OUT, { recursive: true });
const assert = (c, m) => { if (!c) throw new Error(m); };

// Source invariants first. Every exported route must resolve the same Header/Footer.
const rootHeader = fs.readFileSync(path.join(ROOT, 'Site Header.dc.html'), 'utf8');
const rootFooter = fs.readFileSync(path.join(ROOT, 'Site Footer.dc.html'), 'utf8');
function walk(dir, base='') {
  const out=[];
  for (const e of fs.readdirSync(dir,{withFileTypes:true})) {
    if (e.name === '.git' || e.name === 'node_modules' || e.name === '.github') continue;
    const rel=path.join(base,e.name), abs=path.join(dir,e.name);
    if (e.isDirectory()) out.push(...walk(abs,rel)); else out.push(rel);
  }
  return out;
}
const files=walk(ROOT);
for (const rel of files.filter(f=>f.endsWith('Site Header.dc.html'))) assert(fs.readFileSync(path.join(ROOT,rel),'utf8')===rootHeader, `Stale Header copy: ${rel}`);
for (const rel of files.filter(f=>f.endsWith('Site Footer.dc.html'))) assert(fs.readFileSync(path.join(ROOT,rel),'utf8')===rootFooter, `Stale Footer copy: ${rel}`);
for (const rel of files.filter(f=>f.endsWith('.html'))) {
  const t=fs.readFileSync(path.join(ROOT,rel),'utf8');
  if (rel.endsWith('index.html') || rel==='404.html') assert(t.includes('v=20260912-11'), `v11 cache key missing: ${rel}`);
  assert(!/overflow-x\s*:\s*clip/.test(t), `overflow-x:clip remains: ${rel}`);
  assert(!/<div\s+style="[^"]*overflow-y:auto[^"]*">\s*<img\b/i.test(t), `Inner vertical image scrollport remains: ${rel}`);
}
assert(rootFooter.includes('font-size:12.5px;font-weight:300'), 'Root footer email is not source-aligned to body copy');
assert(fs.existsSync(path.join(ROOT,'assets/opt/gallery-capitol.jpg')), 'Optimized Capitol image missing');

const routes=['/','/about/','/services/','/our-work/','/join-our-team/','/sunday-school/','/contact/','/our-work/luckys-cafe-bakery/','/our-work/petti-pathways/','/our-work/pizzeria-coco/','/our-work/folake/','/privacy-policy/','/terms-and-conditions/','/cookie-policy/','/accessibility/'];
const base='http://127.0.0.1:4173';
const browser=await webkit.launch();

async function closeAutoPopup(page){
  const r=page.locator('[aria-label="The Sunday Reservation"]');
  if(await r.count() && await r.isVisible()) { const b=r.getByRole('button',{name:'Close'}); if(await b.count()) await b.evaluate(el=>el.click()); }
}

async function audit(label, viewport) {
  const ctx=await browser.newContext({viewport,deviceScaleFactor:1});
  for(const route of routes){
    const p=await ctx.newPage();
    await p.goto(base+route,{waitUntil:'domcontentloaded',timeout:30000});
    await p.waitForTimeout(850); await closeAutoPopup(p);
    try { await p.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0),null,{timeout:30000}); } catch {}
    const H=await p.evaluate(()=>document.documentElement.scrollHeight);
    for(let y=0;y<H;y+=700){ await p.evaluate(v=>window.scrollTo(0,v),y); await p.waitForTimeout(20); }
    await p.evaluate(()=>window.scrollTo(0,0)); await p.waitForTimeout(180);
    const state=await p.evaluate(()=>{
      const style=el=>el?getComputedStyle(el):null;
      const imgs=Array.from(document.images).map(i=>({
        src:i.getAttribute('src'),
        alt:i.getAttribute('alt')||'',
        id:i.id||'',
        complete:i.complete,
        naturalWidth:i.naturalWidth,
        naturalHeight:i.naturalHeight,
        display:style(i).display,
        visibility:style(i).visibility,
        opacity:style(i).opacity,
        contentVisibility:style(i).contentVisibility,
        intentionalChrome:!!i.closest('header,footer,aside,[role="dialog"],[role="presentation"]'),
        responsiveAlternate:i.id==='map-desk'||i.id==='map-mob'
      }));
      // Every image resource must decode. Hidden duplicates used by closed chrome and the
      // About page's explicit desktop/mobile map pair are allowed to remain hidden at the
      // viewport where their alternate is visible. All other content imagery must paint.
      const broken=imgs.filter(i=>!i.complete||!i.naturalWidth||!i.naturalHeight);
      const hiddenPagePhotos=imgs.filter(i=>!i.intentionalChrome && !i.responsiveAlternate && i.alt && (i.display==='none'||i.visibility==='hidden'||Number(i.opacity)===0));
      const mail=document.querySelector('footer a[href^="mailto:"]'), loc=document.querySelector('footer [data-footer-location]'), ui=document.querySelector('footer [data-footer-ui]');
      const pick=el=>el?({size:style(el).fontSize,weight:style(el).fontWeight,line:style(el).lineHeight,family:style(el).fontFamily}):null;
      const shell=document.querySelector('[data-screen-label]');
      const full=Array.from(document.querySelectorAll('[data-capture-full-image]')).map(el=>({overflow:style(el).overflow,overflowY:style(el).overflowY,maxHeight:style(el).maxHeight,height:style(el).height,imgHeight:el.querySelector('img')?.getBoundingClientRect().height||0}));
      const cap=document.querySelector('img[src="/assets/opt/gallery-capitol.jpg"]');
      const hero=document.querySelector('section#top img[data-sunday-static-hero="true"]');
      return {
        broken,
        hiddenPagePhotos,
        footer:{mail:pick(mail),location:pick(loc),ui:pick(ui)},
        shell:shell?{overflow:style(shell).overflow,overflowX:style(shell).overflowX,overflowY:style(shell).overflowY}:null,
        full,
        cap:cap?{naturalWidth:cap.naturalWidth,naturalHeight:cap.naturalHeight}:null,
        hero:hero?{src:hero.getAttribute('src'),naturalWidth:hero.naturalWidth,naturalHeight:hero.naturalHeight,visibility:style(hero).visibility,opacity:style(hero).opacity,position:style(hero).position}:null
      };
    });
    assert(state.broken.length===0, `${label} ${route} has broken/undecoded images: ${JSON.stringify(state.broken)}`);
    assert(state.hiddenPagePhotos.length===0, `${label} ${route} has hidden page photography: ${JSON.stringify(state.hiddenPagePhotos)}`);
    if(state.footer.mail&&state.footer.location&&state.footer.ui){
      assert(state.footer.mail.size===state.footer.location.size && state.footer.mail.size===state.footer.ui.size, `${label} ${route} footer size mismatch: ${JSON.stringify(state.footer)}`);
      assert(state.footer.mail.weight===state.footer.location.weight && state.footer.mail.weight===state.footer.ui.weight, `${label} ${route} footer weight mismatch: ${JSON.stringify(state.footer)}`);
    }
    if(state.shell) assert(state.shell.overflowY==='visible', `${label} ${route} page shell clips vertical content: ${JSON.stringify(state.shell)}`);
    for(const v of state.full) assert(v.overflowY==='visible' && v.maxHeight==='none' && v.imgHeight>0, `${label} ${route} long image still clipped: ${JSON.stringify(v)}`);
    if(route==='/') assert(state.cap && state.cap.naturalWidth<=1600 && state.cap.naturalWidth*state.cap.naturalHeight<=4500000, `${label} homepage Capitol image too large: ${JSON.stringify(state.cap)}`);
    if(state.hero) assert(state.hero.naturalWidth>0 && state.hero.visibility==='visible' && Number(state.hero.opacity)===1, `${label} ${route} hero not paintable: ${JSON.stringify(state.hero)}`);
    const slug=route==='/'?'home':route.replace(/^\//,'').replace(/\/$/,'').replace(/\//g,'-');
    await p.screenshot({path:`${OUT}/${label}-${slug}.png`,fullPage:true,animations:'disabled',timeout:30000});
    await p.close();
  }
  await ctx.close();
}

await audit('mobile',{width:390,height:844});
await audit('desktop',{width:1440,height:900});

// Print/PDF-style rendering, closer to Safari's Full Page document snapshot path than viewport-only QA.
const printCtx=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
for(const route of ['/','/our-work/luckys-cafe-bakery/','/our-work/petti-pathways/','/our-work/pizzeria-coco/','/our-work/folake/']){
  const p=await printCtx.newPage(); await p.goto(base+route,{waitUntil:'domcontentloaded',timeout:30000}); await p.waitForTimeout(800); await closeAutoPopup(p);
  await p.emulateMedia({media:'print'});
  const s=await p.evaluate(()=>({h:document.documentElement.scrollHeight,bad:Array.from(document.images).filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),clip:Array.from(document.querySelectorAll('[data-capture-full-image]')).filter(el=>getComputedStyle(el).overflowY!=='visible').length}));
  assert(!s.bad.length && s.clip===0, `Print capture ${route} is not image-complete: ${JSON.stringify(s)}`);
  const slug=route==='/'?'home':route.replace(/^\//,'').replace(/\/$/,'').replace(/\//g,'-');
  await p.screenshot({path:`${OUT}/print-${slug}.png`,fullPage:true,animations:'disabled',timeout:30000}); await p.close();
}
await printCtx.close();
await browser.close();
console.log('Capture integrity QA passed');
