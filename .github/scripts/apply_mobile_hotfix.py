# Re-run after refining visual QA; source transformations remain unchanged.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# 1) Project inquiry confirmation: all confirmation copy uses the secondary font + uppercase.
inquiry = ROOT / "Inquiry Form.dc.html"
old_success = '''  <div style="padding:35px 0;text-align:center;display:{{ doneDisplay }}">
    <h3 style="font-size:clamp(28px,3vw,38px);font-weight:400;letter-spacing:-.045em;line-height:.94;margin:0">Your Inquiry Is In.</h3>
    <p style="font-size:12px;line-height:1.5;margin:12px auto 0;max-width:520px">Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>
    <p data-receipt-meta style="font-family:'Inter Tight',sans-serif;font-size:8px;letter-spacing:.16em;margin:18px 0 0;text-transform:uppercase">Status: Inquiry Delivered</p>
  </div>'''
new_success = '''  <div data-inquiry-success role="status" aria-live="polite" style="font-family:'Inter Tight',sans-serif;padding:35px 0;text-align:center;text-transform:uppercase;display:{{ doneDisplay }}">
    <h3 style="font-family:'Inter Tight',sans-serif;font-size:clamp(18px,2.2vw,24px);font-weight:400;letter-spacing:.11em;line-height:1.2;margin:0;text-transform:uppercase">Your Inquiry Is In.</h3>
    <p style="font-family:'Inter Tight',sans-serif;font-size:10px;font-weight:300;letter-spacing:.065em;line-height:1.55;margin:13px auto 0;max-width:520px;text-transform:uppercase">Thank you for sharing the details. We have received your inquiry and will review it before following up.</p>
    <p data-receipt-meta style="font-family:'Inter Tight',sans-serif;font-size:8.5px;font-weight:400;letter-spacing:.11em;margin:18px 0 0;text-transform:uppercase">Status: Inquiry Delivered</p>
  </div>'''
replace_once(inquiry, old_success, new_success, "inquiry success typography")


# 2) Contact FAQ: sticky is desktop-only. On mobile the intro must remain in normal document flow.
contact = ROOT / "contact" / "index.html"
replace_once(
    contact,
    '<div style="align-self:start;position:sticky;top:120px">',
    '<div style="align-self:start;position:{{ faqPosition }};top:{{ faqTop }}">',
    "FAQ responsive position",
)
replace_once(
    contact,
    "      gc4: n ? '26px 1fr auto' : '34px 1fr auto',};",
    "      gc4: n ? '26px 1fr auto' : '34px 1fr auto',\n      faqPosition: n ? 'static' : 'sticky',\n      faqTop: n ? 'auto' : '120px',};",
    "FAQ responsive render values",
)


# 3) Shared typography owner: make mobile footer email visibly larger and newsletter disclaimer lighter.
site_css = ROOT / "assets" / "site.css"
replace_once(
    site_css,
    '''  footer a[href^="mailto:"] {
    font-size: 13.25px !important;
    font-weight: 400 !important;
  }''',
    '''  footer a[href^="mailto:"] {
    font-size: 15.5px !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
  }''',
    "mobile footer email size",
)
replace_once(
    site_css,
    '''  [aria-label="Newsletter"] [data-news-fineprint] {
    font-size: 8.25px !important;
    letter-spacing: .035em !important;
    line-height: 1.5 !important;
  }''',
    '''  [aria-label="Newsletter"] [data-news-fineprint] {
    font-size: 8.25px !important;
    font-weight: 300 !important;
    letter-spacing: .03em !important;
    line-height: 1.5 !important;
    opacity: .68 !important;
  }''',
    "mobile newsletter disclaimer weight",
)

# Cache-bust the shared production assets so iPhone Safari cannot keep the prior typography CSS.
updated = 0
for html in ROOT.rglob("*.html"):
    text = html.read_text(encoding="utf-8")
    new = text.replace("20260913-14", "20260913-15")
    if new != text:
        html.write_text(new, encoding="utf-8")
        updated += 1

if updated < 10:
    raise SystemExit(f"Expected sitewide asset-version bump, changed only {updated} HTML files")

remaining = []
for html in ROOT.rglob("*.html"):
    if "20260913-14" in html.read_text(encoding="utf-8"):
        remaining.append(str(html.relative_to(ROOT)))
if remaining:
    raise SystemExit("Old asset version remains in: " + ", ".join(remaining))

print(f"Applied mobile hotfix and bumped shared assets to 20260913-15 across {updated} HTML files.")
