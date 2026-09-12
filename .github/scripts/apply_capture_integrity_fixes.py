from pathlib import Path
import re
import shutil

ROOT = Path('.')
CSS_FILES = [ROOT / 'assets' / 'site.css', ROOT / 'assets' / 'rendered-corrections.css']

# 1. Footer body copy must be identical, including the email.
# The requested hierarchy is body copy at 12.5px / 300. Labels/legal keep their own rules.
for css_path in CSS_FILES:
    css = css_path.read_text(encoding='utf-8')
    marker = '/* CAPTURE INTEGRITY + FOOTER NORMALIZATION · 2026-09-12 */'
    if marker in css:
        css = css[:css.index(marker)].rstrip() + '\n'
    css += r'''

/* CAPTURE INTEGRITY + FOOTER NORMALIZATION · 2026-09-12 */
footer [data-footer-ui],
footer [data-footer-location],
footer a[href^="mailto:"],
footer a[href*="instagram.com/sundayand_co"] {
  font-family:'Inter Tight',Arial,sans-serif !important;
  font-size:12.5px !important;
  font-weight:300 !important;
  letter-spacing:.01em !important;
  line-height:1.4 !important;
  opacity:1 !important;
}

/* Keep horizontal containment at the true document roots. Do not put any
   overflow axis on the page shell itself: in WebKit/CSS, hidden on one axis
   makes visible on the other axis compute to auto, creating a nested scroller. */
html, body, #dc-root, #dc-root > .sc-host {
  max-width:100% !important;
  overflow-x:hidden !important;
}
[data-screen-label] {
  max-width:100% !important;
  overflow:visible !important;
}

/* Long portfolio screenshots must participate in the outer document instead of
   living inside their own vertical scrollports. This is required for true full-page capture. */
[data-capture-full-image] {
  max-height:none !important;
  overflow:visible !important;
  height:auto !important;
}
[data-capture-full-image] > img {
  display:block !important;
  height:auto !important;
  max-height:none !important;
  width:100% !important;
}

/* Keep actual imagery in the document paint tree for WebKit snapshot/PDF capture. */
img {
  content-visibility:visible !important;
  image-rendering:auto;
}
img[data-sunday-static-hero="true"] {
  backface-visibility:visible !important;
  -webkit-backface-visibility:visible !important;
  transform:none !important;
  will-change:auto !important;
}

@media print {
  html, body, #dc-root, #dc-root > .sc-host,
  [data-screen-label] {
    height:auto !important;
    max-height:none !important;
    overflow:visible !important;
  }
  header { position:absolute !important; }
  [data-capture-full-image] {
    max-height:none !important;
    overflow:visible !important;
    break-inside:avoid !important;
  }
  img, video {
    content-visibility:visible !important;
    opacity:1 !important;
    visibility:visible !important;
    -webkit-print-color-adjust:exact !important;
    print-color-adjust:exact !important;
  }
}
'''
    css_path.write_text(css, encoding='utf-8')

# 2. Fix the shared footer source itself, then replicate the shared components to every
# exported route copy so a route can never resolve an older Header/Footer component.
footer_path = ROOT / 'Site Footer.dc.html'
footer = footer_path.read_text(encoding='utf-8')
footer = re.sub(
    r'(data-footer-ui href="mailto:hello@sundayandcompany\.co" style="[^"]*font-size:)12\.5px(;font-weight:)400',
    r'\g<1>12.5px\g<2>300',
    footer,
)
footer = re.sub(
    r'(data-footer-ui href="mailto:hello@sundayandcompany\.co" style="[^"]*font-size:)12\.5px(;font-weight:)300',
    r'\g<1>12.5px\g<2>300',
    footer,
)
footer_path.write_text(footer, encoding='utf-8')

root_header = ROOT / 'Site Header.dc.html'
for component_name, source in [('Site Header.dc.html', root_header), ('Site Footer.dc.html', footer_path)]:
    source_text = source.read_text(encoding='utf-8')
    for target in ROOT.rglob(component_name):
        if target == source or '.github' in target.parts or 'node_modules' in target.parts:
            continue
        target.write_text(source_text, encoding='utf-8')

# 3. Remove capture-hostile overflow from document/page shells. Horizontal containment
# stays on html/body/root hosts only, so the screen wrapper never becomes an inner scroller.
def normalize_shell_overflow(text: str) -> str:
    text = text.replace('overflow-x: clip;', 'overflow-x: hidden;')
    text = text.replace('overflow-x:clip;', 'overflow-x:hidden;')

    # Exported top-level screen wrappers all carry data-screen-label.
    pattern = re.compile(r'(<div\s+data-screen-label="[^"]+"\s+style=")([^"]*)(")', re.I)
    def repl(m):
        style = m.group(2)
        style = re.sub(r'(^|;)\s*overflow\s*:\s*(?:clip|hidden|auto|scroll)\s*;?', r'\1overflow:visible;', style, flags=re.I)
        style = re.sub(r'(^|;)\s*overflow-x\s*:\s*(?:clip|hidden|auto|scroll)\s*;?', r'\1overflow-x:visible;', style, flags=re.I)
        style = re.sub(r'(^|;)\s*overflow-y\s*:\s*(?:clip|hidden|auto|scroll)\s*;?', r'\1overflow-y:visible;', style, flags=re.I)
        return m.group(1) + style + m.group(3)
    return pattern.sub(repl, text)

# 4. Long screenshot/image viewers cannot be inner vertical scrollports if the outer page
# needs to capture the complete image. Mark and expand only divs that directly wrap an img.
def expand_vertical_image_viewers(text: str) -> tuple[str, int]:
    count = 0
    pattern = re.compile(r'<div\s+style="([^"]*(?:max-height:[^;"]+;)?[^\"]*overflow-y:auto[^\"]*)">\s*(<img\b)', re.I)
    def repl(m):
        nonlocal count
        style = m.group(1)
        style = re.sub(r'max-height:[^;\"]+;?', '', style)
        style = style.replace('overflow-y:auto', 'overflow:visible')
        if 'height:' not in style:
            style += ';height:auto'
        count += 1
        return '<div data-capture-full-image="true" style="' + style.strip(';') + '">' + m.group(2)
    return pattern.sub(repl, text), count

changed = 0
expanded = 0
for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = normalize_shell_overflow(text)
    updated, n = expand_vertical_image_viewers(updated)
    expanded += n
    # Use the capture-sized Capitol image once it has been generated.
    updated = updated.replace('/assets/gallery-capitol.jpeg', '/assets/opt/gallery-capitol.jpg')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

# 5. Bump cache keys exactly once for this candidate.
for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = text.replace('v=20260912-10', 'v=20260912-11')
    if updated != text:
        path.write_text(updated, encoding='utf-8')

site_js = ROOT / 'assets' / 'site.js'
js = site_js.read_text(encoding='utf-8').replace('v=20260912-10', 'v=20260912-11')
site_js.write_text(js, encoding='utf-8')

# Required invariants.
root_footer_text = footer_path.read_text(encoding='utf-8')
root_header_text = root_header.read_text(encoding='utf-8')
for target in ROOT.rglob('Site Footer.dc.html'):
    if '.github' not in target.parts and 'node_modules' not in target.parts:
        if target.read_text(encoding='utf-8') != root_footer_text:
            raise SystemExit(f'Stale footer copy remains: {target}')
for target in ROOT.rglob('Site Header.dc.html'):
    if '.github' not in target.parts and 'node_modules' not in target.parts:
        if target.read_text(encoding='utf-8') != root_header_text:
            raise SystemExit(f'Stale header copy remains: {target}')

for path in ROOT.rglob('*.html'):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if 'overflow-x: clip' in text or 'overflow-x:clip' in text:
        raise SystemExit(f'overflow-x:clip remains in {path}')
    if re.search(r'<div\s+style="[^"]*overflow-y:auto[^"]*">\s*<img\b', text, re.I):
        raise SystemExit(f'Nested vertical image scrollport remains in {path}')
    for m in re.finditer(r'<div\s+data-screen-label="[^"]+"\s+style="([^"]*)"', text, re.I):
        if re.search(r'overflow(?:-x|-y)?\s*:\s*(?:clip|hidden|auto|scroll)', m.group(1), re.I):
            raise SystemExit(f'Page shell still has capture-hostile overflow in {path}: {m.group(1)}')

if expanded < 10:
    raise SystemExit(f'Expected to expand at least 10 long-image viewers, expanded only {expanded}')
if '/assets/opt/gallery-capitol.jpg' not in (ROOT / 'index.html').read_text(encoding='utf-8'):
    raise SystemExit('Homepage is not pointed at optimized Capitol image')

print(f'Capture integrity fixes applied: {changed} HTML files changed, {expanded} inner vertical image viewers expanded, shared Header/Footer copies synchronized, v11 cache key set.')
