from pathlib import Path

CSS = Path('assets/site.css')
MARKER = '/* FORM FIELD GUIDANCE MICROTYPE · 2026-09-13 */'
BLOCK = r'''

/* FORM FIELD GUIDANCE MICROTYPE · 2026-09-13 */
/* Keep entered text at 16px on mobile to prevent iOS focus zoom.
   Size only labels, placeholders, and placeholder-like custom controls down. */
form input::placeholder,
form textarea::placeholder,
form input::-webkit-input-placeholder,
form textarea::-webkit-input-placeholder {
  font-family: var(--sunday-sans) !important;
  font-size: 12px !important;
  font-weight: 300 !important;
  letter-spacing: .01em !important;
  line-height: 1.3 !important;
}

form[data-inq] label > span:first-child,
form[data-inq] fieldset > legend,
form[data-editorial-labels] label > span:first-child,
form[data-editorial-labels] > label[for],
form[data-editorial-labels] > div > span:first-child,
[aria-label="The Sunday Reservation"] label[for="reservationEmail"] {
  font-size: 9.5px !important;
  font-weight: 400 !important;
  letter-spacing: .05em !important;
  line-height: 1.3 !important;
}

form[data-editorial-labels] [aria-haspopup="listbox"],
form[data-inq] [aria-haspopup="dialog"] {
  font-size: 12.5px !important;
  font-weight: 400 !important;
}

@media (max-width: 700px) {
  form input::placeholder,
  form textarea::placeholder,
  form input::-webkit-input-placeholder,
  form textarea::-webkit-input-placeholder {
    font-size: 12px !important;
  }

  form[data-inq] label > span:first-child,
  form[data-inq] fieldset > legend,
  form[data-editorial-labels] label > span:first-child,
  form[data-editorial-labels] > label[for],
  form[data-editorial-labels] > div > span:first-child,
  [aria-label="The Sunday Reservation"] label[for="reservationEmail"] {
    font-size: 9.25px !important;
  }
}
'''


def inject_head_style(path_str, marker, rules):
    path = Path(path_str)
    text = path.read_text()
    if marker in text:
        return False
    if '</head>' not in text:
        raise SystemExit(f'Missing </head> in {path_str}')
    style = f'<style>\n{marker}\n{rules.strip()}\n</style>\n'
    path.write_text(text.replace('</head>', style + '</head>', 1))
    return True


css = CSS.read_text()
if MARKER not in css:
    CSS.write_text(css.rstrip() + BLOCK.rstrip() + '\n')
else:
    # Upgrade a previously staged version to include the WebKit placeholder selector.
    if 'form input::-webkit-input-placeholder' not in css:
        css = css.replace(
            'form input::placeholder,\nform textarea::placeholder {',
            'form input::placeholder,\nform textarea::placeholder,\nform input::-webkit-input-placeholder,\nform textarea::-webkit-input-placeholder {'
        ).replace(
            '  form input::placeholder,\n  form textarea::placeholder {',
            '  form input::placeholder,\n  form textarea::placeholder,\n  form input::-webkit-input-placeholder,\n  form textarea::-webkit-input-placeholder {'
        )
        CSS.write_text(css)

component_marker = '/* COMPONENT FORM GUIDANCE MICROTYPE · 2026-09-13 */'

inject_head_style('Site Header.dc.html', component_marker, r'''
[aria-label="The Sunday Reservation"] input::placeholder,
[aria-label="The Sunday Reservation"] input::-webkit-input-placeholder {
  font-family:'Inter Tight',sans-serif !important;
  font-size:12px !important;
  font-weight:300 !important;
  letter-spacing:.01em !important;
}
[aria-label="The Sunday Reservation"] label[for="reservationEmail"] {
  font-family:'Inter Tight',sans-serif !important;
  font-size:9.5px !important;
  font-weight:400 !important;
  letter-spacing:.05em !important;
}
@media (max-width:700px) {
  [aria-label="The Sunday Reservation"] label[for="reservationEmail"] { font-size:9.25px !important; }
}
''')

inject_head_style('Site Footer.dc.html', component_marker, r'''
[aria-label="Newsletter"] input::placeholder,
[aria-label="Newsletter"] input::-webkit-input-placeholder {
  font-family:'Inter Tight',sans-serif !important;
  font-size:12px !important;
  font-weight:300 !important;
  letter-spacing:.01em !important;
}
''')

inject_head_style('Inquiry Form.dc.html', component_marker, r'''
form[data-inq] input::placeholder,
form[data-inq] textarea::placeholder,
form[data-inq] input::-webkit-input-placeholder,
form[data-inq] textarea::-webkit-input-placeholder {
  font-family:'Inter Tight',sans-serif !important;
  font-size:12px !important;
  font-weight:300 !important;
  letter-spacing:.01em !important;
}
form[data-inq] label > span:first-child,
form[data-inq] fieldset > legend {
  font-size:9.5px !important;
  font-weight:400 !important;
  letter-spacing:.05em !important;
}
form[data-inq] [aria-haspopup="dialog"] { font-size:12.5px !important; }
@media (max-width:700px) {
  form[data-inq] label > span:first-child,
  form[data-inq] fieldset > legend { font-size:9.25px !important; }
}
''')

inject_head_style('sunday-school/index.html', component_marker, r'''
#school-notes-email::placeholder,
#school-notes-email::-webkit-input-placeholder {
  font-family:'Inter Tight',sans-serif !important;
  font-size:12px !important;
  font-weight:300 !important;
  letter-spacing:.01em !important;
}
label[for="school-notes-email"] { font-size:9.5px !important; }
@media (max-width:700px) { label[for="school-notes-email"] { font-size:9.25px !important; } }
''')

inject_head_style('contact/index.html', component_marker, r'''
form[data-editorial-labels] label > span:first-child,
form[data-editorial-labels] > label[for] {
  font-size:9.5px !important;
  font-weight:400 !important;
  letter-spacing:.05em !important;
}
@media (max-width:700px) {
  form[data-editorial-labels] label > span:first-child,
  form[data-editorial-labels] > label[for] { font-size:9.25px !important; }
}
''')

inject_head_style('join-our-team/index.html', component_marker, r'''
form[data-editorial-labels] label > span:first-child,
form[data-editorial-labels] > div > span:first-child {
  font-size:9.5px !important;
  font-weight:400 !important;
  letter-spacing:.05em !important;
}
form[data-editorial-labels] [aria-haspopup="listbox"] { font-size:12.5px !important; }
@media (max-width:700px) {
  form[data-editorial-labels] label > span:first-child,
  form[data-editorial-labels] > div > span:first-child { font-size:9.25px !important; }
}
''')

changed = []
for path in Path('.').rglob('*.html'):
    if any(part in {'.git', '.github', 'node_modules'} for part in path.parts):
        continue
    text = path.read_text()
    new = text.replace('20260913-15', '20260913-16')
    if new != text:
        path.write_text(new)
        changed.append(str(path))

remaining = []
for path in Path('.').rglob('*.html'):
    if any(part in {'.git', '.github', 'node_modules'} for part in path.parts):
        continue
    if '20260913-15' in path.read_text():
        remaining.append(str(path))
if remaining:
    raise SystemExit('Old v15 asset refs remain: ' + ', '.join(remaining))

final_css = CSS.read_text()
checks = [
    MARKER,
    'form input::placeholder',
    'form input::-webkit-input-placeholder',
    'font-size: 12px !important;',
    '[aria-label="The Sunday Reservation"] label[for="reservationEmail"]',
    'font-size: 9.25px !important;',
    'form[data-editorial-labels] [aria-haspopup="listbox"]',
]
for item in checks:
    if item not in final_css:
        raise SystemExit('Missing expected shared CSS: ' + item)

for path_str in ['Site Header.dc.html', 'Site Footer.dc.html', 'Inquiry Form.dc.html', 'sunday-school/index.html', 'contact/index.html', 'join-our-team/index.html']:
    if component_marker not in Path(path_str).read_text():
        raise SystemExit('Missing component guidance styles in ' + path_str)

print(f'Applied component-owned form guidance microtype; bumped {len(changed)} HTML files to asset version 20260913-16.')
