from pathlib import Path

paths = sorted(set(Path('.').glob('**/Program Cards.dc.html')))
if not paths:
    raise SystemExit('No Program Cards component files found')

front_anchor = 'style="backface-visibility:hidden;-webkit-backface-visibility:hidden;background:#f5efe6;'
back_anchor = 'display:{{ backFaceDisplay }};grid-template-rows:auto 1fr auto;'
loop_old = """    for (let i = 0; i < 3; i++) {\n      out['flip' + i] = this.state.flipped === i ? 'rotateY(180deg)' : 'rotateY(0deg)';\n      out['doFlip' + i] = () => this.setState({ flipped: i });\n      out['d' + i] = this.state.dialog === i ? 'flex' : 'none';\n      out['openD' + i] = () => this.setState({ dialog: i });\n    }\n"""
loop_new = """    for (let i = 0; i < 3; i++) {\n      const isFlipped = this.state.flipped === i;\n      out['flip' + i] = isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)';\n      // On phones WebKit can paint the reverse face of untouched 3D cards in\n      // full-page captures. Keep the flip itself, but explicitly gate the\n      // inactive face from the rendered component state. Desktop keeps the\n      // original backface-only behavior.\n      out['frontOpacity' + i] = t && isFlipped ? '0' : '1';\n      out['frontVisibility' + i] = t && isFlipped ? 'hidden' : 'visible';\n      out['frontPointer' + i] = t && isFlipped ? 'none' : 'auto';\n      out['backOpacity' + i] = t && !isFlipped ? '0' : '1';\n      out['backVisibility' + i] = t && !isFlipped ? 'hidden' : 'visible';\n      out['backPointer' + i] = t && !isFlipped ? 'none' : 'auto';\n      out['doFlip' + i] = () => this.setState({ flipped: i });\n      out['d' + i] = this.state.dialog === i ? 'flex' : 'none';\n      out['openD' + i] = () => this.setState({ dialog: i });\n    }\n"""

changed = 0
for path in paths:
    text = path.read_text(encoding='utf-8')
    if 'frontVisibility0' in text:
        continue

    if text.count(front_anchor) != 3:
        raise SystemExit(f'{path}: expected 3 front-face style anchors, found {text.count(front_anchor)}')
    for i in range(3):
        replacement = (
            f'style="backface-visibility:hidden;-webkit-backface-visibility:hidden;'
            f'opacity:{{{{ frontOpacity{i} }}}};pointer-events:{{{{ frontPointer{i} }}}};'
            f'visibility:{{{{ frontVisibility{i} }}}};background:#f5efe6;'
        )
        text = text.replace(front_anchor, replacement, 1)

    if text.count(back_anchor) != 3:
        raise SystemExit(f'{path}: expected 3 back-face style anchors, found {text.count(back_anchor)}')
    for i in range(3):
        replacement = (
            f'display:{{{{ backFaceDisplay }}}};opacity:{{{{ backOpacity{i} }}}};'
            f'pointer-events:{{{{ backPointer{i} }}}};visibility:{{{{ backVisibility{i} }}}};'
            'grid-template-rows:auto 1fr auto;'
        )
        text = text.replace(back_anchor, replacement, 1)

    if text.count(loop_old) != 1:
        raise SystemExit(f'{path}: expected one render loop, found {text.count(loop_old)}')
    text = text.replace(loop_old, loop_new, 1)
    path.write_text(text, encoding='utf-8')
    changed += 1

print(f'Patched {changed} Program Cards component copies ({len(paths)} total).')
