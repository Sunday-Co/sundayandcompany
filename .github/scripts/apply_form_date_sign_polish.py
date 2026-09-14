from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    s = p.read_text()
    if old in s:
        p.write_text(s.replace(old, new, 1))
    elif new in s:
        return
    else:
        raise SystemExit(f"Expected text not found in {path}: {old[:120]!r}")


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

s = s.replace(
    "<span style=\"font-family:'Inter Tight',sans-serif;font-size:9.5px!important;font-weight:400;letter-spacing:.10em;text-transform:uppercase\">Ideal Start Date</span>",
    "<span data-start-date-label style=\"font-family:'Inter Tight',sans-serif;font-size:9.5px!important;font-weight:400;letter-spacing:.055em;text-transform:uppercase\">Ideal Start Date</span>",
)
s = s.replace(
    "<div role=\"dialog\" aria-label=\"Choose a start date\" style=\"background:#fffdf8;border:1px solid #311d03;border-radius:0;box-shadow:6px 8px 0 rgba(49,29,3,.13);left:0;max-width:100%;padding:8px;position:absolute;top:100%;width:min(320px,100%);z-index:30;display:{{ datePanel }}\">",
    "<div data-date-panel role=\"dialog\" aria-label=\"Choose a start date\" style=\"background:#fffdf8;border:1px solid #311d03;border-radius:0;bottom:calc(100% + 6px);box-shadow:6px 8px 0 rgba(49,29,3,.13);left:0;max-width:100%;padding:8px;position:absolute;top:auto;width:min(320px,100%);z-index:30;display:{{ datePanel }}\">",
)
s = s.replace(
    "style=\"display:{{ step3Display }};font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:300;grid-column:1 / -1;letter-spacing:.035em;line-height:1.45;margin:1px 0 0;opacity:.72\"",
    "style=\"display:{{ step3Display }};font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:300;grid-column:1 / -1;letter-spacing:.02em;line-height:1.35;margin:1px 0 0;opacity:.72;white-space:nowrap\"",
)
inquiry.write_text(s)

home = Path('index.html')
h = home.read_text()
h = h.replace(
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
)
old_neon = "  @keyframes sc-neon { 0%,100% { text-shadow:0 0 6px rgba(255,240,236,.5), 0 0 18px rgba(172,116,108,.75), 0 0 44px rgba(172,116,108,.4), 0 0 80px rgba(172,116,108,.18) } 50% { text-shadow:0 0 8px rgba(255,240,236,.75), 0 0 26px rgba(172,116,108,.95), 0 0 62px rgba(172,116,108,.6), 0 0 110px rgba(172,116,108,.3) } }"
new_neon = "  @keyframes sc-neon { 0%,100% { opacity:.72; text-shadow:0 0 5px rgba(255,240,236,.38), 0 0 15px rgba(172,116,108,.62), 0 0 38px rgba(172,116,108,.32), 0 0 70px rgba(172,116,108,.14) } 50% { opacity:1; text-shadow:0 0 10px rgba(255,240,236,.88), 0 0 31px rgba(172,116,108,1), 0 0 72px rgba(172,116,108,.72), 0 0 122px rgba(172,116,108,.36) } }"
if old_neon in h:
    h = h.replace(old_neon, new_neon, 1)
elif new_neon not in h:
    raise SystemExit('sc-neon marker missing')

h = h.replace('<div style="animation:{{ rockAnim }};transform-origin:50% 0">', '<div data-sign-swing style="animation:{{ rockAnim }};transform-origin:50% 0">', 1)
h = h.replace('<p aria-hidden="true" style="animation:{{ signAnim }};color:#ac746c;', '<p data-sign-open aria-hidden="true" style="animation:{{ signAnim }};color:#ac746c;', 1)

sign_setup = """      this._sio.observe(sign);
      this._signEl = sign;
"""
sign_setup_new = """      this._sio.observe(sign);
      this._signClick = (event) => {
        const target = event && event.target;
        if (target && target.closest && target.closest('button,a,input,textarea,select')) return;
        this.nudgeSign();
      };
      sign.addEventListener('click', this._signClick);
      this._signEl = sign;
"""
if "sign.addEventListener('click', this._signClick)" not in h:
    if sign_setup not in h:
        raise SystemExit('sign setup marker missing')
    h = h.replace(sign_setup, sign_setup_new, 1)

h = h.replace(
    "? 'sc-rock 5.4s cubic-bezier(.36,.07,.19,.97) 1 both, sc-sway 7s ease-in-out 5.4s infinite'",
    "? 'sc-rock 6.2s cubic-bezier(.34,.08,.18,.96) 1 both, sc-sway 8.5s ease-in-out 6.2s infinite'",
)
h = h.replace(
    "? 'sc-warm 2.6s ease-out 1 both, sc-neon 3.8s ease-in-out 2.6s infinite'",
    "? 'sc-warm 2.8s ease-out 1 both, sc-neon 5.6s ease-in-out 2.8s infinite'",
)
home.write_text(h)

dirs = ['about','accessibility','contact','cookie-policy','join-our-team','our-work','our-work/folake','our-work/luckys-cafe-bakery','our-work/petti-pathways','our-work/pizzeria-coco','privacy-policy','services','sunday-school','terms-and-conditions']
source = inquiry.read_bytes()
for d in dirs:
    (Path(d) / 'Inquiry Form.dc.html').write_bytes(source)

routes = ['index.html','about/index.html','accessibility/index.html','contact/index.html','cookie-policy/index.html','join-our-team/index.html','our-work/index.html','our-work/folake/index.html','our-work/luckys-cafe-bakery/index.html','our-work/petti-pathways/index.html','our-work/pizzeria-coco/index.html','privacy-policy/index.html','services/index.html','sunday-school/index.html','terms-and-conditions/index.html']
for route in routes:
    p = Path(route)
    p.write_text(p.read_text().replace('20260914-17', '20260914-18'))
p = Path('assets/site.js')
p.write_text(p.read_text().replace('20260914-17', '20260914-18'))

# Integrity checks before browser QA.
failures = []
def check(name, ok):
    print(('PASS' if ok else 'FAIL') + ' | ' + name)
    if not ok:
        failures.append(name)

inquiry_text = inquiry.read_text()
home_text = home.read_text()
check('date label hook', 'data-start-date-label' in inquiry_text)
check('calendar opens upward', 'data-date-panel' in inquiry_text and 'bottom:calc(100% + 6px)' in inquiry_text and 'top:auto' in inquiry_text)
check('privacy one-line source', 'data-form-privacy' in inquiry_text and 'white-space:nowrap' in inquiry_text)
check('manual sign swing restored', "sign.addEventListener('click', this._signClick)" in home_text)
check('sign controls excluded', "target.closest('button,a,input,textarea,select')" in home_text)
check('slow swing timing', 'sc-rock 6.2s' in home_text and 'sc-sway 8.5s' in home_text)
check('stronger slow pulse', 'opacity:.72' in home_text and 'sc-neon 5.6s' in home_text)
root = inquiry.read_bytes()
check('local inquiry copies synced', all((Path(d) / 'Inquiry Form.dc.html').read_bytes() == root for d in dirs))
check('all routes v18', all('20260914-18' in Path(r).read_text() and '20260914-17' not in Path(r).read_text() for r in routes))
petti = Path('our-work/petti-pathways/index.html').read_text().lower()
check('Petti teal preserved', '#35807e' in petti and '#2f7472' not in petti)
if failures:
    raise SystemExit(', '.join(failures))
