import { webkit } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const base='http://127.0.0.1:4173';
const routes=['/','/about/','/services/','/our-work/','/our-work/luckys-cafe-bakery/','/our-work/petti-pathways/','/our-work/pizzeria-coco/','/our-work/folake/','/contact/','/join-our-team/','/sunday-school/','/accessibility/','/privacy-policy/','/terms-and-conditions/','/cookie-policy/','/404.html'];
const browser=await webkit.launch();
const report=[];
for (const route of routes) {
  let context=await browser.newContext({viewport:{width:390,height:844}});
  let page=await context.newPage();
  try {
    await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:45000});
  } catch(e) {
    await context.close();
    context=await browser.newContext({viewport:{width:390,height:844}});
    page=await context.newPage();
    await page.goto(base+route,{waitUntil:'commit',timeout:30000});
    await page.waitForFunction(()=>document.readyState!=='loading',null,{timeout:30000}).catch(()=>{});
  }
  await page.waitForTimeout(400);
  const close=page.locator('[aria-label="The Sunday Reservation"] button[aria-label="Close"]');
  if(await close.count() && await close.first().isVisible().catch(()=>false)){await close.first().evaluate(el=>el.click());await page.waitForTimeout(100);}
  const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
  const serious=axe.violations.filter(v=>['critical','serious'].includes(v.impact)).map(v=>({
    id:v.id, impact:v.impact, help:v.help,
    nodes:v.nodes.map(n=>({target:n.target, html:n.html, failureSummary:n.failureSummary}))
  }));
  if(serious.length) report.push({route,violations:serious});
  console.log('DONE',route,'serious',serious.length);
  await context.close();
}
await browser.close();
console.log('AXE_DETAIL_REPORT_START');
console.log(JSON.stringify(report,null,2));
console.log('AXE_DETAIL_REPORT_END');
if(report.length) process.exitCode=1;
