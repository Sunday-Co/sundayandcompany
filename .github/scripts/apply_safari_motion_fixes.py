from pathlib import Path
import re

ROOT = Path('.')
CSS_PATH = ROOT / 'assets' / 'rendered-corrections.css'
SITE_CSS_PATH = ROOT / 'assets' / 'site.css'
SITE_JS_PATH = ROOT / 'assets' / 'site.js'

fix_marker = '/* FINAL SOURCE-ALIGNED REVISION · 2026-09-12 */'
legacy_markers = [
    '/* FINAL CONSOLIDATED REVISION · 2026-09-12 */',
    '/* FINAL BOUNDED FIXES · SAFARI CAPTURE + ORIGINAL MOTION */',
]

css = CSS_PATH.read_text(encoding='utf-8')
for marker in legacy_markers + [fix_marker]:
    if marker in css:
        css = css[:css.index(marker)].rstrip() + '\n'

css += r'''

/* FINAL SOURCE-ALIGNED REVISION · 2026-09-12 */

/* Remove only recent correction-layer entrance/reveal motion. */
form[data-inq] [data-step-panel],
[data-service-body],
[data-process-body],
aside[data-sheet-state="open"] nav > a,
aside[data-sheet-state="open"] [data-sheet-cta],
[data-reveal],
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

/* Keep original popup opening animation. */
[aria-label="Project inquiry"],
[aria-label="The Sunday Reservation"] {
  animation:sunday-modal-in 300ms cubic-bezier(.22,.75,.18,1) both;
}

/* OPEN sign: original warm-up + first swing, then continuous neon pulse and gentle sway. */
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

/* Project Inquiry hierarchy: rose Inter Tight eyebrow, Playfair headline, bottom air. */
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
  [aria-label="Project inquiry"] > div { padding-bottom:46px !important; }
}
@media (max-width:700px) {
  [aria-label="Project inquiry"] [data-inquiry-kicker],
  #inquiry [data-inquiry-kicker] {
    font-size:11px !important;
    letter-spacing:.115em !important;
    margin-bottom:3px !important;
  }
  [aria-label="Project inquiry"] > div { padding-bottom:48px !important; }
}

/* Sunday Reservation: secondary support copy, small but readable fine print. */
[aria-label="The Sunday Reservation"] h2 + p {
  font-family:var(--sc-sans) !important;
  font-weight:300 !important;
}
@media (min-width:701px) {
  [aria-label="The Sunday Reservation"] [data-res-fineprint] {
    font-size:9px !important;
    font-weight:300 !important;
    letter-spacing:.04em !important;
    line-height:1.45 !important;
    opacity:.78 !important;
  }
}
@media (max-width:700px) {
  [aria-label="The Sunday Reservation"] [data-res-fineprint] {
    font-size:7px !important;
    font-weight:300 !important;
    letter-spacing:.045em !important;
    line-height:1.4 !important;
    opacity:.76 !important;
  }
}

/* Footer email must visually match surrounding body copy. */
footer a[href^="mailto:"] {
  font-family:var(--sc-sans) !important;
  font-size:12.5px !important;
  font-weight:400 !important;
  letter-spacing:.01em !important;
  line-height:1.4 !important;
  opacity:1 !important;
}

/* Capture-safe hero images: actual img stays in normal layout, not runtime-only absolute positioning. */
img { content-visibility:visible !important; }
img[data-sunday-static-hero="true"] {
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
  img[data-sunday-static-hero="true"] {
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

/* Our Work: A Point Of View always one line on desktop. Keep the large Bill of Work. */
@media (min-width:900px) {
  [data-screen-label^="Our Work"] #work-title > span {
    display:block !important;
    max-width:none !important;
    white-space:nowrap !important;
  }
}
@media (min-width:900px) and (max-width:1379px) {
  [data-screen-label^="Our Work"] #top > div {
    align-items:start !important;
    gap:30px !important;
    grid-template-columns:1fr !important;
  }
  [data-work-receipt] {
    justify-self:end !important;
    margin-top:4px !important;
    max-width:520px !important;
    min-width:440px !important;
    width:100% !important;
  }
}
@media (min-width:1380px) {
  [data-screen-label^="Our Work"] #top > div {
    align-items:end !important;
    gap:clamp(24px,2vw,40px) !important;
    grid-template-columns:minmax(720px,1fr) minmax(440px,480px) !important;
  }
  [data-screen-label^="Our Work"] #work-title {
    font-size:clamp(58px,7vw,108px) !important;
    max-width:none !important;
    min-width:0 !important;
  }
  [data-screen-label^="Our Work"] #work-title > span {
    font-size:1.02em !important;
    margin-left:clamp(16px,2vw,34px) !important;
  }
  [data-work-receipt] {
    justify-self:end !important;
    max-width:480px !important;
    min-width:440px !important;
    width:100% !important;
  }
}
'''
CSS_PATH.write_text(css, encoding='utf-8')

# Align the shared source stylesheet with the final direction so the correction layer is not fighting old rules.
site_css = SITE_CSS_PATH.read_text(encoding='utf-8')
source_marker = '/* FINAL SOURCE ALIGNMENT · 2026-09-12 */'
if source_marker in site_css:
    site_css = site_css[:site_css.index(source_marker)].rstrip() + '\n'
site_css += r'''

/* FINAL SOURCE ALIGNMENT · 2026-09-12 */
[data-reveal],
.sc-reveal,
.sc-reveal.sc-in,
form[data-inq] [data-step-panel],
[data-service-body],
[data-process-body],
aside[data-sheet-state="open"] nav > a,
aside[data-sheet-state="open"] [data-sheet-cta] {
  animation:none !important;
  opacity:1 !important;
  transform:none !important;
  transition:none !important;
}
[aria-label="Project inquiry"] [data-inquiry-kicker],
#inquiry [data-inquiry-kicker] {
  color:var(--sunday-rose) !important;
  font-family:var(--sunday-sans) !important;
  font-size:11.5px !important;
  font-style:normal !important;
  font-weight:400 !important;
  letter-spacing:.12em !important;
  line-height:1.25 !important;
  margin:0 0 3px !important;
  text-transform:uppercase !important;
}
footer a[href^="mailto:"] { font-weight:400 !important; opacity:1 !important; }
@media (min-width:701px) {
  [aria-label="The Sunday Reservation"] [data-res-fineprint] { font-size:9px !important; }
}
@media (max-width:700px) {
  [aria-label="The Sunday Reservation"] [data-res-fineprint] { font-size:7px !important; }
}
'''
SITE_CSS_PATH.write_text(site_css, encoding='utf-8')


def align_header_source(path: Path):
    text = path.read_text(encoding='utf-8')
    original = text
    text = re.sub(
        r'<p data-inquiry-kicker style="[^"]*">A Seat At Our Table</p>',
        '<p data-inquiry-kicker style="color:#ac746c;font-family:\'Inter Tight\',sans-serif;font-size:11.5px;font-style:normal;font-weight:400;letter-spacing:.12em;line-height:1.25;margin:0 0 3px;text-transform:uppercase">A Seat At Our Table</p>',
        text,
    )
    text = text.replace(
        '<p style="font-size:11px;line-height:1.5;margin:13px auto 0;max-width:330px">Join our newsletter for thoughtful notes on branding, business and the work behind both.</p>',
        '<p style="font-family:\'Inter Tight\',sans-serif;font-size:11px;font-weight:300;line-height:1.5;margin:13px auto 0;max-width:330px">Join our newsletter for thoughtful notes on branding, business and the work behind both.</p>'
    )
    text = text.replace('data-res-fineprint style="font-family:\'Inter Tight\',sans-serif;font-size:6.5px;', 'data-res-fineprint style="font-family:\'Inter Tight\',sans-serif;font-size:9px;')
    if text != original:
        path.write_text(text, encoding='utf-8')


def align_footer_source(path: Path):
    text = path.read_text(encoding='utf-8')
    original = text
    text = text.replace(
        'href="mailto:hello@sundayandcompany.co" style="font-family:\'Inter Tight\',sans-serif;font-size:12.5px;font-weight:300;',
        'href="mailto:hello@sundayandcompany.co" style="font-family:\'Inter Tight\',sans-serif;font-size:12.5px;font-weight:400;'
    )
    if text != original:
        path.write_text(text, encoding='utf-8')


def align_services_source(path: Path):
    text = path.read_text(encoding='utf-8')
    original = text
    text = re.sub(
        r'<p data-inquiry-kicker style="[^"]*">A Seat At Our Table</p>',
        '<p data-inquiry-kicker style="color:#ac746c;font-family:\'Inter Tight\',sans-serif;font-size:11.5px;font-style:normal;font-weight:400;letter-spacing:.12em;line-height:1.25;margin:0 0 3px;text-transform:uppercase">A Seat At Our Table</p>',
        text,
    )
    if text != original:
        path.write_text(text, encoding='utf-8')


def remove_work_reveal_runtime(path: Path):
    text = path.read_text(encoding='utf-8')
    original = text
    block = re.compile(
        r"\n    const nodes = Array\.from\(document\.querySelectorAll\('\[data-reveal\]'\)\);.*?\n    this\._io = io;",
        re.DOTALL,
    )
    text = block.sub('', text)
    cleanup = re.compile(
        r"\n    if \(this\._io\) this\._io\.disconnect\(\);.*?window\.removeEventListener\('hashchange', this\._sweep\);\n    \}",
        re.DOTALL,
    )
    text = cleanup.sub('', text)
    if text != original:
        path.write_text(text, encoding='utf-8')


align_header_source(ROOT / 'Site Header.dc.html')
align_footer_source(ROOT / 'Site Footer.dc.html')
align_services_source(ROOT / 'services' / 'index.html')
remove_work_reveal_runtime(ROOT / 'our-work' / 'index.html')


def normalize_static_hero_markup(text: str) -> tuple[str, int]:
    total = 0
    # Repair the malformed marker produced by the previous transform.
    text = re.sub(r'\s*/\s*data-sunday-static-hero="true">', ' data-sunday-static-hero="true" />', text)

    section_pattern = re.compile(
        r'(<section\b[^>]*(?:data-screen-hero|id="top")[^>]*>)(.*?)(</section>)',
        re.IGNORECASE | re.DOTALL,
    )

    def section_repl(match):
        nonlocal total
        opening, body, closing = match.groups()
        img_pattern = re.compile(r'<img\b([^>]*style="[^"]*(?:position:absolute|position:relative)[^"]*"[^>]*)/?>', re.IGNORECASE)
        img_match = img_pattern.search(body)
        if not img_match:
            return match.group(0)
        tag = img_match.group(0)
        attrs = tag[4:].rstrip('>').rstrip('/').rstrip()
        if 'data-sunday-static-hero=' not in attrs:
            attrs += ' data-sunday-static-hero="true"'
        attrs = attrs.replace('position:absolute', 'position:relative')
        marked = '<img ' + attrs + ' />'
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
    updated = text.replace('v=20260912-9', 'v=20260912-10').replace('v=20260912-8', 'v=20260912-10')
    count = updated.count(' loading="lazy"')
    if count:
        updated = updated.replace(' loading="lazy"', '')
        lazy_removed += count
    updated, marks = normalize_static_hero_markup(updated)
    hero_marked += marks
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

site_js = SITE_JS_PATH.read_text(encoding='utf-8').replace('v=20260912-9', 'v=20260912-10').replace('v=20260912-8', 'v=20260912-10')
SITE_JS_PATH.write_text(site_js, encoding='utf-8')

# Hard source-truth validation.
final_css = CSS_PATH.read_text(encoding='utf-8')
for marker in [
    fix_marker,
    '[data-reveal]',
    'font-family:var(--sc-sans) !important;',
    'padding-bottom:48px !important;',
    'font-size:9px !important;',
    'font-weight:400 !important;',
    'white-space:nowrap !important;',
    'grid-template-columns:minmax(720px,1fr) minmax(440px,480px) !important;',
]:
    if marker not in final_css:
        raise SystemExit(f'Missing final CSS marker: {marker}')

header = (ROOT / 'Site Header.dc.html').read_text(encoding='utf-8')
if "data-inquiry-kicker style=\"color:#ac746c;font-family:'Inter Tight'" not in header:
    raise SystemExit('Header inquiry kicker source is not Inter Tight')
if 'data-res-fineprint style="font-family:\'Inter Tight\',sans-serif;font-size:9px;' not in header:
    raise SystemExit('Reservation fine print source is not desktop-readable')

footer = (ROOT / 'Site Footer.dc.html').read_text(encoding='utf-8')
if 'mailto:hello@sundayandcompany.co" style="font-family:\'Inter Tight\',sans-serif;font-size:12.5px;font-weight:400;' not in footer:
    raise SystemExit('Footer email source weight is not 400')

work = (ROOT / 'our-work' / 'index.html').read_text(encoding='utf-8')
if "querySelectorAll('[data-reveal]')" in work:
    raise SystemExit('Our Work reveal runtime still exists')

home = (ROOT / 'index.html').read_text(encoding='utf-8')
if 'v=20260912-10' not in home:
    raise SystemExit('Homepage asset version did not bump to v10')
if re.search(r'/\s+data-sunday-static-hero=', home):
    raise SystemExit('Malformed static hero marker still exists')
if 'data-sunday-static-hero="true"' not in home or 'position:relative' not in home:
    raise SystemExit('Homepage hero is not source-level capture safe')

for path in sorted(ROOT.rglob('*.html')):
    if '.github' in path.parts or 'node_modules' in path.parts:
        continue
    txt = path.read_text(encoding='utf-8')
    if 'loading="lazy"' in txt:
        raise SystemExit(f'Lazy image remained in {path}')
    if re.search(r'/\s+data-sunday-static-hero=', txt):
        raise SystemExit(f'Malformed static hero marker remained in {path}')

print(f'Applied source-aligned revision, removed {lazy_removed} lazy attributes, normalized {hero_marked} hero images, and updated {changed} HTML files to v10')
