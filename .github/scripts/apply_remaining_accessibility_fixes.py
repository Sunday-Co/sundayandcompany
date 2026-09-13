from pathlib import Path

ROOT = Path('.')

# User-approved correction to the no-deploy accessibility candidate:
# preserve the Petti Pathways brand teal exactly as originally designed.
petti_path = ROOT / 'our-work/petti-pathways/index.html'
text = petti_path.read_text(encoding='utf-8')

changed = text.count('#2f7472')
if changed:
    text = text.replace('#2f7472', '#35807e')

if '#35807e' not in text:
    raise SystemExit('Petti Pathways original teal #35807e is missing')
if '#2f7472' in text:
    raise SystemExit('Petti Pathways accessibility variant teal still remains')

petti_path.write_text(text, encoding='utf-8')
print(f'Preserved Petti Pathways original teal; restored {changed} occurrence(s).')
