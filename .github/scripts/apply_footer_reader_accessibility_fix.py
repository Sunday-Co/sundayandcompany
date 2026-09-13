from pathlib import Path

ROOT = Path('.')


def replace_exact(path: Path, old: str, new: str, expected=None):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if expected is not None and count != expected:
        raise SystemExit(f'{path}: expected {expected} occurrences, found {count}: {old[:80]!r}')
    if count == 0:
        raise SystemExit(f'{path}: replacement target missing: {old[:80]!r}')
    path.write_text(text.replace(old, new), encoding='utf-8')
    return count


# 1) Current workflow README. The old file still described a retired drag/drop + Wix launch path.
readme = ROOT / 'READ ME FIRST.md'
readme.write_text('''# Sunday & Company Website\n\n## Current production setup\n\nThis repository is the source of truth for `https://sundayandcompany.co`.\n\n- Production branch: `main`\n- Hosting: Netlify, connected to this GitHub repository\n- Publish directory: repository root (`.`)\n- Domain: `sundayandcompany.co`\n- `www` and HTTP redirect to the HTTPS bare domain through `netlify.toml`\n\nDo **not** drag a folder into Netlify for normal updates. Do **not** recreate the Netlify site or reconnect the domain.\n\n## Safe editing workflow\n\n1. Start from the current `main` branch.\n2. Make changes on a temporary/no-deploy branch when the change affects layout, forms, motion, Safari rendering, or shared components.\n3. Test mobile and desktop before production. For Safari-sensitive work, include WebKit/browser capture checks.\n4. Keep temporary QA scripts and workflows off `main`.\n5. Promote one clean production commit to `main` only after the candidate is verified.\n6. If CSS or JavaScript behavior changes, bump the asset query version used by the HTML so Safari does not reuse a stale cached file.\n\n## Files that should not be changed casually\n\n### `netlify.toml`\n\nThe current file already handles the production publish root, cache rules, and domain redirects. Visual/UI corrections normally do **not** require a `netlify.toml` change.\n\n### Shared site assets\n\n- `assets/site.css` contains the shared typography, responsive, modal, footer, Safari/capture, and accessibility-related production rules.\n- `assets/site.js` contains only shared runtime behavior that truly needs JavaScript.\n- `assets/rendered-corrections.css` is a production compatibility layer. Avoid stacking new one-off overrides when a source/component correction is possible.\n\n### Shared components\n\nThe root `Site Header.dc.html`, `Site Footer.dc.html`, `Inquiry Form.dc.html`, and `Program Cards.dc.html` are the canonical shared component sources. Keep generated/duplicate copies aligned when they are intentionally retained in the repository.\n\n## Forms\n\nForms submit through the existing Web3Forms integration. Do not replace the keys or form transport during visual changes. After a form-related production update, test a real submission and confirm delivery to `hello@sundayandcompany.co`.\n\n## Accessibility\n\nSafari **Reader** is a browser reading view, not the site's screen-reader implementation. It intentionally removes navigation, controls, and other non-article material and cannot be used as the requirement that every visual element appear in Reader.\n\nThe accessibility target for this site is semantic HTML, keyboard access, visible focus, meaningful image alt text, labelled controls, reduced-motion support, and compatibility with assistive technology such as Apple VoiceOver.\n\n## If production looks wrong\n\nFirst confirm that the live HTML is serving the newest asset query version. If it is still serving the previous version, do not create another visual patch just to force a redeploy. Wait for or diagnose the current Netlify deploy/cache state.\n\nFor a real regression, roll back to the last known-good GitHub/Netlify deploy, correct the source on a branch, retest, and then publish one clean commit.\n''', encoding='utf-8')


# 2) Shared CSS corrections.
css = ROOT / 'assets/site.css'
text = css.read_text(encoding='utf-8')

old_mobile_inquiry = '''  div[role="presentation"]:has(> [aria-label="Project inquiry"]) {\n    align-items: flex-start !important;\n    padding: 12px !important;\n    overflow-y: auto !important;\n  }\n  [aria-label="Project inquiry"] {\n    margin: 0 auto !important;\n    width: calc(100vw - 24px) !important;\n    max-width: calc(100vw - 24px) !important;\n    max-height: calc(100dvh - 24px) !important;\n    overflow-y: auto !important;\n  }'''
new_mobile_inquiry = '''  div[role="presentation"]:has(> [aria-label="Project inquiry"]) {\n    align-items: center !important;\n    justify-content: center !important;\n    padding: 18px 12px calc(18px + env(safe-area-inset-bottom)) !important;\n    overflow-y: auto !important;\n  }\n  [aria-label="Project inquiry"] {\n    margin: auto !important;\n    width: calc(100vw - 24px) !important;\n    max-width: calc(100vw - 24px) !important;\n    max-height: calc(100dvh - 36px) !important;\n    overflow-y: auto !important;\n  }'''
if text.count(old_mobile_inquiry) != 1:
    raise SystemExit(f'assets/site.css: mobile inquiry source block count = {text.count(old_mobile_inquiry)}')
text = text.replace(old_mobile_inquiry, new_mobile_inquiry)

old_email = '''footer a[href^="mailto:"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 13.25px !important;\n  font-weight: 300 !important;\n  letter-spacing: .005em !important;\n  line-height: 1.4 !important;\n  opacity: 1 !important;\n}'''
new_email = '''footer a[href^="mailto:"] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 13.25px !important;\n  font-weight: 400 !important;\n  letter-spacing: .005em !important;\n  line-height: 1.4 !important;\n  opacity: 1 !important;\n}'''
if text.count(old_email) != 1:
    raise SystemExit(f'assets/site.css: footer email source block count = {text.count(old_email)}')
text = text.replace(old_email, new_email)

footer_rules = '''\n/* Footer source alignment: secondary-font tagline, readable email, and real bottom breathing room. */\nfooter [data-footer-tagline] {\n  font-family: var(--sunday-sans) !important;\n  font-size: clamp(15px, 1.3vw, 18px) !important;\n  font-style: normal !important;\n  font-weight: 300 !important;\n  letter-spacing: .015em !important;\n  line-height: 1.2 !important;\n}\nfooter [data-footer-tagline] em {\n  font-family: var(--sunday-sans) !important;\n  font-style: italic !important;\n  font-weight: 300 !important;\n  letter-spacing: .015em !important;\n}\n\n@media (max-width: 700px) {\n  footer {\n    padding-bottom: calc(44px + env(safe-area-inset-bottom)) !important;\n  }\n  footer a[href^="mailto:"] {\n    font-size: 13.25px !important;\n    font-weight: 400 !important;\n  }\n}\n'''
marker = '/* Footer source alignment: secondary-font tagline, readable email, and real bottom breathing room. */'
if marker in text:
    raise SystemExit('assets/site.css: footer alignment rules already present')
# Insert immediately after the legal footer type rule, keeping footer rules together.
needle = '''footer [data-footer-legal] {\n  font-family: var(--sunday-sans) !important;\n  font-size: 9px !important;\n  font-weight: 400 !important;\n  letter-spacing: .10em !important;\n}\n'''
if text.count(needle) != 1:
    raise SystemExit(f'assets/site.css: legal footer anchor count = {text.count(needle)}')
text = text.replace(needle, needle + footer_rules)
css.write_text(text, encoding='utf-8')


# 3) Canonical and retained footer component copies: fix the source, not only computed CSS.
footer_files = list(ROOT.rglob('Site Footer.dc.html'))
if not footer_files:
    raise SystemExit('No Site Footer.dc.html files found')
for path in footer_files:
    t = path.read_text(encoding='utf-8')
    if 'hello@sundayandcompany.co' not in t:
        raise SystemExit(f'{path}: footer email missing')
    t2 = t.replace("font-size:13.25px;font-weight:300;letter-spacing:.02em", "font-size:13.25px;font-weight:400;letter-spacing:.02em")
    if t2 == t:
        raise SystemExit(f'{path}: expected footer email weight source not found')
    t = t2
    old_tag = '''<p style="align-self:end;font-size:clamp(17px,1.5vw,23px);font-weight:400;letter-spacing:-.04em;line-height:.95;grid-column:{{ fTagCol }};grid-row:{{ fTagRow }};justify-self:{{ fTagJustify }};margin-top:{{ fTagTop }};text-align:{{ fTagAlign }}">A Seat At <em style="color:#ac746c;font-weight:400">Our Table.</em></p>'''
    new_tag = '''<p data-footer-tagline style="align-self:end;font-family:'Inter Tight',sans-serif;font-size:clamp(15px,1.3vw,18px);font-weight:300;letter-spacing:.015em;line-height:1.2;grid-column:{{ fTagCol }};grid-row:{{ fTagRow }};justify-self:{{ fTagJustify }};margin-top:{{ fTagTop }};text-align:{{ fTagAlign }}">A Seat At <em style="color:#ac746c;font-family:'Inter Tight',sans-serif;font-style:italic;font-weight:300">Our Table.</em></p>'''
    if t.count(old_tag) != 1:
        raise SystemExit(f'{path}: expected footer tagline source count = {t.count(old_tag)}')
    t = t.replace(old_tag, new_tag)
    path.write_text(t, encoding='utf-8')


# 4) Cache-buster: every production HTML page and site.js fallback must request the new shared files.
html_files = [p for p in ROOT.rglob('*.html') if '.github' not in p.parts]
changed_versions = 0
for path in html_files:
    t = path.read_text(encoding='utf-8')
    nt = t.replace('20260913-12', '20260913-13')
    if nt != t:
        changed_versions += 1
        path.write_text(nt, encoding='utf-8')
if changed_versions < 10:
    raise SystemExit(f'Expected sitewide asset version replacements, changed only {changed_versions} HTML files')

site_js = ROOT / 'assets/site.js'
js = site_js.read_text(encoding='utf-8')
if js.count('20260913-12') != 1:
    raise SystemExit(f'assets/site.js: expected exactly one v12 fallback reference, found {js.count("20260913-12")}')
js = js.replace('20260913-12', '20260913-13')
site_js.write_text(js, encoding='utf-8')

print(f'Updated README, shared CSS, {len(footer_files)} footer component sources, {changed_versions} HTML asset references, and site.js fallback.')
