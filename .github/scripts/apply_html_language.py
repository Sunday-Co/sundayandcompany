from pathlib import Path
import re

# One-time no-deploy source patch for the document language declaration.
pages = [
    p for p in Path('.').rglob('*.html')
    if '.github' not in p.parts and not p.name.endswith('.dc.html')
]
if not pages:
    raise SystemExit('No public HTML pages found')

changed = 0
verified = 0
for path in pages:
    text = path.read_text(encoding='utf-8')
    matches = list(re.finditer(r'<html\b[^>]*>', text, flags=re.I))
    if len(matches) != 1:
        raise SystemExit(f'{path}: expected exactly one <html> element, found {len(matches)}')

    tag = matches[0].group(0)
    if re.search(r'\blang\s*=', tag, flags=re.I):
        verified += 1
        continue

    new_tag = re.sub(r'^<html\b', '<html lang="en"', tag, count=1, flags=re.I)
    text = text[:matches[0].start()] + new_tag + text[matches[0].end():]
    path.write_text(text, encoding='utf-8')
    changed += 1

for path in pages:
    text = path.read_text(encoding='utf-8')
    tag = re.search(r'<html\b[^>]*>', text, flags=re.I)
    if not tag or not re.search(r'\blang\s*=\s*["\']en["\']', tag.group(0), flags=re.I):
        raise SystemExit(f'{path}: English page language declaration missing after patch')

print(f'Added lang="en" to {changed} public HTML pages; {verified} already had a language declaration. Verified {len(pages)} total pages.')
