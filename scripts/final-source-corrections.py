from pathlib import Path

ROOT = Path('.')
changed = []

def rewrite(path, fn):
    p = ROOT / path
    old = p.read_text(encoding='utf-8')
    new = fn(old)
    if new != old:
        p.write_text(new, encoding='utf-8')
        changed.append(str(p))
    return new

def must_replace(text, old, new, label, count=None):
    found = text.count(old)
    if found == 0:
        raise SystemExit(f'Missing replacement target: {label}')
    if count is not None and found != count:
        raise SystemExit(f'Unexpected count for {label}: {found}, expected {count}')
    return text.replace(old, new)

# ---------------------------------------------------------------------------
# Shared production CSS: fix the old rules that were winning inside DC imports.
# This is the actual source layer the rendered components see.
# ---------------------------------------------------------------------------
def fix_site_css(s):
    s = must_replace(s,
'''  font-size: 11.5px !important;\n  font-weight: 300 !important;\n  letter-spacing: .085em !important;''',
'''  font-size: 11px !important;\n  font-weight: 400 !important;\n  letter-spacing: .07em !important;''',
'functional form label scale')

    s = must_replace(s,
'''form[data-editorial-labels] [aria-haspopup="listbox"],\nform[data-editorial-labels] [role="option"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 14px !important;\n  font-weight: 300 !important;\n  letter-spacing: 0 !important;\n}''',
'''form[data-editorial-labels] [aria-haspopup="listbox"],\nform[data-editorial-labels] [role="option"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 14px !important;\n  font-weight: 400 !important;\n  letter-spacing: 0 !important;\n}''',
'custom listbox functional weight', 1)

    s = must_replace(s,
'''form[data-inq] [aria-haspopup="dialog"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 13px !important;\n  font-weight: 300 !important;\n  letter-spacing: 0 !important;\n}''',
'''form[data-inq] [aria-haspopup="dialog"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 14px !important;\n  font-weight: 400 !important;\n  letter-spacing: 0 !important;\n}''',
'date trigger functional weight', 1)

    s = must_replace(s,
'''[data-screen-label="Contact"] form[data-editorial-labels] input,\n[data-screen-label="Contact"] form[data-editorial-labels] textarea {\n  font-size: 14px !important;\n}''',
'''[data-screen-label="Contact"] form[data-editorial-labels] input,\n[data-screen-label="Contact"] form[data-editorial-labels] textarea {\n  font-size: 16px !important;\n}''',
'contact mobile-safe input size', 1)

    s = must_replace(s,
'''[aria-label="Newsletter"] [data-news-fineprint] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 9px !important;\n  font-weight: 300 !important;\n  letter-spacing: .07em !important;\n  line-height: 1.5 !important;\n}''',
'''[aria-label="Newsletter"] [data-news-fineprint] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 8px !important;\n  font-weight: 300 !important;\n  letter-spacing: .055em !important;\n  line-height: 1.45 !important;\n}''',
'newsletter fine print hierarchy', 1)

    s = must_replace(s,
'''[aria-label="Project inquiry"] [data-inquiry-kicker] {\n  font-size: 28px !important;\n}''',
'''[aria-label="Project inquiry"] [data-inquiry-kicker] {\n  font-size: 40px !important;\n  line-height: .94 !important;\n}''',
'project inquiry desktop kicker', 1)

    s = must_replace(s,
'''  [aria-label="Project inquiry"] [data-inquiry-kicker] {\n    font-size: 30px !important;\n    margin-bottom: 11px !important;\n  }''',
'''  [aria-label="Project inquiry"] [data-inquiry-kicker] {\n    font-size: 46px !important;\n    line-height: .94 !important;\n    margin-bottom: 14px !important;\n  }''',
'project inquiry mobile kicker', 1)

    # Give compact calendar controls readable functional type in the real shared sheet.
    if '/* FINAL FORM CONTROL READABILITY */' not in s:
        s += '''\n\n/* FINAL FORM CONTROL READABILITY */\nform[data-inq] [aria-label="Choose a start date"] > div:first-child > span {\n  font-family:var(--sunday-sans) !important;\n  font-size:10.5px !important;\n  font-weight:400 !important;\n  letter-spacing:.07em !important;\n}\nform[data-inq] [aria-label="Choose a start date"] > div:nth-child(2) {\n  font-family:var(--sunday-sans) !important;\n  font-size:10.5px !important;\n  font-weight:400 !important;\n  letter-spacing:.04em !important;\n}\nform[data-inq] [aria-label="Choose a start date"] > div:last-child button {\n  font-family:var(--sunday-sans) !important;\n  font-size:11.5px !important;\n  font-weight:400 !important;\n  min-height:36px !important;\n}\nform[data-inq] [role="checkbox"] { min-height:40px !important; }\nform[data-inq] [role="checkbox"] span:last-child {\n  font-family:var(--sunday-sans) !important;\n  font-size:11px !important;\n  font-weight:400 !important;\n  letter-spacing:.07em !important;\n}\n[data-form-instruction] {\n  font-family:var(--sunday-sans) !important;\n  font-size:10.5px !important;\n  font-weight:400 !important;\n  letter-spacing:.07em !important;\n}\n[data-program-action] {\n  font-family:var(--sunday-sans) !important;\n  font-size:10px !important;\n  font-weight:400 !important;\n  letter-spacing:.085em !important;\n}\nbutton[data-program-action] { min-height:44px !important; }\n@media (max-width:820px) {\n  form[data-editorial-labels] [aria-haspopup="listbox"],\n  form[data-inq] [aria-haspopup="dialog"] { font-size:16px !important; min-height:44px !important; }\n  [data-program-action] { font-size:10.5px !important; }\n}\n'''
    return s
rewrite('assets/site.css', fix_site_css)

# ---------------------------------------------------------------------------
# Project Inquiry component: source values agree with the shared type system.
# ---------------------------------------------------------------------------
def fix_inquiry(s):
    s = s.replace("font-size:10px !important;\n    font-weight:300 !important;\n    letter-spacing:.12em !important;", "font-size:11px !important;\n    font-weight:400 !important;\n    letter-spacing:.075em !important;")
    s = s.replace("font-size:11.25px;font-weight:300;letter-spacing:.10em", "font-size:11px;font-weight:400;letter-spacing:.075em")
    s = s.replace("font-size:11px;font-weight:300;letter-spacing:.10em", "font-size:11px;font-weight:400;letter-spacing:.075em")
    s = s.replace("font-size:8px;letter-spacing:.14em;text-transform:uppercase">{{ monthLabel }}", "font-size:10.5px;font-weight:400;letter-spacing:.07em;text-transform:uppercase">{{ monthLabel }}")
    s = s.replace("font-size:7px;grid-template-columns:repeat(7,minmax(0,1fr));letter-spacing:.08em", "font-size:10.5px;font-weight:400;grid-template-columns:repeat(7,minmax(0,1fr));letter-spacing:.04em")
    s = s.replace("fontSize: '11px',\n          height: '30px',", "fontSize: '11.5px',\n          fontWeight: '400',\n          height: '36px',")
    s = s.replace("font-size:13px;justify-content:space-between", "font-size:14px;font-weight:400;justify-content:space-between")
    s = s.replace("gap:9px;min-height:28px;padding:0;text-align:left", "gap:9px;min-height:40px;padding:0;text-align:left")
    return s
root_inquiry = rewrite('Inquiry Form.dc.html', fix_inquiry)

# ---------------------------------------------------------------------------
# Shared Header: make the visible popup hierarchy/form source values explicit.
# ---------------------------------------------------------------------------
def fix_header(s):
    s = s.replace("data-inquiry-kicker style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:28px;", "data-inquiry-kicker style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:{{ inqKickerSize }};")
    marker = "      inqDisplay: this.state.inquiry ? 'flex' : 'none',\n"
    if "inqKickerSize:" not in s:
        if marker not in s: raise SystemExit('Header inquiry marker missing')
        s = s.replace(marker, marker + "      inqKickerSize: t ? '46px' : '40px',\n", 1)
    s = s.replace("font-size:9px;font-weight:300;letter-spacing:.14em;text-transform:uppercase\">Email Address", "font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase\">Email Address")
    s = s.replace("font-size:14px;font-weight:300;min-height:45px", "font-size:16px;font-weight:300;min-height:45px")
    s = s.replace("font-size:8px;gap:9px;justify-content:center;letter-spacing:.16em;min-height:43px", "font-size:10px;font-weight:400;gap:9px;justify-content:center;letter-spacing:.10em;min-height:44px")
    s = s.replace("<h2 style=\"font-size:30px;font-weight:500;", "<h2 style=\"font-size:30px;font-weight:400;")
    return s
root_header = rewrite('Site Header.dc.html', fix_header)

# Footer source values align with rendered hierarchy and avoid stale overrides.
def fix_footer(s):
    s = s.replace("data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:7px;letter-spacing:.13em;line-height:1.6", "data-news-fineprint style=\"font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.055em;line-height:1.45")
    s = s.replace("font-size:15px;font-weight:300;min-height:32px", "font-size:16px;font-weight:300;min-height:42px")
    s = s.replace("font-size:8px;gap:10px;justify-content:center;letter-spacing:.16em;min-height:33px", "font-size:10px;font-weight:400;gap:10px;justify-content:center;letter-spacing:.10em;min-height:44px")
    return s
root_footer = rewrite('Site Footer.dc.html', fix_footer)

# Contact form: update actual source instead of relying on an outside override.
def fix_contact(s):
    s = s.replace("font-size:9px;font-weight:300;letter-spacing:.14em;text-transform:uppercase", "font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase")
    s = s.replace("font-family:inherit;font-size:14px;min-height:36px", "font-family:inherit;font-size:16px;min-height:44px")
    s = s.replace("font-family:inherit;font-size:14px;padding:8px 10px", "font-family:inherit;font-size:16px;padding:8px 10px")
    return s
rewrite('contact/index.html', fix_contact)

# Join form: functional labels/controls are Inter Tight and mobile-readable.
def fix_join(s):
    s = s.replace("font-size:8px;font-weight:300;letter-spacing:.16em;text-transform:uppercase", "font-size:11px;font-weight:400;letter-spacing:.075em;text-transform:uppercase")
    s = s.replace("font-family:inherit;font-size:14px;min-height:38px", "font-family:inherit;font-size:16px;min-height:44px")
    s = s.replace("font-family:'Playfair Display',Georgia,serif;font-size:14px;justify-content:space-between;min-height:38px", "font-family:'Inter Tight',sans-serif;font-size:16px;font-weight:400;justify-content:space-between;min-height:44px")
    s = s.replace("font-family:'Playfair Display',Georgia,serif;font-size:13px;padding:9px 10px", "font-family:'Inter Tight',sans-serif;font-size:14px;font-weight:400;padding:9px 10px")
    s = s.replace("font-size:9px;font-weight:500;gap:12px;grid-column:1 / -1;justify-content:center;letter-spacing:.18em;min-height:44px", "font-size:10px;font-weight:400;gap:12px;grid-column:1 / -1;justify-content:center;letter-spacing:.10em;min-height:44px")
    return s
rewrite('join-our-team/index.html', fix_join)

# Services embedded inquiry: source hooks and hierarchy match the popup.
def fix_services(s):
    s = s.replace("<p style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:24px;", "<p data-inquiry-kicker style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:46px;")
    s = s.replace("<p style=\"font-size:12px;line-height:1.5;margin:10px 0 0;max-width:470px\">Share the essentials.", "<p data-inquiry-support style=\"font-family:'Inter Tight',sans-serif;font-size:13px;font-weight:300;line-height:1.5;margin:10px 0 0;max-width:470px\">Share the essentials.")
    return s
rewrite('services/index.html', fix_services)

# Shared components are source-of-truth. Keep every generated page copy identical.
for name, source in [('Site Header.dc.html', root_header), ('Site Footer.dc.html', root_footer), ('Inquiry Form.dc.html', root_inquiry)]:
    for p in ROOT.rglob(name):
        if p == ROOT / name or any(part in {'.git','node_modules'} for part in p.parts):
            continue
        old = p.read_text(encoding='utf-8')
        if old != source:
            p.write_text(source, encoding='utf-8')
            changed.append(str(p))

print(f'Final source corrections updated {len(changed)} files')
for p in changed:
    print(p)
