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

# 1) Fix the ACTUAL success receipt rendered by Site Header after inquiry completion.
# Use inline !important declarations because DC imports generate scoped component CSS.
header_path = Path('Site Header.dc.html')
header = header_path.read_text()
old_h2 = '<h2 style="font-size:clamp(28px,3vw,38px);font-weight:400;letter-spacing:-.045em;line-height:.94;margin:0">Your Inquiry Is In.</h2>'
new_h2 = '<h2 style="font-family:\'Inter Tight\',sans-serif!important;font-size:clamp(18px,2.2vw,24px)!important;font-weight:400!important;letter-spacing:.11em!important;line-height:1.2!important;margin:0;text-transform:uppercase!important">YOUR INQUIRY IS IN.</h2>'
old_p = '<p style="font-size:12px;line-height:1.5;margin:12px auto 0;max-width:520px">Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>'
new_p = '<p style="font-family:\'Inter Tight\',sans-serif!important;font-size:10px!important;font-weight:300!important;letter-spacing:.065em!important;line-height:1.55!important;margin:13px auto 0;max-width:520px;text-transform:uppercase!important">THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>'

if old_h2 in header:
    header = header.replace(old_h2, new_h2, 1)
elif new_h2 not in header:
    # Upgrade the previous candidate version to the authoritative inline-important version.
    previous_h2 = '<h2 style="font-family:\'Inter Tight\',sans-serif;font-size:clamp(18px,2.2vw,24px);font-weight:400;letter-spacing:.11em;line-height:1.2;margin:0;text-transform:uppercase">YOUR INQUIRY IS IN.</h2>'
    if previous_h2 in header:
        header = header.replace(previous_h2, new_h2, 1)
    else:
        raise SystemExit('Could not locate the live Site Header inquiry success heading.')

if old_p in header:
    header = header.replace(old_p, new_p, 1)
elif new_p not in header:
    previous_p = '<p style="font-family:\'Inter Tight\',sans-serif;font-size:10px;font-weight:300;letter-spacing:.065em;line-height:1.55;margin:13px auto 0;max-width:520px;text-transform:uppercase">THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>'
    if previous_p in header:
        header = header.replace(previous_p, new_p, 1)
    else:
        raise SystemExit('Could not locate the live Site Header inquiry success body.')
header_path.write_text(header)

# 2) Make the shared footer own its typography inside the component runtime.
# The DC renderer creates scoped CSS classes, so ordinary page CSS can lose even
# when it appears later in source. Inline !important values are authoritative.
footer_path = Path('Site Footer.dc.html')
footer = footer_path.read_text()
old_fine = "<p data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.055em;line-height:1.45;margin-top:7px;opacity:.78;text-transform:uppercase\">"
previous_fine = "<p data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8.25px;font-weight:300;letter-spacing:.035em;line-height:1.45;margin-top:7px;opacity:.72;text-transform:uppercase\">"
new_fine = "<p data-news-fineprint style=\"font-family:'Inter Tight',sans-serif!important;font-size:8.25px!important;font-weight:300!important;letter-spacing:.035em!important;line-height:1.45!important;margin-top:7px;opacity:.72!important;text-transform:uppercase\">"
if old_fine in footer:
    footer = footer.replace(old_fine, new_fine, 1)
elif previous_fine in footer:
    footer = footer.replace(previous_fine, new_fine, 1)
elif new_fine not in footer:
    raise SystemExit('Could not locate newsletter fine print source.')

old_email = "<a data-footer-ui href=\"mailto:hello@sundayandcompany.co\" style=\"font-family:'Inter Tight',sans-serif;font-size:13.25px;font-weight:400;letter-spacing:.02em;line-height:1.4;overflow-wrap:anywhere\""
new_email = "<a data-footer-ui href=\"mailto:hello@sundayandcompany.co\" style=\"font-family:'Inter Tight',sans-serif!important;font-size:{{ footerEmailSize }}!important;font-weight:400!important;letter-spacing:.02em!important;line-height:1.4!important;overflow-wrap:anywhere\""
if old_email in footer:
    footer = footer.replace(old_email, new_email, 1)
elif new_email not in footer:
    raise SystemExit('Could not locate the footer email source.')

# Put the mobile/desktop choice in the component's own render values instead of
# relying on external media-query selectors to cross the component boundary.
render_anchor = "      nlFormTop: n ? '11px' : '0',\n"
render_insert = "      nlFormTop: n ? '11px' : '0',\n      footerEmailSize: n ? '16.5px' : '13.25px',\n"
if 'footerEmailSize:' not in footer:
    if render_anchor not in footer:
        raise SystemExit('Could not locate Site Footer renderVals insertion point.')
    footer = footer.replace(render_anchor, render_insert, 1)

footer_path.write_text(footer)

# 3) Make the Inquiry Form's own secondary success state literal uppercase too.
inq_path = Path('Inquiry Form.dc.html')
inq = inq_path.read_text()
inq = inq.replace('>Your Inquiry Is In.</h3>', '>YOUR INQUIRY IS IN.</h3>', 1)
inq = inq.replace('>Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>', '>THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>', 1)
inq_path.write_text(inq)

# 4) Keep the global rule consistent as a fallback, even though the imported
# component now owns the final rendered value itself.
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
    raise SystemExit('Could not locate the mobile footer email fallback rule in assets/site.css.')
css_path.write_text(css)

# 5) Bump the reviewed CSS/JS asset version so Safari cannot retain the previous
# production stylesheet after the corrected deployment.
asset_changed = 0
for path in [Path('404.html'), *Path('.').glob('*/index.html'), *Path('our-work').glob('*/index.html')]:
    if not path.exists():
        continue
    text = path.read_text()
    new = text.replace('20260913-16', '20260914-17')
    if new != text:
        path.write_text(new)
        asset_changed += 1

# 6) Synchronize every page-local copy to the canonical root component so there
# is no stale duplicate available anywhere in the published repository.
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

# 7) Refuse to finish unless all copies are byte-for-byte identical and the
# actual runtime owners contain the requested values.
for directory in DIRS:
    for name, content in canonical.items():
        path = Path(directory) / name
        if path.read_text() != content:
            raise SystemExit(f'Shared component drift remains: {path}')

final_header = header_path.read_text()
final_footer = footer_path.read_text()
final_css = css_path.read_text()
if 'YOUR INQUIRY IS IN.' not in final_header or "font-size:clamp(18px,2.2vw,24px)!important" not in final_header:
    raise SystemExit('Live Header success typography did not land.')
if 'font-size:{{ footerEmailSize }}!important' not in final_footer or "footerEmailSize: n ? '16.5px' : '13.25px'" not in final_footer:
    raise SystemExit('Component-owned responsive footer email sizing did not land.')
if 'font-size:8.25px!important;font-weight:300!important' not in final_footer:
    raise SystemExit('Authoritative newsletter disclaimer typography did not land.')
if 'font-size: 16.5px !important;' not in final_css:
    raise SystemExit('Mobile footer email fallback rule did not land in assets/site.css.')

print(f'Corrected actual Header success receipt, component-owned footer typography, synchronized {len(DIRS) * 3} component copies, and bumped {asset_changed} pages to asset version 20260914-17.')
