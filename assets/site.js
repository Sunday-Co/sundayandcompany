(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var observer = null;
  var revealed = new WeakSet();
  var mediaAnimated = new WeakSet();

  function markHeroFallbacks() {
    document.querySelectorAll('section#top, section[data-screen-hero]').forEach(function (hero) {
      var img = hero.querySelector(':scope > img, :scope > div:first-child img');
      if (!img) return;
      hero.setAttribute('data-hero-fallback', 'ready');
      if (hero.closest('[data-screen-label="Home"]')) hero.setAttribute('data-screen-hero', 'home');
      var src = img.getAttribute('src');
      if (src && !hero.style.backgroundImage) hero.style.backgroundImage = 'url("' + src.replace(/"/g, '\\"') + '")';
      if (!hero.style.backgroundPosition && img.style.objectPosition) hero.style.backgroundPosition = img.style.objectPosition;
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

  function stabilizeCaptureUI() {
    normalizeRuntimeRoots();
    document.querySelectorAll('aside[aria-label="Sunday & Company navigation"][data-sheet-state]').forEach(function (sheet) {
      var open = sheet.getAttribute('data-sheet-state') === 'open';
      if (open) sheet.style.display = 'flex';
      else {
        sheet.style.display = 'none';
        sheet.style.visibility = 'hidden';
        sheet.style.transform = 'none';
      }
    });
  }

  function getRevealNodes() {
    return Array.prototype.slice.call(document.querySelectorAll('[data-screen-label] > section, main section'))
      .filter(function (node) {
        return node.id !== 'top' && !node.closest('[role="dialog"]') && node.offsetHeight > 80;
      });
  }

  function animateEditorialMedia(node) {
    if (reduce || !Element.prototype.animate) return;
    Array.prototype.forEach.call(node.querySelectorAll('img'), function (img) {
      if (mediaAnimated.has(img)) return;
      if (img.closest('header, footer, [role="dialog"], [aria-label="Sunday & Company navigation"]')) return;
      if ((img.naturalWidth && img.naturalWidth < 420) || (img.naturalHeight && img.naturalHeight < 260)) return;
      mediaAnimated.add(img);
      img.animate([
        { opacity: 0.94, transform: 'scale(1.012)', clipPath: 'inset(0 0 7% 0)' },
        { opacity: 1, transform: 'scale(1)', clipPath: 'inset(0 0 0 0)' }
      ], { duration: 520, easing: 'cubic-bezier(.22,.75,.18,1)', fill: 'both' });
    });
  }

  function revealSections() {
    var nodes = getRevealNodes();
    if (!nodes.length) return false;

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
          void node.offsetWidth;
          window.requestAnimationFrame(function () {
            node.classList.add('sc-in');
            animateEditorialMedia(node);
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
    stabilizeCaptureUI();
    markHeroFallbacks();
    revealSections();
  }

  function boot() {
    sync();
    var mo = new MutationObserver(function () { sync(); });
    mo.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['data-sheet-state']
    });
    window.setTimeout(function () {
      sync();
      mo.disconnect();
    }, 4000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
