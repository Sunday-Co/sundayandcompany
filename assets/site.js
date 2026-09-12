(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var observer = null;
  var revealed = new WeakSet();

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

  function getRevealNodes() {
    return Array.prototype.slice.call(document.querySelectorAll('[data-screen-label] > section, main section'))
      .filter(function (node) {
        return node.id !== 'top' && !node.closest('[role="dialog"]') && node.offsetHeight > 80;
      });
  }

  function revealSections() {
    var nodes = getRevealNodes();
    if (!nodes.length) return false;

    /* Full-page capture safety: offscreen sections stay fully visible in the
       document until they actually approach the viewport. That means Safari/
       WebKit full-page screenshots never capture large blank blocks simply
       because IntersectionObserver has not scrolled through the page. */
    if (reduce || !('IntersectionObserver' in window)) {
      nodes.forEach(function (node) {
        node.classList.remove('sc-reveal');
        node.classList.add('sc-in');
      });
      return true;
    }

    if (!observer) {
      observer = new IntersectionObserver(function (entries, io) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var node = entry.target;
          node.classList.add('sc-reveal');
          /* Force the initial paper position to exist for one frame, then
             reveal. The class is not added while the section is offscreen. */
          void node.offsetWidth;
          window.requestAnimationFrame(function () {
            node.classList.add('sc-in');
          });
          io.unobserve(node);
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    }

    nodes.forEach(function (node) {
      if (revealed.has(node)) return;
      revealed.add(node);
      observer.observe(node);
    });
    return true;
  }

  function sync() {
    markHeroFallbacks();
    revealSections();
  }

  function boot() {
    sync();

    // The DC runtime mounts page/component markup after the document itself loads.
    // Watch briefly for those mounts so motion and hero fallbacks always bind to
    // the rendered site instead of depending on script timing.
    var root = document.documentElement;
    var mo = new MutationObserver(function () { sync(); });
    mo.observe(root, { childList: true, subtree: true });
    window.setTimeout(function () {
      sync();
      mo.disconnect();
    }, 2500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
