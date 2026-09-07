#!/usr/bin/env python3
"""
build_card_pictures.py - builds card_pictures.json, the pictures the front page
cards use.

Replaces build_sleven_thumbs.py, which assumed one source folder with one
credit line. It no longer does: the Gladius Dunlevy has no RSI store page to
save, so its picture came off the Star Citizen Wiki instead. Two sources, two
different credits, and a credit that is wrong is worse than no picture at all.

Each raw folder carries its OWN manifest.json with its OWN credit string. The
credit travels with the picture into the output, per ship, so nothing downstream
has to guess where a given picture came from.

Rules honoured:
  17  exact ship-name join only. A name that does not match is skipped and named.
  11  fails closed - exits non-zero if anything was skipped.
   1  writes only its own output. Deletes nothing.

Run it with no arguments.
"""
import json, os, io, base64, sys
from PIL import Image

HOME = os.path.expanduser('~')
RAW  = HOME + '/mnt/citizen-compass/data-layer/raw'
DERV = HOME + '/mnt/citizen-compass/data-layer/derived/main-page-concepts'
OUT  = DERV + '/card_pictures.json'
W, H = 340, 191

# Add a folder here to add a source. Each needs its own manifest.json with a
# "credit" string - the builder refuses a manifest without one.
SOURCES = [
    ('ship-images-from-sleven', 'RSI store page saved by Sleven'),
    ('ship-images-from-wiki',   'Star Citizen Wiki'),
]

with open(DERV + '/frontpage_data.json', encoding='utf-8') as f:
    d = json.load(f)
ships = d['ships'] if isinstance(d, dict) and 'ships' in d else d
if isinstance(ships, dict): ships = list(ships.values())
NAMES = {(s.get('n') or s.get('name')) for s in ships}

def thumb(path):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    ar = W / H
    if w / h > ar:                       # centre crop. no distortion, no padding.
        nw = int(h * ar); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / ar); im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    im = im.resize((W, H), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=82, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')

thumbs, credits, skipped, seen = {}, {}, [], {}
for folder, label in SOURCES:
    root = os.path.join(RAW, folder)
    mpath = os.path.join(root, 'manifest.json')
    if not os.path.isfile(mpath):
        skipped.append((folder, 'no manifest.json - source ignored')); continue
    with open(mpath, encoding='utf-8') as f:
        man = json.load(f)
    credit = man.get('credit')
    if not credit:
        skipped.append((folder, 'manifest has no credit line - source refused')); continue

    for e in man.get('ships', []):
        name = e['ship']
        if name not in NAMES:
            skipped.append((name, folder + ': no such ship name on the front page')); continue
        src = os.path.join(root, name, e['pick'])
        if not os.path.isfile(src):
            skipped.append((name, folder + ': pick file missing: ' + e['pick'])); continue
        if name in seen:
            # First source in SOURCES wins. Say so rather than silently overwriting.
            skipped.append((name, folder + ': already supplied by ' + seen[name] + ' - kept the first')); continue
        thumbs[name]  = thumb(src)
        credits[name] = {'source': label, 'credit': credit}
        seen[name]    = folder

out = {
  'generated_by': 'build_card_pictures.py (C1)',
  'join': 'exact front page ship name. no fuzzy matching.',
  'width': W, 'height': H,
  'credits': credits,
  'thumbs': thumbs,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)

print('wrote', OUT)
print('ships:', len(thumbs))
for n in sorted(thumbs):
    print('  ', n, '<-', seen[n])
for n, why in skipped:
    print('SKIPPED', n, '-', why)
if skipped:
    sys.exit(1)
