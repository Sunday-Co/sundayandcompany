#!/usr/bin/env python3
"""Static guardrails for the Sunday & Company exported site."""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = (
    "Site Header.dc.html",
    "Site Footer.dc.html",
    "Inquiry Form.dc.html",
    "Program Cards.dc.html",
)
FORM_FILES = (
    "Site Header.dc.html",
    "Site Footer.dc.html",
    "Inquiry Form.dc.html",
    "contact/index.html",
    "join-our-team/index.html",
    "sunday-school/index.html",
)
errors = []

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

for name in COMPONENTS:
    canonical = ROOT / name
    copies = sorted(p for p in ROOT.rglob(name) if ".git" not in p.parts)
    if len(copies) != 15:
        errors.append(f"{name}: expected 15 copies, found {len(copies)}")
        continue
    canonical_sha = sha(canonical)
    drift = [str(p.relative_to(ROOT)) for p in copies if sha(p) != canonical_sha]
    if drift:
        errors.append(f"{name}: out-of-sync copies: {', '.join(drift)}")

for rel in FORM_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    if re.search(r"\b(?:err|error)\.message\b", text):
        errors.append(f"{rel}: raw error.message is exposed")
    if re.search(r"\bPlease\s+(?:add|select|enter)\b", text):
        errors.append(f"{rel}: sentence-case validation prompt found")
    if "aria-invalid" not in text:
        errors.append(f"{rel}: missing aria-invalid validation hook")
    if "data-form-error-field" not in text:
        errors.append(f"{rel}: missing data-form-error-field validation hook")
    if "preventScroll: true" not in text:
        errors.append(f"{rel}: invalid-field focus can scroll/jump")

for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in {".html", ".css", ".js"}:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*(?:0|1)(?:[\"',\s]|$)", text, re.I):
        errors.append(f"{path.relative_to(ROOT)}: prohibited viewport zoom restriction")

for rel in ("assets/site.css", "assets/rendered-corrections.css"):
    text = (ROOT / rel).read_text(encoding="utf-8")
    scrubbed = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    if scrubbed.count("{") != scrubbed.count("}"):
        errors.append(f"{rel}: unbalanced CSS braces")

home = (ROOT / "index.html").read_text(encoding="utf-8")
if not re.search(r'max-width:\s*900px[\s\S]{0,700}Sunday and Company services[\s\S]{0,180}font-size:\s*7px', home, re.I):
    errors.append("index.html: regular-mobile Home service marquee is not 7px")
if not re.search(r'max-width:\s*599px[\s\S]{0,700}Sunday and Company services[\s\S]{0,180}font-size:\s*7\.75px', home, re.I):
    errors.append("index.html: very-small-mobile Home service marquee is not 7.75px")

site_css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
if not re.search(r'data-news-blurb[\s\S]{0,500}white-space:\s*nowrap', site_css, re.I):
    errors.append("assets/site.css: footer newsletter support line lost nowrap")
if "font-size:16px !important" not in site_css or "font-size:20px !important" not in site_css:
    errors.append("assets/site.css: global mobile focus-size protection is incomplete")

join = (ROOT / "join-our-team/index.html").read_text(encoding="utf-8")
if not re.search(r'data-program-listbox[\s\S]{0,260}bottom:\s*calc\(100%\s*\+\s*1px\)[\s\S]{0,180}top:\s*auto', join, re.I):
    errors.append("join-our-team/index.html: program picker no longer opens upward")

services = (ROOT / "services/index.html").read_text(encoding="utf-8")
if re.search(r'data-inquiry-kicker[^>]*>\s*A Seat At Our Table\s*<', services, re.I):
    errors.append("services/index.html: stale hidden inquiry kicker remains")

if errors:
    print("SITE AUDIT FAILED")
    for item in errors:
        print(f"- {item}")
    sys.exit(1)

print("SITE AUDIT PASSED")
print("Shared components, form guardrails, mobile marquee, newsletter line, and Join picker are consistent.")
