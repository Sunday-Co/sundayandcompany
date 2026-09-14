from pathlib import Path

CSS = Path('assets/site.css')
MARKER = '/* FORM FIELD GUIDANCE MICROTYPE · 2026-09-13 */'
BLOCK = r'''

/* FORM FIELD GUIDANCE MICROTYPE · 2026-09-13 */
/* Keep entered text at 16px on mobile to prevent iOS focus zoom.
   Size only labels, placeholders, and placeholder-like custom controls down. */
form input::placeholder,
form textarea::placeholder {
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
  form textarea::placeholder {
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

css = CSS.read_text()
if MARKER not in css:
    CSS.write_text(css.rstrip() + BLOCK.rstrip() + '\n')

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
    'font-size: 12px !important;',
    '[aria-label="The Sunday Reservation"] label[for="reservationEmail"]',
    'font-size: 9.25px !important;',
    'form[data-editorial-labels] [aria-haspopup="listbox"]',
]
for item in checks:
    if item not in final_css:
        raise SystemExit('Missing expected CSS: ' + item)

print(f'Applied form guidance microtype; bumped {len(changed)} HTML files to asset version 20260913-16.')
