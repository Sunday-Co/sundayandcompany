from pathlib import Path

p = Path('assets/site.css')
s = p.read_text(encoding='utf-8')
old = s

target = '''  [aria-label="Newsletter"] [data-news-fineprint] {\n    font-size: 9.5px !important;\n  }'''
replacement = '''  [aria-label="Newsletter"] [data-news-fineprint] {\n    font-size: 7.5px !important;\n    letter-spacing: .045em !important;\n    line-height: 1.45 !important;\n  }'''

if target not in s:
    raise SystemExit('newsletter fine-print target not found or already applied')

s = s.replace(target, replacement, 1)
p.write_text(s, encoding='utf-8')
print('Updated mobile newsletter fine-print hierarchy')
