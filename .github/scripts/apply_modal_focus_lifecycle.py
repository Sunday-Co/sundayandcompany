from pathlib import Path

path = Path('assets/site.js')
text = path.read_text()

old_dialogs = """  function sundayCurrentSurface() {\n    var dialogs = Array.prototype.slice.call(document.querySelectorAll('[role=\"dialog\"][aria-modal=\"true\"], [role=\"dialog\"][aria-modal=\"true\"]'));\n    for (var i = dialogs.length - 1; i >= 0; i--) if (sundayVisible(dialogs[i])) return dialogs[i];\n    var sheet = document.querySelector('aside[aria-label=\"Sunday & Company navigation\"][data-sheet-state=\"open\"]');\n    return sundayVisible(sheet) ? sheet : null;\n  }\n"""
new_dialogs = """  function sundayCurrentSurface() {\n    var dialogs = Array.prototype.slice.call(document.querySelectorAll('[role=\"dialog\"][aria-modal=\"true\"]'));\n    for (var i = dialogs.length - 1; i >= 0; i--) if (sundayVisible(dialogs[i])) return dialogs[i];\n    var sheet = document.querySelector('aside[aria-label=\"Sunday & Company navigation\"][data-sheet-state=\"open\"]');\n    return sundayVisible(sheet) ? sheet : null;\n  }\n"""
if old_dialogs not in text:
    raise SystemExit('Could not find current-surface block to update')
text = text.replace(old_dialogs, new_dialogs, 1)

old_tab = """      if (event.key !== 'Tab') return;\n      var items = sundayFocusable(surface);\n      if (!items.length) return;\n      var first = items[0], last = items[items.length - 1];\n      if (event.shiftKey && document.activeElement === first) {\n        event.preventDefault();\n        last.focus();\n      } else if (!event.shiftKey && document.activeElement === last) {\n        event.preventDefault();\n        first.focus();\n      }\n"""
new_tab = """      if (event.key !== 'Tab') return;\n      var items = sundayFocusable(surface);\n      if (!items.length) return;\n      var first = items[0], last = items[items.length - 1];\n      var active = document.activeElement;\n      if (!surface.contains(active)) {\n        event.preventDefault();\n        (event.shiftKey ? last : first).focus();\n        return;\n      }\n      if (event.shiftKey && active === first) {\n        event.preventDefault();\n        last.focus();\n      } else if (!event.shiftKey && active === last) {\n        event.preventDefault();\n        first.focus();\n      }\n"""
if old_tab not in text:
    raise SystemExit('Could not find Tab trap block to update')
text = text.replace(old_tab, new_tab, 1)

old_observer = """    var mo = new MutationObserver(function (mutations) {\n      var shouldSync = false;\n      for (var i = 0; i < mutations.length; i++) {\n        if (mutations[i].type === 'childList' && mutations[i].addedNodes.length) {\n          shouldSync = true;\n          break;\n        }\n      }\n      if (shouldSync) window.requestAnimationFrame(sync);\n    });\n\n    mo.observe(document.documentElement, { childList: true, subtree: true });\n"""
new_observer = """    var mo = new MutationObserver(function (mutations) {\n      var shouldSync = false;\n      for (var i = 0; i < mutations.length; i++) {\n        if (mutations[i].type === 'attributes') {\n          shouldSync = true;\n          break;\n        }\n        if (mutations[i].type === 'childList' && mutations[i].addedNodes.length) {\n          shouldSync = true;\n          break;\n        }\n      }\n      if (shouldSync) window.requestAnimationFrame(sync);\n    });\n\n    mo.observe(document.documentElement, {\n      childList: true,\n      subtree: true,\n      attributes: true,\n      attributeFilter: ['style', 'data-sheet-state', 'aria-hidden', 'aria-modal']\n    });\n"""
if old_observer not in text:
    raise SystemExit('Could not find surface observer block to update')
text = text.replace(old_observer, new_observer, 1)

path.write_text(text)
print('Updated modal/sheet focus lifecycle: detect rendered visibility changes, keep Tab inside, and restore opener focus after close.')
