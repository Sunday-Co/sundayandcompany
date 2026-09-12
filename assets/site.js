(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function markHeroFallbacks() {
    document.querySelectorAll('section#top').forEach(function (hero) {
      var img = hero.querySelector(':scope > img');
      if (!img) return;
      hero.setAttribute('data-hero-fallback', 'ready');
      if (hero.closest('[data-screen-label="Home"]')) hero.setAttribute('data-screen-hero', 'home');
      var src = img.getAttribute('src');
      if (src && !hero.style.backgroundImage) hero.style.backgroundImage = 'url("' + src.replace(/"/g, '\\"') + '")';
      if (!hero.style.backgroundPosition && img.style.objectPosition) hero.style.backgroundPosition = img.style.objectPosition;
    });
  }

  function revealSections() {
    if (reduce || !('IntersectionObserver' in window)) return;
    var nodes = Array.prototype.slice.call(document.querySelectorAll('main section, [data-screen-label] > section'))
      .filter(function (node) {
        return node.id !== 'top' && !node.closest('[role="dialog"]') && node.offsetHeight > 80;
      });
    nodes.forEach(function (node) { node.classList.add('sc-reveal'); });
    var io = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('sc-in');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    nodes.forEach(function (node) { io.observe(node); });
  }

  function boot() {
    markHeroFallbacks();
    revealSections();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
