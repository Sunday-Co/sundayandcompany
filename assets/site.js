(function () {
  'use strict';

  function ensureCorrectionStyles() {
    if (document.querySelector('link[data-sunday-rendered-corrections]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/assets/rendered-corrections.css?v=20260914-18';
    link.setAttribute('data-sunday-rendered-corrections', 'true');
    document.head.appendChild(link);
  }


  var signMotionObserver = null;
  var observedSign = null;
  var signMotionClickBound = false;
  var signMotionRafA = 0;
  var signMotionRafB = 0;

  function reducedMotion() {
    return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  function triggerOriginalOpenSignMotion() {
    if (reducedMotion()) return;
    var root = document.documentElement;
    root.dataset.sundaySignFallback = '0';
    if (signMotionRafA) window.cancelAnimationFrame(signMotionRafA);
    if (signMotionRafB) window.cancelAnimationFrame(signMotionRafB);
    signMotionRafA = window.requestAnimationFrame(function () {
      signMotionRafB = window.requestAnimationFrame(function () {
        root.dataset.sundaySignFallback = '1';
      });
    });
  }

  function ensureOpenSignMotion() {
    var sign = document.querySelector('[data-sign]');
    if (!sign) return;

    if (!('IntersectionObserver' in window)) {
      triggerOriginalOpenSignMotion();
      return;
    }

    if (observedSign === sign && signMotionObserver) return;
    if (signMotionObserver) signMotionObserver.disconnect();
    observedSign = sign;
    signMotionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) triggerOriginalOpenSignMotion();
      });
    }, { threshold: 0.35 });
    signMotionObserver.observe(sign);
  }


  var activeSurface = null;
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

  function applyFormRenderCorrections() {
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
    applyFormRenderCorrections();
    syncAccessibleSurface();
  }

  function boot() {
    ensureCorrectionStyles();
    installAccessibleSurfaceManagement();
    sync();

    var mo = new MutationObserver(function (mutations) {
      var shouldSync = false;
      for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].type === 'attributes') {
          shouldSync = true;
          break;
        }
        if (mutations[i].type === 'childList' && mutations[i].addedNodes.length) {
          shouldSync = true;
          break;
        }
      }
      if (shouldSync) window.requestAnimationFrame(sync);
    });

    mo.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style', 'data-sheet-state', 'aria-hidden', 'aria-modal']
    });
    window.addEventListener('pageshow', sync);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
