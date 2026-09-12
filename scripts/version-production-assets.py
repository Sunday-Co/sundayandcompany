from pathlib import Path

ROOT = Path('.')
VERSION = '20260912-3'
changed = []

for path in ROOT.rglob('*.html'):
    if any(part in {'.git', 'node_modules'} for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8')
    new = text
    for old in ('20260912-1', '20260912-2'):
        new = new.replace(f'/assets/site.css?v={old}', f'/assets/site.css?v={VERSION}')
        new = new.replace(f'/assets/site.js?v={old}', f'/assets/site.js?v={VERSION}')
    new = new.replace('/assets/site.css"', f'/assets/site.css?v={VERSION}"')
    new = new.replace('/assets/site.js"', f'/assets/site.js?v={VERSION}"')
    if new != text:
        path.write_text(new, encoding='utf-8')
        changed.append(str(path))

# The previous reveal system deliberately excluded #top for screenshot safety.
# The screenshot issue is now solved through root sizing and closed-drawer
# handling, so include the hero in the real entrance motion. Because the JS
# only animates once a section is intersecting, this does not leave an unseen
# hero or hidden content in full-page captures.
site_js = ROOT / 'assets' / 'site.js'
js = site_js.read_text(encoding='utf-8')
old_filter = "return node.id !== 'top' && !node.closest('[role=\"dialog\"]') && node.offsetHeight > 80;"
new_filter = "return !node.closest('[role=\"dialog\"]') && node.offsetHeight > 80;"
if old_filter in js:
    site_js.write_text(js.replace(old_filter, new_filter), encoding='utf-8')
    changed.append(str(site_js))

print(f'Updated {len(changed)} production files')
for p in changed:
    print(p)
