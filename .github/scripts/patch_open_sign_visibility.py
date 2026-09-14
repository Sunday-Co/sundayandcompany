from pathlib import Path

p = Path('assets/site.js')
s = p.read_text()

vars_old = """  var signMotionClickBound = false;
  var signMotionRafA = 0;
  var signMotionRafB = 0;
"""
vars_new = """  var signMotionClickBound = false;
  var signMotionRafA = 0;
  var signMotionRafB = 0;
  var signMotionVisible = false;
  var signMotionScrollBound = false;
  var signMotionVisibilityRaf = 0;
  var signMotionPoll = 0;
"""
if 'var signMotionVisibilityRaf = 0;' not in s:
    if vars_old not in s:
        raise SystemExit('sign motion vars marker missing')
    s = s.replace(vars_old, vars_new, 1)
elif 'var signMotionPoll = 0;' not in s:
    s = s.replace('  var signMotionVisibilityRaf = 0;\n', '  var signMotionVisibilityRaf = 0;\n  var signMotionPoll = 0;\n', 1)

marker = """  function ensureOpenSignMotion() {
"""
helpers = """  function sundaySignVisibleEnough(sign) {
    if (!sign) return false;
    var rect = sign.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight || 0;
    var visibleHeight = Math.min(rect.bottom, vh) - Math.max(rect.top, 0);
    var threshold = Math.min(rect.height * 0.35, 120);
    return rect.height > 0 && visibleHeight >= Math.max(1, threshold);
  }

  function syncOpenSignVisibility() {
    var sign = observedSign || document.querySelector('[data-sign]');
    var visible = sundaySignVisibleEnough(sign);
    if (visible && !signMotionVisible) triggerOriginalOpenSignMotion();
    signMotionVisible = visible;
  }

  function scheduleOpenSignVisibility() {
    if (signMotionVisibilityRaf) return;
    signMotionVisibilityRaf = window.requestAnimationFrame(function () {
      signMotionVisibilityRaf = 0;
      syncOpenSignVisibility();
    });
  }

  function ensureOpenSignPolling() {
    if (signMotionPoll) return;
    signMotionPoll = window.setInterval(syncOpenSignVisibility, 100);
  }

  function ensureOpenSignMotion() {
"""
if 'function sundaySignVisibleEnough(sign)' not in s:
    if marker not in s:
        raise SystemExit('ensureOpenSignMotion marker missing')
    s = s.replace(marker, helpers, 1)
elif 'function ensureOpenSignPolling()' not in s:
    s = s.replace('  function ensureOpenSignMotion() {\n', "  function ensureOpenSignPolling() {\n    if (signMotionPoll) return;\n    signMotionPoll = window.setInterval(syncOpenSignVisibility, 100);\n  }\n\n  function ensureOpenSignMotion() {\n", 1)

sign_marker = """    var sign = document.querySelector('[data-sign]');
    if (!sign) return;

"""
sign_insert = """    var sign = document.querySelector('[data-sign]');
    if (!sign) return;

    ensureOpenSignPolling();
    if (!signMotionScrollBound) {
      window.addEventListener('scroll', scheduleOpenSignVisibility, { passive: true });
      window.addEventListener('resize', scheduleOpenSignVisibility);
      signMotionScrollBound = true;
    }

"""
if 'ensureOpenSignPolling();' not in s:
    if sign_marker not in s:
        raise SystemExit('sign lookup marker missing')
    s = s.replace(sign_marker, sign_insert, 1)
elif "window.addEventListener('scroll', scheduleOpenSignVisibility" not in s:
    if sign_marker not in s:
        raise SystemExit('sign lookup marker missing')
    s = s.replace(sign_marker, sign_insert, 1)

click_old = """    if (!signMotionClickBound) {
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
click_new = """    if (!signMotionClickBound) {
      document.addEventListener('pointerdown', function (event) {
        var target = event.target;
        var hit = target && target.closest ? target.closest('[data-sign]') : null;
        if (!hit) return;
        if (target.closest && target.closest('button,a[href],input,textarea,select')) return;
        triggerOriginalOpenSignMotion();
      }, { passive: true });
      signMotionClickBound = true;
    }
"""
if "document.addEventListener('pointerdown', function (event)" not in s:
    if click_old not in s:
        raise SystemExit('manual sign trigger marker missing')
    s = s.replace(click_old, click_new, 1)

same_old = """    if (observedSign === sign && signMotionObserver) return;
"""
same_new = """    if (observedSign === sign && signMotionObserver) {
      scheduleOpenSignVisibility();
      return;
    }
"""
if same_old in s:
    s = s.replace(same_old, same_new, 1)

observer_old = """    observedSign = sign;
    signMotionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) triggerOriginalOpenSignMotion();
      });
    }, { threshold: 0.35 });
    signMotionObserver.observe(sign);
"""
observer_new = """    observedSign = sign;
    signMotionVisible = false;
    signMotionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.target !== observedSign) return;
        var visible = entry.isIntersecting && entry.intersectionRatio > 0;
        if (visible && !signMotionVisible) triggerOriginalOpenSignMotion();
        signMotionVisible = visible;
      });
    }, { threshold: [0, 0.2, 0.35] });
    signMotionObserver.observe(sign);
    scheduleOpenSignVisibility();
"""
if 'threshold: [0, 0.2, 0.35]' not in s:
    if observer_old not in s:
        raise SystemExit('sign observer marker missing')
    s = s.replace(observer_old, observer_new, 1)

p.write_text(s)

checks = {
    'scroll visibility fallback': "window.addEventListener('scroll', scheduleOpenSignVisibility" in s,
    'poll visibility fallback': 'window.setInterval(syncOpenSignVisibility, 100)' in s,
    'viewport geometry check': 'function sundaySignVisibleEnough(sign)' in s,
    'observer and fallback share state': 'signMotionVisible = visible;' in s,
    'multi-threshold observer': 'threshold: [0, 0.2, 0.35]' in s,
    'manual sign trigger uses pointerdown': "document.addEventListener('pointerdown', function (event)" in s,
}
failed = []
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ' | ' + name)
    if not ok:
        failed.append(name)
if failed:
    raise SystemExit('Failed: ' + ', '.join(failed))
