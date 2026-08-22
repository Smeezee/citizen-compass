"""
Derive hardpoint positions for every ship that has both a hull and mount data.

This is the four-ship derivation scaled to the fleet. The rules are unchanged —
a mount's NAME says where it sits, and the marker snaps to the nearest real
vertex of the hull — but two things that were safe to assume for four hand-picked
Fan Kit models are not safe across 174 exported .glb, so both are now measured
per ship instead:

  1. WHICH AXIS IS WHICH. The Fan Kit models were all X=beam, Y=up, Z=length.
     Rather than trust that here, each hull's bounding box is matched against
     CIG's own published length/width/height for that ship. If the box does not
     agree with the published figures, the ship is REPORTED AND SKIPPED rather
     than placed in a frame nobody checked.

  2. WHICH END IS THE NOSE. Measured, not assumed: take the cross-sectional
     spread in the slab at each end of the length axis. The tail carries engines,
     wings and hull; the nose is narrow. The wider end is the tail.

Everything else — the target table, the separation pass, the honesty about what
the position is — carries over from place_hardpoints.py unchanged, because it
was already checked against four ships and nothing here weakens it.
"""
import argparse, json, os, re, sys
import numpy as np

# ---------------------------------------------------------------- where
# THIS SCRIPT COULD NOT BE RUN FOR TWELVE DAYS, and nobody noticed because its
# output was already committed. It read /home/claude/fleet/geo and
# /home/claude/fleet/matched.json - a cloud sandbox that was gone by the time
# anyone wanted a second run. hardpoints_fleet.json was the output of a
# derivation that could not be repeated, which is a fact about the data nobody
# could have discovered by reading it.
#
# Both inputs exist here now: the hulls were decoded into
# data-layer/derived/hull-geometry/ on 2026-08-22, and build_matched.py
# reconstructs matched.json from ship_mounts.json plus the model matching
# already recorded in hardpoints_fleet.json.
#
# THE DEFAULT OUTPUT IS _stage/, NOT THE REAL FILE. A script whose bare
# invocation overwrites a committed dataset is a foot-gun, and this one is
# expected to be run repeatedly while comparing before against after.
# Promoting a staged result is a separate, deliberate act.
HERE   = os.path.dirname(os.path.abspath(__file__))
REPO   = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
GEO    = os.environ.get('CC_GEO_DIR') or os.path.join(
             REPO, 'data-layer', 'derived', 'hull-geometry')
MATCHED= os.environ.get('CC_FLEET_MATCHED') or os.path.join(HERE, 'matched.json')
STAGE  = os.path.join(HERE, '_stage')
OUT    = os.path.join(STAGE, 'hardpoints_fleet.json')
REPORT = os.path.join(STAGE, 'placement_report.json')

# ---------------------------------------------------------------- naming
# unchanged from place_hardpoints.py
def tokens(s):
    return re.sub(r'[^a-z0-9]+', ' ', str(s).lower()).split()

def has_vocabulary(loc):
    """Did the name say anything about WHERE this sits?

    `index` is deliberately excluded. A trailing number orders siblings along
    an axis somebody else chose - it says nothing on its own about which axis,
    or which end. Counting it as vocabulary would mean `hardpoint_class_2`
    looked located when all it carries is a 2.
    """
    return any(loc[k] is not None for k in ('side', 'vert', 'lon', 'part'))


def read_location(where, port):
    t = tokens(where) + tokens(port)
    loc = {'side': None, 'vert': None, 'lon': None, 'part': None, 'index': None}
    if 'left' in t or 'port' in t: loc['side'] = 'left'
    if 'right' in t or 'starboard' in t: loc['side'] = 'right'
    if any(w in t for w in ('top', 'upper', 'dorsal')): loc['vert'] = 'top'
    if any(w in t for w in ('bottom', 'lower', 'belly', 'ventral', 'under')): loc['vert'] = 'bottom'
    if any(w in t for w in ('nose', 'front', 'fwd', 'forward')): loc['lon'] = 'front'
    if any(w in t for w in ('rear', 'aft', 'back', 'tail')): loc['lon'] = 'rear'
    if 'mid' in t or 'middle' in t: loc['lon'] = 'mid'
    for part in ('wing', 'pylon', 'nose', 'body', 'hull', 'turret',
                 'missilerack', 'tractor', 'chin', 'roof', 'canopy'):
        if part in t:
            loc['part'] = part; break
    if loc['part'] is None:
        if 'missile' in t and 'rack' in t: loc['part'] = 'missilerack'
        elif 'countermeasure' in t or 'cm' in t: loc['part'] = 'countermeasure'
        elif 'gun' in t or 'weapon' in t or 'laser' in t: loc['part'] = 'gun'
    for w in t:
        if w.isdigit(): loc['index'] = int(w); break
    return loc

TARGET = {
    'nose':(0.18,0.50,0.07), 'chin':(0.16,0.16,0.16), 'canopy':(0.14,0.85,0.26),
    'roof':(0.14,0.92,0.42), 'wing':(0.88,0.46,0.52), 'pylon':(0.72,0.30,0.56),
    'body':(0.34,0.46,0.44), 'hull':(0.34,0.46,0.44), 'turret':(0.16,0.88,0.46),
    'missilerack':(0.56,0.62,0.46), 'countermeasure':(0.62,0.44,0.80),
    'tractor':(0.12,0.20,0.52), 'gun':(0.62,0.50,0.36), None:(0.50,0.50,0.44),
}
LON_SHIFT = {'front': -0.18, 'rear': 0.18, 'mid': 0.0, None: 0.0}

def target_uvw(loc, spread=0.0):
    u, v, w = TARGET[loc['part'] if loc['part'] in TARGET else None]
    u = -u if loc['side'] == 'left' else (u if loc['side'] == 'right' else 0.0)
    if loc['vert'] == 'top': v = max(v, 0.86)
    elif loc['vert'] == 'bottom': v = min(v, 0.14)
    w += LON_SHIFT[loc['lon']] + spread
    if loc['index']: w += (loc['index'] - 1) * 0.13 - 0.13
    return u, float(np.clip(v, 0.02, 0.98)), float(np.clip(w, 0.02, 0.98))

# ------------------------------------------------- frame, measured per ship
def resolve_frame(mn, mx, dim):
    """Which bbox axis is length, which is width, which is height.

    Decided by agreement with CIG's published figures — but on SHAPE, not size.

    The first version of this compared absolute extents and threw away 50 of 174
    ships. Looking at what it rejected showed why: the model library is not
    consistently scaled. The Asgard's hull measures 3,388 x 1,333 x 4,856
    against a published length in the tens of metres — that model is in
    centimetres. The Avenger Stalker measures 1.4 x 0.49 x 1.91 against a
    published 20 x 15 x 6.5 — that one is normalised to roughly unit size.
    Others are in metres. Three different conventions in one folder.

    So the axis assignment is decided on proportions, which survive any uniform
    scale, and the scale itself is then MEASURED and reported. A ship whose
    proportions do not match its own spec sheet is still refused — that is a
    different problem and not one to paper over.

    Returns ((lat, up, lon), err, scale)."""
    ext = [mx[i] - mn[i] for i in range(3)]
    want = {'length': dim.get('length'), 'width': dim.get('width'), 'height': dim.get('height')}
    if not all(want.values()):
        return None, 'no published dimensions', None
    if min(ext) <= 0:
        return None, f'degenerate hull {ext}', None

    wn = [want['length'], want['width'], want['height']]
    wmax = max(wn)
    wr = [x / wmax for x in wn]                     # published proportions

    best, bestErr = None, 1e9
    emax = max(ext)
    for lat in range(3):
        for up in range(3):
            for lon in range(3):
                if len({lat, up, lon}) != 3: continue
                er = [ext[lon] / emax, ext[lat] / emax, ext[up] / emax]
                err = sum(abs(er[i] - wr[i]) for i in range(3))
                if err < bestErr: bestErr, best = err, (lat, up, lon)

    # 0.35 summed proportion error. A model built slightly differently from the
    # spec sheet — landing gear in or out of the height, say — passes. A hull
    # rotated into a different frame does not: swapping length and width on a
    # long ship moves this well past 1.0.
    if bestErr > 0.35:
        return None, (f'proportions do not match published dims '
                      f'(err {bestErr:.2f}, ext {[round(e,2) for e in ext]}, want {wn})'), None

    scale = ext[best[2]] / want['length']           # model units per published metre
    return best, bestErr, scale

def nose_sign(P, ix_len, ix_lat, ix_up):
    """Which end of the length axis is the nose. The tail is wide — engines,
    wings, hull. The nose is narrow. Measure both ends and compare."""
    z = P[:, ix_len]
    lo, hi = z.min(), z.max()
    span = hi - lo
    if span <= 0: return -1
    a = P[(z <= lo + span * 0.15)]
    b = P[(z >= hi - span * 0.15)]
    if len(a) < 20 or len(b) < 20: return -1
    spread = lambda s: (s[:, ix_lat].max() - s[:, ix_lat].min()) + (s[:, ix_up].max() - s[:, ix_up].min())
    # nose is at the NARROW end; return the sign of the forward direction
    return -1 if spread(a) < spread(b) else +1

def place(P, mn, mx, axes, nose, loc, spread=0.0, avoid=(), minsep=0.06):
    lat, up, lon = axes
    # the hull's own centreline — nine of these models are not centred on 0,
    # and the Scorpius is 35% of its own width off, so assuming 0 puts every
    # "left" mount on its right-hand side
    mid = (mn[lat] + mx[lat]) / 2.0
    half = max(mx[lat] - mid, mid - mn[lat]) or 1e-6
    ymin, yr = mn[up], (mx[up] - mn[up]) or 1e-6
    zmin, zr = mn[lon], (mx[lon] - mn[lon]) or 1e-6
    size = float(np.linalg.norm(np.array(mx) - np.array(mn)))
    x, y, z = P[:, lat], P[:, up], P[:, lon]

    side_ok = np.ones(len(P), bool)
    if loc['side'] == 'left':    side_ok = x < mid - half * 0.02
    elif loc['side'] == 'right': side_ok = x >  mid + half * 0.02
    if side_ok.sum() < 30: side_ok = np.ones(len(P), bool)

    p = None
    for attempt in range(9):
        u, v, w = target_uvw(loc, spread + attempt * 0.055 * (1 if attempt % 2 else -1))
        # w runs 0=nose..1=tail; flip into model space using the measured nose end
        wz = w if nose < 0 else (1.0 - w)
        tx, ty, tz = mid + u * half, ymin + v * yr, zmin + wz * zr
        d = (x - tx) ** 2 + (y - ty) ** 2 + (z - tz) ** 2
        d = np.where(side_ok, d, np.inf)
        p = P[int(np.argmin(d))]
        if not avoid: return p, True
        gap = min(float(np.linalg.norm(p - np.asarray(a))) for a in avoid)
        if gap > size * minsep: return p, True
    return p, False

def size_of(mn, mx):
    return float(np.linalg.norm(np.array(mx) - np.array(mn)))

def push_out(p, mn, mx, frac=0.012):
    c = (np.array(mn) + np.array(mx)) / 2.0
    d = np.asarray(p, float) - c
    n = np.linalg.norm(d)
    if n < 1e-9: return np.asarray(p, float)
    size = float(np.linalg.norm(np.array(mx) - np.array(mn)))
    return np.asarray(p, float) + d / n * size * frac

KIND = {'Turret': 'mount', 'MissileLauncher': 'missile',
        'WeaponDefensive': 'countermeasure', 'WeaponGun': 'gun', 'TurretBase': 'mount'}

def main():
    global GEO
    ap = argparse.ArgumentParser(description='Derive hardpoint positions.')
    ap.add_argument('--matched', default=MATCHED)
    ap.add_argument('--geo', default=GEO)
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--report', default=REPORT)
    ap.add_argument('--no-inherit', action='store_true',
                    help='disable B5\'s parent fallback - the BEFORE state, '
                         'so a before/after can be measured rather than '
                         'described.')
    args = ap.parse_args()

    # FAIL CLOSED ON A MISSING INPUT. Writing an empty or partial fleet file
    # over a good one, quietly, is the shape of failure this project keeps
    # finding.
    if not os.path.isdir(args.geo):
        sys.exit('NO GEOMETRY at %s\n'
                 'Decode it first:\n'
                 '  node testing/_src/decode_glb_points.js <dir> '
                 'testing/_deploy/models/*.glb\n'
                 'or set CC_GEO_DIR. Nothing was written.' % args.geo)
    if not os.path.exists(args.matched):
        sys.exit('NO MATCHED INPUT at %s\n'
                 'Build it first:\n'
                 '  python data-layer/derived/holo-hardpoints/build_matched.py\n'
                 'Nothing was written.' % args.matched)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or '.', exist_ok=True)

    GEO = args.geo
    with open(args.matched, 'r', encoding='utf-8') as _fh:
        data = json.load(_fh)['matched']
    if args.no_inherit:
        for _v in data.values():
            for _m in _v['mounts']:
                _m['parent'] = None
        print('--no-inherit: every parent link dropped, so this run is the '
              'BEFORE state.')
    out, report = {}, {'placed': [], 'skipped': [], 'crowded': [],
                       'inherited': []}

    for name, v in sorted(data.items()):
        stem = v['model'][:-4]
        gp = os.path.join(GEO, stem + '.json')
        if not os.path.exists(gp):
            report['skipped'].append([name, 'geometry not decoded']); continue
        with open(gp, 'r', encoding='utf-8') as _gf:
            g = json.load(_gf)
        P = np.asarray(g['pts'], dtype=np.float32).reshape(-1, 3)
        mn, mx = g['min'], g['max']
        axes, err, scale = resolve_frame(mn, mx, v.get('dimension') or {})
        if axes is None:
            report['skipped'].append([name, err]); continue
        nose = nose_sign(P, axes[2], axes[0], axes[1])

        bykey = {}
        inherited_n = 0
        for mt in v['mounts']:
            loc = read_location(mt['where'], mt['port'])
            # B5: A CHILD WITH NO VOCABULARY OF ITS OWN BORROWS ITS PARENT'S.
            #
            # A gun inside a turret is named `hardpoint_class_2`, which says
            # nothing about where it is, so it fell to the None target - the
            # middle of the hull. Its position is on its parent, which is a
            # real port with a real name.
            #
            # ONLY WHEN THE CHILD'S OWN NAME YIELDS NOTHING, never instead of
            # it: a child that knows where it is keeps its own answer. ONE
            # LEVEL, from a REAL PARENT recorded in the flatten - not from
            # siblings, not from anything inferred.
            #
            # `from` is recorded on every point, whichever way it went, because
            # a derivation that stops saying how it got its answer is one
            # nobody can audit later.
            src = 'own'
            if not has_vocabulary(loc) and mt.get('parent'):
                ploc = read_location(mt['parent'], mt['parent'])
                if has_vocabulary(ploc):
                    ploc['index'] = loc['index']   # keep the child's ordering
                    loc = ploc
                    src = 'inherited'
                    inherited_n += 1
            loc['_from'] = src
            bykey.setdefault((loc['side'], loc['vert'], loc['lon'], loc['part']), []).append((mt, loc))

        hps, placed, crowded = [], [], 0
        for key, lst in sorted(bykey.items(), key=lambda kv: str(kv[0])):
            n = len(lst)
            for i, (mt, loc) in enumerate(lst):
                sp = 0.0 if n == 1 else (i / (n - 1.0) - 0.5) * 0.34
                p, ok = place(P, mn, mx, axes, nose, loc, sp, avoid=placed)
                placed.append(p)
                if not ok: crowded += 1
                pcm = push_out(p, mn, mx)
                # MODEL UNITS — the .glb's own space, which is what the viewer
                # needs to place a marker on the mesh it just loaded.
                #
                # Deliberately NOT called metres. 158 of these models are in
                # metres, 8 are normalised to roughly unit size and 1 is in
                # centimetres, so a field called pos_m would be a lie on nine
                # ships. The four-ship file called its field `pos`, the viewer
                # read it as metres, it was centimetres, and every marker landed
                # fifty ship-lengths away. The unit belongs in the NAME.
                #
                # `unit` is normalised to the hull's longest axis and is therefore
                # safe whatever the model's scale. Prefer it.
                span = max(mx[k] - mn[k] for k in range(3)) or 1.0
                centre = [(mn[k] + mx[k]) / 2 for k in range(3)]
                unit = [float((pcm[k] - centre[k]) / (span / 2)) for k in range(3)]
                item = mt.get('item') or {}
                hps.append({
                    'where': mt['where'], 'port': mt['port'],
                    'kind': KIND.get(mt['type'], 'other'),
                    'pilot': None,
                    'turretOf': None,
                    'pos_model': [round(float(c), 3) for c in pcm],
                    'unit': [round(c, 5) for c in unit],
                    'read': [k for k in ('side', 'vert', 'lon', 'part') if loc[k]],
                    # B5: WHERE THE POSITION CAME FROM. 'own' means this port's
                    # own name located it; 'inherited' means its own name said
                    # nothing and its parent's did. renderMarkerNote() keeps
                    # telling the truth because this is here to be told.
                    'placed_from': loc.get('_from', 'own'),
                    'parent': mt.get('parent'),
                    'items': ([{'name': item.get('name'), 'type': item.get('type'),
                                'size': item.get('size') or mt.get('size'),
                                'mfr': item.get('mfr'), 'port': mt['port']}]
                              if item.get('name') else []),
                })
        # A left/right pair placed independently lands on the right sides but at
        # different distances out — the nearest SAMPLED vertex differs on each
        # side. Correct side, wrong look: a user reads asymmetric wing guns as a
        # bug. So mirror the pair across the hull's centreline and re-snap to the
        # nearest real vertex on that side, which keeps both on geometry.
        lat_i = axes[0]
        midx = (mn[lat_i] + mx[lat_i]) / 2.0
        groups = {}
        for h in hps:
            w = h['where'].lower()
            if ' left' in w or ' right' in w:
                k = w.replace(' left', ' *').replace(' right', ' *')
                groups.setdefault(k, {})[('left' if ' left' in w else 'right')] = h
        mirrored = 0
        for k, pair in groups.items():
            if len(pair) != 2: continue
            a, b = pair['left'], pair['right']
            # keep whichever sits further out; mirror it to the other side
            keep, other = (a, b) if abs(a['pos_model'][lat_i] - midx) >= abs(b['pos_model'][lat_i] - midx) else (b, a)
            tgt = list(keep['pos_model'])
            tgt[lat_i] = 2 * midx - tgt[lat_i]
            want_left = (other is a)
            side = (P[:, lat_i] < midx) if want_left else (P[:, lat_i] > midx)
            if side.sum() < 10: continue
            d = np.linalg.norm(P[side] - np.asarray(tgt, float), axis=1)
            snapped = P[side][int(np.argmin(d))]
            newp = push_out(snapped, mn, mx)
            other['pos_model'] = [round(float(c), 3) for c in newp]
            span2 = max(mx[q] - mn[q] for q in range(3)) or 1.0
            centre2 = [(mn[q] + mx[q]) / 2 for q in range(3)]
            other['unit'] = [round(float((newp[q] - centre2[q]) / (span2 / 2)), 5) for q in range(3)]
            mirrored += 1

        # Mirroring bypasses the separation pass, so it can drop a marker on top
        # of one already placed — overlaps went from 15 ships to 28 when mirroring
        # was added. A marker under another marker cannot be clicked, which is a
        # silent failure, so separation is re-checked AFTER mirroring and any
        # collision is walked to the nearest vertex that clears its neighbours.
        MINSEP = size_of(mn, mx) * 0.02
        for i, h in enumerate(hps):
            q = np.asarray(h['pos_model'], float)
            others = [np.asarray(o['pos_model'], float) for j, o in enumerate(hps) if j != i]
            if not others: break
            O = np.asarray(others)
            if np.min(np.linalg.norm(O - q, axis=1)) >= MINSEP:
                continue
            # candidates near the original, ordered by how little they move it
            d0 = np.linalg.norm(P - q, axis=1)
            near = np.argsort(d0)[:4000]
            moved = False
            for idx in near:
                c = P[idx]
                if np.min(np.linalg.norm(O - c, axis=1)) >= MINSEP:
                    newp = push_out(c, mn, mx)
                    h['pos_model'] = [round(float(t), 3) for t in newp]
                    sp = max(mx[t] - mn[t] for t in range(3)) or 1.0
                    ct = [(mn[t] + mx[t]) / 2 for t in range(3)]
                    h['unit'] = [round(float((newp[t] - ct[t]) / (sp / 2)), 5) for t in range(3)]
                    moved = True
                    break
            if not moved:
                crowded += 1        # reported, not hidden

        out[name] = {'maker': v.get('maker'), 'bare': v['bare'], 'model': v['model'],
                     'dimension': v.get('dimension'),
                     'pilot_dps': v.get('pilot_dps'), 'pilot_alpha': v.get('pilot_alpha'),
                     'weapons': v.get('weapons'),
                     'frame': {'lat': axes[0], 'up': axes[1], 'len': axes[2],
                               'nose_sign': int(nose), 'shape_err': round(float(err), 3),
                               'model_units_per_metre': round(float(scale), 4)},
                     'hardpoints': hps}
        report['placed'].append([name, len(hps), round(float(err), 3), round(float(scale), 4)])
        if crowded: report['crowded'].append([name, crowded])
        if inherited_n: report['inherited'].append([name, inherited_n])

    with open(args.out, 'w', encoding='utf-8', newline='\n') as _of:
        json.dump(out, _of, separators=(',', ':'))
    with open(args.report, 'w', encoding='utf-8', newline='\n') as _rf:
        json.dump(report, _rf, indent=1)
    print('ships placed     :', len(out))
    print('hardpoints placed:', sum(len(s['hardpoints']) for s in out.values()))
    print('ships skipped    :', len(report['skipped']))
    for n, why in report['skipped'][:12]:
        print('   ', n, '->', str(why)[:100])
    print('ships with a crowded marker:', len(report['crowded']))
    _inh = sum(n for _, n in report['inherited'])
    _none = sum(1 for s in out.values() for h in s['hardpoints'] if not h['read'])
    print('points placed from a PARENT name:', _inh,
          'on', len(report['inherited']), 'ships')
    print('points that still read NO position vocabulary:', _none)
    # the scale spread is itself a finding — report it rather than bury it
    import collections
    sc = collections.Counter()
    for _, _, _, s_ in report['placed']:
        sc['~1 (metres)' if 0.5 < s_ < 2 else
           '~100 (centimetres)' if 50 < s_ < 200 else
           '<0.5 (normalised/small)' if s_ <= 0.5 else 'other'] += 1
    print()
    print('MODEL SCALE, measured against each ship\'s own published length:')
    for k, n in sc.most_common():
        print(f'   {n:4d} ships  {k}')

if __name__ == '__main__':
    main()
