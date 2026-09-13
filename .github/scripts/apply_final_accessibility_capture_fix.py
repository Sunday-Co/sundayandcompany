from pathlib import Path
import re

ROOT = Path('.')

# 1) Shared header sources: reliable skip link target.
for p in ROOT.rglob('Site Header.dc.html'):
    text = p.read_text(encoding='utf-8')
    text = text.replace('href="#top" style="background:#311d03;color:#f5efe6;font-family:\'Inter Tight\'', 'href="#main-content" style="background:#311d03;color:#f5efe6;font-family:\'Inter Tight\'')
    p.write_text(text, encoding='utf-8')

# 2) Public pages: add a semantic main landmark between shared header/footer imports.
public_pages = [ROOT / '404.html'] + sorted(ROOT.rglob('index.html'))
for p in public_pages:
    text = p.read_text(encoding='utf-8')
    if '<main id="main-content"' not in text and 'name="/Site Header"' in text and 'name="/Site Footer"' in text:
        header_match = re.search(r'(<dc-import\s+name="/Site Header"[^>]*></dc-import>)', text)
        footer_match = re.search(r'(<dc-import\s+name="/Site Footer"[^>]*></dc-import>)', text)
        if header_match and footer_match and header_match.end() < footer_match.start():
            text = text[:header_match.end()] + '\n\n  <main id="main-content" tabindex="-1">' + text[header_match.end():footer_match.start()] + '  </main>\n\n  ' + text[footer_match.start():]
    p.write_text(text, encoding='utf-8')

# 3) Homepage hero: make the real IMG define the hero height in normal document flow.
# This avoids relying on a percentage-height image layer during Safari's Full Page compositor pass.
home = ROOT / 'index.html'
text = home.read_text(encoding='utf-8')
text = text.replace(
    'src="/assets/hero-landscape.jpg" alt="Open laptop, glasses and coffee on a Sunday &amp; Company workspace" fetchpriority="high" style="height:100%;inset:0;object-fit:cover;object-position:50% 48%;display:block;position:static;width:100%" data-sunday-static-hero="true"',
    'src="/assets/hero-landscape.jpg" alt="Open laptop, glasses and coffee on a Sunday &amp; Company workspace" fetchpriority="high" decoding="sync" style="display:block;height:auto;object-fit:cover;object-position:50% 48%;position:relative;width:100%;z-index:0" data-sunday-static-hero="true"'
)
home.write_text(text, encoding='utf-8')

# 4) Shared footer: announce successful newsletter state without changing visual layout.
for p in ROOT.rglob('Site Footer.dc.html'):
    text = p.read_text(encoding='utf-8')
    text = text.replace('<div data-news-receipt style=', '<div data-news-receipt role="status" aria-live="polite" style=')
    p.write_text(text, encoding='utf-8')

# 5) Shared header inquiry success announcement.
for p in ROOT.rglob('Site Header.dc.html'):
    text = p.read_text(encoding='utf-8')
    text = text.replace('<div style="display:{{ inqDoneDisplay }};', '<div role="status" aria-live="polite" style="display:{{ inqDoneDisplay }};')
    p.write_text(text, encoding='utf-8')

# 6) Shared CSS: one source-owned block for mobile readability, focus, touch targets, and flow-based hero capture.
css_path = ROOT / 'assets/site.css'
css = css_path.read_text(encoding='utf-8')
css = css.replace('font-size: 7.5px !important;\n  font-weight: 300 !important;\n  letter-spacing: .045em !important;', 'font-size: 8.25px !important;\n  font-weight: 300 !important;\n  letter-spacing: .035em !important;')
marker = '/* FINAL ACCESSIBILITY + SAFARI FULL-PAGE SOURCE ALIGNMENT · 2026-09-13 */'
if marker not in css:
    css += '''\n\n/* FINAL ACCESSIBILITY + SAFARI FULL-PAGE SOURCE ALIGNMENT · 2026-09-13 */\n\n/* Keep the homepage hero image in normal flow so Safari Full Page paints the image,\n   while preserving the same visual height used by the hero container. */\nsection#top[data-screen-hero="home"] {\n  height: auto !important;\n  min-height: 0 !important;\n  overflow: hidden !important;\n}\nsection#top[data-screen-hero="home"] > img[data-sunday-static-hero="true"] {\n  display: block !important;\n  height: clamp(680px, 66.5vw, 900px) !important;\n  max-width: none !important;\n  object-fit: cover !important;\n  object-position: 50% 48% !important;\n  opacity: 1 !important;\n  position: relative !important;\n  transform: none !important;\n  width: 100% !important;\n  -webkit-print-color-adjust: exact !important;\n  print-color-adjust: exact !important;\n}\n@media (max-width: 700px) {\n  section#top[data-screen-hero="home"] > img[data-sunday-static-hero="true"] {\n    height: clamp(680px, 185vw, 820px) !important;\n  }\n}\n\n/* Keep utility copy editorial but readable on a phone. */\n@media (max-width: 700px) {\n  [aria-label="Newsletter"] [data-news-fineprint] {\n    font-size: 8.25px !important;\n    letter-spacing: .035em !important;\n    line-height: 1.5 !important;\n  }\n  footer [data-footer-legal] {\n    line-height: 1.55 !important;\n  }\n}\n\n/* Small visual controls keep their design size but receive a usable touch target. */\n@media (pointer: coarse) {\n  button[aria-label="Close"],\n  button[aria-label="Open menu"],\n  button[aria-label="Close menu"],\n  footer a[aria-label],\n  header a[aria-label="Instagram"],\n  header a[aria-label="TikTok"],\n  header a[aria-label="LinkedIn"] {\n    min-height: 44px !important;\n    min-width: 44px !important;\n  }\n}\n\n/* Program archive microtype remains small, but not sub-legible. */\n[role="dialog"][aria-label="The Fellows Table"]::after,\n[role="dialog"][aria-label="The Espresso Club"]::after,\n[role="dialog"][aria-label="The Founders Club"]::after {\n  font-size: 8px !important;\n}\n@media (max-width: 720px) {\n  [role="dialog"][aria-label="The Fellows Table"]::after,\n  [role="dialog"][aria-label="The Espresso Club"]::after,\n  [role="dialog"][aria-label="The Founders Club"]::after {\n    font-size: 7.5px !important;\n  }\n}\n'''
css_path.write_text(css, encoding='utf-8')

# 7) Shared runtime: keyboard/focus management only. No visual/motion changes.
js_path = ROOT / 'assets/site.js'
js = js_path.read_text(encoding='utf-8')
focus_marker = 'function installAccessibleSurfaceManagement()'
if focus_marker not in js:
    insert = r'''

  var activeSurface = null;
  var activeSurfaceOpener = null;

  function sundayVisible(el) {
    if (!el) return false;
    var s = window.getComputedStyle(el);
    var r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
  }

  function sundayCurrentSurface() {
    var dialogs = Array.prototype.slice.call(document.querySelectorAll('[role="dialog"][aria-modal="true"], [role="dialog"][aria-modal="true"]'));
    for (var i = dialogs.length - 1; i >= 0; i--) if (sundayVisible(dialogs[i])) return dialogs[i];
    var sheet = document.querySelector('aside[aria-label="Sunday & Company navigation"][data-sheet-state="open"]');
    return sundayVisible(sheet) ? sheet : null;
  }

  function sundayFocusable(root) {
    if (!root) return [];
    return Array.prototype.slice.call(root.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]):not([type="hidden"]),textarea:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])')).filter(sundayVisible);
  }

  function syncAccessibleSurface() {
    var next = sundayCurrentSurface();
    if (next === activeSurface) return;

    if (activeSurface && !next) {
      var restore = activeSurfaceOpener;
      activeSurface = null;
      activeSurfaceOpener = null;
      if (restore && restore.isConnected && typeof restore.focus === 'function') {
        window.requestAnimationFrame(function () { try { restore.focus({ preventScroll: true }); } catch (_) { restore.focus(); } });
      }
      return;
    }

    if (next && next !== activeSurface) {
      var current = document.activeElement;
      if (current && current !== document.body && !next.contains(current)) activeSurfaceOpener = current;
      activeSurface = next;
      window.requestAnimationFrame(function () {
        if (activeSurface !== next) return;
        var items = sundayFocusable(next);
        var target = next.querySelector('button[aria-label="Close"], button[aria-label="Close menu"]') || items[0];
        if (target && typeof target.focus === 'function') target.focus();
      });
    }
  }

  function installAccessibleSurfaceManagement() {
    document.addEventListener('keydown', function (event) {
      var surface = sundayCurrentSurface();
      if (!surface) return;

      if (event.key === 'Escape') {
        var close = surface.querySelector('button[aria-label="Close"], button[aria-label="Close menu"]');
        if (close) {
          event.preventDefault();
          close.click();
        }
        return;
      }

      if (event.key !== 'Tab') return;
      var items = sundayFocusable(surface);
      if (!items.length) return;
      var first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }, true);

    document.addEventListener('click', function (event) {
      var link = event.target && event.target.closest ? event.target.closest('a[href="#main-content"]') : null;
      if (!link) return;
      var main = document.getElementById('main-content');
      if (!main) return;
      window.requestAnimationFrame(function () {
        main.focus({ preventScroll: true });
        main.scrollIntoView({ block: 'start' });
      });
    });
  }
'''
    js = js.replace('\n  function sync() {', insert + '\n  function sync() {')
    js = js.replace('    ensureOpenSignMotion();\n  }', '    ensureOpenSignMotion();\n    syncAccessibleSurface();\n  }')
    js = js.replace('    ensureCorrectionStyles();\n    sync();', '    ensureCorrectionStyles();\n    installAccessibleSurfaceManagement();\n    sync();')
js_path.write_text(js, encoding='utf-8')

# 8) Keep original portfolio movement but avoid forcing full video download before metadata is available.
for p in sorted((ROOT / 'our-work').rglob('index.html')):
    text = p.read_text(encoding='utf-8')
    text = text.replace('preload="auto"', 'preload="metadata"')
    p.write_text(text, encoding='utf-8')

# 9) Bump shared asset query version across public HTML and the JS fallback link.
for p in public_pages:
    text = p.read_text(encoding='utf-8')
    text = re.sub(r'/assets/site\.css\?v=[0-9-]+', '/assets/site.css?v=20260913-14', text)
    text = re.sub(r'/assets/rendered-corrections\.css\?v=[0-9-]+', '/assets/rendered-corrections.css?v=20260913-14', text)
    text = re.sub(r'/assets/site\.js\?v=[0-9-]+', '/assets/site.js?v=20260913-14', text)
    p.write_text(text, encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
js = re.sub(r'/assets/rendered-corrections\.css\?v=[0-9-]+', '/assets/rendered-corrections.css?v=20260913-14', js)
js_path.write_text(js, encoding='utf-8')

print('Applied final accessibility, focus, footer readability, and Safari full-page source corrections.')
