from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
css_path = ROOT / 'assets/site.css'
css = css_path.read_text(encoding='utf-8')
marker = '/* BATCH 7 WEBKIT: PROGRAM CARD FLIP COMPATIBILITY */'
if marker not in css:
    css += r'''

/* BATCH 7 WEBKIT: PROGRAM CARD FLIP COMPATIBILITY
   Safari/WebKit needs the prefixed 3D context on the card wrapper itself,
   not only backface-visibility on each face. */
[data-program-cards] > article {
  -webkit-perspective: 1400px !important;
  perspective: 1400px !important;
}

[data-program-cards] > article > div {
  -webkit-transform-style: preserve-3d !important;
  transform-style: preserve-3d !important;
}

[data-program-cards] > article > div > button,
[data-program-cards] > article > div > div {
  -webkit-backface-visibility: hidden !important;
  backface-visibility: hidden !important;
}
'''
    css_path.write_text(css, encoding='utf-8')

print('Program card WebKit 3D compatibility rules applied.')
