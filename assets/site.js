(function () {
  'use strict';

  function ensureCorrectionStyles() {
    if (document.querySelector('link[data-sunday-rendered-corrections]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/assets/rendered-corrections.css?v=20260912-11';
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

  function sync() {
    ensureCorrectionStyles();
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
