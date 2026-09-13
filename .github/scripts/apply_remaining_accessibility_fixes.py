from pathlib import Path
import re

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def require_replace(text, old, new, label, minimum=1):
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f'{label}: expected at least {minimum} occurrence(s), found {count}')
    return text.replace(old, new), count

# 1) Footer source: keep the brand rose, but use a lighter accessible rose on espresso for small text.
footer_path = 'Site Footer.dc.html'
footer = read(footer_path)
footer, c1 = require_replace(
    footer,
    "color:#ac746c;font-family:'Inter Tight',sans-serif;font-size:9px;font-weight:500",
    "color:#c88f87;font-family:'Inter Tight',sans-serif;font-size:9px;font-weight:500",
    'footer utility labels',
    minimum=3,
)
footer, c2 = require_replace(
    footer,
    "<em style=\"color:#ac746c;font-family:'Inter Tight',sans-serif;font-style:italic;font-weight:300\">Our Table.</em>",
    "<em style=\"color:#c88f87;font-family:'Inter Tight',sans-serif;font-style:italic;font-weight:300\">Our Table.</em>",
    'footer tagline rose',
)
footer = footer.replace('style-hover="color:#ac746c"', 'style-hover="color:#c88f87"')
write(footer_path, footer)

# 2) Homepage: remove nested interactive semantics from the decorative OPEN sign and
# use an accessible darker rose only for the active service-sheet background.
home_path = 'index.html'
home = read(home_path)
home, c3 = require_replace(
    home,
    '<div data-sign="true" role="button" tabindex="0" aria-label="Give the sign a nudge"',
    '<div data-sign="true"',
    'OPEN sign nested interaction',
)
home, c4 = require_replace(
    home,
    "out['svcBg' + i] = on ? '#ac746c' : base[i];",
    "out['svcBg' + i] = on ? '#955851' : base[i];",
    'active service sheet background',
)
home = home.replace('style-hover="background:#ac746c;', 'style-hover="background:#955851;')
write(home_path, home)

# 3) Inquiry Form: active step and selected calendar dates need text/background AA contrast.
inq_path = 'Inquiry Form.dc.html'
inq = read(inq_path)
for idx in (1, 2, 3):
    old = f"out.step{idx}TabBg = st === {idx} ? '#ac746c' : 'transparent';"
    new = f"out.step{idx}TabBg = st === {idx} ? '#955851' : 'transparent';"
    inq, _ = require_replace(inq, old, new, f'inquiry active step {idx}')
inq = inq.replace("background: on ? '#ac746c' : 'transparent'", "background: on ? '#955851' : 'transparent'")
inq = inq.replace("border: '1px solid ' + (on ? '#ac746c'", "border: '1px solid ' + (on ? '#955851'")
write(inq_path, inq)

# 4) Petti Pathways case-study UI chrome: the existing teal is 4.05:1 against cream.
# This is an accessibility presentation variant, not a change to the documented brand swatches.
petti_path = 'our-work/petti-pathways/index.html'
petti = read(petti_path)
petti_count = petti.count('#35807e')
if petti_count < 1:
    raise SystemExit('Petti Pathways UI teal: expected #35807e occurrences')
petti = petti.replace('#35807e', '#2f7472')
write(petti_path, petti)

# 5) Join selector placeholder: the source uses an alpha espresso neutral which computes
# to the failing #8e8271 on paper. Replace the source expression, not the computed color.
join_path = 'join-our-team/index.html'
join = read(join_path)
join, c5 = require_replace(
    join,
    "programColor: p ? '#311d03' : 'rgba(49,29,3,.55)',",
    "programColor: p ? '#311d03' : '#7b7061',",
    'Join selector placeholder',
)
write(join_path, join)

# 6) Make intentionally scrollable project galleries/previews keyboard-focusable without
# changing their scrolling, reveal hooks, dimensions, or layout.
project_paths = {
    'our-work/luckys-cafe-bakery/index.html': 6,
    'our-work/petti-pathways/index.html': 3,
    'our-work/pizzeria-coco/index.html': 3,
    'our-work/folake/index.html': 2,
}

hpat = re.compile(r'<div(?![^>]*data-scroll-region)(?P<attrs>[^>]*)style="(?P<style>[^"]*overflow-x:auto[^"]*)">')
vpat = re.compile(r'<div(?![^>]*data-scroll-region)(?P<attrs>[^>]*)style="(?P<style>[^"]*max-height:[^"]*overflow-y:auto[^"]*)">')

for path, expected_min in project_paths.items():
    text = read(path)

    def hrepl(match):
        hrepl.count += 1
        attrs = match.group('attrs')
        style = match.group('style')
        return f'<div{attrs} data-scroll-region="project-gallery" tabindex="0" role="region" aria-label="Scrollable project gallery {hrepl.count}" style="{style}">'
    hrepl.count = 0

    def vrepl(match):
        vrepl.count += 1
        attrs = match.group('attrs')
        style = match.group('style')
        return f'<div{attrs} data-scroll-region="project-preview" tabindex="0" role="region" aria-label="Scrollable project preview {vrepl.count}" style="{style}">'
    vrepl.count = 0

    text = hpat.sub(hrepl, text)
    text = vpat.sub(vrepl, text)
    total = hrepl.count + vrepl.count
    if total < expected_min:
        raise SystemExit(f'{path}: expected at least {expected_min} scroll regions, updated {total}')
    write(path, text)

# 7) Source-level accessibility contrast layer for small utility rose text. Large decorative
# rose typography stays unchanged. Dark espresso surfaces use a lighter rose; light surfaces
# use a darker rose. The 404's small inherited rose labels are targeted explicitly.
css_path = 'assets/rendered-corrections.css'
css = read(css_path)
marker = '/* WCAG UTILITY CONTRAST FINAL · 2026-09-13 */'
if marker not in css:
    css += r'''

/* WCAG UTILITY CONTRAST FINAL · 2026-09-13 */
:root {
  --sc-rose-utility-light: #945650;
  --sc-rose-utility-dark: #c88f87;
}

/* Small rose utility text on cream/paper. Decorative display rose remains #ac746c. */
[style*="color:#ac746c"][style*="font-size:8px"],
[style*="color:#ac746c"][style*="font-size:9px"],
[style*="color:#ac746c"][style*="font-size:10px"],
[style*="color:#ac746c"][style*="font-size:11.5px"],
[data-inquiry-kicker],
[data-service-price] {
  color: var(--sc-rose-utility-light) !important;
}

/* The same small utilities on espresso need the lighter accessible rose. */
[style*="background:#311d03"] [style*="color:#ac746c"][style*="font-size:8px"],
[style*="background:#311d03"] [style*="color:#ac746c"][style*="font-size:9px"],
[style*="background:#311d03"] [style*="color:#ac746c"][style*="font-size:10px"],
[style*="background:#311d03"] [style*="color:#ac746c"][style*="font-size:11.5px"],
[style*="background: #311d03"] [style*="color:#ac746c"][style*="font-size:8px"],
[style*="background: #311d03"] [style*="color:#ac746c"][style*="font-size:9px"],
[style*="background: #311d03"] [style*="color:#ac746c"][style*="font-size:10px"],
[style*="background: #311d03"] [style*="color:#ac746c"][style*="font-size:11.5px"],
#results [style*="color:#ac746c"],
footer [style*="color:#ac746c"] {
  color: var(--sc-rose-utility-dark) !important;
}

/* 404 small inherited rose labels. Keep the large Pinyon 404 accent untouched. */
[data-screen-label="404"] p[style*="color:#ac746c"] > span:first-child,
[data-screen-label="404"] a span[style*="color:#ac746c"] {
  color: var(--sc-rose-utility-light) !important;
}

/* Keyboard focus for intentionally scrollable case-study regions. */
[data-scroll-region]:focus-visible {
  outline: 2px solid #945650 !important;
  outline-offset: 3px !important;
}
'''
write(css_path, css)

print('Applied remaining accessibility fixes')
print({
    'footer_labels': c1,
    'footer_tagline': c2,
    'open_sign': c3,
    'active_service': c4,
    'join_placeholder': c5,
    'petti_teal_occurrences': petti_count,
})
