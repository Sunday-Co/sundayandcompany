from pathlib import Path

ROOT = Path('.')

PROGRAM_REPLACEMENTS = {
    "dialogPosition: t ? 'static' : 'fixed',": "dialogPosition: 'fixed',",
    "dialogInset: t ? 'auto' : '0',": "dialogInset: '0',",
    "dialogBackdrop: t ? 'transparent' : 'rgba(27,15,3,.66)',": "dialogBackdrop: 'rgba(27,15,3,.66)',",
    "dialogBlur: t ? 'none' : 'blur(5px)',": "dialogBlur: 'blur(5px)',",
    "dialogOuterOverflow: t ? 'visible' : 'auto',": "dialogOuterOverflow: 'auto',",
    "dialogOuterPad: t ? '0' : '18px',": "dialogOuterPad: t ? '12px' : '18px',",
    "dialogAlign: t ? 'stretch' : 'center',": "dialogAlign: 'center',",
    "dialogZ: t ? 'auto' : '80',": "dialogZ: '80',",
    "dialogMargin: t ? '16px 0 0' : 'auto',": "dialogMargin: 'auto',",
    "dialogMaxHeight: t ? 'none' : 'min(86vh,760px)',": "dialogMaxHeight: t ? 'calc(100svh - 24px)' : 'min(86vh,760px)',",
    "dialogMaxWidth: t ? '100%' : 'min(900px, calc(100vw - 36px))',": "dialogMaxWidth: t ? 'calc(100vw - 24px)' : 'min(900px, calc(100vw - 36px))',",
    "dialogInnerOverflow: t ? 'visible' : 'auto',": "dialogInnerOverflow: 'auto',",
    "dialogPad: t ? '24px 18px 28px' : 'clamp(24px,4vw,48px)',": "dialogPad: t ? '16px 16px 22px' : 'clamp(24px,4vw,48px)',",
    "dialogAria: t ? 'false' : 'true',": "dialogAria: 'true',",
}

program_files = sorted(ROOT.rglob('Program Cards.dc.html'))
if not program_files:
    raise SystemExit('No Program Cards.dc.html files found')

for path in program_files:
    text = path.read_text(encoding='utf-8')
    changed = False
    for old, new in PROGRAM_REPLACEMENTS.items():
        if old in text:
            text = text.replace(old, new)
            changed = True
        elif new not in text:
            raise SystemExit(f'Missing expected Program Cards marker in {path}: {old}')
    if changed:
        path.write_text(text, encoding='utf-8')

for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = text.replace('v=20260912-7', 'v=20260912-8')
    if updated != text:
        path.write_text(updated, encoding='utf-8')

# Strict source markers for the intended end state.
css = Path('assets/rendered-corrections.css').read_text(encoding='utf-8')
js = Path('assets/site.js').read_text(encoding='utf-8')
root_program = Path('Program Cards.dc.html').read_text(encoding='utf-8')

required_css = [
    'font-size:30px !important;',
    'margin:0 0 -3px 1px !important;',
    '[data-res-fineprint]',
    'font-size:5.75px !important;',
    'sc-neon-sunday-final 8.4s ease-in-out infinite',
    'sc-sway-sunday-continuous 12s ease-in-out infinite',
    '[data-sunday-grid-hero="true"]',
]
for marker in required_css:
    if marker not in css:
        raise SystemExit(f'Missing CSS marker: {marker}')

for forbidden in ['sc-paper-lift-final', 'sc-step-turn-final', 'sc-accordion-final', 'sc-program-detail']:
    if forbidden in css:
        raise SystemExit(f'Recent motion marker still present in CSS: {forbidden}')

for forbidden in ['animateSection(', 'animatePinyon(', 'revealSections(', 'IntersectionObserver']:
    if forbidden in js:
        raise SystemExit(f'Recent section motion still present in site.js: {forbidden}')

for marker in ["dialogPosition: 'fixed'", "dialogAria: 'true'", "dialogOuterPad: t ? '12px' : '18px'"]:
    if marker not in root_program:
        raise SystemExit(f'Missing Program Cards modal marker: {marker}')

print(f'Updated {len(program_files)} Program Cards copies and asset references to v8')
