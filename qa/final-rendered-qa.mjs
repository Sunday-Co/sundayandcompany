import fs from 'node:fs';
import path from 'node:path';
import { webkit } from 'playwright';

const ROOT=process.cwd();
const OUT=path.join(ROOT,'qa-final-artifacts');
fs.mkdirSync(OUT,{recursive:true});

function routes(dir=ROOT,rel=''){
  const out=[];
  for(const e of fs.readdirSync(dir,{withFileTypes:true})){
    if(['.git','node_modules','qa-final-artifacts','qa-rendered-artifacts'].includes(e.name)) continue;
    const full=path.join(dir,e.name), next=path.join(rel,e.name);
    if(e.isDirectory()) out.push(...routes(full,next));
    else if(e.isFile()&&e.name==='index.html'){
      const folder=path.dirname(next).replaceAll('\\','/');
      out.push(folder==='.'?'/':`/${folder}/`);
    }
  }
  return out;
}
const allRoutes=[...new Set([...routes(),'/404.html'])].sort();
const mobile={name:'mobile',viewport:{width:390,height:844},isMobile:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'};
const desktop={name:'desktop',viewport:{width:1440,height:1000},isMobile:false,userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15'};
const report={failures:[],routes:[],specific:{}};
const fail=(msg,data={})=>report.failures.push({msg,...data});
const browser=await webkit.launch();

async function ready(page,route,{suppressReservation=true}={}){
  if(suppressReservation) await page.addInitScript(()=>{try{sessionStorage.setItem('sunday-reservation-seen','true')}catch{}});
  const r=await page.goto(`http://127.0.0.1:4173${route}`,{waitUntil:'commit',timeout:15000});
  await page.waitForFunction(()=>document.readyState!=='loading',null,{timeout:8000}).catch(()=>{});
  await page.waitForFunction(()=>document.querySelector('[data-screen-label],#dc-root .sc-host'),null,{timeout:10000});
  await page.waitForTimeout(800);
  return r?.status()||0;
}
const cs=(n)=>n?getComputedStyle(n):null;

try{
  // 1) Every route: full-page WebKit rendering at mobile and desktop.
  for(const profile of [mobile,desktop]){
    const ctx=await browser.newContext({viewport:profile.viewport,isMobile:profile.isMobile,userAgent:profile.userAgent,deviceScaleFactor:1});
    for(const route of allRoutes){
      const page=await ctx.newPage();
      try{
        const status=await ready(page,route);
        const m=await page.evaluate((mobileMode)=>{
          const root=document.documentElement,body=document.body,runtime=document.querySelector('#dc-root > .sc-host');
          const sheet=document.querySelector('aside[aria-label="Sunday & Company navigation"]');
          const headingBad=[...document.querySelectorAll('h1,h2,h3,h4')].some(h=>getComputedStyle(h).fontWeight!=='400'||[...h.querySelectorAll('em,strong,span')].some(x=>getComputedStyle(x).fontWeight!=='400'));
          return {overflow:Math.max(root.scrollWidth,body?.scrollWidth||0)-innerWidth,runtimeHeight:runtime?.getBoundingClientRect().height||0,scrollHeight:Math.max(root.scrollHeight,body?.scrollHeight||0),headingBad,closedSheetPainted:mobileMode&&sheet?.getAttribute('data-sheet-state')==='closed'&&getComputedStyle(sheet).display!=='none'};
        },profile.name==='mobile');
        const passed=status<500&&m.overflow<=2&&!m.headingBad&&!m.closedSheetPainted&&m.runtimeHeight+4>=m.scrollHeight;
        if(!passed) fail('route baseline',{profile:profile.name,route,status,...m});
        report.routes.push({profile:profile.name,route,passed,status,...m});
        const slug=route==='/'?'home':route.replace(/^\//,'').replace(/\/$/,'').replaceAll('/','__').replace('.html','');
        await page.screenshot({path:path.join(OUT,`${profile.name}__${slug}.png`),fullPage:true,animations:'disabled'});
      }catch(e){fail('route exception',{profile:profile.name,route,error:String(e)});}
      finally{await page.close().catch(()=>{});}
    }
    await ctx.close();
  }

  // 2) Home: visible motion, Vision rules, footer/newsletter hierarchy.
  {
    const ctx=await browser.newContext({viewport:mobile.viewport,isMobile:true,userAgent:mobile.userAgent});
    const page=await ctx.newPage(); await ready(page,'/');
    const heroAnimations=await page.evaluate(()=>document.querySelector('#top')?.getAnimations({subtree:true}).length||0);
    await page.locator('#vision').scrollIntoViewIfNeeded(); await page.waitForTimeout(120);
    const v=await page.evaluate(()=>{
      const size=n=>n?parseFloat(getComputedStyle(n).fontSize):null;
      const quote=document.querySelector('#vision [data-vision-quote]');
      const bodies=[...document.querySelectorAll('#vision [data-vision-body]')];
      const fine=document.querySelector('[aria-label="Newsletter"] [data-news-fineprint]');
      const nInput=document.querySelector('[aria-label="Newsletter"] input');
      const nBtn=document.querySelector('[aria-label="Newsletter"] form button[type="submit"]');
      const footer=[...document.querySelectorAll('footer [data-footer-ui],footer [data-footer-location],footer a[href^="mailto:"]')].map(size);
      return {heroAnimations,visionAnimations:document.querySelector('#vision')?.getAnimations({subtree:true}).length||0,quoteWeight:quote?getComputedStyle(quote).fontWeight:null,bodySizes:bodies.map(size),fine:size(fine),newsInput:size(nInput),newsButton:size(nBtn),footer};
    });
    report.specific.home=v;
    if(v.heroAnimations<1||v.visionAnimations<1) fail('home editorial motion absent',v);
    if(v.quoteWeight!=='400'||new Set(v.bodySizes).size>1) fail('Vision typography inconsistent',v);
    if(!(v.fine<=8&&v.newsInput>=16&&v.newsButton>=10)) fail('footer newsletter hierarchy incorrect',v);
    if(v.footer.length&&Math.max(...v.footer)-Math.min(...v.footer)>.2) fail('footer UI optical sizes inconsistent',v);
    await page.close(); await ctx.close();
  }

  // 3) Project Inquiry: each step measured while it is actually visible.
  {
    const ctx=await browser.newContext({viewport:mobile.viewport,isMobile:true,userAgent:mobile.userAgent});
    const page=await ctx.newPage(); await ready(page,'/');
    await page.getByRole('button',{name:/Start A Project/i}).first().click();
    const dlg=page.locator('[aria-label="Project inquiry"]'); await dlg.waitFor({state:'visible'}); await page.waitForTimeout(150);
    const step1=await page.evaluate(()=>{
      const d=document.querySelector('[aria-label="Project inquiry"]'), style=n=>n?getComputedStyle(n):null;
      const k=d?.querySelector('[data-inquiry-kicker]'),sup=d?.querySelector('[data-inquiry-support]'),lab=d?.querySelector('form[data-inq] label > span:first-child'),inp=d?.querySelector('form[data-inq] input:not([type="hidden"])');
      const stages=[...d?.querySelectorAll('[aria-label="Project inquiry steps"] > span')||[]].map(n=>({text:n.textContent.trim(),size:parseFloat(style(n).fontSize),weight:style(n).fontWeight}));
      return {kicker:k?parseFloat(style(k).fontSize):null,support:sup?parseFloat(style(sup).fontSize):null,supportFamily:sup?style(sup).fontFamily:null,label:lab?parseFloat(style(lab).fontSize):null,labelWeight:lab?style(lab).fontWeight:null,input:inp?parseFloat(style(inp).fontSize):null,stages,animations:d?.getAnimations({subtree:true}).length||0};
    });
    // fill required step 1
    const fields=dlg.locator('form[data-inq] input[required]:visible');
    for(let i=0;i<await fields.count();i++){
      const el=fields.nth(i),type=await el.getAttribute('type'),name=await el.getAttribute('name');
      await el.fill(type==='email'?'qa@example.com':type==='tel'?'2025550100':name==='business'?'QA Studio':'QA User');
    }
    await dlg.getByRole('button',{name:/^Next/i}).click(); await page.waitForTimeout(120);
    const dateBtn=dlg.locator('button[aria-haspopup="dialog"]:visible');
    const dateInfo={size:parseFloat(await dateBtn.evaluate(n=>getComputedStyle(n).fontSize)),height:(await dateBtn.boundingBox())?.height||0};
    await dateBtn.click(); await page.waitForTimeout(80);
    const cal=dlg.locator('[aria-label="Choose a start date"]');
    const calInfo=await cal.evaluate(c=>{const s=n=>parseFloat(getComputedStyle(n).fontSize);const month=c.querySelector(':scope > div:first-child > span'),week=c.querySelector(':scope > div:nth-child(2)'),day=c.querySelector(':scope > div:last-child button');return {month:s(month),weekdays:s(week),day:s(day),dayHeight:day.getBoundingClientRect().height};});
    await cal.locator(':scope > div:last-child button').first().click();
    const budget=dlg.locator('input[name="budget"]:visible'); if(await budget.count()) await budget.fill('2500');
    await dlg.getByRole('button',{name:/^Next/i}).click(); await page.waitForTimeout(120);
    const check=dlg.locator('[role="checkbox"]:visible').first();
    const checkInfo={height:(await check.boundingBox())?.height||0,size:parseFloat(await check.locator('span:last-child').evaluate(n=>getComputedStyle(n).fontSize)),weight:await check.locator('span:last-child').evaluate(n=>getComputedStyle(n).fontWeight)};
    const q={...step1,dateInfo,calInfo,checkInfo}; report.specific.inquiry=q;
    const stageText=q.stages.map(x=>x.text).join(' ');
    if(q.kicker<45) fail('inquiry kicker not large enough',q);
    if(q.support!==13||!String(q.supportFamily).includes('Inter Tight')) fail('inquiry support hierarchy incorrect',q);
    if(q.label<10.5||q.labelWeight!=='400'||q.input!==16) fail('inquiry step 1 functional type incorrect',q);
    if(!/Project Basics/i.test(stageText)||!/Timing & Budget/i.test(stageText)||!/Project Scope/i.test(stageText)||q.stages.some(x=>x.size<9.5||x.weight!=='400')) fail('inquiry stage hierarchy incorrect',q);
    if(dateInfo.size<16||dateInfo.height<43||calInfo.month<10.5||calInfo.weekdays<10.5||calInfo.day<11.5||calInfo.dayHeight<35) fail('date picker functional UI incorrect',q);
    if(checkInfo.height<39||checkInfo.size<10.5||checkInfo.weight!=='400') fail('service checkbox UI incorrect',q);
    if(q.animations<1) fail('inquiry motion absent',q);
    await page.screenshot({path:path.join(OUT,'mobile__inquiry.png'),fullPage:false,animations:'disabled'});
    await page.close(); await ctx.close();
  }

  // 4) Editorial forms that live outside the Inquiry component.
  for(const route of ['/contact/','/sunday-school/','/join-our-team/']){
    const ctx=await browser.newContext({viewport:mobile.viewport,isMobile:true,userAgent:mobile.userAgent});
    const page=await ctx.newPage(); await ready(page,route);
    const forms=await page.evaluate(()=>[...document.querySelectorAll('form[data-editorial-labels]')].map(form=>{const visible=n=>{const s=getComputedStyle(n);return s.display!=='none'&&s.visibility!=='hidden'};const labels=[...form.querySelectorAll('label > span:first-child,div > span:first-child')].filter(visible).map(n=>({size:parseFloat(getComputedStyle(n).fontSize),weight:getComputedStyle(n).fontWeight,text:n.textContent.trim()}));const controls=[...form.querySelectorAll('input:not([type="hidden"]),textarea,select')].filter(visible).map(n=>parseFloat(getComputedStyle(n).fontSize));const submit=[...form.querySelectorAll('button[type="submit"]')].filter(visible).map(n=>parseFloat(getComputedStyle(n).fontSize));const custom=form.querySelector('button[aria-haspopup="listbox"]');return {labels,controls,submit,custom:custom?{size:parseFloat(getComputedStyle(custom).fontSize),weight:getComputedStyle(custom).fontWeight,family:getComputedStyle(custom).fontFamily}:null};}));
    report.specific[`forms:${route}`]=forms;
    for(const f of forms){if(f.labels.some(x=>x.size<10.5||x.weight!=='400')) fail('editorial form labels incorrect',{route,f});if(f.controls.some(x=>x<16)) fail('editorial inputs below 16px',{route,f});if(f.submit.some(x=>x<10)) fail('editorial action too small',{route,f});if(f.custom&&(f.custom.size<16||f.custom.weight!=='400'||!String(f.custom.family).includes('Inter Tight'))) fail('custom form control incorrect',{route,f});}
    if(route==='/contact/'){
      const instruction=await page.evaluate(()=>{const n=document.querySelector('[data-form-instruction]');return n?{size:parseFloat(getComputedStyle(n).fontSize),weight:getComputedStyle(n).fontWeight}:null});
      if(!instruction||instruction.size<10.5||instruction.weight!=='400') fail('contact instruction hierarchy incorrect',{instruction});
    }
    await page.close(); await ctx.close();
  }

  // 5) Reservation popup form and true fine print.
  {
    const ctx=await browser.newContext({viewport:mobile.viewport,isMobile:true,userAgent:mobile.userAgent});
    const page=await ctx.newPage(); await ready(page,'/',{suppressReservation:false});
    const dlg=page.locator('[aria-label="The Sunday Reservation"]'); await dlg.waitFor({state:'visible',timeout:4000});
    const r=await dlg.evaluate(d=>{const s=n=>n?getComputedStyle(n):null,label=d.querySelector('label[for="reservationEmail"]'),input=d.querySelector('#reservationEmail'),btn=d.querySelector('form button[type="submit"]'),fine=d.querySelector('[data-res-fineprint]');return {labelSize:parseFloat(s(label).fontSize),labelWeight:s(label).fontWeight,input:parseFloat(s(input).fontSize),button:parseFloat(s(btn).fontSize),fine:parseFloat(s(fine).fontSize)};});
    report.specific.reservation=r;
    if(r.labelSize<10.5||r.labelWeight!=='400'||r.input<16||r.button<10||r.fine>8) fail('Reservation typography hierarchy incorrect',r);
    await page.close(); await ctx.close();
  }

  // 6) Join cards: front-facing on mobile, detail content expands in page flow.
  {
    const ctx=await browser.newContext({viewport:mobile.viewport,isMobile:true,userAgent:mobile.userAgent});
    const page=await ctx.newPage(); await ready(page,'/join-our-team/');
    const before=await page.evaluate(()=>{const a=document.querySelector('[data-program-cards] > article'),w=a?.querySelector(':scope > div'),b=w?.querySelector(':scope > div:nth-child(2)'),f=w?.querySelector(':scope > button');return {transform:w?getComputedStyle(w).transform:null,back:b?getComputedStyle(b).display:null,label:f?.getAttribute('aria-label')||'',action:f?.querySelector('[data-program-action]')?.textContent.trim()||''};});
    const card=page.locator('[data-program-cards] > article').first(); await card.locator(':scope > div > button').click(); await page.waitForTimeout(100);
    const after=await page.evaluate(()=>{const d=[...document.querySelectorAll('[role="dialog"]')].find(x=>/Fellows Table/.test(x.getAttribute('aria-label')||''));const o=d?.parentElement;return {visible:!!d&&getComputedStyle(d).display!=='none',outerPosition:o?getComputedStyle(o).position:null,outerOverflow:o?getComputedStyle(o).overflowY:null,innerOverflow:d?getComputedStyle(d).overflowY:null,ariaModal:d?.getAttribute('aria-modal')};});
    report.specific.programs={before,after};
    if(before.back!=='none'||!/View full details/i.test(before.label)||!/View Full Details/i.test(before.action)) fail('mobile program card front state incorrect',{before});
    if(!after.visible||after.outerPosition!=='static'||after.outerOverflow!=='visible'||after.innerOverflow!=='visible'||after.ariaModal!=='false') fail('mobile program details not page-flow',{after});
    await page.screenshot({path:path.join(OUT,'mobile__join-program-details.png'),fullPage:true,animations:'disabled'});
    await page.close(); await ctx.close();
  }

  // 7) Mobile menu opens with motion and disappears from rendering after close.
  {
    const ctx=await browser.newContext({viewport:mobile.viewport,isMobile:true,userAgent:mobile.userAgent});
    const page=await ctx.newPage(); await ready(page,'/about/');
    await page.getByRole('button',{name:/Open menu/i}).click(); await page.waitForTimeout(80);
    const open=await page.evaluate(()=>{const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');return {display:getComputedStyle(s).display,state:s.getAttribute('data-sheet-state'),animations:s.getAnimations({subtree:true}).length};});
    await page.getByRole('button',{name:/Close menu/i}).click(); await page.waitForTimeout(450);
    const closed=await page.evaluate(()=>{const s=document.querySelector('aside[aria-label="Sunday & Company navigation"]');return {display:getComputedStyle(s).display,state:s.getAttribute('data-sheet-state')};});
    report.specific.menu={open,closed};
    if(open.display==='none'||open.state!=='open'||open.animations<1) fail('mobile menu visible motion missing',{open});
    if(closed.display!=='none'||closed.state!=='closed') fail('closed menu still painted',{closed});
    await page.close(); await ctx.close();
  }

}finally{await browser.close();}
fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify(report,null,2));
console.log(`Routes checked: ${report.routes.length}`);
console.log(`Failures: ${report.failures.length}`);
for(const f of report.failures) console.log(JSON.stringify(f));
if(report.failures.length) process.exit(1);
