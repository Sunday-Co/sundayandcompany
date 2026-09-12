from pathlib import Path
import re

ROOT = Path('.')
CSS_PATH = ROOT / 'assets' / 'rendered-corrections.css'
css = CSS_PATH.read_text(encoding='utf-8')

# Remove the correction-layer OPEN-sign override. The homepage component already
# owns the approved IntersectionObserver-triggered sc-rock -> sc-sway and
# sc-warm -> sc-neon sequence. The !important override was bypassing that state
# and is why the original first-entry swing disappeared.
start_marker = '/* The OPEN sign keeps its original character, but now loops without a one-shot handoff. */'
end_marker = '/* SUNDAY ARCHIVE LIBRARY CARD MODALS */'
if start_marker in css:
    start = css.index(start_marker)
    end = css.index(end_marker, start)
    css = css[:start] + '/* OPEN sign motion is intentionally owned by the original homepage component. */\n\n' + css[end:]

fix_marker = '/* FINAL BOUNDED FIXES · SAFARI CAPTURE + ORIGINAL MOTION */'
if fix_marker in css:
    css = css[:css.index(fix_marker)].rstrip() + '\n'

css += r'''

/* FINAL BOUNDED FIXES · SAFARI CAPTURE + ORIGINAL MOTION */

/*
  Remove only motion introduced by the recent correction layers. The original
  component-owned interactions, sliders, flips, menu behavior, OPEN-sign swing,
  marquee, and page-specific approved interactions remain untouched.
*/
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
  animation:none !important;
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

/* Project Inquiry receipt: preserve the top hierarchy and restore bottom air. */
@media (min-width:701px) {
  [aria-label="Project inquiry"] > div {
    padding-bottom:42px !important;
  }
}
@media (max-width:700px) {
  [aria-label="Project inquiry"] > div {
    padding-bottom:44px !important;
  }
}

/* Sunday Reservation: desktop fine print stays secondary but must be readable. */
@media (min-width:701px) {
  [aria-label="The Sunday Reservation"] [data-res-fineprint] {
    font-size:8.5px !important;
    font-weight:300 !important;
    letter-spacing:.045em !important;
    line-height:1.45 !important;
  }
}

/* Safari renders this mail link optically lighter; match the footer body rhythm. */
footer a[href^="mailto:"] {
  font-family:var(--sc-sans) !important;
  font-size:12.5px !important;
  font-weight:400 !important;
  letter-spacing:.01em !important;
  line-height:1.4 !important;
  opacity:1 !important;
}

/*
  iPhone Safari Full Page/PDF capture can discard absolutely positioned hero
  imagery and defer lazy images. Keep actual image elements visible in the print
  and long-capture pipeline rather than relying on a brown background fallback.
*/
img {
  content-visibility:visible !important;
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
  html, body, #dc-root, #dc-root > .sc-host {
    height:auto !important;
    min-height:100% !important;
    overflow:visible !important;
  }
  img {
    content-visibility:visible !important;
    visibility:visible !important;
    -webkit-print-color-adjust:exact !important;
    print-color-adjust:exact !important;
  }
  section#top > img[style*="position:absolute"],
  section[data-screen-hero] > img[style*="position:absolute"],
  [data-sunday-grid-hero="true"] > img[data-sunday-hero-img="true"] {
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

/* Our Work: retain the larger Bill of Work without allowing it over the title. */
@media (min-width:1100px) {
  [data-screen-label^="Our Work"] #top > div {
    align-items:end !important;
    gap:clamp(32px,3vw,52px) !important;
    grid-template-columns:minmax(0,1fr) minmax(440px,500px) !important;
  }
  [data-screen-label^="Our Work"] #work-title {
    font-size:clamp(58px,5.8vw,94px) !important;
    max-width:100% !important;
  }
  [data-screen-label^="Our Work"] #work-title > span {
    font-size:.98em !important;
    margin-left:clamp(20px,3vw,48px) !important;
    max-width:100% !important;
    white-space:normal !important;
  }
  [data-work-receipt] {
    justify-self:end !important;
    max-width:500px !important;
    min-width:440px !important;
    width:100% !important;
  }
}
'''

CSS_PATH.write_text(css, encoding='utf-8')

# Static capture safety across the whole site. Do not rely only on runtime JS to
# turn lazy images eager because Safari Full Page/PDF capture can snapshot before
# that mutation is honored.
changed = 0
lazy_removed = 0
for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = text.replace('v=20260912-8', 'v=20260912-9')
    count = updated.count(' loading="lazy"')
    if count:
        updated = updated.replace(' loading="lazy"', '')
        lazy_removed += count
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

# Strict end-state markers.
final_css = CSS_PATH.read_text(encoding='utf-8')
required = [
    fix_marker,
    'padding-bottom:44px !important;',
    'font-size:8.5px !important;',
    'footer a[href^="mailto:"]',
    'font-size:12.5px !important;',
    'section#top > img[style*="position:absolute"]',
    'position:relative !important;',
    'grid-template-columns:minmax(0,1fr) minmax(440px,500px) !important;',
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

# No rendered HTML file may retain lazy image loading after this pass.
for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    if 'loading="lazy"' in path.read_text(encoding='utf-8'):
        raise SystemExit(f'Lazy image remained in {path}')

print(f'Applied bounded Safari/motion fixes, removed {lazy_removed} lazy image attributes, and bumped {changed} rendered HTML files to v9')
