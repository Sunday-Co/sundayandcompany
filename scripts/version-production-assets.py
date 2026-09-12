from pathlib import Path

ROOT = Path('.')
VERSION = '20260912-2'
changed = []

for path in ROOT.rglob('*.html'):
    if any(part in {'.git', 'node_modules'} for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8')
    new = text
    new = new.replace('/assets/site.css?v=20260912-1', f'/assets/site.css?v={VERSION}')
    new = new.replace('/assets/site.js?v=20260912-1', f'/assets/site.js?v={VERSION}')
    new = new.replace('/assets/site.css"', f'/assets/site.css?v={VERSION}"')
    new = new.replace('/assets/site.js"', f'/assets/site.js?v={VERSION}"')
    if new != text:
        path.write_text(new, encoding='utf-8')
        changed.append(str(path))

print(f'Updated {len(changed)} HTML files')
for p in changed:
    print(p)
