from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


# ------------------------------------------------------------------
# Shared CSS: refine functional-vs-receipt typography without making
# every button in a form tiny. Add missing Join form label coverage.
# ------------------------------------------------------------------
css = read('assets/site.css')
css = replace_once(
    css,
    "form[data-editorial-labels] label > span:first-child,\nform[data-editorial-labels] > label[for] {",
    "form[data-editorial-labels] label > span:first-child,\nform[data-editorial-labels] > label[for],\nform[data-editorial-labels] > div > span:first-child {",
    'desktop editorial label selector',
)
css = replace_once(
    css,
    "form[data-inq] button,\nform[data-editorial-labels] button,\n[aria-label=\"Newsletter\"] button,\n[aria-label=\"The Sunday Reservation\"] form button {\n  font-family: var(--sunday-sans) !important;\n  font-size: 10px !important;\n  font-weight: 400 !important;\n  letter-spacing: .11em !important;\n}",
    "form[data-inq] [data-stepbtns] button,\nform[data-inq] > button[type=\"submit\"],\nform[data-editorial-labels] > button[type=\"submit\"],\n[aria-label=\"Newsletter\"] form button[type=\"submit\"],\n[aria-label=\"The Sunday Reservation\"] form button[type=\"submit\"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 10px !important;\n  font-weight: 400 !important;\n  letter-spacing: .11em !important;\n}\n\n/* Custom select/date controls are functional reading text, not tiny CTA labels. */\nform[data-editorial-labels] [aria-haspopup=\"listbox\"],\nform[data-editorial-labels] [role=\"option\"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 14px !important;\n  font-weight: 300 !important;\n  letter-spacing: 0 !important;\n}\n\nform[data-inq] [aria-haspopup=\"dialog\"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 13px !important;\n  font-weight: 300 !important;\n  letter-spacing: 0 !important;\n}\n\n[data-receipt-meta] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 9.5px !important;\n  font-weight: 400 !important;\n  letter-spacing: .10em !important;\n  line-height: 1.4 !important;\n  text-transform: uppercase;\n}",
    'functional button scope',
)
css = replace_once(
    css,
    "  form[data-editorial-labels] label > span:first-child,\n  form[data-editorial-labels] > label[for] {",
    "  form[data-editorial-labels] label > span:first-child,\n  form[data-editorial-labels] > label[for],\n  form[data-editorial-labels] > div > span:first-child {",
    'mobile editorial label selector',
)
css = replace_once(
    css,
    "[aria-label=\"Newsletter\"] [data-news-receipt] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 9px !important;\n  font-weight: 400 !important;\n  letter-spacing: .10em !important;\n  line-height: 1.45 !important;\n}",
    "[aria-label=\"Newsletter\"] [data-news-receipt] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 9px !important;\n  font-weight: 400 !important;\n  letter-spacing: .10em !important;\n  line-height: 1.45 !important;\n}\n\n[aria-label=\"Newsletter\"] [data-news-fineprint] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 9px !important;\n  font-weight: 300 !important;\n  letter-spacing: .07em !important;\n  line-height: 1.5 !important;\n}",
    'newsletter fine print rule',
)
css = replace_once(
    css,
    "  [aria-label=\"Newsletter\"] form button {\n    min-height: 44px !important;\n    font-size: 10px !important;\n  }",
    "  [aria-label=\"Newsletter\"] form button {\n    min-height: 44px !important;\n    font-size: 10px !important;\n  }\n\n  [aria-label=\"Newsletter\"] [data-news-fineprint] {\n    font-size: 9.5px !important;\n  }",
    'mobile newsletter fine print',
)
write('assets/site.css', css)


# ------------------------------------------------------------------
# Inquiry Form: replace anonymous dot stepper with the three approved
# named receipt tabs and active-stage highlighting.
# ------------------------------------------------------------------
inq = read('Inquiry Form.dc.html')
old_nav = '''      <div style="align-items:center;display:flex;gap:12px;justify-content:space-between">
        <span style="font-family:'Inter Tight',sans-serif;font-size:10px;letter-spacing:.11em;text-transform:uppercase">{{ stepLabel }}</span>
        <span aria-hidden="true" style="align-items:center;display:flex;flex:0 0 auto;gap:6px">
          <span style="align-items:center;border-radius:50%;display:flex;flex:0 0 18px;font-family:'Inter Tight',sans-serif;font-size:9px;height:18px;justify-content:center;background:{{ d1bg }};border:1px solid {{ d1bd }};color:{{ d1fg }}">1</span>
          <span style="height:1px;width:14px;background:{{ r1 }}"></span>
          <span style="align-items:center;border-radius:50%;display:flex;flex:0 0 18px;font-family:'Inter Tight',sans-serif;font-size:9px;height:18px;justify-content:center;background:{{ d2bg }};border:1px solid {{ d2bd }};color:{{ d2fg }}">2</span>
          <span style="height:1px;width:14px;background:{{ r2 }}"></span>
          <span style="align-items:center;border-radius:50%;display:flex;flex:0 0 18px;font-family:'Inter Tight',sans-serif;font-size:9px;height:18px;justify-content:center;background:{{ d3bg }};border:1px solid {{ d3bd }};color:{{ d3fg }}">3</span>
        </span>
      </div>'''
new_nav = '''      <div aria-label="Project inquiry steps" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;width:100%">
        <span style="background:{{ step1TabBg }};border-right:1px solid rgba(49,29,3,.22);color:{{ step1TabFg }};font-family:'Inter Tight',sans-serif;font-size:9px;font-weight:400;letter-spacing:.055em;line-height:1.2;padding:9px 6px;text-align:center;text-transform:uppercase">01&nbsp; Project Basics</span>
        <span style="background:{{ step2TabBg }};border-right:1px solid rgba(49,29,3,.22);color:{{ step2TabFg }};font-family:'Inter Tight',sans-serif;font-size:9px;font-weight:400;letter-spacing:.055em;line-height:1.2;padding:9px 6px;text-align:center;text-transform:uppercase">02&nbsp; Timing &amp; Budget</span>
        <span style="background:{{ step3TabBg }};color:{{ step3TabFg }};font-family:'Inter Tight',sans-serif;font-size:9px;font-weight:400;letter-spacing:.055em;line-height:1.2;padding:9px 6px;text-align:center;text-transform:uppercase">03&nbsp; Project Scope</span>
      </div>'''
inq = replace_once(inq, old_nav, new_nav, 'project inquiry named nav')
anchor = "    out.stepLabel = st === 1 ? '01 · Project Basics' : st === 2 ? '02 · Timing & Budget' : '03 · Project Scope';\n"
insert = anchor + "    out.step1TabBg = st === 1 ? '#ac746c' : 'transparent';\n    out.step1TabFg = st === 1 ? '#fffdf8' : '#311d03';\n    out.step2TabBg = st === 2 ? '#ac746c' : 'transparent';\n    out.step2TabFg = st === 2 ? '#fffdf8' : '#311d03';\n    out.step3TabBg = st === 3 ? '#ac746c' : 'transparent';\n    out.step3TabFg = st === 3 ? '#fffdf8' : '#311d03';\n"
inq = replace_once(inq, anchor, insert, 'project inquiry tab render values')
inq = replace_once(
    inq,
    "    <p style=\"font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.16em;margin:18px 0 0;text-transform:uppercase\">Status: Inquiry Delivered</p>",
    "    <p data-receipt-meta style=\"font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.16em;margin:18px 0 0;text-transform:uppercase\">Status: Inquiry Delivered</p>",
    'inquiry delivered metadata',
)
write('Inquiry Form.dc.html', inq)


# ------------------------------------------------------------------
# Program Cards: on narrow/mobile screens, full details live in normal
# page flow. No fixed second modal and no nested scroll box.
# ------------------------------------------------------------------
pc = read('Program Cards.dc.html')
changes = {
    "      dialogPosition: 'fixed',": "      dialogPosition: t ? 'static' : 'fixed',",
    "      dialogInset: '0',": "      dialogInset: t ? 'auto' : '0',",
    "      dialogBackdrop: 'rgba(27,15,3,.66)',": "      dialogBackdrop: t ? 'transparent' : 'rgba(27,15,3,.66)',",
    "      dialogBlur: 'blur(5px)',": "      dialogBlur: t ? 'none' : 'blur(5px)',",
    "      dialogOuterOverflow: 'auto',": "      dialogOuterOverflow: t ? 'visible' : 'auto',",
    "      dialogOuterPad: t ? '12px' : '18px',": "      dialogOuterPad: t ? '0' : '18px',",
    "      dialogAlign: 'center',": "      dialogAlign: t ? 'stretch' : 'center',",
    "      dialogZ: '80',": "      dialogZ: t ? 'auto' : '80',",
    "      dialogMargin: 'auto',": "      dialogMargin: t ? '16px 0 0' : 'auto',",
    "      dialogMaxHeight: t ? 'calc(100svh - 24px)' : 'min(86vh,760px)',": "      dialogMaxHeight: t ? 'none' : 'min(86vh,760px)',",
    "      dialogMaxWidth: t ? 'calc(100vw - 24px)' : 'min(900px, calc(100vw - 36px))',": "      dialogMaxWidth: t ? '100%' : 'min(900px, calc(100vw - 36px))',",
    "      dialogInnerOverflow: 'auto',": "      dialogInnerOverflow: t ? 'visible' : 'auto',",
    "      dialogPad: t ? '16px 16px 22px' : 'clamp(24px,4vw,48px)',": "      dialogPad: t ? '24px 18px 28px' : 'clamp(24px,4vw,48px)',",
    "      dialogAria: 'true',": "      dialogAria: t ? 'false' : 'true',",
}
for old, new in changes.items():
    pc = replace_once(pc, old, new, f'program cards {old.strip()}')
write('Program Cards.dc.html', pc)


# ------------------------------------------------------------------
# Mark decorative receipt text in each standalone form so it receives
# the receipt scale instead of the functional field scale.
# ------------------------------------------------------------------
contact = read('contact/index.html')
contact = replace_once(contact, '<div aria-hidden="true" style="border-bottom:1px dashed rgba(49,29,3,.5);display:flex;font-family:\'Inter Tight\',sans-serif;font-size:7px;justify-content:space-between;letter-spacing:.15em;margin-bottom:18px;padding-bottom:11px;text-transform:uppercase"><span>Sunday &amp; Company</span><span>Receipt No. 002</span></div>', '<div data-receipt-meta aria-hidden="true" style="border-bottom:1px dashed rgba(49,29,3,.5);display:flex;font-family:\'Inter Tight\',sans-serif;font-size:7px;justify-content:space-between;letter-spacing:.15em;margin-bottom:18px;padding-bottom:11px;text-transform:uppercase"><span>Sunday &amp; Company</span><span>Receipt No. 002</span></div>', 'contact receipt header')
contact = replace_once(contact, '<div aria-hidden="true" style="border-bottom:1px dashed rgba(49,29,3,.55);border-top:1px dashed rgba(49,29,3,.55);display:grid;font-family:\'Inter Tight\',sans-serif;font-size:7px;gap:7px 10px;grid-template-columns:auto 1fr auto;letter-spacing:.12em;margin:18px 0;padding:11px 0;text-transform:uppercase">', '<div data-receipt-meta aria-hidden="true" style="border-bottom:1px dashed rgba(49,29,3,.55);border-top:1px dashed rgba(49,29,3,.55);display:grid;font-family:\'Inter Tight\',sans-serif;font-size:7px;gap:7px 10px;grid-template-columns:auto 1fr auto;letter-spacing:.12em;margin:18px 0;padding:11px 0;text-transform:uppercase">', 'contact receipt ledger')
contact = replace_once(contact, '<p style="font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:0 0 10px;text-transform:uppercase">Sunday &amp; Company</p>', '<p data-receipt-meta style="font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:0 0 10px;text-transform:uppercase">Sunday &amp; Company</p>', 'contact confirmation metadata')
contact = replace_once(contact, '<p style="border-top:1px dashed rgba(49,29,3,.45);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:22px auto 0;padding-top:12px;text-transform:uppercase;width:min(300px,100%)">Status: Message Delivered</p>', '<p data-receipt-meta style="border-top:1px dashed rgba(49,29,3,.45);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:22px auto 0;padding-top:12px;text-transform:uppercase;width:min(300px,100%)">Status: Message Delivered</p>', 'contact confirmation status')
write('contact/index.html', contact)

join = read('join-our-team/index.html')
join = replace_once(join, '<div style="border-bottom:1px dashed rgba(49,29,3,.5);display:flex;font-family:\'Inter Tight\',sans-serif;font-size:7px;justify-content:space-between;letter-spacing:.13em;padding-bottom:11px;text-transform:uppercase"><span>Sunday &amp; Company</span><span>Program Interest</span></div>', '<div data-receipt-meta style="border-bottom:1px dashed rgba(49,29,3,.5);display:flex;font-family:\'Inter Tight\',sans-serif;font-size:7px;justify-content:space-between;letter-spacing:.13em;padding-bottom:11px;text-transform:uppercase"><span>Sunday &amp; Company</span><span>Program Interest</span></div>', 'join receipt header')
join = replace_once(join, '<p style="font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:0 0 10px;text-transform:uppercase">Sunday &amp; Company</p>', '<p data-receipt-meta style="font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:0 0 10px;text-transform:uppercase">Sunday &amp; Company</p>', 'join confirmation metadata')
join = replace_once(join, '<p style="border-top:1px dashed rgba(49,29,3,.45);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:20px auto 0;padding-top:12px;text-transform:uppercase;width:min(280px,100%)">Status: Interest Saved</p>', '<p data-receipt-meta style="border-top:1px dashed rgba(49,29,3,.45);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:20px auto 0;padding-top:12px;text-transform:uppercase;width:min(280px,100%)">Status: Interest Saved</p>', 'join confirmation status')
join = replace_once(join, '<div style="border-bottom:1px solid #311d03;border-top:1px solid #311d03;display:flex;font-family:\'Inter Tight\',sans-serif;font-size:7px;justify-content:space-between;letter-spacing:.13em;margin-top:20px;padding:10px 0;text-transform:uppercase"><span>Status</span><strong style="font-weight:600">Coming Soon</strong></div>', '<div data-receipt-meta style="border-bottom:1px solid #311d03;border-top:1px solid #311d03;display:flex;font-family:\'Inter Tight\',sans-serif;font-size:7px;justify-content:space-between;letter-spacing:.13em;margin-top:20px;padding:10px 0;text-transform:uppercase"><span>Status</span><strong style="font-weight:400">Coming Soon</strong></div>', 'join status ledger')
write('join-our-team/index.html', join)

school = read('sunday-school/index.html')
school = replace_once(school, '<p style="font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:0 0 10px;text-transform:uppercase">The Sunday Reservation</p>', '<p data-receipt-meta style="font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:0 0 10px;text-transform:uppercase">The Sunday Reservation</p>', 'school confirmation metadata')
school = replace_once(school, '<p style="border-top:1px dashed rgba(49,29,3,.45);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:20px 0 0;max-width:280px;padding-top:12px;text-transform:uppercase">Status: Your Seat Is Saved</p>', '<p data-receipt-meta style="border-top:1px dashed rgba(49,29,3,.45);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.16em;margin:20px 0 0;max-width:280px;padding-top:12px;text-transform:uppercase">Status: Your Seat Is Saved</p>', 'school confirmation status')
write('sunday-school/index.html', school)

footer = read('Site Footer.dc.html')
footer = replace_once(footer, '<p style="font-family:\'Inter Tight\',sans-serif;font-size:7px;letter-spacing:.13em;line-height:1.6;margin-top:7px;opacity:.78;text-transform:uppercase">By subscribing you agree to receive notes from Sunday &amp; Company. Unsubscribe any time. See our <a href="/privacy-policy" style="border-bottom:1px solid currentColor">Privacy Policy</a>.</p>', '<p data-news-fineprint style="font-family:\'Inter Tight\',sans-serif;font-size:7px;letter-spacing:.13em;line-height:1.6;margin-top:7px;opacity:.78;text-transform:uppercase">By subscribing you agree to receive notes from Sunday &amp; Company. Unsubscribe any time. See our <a href="/privacy-policy" style="border-bottom:1px solid currentColor">Privacy Policy</a>.</p>', 'footer newsletter fine print')
write('Site Footer.dc.html', footer)


# ------------------------------------------------------------------
# Synchronize every copied shared component with the audited root copy.
# This prevents page-specific stale copies from drifting after the fix.
# ------------------------------------------------------------------
for name in ['Inquiry Form.dc.html', 'Program Cards.dc.html', 'Site Header.dc.html', 'Site Footer.dc.html']:
    source = read(name)
    for target in ROOT.rglob(name):
        if target == ROOT / name:
            continue
        target.write_text(source, encoding='utf-8')

print('Batch 2-3 source corrections applied successfully.')
