from pathlib import Path

p = Path('assets/site.css')
s = p.read_text()

replacements = [
    (
        """@keyframes sunday-modal-in {
  from {
    opacity: 0;
    transform: translateY(8px) scale(.995);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}""",
        """@keyframes sunday-modal-in {
  from {
    opacity: 1;
    transform: translateY(8px) scale(.995);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}""",
    ),
    (
        """  div[role=\"presentation\"]:has(> [aria-label=\"Project inquiry\"]) {
    padding: 12px !important;
    overflow-y: auto !important;
  }
  [aria-label=\"Project inquiry\"] {
    width: calc(100vw - 24px) !important;
    max-width: calc(100vw - 24px) !important;
    max-height: calc(100svh - 24px) !important;
    overflow-y: auto !important;
  }""",
        """  div[role=\"presentation\"]:has(> [aria-label=\"Project inquiry\"]) {
    align-items: flex-start !important;
    padding: 12px !important;
    overflow-y: auto !important;
  }
  [aria-label=\"Project inquiry\"] {
    margin: 0 auto !important;
    width: calc(100vw - 24px) !important;
    max-width: calc(100vw - 24px) !important;
    max-height: calc(100dvh - 24px) !important;
    overflow-y: auto !important;
  }""",
    ),
    (
        """  [aria-label=\"The Sunday Reservation\"] h2 + p {
    font-size: 10.5px !important;
    line-height: 1.45 !important;
    margin-top: 11px !important;
    max-width: 310px !important;
  }
  [aria-label=\"The Sunday Reservation\"] [data-res-fineprint] {
    font-size: 6.5px !important;
    letter-spacing: .04em !important;
    line-height: 1.38 !important;
    margin-top: 6px !important;
  }""",
        """  [aria-label=\"The Sunday Reservation\"] h2 + p {
    font-size: 11.5px !important;
    line-height: 1.48 !important;
    margin-top: 11px !important;
    max-width: 310px !important;
  }
  [aria-label=\"The Sunday Reservation\"] [data-res-fineprint] {
    font-size: 8px !important;
    letter-spacing: .035em !important;
    line-height: 1.42 !important;
    margin-top: 7px !important;
    opacity: .78 !important;
  }""",
    ),
]

for old, new in replacements:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'Expected one exact source match, found {count}')
    s = s.replace(old, new, 1)

p.write_text(s)
print('Applied controlled modal/readability corrections.')
