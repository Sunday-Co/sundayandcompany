from pathlib import Path
import subprocess

site = Path('assets/site.css').read_text()
rendered = Path('assets/rendered-corrections.css').read_text()
js = Path('assets/site.js').read_text()

for token in [
    'normalizeRuntimeRoots', 'normalizeFooterTypography', 'prepareImagesForCapture',
    'markHeroFallbacks', 'CAPTURE INTEGRITY + FOOTER NORMALIZATION', '[data-capture-full-image]'
]:
    if token in site + js:
        raise SystemExit('obsolete source remains: ' + token)

for token in [
    'font-size: 13.25px !important',
    'font-size: 11.5px !important',
    'font-size: 8px !important',
    'align-items: flex-start !important',
    'max-height: calc(100dvh - 24px) !important',
    'overflow-y: visible !important',
]:
    if token not in site:
        raise SystemExit('required controlled source missing: ' + token)

if '/assets/rendered-corrections.css?v=20260913-12' not in js:
    raise SystemExit('wrong rendered CSS cache key')

for token in ['sc-warm', 'sc-neon', 'sc-rock', 'sc-sway']:
    if token not in rendered:
        raise SystemExit('OPEN sign sequence missing: ' + token)

# The modal entrance may translate slightly, but cannot fade the entire dialog.
start = site.find('@keyframes sunday-modal-in {')
if start < 0:
    raise SystemExit('modal animation missing')
brace = site.find('{', start)
depth = 0
end = None
for i in range(brace, len(site)):
    if site[i] == '{': depth += 1
    elif site[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    raise SystemExit('modal animation is malformed')
modal_block = site[start:end]
if 'opacity: 0;' in modal_block:
    raise SystemExit('modal animation still fades whole dialog')
if modal_block.count('opacity: 1;') < 2:
    raise SystemExit('modal animation is not solid throughout')

# Generated shared components must be identical everywhere.
for name in ['Site Header.dc.html', 'Site Footer.dc.html', 'Inquiry Form.dc.html', 'Program Cards.dc.html']:
    paths = list(Path('.').rglob(name))
    if not paths:
        raise SystemExit('missing generated component: ' + name)
    variants = {p.read_text() for p in paths}
    if len(variants) != 1:
        raise SystemExit(f'{name} has {len(variants)} source variants')

# Portfolio presentation and motion are locked to current production.
subprocess.run(['git', 'fetch', 'origin', 'main'], check=True, stdout=subprocess.DEVNULL)
locked = [
    'our-work/index.html',
    'our-work/luckys-cafe-bakery/index.html',
    'our-work/petti-pathways/index.html',
    'our-work/pizzeria-coco/index.html',
    'our-work/folake/index.html',
]
for path in locked:
    prod = subprocess.check_output(['git', 'show', 'origin/main:' + path], text=True)
    cand = Path(path).read_text().replace('v=20260913-12', 'v=20260912-11')
    if cand != prod:
        raise SystemExit('LOCKED portfolio page changed beyond cache key: ' + path)

lucky = Path('our-work/luckys-cafe-bakery/index.html').read_text()
for token in ['max-height:640px;overflow-y:auto', "n.style.opacity = '0'", 'translateY(20px)']:
    if token not in lucky:
        raise SystemExit('original portfolio behavior missing: ' + token)

for path in Path('.').rglob('*.html'):
    if '.github' not in path.parts and 'loading="lazy"' in path.read_text():
        raise SystemExit('lazy image remains: ' + str(path))

if 'data-sunday-static-hero="true"' not in Path('index.html').read_text():
    raise SystemExit('homepage static hero marker missing')

print('Strict V4 source validation passed.')
