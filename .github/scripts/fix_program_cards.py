from pathlib import Path

paths = sorted(set(Path('.').glob('**/Program Cards.dc.html')))
if not paths:
    raise SystemExit('No Program Cards component files found')

needle = '''    [data-program-cards] > article > div > div:nth-child(2) {\n      display:grid !important;\n    }\n'''
addition = '''    /* WebKit full-page capture can paint hidden 3D backs unless the inactive\n       face is also explicitly hidden by the rendered rotateY state. */\n    [data-program-cards] > article > div[style*="rotateY(0deg)"] > button:first-child {\n      opacity:1 !important;\n      pointer-events:auto !important;\n      visibility:visible !important;\n    }\n    [data-program-cards] > article > div[style*="rotateY(0deg)"] > div:nth-child(2) {\n      opacity:0 !important;\n      pointer-events:none !important;\n      visibility:hidden !important;\n    }\n    [data-program-cards] > article > div[style*="rotateY(180deg)"] > button:first-child {\n      opacity:0 !important;\n      pointer-events:none !important;\n      visibility:hidden !important;\n    }\n    [data-program-cards] > article > div[style*="rotateY(180deg)"] > div:nth-child(2) {\n      opacity:1 !important;\n      pointer-events:auto !important;\n      visibility:visible !important;\n    }\n'''

changed = 0
for path in paths:
    text = path.read_text(encoding='utf-8')
    if 'WebKit full-page capture can paint hidden 3D backs' in text:
        continue
    if text.count(needle) != 1:
        raise SystemExit(f'{path}: expected one mobile back-face block, found {text.count(needle)}')
    text = text.replace(needle, needle + addition, 1)
    path.write_text(text, encoding='utf-8')
    changed += 1

print(f'Patched {changed} Program Cards component copies ({len(paths)} total).')
