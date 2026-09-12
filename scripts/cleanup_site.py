from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PAGE_GLOB = "*.html"

FONT_OLD = "family=Ysabeau:wght@300;400;500&family="
FONT_NEW = "family=Inter+Tight:wght@300;400;500&family="

ASSET_LINKS = """<link rel=\"stylesheet\" href=\"/assets/site.css\" />\n<script defer src=\"/assets/site.js\"></script>"""


def write_if_changed(path: Path, text: str):
    old = path.read_text(encoding="utf-8")
    if old != text:
        path.write_text(text, encoding="utf-8")
        print(f"updated {path.relative_to(ROOT)}")
        return True
    return False


def normalize_font(text: str) -> str:
    text = text.replace(FONT_OLD, FONT_NEW)
    text = text.replace("Ysabeau", "Inter Tight")
    return text


def remove_legacy_global_font_patch(text: str) -> str:
    # Remove the old page-level selector block that globally resized every tiny
    # Ysabeau/Inter Tight declaration. The production scale now lives in site.css.
    pattern = re.compile(
        r"\n\s*\[style\*=\"font-family:'Inter Tight'\"\]\s*\{.*?\n\s*\*:focus\s*\{",
        re.S,
    )
    m = pattern.search(text)
    if m:
        replacement = "\n  *:focus {"
        text = text[:m.start()] + replacement + text[m.end():]
    return text


def inject_assets(text: str) -> str:
    if "href=\"/assets/site.css\"" in text:
        return text
    if "</helmet>" in text:
        return text.replace("</helmet>", ASSET_LINKS + "\n</helmet>", 1)
    return text


def stable_viewports(text: str) -> str:
    # Safari's browser chrome changes dynamic viewport units while scrolling.
    # svh keeps the approved mobile modal proportions stable.
    return text.replace("100dvh", "100svh")


def fix_home(path: Path):
    text = path.read_text(encoding="utf-8")
    text = normalize_font(text)
    text = remove_legacy_global_font_patch(text)
    text = inject_assets(text)
    text = stable_viewports(text)

    text = text.replace(
        '<section id="top" aria-labelledby="hero-title"',
        '<section id="top" data-screen-hero="home" aria-labelledby="hero-title"',
        1,
    )
    text = text.replace(
        'style="height:100%;inset:0;object-fit:cover;object-position:50% 48%;position:absolute;width:100%;z-index:0"',
        'style="height:100%;object-fit:cover;object-position:50% 48%;position:relative;width:100%;z-index:0"',
        1,
    )

    old_quote = (
        '<p style="font-family:\'Playfair Display\',Georgia,serif;font-size:clamp(13px,1vw,15px);'
        'font-weight:500;letter-spacing:.055em;line-height:1.62;max-width:660px;text-transform:uppercase">'
        'Marketing should feel less like noise and more like an invitation. We believe the strongest brands give people '
        'something meaningful to recognize, return to and gather around.</p>'
    )
    new_quote = (
        '<p data-vision-quote style="font-family:\'Playfair Display\',Georgia,serif;font-size:clamp(17px,1.35vw,20px);'
        'font-style:italic;font-weight:400;letter-spacing:-.012em;line-height:1.55;max-width:660px">'
        'Marketing Should Feel Less Like Noise And More Like An Invitation. We Believe The Strongest Brands Give People '
        'Something Meaningful To Recognize, Return To And Gather Around.</p>'
    )
    if old_quote not in text and "data-vision-quote" not in text:
        raise SystemExit("Home quote source did not match expected markup")
    text = text.replace(old_quote, new_quote, 1)

    p1 = '<p style="font-size:14px;line-height:1.68;max-width:660px">Sunday &amp; Company is a marketing, creative and design studio for lifestyle brands built with intention.'
    p2 = '<p style="font-size:14px;line-height:1.68;max-width:660px">Our work is grounded in strategy but never stripped of personality.'
    text = text.replace(p1, '<p data-vision-body style="font-size:15px;font-weight:400;line-height:1.68;max-width:660px">Sunday &amp; Company is a marketing, creative and design studio for lifestyle brands built with intention.', 1)
    text = text.replace(p2, '<p data-vision-body style="font-size:15px;font-weight:400;line-height:1.68;max-width:660px">Our work is grounded in strategy but never stripped of personality.', 1)

    write_if_changed(path, text)


def fix_header(path: Path):
    text = path.read_text(encoding="utf-8")
    text = normalize_font(text)
    text = stable_viewports(text)

    text = text.replace(
        '<button type="button" onClick="{{ openInquiryFromSheet }}" style=',
        '<button data-sheet-cta type="button" onClick="{{ openInquiryFromSheet }}" style=',
        1,
    )
    text = text.replace(
        '<a href="/contact" onClick="{{ closeSheet }}" style=',
        '<a data-sheet-cta href="/contact" onClick="{{ closeSheet }}" style=',
        1,
    )
    text = text.replace(
        '<p style="color:#ac746c;font-family:\'Pinyon Script\',cursive;font-size:24px;',
        '<p data-inquiry-kicker style="color:#ac746c;font-family:\'Pinyon Script\',cursive;font-size:28px;',
        1,
    )
    text = text.replace(
        '<p style="font-size:12px;line-height:1.5;margin:10px 0 0;max-width:520px">Share the essentials. We’ll take it from there.</p>',
        '<p data-inquiry-support style="font-family:\'Inter Tight\',sans-serif;font-size:13px;font-weight:300;line-height:1.5;margin:10px 0 0;max-width:520px">Share the essentials. We’ll take it from there.</p>',
        1,
    )
    text = text.replace(
        '<div aria-hidden="true" style="border-bottom:1px solid #311d03;border-top:1px solid #311d03;display:flex;font-family:\'Inter Tight\',sans-serif;font-size:8px;',
        '<div data-inquiry-ledger aria-hidden="true" style="border-bottom:1px solid #311d03;border-top:1px solid #311d03;display:flex;font-family:\'Inter Tight\',sans-serif;font-size:9.5px;',
        1,
    )

    # Remove forced almost-full-screen receipt height. Shared CSS controls the final
    # centered mobile receipt and gives it a modest bottom buffer.
    text = text.replace(
        "inqReceiptMinH: t ? 'calc(100svh - 20px)' : 'min(700px, calc(100svh - 72px))',",
        "inqReceiptMinH: t ? 'min(700px, calc(100svh - 36px))' : 'min(700px, calc(100svh - 72px))',",
    )
    text = text.replace(
        "resDialogMinH: t ? 'min(740px, calc(100svh - 28px))' : 'min(600px, calc(100svh - 56px))',",
        "resDialogMinH: t ? 'auto' : 'min(560px, calc(100svh - 56px))',",
    )
    text = text.replace(
        "resContentMinH: t ? '500px' : '600px',",
        "resContentMinH: t ? 'auto' : '560px',",
    )

    write_if_changed(path, text)


def fix_footer(path: Path):
    text = path.read_text(encoding="utf-8")
    text = normalize_font(text)
    text = stable_viewports(text)
    # Make the six Explore links use the same secondary face and light optical
    # weight as the email/location instead of inheriting Playfair.
    for href in ["/about", "/services", "/our-work", "/contact", "/join-our-team", "/sunday-school"]:
        text = text.replace(
            f'<a href="{href}" style="font-size:11.5px;line-height:1.3"',
            f'<a data-footer-ui href="{href}" style="font-family:\'Inter Tight\',sans-serif;font-size:12.5px;font-weight:300;line-height:1.35"',
            1,
        )
    text = text.replace(
        '<a href="mailto:hello@sundayandcompany.co" style=',
        '<a data-footer-ui href="mailto:hello@sundayandcompany.co" style=',
        1,
    )
    text = text.replace(
        '<p style="font-family:\'Inter Tight\',sans-serif;font-size:12.5px;font-weight:300;letter-spacing:.02em;line-height:1.4">DMV',
        '<p data-footer-location style="font-family:\'Inter Tight\',sans-serif;font-size:12.5px;font-weight:300;letter-spacing:.02em;line-height:1.4">DMV',
        1,
    )
    text = text.replace(
        '<a href="https://www.instagram.com/sundayand_co/" rel="noreferrer" target="_blank" style="font-size:11.5px;line-height:1.3"',
        '<a data-footer-ui href="https://www.instagram.com/sundayand_co/" rel="noreferrer" target="_blank" style="font-family:\'Inter Tight\',sans-serif;font-size:12.5px;font-weight:300;line-height:1.35"',
        1,
    )
    text = text.replace(
        '<div style="align-items:start;border-top:1px solid rgba(245,239,230,.42);column-gap:clamp(20px,3vw,48px);display:grid;font-family:\'Inter Tight\',sans-serif;font-size:7px;',
        '<div data-footer-legal style="align-items:start;border-top:1px solid rgba(245,239,230,.42);column-gap:clamp(20px,3vw,48px);display:grid;font-family:\'Inter Tight\',sans-serif;font-size:8.5px;',
        1,
    )
    write_if_changed(path, text)


def fix_inquiry_form(path: Path):
    text = path.read_text(encoding="utf-8")
    text = normalize_font(text)
    text = stable_viewports(text)
    # Field labels were visually too large after prior global overrides. Keep them
    # only a smidgen smaller than the receipt metadata and reduce tracking.
    text = text.replace("font-size:10px !important;\n    font-weight: 300 !important;\n    letter-spacing: .12em !important;", "font-size:11.25px !important;\n    font-weight: 300 !important;\n    letter-spacing: .10em !important;", 1)
    text = text.replace("font-size:9px;font-weight:300;letter-spacing:.14em", "font-size:11.25px;font-weight:300;letter-spacing:.10em")
    text = text.replace("font-size:8px;font-weight:300;letter-spacing:.16em", "font-size:11px;font-weight:300;letter-spacing:.10em")
    # Step/meta text and button copy get a small readability increase but less width.
    text = text.replace("font-size:7px;letter-spacing:.13em", "font-size:10px;letter-spacing:.11em")
    text = text.replace("font-size:7px;height:18px", "font-size:9px;height:18px")
    text = text.replace("font-size:10px;gap:8px;letter-spacing:.14em", "font-size:10px;gap:8px;letter-spacing:.11em")
    text = text.replace("font-size:8px;gap:9px;justify-content:center;letter-spacing:.16em", "font-size:9.5px;gap:9px;justify-content:center;letter-spacing:.12em")
    write_if_changed(path, text)


def fix_about(path: Path):
    text = path.read_text(encoding="utf-8")
    text = normalize_font(text)
    text = remove_legacy_global_font_patch(text)
    text = inject_assets(text)
    text = stable_viewports(text)
    text = text.replace(
        '<a href="/join-our-team" style="align-items:center;background:#f5efe6;',
        '<a data-about-team-cta href="/join-our-team" style="align-items:center;background:#f5efe6;',
        1,
    )
    write_if_changed(path, text)


def fix_services(path: Path):
    text = path.read_text(encoding="utf-8")
    text = normalize_font(text)
    text = remove_legacy_global_font_patch(text)
    text = inject_assets(text)
    text = stable_viewports(text)

    # Add semantic hooks to the three accordion rows so only the requested
    # supporting microtype changes, not the large Playfair service titles.
    text = re.sub(
        r'<span style="font-family:\'Inter Tight\',sans-serif;font-size:8px;font-weight:500;letter-spacing:.14em;text-transform:uppercase">(0[123])</span>',
        r'<span data-service-number style="font-family:\'Inter Tight\',sans-serif;font-size:8px;font-weight:500;letter-spacing:.14em;text-transform:uppercase">\1</span>',
        text,
    )
    text = text.replace(
        '<strong style="color:#ac746c;font-family:\'Inter Tight\',sans-serif;font-size:10px;font-weight:500;letter-spacing:.14em;text-transform:uppercase">Starting At',
        '<strong data-service-price style="color:#ac746c;font-family:\'Inter Tight\',sans-serif;font-size:10px;font-weight:500;letter-spacing:.14em;text-transform:uppercase">Starting At',
    )
    text = text.replace(
        '<small style="font-family:\'Inter Tight\',sans-serif;font-size:8px;font-weight:500;letter-spacing:.14em;text-transform:uppercase">',
        '<small data-service-meta style="font-family:\'Inter Tight\',sans-serif;font-size:8px;font-weight:500;letter-spacing:.14em;text-transform:uppercase">',
    )
    text = text.replace(
        '<span style="color:#ac746c;font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.13em;text-transform:uppercase">Designed For</span>',
        '<span data-service-meta style="color:#ac746c;font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.13em;text-transform:uppercase">Designed For</span>',
    )
    text = text.replace(
        '<p style="font-family:\'Inter Tight\',sans-serif;font-size:9px;font-weight:500;letter-spacing:.22em;line-height:1.4;margin-bottom:11px;text-transform:uppercase">What Is Included</p>',
        '<p data-service-meta style="font-family:\'Inter Tight\',sans-serif;font-size:9px;font-weight:500;letter-spacing:.18em;line-height:1.4;margin-bottom:11px;text-transform:uppercase">What Is Included</p>',
    )
    text = text.replace(
        '<li style="border-bottom:1px solid rgba(49,29,3,.28);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.1em;padding:10px 0;text-transform:uppercase">',
        '<li data-service-included style="border-bottom:1px solid rgba(49,29,3,.28);font-family:\'Inter Tight\',sans-serif;font-size:8px;letter-spacing:.1em;padding:10px 0;text-transform:uppercase">',
    )
    write_if_changed(path, text)


def fix_generic_page(path: Path):
    text = path.read_text(encoding="utf-8")
    text = normalize_font(text)
    text = remove_legacy_global_font_patch(text)
    text = inject_assets(text)
    text = stable_viewports(text)
    write_if_changed(path, text)


def validate():
    all_html = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts and ".github" not in p.parts]
    page_html = [p for p in all_html if "<helmet>" in p.read_text(encoding="utf-8")]
    failures = []
    for p in all_html:
        t = p.read_text(encoding="utf-8")
        if "Ysabeau" in t:
            failures.append(f"Ysabeau remains in {p.relative_to(ROOT)}")
    for p in page_html:
        t = p.read_text(encoding="utf-8")
        if '/assets/site.css' not in t or '/assets/site.js' not in t:
            failures.append(f"shared assets missing from {p.relative_to(ROOT)}")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if "data-vision-quote" not in home:
        failures.append("home vision quote hook missing")
    if "Marketing Should Feel Less Like Noise" not in home:
        failures.append("home vision quote was not converted to approved display case")
    if "Sunday-Co-Ysabeau-Mobile-Forms-Update" in (ROOT / "netlify.toml").read_text(encoding="utf-8"):
        failures.append("netlify still depends on nested update folder")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"validated {len(all_html)} html/component files and {len(page_html)} page documents")


def main():
    home = ROOT / "index.html"
    fix_home(home)
    fix_header(ROOT / "Site Header.dc.html")
    fix_footer(ROOT / "Site Footer.dc.html")
    fix_inquiry_form(ROOT / "Inquiry Form.dc.html")
    fix_about(ROOT / "about" / "index.html")
    fix_services(ROOT / "services" / "index.html")

    special = {
        home.resolve(),
        (ROOT / "Site Header.dc.html").resolve(),
        (ROOT / "Site Footer.dc.html").resolve(),
        (ROOT / "Inquiry Form.dc.html").resolve(),
        (ROOT / "about" / "index.html").resolve(),
        (ROOT / "services" / "index.html").resolve(),
    }
    for path in ROOT.rglob("*.html"):
        if path.resolve() in special or ".git" in path.parts or ".github" in path.parts:
            continue
        fix_generic_page(path)

    validate()


if __name__ == "__main__":
    main()
