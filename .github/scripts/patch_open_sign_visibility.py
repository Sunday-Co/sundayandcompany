from pathlib import Path

p = Path('assets/site.js')
s = p.read_text()
old = """  function triggerOriginalOpenSignMotion() {
    if (reducedMotion()) return;
    var root = document.documentElement;
    root.dataset.sundaySignFallback = '0';
    if (signMotionRafA) window.cancelAnimationFrame(signMotionRafA);
"""
new = """  function triggerOriginalOpenSignMotion() {
    if (reducedMotion()) return;
    var root = document.documentElement;
    var sign = document.querySelector('[data-sign]');
    root.dataset.sundaySignFallback = '0';
    if (sign) void sign.offsetWidth;
    if (signMotionRafA) window.cancelAnimationFrame(signMotionRafA);
"""
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('OPEN sign restart marker missing')
p.write_text(s)

ok = "var sign = document.querySelector('[data-sign]');" in s and 'if (sign) void sign.offsetWidth;' in s
print(('PASS' if ok else 'FAIL') + ' | force layout between OPEN sign animation reset and restart')
if not ok:
    raise SystemExit('OPEN sign forced restart patch missing')
