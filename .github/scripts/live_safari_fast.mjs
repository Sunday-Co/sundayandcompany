import { webkit } from 'playwright';
import fs from 'node:fs';
import crypto from 'node:crypto';

const BASE='https://sundayandcompany.co';
const OUT='/tmp/sunday-live-fast';
fs.mkdirSync(OUT,{recursive:true});
const routes=['/','/about/','/services/','/our-work/','/join-our-team/','/sunday-school/','/contact/','/our-work/luckys-cafe-bakery/','/our-work/petti-pathways/','/our-work/pizzeria-coco/','/our-work/folake/','/privacy-policy/','/terms-and-conditions/','/cookie-policy/','/accessibility/'];
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const issues=[];

const deploy={};
for(const p of ['/','/assets/site.css?v=20260912-10','/assets/rendered-corrections.css?v=20260912-10','/assets/site.js?v=20260912-10']){
  try{
    const r=await fetch(BASE+p,{headers:{'cache-control':'no-cache'}}); const t=await r.text();
    deploy[p]={status:r.status,cache:r.headers.get('cache-control'),etag:r.headers.get('etag'),age:r.headers.get('age'),sha256:sha(t),length:t.length,hasV10:t.includes('20260912-10')||p.includes('20260912-10')};
  }catch(e){deploy[p]={error:String(e)};issues.push({type:'fetch',path:p,error:String(e)});}
}
const locals={'/':fs.readFileSync('index.html','utf8'),'/assets/site.css?v=20260912-10':fs.readFileSync('assets/site.css','utf8'),'/assets/rendered-corrections.css?v=20260912-10':fs.readFileSync('assets/rendered-corrections.css','utf8'),'/assets/site.js?v=20260912-10':fs.readFileSync('assets/site.js','utf8')};
for(const [p,t] of Object.entries(locals)){if(deploy[p]){deploy[p].repoSha256=sha(t);deploy[p].matchesRepo=deploy[p].sha256===deploy[p].repoSha256;if(!deploy[p].matchesRepo)issues.push({type:'deploy-mismatch',path:p,live:deploy[p].sha256,repo:deploy[p].repoSha256});}}
if(!deploy['/']?.hasV10)issues.push({type:'homepage-version',detail:'live homepage is not v10'});
fs.writeFileSync(`${OUT}/deployment.json`,JSON.stringify(deploy,null,2));
console.log('FAST_DEPLOY',JSON.stringify(deploy));

const browser=await webkit.launch();
const summary=[];
async function audit(label,viewport,userAgent){
  const context=await browser.newContext({viewport,deviceScaleFactor:1,...(userAgent?{userAgent}:{})});
  for(const route of routes){
    const page=await context.newPage(); const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
    const slug=route==='/'?'home':route.replace(/^\//,'').replace(/\/$/,'').replace(/\//g,'-');
    try{
      const resp=await page.goto(BASE+route+`?captureqa=${Date.now()}`,{waitUntil:'domcontentloaded',timeout:30000});
      await page.waitForTimeout(900);
      const reservation=page.locator('[aria-label="The Sunday Reservation"]');
      if(await reservation.count()&&await reservation.isVisible()){const close=reservation.getByRole('button',{name:'Close'});if(await close.count())await close.evaluate(el=>el.click());}
      try{await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0),null,{timeout:20000});}catch(e){errors.push('image-ready-timeout');}
      const H=await page.evaluate(()=>document.documentElement.scrollHeight);
      for(let y=0;y<H;y+=700){await page.evaluate(v=>window.scrollTo(0,v),y);await page.waitForTimeout(25);}
      await page.evaluate(()=>window.scrollTo(0,0)); await page.waitForTimeout(250);
      const state=await page.evaluate(()=>{
        const imgs=Array.from(document.images).map((i,n)=>{const r=i.getBoundingClientRect(),c=getComputedStyle(i);let p=i.parentElement,anc=[];while(p&&p!==document.body){const s=getComputedStyle(p);if(s.transform!=='none'||Number(s.opacity)<1||s.contentVisibility!=='visible')anc.push({tag:p.tagName,id:p.id||'',cls:String(p.className||''),transform:s.transform,opacity:s.opacity,contentVisibility:s.contentVisibility});p=p.parentElement;}return{n,src:i.currentSrc||i.src,alt:i.alt||'',complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,pixels:i.naturalWidth*i.naturalHeight,width:r.width,height:r.height,display:c.display,visibility:c.visibility,opacity:c.opacity,position:c.position,contentVisibility:c.contentVisibility,anc};});
        const bad=imgs.filter(i=>!i.complete||!i.naturalWidth||!i.naturalHeight);
        const huge=imgs.filter(i=>i.pixels>12000000).map(i=>({src:i.src,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,pixels:i.pixels}));
        const mail=document.querySelector('footer a[href^="mailto:"]'),loc=document.querySelector('footer [data-footer-location]'),ui=document.querySelector('footer [data-footer-ui]');
        const style=el=>el?({size:getComputedStyle(el).fontSize,weight:getComputedStyle(el).fontWeight,line:getComputedStyle(el).lineHeight,family:getComputedStyle(el).fontFamily}):null;
        const clips=Array.from(document.querySelectorAll('*')).filter(el=>{const s=getComputedStyle(el);return s.overflow==='clip'||s.overflowX==='clip'||s.overflowY==='clip';}).length;
        return{scrollHeight:document.documentElement.scrollHeight,imgCount:imgs.length,bad,huge,transformed:imgs.filter(i=>i.anc.length).map(i=>({src:i.src,anc:i.anc})),footer:{mail:style(mail),location:style(loc),ui:style(ui)},clips,imgs};
      });
      if(state.bad.length)issues.push({type:'bad-images',label,route,items:state.bad});
      if(state.huge.length)issues.push({type:'huge-images',label,route,items:state.huge});
      if(state.footer.mail&&state.footer.location&&(state.footer.mail.size!==state.footer.location.size||state.footer.mail.weight!==state.footer.location.weight))issues.push({type:'footer-mismatch',label,route,footer:state.footer});
      let shot='ok';try{await page.screenshot({path:`${OUT}/${label}-${slug}.png`,fullPage:true,animations:'disabled',timeout:30000});}catch(e){shot=String(e);issues.push({type:'screenshot',label,route,error:shot});}
      fs.writeFileSync(`${OUT}/${label}-${slug}.json`,JSON.stringify({...state,httpStatus:resp?.status()||null,errors,shot},null,2));
      summary.push({label,route,status:resp?.status()||null,imgCount:state.imgCount,bad:state.bad.length,huge:state.huge.length,transformed:state.transformed.length,clips:state.clips,footer:state.footer,shot,errors,scrollHeight:state.scrollHeight});
    }catch(e){issues.push({type:'route',label,route,error:String(e)});summary.push({label,route,error:String(e)});}
    await page.close();
  }
  await context.close();
}
await audit('mobile',{width:390,height:844},'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 Version/18.6 Mobile/15E148 Safari/604.1');
await audit('desktop',{width:1440,height:900},null);
await browser.close();
fs.writeFileSync(`${OUT}/summary.json`,JSON.stringify(summary,null,2));fs.writeFileSync(`${OUT}/issues.json`,JSON.stringify(issues,null,2));
console.log('FAST_SUMMARY',JSON.stringify(summary));console.log('FAST_ISSUES',JSON.stringify(issues));console.log(`Focused live audit finished with ${issues.length} issue records`);
