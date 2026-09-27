#!/usr/bin/env python3
"""Synchronize Sunday & Company shared DC components in one local pass.

The runtime loads DC components as siblings of each route, so the copies are
intentional. Edit the root canonical files, then run this script once before
committing.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = (
    "Site Header.dc.html",
    "Site Footer.dc.html",
    "Inquiry Form.dc.html",
    "Program Cards.dc.html",
)

changed = []
for name in COMPONENTS:
    source = ROOT / name
    if not source.exists():
        print(f"Missing canonical component: {name}", file=sys.stderr)
        sys.exit(1)
    source_bytes = source.read_bytes()
    targets = sorted(p for p in ROOT.rglob(name) if p != source and ".git" not in p.parts)
    for target in targets:
        if target.read_bytes() != source_bytes:
            shutil.copyfile(source, target)
            changed.append(str(target.relative_to(ROOT)))

if changed:
    print("Synchronized shared components:")
    for path in changed:
        print(f"  {path}")
else:
    print("Shared component copies already match the canonical root files.")
