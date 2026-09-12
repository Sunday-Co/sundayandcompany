from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def rw(path, fn):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    new = fn(text)
    if new == text:
        print(f'no change {path}')
    else:
        p.write_text(new, encoding='utf-8')
        print(f'updated {path}')


def fix_home(text):
    old = 'Marketing Should Feel Less Like Noise And More Like An Invitation. We Believe The Strongest Brands Give People Something Meaningful To Recognize, Return To And Gather Around.'
    new = 'Marketing should feel less like noise and more like an invitation. We believe the strongest brands give people something meaningful to recognize, return to and gather around.'
    if old not in text and new not in text:
        raise SystemExit('home quote text not found')
    return text.replace(old, new, 1)


def fix_inquiry(text):
    # Replace compact current-step + dots row with the approved three named steps.
    old = '''      <div style="align-items:center;display:flex;gap:12px;justify-content:space-between">
        <span style="font-family:'Inter Tight',sans-serif;font-size:10px;letter-spacing:.11em;text-transform:uppercase">{{ stepLabel }}</span>
        <span aria-hidden="true" style="align-items:center;display:flex;flex:0 0 auto;gap:6px">
          <span style="align-items:center;border-radius:50%;display:flex;flex:0 0 18px;font-family:'Inter Tight',sans-serif;font-size:9px;height:18px;justify-content:center;background:{{ d1bg }};border:1px solid {{ d1bd }};color:{{ d1fg }}">1</span>
          <span style="height:1px;width:14px;background:{{ r1 }}"></span>
          <span style="align-items:center;border-radius:50%;display:flex;flex:0 0 18px;font-family:'Inter Tight',sans-serif;font-size:9px;height:18px;justify-content:center;background:{{ d2bg }};border:1px solid {{ d2bd }};color:{{ d2fg }}">2</span>
          <span style="height:1px;width:14px;background:{{ r2 }}"></span>
          <span style="align-items:center;border-radius:50%;display:flex;flex:0 0 18px;font-family:'Inter Tight',sans-serif;font-size:9px;height:18px;justify-content:center;background:{{ d3bg }};border:1px solid {{ d3bd }};color:{{ d3fg }}">3</span>
        </span>
      </div>'''
    new = '''      <div aria-label="Project inquiry steps" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0">
        <span style="background:{{ step1TabBg }};border-right:1px solid rgba(49,29,3,.22);color:{{ step1TabFg }};font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:400;letter-spacing:.09em;line-height:1.2;padding:9px 8px;text-align:center;text-transform:uppercase">01&nbsp; Project Basics</span>
        <span style="background:{{ step2TabBg }};border-right:1px solid rgba(49,29,3,.22);color:{{ step2TabFg }};font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:400;letter-spacing:.09em;line-height:1.2;padding:9px 8px;text-align:center;text-transform:uppercase">02&nbsp; Timing &amp; Budget</span>
        <span style="background:{{ step3TabBg }};color:{{ step3TabFg }};font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:400;letter-spacing:.09em;line-height:1.2;padding:9px 8px;text-align:center;text-transform:uppercase">03&nbsp; Project Scope</span>
      </div>'''
    if old in text:
        text = text.replace(old, new, 1)
    elif 'aria-label="Project inquiry steps"' not in text:
        raise SystemExit('inquiry step navigation did not match')

    anchor = "    out.stepLabel = st === 1 ? '01 · Project Basics' : st === 2 ? '02 · Timing & Budget' : '03 · Project Scope';\n"
    add = anchor + "    out.step1TabBg = st === 1 ? '#ac746c' : 'transparent';\n    out.step1TabFg = st === 1 ? '#fffdf8' : '#311d03';\n    out.step2TabBg = st === 2 ? '#ac746c' : 'transparent';\n    out.step2TabFg = st === 2 ? '#fffdf8' : '#311d03';\n    out.step3TabBg = st === 3 ? '#ac746c' : 'transparent';\n    out.step3TabFg = st === 3 ? '#fffdf8' : '#311d03';\n"
    if 'out.step1TabBg' not in text:
        if anchor not in text:
            raise SystemExit('inquiry render anchor missing')
        text = text.replace(anchor, add, 1)
    return text


def fix_program_cards(text):
    replacements = {
        "dialogPosition: 'fixed',": "dialogPosition: t ? 'static' : 'fixed',",
        "dialogInset: '0',": "dialogInset: t ? 'auto' : '0',",
        "dialogBackdrop: 'rgba(27,15,3,.66)',": "dialogBackdrop: t ? 'transparent' : 'rgba(27,15,3,.66)',",
        "dialogBlur: 'blur(5px)',": "dialogBlur: t ? 'none' : 'blur(5px)',",
        "dialogOuterOverflow: 'auto',": "dialogOuterOverflow: t ? 'visible' : 'auto',",
        "dialogOuterPad: t ? '12px' : '18px',": "dialogOuterPad: t ? '0' : '18px',",
        "dialogAlign: 'center',": "dialogAlign: t ? 'stretch' : 'center',",
        "dialogZ: '80',": "dialogZ: t ? 'auto' : '80',",
        "dialogMargin: 'auto',": "dialogMargin: t ? '16px 0 0' : 'auto',",
        "dialogMaxHeight: t ? 'calc(100svh - 24px)' : 'min(86vh,760px)',": "dialogMaxHeight: t ? 'none' : 'min(86vh,760px)',",
        "dialogMaxWidth: t ? 'calc(100vw - 24px)' : 'min(900px, calc(100vw - 36px))',": "dialogMaxWidth: t ? '100%' : 'min(900px, calc(100vw - 36px))',",
        "dialogInnerOverflow: 'auto',": "dialogInnerOverflow: t ? 'visible' : 'auto',",
        "dialogPad: t ? '16px 16px 22px' : 'clamp(24px,4vw,48px)',": "dialogPad: t ? '24px 18px 28px' : 'clamp(24px,4vw,48px)',",
        "dialogAria: 'true',": "dialogAria: t ? 'false' : 'true',",
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f'program cards anchor missing: {old}')
    return text


def fix_css(text):
    # Exact approved compact receipt proportions plus the user's latest note that
    # mobile legal copy should stay smaller than the rest of the popup.
    text = text.replace('width: min(900px, calc(100vw - 72px)) !important;', 'width: min(880px, calc(100vw - 64px)) !important;')
    text = text.replace('max-width: 900px !important;', 'max-width: 880px !important;')
    text = text.replace('padding: 31px 40px 38px !important;', 'padding: 30px 38px 34px !important;')
    text = text.replace('min-height: min(700px, calc(100svh - 36px)) !important;', 'min-height: min(620px, 70svh) !important;')
    text = text.replace('padding: 23px 18px 38px !important;', 'padding: 22px 18px 28px !important;')

    text = text.replace('width: min(840px, calc(100vw - 64px)) !important;', 'width: min(800px, calc(100vw - 56px)) !important;')
    text = text.replace('max-width: 840px !important;', 'max-width: 800px !important;')
    text = text.replace('height: 560px !important;', 'height: 540px !important;')
    text = text.replace('[aria-label="The Sunday Reservation"] [data-res-fineprint] { font-size: 8.5px !important; }', '[aria-label="The Sunday Reservation"] [data-res-fineprint] { font-size: 9px !important; }')
    # Latest correction: the unsubscribe/privacy line on mobile was still too large.
    text = text.replace('font-size: 8.5px !important;\n    line-height: 1.45 !important;\n    letter-spacing: .07em !important;', 'font-size: 8px !important;\n    line-height: 1.45 !important;\n    letter-spacing: .06em !important;')

    # Footer is one secondary type system, including the tagline and legal copy.
    footer_marker = '/* Footer: one consistent secondary-font system for functional information. */'
    if footer_marker in text and 'footer,\nfooter * {' not in text:
        insert = footer_marker + "\nfooter,\nfooter * {\n  font-family: var(--sunday-sans) !important;\n}\nfooter { font-weight: 300 !important; }\n"
        text = text.replace(footer_marker, insert, 1)

    # Mobile footer readability from the approved correction pass.
    mobile_footer = '''\n@media (max-width: 700px) {\n  footer a[href="/about"],\n  footer a[href="/services"],\n  footer a[href="/our-work"],\n  footer a[href="/contact"],\n  footer a[href="/join-our-team"],\n  footer a[href="/sunday-school"] {\n    font-size: 14px !important;\n    line-height: 1.35 !important;\n  }\n  footer a[href*="instagram.com/sundayand_co"] { font-size: 13.5px !important; }\n}\n'''
    if 'footer a[href="/about"]' not in text:
        point = '/* Project inquiry receipt */'
        text = text.replace(point, mobile_footer + '\n' + point, 1)

    # Named step tabs need to stay legible on a narrow phone without becoming chunky.
    step_css = '''\n@media (max-width: 420px) {\n  [data-stepnav] [aria-label="Project inquiry steps"] > span {\n    font-size: 7.75px !important;\n    letter-spacing: .055em !important;\n    padding: 9px 5px !important;\n  }\n}\n'''
    if 'Project inquiry steps' not in text:
        point = '/* Sunday Reservation popup:'
        text = text.replace(point, step_css + '\n' + point, 1)
    return text

rw('index.html', fix_home)
rw('Inquiry Form.dc.html', fix_inquiry)
rw('Program Cards.dc.html', fix_program_cards)
rw('assets/site.css', fix_css)

# The page-local component copies must remain identical to the root components.
for page in ROOT.rglob('Inquiry Form.dc.html'):
    if page == ROOT / 'Inquiry Form.dc.html':
        continue
    page.write_text((ROOT / 'Inquiry Form.dc.html').read_text(encoding='utf-8'), encoding='utf-8')
for page in ROOT.rglob('Program Cards.dc.html'):
    if page == ROOT / 'Program Cards.dc.html':
        continue
    page.write_text((ROOT / 'Program Cards.dc.html').read_text(encoding='utf-8'), encoding='utf-8')

# Homepage has no duplicate route copy, but every HTML page imports shared site.css.
print('missed-corrections patch complete')
