from pathlib import Path
import re

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


def required_replace(path_str, old, new, minimum=1):
    path = Path(path_str)
    text = path.read_text()
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f'Expected at least {minimum} matches in {path_str}, found {count}: {old[:80]}')
    path.write_text(text.replace(old, new))
    return count


css = CSS.read_text()
if MARKER not in css:
    CSS.write_text(css.rstrip() + BLOCK.rstrip() + '\n')
else:
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
''')

inject_head_style('sunday-school/index.html', component_marker, r'''
#school-notes-email::placeholder,
#school-notes-email::-webkit-input-placeholder {
  font-family:'Inter Tight',sans-serif !important;
  font-size:12px !important;
  font-weight:300 !important;
  letter-spacing:.01em !important;
}
''')

inject_head_style('contact/index.html', component_marker, r'''
form[data-editorial-labels] label > span:first-child,
form[data-editorial-labels] > label[for] {
  font-size:9.5px !important;
  font-weight:400 !important;
  letter-spacing:.05em !important;
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
''')

# Make the owning markup authoritative too. This prevents component/page-level
# rules from silently overriding the guidance sizing after render.
required_replace(
    'Site Header.dc.html',
    "font-family:'Inter Tight',sans-serif;font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase\">Email Address</label>",
    "font-family:'Inter Tight',sans-serif;font-size:9.5px!important;font-weight:400;letter-spacing:.075em;text-transform:uppercase\">Email Address</label>"
)

for page in ['contact/index.html', 'join-our-team/index.html']:
    required_replace(
        page,
        "font-family:'Inter Tight',sans-serif;font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase",
        "font-family:'Inter Tight',sans-serif;font-size:9.5px!important;font-weight:400;letter-spacing:.075em;text-transform:uppercase",
        minimum=3
    )

# Project Inquiry field labels only. Leave service-option/checklist copy alone.
inquiry_path = Path('Inquiry Form.dc.html')
inquiry = inquiry_path.read_text()
inquiry, label_count = re.subn(
    r'(<label data-step-panel[^>]*>\s*<span style="[^"]*?)font-size:10\.25px',
    r'\1font-size:9.5px!important',
    inquiry
)
if label_count < 6:
    raise SystemExit(f'Expected at least 6 Project Inquiry field labels, found {label_count}')
inquiry = inquiry.replace(
    "font-family:'Inter Tight',sans-serif;font-size:11px;font-weight:400;letter-spacing:.10em;text-transform:uppercase\">Ideal Start Date</span>",
    "font-family:'Inter Tight',sans-serif;font-size:9.5px!important;font-weight:400;letter-spacing:.10em;text-transform:uppercase\">Ideal Start Date</span>"
)
inquiry, date_count = re.subn(
    r'(aria-haspopup="dialog"[^>]*style="[^"]*?font-size:)14px',
    r'\g<1>12.5px!important',
    inquiry,
    count=1
)
if date_count != 1:
    raise SystemExit(f'Expected one Project Inquiry date trigger, found {date_count}')

# Remove the component-level 10px !important rule that was still winning in
# WebKit after render. This is the exact override that caused the repeated issue.
inquiry, inquiry_rule_count = re.subn(
    r'(\[data-inq\] label > span:first-child,\s*\[data-inq\] fieldset > legend,\s*\[data-inq\] div\[data-step\] > span:first-child \{\s*font-family: \'Inter Tight\', sans-serif !important;\s*font-size:) 10px( !important;)',
    r'\g<1> 9.5px\2',
    inquiry
)
if inquiry_rule_count < 1:
    raise SystemExit('Did not find the Project Inquiry 10px component override')
inquiry_path.write_text(inquiry)

# Join's Select A Program control is placeholder-like copy inside a button.
join_path = Path('join-our-team/index.html')
join = join_path.read_text()
join, join_trigger_count = re.subn(
    r'(aria-haspopup="listbox"[^>]*style="[^"]*?font-size:)16px',
    r'\g<1>12.5px!important',
    join,
    count=1
)
if join_trigger_count != 1:
    raise SystemExit(f'Expected one Join program trigger, found {join_trigger_count}')
join_path.write_text(join)

# Page-level mobile rules also contained 10px !important guidance sizing.
# Reduce only the form-guidance selectors, not unrelated UI microtype.
page_patterns = [
    (
        re.compile(r'(form\[data-inq\] label > span,\s*form\[data-inq\] legend \{ font-size:) 10px( !important; \})'),
        r'\g<1> 9.5px\2'
    ),
    (
        re.compile(r'(form\[data-editorial-labels\] label > span:first-child,\s*form\[data-editorial-labels\] > div > span:first-child \{\s*font-family: \'Inter Tight\', sans-serif !important;\s*font-size:) 10px( !important;)'),
        r'\g<1> 9.5px\2'
    ),
    (
        re.compile(r'(form\[data-editorial-labels\] > label\[for\] \{\s*font-family: \'Inter Tight\', sans-serif !important;\s*font-size:) 10px( !important;)'),
        r'\g<1> 9.5px\2'
    ),
    (
        re.compile(r'(form\[data-editorial-labels\] label > span:first-child \{\s*font-family: \'Inter Tight\', sans-serif !important;\s*font-size:) 10px( !important;)'),
        r'\g<1> 9.5px\2'
    ),
]

page_rule_changes = 0
for path in Path('.').rglob('*.html'):
    if any(part in {'.git', '.github', 'node_modules'} for part in path.parts):
        continue
    text = path.read_text()
    updated = text
    for pattern, replacement in page_patterns:
        updated, count = pattern.subn(replacement, updated)
        page_rule_changes += count
    if updated != text:
        path.write_text(updated)
if page_rule_changes < 3:
    raise SystemExit(f'Expected multiple page-level 10px form guidance overrides, changed only {page_rule_changes}')

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
for item in [
    MARKER,
    'form input::placeholder',
    'form input::-webkit-input-placeholder',
    'font-size: 12px !important;',
    'font-size: 9.5px !important;',
    'form[data-editorial-labels] [aria-haspopup="listbox"]',
]:
    if item not in final_css:
        raise SystemExit('Missing expected shared CSS: ' + item)

for path_str in ['Site Header.dc.html', 'Site Footer.dc.html', 'Inquiry Form.dc.html', 'sunday-school/index.html', 'contact/index.html', 'join-our-team/index.html']:
    if component_marker not in Path(path_str).read_text():
        raise SystemExit('Missing component guidance styles in ' + path_str)

print(f'Applied authoritative form guidance microtype; removed {inquiry_rule_count + page_rule_changes} remaining 10px form-label overrides; bumped {len(changed)} HTML files to asset version 20260913-16.')
