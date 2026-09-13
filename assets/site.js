(function () {
  'use strict';

  function ensureCorrectionStyles() {
    if (document.querySelector('link[data-sunday-rendered-corrections]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/assets/rendered-corrections.css?v=20260913-14';
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

    if (!signMotionClickBound) {
      document.addEventListener('click', function (event) {
        var target = event.target;
        if (target && target.closest && target.closest('[data-sign]')) {
          triggerOriginalOpenSignMotion();
        }
      });
      signMotionClickBound = true;
    }

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

  function sync() {
    ensureCorrectionStyles();
    ensureOpenSignMotion();
    syncAccessibleSurface();
  }

  function boot() {
    ensureCorrectionStyles();
    installAccessibleSurfaceManagement();
    sync();

    var mo = new MutationObserver(function (mutations) {
      var shouldSync = false;
      for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].type === 'childList' && mutations[i].addedNodes.length) {
          shouldSync = true;
          break;
        }
      }
      if (shouldSync) window.requestAnimationFrame(sync);
    });

    mo.observe(document.documentElement, { childList: true, subtree: true });
    window.addEventListener('pageshow', sync);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
