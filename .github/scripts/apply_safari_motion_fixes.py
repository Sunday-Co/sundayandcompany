from pathlib import Path

ROOT = Path('.')
CSS_PATH = ROOT / 'assets' / 'rendered-corrections.css'
css = CSS_PATH.read_text(encoding='utf-8')

# Remove the correction-layer OPEN-sign override. The homepage component already
# owns the approved IntersectionObserver-triggered sc-rock -> sc-sway and
# sc-warm -> sc-neon sequence. The !important override was bypassing that state.
start_marker = '/* The OPEN sign keeps its original character, but now loops without a one-shot handoff. */'
end_marker = '/* SUNDAY ARCHIVE LIBRARY CARD MODALS */'
if start_marker in css:
    start = css.index(start_marker)
    end = css.index(end_marker, start)
    css = css[:start] + '/* OPEN sign motion is intentionally owned by the original homepage component. */\n\n' + css[end:]

fix_marker = '/* FINAL BOUNDED FIXES · SAFARI CAPTURE + ORIGINAL MOTION */'
if fix_marker not in css:
    css += r'''

/* FINAL BOUNDED FIXES · SAFARI CAPTURE + ORIGINAL MOTION */

/* Remove only correction-layer motion. Original component interactions remain. */
[aria-label="Project inquiry"],
[aria-label="The Sunday Reservation"],
form[data-inq] [data-step-panel],
[data-service-body],
[data-process-body],
aside[data-sheet-state="open"] nav > a,
aside[data-sheet-state="open"] [data-sheet-cta] {
  animation:none !important;
}

.sc-reveal,
.sc-reveal.sc-in,
.sc-reveal h1 [style*="Pinyon Script"],
.sc-reveal h2 [style*="Pinyon Script"],
.sc-reveal h3 [style*="Pinyon Script"],
.sc-reveal.sc-in h1 [style*="Pinyon Script"],
.sc-reveal.sc-in h2 [style*="Pinyon Script"],
.sc-reveal.sc-in h3 [style*="Pinyon Script"] {
  opacity:1 !important;
  transform:none !important;
  transition:none !important;
}

[data-sheet-cta] svg,
[data-about-team-cta] svg,
button[onClick*="openInquiry"] svg,
a[href="/contact"] svg,
a[href="#inquiry"] svg {
  transform:none !important;
  transition:none !important;
}

/* Receipt breathing room requested for the Project Inquiry modal. */
@media (min-width:701px) {
  [aria-label="Project inquiry"] > div {
    padding-bottom:40px !important;
  }
}
@media (max-width:700px) {
  [aria-label="Project inquiry"] > div {
    padding-bottom:40px !important;
  }
}

/* Safari renders the mail link optically lighter than the surrounding footer copy. */
footer a[href^="mailto:"] {
  font-size:12.5px !important;
  font-weight:400 !important;
  letter-spacing:.01em !important;
  line-height:1.4 !important;
  opacity:1 !important;
}

/*
  iPhone Safari Full Page/PDF capture can discard an absolutely positioned hero
  image even though the live viewport shows it. Make every direct full-bleed
  hero <img> a real in-flow image in source CSS, not a JS-only capture repair.
*/
[data-sunday-grid-hero="true"] {
  display:block !important;
  position:relative !important;
}
section#top > img[style*="position:absolute"],
section[data-screen-hero] > img[style*="position:absolute"],
[data-sunday-grid-hero="true"] > img[data-sunday-hero-img="true"] {
  content-visibility:visible !important;
  display:block !important;
  height:100% !important;
  inset:auto !important;
  min-height:100% !important;
  object-fit:cover !important;
  opacity:1 !important;
  position:relative !important;
  visibility:visible !important;
  width:100% !important;
  z-index:0 !important;
  -webkit-print-color-adjust:exact !important;
  print-color-adjust:exact !important;
}

@media print {
  section#top > img[style*="position:absolute"],
  section[data-screen-hero] > img[style*="position:absolute"],
  [data-sunday-grid-hero="true"] > img[data-sunday-hero-img="true"] {
    content-visibility:visible !important;
    display:block !important;
    height:100% !important;
    inset:auto !important;
    min-height:100% !important;
    object-fit:cover !important;
    opacity:1 !important;
    position:relative !important;
    visibility:visible !important;
    width:100% !important;
  }
}
'''

CSS_PATH.write_text(css, encoding='utf-8')

# Cache-bust the bounded correction batch on every rendered route.
changed = 0
for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = text.replace('v=20260912-8', 'v=20260912-9')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

# Strict end-state markers.
final_css = CSS_PATH.read_text(encoding='utf-8')
required = [
    fix_marker,
    'padding-bottom:40px !important;',
    'footer a[href^="mailto:"]',
    'font-weight:400 !important;',
    'section#top > img[style*="position:absolute"]',
    'position:relative !important;',
    '[aria-label="Project inquiry"],',
    'animation:none !important;',
]
for marker in required:
    if marker not in final_css:
        raise SystemExit(f'Missing final CSS marker: {marker}')

for forbidden in ['sc-sway-sunday-continuous', 'The OPEN sign keeps its original character, but now loops']:
    if forbidden in final_css:
        raise SystemExit(f'OPEN sign override still present: {forbidden}')

home = Path('index.html').read_text(encoding='utf-8')
for marker in ['sc-rock 5.4s', 'sc-sway 7s', 'sc-warm 2.6s', 'sc-neon 3.8s', 'IntersectionObserver']:
    if marker not in home:
        raise SystemExit(f'Original OPEN sign behavior missing from homepage: {marker}')

print(f'Applied Safari/motion corrections and bumped {changed} rendered HTML files to v9')
