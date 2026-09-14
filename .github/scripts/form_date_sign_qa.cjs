const { webkit } = require('/tmp/sunday-polish/node_modules/playwright');
const base='http://127.0.0.1:4173';
const failures=[];
const check=(name,ok,detail='')=>{console.log(`${ok?'PASS':'FAIL'} | ${name}${detail?' | '+detail:''}`);if(!ok)failures.push(name+(detail?' :: '+detail:''));};

async function closeReservation(page){
  const c=page.locator('[aria-label="The Sunday Reservation"] button[aria-label="Close"]');
  if(await c.count()&&await c.first().isVisible().catch(()=>false)) await c.first().click();
}
async function openInquiry(page){
  await page.evaluate(()=>window.dispatchEvent(new CustomEvent('sunday:open-inquiry')));
  const modal=page.locator('[role="dialog"][aria-label="Project inquiry"]');
  await modal.waitFor({state:'visible'});
  return modal;
}
async function fillStep1(root){
  await root.locator('input[name="name"]').fill('QA Test');
  await root.locator('input[name="email"]').fill('qa@example.com');
  await root.locator('input[name="phone"]').fill('2025550123');
  await root.locator('input[name="business"]').fill('QA Studio');
  await root.getByRole('button',{name:/^Next/}).click();
  await root.locator('[data-step="2"]').first().waitFor({state:'visible'});
}
async function verifyPrivacy(root,prefix){
  const privacy=root.locator('[data-form-privacy]').first();
  const ps=await privacy.evaluate(el=>({fontSize:getComputedStyle(el).fontSize,whiteSpace:getComputedStyle(el).whiteSpace,height:el.getBoundingClientRect().height,scrollWidth:el.scrollWidth,clientWidth:el.clientWidth}));
  check(`${prefix} privacy stays on one line`,ps.whiteSpace==='nowrap'&&ps.height<18&&ps.scrollWidth<=ps.clientWidth+2,JSON.stringify(ps));
}

(async()=>{
  const browser=await webkit.launch();
  for(const cfg of [{name:'desktop',width:1440,height:900},{name:'mobile',width:390,height:844}]){
    const page=await browser.newPage({viewport:{width:cfg.width,height:cfg.height}});

    await page.goto(base+'/',{waitUntil:'networkidle',timeout:60000});
    await page.waitForTimeout(250); await closeReservation(page);
    const modal=await openInquiry(page);
    await fillStep1(modal);
    const label=modal.locator('[data-start-date-label]').first();
    const ls=await label.evaluate(el=>({size:getComputedStyle(el).fontSize,family:getComputedStyle(el).fontFamily,weight:getComputedStyle(el).fontWeight}));
    check(`${cfg.name} header start-date label`,parseFloat(ls.size)<=10&&ls.family.includes('Inter Tight'),JSON.stringify(ls));
    await modal.locator('input[name="budget"]').fill('2500');
    const trigger=modal.getByRole('button',{name:/Select A Date|\d{4}-\d{2}-\d{2}/}).first();
    await trigger.evaluate(el=>el.scrollIntoView({block:'center',inline:'nearest'}));
    await page.waitForTimeout(100);
    const overlay=modal.locator('..');
    const before=await overlay.evaluate(el=>({scrollHeight:el.scrollHeight,clientHeight:el.clientHeight,scrollTop:el.scrollTop}));
    await trigger.click(); await page.waitForTimeout(120);
    const panel=modal.locator('[data-date-panel]').first();
    const box=await panel.boundingBox(); const vp=page.viewportSize();
    const after=await overlay.evaluate(el=>({scrollHeight:el.scrollHeight,clientHeight:el.clientHeight,scrollTop:el.scrollTop}));
    check(`${cfg.name} header calendar does not add scroll`,after.scrollHeight<=before.scrollHeight+4,JSON.stringify({before,after}));
    check(`${cfg.name} header calendar fits viewport`,!!box&&box.y>=0&&box.y+box.height<=vp.height+1,JSON.stringify({box,vp}));
    await page.screenshot({path:`qa-artifacts/${cfg.name}-header-date-open.png`,fullPage:false});
    await trigger.click();
    await modal.getByRole('button',{name:/^Next/}).click();
    await modal.locator('[role="checkbox"]').first().click();
    await verifyPrivacy(modal,`${cfg.name} header`);
    await page.screenshot({path:`qa-artifacts/${cfg.name}-header-privacy.png`,fullPage:false});
    await page.keyboard.press('Escape');

    await page.goto(base+'/services/',{waitUntil:'networkidle',timeout:60000});
    await page.waitForTimeout(250); await closeReservation(page);
    const form=page.locator('form[data-inq]').first();
    await form.scrollIntoViewIfNeeded();
    await fillStep1(form);
    const sl=form.locator('[data-start-date-label]').first();
    const sls=await sl.evaluate(el=>({size:getComputedStyle(el).fontSize,family:getComputedStyle(el).fontFamily}));
    check(`${cfg.name} services start-date label`,parseFloat(sls.size)<=10&&sls.family.includes('Inter Tight'),JSON.stringify(sls));
    await form.locator('input[name="budget"]').fill('2500');
    const st=form.getByRole('button',{name:/Select A Date|\d{4}-\d{2}-\d{2}/}).first();
    await st.evaluate(el=>el.scrollIntoView({block:'center',inline:'nearest'}));
    const bodyBefore=await page.evaluate(()=>document.documentElement.scrollHeight);
    await st.click(); await page.waitForTimeout(120);
    const spanel=form.locator('[data-date-panel]').first(); const sb=await spanel.boundingBox(); const svp=page.viewportSize();
    const bodyAfter=await page.evaluate(()=>document.documentElement.scrollHeight);
    check(`${cfg.name} services calendar does not grow page`,bodyAfter<=bodyBefore+4,JSON.stringify({bodyBefore,bodyAfter}));
    check(`${cfg.name} services calendar fits viewport`,!!sb&&sb.y>=0&&sb.y+sb.height<=svp.height+1,JSON.stringify({sb,svp}));
    await page.screenshot({path:`qa-artifacts/${cfg.name}-services-date-open.png`,fullPage:false});
    await st.click();
    await form.getByRole('button',{name:/^Next/}).click();
    await form.locator('[role="checkbox"]').first().click();
    await verifyPrivacy(form,`${cfg.name} services`);
    await page.screenshot({path:`qa-artifacts/${cfg.name}-services-privacy.png`,fullPage:false});

    await page.goto(base+'/',{waitUntil:'networkidle',timeout:60000});
    await page.waitForTimeout(250); await closeReservation(page);
    await page.evaluate(()=>{window.__signStarts=0;const el=document.querySelector('[data-sign-swing]');if(el)el.addEventListener('animationstart',()=>window.__signStarts++);});
    const sign=page.locator('[data-sign]').first(); await sign.scrollIntoViewIfNeeded(); await page.waitForTimeout(220);
    const swing=page.locator('[data-sign-swing]').first(); const open=page.locator('[data-sign-open]').first();
    const anim=await swing.evaluate(el=>getComputedStyle(el).animationName);
    const openAnim=await open.evaluate(el=>({name:getComputedStyle(el).animationName,duration:getComputedStyle(el).animationDuration}));
    check(`${cfg.name} sign swings on entry`,anim.includes('sc-rock')&&anim.includes('sc-sway'),anim);
    check(`${cfg.name} sign slow pulse`,openAnim.name.includes('sc-neon')&&openAnim.duration.includes('5.6s'),JSON.stringify(openAnim));
    const startsBefore=await page.evaluate(()=>window.__signStarts||0);
    await open.click({force:true}); await page.waitForTimeout(180);
    const startsAfter=await page.evaluate(()=>window.__signStarts||0);
    check(`${cfg.name} sign re-swings on touch`,startsAfter>startsBefore,JSON.stringify({startsBefore,startsAfter}));
    await page.screenshot({path:`qa-artifacts/${cfg.name}-open-sign.png`,fullPage:false});
    await page.close();
  }
  await browser.close();
  if(failures.length){console.error('\nFAILURES\n'+failures.join('\n'));process.exit(1);}
})().catch(e=>{console.error(e);process.exit(2);});
