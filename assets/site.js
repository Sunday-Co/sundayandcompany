(function () {
  'use strict';

  function ensureCorrectionStyles() {
    if (document.querySelector('link[data-sunday-rendered-corrections]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/assets/rendered-corrections.css?v=20260928-03';
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

  function sundayFieldLabel(form, control) {
    if (!form || !control) return '';

    var label = '';
    var wrap = control.closest && control.closest('label');
    if (wrap) {
      var wrapText = wrap.querySelector('span');
      label = sundayNormalizeText((wrapText || wrap).textContent);
    }

    if (!label && control.id) {
      var external = form.querySelector('label[for="' + control.id.replace(/"/g, '\\"') + '"]');
      if (external) label = sundayNormalizeText(external.textContent);
    }

    if (!label && control.getAttribute && control.getAttribute('aria-haspopup') === 'listbox') {
      var holder = control.parentElement;
      if (holder) {
        var nearby = holder.querySelector(':scope > span:first-child');
        if (nearby) label = sundayNormalizeText(nearby.textContent);
      }
      if (!label) label = sundayNormalizeText(control.getAttribute('aria-label'));
      if (!label) label = 'Program Of Interest';
    }

    if (!label && control.getAttribute && control.getAttribute('role') === 'checkbox') {
      label = 'Service';
    }

    if (!label && control.getAttribute) label = sundayNormalizeText(control.getAttribute('aria-label'));
    if (!label && control.name) {
      var names = {
        email: 'Email Address',
        phone: 'Phone Number',
        name: 'Name',
        message_subject: 'Subject',
        message: 'Message',
        business: 'Business Name',
        customService: 'Tailored Support',
        website: 'Website'
      };
      label = names[control.name] || String(control.name).replace(/[_-]+/g, ' ');
    }

    return sundayNormalizeText(label).replace(/\s*\*\s*$/, '');
  }

  function sundayValidationMessage(form, control, raw) {
    var original = sundayNormalizeText(raw);
    if (!original) return '';

    var lower = original.toLowerCase();
    var isMissing = lower.indexOf('please add') === 0 ||
      lower.indexOf('please select') === 0 ||
      lower.indexOf('required') !== -1;

    if (control && isMissing) {
      var role = control.getAttribute && control.getAttribute('role');
      var popup = control.getAttribute && control.getAttribute('aria-haspopup');
      var name = control.name || '';
      var type = (control.type || '').toLowerCase();

      if (popup === 'listbox') return 'PLEASE SELECT A PROGRAM.';
      if (role === 'checkbox') return 'PLEASE SELECT AT LEAST ONE SERVICE.';
      if (name === 'customService') return 'PLEASE TELL US WHAT TAILORED SUPPORT YOU NEED.';
      if (type === 'email' || name === 'email') return 'PLEASE ADD YOUR EMAIL ADDRESS.';
      if (type === 'tel' || name === 'phone') return 'PLEASE ADD YOUR PHONE NUMBER.';
      if (name === 'name') return 'PLEASE ADD YOUR NAME.';
      if (name === 'message_subject') return 'PLEASE ADD A SUBJECT.';

      var label = sundayFieldLabel(form, control);
      var clean = sundayNormalizeText(label).replace(/^your\s+/i, '');
      if (/^subject$/i.test(clean)) return 'PLEASE ADD A SUBJECT.';
      if (/^program( of interest)?$/i.test(clean)) return 'PLEASE SELECT A PROGRAM.';
      if (/^service/i.test(clean)) return 'PLEASE SELECT AT LEAST ONE SERVICE.';
      if (clean) return ('PLEASE ADD YOUR ' + clean + '.').toUpperCase();
    }

    if (lower.indexOf('valid email') !== -1) return 'PLEASE ENTER A VALID EMAIL ADDRESS.';
    if (lower.indexOf('full phone') !== -1) return 'PLEASE ADD A FULL PHONE NUMBER.';
    if (lower.indexOf('http://') !== -1 || lower.indexOf('https://') !== -1) {
      return 'PLEASE ENTER THE FULL LINK BEGINNING WITH HTTP:// OR HTTPS://.';
    }
    if (lower.indexOf('tailored') !== -1) return 'PLEASE TELL US WHAT TAILORED SUPPORT YOU NEED.';
    if (lower.indexOf('service') !== -1 && lower.indexOf('select') !== -1) return 'PLEASE SELECT AT LEAST ONE SERVICE.';
    if (lower.indexOf('program') !== -1 && lower.indexOf('select') !== -1) return 'PLEASE SELECT A PROGRAM.';

    return original.toUpperCase();
  }

  function sundayNormalizeFormAlerts() {
    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) {
      var form = forms[i];
      var alerts = form.querySelectorAll('[role="alert"]');
      for (var a = 0; a < alerts.length; a++) {
        var alert = alerts[a];
        var raw = sundayNormalizeText(alert.textContent);
        if (!raw) continue;
        var control = sundayErrorControl(form);
        var normalized = sundayValidationMessage(form, control, raw);
        if (normalized && raw !== normalized) alert.textContent = normalized;
      }
    }
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
    // This reservation opens on its own for a first-time visitor. On phones,
    // moving focus to its close button can pan Safari's visual viewport.
    // Leave focus in place until the visitor interacts; Tab is still trapped
    // inside the open dialog by the keyboard handler below.
    if (surface.matches('[aria-label="The Sunday Reservation"]') &&
        window.matchMedia && window.matchMedia('(max-width: 900px)').matches) return;
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

  function sundayErrorControl(form) {
    if (!form) return null;

    var alert = form.querySelector('[role="alert"]');
    var msg = sundayNormalizeText(alert && alert.textContent).toLowerCase();
    if (!msg) return null;

    /* Delivery/network errors are form-level, not field-level. */
    if (msg.indexOf('we could not') === 0 || msg.indexOf('something went wrong') !== -1) return null;

    if (msg.indexOf('email') !== -1) {
      var email = form.querySelector('input[type="email"],input[name="email"]');
      if (email) {
        var emailValue = sundayNormalizeText(email.value);
        var emailInvalid = emailValue && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(emailValue);
        if (!emailValue || emailInvalid) return email;
        return null;
      }
    }
    if (msg.indexOf('phone') !== -1) {
      var phone = form.querySelector('input[type="tel"],input[name="phone"]');
      if (phone) {
        var phoneValue = sundayNormalizeText(phone.value);
        if (!phoneValue || phoneValue.replace(/[^0-9]/g, '').length < 7) return phone;
        return null;
      }
    }
    if (msg.indexOf('subject') !== -1) {
      var subject = form.querySelector('[name="message_subject"]');
      return subject && !sundayNormalizeText(subject.value) ? subject : null;
    }
    if (msg.indexOf('business name') !== -1) {
      var business = form.querySelector('[name="business"]');
      return business && !sundayNormalizeText(business.value) ? business : null;
    }
    if (msg.indexOf('estimated budget') !== -1 || msg.indexOf('budget') !== -1) {
      var budget = form.querySelector('[name="budget"]');
      return budget && !sundayNormalizeText(budget.value) ? budget : null;
    }
    if (/(^|\s)name(\.|\s|$)/.test(msg) && msg.indexOf('business name') === -1) {
      var nameField = form.querySelector('[name="name"]');
      return nameField && !sundayNormalizeText(nameField.value) ? nameField : null;
    }
    if (msg.indexOf('your message') !== -1 || (msg.indexOf('message') !== -1 && msg.indexOf('error message') === -1)) {
      var messageField = form.querySelector('[name="message"]');
      return messageField && !sundayNormalizeText(messageField.value) ? messageField : null;
    }
    if (msg.indexOf('program') !== -1) {
      var programValue = form.querySelector('input[name="program"]');
      return (!programValue || !sundayNormalizeText(programValue.value)) ? form.querySelector('[aria-haspopup="listbox"]') : null;
    }
    if (msg.indexOf('service') !== -1 && msg.indexOf('tailored') === -1) {
      var servicesValue = form.querySelector('input[name="services"]');
      return (!servicesValue || !sundayNormalizeText(servicesValue.value)) ? form.querySelector('[role="checkbox"]') : null;
    }
    if (msg.indexOf('tailored') !== -1) {
      var tailored = form.querySelector('[name="customService"]');
      return tailored && !sundayNormalizeText(tailored.value) ? tailored : null;
    }
    if (msg.indexOf('link') !== -1 || msg.indexOf('http') !== -1) {
      var urls = form.querySelectorAll('input[type="url"]');
      for (var u = 0; u < urls.length; u++) {
        var urlValue = sundayNormalizeText(urls[u].value);
        if (urlValue && !/^https?:\/\/[^\s]+$/i.test(urlValue)) return urls[u];
      }
      return null;
    }

    /* Generic missing-field copy resolves against the actual label, never the
       placeholder, so a stale alert cannot jump the rose state to the field
       the user happens to be typing in. */
    var missing = msg.match(/^please (?:add|complete)(?: your)?\s+(.+?)[.!]?$/i);
    if (missing) {
      var wanted = sundayNormalizeText(missing[1]).replace(/[.!]+$/, '').replace(/^your\s+/i, '').toLowerCase();
      var candidates = form.querySelectorAll('input:not([type="hidden"]),textarea,select');
      for (var c = 0; c < candidates.length; c++) {
        var candidate = candidates[c];
        var label = sundayFieldLabel(form, candidate).replace(/^your\s+/i, '').toLowerCase();
        if (label === wanted) return candidate;
      }
    }

    if (msg.indexOf('complete this field') !== -1) {
      var controls = form.querySelectorAll('input:not([type="hidden"]),textarea,select');
      for (var i = 0; i < controls.length; i++) {
        var el = controls[i];
        var value = sundayNormalizeText(el.value);
        if (el.required && !value) return el;
      }
    }

    return null;
  }

  function syncFormErrorVisuals() {
    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) {
      var form = forms[i];
      var marked = form.querySelectorAll('[data-form-error-field="true"],[aria-invalid="true"]');
      for (var m = 0; m < marked.length; m++) {
        marked[m].removeAttribute('data-form-error-field');
        marked[m].removeAttribute('aria-invalid');
      }

      var alerts = form.querySelectorAll('[role="alert"]');
      var hasError = false;
      for (var a = 0; a < alerts.length; a++) {
        if (sundayNormalizeText(alerts[a].textContent)) {
          hasError = true;
          break;
        }
      }
      if (!hasError) continue;
      var target = sundayErrorControl(form);
      if (target) {
        target.setAttribute('data-form-error-field', 'true');
        target.setAttribute('aria-invalid', 'true');
      }
    }
  }

  function scheduleFormErrorSync() {
    window.setTimeout(syncFormErrorVisuals, 0);
    window.setTimeout(syncFormErrorVisuals, 70);
    window.setTimeout(syncFormErrorVisuals, 180);
  }

  function installFormErrorManagement() {
    document.addEventListener('submit', function () {
      scheduleFormErrorSync();
    }, true);

    function clearTarget(event) {
      var target = event.target && event.target.closest ? event.target.closest('[data-form-error-field="true"],[aria-invalid="true"]') : null;
      if (target) {
        target.removeAttribute('data-form-error-field');
        target.removeAttribute('aria-invalid');
      }
      /* Editing clears the stale field state immediately. Validation is
         re-run by the form's own Next/submit action, avoiding a stale alert
         briefly re-painting the field while the user is correcting it. */
    }
    document.addEventListener('input', clearTarget, true);
    document.addEventListener('change', clearTarget, true);

    document.addEventListener('click', function (event) {
      var form = event.target && event.target.closest ? event.target.closest('form') : null;
      if (!form) return;

      var option = event.target.closest('[role="option"]');
      if (option) {
        var trigger = form.querySelector('[aria-haspopup="listbox"][data-form-error-field="true"],[aria-haspopup="listbox"][aria-invalid="true"]');
        if (trigger) {
          trigger.removeAttribute('data-form-error-field');
          trigger.removeAttribute('aria-invalid');
        }
      }

      var checkbox = event.target.closest('[role="checkbox"][data-form-error-field="true"],[role="checkbox"][aria-invalid="true"]');
      if (checkbox) {
        checkbox.removeAttribute('data-form-error-field');
        checkbox.removeAttribute('aria-invalid');
      }

      /* Covers submit buttons, multi-step Next/Back buttons, custom listboxes,
         checkbox toggles and any future form button. */
      scheduleFormErrorSync();
    }, true);

    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Enter') return;
      var form = event.target && event.target.closest ? event.target.closest('form') : null;
      if (form) scheduleFormErrorSync();
    }, true);
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
    sundayNormalizeFormAlerts();
    syncFormErrorVisuals();
    syncAccessibleSurface();
  }

  function boot() {
    ensureCorrectionStyles();
    installAccessibleSurfaceManagement();
    installFormErrorManagement();
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
        if (mutations[i].type === 'characterData') {
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
      characterData: true,
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
