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
header_path = Path('Site Header.dc.html')
header = header_path.read_text()
old_h2 = '<h2 style="font-size:clamp(28px,3vw,38px);font-weight:400;letter-spacing:-.045em;line-height:.94;margin:0">Your Inquiry Is In.</h2>'
new_h2 = '<h2 style="font-family:\'Inter Tight\',sans-serif;font-size:clamp(18px,2.2vw,24px);font-weight:400;letter-spacing:.11em;line-height:1.2;margin:0;text-transform:uppercase">YOUR INQUIRY IS IN.</h2>'
old_p = '<p style="font-size:12px;line-height:1.5;margin:12px auto 0;max-width:520px">Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>'
new_p = '<p style="font-family:\'Inter Tight\',sans-serif;font-size:10px;font-weight:300;letter-spacing:.065em;line-height:1.55;margin:13px auto 0;max-width:520px;text-transform:uppercase">THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>'

if old_h2 in header:
    header = header.replace(old_h2, new_h2, 1)
elif new_h2 not in header:
    raise SystemExit('Could not locate the live Site Header inquiry success heading.')

if old_p in header:
    header = header.replace(old_p, new_p, 1)
elif new_p not in header:
    raise SystemExit('Could not locate the live Site Header inquiry success body.')

header_path.write_text(header)

# 2) Make the shared footer own the mobile typography directly instead of relying
#    on page-level CSS reaching an imported component.
footer_path = Path('Site Footer.dc.html')
footer = footer_path.read_text()
old_fine = "<p data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.055em;line-height:1.45;margin-top:7px;opacity:.78;text-transform:uppercase\">"
new_fine = "<p data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8.25px;font-weight:300;letter-spacing:.035em;line-height:1.45;margin-top:7px;opacity:.72;text-transform:uppercase\">"
if old_fine in footer:
    footer = footer.replace(old_fine, new_fine, 1)
elif new_fine not in footer:
    raise SystemExit('Could not locate newsletter fine print source.')

marker = '/* AUTHORITATIVE IMPORTED FOOTER MOBILE TYPOGRAPHY · 2026-09-14 */'
if marker not in footer:
    style = """
<style>
/* AUTHORITATIVE IMPORTED FOOTER MOBILE TYPOGRAPHY · 2026-09-14 */
[aria-label=\"Newsletter\"] [data-news-fineprint] {
  font-family:'Inter Tight',sans-serif !important;
  font-size:8.25px !important;
  font-weight:300 !important;
  letter-spacing:.035em !important;
  line-height:1.45 !important;
  opacity:.72 !important;
}
@media (max-width:700px) {
  footer a[href^=\"mailto:\"] {
    font-family:'Inter Tight',sans-serif !important;
    font-size:16.5px !important;
    font-weight:400 !important;
    letter-spacing:0 !important;
    line-height:1.4 !important;
  }
}
</style>
"""
    footer = footer.replace('</head>', style + '</head>', 1)
footer_path.write_text(footer)

# 3) Make the Inquiry Form success copy literally uppercase too, in addition to
#    its existing secondary-font/text-transform styling.
inq_path = Path('Inquiry Form.dc.html')
inq = inq_path.read_text()
inq = inq.replace('>Your Inquiry Is In.</h3>', '>YOUR INQUIRY IS IN.</h3>', 1)
inq = inq.replace('>Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>', '>THANK YOU FOR SHARING THE DETAILS. WE HAVE RECEIVED YOUR INQUIRY AND WILL REVIEW IT BEFORE FOLLOWING UP.</p>', 1)
inq_path.write_text(inq)

# 4) Synchronize every page-local imported copy to the canonical root component.
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

# 5) Refuse to finish unless all copies are byte-for-byte identical.
for directory in DIRS:
    for name, content in canonical.items():
        path = Path(directory) / name
        if path.read_text() != content:
            raise SystemExit(f'Shared component drift remains: {path}')

# Guard the exact live success source and footer rules.
final_header = header_path.read_text()
final_footer = footer_path.read_text()
if 'YOUR INQUIRY IS IN.' not in final_header or "font-family:'Inter Tight',sans-serif;font-size:clamp(18px,2.2vw,24px)" not in final_header:
    raise SystemExit('Live Header success typography did not land.')
if 'font-size:16.5px !important' not in final_footer or 'font-weight:300' not in final_footer:
    raise SystemExit('Authoritative footer mobile typography did not land.')

print(f'Corrected live Header success state and synchronized {len(DIRS) * 3} page-local shared components.')
