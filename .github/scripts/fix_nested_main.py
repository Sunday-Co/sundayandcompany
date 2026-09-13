from pathlib import Path

p = Path('404.html')
text = p.read_text(encoding='utf-8')
old_open = '''  <main id="main-content" tabindex="-1">\n\n  <main style="'''
new_open = '''  <main id="main-content" tabindex="-1" style="'''
if old_open in text:
    text = text.replace(old_open, new_open, 1)
old_close = '''  </main>\n\n    </main>\n\n  <dc-import name="/Site Footer"'''
new_close = '''  </main>\n\n  <dc-import name="/Site Footer"'''
if old_close in text:
    text = text.replace(old_close, new_close, 1)
p.write_text(text, encoding='utf-8')
assert text.count('<main') == 1, f'404 should contain exactly one main, found {text.count("<main")}'
assert '<main id="main-content" tabindex="-1" style=' in text
print('404 semantic main structure corrected.')
