from pathlib import Path

ROOT = Path('.')
changed = []

# WebKit can paint the rotated back face even when backface-visibility is set.
# On mobile the approved behavior is not a 3D flip at all: the front card stays
# readable and View Full Details expands normal page-flow content. Make the
# back face literally display:none from component state instead of relying on
# a media-query/backface rendering quirk.
needle = "display:grid;grid-template-rows:auto 1fr auto;inset:0;padding:0;position:absolute;transform:rotateY(180deg);width:100%"
replacement = "display:{{ backFaceDisplay }};grid-template-rows:auto 1fr auto;inset:0;padding:0;position:absolute;transform:rotateY(180deg);width:100%"

for path in ROOT.rglob('Program Cards.dc.html'):
    if any(part in {'.git', 'node_modules'} for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8')
    new = text
    if 'backFaceDisplay:' not in new:
        marker = "const out = {\n"
        if marker not in new:
            raise SystemExit(f'Program card renderVals marker missing: {path}')
        new = new.replace(marker, marker + "      backFaceDisplay: t ? 'none' : 'grid',\n", 1)
    count = new.count(needle)
    if count:
        new = new.replace(needle, replacement)
    if new != text:
        path.write_text(new, encoding='utf-8')
        changed.append(str(path))

# Make the mobile card action visibly functional rather than 7–8px microtype.
css_path = ROOT / 'assets' / 'rendered-corrections.css'
css = css_path.read_text(encoding='utf-8')
block = """

/* PROGRAM CARD ACTIONS: functional controls stay readable. */
[data-program-action] {
  font-family:var(--sc-sans) !important;
  font-size:10px !important;
  font-weight:400 !important;
  letter-spacing:.085em !important;
}
button[data-program-action] { min-height:44px !important; }
@media (max-width:720px) {
  [data-program-action] { font-size:10.5px !important; }
}
"""
if '/* PROGRAM CARD ACTIONS: functional controls stay readable. */' not in css:
    css_path.write_text(css.rstrip() + block + '\n', encoding='utf-8')
    changed.append(str(css_path))

print(f'Updated {len(changed)} files')
for p in changed:
    print(p)
