from pathlib import Path

ROOT = Path('.')
VERSION = '20260912-4'
changed = []


def write_if_changed(path: Path, new: str):
    old = path.read_text(encoding='utf-8')
    if new != old:
        path.write_text(new, encoding='utf-8')
        changed.append(str(path))


# 1) Bust the stable CSS/JS URLs again so returning Safari sessions must load
# this exact correction pass instead of an older cached copy.
for path in ROOT.rglob('*.html'):
    if any(part in {'.git', 'node_modules'} for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8')
    new = text
    for old_version in ('20260912-1', '20260912-2', '20260912-3'):
        new = new.replace(f'/assets/site.css?v={old_version}', f'/assets/site.css?v={VERSION}')
        new = new.replace(f'/assets/site.js?v={old_version}', f'/assets/site.js?v={VERSION}')
    new = new.replace('/assets/site.css"', f'/assets/site.css?v={VERSION}"')
    new = new.replace('/assets/site.js"', f'/assets/site.js?v={VERSION}"')
    write_if_changed(path, new)

# 2) Keep the hero in the real entrance motion now that screenshot safety is
# handled by document sizing and closed-drawer rendering rather than hiding
# unrevealed sections.
site_js = ROOT / 'assets' / 'site.js'
js = site_js.read_text(encoding='utf-8')
js = js.replace("return node.id !== 'top' && !node.closest('[role=\"dialog\"]') && node.offsetHeight > 80;",
                "return !node.closest('[role=\"dialog\"]') && node.offsetHeight > 80;")
js = js.replace('/assets/rendered-corrections.css?v=20260912-1',
                f'/assets/rendered-corrections.css?v={VERSION}')
write_if_changed(site_js, js)

# 3) Inquiry component: all functional labels/controls use the secondary font
# at intentional readable sizes. The date picker is functional UI, not tiny
# decorative receipt text.
inquiry = ROOT / 'Inquiry Form.dc.html'
inq = inquiry.read_text(encoding='utf-8')
inq = inq.replace("[data-inq] input,\n  [data-inq] textarea,\n  [data-inq] select,\n  [data-inq] button {\n    font-family: 'Inter Tight', sans-serif !important;\n    font-weight: 300;\n  }",
"[data-inq] input,\n  [data-inq] textarea,\n  [data-inq] select {\n    font-family: 'Inter Tight', sans-serif !important;\n    font-weight: 300;\n  }\n  [data-inq] button {\n    font-family: 'Inter Tight', sans-serif !important;\n    font-weight: 400;\n  }")
inq = inq.replace("font-size: 10px !important;\n    font-weight: 300 !important;",
                  "font-size: 10px !important;\n    font-weight: 400 !important;")
inq = inq.replace("font-size:11.25px;font-weight:300", "font-size:11.25px;font-weight:400")
inq = inq.replace("font-size:11px;font-weight:300", "font-size:11px;font-weight:400")
inq = inq.replace("font-size:9px;font-weight:400;letter-spacing:.055em", "font-size:9.5px;font-weight:400;letter-spacing:.045em")
inq = inq.replace("font-family:inherit;font-size:13px;justify-content:space-between", "font-family:'Inter Tight',sans-serif;font-size:14px;font-weight:400;justify-content:space-between")
inq = inq.replace("width:min(260px,100%)", "width:min(320px,100%)")
inq = inq.replace("height:26px;width:26px", "height:36px;width:36px")
inq = inq.replace("font-size:8px;letter-spacing:.14em", "font-size:10.5px;font-weight:400;letter-spacing:.08em")
inq = inq.replace("font-size:7px;grid-template-columns:repeat(7,minmax(0,1fr));letter-spacing:.08em", "font-size:9.5px;font-weight:400;grid-template-columns:repeat(7,minmax(0,1fr));letter-spacing:.045em")
inq = inq.replace("style: { height: '30px' }", "style: { height: '38px' }")
inq = inq.replace("fontSize: '11px',\n          height: '30px',", "fontSize: '11.5px',\n          fontWeight: 400,\n          height: '38px',")
inq = inq.replace("min-height:28px", "min-height:40px")
inq = inq.replace("out.dateTriggerH = narrow ? '36px' : '52px';", "out.dateTriggerH = narrow ? '44px' : '52px';")
write_if_changed(inquiry, inq)

# Keep every route copy of the shared Inquiry component byte-for-byte in sync.
for p in ROOT.rglob('Inquiry Form.dc.html'):
    if p == inquiry:
        continue
    write_if_changed(p, inq)

# 4) Program cards: on mobile there is no 3D flip at all. Tapping the card
# opens the full detail block in normal page flow. This removes the WebKit
# mirrored-back-face bug and the nested scrolling-modal behavior together.
program = ROOT / 'Program Cards.dc.html'
prog = program.read_text(encoding='utf-8')
mobile_style = """
<style>
  /* MOBILE INLINE PROGRAM DETAILS: no WebKit 3D card flip on phones. */
  @media (max-width: 720px) {
    [data-program-cards] > article { perspective:none !important; }
    [data-program-cards] > article > div {
      transform:none !important;
      transform-style:flat !important;
      -webkit-transform-style:flat !important;
    }
    [data-program-cards] > article > div > button:first-child {
      backface-visibility:visible !important;
      -webkit-backface-visibility:visible !important;
      transform:none !important;
      z-index:1 !important;
    }
    [data-program-cards] > article > div > div:nth-child(2) {
      display:none !important;
      transform:none !important;
    }
  }
</style>
"""
if 'MOBILE INLINE PROGRAM DETAILS' not in prog:
    prog = prog.replace('<script src="/support.js"></script>', '<script src="/support.js"></script>' + mobile_style)
prog = prog.replace('aria-label="Flip The Fellows Table card"', 'aria-label="{{ frontLabel0 }}"')
prog = prog.replace('aria-label="Flip The Espresso Club card"', 'aria-label="{{ frontLabel1 }}"')
prog = prog.replace('aria-label="Flip The Founders Club card"', 'aria-label="{{ frontLabel2 }}"')
prog = prog.replace('>Flip <svg', '>{{ frontAction }} <svg')
prog = prog.replace("const out = {\n      cols:",
"const out = {\n      frontAction: t ? 'View Full Details' : 'Flip',\n      frontLabel0: t ? 'View full details for The Fellows Table' : 'Flip The Fellows Table card',\n      frontLabel1: t ? 'View full details for The Espresso Club' : 'Flip The Espresso Club card',\n      frontLabel2: t ? 'View full details for The Founders Club' : 'Flip The Founders Club card',\n      cols:")
prog = prog.replace("detailButtonDisplay: 'block',", "detailButtonDisplay: t ? 'none' : 'block',")
prog = prog.replace("out['flip' + i] = this.state.flipped === i ? 'rotateY(180deg)' : 'rotateY(0deg)';\n      out['doFlip' + i] = () => this.setState({ flipped: i });",
"out['flip' + i] = t ? 'rotateY(0deg)' : (this.state.flipped === i ? 'rotateY(180deg)' : 'rotateY(0deg)');\n      out['doFlip' + i] = () => t ? this.setState({ dialog: i, flipped: null }) : this.setState({ flipped: i });")
write_if_changed(program, prog)
for p in ROOT.rglob('Program Cards.dc.html'):
    if p == program:
        continue
    write_if_changed(p, prog)

# 5) Contact form instruction is necessary form guidance, not decorative
# microtype. Give it a stable hook so the shared stylesheet can size it.
contact = ROOT / 'contact' / 'index.html'
ct = contact.read_text(encoding='utf-8')
if 'data-form-instruction' not in ct:
    ct = ct.replace('>Fields marked with an asterisk are required.</p>', ' data-form-instruction>Fields marked with an asterisk are required.</p>')
write_if_changed(contact, ct)

# 6) Services embedded inquiry uses the same hierarchy as the popup receipt.
services = ROOT / 'services' / 'index.html'
sv = services.read_text(encoding='utf-8')
sv = sv.replace("<p style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:24px;", "<p data-inquiry-kicker style=\"color:#ac746c;font-family:'Pinyon Script',cursive;font-size:24px;")
sv = sv.replace("<p style=\"font-size:12px;line-height:1.5;margin:10px 0 0;max-width:470px\">Share the essentials. We’ll take it from there.</p>", "<p data-inquiry-support style=\"font-size:12px;line-height:1.5;margin:10px 0 0;max-width:470px\">Share the essentials. We’ll take it from there.</p>")
write_if_changed(services, sv)

# 7) Final rendered stylesheet additions for functional actions, the custom
# Join control, date picker, and both Inquiry kicker locations.
rendered = ROOT / 'assets' / 'rendered-corrections.css'
css = rendered.read_text(encoding='utf-8')
marker = '/* FINAL RENDERED FORM + PROGRAM PASS */'
block = r'''

/* FINAL RENDERED FORM + PROGRAM PASS */
form[data-inq] > button,
form[data-editorial-labels] button[type="submit"],
[aria-label="Newsletter"] form button,
[aria-label="The Sunday Reservation"] form button {
  font-family:var(--sc-sans) !important;
  font-size:9.5px !important;
  font-weight:400 !important;
  letter-spacing:.10em !important;
}

[data-form-instruction] {
  font-family:var(--sc-sans) !important;
  font-size:10px !important;
  font-weight:400 !important;
  letter-spacing:.07em !important;
  line-height:1.45 !important;
}

form[data-editorial-labels] button[aria-haspopup="listbox"],
form[data-editorial-labels] [role="listbox"] button[role="option"] {
  font-family:var(--sc-sans) !important;
  font-size:14px !important;
  font-weight:400 !important;
  letter-spacing:0 !important;
}

form[data-inq] button[aria-haspopup="dialog"] {
  font-family:var(--sc-sans) !important;
  font-size:14px !important;
  font-weight:400 !important;
  letter-spacing:0 !important;
}
form[data-inq] [aria-label="Choose a start date"] > div:first-child > span {
  font-family:var(--sc-sans) !important;
  font-size:10.5px !important;
  font-weight:400 !important;
  letter-spacing:.08em !important;
}
form[data-inq] [aria-label="Choose a start date"] > div:nth-child(2) {
  font-family:var(--sc-sans) !important;
  font-size:9.5px !important;
  font-weight:400 !important;
  letter-spacing:.045em !important;
}
form[data-inq] [role="checkbox"] {
  min-height:40px !important;
}
form[data-inq] [role="checkbox"] span:last-child {
  font-family:var(--sc-sans) !important;
  font-size:11px !important;
  font-weight:400 !important;
  letter-spacing:.075em !important;
}

[aria-label="Project inquiry"] [data-inquiry-kicker],
#inquiry [data-inquiry-kicker] {
  font-size:40px !important;
  line-height:.94 !important;
}
#inquiry [data-inquiry-support] {
  font-family:var(--sc-sans) !important;
  font-size:13px !important;
  font-weight:300 !important;
  letter-spacing:0 !important;
  line-height:1.5 !important;
}

@media (max-width:700px) {
  form[data-inq] > button,
  form[data-editorial-labels] button[type="submit"],
  [aria-label="Newsletter"] form button,
  [aria-label="The Sunday Reservation"] form button {
    font-size:10px !important;
  }
  [data-form-instruction] { font-size:10.5px !important; }
  form[data-editorial-labels] button[aria-haspopup="listbox"],
  form[data-editorial-labels] [role="listbox"] button[role="option"],
  form[data-inq] button[aria-haspopup="dialog"] {
    font-size:16px !important;
    min-height:44px !important;
  }
  form[data-inq] [role="checkbox"] span:last-child { font-size:10.75px !important; }
  [aria-label="Project inquiry"] [data-inquiry-kicker],
  #inquiry [data-inquiry-kicker] {
    font-size:46px !important;
  }
}
'''
if marker not in css:
    css += block
else:
    css = css[:css.index(marker)].rstrip() + block
write_if_changed(rendered, css)

print(f'Updated {len(changed)} production files')
for p in changed:
    print(p)
