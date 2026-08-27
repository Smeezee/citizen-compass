"""
Derive FIXED hardpoint positions for the holo viewer.

The click-to-place markers were wrong: a dot landed wherever the mouse
landed, which is an authoring tool, not a ship. What a viewer needs is a
marker sitting where the gun actually is, so a player can click the left
wing gun and read the left wing gun's numbers.

We do not have real coordinates. All 53,651 `position` fields in the
game data are null — that was measured and written up. What we DO have:

  1. the mount NAME, which carries the location in words:
     "Weapon left wing", "Gun laser bottom right", "Missilerack top
     left rear", "Left Pylon 2", "Countermeasure launcher left".
  2. the hull mesh, at real scale in centimetres, verified against
     CIG's own published dimensions.

So a name is turned into a region of the hull, and the marker is snapped
to a real vertex inside that region. The position is DERIVED, not
authored by CIG, and the viewer says so on every marker. It puts the
left wing gun on the left wing, which is the thing the player needs.

MODEL FRAME — worked out from the meshes, not assumed:
  X  lateral   every hull is symmetric about x=0
  Y  up        the Cyclone's minimum Y is 0.0, i.e. the wheels sit on
               the ground plane; the Aquila runs -372..+951, more ship
               above the datum than below
  Z  forward = -Z.  At the low-Z end the Sabre is 369 cm wide; at the
               high-Z end it is 2338 cm, the full wingspan. A Sabre's
               nose is a point and its tail is the wings, so low Z is
               the nose. The Aquila agrees: 1048 cm at low Z, 2072 cm
               and 1088 cm tall at high Z, which is its engine block.

  Handedness: with forward = -Z and up = +Y, right = forward x up = +X.
  That follows only if the export preserved a right-handed frame, which
  is normal but is NOT something these files state. The hulls are
  mirror-symmetric to within 2-3% (stray vertices, not features), so
  nothing in the geometry can confirm it. It is therefore an
  ASSUMPTION, it is labelled as one in the viewer, and the viewer has a
  mirror control so a player who knows better can flip it.
"""
import json, re, numpy as np

B = '/home/claude/work/fankit_test/'
MESH = {
    'Drake Cutlass Black':      'Drake_Cutlass_Black_v.npy',
    'RSI Constellation Aquila': 'RSI_Constellation_Aquila_v.npy',
    'Aegis Sabre':              'Aegis_Sabre_v.npy',
    'Tumbril Cyclone':          'tumbril_cyclone_v.npy',
}

# ---------------------------------------------------------------- naming

def tokens(s):
    return re.sub(r'[^a-z0-9]+', ' ', str(s).lower()).split()

def read_location(where, port):
    """Turn a mount name into a location. Returns a dict of what the name
    actually said — never a default dressed up as a reading. Anything the
    name did not say comes back None so the caller can see the gap."""
    t = tokens(where) + tokens(port)
    loc = {'side': None, 'vert': None, 'lon': None, 'part': None, 'index': None}

    if 'left'  in t or 'port'      in t: loc['side'] = 'left'
    if 'right' in t or 'starboard' in t: loc['side'] = 'right'

    if any(w in t for w in ('top', 'upper', 'dorsal')):   loc['vert'] = 'top'
    if any(w in t for w in ('bottom', 'lower', 'belly', 'ventral', 'under')):
        loc['vert'] = 'bottom'

    if any(w in t for w in ('nose', 'front', 'fwd', 'forward')): loc['lon'] = 'front'
    if any(w in t for w in ('rear', 'aft', 'back', 'tail')):     loc['lon'] = 'rear'
    if 'mid' in t or 'middle' in t:                              loc['lon'] = 'mid'

    for part in ('wing', 'pylon', 'nose', 'body', 'hull', 'turret',
                 'missilerack', 'tractor', 'chin', 'roof', 'canopy'):
        if part in t:
            loc['part'] = part
            break
    if loc['part'] is None:
        if 'missile' in t and 'rack' in t: loc['part'] = 'missilerack'
        elif 'countermeasure' in t or 'cm' in t: loc['part'] = 'countermeasure'
        elif 'gun' in t or 'weapon' in t or 'laser' in t: loc['part'] = 'gun'

    for w in t:
        if w.isdigit():
            loc['index'] = int(w)
            break
    return loc

# ------------------------------------------------------- placement rules

#  Where each kind of mount sits, in the hull's own normalised box:
#     u  lateral   0 = centreline, 1 = wingtip
#     v  vertical  0 = belly, 1 = roof
#     w  along     0 = nose,  1 = tail
#  These are the shapes of ships, not measurements of any one ship: a wing
#  gun is far outboard about halfway back; a nose gun is near the tip and
#  near the centreline; a countermeasure launcher is well aft. Scoring by
#  "how far out can I get" was tried first and collapsed — every left-hand
#  mount raced to the same wingtip vertex. An explicit target does not.
TARGET = {
    'nose':           (0.18, 0.50, 0.07),
    'chin':           (0.16, 0.16, 0.16),
    'canopy':         (0.14, 0.85, 0.26),
    'roof':           (0.14, 0.92, 0.42),
    'wing':           (0.88, 0.46, 0.52),
    'pylon':          (0.72, 0.30, 0.56),
    'body':           (0.34, 0.46, 0.44),
    'hull':           (0.34, 0.46, 0.44),
    'turret':         (0.16, 0.88, 0.46),
    'missilerack':    (0.56, 0.62, 0.46),
    'countermeasure': (0.62, 0.44, 0.80),
    'tractor':        (0.12, 0.20, 0.52),
    'gun':            (0.62, 0.50, 0.36),
    None:             (0.50, 0.50, 0.44),
}
LON_SHIFT = {'front': -0.18, 'rear': 0.18, 'mid': 0.0, None: 0.0}


def norm_axes(verts):
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
    half = max(abs(x.min()), abs(x.max()))
    ymin, ymax = y.min(), y.max()
    zmin, zmax = z.min(), z.max()
    return half, ymin, ymax - ymin, zmin, zmax - zmin


def target_uvw(loc, spread=0.0):
    """The point we are aiming for, in normalised hull coordinates."""
    u, v, w = TARGET[loc['part'] if loc['part'] in TARGET else None]

    if loc['side'] == 'left':    u = -u
    elif loc['side'] == 'right': u = u
    else:                        u = 0.0

    if loc['vert'] == 'top':      v = max(v, 0.86)
    elif loc['vert'] == 'bottom': v = min(v, 0.14)

    w += LON_SHIFT[loc['lon']] + spread
    if loc['index']:
        w += (loc['index'] - 1) * 0.13 - 0.13
    return u, float(np.clip(v, 0.02, 0.98)), float(np.clip(w, 0.02, 0.98))


def place(verts, loc, spread=0.0, avoid=(), minsep=0.06):
    """Snap to the real hull vertex nearest the target.

    Nearest-vertex, not nearest-point-on-a-surface: the marker then sits
    on geometry that exists rather than in the air beside it. Distance is
    measured in centimetres, so a long ship is not squashed against a
    short one by working in normalised space.

    `avoid` holds markers already placed. Two mounts landing on the same
    vertex is the failure this had first time round — three pylons stacked
    into one dot — so a candidate too close to an existing marker is
    pushed along the hull until it separates, and if it cannot separate
    the caller is told rather than the collision being hidden.
    """
    half, ymin, yr, zmin, zr = norm_axes(verts)
    size = float(np.linalg.norm(verts.max(0) - verts.min(0)))
    x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]

    side_ok = np.ones(len(verts), bool)
    if loc['side'] == 'left':    side_ok = x < -half * 0.02
    elif loc['side'] == 'right': side_ok = x >  half * 0.02
    if side_ok.sum() < 50:
        side_ok = np.ones(len(verts), bool)

    for attempt in range(9):
        u, v, w = target_uvw(loc, spread + attempt * 0.055 * (1 if attempt % 2 else -1))
        tx, ty, tz = u * half, ymin + v * yr, zmin + w * zr
        d = (x - tx) ** 2 + (y - ty) ** 2 + (z - tz) ** 2
        d = np.where(side_ok, d, np.inf)
        p = verts[int(np.argmin(d))]
        if not avoid:
            return p, True
        gap = min(float(np.linalg.norm(p - np.asarray(a))) for a in avoid)
        if gap > size * minsep:
            return p, True
    return p, False              # separated as far as the hull allows


def to_unit(p, verts):
    """Into the viewer's own space.

    The viewer packs each hull into an origin-centred cube where the LONGEST
    axis fills -1..1 and the others keep their true proportion — checked by
    decoding the payload rather than trusting the packing code: the Aquila
    comes back spanning 0.870 x 0.435 x 2.000 against real dimensions of
    2649.7 x 1323.8 x 6090.2 cm, the same ratios. So the marker can be baked
    in viewer units and needs no conversion at runtime.
    """
    mn, mx = verts.min(0), verts.max(0)
    centre = (mn + mx) / 2.0
    scale = float((mx - mn).max()) / 2.0
    return (np.asarray(p) - centre) / scale


def push_out(p, verts, frac=0.012):
    """Nudge the marker off the skin so it is not z-fighting the hull."""
    c = np.array([0.0, (verts[:, 1].min() + verts[:, 1].max()) / 2.0, verts[:, 2].mean()])
    d = p - c
    n = np.linalg.norm(d)
    if n < 1e-6:
        return p
    size = float(np.linalg.norm(verts.max(0) - verts.min(0)))
    return p + d / n * size * frac

# ------------------------------------------------------------- grouping

def group_mounts(weapons):
    """One physical hardpoint, one marker.

    The data lists a gimbal mount and the gun sitting in it as two rows
    with the same `where`. They are the same place on the hull, so they
    become one hardpoint carrying both — otherwise every wing grows two
    markers on top of each other.
    """
    out, order = {}, []
    for w in weapons:
        k = w['where']
        if k not in out:
            out[k] = {'where': k, 'items': [], 'pilot': w.get('pilot'),
                      'ports': [], 'turretOf': None}
            order.append(k)
        out[k]['items'].append(w)
        if w.get('port') and w['port'] not in out[k]['ports']:
            out[k]['ports'].append(w['port'])
    # "Turret · weapon left" means a gun INSIDE a turret, not a hull mount.
    for k in order:
        if '·' in k or ' - ' in k:
            out[k]['turretOf'] = k.split('·')[0].strip()
    return [out[k] for k in order]


def kind_of(hp):
    types = {i.get('type') for i in hp['items']}
    if 'MissileLauncher' in types: return 'missile'
    if 'WeaponDefensive' in types: return 'countermeasure'
    if 'WeaponGun' in types:       return 'gun'
    if 'Turret' in types:          return 'mount'
    return 'other'

# ------------------------------------------------------------------ main

def main():
    loadouts = json.load(open(B + 'loadouts.json'))
    result, report = {}, []

    for ship, mesh in MESH.items():
        verts = np.load(B + mesh)
        lo = loadouts[ship]
        groups = group_mounts(lo['weapons'])

        # Mounts that read the same way get nudged apart along the ship, so
        # three pylons on one side do not stack into one dot.
        bykey, hps, placed = {}, [], []
        for g in groups:
            loc = read_location(g['where'], ' '.join(g['ports']))
            key = (loc['side'], loc['vert'], loc['lon'], loc['part'])
            bykey.setdefault(key, []).append((g, loc))

        crowded = 0
        for key, lst in sorted(bykey.items(), key=lambda kv: str(kv[0])):
            n = len(lst)
            for i, (g, loc) in enumerate(lst):
                spread = 0.0 if n == 1 else (i / (n - 1.0) - 0.5) * 0.34
                p, ok = place(verts, loc, spread, avoid=placed)
                placed.append(p)
                if not ok:
                    crowded += 1
                named = [k for k in ('side', 'vert', 'lon', 'part') if loc[k]]
                pcm = push_out(p, verts)
                hps.append({
                    'where': g['where'],
                    'kind': kind_of(g),
                    'pilot': bool(g['pilot']),
                    'turretOf': g['turretOf'],
                    'pos': [round(float(c), 1) for c in pcm],
                    'unit': [round(float(c), 5) for c in to_unit(pcm, verts)],
                    'read': named,                      # which words placed it
                    'items': [{'name': i['name'], 'type': i['type'], 'size': i['size'],
                               'mfr': i['mfr'], 'dps': i['dps'], 'alpha': i['alpha'],
                               'port': i['port']} for i in g['items']],
                })

        result[ship] = hps
        report.append((ship, len(hps), sum(1 for h in hps if h['read']),
                       sum(1 for h in hps if not h['read']), crowded))

    json.dump(result, open(B + 'hardpoints.json', 'w'), separators=(',', ':'))

    print(f'{"ship":28} {"mounts":>7} {"named":>7} {"unnamed":>8} {"crowded":>8}')
    for r in report:
        print(f'{r[0]:28} {r[1]:7d} {r[2]:7d} {r[3]:8d} {r[4]:8d}')
    for ship, hps in result.items():
        print('\n== ' + ship)
        for h in hps:
            print(f'   {h["kind"]:14} {h["where"][:38]:38} '
                  f'{str(h["pos"]):26} from {",".join(h["read"]) or "NOTHING IN THE NAME"}')

    # A marker on top of another marker is unclickable, so this is checked
    # rather than eyeballed.
    print('\n=== separation ===')
    for ship, hps in result.items():
        P = np.array([h['pos'] for h in hps]) if hps else np.zeros((0, 3))
        v = np.load(B + MESH[ship])
        size = float(np.linalg.norm(v.max(0) - v.min(0)))
        worst, pair = 1e9, None
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                d = float(np.linalg.norm(P[i] - P[j]))
                if d < worst:
                    worst, pair = d, (hps[i]['where'], hps[j]['where'])
        if pair:
            print(f'   {ship:28} closest pair {worst:7.0f} cm '
                  f'({worst / size * 100:4.1f}% of hull)  {pair[0]} / {pair[1]}')
        # every marker must actually be near the hull, not floating
        if len(P):
            far = max(float(np.min(np.linalg.norm(v - p, axis=1))) for p in P)
            print(f'   {"":28} furthest any marker sits from the hull: {far:.0f} cm '
                  f'({far / size * 100:.1f}%)')


if __name__ == '__main__':
    main()
