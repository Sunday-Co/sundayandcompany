import { webkit } from 'playwright';
import assert from 'node:assert';
import fs from 'node:fs';

const base = 'http://127.0.0.1:4173';
const outDir = 'final-qa-v4';
fs.mkdirSync(outDir, { recursive: true });

const num = v => Number(String(v).replace('px', ''));
const near = (v, target, tolerance = .38) => Math.abs(num(v) - target) <= tolerance;
const isVisible = async locator => {
  try { return await locator.count() > 0 && await locator.first().isVisible(); }
  catch { return false; }
};
const style = async (locator, pseudo = null) => locator.first().evaluate((el, pseudo) => {
  const s = getComputedStyle(el, pseudo);
  const r = el.getBoundingClientRect();
  return {
    fontFamily: s.fontFamily,
    fontSize: s.fontSize,
    fontWeight: s.fontWeight,
    fontStyle: s.fontStyle,
    letterSpacing: s.letterSpacing,
    lineHeight: s.lineHeight,
    textTransform: s.textTransform,
    overflow: s.overflow,
    overflowX: s.overflowX,
    overflowY: s.overflowY,
    position: s.position,
    transform: s.transform,
    willChange: s.willChange,
    display: s.display,
    visibility: s.visibility,
    opacity: s.opacity,
    backgroundColor: s.backgroundColor,
    color: s.color,
    rect: { x: r.x, y: r.y, top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height },
  };
}, pseudo);

const closeReservation = async page => {
  const close = page.locator('[aria-label="The Sunday Reservation"] button[aria-label="Close"]');
  if (await isVisible(close)) {
    await close.first().evaluate(el => el.click());
    await page.waitForTimeout(220);
  }
};
const decodeImages = async page => page.evaluate(async () => {
  await Promise.all([...document.images].map(img => {
    if (img.complete && img.naturalWidth) return Promise.resolve();
    return img.decode().catch(() => {});
  }));
});

async function testCore(name, viewport) {
  const browser = await webkit.launch();
  const page = await browser.newPage({ viewport });
  const report = {};

  await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1100);
  await decodeImages(page);

  // Reservation must be solid, readable, and genuinely in the viewport.
  const res = page.locator('[aria-label="The Sunday Reservation"]');
  assert.ok(await isVisible(res), `${name}: Reservation did not open`);
  const resStyle = await style(res);
  const resSupport = await style(res.locator('h2 + p'));
  const resFine = await style(res.locator('[data-res-fineprint]').first());
  assert.strictEqual(resStyle.opacity, '1', `${name}: Reservation opacity ${resStyle.opacity}`);
  assert.strictEqual(resStyle.backgroundColor, 'rgb(255, 253, 248)', `${name}: Reservation background ${resStyle.backgroundColor}`);
  assert.ok(resStyle.rect.top >= 0 && resStyle.rect.top < viewport.height, `${name}: Reservation outside viewport ${JSON.stringify(resStyle.rect)}`);
  assert.ok(resStyle.rect.width > (name === 'mobile' ? 340 : 700), `${name}: Reservation width ${resStyle.rect.width}`);
  assert.ok(near(resSupport.fontSize, name === 'mobile' ? 11.5 : 11.25), `${name}: Reservation support ${resSupport.fontSize}`);
  assert.ok(near(resFine.fontSize, name === 'mobile' ? 8 : 8.5), `${name}: Reservation fine print ${resFine.fontSize}`);
  assert.ok(num(resFine.lineHeight) >= 10.5, `${name}: Reservation fine-print line-height ${resFine.lineHeight}`);
  await page.screenshot({ path: `${outDir}/${name}-reservation.png` });
  await closeReservation(page);

  // Footer email should optically match surrounding body copy, not read smaller.
  await page.locator('footer').scrollIntoViewIfNeeded();
  await page.waitForTimeout(100);
  const footerEmail = await style(page.locator('footer a[href^="mailto:"]'));
  const footerLocation = await style(page.locator('footer [data-footer-location]'));
  assert.ok(near(footerEmail.fontSize, 13.25), `${name}: footer email ${footerEmail.fontSize}`);
  assert.ok(near(footerLocation.fontSize, 12.5), `${name}: footer location ${footerLocation.fontSize}`);
  assert.strictEqual(footerEmail.fontWeight, '300', `${name}: footer email weight ${footerEmail.fontWeight}`);
  assert.strictEqual(footerLocation.fontWeight, '300', `${name}: footer location weight ${footerLocation.fontWeight}`);
  assert.strictEqual(footerEmail.opacity, '1', `${name}: footer email opacity ${footerEmail.opacity}`);
  await page.screenshot({ path: `${outDir}/${name}-footer.png` });

  // The outer document, not nested generated shells, must own vertical page scrolling.
  const roots = await page.evaluate(() => [
    document.documentElement,
    document.body,
    document.querySelector('#dc-root'),
    document.querySelector('#dc-root > .sc-host'),
  ].filter(Boolean).map(el => ({
    tag: el.tagName,
    id: el.id,
    cls: String(el.className || ''),
    overflowY: getComputedStyle(el).overflowY,
    scrollHeight: el.scrollHeight,
    clientHeight: el.clientHeight,
  })));
  for (const root of roots) {
    assert.ok(!['auto', 'scroll'].includes(root.overflowY), `${name}: nested root scroller ${JSON.stringify(root)}`);
  }

  // Homepage hero must exist as a normal, decoded image in the paint tree.
  await page.evaluate(() => scrollTo(0, 0));
  const hero = page.locator('#top img[data-sunday-static-hero="true"]');
  assert.strictEqual(await hero.count(), 1, `${name}: static hero missing`);
  const heroInfo = await hero.evaluate(img => {
    const s = getComputedStyle(img), r = img.getBoundingClientRect();
    return {
      complete: img.complete, nw: img.naturalWidth, nh: img.naturalHeight,
      position: s.position, transform: s.transform, willChange: s.willChange,
      opacity: s.opacity, visibility: s.visibility,
      rect: { width: r.width, height: r.height },
    };
  });
  assert.ok(heroInfo.complete && heroInfo.nw > 0, `${name}: hero not decoded`);
  assert.strictEqual(heroInfo.position, 'static', `${name}: hero position ${heroInfo.position}`);
  assert.strictEqual(heroInfo.transform, 'none', `${name}: hero transform ${heroInfo.transform}`);
  assert.strictEqual(heroInfo.willChange, 'auto', `${name}: hero will-change ${heroInfo.willChange}`);
  assert.strictEqual(heroInfo.opacity, '1', `${name}: hero opacity ${heroInfo.opacity}`);
  assert.strictEqual(heroInfo.visibility, 'visible', `${name}: hero visibility ${heroInfo.visibility}`);
  assert.ok(heroInfo.rect.width > 300 && heroInfo.rect.height > 500, `${name}: hero rect ${JSON.stringify(heroInfo.rect)}`);

  // Project Inquiry must be solid and actually occupy the mobile/desktop viewport.
  const start = page.getByText('Start A Project', { exact: true }).first();
  await start.evaluate(el => el.click());
  await page.waitForTimeout(450);
  const inquiry = page.locator('[aria-label="Project inquiry"]');
  assert.ok(await isVisible(inquiry), `${name}: Inquiry not visible`);
  const inquiryStyle = await style(inquiry);
  assert.strictEqual(inquiryStyle.opacity, '1', `${name}: Inquiry opacity ${inquiryStyle.opacity}`);
  assert.ok(inquiryStyle.rect.width > (name === 'mobile' ? 340 : 700), `${name}: Inquiry width ${inquiryStyle.rect.width}`);
  assert.ok(inquiryStyle.rect.height > 500, `${name}: Inquiry height ${inquiryStyle.rect.height}`);
  if (name === 'mobile') {
    assert.ok(inquiryStyle.rect.top >= 0 && inquiryStyle.rect.top <= 30, `${name}: Inquiry top ${inquiryStyle.rect.top}`);
    assert.ok(inquiryStyle.rect.left >= 0 && inquiryStyle.rect.right <= viewport.width + 1, `${name}: Inquiry horizontal rect ${JSON.stringify(inquiryStyle.rect)}`);
  } else {
    assert.ok(inquiryStyle.rect.top >= 20 && inquiryStyle.rect.top < 150, `${name}: Inquiry desktop top ${inquiryStyle.rect.top}`);
  }
  const inquiryReceipt = await style(inquiry.locator(':scope > div').first());
  assert.strictEqual(inquiryReceipt.backgroundColor, 'rgb(255, 253, 248)', `${name}: Inquiry receipt background ${inquiryReceipt.backgroundColor}`);
  assert.strictEqual(inquiryReceipt.opacity, '1', `${name}: Inquiry receipt opacity ${inquiryReceipt.opacity}`);
  const closeBtn = await style(inquiry.locator('button[aria-label="Close"]'));
  assert.ok(closeBtn.rect.top >= 0 && closeBtn.rect.top < viewport.height, `${name}: Inquiry close outside viewport ${JSON.stringify(closeBtn.rect)}`);

  const iqHeading = await style(inquiry.locator('h2'));
  const iqSupport = await style(inquiry.locator('[data-inquiry-support]'));
  const iqKicker = await style(inquiry.locator('[data-inquiry-kicker]'));
  const iqLabel = await style(inquiry.locator('form[data-inq] label > span:first-child').first());
  assert.ok(iqHeading.fontFamily.includes('Playfair'), `${name}: Inquiry heading not Playfair`);
  assert.strictEqual(iqHeading.textTransform, 'uppercase', `${name}: Inquiry heading not uppercase`);
  assert.strictEqual(iqSupport.textTransform, 'uppercase', `${name}: Inquiry support not uppercase`);
  assert.ok(iqKicker.fontFamily.includes('Inter Tight'), `${name}: Inquiry kicker not Inter Tight`);
  assert.ok(near(iqHeading.fontSize, name === 'mobile' ? 24 : 31), `${name}: Inquiry heading ${iqHeading.fontSize}`);
  assert.ok(near(iqSupport.fontSize, name === 'mobile' ? 9.25 : 9.75), `${name}: Inquiry support ${iqSupport.fontSize}`);
  assert.ok(near(iqLabel.fontSize, name === 'mobile' ? 10 : 10.25), `${name}: Inquiry label ${iqLabel.fontSize}`);
  await page.screenshot({ path: `${outDir}/${name}-inquiry.png` });
  const inquiryClose = inquiry.locator('button[aria-label="Close"]');
  if (await isVisible(inquiryClose)) await inquiryClose.evaluate(el => el.click());

  // Contact form visible labels must use the smaller utility hierarchy.
  await page.goto(base + '/contact/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  await closeReservation(page);
  const contactForm = page.locator('form[data-editorial-labels]').first();
  assert.ok(await contactForm.count(), `${name}: Contact form missing`);
  const contactLabel = await style(contactForm.locator('label > span:first-child').first());
  assert.ok(num(contactLabel.fontSize) <= 10.5, `${name}: Contact visible label ${contactLabel.fontSize}`);
  assert.ok(contactLabel.letterSpacing !== 'normal', `${name}: Contact label tracking missing`);
  const contactH1 = page.locator('h1').first();
  const contactScript = contactH1.locator('em').first();
  if (await contactScript.count()) {
    const ch = await style(contactH1), cs = await style(contactScript);
    assert.ok(num(cs.fontSize) >= num(ch.fontSize) * .9, `${name}: Contact decorative type too small ${cs.fontSize} vs ${ch.fontSize}`);
  }
  await page.screenshot({ path: `${outDir}/${name}-contact.png` });

  // Join cards retain their behavior, while small archive metadata remains legible.
  await page.goto(base + '/join-our-team/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  await closeReservation(page);
  const joinH1 = page.locator('h1').first();
  const joinScript = joinH1.locator('em').first();
  if (await joinScript.count()) {
    const jh = await style(joinH1), js = await style(joinScript);
    assert.ok(num(js.fontSize) >= num(jh.fontSize) * .8, `${name}: Join decorative type too small ${js.fontSize} vs ${jh.fontSize}`);
  }
  const card = page.locator('[data-program-cards] > article').first();
  assert.ok(await card.count(), `${name}: program card missing`);
  const frontButton = card.locator('button').first();
  const spans = frontButton.locator('span');
  const visibleSizes = [];
  for (let i = 0; i < await spans.count(); i++) {
    const loc = spans.nth(i);
    if (await loc.isVisible().catch(() => false)) {
      const st = await style(loc);
      if (num(st.fontSize) > 0) visibleSizes.push(num(st.fontSize));
    }
  }
  assert.ok(visibleSizes.some(v => v >= 8), `${name}: Join card metadata ${visibleSizes}`);
  await frontButton.evaluate(el => el.click());
  await page.waitForTimeout(950);
  const details = card.getByText('View Full Details', { exact: true });
  assert.ok(await isVisible(details), `${name}: View Full Details unavailable after flip`);
  await details.evaluate(el => el.click());
  await page.waitForTimeout(250);
  const modal = page.locator('[role="dialog"][aria-label="The Fellows Table"]');
  assert.ok(await isVisible(modal), `${name}: Fellows modal not visible`);
  const modalMeta = await modal.locator(':scope > div:nth-child(2)').evaluate(el => getComputedStyle(el, '::before').fontSize);
  const stamp = await modal.evaluate(el => getComputedStyle(el, '::after').fontSize);
  assert.ok(num(modalMeta) >= (name === 'mobile' ? 7.2 : 8), `${name}: archive meta ${modalMeta}`);
  assert.ok(num(stamp) >= (name === 'mobile' ? 7 : 7.5), `${name}: archive stamp ${stamp}`);
  await page.screenshot({ path: `${outDir}/${name}-join-modal.png` });

  report.reservation = { style: resStyle, support: resSupport, fine: resFine };
  report.footer = { email: footerEmail, location: footerLocation };
  report.roots = roots;
  report.hero = heroInfo;
  report.inquiry = { style: inquiryStyle, receipt: inquiryReceipt, heading: iqHeading, support: iqSupport, kicker: iqKicker, label: iqLabel };
  report.contactLabel = contactLabel;
  report.join = { visibleSizes, modalMeta, stamp };
  await browser.close();
  return report;
}

async function routeImageSweep() {
  const browser = await webkit.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const routes = ['/', '/about/', '/services/', '/join-our-team/', '/sunday-school/', '/contact/', '/our-work/', '/our-work/luckys-cafe-bakery/', '/our-work/petti-pathways/', '/our-work/pizzeria-coco/', '/our-work/folake/'];
  const result = {};
  for (const route of routes) {
    await page.goto(base + route, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(260);
    await closeReservation(page);
    const height = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < height; y += 700) {
      await page.evaluate(y => scrollTo(0, y), y);
      await page.waitForTimeout(10);
    }
    await decodeImages(page);
    const bad = await page.evaluate(() => [...document.images].filter(img => !img.complete || img.naturalWidth === 0).map(img => img.currentSrc || img.src));
    assert.deepStrictEqual(bad, [], `${route}: broken/unloaded images ${bad.join(', ')}`);
    result[route] = await page.evaluate(() => ({ images: document.images.length, height: document.documentElement.scrollHeight }));
  }
  await browser.close();
  return result;
}

async function portfolioBehavior() {
  const browser = await webkit.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(base + '/our-work/luckys-cafe-bakery/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(450);
  await closeReservation(page);
  const target = page.locator('#email');
  const before = await target.evaluate(el => ({ opacity: el.style.opacity, transform: el.style.transform, duration: getComputedStyle(el).transitionDuration }));
  assert.strictEqual(before.opacity, '0', `portfolio reveal initial opacity ${before.opacity}`);
  assert.ok(before.transform.includes('translateY'), `portfolio reveal initial transform ${before.transform}`);
  assert.notStrictEqual(before.duration, '0s', 'portfolio reveal transition removed');
  await target.scrollIntoViewIfNeeded();
  await page.waitForTimeout(900);
  assert.strictEqual(await target.evaluate(el => el.style.opacity), '1', 'portfolio reveal did not animate in');
  const frame = page.locator('img[alt="Lucky’s Café and Bakery homepage"]').locator('..');
  const frameStyle = await frame.evaluate(el => ({ maxHeight: getComputedStyle(el).maxHeight, overflowY: getComputedStyle(el).overflowY }));
  assert.strictEqual(frameStyle.maxHeight, '640px', `portfolio frame height ${frameStyle.maxHeight}`);
  assert.ok(['auto', 'scroll'].includes(frameStyle.overflowY), `portfolio frame overflow ${frameStyle.overflowY}`);
  await browser.close();
  return { before, frameStyle };
}

async function captureChecks() {
  const result = {};
  const noJsBrowser = await webkit.launch();
  const noJsPage = await noJsBrowser.newPage({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
  await noJsPage.goto(base + '/', { waitUntil: 'domcontentloaded' });
  await decodeImages(noJsPage);
  const noJsHero = await noJsPage.locator('#top img[data-sunday-static-hero="true"]').evaluate(img => ({ complete: img.complete, nw: img.naturalWidth, position: getComputedStyle(img).position, opacity: getComputedStyle(img).opacity, visibility: getComputedStyle(img).visibility }));
  assert.ok(noJsHero.complete && noJsHero.nw > 0 && noJsHero.position === 'static' && noJsHero.opacity === '1' && noJsHero.visibility === 'visible', `no-JS hero ${JSON.stringify(noJsHero)}`);
  await noJsPage.screenshot({ path: `${outDir}/mobile-home-full-nojs.png`, fullPage: true });
  result.noJsHero = noJsHero;
  await noJsBrowser.close();

  for (const [name, viewport] of [['mobile', { width: 390, height: 844 }], ['desktop', { width: 1440, height: 1000 }]]) {
    const browser = await webkit.launch();
    const page = await browser.newPage({ viewport });
    await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1100);
    await closeReservation(page);
    await decodeImages(page);
    await page.screenshot({ path: `${outDir}/${name}-home-full.png`, fullPage: true });
    await browser.close();
  }

  const printBrowser = await webkit.launch();
  const printPage = await printBrowser.newPage({ viewport: { width: 390, height: 844 } });
  await printPage.goto(base + '/', { waitUntil: 'domcontentloaded' });
  await printPage.waitForTimeout(350);
  await closeReservation(printPage);
  await printPage.emulateMedia({ media: 'print' });
  await decodeImages(printPage);
  await printPage.screenshot({ path: `${outDir}/mobile-home-full-print.png`, fullPage: true });
  await printBrowser.close();
  return result;
}

try {
  const report = {
    mobile: await testCore('mobile', { width: 390, height: 844 }),
    desktop: await testCore('desktop', { width: 1440, height: 1000 }),
    routes: await routeImageSweep(),
    portfolio: await portfolioBehavior(),
    capture: await captureChecks(),
  };
  fs.writeFileSync(`${outDir}/report.json`, JSON.stringify(report, null, 2));
  console.log('Strict controlled UI V4 browser QA passed.');
} catch (error) {
  console.error(error);
  process.exit(1);
}
