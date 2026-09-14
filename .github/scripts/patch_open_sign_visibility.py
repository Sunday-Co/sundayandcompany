from pathlib import Path

# Make the homepage component the single owner of OPEN-sign interaction.
# The shared legacy fallback stays in source for compatibility, but it is not
# activated and receives no new behavior in this release.
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

# Remove the temporary global click listener that the first-pass script adds.
# Manual replay now belongs to the homepage component above.
global_click = """    if (!signMotionClickBound) {
      document.addEventListener('click', function (event) {
        var target = event.target;
        var hit = target && target.closest ? target.closest('[data-sign]') : null;
        if (!hit) return;
        if (target.closest && target.closest('button,a[href],input,textarea,select')) return;
        triggerOriginalOpenSignMotion();
      });
      signMotionClickBound = true;
    }

"""
s = s.replace(global_click, '', 1)

# Do not activate the duplicate global OPEN-sign fallback. The homepage DC
# component owns entry/re-entry and pointer/touch replay.
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

# The legacy rendered-corrections fallback is inactive now, so keep its source
# unchanged from production instead of creating a second timing owner.
css = Path('assets/rendered-corrections.css')
c = css.read_text()
c = c.replace(
    'animation:sc-warm 2.8s ease-out 1 both, sc-neon 5.6s ease-in-out 2.8s infinite !important;',
    'animation:sc-warm 2.6s ease-out 1 both, sc-neon 3.8s ease-in-out 2.6s infinite !important;',
)
c = c.replace(
    'animation:sc-rock 6.2s cubic-bezier(.34,.08,.18,.96) 1 both, sc-sway 8.5s ease-in-out 6.2s infinite !important;',
    'animation:sc-rock 5.4s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 7s ease-in-out 5.4s infinite !important;',
)
css.write_text(c)

checks = {
    'component owns sign pointer interaction': "sign.addEventListener('pointerdown', this._signClick);" in h,
    'sign controls are excluded': "target.closest('button,a[href],input,textarea,select')" in h,
    'pointer handler is cleaned up': "removeEventListener('pointerdown', this._signClick)" in h,
    'global sign click listener is absent': "target.closest('[data-sign]')" not in s,
    'global fallback is not activated': 'ensureOpenSignMotion();' not in s[s.find('function sync()'):s.find('function sync()') + 220],
    'legacy fallback CSS unchanged': 'sc-rock 5.4s' in c and 'sc-neon 3.8s' in c,
}
failed = []
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ' | ' + name)
    if not ok:
        failed.append(name)
if failed:
    raise SystemExit('Failed: ' + ', '.join(failed))
