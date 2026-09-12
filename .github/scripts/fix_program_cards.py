from pathlib import Path

paths = sorted(set(Path('.').glob('**/Program Cards.dc.html')))
if not paths:
    raise SystemExit('No Program Cards component files found')

loop_old = """    for (let i = 0; i < 3; i++) {\n      out['flip' + i] = this.state.flipped === i ? 'rotateY(180deg)' : 'rotateY(0deg)';\n      out['doFlip' + i] = () => this.setState({ flipped: i });\n      out['d' + i] = this.state.dialog === i ? 'flex' : 'none';\n      out['openD' + i] = () => this.setState({ dialog: i });\n    }\n"""
loop_new = """    for (let i = 0; i < 3; i++) {\n      const isFlipped = this.state.flipped === i;\n      out['flip' + i] = isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)';\n      // Keep the original 3D flip on phones, while explicitly hiding only\n      // the inactive face. This prevents Safari full-page capture from\n      // painting untouched cards backwards without changing the interaction.\n      out['frontOpacity' + i] = t && isFlipped ? '0' : '1';\n      out['frontVisibility' + i] = t && isFlipped ? 'hidden' : 'visible';\n      out['frontPointer' + i] = t && isFlipped ? 'none' : 'auto';\n      out['backOpacity' + i] = t && !isFlipped ? '0' : '1';\n      out['backVisibility' + i] = t && !isFlipped ? 'hidden' : 'visible';\n      out['backPointer' + i] = t && !isFlipped ? 'none' : 'auto';\n      out['doFlip' + i] = () => this.setState({ flipped: i });\n      out['d' + i] = this.state.dialog === i ? 'flex' : 'none';\n      out['openD' + i] = () => this.setState({ dialog: i });\n    }\n"""

back_start = '<div style="backface-visibility:hidden;-webkit-backface-visibility:hidden;background:#f5efe6;'

changed = 0
for path in paths:
    text = path.read_text(encoding='utf-8')
    if 'frontVisibility0' in text:
        continue

    for i in range(3):
        front_marker = f'onClick="{{{{ doFlip{i} }}}}" style="'
        if text.count(front_marker) != 1:
            raise SystemExit(f'{path}: expected one doFlip{i} front, found {text.count(front_marker)}')
        front_insert = (
            front_marker
            + f'opacity:{{{{ frontOpacity{i} }}}};pointer-events:{{{{ frontPointer{i} }}}};'
            + f'visibility:{{{{ frontVisibility{i} }}}};'
        )
        text = text.replace(front_marker, front_insert, 1)

        front_pos = text.index(front_insert)
        back_pos = text.find(back_start, front_pos)
        if back_pos < 0:
            raise SystemExit(f'{path}: back face after doFlip{i} not found')
        style_content_pos = back_pos + len('<div style="')
        back_insert = (
            f'opacity:{{{{ backOpacity{i} }}}};pointer-events:{{{{ backPointer{i} }}}};'
            f'visibility:{{{{ backVisibility{i} }}}};'
        )
        text = text[:style_content_pos] + back_insert + text[style_content_pos:]

    if text.count(loop_old) != 1:
        raise SystemExit(f'{path}: expected one render loop, found {text.count(loop_old)}')
    text = text.replace(loop_old, loop_new, 1)
    path.write_text(text, encoding='utf-8')
    changed += 1

print(f'Patched {changed} Program Cards component copies ({len(paths)} total).')
