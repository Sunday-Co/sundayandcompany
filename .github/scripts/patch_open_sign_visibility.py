from pathlib import Path

# Make the homepage component the single owner of OPEN-sign interaction.
# The shared fallback remains available as dead compatibility code, but sync()
# no longer activates it, so it cannot override the component's inline state.
home = Path('index.html')
h = home.read_text()

old_mount = """      this._sio.observe(sign);
      this._signEl = sign;
    } else {
      this.setState({ signOn: true });
    }
    const row = document.querySelector('[data-ledger]');
"""
new_mount = """      this._sio.observe(sign);
    } else {
      this.setState({ signOn: true });
    }
    if (sign) {
      this._signEl = sign;
      this._signClick = (event) => {
        const target = event.target;
        if (target && target.closest && target.closest('button,a[href],input,textarea,select')) return;
        this.nudgeSign();
      };
      sign.addEventListener('pointerdown', this._signClick);
    }
    const row = document.querySelector('[data-ledger]');
"""
if new_mount not in h:
    if old_mount not in h:
        raise SystemExit('homepage sign mount marker missing')
    h = h.replace(old_mount, new_mount, 1)

old_unmount = """    if (this._signEl && this._signClick) this._signEl.removeEventListener('click', this._signClick);
"""
new_unmount = """    if (this._signEl && this._signClick) this._signEl.removeEventListener('pointerdown', this._signClick);
"""
if new_unmount not in h:
    if old_unmount not in h:
        raise SystemExit('homepage sign unmount marker missing')
    h = h.replace(old_unmount, new_unmount, 1)

home.write_text(h)

site = Path('assets/site.js')
s = site.read_text()
# Do not activate the duplicate global OPEN-sign fallback. The homepage DC
# component now owns entry/re-entry and pointer/touch replay.
sync_old = """  function sync() {
    ensureCorrectionStyles();
    ensureOpenSignMotion();
    applyFormRenderCorrections();
    syncAccessibleSurface();
  }
"""
sync_new = """  function sync() {
    ensureCorrectionStyles();
    applyFormRenderCorrections();
    syncAccessibleSurface();
  }
"""
if sync_new not in s:
    if sync_old not in s:
        raise SystemExit('site.js sync owner marker missing')
    s = s.replace(sync_old, sync_new, 1)
site.write_text(s)

checks = {
    'component owns sign pointer interaction': "sign.addEventListener('pointerdown', this._signClick);" in h,
    'sign controls are excluded': "target.closest('button,a[href],input,textarea,select')" in h,
    'pointer handler is cleaned up': "removeEventListener('pointerdown', this._signClick)" in h,
    'global fallback is not activated': 'ensureOpenSignMotion();' not in s[s.find('function sync()'):s.find('function sync()') + 220],
}
failed = []
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ' | ' + name)
    if not ok:
        failed.append(name)
if failed:
    raise SystemExit('Failed: ' + ', '.join(failed))
