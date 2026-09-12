from pathlib import Path

path = Path('assets/rendered-corrections.css')
text = path.read_text(encoding='utf-8')

old_neon = '*[style*="sc-warm"][style*="sc-neon"]'
new_neon = '[data-sign] p[aria-hidden][style*="Pinyon Script"]'
old_sway = '*[style*="sc-rock"][style*="sc-sway"]'
new_sway = '[data-sign] > div[style*="transform-origin"]'

if text.count(old_neon) != 2:
    raise SystemExit(f'Expected two old neon selectors, found {text.count(old_neon)}')
if text.count(old_sway) != 2:
    raise SystemExit(f'Expected two old sway selectors, found {text.count(old_sway)}')

text = text.replace(old_neon, new_neon)
text = text.replace(old_sway, new_sway)

# The sign should breathe continuously once the page is loaded. The selector is
# structural rather than state-dependent, so Safari cannot miss the animation
# while the component is toggling its signOn state.
if 'sc-neon-sunday-final 8.4s ease-in-out 4.6s infinite' not in text:
    raise SystemExit('Final 8.4s neon cadence is missing')
if 'sc-sway 12s ease-in-out 7s infinite' not in text:
    raise SystemExit('Final 12s sway cadence is missing')

path.write_text(text, encoding='utf-8')
