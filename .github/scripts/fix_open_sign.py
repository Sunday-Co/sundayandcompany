from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
old_rock = """    out.rockAnim = (this._reduced || !sway)\n      ? 'none'\n      : this.state.signOn\n        ? 'sc-rock 5.4s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 7s ease-in-out 5.4s infinite'\n        : 'none';"""
new_rock = """    out.rockAnim = (this._reduced || !sway)\n      ? 'none'\n      : this.state.signOn\n        ? 'sc-rock 7s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 12s ease-in-out 7s infinite'\n        : 'none';"""
old_sign = """    out.signAnim = this._reduced\n      ? 'none'\n      : this.state.signOn\n        ? 'sc-warm 2.6s ease-out 1 both, sc-neon 3.8s ease-in-out 2.6s infinite'\n        : 'none';"""
new_sign = """    out.signAnim = this._reduced\n      ? 'none'\n      : this.state.signOn\n        ? 'sc-warm 4.6s ease-out 1 both, sc-neon-sunday-final 8.4s ease-in-out 4.6s infinite'\n        : 'none';"""
if text.count(old_rock) != 1:
    raise SystemExit(f'Expected one old rock animation block, found {text.count(old_rock)}')
if text.count(old_sign) != 1:
    raise SystemExit(f'Expected one old sign animation block, found {text.count(old_sign)}')
text = text.replace(old_rock, new_rock, 1).replace(old_sign, new_sign, 1)
path.write_text(text, encoding='utf-8')
