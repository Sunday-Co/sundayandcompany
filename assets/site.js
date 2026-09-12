(function () {
  'use strict';

  var motionQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var reduce = !!(motionQuery && motionQuery.matches);
  var observer = null;
  var revealed = new WeakSet();
  var menuTimers = new WeakMap();

  function ensureCorrectionStyles() {
    if (document.querySelector('link[data-sunday-rendered-corrections]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/assets/rendered-corrections.css?v=20260912-7';
    link.setAttribute('data-sunday-rendered-corrections', 'true');
    document.head.appendChild(link);
  }

  function markHeroFallbacks() {
    document.querySelectorAll('section#top, section[data-screen-hero]').forEach(function (hero) {
      var img = hero.querySelector(':scope > img, :scope > div:first-child img');
      if (!img) return;
      hero.setAttribute('data-hero-fallback', 'ready');
      if (hero.closest('[data-screen-label="Home"]')) hero.setAttribute('data-screen-hero', 'home');
      var src = img.getAttribute('src');
      if (src && !hero.style.backgroundImage) {
        hero.style.backgroundImage = 'url("' + src.replace(/"/g, '\\"') + '")';
      }
      if (!hero.style.backgroundPosition && img.style.objectPosition) {
        hero.style.backgroundPosition = img.style.objectPosition;
      }
    });
  }

  function markProgramShells() {
    document.querySelectorAll('[data-program-cards]').forEach(function (grid) {
      var shell = grid.parentElement;
      if (shell) shell.setAttribute('data-program-shell', 'true');
    });
  }

  function normalizeRuntimeRoots() {
    var root = document.documentElement;
    root.style.setProperty('height', 'auto', 'important');
    root.style.setProperty('min-height', '100%', 'important');
    root.style.setProperty('max-width', '100%', 'important');
    root.style.setProperty('overflow-x', 'hidden', 'important');

    if (document.body) {
      document.body.style.setProperty('height', 'auto', 'important');
      document.body.style.setProperty('min-height', '100%', 'important');
      document.body.style.setProperty('max-width', '100%', 'important');
      document.body.style.setProperty('overflow-x', 'hidden', 'important');
      if (!document.body.style.backgroundColor) document.body.style.backgroundColor = '#f5efe6';
    }

    document.querySelectorAll('#dc-root, #dc-root > .sc-host').forEach(function (node) {
      node.style.setProperty('height', 'auto', 'important');
      node.style.setProperty('min-height', '100%', 'important');
      node.style.setProperty('max-width', '100%', 'important');
      node.style.setProperty('overflow-x', 'hidden', 'important');
    });
  }

  function hideSheetNow(sheet) {
    var timer = menuTimers.get(sheet);
    if (timer) window.clearTimeout(timer);
    sheet.style.display = 'none';
    sheet.style.visibility = 'hidden';
    sheet.style.transform = 'none';
    sheet.style.pointerEvents = 'none';
    sheet.dataset.sundayWasOpen = '0';
  }

  function openSheetAnimated(sheet) {
    var timer = menuTimers.get(sheet);
    if (timer) window.clearTimeout(timer);

    sheet.style.display = 'flex';
    sheet.style.visibility = 'visible';
    sheet.style.pointerEvents = 'auto';

    if (reduce) {
      sheet.style.transform = 'translateX(0)';
      sheet.dataset.sundayWasOpen = '1';
      return;
    }

    if (sheet.dataset.sundayWasOpen !== '1') {
      sheet.style.transition = 'none';
      sheet.style.transform = 'translateX(102%)';
      void sheet.offsetWidth;
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          if (sheet.getAttribute('data-sheet-state') !== 'open') return;
          sheet.style.transition = 'transform 760ms cubic-bezier(.22,.68,.18,1), visibility 760ms';
          sheet.style.transform = 'translateX(0)';
        });
      });
    } else {
      sheet.style.transform = 'translateX(0)';
    }
    sheet.dataset.sundayWasOpen = '1';
  }

  function closeSheetAnimated(sheet) {
    if (!sheet.dataset.sundaySheetReady) {
      sheet.dataset.sundaySheetReady = '1';
      hideSheetNow(sheet);
      return;
    }

    if (sheet.dataset.sundayWasOpen !== '1' || reduce) {
      hideSheetNow(sheet);
      return;
    }

    sheet.style.display = 'flex';
    sheet.style.visibility = 'visible';
    sheet.style.pointerEvents = 'none';
    sheet.style.transition = 'transform 700ms cubic-bezier(.22,.68,.18,1), visibility 700ms';
    sheet.style.transform = 'translateX(102%)';

    var timer = window.setTimeout(function () {
      if (sheet.getAttribute('data-sheet-state') === 'closed') hideSheetNow(sheet);
    }, 740);
    menuTimers.set(sheet, timer);
  }

  function stabilizeCaptureUI() {
    normalizeRuntimeRoots();

    document.querySelectorAll('aside[aria-label="Sunday & Company navigation"][data-sheet-state]').forEach(function (sheet) {
      var open = sheet.getAttribute('data-sheet-state') === 'open';
      if (!sheet.dataset.sundaySheetReady) sheet.dataset.sundaySheetReady = '1';
      if (open) openSheetAnimated(sheet);
      else if (sheet.dataset.sundayWasOpen === '1') closeSheetAnimated(sheet);
      else hideSheetNow(sheet);
    });
  }

  function getRevealNodes() {
    return Array.prototype.slice.call(document.querySelectorAll('[data-screen-label] > section, main section'))
      .filter(function (node) {
        return !node.closest('[role="dialog"]') && node.offsetHeight > 80;
      });
  }

  function animatePinyon(node) {
    if (reduce || !Element.prototype.animate) return;
    var accents = node.querySelectorAll('[style*="Pinyon Script"], [style*="Pinyon"]');
    Array.prototype.forEach.call(accents, function (accent, index) {
      accent.animate([
        { opacity: 0.42, transform: 'translateY(6px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], {
        duration: 1450,
        delay: 220 + (index * 70),
        easing: 'cubic-bezier(.22,.68,.18,1)',
        fill: 'both'
      });
    });
  }

  function animateSection(node) {
    if (reduce || !Element.prototype.animate) return;
    node.animate([
      { opacity: 0.5, transform: 'translateY(9px)' },
      { opacity: 1, transform: 'translateY(0)' }
    ], {
      duration: 1300,
      easing: 'cubic-bezier(.22,.68,.18,1)',
      fill: 'both'
    });
    animatePinyon(node);
  }

  function revealSections() {
    var nodes = getRevealNodes();
    if (!nodes.length) return false;

    if (reduce || !('IntersectionObserver' in window)) {
      nodes.forEach(function (node) {
        node.style.opacity = '1';
        node.style.transform = 'none';
      });
      return true;
    }

    if (!observer) {
      observer = new IntersectionObserver(function (entries, io) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var node = entry.target;
          animateSection(node);
          io.unobserve(node);
        });
      }, { rootMargin: '0px 0px -5% 0px', threshold: 0.10 });
    }

    nodes.forEach(function (node) {
      if (revealed.has(node)) return;
      revealed.add(node);
      observer.observe(node);
    });
    return true;
  }

  function sync() {
    ensureCorrectionStyles();
    stabilizeCaptureUI();
    markHeroFallbacks();
    markProgramShells();
    revealSections();
  }

  function boot() {
    ensureCorrectionStyles();
    sync();

    var mo = new MutationObserver(function (mutations) {
      var shouldSync = false;
      for (var i = 0; i < mutations.length; i++) {
        var m = mutations[i];
        if (m.type === 'childList' && (m.addedNodes.length || m.removedNodes.length)) {
          shouldSync = true;
          break;
        }
        if (m.type === 'attributes' && m.attributeName === 'data-sheet-state') {
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
      attributeFilter: ['data-sheet-state']
    });

    window.addEventListener('pageshow', sync);
    window.addEventListener('resize', normalizeRuntimeRoots, { passive: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
