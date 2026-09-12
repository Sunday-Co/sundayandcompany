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

LIBRARY_STYLE = r'''
  /* SUNDAY ARCHIVE LIBRARY CARD MODALS */
  [role="dialog"][aria-label="The Fellows Table"],
  [role="dialog"][aria-label="The Espresso Club"],
  [role="dialog"][aria-label="The Founders Club"] {
    background-color:#f5efe6 !important;
    background-image:linear-gradient(to bottom,rgba(49,29,3,.026) 1px,transparent 1px) !important;
    background-size:100% 32px !important;
    box-shadow:0 18px 56px rgba(27,15,3,.28),inset 0 0 0 5px #f5efe6,inset 0 0 0 6px rgba(49,29,3,.28) !important;
    isolation:isolate;
  }

  [role="dialog"][aria-label="The Fellows Table"] > div:nth-child(2)::before,
  [role="dialog"][aria-label="The Espresso Club"] > div:nth-child(2)::before,
  [role="dialog"][aria-label="The Founders Club"] > div:nth-child(2)::before {
    background:rgba(245,239,230,.88);
    border-bottom:1px solid rgba(49,29,3,.44);
    border-top:1px solid rgba(49,29,3,.44);
    color:#311d03;
    display:block;
    font-family:'Inter Tight',sans-serif;
    font-size:7px;
    font-weight:500;
    letter-spacing:.16em;
    line-height:1.7;
    margin:0 0 4px;
    padding:8px 0;
    text-transform:uppercase;
    white-space:pre-line;
  }

  [role="dialog"][aria-label="The Fellows Table"] > div:nth-child(2)::before {
    content:'SUNDAY & CO. ARCHIVE · RECORD 01\A FILED UNDER: INTERNSHIP · STATUS: INTEREST FILE';
  }
  [role="dialog"][aria-label="The Espresso Club"] > div:nth-child(2)::before {
    content:'SUNDAY & CO. ARCHIVE · RECORD 02\A FILED UNDER: FREELANCE CONTRIBUTOR · STATUS: INTEREST FILE';
  }
  [role="dialog"][aria-label="The Founders Club"] > div:nth-child(2)::before {
    content:'SUNDAY & CO. ARCHIVE · RECORD 03\A FILED UNDER: MEMBERSHIP · STATUS: COMING SOON';
  }

  [role="dialog"][aria-label="The Fellows Table"] > div:nth-child(3),
  [role="dialog"][aria-label="The Espresso Club"] > div:nth-child(3),
  [role="dialog"][aria-label="The Founders Club"] > div:nth-child(3) {
    background:rgba(176,124,115,.08);
    border-color:rgba(49,29,3,.42) !important;
    padding-left:10px !important;
    padding-right:10px !important;
  }

  [role="dialog"][aria-label="The Fellows Table"] h2,
  [role="dialog"][aria-label="The Espresso Club"] h2,
  [role="dialog"][aria-label="The Founders Club"] h2 {
    text-wrap:balance;
  }

  [role="dialog"][aria-label="The Fellows Table"]::after,
  [role="dialog"][aria-label="The Espresso Club"]::after,
  [role="dialog"][aria-label="The Founders Club"]::after {
    background:#f5efe6;
    border:1px solid rgba(176,124,115,.72);
    color:#a56f67;
    content:'REFERENCE COPY · FILED 2026';
    display:block;
    font-family:'Inter Tight',sans-serif;
    font-size:6.5px;
    font-weight:600;
    letter-spacing:.18em;
    margin:18px 2px 0 auto;
    padding:5px 8px;
    text-transform:uppercase;
    transform:rotate(-1.1deg);
    width:max-content;
  }

  @media (max-width:720px) {
    [role="dialog"][aria-label="The Fellows Table"],
    [role="dialog"][aria-label="The Espresso Club"],
    [role="dialog"][aria-label="The Founders Club"] {
      background-size:100% 29px !important;
      box-shadow:0 14px 42px rgba(27,15,3,.26),inset 0 0 0 4px #f5efe6,inset 0 0 0 5px rgba(49,29,3,.25) !important;
    }
    [role="dialog"][aria-label="The Fellows Table"] > div:nth-child(2)::before,
    [role="dialog"][aria-label="The Espresso Club"] > div:nth-child(2)::before,
    [role="dialog"][aria-label="The Founders Club"] > div:nth-child(2)::before {
      font-size:6.25px;
      letter-spacing:.145em;
      line-height:1.65;
      padding:7px 0;
    }
    [role="dialog"][aria-label="The Fellows Table"]::after,
    [role="dialog"][aria-label="The Espresso Club"]::after,
    [role="dialog"][aria-label="The Founders Club"]::after {
      font-size:6px;
      margin-top:16px;
    }
  }
'''

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
    if 'SUNDAY ARCHIVE LIBRARY CARD MODALS' not in text:
        if '</style>' not in text:
            raise SystemExit(f'Missing style block in {path}')
        text = text.replace('</style>', LIBRARY_STYLE + '\n</style>', 1)
        changed = True
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

for marker in [
    "dialogPosition: 'fixed'",
    "dialogAria: 'true'",
    "dialogOuterPad: t ? '12px' : '18px'",
    'SUNDAY ARCHIVE LIBRARY CARD MODALS',
    'SUNDAY & CO. ARCHIVE · RECORD 01',
    'REFERENCE COPY · FILED 2026',
]:
    if marker not in root_program:
        raise SystemExit(f'Missing Program Cards modal marker: {marker}')

print(f'Updated {len(program_files)} Program Cards copies with verified modal behavior, library-card styling, and v8 assets')
