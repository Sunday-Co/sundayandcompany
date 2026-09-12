from pathlib import Path

ROOT = Path('.')
changed = []

def write_if_changed(path, new):
    p = ROOT / path
    old = p.read_text(encoding='utf-8')
    if new != old:
        p.write_text(new, encoding='utf-8')
        changed.append(str(p))

def replace_required(s, old, new, label):
    if old not in s:
        raise SystemExit(f'Missing target: {label}')
    return s.replace(old, new)

# Shared stylesheet. These old declarations were the rules actually winning
# inside imported DC components, so correct them at their source.
p = ROOT / 'assets/site.css'
s = p.read_text(encoding='utf-8')
s = replace_required(s,
"  font-size: 11.5px !important;\n  font-weight: 300 !important;\n  letter-spacing: .085em !important;",
"  font-size: 11px !important;\n  font-weight: 400 !important;\n  letter-spacing: .07em !important;",
'form label system')
s = replace_required(s,
'''form[data-editorial-labels] [aria-haspopup="listbox"],
form[data-editorial-labels] [role="option"] {
  font-family: var(--sunday-sans) !important;
  font-size: 14px !important;
  font-weight: 300 !important;
  letter-spacing: 0 !important;
}''',
'''form[data-editorial-labels] [aria-haspopup="listbox"],
form[data-editorial-labels] [role="option"] {
  font-family: var(--sunday-sans) !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  letter-spacing: 0 !important;
}''', 'listbox weight')
s = replace_required(s,
'''form[data-inq] [aria-haspopup="dialog"] {
  font-family: var(--sunday-sans) !important;
  font-size: 13px !important;
  font-weight: 300 !important;
  letter-spacing: 0 !important;
}''',
'''form[data-inq] [aria-haspopup="dialog"] {
  font-family: var(--sunday-sans) !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  letter-spacing: 0 !important;
}''', 'date trigger weight')
s = replace_required(s,
'''[data-screen-label="Contact"] form[data-editorial-labels] input,
[data-screen-label="Contact"] form[data-editorial-labels] textarea {
  font-size: 14px !important;
}''',
'''[data-screen-label="Contact"] form[data-editorial-labels] input,
[data-screen-label="Contact"] form[data-editorial-labels] textarea {
  font-size: 16px !important;
}''', 'contact input size')
s = replace_required(s,
'''[aria-label="Newsletter"] [data-news-fineprint] {
  font-family: var(--sunday-sans) !important;
  font-size: 9px !important;
  font-weight: 300 !important;
  letter-spacing: .07em !important;
  line-height: 1.5 !important;
}''',
'''[aria-label="Newsletter"] [data-news-fineprint] {
  font-family: var(--sunday-sans) !important;
  font-size: 8px !important;
  font-weight: 300 !important;
  letter-spacing: .055em !important;
  line-height: 1.45 !important;
}''', 'newsletter fine print')
s = replace_required(s,
'''[aria-label="Project inquiry"] [data-inquiry-kicker] {
  font-size: 28px !important;
}''',
'''[aria-label="Project inquiry"] [data-inquiry-kicker] {
  font-size: 40px !important;
  line-height: .94 !important;
}''', 'desktop inquiry kicker')
s = replace_required(s,
'''  [aria-label="Project inquiry"] [data-inquiry-kicker] {
    font-size: 30px !important;
    margin-bottom: 11px !important;
  }''',
'''  [aria-label="Project inquiry"] [data-inquiry-kicker] {
    font-size: 46px !important;
    line-height: .94 !important;
    margin-bottom: 14px !important;
  }''', 'mobile inquiry kicker')
if '/* FINAL FORM CONTROL READABILITY */' not in s:
    s += '''

/* FINAL FORM CONTROL READABILITY */
form[data-inq] [aria-label="Choose a start date"] > div:first-child > span {
  font-family:var(--sunday-sans) !important;
  font-size:10.5px !important;
  font-weight:400 !important;
  letter-spacing:.07em !important;
}
form[data-inq] [aria-label="Choose a start date"] > div:nth-child(2) {
  font-family:var(--sunday-sans) !important;
  font-size:10.5px !important;
  font-weight:400 !important;
  letter-spacing:.04em !important;
}
form[data-inq] [aria-label="Choose a start date"] > div:last-child button {
  font-family:var(--sunday-sans) !important;
  font-size:11.5px !important;
  font-weight:400 !important;
  min-height:36px !important;
}
form[data-inq] [role="checkbox"] { min-height:40px !important; }
form[data-inq] [role="checkbox"] span:last-child {
  font-family:var(--sunday-sans) !important;
  font-size:11px !important;
  font-weight:400 !important;
  letter-spacing:.07em !important;
}
[data-form-instruction] {
  font-family:var(--sunday-sans) !important;
  font-size:10.5px !important;
  font-weight:400 !important;
  letter-spacing:.07em !important;
}
[data-program-action] {
  font-family:var(--sunday-sans) !important;
  font-size:10px !important;
  font-weight:400 !important;
  letter-spacing:.085em !important;
}
button[data-program-action] { min-height:44px !important; }
@media (max-width:820px) {
  form[data-editorial-labels] [aria-haspopup="listbox"],
  form[data-inq] [aria-haspopup="dialog"] { font-size:16px !important; min-height:44px !important; }
  [data-program-action] { font-size:10.5px !important; }
}
'''
write_if_changed('assets/site.css', s)

# Inquiry component itself.
p = ROOT / 'Inquiry Form.dc.html'
iq = p.read_text(encoding='utf-8')
iq = iq.replace('font-size:10px !important;\n    font-weight:300 !important;\n    letter-spacing:.12em !important;', 'font-size:11px !important;\n    font-weight:400 !important;\n    letter-spacing:.075em !important;')
iq = iq.replace('font-size:11.25px;font-weight:300;letter-spacing:.10em', 'font-size:11px;font-weight:400;letter-spacing:.075em')
iq = iq.replace('font-size:11px;font-weight:300;letter-spacing:.10em', 'font-size:11px;font-weight:400;letter-spacing:.075em')
iq = iq.replace('font-size:8px;letter-spacing:.14em;text-transform:uppercase">{{ monthLabel }}', 'font-size:10.5px;font-weight:400;letter-spacing:.07em;text-transform:uppercase">{{ monthLabel }}')
iq = iq.replace('font-size:7px;grid-template-columns:repeat(7,minmax(0,1fr));letter-spacing:.08em', 'font-size:10.5px;font-weight:400;grid-template-columns:repeat(7,minmax(0,1fr));letter-spacing:.04em')
iq = iq.replace("fontSize: '11px',\n          height: '30px',", "fontSize: '11.5px',\n          fontWeight: '400',\n          height: '36px',")
iq = iq.replace('font-size:13px;justify-content:space-between', 'font-size:14px;font-weight:400;justify-content:space-between')
iq = iq.replace('gap:9px;min-height:28px;padding:0;text-align:left', 'gap:9px;min-height:40px;padding:0;text-align:left')
write_if_changed('Inquiry Form.dc.html', iq)

# Header source values, including popup and Reservation form.
p = ROOT / 'Site Header.dc.html'
h = p.read_text(encoding='utf-8')
h = h.replace("data-inquiry-kicker style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:28px;", "data-inquiry-kicker style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:{{ inqKickerSize }};")
if 'inqKickerSize:' not in h:
    marker = "      inqDisplay: this.state.inquiry ? 'flex' : 'none',\n"
    if marker not in h: raise SystemExit('Header inquiry render marker missing')
    h = h.replace(marker, marker + "      inqKickerSize: t ? '46px' : '40px',\n", 1)
h = h.replace('font-size:9px;font-weight:300;letter-spacing:.14em;text-transform:uppercase">Email Address', 'font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase">Email Address')
h = h.replace('font-size:14px;font-weight:300;min-height:45px', 'font-size:16px;font-weight:300;min-height:45px')
h = h.replace('font-size:8px;gap:9px;justify-content:center;letter-spacing:.16em;min-height:43px', 'font-size:10px;font-weight:400;gap:9px;justify-content:center;letter-spacing:.10em;min-height:44px')
h = h.replace('<h2 style="font-size:30px;font-weight:500;', '<h2 style="font-size:30px;font-weight:400;')
write_if_changed('Site Header.dc.html', h)

# Footer newsletter source.
p = ROOT / 'Site Footer.dc.html'
f = p.read_text(encoding='utf-8')
f = f.replace("data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:7px;letter-spacing:.13em;line-height:1.6", "data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.055em;line-height:1.45")
f = f.replace('font-size:15px;font-weight:300;min-height:32px', 'font-size:16px;font-weight:300;min-height:42px')
f = f.replace('font-size:8px;gap:10px;justify-content:center;letter-spacing:.16em;min-height:33px', 'font-size:10px;font-weight:400;gap:10px;justify-content:center;letter-spacing:.10em;min-height:44px')
write_if_changed('Site Footer.dc.html', f)

# Contact form actual source.
p = ROOT / 'contact/index.html'
c = p.read_text(encoding='utf-8')
c = c.replace('font-size:9px;font-weight:300;letter-spacing:.14em;text-transform:uppercase', 'font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase')
c = c.replace('font-family:inherit;font-size:14px;min-height:36px', 'font-family:inherit;font-size:16px;min-height:44px')
c = c.replace('font-family:inherit;font-size:14px;padding:8px 10px', 'font-family:inherit;font-size:16px;padding:8px 10px')
write_if_changed('contact/index.html', c)

# Join form actual source.
p = ROOT / 'join-our-team/index.html'
j = p.read_text(encoding='utf-8')
j = j.replace('font-size:8px;font-weight:300;letter-spacing:.16em;text-transform:uppercase', 'font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase')
j = j.replace('font-family:inherit;font-size:14px;min-height:38px', 'font-family:inherit;font-size:16px;min-height:44px')
j = j.replace("font-family:'Playfair Display',Georgia,serif;font-size:14px;justify-content:space-between;min-height:38px", "font-family:'Inter Tight',sans-serif;font-size:16px;font-weight:400;justify-content:space-between;min-height:44px")
j = j.replace("font-family:'Playfair Display',Georgia,serif;font-size:13px;padding:9px 10px", "font-family:'Inter Tight',sans-serif;font-size:14px;font-weight:400;padding:9px 10px")
j = j.replace('font-size:9px;font-weight:500;gap:12px;grid-column:1 / -1;justify-content:center;letter-spacing:.18em;min-height:44px', 'font-size:10px;font-weight:400;gap:12px;grid-column:1 / -1;justify-content:center;letter-spacing:.10em;min-height:44px')
write_if_changed('join-our-team/index.html', j)

# Services embedded inquiry source hooks.
p = ROOT / 'services/index.html'
sv = p.read_text(encoding='utf-8')
sv = sv.replace("<p style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:24px;", "<p data-inquiry-kicker style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:46px;")
sv = sv.replace('<p style="font-size:12px;line-height:1.5;margin:10px 0 0;max-width:470px">Share the essentials.', '<p data-inquiry-support style="font-family:\'Inter Tight\',sans-serif;font-size:13px;font-weight:300;line-height:1.5;margin:10px 0 0;max-width:470px">Share the essentials.')
write_if_changed('services/index.html', sv)

# Generated copies follow the root shared components exactly.
for name, source in [('Site Header.dc.html', h), ('Site Footer.dc.html', f), ('Inquiry Form.dc.html', iq)]:
    for q in ROOT.rglob(name):
        if q == ROOT / name or any(part in {'.git','node_modules'} for part in q.parts):
            continue
        old = q.read_text(encoding='utf-8')
        if old != source:
            q.write_text(source, encoding='utf-8')
            changed.append(str(q))

print(f'Final source corrections updated {len(changed)} files')
for path in changed:
    print(path)
