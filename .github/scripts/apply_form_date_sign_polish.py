from pathlib import Path


def require_replace(text, old, new, label):
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise SystemExit(f"Missing {label}")


# Project Inquiry: fix the real date-label owner, open the calendar upward,
# and give the privacy notice its own block display state rather than reusing
# the step fieldset's `grid` display value.
inquiry = Path('Inquiry Form.dc.html')
s = inquiry.read_text()
marker = """  [data-inq] button {
    font-family: 'Inter Tight', sans-serif !important;
    font-weight: 400;
  }
"""
addition = marker + """  [data-inq] [data-start-date-label] {
    font-family: 'Inter Tight', sans-serif !important;
    font-size: 9.5px !important;
    font-weight: 400 !important;
    letter-spacing: .055em !important;
    line-height: 1.25 !important;
    text-transform: uppercase !important;
  }
  [data-inq] [data-form-privacy] {
    font-family: 'Inter Tight', sans-serif !important;
    font-size: 8.5px !important;
    font-weight: 300 !important;
    letter-spacing: .02em !important;
    line-height: 1.35 !important;
    white-space: nowrap !important;
  }
  [data-inq] [data-date-panel] {
    bottom: calc(100% + 6px) !important;
    top: auto !important;
  }
"""
if '[data-start-date-label]' not in s.split('</style>', 1)[0]:
    if marker not in s:
        raise SystemExit('Inquiry style marker missing')
    s = s.replace(marker, addition, 1)

s = require_replace(
    s,
    "<span style=\"font-family:'Inter Tight',sans-serif;font-size:9.5px!important;font-weight:400;letter-spacing:.10em;text-transform:uppercase\">Ideal Start Date</span>",
    "<span data-start-date-label style=\"font-family:'Inter Tight',sans-serif;font-size:9.5px!important;font-weight:400;letter-spacing:.055em;text-transform:uppercase\">Ideal Start Date</span>",
    'date label hook',
)
s = require_replace(
    s,
    "<div role=\"dialog\" aria-label=\"Choose a start date\" style=\"background:#fffdf8;border:1px solid #311d03;border-radius:0;box-shadow:6px 8px 0 rgba(49,29,3,.13);left:0;max-width:100%;padding:8px;position:absolute;top:100%;width:min(320px,100%);z-index:30;display:{{ datePanel }}\">",
    "<div data-date-panel role=\"dialog\" aria-label=\"Choose a start date\" style=\"background:#fffdf8;border:1px solid #311d03;border-radius:0;bottom:calc(100% + 6px);box-shadow:6px 8px 0 rgba(49,29,3,.13);left:0;max-width:100%;padding:8px;position:absolute;top:auto;width:min(320px,100%);z-index:30;display:{{ datePanel }}\">",
    'upward date panel',
)
s = require_replace(
    s,
    "<p data-form-privacy data-step=\"3\" style=\"display:{{ step3Display }};font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:300;grid-column:1 / -1;letter-spacing:.035em;line-height:1.45;margin:1px 0 0;opacity:.72\">By submitting this form, you acknowledge our <a href=\"/privacy-policy\" style=\"border-bottom:1px solid currentColor;padding-bottom:1px\">Privacy Policy</a>.</p>",
    "<p data-form-privacy data-step=\"3\" style=\"display:{{ privacyDisplay }};font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:300;grid-column:1 / -1;letter-spacing:.02em;line-height:1.35;margin:1px 0 0;opacity:.72;white-space:nowrap\">By submitting this form, you acknowledge our <a href=\"/privacy-policy\" style=\"border-bottom:1px solid currentColor;padding-bottom:1px\">Privacy Policy</a>.</p>",
    'privacy display owner',
)
s = require_replace(
    s,
    "    out.step3Display = st === 3 ? 'grid' : 'none';\n    out.otherDisplay = st === 3 && this.state.picked.iqOther ? 'grid' : 'none';",
    "    out.step3Display = st === 3 ? 'grid' : 'none';\n    out.privacyDisplay = st === 3 ? 'block' : 'none';\n    out.otherDisplay = st === 3 && this.state.picked.iqOther ? 'grid' : 'none';",
    'privacy display state',
)
inquiry.write_text(s)

# Homepage OPEN sign: retain the original hanging-sign behavior but make it
# slower, slightly more visible, and expose stable hooks for rendered QA.
home = Path('index.html')
h = home.read_text()
h = require_replace(
    h,
    """  @keyframes sc-rock {
    0%   { transform: rotate(2.6deg) }
    14%  { transform: rotate(-2.1deg) }
    28%  { transform: rotate(1.5deg) }
    42%  { transform: rotate(-1.05deg) }
    56%  { transform: rotate(.7deg) }
    70%  { transform: rotate(-.45deg) }
    84%  { transform: rotate(.26deg) }
    100% { transform: rotate(-.6deg) }
  }
  @keyframes sc-sway {
    0%, 100% { transform: rotate(-.6deg) }
    50%      { transform: rotate(.45deg) }
  }
""",
    """  @keyframes sc-rock {
    0%   { transform: rotate(3.2deg) }
    16%  { transform: rotate(-2.55deg) }
    32%  { transform: rotate(1.78deg) }
    48%  { transform: rotate(-1.18deg) }
    64%  { transform: rotate(.72deg) }
    80%  { transform: rotate(-.34deg) }
    100% { transform: rotate(-.55deg) }
  }
  @keyframes sc-sway {
    0%, 100% { transform: rotate(-.55deg) }
    50%      { transform: rotate(.52deg) }
  }
""",
    'slower sign keyframes',
)
old_neon = "  @keyframes sc-neon { 0%,100% { text-shadow:0 0 6px rgba(255,240,236,.5), 0 0 18px rgba(172,116,108,.75), 0 0 44px rgba(172,116,108,.4), 0 0 80px rgba(172,116,108,.18) } 50% { text-shadow:0 0 8px rgba(255,240,236,.75), 0 0 26px rgba(172,116,108,.95), 0 0 62px rgba(172,116,108,.6), 0 0 110px rgba(172,116,108,.3) } }"
new_neon = "  @keyframes sc-neon { 0%,100% { opacity:.72; text-shadow:0 0 5px rgba(255,240,236,.38), 0 0 15px rgba(172,116,108,.62), 0 0 38px rgba(172,116,108,.32), 0 0 70px rgba(172,116,108,.14) } 50% { opacity:1; text-shadow:0 0 10px rgba(255,240,236,.88), 0 0 31px rgba(172,116,108,1), 0 0 72px rgba(172,116,108,.72), 0 0 122px rgba(172,116,108,.36) } }"
h = require_replace(h, old_neon, new_neon, 'stronger neon pulse')
h = require_replace(h, '<div style="animation:{{ rockAnim }};transform-origin:50% 0">', '<div data-sign-swing style="animation:{{ rockAnim }};transform-origin:50% 0">', 'sign swing hook')
h = require_replace(h, '<p aria-hidden="true" style="animation:{{ signAnim }};color:#ac746c;', '<p data-sign-open aria-hidden="true" style="animation:{{ signAnim }};color:#ac746c;', 'sign open hook')
h = require_replace(
    h,
    "? 'sc-rock 5.4s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 7s ease-in-out 5.4s infinite'",
    "? 'sc-rock 6.2s cubic-bezier(.34,.08,.18,.96) 1 both, sc-sway 8.5s ease-in-out 6.2s infinite'",
    'component swing timing',
)
h = require_replace(
    h,
    "? 'sc-warm 2.6s ease-out 1 both, sc-neon 3.8s ease-in-out 2.6s infinite'",
    "? 'sc-warm 2.8s ease-out 1 both, sc-neon 5.6s ease-in-out 2.8s infinite'",
    'component pulse timing',
)
home.write_text(h)

# The DC renderer can strip component typography. Enforce the one exceptional
# date label after render, idempotently, and restore manual OPEN-sign motion
# through the existing fallback that already survives DC recompiles.
site_js = Path('assets/site.js')
j = site_js.read_text().replace('20260914-17', '20260914-18')
click_marker = """    var sign = document.querySelector('[data-sign]');
    if (!sign) return;

    if (!('IntersectionObserver' in window)) {
"""
click_insert = """    var sign = document.querySelector('[data-sign]');
    if (!sign) return;

    if (!signMotionClickBound) {
      document.addEventListener('click', function (event) {
        var target = event.target;
        var hit = target && target.closest ? target.closest('[data-sign]') : null;
        if (!hit) return;
        if (target.closest && target.closest('button,a[href],input,textarea,select')) return;
        triggerOriginalOpenSignMotion();
      });
      signMotionClickBound = true;
    }

    if (!('IntersectionObserver' in window)) {
"""
if "target.closest('[data-sign]')" not in j:
    if click_marker not in j:
        raise SystemExit('site.js sign marker missing')
    j = j.replace(click_marker, click_insert, 1)

sync_marker = """  function sync() {
    ensureCorrectionStyles();
    ensureOpenSignMotion();
    syncAccessibleSurface();
  }
"""
form_correction = """  function applyFormRenderCorrections() {
    var labels = document.querySelectorAll('[data-start-date-label]');
    for (var i = 0; i < labels.length; i++) {
      var label = labels[i];
      if (label.style.getPropertyValue('font-size') !== '9.5px' || label.style.getPropertyPriority('font-size') !== 'important') {
        label.style.setProperty('font-family', "'Inter Tight', sans-serif", 'important');
        label.style.setProperty('font-size', '9.5px', 'important');
        label.style.setProperty('font-weight', '400', 'important');
        label.style.setProperty('letter-spacing', '.055em', 'important');
        label.style.setProperty('line-height', '1.25', 'important');
        label.style.setProperty('text-transform', 'uppercase', 'important');
      }
    }
  }

  function sync() {
    ensureCorrectionStyles();
    ensureOpenSignMotion();
    applyFormRenderCorrections();
    syncAccessibleSurface();
  }
"""
if 'function applyFormRenderCorrections()' not in j:
    if sync_marker not in j:
        raise SystemExit('site.js sync marker missing')
    j = j.replace(sync_marker, form_correction, 1)
site_js.write_text(j)

# Keep the CSS fallback motion exactly aligned with the component timing.
corrections = Path('assets/rendered-corrections.css')
c = corrections.read_text()
c = c.replace(
    'animation:sc-warm 2.6s ease-out 1 both, sc-neon 3.8s ease-in-out 2.6s infinite !important;',
    'animation:sc-warm 2.8s ease-out 1 both, sc-neon 5.6s ease-in-out 2.8s infinite !important;',
)
c = c.replace(
    'animation:sc-rock 5.4s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 7s ease-in-out 5.4s infinite !important;',
    'animation:sc-rock 6.2s cubic-bezier(.34,.08,.18,.96) 1 both, sc-sway 8.5s ease-in-out 6.2s infinite !important;',
)
corrections.write_text(c)

# Keep every page-local Inquiry component identical to the reviewed root source.
dirs = ['about','accessibility','contact','cookie-policy','join-our-team','our-work','our-work/folake','our-work/luckys-cafe-bakery','our-work/petti-pathways','our-work/pizzeria-coco','privacy-policy','services','sunday-school','terms-and-conditions']
source = inquiry.read_bytes()
for d in dirs:
    (Path(d) / 'Inquiry Form.dc.html').write_bytes(source)

# Cache-bust the corrected shared assets on all public pages.
routes = ['index.html','about/index.html','accessibility/index.html','contact/index.html','cookie-policy/index.html','join-our-team/index.html','our-work/index.html','our-work/folake/index.html','our-work/luckys-cafe-bakery/index.html','our-work/petti-pathways/index.html','our-work/pizzeria-coco/index.html','privacy-policy/index.html','services/index.html','sunday-school/index.html','terms-and-conditions/index.html']
for route in routes:
    p = Path(route)
    p.write_text(p.read_text().replace('20260914-17', '20260914-18'))

# Static guardrails before rendered QA.
failures = []
def check(name, ok):
    print(('PASS' if ok else 'FAIL') + ' | ' + name)
    if not ok:
        failures.append(name)

inquiry_text = inquiry.read_text()
home_text = home.read_text()
js_text = site_js.read_text()
css_text = corrections.read_text()
check('date label hook', 'data-start-date-label' in inquiry_text)
check('calendar opens upward', 'data-date-panel' in inquiry_text and 'bottom:calc(100% + 6px)' in inquiry_text and 'top:auto' in inquiry_text)
check('privacy has block display owner', 'display:{{ privacyDisplay }}' in inquiry_text and "out.privacyDisplay = st === 3 ? 'block' : 'none';" in inquiry_text)
check('privacy one-line source', 'data-form-privacy' in inquiry_text and 'white-space:nowrap' in inquiry_text)
check('render-level date correction', 'function applyFormRenderCorrections()' in js_text and "'9.5px'" in js_text)
check('manual sign swing restored', "target.closest('[data-sign]')" in js_text and 'triggerOriginalOpenSignMotion();' in js_text)
check('sign controls excluded', "target.closest('button,a[href],input,textarea,select')" in js_text)
check('slow swing timing', 'sc-rock 6.2s' in home_text and 'sc-sway 8.5s' in home_text and 'sc-rock 6.2s' in css_text)
check('stronger slow pulse', 'opacity:.72' in home_text and 'sc-neon 5.6s' in home_text and 'sc-neon 5.6s' in css_text)
root = inquiry.read_bytes()
check('local inquiry copies synced', all((Path(d) / 'Inquiry Form.dc.html').read_bytes() == root for d in dirs))
check('all routes v18', all('20260914-18' in Path(r).read_text() and '20260914-17' not in Path(r).read_text() for r in routes))
petti = Path('our-work/petti-pathways/index.html').read_text().lower()
check('Petti teal preserved', '#35807e' in petti and '#2f7472' not in petti)
if failures:
    raise SystemExit(', '.join(failures))
