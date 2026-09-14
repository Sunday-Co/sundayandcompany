from pathlib import Path

VERSION_OLD = '20260914-18'
VERSION_NEW = '20260914-19'

site_js = Path('assets/site.js')
s = site_js.read_text()

# Keep the fallback stylesheet cache key aligned with the public page assets.
s = s.replace(f"/assets/rendered-corrections.css?v={VERSION_OLD}", f"/assets/rendered-corrections.css?v={VERSION_NEW}")

marker = "  function syncAccessibleSurface() {\n"
block = r'''  var sundayMobileModalLock = null;
  var sundayViewportTimerA = 0;
  var sundayViewportTimerB = 0;

  function sundayIsMobileFormSurface(surface) {
    if (!surface || !window.matchMedia || !window.matchMedia('(max-width: 820px)').matches) return false;
    var label = surface.getAttribute('aria-label') || '';
    return label === 'Project inquiry' || label === 'The Sunday Reservation';
  }

  function sundaySetVisualHeight() {
    var root = document.documentElement;
    var vv = window.visualViewport;
    var height = vv && vv.height ? vv.height : window.innerHeight;
    if (!height) return;
    var value = (Math.round(height * 100) / 100) + 'px';
    if (root.style.getPropertyValue('--sunday-visual-height') !== value) {
      root.style.setProperty('--sunday-visual-height', value);
    }
  }

  function sundayScheduleVisualHeight() {
    sundaySetVisualHeight();
    if (sundayViewportTimerA) window.clearTimeout(sundayViewportTimerA);
    if (sundayViewportTimerB) window.clearTimeout(sundayViewportTimerB);
    sundayViewportTimerA = window.setTimeout(sundaySetVisualHeight, 120);
    sundayViewportTimerB = window.setTimeout(sundaySetVisualHeight, 320);
  }

  function sundayLockMobileFormSurface(surface) {
    if (!document.body) return;
    if (sundayMobileModalLock && sundayMobileModalLock.surface === surface) {
      sundayScheduleVisualHeight();
      return;
    }
    if (sundayMobileModalLock) sundayUnlockMobileFormSurface(false);

    var body = document.body;
    var scrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
    sundayMobileModalLock = {
      surface: surface,
      scrollY: scrollY,
      position: body.style.position,
      top: body.style.top,
      left: body.style.left,
      right: body.style.right,
      width: body.style.width,
      overflow: body.style.overflow
    };

    document.documentElement.setAttribute('data-sunday-form-modal', 'open');
    body.style.position = 'fixed';
    body.style.top = '-' + scrollY + 'px';
    body.style.left = '0';
    body.style.right = '0';
    body.style.width = '100%';
    body.style.overflow = 'hidden';
    sundayScheduleVisualHeight();
  }

  function sundayUnlockMobileFormSurface(restoreScroll) {
    if (!sundayMobileModalLock || !document.body) return;
    var lock = sundayMobileModalLock;
    sundayMobileModalLock = null;
    var body = document.body;

    body.style.position = lock.position;
    body.style.top = lock.top;
    body.style.left = lock.left;
    body.style.right = lock.right;
    body.style.width = lock.width;
    body.style.overflow = lock.overflow;
    document.documentElement.removeAttribute('data-sunday-form-modal');
    document.documentElement.style.removeProperty('--sunday-visual-height');

    if (restoreScroll !== false) {
      window.requestAnimationFrame(function () {
        window.scrollTo({ left: 0, top: lock.scrollY, behavior: 'auto' });
      });
    }
  }

  function syncMobileFormFocusStability() {
    var surface = sundayCurrentSurface();
    if (sundayIsMobileFormSurface(surface)) sundayLockMobileFormSurface(surface);
    else sundayUnlockMobileFormSurface(true);
  }

'''
if 'function syncMobileFormFocusStability()' not in s:
    if marker not in s:
        raise SystemExit('syncAccessibleSurface marker not found')
    s = s.replace(marker, block + marker, 1)

sync_old = """  function sync() {
    ensureCorrectionStyles();
    applyFormRenderCorrections();
    syncAccessibleSurface();
  }
"""
sync_new = """  function sync() {
    ensureCorrectionStyles();
    applyFormRenderCorrections();
    syncAccessibleSurface();
    syncMobileFormFocusStability();
  }
"""
if sync_new not in s:
    if sync_old not in s:
        raise SystemExit('sync function marker not found')
    s = s.replace(sync_old, sync_new, 1)

boot_marker = """    installAccessibleSurfaceManagement();
    sync();

"""
boot_new = """    installAccessibleSurfaceManagement();
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', sundayScheduleVisualHeight, { passive: true });
    }
    window.addEventListener('resize', sundayScheduleVisualHeight, { passive: true });
    document.addEventListener('focusin', function (event) {
      var target = event.target;
      if (!target || !target.matches) return;
      if (!target.matches('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]),textarea,select,[contenteditable="true"]')) return;
      if (sundayIsMobileFormSurface(sundayCurrentSurface())) sundayScheduleVisualHeight();
    }, true);
    sync();

"""
if 'window.visualViewport.addEventListener' not in s:
    if boot_marker not in s:
        raise SystemExit('boot insertion marker not found')
    s = s.replace(boot_marker, boot_new, 1)

site_js.write_text(s)

css_path = Path('assets/rendered-corrections.css')
c = css_path.read_text()
css_marker = '/* MOBILE FORM FOCUS STABILITY · 2026-09-14 */'
css_block = r'''

/* MOBILE FORM FOCUS STABILITY · 2026-09-14 */
@media (max-width:820px) {
  input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]),
  textarea,
  select,
  [contenteditable="true"] {
    font-size:16px !important;
    -webkit-text-size-adjust:100%;
    text-size-adjust:100%;
  }

  input,
  textarea,
  select,
  button,
  [role="button"] {
    touch-action:manipulation;
  }

  input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]),
  textarea,
  select,
  [contenteditable="true"] {
    scroll-margin-top:92px;
    scroll-margin-bottom:32vh;
  }

  html[data-sunday-form-modal="open"],
  html[data-sunday-form-modal="open"] body {
    overscroll-behavior:none !important;
  }

  html[data-sunday-form-modal="open"] body {
    overflow:hidden !important;
  }

  html[data-sunday-form-modal="open"] div[role="presentation"]:has(> [aria-label="Project inquiry"]),
  html[data-sunday-form-modal="open"] div[role="presentation"]:has(> [aria-label="The Sunday Reservation"]) {
    align-items:flex-start !important;
    bottom:auto !important;
    height:var(--sunday-visual-height,100dvh) !important;
    max-height:var(--sunday-visual-height,100dvh) !important;
    min-height:0 !important;
    overflow:hidden !important;
    overscroll-behavior:none !important;
    padding:12px !important;
  }

  html[data-sunday-form-modal="open"] [aria-label="Project inquiry"],
  html[data-sunday-form-modal="open"] [aria-label="The Sunday Reservation"] {
    margin:0 auto !important;
    max-height:calc(var(--sunday-visual-height,100dvh) - 24px) !important;
    overflow-x:hidden !important;
    overflow-y:auto !important;
    overscroll-behavior:contain !important;
    scroll-behavior:auto !important;
    scroll-padding-top:18px;
    scroll-padding-bottom:clamp(140px,32dvh,280px);
    -webkit-overflow-scrolling:touch;
  }
}
'''
if css_marker not in c:
    c = c.rstrip() + css_block + '\n'
css_path.write_text(c)

# Cache-bust all public HTML references together so iOS Safari cannot retain the old JS/CSS.
changed_html = 0
for p in Path('.').rglob('*.html'):
    text = p.read_text()
    new = text.replace(VERSION_OLD, VERSION_NEW)
    if new != text:
        p.write_text(new)
        changed_html += 1

checks = {
    'mobile modal page lock installed': 'function sundayLockMobileFormSurface(surface)' in s,
    'scroll restoration installed': "window.scrollTo({ left: 0, top: lock.scrollY, behavior: 'auto' });" in s,
    'visual viewport listener installed': "window.visualViewport.addEventListener('resize', sundayScheduleVisualHeight" in s,
    'sync activates focus stability': 'syncMobileFormFocusStability();' in s,
    'mobile editable controls forced to 16px': 'font-size:16px !important;' in c,
    'modal overlay uses visual viewport height': 'var(--sunday-visual-height,100dvh)' in c,
    'pinch zoom remains allowed': 'user-scalable=no' not in c and 'maximum-scale=1' not in c,
    'asset cache key advanced': VERSION_NEW in s,
    'public HTML refs advanced': changed_html >= 15 or all(VERSION_NEW in p.read_text() for p in Path('.').rglob('index.html')),
}
failed = []
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ' | ' + name)
    if not ok:
        failed.append(name)
print('HTML files cache-busted:', changed_html)
if failed:
    raise SystemExit('Failed: ' + ', '.join(failed))
