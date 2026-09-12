from pathlib import Path
import re

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


# ------------------------------------------------------------
# Batch 8: Safari/WebKit hero stability.
# Keep a real CSS background under image heroes and take the
# homepage/About hero image out of normal document flow.
# ------------------------------------------------------------
home = read('index.html')
home = replace_once(
    home,
    'style="height:100%;object-fit:cover;object-position:50% 48%;position:relative;width:100%;z-index:0"',
    'style="height:100%;inset:0;object-fit:cover;object-position:50% 48%;position:absolute;width:100%;z-index:0"',
    'home hero absolute image',
)
# Client letters already behave like stacked paper; add a semantic hook for QA/motion rules.
old_letter = '<article style="background:#fffdf8;min-height:{{ gbH }};'
if home.count(old_letter) != 4:
    raise RuntimeError(f'client love letters: expected 4 cards, found {home.count(old_letter)}')
home = home.replace(old_letter, '<article data-love-letter style="background:#fffdf8;min-height:{{ gbH }};')
write('index.html', home)

about = read('about/index.html')
about = replace_once(
    about,
    '<section id="top" aria-labelledby="about-hero-title" style="scroll-margin-top:92px;color:#f5efe6;height:min(760px,82svh);min-height:520px;overflow:hidden;position:relative">',
    '<section id="top" data-screen-hero="image" aria-labelledby="about-hero-title" style="background:#311d03 url(\'/assets/about-hero.jpg\') center 61% / cover no-repeat;scroll-margin-top:92px;color:#f5efe6;height:min(760px,82svh);min-height:520px;overflow:hidden;position:relative">',
    'about hero fallback',
)
about = replace_once(
    about,
    'style="height:100%;object-fit:cover;object-position:center 61%;width:100%"',
    'style="height:100%;inset:0;object-fit:cover;object-position:center 61%;position:absolute;width:100%;z-index:0"',
    'about hero absolute image',
)
write('about/index.html', about)

school = read('sunday-school/index.html')
school = replace_once(
    school,
    '<section aria-labelledby="school-title" style="align-items:end;color:#f5efe6;display:grid;isolation:isolate;min-height:68svh;overflow:hidden;padding:118px max(clamp(22px,7vw,110px), calc((100vw - 1240px) / 2)) 58px;position:relative">',
    '<section data-screen-hero="image" aria-labelledby="school-title" style="align-items:end;background:#311d03 url(\'/assets/sunday-school-hero.jpg\') center / cover no-repeat;color:#f5efe6;display:grid;isolation:isolate;min-height:68svh;overflow:hidden;padding:118px max(clamp(22px,7vw,110px), calc((100vw - 1240px) / 2)) 58px;position:relative">',
    'sunday school hero fallback',
)
write('sunday-school/index.html', school)

js = read('assets/site.js')
js = replace_once(
    js,
    "document.querySelectorAll('section#top').forEach(function (hero) {\n      var img = hero.querySelector(':scope > img');",
    "document.querySelectorAll('section#top, section[data-screen-hero]').forEach(function (hero) {\n      var img = hero.querySelector(':scope > img, :scope > div:first-child img');",
    'hero runtime coverage',
)
write('assets/site.js', js)


# ------------------------------------------------------------
# Batch 9: restrained editorial motion hooks.
# ------------------------------------------------------------
header = read('Site Header.dc.html')
header = replace_once(
    header,
    '<aside aria-label="Sunday &amp; Company navigation"',
    '<aside data-sheet-state="{{ sheetState }}" aria-label="Sunday &amp; Company navigation"',
    'mobile sheet state hook',
)
header = replace_once(
    header,
    "      sheetTransform: this.state.sheet ? 'translateX(0)' : 'translateX(102%)',",
    "      sheetTransform: this.state.sheet ? 'translateX(0)' : 'translateX(102%)',\n      sheetState: this.state.sheet ? 'open' : 'closed',",
    'mobile sheet render state',
)
write('Site Header.dc.html', header)

inq = read('Inquiry Form.dc.html')
# Mark the three step panels so opening a new stage gets a tiny paper-like reveal.
inq, step_count = re.subn(r'(<(?:label|div|fieldset)\s+)data-step="([123])"', r'\1data-step-panel data-step="\2"', inq)
if step_count < 8:
    raise RuntimeError(f'inquiry step hooks: expected at least 8, found {step_count}')
write('Inquiry Form.dc.html', inq)

services = read('services/index.html')
services, service_count = re.subn(
    r'<div style="([^"]*display:\{\{ body[0-2] \}\}[^"]*)">',
    r'<div data-service-body style="\1">',
    services,
)
if service_count != 3:
    raise RuntimeError(f'service accordion hooks: expected 3, found {service_count}')
services, process_count = re.subn(
    r'<p style="([^"]*display:\{\{ bodyP[0-3] \}\}[^"]*)">',
    r'<p data-process-body style="\1">',
    services,
)
if process_count != 4:
    raise RuntimeError(f'process accordion hooks: expected 4, found {process_count}')
write('services/index.html', services)

css = read('assets/site.css')
marker = '/* BATCH 8-9: HERO STABILITY + EDITORIAL MOTION */'
if marker in css:
    raise RuntimeError('Batch 8-9 CSS block already exists')
css += r'''

/* BATCH 8-9: HERO STABILITY + EDITORIAL MOTION */
html,
body {
  max-width: 100%;
  overflow-x: clip;
}

/* Full-page capture safety: the homepage keeps a real background image under
   the absolutely positioned photo, and its height is based on width rather
   than a changing browser-chrome viewport. */
section#top[data-screen-hero="home"] {
  height: clamp(680px, 66.5vw, 900px) !important;
  min-height: 680px !important;
  background-position: 50% 48% !important;
}

section[data-screen-hero="image"][data-hero-fallback="ready"],
section#top[data-hero-fallback="ready"] {
  background-color: var(--sunday-espresso) !important;
  background-repeat: no-repeat !important;
  background-size: cover !important;
}

@media (max-width: 700px) {
  section#top[data-screen-hero="home"] {
    height: clamp(680px, 185vw, 820px) !important;
    min-height: 680px !important;
  }
}

@keyframes sunday-step-in {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes sunday-accordion-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes sunday-menu-row-in {
  from { opacity: 0; transform: translateX(7px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Inquiry stages feel like turning to the next part of the same receipt. */
form[data-inq] [data-step-panel] {
  animation: sunday-step-in 190ms cubic-bezier(.22,.75,.18,1) both;
}

/* Service/process accordions already rotate their arrows; the opened copy now
   arrives with a restrained fade rather than snapping into place. */
[data-service-body],
[data-process-body] {
  animation: sunday-accordion-in 220ms cubic-bezier(.22,.75,.18,1) both;
}

/* Pinyon heading accents follow the Playfair line by a fraction of a beat. */
.sc-reveal h1 [style*="Pinyon Script"],
.sc-reveal h2 [style*="Pinyon Script"],
.sc-reveal h3 [style*="Pinyon Script"] {
  opacity: 0;
  transform: translateY(4px);
  transition: opacity 360ms ease 90ms, transform 360ms cubic-bezier(.22,.75,.18,1) 90ms;
}

.sc-reveal.sc-in h1 [style*="Pinyon Script"],
.sc-reveal.sc-in h2 [style*="Pinyon Script"],
.sc-reveal.sc-in h3 [style*="Pinyon Script"] {
  opacity: 1;
  transform: translateY(0);
}

/* Mobile navigation: a very small row stagger, no bounce. */
@media (max-width: 1240px) {
  aside[data-sheet-state="open"] nav > a,
  aside[data-sheet-state="open"] [data-sheet-cta] {
    animation: sunday-menu-row-in 260ms cubic-bezier(.22,.75,.18,1) both;
  }
  aside[data-sheet-state="open"] nav > a:nth-child(1) { animation-delay: 30ms; }
  aside[data-sheet-state="open"] nav > a:nth-child(2) { animation-delay: 55ms; }
  aside[data-sheet-state="open"] nav > a:nth-child(3) { animation-delay: 80ms; }
  aside[data-sheet-state="open"] nav > a:nth-child(4) { animation-delay: 105ms; }
  aside[data-sheet-state="open"] nav > a:nth-child(5) { animation-delay: 130ms; }
  aside[data-sheet-state="open"] [data-sheet-cta]:first-child { animation-delay: 150ms; }
  aside[data-sheet-state="open"] [data-sheet-cta]:last-child { animation-delay: 175ms; }
}

/* Client Love Letters intentionally remain a physical paper stack. */
[data-love-letter] {
  will-change: transform, opacity;
}

@media (prefers-reduced-motion: reduce) {
  form[data-inq] [data-step-panel],
  [data-service-body],
  [data-process-body],
  aside[data-sheet-state="open"] nav > a,
  aside[data-sheet-state="open"] [data-sheet-cta] {
    animation: none !important;
  }

  .sc-reveal h1 [style*="Pinyon Script"],
  .sc-reveal h2 [style*="Pinyon Script"],
  .sc-reveal h3 [style*="Pinyon Script"],
  .sc-reveal.sc-in h1 [style*="Pinyon Script"],
  .sc-reveal.sc-in h2 [style*="Pinyon Script"],
  .sc-reveal.sc-in h3 [style*="Pinyon Script"] {
    opacity: 1 !important;
    transform: none !important;
    transition: none !important;
  }
}
'''
write('assets/site.css', css)


# ------------------------------------------------------------
# Synchronize shared component copies after root source changes.
# ------------------------------------------------------------
for name in ['Inquiry Form.dc.html', 'Site Header.dc.html']:
    root_text = read(name)
    for p in ROOT.rglob(name):
        if p == ROOT / name:
            continue
        p.write_text(root_text, encoding='utf-8')


# ------------------------------------------------------------
# Source audit report: inventory hero/capture risk signals and tiny
# functional text so final QA is based on a concrete list.
# ------------------------------------------------------------
page_files = []
for p in ROOT.rglob('index.html'):
    if any(part.startswith('.') for part in p.relative_to(ROOT).parts):
        continue
    page_files.append(p)
page_files.append(ROOT / '404.html')
page_files = sorted(set(page_files))

lines = [
    '# Sunday & Company Source QA Report',
    '',
    'Generated by `scripts/apply-batch-8-9.py` on the correction branch.',
    '',
    '## Hero / viewport audit',
    '',
    '| File | Hero/image signal | viewport-unit signal |',
    '| --- | --- | --- |',
]
for p in page_files:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    rel = str(p.relative_to(ROOT))
    tags = re.findall(r'<section\b[^>]*>', text)
    hero_tags = [t for t in tags if 'id="top"' in t or 'data-screen-hero=' in t or 'aria-labelledby="school-title"' in t]
    sample = ' '.join(hero_tags[:2])
    image_signal = 'yes' if re.search(r'<img\b', text[text.find(hero_tags[0]):text.find(hero_tags[0]) + 1800] if hero_tags else '') else 'no/none'
    units = []
    for token in ['svh', 'dvh', 'lvh', 'vh']:
        if token in sample:
            units.append(token)
    lines.append(f'| `{rel}` | {image_signal} | {", ".join(units) if units else "none in hero tag"} |')

lines += [
    '',
    '## Tiny functional-text scan',
    '',
    'This is an inventory, not a blanket instruction to enlarge everything. Receipt metadata and true fine print may intentionally remain small.',
    '',
]
pattern = re.compile(r'font-size:([0-9]+(?:\.[0-9]+)?)px')
for p in page_files + [ROOT / 'Site Header.dc.html', ROOT / 'Site Footer.dc.html', ROOT / 'Inquiry Form.dc.html', ROOT / 'Program Cards.dc.html']:
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    vals = sorted({float(m.group(1)) for m in pattern.finditer(text) if float(m.group(1)) < 11})
    if vals:
        rel = str(p.relative_to(ROOT))
        lines.append(f'- `{rel}`: ' + ', '.join(f'{v:g}px' for v in vals))
write('QA_SOURCE_REPORT.md', '\n'.join(lines) + '\n')


# ------------------------------------------------------------
# Checklist: check only source-level work. WebKit/Safari screenshots
# and final visual QA remain deliberately unchecked.
# ------------------------------------------------------------
check = read('CORRECTION_CHECKLIST.md')
check = check.replace(
    '- [ ] Audit every page hero that relies on viewport height, absolute image layers or compositing.',
    '- [x] Audit every page hero that relies on viewport height, absolute image layers or compositing; inventory written to `QA_SOURCE_REPORT.md`.',
)
for old, new in [
    ('- [ ] Keep motion restrained and specific to Sunday & Co.', '- [x] Keep motion restrained and specific to Sunday & Co. in the shared/source motion layer.'),
    ('- [ ] Section reveals use small upward drift + fade where appropriate.', '- [x] Section reveals use small upward drift + fade where appropriate.'),
    ('- [ ] Pinyon accents can reveal slightly after Playfair headings.', '- [x] Pinyon heading accents reveal slightly after Playfair headings.'),
    ('- [ ] Project Inquiry step transitions are subtle rather than abrupt.', '- [x] Project Inquiry step panels use a subtle short fade/up transition.'),
    ('- [ ] Service accordion arrows rotate and content fades cleanly.', '- [x] Service/process accordion arrows rotate and opened content fades cleanly.'),
    ('- [ ] Image/editorial blocks use restrained reveal behavior only where it adds value.', '- [x] Image/editorial sections use the existing restrained reveal behavior only where it adds value.'),
    ('- [ ] Mobile menu uses a subtle row stagger if it remains clean in QA.', '- [x] Mobile menu uses a subtle short row stagger; final visual QA remains pending.'),
    ('- [ ] Client Love Letters motion feels like paper/notes rather than generic app animation.', '- [x] Client Love Letters retain the stacked-paper transform/opacity motion and are tagged for QA.'),
]:
    if old not in check:
        raise RuntimeError(f'checklist item not found: {old}')
    check = check.replace(old, new)
write('CORRECTION_CHECKLIST.md', check)

print('Batch 8-9 source corrections applied.')
