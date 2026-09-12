(function () {
  'use strict';

  function ensureCorrectionStyles() {
    if (document.querySelector('link[data-sunday-rendered-corrections]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/assets/rendered-corrections.css?v=20260912-10';
    link.setAttribute('data-sunday-rendered-corrections', 'true');
    document.head.appendChild(link);
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

  function normalizeFooterTypography() {
    document.querySelectorAll('a[data-footer-ui][href="mailto:hello@sundayandcompany.co"], footer [data-footer-location], footer a[data-footer-ui]').forEach(function (node) {
      node.style.setProperty('font-family', "'Inter Tight', Arial, sans-serif", 'important');
      node.style.setProperty('font-size', '12.5px', 'important');
      node.style.setProperty('font-weight', '300', 'important');
      node.style.setProperty('letter-spacing', '.01em', 'important');
      node.style.setProperty('line-height', '1.4', 'important');
      node.style.setProperty('opacity', '1', 'important');
    });
  }

  function prepareImagesForCapture(scope) {
    var root = scope && scope.querySelectorAll ? scope : document;
    root.querySelectorAll('img').forEach(function (img) {
      img.loading = 'eager';
      img.decoding = 'sync';
      img.setAttribute('data-sunday-capture-ready', 'true');
    });
  }

  function markHeroFallbacks() {
    document.querySelectorAll('section#top, section[data-screen-hero]').forEach(function (hero) {
      var img = hero.querySelector(':scope > img, :scope > div:first-child img');
      if (!img) return;

      hero.setAttribute('data-hero-fallback', 'ready');
      img.setAttribute('data-sunday-hero-img', 'true');
      img.loading = 'eager';
      img.decoding = 'sync';
      try { img.fetchPriority = 'high'; } catch (e) {}

      if (img.parentElement === hero) hero.setAttribute('data-sunday-grid-hero', 'true');
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

  function sync() {
    ensureCorrectionStyles();
    normalizeRuntimeRoots();
    normalizeFooterTypography();
    prepareImagesForCapture(document);
    markHeroFallbacks();
    ensureOpenSignMotion();
  }

  function boot() {
    ensureCorrectionStyles();
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
    window.addEventListener('resize', function () {
      normalizeRuntimeRoots();
      normalizeFooterTypography();
    }, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
