from pathlib import Path

DIRS = [
    'about',
    'accessibility',
    'contact',
    'cookie-policy',
    'join-our-team',
    'our-work',
    'our-work/folake',
    'our-work/luckys-cafe-bakery',
    'our-work/petti-pathways',
    'our-work/pizzeria-coco',
    'privacy-policy',
    'services',
    'sunday-school',
    'terms-and-conditions',
]

header_path = Path('Site Header.dc.html')
header = header_path.read_text()
old_h2 = '<h2 style="font-size:clamp(28px,3vw,38px);font-weight:400;letter-spacing:-.045em;line-height:.94;margin:0">Your Inquiry Is In.</h2>'
previous_h2 = '<h2 style="font-family:\'Inter Tight\',sans-serif;font-size:clamp(18px,2.2vw,24px);font-weight:400;letter-spacing:.11em;line-height:1.2;margin:0;text-transform:uppercase">YOUR INQUIRY IS IN.</h2>'
new_h2 = '<h2 style="font-family:\'Inter Tight\',sans-serif!important;font-size:clamp(18px,2.2vw,24px)!important;font-weight:400!important;letter-spacing:.11em!important;line-height:1.2!important;margin:0;text-transform:uppercase!important">YOUR INQUIRY IS IN.</h2>'
old_p = '<p style="font-size:12px;line-height:1.5;margin:12px auto 0;max-width:520px">Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>'
previous_p = '<p style="font-family:\'Inter Tight\',sans-serif;font-size:10px;font-weight:300;letter-spacing:.065em;line-height:1.55;margin:13px auto 0;max-width:520px;text-transform:uppercase">THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>'
new_p = '<p style="font-family:\'Inter Tight\',sans-serif!important;font-size:10px!important;font-weight:300!important;letter-spacing:.065em!important;line-height:1.55!important;margin:13px auto 0;max-width:520px;text-transform:uppercase!important">THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>'

if old_h2 in header:
    header = header.replace(old_h2, new_h2, 1)
elif previous_h2 in header:
    header = header.replace(previous_h2, new_h2, 1)
elif new_h2 not in header:
    raise SystemExit('Could not locate live Header inquiry success heading.')
if old_p in header:
    header = header.replace(old_p, new_p, 1)
elif previous_p in header:
    header = header.replace(previous_p, new_p, 1)
elif new_p not in header:
    raise SystemExit('Could not locate live Header inquiry success body.')
header_path.write_text(header)

footer_path = Path('Site Footer.dc.html')
footer = footer_path.read_text()
old_fine = "<p data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.055em;line-height:1.45;margin-top:7px;opacity:.78;text-transform:uppercase\">"
previous_fine = "<p data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8.25px;font-weight:300;letter-spacing:.035em;line-height:1.45;margin-top:7px;opacity:.72;text-transform:uppercase\">"
if old_fine in footer:
    footer = footer.replace(old_fine, previous_fine, 1)
elif previous_fine not in footer:
    raise SystemExit('Could not locate newsletter fine print source.')
footer_path.write_text(footer)

inq_path = Path('Inquiry Form.dc.html')
inq = inq_path.read_text()
inq = inq.replace('>Your Inquiry Is In.</h3>', '>YOUR INQUIRY IS IN.</h3>', 1)
inq = inq.replace('>Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>', '>THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>', 1)
inq_path.write_text(inq)

css_path = Path('assets/site.css')
css = css_path.read_text()
old_email_rule = '''  footer a[href^="mailto:"] {
    font-size: 15.5px !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
  }'''
new_email_rule = '''  footer a[href^="mailto:"] {
    font-size: 16.5px !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
  }'''
if old_email_rule in css:
    css = css.replace(old_email_rule, new_email_rule, 1)
elif new_email_rule not in css:
    raise SystemExit('Could not locate mobile footer email fallback rule.')
css_path.write_text(css)

js_path = Path('assets/site.js')
js = js_path.read_text()
runtime_marker = '/* AUTHORITATIVE POST-DC SHARED TYPOGRAPHY · 2026-09-14 */'
runtime_block = r'''

  /* AUTHORITATIVE POST-DC SHARED TYPOGRAPHY · 2026-09-14 */
  function sundaySetImportant(el, prop, value) {
    if (!el || !el.style) return;
    if (el.style.getPropertyValue(prop) === value && el.style.getPropertyPriority(prop) === 'important') return;
    el.style.setProperty(prop, value, 'important');
  }

  function syncImportedSharedTypography() {
    var mobile = window.innerWidth <= 700;
    var footerEmails = document.querySelectorAll('footer a[href^="mailto:hello@sundayandcompany.co"]');
    for (var i = 0; i < footerEmails.length; i++) {
      sundaySetImportant(footerEmails[i], 'font-family', "'Inter Tight', Arial, sans-serif");
      sundaySetImportant(footerEmails[i], 'font-size', mobile ? '16.5px' : '13.25px');
      sundaySetImportant(footerEmails[i], 'font-weight', '400');
      sundaySetImportant(footerEmails[i], 'letter-spacing', mobile ? '0px' : '.005em');
      sundaySetImportant(footerEmails[i], 'line-height', '1.4');
    }

    var fine = document.querySelectorAll('[aria-label="Newsletter"] [data-news-fineprint]');
    for (var j = 0; j < fine.length; j++) {
      sundaySetImportant(fine[j], 'font-family', "'Inter Tight', Arial, sans-serif");
      sundaySetImportant(fine[j], 'font-size', '8.25px');
      sundaySetImportant(fine[j], 'font-weight', '300');
      sundaySetImportant(fine[j], 'letter-spacing', '.035em');
      sundaySetImportant(fine[j], 'line-height', '1.45');
      sundaySetImportant(fine[j], 'opacity', '.72');
    }

    var successes = document.querySelectorAll('[aria-label="Project inquiry"] div[role="status"][aria-live="polite"]');
    for (var k = 0; k < successes.length; k++) {
      var heading = successes[k].querySelector('h2');
      var body = successes[k].querySelector('p:last-of-type');
      if (heading && /inquiry is in/i.test(heading.textContent || '')) {
        heading.textContent = 'YOUR INQUIRY IS IN.';
        sundaySetImportant(heading, 'font-family', "'Inter Tight', Arial, sans-serif");
        sundaySetImportant(heading, 'font-size', mobile ? '18px' : '24px');
        sundaySetImportant(heading, 'font-weight', '400');
        sundaySetImportant(heading, 'letter-spacing', '.11em');
        sundaySetImportant(heading, 'line-height', '1.2');
        sundaySetImportant(heading, 'text-transform', 'uppercase');
      }
      if (body && /thank you for sharing the details/i.test(body.textContent || '')) {
        body.textContent = 'THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.';
        sundaySetImportant(body, 'font-family', "'Inter Tight', Arial, sans-serif");
        sundaySetImportant(body, 'font-size', '10px');
        sundaySetImportant(body, 'font-weight', '300');
        sundaySetImportant(body, 'letter-spacing', '.065em');
        sundaySetImportant(body, 'line-height', '1.55');
        sundaySetImportant(body, 'text-transform', 'uppercase');
      }
    }
  }
'''
if runtime_marker not in js:
    anchor = '\n  function sync() {\n'
    if anchor not in js:
        raise SystemExit('Could not locate site.js sync() insertion point.')
    js = js.replace(anchor, runtime_block + anchor, 1)

old_sync = '''  function sync() {
    ensureCorrectionStyles();
    ensureOpenSignMotion();
    syncAccessibleSurface();
  }'''
new_sync = '''  function sync() {
    ensureCorrectionStyles();
    ensureOpenSignMotion();
    syncImportedSharedTypography();
    syncAccessibleSurface();
  }'''
if old_sync in js:
    js = js.replace(old_sync, new_sync, 1)
elif new_sync not in js:
    raise SystemExit('Could not wire post-DC typography into site.js sync().')

resize_anchor = "    window.addEventListener('pageshow', sync);\n"
resize_insert = "    window.addEventListener('pageshow', sync);\n    window.addEventListener('resize', sync, { passive: true });\n"
if "window.addEventListener('resize', sync" not in js:
    if resize_anchor not in js:
        raise SystemExit('Could not locate site.js pageshow listener.')
    js = js.replace(resize_anchor, resize_insert, 1)
js_path.write_text(js)

public_pages = [Path('index.html'), Path('404.html')]
public_pages += list(Path('.').glob('*/index.html'))
public_pages += list(Path('our-work').glob('*/index.html'))
seen = set()
asset_changed = 0
for path in public_pages:
    if not path.exists() or str(path) in seen:
        continue
    seen.add(str(path))
    text = path.read_text()
    new = text.replace('20260913-16', '20260914-17')
    if new != text:
        path.write_text(new)
        asset_changed += 1

canonical = {
    'Inquiry Form.dc.html': Path('Inquiry Form.dc.html').read_text(),
    'Site Footer.dc.html': Path('Site Footer.dc.html').read_text(),
    'Site Header.dc.html': Path('Site Header.dc.html').read_text(),
}
for directory in DIRS:
    for name, content in canonical.items():
        path = Path(directory) / name
        if not path.exists():
            raise SystemExit(f'Missing expected page-local component: {path}')
        path.write_text(content)

for directory in DIRS:
    for name, content in canonical.items():
        path = Path(directory) / name
        if path.read_text() != content:
            raise SystemExit(f'Shared component drift remains: {path}')

final_js = js_path.read_text()
if runtime_marker not in final_js or "mobile ? '16.5px' : '13.25px'" not in final_js:
    raise SystemExit('Post-DC footer email runtime enforcement did not land.')
if "sundaySetImportant(fine[j], 'font-weight', '300')" not in final_js:
    raise SystemExit('Post-DC disclaimer enforcement did not land.')
if "heading.textContent = 'YOUR INQUIRY IS IN.'" not in final_js:
    raise SystemExit('Post-DC inquiry success enforcement did not land.')

print(f'Added post-DC runtime typography enforcement, synchronized {len(DIRS) * 3} shared copies, and bumped {asset_changed} public pages to asset version 20260914-17.')
