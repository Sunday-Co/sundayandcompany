from pathlib import Path

path = Path('contact/index.html')
text = path.read_text()
old = 'padding:145px clamp(22px,7vw,110px) clamp(54px,7vw,92px);position:relative">\n    <span aria-hidden="true" style="color:rgba(245,239,230,.045);font-size:clamp(100px,18vw,285px);'
new = 'padding:145px clamp(22px,7vw,110px) clamp(54px,7vw,92px);overflow:hidden;position:relative">\n    <span aria-hidden="true" style="color:rgba(245,239,230,.045);font-size:clamp(100px,18vw,285px);'

if new in text:
    print('Contact capture clip already present.')
elif old in text:
    path.write_text(text.replace(old, new, 1))
    print('Clipped only the Contact hero so its decorative CONTACT word cannot widen Safari/WebKit full-page captures.')
else:
    raise SystemExit('Could not locate the expected Contact hero markup; refusing a broad fallback change.')

final = path.read_text()
if new not in final:
    raise SystemExit('Contact capture clip was not applied.')
