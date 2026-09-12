from pathlib import Path
p=Path('assets/site.css')
s=p.read_text(encoding='utf-8')
old=s
s=s.replace('''[aria-label="Newsletter"] form input {\n  font-size: 15px !important;\n}''','''[aria-label="Newsletter"] form input {\n  font-size: 16px !important;\n}''')
s=s.replace('''[aria-label="Newsletter"] form button {\n  min-height: 42px !important;\n}''','''[aria-label="Newsletter"] form button {\n  min-height: 44px !important;\n}''')
if s==old:
    raise SystemExit('newsletter correction targets not found or already applied')
p.write_text(s,encoding='utf-8')
print('Updated newsletter functional control sizing')
