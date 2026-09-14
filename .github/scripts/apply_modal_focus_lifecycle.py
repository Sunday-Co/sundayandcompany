from pathlib import Path

path = Path('assets/site.js')
text = path.read_text()

start = text.find('  var activeSurface = null;')
end = text.find('  function sync() {', start)
if start == -1 or end == -1:
    raise SystemExit('Could not locate accessible surface management block')

replacement = r'''  var activeSurface = null;
  var activeSurfaceOpener = null;
  var pendingSurfaceOpener = null;

  function sundayVisible(el) {
    if (!el) return false;
    var s = window.getComputedStyle(el);
    var r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0;
  }

  function sundayCurrentSurface() {
    var dialogs = Array.prototype.slice.call(document.querySelectorAll('[role="dialog"][aria-modal="true"]'));
    for (var i = dialogs.length - 1; i >= 0; i--) {
      if (sundayVisible(dialogs[i])) return dialogs[i];
    }
    /* data-sheet-state is the authoritative menu state. During the opening
       transition visibility can still be changing, so do not require the
       sheet itself to pass the visual test before we start managing focus. */
    return document.querySelector('aside[aria-label="Sunday & Company navigation"][data-sheet-state="open"]');
  }

  function sundayFocusable(root) {
    if (!root) return [];
    return Array.prototype.slice.call(root.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]):not([type="hidden"]),textarea:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])')).filter(sundayVisible);
  }

  function sundayNormalizeText(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  function sundayDescribeOpener(el) {
    if (!el || el === document.body || el === document.documentElement) return null;
    return {
      node: el,
      id: el.id || '',
      ariaLabel: el.getAttribute && (el.getAttribute('aria-label') || ''),
      href: el.getAttribute && (el.getAttribute('href') || ''),
      tag: (el.tagName || '').toLowerCase(),
      text: sundayNormalizeText(el.textContent)
    };
  }

  function sundayResolveOpener(ref) {
    if (!ref) return null;
    if (ref.node && ref.node.isConnected && sundayVisible(ref.node)) return ref.node;
    if (ref.id) {
      var byId = document.getElementById(ref.id);
      if (byId && sundayVisible(byId)) return byId;
    }
    var candidates = Array.prototype.slice.call(document.querySelectorAll('button,a[href],[role="button"],[tabindex]:not([tabindex="-1"])'));
    var i, candidate;
    if (ref.ariaLabel) {
      for (i = 0; i < candidates.length; i++) {
        candidate = candidates[i];
        if (candidate.getAttribute('aria-label') === ref.ariaLabel && sundayVisible(candidate)) return candidate;
      }
    }
    if (ref.href) {
      for (i = 0; i < candidates.length; i++) {
        candidate = candidates[i];
        if (candidate.getAttribute('href') === ref.href && sundayVisible(candidate)) return candidate;
      }
    }
    if (ref.text) {
      for (i = 0; i < candidates.length; i++) {
        candidate = candidates[i];
        if ((!ref.tag || candidate.tagName.toLowerCase() === ref.tag) && sundayNormalizeText(candidate.textContent) === ref.text && sundayVisible(candidate)) return candidate;
      }
    }
    return null;
  }

  function sundayInteractiveTarget(target) {
    return target && target.closest ? target.closest('button,a[href],input,textarea,select,[role="button"],[tabindex]:not([tabindex="-1"])') : null;
  }

  function sundayRememberActivator(event) {
    var candidate = sundayInteractiveTarget(event.target);
    if (!candidate) return;
    var surface = sundayCurrentSurface();
    if (surface && surface.contains(candidate)) return;
    pendingSurfaceOpener = sundayDescribeOpener(candidate);
  }

  function sundayFocusSurface(surface) {
    if (!surface || surface !== activeSurface) return;
    if (surface.contains(document.activeElement)) return;
    var items = sundayFocusable(surface);
    var close = surface.querySelector('button[aria-label="Close"], button[aria-label="Close menu"]');
    var target = close && sundayVisible(close) ? close : items[0];
    if (target && typeof target.focus === 'function') {
      try { target.focus({ preventScroll: true }); } catch (_) { target.focus(); }
    }
  }

  function sundayRestoreOpener(ref) {
    function restore() {
      var target = sundayResolveOpener(ref);
      if (!target || typeof target.focus !== 'function') return;
      try { target.focus({ preventScroll: true }); } catch (_) { target.focus(); }
    }
    window.requestAnimationFrame(restore);
    /* A DC state change can replace the triggering button after the first
       frame. Resolve the opener again after the render settles so desktop
       and mobile both return focus to the current live control. */
    window.setTimeout(restore, 120);
  }

  function syncAccessibleSurface() {
    var next = sundayCurrentSurface();

    if (next === activeSurface) {
      if (next && !next.contains(document.activeElement)) {
        window.requestAnimationFrame(function () { sundayFocusSurface(next); });
      }
      return;
    }

    if (activeSurface && !next) {
      var restore = activeSurfaceOpener;
      activeSurface = null;
      activeSurfaceOpener = null;
      pendingSurfaceOpener = null;
      sundayRestoreOpener(restore);
      return;
    }

    if (next && next !== activeSurface) {
      if (!activeSurface) {
        var current = document.activeElement;
        if (current && current !== document.body && !next.contains(current)) {
          activeSurfaceOpener = sundayDescribeOpener(current);
        } else {
          activeSurfaceOpener = pendingSurfaceOpener;
        }
        pendingSurfaceOpener = null;
      }
      activeSurface = next;
      window.requestAnimationFrame(function () { sundayFocusSurface(next); });
      window.setTimeout(function () { sundayFocusSurface(next); }, 80);
    }
  }

  function installAccessibleSurfaceManagement() {
    document.addEventListener('pointerdown', sundayRememberActivator, true);
    document.addEventListener('click', function (event) {
      sundayRememberActivator(event);
      /* Run after the component click handler has had time to publish its
         new dialog/menu state. A second frame covers the animated nav sheet. */
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(syncAccessibleSurface);
      });
      window.setTimeout(syncAccessibleSurface, 100);
    }, true);

    document.addEventListener('keydown', function (event) {
      var surface = sundayCurrentSurface() || activeSurface;
      if (!surface) return;

      if (event.key === 'Escape') {
        var close = surface.querySelector('button[aria-label="Close"], button[aria-label="Close menu"]');
        if (close) {
          event.preventDefault();
          close.click();
          window.requestAnimationFrame(syncAccessibleSurface);
          window.setTimeout(syncAccessibleSurface, 100);
        }
        return;
      }

      if (event.key !== 'Tab') return;
      var items = sundayFocusable(surface);
      if (!items.length) return;
      var first = items[0], last = items[items.length - 1];
      var current = document.activeElement;
      if (!surface.contains(current)) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus();
        return;
      }
      if (event.shiftKey && current === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && current === last) {
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

text = text[:start] + replacement + text[end:]

old_observer = """    var mo = new MutationObserver(function (mutations) {\n      var shouldSync = false;\n      for (var i = 0; i < mutations.length; i++) {\n        if (mutations[i].type === 'childList' && mutations[i].addedNodes.length) {\n          shouldSync = true;\n          break;\n        }\n      }\n      if (shouldSync) window.requestAnimationFrame(sync);\n    });\n\n    mo.observe(document.documentElement, { childList: true, subtree: true });\n"""
new_observer = """    var mo = new MutationObserver(function (mutations) {\n      var shouldSync = false;\n      for (var i = 0; i < mutations.length; i++) {\n        if (mutations[i].type === 'attributes') {\n          shouldSync = true;\n          break;\n        }\n        if (mutations[i].type === 'childList' && mutations[i].addedNodes.length) {\n          shouldSync = true;\n          break;\n        }\n      }\n      if (shouldSync) window.requestAnimationFrame(sync);\n    });\n\n    mo.observe(document.documentElement, {\n      childList: true,\n      subtree: true,\n      attributes: true,\n      attributeFilter: ['style', 'data-sheet-state', 'aria-hidden', 'aria-modal']\n    });\n"""
if old_observer not in text:
    raise SystemExit('Could not locate MutationObserver block')
text = text.replace(old_observer, new_observer, 1)

path.write_text(text)
print('Updated accessible surface lifecycle with activator capture, rerender-safe focus restoration, animated menu focus entry, Tab containment, and Escape handling.')
