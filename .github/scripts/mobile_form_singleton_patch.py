from pathlib import Path

p = Path('assets/site.js')
s = p.read_text()
marker = "  'use strict';\n\n"
guard = """  'use strict';

  /* This shared file can be referenced through more than one DC component
     path. Run the behavior layer only once so modal/body locks cannot stack. */
  if (window.__sundaySharedRuntimeLoaded) return;
  window.__sundaySharedRuntimeLoaded = true;

"""
if 'window.__sundaySharedRuntimeLoaded = true;' not in s:
    if marker not in s:
        raise SystemExit('site.js strict-mode marker missing')
    s = s.replace(marker, guard, 1)
p.write_text(s)

ok = s.count('window.__sundaySharedRuntimeLoaded = true;') == 1
print(('PASS' if ok else 'FAIL') + ' | shared Sunday runtime is singleton-guarded')
if not ok:
    raise SystemExit('runtime singleton guard invalid')
