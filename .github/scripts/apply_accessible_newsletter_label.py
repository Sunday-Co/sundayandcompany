from pathlib import Path

# One-time no-deploy source patch for the newsletter field's accessible name.
# Rerun after correcting the workflow staging pathspec.
files = list(Path('.').rglob('Site Footer.dc.html'))
if not files:
    raise SystemExit('No Site Footer.dc.html files found')

old = '<input autocomplete="email" name="email" placeholder="Email Address" required="required" type="email" maxlength="120"'
new = '<input aria-label="Email address" autocomplete="email" name="email" placeholder="Email Address" required="required" type="email" maxlength="120"'

changed = 0
for path in files:
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one newsletter email input, found {count}')
    path.write_text(text.replace(old, new), encoding='utf-8')
    changed += 1

print(f'Added an accessible name to the newsletter email input in {changed} retained footer component sources.')
