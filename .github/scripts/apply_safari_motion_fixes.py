from pathlib import Path
import re

ROOT = Path('.')
CSS_PATH = ROOT / 'assets' / 'rendered-corrections.css'
css = CSS_PATH.read_text(encoding='utf-8')

start_marker = '/* The OPEN sign keeps its original character, but now loops without a one-shot handoff. */'
end_marker = '/* SUNDAY ARCHIVE LIBRARY CARD MODALS */'
if start_marker in css:
    start = css.index(start_marker)
    end = css.index(end_marker, start)
    css = css[:start] + '/* OPEN sign motion uses the original homepage sequence. */\n\n' + css[end:]

fix_marker = '/* FINAL CONSOLIDATED REVISION · 2026-09-12 */'
old_fix_marker = '/* FINAL BOUNDED FIXES · SAFARI CAPTURE + ORIGINAL MOTION */'
for marker in (fix_marker, old_fix_marker):
    if marker in css:
        css = css[:css.index(marker)].rstrip() + '\n'

css += r'''

/* FINAL CONSOLIDATED REVISION · 2026-09-12 */

/* Remove only the recent correction-layer motion. Original component motion stays. */
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

/* Reuse the exact original OPEN warm-up, damped swing, neon loop and slow sway.
   The state sits on html so a component rerender cannot erase it. */
html[data-sunday-sign-fallback="0"] [data-sign] p[aria-hidden][style*="Pinyon Script"],
html[data-sunday-sign-fallback="0"] [data-sign] > div[style*="transform-origin"] {
  animation:none !important;
}
html[data-sunday-sign-fallback="1"] [data-sign] p[aria-hidden][style*="Pinyon Script"] {
  animation:sc-warm 2.6s ease-out 1 both, sc-neon 3.8s ease-in-out 2.6s infinite !important;
}
html[data-sunday-sign-fallback="1"] [data-sign] > div[style*="transform-origin"] {
  animation:sc-rock 5.4s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 7s ease-in-out 5.4s infinite !important;
}

/* Project Inquiry: rose Inter Tight eyebrow, Playfair headline, more bottom air. */
[aria-label="Project inquiry"] [data-inquiry-kicker],
#inquiry [data-inquiry-kicker] {
  color:var(--sc-rose) !important;
  font-family:var(--sc-sans) !important;
  font-size:11.5px !important;
  font-style:normal !important;
  font-weight:400 !important;
  letter-spacing:.12em !important;
  line-height:1.25 !important;
  margin:0 0 3px 0 !important;
  text-transform:uppercase !important;
}
[aria-label="Project inquiry"] [data-inquiry-kicker] + h2,
#inquiry [data-inquiry-kicker] + h2 {
  color:var(--sc-espresso) !important;
  font-family:var(--sc-serif) !important;
  font-weight:400 !important;
  margin-top:0 !important;
}
@media (min-width:701px) {
  [aria-label="Project inquiry"] > div { padding-bottom:42px !important; }
}
@media (max-width:700px) {
  [aria-label="Project inquiry"] [data-inquiry-kicker],
  #inquiry [data-inquiry-kicker] {
    font-size:11px !important;
    letter-spacing:.115em !important;
    margin-bottom:3px !important;
  }
  [aria-label="Project inquiry"] > div { padding-bottom:44px !important; }
}

/* Sunday Reservation: receipt hierarchy with readable fine print by viewport. */
@media (min-width:701px) {
  [aria-label="The Sunday Reservation"] [data-res-fineprint] {
    font-size:9px !important;
    font-weight:300 !important;
    letter-spacing:.04em !important;
    line-height:1.45 !important;
  }
}
@media (max-width:700px) {
  [aria-label="The Sunday Reservation"] [data-res-fineprint] {
    font-size:7px !important;
    font-weight:300 !important;
    letter-spacing:.045em !important;
    line-height:1.4 !important;
  }
}

/* Match the footer mail link to the visual weight of the surrounding body copy. */
footer a[href^="mailto:"] {
  font-family:var(--sc-sans) !important;
  font-size:12.5px !important;
  font-weight:400 !important;
  letter-spacing:.01em !important;
  line-height:1.4 !important;
  opacity:1 !important;
}

/* Static Safari Full Page/PDF capture safeguards. */
img { content-visibility:visible !important; }
img[data-sunday-static-hero="true"],
section#top > img[style*="position:absolute"],
section[data-screen-hero] > img[style*="position:absolute"] {
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
  img[data-sunday-static-hero="true"],
  section#top > img[style*="position:absolute"],
  section[data-screen-hero] > img[style*="position:absolute"] {
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

/* Our Work: keep the large Bill of Work, but give the headline its own column. */
@media (min-width:1100px) {
  [data-screen-label^="Our Work"] #top > div {
    align-items:end !important;
    gap:clamp(40px,4vw,64px) !important;
    grid-template-columns:minmax(0,1fr) minmax(440px,500px) !important;
  }
  [data-screen-label^="Our Work"] #work-title {
    font-size:clamp(58px,7vw,108px) !important;
    max-width:100% !important;
    min-width:0 !important;
  }
  [data-screen-label^="Our Work"] #work-title > span {
    font-size:1.02em !important;
    margin-left:clamp(16px,2vw,34px) !important;
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


def mark_static_hero_images(text: str) -> tuple[str, int]:
    total = 0
    section_pattern = re.compile(
        r'(<section\b[^>]*(?:data-screen-hero|id="top")[^>]*>)(.*?)(</section>)',
        re.IGNORECASE | re.DOTALL,
    )

    def section_repl(match):
        nonlocal total
        opening, body, closing = match.groups()
        img_pattern = re.compile(r'<img\b([^>]*style="[^"]*position:absolute[^"]*"[^>]*)>', re.IGNORECASE)
        img_match = img_pattern.search(body)
        if not img_match:
            return match.group(0)
        tag = img_match.group(0)
        if 'data-sunday-static-hero=' in tag:
            return match.group(0)
        marked = tag[:-1] + ' data-sunday-static-hero="true">'
        body = body[:img_match.start()] + marked + body[img_match.end():]
        total += 1
        return opening + body + closing

    return section_pattern.sub(section_repl, text), total


changed = 0
lazy_removed = 0
hero_marked = 0
for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = text.replace('v=20260912-8', 'v=20260912-9')
    count = updated.count(' loading="lazy"')
    if count:
        updated = updated.replace(' loading="lazy"', '')
        lazy_removed += count
    updated, marks = mark_static_hero_images(updated)
    hero_marked += marks
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

final_css = CSS_PATH.read_text(encoding='utf-8')
required = [
    fix_marker,
    'html[data-sunday-sign-fallback="1"]',
    'sc-rock 5.4s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 7s ease-in-out 5.4s infinite',
    'font-family:var(--sc-sans) !important;',
    'padding-bottom:44px !important;',
    'font-size:9px !important;',
    'footer a[href^="mailto:"]',
    'font-size:12.5px !important;',
    'img[data-sunday-static-hero="true"]',
    'position:relative !important;',
    'grid-template-columns:minmax(0,1fr) minmax(440px,500px) !important;',
    'font-size:clamp(58px,7vw,108px) !important;',
]
for marker in required:
    if marker not in final_css:
        raise SystemExit(f'Missing final CSS marker: {marker}')

if re.search(r'\[aria-label="Project inquiry"\]\s*,\s*\n\[aria-label="The Sunday Reservation"\]\s*\{\s*animation:none', final_css):
    raise SystemExit('Original modal opening animation was accidentally disabled')

for forbidden in ['sc-sway-sunday-continuous', 'sc-neon-sunday-final', 'The OPEN sign keeps its original character, but now loops']:
    if forbidden in final_css:
        raise SystemExit(f'OPEN sign correction override still present: {forbidden}')

home = Path('index.html').read_text(encoding='utf-8')
for marker in ['sc-rock 5.4s', 'sc-sway 7s', 'sc-warm 2.6s', 'sc-neon 3.8s', 'IntersectionObserver']:
    if marker not in home:
        raise SystemExit(f'Original OPEN sign behavior missing from homepage: {marker}')
if 'data-sunday-static-hero="true"' not in home:
    raise SystemExit('Homepage hero was not statically marked for capture')

for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    if 'loading="lazy"' in path.read_text(encoding='utf-8'):
        raise SystemExit(f'Lazy image remained in {path}')

if hero_marked < 1:
    raise SystemExit('No static hero image markers were written')

print(
    f'Applied consolidated revision, removed {lazy_removed} lazy image attributes, '
    f'marked {hero_marked} static hero images, and updated {changed} rendered HTML files to v9'
)
