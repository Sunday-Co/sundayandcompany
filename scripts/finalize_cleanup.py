from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def clean_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    old = text

    # Repair literal backslashes accidentally introduced around Inter Tight in a
    # few generated inline style attributes during the first deterministic pass.
    text = text.replace("font-family:\\'Inter Tight\\'", "font-family:'Inter Tight'")

    # Remove obsolete popup sizing declarations left from the pre-cleanup mobile
    # patch. Shared production CSS now owns these dimensions, so keeping duplicate
    # !important rules only creates unnecessary cascade conflicts.
    text = re.sub(r'^\s*\[aria-label="The Sunday Reservation"\].*?\n', '', text, flags=re.M)
    text = re.sub(r'^\s*\[aria-label="Project inquiry"\] h2 .*?\n', '', text, flags=re.M)
    text = re.sub(r'^\s*\[aria-label="Project inquiry"\] > div .*?\n', '', text, flags=re.M)
    text = re.sub(r'^\s*#inquiry > div .*?\n', '', text, flags=re.M)
    text = re.sub(r'^\s*#inquiry header h2 .*?\n', '', text, flags=re.M)
    text = re.sub(r'^\s*#inquiry header h2 \+ p .*?\n', '', text, flags=re.M)

    if text != old:
        path.write_text(text, encoding="utf-8")
        print(f"finalized {path.relative_to(ROOT)}")
        return True
    return False


def validate():
    html_files = [p for p in ROOT.rglob('*.html') if '.git' not in p.parts]
    failures = []
    for p in html_files:
        t = p.read_text(encoding='utf-8')
        if "font-family:\\'Inter Tight\\'" in t:
            failures.append(f"escaped font family remains: {p.relative_to(ROOT)}")
        if 'Ysabeau' in t:
            failures.append(f"old font remains: {p.relative_to(ROOT)}")
        if '<helmet>' in t and '/assets/site.css' not in t:
            failures.append(f"shared production CSS missing: {p.relative_to(ROOT)}")
        if '100dvh' in t:
            failures.append(f"dynamic viewport unit remains: {p.relative_to(ROOT)}")

    services = (ROOT / 'services' / 'index.html').read_text(encoding='utf-8')
    for hook in ['data-service-number', 'data-service-price', 'data-service-meta', 'data-service-included']:
        if hook not in services:
            failures.append(f"services hook missing: {hook}")

    header = (ROOT / 'Site Header.dc.html').read_text(encoding='utf-8')
    for hook in ['data-sheet-cta', 'data-inquiry-kicker', 'data-inquiry-support', 'data-inquiry-ledger']:
        if hook not in header:
            failures.append(f"header hook missing: {hook}")

    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    if 'data-vision-quote' not in home or 'Marketing Should Feel Less Like Noise' not in home:
        failures.append('approved Our Vision quote treatment missing')

    if failures:
        raise SystemExit('\n'.join(failures))
    print(f"final validation passed for {len(html_files)} HTML/component files")


if __name__ == '__main__':
    for path in ROOT.rglob('*.html'):
        if '.git' in path.parts:
            continue
        clean_html(path)
    validate()
