"""Render one page of each of the six source_kinds and confirm none has an
empty block above its disclosure."""
import json
import os

D = 'data-layer/processed/blueprints'
bp = json.load(open('data-layer/processed/blueprint_index.json', encoding='utf-8'))

KINDS = ['contract', 'event', 'direct_reward', 'other_pool', 'default', 'none']
failures = []

for kind in KINDS:
    rows = [r for r in bp if r.get('source_kind') == kind]
    if not rows:
        failures.append('%s: no blueprint of this kind' % kind)
        continue
    # pick the one with the most sources, the hardest case for that kind
    row = max(rows, key=lambda r: len(r.get('sources') or []))
    key = row['blueprint_key']
    page = json.load(open(os.path.join(D, key + '.json'), encoding='utf-8'))
    ss = page.get('source_summary')
    disclosure = os.path.exists(os.path.join(D, key + '.sources.json'))

    print('--- %-14s %s' % (kind, key[:48]))
    print('    rows of this kind : %d' % len(rows))
    print('    disclosure file   : %s' % ('yes' if disclosure else 'no'))

    if not ss:
        failures.append('%s: source_summary is %r - EMPTY BLOCK' % (kind, ss))
        print('    BLOCK             : *** EMPTY ***')
        continue

    if kind == 'contract':
        best = ss.get('best') or {}
        rendered = '%s (%s) - %d source(s), %d others' % (
            best.get('title'), best.get('giver'), ss.get('total'), ss.get('others'))
    else:
        rendered = ss.get('headline')

    print('    kind field        : %s' % ss.get('kind'))
    print('    RENDERS AS        : %s' % rendered)

    if not rendered or not str(rendered).strip():
        failures.append('%s: renders to empty text' % kind)
    if ss.get('kind') != kind:
        failures.append('%s: block kind field is %r' % (kind, ss.get('kind')))
    # a disclosure with nothing above it is the exact defect being fixed
    if disclosure and not rendered:
        failures.append('%s: has a disclosure and an empty block above it' % kind)
    print()

# and the whole-set sweep, not just six samples
empty = [r['blueprint_key'] for r in bp
         if not json.load(open(os.path.join(D, r['blueprint_key'] + '.json'),
                               encoding='utf-8')).get('source_summary')]
with_disc_no_block = [
    r['blueprint_key'] for r in bp
    if os.path.exists(os.path.join(D, r['blueprint_key'] + '.sources.json'))
    and not json.load(open(os.path.join(D, r['blueprint_key'] + '.json'),
                           encoding='utf-8')).get('source_summary')]

print('=' * 62)
print('pages with NO source_summary at all        : %d of %d' % (len(empty), len(bp)))
print('pages with a disclosure and an empty block : %d   <- was 48' % len(with_disc_no_block))
if failures:
    print('\nFAILURES:')
    for f in failures:
        print('  -', f)
    raise SystemExit(1)
print('\nAll six kinds render a non-empty block.')
