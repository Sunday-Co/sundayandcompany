from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')

# Mark only actual program-card actions. The tiny catalog/receipt metadata can
# remain intentionally smaller.
cards = read('Program Cards.dc.html')
if 'data-program-cards' not in cards:
    cards = cards.replace('<div style="display:{{ cardsDisplay }};', '<div data-program-cards style="display:{{ cardsDisplay }};', 1)

# Flip text on the three card fronts.
cards, flip_count = re.subn(
    r'<span style="([^"]*font-size:7\.5px[^"]*)">Flip ',
    r'<span data-program-action style="\1">Flip ',
    cards,
)
if flip_count != 3:
    raise RuntimeError(f'program Flip actions: expected 3, found {flip_count}')

# Flip Back / View Full Details buttons on the three card backs.
cards, back_count = re.subn(
    r'<button type="button" onClick="\{\{ unflip \}\}"',
    '<button data-program-action type="button" onClick="{{ unflip }}"',
    cards,
)
if back_count != 3:
    raise RuntimeError(f'program Flip Back actions: expected 3, found {back_count}')

cards, detail_count = re.subn(
    r'<button type="button" onClick="\{\{ openD([0-2]) \}\}"',
    r'<button data-program-action type="button" onClick="{{ openD\1 }}"',
    cards,
)
if detail_count != 3:
    raise RuntimeError(f'program detail actions: expected 3, found {detail_count}')
write('Program Cards.dc.html', cards)

css = read('assets/site.css')
marker = '/* BATCH 1 FINAL: FUNCTIONAL MICROTYPE AUDIT */'
if marker in css:
    raise RuntimeError('Batch 1 final CSS already exists')
css += r'''

/* BATCH 1 FINAL: FUNCTIONAL MICROTYPE AUDIT
   Functional navigation/actions are brought into a readable 9–10px range.
   Tiny receipt/catalog metadata and real fine print stay intentionally smaller. */

header nav[aria-label="Primary navigation"] {
  font-size: 10px !important;
  letter-spacing: .14em !important;
}

header > div button[onClick*="openInquiry"],
header > div > a[href="/contact"] {
  font-size: 9.5px !important;
  font-weight: 400 !important;
  letter-spacing: .12em !important;
}

header > button[aria-label="Open menu"],
a[href="#top"]:first-child {
  font-size: 10px !important;
  letter-spacing: .13em !important;
}

[data-screen-label="Home"] section#top button[onClick*="openInquiry"],
[data-screen-label="Home"] section#top a[href="/contact"],
[data-screen-label="Services"] a[href="#service-menu"],
[data-screen-label="Services"] a[href="#inquiry"],
[data-screen-label="Services"] a[href^="mailto:"],
[data-screen-label="Contact"] button[onClick*="openInquiry"] {
  font-family: var(--sunday-sans) !important;
  font-size: 9.5px !important;
  font-weight: 400 !important;
  letter-spacing: .12em !important;
}

[data-screen-label="Contact"] a[href*="instagram.com"],
[data-screen-label="Contact"] a[href*="tiktok.com"],
[data-screen-label="Contact"] a[href*="linkedin.com"] {
  font-size: 9px !important;
  font-weight: 400 !important;
  letter-spacing: .10em !important;
}

[aria-label="Newsletter"] form button {
  font-size: 9.5px !important;
  font-weight: 400 !important;
  letter-spacing: .11em !important;
}

footer [data-footer-legal] {
  font-size: 9px !important;
  letter-spacing: .12em !important;
}

/* Services content labels are information, not decorative receipt metadata. */
[data-screen-label="Services"] [data-service-number],
[data-screen-label="Services"] [data-service-meta],
[data-screen-label="Services"] [data-service-included] {
  font-size: 9.5px !important;
  letter-spacing: .10em !important;
}

[data-screen-label="Services"] [data-service-price] {
  font-size: 10.5px !important;
  letter-spacing: .11em !important;
}

/* Program-card catalog text remains small; only the actions are promoted. */
[data-program-cards] [data-program-action] {
  font-family: var(--sunday-sans) !important;
  font-size: 9.5px !important;
  font-weight: 400 !important;
  letter-spacing: .11em !important;
}

@media (max-width: 700px) {
  header nav[aria-label="Primary navigation"] { font-size: 10px !important; }

  [data-screen-label="Services"] [data-service-number],
  [data-screen-label="Services"] [data-service-meta],
  [data-screen-label="Services"] [data-service-included] {
    font-size: 10.5px !important;
    letter-spacing: .095em !important;
  }

  [data-screen-label="Services"] [data-service-price] {
    font-size: 11.5px !important;
    letter-spacing: .10em !important;
  }

  [data-program-cards] [data-program-action] {
    font-size: 10px !important;
    min-height: 44px !important;
  }
}
'''
write('assets/site.css', css)

# Synchronize Program Cards copies after the audited root changes.
root_cards = read('Program Cards.dc.html')
for p in ROOT.rglob('Program Cards.dc.html'):
    if p == ROOT / 'Program Cards.dc.html':
        continue
    p.write_text(root_cards, encoding='utf-8')

# Record the classification decision in the temporary source report.
report = read('QA_SOURCE_REPORT.md')
report += '''\n## Small-type classification decision\n\n- Functional navigation, CTA, form actions, Services information labels and Program Card actions are promoted by the shared CSS into a readable functional range.\n- Project Inquiry/Contact/Sunday School form labels and actions are governed by the dedicated form typography system.\n- Footer Explore/email/location/social content remains at the approved 12.5px secondary-text scale.\n- Receipt numbers, catalog numbers, status metadata and decorative indexing may intentionally remain below 11px.\n- Newsletter privacy/unsubscribe copy remains intentionally quiet fine print, with its own mobile rule rather than inheriting functional UI sizing.\n'''
write('QA_SOURCE_REPORT.md', report)

check = read('CORRECTION_CHECKLIST.md')
repls = {
    '- [ ] Normalize excessive letter-spacing on all remaining small uppercase UI.': '- [x] Normalize excessive letter-spacing on remaining small functional uppercase UI while preserving decorative receipt/catalog spacing.',
    '- [ ] Audit all remaining functional text below roughly 11px and decide intentionally whether it is functional, decorative receipt metadata, or true fine print.': '- [x] Audit remaining sub-11px text and classify it as functional UI, decorative receipt/catalog metadata, or true fine print; decision recorded in `QA_SOURCE_REPORT.md`.',
}
for old, new in repls.items():
    if old not in check:
        raise RuntimeError(f'checklist item missing: {old}')
    check = check.replace(old, new)
write('CORRECTION_CHECKLIST.md', check)

print('Batch 1 final functional microtype audit applied.')
