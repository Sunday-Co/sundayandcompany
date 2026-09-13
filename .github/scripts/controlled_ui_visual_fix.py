from pathlib import Path

p = Path('assets/site.css')
s = p.read_text()

# 1. Keep the existing modal entrance motion, but never fade the whole dialog.
start = s.find('@keyframes sunday-modal-in {')
end = s.find('\n}\n\n[aria-label="Project inquiry"]', start)
if start < 0 or end < 0:
    raise SystemExit('Could not isolate sunday-modal-in keyframes')
block = s[start:end + 2]
if block.count('opacity: 0;') != 1:
    raise SystemExit(f'Unexpected modal opacity source: {block.count("opacity: 0;")} zero-opacity declarations')
block_new = block.replace('opacity: 0;', 'opacity: 1;', 1)
s = s[:start] + block_new + s[end + 2:]
print('Modal opacity source corrected.')

# 2. On mobile, anchor Project Inquiry at the top of the overlay instead of
# centering a tall dialog outside the visible viewport.
overlay_old = '''  div[role="presentation"]:has(> [aria-label="Project inquiry"]) {
    padding: 12px !important;
    overflow-y: auto !important;
  }'''
overlay_new = '''  div[role="presentation"]:has(> [aria-label="Project inquiry"]) {
    align-items: flex-start !important;
    padding: 12px !important;
    overflow-y: auto !important;
  }'''
if s.count(overlay_old) != 1:
    raise SystemExit(f'Unexpected mobile inquiry overlay matches: {s.count(overlay_old)}')
s = s.replace(overlay_old, overlay_new, 1)

dialog_old = '''  [aria-label="Project inquiry"] {
    width: calc(100vw - 24px) !important;
    max-width: calc(100vw - 24px) !important;
    max-height: calc(100svh - 24px) !important;
    overflow-y: auto !important;
  }'''
dialog_new = '''  [aria-label="Project inquiry"] {
    margin: 0 auto !important;
    width: calc(100vw - 24px) !important;
    max-width: calc(100vw - 24px) !important;
    max-height: calc(100dvh - 24px) !important;
    overflow-y: auto !important;
  }'''
if s.count(dialog_old) != 1:
    raise SystemExit(f'Unexpected mobile inquiry dialog matches: {s.count(dialog_old)}')
s = s.replace(dialog_old, dialog_new, 1)
print('Mobile inquiry viewport anchoring corrected.')

# 3. Refine the mobile Reservation copy to remain small, but actually readable.
fine_marker = '    font-size: 6.5px !important;'
fine_idx = s.find(fine_marker)
if fine_idx < 0 or s.find(fine_marker, fine_idx + 1) >= 0:
    raise SystemExit('Could not uniquely locate mobile Reservation fine print')

support_start = s.rfind('  [aria-label="The Sunday Reservation"] h2 + p {', 0, fine_idx)
support_end = s.find('\n  }', support_start)
if support_start < 0 or support_end < 0:
    raise SystemExit('Could not isolate mobile Reservation support block')
support = s[support_start:support_end + 4]
for old, new in [
    ('font-size: 10.5px !important;', 'font-size: 11.5px !important;'),
    ('line-height: 1.45 !important;', 'line-height: 1.48 !important;'),
]:
    if support.count(old) != 1:
        raise SystemExit(f'Unexpected Reservation support source for {old}')
    support = support.replace(old, new, 1)
s = s[:support_start] + support + s[support_end + 4:]

fine_idx = s.find(fine_marker)
fine_start = s.rfind('  [aria-label="The Sunday Reservation"] [data-res-fineprint] {', 0, fine_idx)
fine_end = s.find('\n  }', fine_start)
if fine_start < 0 or fine_end < 0:
    raise SystemExit('Could not isolate mobile Reservation fine print block')
fine = s[fine_start:fine_end + 4]
changes = [
    ('font-size: 6.5px !important;', 'font-size: 8px !important;'),
    ('letter-spacing: .04em !important;', 'letter-spacing: .035em !important;'),
    ('line-height: 1.38 !important;', 'line-height: 1.42 !important;'),
    ('margin-top: 6px !important;', 'margin-top: 7px !important;'),
]
for old, new in changes:
    if fine.count(old) != 1:
        raise SystemExit(f'Unexpected Reservation fine-print source for {old}')
    fine = fine.replace(old, new, 1)
if 'opacity:' not in fine:
    fine = fine[:-4] + '    opacity: .78 !important;\n  }'
s = s[:fine_start] + fine + s[fine_end + 4:]
print('Mobile Reservation readability corrected.')

p.write_text(s)
print('Controlled visual source correction complete.')
