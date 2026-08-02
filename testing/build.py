#!/usr/bin/env python3
"""
Build the Citizen Compass testing area.

Reads the current published page, injects the testing layer, writes testing/index.html.
Re-run this any time the live page changes and the testing area stays flush with it.
The live page is never modified.
"""
import pathlib, sys, datetime

ROOT  = pathlib.Path(__file__).resolve().parent.parent
SRC   = ROOT / "releases" / "latest.html"
LAYER = ROOT / "testing" / "_layer.html"
OUT   = ROOT / "testing" / "index.html"

if not SRC.exists():  sys.exit(f"missing source page: {SRC}")
if not LAYER.exists(): sys.exit(f"missing layer: {LAYER}")

page  = SRC.read_text(encoding="utf-8", errors="replace")
layer = LAYER.read_text(encoding="utf-8", errors="replace")

marker = "</body>"
i = page.lower().rfind(marker)
if i == -1: sys.exit("no </body> found in source page")

stamp = f"\n<!-- testing layer injected {datetime.datetime.utcnow():%Y-%m-%dT%H:%M:%SZ} from {SRC.name} -->\n"
out = page[:i] + stamp + layer + "\n" + page[i:]
OUT.write_text(out, encoding="utf-8")

ver = "unknown"
for tag in ('class="version">', "class='version'>"):
    if tag in page:
        ver = page.split(tag,1)[1].split("<",1)[0].strip(); break

print(f"source : {SRC.relative_to(ROOT)}  ({len(page):,} chars, version {ver})")
print(f"layer  : {LAYER.relative_to(ROOT)}  ({len(layer):,} chars)")
print(f"output : {OUT.relative_to(ROOT)}  ({len(out):,} chars)")
print("\nlive page untouched.")
